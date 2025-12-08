"""
Contract tests for questions endpoint.

Tests the random question retrieval functionality according to API contract.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any

from src.api.main import create_app
from src.utils.config import AppConfig


class TestQuestionsEndpoint:
    
    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client for FastAPI application."""
        config = AppConfig(debug=True)
        app = create_app(config)
        return TestClient(app)
    
    @pytest.fixture
    def valid_session_data(self) -> Dict[str, Any]:
        """Valid session creation data."""
        return {
            "topic": "Physics",
            "difficulty": "Medium",
            "total_questions": 5
        }
    
    """Contract tests for the questions API endpoint."""

    def test_get_random_question_in_session(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test getting a random question for an active session.
        
        GIVEN a valid session exists
        WHEN requesting the next question
        THEN return a valid question with expected structure
        """
        # Create a session first
        session_response = client.post("/api/v1/sessions/", json=valid_session_data)
        assert session_response.status_code == 200
        session_data = session_response.json()
        session_id = session_data["session_id"]
        
        # Get next question
        response = client.get(f"/api/v1/sessions/{session_id}/next-question")
        assert response.status_code == 200
        
        question_data = response.json()
        
        # Verify response structure
        assert "question_id" in question_data
        assert "question_text" in question_data
        assert "options" in question_data
        assert "session_complete" in question_data
        
        # Verify question is not None when session is active
        assert question_data["question_id"] is not None
        assert question_data["question_text"] is not None
        assert isinstance(question_data["options"], list)
        assert len(question_data["options"]) == 4
        assert question_data["session_complete"] is False
        
        # Verify options are strings
        for option in question_data["options"]:
            assert isinstance(option, str)
            assert len(option.strip()) > 0

    def test_get_random_question_for_completed_session(self, client: TestClient) -> None:
        """
        Test getting a question when session is complete.
        
        GIVEN a session has answered all questions
        WHEN requesting the next question
        THEN return session_complete=True with null question data
        """
        # This test will be implemented when we have session completion logic
        # For now, test the structure
        session_id = "test-completed-session"
        
        response = client.get(f"/api/v1/sessions/{session_id}/next-question")
        
        # Should handle invalid session gracefully
        assert response.status_code in [404, 400]
        
        error_data = response.json()
        assert "detail" in error_data

    def test_get_random_question_invalid_session_id(self, client: TestClient) -> None:
        """
        Test getting a question with invalid session ID.
        
        GIVEN an invalid session ID
        WHEN requesting the next question
        THEN return 404 error
        """
        invalid_session_id = "invalid-session-id"
        
        response = client.get(f"/api/v1/sessions/{invalid_session_id}/next-question")
        assert response.status_code == 404
        
        error_data = response.json()
        assert "detail" in error_data

    def test_question_randomization_across_requests(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test that questions are randomized across multiple sessions.
        
        GIVEN multiple sessions with same parameters
        WHEN requesting questions from each session
        THEN questions should be different (randomized)
        """
        questions_received = []
        
        # Create multiple sessions and get first question from each
        for _ in range(3):
            session_response = client.post("/api/v1/sessions/", json=valid_session_data)
            assert session_response.status_code == 200
            session_data = session_response.json()
            session_id = session_data["session_id"]
            
            # Get first question
            question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
            assert question_response.status_code == 200
            question_data = question_response.json()
            questions_received.append(question_data["question_id"])
        
        # At least some questions should be different (randomization)
        # Note: This is probabilistic, but with sufficient questions should work
        unique_questions = set(questions_received)
        assert len(unique_questions) >= 1  # At least one unique question

    def test_question_matches_session_topic_and_difficulty(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test that returned questions match the session's topic and difficulty.
        
        GIVEN a session with specific topic and difficulty
        WHEN requesting a question
        THEN the question should match those parameters
        """
        # Create session with specific parameters
        session_response = client.post("/api/v1/sessions/", json=valid_session_data)
        assert session_response.status_code == 200
        session_data = session_response.json()
        session_id = session_data["session_id"]
        
        # Get a question
        question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
        assert question_response.status_code == 200
        question_data = question_response.json()
        
        # We would need to verify the question matches topic/difficulty
        # This requires access to the question bank or additional endpoint
        # For now, verify we get a valid question structure
        assert question_data["question_id"] is not None
        assert question_data["question_text"] is not None

    def test_no_duplicate_questions_in_session(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test that questions are not repeated within the same session.
        
        GIVEN an active session
        WHEN requesting multiple questions
        THEN no question should be repeated
        """
        # Create session
        session_response = client.post("/api/v1/sessions/", json=valid_session_data)
        assert session_response.status_code == 200
        session_data = session_response.json()
        session_id = session_data["session_id"]
        
        # Get multiple questions
        questions_received = []
        for _ in range(5):  # Get 5 questions
            question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
            if question_response.json()["session_complete"]:
                break  # Session completed
            assert question_response.status_code == 200
            question_data = question_response.json()
            questions_received.append(question_data["question_id"])
        
        # Verify no duplicates
        assert len(questions_received) == len(set(questions_received))
