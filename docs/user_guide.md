# Q&A Practice Application - User Guide

This guide provides instructions for setting up and running the Q&A Practice Application, including the backend API, web application, and CLI interface.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Running the Backend API](#running-the-backend-api)
4. [Running the Web Application](#running-the-web-application)
5. [Running the CLI Interface](#running-the-cli-interface)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before running the application, ensure you have the following installed:

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| **Python** | 3.12+ | Backend and web runtime |
| **uv** | Latest | Python package manager (recommended) |

### Verify Installation

```bash
# Check Python version
python --version  # Should be 3.12 or higher

# Check uv (optional but recommended)
uv --version
```

### Installing uv (Recommended)

If you don't have `uv` installed, you can install it with:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

---

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd q_and_a_practise1
```

### 2. Install Backend Dependencies

Using `uv` (recommended):
```bash
uv sync
```

Or using `pip`:
```bash
pip install -r requirements.txt
```

---

## Running the Backend API

The backend is a FastAPI application that provides RESTful endpoints for the Q&A practice functionality.

### Start the Backend Server

Using `uv`:
```bash
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Or using Python directly:
```bash
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Access the API

Once the server is running, you can access:

| URL | Description |
|-----|-------------|
| `http://localhost:8000` | API root |
| `http://localhost:8000/docs` | **Swagger UI** - Interactive API documentation |
| `http://localhost:8000/redoc` | ReDoc - Alternative API documentation |
| `http://localhost:8000/openapi.json` | OpenAPI specification (JSON) |

### Swagger Documentation

The Swagger UI at `http://localhost:8000/docs` provides:

- **Interactive API testing** - Try out endpoints directly in the browser
- **Request/Response schemas** - View expected data formats
- **Authentication** - Test authenticated endpoints
- **API versioning** - See available API versions

#### Available API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/topics` | GET | List available topics |
| `/api/difficulties` | GET | List difficulty levels |
| `/api/sessions` | POST | Create a new quiz session |
| `/api/sessions/{id}` | GET | Get session details |
| `/api/sessions/{id}/questions` | GET | Get questions for a session |
| `/api/sessions/{id}/answer` | POST | Submit an answer |
| `/api/sessions/{id}/score` | GET | Get session score |
| `/api/questions` | GET | List all questions |

### Backend Configuration

The backend can be configured via environment variables:

```bash
# Set custom port
export PORT=8000

# Set log level
export LOG_LEVEL=INFO

# Set data file path
export DATA_FILE=src/main/resources/question-bank.csv
```

---

## Running the Web Application

The web application is a Python-based FastAPI application with Jinja2 templates that provides a modern web interface for the Q&A practice.

### Start the Web Application Server

Using `uv`:
```bash
uv run uvicorn src.web.main:app --reload --host 0.0.0.0 --port 8000
```

Or using Python directly:
```bash
python -m uvicorn src.web.main:app --reload --host 0.0.0.0 --port 8000
```

### Access the Web Application

Once the server is running:

| URL | Description |
|-----|-------------|
| `http://localhost:8000` | Web application home page |
| `http://localhost:8000/docs` | Swagger API documentation |
| `http://localhost:8000/about` | About page |

### Web Application Features

The web application provides:

- **Topic Selection** - Choose from Physics, Chemistry, or Math
- **Difficulty Selection** - Select Easy, Medium, or Hard
- **Interactive Quiz** - Answer multiple-choice questions
- **Real-time Feedback** - See correct/incorrect answers immediately
- **Score Summary** - View detailed performance statistics
- **Question Review** - Review all questions and answers after completion

---

## Running the CLI Interface

The CLI (Command Line Interface) provides a terminal-based interface for practicing Q&A questions.

### Start the CLI Application

Using `uv`:
```bash
uv run python -m src.cli.main
```

Or using Python directly:
```bash
python -m src.cli.main
```

### CLI Options

```bash
# Show help
uv run python -m src.cli.main --help

# List available topics
uv run python -m src.cli.main --list-topics

# List difficulty levels
uv run python -m src.cli.main --list-difficulties

# Show statistics
uv run python -m src.cli.main --stats

# Start session with specific topic and difficulty
uv run python -m src.cli.main --topic Physics --difficulty Easy

# Verbose mode (show debug logs)
uv run python -m src.cli.main --verbose

# Quiet mode (minimal output)
uv run python -m src.cli.main --quiet

# Specify custom data file
uv run python -m src.cli.main --data-file path/to/questions.csv
```

### Interactive Session

When you start the CLI without specifying topic/difficulty, it will prompt you interactively:

```
🎯 Q&A Practice Application
========================================

📚 Available Topics:
  1. Physics (15 questions)
  2. Chemistry (15 questions)
  3. Math (15 questions)

Select a topic (1-3): 1

🎯 Available Difficulty Levels:
  1. Easy
  2. Medium
  3. Hard

Select difficulty (1-3): 1

Starting session: Physics - Easy
========================================

Question 1 of 10:
What is Newton's first law?

  A) Inertia
  B) F=ma
  C) Action-reaction
  D) Gravity

Your answer (A/B/C/D): A

✓ Correct!
```

### CLI Commands During Session

| Command | Action |
|---------|--------|
| `A`, `B`, `C`, `D` | Select answer option |
| `quit` or `exit` | End session early |
| `skip` | Skip current question |
| `hint` | Show hint (if available) |

---

## Troubleshooting

### Common Issues

#### Backend won't start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill the process using the port
kill -9 <PID>
```

#### Missing dependencies

```bash
# Reinstall dependencies
uv sync --reinstall
```

#### Question data not loading

Ensure the question bank CSV file exists:
```bash
ls -la src/main/resources/question-bank.csv
```

### Getting Help

- Check the [README.md](../README.md) for project overview
- Review the [API documentation](http://localhost:8000/docs) for endpoint details
- Check logs for error messages (use `--verbose` flag for CLI)

---

## Quick Start Summary

```bash
# 1. Install dependencies
uv sync

# 2. Start the web application (includes API)
uv run uvicorn src.web.main:app --reload --port 8000

# 3. Or start API-only backend
uv run uvicorn src.api.main:app --reload --port 8000

# to stop the server press Ctrl+C .. else use the following command
lsof -ti :8000 | xargs kill -9 2>/dev/null; echo "Server stopped"

# 4. Or use CLI instead
uv run python -m src.cli.main
```

**Access Points:**
- Web Application: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- API Root: http://localhost:8000/api
