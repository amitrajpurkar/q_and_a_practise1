"""
Contract tests for the session completion API endpoint.

Tests the session completion endpoint to ensure it properly finalizes
sessions and returns comprehensive score summaries.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any

from src.api.main import create_app
from src.utils.config import AppConfig


class TestSessionCompletionEndpoint:
    """Contract tests for the session completion API endpoint."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client."""
        config = AppConfig(debug=True)
        app = create_app(config)
        return TestClient(app)

    @pytest.fixture
    def valid_session_data(self) -> Dict[str, Any]:
        """Valid session creation data."""
        return {
            "topic": "Physics",
            "difficulty": "Medium",
            "total_questions": 3
        }

    def test_complete_session_success(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test completing a session successfully.
        
        GIVEN a valid active session
        WHEN completing the session
        THEN return final score and mark session as inactive
        """
        # Create session
        session_response = client.post("/api/v1/sessions/", json=valid_session_data)
        assert session_response.status_code == 200
        session_data = session_response.json()
        session_id = session_data["session_id"]
        
        # Complete session
        response = client.post(f"/api/v1/sessions/{session_id}/complete")
        assert response.status_code == 200
        
        completion_data = response.json()
        
        # Verify score fields
        assert "session_id" in completion_data
        assert "total_questions" in completion_data
        assert "correct_answers" in completion_data
        assert "incorrect_answers" in completion_data
        assert "accuracy_percentage" in completion_data
        assert "time_taken_seconds" in completion_data
        assert "topic_performance" in completion_data
        
        # Verify session is marked as completed
        assert completion_data["session_id"] == session_id
        
        # Verify session is now inactive
        session_get_response = client.get(f"/api/v1/sessions/{session_id}")
        assert session_get_response.status_code == 200
        session_info = session_get_response.json()
        assert session_info["is_active"] is False
        assert session_info["end_time"] is not None

    def test_complete_session_with_answers(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test completing a session with answered questions.
        
        GIVEN a session with answered questions
        WHEN completing the session
        THEN return accurate final score
        """
        # Create session with 2 questions
        session_data = valid_session_data.copy()
        session_data["total_questions"] = 2
        
        session_response = client.post("/api/v1/sessions/", json=session_data)
        assert session_response.status_code == 200
        session_info = session_response.json()
        session_id = session_info["session_id"]
        
        # Answer first question correctly
        question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
        question_data = question_response.json()
        
        answer_data = {
            "question_id": question_data["question_id"],
            "answer": question_data["correct_answer"]
        }
        
        submit_response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
        assert submit_response.status_code == 200
        
        # Answer second question incorrectly
        question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
        question_data = question_response.json()
        
        answer_data = {
            "question_id": question_data["question_id"],
            "answer": "Wrong answer"
        }
        
        submit_response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
        assert submit_response.status_code == 200
        
        # Complete session
        response = client.post(f"/api/v1/sessions/{session_id}/complete")
        assert response.status_code == 200
        
        completion_data = response.json()
        
        # Verify final score
        assert completion_data["total_questions"] == 2
        assert completion_data["correct_answers"] == 1
        assert completion_data["incorrect_answers"] == 1
        assert completion_data["accuracy_percentage"] == 50.0
        assert completion_data["time_taken_seconds"] >= 0

    def test_complete_session_invalid_session_id(self, client: TestClient) -> None:
        """
        Test completing session with invalid session ID.
        
        GIVEN an invalid session ID
        WHEN completing the session
        THEN return 404 error
        """
        invalid_session_id = "invalid-session-id"
        
        response = client.post(f"/api/v1/sessions/{invalid_session_id}/complete")
        assert response.status_code == 404
        
        error_data = response.json()
        assert "detail" in error_data

    def test_complete_session_already_completed(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test completing an already completed session.
        
        GIVEN a completed session
        WHEN completing the session again
        THEN return the same final score
        """
        # Create session
        session_response = client.post("/api/v1/sessions/", json=valid_session_data)
        assert session_response.status_code == 200
        session_data = session_response.json()
        session_id = session_data["session_id"]
        
        # Complete session first time
        first_complete = client.post(f"/api/v1/sessions/{session_id}/complete")
        assert first_complete.status_code == 200
        
        # Complete session second time
        second_complete = client.post(f"/api/v1/sessions/{session_id}/complete")
        assert second_complete.status_code == 200
        
        # Both responses should be identical
        assert first_complete.json() == second_complete.json()

    def test_complete_session_empty_session(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test completing a session with no answered questions.
        
        GIVEN a session with no answered questions
        WHEN completing the session
        THEN return score with zero values
        """
        # Create session
        session_response = client.post("/api/v1/sessions/", json=valid_session_data)
        assert session_response.status_code == 200
        session_data = session_response.json()
        session_id = session_data["session_id"]
        
        # Complete without answering any questions
        response = client.post(f"/api/v1/sessions/{session_id}/complete")
        assert response.status_code == 200
        
        completion_data = response.json()
        
        # Verify empty session score
        assert completion_data["total_questions"] == 0
        assert completion_data["correct_answers"] == 0
        assert completion_data["incorrect_answers"] == 0
        assert completion_data["accuracy_percentage"] == 0.0
        assert completion_data["time_taken_seconds"] >= 0

    def test_complete_session_performance_breakdown(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test performance breakdown in completed session.
        
        GIVEN a session with answered questions
        WHEN completing the session
        THEN return detailed performance breakdown by topic/difficulty
        """
        # Create session
        session_response = client.post("/api/v1/sessions/", json=valid_session_data)
        assert session_response.status_code == 200
        session_data = session_response.json()
        session_id = session_data["session_id"]
        
        # Answer one question
        question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
        question_data = question_response.json()
        
        answer_data = {
            "question_id": question_data["question_id"],
            "answer": question_data["correct_answer"]
        }
        
        submit_response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
        assert submit_response.status_code == 200
        
        # Complete session
        response = client.post(f"/api/v1/sessions/{session_id}/complete")
        assert response.status_code == 200
        
        completion_data = response.json()
        
        # Verify performance breakdown
        topic_performance = completion_data["topic_performance"]
        assert isinstance(topic_performance, dict)
        
        # Should have performance data for the session topic
        assert "Physics" in topic_performance
        assert "Medium" in topic_performance["Physics"]
        
        physics_medium = topic_performance["Physics"]["Medium"]
        assert "correct" in physics_medium
        assert "incorrect" in physics_medium
        assert "total" in physics_medium
        assert physics_medium["total"] == 1
        assert physics_medium["correct"] + physics_medium["incorrect"] == physics_medium["total"]

    def test_complete_session_time_tracking(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test time tracking in completed session.
        
        GIVEN a session that has been active
        WHEN completing the session
        THEN return accurate time duration
        """
        # Create session
        session_response = client.post("/api/v1/sessions/", json=valid_session_data)
        assert session_response.status_code == 200
        session_data = session_response.json()
        session_id = session_data["session_id"]
        
        # Wait a bit to ensure time tracking works
        import time
        time.sleep(0.1)
        
        # Complete session
        response = client.post(f"/api/v1/sessions/{session_id}/complete")
        assert response.status_code == 200
        
        completion_data = response.json()
        
        # Verify time tracking
        assert completion_data["time_taken_seconds"] >= 0
        assert completion_data["time_taken_seconds"] < 60  # Should be less than a minute for test
