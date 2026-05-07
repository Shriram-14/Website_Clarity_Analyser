# Website Clarity Analyzer

Simple **AI-powered homepage messaging analyzer** powered by Streamlit and Google Gemini. Paste a homepage URL or raw copy and receive a concise summary, clarity score (1–10), reasoning tuned to how specific the offer is, and concrete suggestions anchored in the extracted text.

## What it does

- **Fast extraction:** Pulls readable homepage text (trafilatura first, BeautifulSoup fallback) with a realistic browser User-Agent.
- **Manual override:** Paste text if scraping fails, is blocked, or returns too little copy.
- **Structured insight:** Gemini returns strict JSON summarizing positioning, evaluating clarity dimensions, and listing 2–3 practical improvements.

## Tech stack

- Python, Streamlit UI
- `requests` + `beautifulsoup4` for HTML fallback
- `trafilatura` for primary article/main-text extraction
- `google-genai` (Gemini API) with model fallback (`gemini-2.5-flash` → `gemini-2.0-flash` → `gemini-1.5-flash`)
- `python-dotenv` for local `.env` configuration

## Project layout

The code is split so **presentation** stays separate from **scraping**, **credential loading**, **prompting**, and **Gemini I/O**:

| Path | Responsibility |
|------|----------------|
| [`app.py`](app.py) | Thin Streamlit bootstrap (`run_app()` from [`clarity.ui`](clarity/ui/__init__.py)). |
| [`clarity/config.py`](clarity/config.py) | Thresholds (`MIN_TEXT_CHARS`, `MAX_TEXT_CHARS`), scrape headers, model chain, shared copy like thin-text warnings. |
| [`clarity/urls.py`](clarity/urls.py) | URL normalization and HTTP(S) validation. |
| [`clarity/scraping.py`](clarity/scraping.py) | Trafilatura + BeautifulSoup pipeline, whitespace cleanup, `extract_homepage_text`. |
| [`clarity/prompts.py`](clarity/prompts.py) | Single place for the analyst system prompt (`build_clarity_prompt`). |
| [`clarity/model_json.py`](clarity/model_json.py) | Strip markdown fences and `json.loads` model output (`extract_json`). |
| [`clarity/gemini.py`](clarity/gemini.py) | `genai.Client`, model fallback, response text shaping (`analyze_with_gemini`). |
| [`clarity/credentials.py`](clarity/credentials.py) | `resolve_api_key` from Streamlit secrets (optional) plus `.env` / OS env — no Streamlit import here. |
| [`clarity/ui/`](clarity/ui/) | Streamlit-only code: sidebar/metrics/layout (`components.py`), secrets shim (`streamlit_helpers.py`), page orchestration (`app.py`). |

This keeps **`clarity`** suitable for reuse (e.g. tests or a CLI) without pulling in Streamlit, except under `clarity/ui`.

## How to get a Gemini API key

1. Sign in at [Google AI Studio](https://aistudio.google.com/apikey) (Gemini Developer API).
2. Create an API key and restrict it appropriately for production use.

You can expose the key either as **`GEMINI_API_KEY`** or **`GOOGLE_API_KEY`** in `.env` or Streamlit secrets so the unified client can authenticate.

## How to run locally

```bash
python -m venv venv
source venv/bin/activate    # macOS/Linux
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set GEMINI_API_KEY

streamlit run app.py
```

**Windows (venv activation):**

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

### Optional: Streamlit secrets

Create `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your_key_here"
# or GOOGLE_API_KEY = "your_key_here"
```

## Approach

1. Normalize and validate URLs (`http`/`https`).
2. **Primary scrape:** `trafilatura.fetch_url` + `trafilatura.extract` for fast, readable main text.
3. **Fallback scrape:** GET with browser-like headers → BeautifulSoup strips `script`, `style`, `nav`, `footer`, `noscript`, `svg`; collects title, meta description (and OG description fallback), headings, paragraphs, buttons, and link text.
4. **Cleaning:** Normalize whitespace and cap inputs at ~10k characters before calling Gemini (keeps prompts reliable and avoids huge pages).
5. **Analysis:** Gemini must return JSON only (with client-side stripping of stray ``` fences if needed). Parsing errors surface the raw model output for troubleshooting.

### Scraping fallback explanation

Sites that aggressively rate-limit bots, rely on cookies, geoblocking, anti-bot tooling, WAF/CDN puzzles, **or ship most meaningful copy via client-side rendering** often yield sparse text from static HTML parsers. That is why manual paste remains a first-class path when extraction is noisy or `< 300` characters.

## Example output JSON

```json
{
  "business_summary": "ClearCal provides automated SOC2 readiness checks and evidence collection for SaaS teams so they ship enterprise deals faster.",
  "clarity_score": 8,
  "score_reasoning": "Hero states the product category and buyer (SOC2-focused SaaS) with concrete verbs; primary CTA is visible though proof points are sparse.",
  "suggestions": [
    "Lead the hero with a quantified outcome (e.g., 'cut audit prep weeks') tied to ClearCal rather than leaning on generic 'compliance made easy' phrases.",
    "Name the smallest viable customer segment explicitly (startup vs mid-market SaaS size or ARR band) above the fold so visitors self-qualify quickly.",
    "Move one concrete credibility signal (named customer logos, SOC2 posture, uptime) adjacent to the main CTA to reduce skepticism."
  ]
}
```

*(Illustrative; actual output depends on the homepage body you analyze.)*

## Limitations

- **No browser automation:** Cannot execute JavaScript, solve CAPTCHAs, or emulate logged-in dashboards.
- **Single page:** Only the fetched URL payload is analyzed, not nested marketing pages unless you paste combined copy.
- **Model variability:** Gemini answers can differ slightly between runs; guardrails rely on prompting plus JSON parsing—not hard schema enforcement beyond `json.loads`.
- **Thin text:** Boilerplate-heavy or legal-only pages receive lower-confidence scores by design because the evaluator must infer positioning from scarce signal.
