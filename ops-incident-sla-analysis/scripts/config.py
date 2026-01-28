"""
Configuration for SLA Violation Analysis Report.
"""

# ============================================
# SLA THRESHOLDS
# ============================================

# Risk level thresholds (percentage of SLA consumed)
RISK_HIGH_THRESHOLD = 80  # >80% of SLA consumed = High Risk
RISK_MEDIUM_THRESHOLD = 60  # 60-80% = Medium Risk

# SLA compliance target
SLA_TARGET = 95.0  # 95%

# ============================================
# ATTRIBUTION RULES
# ============================================

# Process factors
MAX_REASSIGNMENTS = 3  # More than this = "too many reassignments"
MAX_ESCALATIONS = 2  # More than this = "escalation delay"
INITIAL_ASSIGNMENT_THRESHOLD = 30  # minutes

# Resource factors
CONCURRENT_TICKET_THRESHOLD = 5  # Overloaded if handling more than this

# External dependency factors
SUSPEND_TIME_RATIO = 0.5  # If suspend time > 50% of resolution time

# Time window factors
WORK_HOURS_START = 9
WORK_HOURS_END = 18
WEEKEND_DAYS = [5, 6]  # Saturday, Sunday

# ============================================
# REPORT CONFIGURATION
# ============================================

TOP_N_VIOLATIONS = 20
TOP_N_RISK = 10
TOP_N_BY_CATEGORY = 10

# Chart settings
CHART_DPI = 100
CHART_FIGURE_SIZE = (10, 6)

# ============================================
# CACHE CONFIGURATION
# ============================================

MAX_CACHE_ENTRIES = 100
CACHE_EXPIRY_DAYS = 7
