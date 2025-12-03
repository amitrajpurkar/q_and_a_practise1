"""
Score service implementation for Q&A Practice Application.

Implements business logic for score calculation following SOLID principles.
"""

from typing import List, Optional, Dict, Any
import logging

from src.models.score import Score
from src.models.session import UserSession
from src.models.question import Question
from src.services.interfaces import IScoreService, ISessionService, IQuestionService
from src.utils.exceptions import ScoreError, SessionError


class ScoreService(IScoreService):
    """
    Business logic service for score operations.
    
    Follows Single Responsibility principle by handling
    only score-related business logic.
    """
    
    def __init__(self, 
                 session_service: ISessionService,
                 question_service: IQuestionService,
                 logger: Optional[logging.Logger] = None) -> None:
        """
        Initialize score service.
        
        Args:
            session_service: Service for session operations
            question_service: Service for question operations
            logger: Optional logger instance
        """
        self.session_service = session_service
        self.question_service = question_service
        self.logger = logger or logging.getLogger(__name__)
        self._scores: Dict[str, Score] = {}
    
    def calculate_score(self, session_id: str) -> Optional[Score]:
        """
        Calculate final score for session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Calculated score if session exists, None otherwise
            
        Raises:
            ScoreError: If score calculation fails
        """
        try:
            session = self.session_service.get_session(session_id)
            if not session:
                self.logger.warning(f"Cannot calculate score for non-existent session: {session_id}")
                return None
            
            # Count correct and incorrect answers
            correct_answers = 0
            incorrect_answers = 0
            topic_performance = {}
            
            for question_id, user_answer in session.user_answers.items():
                question = self.question_service.get_question_by_id(question_id)
                if not question:
                    self.logger.warning(f"Question {question_id} not found for score calculation")
                    continue
                
                # Check if answer is correct
                is_correct = question.is_correct_answer(user_answer)
                
                if is_correct:
                    correct_answers += 1
                else:
                    incorrect_answers += 1
                
                # Update topic performance
                topic = question.topic
                if topic not in topic_performance:
                    topic_performance[topic] = {'correct': 0, 'total': 0}
                topic_performance[topic]['total'] += 1
                if is_correct:
                    topic_performance[topic]['correct'] += 1
            
            # Calculate time taken
            time_taken = session.get_session_duration()
            
            # Create score
            score = Score.from_session_results(
                session_id=session_id,
                total_questions=session.total_questions,
                correct_answers=correct_answers,
                incorrect_answers=incorrect_answers,
                time_taken_seconds=time_taken,
                topic_performance=topic_performance
            )
            
            # Store score
            self._scores[session_id] = score
            
            self.logger.info(
                f"Calculated score for session {session_id}: {score.accuracy_percentage}% accuracy",
                extra={
                    "event_type": "score_calculated",
                    "session_id": session_id,
                    "accuracy_percentage": score.accuracy_percentage,
                    "correct_answers": correct_answers,
                    "total_answered": correct_answers + incorrect_answers
                }
            )
            
            return score
            
        except (SessionError, ScoreError):
            raise
        except Exception as e:
            self.logger.error(f"Failed to calculate score for session {session_id}: {str(e)}")
            raise ScoreError(f"Failed to calculate score: {str(e)}", session_id)
    
    def get_current_score(self, session_id: str) -> Optional[Score]:
        """
        Get current session score.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Current score if available, None otherwise
        """
        try:
            # Check if we have a cached score
            if session_id in self._scores:
                return self._scores[session_id]
            
            # Calculate current score
            return self.calculate_score(session_id)
            
        except Exception as e:
            self.logger.error(f"Failed to get current score for session {session_id}: {str(e)}")
            raise ScoreError(f"Failed to retrieve current score: {str(e)}", session_id)
    
    def generate_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Generate session performance summary.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Performance summary dictionary
            
        Raises:
            ScoreError: If summary generation fails
        """
        try:
            score = self.get_current_score(session_id)
            if not score:
                raise ScoreError(f"No score available for session: {session_id}", session_id)
            
            session = self.session_service.get_session(session_id)
            if not session:
                raise ScoreError(f"Session not found: {session_id}", session_id)
            
            # Generate detailed summary
            summary = {
                "session_info": {
                    "session_id": session_id,
                    "topic": session.topic,
                    "difficulty": session.difficulty,
                    "total_questions": session.total_questions,
                    "duration_seconds": session.get_session_duration(),
                    "duration_formatted": score._format_time(session.get_session_duration()),
                    "completed_at": session.end_time
                },
                "performance": {
                    "total_questions": score.total_questions,
                    "questions_answered": score.correct_answers + score.incorrect_answers,
                    "correct_answers": score.correct_answers,
                    "incorrect_answers": score.incorrect_answers,
                    "accuracy_percentage": score.accuracy_percentage,
                    "performance_grade": score._get_performance_grade(),
                    "questions_per_minute": score._get_questions_per_minute()
                },
                "topic_breakdown": score.topic_performance,
                "recommendations": self._generate_recommendations(score)
            }
            
            self.logger.info(
                f"Generated performance summary for session {session_id}",
                extra={
                    "event_type": "summary_generated",
                    "session_id": session_id,
                    "accuracy": score.accuracy_percentage
                }
            )
            
            return summary
            
        except (ScoreError, SessionError):
            raise
        except Exception as e:
            self.logger.error(f"Failed to generate summary for session {session_id}: {str(e)}")
            raise ScoreError(f"Failed to generate summary: {str(e)}", session_id)
    
    def _generate_recommendations(self, score: Score) -> List[str]:
        """
        Generate performance recommendations based on score.
        
        Args:
            score: Score object
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Accuracy-based recommendations
        if score.accuracy_percentage >= 90:
            recommendations.append("Excellent performance! Consider trying harder difficulty levels.")
        elif score.accuracy_percentage >= 70:
            recommendations.append("Good performance! Review incorrect answers and practice similar questions.")
        elif score.accuracy_percentage >= 50:
            recommendations.append("Fair performance. Focus on understanding fundamental concepts.")
        else:
            recommendations.append("Keep practicing! Consider reviewing study materials for this topic.")
        
        # Speed-based recommendations
        qpm = score._get_questions_per_minute()
        if qpm < 1:
            recommendations.append("Try to answer questions more quickly with practice.")
        elif qpm > 5:
            recommendations.append("Great speed! Make sure you're not rushing through questions.")
        
        # Topic-specific recommendations
        for topic, performance in score.topic_performance.items():
            if performance['total'] > 0:
                topic_accuracy = (performance['correct'] / performance['total']) * 100
                if topic_accuracy < 60:
                    recommendations.append(f"Consider reviewing {topic} concepts for better understanding.")
        
        return recommendations
    
    def get_all_scores(self) -> List[Score]:
        """
        Get all calculated scores.
        
        Returns:
            List of all scores
        """
        return list(self._scores.values())
    
    def get_scores_by_topic(self, topic: str) -> List[Score]:
        """
        Get scores for a specific topic.
        
        Args:
            topic: Topic to filter by
            
        Returns:
            List of scores for the topic
        """
        return [score for score in self._scores.values() if topic in score.topic_performance]
    
    def get_average_accuracy(self, topic: Optional[str] = None) -> float:
        """
        Get average accuracy across all scores or specific topic.
        
        Args:
            topic: Optional topic to filter by
            
        Returns:
            Average accuracy percentage
        """
        scores = self.get_scores_by_topic(topic) if topic else self.get_all_scores()
        
        if not scores:
            return 0.0
        
        total_accuracy = sum(score.accuracy_percentage for score in scores)
        return round(total_accuracy / len(scores), 2)
    
    def clear_scores(self) -> None:
        """Clear all cached scores."""
        self._scores.clear()
        self.logger.info("Cleared all cached scores")
    
    def delete_score(self, session_id: str) -> bool:
        """
        Delete score for specific session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if score was deleted, False if not found
        """
        if session_id in self._scores:
            del self._scores[session_id]
            self.logger.info(f"Deleted score for session {session_id}")
            return True
        return False
