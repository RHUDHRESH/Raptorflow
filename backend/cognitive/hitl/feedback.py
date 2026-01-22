"""
Feedback Collector - Collects and manages feedback for approvals

Gathers structured feedback, ratings, and corrections from users
to improve system performance and user experience.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ...redis.client import RedisClient
from .models import FeedbackData

logger = logging.getLogger(__name__)


class FeedbackCollector:
    """Collects and manages approval feedback."""

    def __init__(self, redis_client: Optional[RedisClient] = None):
        self.redis = redis_client or RedisClient()
        self.feedback_key_prefix = "approval_feedback:"

    async def request_feedback(
        self, gate_id: str, specific_questions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Request feedback for an approval.

        Args:
            gate_id: Approval gate identifier
            specific_questions: Specific questions to ask

        Returns:
            Feedback request data
        """
        try:
            default_questions = [
                "How satisfied are you with this approval process? (1-5)",
                "Was the approval decision clear and well-explained?",
                "Do you have any suggestions for improvement?",
                "Were there any issues with the output quality?",
            ]

            questions = specific_questions or default_questions

            feedback_request = {
                "gate_id": gate_id,
                "questions": questions,
                "created_at": datetime.now().isoformat(),
                "status": "pending",
            }

            # Store feedback request
            key = f"{self.feedback_key_prefix}request:{gate_id}"
            await self.redis.set(key, json.dumps(feedback_request), ex=86400 * 7)

            logger.info(f"Created feedback request for gate {gate_id}")
            return feedback_request

        except Exception as e:
            logger.error(f"Failed to request feedback: {e}")
            raise

    async def record_feedback(
        self,
        gate_id: str,
        rating: Optional[int] = None,
        comments: Optional[str] = None,
        corrections: Optional[List[str]] = None,
        question_responses: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Record feedback for an approval.

        Args:
            gate_id: Approval gate identifier
            rating: Rating (1-5 scale)
            comments: General comments
            corrections: Suggested corrections
            question_responses: Responses to specific questions

        Returns:
            Success status
        """
        try:
            feedback_data = FeedbackData(
                gate_id=gate_id,
                rating=rating,
                comments=comments,
                corrections=corrections,
            )

            # Store feedback
            key = f"{self.feedback_key_prefix}{gate_id}"
            feedback_json = json.dumps(
                {
                    "gate_id": gate_id,
                    "rating": rating,
                    "comments": comments,
                    "corrections": corrections,
                    "question_responses": question_responses,
                    "timestamp": feedback_data.timestamp.isoformat(),
                }
            )

            await self.redis.set(key, feedback_json, ex=86400 * 30)  # Keep for 30 days

            # Update request status
            request_key = f"{self.feedback_key_prefix}request:{gate_id}"
            request_data = await self.redis.get(request_key)
            if request_data:
                request = json.loads(request_data)
                request["status"] = "completed"
                request["completed_at"] = datetime.now().isoformat()
                await self.redis.set(request_key, json.dumps(request))

            logger.info(f"Recorded feedback for gate {gate_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to record feedback: {e}")
            return False

    async def get_feedback_summary(
        self, workspace_id: str, days: int = 30
    ) -> Dict[str, Any]:
        """
        Get feedback summary for a workspace.

        Args:
            workspace_id: Workspace identifier
            days: Number of days to analyze

        Returns:
            Feedback summary statistics
        """
        try:
            # Get all feedback for workspace
            # This would require workspace_id in feedback keys
            # For now, return placeholder summary

            summary = {
                "total_feedback": 0,
                "average_rating": 0.0,
                "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                "common_issues": [],
                "improvement_suggestions": [],
                "period_days": days,
            }

            # TODO: Implement actual feedback aggregation
            # This would involve:
            # 1. Getting all feedback keys for workspace
            # 2. Parsing and aggregating ratings
            # 3. Analyzing comments for common themes
            # 4. Generating improvement suggestions

            return summary

        except Exception as e:
            logger.error(f"Failed to get feedback summary: {e}")
            return {"total_feedback": 0, "average_rating": 0.0, "error": str(e)}

    async def get_feedback_for_gate(self, gate_id: str) -> Optional[Dict[str, Any]]:
        """
        Get feedback for a specific approval gate.

        Args:
            gate_id: Gate identifier

        Returns:
            Feedback data or None
        """
        try:
            key = f"{self.feedback_key_prefix}{gate_id}"
            data = await self.redis.get(key)

            if data:
                return json.loads(data)

            return None

        except Exception as e:
            logger.error(f"Failed to get feedback for gate {gate_id}: {e}")
            return None

    async def apply_corrections(self, gate_id: str, corrections: List[str]) -> bool:
        """
        Apply suggested corrections from feedback.

        Args:
            gate_id: Gate identifier
            corrections: List of corrections to apply

        Returns:
            Success status
        """
        try:
            # Store corrections for later application
            corrections_key = f"{self.feedback_key_prefix}corrections:{gate_id}"
            corrections_data = {
                "gate_id": gate_id,
                "corrections": corrections,
                "created_at": datetime.now().isoformat(),
                "status": "pending",
            }

            await self.redis.set(
                corrections_key, json.dumps(corrections_data), ex=86400 * 7
            )

            logger.info(f"Stored {len(corrections)} corrections for gate {gate_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to apply corrections: {e}")
            return False

    async def get_pending_corrections(self, workspace_id: str) -> List[Dict[str, Any]]:
        """
        Get pending corrections for a workspace.

        Args:
            workspace_id: Workspace identifier

        Returns:
            List of pending corrections
        """
        try:
            # This would need to query by workspace_id
            # For now, return empty list
            return []

        except Exception as e:
            logger.error(f"Failed to get pending corrections: {e}")
            return []
