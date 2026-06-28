import threading
import logging
from typing import Dict, Any, List
from backend.app.config import settings

logger = logging.getLogger(__name__)

# Global variables for the pipeline
_lamini_pipeline = None
_loading_error = None
_is_loading = False

def load_lamini_model():
    """
    Loads MBZUAI/LaMini-Flan-T5-77M model in a thread-safe way.
    """
    global _lamini_pipeline, _loading_error, _is_loading
    
    if _lamini_pipeline is not None:
        return _lamini_pipeline
        
    if _is_loading:
        return None
        
    _is_loading = True
    try:
        logger.info("Initializing HuggingFace LaMini-Flan-T5 pipeline...")
        from transformers import pipeline
        
        # Load small 77M parameter model, ideal for local CPU execution
        _lamini_pipeline = pipeline(
            "text2text-generation",
            model="MBZUAI/LaMini-Flan-T5-77M",
            device=-1  # Force CPU execution
        )
        logger.info("LaMini-Flan-T5 model loaded successfully.")
    except Exception as e:
        _loading_error = str(e)
        logger.error(f"Failed to load LaMini model: {str(e)}. Fallbacks will be utilized.")
    finally:
        _is_loading = False
        
    return _lamini_pipeline

def start_background_load():
    """
    Spins off a background thread to pre-load the LaMini model.
    """
    thread = threading.Thread(target=load_lamini_model, daemon=True)
    thread.start()

def get_lamini_explanation(topic: str) -> Dict[str, Any]:
    """
    Explanation Module: Explains concepts in simple language.
    Attempts to run local LaMini-Flan-T5 model.
    If unavailable or fails, falls back to Gemini API.
    """
    pipeline = load_lamini_model()
    
    if pipeline:
        try:
            # Format prompt for the text2text model
            prompt = f"Explain the concept of {topic} simply with examples and applications."
            response = pipeline(prompt, max_length=256, num_return_sequences=1)
            generated_text = response[0]["generated_text"].strip()
            
            # Since LaMini is a small model and returns unstructured text,
            # we'll parse it into structural parts or use simple defaults.
            definition = generated_text
            examples = [f"An instance of {topic} in practice.", f"Demonstration of {topic} concepts."]
            applications = [f"Used to solve real-world problems involving {topic}."]
            summary = f"In conclusion, {topic} represents a crucial foundational block."
            
            return {
                "Definition": definition,
                "Examples": examples,
                "Applications": applications,
                "Summary": summary,
                "ModelUsed": "LaMini-Flan-T5"
            }
        except Exception as e:
            logger.error(f"LaMini inference failed: {str(e)}. Falling back to Gemini.")
            
    # Fallback to Gemini with custom prompts for the simple explanation structure
    return get_gemini_fallback_explanation(topic)

def get_gemini_fallback_explanation(topic: str) -> Dict[str, Any]:
    """
    Gemini fallback explanation generator if local LaMini is not running or fails.
    """
    from backend.app.services.gemini import ask_gemini_qa, settings
    import json
    
    # If Gemini API Key is configured, use it to get a beautiful simple explanation structure
    if settings.GEMINI_API_KEY:
        from backend.app.services.gemini import _call_gemini_with_retry, _parse_json_safely
        prompt = f"""
        You are a teaching assistant tasked with explaining "{topic}" in extremely simple language (suitable for self-learners).
        Provide the response strictly in JSON format with the following keys:
        - "Definition": A simple, jargon-free definition of the topic.
        - "Examples": A list of 2-3 simple, easy-to-grasp examples.
        - "Applications": A list of 2-3 real-world applications of this concept.
        - "Summary": A one-sentence summary of the concept.

        Do not include any text outside the JSON structure.
        """
        try:
            response_text = _call_gemini_with_retry(prompt, model_name="gemini-2.5-flash", json_mode=True)
            result = _parse_json_safely(response_text)
            result["ModelUsed"] = "Gemini (LaMini-Fallback)"
            return result

        except Exception as e:
            logger.error(f"Gemini fallback explanation failed: {str(e)}")
            
    # Local simulation fallback if both LaMini and Gemini are unavailable
    return {
        "Definition": f"{topic} is a conceptual subject of study. (Simulated explanation)",
        "Examples": [
            f"An example of {topic} is its use in everyday decision-making.",
            f"Applying {topic} to simplify complex workflows."
        ],
        "Applications": [
            f"Self-learners use {topic} to map out academic subjects.",
            f"Educators use {topic} to construct illustrative analogies."
        ],
        "Summary": f"To summarize, {topic} is a fundamental topic for students and educators.",
        "ModelUsed": "Simulated (LaMini-Fallback)"
    }
