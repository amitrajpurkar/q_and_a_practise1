"""
Score entity for Q&A Practice Application.

Implements the Score data model following SOLID principles
with proper encapsulation, validation, and performance tracking.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime

from src.utils.exceptions import ValidationError, ScoreError


@dataclass
class AnswerResult:
    """
    Represents the result of an answer submission.
    
    Contains information about whether the answer was correct,
    the correct answer, and optional explanation.
    """
    
    question_id: str
    correct: bool
    answer_text: str
    correct_answer: str
    explanation: Optional[str] = None
    time_taken_seconds: int = 0


@dataclass
class Score:
    """
    Tracks user performance including correct answers, total questions,
    accuracy percentage, timing information, and streak data.

    Follows Single Responsibility principle by handling
    only score data and calculation logic.
    """

    # Core score data
    session_id: str
    total_questions: int
    correct_answers: int
    incorrect_answers: int

    # Performance metrics
    accuracy_percentage: float = 0.0
    time_taken_seconds: int = 0

    # Topic performance breakdown
    topic_performance: Dict[str, Dict[str, Dict[str, int]]] = field(default_factory=dict)
    
    # Streak tracking
    streak_data: Dict[str, int] = field(default_factory=dict)

    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate and calculate score data after initialization."""
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        self._calculate_accuracy()
        self.validate()

    def validate(self) -> None:
        """
        Validate score data following business rules.

        Raises:
            ValidationError: If validation fails
        """
        self._validate_session_id()
        self._validate_question_counts()
        self._validate_accuracy()
        self._validate_time_taken()
        self._validate_topic_performance()

    def _validate_session_id(self) -> None:
        """Validate session ID."""
        if not self.session_id or not self.session_id.strip():
            raise ValidationError(
                "Session ID cannot be empty", "session_id", self.session_id
            )

    def _validate_question_counts(self) -> None:
        """Validate question count fields."""
        if not isinstance(self.total_questions, int) or self.total_questions < 0:
            raise ValidationError(
                "Total questions must be a non-negative integer",
                "total_questions",
                self.total_questions,
            )

        if not isinstance(self.correct_answers, int) or self.correct_answers < 0:
            raise ValidationError(
                "Correct answers must be a non-negative integer",
                "correct_answers",
                self.correct_answers,
            )

        if not isinstance(self.incorrect_answers, int) or self.incorrect_answers < 0:
            raise ValidationError(
                "Incorrect answers must be a non-negative integer",
                "incorrect_answers",
                self.incorrect_answers,
            )

        # Check that counts add up correctly
        answered_questions = self.correct_answers + self.incorrect_answers
        if answered_questions > self.total_questions:
            raise ValidationError(
                f"Answered questions ({answered_questions}) cannot exceed total questions ({self.total_questions})",
                "question_counts",
                {
                    "correct": self.correct_answers,
                    "incorrect": self.incorrect_answers,
                    "total": self.total_questions,
                },
            )

    def _validate_accuracy(self) -> None:
        """Validate accuracy percentage."""
        if not isinstance(self.accuracy_percentage, float) or not (
            0 <= self.accuracy_percentage <= 100
        ):
            raise ValidationError(
                "Accuracy percentage must be between 0 and 100",
                "accuracy_percentage",
                self.accuracy_percentage,
            )

    def _validate_time_taken(self) -> None:
        """Validate time taken."""
        if not isinstance(self.time_taken_seconds, int) or self.time_taken_seconds < 0:
            raise ValidationError(
                "Time taken must be a non-negative integer",
                "time_taken_seconds",
                self.time_taken_seconds,
            )

    def _validate_topic_performance(self) -> None:
        """Validate topic performance breakdown."""
        for topic, difficulties in self.topic_performance.items():
            if not isinstance(difficulties, dict):
                raise ValidationError(
                    f"Topic performance for '{topic}' must be a dictionary of difficulties",
                    "topic_performance",
                    self.topic_performance,
                )

            for difficulty, performance in difficulties.items():
                if not isinstance(performance, dict):
                    raise ValidationError(
                        f"Performance for '{topic}-{difficulty}' must be a dictionary",
                        "topic_performance",
                        self.topic_performance,
                    )

                required_keys = ["correct", "incorrect", "total"]
                for key in required_keys:
                    if key not in performance:
                        raise ValidationError(
                            f"Performance for '{topic}-{difficulty}' must contain '{key}' key",
                            "topic_performance",
                            performance,
                        )

                if not isinstance(performance["correct"], int) or not isinstance(
                    performance["incorrect"], int
                ) or not isinstance(performance["total"], int):
                    raise ValidationError(
                        f"Performance values for '{topic}-{difficulty}' must be integers",
                        "topic_performance",
                        performance,
                    )

                if performance["correct"] < 0 or performance["incorrect"] < 0 or performance["total"] < 0:
                    raise ValidationError(
                        f"Performance values for '{topic}-{difficulty}' must be non-negative",
                        "topic_performance",
                        performance,
                    )

                if performance["correct"] + performance["incorrect"] != performance["total"]:
                    raise ValidationError(
                        f"Performance for '{topic}-{difficulty}' must have correct + incorrect = total",
                        "topic_performance",
                        performance,
                    )

    def _calculate_accuracy(self) -> None:
        """Calculate accuracy percentage."""
        answered_questions = self.correct_answers + self.incorrect_answers
        if answered_questions > 0:
            self.accuracy_percentage = round(
                (self.correct_answers / answered_questions) * 100, 2
            )
        else:
            self.accuracy_percentage = 0.0

    def add_correct_answer(self, topic: str) -> None:
        """
        Add a correct answer to the score.

        Args:
            topic: Topic of the correctly answered question
        """
        self.correct_answers += 1
        self._update_topic_performance(topic, correct=True)
        self._calculate_accuracy()
        self._update_timestamp()

    def add_incorrect_answer(self, topic: str) -> None:
        """
        Add an incorrect answer to the score.

        Args:
            topic: Topic of the incorrectly answered question
        """
        self.incorrect_answers += 1
        self._update_topic_performance(topic, correct=False)
        self._calculate_accuracy()
        self._update_timestamp()

    def _update_topic_performance(self, topic: str, correct: bool) -> None:
        """
        Update topic performance breakdown.

        Args:
            topic: Topic being updated
            correct: Whether the answer was correct
        """
        if topic not in self.topic_performance:
            self.topic_performance[topic] = {"correct": 0, "total": 0}

        self.topic_performance[topic]["total"] += 1
        if correct:
            self.topic_performance[topic]["correct"] += 1

    def set_time_taken(self, seconds: int) -> None:
        """
        Set the time taken for the session.

        Args:
            seconds: Time in seconds
        """
        if seconds < 0:
            raise ScoreError("Time taken cannot be negative", self.session_id)

        self.time_taken_seconds = seconds
        self._update_timestamp()

    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive performance summary.

        Returns:
            Dictionary containing performance details
        """
        answered_questions = self.correct_answers + self.incorrect_answers
        unanswered_questions = self.total_questions - answered_questions

        return {
            "session_id": self.session_id,
            "total_questions": self.total_questions,
            "answered_questions": answered_questions,
            "unanswered_questions": unanswered_questions,
            "correct_answers": self.correct_answers,
            "incorrect_answers": self.incorrect_answers,
            "accuracy_percentage": self.accuracy_percentage,
            "time_taken_seconds": self.time_taken_seconds,
            "time_taken_formatted": self._format_time(self.time_taken_seconds),
            "topic_performance": self.topic_performance.copy(),
            "performance_grade": self._get_performance_grade(),
            "questions_per_minute": self._get_questions_per_minute(),
        }

    def get_topic_accuracy(self, topic: str) -> float:
        """
        Get accuracy for a specific topic.

        Args:
            topic: Topic to get accuracy for

        Returns:
            Accuracy percentage for the topic
        """
        if topic not in self.topic_performance:
            return 0.0

        performance = self.topic_performance[topic]
        if performance["total"] == 0:
            return 0.0

        return round((performance["correct"] / performance["total"]) * 100, 2)

    def _format_time(self, seconds: int) -> str:
        """
        Format time in seconds to human-readable format.

        Args:
            seconds: Time in seconds

        Returns:
            Formatted time string
        """
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds}s"
        else:
            hours = seconds // 3600
            remaining_minutes = (seconds % 3600) // 60
            return f"{hours}h {remaining_minutes}m"

    def _get_performance_grade(self) -> str:
        """
        Get performance grade based on accuracy.

        Returns:
            Performance grade (A, B, C, D, F)
        """
        if self.accuracy_percentage >= 90:
            return "A"
        elif self.accuracy_percentage >= 80:
            return "B"
        elif self.accuracy_percentage >= 70:
            return "C"
        elif self.accuracy_percentage >= 60:
            return "D"
        else:
            return "F"

    def _get_questions_per_minute(self) -> float:
        """
        Calculate questions answered per minute.

        Returns:
            Questions per minute rate
        """
        if self.time_taken_seconds == 0:
            return 0.0

        minutes = self.time_taken_seconds / 60
        answered_questions = self.correct_answers + self.incorrect_answers

        return round(answered_questions / minutes, 2)

    def _update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert score to dictionary representation.

        Returns:
            Dictionary representation of score
        """
        return {
            "session_id": self.session_id,
            "total_questions": self.total_questions,
            "correct_answers": self.correct_answers,
            "incorrect_answers": self.incorrect_answers,
            "accuracy_percentage": self.accuracy_percentage,
            "time_taken_seconds": self.time_taken_seconds,
            "topic_performance": self.topic_performance.copy(),
            "performance_summary": self.get_performance_summary(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_session_results(
        cls,
        session_id: str,
        total_questions: int,
        correct_answers: int,
        incorrect_answers: int,
        time_taken_seconds: int = 0,
        topic_performance: Optional[Dict[str, Dict[str, int]]] = None,
    ) -> "Score":
        """
        Create score from session results.

        Args:
            session_id: Session identifier
            total_questions: Total questions in session
            correct_answers: Number of correct answers
            incorrect_answers: Number of incorrect answers
            time_taken_seconds: Time taken in seconds
            topic_performance: Optional topic performance breakdown

        Returns:
            Score instance
        """
        return cls(
            session_id=session_id,
            total_questions=total_questions,
            correct_answers=correct_answers,
            incorrect_answers=incorrect_answers,
            time_taken_seconds=time_taken_seconds,
            topic_performance=topic_performance or {},
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Score":
        """
        Create score from dictionary data.

        Args:
            data: Dictionary containing score data

        Returns:
            Score instance
        """
        return cls(
            session_id=data["session_id"],
            total_questions=data["total_questions"],
            correct_answers=data["correct_answers"],
            incorrect_answers=data["incorrect_answers"],
            accuracy_percentage=data.get("accuracy_percentage", 0.0),
            time_taken_seconds=data.get("time_taken_seconds", 0),
            topic_performance=data.get("topic_performance", {}),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def __str__(self) -> str:
        """String representation of score."""
        return f"Score(session={self.session_id[:8]}..., accuracy={self.accuracy_percentage}%, {self.correct_answers}/{self.total_questions})"

    def __repr__(self) -> str:
        """Detailed string representation of score."""
        return (
            f"Score(session_id='{self.session_id}', total={self.total_questions}, "
            f"correct={self.correct_answers}, accuracy={self.accuracy_percentage}%)"
        )
