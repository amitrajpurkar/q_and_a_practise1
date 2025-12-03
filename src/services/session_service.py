"""
Session service implementation for Q&A Practice Application.

Implements business logic for session management following SOLID principles.
"""

from typing import List, Optional, Dict, Any
import logging
import uuid

from src.models.session import UserSession
from src.models.question import Question
from src.models.score import Score, AnswerResult
from src.services.interfaces import ISessionService, IQuestionService, IScoreService
from src.utils.exceptions import SessionError, ValidationError


class SessionService(ISessionService):
    """
    Business logic service for session operations.
    
    Follows Single Responsibility principle by handling
    only session-related business logic.
    """
    
    def __init__(self, 
                 question_service: IQuestionService,
                 score_service: IScoreService,
                 logger: Optional[logging.Logger] = None) -> None:
        """
        Initialize session service.
        
        Args:
            question_service: Service for question operations
            score_service: Service for score operations
            logger: Optional logger instance
        """
        self.question_service = question_service
        self.score_service = score_service
        self.logger = logger or logging.getLogger(__name__)
        self._active_sessions: Dict[str, UserSession] = {}
    
    def create_session(self, topic: str, difficulty: str, total_questions: int = 10) -> str:
        """
        Create new practice session.
        
        Args:
            topic: Session topic
            difficulty: Session difficulty
            total_questions: Number of questions in session
            
        Returns:
            Session ID
            
        Raises:
            ValidationError: If parameters are invalid
            SessionError: If session creation fails
        """
        try:
            # Validate inputs
            self._validate_session_parameters(topic, difficulty, total_questions)
            
            # Check if enough questions are available
            available_count = self.question_service.count_questions_by_criteria(topic, difficulty)
            if available_count < total_questions:
                raise SessionError(
                    f"Not enough questions available for {topic}-{difficulty}. "
                    f"Need {total_questions}, have {available_count}"
                )
            
            # Create session
            session = UserSession.create_new(topic, difficulty, total_questions)
            
            # Store session
            self._active_sessions[session.session_id] = session
            
            self.logger.info(
                f"Created new session {session.session_id} for {topic}-{difficulty} with {total_questions} questions",
                extra={
                    "event_type": "session_created",
                    "session_id": session.session_id,
                    "topic": topic,
                    "difficulty": difficulty,
                    "total_questions": total_questions
                }
            )
            
            return session.session_id
            
        except (ValidationError, SessionError):
            raise
        except Exception as e:
            self.logger.error(f"Failed to create session: {str(e)}")
            raise SessionError(f"Failed to create session: {str(e)}")
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """
        Get session details.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session details if found, None otherwise
        """
        try:
            session = self._active_sessions.get(session_id)
            if session:
                self.logger.debug(f"Retrieved session {session_id}")
            else:
                self.logger.warning(f"Session not found: {session_id}")
            return session
        except Exception as e:
            self.logger.error(f"Failed to get session {session_id}: {str(e)}")
            raise SessionError(f"Failed to retrieve session: {str(e)}", session_id)
    
    def submit_answer(self, session_id: str, question_id: str, answer: str) -> bool:
        """
        Submit answer for current question.
        
        Args:
            session_id: Session identifier
            question_id: Question ID
            answer: User's answer
            
        Returns:
            True if answer was submitted successfully
            
        Raises:
            SessionError: If session operations fail
        """
        try:
            session = self.get_session(session_id)
            if not session:
                raise SessionError(f"Session not found: {session_id}", session_id)
            
            # Validate answer
            is_correct = self.question_service.validate_answer(question_id, answer)
            
            # Submit answer to session
            session.submit_answer(question_id, answer)
            
            self.logger.info(
                f"Answer submitted for session {session_id}, question {question_id}, correct: {is_correct}",
                extra={
                    "event_type": "answer_submitted",
                    "session_id": session_id,
                    "question_id": question_id,
                    "is_correct": is_correct
                }
            )
            
            return True
            
        except SessionError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to submit answer: {str(e)}")
            raise SessionError(f"Failed to submit answer: {str(e)}", session_id)
    
    def validate_answer(self, session_id: str, question_id: str, answer: str) -> AnswerResult:
        """
        Validate answer for a question in a session.
        
        Args:
            session_id: Session identifier
            question_id: Question ID
            answer: User's answer
            
        Returns:
            AnswerResult with validation details
            
        Raises:
            SessionError: If session operations fail
            ValidationError: If answer validation fails
        """
        try:
            # Validate input parameters
            if not session_id or not session_id.strip():
                raise ValidationError("Session ID cannot be empty")
            if not question_id or not question_id.strip():
                raise ValidationError("Question ID cannot be empty")
            if not answer or not answer.strip():
                raise ValidationError("Answer cannot be empty")
            
            # Get session
            session = self.get_session(session_id)
            if not session:
                raise SessionError(f"Session not found: {session_id}", session_id)
            
            if not session.is_active:
                raise ValidationError(f"Session is not active: {session_id}")
            
            # Check if question was already answered
            if question_id in session.user_answers:
                raise ValidationError(f"Question {question_id} already answered in session {session_id}")
            
            # Get question details
            question = self.question_service.get_question_by_id(question_id)
            if not question:
                raise ValidationError(f"Invalid question ID: {question_id}")
            
            # Validate answer ( case-insensitive and whitespace trimmed)
            user_answer = answer.strip().lower()
            correct_answer = question.correct_answer.strip().lower()
            is_correct = user_answer == correct_answer
            
            # Record answer with score service
            result = self.score_service.record_answer(
                session_id=session_id,
                question_id=question_id,
                user_answer=answer,
                correct_answer=question.correct_answer,
                is_correct=is_correct
            )
            
            # Update session state
            session.submit_answer(question_id, answer)
            
            self.logger.info(
                f"Answer validated for session {session_id}, question {question_id}, correct: {is_correct}",
                extra={
                    "event_type": "answer_validated",
                    "session_id": session_id,
                    "question_id": question_id,
                    "is_correct": is_correct,
                    "user_answer": answer,
                    "correct_answer": question.correct_answer
                }
            )
            
            return result
            
        except (ValidationError, SessionError):
            raise
        except Exception as e:
            self.logger.error(f"Failed to validate answer: {str(e)}")
            raise SessionError(f"Failed to validate answer: {str(e)}", session_id)
    
    def get_next_question(self, session_id: str) -> Optional[Question]:
        """
        Get next question for session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Next question if available, None if session is complete
        """
        try:
            session = self.get_session(session_id)
            if not session:
                raise SessionError(f"Session not found: {session_id}", session_id)
            
            # Check if session is complete
            if session.is_complete():
                self.logger.info(f"Session {session_id} is complete")
                return None
            
            # Get next question
            exclude_ids = session.questions_asked
            next_question = self.question_service.get_random_question(
                session.topic, 
                session.difficulty, 
                exclude_ids
            )
            
            if next_question:
                # Add to session
                session.add_question(next_question.id)
                
                self.logger.info(
                    f"Retrieved next question {next_question.id} for session {session_id}",
                    extra={
                        "event_type": "next_question_retrieved",
                        "session_id": session_id,
                        "question_id": next_question.id
                    }
                )
            
            return next_question
            
        except SessionError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to get next question: {str(e)}")
            raise SessionError(f"Failed to retrieve next question: {str(e)}", session_id)
    
    def complete_session(self, session_id: str) -> Optional[Score]:
        """
        Complete session and return score.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Final score if session was completed successfully
            
        Raises:
            SessionError: If session operations fail
        """
        try:
            session = self.get_session(session_id)
            if not session:
                raise SessionError(f"Session not found: {session_id}", session_id)
            
            # If session is already completed, just return the existing score
            if not session.is_active:
                score = self.score_service.calculate_score(session_id)
                self.logger.info(
                    f"Session {session_id} was already completed, returning existing score",
                    extra={
                        "event_type": "session_already_completed",
                        "session_id": session_id,
                        "existing_score": score.accuracy_percentage if score else 0
                    }
                )
                return score
            
            # Complete the session
            session.complete_session()
            
            # Calculate score
            score = self.score_service.calculate_score(session_id)
            
            self.logger.info(
                f"Session {session_id} completed with score {score.accuracy_percentage if score else 0}%",
                extra={
                    "event_type": "session_completed",
                    "session_id": session_id,
                    "final_score": score.accuracy_percentage if score else 0
                }
            )
            
            # Remove from active sessions (optional - keep for history)
            # del self._active_sessions[session_id]
            
            return score
            
        except SessionError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to complete session: {str(e)}")
            raise SessionError(f"Failed to complete session: {str(e)}", session_id)
    
    def get_session_score(self, session_id: str) -> Optional[Score]:
        """
        Get current score for an active or completed session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Current score if session exists, None otherwise
            
        Raises:
            SessionError: If session operations fail
        """
        try:
            session = self.get_session(session_id)
            if not session:
                raise SessionError(f"Session not found: {session_id}", session_id)
            
            # Calculate score (doesn't complete the session)
            score = self.score_service.calculate_score(session_id)
            
            self.logger.info(
                f"Retrieved score for session {session_id}: {score.accuracy_percentage if score else 0}%",
                extra={
                    "event_type": "score_retrieved",
                    "session_id": session_id,
                    "accuracy_percentage": score.accuracy_percentage if score else 0
                }
            )
            
            return score
            
        except SessionError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to get session score: {str(e)}")
            raise SessionError(f"Failed to get session score: {str(e)}", session_id)
    
    def _validate_session_parameters(self, topic: str, difficulty: str, total_questions: int) -> None:
        """
        Validate session creation parameters.
        
        Args:
            topic: Session topic
            difficulty: Session difficulty
            total_questions: Number of questions
            
        Raises:
            ValidationError: If parameters are invalid
        """
        # Validate topic
        available_topics = self.question_service.get_available_topics()
        if topic not in available_topics:
            raise ValidationError(f"Invalid topic: {topic}. Available topics: {available_topics}")
        
        # Validate difficulty
        available_difficulties = self.question_service.get_available_difficulties()
        if difficulty not in available_difficulties:
            raise ValidationError(f"Invalid difficulty: {difficulty}. Available difficulties: {available_difficulties}")
        
        # Validate total questions
        if not isinstance(total_questions, int) or total_questions <= 0:
            raise ValidationError("Total questions must be a positive integer")
        
        if total_questions > 50:
            raise ValidationError("Total questions cannot exceed 50")
    
    def get_active_sessions(self) -> List[UserSession]:
        """
        Get list of all active sessions.
        
        Returns:
            List of active sessions
        """
        return [session for session in self._active_sessions.values() if session.is_active]
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about all sessions.
        
        Returns:
            Dictionary containing session statistics
        """
        active_sessions = self.get_active_sessions()
        completed_sessions = [s for s in self._active_sessions.values() if not s.is_active]
        
        return {
            "total_sessions": len(self._active_sessions),
            "active_sessions": len(active_sessions),
            "completed_sessions": len(completed_sessions),
            "topics": list(set(s.topic for s in self._active_sessions.values())),
            "difficulties": list(set(s.difficulty for s in self._active_sessions.values()))
        }
