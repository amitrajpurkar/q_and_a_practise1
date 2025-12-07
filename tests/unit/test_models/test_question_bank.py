"""
Unit tests for QuestionBank model.

Tests question collection management, filtering, and indexing.
"""

import pytest
from typing import List
from unittest.mock import Mock

from src.models.question_bank import QuestionBank
from src.models.question import Question
from src.services.interfaces import QuestionFilter
from src.utils.exceptions import ValidationError, QuestionError


class TestQuestionBankCreation:
    """Unit tests for QuestionBank creation."""

    def test_create_empty_question_bank(self) -> None:
        """Test creating an empty question bank."""
        bank = QuestionBank()
        
        assert bank.questions == []
        assert bank.total_count == 0
        assert bank.loaded_at is not None

    def test_create_with_questions(self) -> None:
        """Test creating question bank with questions."""
        questions = [
            Question(
                id="q_1",
                topic="Physics",
                question_text="What is Newton's first law?",
                option1="Inertia",
                option2="F=ma",
                option3="Action-reaction",
                option4="Gravity",
                correct_answer="Inertia",
                difficulty="Easy",
                tag="Physics-Easy"
            )
        ]
        
        bank = QuestionBank(questions=questions)
        
        assert len(bank.questions) == 1
        assert bank.total_count == 1


class TestAddQuestion:
    """Unit tests for add_question method."""

    @pytest.fixture
    def bank(self) -> QuestionBank:
        """Create an empty question bank."""
        return QuestionBank()

    @pytest.fixture
    def sample_question(self) -> Question:
        """Create a sample question."""
        return Question(
            id="q_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            option1="Inertia",
            option2="F=ma",
            option3="Action-reaction",
            option4="Gravity",
            correct_answer="Inertia",
            difficulty="Easy",
            tag="Physics-Easy"
        )

    def test_add_question_success(self, bank: QuestionBank, sample_question: Question) -> None:
        """Test adding a question successfully."""
        bank.add_question(sample_question)
        
        assert len(bank.questions) == 1
        assert bank.total_count == 1

    def test_add_question_updates_indexes(self, bank: QuestionBank, sample_question: Question) -> None:
        """Test that adding question updates indexes."""
        bank.add_question(sample_question)
        
        assert "Physics" in bank._topic_index
        assert "Easy" in bank._difficulty_index
        assert "q_1" in bank._id_index

    def test_add_question_invalid_type_raises_error(self, bank: QuestionBank) -> None:
        """Test that adding non-Question raises ValidationError."""
        with pytest.raises(ValidationError):
            bank.add_question("not a question")

    def test_add_question_duplicate_id_raises_error(self, bank: QuestionBank, sample_question: Question) -> None:
        """Test that adding duplicate ID raises QuestionError."""
        bank.add_question(sample_question)
        
        with pytest.raises(QuestionError):
            bank.add_question(sample_question)


class TestGetQuestionById:
    """Unit tests for get_question_by_id method."""

    @pytest.fixture
    def bank_with_questions(self) -> QuestionBank:
        """Create a question bank with questions."""
        questions = [
            Question(
                id="q_1",
                topic="Physics",
                question_text="What is Newton's first law?",
                option1="Inertia",
                option2="F=ma",
                option3="Action-reaction",
                option4="Gravity",
                correct_answer="Inertia",
                difficulty="Easy",
                tag="Physics-Easy"
            ),
            Question(
                id="q_2",
                topic="Chemistry",
                question_text="What is H2O?",
                option1="Water",
                option2="Oxygen",
                option3="Hydrogen",
                option4="Carbon",
                correct_answer="Water",
                difficulty="Easy",
                tag="Chemistry-Easy"
            )
        ]
        return QuestionBank(questions=questions)

    def test_get_question_by_id_found(self, bank_with_questions: QuestionBank) -> None:
        """Test getting question by ID when found."""
        result = bank_with_questions.get_question_by_id("q_1")
        
        assert result is not None
        assert result.id == "q_1"

    def test_get_question_by_id_not_found(self, bank_with_questions: QuestionBank) -> None:
        """Test getting question by ID when not found."""
        result = bank_with_questions.get_question_by_id("nonexistent")
        
        assert result is None


class TestGetAllQuestions:
    """Unit tests for get_all_questions method."""

    def test_get_all_questions_empty(self) -> None:
        """Test getting all questions from empty bank."""
        bank = QuestionBank()
        
        result = bank.get_all_questions()
        
        assert result == []

    def test_get_all_questions_with_data(self) -> None:
        """Test getting all questions with data."""
        questions = [
            Question(
                id="q_1",
                topic="Physics",
                question_text="What is Newton's first law?",
                option1="Inertia",
                option2="F=ma",
                option3="Action-reaction",
                option4="Gravity",
                correct_answer="Inertia",
                difficulty="Easy",
                tag="Physics-Easy"
            ),
            Question(
                id="q_2",
                topic="Chemistry",
                question_text="What is H2O?",
                option1="Water",
                option2="Oxygen",
                option3="Hydrogen",
                option4="Carbon",
                correct_answer="Water",
                difficulty="Easy",
                tag="Chemistry-Easy"
            )
        ]
        bank = QuestionBank(questions=questions)
        
        result = bank.get_all_questions()
        
        assert len(result) == 2


class TestFilterQuestions:
    """Unit tests for filter_questions method."""

    @pytest.fixture
    def bank_with_questions(self) -> QuestionBank:
        """Create a question bank with diverse questions."""
        questions = [
            Question(
                id="q_1",
                topic="Physics",
                question_text="What is Newton's first law?",
                option1="Inertia",
                option2="F=ma",
                option3="Action-reaction",
                option4="Gravity",
                correct_answer="Inertia",
                difficulty="Easy",
                tag="Physics-Easy"
            ),
            Question(
                id="q_2",
                topic="Physics",
                question_text="What is the speed of light?",
                option1="3x10^8 m/s",
                option2="2x10^8 m/s",
                option3="4x10^8 m/s",
                option4="1x10^8 m/s",
                correct_answer="3x10^8 m/s",
                difficulty="Hard",
                tag="Physics-Hard"
            ),
            Question(
                id="q_3",
                topic="Chemistry",
                question_text="What is H2O?",
                option1="Water",
                option2="Oxygen",
                option3="Hydrogen",
                option4="Carbon",
                correct_answer="Water",
                difficulty="Easy",
                tag="Chemistry-Easy"
            )
        ]
        return QuestionBank(questions=questions)

    def test_filter_by_topic(self, bank_with_questions: QuestionBank) -> None:
        """Test filtering by topic."""
        criteria = QuestionFilter(topic="Physics")
        
        result = bank_with_questions.filter_questions(criteria)
        
        assert len(result) == 2
        assert all(q.topic == "Physics" for q in result)

    def test_filter_by_difficulty(self, bank_with_questions: QuestionBank) -> None:
        """Test filtering by difficulty."""
        criteria = QuestionFilter(difficulty="Easy")
        
        result = bank_with_questions.filter_questions(criteria)
        
        assert len(result) == 2
        assert all(q.difficulty == "Easy" for q in result)

    def test_filter_by_topic_and_difficulty(self, bank_with_questions: QuestionBank) -> None:
        """Test filtering by topic and difficulty."""
        criteria = QuestionFilter(topic="Physics", difficulty="Easy")
        
        result = bank_with_questions.filter_questions(criteria)
        
        assert len(result) == 1
        assert result[0].id == "q_1"

    def test_filter_with_exclude_ids(self, bank_with_questions: QuestionBank) -> None:
        """Test filtering with excluded IDs."""
        criteria = QuestionFilter(topic="Physics", exclude_ids=["q_1"])
        
        result = bank_with_questions.filter_questions(criteria)
        
        assert len(result) == 1
        assert result[0].id == "q_2"


class TestGetRandomQuestion:
    """Unit tests for get_random_question method."""

    @pytest.fixture
    def bank_with_questions(self) -> QuestionBank:
        """Create a question bank with questions."""
        questions = [
            Question(
                id="q_1",
                topic="Physics",
                question_text="What is Newton's first law?",
                option1="Inertia",
                option2="F=ma",
                option3="Action-reaction",
                option4="Gravity",
                correct_answer="Inertia",
                difficulty="Easy",
                tag="Physics-Easy"
            ),
            Question(
                id="q_2",
                topic="Physics",
                question_text="What is the speed of light?",
                option1="3x10^8 m/s",
                option2="2x10^8 m/s",
                option3="4x10^8 m/s",
                option4="1x10^8 m/s",
                correct_answer="3x10^8 m/s",
                difficulty="Easy",
                tag="Physics-Easy"
            )
        ]
        return QuestionBank(questions=questions)

    def test_get_random_question_found(self, bank_with_questions: QuestionBank) -> None:
        """Test getting random question when available."""
        criteria = QuestionFilter(topic="Physics", difficulty="Easy")
        
        result = bank_with_questions.get_random_question(criteria)
        
        assert result is not None
        assert result.topic == "Physics"

    def test_get_random_question_not_found(self, bank_with_questions: QuestionBank) -> None:
        """Test getting random question when none match."""
        criteria = QuestionFilter(topic="Math", difficulty="Easy")
        
        result = bank_with_questions.get_random_question(criteria)
        
        assert result is None


class TestCountQuestions:
    """Unit tests for count_questions method."""

    @pytest.fixture
    def bank_with_questions(self) -> QuestionBank:
        """Create a question bank with questions."""
        questions = [
            Question(
                id="q_1",
                topic="Physics",
                question_text="What is Newton's first law?",
                option1="Inertia",
                option2="F=ma",
                option3="Action-reaction",
                option4="Gravity",
                correct_answer="Inertia",
                difficulty="Easy",
                tag="Physics-Easy"
            ),
            Question(
                id="q_2",
                topic="Physics",
                question_text="What is the speed of light?",
                option1="3x10^8 m/s",
                option2="2x10^8 m/s",
                option3="4x10^8 m/s",
                option4="1x10^8 m/s",
                correct_answer="3x10^8 m/s",
                difficulty="Hard",
                tag="Physics-Hard"
            )
        ]
        return QuestionBank(questions=questions)

    def test_count_questions_by_criteria(self, bank_with_questions: QuestionBank) -> None:
        """Test counting questions by criteria."""
        criteria = QuestionFilter(topic="Physics")
        
        result = bank_with_questions.count_questions(criteria)
        
        assert result == 2

    def test_count_questions_zero(self, bank_with_questions: QuestionBank) -> None:
        """Test counting when no questions match."""
        criteria = QuestionFilter(topic="Math")
        
        result = bank_with_questions.count_questions(criteria)
        
        assert result == 0


class TestGetAvailableTopicsAndDifficulties:
    """Unit tests for get_available_topics and get_available_difficulties methods."""

    @pytest.fixture
    def bank_with_questions(self) -> QuestionBank:
        """Create a question bank with diverse questions."""
        questions = [
            Question(
                id="q_1",
                topic="Physics",
                question_text="What is Newton's first law?",
                option1="Inertia",
                option2="F=ma",
                option3="Action-reaction",
                option4="Gravity",
                correct_answer="Inertia",
                difficulty="Easy",
                tag="Physics-Easy"
            ),
            Question(
                id="q_2",
                topic="Chemistry",
                question_text="What is H2O?",
                option1="Water",
                option2="Oxygen",
                option3="Hydrogen",
                option4="Carbon",
                correct_answer="Water",
                difficulty="Hard",
                tag="Chemistry-Hard"
            )
        ]
        return QuestionBank(questions=questions)

    def test_get_available_topics(self, bank_with_questions: QuestionBank) -> None:
        """Test getting available topics."""
        result = bank_with_questions.get_available_topics()
        
        assert len(result) == 2
        assert "Physics" in result
        assert "Chemistry" in result

    def test_get_available_difficulties(self, bank_with_questions: QuestionBank) -> None:
        """Test getting available difficulties."""
        result = bank_with_questions.get_available_difficulties()
        
        assert len(result) == 2
        assert "Easy" in result
        assert "Hard" in result
