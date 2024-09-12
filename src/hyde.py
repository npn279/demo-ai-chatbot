import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import logging
from model_loader import setup_model
from src.prompts import hyde_prompt
from models.gpt import generate

def get_ai_tutor_response(questions):
    """
    Get the AI tutor's response to the classification answer.
    """
    pre_questions = [f'{i+1}. {q}' for i, q in enumerate(questions[:-1])]
    pre_questions = '\n---\n'.join(pre_questions)

    prompt = """\
### Previous questions:
{pre_questions}

### Current question:
{current_question}
""".format(
    pre_questions=pre_questions,
    current_question=questions[-1]
)
    
    response = generate(prompt=prompt, system_instruction=hyde_prompt)

    logging.info(f"HyDE: {response}")
    return response
