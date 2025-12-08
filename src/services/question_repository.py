"""
Concrete question repository implementation.

Implements the IQuestionRepository interface following SOLID principles.
"""

from typing import List, Optional
import logging

from src.services.interfaces import IQuestionRepository, QuestionFilter
from src.models.question import Question
from src.models.question_bank import QuestionBank
from src.utils.exceptions import QuestionError


class QuestionRepository(IQuestionRepository):
    """
    Concrete implementation of question repository.
    
    Follows Single Responsibility principle by handling
    only question data access operations.
    """
    
    def __init__(self, question_bank: QuestionBank, logger: Optional[logging.Logger] = None) -> None:
        """
        Initialize question repository.
        
        Args:
            question_bank: Question bank instance
            logger: Optional logger instance
        """
        self.question_bank = question_bank
        self.logger = logger or logging.getLogger(__name__)
    
    def get_by_id(self, question_id: str) -> Optional[Question]:
        """
        Get question by ID.
        
        Args:
            question_id: ID of the question
            
        Returns:
            Question if found, None otherwise
        """
        try:
            question = self.question_bank.get_question_by_id(question_id)
            if question:
                self.logger.debug(f"Retrieved question {question_id}")
            return question
        except Exception as e:
            self.logger.error(f"Failed to get question by ID {question_id}: {str(e)}")
            raise QuestionError(f"Failed to retrieve question: {str(e)}", question_id)
    
    def get_all(self) -> List[Question]:
        """
        Get all questions.
        
        Returns:
            List of all questions
        """
        try:
            questions = self.question_bank.get_all_questions()
            self.logger.info(f"Retrieved {len(questions)} questions")
            return questions
        except Exception as e:
            self.logger.error(f"Failed to get all questions: {str(e)}")
            raise QuestionError(f"Failed to retrieve questions: {str(e)}")
    
    def filter(self, criteria: QuestionFilter) -> List[Question]:
        """
        Filter questions based on criteria.
        
        Args:
            criteria: Filter criteria
            
        Returns:
            Filtered list of questions
        """
        try:
            questions = self.question_bank.filter_questions(criteria)
            self.logger.info(f"Filtered {len(questions)} questions by criteria")
            return questions
        except Exception as e:
            self.logger.error(f"Failed to filter questions: {str(e)}")
            raise QuestionError(f"Failed to filter questions: {str(e)}")
    
    def get_random(self, criteria: QuestionFilter) -> Optional[Question]:
        """
        Get random question matching criteria.
        
        Args:
            criteria: Filter criteria
            
        Returns:
            Random question if found, None otherwise
        """
        try:
            question = self.question_bank.get_random_question(criteria)
            if question:
                self.logger.debug(f"Retrieved random question {question.id}")
            return question
        except Exception as e:
            self.logger.error(f"Failed to get random question: {str(e)}")
            raise QuestionError(f"Failed to retrieve random question: {str(e)}")
    
    def count_by_criteria(self, criteria: QuestionFilter) -> int:
        """
        Count questions matching criteria.
        
        Args:
            criteria: Filter criteria
            
        Returns:
            Number of matching questions
        """
        try:
            count = self.question_bank.count_questions(criteria)
            self.logger.info(f"Counted {count} questions by criteria")
            return count
        except Exception as e:
            self.logger.error(f"Failed to count questions: {str(e)}")
            raise QuestionError(f"Failed to count questions: {str(e)}")
    
    def get_available_topics(self) -> List[str]:
        """
        Get list of available topics.
        
        Returns:
            List of topic names
        """
        try:
            topics = self.question_bank.get_available_topics()
            self.logger.info(f"Retrieved {len(topics)} available topics")
            return topics
        except Exception as e:
            self.logger.error(f"Failed to get available topics: {str(e)}")
            raise QuestionError(f"Failed to retrieve topics: {str(e)}")
    
    def get_available_difficulties(self) -> List[str]:
        """
        Get list of available difficulty levels.
        
        Returns:
            List of difficulty names
        """
        try:
            difficulties = self.question_bank.get_available_difficulties()
            self.logger.info(f"Retrieved {len(difficulties)} available difficulties")
            return difficulties
        except Exception as e:
            self.logger.error(f"Failed to get available difficulties: {str(e)}")
            raise QuestionError(f"Failed to retrieve difficulties: {str(e)}")
    
    def save(self, entity: Question) -> Question:
        """
        Save question (not implemented for this repository).
        
        Args:
            entity: Question to save
            
        Returns:
            Saved question
            
        Raises:
            NotImplementedError: This method is not supported
        """
        raise NotImplementedError("Save operation not supported for read-only repository")
