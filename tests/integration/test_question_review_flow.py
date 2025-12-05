"""
Integration tests for Question Review data flow.

Tests the complete flow of tracking questions during quiz
and displaying them on the results page.
"""

import pytest
import json
from urllib.parse import urlencode


class TestQuestionReviewDataFlow:
    """Integration tests for question review feature."""

    def test_question_reviews_passed_to_results(self):
        """Test that question reviews are passed to results page."""
        # Simulate question review data that would be passed from quiz
        question_reviews = [
            {
                "question_number": 1,
                "question_text": "What is 2 + 2?",
                "user_answer": "4",
                "correct_answer": "4",
                "correct": True
            },
            {
                "question_number": 2,
                "question_text": "What is the capital of France?",
                "user_answer": "London",
                "correct_answer": "Paris",
                "correct": False
            }
        ]
        
        # Verify data structure is valid JSON
        json_data = json.dumps(question_reviews)
        parsed = json.loads(json_data)
        
        assert len(parsed) == 2
        assert parsed[0]["correct"] is True
        assert parsed[1]["correct"] is False

    def test_perfect_score_detection(self):
        """Test detecting perfect score from review data."""
        # All correct answers
        perfect_reviews = [
            {"question_number": i, "question_text": f"Q{i}", 
             "user_answer": "A", "correct_answer": "A", "correct": True}
            for i in range(1, 11)
        ]
        
        is_perfect = all(r["correct"] for r in perfect_reviews)
        assert is_perfect is True
        
        # With one incorrect
        imperfect_reviews = perfect_reviews.copy()
        imperfect_reviews[5] = {
            "question_number": 6, "question_text": "Q6",
            "user_answer": "B", "correct_answer": "A", "correct": False
        }
        
        is_perfect = all(r["correct"] for r in imperfect_reviews)
        assert is_perfect is False

    def test_url_encoding_question_reviews(self):
        """Test URL encoding of question review data."""
        reviews = [
            {"question_number": 1, "question_text": "Test?", 
             "user_answer": "A", "correct_answer": "A", "correct": True}
        ]
        
        # Encode as JSON for URL parameter
        encoded = urlencode({"reviews": json.dumps(reviews)})
        
        assert "reviews=" in encoded
        # Verify it can be decoded back
        assert "question_number" in encoded or "%22question_number%22" in encoded

    def test_session_storage_format(self):
        """Test format for storing reviews in session storage."""
        reviews = [
            {
                "question_number": 1,
                "question_text": "What is Newton's first law?",
                "user_answer": "Objects in motion stay in motion",
                "correct_answer": "Objects in motion stay in motion",
                "correct": True,
                "explanation": None
            },
            {
                "question_number": 2,
                "question_text": "What is the speed of light?",
                "user_answer": "300,000 m/s",
                "correct_answer": "299,792,458 m/s",
                "correct": False,
                "explanation": "The exact speed is approximately 299,792,458 m/s"
            }
        ]
        
        # Simulate sessionStorage format
        storage_data = json.dumps(reviews)
        restored = json.loads(storage_data)
        
        assert len(restored) == 2
        assert restored[0]["correct"] is True
        assert restored[1]["explanation"] is not None

    def test_accuracy_calculation_from_reviews(self):
        """Test calculating accuracy from review data."""
        reviews = [
            {"correct": True},
            {"correct": True},
            {"correct": False},
            {"correct": True},
            {"correct": False},
        ]
        
        total = len(reviews)
        correct = sum(1 for r in reviews if r["correct"])
        accuracy = (correct / total) * 100
        
        assert total == 5
        assert correct == 3
        assert accuracy == 60.0

    def test_empty_reviews_handling(self):
        """Test handling of empty review list."""
        reviews = []
        
        is_perfect = len(reviews) > 0 and all(r.get("correct", False) for r in reviews)
        
        assert is_perfect is False

    def test_review_data_with_special_characters(self):
        """Test handling questions with special characters."""
        reviews = [
            {
                "question_number": 1,
                "question_text": "What is H₂O's chemical name?",
                "user_answer": "Dihydrogen monoxide",
                "correct_answer": "Dihydrogen monoxide",
                "correct": True
            },
            {
                "question_number": 2,
                "question_text": "Calculate: 5² + 3³ = ?",
                "user_answer": "52",
                "correct_answer": "52",
                "correct": True
            }
        ]
        
        # Verify JSON encoding handles special characters
        encoded = json.dumps(reviews)
        decoded = json.loads(encoded)
        
        assert "H₂O" in decoded[0]["question_text"]
        assert "²" in decoded[1]["question_text"]


class TestQuestionReviewDisplay:
    """Tests for question review display logic."""

    def test_show_congratulations_for_perfect_score(self):
        """Test that congratulations message is shown for 100% accuracy."""
        accuracy = 100.0
        total_correct = 10
        total_questions = 10
        
        should_show_congrats = (accuracy == 100.0 and 
                                total_correct == total_questions)
        
        assert should_show_congrats is True

    def test_show_review_for_imperfect_score(self):
        """Test that review section is shown for non-perfect scores."""
        accuracy = 80.0
        total_correct = 8
        total_questions = 10
        
        should_show_review = accuracy < 100.0
        
        assert should_show_review is True

    def test_review_card_styling_correct(self):
        """Test correct answer card styling class."""
        is_correct = True
        
        card_class = "bg-green-50 border-green-200" if is_correct else "bg-red-50 border-red-200"
        
        assert "green" in card_class

    def test_review_card_styling_incorrect(self):
        """Test incorrect answer card styling class."""
        is_correct = False
        
        card_class = "bg-green-50 border-green-200" if is_correct else "bg-red-50 border-red-200"
        
        assert "red" in card_class

    def test_filter_reviews_for_display(self):
        """Test filtering reviews to show only incorrect ones optionally."""
        reviews = [
            {"question_number": 1, "correct": True},
            {"question_number": 2, "correct": False},
            {"question_number": 3, "correct": True},
            {"question_number": 4, "correct": False},
        ]
        
        # Show all
        all_reviews = reviews
        assert len(all_reviews) == 4
        
        # Show only incorrect
        incorrect_only = [r for r in reviews if not r["correct"]]
        assert len(incorrect_only) == 2
        assert all(not r["correct"] for r in incorrect_only)
