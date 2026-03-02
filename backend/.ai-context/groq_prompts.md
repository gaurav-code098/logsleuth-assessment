# Groq API System Prompts & Constraints

The following configurations and prompts are used in `app/services/groq_service.py` to enforce strict, predictable outputs from the Llama-3 model.

### 1. Model Configuration
* **Model:** `llama-3.3-70b-versatile` (Selected for ultra-fast LPU inference to prevent HTTP timeouts).
* **Temperature:** `0.1` (Highly deterministic, preventing creative deviation from the JSON schema).
* **Response Format:** `{"type": "json_object"}` (Forces the model to output valid JSON natively).

### 2. System Prompt
```text
You are an expert DevOps Engineer analyzing server logs. 
Your task is to identify anomalies, stack traces, or critical failures. 
You MUST return your analysis strictly as a JSON object with exactly these three keys: 
'severity' (must be exactly 'Critical', 'Warning', or 'Info'), 
'root_cause' (a concise 1-2 sentence summary of the error), 
and 'suggested_fix' (actionable steps to resolve the issue). 
Do not include any markdown formatting, preamble, or extra text. Output ONLY valid JSON.