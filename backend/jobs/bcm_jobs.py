"""
BCM background jobs.

Schedules periodic backfill of BCM vectors into semantic memory.
"""

import os
from typing import Any, Dict

from services.bcm_backfill_service import BCMVectorBackfillService

from .decorators import daily_job


@daily_job(
    hour=int(os.getenv("BCM_BACKFILL_HOUR", "3")),
    minute=int(os.getenv("BCM_BACKFILL_MINUTE", "30")),
    queue="memory",
    retries=1,
    timeout=3600,
    description="Backfill BCM vectors into semantic memory",
)
async def bcm_vector_backfill_job() -> Dict[str, Any]:
    service = BCMVectorBackfillService()
    batch_size = int(os.getenv("BCM_BACKFILL_BATCH_SIZE", "50"))
    max_records = int(os.getenv("BCM_BACKFILL_MAX_RECORDS", "0"))
    run_id = f"bcm-backfill-cron-{os.getpid()}"
    return await service.backfill_with_lock(
        run_id=run_id,
        table="both",
        batch_size=batch_size,
        max_records=max_records,
        dry_run=False,
    )
