"""
FastAPI main application for Q&A Practice Application.

Sets up the FastAPI application with proper middleware,
routing, and configuration following SOLID principles.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from typing import Dict, Any, Optional

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


class QAAFastAPI:
    """
    FastAPI application wrapper for Q&A Practice Application.

    Follows Single Responsibility principle by handling
    only application setup and configuration.
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize FastAPI application.

        Args:
            config: Application configuration
        """
        self.config = config
        self.logger = get_logger(__name__)
        self.app = self._create_app()
        self._setup_middleware()
        self._setup_routes()
        self._setup_exception_handlers()

    def _create_app(self) -> FastAPI:
        """Create FastAPI application instance."""
        return FastAPI(
            title="Q&A Practice Application",
            description="A standalone application for practicing questions with dual CLI and web interfaces",
            version="1.0.0",
            docs_url="/docs" if self.config.debug else None,
            redoc_url="/redoc" if self.config.debug else None,
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

    def _setup_routes(self) -> None:
        """Setup application routes."""
        # Include routers from different modules
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

        # Root endpoint
        @self.app.get("/", tags=["root"])
        async def root() -> Dict[str, Any]:
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
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred",
                    "error_code": "INTERNAL_ERROR",
                },
            )

    def get_app(self) -> FastAPI:
        """
        Get the FastAPI application instance.

        Returns:
            FastAPI application
        """
        return self.app


# Global application instance
_app_instance: QAAFastAPI


def create_app(config: Optional[AppConfig] = None) -> FastAPI:
    """
    Create and configure FastAPI application.

    Args:
        config: Optional application configuration

    Returns:
        Configured FastAPI application
    """

    if config is None:
        config = get_app_config()

    # Setup dependencies first ( this will also setup logging)
    setup_dependency_injection(config)

    # Create application
    _app_instance = QAAFastAPI(config)

    logger = get_logger(__name__)
    logger.info(
        "FastAPI application created successfully",
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
app = create_app()


if __name__ == "__main__":
    import uvicorn

    # Load configuration
    config = load_app_config()

    # Run server
    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        log_level="info"
    )
