import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import json
import logging
from src.prompts import intent_prompt
from models.gpt import generate

def load_and_process_json(file_path):
    """
    Load and process the JSON file, then return lesson content as a formatted string.
    """
    lesson_content = ""
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            json_data = json.load(file)
            # print(json_data)
            for lesson in json_data:
                lesson_id = lesson.get("id")
                summary = lesson.get("summary")
                if lesson_id and summary:
                    lesson_content += f"{lesson_id} - {summary}\n"
            print(lesson_content)
            return lesson_content
        
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {e}")
            return None


def classify_question(questions, lesson_content):
    """
    Classify the user's question and return the appropriate response.
    """
    # Use the formatted string of lesson content
    lesson_content_str = [f'{i+1}. {lc}' for i, lc in enumerate(lesson_content)]
    lesson_content_str = '\n---\n'.join(lesson_content_str)
    
    # Format the question history (excluding the last question)
    q_his = [f'{i+1}. {q}' for i, q in enumerate(questions[:-1])]

    # Construct the prompt with the question history and the current question
    prompt = """\
### Lesson Content: 
{lesson_content_str}

### Question history:
{question_history}

### Current question:
{current_question}
""".format(
        lesson_content_str=lesson_content_str,
        question_history='\n'.join(q_his),
        current_question=questions[-1]
    )

    print('SYSTEM INSTRUCTION:', intent_prompt)
    
    logging.info(f'PROMPT INTENT: {prompt}')

    # Generate content using the model
    response = generate(prompt=prompt, system_instruction=intent_prompt, temperature=0.05)
    
    try:
        start = response.index('{')
        end = response.rindex('}') + 1
        json_str = response[start:end]
        result = json.loads(json_str)
        logging.info(f"Response intent classification: {result}")
        return result
    except (ValueError, json.JSONDecodeError) as e:
        logging.error(f"Error parsing response: {e}")
        logging.info(f"Raw response: {response}")
        return None

