# model_loader.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

def load_api_key():
    """
    Load the API key from the .env file.
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        api_key = os.environ['GEMINI_API_KEY']
    
    if not api_key:
        raise ValueError("API key not found. Make sure it is set in the .env file.")
    
    return api_key

def generate(prompt, model_name='gemini-flash', system_instruction=None, temperature=0.45, max_output_tokens=8192):
    api_key = load_api_key()
    genai.configure(api_key=api_key)
    generation_config = {
        "temperature": temperature,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": max_output_tokens,
    }

    if not system_instruction:
        system_instruction='You are a helpful AI assistant. You always respond in a friendly and helpful manner. Always respond in user language.',

    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
        system_instruction=system_instruction,
    )

    response = model.generate_content(prompt)
    return response.text

