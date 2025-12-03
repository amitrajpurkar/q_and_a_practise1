"""
Contract tests for topics API endpoint.

Tests the API contract for topics endpoint following TDD approach.
These tests should FAIL initially and PASS after implementation.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any

from src.api.main import create_app
from src.utils.config import AppConfig


class TestTopicsEndpointContract:
    """
    Contract tests for topics API endpoint.
    
    Tests the public API contract to ensure it meets specification requirements.
    """
    
    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client for FastAPI application."""
        config = AppConfig(debug=True)
        app = create_app(config)
        return TestClient(app)
    
    @pytest.fixture
    def topics_endpoint(self) -> str:
        """Topics endpoint URL."""
        return "/api/v1/topics/"
    
    def test_topics_endpoint_returns_200(self, client: TestClient, topics_endpoint: str) -> None:
        """
        Test that topics endpoint returns 200 status code.
        
        GIVEN the topics endpoint is available
        WHEN a GET request is made to /api/v1/topics/
        THEN the response should have status code 200
        """
        response = client.get(topics_endpoint)
        assert response.status_code == 200
    
    def test_topics_endpoint_returns_json(self, client: TestClient, topics_endpoint: str) -> None:
        """
        Test that topics endpoint returns JSON response.
        
        GIVEN the topics endpoint is available
        WHEN a GET request is made to /api/v1/topics/
        THEN the response should have content-type application/json
        """
        response = client.get(topics_endpoint)
        assert response.headers["content-type"] == "application/json"
    
    def test_topics_endpoint_returns_array(self, client: TestClient, topics_endpoint: str) -> None:
        """
        Test that topics endpoint returns an array of strings.
        
        GIVEN the topics endpoint is available
        WHEN a GET request is made to /api/v1/topics/
        THEN the response should be a JSON array
        """
        response = client.get(topics_endpoint)
        data = response.json()
        assert isinstance(data, list)
    
    def test_topics_endpoint_contains_required_topics(self, client: TestClient, topics_endpoint: str) -> None:
        """
        Test that topics endpoint contains all required topics.
        
        GIVEN the topics endpoint is available
        WHEN a GET request is made to /api/v1/topics/
        THEN the response should contain Physics, Chemistry, and Math
        """
        response = client.get(topics_endpoint)
        topics = response.json()
        
        required_topics = ["Physics", "Chemistry", "Math"]
        for topic in required_topics:
            assert topic in topics, f"Required topic '{topic}' not found in response"
    
    def test_topics_endpoint_topics_are_strings(self, client: TestClient, topics_endpoint: str) -> None:
        """
        Test that all topics returned are strings.
        
        GIVEN the topics endpoint is available
        WHEN a GET request is made to /api/v1/topics/
        THEN all items in the response should be strings
        """
        response = client.get(topics_endpoint)
        topics = response.json()
        
        for topic in topics:
            assert isinstance(topic, str), f"Topic '{topic}' is not a string"
            assert len(topic.strip()) > 0, f"Topic '{topic}' is empty or whitespace"
    
    def test_topics_endpoint_no_duplicates(self, client: TestClient, topics_endpoint: str) -> None:
        """
        Test that topics endpoint returns no duplicate topics.
        
        GIVEN the topics endpoint is available
        WHEN a GET request is made to /api/v1/topics/
        THEN the response should contain no duplicate topics
        """
        response = client.get(topics_endpoint)
        topics = response.json()
        
        assert len(topics) == len(set(topics)), "Topics response contains duplicates"
    
    def test_topics_endpoint_handles_invalid_method(self, client: TestClient, topics_endpoint: str) -> None:
        """
        Test that topics endpoint properly handles invalid HTTP methods.
        
        GIVEN the topics endpoint is available
        WHEN a POST request is made to /api/v1/topics/
        THEN the response should have status code 405 (Method Not Allowed)
        """
        response = client.post(topics_endpoint)
        assert response.status_code == 405
    
    def test_topics_endpoint_response_time(self, client: TestClient, topics_endpoint: str) -> None:
        """
        Test that topics endpoint responds within acceptable time.
        
        GIVEN the topics endpoint is available
        WHEN a GET request is made to /api/v1/topics/
        THEN the response should be received within 200ms (performance requirement)
        """
        import time
        start_time = time.time()
        response = client.get(topics_endpoint)
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        assert response_time_ms < 200, f"Response time {response_time_ms}ms exceeds 200ms requirement"
        assert response.status_code == 200
