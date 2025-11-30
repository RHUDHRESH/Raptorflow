import asyncio
import logging
import os
from typing import Dict, Any, List, Optional
from backend.utils.queue import redis_queue, Priority
from backend.services.extractors.universal import UniversalExtractor
from backend.services.task_tracker import update_task_status, bulk_update_task_status

logger = logging.getLogger(__name__)

class IntelligenceWorkerV2:
    """
    Batch processing. Parallel execution. Bulk saving.
    """
    
    def __init__(self):
        self.extractor = UniversalExtractor()
        self.queue = redis_queue
        self.running = False
        self.batch_size = 10
        
    async def start(self):
        self.running = True
        logger.info(f"Intelligence Worker V2 started (Batch Size: {self.batch_size})")
        
        # Ensure queue connected
        if not self.queue.redis:
            await self.queue.connect()
            
        while self.running:
            # 1. Fetch Batch
            tasks = await self._fetch_batch(self.batch_size)
            
            if not tasks:
                await asyncio.sleep(0.5)
                continue
                
            logger.info(f"Processing batch of {len(tasks)} tasks")

            # 2. Process in Parallel
            # We define a wrapper that returns the update dict
            process_futures = [self._process_single_task(task) for task in tasks]
            results = await asyncio.gather(*process_futures, return_exceptions=True)
            
            # 3. Prepare Bulk Updates
            updates = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # Handle uncaught exception in wrapper
                    task = tasks[i]
                    payload = task["payload"]
                    task_id = task.get("correlation_id") or payload.get("task_id")
                    logger.error(f"Critical error processing task {task_id}: {result}")
                    if task_id:
                        updates.append({
                            "task_id": task_id,
                            "status": "failed",
                            "data": {"message": str(result)}
                        })
                elif result:
                    updates.append(result)
            
            # 4. Bulk Save
            if updates:
                try:
                    await bulk_update_task_status(updates)
                    logger.info(f"Bulk updated status for {len(updates)} tasks")
                except Exception as e:
                    logger.error(f"Failed to bulk update tasks: {e}")
                    # Fallback? For now just log.

    async def _fetch_batch(self, limit: int) -> List[Dict[str, Any]]:
        """Fetch up to 'limit' tasks from priority queues"""
        tasks = []
        for _ in range(limit):
            # Check priorities in order
            task = None
            for priority in [Priority.HIGH, Priority.MEDIUM, Priority.LOW]:
                task = await self.queue.dequeue(priority, timeout=0)
                if task:
                    break
            
            if task:
                tasks.append(task)
            else:
                # No more tasks available instantly
                break
        return tasks

    async def _process_single_task(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a single task and return the status update dictionary.
        Does NOT save to DB/Redis itself (except for intermediate 'processing' updates if needed).
        """
        payload = task["payload"]
        task_id = task.get("correlation_id") or payload.get("task_id")
        
        if not task_id:
            logger.error("Task missing ID", extra={"payload": payload})
            return None
            
        try:
            # Optional: Update to 'processing' immediately? 
            # For true bulk efficiency, we might skip this or batch it too.
            # But UI might expect it. Let's fire and forget (no await) or just skip for speed.
            # await update_task_status(task_id, "processing", {"progress": 10, "message": "Extracting..."})
            
            # Determine input
            input_data = payload.get("file_path") or payload.get("url")
            
            # Legacy fallback
            if not input_data and payload.get("content_b64"):
                import base64
                import tempfile
                content = base64.b64decode(payload.get("content_b64"))
                suffix = f".{payload.get('upload_type', 'dat')}"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(content)
                    input_data = tmp.name
                    payload["file_path"] = input_data # Mark for cleanup
            
            if not input_data:
                return {
                    "task_id": task_id,
                    "status": "failed",
                    "data": {"message": "No input data found"}
                }
                
            # Extract
            result = await self.extractor.extract(input_data, metadata={"original_filename": payload.get("filename")})
            
            if "error" in result and result.get("error"):
                raise Exception(result["error"])
                
            # Cleanup temp file
            if payload.get("file_path") and os.path.exists(payload.get("file_path")):
                try:
                    os.remove(payload.get("file_path"))
                except OSError:
                    pass

            # Return success update
            return {
                "task_id": task_id,
                "status": "completed",
                "data": {
                    "progress": 100, 
                    "message": "Extraction complete",
                    "result": result
                }
            }
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            
            # Cleanup
            if payload.get("file_path") and os.path.exists(payload.get("file_path")):
                try:
                    os.remove(payload.get("file_path"))
                except:
                    pass
            
            return {
                "task_id": task_id,
                "status": "failed",
                "data": {"message": str(e)}
            }

    async def stop(self):
        self.running = False
        logger.info("Intelligence Worker stopping...")

if __name__ == "__main__":
    from backend.utils.logging_config import setup_logging
    setup_logging()
    worker = IntelligenceWorkerV2()
    loop = asyncio.get_event_loop()
    
    try:
        loop.run_until_complete(worker.start())
    except KeyboardInterrupt:
        loop.run_until_complete(worker.stop())
