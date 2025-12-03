"""
Score service implementation for Q&A Practice Application.

Implements business logic for score calculation following SOLID principles.
"""

from typing import List, Optional, Dict, Any
import logging

from src.models.score import Score, AnswerResult
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
    
    def record_answer(self, session_id: str, question_id: str, user_answer: str, correct_answer: str, is_correct: bool) -> AnswerResult:
        """
        Record an answer and return validation result.
        
        Args:
            session_id: Session identifier
            question_id: Question ID
            user_answer: User's submitted answer
            correct_answer: The correct answer
            is_correct: Whether the answer is correct
            
        Returns:
            AnswerResult with validation details
            
        Raises:
            ScoreError: If recording fails
        """
        try:
            # Generate explanation for incorrect answers (simple implementation)
            explanation = None
            if not is_correct:
                explanation = f"The correct answer is: {correct_answer}"
            
            result = AnswerResult(
                question_id=question_id,
                correct=is_correct,
                answer_text=user_answer,
                correct_answer=correct_answer,
                explanation=explanation,
                time_taken_seconds=0  # Could be enhanced to track actual time
            )
            
            self.logger.info(
                f"Answer recorded for session {session_id}, question {question_id}, correct: {is_correct}",
                extra={
                    "event_type": "answer_recorded",
                    "session_id": session_id,
                    "question_id": question_id,
                    "is_correct": is_correct
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to record answer: {str(e)}")
            raise ScoreError(f"Failed to record answer: {str(e)}")
    
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
            current_streak = 0
            best_streak = 0
            
            for question_id, user_answer in session.user_answers.items():
                question = self.question_service.get_question_by_id(question_id)
                if not question:
                    self.logger.warning(f"Question {question_id} not found for score calculation")
                    continue
                
                # Check if answer is correct
                is_correct = question.is_correct_answer(user_answer)
                
                if is_correct:
                    correct_answers += 1
                    current_streak += 1
                    best_streak = max(best_streak, current_streak)
                else:
                    incorrect_answers += 1
                    current_streak = 0
                
                # Update topic performance by difficulty
                topic = question.topic
                difficulty = question.difficulty
                
                if topic not in topic_performance:
                    topic_performance[topic] = {}
                if difficulty not in topic_performance[topic]:
                    topic_performance[topic][difficulty] = {'correct': 0, 'incorrect': 0, 'total': 0}
                
                topic_performance[topic][difficulty]['total'] += 1
                if is_correct:
                    topic_performance[topic][difficulty]['correct'] += 1
                else:
                    topic_performance[topic][difficulty]['incorrect'] += 1
            
            # Calculate time taken
            time_taken = session.get_session_duration()
            
            # Create streak data
            streak_data = {
                "current": current_streak,
                "best": best_streak
            }
            
            # Create score
            score = Score(
                session_id=session_id,
                total_questions=correct_answers + incorrect_answers,
                correct_answers=correct_answers,
                incorrect_answers=incorrect_answers,
                time_taken_seconds=time_taken,
                topic_performance=topic_performance,
                streak_data=streak_data
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

    # User-defined methods with return values for calculations
    def calculate_performance_metrics(self, session_id: str) -> Dict[str, float]:
        """
        Calculate detailed performance metrics for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with calculated performance metrics
        """
        score = self.get_score(session_id)
        if not score:
            return {
                'accuracy': 0.0,
                'speed_score': 0.0,
                'consistency_score': 0.0,
                'overall_performance': 0.0
            }
        
        # Calculate accuracy (already available)
        accuracy = score.accuracy_percentage
        
        # Calculate speed score based on time per question
        if score.total_questions > 0:
            time_per_question = score.time_taken_seconds / score.total_questions
            # Optimal time is 30 seconds per question
            speed_score = max(0.0, 100.0 - (time_per_question - 30) * 2)
            speed_score = min(100.0, speed_score)
        else:
            speed_score = 0.0
        
        # Calculate consistency score based on topic performance variance
        if score.topic_performance:
            topic_accuracies = []
            for topic_data in score.topic_performance.values():
                for difficulty_data in topic_data.values():
                    if difficulty_data.get('total', 0) > 0:
                        topic_accuracy = (difficulty_data['correct'] / difficulty_data['total']) * 100
                        topic_accuracies.append(topic_accuracy)
            
            if topic_accuracies:
                avg_accuracy = sum(topic_accuracies) / len(topic_accuracies)
                variance = sum((x - avg_accuracy) ** 2 for x in topic_accuracies) / len(topic_accuracies)
                consistency_score = max(0.0, 100.0 - variance * 2)
            else:
                consistency_score = 0.0
        else:
            consistency_score = 0.0
        
        # Calculate overall performance (weighted average)
        overall_performance = (accuracy * 0.5 + speed_score * 0.3 + consistency_score * 0.2)
        
        return {
            'accuracy': round(accuracy, 2),
            'speed_score': round(speed_score, 2),
            'consistency_score': round(consistency_score, 2),
            'overall_performance': round(overall_performance, 2)
        }

    def calculate_learning_progress(self, user_sessions: List[str]) -> Dict[str, Any]:
        """
        Calculate learning progress across multiple sessions.
        
        Args:
            user_sessions: List of session IDs for the user
            
        Returns:
            Dictionary with learning progress analytics
        """
        if not user_sessions:
            return {
                'total_sessions': 0,
                'improvement_rate': 0.0,
                'strongest_topics': [],
                'weakest_topics': [],
                'learning_trend': 'stable'
            }
        
        session_scores = []
        topic_performance = {}
        
        # Collect data from all sessions
        for session_id in user_sessions:
            score = self.get_score(session_id)
            if score:
                session_scores.append(score.accuracy_percentage)
                
                # Aggregate topic performance
                for topic, difficulties in score.topic_performance.items():
                    if topic not in topic_performance:
                        topic_performance[topic] = {'correct': 0, 'total': 0}
                    
                    for difficulty, stats in difficulties.items():
                        topic_performance[topic]['correct'] += stats['correct']
                        topic_performance[topic]['total'] += stats['total']
        
        # Calculate improvement rate
        if len(session_scores) > 1:
            recent_avg = sum(session_scores[-3:]) / min(3, len(session_scores))
            early_avg = sum(session_scores[:3:]) / min(3, len(session_scores))
            improvement_rate = recent_avg - early_avg
        else:
            improvement_rate = 0.0
        
        # Determine strongest and weakest topics
        topic_accuracies = []
        for topic, stats in topic_performance.items():
            if stats['total'] > 0:
                accuracy = (stats['correct'] / stats['total']) * 100
                topic_accuracies.append((topic, accuracy))
        
        topic_accuracies.sort(key=lambda x: x[1], reverse=True)
        
        strongest_topics = [topic for topic, _ in topic_accuracies[:3]]
        weakest_topics = [topic for topic, _ in topic_accuracies[-3:]]
        
        # Determine learning trend
        if len(session_scores) >= 5:
            recent_slope = (session_scores[-1] - session_scores[-5]) / 5
            if recent_slope > 5:
                learning_trend = 'improving'
            elif recent_slope < -5:
                learning_trend = 'declining'
            else:
                learning_trend = 'stable'
        else:
            learning_trend = 'insufficient_data'
        
        return {
            'total_sessions': len(session_scores),
            'improvement_rate': round(improvement_rate, 2),
            'strongest_topics': strongest_topics,
            'weakest_topics': weakest_topics,
            'learning_trend': learning_trend,
            'average_accuracy': round(sum(session_scores) / len(session_scores), 2) if session_scores else 0.0
        }

    def calculate_difficulty_progression(self, session_id: str) -> Dict[str, List[float]]:
        """
        Calculate performance progression by difficulty level.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with difficulty-specific performance data
        """
        score = self.get_score(session_id)
        if not score or not score.topic_performance:
            return {
                'easy_progression': [],
                'medium_progression': [],
                'hard_progression': []
            }
        
        difficulty_data = {
            'easy_progression': [],
            'medium_progression': [],
            'hard_progression': []
        }
        
        # Extract performance by difficulty across topics
        for topic, difficulties in score.topic_performance.items():
            for difficulty, stats in difficulties.items():
                if stats['total'] > 0:
                    accuracy = (stats['correct'] / stats['total']) * 100
                    
                    if difficulty.lower() == 'easy':
                        difficulty_data['easy_progression'].append(accuracy)
                    elif difficulty.lower() == 'medium':
                        difficulty_data['medium_progression'].append(accuracy)
                    elif difficulty.lower() == 'hard':
                        difficulty_data['hard_progression'].append(accuracy)
        
        # Calculate averages for each difficulty
        for key in difficulty_data:
            if difficulty_data[key]:
                avg_accuracy = sum(difficulty_data[key]) / len(difficulty_data[key])
                difficulty_data[key] = [round(avg_accuracy, 2)]
            else:
                difficulty_data[key] = [0.0]
        
        return difficulty_data

    def calculate_time_analysis(self, session_id: str) -> Dict[str, Any]:
        """
        Calculate time-based performance analysis.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with time analysis metrics
        """
        score = self.get_score(session_id)
        if not score:
            return {
                'total_time': 0,
                'average_time_per_question': 0.0,
                'time_efficiency': 0.0,
                'pacing_analysis': 'no_data'
            }
        
        total_time = score.time_taken_seconds
        
        if score.total_questions > 0:
            avg_time_per_question = total_time / score.total_questions
            
            # Time efficiency: optimal is 30 seconds per question
            optimal_time_per_question = 30.0
            time_efficiency = max(0.0, 100.0 - abs(avg_time_per_question - optimal_time_per_question) * 2)
            
            # Pacing analysis
            if avg_time_per_question < 20:
                pacing_analysis = 'too_fast'
            elif avg_time_per_question > 60:
                pacing_analysis = 'too_slow'
            else:
                pacing_analysis = 'optimal'
        else:
            avg_time_per_question = 0.0
            time_efficiency = 0.0
            pacing_analysis = 'no_data'
        
        return {
            'total_time': total_time,
            'average_time_per_question': round(avg_time_per_question, 2),
            'time_efficiency': round(time_efficiency, 2),
            'pacing_analysis': pacing_analysis
        }

    def generate_score_summary(self, session_id: str) -> str:
        """
        Generate a textual summary of the score.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Formatted string summary of performance
        """
        score = self.get_score(session_id)
        if not score:
            return "No score data available for this session."
        
        # Get various metrics
        performance = self.calculate_performance_metrics(session_id)
        time_analysis = self.calculate_time_analysis(session_id)
        
        # Build summary
        summary_parts = []
        
        # Basic performance
        summary_parts.append(f"Accuracy: {performance['accuracy']:.1f}%")
        summary_parts.append(f"Overall Performance: {performance['overall_performance']:.1f}%")
        
        # Time analysis
        summary_parts.append(f"Average Time per Question: {time_analysis['average_time_per_question']:.1f} seconds")
        summary_parts.append(f"Pacing: {time_analysis['pacing_analysis'].replace('_', ' ').title()}")
        
        # Topic performance highlights
        if score.topic_performance:
            best_topic = None
            best_accuracy = 0.0
            
            for topic, difficulties in score.topic_performance.items():
                total_correct = sum(stats['correct'] for stats in difficulties.values())
                total_questions = sum(stats['total'] for stats in difficulties.values())
                
                if total_questions > 0:
                    topic_accuracy = (total_correct / total_questions) * 100
                    if topic_accuracy > best_accuracy:
                        best_accuracy = topic_accuracy
                        best_topic = topic
            
            if best_topic:
                summary_parts.append(f"Strongest Topic: {best_topic} ({best_accuracy:.1f}%)")
        
        return " | ".join(summary_parts)
