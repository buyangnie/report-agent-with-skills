"""
Office Theme Module for DOCX and PPTX Reports.

Provides unified color definitions and helper functions for styling
Office documents to match the HTML report quality.
"""

from docx.shared import Pt, Inches, RGBColor
from docx.oxml.ns import qn, nsmap
from docx.oxml import OxmlElement
from pptx.dml.color import RGBColor as PPTXRGBColor


# =============================================================================
# Color Palette (matching HTML CSS variables)
# =============================================================================

# Core colors as hex strings (for DOCX which uses hex without #)
COLORS = {
    # Primary brand colors
    "primary": "1e3a5f",       # Dark navy (header background)
    "primary_light": "2c5282",
    "accent": "3182ce",        # Blue accent
    
    # Status colors
    "success": "276749",       # Green
    "success_light": "c6f6d5",
    "warning": "c05621",       # Orange
    "warning_light": "feebc8",
    "danger": "9b2c2c",        # Red
    "danger_light": "fed7d7",
    
    # Neutral/Gray scale
    "gray_50": "f7fafc",
    "gray_100": "edf2f7",
    "gray_200": "e2e8f0",
    "gray_300": "cbd5e0",
    "gray_400": "a0aec0",
    "gray_500": "718096",
    "gray_600": "4a5568",
    "gray_700": "2d3748",
    "gray_800": "1a202c",
    "gray_900": "171923",
    
    # Text colors
    "text_primary": "1a202c",
    "text_secondary": "4a5568",
    "text_light": "ffffff",
    
    # Process-specific colors
    "incident": "1e40af",      # Deep blue
    "change": "065f46",        # Deep green
    "request": "92400e",       # Deep amber
    "problem": "9d174d",       # Deep pink
}

# PPTX Dark theme colors (for presentations)
PPTX_COLORS = {
    "background": "1a1f2e",
    "card_bg": "252b3d",
    "primary": "3182ce",
    "success": "38a169",
    "warning": "d69e2e",
    "danger": "c53030",
    "text_primary": "f7fafc",
    "text_secondary": "a0aec0",
    "accent": "4299e1",
}


# =============================================================================
# Helper Functions - DOCX
# =============================================================================

def hex_to_rgb(hex_color: str) -> RGBColor:
    """Convert hex color to DOCX RGBColor."""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return RGBColor(r, g, b)


def set_cell_shading(cell, hex_color: str) -> None:
    """Apply background shading to a DOCX table cell."""
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), hex_color.lstrip('#'))
    cell._tc.get_or_add_tcPr().append(shading)


def set_cell_border(cell, border_color: str = "e2e8f0", width: str = "4") -> None:
    """Set borders on a DOCX table cell."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    
    for border_name in ['top', 'left', 'bottom', 'right']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), width)
        border.set(qn('w:color'), border_color.lstrip('#'))
        tcBorders.append(border)
    
    tcPr.append(tcBorders)


def set_paragraph_shading(paragraph, hex_color: str) -> None:
    """Apply background shading to a paragraph."""
    pPr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), hex_color.lstrip('#'))
    pPr.append(shd)


def create_colored_run(paragraph, text: str, font_size: int = 11, 
                       bold: bool = False, color: str = None) -> None:
    """Add a styled run to a paragraph."""
    run = paragraph.add_run(text)
    run.font.size = Pt(font_size)
    run.bold = bold
    if color:
        run.font.color.rgb = hex_to_rgb(color)
    return run


# =============================================================================
# Helper Functions - PPTX
# =============================================================================

def pptx_hex_to_rgb(hex_color: str) -> PPTXRGBColor:
    """Convert hex color to PPTX RGBColor."""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return PPTXRGBColor(r, g, b)


# =============================================================================
# Status-based Color Mapping
# =============================================================================

def get_status_color(status: str, for_pptx: bool = False) -> str:
    """Get color hex for a status value."""
    color_map = {
        "success": COLORS["success"],
        "normal": COLORS["success"],
        "warning": COLORS["warning"],
        "danger": COLORS["danger"],
        "critical": COLORS["danger"],
    }
    return color_map.get(status.lower(), COLORS["gray_500"])


def get_status_bg_color(status: str) -> str:
    """Get background color for a status value (lighter shade)."""
    bg_map = {
        "success": COLORS["success_light"],
        "normal": COLORS["success_light"],
        "warning": COLORS["warning_light"],
        "danger": COLORS["danger_light"],
        "critical": COLORS["danger_light"],
    }
    return bg_map.get(status.lower(), COLORS["gray_100"])


def get_priority_color(priority: str) -> str:
    """Get color for priority level."""
    priority_map = {
        "critical": COLORS["danger"],
        "urgent": COLORS["danger"],
        "high": COLORS["warning"],
        "medium": COLORS["accent"],
        "low": COLORS["success"],
        "attention": COLORS["accent"],
        "warning": COLORS["warning"],
    }
    return priority_map.get(priority.lower(), COLORS["gray_500"])


def get_process_color(process: str) -> str:
    """Get color for ITIL process type."""
    process_map = {
        "incident": COLORS["incident"],
        "change": COLORS["change"],
        "request": COLORS["request"],
        "problem": COLORS["problem"],
    }
    return process_map.get(process.lower(), COLORS["primary"])


# =============================================================================
# Typography Settings
# =============================================================================

FONTS = {
    "heading": "Calibri",
    "body": "Calibri",
    "chinese_heading": "PingFang SC",
    "chinese_body": "Microsoft YaHei",
    "monospace": "Consolas",
}

FONT_SIZES = {
    "title": 28,
    "heading1": 18,
    "heading2": 14,
    "body": 11,
    "small": 9,
    "caption": 8,
}


# =============================================================================
# Document Dimensions
# =============================================================================

DOCX_MARGINS = {
    "top": Inches(0.75),
    "bottom": Inches(0.75),
    "left": Inches(0.75),
    "right": Inches(0.75),
}

PPTX_DIMENSIONS = {
    "width": Inches(13.333),  # 16:9 aspect ratio
    "height": Inches(7.5),
}
