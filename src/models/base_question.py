"""
Base question classes demonstrating inheritance hierarchies for Q&A Practice Application.

This module defines abstract base classes and inheritance hierarchies
for different types of questions in the system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

from src.utils.exceptions import ValidationError


@dataclass
class BaseQuestion(ABC):
    """
    Abstract base class for all question types.
    
    This class defines the common interface and properties that all
    question types must implement, demonstrating inheritance principles.
    """
    id: str
    topic: str
    question_text: str
    difficulty: str
    tag: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self) -> None:
        """Validate the question after initialization."""
        self._validate_base_fields()
    
    def _validate_base_fields(self) -> None:
        """Validate common fields for all question types."""
        if not self.id or not self.id.strip():
            raise ValidationError("Question ID cannot be empty", "id", self.id)
        
        if not self.topic or not self.topic.strip():
            raise ValidationError("Topic cannot be empty", "topic", self.topic)
        
        if not self.question_text or not self.question_text.strip():
            raise ValidationError("Question text cannot be empty", "question_text", self.question_text)
        
        if not self.difficulty or not self.difficulty.strip():
            raise ValidationError("Difficulty cannot be empty", "difficulty", self.difficulty)
    
    @abstractmethod
    def get_question_type(self) -> str:
        """
        Get the type of this question.
        
        Returns:
            String representing question type
        """
        pass
    
    @abstractmethod
    def validate_answer(self, user_answer: str) -> bool:
        """
        Validate user's answer.
        
        Args:
            user_answer: User's submitted answer
            
        Returns:
            True if answer is correct, False otherwise
        """
        pass
    
    @abstractmethod
    def get_display_format(self) -> Dict[str, Any]:
        """
        Get display format for this question.
        
        Returns:
            Dictionary with display information
        """
        pass
    
    @abstractmethod
    def calculate_difficulty_score(self) -> float:
        """
        Calculate difficulty score for this question.
        
        Returns:
            Float representing difficulty score
        """
        pass
    
    @abstractmethod
    def get_hint(self) -> str:
        """
        Get hint for this question.
        
        Returns:
            Hint string for the question
        """
        pass
    
    @abstractmethod
    def get_time_limit(self) -> int:
        """
        Get time limit for this question.
        
        Returns:
            Time limit in seconds
        """
        pass
    
    def __str__(self) -> str:
        """String representation of base question."""
        return f"BaseQuestion(id={self.id}, type={self.get_question_type()}, topic={self.topic})"
    
    def __repr__(self) -> str:
        """Detailed string representation of base question."""
        return (
            f"BaseQuestion(id='{self.id}', type='{self.get_question_type()}', "
            f"topic='{self.topic}', difficulty='{self.difficulty}')"
        )


@dataclass
class ChoiceBasedQuestion(BaseQuestion):
    """
    Base class for questions that have multiple choice options.
    
    This class extends BaseQuestion and adds properties specific
    to choice-based questions, demonstrating inheritance.
    """
    option1: Optional[str] = None
    option2: Optional[str] = None
    option3: Optional[str] = None
    option4: Optional[str] = None
    correct_answer: str = ""
    
    def __post_init__(self) -> None:
        """Validate choice-based question fields."""
        super().__post_init__()
        self._validate_choice_fields()
    
    def _validate_choice_fields(self) -> None:
        """Validate fields specific to choice-based questions."""
        if not self.correct_answer or not self.correct_answer.strip():
            raise ValidationError("Correct answer cannot be empty", "correct_answer", self.correct_answer)
        
        # Count non-None options
        options = [self.option1, self.option2, self.option3, self.option4]
        valid_options = [opt for opt in options if opt and opt.strip()]
        
        if len(valid_options) < 2:
            raise ValidationError("Choice-based questions must have at least 2 options", "options", options)
    
    def get_all_options(self) -> List[str]:
        """
        Get all valid options for this question.
        
        Returns:
            List of non-empty option strings
        """
        options = [self.option1, self.option2, self.option3, self.option4]
        return [opt for opt in options if opt and opt.strip()]
    
    def has_multiple_correct_answers(self) -> bool:
        """
        Check if this question has multiple correct answers.
        
        Returns:
            True if multiple correct answers, False otherwise
        """
        return ',' in self.correct_answer
    
    def get_correct_answers_list(self) -> List[str]:
        """
        Get list of correct answers.
        
        Returns:
            List of correct answer strings
        """
        return [ans.strip() for ans in self.correct_answer.split(',') if ans.strip()]


@dataclass
class TextBasedQuestion(BaseQuestion):
    """
    Base class for questions that require text-based answers.
    
    This class extends BaseQuestion and adds properties specific
    to text-based questions, demonstrating inheritance.
    """
    expected_answer: str = ""
    case_sensitive: bool = False
    allow_partial_credit: bool = False
    
    def __post_init__(self) -> None:
        """Validate text-based question fields."""
        super().__post_init__()
        self._validate_text_fields()
    
    def _validate_text_fields(self) -> None:
        """Validate fields specific to text-based questions."""
        if not self.expected_answer or not self.expected_answer.strip():
            raise ValidationError("Expected answer cannot be empty", "expected_answer", self.expected_answer)
    
    def normalize_answer(self, answer: str) -> str:
        """
        Normalize answer for comparison.
        
        Args:
            answer: Answer to normalize
            
        Returns:
            Normalized answer string
        """
        if self.case_sensitive:
            return answer.strip()
        else:
            return answer.strip().lower()
    
    def calculate_similarity_score(self, user_answer: str) -> float:
        """
        Calculate similarity score between user answer and expected answer.
        
        Args:
            user_answer: User's submitted answer
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        from difflib import SequenceMatcher
        
        normalized_user = self.normalize_answer(user_answer)
        normalized_expected = self.normalize_answer(self.expected_answer)
        
        return SequenceMatcher(None, normalized_user, normalized_expected).ratio()


@dataclass
class InteractiveQuestion(BaseQuestion):
    """
    Base class for interactive questions with multimedia or dynamic elements.
    
    This class extends BaseQuestion and adds properties specific
    to interactive questions, demonstrating inheritance.
    """
    media_url: Optional[str] = None
    interactive_elements: List[Dict[str, Any]] = None
    requires_special_input: bool = False
    
    def __post_init__(self) -> None:
        """Validate interactive question fields."""
        super().__post_init__()
        if self.interactive_elements is None:
            self.interactive_elements = []
        self._validate_interactive_fields()
    
    def _validate_interactive_fields(self) -> None:
        """Validate fields specific to interactive questions."""
        if self.media_url and not self.media_url.strip():
            raise ValidationError("Media URL cannot be empty if provided", "media_url", self.media_url)
    
    def has_media(self) -> bool:
        """Check if question has media content."""
        return bool(self.media_url)
    
    def get_interactive_element_count(self) -> int:
        """Get count of interactive elements."""
        return len(self.interactive_elements)


@dataclass
class AdaptiveQuestion(BaseQuestion):
    """
    Base class for adaptive questions that change based on user performance.
    
    This class extends BaseQuestion and adds properties specific
    to adaptive questions, demonstrating inheritance.
    """
    adaptive_difficulty: bool = False
    prerequisite_topics: List[str] = None
    follow_up_questions: List[str] = None
    
    def __post_init__(self) -> None:
        """Validate adaptive question fields."""
        super().__post_init__()
        if self.prerequisite_topics is None:
            self.prerequisite_topics = []
        if self.follow_up_questions is None:
            self.follow_up_questions = []
        self._validate_adaptive_fields()
    
    def _validate_adaptive_fields(self) -> None:
        """Validate fields specific to adaptive questions."""
        # Validate prerequisite topics
        for topic in self.prerequisite_topics:
            if not topic or not topic.strip():
                raise ValidationError("Prerequisite topics cannot be empty", "prerequisite_topics", self.prerequisite_topics)
    
    def has_prerequisites(self) -> bool:
        """Check if question has prerequisite topics."""
        return len(self.prerequisite_topics) > 0
    
    def has_follow_ups(self) -> bool:
        """Check if question has follow-up questions."""
        return len(self.follow_up_questions) > 0
    
    def should_adapt_difficulty(self, user_performance: float) -> str:
        """
        Determine if difficulty should be adapted based on performance.
        
        Args:
            user_performance: User's performance score (0.0 to 1.0)
            
        Returns:
            Suggested difficulty adjustment
        """
        if not self.adaptive_difficulty:
            return self.difficulty
        
        if user_performance > 0.8:
            # Increase difficulty if performing well
            difficulty_order = ['Easy', 'Medium', 'Hard']
            current_index = difficulty_order.index(self.difficulty)
            if current_index < len(difficulty_order) - 1:
                return difficulty_order[current_index + 1]
        elif user_performance < 0.4:
            # Decrease difficulty if struggling
            difficulty_order = ['Easy', 'Medium', 'Hard']
            current_index = difficulty_order.index(self.difficulty)
            if current_index > 0:
                return difficulty_order[current_index - 1]
        
        return self.difficulty


class QuestionFactory:
    """
    Factory class for creating questions based on inheritance hierarchy.
    
    This class demonstrates the Factory pattern working with
    inheritance hierarchies.
    """
    
    @staticmethod
    def create_base_question(question_data: Dict[str, Any]) -> BaseQuestion:
        """
        Create a base question from data.
        
        Args:
            question_data: Dictionary with question data
            
        Returns:
            BaseQuestion instance
        """
        # This would be implemented by concrete subclasses
        raise NotImplementedError("Subclasses must implement create_base_question")
    
    @staticmethod
    def create_choice_question(question_data: Dict[str, Any]) -> ChoiceBasedQuestion:
        """
        Create a choice-based question from data.
        
        Args:
            question_data: Dictionary with question data
            
        Returns:
            ChoiceBasedQuestion instance
        """
        # This would be implemented by concrete subclasses
        raise NotImplementedError("Subclasses must implement create_choice_question")
    
    @staticmethod
    def create_text_question(question_data: Dict[str, Any]) -> TextBasedQuestion:
        """
        Create a text-based question from data.
        
        Args:
            question_data: Dictionary with question data
            
        Returns:
            TextBasedQuestion instance
        """
        # This would be implemented by concrete subclasses
        raise NotImplementedError("Subclasses must implement create_text_question")
    
    @staticmethod
    def create_interactive_question(question_data: Dict[str, Any]) -> InteractiveQuestion:
        """
        Create an interactive question from data.
        
        Args:
            question_data: Dictionary with question data
            
        Returns:
            InteractiveQuestion instance
        """
        # This would be implemented by concrete subclasses
        raise NotImplementedError("Subclasses must implement create_interactive_question")
    
    @staticmethod
    def create_adaptive_question(question_data: Dict[str, Any]) -> AdaptiveQuestion:
        """
        Create an adaptive question from data.
        
        Args:
            question_data: Dictionary with question data
            
        Returns:
            AdaptiveQuestion instance
        """
        # This would be implemented by concrete subclasses
        raise NotImplementedError("Subclasses must implement create_adaptive_question")


def validate_question_hierarchy(question: BaseQuestion) -> bool:
    """
    Validate that a question follows the proper inheritance hierarchy.
    
    Args:
        question: Question to validate
        
    Returns:
        True if valid hierarchy, False otherwise
    """
    # Check if question is instance of BaseQuestion
    if not isinstance(question, BaseQuestion):
        return False
    
    # Check if required abstract methods are implemented
    required_methods = [
        'get_question_type',
        'validate_answer', 
        'get_display_format',
        'calculate_difficulty_score',
        'get_hint',
        'get_time_limit'
    ]
    
    for method_name in required_methods:
        if not hasattr(question, method_name):
            return False
        
        method = getattr(question, method_name)
        if not callable(method):
            return False
    
    return True


def get_question_hierarchy_info(question: BaseQuestion) -> Dict[str, Any]:
    """
    Get information about a question's place in the inheritance hierarchy.
    
    Args:
        question: Question to analyze
        
    Returns:
        Dictionary with hierarchy information
    """
    hierarchy_info = {
        'class_name': question.__class__.__name__,
        'base_classes': [base.__name__ for base in question.__class__.__mro__[1:]],
        'is_choice_based': isinstance(question, ChoiceBasedQuestion),
        'is_text_based': isinstance(question, TextBasedQuestion),
        'is_interactive': isinstance(question, InteractiveQuestion),
        'is_adaptive': isinstance(question, AdaptiveQuestion),
        'question_type': question.get_question_type()
    }
    
    return hierarchy_info
