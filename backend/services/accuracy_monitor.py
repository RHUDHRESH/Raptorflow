import logging
from typing import Dict, Any, Optional
from backend.db import get_db_connection

logger = logging.getLogger("raptorflow.services.accuracy_monitor")

class ModelAccuracyMonitor:
    """
    SOTA Model Accuracy Monitor.
    Integrates human-in-the-loop feedback to track agent decision quality.
    Enables long-term reinforcement learning and performance auditing.
    """

    async def log_feedback(
        self, 
        workspace_id: str, 
        decision_id: str, 
        is_accurate: bool, 
        feedback_text: Optional[str] = None
    ) -> bool:
        """Logs accuracy feedback for a specific agent decision."""
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                query = """
                    UPDATE agent_decision_audit
                    SET 
                        accuracy_validated = TRUE,
                        is_accurate = %s,
                        feedback_notes = %s
                    WHERE id = %s AND tenant_id = %s;
                """
                try:
                    await cur.execute(query, (is_accurate, feedback_text, decision_id, workspace_id))
                    await conn.commit()
                    logger.info(f"Accuracy logged for decision {decision_id}: {is_accurate}")
                    return True
                except Exception as e:
                    logger.error(f"Failed to log accuracy feedback: {e}")
                    return False

    async def get_metrics(self, workspace_id: str) -> Dict[str, Any]:
        """Calculates accuracy metrics based on validated decisions."""
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                query = """
                    SELECT 
                        COUNT(*) FILTER (WHERE is_accurate = TRUE) as correct,
                        COUNT(*) FILTER (WHERE is_accurate = FALSE) as incorrect
                    FROM agent_decision_audit
                    WHERE tenant_id = %s AND accuracy_validated = TRUE;
                """
                await cur.execute(query, (workspace_id,))
                result = await cur.fetchone()
                
                correct = result[0] or 0
                incorrect = result[1] or 0
                total = correct + incorrect
                
                rate = correct / total if total > 0 else 1.0
                
                return {
                    "accuracy_rate": rate,
                    "total_validated": total,
                    "correct_count": correct,
                    "incorrect_count": incorrect
                }
