"""
Unit tests for question randomization algorithm in QuestionService.

Tests the randomization logic and duplicate prevention.
"""

import pytest
from unittest.mock import Mock, patch
from typing import List, Dict, Any
import random

from src.services.question_service import QuestionService
from src.models.question import Question
from src.utils.exceptions import QuestionError


class TestQuestionRandomization:
    """Unit tests for question randomization functionality."""

    @pytest.fixture
    def mock_question_bank(self) -> Mock:
        """Create a mock question bank with test data."""
        bank = Mock()
        
        # Create test questions
        questions = [
            Question(
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
            ),
            Question(
                id="physics_2",
                topic="Physics",
                question_text="What is the unit of force?",
                option1="Newton",
                option2="Joule",
                option3="Watt",
                option4="Pascal",
                correct_answer="Newton",
                difficulty="Easy",
                tag="Physics-Easy"
            ),
            Question(
                id="physics_3",
                topic="Physics",
                question_text="What is speed of light?",
                option1="3x10^8 m/s",
                option2="2x10^8 m/s",
                option3="4x10^8 m/s",
                option4="1x10^8 m/s",
                correct_answer="3x10^8 m/s",
                difficulty="Medium",
                tag="Physics-Medium"
            ),
            Question(
                id="chemistry_1",
                topic="Chemistry",
                question_text="What is H2O?",
                option1="Water",
                option2="Oxygen",
                option3="Hydrogen",
                option4="Carbon",
                correct_answer="Water",
                difficulty="Easy",
                tag="Chemistry-Easy"
            ),
            Question(
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
        ]
        
        bank.get_questions_by_criteria.return_value = questions
        bank.get_all_questions.return_value = questions
        return bank

    @pytest.fixture
    def question_service(self, mock_question_bank: Mock) -> QuestionService:
        """Create QuestionService instance with mock dependencies."""
        return QuestionService(mock_question_bank)

    def test_get_random_question_returns_valid_question(self, question_service: QuestionService) -> None:
        """
        Test that get_random_question returns a valid question.
        
        GIVEN valid topic and difficulty
        WHEN requesting a random question
        THEN return a valid Question object
        """
        topic = "Physics"
        difficulty = "Easy"
        
        question = question_service.get_random_question(topic, difficulty)
        
        assert isinstance(question, Question)
        assert question.topic == topic
        assert question.difficulty == difficulty
        assert question.id is not None
        assert question.question_text is not None

    def test_get_random_question_with_exclusions(self, question_service: QuestionService) -> None:
        """
        Test random question retrieval with exclusions.
        
        GIVEN valid topic, difficulty, and excluded questions
        WHEN requesting a random question
        THEN return a question not in exclusions
        """
        topic = "Physics"
        difficulty = "Easy"
        exclusions = ["physics_1"]
        
        question = question_service.get_random_question(topic, difficulty, exclusions)
        
        assert isinstance(question, Question)
        assert question.topic == topic
        assert question.difficulty == difficulty
        assert question.id not in exclusions

    def test_get_random_question_no_available_questions(self, question_service: QuestionService) -> None:
        """
        Test behavior when no questions are available.
        
        GIVEN topic/difficulty with no matching questions
        WHEN requesting a random question
        THEN raise QuestionError
        """
        topic = "NonExistent"
        difficulty = "Easy"
        
        with pytest.raises(QuestionError) as exc_info:
            question_service.get_random_question(topic, difficulty)
        
        assert "No questions available" in str(exc_info.value)

    def test_get_random_question_all_questions_excluded(self, question_service: QuestionService) -> None:
        """
        Test behavior when all questions are excluded.
        
        GIVEN topic/difficulty with all questions excluded
        WHEN requesting a random question
        THEN raise QuestionError
        """
        topic = "Physics"
        difficulty = "Easy"
        exclusions = ["physics_1", "physics_2"]  # All Easy Physics questions
        
        with pytest.raises(QuestionError) as exc_info:
            question_service.get_random_question(topic, difficulty, exclusions)
        
        assert "No questions available" in str(exc_info.value)

    def test_randomization_distribution(self, question_service: QuestionService) -> None:
        """
        Test that randomization is properly distributed.
        
        GIVEN multiple requests for random questions
        WHEN requesting many questions
        THEN distribution should be reasonably uniform
        """
        topic = "Physics"
        difficulty = "Easy"
        
        # Get many random questions
        questions = []
        for _ in range(100):
            question = question_service.get_random_question(topic, difficulty)
            questions.append(question.id)
        
        # Count occurrences
        counts = {}
        for q_id in questions:
            counts[q_id] = counts.get(q_id, 0) + 1
        
        # Should have both physics_1 and physics_2
        assert len(counts) >= 2
        assert "physics_1" in counts
        assert "physics_2" in counts
        
        # Distribution should be reasonable (not too skewed)
        # This is probabilistic, but with 100 samples should be roughly even
        for count in counts.values():
            assert count >= 10  # Each should appear at least 10 times

    def test_fisher_yates_shuffle_implementation(self, question_service: QuestionService) -> None:
        """
        Test that Fisher-Yates shuffle is properly implemented.
        
        GIVEN a list of questions
        WHEN shuffling multiple times
        THEN results should be different and properly randomized
        """
        # Get the list of available questions
        questions = question_service._question_bank.get_questions_by_criteria("Physics", "Easy")
        original_order = [q.id for q in questions]
        
        # Shuffle multiple times and verify different orders
        shuffled_orders = []
        for _ in range(10):
            shuffled = question_service._shuffle_questions(questions)
            shuffled_order = [q.id for q in shuffled]
            shuffled_orders.append(shuffled_order)
        
        # At least some shuffles should be different from original
        different_from_original = any(order != original_order for order in shuffled_orders)
        assert different_from_original, "Shuffle should produce different orders"
        
        # All shuffles should contain the same elements
        for shuffled_order in shuffled_orders:
            assert sorted(shuffled_order) == sorted(original_order)

    def test_duplicate_prevention_in_session(self, question_service: QuestionService) -> None:
        """
        Test that duplicates are prevented within a session.
        
        GIVEN a session with asked questions
        WHEN requesting new questions
        THEN no duplicates should be returned
        """
        topic = "Physics"
        difficulty = "Easy"
        asked_questions = set()
        
        # Get multiple questions without duplicates
        for _ in range(2):  # There are 2 Easy Physics questions
            question = question_service.get_random_question(topic, difficulty, list(asked_questions))
            assert question.id not in asked_questions
            asked_questions.add(question.id)
        
        # Next request should fail (no more questions)
        with pytest.raises(QuestionError):
            question_service.get_random_question(topic, difficulty, list(asked_questions))

    def test_random_question_with_different_parameters(self, question_service: QuestionService) -> None:
        """
        Test randomization with different topic/difficulty combinations.
        
        GIVEN various topic and difficulty combinations
        WHEN requesting random questions
        THEN return appropriate questions for each combination
        """
        test_cases = [
            ("Physics", "Easy"),
            ("Physics", "Medium"),
            ("Chemistry", "Easy"),
            ("Math", "Easy")
        ]
        
        for topic, difficulty in test_cases:
            question = question_service.get_random_question(topic, difficulty)
            assert question.topic == topic
            assert question.difficulty == difficulty

    def test_random_question_thread_safety(self, question_service: QuestionService) -> None:
        """
        Test that randomization is thread-safe.
        
        GIVEN multiple concurrent requests
        WHEN requesting random questions simultaneously
        THEN all requests should succeed without errors
        """
        import threading
        import time
        
        results = []
        errors = []
        
        def get_question():
            try:
                question = question_service.get_random_question("Physics", "Easy")
                results.append(question.id)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=get_question)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 10, "Not all requests completed"

    def test_random_question_performance(self, question_service: QuestionService) -> None:
        """
        Test performance of random question selection.
        
        GIVEN a large number of requests
        WHEN requesting random questions
        THEN performance should be acceptable
        """
        import time
        
        start_time = time.time()
        
        # Make many requests
        for _ in range(1000):
            question = question_service.get_random_question("Physics", "Easy")
            assert question is not None
        
        elapsed_time = time.time() - start_time
        
        # Should complete 1000 requests in reasonable time (less than 1 second)
        assert elapsed_time < 1.0, f"Performance issue: {elapsed_time:.3f}s for 1000 requests"

    def test_random_question_with_empty_exclusions(self, question_service: QuestionService) -> None:
        """
        Test behavior with empty exclusions list.
        
        GIVEN valid parameters and empty exclusions
        WHEN requesting random question
        THEN should work same as no exclusions
        """
        question1 = question_service.get_random_question("Physics", "Easy", [])
        question2 = question_service.get_random_question("Physics", "Easy")
        
        # Both should be valid questions
        assert isinstance(question1, Question)
        assert isinstance(question2, Question)
        assert question1.topic == "Physics"
        assert question1.difficulty == "Easy"
        assert question2.topic == "Physics"
        assert question2.difficulty == "Easy"
