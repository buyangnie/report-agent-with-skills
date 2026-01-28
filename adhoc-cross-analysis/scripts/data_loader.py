"""
Data Loader and Preprocessor for Adhoc Analysis.
Loads Excel data and pre-computes aggregations.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class DataLoader:
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = None
        self.sla_criteria = None
        self.aggregated = {}

    def load(self):
        """Load and preprocess data."""
        self.sla_criteria = pd.read_excel(self.filepath, sheet_name='SLA_Criteria')
        self.df = pd.read_excel(self.filepath, sheet_name='Data')
        self._preprocess()
        self._aggregate()
        return self

    def _preprocess(self):
        """Clean and enrich data."""
        df = self.df

        # Standardize strings
        df['Priority'] = df['Priority'].astype(str).str.strip()
        df['Resolver'] = df['Resolver'].fillna('Unassigned').astype(str).str.strip()
        df['Category'] = df['Category'].fillna('Uncategorized').astype(str).str.strip()

        # Team extraction (from Assignment Group or use Category)
        if 'Assignment Group' in df.columns:
            df['Team'] = df['Assignment Group'].fillna('Unassigned').astype(str).str.strip()
        else:
            df['Team'] = df['Category']

        # Parse dates
        df['Begin Date'] = pd.to_datetime(df['Begin Date'], errors='coerce')
        df['Resolution Date'] = pd.to_datetime(df['Resolution Date'], errors='coerce')

        # Calculate hours
        df['Resolution_Hours'] = df['Resolution Time(m)'] / 60.0

        # Map SLA thresholds
        self.sla_criteria['Priority'] = self.sla_criteria['Priority'].astype(str).str.strip()
        res_col = [c for c in self.sla_criteria.columns if 'Resolution' in c][0]

        sla_res_map = dict(zip(self.sla_criteria['Priority'], self.sla_criteria[res_col]))
        df['SLA_Res_Limit_Hours'] = df['Priority'].map(sla_res_map)

        # SLA violation flag
        df['SLA_Violated'] = df['Resolution_Hours'] > df['SLA_Res_Limit_Hours']

        # Time features
        df['Week'] = df['Begin Date'].dt.strftime('%Y-W%V')
        df['Month'] = df['Begin Date'].dt.strftime('%Y-%m')
        df['Date'] = df['Begin Date'].dt.date

        # Filter invalid data
        df = df[df['Resolution Time(m)'] >= 0]
        self.df = df

    def _aggregate(self):
        """Pre-compute aggregations for all dimensions."""
        df = self.df

        # Summary
        total = len(df)
        violations = df['SLA_Violated'].sum()
        self.aggregated['summary'] = {
            'total': total,
            'violations': int(violations),
            'sla_rate': round((total - violations) / total * 100, 1) if total > 0 else 0,
            'avg_mttr': round(df['Resolution_Hours'].mean(), 1),
            'period': f"{df['Begin Date'].min().strftime('%Y-%m-%d')} ~ {df['Begin Date'].max().strftime('%Y-%m-%d')}"
        }

        # By Priority
        self.aggregated['by_priority'] = self._aggregate_by(df, 'Priority')

        # By Category
        self.aggregated['by_category'] = self._aggregate_by(df, 'Category')

        # By Team
        self.aggregated['by_team'] = self._aggregate_by(df, 'Team')

        # By Resolver
        self.aggregated['by_resolver'] = self._aggregate_by(df, 'Resolver')

        # By Week
        self.aggregated['by_week'] = self._aggregate_by(df, 'Week')

        # By Month
        self.aggregated['by_month'] = self._aggregate_by(df, 'Month')

        # Comparisons (WoW, MoM)
        self.aggregated['comparisons'] = self._compute_comparisons(df)

    def _aggregate_by(self, df, column):
        """Aggregate metrics by a dimension."""
        result = {}
        grouped = df.groupby(column)

        for name, group in grouped:
            total = len(group)
            violations = group['SLA_Violated'].sum()
            result[str(name)] = {
                'count': total,
                'violations': int(violations),
                'sla_rate': round((total - violations) / total * 100, 1) if total > 0 else 0,
                'avg_mttr': round(group['Resolution_Hours'].mean(), 1),
            }

        return result

    def _compute_comparisons(self, df):
        """Compute week-over-week and month-over-month comparisons."""
        result = {'wow': {}, 'mom': {}}

        # Get current and previous week
        weeks = sorted(df['Week'].dropna().unique())
        if len(weeks) >= 2:
            curr_week = weeks[-1]
            prev_week = weeks[-2]
            curr_data = df[df['Week'] == curr_week]
            prev_data = df[df['Week'] == prev_week]

            curr_vol = len(curr_data)
            prev_vol = len(prev_data)
            curr_sla = (len(curr_data) - curr_data['SLA_Violated'].sum()) / len(curr_data) * 100 if len(curr_data) > 0 else 0
            prev_sla = (len(prev_data) - prev_data['SLA_Violated'].sum()) / len(prev_data) * 100 if len(prev_data) > 0 else 0

            result['wow'] = {
                'volume_change': round((curr_vol - prev_vol) / prev_vol * 100, 1) if prev_vol > 0 else 0,
                'sla_change': round(curr_sla - prev_sla, 1),
                'current': curr_week,
                'previous': prev_week
            }

        # Get current and previous month
        months = sorted(df['Month'].dropna().unique())
        if len(months) >= 2:
            curr_month = months[-1]
            prev_month = months[-2]
            curr_data = df[df['Month'] == curr_month]
            prev_data = df[df['Month'] == prev_month]

            curr_vol = len(curr_data)
            prev_vol = len(prev_data)
            curr_sla = (len(curr_data) - curr_data['SLA_Violated'].sum()) / len(curr_data) * 100 if len(curr_data) > 0 else 0
            prev_sla = (len(prev_data) - prev_data['SLA_Violated'].sum()) / len(prev_data) * 100 if len(prev_data) > 0 else 0

            result['mom'] = {
                'volume_change': round((curr_vol - prev_vol) / prev_vol * 100, 1) if prev_vol > 0 else 0,
                'sla_change': round(curr_sla - prev_sla, 1),
                'current': curr_month,
                'previous': prev_month
            }

        return result

    def get_samples(self, dimension, value, limit=5):
        """Get sample tickets for a specific dimension value."""
        df = self.df

        # Map dimension to column
        col_map = {
            'priority': 'Priority',
            'category': 'Category',
            'team': 'Team',
            'resolver': 'Resolver',
        }

        col = col_map.get(dimension)
        if not col:
            return []

        filtered = df[df[col] == value].sort_values('Resolution_Hours', ascending=False)

        samples = []
        for _, row in filtered.head(limit).iterrows():
            samples.append({
                'order_number': row['Order Number'],
                'priority': row['Priority'],
                'category': row['Category'],
                'resolver': row['Resolver'],
                'mttr': round(row['Resolution_Hours'], 1),
                'violated': bool(row['SLA_Violated']),
            })

        return samples
