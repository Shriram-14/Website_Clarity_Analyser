"""Homepage text extraction using trafilatura with a BeautifulSoup fallback."""

from __future__ import annotations

import re

import requests
import trafilatura
from bs4 import BeautifulSoup

from clarity.config import MAX_TEXT_CHARS, SCRAPING_HEADERS, REQUEST_TIMEOUT_SECONDS


def scrape_with_trafilatura(url: str) -> str | None:
    """Fetch and extract visible text via trafilatura (primary, fast path)."""
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return None
        text = trafilatura.extract(downloaded)
        return text.strip() if text else None
    except Exception:
        return None


def scrape_with_beautifulsoup(url: str) -> str | None:
    """Fallback: requests + BeautifulSoup with browser-like headers and noisy tags stripped."""
    try:
        resp = requests.get(url, headers=SCRAPING_HEADERS, timeout=REQUEST_TIMEOUT_SECONDS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "noscript", "svg"]):
            tag.decompose()

        chunks: list[str] = []

        if soup.title and soup.title.string:
            t = soup.title.string.strip()
            if t:
                chunks.append(t)

        md = soup.find("meta", attrs={"name": "description"})
        if md is None:
            md = next(
                (
                    m
                    for m in soup.find_all("meta")
                    if (m.get("name") or "").lower() == "description"
                ),
                None,
            )
        if md and md.get("content"):
            c = md["content"].strip()
            if c:
                chunks.append(c)
        og = soup.find("meta", attrs={"property": "og:description"})
        if og and og.get("content"):
            c = og["content"].strip()
            if c:
                chunks.append(c)

        for el in soup.find_all(["h1", "h2", "h3"]):
            t = el.get_text(separator=" ", strip=True)
            if t:
                chunks.append(t)
        for el in soup.find_all(["p", "button", "a"]):
            t = el.get_text(separator=" ", strip=True)
            if t:
                chunks.append(t)

        body = "\n".join(chunks).strip()
        return body if body else None
    except Exception:
        return None


def clean_text(text: str) -> str:
    """Normalize whitespace and cap length before sending content to Gemini."""
    if not text:
        return ""
    s = text.replace("\xa0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s).strip()
    if len(s) > MAX_TEXT_CHARS:
        s = s[:MAX_TEXT_CHARS]
    return s


def extract_homepage_text(url: str) -> str:
    """Try trafilatura; fall back to BeautifulSoup; return cleaned text or empty."""
    text = scrape_with_trafilatura(url)
    if text:
        cleaned = clean_text(text)
        if cleaned:
            return cleaned
    text = scrape_with_beautifulsoup(url)
    if not text:
        return ""
    return clean_text(text)
