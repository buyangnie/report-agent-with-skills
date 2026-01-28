"""
Internationalization module for Customer Quality Report.
Comprehensive version supporting all 4 ITIL processes.
"""

TEXTS = {
    "en": {
        # Report Title
        "report_title": "Operation Quality Report",
        "report_subtitle": "Comprehensive ITIL Service Dashboard",

        # Section Titles
        "section_health_score": "Service Health Score",
        "section_process_overview": "Process Overview",
        "section_kpi_dashboard": "Key Performance Indicators",
        "section_sla_breakdown": "SLA Breakdown by Priority",
        "section_risk_radar": "Risk Radar",
        "section_trends": "Trend Analysis",
        "section_actions": "Recommended Actions",
        "section_major_incidents": "Major Incidents",
        "section_failed_changes": "Failed Changes",
        "section_open_problems": "Open Problems",
        "section_summary": "Data Summary",

        # Navigation
        "nav_health": "Health Score",
        "nav_overview": "Process Overview",
        "nav_kpis": "KPI Dashboard",
        "nav_sla": "SLA Details",
        "nav_risks": "Risk Radar",
        "nav_actions": "Actions",
        "nav_details": "Details",

        # Health Score
        "health_score": "Health Score",
        "grade_excellent": "Excellent",
        "grade_good": "Good",
        "grade_needs_improvement": "Needs Improvement",
        "grade_at_risk": "At Risk",
        "vs_previous": "vs previous",

        # Process Names
        "process_incident": "Incident Management",
        "process_change": "Change Management",
        "process_request": "Service Requests",
        "process_problem": "Problem Management",

        # Process Labels
        "total_incidents": "Total Incidents",
        "total_changes": "Total Changes",
        "total_requests": "Total Requests",
        "total_problems": "Total Problems",

        # KPI Labels - Incident
        "kpi_sla_rate": "SLA Compliance",
        "kpi_avg_mttr": "Avg MTTR",
        "kpi_p1_p2_count": "P1/P2 Incidents",
        "kpi_backlog": "Backlog",
        "kpi_total_tickets": "Total Tickets",

        # KPI Labels - Change
        "kpi_change_success_rate": "Change Success Rate",
        "kpi_change_incident_rate": "Change-Induced Incidents",
        "kpi_emergency_change_rate": "Emergency Changes",

        # KPI Labels - Request
        "kpi_request_sla_rate": "Request SLA",
        "kpi_request_csat": "CSAT Score",
        "kpi_request_backlog": "Request Backlog",

        # KPI Labels - Problem
        "kpi_problem_closure_rate": "Problem Closure Rate",
        "kpi_rca_completion_rate": "RCA Completion",
        "kpi_open_problems": "Open Problems",

        # SLA Table
        "sla_priority": "Priority",
        "sla_target": "Target (hours)",
        "sla_total": "Total Tickets",
        "sla_compliant": "Compliant",
        "sla_rate": "SLA Rate",
        "sla_status": "Status",
        "sla_met": "On Target",
        "sla_missed": "Below Target",

        # Trend Labels
        "trend_up": "↑",
        "trend_down": "↓",
        "trend_stable": "→",
        "trend_rising": "Rising",
        "trend_declining": "Declining",
        "trend_stable_label": "Stable",

        # Chart Titles
        "chart_incident_volume": "Incident Volume Trend",
        "chart_sla_trend": "SLA Compliance Trend",
        "chart_mttr_trend": "MTTR Trend",
        "chart_process_distribution": "Process Distribution",
        "chart_health_gauge": "Health Score Gauge",

        # Comparison
        "vs_last_week": "vs Last Week",
        "vs_last_month": "vs Last Month",
        "current_period": "Current Period",
        "previous_period": "Previous Period",
        "change": "Change",
        "wow": "WoW",
        "mom": "MoM",

        # Risk Priorities
        "risk_critical": "CRITICAL",
        "risk_warning": "WARNING",
        "risk_attention": "ATTENTION",

        # Risk Messages
        "risk_sla_low": "Incident SLA compliance at {value:.1%}",
        "risk_sla_impact": "Customer SLO commitments at risk",
        "risk_mttr_high": "Category '{category}' MTTR is {value:.1f}h",
        "risk_mttr_impact": "Extended resolution times affecting service levels",
        "risk_change_fail": "{count} changes failed ({rate:.1%})",
        "risk_change_fail_impact": "Change quality needs improvement",
        "risk_change_incident": "{count} changes caused incidents ({rate:.1%})",
        "risk_change_incident_impact": "Changes are causing service incidents",
        "risk_problem_backlog": "{count} problems remain open",
        "risk_problem_backlog_impact": "Recurring incidents risk if not resolved",

        # Actions
        "action_priority_urgent": "URGENT",
        "action_priority_high": "HIGH",
        "action_priority_medium": "MEDIUM",

        # Action Messages
        "action_improve_sla": "Review and optimize incident SLA compliance processes",
        "action_improve_sla_impact": "Expected: Improve SLA rate by 10-15%",
        "action_reduce_mttr": "Analyze and streamline incident resolution workflow",
        "action_reduce_mttr_impact": "Expected: Reduce average MTTR by 20-30%",
        "action_improve_change": "Strengthen change assessment and testing procedures",
        "action_improve_change_impact": "Expected: Improve change success rate to 95%+",
        "action_reduce_change_incident": "Implement post-change validation and monitoring",
        "action_reduce_change_incident_impact": "Expected: Reduce change-induced incidents by 50%",
        "action_improve_csat": "Analyze customer feedback and improve service delivery",
        "action_improve_csat_impact": "Expected: Improve CSAT to 4.0+",
        "action_close_problems": "Prioritize problem resolution and RCA completion",
        "action_close_problems_impact": "Expected: Reduce recurring incidents by 30%",

        # Table Headers - Incidents
        "col_incident_id": "ID",
        "col_incident_desc": "Description",
        "col_incident_priority": "Priority",
        "col_incident_status": "Status",
        "col_incident_resolution_time": "Resolution Time",

        # Table Headers - Changes
        "col_change_id": "Change ID",
        "col_change_title": "Title",
        "col_change_type": "Type",
        "col_change_status": "Status",
        "col_change_incident": "Incident Caused",

        # Table Headers - Problems
        "col_problem_id": "Problem ID",
        "col_problem_title": "Title",
        "col_problem_status": "Status",
        "col_problem_known_error": "Known Error",
        "col_problem_incidents": "Related Incidents",

        # Data
        "hours": "h",
        "hours_full": "hours",
        "tickets": "tickets",
        "days": "days",
        "yes": "Yes",
        "no": "No",

        # Warnings
        "data_insufficient": "Insufficient data for trend comparison",
        "no_comparison": "No comparison data available",
        "no_risks": "No significant risks identified",
        "no_incidents": "No major incidents in this period",
        "no_failed_changes": "No failed changes in this period",
        "no_open_problems": "No open problems",

        # PPTX Slides
        "slide_cover": "Operation Quality Report",
        "slide_health": "Service Health Score",
        "slide_overview": "Process Overview",
        "slide_kpi": "Key Performance Indicators",
        "slide_sla": "SLA Breakdown",
        "slide_risks": "Risk Radar",
        "slide_trends": "Trend Analysis",
        "slide_incidents": "Major Incidents",
        "slide_changes": "Failed Changes",
        "slide_problems": "Open Problems",
        "slide_actions": "Recommended Actions",

        # Report Meta
        "report_id": "Report ID",
        "analysis_period": "Analysis Period",
        "data_span": "Data Span",
        "generated_on": "Generated on",
        "period": "Analysis Period",
        "to": "to",
        "na": "N/A",

        # Footer
        "footer_confidential": "Confidential - Internal Use Only",
        "footer_generated": "Auto-generated report",
    },

    "zh": {
        # Report Title
        "report_title": "运维质量报告",
        "report_subtitle": "综合 ITIL 服务仪表盘",

        # Section Titles
        "section_health_score": "服务健康评分",
        "section_process_overview": "流程概览",
        "section_kpi_dashboard": "关键绩效指标",
        "section_sla_breakdown": "SLA 分级明细",
        "section_risk_radar": "风险雷达",
        "section_trends": "趋势分析",
        "section_actions": "改进建议",
        "section_major_incidents": "重大事件",
        "section_failed_changes": "失败变更",
        "section_open_problems": "待解决问题",
        "section_summary": "数据摘要",

        # Navigation
        "nav_health": "健康评分",
        "nav_overview": "流程概览",
        "nav_kpis": "KPI仪表盘",
        "nav_sla": "SLA明细",
        "nav_risks": "风险雷达",
        "nav_actions": "改进建议",
        "nav_details": "详情数据",

        # Health Score
        "health_score": "健康评分",
        "grade_excellent": "优秀",
        "grade_good": "良好",
        "grade_needs_improvement": "待改进",
        "grade_at_risk": "风险",
        "vs_previous": "环比",

        # Process Names
        "process_incident": "事件管理",
        "process_change": "变更管理",
        "process_request": "服务请求",
        "process_problem": "问题管理",

        # Process Labels
        "total_incidents": "事件总数",
        "total_changes": "变更总数",
        "total_requests": "请求总数",
        "total_problems": "问题总数",

        # KPI Labels - Incident
        "kpi_sla_rate": "SLA 达成率",
        "kpi_avg_mttr": "平均 MTTR",
        "kpi_p1_p2_count": "P1/P2 事件",
        "kpi_backlog": "积压工单",
        "kpi_total_tickets": "工单总量",

        # KPI Labels - Change
        "kpi_change_success_rate": "变更成功率",
        "kpi_change_incident_rate": "变更引发事件",
        "kpi_emergency_change_rate": "紧急变更率",

        # KPI Labels - Request
        "kpi_request_sla_rate": "请求 SLA",
        "kpi_request_csat": "客户满意度",
        "kpi_request_backlog": "请求积压",

        # KPI Labels - Problem
        "kpi_problem_closure_rate": "问题关闭率",
        "kpi_rca_completion_rate": "RCA 完成率",
        "kpi_open_problems": "待处理问题",

        # SLA Table
        "sla_priority": "优先级",
        "sla_target": "目标 (小时)",
        "sla_total": "工单总数",
        "sla_compliant": "达标数",
        "sla_rate": "SLA 达成率",
        "sla_status": "状态",
        "sla_met": "达标",
        "sla_missed": "未达标",

        # Trend Labels
        "trend_up": "↑",
        "trend_down": "↓",
        "trend_stable": "→",
        "trend_rising": "上升",
        "trend_declining": "下降",
        "trend_stable_label": "稳定",

        # Chart Titles
        "chart_incident_volume": "事件量趋势",
        "chart_sla_trend": "SLA 达成趋势",
        "chart_mttr_trend": "MTTR 趋势",
        "chart_process_distribution": "流程分布",
        "chart_health_gauge": "健康评分仪表",

        # Comparison
        "vs_last_week": "环比上周",
        "vs_last_month": "环比上月",
        "current_period": "本期",
        "previous_period": "上期",
        "change": "变化",
        "wow": "周环比",
        "mom": "月环比",

        # Risk Priorities
        "risk_critical": "严重",
        "risk_warning": "警告",
        "risk_attention": "关注",

        # Risk Messages
        "risk_sla_low": "事件 SLA 达成率仅 {value:.1%}",
        "risk_sla_impact": "客户 SLO 承诺存在风险",
        "risk_mttr_high": "类别 '{category}' MTTR 为 {value:.1f}小时",
        "risk_mttr_impact": "解决时间过长，影响服务水平",
        "risk_change_fail": "{count} 个变更失败 ({rate:.1%})",
        "risk_change_fail_impact": "变更质量需要改进",
        "risk_change_incident": "{count} 个变更引发事件 ({rate:.1%})",
        "risk_change_incident_impact": "变更正在导致服务中断",
        "risk_problem_backlog": "{count} 个问题待解决",
        "risk_problem_backlog_impact": "未解决问题可能导致事件复发",

        # Actions
        "action_priority_urgent": "紧急",
        "action_priority_high": "高",
        "action_priority_medium": "中",

        # Action Messages
        "action_improve_sla": "审查并优化事件 SLA 达成流程",
        "action_improve_sla_impact": "预期：提升 SLA 达成率 10-15%",
        "action_reduce_mttr": "分析并优化事件解决流程",
        "action_reduce_mttr_impact": "预期：平均 MTTR 降低 20-30%",
        "action_improve_change": "加强变更评审和测试流程",
        "action_improve_change_impact": "预期：变更成功率提升至 95%+",
        "action_reduce_change_incident": "实施变更后验证和监控",
        "action_reduce_change_incident_impact": "预期：变更引发事件减少 50%",
        "action_improve_csat": "分析客户反馈，改进服务交付",
        "action_improve_csat_impact": "预期：满意度提升至 4.0+",
        "action_close_problems": "优先解决问题并完成 RCA",
        "action_close_problems_impact": "预期：减少重复事件 30%",

        # Table Headers - Incidents
        "col_incident_id": "事件编号",
        "col_incident_desc": "描述",
        "col_incident_priority": "优先级",
        "col_incident_status": "状态",
        "col_incident_resolution_time": "解决时长",

        # Table Headers - Changes
        "col_change_id": "变更编号",
        "col_change_title": "标题",
        "col_change_type": "类型",
        "col_change_status": "状态",
        "col_change_incident": "是否引发事件",

        # Table Headers - Problems
        "col_problem_id": "问题编号",
        "col_problem_title": "标题",
        "col_problem_status": "状态",
        "col_problem_known_error": "已知错误",
        "col_problem_incidents": "关联事件",

        # Data
        "hours": "小时",
        "hours_full": "小时",
        "tickets": "个工单",
        "days": "天",
        "yes": "是",
        "no": "否",

        # Warnings
        "data_insufficient": "数据不足，无法进行趋势对比",
        "no_comparison": "暂无对比数据",
        "no_risks": "未发现重大风险",
        "no_incidents": "本期无重大事件",
        "no_failed_changes": "本期无失败变更",
        "no_open_problems": "无待解决问题",

        # PPTX Slides
        "slide_cover": "运维质量报告",
        "slide_health": "服务健康评分",
        "slide_overview": "流程概览",
        "slide_kpi": "关键绩效指标",
        "slide_sla": "SLA 分级明细",
        "slide_risks": "风险雷达",
        "slide_trends": "趋势分析",
        "slide_incidents": "重大事件",
        "slide_changes": "失败变更",
        "slide_problems": "待解决问题",
        "slide_actions": "改进建议",

        # Report Meta
        "report_id": "报告编号",
        "analysis_period": "分析周期",
        "data_span": "数据跨度",
        "generated_on": "生成时间",
        "period": "分析周期",
        "to": "至",
        "na": "不适用",

        # Footer
        "footer_confidential": "机密 - 仅供内部使用",
        "footer_generated": "自动生成报告",
    }
}


def get_text(key: str, language: str = "en") -> str:
    """Get localized text by key."""
    if language not in TEXTS:
        language = "en"
    return TEXTS[language].get(key, TEXTS["en"].get(key, key))


def get_all_texts(language: str = "en") -> dict:
    """Get all texts for a language."""
    if language not in TEXTS:
        language = "en"
    return TEXTS[language]


def get_grade_text(grade: str, language: str = "en") -> str:
    """Get localized grade text."""
    grade_map = {
        "Excellent": "grade_excellent",
        "Good": "grade_good",
        "Needs Improvement": "grade_needs_improvement",
        "At Risk": "grade_at_risk",
    }
    key = grade_map.get(grade, "grade_at_risk")
    return get_text(key, language)


def get_priority_text(priority: str, language: str = "en") -> str:
    """Get localized priority text."""
    priority_map = {
        "URGENT": "action_priority_urgent",
        "HIGH": "action_priority_high",
        "MEDIUM": "action_priority_medium",
    }
    key = priority_map.get(priority.upper(), "action_priority_medium")
    return get_text(key, language)
