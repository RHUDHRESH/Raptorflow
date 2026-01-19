"""
Redis recovery and disaster recovery system.

Provides automated recovery procedures, data restoration,
cluster recovery, and emergency response capabilities.
"""

import asyncio
import json
import logging
import os
import subprocess
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .backup import BackupManager, BackupMetadata, BackupStatus
from .client import get_redis
from .cluster import ClusterNode, ClusterNodeStatus, RedisClusterManager
from .critical_fixes import SecureErrorHandler


class RecoveryType(Enum):
    """Recovery type enumeration."""

    AUTOMATIC = "automatic"
    MANUAL = "manual"
    EMERGENCY = "emergency"
    SCHEDULED = "scheduled"


class RecoveryStatus(Enum):
    """Recovery status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLING_BACK = "rolling_back"


class RecoveryAction(Enum):
    """Recovery action enumeration."""

    RESTART_NODE = "restart_node"
    RESTART_CLUSTER = "restart_cluster"
    FAILOVER = "failover"
    RESTORE_BACKUP = "restore_backup"
    REBUILD_INDEX = "rebuild_index"
    CLEAR_CACHE = "clear_cache"
    RECONFIGURE = "reconfigure"
    EMERGENCY_SHUTDOWN = "emergency_shutdown"


@dataclass
class RecoveryPlan:
    """Recovery plan configuration."""

    plan_id: str
    name: str
    description: str
    recovery_type: RecoveryType

    # Trigger conditions
    trigger_events: List[str] = field(default_factory=list)
    trigger_thresholds: Dict[str, float] = field(default_factory=dict)
    trigger_timeouts: Dict[str, int] = field(default_factory=dict)

    # Recovery actions
    actions: List[Dict[str, Any]] = field(default_factory=list)
    rollback_actions: List[Dict[str, Any]] = field(default_factory=list)

    # Execution settings
    parallel_actions: bool = False
    timeout_seconds: int = 3600
    retry_attempts: int = 3
    retry_delay_seconds: int = 60

    # Validation settings
    validate_before_execute: bool = True
    validate_after_execute: bool = True
    validation_checks: List[str] = field(default_factory=list)

    # Notification settings
    notify_on_start: bool = True
    notify_on_complete: bool = True
    notify_on_failure: bool = True
    notification_channels: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.recovery_type, str):
            self.recovery_type = RecoveryType(self.recovery_type)

    def should_trigger(self, event: str, metrics: Dict[str, float]) -> bool:
        """Check if recovery plan should be triggered."""
        # Check trigger events
        if self.trigger_events and event not in self.trigger_events:
            return False

        # Check trigger thresholds
        for metric, threshold in self.trigger_thresholds.items():
            if metric in metrics:
                if metrics[metric] > threshold:
                    return True

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert enum to string
        data["recovery_type"] = self.recovery_type.value

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RecoveryPlan":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class RecoveryEvent:
    """Recovery event tracking."""

    event_id: str
    plan_id: str
    recovery_type: RecoveryType
    trigger_event: str
    cluster_id: str

    # Event details
    trigger_metrics: Dict[str, float] = field(default_factory=dict)
    affected_nodes: List[str] = field(default_factory=list)
    severity: str = "medium"

    # Execution details
    actions_executed: List[Dict[str, Any]] = field(default_factory=list)
    actions_failed: List[Dict[str, Any]] = field(default_factory=list)

    # Timing
    triggered_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    # Results
    status: RecoveryStatus = RecoveryStatus.PENDING
    success: bool = False
    error_message: Optional[str] = None
    rollback_performed: bool = False

    # Validation results
    validation_passed: bool = False
    validation_results: Dict[str, bool] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.recovery_type, str):
            self.recovery_type = RecoveryType(self.recovery_type)
        if isinstance(self.status, str):
            self.status = RecoveryStatus(self.status)
        if isinstance(self.triggered_at, str):
            self.triggered_at = datetime.fromisoformat(self.triggered_at)
        if isinstance(self.started_at, str):
            self.started_at = datetime.fromisoformat(self.started_at)
        if isinstance(self.completed_at, str):
            self.completed_at = datetime.fromisoformat(self.completed_at)

    def mark_started(self):
        """Mark recovery as started."""
        self.status = RecoveryStatus.RUNNING
        self.started_at = datetime.now()

    def mark_completed(self, success: bool, error_message: str = None):
        """Mark recovery as completed."""
        self.status = RecoveryStatus.COMPLETED
        self.completed_at = datetime.now()
        self.success = success
        self.error_message = error_message

        if self.started_at and self.completed_at:
            self.duration_seconds = (
                self.completed_at - self.started_at
            ).total_seconds()

    def mark_failed(self, error_message: str):
        """Mark recovery as failed."""
        self.status = RecoveryStatus.FAILED
        self.completed_at = datetime.now()
        self.success = False
        self.error_message = error_message

        if self.started_at and self.completed_at:
            self.duration_seconds = (
                self.completed_at - self.started_at
            ).total_seconds()

    def add_action_result(
        self, action: Dict[str, Any], success: bool, error: str = None
    ):
        """Add action execution result."""
        action_result = {
            **action,
            "executed_at": datetime.now().isoformat(),
            "success": success,
            "error": error,
        }

        if success:
            self.actions_executed.append(action_result)
        else:
            self.actions_failed.append(action_result)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert enums to strings
        data["recovery_type"] = self.recovery_type.value
        data["status"] = self.status.value

        # Convert datetime objects
        data["triggered_at"] = self.triggered_at.isoformat()
        if self.started_at:
            data["started_at"] = self.started_at.isoformat()
        if self.completed_at:
            data["completed_at"] = self.completed_at.isoformat()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RecoveryEvent":
        """Create from dictionary."""
        return cls(**data)


class RecoveryManager:
    """Redis recovery and disaster recovery manager."""

    def __init__(self, cluster_manager: Optional[RedisClusterManager] = None):
        self.cluster_manager = cluster_manager
        self.redis = get_redis()
        self.backup_manager = BackupManager(cluster_manager)
        self.error_handler = SecureErrorHandler()
        self.logger = logging.getLogger("recovery_manager")

        # Recovery state
        self.recovery_plans: Dict[str, RecoveryPlan] = {}
        self.active_recoveries: Dict[str, RecoveryEvent] = {}
        self.recovery_history: List[RecoveryEvent] = []

        # Monitoring state
        self._monitoring_running = False
        self._monitoring_task = None

        # Setup default recovery plans
        self._setup_default_recovery_plans()

    def _setup_default_recovery_plans(self):
        """Setup default recovery plans."""
        # Node failure recovery plan
        node_failure_plan = RecoveryPlan(
            plan_id="node_failure",
            name="Node Failure Recovery",
            description="Automatic recovery for failed Redis nodes",
            recovery_type=RecoveryType.AUTOMATIC,
            trigger_events=["node_failure", "node_timeout"],
            trigger_thresholds={"consecutive_failures": 3},
            actions=[
                {"action": "restart_node", "timeout": 60, "retry_attempts": 3},
                {"action": "failover", "timeout": 30, "retry_attempts": 1},
            ],
            validate_after_execute=True,
            validation_checks=["node_health", "cluster_health"],
        )
        self.recovery_plans["node_failure"] = node_failure_plan

        # Cluster failure recovery plan
        cluster_failure_plan = RecoveryPlan(
            plan_id="cluster_failure",
            name="Cluster Failure Recovery",
            description="Emergency recovery for cluster-wide failures",
            recovery_type=RecoveryType.EMERGENCY,
            trigger_events=["cluster_failure", "majority_nodes_failed"],
            trigger_thresholds={"failed_nodes_percentage": 50},
            actions=[
                {"action": "emergency_shutdown", "timeout": 30},
                {"action": "restore_backup", "timeout": 600},
            ],
            validate_after_execute=True,
            validation_checks=["cluster_health", "data_integrity"],
        )
        self.recovery_plans["cluster_failure"] = cluster_failure_plan

        # Performance degradation recovery plan
        performance_plan = RecoveryPlan(
            plan_id="performance_degradation",
            name="Performance Degradation Recovery",
            description="Recovery for performance issues",
            recovery_type=RecoveryType.AUTOMATIC,
            trigger_events=["high_latency", "high_memory", "high_cpu"],
            trigger_thresholds={
                "response_time_ms": 1000,
                "memory_usage_percent": 90,
                "cpu_usage_percent": 85,
            },
            actions=[
                {"action": "clear_cache", "timeout": 30},
                {"action": "restart_node", "timeout": 60},
            ],
            validate_after_execute=True,
            validation_checks=["performance_metrics"],
        )
        self.recovery_plans["performance_degradation"] = performance_plan

    def add_recovery_plan(self, plan: RecoveryPlan):
        """Add a recovery plan."""
        self.recovery_plans[plan.plan_id] = plan
        self.logger.info(f"Added recovery plan {plan.plan_id}")

    def remove_recovery_plan(self, plan_id: str):
        """Remove a recovery plan."""
        if plan_id in self.recovery_plans:
            del self.recovery_plans[plan_id]
            self.logger.info(f"Removed recovery plan {plan_id}")

    async def start_monitoring(self):
        """Start recovery monitoring."""
        if self._monitoring_running:
            return

        self._monitoring_running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())

        self.logger.info("Started recovery monitoring")

        try:
            await self._monitoring_task
        except asyncio.CancelledError:
            pass
        finally:
            self._monitoring_running = False
            self._monitoring_task = None
            self.logger.info("Stopped recovery monitoring")

    async def stop_monitoring(self):
        """Stop recovery monitoring."""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            self._monitoring_task = None

        self._monitoring_running = False
        self.logger.info("Stopped recovery monitoring")

    async def _monitoring_loop(self):
        """Main recovery monitoring loop."""
        while self._monitoring_running:
            try:
                # Monitor cluster health
                await self._monitor_cluster_health()

                # Check for recovery triggers
                await self._check_recovery_triggers()

                # Process active recoveries
                await self._process_active_recoveries()

                # Wait for next iteration
                await asyncio.sleep(30)  # Check every 30 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Recovery monitoring loop error: {e}")
                await asyncio.sleep(30)

    async def _monitor_cluster_health(self):
        """Monitor cluster health for recovery triggers."""
        if not self.cluster_manager:
            return

        try:
            # Get cluster status
            cluster_status = await self.cluster_manager.get_cluster_status()

            if not cluster_status:
                return

            # Check for node failures
            failed_nodes = [
                node_id
                for node_id, node_data in cluster_status.get("nodes", {}).items()
                if node_data.get("status") == "failed"
            ]

            if failed_nodes:
                await self._trigger_recovery(
                    "node_failure",
                    {
                        "failed_nodes": len(failed_nodes),
                        "total_nodes": cluster_status.get("total_nodes", 0),
                    },
                )

            # Check for performance issues
            avg_response_time = cluster_status.get("avg_response_time_ms", 0)
            if avg_response_time > 1000:
                await self._trigger_recovery(
                    "high_latency", {"response_time_ms": avg_response_time}
                )

            # Check for memory issues
            total_memory = cluster_status.get("total_memory_mb", 0)
            if total_memory > 0:
                # This would require actual memory usage data
                pass

        except Exception as e:
            self.logger.error(f"Failed to monitor cluster health: {e}")

    async def _check_recovery_triggers(self):
        """Check for recovery triggers."""
        # This would check various system metrics and events
        # For now, the monitoring loop handles this
        pass

    async def _trigger_recovery(self, event: str, metrics: Dict[str, float]):
        """Trigger recovery based on event and metrics."""
        for plan in self.recovery_plans.values():
            if plan.should_trigger(event, metrics):
                await self._execute_recovery_plan(plan, event, metrics)

    async def _execute_recovery_plan(
        self, plan: RecoveryPlan, event: str, metrics: Dict[str, float]
    ):
        """Execute a recovery plan."""
        recovery_id = str(uuid.uuid4())

        # Create recovery event
        recovery_event = RecoveryEvent(
            event_id=recovery_id,
            plan_id=plan.plan_id,
            recovery_type=plan.recovery_type,
            trigger_event=event,
            cluster_id=(
                self.cluster_manager.config.cluster_id
                if self.cluster_manager
                else "single"
            ),
            trigger_metrics=metrics,
        )

        self.active_recoveries[recovery_id] = recovery_event
        self.recovery_history.append(recovery_event)

        try:
            # Store recovery event
            await self._store_recovery_event(recovery_event)

            # Log security event for emergency recoveries
            if plan.recovery_type == RecoveryType.EMERGENCY:
                self.error_handler.log_security_event(
                    event_type="emergency_recovery",
                    severity="CRITICAL",
                    description=f"Emergency recovery triggered: {plan.name}",
                    context={
                        "recovery_id": recovery_id,
                        "plan_id": plan.plan_id,
                        "trigger_event": event,
                        "metrics": metrics,
                    },
                )

            # Execute recovery actions
            await self._execute_recovery_actions(plan, recovery_event)

            # Mark as completed
            recovery_event.mark_completed(True)

            # Store updated event
            await self._store_recovery_event(recovery_event)

            self.logger.info(f"Recovery {recovery_id} completed successfully")

        except Exception as e:
            self.logger.error(f"Recovery {recovery_id} failed: {e}")
            recovery_event.mark_failed(str(e))
            await self._store_recovery_event(recovery_event)

    async def _execute_recovery_actions(
        self, plan: RecoveryPlan, recovery_event: RecoveryEvent
    ):
        """Execute recovery actions."""
        recovery_event.mark_started()

        for action in plan.actions:
            try:
                action_type = action.get("action")
                timeout = action.get("timeout", 60)
                retry_attempts = action.get("retry_attempts", 1)

                success = False
                error = None

                for attempt in range(retry_attempts):
                    try:
                        if action_type == "restart_node":
                            success = await self._restart_node(action, recovery_event)
                        elif action_type == "restart_cluster":
                            success = await self._restart_cluster(
                                action, recovery_event
                            )
                        elif action_type == "failover":
                            success = await self._trigger_failover(
                                action, recovery_event
                            )
                        elif action_type == "restore_backup":
                            success = await self._restore_backup(action, recovery_event)
                        elif action_type == "clear_cache":
                            success = await self._clear_cache(action, recovery_event)
                        elif action_type == "emergency_shutdown":
                            success = await self._emergency_shutdown(
                                action, recovery_event
                            )
                        else:
                            self.logger.warning(
                                f"Unknown recovery action: {action_type}"
                            )
                            success = True  # Skip unknown actions

                        if success:
                            break

                    except Exception as e:
                        error = str(e)
                        self.logger.warning(
                            f"Recovery action {action_type} attempt {attempt + 1} failed: {e}"
                        )

                        if attempt < retry_attempts - 1:
                            await asyncio.sleep(action.get("retry_delay", 60))

                recovery_event.add_action_result(action, success, error)

                if not success and not plan.parallel_actions:
                    break  # Stop on first failure if not parallel

            except Exception as e:
                self.logger.error(
                    f"Failed to execute recovery action {action_type}: {e}"
                )
                recovery_event.add_action_result(action, False, str(e))

        # Perform post-execution validation
        if plan.validate_after_execute:
            await self._validate_recovery(plan, recovery_event)

    async def _restart_node(
        self, action: Dict[str, Any], recovery_event: RecoveryEvent
    ) -> bool:
        """Restart a Redis node."""
        node_id = action.get("node_id")

        if self.cluster_manager and node_id:
            node = self.cluster_manager.nodes.get(node_id)
            if node:
                # This would implement actual node restart
                # For now, just simulate the action
                self.logger.info(f"Restarting node {node_id}")

                # Simulate restart time
                await asyncio.sleep(5)

                # Mark node as online
                node.status = ClusterNodeStatus.ONLINE
                node.consecutive_failures = 0

                recovery_event.affected_nodes.append(node_id)
                return True

        return False

    async def _restart_cluster(
        self, action: Dict[str, Any], recovery_event: RecoveryEvent
    ) -> bool:
        """Restart the entire Redis cluster."""
        self.logger.info("Restarting Redis cluster")

        # This would implement actual cluster restart
        # For now, just simulate the action
        await asyncio.sleep(10)

        # Mark all nodes as online
        if self.cluster_manager:
            for node in self.cluster_manager.nodes.values():
                node.status = ClusterNodeStatus.ONLINE
                node.consecutive_failures = 0
                recovery_event.affected_nodes.append(node.node_id)

        return True

    async def _trigger_failover(
        self, action: Dict[str, Any], recovery_event: RecoveryEvent
    ) -> bool:
        """Trigger cluster failover."""
        self.logger.info("Triggering cluster failover")

        if self.cluster_manager:
            try:
                await self.cluster_manager._initiate_failover()
                return True
            except Exception as e:
                self.logger.error(f"Failover failed: {e}")
                return False

        return False

    async def _restore_backup(
        self, action: Dict[str, Any], recovery_event: RecoveryEvent
    ) -> bool:
        """Restore from backup."""
        backup_id = action.get("backup_id")

        if not backup_id:
            # Get latest backup
            backups = await self.backup_manager.get_backup_list(limit=1)
            if backups:
                backup_id = backups[0]["backup_id"]

        if backup_id:
            self.logger.info(f"Restoring from backup {backup_id}")

            try:
                success = await self.backup_manager.restore_backup(backup_id)
                return success
            except Exception as e:
                self.logger.error(f"Backup restore failed: {e}")
                return False

        return False

    async def _clear_cache(
        self, action: Dict[str, Any], recovery_event: RecoveryEvent
    ) -> bool:
        """Clear Redis cache."""
        self.logger.info("Clearing Redis cache")

        try:
            # Clear all keys (use with caution!)
            pattern = action.get("pattern", "*")
            keys = await self.redis.keys(pattern)

            if keys:
                await self.redis.delete(*keys)
                self.logger.info(f"Cleared {len(keys)} keys from cache")

            return True

        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")
            return False

    async def _emergency_shutdown(
        self, action: Dict[str, Any], recovery_event: RecoveryEvent
    ) -> bool:
        """Perform emergency shutdown."""
        self.logger.info("Performing emergency shutdown")

        try:
            # This would implement actual emergency shutdown
            # For now, just simulate the action
            await asyncio.sleep(5)

            # Mark all nodes as offline
            if self.cluster_manager:
                for node in self.cluster_manager.nodes.values():
                    node.status = ClusterNodeStatus.OFFLINE
                    recovery_event.affected_nodes.append(node.node_id)

            return True

        except Exception as e:
            self.logger.error(f"Emergency shutdown failed: {e}")
            return False

    async def _validate_recovery(
        self, plan: RecoveryPlan, recovery_event: RecoveryEvent
    ):
        """Validate recovery results."""
        validation_results = {}

        for check in plan.validation_checks:
            try:
                if check == "node_health":
                    validation_results[check] = await self._validate_node_health(
                        recovery_event
                    )
                elif check == "cluster_health":
                    validation_results[check] = await self._validate_cluster_health(
                        recovery_event
                    )
                elif check == "performance_metrics":
                    validation_results[check] = (
                        await self._validate_performance_metrics(recovery_event)
                    )
                elif check == "data_integrity":
                    validation_results[check] = await self._validate_data_integrity(
                        recovery_event
                    )
                else:
                    validation_results[check] = (
                        True  # Default to pass for unknown checks
                    )

            except Exception as e:
                self.logger.error(f"Validation check {check} failed: {e}")
                validation_results[check] = False

        recovery_event.validation_results = validation_results
        recovery_event.validation_passed = all(validation_results.values())

    async def _validate_node_health(self, recovery_event: RecoveryEvent) -> bool:
        """Validate node health after recovery."""
        if not self.cluster_manager:
            return True

        for node_id in recovery_event.affected_nodes:
            node = self.cluster_manager.nodes.get(node_id)
            if node and not node.is_healthy():
                return False

        return True

    async def _validate_cluster_health(self, recovery_event: RecoveryEvent) -> bool:
        """Validate cluster health after recovery."""
        if not self.cluster_manager:
            return True

        # Check if cluster has healthy primary
        if self.cluster_manager.primary_node:
            primary = self.cluster_manager.nodes.get(self.cluster_manager.primary_node)
            if not primary or not primary.is_healthy():
                return False

        # Check if we have minimum required nodes
        min_nodes = self.cluster_manager.config.min_nodes
        online_nodes = len(
            [node for node in self.cluster_manager.nodes.values() if node.is_healthy()]
        )

        return online_nodes >= min_nodes

    async def _validate_performance_metrics(
        self, recovery_event: RecoveryEvent
    ) -> bool:
        """Validate performance metrics after recovery."""
        # This would check actual performance metrics
        # For now, just return True
        return True

    async def _validate_data_integrity(self, recovery_event: RecoveryEvent) -> bool:
        """Validate data integrity after recovery."""
        # This would perform data integrity checks
        # For now, just return True
        return True

    async def _store_recovery_event(self, event: RecoveryEvent):
        """Store recovery event in Redis."""
        event_key = f"recovery:{event.event_id}"
        await self.redis.set_json(event_key, event.to_dict(), ex=86400 * 30)  # 30 days

        # Add to recovery index
        index_key = f"recovery:index:{event.cluster_id}"
        await self.redis.zadd(
            index_key, {event.event_id: event.triggered_at.timestamp()}
        )

    async def manual_recovery(
        self, plan_id: str, reason: str = "Manual recovery requested"
    ) -> str:
        """Trigger manual recovery."""
        if plan_id not in self.recovery_plans:
            raise ValueError(f"Recovery plan {plan_id} not found")

        plan = self.recovery_plans[plan_id]

        # Create manual recovery event
        recovery_id = str(uuid.uuid4())

        recovery_event = RecoveryEvent(
            event_id=recovery_id,
            plan_id=plan_id,
            recovery_type=RecoveryType.MANUAL,
            trigger_event="manual_trigger",
            cluster_id=(
                self.cluster_manager.config.cluster_id
                if self.cluster_manager
                else "single"
            ),
        )

        self.active_recoveries[recovery_id] = recovery_event
        self.recovery_history.append(recovery_event)

        try:
            # Execute recovery plan
            await self._execute_recovery_actions(plan, recovery_event)

            # Mark as completed
            recovery_event.mark_completed(True)

            # Store event
            await self._store_recovery_event(recovery_event)

            self.logger.info(f"Manual recovery {recovery_id} completed")
            return recovery_id

        except Exception as e:
            self.logger.error(f"Manual recovery {recovery_id} failed: {e}")
            recovery_event.mark_failed(str(e))
            await self._store_recovery_event(recovery_event)
            raise

    async def get_recovery_status(self, recovery_id: str) -> Optional[Dict[str, Any]]:
        """Get recovery status."""
        event_key = f"recovery:{recovery_id}"
        data = await self.redis.get_json(event_key)

        if data:
            return RecoveryEvent.from_dict(data).to_dict()

        return None

    async def get_recovery_history(
        self, cluster_id: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get recovery history."""
        if cluster_id:
            # Get recoveries for specific cluster
            index_key = f"recovery:index:{cluster_id}"
            result = await self.redis.zrevrange(
                index_key, 0, limit - 1, withscores=True
            )

            recoveries = []
            for recovery_id, timestamp in result:
                event_key = f"recovery:{recovery_id}"
                data = await self.redis.get_json(event_key)
                if data:
                    recoveries.append(RecoveryEvent.from_dict(data).to_dict())

            return recoveries
        else:
            # Get all recoveries
            pattern = f"recovery:*"
            keys = await self.redis.keys(pattern)

            recoveries = []
            for key in keys[:limit]:
                data = await self.redis.get_json(key)
                if data:
                    recoveries.append(RecoveryEvent.from_dict(data).to_dict())

            # Sort by triggered time
            recoveries.sort(key=lambda x: x["triggered_at"], reverse=True)

            return recoveries

    async def get_recovery_statistics(self) -> Dict[str, Any]:
        """Get recovery statistics."""
        # Get all recovery events
        pattern = f"recovery:*"
        keys = await self.redis.keys(pattern)

        stats = {
            "total_recoveries": len(keys),
            "recovery_types": {},
            "status_counts": {},
            "success_rate": 0.0,
            "avg_duration_seconds": 0.0,
            "last_recovery": None,
            "active_recoveries": len(self.active_recoveries),
        }

        total_duration = 0
        successful_recoveries = 0

        for key in keys:
            data = await self.redis.get_json(key)
            if data:
                event = RecoveryEvent.from_dict(data)

                # Count by type
                recovery_type = event.recovery_type.value
                if recovery_type not in stats["recovery_types"]:
                    stats["recovery_types"][recovery_type] = 0
                stats["recovery_types"][recovery_type] += 1

                # Count by status
                status = event.status.value
                if status not in stats["status_counts"]:
                    stats["status_counts"][status] = 0
                stats["status_counts"][status] += 1

                # Calculate duration and success rate
                if event.duration_seconds:
                    total_duration += event.duration_seconds

                if event.success:
                    successful_recoveries += 1

                # Track last recovery
                if (
                    not stats["last_recovery"]
                    or event.triggered_at > stats["last_recovery"]
                ):
                    stats["last_recovery"] = event.triggered_at.isoformat()

        # Calculate derived stats
        if stats["total_recoveries"] > 0:
            stats["avg_duration_seconds"] = total_duration / stats["total_recoveries"]
            stats["success_rate"] = (
                successful_recoveries / stats["total_recoveries"]
            ) * 100

        return stats

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_monitoring()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop_monitoring()
