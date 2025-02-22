import requests
import logging

logger = logging.getLogger(__name__)

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def get_llm_response(user_message, cv_context):
    """Get response from Ollama LLM."""
    try:
        prompt = f"""Context: The following is a CV/resume: {cv_context}

User question: {user_message}

Please provide a relevant response based on the CV context."""

        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": "llama2",
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json().get('response', '')
    
    except Exception as e:
        logger.error(f"Error getting LLM response: {str(e)}")
        raise
