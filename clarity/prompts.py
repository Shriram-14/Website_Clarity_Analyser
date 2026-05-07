"""Prompt templates for Gemini messaging-clarity evaluation."""


def build_clarity_prompt(homepage_text: str, source_label: str) -> str:
    """Produce the structured JSON-only analyst prompt for a homepage body."""
    return f"""You are a website messaging clarity analyst.

Analyze the homepage text and return ONLY valid JSON.

Evaluate:
1. What the business does
2. Who it serves
3. What value it provides
4. Whether the main message is specific or vague
5. Whether the next action for the visitor is clear

Return exactly this JSON structure:
{{
  "business_summary": "1-2 sentence summary of what the business does.",
  "clarity_score": 1,
  "score_reasoning": "Brief explanation of the score.",
  "suggestions": [
    "Specific actionable suggestion 1.",
    "Specific actionable suggestion 2.",
    "Specific actionable suggestion 3."
  ]
}}

Scoring rubric:
10 = Immediately clear, specific, compelling, and action-oriented.
8-9 = Clear overall, but minor specificity or CTA improvements needed.
6-7 = Understandable, but some vague language or missing audience/value details.
4-5 = Partially clear, but visitors may struggle to understand the offer quickly.
1-3 = Confusing, generic, or unclear what the business does.

Rules:
- Be specific and practical.
- Do not give generic advice.
- Suggestions must be directly related to the homepage text.
- If the homepage text is too thin, mention that in score_reasoning and suggestions.
- Return only JSON. No markdown. No extra commentary.

Homepage source: {source_label}

Homepage text:
\"\"\"
{homepage_text}
\"\"\"
"""
