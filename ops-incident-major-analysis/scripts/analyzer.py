"""
Analyzer for Major Incident Analysis Report.

Performs time analysis, flow analysis, and issue detection.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from models import (
    ActionItem,
    ActionItemStatus,
    EventType,
    Incident,
    IncidentAnalysis,
    Issue,
    IssueSeverity,
    RootCauseAnalysis,
    TimelineEvent,
)
import config
from llm_analyzer import generate_insights


class IncidentAnalyzer:
    """Analyzes a single incident's timeline and workflow."""

    def __init__(self, incident: Incident, timeline: list[TimelineEvent]):
        self.incident = incident
        self.timeline = sorted(timeline, key=lambda e: e.timestamp)
        self.issues: list[Issue] = []

    @classmethod
    def from_json(cls, data: dict) -> "IncidentAnalyzer":
        """Create analyzer from JSON data."""
        incident = Incident.from_dict(data.get("incident", {}))
        timeline = [
            TimelineEvent.from_dict(e) for e in data.get("timeline", [])
        ]
        return cls(incident, timeline)

    @classmethod
    def from_file(cls, filepath: Path) -> "IncidentAnalyzer":
        """Load incident data from JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_json(data)

    def analyze(self, language: str = "en", use_llm: bool = True) -> IncidentAnalysis:
        """Run full analysis and return results.

        Args:
            language: Output language ('en' or 'zh')
            use_llm: Whether to use LLM for generating insights
        """
        # Compute event durations
        self._compute_event_durations()

        # Run all analysis steps
        time_metrics = self._analyze_time()
        flow_metrics = self._analyze_flow()

        # Detect issues
        self._detect_issues(time_metrics, flow_metrics)

        # Build analysis result
        analysis = IncidentAnalysis(
            incident=self.incident,
            timeline=self.timeline,
            response_time_minutes=time_metrics.get("response_time"),
            resolution_time_minutes=time_metrics.get("resolution_time"),
            phase_durations=time_metrics.get("phase_durations", {}),
            escalation_count=flow_metrics.get("escalation_count", 0),
            reassignment_count=flow_metrics.get("reassignment_count", 0),
            unique_actors=flow_metrics.get("unique_actors", []),
            handover_events=flow_metrics.get("handover_events", []),
            issues=self.issues,
        )

        # Update incident computed fields
        self.incident.total_duration_minutes = time_metrics.get("resolution_time")
        self.incident.sla_response_met = time_metrics.get("sla_response_met")
        self.incident.sla_resolution_met = time_metrics.get("sla_resolution_met")

        # Set root cause analysis from incident data if available
        if self.incident.root_cause:
            analysis.root_cause_analysis = self.incident.root_cause

        # Generate AI insights
        if use_llm:
            analysis.insights = generate_insights(analysis, language)

            # Generate root cause analysis if not provided
            if not analysis.root_cause_analysis:
                analysis.root_cause_analysis = self._generate_root_cause_analysis(analysis, language)

            # Generate action items from issues and insights
            analysis.action_items = self._generate_action_items(analysis, language)

        return analysis

    def _generate_root_cause_analysis(self, analysis: IncidentAnalysis, language: str) -> RootCauseAnalysis:
        """Generate root cause analysis from insights and issues."""
        insights = analysis.insights

        # Default 5-Whys based on common patterns
        five_whys = []
        control_failures = []
        contributing_factors = []

        # Analyze issues to build 5-whys
        sla_violated = any(i.category == "sla" for i in analysis.issues)
        has_gaps = any(i.category == "duration" for i in analysis.issues)
        many_escalations = analysis.escalation_count >= 2

        if language == "zh":
            if sla_violated:
                five_whys = [
                    "为什么 SLA 被违反？—— 解决时间超出预期",
                    "为什么解决时间超出预期？—— 问题诊断和决策过程耗时过长",
                    "为什么诊断和决策耗时过长？—— 缺乏预案和自动化工具",
                    "为什么缺乏预案？—— 没有针对此类场景进行充分的演练",
                    "为什么没有充分演练？—— 演练计划不完善或执行不到位",
                ]
                control_failures = [
                    "监控预警未能提前发现问题征兆",
                    "故障切换流程不够自动化",
                    "数据同步延迟监控不到位",
                ]
            if has_gaps:
                contributing_factors.append("处理过程中存在较长等待时间")
            if many_escalations:
                contributing_factors.append("多次升级表明初始处理能力不足")
        else:
            if sla_violated:
                five_whys = [
                    "Why was SLA violated? — Resolution time exceeded expectations",
                    "Why did resolution time exceed expectations? — Diagnosis and decision-making took too long",
                    "Why did diagnosis/decision take too long? — Lack of runbooks and automation tools",
                    "Why lack of runbooks? — Insufficient drills for this scenario",
                    "Why insufficient drills? — Drill plan incomplete or not executed properly",
                ]
                control_failures = [
                    "Monitoring failed to detect early warning signs",
                    "Failover process not sufficiently automated",
                    "Data sync delay monitoring inadequate",
                ]
            if has_gaps:
                contributing_factors.append("Long waiting periods during handling process")
            if many_escalations:
                contributing_factors.append("Multiple escalations indicate insufficient initial handling capability")

        return RootCauseAnalysis(
            category=analysis.incident.category,
            description=insights.get("problem_analysis", ""),
            five_whys=five_whys,
            control_point_failures=control_failures,
            contributing_factors=contributing_factors,
        )

    def _generate_action_items(self, analysis: IncidentAnalysis, language: str) -> list[ActionItem]:
        """Generate action items from issues and insights."""
        action_items = []
        insights = analysis.insights

        # Generate action items from improvement suggestions
        suggestions = insights.get("improvement_suggestions", [])
        prevention = insights.get("prevention_measures", [])

        item_id = 1
        for suggestion in suggestions[:3]:  # Top 3 suggestions
            action_items.append(ActionItem(
                id=f"AI-{item_id:03d}",
                title=suggestion[:50] + "..." if len(suggestion) > 50 else suggestion,
                description=suggestion,
                owner="TBD",
                status=ActionItemStatus.OPEN,
                priority="high",
                category="process",
            ))
            item_id += 1

        for measure in prevention[:2]:  # Top 2 prevention measures
            action_items.append(ActionItem(
                id=f"AI-{item_id:03d}",
                title=measure[:50] + "..." if len(measure) > 50 else measure,
                description=measure,
                owner="TBD",
                status=ActionItemStatus.OPEN,
                priority="medium",
                category="technology",
            ))
            item_id += 1

        return action_items

    def _compute_event_durations(self) -> None:
        """Compute duration from previous event for each timeline event."""
        for i, event in enumerate(self.timeline):
            if i == 0:
                event.duration_from_previous = 0
            else:
                prev_event = self.timeline[i - 1]
                delta = event.timestamp - prev_event.timestamp
                event.duration_from_previous = int(delta.total_seconds() / 60)

    def _analyze_time(self) -> dict:
        """Analyze time-related metrics."""
        metrics = {
            "response_time": None,
            "resolution_time": None,
            "sla_response_met": None,
            "sla_resolution_met": None,
            "phase_durations": {},
        }

        if not self.timeline:
            return metrics

        # Response time: created -> first assigned/status_change
        created_time = self.incident.created_at
        first_response = None
        for event in self.timeline:
            if event.event in (EventType.ASSIGNED, EventType.STATUS_CHANGE):
                first_response = event.timestamp
                break

        if first_response:
            delta = first_response - created_time
            metrics["response_time"] = int(delta.total_seconds() / 60)

        # Resolution time: created -> resolved/closed
        if self.incident.resolved_at:
            delta = self.incident.resolved_at - created_time
            metrics["resolution_time"] = int(delta.total_seconds() / 60)
        elif not self.incident.is_ongoing:
            # Find resolved/closed event
            for event in reversed(self.timeline):
                if event.event in (EventType.RESOLVED, EventType.CLOSED):
                    delta = event.timestamp - created_time
                    metrics["resolution_time"] = int(delta.total_seconds() / 60)
                    break

        # SLA compliance
        if self.incident.sla:
            sla = self.incident.sla
            if metrics["response_time"] is not None:
                metrics["sla_response_met"] = (
                    metrics["response_time"] <= sla.response_minutes
                )
            if metrics["resolution_time"] is not None:
                metrics["sla_resolution_met"] = (
                    metrics["resolution_time"] <= sla.resolution_hours * 60
                )

        # Phase durations (based on status changes)
        metrics["phase_durations"] = self._compute_phase_durations()

        return metrics

    def _compute_phase_durations(self) -> dict[str, int]:
        """Compute duration of each phase based on status changes."""
        phases = {}
        current_status = None
        status_start = None

        for event in self.timeline:
            if event.event == EventType.CREATED:
                current_status = "Open"
                status_start = event.timestamp
            elif event.event == EventType.STATUS_CHANGE:
                if current_status and status_start:
                    delta = event.timestamp - status_start
                    duration = int(delta.total_seconds() / 60)
                    phases[current_status] = phases.get(current_status, 0) + duration
                current_status = event.to_value
                status_start = event.timestamp
            elif event.event in (EventType.RESOLVED, EventType.CLOSED):
                if current_status and status_start:
                    delta = event.timestamp - status_start
                    duration = int(delta.total_seconds() / 60)
                    phases[current_status] = phases.get(current_status, 0) + duration
                current_status = event.event.value
                status_start = event.timestamp

        return phases

    def _analyze_flow(self) -> dict:
        """Analyze workflow-related metrics."""
        metrics = {
            "escalation_count": 0,
            "reassignment_count": 0,
            "unique_actors": [],
            "handover_events": [],
        }

        actors = set()
        for event in self.timeline:
            actors.add(event.actor)
            if event.to_value:
                actors.add(event.to_value)

            if event.event == EventType.ESCALATED:
                metrics["escalation_count"] += 1
                metrics["handover_events"].append(event)
            elif event.event == EventType.REASSIGNED:
                metrics["reassignment_count"] += 1
                metrics["handover_events"].append(event)
            elif event.event == EventType.ASSIGNED and event.from_value:
                # Assignment with previous owner is a handover
                metrics["handover_events"].append(event)

        # Deduplicate and normalize actors
        metrics["unique_actors"] = self._normalize_actors(actors)
        return metrics

    def _normalize_actors(self, actors: set) -> list[str]:
        """Normalize and deduplicate actor names.

        - Excludes non-person values (status values, system keywords)
        - Normalizes names with annotations (e.g., '张伟 (高级 DBA)' -> '张伟')
        - Deduplicates based on base name
        """
        # Values to exclude (status values and non-person entities)
        exclude_patterns = {
            "In Progress", "Open", "Resolved", "Closed", "Pending",
            "进行中", "已解决", "已关闭", "待处理",
        }

        # System/automated actors to keep as-is
        system_actors = {
            "监控系统", "Monitoring System",
            "自动派单系统", "Auto Dispatcher", "Auto-Dispatcher",
        }

        normalized_map = {}  # base_name -> full_name (keep the most detailed version)

        for actor in actors:
            if not actor or actor in exclude_patterns:
                continue

            # Keep system actors as-is
            if actor in system_actors:
                normalized_map[actor] = actor
                continue

            # Extract base name (remove annotations in parentheses)
            base_name = actor
            if "(" in actor:
                base_name = actor.split("(")[0].strip()
            elif "（" in actor:
                base_name = actor.split("（")[0].strip()

            # Keep the most detailed version of the name
            if base_name not in normalized_map:
                normalized_map[base_name] = actor
            elif len(actor) > len(normalized_map[base_name]):
                # Keep the longer (more detailed) version
                normalized_map[base_name] = actor

        return sorted(normalized_map.values())

    def _detect_issues(self, time_metrics: dict, flow_metrics: dict) -> None:
        """Detect issues based on thresholds and patterns."""
        self.issues = []

        # Check SLA violations
        self._check_sla_issues(time_metrics)

        # Check response time
        self._check_response_time_issues(time_metrics)

        # Check event gaps
        self._check_event_gap_issues()

        # Check escalation patterns
        self._check_escalation_issues(flow_metrics)

        # Check reassignment patterns
        self._check_reassignment_issues(flow_metrics)

        # Check handover wait times
        self._check_handover_issues(flow_metrics)

        # Sort by severity
        severity_order = {
            IssueSeverity.CRITICAL: 0,
            IssueSeverity.HIGH: 1,
            IssueSeverity.MEDIUM: 2,
            IssueSeverity.LOW: 3,
        }
        self.issues.sort(key=lambda x: severity_order[x.severity])

    def _check_sla_issues(self, time_metrics: dict) -> None:
        """Check for SLA violations."""
        if time_metrics.get("sla_response_met") is False:
            sla = self.incident.sla
            self.issues.append(Issue(
                severity=IssueSeverity.CRITICAL,
                category="sla",
                title="SLA Response Time Violated",
                description=f"Response time ({time_metrics['response_time']} min) "
                           f"exceeded SLA target ({sla.response_minutes} min)",
                metric_value=time_metrics["response_time"],
                threshold_value=sla.response_minutes,
            ))

        if time_metrics.get("sla_resolution_met") is False:
            sla = self.incident.sla
            resolution_hours = time_metrics["resolution_time"] / 60
            self.issues.append(Issue(
                severity=IssueSeverity.CRITICAL,
                category="sla",
                title="SLA Resolution Time Violated",
                description=f"Resolution time ({resolution_hours:.1f} hours) "
                           f"exceeded SLA target ({sla.resolution_hours} hours)",
                metric_value=resolution_hours,
                threshold_value=sla.resolution_hours,
            ))

    def _check_response_time_issues(self, time_metrics: dict) -> None:
        """Check for slow response time."""
        response_time = time_metrics.get("response_time")
        if response_time is None:
            return

        # Get SLA or default
        if self.incident.sla:
            sla_response = self.incident.sla.response_minutes
        else:
            default_sla = config.DEFAULT_SLA.get(self.incident.priority, {})
            sla_response = default_sla.get("response_minutes", 60)

        warning_threshold = sla_response * config.RESPONSE_TIME_WARNING_MULTIPLIER
        critical_threshold = sla_response * config.RESPONSE_TIME_CRITICAL_MULTIPLIER

        if response_time >= critical_threshold:
            self.issues.append(Issue(
                severity=IssueSeverity.HIGH,
                category="response",
                title="Critically Slow Response",
                description=f"Response took {response_time} minutes, "
                           f"more than {config.RESPONSE_TIME_CRITICAL_MULTIPLIER}x SLA",
                metric_value=response_time,
                threshold_value=sla_response,
            ))
        elif response_time >= warning_threshold:
            self.issues.append(Issue(
                severity=IssueSeverity.MEDIUM,
                category="response",
                title="Slow Response",
                description=f"Response took {response_time} minutes, "
                           f"at or above SLA threshold",
                metric_value=response_time,
                threshold_value=sla_response,
            ))

    def _check_event_gap_issues(self) -> None:
        """Check for long gaps between events."""
        for i, event in enumerate(self.timeline):
            if i == 0:
                continue

            gap = event.duration_from_previous
            if gap is None:
                continue

            if gap >= config.EVENT_GAP_CRITICAL:
                prev_event = self.timeline[i - 1]
                self.issues.append(Issue(
                    severity=IssueSeverity.HIGH,
                    category="duration",
                    title="Critical Activity Gap",
                    description=f"No activity for {gap} minutes between events",
                    timestamp=prev_event.timestamp,
                    actor=prev_event.actor,
                    metric_value=gap,
                    threshold_value=config.EVENT_GAP_CRITICAL,
                ))
            elif gap >= config.EVENT_GAP_WARNING:
                prev_event = self.timeline[i - 1]
                self.issues.append(Issue(
                    severity=IssueSeverity.MEDIUM,
                    category="duration",
                    title="Long Activity Gap",
                    description=f"No activity for {gap} minutes between events",
                    timestamp=prev_event.timestamp,
                    actor=prev_event.actor,
                    metric_value=gap,
                    threshold_value=config.EVENT_GAP_WARNING,
                ))

    def _check_escalation_issues(self, flow_metrics: dict) -> None:
        """Check for excessive escalations."""
        count = flow_metrics.get("escalation_count", 0)

        if count >= config.ESCALATION_COUNT_CRITICAL:
            self.issues.append(Issue(
                severity=IssueSeverity.HIGH,
                category="escalation",
                title="Excessive Escalations",
                description=f"Incident was escalated {count} times, "
                           f"indicating complexity or capability gaps",
                metric_value=count,
                threshold_value=config.ESCALATION_COUNT_CRITICAL,
            ))
        elif count >= config.ESCALATION_COUNT_WARNING:
            self.issues.append(Issue(
                severity=IssueSeverity.MEDIUM,
                category="escalation",
                title="Multiple Escalations",
                description=f"Incident was escalated {count} times",
                metric_value=count,
                threshold_value=config.ESCALATION_COUNT_WARNING,
            ))

    def _check_reassignment_issues(self, flow_metrics: dict) -> None:
        """Check for excessive reassignments (ping-pong)."""
        count = flow_metrics.get("reassignment_count", 0)

        if count >= config.REASSIGNMENT_COUNT_CRITICAL:
            self.issues.append(Issue(
                severity=IssueSeverity.HIGH,
                category="reassignment",
                title="Excessive Reassignments (Ping-Pong)",
                description=f"Incident was reassigned {count} times, "
                           f"indicating routing or ownership issues",
                metric_value=count,
                threshold_value=config.REASSIGNMENT_COUNT_CRITICAL,
            ))
        elif count >= config.REASSIGNMENT_COUNT_WARNING:
            self.issues.append(Issue(
                severity=IssueSeverity.MEDIUM,
                category="reassignment",
                title="Multiple Reassignments",
                description=f"Incident was reassigned {count} times",
                metric_value=count,
                threshold_value=config.REASSIGNMENT_COUNT_WARNING,
            ))

    def _check_handover_issues(self, flow_metrics: dict) -> None:
        """Check for long handover wait times."""
        for event in flow_metrics.get("handover_events", []):
            # Find next event after handover
            idx = self.timeline.index(event)
            if idx + 1 < len(self.timeline):
                next_event = self.timeline[idx + 1]
                wait_time = next_event.duration_from_previous

                if wait_time and wait_time >= config.HANDOVER_WAIT_CRITICAL:
                    self.issues.append(Issue(
                        severity=IssueSeverity.HIGH,
                        category="handover",
                        title="Critical Handover Delay",
                        description=f"Waited {wait_time} minutes after handover "
                                   f"to {event.to_value}",
                        timestamp=event.timestamp,
                        actor=event.to_value,
                        metric_value=wait_time,
                        threshold_value=config.HANDOVER_WAIT_CRITICAL,
                    ))
                elif wait_time and wait_time >= config.HANDOVER_WAIT_WARNING:
                    self.issues.append(Issue(
                        severity=IssueSeverity.MEDIUM,
                        category="handover",
                        title="Slow Handover",
                        description=f"Waited {wait_time} minutes after handover "
                                   f"to {event.to_value}",
                        timestamp=event.timestamp,
                        actor=event.to_value,
                        metric_value=wait_time,
                        threshold_value=config.HANDOVER_WAIT_WARNING,
                    ))


def load_incident_data(filepath: Optional[Path] = None) -> dict:
    """Load incident data from file or return sample data for testing."""
    if filepath and filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    # Return empty structure if no file
    return {"incident": {}, "timeline": []}
