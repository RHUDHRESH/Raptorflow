"""
Resource and metrics system initialization for Raptorflow backend.
Initializes and starts all resource management components.
"""

import asyncio
import logging
import signal
import sys
from typing import Optional

from .resources import get_resource_manager, start_resource_manager, stop_resource_manager
from .metrics_collector import get_metrics_collector, start_metrics_collector, stop_metrics_collector
from .resource_analytics import get_resource_analyzer, start_resource_analyzer, stop_resource_analyzer
from .quota_manager import get_quota_manager, start_quota_manager, stop_quota_manager
from .cleanup_scheduler import get_cleanup_scheduler, start_cleanup_scheduler, stop_cleanup_scheduler

logger = logging.getLogger(__name__)


class ResourceSystemManager:
    """Manages the lifecycle of all resource and metrics systems."""
    
    def __init__(self):
        self._running = False
        self._shutdown_event = asyncio.Event()
        
        # System components
        self.resource_manager = None
        self.metrics_collector = None
        self.resource_analyzer = None
        self.quota_manager = None
        self.cleanup_scheduler = None
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start(self):
        """Start all resource and metrics systems."""
        if self._running:
            logger.warning("Resource systems already running")
            return
        
        logger.info("Starting resource and metrics systems...")
        
        try:
            # 1. Start Resource Manager
            logger.info("Starting resource manager...")
            self.resource_manager = get_resource_manager()
            await start_resource_manager()
            logger.info("Resource manager started successfully")
            
            # 2. Start Metrics Collector
            logger.info("Starting metrics collector...")
            self.metrics_collector = get_metrics_collector()
            await start_metrics_collector()
            logger.info("Metrics collector started successfully")
            
            # 3. Start Resource Analyzer
            logger.info("Starting resource analyzer...")
            self.resource_analyzer = get_resource_analyzer()
            await start_resource_analyzer()
            logger.info("Resource analyzer started successfully")
            
            # 4. Start Quota Manager
            logger.info("Starting quota manager...")
            self.quota_manager = get_quota_manager()
            await start_quota_manager()
            logger.info("Quota manager started successfully")
            
            # 5. Start Cleanup Scheduler
            logger.info("Starting cleanup scheduler...")
            self.cleanup_scheduler = get_cleanup_scheduler()
            await start_cleanup_scheduler()
            logger.info("Cleanup scheduler started successfully")
            
            self._running = True
            
            # Log system status
            await self._log_system_status()
            
            logger.info("All resource and metrics systems started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start resource systems: {e}")
            await self.shutdown()
            raise
    
    async def stop(self):
        """Stop all resource and metrics systems."""
        if not self._running:
            return
        
        logger.info("Stopping resource and metrics systems...")
        
        try:
            # Stop in reverse order of startup
            if self.cleanup_scheduler:
                logger.info("Stopping cleanup scheduler...")
                await stop_cleanup_scheduler()
                logger.info("Cleanup scheduler stopped")
            
            if self.quota_manager:
                logger.info("Stopping quota manager...")
                await stop_quota_manager()
                logger.info("Quota manager stopped")
            
            if self.resource_analyzer:
                logger.info("Stopping resource analyzer...")
                await stop_resource_analyzer()
                logger.info("Resource analyzer stopped")
            
            if self.metrics_collector:
                logger.info("Stopping metrics collector...")
                await stop_metrics_collector()
                logger.info("Metrics collector stopped")
            
            if self.resource_manager:
                logger.info("Stopping resource manager...")
                await stop_resource_manager()
                logger.info("Resource manager stopped")
            
            self._running = False
            logger.info("All resource and metrics systems stopped successfully")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    async def shutdown(self):
        """Initiate graceful shutdown."""
        self._shutdown_event.set()
        await self.stop()
    
    async def _log_system_status(self):
        """Log current system status."""
        try:
            # Resource Manager Status
            if self.resource_manager:
                resource_summary = self.resource_manager.get_resource_summary()
                logger.info(f"Resource Manager Status: {resource_summary['total_resources']} resources tracked")
                
                # Log any leaks
                leaks = self.resource_manager.get_leaked_resources()
                if leaks:
                    logger.warning(f"Detected {len(leaks)} resource leaks")
            
            # Metrics Collector Status
            if self.metrics_collector:
                metrics_summary = self.metrics_collector.get_metrics_summary()
                logger.info(f"Metrics Collector Status: {metrics_summary['total_metrics']} metrics defined, {metrics_summary['total_values']} values recorded")
                
                # Log active alerts
                active_alerts = self.metrics_collector.get_active_alerts()
                if active_alerts:
                    logger.warning(f"Active alerts: {len(active_alerts)}")
            
            # Resource Analyzer Status
            if self.resource_analyzer:
                analysis_summary = self.resource_analyzer.get_analysis_summary()
                logger.info(f"Resource Analyzer Status: {analysis_summary['total_patterns_detected']} patterns detected, {analysis_summary['total_recommendations']} recommendations generated")
            
            # Quota Manager Status
            if self.quota_manager:
                quota_metrics = self.quota_manager.quota_metrics
                logger.info(f"Quota Manager Status: {quota_metrics['total_checks']} checks performed, {quota_metrics['total_violations']} violations")
            
            # Cleanup Scheduler Status
            if self.cleanup_scheduler:
                scheduler_metrics = self.cleanup_scheduler.get_scheduler_metrics()
                logger.info(f"Cleanup Scheduler Status: {scheduler_metrics['total_tasks']} tasks configured, {scheduler_metrics['success_rate']:.1f}% success rate")
                
        except Exception as e:
            logger.error(f"Failed to log system status: {e}")
    
    async def health_check(self) -> dict:
        """Perform health check of all systems."""
        health_status = {
            "overall": "healthy",
            "timestamp": None,
            "systems": {}
        }
        
        try:
            from datetime import datetime
            health_status["timestamp"] = datetime.now().isoformat()
            
            # Check Resource Manager
            if self.resource_manager:
                resource_summary = self.resource_manager.get_resource_summary()
                leaks = self.resource_manager.get_leaked_resources()
                
                resource_health = "healthy"
                if len(leaks) > 10:
                    resource_health = "degraded"
                if len(leaks) > 50:
                    resource_health = "unhealthy"
                
                health_status["systems"]["resource_manager"] = {
                    "status": resource_health,
                    "resources_tracked": resource_summary["total_resources"],
                    "active_leaks": len(leaks)
                }
            
            # Check Metrics Collector
            if self.metrics_collector:
                metrics_summary = self.metrics_collector.get_metrics_summary()
                active_alerts = self.metrics_collector.get_active_alerts()
                
                metrics_health = "healthy"
                if len(active_alerts) > 5:
                    metrics_health = "degraded"
                if len(active_alerts) > 20:
                    metrics_health = "unhealthy"
                
                health_status["systems"]["metrics_collector"] = {
                    "status": metrics_health,
                    "metrics_defined": metrics_summary["total_metrics"],
                    "active_alerts": len(active_alerts)
                }
            
            # Check Resource Analyzer
            if self.resource_analyzer:
                analysis_summary = self.resource_analyzer.get_analysis_summary()
                
                analyzer_health = "healthy"
                # Analyzer is generally healthy unless there are errors
                # Could add more sophisticated health checks here
                
                health_status["systems"]["resource_analyzer"] = {
                    "status": analyzer_health,
                    "patterns_detected": analysis_summary["total_patterns_detected"],
                    "recommendations": analysis_summary["total_recommendations"]
                }
            
            # Check Quota Manager
            if self.quota_manager:
                quota_metrics = self.quota_manager.quota_metrics
                recent_violations = [
                    v for v in self.quota_manager.quota_violations
                    if (datetime.now() - v.violation_time).total_seconds() < 3600  # Last hour
                ]
                
                quota_health = "healthy"
                if len(recent_violations) > 10:
                    quota_health = "degraded"
                if len(recent_violations) > 50:
                    quota_health = "unhealthy"
                
                health_status["systems"]["quota_manager"] = {
                    "status": quota_health,
                    "total_checks": quota_metrics["total_checks"],
                    "recent_violations": len(recent_violations)
                }
            
            # Check Cleanup Scheduler
            if self.cleanup_scheduler:
                scheduler_metrics = self.cleanup_scheduler.get_scheduler_metrics()
                
                scheduler_health = "healthy"
                if scheduler_metrics["success_rate"] < 80:
                    scheduler_health = "degraded"
                if scheduler_metrics["success_rate"] < 50:
                    scheduler_health = "unhealthy"
                
                health_status["systems"]["cleanup_scheduler"] = {
                    "status": scheduler_health,
                    "tasks_configured": scheduler_metrics["total_tasks"],
                    "success_rate": scheduler_metrics["success_rate"]
                }
            
            # Determine overall health
            system_statuses = [s["status"] for s in health_status["systems"].values()]
            if any(status == "unhealthy" for status in system_statuses):
                health_status["overall"] = "unhealthy"
            elif any(status == "degraded" for status in system_statuses):
                health_status["overall"] = "degraded"
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            health_status["overall"] = "error"
            health_status["error"] = str(e)
        
        return health_status
    
    async def wait_for_shutdown(self):
        """Wait for shutdown signal."""
        await self._shutdown_event.wait()


# Global instance
_resource_system_manager: Optional[ResourceSystemManager] = None


def get_resource_system_manager() -> ResourceSystemManager:
    """Get the global resource system manager instance."""
    global _resource_system_manager
    if _resource_system_manager is None:
        _resource_system_manager = ResourceSystemManager()
    return _resource_system_manager


async def start_resource_systems():
    """Start all resource and metrics systems."""
    manager = get_resource_system_manager()
    await manager.start()


async def stop_resource_systems():
    """Stop all resource and metrics systems."""
    manager = get_resource_system_manager()
    await manager.stop()


async def get_system_health() -> dict:
    """Get health status of all systems."""
    manager = get_resource_system_manager()
    return await manager.health_check()


# CLI interface for standalone operation
async def main():
    """Main function for running resource systems standalone."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Raptorflow Resource and Metrics System")
    parser.add_argument(
        "--health-check",
        action="store_true",
        help="Perform health check and exit"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show system status and exit"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon (continuous operation)"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if args.health_check:
        # Perform health check
        health = await get_system_health()
        print(f"System Health: {health['overall']}")
        for system, status in health["systems"].items():
            print(f"  {system}: {status['status']}")
        return
    
    if args.status:
        # Show system status
        manager = get_resource_system_manager()
        await manager._log_system_status()
        return
    
    # Start systems (daemon mode or default)
    try:
        await start_resource_systems()
        
        if args.daemon:
            # Run indefinitely
            await manager.wait_for_shutdown()
        else:
            # Run for a short time then exit
            await asyncio.sleep(5)
            await stop_resource_systems()
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        await stop_resource_systems()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
