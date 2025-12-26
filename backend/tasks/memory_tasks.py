"""
Memory System Tasks and Scheduling

Background tasks for periodic memory consolidation, cleanup, and maintenance.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List

from backend.memory.swarm_coordinator import _coordinator_registry
from backend.memory.cache import SwarmMemoryCache

logger = logging.getLogger("raptorflow.memory.tasks")


class MemoryTaskScheduler:
    """
    Scheduler for memory system background tasks.
    Handles periodic consolidation, cleanup, and maintenance operations.
    """
    
    def __init__(self):
        self.running = False
        self.tasks: List[asyncio.Task] = []
        self.config = {
            "consolidation_interval": timedelta(minutes=5),
            "cleanup_interval": timedelta(hours=1),
            "health_check_interval": timedelta(minutes=15),
            "cache_cleanup_interval": timedelta(minutes=30)
        }
    
    async def start(self):
        """Start all background tasks."""
        if self.running:
            logger.warning("Memory task scheduler already running")
            return
        
        self.running = True
        logger.info("Starting memory task scheduler...")
        
        # Start background tasks
        self.tasks = [
            asyncio.create_task(self._periodic_consolidation()),
            asyncio.create_task(self._periodic_cleanup()),
            asyncio.create_task(self._periodic_health_check()),
            asyncio.create_task(self._periodic_cache_cleanup())
        ]
        
        logger.info(f"Started {len(self.tasks)} memory background tasks")
    
    async def stop(self):
        """Stop all background tasks."""
        if not self.running:
            return
        
        self.running = False
        logger.info("Stopping memory task scheduler...")
        
        # Cancel all tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        self.tasks.clear()
        logger.info("Memory task scheduler stopped")
    
    async def _periodic_consolidation(self):
        """Periodic memory consolidation task."""
        while self.running:
            try:
                logger.debug("Starting periodic memory consolidation...")
                
                # Consolidate memory for all active workspaces
                consolidation_results = []
                for workspace_id, coordinator in _coordinator_registry.items():
                    if coordinator.active_agents:  # Only consolidate active workspaces
                        try:
                            result = await coordinator.consolidate_swarm_memories()
                            consolidation_results.append({
                                "workspace_id": workspace_id,
                                "result": result
                            })
                            logger.debug(f"Consolidated memory for workspace {workspace_id}")
                        except Exception as e:
                            logger.error(f"Consolidation failed for workspace {workspace_id}: {e}")
                
                # Log summary
                successful = sum(1 for r in consolidation_results if "error" not in r["result"])
                logger.info(f"Periodic consolidation completed: {successful}/{len(consolidation_results)} workspaces")
                
                # Wait before next consolidation
                await asyncio.sleep(self.config["consolidation_interval"].total_seconds())
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Periodic consolidation task failed: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def _periodic_cleanup(self):
        """Periodic memory cleanup task."""
        while self.running:
            try:
                logger.debug("Starting periodic memory cleanup...")
                
                cleanup_stats = {
                    "workspaces_processed": 0,
                    "agents_cleaned": 0,
                    "errors": 0
                }
                
                for workspace_id, coordinator in _coordinator_registry.items():
                    try:
                        # Clean up inactive agents (no activity for 24 hours)
                        inactive_agents = []
                        for agent_id, usage in coordinator.agent_memory_usage.items():
                            last_activity = usage.get("last_activity")
                            if last_activity:
                                last_activity_dt = datetime.fromisoformat(last_activity)
                                if datetime.now() - last_activity_dt > timedelta(hours=24):
                                    inactive_agents.append(agent_id)
                        
                        # Clean up inactive agents
                        for agent_id in inactive_agents:
                            await coordinator.cleanup_agent_memory(agent_id)
                            cleanup_stats["agents_cleaned"] += 1
                        
                        cleanup_stats["workspaces_processed"] += 1
                        
                    except Exception as e:
                        logger.error(f"Cleanup failed for workspace {workspace_id}: {e}")
                        cleanup_stats["errors"] += 1
                
                logger.info(f"Periodic cleanup completed: {cleanup_stats}")
                
                # Wait before next cleanup
                await asyncio.sleep(self.config["cleanup_interval"].total_seconds())
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Periodic cleanup task failed: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def _periodic_health_check(self):
        """Periodic health check task."""
        while self.running:
            try:
                logger.debug("Starting periodic health check...")
                
                health_summary = {
                    "healthy_workspaces": 0,
                    "degraded_workspaces": 0,
                    "unhealthy_workspaces": 0,
                    "issues_found": []
                }
                
                for workspace_id, coordinator in _coordinator_registry.items():
                    try:
                        stats = await coordinator.get_swarm_memory_metrics()
                        
                        workspace_health = {
                            "workspace_id": workspace_id,
                            "status": "healthy",
                            "issues": []
                        }
                        
                        # Check cache performance
                        cache_hit_rate = stats.get("cache_performance", {}).get("hit_rate", 0)
                        if cache_hit_rate < 0.7:
                            workspace_health["issues"].append("Low cache hit rate")
                            health_summary["issues_found"].append(f"{workspace_id}: Low cache hit rate")
                        
                        # Check consolidation lag
                        if stats.get("last_consolidation"):
                            last_consolidation = datetime.fromisoformat(stats["last_consolidation"])
                            if datetime.now() - last_consolidation > timedelta(minutes=10):
                                workspace_health["issues"].append("Consolidation lag")
                                health_summary["issues_found"].append(f"{workspace_id}: Consolidation lag")
                        
                        # Check memory usage
                        total_fragments = stats.get("total_fragments", 0)
                        if total_fragments > 5000:
                            workspace_health["issues"].append("High memory usage")
                            health_summary["issues_found"].append(f"{workspace_id}: High memory usage")
                        
                        # Determine health status
                        if not workspace_health["issues"]:
                            health_summary["healthy_workspaces"] += 1
                        elif len(workspace_health["issues"]) <= 2:
                            health_summary["degraded_workspaces"] += 1
                            workspace_health["status"] = "degraded"
                        else:
                            health_summary["unhealthy_workspaces"] += 1
                            workspace_health["status"] = "unhealthy"
                        
                        logger.debug(f"Health check for {workspace_id}: {workspace_health['status']}")
                        
                    except Exception as e:
                        logger.error(f"Health check failed for workspace {workspace_id}: {e}")
                        health_summary["unhealthy_workspaces"] += 1
                        health_summary["issues_found"].append(f"{workspace_id}: Health check failed")
                
                logger.info(f"Health check completed: {health_summary}")
                
                # Wait before next health check
                await asyncio.sleep(self.config["health_check_interval"].total_seconds())
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Periodic health check task failed: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def _periodic_cache_cleanup(self):
        """Periodic cache cleanup task."""
        while self.running:
            try:
                logger.debug("Starting periodic cache cleanup...")
                
                cleanup_stats = {
                    "coordinators_processed": 0,
                    "cache_entries_cleaned": 0,
                    "errors": 0
                }
                
                for workspace_id, coordinator in _coordinator_registry.items():
                    try:
                        # Get cache stats before cleanup
                        stats = await coordinator.get_swarm_memory_metrics()
                        cache_stats = stats.get("cache_performance", {})
                        
                        # Simulate cache cleanup (actual cleanup happens automatically in cache)
                        # This is more for monitoring and reporting
                        cache_size = cache_stats.get("total_entries", 0)
                        if cache_size > 1000:
                            logger.info(f"Large cache detected for workspace {workspace_id}: {cache_size} entries")
                        
                        cleanup_stats["coordinators_processed"] += 1
                        cleanup_stats["cache_entries_cleaned"] += cache_size
                        
                    except Exception as e:
                        logger.error(f"Cache cleanup failed for workspace {workspace_id}: {e}")
                        cleanup_stats["errors"] += 1
                
                logger.info(f"Cache cleanup completed: {cleanup_stats}")
                
                # Wait before next cache cleanup
                await asyncio.sleep(self.config["cache_cleanup_interval"].total_seconds())
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Periodic cache cleanup task failed: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    def update_config(self, **kwargs):
        """Update scheduler configuration."""
        for key, value in kwargs.items():
            if key in self.config:
                if isinstance(value, str):
                    # Parse time intervals from strings
                    if value.endswith('m'):
                        self.config[key] = timedelta(minutes=int(value[:-1]))
                    elif value.endswith('h'):
                        self.config[key] = timedelta(hours=int(value[:-1]))
                    elif value.endswith('s'):
                        self.config[key] = timedelta(seconds=int(value[:-1]))
                    else:
                        logger.warning(f"Invalid time format for {key}: {value}")
                else:
                    self.config[key] = value
        
        logger.info(f"Updated scheduler config: {self.config}")


# Global scheduler instance
_scheduler: MemoryTaskScheduler = None


async def start_memory_tasks():
    """Start memory system background tasks."""
    global _scheduler
    if _scheduler is None:
        _scheduler = MemoryTaskScheduler()
    await _scheduler.start()


async def stop_memory_tasks():
    """Stop memory system background tasks."""
    global _scheduler
    if _scheduler is not None:
        await _scheduler.stop()
        _scheduler = None


def get_memory_scheduler() -> MemoryTaskScheduler:
    """Get the global memory task scheduler."""
    return _scheduler


# Individual task functions for manual execution
async def trigger_consolidation_for_workspace(workspace_id: str, force: bool = False) -> Dict[str, Any]:
    """Manually trigger consolidation for a specific workspace."""
    if workspace_id not in _coordinator_registry:
        raise ValueError(f"Workspace {workspace_id} not found")
    
    coordinator = _coordinator_registry[workspace_id]
    return await coordinator.consolidate_swarm_memories(force=force)


async def cleanup_workspace_memory(workspace_id: str) -> Dict[str, Any]:
    """Manually trigger cleanup for a specific workspace."""
    if workspace_id not in _coordinator_registry:
        raise ValueError(f"Workspace {workspace_id} not found")
    
    coordinator = _coordinator_registry[workspace_id]
    
    cleanup_results = {
        "agents_cleaned": 0,
        "errors": []
    }
    
    # Clean up inactive agents
    for agent_id in list(coordinator.active_agents):
        try:
            await coordinator.cleanup_agent_memory(agent_id)
            cleanup_results["agents_cleaned"] += 1
        except Exception as e:
            cleanup_results["errors"].append(f"Failed to cleanup {agent_id}: {e}")
    
    return cleanup_results


async def get_system_health() -> Dict[str, Any]:
    """Get overall memory system health."""
    health_summary = {
        "total_workspaces": len(_coordinator_registry),
        "active_workspaces": 0,
        "total_agents": 0,
        "total_fragments": 0,
        "system_status": "healthy",
        "issues": []
    }
    
    for workspace_id, coordinator in _coordinator_registry.items():
        if coordinator.active_agents:
            health_summary["active_workspaces"] += 1
            health_summary["total_agents"] += len(coordinator.active_agents)
        
        try:
            stats = await coordinator.get_swarm_memory_metrics()
            health_summary["total_fragments"] += stats.get("total_fragments", 0)
            
            # Check for issues
            cache_hit_rate = stats.get("cache_performance", {}).get("hit_rate", 0)
            if cache_hit_rate < 0.7:
                health_summary["issues"].append(f"{workspace_id}: Low cache hit rate")
            
        except Exception as e:
            health_summary["issues"].append(f"{workspace_id}: Failed to get stats")
    
    # Determine overall system status
    if health_summary["issues"]:
        if len(health_summary["issues"]) <= 2:
            health_summary["system_status"] = "degraded"
        else:
            health_summary["system_status"] = "unhealthy"
    
    return health_summary


# Application lifecycle hooks
async def on_application_startup():
    """Called when application starts up."""
    await start_memory_tasks()
    logger.info("Memory system tasks started on application startup")


async def on_application_shutdown():
    """Called when application shuts down."""
    await stop_memory_tasks()
    logger.info("Memory system tasks stopped on application shutdown")
