"""
CLI Commands Module for Q&A Practice Application.

This module implements all CLI commands including topic/difficulty selection,
question presentation, answer validation, session summary, and error handling.
"""

import sys
import os
from typing import Optional, List, Dict, Any
from pathlib import Path
import logging

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.question_service import QuestionService
from src.services.session_service import SessionService
from src.services.score_service import ScoreService
from src.services.csv_parser import CSVParserService
from src.models.question import Question
from src.models.session import UserSession
from src.models.score import Score
from src.models.question_review import QuestionReview, QuestionReviewList
from src.utils.config import AppConfig
from src.utils.exceptions import ValidationError, QuestionError, SessionError


class CLICommands:
    """
    Command-line interface commands for Q&A Practice Application.
    
    This class provides all the functionality needed for the CLI interface,
    including user interaction, session management, and error handling.
    """
    
    def __init__(self, config: AppConfig):
        """
        Initialize CLI commands with configuration and services.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize services
        self.csv_parser = CSVParserService()
        self.question_service = QuestionService()
        self.session_service = SessionService()
        self.score_service = ScoreService()
        
        # Load questions from CSV
        self._load_questions()
        
        # Available options
        self.available_topics = ["Physics", "Chemistry", "Math"]
        self.available_difficulties = ["Easy", "Medium", "Hard"]
    
    def _load_questions(self) -> None:
        """Load questions from CSV file."""
        try:
            data_file = self.config.get('data_file', 'question-bank.csv')
            
            # Check if file exists
            if not os.path.exists(data_file):
                # Try relative path from project root
                project_root = Path(__file__).parent.parent.parent
                data_file = project_root / data_file
                
                if not os.path.exists(data_file):
                    raise FileNotFoundError(f"Question data file not found: {data_file}")
            
            # Load questions
            questions = self.csv_parser.load_questions_from_csv(str(data_file))
            self.question_service.load_questions(questions)
            
            self.logger.info(f"Loaded {len(questions)} questions from {data_file}")
            
        except Exception as e:
            raise QuestionError(f"Failed to load questions: {str(e)}")
    
    def list_topics(self) -> None:
        """Display available topics."""
        print("\n📚 Available Topics:")
        print("=" * 30)
        
        for i, topic in enumerate(self.available_topics, 1):
            # Get question count for each topic
            questions = self.question_service.get_questions_by_topic(topic)
            print(f"  {i}. {topic} ({len(questions)} questions)")
        
        print()
    
    def list_difficulties(self) -> None:
        """Display available difficulty levels."""
        print("\n🎯 Available Difficulty Levels:")
        print("=" * 35)
        
        difficulty_descriptions = {
            "Easy": "Basic concepts and straightforward problems",
            "Medium": "Intermediate concepts and moderate complexity",
            "Hard": "Advanced concepts and challenging problems"
        }
        
        for i, difficulty in enumerate(self.available_difficulties, 1):
            # Get question count for each difficulty
            questions = self.question_service.get_questions_by_difficulty(difficulty)
            description = difficulty_descriptions.get(difficulty, "")
            print(f"  {i}. {difficulty} ({len(questions)} questions)")
            print(f"     {description}")
        
        print()
    
    def show_statistics(self) -> None:
        """Display application statistics."""
        print("\n📊 Application Statistics:")
        print("=" * 35)
        
        all_questions = self.question_service.get_all_questions()
        
        # Total questions
        print(f"Total Questions: {len(all_questions)}")
        
        # Questions by topic
        print("\nQuestions by Topic:")
        for topic in self.available_topics:
            count = len(self.question_service.get_questions_by_topic(topic))
            print(f"  {topic}: {count}")
        
        # Questions by difficulty
        print("\nQuestions by Difficulty:")
        for difficulty in self.available_difficulties:
            count = len(self.question_service.get_questions_by_difficulty(difficulty))
            print(f"  {difficulty}: {count}")
        
        # Topic-Difficulty matrix
        print("\nTopic-Difficulty Matrix:")
        print("   " + " | ".join(f"{d:>6}" for d in self.available_difficulties))
        print("   " + "+".join("-" * 7 for _ in self.available_difficulties))
        
        for topic in self.available_topics:
            row = f"{topic:>8} |"
            for difficulty in self.available_difficulties:
                questions = self.question_service.get_questions_by_topic_and_difficulty(topic, difficulty)
                row += f" {len(questions):>5} |"
            print(row)
        
        print()
    
    def interactive_session(self) -> None:
        """Start an interactive practice session with user prompts."""
        print("\n🚀 Starting Interactive Practice Session")
        print("=" * 45)
        
        # Get topic selection
        topic = self._prompt_topic_selection()
        
        # Get difficulty selection
        difficulty = self._prompt_difficulty_selection()
        
        # Start session with selected parameters
        self.start_session(topic=topic, difficulty=difficulty)
    
    def _prompt_topic_selection(self) -> str:
        """
        Prompt user to select a topic.
        
        Returns:
            Selected topic
        """
        print("\n📚 Select a Topic:")
        print("-" * 20)
        
        for i, topic in enumerate(self.available_topics, 1):
            questions = self.question_service.get_questions_by_topic(topic)
            print(f"  {i}. {topic} ({len(questions)} questions)")
        
        while True:
            try:
                choice = input(f"\nEnter topic number (1-{len(self.available_topics)}) or 'quit': ").strip()
                
                if choice.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    sys.exit(0)
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(self.available_topics):
                    selected_topic = self.available_topics[choice_num - 1]
                    print(f"\n✅ Selected topic: {selected_topic}")
                    return selected_topic
                else:
                    print(f"❌ Please enter a number between 1 and {len(self.available_topics)}")
            
            except ValueError:
                print("❌ Please enter a valid number")
            except KeyboardInterrupt:
                print("\n\n👋 Session cancelled. Goodbye!")
                sys.exit(130)
    
    def _prompt_difficulty_selection(self) -> str:
        """
        Prompt user to select a difficulty level.
        
        Returns:
            Selected difficulty
        """
        print("\n🎯 Select Difficulty Level:")
        print("-" * 25)
        
        difficulty_descriptions = {
            "Easy": "Basic concepts and straightforward problems",
            "Medium": "Intermediate concepts and moderate complexity", 
            "Hard": "Advanced concepts and challenging problems"
        }
        
        for i, difficulty in enumerate(self.available_difficulties, 1):
            description = difficulty_descriptions.get(difficulty, "")
            print(f"  {i}. {difficulty}")
            print(f"     {description}")
        
        while True:
            try:
                choice = input(f"\nEnter difficulty number (1-{len(self.available_difficulties)}) or 'quit': ").strip()
                
                if choice.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    sys.exit(0)
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(self.available_difficulties):
                    selected_difficulty = self.available_difficulties[choice_num - 1]
                    print(f"\n✅ Selected difficulty: {selected_difficulty}")
                    return selected_difficulty
                else:
                    print(f"❌ Please enter a number between 1 and {len(self.available_difficulties)}")
            
            except ValueError:
                print("❌ Please enter a valid number")
            except KeyboardInterrupt:
                print("\n\n👋 Session cancelled. Goodbye!")
                sys.exit(130)
    
    def start_session(self, topic: Optional[str] = None, difficulty: Optional[str] = None) -> None:
        """
        Start a practice session with specified parameters.
        
        Args:
            topic: Selected topic (None to prompt)
            difficulty: Selected difficulty (None to prompt)
        """
        try:
            # Prompt for missing parameters
            if not topic:
                topic = self._prompt_topic_selection()
            
            if not difficulty:
                difficulty = self._prompt_difficulty_selection()
            
            # Validate parameters
            if topic not in self.available_topics:
                raise ValidationError(f"Invalid topic: {topic}")
            
            if difficulty not in self.available_difficulties:
                raise ValidationError(f"Invalid difficulty: {difficulty}")
            
            # Get available questions
            questions = self.question_service.get_questions_by_topic_and_difficulty(topic, difficulty)
            
            if not questions:
                print(f"\n❌ No questions available for {topic} - {difficulty}")
                return
            
            print(f"\n🎯 Starting {topic} - {difficulty} Practice Session")
            print(f"📝 Available questions: {len(questions)}")
            print("=" * 50)
            
            # Create session
            session = self.session_service.create_session(topic, difficulty)
            
            # Run the practice session
            self._run_practice_session(session, questions)
            
        except (ValidationError, SessionError) as e:
            print(f"\n❌ Session error: {e}")
        except KeyboardInterrupt:
            print("\n\n👋 Session cancelled by user. Goodbye!")
            sys.exit(130)
    
    def _run_practice_session(self, session: UserSession, questions: List[Question]) -> None:
        """
        Run the main practice session loop.
        
        Args:
            session: User session object
            questions: Available questions for the session
        """
        total_questions = min(10, len(questions))  # Limit to 10 questions per session
        asked_questions = 0
        correct_answers = 0
        
        # Track question reviews for session summary (User Story 5)
        question_reviews = QuestionReviewList()
        
        print(f"\nAnswering {total_questions} questions. Type 'quit' to exit.\n")
        
        for i in range(total_questions):
            try:
                # Get next random question
                question = self.question_service.get_random_question(
                    session.topic, session.difficulty, exclude_asked=True
                )
                
                if not question:
                    print("No more questions available.")
                    break
                
                # Present question
                self._present_question(question, i + 1, total_questions)
                
                # Collect and validate answer
                user_answer = self._collect_answer(question)
                
                if user_answer is None:  # User quit
                    break
                
                # Check answer and provide feedback
                is_correct, user_answer_text = self._validate_and_provide_feedback(question, user_answer)
                
                # Track question review (User Story 5)
                review = QuestionReview(
                    question_number=i + 1,
                    question_text=question.question_text,
                    user_answer=user_answer_text,
                    correct_answer=question.correct_answer,
                    correct=is_correct,
                    topic=question.topic,
                    difficulty=question.difficulty
                )
                question_reviews.add(review)
                
                # Update session
                self.session_service.record_answer(session, question.id, is_correct)
                
                asked_questions += 1
                if is_correct:
                    correct_answers += 1
                
                print("-" * 50)
                
            except (QuestionError, ValidationError) as e:
                print(f"❌ Error: {e}")
                continue
            except KeyboardInterrupt:
                print("\n\n👋 Session cancelled by user.")
                break
        
        # Show session summary with question reviews
        self._show_session_summary(session, asked_questions, correct_answers, question_reviews)
    
    def _present_question(self, question: Question, question_num: int, total: int) -> None:
        """
        Present a question to the user in CLI format.
        
        Args:
            question: Question to present
            question_num: Current question number
            total: Total number of questions
        """
        print(f"📝 Question {question_num} of {total}")
        print(f"🏷️  Topic: {question.topic} | 🎯 Difficulty: {question.difficulty}")
        print()
        print(f"Q: {question.question_text}")
        print()
        
        # Display options
        options = [
            ("A", question.option1),
            ("B", question.option2),
            ("C", question.option3),
            ("D", question.option4)
        ]
        
        for label, option in options:
            if option:  # Only show non-None options
                print(f"   {label}) {option}")
        
        print()
    
    def _collect_answer(self, question: Question) -> Optional[str]:
        """
        Collect user's answer with validation.
        
        Args:
            question: Current question
            
        Returns:
            User's answer or None if user quit
        """
        while True:
            try:
                answer = input("Your answer (A/B/C/D) or 'quit': ").strip().upper()
                
                if answer in ['QUIT', 'EXIT', 'Q']:
                    return None
                
                if answer in ['A', 'B', 'C', 'D']:
                    return answer
                
                print("❌ Please enter A, B, C, or D")
                
            except KeyboardInterrupt:
                return None
    
    def _validate_and_provide_feedback(self, question: Question, user_answer: str) -> tuple:
        """
        Validate answer and provide immediate feedback.
        
        Args:
            question: Current question
            user_answer: User's answer (A/B/C/D)
            
        Returns:
            Tuple of (is_correct: bool, user_answer_text: str)
        """
        # Map answer letter to option text
        answer_map = {
            'A': question.option1,
            'B': question.option2,
            'C': question.option3,
            'D': question.option4
        }
        
        selected_option = answer_map.get(user_answer, "")
        is_correct = question.validate_answer(selected_option)
        
        if is_correct:
            print("✅ Correct! Well done!")
        else:
            print(f"❌ Incorrect. The correct answer is: {question.correct_answer}")
            print(f"   You selected: {selected_option}")
        
        # Provide additional feedback based on difficulty
        if question.difficulty == "Easy" and not is_correct:
            print("💡 Hint: Review the basic concepts for this topic.")
        elif question.difficulty == "Hard" and is_correct:
            print("🌟 Excellent! That was a challenging question.")
        
        print()
        return is_correct, selected_option
    
    def _show_session_summary(
        self, 
        session: UserSession, 
        asked: int, 
        correct: int,
        question_reviews: Optional[QuestionReviewList] = None
    ) -> None:
        """
        Display session summary with statistics and question review.
        
        Args:
            session: User session
            asked: Number of questions asked
            correct: Number of correct answers
            question_reviews: Optional list of question reviews (User Story 5)
        """
        if asked == 0:
            print("\n📊 Session Summary")
            print("=" * 20)
            print("No questions were answered.")
            return
        
        accuracy = (correct / asked) * 100
        
        print(f"\n📊 Session Summary")
        print("=" * 40)
        print(f"Topic: {session.topic}")
        print(f"Difficulty: {session.difficulty}")
        print(f"Questions Answered: {asked}")
        print(f"Correct Answers: {correct}")
        print(f"Accuracy: {accuracy:.1f}%")
        
        # Performance feedback
        if accuracy >= 90:
            print("🌟 Outstanding performance!")
        elif accuracy >= 75:
            print("👍 Great job!")
        elif accuracy >= 60:
            print("📈 Good effort! Keep practicing.")
        else:
            print("💪 Keep practicing! Review the concepts and try again.")
        
        # Question Review Section (User Story 5)
        if question_reviews and question_reviews.total_count > 0:
            print(f"\n📝 Question Review")
            print("=" * 40)
            
            if question_reviews.is_perfect_score():
                # Perfect score - show congratulations
                print("\n🎉 PERFECT SCORE! 🎉")
                print("Congratulations! You answered all questions correctly!")
                print("No wrong answers to review - you've mastered this topic!")
            else:
                # Show question-by-question breakdown
                print(f"\nReviewing {question_reviews.incorrect_count} incorrect answer(s):\n")
                
                for review in question_reviews.get_incorrect():
                    print(f"  Q{review.question_number}: {review.question_text[:60]}...")
                    print(f"     ❌ Your answer: {review.user_answer}")
                    print(f"     ✅ Correct answer: {review.correct_answer}")
                    print()
        
        print(f"\nSession ID: {session.session_id}")
        print("Thank you for using Q&A Practice Application! 🎯")
        print()
