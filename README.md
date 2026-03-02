# LogSleuth - AI-Powered Log Anomaly Detector

**Assessment for Associate Software Engineer @ Better Software**
**Applicant:** Gaurav Katheriya


## Overview
LogSleuth is an internal developer tool that ingests raw, unstructured server logs, utilizes Groq's fast LPU inference (Llama-3) to identify anomalies, and outputs strict, actionable JSON (Severity, Root Cause, Suggested Fix). 

## Tech Stack
* **Backend:** Python + FastAPI 
* **Frontend:** React + Vite + Tailwind CSS
* **Database:** Neon Serverless PostgreSQL (via SQLAlchemy)
* **AI Inference:** Groq API (Llama3-8b-8192)

## Key Technical Decisions & Architecture

To align with the principles of clear boundaries, correctness, and simplicity, I made the following architectural choices:

**1. FastAPI over Flask (Interface Safety)**
FastAPI natively integrates with Pydantic. By defining `LogSubmissionRequest` and `GroqAnalysisResult` schemas, the application automatically rejects invalid client HTTP payloads and catches LLM hallucinations before they can corrupt the database.

**2. Serverless PostgreSQL over SQLite (Correctness & State Management)**
Instead of relying on ephemeral local SQLite files that wipe during container restarts, I integrated Neon Serverless Postgres. Data state (`pending` -> `success`/`failed`) is strictly managed and persists across deployments. 

**3. Decoupled AI Orchestration (Change Resilience)**
The API routing (`routes.py`) has no awareness of the LLM. All AI prompting, inference, and JSON validation is completely isolated in `app/services/groq_service.py`. If the team decides to migrate from Groq to OpenAI, the core API logic remains untouched.

**4. Explicit Observability**
The system does not silently fail. Pydantic validation errors, Groq rate limits, and JSON decode failures are caught, logged explicitly via standard Python logging, and return graceful HTTP 503 or 422 errors to the React client.

## Running Locally

**Backend:**
1. `cd backend`
2. `pip install -r requirements.txt`
3. Create a `.env` file with `DATABASE_URL` (Neon) and `GROQ_API_KEY`.
4. `uvicorn app.main:app --reload` (Runs on port 8000)

**Frontend:**
1. `cd frontend`
2. `npm install`
3. `npm run dev` (Runs on port 5173)

## Risks & Extension Approach
* **Risk (Rate Limiting):** Direct, synchronous calls to the Groq API tie up the HTTP request thread. If under heavy load, this could cause bottlenecks.
* **Extension:** For a production environment, I would decouple the ingestion from the inference using a message broker (e.g., Redis + Celery/RabbitMQ). The FastAPI endpoint would simply enqueue the raw log and immediately return a `202 Accepted` with a task ID, while workers process the Groq API calls asynchronously.
