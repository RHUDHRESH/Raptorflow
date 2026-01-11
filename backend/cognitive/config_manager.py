"""
Advanced Configuration Management
Environment-aware configuration with validation and hot reload
"""

import asyncio
import json
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)

T = TypeVar("T")


class Environment(str, Enum):
    """Environment types"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    """Database configuration"""

    host: str = "localhost"
    port: int = 5432
    database: str = "raptorflow"
    username: str = "postgres"
    password: str = ""
    ssl_mode: str = "prefer"
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600


@dataclass
class RedisConfig:
    """Redis configuration"""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    ssl: bool = False
    max_connections: int = 10
    retry_on_timeout: bool = True
    socket_timeout: int = 5
    socket_connect_timeout: int = 5


@dataclass
class LLMConfig:
    """LLM configuration"""

    provider: str = "openai"
    api_key: str = ""
    base_url: str = ""
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 1000
    timeout: int = 60
    max_retries: int = 3
    rate_limit_per_minute: int = 60


@dataclass
class CognitiveEngineConfig:
    """Cognitive engine configuration"""

    enable_auto_execution: bool = False
    quality_threshold: int = 70
    enable_human_approval: bool = True
    max_processing_time_minutes: int = 30
    max_concurrent_requests: int = 10
    max_queue_size: int = 100
    session_ttl_hours: int = 24

    # Rate limiting
    rate_limit_requests_per_minute: int = 60
    rate_limit_burst_size: int = 10

    # Resource limits
    max_memory_mb: int = 2048
    max_tokens_per_request: int = 10000
    max_cost_per_request: float = 10.0


@dataclass
class LoggingConfig:
    """Logging configuration"""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size_mb: int = 100
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = True


@dataclass
class MonitoringConfig:
    """Monitoring configuration"""

    enable_metrics: bool = True
    enable_health_checks: bool = True
    enable_alerts: bool = True
    metrics_port: int = 9090
    health_check_interval: int = 30
    alert_webhook_url: Optional[str] = None

    # Resource monitoring
    memory_threshold_mb: int = 1024
    cpu_threshold_percent: float = 80.0
    disk_threshold_percent: float = 85.0


@dataclass
class SecurityConfig:
    """Security configuration"""

    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    enable_cors: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    enable_rate_limiting: bool = True
    max_request_size_mb: int = 10


@dataclass
class AppConfig:
    """Main application configuration"""

    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    log_level: str = "INFO"

    # Component configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    cognitive_engine: CognitiveEngineConfig = field(
        default_factory=CognitiveEngineConfig
    )
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)

    # Custom configuration
    custom: Dict[str, Any] = field(default_factory=dict)


class ConfigValidationError(Exception):
    """Configuration validation error"""

    pass


class ConfigFileHandler(FileSystemEventHandler):
    """File system event handler for config file changes"""

    def __init__(self, config_manager: "ConfigManager"):
        self.config_manager = config_manager
        self.last_reload = datetime.now()

    def on_modified(self, event):
        """Handle file modification"""
        if event.is_directory:
            return

        # Debounce rapid file changes
        if (datetime.now() - self.last_reload).total_seconds() < 1:
            return

        file_path = Path(event.src_path)
        if file_path.name in ["config.yaml", "config.yml", "config.json"]:
            logger.info(f"Configuration file changed: {file_path}")
            asyncio.create_task(self.config_manager.reload_config())
            self.last_reload = datetime.now()


class ConfigManager:
    """Advanced configuration manager"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.yaml"
        self.environment_file = (
            self.config_dir / f"config.{os.getenv('ENVIRONMENT', 'development')}.yaml"
        )

        self._config: Optional[AppConfig] = None
        self._observers: List[callable] = []
        self._file_observer: Optional[Observer] = None
        self._watching = False

        # Configuration schema for validation
        self._schema = self._build_schema()

    def _build_schema(self) -> Dict[str, Any]:
        """Build configuration validation schema"""
        return {
            "environment": {"type": str, "choices": [e.value for e in Environment]},
            "debug": {"type": bool},
            "log_level": {
                "type": str,
                "choices": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            },
            "database": {
                "type": "dict",
                "required": ["host", "port", "database"],
                "schema": {
                    "host": {"type": str},
                    "port": {"type": int, "min": 1, "max": 65535},
                    "database": {"type": str},
                    "pool_size": {"type": int, "min": 1, "max": 100},
                },
            },
            "redis": {
                "type": "dict",
                "required": ["host", "port"],
                "schema": {
                    "host": {"type": str},
                    "port": {"type": int, "min": 1, "max": 65535},
                    "max_connections": {"type": int, "min": 1, "max": 100},
                },
            },
            "cognitive_engine": {
                "type": "dict",
                "schema": {
                    "quality_threshold": {"type": int, "min": 0, "max": 100},
                    "max_concurrent_requests": {"type": int, "min": 1, "max": 100},
                    "max_processing_time_minutes": {"type": int, "min": 1, "max": 180},
                },
            },
        }

    async def load_config(self) -> AppConfig:
        """Load configuration from files and environment"""
        # Start with default configuration
        config_dict = asdict(AppConfig())

        # Load base configuration file
        if self.config_file.exists():
            base_config = self._load_config_file(self.config_file)
            config_dict = self._merge_configs(config_dict, base_config)

        # Load environment-specific configuration
        if self.environment_file.exists():
            env_config = self._load_config_file(self.environment_file)
            config_dict = self._merge_configs(config_dict, env_config)

        # Override with environment variables
        config_dict = self._apply_env_overrides(config_dict)

        # Validate configuration
        self._validate_config(config_dict)

        # Create configuration object
        self._config = self._dict_to_config(config_dict)

        # Start file watching
        if not self._watching:
            await self._start_file_watching()

        logger.info(f"Configuration loaded for environment: {self._config.environment}")
        return self._config

    def _load_config_file(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(file_path, "r") as f:
                if file_path.suffix.lower() == ".json":
                    return json.load(f)
                else:
                    return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to load config file {file_path}: {e}")
            return {}

    def _merge_configs(
        self, base: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge two configuration dictionaries"""
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides"""
        env_mappings = {
            "RAPTORFLOW_ENVIRONMENT": ("environment", str),
            "RAPTORFLOW_DEBUG": ("debug", bool),
            "RAPTORFLOW_LOG_LEVEL": ("log_level", str),
            "DATABASE_HOST": ("database.host", str),
            "DATABASE_PORT": ("database.port", int),
            "DATABASE_NAME": ("database.database", str),
            "DATABASE_USER": ("database.username", str),
            "DATABASE_PASSWORD": ("database.password", str),
            "REDIS_HOST": ("redis.host", str),
            "REDIS_PORT": ("redis.port", int),
            "REDIS_PASSWORD": ("redis.password", str),
            "LLM_API_KEY": ("llm.api_key", str),
            "LLM_MODEL": ("llm.model", str),
            "COGNITIVE_MAX_CONCURRENT": (
                "cognitive_engine.max_concurrent_requests",
                int,
            ),
            "JWT_SECRET": ("security.jwt_secret", str),
        }

        for env_var, (config_path, value_type) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert value type
                if value_type == bool:
                    value = value.lower() in ("true", "1", "yes", "on")
                elif value_type == int:
                    value = int(value)
                elif value_type == float:
                    value = float(value)

                # Set nested value
                self._set_nested_value(config, config_path, value)

        return config

    def _set_nested_value(self, config: Dict[str, Any], path: str, value: Any):
        """Set nested configuration value"""
        keys = path.split(".")
        current = config

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    def _validate_config(self, config: Dict[str, Any]):
        """Validate configuration against schema"""
        errors = []

        def validate_schema(schema: Dict[str, Any], data: Any, path: str = ""):
            if isinstance(schema, dict):
                if "type" in schema:
                    # Validate field
                    field_type = schema["type"]
                    field_path = path.rstrip(".")

                    if field_type == str and not isinstance(data, str):
                        errors.append(
                            f"{field_path}: Expected string, got {type(data).__name__}"
                        )
                    elif field_type == int and not isinstance(data, int):
                        errors.append(
                            f"{field_path}: Expected integer, got {type(data).__name__}"
                        )
                    elif field_type == bool and not isinstance(data, bool):
                        errors.append(
                            f"{field_path}: Expected boolean, got {type(data).__name__}"
                        )
                    elif field_type == list and not isinstance(data, list):
                        errors.append(
                            f"{field_path}: Expected list, got {type(data).__name__}"
                        )

                    # Check choices
                    if "choices" in schema and data not in schema["choices"]:
                        errors.append(
                            f"{field_path}: Invalid value '{data}', choices: {schema['choices']}"
                        )

                    # Check ranges
                    if "min" in schema and data < schema["min"]:
                        errors.append(
                            f"{field_path}: Value {data} below minimum {schema['min']}"
                        )
                    if "max" in schema and data > schema["max"]:
                        errors.append(
                            f"{field_path}: Value {data} above maximum {schema['max']}"
                        )
                else:
                    # Validate nested dict
                    if not isinstance(data, dict):
                        errors.append(
                            f"{path}: Expected dict, got {type(data).__name__}"
                        )
                        return

                    for key, sub_schema in schema.items():
                        if key in data:
                            validate_schema(sub_schema, data[key], f"{key}.")
                        elif "required" in schema and key in schema["required"]:
                            errors.append(f"{path}{key}: Required field missing")

        validate_schema(self._schema, config)

        if errors:
            raise ConfigValidationError(
                f"Configuration validation failed:\n" + "\n".join(errors)
            )

    def _dict_to_config(self, config_dict: Dict[str, Any]) -> AppConfig:
        """Convert dictionary to configuration object"""
        # Convert nested dictionaries to config objects
        if "database" in config_dict:
            config_dict["database"] = DatabaseConfig(**config_dict["database"])

        if "redis" in config_dict:
            config_dict["redis"] = RedisConfig(**config_dict["redis"])

        if "llm" in config_dict:
            config_dict["llm"] = LLMConfig(**config_dict["llm"])

        if "cognitive_engine" in config_dict:
            config_dict["cognitive_engine"] = CognitiveEngineConfig(
                **config_dict["cognitive_engine"]
            )

        if "logging" in config_dict:
            config_dict["logging"] = LoggingConfig(**config_dict["logging"])

        if "monitoring" in config_dict:
            config_dict["monitoring"] = MonitoringConfig(**config_dict["monitoring"])

        if "security" in config_dict:
            config_dict["security"] = SecurityConfig(**config_dict["security"])

        # Convert environment
        if "environment" in config_dict:
            config_dict["environment"] = Environment(config_dict["environment"])

        return AppConfig(**config_dict)

    async def _start_file_watching(self):
        """Start watching configuration files for changes"""
        if not self.config_dir.exists():
            return

        try:
            self._file_observer = Observer()
            handler = ConfigFileHandler(self)
            self._file_observer.schedule(handler, str(self.config_dir), recursive=False)
            self._file_observer.start()
            self._watching = True
            logger.info("Configuration file watching enabled")
        except Exception as e:
            logger.warning(f"Failed to start config file watching: {e}")

    async def reload_config(self):
        """Reload configuration from files"""
        try:
            old_config = self._config
            new_config = await self.load_config()

            # Notify observers
            for observer in self._observers:
                try:
                    if asyncio.iscoroutinefunction(observer):
                        await observer(old_config, new_config)
                    else:
                        observer(old_config, new_config)
                except Exception as e:
                    logger.error(f"Config observer error: {e}")

            logger.info("Configuration reloaded successfully")

        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")

    def get_config(self) -> AppConfig:
        """Get current configuration"""
        if self._config is None:
            raise ConfigValidationError("Configuration not loaded")
        return self._config

    def add_observer(self, observer: callable):
        """Add configuration change observer"""
        self._observers.append(observer)

    def remove_observer(self, observer: callable):
        """Remove configuration change observer"""
        if observer in self._observers:
            self._observers.remove(observer)

    def get_value(self, path: str, default: Any = None) -> Any:
        """Get configuration value by path (e.g., 'database.host')"""
        config = self.get_config()
        keys = path.split(".")
        current = config

        try:
            for key in keys:
                current = getattr(current, key)
            return current
        except AttributeError:
            return default

    async def shutdown(self):
        """Shutdown configuration manager"""
        if self._file_observer:
            self._file_observer.stop()
            self._file_observer.join()
            self._watching = False


# Global configuration manager
config_manager = ConfigManager()
