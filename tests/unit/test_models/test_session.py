"""
Unit tests for UserSession entity initialization.

Tests the UserSession model validation and business logic following TDD approach.
These tests should FAIL initially and PASS after implementation.
"""

import pytest
import uuid
from datetime import datetime
from src.models.session import UserSession
from src.utils.exceptions import ValidationError, SessionError


class TestUserSessionInitialization:
    """
    Unit tests for UserSession entity initialization and validation.
    
    Tests validation rules and business logic for the UserSession model.
    """
    
    def test_valid_session_creation(self) -> None:
        """
        Test creating a valid session.
        
        GIVEN valid session data
        WHEN a UserSession instance is created
        THEN it should be created successfully
        """
        session = UserSession(
            session_id=str(uuid.uuid4()),
            topic="Physics",
            difficulty="Medium",
            total_questions=10
        )
        
        assert session.topic == "Physics"
        assert session.difficulty == "Medium"
        assert session.total_questions == 10
        assert session.current_question_index == 0
        assert session.is_active is True
        assert len(session.questions_asked) == 0
        assert len(session.user_answers) == 0
        assert session.start_time is not None
        assert session.created_at is not None
    
    def test_session_creation_with_custom_id(self) -> None:
        """
        Test creating a session with custom ID.
        
        GIVEN a custom session ID
        WHEN a UserSession instance is created
        THEN it should use the provided ID
        """
        custom_id = "custom-session-123"
        session = UserSession(
            session_id=custom_id,
            topic="Chemistry",
            difficulty="Easy",
            total_questions=5
        )
        
        assert session.session_id == custom_id
    
    def test_session_validation_invalid_topic(self) -> None:
        """
        Test session validation with invalid topic.
        
        GIVEN session data with invalid topic
        WHEN a UserSession instance is created
        THEN it should raise ValidationError
        """
        with pytest.raises(ValidationError) as exc_info:
            UserSession(
                session_id=str(uuid.uuid4()),
                topic="InvalidTopic",
                difficulty="Medium",
                total_questions=10
            )
        
        assert "Invalid topic" in str(exc_info.value)
        assert exc_info.value.field == "topic"
    
    def test_session_validation_invalid_difficulty(self) -> None:
        """
        Test session validation with invalid difficulty.
        
        GIVEN session data with invalid difficulty
        WHEN a UserSession instance is created
        THEN it should raise ValidationError
        """
        with pytest.raises(ValidationError) as exc_info:
            UserSession(
                session_id=str(uuid.uuid4()),
                topic="Physics",
                difficulty="InvalidDifficulty",
                total_questions=10
            )
        
        assert "Invalid difficulty" in str(exc_info.value)
        assert exc_info.value.field == "difficulty"
    
    def test_session_validation_negative_total_questions(self) -> None:
        """
        Test session validation with negative total questions.
        
        GIVEN session data with negative total questions
        WHEN a UserSession instance is created
        THEN it should raise ValidationError
        """
        with pytest.raises(ValidationError) as exc_info:
            UserSession(
                session_id=str(uuid.uuid4()),
                topic="Physics",
                difficulty="Medium",
                total_questions=-5
            )
        
        assert "Total questions must be a positive integer" in str(exc_info.value)
        assert exc_info.value.field == "total_questions"
    
    def test_session_validation_zero_total_questions(self) -> None:
        """
        Test session validation with zero total questions.
        
        GIVEN session data with zero total questions
        WHEN a UserSession instance is created
        THEN it should raise ValidationError
        """
        with pytest.raises(ValidationError) as exc_info:
            UserSession(
                session_id=str(uuid.uuid4()),
                topic="Physics",
                difficulty="Medium",
                total_questions=0
            )
        
        assert "Total questions must be a positive integer" in str(exc_info.value)
    
    def test_session_validation_excessive_total_questions(self) -> None:
        """
        Test session validation with excessive total questions.
        
        GIVEN session data with total questions exceeding limit
        WHEN a UserSession instance is created
        THEN it should raise ValidationError
        """
        with pytest.raises(ValidationError) as exc_info:
            UserSession(
                session_id=str(uuid.uuid4()),
                topic="Physics",
                difficulty="Medium",
                total_questions=100  # Exceeds maximum of 50
            )
        
        assert "Total questions cannot exceed 50" in str(exc_info.value)
        assert exc_info.value.field == "total_questions"
    
    def test_session_validation_invalid_current_index(self) -> None:
        """
        Test session validation with invalid current question index.
        
        GIVEN session data with negative current index
        WHEN a UserSession instance is created
        THEN it should raise ValidationError
        """
        with pytest.raises(ValidationError) as exc_info:
            UserSession(
                session_id=str(uuid.uuid4()),
                topic="Physics",
                difficulty="Medium",
                total_questions=10,
                current_question_index=-1
            )
        
        assert "Current question index must be a non-negative integer" in str(exc_info.value)
        assert exc_info.value.field == "current_question_index"
    
    def test_session_validation_current_index_exceeds_total(self) -> None:
        """
        Test session validation with current index exceeding total questions.
        
        GIVEN session data with current index greater than total questions
        WHEN a UserSession instance is created
        THEN it should raise ValidationError
        """
        with pytest.raises(ValidationError) as exc_info:
            UserSession(
                session_id=str(uuid.uuid4()),
                topic="Physics",
                difficulty="Medium",
                total_questions=5,
                current_question_index=10  # Exceeds total
            )
        
        assert "Current question index cannot exceed total questions" in str(exc_info.value)
    
    def test_session_validation_empty_session_id(self) -> None:
        """
        Test session validation with empty session ID.
        
        GIVEN session data with empty session ID
        WHEN a UserSession instance is created
        THEN it should raise ValidationError
        """
        with pytest.raises(ValidationError) as exc_info:
            UserSession(
                session_id="",
                topic="Physics",
                difficulty="Medium",
                total_questions=10
            )
        
        assert "Session ID cannot be empty" in str(exc_info.value)
        assert exc_info.value.field == "session_id"
    
    def test_session_add_question(self) -> None:
        """
        Test adding a question to session.
        
        GIVEN a valid session
        WHEN a question is added
        THEN the question should be tracked and index updated
        """
        session = UserSession(
            session_id=str(uuid.uuid4()),
            topic="Physics",
            difficulty="Medium",
            total_questions=10
        )
        
        question_id = "physics_1"
        session.add_question(question_id)
        
        assert question_id in session.questions_asked
        assert session.current_question_index == 1
        assert session.updated_at is not None
    
    def test_session_add_duplicate_question(self) -> None:
        """
        Test adding duplicate question to session.
        
        GIVEN a session with an existing question
        WHEN the same question is added again
        THEN it should raise SessionError
        """
        session = UserSession(
            session_id=str(uuid.uuid4()),
            topic="Physics",
            difficulty="Medium",
            total_questions=10
        )
        
        question_id = "physics_1"
        session.add_question(question_id)
        
        with pytest.raises(SessionError) as exc_info:
            session.add_question(question_id)
        
        assert "already asked in this session" in str(exc_info.value)
        assert exc_info.value.session_id == session.session_id
    
    def test_session_add_question_exceeds_limit(self) -> None:
        """
        Test adding questions beyond session limit.
        
        GIVEN a session that has reached its question limit
        WHEN another question is added
        THEN it should raise SessionError
        """
        session = UserSession(
            session_id=str(uuid.uuid4()),
            topic="Physics",
            difficulty="Medium",
            total_questions=2
        )
        
        # Add questions up to limit
        session.add_question("physics_1")
        session.add_question("physics_2")
        
        # Try to add one more
        with pytest.raises(SessionError) as exc_info:
            session.add_question("physics_3")
        
        assert "Question limit reached" in str(exc_info.value)
        assert exc_info.value.session_id == session.session_id
    
    def test_session_submit_answer(self) -> None:
        """
        Test submitting an answer for a question.
        
        GIVEN a session with an asked question
        WHEN an answer is submitted
        THEN the answer should be recorded
        """
        session = UserSession(
            session_id=str(uuid.uuid4()),
            topic="Physics",
            difficulty="Medium",
            total_questions=10
        )
        
        question_id = "physics_1"
        answer = "299,792,458 m/s"
        
        session.add_question(question_id)
        session.submit_answer(question_id, answer)
        
        assert question_id in session.user_answers
        assert session.user_answers[question_id] == answer
        assert session.updated_at is not None
    
    def test_session_submit_answer_for_unasked_question(self) -> None:
        """
        Test submitting answer for unasked question.
        
        GIVEN a session without asked questions
        WHEN an answer is submitted
        THEN it should raise SessionError
        """
        session = UserSession(
            session_id=str(uuid.uuid4()),
            topic="Physics",
            difficulty="Medium",
            total_questions=10
        )
        
        with pytest.raises(SessionError) as exc_info:
            session.submit_answer("physics_1", "answer")
        
        assert "was not asked in this session" in str(exc_info.value)
        assert exc_info.value.session_id == session.session_id
    
    def test_session_submit_duplicate_answer(self) -> None:
        """
        Test submitting duplicate answer for same question.
        
        GIVEN a session with an answered question
        WHEN the same answer is submitted again
        THEN it should raise SessionError
        """
        session = UserSession(
            session_id=str(uuid.uuid4()),
            topic="Physics",
            difficulty="Medium",
            total_questions=10
        )
        
        question_id = "physics_1"
        session.add_question(question_id)
        session.submit_answer(question_id, "answer1")
        
        with pytest.raises(SessionError) as exc_info:
            session.submit_answer(question_id, "answer2")
        
        assert "already answered" in str(exc_info.value)
        assert exc_info.value.session_id == session.session_id
    
    def test_session_is_complete(self) -> None:
        """
        Test checking if session is complete.
        
        GIVEN a session with questions
        WHEN is_complete is called
        THEN it should return True when all questions are asked
        """
        session = UserSession(
            session_id=str(uuid.uuid4()),
            topic="Physics",
            difficulty="Medium",
            total_questions=3
        )
        
        assert session.is_complete() is False
        
        session.add_question("physics_1")
        assert session.is_complete() is False
        
        session.add_question("physics_2")
        assert session.is_complete() is False
        
        session.add_question("physics_3")
        assert session.is_complete() is True
    
    def test_session_get_progress(self) -> None:
        """
        Test getting session progress.
        
        GIVEN a session with some questions asked
        WHEN get_progress is called
        THEN it should return accurate progress information
        """
        session = UserSession(
            session_id=str(uuid.uuid4()),
            topic="Physics",
            difficulty="Medium",
            total_questions=10
        )
        
        progress = session.get_progress()
        assert progress["total_questions"] == 10
        assert progress["questions_asked"] == 0
        assert progress["questions_answered"] == 0
        assert progress["current_index"] == 0
        assert progress["progress_percentage"] == 0.0
        assert progress["is_complete"] is False
        assert progress["remaining_questions"] == 10
        
        # Add some questions
        session.add_question("physics_1")
        session.submit_answer("physics_1", "answer")
        
        progress = session.get_progress()
        assert progress["questions_asked"] == 1
        assert progress["questions_answered"] == 1
        assert progress["current_index"] == 1
        assert progress["progress_percentage"] == 10.0
        assert progress["remaining_questions"] == 9
    
    def test_session_complete_session(self) -> None:
        """
        Test completing a session.
        
        GIVEN an active session
        WHEN complete_session is called
        THEN the session should be marked as inactive
        """
        session = UserSession(
            session_id=str(uuid.uuid4()),
            topic="Physics",
            difficulty="Medium",
            total_questions=10
        )
        
        assert session.is_active is True
        assert session.end_time is None
        
        session.complete_session()
        
        assert session.is_active is False
        assert session.end_time is not None
        assert session.updated_at is not None
    
    def test_session_complete_already_inactive(self) -> None:
        """
        Test completing an already inactive session.
        
        GIVEN an inactive session
        WHEN complete_session is called
        THEN it should raise SessionError
        """
        session = UserSession(
            session_id=str(uuid.uuid4()),
            topic="Physics",
            difficulty="Medium",
            total_questions=10
        )
        
        session.complete_session()
        
        with pytest.raises(SessionError) as exc_info:
            session.complete_session()
        
        assert "already inactive" in str(exc_info.value)
        assert exc_info.value.session_id == session.session_id
    
    def test_session_create_new_factory_method(self) -> None:
        """
        Test the create_new factory method.
        
        WHEN create_new is called with topic and difficulty
        THEN it should create a session with generated UUID
        """
        session = UserSession.create_new("Chemistry", "Hard", 15)
        
        assert session.topic == "Chemistry"
        assert session.difficulty == "Hard"
        assert session.total_questions == 15
        assert session.session_id is not None
        assert len(session.session_id) > 0  # UUID should be generated
        
        # Should be a valid UUID
        uuid.UUID(session.session_id)
    
    def test_session_get_session_duration(self) -> None:
        """
        Test getting session duration.
        
        GIVEN a session
        WHEN get_session_duration is called
        THEN it should return the duration in seconds
        """
        session = UserSession(
            session_id=str(uuid.uuid4()),
            topic="Physics",
            difficulty="Medium",
            total_questions=10
        )
        
        # Duration should be small for new session
        duration = session.get_session_duration()
        assert isinstance(duration, int)
        assert duration >= 0
        
        # Complete session and check duration
        session.complete_session()
        duration_after_complete = session.get_session_duration()
        assert duration_after_complete >= duration
    
    def test_session_pause_and_resume(self) -> None:
        """
        Test pausing and resuming a session.
        
        GIVEN an active session
        WHEN pause_session and resume_session are called
        THEN session should remain active but update timestamps
        """
        session = UserSession(
            session_id=str(uuid.uuid4()),
            topic="Physics",
            difficulty="Medium",
            total_questions=10
        )
        
        original_updated_at = session.updated_at
        
        # Pause session
        session.pause_session()
        assert session.is_active is True
        assert session.updated_at != original_updated_at
        
        # Resume session
        session.resume_session()
        assert session.is_active is True
        assert session.updated_at is not None
    
    def test_session_pause_inactive_session(self) -> None:
        """
        Test pausing an inactive session.
        
        GIVEN an inactive session
        WHEN pause_session is called
        THEN it should raise SessionError
        """
        session = UserSession(
            session_id=str(uuid.uuid4()),
            topic="Physics",
            difficulty="Medium",
            total_questions=10
        )
        
        session.complete_session()
        
        with pytest.raises(SessionError) as exc_info:
            session.pause_session()
        
        assert "Cannot pause inactive session" in str(exc_info.value)
        assert exc_info.value.session_id == session.session_id
    
    def test_session_resume_inactive_session(self) -> None:
        """
        Test resuming an inactive session.
        
        GIVEN an inactive session
        WHEN resume_session is called
        THEN it should raise SessionError
        """
        session = UserSession(
            session_id=str(uuid.uuid4()),
            topic="Physics",
            difficulty="Medium",
            total_questions=10
        )
        
        session.complete_session()
        
        with pytest.raises(SessionError) as exc_info:
            session.resume_session()
        
        assert "Cannot resume inactive session" in str(exc_info.value)
        assert exc_info.value.session_id == session.session_id
