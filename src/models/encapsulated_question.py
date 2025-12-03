"""
Encapsulated question classes demonstrating proper data protection for Q&A Practice Application.

This module implements encapsulation principles to protect sensitive data
and ensure controlled access to question properties.
"""

from typing import Dict, Any, Optional, List, Set
from datetime import datetime
import logging
from dataclasses import dataclass, field

from src.utils.exceptions import ValidationError, QuestionError


class EncapsulatedQuestion:
    """
    Encapsulated question class with proper data protection.
    
    This class demonstrates encapsulation by making all fields private
    and providing controlled access through getter and setter methods.
    """
    
    def __init__(self, id: str, topic: str, question_text: str, 
                 correct_answer: str, difficulty: str = "Medium",
                 options: Optional[List[str]] = None, tag: Optional[str] = None):
        """
        Initialize encapsulated question.
        
        Args:
            id: Unique identifier
            topic: Question topic
            question_text: The question text
            correct_answer: The correct answer
            difficulty: Question difficulty
            options: List of answer options
            tag: Optional tag
        """
        self._id = self._validate_and_set_id(id)
        self._topic = self._validate_and_set_topic(topic)
        self._question_text = self._validate_and_set_question_text(question_text)
        self._correct_answer = self._validate_and_set_correct_answer(correct_answer)
        self._difficulty = self._validate_and_set_difficulty(difficulty)
        self._options = self._validate_and_set_options(options or [])
        self._tag = self._validate_and_set_tag(tag)
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
        self._access_count = 0
        self._is_active = True
        self._metadata = {}
        
        # Private validation cache
        self._validation_cache = {}
        self._logger = logging.getLogger(__name__)
    
    # Private validation methods
    def _validate_and_set_id(self, id: str) -> str:
        """Validate and set question ID."""
        if not id or not isinstance(id, str) or not id.strip():
            raise ValidationError("Question ID must be a non-empty string", "id", id)
        return id.strip()
    
    def _validate_and_set_topic(self, topic: str) -> str:
        """Validate and set question topic."""
        if not topic or not isinstance(topic, str) or not topic.strip():
            raise ValidationError("Topic must be a non-empty string", "topic", topic)
        
        valid_topics = {"Physics", "Chemistry", "Math"}
        if topic not in valid_topics:
            raise ValidationError(
                f"Invalid topic '{topic}'. Must be one of: {valid_topics}",
                "topic", topic
            )
        return topic
    
    def _validate_and_set_question_text(self, question_text: str) -> str:
        """Validate and set question text."""
        if not question_text or not isinstance(question_text, str) or not question_text.strip():
            raise ValidationError("Question text must be a non-empty string", "question_text", question_text)
        
        if len(question_text) > 1000:
            raise ValidationError("Question text cannot exceed 1000 characters", "question_text", question_text)
        
        return question_text.strip()
    
    def _validate_and_set_correct_answer(self, correct_answer: str) -> str:
        """Validate and set correct answer."""
        if not correct_answer or not isinstance(correct_answer, str) or not correct_answer.strip():
            raise ValidationError("Correct answer must be a non-empty string", "correct_answer", correct_answer)
        return correct_answer.strip()
    
    def _validate_and_set_difficulty(self, difficulty: str) -> str:
        """Validate and set question difficulty."""
        if not difficulty or not isinstance(difficulty, str) or not difficulty.strip():
            raise ValidationError("Difficulty must be a non-empty string", "difficulty", difficulty)
        
        valid_difficulties = {"Easy", "Medium", "Hard"}
        if difficulty not in valid_difficulties:
            raise ValidationError(
                f"Invalid difficulty '{difficulty}'. Must be one of: {valid_difficulties}",
                "difficulty", difficulty
            )
        return difficulty
    
    def _validate_and_set_options(self, options: List[str]) -> List[str]:
        """Validate and set question options."""
        if not isinstance(options, list):
            raise ValidationError("Options must be a list", "options", options)
        
        validated_options = []
        for i, option in enumerate(options):
            if option is not None:
                if not isinstance(option, str):
                    raise ValidationError(f"Option {i} must be a string", "options", options)
                validated_options.append(option.strip())
            else:
                validated_options.append(None)
        
        return validated_options
    
    def _validate_and_set_tag(self, tag: Optional[str]) -> Optional[str]:
        """Validate and set question tag."""
        if tag is None:
            return None
        
        if not isinstance(tag, str):
            raise ValidationError("Tag must be a string", "tag", tag)
        
        return tag.strip() if tag.strip() else None
    
    # Public getter methods (controlled access)
    def get_id(self) -> str:
        """Get question ID with access tracking."""
        self._track_access("id")
        return self._id
    
    def get_topic(self) -> str:
        """Get question topic with access tracking."""
        self._track_access("topic")
        return self._topic
    
    def get_question_text(self) -> str:
        """Get question text with access tracking."""
        self._track_access("question_text")
        return self._question_text
    
    def get_correct_answer(self, require_auth: bool = False) -> str:
        """
        Get correct answer with optional authentication requirement.
        
        Args:
            require_auth: If True, requires authentication to access
            
        Returns:
            Correct answer if authorized
            
        Raises:
            QuestionError: If authentication is required but not provided
        """
        self._track_access("correct_answer")
        
        if require_auth:
            # In a real implementation, this would check actual authentication
            self._logger.warning(f"Attempted unauthorized access to correct answer for question {self._id}")
            raise QuestionError("Authentication required to access correct answer", self._id)
        
        return self._correct_answer
    
    def get_difficulty(self) -> str:
        """Get question difficulty with access tracking."""
        self._track_access("difficulty")
        return self._difficulty
    
    def get_options(self) -> List[str]:
        """Get question options with access tracking."""
        self._track_access("options")
        return self._options.copy()  # Return copy to prevent external modification
    
    def get_tag(self) -> Optional[str]:
        """Get question tag with access tracking."""
        self._track_access("tag")
        return self._tag
    
    def get_created_at(self) -> datetime:
        """Get creation timestamp with access tracking."""
        self._track_access("created_at")
        return self._created_at
    
    def get_updated_at(self) -> datetime:
        """Get last updated timestamp with access tracking."""
        self._track_access("updated_at")
        return self._updated_at
    
    def get_access_count(self) -> int:
        """Get access count (for monitoring)."""
        return self._access_count
    
    def is_active(self) -> bool:
        """Check if question is active."""
        return self._is_active
    
    def get_metadata(self, key: Optional[str] = None) -> Any:
        """
        Get metadata with controlled access.
        
        Args:
            key: Specific metadata key to retrieve, or None for all metadata
            
        Returns:
            Metadata value or dictionary
        """
        self._track_access("metadata")
        
        if key is None:
            return self._metadata.copy()  # Return copy to prevent external modification
        else:
            return self._metadata.get(key)
    
    # Public setter methods (controlled modification)
    def set_topic(self, topic: str) -> None:
        """
        Set question topic with validation.
        
        Args:
            topic: New topic value
        """
        old_topic = self._topic
        self._topic = self._validate_and_set_topic(topic)
        self._update_timestamp()
        self._logger.info(f"Question {self._id}: Topic changed from '{old_topic}' to '{topic}'")
    
    def set_question_text(self, question_text: str) -> None:
        """
        Set question text with validation.
        
        Args:
            question_text: New question text
        """
        old_text = self._question_text
        self._question_text = self._validate_and_set_question_text(question_text)
        self._update_timestamp()
        self._logger.info(f"Question {self._id}: Question text updated")
    
    def set_correct_answer(self, correct_answer: str, require_auth: bool = False) -> None:
        """
        Set correct answer with optional authentication requirement.
        
        Args:
            correct_answer: New correct answer
            require_auth: If True, requires authentication to modify
            
        Raises:
            QuestionError: If authentication is required but not provided
        """
        if require_auth:
            self._logger.warning(f"Attempted unauthorized modification of correct answer for question {self._id}")
            raise QuestionError("Authentication required to modify correct answer", self._id)
        
        old_answer = self._correct_answer
        self._correct_answer = self._validate_and_set_correct_answer(correct_answer)
        self._update_timestamp()
        self._logger.info(f"Question {self._id}: Correct answer updated")
    
    def set_difficulty(self, difficulty: str) -> None:
        """
        Set question difficulty with validation.
        
        Args:
            difficulty: New difficulty value
        """
        old_difficulty = self._difficulty
        self._difficulty = self._validate_and_set_difficulty(difficulty)
        self._update_timestamp()
        self._logger.info(f"Question {self._id}: Difficulty changed from '{old_difficulty}' to '{difficulty}'")
    
    def set_options(self, options: List[str]) -> None:
        """
        Set question options with validation.
        
        Args:
            options: New list of options
        """
        old_options = self._options.copy()
        self._options = self._validate_and_set_options(options)
        self._update_timestamp()
        self._logger.info(f"Question {self._id}: Options updated")
    
    def set_tag(self, tag: Optional[str]) -> None:
        """
        Set question tag with validation.
        
        Args:
            tag: New tag value or None
        """
        old_tag = self._tag
        self._tag = self._validate_and_set_tag(tag)
        self._update_timestamp()
        self._logger.info(f"Question {self._id}: Tag changed from '{old_tag}' to '{tag}'")
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata value with validation.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        if not isinstance(key, str) or not key.strip():
            raise ValidationError("Metadata key must be a non-empty string", "metadata_key", key)
        
        self._metadata[key.strip()] = value
        self._update_timestamp()
    
    def activate(self) -> None:
        """Activate the question."""
        if not self._is_active:
            self._is_active = True
            self._update_timestamp()
            self._logger.info(f"Question {self._id}: Activated")
    
    def deactivate(self) -> None:
        """Deactivate the question."""
        if self._is_active:
            self._is_active = False
            self._update_timestamp()
            self._logger.info(f"Question {self._id}: Deactivated")
    
    # Private helper methods
    def _track_access(self, field: str) -> None:
        """Track field access for monitoring."""
        self._access_count += 1
        if field not in self._validation_cache:
            self._validation_cache[field] = 0
        self._validation_cache[field] += 1
    
    def _update_timestamp(self) -> None:
        """Update the last modified timestamp."""
        self._updated_at = datetime.now()
    
    # Public business methods
    def validate_answer(self, user_answer: str) -> bool:
        """
        Validate user's answer.
        
        Args:
            user_answer: User's submitted answer
            
        Returns:
            True if answer is correct, False otherwise
        """
        self._track_access("validate_answer")
        
        if not user_answer or not isinstance(user_answer, str):
            return False
        
        return user_answer.strip().lower() == self._correct_answer.lower()
    
    def get_display_format(self, hide_answer: bool = True) -> Dict[str, Any]:
        """
        Get display format for the question.
        
        Args:
            hide_answer: Whether to hide the correct answer
            
        Returns:
            Dictionary with display information
        """
        self._track_access("display_format")
        
        display_data = {
            'id': self._id,
            'topic': self._topic,
            'question_text': self._question_text,
            'difficulty': self._difficulty,
            'options': [opt for opt in self._options if opt is not None],
            'tag': self._tag
        }
        
        if not hide_answer:
            display_data['correct_answer'] = self._correct_answer
        
        return display_data
    
    def get_access_statistics(self) -> Dict[str, int]:
        """
        Get access statistics for monitoring.
        
        Returns:
            Dictionary with field access counts
        """
        return {
            'total_access': self._access_count,
            'field_access': self._validation_cache.copy()
        }
    
    def reset_access_statistics(self) -> None:
        """Reset access statistics."""
        self._access_count = 0
        self._validation_cache.clear()
        self._logger.info(f"Question {self._id}: Access statistics reset")
    
    def clone(self, new_id: str) -> 'EncapsulatedQuestion':
        """
        Create a clone of this question with a new ID.
        
        Args:
            new_id: ID for the cloned question
            
        Returns:
            New EncapsulatedQuestion instance
        """
        cloned = EncapsulatedQuestion(
            id=new_id,
            topic=self._topic,
            question_text=self._question_text,
            correct_answer=self._correct_answer,
            difficulty=self._difficulty,
            options=self._options.copy(),
            tag=self._tag
        )
        
        # Copy metadata
        cloned._metadata = self._metadata.copy()
        
        self._logger.info(f"Question {self._id}: Cloned to {new_id}")
        return cloned
    
    def __str__(self) -> str:
        """String representation (limited for security)."""
        return f"EncapsulatedQuestion(id={self._id}, topic={self._topic}, difficulty={self._difficulty})"
    
    def __repr__(self) -> str:
        """Detailed string representation (limited for security)."""
        return (
            f"EncapsulatedQuestion(id='{self._id}', topic='{self._topic}', "
            f"difficulty='{self._difficulty}', active={self._is_active})"
        )


class SecureQuestionManager:
    """
    Manager class for secure question operations.
    
    This class demonstrates encapsulation by managing access to
    encapsulated questions with proper security controls.
    """
    
    def __init__(self):
        """Initialize the secure question manager."""
        self._questions: Dict[str, EncapsulatedQuestion] = {}
        self._access_log: List[Dict[str, Any]] = []
        self._logger = logging.getLogger(__name__)
    
    def add_question(self, question: EncapsulatedQuestion) -> None:
        """
        Add a question to the manager.
        
        Args:
            question: Question to add
        """
        if not isinstance(question, EncapsulatedQuestion):
            raise ValidationError("Only EncapsulatedQuestion instances can be added", "question_type", type(question))
        
        question_id = question.get_id()
        if question_id in self._questions:
            raise ValidationError(f"Question with ID '{question_id}' already exists", "question_id", question_id)
        
        self._questions[question_id] = question
        self._log_access("add_question", question_id)
        self._logger.info(f"Added question {question_id} to secure manager")
    
    def get_question(self, question_id: str, hide_answer: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get a question with security controls.
        
        Args:
            question_id: ID of question to retrieve
            hide_answer: Whether to hide the correct answer
            
        Returns:
            Question display format or None if not found
        """
        self._log_access("get_question", question_id)
        
        question = self._questions.get(question_id)
        if question is None:
            return None
        
        if not question.is_active():
            self._logger.warning(f"Attempted access to inactive question {question_id}")
            return None
        
        return question.get_display_format(hide_answer)
    
    def update_question(self, question_id: str, updates: Dict[str, Any], 
                       require_auth: bool = False) -> bool:
        """
        Update a question with security controls.
        
        Args:
            question_id: ID of question to update
            updates: Dictionary of field updates
            require_auth: Whether authentication is required
            
        Returns:
            True if successful, False otherwise
        """
        self._log_access("update_question", question_id)
        
        question = self._questions.get(question_id)
        if question is None:
            return False
        
        try:
            for field, value in updates.items():
                if field == "topic":
                    question.set_topic(value)
                elif field == "question_text":
                    question.set_question_text(value)
                elif field == "correct_answer":
                    question.set_correct_answer(value, require_auth)
                elif field == "difficulty":
                    question.set_difficulty(value)
                elif field == "options":
                    question.set_options(value)
                elif field == "tag":
                    question.set_tag(value)
                else:
                    self._logger.warning(f"Attempted to update invalid field '{field}' for question {question_id}")
            
            return True
        except (ValidationError, QuestionError) as e:
            self._logger.error(f"Failed to update question {question_id}: {str(e)}")
            return False
    
    def delete_question(self, question_id: str, require_auth: bool = False) -> bool:
        """
        Delete a question with security controls.
        
        Args:
            question_id: ID of question to delete
            require_auth: Whether authentication is required
            
        Returns:
            True if successful, False otherwise
        """
        self._log_access("delete_question", question_id)
        
        if require_auth:
            self._logger.warning(f"Attempted unauthorized deletion of question {question_id}")
            raise QuestionError("Authentication required to delete questions", question_id)
        
        if question_id in self._questions:
            del self._questions[question_id]
            self._logger.info(f"Deleted question {question_id} from secure manager")
            return True
        
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get manager statistics.
        
        Returns:
            Dictionary with statistics
        """
        total_questions = len(self._questions)
        active_questions = sum(1 for q in self._questions.values() if q.is_active())
        
        topic_counts = {}
        difficulty_counts = {}
        
        for question in self._questions.values():
            topic = question.get_topic()
            difficulty = question.get_difficulty()
            
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
            difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1
        
        return {
            'total_questions': total_questions,
            'active_questions': active_questions,
            'inactive_questions': total_questions - active_questions,
            'topic_distribution': topic_counts,
            'difficulty_distribution': difficulty_counts,
            'access_log_entries': len(self._access_log)
        }
    
    def _log_access(self, operation: str, question_id: str) -> None:
        """Log access for security monitoring."""
        log_entry = {
            'timestamp': datetime.now(),
            'operation': operation,
            'question_id': question_id
        }
        self._access_log.append(log_entry)
        
        # Keep log size manageable
        if len(self._access_log) > 1000:
            self._access_log = self._access_log[-500:]
