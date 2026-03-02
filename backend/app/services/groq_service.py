import os
import json
import logging
from groq import Groq
from pydantic import ValidationError
from app.schemas import GroqAnalysisResult

# Set up logging for Observability
logger = logging.getLogger(__name__)

# Initialize the Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def analyze_log_with_groq(raw_log_text: str) -> GroqAnalysisResult:
    """
    Sends the raw log to Groq's Llama 3 model, forces a JSON response,
    and strictly validates the output against our Pydantic schema.
    """
    system_prompt = (
        "You are an expert DevOps Engineer analyzing server logs. "
        "Your task is to identify anomalies, stack traces, or critical failures. "
        "You MUST return your analysis strictly as a JSON object with exactly these three keys: "
        "'severity' (must be exactly 'Critical', 'Warning', or 'Info'), "
        "'root_cause' (a concise 1-2 sentence summary of the error), "
        "and 'suggested_fix' (actionable steps to resolve the issue). "
        "Do not include any markdown formatting, preamble, or extra text. Output ONLY valid JSON."
    )

    # Pre-define variables so they are guaranteed to exist for the except blocks
    raw_response = None
    parsed_json = None

    try:
        logger.info("Initiating Groq API call...")
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this log:\n\n{raw_log_text}"}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        raw_response = completion.choices[0].message.content
        
        # Pylance Fix 1: explicitly handle the possibility of a None response
        if not raw_response:
            raise Exception("Groq API returned an empty response.")

        logger.info("Received response from Groq. Parsing and validating...")

        parsed_json = json.loads(raw_response)
        validated_result = GroqAnalysisResult(**parsed_json)
        
        return validated_result

    except json.JSONDecodeError as e:
        # Pylance Fix 2: raw_response is now guaranteed to be bound
        logger.error(f"Groq did not return valid JSON: {str(e)}\nRaw Response: {raw_response}")
        raise Exception("AI response was not valid JSON.")
    
    except ValidationError as e:
        logger.error(f"Groq JSON did not match Pydantic schema: {str(e)}\nParsed JSON: {parsed_json}")
        raise Exception("AI response failed schema validation.")
    
    except Exception as e:
        logger.error(f"Groq API call failed entirely: {str(e)}")
        raise Exception(f"AI Inference Service Error: {str(e)}")