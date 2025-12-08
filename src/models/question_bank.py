"""
QuestionBank entity for Q&A Practice Application.

Implements the QuestionBank data model following SOLID principles
with proper encapsulation, filtering, and data management.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import random
from datetime import datetime

from src.models.question import Question
from src.services.interfaces import QuestionFilter
from src.utils.exceptions import ValidationError, QuestionError


@dataclass
class QuestionBank:
    """
    Manages the collection of all questions loaded from CSV file
    with filtering and search capabilities.

    Follows Single Responsibility principle by handling
    only question collection management and filtering.
    """

    # Core data
    questions: List[Question] = field(default_factory=list)

    # Indexes for efficient lookup
    _topic_index: Dict[str, List[Question]] = field(default_factory=dict)
    _difficulty_index: Dict[str, List[Question]] = field(default_factory=dict)
    _topic_difficulty_index: Dict[str, List[Question]] = field(default_factory=dict)
    _id_index: Dict[str, Question] = field(default_factory=dict)

    # Metadata
    loaded_at: Optional[str] = None
    file_path: Optional[str] = None
    total_count: int = 0

    def __post_init__(self) -> None:
        """Initialize question bank after data loading."""
        if self.loaded_at is None:
            self.loaded_at = datetime.now().isoformat()
        self._rebuild_indexes()

    def add_question(self, question: Question) -> None:
        """
        Add a question to the bank.

        Args:
            question: Question to add
        """
        if not isinstance(question, Question):
            raise ValidationError("Question must be a Question instance")

        # Check for duplicate ID
        if question.id in self._id_index:
            raise QuestionError(
                f"Question with ID '{question.id}' already exists", question.id
            )

        self.questions.append(question)
        self._add_to_indexes(question)
        self.total_count = len(self.questions)

    def _add_to_indexes(self, question: Question) -> None:
        """Add question to all indexes."""
        # Topic index
        if question.topic not in self._topic_index:
            self._topic_index[question.topic] = []
        self._topic_index[question.topic].append(question)

        # Difficulty index
        if question.difficulty not in self._difficulty_index:
            self._difficulty_index[question.difficulty] = []
        self._difficulty_index[question.difficulty].append(question)

        # Topic-difficulty index
        tag = question.tag
        if tag not in self._topic_difficulty_index:
            self._topic_difficulty_index[tag] = []
        self._topic_difficulty_index[tag].append(question)

        # ID index
        self._id_index[question.id] = question

    def _rebuild_indexes(self) -> None:
        """Rebuild all indexes from questions list."""
        self._topic_index.clear()
        self._difficulty_index.clear()
        self._topic_difficulty_index.clear()
        self._id_index.clear()

        for question in self.questions:
            self._add_to_indexes(question)

        self.total_count = len(self.questions)

    def get_question_by_id(self, question_id: str) -> Optional[Question]:
        """
        Get question by ID.

        Args:
            question_id: ID of the question

        Returns:
            Question if found, None otherwise
        """
        return self._id_index.get(question_id)

    def get_all_questions(self) -> List[Question]:
        """
        Get all questions in the bank.

        Returns:
            List of all questions
        """
        return self.questions.copy()

    def get_questions_slice(self, start: int, end: int) -> List[Question]:
        """
        Get a slice of questions using array slicing.
        
        Args:
            start: Start index ( slice)
            end: End index for slice
            
        Returns:
            List of questions in the specified range
        """
        return self.questions[start:end]

    def insert_questions_at(self, index: int, questions: List[Question]) -> None:
        """
        Insert multiple questions at a specific index using array operations.
        
        Args:
            index: Position to insert at
            questions: List of questions to insert
        """
        for i, question in enumerate(questions):
            self.questions.insert(index + i, question)
        self._rebuild_indexes()

    def remove_questions_range(self, start: int, end: int) -> List[Question]:
        """
        Remove questions in a range and returnreturn the removed questions.
        
        Args:
            start: Start index
            end: End index
            
        Returns:
            List of removed questions
        """
        removed = self.questions[start:end]
        del self.questions[start:end]
        self._rebuild_indexes()
        return removed

    def extend_questions(self, questions: List[Question]) -> None:
        """
        Extend the questions array with another list using array operations.
        
        Args:
            questions: List of questions to extend with
        """
        self.questions.extend(questions)
        self._rebuild_indexes()

    def clear_questions(self) -> None:
        """
        Clear all questions using array operations.
        """
        self.questions.clear()
        self._rebuild_indexes()

    def filter_questions(self, criteria: QuestionFilter) -> List[Question]:
        """
        Filter questions based on criteria.

        Args:
            criteria: Filter criteria

        Returns:
            Filtered list of questions
        """
        if not criteria.topic and not criteria.difficulty:
            return self.get_all_questions()

        # Use indexes for efficient filtering
        if criteria.topic and criteria.difficulty:
            tag = f"{criteria.topic}-{criteria.difficulty}"
            questions = self._topic_difficulty_index.get(tag, [])
        elif criteria.topic:
            questions = self._topic_index.get(criteria.topic, [])
        elif criteria.difficulty:
            questions = self._difficulty_index.get(criteria.difficulty, [])
        else:
            questions = self.questions

        # Apply exclude filter if specified
        if criteria.exclude_ids:
            exclude_set = set(criteria.exclude_ids)
            questions = [q for q in questions if q.id not in exclude_set]

        return questions.copy()

    def get_random_question(self, criteria: QuestionFilter) -> Optional[Question]:
        """
        Get random question matching criteria.

        Args:
            criteria: Filter criteria

        Returns:
            Random question if found, None otherwise
        """
        filtered_questions = self.filter_questions(criteria)

        if not filtered_questions:
            return None

        # Use Fisher-Yates shuffle for true randomness
        return random.choice(filtered_questions)

    def get_random_questions(
        self, criteria: QuestionFilter, count: int
    ) -> List[Question]:
        """
        Get multiple random questions matching criteria.

        Args:
            criteria: Filter criteria
            count: Number of questions to return

        Returns:
            List of random questions
        """
        filtered_questions = self.filter_questions(criteria)

        if not filtered_questions:
            return []

        # Limit count to available questions
        actual_count = min(count, len(filtered_questions))

        # Use random.sample for unique random selection
        return random.sample(filtered_questions, actual_count)

    def get_available_topics(self) -> List[str]:
        """
        Get list of available topics.

        Returns:
            List of topic names
        """
        return sorted(self._topic_index.keys())

    def get_available_difficulties(self) -> List[str]:
        """
        Get list of available difficulty levels.

        Returns:
            List of difficulty names in logical order (Easy, Medium, Hard)
        """
        difficulty_order = ["Easy", "Medium", "Hard"]
        available = list(self._difficulty_index.keys())
        
        # Return difficulties in the predefined order if they exist
        ordered_difficulties = []
        for diff in difficulty_order:
            if diff in available:
                ordered_difficulties.append(diff)
        
        # Add any other difficulties not in the predefined order
        for diff in available:
            if diff not in ordered_difficulties:
                ordered_difficulties.append(diff)
        
        return ordered_difficulties

    def get_topic_difficulty_combinations(self) -> List[str]:
        """
        Get all topic-difficulty combinations.

        Returns:
            List of topic-difficulty tags
        """
        return sorted(self._topic_difficulty_index.keys())

    def count_questions(self, criteria: QuestionFilter) -> int:
        """
        Count questions matching criteria.

        Args:
            criteria: Filter criteria

        Returns:
            Number of matching questions
        """
        return len(self.filter_questions(criteria))

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get question bank statistics.

        Returns:
            Dictionary containing statistics
        """
        topic_stats = {}
        for topic, questions in self._topic_index.items():
            topic_stats[topic] = {"total": len(questions), "by_difficulty": {}}

            for difficulty in ["Easy", "Medium", "Hard"]:
                count = len([q for q in questions if q.difficulty == difficulty])
                if count > 0:
                    topic_stats[topic]["by_difficulty"][difficulty] = count

        difficulty_stats = {}
        for difficulty, questions in self._difficulty_index.items():
            difficulty_stats[difficulty] = len(questions)

        return {
            "total_questions": self.total_count,
            "topics": list(self._topic_index.keys()),
            "difficulties": list(self._difficulty_index.keys()),
            "topic_difficulty_combinations": list(self._topic_difficulty_index.keys()),
            "topic_breakdown": topic_stats,
            "difficulty_breakdown": difficulty_stats,
            "loaded_at": self.loaded_at,
            "file_path": self.file_path,
        }

    def reset_session_state(self) -> None:
        """Reset session state for all questions."""
        for question in self.questions:
            question.reset_session_state()

    def get_questions_for_session(
        self, topic: str, difficulty: str, count: int
    ) -> List[Question]:
        """
        Get questions for a new session.

        Args:
            topic: Session topic
            difficulty: Session difficulty
            count: Number of questions needed

        Returns:
            List of questions for the session

        Raises:
            QuestionError: If not enough questions available
        """
        criteria = QuestionFilter(topic=topic, difficulty=difficulty)
        available_questions = self.filter_questions(criteria)

        if len(available_questions) < count:
            raise QuestionError(
                f"Not enough questions available. Need {count}, have {len(available_questions)}",
                f"{topic}-{difficulty}",
            )

        # Get random questions and reset their session state
        session_questions = self.get_random_questions(criteria, count)
        for question in session_questions:
            question.reset_session_state()

        return session_questions

    def validate_question_bank(self) -> List[str]:
        """
        Validate the entire question bank.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        seen_ids = set()

        for i, question in enumerate(self.questions):
            try:
                question.validate()

                # Check for duplicate IDs
                if question.id in seen_ids:
                    errors.append(f"Duplicate question ID found: {question.id}")
                else:
                    seen_ids.add(question.id)

            except ValidationError as e:
                errors.append(f"Question {i+1} validation error: {str(e)}")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert question bank to dictionary representation.

        Returns:
            Dictionary representation of question bank
        """
        return {
            "questions": [q.to_dict() for q in self.questions],
            "statistics": self.get_statistics(),
            "loaded_at": self.loaded_at,
            "file_path": self.file_path,
            "total_count": self.total_count,
        }

    @classmethod
    def from_questions(
        cls, questions: List[Question], file_path: Optional[str] = None
    ) -> "QuestionBank":
        """
        Create question bank from list of questions.

        Args:
            questions: List of questions
            file_path: Optional source file path

        Returns:
            QuestionBank instance
        """
        return cls(
            questions=questions.copy(),
            file_path=file_path,
            loaded_at=datetime.now().isoformat(),
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuestionBank":
        """
        Create question bank from dictionary data.

        Args:
            data: Dictionary containing question bank data

        Returns:
            QuestionBank instance
        """
        questions = [Question.from_dict(q) for q in data["questions"]]
        return cls(
            questions=questions,
            file_path=data.get("file_path"),
            loaded_at=data.get("loaded_at"),
        )

    def __len__(self) -> int:
        """Return number of questions in bank."""
        return len(self.questions)

    def __iter__(self):
        """Iterate over questions."""
        return iter(self.questions)

    def __str__(self) -> str:
        """String representation of question bank."""
        return f"QuestionBank({self.total_count} questions, {len(self._topic_index)} topics)"

    def __repr__(self) -> str:
        """Detailed string representation of question bank."""
        topics = list(self._topic_index.keys())
        return (
            f"QuestionBank(total={self.total_count}, topics={topics}, "
            f"loaded_at={self.loaded_at})"
        )
