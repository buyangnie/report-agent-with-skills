"""
Configuration for Adhoc Cross Analysis.
"""
import os

# ============================================
# PATHS
# ============================================

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(SKILL_DIR, 'data')
OUTPUT_DIR = os.path.join(SKILL_DIR, 'output')
SCRIPTS_DIR = os.path.join(SKILL_DIR, 'scripts')

# ============================================
# ANALYSIS TYPES
# ============================================

ANALYSIS_TYPES = ['ranking', 'trend', 'breakdown', 'comparison', 'drilldown']

# ============================================
# DIMENSIONS
# ============================================

DIMENSIONS = ['priority', 'category', 'team', 'resolver', 'time']

# ============================================
# METRICS
# ============================================

METRICS = ['volume', 'sla_rate', 'mttr', 'violations']

# ============================================
# KEYWORD PATTERNS
# ============================================

# Analysis type keywords
TYPE_KEYWORDS = {
    'ranking': {
        'zh': ['最好', '最差', '最多', '最少', '排名', 'top', 'bottom', '第一', '最高', '最低'],
        'en': ['best', 'worst', 'most', 'least', 'top', 'bottom', 'rank', 'highest', 'lowest']
    },
    'trend': {
        'zh': ['趋势', '变化', '增长', '下降', '走势', '发展'],
        'en': ['trend', 'change', 'growth', 'decline', 'over time']
    },
    'breakdown': {
        'zh': ['分布', '构成', '占比', '组成', '比例'],
        'en': ['distribution', 'breakdown', 'composition', 'proportion']
    },
    'comparison': {
        'zh': ['对比', '比较', '环比', '同比', 'vs', '相比'],
        'en': ['compare', 'versus', 'vs', 'week-over-week', 'month-over-month', 'wow', 'mom']
    },
    'drilldown': {
        'zh': ['为什么', '原因', '归因', '分析', '深入'],
        'en': ['why', 'reason', 'cause', 'attribution', 'drill']
    }
}

# Dimension keywords
DIMENSION_KEYWORDS = {
    'priority': {
        'zh': ['优先级', 'p1', 'p2', 'p3', 'p4', '级别'],
        'en': ['priority', 'p1', 'p2', 'p3', 'p4', 'level']
    },
    'category': {
        'zh': ['类别', '分类', '类型', '种类'],
        'en': ['category', 'type', 'class']
    },
    'team': {
        'zh': ['团队', '队伍', '组', '小组', '部门'],
        'en': ['team', 'group', 'department']
    },
    'resolver': {
        'zh': ['人员', '处理人', '工程师', '人', '员工'],
        'en': ['resolver', 'engineer', 'person', 'staff', 'assignee']
    },
    'time': {
        'zh': ['时间', '日', '周', '月', '季度', '年'],
        'en': ['time', 'day', 'week', 'month', 'quarter', 'year']
    }
}

# Metric keywords
METRIC_KEYWORDS = {
    'volume': {
        'zh': ['数量', '工单量', '量', '个数', '多少'],
        'en': ['volume', 'count', 'number', 'how many']
    },
    'sla_rate': {
        'zh': ['sla', '达成率', '合规', '达标', '遵从'],
        'en': ['sla', 'compliance', 'rate', 'achievement']
    },
    'mttr': {
        'zh': ['mttr', '解决时间', '时效', '处理时间', '耗时'],
        'en': ['mttr', 'resolution time', 'time to resolve', 'duration']
    },
    'violations': {
        'zh': ['违约', '超时', '违规', '不达标'],
        'en': ['violations', 'breach', 'overdue', 'missed']
    }
}

# Order keywords
ORDER_KEYWORDS = {
    'asc': {
        'zh': ['最差', '最少', '最低', '最慢', '最小'],
        'en': ['worst', 'least', 'lowest', 'slowest', 'minimum']
    },
    'desc': {
        'zh': ['最好', '最多', '最高', '最快', '最大'],
        'en': ['best', 'most', 'highest', 'fastest', 'maximum']
    }
}

# ============================================
# DEFAULT VALUES
# ============================================

DEFAULT_LIMIT = 5
DEFAULT_METRIC = 'sla_rate'
DEFAULT_DIMENSION = 'category'
DEFAULT_ORDER = 'desc'

# ============================================
# LLM CONFIGURATION
# ============================================

LLM_TIMEOUT = 30
LLM_MAX_TOKENS = 500
