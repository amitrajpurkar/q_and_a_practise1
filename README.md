# Practice application
This is a question back application. {+ practise with different tech stack +}


## features

 * use a pre-defined list of questions and answers stored in a text/csv file
 * user is aked what topic he wants from a pre-defined list; 
 * user is also asked a difficulty level -- choose from 3, easy-medium-hard
 * application randomly picks one question from the topic for that difficulty level
 * application receives answer from user, checks against the dataset (question-bank)
 * application also keeps track of user's scores
 * at the end, the application summarizes the results


## for the kata/ practice
make use of spec-kit to trial or experiment with different tech-stacks

## Quick Start - Backend Services

### Prerequisites
- Python 3.8+ installed
- Virtual environment (recommended)

### Setup and Installation

1. **Clone and navigate to the project:**
```bash
cd q_and_a_practise1
```

2. **Create and activate virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

### Running the Backend Server

1. **Start the backend service:**
```bash
python -m src.api.main
```

2. **The server will start on `http://localhost:8000`**

### API Documentation

Once the server is running, you can access:

- **OpenAPI Spec**: `http://localhost:8000/openapi.json`
- **Health Check**: `http://localhost:8000/health`
- **Root Info**: `http://localhost:8000/`

### Testing the API

**Get available topics:**
```bash
curl http://localhost:8000/api/v1/topics/
# Returns: ["Chemistry", "Math", "Physics"]
```

**Get difficulty levels:**
```bash
curl http://localhost:8000/api/v1/difficulties/
# Returns: ["Easy", "Medium", "Hard"]
```

**Create a practice session:**
```bash
curl -X POST http://localhost:8000/api/v1/sessions/ \
  -H "Content-Type: application/json" \
  -d '{"topic":"Physics","difficulty":"Medium","total_questions":5}'
```

**Get next question in session:**
```bash
curl http://localhost:8000/api/v1/sessions/{session_id}/next-question
```

**Submit an answer:**
```bash
curl -X POST http://localhost:8000/api/v1/sessions/{session_id}/submit-answer \
  -H "Content-Type: application/json" \
  -d '{"question_id":"physics_3","answer":"Ampere"}'
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest tests/contract/
python -m pytest tests/integration/
python -m pytest tests/unit/
```

### Key Features Implemented

- ✅ Topic selection (Physics, Chemistry, Math)
- ✅ Difficulty levels (Easy, Medium, Hard)
- ✅ Session management with progress tracking
- ✅ Question randomization from CSV dataset
- ✅ Answer validation and scoring
- ✅ RESTful API with OpenAPI documentation
- ✅ Comprehensive test suite (64 tests passing)
- ✅ Structured logging and error handling


