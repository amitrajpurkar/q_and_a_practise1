"""
Structured logging configuration for Q&A Practice Application.

Provides centralized logging setup following SOLID principles
and clean code standards with proper formatting and handlers.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

from src.utils.config import AppConfig
from src.utils.exceptions import ConfigurationError


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter for structured JSON logging.

    Follows Single Responsibility principle by handling
    only log message formatting and structure.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as structured JSON.

        Args:
            record: Log record to format

        Returns:
            Formatted JSON log message
        """
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        for key, value in record.__dict__.items():
            if key not in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
                "exc_info",
                "exc_text",
                "stack_info",
            }:
                log_entry[key] = value

        return json.dumps(log_entry, default=str)

    def format_console(self, record: logging.LogRecord) -> str:
        """
        Format log record for console output.

        Args:
            record: Log record to format

        Returns:
            Formatted console log message
        """
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        level = record.levelname.ljust(8)
        logger = record.name.ljust(20)
        message = record.getMessage()

        return f"{timestamp} {level} {logger} {message}"


class LoggingConfig:
    """
    Logging configuration manager.

    Follows Single Responsibility principle by handling
    only logging setup and configuration.
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize logging configuration.

        Args:
            config: Application configuration
        """
        self.config = config
        self._configured = False

    def setup_logging(self) -> None:
        """Set up structured logging for the application."""
        if self._configured:
            return

        try:
            # Create logs directory if it doesn't exist
            log_file_path = Path(self.config.log_file)
            log_file_path.parent.mkdir(parents=True, exist_ok=True)

            # Configure root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(getattr(logging, self.config.log_level.upper()))

            # Clear existing handlers
            root_logger.handlers.clear()

            # Create formatters
            structured_formatter = StructuredFormatter()
            console_formatter = StructuredFormatter()

            # Console handler with console formatting
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, self.config.log_level.upper()))
            console_handler.setFormatter(console_formatter)

            # File handler with JSON formatting
            file_handler = logging.handlers.RotatingFileHandler(
                filename=self.config.log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding="utf-8",
            )
            file_handler.setLevel(logging.DEBUG)  # Always log DEBUG to file
            file_handler.setFormatter(structured_formatter)

            # Add handlers to root logger
            root_logger.addHandler(console_handler)
            root_logger.addHandler(file_handler)

            # Configure specific loggers
            self._configure_specific_loggers()

            self._configured = True

            # Log initialization message
            logger = logging.getLogger(__name__)
            logger.info(
                "Logging configured successfully",
                extra={
                    "log_level": self.config.log_level,
                    "log_file": self.config.log_file,
                    "debug_mode": self.config.debug,
                },
            )

        except Exception as e:
            raise ConfigurationError(f"Failed to configure logging: {str(e)}")

    def _configure_specific_loggers(self) -> None:
        """Configure specific application loggers."""
        # Configure API logger
        api_logger = logging.getLogger("src.api")
        api_logger.setLevel(logging.INFO)

        # Configure service logger
        service_logger = logging.getLogger("src.services")
        service_logger.setLevel(logging.DEBUG)

        # Configure CLI logger
        cli_logger = logging.getLogger("src.cli")
        cli_logger.setLevel(logging.INFO)

        # Configure web logger
        web_logger = logging.getLogger("src.web")
        web_logger.setLevel(logging.INFO)

        # Configure utility loggers
        utils_logger = logging.getLogger("src.utils")
        utils_logger.setLevel(logging.DEBUG)

        # Reduce noise from external libraries
        logging.getLogger("uvicorn").setLevel(logging.WARNING)
        logging.getLogger("fastapi").setLevel(logging.WARNING)
        logging.getLogger("pandas").setLevel(logging.WARNING)

    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a configured logger instance.

        Args:
            name: Logger name

        Returns:
            Configured logger instance
        """
        if not self._configured:
            self.setup_logging()

        return logging.getLogger(name)

    def log_request(
        self,
        logger: logging.Logger,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        **kwargs,
    ) -> None:
        """
        Log HTTP request information.

        Args:
            logger: Logger instance
            method: HTTP method
            path: Request path
            status_code: Response status code
            duration_ms: Request duration in milliseconds
            **kwargs: Additional request metadata
        """
        logger.info(
            f"{method} {path} - {status_code}",
            extra={
                "event_type": "http_request",
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": duration_ms,
                **kwargs,
            },
        )

    def log_session_event(
        self, logger: logging.Logger, session_id: str, event_type: str, **kwargs
    ) -> None:
        """
        Log session-related events.

        Args:
            logger: Logger instance
            session_id: Session identifier
            event_type: Type of session event
            **kwargs: Additional session metadata
        """
        logger.info(
            f"Session {event_type}: {session_id}",
            extra={
                "event_type": "session_event",
                "session_id": session_id,
                "session_event": event_type,
                **kwargs,
            },
        )

    def log_performance_metric(
        self,
        logger: logging.Logger,
        metric_name: str,
        value: float,
        unit: str,
        **kwargs,
    ) -> None:
        """
        Log performance metrics.

        Args:
            logger: Logger instance
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
            **kwargs: Additional metric metadata
        """
        logger.info(
            f"Performance metric: {metric_name} = {value} {unit}",
            extra={
                "event_type": "performance_metric",
                "metric_name": metric_name,
                "metric_value": value,
                "metric_unit": unit,
                **kwargs,
            },
        )


# Global logging configuration instance
_logging_config: LoggingConfig


def setup_logging(config: AppConfig) -> LoggingConfig:
    """
    Set up application logging.

    Args:
        config: Application configuration

    Returns:
        Configured logging instance
    """
    global _logging_config
    _logging_config = LoggingConfig(config)
    _logging_config.setup_logging()
    return _logging_config


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    global _logging_config
    if _logging_config is None:
        # Default configuration if not set up
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(name)

    return _logging_config.get_logger(name)
