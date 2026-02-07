import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pytest

logger = logging.getLogger("raptorflow.testing.config")


@dataclass
class TestConfiguration:
    """Test configuration for all test types."""

    # General settings
    test_environment: str = "testing"
    base_url: str = "http://localhost:8000"
    database_url: str = "sqlite:///test.db"
    redis_url: str = "redis://localhost:6379/1"

    # Test execution settings
    timeout: int = 30
    max_retries: int = 3
    parallel_tests: bool = True
    cleanup_after_test: bool = True
    generate_reports: bool = True

    # Unit test settings
    unit_test_timeout: int = 10
    unit_test_retries: int = 1

    # Integration test settings
    integration_test_timeout: int = 30
    integration_test_retries: int = 2

    # Load test settings
    load_test_concurrent_users: int = 100
    load_test_ramp_up_time: int = 60
    load_test_duration: int = 300
    load_test_requests_per_second: int = 50
    load_test_endpoints: List[str] = None

    # Security test settings
    security_test_sql_injection: bool = True
    security_test_xss: bool = True
    security_test_auth_bypass: bool = True
    security_test_rate_limiting: bool = True
    security_test_input_validation: bool = True
    security_test_authorization: bool = True

    # Report settings
    report_format: str = "json"  # json, html, xml
    report_include_details: bool = True
    report_include_recommendations: bool = True

    def __post_init__(self):
        if self.load_test_endpoints is None:
            self.load_test_endpoints = [
                "/health",
                "/metrics",
                "/api/v1/campaigns",
                "/api/v1/moves",
                "/api/v1/users",
            ]


class TestConfigManager:
    """Test configuration manager."""

    def __init__(self):
        self.config = TestConfiguration()
        self.config_file = "test_config.json"

    def load_config(self, config_file: str = None) -> TestConfiguration:
        """Load configuration from file."""
        file_path = config_file or self.config_file

        try:
            with open(file_path, "r") as f:
                config_data = json.load(f)

            # Update configuration with loaded data
            for key, value in config_data.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)

            logger.info(f"Configuration loaded from {file_path}")
            return self.config

        except FileNotFoundError:
            logger.warning(f"Config file {file_path} not found, using defaults")
            return self.config
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file {file_path}: {e}")
            return self.config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self.config

    def save_config(self, config_file: str = None):
        """Save configuration to file."""
        file_path = config_file or self.config_file

        try:
            config_data = {
                "test_environment": self.config.test_environment,
                "base_url": self.config.base_url,
                "database_url": self.config.database_url,
                "redis_url": self.config.redis_url,
                "timeout": self.config.timeout,
                "max_retries": self.config.max_retries,
                "parallel_tests": self.config.parallel_tests,
                "cleanup_after_test": self.config.cleanup_after_test,
                "generate_reports": self.config.generate_reports,
                "unit_test_timeout": self.config.unit_test_timeout,
                "unit_test_retries": self.config.unit_test_retries,
                "integration_test_timeout": self.config.integration_test_timeout,
                "integration_test_retries": self.config.integration_test_retries,
                "load_test_concurrent_users": self.config.load_test_concurrent_users,
                "load_test_ramp_up_time": self.config.load_test_ramp_up_time,
                "load_test_duration": self.config.load_test_duration,
                "load_test_requests_per_second": self.config.load_test_requests_per_second,
                "load_test_endpoints": self.config.load_test_endpoints,
                "security_test_sql_injection": self.config.security_test_sql_injection,
                "security_test_xss": self.config.security_test_xss,
                "security_test_auth_bypass": self.config.security_test_auth_bypass,
                "security_test_rate_limiting": self.config.security_test_rate_limiting,
                "security_test_input_validation": self.config.security_test_input_validation,
                "security_test_authorization": self.config.security_test_authorization,
                "report_format": self.config.report_format,
                "report_include_details": self.config.report_include_details,
                "report_include_recommendations": self.config.report_include_recommendations,
            }

            with open(file_path, "w") as f:
                json.dump(config_data, f, indent=2)

            logger.info(f"Configuration saved to {file_path}")

        except Exception as e:
            logger.error(f"Error saving config: {e}")


# Global config manager
_config_manager = None


def get_config_manager() -> TestConfigManager:
    """Get the global config manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = TestConfigManager()
    return _config_manager


def get_test_config() -> TestConfiguration:
    """Get test configuration."""
    manager = get_config_manager()
    return manager.get_config()


if __name__ == "__main__":
    # Create default configuration file
    manager = get_config_manager()
    manager.save_config()
    print("Default test configuration created: test_config.json")
