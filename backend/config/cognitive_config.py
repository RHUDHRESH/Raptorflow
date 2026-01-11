"""
Configuration Management for Cognitive Engine

Centralized configuration management and settings.
Implements PROMPT 95 from STREAM_3_COGNITIVE_ENGINE.
"""

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigFormat(Enum):
    """Configuration file formats."""

    JSON = "json"
    YAML = "yaml"
    ENV = "env"


class ConfigEnvironment(Enum):
    """Configuration environments."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class CognitiveEngineConfig:
    """Cognitive engine configuration."""

    # Engine settings
    engine_name: str = "Raptorflow Cognitive Engine"
    version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    # Processing settings
    max_concurrent_requests: int = 10
    request_timeout_seconds: int = 300
    max_text_length: int = 10000
    max_tokens_per_request: int = 4000

    # Performance settings
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    cache_max_size_mb: int = 100
    enable_parallel_processing: bool = True
    max_parallel_tasks: int = 5

    # Retry settings
    enable_retry: bool = True
    max_retries: int = 3
    retry_backoff_multiplier: float = 2.0
    retry_max_delay_seconds: float = 60.0

    # Fallback settings
    enable_fallback: bool = True
    fallback_timeout_seconds: int = 30
    enable_escalation: bool = True

    # Monitoring settings
    enable_monitoring: bool = True
    enable_tracing: bool = True
    enable_metrics: bool = True
    metrics_retention_hours: int = 24

    # Security settings
    enable_authentication: bool = True
    enable_authorization: bool = True
    session_timeout_minutes: int = 60
    max_login_attempts: int = 5

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1
    enable_cors: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])

    # Database settings
    database_url: str = "sqlite:///cognitive_engine.db"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # LLM settings
    llm_provider: str = "openai"
    llm_model: str = "gpt-4"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000
    llm_timeout_seconds: int = 30

    # Cost settings
    cost_per_token: float = 0.00001
    max_cost_per_request: float = 0.10
    daily_cost_limit: float = 100.0

    # Quality settings
    min_confidence_threshold: float = 0.7
    max_reflection_iterations: int = 3
    enable_quality_checking: bool = True

    # Integration settings
    enable_webhooks: bool = True
    webhook_timeout_seconds: int = 10
    enable_notifications: bool = True

    # Feature flags
    enable_multimodal: bool = True
    enable_voice_processing: bool = False
    enable_real_time_processing: bool = True

    # Custom settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModuleConfig:
    """Module-specific configuration."""

    module_name: str
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    version: str = "1.0.0"


class ConfigManager:
    """
    Centralized configuration management for cognitive engine.

    Handles loading, validation, and management of configuration settings.
    """

    def __init__(self, config_dir: str = "config", environment: str = None):
        """
        Initialize configuration manager.

        Args:
            config_dir: Directory containing configuration files
            environment: Target environment (development, testing, staging, production)
        """
        self.config_dir = Path(config_dir)
        self.environment = environment or os.getenv("COGNITIVE_ENV", "development")

        # Configuration storage
        self.engine_config: CognitiveEngineConfig = CognitiveEngineConfig()
        self.module_configs: Dict[str, ModuleConfig] = {}

        # Configuration file paths
        self.config_files = {
            "engine": self.config_dir / f"cognitive_engine.{self.environment}.json",
            "modules": self.config_dir / f"modules.{self.environment}.json",
            "secrets": self.config_dir / "secrets.json",
        }

        # Load configuration
        self._load_configuration()

        # Validate configuration
        self._validate_configuration()

    def _load_configuration(self) -> None:
        """Load configuration from files and environment."""
        logger.info(f"Loading configuration for environment: {self.environment}")

        # Load engine configuration
        self._load_engine_config()

        # Load module configurations
        self._load_module_configs()

        # Load secrets
        self._load_secrets()

        # Override with environment variables
        self._load_environment_overrides()

        logger.info("Configuration loaded successfully")

    def _load_engine_config(self) -> None:
        """Load engine configuration from file."""
        config_file = self.config_files["engine"]

        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    config_data = json.load(f)

                # Update engine config with loaded data
                for key, value in config_data.items():
                    if hasattr(self.engine_config, key):
                        setattr(self.engine_config, key, value)
                    else:
                        self.engine_config.custom_settings[key] = value

                logger.info(f"Engine configuration loaded from {config_file}")

            except Exception as e:
                logger.error(f"Failed to load engine configuration: {e}")
                logger.info("Using default engine configuration")
        else:
            logger.info(f"Engine configuration file not found: {config_file}")
            logger.info("Using default engine configuration")

    def _load_module_configs(self) -> None:
        """Load module configurations from file."""
        config_file = self.config_files["modules"]

        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    modules_data = json.load(f)

                for module_name, module_data in modules_data.items():
                    module_config = ModuleConfig(
                        module_name=module_name,
                        enabled=module_data.get("enabled", True),
                        config=module_data.get("config", {}),
                        dependencies=module_data.get("dependencies", []),
                        version=module_data.get("version", "1.0.0"),
                    )
                    self.module_configs[module_name] = module_config

                logger.info(f"Module configurations loaded from {config_file}")

            except Exception as e:
                logger.error(f"Failed to load module configurations: {e}")
                logger.info("Using default module configurations")
        else:
            logger.info(f"Module configuration file not found: {config_file}")
            logger.info("Using default module configurations")

    def _load_secrets(self) -> None:
        """Load secrets from file."""
        secrets_file = self.config_files["secrets"]

        if secrets_file.exists():
            try:
                with open(secrets_file, "r") as f:
                    secrets_data = json.load(f)

                # Add secrets to custom settings
                self.engine_config.custom_settings["secrets"] = secrets_data

                logger.info(f"Secrets loaded from {secrets_file}")

            except Exception as e:
                logger.error(f"Failed to load secrets: {e}")
        else:
            logger.info(f"Secrets file not found: {secrets_file}")

    def _load_environment_overrides(self) -> None:
        """Load configuration overrides from environment variables."""
        env_mappings = {
            "COGNITIVE_ENGINE_NAME": ("engine_name", str),
            "COGNITIVE_VERSION": ("version", str),
            "COGNITIVE_ENVIRONMENT": ("environment", str),
            "COGNITIVE_DEBUG": ("debug", bool),
            "COGNITIVE_LOG_LEVEL": ("log_level", str),
            "COGNITIVE_MAX_CONCURRENT_REQUESTS": ("max_concurrent_requests", int),
            "COGNITIVE_REQUEST_TIMEOUT": ("request_timeout_seconds", int),
            "COGNITIVE_MAX_TEXT_LENGTH": ("max_text_length", int),
            "COGNITIVE_MAX_TOKENS": ("max_tokens_per_request", int),
            "COGNITIVE_ENABLE_CACHING": ("enable_caching", bool),
            "COGNITIVE_CACHE_TTL": ("cache_ttl_seconds", int),
            "COGNITIVE_CACHE_MAX_SIZE": ("cache_max_size_mb", int),
            "COGNITIVE_ENABLE_PARALLEL": ("enable_parallel_processing", bool),
            "COGNITIVE_MAX_PARALLEL_TASKS": ("max_parallel_tasks", int),
            "COGNITIVE_ENABLE_RETRY": ("enable_retry", bool),
            "COGNITIVE_MAX_RETRIES": ("max_retries", int),
            "COGNITIVE_ENABLE_FALLBACK": ("enable_fallback", bool),
            "COGNITIVE_ENABLE_MONITORING": ("enable_monitoring", bool),
            "COGNITIVE_ENABLE_TRACING": ("enable_tracing", bool),
            "COGNITIVE_API_HOST": ("api_host", str),
            "COGNITIVE_API_PORT": ("api_port", int),
            "COGNITIVE_DATABASE_URL": ("database_url", str),
            "COGNITIVE_LLM_PROVIDER": ("llm_provider", str),
            "COGNITIVE_LLM_MODEL": ("llm_model", str),
            "COGNITIVE_LLM_TEMPERATURE": ("llm_temperature", float),
            "COGNITIVE_COST_PER_TOKEN": ("cost_per_token", float),
            "COGNITIVE_MAX_COST_PER_REQUEST": ("max_cost_per_request", float),
            "COGNITIVE_DAILY_COST_LIMIT": ("daily_cost_limit", float),
        }

        for env_var, (config_key, value_type) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    if value_type == bool:
                        value = env_value.lower() in ("true", "1", "yes", "on")
                    elif value_type == int:
                        value = int(env_value)
                    elif value_type == float:
                        value = float(env_value)
                    else:
                        value = env_value

                    setattr(self.engine_config, config_key, value)
                    logger.info(f"Environment override: {config_key} = {value}")

                except ValueError as e:
                    logger.error(f"Invalid environment variable {env_var}: {e}")

    def _validate_configuration(self) -> None:
        """Validate configuration settings."""
        logger.info("Validating configuration...")

        validation_errors = []

        # Validate engine configuration
        if self.engine_config.max_concurrent_requests <= 0:
            validation_errors.append("max_concurrent_requests must be greater than 0")

        if self.engine_config.request_timeout_seconds <= 0:
            validation_errors.append("request_timeout_seconds must be greater than 0")

        if self.engine_config.max_text_length <= 0:
            validation_errors.append("max_text_length must be greater than 0")

        if self.engine_config.max_tokens_per_request <= 0:
            validation_errors.append("max_tokens_per_request must be greater than 0")

        if self.engine_config.cache_ttl_seconds <= 0:
            validation_errors.append("cache_ttl_seconds must be greater than 0")

        if self.engine_config.cache_max_size_mb <= 0:
            validation_errors.append("cache_max_size_mb must be greater than 0")

        if self.engine_config.max_retries < 0:
            validation_errors.append("max_retries must be non-negative")

        if self.engine_config.retry_backoff_multiplier <= 1.0:
            validation_errors.append(
                "retry_backoff_multiplier must be greater than 1.0"
            )

        if self.engine_config.api_port <= 0 or self.engine_config.api_port > 65535:
            validation_errors.append("api_port must be between 1 and 65535")

        if (
            self.engine_config.llm_temperature < 0.0
            or self.engine_config.llm_temperature > 2.0
        ):
            validation_errors.append("llm_temperature must be between 0.0 and 2.0")

        if self.engine_config.cost_per_token < 0.0:
            validation_errors.append("cost_per_token must be non-negative")

        if self.engine_config.max_cost_per_request < 0.0:
            validation_errors.append("max_cost_per_request must be non-negative")

        if self.engine_config.daily_cost_limit < 0.0:
            validation_errors.append("daily_cost_limit must be non-negative")

        if (
            self.engine_config.min_confidence_threshold < 0.0
            or self.engine_config.min_confidence_threshold > 1.0
        ):
            validation_errors.append(
                "min_confidence_threshold must be between 0.0 and 1.0"
            )

        if self.engine_config.max_reflection_iterations <= 0:
            validation_errors.append("max_reflection_iterations must be greater than 0")

        # Report validation results
        if validation_errors:
            logger.error("Configuration validation failed:")
            for error in validation_errors:
                logger.error(f"  - {error}")
            raise ValueError("Configuration validation failed")
        else:
            logger.info("Configuration validation passed")

    def get_engine_config(self) -> CognitiveEngineConfig:
        """Get engine configuration."""
        return self.engine_config

    def get_module_config(self, module_name: str) -> Optional[ModuleConfig]:
        """Get module configuration."""
        return self.module_configs.get(module_name)

    def get_all_module_configs(self) -> Dict[str, ModuleConfig]:
        """Get all module configurations."""
        return self.module_configs.copy()

    def update_engine_config(self, updates: Dict[str, Any]) -> None:
        """Update engine configuration."""
        for key, value in updates.items():
            if hasattr(self.engine_config, key):
                setattr(self.engine_config, key, value)
            else:
                self.engine_config.custom_settings[key] = value

        # Re-validate after update
        self._validate_configuration()

        logger.info(f"Engine configuration updated: {list(updates.keys())}")

    def update_module_config(self, module_name: str, updates: Dict[str, Any]) -> None:
        """Update module configuration."""
        if module_name not in self.module_configs:
            self.module_configs[module_name] = ModuleConfig(module_name=module_name)

        module_config = self.module_configs[module_name]

        for key, value in updates.items():
            if key == "enabled":
                module_config.enabled = value
            elif key == "config":
                module_config.config.update(value)
            elif key == "dependencies":
                module_config.dependencies = value
            elif key == "version":
                module_config.version = value
            else:
                module_config.config[key] = value

        logger.info(f"Module configuration updated: {module_name}")

    def enable_module(self, module_name: str) -> None:
        """Enable a module."""
        self.update_module_config(module_name, {"enabled": True})

    def disable_module(self, module_name: str) -> None:
        """Disable a module."""
        self.update_module_config(module_name, {"enabled": False})

    def is_module_enabled(self, module_name: str) -> bool:
        """Check if a module is enabled."""
        module_config = self.get_module_config(module_name)
        return module_config.enabled if module_config else False

    def save_configuration(self, format: str = "json") -> None:
        """Save current configuration to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save engine configuration
        engine_config_file = (
            self.config_dir
            / f"cognitive_engine.{self.environment}.{timestamp}.{format}"
        )

        engine_data = {
            key: getattr(self.engine_config, key)
            for key in dir(self.engine_config)
            if not key.startswith("_")
            and not callable(getattr(self.engine_config, key))
        }

        with open(engine_config_file, "w") as f:
            if format == "json":
                json.dump(engine_data, f, indent=2, default=str)
            elif format == "yaml":
                yaml.dump(engine_data, f, default_flow_style=False)

        # Save module configurations
        module_config_file = (
            self.config_dir / f"modules.{self.environment}.{timestamp}.{format}"
        )

        modules_data = {
            module_name: {
                "enabled": module_config.enabled,
                "config": module_config.config,
                "dependencies": module_config.dependencies,
                "version": module_config.version,
            }
            for module_name, module_config in self.module_configs.items()
        }

        with open(module_config_file, "w") as f:
            if format == "json":
                json.dump(modules_data, f, indent=2, default=str)
            elif format == "yaml":
                yaml.dump(modules_data, f, default_flow_style=False)

        logger.info(
            f"Configuration saved to {engine_config_file} and {module_config_file}"
        )

    def reload_configuration(self) -> None:
        """Reload configuration from files."""
        logger.info("Reloading configuration...")

        # Clear current configuration
        self.engine_config = CognitiveEngineConfig()
        self.module_configs.clear()

        # Reload configuration
        self._load_configuration()

        logger.info("Configuration reloaded successfully")

    def get_environment_info(self) -> Dict[str, Any]:
        """Get environment information."""
        return {
            "environment": self.environment,
            "config_dir": str(self.config_dir),
            "config_files": {
                name: str(path) for name, path in self.config_files.items()
            },
            "engine_name": self.engine_config.engine_name,
            "version": self.engine_config.version,
            "debug": self.engine_config.debug,
            "enabled_modules": [
                name for name, config in self.module_configs.items() if config.enabled
            ],
        }

    def export_configuration(self, format: str = "json") -> str:
        """Export complete configuration."""
        export_data = {
            "environment": self.environment,
            "timestamp": datetime.now().isoformat(),
            "engine_config": {
                key: getattr(self.engine_config, key)
                for key in dir(self.engine_config)
                if not key.startswith("_")
                and not callable(getattr(self.engine_config, key))
            },
            "module_configs": {
                module_name: {
                    "enabled": module_config.enabled,
                    "config": module_config.config,
                    "dependencies": module_config.dependencies,
                    "version": module_config.version,
                }
                for module_name, module_config in self.module_configs.items()
            },
        }

        if format == "json":
            return json.dumps(export_data, indent=2, default=str)
        elif format == "yaml":
            return yaml.dump(export_data, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def import_configuration(self, config_data: str, format: str = "json") -> None:
        """Import configuration from data."""
        if format == "json":
            data = json.loads(config_data)
        elif format == "yaml":
            data = yaml.safe_load(config_data)
        else:
            raise ValueError(f"Unsupported format: {format}")

        # Import engine configuration
        if "engine_config" in data:
            self.update_engine_config(data["engine_config"])

        # Import module configurations
        if "module_configs" in data:
            for module_name, module_data in data["module_configs"].items():
                self.update_module_config(module_name, module_data)

        logger.info("Configuration imported successfully")

    def create_default_configs(self) -> None:
        """Create default configuration files."""
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)

        # Create default engine configuration
        default_engine_config = {
            "engine_name": "Raptorflow Cognitive Engine",
            "version": "1.0.0",
            "environment": self.environment,
            "debug": False,
            "log_level": "INFO",
            "max_concurrent_requests": 10,
            "request_timeout_seconds": 300,
            "max_text_length": 10000,
            "max_tokens_per_request": 4000,
            "enable_caching": True,
            "cache_ttl_seconds": 3600,
            "cache_max_size_mb": 100,
            "enable_parallel_processing": True,
            "max_parallel_tasks": 5,
            "enable_retry": True,
            "max_retries": 3,
            "retry_backoff_multiplier": 2.0,
            "retry_max_delay_seconds": 60.0,
            "enable_fallback": True,
            "fallback_timeout_seconds": 30,
            "enable_escalation": True,
            "enable_monitoring": True,
            "enable_tracing": True,
            "enable_metrics": True,
            "metrics_retention_hours": 24,
            "enable_authentication": True,
            "enable_authorization": True,
            "session_timeout_minutes": 60,
            "max_login_attempts": 5,
            "api_host": "0.0.0.0",
            "api_port": 8000,
            "api_workers": 1,
            "enable_cors": True,
            "cors_origins": ["*"],
            "database_url": "sqlite:///cognitive_engine.db",
            "database_pool_size": 10,
            "database_max_overflow": 20,
            "llm_provider": "openai",
            "llm_model": "gpt-4",
            "llm_temperature": 0.7,
            "llm_max_tokens": 2000,
            "llm_timeout_seconds": 30,
            "cost_per_token": 0.00001,
            "max_cost_per_request": 0.10,
            "daily_cost_limit": 100.0,
            "min_confidence_threshold": 0.7,
            "max_reflection_iterations": 3,
            "enable_quality_checking": True,
            "enable_webhooks": True,
            "webhook_timeout_seconds": 10,
            "enable_notifications": True,
            "enable_multimodal": True,
            "enable_voice_processing": False,
            "enable_real_time_processing": True,
        }

        engine_config_file = self.config_files["engine"]
        with open(engine_config_file, "w") as f:
            json.dump(default_engine_config, f, indent=2)

        # Create default module configuration
        default_module_config = {
            "perception": {
                "enabled": True,
                "config": {
                    "enable_entity_extraction": True,
                    "enable_intent_detection": True,
                    "enable_sentiment_analysis": True,
                    "enable_urgency_classification": True,
                },
                "dependencies": [],
                "version": "1.0.0",
            },
            "planning": {
                "enabled": True,
                "config": {
                    "enable_task_decomposition": True,
                    "enable_step_planning": True,
                    "enable_cost_estimation": True,
                    "enable_risk_assessment": True,
                },
                "dependencies": ["perception"],
                "version": "1.0.0",
            },
            "reflection": {
                "enabled": True,
                "config": {
                    "enable_fact_checking": True,
                    "enable_plagiarism_detection": True,
                    "enable_learning": True,
                    "max_iterations": 3,
                },
                "dependencies": ["perception"],
                "version": "1.0.0",
            },
            "critic": {
                "enabled": True,
                "config": {
                    "enable_failure_mode_analysis": True,
                    "enable_edge_case_testing": True,
                    "enable_competitor_lens": True,
                    "enable_customer_lens": True,
                },
                "dependencies": ["perception"],
                "version": "1.0.0",
            },
        }

        module_config_file = self.config_files["modules"]
        with open(module_config_file, "w") as f:
            json.dump(default_module_config, f, indent=2)

        # Create empty secrets file
        secrets_file = self.config_files["secrets"]
        with open(secrets_file, "w") as f:
            json.dump({}, f, indent=2)

        logger.info(f"Default configuration files created in {self.config_dir}")


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager(
    config_dir: str = "config", environment: str = None
) -> ConfigManager:
    """Get global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_dir, environment)
    return _config_manager


def get_engine_config() -> CognitiveEngineConfig:
    """Get engine configuration."""
    return get_config_manager().get_engine_config()


def get_module_config(module_name: str) -> Optional[ModuleConfig]:
    """Get module configuration."""
    return get_config_manager().get_module_config(module_name)


def is_module_enabled(module_name: str) -> bool:
    """Check if a module is enabled."""
    return get_config_manager().is_module_enabled(module_name)


# Configuration utilities
def create_default_configs(
    config_dir: str = "config", environment: str = "development"
) -> None:
    """Create default configuration files."""
    config_manager = ConfigManager(config_dir, environment)
    config_manager.create_default_configs()


def reload_configuration() -> None:
    """Reload configuration."""
    get_config_manager().reload_configuration()


def save_configuration(format: str = "json") -> None:
    """Save current configuration."""
    get_config_manager().save_configuration(format)


def export_configuration(format: str = "json") -> str:
    """Export configuration."""
    return get_config_manager().export_configuration(format)


def import_configuration(config_data: str, format: str = "json") -> None:
    """Import configuration."""
    get_config_manager().import_configuration(config_data, format)


def get_environment_info() -> Dict[str, Any]:
    """Get environment information."""
    return get_config_manager().get_environment_info()
