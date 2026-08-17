"""
=========================================================
report_styles.py
---------------------------------------------------------
Centralized ReportLab styles for the
Solar Wind Deployment Intelligence project.

Author : HorizonOne
=========================================================
"""

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import TableStyle


# =========================================================
# Color Palette
# =========================================================

PRIMARY = colors.HexColor("#0B5ED7")
SECONDARY = colors.HexColor("#198754")
ACCENT = colors.HexColor("#0D6EFD")

TITLE_COLOR = colors.HexColor("#003366")
HEADER_COLOR = colors.HexColor("#1F4E79")

LIGHT_BLUE = colors.HexColor("#D9EAF7")
LIGHT_GREEN = colors.HexColor("#EAF7EA")
LIGHT_GREY = colors.HexColor("#F5F5F5")

SUCCESS = colors.HexColor("#2E8B57")
WARNING = colors.HexColor("#FF9800")
DANGER = colors.HexColor("#D32F2F")

TEXT = colors.black


# =========================================================
# Paragraph Styles
# =========================================================

_styles = getSampleStyleSheet()


TITLE_STYLE = ParagraphStyle(
    "TitleStyle",
    parent=_styles["Title"],
    alignment=TA_CENTER,
    fontName="Helvetica-Bold",
    fontSize=22,
    leading=28,
    textColor=TITLE_COLOR,
    spaceAfter=18,
)

SUBTITLE_STYLE = ParagraphStyle(
    "SubtitleStyle",
    parent=_styles["Heading2"],
    alignment=TA_CENTER,
    fontName="Helvetica",
    fontSize=13,
    leading=18,
    textColor=HEADER_COLOR,
    spaceAfter=18,
)

HEADING_STYLE = ParagraphStyle(
    "HeadingStyle",
    parent=_styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=15,
    leading=18,
    textColor=HEADER_COLOR,
    spaceBefore=12,
    spaceAfter=10,
)

SUBHEADING_STYLE = ParagraphStyle(
    "SubHeadingStyle",
    parent=_styles["Heading3"],
    fontName="Helvetica-Bold",
    fontSize=12,
    leading=16,
    textColor=PRIMARY,
    spaceBefore=8,
    spaceAfter=6,
)

BODY_STYLE = ParagraphStyle(
    "BodyStyle",
    parent=_styles["BodyText"],
    fontName="Helvetica",
    fontSize=10,
    leading=16,
    textColor=TEXT,
)

SMALL_STYLE = ParagraphStyle(
    "SmallStyle",
    parent=_styles["BodyText"],
    fontName="Helvetica",
    fontSize=8,
    leading=12,
    textColor=colors.grey,
)

CENTER_STYLE = ParagraphStyle(
    "CenterStyle",
    parent=BODY_STYLE,
    alignment=TA_CENTER,
)

RIGHT_STYLE = ParagraphStyle(
    "RightStyle",
    parent=BODY_STYLE,
    alignment=TA_RIGHT,
)

SUCCESS_STYLE = ParagraphStyle(
    "SuccessStyle",
    parent=BODY_STYLE,
    fontName="Helvetica-Bold",
    textColor=SUCCESS,
    fontSize=12,
)

WARNING_STYLE = ParagraphStyle(
    "WarningStyle",
    parent=BODY_STYLE,
    fontName="Helvetica-Bold",
    textColor=WARNING,
    fontSize=12,
)

DANGER_STYLE = ParagraphStyle(
    "DangerStyle",
    parent=BODY_STYLE,
    fontName="Helvetica-Bold",
    textColor=DANGER,
    fontSize=12,
)


# =========================================================
# Table Styles
# =========================================================

TABLE_STYLE = TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, 0), 10),

    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
    ("TOPPADDING", (0, 0), (-1, 0), 8),

    ("BACKGROUND", (0, 1), (-1, -1), colors.white),

    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
    ("FONTSIZE", (0, 1), (-1, -1), 9),

    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

    ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
    ("TOPPADDING", (0, 1), (-1, -1), 6),
])


SUMMARY_TABLE_STYLE = TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), HEADER_COLOR),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),

    ("BACKGROUND", (0, 1), (-1, -1), LIGHT_GREY),

    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 6),

    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
])


# =========================================================
# Recommendation Helper
# =========================================================

def get_recommendation_style(recommendation: str):
    """
    Return the paragraph style based on
    deployment recommendation.
    """

    recommendation = recommendation.upper()

    if "HIGHLY" in recommendation:
        return SUCCESS_STYLE

    if "MODERATE" in recommendation:
        return WARNING_STYLE

    return DANGER_STYLE


# =========================================================
# Export All Styles
# =========================================================

def get_styles():
    """
    Returns all styles as a dictionary.
    """

    return {
        "title": TITLE_STYLE,
        "subtitle": SUBTITLE_STYLE,
        "heading": HEADING_STYLE,
        "subheading": SUBHEADING_STYLE,
        "body": BODY_STYLE,
        "small": SMALL_STYLE,
        "center": CENTER_STYLE,
        "right": RIGHT_STYLE,
        "success": SUCCESS_STYLE,
        "warning": WARNING_STYLE,
        "danger": DANGER_STYLE,
        "table": TABLE_STYLE,
        "summary_table": SUMMARY_TABLE_STYLE,
    }