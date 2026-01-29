"""
Resource quota management and enforcement for Raptorflow backend.
Provides quota tracking, enforcement, and alerting for resource usage.
"""

import asyncio
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union

from metrics_collector import get_metrics_collector
from resources import ResourceQuota, ResourceType, get_resource_manager

logger = logging.getLogger(__name__)


class QuotaType(Enum):
    """Types of quotas that can be enforced."""

    HARD = "hard"  # Cannot be exceeded
    SOFT = "soft"  # Can be exceeded with warnings
    BURST = "burst"  # Temporary allowance for bursts
    DYNAMIC = "dynamic"  # Adjusts based on usage patterns


class QuotaPeriod(Enum):
    """Time periods for quota enforcement."""

    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    FOREVER = "forever"


class QuotaAction(Enum):
    """Actions to take when quotas are exceeded."""

    BLOCK = "block"  # Block the operation
    WARN = "warn"  # Allow with warning
    THROTTLE = "throttle"  # Slow down the operation
    QUEUE = "queue"  # Queue for later execution
    ESCALATE = "escalate"  # Escalate to admin


@dataclass
class QuotaDefinition:
    """Definition of a resource quota."""

    quota_id: str
    name: str
    description: str
    resource_type: ResourceType
    quota_type: QuotaType
    period: QuotaPeriod
    limit: Union[int, float]
    burst_limit: Optional[Union[int, float]] = None
    action: QuotaAction = QuotaAction.WARN
    workspace_id: Optional[str] = None
    user_id: Optional[str] = None
    enabled: bool = True
    tags: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "quota_id": self.quota_id,
            "name": self.name,
            "description": self.description,
            "resource_type": self.resource_type.value,
            "quota_type": self.quota_type.value,
            "period": self.period.value,
            "limit": self.limit,
            "burst_limit": self.burst_limit,
            "action": self.action.value,
            "workspace_id": self.workspace_id,
            "user_id": self.user_id,
            "enabled": self.enabled,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class QuotaUsage:
    """Current usage of a quota."""

    quota_id: str
    current_usage: Union[int, float]
    period_start: datetime
    last_updated: datetime
    burst_usage: Union[int, float] = 0
    violations: int = 0
    warnings: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "quota_id": self.quota_id,
            "current_usage": self.current_usage,
            "period_start": self.period_start.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "burst_usage": self.burst_usage,
            "violations": self.violations,
            "warnings": self.warnings,
        }


@dataclass
class QuotaViolation:
    """Record of a quota violation."""

    violation_id: str
    quota_id: str
    resource_type: ResourceType
    violation_time: datetime
    current_usage: Union[int, float]
    limit: Union[int, float]
    exceeded_by: Union[int, float]
    action_taken: QuotaAction
    user_id: Optional[str] = None
    workspace_id: Optional[str] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "violation_id": self.violation_id,
            "quota_id": self.quota_id,
            "resource_type": self.resource_type.value,
            "violation_time": self.violation_time.isoformat(),
            "current_usage": self.current_usage,
            "limit": self.limit,
            "exceeded_by": self.exceeded_by,
            "action_taken": self.action_taken.value,
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }


@dataclass
class QuotaCheckResult:
    """Result of a quota check."""

    allowed: bool
    quota_id: str
    current_usage: Union[int, float]
    limit: Union[int, float]
    remaining: Union[int, float]
    action: QuotaAction
    message: str
    is_warning: bool = False
    is_violation: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "allowed": self.allowed,
            "quota_id": self.quota_id,
            "current_usage": self.current_usage,
            "limit": self.limit,
            "remaining": self.remaining,
            "action": self.action.value,
            "message": self.message,
            "is_warning": self.is_warning,
            "is_violation": self.is_violation,
        }


class QuotaManager:
    """Manages resource quotas with enforcement and monitoring."""

    def __init__(self, check_interval: int = 30):  # 30 seconds
        self.check_interval = check_interval

        # Quota definitions and usage tracking
        self.quotas: Dict[str, QuotaDefinition] = {}
        self.quota_usage: Dict[str, QuotaUsage] = {}
        self.quota_violations: List[QuotaViolation] = []

        # Usage history for trend analysis
        self.usage_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))

        # Background tasks
        self._background_tasks: Set[asyncio.Task] = set()
        self._running = False

        # Enforcement callbacks
        self.violation_callbacks: List[Callable] = []
        self.warning_callbacks: List[Callable] = []

        # Metrics
        self.quota_metrics = {
            "total_checks": 0,
            "total_violations": 0,
            "total_warnings": 0,
            "blocks_enforced": 0,
            "throttles_enforced": 0,
            "quota_resets": 0,
        }

        # Initialize default quotas
        self._initialize_default_quotas()

        logger.info(f"Quota manager initialized with check interval: {check_interval}s")

    def _initialize_default_quotas(self):
        """Initialize default quota definitions."""
        default_quotas = [
            # Memory quotas
            QuotaDefinition(
                quota_id="memory_per_user",
                name="Memory Usage Per User",
                description="Maximum memory usage per user",
                resource_type=ResourceType.MEMORY,
                quota_type=QuotaType.SOFT,
                period=QuotaPeriod.HOUR,
                limit=1024 * 1024 * 1024,  # 1GB
                burst_limit=1536 * 1024 * 1024,  # 1.5GB burst
                action=QuotaAction.WARN,
            ),
            QuotaDefinition(
                quota_id="memory_per_workspace",
                name="Memory Usage Per Workspace",
                description="Maximum memory usage per workspace",
                resource_type=ResourceType.MEMORY,
                quota_type=QuotaType.HARD,
                period=QuotaPeriod.HOUR,
                limit=4 * 1024 * 1024 * 1024,  # 4GB
                action=QuotaAction.BLOCK,
            ),
            # File handle quotas
            QuotaDefinition(
                quota_id="file_handles_per_user",
                name="File Handles Per User",
                description="Maximum open file handles per user",
                resource_type=ResourceType.FILE_HANDLE,
                quota_type=QuotaType.HARD,
                period=QuotaPeriod.MINUTE,
                limit=100,
                action=QuotaAction.BLOCK,
            ),
            # Database connection quotas
            QuotaDefinition(
                quota_id="db_connections_per_workspace",
                name="Database Connections Per Workspace",
                description="Maximum database connections per workspace",
                resource_type=ResourceType.DATABASE_CONNECTION,
                quota_type=QuotaType.SOFT,
                period=QuotaPeriod.SECOND,
                limit=10,
                burst_limit=20,
                action=QuotaAction.THROTTLE,
            ),
            # Async task quotas
            QuotaDefinition(
                quota_id="async_tasks_per_user",
                name="Async Tasks Per User",
                description="Maximum concurrent async tasks per user",
                resource_type=ResourceType.ASYNC_TASK,
                quota_type=QuotaType.HARD,
                period=QuotaPeriod.SECOND,
                limit=50,
                action=QuotaAction.BLOCK,
            ),
            # Network connection quotas
            QuotaDefinition(
                quota_id="network_connections_per_workspace",
                name="Network Connections Per Workspace",
                description="Maximum network connections per workspace",
                resource_type=ResourceType.NETWORK_CONNECTION,
                quota_type=QuotaType.SOFT,
                period=QuotaPeriod.MINUTE,
                limit=100,
                action=QuotaAction.WARN,
            ),
        ]

        for quota in default_quotas:
            self.quotas[quota.quota_id] = quota
            self.quota_usage[quota.quota_id] = QuotaUsage(
                quota_id=quota.quota_id,
                current_usage=0,
                period_start=datetime.now(),
                last_updated=datetime.now(),
            )

    async def start(self):
        """Start the quota manager."""
        if self._running:
            return

        self._running = True

        # Start background tasks
        self._background_tasks.add(asyncio.create_task(self._quota_reset_loop()))
        self._background_tasks.add(asyncio.create_task(self._usage_monitoring_loop()))

        logger.info("Quota manager started")

    async def stop(self):
        """Stop the quota manager."""
        self._running = False

        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()

        await asyncio.gather(*self._background_tasks, return_exceptions=True)
        self._background_tasks.clear()

        logger.info("Quota manager stopped")

    def add_quota(self, quota: QuotaDefinition) -> bool:
        """Add a new quota definition."""
        try:
            self.quotas[quota.quota_id] = quota

            # Initialize usage tracking
            if quota.quota_id not in self.quota_usage:
                self.quota_usage[quota.quota_id] = QuotaUsage(
                    quota_id=quota.quota_id,
                    current_usage=0,
                    period_start=datetime.now(),
                    last_updated=datetime.now(),
                )

            logger.info(f"Added quota: {quota.quota_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to add quota {quota.quota_id}: {e}")
            return False

    def remove_quota(self, quota_id: str) -> bool:
        """Remove a quota definition."""
        if quota_id in self.quotas:
            del self.quotas[quota_id]
            if quota_id in self.quota_usage:
                del self.quota_usage[quota_id]

            logger.info(f"Removed quota: {quota_id}")
            return True
        return False

    def update_quota(self, quota_id: str, **updates) -> bool:
        """Update a quota definition."""
        if quota_id not in self.quotas:
            return False

        quota = self.quotas[quota_id]

        for key, value in updates.items():
            if hasattr(quota, key):
                setattr(quota, key, value)

        quota.updated_at = datetime.now()

        logger.info(f"Updated quota: {quota_id}")
        return True

    async def check_quota(
        self,
        resource_type: ResourceType,
        usage_amount: Union[int, float] = 1,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> List[QuotaCheckResult]:
        """Check if resource usage is within quotas."""
        results = []

        try:
            # Find applicable quotas
            applicable_quotas = self._find_applicable_quotas(
                resource_type, user_id, workspace_id
            )

            for quota in applicable_quotas:
                if not quota.enabled:
                    continue

                # Get current usage
                usage = self.quota_usage.get(quota.quota_id)
                if not usage:
                    usage = QuotaUsage(
                        quota_id=quota.quota_id,
                        current_usage=0,
                        period_start=datetime.now(),
                        last_updated=datetime.now(),
                    )
                    self.quota_usage[quota.quota_id] = usage

                # Check if quota period needs reset
                if self._should_reset_quota(quota, usage):
                    self._reset_quota_usage(quota.quota_id)
                    usage = self.quota_usage[quota.quota_id]

                # Calculate new usage
                new_usage = usage.current_usage + usage_amount

                # Determine if this is allowed
                result = self._evaluate_quota_check(
                    quota, usage, new_usage, usage_amount
                )
                results.append(result)

                # Update usage if allowed
                if result.allowed:
                    usage.current_usage = new_usage
                    usage.last_updated = datetime.now()

                    # Update burst usage if applicable
                    if quota.burst_limit and new_usage > quota.limit:
                        usage.burst_usage = new_usage - quota.limit

                # Record metrics
                self.quota_metrics["total_checks"] += 1

                if result.is_violation:
                    self.quota_metrics["total_violations"] += 1
                    await self._handle_violation(quota, result, user_id, workspace_id)

                if result.is_warning:
                    self.quota_metrics["total_warnings"] += 1
                    await self._handle_warning(quota, result, user_id, workspace_id)

            return results

        except Exception as e:
            logger.error(f"Quota check failed: {e}")
            return []

    def _find_applicable_quotas(
        self,
        resource_type: ResourceType,
        user_id: Optional[str],
        workspace_id: Optional[str],
    ) -> List[QuotaDefinition]:
        """Find quotas that apply to the given resource and context."""
        applicable = []

        for quota in self.quotas.values():
            if not quota.enabled:
                continue

            # Check resource type match
            if quota.resource_type != resource_type:
                continue

            # Check scope match
            if quota.user_id and quota.user_id != user_id:
                continue

            if quota.workspace_id and quota.workspace_id != workspace_id:
                continue

            applicable.append(quota)

        return applicable

    def _should_reset_quota(self, quota: QuotaDefinition, usage: QuotaUsage) -> bool:
        """Check if a quota period should be reset."""
        if quota.period == QuotaPeriod.FOREVER:
            return False

        now = datetime.now()
        period_duration = self._get_period_duration(quota.period)

        return (now - usage.period_start) >= period_duration

    def _get_period_duration(self, period: QuotaPeriod) -> timedelta:
        """Get the duration for a quota period."""
        durations = {
            QuotaPeriod.SECOND: timedelta(seconds=1),
            QuotaPeriod.MINUTE: timedelta(minutes=1),
            QuotaPeriod.HOUR: timedelta(hours=1),
            QuotaPeriod.DAY: timedelta(days=1),
            QuotaPeriod.WEEK: timedelta(weeks=1),
            QuotaPeriod.MONTH: timedelta(days=30),
        }
        return durations.get(period, timedelta(hours=1))

    def _reset_quota_usage(self, quota_id: str):
        """Reset quota usage for a new period."""
        if quota_id in self.quota_usage:
            usage = self.quota_usage[quota_id]

            # Store in history
            self.usage_history[quota_id].append(
                {
                    "period_start": usage.period_start,
                    "period_end": datetime.now(),
                    "usage": usage.current_usage,
                    "burst_usage": usage.burst_usage,
                    "violations": usage.violations,
                    "warnings": usage.warnings,
                }
            )

            # Reset usage
            usage.current_usage = 0
            usage.burst_usage = 0
            usage.period_start = datetime.now()
            usage.last_updated = datetime.now()

            self.quota_metrics["quota_resets"] += 1

            logger.debug(f"Reset quota usage for: {quota_id}")

    def _evaluate_quota_check(
        self,
        quota: QuotaDefinition,
        usage: QuotaUsage,
        new_usage: Union[int, float],
        usage_amount: Union[int, float],
    ) -> QuotaCheckResult:
        """Evaluate a quota check and return the result."""
        limit = quota.limit
        remaining = limit - usage.current_usage

        # Check if we're in burst mode
        if quota.burst_limit and new_usage > limit:
            if new_usage <= quota.burst_limit:
                return QuotaCheckResult(
                    allowed=True,
                    quota_id=quota.quota_id,
                    current_usage=usage.current_usage,
                    limit=limit,
                    remaining=remaining,
                    action=quota.action,
                    message=f"Allowed within burst limit: {new_usage}/{quota.burst_limit}",
                    is_warning=True,
                    is_violation=False,
                )
            else:
                # Exceeded burst limit
                exceeded_by = new_usage - quota.burst_limit
                return QuotaCheckResult(
                    allowed=self._is_action_allowed(quota.action),
                    quota_id=quota.quota_id,
                    current_usage=usage.current_usage,
                    limit=quota.burst_limit,
                    remaining=quota.burst_limit - usage.current_usage,
                    action=quota.action,
                    message=f"Exceeded burst limit by {exceeded_by}",
                    is_warning=False,
                    is_violation=True,
                )

        # Normal limit check
        if new_usage > limit:
            exceeded_by = new_usage - limit
            return QuotaCheckResult(
                allowed=self._is_action_allowed(quota.action),
                quota_id=quota.quota_id,
                current_usage=usage.current_usage,
                limit=limit,
                remaining=remaining,
                action=quota.action,
                message=f"Exceeded limit by {exceeded_by}",
                is_warning=quota.quota_type == QuotaType.SOFT,
                is_violation=quota.quota_type == QuotaType.HARD,
            )

        # Within limits
        return QuotaCheckResult(
            allowed=True,
            quota_id=quota.quota_id,
            current_usage=usage.current_usage,
            limit=limit,
            remaining=remaining - usage_amount,
            action=quota.action,
            message=f"Within limits: {new_usage}/{limit}",
            is_warning=False,
            is_violation=False,
        )

    def _is_action_allowed(self, action: QuotaAction) -> bool:
        """Check if an action allows the operation."""
        return action in [QuotaAction.WARN, QuotaAction.THROTTLE, QuotaAction.QUEUE]

    async def _handle_violation(
        self,
        quota: QuotaDefinition,
        result: QuotaCheckResult,
        user_id: Optional[str],
        workspace_id: Optional[str],
    ):
        """Handle a quota violation."""
        try:
            # Create violation record
            violation = QuotaViolation(
                violation_id=f"violation_{int(time.time())}_{quota.quota_id}",
                quota_id=quota.quota_id,
                resource_type=quota.resource_type,
                violation_time=datetime.now(),
                current_usage=result.current_usage,
                limit=result.limit,
                exceeded_by=result.current_usage - result.limit,
                action_taken=result.action,
                user_id=user_id,
                workspace_id=workspace_id,
            )

            self.quota_violations.append(violation)

            # Update usage statistics
            if quota.quota_id in self.quota_usage:
                self.quota_usage[quota.quota_id].violations += 1

            # Track enforcement actions
            if result.action == QuotaAction.BLOCK:
                self.quota_metrics["blocks_enforced"] += 1
            elif result.action == QuotaAction.THROTTLE:
                self.quota_metrics["throttles_enforced"] += 1

            # Call violation callbacks
            for callback in self.violation_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(violation)
                    else:
                        callback(violation)
                except Exception as e:
                    logger.error(f"Violation callback error: {e}")

            logger.warning(f"Quota violation: {result.message}")

        except Exception as e:
            logger.error(f"Failed to handle quota violation: {e}")

    async def _handle_warning(
        self,
        quota: QuotaDefinition,
        result: QuotaCheckResult,
        user_id: Optional[str],
        workspace_id: Optional[str],
    ):
        """Handle a quota warning."""
        try:
            # Update usage statistics
            if quota.quota_id in self.quota_usage:
                self.quota_usage[quota.quota_id].warnings += 1

            # Call warning callbacks
            for callback in self.warning_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(result)
                    else:
                        callback(result)
                except Exception as e:
                    logger.error(f"Warning callback error: {e}")

            logger.info(f"Quota warning: {result.message}")

        except Exception as e:
            logger.error(f"Failed to handle quota warning: {e}")

    async def _quota_reset_loop(self):
        """Background loop for resetting quota periods."""
        while self._running:
            try:
                await asyncio.sleep(60)  # Check every minute

                now = datetime.now()
                for quota_id, usage in self.quota_usage.items():
                    quota = self.quotas.get(quota_id)
                    if quota and self._should_reset_quota(quota, usage):
                        self._reset_quota_usage(quota_id)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Quota reset loop error: {e}")

    async def _usage_monitoring_loop(self):
        """Background loop for monitoring usage trends."""
        while self._running:
            try:
                await asyncio.sleep(self.check_interval)
                await self._monitor_usage_trends()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Usage monitoring loop error: {e}")

    async def _monitor_usage_trends(self):
        """Monitor usage trends and adjust quotas if needed."""
        try:
            for quota_id, usage_history in self.usage_history.items():
                if len(usage_history) < 5:  # Need at least 5 periods
                    continue

                # Analyze usage trends
                recent_usage = [entry["usage"] for entry in list(usage_history)[-5:]]

                # Check for consistent high usage
                quota = self.quotas.get(quota_id)
                if not quota:
                    continue

                high_usage_ratio = sum(
                    1 for u in recent_usage if u > quota.limit * 0.8
                ) / len(recent_usage)

                if high_usage_ratio > 0.8:  # 80% of periods have high usage
                    logger.info(
                        f"High usage trend detected for quota {quota_id}: {high_usage_ratio:.1%}"
                    )

                    # Could trigger dynamic quota adjustment here
                    if quota.quota_type == QuotaType.DYNAMIC:
                        await self._adjust_dynamic_quota(quota_id, recent_usage)

        except Exception as e:
            logger.error(f"Usage trend monitoring failed: {e}")

    async def _adjust_dynamic_quota(
        self, quota_id: str, recent_usage: List[Union[int, float]]
    ):
        """Adjust dynamic quotas based on usage patterns."""
        try:
            quota = self.quotas.get(quota_id)
            if not quota or quota.quota_type != QuotaType.DYNAMIC:
                return

            # Calculate new limit based on usage patterns
            avg_usage = statistics.mean(recent_usage)
            max_usage = max(recent_usage)

            # Set new limit to 120% of average usage, but not less than current limit
            new_limit = max(quota.limit, avg_usage * 1.2)

            # Don't exceed maximum reasonable limit
            max_reasonable = quota.limit * 2
            new_limit = min(new_limit, max_reasonable)

            if new_limit != quota.limit:
                quota.limit = new_limit
                quota.updated_at = datetime.now()

                logger.info(
                    f"Adjusted dynamic quota {quota_id}: {quota.limit} (was {quota.limit * 0.8:.0f})"
                )

        except Exception as e:
            logger.error(f"Dynamic quota adjustment failed: {e}")

    def add_violation_callback(self, callback: Callable):
        """Add a callback for quota violations."""
        self.violation_callbacks.append(callback)

    def add_warning_callback(self, callback: Callable):
        """Add a callback for quota warnings."""
        self.warning_callbacks.append(callback)

    def get_quota_status(
        self,
        quota_id: Optional[str] = None,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get current quota status."""
        status = {
            "quotas": {},
            "usage": {},
            "violations": [],
            "metrics": self.quota_metrics.copy(),
        }

        # Filter quotas
        quotas = self.quotas.values()
        if quota_id:
            quotas = [q for q in quotas if q.quota_id == quota_id]
        if user_id:
            quotas = [q for q in quotas if q.user_id == user_id]
        if workspace_id:
            quotas = [q for q in quotas if q.workspace_id == workspace_id]

        # Add quota definitions and usage
        for quota in quotas:
            status["quotas"][quota.quota_id] = quota.to_dict()

            usage = self.quota_usage.get(quota.quota_id)
            if usage:
                status["usage"][quota.quota_id] = usage.to_dict()

        # Add recent violations
        cutoff_time = datetime.now() - timedelta(hours=24)
        status["violations"] = [
            v.to_dict()
            for v in self.quota_violations
            if v.violation_time >= cutoff_time
        ]

        return status

    def get_quota_usage_history(
        self,
        quota_id: str,
        periods: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get usage history for a quota."""
        history = list(self.usage_history.get(quota_id, []))
        history.sort(key=lambda x: x["period_start"], reverse=True)

        return history[:periods]

    def get_quota_violations(
        self,
        quota_id: Optional[str] = None,
        resolved: Optional[bool] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get quota violations with optional filtering."""
        violations = self.quota_violations

        if quota_id:
            violations = [v for v in violations if v.quota_id == quota_id]

        if resolved is not None:
            violations = [v for v in violations if v.resolved == resolved]

        # Sort by violation time (most recent first)
        violations.sort(key=lambda x: x.violation_time, reverse=True)

        return [v.to_dict() for v in violations[:limit]]


# Global quota manager instance
_quota_manager: Optional[QuotaManager] = None


def get_quota_manager() -> QuotaManager:
    """Get or create the global quota manager instance."""
    global _quota_manager
    if _quota_manager is None:
        _quota_manager = QuotaManager()
    return _quota_manager


async def start_quota_manager():
    """Start the global quota manager."""
    manager = get_quota_manager()
    await manager.start()


async def stop_quota_manager():
    """Stop the global quota manager."""
    manager = get_quota_manager()
    if manager:
        await manager.stop()
