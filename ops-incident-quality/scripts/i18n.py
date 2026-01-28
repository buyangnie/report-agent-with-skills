"""
Internationalization (i18n) support for report generation
Provides text resources for English and Chinese languages
"""

from datetime import datetime
from typing import Dict, Any


# Language text resources
TEXTS = {
    'en': {
        # Report titles
        'report_title': 'Incident Quality Report',
        'report_subtitle': 'IT Operations Department',
        'data_period': 'Data Period',
        'report_generated': 'Report Generated',

        # Section titles
        'executive_summary': 'Executive Summary',
        'sla_analysis': 'SLA Compliance Analysis',
        'priority_analysis': 'Priority Distribution & MTTR',
        'personnel_analysis': 'Personnel Performance Analysis',
        'category_analysis': 'Category Analysis',
        'time_analysis': 'Time Pattern Analysis',
        'sla_violations': 'SLA Violations Detail',
        'recommendations': 'Recommendations',

        # KPI labels
        'total_tickets': 'Total Tickets',
        'sla_compliance': 'SLA Compliance',
        'avg_mttr': 'Avg MTTR',
        'p1_incidents': 'P1 Incidents',
        'p2_incidents': 'P2 Incidents',

        # Insight labels
        'ai_insight': 'AI Executive Insight',
        'ai_insight_sla': 'AI SLA Insight',
        'ai_insight_priority': 'AI Priority Insight',
        'ai_insight_personnel': 'AI Personnel Insight',
        'ai_insight_category': 'AI Category Insight',
        'ai_insight_time': 'AI Time Insight',

        # Table headers
        'priority': 'Priority',
        'tickets': 'Tickets',
        'percentage': 'Percentage',
        'sla_rate': 'SLA Rate',
        'avg_resolution': 'Avg Resolution',
        'resolver': 'Resolver',
        'category': 'Category',
        'violations': 'Violations',
        'order_number': 'Order Number',
        'order_name': 'Order Name',
        'begin_date': 'Begin Date',
        'resolution_date': 'Resolution Date',
        'resolution_hours': 'Resolution (h)',
        'sla_target': 'SLA Target (h)',
        'overage': 'Overage (h)',

        # Chart titles (kept in English as per requirement)
        'chart_sla_rate': 'SLA Compliance Rate by Priority',
        'chart_sla_violations': 'SLA Violations by Person',
        'chart_priority_dist': 'Priority Distribution',
        'chart_mttr': 'MTTR by Priority',
        'chart_personnel': 'Personnel Performance Matrix',
        'chart_category': 'Category Distribution',
        'chart_heatmap': 'Incident Heatmap',

        # Summary text
        'key_alerts': 'Key Alerts',
        'p1_alert': 'P1 incidents occurred this period',
        'p2_alert': 'P2 incidents occurred this period',
        'sla_violation_alert': 'SLA violations detected',

        # Recommendation labels
        'rec_sla': '[SLA]',
        'rec_category': '[Category]',
        'rec_time': '[Time]',
        'rec_personnel': '[Personnel]',

        # Output messages
        'output_files': 'Output Files',
        'generation_complete': 'Report generation complete',

        # Time units
        'hours': 'h',
        'minutes': 'm',
        'days': 'd',
    },

    'zh': {
        # Report titles
        'report_title': '事件质量报告',
        'report_subtitle': 'IT 运维部门',
        'data_period': '数据周期',
        'report_generated': '报告生成时间',

        # Section titles
        'executive_summary': '执行摘要',
        'sla_analysis': 'SLA 合规性分析',
        'priority_analysis': '优先级分布与 MTTR',
        'personnel_analysis': '人员绩效分析',
        'category_analysis': '类别分析',
        'time_analysis': '时间模式分析',
        'sla_violations': 'SLA 违规详情',
        'recommendations': '改进建议',

        # KPI labels
        'total_tickets': '工单总数',
        'sla_compliance': 'SLA 合规率',
        'avg_mttr': '平均 MTTR',
        'p1_incidents': 'P1 事件',
        'p2_incidents': 'P2 事件',

        # Insight labels
        'ai_insight': 'AI 执行洞察',
        'ai_insight_sla': 'AI SLA 洞察',
        'ai_insight_priority': 'AI 优先级洞察',
        'ai_insight_personnel': 'AI 人员洞察',
        'ai_insight_category': 'AI 类别洞察',
        'ai_insight_time': 'AI 时间洞察',

        # Table headers
        'priority': '优先级',
        'tickets': '工单数',
        'percentage': '百分比',
        'sla_rate': 'SLA 达标率',
        'avg_resolution': '平均解决时间',
        'resolver': '处理人',
        'category': '类别',
        'violations': '违规次数',
        'order_number': '工单号',
        'order_name': '工单名称',
        'begin_date': '创建时间',
        'resolution_date': '解决时间',
        'resolution_hours': '解决时长（小时）',
        'sla_target': 'SLA 目标（小时）',
        'overage': '超时（小时）',

        # Chart titles (kept in English as per requirement)
        'chart_sla_rate': 'SLA Compliance Rate by Priority',
        'chart_sla_violations': 'SLA Violations by Person',
        'chart_priority_dist': 'Priority Distribution',
        'chart_mttr': 'MTTR by Priority',
        'chart_personnel': 'Personnel Performance Matrix',
        'chart_category': 'Category Distribution',
        'chart_heatmap': 'Incident Heatmap',

        # Summary text
        'key_alerts': '关键警报',
        'p1_alert': '个 P1 事件发生在本周期',
        'p2_alert': '个 P2 事件发生在本周期',
        'sla_violation_alert': '个 SLA 违规被检测到',

        # Recommendation labels
        'rec_sla': '[SLA]',
        'rec_category': '[类别]',
        'rec_time': '[时间]',
        'rec_personnel': '[人员]',

        # Output messages
        'output_files': '输出文件',
        'generation_complete': '报告生成完成',

        # Time units
        'hours': '小时',
        'minutes': '分钟',
        'days': '天',
    }
}


def get_text(key: str, lang: str = 'en') -> str:
    """
    Get localized text by key

    Args:
        key: Text key
        lang: Language code ('en' or 'zh')

    Returns:
        Localized text string
    """
    return TEXTS.get(lang, TEXTS['en']).get(key, TEXTS['en'].get(key, key))


def format_date_range(start_date: str, end_date: str, lang: str = 'en') -> str:
    """
    Format date range according to language

    Args:
        start_date: Start date string (YYYY-MM-DD)
        end_date: End date string (YYYY-MM-DD)
        lang: Language code

    Returns:
        Formatted date range string
    """
    if lang == 'zh':
        # Chinese format: 2024年04月19日 至 2025年07月06日
        try:
            start = datetime.strptime(str(start_date)[:10], '%Y-%m-%d')
            end = datetime.strptime(str(end_date)[:10], '%Y-%m-%d')
            return f"{start.strftime('%Y年%m月%d日')} 至 {end.strftime('%Y年%m月%d日')}"
        except:
            return f"{start_date} 至 {end_date}"
    else:
        # English format: 2024-04-19 to 2025-07-06
        return f"{str(start_date)[:10]} to {str(end_date)[:10]}"


def format_date(date_str: str, lang: str = 'en') -> str:
    """
    Format single date according to language

    Args:
        date_str: Date string
        lang: Language code

    Returns:
        Formatted date string
    """
    if lang == 'zh':
        try:
            date_obj = datetime.strptime(str(date_str)[:10], '%Y-%m-%d')
            return date_obj.strftime('%Y年%m月%d日')
        except:
            return str(date_str)
    else:
        return str(date_str)[:10]


def get_report_filename(start_date: str, end_date: str, lang: str = 'en', ext: str = 'html') -> str:
    """
    Generate report filename with language suffix

    Args:
        start_date: Start date string
        end_date: End date string
        lang: Language code
        ext: File extension (html, docx, pptx)

    Returns:
        Filename string
    """
    start = str(start_date)[:10]
    end = str(end_date)[:10]
    lang_suffix = 'EN' if lang == 'en' else 'CN'

    return f"Incident_Quality_Report_{start}_to_{end}_{lang_suffix}.{ext}"


def get_all_texts(lang: str = 'en') -> Dict[str, str]:
    """
    Get all text resources for a language

    Args:
        lang: Language code

    Returns:
        Dictionary of all text resources
    """
    return TEXTS.get(lang, TEXTS['en']).copy()
