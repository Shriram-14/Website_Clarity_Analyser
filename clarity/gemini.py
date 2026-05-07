"""Gemini client calls with model fallback and defensive response parsing."""

from __future__ import annotations

from google import genai

from clarity.config import MODEL_FALLBACK_CHAIN
from clarity.prompts import build_clarity_prompt


def _response_text(response: object) -> str:
    """Best-effort extraction of text from ``GenerateContentResponse``."""
    raw = getattr(response, "text", None) or ""
    if raw.strip():
        return raw
    candidates = getattr(response, "candidates", None)
    if not candidates:
        return ""
    cand = candidates[0]
    content = getattr(cand, "content", None)
    parts = getattr(content, "parts", None) if content else None
    if not parts:
        return ""
    texts: list[str] = []
    for p in parts:
        t = getattr(p, "text", None)
        if t:
            texts.append(t)
    return "".join(texts)


def analyze_with_gemini(
    homepage_text: str,
    source_label: str,
    *,
    api_key: str | None,
) -> tuple[str | None, str | None]:
    """
    Send homepage text to Gemini with the configured model fallback chain.

    Returns ``(raw_text, error_message)``. On success ``error_message`` is ``None``.
    """
    if not api_key:
        return None, "Add GEMINI_API_KEY to .env or Streamlit secrets."

    client = genai.Client(api_key=api_key)
    prompt = build_clarity_prompt(homepage_text, source_label)

    last_raw: str | None = None
    last_exc: BaseException | None = None

    for model_name in MODEL_FALLBACK_CHAIN:
        try:
            response = client.models.generate_content(model=model_name, contents=prompt)
            raw = _response_text(response)
            if raw.strip():
                return raw.strip(), None
            last_raw = raw or last_raw
        except BaseException as e:  # noqa: BLE001 — keep callers resilient across SDK changes
            last_exc = e

    detail = repr(last_exc) if last_exc else "empty response"
    return (
        last_raw.strip() if last_raw else None,
        f"Gemini request failed after trying all fallback models ({detail}).",
    )
