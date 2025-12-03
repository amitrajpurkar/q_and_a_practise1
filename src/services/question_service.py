"""
Question service for Q&A Practice Application.

Implements business logic for question management following SOLID principles
with dependency injection and proper separation of concerns.
"""

from typing import List, Optional, Dict, Any
import logging
import random

from src.models.question import Question
from src.services.interfaces import (
    IQuestionService,
    IQuestionRepository,
    QuestionFilter,
)
from src.utils.exceptions import QuestionError, ValidationError
from src.utils.container import DIContainer


class QuestionService(IQuestionService):
    """
    Business logic service for question operations.

    Follows Single Responsibility principle by handling
    only question-related business logic.
    """

    def __init__(
        self,
        question_repository: IQuestionRepository,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """
        Initialize question service.

        Args:
            question_repository: Repository for question data access
            logger: Optional logger instance
        """
        self.question_repository = question_repository
        self.logger = logger or logging.getLogger(__name__)

    def get_available_topics(self) -> List[str]:
        """
        Get list of available topics.

        Returns:
            List of topic names
        """
        try:
            topics = self.question_repository.get_available_topics()
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
            difficulties = self.question_repository.get_available_difficulties()
            self.logger.info(f"Retrieved {len(difficulties)} available difficulties")
            return difficulties
        except Exception as e:
            self.logger.error(f"Failed to get available difficulties: {str(e)}")
            raise QuestionError(f"Failed to retrieve difficulties: {str(e)}")

    def get_random_question(
        self, topic: str, difficulty: str, exclude_ids: Optional[List[str]] = None
    ) -> Optional[Question]:
        """
        Get random question for session.

        Args:
            topic: Question topic
            difficulty: Question difficulty
            exclude_ids: List of question IDs to exclude

        Returns:
            Random question if found, None otherwise
        """
        try:
            # Validate inputs
            if topic not in self.get_available_topics():
                raise ValidationError(f"Invalid topic: {topic}")

            if difficulty not in self.get_available_difficulties():
                raise ValidationError(f"Invalid difficulty: {difficulty}")

            # Create filter criteria
            criteria = QuestionFilter(
                topic=topic, difficulty=difficulty, exclude_ids=exclude_ids
            )

            # Get random question from repository
            question = self.question_repository.get_random(criteria)

            if question:
                self.logger.info(
                    f"Retrieved random question {question.id} for {topic}-{difficulty}"
                )
                # Mark question as asked in session
                question.mark_as_asked()
            else:
                self.logger.warning(
                    f"No questions available for {topic}-{difficulty} excluding {len(exclude_ids)} questions"
                )

            return question

        except (ValidationError, QuestionError):
            raise
        except Exception as e:
            self.logger.error(f"Failed to get random question: {str(e)}")
            raise QuestionError(f"Failed to retrieve random question: {str(e)}")

    def validate_answer(self, question_id: str, user_answer: str) -> bool:
        """
        Validate user answer against correct answer.

        Args:
            question_id: ID of the question
            user_answer: User's answer

        Returns:
            True if answer is correct, False otherwise
        """
        try:
            if not user_answer or not user_answer.strip():
                raise ValidationError("User answer cannot be empty")

            # Get question from repository
            question = self.question_repository.get_by_id(question_id)
            if not question:
                raise QuestionError(f"Question not found: {question_id}", question_id)

            # Validate answer
            is_correct = question.is_correct_answer(user_answer)

            if is_correct:
                question.mark_as_answered(True)
                self.logger.info(f"Correct answer submitted for question {question_id}")
            else:
                question.mark_as_answered(False)
                self.logger.info(
                    f"Incorrect answer submitted for question {question_id}"
                )

            return is_correct

        except (ValidationError, QuestionError):
            raise
        except Exception as e:
            self.logger.error(f"Failed to validate answer: {str(e)}")
            raise QuestionError(f"Failed to validate answer: {str(e)}", question_id)

    def get_question_by_id(self, question_id: str) -> Optional[Question]:
        """
        Get question by ID.

        Args:
            question_id: ID of the question

        Returns:
            Question if found, None otherwise
        """
        try:
            question = self.question_repository.get_by_id(question_id)
            if question:
                self.logger.debug(f"Retrieved question {question_id}")
            else:
                self.logger.warning(f"Question not found: {question_id}")
            return question
        except Exception as e:
            self.logger.error(f"Failed to get question by ID: {str(e)}")
            raise QuestionError(f"Failed to retrieve question: {str(e)}", question_id)

    def get_questions_by_criteria(
        self, topic: str, difficulty: str, limit: Optional[int] = None
    ) -> List[Question]:
        """
        Get questions by topic and difficulty.

        Args:
            topic: Question topic
            difficulty: Question difficulty
            limit: Optional limit on number of questions

        Returns:
            List of matching questions
        """
        try:
            criteria = QuestionFilter(topic=topic, difficulty=difficulty)
            questions = self.question_repository.filter(criteria)

            if limit and len(questions) > limit:
                # Randomly sample if limit is specified
                questions = random.sample(questions, limit)

            self.logger.info(
                f"Retrieved {len(questions)} questions for {topic}-{difficulty}"
            )
            return questions

        except Exception as e:
            self.logger.error(f"Failed to get questions by criteria: {str(e)}")
            raise QuestionError(f"Failed to retrieve questions: {str(e)}")

    def count_questions_by_criteria(self, topic: str, difficulty: str) -> int:
        """
        Count questions by topic and difficulty.

        Args:
            topic: Question topic
            difficulty: Question difficulty

        Returns:
            Number of matching questions
        """
        try:
            criteria = QuestionFilter(topic=topic, difficulty=difficulty)
            count = self.question_repository.count_by_criteria(criteria)
            self.logger.info(f"Counted {count} questions for {topic}-{difficulty}")
            return count
        except Exception as e:
            self.logger.error(f"Failed to count questions: {str(e)}")
            raise QuestionError(f"Failed to count questions: {str(e)}")

    def get_question_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about available questions.

        Returns:
            Dictionary containing question statistics
        """
        try:
            topics = self.get_available_topics()
            difficulties = self.get_available_difficulties()

            stats = {
                "total_topics": len(topics),
                "total_difficulties": len(difficulties),
                "topics": topics,
                "difficulties": difficulties,
                "topic_difficulty_counts": {},
            }

            for topic in topics:
                stats["topic_difficulty_counts"][topic] = {}
                for difficulty in difficulties:
                    count = self.count_questions_by_criteria(topic, difficulty)
                    stats["topic_difficulty_counts"][topic][difficulty] = count

            self.logger.info("Generated question statistics")
            return stats

        except Exception as e:
            self.logger.error(f"Failed to get question statistics: {str(e)}")
            raise QuestionError(f"Failed to generate statistics: {str(e)}")

    def reset_all_session_states(self) -> None:
        """Reset session state for all questions."""
        try:
            all_questions = self.question_repository.get_all()
            for question in all_questions:
                question.reset_session_state()
            self.logger.info(f"Reset session state for {len(all_questions)} questions")
        except Exception as e:
            self.logger.error(f"Failed to reset session states: {str(e)}")
            raise QuestionError(f"Failed to reset session states: {str(e)}")


def register_question_service(
    container: DIContainer, question_repository: IQuestionRepository
) -> None:
    """
    Register question service in dependency injection container.

    Args:
        container: DI container
        question_repository: Question repository instance
    """
    question_service = QuestionService(question_repository)
    container.register_instance(IQuestionService, question_service)
