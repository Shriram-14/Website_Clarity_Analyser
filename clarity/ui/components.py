"""Reusable Streamlit layout fragments."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import streamlit as st

from clarity.config import MISSING_API_KEY_HINT
from clarity.report import generate_pdf_report


def render_sidebar(has_api_key: bool) -> None:
    st.sidebar.markdown("### Instructions")
    st.sidebar.markdown(
        "1. Enter a **homepage URL** and click **Analyze Website**, **or**\n"
        "2. Paste homepage copy into the text area and click **Analyze Pasted Text**.\n\n"
        "Scraped pages are summarized by Gemini against a messaging clarity rubric."
    )

    st.sidebar.markdown("### Gemini API key status")
    if has_api_key:
        st.sidebar.success("API key is configured.")
    else:
        st.sidebar.error(
            "No key found. Add **GEMINI_API_KEY** or **GOOGLE_API_KEY** to `.env` "
            "or Streamlit `.streamlit/secrets.toml`."
        )

    st.sidebar.markdown("### Scoring rubric")
    st.sidebar.markdown(
        "**10** — Immediately clear, specific, compelling, action-oriented.\n\n"
        "**8–9** — Clear with minor specificity or CTA gaps.\n\n"
        "**6–7** — Understandable but some vague language or missing detail.\n\n"
        "**4–5** — Partially clear; offer may not land quickly.\n\n"
        "**1–3** — Confusing or unclear what the business does."
    )


def display_analysis_results(parsed: dict, raw_json_pretty: str) -> None:
    st.markdown("### Business Summary")
    st.write(parsed.get("business_summary", "—"))

    score = parsed.get("clarity_score")
    try:
        score_num = float(score)
    except (TypeError, ValueError):
        score_num = None
    col1, _col2 = st.columns([1, 3])
    with col1:
        if score_num is not None:
            label = (
                f"{int(score_num)} / 10"
                if score_num == int(score_num)
                else f"{score_num} / 10"
            )
            st.metric("Clarity Score", label)
        else:
            st.metric("Clarity Score", "—")

    st.markdown("### Score Reasoning")
    st.write(parsed.get("score_reasoning", "—"))

    suggestions = parsed.get("suggestions")
    st.markdown("### Suggestions")
    if isinstance(suggestions, list):
        for item in suggestions:
            if item:
                st.markdown(f"- {item}")
    else:
        st.write("—")

    st.markdown("### Raw JSON")
    st.code(raw_json_pretty, language="json")


def render_download_pdf_button(
    parsed: dict,
    source_label: str,
    raw_json_pretty: str,
) -> None:
    """Render a Streamlit download button that streams the PDF to the browser."""
    try:
        pdf_bytes = generate_pdf_report(parsed, source_label, raw_json_pretty)
    except Exception as exc:  # noqa: BLE001
        st.warning(f"Could not generate PDF report: {exc}")
        return

    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"clarity_report_{timestamp}.pdf"

    st.download_button(
        label="Download PDF Report",
        data=pdf_bytes,
        file_name=filename,
        mime="application/pdf",
        type="primary",
        icon=":material/picture_as_pdf:",
    )


def warn_if_missing_api_key(triggered_analysis: bool, has_api_key: bool) -> None:
    if triggered_analysis and not has_api_key:
        st.warning(MISSING_API_KEY_HINT)


def dump_gemini_on_error(raw: str | None, *, taller: bool = False) -> None:
    if raw:
        st.text_area("Raw Gemini response", raw, height=240 if taller else 200)
