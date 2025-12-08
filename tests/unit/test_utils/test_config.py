"""
Unit tests for configuration management.

Tests AppConfig validation and settings.
"""

import pytest
from typing import Dict, Any

from src.utils.config import AppConfig
from src.utils.exceptions import ConfigurationError


class TestAppConfigCreation:
    """Unit tests for AppConfig creation."""

    def test_create_default_config(self) -> None:
        """Test creating config with default values."""
        config = AppConfig()
        
        assert config.host == "0.0.0.0"
        assert config.port == 8000
        assert config.debug is False
        assert config.log_level == "INFO"

    def test_create_config_with_custom_values(self) -> None:
        """Test creating config with custom values."""
        config = AppConfig(
            host="127.0.0.1",
            port=3000,
            debug=True,
            log_level="DEBUG"
        )
        
        assert config.host == "127.0.0.1"
        assert config.port == 3000
        assert config.debug is True
        assert config.log_level == "DEBUG"


class TestAppConfigValidation:
    """Unit tests for AppConfig validation."""

    def test_invalid_port_too_low_raises_error(self) -> None:
        """Test that port < 1 raises ConfigurationError."""
        with pytest.raises(ConfigurationError):
            AppConfig(port=0)

    def test_invalid_port_too_high_raises_error(self) -> None:
        """Test that port > 65535 raises ConfigurationError."""
        with pytest.raises(ConfigurationError):
            AppConfig(port=70000)

    def test_valid_port_boundary_low(self) -> None:
        """Test that port = 1 is valid."""
        config = AppConfig(port=1)
        assert config.port == 1

    def test_valid_port_boundary_high(self) -> None:
        """Test that port = 65535 is valid."""
        config = AppConfig(port=65535)
        assert config.port == 65535

    def test_invalid_log_level_raises_error(self) -> None:
        """Test that invalid log level raises ConfigurationError."""
        with pytest.raises(ConfigurationError):
            AppConfig(log_level="INVALID")

    def test_valid_log_levels(self) -> None:
        """Test all valid log levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in valid_levels:
            config = AppConfig(log_level=level)
            assert config.log_level == level

    def test_invalid_session_length_min_greater_than_max(self) -> None:
        """Test that min > max session length raises error."""
        with pytest.raises(ConfigurationError):
            AppConfig(min_session_length=20, max_session_length=10)

    def test_invalid_default_session_length_out_of_range(self) -> None:
        """Test that default session length out of range raises error."""
        with pytest.raises(ConfigurationError):
            AppConfig(
                min_session_length=5,
                max_session_length=10,
                default_session_length=15
            )

    def test_invalid_csv_timeout_zero(self) -> None:
        """Test that csv_parsing_timeout = 0 raises error."""
        with pytest.raises(ConfigurationError):
            AppConfig(csv_parsing_timeout=0)

    def test_invalid_csv_timeout_negative(self) -> None:
        """Test that negative csv_parsing_timeout raises error."""
        with pytest.raises(ConfigurationError):
            AppConfig(csv_parsing_timeout=-1)

    def test_invalid_ui_timeout_zero(self) -> None:
        """Test that ui_response_timeout = 0 raises error."""
        with pytest.raises(ConfigurationError):
            AppConfig(ui_response_timeout=0)

    def test_invalid_coverage_threshold_negative(self) -> None:
        """Test that negative coverage threshold raises error."""
        with pytest.raises(ConfigurationError):
            AppConfig(test_coverage_threshold=-1)

    def test_invalid_coverage_threshold_over_100(self) -> None:
        """Test that coverage threshold > 100 raises error."""
        with pytest.raises(ConfigurationError):
            AppConfig(test_coverage_threshold=101)


class TestAppConfigSessionSettings:
    """Unit tests for session-related configuration."""

    def test_default_session_settings(self) -> None:
        """Test default session settings."""
        config = AppConfig()
        
        assert config.default_session_length == 10
        assert config.max_session_length == 50
        assert config.min_session_length == 5

    def test_custom_session_settings(self) -> None:
        """Test custom session settings."""
        config = AppConfig(
            min_session_length=3,
            max_session_length=100,
            default_session_length=20
        )
        
        assert config.min_session_length == 3
        assert config.max_session_length == 100
        assert config.default_session_length == 20


class TestAppConfigFilePaths:
    """Unit tests for file path configuration."""

    def test_default_file_paths(self) -> None:
        """Test default file paths."""
        config = AppConfig()
        
        assert "question-bank.csv" in config.question_bank_path
        assert "app.log" in config.log_file

    def test_custom_file_paths(self) -> None:
        """Test custom file paths."""
        config = AppConfig(
            question_bank_path="/custom/path/questions.csv",
            log_file="/custom/logs/app.log"
        )
        
        assert config.question_bank_path == "/custom/path/questions.csv"
        assert config.log_file == "/custom/logs/app.log"


class TestAppConfigPerformance:
    """Unit tests for performance configuration."""

    def test_default_timeouts(self) -> None:
        """Test default timeout values."""
        config = AppConfig()
        
        assert config.csv_parsing_timeout == 5
        assert config.ui_response_timeout == 200

    def test_custom_timeouts(self) -> None:
        """Test custom timeout values."""
        config = AppConfig(
            csv_parsing_timeout=10,
            ui_response_timeout=500
        )
        
        assert config.csv_parsing_timeout == 10
        assert config.ui_response_timeout == 500
