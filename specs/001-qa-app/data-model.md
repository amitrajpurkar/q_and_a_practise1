# Data Model: Q&A Practice Application

**Created**: 2025-12-02  
**Purpose**: Define data entities, relationships, and validation rules

## Core Entities

### Question Entity

**Purpose**: Represents a single question with all associated data.

**Fields**:
```python
@dataclass
class Question:
    id: str                    # Unique identifier (topic + index)
    topic: str                 # Physics, Chemistry, Math
    question_text: str         # The actual question
    option1: str              # First multiple choice option
    option2: str              # Second multiple choice option
    option3: str              # Third multiple choice option
    option4: str              # Fourth multiple choice option
    correct_answer: str       # The correct answer (matches option text)
    difficulty: str           # Easy, Medium, Hard
    tag: str                  # Topic-difficulty combination
    asked_in_session: bool    # Track if asked in current session
    got_right: bool          # Track if answered correctly
```

**Validation Rules**:
- `topic` must be one of: ["Physics", "Chemistry", "Math"]
- `difficulty` must be one of: ["Easy", "Medium", "Hard"]
- `correct_answer` must match one of the four option texts
- All string fields must be non-empty after stripping
- `question_text` must be at least 10 characters long

**State Transitions**:
- `asked_in_session`: False → True (when question is presented)
- `got_right`: False → True (when answered correctly, only if asked_in_session is True)

### UserSession Entity

**Purpose**: Manages the current practice session state and progress.

**Fields**:
```python
@dataclass
class UserSession:
    session_id: str           # Unique session identifier
    topic: str               # Selected topic for this session
    difficulty: str          # Selected difficulty for this session
    questions_asked: List[str]  # List of question IDs asked
    user_answers: Dict[str, str]  # Mapping question_id → user_answer
    start_time: datetime     # Session start timestamp
    end_time: Optional[datetime]  # Session end timestamp
    is_active: bool          # Whether session is currently active
    total_questions: int     # Total questions in session
    current_question_index: int  # Index of current question
```

**Validation Rules**:
- `topic` and `difficulty` must match valid options
- `questions_asked` length must equal `total_questions` when session is complete
- `user_answers` keys must be subset of `questions_asked`
- `end_time` must be after `start_time` if present
- `current_question_index` must be <= `total_questions`

**State Transitions**:
- Created → Active (when first question is presented)
- Active → Completed (when all questions answered or user ends session)
- Can transition to Ended at any point (user cancellation)

### Score Entity

**Purpose**: Tracks and calculates user performance metrics.

**Fields**:
```python
@dataclass
class Score:
    session_id: str          # Associated session identifier
    total_questions: int     # Total questions attempted
    correct_answers: int     # Number of correct answers
    incorrect_answers: int   # Number of incorrect answers
    accuracy_percentage: float  # (correct / total) * 100
    time_taken_seconds: int  # Total session duration
    topic_performance: Dict[str, Dict[str, int]]  # Performance by topic and difficulty
    streak_data: Dict[str, int]  # Current and best streaks
```

**Validation Rules**:
- `total_questions` = `correct_answers` + `incorrect_answers`
- `accuracy_percentage` must be between 0 and 100
- `time_taken_seconds` must be non-negative
- All counts in `topic_performance` must sum to `total_questions`

**Calculated Fields**:
- `accuracy_percentage` = (`correct_answers` / `total_questions`) * 100
- `incorrect_answers` = `total_questions` - `correct_answers`

### QuestionBank Entity

**Purpose**: Manages the collection of all questions and provides filtering/searching capabilities.

**Fields**:
```python
@dataclass
class QuestionBank:
    questions: List[Question]  # All available questions
    topic_index: Dict[str, List[str]]  # Topic → question IDs mapping
    difficulty_index: Dict[str, List[str]]  # Difficulty → question IDs mapping
    topic_difficulty_index: Dict[str, List[str]]  # "topic-difficulty" → question IDs
    loaded_at: datetime       # When the bank was loaded from CSV
    csv_path: str            # Path to the source CSV file
```

**Validation Rules**:
- All index mappings must reference valid question IDs
- No duplicate question IDs in the questions list
- At least 20 questions per topic-difficulty combination
- CSV file must exist and be readable

**Index Structure**:
- `topic_index`: {"Physics": ["physics_1", "physics_2", ...], ...}
- `difficulty_index`: {"Easy": ["physics_1", "chemistry_1", ...], ...}
- `topic_difficulty_index`: {"Physics-Easy": ["physics_1", ...], ...}

## Relationships

### Entity Relationships

```
UserSession 1..1 ←→ Score
UserSession 1..* ←→ Question (through questions_asked)
QuestionBank 1..* ←→ Question
Score 1..1 ←→ UserSession
```

### Data Flow

1. **Session Creation**: UserSession created with topic/difficulty selection
2. **Question Selection**: QuestionBank filters questions based on session criteria
3. **Question Presentation**: Question marked as asked_in_session = True
4. **Answer Submission**: UserSession records user answer, Question updates got_right if correct
5. **Score Calculation**: Score entity calculated from UserSession data
6. **Session Completion**: UserSession marked inactive, Score finalized

## CSV Data Mapping

### Input CSV Format
```csv
topic,question,option1,option2,option3,option4,answer,difficulty,asked_in_this_session,got_right,tag
Physics,"What is the SI unit of force?","Newton","Joule","Watt","Pascal","Newton","Easy",FALSE,FALSE,"Physics-Mechanics"
```

### Field Mapping
| CSV Column | Question Field | Transformation |
|------------|----------------|----------------|
| topic | topic | Direct mapping |
| question | question_text | Direct mapping |
| option1 | option1 | Direct mapping |
| option2 | option2 | Direct mapping |
| option3 | option3 | Direct mapping |
| option4 | option4 | Direct mapping |
| answer | correct_answer | Direct mapping |
| difficulty | difficulty | Direct mapping |
| asked_in_this_session | asked_in_session | CSV boolean → Python bool |
| got_right | got_right | CSV boolean → Python bool |
| tag | tag | Direct mapping, used for ID generation |

### ID Generation Strategy
```python
def generate_question_id(question: Question, index: int) -> str:
    return f"{question.topic.lower()}_{index}"
```

## Validation Rules Summary

### Input Validation
- All user inputs validated at service layer boundaries
- Topic and difficulty selections checked against allowed values
- Answer selections validated against available options
- Session state transitions validated before execution

### Data Integrity
- Question IDs must be unique across the entire bank
- CSV file must contain all required columns
- No empty or malformed question data
- Correct answer must match one of the provided options

### Business Logic Validation
- Cannot ask the same question twice in one session
- Session cannot be completed if no questions were asked
- Score calculations must be mathematically correct
- Time tracking must be consistent and accurate

## Error Handling

### Validation Errors
- `InvalidTopicError`: Topic not in allowed list
- `InvalidDifficultyError`: Difficulty not in allowed list
- `InvalidAnswerError`: Answer not in available options
- `DuplicateQuestionError`: Question ID already exists

### Data Errors
- `CSVParseError`: CSV file cannot be parsed
- `MissingFieldError`: Required field missing from CSV
- `InvalidDataError`: Data validation failed
- `FileNotFoundError`: CSV file not found

### Session Errors
- `SessionNotFoundError`: Session ID not found
- `InactiveSessionError`: Operation on inactive session
- `QuestionNotFoundError`: Question ID not found in bank

## Performance Considerations

### Memory Usage
- QuestionBank loaded once and cached in memory
- Estimated memory usage: ~200 questions × ~500 bytes = ~100KB
- Well within 100MB memory constraint

### Query Performance
- O(1) lookup for questions by ID using dictionary
- O(n) filtering for topic/difficulty combinations
- O(k) random selection where k is filtered question count

### Caching Strategy
- QuestionBank cached for application lifetime
- Session data cached during active session
- Score calculations cached after session completion

## Testing Strategy

### Unit Tests
- Question entity validation and state transitions
- UserSession lifecycle management
- Score calculation accuracy
- QuestionBank filtering and indexing

### Integration Tests
- CSV loading and QuestionBank population
- Session workflow with multiple questions
- Score calculation across different scenarios
- Error handling for invalid data

### Data Validation Tests
- All validation rules for each entity
- Edge cases and boundary conditions
- Error scenarios and recovery
- Performance under load
