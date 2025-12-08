"""
Unit tests for question service."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import List, Optional, Dict, Any
import random

from src.services.question_service import QuestionService
from src.services.interfaces import IQuestionRepository, QuestionFilter
from src.models.question import Question
from src.utils.exceptions import QuestionError, ValidationError


class TestQuestionServiceInitialization:
    """Unit tests for QuestionService initialization."""

    def test_init_with_repository(self) -> None:
        """Test initialization with repository."""
        mock_repo = Mock(spec=IQuestionRepository)
        
        service = QuestionService(question_repository=mock_repo)
        
        assert service.question_repository == mock_repo

    def test_init_with_custom_logger(self) -> None:
        """Test initialization with custom logger."""
        mock_repo = Mock(spec=IQuestionRepository)
        mock_logger = Mock()
        
        service = QuestionService(question_repository=mock_repo, logger=mock_logger)
        
        assert service.logger == mock_logger


class TestGetAvailableTopics:
    """Unit tests for get_available_topics method."""

    def test_get_available_topics_success(self) -> None:
        """Test successful retrieval of topics."""
        mock_repo = Mock()
        mock_repo.get_available_topics.return_value = ["Physics", "Chemistry", "Math"]
        
        service = QuestionService(question_repository=mock_repo)
        result = service.get_available_topics()
        
        assert len(result) == 3
        assert "Physics" in result

    def test_get_available_topics_error(self) -> None:
        """Test error handling in get_available_topics."""
        mock_repo = Mock()
        mock_repo.get_available_topics.side_effect = Exception("Database error")
        
        service = QuestionService(question_repository=mock_repo)
        
        with pytest.raises(QuestionError):
            service.get_available_topics()


class TestGetAvailableDifficulties:
    """Unit tests for get_available_difficulties method."""

    def test_get_available_difficulties_success(self) -> None:
        """Test successful retrieval of difficulties."""
        mock_repo = Mock()
        mock_repo.get_available_difficulties.return_value = ["Easy", "Medium", "Hard"]
        
        service = QuestionService(question_repository=mock_repo)
        result = service.get_available_difficulties()
        
        assert len(result) == 3
        assert "Easy" in result

    def test_get_available_difficulties_error(self) -> None:
        """Test error handling in get_available_difficulties."""
        mock_repo = Mock()
        mock_repo.get_available_difficulties.side_effect = Exception("Database error")
        
        service = QuestionService(question_repository=mock_repo)
        
        with pytest.raises(QuestionError):
            service.get_available_difficulties()


class TestValidateAnswer:
    """Unit tests for validate_answer method."""

    @pytest.fixture
    def sample_question(self) -> Mock:
        """Create a sample question mock."""
        question = Mock(spec=Question)
        question.id = "q_1"
        question.is_correct_answer.return_value = True
        return question

    def test_validate_answer_correct(self, sample_question: Mock) -> None:
        """Test validating a correct answer."""
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = sample_question
        
        service = QuestionService(question_repository=mock_repo)
        result = service.validate_answer("q_1", "Inertia")
        
        assert result is True
        sample_question.mark_as_answered.assert_called_once_with(True)

    def test_validate_answer_incorrect(self, sample_question: Mock) -> None:
        """Test validating an incorrect answer."""
        sample_question.is_correct_answer.return_value = False
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = sample_question
        
        service = QuestionService(question_repository=mock_repo)
        result = service.validate_answer("q_1", "Wrong")
        
        assert result is False
        sample_question.mark_as_answered.assert_called_once_with(False)

    def test_validate_answer_empty_raises_error(self) -> None:
        """Test that empty answer raises ValidationError."""
        mock_repo = Mock()
        service = QuestionService(question_repository=mock_repo)
        
        with pytest.raises(ValidationError):
            service.validate_answer("q_1", "")

    def test_validate_answer_question_not_found(self) -> None:
        """Test that missing question raises QuestionError."""
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = None
        
        service = QuestionService(question_repository=mock_repo)
        
        with pytest.raises(QuestionError):
            service.validate_answer("nonexistent", "Answer")


class TestGetQuestionById:
    """Unit tests for get_question_by_id method."""

    def test_get_question_by_id_found(self) -> None:
        """Test getting question by ID when found."""
        mock_question = Mock(spec=Question)
        mock_question.id = "q_1"
        
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = mock_question
        
        service = QuestionService(question_repository=mock_repo)
        result = service.get_question_by_id("q_1")
        
        assert result is not None
        assert result.id == "q_1"

    def test_get_question_by_id_not_found(self) -> None:
        """Test getting question by ID when not found."""
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = None
        
        service = QuestionService(question_repository=mock_repo)
        result = service.get_question_by_id("nonexistent")
        
        assert result is None

    def test_get_question_by_id_error(self) -> None:
        """Test error handling in get_question_by_id."""
        mock_repo = Mock()
        mock_repo.get_by_id.side_effect = Exception("Database error")
        
        service = QuestionService(question_repository=mock_repo)
        
        with pytest.raises(QuestionError):
            service.get_question_by_id("q_1")


class TestGetQuestionsByCriteria:
    """Unit tests for get_questions_by_criteria method."""

    @pytest.fixture
    def sample_questions(self) -> List[Mock]:
        """Create sample question mocks."""
        questions = []
        for i in range(5):
            q = Mock(spec=Question)
            q.id = f"q_{i}"
            questions.append(q)
        return questions

    def test_get_questions_by_criteria_success(self, sample_questions: List[Mock]) -> None:
        """Test getting questions by criteria."""
        mock_repo = Mock()
        mock_repo.filter.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.get_questions_by_criteria("Physics", "Easy")
        
        assert len(result) == 5

    def test_get_questions_by_criteria_with_limit(self, sample_questions: List[Mock]) -> None:
        """Test getting questions by criteria with limit."""
        mock_repo = Mock()
        mock_repo.filter.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.get_questions_by_criteria("Physics", "Easy", limit=3)
        
        assert len(result) == 3

    def test_get_questions_by_criteria_error(self) -> None:
        """Test error handling in get_questions_by_criteria."""
        mock_repo = Mock()
        mock_repo.filter.side_effect = Exception("Filter error")
        
        service = QuestionService(question_repository=mock_repo)
        
        with pytest.raises(QuestionError):
            service.get_questions_by_criteria("Physics", "Easy")


class TestCountQuestionsByCriteria:
    """Unit tests for count_questions_by_criteria method."""

    def test_count_questions_by_criteria_success(self) -> None:
        """Test counting questions by criteria."""
        mock_repo = Mock()
        mock_repo.count_by_criteria.return_value = 10
        
        service = QuestionService(question_repository=mock_repo)
        result = service.count_questions_by_criteria("Physics", "Easy")
        
        assert result == 10

    def test_count_questions_by_criteria_zero(self) -> None:
        """Test counting when no questions match."""
        mock_repo = Mock()
        mock_repo.count_by_criteria.return_value = 0
        
        service = QuestionService(question_repository=mock_repo)
        result = service.count_questions_by_criteria("Physics", "Hard")
        
        assert result == 0

    def test_count_questions_by_criteria_error(self) -> None:
        """Test error handling in count_questions_by_criteria."""
        mock_repo = Mock()
        mock_repo.count_by_criteria.side_effect = Exception("Count error")
        
        service = QuestionService(question_repository=mock_repo)
        
        with pytest.raises(QuestionError):
            service.count_questions_by_criteria("Physics", "Easy")


class TestGetQuestionStatistics:
    """Unit tests for get_question_statistics method."""

    def test_get_question_statistics_success(self) -> None:
        """Test getting question statistics."""
        mock_repo = Mock()
        mock_repo.get_available_topics.return_value = ["Physics", "Chemistry"]
        mock_repo.get_available_difficulties.return_value = ["Easy", "Hard"]
        mock_repo.count_by_criteria.return_value = 5
        
        service = QuestionService(question_repository=mock_repo)
        result = service.get_question_statistics()
        
        assert result["total_topics"] == 2
        assert result["total_difficulties"] == 2
        assert "topic_difficulty_counts" in result

    def test_get_question_statistics_error(self) -> None:
        """Test error handling in get_question_statistics."""
        mock_repo = Mock()
        mock_repo.get_available_topics.side_effect = Exception("Stats error")
        
        service = QuestionService(question_repository=mock_repo)
        
        with pytest.raises(QuestionError):
            service.get_question_statistics()


class TestResetAllSessionStates:
    """Unit tests for reset_all_session_states method."""

    def test_reset_all_session_states_success(self) -> None:
        """Test resetting all session states."""
        mock_questions = [Mock(spec=Question) for _ in range(3)]
        mock_repo = Mock()
        mock_repo.get_all.return_value = mock_questions
        
        service = QuestionService(question_repository=mock_repo)
        service.reset_all_session_states()
        
        for q in mock_questions:
            q.reset_session_state.assert_called_once()

    def test_reset_all_session_states_error(self) -> None:
        """Test error handling in reset_all_session_states."""
        mock_repo = Mock()
        mock_repo.get_all.side_effect = Exception("Reset error")
        
        service = QuestionService(question_repository=mock_repo)
        
        with pytest.raises(QuestionError):
            service.reset_all_session_states()


class TestQuestionRandomization:
    """Unit tests for question randomization functionality."""

    @pytest.fixture
    def mock_question_bank(self) -> Mock:
        """Create a mock question bank with test data."""
        bank = Mock()
        
        # Create test questions
        questions = [
            Question(
                id="physics_1",
                topic="Physics",
                question_text="What is Newton's first law?",
                option1="Inertia",
                option2="F=ma",
                option3="Action-reaction",
                option4="Gravity",
                correct_answer="Inertia",
                difficulty="Easy",
                tag="Physics-Easy"
            ),
            Question(
                id="physics_2",
                topic="Physics",
                question_text="What is the unit of force?",
                option1="Newton",
                option2="Joule",
                option3="Watt",
                option4="Pascal",
                correct_answer="Newton",
                difficulty="Easy",
                tag="Physics-Easy"
            ),
            Question(
                id="physics_3",
                topic="Physics",
                question_text="What is speed of light?",
                option1="3x10^8 m/s",
                option2="2x10^8 m/s",
                option3="4x10^8 m/s",
                option4="1x10^8 m/s",
                correct_answer="3x10^8 m/s",
                difficulty="Medium",
                tag="Physics-Medium"
            ),
            Question(
                id="chemistry_1",
                topic="Chemistry",
                question_text="What is H2O?",
                option1="Water",
                option2="Oxygen",
                option3="Hydrogen",
                option4="Carbon",
                correct_answer="Water",
                difficulty="Easy",
                tag="Chemistry-Easy"
            ),
            Question(
                id="math_1",
                topic="Math",
                question_text="What is 2+2?",
                option1="3",
                option2="4",
                option3="5",
                option4="6",
                correct_answer="4",
                difficulty="Easy",
                tag="Math-Easy"
            )
        ]
        
        bank.get_questions_by_criteria.return_value = questions
        bank.get_all_questions.return_value = questions
        bank.get_all.return_value = questions
        bank.get_available_topics.return_value = ["Physics", "Chemistry", "Math"]
        bank.get_available_difficulties.return_value = ["Easy", "Medium", "Hard"]
        
        # Setup filter to return filtered questions based on criteria
        def filter_questions(criteria):
            result = []
            for q in questions:
                if criteria.topic and q.topic != criteria.topic:
                    continue
                if criteria.difficulty and q.difficulty != criteria.difficulty:
                    continue
                if criteria.exclude_ids and q.id in criteria.exclude_ids:
                    continue
                result.append(q)
            return result
        
        bank.filter.side_effect = filter_questions
        
        # Setup get_random to return a random question from filtered list
        def get_random(criteria):
            filtered = filter_questions(criteria)
            if not filtered:
                return None
            import random
            return random.choice(filtered)
        
        bank.get_random.side_effect = get_random
        bank.count_by_criteria.side_effect = lambda criteria: len(filter_questions(criteria))
        
        return bank

    @pytest.fixture
    def question_service(self, mock_question_bank: Mock) -> QuestionService:
        """Create QuestionService instance with mock dependencies."""
        return QuestionService(mock_question_bank)

    def test_get_random_question_returns_valid_question(self, question_service: QuestionService) -> None:
        """
        Test that get_random_question returns a valid question.
        
        GIVEN valid topic and difficulty
        WHEN requesting a random question
        THEN return a valid Question object
        """
        topic = "Physics"
        difficulty = "Easy"
        
        question = question_service.get_random_question(topic, difficulty)
        
        assert isinstance(question, Question)
        assert question.topic == topic
        assert question.difficulty == difficulty
        assert question.id is not None
        assert question.question_text is not None

    def test_get_random_question_with_exclusions(self, question_service: QuestionService) -> None:
        """
        Test random question retrieval with exclusions.
        
        GIVEN valid topic, difficulty, and excluded questions
        WHEN requesting a random question
        THEN return a question not in exclusions
        """
        topic = "Physics"
        difficulty = "Easy"
        exclusions = ["physics_1"]
        
        question = question_service.get_random_question(topic, difficulty, exclusions)
        
        assert isinstance(question, Question)
        assert question.topic == topic
        assert question.difficulty == difficulty
        assert question.id not in exclusions

    def test_get_random_question_no_available_questions(self, question_service: QuestionService) -> None:
        """
        Test behavior when no questions are available.
        
        GIVEN topic/difficulty with no matching questions
        WHEN requesting a random question
        THEN raise ValidationError for invalid topic
        """
        from src.utils.exceptions import ValidationError
        topic = "NonExistent"
        difficulty = "Easy"
        
        with pytest.raises(ValidationError) as exc_info:
            question_service.get_random_question(topic, difficulty)
        
        assert "Invalid topic" in str(exc_info.value)

    def test_get_random_question_all_questions_excluded(self, question_service: QuestionService) -> None:
        """
        Test behavior when all questions are excluded.
        
        GIVEN topic/difficulty with all questions excluded
        WHEN requesting a random question
        THEN return None (no questions available)
        """
        topic = "Physics"
        difficulty = "Easy"
        exclusions = ["physics_1", "physics_2"]  # All Easy Physics questions
        
        result = question_service.get_random_question(topic, difficulty, exclusions)
        
        # Service returns None when no questions are available
        assert result is None

    def test_randomization_distribution(self, question_service: QuestionService) -> None:
        """
        Test that randomization is properly distributed.
        
        GIVEN multiple requests for random questions
        WHEN requesting many questions
        THEN distribution should be reasonably uniform
        """
        topic = "Physics"
        difficulty = "Easy"
        
        # Get many random questions
        questions = []
        for _ in range(100):
            question = question_service.get_random_question(topic, difficulty)
            questions.append(question.id)
        
        # Count occurrences
        counts = {}
        for q_id in questions:
            counts[q_id] = counts.get(q_id, 0) + 1
        
        # Should have both physics_1 and physics_2
        assert len(counts) >= 2
        assert "physics_1" in counts
        assert "physics_2" in counts
        
        # Distribution should be reasonable (not too skewed)
        # This is probabilistic, but with 100 samples should be roughly even
        for count in counts.values():
            assert count >= 10  # Each should appear at least 10 times

    def test_fisher_yates_shuffle_implementation(self, question_service: QuestionService) -> None:
        """
        Test that randomization produces different results.
        
        GIVEN multiple requests for random questions
        WHEN requesting many times
        THEN results should vary (not always the same)
        """
        topic = "Physics"
        difficulty = "Easy"
        
        # Get many random questions and verify we get different ones
        question_ids = []
        for _ in range(20):
            question = question_service.get_random_question(topic, difficulty)
            question_ids.append(question.id)
        
        # Should have gotten both physics_1 and physics_2 at some point
        unique_ids = set(question_ids)
        assert len(unique_ids) >= 2, "Randomization should produce different questions"

    def test_duplicate_prevention_in_session(self, question_service: QuestionService) -> None:
        """
        Test that duplicates are prevented within a session.
        
        GIVEN a session with asked questions
        WHEN requesting new questions
        THEN no duplicates should be returned
        """
        topic = "Physics"
        difficulty = "Easy"
        asked_questions = set()
        
        # Get multiple questions without duplicates
        for _ in range(2):  # There are 2 Easy Physics questions
            question = question_service.get_random_question(topic, difficulty, list(asked_questions))
            assert question.id not in asked_questions
            asked_questions.add(question.id)
        
        # Next request should return None (no more questions available)
        result = question_service.get_random_question(topic, difficulty, list(asked_questions))
        assert result is None, "Should return None when all questions are excluded"

    def test_random_question_with_different_parameters(self, question_service: QuestionService) -> None:
        """
        Test randomization with different topic/difficulty combinations.
        
        GIVEN various topic and difficulty combinations
        WHEN requesting random questions
        THEN return appropriate questions for each combination
        """
        test_cases = [
            ("Physics", "Easy"),
            ("Physics", "Medium"),
            ("Chemistry", "Easy"),
            ("Math", "Easy")
        ]
        
        for topic, difficulty in test_cases:
            question = question_service.get_random_question(topic, difficulty)
            assert question.topic == topic
            assert question.difficulty == difficulty

    def test_random_question_thread_safety(self, question_service: QuestionService) -> None:
        """
        Test that randomization is thread-safe.
        
        GIVEN multiple concurrent requests
        WHEN requesting random questions simultaneously
        THEN all requests should succeed without errors
        """
        import threading
        import time
        
        results = []
        errors = []
        
        def get_question():
            try:
                question = question_service.get_random_question("Physics", "Easy")
                results.append(question.id)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=get_question)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 10, "Not all requests completed"

    def test_random_question_performance(self, question_service: QuestionService) -> None:
        """
        Test performance of random question selection.
        
        GIVEN a large number of requests
        WHEN requesting random questions
        THEN performance should be acceptable
        """
        import time
        
        start_time = time.time()
        
        # Make many requests
        for _ in range(1000):
            question = question_service.get_random_question("Physics", "Easy")
            assert question is not None
        
        elapsed_time = time.time() - start_time
        
        # Should complete 1000 requests in reasonable time (less than 1 second)
        assert elapsed_time < 1.0, f"Performance issue: {elapsed_time:.3f}s for 1000 requests"

    def test_random_question_with_empty_exclusions(self, question_service: QuestionService) -> None:
        """
        Test behavior with empty exclusions list.
        
        GIVEN valid parameters and empty exclusions
        WHEN requesting random question
        THEN should work same as no exclusions
        """
        question1 = question_service.get_random_question("Physics", "Easy", [])
        question2 = question_service.get_random_question("Physics", "Easy")
        
        # Both should be valid questions
        assert isinstance(question1, Question)
        assert isinstance(question2, Question)
        assert question1.topic == "Physics"
        assert question1.difficulty == "Easy"
        assert question2.topic == "Physics"
        assert question2.difficulty == "Easy"


class TestLinearSearchQuestions:
    """Unit tests for linear_search_questions method."""

    @pytest.fixture
    def sample_questions(self) -> List[Mock]:
        """Create sample question mocks."""
        q1 = Mock(spec=Question)
        q1.id = "q_1"
        q1.question_text = "What is Newton's first law of motion?"
        
        q2 = Mock(spec=Question)
        q2.id = "q_2"
        q2.question_text = "What is the speed of light?"
        
        q3 = Mock(spec=Question)
        q3.id = "q_3"
        q3.question_text = "What is the chemical formula for water?"
        
        return [q1, q2, q3]

    def test_linear_search_found(self, sample_questions: List[Mock]) -> None:
        """Test linear search when matches are found."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.linear_search_questions("Newton")
        
        assert len(result) == 1
        assert result[0].id == "q_1"

    def test_linear_search_not_found(self, sample_questions: List[Mock]) -> None:
        """Test linear search when no matches found."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.linear_search_questions("Einstein")
        
        assert len(result) == 0

    def test_linear_search_case_insensitive(self, sample_questions: List[Mock]) -> None:
        """Test linear search is case insensitive."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.linear_search_questions("newton")
        
        assert len(result) == 1

    def test_linear_search_error(self) -> None:
        """Test linear search error handling."""
        mock_repo = Mock()
        mock_repo.get_all.side_effect = Exception("Search error")
        
        service = QuestionService(question_repository=mock_repo)
        
        with pytest.raises(QuestionError):
            service.linear_search_questions("test")


class TestBinarySearchQuestionById:
    """Unit tests for binary_search_question_by_id method."""

    @pytest.fixture
    def sample_questions(self) -> List[Mock]:
        """Create sample question mocks."""
        questions = []
        for i in range(5):
            q = Mock(spec=Question)
            q.id = f"q_{i}"
            questions.append(q)
        return questions

    def test_binary_search_found(self, sample_questions: List[Mock]) -> None:
        """Test binary search when question is found."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.binary_search_question_by_id("q_2")
        
        assert result is not None
        assert result.id == "q_2"

    def test_binary_search_not_found(self, sample_questions: List[Mock]) -> None:
        """Test binary search when question not found."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.binary_search_question_by_id("nonexistent")
        
        assert result is None

    def test_binary_search_error(self) -> None:
        """Test binary search error handling."""
        mock_repo = Mock()
        mock_repo.get_all.side_effect = Exception("Search error")
        
        service = QuestionService(question_repository=mock_repo)
        
        with pytest.raises(QuestionError):
            service.binary_search_question_by_id("q_1")


class TestSearchQuestionsByPattern:
    """Unit tests for search_questions_by_pattern method."""

    @pytest.fixture
    def sample_questions(self) -> List[Mock]:
        """Create sample question mocks."""
        q1 = Mock(spec=Question)
        q1.id = "q_1"
        q1.question_text = "What is Newton's first law?"
        
        q2 = Mock(spec=Question)
        q2.id = "q_2"
        q2.question_text = "What is Newton's second law?"
        
        q3 = Mock(spec=Question)
        q3.id = "q_3"
        q3.question_text = "What is the speed of light?"
        
        return [q1, q2, q3]

    def test_pattern_search_wildcard(self, sample_questions: List[Mock]) -> None:
        """Test pattern search with wildcard."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.search_questions_by_pattern("Newton*law")
        
        assert len(result) == 2

    def test_pattern_search_no_match(self, sample_questions: List[Mock]) -> None:
        """Test pattern search with no matches."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.search_questions_by_pattern("Einstein")
        
        assert len(result) == 0

    def test_pattern_search_error(self) -> None:
        """Test pattern search error handling."""
        mock_repo = Mock()
        mock_repo.get_all.side_effect = Exception("Pattern error")
        
        service = QuestionService(question_repository=mock_repo)
        
        with pytest.raises(QuestionError):
            service.search_questions_by_pattern("test*")


class TestFuzzySearchQuestions:
    """Unit tests for fuzzy_search_questions method."""

    @pytest.fixture
    def sample_questions(self) -> List[Mock]:
        """Create sample question mocks."""
        q1 = Mock(spec=Question)
        q1.id = "q_1"
        q1.question_text = "What is Newton's first law?"
        
        q2 = Mock(spec=Question)
        q2.id = "q_2"
        q2.question_text = "What is the speed of light?"
        
        return [q1, q2]

    def test_fuzzy_search_high_threshold(self, sample_questions: List[Mock]) -> None:
        """Test fuzzy search with high threshold."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.fuzzy_search_questions("What is Newton's first law?", threshold=0.9)
        
        assert len(result) >= 1

    def test_fuzzy_search_low_threshold(self, sample_questions: List[Mock]) -> None:
        """Test fuzzy search with low threshold."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.fuzzy_search_questions("What is", threshold=0.3)
        
        assert len(result) == 2

    def test_fuzzy_search_error(self) -> None:
        """Test fuzzy search error handling."""
        mock_repo = Mock()
        mock_repo.get_all.side_effect = Exception("Fuzzy error")
        
        service = QuestionService(question_repository=mock_repo)
        
        with pytest.raises(QuestionError):
            service.fuzzy_search_questions("test")


class TestSearchQuestionsWithFilters:
    """Unit tests for search_questions_with_filters method."""

    @pytest.fixture
    def sample_questions(self) -> List[Mock]:
        """Create sample question mocks."""
        q1 = Mock(spec=Question)
        q1.id = "q_1"
        q1.topic = "Physics"
        q1.difficulty = "Easy"
        q1.question_text = "What is Newton's first law?"
        
        q2 = Mock(spec=Question)
        q2.id = "q_2"
        q2.topic = "Physics"
        q2.difficulty = "Hard"
        q2.question_text = "What is the speed of light?"
        
        q3 = Mock(spec=Question)
        q3.id = "q_3"
        q3.topic = "Chemistry"
        q3.difficulty = "Easy"
        q3.question_text = "What is H2O?"
        
        return [q1, q2, q3]

    def test_filter_by_topic(self, sample_questions: List[Mock]) -> None:
        """Test filtering by topic only."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.search_questions_with_filters(topic="Physics")
        
        assert len(result) == 2

    def test_filter_by_difficulty(self, sample_questions: List[Mock]) -> None:
        """Test filtering by difficulty only."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.search_questions_with_filters(difficulty="Easy")
        
        assert len(result) == 2

    def test_filter_by_topic_and_difficulty(self, sample_questions: List[Mock]) -> None:
        """Test filtering by topic and difficulty."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.search_questions_with_filters(topic="Physics", difficulty="Easy")
        
        assert len(result) == 1
        assert result[0].id == "q_1"

    def test_filter_with_search_text(self, sample_questions: List[Mock]) -> None:
        """Test filtering with search text."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.search_questions_with_filters(search_text="Newton")
        
        assert len(result) == 1
        assert result[0].id == "q_1"

    def test_filter_error_handling(self) -> None:
        """Test error handling in search_questions_with_filters."""
        mock_repo = Mock()
        mock_repo.get_all.side_effect = Exception("Filter error")
        
        service = QuestionService(question_repository=mock_repo)
        
        with pytest.raises(QuestionError):
            service.search_questions_with_filters(topic="Physics")


class TestAdvancedSearchQuestions:
    """Unit tests for advanced_search_questions method."""

    @pytest.fixture
    def sample_questions(self) -> List[Mock]:
        """Create sample question mocks."""
        q1 = Mock(spec=Question)
        q1.id = "physics_1"
        q1.topic = "Physics"
        q1.difficulty = "Easy"
        q1.question_text = "What is Newton's first law?"
        q1.option1 = "A"
        q1.option2 = "B"
        q1.option3 = "C"
        q1.option4 = "D"
        
        q2 = Mock(spec=Question)
        q2.id = "physics_2"
        q2.topic = "Physics"
        q2.difficulty = "Hard"
        q2.question_text = "What is the speed of light?"
        q2.option1 = "A"
        q2.option2 = "B"
        q2.option3 = "C"
        q2.option4 = "D"
        
        q3 = Mock(spec=Question)
        q3.id = "chemistry_1"
        q3.topic = "Chemistry"
        q3.difficulty = "Easy"
        q3.question_text = "What is H2O?"
        q3.option1 = "A"
        q3.option2 = "B"
        q3.option3 = "C"
        q3.option4 = "D"
        
        return [q1, q2, q3]

    def test_advanced_search_by_topic(self, sample_questions: List[Mock]) -> None:
        """Test advanced search by topic."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.advanced_search_questions({"topic": "Physics"})
        
        assert len(result) == 2

    def test_advanced_search_by_difficulty(self, sample_questions: List[Mock]) -> None:
        """Test advanced search by difficulty."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.advanced_search_questions({"difficulty": "Easy"})
        
        assert len(result) == 2

    def test_advanced_search_by_text_contains(self, sample_questions: List[Mock]) -> None:
        """Test advanced search by text contains."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.advanced_search_questions({"text_contains": "Newton"})
        
        assert len(result) == 1

    def test_advanced_search_by_id_pattern(self, sample_questions: List[Mock]) -> None:
        """Test advanced search by ID pattern."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.advanced_search_questions({"id_pattern": "physics"})
        
        assert len(result) == 2

    def test_advanced_search_has_options(self, sample_questions: List[Mock]) -> None:
        """Test advanced search with has_options filter."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.advanced_search_questions({"has_options": True})
        
        assert len(result) == 3

    def test_advanced_search_multiple_criteria(self, sample_questions: List[Mock]) -> None:
        """Test advanced search with multiple criteria."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.advanced_search_questions({
            "topic": "Physics",
            "difficulty": "Easy"
        })
        
        assert len(result) == 1

    def test_advanced_search_error(self) -> None:
        """Test advanced search error handling."""
        mock_repo = Mock()
        mock_repo.get_all.side_effect = Exception("Search error")
        
        service = QuestionService(question_repository=mock_repo)
        
        with pytest.raises(QuestionError):
            service.advanced_search_questions({"topic": "Physics"})


class TestFilterQuestionsByComplexCriteria:
    """Unit tests for filter_questions_by_complex_criteria method."""

    @pytest.fixture
    def sample_questions(self) -> List[Mock]:
        """Create sample question mocks."""
        q1 = Mock(spec=Question)
        q1.id = "physics_1"
        q1.topic = "Physics"
        q1.difficulty = "Easy"
        
        q2 = Mock(spec=Question)
        q2.id = "chemistry_1"
        q2.topic = "Chemistry"
        q2.difficulty = "Medium"
        
        q3 = Mock(spec=Question)
        q3.id = "math_1"
        q3.topic = "Math"
        q3.difficulty = "Hard"
        
        return [q1, q2, q3]

    def test_filter_topic_all(self, sample_questions: List[Mock]) -> None:
        """Test filtering with 'all' topic."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.filter_questions_by_complex_criteria(topic="all")
        
        assert len(result) == 3

    def test_filter_topic_science(self, sample_questions: List[Mock]) -> None:
        """Test filtering with 'science' topic."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.filter_questions_by_complex_criteria(topic="science")
        
        assert len(result) == 2  # Physics and Chemistry

    def test_filter_topic_mathematics(self, sample_questions: List[Mock]) -> None:
        """Test filtering with 'mathematics' topic."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.filter_questions_by_complex_criteria(topic="mathematics")
        
        assert len(result) == 1  # Math only

    def test_filter_difficulty_beginner(self, sample_questions: List[Mock]) -> None:
        """Test filtering with 'beginner' difficulty."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.filter_questions_by_complex_criteria(difficulty="beginner")
        
        assert len(result) == 1  # Easy only

    def test_filter_difficulty_advanced(self, sample_questions: List[Mock]) -> None:
        """Test filtering with 'advanced' difficulty."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.filter_questions_by_complex_criteria(difficulty="advanced")
        
        assert len(result) == 1  # Hard only

    def test_filter_difficulty_intermediate(self, sample_questions: List[Mock]) -> None:
        """Test filtering with 'intermediate' difficulty."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.filter_questions_by_complex_criteria(difficulty="intermediate")
        
        assert len(result) == 1  # Medium only

    def test_filter_sort_by_topic(self, sample_questions: List[Mock]) -> None:
        """Test sorting by topic."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.filter_questions_by_complex_criteria(sort_by="topic")
        
        assert len(result) == 3

    def test_filter_sort_by_difficulty(self, sample_questions: List[Mock]) -> None:
        """Test sorting by difficulty."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.filter_questions_by_complex_criteria(sort_by="difficulty")
        
        assert len(result) == 3

    def test_filter_sort_by_random(self, sample_questions: List[Mock]) -> None:
        """Test sorting by random."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.filter_questions_by_complex_criteria(sort_by="random")
        
        assert len(result) == 3

    def test_filter_with_question_count(self, sample_questions: List[Mock]) -> None:
        """Test filtering with question count limit."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.filter_questions_by_complex_criteria(question_count=2)
        
        assert len(result) == 2

    def test_filter_with_zero_question_count(self, sample_questions: List[Mock]) -> None:
        """Test filtering with zero question count."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.filter_questions_by_complex_criteria(question_count=0)
        
        assert len(result) == 0

    def test_filter_exact_topic_match(self, sample_questions: List[Mock]) -> None:
        """Test filtering with exact topic match."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.filter_questions_by_complex_criteria(topic="Physics")
        
        assert len(result) == 1

    def test_filter_exact_difficulty_match(self, sample_questions: List[Mock]) -> None:
        """Test filtering with exact difficulty match."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.filter_questions_by_complex_criteria(difficulty="Easy")
        
        assert len(result) == 1

    def test_filter_difficulty_all(self, sample_questions: List[Mock]) -> None:
        """Test filtering with 'all' difficulty."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = sample_questions
        
        service = QuestionService(question_repository=mock_repo)
        result = service.filter_questions_by_complex_criteria(difficulty="all")
        
        assert len(result) == 3

    def test_filter_error_handling(self) -> None:
        """Test error handling in filter_questions_by_complex_criteria."""
        mock_repo = Mock()
        mock_repo.get_all.side_effect = Exception("Filter error")
        
        service = QuestionService(question_repository=mock_repo)
        
        with pytest.raises(QuestionError):
            service.filter_questions_by_complex_criteria()


class TestDetermineQuestionComplexity:
    """Unit tests for determine_question_complexity method."""

    def test_physics_easy(self) -> None:
        """Test complexity for easy physics question."""
        mock_repo = Mock()
        service = QuestionService(question_repository=mock_repo)
        
        question = Mock(spec=Question)
        question.topic = "Physics"
        question.difficulty = "Easy"
        question.question_text = "What is Newton's first law?"
        
        result = service.determine_question_complexity(question)
        
        assert result == "Basic Physics"

    def test_physics_medium_mechanics(self) -> None:
        """Test complexity for medium physics mechanics question."""
        mock_repo = Mock()
        service = QuestionService(question_repository=mock_repo)
        
        question = Mock(spec=Question)
        question.topic = "Physics"
        question.difficulty = "Medium"
        question.question_text = "What is the mechanics of a pendulum?"
        
        result = service.determine_question_complexity(question)
        
        assert result == "Intermediate Mechanics"

    def test_physics_hard_quantum(self) -> None:
        """Test complexity for hard physics quantum question."""
        mock_repo = Mock()
        service = QuestionService(question_repository=mock_repo)
        
        question = Mock(spec=Question)
        question.topic = "Physics"
        question.difficulty = "Hard"
        question.question_text = "Explain quantum entanglement."
        
        result = service.determine_question_complexity(question)
        
        assert result == "Advanced Quantum Physics"

    def test_chemistry_easy(self) -> None:
        """Test complexity for easy chemistry question."""
        mock_repo = Mock()
        service = QuestionService(question_repository=mock_repo)
        
        question = Mock(spec=Question)
        question.topic = "Chemistry"
        question.difficulty = "Easy"
        question.question_text = "What is H2O?"
        
        result = service.determine_question_complexity(question)
        
        assert result == "Basic Chemistry"

    def test_chemistry_medium_organic(self) -> None:
        """Test complexity for medium organic chemistry question."""
        mock_repo = Mock()
        service = QuestionService(question_repository=mock_repo)
        
        question = Mock(spec=Question)
        question.topic = "Chemistry"
        question.difficulty = "Medium"
        question.question_text = "What is organic chemistry?"
        
        result = service.determine_question_complexity(question)
        
        assert result == "Intermediate Organic Chemistry"

    def test_math_easy(self) -> None:
        """Test complexity for easy math question."""
        mock_repo = Mock()
        service = QuestionService(question_repository=mock_repo)
        
        question = Mock(spec=Question)
        question.topic = "Math"
        question.difficulty = "Easy"
        question.question_text = "What is 2+2?"
        
        result = service.determine_question_complexity(question)
        
        assert result == "Basic Mathematics"

    def test_math_medium_algebra(self) -> None:
        """Test complexity for medium algebra question."""
        mock_repo = Mock()
        service = QuestionService(question_repository=mock_repo)
        
        question = Mock(spec=Question)
        question.topic = "Math"
        question.difficulty = "Medium"
        question.question_text = "Solve this algebra equation."
        
        result = service.determine_question_complexity(question)
        
        assert result == "Intermediate Algebra"

    def test_unknown_topic(self) -> None:
        """Test complexity for unknown topic."""
        mock_repo = Mock()
        service = QuestionService(question_repository=mock_repo)
        
        question = Mock(spec=Question)
        question.topic = "Biology"
        question.difficulty = "Easy"
        question.question_text = "What is DNA?"
        
        result = service.determine_question_complexity(question)
        
        assert result == "Unknown Complexity"


class TestProcessQuestionsWithLoops:
    """Unit tests for process_questions_with_loops method."""

    @pytest.fixture
    def sample_questions(self) -> List[Mock]:
        """Create sample question mocks."""
        q1 = Mock(spec=Question)
        q1.id = "q_1"
        q1.topic = "Physics"
        q1.difficulty = "Easy"
        q1.question_text = "What is Newton's first law?"
        q1.option1 = "A"
        q1.option2 = "B"
        q1.option3 = "C"
        q1.option4 = "D"
        
        q2 = Mock(spec=Question)
        q2.id = "q_2"
        q2.topic = "Physics"
        q2.difficulty = "Hard"
        q2.question_text = "What is the speed of light?"
        q2.option1 = "A"
        q2.option2 = "B"
        q2.option3 = "C"
        q2.option4 = "D"
        
        q3 = Mock(spec=Question)
        q3.id = "q_3"
        q3.topic = "Chemistry"
        q3.difficulty = "Easy"
        q3.question_text = "What is H2O?"
        q3.option1 = "A"
        q3.option2 = "B"
        q3.option3 = "C"
        q3.option4 = "D"
        
        return [q1, q2, q3]

    def test_process_questions_total_count(self, sample_questions: List[Mock]) -> None:
        """Test total count in process results."""
        mock_repo = Mock()
        service = QuestionService(question_repository=mock_repo)
        
        result = service.process_questions_with_loops(sample_questions)
        
        assert result["total_count"] == 3

    def test_process_questions_topic_counts(self, sample_questions: List[Mock]) -> None:
        """Test topic counts in process results."""
        mock_repo = Mock()
        service = QuestionService(question_repository=mock_repo)
        
        result = service.process_questions_with_loops(sample_questions)
        
        assert result["topic_counts"]["Physics"] == 2
        assert result["topic_counts"]["Chemistry"] == 1

    def test_process_questions_difficulty_counts(self, sample_questions: List[Mock]) -> None:
        """Test difficulty counts in process results."""
        mock_repo = Mock()
        service = QuestionService(question_repository=mock_repo)
        
        result = service.process_questions_with_loops(sample_questions)
        
        assert result["difficulty_counts"]["Easy"] == 2
        assert result["difficulty_counts"]["Hard"] == 1

    def test_process_questions_average_length(self, sample_questions: List[Mock]) -> None:
        """Test average question length in process results."""
        mock_repo = Mock()
        service = QuestionService(question_repository=mock_repo)
        
        result = service.process_questions_with_loops(sample_questions)
        
        assert result["average_question_length"] > 0

    def test_process_questions_with_options(self, sample_questions: List[Mock]) -> None:
        """Test questions with options in process results."""
        mock_repo = Mock()
        service = QuestionService(question_repository=mock_repo)
        
        result = service.process_questions_with_loops(sample_questions)
        
        assert len(result["questions_with_options"]) == 3

    def test_process_empty_questions(self) -> None:
        """Test processing empty question list."""
        mock_repo = Mock()
        service = QuestionService(question_repository=mock_repo)
        
        result = service.process_questions_with_loops([])
        
        assert result["total_count"] == 0
        assert result["average_question_length"] == 0.0
