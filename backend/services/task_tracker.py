from backend.utils.cache import redis_cache
from typing import Dict, Any, Optional, List

async def update_task_status(task_id: str, status: str, data: Optional[Dict[str, Any]] = None):
    """
    Update task status in Redis.
    Key format: raptorflow:task:{task_id}
    """
    payload = {"status": status}
    if data:
        payload.update(data)
    
    # Uses redis_cache.set which handles prefixing
    await redis_cache.set("task", task_id, payload, ttl=3600) # 1 hour TTL for task status

async def bulk_update_task_status(updates: List[Dict[str, Any]]):
    """
    Update multiple tasks at once using pipeline.
    updates = [{"task_id": "...", "status": "...", "data": {...}}]
    """
    # We can't easily do pipeline with the current redis_cache wrapper if it doesn't expose it.
    # But we can iterate for now, or check if redis_cache has a pipeline method.
    # Assuming redis_cache.client exposes the raw redis client.
    
    if not updates:
        return

    # If we can't access pipeline easily, we just await concurrently.
    # But let's try to use the raw client if available, or just loop.
    # Since this is for "bulk database saves" (mocked here as redis updates), 
    # doing them in parallel is better than sequential.
    
    import asyncio
    tasks = []
    for update in updates:
        task_id = update["task_id"]
        status = update["status"]
        data = update.get("data")
        tasks.append(update_task_status(task_id, status, data))
    
    await asyncio.gather(*tasks)

async def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve task status from Redis.
    """
    return await redis_cache.get("task", task_id)
