"""Central constants and scrape / model configuration."""

MIN_TEXT_CHARS = 300
MAX_TEXT_CHARS = 10000

SCRAPING_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

REQUEST_TIMEOUT_SECONDS = 15

MODEL_FALLBACK_CHAIN: tuple[str, ...] = (
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
)

SHORT_TEXT_SCRAPE_WARNING = (
    "Could not extract enough text. This site may block scraping or rely heavily "
    "on JavaScript. Please paste homepage text manually."
)

MISSING_API_KEY_HINT = "Add GEMINI_API_KEY to .env or Streamlit secrets."
