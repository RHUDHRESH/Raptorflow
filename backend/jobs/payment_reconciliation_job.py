"""
Scheduled payment reconciliation job.
Runs periodically to reconcile payment status with PhonePe.

Can be triggered via:
1. APScheduler background job
2. Cloud Scheduler (Google Cloud Run)
3. Manual endpoint call
4. Cron task
"""

import logging
import asyncio
from datetime import datetime, timezone
from backend.services.payment_reconciliation import payment_reconciliation_service

logger = logging.getLogger(__name__)


async def run_payment_reconciliation_job():
    """
    Execute the payment reconciliation job.
    This should be called periodically (e.g., every 15 minutes).
    """
    logger.info(f"Payment reconciliation job started at {datetime.now(timezone.utc).isoformat()}")

    try:
        results = await payment_reconciliation_service.run_full_reconciliation()

        logger.info(f"Payment reconciliation job completed: {results}")

        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results": results
        }

    except Exception as e:
        logger.error(f"Payment reconciliation job failed: {str(e)}", exc_info=True)

        return {
            "status": "failed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }


# For APScheduler integration
def setup_payment_reconciliation_schedule(scheduler):
    """
    Setup APScheduler to run payment reconciliation every 15 minutes.

    Args:
        scheduler: APScheduler scheduler instance
    """
    from apscheduler.schedulers.background import BackgroundScheduler

    try:
        scheduler.add_job(
            func=lambda: asyncio.run(run_payment_reconciliation_job()),
            trigger="interval",
            minutes=15,
            id="payment_reconciliation",
            name="Payment Reconciliation",
            replace_existing=True
        )

        logger.info("Payment reconciliation job scheduled to run every 15 minutes")

    except Exception as e:
        logger.error(f"Failed to setup payment reconciliation schedule: {str(e)}")
