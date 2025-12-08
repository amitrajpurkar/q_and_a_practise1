"""
FastAPI web application for Q&A Practice Application.

Sets up the FastAPI application with web templates, static files,
and API endpoints following SOLID principles.
"""

from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import time
from typing import Dict, Any, Optional
import uvicorn

from src.utils.config import get_app_config, load_app_config, AppConfig
from src.utils.logging_config import setup_logging, get_logger
from src.utils.exceptions import (
    QAAException,
    ValidationError,
    SessionError,
    QuestionError,
    ScoreError,
)
from src.api.routes import topics, difficulties, questions, sessions, scores
from src.services.di_setup import setup_dependency_injection


class QAAWebApp:
    """
    FastAPI web application wrapper for Q&A Practice Application.

    Follows Single Responsibility principle by handling
    only application setup and configuration.
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize FastAPI web application.

        Args:
            config: Application configuration
        """
        self.config = config
        self.logger = get_logger(__name__)
        self.app = self._create_app()
        self.templates = Jinja2Templates(directory="src/web/templates")
        self._setup_middleware()
        self._setup_static_files()
        self._setup_routes()
        self._setup_exception_handlers()

    def _create_app(self) -> FastAPI:
        """Create FastAPI application instance."""
        return FastAPI(
            title="Q&A Practice Application",
            description="A standalone application for practicing questions with dual CLI and web interfaces",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc",
            debug=self.config.debug,
        )

    def _setup_middleware(self) -> None:
        """Setup application middleware."""
        # CORS middleware
        origins = [
            "http://localhost:8000",
            "http://localhost:3000",
            "http://127.0.0.1:8000",
            "http://127.0.0.1:3000",
        ]

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
        )

        # Request logging middleware
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            start_time = time.time()

            # Log request
            self.logger.info(
                f"Request started: {request.method} {request.url.path}",
                extra={
                    "event_type": "http_request_start",
                    "method": request.method,
                    "path": request.url.path,
                    "query_params": str(request.query_params),
                },
            )

            # Process request
            response = await call_next(request)

            # Calculate duration
            process_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            # Log response
            self.logger.info(
                f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                extra={
                    "event_type": "http_request_complete",
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(process_time, 2),
                },
            )

            # Add response header
            response.headers["X-Process-Time"] = str(round(process_time, 2))

            return response

    def _setup_static_files(self) -> None:
        """Setup static file serving."""
        self.app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

    def _setup_routes(self) -> None:
        """Setup application routes."""
        # Include API routers from different modules
        self.app.include_router(topics.router, prefix="/api/v1/topics", tags=["topics"])

        self.app.include_router(
            difficulties.router, prefix="/api/v1/difficulties", tags=["difficulties"]
        )

        self.app.include_router(
            questions.router, prefix="/api/v1/questions", tags=["questions"]
        )

        self.app.include_router(
            sessions.router, prefix="/api/v1/sessions", tags=["sessions"]
        )

        self.app.include_router(scores.router, prefix="/api/v1/scores", tags=["scores"])

        def reset_csv_asked_flags():
            """Reset all asked_in_this_session flags to FALSE in the CSV."""
            try:
                import csv
                from pathlib import Path
                
                csv_path = Path("src/main/resources/question-bank.csv")
                updated_rows = []
                
                with open(csv_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    fieldnames = reader.fieldnames
                    
                    for row in reader:
                        row['asked_in_this_session'] = 'FALSE'
                        row['got_right'] = 'FALSE'
                        updated_rows.append(row)
                
                with open(csv_path, 'w', encoding='utf-8', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(updated_rows)
                    
                self.logger.info("Reset CSV asked flags for new session")
                return True
            except Exception as e:
                self.logger.error(f"Failed to reset CSV: {str(e)}")
                return False

        # Web page routes
        @self.app.get("/", response_class=HTMLResponse, tags=["web"])
        async def index(request: Request):
            """Main page with topic and difficulty selection."""
            return self.templates.TemplateResponse("index.html", {"request": request})

        @self.app.get("/about", response_class=HTMLResponse, tags=["web"])
        async def about(request: Request):
            """About page with application information."""
            return self.templates.TemplateResponse("about.html", {"request": request})

        @self.app.get("/quiz", response_class=HTMLResponse, tags=["web"])
        async def quiz_page(request: Request):
            """Quiz page."""
            return self.templates.TemplateResponse("quiz.html", {"request": request})

        @self.app.get("/quiz/{session_id}", response_class=HTMLResponse, tags=["web"])
        async def quiz_page_with_session(request: Request, session_id: str):
            """Quiz page with session ID."""
            # Reset CSV flags for new session
            reset_csv_asked_flags()
            
            # Get actual session data from the session service via DI container
            try:
                from src.utils.container import get_container
                from src.services.interfaces import ISessionService
                container = get_container()
                session_service = container.resolve(ISessionService)
                session_data = session_service.get_session(session_id)
                if session_data:
                    self.logger.info(f"Found session {session_id}: topic={session_data.topic}, difficulty={session_data.difficulty}")
                    return self.templates.TemplateResponse("quiz.html", {
                        "request": request, 
                        "session_id": session_id,
                        "session": {
                            "session_id": session_id,
                            "topic": session_data.topic,
                            "difficulty": session_data.difficulty, 
                            "total_questions": session_data.total_questions,
                            "current_question_index": 0,
                            "is_active": True
                        }
                    })
                else:
                    self.logger.warning(f"Session {session_id} not found in session service")
            except Exception as e:
                self.logger.error(f"Failed to get session {session_id}: {e}")
            
            # Fallback: Parse topic and difficulty from query params if session not found
            topic = request.query_params.get("topic", "Physics")
            difficulty = request.query_params.get("difficulty", "Easy")
            
            return self.templates.TemplateResponse("quiz.html", {
                "request": request, 
                "session_id": session_id,
                "session": {
                    "session_id": session_id,
                    "topic": topic,
                    "difficulty": difficulty, 
                    "total_questions": 10,
                    "current_question_index": 0,
                    "is_active": True
                }
            })

        @self.app.get("/results", response_class=HTMLResponse, tags=["web"])
        async def results_page(request: Request):
            """Results page."""
            return self.templates.TemplateResponse("results.html", {
                "request": request,
                "session_id": "demo",
                "session": {
                    "session_id": "demo",
                    "topic": "Physics",
                    "difficulty": "Medium",
                    "total_questions": 10,
                    "correct_answers": 7,
                    "incorrect_answers": 2,
                    "skipped_answers": 1,
                    "score_percentage": 70.0,
                    "time_taken": "05:32",
                    "completion_time": "2025-12-04 19:00:00",
                    "start_time": "2025-12-04 18:55:00",
                    "end_time": "2025-12-04 19:00:00"
                },
                "score": {
                    "accuracy": 70.0,
                    "total_questions": 10,
                    "total_answered": 9,
                    "correct_answers": 7,
                    "incorrect_answers": 2,
                    "skipped_answers": 1,
                    "time_taken": "05:32"
                }
            })

        @self.app.get("/results/{session_id}", response_class=HTMLResponse, tags=["web"])
        async def results_page_with_session(
            request: Request, 
            session_id: str,
            topic: str = "Physics",
            difficulty: str = "Medium", 
            total_questions: int = 10,
            correct_answers: int = 0,
            incorrect_answers: int = 0,
            skipped_answers: int = 0,
            accuracy: float = 0.0,
            time_taken: str = "00:00"
        ):
            """Results page with session ID."""
            try:
                # Use actual quiz data from URL parameters
                return self.templates.TemplateResponse("results.html", {
                    "request": request,
                    "session_id": session_id,
                    "session": {
                        "session_id": session_id,
                        "topic": topic,
                        "difficulty": difficulty,
                        "total_questions": total_questions,
                        "correct_answers": correct_answers,
                        "incorrect_answers": incorrect_answers,
                        "skipped_answers": skipped_answers,
                        "score_percentage": accuracy,
                        "time_taken": time_taken,
                        "completion_time": "2025-12-04 19:00:00",
                        "start_time": "2025-12-04 18:55:00",
                        "end_time": "2025-12-04 19:00:00"
                    },
                    "score": {
                        "accuracy": accuracy,
                        "total_questions": total_questions,
                        "total_answered": correct_answers + incorrect_answers,
                        "correct_answers": correct_answers,
                        "incorrect_answers": incorrect_answers,
                        "skipped_answers": skipped_answers,
                        "time_taken": time_taken
                    }
                })
            except Exception as e:
                self.logger.error(f"Error loading results: {str(e)}")
                return self.templates.TemplateResponse("404.html", {
                    "request": request,
                    "error": f"Error loading results for session {session_id}"
                })

        @self.app.post("/validate-answer", response_class=HTMLResponse, tags=["web"])
        async def validate_answer(request: Request):
            """Validate answer against CSV data and return feedback."""
            try:
                import csv
                from pathlib import Path
                
                # Get form data - HTMX sends as form data when using values parameter
                form = await request.form()
                question_id = form.get('question_id', '')
                answer = form.get('answer', '')
                
                self.logger.info(f"Validating - Q: {repr(question_id)} A: {repr(answer)}")
                
                csv_path = Path("src/main/resources/question-bank.csv")
                correct_answer = None
                is_correct = False
                
                # Find the question in CSV and get correct answer
                with open(csv_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        # Try exact match first
                        if row['question'].strip() == question_id.strip():
                            correct_answer = row['answer'].strip()
                            # Simple string comparison with normalization
                            is_correct = answer.strip() == correct_answer
                            self.logger.info(f"Match found - CSV: {repr(correct_answer)} User: {repr(answer)} -> {is_correct}")
                            break
                
                if not correct_answer:
                    # Fallback for demo questions
                    correct_answer = "Newton"
                    is_correct = (answer.strip() == correct_answer)
                    self.logger.info(f"Fallback - User: {repr(answer)} -> {is_correct}")
                
                # Return feedback HTML
                feedback_class = "correct-answer" if is_correct else "incorrect-answer"
                feedback_icon = "✓" if is_correct else "✗"
                feedback_text = "Correct!" if is_correct else f"Incorrect. The correct answer is: {correct_answer}"
                
                bg_class = "bg-green-100 border-green-300" if is_correct else "bg-red-100 border-red-300"
                text_class = "text-green-600" if is_correct else "text-red-600"
                text_class_medium = "text-green-800" if is_correct else "text-red-800"
                
                feedback_html = f'''
                <div id="feedback-section" class="{feedback_class}" data-correct-answer="{correct_answer}" data-is-correct="{'true' if is_correct else 'false'}">
                    <div class="p-4 rounded-lg {bg_class} border">
                        <div class="flex items-center">
                            <span class="text-2xl mr-2 {text_class}">{feedback_icon}</span>
                            <span class="font-medium {text_class_medium}">{feedback_text}</span>
                        </div>
                    </div>
                    <script>window.lastAnswerCorrect = {str(is_correct).lower()};</script>
                </div>
                '''
                
                # Debug: Log the HTML being generated
                self.logger.info(f"Generated HTML snippet: {feedback_html[:200]}...")
                
                return HTMLResponse(content=feedback_html)
                
            except Exception as e:
                self.logger.error(f"Error validating answer: {str(e)}")
                return HTMLResponse(content="<div class='text-red-600 p-4'>Error validating answer</div>")

        @self.app.get("/question", response_class=HTMLResponse, tags=["web"])
        async def question_html(request: Request, topic: str, difficulty: str):
            """Return question as HTML for HTMX loading."""
            try:
                self.logger.info(f"Loading question for {topic}-{difficulty}")
                
                # Load questions from CSV file
                import csv
                import random
                from pathlib import Path
                
                csv_path = Path("src/main/resources/question-bank.csv")
                questions = []
                updated_rows = []
                
                try:
                    with open(csv_path, 'r', encoding='utf-8') as file:
                        reader = csv.DictReader(file)
                        fieldnames = reader.fieldnames
                        
                        for row in reader:
                            # Filter questions by topic and difficulty that haven't been asked
                            if (row['topic'].strip() == topic and 
                                row['difficulty'].strip() == difficulty and 
                                row['asked_in_this_session'].strip().upper() == 'FALSE'):
                                questions.append({
                                    "id": f"{topic.lower()}-{difficulty.lower()}-{len(questions)}",
                                    "question_text": row['question'].strip(),
                                    "options": [
                                        row['option1'].strip(),
                                        row['option2'].strip(), 
                                        row['option3'].strip(),
                                        row['option4'].strip()
                                    ],
                                    "correct_answer": row['answer'].strip(),
                                    "csv_row": row  # Keep reference to original row
                                    })
                            # Always add row to updated_rows to preserve all data
                            updated_rows.append(row)
                            
                except FileNotFoundError:
                    self.logger.error(f"Question bank file not found at {csv_path}")
                    # Fallback to sample questions
                    questions = [{
                        "id": "fallback_1",
                        "question_text": f"Sample {topic} {difficulty} question",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": "Option A",
                        "csv_row": None
                    }]
                
                if not questions:
                    # Fallback if no unasked questions found
                    question_data = {
                        "id": "no_questions",
                        "question_text": f"No more questions available for {topic} {difficulty}",
                        "options": ["N/A", "N/A", "N/A", "N/A"],
                        "correct_answer": "N/A"
                    }
                else:
                    # Select a random question
                    selected_question = random.choice(questions)
                    question_data = {
                        "id": selected_question["id"],
                        "question_text": selected_question["question_text"],
                        "options": selected_question["options"],
                        "correct_answer": selected_question["correct_answer"]
                    }
                    
                    # Update the CSV to mark this question as asked
                    if selected_question["csv_row"]:
                        for i, row in enumerate(updated_rows):
                            if (row['question'].strip() == selected_question["csv_row"]["question"].strip() and
                                row['topic'].strip() == topic and
                                row['difficulty'].strip() == difficulty):
                                updated_rows[i]['asked_in_this_session'] = 'TRUE'
                                break
                        
                        # Write updated data back to CSV
                        try:
                            with open(csv_path, 'w', encoding='utf-8', newline='') as file:
                                writer = csv.DictWriter(file, fieldnames=fieldnames)
                                writer.writeheader()
                                writer.writerows(updated_rows)
                            self.logger.info(f"Marked question as asked: {selected_question['question_text'][:50]}...")
                        except Exception as e:
                            self.logger.error(f"Failed to update CSV: {str(e)}")
                
                self.logger.info(f"Selected question: {question_data['question_text'][:50]}...")
                
                return self.templates.TemplateResponse("question.html", {
                    "request": request,
                    **question_data
                })
                
            except Exception as e:
                self.logger.error(f"Error loading question: {str(e)}")
                return HTMLResponse(
                    content=f"<div class='text-red-600 p-4'>Error: {str(e)}</div>",
                    status_code=500
                )

        # Health check endpoint
        @self.app.get("/health", tags=["health"])
        async def health_check() -> Dict[str, Any]:
            """Health check endpoint."""
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "version": "1.0.0",
                "debug": self.config.debug,
            }

        # Statistics endpoint for home page counters
        @self.app.get("/api/v1/statistics", tags=["statistics"])
        async def get_statistics() -> Dict[str, Any]:
            """Get application statistics for home page counters."""
            import csv
            from pathlib import Path
            
            csv_path = Path("src/main/resources/question-bank.csv")
            total_questions = 0
            questions_by_topic = {}
            questions_by_difficulty = {}
            
            try:
                with open(csv_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        total_questions += 1
                        topic = row.get('topic', 'Unknown').strip()
                        difficulty = row.get('difficulty', 'Unknown').strip()
                        
                        # Count by topic
                        if topic not in questions_by_topic:
                            questions_by_topic[topic] = 0
                        questions_by_topic[topic] += 1
                        
                        # Count by difficulty
                        if difficulty not in questions_by_difficulty:
                            questions_by_difficulty[difficulty] = 0
                        questions_by_difficulty[difficulty] += 1
                        
            except FileNotFoundError:
                self.logger.error(f"Question bank file not found at {csv_path}")
                total_questions = 0
            except Exception as e:
                self.logger.error(f"Error reading question bank: {str(e)}")
                total_questions = 0
            
            # Get session statistics from session service
            completed_sessions = 0
            average_score = 0.0
            
            try:
                from src.utils.container import get_container
                from src.services.interfaces import ISessionService
                container = get_container()
                session_service = container.resolve(ISessionService)
                
                # Get completed sessions count and average score
                # Note: This depends on session service implementation
                if hasattr(session_service, 'get_completed_sessions_count'):
                    completed_sessions = session_service.get_completed_sessions_count()
                if hasattr(session_service, 'get_average_score'):
                    average_score = session_service.get_average_score()
            except Exception as e:
                self.logger.warning(f"Could not get session statistics: {str(e)}")
                # Use defaults
                completed_sessions = 0
                average_score = 0.0
            
            return {
                "total_questions": total_questions,
                "completed_sessions": completed_sessions,
                "average_score": round(average_score, 1),
                "questions_by_topic": questions_by_topic,
                "questions_by_difficulty": questions_by_difficulty
            }

        # Root endpoint
        @self.app.get("/api", tags=["root"])
        async def api_root() -> Dict[str, Any]:
            """Root endpoint with API information."""
            return {
                "name": "Q&A Practice Application",
                "version": "1.0.0",
                "description": "A standalone application for practicing questions with dual CLI and web interfaces",
                "docs_url": (
                    "/docs"
                    if self.config.debug
                    else "Documentation disabled in production"
                ),
                "health_url": "/health",
                "web_url": "/",
            }

    def _setup_exception_handlers(self) -> None:
        """Setup custom exception handlers."""

        @self.app.exception_handler(ValidationError)
        async def validation_exception_handler(request: Request, exc: ValidationError):
            """Handle validation errors."""
            self.logger.warning(
                f"Validation error: {str(exc)}",
                extra={
                    "event_type": "validation_error",
                    "field": exc.field,
                    "value": exc.value,
                    "path": request.url.path,
                },
            )
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Validation Error",
                    "message": str(exc),
                    "field": exc.field,
                    "error_code": exc.error_code,
                },
            )

        @self.app.exception_handler(SessionError)
        async def session_exception_handler(request: Request, exc: SessionError):
            """Handle session errors."""
            self.logger.warning(
                f"Session error: {str(exc)}",
                extra={
                    "event_type": "session_error",
                    "session_id": exc.session_id,
                    "path": request.url.path,
                },
            )
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Session Error",
                    "message": str(exc),
                    "session_id": exc.session_id,
                    "error_code": exc.error_code,
                },
            )

        @self.app.exception_handler(QuestionError)
        async def question_exception_handler(request: Request, exc: QuestionError):
            """Handle question errors."""
            self.logger.warning(
                f"Question error: {str(exc)}",
                extra={
                    "event_type": "question_error",
                    "question_id": exc.question_id,
                    "path": request.url.path,
                },
            )
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Question Error",
                    "message": str(exc),
                    "question_id": exc.question_id,
                    "error_code": exc.error_code,
                },
            )

        @self.app.exception_handler(ScoreError)
        async def score_exception_handler(request: Request, exc: ScoreError):
            """Handle score errors."""
            self.logger.warning(
                f"Score error: {str(exc)}",
                extra={
                    "event_type": "score_error",
                    "session_id": exc.session_id,
                    "path": request.url.path,
                },
            )
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Score Error",
                    "message": str(exc),
                    "session_id": exc.session_id,
                    "error_code": exc.error_code,
                },
            )

        @self.app.exception_handler(QAAException)
        async def qa_exception_handler(request: Request, exc: QAAException):
            """Handle general Q&A application errors."""
            self.logger.error(
                f"Application error: {str(exc)}",
                extra={
                    "event_type": "application_error",
                    "error_code": exc.error_code,
                    "path": request.url.path,
                    "details": exc.details,
                },
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Application Error",
                    "message": str(exc),
                    "error_code": exc.error_code,
                },
            )

        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            """Handle unexpected errors."""
            self.logger.error(
                f"Unexpected error: {str(exc)}",
                extra={
                    "event_type": "unexpected_error",
                    "path": request.url.path,
                    "exception_type": type(exc).__name__,
                },
            )
            
            def reset_csv_asked_flags():
                """Reset all asked_in_this_session flags to FALSE in the CSV."""
                try:
                    import csv
                    from pathlib import Path
                    
                    csv_path = Path("src/main/resources/question-bank.csv")
                    updated_rows = []
                    
                    with open(csv_path, 'r', encoding='utf-8') as file:
                        reader = csv.DictReader(file)
                        fieldnames = reader.fieldnames
                        
                        for row in reader:
                            row['asked_in_this_session'] = 'FALSE'
                            row['got_right'] = 'FALSE'
                            updated_rows.append(row)
                    
                    with open(csv_path, 'w', encoding='utf-8', newline='') as file:
                        writer = csv.DictWriter(file, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(updated_rows)
                        
                    self.logger.info("Reset CSV asked flags for new session")
                    return True
                except Exception as e:
                    self.logger.error(f"Failed to reset CSV: {str(e)}")
                    return False

            # For web routes, return error page
            if request.url.path.startswith("/api"):
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "Internal Server Error",
                        "message": "An unexpected error occurred",
                        "error_code": "INTERNAL_ERROR",
                    },
                )
            else:
                # Return error page for web routes
                return self.templates.TemplateResponse(
                    "error.html", 
                    {
                        "request": request,
                        "error_code": 500,
                        "error_details": str(exc),
                        "error_id": f"ERR_{int(time.time())}"
                    }
                )

    def get_app(self) -> FastAPI:
        """
        Get the FastAPI application instance.

        Returns:
            FastAPI application
        """
        return self.app


# Global application instance
_app_instance: QAAWebApp


def create_app(config: Optional[AppConfig] = None) -> FastAPI:
    """
    Create and configure FastAPI web application.

    Args:
        config: Optional application configuration

    Returns:
        Configured FastAPI application
    """

    if config is None:
        config = load_app_config()

    # Setup dependencies first ( this will also setup logging)
    setup_dependency_injection(config)

    # Create application
    _app_instance = QAAWebApp(config)

    logger = get_logger(__name__)
    logger.info(
        "FastAPI web application created successfully",
        extra={
            "event_type": "application_created",
            "debug": config.debug,
            "host": config.host,
            "port": config.port,
        },
    )

    return _app_instance.get_app()


def get_app() -> FastAPI:
    """
    Get the FastAPI application instance.

    Returns:
        FastAPI application instance

    Raises:
        Exception: If application not created
    """
    global _app_instance
    if _app_instance is None:
        raise Exception("Application not created. Call create_app() first.")
    return _app_instance.get_app()


# Module-level app instance for uvicorn
def _create_app_instance():
    """Create the FastAPI web application instance."""
    return create_app()


# Create app instance at module level for uvicorn
app = _create_app_instance()


if __name__ == "__main__":
    # Load configuration
    config = load_app_config()

    # Run server
    print(f"🚀 Starting Q&A Practice Web Application")
    print(f"📍 Server will be available at: http://{config.host}:{config.port}")
    print(f"📖 API Documentation: http://{config.host}:{config.port}/docs")
    print(f"🌐 Web Interface: http://{config.host}:{config.port}")
    
    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        log_level="info"
    )
