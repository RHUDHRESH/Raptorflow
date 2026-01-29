"""
Auto Approver - Intelligent automatic approval system

Learns from user patterns to automatically approve low-risk,
similar requests that match historical approval patterns.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ...redis.client import RedisClient
from ..models import ApprovalRequest, RequestType, RiskLevel

logger = logging.getLogger(__name__)


@dataclass
class ApprovalPattern:
    """Pattern for automatic approval."""

    request_type: RequestType
    risk_level: RiskLevel
    content_similarity_threshold: float
    user_approval_rate: float
    pattern_confidence: float


class AutoApprover:
    """Intelligent automatic approval system."""

    def __init__(self, redis_client: Optional[RedisClient] = None):
        self.redis = redis_client or RedisClient()
        self.pattern_key_prefix = "approval_pattern:"
        self.history_key_prefix = "approval_history:"
        self.min_confidence_threshold = 0.85
        self.learning_window_days = 30

    async def check_auto_approval(self, request: ApprovalRequest) -> bool:
        """
        Check if request can be automatically approved.

        Args:
            request: Approval request to check

        Returns:
            True if auto-approval recommended
        """
        try:
            # Skip high-risk requests
            if request.risk_level.value >= RiskLevel.HIGH.value:
                return False

            # Check user's approval history
            user_approval_rate = await self._get_user_approval_rate(request.user_id)
            if user_approval_rate < 0.9:  # Require 90% approval rate
                return False

            # Check content similarity to approved requests
            similarity_score = await self._calculate_content_similarity(request)
            if similarity_score < 0.8:  # Require 80% similarity
                return False

            # Check pattern confidence
            pattern_confidence = await self._get_pattern_confidence(request)
            if pattern_confidence < self.min_confidence_threshold:
                return False

            logger.info(f"Auto-approval recommended for gate {request.gate_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to check auto-approval: {e}")
            return False

    async def learn_from_approval(
        self, request: ApprovalRequest, approved: bool, response_time: float
    ) -> None:
        """
        Learn from approval decision to improve patterns.

        Args:
            request: Original approval request
            approved: Whether it was approved
            response_time: Time to respond in seconds
        """
        try:
            # Record approval history
            history_data = {
                "gate_id": request.gate_id,
                "user_id": request.user_id,
                "request_type": request.request_type.value,
                "risk_level": request.risk_level.value,
                "approved": approved,
                "response_time": response_time,
                "content_hash": self._hash_content(request.output_preview),
                "timestamp": datetime.now().isoformat(),
            }

            history_key = f"{self.history_key_prefix}{request.user_id}"
            await self.redis.lpush(history_key, json.dumps(history_data))
            await self.redis.ltrim(history_key, 0, 999)  # Keep last 1000 records
            await self.redis.expire(history_key, 86400 * self.learning_window_days)

            # Update patterns
            await self._update_patterns(request, approved, response_time)

            logger.info(f"Learned from approval decision for gate {request.gate_id}")

        except Exception as e:
            logger.error(f"Failed to learn from approval: {e}")

    async def get_approval_patterns(self, user_id: str) -> List[ApprovalPattern]:
        """
        Get learned approval patterns for a user.

        Args:
            user_id: User identifier

        Returns:
            List of approval patterns
        """
        try:
            patterns = []

            # Get pattern data
            pattern_key = f"{self.pattern_key_prefix}{user_id}"
            pattern_data = await self.redis.get(pattern_key)

            if pattern_data:
                patterns_json = json.loads(pattern_data)
                for pattern_json in patterns_json:
                    patterns.append(
                        ApprovalPattern(
                            request_type=RequestType(pattern_json["request_type"]),
                            risk_level=RiskLevel(pattern_json["risk_level"]),
                            content_similarity_threshold=pattern_json[
                                "content_similarity_threshold"
                            ],
                            user_approval_rate=pattern_json["user_approval_rate"],
                            pattern_confidence=pattern_json["pattern_confidence"],
                        )
                    )

            return patterns

        except Exception as e:
            logger.error(f"Failed to get approval patterns: {e}")
            return []

    async def _get_user_approval_rate(self, user_id: str) -> float:
        """Calculate user's approval rate."""
        try:
            history_key = f"{self.history_key_prefix}{user_id}"
            history_records = await self.redis.lrange(
                history_key, 0, 99
            )  # Last 100 records

            if not history_records:
                return 0.5  # Default to 50%

            approved_count = 0
            total_count = len(history_records)

            for record in history_records:
                history_data = json.loads(record)
                if history_data.get("approved", False):
                    approved_count += 1

            return approved_count / total_count if total_count > 0 else 0.5

        except Exception as e:
            logger.error(f"Failed to get user approval rate: {e}")
            return 0.5

    async def _calculate_content_similarity(self, request: ApprovalRequest) -> float:
        """Calculate similarity to previously approved content."""
        try:
            content_hash = self._hash_content(request.output_preview)

            # Get user's approval history
            history_key = f"{self.history_key_prefix}{request.user_id}"
            history_records = await self.redis.lrange(
                history_key, 0, 49
            )  # Last 50 records

            if not history_records:
                return 0.0

            similar_approved = 0
            total_similar = 0

            for record in history_records:
                history_data = json.loads(record)

                # Check if similar content type
                if (
                    history_data["request_type"] == request.request_type.value
                    and history_data["risk_level"] == request.risk_level.value
                ):

                    # Simple similarity check based on content hash
                    # In production, this would use more sophisticated NLP
                    total_similar += 1

                    if history_data.get("approved", False):
                        similar_approved += 1

            return similar_approved / total_similar if total_similar > 0 else 0.0

        except Exception as e:
            logger.error(f"Failed to calculate content similarity: {e}")
            return 0.0

    async def _get_pattern_confidence(self, request: ApprovalRequest) -> float:
        """Get confidence score for approval pattern."""
        try:
            patterns = await self.get_approval_patterns(request.user_id)

            for pattern in patterns:
                if (
                    pattern.request_type == request.request_type
                    and pattern.risk_level == request.risk_level
                ):
                    return pattern.pattern_confidence

            # No pattern found, return low confidence
            return 0.0

        except Exception as e:
            logger.error(f"Failed to get pattern confidence: {e}")
            return 0.0

    async def _update_patterns(
        self, request: ApprovalRequest, approved: bool, response_time: float
    ) -> None:
        """Update approval patterns based on new data."""
        try:
            patterns = await self.get_approval_patterns(request.user_id)

            # Find or create pattern for this request type
            pattern = None
            for p in patterns:
                if (
                    p.request_type == request.request_type
                    and p.risk_level == request.risk_level
                ):
                    pattern = p
                    break

            if not pattern:
                # Create new pattern
                pattern = ApprovalPattern(
                    request_type=request.request_type,
                    risk_level=request.risk_level,
                    content_similarity_threshold=0.8,
                    user_approval_rate=0.5,
                    pattern_confidence=0.1,
                )
                patterns.append(pattern)

            # Update pattern with new data
            # Simple learning algorithm - in production would be more sophisticated
            learning_rate = 0.1

            # Update approval rate
            current_rate = pattern.user_approval_rate
            new_rate = current_rate + learning_rate * (
                1.0 if approved else 0.0 - current_rate
            )
            pattern.user_approval_rate = new_rate

            # Update confidence based on consistency
            if abs(new_rate - 0.5) > 0.3:  # Strong preference
                pattern.pattern_confidence = min(
                    1.0, pattern.pattern_confidence + learning_rate
                )
            else:
                pattern.pattern_confidence = max(
                    0.1, pattern.pattern_confidence - learning_rate * 0.5
                )

            # Save updated patterns
            pattern_key = f"{self.pattern_key_prefix}{request.user_id}"
            patterns_json = []

            for p in patterns:
                patterns_json.append(
                    {
                        "request_type": p.request_type.value,
                        "risk_level": p.risk_level.value,
                        "content_similarity_threshold": p.content_similarity_threshold,
                        "user_approval_rate": p.user_approval_rate,
                        "pattern_confidence": p.pattern_confidence,
                    }
                )

            await self.redis.set(
                pattern_key,
                json.dumps(patterns_json),
                ex=86400 * self.learning_window_days,
            )

        except Exception as e:
            logger.error(f"Failed to update patterns: {e}")

    def _hash_content(self, content: str) -> str:
        """Create simple hash of content for similarity matching."""
        # Simple hash for demonstration - in production would use better NLP
        import hashlib

        # Normalize content
        normalized = content.lower().strip()

        # Create hash
        return hashlib.md5(normalized.encode()).hexdigest()[:8]

    async def reset_learning(self, user_id: str) -> bool:
        """
        Reset learning data for a user.

        Args:
            user_id: User identifier

        Returns:
            Success status
        """
        try:
            # Delete history
            history_key = f"{self.history_key_prefix}{user_id}"
            await self.redis.delete(history_key)

            # Delete patterns
            pattern_key = f"{self.pattern_key_prefix}{user_id}"
            await self.redis.delete(pattern_key)

            logger.info(f"Reset learning data for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to reset learning: {e}")
            return False
