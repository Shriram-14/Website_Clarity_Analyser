"""ReportLab PDF generation for homepage clarity analysis results."""

from __future__ import annotations

import io
import textwrap
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ---------------------------------------------------------------------------
# Brand palette
# ---------------------------------------------------------------------------
_BRAND_DARK = colors.HexColor("#1E293B")   # slate-900 — headings / header bg
_BRAND_MID = colors.HexColor("#334155")    # slate-700 — body text
_BRAND_LIGHT = colors.HexColor("#F1F5F9")  # slate-100 — section bg tints
_ACCENT = colors.HexColor("#6366F1")       # indigo-500 — accents / dividers

_SCORE_COLORS = {
    "high": colors.HexColor("#16A34A"),    # green-600  (8–10)
    "mid": colors.HexColor("#D97706"),     # amber-600  (5–7)
    "low": colors.HexColor("#DC2626"),     # red-600    (1–4)
}

PAGE_WIDTH, PAGE_HEIGHT = A4


# ---------------------------------------------------------------------------
# Style helpers
# ---------------------------------------------------------------------------

def _build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=base["Title"],
            fontSize=22,
            leading=28,
            textColor=colors.white,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "ReportSubtitle",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#CBD5E1"),
            alignment=TA_CENTER,
            spaceAfter=0,
        ),
        "section_heading": ParagraphStyle(
            "SectionHeading",
            parent=base["Heading2"],
            fontSize=13,
            leading=18,
            textColor=_BRAND_DARK,
            spaceBefore=14,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "BodyText",
            parent=base["Normal"],
            fontSize=10,
            leading=15,
            textColor=_BRAND_MID,
            spaceAfter=4,
        ),
        "bullet": ParagraphStyle(
            "BulletItem",
            parent=base["Normal"],
            fontSize=10,
            leading=15,
            textColor=_BRAND_MID,
            leftIndent=14,
            bulletIndent=0,
            spaceAfter=3,
        ),
        "monospace": ParagraphStyle(
            "Monospace",
            parent=base["Code"],
            fontSize=7.5,
            leading=11,
            textColor=colors.HexColor("#374151"),
            backColor=colors.HexColor("#F9FAFB"),
            spaceAfter=0,
        ),
        "score_label": ParagraphStyle(
            "ScoreLabel",
            parent=base["Normal"],
            fontSize=11,
            leading=14,
            textColor=colors.white,
            alignment=TA_CENTER,
        ),
        "score_value": ParagraphStyle(
            "ScoreValue",
            parent=base["Normal"],
            fontSize=30,
            leading=36,
            textColor=colors.white,
            alignment=TA_CENTER,
        ),
        "meta": ParagraphStyle(
            "Meta",
            parent=base["Normal"],
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#64748B"),
            alignment=TA_LEFT,
        ),
    }


def _score_color(score: float | None) -> colors.Color:
    if score is None:
        return _BRAND_MID
    if score >= 8:
        return _SCORE_COLORS["high"]
    if score >= 5:
        return _SCORE_COLORS["mid"]
    return _SCORE_COLORS["low"]


def _score_band_label(score: float | None) -> str:
    if score is None:
        return "N/A"
    if score >= 8:
        return "Strong"
    if score >= 5:
        return "Moderate"
    return "Needs Work"


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def _header_table(styles: dict, source_label: str, generated_at: str) -> Table:
    """Dark branded header spanning full width."""
    title_cell = Paragraph("Website Clarity Analysis Report", styles["title"])
    subtitle_cell = Paragraph("Powered by Google Gemini", styles["subtitle"])

    data = [[title_cell], [subtitle_cell]]
    tbl = Table(data, colWidths=[PAGE_WIDTH - 4 * cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _BRAND_DARK),
        ("TOPPADDING", (0, 0), (0, 0), 18),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 18),
        ("LEFTPADDING", (0, 0), (-1, -1), 20),
        ("RIGHTPADDING", (0, 0), (-1, -1), 20),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    return tbl


def _meta_table(styles: dict, source_label: str, generated_at: str) -> Table:
    """Two-column meta row: source on left, timestamp on right."""
    left = Paragraph(f"<b>Source:</b> {source_label}", styles["meta"])
    right = Paragraph(f"<b>Generated:</b> {generated_at}", styles["meta"])
    tbl = Table([[left, right]], colWidths=[(PAGE_WIDTH - 4 * cm) / 2] * 2)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _BRAND_LIGHT),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    return tbl


def _score_block(styles: dict, score: float | None) -> Table:
    """Coloured score badge with band label."""
    bg = _score_color(score)
    score_str = (
        str(int(score)) if score is not None and score == int(score)
        else (str(score) if score is not None else "—")
    )
    band = _score_band_label(score)

    label_p = Paragraph("CLARITY SCORE", styles["score_label"])
    value_p = Paragraph(f"{score_str} / 10", styles["score_value"])
    band_p = Paragraph(band, styles["score_label"])

    cell_w = 6 * cm
    tbl = Table(
        [[label_p], [value_p], [band_p]],
        colWidths=[cell_w],
    )
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("TOPPADDING", (0, 0), (0, 0), 10),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROUNDEDCORNERS", [8, 8, 8, 8]),
    ]))
    return tbl


def _divider() -> HRFlowable:
    return HRFlowable(
        width="100%",
        thickness=1,
        color=colors.HexColor("#E2E8F0"),
        spaceAfter=6,
        spaceBefore=6,
    )


def _section(heading: str, content_flowables: list, styles: dict) -> list:
    """Heading + content with a trailing divider."""
    items: list = [Paragraph(heading, styles["section_heading"])]
    items.extend(content_flowables)
    items.append(_divider())
    return items


def _wrap_monospace_line(line: str, width: int = 90) -> list[str]:
    """Hard-wrap a single line so it fits the monospace block."""
    if len(line) <= width:
        return [line]
    return textwrap.wrap(line, width=width) or [""]


def _json_flowables(raw_json: str, styles: dict) -> list:
    """Render raw JSON as monospaced paragraphs with light background."""
    lines: list[str] = []
    for raw_line in raw_json.splitlines():
        escaped = raw_line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        for wrapped in _wrap_monospace_line(escaped, width=95):
            lines.append(wrapped)

    # Group into one table cell so background covers the whole block
    joined_html = "<br/>".join(lines) if lines else "(empty)"
    para = Paragraph(joined_html, styles["monospace"])
    cell_w = PAGE_WIDTH - 4 * cm
    tbl = Table([[para]], colWidths=[cell_w])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F9FAFB")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    return [tbl]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_pdf_report(
    parsed: dict,
    source_label: str,
    raw_json: str,
) -> bytes:
    """
    Build and return a PDF report as raw bytes.

    Parameters
    ----------
    parsed:       The structured dict from Gemini (business_summary, clarity_score, …).
    source_label: Human-readable origin string, e.g. "scraped:https://…" or "manual_paste".
    raw_json:     Pretty-printed JSON string of the full Gemini response.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Website Clarity Analysis Report",
        author="Website Clarity Analyzer",
    )

    styles = _build_styles()
    generated_at = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Normalise score
    raw_score = parsed.get("clarity_score")
    try:
        score_num: float | None = float(raw_score)
    except (TypeError, ValueError):
        score_num = None

    # Normalise source label for display
    display_source = source_label
    if display_source.startswith("scraped:"):
        display_source = display_source[len("scraped:"):]

    # -----------------------------------------------------------------------
    story: list = []

    # Header banner
    story.append(_header_table(styles, display_source, generated_at))
    story.append(Spacer(1, 0.3 * cm))

    # Meta row
    story.append(_meta_table(styles, display_source, generated_at))
    story.append(Spacer(1, 0.5 * cm))

    # Score badge (standalone, centred)
    story.append(Paragraph("Clarity Score", styles["section_heading"]))
    score_tbl = _score_block(styles, score_num)
    # Centre the badge via a wrapper table
    wrapper = Table([[score_tbl]], colWidths=[PAGE_WIDTH - 4 * cm])
    wrapper.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "LEFT")]))
    story.append(wrapper)
    story.append(_divider())

    # Business Summary
    summary_text = parsed.get("business_summary") or "—"
    story.extend(_section(
        "Business Summary",
        [Paragraph(summary_text, styles["body"])],
        styles,
    ))

    # Score Reasoning
    reasoning_text = parsed.get("score_reasoning") or "—"
    story.extend(_section(
        "Score Reasoning",
        [Paragraph(reasoning_text, styles["body"])],
        styles,
    ))

    # Suggestions
    suggestions = parsed.get("suggestions")
    if isinstance(suggestions, list) and suggestions:
        bullet_items = [
            Paragraph(f"\u2022&nbsp;&nbsp;{item}", styles["bullet"])
            for item in suggestions
            if item
        ]
    else:
        bullet_items = [Paragraph("No suggestions provided.", styles["body"])]
    story.extend(_section("Suggestions for Improvement", bullet_items, styles))

    # Raw JSON
    story.extend(_section(
        "Raw Gemini JSON Response",
        _json_flowables(raw_json, styles),
        styles,
    ))

    # Footer note
    story.append(Spacer(1, 0.3 * cm))
    footer_text = (
        "This report was generated automatically by Website Clarity Analyzer. "
        "Results reflect Gemini's analysis of the homepage text provided at the time of evaluation."
    )
    story.append(Paragraph(footer_text, styles["meta"]))

    doc.build(story)
    return buf.getvalue()
