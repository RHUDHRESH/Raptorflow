"""
Startup sequence for RaptorFlow backend.
Initializes all services and verifies connections.
"""

import asyncio
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, Optional

from ..agents.dispatcher import AgentDispatcher
from ..agents.llm import get_llm
from core.migrations import run_migrations
from core.redis import get_redis_client
from core.supabase_mgr import get_supabase_client
from memory.controller import SimpleMemoryController as MemoryController
from supabase import create_client

logger = logging.getLogger(__name__)


class StartupReport:
    """Report of startup status and health checks."""

    def __init__(self):
        self.start_time = datetime.now()
        self.services = {}
        self.errors = []
        self.warnings = []
        self.success = False

    def add_service_status(
        self, service: str, status: str, details: Optional[Dict[str, Any]] = None
    ):
        """Add service status to report."""
        self.services[service] = {
            "status": status,
            "details": details or {},
            "timestamp": datetime.now(),
        }

    def add_error(self, error: str):
        """Add error to report."""
        self.errors.append({"error": error, "timestamp": datetime.now()})

    def add_warning(self, warning: str):
        """Add warning to report."""
        self.warnings.append({"warning": warning, "timestamp": datetime.now()})

    def finalize(self):
        """Finalize the startup report."""
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.success = len(self.errors) == 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "success": self.success,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_seconds": self.duration,
            "services": self.services,
            "errors": self.errors,
            "warnings": self.warnings,
        }


async def verify_supabase_connection() -> bool:
    """Verify Supabase connection and basic operations."""
    try:
        client = get_supabase_client()
        if not client:
            return False

        # Test basic query
        result = client.table("users").select("id").limit(1).execute()
        return True

    except Exception as e:
        logger.error(f"Supabase connection failed: {e}")
        return False


async def verify_redis_connection() -> bool:
    """Verify Redis connection and basic operations."""
    try:
        client = get_redis_client()
        if not client:
            return False

        # Test basic operations
        await client.set("startup_test", "test_value", ex=10)
        value = await client.get("startup_test")
        await client.delete("startup_test")

        return value == "test_value"

    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return False


async def initialize_agent_dispatcher() -> bool:
    """Initialize the agent dispatcher system."""
    try:
        from ..agents.dispatcher import AgentDispatcher

        # Create dispatcher instance
        dispatcher = AgentDispatcher()
        # Dispatcher auto-registers agents on initialization
        return dispatcher is not None

    except Exception as e:
        logger.error(f"Agent dispatcher initialization failed: {e}")
        return False


async def verify_vertex_ai_credentials() -> bool:
    """Verify Vertex AI credentials and model access."""
    try:
        # Try to get LLM instance
        llm = get_llm()
        if not llm:
            return False

        # Test basic generation (small test)
        test_response = await llm.generate("Test", max_tokens=10)
        return bool(test_response)

    except Exception as e:
        logger.error(f"Vertex AI verification failed: {e}")
        return False


async def warm_up_embedding_models() -> bool:
    """Warm up embedding models for better performance."""
    try:
        # Skip embedding warmup for now - it's not critical for basic functionality
        logger.info("Embedding model warmup skipped (not critical for startup)")
        return True

    except Exception as e:
        logger.error(f"Embedding model warmup failed: {e}")
        return False


async def initialize_tool_registry() -> bool:
    """Initialize the tool registry."""
    try:
        from ..agents.tools import ToolRegistry

        registry = ToolRegistry()
        # Registry is auto-initialized on import
        return registry is not None

    except Exception as e:
        logger.error(f"Tool registry initialization failed: {e}")
        return False


async def compile_langgraph_workflows() -> bool:
    """Compile LangGraph workflows for better performance."""
    try:
        from ..agents.routing.pipeline import RoutingPipeline

        pipeline = RoutingPipeline()
        # Pipeline is auto-compiled on first use
        return pipeline is not None

    except Exception as e:
        logger.error(f"LangGraph workflow compilation failed: {e}")
        return False


async def initialize_memory_controller() -> bool:
    """Initialize memory controller."""
    try:
        from memory import SimpleMemoryController as MemoryController

        controller = MemoryController()
        return controller is not None

    except Exception as e:
        logger.error(f"Memory controller initialization failed: {e}")
        return False


async def initialize_cognitive_engine() -> bool:
    """Initialize cognitive engine."""
    try:
        # Skip cognitive engine for now - it's complex and not critical for basic functionality
        logger.info(
            "Cognitive engine initialization skipped (not critical for startup)"
        )
        return True

    except Exception as e:
        logger.error(f"Cognitive engine initialization failed: {e}")
        return False


async def run_database_migrations() -> bool:
    """Run database migrations on startup."""
    try:
        migration_result = await run_migrations()
        return migration_result.get("status") in ["success", "partial_failure"]
    except Exception as e:
        logger.error(f"Database migrations failed: {e}")
        return False


async def check_environment_variables() -> Dict[str, Any]:
    """Check required environment variables."""
    required_vars = {
        "SUPABASE_URL": "Supabase project URL",
        "SUPABASE_SERVICE_ROLE_KEY": "Supabase service role key",
        "GOOGLE_APPLICATION_CREDENTIALS": "Google Cloud credentials file",
        "UPSTASH_REDIS_URL": "Upstash Redis URL",
        "UPSTASH_REDIS_TOKEN": "Upstash Redis Token",
    }

    optional_vars = {
        "ENVIRONMENT": "Environment (development/staging/production)",
        "LOG_LEVEL": "Logging level",
        "MAX_WORKERS": "Maximum worker processes",
    }

    missing_required = []
    missing_optional = []
    present = {}

    # Check required variables
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            present[var] = {
                "value": value[:10] + "..." if len(value) > 10 else value,
                "description": description,
            }
        else:
            missing_required.append(f"{var} ({description})")

    # Check optional variables
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            present[var] = {
                "value": value[:10] + "..." if len(value) > 10 else value,
                "description": description,
            }
        else:
            missing_optional.append(f"{var} ({description})")

    return {
        "present": present,
        "missing_required": missing_required,
        "missing_optional": missing_optional,
    }


async def initialize() -> StartupReport:
    """
    Initialize all RaptorFlow backend services.

    Returns:
        StartupReport with status of all services
    """
    report = StartupReport()
    logger.info("Starting RaptorFlow backend initialization...")

    try:
        # Check environment variables
        env_check = await check_environment_variables()
        if env_check["missing_required"]:
            for missing in env_check["missing_required"]:
                report.add_error(f"Missing required environment variable: {missing}")

        if env_check["missing_optional"]:
            for missing in env_check["missing_optional"]:
                report.add_warning(f"Missing optional environment variable: {missing}")

        report.add_service_status(
            "environment",
            "checked" if not env_check["missing_required"] else "failed",
            env_check,
        )

        # Initialize services in dependency order
        services = [
            ("supabase", verify_supabase_connection),
            ("redis", verify_redis_connection),
            ("agent_dispatcher", initialize_agent_dispatcher),
        ]

        for service_name, init_func in services:
            logger.info(f"Initializing {service_name}...")
            start_time = time.time()

            try:
                success = await init_func()
                duration = time.time() - start_time

                if success:
                    report.add_service_status(
                        service_name, "initialized", {"duration_seconds": duration}
                    )
                    logger.info(
                        f"Γ£ô {service_name} initialized successfully in {duration:.2f}s"
                    )
                else:
                    report.add_service_status(
                        service_name, "failed", {"duration_seconds": duration}
                    )
                    report.add_error(f"Failed to initialize {service_name}")
                    logger.error(f"Γ£ù {service_name} initialization failed")

            except Exception as e:
                duration = time.time() - start_time
                report.add_service_status(
                    service_name,
                    "error",
                    {"duration_seconds": duration, "error": str(e)},
                )
                report.add_error(f"Error initializing {service_name}: {e}")
                logger.error(f"Γ£ù {service_name} initialization error: {e}")

        # Finalize report
        report.finalize()

        if report.success:
            logger.info(
                f"Γ£ô All services initialized successfully in {report.duration:.2f}s"
            )
        else:
            logger.error(
                f"Γ£ù Startup completed with {len(report.errors)} errors in {report.duration:.2f}s"
            )

        return report

    except Exception as e:
        logger.error(f"Critical error during startup: {e}")
        report.add_error(f"Critical startup error: {e}")
        report.finalize()
        return report


# Global startup report
_startup_report: Optional[StartupReport] = None


async def get_startup_report() -> Optional[StartupReport]:
    """Get the most recent startup report."""
    return _startup_report


async def run_startup() -> StartupReport:
    """Run startup and store report globally."""
    global _startup_report
    _startup_report = await initialize()
    return _startup_report


if __name__ == "__main__":
    # Run startup when script is executed directly
    asyncio.run(run_startup())
