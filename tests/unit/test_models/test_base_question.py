"""
Unit tests for base question models.

Tests abstract base classes and inheritance hierarchies.
"""

import pytest
from typing import Dict, Any
from dataclasses import dataclass

from src.models.base_question import BaseQuestion, ChoiceBasedQuestion, TextBasedQuestion
from src.utils.exceptions import ValidationError


# Concrete implementation of BaseQuestion for testing
@dataclass
class ConcreteQuestion(BaseQuestion):
    """Concrete implementation of BaseQuestion for testing."""
    
    def get_question_type(self) -> str:
        return "concrete"
    
    def validate_answer(self, user_answer: str) -> bool:
        return user_answer.lower() == "correct"
    
    def get_display_format(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "topic": self.topic,
            "question_text": self.question_text,
            "difficulty": self.difficulty
        }
    
    def calculate_difficulty_score(self) -> float:
        difficulty_scores = {"Easy": 1.0, "Medium": 2.0, "Hard": 3.0}
        return difficulty_scores.get(self.difficulty, 1.0)
    
    def get_hint(self) -> str:
        return f"Hint for {self.topic} question"
    
    def get_time_limit(self) -> int:
        time_limits = {"Easy": 30, "Medium": 60, "Hard": 90}
        return time_limits.get(self.difficulty, 60)


# Concrete implementation of ChoiceBasedQuestion for testing
@dataclass
class ConcreteChoiceQuestion(ChoiceBasedQuestion):
    """Concrete implementation of ChoiceBasedQuestion for testing."""
    
    def get_question_type(self) -> str:
        return "multiple_choice"
    
    def validate_answer(self, user_answer: str) -> bool:
        return user_answer.strip().lower() == self.correct_answer.strip().lower()
    
    def get_display_format(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "topic": self.topic,
            "question_text": self.question_text,
            "options": self.get_all_options(),
            "difficulty": self.difficulty
        }
    
    def calculate_difficulty_score(self) -> float:
        difficulty_scores = {"Easy": 1.0, "Medium": 2.0, "Hard": 3.0}
        return difficulty_scores.get(self.difficulty, 1.0)
    
    def get_hint(self) -> str:
        return f"Choose from the available options"
    
    def get_time_limit(self) -> int:
        return 60


# Concrete implementation of TextBasedQuestion for testing
@dataclass
class ConcreteTextQuestion(TextBasedQuestion):
    """Concrete implementation of TextBasedQuestion for testing."""
    
    def get_question_type(self) -> str:
        return "text_input"
    
    def validate_answer(self, user_answer: str) -> bool:
        if self.case_sensitive:
            return user_answer.strip() == self.expected_answer.strip()
        return user_answer.strip().lower() == self.expected_answer.strip().lower()
    
    def get_display_format(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "topic": self.topic,
            "question_text": self.question_text,
            "difficulty": self.difficulty,
            "case_sensitive": self.case_sensitive
        }
    
    def calculate_difficulty_score(self) -> float:
        difficulty_scores = {"Easy": 1.0, "Medium": 2.0, "Hard": 3.0}
        base_score = difficulty_scores.get(self.difficulty, 1.0)
        # Text-based questions are slightly harder
        return base_score * 1.2
    
    def get_hint(self) -> str:
        return f"Type your answer"
    
    def get_time_limit(self) -> int:
        return 90


class TestBaseQuestion:
    """Unit tests for BaseQuestion abstract class."""

    def test_create_concrete_question(self) -> None:
        """Test creating a concrete question."""
        question = ConcreteQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            difficulty="Easy"
        )
        
        assert question.id == "test_1"
        assert question.topic == "Physics"
        assert question.difficulty == "Easy"

    def test_question_type(self) -> None:
        """Test get_question_type method."""
        question = ConcreteQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            difficulty="Easy"
        )
        
        assert question.get_question_type() == "concrete"

    def test_validate_answer(self) -> None:
        """Test validate_answer method."""
        question = ConcreteQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            difficulty="Easy"
        )
        
        assert question.validate_answer("correct") is True
        assert question.validate_answer("CORRECT") is True
        assert question.validate_answer("wrong") is False

    def test_get_display_format(self) -> None:
        """Test get_display_format method."""
        question = ConcreteQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            difficulty="Easy"
        )
        
        display = question.get_display_format()
        
        assert display["id"] == "test_1"
        assert display["topic"] == "Physics"
        assert display["question_text"] == "What is Newton's first law?"

    def test_calculate_difficulty_score(self) -> None:
        """Test calculate_difficulty_score method."""
        easy_question = ConcreteQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            difficulty="Easy"
        )
        hard_question = ConcreteQuestion(
            id="test_2",
            topic="Physics",
            question_text="What is Newton's first law?",
            difficulty="Hard"
        )
        
        assert easy_question.calculate_difficulty_score() == 1.0
        assert hard_question.calculate_difficulty_score() == 3.0

    def test_get_hint(self) -> None:
        """Test get_hint method."""
        question = ConcreteQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            difficulty="Easy"
        )
        
        hint = question.get_hint()
        assert "Physics" in hint

    def test_get_time_limit(self) -> None:
        """Test get_time_limit method."""
        easy_question = ConcreteQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            difficulty="Easy"
        )
        hard_question = ConcreteQuestion(
            id="test_2",
            topic="Physics",
            question_text="What is Newton's first law?",
            difficulty="Hard"
        )
        
        assert easy_question.get_time_limit() == 30
        assert hard_question.get_time_limit() == 90

    def test_empty_id_raises_error(self) -> None:
        """Test that empty ID raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ConcreteQuestion(
                id="",
                topic="Physics",
                question_text="What is Newton's first law?",
                difficulty="Easy"
            )
        
        assert "ID cannot be empty" in str(exc_info.value)

    def test_empty_topic_raises_error(self) -> None:
        """Test that empty topic raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ConcreteQuestion(
                id="test_1",
                topic="",
                question_text="What is Newton's first law?",
                difficulty="Easy"
            )
        
        assert "Topic cannot be empty" in str(exc_info.value)

    def test_empty_question_text_raises_error(self) -> None:
        """Test that empty question text raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ConcreteQuestion(
                id="test_1",
                topic="Physics",
                question_text="",
                difficulty="Easy"
            )
        
        assert "Question text cannot be empty" in str(exc_info.value)

    def test_empty_difficulty_raises_error(self) -> None:
        """Test that empty difficulty raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ConcreteQuestion(
                id="test_1",
                topic="Physics",
                question_text="What is Newton's first law?",
                difficulty=""
            )
        
        assert "Difficulty cannot be empty" in str(exc_info.value)

    def test_str_representation(self) -> None:
        """Test string representation."""
        question = ConcreteQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            difficulty="Easy"
        )
        
        str_repr = str(question)
        assert "test_1" in str_repr
        assert "concrete" in str_repr

    def test_repr_representation(self) -> None:
        """Test repr representation."""
        question = ConcreteQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            difficulty="Easy"
        )
        
        repr_str = repr(question)
        assert "test_1" in repr_str
        assert "Physics" in repr_str


class TestChoiceBasedQuestion:
    """Unit tests for ChoiceBasedQuestion class."""

    def test_create_choice_question(self) -> None:
        """Test creating a choice-based question."""
        question = ConcreteChoiceQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            difficulty="Easy",
            option1="Inertia",
            option2="F=ma",
            option3="Action-reaction",
            option4="Gravity",
            correct_answer="Inertia"
        )
        
        assert question.id == "test_1"
        assert question.option1 == "Inertia"
        assert question.correct_answer == "Inertia"

    def test_get_all_options(self) -> None:
        """Test get_all_options method."""
        question = ConcreteChoiceQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            difficulty="Easy",
            option1="Inertia",
            option2="F=ma",
            option3="Action-reaction",
            option4="Gravity",
            correct_answer="Inertia"
        )
        
        options = question.get_all_options()
        
        assert len(options) == 4
        assert "Inertia" in options
        assert "F=ma" in options

    def test_get_all_options_with_none(self) -> None:
        """Test get_all_options with some None options."""
        question = ConcreteChoiceQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            difficulty="Easy",
            option1="Inertia",
            option2="F=ma",
            option3=None,
            option4=None,
            correct_answer="Inertia"
        )
        
        options = question.get_all_options()
        
        assert len(options) == 2

    def test_validate_answer_correct(self) -> None:
        """Test validating correct answer."""
        question = ConcreteChoiceQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            difficulty="Easy",
            option1="Inertia",
            option2="F=ma",
            option3="Action-reaction",
            option4="Gravity",
            correct_answer="Inertia"
        )
        
        assert question.validate_answer("Inertia") is True
        assert question.validate_answer("inertia") is True  # Case insensitive

    def test_validate_answer_incorrect(self) -> None:
        """Test validating incorrect answer."""
        question = ConcreteChoiceQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            difficulty="Easy",
            option1="Inertia",
            option2="F=ma",
            option3="Action-reaction",
            option4="Gravity",
            correct_answer="Inertia"
        )
        
        assert question.validate_answer("F=ma") is False

    def test_has_multiple_correct_answers(self) -> None:
        """Test checking for multiple correct answers."""
        single_answer = ConcreteChoiceQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            difficulty="Easy",
            option1="Inertia",
            option2="F=ma",
            option3="Action-reaction",
            option4="Gravity",
            correct_answer="Inertia"
        )
        
        multiple_answers = ConcreteChoiceQuestion(
            id="test_2",
            topic="Physics",
            question_text="Which are Newton's laws?",
            difficulty="Easy",
            option1="Inertia",
            option2="F=ma",
            option3="Action-reaction",
            option4="Gravity",
            correct_answer="Inertia, F=ma"
        )
        
        assert single_answer.has_multiple_correct_answers() is False
        assert multiple_answers.has_multiple_correct_answers() is True

    def test_get_correct_answers_list(self) -> None:
        """Test getting list of correct answers."""
        question = ConcreteChoiceQuestion(
            id="test_1",
            topic="Physics",
            question_text="Which are Newton's laws?",
            difficulty="Easy",
            option1="Inertia",
            option2="F=ma",
            option3="Action-reaction",
            option4="Gravity",
            correct_answer="Inertia, F=ma"
        )
        
        answers = question.get_correct_answers_list()
        
        assert len(answers) == 2
        assert "Inertia" in answers
        assert "F=ma" in answers

    def test_empty_correct_answer_raises_error(self) -> None:
        """Test that empty correct answer raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ConcreteChoiceQuestion(
                id="test_1",
                topic="Physics",
                question_text="What is Newton's first law?",
                difficulty="Easy",
                option1="Inertia",
                option2="F=ma",
                option3="Action-reaction",
                option4="Gravity",
                correct_answer=""
            )
        
        assert "Correct answer cannot be empty" in str(exc_info.value)

    def test_too_few_options_raises_error(self) -> None:
        """Test that too few options raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ConcreteChoiceQuestion(
                id="test_1",
                topic="Physics",
                question_text="What is Newton's first law?",
                difficulty="Easy",
                option1="Inertia",
                option2=None,
                option3=None,
                option4=None,
                correct_answer="Inertia"
            )
        
        assert "at least 2 options" in str(exc_info.value)


class TestTextBasedQuestion:
    """Unit tests for TextBasedQuestion class."""

    def test_create_text_question(self) -> None:
        """Test creating a text-based question."""
        question = ConcreteTextQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is the formula for force?",
            difficulty="Medium",
            expected_answer="F=ma",
            case_sensitive=False
        )
        
        assert question.id == "test_1"
        assert question.expected_answer == "F=ma"
        assert question.case_sensitive is False

    def test_validate_answer_case_insensitive(self) -> None:
        """Test validating answer case insensitively."""
        question = ConcreteTextQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is the formula for force?",
            difficulty="Medium",
            expected_answer="F=ma",
            case_sensitive=False
        )
        
        assert question.validate_answer("F=ma") is True
        assert question.validate_answer("f=ma") is True
        assert question.validate_answer("F=MA") is True

    def test_validate_answer_case_sensitive(self) -> None:
        """Test validating answer case sensitively."""
        question = ConcreteTextQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is the formula for force?",
            difficulty="Medium",
            expected_answer="F=ma",
            case_sensitive=True
        )
        
        assert question.validate_answer("F=ma") is True
        assert question.validate_answer("f=ma") is False
        assert question.validate_answer("F=MA") is False

    def test_get_display_format(self) -> None:
        """Test get_display_format method."""
        question = ConcreteTextQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is the formula for force?",
            difficulty="Medium",
            expected_answer="F=ma",
            case_sensitive=True
        )
        
        display = question.get_display_format()
        
        assert display["case_sensitive"] is True

    def test_difficulty_score_higher_than_choice(self) -> None:
        """Test that text-based questions have higher difficulty score."""
        text_question = ConcreteTextQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is the formula for force?",
            difficulty="Medium",
            expected_answer="F=ma"
        )
        
        choice_question = ConcreteChoiceQuestion(
            id="test_2",
            topic="Physics",
            question_text="What is the formula for force?",
            difficulty="Medium",
            option1="F=ma",
            option2="E=mc2",
            option3="V=IR",
            option4="P=IV",
            correct_answer="F=ma"
        )
        
        # Text-based should have 1.2x multiplier
        assert text_question.calculate_difficulty_score() > choice_question.calculate_difficulty_score()

    def test_get_question_type(self) -> None:
        """Test get_question_type method."""
        question = ConcreteTextQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is the formula for force?",
            difficulty="Medium",
            expected_answer="F=ma"
        )
        
        assert question.get_question_type() == "text_input"
