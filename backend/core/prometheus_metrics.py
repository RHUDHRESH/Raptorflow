"""
Prometheus metrics collection for RaptorFlow Backend
Comprehensive monitoring with custom metrics and exporters
"""

import asyncio
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from prometheus_client import Counter, Gauge, Histogram, Info, generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse

logger = logging.getLogger(__name__)


class PrometheusMetrics:
    """Prometheus metrics collection system"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.registry = CollectorRegistry()
        
        # Initialize metrics
        self._initialize_metrics()
        
        # Add metrics endpoint
        self._add_metrics_endpoint()
        
        # Start background collection
        self._start_background_collection()
    
    def _initialize_metrics(self) -> None:
        """Initialize all Prometheus metrics"""
        
        # Application info
        self.app_info = Info(
            'raptorflow_application_info',
            'RaptorFlow application information',
            registry=self.registry
        )
        self.app_info.info({
            'version': os.getenv("APP_VERSION", "1.0.0"),
            'environment': os.getenv("ENVIRONMENT", "development"),
            'build_date': datetime.utcnow().isoformat(),
            'python_version': os.sys.version,
        })
        
        # HTTP request metrics
        self.http_requests_total = Counter(
            'raptorflow_http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code'],
            registry=self.registry
        )
        
        self.http_request_duration = Histogram(
            'raptorflow_http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry
        )
        
        self.http_request_size = Histogram(
            'raptorflow_http_request_size_bytes',
            'HTTP request size in bytes',
            ['method', 'endpoint'],
            buckets=[100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000],
            registry=self.registry
        )
        
        self.http_response_size = Histogram(
            'raptorflow_http_response_size_bytes',
            'HTTP response size in bytes',
            ['method', 'endpoint'],
            buckets=[100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000],
            registry=self.registry
        )
        
        # Database metrics
        self.database_connections_active = Gauge(
            'raptorflow_database_connections_active',
            'Number of active database connections',
            ['database'],
            registry=self.registry
        )
        
        self.database_connections_total = Counter(
            'raptorflow_database_connections_total',
            'Total database connections created',
            ['database'],
            registry=self.registry
        )
        
        self.database_query_duration = Histogram(
            'raptorflow_database_query_duration_seconds',
            'Database query duration in seconds',
            ['database', 'operation'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
            registry=self.registry
        )
        
        self.database_query_total = Counter(
            'raptorflow_database_queries_total',
            'Total database queries',
            ['database', 'operation', 'status'],
            registry=self.registry
        )
        
        # Redis metrics
        self.redis_connections_active = Gauge(
            'raptorflow_redis_connections_active',
            'Number of active Redis connections',
            registry=self.registry
        )
        
        self.redis_commands_total = Counter(
            'raptorflow_redis_commands_total',
            'Total Redis commands',
            ['command', 'status'],
            registry=self.registry
        )
        
        self.redis_memory_usage = Gauge(
            'raptorflow_redis_memory_usage_bytes',
            'Redis memory usage in bytes',
            registry=self.registry
        )
        
        # Cache metrics
        self.cache_operations_total = Counter(
            'raptorflow_cache_operations_total',
            'Total cache operations',
            ['operation', 'cache_type', 'status'],
            registry=self.registry
        )
        
        self.cache_hit_ratio = Gauge(
            'raptorflow_cache_hit_ratio',
            'Cache hit ratio',
            ['cache_type'],
            registry=self.registry
        )
        
        # Circuit breaker metrics
        self.circuit_breaker_state = Gauge(
            'raptorflow_circuit_breaker_state',
            'Circuit breaker state (0=closed, 1=open, 2=half_open)',
            ['service'],
            registry=self.registry
        )
        
        self.circuit_breaker_failures_total = Counter(
            'raptorflow_circuit_breaker_failures_total',
            'Total circuit breaker failures',
            ['service'],
            registry=self.registry
        )
        
        # Rate limiting metrics
        self.rate_limit_requests_total = Counter(
            'raptorflow_rate_limit_requests_total',
            'Total rate limit requests',
            ['user_id', 'endpoint', 'status'],
            registry=self.registry
        )
        
        # Error metrics
        self.errors_total = Counter(
            'raptorflow_errors_total',
            'Total errors',
            ['type', 'endpoint', 'severity'],
            registry=self.registry
        )
        
        # Business metrics
        self.users_total = Gauge(
            'raptorflow_users_total',
            'Total number of users',
            ['status'],
            registry=self.registry
        )
        
        self.workspaces_total = Gauge(
            'raptorflow_workspaces_total',
            'Total number of workspaces',
            ['status'],
            registry=self.registry
        )
        
        self.icps_total = Gauge(
            'raptorflow_icps_total',
            'Total number of ICPs',
            ['status'],
            registry=self.registry
        )
        
        # System metrics
        self.system_cpu_usage = Gauge(
            'raptorflow_system_cpu_usage_percent',
            'System CPU usage percentage',
            registry=self.registry
        )
        
        self.system_memory_usage = Gauge(
            'raptorflow_system_memory_usage_bytes',
            'System memory usage in bytes',
            registry=self.registry
        )
        
        self.system_disk_usage = Gauge(
            'raptorflow_system_disk_usage_bytes',
            'System disk usage in bytes',
            registry=self.registry
        )
        
        # Performance metrics
        self.response_time_p95 = Gauge(
            'raptorflow_response_time_p95_seconds',
            '95th percentile response time',
            ['endpoint'],
            registry=self.registry
        )
        
        self.throughput = Gauge(
            'raptorflow_throughput_requests_per_second',
            'Requests per second',
            ['endpoint'],
            registry=self.registry
        )
    
    def _add_metrics_endpoint(self) -> None:
        """Add Prometheus metrics endpoint"""
        
        @self.app.get("/metrics")
        async def metrics():
            """Prometheus metrics endpoint"""
            try:
                # Update dynamic metrics before serving
                await self._update_dynamic_metrics()
                
                # Generate metrics
                metrics_data = generate_latest(self.registry)
                
                return PlainTextResponse(
                    content=metrics_data,
                    media_type=CONTENT_TYPE_LATEST
                )
                
            except Exception as e:
                logger.error(f"Failed to generate metrics: {e}")
                return PlainTextResponse(
                    content="# Error generating metrics",
                    media_type=CONTENT_TYPE_LATEST
                )
        
        @self.app.get("/metrics/info")
        async def metrics_info():
            """Metrics information endpoint"""
            return {
                "metrics_enabled": True,
                "registry_size": len(self.registry._collector_to_names),
                "last_update": datetime.utcnow().isoformat(),
                "categories": [
                    "http", "database", "redis", "cache", 
                    "circuit_breaker", "rate_limiting", "errors",
                    "business", "system", "performance"
                ]
            }
    
    def _start_background_collection(self) -> None:
        """Start background metrics collection"""
        asyncio.create_task(self._background_collection_loop())
    
    async def _background_collection_loop(self) -> None:
        """Background loop for collecting metrics"""
        while True:
            try:
                await self._update_dynamic_metrics()
                await asyncio.sleep(30)  # Update every 30 seconds
            except Exception as e:
                logger.error(f"Background metrics collection error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _update_dynamic_metrics(self) -> None:
        """Update dynamic metrics"""
        try:
            # Update system metrics
            await self._update_system_metrics()
            
            # Update database metrics
            await self._update_database_metrics()
            
            # Update Redis metrics
            await self._update_redis_metrics()
            
            # Update business metrics
            await self._update_business_metrics()
            
        except Exception as e:
            logger.error(f"Failed to update dynamic metrics: {e}")
    
    async def _update_system_metrics(self) -> None:
        """Update system metrics"""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent()
            self.system_cpu_usage.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.system_memory_usage.set(memory.used)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.system_disk_usage.set(disk.used)
            
        except ImportError:
            # psutil not available, skip system metrics
            pass
        except Exception as e:
            logger.error(f"Failed to update system metrics: {e}")
    
    async def _update_database_metrics(self) -> None:
        """Update database metrics"""
        try:
            from core.supabase_production import get_supabase_production_manager
            
            manager = get_supabase_production_manager()
            if manager.client:
                stats = await manager.get_database_stats()
                
                # Update connection metrics
                pool_stats = stats.get("connection_pool", {})
                self.database_connections_active.labels(database="supabase").set(
                    pool_stats.get("active_connections", 0)
                )
                
                # Update query metrics (simplified)
                self.database_query_total.labels(
                    database="supabase", 
                    operation="select", 
                    status="success"
                ).inc(stats.get("queries_executed", 0))
                
        except Exception as e:
            logger.error(f"Failed to update database metrics: {e}")
    
    async def _update_redis_metrics(self) -> None:
        """Update Redis metrics"""
        try:
            from core.redis_production import get_redis_production_manager
            
            manager = get_redis_production_manager()
            if manager.client:
                stats = await manager.get_redis_stats()
                
                # Update connection metrics
                self.redis_connections_active.set(
                    stats.get("connected_clients", 0)
                )
                
                # Update memory metrics
                memory_bytes = stats.get("used_memory", 0)
                self.redis_memory_usage.set(memory_bytes)
                
                # Update command metrics
                self.redis_commands_total.labels(
                    command="get", 
                    status="success"
                ).inc(stats.get("keyspace_hits", 0))
                
                self.redis_commands_total.labels(
                    command="get", 
                    status="miss"
                ).inc(stats.get("keyspace_misses", 0))
                
        except Exception as e:
            logger.error(f"Failed to update Redis metrics: {e}")
    
    async def _update_business_metrics(self) -> None:
        """Update business metrics"""
        try:
            from core.supabase_production import get_supabase_production_manager
            
            manager = get_supabase_production_manager()
            if manager.client:
                # Count users
                try:
                    users_result = manager.client.table("users").select("*", count="exact").execute()
                    user_count = users_result.count if hasattr(users_result, 'count') else len(users_result.data)
                    self.users_total.labels(status="active").set(user_count)
                except Exception:
                    pass
                
                # Count workspaces
                try:
                    workspaces_result = manager.client.table("workspaces").select("*", count="exact").execute()
                    workspace_count = workspaces_result.count if hasattr(workspaces_result, 'count') else len(workspaces_result.data)
                    self.workspaces_total.labels(status="active").set(workspace_count)
                except Exception:
                    pass
                
                # Count ICPs
                try:
                    icps_result = manager.client.table("icp_profiles").select("*", count="exact").execute()
                    icp_count = icps_result.count if hasattr(icps_result, 'count') else len(icps_result.data)
                    self.icps_total.labels(status="active").set(icp_count)
                except Exception:
                    pass
                
        except Exception as e:
            logger.error(f"Failed to update business metrics: {e}")
    
    def record_http_request(
        self, 
        method: str, 
        endpoint: str, 
        status_code: int,
        duration: float,
        request_size: int = 0,
        response_size: int = 0
    ) -> None:
        """Record HTTP request metrics"""
        
        # Clean endpoint name
        endpoint_clean = endpoint.split("?")[0]  # Remove query params
        
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint_clean,
            status_code=str(status_code)
        ).inc()
        
        self.http_request_duration.labels(
            method=method,
            endpoint=endpoint_clean
        ).observe(duration)
        
        if request_size > 0:
            self.http_request_size.labels(
                method=method,
                endpoint=endpoint_clean
            ).observe(request_size)
        
        if response_size > 0:
            self.http_response_size.labels(
                method=method,
                endpoint=endpoint_clean
            ).observe(response_size)
    
    def record_database_query(
        self, 
        database: str, 
        operation: str, 
        duration: float,
        status: str = "success"
    ) -> None:
        """Record database query metrics"""
        
        self.database_query_duration.labels(
            database=database,
            operation=operation
        ).observe(duration)
        
        self.database_query_total.labels(
            database=database,
            operation=operation,
            status=status
        ).inc()
    
    def record_cache_operation(
        self, 
        operation: str, 
        cache_type: str, 
        status: str
    ) -> None:
        """Record cache operation metrics"""
        
        self.cache_operations_total.labels(
            operation=operation,
            cache_type=cache_type,
            status=status
        ).inc()
    
    def record_error(
        self, 
        error_type: str, 
        endpoint: str, 
        severity: str = "error"
    ) -> None:
        """Record error metrics"""
        
        self.errors_total.labels(
            type=error_type,
            endpoint=endpoint,
            severity=severity
        ).inc()
    
    def record_circuit_breaker_state(
        self, 
        service: str, 
        state: int
    ) -> None:
        """Record circuit breaker state"""
        
        self.circuit_breaker_state.labels(service=service).set(state)
    
    def record_rate_limit_request(
        self, 
        user_id: str, 
        endpoint: str, 
        status: str
    ) -> None:
        """Record rate limiting metrics"""
        
        self.rate_limit_requests_total.labels(
            user_id=user_id,
            endpoint=endpoint,
            status=status
        ).inc()


# Global metrics instance
_prometheus_metrics: Optional[PrometheusMetrics] = None


def init_prometheus_metrics(app: FastAPI) -> PrometheusMetrics:
    """Initialize Prometheus metrics"""
    global _prometheus_metrics
    if _prometheus_metrics is None:
        _prometheus_metrics = PrometheusMetrics(app)
    return _prometheus_metrics


def get_prometheus_metrics() -> Optional[PrometheusMetrics]:
    """Get global Prometheus metrics instance"""
    return _prometheus_metrics


# Metrics middleware
class PrometheusMiddleware:
    """Middleware to automatically record HTTP metrics"""
    
    def __init__(self, app, metrics: PrometheusMetrics):
        self.app = app
        self.metrics = metrics
    
    async def __call__(self, scope, receive, send):
        """ASGI middleware implementation"""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Record start time
        start_time = time.time()
        
        # Get request details
        method = scope["method"]
        path = scope["path"]
        
        # Get request size if available
        request_size = 0
        headers = dict(scope.get("headers", []))
        content_length = headers.get("content-length")
        if content_length:
            try:
                request_size = int(content_length)
            except ValueError:
                pass
        
        # Custom send function to capture response
        async def custom_send(message):
            if message["type"] == "http.response.start":
                # Record metrics
                duration = time.time() - start_time
                status_code = message.get("status", 200)
                
                # Get response size if available
                response_size = 0
                for header, value in message.get("headers", []):
                    if header == b"content-length":
                        try:
                            response_size = int(value.decode())
                        except (ValueError, UnicodeDecodeError):
                            pass
                
                # Record metrics
                self.metrics.record_http_request(
                    method=method,
                    endpoint=path,
                    status_code=status_code,
                    duration=duration,
                    request_size=request_size,
                    response_size=response_size
                )
            
            await send(message)
        
        await self.app(scope, receive, custom_send)


# Decorator for metrics
def track_metrics(operation: str, category: str = "function"):
    """Decorator to automatically track function metrics"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record success metrics
                metrics = get_prometheus_metrics()
                if metrics:
                    metrics.record_http_request(
                        method="FUNCTION",
                        endpoint=f"{category}.{operation}",
                        status_code=200,
                        duration=duration
                    )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Record error metrics
                metrics = get_prometheus_metrics()
                if metrics:
                    metrics.record_error(
                        error_type=type(e).__name__,
                        endpoint=f"{category}.{operation}",
                        severity="error"
                    )
                
                raise
        
        return wrapper
    return decorator
