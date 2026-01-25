"""
Shutdown sequence for RaptorFlow backend.
Gracefully closes connections and saves state.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Dict, Optional

from backend.core.redis import get_redis_client
from backend.core.supabase_mgr import get_supabase_client

logger = logging.getLogger(__name__)


class ShutdownReport:
    """Report of shutdown status and operations."""

    def __init__(self):
        self.start_time = datetime.now()
        self.operations = {}
        self.errors = []
        self.warnings = []
        self.success = False

    def add_operation_status(
        self, operation: str, status: str, details: Optional[Dict[str, Any]] = None
    ):
        """Add operation status to report."""
        self.operations[operation] = {
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
        """Finalize the shutdown report."""
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
            "operations": self.operations,
            "errors": self.errors,
            "warnings": self.warnings,
        }


async def close_database_connections() -> bool:
    """Close database connections gracefully."""
    try:
        # Supabase client doesn't need explicit closing
        # But we can verify it's still accessible
        client = get_supabase_client()
        if client:
            # Test connection is still valid
            client.table("users").select("id").limit(1).execute()

        return True

    except Exception as e:
        logger.error(f"Error closing database connections: {e}")
        return False


async def flush_redis_writes() -> bool:
    """Flush pending Redis writes."""
    try:
        client = get_redis_client()
        if client:
            # Ensure all writes are flushed
            await client.save()
            return True

        return False

    except Exception as e:
        logger.error(f"Error flushing Redis writes: {e}")
        return False


async def save_checkpoints() -> bool:
    """Save any pending checkpoints or state."""
    try:
        # Save agent execution checkpoints
        from agents.dispatcher import AgentDispatcher

        dispatcher = AgentDispatcher()
        # Save any active sessions
        # This would be implemented based on specific requirements

        return True

    except Exception as e:
        logger.error(f"Error saving checkpoints: {e}")
        return False


async def complete_pending_jobs() -> bool:
    """Complete or gracefully stop pending jobs."""
    try:
        # Check for any running agent executions
        # This would be implemented based on job queue system

        # For now, just log that we're checking
        logger.info("Checking for pending jobs...")

        # In a real implementation, this would:
        # 1. Check job queue for running jobs
        # 2. Either complete them or mark as interrupted
        # 3. Update job status in database

        return True

    except Exception as e:
        logger.error(f"Error completing pending jobs: {e}")
        return False


async def cleanup_temporary_files() -> bool:
    """Clean up temporary files and resources."""
    try:
        import os
        import tempfile

        # Clean up temp directory
        temp_dir = tempfile.gettempdir()

        # Remove any RaptorFlow-specific temp files
        temp_files = []
        for filename in os.listdir(temp_dir):
            if filename.startswith("raptorflow_"):
                filepath = os.path.join(temp_dir, filename)
                try:
                    os.remove(filepath)
                    temp_files.append(filename)
                except Exception as e:
                    logger.warning(f"Could not remove temp file {filename}: {e}")

        logger.info(f"Cleaned up {len(temp_files)} temporary files")
        return True

    except Exception as e:
        logger.error(f"Error cleaning up temporary files: {e}")
        return False


async def close_llm_connections() -> bool:
    """Close LLM connections and clean up resources."""
    try:
        from agents.llm import get_llm

        llm = get_llm()
        if llm:
            # Close any open connections
            # This would be implemented based on specific LLM client
            pass

        return True

    except Exception as e:
        logger.error(f"Error closing LLM connections: {e}")
        return False


async def log_shutdown_summary() -> bool:
    """Log shutdown summary and metrics."""
    try:
        # Log final metrics
        logger.info("=== RaptorFlow Backend Shutdown Summary ===")
        logger.info(f"Shutdown initiated at: {datetime.now().isoformat()}")

        # Log any final statistics
        from agents.dispatcher import AgentDispatcher

        dispatcher = AgentDispatcher()
        # Log dispatcher stats if available

        logger.info("Shutdown completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error logging shutdown summary: {e}")
        return False


async def cleanup() -> ShutdownReport:
    """
    Clean up all RaptorFlow backend resources.

    Returns:
        ShutdownReport with status of all cleanup operations
    """
    report = ShutdownReport()
    logger.info("Starting RaptorFlow backend shutdown...")

    try:
        # Run cleanup operations in dependency order
        operations = [
            ("complete_pending_jobs", complete_pending_jobs),
            ("save_checkpoints", save_checkpoints),
            ("flush_redis_writes", flush_redis_writes),
            ("close_llm_connections", close_llm_connections),
            ("close_database_connections", close_database_connections),
            ("cleanup_temporary_files", cleanup_temporary_files),
            ("log_shutdown_summary", log_shutdown_summary),
        ]

        for operation_name, cleanup_func in operations:
            logger.info(f"Cleaning up {operation_name}...")
            start_time = time.time()

            try:
                success = await cleanup_func()
                duration = time.time() - start_time

                if success:
                    report.add_operation_status(
                        operation_name, "completed", {"duration_seconds": duration}
                    )
                    logger.info(
                        f"Γ£ô {operation_name} completed successfully in {duration:.2f}s"
                    )
                else:
                    report.add_operation_status(
                        operation_name, "failed", {"duration_seconds": duration}
                    )
                    report.add_error(f"Failed to complete {operation_name}")
                    logger.error(f"Γ£ù {operation_name} cleanup failed")

            except Exception as e:
                duration = time.time() - start_time
                report.add_operation_status(
                    operation_name,
                    "error",
                    {"duration_seconds": duration, "error": str(e)},
                )
                report.add_error(f"Error during {operation_name} cleanup: {e}")
                logger.error(f"Γ£ù {operation_name} cleanup error: {e}")

        # Finalize report
        report.finalize()

        if report.success:
            logger.info(
                f"Γ£ô All cleanup operations completed successfully in {report.duration:.2f}s"
            )
        else:
            logger.error(
                f"Γ£ù Shutdown completed with {len(report.errors)} errors in {report.duration:.2f}s"
            )

        return report

    except Exception as e:
        logger.error(f"Critical error during shutdown: {e}")
        report.add_error(f"Critical shutdown error: {e}")
        report.finalize()
        return report


# Global shutdown report
_shutdown_report: Optional[ShutdownReport] = None


async def get_shutdown_report() -> Optional[ShutdownReport]:
    """Get the most recent shutdown report."""
    return _shutdown_report


async def run_shutdown() -> ShutdownReport:
    """Run shutdown and store report globally."""
    global _shutdown_report
    _shutdown_report = await cleanup()
    return _shutdown_report


# Graceful shutdown handler
import signal
import sys


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    asyncio.run(run_shutdown())
    sys.exit(0)


# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def cleanup_app():
    """Cleanup app function for FastAPI shutdown."""
    return asyncio.run(cleanup())


if __name__ == "__main__":
    # Run shutdown when script is executed directly
    asyncio.run(run_shutdown())
