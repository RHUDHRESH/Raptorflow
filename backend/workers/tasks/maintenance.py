"""
Maintenance and monitoring tasks for Celery
"""

import logging
import time
from datetime import datetime, timedelta

from ..core.celery_manager import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="workers.tasks.maintenance.cleanup_expired_tasks")
def cleanup_expired_tasks():
    """Clean up expired task results"""
    try:
        logger.info("Starting cleanup of expired tasks")

        # This would integrate with your result backend cleanup
        # For Redis, this is handled automatically by result_expires config

        logger.info("Completed cleanup of expired tasks")
        return {"success": True, "timestamp": datetime.utcnow().isoformat()}

    except Exception as e:
        logger.error(f"Task cleanup failed: {e}")
        return {"success": False, "error": str(e)}


@celery_app.task(name="workers.tasks.maintenance.health_check")
def health_check():
    """Health check task for monitoring"""
    try:
        # Check basic functionality
        start_time = time.time()

        # Simulate some work
        time.sleep(0.1)

        end_time = time.time()

        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time": end_time - start_time,
            "worker_id": health_check.request.id,
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
