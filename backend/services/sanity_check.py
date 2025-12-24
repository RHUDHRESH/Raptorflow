import asyncio
import logging
from typing import Any, Dict

from backend.core.cache import get_cache_manager
from backend.db import get_db_connection
from backend.inference import InferenceProvider

logger = logging.getLogger("raptorflow.services.sanity_check")


class SystemSanityCheck:
    """
    SOTA System Sanity Checker.
    Performs periodic health probes on all critical infrastructure.
    Ensures agentic stability and prevents cascade failures.
    """

    async def check_redis(self) -> bool:
        """Pings Upstash Redis."""
        try:
            manager = get_cache_manager()
            if not manager.client:
                return False
            manager.client.ping()
            return True
        except Exception as e:
            logger.error(f"Sanity Check: Redis offline - {e}")
            return False

    async def check_postgres(self) -> bool:
        """Pings Supabase Postgres."""
        try:
            async with get_db_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1")
                    return True
        except Exception as e:
            logger.error(f"Sanity Check: Postgres offline - {e}")
            return False

    async def check_inference(self) -> bool:
        """Verifies Vertex AI model access."""
        try:
            # We don't want to run a full inference, just check if we can get the model
            InferenceProvider.get_model(model_tier="fast")
            return True
        except Exception as e:
            logger.error(f"Sanity Check: Inference Provider error - {e}")
            return False

    async def run_suite(self) -> Dict[str, Any]:
        """Runs the full sanity check suite and returns a report."""
        results = await asyncio.gather(
            self.check_redis(), self.check_postgres(), self.check_inference()
        )

        report = {
            "status": "healthy" if all(results) else "unhealthy",
            "services": {
                "redis": results[0],
                "postgres": results[1],
                "inference": results[2],
            },
        }

        if report["status"] == "unhealthy":
            logger.critical(f"SYSTEM SANITY ALERT: {report['services']}")

        return report
