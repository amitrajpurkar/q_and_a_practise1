# Quickstart Guide: Q&A Practice Application

**Created**: 2025-12-02  
**Purpose**: Get the Q&A practice application running in minutes

## Prerequisites

### System Requirements
- **Python**: 3.12 or higher
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Memory**: Minimum 512MB RAM (recommended: 2GB+)
- **Storage**: 100MB free disk space
- **Network**: Internet connection for dependency installation

### Required Tools
- **UV**: Ultra-fast Python package installer (see installation below)
- **Git**: For cloning and version control
- **Modern Web Browser**: Chrome 90+, Firefox 88+, Safari 14+, or Edge 90+

## Installation

### 1. Install UV Package Manager
```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

### 2. Clone the Repository
```bash
git clone <repository-url>
cd q_and_a_practise1
```

### 3. Create Virtual Environment and Install Dependencies
```bash
# Create virtual environment with UV
uv venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
uv pip install -e .
```

### 4. Verify Question Bank
```bash
# Check if question bank exists
ls src/main/resources/question-bank.csv

# Verify CSV format (should show headers)
head -1 src/main/resources/question-bank.csv
```

## Running the Application

### Option 1: Web Interface (Recommended)

#### Start the Web Server
```bash
# From project root
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

#### Access the Web Interface
1. Open your web browser
2. Navigate to: http://localhost:8000
3. You should see the Q&A practice application homepage

#### Using the Web Interface
1. **Select Topic**: Choose from Physics, Chemistry, or Math
2. **Select Difficulty**: Choose Easy, Medium, or Hard
3. **Start Session**: Click "Start Practice"
4. **Answer Questions**: Select your answer and click "Submit"
5. **View Results**: See your score and performance summary

### Option 2: Command Line Interface

#### Start the CLI Application
```bash
# From project root
python -m src.cli.main
```

#### Using the CLI Interface
```
Welcome to Q&A Practice Application!

Available Topics:
1. Physics
2. Chemistry  
3. Math

Available Difficulties:
1. Easy
2. Medium
3. Hard

Select a topic (1-3): 1
Select a difficulty (1-3): 1

Question 1/10:
What is the SI unit of force?
A) Newton
B) Joule
C) Watt
D) Pascal

Your answer (A-D): A

✓ Correct!

[Continue with more questions...]

Session Complete!
Total Questions: 10
Correct Answers: 8
Accuracy: 80%
Time Taken: 3 minutes 45 seconds
```

## Development Setup

### Running Tests
```bash
# Run all tests with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test categories
uv run pytest tests/unit/          # Unit tests only
uv run pytest tests/integration/   # Integration tests only
uv run pytest tests/contract/      # Contract tests only

# Run tests with verbose output
uv run pytest -v
```

### Code Quality Checks
```bash
# Format code
uv run black src/ tests/

# Lint code
uv run flake8 src/ tests/

# Type checking
uv run mypy src/

# Run all quality checks
uv run pre-commit run --all-files
```

### Development Server
```bash
# Start development server with auto-reload
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Start with debug mode
uv run uvicorn src.api.main:app --reload --log-level debug
```

## API Documentation

### Interactive API Docs
Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key API Endpoints
```bash
# Get available topics
curl http://localhost:8000/api/v1/topics

# Get available difficulties
curl http://localhost:8000/api/v1/difficulties

# Get random question
curl "http://localhost:8000/api/v1/questions/random?topic=Physics&difficulty=Easy"

# Create new session
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"topic": "Physics", "difficulty": "Easy", "total_questions": 10}'
```

## Configuration

### Environment Variables
Create a `.env` file in the project root:
```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Question Bank Path
QUESTION_BANK_PATH=src/main/resources/question-bank.csv

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Testing
TEST_COVERAGE_THRESHOLD=90
```

### Custom Question Bank
To use a custom question bank:
1. Place your CSV file in `src/main/resources/`
2. Update the `QUESTION_BANK_PATH` environment variable
3. Ensure your CSV follows the required format:
```csv
topic,question,option1,option2,option3,option4,answer,difficulty,asked_in_this_session,got_right,tag
```

## Troubleshooting

### Common Issues

#### "ModuleNotFoundError: No module named 'src'"
```bash
# Ensure you're in the project root and virtual environment is activated
pwd  # Should be .../q_and_a_practise1
which python  # Should point to .venv/bin/python

# Reinstall in development mode
uv pip install -e .
```

#### "Question bank file not found"
```bash
# Check if file exists
ls -la src/main/resources/question-bank.csv

# If missing, copy from sample
cp src/main/resources/question-bank.sample.csv src/main/resources/question-bank.csv
```

#### "Port 8000 already in use"
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Or use different port
uv run uvicorn src.api.main:app --port 8001
```

#### "Tests failing with low coverage"
```bash
# Check coverage report
open htmlcov/index.html

# Run tests with more verbose output
uv run pytest --cov=src --cov-report=term-missing
```

### Performance Issues

#### Slow CSV Loading
```bash
# Check question bank size
wc -l src/main/resources/question-bank.csv

# Optimize by using smaller test set
head -50 src/main/resources/question-bank.csv > src/main/resources/question-bank-small.csv
```

#### Memory Usage
```bash
# Monitor memory usage
python -m memory_profiler src/api/main.py

# Check for memory leaks
python -m tracemalloc src/api/main.py
```

### Getting Help

1. **Check Logs**: Look at `logs/app.log` for detailed error messages
2. **Run Diagnostics**: `python -m src.cli.main --diagnostics`
3. **API Health Check**: `curl http://localhost:8000/health`
4. **Test Coverage**: Verify all tests pass: `uv run pytest`

## Next Steps

### For Users
1. Try different topics and difficulty levels
2. Complete a full practice session
3. Review your performance summary
4. Experiment with both CLI and web interfaces

### For Developers
1. Read the [Architecture Guide](../architecture.md)
2. Review the [API Documentation](api.yaml)
3. Examine the [Data Models](data-model.md)
4. Run the test suite and ensure 90% coverage
5. Contribute to the codebase following the SOLID principles

### For System Administrators
1. Configure production settings
2. Set up monitoring and logging
3. Deploy using Docker or similar containerization
4. Configure backup for question bank data

## Additional Resources

- **Full Documentation**: [docs/](../docs/)
- **API Reference**: http://localhost:8000/docs
- **Test Reports**: `htmlcov/index.html` (after running tests)
- **Configuration Guide**: [docs/configuration.md](../docs/configuration.md)
- **Deployment Guide**: [docs/deployment.md](../docs/deployment.md)

---

**Need Help?** Check the [troubleshooting section](#troubleshooting) or open an issue in the project repository.
