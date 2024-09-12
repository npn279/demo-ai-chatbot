import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import json
import logging

from prompts import main_prompt
from model_loader import setup_model
from intent_classification import classify_question
from hyde import get_ai_tutor_response

# Set up logging
logging.basicConfig(level=logging.INFO)

# Global variable for the model
model = None
chat_history_file = 'data/chat_history.json'


def load_and_process_json(file_path):
    """
    Load and process the JSON file, then return lesson content as a list of dictionaries.
    """
    lesson_content = []
    with open(file_path, 'r', encoding='utf8') as file:
        try:
            json_data = json.load(file)
            for lesson_id, lesson_data in json_data.items():
                summary = lesson_data.get("summary")
                lesson_content.append({"id": lesson_id, "summary": summary})
            return lesson_content
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {e}")
            return None

def get_final_answer(content, question, constraint_prompt):
    """
    Get the final answer by combining content from Hyde and lesson content, and leveraging chat history.
    Output: final_answer (str)
    """
    global model
    model = setup_model("gemini-1.5-flash", main_prompt, temperature=0.15)
    # Start a new chat session with the model
    chat_session = model.start_chat(history=[])

    # Create the full prompt with content and question
    prompt = f"""\
    ### Content: 
    {content}
    
    ### Question:
    {question}

    ### Important:
    {constraint_prompt}
    """

    # Send the message to the model
    response = chat_session.send_message(prompt)
    
    return response.text

def load_chat_history():
    """
    Load chat history from the chat_history.json file, or return an empty dictionary if the file doesn't exist.
    Output: chat_history (dict)
    """
    if os.path.exists(chat_history_file):
        with open(chat_history_file, 'r', encoding='utf8') as file:
            try:
                chat_history = json.load(file)
                return chat_history
            except json.JSONDecodeError as e:
                print(f"Error loading chat history: {e}")
                return {}
    else:
        return {}

def save_chat_history(chat_id, question, response):
    """
    Save the chat history to the chat_history.json file after every interaction.
    """
    chat_history = load_chat_history()
    
    # If this chat ID doesn't exist in the history, create it
    if chat_id not in chat_history:
        chat_history[chat_id] = []
    
    # Append the current question and response to the chat history
    chat_history[chat_id].append({
        'question': question,
        'parts': response
    })

    # Write the updated history back to the file
    with open(chat_history_file, 'w', encoding='utf8') as file:
        json.dump(chat_history, file, ensure_ascii=False, indent=2)

def genAnswer(question, chat_id):
    """
    Generate the final answer based on the question. No need to pass history as it is stored.
    """

    # Load lesson content from output.json
    lesson_content = load_and_process_json('data/output.json')

    # Load chat history
    chat_history = load_chat_history()

    # Get history for the current chat_id
    current_chat_history = chat_history.get(chat_id, [])

    # Extract all questions from the history
    history_questions = [item['question'] for item in current_chat_history]

    # Combine history questions with the current question
    all_questions = history_questions + [question]

    # Classify the combined questions with Intent Classification
    intent_result = classify_question(all_questions, lesson_content)

    logging.info(f"Intent result: {intent_result}")
    
    # Check if the intent_result is None
    if intent_result is None:
        logging.error("Error: Intent classification returned None.")
        return "Xin lỗi, hiện tại tôi không thể trả lời câu hỏi của bạn. Bạn có thể thử hỏi về một chủ đề cụ thể khác."

    class_intent = intent_result.get('class', 'study')
    constraint_prompt = intent_result.get('answer', '')

    if class_intent == 'other':
        response = intent_result.get('answer')
        save_chat_history(chat_id, question, response)
        return response

    # For "study" intent, continue with lesson processing
    lesson_ids = intent_result.get('id_lesson', '').split(',')
    logging.info(f"Lesson IDs: {lesson_ids}")
    
    if not lesson_ids:
        # response = "It seems like no lessons are directly related to your question. Please try asking about a specific topic."
        response = "Xin lỗi, hiện tại tôi không thể trả lời câu hỏi của bạn. Bạn có thể thử hỏi về một chủ đề cụ thể khác."
        save_chat_history(chat_id, question, response)
        return response

    # Filter relevant content from output.json based on lesson_ids
    lesson_content_filtered = [item['summary'] for item in lesson_content if item['id'] in lesson_ids]
    lesson_content_filtered = "\n---\n".join(lesson_content_filtered)

    # Get the answer from Hyde
    hyde_response = get_ai_tutor_response(all_questions)

    # Combine content from Hyde, lesson_content, and the original question
    content = hyde_response + "\n---\n" + lesson_content_filtered

    # Get the final answer from the model
    final_answer = get_final_answer(content, question, constraint_prompt)

    # Save the interaction to the chat history
    save_chat_history(chat_id, question, final_answer)
    
    return final_answer


def main():
    """
    Main execution function.
    """
    global model  # Access the global model variable
    model = setup_model("gemini-1.5-flash", main_prompt, temperature=0.15)

    # Example question and chat ID (to simulate unique user or conversation session)
    question = "Singular Value Decomposition là gì?"
    chat_id = 'user_4567ffff4ff83333390'
    # Generate the final answer from the question
    final_answer = genAnswer(question, chat_id)

    # Print the final answer
    print("\n--- Final Answer ---")
    print(final_answer)

if __name__ == "__main__":
    main()

