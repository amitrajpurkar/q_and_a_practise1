"""
Unit tests for CSV parser service.

Tests CSV file loading, validation, and data transformation.
"""

import pytest
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, List

from src.services.csv_parser import CSVParserService
from src.utils.exceptions import CSVParsingError, ValidationError


class TestCSVParserService:
    """Unit tests for CSV parser service."""

    @pytest.fixture
    def csv_parser(self) -> CSVParserService:
        """Create CSV parser service instance."""
        return CSVParserService()

    @pytest.fixture
    def valid_csv_content(self) -> str:
        """Create valid CSV content."""
        return """topic,question,option1,option2,option3,option4,answer,difficulty
Physics,What is Newton's first law of motion?,Inertia,F=ma,Action-reaction,Gravity,Inertia,Easy
Chemistry,What is the chemical formula for water?,H2O,CO2,NaCl,O2,H2O,Easy
Math,What is the value of pi approximately?,3.14,2.71,1.41,1.73,3.14,Medium
"""

    @pytest.fixture
    def valid_csv_file(self, valid_csv_content: str) -> str:
        """Create a temporary valid CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(valid_csv_content)
            return f.name

    def test_load_questions_from_valid_csv(self, csv_parser: CSVParserService, valid_csv_file: str) -> None:
        """Test loading questions from valid CSV file."""
        try:
            questions = csv_parser.load_questions_from_csv(valid_csv_file)
            
            assert len(questions) == 3
            assert questions[0]["topic"] == "Physics"
            assert questions[1]["topic"] == "Chemistry"
            assert questions[2]["topic"] == "Math"
        finally:
            # Cleanup
            os.unlink(valid_csv_file)

    def test_load_questions_validates_topic(self, csv_parser: CSVParserService, valid_csv_file: str) -> None:
        """Test that questions have valid topics."""
        try:
            questions = csv_parser.load_questions_from_csv(valid_csv_file)
            
            for question in questions:
                assert question["topic"] in ["Physics", "Chemistry", "Math"]
        finally:
            os.unlink(valid_csv_file)

    def test_load_questions_validates_difficulty(self, csv_parser: CSVParserService, valid_csv_file: str) -> None:
        """Test that questions have valid difficulties."""
        try:
            questions = csv_parser.load_questions_from_csv(valid_csv_file)
            
            for question in questions:
                assert question["difficulty"] in ["Easy", "Medium", "Hard"]
        finally:
            os.unlink(valid_csv_file)

    def test_load_questions_generates_ids(self, csv_parser: CSVParserService, valid_csv_file: str) -> None:
        """Test that questions get generated IDs."""
        try:
            questions = csv_parser.load_questions_from_csv(valid_csv_file)
            
            for question in questions:
                assert "id" in question
                assert question["id"] is not None
        finally:
            os.unlink(valid_csv_file)

    def test_load_questions_generates_tags(self, csv_parser: CSVParserService, valid_csv_file: str) -> None:
        """Test that questions get generated tags."""
        try:
            questions = csv_parser.load_questions_from_csv(valid_csv_file)
            
            assert questions[0]["tag"] == "Physics-Easy"
            assert questions[1]["tag"] == "Chemistry-Easy"
            assert questions[2]["tag"] == "Math-Medium"
        finally:
            os.unlink(valid_csv_file)

    def test_load_questions_file_not_found(self, csv_parser: CSVParserService) -> None:
        """Test error when CSV file not found."""
        with pytest.raises(CSVParsingError) as exc_info:
            csv_parser.load_questions_from_csv("/nonexistent/path/file.csv")
        
        assert "not found" in str(exc_info.value).lower()

    def test_load_questions_missing_columns(self, csv_parser: CSVParserService) -> None:
        """Test error when CSV is missing required columns."""
        csv_content = """topic,question
Physics,What is Newton's first law?
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            with pytest.raises(CSVParsingError) as exc_info:
                csv_parser.load_questions_from_csv(temp_file)
            
            assert "Missing required columns" in str(exc_info.value)
        finally:
            os.unlink(temp_file)

    def test_load_questions_empty_file(self, csv_parser: CSVParserService) -> None:
        """Test error when CSV file is empty."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("")
            temp_file = f.name
        
        try:
            with pytest.raises(CSVParsingError) as exc_info:
                csv_parser.load_questions_from_csv(temp_file)
            
            assert "empty" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_file)

    def test_load_questions_invalid_topic(self, csv_parser: CSVParserService) -> None:
        """Test that invalid topics are skipped."""
        csv_content = """topic,question,option1,option2,option3,option4,answer,difficulty
InvalidTopic,What is this?,A,B,C,D,A,Easy
Physics,What is Newton's first law of motion?,Inertia,F=ma,Action-reaction,Gravity,Inertia,Easy
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            questions = csv_parser.load_questions_from_csv(temp_file)
            # Invalid topic should be skipped
            assert len(questions) == 1
            assert questions[0]["topic"] == "Physics"
        finally:
            os.unlink(temp_file)

    def test_load_questions_invalid_difficulty(self, csv_parser: CSVParserService) -> None:
        """Test that invalid difficulties are skipped."""
        csv_content = """topic,question,option1,option2,option3,option4,answer,difficulty
Physics,What is Newton's first law of motion?,Inertia,F=ma,Action-reaction,Gravity,Inertia,VeryHard
Chemistry,What is the chemical formula for water?,H2O,CO2,NaCl,O2,H2O,Easy
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            questions = csv_parser.load_questions_from_csv(temp_file)
            # Invalid difficulty should be skipped
            assert len(questions) == 1
            assert questions[0]["topic"] == "Chemistry"
        finally:
            os.unlink(temp_file)

    def test_load_questions_empty_question_text(self, csv_parser: CSVParserService) -> None:
        """Test that empty question text is skipped."""
        csv_content = """topic,question,option1,option2,option3,option4,answer,difficulty
Physics,,Inertia,F=ma,Action-reaction,Gravity,Inertia,Easy
Chemistry,What is the chemical formula for water?,H2O,CO2,NaCl,O2,H2O,Easy
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            questions = csv_parser.load_questions_from_csv(temp_file)
            assert len(questions) == 1
        finally:
            os.unlink(temp_file)

    def test_load_questions_short_question_text(self, csv_parser: CSVParserService) -> None:
        """Test that short question text is skipped."""
        csv_content = """topic,question,option1,option2,option3,option4,answer,difficulty
Physics,Short?,A,B,C,D,A,Easy
Chemistry,What is the chemical formula for water?,H2O,CO2,NaCl,O2,H2O,Easy
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            questions = csv_parser.load_questions_from_csv(temp_file)
            assert len(questions) == 1
        finally:
            os.unlink(temp_file)

    def test_load_questions_answer_not_in_options(self, csv_parser: CSVParserService) -> None:
        """Test that answer not in options is skipped."""
        csv_content = """topic,question,option1,option2,option3,option4,answer,difficulty
Physics,What is Newton's first law of motion?,Inertia,F=ma,Action-reaction,Gravity,NotAnOption,Easy
Chemistry,What is the chemical formula for water?,H2O,CO2,NaCl,O2,H2O,Easy
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            questions = csv_parser.load_questions_from_csv(temp_file)
            assert len(questions) == 1
        finally:
            os.unlink(temp_file)

    def test_load_questions_duplicate_options(self, csv_parser: CSVParserService) -> None:
        """Test that duplicate options are skipped."""
        csv_content = """topic,question,option1,option2,option3,option4,answer,difficulty
Physics,What is Newton's first law of motion?,Inertia,Inertia,Action-reaction,Gravity,Inertia,Easy
Chemistry,What is the chemical formula for water?,H2O,CO2,NaCl,O2,H2O,Easy
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            questions = csv_parser.load_questions_from_csv(temp_file)
            assert len(questions) == 1
        finally:
            os.unlink(temp_file)


class TestCSVParserFiltering:
    """Tests for CSV parser filtering methods."""

    @pytest.fixture
    def csv_parser(self) -> CSVParserService:
        """Create CSV parser service instance."""
        return CSVParserService()

    @pytest.fixture
    def sample_questions(self) -> List[Dict[str, Any]]:
        """Create sample question dictionaries."""
        return [
            {"topic": "Physics", "difficulty": "Easy", "question_text": "Q1"},
            {"topic": "Physics", "difficulty": "Hard", "question_text": "Q2"},
            {"topic": "Chemistry", "difficulty": "Easy", "question_text": "Q3"},
            {"topic": "Math", "difficulty": "Medium", "question_text": "Q4"},
        ]

    def test_get_questions_by_topic(self, csv_parser: CSVParserService, sample_questions: List[Dict[str, Any]]) -> None:
        """Test filtering questions by topic."""
        result = csv_parser.get_questions_by_topic(sample_questions, "Physics")
        
        assert len(result) == 2
        assert all(q["topic"] == "Physics" for q in result)

    def test_get_questions_by_difficulty(self, csv_parser: CSVParserService, sample_questions: List[Dict[str, Any]]) -> None:
        """Test filtering questions by difficulty."""
        result = csv_parser.get_questions_by_difficulty(sample_questions, "Easy")
        
        assert len(result) == 2
        assert all(q["difficulty"] == "Easy" for q in result)

    def test_get_questions_by_criteria(self, csv_parser: CSVParserService, sample_questions: List[Dict[str, Any]]) -> None:
        """Test filtering questions by topic and difficulty."""
        result = csv_parser.get_questions_by_criteria(sample_questions, "Physics", "Easy")
        
        assert len(result) == 1
        assert result[0]["topic"] == "Physics"
        assert result[0]["difficulty"] == "Easy"


class TestCSVParserRecordConversion:
    """Tests for CSV parser record conversion methods."""

    @pytest.fixture
    def csv_parser(self) -> CSVParserService:
        """Create CSV parser service instance."""
        return CSVParserService()

    @pytest.fixture
    def sample_records(self) -> List[Dict[str, Any]]:
        """Create sample question records."""
        return [
            {
                "id": "q_001",
                "topic": "Physics",
                "question_text": "What is Newton's first law of motion?",
                "option1": "Inertia",
                "option2": "F=ma",
                "option3": "Action-reaction",
                "option4": "Gravity",
                "correct_answer": "Inertia",
                "difficulty": "Easy",
                "tag": "Physics-Easy"
            },
            {
                "id": "q_002",
                "topic": "Chemistry",
                "question_text": "What is the chemical formula for water?",
                "option1": "H2O",
                "option2": "CO2",
                "option3": "NaCl",
                "option4": "O2",
                "correct_answer": "H2O",
                "difficulty": "Easy",
                "tag": "Chemistry-Easy"
            }
        ]

    def test_records_to_objects(self, csv_parser: CSVParserService, sample_records: List[Dict[str, Any]]) -> None:
        """Test converting records to Question objects."""
        from src.models.question import Question
        
        questions = csv_parser.records_to_objects(sample_records)
        
        assert len(questions) == 2
        assert isinstance(questions[0], Question)
        assert questions[0].id == "q_001"
        assert questions[0].topic == "Physics"

    def test_objects_to_records(self, csv_parser: CSVParserService) -> None:
        """Test converting Question objects to records."""
        from src.models.question import Question
        
        questions = [
            Question(
                id="q_001",
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
        
        records = csv_parser.objects_to_records(questions)
        
        assert len(records) == 1
        assert records[0]["id"] == "q_001"
        assert records[0]["topic"] == "Physics"


class TestCSVParserFileIO:
    """Tests for CSV parser file I/O operations."""

    @pytest.fixture
    def csv_parser(self) -> CSVParserService:
        """Create CSV parser service instance."""
        return CSVParserService()

    @pytest.fixture
    def sample_questions(self) -> List:
        """Create sample Question objects."""
        from src.models.question import Question
        
        return [
            Question(
                id="q_001",
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
                id="q_002",
                topic="Chemistry",
                question_text="What is the chemical formula for water?",
                option1="H2O",
                option2="CO2",
                option3="NaCl",
                option4="O2",
                correct_answer="H2O",
                difficulty="Easy",
                tag="Chemistry-Easy"
            )
        ]

    def test_save_questions_to_csv(self, csv_parser: CSVParserService, sample_questions: List) -> None:
        """Test saving questions to CSV file."""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_file = f.name
        
        try:
            result = csv_parser.save_questions_to_csv(sample_questions, temp_file)
            
            assert result is True
            assert os.path.exists(temp_file)
        finally:
            os.unlink(temp_file)

    def test_load_questions_from_csv_file(self, csv_parser: CSVParserService, sample_questions: List) -> None:
        """Test loading questions from CSV file."""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_file = f.name
        
        try:
            # First save questions
            csv_parser.save_questions_to_csv(sample_questions, temp_file)
            
            # Then load them back
            loaded = csv_parser.load_questions_from_csv_file(temp_file)
            
            assert len(loaded) == 2
            assert loaded[0].id == "q_001"
        finally:
            os.unlink(temp_file)

    def test_load_questions_from_csv_file_not_found(self, csv_parser: CSVParserService) -> None:
        """Test loading from non-existent file."""
        result = csv_parser.load_questions_from_csv_file("/nonexistent/path/file.csv")
        
        assert result == []

    def test_save_and_load_roundtrip(self, csv_parser: CSVParserService, sample_questions: List) -> None:
        """Test save and load roundtrip."""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_file = f.name
        
        try:
            # Save
            csv_parser.save_questions_to_csv(sample_questions, temp_file)
            
            # Load
            loaded = csv_parser.load_questions_from_csv_file(temp_file)
            
            # Verify
            assert len(loaded) == len(sample_questions)
            for orig, load in zip(sample_questions, loaded):
                assert orig.id == load.id
                assert orig.topic == load.topic
                assert orig.question_text == load.question_text
        finally:
            os.unlink(temp_file)


class TestAppendQuestionsToCSV:
    """Tests for append_questions_to_csv method."""

    @pytest.fixture
    def csv_parser(self) -> CSVParserService:
        """Create CSV parser service instance."""
        return CSVParserService()

    @pytest.fixture
    def sample_questions(self) -> List:
        """Create sample Question objects."""
        from src.models.question import Question
        
        return [
            Question(
                id="q_001",
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

    def test_append_to_new_file(self, csv_parser: CSVParserService, sample_questions: List) -> None:
        """Test appending to a new file."""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_file = f.name
        os.unlink(temp_file)  # Remove so it doesn't exist
        
        try:
            result = csv_parser.append_questions_to_csv(sample_questions, temp_file)
            
            assert result is True
            assert os.path.exists(temp_file)
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_append_to_existing_file(self, csv_parser: CSVParserService, sample_questions: List) -> None:
        """Test appending to an existing file."""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_file = f.name
        
        try:
            # First save
            csv_parser.save_questions_to_csv(sample_questions, temp_file)
            
            # Then append
            result = csv_parser.append_questions_to_csv(sample_questions, temp_file)
            
            assert result is True
            
            # Load and verify count
            loaded = csv_parser.load_questions_from_csv_file(temp_file)
            assert len(loaded) == 2
        finally:
            os.unlink(temp_file)


class TestBackupCSVFile:
    """Tests for backup_csv_file method."""

    @pytest.fixture
    def csv_parser(self) -> CSVParserService:
        """Create CSV parser service instance."""
        return CSVParserService()

    def test_backup_existing_file(self, csv_parser: CSVParserService) -> None:
        """Test backing up an existing file."""
        import tempfile
        import os
        import glob
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("id,topic,question_text\n")
            temp_file = f.name
        
        try:
            result = csv_parser.backup_csv_file(temp_file)
            
            assert result is True
            
            # Find and clean up backup file
            base_name = os.path.splitext(temp_file)[0]
            backup_files = glob.glob(f"{base_name}_backup_*.csv")
            for bf in backup_files:
                os.unlink(bf)
        finally:
            os.unlink(temp_file)

    def test_backup_nonexistent_file(self, csv_parser: CSVParserService) -> None:
        """Test backing up a non-existent file."""
        result = csv_parser.backup_csv_file("/nonexistent/path/file.csv")
        
        assert result is False


