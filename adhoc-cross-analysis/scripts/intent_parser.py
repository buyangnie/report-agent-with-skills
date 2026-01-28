"""
Intent Parser for Adhoc Analysis.
Parses user query to extract analysis intent using rule-based matching.
"""
import re
from config import (
    TYPE_KEYWORDS, DIMENSION_KEYWORDS, METRIC_KEYWORDS, ORDER_KEYWORDS,
    DEFAULT_LIMIT, DEFAULT_METRIC, DEFAULT_DIMENSION, DEFAULT_ORDER
)


class IntentParser:
    def __init__(self):
        pass

    def parse(self, query):
        """
        Parse user query to extract intent.

        Returns:
            dict: {
                'type': 'ranking|trend|breakdown|comparison|drilldown',
                'dimension': 'priority|category|team|resolver|time',
                'metric': 'volume|sla_rate|mttr|violations',
                'order': 'asc|desc',
                'limit': int,
                'filters': dict
            }
        """
        query_lower = query.lower()

        intent = {
            'type': self._detect_type(query_lower),
            'dimension': self._detect_dimension(query_lower),
            'metric': self._detect_metric(query_lower),
            'order': self._detect_order(query_lower),
            'limit': self._detect_limit(query_lower),
            'filters': self._detect_filters(query_lower),
            'raw_query': query
        }

        # Apply defaults
        if not intent['type']:
            intent['type'] = 'ranking'
        if not intent['dimension']:
            intent['dimension'] = DEFAULT_DIMENSION
        if not intent['metric']:
            intent['metric'] = DEFAULT_METRIC
        if not intent['order']:
            # Infer order from type and metric
            if intent['metric'] == 'sla_rate':
                intent['order'] = 'asc' if '差' in query or 'worst' in query_lower else 'desc'
            else:
                intent['order'] = 'desc' if '多' in query or 'most' in query_lower else 'asc'
        if not intent['limit']:
            intent['limit'] = DEFAULT_LIMIT

        return intent

    def _detect_type(self, query):
        """Detect analysis type from query."""
        for type_name, keywords in TYPE_KEYWORDS.items():
            all_keywords = keywords['zh'] + keywords['en']
            for kw in all_keywords:
                if kw.lower() in query:
                    return type_name
        return None

    def _detect_dimension(self, query):
        """Detect dimension from query."""
        for dim_name, keywords in DIMENSION_KEYWORDS.items():
            all_keywords = keywords['zh'] + keywords['en']
            for kw in all_keywords:
                if kw.lower() in query:
                    return dim_name
        return None

    def _detect_metric(self, query):
        """Detect metric from query."""
        for metric_name, keywords in METRIC_KEYWORDS.items():
            all_keywords = keywords['zh'] + keywords['en']
            for kw in all_keywords:
                if kw.lower() in query:
                    return metric_name
        return None

    def _detect_order(self, query):
        """Detect sort order from query."""
        for order_name, keywords in ORDER_KEYWORDS.items():
            all_keywords = keywords['zh'] + keywords['en']
            for kw in all_keywords:
                if kw.lower() in query:
                    return order_name
        return None

    def _detect_limit(self, query):
        """Detect limit from query (e.g., "top 10")."""
        # Match patterns like "top 5", "前10", "10个"
        patterns = [
            r'top\s*(\d+)',
            r'前\s*(\d+)',
            r'(\d+)\s*个',
            r'(\d+)\s*名',
        ]
        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                return int(match.group(1))
        return None

    def _detect_filters(self, query):
        """Detect any filters (e.g., specific priority, time range)."""
        filters = {}

        # Detect specific priority
        priority_match = re.search(r'p([1-4])', query.lower())
        if priority_match:
            filters['priority'] = f'P{priority_match.group(1)}'

        # Detect time references
        if '本周' in query or 'this week' in query.lower():
            filters['time_range'] = 'this_week'
        elif '上周' in query or 'last week' in query.lower():
            filters['time_range'] = 'last_week'
        elif '本月' in query or 'this month' in query.lower():
            filters['time_range'] = 'this_month'
        elif '上月' in query or 'last month' in query.lower():
            filters['time_range'] = 'last_month'

        return filters

    def describe_intent(self, intent, lang='zh'):
        """Generate human-readable description of intent."""
        type_names = {
            'ranking': {'zh': '排名分析', 'en': 'Ranking Analysis'},
            'trend': {'zh': '趋势分析', 'en': 'Trend Analysis'},
            'breakdown': {'zh': '分布分析', 'en': 'Breakdown Analysis'},
            'comparison': {'zh': '对比分析', 'en': 'Comparison Analysis'},
            'drilldown': {'zh': '下钻分析', 'en': 'Drilldown Analysis'},
        }

        dim_names = {
            'priority': {'zh': '优先级', 'en': 'Priority'},
            'category': {'zh': '类别', 'en': 'Category'},
            'team': {'zh': '团队', 'en': 'Team'},
            'resolver': {'zh': '处理人', 'en': 'Resolver'},
            'time': {'zh': '时间', 'en': 'Time'},
        }

        metric_names = {
            'volume': {'zh': '工单量', 'en': 'Volume'},
            'sla_rate': {'zh': 'SLA 达成率', 'en': 'SLA Rate'},
            'mttr': {'zh': 'MTTR', 'en': 'MTTR'},
            'violations': {'zh': '违约数', 'en': 'Violations'},
        }

        type_str = type_names.get(intent['type'], {}).get(lang, intent['type'])
        dim_str = dim_names.get(intent['dimension'], {}).get(lang, intent['dimension'])
        metric_str = metric_names.get(intent['metric'], {}).get(lang, intent['metric'])

        if lang == 'zh':
            return f"{type_str}: 按 {dim_str} 分析 {metric_str}"
        else:
            return f"{type_str}: Analyze {metric_str} by {dim_str}"
