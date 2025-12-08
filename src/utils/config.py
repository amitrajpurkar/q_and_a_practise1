"""
Configuration management for Q&A Practice Application.

Handles environment variables and application settings
following SOLID principles and clean code standards.
"""

import os
from typing import Optional
from pathlib import Path
from dataclasses import dataclass
import logging

from src.utils.exceptions import ConfigurationError


@dataclass
class AppConfig:
    """
    Application configuration data class.

    Follows Single Responsibility principle by containing
    only configuration data and validation logic.
    """

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # File Paths
    question_bank_path: str = "src/main/resources/question-bank.csv"
    log_file: str = "logs/app.log"

    # Logging Configuration
    log_level: str = "INFO"

    # Session Configuration
    default_session_length: int = 10
    max_session_length: int = 50
    min_session_length: int = 5

    # Performance Configuration
    csv_parsing_timeout: int = 5  # seconds
    ui_response_timeout: int = 200  # milliseconds

    # Testing Configuration
    test_coverage_threshold: int = 90
    test_data_path: str = "tests/data/"

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate configuration values."""
        # Validate port
        if not (1 <= self.port <= 65535):
            raise ConfigurationError(f"Invalid port number: {self.port}", "port")

        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_log_levels:
            raise ConfigurationError(
                f"Invalid log level: {self.log_level}. Must be one of: {valid_log_levels}",
                "log_level",
            )

        # Validate session lengths
        if not (1 <= self.min_session_length <= self.max_session_length):
            raise ConfigurationError(
                "min_session_length must be less than or equal to max_session_length",
                "session_length",
            )

        if not (
            self.min_session_length
            <= self.default_session_length
            <= self.max_session_length
        ):
            raise ConfigurationError(
                "default_session_length must be between min_session_length and max_session_length",
                "default_session_length",
            )

        # Validate timeouts
        if self.csv_parsing_timeout <= 0:
            raise ConfigurationError(
                "csv_parsing_timeout must be positive", "csv_parsing_timeout"
            )

        if self.ui_response_timeout <= 0:
            raise ConfigurationError(
                "ui_response_timeout must be positive", "ui_response_timeout"
            )

        # Validate coverage threshold
        if not (0 <= self.test_coverage_threshold <= 100):
            raise ConfigurationError(
                "test_coverage_threshold must be between 0 and 100",
                "test_coverage_threshold",
            )


class ConfigManager:
    """
    Configuration manager for the application.

    Follows Single Responsibility principle by handling
    only configuration loading and management.
    """

    def __init__(self, env_file: Optional[str] = None) -> None:
        """
        Initialize configuration manager.

        Args:
            env_file: Optional path to .env file
        """
        self.env_file = env_file
        self.logger = logging.getLogger(__name__)
        self._config: Optional[AppConfig] = None

    def load_config(self) -> AppConfig:
        """
        Load configuration from environment variables.

        Returns:
            Loaded application configuration

        Raises:
            ConfigurationError: If configuration loading fails
        """
        try:
            # Load .env file if specified
            if self.env_file and Path(self.env_file).exists():
                self._load_env_file(self.env_file)

            # Create configuration from environment variables
            config = AppConfig(
                host=os.getenv("QA_HOST", "0.0.0.0"),
                port=int(os.getenv("QA_PORT", "8000")),
                debug=os.getenv("QA_DEBUG", "false").lower() == "true",
                question_bank_path=os.getenv(
                    "QA_QUESTION_BANK_PATH", "src/main/resources/question-bank.csv"
                ),
                log_file=os.getenv("QA_LOG_FILE", "logs/app.log"),
                log_level=os.getenv("QA_LOG_LEVEL", "INFO"),
                default_session_length=int(
                    os.getenv("QA_DEFAULT_SESSION_LENGTH", "10")
                ),
                max_session_length=int(os.getenv("QA_MAX_SESSION_LENGTH", "50")),
                min_session_length=int(os.getenv("QA_MIN_SESSION_LENGTH", "5")),
                csv_parsing_timeout=int(os.getenv("QA_CSV_PARSING_TIMEOUT", "5")),
                ui_response_timeout=int(os.getenv("QA_UI_RESPONSE_TIMEOUT", "200")),
                test_coverage_threshold=int(
                    os.getenv("QA_TEST_COVERAGE_THRESHOLD", "90")
                ),
                test_data_path=os.getenv("QA_TEST_DATA_PATH", "tests/data/"),
            )

            self._config = config
            self.logger.info("Configuration loaded successfully")
            return config

        except ValueError as e:
            raise ConfigurationError(f"Invalid configuration value: {str(e)}")
        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            raise ConfigurationError(f"Failed to load configuration: {str(e)}")

    def get_config(self) -> AppConfig:
        """
        Get current configuration.

        Returns:
            Current application configuration

        Raises:
            ConfigurationError: If configuration is not loaded
        """
        if self._config is None:
            raise ConfigurationError(
                "Configuration not loaded. Call load_config() first."
            )
        return self._config

    def _load_env_file(self, env_file: str) -> None:
        """
        Load environment variables from .env file.

        Args:
            env_file: Path to .env file
        """
        try:
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        os.environ[key] = value
        except Exception as e:
            raise ConfigurationError(f"Failed to load .env file: {str(e)}", "env_file")

    def get_database_url(self) -> str:
        """
        Get database URL (placeholder for future database integration).

        Returns:
            Database connection string
        """
        return os.getenv("QA_DATABASE_URL", "sqlite:///qa_app.db")

    def get_cors_origins(self) -> list[str]:
        """
        Get CORS origins for web interface.

        Returns:
            List of allowed CORS origins
        """
        origins = os.getenv(
            "QA_CORS_ORIGINS", "http://localhost:8000,http://localhost:3000"
        )
        return [origin.strip() for origin in origins.split(",") if origin.strip()]

    def is_development(self) -> bool:
        """
        Check if running in development mode.

        Returns:
            True if in development mode
        """
        config = self.get_config()
        return (
            config.debug or os.getenv("QA_ENV", "development").lower() == "development"
        )

    def is_production(self) -> bool:
        """
        Check if running in production mode.

        Returns:
            True if in production mode
        """
        return os.getenv("QA_ENV", "development").lower() == "production"


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def load_app_config() -> AppConfig:
    """Load and return application configuration."""
    return get_config_manager().load_config()


def get_app_config() -> AppConfig:
    """Get current application configuration."""
    return get_config_manager().get_config()
