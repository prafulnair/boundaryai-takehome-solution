# backend/app/providers/gemini_provider.py
import os, json, re
import google.generativeai as genai

def generate_survey_from_description(desc: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    create an AI-powered survey generator that transforms a user’s brief description into a fully structured questionnaire, covering diverse question types (multiple-choice, ratings, open-text, etc.) tailored to their needs
    You output JSON only. Build a survey for: "{desc}".
    Schema:
    {{
      "title": string,
      "questions": [
        {{"type":"rating","text":string,"scale":5}},
        {{"type":"multiple_choice","text":string,"options":[string,...]}},
        {{"type":"open_text","text":string}}
      ]
    }}
    3-6 questions total. JSON only.
    """
    resp = model.generate_content(prompt)
    text = resp.text.strip()
    json_str = re.search(r"\{.*\}\s*$", text, re.S).group(0)
    return json.loads(json_str)