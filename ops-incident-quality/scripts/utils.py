"""
Utility functions and configuration for the Ops Deep Dive Report Skill.
Modern Light Theme - Professional Design System
"""
import os

# Paths
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(SKILL_DIR, 'data')
OUTPUT_DIR = os.path.join(SKILL_DIR, 'output')
IMG_DIR = os.path.join(OUTPUT_DIR, 'images')

# Find the first xlsx file in data dir
def get_data_file():
    for f in os.listdir(DATA_DIR):
        if f.endswith('.xlsx'):
            return os.path.join(DATA_DIR, f)
    raise FileNotFoundError("No Excel file found in data/ directory")

DATA_PATH = None  # Will be set at runtime

def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(IMG_DIR, exist_ok=True)

# ============================================
# MODERN LIGHT DESIGN SYSTEM
# ============================================

# Primary Colors (Hues lowered in saturation)
COLORS = {
    # Core
    'primary': '#3b82f6',       # Blue 500 - Clear, professional blue
    'primary_light': '#93c5fd', # Blue 300
    'primary_dark': '#1e40af',  # Blue 800
    
    # Semantic (Softer)
    'success': '#10b981',       # Emerald 500
    'warning': '#f59e0b',       # Amber 500
    'danger': '#ef4444',        # Red 500
    
    # Neutrals
    'text': '#374151',          # Gray 700 - Softer than black
    'text_secondary': '#6b7280', # Gray 500
    'border': '#e5e7eb',        # Gray 200
    'background': '#f3f4f6',    # Gray 100
    'card': '#ffffff',          # White
    
    # Legacy aliases
    'accent': '#3b82f6',
    'secondary': '#6b7280',
    'neutral': '#9ca3af',
    'light': '#f9fafb',
}

# Chart Colors - "Corporate Modern" (Clean, distinct but not harsh)
CHART_COLORS = [
    '#3b82f6',  # Blue
    '#10b981',  # Emerald
    '#f59e0b',  # Amber
    '#ef4444',  # Red
    '#8b5cf6',  # Violet
    '#06b6d4',  # Cyan
    '#ec4899',  # Pink
    '#6b7280',  # Gray
]

# Pastel variants for backgrounds/secondary elements
PASTEL_COLORS = [
    '#dbeafe',  # Pastel Blue
    '#d1fae5',  # Pastel Emerald
    '#fef3c7',  # Pastel Amber
    '#fee2e2',  # Pastel Red
    '#ede9fe',  # Pastel Violet
    '#cffafe',  # Pastel Cyan
]

# Thresholds for rule-based insights
THRESHOLDS = {
    'sla_warning': 95.0,
    'sla_critical': 90.0,
    'trend_spike': 20.0,
    'long_tail_hours': 48,
}
