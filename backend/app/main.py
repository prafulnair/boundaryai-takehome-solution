from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
import os
from .db import engine, SessionLocal
from .models import Base, SurveyRow
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv; load_dotenv()  # pip install python-dotenv
from .providers.gemini_provider import generate_survey_from_description as gemini_generate


def select_generator():
    return gemini_generate if os.getenv("AI_PROVIDER","heuristic").lower()=="gemini" else heuristic_generate

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# create tables on startup (simple for take-home)
Base.metadata.create_all(bind=engine)

QuestionType = Literal["multiple_choice", "rating", "open_text"]

class Question(BaseModel):
    type: QuestionType
    text: str
    options: Optional[List[str]] = None
    scale: Optional[int] = Field(default=5, ge=2, le=10)

class GenerateReq(BaseModel):
    description: str

class GenerateResp(BaseModel):
    id: int
    title: str
    questions: List[Question]
    cached: bool = False

def _normalize_payload(payload: dict) -> dict:
    """Coerce provider output to {title, questions[]} with our allowed types."""
    def norm_type(t: str) -> str:
        t = (t or "").strip().lower().replace("-", "_").replace(" ", "_")
        if t in {"multiple_choice", "multiplechoice", "multi_choice"}:
            return "multiple_choice"
        if t in {"rating", "likert", "scale"}:
            return "rating"
        if t in {"open_text", "openended", "open_end", "text"}:
            return "open_text"
        return "open_text"

    title = (payload or {}).get("title") or "Generated Survey"
    out_qs: list[dict] = []
    for q in (payload or {}).get("questions", []):
        qt = norm_type(q.get("type"))
        item = {"type": qt, "text": (q.get("text") or "").strip()}
        if qt == "rating":
            try:
                item["scale"] = max(2, min(int(q.get("scale") or 5), 10))
            except Exception:
                item["scale"] = 5
        if qt == "multiple_choice":
            opts = q.get("options") or []
            item["options"] = [str(o) for o in opts if str(o).strip()][:12]  # small guard
        out_qs.append(item)
    # Ensure at least one question
    if not out_qs:
        out_qs = [{"type": "open_text", "text": "Share your thoughts"}]
    return {"title": title, "questions": out_qs}

@app.get("/health")
def health():
    return {"ok": True}

def heuristic_generate(desc: str) -> dict:
    topic = (desc or "").strip().lower()
    title = (desc or "Generated Survey").title()
    questions: List[dict] = [
        {"type": "rating", "text": "Overall satisfaction", "scale": 5}
    ]
    if any(k in topic for k in ["store", "shop", "ecommerce", "cart"]):
        questions.append({
            "type": "multiple_choice",
            "text": "Which area needs the most improvement?",
            "options": ["Pricing", "Delivery speed", "Product quality", "Support"]
        })
    else:
        questions.append({
            "type": "multiple_choice",
            "text": "Where did you first hear about us?",
            "options": ["Search", "Friend", "Social Media", "Other"]
        })
    questions.append({"type": "open_text", "text": "What is one thing we should change first?"})
    return {"title": title, "questions": questions}

@app.post("/api/surveys/generate", response_model=GenerateResp)
def generate(req: GenerateReq):
    prompt = (req.description or "").strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="description is required")

    with SessionLocal() as session:
        # Cache check
        existing = session.execute(select(SurveyRow).where(SurveyRow.prompt == prompt)).scalars().first()
        if existing:
            payload = existing.payload
            return {
                "id": existing.id,
                "title": payload.get("title", existing.title),
                "questions": payload.get("questions", []),
                "cached": True,
            }

        # Generate (heuristic for now)
        payload = heuristic_generate(prompt)
        # Validate minimally via Pydantic to catch mistakes
        _validated = GenerateResp(id=0, title=payload["title"], questions=[Question(**q) for q in payload["questions"]], cached=False)

        row = SurveyRow(prompt=prompt, title=payload["title"], payload=payload, model_name="heuristic")
        session.add(row)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            existing = session.execute(select(SurveyRow).where(SurveyRow.prompt == prompt)).scalars().first()
            if existing:
                payload = existing.payload
                return {
                    "id": existing.id,
                    "title": payload.get("title", existing.title),
                    "questions": payload.get("questions", []),
                    "cached": True,
                }
            raise
        session.refresh(row)
        return {"id": row.id, "title": payload["title"], "questions": payload["questions"], "cached": False}