"""
Internationalization (i18n) module for BO Workload Performance Report.

Provides bilingual text resources (English and Chinese).
"""

# =============================================================================
# Language Resources
# =============================================================================

TEXTS = {
    "en": {
        # Report Title
        "report_title": "BO Workload Performance Report",
        "report_subtitle": "Second/Third-Line Expert Analysis",
        
        # Section Titles
        "section_executive_summary": "Executive Summary",
        "section_tier_classification": "BO Tier Classification",
        "section_expert_profiles": "Expert Profiles",
        "section_dependency_matrix": "Single-Point Dependency Risk Matrix",
        "section_bottleneck_analysis": "Bottleneck Analysis",
        "section_workload_balance": "Workload Balance Analysis",
        "section_knowledge_silo": "Knowledge Silo Detection",
        "section_ai_insights": "AI Insights & Recommendations",
        "section_trend_analysis": "Trend Analysis",
        
        # Executive Summary
        "exec_total_bo_experts": "Total BO Experts",
        "exec_total_bo_tickets": "Total BO Tickets",
        "exec_avg_mttr": "Average MTTR",
        "exec_sla_rate": "SLA Compliance Rate",
        "exec_high_risk_count": "High Risk Items",
        "exec_bottleneck_count": "Bottleneck Experts",
        "exec_hours": "hours",
        
        # Tier Classification
        "tier_1": "Tier 1 (Front-line)",
        "tier_2": "Tier 2 (Specialist)",
        "tier_3": "Tier 3 (Expert)",
        "tier_classification_desc": "Auto-classification based on complexity index, priority handling, and specialization.",
        "tier_resolver": "Resolver",
        "tier_assigned": "Assigned Tier",
        "tier_complexity_index": "Complexity Index",
        "tier_priority_index": "Priority Index",
        "tier_specialization": "Specialization",
        "tier_justification": "Justification",
        
        # Expert Profile
        "profile_specialty": "Specialty Areas",
        "profile_efficiency": "Efficiency Metrics",
        "profile_workload": "Workload Distribution",
        "profile_total_tickets": "Total Tickets",
        "profile_avg_mttr": "Average MTTR",
        "profile_sla_rate": "SLA Rate",
        "profile_long_tail_rate": "Long-Tail Rate",
        "profile_top_categories": "Top Categories",
        
        # Dependency Matrix
        "dependency_high_risk": "High Risk (1-2 resolvers)",
        "dependency_medium_risk": "Medium Risk (3-4 resolvers)",
        "dependency_low_risk": "Low Risk (5+ resolvers)",
        "dependency_category": "Category",
        "dependency_resolver_count": "Resolver Count",
        "dependency_risk_level": "Risk Level",
        "dependency_resolvers": "Resolvers",
        
        # Bottleneck Analysis
        "bottleneck_score": "Bottleneck Score",
        "bottleneck_rank": "Rank",
        "bottleneck_backlog": "Current Backlog",
        "bottleneck_mttr": "Avg MTTR",
        "bottleneck_replaceability": "Replaceability",
        "bottleneck_sla_trend": "SLA Trend",
        "bottleneck_root_cause": "Root Cause",
        "bottleneck_overloaded": "Overloaded",
        "bottleneck_slow": "Slow Processing",
        "bottleneck_irreplaceable": "Irreplaceable",
        "bottleneck_declining_sla": "Declining SLA",
        
        # Workload Balance
        "balance_gini": "Gini Coefficient",
        "balance_interpretation": "Interpretation",
        "balance_well_balanced": "Well Balanced",
        "balance_moderate_imbalance": "Moderate Imbalance",
        "balance_severe_imbalance": "Severe Imbalance",
        "balance_overloaded": "Overloaded Experts",
        "balance_underloaded": "Underloaded Experts",
        "balance_avg_workload": "Average Workload",
        
        # Knowledge Silo
        "silo_category": "Category",
        "silo_sole_expert": "Sole Expert(s)",
        "silo_ticket_count": "Ticket Count",
        "silo_priority": "Documentation Priority",
        "silo_high": "High",
        "silo_medium": "Medium",
        "silo_low": "Low",
        
        # AI Insights
        "insight_summary": "Summary",
        "insight_risks": "Key Risks",
        "insight_recommendations": "Recommendations",
        "insight_short_term": "Short-term Actions",
        "insight_medium_term": "Medium-term Actions",
        "insight_long_term": "Long-term Actions",
        
        # Charts
        "chart_tier_distribution": "BO Tier Distribution",
        "chart_dependency_heatmap": "Resolver × Category Dependency Matrix",
        "chart_bottleneck_ranking": "Bottleneck Score Ranking",
        "chart_workload_distribution": "Workload Distribution",
        "chart_mttr_comparison": "MTTR Comparison by Tier",
        "chart_category_coverage": "Category Coverage Analysis",
        
        # Misc
        "generated_on": "Generated on",
        "period": "Analysis Period",
        "to": "to",
        "no_data": "No data available",
        "na": "N/A",

        # Trend Analysis
        "trend": "Trend",
        "trend_improving": "Improving",
        "trend_deteriorating": "Deteriorating",
        "trend_stable": "Stable",
        "trend_increasing": "Increasing",
        "trend_decreasing": "Decreasing",
        "volume": "Volume",
        "period_type": "Period Type",
        "periods": "periods",
        "nav_contents": "Contents",
        "disclaimer": "This report is auto-generated for internal use. Data accuracy depends on source system inputs.",
        "chart_hourly_pattern": "Expert Hourly Activity Pattern",
        "chart_sla_comparison": "SLA Compliance Comparison",
        
        # Priority dimension
        "weighted_workload": "Weighted Workload",
        "priority_distribution": "Priority Distribution",
        "p1_p2_ratio": "P1/P2 Ratio",
        "high_priority_specialist": "High Priority Specialist",
        "chart_priority_heatmap": "Priority Distribution Heatmap",
        "weighted_gini": "Weighted Gini",
        "raw_workload": "Raw Ticket Count",
        "weighted_balance": "Priority-Weighted Balance"
    },
    
    "zh": {
        # Report Title
        "report_title": "BO 负载绩效报告",
        "report_subtitle": "后台专家深度分析",
        
        # Section Titles
        "section_executive_summary": "执行摘要",
        "section_tier_classification": "人员层级分类",
        "section_expert_profiles": "专家画像",
        "section_dependency_matrix": "单点依赖风险矩阵",
        "section_bottleneck_analysis": "瓶颈分析",
        "section_workload_balance": "负载均衡分析",
        "section_knowledge_silo": "知识孤岛检测",
        "section_ai_insights": "AI 洞察与建议",
        "section_trend_analysis": "趋势分析",
        
        # Executive Summary
        "exec_total_bo_experts": "BO 专家总数",
        "exec_total_bo_tickets": "BO 工单总数",
        "exec_avg_mttr": "平均解决时长",
        "exec_sla_rate": "SLA 达成率",
        "exec_high_risk_count": "高风险项",
        "exec_bottleneck_count": "瓶颈专家数",
        "exec_hours": "小时",
        
        # Tier Classification
        "tier_1": "一线（前台）",
        "tier_2": "二线（专员）",
        "tier_3": "三线（专家）",
        "tier_classification_desc": "基于复杂度指数、优先级处理比例和专业化程度自动分类。",
        "tier_resolver": "处理人",
        "tier_assigned": "分配层级",
        "tier_complexity_index": "复杂度指数",
        "tier_priority_index": "优先级指数",
        "tier_specialization": "专业化程度",
        "tier_justification": "分类依据",
        
        # Expert Profile
        "profile_specialty": "专长领域",
        "profile_efficiency": "效率指标",
        "profile_workload": "工作量分布",
        "profile_total_tickets": "总工单数",
        "profile_avg_mttr": "平均 MTTR",
        "profile_sla_rate": "SLA 达成率",
        "profile_long_tail_rate": "长尾工单占比",
        "profile_top_categories": "主要处理类别",
        
        # Dependency Matrix
        "dependency_high_risk": "高风险（仅 1-2 人）",
        "dependency_medium_risk": "中风险（3-4 人）",
        "dependency_low_risk": "低风险（5+ 人）",
        "dependency_category": "类别",
        "dependency_resolver_count": "处理人数",
        "dependency_risk_level": "风险等级",
        "dependency_resolvers": "处理人员",
        
        # Bottleneck Analysis
        "bottleneck_score": "瓶颈评分",
        "bottleneck_rank": "排名",
        "bottleneck_backlog": "当前积压",
        "bottleneck_mttr": "平均 MTTR",
        "bottleneck_replaceability": "可替代性",
        "bottleneck_sla_trend": "SLA 趋势",
        "bottleneck_root_cause": "根因",
        "bottleneck_overloaded": "工作量过大",
        "bottleneck_slow": "处理速度慢",
        "bottleneck_irreplaceable": "不可替代",
        "bottleneck_declining_sla": "SLA 恶化",
        
        # Workload Balance
        "balance_gini": "基尼系数",
        "balance_interpretation": "解读",
        "balance_well_balanced": "分配均衡",
        "balance_moderate_imbalance": "中度不均",
        "balance_severe_imbalance": "严重不均",
        "balance_overloaded": "超负荷人员",
        "balance_underloaded": "低负荷人员",
        "balance_avg_workload": "平均工作量",
        
        # Knowledge Silo
        "silo_category": "类别",
        "silo_sole_expert": "唯一专家",
        "silo_ticket_count": "工单数",
        "silo_priority": "文档化优先级",
        "silo_high": "高",
        "silo_medium": "中",
        "silo_low": "低",
        
        # AI Insights
        "insight_summary": "总结",
        "insight_risks": "关键风险",
        "insight_recommendations": "改进建议",
        "insight_short_term": "短期行动",
        "insight_medium_term": "中期行动",
        "insight_long_term": "长期行动",
        
        # Charts
        "chart_tier_distribution": "人员层级分布",
        "chart_dependency_heatmap": "处理人 × 类别 依赖矩阵",
        "chart_bottleneck_ranking": "瓶颈评分排名",
        "chart_workload_distribution": "工作量分布",
        "chart_mttr_comparison": "各层级 MTTR 对比",
        "chart_category_coverage": "类别覆盖分析",
        
        # Misc
        "generated_on": "生成时间",
        "period": "分析周期",
        "to": "至",
        "no_data": "暂无数据",
        "na": "不适用",

        # Trend Analysis
        "trend": "趋势",
        "trend_improving": "改善中",
        "trend_deteriorating": "恶化中",
        "trend_stable": "稳定",
        "trend_increasing": "增长中",
        "trend_decreasing": "下降中",
        "volume": "工单量",
        "period_type": "周期类型",
        "periods": "个周期",
        "nav_contents": "目录",
        "disclaimer": "本报告为自动生成，仅供内部参考。数据准确性取决于源系统输入。",
        "chart_hourly_pattern": "专家小时活跃度分布",
        "chart_sla_comparison": "SLA 达成率对比",
        
        # Priority dimension
        "weighted_workload": "加权工作量",
        "priority_distribution": "优先级分布",
        "p1_p2_ratio": "P1/P2 占比",
        "high_priority_specialist": "高优先级专家",
        "chart_priority_heatmap": "优先级分布热力图",
        "weighted_gini": "加权基尼系数",
        "raw_workload": "原始工单数",
        "weighted_balance": "优先级加权均衡度"
    }
}


def get_text(key: str, language: str = "en") -> str:
    """
    Get localized text by key.
    
    Args:
        key: Text key
        language: Language code ("en" or "zh")
    
    Returns:
        Localized text string
    """
    if language not in TEXTS:
        language = "en"
    
    return TEXTS[language].get(key, TEXTS["en"].get(key, key))


def get_all_texts(language: str = "en") -> dict:
    """
    Get all texts for a language.
    
    Args:
        language: Language code ("en" or "zh")
    
    Returns:
        Dictionary of all texts
    """
    if language not in TEXTS:
        language = "en"
    
    return TEXTS[language]
