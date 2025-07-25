import os
import json
import requests
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_openrouter_models():
    """Fetch available models from OpenRouter API"""
    try:
        response = requests.get("https://openrouter.ai/api/v1/models")
        if response.status_code == 200:
            models_data = response.json()
            # Filter for free models (price = 0)
            free_models = []
            for model in models_data.get("data", []):
                pricing = model.get("pricing", {})
                # Check if prompt and completion prices are 0 or "0"
                prompt_price = pricing.get("prompt", "1")
                completion_price = pricing.get("completion", "1")
                if (prompt_price == "0" or prompt_price == 0) and (completion_price == "0" or completion_price == 0):
                    free_models.append({
                        "id": model.get("id"),
                        "name": model.get("name"),
                        "description": model.get("description", "")
                    })
            return free_models
        else:
            logging.error(f"Failed to fetch models: {response.status_code}")
            return []
    except Exception as e:
        logging.error(f"Error fetching models: {str(e)}")
        return []

def openrouter_call(model="qwen/qwen3-235b-a22b-2507:free", 
                   user_content="What is the meaning of life?", 
                   system_content=None):
    """Make a call to the OpenRouter API"""
    try:
        # Get API key from environment
        api_key = os.getenv("API-KEY")
        if not api_key:
            raise ValueError("API-KEY not found in environment variables")
        
        # Prepare messages
        if system_content is not None and len(system_content.strip()):
            messages = [
                {'role': 'system', 'content': system_content},
                {'role': 'user', 'content': user_content}
            ]
        else:
            messages = [
                {'role': 'user', 'content': user_content}
            ]
        
        # Make API call
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
            },
            data=json.dumps({
                "model": model,
                "messages": messages
            })
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            logging.error(f"OpenRouter API call failed: {response.status_code} - {response.text}")
            return f"Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        logging.error(f"Error in OpenRouter call: {str(e)}")
        return f"Error: {str(e)}"

