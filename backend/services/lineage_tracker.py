import logging
from typing import Any, Dict, Optional

from db import get_db_connection

logger = logging.getLogger("raptorflow.services.lineage_tracker")


class ModelLineageTracker:
    """
    SOTA Model Lineage Tracker.
    Records the immutable link between model artifacts, training data, and production deployments.
    Essential for MLOps auditing and reproducibility in agentic systems.
    """

    async def register_model(
        self,
        model_id: str,
        dataset_uri: str,
        artifact_uri: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Registers a new model version with its GCS lineage."""
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                query = """
                    INSERT INTO model_lineage (model_id, dataset_uri, artifact_uri, metadata)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (model_id) DO UPDATE
                    SET dataset_uri = EXCLUDED.dataset_uri,
                        artifact_uri = EXCLUDED.artifact_uri,
                        metadata = model_lineage.metadata || EXCLUDED.metadata,
                        updated_at = CURRENT_TIMESTAMP;
                """
                import psycopg

                try:
                    await cur.execute(
                        query,
                        (
                            model_id,
                            dataset_uri,
                            artifact_uri,
                            psycopg.types.json.Jsonb(metadata or {}),
                        ),
                    )
                    await conn.commit()
                    logger.info(f"Model lineage registered: {model_id}")
                    return True
                except Exception as e:
                    logger.error(f"Failed to register model lineage: {e}")
                    return False

    async def get_model_lineage(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves lineage information for a specific model."""
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                query = """
                    SELECT model_id, dataset_uri, artifact_uri, created_at, metadata
                    FROM model_lineage
                    WHERE model_id = %s;
                """
                await cur.execute(query, (model_id,))
                result = await cur.fetchone()

                if not result:
                    return None

                return {
                    "model_id": result[0],
                    "dataset_uri": result[1],
                    "artifact_uri": result[2],
                    "registered_at": result[3],
                    "metadata": result[4],
                }
