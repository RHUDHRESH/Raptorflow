import logging
import logging.config
import os
from typing import Dict, Any

# Production-grade logging configuration
LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
        "simple": {
            "format": "%(levelname)s - %(name)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "detailed",
            "stream": "ext://sys.stdout",
        },
        "console_json": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "logs/raptorflow.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8",
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "filename": "logs/raptorflow_errors.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8",
        },
    },
    "loggers": {
        "raptorflow": {
            "level": "DEBUG",
            "handlers": ["console", "file", "error_file"],
            "propagate": False,
        },
        "raptorflow.api": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "raptorflow.db": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "raptorflow.auth": {
            "level": "WARNING",
            "handlers": ["console", "file", "error_file"],
            "propagate": False,
        },
        "raptorflow.services.rate_limiter": {
            "level": "WARNING",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "fastapi": {
            "level": "WARNING",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "psycopg": {
            "level": "WARNING",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "httpx": {
            "level": "WARNING",
            "handlers": ["console", "file"],
            "propagate": False,
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}


def setup_logging():
    """Initialize logging configuration."""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Use JSON format in production
    if os.getenv("ENVIRONMENT") == "production":
        LOGGING_CONFIG["handlers"]["console"]["formatter"] = "json"
    
    # Apply configuration
    logging.config.dictConfig(LOGGING_CONFIG)


def get_logger(name: str) -> logging.Logger:
    """Get a properly configured logger."""
    return logging.getLogger(f"raptorflow.{name}")


# Security logger for sensitive operations
def get_security_logger() -> logging.Logger:
    """Get logger for security-related events."""
    logger = logging.getLogger("raptorflow.security")
    return logger


# Performance logger for metrics
def get_performance_logger() -> logging.Logger:
    """Get logger for performance metrics."""
    logger = logging.getLogger("raptorflow.performance")
    return logger
