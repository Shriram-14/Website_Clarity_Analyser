"""Main Streamlit page wiring: inputs, scraping, Gemini, JSON display."""

from __future__ import annotations

import json

import streamlit as st

from clarity.config import MIN_TEXT_CHARS, SHORT_TEXT_SCRAPE_WARNING
from clarity.credentials import resolve_api_key
from clarity.gemini import analyze_with_gemini
from clarity.model_json import extract_json
from clarity.scraping import clean_text, extract_homepage_text
from clarity.urls import is_valid_http_url, normalize_url
from clarity.ui.components import (
    display_analysis_results,
    dump_gemini_on_error,
    render_download_pdf_button,
    render_sidebar,
    warn_if_missing_api_key,
)
from clarity.ui.streamlit_helpers import streamlit_secrets_or_none


def _process_gemini_output(raw_gemini: str | None, source_label: str = "unknown") -> None:
    if raw_gemini is None or not raw_gemini.strip():
        return
    try:
        parsed = extract_json(raw_gemini)
        pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
        display_analysis_results(parsed, pretty)
        st.markdown("---")
        render_download_pdf_button(parsed, source_label, pretty)
    except (json.JSONDecodeError, ValueError):
        st.error("Could not parse JSON from the model response.")
        dump_gemini_on_error(raw_gemini, taller=True)


def _handle_analyze_website(normalized_url: str, *, api_key: str | None) -> None:
    if not normalized_url or not is_valid_http_url(normalized_url):
        st.warning("Enter a valid website URL (e.g. https://example.com).")
        return

    with st.spinner("Fetching and analyzing homepage…"):
        extracted = ""
        scrape_error: str | None = None
        try:
            extracted = extract_homepage_text(normalized_url)
        except BaseException as e:  # noqa: BLE001
            scrape_error = str(e)

        if scrape_error:
            st.warning(
                f"Scraping error: {scrape_error}. Try pasting the homepage text manually."
            )
            return

        if not extracted:
            st.warning(
                "Could not extract text automatically. Paste the homepage copy manually, "
                "or retry with another URL."
            )
            return

        if len(extracted) < MIN_TEXT_CHARS:
            st.warning(SHORT_TEXT_SCRAPE_WARNING)

        raw_gemini, err = analyze_with_gemini(
            extracted,
            f"scraped:{normalized_url}",
            api_key=api_key,
        )
        if err:
            st.error(err)
            dump_gemini_on_error(raw_gemini)
            return

        _process_gemini_output(raw_gemini, source_label=f"scraped:{normalized_url}")


def _handle_analyze_paste(text: str, *, api_key: str | None) -> None:
    cleaned = clean_text(text)
    if not cleaned:
        st.warning("Paste homepage text before analyzing.")
        return
    if len(cleaned) < MIN_TEXT_CHARS:
        st.warning(SHORT_TEXT_SCRAPE_WARNING)

    with st.spinner("Analyzing pasted homepage text…"):
        raw_gemini, err = analyze_with_gemini(cleaned, "manual_paste", api_key=api_key)
        if err:
            st.error(err)
            dump_gemini_on_error(raw_gemini)
            return

        _process_gemini_output(raw_gemini, source_label="manual_paste")


def run_app() -> None:
    st.set_page_config(page_title="Website Clarity Analyzer", layout="wide")
    st.title("Website Clarity Analyzer")
    st.markdown("Analyze how clearly a website communicates its business value.")

    api_key = resolve_api_key(streamlit_secrets_or_none())
    has_api_key = bool(api_key)

    render_sidebar(has_api_key)

    url_in = st.text_input("Website URL", placeholder="https://example.com")
    pasted = st.text_area(
        "Or paste homepage text manually",
        height=220,
        placeholder="Paste visible homepage copy…",
    )

    col1, col2, *_ = st.columns(4)
    with col1:
        analyze_site = st.button("Analyze Website", type="primary")
    with col2:
        analyze_paste = st.button("Analyze Pasted Text", type="secondary")

    triggered = analyze_site or analyze_paste
    warn_if_missing_api_key(triggered, has_api_key)

    if analyze_site:
        _handle_analyze_website(normalize_url(url_in), api_key=api_key)

    if analyze_paste:
        _handle_analyze_paste(pasted, api_key=api_key)
