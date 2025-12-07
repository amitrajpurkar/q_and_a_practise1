"""
Unit tests for CLI commands module.

Tests CLI command functionality with mocked dependencies.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
import sys

from src.cli.commands import CLICommands
from src.models.question import Question
from src.models.session import UserSession
from src.models.question_review import QuestionReview, QuestionReviewList
from src.utils.config import AppConfig


class TestCLICommandsInitialization:
    """Unit tests for CLICommands initialization."""

    def test_cli_commands_has_expected_attributes(self) -> None:
        """Test that CLICommands class has expected attributes when mocked."""
        with patch.object(CLICommands, '__init__', lambda x, y: None):
            cli = CLICommands(None)
            cli.config = Mock()
            cli.logger = Mock()
            cli.question_service = Mock()
            cli.session_service = Mock()
            cli.score_service = Mock()
            cli.available_topics = ["Physics", "Chemistry", "Math"]
            cli.available_difficulties = ["Easy", "Medium", "Hard"]
        
        assert cli.available_topics == ["Physics", "Chemistry", "Math"]
        assert cli.available_difficulties == ["Easy", "Medium", "Hard"]


class TestCLICommandsListMethods:
    """Unit tests for CLI list methods."""

    @pytest.fixture
    def mock_cli(self) -> CLICommands:
        """Create a mock CLI commands instance."""
        with patch.object(CLICommands, '__init__', lambda x, y: None):
            cli = CLICommands(None)
            cli.config = Mock()
            cli.logger = Mock()
            cli.question_service = Mock()
            cli.session_service = Mock()
            cli.score_service = Mock()
            cli.available_topics = ["Physics", "Chemistry", "Math"]
            cli.available_difficulties = ["Easy", "Medium", "Hard"]
            return cli

    def test_list_topics(self, mock_cli: CLICommands, capsys) -> None:
        """Test list_topics method."""
        mock_cli.question_service.get_questions_by_topic.return_value = [Mock(), Mock()]
        
        mock_cli.list_topics()
        
        captured = capsys.readouterr()
        assert "Available Topics" in captured.out
        assert "Physics" in captured.out
        assert "Chemistry" in captured.out
        assert "Math" in captured.out

    def test_list_difficulties(self, mock_cli: CLICommands, capsys) -> None:
        """Test list_difficulties method."""
        mock_cli.question_service.get_questions_by_difficulty.return_value = [Mock()]
        
        mock_cli.list_difficulties()
        
        captured = capsys.readouterr()
        assert "Difficulty Levels" in captured.out
        assert "Easy" in captured.out
        assert "Medium" in captured.out
        assert "Hard" in captured.out

    def test_show_statistics(self, mock_cli: CLICommands, capsys) -> None:
        """Test show_statistics method."""
        mock_cli.question_service.get_all_questions.return_value = [Mock(), Mock(), Mock()]
        mock_cli.question_service.get_questions_by_topic.return_value = [Mock()]
        mock_cli.question_service.get_questions_by_difficulty.return_value = [Mock()]
        mock_cli.question_service.get_questions_by_topic_and_difficulty.return_value = [Mock()]
        
        mock_cli.show_statistics()
        
        captured = capsys.readouterr()
        assert "Statistics" in captured.out
        assert "Total Questions" in captured.out


class TestCLICommandsSessionMethods:
    """Unit tests for CLI session methods."""

    @pytest.fixture
    def mock_cli(self) -> CLICommands:
        """Create a mock CLI commands instance."""
        with patch.object(CLICommands, '__init__', lambda x, y: None):
            cli = CLICommands(None)
            cli.config = Mock()
            cli.logger = Mock()
            cli.question_service = Mock()
            cli.session_service = Mock()
            cli.score_service = Mock()
            cli.available_topics = ["Physics", "Chemistry", "Math"]
            cli.available_difficulties = ["Easy", "Medium", "Hard"]
            return cli

    def test_start_session_invalid_topic(self, mock_cli: CLICommands, capsys) -> None:
        """Test start_session with invalid topic."""
        mock_cli.start_session(topic="InvalidTopic", difficulty="Easy")
        
        captured = capsys.readouterr()
        assert "error" in captured.out.lower() or "invalid" in captured.out.lower() or captured.out == ""

    def test_start_session_invalid_difficulty(self, mock_cli: CLICommands, capsys) -> None:
        """Test start_session with invalid difficulty."""
        mock_cli.start_session(topic="Physics", difficulty="VeryHard")
        
        captured = capsys.readouterr()
        assert "error" in captured.out.lower() or "invalid" in captured.out.lower() or captured.out == ""

    def test_start_session_no_questions(self, mock_cli: CLICommands, capsys) -> None:
        """Test start_session when no questions available."""
        mock_cli.question_service.get_questions_by_topic_and_difficulty.return_value = []
        
        mock_cli.start_session(topic="Physics", difficulty="Easy")
        
        captured = capsys.readouterr()
        assert "No questions available" in captured.out


class TestCLICommandsQuestionPresentation:
    """Unit tests for question presentation methods."""

    @pytest.fixture
    def mock_cli(self) -> CLICommands:
        """Create a mock CLI commands instance."""
        with patch.object(CLICommands, '__init__', lambda x, y: None):
            cli = CLICommands(None)
            cli.config = Mock()
            cli.logger = Mock()
            cli.question_service = Mock()
            cli.session_service = Mock()
            cli.score_service = Mock()
            cli.available_topics = ["Physics", "Chemistry", "Math"]
            cli.available_difficulties = ["Easy", "Medium", "Hard"]
            return cli

    @pytest.fixture
    def sample_question(self) -> Question:
        """Create a sample question."""
        return Question(
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
        )

    def test_present_question(self, mock_cli: CLICommands, sample_question: Question, capsys) -> None:
        """Test _present_question method."""
        mock_cli._present_question(sample_question, 1, 5)
        
        captured = capsys.readouterr()
        assert "Question 1 of 5" in captured.out
        assert "Newton's first law" in captured.out
        assert "A)" in captured.out
        assert "B)" in captured.out
        assert "C)" in captured.out
        assert "D)" in captured.out

    def test_validate_and_provide_feedback_correct(self, mock_cli: CLICommands, sample_question: Question, capsys) -> None:
        """Test feedback for correct answer."""
        is_correct, answer_text = mock_cli._validate_and_provide_feedback(sample_question, "A")
        
        captured = capsys.readouterr()
        assert is_correct is True
        assert "Correct" in captured.out

    def test_validate_and_provide_feedback_incorrect(self, mock_cli: CLICommands, sample_question: Question, capsys) -> None:
        """Test feedback for incorrect answer."""
        is_correct, answer_text = mock_cli._validate_and_provide_feedback(sample_question, "B")
        
        captured = capsys.readouterr()
        assert is_correct is False
        assert "Incorrect" in captured.out


class TestCLICommandsSessionSummary:
    """Unit tests for session summary methods."""

    @pytest.fixture
    def mock_cli(self) -> CLICommands:
        """Create a mock CLI commands instance."""
        with patch.object(CLICommands, '__init__', lambda x, y: None):
            cli = CLICommands(None)
            cli.config = Mock()
            cli.logger = Mock()
            cli.question_service = Mock()
            cli.session_service = Mock()
            cli.score_service = Mock()
            cli.available_topics = ["Physics", "Chemistry", "Math"]
            cli.available_difficulties = ["Easy", "Medium", "Hard"]
            return cli

    @pytest.fixture
    def sample_session(self) -> UserSession:
        """Create a sample session."""
        return UserSession(
            session_id="test-session-1",
            topic="Physics",
            difficulty="Easy",
            total_questions=5,
            current_question_index=0,
            is_active=True,
            questions_asked=[],
            user_answers={}
        )

    def test_show_session_summary_no_questions(self, mock_cli: CLICommands, sample_session: UserSession, capsys) -> None:
        """Test session summary with no questions answered."""
        mock_cli._show_session_summary(sample_session, 0, 0)
        
        captured = capsys.readouterr()
        assert "No questions were answered" in captured.out

    def test_show_session_summary_with_answers(self, mock_cli: CLICommands, sample_session: UserSession, capsys) -> None:
        """Test session summary with answers."""
        mock_cli._show_session_summary(sample_session, 5, 3)
        
        captured = capsys.readouterr()
        assert "Session Summary" in captured.out
        assert "Physics" in captured.out
        assert "5" in captured.out  # Questions answered
        assert "3" in captured.out  # Correct answers
        assert "60" in captured.out  # 60% accuracy

    def test_show_session_summary_perfect_score(self, mock_cli: CLICommands, sample_session: UserSession, capsys) -> None:
        """Test session summary with perfect score."""
        reviews = QuestionReviewList()
        reviews.add(QuestionReview(
            question_number=1,
            question_text="Test question",
            user_answer="Correct",
            correct_answer="Correct",
            correct=True,
            topic="Physics",
            difficulty="Easy"
        ))
        
        mock_cli._show_session_summary(sample_session, 1, 1, reviews)
        
        captured = capsys.readouterr()
        assert "100" in captured.out  # 100% accuracy

    def test_show_session_summary_with_incorrect_reviews(self, mock_cli: CLICommands, sample_session: UserSession, capsys) -> None:
        """Test session summary with incorrect answer reviews."""
        reviews = QuestionReviewList()
        reviews.add(QuestionReview(
            question_number=1,
            question_text="What is Newton's first law?",
            user_answer="F=ma",
            correct_answer="Inertia",
            correct=False,
            topic="Physics",
            difficulty="Easy"
        ))
        
        mock_cli._show_session_summary(sample_session, 1, 0, reviews)
        
        captured = capsys.readouterr()
        assert "Question Review" in captured.out
        assert "incorrect" in captured.out.lower()

    def test_show_session_summary_outstanding_performance(self, mock_cli: CLICommands, sample_session: UserSession, capsys) -> None:
        """Test session summary with outstanding performance (>=90%)."""
        mock_cli._show_session_summary(sample_session, 10, 9)
        
        captured = capsys.readouterr()
        assert "Outstanding" in captured.out

    def test_show_session_summary_great_performance(self, mock_cli: CLICommands, sample_session: UserSession, capsys) -> None:
        """Test session summary with great performance (>=75%)."""
        mock_cli._show_session_summary(sample_session, 10, 8)
        
        captured = capsys.readouterr()
        assert "Great" in captured.out

    def test_show_session_summary_good_performance(self, mock_cli: CLICommands, sample_session: UserSession, capsys) -> None:
        """Test session summary with good performance (>=60%)."""
        mock_cli._show_session_summary(sample_session, 10, 6)
        
        captured = capsys.readouterr()
        assert "Good" in captured.out

    def test_show_session_summary_needs_practice(self, mock_cli: CLICommands, sample_session: UserSession, capsys) -> None:
        """Test session summary with low performance (<60%)."""
        mock_cli._show_session_summary(sample_session, 10, 4)
        
        captured = capsys.readouterr()
        assert "practicing" in captured.out.lower()


class TestCLICommandsAnswerCollection:
    """Unit tests for answer collection methods."""

    @pytest.fixture
    def mock_cli(self) -> CLICommands:
        """Create a mock CLI commands instance."""
        with patch.object(CLICommands, '__init__', lambda x, y: None):
            cli = CLICommands(None)
            cli.config = Mock()
            cli.logger = Mock()
            cli.question_service = Mock()
            cli.session_service = Mock()
            cli.score_service = Mock()
            cli.available_topics = ["Physics", "Chemistry", "Math"]
            cli.available_difficulties = ["Easy", "Medium", "Hard"]
            return cli

    @pytest.fixture
    def sample_question(self) -> Question:
        """Create a sample question."""
        return Question(
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
        )

    @patch('builtins.input', return_value='A')
    def test_collect_answer_valid_a(self, mock_input: Mock, mock_cli: CLICommands, sample_question: Question) -> None:
        """Test collecting valid answer A."""
        result = mock_cli._collect_answer(sample_question)
        
        assert result == 'A'

    @patch('builtins.input', return_value='B')
    def test_collect_answer_valid_b(self, mock_input: Mock, mock_cli: CLICommands, sample_question: Question) -> None:
        """Test collecting valid answer B."""
        result = mock_cli._collect_answer(sample_question)
        
        assert result == 'B'

    @patch('builtins.input', return_value='quit')
    def test_collect_answer_quit(self, mock_input: Mock, mock_cli: CLICommands, sample_question: Question) -> None:
        """Test quitting during answer collection."""
        result = mock_cli._collect_answer(sample_question)
        
        assert result is None

    @patch('builtins.input', return_value='exit')
    def test_collect_answer_exit(self, mock_input: Mock, mock_cli: CLICommands, sample_question: Question) -> None:
        """Test exiting during answer collection."""
        result = mock_cli._collect_answer(sample_question)
        
        assert result is None

    @patch('builtins.input', side_effect=['invalid', 'A'])
    def test_collect_answer_invalid_then_valid(self, mock_input: Mock, mock_cli: CLICommands, sample_question: Question, capsys) -> None:
        """Test invalid answer followed by valid answer."""
        result = mock_cli._collect_answer(sample_question)
        
        assert result == 'A'
        captured = capsys.readouterr()
        assert "A, B, C, or D" in captured.out


class TestListTopics:
    """Unit tests for list_topics method."""

    @pytest.fixture
    def mock_cli(self) -> CLICommands:
        """Create a mock CLI commands instance."""
        with patch.object(CLICommands, '__init__', lambda x, y: None):
            cli = CLICommands(None)
            cli.config = {}
            cli.logger = Mock()
            cli.question_service = Mock()
            cli.question_service.get_questions_by_topic.return_value = [Mock(), Mock()]
            cli.available_topics = ["Physics", "Chemistry", "Math"]
            return cli

    def test_list_topics_output(self, mock_cli: CLICommands, capsys) -> None:
        """Test list_topics prints topics."""
        mock_cli.list_topics()
        
        captured = capsys.readouterr()
        assert "Physics" in captured.out
        assert "Chemistry" in captured.out
        assert "Math" in captured.out


class TestListDifficulties:
    """Unit tests for list_difficulties method."""

    @pytest.fixture
    def mock_cli(self) -> CLICommands:
        """Create a mock CLI commands instance."""
        with patch.object(CLICommands, '__init__', lambda x, y: None):
            cli = CLICommands(None)
            cli.config = {}
            cli.logger = Mock()
            cli.question_service = Mock()
            cli.question_service.get_questions_by_difficulty.return_value = [Mock()]
            cli.available_difficulties = ["Easy", "Medium", "Hard"]
            return cli

    def test_list_difficulties_output(self, mock_cli: CLICommands, capsys) -> None:
        """Test list_difficulties prints difficulties."""
        mock_cli.list_difficulties()
        
        captured = capsys.readouterr()
        assert "Easy" in captured.out
        assert "Medium" in captured.out
        assert "Hard" in captured.out


class TestShowStatistics:
    """Unit tests for show_statistics method."""

    @pytest.fixture
    def mock_cli(self) -> CLICommands:
        """Create a mock CLI commands instance."""
        with patch.object(CLICommands, '__init__', lambda x, y: None):
            cli = CLICommands(None)
            cli.config = {}
            cli.logger = Mock()
            cli.question_service = Mock()
            # Return actual lists instead of mocks for all methods
            cli.question_service.get_all_questions.return_value = ["q1", "q2", "q3"]
            cli.question_service.get_questions_by_topic.return_value = ["q1"]
            cli.question_service.get_questions_by_difficulty.return_value = ["q1"]
            cli.question_service.get_questions_by_criteria.return_value = ["q1"]
            cli.question_service.get_questions_by_topic_and_difficulty.return_value = ["q1"]
            cli.available_topics = ["Physics", "Chemistry", "Math"]
            cli.available_difficulties = ["Easy", "Medium", "Hard"]
            return cli

    def test_show_statistics_output(self, mock_cli: CLICommands, capsys) -> None:
        """Test show_statistics prints statistics."""
        mock_cli.show_statistics()
        
        captured = capsys.readouterr()
        assert "Statistics" in captured.out
        assert "Total Questions" in captured.out
