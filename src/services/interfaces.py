"""
Base interfaces for repository pattern implementation.

Follows SOLID principles by defining abstractions that
high-level modules can depend on instead of concrete implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class QuestionFilter:
    """Filter criteria for question queries."""
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    exclude_ids: Optional[List[str]] = None


class IRepository(ABC):
    """
    Base repository interface following SOLID principles.
    
    Defines contract for data access operations that
    concrete implementations must follow.
    """
    
    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[Any]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Any]:
        """Get all entities."""
        pass
    
    @abstractmethod
    def filter(self, criteria: QuestionFilter) -> List[Any]:
        """Filter entities based on criteria."""
        pass
    
    @abstractmethod
    def save(self, entity: Any) -> Any:
        """Save entity."""
        pass


class IQuestionRepository(IRepository):
    """
    Interface for question data access operations.
    
    Follows Interface Segregation principle by providing
    only methods needed for question management.
    """
    
    @abstractmethod
    def get_by_id(self, question_id: str) -> Optional[Any]:
        """Get question by ID."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Any]:
        """Get all questions."""
        pass
    
    @abstractmethod
    def filter(self, criteria: QuestionFilter) -> List[Any]:
        """Filter questions by topic and difficulty."""
        pass
    
    @abstractmethod
    def get_random(self, criteria: QuestionFilter) -> Optional[Any]:
        """Get random question matching criteria."""
        pass
    
    @abstractmethod
    def count_by_criteria(self, criteria: QuestionFilter) -> int:
        """Count questions matching criteria."""
        pass


class ISessionRepository(IRepository):
    """
    Interface for session data access operations.
    
    Provides methods for session lifecycle management
    following Single Responsibility principle.
    """
    
    @abstractmethod
    def create_session(self, topic: str, difficulty: str, total_questions: int) -> str:
        """Create new practice session."""
        pass
    
    @abstractmethod
    def get_session(self, session_id: str) -> Optional[Any]:
        """Get session by ID."""
        pass
    
    @abstractmethod
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data."""
        pass
    
    @abstractmethod
    def delete_session(self, session_id: str) -> bool:
        """Delete session."""
        pass


class IQuestionService(ABC):
    """
    Interface for question business logic operations.
    
    Follows Dependency Inversion principle by allowing
    high-level modules to depend on this abstraction.
    """
    
    @abstractmethod
    def get_available_topics(self) -> List[str]:
        """Get list of available topics."""
        pass
    
    @abstractmethod
    def get_available_difficulties(self) -> List[str]:
        """Get list of available difficulty levels."""
        pass
    
    @abstractmethod
    def get_random_question(self, topic: str, difficulty: str, exclude_ids: List[str]) -> Optional[Any]:
        """Get random question for session."""
        pass
    
    @abstractmethod
    def validate_answer(self, question_id: str, user_answer: str) -> bool:
        """Validate user answer against correct answer."""
        pass


class ISessionService(ABC):
    """
    Interface for session business logic operations.
    
    Defines contract for session management following
    SOLID principles.
    """
    
    @abstractmethod
    def create_session(self, topic: str, difficulty: str, total_questions: int = 10) -> str:
        """Create new practice session."""
        pass
    
    @abstractmethod
    def get_session(self, session_id: str) -> Optional[Any]:
        """Get session details."""
        pass
    
    @abstractmethod
    def submit_answer(self, session_id: str, question_id: str, answer: str) -> bool:
        """Submit answer for current question."""
        pass
    
    @abstractmethod
    def get_next_question(self, session_id: str) -> Optional[Any]:
        """Get next question for session."""
        pass
    
    @abstractmethod
    def complete_session(self, session_id: str) -> Optional[Any]:
        """Complete session and return score."""
        pass


class IScoreService(ABC):
    """
    Interface for score calculation operations.
    
    Follows Single Responsibility principle by focusing
    only on score-related operations.
    """
    
    @abstractmethod
    def calculate_score(self, session_id: str) -> Optional[Any]:
        """Calculate final score for session."""
        pass
    
    @abstractmethod
    def get_current_score(self, session_id: str) -> Optional[Any]:
        """Get current session score."""
        pass
    
    @abstractmethod
    def generate_summary(self, session_id: str) -> Dict[str, Any]:
        """Generate session performance summary."""
        pass
