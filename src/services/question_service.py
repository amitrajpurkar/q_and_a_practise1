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

    # Searching algorithms implementation
    def linear_search_questions(self, search_text: str) -> List[Question]:
        """
        Search questions using linear search algorithm.
        
        Args:
            search_text: Text to search for in question text
            
        Returns:
            List of questions containing the search text
        """
        try:
            all_questions = self.question_repository.get_all()
            search_text_lower = search_text.lower()
            
            # Linear search through all questions
            matching_questions = []
            for question in all_questions:
                if search_text_lower in question.question_text.lower():
                    matching_questions.append(question)
            
            self.logger.info(f"Linear search found {len(matching_questions)} questions for '{search_text}'")
            return matching_questions
            
        except Exception as e:
            self.logger.error(f"Failed to perform linear search: {str(e)}")
            raise QuestionError(f"Failed to search questions: {str(e)}")

    def binary_search_question_by_id(self, question_id: str) -> Optional[Question]:
        """
        Search question by ID using binary search algorithm.
        
        Args:
            question_id: ID to search for
            
        Returns:
            Question if found, None otherwise
        """
        try:
            all_questions = self.question_repository.get_all()
            
            # Sort questions by ID for binary search
            sorted_questions = sorted(all_questions, key=lambda q: q.id)
            
            # Binary search implementation
            left, right = 0, len(sorted_questions) - 1
            
            while left <= right:
                mid = (left + right) // 2
                mid_question = sorted_questions[mid]
                
                if mid_question.id == question_id:
                    self.logger.info(f"Binary search found question {question_id}")
                    return mid_question
                elif mid_question.id < question_id:
                    left = mid + 1
                else:
                    right = mid - 1
            
            self.logger.info(f"Binary search: Question {question_id} not found")
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to perform binary search: {str(e)}")
            raise QuestionError(f"Failed to search question by ID: {str(e)}")

    def search_questions_by_pattern(self, pattern: str) -> List[Question]:
        """
        Search questions using pattern matching.
        
        Args:
            pattern: Pattern to search for (supports wildcards)
            
        Returns:
            List of questions matching the pattern
        """
        try:
            import re
            all_questions = self.question_repository.get_all()
            
            # Convert wildcard pattern to regex
            regex_pattern = pattern.replace('*', '.*').replace('?', '.')
            compiled_pattern = re.compile(regex_pattern, re.IGNORECASE)
            
            matching_questions = []
            for question in all_questions:
                if compiled_pattern.search(question.question_text):
                    matching_questions.append(question)
            
            self.logger.info(f"Pattern search found {len(matching_questions)} questions for pattern '{pattern}'")
            return matching_questions
            
        except Exception as e:
            self.logger.error(f"Failed to perform pattern search: {str(e)}")
            raise QuestionError(f"Failed to search questions by pattern: {str(e)}")

    def fuzzy_search_questions(self, search_text: str, threshold: float = 0.6) -> List[Question]:
        """
        Search questions using fuzzy matching.
        
        Args:
            search_text: Text to search for
            threshold: Similarity threshold (0.0 to 1.0)
            
        Returns:
            List of questions with similarity above threshold
        """
        try:
            from difflib import SequenceMatcher
            all_questions = self.question_repository.get_all()
            
            matching_questions = []
            for question in all_questions:
                similarity = SequenceMatcher(None, search_text.lower(), question.question_text.lower()).ratio()
                if similarity >= threshold:
                    matching_questions.append(question)
            
            # Sort by similarity (highest first)
            matching_questions.sort(key=lambda q: SequenceMatcher(None, search_text.lower(), q.question_text.lower()).ratio(), reverse=True)
            
            self.logger.info(f"Fuzzy search found {len(matching_questions)} questions for '{search_text}' with threshold {threshold}")
            return matching_questions
            
        except Exception as e:
            self.logger.error(f"Failed to perform fuzzy search: {str(e)}")
            raise QuestionError(f"Failed to perform fuzzy search: {str(e)}")

    def search_questions_with_filters(self, search_text: Optional[str] = None, 
                                    topic: Optional[str] = None, 
                                    difficulty: Optional[str] = None) -> List[Question]:
        """
        Search questions with multiple filters using efficient algorithms.
        
        Args:
            search_text: Optional text to search for
            topic: Optional topic filter
            difficulty: Optional difficulty filter
            
        Returns:
            Filtered list of questions
        """
        try:
            # Start with all questions
            questions = self.question_repository.get_all()
            
            # Apply filters in order of selectivity (most restrictive first)
            if difficulty:
                questions = [q for q in questions if q.difficulty == difficulty]
            
            if topic:
                questions = [q for q in questions if q.topic == topic]
            
            if search_text:
                search_text_lower = search_text.lower()
                questions = [q for q in questions if search_text_lower in q.question_text.lower()]
            
            self.logger.info(f"Multi-filter search found {len(questions)} questions")
            return questions
            
        except Exception as e:
            self.logger.error(f"Failed to perform multi-filter search: {str(e)}")
            raise QuestionError(f"Failed to search questions with filters: {str(e)}")

    def advanced_search_questions(self, criteria: Dict[str, Any]) -> List[Question]:
        """
        Advanced search with multiple criteria using optimized algorithms.
        
        Args:
            criteria: Dictionary of search criteria
            
        Returns:
            List of questions matching all criteria
        """
        try:
            all_questions = self.question_repository.get_all()
            results = []
            
            # Use efficient iteration through questions once
            for question in all_questions:
                matches = True
                
                # Check each criterion
                for key, value in criteria.items():
                    if key == 'topic' and question.topic != value:
                        matches = False
                        break
                    elif key == 'difficulty' and question.difficulty != value:
                        matches = False
                        break
                    elif key == 'text_contains' and value.lower() not in question.question_text.lower():
                        matches = False
                        break
                    elif key == 'id_pattern' and not question.id.startswith(value):
                        matches = False
                        break
                    elif key == 'has_options' and value:
                        # Check if question has all required options
                        if not all([question.option1, question.option2, question.option3, question.option4]):
                            matches = False
                            break
                
                if matches:
                    results.append(question)
            
            self.logger.info(f"Advanced search found {len(results)} questions")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to perform advanced search: {str(e)}")
            raise QuestionError(f"Failed to perform advanced search: {str(e)}")

    # Complex selection (nested if/switch) for topic/difficulty filtering
    def filter_questions_by_complex_criteria(self, topic: Optional[str] = None, 
                                            difficulty: Optional[str] = None,
                                            question_count: Optional[int] = None,
                                            sort_by: str = 'id') -> List[Question]:
        """
        Complex selection with nested if/switch statements for advanced filtering.
        
        Args:
            topic: Optional topic filter
            difficulty: Optional difficulty filter  
            question_count: Optional limit on number of questions
            sort_by: Sort criteria ('id', 'topic', 'difficulty', 'random')
            
        Returns:
            Filtered and sorted list of questions
        """
        try:
            all_questions = self.question_repository.get_all()
            filtered_questions = []
            
            # Complex nested if/switch for filtering logic
            for question in all_questions:
                include_question = True
                
                # Topic filtering with nested conditions
                if topic is not None:
                    if topic.lower() == 'all':
                        # Include all topics - no filtering needed
                        pass
                    elif topic.lower() == 'science':
                        # Complex selection for science topics
                        if question.topic == 'Physics' or question.topic == 'Chemistry':
                            include_question = True
                        else:
                            include_question = False
                    elif topic.lower() == 'mathematics':
                        # Switch-like behavior for math topics
                        if question.topic == 'Math':
                            include_question = True
                        else:
                            include_question = False
                    else:
                        # Exact topic match
                        if question.topic == topic:
                            include_question = True
                        else:
                            include_question = False
                
                # Difficulty filtering with nested conditions (only if topic passed)
                if include_question and difficulty is not None:
                    if difficulty.lower() == 'all':
                        # Include all difficulties - no filtering needed
                        pass
                    elif difficulty.lower() == 'beginner':
                        # Complex selection for beginner levels
                        if question.difficulty == 'Easy':
                            include_question = True
                        else:
                            include_question = False
                    elif difficulty.lower() == 'advanced':
                        # Switch-like behavior for advanced levels
                        if question.difficulty == 'Hard':
                            include_question = True
                        else:
                            include_question = False
                    elif difficulty.lower() == 'intermediate':
                        # Nested if for intermediate
                        if question.difficulty == 'Medium':
                            include_question = True
                        else:
                            include_question = False
                    else:
                        # Exact difficulty match
                        if question.difficulty == difficulty:
                            include_question = True
                        else:
                            include_question = False
                
                # Add question if it passed all filters
                if include_question:
                    filtered_questions.append(question)
            
            # Complex selection for sorting (switch-like behavior)
            if sort_by.lower() == 'id':
                filtered_questions.sort(key=lambda q: q.id)
            elif sort_by.lower() == 'topic':
                filtered_questions.sort(key=lambda q: q.topic)
            elif sort_by.lower() == 'difficulty':
                difficulty_order = {'Easy': 0, 'Medium': 1, 'Hard': 2}
                filtered_questions.sort(key=lambda q: difficulty_order[q.difficulty])
            elif sort_by.lower() == 'random':
                import random
                random.shuffle(filtered_questions)
            elif sort_by.lower() == 'topic_difficulty':
                # Nested sorting by topic then difficulty
                topic_order = {'Chemistry': 0, 'Math': 1, 'Physics': 2}
                difficulty_order = {'Easy': 0, 'Medium': 1, 'Hard': 2}
                filtered_questions.sort(key=lambda q: (topic_order[q.topic], difficulty_order[q.difficulty]))
            else:
                # Default sort by ID
                filtered_questions.sort(key=lambda q: q.id)
            
            # Apply question count limit if specified
            if question_count is not None:
                if question_count > 0:
                    if len(filtered_questions) > question_count:
                        filtered_questions = filtered_questions[:question_count]
                else:
                    filtered_questions = []
            
            self.logger.info(f"Complex filter returned {len(filtered_questions)} questions")
            return filtered_questions
            
        except Exception as e:
            self.logger.error(f"Failed to perform complex filtering: {str(e)}")
            raise QuestionError(f"Failed to filter questions: {str(e)}")

    def determine_question_complexity(self, question: Question) -> str:
        """
        Complex selection using nested if/switch to determine question complexity.
        
        Args:
            question: Question to analyze
            
        Returns:
            Complexity rating string
        """
        # Complex nested if/switch for complexity determination
        if question.topic == 'Physics':
            if question.difficulty == 'Easy':
                return 'Basic Physics'
            elif question.difficulty == 'Medium':
                if 'mechanics' in question.question_text.lower():
                    return 'Intermediate Mechanics'
                elif 'electricity' in question.question_text.lower():
                    return 'Intermediate Electricity'
                else:
                    return 'Intermediate Physics'
            else:  # Hard
                if 'quantum' in question.question_text.lower():
                    return 'Advanced Quantum Physics'
                elif 'relativity' in question.question_text.lower():
                    return 'Advanced Relativity'
                else:
                    return 'Advanced Physics'
        
        elif question.topic == 'Chemistry':
            if question.difficulty == 'Easy':
                return 'Basic Chemistry'
            elif question.difficulty == 'Medium':
                if 'organic' in question.question_text.lower():
                    return 'Intermediate Organic Chemistry'
                elif 'inorganic' in question.question_text.lower():
                    return 'Intermediate Inorganic Chemistry'
                else:
                    return 'Intermediate Chemistry'
            else:  # Hard
                if 'biochemistry' in question.question_text.lower():
                    return 'Advanced Biochemistry'
                elif 'physical' in question.question_text.lower():
                    return 'Advanced Physical Chemistry'
                else:
                    return 'Advanced Chemistry'
        
        elif question.topic == 'Math':
            if question.difficulty == 'Easy':
                return 'Basic Mathematics'
            elif question.difficulty == 'Medium':
                if 'algebra' in question.question_text.lower():
                    return 'Intermediate Algebra'
                elif 'geometry' in question.question_text.lower():
                    return 'Intermediate Geometry'
                elif 'calculus' in question.question_text.lower():
                    return 'Intermediate Calculus'
                else:
                    return 'Intermediate Mathematics'
            else:  # Hard
                if 'differential' in question.question_text.lower():
                    return 'Advanced Differential Equations'
                elif 'linear' in question.question_text.lower():
                    return 'Advanced Linear Algebra'
                elif 'statistics' in question.question_text.lower():
                    return 'Advanced Statistics'
                else:
                    return 'Advanced Mathematics'
        
        else:
            return 'Unknown Complexity'

    # Loop-based methods for question iteration and processing
    def process_questions_with_loops(self, questions: List[Question]) -> Dict[str, Any]:
        """
        Process questions using various loop constructs.
        
        Args:
            questions: List of questions to process
            
        Returns:
            Dictionary with processing results
        """
        results = {
            'total_count': 0,
            'topic_counts': {},
            'difficulty_counts': {},
            'average_question_length': 0.0,
            'questions_with_options': []
        }
        
        # For loop for basic iteration
        total_length = 0
        for question in questions:
            results['total_count'] += 1
            
            # Process topic counts
            topic = question.topic
            if topic in results['topic_counts']:
                results['topic_counts'][topic] += 1
            else:
                results['topic_counts'][topic] = 1
            
            # Process difficulty counts
            difficulty = question.difficulty
            if difficulty in results['difficulty_counts']:
                results['difficulty_counts'][difficulty] += 1
            else:
                results['difficulty_counts'][difficulty] = 1
            
            # Calculate question text length
            total_length += len(question.question_text)
            
            # Collect questions with complete options
            if question.option1 and question.option2 and question.option3 and question.option4:
                results['questions_with_options'].append(question.id)
        
        # Calculate average
        if questions:
            results['average_question_length'] = total_length / len(questions)
        
        return results

    def find_questions_by_keyword_loops(self, questions: List[Question], keywords: List[str]) -> List[Question]:
        """
        Find questions containing keywords using loop iteration.
        
        Args:
            questions: List of questions to search
            keywords: List of keywords to search for
            
        Returns:
            List of questions containing any of the keywords
        """
        matching_questions = []
        
        # While loop for iteration
        i = 0
        while i < len(questions):
            question = questions[i]
            question_text_lower = question.question_text.lower()
            
            # Inner for loop for keyword checking
            for keyword in keywords:
                if keyword.lower() in question_text_lower:
                    matching_questions.append(question)
                    break  # Found a match, move to next question
            
            i += 1
        
        return matching_questions

    def validate_question_batch_loops(self, questions: List[Question]) -> Dict[str, List[str]]:
        """
        Validate a batch of questions using loops.
        
        Args:
            questions: List of questions to validate
            
        Returns:
            Dictionary with validation errors by question ID
        """
        validation_errors = {}
        
        # For loop with enumerate for index tracking
        for index, question in enumerate(questions):
            errors = []
            
            # Validation checks using if statements within loops
            if not question.id or not question.id.strip():
                errors.append("Question ID is empty")
            
            if not question.topic or not question.topic.strip():
                errors.append("Question topic is empty")
            elif question.topic not in ['Physics', 'Chemistry', 'Math']:
                errors.append(f"Invalid topic: {question.topic}")
            
            if not question.question_text or not question.question_text.strip():
                errors.append("Question text is empty")
            elif len(question.question_text) < 10:
                errors.append("Question text is too short")
            
            # Check options using loop
            options = [question.option1, question.option2, question.option3, question.option4]
            for i, option in enumerate(options, 1):
                if not option or not option.strip():
                    errors.append(f"Option {i} is empty")
            
            if not question.correct_answer or not question.correct_answer.strip():
                errors.append("Correct answer is empty")
            
            if errors:
                validation_errors[question.id] = errors
        
        return validation_errors

    def calculate_question_statistics_loops(self, questions: List[Question]) -> Dict[str, Any]:
        """
        Calculate statistics using loop constructs.
        
        Args:
            questions: List of questions to analyze
            
        Returns:
            Dictionary with calculated statistics
        """
        stats = {
            'total_questions': len(questions),
            'topics': set(),
            'difficulties': set(),
            'topic_difficulty_matrix': {},
            'option_completeness': {'complete': 0, 'incomplete': 0}
        }
        
        # For loop to build statistics
        for question in questions:
            # Collect topics and difficulties
            stats['topics'].add(question.topic)
            stats['difficulties'].add(question.difficulty)
            
            # Build topic-difficulty matrix using nested logic
            topic_key = question.topic
            if topic_key not in stats['topic_difficulty_matrix']:
                stats['topic_difficulty_matrix'][topic_key] = {'Easy': 0, 'Medium': 0, 'Hard': 0}
            
            stats['topic_difficulty_matrix'][topic_key][question.difficulty] += 1
            
            # Check option completeness
            options = [question.option1, question.option2, question.option3, question.option4]
            if all(option.strip() for option in options if option):
                stats['option_completeness']['complete'] += 1
            else:
                stats['option_completeness']['incomplete'] += 1
        
        # Convert sets to lists for JSON serialization
        stats['topics'] = list(stats['topics'])
        stats['difficulties'] = list(stats['difficulties'])
        
        return stats

    def transform_questions_loops(self, questions: List[Question], transform_type: str) -> List[Dict[str, Any]]:
        """
        Transform questions using loop-based processing.
        
        Args:
            questions: List of questions to transform
            transform_type: Type of transformation ('summary', 'options_only', 'metadata')
            
        Returns:
            List of transformed question dictionaries
        """
        transformed = []
        
        # For loop with conditional transformation
        for question in questions:
            if transform_type == 'summary':
                # Create summary version
                transformed.append({
                    'id': question.id,
                    'topic': question.topic,
                    'difficulty': question.difficulty,
                    'text_preview': question.question_text[:50] + '...' if len(question.question_text) > 50 else question.question_text
                })
            
            elif transform_type == 'options_only':
                # Create options-only version
                transformed.append({
                    'id': question.id,
                    'question': question.question_text,
                    'options': {
                        'A': question.option1,
                        'B': question.option2,
                        'C': question.option3,
                        'D': question.option4
                    }
                })
            
            elif transform_type == 'metadata':
                # Create metadata version
                transformed.append({
                    'id': question.id,
                    'topic': question.topic,
                    'difficulty': question.difficulty,
                    'has_options': all([question.option1, question.option2, question.option3, question.option4]),
                    'text_length': len(question.question_text),
                    'correct_answer_length': len(question.correct_answer) if question.correct_answer else 0
                })
            
            else:
                # Default transformation
                transformed.append({
                    'id': question.id,
                    'topic': question.topic,
                    'difficulty': question.difficulty,
                    'full_question': question.question_text
                })
        
        return transformed

    # Nested loops for advanced searching operations
    def advanced_search_with_nested_loops(self, questions: List[Question], 
                                         search_criteria: Dict[str, Any]) -> List[Question]:
        """
        Advanced search using nested loops for complex criteria matching.
        
        Args:
            questions: List of questions to search
            search_criteria: Dictionary with search criteria
            
        Returns:
            List of questions matching all criteria
        """
        matching_questions = []
        
        # Outer loop through questions
        for question in questions:
            matches_all_criteria = True
            
            # Nested loop through criteria
            for criterion_key, criterion_value in search_criteria.items():
                if criterion_key == 'keywords':
                    # Nested loop through keywords
                    keyword_found = False
                    for keyword in criterion_value:
                        if keyword.lower() in question.question_text.lower():
                            keyword_found = True
                            break
                    if not keyword_found:
                        matches_all_criteria = False
                        break
                
                elif criterion_key == 'topic_difficulty_pairs':
                    # Nested loops through topic-difficulty pairs
                    pair_found = False
                    for pair in criterion_value:
                        if question.topic == pair['topic'] and question.difficulty == pair['difficulty']:
                            pair_found = True
                            break
                    if not pair_found:
                        matches_all_criteria = False
                        break
                
                elif criterion_key == 'option_patterns':
                    # Nested loop through option patterns
                    pattern_found = False
                    options = [question.option1, question.option2, question.option3, question.option4]
                    for pattern in criterion_value:
                        for option in options:
                            if option and pattern.lower() in option.lower():
                                pattern_found = True
                                break
                        if pattern_found:
                            break
                    if not pattern_found:
                        matches_all_criteria = False
                        break
                
                elif criterion_key == 'text_length_range':
                    # Nested logic for length range checking
                    min_length = criterion_value.get('min', 0)
                    max_length = criterion_value.get('max', float('inf'))
                    question_length = len(question.question_text)
                    
                    length_ok = False
                    # Check if length falls within any specified ranges
                    if 'ranges' in criterion_value:
                        for range_pair in criterion_value['ranges']:
                            if range_pair[0] <= question_length <= range_pair[1]:
                                length_ok = True
                                break
                    else:
                        length_ok = min_length <= question_length <= max_length
                    
                    if not length_ok:
                        matches_all_criteria = False
                        break
            
            if matches_all_criteria:
                matching_questions.append(question)
        
        return matching_questions

    def find_similar_questions_nested_loops(self, target_question: Question, 
                                          questions: List[Question], 
                                          similarity_threshold: float = 0.5) -> List[tuple[Question, float]]:
        """
        Find similar questions using nested loops for similarity calculation.
        
        Args:
            target_question: Question to find similarities for
            questions: List of questions to compare against
            similarity_threshold: Minimum similarity score (0.0 to 1.0)
            
        Returns:
            List of tuples (question, similarity_score) sorted by similarity
        """
        from difflib import SequenceMatcher
        similar_questions = []
        
        # Outer loop through all questions
        for question in questions:
            if question.id == target_question.id:
                continue  # Skip the target question itself
            
            total_similarity = 0.0
            similarity_count = 0
            
            # Nested loops for multi-aspect similarity calculation
            aspects = [
                ('topic', target_question.topic, question.topic),
                ('difficulty', target_question.difficulty, question.difficulty),
                ('question_text', target_question.question_text, question.question_text)
            ]
            
            # Loop through aspects for similarity calculation
            for aspect_name, target_value, question_value in aspects:
                if aspect_name in ['topic', 'difficulty']:
                    # Exact match for categorical data
                    similarity = 1.0 if target_value == question_value else 0.0
                else:
                    # Text similarity for question text
                    similarity = SequenceMatcher(None, target_value.lower(), question_value.lower()).ratio()
                
                total_similarity += similarity
                similarity_count += 1
            
            # Additional nested loops for option similarity
            target_options = [target_question.option1, target_question.option2, 
                            target_question.option3, target_question.option4]
            question_options = [question.option1, question.option2, 
                              question.option3, question.option4]
            
            option_similarity_sum = 0.0
            option_comparisons = 0
            
            # Nested loops through options
            for i, target_option in enumerate(target_options):
                for j, question_option in enumerate(question_options):
                    if target_option and question_option:
                        option_similarity = SequenceMatcher(None, target_option.lower(), 
                                                           question_option.lower()).ratio()
                        option_similarity_sum += option_similarity
                        option_comparisons += 1
            
            # Calculate average similarity
            if option_comparisons > 0:
                average_option_similarity = option_similarity_sum / option_comparisons
                total_similarity += average_option_similarity
                similarity_count += 1
            
            # Final similarity score
            final_similarity = total_similarity / similarity_count if similarity_count > 0 else 0.0
            
            # Include if above threshold
            if final_similarity >= similarity_threshold:
                similar_questions.append((question, final_similarity))
        
        # Sort by similarity (highest first)
        similar_questions.sort(key=lambda x: x[1], reverse=True)
        
        return similar_questions

    def analyze_question_patterns_nested_loops(self, questions: List[Question]) -> Dict[str, Any]:
        """
        Analyze patterns in questions using nested loops.
        
        Args:
            questions: List of questions to analyze
            
        Returns:
            Dictionary with pattern analysis results
        """
        patterns = {
            'common_words': {},
            'topic_difficulty_combinations': {},
            'option_length_patterns': {},
            'question_structure_patterns': {}
        }
        
        # Nested loops for word frequency analysis
        all_words = []
        for question in questions:
            words = question.question_text.lower().split()
            for word in words:
                # Clean word and add to list
                clean_word = ''.join(c for c in word if c.isalnum())
                if len(clean_word) > 3:  # Only words longer than 3 characters
                    all_words.append(clean_word)
        
        # Count word frequencies
        for word in all_words:
            if word in patterns['common_words']:
                patterns['common_words'][word] += 1
            else:
                patterns['common_words'][word] = 1
        
        # Nested loops for topic-difficulty combination analysis
        for question in questions:
            combo_key = f"{question.topic}_{question.difficulty}"
            if combo_key in patterns['topic_difficulty_combinations']:
                patterns['topic_difficulty_combinations'][combo_key] += 1
            else:
                patterns['topic_difficulty_combinations'][combo_key] = 1
        
        # Nested loops for option length patterns
        length_ranges = [(0, 20), (21, 50), (51, 100), (101, float('inf'))]
        for question in questions:
            options = [question.option1, question.option2, question.option3, question.option4]
            total_length = 0
            
            for option in options:
                if option:
                    total_length += len(option)
            
            average_length = total_length / 4 if options else 0
            
            # Find which range this falls into
            for i, (min_len, max_len) in enumerate(length_ranges):
                if min_len <= average_length <= max_len:
                    range_key = f"range_{i+1}"
                    if range_key in patterns['option_length_patterns']:
                        patterns['option_length_patterns'][range_key] += 1
                    else:
                        patterns['option_length_patterns'][range_key] = 1
                    break
        
        # Nested loops for question structure patterns
        structure_patterns = ['contains_numbers', 'contains_formulas', 'question_mark_end', 'multiple_sentences']
        
        for question in questions:
            text = question.question_text
            
            # Check each pattern
            for pattern in structure_patterns:
                pattern_found = False
                
                if pattern == 'contains_numbers':
                    for char in text:
                        if char.isdigit():
                            pattern_found = True
                            break
                
                elif pattern == 'contains_formulas':
                    formula_indicators = ['=', '+', '-', '*', '/', '(', ')', '^', '√', 'π', '∑']
                    for indicator in formula_indicators:
                        if indicator in text:
                            pattern_found = True
                            break
                
                elif pattern == 'question_mark_end':
                    pattern_found = text.strip().endswith('?')
                
                elif pattern == 'multiple_sentences':
                    sentence_count = 0
                    for char in text:
                        if char in '.!?':
                            sentence_count += 1
                    pattern_found = sentence_count > 1
                
                if pattern_found:
                    if pattern in patterns['question_structure_patterns']:
                        patterns['question_structure_patterns'][pattern] += 1
                    else:
                        patterns['question_structure_patterns'][pattern] = 1
        
        return patterns

    def cross_reference_search_nested_loops(self, questions: List[Question], 
                                          reference_data: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """
        Cross-reference questions with external data using nested loops.
        
        Args:
            questions: List of questions to cross-reference
            reference_data: Dictionary with reference data lists
            
        Returns:
            List of cross-reference results
        """
        results = []
        
        # Outer loop through questions
        for question in questions:
            cross_refs = {
                'question_id': question.id,
                'matches': {}
            }
            
            # Nested loops through reference data categories
            for category, reference_list in reference_data.items():
                matches_found = []
                
                # Nested loops through reference items
                for reference_item in reference_list:
                    # Check if reference item matches any part of the question
                    question_text_lower = question.question_text.lower()
                    reference_lower = reference_item.lower()
                    
                    # Check various fields for matches
                    fields_to_check = [
                        ('question_text', question.question_text),
                        ('option1', question.option1),
                        ('option2', question.option2),
                        ('option3', question.option3),
                        ('option4', question.option4),
                        ('correct_answer', question.correct_answer)
                    ]
                    
                    # Nested loops through fields
                    for field_name, field_value in fields_to_check:
                        if field_value and reference_lower in field_value.lower():
                            matches_found.append({
                                'reference': reference_item,
                                'field': field_name,
                                'context': field_value
                            })
                            break  # Found match in this question, move to next reference
                
                if matches_found:
                    cross_refs['matches'][category] = matches_found
            
            # Only include questions with matches
            if cross_refs['matches']:
                results.append(cross_refs)
        
        return results

    # User-defined methods with parameter for service operations
    def process_questions_with_parameters(self, questions: List[Question], 
                                         operation_type: str = 'validate',
                                         custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        User-defined method with multiple parameters for flexible question processing.
        
        Args:
            questions: List of questions to process
            operation_type: Type of operation ('validate', 'transform', 'analyze', 'filter')
            custom_params: Optional dictionary of custom parameters
            
        Returns:
            Dictionary with operation results
        """
        if custom_params is None:
            custom_params = {}
        
        results = {
            'operation_type': operation_type,
            'processed_count': 0,
            'results': [],
            'errors': [],
            'metadata': custom_params
        }
        
        try:
            if operation_type == 'validate':
                validation_rules = custom_params.get('validation_rules', {})
                for question in questions:
                    validation_result = self._validate_question_with_params(question, validation_rules)
                    results['results'].append(validation_result)
                    results['processed_count'] += 1
            
            elif operation_type == 'transform':
                transform_config = custom_params.get('transform_config', {})
                for question in questions:
                    transformed = self._transform_question_with_params(question, transform_config)
                    results['results'].append(transformed)
                    results['processed_count'] += 1
            
            elif operation_type == 'analyze':
                analysis_params = custom_params.get('analysis_params', {})
                analysis_result = self._analyze_questions_with_params(questions, analysis_params)
                results.update(analysis_result)
            
            elif operation_type == 'filter':
                filter_criteria = custom_params.get('filter_criteria', {})
                filtered_questions = self._filter_questions_with_params(questions, filter_criteria)
                results['results'] = filtered_questions
                results['processed_count'] = len(filtered_questions)
            
            else:
                raise ValueError(f"Unknown operation type: {operation_type}")
        
        except Exception as e:
            results['errors'].append(str(e))
            self.logger.error(f"Error in process_questions_with_parameters: {str(e)}")
        
        return results

    def batch_operation_with_parameters(self, operation_name: str, 
                                       questions: List[Question],
                                       batch_size: int = 10,
                                       operation_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        User-defined method for batch operations with parameter control.
        
        Args:
            operation_name: Name of the operation to perform
            questions: List of questions to process
            batch_size: Size of each batch
            operation_params: Parameters specific to the operation
            
        Returns:
            Dictionary with batch operation results
        """
        if operation_params is None:
            operation_params = {}
        
        results = {
            'operation_name': operation_name,
            'total_questions': len(questions),
            'batch_size': batch_size,
            'batches_processed': 0,
            'total_processed': 0,
            'batch_results': [],
            'errors': []
        }
        
        try:
            # Process in batches
            for i in range(0, len(questions), batch_size):
                batch = questions[i:i + batch_size]
                
                if operation_name == 'validate':
                    batch_result = self.process_questions_with_parameters(
                        batch, 'validate', operation_params
                    )
                elif operation_name == 'transform':
                    batch_result = self.process_questions_with_parameters(
                        batch, 'transform', operation_params
                    )
                elif operation_name == 'analyze':
                    batch_result = self.process_questions_with_parameters(
                        batch, 'analyze', operation_params
                    )
                else:
                    raise ValueError(f"Unknown batch operation: {operation_name}")
                
                results['batch_results'].append(batch_result)
                results['batches_processed'] += 1
                results['total_processed'] += batch_result.get('processed_count', 0)
        
        except Exception as e:
            results['errors'].append(str(e))
            self.logger.error(f"Error in batch_operation_with_parameters: {str(e)}")
        
        return results


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
