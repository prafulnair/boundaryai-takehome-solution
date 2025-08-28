# backend/app/providers/gemini_provider.py
import os, json
import google.generativeai as genai

_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

def generate_survey_from_description(desc: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")

    genai.configure(api_key=api_key)

    # Force JSON-only output to avoid parsing issues
    model = genai.GenerativeModel(
        model_name=_MODEL,
        generation_config={
            "response_mime_type": "application/json",
            # optional: tighten length if you want:
            # "max_output_tokens": 2048,
        }
        # You can also relax safety if it blocks harmless prompts:
        #, safety_settings={"HARASSMENT": "block_none", "HATE_SPEECH": "block_none", ...}
    )

    prompt = {
        "instruction": "You are an API. Return JSON only — no markdown, no prose.",
        "constraints": [
            "3 to 6 questions total",
            "At least one rating, one multiple_choice, one open_text",
            "Keep language neutral and concise",
        ],
        "schema": {
            "title": "string",
            "questions": [
                {
                    "type": "rating | multiple_choice | open_text",
                    "text": "string",
                    "scale": "int (2..10, only for rating)",
                    "options": "[string, ...] (only for multiple_choice)"
                }
            ]
        },
        "description": desc.strip(),
    }

    # Ask explicitly for the target schema
    user = f"""
Create a survey for: "{prompt['description']}"
Return JSON with this shape:
{{
  "title": string,
  "questions": [
    {{"type":"rating","text":string,"scale":5}},
    {{"type":"multiple_choice","text":string,"options":[string,...]}},
    {{"type":"open_text","text":string}}
  ]
}}
Rules: 3–6 total questions. JSON ONLY.
"""

    resp = model.generate_content(user)

    # Surface blocking or empty responses as clear errors
    pf = getattr(resp, "prompt_feedback", None)
    if pf and getattr(pf, "block_reason", None):
        raise RuntimeError(f"blocked_by_safety: {pf.block_reason}")

    text = (getattr(resp, "text", None) or "").strip()
    if not text:
        # Some SDK versions use candidates/parts; try to fetch text defensively
        try:
            cand = resp.candidates[0]
            parts = getattr(cand, "content", cand).parts
            text = "".join(getattr(p, "text", "") for p in parts).strip()
        except Exception:
            pass

    if not text:
        raise RuntimeError("empty_response_from_gemini")

    try:
        data = json.loads(text)  # response_mime_type=json should make this clean
    except json.JSONDecodeError as e:
        raise RuntimeError(f"invalid_json_from_gemini: {e}")

    # Minimal shape sanity; let main.py normalize further
    if "title" not in data or "questions" not in data:
        raise RuntimeError("missing_keys_in_gemini_json")

    return data