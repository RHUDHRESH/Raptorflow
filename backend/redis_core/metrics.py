"""
Redis metrics collection and monitoring.

Provides comprehensive metrics collection for Redis performance
and usage monitoring with dashboard support.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from .client import get_redis

logger = logging.getLogger(__name__)


@dataclass
class RedisMemoryMetrics:
    """Redis memory usage metrics."""

    used_memory: int
    used_memory_human: str
    used_memory_rss: int
    used_memory_peak: int
    used_memory_peak_human: str
    total_system_memory: int
    total_system_memory_human: str
    maxmemory: int
    maxmemory_human: str
    memory_fragmentation_ratio: float


@dataclass
class RedisPerformanceMetrics:
    """Redis performance metrics."""

    total_connections_received: int
    total_commands_processed: int
    instantaneous_ops_per_sec: int
    total_net_input_bytes: int
    total_net_output_bytes: int
    instantaneous_input_kbps: float
    instantaneous_output_kbps: float
    rejected_connections: int
    sync_full: int
    sync_partial_ok: int
    sync_partial_err: int


@dataclass
class RedisKeyMetrics:
    """Redis key space metrics."""

    total_keys: int
    expires: int
    avg_ttl: int
    keyspace_hits: int
    keyspace_misses: int
    hit_rate: float
    keys_by_db: Dict[str, Dict[str, int]]


@dataclass
class RedisConnectionMetrics:
    """Redis connection metrics."""

    connected_clients: int
    client_recent_max_input_buffer: int
    client_recent_max_output_buffer: int
    blocked_clients: int
    tracking_clients: int
    tracking_total_keys: int
    tracking_total_items: int
    tracking_total_prefixes: int


@dataclass
class RedisPersistenceMetrics:
    """Redis persistence metrics."""

    loading: bool
    rdb_changes_since_last_save: int
    rdb_bgsave_in_progress: bool
    rdb_last_save_time: int
    rdb_last_bgsave_status: str
    rdb_last_bgsave_time_sec: int
    rdb_current_bgsave_time_sec: int
    rdb_last_cow_size: int
    aof_enabled: bool
    aof_rewrite_in_progress: bool
    aof_rewrite_scheduled: bool
    aof_last_rewrite_time_sec: int
    aof_current_rewrite_time_sec: int
    aof_last_bgrewrite_status: str
    aof_last_write_status: str


@dataclass
class RedisReplicationMetrics:
    """Redis replication metrics."""

    role: str
    connected_slaves: int
    master_repl_offset: int
    repl_backlog_active: bool
    repl_backlog_size: int
    repl_backlog_first_byte_offset: int
    repl_backlog_histlen: int
    master_sync_in_progress: bool
    master_sync_last_io_seconds_ago: int
    master_link_status: str
    master_link_down_since_seconds: int


@dataclass
class RedisServerMetrics:
    """Redis server information."""

    redis_version: str
    redis_mode: str
    os: str
    arch_bits: int
    process_id: int
    run_id: str
    tcp_port: int
    uptime_in_seconds: int
    uptime_in_days: int
    hz: int
    configured_hz: int
    lru_clock: int
    executable: str
    config_file: str


@dataclass
class RedisMetricsReport:
    """Complete Redis metrics report."""

    timestamp: datetime
    memory: RedisMemoryMetrics
    performance: RedisPerformanceMetrics
    keyspace: RedisKeyMetrics
    connections: RedisConnectionMetrics
    persistence: RedisPersistenceMetrics
    replication: RedisReplicationMetrics
    server: RedisServerMetrics
    custom_metrics: Dict[str, Any] = field(default_factory=dict)


class RedisMetrics:
    """Redis metrics collector and analyzer."""

    def __init__(self):
        self.redis = get_redis()
        self.metrics_history: List[RedisMetricsReport] = []
        self.max_history_size = 1000
        self.collection_interval_seconds = 60
        self._collection_task: Optional[asyncio.Task] = None
        self._collecting = False

        # Custom metrics
        self.custom_metrics: Dict[str, Any] = {}
        self.metric_callbacks: List[callable] = []

    async def get_metrics(self) -> RedisMetricsReport:
        """Get comprehensive Redis metrics."""
        try:
            # Get Redis INFO command
            info = await self.redis.async_client.info()

            # Parse metrics
            report = RedisMetricsReport(
                timestamp=datetime.now(),
                memory=self._parse_memory_metrics(info),
                performance=self._parse_performance_metrics(info),
                keyspace=self._parse_keyspace_metrics(info),
                connections=self._parse_connection_metrics(info),
                persistence=self._parse_persistence_metrics(info),
                replication=self._parse_replication_metrics(info),
                server=self._parse_server_metrics(info),
                custom_metrics=self.custom_metrics.copy(),
            )

            return report

        except Exception as e:
            logger.error(f"Failed to get Redis metrics: {e}")
            return self._get_empty_metrics()

    def _parse_memory_metrics(self, info: Dict[str, Any]) -> RedisMemoryMetrics:
        """Parse memory metrics from Redis INFO."""
        return RedisMemoryMetrics(
            used_memory=info.get("used_memory", 0),
            used_memory_human=info.get("used_memory_human", "0B"),
            used_memory_rss=info.get("used_memory_rss", 0),
            used_memory_peak=info.get("used_memory_peak", 0),
            used_memory_peak_human=info.get("used_memory_peak_human", "0B"),
            total_system_memory=info.get("total_system_memory", 0),
            total_system_memory_human=info.get("total_system_memory_human", "0B"),
            maxmemory=info.get("maxmemory", 0),
            maxmemory_human=info.get("maxmemory_human", "0B"),
            memory_fragmentation_ratio=info.get("mem_fragmentation_ratio", 0.0),
        )

    def _parse_performance_metrics(
        self, info: Dict[str, Any]
    ) -> RedisPerformanceMetrics:
        """Parse performance metrics from Redis INFO."""
        return RedisPerformanceMetrics(
            total_connections_received=info.get("total_connections_received", 0),
            total_commands_processed=info.get("total_commands_processed", 0),
            instantaneous_ops_per_sec=info.get("instantaneous_ops_per_sec", 0),
            total_net_input_bytes=info.get("total_net_input_bytes", 0),
            total_net_output_bytes=info.get("total_net_output_bytes", 0),
            instantaneous_input_kbps=info.get("instantaneous_input_kbps", 0.0),
            instantaneous_output_kbps=info.get("instantaneous_output_kbps", 0.0),
            rejected_connections=info.get("rejected_connections", 0),
            sync_full=info.get("sync_full", 0),
            sync_partial_ok=info.get("sync_partial_ok", 0),
            sync_partial_err=info.get("sync_partial_err", 0),
        )

    def _parse_keyspace_metrics(self, info: Dict[str, Any]) -> RedisKeyMetrics:
        """Parse keyspace metrics from Redis INFO."""
        keyspace_hits = info.get("keyspace_hits", 0)
        keyspace_misses = info.get("keyspace_misses", 0)
        total_requests = keyspace_hits + keyspace_misses
        hit_rate = (keyspace_hits / total_requests) if total_requests > 0 else 0.0

        # Parse keyspace info for each database
        keys_by_db = {}
        for key, value in info.items():
            if key.startswith("db"):
                try:
                    # Format: "db0:keys=100,expires=10,avg_ttl=3600"
                    parts = value.split(",")
                    db_info = {}
                    for part in parts:
                        if "=" in part:
                            k, v = part.split("=", 1)
                            db_info[k] = int(v) if k != "avg_ttl" else int(v)
                    keys_by_db[key] = db_info
                except (ValueError, AttributeError):
                    continue

        # Calculate total keys
        total_keys = sum(db_info.get("keys", 0) for db_info in keys_by_db.values())
        expires = sum(db_info.get("expires", 0) for db_info in keys_by_db.values())
        avg_ttl = sum(db_info.get("avg_ttl", 0) for db_info in keys_by_db.values())
        avg_ttl = avg_ttl // len(keys_by_db) if keys_by_db else 0

        return RedisKeyMetrics(
            total_keys=total_keys,
            expires=expires,
            avg_ttl=avg_ttl,
            keyspace_hits=keyspace_hits,
            keyspace_misses=keyspace_misses,
            hit_rate=hit_rate,
            keys_by_db=keys_by_db,
        )

    def _parse_connection_metrics(self, info: Dict[str, Any]) -> RedisConnectionMetrics:
        """Parse connection metrics from Redis INFO."""
        return RedisConnectionMetrics(
            connected_clients=info.get("connected_clients", 0),
            client_recent_max_input_buffer=info.get(
                "client_recent_max_input_buffer", 0
            ),
            client_recent_max_output_buffer=info.get(
                "client_recent_max_output_buffer", 0
            ),
            blocked_clients=info.get("blocked_clients", 0),
            tracking_clients=info.get("tracking_clients", 0),
            tracking_total_keys=info.get("tracking_total_keys", 0),
            tracking_total_items=info.get("tracking_total_items", 0),
            tracking_total_prefixes=info.get("tracking_total_prefixes", 0),
        )

    def _parse_persistence_metrics(
        self, info: Dict[str, Any]
    ) -> RedisPersistenceMetrics:
        """Parse persistence metrics from Redis INFO."""
        return RedisPersistenceMetrics(
            loading=info.get("loading", False),
            rdb_changes_since_last_save=info.get("rdb_changes_since_last_save", 0),
            rdb_bgsave_in_progress=info.get("rdb_bgsave_in_progress", False),
            rdb_last_save_time=info.get("rdb_last_save_time", 0),
            rdb_last_bgsave_status=info.get("rdb_last_bgsave_status", ""),
            rdb_last_bgsave_time_sec=info.get("rdb_last_bgsave_time_sec", 0),
            rdb_current_bgsave_time_sec=info.get("rdb_current_bgsave_time_sec", 0),
            rdb_last_cow_size=info.get("rdb_last_cow_size", 0),
            aof_enabled=info.get("aof_enabled", False),
            aof_rewrite_in_progress=info.get("aof_rewrite_in_progress", False),
            aof_rewrite_scheduled=info.get("aof_rewrite_scheduled", False),
            aof_last_rewrite_time_sec=info.get("aof_last_rewrite_time_sec", 0),
            aof_current_rewrite_time_sec=info.get("aof_current_rewrite_time_sec", 0),
            aof_last_bgrewrite_status=info.get("aof_last_bgrewrite_status", ""),
            aof_last_write_status=info.get("aof_last_write_status", ""),
        )

    def _parse_replication_metrics(
        self, info: Dict[str, Any]
    ) -> RedisReplicationMetrics:
        """Parse replication metrics from Redis INFO."""
        return RedisReplicationMetrics(
            role=info.get("role", "master"),
            connected_slaves=info.get("connected_slaves", 0),
            master_repl_offset=info.get("master_repl_offset", 0),
            repl_backlog_active=info.get("repl_backlog_active", False),
            repl_backlog_size=info.get("repl_backlog_size", 0),
            repl_backlog_first_byte_offset=info.get(
                "repl_backlog_first_byte_offset", 0
            ),
            repl_backlog_histlen=info.get("repl_backlog_histlen", 0),
            master_sync_in_progress=info.get("master_sync_in_progress", False),
            master_sync_last_io_seconds_ago=info.get(
                "master_sync_last_io_seconds_ago", 0
            ),
            master_link_status=info.get("master_link_status", ""),
            master_link_down_since_seconds=info.get(
                "master_link_down_since_seconds", 0
            ),
        )

    def _parse_server_metrics(self, info: Dict[str, Any]) -> RedisServerMetrics:
        """Parse server metrics from Redis INFO."""
        return RedisServerMetrics(
            redis_version=info.get("redis_version", "unknown"),
            redis_mode=info.get("redis_mode", "standalone"),
            os=info.get("os", "unknown"),
            arch_bits=info.get("arch_bits", 0),
            process_id=info.get("process_id", 0),
            run_id=info.get("run_id", ""),
            tcp_port=info.get("tcp_port", 6379),
            uptime_in_seconds=info.get("uptime_in_seconds", 0),
            uptime_in_days=info.get("uptime_in_days", 0),
            hz=info.get("hz", 10),
            configured_hz=info.get("configured_hz", 10),
            lru_clock=info.get("lru_clock", 0),
            executable=info.get("executable", ""),
            config_file=info.get("config_file", ""),
        )

    def _get_empty_metrics(self) -> RedisMetricsReport:
        """Get empty metrics report for error cases."""
        return RedisMetricsReport(
            timestamp=datetime.now(),
            memory=RedisMemoryMetrics(0, "0B", 0, 0, "0B", 0, "0B", 0, "0B", 0.0),
            performance=RedisPerformanceMetrics(0, 0, 0, 0, 0, 0.0, 0.0, 0, 0, 0, 0),
            keyspace=RedisKeyMetrics(0, 0, 0, 0, 0, 0.0, {}),
            connections=RedisConnectionMetrics(0, 0, 0, 0, 0, 0, 0, 0),
            persistence=RedisPersistenceMetrics(
                False, 0, False, 0, "", 0, 0, 0, False, False, False, 0, 0, "", ""
            ),
            replication=RedisReplicationMetrics(
                "master", 0, 0, False, 0, 0, 0, False, 0, "", 0
            ),
            server=RedisServerMetrics(
                "unknown",
                "standalone",
                "unknown",
                0,
                0,
                "",
                6379,
                0,
                0,
                10,
                10,
                0,
                "",
                "",
            ),
            custom_metrics={},
        )

    async def get_memory_usage(self) -> Dict[str, Any]:
        """Get detailed memory usage information."""
        try:
            metrics = await self.get_metrics()
            memory = metrics.memory

            return {
                "used_memory_bytes": memory.used_memory,
                "used_memory_human": memory.used_memory_human,
                "used_memory_mb": memory.used_memory / (1024 * 1024),
                "used_memory_gb": memory.used_memory / (1024 * 1024 * 1024),
                "used_memory_rss_bytes": memory.used_memory_rss,
                "used_memory_rss_mb": memory.used_memory_rss / (1024 * 1024),
                "used_memory_peak_bytes": memory.used_memory_peak,
                "used_memory_peak_mb": memory.used_memory_peak / (1024 * 1024),
                "total_system_memory_bytes": memory.total_system_memory,
                "total_system_memory_gb": memory.total_system_memory
                / (1024 * 1024 * 1024),
                "memory_usage_percentage": (
                    (memory.used_memory / memory.total_system_memory) * 100
                    if memory.total_system_memory > 0
                    else 0
                ),
                "memory_fragmentation_ratio": memory.memory_fragmentation_ratio,
                "maxmemory_bytes": memory.maxmemory,
                "maxmemory_mb": memory.maxmemory / (1024 * 1024),
                "maxmemory_percentage": (
                    (memory.used_memory / memory.maxmemory) * 100
                    if memory.maxmemory > 0
                    else 0
                ),
            }

        except Exception as e:
            logger.error(f"Failed to get memory usage: {e}")
            return {}

    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        try:
            metrics = await self.get_metrics()
            perf = metrics.performance

            return {
                "total_commands_processed": perf.total_commands_processed,
                "total_connections_received": perf.total_connections_received,
                "instantaneous_ops_per_sec": perf.instantaneous_ops_per_sec,
                "instantaneous_input_kbps": perf.instantaneous_input_kbps,
                "instantaneous_output_kbps": perf.instantaneous_output_kbps,
                "total_net_input_bytes": perf.total_net_input_bytes,
                "total_net_output_bytes": perf.total_net_output_bytes,
                "rejected_connections": perf.rejected_connections,
                "sync_operations": {
                    "full": perf.sync_full,
                    "partial_ok": perf.sync_partial_ok,
                    "partial_err": perf.sync_partial_err,
                },
                "commands_per_connection": (
                    perf.total_commands_processed / perf.total_connections_received
                    if perf.total_connections_received > 0
                    else 0
                ),
                "bytes_per_command": (
                    (perf.total_net_input_bytes + perf.total_net_output_bytes)
                    / perf.total_commands_processed
                    if perf.total_commands_processed > 0
                    else 0
                ),
            }

        except Exception as e:
            logger.error(f"Failed to get performance stats: {e}")
            return {}

    async def get_keyspace_stats(self) -> Dict[str, Any]:
        """Get keyspace statistics."""
        try:
            metrics = await self.get_metrics()
            keyspace = metrics.keyspace

            return {
                "total_keys": keyspace.total_keys,
                "keys_with_ttl": keyspace.expires,
                "keys_without_ttl": keyspace.total_keys - keyspace.expires,
                "average_ttl_seconds": keyspace.avg_ttl,
                "average_ttl_minutes": keyspace.avg_ttl / 60,
                "average_ttl_hours": keyspace.avg_ttl / 3600,
                "keyspace_hits": keyspace.keyspace_hits,
                "keyspace_misses": keyspace.keyspace_misses,
                "hit_rate_percentage": keyspace.hit_rate * 100,
                "total_requests": keyspace.keyspace_hits + keyspace.keyspace_misses,
                "keys_by_database": keyspace.keys_by_db,
                "database_count": len(keyspace.keys_by_db),
            }

        except Exception as e:
            logger.error(f"Failed to get keyspace stats: {e}")
            return {}

    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        try:
            metrics = await self.get_metrics()
            connections = metrics.connections

            return {
                "connected_clients": connections.connected_clients,
                "blocked_clients": connections.blocked_clients,
                "tracking_clients": connections.tracking_clients,
                "max_input_buffer": connections.client_recent_max_input_buffer,
                "max_output_buffer": connections.client_recent_max_output_buffer,
                "tracking_total_keys": connections.tracking_total_keys,
                "tracking_total_items": connections.tracking_total_items,
                "tracking_total_prefixes": connections.tracking_total_prefixes,
                "blocked_percentage": (
                    (connections.blocked_clients / connections.connected_clients) * 100
                    if connections.connected_clients > 0
                    else 0
                ),
                "tracking_percentage": (
                    (connections.tracking_clients / connections.connected_clients) * 100
                    if connections.connected_clients > 0
                    else 0
                ),
            }

        except Exception as e:
            logger.error(f"Failed to get connection stats: {e}")
            return {}

    async def get_server_info(self) -> Dict[str, Any]:
        """Get server information."""
        try:
            metrics = await self.get_metrics()
            server = metrics.server

            return {
                "redis_version": server.redis_version,
                "redis_mode": server.redis_mode,
                "operating_system": server.os,
                "architecture_bits": server.arch_bits,
                "process_id": server.process_id,
                "run_id": server.run_id,
                "tcp_port": server.tcp_port,
                "uptime_seconds": server.uptime_in_seconds,
                "uptime_minutes": server.uptime_in_seconds / 60,
                "uptime_hours": server.uptime_in_seconds / 3600,
                "uptime_days": server.uptime_in_days,
                "hz": server.hz,
                "configured_hz": server.configured_hz,
                "lru_clock": server.lru_clock,
                "executable_path": server.executable,
                "config_file": server.config_file,
            }

        except Exception as e:
            logger.error(f"Failed to get server info: {e}")
            return {}

    async def get_health_status(self) -> Dict[str, Any]:
        """Get Redis health status."""
        try:
            metrics = await self.get_metrics()

            # Determine health status
            health_status = "healthy"
            issues = []

            # Check memory usage
            memory_usage_percentage = (
                (metrics.memory.used_memory / metrics.memory.total_system_memory) * 100
                if metrics.memory.total_system_memory > 0
                else 0
            )
            if memory_usage_percentage > 90:
                health_status = "critical"
                issues.append(f"High memory usage: {memory_usage_percentage:.1f}%")
            elif memory_usage_percentage > 80:
                health_status = "warning"
                issues.append(f"Elevated memory usage: {memory_usage_percentage:.1f}%")

            # Check fragmentation
            if metrics.memory.memory_fragmentation_ratio > 2.0:
                health_status = "warning"
                issues.append(
                    f"High memory fragmentation: {metrics.memory.memory_fragmentation_ratio:.2f}"
                )

            # Check hit rate
            if metrics.keyspace.hit_rate < 0.8:
                health_status = "warning"
                issues.append(f"Low hit rate: {metrics.keyspace.hit_rate:.2f}")

            # Check rejected connections
            if metrics.performance.rejected_connections > 0:
                health_status = "warning"
                issues.append(
                    f"Rejected connections: {metrics.performance.rejected_connections}"
                )

            # Check blocked clients
            if (
                metrics.connections.blocked_clients
                > metrics.connections.connected_clients * 0.1
            ):
                health_status = "warning"
                issues.append(
                    f"High blocked clients: {metrics.connections.blocked_clients}"
                )

            return {
                "status": health_status,
                "issues": issues,
                "memory_usage_percentage": memory_usage_percentage,
                "hit_rate": metrics.keyspace.hit_rate,
                "instantaneous_ops_per_sec": metrics.performance.instantaneous_ops_per_sec,
                "connected_clients": metrics.connections.connected_clients,
                "uptime_seconds": metrics.server.uptime_in_seconds,
                "timestamp": metrics.timestamp.isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get health status: {e}")
            return {
                "status": "unknown",
                "issues": [f"Error getting metrics: {str(e)}"],
                "timestamp": datetime.now().isoformat(),
            }

    async def start_metrics_collection(self):
        """Start automatic metrics collection."""
        if self._collecting:
            return

        self._collecting = True
        self._collection_task = asyncio.create_task(self._collection_loop())
        logger.info("Redis metrics collection started")

    async def stop_metrics_collection(self):
        """Stop automatic metrics collection."""
        if not self._collecting:
            return

        self._collecting = False

        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass

        logger.info("Redis metrics collection stopped")

    async def _collection_loop(self):
        """Background metrics collection loop."""
        while self._collecting:
            try:
                # Collect metrics
                metrics = await self.get_metrics()

                # Add to history
                self.metrics_history.append(metrics)

                # Limit history size
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history = self.metrics_history[
                        -self.max_history_size :
                    ]

                # Call metric callbacks
                for callback in self.metric_callbacks:
                    try:
                        await callback(metrics)
                    except Exception as e:
                        logger.error(f"Metric callback error: {e}")

                # Sleep until next collection
                await asyncio.sleep(self.collection_interval_seconds)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(60)  # Retry after 1 minute

    def add_custom_metric(self, name: str, value: Any):
        """Add custom metric."""
        self.custom_metrics[name] = value

    def add_metric_callback(self, callback: callable):
        """Add metric collection callback."""
        self.metric_callbacks.append(callback)

    def get_metrics_history(
        self, limit: int = 100, since: Optional[datetime] = None
    ) -> List[RedisMetricsReport]:
        """Get metrics history."""
        history = self.metrics_history

        if since:
            history = [m for m in history if m.timestamp >= since]

        return history[-limit:] if limit > 0 else history

    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary for specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]

        if not recent_metrics:
            return {}

        # Calculate averages and aggregates
        avg_ops_per_sec = sum(
            m.performance.instantaneous_ops_per_sec for m in recent_metrics
        ) / len(recent_metrics)
        avg_memory_usage = sum(m.memory.used_memory for m in recent_metrics) / len(
            recent_metrics
        )
        avg_hit_rate = sum(m.keyspace.hit_rate for m in recent_metrics) / len(
            recent_metrics
        )
        avg_connections = sum(
            m.connections.connected_clients for m in recent_metrics
        ) / len(recent_metrics)

        max_ops_per_sec = max(
            m.performance.instantaneous_ops_per_sec for m in recent_metrics
        )
        max_memory_usage = max(m.memory.used_memory for m in recent_metrics)
        max_connections = max(m.connections.connected_clients for m in recent_metrics)

        return {
            "period_hours": hours,
            "sample_count": len(recent_metrics),
            "performance": {
                "avg_ops_per_sec": avg_ops_per_sec,
                "max_ops_per_sec": max_ops_per_sec,
                "total_commands_processed": recent_metrics[
                    -1
                ].performance.total_commands_processed
                - recent_metrics[0].performance.total_commands_processed,
            },
            "memory": {
                "avg_usage_bytes": avg_memory_usage,
                "max_usage_bytes": max_memory_usage,
                "avg_usage_mb": avg_memory_usage / (1024 * 1024),
                "max_usage_mb": max_memory_usage / (1024 * 1024),
            },
            "keyspace": {
                "avg_hit_rate": avg_hit_rate,
                "total_keys": recent_metrics[-1].keyspace.total_keys,
            },
            "connections": {
                "avg_connections": avg_connections,
                "max_connections": max_connections,
            },
            "uptime": recent_metrics[-1].server.uptime_in_seconds,
        }

    async def export_metrics(
        self, format: str = "json", output_file: Optional[str] = None
    ) -> str:
        """Export metrics in specified format."""
        metrics = await self.get_metrics()

        if format == "json":
            data = {
                "timestamp": metrics.timestamp.isoformat(),
                "memory": {
                    "used_memory": metrics.memory.used_memory,
                    "used_memory_human": metrics.memory.used_memory_human,
                    "used_memory_rss": metrics.memory.used_memory_rss,
                    "used_memory_peak": metrics.memory.used_memory_peak,
                    "total_system_memory": metrics.memory.total_system_memory,
                    "memory_fragmentation_ratio": metrics.memory.memory_fragmentation_ratio,
                },
                "performance": {
                    "total_commands_processed": metrics.performance.total_commands_processed,
                    "instantaneous_ops_per_sec": metrics.performance.instantaneous_ops_per_sec,
                    "instantaneous_input_kbps": metrics.performance.instantaneous_input_kbps,
                    "instantaneous_output_kbps": metrics.performance.instantaneous_output_kbps,
                    "rejected_connections": metrics.performance.rejected_connections,
                },
                "keyspace": {
                    "total_keys": metrics.keyspace.total_keys,
                    "expires": metrics.keyspace.expires,
                    "hit_rate": metrics.keyspace.hit_rate,
                    "keyspace_hits": metrics.keyspace.keyspace_hits,
                    "keyspace_misses": metrics.keyspace.keyspace_misses,
                },
                "connections": {
                    "connected_clients": metrics.connections.connected_clients,
                    "blocked_clients": metrics.connections.blocked_clients,
                    "tracking_clients": metrics.connections.tracking_clients,
                },
                "server": {
                    "redis_version": metrics.server.redis_version,
                    "redis_mode": metrics.server.redis_mode,
                    "uptime_in_seconds": metrics.server.uptime_in_seconds,
                    "process_id": metrics.server.process_id,
                },
            }

            json_data = json.dumps(data, indent=2, default=str)

            if output_file:
                with open(output_file, "w") as f:
                    f.write(json_data)

            return json_data

        elif format == "prometheus":
            # Prometheus format
            lines = []

            # Memory metrics
            lines.append(f"# HELP redis_memory_used_bytes Memory used by Redis")
            lines.append(f"# TYPE redis_memory_used_bytes gauge")
            lines.append(f"redis_memory_used_bytes {metrics.memory.used_memory}")

            lines.append(
                f"# HELP redis_memory_fragmentation_ratio Memory fragmentation ratio"
            )
            lines.append(f"# TYPE redis_memory_fragmentation_ratio gauge")
            lines.append(
                f"redis_memory_fragmentation_ratio {metrics.memory.memory_fragmentation_ratio}"
            )

            # Performance metrics
            lines.append(f"# HELP redis_ops_per_sec Operations per second")
            lines.append(f"# TYPE redis_ops_per_sec gauge")
            lines.append(
                f"redis_ops_per_sec {metrics.performance.instantaneous_ops_per_sec}"
            )

            lines.append(
                f"# HELP redis_commands_processed_total Total commands processed"
            )
            lines.append(f"# TYPE redis_commands_processed_total counter")
            lines.append(
                f"redis_commands_processed_total {metrics.performance.total_commands_processed}"
            )

            # Keyspace metrics
            lines.append(f"# HELP redis_keys_total Total number of keys")
            lines.append(f"# TYPE redis_keys_total gauge")
            lines.append(f"redis_keys_total {metrics.keyspace.total_keys}")

            lines.append(f"# HELP redis_hit_rate Cache hit rate")
            lines.append(f"# TYPE redis_hit_rate gauge")
            lines.append(f"redis_hit_rate {metrics.keyspace.hit_rate}")

            # Connection metrics
            lines.append(f"# HELP redis_connected_clients Connected clients")
            lines.append(f"# TYPE redis_connected_clients gauge")
            lines.append(
                f"redis_connected_clients {metrics.connections.connected_clients}"
            )

            prometheus_data = "\n".join(lines)

            if output_file:
                with open(output_file, "w") as f:
                    f.write(prometheus_data)

            return prometheus_data

        else:
            raise ValueError(f"Unsupported format: {format}")

    def is_collecting(self) -> bool:
        """Check if metrics collection is active."""
        return self._collecting

    def get_collection_interval(self) -> int:
        """Get metrics collection interval."""
        return self.collection_interval_seconds

    def set_collection_interval(self, seconds: int):
        """Set metrics collection interval."""
        self.collection_interval_seconds = max(10, seconds)  # Minimum 10 seconds


# Global metrics instance
_redis_metrics = RedisMetrics()


def get_redis_metrics() -> RedisMetrics:
    """Get global Redis metrics instance."""
    return _redis_metrics


# Convenience functions
async def get_metrics() -> RedisMetricsReport:
    """Get current Redis metrics."""
    return await _redis_metrics.get_metrics()


async def get_memory_usage() -> Dict[str, Any]:
    """Get memory usage statistics."""
    return await _redis_metrics.get_memory_usage()


async def get_performance_stats() -> Dict[str, Any]:
    """Get performance statistics."""
    return await _redis_metrics.get_performance_stats()


async def get_health_status() -> Dict[str, Any]:
    """Get Redis health status."""
    return await _redis_metrics.get_health_status()


async def start_metrics_collection():
    """Start automatic metrics collection."""
    await _redis_metrics.start_metrics_collection()


async def stop_metrics_collection():
    """Stop automatic metrics collection."""
    await _redis_metrics.stop_metrics_collection()
