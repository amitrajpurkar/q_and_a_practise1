"""
CSV file parsing service for Q&A Practice Application.

Handles loading and parsing of question bank from CSV files using pandas.
Implements proper error handling and validation following SOLID principles.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from src.utils.exceptions import CSVParsingError, ValidationError


class CSVParserService:
    """
    Service for parsing CSV question bank files.

    Follows Single Responsibility principle by focusing only on
    CSV parsing and data transformation operations.
    """

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        """Initialize CSV parser service."""
        self.logger = logger or logging.getLogger(__name__)

    def load_questions_from_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load questions from CSV file with proper error handling.

        Args:
            file_path: Path to the CSV file

        Returns:
            List of question dictionaries

        Raises:
            CSVParsingError: If file cannot be parsed
            ValidationError: If data validation fails
        """
        try:
            # Check if file exists
            path = Path(file_path)
            if not path.exists():
                raise CSVParsingError(f"CSV file not found: {file_path}")

            # Load CSV using pandas
            df = pd.read_csv(file_path)
            self.logger.info(f"Loaded {len(df)} rows from CSV file: {file_path}")

            # Validate required columns
            required_columns = [
                "topic",
                "question",
                "option1",
                "option2",
                "option3",
                "option4",
                "answer",
                "difficulty",
            ]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise CSVParsingError(f"Missing required columns: {missing_columns}")

            # Convert DataFrame to list of dictionaries
            questions = df.to_dict("records")

            # Validate and clean data
            validated_questions = []
            for i, question in enumerate(questions):
                try:
                    validated_question = self._validate_question_data(question, i)
                    validated_questions.append(validated_question)
                except ValidationError as e:
                    self.logger.warning(f"Skipping invalid question at row {i+1}: {e}")
                    continue

            if not validated_questions:
                raise ValidationError("No valid questions found in CSV file")

            self.logger.info(
                f"Successfully parsed {len(validated_questions)} valid questions"
            )
            return validated_questions

        except pd.errors.EmptyDataError:
            raise CSVParsingError("CSV file is empty")
        except pd.errors.ParserError as e:
            raise CSVParsingError(f"Failed to parse CSV file: {str(e)}")
        except Exception as e:
            if isinstance(e, (CSVParsingError, ValidationError)):
                raise
            raise CSVParsingError(f"Unexpected error loading CSV: {str(e)}")

    def _validate_question_data(
        self, question: Dict[str, Any], row_index: int
    ) -> Dict[str, Any]:
        """
        Validate individual question data.

        Args:
            question: Question dictionary from CSV
            row_index: Row index for error reporting

        Returns:
            Validated question dictionary

        Raises:
            ValidationError: If validation fails
        """
        validated = {}

        # Validate topic
        topic = str(question.get("topic", "")).strip()
        if not topic:
            raise ValidationError(f"Row {row_index+1}: Topic cannot be empty")
        if topic not in ["Physics", "Chemistry", "Math"]:
            raise ValidationError(
                f"Row {row_index+1}: Invalid topic '{topic}'. Must be one of: Physics, Chemistry, Math"
            )
        validated["topic"] = topic

        # Validate question text
        question_text = str(question.get("question", "")).strip()
        if not question_text:
            raise ValidationError(f"Row {row_index+1}: Question text cannot be empty")
        if len(question_text) < 10:
            raise ValidationError(
                f"Row {row_index+1}: Question text must be at least 10 characters long"
            )
        validated["question_text"] = question_text

        # Validate options
        options = []
        for i in range(1, 5):
            option_key = f"option{i}"
            option_value = str(question.get(option_key, "")).strip()
            if not option_value:
                raise ValidationError(f"Row {row_index+1}: Option {i} cannot be empty")
            options.append(option_value)

        # Check for duplicate options
        if len(set(options)) != len(options):
            raise ValidationError(f"Row {row_index+1}: Options must be unique")

        validated["option1"] = options[0]
        validated["option2"] = options[1]
        validated["option3"] = options[2]
        validated["option4"] = options[3]

        # Validate correct answer
        correct_answer = str(question.get("answer", "")).strip()
        if not correct_answer:
            raise ValidationError(f"Row {row_index+1}: Correct answer cannot be empty")
        if correct_answer not in options:
            raise ValidationError(
                f"Row {row_index+1}: Correct answer '{correct_answer}' must match one of the options"
            )
        validated["correct_answer"] = correct_answer

        # Validate difficulty
        difficulty = str(question.get("difficulty", "")).strip()
        if not difficulty:
            raise ValidationError(f"Row {row_index+1}: Difficulty cannot be empty")
        if difficulty not in ["Easy", "Medium", "Hard"]:
            raise ValidationError(
                f"Row {row_index+1}: Invalid difficulty '{difficulty}'. Must be one of: Easy, Medium, Hard"
            )
        validated["difficulty"] = difficulty

        # Generate tag
        validated["tag"] = f"{topic}-{difficulty}"

        # Set default session tracking
        validated["asked_in_session"] = False
        validated["got_right"] = False

        # Generate ID (if not present)
        if "id" in question and str(question["id"]).strip():
            validated["id"] = str(question["id"]).strip()
        else:
            validated["id"] = f"{topic.lower()}_{row_index+1}"

        return validated

    def get_questions_by_topic(
        self, questions: List[Dict[str, Any]], topic: str
    ) -> List[Dict[str, Any]]:
        """
        Filter questions by topic.

        Args:
            questions: List of question dictionaries
            topic: Topic to filter by

        Returns:
            Filtered list of questions
        """
        return [q for q in questions if q["topic"] == topic]

    def get_questions_by_difficulty(
        self, questions: List[Dict[str, Any]], difficulty: str
    ) -> List[Dict[str, Any]]:
        """
        Filter questions by difficulty.

        Args:
            questions: List of question dictionaries
            difficulty: Difficulty to filter by

        Returns:
            Filtered list of questions
        """
        return [q for q in questions if q["difficulty"] == difficulty]

    def get_questions_by_criteria(
        self, questions: List[Dict[str, Any]], topic: str, difficulty: str
    ) -> List[Dict[str, Any]]:
        """
        Filter questions by both topic and difficulty.

        Args:
            questions: List of question dictionaries
            topic: Topic to filter by
            difficulty: Difficulty to filter by

        Returns:
            Filtered list of questions
        """
        return [
            q
            for q in questions
            if q["topic"] == topic and q["difficulty"] == difficulty
        ]
