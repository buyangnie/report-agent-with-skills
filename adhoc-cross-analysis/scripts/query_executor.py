"""
Query Executor for Adhoc Analysis.
Executes queries against pre-aggregated data.
"""


class QueryExecutor:
    def __init__(self, data_loader):
        self.loader = data_loader
        self.data = data_loader.aggregated

    def execute(self, intent):
        """
        Execute query based on intent.

        Returns:
            dict: {
                'data': list of results,
                'summary': summary statistics,
                'samples': evidence samples
            }
        """
        query_type = intent['type']

        if query_type == 'ranking':
            return self._execute_ranking(intent)
        elif query_type == 'trend':
            return self._execute_trend(intent)
        elif query_type == 'breakdown':
            return self._execute_breakdown(intent)
        elif query_type == 'comparison':
            return self._execute_comparison(intent)
        elif query_type == 'drilldown':
            return self._execute_drilldown(intent)
        else:
            return self._execute_ranking(intent)  # Default to ranking

    def _execute_ranking(self, intent):
        """Execute ranking query."""
        dimension = intent['dimension']
        metric = intent['metric']
        order = intent['order']
        limit = intent['limit']

        # Map dimension to aggregated data key
        dim_map = {
            'priority': 'by_priority',
            'category': 'by_category',
            'team': 'by_team',
            'resolver': 'by_resolver',
            'time': 'by_week',
        }

        data_key = dim_map.get(dimension, 'by_category')
        dim_data = self.data.get(data_key, {})

        # Map metric to field
        metric_map = {
            'volume': 'count',
            'sla_rate': 'sla_rate',
            'mttr': 'avg_mttr',
            'violations': 'violations',
        }
        field = metric_map.get(metric, 'sla_rate')

        # Sort and limit
        items = [(name, vals) for name, vals in dim_data.items()]
        reverse = (order == 'desc')

        # For SLA rate with "worst", we want ascending (lower is worse)
        if metric == 'sla_rate' and order == 'asc':
            reverse = False
        elif metric == 'sla_rate' and order == 'desc':
            reverse = True

        items.sort(key=lambda x: x[1].get(field, 0), reverse=reverse)
        items = items[:limit]

        # Build result
        result_data = []
        for name, vals in items:
            result_data.append({
                'name': name,
                'value': vals.get(field, 0),
                'count': vals.get('count', 0),
                'sla_rate': vals.get('sla_rate', 0),
                'avg_mttr': vals.get('avg_mttr', 0),
                'violations': vals.get('violations', 0),
            })

        # Get samples for top result
        samples = []
        if result_data and dimension in ['category', 'team', 'resolver', 'priority']:
            top_name = result_data[0]['name']
            samples = self.loader.get_samples(dimension, top_name, limit=5)

        # Summary
        summary = self.data.get('summary', {})

        return {
            'data': result_data,
            'summary': summary,
            'samples': samples,
            'dimension': dimension,
            'metric': metric,
            'order': order,
        }

    def _execute_trend(self, intent):
        """Execute trend query."""
        metric = intent['metric']

        # Use weekly or monthly data
        time_data = self.data.get('by_week', {})
        if not time_data:
            time_data = self.data.get('by_month', {})

        metric_map = {
            'volume': 'count',
            'sla_rate': 'sla_rate',
            'mttr': 'avg_mttr',
            'violations': 'violations',
        }
        field = metric_map.get(metric, 'count')

        # Sort by time
        items = [(name, vals) for name, vals in time_data.items()]
        items.sort(key=lambda x: x[0])

        result_data = []
        for name, vals in items[-12:]:  # Last 12 periods
            result_data.append({
                'name': name,
                'value': vals.get(field, 0),
                'count': vals.get('count', 0),
            })

        # Calculate trend direction
        if len(result_data) >= 2:
            first_val = result_data[0]['value']
            last_val = result_data[-1]['value']
            if first_val > 0:
                change_pct = (last_val - first_val) / first_val * 100
            else:
                change_pct = 0
        else:
            change_pct = 0

        return {
            'data': result_data,
            'summary': self.data.get('summary', {}),
            'samples': [],
            'metric': metric,
            'trend_change': round(change_pct, 1),
        }

    def _execute_breakdown(self, intent):
        """Execute breakdown/distribution query."""
        dimension = intent['dimension']

        dim_map = {
            'priority': 'by_priority',
            'category': 'by_category',
            'team': 'by_team',
            'resolver': 'by_resolver',
        }

        data_key = dim_map.get(dimension, 'by_category')
        dim_data = self.data.get(data_key, {})

        # Calculate percentages
        total = sum(v.get('count', 0) for v in dim_data.values())

        result_data = []
        for name, vals in dim_data.items():
            count = vals.get('count', 0)
            result_data.append({
                'name': name,
                'count': count,
                'percentage': round(count / total * 100, 1) if total > 0 else 0,
                'sla_rate': vals.get('sla_rate', 0),
            })

        # Sort by count
        result_data.sort(key=lambda x: x['count'], reverse=True)
        result_data = result_data[:10]

        return {
            'data': result_data,
            'summary': self.data.get('summary', {}),
            'samples': [],
            'dimension': dimension,
            'total': total,
        }

    def _execute_comparison(self, intent):
        """Execute comparison query (WoW, MoM)."""
        comparisons = self.data.get('comparisons', {})

        result_data = []

        if 'wow' in comparisons and comparisons['wow']:
            wow = comparisons['wow']
            result_data.append({
                'type': 'wow',
                'label': 'Week over Week',
                'current': wow.get('current', ''),
                'previous': wow.get('previous', ''),
                'volume_change': wow.get('volume_change', 0),
                'sla_change': wow.get('sla_change', 0),
            })

        if 'mom' in comparisons and comparisons['mom']:
            mom = comparisons['mom']
            result_data.append({
                'type': 'mom',
                'label': 'Month over Month',
                'current': mom.get('current', ''),
                'previous': mom.get('previous', ''),
                'volume_change': mom.get('volume_change', 0),
                'sla_change': mom.get('sla_change', 0),
            })

        return {
            'data': result_data,
            'summary': self.data.get('summary', {}),
            'samples': [],
        }

    def _execute_drilldown(self, intent):
        """Execute drilldown query - find reasons for issues."""
        dimension = intent['dimension']
        metric = intent['metric']

        # First, find the worst performers
        ranking_intent = {
            'type': 'ranking',
            'dimension': dimension,
            'metric': metric,
            'order': 'asc' if metric == 'sla_rate' else 'desc',
            'limit': 3,
        }
        ranking_result = self._execute_ranking(ranking_intent)

        # For each worst performer, get breakdown
        drilldown_data = []
        for item in ranking_result['data']:
            name = item['name']
            drilldown_data.append({
                'name': name,
                'value': item['value'],
                'count': item['count'],
                'violations': item['violations'],
                'samples': self.loader.get_samples(dimension, name, limit=3),
            })

        return {
            'data': drilldown_data,
            'summary': self.data.get('summary', {}),
            'samples': ranking_result.get('samples', []),
            'dimension': dimension,
            'metric': metric,
        }
