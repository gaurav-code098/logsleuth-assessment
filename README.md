# LogSleuth 🕵️‍♂️ - AI-Powered Log Anomaly Detector

**Assessment Submission for Better Software - Associate Software Engineer**
**Candidate:** Gaurav 

---


## 🎯 Problem Statement
Modern applications generate thousands of logs, making it difficult for developers and sysadmins to quickly identify the root cause of failures. LogSleuth is a lightweight, AI-powered log anomaly detector. Users can paste or upload raw server logs (stack traces, server errors, DB timeouts), and the system uses an LLM to instantly categorize the severity, identify the root cause, and suggest a fix.

## 🛠 Tech Stack
* **Backend:** Python + Flask (API)
* **Frontend:** React + Vite + TailwindCSS
* **Database:** PostgreSQL (Serverless Neon Tech)
* **AI:** Groq API (Llama 3) for high-speed log parsing
* **Data Validation:** Pydantic

---

## 🧠 Key Technical Decisions & Architecture

My primary goal was to build a system that prioritizes **simplicity, correct boundaries, and interface safety** over feature bloat. 

### 1. Structure & Boundaries (Separation of Concerns)
The backend is split into distinct, isolated layers so changes in one area do not break others (Change Resilience):
* `routes.py`: Purely handles HTTP requests and responses.
* `database.py` & `models.py`: Manages the SQLAlchemy database connection and table structures.
* `schemas.py`: Houses Pydantic models for strict data contracts.
* `services/groq_service.py`: Isolates the external AI API logic. If we swap Groq for OpenAI tomorrow, the API routes remain completely untouched.

### 2. Interface Safety (Flask + Pydantic)
While Flask doesn't have built-in request validation like FastAPI, I deliberately brought **Pydantic** into the Flask environment. Before any log touches the database or the AI service, it must pass strict validation via `LogSubmissionRequest`. This guards against malformed payloads, preventing invalid system states.

### 3. Anonymous Session Management
To keep the application frictionless, I implemented a UUID-based session system. The frontend generates a session ID stored in `localStorage` and sends it via the `X-Session-ID` header. This ensures users only see their own logs without the overhead of a complex JWT/OAuth authentication system.

### 4. Observability & Error Handling
Failures are visible and diagnosable. If the Groq API times out, or if the user submits invalid JSON, the Flask API catches the exception and returns explicit HTTP error codes (400, 422, 500) along with a descriptive payload. The React frontend reads these codes and displays clear error banners to the user, ensuring the system never fails silently.

---

## 🤖 AI Guidance & Usage

I utilized AI agents (Claude/Gemini) to accelerate boilerplate creation and React component styling. However, to ensure system integrity, I applied strict constraints.

* **AI Guidance Files:** Included in the `.ai-context/` directory, you will find `groq_prompts.md` and `coding_standards.md`. These files were used to constrain the AI's behavior, enforcing strict JSON output from the LLM and dictating Python/React coding standards.
* **Verification:** All AI-generated code was critically reviewed. Specifically, I manually enforced the separation of the `groq_service.py` to ensure the external LLM calls didn't pollute the core API routing logic.

---

## ⚠️ Risks & Extension Approach

### Current Risks
1. **Context Window Limits:** Currently, massive log files (e.g., 50MB) will exceed the LLM's token limit and cause a failure.
2. **Blocking Operations:** The Groq API call is currently synchronous. If the LLM takes 5 seconds to respond, the Flask worker is blocked.

### Extension Approach (Next Steps)
If this were a production system moving from 0→1, my immediate next steps would be:
1. **Asynchronous Processing:** Introduce Celery + Redis to process large log files in the background, allowing the API to instantly return a `202 Accepted` status while the frontend polls for completion.
2. **Chunking & RAG:** Implement a chunking strategy for massive logs, using a vector database to search for the most relevant error signatures before sending them to the LLM to save tokens and reduce latency.

---

## 💻 Local Setup Instructions

### Backend (Flask)
1. Navigate to the `/backend` directory.
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file and add your `GROQ_API_KEY`.
6. Run the server: `python app/main.py`

### Frontend (React)
1. Navigate to the `/frontend` directory.
2. Install dependencies: `npm install`
3. Create a `.env` file and add: `VITE_API_URL=http://127.0.0.1:8000/api`
4. Run the development server: `npm run dev`
