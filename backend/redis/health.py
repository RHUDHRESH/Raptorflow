"""
Redis health checking and monitoring.

Provides comprehensive health checks for Redis instances
with detailed reporting and alerting capabilities.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .client import get_redis
from .metrics import get_redis_metrics

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    name: str
    status: HealthStatus
    message: str
    response_time_ms: float
    details: Dict[str, Any] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class MemoryStatus:
    """Memory health status."""

    used_memory_bytes: int
    total_memory_bytes: int
    usage_percentage: float
    fragmentation_ratio: float
    status: HealthStatus
    warnings: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


@dataclass
class LatencyStatus:
    """Latency health status."""

    ping_latency_ms: float
    command_latency_ms: float
    status: HealthStatus
    warnings: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


@dataclass
class ConnectionStatus:
    """Connection health status."""

    connected_clients: int
    max_clients: int
    blocked_clients: int
    rejected_connections: int
    status: HealthStatus
    warnings: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


@dataclass
class PerformanceStatus:
    """Performance health status."""

    ops_per_sec: int
    hit_rate: float
    key_count: int
    status: HealthStatus
    warnings: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


@dataclass
class RedisHealthReport:
    """Comprehensive Redis health report."""

    overall_status: HealthStatus
    timestamp: datetime
    uptime_seconds: int
    checks: List[HealthCheckResult]
    memory: MemoryStatus
    latency: LatencyStatus
    connections: ConnectionStatus
    performance: PerformanceStatus
    server_info: Dict[str, Any]
    recommendations: List[str]


class RedisHealthChecker:
    """Comprehensive Redis health checker."""

    def __init__(self):
        self.redis = get_redis()
        self.metrics = get_redis_metrics()

        # Health thresholds
        self.thresholds = {
            "memory_usage_warning": 80.0,  # 80%
            "memory_usage_critical": 95.0,  # 95%
            "fragmentation_warning": 1.5,  # 1.5x
            "fragmentation_critical": 2.5,  # 2.5x
            "ping_latency_warning": 50.0,  # 50ms
            "ping_latency_critical": 100.0,  # 100ms
            "command_latency_warning": 10.0,  # 10ms
            "command_latency_critical": 50.0,  # 50ms
            "hit_rate_warning": 0.8,  # 80%
            "hit_rate_critical": 0.6,  # 60%
            "client_usage_warning": 0.8,  # 80%
            "client_usage_critical": 0.95,  # 95%
            "blocked_clients_warning": 10,  # 10 clients
            "blocked_clients_critical": 50,  # 50 clients
            "ops_per_sec_warning": 1000,  # 1000 ops/sec
            "ops_per_sec_critical": 5000,  # 5000 ops/sec
        }

    async def check_connection(self) -> HealthCheckResult:
        """Check Redis connection health."""
        start_time = datetime.now()

        try:
            # Basic ping test
            ping_result = await self.redis.ping()

            if not ping_result:
                return HealthCheckResult(
                    name="connection",
                    status=HealthStatus.CRITICAL,
                    message="Redis ping failed",
                    response_time_ms=(datetime.now() - start_time).total_seconds()
                    * 1000,
                )

            # Get server info
            info = await self.redis.async_client.info()

            response_time = (datetime.now() - start_time).total_seconds() * 1000

            return HealthCheckResult(
                name="connection",
                status=HealthStatus.HEALTHY,
                message="Redis connection successful",
                response_time_ms=response_time,
                details={
                    "redis_version": info.get("redis_version", "unknown"),
                    "redis_mode": info.get("redis_mode", "unknown"),
                    "uptime_seconds": info.get("uptime_in_seconds", 0),
                    "process_id": info.get("process_id", 0),
                },
            )

        except Exception as e:
            return HealthCheckResult(
                name="connection",
                status=HealthStatus.CRITICAL,
                message=f"Connection check failed: {str(e)}",
                response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
            )

    async def check_latency(self) -> HealthCheckResult:
        """Check Redis latency."""
        start_time = datetime.now()

        try:
            # Multiple ping tests for latency measurement
            ping_times = []
            for _ in range(5):
                ping_start = datetime.now()
                await self.redis.ping()
                ping_time = (datetime.now() - ping_start).total_seconds() * 1000
                ping_times.append(ping_time)

            # Calculate average ping latency
            avg_ping_latency = sum(ping_times) / len(ping_times)
            max_ping_latency = max(ping_times)

            # Test command latency (SET/GET)
            test_key = "health_check_latency_test"
            set_start = datetime.now()
            await self.redis.set(test_key, "test", ex=10)
            await self.redis.get(test_key)
            command_latency = (datetime.now() - set_start).total_seconds() * 1000

            # Clean up
            await self.redis.delete(test_key)

            # Determine status
            status = HealthStatus.HEALTHY
            warnings = []

            if avg_ping_latency > self.thresholds["ping_latency_critical"]:
                status = HealthStatus.CRITICAL
                warnings.append(f"High ping latency: {avg_ping_latency:.2f}ms")
            elif avg_ping_latency > self.thresholds["ping_latency_warning"]:
                status = HealthStatus.WARNING
                warnings.append(f"Elevated ping latency: {avg_ping_latency:.2f}ms")

            if command_latency > self.thresholds["command_latency_critical"]:
                status = HealthStatus.CRITICAL
                warnings.append(f"High command latency: {command_latency:.2f}ms")
            elif command_latency > self.thresholds["command_latency_warning"]:
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.WARNING
                warnings.append(f"Elevated command latency: {command_latency:.2f}ms")

            message = (
                f"Latency check passed"
                if status == HealthStatus.HEALTHY
                else "; ".join(warnings)
            )

            return HealthCheckResult(
                name="latency",
                status=status,
                message=message,
                response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                details={
                    "avg_ping_latency_ms": avg_ping_latency,
                    "max_ping_latency_ms": max_ping_latency,
                    "command_latency_ms": command_latency,
                    "ping_samples": ping_times,
                },
            )

        except Exception as e:
            return HealthCheckResult(
                name="latency",
                status=HealthStatus.CRITICAL,
                message=f"Latency check failed: {str(e)}",
                response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
            )

    async def check_memory(self) -> HealthCheckResult:
        """Check Redis memory health."""
        start_time = datetime.now()

        try:
            # Get memory metrics
            metrics = await self.metrics.get_metrics()
            memory = metrics.memory

            # Calculate memory usage percentage
            usage_percentage = (
                (memory.used_memory / memory.total_system_memory) * 100
                if memory.total_system_memory > 0
                else 0
            )

            # Determine status
            status = HealthStatus.HEALTHY
            warnings = []

            if usage_percentage > self.thresholds["memory_usage_critical"]:
                status = HealthStatus.CRITICAL
                warnings.append(f"Critical memory usage: {usage_percentage:.1f}%")
            elif usage_percentage > self.thresholds["memory_usage_warning"]:
                status = HealthStatus.WARNING
                warnings.append(f"High memory usage: {usage_percentage:.1f}%")

            if (
                memory.memory_fragmentation_ratio
                > self.thresholds["fragmentation_critical"]
            ):
                status = HealthStatus.CRITICAL
                warnings.append(
                    f"Critical memory fragmentation: {memory.memory_fragmentation_ratio:.2f}"
                )
            elif (
                memory.memory_fragmentation_ratio
                > self.thresholds["fragmentation_warning"]
            ):
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.WARNING
                warnings.append(
                    f"High memory fragmentation: {memory.memory_fragmentation_ratio:.2f}"
                )

            message = (
                f"Memory check passed"
                if status == HealthStatus.HEALTHY
                else "; ".join(warnings)
            )

            return HealthCheckResult(
                name="memory",
                status=status,
                message=message,
                response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                details={
                    "used_memory_bytes": memory.used_memory,
                    "used_memory_human": memory.used_memory_human,
                    "total_memory_bytes": memory.total_system_memory,
                    "usage_percentage": usage_percentage,
                    "fragmentation_ratio": memory.memory_fragmentation_ratio,
                    "used_memory_peak": memory.used_memory_peak,
                    "maxmemory": memory.maxmemory,
                },
            )

        except Exception as e:
            return HealthCheckResult(
                name="memory",
                status=HealthStatus.CRITICAL,
                message=f"Memory check failed: {str(e)}",
                response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
            )

    async def check_performance(self) -> HealthCheckResult:
        """Check Redis performance."""
        start_time = datetime.now()

        try:
            # Get performance metrics
            metrics = await self.metrics.get_metrics()
            perf = metrics.performance
            keyspace = metrics.keyspace

            # Determine status
            status = HealthStatus.HEALTHY
            warnings = []

            # Check operations per second
            if perf.instantaneous_ops_per_sec > self.thresholds["ops_per_sec_critical"]:
                status = HealthStatus.WARNING
                warnings.append(
                    f"High operations per second: {perf.instantaneous_ops_per_sec}"
                )
            elif (
                perf.instantaneous_ops_per_sec > self.thresholds["ops_per_sec_warning"]
            ):
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.WARNING
                warnings.append(
                    f"Elevated operations per second: {perf.instantaneous_ops_per_sec}"
                )

            # Check hit rate
            if keyspace.hit_rate < self.thresholds["hit_rate_critical"]:
                status = HealthStatus.WARNING
                warnings.append(f"Low hit rate: {keyspace.hit_rate:.2f}")
            elif keyspace.hit_rate < self.thresholds["hit_rate_warning"]:
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.WARNING
                warnings.append(f"Elevated miss rate: {1 - keyspace.hit_rate:.2f}")

            # Check rejected connections
            if perf.rejected_connections > 0:
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.WARNING
                warnings.append(f"Rejected connections: {perf.rejected_connections}")

            message = (
                f"Performance check passed"
                if status == HealthStatus.HEALTHY
                else "; ".join(warnings)
            )

            return HealthCheckResult(
                name="performance",
                status=status,
                message=message,
                response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                details={
                    "ops_per_sec": perf.instantaneous_ops_per_sec,
                    "hit_rate": keyspace.hit_rate,
                    "total_keys": keyspace.total_keys,
                    "rejected_connections": perf.rejected_connections,
                    "total_commands_processed": perf.total_commands_processed,
                    "instantaneous_input_kbps": perf.instantaneous_input_kbps,
                    "instantaneous_output_kbps": perf.instantaneous_output_kbps,
                },
            )

        except Exception as e:
            return HealthCheckResult(
                name="performance",
                status=HealthStatus.CRITICAL,
                message=f"Performance check failed: {str(e)}",
                response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
            )

    async def check_connections(self) -> HealthCheckResult:
        """Check Redis connections."""
        start_time = datetime.now()

        try:
            # Get connection metrics
            metrics = await self.metrics.get_metrics()
            connections = metrics.connections

            # Get max clients from server info
            info = await self.redis.async_client.info()
            max_clients = info.get("maxclients", 10000)

            # Calculate client usage percentage
            client_usage_percentage = (
                (connections.connected_clients / max_clients) * 100
                if max_clients > 0
                else 0
            )

            # Determine status
            status = HealthStatus.HEALTHY
            warnings = []

            if client_usage_percentage > self.thresholds["client_usage_critical"]:
                status = HealthStatus.CRITICAL
                warnings.append(
                    f"Critical client usage: {client_usage_percentage:.1f}%"
                )
            elif client_usage_percentage > self.thresholds["client_usage_warning"]:
                status = HealthStatus.WARNING
                warnings.append(f"High client usage: {client_usage_percentage:.1f}%")

            if (
                connections.blocked_clients
                > self.thresholds["blocked_clients_critical"]
            ):
                status = HealthStatus.CRITICAL
                warnings.append(
                    f"Critical blocked clients: {connections.blocked_clients}"
                )
            elif (
                connections.blocked_clients > self.thresholds["blocked_clients_warning"]
            ):
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.WARNING
                warnings.append(f"High blocked clients: {connections.blocked_clients}")

            message = (
                f"Connection check passed"
                if status == HealthStatus.HEALTHY
                else "; ".join(warnings)
            )

            return HealthCheckResult(
                name="connections",
                status=status,
                message=message,
                response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                details={
                    "connected_clients": connections.connected_clients,
                    "max_clients": max_clients,
                    "client_usage_percentage": client_usage_percentage,
                    "blocked_clients": connections.blocked_clients,
                    "tracking_clients": connections.tracking_clients,
                    "max_input_buffer": connections.client_recent_max_input_buffer,
                    "max_output_buffer": connections.client_recent_max_output_buffer,
                },
            )

        except Exception as e:
            return HealthCheckResult(
                name="connections",
                status=HealthStatus.CRITICAL,
                message=f"Connection check failed: {str(e)}",
                response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
            )

    async def check_persistence(self) -> HealthCheckResult:
        """Check Redis persistence."""
        start_time = datetime.now()

        try:
            # Get persistence metrics
            metrics = await self.metrics.get_metrics()
            persistence = metrics.persistence

            # Determine status
            status = HealthStatus.HEALTHY
            warnings = []

            # Check if loading
            if persistence.loading:
                status = HealthStatus.WARNING
                warnings.append("Redis is currently loading data")

            # Check background save status
            if persistence.rdb_bgsave_in_progress:
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.WARNING
                warnings.append("Background save in progress")

            # Check last save status
            if persistence.rdb_last_bgsave_status != "ok":
                status = HealthStatus.WARNING
                warnings.append(
                    f"Last background save status: {persistence.rdb_last_bgsave_status}"
                )

            # Check AOF status if enabled
            if persistence.aof_enabled:
                if persistence.aof_rewrite_in_progress:
                    if status == HealthStatus.HEALTHY:
                        status = HealthStatus.WARNING
                    warnings.append("AOF rewrite in progress")

                if persistence.aof_last_rewrite_status != "ok":
                    status = HealthStatus.WARNING
                    warnings.append(
                        f"Last AOF rewrite status: {persistence.aof_last_rewrite_status}"
                    )

            # Check time since last save
            if persistence.rdb_last_save_time > 0:
                time_since_save = (
                    datetime.now().timestamp() - persistence.rdb_last_save_time
                )
                if time_since_save > 3600:  # 1 hour
                    if status == HealthStatus.HEALTHY:
                        status = HealthStatus.WARNING
                    warnings.append(
                        f"Long time since last save: {time_since_save:.0f} seconds"
                    )

            message = (
                f"Persistence check passed"
                if status == HealthStatus.HEALTHY
                else "; ".join(warnings)
            )

            return HealthCheckResult(
                name="persistence",
                status=status,
                message=message,
                response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                details={
                    "loading": persistence.loading,
                    "rdb_bgsave_in_progress": persistence.rdb_bgsave_in_progress,
                    "rdb_last_save_time": persistence.rdb_last_save_time,
                    "rdb_last_bgsave_status": persistence.rdb_last_bgsave_status,
                    "aof_enabled": persistence.aof_enabled,
                    "aof_rewrite_in_progress": persistence.aof_rewrite_in_progress,
                    "rdb_changes_since_last_save": persistence.rdb_changes_since_last_save,
                },
            )

        except Exception as e:
            return HealthCheckResult(
                name="persistence",
                status=HealthStatus.CRITICAL,
                message=f"Persistence check failed: {str(e)}",
                response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
            )

    async def check_replication(self) -> HealthCheckResult:
        """Check Redis replication."""
        start_time = datetime.now()

        try:
            # Get replication metrics
            metrics = await self.metrics.get_metrics()
            replication = metrics.replication

            # Determine status
            status = HealthStatus.HEALTHY
            warnings = []

            # Check replication role
            if replication.role == "slave":
                if replication.master_link_status != "up":
                    status = HealthStatus.CRITICAL
                    warnings.append(
                        f"Master link down: {replication.master_link_status}"
                    )
                elif replication.master_link_down_since_seconds > 0:
                    status = HealthStatus.WARNING
                    warnings.append(
                        f"Master link down for {replication.master_link_down_since_seconds} seconds"
                    )

            # Check connected slaves (if master)
            if replication.role == "master" and replication.connected_slaves == 0:
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.WARNING
                warnings.append("No connected slaves")

            # Check replication backlog
            if (
                replication.repl_backlog_active
                and replication.repl_backlog_size > 100 * 1024 * 1024
            ):  # 100MB
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.WARNING
                warnings.append(
                    f"Large replication backlog: {replication.repl_backlog_size} bytes"
                )

            message = (
                f"Replication check passed"
                if status == HealthStatus.HEALTHY
                else "; ".join(warnings)
            )

            return HealthCheckResult(
                name="replication",
                status=status,
                message=message,
                response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                details={
                    "role": replication.role,
                    "connected_slaves": replication.connected_slaves,
                    "master_repl_offset": replication.master_repl_offset,
                    "repl_backlog_active": replication.repl_backlog_active,
                    "repl_backlog_size": replication.repl_backlog_size,
                    "master_link_status": replication.master_link_status,
                    "master_sync_in_progress": replication.master_sync_in_progress,
                },
            )

        except Exception as e:
            return HealthCheckResult(
                name="replication",
                status=HealthStatus.CRITICAL,
                message=f"Replication check failed: {str(e)}",
                response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
            )

    async def comprehensive_health_check(self) -> RedisHealthReport:
        """Perform comprehensive health check."""
        start_time = datetime.now()

        # Run all health checks
        checks = await asyncio.gather(
            self.check_connection(),
            self.check_latency(),
            self.check_memory(),
            self.check_performance(),
            self.check_connections(),
            self.check_persistence(),
            self.check_replication(),
            return_exceptions=True,
        )

        # Filter out exceptions
        valid_checks = []
        for check in checks:
            if isinstance(check, HealthCheckResult):
                valid_checks.append(check)
            else:
                # Create error result for exceptions
                valid_checks.append(
                    HealthCheckResult(
                        name="unknown",
                        status=HealthStatus.CRITICAL,
                        message=f"Health check error: {str(check)}",
                        response_time_ms=0.0,
                    )
                )

        # Determine overall status
        overall_status = HealthStatus.HEALTHY
        for check in valid_checks:
            if check.status == HealthStatus.CRITICAL:
                overall_status = HealthStatus.CRITICAL
                break
            elif (
                check.status == HealthStatus.WARNING
                and overall_status == HealthStatus.HEALTHY
            ):
                overall_status = HealthStatus.WARNING

        # Extract detailed status information
        memory_status = self._extract_memory_status(valid_checks)
        latency_status = self._extract_latency_status(valid_checks)
        connection_status = self._extract_connection_status(valid_checks)
        performance_status = self._extract_performance_status(valid_checks)

        # Get server info
        server_info = await self._get_server_info()

        # Generate recommendations
        recommendations = self._generate_recommendations(
            valid_checks,
            memory_status,
            latency_status,
            connection_status,
            performance_status,
        )

        # Calculate uptime
        uptime_seconds = server_info.get("uptime_in_seconds", 0)

        return RedisHealthReport(
            overall_status=overall_status,
            timestamp=datetime.now(),
            uptime_seconds=uptime_seconds,
            checks=valid_checks,
            memory=memory_status,
            latency=latency_status,
            connections=connection_status,
            performance=performance_status,
            server_info=server_info,
            recommendations=recommendations,
        )

    def _extract_memory_status(self, checks: List[HealthCheckResult]) -> MemoryStatus:
        """Extract memory status from health checks."""
        memory_check = next((c for c in checks if c.name == "memory"), None)

        if memory_check and memory_check.details:
            details = memory_check.details
            return MemoryStatus(
                used_memory_bytes=details.get("used_memory_bytes", 0),
                total_memory_bytes=details.get("total_memory_bytes", 0),
                usage_percentage=details.get("usage_percentage", 0.0),
                fragmentation_ratio=details.get("fragmentation_ratio", 0.0),
                status=memory_check.status,
                warnings=(
                    memory_check.message.split("; ")
                    if memory_check.status != HealthStatus.HEALTHY
                    else []
                ),
            )

        return MemoryStatus(0, 0, 0.0, 0.0, HealthStatus.UNKNOWN)

    def _extract_latency_status(self, checks: List[HealthCheckResult]) -> LatencyStatus:
        """Extract latency status from health checks."""
        latency_check = next((c for c in checks if c.name == "latency"), None)

        if latency_check and latency_check.details:
            details = latency_check.details
            return LatencyStatus(
                ping_latency_ms=details.get("avg_ping_latency_ms", 0.0),
                command_latency_ms=details.get("command_latency_ms", 0.0),
                status=latency_check.status,
                warnings=(
                    latency_check.message.split("; ")
                    if latency_check.status != HealthStatus.HEALTHY
                    else []
                ),
            )

        return LatencyStatus(0.0, 0.0, HealthStatus.UNKNOWN)

    def _extract_connection_status(
        self, checks: List[HealthCheckResult]
    ) -> ConnectionStatus:
        """Extract connection status from health checks."""
        connection_check = next((c for c in checks if c.name == "connections"), None)

        if connection_check and connection_check.details:
            details = connection_check.details
            return ConnectionStatus(
                connected_clients=details.get("connected_clients", 0),
                max_clients=details.get("max_clients", 0),
                blocked_clients=details.get("blocked_clients", 0),
                rejected_connections=0,  # Not available in details
                status=connection_check.status,
                warnings=(
                    connection_check.message.split("; ")
                    if connection_check.status != HealthStatus.HEALTHY
                    else []
                ),
            )

        return ConnectionStatus(0, 0, 0, 0, HealthStatus.UNKNOWN)

    def _extract_performance_status(
        self, checks: List[HealthCheckResult]
    ) -> PerformanceStatus:
        """Extract performance status from health checks."""
        performance_check = next((c for c in checks if c.name == "performance"), None)

        if performance_check and performance_check.details:
            details = performance_check.details
            return PerformanceStatus(
                ops_per_sec=details.get("ops_per_sec", 0),
                hit_rate=details.get("hit_rate", 0.0),
                key_count=details.get("total_keys", 0),
                status=performance_check.status,
                warnings=(
                    performance_check.message.split("; ")
                    if performance_check.status != HealthStatus.HEALTHY
                    else []
                ),
            )

        return PerformanceStatus(0, 0.0, 0, HealthStatus.UNKNOWN)

    async def _get_server_info(self) -> Dict[str, Any]:
        """Get server information."""
        try:
            info = await self.redis.async_client.info()
            return {
                "redis_version": info.get("redis_version", "unknown"),
                "redis_mode": info.get("redis_mode", "standalone"),
                "os": info.get("os", "unknown"),
                "arch_bits": info.get("arch_bits", 0),
                "process_id": info.get("process_id", 0),
                "run_id": info.get("run_id", ""),
                "tcp_port": info.get("tcp_port", 6379),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0),
                "uptime_in_days": info.get("uptime_in_days", 0),
                "hz": info.get("hz", 10),
                "configured_hz": info.get("configured_hz", 10),
            }
        except Exception as e:
            logger.error(f"Failed to get server info: {e}")
            return {}

    def _generate_recommendations(
        self,
        checks: List[HealthCheckResult],
        memory: MemoryStatus,
        latency: LatencyStatus,
        connections: ConnectionStatus,
        performance: PerformanceStatus,
    ) -> List[str]:
        """Generate health recommendations."""
        recommendations = []

        # Memory recommendations
        if memory.status == HealthStatus.CRITICAL:
            if memory.usage_percentage > 90:
                recommendations.append(
                    "Consider increasing memory allocation or implementing memory cleanup"
                )
            if memory.fragmentation_ratio > 2.0:
                recommendations.append(
                    "High memory fragmentation detected - consider restarting Redis"
                )
        elif memory.status == HealthStatus.WARNING:
            if memory.usage_percentage > 80:
                recommendations.append("Monitor memory usage closely")
            if memory.fragmentation_ratio > 1.5:
                recommendations.append(
                    "Memory fragmentation is elevated - monitor for degradation"
                )

        # Latency recommendations
        if latency.status == HealthStatus.CRITICAL:
            if latency.ping_latency_ms > 100:
                recommendations.append(
                    "High latency detected - check network connectivity and server load"
                )
            if latency.command_latency_ms > 50:
                recommendations.append(
                    "High command latency - consider optimizing Redis configuration"
                )
        elif latency.status == HealthStatus.WARNING:
            recommendations.append(
                "Latency is elevated - monitor for performance degradation"
            )

        # Connection recommendations
        if connections.status == HealthStatus.CRITICAL:
            if connections.connected_clients / connections.max_clients > 0.95:
                recommendations.append(
                    "Client limit nearly reached - consider increasing maxclients"
                )
            if connections.blocked_clients > 50:
                recommendations.append(
                    "High number of blocked clients - check for long-running operations"
                )
        elif connections.status == HealthStatus.WARNING:
            recommendations.append("Monitor client connections for capacity planning")

        # Performance recommendations
        if performance.status == HealthStatus.WARNING:
            if performance.hit_rate < 0.8:
                recommendations.append(
                    "Low cache hit rate - review caching strategy and key expiration"
                )
            if performance.ops_per_sec > 1000:
                recommendations.append(
                    "High operations per second - monitor for performance bottlenecks"
                )

        # General recommendations
        critical_checks = [c for c in checks if c.status == HealthStatus.CRITICAL]
        if critical_checks:
            recommendations.append(
                "Address critical issues immediately to prevent service degradation"
            )

        if not recommendations:
            recommendations.append("Redis instance is healthy - continue monitoring")

        return recommendations

    async def quick_health_check(self) -> Dict[str, Any]:
        """Quick health check for monitoring endpoints."""
        try:
            # Just check connection and basic metrics
            connection_ok = await self.redis.ping()

            if not connection_ok:
                return {
                    "status": "unhealthy",
                    "message": "Redis connection failed",
                    "timestamp": datetime.now().isoformat(),
                }

            # Get basic metrics
            info = await self.redis.async_client.info()

            return {
                "status": "healthy",
                "message": "Redis is responding",
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": info.get("uptime_in_seconds", 0),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "ops_per_sec": info.get("instantaneous_ops_per_sec", 0),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Health check failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    def update_thresholds(self, thresholds: Dict[str, float]):
        """Update health check thresholds."""
        self.thresholds.update(thresholds)

    def get_thresholds(self) -> Dict[str, float]:
        """Get current health check thresholds."""
        return self.thresholds.copy()


# Global health checker instance
_health_checker = RedisHealthChecker()


def get_health_checker() -> RedisHealthChecker:
    """Get global health checker instance."""
    return _health_checker


# Convenience functions
async def check_redis_health() -> RedisHealthReport:
    """Perform comprehensive Redis health check."""
    return await _health_checker.comprehensive_health_check()


async def quick_health_check() -> Dict[str, Any]:
    """Quick health check for monitoring."""
    return await _health_checker.quick_health_check()
