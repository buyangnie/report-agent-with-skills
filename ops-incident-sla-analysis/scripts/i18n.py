"""
Internationalization for SLA Violation Analysis Report.
"""

TEXTS = {
    'en': {
        'report_title': 'SLA Violation Analysis Report',
        'sla_overview': 'SLA Overview',
        'risk_analysis': 'Risk Analysis',
        'violation_deep_dive': 'Violation Deep Dive',
        'attribution_analysis': 'Attribution Analysis',
        'recommendations': 'Recommendations',

        'total_tickets': 'Total Tickets',
        'sla_compliance': 'SLA Compliance Rate',
        'total_violations': 'Total Violations',
        'high_risk_count': 'High Risk Tickets',
        'data_period': 'Data Period',

        'response_sla': 'Response SLA',
        'resolution_sla': 'Resolution SLA',
        'by_priority': 'By Priority',
        'by_category': 'By Category',
        'by_team': 'By Team',

        'risk_level': 'Risk Level',
        'high_risk': 'High Risk',
        'medium_risk': 'Medium Risk',
        'low_risk': 'Low Risk',

        'attribution_process': 'Process Factors',
        'attribution_resource': 'Resource Factors',
        'attribution_external': 'External Dependencies',
        'attribution_timewindow': 'Time Window Factors',

        'order_number': 'Order Number',
        'priority': 'Priority',
        'category': 'Category',
        'resolver': 'Resolver',
        'resolution_time': 'Resolution Time',
        'sla_limit': 'SLA Limit',
        'overage': 'Overage',
        'attribution': 'Attribution',

        'generation_complete': 'Report generation complete',
        'output_files': 'Output Files',
    },
    'zh': {
        'report_title': 'SLA 违约归因分析报告',
        'sla_overview': 'SLA 总览',
        'risk_analysis': '风险分析',
        'violation_deep_dive': '违约深挖',
        'attribution_analysis': '归因分析',
        'recommendations': '改进建议',

        'total_tickets': '工单总数',
        'sla_compliance': 'SLA 达成率',
        'total_violations': '违约总数',
        'high_risk_count': '高风险工单',
        'data_period': '数据周期',

        'response_sla': '响应 SLA',
        'resolution_sla': '解决 SLA',
        'by_priority': '按优先级',
        'by_category': '按类别',
        'by_team': '按团队',

        'risk_level': '风险等级',
        'high_risk': '高风险',
        'medium_risk': '中风险',
        'low_risk': '低风险',

        'attribution_process': '流程因素',
        'attribution_resource': '资源因素',
        'attribution_external': '外部依赖',
        'attribution_timewindow': '时间窗因素',

        'order_number': '工单号',
        'priority': '优先级',
        'category': '类别',
        'resolver': '处理人',
        'resolution_time': '解决时间',
        'sla_limit': 'SLA 限制',
        'overage': '超时',
        'attribution': '归因',

        'generation_complete': '报告生成完成',
        'output_files': '输出文件',
    }
}


def get_text(key, lang='en'):
    """Get localized text."""
    return TEXTS.get(lang, TEXTS['en']).get(key, key)


def get_report_filename(lang='en'):
    """Get report filename with language suffix."""
    suffix = 'EN' if lang == 'en' else 'CN'
    return f'SLA_Violation_Analysis_{suffix}'
