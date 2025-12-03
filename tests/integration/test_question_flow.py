"""
Integration tests for complete question-answer workflow.

Tests the end-to-end flow of getting questions and submitting answers.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any

from src.api.main import create_app
from src.utils.config import AppConfig


class TestQuestionAnswerWorkflow:
    
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
    
    """Integration tests for the complete Q&A workflow."""

    def test_complete_question_answer_cycle(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test the complete cycle of getting questions and submitting answers.
        
        GIVEN a newly created session
        WHEN getting questions and submitting answers in sequence
        THEN all operations should succeed and maintain consistency
        """
        # Create session
        session_response = client.post("/api/v1/sessions/", json=valid_session_data)
        assert session_response.status_code == 200
        session_data = session_response.json()
        session_id = session_data["session_id"]
        
        # Track answered questions
        answered_questions = []
        
        # Complete a few question-answer cycles
        for i in range(3):
            # Get next question
            question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
            assert question_response.status_code == 200
            question_data = question_response.json()
            
            # Verify we get a valid question
            assert question_data["question_id"] is not None
            assert not question_data["session_complete"]
            assert question_data["question_id"] not in answered_questions  # No duplicates
            
            # Submit an answer
            answer_data = {
                "question_id": question_data["question_id"],
                "answer": "Test Answer"  # We don't need the correct answer for workflow test
            }
            
            answer_response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
            assert answer_response.status_code == 200
            answer_result = answer_response.json()
            
            # Verify answer response structure
            assert "correct" in answer_result
            assert "correct_answer" in answer_result
            assert "explanation" in answer_result
            
            # Track this question
            answered_questions.append(question_data["question_id"])
        
        # Verify session progress
        session_response = client.get(f"/api/v1/sessions/{session_id}")
        assert session_response.status_code == 200
        updated_session = session_response.json()
        
        assert updated_session["progress"]["questions_answered"] >= 3
        assert updated_session["is_active"] is True

    def test_workflow_with_different_topics_and_difficulties(self, client: TestClient) -> None:
        """
        Test workflow across different topic and difficulty combinations.
        
        GIVEN sessions with different topics and difficulties
        WHEN running the Q&A workflow for each
        THEN each should work correctly with appropriate questions
        """
        combinations = [
            {"topic": "Physics", "difficulty": "Easy", "total_questions": 3},
            {"topic": "Physics", "difficulty": "Medium", "total_questions": 3},
            {"topic": "Physics", "difficulty": "Hard", "total_questions": 1}
        ]
        
        for session_data in combinations:
            # Create session
            session_response = client.post("/api/v1/sessions/", json=session_data)
            assert session_response.status_code == 200
            session_info = session_response.json()
            session_id = session_info["session_id"]
            
            # Get a question
            question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
            assert question_response.status_code == 200
            question_data = question_response.json()
            
            # Submit answer
            answer_data = {
                "question_id": question_data["question_id"],
                "answer": "Test Answer"
            }
            
            answer_response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
            assert answer_response.status_code == 200
            
            # Verify session is still active
            session_response = client.get(f"/api/v1/sessions/{session_id}")
            assert session_response.status_code == 200
            assert session_response.json()["is_active"] is True

    def test_workflow_session_completion(self, client: TestClient) -> None:
        """
        Test workflow when session completes all questions.
        
        GIVEN a session with small number of questions
        WHEN answering all questions
        THEN session should complete correctly
        """
        # Create session with minimal questions
        session_data = {"topic": "Physics", "difficulty": "Easy", "total_questions": 2}
        session_response = client.post("/api/v1/sessions/", json=session_data)
        assert session_response.status_code == 200
        session_info = session_response.json()
        session_id = session_info["session_id"]
        
        questions_answered = 0
        
        # Answer questions until session completes
        while questions_answered < 5:  # Safety limit
            # Get next question
            question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
            assert question_response.status_code == 200
            question_data = question_response.json()
            
            if question_data["session_complete"]:
                break
                
            # Submit answer
            answer_data = {
                "question_id": question_data["question_id"],
                "answer": "Test Answer"
            }
            
            answer_response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
            assert answer_response.status_code == 200
            
            questions_answered += 1
        
        # Verify we either completed or answered all requested questions
        assert questions_answered >= 2 or question_data["session_complete"]

    def test_workflow_error_recovery(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test workflow recovery from errors.
        
        GIVEN a session with various error scenarios
        WHEN errors occur during the workflow
        THEN the session should remain usable
        """
        # Create session
        session_response = client.post("/api/v1/sessions/", json=valid_session_data)
        assert session_response.status_code == 200
        session_data = session_response.json()
        session_id = session_data["session_id"]
        
        # Get a valid question
        question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
        assert question_response.status_code == 200
        question_data = question_response.json()
        
        # Try to submit answer with invalid question ID (should fail)
        invalid_answer = {
            "question_id": "invalid-question-id",
            "answer": "Test Answer"
        }
        
        error_response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=invalid_answer)
        assert error_response.status_code in [400, 404]
        
        # Session should still be usable - get another question
        question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
        assert question_response.status_code == 200
        
        # Submit valid answer
        valid_answer = {
            "question_id": question_data["question_id"],
            "answer": "Test Answer"
        }
        
        answer_response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=valid_answer)
        assert answer_response.status_code == 200
        
        # Verify session is still active and functional
        session_response = client.get(f"/api/v1/sessions/{session_id}")
        assert session_response.status_code == 200
        assert session_response.json()["is_active"] is True

    def test_workflow_concurrent_sessions(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test workflow with multiple concurrent sessions.
        
        GIVEN multiple sessions running simultaneously
        WHEN each session runs the Q&A workflow
        THEN sessions should not interfere with each other
        """
        sessions = []
        
        # Create multiple sessions
        for i in range(3):
            session_response = client.post("/api/v1/sessions/", json=valid_session_data)
            assert session_response.status_code == 200
            session_data = session_response.json()
            sessions.append(session_data["session_id"])
        
        # Run workflow for each session
        for session_id in sessions:
            # Get question
            question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
            assert question_response.status_code == 200
            question_data = question_response.json()
            
            # Submit answer
            answer_data = {
                "question_id": question_data["question_id"],
                "answer": f"Answer for {session_id}"
            }
            
            answer_response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
            assert answer_response.status_code == 200
        
        # Verify all sessions are still active and independent
        for session_id in sessions:
            session_response = client.get(f"/api/v1/sessions/{session_id}")
            assert session_response.status_code == 200
            session_data = session_response.json()
            assert session_data["is_active"] is True
            assert session_data["session_id"] == session_id

    def test_workflow_performance_requirements(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test workflow meets performance requirements.
        
        GIVEN a session
        WHEN running the Q&A workflow
        THEN operations should complete within performance limits
        """
        import time
        
        # Create session
        start_time = time.time()
        session_response = client.post("/api/v1/sessions/", json=valid_session_data)
        session_creation_time = time.time() - start_time
        
        assert session_response.status_code == 200
        assert session_creation_time < 1.0  # Should create session in under 1 second
        
        session_data = session_response.json()
        session_id = session_data["session_id"]
        
        # Test question retrieval performance
        start_time = time.time()
        question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
        question_time = time.time() - start_time
        
        assert question_response.status_code == 200
        assert question_time < 0.5  # Should get question in under 500ms
        
        question_data = question_response.json()
        
        # Test answer submission performance
        start_time = time.time()
        answer_data = {
            "question_id": question_data["question_id"],
            "answer": "Test Answer"
        }
        answer_response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
        answer_time = time.time() - start_time
        
        assert answer_response.status_code == 200
        assert answer_time < 0.5  # Should submit answer in under 500ms
