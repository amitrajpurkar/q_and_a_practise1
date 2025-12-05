"""
QuestionReview entity for Q&A Practice Application.

Implements the QuestionReview data model for tracking individual
question responses during a quiz session, following SOLID principles.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


@dataclass
class QuestionReview:
    """
    Tracks individual question responses including question number,
    question text, user answer, correct answer, and correctness status.

    Follows Single Responsibility principle by handling
    only question review data and related operations.
    """

    # Core review data
    question_number: int
    question_text: str
    user_answer: str
    correct_answer: str
    correct: bool

    # Optional fields
    explanation: Optional[str] = None
    topic: Optional[str] = None
    difficulty: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate review data after initialization."""
        self._validate()

    def _validate(self) -> None:
        """Validate review data."""
        if self.question_number < 1:
            raise ValueError("Question number must be positive")
        if not self.question_text:
            raise ValueError("Question text cannot be empty")
        if not self.user_answer:
            raise ValueError("User answer cannot be empty")
        if not self.correct_answer:
            raise ValueError("Correct answer cannot be empty")

    def __str__(self) -> str:
        """String representation of the review."""
        status = "Correct" if self.correct else "Incorrect"
        return f"Q{self.question_number}: {status}"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"QuestionReview(num={self.question_number}, "
            f"correct={self.correct}, user='{self.user_answer[:20]}...')"
        )

    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, QuestionReview):
            return False
        return (
            self.question_number == other.question_number
            and self.question_text == other.question_text
            and self.user_answer == other.user_answer
            and self.correct_answer == other.correct_answer
            and self.correct == other.correct
        )

    def __hash__(self) -> int:
        """Hash for use in sets/dicts."""
        return hash((self.question_number, self.question_text))

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert review to dictionary representation.

        Returns:
            Dictionary representation of the review
        """
        return {
            "question_number": self.question_number,
            "question_text": self.question_text,
            "user_answer": self.user_answer,
            "correct_answer": self.correct_answer,
            "correct": self.correct,
            "explanation": self.explanation,
            "topic": self.topic,
            "difficulty": self.difficulty,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuestionReview":
        """
        Create review from dictionary data.

        Args:
            data: Dictionary containing review data

        Returns:
            QuestionReview instance
        """
        return cls(
            question_number=data["question_number"],
            question_text=data["question_text"],
            user_answer=data["user_answer"],
            correct_answer=data["correct_answer"],
            correct=data["correct"],
            explanation=data.get("explanation"),
            topic=data.get("topic"),
            difficulty=data.get("difficulty"),
        )


class QuestionReviewList:
    """
    Manages a collection of QuestionReview objects for a session.
    
    Provides utility methods for analyzing review data and
    determining display logic (e.g., perfect score detection).
    """

    def __init__(self, reviews: Optional[List[QuestionReview]] = None):
        """Initialize with optional list of reviews."""
        self._reviews: List[QuestionReview] = reviews or []

    def add(self, review: QuestionReview) -> None:
        """Add a review to the list."""
        self._reviews.append(review)

    def get_all(self) -> List[QuestionReview]:
        """Get all reviews."""
        return self._reviews.copy()

    def get_incorrect(self) -> List[QuestionReview]:
        """Get only incorrect answer reviews."""
        return [r for r in self._reviews if not r.correct]

    def get_correct(self) -> List[QuestionReview]:
        """Get only correct answer reviews."""
        return [r for r in self._reviews if r.correct]

    @property
    def total_count(self) -> int:
        """Get total number of reviews."""
        return len(self._reviews)

    @property
    def correct_count(self) -> int:
        """Get count of correct answers."""
        return sum(1 for r in self._reviews if r.correct)

    @property
    def incorrect_count(self) -> int:
        """Get count of incorrect answers."""
        return sum(1 for r in self._reviews if not r.correct)

    @property
    def accuracy(self) -> float:
        """Calculate accuracy percentage."""
        if self.total_count == 0:
            return 0.0
        return round((self.correct_count / self.total_count) * 100, 2)

    def is_perfect_score(self) -> bool:
        """
        Check if all answers are correct (100% accuracy).
        
        Returns:
            True if all answers are correct, False otherwise
        """
        return self.total_count > 0 and all(r.correct for r in self._reviews)

    def should_show_congratulations(self) -> bool:
        """
        Determine if congratulations message should be shown.
        
        Returns:
            True if perfect score achieved, False otherwise
        """
        return self.is_perfect_score()

    def should_show_review_breakdown(self) -> bool:
        """
        Determine if question-by-question breakdown should be shown.
        
        Returns:
            True if there are incorrect answers to review, False for perfect score
        """
        return not self.is_perfect_score() and self.total_count > 0

    def to_list(self) -> List[Dict[str, Any]]:
        """Convert all reviews to list of dictionaries."""
        return [r.to_dict() for r in self._reviews]

    @classmethod
    def from_list(cls, data: List[Dict[str, Any]]) -> "QuestionReviewList":
        """Create QuestionReviewList from list of dictionaries."""
        reviews = [QuestionReview.from_dict(d) for d in data]
        return cls(reviews)

    def __len__(self) -> int:
        """Return number of reviews."""
        return len(self._reviews)

    def __iter__(self):
        """Iterate over reviews."""
        return iter(self._reviews)

    def __getitem__(self, index: int) -> QuestionReview:
        """Get review by index."""
        return self._reviews[index]
