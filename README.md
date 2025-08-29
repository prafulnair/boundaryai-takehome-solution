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


# BoundaryAI Take-Home — Minimal README

A small, production-shaped implementation of an **AI-powered survey generator** added to the provided React page.

- **Frontend:** Adds a **Generate Survey** button that prompts for a description, calls the backend, and auto-fills the form with rating / multiple-choice / open-text questions.
- **Backend (FastAPI, Python 3.11):** Exposes `POST /api/surveys/generate`, generates a survey (Google Gemini or deterministic fallback), **persists input/output in PostgreSQL**, and **returns cached results** for repeated prompts.

---

## Tech choices (why FastAPI)

- **FastAPI + Pydantic** for explicit request/response validation and a typed JSON API (less boilerplate than Flask for this use case).
- **SQLAlchemy + PostgreSQL** with a **unique constraint on `prompt`** to enforce cache-by-prompt and avoid race conditions.
- **Provider abstraction:** Gemini when configured; otherwise a small deterministic heuristic so the app runs without external keys.

---

## API

### Endpoint
`POST /api/surveys/generate`

### Request
```json
{ "description": "Customer satisfaction for an online store" }