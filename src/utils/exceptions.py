"""
Custom exception classes for Q&A Practice Application.

Defines specific exception types following SOLID principles
for better error handling and debugging.
"""

from typing import Optional, Any


class QAAException(Exception):
    """
    Base exception class for Q&A Practice Application.

    All custom exceptions inherit from this base class
    following the Single Responsibility principle.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Any] = None,
    ) -> None:
        """
        Initialize base exception.

        Args:
            message: Error message
            error_code: Optional error code for categorization
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details

    def __str__(self) -> str:
        """String representation of exception."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ValidationError(QAAException):
    """
    Exception raised for data validation errors.

    Used when input data fails validation rules
    following SOLID principles.
    """

    def __init__(
        self, message: str, field: Optional[str] = None, value: Optional[Any] = None
    ) -> None:
        """
        Initialize validation error.

        Args:
            message: Error message
            field: Field that failed validation
            value: Value that failed validation
        """
        super().__init__(message, "VALIDATION_ERROR", {"field": field, "value": value})
        self.field = field
        self.value = value


class CSVParsingError(QAAException):
    """
    Exception raised for CSV parsing errors.

    Used when CSV file cannot be parsed or contains invalid data
    following Single Responsibility principle.
    """

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
    ) -> None:
        """
        Initialize CSV parsing error.

        Args:
            message: Error message
            file_path: Path to the CSV file
            line_number: Line number where error occurred
        """
        super().__init__(
            message,
            "CSV_PARSING_ERROR",
            {"file_path": file_path, "line_number": line_number},
        )
        self.file_path = file_path
        self.line_number = line_number


class SessionError(QAAException):
    """
    Exception raised for session management errors.

    Used when session operations fail following SOLID principles.
    """

    def __init__(self, message: str, session_id: Optional[str] = None) -> None:
        """
        Initialize session error.

        Args:
            message: Error message
            session_id: Session identifier
        """
        super().__init__(message, "SESSION_ERROR", {"session_id": session_id})
        self.session_id = session_id


class QuestionError(QAAException):
    """
    Exception raised for question-related errors.

    Used when question operations fail following Single Responsibility principle.
    """

    def __init__(self, message: str, question_id: Optional[str] = None) -> None:
        """
        Initialize question error.

        Args:
            message: Error message
            question_id: Question identifier
        """
        super().__init__(message, "QUESTION_ERROR", {"question_id": question_id})
        self.question_id = question_id


class ScoreError(QAAException):
    """
    Exception raised for score calculation errors.

    Used when score operations fail following SOLID principles.
    """

    def __init__(self, message: str, session_id: Optional[str] = None) -> None:
        """
        Initialize score error.

        Args:
            message: Error message
            session_id: Session identifier
        """
        super().__init__(message, "SCORE_ERROR", {"session_id": session_id})
        self.session_id = session_id


class ConfigurationError(QAAException):
    """
    Exception raised for configuration errors.

    Used when application configuration is invalid
    following Single Responsibility principle.
    """

    def __init__(self, message: str, config_key: Optional[str] = None) -> None:
        """
        Initialize configuration error.

        Args:
            message: Error message
            config_key: Configuration key that caused the error
        """
        super().__init__(message, "CONFIG_ERROR", {"config_key": config_key})
        self.config_key = config_key


class DependencyInjectionError(QAAException):
    """
    Exception raised for dependency injection errors.

    Used when service resolution fails following SOLID principles.
    """

    def __init__(self, message: str, service_type: Optional[str] = None) -> None:
        """
        Initialize dependency injection error.

        Args:
            message: Error message
            service_type: Type of service that failed to resolve
        """
        super().__init__(message, "DI_ERROR", {"service_type": service_type})
        self.service_type = service_type
