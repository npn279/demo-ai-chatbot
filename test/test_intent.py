import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from src.intent_classification import classify_question

questions = [
    'KNN là gì?',
    'Linear regression là gì?',
    'Phân biệt hai thuật toán'
]

lesson_content = [
    {"id": "1", "summary": "Học về KNN"},
    {"id": "2", "summary": "Học về Linear regression"},
    {"id": "3", "summary": "Học về Logistic regression"}
]

classify_question(questions, lesson_content)