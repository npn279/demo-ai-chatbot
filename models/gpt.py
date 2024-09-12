# model_loader.py
import os
from openai import OpenAI
from dotenv import load_dotenv

def load_api_key():
    """
    Load the API key from the .env file.
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        api_key = os.environ['OPENAI_API_KEY']
    
    if not api_key:
        raise ValueError("API key not found. Make sure it is set in the .env file.")
    
    return api_key

def generate(prompt, system_instruction=None, model_name='gpt-4o-mini', temperature=0.45, max_output_tokens=8192, stream=False):
    
    api_key = load_api_key()
    client = OpenAI(api_key=api_key)
    messages = []
    if system_instruction:
        messages.append({'role': 'system', 'content': system_instruction})
    else:
        messages.append({'role': 'system', 'content': 'You are a helpful AI assistant. You always respond in a friendly and helpful manner. Always respond in user language.'})

    messages.append({'role': 'user', 'content': prompt})

    completion = client.chat.completions.create(
        model=model_name,
        messages=messages,
        max_tokens=max_output_tokens,
        temperature=temperature,
        stream=stream,
    )

    return completion.choices[0].message.content
    
