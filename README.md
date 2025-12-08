# Practice application
This is a question back application. $${\color{blue}practise \space with \space different \space tech \space stack }$$


## features

 * use a pre-defined list of questions and answers stored in a text/csv file
 * user is aked what topic he wants from a pre-defined list; 
 * user is also asked a difficulty level -- choose from 3, easy-medium-hard
 * application randomly picks one question from the topic for that difficulty level
 * application receives answer from user, checks against the dataset (question-bank)
 * application also keeps track of user's scores
 * at the end, the application summarizes the results


## for the kata/ practice
make use of spec-kit to trial or {+ experiment with different tech-stacks +}

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

## Frontend User Interfaces

### Command Line Interface (CLI)

**Start the CLI application:**
```bash
# Navigate to project root
cd q_and_a_practise1

# Run the CLI application
python -m src.cli.main

# Or with verbose logging
python -m src.cli.main --verbose
```

**CLI Features:**
- Interactive topic and difficulty selection
- Real-time question presentation with answer validation
- Progress tracking and session summary
- Keyboard shortcuts for navigation
- Comprehensive error handling and user feedback

**CLI Usage Example:**
```bash
$ python -m src.cli.main
🎓 Q&A Practice Application

Select a topic:
1. Physics
2. Chemistry  
3. Math

Enter your choice (1-3): 1

Select difficulty:
1. Easy
2. Medium
3. Hard

Enter your choice (1-3): 2

📝 Starting Physics (Medium) session...

Question 1/10:
What is the SI unit of electric current?
A) Volt
B) Ampere
C) Ohm
D) Watt

Your answer (A-D): B
✅ Correct!

[... continues with more questions ...]

📊 Session Summary:
Topic: Physics (Medium)
Questions: 10
Correct: 8
Accuracy: 80.0%
Duration: 5 minutes 23 seconds
```

### Web Interface

**Start the web application:**
```bash
# Navigate to project root
cd q_and_a_practise1

# Start the web server
python -m src.web.main

# The application will be available at:
# http://localhost:8000
```

**Web Features:**
- Modern responsive design with Tailwind CSS
- Interactive quiz interface with real-time feedback
- Dynamic question loading with HTMX
- Progress tracking and performance analytics
- Session results with detailed breakdowns
- Mobile-friendly design with accessibility support
- Error handling with user-friendly pages

**Web Access:**
1. Open your browser and go to `http://localhost:8000`
2. Select your preferred topic (Physics, Chemistry, or Math)
3. Choose difficulty level (Easy, Medium, or Hard)
4. Click "Start Quiz" to begin your session
5. Answer questions using the interactive interface
6. View your results and performance analytics

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

#### Backend Services
- ✅ Topic selection (Physics, Chemistry, Math)
- ✅ Difficulty levels (Easy, Medium, Hard)
- ✅ Session management with progress tracking
- ✅ Question randomization from CSV dataset
- ✅ Answer validation and scoring
- ✅ RESTful API with OpenAPI documentation
- ✅ Comprehensive test suite (64 tests passing)
- ✅ Structured logging and error handling

#### Command Line Interface (CLI)
- ✅ Interactive topic and difficulty selection prompts
- ✅ Real-time question presentation with formatted display
- ✅ Answer collection and validation with immediate feedback
- ✅ Session summary display with performance metrics
- ✅ Comprehensive error handling and user input validation
- ✅ Progress tracking and navigation controls
- ✅ Verbose logging support for debugging

#### Web Frontend Interface
- ✅ Modern responsive design with Tailwind CSS
- ✅ Interactive topic/difficulty selection page with statistics
- ✅ Dynamic quiz interface with real-time feedback
- ✅ HTMX-powered question loading without page refreshes
- ✅ Progress tracking with visual progress bars
- ✅ Session results with performance analytics and breakdowns
- ✅ Mobile-responsive design with accessibility support
- ✅ Error handling with user-friendly error pages
- ✅ Keyboard shortcuts and enhanced UX features
- ✅ CSS animations and transitions for better user experience


