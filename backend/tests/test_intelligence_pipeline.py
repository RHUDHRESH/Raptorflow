import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from backend.workers.intelligence_worker import IntelligenceWorkerV2
from backend.services.extractors.universal import UniversalExtractor

@pytest.mark.asyncio
async def test_intelligence_pipeline_e2e():
    # Mock dependencies
    with patch("backend.workers.intelligence_worker.redis_queue") as mock_queue:
        with patch("backend.workers.intelligence_worker.update_task_status", new_callable=AsyncMock) as mock_update:
            with patch("backend.workers.intelligence_worker.bulk_update_task_status", new_callable=AsyncMock) as mock_bulk:
                
                # Setup worker
                worker = IntelligenceWorkerV2()
                worker.queue = mock_queue
                
                # Create a dummy task
                task = {
                    "payload": {
                        "task_id": "test-task-123",
                        "url": "https://example.com",
                        "filename": "test.html"
                    },
                    "correlation_id": "test-task-123"
                }
                
                # Mock fetch to return task once then None
                # We mock the method on the instance we created
                worker._fetch_batch = AsyncMock(side_effect=[[task], []])
                
                # Mock extraction to avoid real network call
                with patch.object(UniversalExtractor, "extract", return_value={"content_type": "url", "raw_text": "Success"}) as mock_extract:
                    
                    # Execute what start() loop does for one batch
                    tasks = await worker._fetch_batch(10)
                    assert len(tasks) == 1
                    
                    # Process in Parallel
                    futures = [worker._process_single_task(t) for t in tasks]
                    results = await asyncio.gather(*futures)
                    
                    # Verify results
                    assert len(results) == 1
                    result = results[0]
                    
                    assert result["task_id"] == "test-task-123"
                    assert result["status"] == "completed"
                    assert result["data"]["result"]["raw_text"] == "Success"
                    
                    # Verify interactions
                    mock_extract.assert_called_once()
