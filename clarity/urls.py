"""URL normalization and validation helpers."""

from __future__ import annotations

from urllib.parse import urlparse, urlunparse


def normalize_url(raw: str) -> str:
    """Strip input and ensure http(s) scheme; return empty string if no host."""
    if not raw or not isinstance(raw, str):
        return ""
    url = raw.strip()
    if not url:
        return ""
    if not urlparse(url).scheme:
        url = "https://" + url
    parsed = urlparse(url)
    if not parsed.netloc:
        return ""
    return urlunparse(
        (
            (parsed.scheme or "https").lower(),
            parsed.netloc,
            parsed.path or "",
            parsed.params,
            parsed.query,
            parsed.fragment,
        )
    )


def is_valid_http_url(url: str) -> bool:
    """Return True only for http/https URLs with a netloc."""
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False
