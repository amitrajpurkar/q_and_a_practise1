"""
Unit tests for question repository.

Tests question data access operations.
"""

import pytest
from unittest.mock import Mock, MagicMock
from typing import List, Optional

from src.services.question_repository import QuestionRepository
from src.services.interfaces import QuestionFilter
from src.models.question import Question
from src.models.question_bank import QuestionBank
from src.utils.exceptions import QuestionError


class TestQuestionRepositoryInitialization:
    """Unit tests for QuestionRepository initialization."""

    def test_init_with_question_bank(self) -> None:
        """Test initialization with question bank."""
        mock_bank = Mock(spec=QuestionBank)
        
        repo = QuestionRepository(question_bank=mock_bank)
        
        assert repo.question_bank == mock_bank

    def test_init_with_custom_logger(self) -> None:
        """Test initialization with custom logger."""
        mock_bank = Mock(spec=QuestionBank)
        mock_logger = Mock()
        
        repo = QuestionRepository(question_bank=mock_bank, logger=mock_logger)
        
        assert repo.logger == mock_logger


class TestGetById:
    """Unit tests for get_by_id method."""

    @pytest.fixture
    def sample_question(self) -> Question:
        """Create a sample question."""
        return Question(
            id="q_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            option1="Inertia",
            option2="F=ma",
            option3="Action-reaction",
            option4="Gravity",
            correct_answer="Inertia",
            difficulty="Easy",
            tag="Physics-Easy"
        )

    @pytest.fixture
    def repo(self, sample_question: Question) -> QuestionRepository:
        """Create a repository for testing."""
        mock_bank = Mock(spec=QuestionBank)
        mock_bank.get_question_by_id.return_value = sample_question
        return QuestionRepository(question_bank=mock_bank)

    def test_get_by_id_found(self, repo: QuestionRepository, sample_question: Question) -> None:
        """Test get_by_id when question is found."""
        result = repo.get_by_id("q_1")
        
        assert result is not None
        assert result.id == "q_1"

    def test_get_by_id_not_found(self) -> None:
        """Test get_by_id when question is not found."""
        mock_bank = Mock(spec=QuestionBank)
        mock_bank.get_question_by_id.return_value = None
        repo = QuestionRepository(question_bank=mock_bank)
        
        result = repo.get_by_id("nonexistent")
        
        assert result is None

    def test_get_by_id_error_raises_question_error(self) -> None:
        """Test get_by_id raises QuestionError on failure."""
        mock_bank = Mock(spec=QuestionBank)
        mock_bank.get_question_by_id.side_effect = Exception("Database error")
        repo = QuestionRepository(question_bank=mock_bank)
        
        with pytest.raises(QuestionError):
            repo.get_by_id("q_1")


class TestGetAll:
    """Unit tests for get_all method."""

    @pytest.fixture
    def sample_questions(self) -> List[Question]:
        """Create sample questions."""
        return [
            Question(
                id="q_1",
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
                id="q_2",
                topic="Chemistry",
                question_text="What is H2O?",
                option1="Water",
                option2="Oxygen",
                option3="Hydrogen",
                option4="Carbon",
                correct_answer="Water",
                difficulty="Easy",
                tag="Chemistry-Easy"
            )
        ]

    @pytest.fixture
    def repo(self, sample_questions: List[Question]) -> QuestionRepository:
        """Create a repository for testing."""
        mock_bank = Mock(spec=QuestionBank)
        mock_bank.get_all_questions.return_value = sample_questions
        return QuestionRepository(question_bank=mock_bank)

    def test_get_all_returns_questions(self, repo: QuestionRepository) -> None:
        """Test get_all returns all questions."""
        result = repo.get_all()
        
        assert len(result) == 2

    def test_get_all_empty(self) -> None:
        """Test get_all with no questions."""
        mock_bank = Mock(spec=QuestionBank)
        mock_bank.get_all_questions.return_value = []
        repo = QuestionRepository(question_bank=mock_bank)
        
        result = repo.get_all()
        
        assert result == []

    def test_get_all_error_raises_question_error(self) -> None:
        """Test get_all raises QuestionError on failure."""
        mock_bank = Mock(spec=QuestionBank)
        mock_bank.get_all_questions.side_effect = Exception("Database error")
        repo = QuestionRepository(question_bank=mock_bank)
        
        with pytest.raises(QuestionError):
            repo.get_all()


class TestFilter:
    """Unit tests for filter method."""

    @pytest.fixture
    def sample_questions(self) -> List[Question]:
        """Create sample questions."""
        return [
            Question(
                id="q_1",
                topic="Physics",
                question_text="What is Newton's first law?",
                option1="Inertia",
                option2="F=ma",
                option3="Action-reaction",
                option4="Gravity",
                correct_answer="Inertia",
                difficulty="Easy",
                tag="Physics-Easy"
            )
        ]

    @pytest.fixture
    def repo(self, sample_questions: List[Question]) -> QuestionRepository:
        """Create a repository for testing."""
        mock_bank = Mock(spec=QuestionBank)
        mock_bank.filter_questions.return_value = sample_questions
        return QuestionRepository(question_bank=mock_bank)

    def test_filter_by_topic(self, repo: QuestionRepository) -> None:
        """Test filtering by topic."""
        criteria = QuestionFilter(topic="Physics")
        
        result = repo.filter(criteria)
        
        assert len(result) == 1

    def test_filter_by_difficulty(self, repo: QuestionRepository) -> None:
        """Test filtering by difficulty."""
        criteria = QuestionFilter(difficulty="Easy")
        
        result = repo.filter(criteria)
        
        assert len(result) == 1

    def test_filter_with_exclude_ids(self, repo: QuestionRepository) -> None:
        """Test filtering with excluded IDs."""
        criteria = QuestionFilter(topic="Physics", exclude_ids=["q_2"])
        
        result = repo.filter(criteria)
        
        assert len(result) == 1

    def test_filter_error_raises_question_error(self) -> None:
        """Test filter raises QuestionError on failure."""
        mock_bank = Mock(spec=QuestionBank)
        mock_bank.filter_questions.side_effect = Exception("Filter error")
        repo = QuestionRepository(question_bank=mock_bank)
        
        with pytest.raises(QuestionError):
            repo.filter(QuestionFilter(topic="Physics"))


class TestGetRandom:
    """Unit tests for get_random method."""

    @pytest.fixture
    def sample_question(self) -> Question:
        """Create a sample question."""
        return Question(
            id="q_1",
            topic="Physics",
            question_text="What is Newton's first law?",
            option1="Inertia",
            option2="F=ma",
            option3="Action-reaction",
            option4="Gravity",
            correct_answer="Inertia",
            difficulty="Easy",
            tag="Physics-Easy"
        )

    @pytest.fixture
    def repo(self, sample_question: Question) -> QuestionRepository:
        """Create a repository for testing."""
        mock_bank = Mock(spec=QuestionBank)
        mock_bank.get_random_question.return_value = sample_question
        return QuestionRepository(question_bank=mock_bank)

    def test_get_random_found(self, repo: QuestionRepository) -> None:
        """Test get_random when question is found."""
        criteria = QuestionFilter(topic="Physics")
        
        result = repo.get_random(criteria)
        
        assert result is not None
        assert result.id == "q_1"

    def test_get_random_not_found(self) -> None:
        """Test get_random when no question matches."""
        mock_bank = Mock(spec=QuestionBank)
        mock_bank.get_random_question.return_value = None
        repo = QuestionRepository(question_bank=mock_bank)
        
        result = repo.get_random(QuestionFilter(topic="Physics"))
        
        assert result is None

    def test_get_random_error_raises_question_error(self) -> None:
        """Test get_random raises QuestionError on failure."""
        mock_bank = Mock(spec=QuestionBank)
        mock_bank.get_random_question.side_effect = Exception("Random error")
        repo = QuestionRepository(question_bank=mock_bank)
        
        with pytest.raises(QuestionError):
            repo.get_random(QuestionFilter(topic="Physics"))


class TestCountByCriteria:
    """Unit tests for count_by_criteria method."""

    @pytest.fixture
    def repo(self) -> QuestionRepository:
        """Create a repository for testing."""
        mock_bank = Mock(spec=QuestionBank)
        mock_bank.count_questions.return_value = 5
        return QuestionRepository(question_bank=mock_bank)

    def test_count_by_criteria(self, repo: QuestionRepository) -> None:
        """Test count_by_criteria returns count."""
        criteria = QuestionFilter(topic="Physics")
        
        result = repo.count_by_criteria(criteria)
        
        assert result == 5

    def test_count_by_criteria_zero(self) -> None:
        """Test count_by_criteria returns zero."""
        mock_bank = Mock(spec=QuestionBank)
        mock_bank.count_questions.return_value = 0
        repo = QuestionRepository(question_bank=mock_bank)
        
        result = repo.count_by_criteria(QuestionFilter(topic="Physics"))
        
        assert result == 0

    def test_count_by_criteria_error_raises_question_error(self) -> None:
        """Test count_by_criteria raises QuestionError on failure."""
        mock_bank = Mock(spec=QuestionBank)
        mock_bank.count_questions.side_effect = Exception("Count error")
        repo = QuestionRepository(question_bank=mock_bank)
        
        with pytest.raises(QuestionError):
            repo.count_by_criteria(QuestionFilter(topic="Physics"))


class TestGetAvailableTopics:
    """Unit tests for get_available_topics method."""

    @pytest.fixture
    def repo(self) -> QuestionRepository:
        """Create a repository for testing."""
        mock_bank = Mock(spec=QuestionBank)
        mock_bank.get_available_topics.return_value = ["Physics", "Chemistry", "Math"]
        return QuestionRepository(question_bank=mock_bank)

    def test_get_available_topics(self, repo: QuestionRepository) -> None:
        """Test get_available_topics returns topics."""
        result = repo.get_available_topics()
        
        assert len(result) == 3
        assert "Physics" in result

    def test_get_available_topics_error_raises_question_error(self) -> None:
        """Test get_available_topics raises QuestionError on failure."""
        mock_bank = Mock(spec=QuestionBank)
        mock_bank.get_available_topics.side_effect = Exception("Topics error")
        repo = QuestionRepository(question_bank=mock_bank)
        
        with pytest.raises(QuestionError):
            repo.get_available_topics()


class TestGetAvailableDifficulties:
    """Unit tests for get_available_difficulties method."""

    @pytest.fixture
    def repo(self) -> QuestionRepository:
        """Create a repository for testing."""
        mock_bank = Mock(spec=QuestionBank)
        mock_bank.get_available_difficulties.return_value = ["Easy", "Medium", "Hard"]
        return QuestionRepository(question_bank=mock_bank)

    def test_get_available_difficulties(self, repo: QuestionRepository) -> None:
        """Test get_available_difficulties returns difficulties."""
        result = repo.get_available_difficulties()
        
        assert len(result) == 3
        assert "Easy" in result

    def test_get_available_difficulties_error_raises_question_error(self) -> None:
        """Test get_available_difficulties raises QuestionError on failure."""
        mock_bank = Mock(spec=QuestionBank)
        mock_bank.get_available_difficulties.side_effect = Exception("Difficulties error")
        repo = QuestionRepository(question_bank=mock_bank)
        
        with pytest.raises(QuestionError):
            repo.get_available_difficulties()


class TestSave:
    """Unit tests for save method."""

    def test_save_raises_not_implemented(self) -> None:
        """Test save raises NotImplementedError."""
        mock_bank = Mock(spec=QuestionBank)
        repo = QuestionRepository(question_bank=mock_bank)
        
        mock_question = Mock(spec=Question)
        
        with pytest.raises(NotImplementedError):
            repo.save(mock_question)
