"""
Utility functions for Adhoc Cross Analysis.
"""
import os
from config import DATA_DIR, OUTPUT_DIR


def get_data_file():
    """Find Excel file in data directory."""
    for f in os.listdir(DATA_DIR):
        if f.endswith('.xlsx'):
            return os.path.join(DATA_DIR, f)
    raise FileNotFoundError("No Excel file found in data/ directory")


def ensure_dirs():
    """Ensure output directories exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================
# INTERNATIONALIZATION
# ============================================

TEXTS = {
    'en': {
        'report_title': 'Ad-hoc Analysis Report',
        'query': 'Query',
        'result': 'Result',
        'conclusion': 'Conclusion',
        'evidence': 'Evidence Samples',
        'recommendations': 'Recommendations',
        'no_data': 'No data available',
        'analysis_complete': 'Analysis complete',

        # Metrics
        'volume': 'Volume',
        'sla_rate': 'SLA Rate',
        'mttr': 'Avg MTTR',
        'violations': 'Violations',

        # Dimensions
        'priority': 'Priority',
        'category': 'Category',
        'team': 'Team',
        'resolver': 'Resolver',
        'time': 'Time',
    },
    'zh': {
        'report_title': '即席分析报告',
        'query': '查询',
        'result': '结果',
        'conclusion': '结论',
        'evidence': '证据样本',
        'recommendations': '建议',
        'no_data': '无数据',
        'analysis_complete': '分析完成',

        # Metrics
        'volume': '工单量',
        'sla_rate': 'SLA 达成率',
        'mttr': '平均 MTTR',
        'violations': '违约数',

        # Dimensions
        'priority': '优先级',
        'category': '类别',
        'team': '团队',
        'resolver': '处理人',
        'time': '时间',
    }
}


def get_text(key, lang='zh'):
    """Get localized text."""
    return TEXTS.get(lang, TEXTS['zh']).get(key, key)


# ============================================
# DESIGN COLORS
# ============================================

COLORS = {
    'primary': '#3b82f6',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'text': '#374151',
    'border': '#e5e7eb',
    'background': '#f3f4f6',
}
