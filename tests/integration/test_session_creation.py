"""
Integration tests for session creation workflow.

Tests the complete session creation flow following TDD approach.
These tests should FAIL initially and PASS after implementation.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any

from src.api.main import create_app
from src.utils.config import AppConfig


class TestSessionCreationWorkflow:
    """
    Integration tests for session creation workflow.
    
    Tests the complete flow from topic/difficulty selection to session creation.
    """
    
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
            "total_questions": 10
        }
    
    def test_complete_session_creation_workflow(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test complete session creation workflow.
        
        GIVEN the application is running
        WHEN a user selects topic and difficulty and creates a session
        THEN the session should be created successfully with correct parameters
        """
        # Step 1: Get available topics
        topics_response = client.get("/api/v1/topics/")
        assert topics_response.status_code == 200
        topics = topics_response.json()
        assert valid_session_data["topic"] in topics
        
        # Step 2: Get available difficulties
        difficulties_response = client.get("/api/v1/difficulties/")
        assert difficulties_response.status_code == 200
        difficulties = difficulties_response.json()
        assert valid_session_data["difficulty"] in difficulties
        
        # Step 3: Create session
        session_response = client.post("/api/v1/sessions/", json=valid_session_data)
        assert session_response.status_code == 200
        
        session_data = session_response.json()
        assert session_data["topic"] == valid_session_data["topic"]
        assert session_data["difficulty"] == valid_session_data["difficulty"]
        assert session_data["total_questions"] == valid_session_data["total_questions"]
        assert "session_id" in session_data
        assert session_data["is_active"] is True
        assert session_data["current_question_index"] == 0
    
    def test_session_creation_with_invalid_topic(self, client: TestClient) -> None:
        """
        Test session creation with invalid topic.
        
        GIVEN the application is running
        WHEN a user tries to create a session with an invalid topic
        THEN the session creation should fail with appropriate error
        """
        invalid_data = {
            "topic": "InvalidTopic",
            "difficulty": "Medium",
            "total_questions": 10
        }
        
        response = client.post("/api/v1/sessions/", json=invalid_data)
        assert response.status_code == 400
        
        error_data = response.json()
        assert "detail" in error_data
        assert "error" in error_data["detail"]
        assert "Invalid topic" in error_data["detail"]["message"]
    
    def test_session_creation_with_invalid_difficulty(self, client: TestClient) -> None:
        """
        Test session creation with invalid difficulty.
        
        GIVEN the application is running
        WHEN a user tries to create a session with an invalid difficulty
        THEN the session creation should fail with appropriate error
        """
        invalid_data = {
            "topic": "Physics",
            "difficulty": "InvalidDifficulty",
            "total_questions": 10
        }
        
        response = client.post("/api/v1/sessions/", json=invalid_data)
        assert response.status_code == 400
        
        error_data = response.json()
        assert "detail" in error_data
        assert "error" in error_data["detail"]
        assert "Invalid difficulty" in error_data["detail"]["message"]
    
    def test_session_creation_with_invalid_question_count(self, client: TestClient) -> None:
        """
        Test session creation with invalid question count.
        
        GIVEN the application is running
        WHEN a user tries to create a session with invalid question count
        THEN the session creation should fail with appropriate error
        """
        invalid_data = {
            "topic": "Physics",
            "difficulty": "Medium",
            "total_questions": 100  # Exceeds maximum
        }
        
        response = client.post("/api/v1/sessions/", json=invalid_data)
        assert response.status_code == 400
        
        error_data = response.json()
        assert "detail" in error_data
        assert "error" in error_data["detail"]
        assert "cannot exceed" in error_data["detail"]["message"].lower()
    
    def test_session_creation_persistence(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test that created sessions persist and can be retrieved.
        
        GIVEN a session has been created
        WHEN the session is retrieved by ID
        THEN the session data should match the creation data
        """
        # Create session
        create_response = client.post("/api/v1/sessions/", json=valid_session_data)
        assert create_response.status_code == 200
        
        session_data = create_response.json()
        session_id = session_data["session_id"]
        
        # Retrieve session
        get_response = client.get(f"/api/v1/sessions/{session_id}")
        assert get_response.status_code == 200
        
        retrieved_data = get_response.json()
        assert retrieved_data["session_id"] == session_id
        assert retrieved_data["topic"] == valid_session_data["topic"]
        assert retrieved_data["difficulty"] == valid_session_data["difficulty"]
        assert retrieved_data["total_questions"] == valid_session_data["total_questions"]
    
    def test_session_creation_with_different_combinations(self, client: TestClient) -> None:
        """
        Test session creation with different topic/difficulty combinations.
        
        GIVEN the application supports multiple topics and difficulties
        WHEN sessions are created with different combinations
        THEN all sessions should be created successfully
        """
        combinations = [
            {"topic": "Physics", "difficulty": "Easy", "total_questions": 5},
            {"topic": "Chemistry", "difficulty": "Hard", "total_questions": 15},
            {"topic": "Math", "difficulty": "Medium", "total_questions": 20}
        ]
        
        for session_data in combinations:
            response = client.post("/api/v1/sessions/", json=session_data)
            assert response.status_code == 200
            
            created_session = response.json()
            assert created_session["topic"] == session_data["topic"]
            assert created_session["difficulty"] == session_data["difficulty"]
            assert created_session["total_questions"] == session_data["total_questions"]
    
    def test_session_creation_workflow_performance(self, client: TestClient, valid_session_data: Dict[str, Any]) -> None:
        """
        Test session creation workflow performance.
        
        GIVEN the application is running
        WHEN a session is created
        THEN the complete workflow should complete within performance requirements
        """
        import time
        
        start_time = time.time()
        
        # Get topics
        client.get("/api/v1/topics/")
        
        # Get difficulties
        client.get("/api/v1/difficulties/")
        
        # Create session
        response = client.post("/api/v1/sessions/", json=valid_session_data)
        
        end_time = time.time()
        
        workflow_time_ms = (end_time - start_time) * 1000
        assert workflow_time_ms < 500, f"Workflow time {workflow_time_ms}ms exceeds 500ms requirement"
        assert response.status_code == 200
