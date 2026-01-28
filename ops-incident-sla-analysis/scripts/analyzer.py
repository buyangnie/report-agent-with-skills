"""
Core Analysis Engine for SLA Violation Analysis.
Implements three-layer analysis: Overview, Risk, Deep Dive.
"""
import pandas as pd
import numpy as np
from datetime import datetime
from config import (
    RISK_HIGH_THRESHOLD, RISK_MEDIUM_THRESHOLD,
    MAX_REASSIGNMENTS, MAX_ESCALATIONS, SUSPEND_TIME_RATIO,
    WORK_HOURS_START, WORK_HOURS_END, WEEKEND_DAYS
)


class SLAAnalyzer:
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = None
        self.sla_criteria = None
        self.results = {}

    def load_data(self):
        """Load and preprocess data from Excel."""
        self.sla_criteria = pd.read_excel(self.filepath, sheet_name='SLA_Criteria')
        self.df = pd.read_excel(self.filepath, sheet_name='Data')
        self._validate_schema()
        self._preprocess()

    def _validate_schema(self):
        """Validate required columns exist."""
        required_cols = [
            'Order Number', 'Order Name', 'Priority', 'Resolver',
            'Category', 'Begin Date', 'Resolution Date',
            'Resolution Time(m)', 'Response Time(m)'
        ]
        missing = [c for c in required_cols if c not in self.df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

    def _preprocess(self):
        """Clean and enrich data."""
        df = self.df

        # Standardize strings
        df['Priority'] = df['Priority'].astype(str).str.strip()
        df['Resolver'] = df['Resolver'].fillna('Unassigned').astype(str).str.strip()
        df['Category'] = df['Category'].fillna('Uncategorized').astype(str).str.strip()

        # Parse dates
        df['Begin Date'] = pd.to_datetime(df['Begin Date'], errors='coerce')
        df['Resolution Date'] = pd.to_datetime(df['Resolution Date'], errors='coerce')

        # Calculate hours
        df['Resolution_Hours'] = df['Resolution Time(m)'] / 60.0
        df['Response_Mins'] = df['Response Time(m)']

        # Map SLA thresholds
        self.sla_criteria['Priority'] = self.sla_criteria['Priority'].astype(str).str.strip()
        res_col = [c for c in self.sla_criteria.columns if 'Resolution' in c][0]
        resp_col = [c for c in self.sla_criteria.columns if 'Response' in c][0]

        sla_res_map = dict(zip(self.sla_criteria['Priority'], self.sla_criteria[res_col]))
        sla_resp_map = dict(zip(self.sla_criteria['Priority'], self.sla_criteria[resp_col]))

        df['SLA_Res_Limit_Hours'] = df['Priority'].map(sla_res_map)
        df['SLA_Resp_Limit_Mins'] = df['Priority'].map(sla_resp_map)

        # SLA percentage consumed
        df['SLA_Res_Pct'] = (df['Resolution_Hours'] / df['SLA_Res_Limit_Hours'] * 100).clip(upper=999)
        df['SLA_Resp_Pct'] = (df['Response_Mins'] / df['SLA_Resp_Limit_Mins'] * 100).clip(upper=999)

        # Violation flags
        df['SLA_Res_Violated'] = df['Resolution_Hours'] > df['SLA_Res_Limit_Hours']
        df['SLA_Resp_Violated'] = df['Response_Mins'] > df['SLA_Resp_Limit_Mins']
        df['SLA_Res_Overage_Hours'] = (df['Resolution_Hours'] - df['SLA_Res_Limit_Hours']).clip(lower=0)

        # Risk level
        def calc_risk(pct, violated):
            if violated:
                return 'Violated'
            if pct >= RISK_HIGH_THRESHOLD:
                return 'High'
            if pct >= RISK_MEDIUM_THRESHOLD:
                return 'Medium'
            return 'Low'

        df['Risk_Level'] = df.apply(lambda r: calc_risk(r['SLA_Res_Pct'], r['SLA_Res_Violated']), axis=1)

        # Time features
        df['Hour'] = df['Begin Date'].dt.hour
        df['DayOfWeek'] = df['Begin Date'].dt.dayofweek
        df['IsWeekend'] = df['DayOfWeek'].isin(WEEKEND_DAYS)
        df['IsOffHours'] = ~df['Hour'].between(WORK_HOURS_START, WORK_HOURS_END)

        # Filter invalid data
        df = df[df['Resolution Time(m)'] >= 0]
        self.df = df

    def analyze_all(self):
        """Run all analysis layers."""
        self.results = {
            'overview': self._analyze_overview(),
            'risk': self._analyze_risk(),
            'violations': self._analyze_violations(),
            'attribution': self._analyze_attribution(),
            'recommendations': self._generate_recommendations(),
        }
        return self.results

    def _analyze_overview(self):
        """Layer 1: SLA Overview."""
        df = self.df
        total = len(df)

        # Overall SLA
        res_violations = df['SLA_Res_Violated'].sum()
        resp_violations = df['SLA_Resp_Violated'].sum()
        res_rate = ((total - res_violations) / total * 100) if total > 0 else 0
        resp_rate = ((total - resp_violations) / total * 100) if total > 0 else 0

        # By priority
        by_priority = df.groupby('Priority').agg(
            Total=('Order Number', 'count'),
            Res_Violations=('SLA_Res_Violated', 'sum'),
            Resp_Violations=('SLA_Resp_Violated', 'sum'),
            Avg_MTTR=('Resolution_Hours', 'mean')
        ).reset_index()
        by_priority['Res_Rate'] = ((by_priority['Total'] - by_priority['Res_Violations']) / by_priority['Total'] * 100).round(1)
        by_priority['Resp_Rate'] = ((by_priority['Total'] - by_priority['Resp_Violations']) / by_priority['Total'] * 100).round(1)

        # By category
        by_category = df.groupby('Category').agg(
            Total=('Order Number', 'count'),
            Violations=('SLA_Res_Violated', 'sum')
        ).reset_index()
        by_category['Rate'] = ((by_category['Total'] - by_category['Violations']) / by_category['Total'] * 100).round(1)
        by_category = by_category.sort_values('Violations', ascending=False).head(10)

        # Trend by week
        df['Week'] = df['Begin Date'].dt.isocalendar().week
        weekly_trend = df.groupby('Week').agg(
            Total=('Order Number', 'count'),
            Violations=('SLA_Res_Violated', 'sum')
        ).reset_index()
        weekly_trend['Rate'] = ((weekly_trend['Total'] - weekly_trend['Violations']) / weekly_trend['Total'] * 100).round(1)

        # Date range
        date_range = f"{df['Begin Date'].min().strftime('%Y-%m-%d')} ~ {df['Begin Date'].max().strftime('%Y-%m-%d')}"

        return {
            'total': total,
            'res_violations': int(res_violations),
            'resp_violations': int(resp_violations),
            'res_rate': round(res_rate, 1),
            'resp_rate': round(resp_rate, 1),
            'by_priority': by_priority,
            'by_category': by_category,
            'weekly_trend': weekly_trend,
            'date_range': date_range,
        }

    def _analyze_risk(self):
        """Layer 2: Risk Analysis (not yet violated but high risk)."""
        df = self.df
        non_violated = df[df['SLA_Res_Violated'] == False].copy()

        # Risk distribution
        risk_dist = non_violated['Risk_Level'].value_counts()

        # High risk tickets
        high_risk = non_violated[non_violated['Risk_Level'] == 'High'].copy()
        high_risk = high_risk.sort_values('SLA_Res_Pct', ascending=False)

        high_risk_list = high_risk[[
            'Order Number', 'Order Name', 'Priority', 'Category',
            'Resolver', 'Resolution_Hours', 'SLA_Res_Limit_Hours', 'SLA_Res_Pct'
        ]].head(20).to_dict('records')

        # Medium risk tickets
        medium_risk = non_violated[non_violated['Risk_Level'] == 'Medium']

        # Risk by category
        risk_by_category = high_risk.groupby('Category').size().sort_values(ascending=False).head(10)

        # Risk by resolver
        risk_by_resolver = high_risk.groupby('Resolver').size().sort_values(ascending=False).head(10)

        return {
            'distribution': risk_dist.to_dict(),
            'high_risk_count': len(high_risk),
            'medium_risk_count': len(medium_risk),
            'high_risk_list': high_risk_list,
            'by_category': risk_by_category,
            'by_resolver': risk_by_resolver,
        }

    def _analyze_violations(self):
        """Layer 3: Violation Deep Dive."""
        df = self.df
        violated = df[df['SLA_Res_Violated'] == True].copy()
        violated = violated.sort_values('SLA_Res_Overage_Hours', ascending=False)

        # Severity distribution
        severity_bins = [0, 2, 8, 24, float('inf')]
        severity_labels = ['Minor (<2h)', 'Moderate (2-8h)', 'Severe (8-24h)', 'Critical (>24h)']
        violated['Severity'] = pd.cut(violated['SLA_Res_Overage_Hours'], bins=severity_bins, labels=severity_labels)
        severity_dist = violated['Severity'].value_counts()

        # Violation list with attribution
        violation_list = []
        for _, row in violated.head(30).iterrows():
            attribution = self._attribute_violation(row)
            violation_list.append({
                'order_number': row['Order Number'],
                'order_name': str(row['Order Name'])[:50],
                'priority': row['Priority'],
                'category': row['Category'],
                'resolver': row['Resolver'],
                'resolution_hours': round(row['Resolution_Hours'], 1),
                'sla_limit_hours': round(row['SLA_Res_Limit_Hours'], 1),
                'overage_hours': round(row['SLA_Res_Overage_Hours'], 1),
                'severity': str(row['Severity']),
                'attribution': attribution,
                'begin_date': row['Begin Date'].strftime('%Y-%m-%d %H:%M') if pd.notna(row['Begin Date']) else '',
            })

        # By priority
        by_priority = violated.groupby('Priority').size().to_dict()

        # By category
        by_category = violated.groupby('Category').size().sort_values(ascending=False).head(10)

        # By resolver
        by_resolver = violated.groupby('Resolver').size().sort_values(ascending=False).head(10)

        return {
            'total': len(violated),
            'severity_distribution': severity_dist.to_dict(),
            'violation_list': violation_list,
            'by_priority': by_priority,
            'by_category': by_category,
            'by_resolver': by_resolver,
        }

    def _attribute_violation(self, row):
        """Determine attribution for a violation."""
        attributions = []

        # Check reassignments
        if 'Reassignment Count' in row.index and pd.notna(row.get('Reassignment Count')):
            if row['Reassignment Count'] >= MAX_REASSIGNMENTS:
                attributions.append('Process: Too many reassignments')

        # Check escalations
        if 'Escalation Count' in row.index and pd.notna(row.get('Escalation Count')):
            if row['Escalation Count'] >= MAX_ESCALATIONS:
                attributions.append('Process: Escalation delay')

        # Check suspend time
        if 'Suspend Time(m)' in row.index and pd.notna(row.get('Suspend Time(m)')):
            suspend_mins = row['Suspend Time(m)']
            resolution_mins = row['Resolution Time(m)']
            if resolution_mins > 0 and suspend_mins / resolution_mins > SUSPEND_TIME_RATIO:
                attributions.append('External: Long wait time')

        # Check time window
        if row.get('IsWeekend', False):
            attributions.append('TimeWindow: Weekend')
        elif row.get('IsOffHours', False):
            attributions.append('TimeWindow: Off-hours')

        # Default attribution
        if not attributions:
            if row['SLA_Res_Overage_Hours'] > 24:
                attributions.append('Resource: Capacity issue')
            else:
                attributions.append('Process: General delay')

        return attributions

    def _analyze_attribution(self):
        """Aggregate attribution analysis."""
        df = self.df
        violated = df[df['SLA_Res_Violated'] == True].copy()

        # Count by attribution type
        attribution_counts = {
            'Process': 0,
            'Resource': 0,
            'External': 0,
            'TimeWindow': 0,
        }

        for _, row in violated.iterrows():
            attrs = self._attribute_violation(row)
            for attr in attrs:
                if attr.startswith('Process'):
                    attribution_counts['Process'] += 1
                elif attr.startswith('Resource'):
                    attribution_counts['Resource'] += 1
                elif attr.startswith('External'):
                    attribution_counts['External'] += 1
                elif attr.startswith('TimeWindow'):
                    attribution_counts['TimeWindow'] += 1

        return attribution_counts

    def _generate_recommendations(self):
        """Generate actionable recommendations."""
        recs = []
        overview = self._analyze_overview()
        violations = self._analyze_violations()
        risk = self._analyze_risk()

        # SLA rate recommendations
        if overview['res_rate'] < 95:
            recs.append({
                'priority': 'HIGH',
                'category': 'SLA',
                'text': f"Resolution SLA compliance is {overview['res_rate']:.1f}%, below 95% target. Immediate action required.",
                'text_zh': f"解决 SLA 达成率为 {overview['res_rate']:.1f}%，低于 95% 目标。需立即采取行动。"
            })

        # High risk recommendations
        if risk['high_risk_count'] > 10:
            recs.append({
                'priority': 'HIGH',
                'category': 'Risk',
                'text': f"{risk['high_risk_count']} tickets at high risk of SLA breach. Prioritize intervention.",
                'text_zh': f"{risk['high_risk_count']} 张工单处于高风险状态。需优先干预。"
            })

        # Category recommendations
        if len(violations['by_category']) > 0:
            top_cat = violations['by_category'].index[0]
            top_count = violations['by_category'].iloc[0]
            recs.append({
                'priority': 'MEDIUM',
                'category': 'Category',
                'text': f"'{top_cat}' has {top_count} violations. Review process for this category.",
                'text_zh': f"'{top_cat}' 类别有 {top_count} 次违约。请审视该类别的处理流程。"
            })

        # Resolver recommendations
        if len(violations['by_resolver']) > 0:
            top_resolver = violations['by_resolver'].index[0]
            resolver_count = violations['by_resolver'].iloc[0]
            if resolver_count >= 5:
                recs.append({
                    'priority': 'MEDIUM',
                    'category': 'Personnel',
                    'text': f"'{top_resolver}' has {resolver_count} violations. Consider workload balancing or training.",
                    'text_zh': f"'{top_resolver}' 有 {resolver_count} 次违约。建议调整工作量或加强培训。"
                })

        return recs
