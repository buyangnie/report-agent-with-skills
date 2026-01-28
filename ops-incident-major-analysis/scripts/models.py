"""
Data models for Major Incident Analysis.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class EventType(str, Enum):
    """Timeline event types."""
    CREATED = "created"
    ASSIGNED = "assigned"
    REASSIGNED = "reassigned"
    ESCALATED = "escalated"
    STATUS_CHANGE = "status_change"
    PRIORITY_CHANGE = "priority_change"
    NOTE = "note"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"

    @classmethod
    def from_string(cls, value: str) -> "EventType":
        """Convert string to EventType, default to NOTE if unknown."""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.NOTE


class IssueSeverity(str, Enum):
    """Issue severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ActionItemStatus(str, Enum):
    """Action item status levels."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


@dataclass
class SLA:
    """SLA definition."""
    response_minutes: int
    resolution_hours: float

    @classmethod
    def from_dict(cls, data: dict) -> "SLA":
        return cls(
            response_minutes=data.get("response_minutes", 60),
            resolution_hours=data.get("resolution_hours", 24),
        )


@dataclass
class RootCauseAnalysis:
    """Root cause analysis with 5-Why structure."""
    category: str
    description: str
    description_en: Optional[str] = None
    five_whys: list[str] = field(default_factory=list)  # List of "why" answers
    control_point_failures: list[str] = field(default_factory=list)  # What should have prevented this
    contributing_factors: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "RootCauseAnalysis":
        return cls(
            category=data.get("category", "Unknown"),
            description=data.get("description", ""),
            description_en=data.get("description_en"),
            five_whys=data.get("five_whys", []),
            control_point_failures=data.get("control_point_failures", []),
            contributing_factors=data.get("contributing_factors", []),
        )

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "description": self.description,
            "description_en": self.description_en,
            "five_whys": self.five_whys,
            "control_point_failures": self.control_point_failures,
            "contributing_factors": self.contributing_factors,
        }


@dataclass
class ActionItem:
    """An action item for improvement tracking."""
    id: str
    title: str
    description: str
    owner: str
    due_date: Optional[datetime] = None
    status: ActionItemStatus = ActionItemStatus.OPEN
    priority: str = "medium"  # high, medium, low
    category: str = "process"  # process, technology, people, policy

    @classmethod
    def from_dict(cls, data: dict) -> "ActionItem":
        due_date = data.get("due_date")
        if due_date and isinstance(due_date, str):
            due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))

        status_str = data.get("status", "open")
        try:
            status = ActionItemStatus(status_str)
        except ValueError:
            status = ActionItemStatus.OPEN

        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            owner=data.get("owner", "Unassigned"),
            due_date=due_date,
            status=status,
            priority=data.get("priority", "medium"),
            category=data.get("category", "process"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "owner": self.owner,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "status": self.status.value,
            "priority": self.priority,
            "category": self.category,
        }


@dataclass
class TimelineEvent:
    """A single event in the incident timeline."""
    timestamp: datetime
    event: EventType
    actor: str
    from_value: Optional[str] = None
    to_value: Optional[str] = None
    detail: Optional[str] = None

    # i18n fields
    actor_en: Optional[str] = None
    from_value_en: Optional[str] = None
    to_value_en: Optional[str] = None
    detail_en: Optional[str] = None

    # Computed fields (set by analyzer)
    duration_from_previous: Optional[int] = None  # minutes

    @classmethod
    def from_dict(cls, data: dict) -> "TimelineEvent":
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

        return cls(
            timestamp=timestamp,
            event=EventType.from_string(data.get("event", "note")),
            actor=data.get("actor", "Unknown"),
            from_value=data.get("from"),
            to_value=data.get("to"),
            detail=data.get("detail"),
            actor_en=data.get("actor_en"),
            from_value_en=data.get("from_en"),
            to_value_en=data.get("to_en"),
            detail_en=data.get("detail_en"),
        )

    def get_actor(self, language: str = "zh") -> str:
        """Get actor name based on language."""
        if language == "en" and self.actor_en:
            return self.actor_en
        return self.actor

    def get_from_value(self, language: str = "zh") -> Optional[str]:
        """Get from value based on language."""
        if language == "en" and self.from_value_en:
            return self.from_value_en
        return self.from_value

    def get_to_value(self, language: str = "zh") -> Optional[str]:
        """Get to value based on language."""
        if language == "en" and self.to_value_en:
            return self.to_value_en
        return self.to_value

    def get_detail(self, language: str = "zh") -> Optional[str]:
        """Get detail based on language."""
        if language == "en" and self.detail_en:
            return self.detail_en
        return self.detail

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "event": self.event.value,
            "actor": self.actor,
            "from": self.from_value,
            "to": self.to_value,
            "detail": self.detail,
            "actor_en": self.actor_en,
            "from_en": self.from_value_en,
            "to_en": self.to_value_en,
            "detail_en": self.detail_en,
            "duration_from_previous": self.duration_from_previous,
        }


@dataclass
class Incident:
    """Incident data model."""
    order_number: str
    title: str
    priority: str
    category: str
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    affected_systems: list[str] = field(default_factory=list)
    sla: Optional[SLA] = None

    # i18n fields
    title_en: Optional[str] = None
    affected_systems_en: list[str] = field(default_factory=list)

    # Root cause data (from JSON or LLM)
    root_cause: Optional[RootCauseAnalysis] = None

    # Computed fields (set by analyzer)
    is_ongoing: bool = False
    total_duration_minutes: Optional[int] = None
    sla_response_met: Optional[bool] = None
    sla_resolution_met: Optional[bool] = None

    def get_title(self, language: str = "zh") -> str:
        """Get title based on language."""
        if language == "en" and self.title_en:
            return self.title_en
        return self.title

    def get_affected_systems(self, language: str = "zh") -> list[str]:
        """Get affected systems based on language."""
        if language == "en" and self.affected_systems_en:
            return self.affected_systems_en
        return self.affected_systems

    @classmethod
    def from_dict(cls, data: dict) -> "Incident":
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

        resolved_at = data.get("resolved_at")
        if resolved_at and isinstance(resolved_at, str):
            resolved_at = datetime.fromisoformat(resolved_at.replace("Z", "+00:00"))

        sla_data = data.get("sla")
        sla = SLA.from_dict(sla_data) if sla_data else None

        root_cause_data = data.get("root_cause")
        root_cause = RootCauseAnalysis.from_dict(root_cause_data) if root_cause_data else None

        return cls(
            order_number=data.get("order_number", ""),
            title=data.get("title", ""),
            priority=data.get("priority", "P4"),
            category=data.get("category", ""),
            status=data.get("status", ""),
            created_at=created_at,
            resolved_at=resolved_at,
            affected_systems=data.get("affected_systems", []),
            sla=sla,
            title_en=data.get("title_en"),
            affected_systems_en=data.get("affected_systems_en", []),
            root_cause=root_cause,
            is_ongoing=resolved_at is None,
        )

    def to_dict(self) -> dict:
        return {
            "order_number": self.order_number,
            "title": self.title,
            "title_en": self.title_en,
            "priority": self.priority,
            "category": self.category,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "affected_systems": self.affected_systems,
            "affected_systems_en": self.affected_systems_en,
            "root_cause": self.root_cause.to_dict() if self.root_cause else None,
            "is_ongoing": self.is_ongoing,
            "total_duration_minutes": self.total_duration_minutes,
            "sla_response_met": self.sla_response_met,
            "sla_resolution_met": self.sla_resolution_met,
        }


@dataclass
class Issue:
    """An identified issue in incident handling."""
    severity: IssueSeverity
    category: str  # e.g., "response", "escalation", "handover", "duration"
    title: str
    description: str
    timestamp: Optional[datetime] = None
    actor: Optional[str] = None
    metric_value: Optional[float] = None  # e.g., actual duration
    threshold_value: Optional[float] = None  # e.g., expected duration

    def to_dict(self) -> dict:
        return {
            "severity": self.severity.value,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "actor": self.actor,
            "metric_value": self.metric_value,
            "threshold_value": self.threshold_value,
        }


@dataclass
class IncidentAnalysis:
    """Complete analysis results for an incident."""
    incident: Incident
    timeline: list[TimelineEvent]

    # Time analysis
    response_time_minutes: Optional[int] = None
    resolution_time_minutes: Optional[int] = None
    phase_durations: dict = field(default_factory=dict)  # phase -> minutes

    # Flow analysis
    escalation_count: int = 0
    reassignment_count: int = 0
    unique_actors: list[str] = field(default_factory=list)
    handover_events: list[TimelineEvent] = field(default_factory=list)

    # Issues detected
    issues: list[Issue] = field(default_factory=list)

    # AI insights
    insights: dict = field(default_factory=dict)

    # Root cause analysis (generated or from data)
    root_cause_analysis: Optional[RootCauseAnalysis] = None

    # Action items for improvement tracking
    action_items: list[ActionItem] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "incident": self.incident.to_dict(),
            "timeline": [e.to_dict() for e in self.timeline],
            "response_time_minutes": self.response_time_minutes,
            "resolution_time_minutes": self.resolution_time_minutes,
            "phase_durations": self.phase_durations,
            "escalation_count": self.escalation_count,
            "reassignment_count": self.reassignment_count,
            "unique_actors": self.unique_actors,
            "issues": [i.to_dict() for i in self.issues],
            "insights": self.insights,
            "root_cause_analysis": self.root_cause_analysis.to_dict() if self.root_cause_analysis else None,
            "action_items": [a.to_dict() for a in self.action_items],
        }
