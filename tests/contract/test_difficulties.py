"""
Contract tests for difficulties API endpoint.

Tests the API contract for difficulties endpoint following TDD approach.
These tests should FAIL initially and PASS after implementation.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any

from src.api.main import create_app
from src.utils.config import AppConfig


class TestDifficultiesEndpointContract:
    """
    Contract tests for difficulties API endpoint.
    
    Tests the public API contract to ensure it meets specification requirements.
    """
    
    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client for FastAPI application."""
        config = AppConfig(debug=True)
        app = create_app(config)
        return TestClient(app)
    
    @pytest.fixture
    def difficulties_endpoint(self) -> str:
        """Difficulties endpoint URL."""
        return "/api/v1/difficulties/"
    
    def test_difficulties_endpoint_returns_200(self, client: TestClient, difficulties_endpoint: str) -> None:
        """
        Test that difficulties endpoint returns 200 status code.
        
        GIVEN the difficulties endpoint is available
        WHEN a GET request is made to /api/v1/difficulties/
        THEN the response should have status code 200
        """
        response = client.get(difficulties_endpoint)
        assert response.status_code == 200
    
    def test_difficulties_endpoint_returns_json(self, client: TestClient, difficulties_endpoint: str) -> None:
        """
        Test that difficulties endpoint returns JSON response.
        
        GIVEN the difficulties endpoint is available
        WHEN a GET request is made to /api/v1/difficulties/
        THEN the response should have content-type application/json
        """
        response = client.get(difficulties_endpoint)
        assert response.headers["content-type"] == "application/json"
    
    def test_difficulties_endpoint_returns_array(self, client: TestClient, difficulties_endpoint: str) -> None:
        """
        Test that difficulties endpoint returns an array of strings.
        
        GIVEN the difficulties endpoint is available
        WHEN a GET request is made to /api/v1/difficulties/
        THEN the response should be a JSON array
        """
        response = client.get(difficulties_endpoint)
        data = response.json()
        assert isinstance(data, list)
    
    def test_difficulties_endpoint_contains_required_difficulties(self, client: TestClient, difficulties_endpoint: str) -> None:
        """
        Test that difficulties endpoint contains all required difficulty levels.
        
        GIVEN the difficulties endpoint is available
        WHEN a GET request is made to /api/v1/difficulties/
        THEN the response should contain Easy, Medium, and Hard
        """
        response = client.get(difficulties_endpoint)
        difficulties = response.json()
        
        required_difficulties = ["Easy", "Medium", "Hard"]
        for difficulty in required_difficulties:
            assert difficulty in difficulties, f"Required difficulty '{difficulty}' not found in response"
    
    def test_difficulties_endpoint_difficulties_are_strings(self, client: TestClient, difficulties_endpoint: str) -> None:
        """
        Test that all difficulties returned are strings.
        
        GIVEN the difficulties endpoint is available
        WHEN a GET request is made to /api/v1/difficulties/
        THEN all items in the response should be strings
        """
        response = client.get(difficulties_endpoint)
        difficulties = response.json()
        
        for difficulty in difficulties:
            assert isinstance(difficulty, str), f"Difficulty '{difficulty}' is not a string"
            assert len(difficulty.strip()) > 0, f"Difficulty '{difficulty}' is empty or whitespace"
    
    def test_difficulties_endpoint_no_duplicates(self, client: TestClient, difficulties_endpoint: str) -> None:
        """
        Test that difficulties endpoint returns no duplicate difficulties.
        
        GIVEN the difficulties endpoint is available
        WHEN a GET request is made to /api/v1/difficulties/
        THEN the response should contain no duplicate difficulties
        """
        response = client.get(difficulties_endpoint)
        difficulties = response.json()
        
        assert len(difficulties) == len(set(difficulties)), "Difficulties response contains duplicates"
    
    def test_difficulties_endpoint_handles_invalid_method(self, client: TestClient, difficulties_endpoint: str) -> None:
        """
        Test that difficulties endpoint properly handles invalid HTTP methods.
        
        GIVEN the difficulties endpoint is available
        WHEN a POST request is made to /api/v1/difficulties/
        THEN the response should have status code 405 (Method Not Allowed)
        """
        response = client.post(difficulties_endpoint)
        assert response.status_code == 405
    
    def test_difficulties_endpoint_response_time(self, client: TestClient, difficulties_endpoint: str) -> None:
        """
        Test that difficulties endpoint responds within acceptable time.
        
        GIVEN the difficulties endpoint is available
        WHEN a GET request is made to /api/v1/difficulties/
        THEN the response should be received within 200ms (performance requirement)
        """
        import time
        start_time = time.time()
        response = client.get(difficulties_endpoint)
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        assert response_time_ms < 200, f"Response time {response_time_ms}ms exceeds 200ms requirement"
        assert response.status_code == 200
    
    def test_difficulties_endpoint_ordered_by_difficulty(self, client: TestClient, difficulties_endpoint: str) -> None:
        """
        Test that difficulties endpoint returns difficulties in logical order.
        
        GIVEN the difficulties endpoint is available
        WHEN a GET request is made to /api/v1/difficulties/
        THEN the response should be ordered from Easy to Hard
        """
        response = client.get(difficulties_endpoint)
        difficulties = response.json()
        
        expected_order = ["Easy", "Medium", "Hard"]
        assert difficulties == expected_order, f"Difficulties not in expected order. Got: {difficulties}"
