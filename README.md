# Website Clarity Analyzer

An AI-powered homepage messaging analyzer built with **Python**, **Streamlit**, and **Google Gemini**. Enter a URL or paste homepage copy and receive a structured report: a plain-English business summary, a clarity score from 1 to 10, reasoning behind that score, and concrete improvement suggestions — all exportable as a styled **PDF report** via ReportLab.

---

## Table of Contents

1. [What It Does](#what-it-does)
2. [Tech Stack](#tech-stack)
3. [Prerequisites](#prerequisites)
4. [Getting a Gemini API Key](#getting-a-gemini-api-key)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Running the App](#running-the-app)
8. [Using the App](#using-the-app)
9. [PDF Report](#pdf-report)
10. [Project Layout](#project-layout)
11. [Architecture & Data Flow](#architecture--data-flow)
12. [Scraping Strategy](#scraping-strategy)
13. [Gemini Integration](#gemini-integration)
14. [API Key Resolution Logic](#api-key-resolution-logic)
15. [Example Gemini Output JSON](#example-gemini-output-json)
16. [Scoring Rubric](#scoring-rubric)
17. [Known Limitations](#known-limitations)
18. [Troubleshooting](#troubleshooting)

---

## What It Does

| Capability | Detail |
|---|---|
| URL scraping | Fetches a homepage and extracts readable text (no JavaScript required) |
| Manual paste | Accept raw copy if scraping is blocked or returns too little text |
| AI analysis | Sends text to Google Gemini and asks three questions: what does this business do, for whom, and what should a visitor do next? |
| Structured output | Returns a strict JSON object with `business_summary`, `clarity_score`, `score_reasoning`, and `suggestions` |
| PDF export | Renders the full analysis to a professionally styled, downloadable PDF |

---

## Tech Stack

| Package | Purpose |
|---|---|
| `streamlit` | Web UI and interactive widgets |
| `trafilatura` | Primary homepage text extraction (main-content focused) |
| `requests` + `beautifulsoup4` | Fallback HTML scraper |
| `google-genai` | Google Gemini API client (`genai.Client`) |
| `python-dotenv` | Loads `.env` files for local development |
| `reportlab` | Generates the styled PDF analysis report |

Python version: **3.8 or later** (tested on 3.11 and 3.13).

---

## Prerequisites

- Python 3.8+ installed and on your `PATH`
- A Google Gemini API key (free tier available — see below)
- `pip` or a package manager that can read `requirements.txt`
- Git (optional, for cloning)

---

## Getting a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey) and sign in with a Google account.
2. Click **Create API key** and copy the generated key.
3. Optionally, add API restrictions (HTTP referrer, IP, etc.) if you plan to use the key in a shared environment.

The key can be named either `GEMINI_API_KEY` or `GOOGLE_API_KEY` — the app accepts both.

---

## Installation

### macOS / Linux

```bash
# 1. Clone or download the project
git clone <repo-url>
cd website-clarity-analyzer

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install all dependencies
pip install -r requirements.txt
```

### Windows

```bat
:: 1. Enter the project directory
cd website-clarity-analyzer

:: 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate

:: 3. Install all dependencies
pip install -r requirements.txt
```

---

## Configuration

The app needs exactly one thing to work: a Gemini API key. There are three ways to supply it, checked in this order:

### Option A — `.env` file (recommended for local development)

```bash
cp .env.example .env
```

Open `.env` and set your key:

```dotenv
GEMINI_API_KEY=your_key_here
```

The file is already listed in `.gitignore` so it will never be committed.

### Option B — Streamlit secrets (recommended for Streamlit Cloud deployments)

Create the file `.streamlit/secrets.toml` (also in `.gitignore`):

```toml
GEMINI_API_KEY = "your_key_here"
# Alternatively:
# GOOGLE_API_KEY = "your_key_here"
```

On **Streamlit Community Cloud**, paste this key-value pair into the app's **Secrets** panel in the dashboard instead of creating the file manually.

### Option C — Environment variable

Export the variable in your shell before running:

```bash
export GEMINI_API_KEY=your_key_here
streamlit run app.py
```

---

## Running the App

With the virtual environment active and a key configured:

```bash
streamlit run app.py
```

Streamlit will print a local URL (default `http://localhost:8501`). Open it in any browser.

---

## Using the App

### Analyzing a Website URL

1. Paste a full URL (e.g. `https://example.com`) into the **Website URL** field.
2. Click **Analyze Website**.
3. The app fetches the page, extracts text, sends it to Gemini, and renders results.

> If the site blocks scraping or relies on JavaScript for its main content, the extracted text may be too short (< 300 characters). The app warns you and suggests the manual paste path.

### Analyzing Pasted Text

1. Copy the visible text from a homepage (use browser → Select All → Copy, or copy from the browser's reader view).
2. Paste it into the **Or paste homepage text manually** text area.
3. Click **Analyze Pasted Text**.

### Reading the Results

After a successful analysis the page displays:

| Section | What it means |
|---|---|
| **Business Summary** | A one-to-two sentence plain-English description of what the business does, who it serves, and what the primary action is |
| **Clarity Score** | A number from 1 (very confusing) to 10 (immediately clear and compelling) |
| **Score Reasoning** | Gemini's explanation of why the page earned that score, referencing specific copy from the page |
| **Suggestions** | Two to four concrete, actionable improvements grounded in the actual text |
| **Raw JSON** | The exact JSON object returned by Gemini, useful for debugging or programmatic use |

### Sidebar

The sidebar always shows:
- Step-by-step instructions
- API key status (configured / missing)
- The full scoring rubric so you can interpret the score at a glance

---

## PDF Report

After every successful analysis a **Download PDF Report** button appears below the results. Clicking it generates and downloads a fully styled PDF named `clarity_report_<UTC-timestamp>.pdf`.

### What the PDF contains

| Section | Description |
|---|---|
| **Header banner** | Dark branded header with report title and subtitle |
| **Meta row** | Source (URL or "manual\_paste") and UTC generation timestamp |
| **Clarity Score badge** | Large coloured block — green for 8–10 (Strong), amber for 5–7 (Moderate), red for 1–4 (Needs Work) — with the numeric score and band label |
| **Business Summary** | Full summary paragraph |
| **Score Reasoning** | Full reasoning paragraph |
| **Suggestions** | Bulleted list of all improvement suggestions |
| **Raw Gemini JSON** | Monospaced, light-background code block with hard-wrapped lines |
| **Footer** | Disclaimer noting the report was auto-generated |

The PDF is built entirely in memory (no temp files written to disk) and streamed directly to the browser.

---

## Project Layout

```
website-clarity-analyzer/
├── app.py                        # Entry point — calls run_app() from clarity.ui
├── requirements.txt              # All Python dependencies
├── README.md                     # This file
├── .env.example                  # Copy to .env and fill in your key
├── .gitignore                    # Ignores .env, venv/, __pycache__/, secrets.toml
│
└── clarity/
    ├── __init__.py
    ├── config.py                 # Shared constants: thresholds, headers, model chain, warning strings
    ├── urls.py                   # normalize_url(), is_valid_http_url()
    ├── scraping.py               # extract_homepage_text(), scrape_with_trafilatura(),
    │                             #   scrape_with_beautifulsoup(), clean_text()
    ├── prompts.py                # build_clarity_prompt(homepage_text, source_label)
    ├── model_json.py             # extract_json() — strips ``` fences, then json.loads
    ├── gemini.py                 # analyze_with_gemini() — client, model fallback, response shaping
    ├── credentials.py            # resolve_api_key() — Streamlit secrets → .env → env var
    ├── report.py                 # generate_pdf_report() — full ReportLab PDF builder
    │
    └── ui/
        ├── __init__.py           # Exports run_app
        ├── streamlit_helpers.py  # streamlit_secrets_or_none() — safe secrets dict wrapper
        ├── components.py         # render_sidebar(), display_analysis_results(),
        │                         #   render_download_pdf_button(), warn_if_missing_api_key(),
        │                         #   dump_gemini_on_error()
        └── app.py                # run_app() — full page wiring, inputs, spinner, orchestration
```

### Design principle

Everything under `clarity/` **except `clarity/ui/`** is intentionally free of Streamlit imports. This means:

- `clarity/scraping.py`, `clarity/gemini.py`, `clarity/report.py`, etc. can be imported and called from a CLI script, a test suite, or any other Python context without pulling in Streamlit.
- `clarity/ui/` is the only layer that knows about `st.*`.

---

## Architecture & Data Flow

```
User input (URL or pasted text)
        │
        ▼
  clarity/urls.py           normalize_url(), is_valid_http_url()
        │
        ▼
  clarity/scraping.py       extract_homepage_text(url)
    ├── trafilatura.fetch_url + trafilatura.extract   [primary]
    └── requests.get + BeautifulSoup                  [fallback]
        │   strip: script, style, nav, footer, noscript, svg
        │   collect: title, meta description, og:description,
        │            h1–h3, p, button, a
        │
        ▼
  clarity/scraping.py       clean_text()
    └── normalize whitespace, cap at MAX_TEXT_CHARS (10,000 chars)
        │
        ▼
  clarity/prompts.py        build_clarity_prompt(text, source_label)
        │
        ▼
  clarity/gemini.py         analyze_with_gemini(text, source_label, api_key=...)
    ├── genai.Client(api_key=...)
    └── model fallback: gemini-2.5-flash → gemini-2.0-flash → gemini-1.5-flash
        │
        ▼
  clarity/model_json.py     extract_json(raw_text)
    └── strip ``` fences → json.loads
        │
        ▼
  clarity/ui/components.py  display_analysis_results(parsed, pretty_json)
        │
        ▼
  clarity/report.py         generate_pdf_report(parsed, source_label, raw_json)
        │
        ▼
  st.download_button        streams PDF bytes to browser
```

---

## Scraping Strategy

`extract_homepage_text(url)` tries two methods in sequence:

### 1. Trafilatura (primary)

Uses `trafilatura.fetch_url` followed by `trafilatura.extract`. Trafilatura is optimized for pulling the main article/body text from web pages while ignoring boilerplate. It is fast and produces clean output for most standard marketing sites.

If the result is empty or shorter than `MIN_TEXT_CHARS` (300 characters), the app falls through to the BeautifulSoup fallback.

### 2. BeautifulSoup (fallback)

Issues a `requests.get` with a realistic browser `User-Agent` and then:

1. Removes `<script>`, `<style>`, `<nav>`, `<footer>`, `<noscript>`, `<svg>` entirely.
2. Collects text from:
   - `<title>`
   - `<meta name="description">` (case-insensitive attribute scan)
   - `<meta property="og:description">`
   - `<h1>`, `<h2>`, `<h3>`
   - `<p>`
   - `<button>`
   - `<a>` (link text)

### 3. Text cleaning

`clean_text(text)` normalizes whitespace (collapses runs of spaces, tabs, newlines) and truncates the result to `MAX_TEXT_CHARS` (10,000 characters) before it is sent to Gemini. This keeps prompts predictable and avoids unexpected token costs on very large pages.

---

## Gemini Integration

### Model fallback chain

The app tries models in this order until one returns a non-empty response:

```
gemini-2.5-flash  →  gemini-2.0-flash  →  gemini-1.5-flash
```

Defined in `clarity/config.py` as `MODEL_FALLBACK_CHAIN`. If all three fail, a descriptive error is shown with the raw model output for debugging.

### Prompt shape

The prompt in `clarity/prompts.py` instructs Gemini to act as a messaging analyst and return **only JSON** with this exact shape:

```json
{
  "business_summary": "string",
  "clarity_score": 1,
  "score_reasoning": "string",
  "suggestions": ["...", "...", "..."]
}
```

### Response parsing

`clarity/model_json.py` strips any accidental markdown code fences (` ```json ... ``` `) that Gemini sometimes adds, then calls `json.loads`. If parsing fails, the app shows an error and exposes the raw text in a text area so you can inspect or copy it.

---

## API Key Resolution Logic

Implemented in `clarity/credentials.py` as `resolve_api_key(secrets)`:

```
1. If a secrets dict is passed (from Streamlit):
       check GOOGLE_API_KEY, then GEMINI_API_KEY in that dict.
2. Otherwise (None passed):
       call load_dotenv() to load .env into the environment.
       check GOOGLE_API_KEY, then GEMINI_API_KEY from os.environ.
```

**Why both key names?** Google has used both `GOOGLE_API_KEY` and `GEMINI_API_KEY` in different documentation versions. The app accepts either so you do not need to rename an existing key.

**Streamlit secrets safety:** `clarity/ui/streamlit_helpers.py` wraps the `st.secrets` iteration in a `try/except StreamlitSecretNotFoundError` so that `.env`-only setups (no `secrets.toml`) do not crash on startup.

---

## Example Gemini Output JSON

```json
{
  "business_summary": "ClearCal provides automated SOC 2 readiness checks and evidence collection for SaaS teams so they can close enterprise deals faster without hiring a dedicated compliance manager.",
  "clarity_score": 8,
  "score_reasoning": "The hero clearly states the product category (SOC 2 automation) and buyer (SaaS teams), and the primary CTA is above the fold. Score falls short of 9 because proof points are sparse and the value proposition relies on implicit urgency rather than a quantified outcome.",
  "suggestions": [
    "Lead the hero with a quantified outcome tied to ClearCal — e.g. 'Cut SOC 2 audit prep from 3 months to 3 weeks' — rather than the generic phrase 'compliance made easy'.",
    "Name the smallest viable customer segment explicitly (startup vs mid-market SaaS, ARR band, or team size) so visitors self-qualify above the fold.",
    "Move one concrete credibility signal — named customer logos, audit pass rate, or uptime figure — adjacent to the main CTA to reduce first-visit skepticism."
  ]
}
```

*(Illustrative. Actual output depends entirely on the homepage text analyzed.)*

---

## Scoring Rubric

| Score | Interpretation |
|---|---|
| **10** | Immediately clear, highly specific, compelling value proposition, strong action-oriented CTA. |
| **8–9** | Clear with only minor gaps in specificity, audience targeting, or CTA strength. |
| **6–7** | Understandable but contains vague language, missing detail, or a weak call to action. |
| **4–5** | Partially clear — the offer may not land quickly; visitors likely need to dig deeper. |
| **1–3** | Confusing or very unclear about what the business does, who it serves, or what to do next. |

---

## Known Limitations

| Limitation | Why |
|---|---|
| No JavaScript rendering | The app uses static HTTP requests only. Pages that load their main marketing copy via React, Vue, Angular, or other client-side frameworks often yield sparse text. Use the manual paste path for these sites. |
| Single page only | Only the directly fetched URL is analyzed. Sub-pages (pricing, about, features) are not crawled unless you paste their combined text manually. |
| Model variability | Gemini is a generative model. Scores and suggestions can vary slightly between runs on identical input. |
| No schema enforcement | JSON parsing relies on prompting and `json.loads`. There is no JSON Schema or Pydantic validation of the Gemini response. If Gemini returns a malformed structure, the raw text is shown. |
| Thin text pages | Pages with fewer than 300 characters of extractable text receive a low-confidence analysis by design. A warning is shown in the UI and included in the context sent to Gemini. |
| Rate limits | The free Gemini tier has per-minute and per-day quotas. If you hit them, the app will show an error from the fallback chain. Wait a moment and retry. |

---

## Troubleshooting

**"No key found" warning in the sidebar**

The app cannot find a Gemini API key. Check:
- `.env` exists and contains `GEMINI_API_KEY=...` (no quotes, no spaces around `=`)
- The virtual environment is active when running `streamlit run app.py`
- If using Streamlit Cloud, the secret is set in the app's dashboard under **Settings → Secrets**

**"Could not extract text automatically"**

The scraper returned an empty result. Try:
- Pasting the homepage text manually into the text area
- Checking that the URL is reachable in your browser
- Trying a slightly different URL format (with or without `www`)

**"Could not parse JSON from the model response"**

Gemini returned text that could not be parsed as JSON. The raw response is shown below the error. This is rare but can happen when the model is overloaded or the input text is very unusual. Retry the analysis.

**PDF download button is missing**

The button only appears after a successful analysis that produced valid JSON. If the analysis shows an error, fix the underlying issue (API key, scraping, JSON parse) first.

**`ModuleNotFoundError: No module named 'reportlab'`**

Run `pip install -r requirements.txt` again inside your active virtual environment. ReportLab was added in the latest version of `requirements.txt`.
