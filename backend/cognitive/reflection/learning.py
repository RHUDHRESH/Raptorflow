"""
Reflection Learner - Learns from reflection patterns

Analyzes reflection data to identify common issues and prevent recurring problems.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..models import Issue, Severity

logger = logging.getLogger(__name__)


class ReflectionLearner:
    """Learns from reflection patterns to improve quality."""

    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.learning_key_prefix = "reflection_learning:"

    async def record_reflection(
        self,
        output_id: str,
        initial_score: int,
        final_score: int,
        corrections: List[str],
    ) -> None:
        """
        Record reflection data for learning.

        Args:
            output_id: Unique identifier for the output
            initial_score: Quality score before reflection
            final_score: Quality score after reflection
            corrections: List of corrections applied
        """
        try:
            learning_data = {
                "output_id": output_id,
                "initial_score": initial_score,
                "final_score": final_score,
                "improvement": final_score - initial_score,
                "corrections": corrections,
                "timestamp": datetime.now().isoformat(),
            }

            # Store in Redis if available
            if self.redis:
                key = f"{self.learning_key_prefix}{output_id}"
                await self.redis.set(
                    key, json.dumps(learning_data), ex=86400 * 30
                )  # 30 days

            logger.info(f"Recorded reflection data for {output_id}")

        except Exception as e:
            logger.error(f"Failed to record reflection data: {e}")

    async def get_common_issues(
        self, workspace_id: str, days: int = 7
    ) -> Dict[str, Any]:
        """
        Get common issues from recent reflections.

        Args:
            workspace_id: Workspace identifier
            days: Number of days to analyze

        Returns:
            Dictionary with common issues and patterns
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            # Analyze recent reflection data
            common_issues = {}
            improvement_patterns = []

            if self.redis:
                # Get all reflection keys
                pattern = f"{self.learning_key_prefix}*"
                keys = await self.redis.keys(pattern)

                for key in keys:
                    data = await self.redis.get(key)
                    if data:
                        learning_data = json.loads(data)

                        # Check if within date range
                        timestamp = datetime.fromisoformat(learning_data["timestamp"])
                        if timestamp >= cutoff_date:
                            # Analyze corrections
                            for correction in learning_data.get("corrections", []):
                                issue_type = self._extract_issue_type(correction)
                                if issue_type not in common_issues:
                                    common_issues[issue_type] = 0
                                common_issues[issue_type] += 1

                            # Track improvement patterns
                            improvement = learning_data["improvement"]
                            if improvement > 10:  # Significant improvement
                                improvement_patterns.append(
                                    {
                                        "corrections": learning_data["corrections"],
                                        "improvement": improvement,
                                    }
                                )

            # Sort issues by frequency
            sorted_issues = sorted(
                common_issues.items(), key=lambda x: x[1], reverse=True
            )

            return {
                "common_issues": dict(sorted_issues[:10]),  # Top 10 issues
                "total_reflections": len(common_issues),
                "improvement_patterns": improvement_patterns[:5],  # Top 5 patterns
                "analysis_period_days": days,
            }

        except Exception as e:
            logger.error(f"Failed to get common issues: {e}")
            return {
                "common_issues": {},
                "total_reflections": 0,
                "improvement_patterns": [],
                "analysis_period_days": days,
            }

    async def suggest_preventive_measures(self, workspace_id: str) -> List[str]:
        """
        Suggest preventive measures based on common issues.

        Args:
            workspace_id: Workspace identifier

        Returns:
            List of preventive measure suggestions
        """
        try:
            common_issues_data = await self.get_common_issues(workspace_id)
            common_issues = common_issues_data.get("common_issues", {})

            suggestions = []

            # Generate suggestions based on common issues
            for issue_type, count in common_issues.items():
                if count >= 5:  # Frequent issue
                    suggestion = self._generate_preventive_suggestion(issue_type)
                    if suggestion:
                        suggestions.append(suggestion)

            # Add general suggestions if no specific patterns
            if not suggestions:
                suggestions = [
                    "Continue monitoring reflection patterns",
                    "Consider adding more specific quality criteria",
                    "Review prompt templates for common issues",
                ]

            return suggestions

        except Exception as e:
            logger.error(f"Failed to suggest preventive measures: {e}")
            return ["Unable to generate suggestions due to error"]

    def _extract_issue_type(self, correction: str) -> str:
        """Extract issue type from correction text."""
        correction_lower = correction.lower()

        # Common issue patterns
        if any(word in correction_lower for word in ["accuracy", "factual", "correct"]):
            return "accuracy_issues"
        elif any(
            word in correction_lower for word in ["clarity", "clear", "understand"]
        ):
            return "clarity_issues"
        elif any(word in correction_lower for word in ["complete", "missing", "add"]):
            return "completeness_issues"
        elif any(word in correction_lower for word in ["relevant", "related", "focus"]):
            return "relevance_issues"
        elif any(
            word in correction_lower for word in ["structure", "organize", "format"]
        ):
            return "structure_issues"
        elif any(word in correction_lower for word in ["tone", "voice", "style"]):
            return "tone_issues"
        else:
            return "other_issues"

    def _generate_preventive_suggestion(self, issue_type: str) -> Optional[str]:
        """Generate preventive suggestion for issue type."""
        suggestions = {
            "accuracy_issues": "Add fact-checking step before final output",
            "clarity_issues": "Include clarity review in quality checklist",
            "completeness_issues": "Use comprehensive prompts with all required elements",
            "relevance_issues": "Add relevance validation against user intent",
            "structure_issues": "Apply consistent formatting templates",
            "tone_issues": "Include tone analysis in reflection process",
            "other_issues": "Monitor for emerging patterns and adjust accordingly",
        }

        return suggestions.get(issue_type)
