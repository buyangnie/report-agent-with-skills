"""
LLM-powered analysis for Major Incident Analysis Report.

Uses OpenAI-compatible API to generate insights and recommendations.
"""
import json
import os
from typing import Optional

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

import config


def get_llm_client() -> Optional["OpenAI"]:
    """Get OpenAI client configured from environment."""
    if not HAS_OPENAI:
        return None

    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("LLM_BASE_URL")

    if not api_key:
        return None

    return OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)


ANALYSIS_PROMPT_ZH = """你是一位资深的 IT 运维专家和事故分析师。请分析以下重大事故的处理过程，并提供专业的洞察和改进建议。

## 事故信息
- 工单号: {order_number}
- 标题: {title}
- 优先级: {priority}
- 类别: {category}
- 状态: {status}
- 创建时间: {created_at}
- 解决时间: {resolved_at}
- 持续时长: {duration}
- 受影响系统: {affected_systems}

## 关键指标
- 响应时间: {response_time} 分钟 (SLA: {sla_response} 分钟) - {sla_response_status}
- 解决时间: {resolution_time} 分钟 (SLA: {sla_resolution} 小时) - {sla_resolution_status}
- 升级次数: {escalation_count}
- 重分配次数: {reassignment_count}
- 参与人数: {participant_count}

## 时间线
{timeline}

## 检测到的问题
{issues}

请基于以上信息，提供以下分析（使用中文）：

1. **处理过程评估**: 简要评估整体处理过程的效率和专业性
2. **亮点**: 处理过程中做得好的地方（如果有）
3. **问题分析**: 对检测到的问题进行深入分析
4. **改进建议**: 针对性的改进建议，包括流程、技术、人员等方面
5. **预防措施**: 如何避免类似事故再次发生

请以 JSON 格式返回，结构如下：
{{
    "overall_assessment": "整体评估...",
    "highlights": ["亮点1", "亮点2"],
    "problem_analysis": "问题分析...",
    "improvement_suggestions": ["建议1", "建议2", "建议3"],
    "prevention_measures": ["预防措施1", "预防措施2"]
}}
"""

ANALYSIS_PROMPT_EN = """You are a senior IT operations expert and incident analyst. Please analyze the following major incident handling process and provide professional insights and recommendations.

## Incident Information
- Order Number: {order_number}
- Title: {title}
- Priority: {priority}
- Category: {category}
- Status: {status}
- Created At: {created_at}
- Resolved At: {resolved_at}
- Duration: {duration}
- Affected Systems: {affected_systems}

## Key Metrics
- Response Time: {response_time} minutes (SLA: {sla_response} minutes) - {sla_response_status}
- Resolution Time: {resolution_time} minutes (SLA: {sla_resolution} hours) - {sla_resolution_status}
- Escalations: {escalation_count}
- Reassignments: {reassignment_count}
- Participants: {participant_count}

## Timeline
{timeline}

## Detected Issues
{issues}

Based on the above information, please provide the following analysis (in English):

1. **Overall Assessment**: Brief evaluation of the handling process efficiency and professionalism
2. **Highlights**: What was done well during the handling (if any)
3. **Problem Analysis**: In-depth analysis of detected issues
4. **Improvement Suggestions**: Targeted improvement suggestions for process, technology, personnel, etc.
5. **Prevention Measures**: How to prevent similar incidents from happening again

Please return in JSON format with the following structure:
{{
    "overall_assessment": "Overall assessment...",
    "highlights": ["Highlight 1", "Highlight 2"],
    "problem_analysis": "Problem analysis...",
    "improvement_suggestions": ["Suggestion 1", "Suggestion 2", "Suggestion 3"],
    "prevention_measures": ["Prevention measure 1", "Prevention measure 2"]
}}
"""


def format_timeline_for_prompt(timeline: list, language: str = "en") -> str:
    """Format timeline events for the prompt."""
    lines = []
    for event in timeline:
        timestamp = event.timestamp.strftime("%H:%M")
        actor = event.actor
        event_type = event.event.value

        if event.detail:
            detail = event.detail
        elif event.from_value and event.to_value:
            detail = f"{event.from_value} → {event.to_value}"
        elif event.to_value:
            detail = f"→ {event.to_value}"
        else:
            detail = ""

        duration_note = ""
        if event.duration_from_previous and event.duration_from_previous > 0:
            duration_note = f" (+{event.duration_from_previous}min)"

        lines.append(f"- [{timestamp}]{duration_note} {event_type}: {actor} - {detail}")

    return "\n".join(lines)


def format_issues_for_prompt(issues: list, language: str = "en") -> str:
    """Format detected issues for the prompt."""
    if not issues:
        return "No issues detected" if language == "en" else "未检测到问题"

    lines = []
    for issue in issues:
        lines.append(f"- [{issue.severity.value.upper()}] {issue.title}: {issue.description}")

    return "\n".join(lines)


def generate_insights(analysis: "IncidentAnalysis", language: str = "en") -> dict:
    """Generate AI insights for the incident analysis.

    Args:
        analysis: The incident analysis result
        language: Output language ('en' or 'zh')

    Returns:
        Dictionary containing AI-generated insights
    """
    client = get_llm_client()

    if not client:
        return _generate_fallback_insights(analysis, language)

    # Prepare prompt data
    incident = analysis.incident

    # Get SLA info
    sla_response = incident.sla.response_minutes if incident.sla else 60
    sla_resolution = incident.sla.resolution_hours if incident.sla else 24

    # Format SLA status
    if analysis.incident.sla_response_met is None:
        sla_response_status = "N/A"
    elif analysis.incident.sla_response_met:
        sla_response_status = "Met" if language == "en" else "达标"
    else:
        sla_response_status = "Violated" if language == "en" else "违规"

    if analysis.incident.sla_resolution_met is None:
        sla_resolution_status = "N/A"
    elif analysis.incident.sla_resolution_met:
        sla_resolution_status = "Met" if language == "en" else "达标"
    else:
        sla_resolution_status = "Violated" if language == "en" else "违规"

    # Calculate duration
    if analysis.resolution_time_minutes:
        hours = analysis.resolution_time_minutes / 60
        duration = f"{hours:.1f} hours ({analysis.resolution_time_minutes} minutes)"
    else:
        duration = "Ongoing" if language == "en" else "进行中"

    # Choose prompt template
    prompt_template = ANALYSIS_PROMPT_ZH if language == "zh" else ANALYSIS_PROMPT_EN

    prompt = prompt_template.format(
        order_number=incident.order_number,
        title=incident.title,
        priority=incident.priority,
        category=incident.category,
        status=incident.status,
        created_at=incident.created_at.strftime("%Y-%m-%d %H:%M"),
        resolved_at=incident.resolved_at.strftime("%Y-%m-%d %H:%M") if incident.resolved_at else "N/A",
        duration=duration,
        affected_systems=", ".join(incident.affected_systems) if incident.affected_systems else "N/A",
        response_time=analysis.response_time_minutes or "N/A",
        sla_response=sla_response,
        sla_response_status=sla_response_status,
        resolution_time=analysis.resolution_time_minutes or "N/A",
        sla_resolution=sla_resolution,
        sla_resolution_status=sla_resolution_status,
        escalation_count=analysis.escalation_count,
        reassignment_count=analysis.reassignment_count,
        participant_count=len(analysis.unique_actors),
        timeline=format_timeline_for_prompt(analysis.timeline, language),
        issues=format_issues_for_prompt(analysis.issues, language),
    )

    try:
        response = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", config.OPENAI_MODEL),
            messages=[
                {"role": "system", "content": "You are a professional IT incident analyst. Always respond with valid JSON only, no additional text."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=config.OPENAI_MAX_TOKENS,
            temperature=config.OPENAI_TEMPERATURE,
        )

        content = response.choices[0].message.content.strip()

        # Try to parse JSON from response
        # Handle potential markdown code blocks
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1])

        insights = json.loads(content)
        return insights

    except Exception as e:
        print(f"Warning: LLM analysis failed: {e}")
        return _generate_fallback_insights(analysis, language)


def _generate_fallback_insights(analysis: "IncidentAnalysis", language: str = "en") -> dict:
    """Generate rule-based fallback insights when LLM is not available."""
    incident = analysis.incident

    if language == "zh":
        insights = {
            "overall_assessment": _generate_overall_assessment_zh(analysis),
            "highlights": _generate_highlights_zh(analysis),
            "problem_analysis": _generate_problem_analysis_zh(analysis),
            "improvement_suggestions": _generate_suggestions_zh(analysis),
            "prevention_measures": _generate_prevention_zh(analysis),
        }
    else:
        insights = {
            "overall_assessment": _generate_overall_assessment_en(analysis),
            "highlights": _generate_highlights_en(analysis),
            "problem_analysis": _generate_problem_analysis_en(analysis),
            "improvement_suggestions": _generate_suggestions_en(analysis),
            "prevention_measures": _generate_prevention_en(analysis),
        }

    return insights


def _generate_overall_assessment_zh(analysis: "IncidentAnalysis") -> str:
    """Generate overall assessment in Chinese."""
    parts = []

    # SLA compliance
    if analysis.incident.sla_response_met and analysis.incident.sla_resolution_met:
        parts.append("事故处理在 SLA 要求内完成，整体响应及时")
    elif analysis.incident.sla_response_met is False:
        parts.append("响应时间超出 SLA 要求，需要改进告警响应机制")
    elif analysis.incident.sla_resolution_met is False:
        parts.append("解决时间超出 SLA 要求，处理效率有待提升")

    # Escalations
    if analysis.escalation_count >= 3:
        parts.append("升级次数较多，可能存在初始诊断不准确或团队能力覆盖不足的问题")
    elif analysis.escalation_count == 0:
        parts.append("无需升级即完成处理，表明初始分配准确")

    # Reassignments
    if analysis.reassignment_count >= 3:
        parts.append("重分配次数过多，存在工单流转效率问题")

    return "。".join(parts) + "。" if parts else "事故处理过程基本正常。"


def _generate_overall_assessment_en(analysis: "IncidentAnalysis") -> str:
    """Generate overall assessment in English."""
    parts = []

    if analysis.incident.sla_response_met and analysis.incident.sla_resolution_met:
        parts.append("Incident was handled within SLA requirements with timely response")
    elif analysis.incident.sla_response_met is False:
        parts.append("Response time exceeded SLA, alert response mechanism needs improvement")
    elif analysis.incident.sla_resolution_met is False:
        parts.append("Resolution time exceeded SLA, handling efficiency needs improvement")

    if analysis.escalation_count >= 3:
        parts.append("High number of escalations suggests initial diagnosis issues or capability gaps")
    elif analysis.escalation_count == 0:
        parts.append("Completed without escalation, indicating accurate initial assignment")

    if analysis.reassignment_count >= 3:
        parts.append("Excessive reassignments indicate ticket routing efficiency issues")

    return ". ".join(parts) + "." if parts else "Incident handling process was generally normal."


def _generate_highlights_zh(analysis: "IncidentAnalysis") -> list:
    """Generate highlights in Chinese."""
    highlights = []

    if analysis.response_time_minutes and analysis.response_time_minutes <= 5:
        highlights.append("响应迅速，在 5 分钟内开始处理")

    if analysis.incident.sla_response_met:
        highlights.append("响应时间符合 SLA 要求")

    if analysis.incident.sla_resolution_met:
        highlights.append("解决时间符合 SLA 要求")

    if analysis.escalation_count <= 1:
        highlights.append("升级流程简洁，未出现过度升级")

    if len(analysis.unique_actors) >= 3:
        highlights.append("多团队协作处理，资源调配到位")

    return highlights if highlights else ["无特别亮点"]


def _generate_highlights_en(analysis: "IncidentAnalysis") -> list:
    """Generate highlights in English."""
    highlights = []

    if analysis.response_time_minutes and analysis.response_time_minutes <= 5:
        highlights.append("Quick response, handling started within 5 minutes")

    if analysis.incident.sla_response_met:
        highlights.append("Response time met SLA requirements")

    if analysis.incident.sla_resolution_met:
        highlights.append("Resolution time met SLA requirements")

    if analysis.escalation_count <= 1:
        highlights.append("Clean escalation process, no over-escalation")

    if len(analysis.unique_actors) >= 3:
        highlights.append("Multi-team collaboration with proper resource allocation")

    return highlights if highlights else ["No particular highlights"]


def _generate_problem_analysis_zh(analysis: "IncidentAnalysis") -> str:
    """Generate problem analysis in Chinese."""
    if not analysis.issues:
        return "本次事故处理过程未发现明显问题。"

    critical_issues = [i for i in analysis.issues if i.severity.value == "critical"]
    high_issues = [i for i in analysis.issues if i.severity.value == "high"]

    parts = []
    if critical_issues:
        parts.append(f"存在 {len(critical_issues)} 个严重问题需要立即关注")
    if high_issues:
        parts.append(f"发现 {len(high_issues)} 个高优先级问题")

    # Analyze patterns
    sla_issues = [i for i in analysis.issues if i.category == "sla"]
    response_issues = [i for i in analysis.issues if i.category == "response"]
    duration_issues = [i for i in analysis.issues if i.category == "duration"]

    if sla_issues:
        parts.append("SLA 违规是最需要关注的问题，直接影响服务承诺")
    if response_issues:
        parts.append("响应时间问题可能与告警机制或值班安排有关")
    if duration_issues:
        parts.append("处理过程中存在活动间隙，可能是等待审批或资源协调造成")

    return "。".join(parts) + "。" if parts else "未发现显著问题模式。"


def _generate_problem_analysis_en(analysis: "IncidentAnalysis") -> str:
    """Generate problem analysis in English."""
    if not analysis.issues:
        return "No significant issues found in incident handling process."

    critical_issues = [i for i in analysis.issues if i.severity.value == "critical"]
    high_issues = [i for i in analysis.issues if i.severity.value == "high"]

    parts = []
    if critical_issues:
        parts.append(f"{len(critical_issues)} critical issues require immediate attention")
    if high_issues:
        parts.append(f"{len(high_issues)} high-priority issues identified")

    sla_issues = [i for i in analysis.issues if i.category == "sla"]
    response_issues = [i for i in analysis.issues if i.category == "response"]
    duration_issues = [i for i in analysis.issues if i.category == "duration"]

    if sla_issues:
        parts.append("SLA violations are the most critical concern, directly impacting service commitments")
    if response_issues:
        parts.append("Response time issues may relate to alerting mechanisms or on-call arrangements")
    if duration_issues:
        parts.append("Activity gaps during handling may be due to waiting for approvals or resource coordination")

    return ". ".join(parts) + "." if parts else "No significant problem patterns identified."


def _generate_suggestions_zh(analysis: "IncidentAnalysis") -> list:
    """Generate improvement suggestions in Chinese."""
    suggestions = []

    if analysis.incident.sla_response_met is False:
        suggestions.append("优化告警通知机制，确保 P1 事故能在第一时间触达值班人员")
        suggestions.append("考虑引入电话告警或多渠道通知以加快响应速度")

    if analysis.incident.sla_resolution_met is False:
        suggestions.append("建立更完善的事故处理预案，减少临时决策时间")
        suggestions.append("定期进行事故演练，提升团队处理效率")

    if analysis.escalation_count >= 3:
        suggestions.append("完善 L1 支持团队的技能培训，减少不必要的升级")
        suggestions.append("建立更清晰的升级标准和流程")

    if analysis.reassignment_count >= 3:
        suggestions.append("优化工单路由规则，提高初次分配的准确性")
        suggestions.append("建立技能矩阵，便于快速找到合适的处理人员")

    # Check for activity gaps
    gap_issues = [i for i in analysis.issues if i.category == "duration"]
    if gap_issues:
        suggestions.append("减少处理过程中的等待时间，建立快速决策机制")

    return suggestions if suggestions else ["持续保持当前良好的事故处理实践"]


def _generate_suggestions_en(analysis: "IncidentAnalysis") -> list:
    """Generate improvement suggestions in English."""
    suggestions = []

    if analysis.incident.sla_response_met is False:
        suggestions.append("Optimize alerting mechanism to ensure P1 incidents reach on-call personnel immediately")
        suggestions.append("Consider phone alerts or multi-channel notifications to speed up response")

    if analysis.incident.sla_resolution_met is False:
        suggestions.append("Establish better incident handling runbooks to reduce ad-hoc decision time")
        suggestions.append("Conduct regular incident drills to improve team efficiency")

    if analysis.escalation_count >= 3:
        suggestions.append("Improve L1 support team skill training to reduce unnecessary escalations")
        suggestions.append("Establish clearer escalation criteria and procedures")

    if analysis.reassignment_count >= 3:
        suggestions.append("Optimize ticket routing rules to improve initial assignment accuracy")
        suggestions.append("Build a skill matrix for quick identification of appropriate handlers")

    gap_issues = [i for i in analysis.issues if i.category == "duration"]
    if gap_issues:
        suggestions.append("Reduce waiting time during handling by establishing quick decision mechanisms")

    return suggestions if suggestions else ["Continue maintaining current good incident handling practices"]


def _generate_prevention_zh(analysis: "IncidentAnalysis") -> list:
    """Generate prevention measures in Chinese."""
    measures = []

    category = analysis.incident.category.lower()

    if "database" in category or "db" in category:
        measures.append("定期检查数据库服务器健康状态，包括硬件、存储、网络")
        measures.append("确保数据库高可用架构正常工作，定期进行故障切换演练")
        measures.append("优化数据同步延迟，减少故障切换时的数据丢失风险")
    elif "network" in category:
        measures.append("加强网络监控，及时发现潜在的网络故障")
        measures.append("建立网络设备冗余，避免单点故障")
    elif "application" in category or "app" in category:
        measures.append("加强应用性能监控和容量规划")
        measures.append("实施蓝绿部署或金丝雀发布以降低变更风险")

    # General measures
    measures.append("建立定期的系统健康检查机制")
    measures.append("完善监控告警覆盖，确保问题能被及时发现")

    return measures


def _generate_prevention_en(analysis: "IncidentAnalysis") -> list:
    """Generate prevention measures in English."""
    measures = []

    category = analysis.incident.category.lower()

    if "database" in category or "db" in category:
        measures.append("Regularly check database server health including hardware, storage, and network")
        measures.append("Ensure database HA architecture works properly, conduct regular failover drills")
        measures.append("Optimize data sync delay to reduce data loss risk during failover")
    elif "network" in category:
        measures.append("Enhance network monitoring to detect potential network failures early")
        measures.append("Establish network device redundancy to avoid single points of failure")
    elif "application" in category or "app" in category:
        measures.append("Strengthen application performance monitoring and capacity planning")
        measures.append("Implement blue-green or canary deployments to reduce change risk")

    measures.append("Establish regular system health check mechanisms")
    measures.append("Improve monitoring and alerting coverage to ensure issues are detected promptly")

    return measures
