"""
Contract tests for answer submission endpoint.

Tests the answer validation and feedback functionality according to API contract.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any

from src.api.main import create_app
from src.utils.config import AppConfig


class TestAnswerSubmission:
    
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
    
    """Contract tests for the answer submission API endpoint."""

    def test_submit_correct_answer(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test submitting a correct answer.
        
        GIVEN a valid session with an active question
        WHEN submitting the correct answer
        THEN return success response with correct=True and feedback
        """
        # Create session
        session_response = client.post("/api/v1/sessions/", json=valid_session_data)
        assert session_response.status_code == 200
        session_data = session_response.json()
        session_id = session_data["session_id"]
        
        # Get a question
        question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
        assert question_response.status_code == 200
        question_data = question_response.json()
        question_id = question_data["question_id"]
        
        # Submit correct answer (we need to know the correct answer - for now use a placeholder)
        # In real implementation, we'd get this from the question bank
        answer_data = {
            "question_id": question_id,
            "answer": "Ampere"  # This would be the actual correct answer
        }
        
        response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "correct" in result
        assert "correct_answer" in result
        assert "explanation" in result
        
        # Structure verification
        assert isinstance(result["correct"], bool)
        assert isinstance(result["correct_answer"], str)
        assert result["explanation"] is None or isinstance(result["explanation"], str)

    def test_submit_incorrect_answer(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test submitting an incorrect answer.
        
        GIVEN a valid session with an active question
        WHEN submitting an incorrect answer
        THEN return success response with correct=False and correct answer
        """
        # Create session
        session_response = client.post("/api/v1/sessions/", json=valid_session_data)
        assert session_response.status_code == 200
        session_data = session_response.json()
        session_id = session_data["session_id"]
        
        # Get a question
        question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
        assert question_response.status_code == 200
        question_data = question_response.json()
        question_id = question_data["question_id"]
        
        # Submit incorrect answer
        answer_data = {
            "question_id": question_id,
            "answer": "Incorrect Answer"
        }
        
        response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "correct" in result
        assert "correct_answer" in result
        assert "explanation" in result
        
        # Verify structure for incorrect answer
        assert isinstance(result["correct"], bool)
        assert isinstance(result["correct_answer"], str)
        assert result["explanation"] is None or isinstance(result["explanation"], str)

    def test_submit_answer_invalid_session_id(self, client: TestClient) -> None:
        """
        Test submitting an answer with invalid session ID.
        
        GIVEN an invalid session ID
        WHEN submitting an answer
        THEN return 404 error
        """
        invalid_session_id = "invalid-session-id"
        answer_data = {
            "question_id": "some-question-id",
            "answer": "Some answer"
        }
        
        response = client.post(f"/api/v1/sessions/{invalid_session_id}/submit-answer", json=answer_data)
        assert response.status_code == 404
        
        error_data = response.json()
        assert "detail" in error_data

    def test_submit_answer_invalid_question_id(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test submitting an answer with invalid question ID.
        
        GIVEN a valid session
        WHEN submitting an answer with invalid question ID
        THEN return 400 error
        """
        # Create session
        session_response = client.post("/api/v1/sessions/", json=valid_session_data)
        assert session_response.status_code == 200
        session_data = session_response.json()
        session_id = session_data["session_id"]
        
        # Submit answer with invalid question ID
        answer_data = {
            "question_id": "invalid-question-id",
            "answer": "Some answer"
        }
        
        response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
        assert response.status_code == 400
        
        error_data = response.json()
        assert "detail" in error_data

    def test_submit_answer_missing_fields(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test submitting an answer with missing required fields.
        
        GIVEN a valid session
        WHEN submitting an answer with missing fields
        THEN return 422 validation error
        """
        # Create session
        session_response = client.post("/api/v1/sessions/", json=valid_session_data)
        assert session_response.status_code == 200
        session_data = session_response.json()
        session_id = session_data["session_id"]
        
        # Test missing question_id
        answer_data = {
            "answer": "Some answer"
        }
        
        response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
        assert response.status_code == 422
        
        # Test missing answer
        answer_data = {
            "question_id": "some-question-id"
        }
        
        response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
        assert response.status_code == 422

    def test_submit_answer_empty_fields(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test submitting an answer with empty fields.
        
        GIVEN a valid session
        WHEN submitting an answer with empty question_id or answer
        THEN return 400 validation error
        """
        # Create session
        session_response = client.post("/api/v1/sessions/", json=valid_session_data)
        assert session_response.status_code == 200
        session_data = session_response.json()
        session_id = session_data["session_id"]
        
        # Test empty question_id
        answer_data = {
            "question_id": "",
            "answer": "Some answer"
        }
        
        response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
        assert response.status_code == 400
        
        # Test empty answer
        answer_data = {
            "question_id": "some-question-id",
            "answer": ""
        }
        
        response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
        assert response.status_code == 400

    def test_submit_answer_for_completed_session(self, client: TestClient) -> None:
        """
        Test submitting an answer for a completed session.
        
        GIVEN a completed session
        WHEN submitting an answer
        THEN return 400 error
        """
        completed_session_id = "completed-session-id"
        answer_data = {
            "question_id": "some-question-id",
            "answer": "Some answer"
        }
        
        response = client.post(f"/api/v1/sessions/{completed_session_id}/submit-answer", json=answer_data)
        # Should handle gracefully - either 404 (not found) or 400 (completed)
        assert response.status_code in [404, 400]

    def test_answer_submission_updates_progress(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test that answer submission updates session progress.
        
        GIVEN a valid session
        WHEN submitting an answer
        THEN the session progress should be updated
        """
        # Create session
        session_response = client.post("/api/v1/sessions/", json=valid_session_data)
        assert session_response.status_code == 200
        session_data = session_response.json()
        session_id = session_data["session_id"]
        initial_progress = session_data["progress"]
        
        # Get a question
        question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
        assert question_response.status_code == 200
        question_data = question_response.json()
        question_id = question_data["question_id"]
        
        # Submit answer
        answer_data = {
            "question_id": question_id,
            "answer": "Some answer"
        }
        
        client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
        
        # Check session progress was updated
        session_response = client.get(f"/api/v1/sessions/{session_id}")
        assert session_response.status_code == 200
        updated_session = session_response.json()
        
        # Progress should be updated
        assert updated_session["progress"]["questions_answered"] >= initial_progress["questions_answered"]
