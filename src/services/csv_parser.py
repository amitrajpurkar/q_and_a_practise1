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
from src.models.question import Question


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

            # Convert DataFrame to list of dictionaries ( data records)
            questions = df.to_dict("records")
            
            # Additional data record transformations
            questions = self._transform_data_records(questions)

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

        # Validate question text (check both 'question' and 'question_text' for compatibility)
        question_text = str(question.get("question_text", question.get("question", ""))).strip()
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

        # Validate correct answer (check both 'answer' and 'correct_answer' for compatibility)
        correct_answer = str(question.get("correct_answer", question.get("answer", ""))).strip()
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

    def _transform_data_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform raw CSV records into structured data records.
        
        Args:
            records: Raw CSV records from pandas
            
        Returns:
            Transformed data records with consistent structure
        """
        transformed = []
        for i, record in enumerate(records):
            # Create a new record with consistent field names and data types
            transformed_record = {
                'id': f"q_{i+1:03d}",  # Generate unique ID
                'topic': self._clean_string_field(record.get('topic', '')),
                'question_text': self._clean_string_field(record.get('question', '')),
                'option1': self._clean_string_field(record.get('option1', '')),
                'option2': self._clean_string_field(record.get('option2', '')),
                'option3': self._clean_string_field(record.get('option3', '')),
                'option4': self._clean_string_field(record.get('option4', '')),
                'correct_answer': self._clean_string_field(record.get('answer', '')),
                'difficulty': self._clean_string_field(record.get('difficulty', '')),
                'tag': f"{self._clean_string_field(record.get('topic', ''))}-{self._clean_string_field(record.get('difficulty', ''))}",
                'source_row': i + 1  # Track original row number
            }
            transformed.append(transformed_record)
        
        return transformed

    def _clean_string_field(self, value: Any) -> str:
        """
        Clean and normalize string fields from CSV data.
        
        Args:
            value: Raw value from CSV
            
        Returns:
            Cleaned string value
        """
        if value is None:
            return ""
        if pd.isna(value):
            return ""
        return str(value).strip()

    def records_to_objects(self, records: List[Dict[str, Any]]) -> List['Question']:
        """
        Convert data records to Question objects.
        
        Args:
            records: List of data records
            
        Returns:
            List of Question objects
        """
        from src.models.question import Question
        
        questions = []
        for record in records:
            question = Question(
                id=record['id'],
                topic=record['topic'],
                question_text=record['question_text'],
                option1=record['option1'],
                option2=record['option2'],
                option3=record['option3'],
                option4=record['option4'],
                correct_answer=record['correct_answer'],
                difficulty=record['difficulty'],
                tag=record['tag']
            )
            questions.append(question)
        
        return questions

    def objects_to_records(self, questions: List['Question']) -> List[Dict[str, Any]]:
        """
        Convert Question objects back to data records.
        
        Args:
            questions: List of Question objects
            
        Returns:
            List of data records
        """
        records = []
        for question in questions:
            record = {
                'id': question.id,
                'topic': question.topic,
                'question_text': question.question_text,
                'option1': question.option1,
                'option2': question.option2,
                'option3': question.option3,
                'option4': question.option4,
                'correct_answer': question.correct_answer,
                'difficulty': question.difficulty,
                'tag': question.tag
            }
            records.append(record)
        
        return records

    # File I/O operations for CSV question bank
    def save_questions_to_csv(self, questions: List[Question], file_path: str) -> bool:
        """
        Save questions to a CSV file using file I/O operations.
        
        Args:
            questions: List of questions to save
            file_path: Path to the output CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import csv
            
            # Define CSV headers
            headers = [
                'id', 'topic', 'question_text', 'option1', 'option2', 
                'option3', 'option4', 'correct_answer', 'difficulty', 'tag'
            ]
            
            # Write to CSV file
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                
                # Write each question as a row
                for question in questions:
                    row = {
                        'id': question.id,
                        'topic': question.topic,
                        'question_text': question.question_text,
                        'option1': question.option1 or '',
                        'option2': question.option2 or '',
                        'option3': question.option3 or '',
                        'option4': question.option4 or '',
                        'correct_answer': question.correct_answer,
                        'difficulty': question.difficulty,
                        'tag': question.tag or ''
                    }
                    writer.writerow(row)
            
            self.logger.info(f"Successfully saved {len(questions)} questions to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save questions to CSV: {str(e)}")
            return False

    def load_questions_from_csv_file(self, file_path: str) -> List[Question]:
        """
        Load questions from a CSV file using file I/O operations.
        
        Args:
            file_path: Path to the input CSV file
            
        Returns:
            List of loaded questions
        """
        try:
            import csv
            
            questions = []
            
            # Read from CSV file
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        # Validate required fields
                        if not row.get('id') or not row.get('question_text') or not row.get('correct_answer'):
                            self.logger.warning(f"Skipping row {row_num}: missing required fields")
                            continue
                        
                        # Create Question object from row
                        question = Question(
                            id=row['id'].strip(),
                            topic=row['topic'].strip(),
                            question_text=row['question_text'].strip(),
                            option1=row.get('option1', '').strip() or None,
                            option2=row.get('option2', '').strip() or None,
                            option3=row.get('option3', '').strip() or None,
                            option4=row.get('option4', '').strip() or None,
                            correct_answer=row['correct_answer'].strip(),
                            difficulty=row['difficulty'].strip(),
                            tag=row.get('tag', '').strip() or None
                        )
                        
                        questions.append(question)
                        
                    except Exception as row_error:
                        self.logger.warning(f"Error processing row {row_num}: {str(row_error)}")
                        continue
            
            self.logger.info(f"Successfully loaded {len(questions)} questions from {file_path}")
            return questions
            
        except FileNotFoundError:
            self.logger.error(f"CSV file not found: {file_path}")
            return []
        except Exception as e:
            self.logger.error(f"Failed to load questions from CSV: {str(e)}")
            return []

    def append_questions_to_csv(self, questions: List[Question], file_path: str) -> bool:
        """
        Append questions to an existing CSV file.
        
        Args:
            questions: List of questions to append
            file_path: Path to the CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import csv
            import os
            
            # Check if file exists
            file_exists = os.path.exists(file_path)
            
            # Define CSV headers
            headers = [
                'id', 'topic', 'question_text', 'option1', 'option2', 
                'option3', 'option4', 'correct_answer', 'difficulty', 'tag'
            ]
            
            # Append to CSV file
            with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                
                # Write header if file is new
                if not file_exists:
                    writer.writeheader()
                
                # Write each question as a row
                for question in questions:
                    row = {
                        'id': question.id,
                        'topic': question.topic,
                        'question_text': question.question_text,
                        'option1': question.option1 or '',
                        'option2': question.option2 or '',
                        'option3': question.option3 or '',
                        'option4': question.option4 or '',
                        'correct_answer': question.correct_answer,
                        'difficulty': question.difficulty,
                        'tag': question.tag or ''
                    }
                    writer.writerow(row)
            
            self.logger.info(f"Successfully appended {len(questions)} questions to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to append questions to CSV: {str(e)}")
            return False

    def backup_csv_file(self, source_path: str, backup_suffix: str = '_backup') -> bool:
        """
        Create a backup of a CSV file.
        
        Args:
            source_path: Path to the source CSV file
            backup_suffix: Suffix to add to backup filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import shutil
            import os
            from datetime import datetime
            
            # Check if source file exists
            if not os.path.exists(source_path):
                self.logger.error(f"Source file not found: {source_path}")
                return False
            
            # Generate backup filename
            base_name, ext = os.path.splitext(source_path)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{base_name}{backup_suffix}_{timestamp}{ext}"
            
            # Copy file to backup location
            shutil.copy2(source_path, backup_path)
            
            self.logger.info(f"Successfully created backup: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {str(e)}")
            return False

    def validate_csv_file_structure(self, file_path: str) -> Dict[str, Any]:
        """
        Validate the structure of a CSV file.
        
        Args:
            file_path: Path to the CSV file to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            import csv
            
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': [],
                'row_count': 0,
                'header_columns': []
            }
            
            # Check if file exists
            if not os.path.exists(file_path):
                validation_result['is_valid'] = False
                validation_result['errors'].append("File does not exist")
                return validation_result
            
            # Read and validate file structure
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Check headers
                expected_headers = {
                    'id', 'topic', 'question_text', 'option1', 'option2', 
                    'option3', 'option4', 'correct_answer', 'difficulty', 'tag'
                }
                
                actual_headers = set(reader.fieldnames or [])
                validation_result['header_columns'] = list(reader.fieldnames or [])
                
                # Check for missing required headers
                required_headers = {'id', 'question_text', 'correct_answer'}
                missing_headers = required_headers - actual_headers
                
                if missing_headers:
                    validation_result['is_valid'] = False
                    validation_result['errors'].append(f"Missing required headers: {missing_headers}")
                
                # Check for unexpected headers
                unexpected_headers = actual_headers - expected_headers
                if unexpected_headers:
                    validation_result['warnings'].append(f"Unexpected headers found: {unexpected_headers}")
                
                # Count rows
                row_count = sum(1 for _ in reader)
                validation_result['row_count'] = row_count
                
                if row_count == 0:
                    validation_result['warnings'].append("File contains no data rows")
            
            return validation_result
            
        except Exception as e:
            return {
                'is_valid': False,
                'errors': [f"Failed to validate file: {str(e)}"],
                'warnings': [],
                'row_count': 0,
                'header_columns': []
            }

    def merge_csv_files(self, file_paths: List[str], output_path: str) -> bool:
        """
        Merge multiple CSV files into one.
        
        Args:
            file_paths: List of CSV file paths to merge
            output_path: Path to the merged output file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import csv
            
            all_questions = []
            
            # Load questions from all files
            for file_path in file_paths:
                questions = self.load_questions_from_csv_file(file_path)
                all_questions.extend(questions)
            
            # Remove duplicates based on ID
            seen_ids = set()
            unique_questions = []
            
            for question in all_questions:
                if question.id not in seen_ids:
                    seen_ids.add(question.id)
                    unique_questions.append(question)
            
            # Save merged questions
            success = self.save_questions_to_csv(unique_questions, output_path)
            
            if success:
                self.logger.info(f"Successfully merged {len(file_paths)} files into {output_path}")
                self.logger.info(f"Total questions: {len(all_questions)}, Unique questions: {len(unique_questions)}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to merge CSV files: {str(e)}")
            return False

    # Text file parsing for CSV processing
    def parse_text_file_to_csv(self, text_file_path: str, output_csv_path: str, 
                              delimiter: str = '\t') -> bool:
        """
        Parse a text file and convert to CSV format.
        
        Args:
            text_file_path: Path to the input text file
            output_csv_path: Path to the output CSV file
            delimiter: Delimiter used in the text file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            questions = []
            
            with open(text_file_path, 'r', encoding='utf-8') as textfile:
                lines = textfile.readlines()
            
            # Parse text file lines
            current_question = {}
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                if not line or line.startswith('#'):
                    continue  # Skip empty lines and comments
                
                # Parse key-value pairs
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    # Map keys to question fields
                    if key in ['id', 'question_id']:
                        current_question['id'] = value
                    elif key in ['topic', 'subject']:
                        current_question['topic'] = value
                    elif key in ['question', 'question_text', 'prompt']:
                        current_question['question_text'] = value
                    elif key in ['answer', 'correct_answer', 'solution']:
                        current_question['correct_answer'] = value
                    elif key in ['difficulty', 'level']:
                        current_question['difficulty'] = value
                    elif key in ['tag', 'category', 'label']:
                        current_question['tag'] = value
                    elif key in ['option1', 'choice1', 'a']:
                        current_question['option1'] = value
                    elif key in ['option2', 'choice2', 'b']:
                        current_question['option2'] = value
                    elif key in ['option3', 'choice3', 'c']:
                        current_question['option3'] = value
                    elif key in ['option4', 'choice4', 'd']:
                        current_question['option4'] = value
                    elif key == '---':  # Question separator
                        if self._is_complete_question(current_question):
                            questions.append(self._create_question_from_dict(current_question))
                        current_question = {}
            
            # Add the last question if complete
            if self._is_complete_question(current_question):
                questions.append(self._create_question_from_dict(current_question))
            
            # Save to CSV
            success = self.save_questions_to_csv(questions, output_csv_path)
            
            if success:
                self.logger.info(f"Successfully parsed {len(questions)} questions from text file to CSV")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to parse text file: {str(e)}")
            return False

    def parse_json_file_to_csv(self, json_file_path: str, output_csv_path: str) -> bool:
        """
        Parse a JSON file and convert to CSV format.
        
        Args:
            json_file_path: Path to the input JSON file
            output_csv_path: Path to the output CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import json
            
            with open(json_file_path, 'r', encoding='utf-8') as jsonfile:
                data = json.load(jsonfile)
            
            questions = []
            
            # Handle different JSON structures
            if isinstance(data, list):
                # Array of question objects
                for item in data:
                    question = self._parse_json_question_object(item)
                    if question:
                        questions.append(question)
            
            elif isinstance(data, dict):
                if 'questions' in data:
                    # Object with questions array
                    for item in data['questions']:
                        question = self._parse_json_question_object(item)
                        if question:
                            questions.append(question)
                else:
                    # Single question object
                    question = self._parse_json_question_object(data)
                    if question:
                        questions.append(question)
            
            # Save to CSV
            success = self.save_questions_to_csv(questions, output_csv_path)
            
            if success:
                self.logger.info(f"Successfully parsed {len(questions)} questions from JSON file to CSV")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to parse JSON file: {str(e)}")
            return False

    def parse_xml_file_to_csv(self, xml_file_path: str, output_csv_path: str) -> bool:
        """
        Parse an XML file and convert to CSV format.
        
        Args:
            xml_file_path: Path to the input XML file
            output_csv_path: Path to the output CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import xml.etree.ElementTree as ET
            
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            
            questions = []
            
            # Find all question elements (support different XML structures)
            question_elements = root.findall('.//question') or root.findall('.//Question')
            
            for elem in question_elements:
                question_data = {}
                
                # Extract text content from child elements
                for child in elem:
                    tag_name = child.tag.lower()
                    text_content = child.text.strip() if child.text else ''
                    
                    if text_content:
                        if tag_name in ['id', 'question_id']:
                            question_data['id'] = text_content
                        elif tag_name in ['topic', 'subject']:
                            question_data['topic'] = text_content
                        elif tag_name in ['question', 'question_text', 'prompt', 'text']:
                            question_data['question_text'] = text_content
                        elif tag_name in ['answer', 'correct_answer', 'solution']:
                            question_data['correct_answer'] = text_content
                        elif tag_name in ['difficulty', 'level']:
                            question_data['difficulty'] = text_content
                        elif tag_name in ['tag', 'category', 'label']:
                            question_data['tag'] = text_content
                        elif tag_name.startswith('option') or tag_name.startswith('choice'):
                            question_data[tag_name] = text_content
                
                # Also check attributes
                for attr_name, attr_value in elem.attrib.items():
                    if attr_name.lower() in ['id', 'topic', 'difficulty', 'tag']:
                        question_data[attr_name.lower()] = attr_value
                
                if self._is_complete_question(question_data):
                    question = self._create_question_from_dict(question_data)
                    if question:
                        questions.append(question)
            
            # Save to CSV
            success = self.save_questions_to_csv(questions, output_csv_path)
            
            if success:
                self.logger.info(f"Successfully parsed {len(questions)} questions from XML file to CSV")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to parse XML file: {str(e)}")
            return False

    def parse_delimited_file_to_csv(self, file_path: str, output_csv_path: str, 
                                   delimiter: str = '|') -> bool:
        """
        Parse a delimited text file and convert to CSV format.
        
        Args:
            file_path: Path to the input delimited file
            output_csv_path: Path to the output CSV file
            delimiter: Field delimiter in the input file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            questions = []
            
            with open(file_path, 'r', encoding='utf-8') as dfile:
                lines = dfile.readlines()
            
            # Assume first line is header
            if not lines:
                self.logger.error("Delimited file is empty")
                return False
            
            header_line = lines[0].strip()
            headers = [h.strip() for h in header_line.split(delimiter)]
            
            # Map headers to question fields
            field_mapping = self._create_field_mapping(headers)
            
            # Parse data lines
            for line_num, line in enumerate(lines[1:], 2):
                line = line.strip()
                if not line:
                    continue
                
                values = [v.strip() for v in line.split(delimiter)]
                
                if len(values) != len(headers):
                    self.logger.warning(f"Line {line_num}: Field count mismatch. Expected {len(headers)}, got {len(values)}")
                    continue
                
                question_data = {}
                for i, (header, value) in enumerate(zip(headers, values)):
                    if header in field_mapping and value:
                        question_data[field_mapping[header]] = value
                
                if self._is_complete_question(question_data):
                    question = self._create_question_from_dict(question_data)
                    if question:
                        questions.append(question)
            
            # Save to CSV
            success = self.save_questions_to_csv(questions, output_csv_path)
            
            if success:
                self.logger.info(f"Successfully parsed {len(questions)} questions from delimited file to CSV")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to parse delimited file: {str(e)}")
            return False

    def parse_mixed_format_file(self, file_path: str, output_csv_path: str) -> bool:
        """
        Parse a file with mixed formats (e.g., some JSON, some text) and convert to CSV.
        
        Args:
            file_path: Path to the input mixed format file
            output_csv_path: Path to the output CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            questions = []
            
            with open(file_path, 'r', encoding='utf-8') as mfile:
                content = mfile.read()
            
            # Try to detect format and parse accordingly
            if content.strip().startswith('{') or content.strip().startswith('['):
                # JSON format
                return self.parse_json_file_to_csv(file_path, output_csv_path)
            
            elif content.strip().startswith('<'):
                # XML format
                return self.parse_xml_file_to_csv(file_path, output_csv_path)
            
            elif ':' in content and '\n' in content:
                # Key-value text format
                return self.parse_text_file_to_csv(file_path, output_csv_path)
            
            elif '|' in content or '\t' in content:
                # Delimited format
                delimiter = '|' if '|' in content else '\t'
                return self.parse_delimited_file_to_csv(file_path, output_csv_path, delimiter)
            
            else:
                # Try to parse as generic text
                return self.parse_text_file_to_csv(file_path, output_csv_path)
            
        except Exception as e:
            self.logger.error(f"Failed to parse mixed format file: {str(e)}")
            return False

    def validate_parsed_questions(self, questions: List[Question]) -> Dict[str, Any]:
        """
        Validate a list of parsed questions.
        
        Args:
            questions: List of questions to validate
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'total_questions': len(questions),
            'valid_questions': 0,
            'invalid_questions': 0,
            'validation_errors': [],
            'warnings': [],
            'topic_distribution': {},
            'difficulty_distribution': {}
        }
        
        for i, question in enumerate(questions):
            try:
                # Validate the question
                question.validate()
                validation_results['valid_questions'] += 1
                
                # Update distributions
                topic = question.topic
                difficulty = question.difficulty
                
                validation_results['topic_distribution'][topic] = \
                    validation_results['topic_distribution'].get(topic, 0) + 1
                validation_results['difficulty_distribution'][difficulty] = \
                    validation_results['difficulty_distribution'].get(difficulty, 0) + 1
                
            except ValidationError as e:
                validation_results['invalid_questions'] += 1
                validation_results['validation_errors'].append({
                    'question_index': i,
                    'question_id': getattr(question, 'id', 'unknown'),
                    'error': str(e)
                })
            
            # Check for warnings
            if hasattr(question, 'tag') and not question.tag:
                validation_results['warnings'].append({
                    'question_index': i,
                    'question_id': getattr(question, 'id', 'unknown'),
                    'warning': 'Question has no tag'
                })
        
        return validation_results

    # Helper methods for text file parsing
    def _is_complete_question(self, question_data: Dict[str, str]) -> bool:
        """Check if question data has required fields."""
        required_fields = ['id', 'topic', 'question_text', 'correct_answer', 'difficulty']
        return all(field in question_data and question_data[field] for field in required_fields)

    def _create_question_from_dict(self, question_data: Dict[str, str]) -> Question:
        """Create a Question object from dictionary data."""
        return Question(
            id=question_data['id'],
            topic=question_data['topic'],
            question_text=question_data['question_text'],
            option1=question_data.get('option1'),
            option2=question_data.get('option2'),
            option3=question_data.get('option3'),
            option4=question_data.get('option4'),
            correct_answer=question_data['correct_answer'],
            difficulty=question_data['difficulty'],
            tag=question_data.get('tag')
        )

    def _parse_json_question_object(self, obj: Dict[str, Any]) -> Optional[Question]:
        """Parse a single question object from JSON."""
        try:
            question_data = {}
            
            # Map JSON fields to question fields
            field_mappings = {
                'id': ['id', 'question_id', 'questionId'],
                'topic': ['topic', 'subject', 'category'],
                'question_text': ['question', 'question_text', 'prompt', 'text'],
                'correct_answer': ['answer', 'correct_answer', 'solution'],
                'difficulty': ['difficulty', 'level'],
                'tag': ['tag', 'category', 'label'],
                'option1': ['option1', 'choice1', 'a', 'optionA'],
                'option2': ['option2', 'choice2', 'b', 'optionB'],
                'option3': ['option3', 'choice3', 'c', 'optionC'],
                'option4': ['option4', 'choice4', 'd', 'optionD']
            }
            
            for question_field, json_fields in field_mappings.items():
                for json_field in json_fields:
                    if json_field in obj and obj[json_field]:
                        question_data[question_field] = str(obj[json_field])
                        break
            
            if self._is_complete_question(question_data):
                return self._create_question_from_dict(question_data)
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Failed to parse JSON question object: {str(e)}")
            return None

    def _create_field_mapping(self, headers: List[str]) -> Dict[str, str]:
        """Create mapping from file headers to question fields."""
        mapping = {}
        
        for header in headers:
            header_lower = header.lower()
            
            if header_lower in ['id', 'question_id', 'questionid']:
                mapping[header] = 'id'
            elif header_lower in ['topic', 'subject', 'category']:
                mapping[header] = 'topic'
            elif header_lower in ['question', 'question_text', 'prompt', 'text']:
                mapping[header] = 'question_text'
            elif header_lower in ['answer', 'correct_answer', 'solution']:
                mapping[header] = 'correct_answer'
            elif header_lower in ['difficulty', 'level']:
                mapping[header] = 'difficulty'
            elif header_lower in ['tag', 'label', 'category']:
                mapping[header] = 'tag'
            elif header_lower.startswith('option') or header_lower.startswith('choice'):
                mapping[header] = header_lower
        
        return mapping
