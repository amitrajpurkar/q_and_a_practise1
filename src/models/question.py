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

    def __str__(self) -> str:
        """String representation of the question."""
        return f"Question(id={self.id}, topic={self.topic}, difficulty={self.difficulty})"

    def __repr__(self) -> str:
        """ Detailed string representation."""
        return f"Question(id='{self.id}', topic='{self.topic}', difficulty='{self.difficulty}', text='{self.question_text[:50]}...')"

    def __eq__(self, other) -> bool:
        """Equality comparison based on question ID."""
        if not isinstance(other, Question):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on question ID for use in sets/dicts."""
        return hash(self.id)

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

    # Polymorphism for different question types
    def get_question_type(self) -> str:
        """
        Get the type of this question (polymorphic method).
        
        Returns:
            String representing question type
        """
        return "multiple_choice"

    def validate_answer(self, user_answer: str) -> bool:
        """
        Validate user answer (polymorphic method).
        
        Args:
            user_answer: User's submitted answer
            
        Returns:
            True if answer is correct, False otherwise
        """
        return self.is_correct_answer(user_answer)

    def get_display_format(self) -> Dict[str, Any]:
        """
        Get display format for this question type (polymorphic method).
        
        Returns:
            Dictionary with display information
        """
        return {
            'type': 'multiple_choice',
            'question': self.question_text,
            'options': [
                {'label': 'A', 'text': self.option1},
                {'label': 'B', 'text': self.option2},
                {'label': 'C', 'text': self.option3},
                {'label': 'D', 'text': self.option4}
            ],
            'correct_answer': self.correct_answer
        }

    def calculate_difficulty_score(self) -> float:
        """
        Calculate difficulty score for this question type (polymorphic method).
        
        Returns:
            Float representing difficulty score
        """
        difficulty_multipliers = {'Easy': 1.0, 'Medium': 1.5, 'Hard': 2.0}
        base_score = difficulty_multipliers.get(self.difficulty, 1.0)
        
        # Add complexity based on question text length
        length_factor = min(len(self.question_text) / 100.0, 2.0)
        
        return base_score * length_factor

    def get_hint(self) -> str:
        """
        Get hint for this question type (polymorphic method).
        
        Returns:
            Hint string for the question
        """
        return f"This is a {self.difficulty.lower()} {self.topic} question. Consider all options carefully."

    def get_time_limit(self) -> int:
        """
        Get time limit for this question type (polymorphic method).
        
        Returns:
            Time limit in seconds
        """
        base_times = {'Easy': 30, 'Medium': 45, 'Hard': 60}
        return base_times.get(self.difficulty, 45)


class TrueFalseQuestion(Question):
    """
    True/False question type demonstrating polymorphism.
    """
    
    def __init__(self, id: str, topic: str, question_text: str, 
                 correct_answer: str, difficulty: str = "Easy", 
                 tag: Optional[str] = None, **kwargs):
        """
        Initialize True/False question.
        
        Args:
            id: Unique identifier
            topic: Question topic
            question_text: The question text
            correct_answer: Either "True" or "False"
            difficulty: Question difficulty
            tag: Optional tag
            **kwargs: Additional keyword arguments
        """
        # Set options to True/False
        super().__init__(
            id=id,
            topic=topic,
            question_text=question_text,
            option1="True",
            option2="False",
            option3=None,
            option4=None,
            correct_answer=correct_answer,
            difficulty=difficulty,
            tag=tag,
            **kwargs
        )
    
    def get_question_type(self) -> str:
        """Override: Return true_false type."""
        return "true_false"
    
    def get_display_format(self) -> Dict[str, Any]:
        """Override: Return true/false specific format."""
        return {
            'type': 'true_false',
            'question': self.question_text,
            'options': [
                {'label': 'T', 'text': 'True'},
                {'label': 'F', 'text': 'False'}
            ],
            'correct_answer': self.correct_answer
        }
    
    def calculate_difficulty_score(self) -> float:
        """Override: Simpler scoring for true/false."""
        difficulty_multipliers = {'Easy': 0.5, 'Medium': 0.8, 'Hard': 1.2}
        return difficulty_multipliers.get(self.difficulty, 0.8)
    
    def get_hint(self) -> str:
        """Override: True/false specific hint."""
        return f"This is a {self.difficulty.lower()} true/false question. Read the statement carefully."
    
    def get_time_limit(self) -> int:
        """Override: Shorter time for true/false."""
        base_times = {'Easy': 15, 'Medium': 20, 'Hard': 25}
        return base_times.get(self.difficulty, 20)


class FillInBlankQuestion(Question):
    """
    Fill in the blank question type demonstrating polymorphism.
    """
    
    def __init__(self, id: str, topic: str, question_text: str, 
                 correct_answer: str, difficulty: str = "Medium", 
                 tag: Optional[str] = None, **kwargs):
        """
        Initialize fill in the blank question.
        
        Args:
            id: Unique identifier
            topic: Question topic
            question_text: The question with blank indicated by ___
            correct_answer: The answer to fill the blank
            difficulty: Question difficulty
            tag: Optional tag
            **kwargs: Additional keyword arguments
        """
        super().__init__(
            id=id,
            topic=topic,
            question_text=question_text,
            option1=None,
            option2=None,
            option3=None,
            option4=None,
            correct_answer=correct_answer,
            difficulty=difficulty,
            tag=tag,
            **kwargs
        )
    
    def get_question_type(self) -> str:
        """Override: Return fill_in_blank type."""
        return "fill_in_blank"
    
    def get_display_format(self) -> Dict[str, Any]:
        """Override: Return fill in the blank specific format."""
        return {
            'type': 'fill_in_blank',
            'question': self.question_text,
            'blank_count': self.question_text.count('___'),
            'correct_answer': self.correct_answer
        }
    
    def validate_answer(self, user_answer: str) -> bool:
        """Override: Case-insensitive validation for fill in blank."""
        return user_answer.strip().lower() == self.correct_answer.strip().lower()
    
    def calculate_difficulty_score(self) -> float:
        """Override: Higher scoring for fill in blank."""
        difficulty_multipliers = {'Easy': 1.2, 'Medium': 1.8, 'Hard': 2.5}
        base_score = difficulty_multipliers.get(self.difficulty, 1.8)
        
        # Add complexity based on number of blanks
        blank_factor = 1.0 + (self.question_text.count('___') * 0.3)
        
        return base_score * blank_factor
    
    def get_hint(self) -> str:
        """Override: Fill in blank specific hint."""
        blank_count = self.question_text.count('___')
        hint = f"This is a {self.difficulty.lower()} fill-in-the-blank question."
        if blank_count > 1:
            hint += f" There are {blank_count} blanks to fill."
        return hint
    
    def get_time_limit(self) -> int:
        """Override: Longer time for fill in blank."""
        base_times = {'Easy': 30, 'Medium': 45, 'Hard': 60}
        extra_time = self.question_text.count('___') * 10
        return base_times.get(self.difficulty, 45) + extra_time


class MultiSelectQuestion(Question):
    """
    Multi-select question type demonstrating polymorphism.
    """
    
    def __init__(self, id: str, topic: str, question_text: str, 
                 options: List[str], correct_answers: List[str], 
                 difficulty: str = "Hard", tag: Optional[str] = None, **kwargs):
        """
        Initialize multi-select question.
        
        Args:
            id: Unique identifier
            topic: Question topic
            question_text: The question text
            options: List of all options
            correct_answers: List of correct answers
            difficulty: Question difficulty
            tag: Optional tag
            **kwargs: Additional keyword arguments
        """
        # Store multiple correct answers
        self.correct_answers = correct_answers
        
        # Pad options to 4 slots
        padded_options = options + [None] * (4 - len(options))
        
        super().__init__(
            id=id,
            topic=topic,
            question_text=question_text,
            option1=padded_options[0],
            option2=padded_options[1],
            option3=padded_options[2],
            option4=padded_options[3],
            correct_answer=",".join(correct_answers),  # Store as comma-separated
            difficulty=difficulty,
            tag=tag,
            **kwargs
        )
    
    def get_question_type(self) -> str:
        """Override: Return multi_select type."""
        return "multi_select"
    
    def get_display_format(self) -> Dict[str, Any]:
        """Override: Return multi-select specific format."""
        options = [opt for opt in [self.option1, self.option2, self.option3, self.option4] if opt]
        return {
            'type': 'multi_select',
            'question': self.question_text,
            'options': [
                {'label': chr(65+i), 'text': opt} for i, opt in enumerate(options)
            ],
            'correct_answers': self.correct_answers,
            'selection_type': 'multiple'
        }
    
    def validate_answer(self, user_answer: str) -> bool:
        """Override: Validate multiple answers."""
        user_answers = [ans.strip() for ans in user_answer.split(',') if ans.strip()]
        correct_set = set(self.correct_answers)
        user_set = set(user_answers)
        return correct_set == user_set
    
    def calculate_difficulty_score(self) -> float:
        """Override: Highest scoring for multi-select."""
        difficulty_multipliers = {'Easy': 1.5, 'Medium': 2.0, 'Hard': 3.0}
        base_score = difficulty_multipliers.get(self.difficulty, 2.0)
        
        # Add complexity based on number of correct answers
        complexity_factor = 1.0 + (len(self.correct_answers) - 1) * 0.2
        
        return base_score * complexity_factor
    
    def get_hint(self) -> str:
        """Override: Multi-select specific hint."""
        return f"This is a {self.difficulty.lower()} multi-select question. Select {len(self.correct_answers)} correct option(s)."
    
    def get_time_limit(self) -> int:
        """Override: Extended time for multi-select."""
        base_times = {'Easy': 45, 'Medium': 60, 'Hard': 90}
        extra_time = (len(self.correct_answers) - 1) * 15
        return base_times.get(self.difficulty, 60) + extra_time


class EssayQuestion(Question):
    """
    Essay question type demonstrating polymorphism.
    """
    
    def __init__(self, id: str, topic: str, question_text: str, 
                 expected_keywords: List[str], difficulty: str = "Hard", 
                 tag: Optional[str] = None, **kwargs):
        """
        Initialize essay question.
        
        Args:
            id: Unique identifier
            topic: Question topic
            question_text: The essay prompt
            expected_keywords: List of keywords expected in answer
            difficulty: Question difficulty
            tag: Optional tag
            **kwargs: Additional keyword arguments
        """
        self.expected_keywords = expected_keywords
        
        super().__init__(
            id=id,
            topic=topic,
            question_text=question_text,
            option1=None,
            option2=None,
            option3=None,
            option4=None,
            correct_answer=",".join(expected_keywords),  # Store keywords as correct answer
            difficulty=difficulty,
            tag=tag,
            **kwargs
        )
    
    def get_question_type(self) -> str:
        """Override: Return essay type."""
        return "essay"
    
    def get_display_format(self) -> Dict[str, Any]:
        """Override: Return essay specific format."""
        return {
            'type': 'essay',
            'question': self.question_text,
            'expected_keywords': self.expected_keywords,
            'response_type': 'text'
        }
    
    def validate_answer(self, user_answer: str) -> bool:
        """Override: Validate essay based on keywords."""
        user_text_lower = user_answer.lower()
        found_keywords = sum(1 for keyword in self.expected_keywords 
                           if keyword.lower() in user_text_lower)
        # Consider correct if at least 50% of keywords are found
        return found_keywords >= len(self.expected_keywords) // 2
    
    def calculate_difficulty_score(self) -> float:
        """Override: Variable scoring for essay."""
        difficulty_multipliers = {'Easy': 2.0, 'Medium': 2.5, 'Hard': 3.5}
        base_score = difficulty_multipliers.get(self.difficulty, 2.5)
        
        # Add complexity based on number of expected keywords
        keyword_factor = 1.0 + (len(self.expected_keywords) * 0.1)
        
        return base_score * keyword_factor
    
    def get_hint(self) -> str:
        """Override: Essay specific hint."""
        return f"This is a {self.difficulty.lower()} essay question. Include key concepts in your answer."
    
    def get_time_limit(self) -> int:
        """Override: Extended time for essay."""
        base_times = {'Easy': 180, 'Medium': 300, 'Hard': 600}  # 3, 5, 10 minutes
        return base_times.get(self.difficulty, 300)


def create_question(question_type: str, **kwargs) -> Question:
    """
    Factory function to create different question types (polymorphism).
    
    Args:
        question_type: Type of question to create
        **kwargs: Arguments for question constructor
        
    Returns:
        Appropriate question instance
    """
    question_classes = {
        'multiple_choice': Question,
        'true_false': TrueFalseQuestion,
        'fill_in_blank': FillInBlankQuestion,
        'multi_select': MultiSelectQuestion,
        'essay': EssayQuestion
    }
    
    if question_type not in question_classes:
        raise ValueError(f"Unknown question type: {question_type}")
    
    return question_classes[question_type](**kwargs)
