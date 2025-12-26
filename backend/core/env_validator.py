import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger("raptorflow.config")


class EnvType(Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    URL = "url"
    EMAIL = "email"


@dataclass
class EnvVar:
    name: str
    env_type: EnvType
    required: bool = True
    default: Any = None
    description: str = ""
    choices: Optional[List[Any]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None


class EnvironmentValidator:
    """
    Production-grade environment variable validation with detailed error reporting.
    """

    def __init__(self):
        self.variables: Dict[str, EnvVar] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def add_variable(self, env_var: EnvVar):
        """Add an environment variable definition for validation."""
        self.variables[env_var.name] = env_var

    def validate_all(self) -> bool:
        """Validate all defined environment variables."""
        self.errors.clear()
        self.warnings.clear()

        logger.info("Starting environment variable validation")

        for name, env_var in self.variables.items():
            self._validate_variable(name, env_var)

        # Log results
        if self.errors:
            logger.error(
                f"Environment validation failed with {len(self.errors)} errors"
            )
            for error in self.errors:
                logger.error(f"  - {error}")

        if self.warnings:
            logger.warning(
                f"Environment validation completed with {len(self.warnings)} warnings"
            )
            for warning in self.warnings:
                logger.warning(f"  - {warning}")

        if not self.errors:
            logger.info("Environment validation completed successfully")

        return len(self.errors) == 0

    def _validate_variable(self, name: str, env_var: EnvVar):
        """Validate a single environment variable."""
        raw_value = os.getenv(name)

        # Check if required variable is missing
        if env_var.required and raw_value is None:
            if env_var.default is not None:
                self.warnings.append(
                    f"Required variable {name} not set, using default: {env_var.default}"
                )
                os.environ[name] = str(env_var.default)
                raw_value = str(env_var.default)
            else:
                self.errors.append(f"Required variable {name} is not set")
                return

        # Use default if value is None
        if raw_value is None and env_var.default is not None:
            os.environ[name] = str(env_var.default)
            raw_value = str(env_var.default)

        # Skip validation if value is None and not required
        if raw_value is None:
            return

        # Type-specific validation
        try:
            validated_value = self._validate_type(raw_value, env_var)

            # Additional validations
            self._validate_choices(validated_value, env_var, name)
            self._validate_range(validated_value, env_var, name)
            self._validate_pattern(validated_value, env_var, name)

            # Update environment with validated value
            os.environ[name] = str(validated_value)

        except ValueError as e:
            self.errors.append(f"Variable {name}: {str(e)}")

    def _validate_type(self, value: str, env_var: EnvVar) -> Any:
        """Validate and convert the value to the correct type."""
        if env_var.env_type == EnvType.STRING:
            return str(value)

        elif env_var.env_type == EnvType.INTEGER:
            try:
                return int(value)
            except ValueError:
                raise ValueError(f"Expected integer, got '{value}'")

        elif env_var.env_type == EnvType.FLOAT:
            try:
                return float(value)
            except ValueError:
                raise ValueError(f"Expected float, got '{value}'")

        elif env_var.env_type == EnvType.BOOLEAN:
            normalized = value.lower().strip()
            if normalized in ("true", "1", "yes", "on"):
                return True
            elif normalized in ("false", "0", "no", "off"):
                return False
            else:
                raise ValueError(f"Expected boolean, got '{value}'")

        elif env_var.env_type == EnvType.LIST:
            # Split by comma and strip whitespace
            items = [item.strip() for item in value.split(",") if item.strip()]
            return items

        elif env_var.env_type == EnvType.URL:
            import re

            url_pattern = re.compile(
                r"^https?://"  # http:// or https://
                r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
                r"localhost|"  # localhost...
                r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
                r"(?::\d+)?"  # optional port
                r"(?:/?|[/?]\S+)$",
                re.IGNORECASE,
            )
            if not url_pattern.match(value):
                raise ValueError(f"Expected valid URL, got '{value}'")
            return value

        elif env_var.env_type == EnvType.EMAIL:
            import re

            email_pattern = re.compile(
                r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            )
            if not email_pattern.match(value):
                raise ValueError(f"Expected valid email, got '{value}'")
            return value

        else:
            return value

    def _validate_choices(self, value: Any, env_var: EnvVar, name: str):
        """Validate that the value is in the allowed choices."""
        if env_var.choices and value not in env_var.choices:
            raise ValueError(
                f"Value '{value}' not in allowed choices: {env_var.choices}"
            )

    def _validate_range(self, value: Any, env_var: EnvVar, name: str):
        """Validate numeric range constraints."""
        if isinstance(value, (int, float)):
            if env_var.min_value is not None and value < env_var.min_value:
                raise ValueError(f"Value {value} is below minimum {env_var.min_value}")
            if env_var.max_value is not None and value > env_var.max_value:
                raise ValueError(f"Value {value} is above maximum {env_var.max_value}")

    def _validate_pattern(self, value: Any, env_var: EnvVar, name: str):
        """Validate regex pattern for string values."""
        if env_var.pattern and isinstance(value, str):
            import re

            if not re.match(env_var.pattern, value):
                raise ValueError(
                    f"Value '{value}' does not match required pattern: {env_var.pattern}"
                )

    def get_validation_report(self) -> Dict[str, Any]:
        """Get a detailed validation report."""
        return {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "total_variables": len(self.variables),
            "missing_required": len([e for e in self.errors if "is not set" in e]),
        }


def setup_raptorflow_environment() -> EnvironmentValidator:
    """Setup and validate all RaptorFlow environment variables."""
    validator = EnvironmentValidator()

    # Database Configuration
    validator.add_variable(
        EnvVar(
            name="DATABASE_URL",
            env_type=EnvType.URL,
            required=True,
            description="PostgreSQL database connection URL",
        )
    )

    validator.add_variable(
        EnvVar(
            name="DATABASE_POOL_SIZE",
            env_type=EnvType.INTEGER,
            required=False,
            default=10,
            min_value=1,
            max_value=100,
            description="Database connection pool size",
        )
    )

    # Redis/Cache Configuration
    validator.add_variable(
        EnvVar(
            name="REDIS_URL",
            env_type=EnvType.URL,
            required=True,
            description="Redis connection URL for caching",
        )
    )

    # Authentication Configuration
    validator.add_variable(
        EnvVar(
            name="SUPABASE_URL",
            env_type=EnvType.URL,
            required=True,
            description="Supabase project URL",
        )
    )

    validator.add_variable(
        EnvVar(
            name="SUPABASE_ANON_KEY",
            env_type=EnvType.STRING,
            required=True,
            description="Supabase anonymous key",
        )
    )

    validator.add_variable(
        EnvVar(
            name="AUTH_JWT_SECRET",
            env_type=EnvType.STRING,
            required=True,
            min_value=32,
            description="JWT secret for authentication",
        )
    )

    # External Services
    validator.add_variable(
        EnvVar(
            name="SENDGRID_API_KEY",
            env_type=EnvType.STRING,
            required=True,
            description="SendGrid API key for email sending",
        )
    )

    validator.add_variable(
        EnvVar(
            name="OPENAI_API_KEY",
            env_type=EnvType.STRING,
            required=True,
            description="OpenAI API key for AI services",
        )
    )

    # Application Configuration
    validator.add_variable(
        EnvVar(
            name="ENVIRONMENT",
            env_type=EnvType.STRING,
            required=False,
            default="development",
            choices=["development", "staging", "production"],
            description="Application environment",
        )
    )

    validator.add_variable(
        EnvVar(
            name="LOG_LEVEL",
            env_type=EnvType.STRING,
            required=False,
            default="INFO",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            description="Logging level",
        )
    )

    validator.add_variable(
        EnvVar(
            name="PORT",
            env_type=EnvType.INTEGER,
            required=False,
            default=8000,
            min_value=1,
            max_value=65535,
            description="Application port",
        )
    )

    # Rate Limiting
    validator.add_variable(
        EnvVar(
            name="RATE_LIMIT_REQUESTS",
            env_type=EnvType.INTEGER,
            required=False,
            default=60,
            min_value=1,
            description="Rate limit requests per window",
        )
    )

    validator.add_variable(
        EnvVar(
            name="RATE_LIMIT_WINDOW",
            env_type=EnvType.INTEGER,
            required=False,
            default=60,
            min_value=1,
            description="Rate limit window in seconds",
        )
    )

    # GCP Configuration
    validator.add_variable(
        EnvVar(
            name="GCP_PROJECT_ID",
            env_type=EnvType.STRING,
            required=False,
            description="Google Cloud Project ID",
        )
    )

    validator.add_variable(
        EnvVar(
            name="GCP_BUCKET_NAME",
            env_type=EnvType.STRING,
            required=False,
            description="Google Cloud Storage bucket name",
        )
    )

    # Internal Configuration
    validator.add_variable(
        EnvVar(
            name="RF_INTERNAL_KEY",
            env_type=EnvType.STRING,
            required=True,
            min_value=32,
            description="Internal service key for health checks",
        )
    )

    return validator


def validate_environment() -> bool:
    """Validate the environment and return True if successful."""
    validator = setup_raptorflow_environment()
    return validator.validate_all()
