"""
Configuration settings for Major Incident Analysis Report.
"""
from pathlib import Path

# =============================================================================
# Directory Paths
# =============================================================================
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
IMAGES_DIR = OUTPUT_DIR / "images"

# Ensure directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)

# =============================================================================
# SLA Thresholds (Default, can be overridden by incident data)
# =============================================================================
DEFAULT_SLA = {
    "P1": {"response_minutes": 15, "resolution_hours": 2},
    "P2": {"response_minutes": 30, "resolution_hours": 6},
    "P3": {"response_minutes": 45, "resolution_hours": 24},
    "P4": {"response_minutes": 60, "resolution_hours": 48},
}

# =============================================================================
# Time Analysis Thresholds
# =============================================================================
# Response time thresholds (in minutes)
RESPONSE_TIME_WARNING_MULTIPLIER = 1.0   # 100% of SLA
RESPONSE_TIME_CRITICAL_MULTIPLIER = 2.0  # 200% of SLA

# Phase duration thresholds (in minutes)
PHASE_DURATION_THRESHOLDS = {
    "short": 15,      # < 15 min is fast
    "normal": 60,     # 15-60 min is normal
    "long": 180,      # 60-180 min is slow
    "critical": 360,  # > 360 min (6h) is critical
}

# Gap between events threshold (in minutes)
EVENT_GAP_WARNING = 30    # 30 min gap triggers warning
EVENT_GAP_CRITICAL = 120  # 2 hour gap triggers critical

# =============================================================================
# Flow Analysis Thresholds
# =============================================================================
# Escalation thresholds
ESCALATION_COUNT_WARNING = 2   # 2 escalations trigger warning
ESCALATION_COUNT_CRITICAL = 4  # 4+ escalations trigger critical

# Reassignment thresholds
REASSIGNMENT_COUNT_WARNING = 3   # 3 reassignments trigger warning
REASSIGNMENT_COUNT_CRITICAL = 5  # 5+ reassignments trigger critical

# Handover wait time threshold (in minutes)
HANDOVER_WAIT_WARNING = 15   # 15 min wait triggers warning
HANDOVER_WAIT_CRITICAL = 60  # 1 hour wait triggers critical

# =============================================================================
# Issue Severity Levels
# =============================================================================
SEVERITY_LEVELS = {
    "critical": {"color": "#ef4444", "label": "Critical", "weight": 4},
    "high": {"color": "#f97316", "label": "High", "weight": 3},
    "medium": {"color": "#eab308", "label": "Medium", "weight": 2},
    "low": {"color": "#22c55e", "label": "Low", "weight": 1},
}

# =============================================================================
# AI Insight Generation
# =============================================================================
# OpenAI-compatible API settings (loaded from .env)
OPENAI_MODEL = "deepseek-chat"
OPENAI_MAX_TOKENS = 1500
OPENAI_TEMPERATURE = 0.7

# Cache settings
INSIGHT_CACHE_MAX_SIZE = 100
INSIGHT_CACHE_TTL_DAYS = 30

# =============================================================================
# Report Settings
# =============================================================================
# Design system colors (matching incident-quality-report)
COLORS = {
    "primary": "#3b82f6",      # Blue
    "success": "#10b981",      # Emerald
    "warning": "#f59e0b",      # Amber
    "danger": "#ef4444",       # Red
    "info": "#06b6d4",         # Cyan
    "text": "#374151",         # Gray 700
    "text_light": "#6b7280",   # Gray 500
    "background": "#f3f4f6",   # Gray 100
    "border": "#e5e7eb",       # Gray 200
}

# Chart colors for timeline
TIMELINE_COLORS = {
    "created": "#3b82f6",
    "assigned": "#10b981",
    "status_change": "#8b5cf6",
    "escalated": "#f97316",
    "reassigned": "#eab308",
    "note": "#6b7280",
    "resolved": "#10b981",
    "closed": "#374151",
    "reopened": "#ef4444",
}

# Report title templates
REPORT_TITLE = {
    "en": "Major Incident Analysis Report",
    "zh": "重大事故分析报告",
}
