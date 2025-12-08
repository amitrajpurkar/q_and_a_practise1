"""
Pytest configuration and fixtures for Q&A Practice Application tests.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest


@pytest.fixture
def sample_question_data():
    """Provide sample question data for tests."""
    return {
        'id': 'test-q-001',
        'topic': 'Physics',
        'question_text': 'What is the SI unit of force?',
        'difficulty': 'Easy',
        'option1': 'Newton',
        'option2': 'Joule',
        'option3': 'Watt',
        'option4': 'Pascal',
        'correct_answer': 'Newton',
        'tag': 'mechanics',
        'asked_in_this_session': 'FALSE',
        'got_right': 'FALSE'
    }


@pytest.fixture
def sample_session_data():
    """Provide sample session data for tests."""
    return {
        'topic': 'Physics',
        'difficulty': 'Easy',
        'total_questions': 10
    }


@pytest.fixture
def csv_path():
    """Provide path to question bank CSV."""
    return Path('src/main/resources/question-bank.csv')
