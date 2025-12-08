"""
UserSession entity for Q&A Practice Application.

Implements the UserSession data model following SOLID principles
with proper encapsulation, validation, and state management.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from src.utils.exceptions import ValidationError, SessionError


@dataclass
class UserSession:
    """
    Manages the current practice session state and progress.

    Follows Single Responsibility principle by handling
    only session data and state management logic.
    """

    # Core session data
    session_id: str
    topic: str
    difficulty: str
    total_questions: int
    current_question_index: int = 0

    # Session tracking
    questions_asked: List[str] = field(default_factory=list)
    user_answers: Dict[str, str] = field(default_factory=dict)
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    is_active: bool = True

    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate session data after initialization."""
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.start_time is None:
            self.start_time = datetime.now().isoformat()
        self.validate()

    def __str__(self) -> str:
        """String representation of the session."""
        return f"UserSession(id={self.session_id}, topic={self.topic}, difficulty={self.difficulty})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"UserSession(id='{self.session_id}', topic='{self.topic}', difficulty='{self.difficulty}', questions={self.total_questions}, active={self.is_active})"

    def __eq__(self, other) -> bool:
        """Equality comparison based on session ID."""
        if not isinstance(other, UserSession):
            return False
        return self.session_id == other.session_id

    def __hash__(self) -> int:
        """Hash based on session ID for use in sets/dicts."""
        return hash(self.session_id)

    def validate(self) -> None:
        """
        Validate session data following business rules.

        Raises:
            ValidationError: If validation fails
        """
        self._validate_session_id()
        self._validate_topic()
        self._validate_difficulty()
        self._validate_total_questions()
        self._validate_current_index()
        self._validate_state_consistency()

    def _validate_session_id(self) -> None:
        """Validate session ID."""
        if not self.session_id or not self.session_id.strip():
            raise ValidationError(
                "Session ID cannot be empty", "session_id", self.session_id
            )

        # Check if it's a valid UUID or custom format
        try:
            uuid.UUID(self.session_id)
        except ValueError:
            # If not UUID, check for alphanumeric format
            if not self.session_id.replace("-", "").replace("_", "").isalnum():
                raise ValidationError(
                    "Session ID must be a valid UUID or alphanumeric string",
                    "session_id",
                    self.session_id,
                )

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

    def _validate_total_questions(self) -> None:
        """Validate total questions field."""
        if not isinstance(self.total_questions, int) or self.total_questions <= 0:
            raise ValidationError(
                "Total questions must be a positive integer",
                "total_questions",
                self.total_questions,
            )

        if self.total_questions > 50:
            raise ValidationError(
                "Total questions cannot exceed 50",
                "total_questions",
                self.total_questions,
            )

    def _validate_current_index(self) -> None:
        """Validate current question index."""
        if (
            not isinstance(self.current_question_index, int)
            or self.current_question_index < 0
        ):
            raise ValidationError(
                "Current question index must be a non-negative integer",
                "current_question_index",
                self.current_question_index,
            )

        if self.current_question_index > self.total_questions:
            raise ValidationError(
                "Current question index cannot exceed total questions",
                "current_question_index",
                self.current_question_index,
            )

    def _validate_state_consistency(self) -> None:
        """Validate consistency of session state."""
        if len(self.questions_asked) != len(self.user_answers):
            raise ValidationError(
                "Questions asked and user answers must have the same length",
                "state_consistency",
                f"questions_asked={len(self.questions_asked)}, user_answers={len(self.user_answers)}",
            )

        if self.current_question_index != len(self.questions_asked):
            raise ValidationError(
                "Current question index must match number of questions asked",
                "state_consistency",
                f"current_index={self.current_question_index}, asked={len(self.questions_asked)}",
            )

    def add_question(self, question_id: str) -> None:
        """
        Add a question to the session.

        Args:
            question_id: ID of the question to add

        Raises:
            SessionError: If session is not active or question limit reached
        """
        if not self.is_active:
            raise SessionError(
                "Cannot add question to inactive session", self.session_id
            )

        if len(self.questions_asked) >= self.total_questions:
            raise SessionError(
                "Question limit reached for this session", self.session_id
            )

        if question_id in self.questions_asked:
            raise SessionError(
                f"Question {question_id} already asked in this session", self.session_id
            )

        self.questions_asked.append(question_id)
        self.current_question_index = len(self.questions_asked)
        self._update_timestamp()

    def submit_answer(self, question_id: str, answer: str) -> None:
        """
        Submit an answer for a question.

        Args:
            question_id: ID of the question being answered
            answer: User's answer

        Raises:
            SessionError: If question was not asked or already answered
        """
        if not self.is_active:
            raise SessionError(
                "Cannot submit answer to inactive session", self.session_id
            )

        if question_id not in self.questions_asked:
            raise SessionError(
                f"Question {question_id} was not asked in this session", self.session_id
            )

        if question_id in self.user_answers:
            raise SessionError(
                f"Question {question_id} already answered", self.session_id
            )

        self.user_answers[question_id] = answer.strip()
        self._update_timestamp()

    def is_complete(self) -> bool:
        """
        Check if the session is complete.

        Returns:
            True if all questions have been answered
        """
        return len(self.questions_asked) >= self.total_questions

    def get_progress(self) -> Dict[str, Any]:
        """
        Get session progress information.

        Returns:
            Dictionary containing progress details
        """
        return {
            "total_questions": self.total_questions,
            "questions_asked": len(self.questions_asked),
            "questions_answered": len(self.user_answers),
            "current_index": self.current_question_index,
            "progress_percentage": (len(self.questions_asked) / self.total_questions)
            * 100,
            "is_complete": self.is_complete(),
            "remaining_questions": self.total_questions - len(self.questions_asked),
        }

    def get_session_duration(self) -> int:
        """
        Get session duration in seconds.

        Returns:
            Duration in seconds
        """
        if not self.start_time:
            return 0

        start_dt = datetime.fromisoformat(self.start_time.replace("Z", "+00:00"))

        if self.end_time:
            end_dt = datetime.fromisoformat(self.end_time.replace("Z", "+00:00"))
        else:
            end_dt = datetime.now()

        return int((end_dt - start_dt).total_seconds())

    def complete_session(self) -> None:
        """Mark the session as complete."""
        if not self.is_active:
            raise SessionError("Session is already inactive", self.session_id)

        self.is_active = False
        self.end_time = datetime.now().isoformat()
        self._update_timestamp()

    def pause_session(self) -> None:
        """Pause the session (keep active but stop progress)."""
        if not self.is_active:
            raise SessionError("Cannot pause inactive session", self.session_id)

        self._update_timestamp()

    def resume_session(self) -> None:
        """Resume a paused session."""
        if not self.is_active:
            raise SessionError("Cannot resume inactive session", self.session_id)

        self._update_timestamp()

    def _update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert session to dictionary representation.

        Returns:
            Dictionary representation of session
        """
        return {
            "session_id": self.session_id,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "total_questions": self.total_questions,
            "current_question_index": self.current_question_index,
            "questions_asked": self.questions_asked.copy(),
            "user_answers": self.user_answers.copy(),
            "start_time": self.start_time,
            "end_time": self.end_time,
            "is_active": self.is_active,
            "progress": self.get_progress(),
            "duration_seconds": self.get_session_duration(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def create_new(
        cls, topic: str, difficulty: str, total_questions: int = 10
    ) -> "UserSession":
        """
        Create a new session with generated ID.

        Args:
            topic: Session topic
            difficulty: Session difficulty
            total_questions: Number of questions in session

        Returns:
            New UserSession instance
        """
        session_id = str(uuid.uuid4())
        return cls(
            session_id=session_id,
            topic=topic,
            difficulty=difficulty,
            total_questions=total_questions,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserSession":
        """
        Create session from dictionary data.

        Args:
            data: Dictionary containing session data

        Returns:
            UserSession instance
        """
        return cls(
            session_id=data["session_id"],
            topic=data["topic"],
            difficulty=data["difficulty"],
            total_questions=data["total_questions"],
            current_question_index=data.get("current_question_index", 0),
            questions_asked=data.get("questions_asked", []),
            user_answers=data.get("user_answers", {}),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def __str__(self) -> str:
        """String representation of session."""
        return f"UserSession(id={self.session_id[:8]}..., topic={self.topic}, progress={len(self.questions_asked)}/{self.total_questions})"

    def __repr__(self) -> str:
        """Detailed string representation of session."""
        return (
            f"UserSession(id='{self.session_id}', topic='{self.topic}', "
            f"difficulty='{self.difficulty}', progress={len(self.questions_asked)}/{self.total_questions}, "
            f"active={self.is_active})"
        )
