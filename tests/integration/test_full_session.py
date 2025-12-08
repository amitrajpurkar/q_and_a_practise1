"""
Integration tests for complete session workflow.

Tests the entire Q&A session lifecycle from creation to completion,
including question presentation, answer submission, and score tracking.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any
import time

from src.api.main import create_app
from src.utils.config import AppConfig


class TestFullSessionWorkflow:
    """Integration tests for the complete Q&A session workflow."""

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

    def test_complete_session_workflow_all_correct(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test complete workflow with all correct answers.
        
        GIVEN a new session
        WHEN answering all questions correctly and completing
        THEN track progress accurately and return perfect score
        """
        # Create session
        session_response = client.post("/api/v1/sessions/", json=valid_session_data)
        assert session_response.status_code == 200
        session_info = session_response.json()
        session_id = session_info["session_id"]
        
        answered_questions = []
        
        # Answer all questions correctly
        for i in range(valid_session_data["total_questions"]):
            # Get question
            question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
            assert question_response.status_code == 200
            question_data = question_response.json()
            
            # Verify we get a valid question
            assert question_data["question_id"] is not None
            assert question_data["question_text"] is not None
            assert question_data["options"] is not None
            assert len(question_data["options"]) == 4
            assert question_data["session_complete"] is False
            
            # Track answered questions to ensure no duplicates
            assert question_data["question_id"] not in answered_questions
            answered_questions.append(question_data["question_id"])
            
            # Submit correct answer
            answer_data = {
                "question_id": question_data["question_id"],
                "answer": question_data["correct_answer"]
            }
            
            submit_response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
            assert submit_response.status_code == 200
            
            answer_result = submit_response.json()
            assert answer_result["correct"] is True
            assert answer_result["correct_answer"] == question_data["correct_answer"]
        
        # Verify session is complete
        final_question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
        assert final_question_response.status_code == 200
        final_question_data = final_question_response.json()
        assert final_question_data["session_complete"] is True
        
        # Get current score before completion
        score_response = client.get(f"/api/v1/sessions/{session_id}/score")
        assert score_response.status_code == 200
        score_data = score_response.json()
        assert score_data["total_questions"] == 3
        assert score_data["correct_answers"] == 3
        assert score_data["incorrect_answers"] == 0
        assert score_data["accuracy_percentage"] == 100.0
        
        # Complete session
        complete_response = client.post(f"/api/v1/sessions/{session_id}/complete")
        assert complete_response.status_code == 200
        
        final_score = complete_response.json()
        assert final_score["total_questions"] == 3
        assert final_score["correct_answers"] == 3
        assert final_score["incorrect_answers"] == 0
        assert final_score["accuracy_percentage"] == 100.0
        assert final_score["time_taken_seconds"] >= 0

    def test_complete_session_workflow_mixed_answers(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test complete workflow with mixed correct/incorrect answers.
        
        GIVEN a new session
        WHEN answering some correctly and some incorrectly
        THEN track progress and return accurate score
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
        answer_result = submit_response.json()
        assert answer_result["correct"] is True
        
        # Answer second question incorrectly
        question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
        question_data = question_response.json()
        
        answer_data = {
            "question_id": question_data["question_id"],
            "answer": "Definitely wrong answer"
        }
        
        submit_response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
        assert submit_response.status_code == 200
        answer_result = submit_response.json()
        assert answer_result["correct"] is False
        
        # Complete session
        complete_response = client.post(f"/api/v1/sessions/{session_id}/complete")
        assert complete_response.status_code == 200
        
        final_score = complete_response.json()
        assert final_score["total_questions"] == 2
        assert final_score["correct_answers"] == 1
        assert final_score["incorrect_answers"] == 1
        assert final_score["accuracy_percentage"] == 50.0

    def test_complete_session_workflow_score_tracking(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test score tracking throughout session.
        
        GIVEN a new session
        WHEN checking score after each answer
        THEN score updates progressively and accurately
        """
        # Create session with 2 questions
        session_data = valid_session_data.copy()
        session_data["total_questions"] = 2
        
        session_response = client.post("/api/v1/sessions/", json=session_data)
        assert session_response.status_code == 200
        session_info = session_response.json()
        session_id = session_info["session_id"]
        
        # Check initial score
        score_response = client.get(f"/api/v1/sessions/{session_id}/score")
        assert score_response.status_code == 200
        score_data = score_response.json()
        assert score_data["total_questions"] == 0
        assert score_data["correct_answers"] == 0
        assert score_data["incorrect_answers"] == 0
        assert score_data["accuracy_percentage"] == 0.0
        
        # Answer first question correctly
        question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
        question_data = question_response.json()
        
        answer_data = {
            "question_id": question_data["question_id"],
            "answer": question_data["correct_answer"]
        }
        
        submit_response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
        assert submit_response.status_code == 200
        
        # Check score after first answer
        score_response = client.get(f"/api/v1/sessions/{session_id}/score")
        assert score_response.status_code == 200
        score_data = score_response.json()
        assert score_data["total_questions"] == 1
        assert score_data["correct_answers"] == 1
        assert score_data["incorrect_answers"] == 0
        assert score_data["accuracy_percentage"] == 100.0
        
        # Answer second question incorrectly
        question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
        question_data = question_response.json()
        
        answer_data = {
            "question_id": question_data["question_id"],
            "answer": "Wrong answer"
        }
        
        submit_response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
        assert submit_response.status_code == 200
        
        # Check score after second answer
        score_response = client.get(f"/api/v1/sessions/{session_id}/score")
        assert score_response.status_code == 200
        score_data = score_response.json()
        assert score_data["total_questions"] == 2
        assert score_data["correct_answers"] == 1
        assert score_data["incorrect_answers"] == 1
        assert score_data["accuracy_percentage"] == 50.0
        
        # Complete session and verify final score matches
        complete_response = client.post(f"/api/v1/sessions/{session_id}/complete")
        assert complete_response.status_code == 200
        
        final_score = complete_response.json()
        assert final_score["total_questions"] == score_data["total_questions"]
        assert final_score["correct_answers"] == score_data["correct_answers"]
        assert final_score["incorrect_answers"] == score_data["incorrect_answers"]
        assert final_score["accuracy_percentage"] == score_data["accuracy_percentage"]

    def test_complete_session_workflow_performance_breakdown(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test performance breakdown in complete workflow.
        
        GIVEN a session with multiple questions
        WHEN completing the session
        THEN return detailed performance breakdown by topic/difficulty
        """
        # Create session
        session_response = client.post("/api/v1/sessions/", json=valid_session_data)
        assert session_response.status_code == 200
        session_info = session_response.json()
        session_id = session_info["session_id"]
        
        # Answer 2 questions
        for i in range(2):
            question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
            question_data = question_response.json()
            
            # Alternate correct/incorrect answers
            if i == 0:
                answer = question_data["correct_answer"]
            else:
                answer = "Wrong answer"
            
            answer_data = {
                "question_id": question_data["question_id"],
                "answer": answer
            }
            
            submit_response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
            assert submit_response.status_code == 200
        
        # Complete session
        complete_response = client.post(f"/api/v1/sessions/{session_id}/complete")
        assert complete_response.status_code == 200
        
        final_score = complete_response.json()
        
        # Verify performance breakdown
        topic_performance = final_score["topic_performance"]
        assert isinstance(topic_performance, dict)
        
        # Should have Physics-Medium performance
        assert "Physics" in topic_performance
        assert "Medium" in topic_performance["Physics"]
        
        physics_medium = topic_performance["Physics"]["Medium"]
        assert physics_medium["total"] == 2
        assert physics_medium["correct"] == 1
        assert physics_medium["incorrect"] == 1

    def test_complete_session_workflow_time_tracking(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test time tracking throughout session workflow.
        
        GIVEN a new session
        WHEN completing the session after some time
        THEN track and report accurate session duration
        """
        # Create session
        session_response = client.post("/api/v1/sessions/", json=valid_session_data)
        assert session_response.status_code == 200
        session_info = session_response.json()
        session_id = session_info["session_id"]
        
        start_time = time.time()
        
        # Wait a bit and answer one question
        time.sleep(0.1)
        
        question_response = client.get(f"/api/v1/sessions/{session_id}/next-question")
        question_data = question_response.json()
        
        answer_data = {
            "question_id": question_data["question_id"],
            "answer": question_data["correct_answer"]
        }
        
        submit_response = client.post(f"/api/v1/sessions/{session_id}/submit-answer", json=answer_data)
        assert submit_response.status_code == 200
        
        # Wait a bit more
        time.sleep(0.1)
        
        # Complete session
        complete_response = client.post(f"/api/v1/sessions/{session_id}/complete")
        assert complete_response.status_code == 200
        
        final_score = complete_response.json()
        
        # Verify time tracking
        assert final_score["time_taken_seconds"] >= 0
        assert final_score["time_taken_seconds"] < 60  # Should be reasonable for test
        
        # Session should have end_time set
        session_get_response = client.get(f"/api/v1/sessions/{session_id}")
        assert session_get_response.status_code == 200
        session_data = session_get_response.json()
        assert session_data["end_time"] is not None
        assert session_data["is_active"] is False

    def test_complete_session_workflow_multiple_sessions(self, client: TestClient) -> None:
        """
        Test workflow with multiple concurrent sessions.
        
        GIVEN multiple sessions with different topics
        WHEN running workflows in parallel
        THEN each session tracks scores independently
        """
        # Create two sessions with different topics
        session1_data = {
            "topic": "Physics",
            "difficulty": "Easy",
            "total_questions": 2
        }
        
        session2_data = {
            "topic": "Physics", 
            "difficulty": "Medium",
            "total_questions": 2
        }
        
        # Create sessions
        session1_response = client.post("/api/v1/sessions/", json=session1_data)
        assert session1_response.status_code == 200
        session1_info = session1_response.json()
        session1_id = session1_info["session_id"]
        
        session2_response = client.post("/api/v1/sessions/", json=session2_data)
        assert session2_response.status_code == 200
        session2_info = session2_response.json()
        session2_id = session2_info["session_id"]
        
        # Answer questions in session 1
        for i in range(2):
            question_response = client.get(f"/api/v1/sessions/{session1_id}/next-question")
            question_data = question_response.json()
            
            answer_data = {
                "question_id": question_data["question_id"],
                "answer": question_data["correct_answer"]
            }
            
            submit_response = client.post(f"/api/v1/sessions/{session1_id}/submit-answer", json=answer_data)
            assert submit_response.status_code == 200
        
        # Answer questions in session 2
        for i in range(2):
            question_response = client.get(f"/api/v1/sessions/{session2_id}/next-question")
            question_data = question_response.json()
            
            answer_data = {
                "question_id": question_data["question_id"],
                "answer": "Wrong answer"  # All wrong
            }
            
            submit_response = client.post(f"/api/v1/sessions/{session2_id}/submit-answer", json=answer_data)
            assert submit_response.status_code == 200
        
        # Complete both sessions
        complete1_response = client.post(f"/api/v1/sessions/{session1_id}/complete")
        assert complete1_response.status_code == 200
        
        complete2_response = client.post(f"/api/v1/sessions/{session2_id}/complete")
        assert complete2_response.status_code == 200
        
        # Verify independent tracking
        score1 = complete1_response.json()
        score2 = complete2_response.json()
        
        assert score1["session_id"] == session1_id
        assert score1["correct_answers"] == 2
        assert score1["accuracy_percentage"] == 100.0
        
        assert score2["session_id"] == session2_id
        assert score2["correct_answers"] == 0
        assert score2["accuracy_percentage"] == 0.0
