"""
Unit tests for Question entity validation.

Tests the Question model validation following TDD approach.
These tests should FAIL initially and PASS after implementation.
"""

import pytest
from src.models.question import Question
from src.utils.exceptions import ValidationError


class TestQuestionEntityValidation:
    """
    Unit tests for Question entity validation.
    
    Tests validation rules and business logic for the Question model.
    """
    
    def test_valid_question_creation(self) -> None:
        """
        Test creating a valid question.
        
        GIVEN valid question data
        WHEN a Question instance is created
        THEN it should be created successfully
        """
        question = Question(
            id="physics_1",
            topic="Physics",
            question_text="What is the speed of light?",
            option1="299,792,458 m/s",
            option2="150,000,000 m/s",
            option3="3,000,000 m/s",
            option4="1,000,000 m/s",
            correct_answer="299,792,458 m/s",
            difficulty="Easy",
            tag="Physics-Easy"
        )
        
        assert question.id == "physics_1"
        assert question.topic == "Physics"
        assert question.difficulty == "Easy"
        assert question.tag == "Physics-Easy"
        assert question.asked_in_session is False
        assert question.got_right is False
    
    def test_question_validation_invalid_topic(self) -> None:
        """
        Test question validation with invalid topic.
        
        GIVEN question data with invalid topic
        WHEN a Question instance is created
        THEN it should raise ValidationError
        """
        with pytest.raises(ValidationError) as exc_info:
            Question(
                id="invalid_1",
                topic="InvalidTopic",
                question_text="What is the speed of light?",
                option1="299,792,458 m/s",
                option2="150,000,000 m/s",
                option3="3,000,000 m/s",
                option4="1,000,000 m/s",
                correct_answer="299,792,458 m/s",
                difficulty="Easy",
                tag="InvalidTopic-Easy"
            )
        
        assert "Invalid topic" in str(exc_info.value)
        assert exc_info.value.field == "topic"
    
    def test_question_validation_invalid_difficulty(self) -> None:
        """
        Test question validation with invalid difficulty.
        
        GIVEN question data with invalid difficulty
        WHEN a Question instance is created
        THEN it should raise ValidationError
        """
        with pytest.raises(ValidationError) as exc_info:
            Question(
                id="physics_1",
                topic="Physics",
                question_text="What is the speed of light?",
                option1="299,792,458 m/s",
                option2="150,000,000 m/s",
                option3="3,000,000 m/s",
                option4="1,000,000 m/s",
                correct_answer="299,792,458 m/s",
                difficulty="InvalidDifficulty",
                tag="Physics-InvalidDifficulty"
            )
        
        assert "Invalid difficulty" in str(exc_info.value)
        assert exc_info.value.field == "difficulty"
    
    def test_question_validation_empty_question_text(self) -> None:
        """
        Test question validation with empty question text.
        
        GIVEN question data with empty question text
        WHEN a Question instance is created
        THEN it should raise ValidationError
        """
        with pytest.raises(ValidationError) as exc_info:
            Question(
                id="physics_1",
                topic="Physics",
                question_text="",
                option1="299,792,458 m/s",
                option2="150,000,000 m/s",
                option3="3,000,000 m/s",
                option4="1,000,000 m/s",
                correct_answer="299,792,458 m/s",
                difficulty="Easy",
                tag="Physics-Easy"
            )
        
        assert "Question text cannot be empty" in str(exc_info.value)
        assert exc_info.value.field == "question_text"
    
    def test_question_validation_short_question_text(self) -> None:
        """
        Test question validation with short question text.
        
        GIVEN question data with question text shorter than 10 characters
        WHEN a Question instance is created
        THEN it should raise ValidationError
        """
        with pytest.raises(ValidationError) as exc_info:
            Question(
                id="physics_1",
                topic="Physics",
                question_text="Short?",
                option1="299,792,458 m/s",
                option2="150,000,000 m/s",
                option3="3,000,000 m/s",
                option4="1,000,000 m/s",
                correct_answer="299,792,458 m/s",
                difficulty="Easy",
                tag="Physics-Easy"
            )
        
        assert "Question text must be at least 10 characters long" in str(exc_info.value)
        assert exc_info.value.field == "question_text"
    
    def test_question_validation_empty_option(self) -> None:
        """
        Test question validation with empty option.
        
        GIVEN question data with an empty option
        WHEN a Question instance is created
        THEN it should raise ValidationError
        """
        with pytest.raises(ValidationError) as exc_info:
            Question(
                id="physics_1",
                topic="Physics",
                question_text="What is the speed of light?",
                option1="",
                option2="150,000,000 m/s",
                option3="3,000,000 m/s",
                option4="1,000,000 m/s",
                correct_answer="299,792,458 m/s",
                difficulty="Easy",
                tag="Physics-Easy"
            )
        
        assert "Option 1 cannot be empty" in str(exc_info.value)
    
    def test_question_validation_duplicate_options(self) -> None:
        """
        Test question validation with duplicate options.
        
        GIVEN question data with duplicate options
        WHEN a Question instance is created
        THEN it should raise ValidationError
        """
        with pytest.raises(ValidationError) as exc_info:
            Question(
                id="physics_1",
                topic="Physics",
                question_text="What is the speed of light?",
                option1="299,792,458 m/s",
                option2="299,792,458 m/s",  # Duplicate
                option3="3,000,000 m/s",
                option4="1,000,000 m/s",
                correct_answer="299,792,458 m/s",
                difficulty="Easy",
                tag="Physics-Easy"
            )
        
        assert "All options must be unique" in str(exc_info.value)
    
    def test_question_validation_correct_answer_not_in_options(self) -> None:
        """
        Test question validation with correct answer not in options.
        
        GIVEN question data where correct answer doesn't match any option
        WHEN a Question instance is created
        THEN it should raise ValidationError
        """
        with pytest.raises(ValidationError) as exc_info:
            Question(
                id="physics_1",
                topic="Physics",
                question_text="What is the speed of light?",
                option1="299,792,458 m/s",
                option2="150,000,000 m/s",
                option3="3,000,000 m/s",
                option4="1,000,000 m/s",
                correct_answer="Wrong Answer",
                difficulty="Easy",
                tag="Physics-Easy"
            )
        
        assert "Correct answer" in str(exc_info.value)
        assert "must match one of the options" in str(exc_info.value)
        assert exc_info.value.field == "correct_answer"
    
    def test_question_validation_invalid_tag(self) -> None:
        """
        Test question validation with invalid tag.
        
        GIVEN question data with incorrect tag format
        WHEN a Question instance is created
        THEN it should raise ValidationError
        """
        with pytest.raises(ValidationError) as exc_info:
            Question(
                id="physics_1",
                topic="Physics",
                question_text="What is the speed of light?",
                option1="299,792,458 m/s",
                option2="150,000,000 m/s",
                option3="3,000,000 m/s",
                option4="1,000,000 m/s",
                correct_answer="299,792,458 m/s",
                difficulty="Easy",
                tag="Wrong-Tag"
            )
        
        assert "Tag" in str(exc_info.value)
        assert "should match" in str(exc_info.value)
        assert exc_info.value.field == "tag"
    
    def test_question_is_correct_answer(self) -> None:
        """
        Test answer validation functionality.
        
        GIVEN a valid question
        WHEN answers are checked
        THEN correct answers should return True, incorrect should return False
        """
        question = Question(
            id="physics_1",
            topic="Physics",
            question_text="What is the speed of light?",
            option1="299,792,458 m/s",
            option2="150,000,000 m/s",
            option3="3,000,000 m/s",
            option4="1,000,000 m/s",
            correct_answer="299,792,458 m/s",
            difficulty="Easy",
            tag="Physics-Easy"
        )
        
        # Test correct answer
        assert question.is_correct_answer("299,792,458 m/s") is True
        
        # Test incorrect answer
        assert question.is_correct_answer("150,000,000 m/s") is False
        
        # Test answer with extra whitespace
        assert question.is_correct_answer(" 299,792,458 m/s ") is True
    
    def test_question_mark_as_asked(self) -> None:
        """
        Test marking question as asked in session.
        
        GIVEN a valid question
        WHEN mark_as_asked is called
        THEN asked_in_session should be True
        """
        question = Question(
            id="physics_1",
            topic="Physics",
            question_text="What is the speed of light?",
            option1="299,792,458 m/s",
            option2="150,000,000 m/s",
            option3="3,000,000 m/s",
            option4="1,000,000 m/s",
            correct_answer="299,792,458 m/s",
            difficulty="Easy",
            tag="Physics-Easy"
        )
        
        assert question.asked_in_session is False
        
        question.mark_as_asked()
        assert question.asked_in_session is True
        assert question.updated_at is not None
    
    def test_question_mark_as_answered(self) -> None:
        """
        Test marking question as answered with result.
        
        GIVEN a question that has been asked
        WHEN mark_as_answered is called
        THEN got_right should be set appropriately
        """
        question = Question(
            id="physics_1",
            topic="Physics",
            question_text="What is the speed of light?",
            option1="299,792,458 m/s",
            option2="150,000,000 m/s",
            option3="3,000,000 m/s",
            option4="1,000,000 m/s",
            correct_answer="299,792,458 m/s",
            difficulty="Easy",
            tag="Physics-Easy"
        )
        
        question.mark_as_asked()
        
        # Mark as answered correctly
        question.mark_as_answered(True)
        assert question.got_right is True
        assert question.updated_at is not None
        
        # Reset and mark as answered incorrectly
        question.reset_session_state()
        question.mark_as_asked()
        question.mark_as_answered(False)
        assert question.got_right is False
    
    def test_question_mark_as_answered_without_asking(self) -> None:
        """
        Test marking question as answered without asking first.
        
        GIVEN a question that hasn't been asked
        WHEN mark_as_answered is called
        THEN it should raise ValidationError
        """
        question = Question(
            id="physics_1",
            topic="Physics",
            question_text="What is the speed of light?",
            option1="299,792,458 m/s",
            option2="150,000,000 m/s",
            option3="3,000,000 m/s",
            option4="1,000,000 m/s",
            correct_answer="299,792,458 m/s",
            difficulty="Easy",
            tag="Physics-Easy"
        )
        
        with pytest.raises(ValidationError) as exc_info:
            question.mark_as_answered(True)
        
        assert "Cannot mark as answered before question is asked" in str(exc_info.value)
    
    def test_question_get_options(self) -> None:
        """
        Test getting options as list.
        
        GIVEN a valid question
        WHEN get_options is called
        THEN it should return a list of all options
        """
        question = Question(
            id="physics_1",
            topic="Physics",
            question_text="What is the speed of light?",
            option1="299,792,458 m/s",
            option2="150,000,000 m/s",
            option3="3,000,000 m/s",
            option4="1,000,000 m/s",
            correct_answer="299,792,458 m/s",
            difficulty="Easy",
            tag="Physics-Easy"
        )
        
        options = question.get_options()
        expected_options = [
            "299,792,458 m/s",
            "150,000,000 m/s",
            "3,000,000 m/s",
            "1,000,000 m/s"
        ]
        
        assert options == expected_options
        assert len(options) == 4
    
    def test_question_reset_session_state(self) -> None:
        """
        Test resetting session state.
        
        GIVEN a question with session state
        WHEN reset_session_state is called
        THEN session state should be reset to defaults
        """
        question = Question(
            id="physics_1",
            topic="Physics",
            question_text="What is the speed of light?",
            option1="299,792,458 m/s",
            option2="150,000,000 m/s",
            option3="3,000,000 m/s",
            option4="1,000,000 m/s",
            correct_answer="299,792,458 m/s",
            difficulty="Easy",
            tag="Physics-Easy"
        )
        
        # Set session state
        question.mark_as_asked()
        question.mark_as_answered(True)
        
        assert question.asked_in_session is True
        assert question.got_right is True
        
        # Reset session state
        question.reset_session_state()
        assert question.asked_in_session is False
        assert question.got_right is False
        assert question.updated_at is not None


class TestQuestionStringRepresentations:
    """Unit tests for Question string representations."""

    @pytest.fixture
    def sample_question(self) -> Question:
        """Create a sample question."""
        return Question(
            id="physics_1",
            topic="Physics",
            question_text="What is Newton's first law of motion?",
            option1="Inertia",
            option2="F=ma",
            option3="Action-reaction",
            option4="Gravity",
            correct_answer="Inertia",
            difficulty="Easy",
            tag="Physics-Easy"
        )

    def test_str_representation(self, sample_question: Question) -> None:
        """Test __str__ method."""
        str_repr = str(sample_question)
        
        assert "physics_1" in str_repr
        assert "Physics" in str_repr
        assert "Easy" in str_repr

    def test_repr_representation(self, sample_question: Question) -> None:
        """Test __repr__ method."""
        repr_str = repr(sample_question)
        
        assert "physics_1" in repr_str
        assert "Physics" in repr_str


class TestQuestionEquality:
    """Unit tests for Question equality and hashing."""

    def test_equality_same_id(self) -> None:
        """Test that questions with same ID are equal."""
        q1 = Question(
            id="q_1",
            topic="Physics",
            question_text="Question 1?",
            option1="A",
            option2="B",
            option3="C",
            option4="D",
            correct_answer="A",
            difficulty="Easy",
            tag="Physics-Easy"
        )
        q2 = Question(
            id="q_1",
            topic="Physics",
            question_text="Different text?",
            option1="A",
            option2="B",
            option3="C",
            option4="D",
            correct_answer="A",
            difficulty="Easy",
            tag="Physics-Easy"
        )
        
        assert q1 == q2

    def test_equality_different_id(self) -> None:
        """Test that questions with different IDs are not equal."""
        q1 = Question(
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
        q2 = Question(
            id="q_2",
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
        
        assert q1 != q2

    def test_equality_with_non_question(self) -> None:
        """Test equality with non-Question object."""
        q = Question(
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
        
        assert q != "not a question"
        assert q != 123

    def test_hash_same_id(self) -> None:
        """Test that questions with same ID have same hash."""
        q1 = Question(
            id="q_1",
            topic="Physics",
            question_text="Question 1?",
            option1="A",
            option2="B",
            option3="C",
            option4="D",
            correct_answer="A",
            difficulty="Easy",
            tag="Physics-Easy"
        )
        q2 = Question(
            id="q_1",
            topic="Chemistry",
            question_text="Question 2?",
            option1="A",
            option2="B",
            option3="C",
            option4="D",
            correct_answer="A",
            difficulty="Hard",
            tag="Chemistry-Hard"
        )
        
        assert hash(q1) == hash(q2)

    def test_questions_in_set(self) -> None:
        """Test that questions can be used in sets."""
        q1 = Question(
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
        q2 = Question(
            id="q_1",
            topic="Physics",
            question_text="What is Newton's second law?",
            option1="Inertia",
            option2="F=ma",
            option3="Action-reaction",
            option4="Gravity",
            correct_answer="Inertia",
            difficulty="Easy",
            tag="Physics-Easy"
        )
        
        question_set = {q1, q2}
        assert len(question_set) == 1


class TestQuestionGetOptions:
    """Unit tests for get_options method."""

    def test_get_options(self) -> None:
        """Test get_options returns all options."""
        q = Question(
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
        
        options = q.get_options()
        
        assert len(options) == 4
        assert "Inertia" in options
        assert "F=ma" in options
        assert "Action-reaction" in options
        assert "Gravity" in options
