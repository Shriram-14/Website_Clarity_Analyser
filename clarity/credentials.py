"""Resolve Gemini / Google GenAI credentials from Streamlit secrets or environment."""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any

from dotenv import load_dotenv


def resolve_api_key(secrets: Mapping[str, Any] | None) -> str | None:
    """
    Prefer ``GOOGLE_API_KEY`` then ``GEMINI_API_KEY`` in a secrets mapping.

    The UI passes a **plain dict** from ``streamlit_helpers`` when ``secrets.toml`` exists;
    otherwise ``secrets`` should be ``None`` so lookups never touch Streamlit lazy parsing.

    Fallback: ``load_dotenv`` then identical environment variables.
    """
    if secrets is not None:
        for name in ("GOOGLE_API_KEY", "GEMINI_API_KEY"):
            if name in secrets and secrets[name]:
                found = str(secrets[name]).strip()
                if found:
                    return found

    load_dotenv()
    env_g = os.getenv("GOOGLE_API_KEY", "").strip()
    env_m = os.getenv("GEMINI_API_KEY", "").strip()
    return env_g or env_m or None
