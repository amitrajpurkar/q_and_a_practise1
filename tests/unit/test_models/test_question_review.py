"""
Unit tests for QuestionReview model.

Tests the QuestionReview data model following TDD approach
for User Story 5 - Question Review on Results Page.
"""

import pytest
from src.models.question_review import QuestionReview


class TestQuestionReview:
    """Test suite for QuestionReview model."""

    def test_create_correct_answer_review(self):
        """Test creating a review for a correct answer."""
        review = QuestionReview(
            question_number=1,
            question_text="What is 2 + 2?",
            user_answer="4",
            correct_answer="4",
            correct=True
        )
        
        assert review.question_number == 1
        assert review.question_text == "What is 2 + 2?"
        assert review.user_answer == "4"
        assert review.correct_answer == "4"
        assert review.correct is True

    def test_create_incorrect_answer_review(self):
        """Test creating a review for an incorrect answer."""
        review = QuestionReview(
            question_number=2,
            question_text="What is the capital of France?",
            user_answer="London",
            correct_answer="Paris",
            correct=False
        )
        
        assert review.question_number == 2
        assert review.user_answer == "London"
        assert review.correct_answer == "Paris"
        assert review.correct is False

    def test_review_with_explanation(self):
        """Test review with optional explanation field."""
        review = QuestionReview(
            question_number=3,
            question_text="What is H2O?",
            user_answer="Water",
            correct_answer="Water",
            correct=True,
            explanation="H2O is the chemical formula for water."
        )
        
        assert review.explanation == "H2O is the chemical formula for water."

    def test_review_to_dict(self):
        """Test converting review to dictionary."""
        review = QuestionReview(
            question_number=1,
            question_text="Test question",
            user_answer="A",
            correct_answer="B",
            correct=False,
            explanation="Test explanation"
        )
        
        result = review.to_dict()
        
        assert result["question_number"] == 1
        assert result["question_text"] == "Test question"
        assert result["user_answer"] == "A"
        assert result["correct_answer"] == "B"
        assert result["correct"] is False
        assert result["explanation"] == "Test explanation"

    def test_review_from_dict(self):
        """Test creating review from dictionary."""
        data = {
            "question_number": 5,
            "question_text": "Sample question",
            "user_answer": "C",
            "correct_answer": "C",
            "correct": True,
            "explanation": None
        }
        
        review = QuestionReview.from_dict(data)
        
        assert review.question_number == 5
        assert review.question_text == "Sample question"
        assert review.user_answer == "C"
        assert review.correct is True

    def test_review_str_representation(self):
        """Test string representation of review."""
        review = QuestionReview(
            question_number=1,
            question_text="Test",
            user_answer="A",
            correct_answer="A",
            correct=True
        )
        
        str_repr = str(review)
        assert "Q1" in str_repr
        assert "Correct" in str_repr

    def test_review_equality(self):
        """Test equality comparison of reviews."""
        review1 = QuestionReview(
            question_number=1,
            question_text="Test",
            user_answer="A",
            correct_answer="A",
            correct=True
        )
        review2 = QuestionReview(
            question_number=1,
            question_text="Test",
            user_answer="A",
            correct_answer="A",
            correct=True
        )
        
        assert review1 == review2


class TestQuestionReviewList:
    """Test suite for list of QuestionReview objects."""

    def test_is_perfect_score_all_correct(self):
        """Test detecting perfect score when all answers are correct."""
        reviews = [
            QuestionReview(i, f"Q{i}", "A", "A", True)
            for i in range(1, 11)
        ]
        
        all_correct = all(r.correct for r in reviews)
        assert all_correct is True

    def test_is_perfect_score_with_incorrect(self):
        """Test detecting non-perfect score with incorrect answers."""
        reviews = [
            QuestionReview(1, "Q1", "A", "A", True),
            QuestionReview(2, "Q2", "B", "C", False),  # Incorrect
            QuestionReview(3, "Q3", "A", "A", True),
        ]
        
        all_correct = all(r.correct for r in reviews)
        assert all_correct is False

    def test_count_correct_answers(self):
        """Test counting correct answers in review list."""
        reviews = [
            QuestionReview(1, "Q1", "A", "A", True),
            QuestionReview(2, "Q2", "B", "C", False),
            QuestionReview(3, "Q3", "D", "D", True),
            QuestionReview(4, "Q4", "A", "B", False),
        ]
        
        correct_count = sum(1 for r in reviews if r.correct)
        incorrect_count = sum(1 for r in reviews if not r.correct)
        
        assert correct_count == 2
        assert incorrect_count == 2

    def test_filter_incorrect_only(self):
        """Test filtering to show only incorrect answers."""
        reviews = [
            QuestionReview(1, "Q1", "A", "A", True),
            QuestionReview(2, "Q2", "B", "C", False),
            QuestionReview(3, "Q3", "D", "D", True),
        ]
        
        incorrect_only = [r for r in reviews if not r.correct]
        
        assert len(incorrect_only) == 1
        assert incorrect_only[0].question_number == 2

    def test_serialize_review_list(self):
        """Test serializing list of reviews to JSON-compatible format."""
        reviews = [
            QuestionReview(1, "Q1", "A", "A", True),
            QuestionReview(2, "Q2", "B", "C", False),
        ]
        
        serialized = [r.to_dict() for r in reviews]
        
        assert len(serialized) == 2
        assert serialized[0]["question_number"] == 1
        assert serialized[1]["correct"] is False

    def test_deserialize_review_list(self):
        """Test deserializing list of reviews from JSON-compatible format."""
        data = [
            {"question_number": 1, "question_text": "Q1", "user_answer": "A", 
             "correct_answer": "A", "correct": True, "explanation": None},
            {"question_number": 2, "question_text": "Q2", "user_answer": "B", 
             "correct_answer": "C", "correct": False, "explanation": "Wrong choice"},
        ]
        
        reviews = [QuestionReview.from_dict(d) for d in data]
        
        assert len(reviews) == 2
        assert reviews[0].correct is True
        assert reviews[1].explanation == "Wrong choice"
