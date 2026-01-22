"""
Raptorflow Backend - AI Agent System
=====================================

A comprehensive AI agent system built with FastAPI, LangChain, and LangGraph.
Designed for intelligent workflow automation and multi-agent coordination.

Core Features:
- Multi-agent orchestration with LangGraph
- Specialist agents for different domains
- Advanced tool integration
- Performance monitoring and health checks
- Real-time workflow execution
- Comprehensive API endpoints

Architecture:
- FastAPI web framework
- LangChain for LLM integration
- LangGraph for workflow orchestration
- Redis for caching and session management
- PostgreSQL for persistent storage
- Comprehensive monitoring and logging

Author: Raptorflow Team
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Raptorflow Team"
__email__ = "team@raptorflow.ai"
__description__ = "AI Agent System for Workflow Automation"
__url__ = "https://raptorflow.ai"
__license__ = "MIT"

# NOTE: AgentDispatcher and AgentRegistry are NOT imported at module level
# to prevent blocking during heavy SDK initialization (VertexAI, LangChain).
# Import them directly where needed: from backend.agents.dispatcher import AgentDispatcher

# Core imports (lightweight)
from .config import get_settings

settings = get_settings()

# Public API
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "__url__",
    "__license__",
    # Core components
    "settings",
    "AgentRegistry",
    "AgentDispatcher",
    "WorkflowManager",
    "MetricsCollector",
    "HealthChecker",
    "AlertManager",
    # Configuration
    "get_settings",
    "setup_logging",
    "initialize_system",
]


# System initialization
def get_settings():
    """Get application settings."""
    return settings


def setup_logging():
    """Setup application logging."""
    import logging
    import sys

    import structlog

    # Configure structured logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )


def initialize_system():
    """Initialize the Raptorflow system."""
    setup_logging()

    # Initialize core components
    from .agents import AgentRegistry
    from .monitoring import AlertManager, HealthChecker, MetricsCollector
    from .workflows import WorkflowManager

    # Create singleton instances
    agent_registry = AgentRegistry()
    workflow_manager = WorkflowManager()
    metrics_collector = MetricsCollector()
    health_checker = HealthChecker()
    alert_manager = AlertManager()

    return {
        "agent_registry": agent_registry,
        "workflow_manager": workflow_manager,
        "metrics_collector": metrics_collector,
        "health_checker": health_checker,
        "alert_manager": alert_manager,
    }


# Package metadata
PACKAGE_INFO = {
    "name": "raptorflow-backend",
    "version": __version__,
    "description": __description__,
    "author": __author__,
    "license": __license__,
    "url": __url__,
    "python_requires": ">=3.11",
    "install_requires": [
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "langchain>=0.1.0",
        "langgraph>=0.0.20",
        "redis>=5.0.0",
        "sqlalchemy>=2.0.0",
        "structlog>=23.2.0",
        "prometheus-client>=0.19.0",
    ],
    "extras_require": {
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.11.0",
            "isort>=5.12.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.4.0",
            "mkdocstrings[python]>=0.24.0",
        ],
        "monitoring": [
            "prometheus-client>=0.19.0",
            "sentry-sdk>=1.38.0",
            "newrelic>=9.2.0",
        ],
        "cloud": [
            "google-cloud-storage>=2.10.0",
            "boto3>=1.34.0",
            "azure-storage-blob>=12.19.0",
        ],
    },
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: FastAPI",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    "keywords": [
        "ai",
        "agents",
        "workflow",
        "automation",
        "langchain",
        "langgraph",
        "fastapi",
        "machine learning",
    ],
    "project_urls": {
        "Documentation": f"{__url__}/docs",
        "Source": f"{__url__}/source",
        "Tracker": f"{__url__}/issues",
        "Changelog": f"{__url__}/changelog",
    },
}


# Environment information
def get_environment_info():
    """Get environment information for debugging."""
    import os
    import platform
    import sys

    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "debug": os.getenv("DEBUG", "false").lower() == "true",
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "database_url": os.getenv("DATABASE_URL", "Not configured"),
        "redis_url": os.getenv("REDIS_URL", "Not configured"),
        "api_host": os.getenv("API_HOST", "localhost"),
        "api_port": os.getenv("API_PORT", "8000"),
    }


# Health check for package
def health_check():
    """Perform basic health check of the package."""
    try:
        import os
        import sys

        # Check Python version
        if sys.version_info < (3, 11):
            return False, "Python 3.11+ required"

        # Check required environment variables
        required_vars = ["DATABASE_URL", "REDIS_URL"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            return False, f"Missing environment variables: {missing_vars}"

        # Check core modules
        try:
            import fastapi
            import langchain
            import langgraph
            import redis
            import sqlalchemy
        except ImportError as e:
            return False, f"Missing required module: {e}"

        return True, "All checks passed"

    except Exception as e:
        return False, f"Health check failed: {e}"


# Package initialization
try:
    import logging
    import os

    if os.getenv("RAPTORFLOW_SKIP_INIT", "false").lower() == "true":
        logger = logging.getLogger(__name__)
        logger.info(
            "Skipping Raptorflow system initialization (RAPTORFLOW_SKIP_INIT=true)"
        )
        system_components = None
    else:
        # Initialize system on import
        system_components = initialize_system()

        # Log successful initialization
        import structlog

        logger = structlog.get_logger(__name__)
        logger.info("Raptorflow backend initialized successfully", version=__version__)

except Exception as e:
    # Log initialization error
    import logging

    logger = logging.getLogger(__name__)
    logger.critical(f"Failed to initialize Raptorflow backend: {e}")

# Export system components for external use
system_components = system_components if "system_components" in locals() else None
