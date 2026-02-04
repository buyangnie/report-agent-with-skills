"""
Configuration module for BO Workload Performance Report.

Contains thresholds, weights, and settings for analysis.
"""

import os
from pathlib import Path

# =============================================================================
# Path Configuration
# =============================================================================

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "output"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)

# Data file
DATA_FILE = DATA_DIR / "Incidents-exported.xlsx"

# =============================================================================
# API Configuration
# =============================================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "deepseek-chat")

# =============================================================================
# BO Tier Classification Thresholds
# =============================================================================

# Complexity Index: Resolver avg MTTR / global avg MTTR
# > 1.5 suggests handling more complex issues
COMPLEXITY_INDEX_TIER2_THRESHOLD = 1.2
COMPLEXITY_INDEX_TIER3_THRESHOLD = 1.8

# Priority Index: % of P1+P2 tickets handled
# Higher percentage suggests higher-tier work
PRIORITY_INDEX_TIER2_THRESHOLD = 0.15  # 15% P1+P2
PRIORITY_INDEX_TIER3_THRESHOLD = 0.30  # 30% P1+P2

# Specialization: Herfindahl Index (category concentration)
# Higher value means more specialized (fewer categories)
SPECIALIZATION_TIER2_THRESHOLD = 0.25
SPECIALIZATION_TIER3_THRESHOLD = 0.40

# Minimum tickets to be considered for tier classification
MIN_TICKETS_FOR_CLASSIFICATION = 5

# =============================================================================
# Bottleneck Scoring Weights
# =============================================================================

BOTTLENECK_WEIGHTS = {
    "backlog": 0.30,        # Current open tickets
    "mttr": 0.25,           # Average resolution time
    "replaceability": 0.25, # How many others can do the same work
    "sla_trend": 0.20       # SLA violation trend
}

# Backlog thresholds (calibrated for typical BO queue)
BACKLOG_WARNING_THRESHOLD = 3   # 3 open tickets - early warning
BACKLOG_CRITICAL_THRESHOLD = 5  # 5 open tickets - critical

# MTTR thresholds (in hours) - calibrated against SLA
MTTR_WARNING_THRESHOLD = 12   # 12 hours (2x P2 SLA)
MTTR_CRITICAL_THRESHOLD = 48  # 48 hours (P4 SLA limit)

# =============================================================================
# Single-Point Dependency Risk
# =============================================================================

# Category with only 1-2 resolvers is high risk
SINGLE_POINT_RISK_THRESHOLD = 2

# =============================================================================
# Workload Balance
# =============================================================================

# Gini coefficient thresholds
GINI_GOOD_THRESHOLD = 0.3      # < 0.3 = well balanced
GINI_WARNING_THRESHOLD = 0.5   # 0.3-0.5 = moderate imbalance
# > 0.5 = severe imbalance

# Overload threshold: resolver has > X times average workload
OVERLOAD_MULTIPLIER = 1.5

# =============================================================================
# Knowledge Silo Detection
# =============================================================================

# Minimum recurrence count to be flagged
RECURRENCE_THRESHOLD = 3

# Category handled by only 1 person is a knowledge silo
KNOWLEDGE_SILO_THRESHOLD = 1

# =============================================================================
# Long-Tail Analysis
# =============================================================================

# Tickets taking > 48 hours are considered long-tail
LONG_TAIL_HOURS = 48

# =============================================================================
# SLA Configuration
# =============================================================================

# Default SLA if not specified (hours) - matches contract SLA_Criteria sheet
DEFAULT_SLA = {
    "P1": 2,   # Contract: 2 hours
    "P2": 6,   # Contract: 6 hours
    "P3": 24,  # Contract: 24 hours
    "P4": 48   # Contract: 48 hours
}

# =============================================================================
# Priority Weights for Weighted Workload Calculation
# =============================================================================

# Higher priority tickets count more towards weighted workload
# This reflects that handling P1/P2 is more valuable/difficult than P3/P4
PRIORITY_WEIGHTS = {
    "P1": 4,   # Critical priority = 4x weight
    "P2": 3,   # High priority = 3x weight
    "P3": 2,   # Medium priority = 2x weight
    "P4": 1    # Low priority = 1x weight
}

# =============================================================================
# Excluded Resolvers
# =============================================================================

EXCLUDED_RESOLVERS = ["Unassigned", "System", "Auto", ""]

# =============================================================================
# BO Categories (categories typically handled by BO)
# =============================================================================

BO_CATEGORIES = [
    "Database",
    "Architecture", 
    "Network",
    "Security",
    "Integration",
    "Infrastructure"
]

# =============================================================================
# Chart Configuration
# =============================================================================

CHART_FIGSIZE = (10, 6)
CHART_DPI = 150

# Color palette (Corporate Modern)
COLORS = {
    "primary": "#2E5090",
    "secondary": "#4A90D9",
    "success": "#28A745",
    "warning": "#FFC107",
    "danger": "#DC3545",
    "info": "#17A2B8",
    "light": "#F8F9FA",
    "dark": "#343A40",
    "tier1": "#6C757D",
    "tier2": "#4A90D9",
    "tier3": "#2E5090"
}

# Tier color mapping
TIER_COLORS = {
    "Tier 1": COLORS["tier1"],
    "Tier 2": COLORS["tier2"],
    "Tier 3": COLORS["tier3"]
}
