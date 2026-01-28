"""
Core Analysis Engine for Ops Deep Dive Report.
Implements 8-dimension analysis based on incident data.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import Counter
import re

class ReportAnalyzer:
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = None
        self.sla_criteria = None
        self.results = {}
        
    def load_data(self):
        """Load and preprocess data from Excel with schema validation."""
        try:
            self.sla_criteria = pd.read_excel(self.filepath, sheet_name='SLA_Criteria')
            self.df = pd.read_excel(self.filepath, sheet_name='Data')
        except ValueError as e:
            raise ValueError(f"Missing required sheet in Excel file. Expected sheets: 'SLA_Criteria' and 'Data'. Error: {e}")
        except Exception as e:
            raise Exception(f"Failed to load Excel file: {e}")

        # Validate schema
        self._validate_schema()
        self._preprocess()

    def _validate_schema(self):
        """Validate that required columns exist in the data."""
        required_data_columns = [
            'Order Number',
            'Order Name',
            'Priority',
            'Resolver',
            'Category',
            'Begin Date',
            'Resolution Date',
            'Resolution Time(m)',
            'Response Time(m)'
        ]

        required_sla_columns = [
            'Priority'
        ]

        # Check Data sheet columns
        missing_data_cols = [col for col in required_data_columns if col not in self.df.columns]
        if missing_data_cols:
            raise ValueError(
                f"Missing required columns in 'Data' sheet: {', '.join(missing_data_cols)}\n"
                f"Found columns: {', '.join(self.df.columns.tolist())}"
            )

        # Check SLA_Criteria sheet columns
        missing_sla_cols = [col for col in required_sla_columns if col not in self.sla_criteria.columns]
        if missing_sla_cols:
            raise ValueError(
                f"Missing required columns in 'SLA_Criteria' sheet: {', '.join(missing_sla_cols)}\n"
                f"Found columns: {', '.join(self.sla_criteria.columns.tolist())}"
            )

        # Check for Resolution and Response columns in SLA_Criteria (flexible naming)
        has_resolution = any('Resolution' in col for col in self.sla_criteria.columns)
        has_response = any('Response' in col for col in self.sla_criteria.columns)

        if not has_resolution:
            raise ValueError(
                "SLA_Criteria sheet must have a column containing 'Resolution' (e.g., 'Resolution Time Limit (h)')"
            )
        if not has_response:
            raise ValueError(
                "SLA_Criteria sheet must have a column containing 'Response' (e.g., 'Response Time Limit (m)')"
            )

        # Validate data types - check if critical columns can be parsed
        if len(self.df) == 0:
            raise ValueError("Data sheet is empty. Please provide incident data.")

        if len(self.sla_criteria) == 0:
            raise ValueError("SLA_Criteria sheet is empty. Please provide SLA criteria (P1-P4).")
        
    def _preprocess(self):
        """Clean and enrich the data."""
        df = self.df
        
        # Standardize strings
        df['Priority'] = df['Priority'].astype(str).str.strip()
        df['Resolver'] = df['Resolver'].fillna('Unassigned').astype(str).str.strip()
        df['Category'] = df['Category'].fillna('Uncategorized').astype(str).str.strip()
        df['Order Name'] = df['Order Name'].fillna('').astype(str)
        
        # Parse dates
        df['Begin Date'] = pd.to_datetime(df['Begin Date'], errors='coerce')
        df['Resolution Date'] = pd.to_datetime(df['Resolution Date'], errors='coerce')
        
        # Calculate hours from minutes
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
        
        # Determine SLA violations
        df['SLA_Res_Violated'] = df['Resolution_Hours'] > df['SLA_Res_Limit_Hours']
        df['SLA_Res_Overage_Hours'] = (df['Resolution_Hours'] - df['SLA_Res_Limit_Hours']).clip(lower=0)
        
        # Time features
        df['DayOfWeek'] = df['Begin Date'].dt.day_name()
        df['Hour'] = df['Begin Date'].dt.hour
        df['Week'] = df['Begin Date'].dt.isocalendar().week
        df['Month'] = df['Begin Date'].dt.to_period('M')
        
        # Period split for trend (first half vs second half)
        if df['Begin Date'].notna().any():
            min_date = df['Begin Date'].min()
            max_date = df['Begin Date'].max()
            mid_date = min_date + (max_date - min_date) / 2
            df['Period'] = np.where(df['Begin Date'] > mid_date, 'Current', 'Previous')
        else:
            df['Period'] = 'Current'
            
        # Filter out invalid data
        df = df[df['Resolution Time(m)'] >= 0]
        self.df = df
        
    def analyze_all(self):
        """Run all analysis dimensions."""
        # First, populate all analysis results
        self.results = {
            'summary': self._analyze_summary(),
            'sla': self._analyze_sla(),
            'priority': self._analyze_priority(),
            'personnel': self._analyze_personnel(),
            'category': self._analyze_category(),
            'time': self._analyze_time(),
            'violations': self._analyze_violations(),
        }
        # Now generate recommendations based on populated results
        self.results['recommendations'] = self._generate_recommendations()
        return self.results

    
    def _calc_trend(self, curr_val, prev_val):
        """Calculate percentage change."""
        if prev_val == 0:
            return 0.0
        return ((curr_val - prev_val) / prev_val) * 100
    
    def _analyze_summary(self):
        """Dimension 1: Executive Summary."""
        df = self.df
        curr = df[df['Period'] == 'Current']
        prev = df[df['Period'] == 'Previous']
        
        total = len(df)
        sla_rate = ((total - df['SLA_Res_Violated'].sum()) / total) * 100 if total > 0 else 0
        avg_mttr = df['Resolution_Hours'].mean()
        p1_count = len(df[df['Priority'] == 'P1'])
        p2_count = len(df[df['Priority'] == 'P2'])
        
        # Trends
        vol_trend = self._calc_trend(len(curr), len(prev))
        mttr_curr = curr['Resolution_Hours'].mean() if len(curr) > 0 else 0
        mttr_prev = prev['Resolution_Hours'].mean() if len(prev) > 0 else 0
        mttr_trend = self._calc_trend(mttr_curr, mttr_prev)
        
        # Date range
        date_range = f"{df['Begin Date'].min().strftime('%Y-%m-%d')} ~ {df['Begin Date'].max().strftime('%Y-%m-%d')}"
        
        # Anomalies (rule-based)
        anomalies = []
        if sla_rate < 95:
            anomalies.append(f"SLA compliance below 95% ({sla_rate:.1f}%)")
        if vol_trend > 20:
            anomalies.append(f"Incident volume spiked {vol_trend:.1f}%")
        if p1_count > 0:
            anomalies.append(f"{p1_count} P1 incidents occurred this period")
            
        return {
            'total': total,
            'sla_rate': sla_rate,
            'avg_mttr': avg_mttr,
            'p1_count': p1_count,
            'p2_count': p2_count,
            'vol_trend': vol_trend,
            'mttr_trend': mttr_trend,
            'date_range': date_range,
            'anomalies': anomalies,
        }
    
    def _analyze_sla(self):
        """Dimension 2: SLA Analysis."""
        df = self.df
        
        # Overall SLA
        total = len(df)
        violations = df['SLA_Res_Violated'].sum()
        sla_rate = ((total - violations) / total) * 100 if total > 0 else 0
        
        # By Priority
        by_priority = df.groupby('Priority').agg(
            Total=('Order Number', 'count'),
            Violations=('SLA_Res_Violated', 'sum'),
            Avg_MTTR=('Resolution_Hours', 'mean')
        ).reset_index()
        by_priority['SLA_Rate'] = ((by_priority['Total'] - by_priority['Violations']) / by_priority['Total']) * 100
        
        # Violation root cause: by person
        violated_df = df[df['SLA_Res_Violated'] == True]
        by_person = violated_df.groupby('Resolver').size().sort_values(ascending=False).head(10)
        
        # By category
        by_category = violated_df.groupby('Category').size().sort_values(ascending=False).head(10)
        
        # By hour
        by_hour = violated_df.groupby('Hour').size()
        
        # Severity distribution
        severity_bins = [0, 2, 8, 24, float('inf')]
        severity_labels = ['Minor (<2h)', 'Moderate (2-8h)', 'Severe (8-24h)', 'Critical (>24h)']
        violated_df = violated_df.copy()
        violated_df['Severity'] = pd.cut(violated_df['SLA_Res_Overage_Hours'], bins=severity_bins, labels=severity_labels)
        severity_dist = violated_df['Severity'].value_counts()
        
        return {
            'overall_rate': sla_rate,
            'total_violations': int(violations),
            'by_priority': by_priority,
            'violations_by_person': by_person,
            'violations_by_category': by_category,
            'violations_by_hour': by_hour,
            'severity_distribution': severity_dist,
        }
    
    def _analyze_priority(self):
        """Dimension 3: Priority Analysis."""
        df = self.df
        curr = df[df['Period'] == 'Current']
        prev = df[df['Period'] == 'Previous']
        
        # Distribution
        dist = df['Priority'].value_counts()
        dist_pct = (dist / len(df) * 100).round(1)
        
        # MTTR by priority
        mttr_by_priority = df.groupby('Priority')['Resolution_Hours'].agg(['mean', 'median', 'std']).round(2)
        
        # Priority trend
        curr_dist = curr['Priority'].value_counts()
        prev_dist = prev['Priority'].value_counts()
        trend = {}
        for p in ['P1', 'P2', 'P3', 'P4']:
            c = curr_dist.get(p, 0)
            v = prev_dist.get(p, 0)
            trend[p] = self._calc_trend(c, v)
        
        # P1 & P2 case cards
        p1_cases = df[df['Priority'] == 'P1'][['Order Number', 'Order Name', 'Resolver', 'Category', 'Resolution_Hours', 'Begin Date']].to_dict('records')
        p2_cases = df[df['Priority'] == 'P2'][['Order Number', 'Order Name', 'Resolver', 'Category', 'Resolution_Hours', 'Begin Date']].head(10).to_dict('records')
        
        return {
            'distribution': dist,
            'distribution_pct': dist_pct,
            'mttr_by_priority': mttr_by_priority,
            'trend': trend,
            'p1_cases': p1_cases,
            'p2_cases': p2_cases,
        }
    
    def _analyze_personnel(self):
        """Dimension 4: Personnel Analysis."""
        df = self.df
        
        # Exclude Unassigned for rankings
        assigned_df = df[df['Resolver'] != 'Unassigned']
        
        # Volume ranking
        volume_rank = assigned_df.groupby('Resolver').size().sort_values(ascending=False)
        
        # Efficiency matrix data
        efficiency = assigned_df.groupby('Resolver').agg(
            Volume=('Order Number', 'count'),
            Avg_MTTR=('Resolution_Hours', 'mean'),
            SLA_Violations=('SLA_Res_Violated', 'sum')
        ).reset_index()
        efficiency['SLA_Rate'] = ((efficiency['Volume'] - efficiency['SLA_Violations']) / efficiency['Volume'] * 100).round(1)
        
        # SLA violation ranking
        sla_violation_rank = efficiency.sort_values('SLA_Violations', ascending=False).head(10)
        
        # Top performers (high volume, low MTTR)
        efficiency['Score'] = (efficiency['Volume'] / efficiency['Volume'].max()) * 0.5 + \
                              (1 - efficiency['Avg_MTTR'] / efficiency['Avg_MTTR'].max()) * 0.5
        top_performers = efficiency.sort_values('Score', ascending=False).head(5)
        
        # Unassigned analysis
        unassigned_df = df[df['Resolver'] == 'Unassigned']
        unassigned_stats = {
            'count': len(unassigned_df),
            'avg_mttr': unassigned_df['Resolution_Hours'].mean() if len(unassigned_df) > 0 else 0,
            'percentage': len(unassigned_df) / len(df) * 100 if len(df) > 0 else 0,
        }
        
        return {
            'volume_rank': volume_rank,
            'efficiency': efficiency,
            'sla_violation_rank': sla_violation_rank,
            'top_performers': top_performers,
            'unassigned': unassigned_stats,
        }
    
    def _analyze_category(self):
        """Dimension 5: Category Analysis."""
        df = self.df
        curr = df[df['Period'] == 'Current']
        prev = df[df['Period'] == 'Previous']
        
        # Distribution
        dist = df['Category'].value_counts()
        dist_pct = (dist / len(df) * 100).round(1)
        
        # Trend
        curr_dist = curr['Category'].value_counts()
        prev_dist = prev['Category'].value_counts()
        trend = {}
        for cat in dist.index:
            c = curr_dist.get(cat, 0)
            v = prev_dist.get(cat, 0)
            trend[cat] = self._calc_trend(c, v)
        
        # Fastest growing
        trend_sorted = sorted(trend.items(), key=lambda x: x[1], reverse=True)
        fastest_growing = trend_sorted[:5] if trend_sorted else []
        
        # Keyword extraction from Order Name
        text = ' '.join(df['Order Name'].astype(str).tolist()).lower()
        stop_words = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'and', 'or', 'is', 'are', 'was', 'were', 'not', 'no', 'null', 'none'}
        words = re.findall(r'\b[a-z]{3,}\b', text)
        words = [w for w in words if w not in stop_words]
        keywords = Counter(words).most_common(15)
        
        return {
            'distribution': dist,
            'distribution_pct': dist_pct,
            'trend': trend,
            'fastest_growing': fastest_growing,
            'keywords': keywords,
        }
    
    def _analyze_time(self):
        """Dimension 6: Time Analysis."""
        df = self.df
        
        # Heatmap: Day x Hour
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        df['DayOfWeek'] = pd.Categorical(df['DayOfWeek'], categories=days_order, ordered=True)
        heatmap = df.groupby(['DayOfWeek', 'Hour'], observed=False).size().unstack(fill_value=0)
        
        # Peak hours
        hourly = df.groupby('Hour').size()
        peak_hour = hourly.idxmax()
        valley_hour = hourly.idxmin()
        
        # Peak day
        daily = df.groupby('DayOfWeek', observed=False).size()
        peak_day = daily.idxmax()
        
        # Long tail tickets (> 48 hours)
        long_tail_threshold = 48  # hours
        long_tail = df[df['Resolution_Hours'] > long_tail_threshold]
        long_tail_stats = {
            'count': len(long_tail),
            'percentage': len(long_tail) / len(df) * 100 if len(df) > 0 else 0,
            'avg_hours': long_tail['Resolution_Hours'].mean() if len(long_tail) > 0 else 0,
            'samples': long_tail[['Order Number', 'Order Name', 'Resolver', 'Resolution_Hours']].head(10).to_dict('records'),
        }
        
        # Trend by week/month
        monthly_volume = df.groupby('Month').size()
        
        return {
            'heatmap': heatmap,
            'peak_hour': peak_hour,
            'valley_hour': valley_hour,
            'peak_day': peak_day,
            'hourly_distribution': hourly,
            'long_tail': long_tail_stats,
            'monthly_volume': monthly_volume,
        }
    
    def _analyze_violations(self):
        """Dimension 7: All SLA Violations Detail."""
        df = self.df
        violated = df[df['SLA_Res_Violated'] == True].copy()
        violated = violated.sort_values('SLA_Res_Overage_Hours', ascending=False)
        
        columns = ['Order Number', 'Order Name', 'Priority', 'Resolver', 'Category', 
                   'Resolution_Hours', 'SLA_Res_Limit_Hours', 'SLA_Res_Overage_Hours', 'Begin Date']
        
        return {
            'total': len(violated),
            'details': violated[columns].to_dict('records'),
        }
    
    def _generate_recommendations(self):
        """Dimension 8: Auto-generated Recommendations."""
        recs = []
        r = self.results if self.results else {}
        
        # SLA-based recommendations
        if 'sla' in r:
            sla = r['sla']
            if sla['overall_rate'] < 95:
                recs.append({
                    'priority': 'HIGH',
                    'category': 'SLA',
                    'text': f"SLA compliance is only {sla['overall_rate']:.1f}%. Investigate top violating categories and assignees immediately."
                })
            if len(sla.get('violations_by_category', [])) > 0:
                top_cat = sla['violations_by_category'].index[0] if len(sla['violations_by_category']) > 0 else None
                if top_cat:
                    recs.append({
                        'priority': 'MEDIUM',
                        'category': 'SLA',
                        'text': f"'{top_cat}' has the most SLA violations. Consider process optimization or additional resources."
                    })
        
        # Category trend recommendations
        if 'category' in r:
            cat = r['category']
            for name, change in cat.get('fastest_growing', [])[:3]:
                if change > 20:
                    recs.append({
                        'priority': 'MEDIUM',
                        'category': 'Category',
                        'text': f"'{name}' category incidents increased by {change:.1f}%. Investigate root cause."
                    })
        
        # Personnel recommendations
        if 'personnel' in r:
            pers = r['personnel']
            if pers['unassigned']['count'] > 0 and pers['unassigned']['percentage'] > 5:
                recs.append({
                    'priority': 'HIGH',
                    'category': 'Process',
                    'text': f"Unassigned tickets at {pers['unassigned']['percentage']:.1f}%. Improve ticket routing mechanism."
                })
        
        # Time-based recommendations
        if 'time' in r:
            time_data = r['time']
            if time_data['long_tail']['count'] > 0:
                pct = time_data['long_tail']['percentage']
                if pct > 5:
                    recs.append({
                        'priority': 'MEDIUM',
                        'category': 'Efficiency',
                        'text': f"{pct:.1f}% of tickets took over 48 hours. Implement escalation procedures."
                    })
        
        # Priority recommendations
        if 'summary' in r:
            summary = r['summary']
            if summary['p1_count'] > 0:
                recs.append({
                    'priority': 'HIGH',
                    'category': 'Critical',
                    'text': f"{summary['p1_count']} P1 incidents occurred. Conduct post-mortems and implement preventive measures."
                })
        
        return recs

