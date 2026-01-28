"""
Utility functions for SLA Violation Analysis Report.
"""
import os

# Paths
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(SKILL_DIR, 'data')
OUTPUT_DIR = os.path.join(SKILL_DIR, 'output')
IMG_DIR = os.path.join(OUTPUT_DIR, 'images')


def get_data_file():
    """Find the first xlsx file in data directory."""
    for f in os.listdir(DATA_DIR):
        if f.endswith('.xlsx'):
            return os.path.join(DATA_DIR, f)
    raise FileNotFoundError("No Excel file found in data/ directory")


def ensure_dirs():
    """Ensure output directories exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(IMG_DIR, exist_ok=True)


# ============================================
# DESIGN SYSTEM
# ============================================

COLORS = {
    'primary': '#3b82f6',
    'primary_light': '#93c5fd',
    'primary_dark': '#1e40af',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'text': '#374151',
    'text_secondary': '#6b7280',
    'border': '#e5e7eb',
    'background': '#f3f4f6',
    'card': '#ffffff',
}

CHART_COLORS = [
    '#3b82f6',  # Blue
    '#10b981',  # Emerald
    '#f59e0b',  # Amber
    '#ef4444',  # Red
    '#8b5cf6',  # Violet
    '#06b6d4',  # Cyan
]

RISK_COLORS = {
    'High': '#ef4444',
    'Medium': '#f59e0b',
    'Low': '#10b981',
}

ATTRIBUTION_COLORS = {
    'Process': '#3b82f6',
    'Resource': '#8b5cf6',
    'External': '#f59e0b',
    'TimeWindow': '#06b6d4',
}
