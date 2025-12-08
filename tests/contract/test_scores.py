"""
Contract tests for the scores API endpoint.

Tests the score retrieval endpoint to ensure it returns accurate
performance data and handles edge cases properly.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any

from src.api.main import create_app
from src.utils.config import AppConfig


class TestScoresEndpoint:
    """Contract tests for the scores API endpoint."""

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
            "total_questions": 5
        }

    def test_get_session_score_active_session(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test getting score for an active session.
        
        GIVEN a valid active session
        WHEN requesting the session score
        THEN return accurate current score and progress
        """
        # Create session
        session_response = client.post("/api/v1/sessions/", json=valid_session_data)
        assert session_response.status_code == 200
        session_data = session_response.json()
        session_id = session_data["session_id"]
        
        # Get score
        response = client.get(f"/api/v1/sessions/{session_id}/score")
        assert response.status_code == 200
        
        score_data = response.json()
        
        # Verify required fields
        assert "session_id" in score_data
        assert "total_questions" in score_data
        assert "correct_answers" in score_data
        assert "incorrect_answers" in score_data
        assert "accuracy_percentage" in score_data
        assert "time_taken_seconds" in score_data
        assert "topic_performance" in score_data
        
        # Verify data consistency
        assert score_data["session_id"] == session_id
        assert score_data["total_questions"] == 0  # No questions answered yet
        assert score_data["correct_answers"] == 0
        assert score_data["incorrect_answers"] == 0
        assert score_data["accuracy_percentage"] == 0.0
        
        # Verify topic performance structure
        assert isinstance(score_data["topic_performance"], dict)

    def test_get_session_score_with_answers(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test getting score after answering some questions.
        
        GIVEN a session with answered questions
        WHEN requesting the session score
        THEN return score reflecting answered questions
        """
        # Create session
        session_response = client.post("/api/v1/sessions/", json=valid_session_data)
        assert session_response.status_code == 200
        session_data = session_response.json()
        session_id = session_data["session_id"]
        
        # Get and answer a question
        question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
        assert question_response.status_code == 200
        question_data = question_response.json()
        
        answer_data = {
            "question_id": question_data["question_id"],
            "answer": question_data["options"][0]  # First option
        }
        
        # Submit answer
        submit_response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
        assert submit_response.status_code == 200
        
        # Get score
        response = client.get(f"/api/v1/sessions/{session_id}/score")
        assert response.status_code == 200
        
        score_data = response.json()
        
        # Verify score reflects the answered question
        assert score_data["total_questions"] == 1
        assert score_data["correct_answers"] in [0, 1]
        assert score_data["incorrect_answers"] in [0, 1]
        assert score_data["correct_answers"] + score_data["incorrect_answers"] == 1
        
        # Verify accuracy calculation
        expected_accuracy = (score_data["correct_answers"] / score_data["total_questions"]) * 100
        assert abs(score_data["accuracy_percentage"] - expected_accuracy) < 0.01

    def test_get_session_score_invalid_session_id(self, client: TestClient) -> None:
        """
        Test getting score with invalid session ID.
        
        GIVEN an invalid session ID
        WHEN requesting the session score
        THEN return 404 error
        """
        invalid_session_id = "invalid-session-id"
        
        response = client.get(f"/api/v1/sessions/{invalid_session_id}/score")
        assert response.status_code == 404
        
        error_data = response.json()
        assert "detail" in error_data

    def test_get_session_score_completed_session(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test getting score for a completed session.
        
        GIVEN a completed session
        WHEN requesting the session score
        THEN return final score with all metrics
        """
        # Create session with 1 question
        session_data = valid_session_data.copy()
        session_data["total_questions"] = 1
        
        session_response = client.post("/api/v1/sessions/", json=session_data)
        assert session_response.status_code == 200
        session_info = session_response.json()
        session_id = session_info["session_id"]
        
        # Get and answer the only question
        question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
        assert question_response.status_code == 200
        question_data = question_response.json()
        
        answer_data = {
            "question_id": question_data["question_id"],
            "answer": question_data["options"][0]
        }
        
        submit_response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
        assert submit_response.status_code == 200
        
        # Complete the session
        complete_response = client.post(f"/api/v1/sessions/{session_id}/complete")
        assert complete_response.status_code == 200
        
        # Get score
        response = client.get(f"/api/v1/sessions/{session_id}/score")
        assert response.status_code == 200
        
        score_data = response.json()
        
        # Verify final score
        assert score_data["total_questions"] == 1
        assert score_data["correct_answers"] in [0, 1]
        assert score_data["incorrect_answers"] in [0, 1]
        assert score_data["time_taken_seconds"] >= 0
        
        # Verify topic performance includes the session topic
        assert "Physics" in score_data["topic_performance"]
        assert "Medium" in score_data["topic_performance"]["Physics"]

    def test_get_session_score_accuracy_calculation(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test accuracy percentage calculation.
        
        GIVEN a session with multiple answers
        WHEN requesting the session score
        THEN return accurate accuracy percentage
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
            "answer": question_data["correct_answer"]  # Correct answer
        }
        
        submit_response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
        assert submit_response.status_code == 200
        
        # Answer second question
        question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
        question_data = question_response.json()
        
        answer_data = {
            "question_id": question_data["question_id"],
            "answer": question_data["options"][0]  # Might be wrong
        }
        
        submit_response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
        assert submit_response.status_code == 200
        
        # Get score
        response = client.get(f"/api/v1/sessions/{session_id}/score")
        assert response.status_code == 200
        
        score_data = response.json()
        
        # Verify accuracy calculation
        expected_accuracy = (score_data["correct_answers"] / score_data["total_questions"]) * 100
        assert abs(score_data["accuracy_percentage"] - expected_accuracy) < 0.01
        assert 0 <= score_data["accuracy_percentage"] <= 100
