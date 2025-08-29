<!-- # Backend Task

This task is designed to evaluate your backend skills, API design, code quality, architecture, and creativity. The goal is to augment the provided isolated frontend page with a fully working survey-generation feature.

To do so you are asked to create an AI-powered survey generator that transforms a user’s brief description into a fully structured questionnaire, covering diverse question types (multiple-choice, ratings, open-text, etc.) tailored to their needs.

## Description

You have been given an isolated version of one page of our frontend (React + TypeScript): [https://github.com/BoundaryAIRecruitment/BackendTask](https://github.com/BoundaryAIRecruitment/BackendTask)

Your job is to:

* **Add a “Generate Survey” button to the page:**

  * When clicked, it should prompt the user to enter a short survey description (e.g. “Customer satisfaction for an online store”).
  * Once submitted, the frontend should call your new backend endpoint.

* **Implement the backend (using Flask or FastAPI, your choice):**

  * **Route(s):**

    * A POST endpoint (e.g. `/api/surveys/generate`) that accepts the user’s description.
  * **Logic & Integration:**

    * Use the OpenAI API, or another LLM of your choice to generate a structured survey.
    * It is recommended that the output be JSON-structured (e.g. `{ "title": "...", "questions": [ { "type": "...", "text": "..." }, … ] }`).
  * **Storage:** save generated surveys for repeated prompts.

    * Save the input and output in a PostGreSQL database; if an input is the same, you should fetch it instead of generate it.
  * **Auto-fill:**

    * Return the generated JSON so the frontend can render the new survey form automatically.

## Tech Stack

* **Language:** Python (3.11)
* **Framework:** Flask or FastAPI
* **AI Integration:** OpenAI API (or equivalent LLM)

## What We are Evaluating

* **Architecture & Design**

  * Logical separation of concerns (routes, services, models), clear dependency injection or config management.
* **Code Quality**

  * Clean, modular, well-documented code following best practices and style guides.
* **API Design**

  * RESTful principles, clear request/response schemas, proper status codes and error messages.
* **Integration & Robustness**

  * Correct handling of API keys, timeouts, retries, input validation, and error cases.
* **Performance & Security**

  * Efficient request handling, minimal cold-start overhead, sanitization of inputs.
* **Documentation**

  * Clear README explaining setup, env vars, how to run, and any design decisions.

## Submission

Provide one of the following:

* A GitHub repository (with public or private access) or a ZIP archive containing your code.
* (Optional) A deployed version of your backend (e.g. on Heroku, Vercel Functions, or similar) with URL.

Include a brief README that covers:

* Tech choices (why Flask vs. FastAPI, any libraries you picked)
* Setup & Run instructions (install, env vars, start server)
* Areas of focus (What did you implement that other candidates might not have?)

## Bonus Points

* **Dockerization:** supply a Dockerfile and easy docker-compose setup.
* **Testing:** Unit and/or integration tests covering core functionality.
* **Authentication:** simple token check on your API.
* **Rate limiting:** prevent abuse of the generation endpoint.
* **Security:**

Feel free to innovate beyond the spec. If you see an opportunity to improve UX or backend architecture, show us. Good luck! -->


BoundaryAI Take-Home — Minimal README

A small, production-shaped implementation of an AI-powered survey generator added to the provided React page.
	•	Frontend: adds a Generate Survey button that prompts for a description, calls the backend, and auto-fills the form with rating / multiple-choice / open-text questions.
	•	Backend (FastAPI, Python 3.11): exposes POST /api/surveys/generate, generates a survey (Google Gemini or deterministic fallback), persists input/output in PostgreSQL, and returns cached results for repeated prompts.

⸻

Tech choices (why FastAPI)
	•	FastAPI + Pydantic for explicit request/response validation and a clean, typed JSON API (less boilerplate than Flask for this use case).
	•	SQLAlchemy + Postgres with a unique constraint on prompt to enforce cache-by-prompt and avoid race conditions.
	•	Provider abstraction: Gemini when configured; otherwise a small deterministic heuristic so the app runs without external keys.

⸻

API

Endpoint
POST /api/surveys/generate

Request

{ "description": "Customer satisfaction for an online store" }

Response (example)

{
  "id": 42,
  "title": "Customer Satisfaction For An Online Store",
  "questions": [
    { "type": "rating", "text": "Overall satisfaction", "scale": 5 },
    {
      "type": "multiple_choice",
      "text": "Which area needs the most improvement?",
      "options": ["Pricing","Delivery speed","Product quality","Support"]
    },
    { "type": "open_text", "text": "What should we change first?" }
  ],
  "cached": false
}

Behavior
	•	Same description → returns stored survey with cached: true and the same id.
	•	Response header X-Model-Provider: gemini|heuristic.
	•	Optional ?force=true (for testing) bypasses cache and overwrites the stored row.

Status codes
	•	200 OK, 400 empty/missing description, 502 provider failure (only when a provider is forced).

⸻

Storage model (PostgreSQL)

Table surveys:
	•	id (PK), prompt (UNIQUE), title, payload (JSONB), model_name (gemini|heuristic), created_at (timestamptz).
Full JSON is stored to stay flexible as question types evolve.

⸻

Setup & run

1) Database (Docker)

docker run --name surveys \
  -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=surveys \
  -p 5433:5432 -d postgres:16

2) Backend (FastAPI)

python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt

# Env vars
export DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5433/surveys
# Optional AI
export AI_PROVIDER=gemini
export GEMINI_API_KEY='your-gemini-key'

# Run API
uvicorn app.main:app --app-dir backend --reload
# Health: GET http://localhost:8000/health -> {"ok": true}

3) Frontend

cd frontend
npm install
# frontend/.env.local
# REACT_APP_API_BASE=http://localhost:8000
npm start


⸻

Quick test

# new prompt -> cached:false
curl -X POST http://localhost:8000/api/surveys/generate \
  -H "Content-Type: application/json" \
  -d '{"description":"New user onboarding feedback for a B2B analytics dashboard (v2)"}'

# repeat same prompt -> cached:true, same id
curl -X POST http://localhost:8000/api/surveys/generate \
  -H "Content-Type: application/json" \
  -d '{"description":"New user onboarding feedback for a B2B analytics dashboard (v2)"}'

# inspect rows
docker exec -it surveys psql -U postgres -d surveys \
  -c "SELECT id, prompt, model_name, created_at FROM surveys ORDER BY id DESC LIMIT 5;"


⸻

Areas of focus
	•	Provider-agnostic design with a small normalization step and visible X-Model-Provider.
	•	DB-enforced cache (prompt unique) to avoid duplicates and races.
	•	Strict schema validation (Pydantic) before persistence.
	•	Clear failure modes (400/502) for straightforward testing.
	•	Small, readable code with separation of concerns (route / provider / persistence).

⸻

Security & ops notes
	•	Secrets via environment variables; .env files are git-ignored. The Gemini key is server-side only.
	•	CORS open for local dev; restrict origins in production.
	•	Stateless service; cache-by-prompt reduces repeated model calls.

⸻

Bonus (future work)
	•	Auth: simple bearer token on /api/*.
	•	Rate limiting: token bucket on /api/surveys/generate.
	•	Tests: pytest + FastAPI TestClient + temporary DB.
	•	Compose: one-command spin-up for API + DB + frontend.

⸻

Transparency on AI usage

No AI-enabled IDEs or code autocompletion (e.g., Copilot) were used. After the initial working version, an AI assistant was consulted for review and debugging (schema/API validation, configuration checks, and targeted error triage). The backend integrates Gemini when configured; otherwise, it uses a small deterministic heuristic so the system remains usable without external keys.