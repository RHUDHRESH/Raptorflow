"""
Enhanced metrics collection system for Raptorflow agents.
Includes request metrics, performance tracking, and comprehensive monitoring.
"""

import asyncio
import logging
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from enum import Enum

logger = logging.getLogger(__name__)


class TimeoutMetrics:
    """Enhanced timeout metrics collection and alerting."""
    
    def __init__(self):
        self.timeout_events = []
        self.timeout_stats = {
            "total_timeouts": 0,
            "recoveries": 0,
            "failures": 0,
            "by_operation": {},
            "by_agent": {},
            "recovery_success_rate": 0.0,
        }
        self.alert_thresholds = {
            "timeout_rate": 0.1,  # 10% timeout rate
            "failure_rate": 0.05,  # 5% failure rate
            "recovery_failure_rate": 0.2,  # 20% recovery failure rate
        }
        self.alerts_sent = []
    
    async def record_timeout(self, operation_type: str, agent_name: str, timeout_seconds: int, elapsed_seconds: float, recovery_strategies: List[str] = None):
        """Record a timeout event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "operation_type": operation_type,
            "agent_name": agent_name,
            "timeout_seconds": timeout_seconds,
            "elapsed_seconds": elapsed_seconds,
            "recovery_strategies": recovery_strategies or [],
        }
        
        self.timeout_events.append(event)
        self.timeout_stats["total_timeouts"] += 1
        
        # Update operation-specific stats
        if operation_type not in self.timeout_stats["by_operation"]:
            self.timeout_stats["by_operation"][operation_type] = {
                "count": 0, "recoveries": 0, "failures": 0
            }
        
        self.timeout_stats["by_operation"][operation_type]["count"] += 1
        
        # Update agent-specific stats
        if agent_name not in self.timeout_stats["by_agent"]:
            self.timeout_stats["by_agent"][agent_name] = {"count": 0, "recoveries": 0, "failures": 0}
        
        self.timeout_stats["by_agent"][agent_name]["count"] += 1
        
        # Check for alert conditions
        await self._check_alert_conditions()
    
    async def record_recovery(self, operation_type: str, agent_name: str, strategy: str, success: bool):
        """Record a recovery attempt."""
        self.timeout_stats["recoveries"] += 1
        
        if success:
            if operation_type in self.timeout_stats["by_operation"]:
                self.timeout_stats["by_operation"][operation_type]["recoveries"] += 1
            
            if agent_name in self.timeout_stats["by_agent"]:
                self.timeout_stats["by_agent"][agent_name]["recoveries"] += 1
        
        # Update recovery success rate
        total_recoveries = self.timeout_stats["recoveries"]
        total_timeouts = self.timeout_stats["total_timeouts"]
        if total_timeouts > 0:
            self.timeout_stats["recovery_success_rate"] = total_recoveries / total_timeouts
        
        await self._check_alert_conditions()
    
    async def record_failure(self, operation_type: str, agent_name: str, error_type: str):
        """Record a failure event."""
        self.timeout_stats["failures"] += 1
        
        if operation_type in self.timeout_stats["by_operation"]:
            self.timeout_stats["by_operation"][operation_type]["failures"] += 1
        
        if agent_name in self.timeout_stats["by_agent"]:
            self.timeout_stats["by_agent"][agent_name]["failures"] += 1
        
        await self._check_alert_conditions()
    
    async def _check_alert_conditions(self):
        """Check if alert conditions are met and send alerts."""
        total_operations = sum(
            stats.get("count", 0) 
            for stats in self.timeout_stats["by_operation"].values()
        )
        
        if total_operations == 0:
            return
        
        # Check timeout rate alert
        timeout_rate = self.timeout_stats["total_timeouts"] / total_operations
        if timeout_rate > self.alert_thresholds["timeout_rate"]:
            await self._send_alert(
                "high_timeout_rate",
                f"High timeout rate detected: {timeout_rate:.2%} ({self.timeout_stats['total_timeouts']}/{total_operations})"
            )
        
        # Check failure rate alert
        failure_rate = self.timeout_stats["failures"] / total_operations
        if failure_rate > self.alert_thresholds["failure_rate"]:
            await self._send_alert(
                "high_failure_rate",
                f"High failure rate detected: {failure_rate:.2%} ({self.timeout_stats['failures']}/{total_operations})"
            )
        
        # Check recovery failure rate alert
        total_recoveries = self.timeout_stats["recoveries"]
        if total_recoveries > 0:
            recovery_failure_rate = (total_recoveries - (self.timeout_stats["recoveries"] * self.timeout_stats["recovery_success_rate"])) / total_recoveries
            if recovery_failure_rate > self.alert_thresholds["recovery_failure_rate"]:
                await self._send_alert(
                    "high_recovery_failure_rate",
                    f"High recovery failure rate: {recovery_failure_rate:.2%}"
                )
    
    async def _send_alert(self, alert_type: str, message: str):
        """Send alert notification."""
        alert = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "message": message,
            "severity": self._get_alert_severity(alert_type),
            "timeout_stats": self.get_timeout_stats(),
        }
        
        self.alerts_sent.append(alert)
        logger.warning(f"TIMEOUT ALERT [{alert_type.upper()}]: {message}")
        
        # In a real implementation, this would send to monitoring system
        # For now, just log the alert
    
    def _get_alert_severity(self, alert_type: str) -> str:
        """Get alert severity level."""
        severity_map = {
            "high_timeout_rate": "warning",
            "high_failure_rate": "critical",
            "high_recovery_failure_rate": "error",
        }
        return severity_map.get(alert_type, "info")
    
    def get_timeout_stats(self) -> Dict[str, Any]:
        """Get comprehensive timeout statistics."""
        return {
            "stats": self.timeout_stats.copy(),
            "recent_events": self.timeout_events[-10:],  # Last 10 events
            "alerts_sent": len(self.alerts_sent),
            "alert_thresholds": self.alert_thresholds.copy(),
        }


class CacheMetrics:
    """Enhanced cache performance metrics collection and monitoring."""
    
    def __init__(self):
        self.cache_events = []
        self.cache_stats = {
            "total_requests": 0,
            "total_response_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
            "cache_sets": 0,
            "cache_evictions": 0,
            "cache_errors": 0,
            "hit_rate": 0.0,
            "avg_response_time": 0.0,
            "compression_ratio": 0.0,
            "memory_usage_mb": 0.0,
            "by_agent": {},
            "by_operation": {},
        }
        self.performance_alerts = {
            "low_hit_rate": 0.5,  # Hit rate below 50%
            "high_memory_usage": 0.8,  # Memory usage above 80%
            "high_error_rate": 0.1,  # Error rate above 10%
        }
        self.alerts_sent = []
    
    async def record_cache_request(self, agent_name: str, operation_type: str, hit: bool, response_time: float):
        """Record a cache request event."""
        self.cache_stats["total_requests"] += 1
        self.cache_stats["total_response_time"] += response_time
        self.cache_stats["avg_response_time"] = self.cache_stats["total_response_time"] / self.cache_stats["total_requests"]
        
        if hit:
            self.cache_stats["cache_hits"] += 1
        else:
            self.cache_stats["cache_misses"] += 1
        
        # Update response time average
        current_avg = self.cache_stats["avg_response_time"]
        self.cache_stats["avg_response_time"] = (current_avg + response_time) / 2
        
        # Update agent-specific stats
        if agent_name not in self.cache_stats["by_agent"]:
            self.cache_stats["by_agent"][agent_name] = {
                "requests": 0, "hits": 0, "misses": 0, "avg_response_time": 0.0
            }
        
        agent_stats = self.cache_stats["by_agent"][agent_name]
        agent_stats["requests"] += 1
        
        if hit:
            agent_stats["hits"] += 1
        else:
            agent_stats["misses"] += 1
        
        # Update operation-specific stats
        if operation_type not in self.cache_stats["by_operation"]:
            self.cache_stats["by_operation"][operation_type] = {
                "requests": 0, "hits": 0, "misses": 0
            }
        
        self.cache_stats["by_operation"][operation_type]["requests"] += 1
        
        if hit:
            self.cache_stats["by_operation"][operation_type]["hits"] += 1
        else:
            self.cache_stats["by_operation"][operation_type]["misses"] += 1
        
        # Check for alert conditions
        await self._check_performance_alerts()
    
    async def record_cache_set(self, agent_name: str, operation_type: str, size_bytes: int, compressed: bool = False):
        """Record a cache set event."""
        self.cache_stats["cache_sets"] += 1
        
        # Update compression metrics
        if compressed:
            # Simple compression ratio tracking
            current_ratio = self.cache_stats["compression_ratio"]
            self.cache_stats["compression_ratio"] = (current_ratio + 0.1) / 2  # Assume 10% compression
        
        # Check for alert conditions
        await self._check_performance_alerts()
    
    async def record_cache_eviction(self, agent_name: str, reason: str = "lru"):
        """Record a cache eviction event."""
        self.cache_stats["cache_evictions"] += 1
        
        # Update agent-specific eviction stats
        if agent_name not in self.cache_stats["by_agent"]:
            self.cache_stats["by_agent"][agent_name] = {
                "requests": 0, "hits": 0, "misses": 0, "avg_response_time": 0.0, "evictions": 0
            }
        
        if "evictions" not in self.cache_stats["by_agent"][agent_name]:
            self.cache_stats["by_agent"][agent_name]["evictions"] = 0
        
        self.cache_stats["by_agent"][agent_name]["evictions"] += 1
        
        logger.info(f"Cache eviction for agent '{agent_name}': {reason}")
        
        # Check for alert conditions
        await self._check_performance_alerts()
    
    async def record_cache_error(self, agent_name: str, operation_type: str, error_type: str):
        """Record a cache error event."""
        self.cache_stats["cache_errors"] += 1
        
        # Update operation-specific error stats
        if operation_type not in self.cache_stats["by_operation"]:
            self.cache_stats["by_operation"][operation_type]["errors"] = 0
        
        self.cache_stats["by_operation"][operation_type]["errors"] += 1
        
        logger.error(f"Cache error for agent '{agent_name}' ({operation_type}): {error_type}")
        
        # Check for alert conditions
        await self._check_performance_alerts()
    
    async def update_memory_usage(self, memory_usage_mb: float):
        """Update memory usage and check for alerts."""
        self.cache_stats["memory_usage_mb"] = memory_usage_mb
        
        # Check for memory usage alert
        if memory_usage_mb > 400:  # Assume 400MB limit
            await self._send_performance_alert(
                "high_memory_usage",
                f"High memory usage: {memory_usage_mb:.1f}MB"
            )
    
    async def _check_performance_alerts(self):
        """Check if performance alert conditions are met."""
        total_requests = self.cache_stats["total_requests"]
        
        if total_requests == 0:
            return
        
        # Calculate hit rate
        hit_rate = self.cache_stats["cache_hits"] / total_requests if total_requests > 0 else 0
        self.cache_stats["hit_rate"] = hit_rate
        
        # Check hit rate alert
        if hit_rate < self.performance_alerts["low_hit_rate"]:
            await self._send_performance_alert(
                "low_hit_rate",
                f"Low cache hit rate: {hit_rate:.2%}"
            )
        
        # Check error rate alert
        error_rate = self.cache_stats["cache_errors"] / total_requests if total_requests > 0 else 0
        if error_rate > self.performance_alerts["high_error_rate"]:
            await self._send_performance_alert(
                "high_error_rate",
                f"High cache error rate: {error_rate:.2%}"
            )
    
    async def _send_performance_alert(self, alert_type: str, message: str):
        """Send performance alert notification."""
        alert = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "message": message,
            "severity": "warning",
            "cache_stats": self.get_cache_stats(),
        }
        
        self.alerts_sent.append(alert)
        logger.warning(f"CACHE PERFORMANCE ALERT [{alert_type.upper()}]: {message}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        # Calculate hit rates by agent
        agent_hit_rates = {}
        for agent_name, stats in self.cache_stats["by_agent"].items():
            total_requests = stats.get("requests", 0)
            if total_requests > 0:
                hit_rate = stats.get("hits", 0) / total_requests
                agent_hit_rates[agent_name] = hit_rate
        
        return {
            "stats": self.cache_stats.copy(),
            "agent_hit_rates": agent_hit_rates,
            "alerts_sent": len(self.alerts_sent),
            "performance_alerts": self.performance_alerts.copy(),
        }


class MetricType(Enum):
    SESSION = "session"
    USER_BEHAVIOR = "user_behavior"
    SYSTEM_RESOURCE = "system_resource"
    BUSINESS = "business"
    CUSTOM = "custom"


class RequestStatus(Enum):
    """Request execution status."""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    SECURITY_BLOCKED = "security_blocked"


@dataclass
class MetricData:
    """Single metric data point."""
    
    timestamp: datetime
    metric_type: MetricType
    value: float
    unit: str
    agent_id: Optional[str] = None
    workspace_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "metric_type": self.metric_type.value,
            "agent_id": self.agent_id,
            "workspace_id": self.workspace_id,
            "value": self.value,
            "unit": self.unit,
            "metadata": self.metadata,
        }


@dataclass
class RequestMetric:
    """Individual request metric for comprehensive tracking."""
    
    timestamp: datetime
    request_id: str
    agent_name: str
    user_id: str
    workspace_id: str
    session_id: str
    request_length: int
    response_length: int
    execution_time: float
    status: RequestStatus
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    routing_time: Optional[float] = None
    validation_time: Optional[float] = None
    security_time: Optional[float] = None
    llm_tokens_used: Optional[int] = None
    tools_used: List[str] = field(default_factory=list)
    memory_operations: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "request_id": self.request_id,
            "agent_name": self.agent_name,
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
            "session_id": self.session_id,
            "request_length": self.request_length,
            "response_length": self.response_length,
            "execution_time": self.execution_time,
            "status": self.status.value,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "client_ip": self.client_ip,
            "user_agent": self.user_agent,
            "routing_time": self.routing_time,
            "validation_time": self.validation_time,
            "security_time": self.security_time,
            "llm_tokens_used": self.llm_tokens_used,
            "tools_used": self.tools_used,
            "memory_operations": self.memory_operations,
        }


@dataclass
class AgentMetrics:
    """Metrics specific to an agent."""
    
    agent_id: str
    workspace_id: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_execution_time_ms: float = 0.0
    total_tokens_used: int = 0
    total_cost_usd: float = 0.0
    last_execution_time: Optional[datetime] = None
    error_rate: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "agent_id": self.agent_id,
            "workspace_id": self.workspace_id,
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "failed_executions": self.failed_executions,
            "success_rate": (
                self.successful_executions / self.total_executions * 100
                if self.total_executions > 0 else 0
            ),
            "error_rate": self.error_rate,
            "average_execution_time_ms": self.average_execution_time_ms,
            "total_tokens_used": self.total_tokens_used,
            "total_cost_usd": self.total_cost_usd,
            "last_execution_time": (
                self.last_execution_time.isoformat() if self.last_execution_time else None
            ),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class MetricsCollector:
    """Simple but effective metrics collector for Raptorflow agents."""
    
    def __init__(self, max_history_size: int = 10000):
        self.max_history_size = max_history_size
        
        # In-memory storage
        self.metrics_history: deque = deque(maxlen=max_history_size)
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        
        # Global counters
        self.global_counters = defaultdict(float)
        self.global_start_time = time.time()
        
        # Background tasks
        self._background_tasks: set = set()
        self._running = False
        
        logger.info(f"Metrics collector initialized with max history size: {max_history_size}")
    
    async def start(self):
        """Start the metrics collector background tasks."""
        if self._running:
            return
        
        self._running = True
        self._background_tasks.add(asyncio.create_task(self._cleanup_loop()))
        self._background_tasks.add(asyncio.create_task(self._persist_loop()))
        logger.info("Metrics collector started")
    
    async def stop(self):
        """Stop the metrics collector background tasks."""
        self._running = False
        
        for task in self._background_tasks:
            task.cancel()
        
        await asyncio.gather(*self._background_tasks, return_exceptions=True)
        self._background_tasks.clear()
        logger.info("Metrics collector stopped")
    
    def record_execution(
        self,
        agent_id: str,
        workspace_id: str,
        execution_time_ms: int,
        success: bool,
        tokens_used: int = 0,
        cost_usd: float = 0.0,
        error_message: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ):
        """Record an agent execution."""
        try:
            # Update agent metrics
            if agent_id not in self.agent_metrics:
                self.agent_metrics[agent_id] = AgentMetrics(
                    agent_id=agent_id,
                    workspace_id=workspace_id
                )
            
            agent_metrics = self.agent_metrics[agent_id]
            agent_metrics.total_executions += 1
            agent_metrics.updated_at = datetime.now()
            
            if success:
                agent_metrics.successful_executions += 1
            else:
                agent_metrics.failed_executions += 1
                agent_metrics.error_rate = (
                    agent_metrics.failed_executions / agent_metrics.total_executions
                )
            
            # Update average execution time
            if agent_metrics.total_executions > 0:
                agent_metrics.average_execution_time_ms = (
                    (agent_metrics.average_execution_time_ms * (agent_metrics.total_executions - 1) + execution_time_ms)
                    / agent_metrics.total_executions
                )
            
            # Update tokens and cost
            agent_metrics.total_tokens_used += tokens_used
            agent_metrics.total_cost_usd += cost_usd
            
            # Update last execution time
            agent_metrics.last_execution_time = datetime.now()
            
            # Record metric
            metric = MetricData(
                timestamp=datetime.now(),
                metric_type=MetricType.AGENT_EXECUTION,
                agent_id=agent_id,
                workspace_id=workspace_id,
                value=execution_time_ms,
                unit="ms",
                metadata={
                    "success": success,
                    "tokens_used": tokens_used,
                    "cost_usd": cost_usd,
                    "error_message": error_message,
                    **(metadata or {})
                }
            )
            
            self.metrics_history.append(metric)
            
            # Update global counters
            self.global_counters["total_executions"] += 1
            if success:
                self.global_counters["successful_executions"] += 1
            else:
                self.global_counters["failed_executions"] += 1
            
            logger.info(f"Recorded execution for agent {agent_id}: {success} in {execution_time_ms}ms")
            
        except Exception as e:
            logger.error(f"Failed to record execution for agent {agent_id}: {e}")
    
    def record_llm_usage(
        self,
        agent_id: str,
        workspace_id: str,
        model_tier: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        latency_ms: int,
        metadata: Dict[str, Any] = None
    ):
        """Record LLM usage metrics."""
        try:
            # Record metric
            metric = MetricData(
                timestamp=datetime.now(),
                metric_type=MetricType.LLM_USAGE,
                agent_id=agent_id,
                workspace_id=workspace_id,
                value=cost_usd,
                unit="usd",
                metadata={
                    "model_tier": model_tier,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "latency_ms": latency_ms,
                    "total_tokens": input_tokens + output_tokens,
                    **(metadata or {})
                }
            )
            
            self.metrics_history.append(metric)
            
            # Update global counters
            self.global_counters["total_llm_cost"] += cost_usd
            self.global_counters["total_tokens"] += input_tokens + output_tokens
            
            logger.info(f"Recorded LLM usage for agent {agent_id}: {cost_usd} USD, {input_tokens + output_tokens} tokens")
            
        except Exception as e:
            logger.error(f"Failed to record LLM usage for agent {agent_id}: {e}")
    
    def record_tool_usage(
        self,
        agent_id: str,
        workspace_id: str,
        tool_name: str,
        execution_time_ms: int,
        success: bool,
        metadata: Dict[str, Any] = None
    ):
        """Record tool usage metrics."""
        try:
            # Record metric
            metric = MetricData(
                timestamp=datetime.now(),
                metric_type=MetricType.TOOL_USAGE,
                agent_id=agent_id,
                workspace_id=workspace_id,
                value=execution_time_ms,
                unit="ms",
                metadata={
                    "tool_name": tool_name,
                    "success": success,
                    **(metadata or {})
                }
            )
            
            self.metrics_history.append(metric)
            
            # Update global counters
            self.global_counters["total_tool_executions"] += 1
            if success:
                self.global_counters["successful_tool_executions"] += 1
            else:
                self.global_counters["failed_tool_executions"] += 1
            
            logger.info(f"Recorded tool usage for agent {agent_id}: {tool_name} in {execution_time_ms}ms")
            
        except Exception as e:
            logger.error(f"Failed to record tool usage for agent {agent_id}: {e}")
    
    def record_error(
        self,
        agent_id: str,
        workspace_id: str,
        error_type: str,
        error_message: str,
        metadata: Dict[str, Any] = None
    ):
        """Record an error metric."""
        try:
            # Record metric
            metric = MetricData(
                timestamp=datetime.now(),
                metric_type=MetricType.ERROR_RATE,
                agent_id=agent_id,
                workspace_id=workspace_id,
                value=1.0,
                unit="count",
                metadata={
                    "error_type": error_type,
                    "error_message": error_message,
                    **(metadata or {})
                }
            )
            
            self.metrics_history.append(metric)
            
            # Update global counters
            self.global_counters["total_errors"] += 1
            
            logger.warning(f"Recorded error for agent {agent_id}: {error_type} - {error_message}")
            
        except Exception as e:
            logger.error(f"Failed to record error for agent {agent_id}: {e}")
    
    def get_agent_metrics(self, agent_id: str) -> Optional[AgentMetrics]:
        """Get metrics for a specific agent."""
        return self.agent_metrics.get(agent_id)
    
    def get_global_metrics(self) -> Dict[str, Any]:
        """Get global metrics summary."""
        uptime = time.time() - self.global_start_time
        
        return {
            "uptime_seconds": int(uptime),
            "uptime_formatted": str(timedelta(seconds=int(uptime))),
            "total_metrics_recorded": len(self.metrics_history),
            "global_counters": dict(self.global_counters),
            "active_agents": len(self.agent_metrics),
            "metrics_history_size": len(self.metrics_history),
        }
    
    def get_metrics_history(
        self,
        metric_type: Optional[MetricType] = None,
        agent_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: int = 1000,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get metrics history with optional filtering."""
        try:
            # Filter metrics
            filtered_metrics = []
            for metric in self.metrics_history:
                if metric_type and metric.metric_type != metric_type:
                    continue
                if agent_id and metric.agent_id != agent_id:
                    continue
                if workspace_id and metric.workspace_id != workspace_id:
                    continue
                
                filtered_metrics.append(metric.to_dict())
            
            # Apply pagination
            start_idx = offset
            end_idx = start_idx + limit
            paginated_metrics = filtered_metrics[start_idx:end_idx]
            
            return paginated_metrics
            
        except Exception as e:
            logger.error(f"Failed to get metrics history: {e}")
            return []
    
    def get_performance_summary(
        self,
        time_window_minutes: int = 60
    ) -> Dict[str, Any]:
        """Get performance summary for the last N minutes."""
        try:
            cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
            
            # Filter recent metrics
            recent_metrics = []
            for metric in self.metrics_history:
                if metric.timestamp >= cutoff_time:
                    recent_metrics.append(metric)
            
            if not recent_metrics:
                return {"message": f"No metrics found in the last {time_window_minutes} minutes"}
            
            # Calculate performance metrics
            execution_times = [
                metric.value for metric in recent_metrics
                if metric.metric_type == MetricType.AGENT_EXECUTION
            ]
            
            llm_costs = [
                metric.value for metric in recent_metrics
                if metric.metric_type == MetricType.LLM_USAGE
            ]
            
            tool_times = [
                metric.value for metric in recent_metrics
                if metric.metric_type == MetricType.TOOL_USAGE
            ]
            
            # Calculate statistics
            avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
            total_llm_cost = sum(llm_costs) if llm_costs else 0
            avg_tool_time = sum(tool_times) / len(tool_times) if tool_times else 0
            
            return {
                "time_window_minutes": time_window_minutes,
                "total_metrics": len(recent_metrics),
                "performance": {
                    "average_execution_time_ms": round(avg_execution_time, 2),
                    "total_llm_cost_usd": round(total_llm_cost, 4),
                    "average_tool_time_ms": round(avg_tool_time, 2),
                    "total_executions": len(execution_times),
                    "total_tool_executions": len(tool_times),
                },
                "timestamp_range": {
                    "start": min(metric.timestamp for metric in recent_metrics).isoformat(),
                    "end": max(metric.timestamp for metric in recent_metrics).isoformat(),
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            return {"error": str(e)}
    
    async def _cleanup_loop(self):
        """Background cleanup of old metrics."""
        while self._running:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Keep only last N metrics
                if len(self.metrics_history) > self.max_history_size:
                    # Calculate how many to remove
                    to_remove = len(self.metrics_history) - self.max_history_size
                    
                    # Remove oldest metrics
                    for _ in range(to_remove):
                        self.metrics_history.popleft()
                    
                    logger.debug(f"Cleaned up {to_remove} old metrics entries")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics cleanup error: {e}")
    
    async def _persist_loop(self):
        """Background persistence of metrics (placeholder for now)."""
        while self._running:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                # In a real implementation, this would persist to database
                # For now, just log that we would persist
                metrics_count = len(self.metrics_history)
                agent_count = len(self.agent_metrics)
                
                logger.debug(f"Would persist {metrics_count} metrics for {agent_count} agents")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics persistence error: {e}")


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector(max_history_size: int = 10000) -> MetricsCollector:
    """Get or create global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector(max_history_size)
    return _metrics_collector


async def start_metrics_collector():
    """Start the global metrics collector."""
    collector = get_metrics_collector()
    await collector.start()


async def stop_metrics_collector():
    """Stop the global metrics collector."""
    collector = get_metrics_collector()
    if collector:
        await collector.stop()


class RequestMetricsCollector:
    """Collects and analyzes request metrics for comprehensive monitoring."""
    
    def __init__(self, max_metrics: int = 10000, cleanup_interval: int = 3600):
        self.max_metrics = max_metrics
        self.cleanup_interval = cleanup_interval
        self.metrics: deque[RequestMetric] = deque(maxlen=max_metrics)
        self.last_cleanup = datetime.now()
        
        # Performance tracking
        self.agent_performance: Dict[str, List[float]] = defaultdict(list)
        self.user_performance: Dict[str, List[float]] = defaultdict(list)
        self.workspace_performance: Dict[str, List[float]] = defaultdict(list)
        
        # Error tracking
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.error_details: Dict[str, List[RequestMetric]] = defaultdict(list)
        
        # Rate limiting tracking
        self.request_counts: Dict[str, List[datetime]] = defaultdict(list)
        self.blocked_entities: Dict[str, Set[str]] = {
            "ips": set(),
            "users": set(),
            "workspaces": set(),
        }
        
        # Real-time statistics
        self.current_requests: Dict[str, datetime] = {}
        self.concurrent_counts: Dict[str, int] = defaultdict(int)
        
        # Performance thresholds
        self.performance_thresholds = {
            "slow_request": 5.0,  # seconds
            "very_slow_request": 10.0,  # seconds
            "large_request": 10000,  # characters
            "large_response": 50000,  # characters
            "high_token_usage": 2000,  # tokens
        }
    
    def start_request(
        self,
        request_id: str,
        agent_name: str,
        user_id: str,
        workspace_id: str,
        session_id: str,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> datetime:
        """Start tracking a request."""
        start_time = datetime.now()
        self.current_requests[request_id] = start_time
        
        # Update concurrent counts
        for entity_id in [f"user:{user_id}", f"workspace:{workspace_id}"]:
            self.concurrent_counts[entity_id] += 1
        
        logger.debug(f"Started tracking request {request_id} for agent {agent_name}")
        return start_time
    
    def end_request(
        self,
        request_id: str,
        agent_name: str,
        user_id: str,
        workspace_id: str,
        session_id: str,
        request_length: int,
        response_length: int,
        status: RequestStatus,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        routing_time: Optional[float] = None,
        validation_time: Optional[float] = None,
        security_time: Optional[float] = None,
        llm_tokens_used: Optional[int] = None,
        tools_used: Optional[List[str]] = None,
        memory_operations: int = 0,
    ) -> Optional[RequestMetric]:
        """End tracking a request and record metrics."""
        try:
            # Calculate execution time
            start_time = self.current_requests.pop(request_id, None)
            if not start_time:
                logger.warning(f"Request {request_id} not found in current requests")
                return None
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Update concurrent counts
            for entity_id in [f"user:{user_id}", f"workspace:{workspace_id}"]:
                self.concurrent_counts[entity_id] = max(
                    self.concurrent_counts[entity_id] - 1, 0
                )
            
            # Create metric
            metric = RequestMetric(
                timestamp=start_time,
                request_id=request_id,
                agent_name=agent_name,
                user_id=user_id,
                workspace_id=workspace_id,
                session_id=session_id,
                request_length=request_length,
                response_length=response_length,
                execution_time=execution_time,
                status=status,
                error_code=error_code,
                error_message=error_message,
                client_ip=client_ip,
                user_agent=user_agent,
                routing_time=routing_time,
                validation_time=validation_time,
                security_time=security_time,
                llm_tokens_used=llm_tokens_used,
                tools_used=tools_used or [],
                memory_operations=memory_operations,
            )
            
            # Store metric
            self.metrics.append(metric)
            
            # Update performance tracking
            self.agent_performance[agent_name].append(execution_time)
            self.user_performance[user_id].append(execution_time)
            self.workspace_performance[workspace_id].append(execution_time)
            
            # Update error tracking
            if status != RequestStatus.SUCCESS:
                error_key = error_code or status.value
                self.error_counts[error_key] += 1
                self.error_details[error_key].append(metric)
            
            # Update rate limiting tracking
            now = datetime.now()
            for entity_id in [f"ip:{client_ip}", f"user:{user_id}", f"workspace:{workspace_id}"]:
                if entity_id and not entity_id.endswith(":"):
                    self.request_counts[entity_id].append(now)
            
            # Log performance issues
            self._check_performance_issues(metric)
            
            # Cleanup old metrics
            self._cleanup_old_metrics()
            
            logger.debug(f"Recorded metric for request {request_id}: {execution_time:.3f}s")
            return metric
            
        except Exception as e:
            logger.error(f"Failed to record metric for request {request_id}: {e}")
            return None
    
    def _check_performance_issues(self, metric: RequestMetric):
        """Check for performance issues and log them."""
        issues = []
        
        if metric.execution_time > self.performance_thresholds["very_slow_request"]:
            issues.append(f"Very slow request: {metric.execution_time:.3f}s")
        elif metric.execution_time > self.performance_thresholds["slow_request"]:
            issues.append(f"Slow request: {metric.execution_time:.3f}s")
        
        if metric.request_length > self.performance_thresholds["large_request"]:
            issues.append(f"Large request: {metric.request_length} chars")
        
        if metric.response_length > self.performance_thresholds["large_response"]:
            issues.append(f"Large response: {metric.response_length} chars")
        
        if metric.llm_tokens_used and metric.llm_tokens_used > self.performance_thresholds["high_token_usage"]:
            issues.append(f"High token usage: {metric.llm_tokens_used} tokens")
        
        if issues:
            logger.warning(
                f"Performance issues for request {metric.request_id} "
                f"(agent: {metric.agent_name}, user: {metric.user_id}): "
                f"; ".join(issues)
            )
    
    def _cleanup_old_metrics(self):
        """Clean up old metrics and request counts."""
        now = datetime.now()
        
        # Clean up old request counts (older than 1 hour)
        cutoff = now - timedelta(hours=1)
        for entity_id in list(self.request_counts.keys()):
            self.request_counts[entity_id] = [
                req_time for req_time in self.request_counts[entity_id]
                if req_time > cutoff
            ]
            if not self.request_counts[entity_id]:
                del self.request_counts[entity_id]
        
        # Periodic cleanup of old metrics
        if (now - self.last_cleanup).total_seconds() > self.cleanup_interval:
            self.last_cleanup = now
            logger.info(f"Performed metrics cleanup. Total metrics: {len(self.metrics)}")
    
    def get_metrics_summary(
        self,
        hours: int = 24,
        agent_name: Optional[str] = None,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get metrics summary with optional filtering."""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        # Filter metrics
        filtered_metrics = [
            metric for metric in self.metrics
            if metric.timestamp >= cutoff
            and (agent_name is None or metric.agent_name == agent_name)
            and (user_id is None or metric.user_id == user_id)
            and (workspace_id is None or metric.workspace_id == workspace_id)
        ]
        
        if not filtered_metrics:
            return {"message": "No metrics found for the specified criteria"}
        
        # Calculate statistics
        total_requests = len(filtered_metrics)
        successful_requests = sum(1 for m in filtered_metrics if m.status == RequestStatus.SUCCESS)
        error_requests = total_requests - successful_requests
        
        execution_times = [m.execution_time for m in filtered_metrics]
        avg_execution_time = sum(execution_times) / len(execution_times)
        min_execution_time = min(execution_times)
        max_execution_time = max(execution_times)
        
        # Calculate percentiles
        sorted_times = sorted(execution_times)
        p50 = sorted_times[len(sorted_times) // 2]
        p95 = sorted_times[int(len(sorted_times) * 0.95)]
        p99 = sorted_times[int(len(sorted_times) * 0.99)]
        
        return {
            "summary": {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "error_requests": error_requests,
                "success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0,
                "time_period_hours": hours,
            },
            "performance": {
                "avg_execution_time": avg_execution_time,
                "min_execution_time": min_execution_time,
                "max_execution_time": max_execution_time,
                "p50_execution_time": p50,
                "p95_execution_time": p95,
                "p99_execution_time": p99,
            },
            "current_concurrent_requests": dict(self.concurrent_counts),
            "blocked_entities": {
                "ips": len(self.blocked_entities["ips"]),
                "users": len(self.blocked_entities["users"]),
                "workspaces": len(self.blocked_entities["workspaces"]),
            },
        }


# Global request metrics collector instance
_request_metrics_collector: Optional[RequestMetricsCollector] = None


def get_request_metrics_collector() -> RequestMetricsCollector:
    """Get the global request metrics collector instance."""
    global _request_metrics_collector
    if _request_metrics_collector is None:
        _request_metrics_collector = RequestMetricsCollector()
    return _request_metrics_collector


def start_request_tracking(
    request_id: str,
    agent_name: str,
    user_id: str,
    workspace_id: str,
    session_id: str,
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> datetime:
    """Start tracking a request (convenience function)."""
    collector = get_request_metrics_collector()
    return collector.start_request(
        request_id, agent_name, user_id, workspace_id, session_id, client_ip, user_agent
    )


def end_request_tracking(
    request_id: str,
    agent_name: str,
    user_id: str,
    workspace_id: str,
    session_id: str,
    request_length: int,
    response_length: int,
    status: RequestStatus,
    error_code: Optional[str] = None,
    error_message: Optional[str] = None,
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    routing_time: Optional[float] = None,
    validation_time: Optional[float] = None,
    security_time: Optional[float] = None,
    llm_tokens_used: Optional[int] = None,
    tools_used: Optional[List[str]] = None,
    memory_operations: int = 0,
) -> Optional[RequestMetric]:
    """End tracking a request (convenience function)."""
    collector = get_request_metrics_collector()
    return collector.end_request(
        request_id, agent_name, user_id, workspace_id, session_id,
        request_length, response_length, status, error_code, error_message,
        client_ip, user_agent, routing_time, validation_time, security_time,
        llm_tokens_used, tools_used, memory_operations
    )


def get_request_metrics_summary(
    hours: int = 24,
    agent_name: Optional[str] = None,
    user_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Get request metrics summary (convenience function)."""
    collector = get_request_metrics_collector()
    return collector.get_metrics_summary(hours, agent_name, user_id, workspace_id)


def get_analytics_manager():
    """Get analytics manager instance (backward compatibility)."""
    return get_request_metrics_collector()
