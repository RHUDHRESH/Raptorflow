"""
Job worker for Redis-based background job processing.

Implements worker lifecycle management, job execution,
and coordination with the queue system.
import asyncio
import logging
import os
import signal
import sys
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional
import psutil
from .client import get_redis
from .critical_fixes import SecureErrorHandler
from .queue import QueueService
from .queue_models import Job, JobResult, JobStatus
from .worker_models import (
    WorkerMetrics,
    WorkerPool,
    WorkerRegistry,
    WorkerState,
    WorkerStatus,
    WorkerType,
)
class JobWorker:
    """Background job worker with lifecycle management."""
    def __init__(
        self,
        worker_id: Optional[str] = None,
        worker_type: WorkerType = WorkerType.AGENT_PROCESSOR,
        queue_names: List[str] = None,
        max_concurrent_jobs: int = 1,
        job_timeout_seconds: int = 300,
        heartbeat_interval: int = 30,
        max_retries: int = 3,
        retry_delay_seconds: int = 60,
    ):
        self.worker_id = worker_id or str(uuid.uuid4())
        self.worker_type = worker_type
        self.queue_names = queue_names or ["agent_tasks"]
        self.max_concurrent_jobs = max_concurrent_jobs
        self.job_timeout_seconds = job_timeout_seconds
        self.heartbeat_interval = heartbeat_interval
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds
        # Core services
        self.redis = get_redis()
        self.queue_service = QueueService()
        self.error_handler = SecureErrorHandler()
        # Worker state
        self.state = WorkerState(
            worker_id=self.worker_id,
            worker_type=self.worker_type,
            status=WorkerStatus.STARTING,
            queue_name=self.queue_names[0] if self.queue_names else "default",
            max_concurrent_jobs=max_concurrent_jobs,
            job_timeout_seconds=job_timeout_seconds,
            retry_attempts=max_retries,
            retry_delay_seconds=retry_delay_seconds,
            hostname=psutil.os.uname().nodename,
            pid=os.getpid(),
            version="1.0.0",
        )
        # Worker metrics
        self.metrics = WorkerMetrics(worker_id=self.worker_id)
        # Job handlers registry
        self.job_handlers: Dict[str, Callable] = {}
        # Runtime state
        self._running = False
        self._shutdown_requested = False
        self._current_jobs: Dict[str, asyncio.Task] = {}
        self._executor = ThreadPoolExecutor(max_workers=max_concurrent_jobs)
        # Setup signal handlers
        self._setup_signal_handlers()
        # Setup logging
        self.logger = logging.getLogger(f"worker.{self.worker_id}")
        # Register default handlers
        self._register_default_handlers()
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown")
            self._shutdown_requested = True
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    def _register_default_handlers(self):
        """Register default job handlers."""
        self.register_handler("test_job", self._handle_test_job)
        self.register_handler("agent_task", self._handle_agent_task)
        self.register_handler("webhook_task", self._handle_webhook_task)
        self.register_handler("usage_aggregation", self._handle_usage_aggregation)
        self.register_handler("session_cleanup", self._handle_session_cleanup)
    def register_handler(self, job_type: str, handler: Callable):
        """Register a job handler."""
        self.job_handlers[job_type] = handler
        self.state.capabilities.append(job_type)
        self.logger.info(f"Registered handler for job type: {job_type}")
    async def start(self):
        """Start the worker."""
        try:
            self.logger.info(
                f"Starting worker {self.worker_id} of type {self.worker_type.value}"
            )
            # Register worker
            await self._register_worker()
            # Set status to idle
            self.state.set_status(WorkerStatus.IDLE)
            # Start heartbeat loop
            self._running = True
            heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            # Start main processing loop
            await self._processing_loop()
        except Exception as e:
            self.logger.error(f"Worker startup failed: {e}")
            self.state.set_status(WorkerStatus.ERROR, str(e))
            raise
        finally:
            # Cleanup
            await self._cleanup()
            if "heartbeat_task" in locals():
                heartbeat_task.cancel()
    async def stop(self):
        """Stop the worker gracefully."""
        self.logger.info(f"Stopping worker {self.worker_id}")
        self._shutdown_requested = True
        self.state.set_status(WorkerStatus.SHUTTING_DOWN)
    async def _register_worker(self):
        """Register worker in Redis."""
        worker_key = f"worker:{self.worker_id}"
        await self.redis.set_json(
            worker_key, self.state.to_dict(), ex=3600
        )  # 1 hour TTL
        # Add to worker registry
        registry_key = os.getenv("REGISTRY_KEY")
        await self.redis.hset(registry_key, self.worker_id, worker_key)
        self.logger.info(f"Worker {self.worker_id} registered")
    async def _unregister_worker(self):
        """Unregister worker from Redis."""
        await self.redis.delete(worker_key)
        # Remove from worker registry
        await self.redis.hdel(registry_key, self.worker_id)
        self.logger.info(f"Worker {self.worker_id} unregistered")
    async def _heartbeat_loop(self):
        """Send periodic heartbeats."""
        while self._running and not self._shutdown_requested:
            try:
                self.state.update_heartbeat()
                # Update worker state in Redis
                worker_key = f"worker:{self.worker_id}"
                await self.redis.set_json(worker_key, self.state.to_dict(), ex=3600)
                # Update resource usage
                await self._update_resource_usage()
                # Wait for next heartbeat
                await asyncio.sleep(self.heartbeat_interval)
            except Exception as e:
                self.logger.error(f"Heartbeat failed: {e}")
                await asyncio.sleep(5)  # Short retry delay
    async def _update_resource_usage(self):
        """Update worker resource usage metrics."""
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            # Get memory usage
            memory_info = psutil.virtual_memory()
            memory_mb = memory_info.used / (1024 * 1024)
            # Get network I/O
            network_io = psutil.net_io_counters()
            network_mb = (network_io.bytes_sent + network_io.bytes_recv) / (1024 * 1024)
            # Update metrics
            self.metrics.update_resource_usage(cpu_percent, memory_mb, network_mb)
            self.logger.error(f"Failed to update resource usage: {e}")
    async def _processing_loop(self):
        """Main job processing loop."""
        self.logger.info(f"Worker {self.worker_id} starting processing loop")
                # Check if we can process more jobs
                if len(self._current_jobs) >= self.max_concurrent_jobs:
                    await asyncio.sleep(1)
                    continue
                # Try to get a job from any queue
                job = None
                for queue_name in self.queue_names:
                    job = await self.queue_service.dequeue(queue_name, self.worker_id)
                    if job:
                        break
                if job:
                    # Process the job
                    task = asyncio.create_task(self._process_job(job))
                    self._current_jobs[job.job_id] = task
                    self.state.assign_job(job.job_id)
                else:
                    # No jobs available, wait a bit
                self.logger.error(f"Processing loop error: {e}")
                self.state.set_status(WorkerStatus.ERROR, str(e))
                await asyncio.sleep(5)  # Error recovery delay
    async def _process_job(self, job: Job):
        """Process a single job."""
        job_start_time = datetime.now()
            self.logger.info(f"Processing job {job.job_id} of type {job.job_type}")
            # Check for handler
            if job.job_type not in self.job_handlers:
                raise ValueError(f"No handler registered for job type: {job.job_type}")
            # Execute job with timeout
            handler = self.job_handlers[job.job_type]
            if asyncio.iscoroutinefunction(handler):
                result_data = await asyncio.wait_for(
                    handler(job.payload), timeout=self.job_timeout_seconds
                )
            else:
                # Run synchronous handler in thread pool
                    asyncio.get_event_loop().run_in_executor(
                        self._executor, handler, job.payload
                    ),
                    timeout=self.job_timeout_seconds,
            # Create successful result
            result = JobResult(
                success=True,
                data=result_data,
                execution_time_ms=int(
                    (datetime.now() - job_start_time).total_seconds() * 1000
                ),
            # Complete the job
            await self.queue_service.complete_job(job.job_id, result, self.worker_id)
            processing_time_ms = result.execution_time_ms
            self.metrics.record_job_completed(processing_time_ms)
                f"Job {job.job_id} completed successfully in {processing_time_ms}ms"
        except asyncio.TimeoutError:
            error_msg = f"Job {job.job_id} timed out after {self.job_timeout_seconds}s"
            self.logger.error(error_msg)
            # Fail the job with timeout error
            await self.queue_service.fail_job(job.job_id, error_msg, self.worker_id)
            self.metrics.record_job_failed()
            self.state.set_status(WorkerStatus.ERROR, error_msg)
            error_msg = f"Job {job.job_id} failed: {str(e)}"
            self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
            # Log security event if suspicious
            if any(
                keyword in str(e).lower()
                for keyword in ["injection", "xss", "sql", "drop", "delete"]
            ):
                self.error_handler.log_security_event(
                    event_type=os.getenv("REGISTRY_KEY"),
                    severity="HIGH",
                    description=f"Suspicious error in job {job.job_id}: {str(e)}",
                    context={"job_type": job.job_type, "worker_id": self.worker_id},
                    workspace_id=job.payload.get("workspace_id"),
            # Fail the job
            await self.queue_service.fail_job(job.job_id, str(e), self.worker_id)
            # Clean up
            if job.job_id in self._current_jobs:
                del self._current_jobs[job.job_id]
            if self.state.current_job_id == job.job_id:
                self.state.complete_job()
            # Reset status if not shutting down
            if self.state.status == WorkerStatus.ERROR and not self._shutdown_requested:
                self.state.set_status(WorkerStatus.IDLE)
    async def _cleanup(self):
        """Cleanup worker resources."""
        self.logger.info(f"Cleaning up worker {self.worker_id}")
        # Wait for current jobs to finish (with timeout)
        if self._current_jobs:
            self.logger.info(f"Waiting for {len(self._current_jobs)} jobs to finish")
                await asyncio.wait_for(
                    asyncio.gather(
                        *self._current_jobs.values(), return_exceptions=True
                    timeout=30,  # 30 second timeout
            except asyncio.TimeoutError:
                self.logger.warning("Some jobs didn't finish in time")
        # Shutdown executor
        self._executor.shutdown(wait=True)
        # Unregister worker
        await self._unregister_worker()
        # Set final status
        self.state.set_status(WorkerStatus.STOPPED)
        self.logger.info(f"Worker {self.worker_id} cleanup completed")
    # Default job handlers
    async def _handle_test_job(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle test job."""
        await asyncio.sleep(1)  # Simulate work
        return {"status": "completed", "message": "Test job executed successfully"}
    async def _handle_agent_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle agent task."""
        # This would integrate with the actual agent system
        workspace_id = payload.get("workspace_id")
        task_type = payload.get("task_type", "unknown")
        self.logger.info(
            f"Processing agent task {task_type} for workspace {workspace_id}"
        # Simulate agent processing
        await asyncio.sleep(2)
        return {
            "status": "completed",
            "task_type": task_type,
            "workspace_id": workspace_id,
            "result": f"Agent task {task_type} completed",
        }
    async def _handle_webhook_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle webhook task."""
        webhook_url = payload.get("webhook_url")
        webhook_data = payload.get("data", {})
        self.logger.info(f"Processing webhook task for {webhook_url}")
        # This would integrate with actual webhook processing
        await asyncio.sleep(1)
        return {"status": "completed", "webhook_url": webhook_url, "delivered": True}
    async def _handle_usage_aggregation(
        self, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle usage aggregation task."""
        date_range = payload.get("date_range", "daily")
            f"Aggregating usage for workspace {workspace_id} ({date_range})"
        # This would integrate with actual usage aggregation
        await asyncio.sleep(3)
            "date_range": date_range,
            "aggregated_data": {"total_tokens": 1000, "total_cost": 0.10},
    async def _handle_session_cleanup(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle session cleanup task."""
        cleanup_type = payload.get("cleanup_type", "expired")
            f"Cleaning up sessions for workspace {workspace_id} ({cleanup_type})"
        # This would integrate with actual session cleanup
            "cleanup_type": cleanup_type,
            "sessions_cleaned": 10,
class WorkerManager:
    """Manages multiple workers and worker pools."""
    def __init__(self):
        self.workers: Dict[str, JobWorker] = {}
        self.pools: Dict[str, WorkerPool] = {}
        self.registry = WorkerRegistry()
        self.logger = logging.getLogger("worker_manager")
    async def create_worker_pool(
        pool_name: str,
        worker_type: WorkerType,
        queue_names: List[str],
        pool_size: int = 3,
    ) -> WorkerPool:
        """Create a worker pool."""
        pool = WorkerPool(
            pool_name=pool_name,
            worker_type=worker_type,
            min_workers=1,
            max_workers=pool_size,
        # Create workers
        for i in range(pool_size):
            worker = JobWorker(
                worker_type=worker_type,
                queue_names=queue_names,
                max_concurrent_jobs=max_concurrent_jobs,
            self.workers[worker.worker_id] = worker
            pool.add_worker(worker.state)
            self.registry.register_worker(worker.state)
        self.pools[pool_name] = pool
        self.logger.info(f"Created worker pool {pool_name} with {pool_size} workers")
        return pool
    async def start_pool(self, pool_name: str):
        """Start all workers in a pool."""
        if pool_name not in self.pools:
            raise ValueError(f"Pool {pool_name} not found")
        pool = self.pools[pool_name]
        tasks = []
        for worker_id in pool.workers.keys():
            if worker_id in self.workers:
                task = asyncio.create_task(self.workers[worker_id].start())
                tasks.append(task)
        self.logger.info(f"Starting {len(tasks)} workers in pool {pool_name}")
        return tasks
    async def stop_pool(self, pool_name: str):
        """Stop all workers in a pool."""
            return
                await self.workers[worker_id].stop()
        self.logger.info(f"Stopped workers in pool {pool_name}")
    async def get_pool_status(self, pool_name: str) -> Optional[Dict[str, Any]]:
        """Get pool status."""
            return None
        pool._update_metrics()
            "pool_name": pool_name,
            "worker_type": pool.worker_type.value,
            "total_workers": pool.total_capacity,
            "active_workers": pool.active_workers,
            "idle_workers": pool.idle_workers,
            "jobs_processed_total": pool.jobs_processed_total,
            "jobs_failed_total": pool.jobs_failed_total,
            "avg_throughput": pool.avg_throughput,
            "should_scale_up": pool.should_scale_up(),
            "should_scale_down": pool.should_scale_down(),
    async def get_registry_status(self) -> Dict[str, Any]:
        """Get global worker registry status."""
        self.registry._update_metrics()
            "total_workers": self.registry.total_workers,
            "active_workers": self.registry.active_workers,
            "idle_workers": self.registry.idle_workers,
            "error_workers": self.registry.error_workers,
            "pools": {
                name: {
                    "worker_type": pool.worker_type.value,
                    "total_capacity": pool.total_capacity,
                    "active_workers": pool.active_workers,
                }
                for name, pool in self.pools.items()
            },
