"""
Question entity for Q&A Practice Application.

Implements the Question data model following SOLID principles
with proper encapsulation, validation, and state management.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import re

from src.utils.exceptions import ValidationError


@dataclass
class Question:
    """
    Represents a single question with all associated data.

    Follows Single Responsibility principle by handling
    only question data and validation logic.
    """

    # Core question data
    id: str
    topic: str
    question_text: str
    option1: str
    option2: str
    option3: str
    option4: str
    correct_answer: str
    difficulty: str
    tag: str

    # Session tracking fields
    asked_in_session: bool = False
    got_right: bool = False

    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate question data after initialization."""
        if self.created_at is None:
            from datetime import datetime

            self.created_at = datetime.now().isoformat()
        self.validate()

    def validate(self) -> None:
        """
        Validate question data following business rules.

        Raises:
            ValidationError: If validation fails
        """
        self._validate_topic()
        self._validate_difficulty()
        self._validate_question_text()
        self._validate_options()
        self._validate_correct_answer()
        self._validate_tag()
        self._validate_id()

    def _validate_topic(self) -> None:
        """Validate topic field."""
        if not self.topic or not self.topic.strip():
            raise ValidationError("Topic cannot be empty", "topic", self.topic)

        valid_topics = ["Physics", "Chemistry", "Math"]
        if self.topic not in valid_topics:
            raise ValidationError(
                f"Invalid topic '{self.topic}'. Must be one of: {valid_topics}",
                "topic",
                self.topic,
            )

    def _validate_difficulty(self) -> None:
        """Validate difficulty field."""
        if not self.difficulty or not self.difficulty.strip():
            raise ValidationError(
                "Difficulty cannot be empty", "difficulty", self.difficulty
            )

        valid_difficulties = ["Easy", "Medium", "Hard"]
        if self.difficulty not in valid_difficulties:
            raise ValidationError(
                f"Invalid difficulty '{self.difficulty}'. Must be one of: {valid_difficulties}",
                "difficulty",
                self.difficulty,
            )

    def _validate_question_text(self) -> None:
        """Validate question text field."""
        if not self.question_text or not self.question_text.strip():
            raise ValidationError(
                "Question text cannot be empty", "question_text", self.question_text
            )

        if len(self.question_text.strip()) < 10:
            raise ValidationError(
                "Question text must be at least 10 characters long",
                "question_text",
                self.question_text,
            )

        # Check for basic question structure (ends with ?)
        if not self.question_text.strip().endswith("?"):
            raise ValidationError(
                "Question text should end with a question mark",
                "question_text",
                self.question_text,
            )

    def _validate_options(self) -> None:
        """Validate option fields."""
        options = [self.option1, self.option2, self.option3, self.option4]

        for i, option in enumerate(options, 1):
            if not option or not option.strip():
                raise ValidationError(
                    f"Option {i} cannot be empty", f"option{i}", option
                )

            if len(option.strip()) < 1:
                raise ValidationError(
                    f"Option {i} must contain at least 1 character",
                    f"option{i}",
                    option,
                )

        # Check for duplicate options
        stripped_options = [opt.strip() for opt in options]
        if len(set(stripped_options)) != len(stripped_options):
            raise ValidationError("All options must be unique", "options", options)

    def _validate_correct_answer(self) -> None:
        """Validate correct answer field."""
        if not self.correct_answer or not self.correct_answer.strip():
            raise ValidationError(
                "Correct answer cannot be empty", "correct_answer", self.correct_answer
            )

        options = [
            self.option1.strip(),
            self.option2.strip(),
            self.option3.strip(),
            self.option4.strip(),
        ]
        correct_stripped = self.correct_answer.strip()

        if correct_stripped not in options:
            raise ValidationError(
                f"Correct answer '{self.correct_answer}' must match one of the options",
                "correct_answer",
                self.correct_answer,
            )

    def _validate_tag(self) -> None:
        """Validate tag field."""
        if not self.tag or not self.tag.strip():
            raise ValidationError("Tag cannot be empty", "tag", self.tag)

        expected_tag = f"{self.topic}-{self.difficulty}"
        if self.tag != expected_tag:
            raise ValidationError(
                f"Tag '{self.tag}' should match '{expected_tag}'", "tag", self.tag
            )

    def _validate_id(self) -> None:
        """Validate ID field."""
        if not self.id or not self.id.strip():
            raise ValidationError("ID cannot be empty", "id", self.id)

        # Check ID format (alphanumeric with underscores)
        if not re.match(r"^[a-zA-Z0-9_]+$", self.id):
            raise ValidationError(
                "ID must contain only alphanumeric characters and underscores",
                "id",
                self.id,
            )

    def get_options(self) -> List[str]:
        """
        Get all options as a list.

        Returns:
            List of option strings
        """
        return [self.option1, self.option2, self.option3, self.option4]

    def is_correct_answer(self, answer: str) -> bool:
        """
        Check if the provided answer is correct.

        Args:
            answer: Answer to check

        Returns:
            True if answer is correct, False otherwise
        """
        return answer.strip() == self.correct_answer.strip()

    def mark_as_asked(self) -> None:
        """Mark question as asked in current session."""
        self.asked_in_session = True
        self._update_timestamp()

    def mark_as_answered(self, correct: bool) -> None:
        """
        Mark question as answered with result.

        Args:
            correct: Whether the answer was correct
        """
        if not self.asked_in_session:
            raise ValidationError("Cannot mark as answered before question is asked")

        self.got_right = correct
        self._update_timestamp()

    def reset_session_state(self) -> None:
        """Reset session tracking state."""
        self.asked_in_session = False
        self.got_right = False
        self._update_timestamp()

    def _update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        from datetime import datetime

        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert question to dictionary representation.

        Returns:
            Dictionary representation of question
        """
        return {
            "id": self.id,
            "topic": self.topic,
            "question_text": self.question_text,
            "options": self.get_options(),
            "correct_answer": self.correct_answer,
            "difficulty": self.difficulty,
            "tag": self.tag,
            "asked_in_session": self.asked_in_session,
            "got_right": self.got_right,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Question":
        """
        Create question from dictionary data.

        Args:
            data: Dictionary containing question data

        Returns:
            Question instance
        """
        # Handle options array or individual option fields
        if "options" in data and len(data["options"]) == 4:
            options = data["options"]
            return cls(
                id=data["id"],
                topic=data["topic"],
                question_text=data["question_text"],
                option1=options[0],
                option2=options[1],
                option3=options[2],
                option4=options[3],
                correct_answer=data["correct_answer"],
                difficulty=data["difficulty"],
                tag=data["tag"],
                asked_in_session=data.get("asked_in_session", False),
                got_right=data.get("got_right", False),
                created_at=data.get("created_at"),
                updated_at=data.get("updated_at"),
            )
        else:
            return cls(
                id=data["id"],
                topic=data["topic"],
                question_text=data["question_text"],
                option1=data["option1"],
                option2=data["option2"],
                option3=data["option3"],
                option4=data["option4"],
                correct_answer=data["correct_answer"],
                difficulty=data["difficulty"],
                tag=data["tag"],
                asked_in_session=data.get("asked_in_session", False),
                got_right=data.get("got_right", False),
                created_at=data.get("created_at"),
                updated_at=data.get("updated_at"),
            )

    def __str__(self) -> str:
        """String representation of question."""
        return (
            f"Question(id={self.id}, topic={self.topic}, difficulty={self.difficulty})"
        )

    def __repr__(self) -> str:
        """Detailed string representation of question."""
        return (
            f"Question(id='{self.id}', topic='{self.topic}', "
            f"difficulty='{self.difficulty}', asked={self.asked_in_session}, "
            f"correct={self.got_right})"
        )
