# AI Coding Standards & Constraints

These are the strict constraints provided to the AI (Gemini) used to assist in generating the codebase for this assessment:

1. **Simplicity over Cleverness:** Do not generate complex one-liners or abstract design patterns. Prioritize readable, predictable Python and React code.
2. **Strict Typing & Interface Safety:** Always enforce type hints in Python. Use Pydantic models for *all* data entering or leaving the system. Never trust external input.
3. **Database Agnosticism:** Use SQLAlchemy ORM for all database interactions. Do not write raw SQL strings to ensure change resilience and prevent SQL injection.
4. **Error Handling (Observability):** Never swallow exceptions. External API calls must be wrapped in `try/except` blocks, explicitly logged, and mapped to proper HTTP status codes (e.g., 503 for upstream AI failures).
5. **No Hallucinated States:** Database state must be tracked explicitly (`pending`, `success`, `failed`). Changes must be committed before making external LLM calls to prevent data loss.