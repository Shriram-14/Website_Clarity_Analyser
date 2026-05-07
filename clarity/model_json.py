"""Parse JSON from Gemini text output while tolerating stray markdown fences."""

from __future__ import annotations

import json
import re


def extract_json(text: str) -> dict:
    """Strip accidental ``` fences, then ``json.loads`` the payload."""
    if not text or not text.strip():
        raise ValueError("Empty model response.")

    cleaned = text.strip()
    fence = re.match(r"^```(?:json)?\s*\n?(.*)", cleaned, flags=re.DOTALL | re.IGNORECASE)
    if fence:
        cleaned = fence.group(1)
    cleaned = re.sub(r"\s*```\s*$", "", cleaned, flags=re.DOTALL)

    return json.loads(cleaned.strip())
