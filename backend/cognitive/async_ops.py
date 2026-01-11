"""
Truly Asynchronous Operations
Replaces fake async with real concurrent processing
"""

import asyncio
import concurrent.futures
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, TypeVar

import aiohttp

logger = logging.getLogger(__name__)

T = TypeVar("T")


class AsyncProcessor:
    """Manages truly asynchronous operations"""

    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers
        )
        self.process_pool = concurrent.futures.ProcessPoolExecutor(
            max_workers=max_workers // 2
        )

    async def run_in_thread(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Run CPU-bound function in thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.thread_pool, func, *args, **kwargs)

    async def run_in_process(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Run heavy CPU-bound function in process pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.process_pool, func, *args, **kwargs)

    async def gather_with_concurrency(
        self, tasks: List[Callable[..., T]], max_concurrency: Optional[int] = None
    ) -> List[T]:
        """Run tasks with concurrency limit"""
        max_concurrency = max_concurrency or self.max_workers
        semaphore = asyncio.Semaphore(max_concurrency)

        async def limited_task(task):
            async with semaphore:
                if asyncio.iscoroutinefunction(task):
                    return await task()
                else:
                    return await self.run_in_thread(task)

        return await asyncio.gather(*(limited_task(task) for task in tasks))

    async def parallel_map(
        self,
        func: Callable[[Any], T],
        items: List[Any],
        max_concurrency: Optional[int] = None,
    ) -> List[T]:
        """Apply function to items in parallel"""
        tasks = [lambda item=item: func(item) for item in items]
        return await self.gather_with_concurrency(tasks, max_concurrency)

    def shutdown(self):
        """Shutdown thread and process pools"""
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)


class AsyncLLMClient:
    """Truly asynchronous LLM client with connection pooling"""

    def __init__(self, base_url: str, api_key: str, max_connections: int = 10):
        self.base_url = base_url
        self.api_key = api_key
        self.max_connections = max_connections
        self.session: Optional[aiohttp.ClientSession] = None
        self.request_semaphore = asyncio.Semaphore(max_connections)

    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(limit=self.max_connections)
        timeout = aiohttp.ClientTimeout(total=60, connect=10)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def generate(
        self,
        prompt: str,
        model: str = "default",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> str:
        """Generate text asynchronously"""
        if not self.session:
            raise RuntimeError("LLMClient not initialized. Use async context manager.")

        async with self.request_semaphore:
            payload = {
                "prompt": prompt,
                "model": model,
                "temperature": temperature,
                **kwargs,
            }
            if max_tokens:
                payload["max_tokens"] = max_tokens

            try:
                async with self.session.post(
                    f"{self.base_url}/generate", json=payload
                ) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return result.get("text", "")
            except aiohttp.ClientError as e:
                logger.error(f"LLM API error: {e}")
                raise

    async def count_tokens(self, text: str, model: str = "default") -> int:
        """Count tokens asynchronously"""
        if not self.session:
            raise RuntimeError("LLMClient not initialized. Use async context manager.")

        async with self.request_semaphore:
            payload = {"text": text, "model": model}

            try:
                async with self.session.post(
                    f"{self.base_url}/count_tokens", json=payload
                ) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return result.get("token_count", 0)
            except aiohttp.ClientError as e:
                logger.error(f"Token counting error: {e}")
                # Fallback to simple estimation
                return len(text.split())

    async def batch_generate(
        self, prompts: List[str], max_concurrency: int = 5, **kwargs
    ) -> List[str]:
        """Generate multiple texts in parallel"""
        semaphore = asyncio.Semaphore(max_concurrency)

        async def generate_single(prompt: str) -> str:
            async with semaphore:
                return await self.generate(prompt, **kwargs)

        tasks = [generate_single(prompt) for prompt in prompts]
        return await asyncio.gather(*tasks)


class AsyncCache:
    """Asynchronous cache with background cleanup"""

    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, Any] = {}
        self.expiry: Dict[str, datetime] = {}
        self.ttl_seconds = ttl_seconds
        self.cleanup_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """Start background cleanup task"""
        self._running = True
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop(self):
        """Stop background cleanup task"""
        self._running = False
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.expiry and datetime.now() > self.expiry[key]:
            await self.delete(key)
            return None
        return self.cache.get(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        self.cache[key] = value
        ttl_seconds = ttl or self.ttl_seconds
        self.expiry[key] = datetime.now() + timedelta(seconds=ttl_seconds)

    async def delete(self, key: str) -> None:
        """Delete value from cache"""
        self.cache.pop(key, None)
        self.expiry.pop(key, None)

    async def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
        self.expiry.clear()

    async def _cleanup_loop(self):
        """Background cleanup of expired entries"""
        while self._running:
            try:
                now = datetime.now()
                expired_keys = [
                    key for key, expiry in self.expiry.items() if now > expiry
                ]
                for key in expired_keys:
                    await self.delete(key)

                await asyncio.sleep(60)  # Clean up every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")
                await asyncio.sleep(10)


class AsyncBatchProcessor:
    """Batch processor for handling multiple operations efficiently"""

    def __init__(
        self,
        batch_size: int = 10,
        flush_interval: float = 1.0,
        max_concurrent_batches: int = 5,
    ):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.max_concurrent_batches = max_concurrent_batches
        self.queue: asyncio.Queue = asyncio.Queue()
        self.processor_task: Optional[asyncio.Task] = None
        self._running = False
        self.semaphore = asyncio.Semaphore(max_concurrent_batches)

    async def start(self, processor_func: Callable[[List[Any]], Any]):
        """Start batch processor"""
        self._running = True
        self.processor_task = asyncio.create_task(self._process_loop(processor_func))

    async def stop(self):
        """Stop batch processor"""
        self._running = False
        if self.processor_task:
            self.processor_task.cancel()
            try:
                await self.processor_task
            except asyncio.CancelledError:
                pass

    async def add_item(self, item: Any):
        """Add item to processing queue"""
        await self.queue.put(item)

    async def _process_loop(self, processor_func: Callable[[List[Any]], Any]):
        """Main processing loop"""
        while self._running:
            try:
                batch = []

                # Collect batch
                try:
                    timeout = self.flush_interval
                    while len(batch) < self.batch_size:
                        item = await asyncio.wait_for(self.queue.get(), timeout=timeout)
                        batch.append(item)
                        timeout = 0.1  # Reduce timeout after first item
                except asyncio.TimeoutError:
                    pass  # Process whatever we have

                if batch:
                    async with self.semaphore:
                        await processor_func(batch)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Batch processing error: {e}")
                await asyncio.sleep(1)
