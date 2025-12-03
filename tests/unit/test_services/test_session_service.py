"""
Unit tests for answer validation logic in SessionService.

Tests the answer validation, feedback generation, and session state management.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from src.services.session_service import SessionService
from src.services.question_service import IQuestionService
from src.services.score_service import IScoreService
from src.models.session import UserSession
from src.models.question import Question
from src.models.score import Score
from src.utils.exceptions import SessionError, ValidationError


class TestSessionSummaryGeneration:
    """Unit tests for session summary generation."""

    @pytest.fixture
    def mock_question_service(self) -> Mock:
        """Create mock question service."""
        mock_service = Mock(spec=IQuestionService)
        mock_service.get_question_by_id.return_value = None
        return mock_service

    @pytest.fixture
    def mock_score_service(self) -> Mock:
        """Create mock score service."""
        mock_service = Mock(spec=IScoreService)
        mock_service.calculate_score.return_value = None
        mock_service.generate_summary.return_value = None
        return mock_service

    @pytest.fixture
    def session_service(self, mock_question_service: Mock, mock_score_service: Mock) -> SessionService:
        """Create session service with mocked dependencies."""
        return SessionService(mock_question_service, mock_score_service)

    @pytest.fixture
    def sample_session(self) -> UserSession:
        """Create a sample user session."""
        return UserSession(
            session_id="test-session-123",
            topic="Physics",
            difficulty="Medium",
            total_questions=5,
            start_time=datetime.utcnow(),
            is_active=True
        )

    @pytest.fixture
    def sample_questions(self) -> List[Question]:
        """Create sample questions for testing."""
        return [
            Question(
                id="physics_1",
                topic="Physics",
                question_text="What is force?",
                option1="A) Mass × acceleration",
                option2="B) Mass / acceleration", 
                option3="C) Acceleration / mass",
                option4="D) Mass + acceleration",
                correct_answer="A) Mass × acceleration",
                difficulty="Easy",
                tag="Physics-Easy"
            ),
            Question(
                id="physics_2",
                topic="Physics",
                question_text="What is energy?",
                option1="A) Force × distance",
                option2="B) Mass × velocity",
                option3="C) Power × time",
                option4="D) Force / distance",
                correct_answer="A) Force × distance",
                difficulty="Medium",
                tag="Physics-Medium"
            )
        ]

    def test_complete_session_success(self, session_service: SessionService, sample_session: UserSession) -> None:
        """
        Test completing a session successfully.
        
        GIVEN an active session
        WHEN completing the session
        THEN return accurate score summary
        """
        # Setup session with answers
        sample_session.user_answers = {
            "physics_1": "A) Mass × acceleration",  # Correct
            "physics_2": "B) Mass × velocity"       # Incorrect
        }
        sample_session.is_active = True
        
        # Mock score calculation
        expected_score = Score(
            session_id="test-session-123",
            total_questions=2,
            correct_answers=1,
            incorrect_answers=1,
            accuracy_percentage=50.0,
            time_taken_seconds=300,
            topic_performance={
                "Physics": {
                    "Easy": {"correct": 1, "incorrect": 0, "total": 1},
                    "Medium": {"correct": 0, "incorrect": 1, "total": 1}
                }
            },
            streak_data={"current": 0, "best": 1}
        )
        
        session_service.score_service.calculate_score.return_value = expected_score
        
        # Store session
        session_service.sessions = {"test-session-123": sample_session}
        
        # Complete session
        result = session_service.complete_session("test-session-123")
        
        # Verify result
        assert result is not None
        assert result.session_id == "test-session-123"
        assert result.total_questions == 2
        assert result.correct_answers == 1
        assert result.incorrect_answers == 1
        assert result.accuracy_percentage == 50.0
        
        # Verify session is marked inactive
        assert sample_session.is_active is False
        assert sample_session.end_time is not None

    def test_get_session_score_active_session(self, session_service: SessionService, sample_session: UserSession) -> None:
        """
        Test getting score for an active session.
        
        GIVEN an active session with answers
        WHEN getting the session score
        THEN return current score without completing session
        """
        # Setup session with answers
        sample_session.user_answers = {
            "physics_1": "A) Mass × acceleration",  # Correct
        }
        sample_session.is_active = True
        
        expected_score = Score(
            session_id="test-session-123",
            total_questions=1,
            correct_answers=1,
            incorrect_answers=0,
            accuracy_percentage=100.0,
            time_taken_seconds=150,
            topic_performance={
                "Physics": {
                    "Easy": {"correct": 1, "incorrect": 0, "total": 1}
                }
            },
            streak_data={"current": 1, "best": 1}
        )
        
        session_service.score_service.calculate_score.return_value = expected_score
        session_service.sessions = {"test-session-123": sample_session}
        
        # Get score
        result = session_service.get_session_score("test-session-123")
        
        # Verify result
        assert result is not None
        assert result.session_id == "test-session-123"
        assert result.total_questions == 1
        assert result.correct_answers == 1
        assert result.accuracy_percentage == 100.0
        
        # Verify session is still active
        assert sample_session.is_active is True
        assert sample_session.end_time is None


class TestAnswerValidation:
    """Unit tests for answer validation functionality."""

    @pytest.fixture
    def mock_question_bank(self) -> Mock:
        """Create a mock question bank with test data."""
        bank = Mock()
        
        # Create test question
        question = Question(
            id="physics_1",
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
        
        bank.get_question_by_id.return_value = question
        return bank

    @pytest.fixture
    def mock_score_service(self) -> Mock:
        """Create a mock score service."""
        score_service = Mock(spec=ScoreService)
        score_service.record_answer.return_value = AnswerResult(
            question_id="physics_1",
            correct=True,
            answer_text="Inertia",
            correct_answer="Inertia",
            explanation=None,
            time_taken_seconds=5
        )
        return score_service

    @pytest.fixture
    def session_service(self, mock_question_bank: Mock, mock_score_service: Mock) -> SessionService:
        """Create SessionService instance with mock dependencies."""
        return SessionService(mock_question_bank, mock_score_service)

    @pytest.fixture
    def active_session(self) -> UserSession:
        """Create an active user session."""
        return UserSession(
            session_id="test-session-1",
            topic="Physics",
            difficulty="Easy",
            total_questions=5,
            current_question_index=0,
            is_active=True,
            created_at=datetime.now(),
            asked_questions=[],
            answered_questions=[]
        )

    def test_validate_answer_correct_answer(self, session_service: SessionService, active_session: UserSession) -> None:
        """
        Test validation of a correct answer.
        
        GIVEN a session and correct answer
        WHEN validating the answer
        THEN return correct=True with appropriate feedback
        """
        question_id = "physics_1"
        user_answer = "Inertia"
        
        result = session_service.validate_answer(active_session, question_id, user_answer)
        
        assert result is not None
        assert result.correct is True
        assert result.answer_text == user_answer
        assert result.correct_answer == "Inertia"
        assert result.time_taken_seconds > 0

    def test_validate_answer_incorrect_answer(self, session_service: SessionService, active_session: UserSession) -> None:
        """
        Test validation of an incorrect answer.
        
        GIVEN a session and incorrect answer
        WHEN validating the answer
        THEN return correct=False with correct answer provided
        """
        question_id = "physics_1"
        user_answer = "Wrong Answer"
        
        # Mock the score service to return incorrect result
        session_service._score_service.record_answer.return_value = AnswerResult(
            question_id=question_id,
            correct=False,
            answer_text=user_answer,
            correct_answer="Inertia",
            explanation=None,
            time_taken_seconds=3
        )
        
        result = session_service.validate_answer(active_session, question_id, user_answer)
        
        assert result is not None
        assert result.correct is False
        assert result.answer_text == user_answer
        assert result.correct_answer == "Inertia"

    def test_validate_answer_case_insensitive(self, session_service: SessionService, active_session: UserSession) -> None:
        """
        Test that answer validation is case insensitive.
        
        GIVEN a session and answer with different case
        WHEN validating the answer
        THEN should match correctly regardless of case
        """
        question_id = "physics_1"
        user_answer = "inertia"  # lowercase
        
        result = session_service.validate_answer(active_session, question_id, user_answer)
        
        assert result is not None
        assert result.correct is True

    def test_validate_answer_whitespace_handling(self, session_service: SessionService, active_session: UserSession) -> None:
        """
        Test that answer validation handles whitespace properly.
        
        GIVEN a session and answer with extra whitespace
        WHEN validating the answer
        THEN should match correctly after trimming
        """
        question_id = "physics_1"
        user_answer = "  inertia  "  # with whitespace
        
        result = session_service.validate_answer(active_session, question_id, user_answer)
        
        assert result is not None
        assert result.correct is True

    def test_validate_answer_invalid_session(self, session_service: SessionService) -> None:
        """
        Test validation with inactive session.
        
        GIVEN an inactive session
        WHEN validating an answer
        THEN raise SessionError
        """
        inactive_session = UserSession(
            session_id="inactive-session",
            topic="Physics",
            difficulty="Easy",
            total_questions=5,
            current_question_index=0,
            is_active=False,  # Inactive session
            created_at=datetime.now(),
            asked_questions=[],
            answered_questions=[]
        )
        
        with pytest.raises(SessionError) as exc_info:
            session_service.validate_answer(inactive_session, "physics_1", "Inertia")
        
        assert "inactive" in str(exc_info.value).lower()

    def test_validate_answer_invalid_question_id(self, session_service: SessionService, active_session: UserSession) -> None:
        """
        Test validation with invalid question ID.
        
        GIVEN a session and invalid question ID
        WHEN validating the answer
        THEN raise ValidationError
        """
        session_service._question_bank.get_question_by_id.return_value = None
        
        with pytest.raises(ValidationError) as exc_info:
            session_service.validate_answer(active_session, "invalid-question", "Inertia")
        
        assert "Invalid question" in str(exc_info.value)

    def test_validate_answer_empty_answer(self, session_service: SessionService, active_session: UserSession) -> None:
        """
        Test validation with empty answer.
        
        GIVEN a session and empty answer
        WHEN validating the answer
        THEN raise ValidationError
        """
        with pytest.raises(ValidationError) as exc_info:
            session_service.validate_answer(active_session, "physics_1", "")
        
        assert "Answer cannot be empty" in str(exc_info.value)

    def test_validate_answer_none_answer(self, session_service: SessionService, active_session: UserSession) -> None:
        """
        Test validation with None answer.
        
        GIVEN a session and None answer
        WHEN validating the answer
        THEN raise ValidationError
        """
        with pytest.raises(ValidationError) as exc_info:
            session_service.validate_answer(active_session, "physics_1", None)
        
        assert "Answer cannot be empty" in str(exc_info.value)

    def test_validate_answer_updates_session_state(self, session_service: SessionService, active_session: UserSession) -> None:
        """
        Test that answer validation updates session state.
        
        GIVEN a session and valid answer
        WHEN validating the answer
        THEN session state should be updated
        """
        initial_answered_count = len(active_session.answered_questions)
        initial_current_index = active_session.current_question_index
        
        question_id = "physics_1"
        user_answer = "Inertia"
        
        result = session_service.validate_answer(active_session, question_id, user_answer)
        
        # Session should be updated
        assert len(active_session.answered_questions) > initial_answered_count
        assert active_session.current_question_index > initial_current_index
        assert question_id in active_session.answered_questions

    def test_validate_answer_duplicate_question(self, session_service: SessionService, active_session: UserSession) -> None:
        """
        Test validation of duplicate question answers.
        
        GIVEN a session that already answered a question
        WHEN validating the same question again
        THEN raise ValidationError
        """
        question_id = "physics_1"
        user_answer = "Inertia"
        
        # First answer should succeed
        result1 = session_service.validate_answer(active_session, question_id, user_answer)
        assert result1 is not None
        
        # Second answer for same question should fail
        with pytest.raises(ValidationError) as exc_info:
            session_service.validate_answer(active_session, question_id, user_answer)
        
        assert "already answered" in str(exc_info.value).lower()

    def test_validate_answer_with_explanation(self, session_service: SessionService, active_session: UserSession) -> None:
        """
        Test validation with explanation generation.
        
        GIVEN a session and answer
        WHEN validating the answer
        THEN should include explanation if available
        """
        # Mock score service to return explanation
        session_service._score_service.record_answer.return_value = AnswerResult(
            question_id="physics_1",
            correct=True,
            answer_text="Inertia",
            correct_answer="Inertia",
            explanation="Newton's first law states that an object will remain at rest or in uniform motion unless acted upon by an external force.",
            time_taken_seconds=5
        )
        
        result = session_service.validate_answer(active_session, "physics_1", "Inertia")
        
        assert result is not None
        assert result.explanation is not None
        assert "Newton's first law" in result.explanation

    def test_validate_answer_performance(self, session_service: SessionService, active_session: UserSession) -> None:
        """
        Test performance of answer validation.
        
        GIVEN multiple answer validations
        WHEN validating many answers
        THEN performance should be acceptable
        """
        import time
        
        start_time = time.time()
        
        # Create multiple sessions for testing
        for i in range(100):
            session = UserSession(
                session_id=f"test-session-{i}",
                topic="Physics",
                difficulty="Easy",
                total_questions=5,
                current_question_index=0,
                is_active=True,
                created_at=datetime.now(),
                asked_questions=[],
                answered_questions=[]
            )
            
            result = session_service.validate_answer(session, "physics_1", "Inertia")
            assert result is not None
        
        elapsed_time = time.time() - start_time
        
        # Should complete 100 validations in reasonable time (less than 1 second)
        assert elapsed_time < 1.0, f"Performance issue: {elapsed_time:.3f}s for 100 validations"

    def test_validate_answer_different_question_types(self, session_service: SessionService, mock_question_bank: Mock, active_session: UserSession) -> None:
        """
        Test validation with different types of questions.
        
        GIVEN questions with different answer formats
        WHEN validating answers
        THEN should handle each type correctly
        """
        # Test with numerical answer
        math_question = Question(
            id="math_1",
            topic="Math",
            question_text="What is 2+2?",
            option1="3",
            option2="4",
            option3="5",
            option4="6",
            correct_answer="4",
            difficulty="Easy",
            tag="Math-Easy"
        )
        
        mock_question_bank.get_question_by_id.return_value = math_question
        
        result = session_service.validate_answer(active_session, "math_1", "4")
        assert result is not None
        assert result.correct is True
        
        # Test with formula answer
        physics_question = Question(
            id="physics_2",
            topic="Physics",
            question_text="What is F=ma?",
            option1="Force formula",
            option2="Energy formula",
            option3="Power formula",
            option4="Velocity formula",
            correct_answer="Force formula",
            difficulty="Medium",
            tag="Physics-Medium"
        )
        
        mock_question_bank.get_question_by_id.return_value = physics_question
        
        result = session_service.validate_answer(active_session, "physics_2", "Force formula")
        assert result is not None
        assert result.correct is True

    def test_validate_answer_session_completion(self, session_service: SessionService, mock_question_bank: Mock) -> None:
        """
        Test validation when session completes.
        
        GIVEN a session about to complete
        WHEN validating the final answer
        THEN session should be marked as completed
        """
        # Create session with one question left
        near_complete_session = UserSession(
            session_id="near-complete-session",
            topic="Physics",
            difficulty="Easy",
            total_questions=1,
            current_question_index=0,
            is_active=True,
            created_at=datetime.now(),
            asked_questions=[],
            answered_questions=[]
        )
        
        result = session_service.validate_answer(near_complete_session, "physics_1", "Inertia")
        
        assert result is not None
        # Session should be completed after answering all questions
        assert near_complete_session.current_question_index >= near_complete_session.total_questions
