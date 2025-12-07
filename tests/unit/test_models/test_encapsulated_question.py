"""
Unit tests for encapsulated question models.

Tests encapsulation, data protection, and secure access patterns.
"""

import pytest
from typing import Dict, Any, List
from datetime import datetime

from src.models.encapsulated_question import EncapsulatedQuestion, SecureQuestionManager
from src.utils.exceptions import ValidationError, QuestionError


class TestEncapsulatedQuestionCreation:
    """Unit tests for EncapsulatedQuestion creation and validation."""

    def test_create_valid_question(self) -> None:
        """Test creating a valid encapsulated question."""
        question = EncapsulatedQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            correct_answer="Inertia",
            difficulty="Easy",
            options=["Inertia", "F=ma", "Action-reaction", "Gravity"],
            tag="Physics-Easy"
        )
        
        assert question.get_id() == "test_1"
        assert question.get_topic() == "Physics"
        assert question.get_question_text() == "What is Newton's first law?"
        assert question.get_difficulty() == "Easy"

    def test_create_question_without_options(self) -> None:
        """Test creating question without options."""
        question = EncapsulatedQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            correct_answer="Inertia"
        )
        
        assert question.get_options() == []

    def test_create_question_default_difficulty(self) -> None:
        """Test creating question with default difficulty."""
        question = EncapsulatedQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            correct_answer="Inertia"
        )
        
        assert question.get_difficulty() == "Medium"

    def test_empty_id_raises_error(self) -> None:
        """Test that empty ID raises ValidationError."""
        with pytest.raises(ValidationError):
            EncapsulatedQuestion(
                id="",
                topic="Physics",
                question_text="What is Newton's first law?",
                correct_answer="Inertia"
            )

    def test_invalid_topic_raises_error(self) -> None:
        """Test that invalid topic raises ValidationError."""
        with pytest.raises(ValidationError):
            EncapsulatedQuestion(
                id="test_1",
                topic="InvalidTopic",
                question_text="What is Newton's first law?",
                correct_answer="Inertia"
            )

    def test_empty_question_text_raises_error(self) -> None:
        """Test that empty question text raises ValidationError."""
        with pytest.raises(ValidationError):
            EncapsulatedQuestion(
                id="test_1",
                topic="Physics",
                question_text="",
                correct_answer="Inertia"
            )

    def test_question_text_too_long_raises_error(self) -> None:
        """Test that question text over 1000 chars raises ValidationError."""
        with pytest.raises(ValidationError):
            EncapsulatedQuestion(
                id="test_1",
                topic="Physics",
                question_text="x" * 1001,
                correct_answer="Inertia"
            )

    def test_empty_correct_answer_raises_error(self) -> None:
        """Test that empty correct answer raises ValidationError."""
        with pytest.raises(ValidationError):
            EncapsulatedQuestion(
                id="test_1",
                topic="Physics",
                question_text="What is Newton's first law?",
                correct_answer=""
            )

    def test_invalid_difficulty_raises_error(self) -> None:
        """Test that invalid difficulty raises ValidationError."""
        with pytest.raises(ValidationError):
            EncapsulatedQuestion(
                id="test_1",
                topic="Physics",
                question_text="What is Newton's first law?",
                correct_answer="Inertia",
                difficulty="VeryHard"
            )


class TestEncapsulatedQuestionGetters:
    """Unit tests for EncapsulatedQuestion getter methods."""

    @pytest.fixture
    def sample_question(self) -> EncapsulatedQuestion:
        """Create a sample question for testing."""
        return EncapsulatedQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            correct_answer="Inertia",
            difficulty="Easy",
            options=["Inertia", "F=ma", "Action-reaction", "Gravity"],
            tag="Physics-Easy"
        )

    def test_get_id(self, sample_question: EncapsulatedQuestion) -> None:
        """Test get_id method."""
        assert sample_question.get_id() == "test_1"

    def test_get_topic(self, sample_question: EncapsulatedQuestion) -> None:
        """Test get_topic method."""
        assert sample_question.get_topic() == "Physics"

    def test_get_question_text(self, sample_question: EncapsulatedQuestion) -> None:
        """Test get_question_text method."""
        assert sample_question.get_question_text() == "What is Newton's first law?"

    def test_get_correct_answer(self, sample_question: EncapsulatedQuestion) -> None:
        """Test get_correct_answer method."""
        assert sample_question.get_correct_answer() == "Inertia"

    def test_get_correct_answer_with_auth_raises_error(self, sample_question: EncapsulatedQuestion) -> None:
        """Test get_correct_answer with auth requirement raises error."""
        with pytest.raises(QuestionError):
            sample_question.get_correct_answer(require_auth=True)

    def test_get_difficulty(self, sample_question: EncapsulatedQuestion) -> None:
        """Test get_difficulty method."""
        assert sample_question.get_difficulty() == "Easy"

    def test_get_options(self, sample_question: EncapsulatedQuestion) -> None:
        """Test get_options method returns copy."""
        options = sample_question.get_options()
        assert options == ["Inertia", "F=ma", "Action-reaction", "Gravity"]
        
        # Verify it's a copy
        options.append("New Option")
        assert sample_question.get_options() == ["Inertia", "F=ma", "Action-reaction", "Gravity"]

    def test_get_tag(self, sample_question: EncapsulatedQuestion) -> None:
        """Test get_tag method."""
        assert sample_question.get_tag() == "Physics-Easy"

    def test_get_created_at(self, sample_question: EncapsulatedQuestion) -> None:
        """Test get_created_at method."""
        created_at = sample_question.get_created_at()
        assert isinstance(created_at, datetime)

    def test_get_updated_at(self, sample_question: EncapsulatedQuestion) -> None:
        """Test get_updated_at method."""
        updated_at = sample_question.get_updated_at()
        assert isinstance(updated_at, datetime)

    def test_get_access_count(self, sample_question: EncapsulatedQuestion) -> None:
        """Test get_access_count method."""
        initial_count = sample_question.get_access_count()
        sample_question.get_id()
        sample_question.get_topic()
        assert sample_question.get_access_count() == initial_count + 2

    def test_is_active(self, sample_question: EncapsulatedQuestion) -> None:
        """Test is_active method."""
        assert sample_question.is_active() is True

    def test_get_metadata_all(self, sample_question: EncapsulatedQuestion) -> None:
        """Test get_metadata returns all metadata."""
        metadata = sample_question.get_metadata()
        assert isinstance(metadata, dict)

    def test_get_metadata_specific_key(self, sample_question: EncapsulatedQuestion) -> None:
        """Test get_metadata with specific key."""
        sample_question.set_metadata("test_key", "test_value")
        assert sample_question.get_metadata("test_key") == "test_value"


class TestEncapsulatedQuestionSetters:
    """Unit tests for EncapsulatedQuestion setter methods."""

    @pytest.fixture
    def sample_question(self) -> EncapsulatedQuestion:
        """Create a sample question for testing."""
        return EncapsulatedQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            correct_answer="Inertia",
            difficulty="Easy",
            options=["Inertia", "F=ma", "Action-reaction", "Gravity"],
            tag="Physics-Easy"
        )

    def test_set_topic(self, sample_question: EncapsulatedQuestion) -> None:
        """Test set_topic method."""
        sample_question.set_topic("Chemistry")
        assert sample_question.get_topic() == "Chemistry"

    def test_set_topic_invalid_raises_error(self, sample_question: EncapsulatedQuestion) -> None:
        """Test set_topic with invalid topic raises error."""
        with pytest.raises(ValidationError):
            sample_question.set_topic("InvalidTopic")

    def test_set_question_text(self, sample_question: EncapsulatedQuestion) -> None:
        """Test set_question_text method."""
        sample_question.set_question_text("What is the speed of light?")
        assert sample_question.get_question_text() == "What is the speed of light?"

    def test_set_correct_answer(self, sample_question: EncapsulatedQuestion) -> None:
        """Test set_correct_answer method."""
        sample_question.set_correct_answer("F=ma")
        assert sample_question.get_correct_answer() == "F=ma"

    def test_set_correct_answer_with_auth_raises_error(self, sample_question: EncapsulatedQuestion) -> None:
        """Test set_correct_answer with auth requirement raises error."""
        with pytest.raises(QuestionError):
            sample_question.set_correct_answer("F=ma", require_auth=True)

    def test_set_difficulty(self, sample_question: EncapsulatedQuestion) -> None:
        """Test set_difficulty method."""
        sample_question.set_difficulty("Hard")
        assert sample_question.get_difficulty() == "Hard"

    def test_set_options(self, sample_question: EncapsulatedQuestion) -> None:
        """Test set_options method."""
        new_options = ["A", "B", "C", "D"]
        sample_question.set_options(new_options)
        assert sample_question.get_options() == new_options

    def test_set_tag(self, sample_question: EncapsulatedQuestion) -> None:
        """Test set_tag method."""
        sample_question.set_tag("Physics-Hard")
        assert sample_question.get_tag() == "Physics-Hard"

    def test_set_tag_none(self, sample_question: EncapsulatedQuestion) -> None:
        """Test set_tag with None."""
        sample_question.set_tag(None)
        assert sample_question.get_tag() is None

    def test_set_metadata(self, sample_question: EncapsulatedQuestion) -> None:
        """Test set_metadata method."""
        sample_question.set_metadata("author", "Test Author")
        assert sample_question.get_metadata("author") == "Test Author"

    def test_set_metadata_invalid_key_raises_error(self, sample_question: EncapsulatedQuestion) -> None:
        """Test set_metadata with invalid key raises error."""
        with pytest.raises(ValidationError):
            sample_question.set_metadata("", "value")


class TestEncapsulatedQuestionActivation:
    """Unit tests for EncapsulatedQuestion activation/deactivation."""

    @pytest.fixture
    def sample_question(self) -> EncapsulatedQuestion:
        """Create a sample question for testing."""
        return EncapsulatedQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            correct_answer="Inertia"
        )

    def test_deactivate(self, sample_question: EncapsulatedQuestion) -> None:
        """Test deactivate method."""
        assert sample_question.is_active() is True
        sample_question.deactivate()
        assert sample_question.is_active() is False

    def test_activate(self, sample_question: EncapsulatedQuestion) -> None:
        """Test activate method."""
        sample_question.deactivate()
        assert sample_question.is_active() is False
        sample_question.activate()
        assert sample_question.is_active() is True

    def test_activate_already_active(self, sample_question: EncapsulatedQuestion) -> None:
        """Test activate when already active."""
        assert sample_question.is_active() is True
        sample_question.activate()
        assert sample_question.is_active() is True

    def test_deactivate_already_inactive(self, sample_question: EncapsulatedQuestion) -> None:
        """Test deactivate when already inactive."""
        sample_question.deactivate()
        sample_question.deactivate()
        assert sample_question.is_active() is False


class TestEncapsulatedQuestionBusinessMethods:
    """Unit tests for EncapsulatedQuestion business methods."""

    @pytest.fixture
    def sample_question(self) -> EncapsulatedQuestion:
        """Create a sample question for testing."""
        return EncapsulatedQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            correct_answer="Inertia",
            difficulty="Easy",
            options=["Inertia", "F=ma", "Action-reaction", "Gravity"],
            tag="Physics-Easy"
        )

    def test_validate_answer_correct(self, sample_question: EncapsulatedQuestion) -> None:
        """Test validate_answer with correct answer."""
        assert sample_question.validate_answer("Inertia") is True

    def test_validate_answer_correct_case_insensitive(self, sample_question: EncapsulatedQuestion) -> None:
        """Test validate_answer is case insensitive."""
        assert sample_question.validate_answer("inertia") is True
        assert sample_question.validate_answer("INERTIA") is True

    def test_validate_answer_incorrect(self, sample_question: EncapsulatedQuestion) -> None:
        """Test validate_answer with incorrect answer."""
        assert sample_question.validate_answer("F=ma") is False

    def test_validate_answer_empty(self, sample_question: EncapsulatedQuestion) -> None:
        """Test validate_answer with empty answer."""
        assert sample_question.validate_answer("") is False

    def test_validate_answer_none(self, sample_question: EncapsulatedQuestion) -> None:
        """Test validate_answer with None."""
        assert sample_question.validate_answer(None) is False

    def test_get_display_format_hide_answer(self, sample_question: EncapsulatedQuestion) -> None:
        """Test get_display_format with hidden answer."""
        display = sample_question.get_display_format(hide_answer=True)
        
        assert display["id"] == "test_1"
        assert display["topic"] == "Physics"
        assert display["question_text"] == "What is Newton's first law?"
        assert "correct_answer" not in display

    def test_get_display_format_show_answer(self, sample_question: EncapsulatedQuestion) -> None:
        """Test get_display_format with shown answer."""
        display = sample_question.get_display_format(hide_answer=False)
        
        assert display["correct_answer"] == "Inertia"

    def test_get_access_statistics(self, sample_question: EncapsulatedQuestion) -> None:
        """Test get_access_statistics method."""
        sample_question.get_id()
        sample_question.get_topic()
        
        stats = sample_question.get_access_statistics()
        
        assert "total_access" in stats
        assert "field_access" in stats
        assert stats["total_access"] >= 2

    def test_reset_access_statistics(self, sample_question: EncapsulatedQuestion) -> None:
        """Test reset_access_statistics method."""
        sample_question.get_id()
        sample_question.get_topic()
        sample_question.reset_access_statistics()
        
        assert sample_question.get_access_count() == 0

    def test_clone(self, sample_question: EncapsulatedQuestion) -> None:
        """Test clone method."""
        cloned = sample_question.clone("cloned_1")
        
        assert cloned.get_id() == "cloned_1"
        assert cloned.get_topic() == sample_question.get_topic()
        assert cloned.get_question_text() == sample_question.get_question_text()
        assert cloned.get_correct_answer() == sample_question.get_correct_answer()

    def test_str_representation(self, sample_question: EncapsulatedQuestion) -> None:
        """Test __str__ method."""
        str_repr = str(sample_question)
        assert "test_1" in str_repr
        assert "Physics" in str_repr

    def test_repr_representation(self, sample_question: EncapsulatedQuestion) -> None:
        """Test __repr__ method."""
        repr_str = repr(sample_question)
        assert "test_1" in repr_str
        assert "Physics" in repr_str


class TestSecureQuestionManager:
    """Unit tests for SecureQuestionManager."""

    @pytest.fixture
    def manager(self) -> SecureQuestionManager:
        """Create a manager for testing."""
        return SecureQuestionManager()

    @pytest.fixture
    def sample_question(self) -> EncapsulatedQuestion:
        """Create a sample question for testing."""
        return EncapsulatedQuestion(
            id="test_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            correct_answer="Inertia",
            difficulty="Easy"
        )

    def test_add_question(self, manager: SecureQuestionManager, sample_question: EncapsulatedQuestion) -> None:
        """Test add_question method."""
        manager.add_question(sample_question)
        
        result = manager.get_question("test_1")
        assert result is not None
        assert result["id"] == "test_1"

    def test_add_question_invalid_type_raises_error(self, manager: SecureQuestionManager) -> None:
        """Test add_question with invalid type raises error."""
        with pytest.raises(ValidationError):
            manager.add_question("not a question")

    def test_add_question_duplicate_id_raises_error(self, manager: SecureQuestionManager, sample_question: EncapsulatedQuestion) -> None:
        """Test add_question with duplicate ID raises error."""
        manager.add_question(sample_question)
        
        with pytest.raises(ValidationError):
            manager.add_question(sample_question)

    def test_get_question_not_found(self, manager: SecureQuestionManager) -> None:
        """Test get_question with non-existent ID."""
        result = manager.get_question("nonexistent")
        assert result is None

    def test_get_question_inactive(self, manager: SecureQuestionManager, sample_question: EncapsulatedQuestion) -> None:
        """Test get_question with inactive question."""
        sample_question.deactivate()
        manager.add_question(sample_question)
        
        result = manager.get_question("test_1")
        assert result is None

    def test_get_question_hide_answer(self, manager: SecureQuestionManager, sample_question: EncapsulatedQuestion) -> None:
        """Test get_question hides answer by default."""
        manager.add_question(sample_question)
        
        result = manager.get_question("test_1")
        assert "correct_answer" not in result

    def test_get_question_show_answer(self, manager: SecureQuestionManager, sample_question: EncapsulatedQuestion) -> None:
        """Test get_question can show answer."""
        manager.add_question(sample_question)
        
        result = manager.get_question("test_1", hide_answer=False)
        assert "correct_answer" in result

    def test_update_question(self, manager: SecureQuestionManager, sample_question: EncapsulatedQuestion) -> None:
        """Test update_question method."""
        manager.add_question(sample_question)
        
        result = manager.update_question("test_1", {"topic": "Chemistry"})
        assert result is True
        
        updated = manager.get_question("test_1")
        assert updated["topic"] == "Chemistry"

    def test_update_question_not_found(self, manager: SecureQuestionManager) -> None:
        """Test update_question with non-existent ID."""
        result = manager.update_question("nonexistent", {"topic": "Chemistry"})
        assert result is False

    def test_update_question_invalid_field(self, manager: SecureQuestionManager, sample_question: EncapsulatedQuestion) -> None:
        """Test update_question with invalid field."""
        manager.add_question(sample_question)
        
        # Should not raise, just log warning
        result = manager.update_question("test_1", {"invalid_field": "value"})
        assert result is True

    def test_update_question_invalid_value(self, manager: SecureQuestionManager, sample_question: EncapsulatedQuestion) -> None:
        """Test update_question with invalid value."""
        manager.add_question(sample_question)
        
        result = manager.update_question("test_1", {"topic": "InvalidTopic"})
        assert result is False

    def test_delete_question(self, manager: SecureQuestionManager, sample_question: EncapsulatedQuestion) -> None:
        """Test delete_question method."""
        manager.add_question(sample_question)
        
        result = manager.delete_question("test_1")
        assert result is True
        
        assert manager.get_question("test_1") is None

    def test_delete_question_not_found(self, manager: SecureQuestionManager) -> None:
        """Test delete_question with non-existent ID."""
        result = manager.delete_question("nonexistent")
        assert result is False

    def test_delete_question_with_auth_raises_error(self, manager: SecureQuestionManager, sample_question: EncapsulatedQuestion) -> None:
        """Test delete_question with auth requirement raises error."""
        manager.add_question(sample_question)
        
        with pytest.raises(QuestionError):
            manager.delete_question("test_1", require_auth=True)

    def test_get_statistics(self, manager: SecureQuestionManager) -> None:
        """Test get_statistics method."""
        q1 = EncapsulatedQuestion(
            id="q1", topic="Physics", question_text="Question 1?", 
            correct_answer="A", difficulty="Easy"
        )
        q2 = EncapsulatedQuestion(
            id="q2", topic="Chemistry", question_text="Question 2?", 
            correct_answer="B", difficulty="Hard"
        )
        
        manager.add_question(q1)
        manager.add_question(q2)
        
        stats = manager.get_statistics()
        
        assert stats["total_questions"] == 2
        assert stats["active_questions"] == 2
        assert "topic_distribution" in stats
        assert "difficulty_distribution" in stats

    def test_get_statistics_with_inactive(self, manager: SecureQuestionManager) -> None:
        """Test get_statistics with inactive questions."""
        q1 = EncapsulatedQuestion(
            id="q1", topic="Physics", question_text="Question 1?", 
            correct_answer="A"
        )
        q2 = EncapsulatedQuestion(
            id="q2", topic="Chemistry", question_text="Question 2?", 
            correct_answer="B"
        )
        q2.deactivate()
        
        manager.add_question(q1)
        manager.add_question(q2)
        
        stats = manager.get_statistics()
        
        assert stats["total_questions"] == 2
        assert stats["active_questions"] == 1
        assert stats["inactive_questions"] == 1
