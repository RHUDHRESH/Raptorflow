"""
Cognitive Engine Startup and Shutdown Manager
Handles proper initialization and cleanup of all services
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from .config_manager import config_manager
from di import container
from engine import CognitiveEngine
from health_monitor import health_monitor
from metrics import metrics_collector
from rate_limiter import rate_limiter
from session_manager import SessionManager

logger = logging.getLogger(__name__)


class CognitiveEngineManager:
    """Manages the complete lifecycle of the Cognitive Engine"""

    def __init__(self):
        self.engine: Optional[CognitiveEngine] = None
        self.is_running = False
        self.startup_time: Optional[datetime] = None
        self.shutdown_time: Optional[datetime] = None

    async def initialize(
        self,
        llm_client=None,
        storage_backend=None,
        cache_backend=None,
        config: Optional[Dict[str, Any]] = None,
    ) -> CognitiveEngine:
        """
        Initialize the complete cognitive engine system

        Args:
            llm_client: LLM client for advanced processing
            storage_backend: Storage backend for persistence
            cache_backend: Cache backend for performance
            config: Configuration settings

        Returns:
            Initialized CognitiveEngine instance
        """
        try:
            logger.info("Initializing Cognitive Engine system...")

            # Initialize configuration manager
            await config_manager.initialize()

            # Initialize metrics collector
            await metrics_collector.initialize()

            # Initialize rate limiter
            await rate_limiter.initialize()

            # Initialize health monitor
            await health_monitor.initialize()

            # Initialize session manager
            session_manager = SessionManager(
                storage_backend=storage_backend,
                cache_backend=cache_backend,
                default_ttl_hours=24,
            )
            await session_manager.initialize()

            # Create the cognitive engine
            self.engine = CognitiveEngine(
                llm_client=llm_client,
                storage_backend=storage_backend,
                cache_backend=cache_backend,
                config=config,
            )

            # Start background services
            await self.engine.start_background_services()

            self.is_running = True
            self.startup_time = datetime.now()

            logger.info("Cognitive Engine system initialized successfully")
            return self.engine

        except Exception as e:
            logger.error(f"Failed to initialize Cognitive Engine: {e}")
            await self.shutdown()
            raise

    async def shutdown(self) -> None:
        """Gracefully shutdown the cognitive engine system"""
        try:
            logger.info("Shutting down Cognitive Engine system...")

            if self.engine:
                # Stop background services
                await self.engine.stop_background_services()

                # Clear active sessions
                await self.engine.session_manager._cleanup_expired_sessions()

                self.engine = None

            # Shutdown services in reverse order
            await health_monitor.shutdown()
            await rate_limiter.shutdown()
            await metrics_collector.shutdown()
            await session_manager.shutdown()
            await config_manager.shutdown()

            self.is_running = False
            self.shutdown_time = datetime.now()

            logger.info("Cognitive Engine system shutdown complete")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        if not self.engine:
            return {
                "status": "unhealthy",
                "message": "Engine not initialized",
                "timestamp": datetime.now().isoformat(),
            }

        try:
            # Get engine health status
            engine_health = await self.engine.get_health_status()

            # Get background services status
            services_status = self.engine.get_background_services_status()

            # Get system metrics
            system_metrics = await self.engine.get_engine_metrics()

            # Overall status
            overall_status = "healthy"
            if engine_health.get("overall_status") != "healthy":
                overall_status = "degraded"

            if not all(s.get("running", False) for s in services_status.values()):
                overall_status = "unhealthy"

            return {
                "status": overall_status,
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": (
                    (datetime.now() - self.startup_time).total_seconds()
                    if self.startup_time
                    else 0
                ),
                "engine": engine_health,
                "services": services_status,
                "metrics": system_metrics,
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Health check failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            "is_running": self.is_running,
            "startup_time": (
                self.startup_time.isoformat() if self.startup_time else None
            ),
            "shutdown_time": (
                self.shutdown_time.isoformat() if self.shutdown_time else None
            ),
            "engine_initialized": self.engine is not None,
            "version": "1.0.0",
        }


# Global instance
engine_manager = CognitiveEngineManager()


async def get_engine() -> CognitiveEngine:
    """Get the initialized engine instance"""
    if not engine_manager.engine:
        raise RuntimeError("Engine not initialized. Call initialize() first.")
    return engine_manager.engine


async def initialize_engine(
    llm_client=None,
    storage_backend=None,
    cache_backend=None,
    config: Optional[Dict[str, Any]] = None,
) -> CognitiveEngine:
    """Initialize the global engine instance"""
    return await engine_manager.initialize(
        llm_client=llm_client,
        storage_backend=storage_backend,
        cache_backend=cache_backend,
        config=config,
    )


async def shutdown_engine() -> None:
    """Shutdown the global engine instance"""
    await engine_manager.shutdown()
