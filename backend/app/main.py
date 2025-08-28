from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal, Optional

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

class Question(BaseModel):
    type: Literal["multiple_choice", "rating", "open_text"]
    text: str
    options: Optional[List[str]] = None
    scale: Optional[int] = 5

class GenerateReq(BaseModel):
    description: str

@app.get("/health")
def healthz():
    return {"ok": True}

@app.post("/api/surveys/generate")
def generate(req: GenerateReq):
    desc = (req.description or "").strip()
    title = desc.title() or "Generated Survey"
    # simple stub output to unblock the frontend
    return {
        "id": 1,
        "title": title,
        "questions": [
            {"type": "rating", "text": "Overall satisfaction", "scale": 5},
            {
                "type": "multiple_choice",
                "text": "Which area needs the most improvement?",
                "options": ["Pricing", "Delivery speed", "Product quality", "Support"],
            },
            {"type": "open_text", "text": "What is one thing we should change first?"},
        ],
        "cached": False,
    }