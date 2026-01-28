"""
Configuration file for Incident Quality Report.
Defines thresholds and system parameters.
"""

# ============================================
# ANALYSIS THRESHOLDS
# ============================================

# SLA Compliance threshold (below this triggers alert)
SLA_THRESHOLD = 0.95  # 95%

# Volume change threshold (above this triggers spike alert)
VOLUME_SPIKE_THRESHOLD = 0.20  # 20%

# MTTR thresholds (hours)
MTTR_WARNING_THRESHOLD = 24  # Hours
MTTR_CRITICAL_THRESHOLD = 48  # Hours

# Long-tail ticket threshold (hours)
LONG_TAIL_THRESHOLD = 48  # Hours

# Unassigned ticket threshold (percentage)
UNASSIGNED_WARNING_THRESHOLD = 0.05  # 5%

# Personnel performance thresholds
HIGH_VOLUME_THRESHOLD = 50  # Tickets per person
LOW_EFFICIENCY_THRESHOLD = 0.85  # Below 85% SLA rate

# ============================================
# CACHE CONFIGURATION
# ============================================

# AI insights cache settings
MAX_CACHE_ENTRIES = 200
CACHE_EXPIRY_DAYS = 30

# ============================================
# API CONFIGURATION
# ============================================

# API retry settings
MAX_API_RETRIES = 3
API_BASE_DELAY = 1  # seconds
API_TIMEOUT = 30  # seconds

# ============================================
# REPORT CONFIGURATION
# ============================================

# Number of items to display in reports
TOP_N_VIOLATORS = 10
TOP_N_CATEGORIES = 8
TOP_N_KEYWORDS = 15
TOP_N_VIOLATIONS_DETAIL = 15

# Chart dimensions
CHART_DPI = 100
CHART_FIGURE_SIZE = (10, 6)

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_threshold(key: str, default=None):
    """Get a threshold value by key name."""
    globals_dict = globals()
    return globals_dict.get(key, default)


def update_threshold(key: str, value):
    """Update a threshold value dynamically."""
    globals_dict = globals()
    if key in globals_dict:
        globals_dict[key] = value
        return True
    return False
