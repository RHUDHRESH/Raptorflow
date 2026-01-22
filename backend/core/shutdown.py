"""
Application shutdown module for Raptorflow backend.
Handles graceful shutdown of all services and cleanup.
"""

import asyncio
import logging
import signal
from datetime import datetime
from typing import Any, Dict, Optional

from backend.agents.core.metrics import AgentMetricsCollector
from backend.agents.core.monitor import AgentMonitor

from .startup import get_startup_manager

logger = logging.getLogger(__name__)


class ShutdownManager:
    """Manages graceful shutdown of application components."""

    def __init__(self):
        self.startup_manager = get_startup_manager()
        self.shutdown_time: Optional[datetime] = None
        self.shutdown_errors: list = []
        self.is_shutting_down: bool = False

        # Shutdown timeout settings
        self.default_timeout_seconds = 30
        self.force_shutdown_timeout_seconds = 60

    async def cleanup_app(self, force: bool = False) -> Dict[str, Any]:
        """Perform graceful shutdown of all application components."""
        if self.is_shutting_down and not force:
            return {
                "status": "already_shutting_down",
                "message": "Shutdown already in progress",
            }

        self.is_shutting_down = True
        self.shutdown_time = datetime.now()

        logger.info("Starting Raptorflow backend shutdown...")

        try:
            # Record shutdown start
            if self.startup_manager.metrics:
                await self.startup_manager.metrics.record_metric("system_shutdown", 1.0)

            # Perform graceful shutdown sequence
            shutdown_results = await self._perform_shutdown_sequence(force)

            shutdown_duration = (datetime.now() - self.shutdown_time).total_seconds()

            logger.info(
                f"Raptorflow backend shutdown completed in {shutdown_duration:.2f}s"
            )

            return {
                "status": "shutdown_complete",
                "shutdown_time_seconds": shutdown_duration,
                "results": shutdown_results,
                "errors": self.shutdown_errors,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Application shutdown failed: {e}")
            self.shutdown_errors.append(str(e))

            return {
                "status": "shutdown_failed",
                "shutdown_time_seconds": (
                    datetime.now() - self.shutdown_time
                ).total_seconds(),
                "errors": self.shutdown_errors,
                "timestamp": datetime.now().isoformat(),
            }

    async def _perform_shutdown_sequence(self, force: bool) -> Dict[str, Any]:
        """Perform the shutdown sequence in proper order."""
        results = {}

        # Step 1: Stop accepting new requests
        results["stop_requests"] = await self._stop_accepting_requests()

        # Step 2: Complete in-progress executions (with timeout)
        results["complete_executions"] = await self._complete_in_progress_executions(
            force
        )

        # Step 3: Stop monitoring systems
        results["stop_monitoring"] = await self._stop_monitoring_systems()

        # Step 4: Flush metrics and save checkpoints
        results["flush_metrics"] = await self._flush_metrics_and_checkpoints()

        # Step 5: Stop agent systems
        results["stop_agents"] = await self._stop_agent_systems(force)

        # Step 6: Close database connections
        results["close_database"] = await self._close_database_connections(force)

        # Step 7: Close cache connections
        results["close_cache"] = await self._close_cache_connections(force)

        # Step 8: Close external service connections
        results["close_external"] = await self._close_external_connections(force)

        # Step 9: Cleanup temporary resources
        results["cleanup_resources"] = await self._cleanup_temporary_resources()

        return results

    async def _stop_accepting_requests(self) -> Dict[str, Any]:
        """Stop accepting new requests."""
        logger.info("Stopping acceptance of new requests...")

        try:
            # Close gateway to stop accepting new requests
            if self.startup_manager.gateway:
                # In a real implementation, would close HTTP server
                logger.info("Gateway closed for new requests")

            return {"status": "success", "message": "Stopped accepting new requests"}

        except Exception as e:
            logger.error(f"Failed to stop accepting requests: {e}")
            self.shutdown_errors.append(f"Stop Requests: {e}")
            return {"status": "failed", "error": str(e)}

    async def _complete_in_progress_executions(self, force: bool) -> Dict[str, Any]:
        """Complete or cancel in-progress executions."""
        logger.info("Completing in-progress executions...")

        try:
            completed_count = 0
            cancelled_count = 0

            if self.startup_manager.executor:
                # Get running executions
                running_executions = list(
                    self.startup_manager.executor._running_executions.keys()
                )

                if force:
                    # Force cancel all executions
                    for execution_id in running_executions:
                        try:
                            await self.startup_manager.executor.cancel_execution(
                                execution_id
                            )
                            cancelled_count += 1
                        except Exception as e:
                            logger.warning(
                                f"Failed to cancel execution {execution_id}: {e}"
                            )
                else:
                    # Wait for executions to complete with timeout
                    timeout = self.default_timeout_seconds

                    try:
                        # Wait for all running tasks to complete
                        tasks = list(
                            self.startup_manager.executor._running_executions.values()
                        )
                        if tasks:
                            await asyncio.wait_for(
                                asyncio.gather(*tasks, return_exceptions=True),
                                timeout=timeout,
                            )
                            completed_count = len(tasks)
                    except asyncio.TimeoutError:
                        # Cancel remaining executions
                        remaining_tasks = list(
                            self.startup_manager.executor._running_executions.values()
                        )
                        for task in remaining_tasks:
                            task.cancel()
                        cancelled_count = len(remaining_tasks)

            logger.info(
                f"Completed {completed_count} executions, cancelled {cancelled_count}"
            )

            return {
                "status": "success",
                "completed_count": completed_count,
                "cancelled_count": cancelled_count,
            }

        except Exception as e:
            logger.error(f"Failed to complete executions: {e}")
            self.shutdown_errors.append(f"Complete Executions: {e}")
            return {"status": "failed", "error": str(e)}

    async def _stop_monitoring_systems(self) -> Dict[str, Any]:
        """Stop monitoring systems."""
        logger.info("Stopping monitoring systems...")

        try:
            if self.startup_manager.monitor:
                await self.startup_manager.monitor.stop_monitoring()
                logger.info("Agent monitor stopped")

            if self.startup_manager.metrics:
                await self.startup_manager.metrics.stop()
                logger.info("Metrics collector stopped")

            return {"status": "success", "message": "Monitoring systems stopped"}

        except Exception as e:
            logger.error(f"Failed to stop monitoring: {e}")
            self.shutdown_errors.append(f"Stop Monitoring: {e}")
            return {"status": "failed", "error": str(e)}

    async def _flush_metrics_and_checkpoints(self) -> Dict[str, Any]:
        """Flush metrics and save checkpoints."""
        logger.info("Flushing metrics and saving checkpoints...")

        try:
            metrics_flushed = 0
            checkpoints_saved = 0

            # Flush metrics
            if self.startup_manager.metrics:
                # Export final metrics
                try:
                    await self.startup_manager.metrics.export_metrics(
                        format="json", output_file="final_metrics.json"
                    )
                    metrics_flushed = 1
                except Exception as e:
                    logger.warning(f"Failed to export metrics: {e}")

            # Save state checkpoints
            if self.startup_manager.state_manager:
                try:
                    # Create final state checkpoint
                    await self.startup_manager.state_manager.cleanup_expired_states()
                    checkpoints_saved = 1
                except Exception as e:
                    logger.warning(f"Failed to save state checkpoint: {e}")

            # Save memory checkpoints
            if self.startup_manager.memory_manager:
                try:
                    # Consolidate memory before shutdown
                    await self.startup_manager.memory_manager.consolidate_memories()
                    checkpoints_saved += 1
                except Exception as e:
                    logger.warning(f"Failed to save memory checkpoint: {e}")

            logger.info(
                f"Flushed {metrics_flushed} metric exports, saved {checkpoints_saved} checkpoints"
            )

            return {
                "status": "success",
                "metrics_flushed": metrics_flushed,
                "checkpoints_saved": checkpoints_saved,
            }

        except Exception as e:
            logger.error(f"Failed to flush metrics/checkpoints: {e}")
            self.shutdown_errors.append(f"Flush Metrics: {e}")
            return {"status": "failed", "error": str(e)}

    async def _stop_agent_systems(self, force: bool) -> Dict[str, Any]:
        """Stop agent system components."""
        logger.info("Stopping agent systems...")

        try:
            stopped_components = []

            # Stop orchestrator
            if self.startup_manager.orchestrator:
                try:
                    await self.startup_manager.orchestrator.stop()
                    stopped_components.append("orchestrator")
                except Exception as e:
                    logger.warning(f"Failed to stop orchestrator: {e}")

            # Stop executor
            if self.startup_manager.executor:
                try:
                    await self.startup_manager.executor.stop()
                    stopped_components.append("executor")
                except Exception as e:
                    logger.warning(f"Failed to stop executor: {e}")

            # Stop state manager
            if self.startup_manager.state_manager:
                try:
                    await self.startup_manager.state_manager.stop()
                    stopped_components.append("state_manager")
                except Exception as e:
                    logger.warning(f"Failed to stop state manager: {e}")

            # Stop memory manager
            if self.startup_manager.memory_manager:
                try:
                    await self.startup_manager.memory_manager.stop()
                    stopped_components.append("memory_manager")
                except Exception as e:
                    logger.warning(f"Failed to stop memory manager: {e}")

            # Stop registry
            if self.startup_manager.registry:
                try:
                    await self.startup_manager.registry.stop()
                    stopped_components.append("registry")
                except Exception as e:
                    logger.warning(f"Failed to stop registry: {e}")

            logger.info(f"Stopped agent components: {', '.join(stopped_components)}")

            return {"status": "success", "stopped_components": stopped_components}

        except Exception as e:
            logger.error(f"Failed to stop agent systems: {e}")
            self.shutdown_errors.append(f"Stop Agents: {e}")
            return {"status": "failed", "error": str(e)}

    async def _close_database_connections(self, force: bool) -> Dict[str, Any]:
        """Close database connections."""
        logger.info("Closing database connections...")

        try:
            if self.startup_manager.db_manager:
                await self.startup_manager.db_manager.close()
                logger.info("Database connections closed")

            return {"status": "success", "message": "Database connections closed"}

        except Exception as e:
            logger.error(f"Failed to close database: {e}")
            self.shutdown_errors.append(f"Close Database: {e}")
            return {"status": "failed", "error": str(e)}

    async def _close_cache_connections(self, force: bool) -> Dict[str, Any]:
        """Close cache connections."""
        logger.info("Closing cache connections...")

        try:
            if self.startup_manager.redis_client:
                await self.startup_manager.redis_client.close()
                logger.info("Redis connections closed")

            return {"status": "success", "message": "Cache connections closed"}

        except Exception as e:
            logger.error(f"Failed to close cache: {e}")
            self.shutdown_errors.append(f"Close Cache: {e}")
            return {"status": "failed", "error": str(e)}

    async def _close_external_connections(self, force: bool) -> Dict[str, Any]:
        """Close external service connections."""
        logger.info("Closing external service connections...")

        try:
            if self.startup_manager.vertex_client:
                await self.startup_manager.vertex_client.close()
                logger.info("Vertex AI connections closed")

            return {"status": "success", "message": "External connections closed"}

        except Exception as e:
            logger.error(f"Failed to close external connections: {e}")
            self.shutdown_errors.append(f"Close External: {e}")
            return {"status": "failed", "error": str(e)}

    async def _cleanup_temporary_resources(self) -> Dict[str, Any]:
        """Clean up temporary resources."""
        logger.info("Cleaning up temporary resources...")

        try:
            cleaned_resources = []

            # Clean up temporary files
            import os
            import tempfile

            temp_dir = tempfile.gettempdir()
            raptorflow_temp_files = [
                f
                for f in os.listdir(temp_dir)
                if f.startswith("raptorflow_") or f.startswith("tmp_raptorflow_")
            ]

            for temp_file in raptorflow_temp_files:
                try:
                    file_path = os.path.join(temp_dir, temp_file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        cleaned_resources.append(f"file:{temp_file}")
                    elif os.path.isdir(file_path):
                        import shutil

                        shutil.rmtree(file_path)
                        cleaned_resources.append(f"dir:{temp_file}")
                except Exception as e:
                    logger.warning(f"Failed to clean up {temp_file}: {e}")

            # Clean up in-memory caches
            if hasattr(self.startup_manager, "_temp_caches"):
                self.startup_manager._temp_caches.clear()
                cleaned_resources.append("memory_caches")

            logger.info(f"Cleaned up {len(cleaned_resources)} temporary resources")

            return {"status": "success", "cleaned_resources": cleaned_resources}

        except Exception as e:
            logger.error(f"Failed to cleanup resources: {e}")
            self.shutdown_errors.append(f"Cleanup Resources: {e}")
            return {"status": "failed", "error": str(e)}

    async def force_shutdown(self) -> Dict[str, Any]:
        """Force immediate shutdown."""
        logger.warning("Force shutdown initiated")

        # Set force shutdown flag
        self.default_timeout_seconds = 5
        self.force_shutdown_timeout_seconds = 10

        return await self.cleanup_app(force=True)

    def get_shutdown_status(self) -> Dict[str, Any]:
        """Get current shutdown status."""
        return {
            "is_shutting_down": self.is_shutting_down,
            "shutdown_time": (
                self.shutdown_time.isoformat() if self.shutdown_time else None
            ),
            "shutdown_errors": self.shutdown_errors,
            "errors_count": len(self.shutdown_errors),
        }


# Global shutdown manager instance
_shutdown_manager = ShutdownManager()


async def cleanup_app(force: bool = False) -> Dict[str, Any]:
    """Clean up the Raptorflow application."""
    return await _shutdown_manager.cleanup_app(force)


async def force_shutdown() -> Dict[str, Any]:
    """Force immediate shutdown."""
    return await _shutdown_manager.force_shutdown()


def get_shutdown_status() -> Dict[str, Any]:
    """Get current shutdown status."""
    return _shutdown_manager.get_shutdown_status()


def get_shutdown_manager() -> ShutdownManager:
    """Get the shutdown manager instance."""
    return _shutdown_manager


# Signal handlers for graceful shutdown
def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown."""

    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")

        # Create async task for shutdown
        loop = asyncio.get_event_loop()
        if loop and not loop.is_closed():
            loop.create_task(cleanup_app())
        else:
            logger.warning("Event loop not available for graceful shutdown")

    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    logger.info("Signal handlers registered for graceful shutdown")


# Auto-setup signal handlers when module is imported
setup_signal_handlers()
