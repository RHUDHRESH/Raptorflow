"""
Execution Supervisor - Orchestrates content publishing across platforms.
Manages publishing tasks, delegates to platform-specific agents, and tracks status.
"""

import structlog
from typing import Dict, Any, List, Optional, Literal
from uuid import UUID, uuid4
from datetime import datetime

from backend.agents.base_agent import BaseSupervisor
from backend.agents.execution.linkedin_agent import linkedin_agent
from backend.agents.execution.scheduler_agent import scheduler_agent
from backend.agents.execution.twitter_agent import twitter_agent
from backend.agents.execution.instagram_agent import instagram_agent
from backend.agents.execution.email_agent import email_agent
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import get_correlation_id
from backend.utils.queue import redis_queue

logger = structlog.get_logger(__name__)


class ExecutionSupervisor(BaseSupervisor):
    """
    Tier 1 Supervisor for Execution Domain.

    Responsibilities:
    - Manage publishing tasks across platforms
    - Validate content approval status before publishing
    - Delegate to platform-specific publisher agents
    - Track publishing job status
    - Handle scheduling and batch operations
    """

    def __init__(self):
        super().__init__("execution_supervisor")

        # Register platform-specific publisher agents
        self.publishers = {
            "linkedin": linkedin_agent,
            "twitter": twitter_agent,
            "instagram": instagram_agent,
            "email": email_agent,
        }

        # Register scheduler agent
        self.scheduler = scheduler_agent

    async def execute(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute publishing workflow based on goal.

        Args:
            goal: High-level publishing goal (e.g., "publish_content", "schedule_campaign")
            context: Execution context with content IDs, channels, etc.

        Returns:
            Execution result with job IDs and status
        """
        correlation_id = context.get("correlation_id") or get_correlation_id()
        self.log(f"Executing: {goal}", correlation_id=correlation_id)

        # Route to appropriate handler
        if "publish" in goal.lower():
            return await self.publish_content(context, correlation_id)
        elif "schedule" in goal.lower():
            return await self.schedule_content(context, correlation_id)
        elif "status" in goal.lower():
            return await self.get_publishing_status(context, correlation_id)
        else:
            return {
                "status": "error",
                "message": f"Unknown execution goal: {goal}",
                "correlation_id": correlation_id
            }

    async def publish_content(
        self,
        payload: Dict[str, Any],
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Publishes content to specified platforms.

        Args:
            payload: {
                "content_id": UUID,
                "variant_id": str,
                "channels": List[str],  # ["linkedin", "twitter", etc.]
                "workspace_id": UUID,
                "schedule_time": Optional[datetime],
                "account_ids": Optional[Dict[str, str]]  # Platform-specific account IDs
            }

        Returns:
            Dict with job IDs and publishing status
        """
        correlation_id = correlation_id or get_correlation_id()

        content_id = payload.get("content_id")
        variant_id = payload.get("variant_id")
        channels = payload.get("channels", [])
        workspace_id = payload.get("workspace_id")
        schedule_time = payload.get("schedule_time")
        account_ids = payload.get("account_ids", {})

        logger.info(
            "Publishing content",
            content_id=content_id,
            channels=channels,
            scheduled=schedule_time is not None,
            correlation_id=correlation_id
        )

        # Validate content exists and is approved
        validation_result = await self._validate_content_for_publishing(
            content_id,
            variant_id,
            workspace_id,
            correlation_id
        )

        if not validation_result["is_valid"]:
            return {
                "status": "rejected",
                "reason": validation_result["reason"],
                "correlation_id": correlation_id
            }

        content_data = validation_result["content"]

        # Publish to each channel
        publishing_results = []

        for channel in channels:
            publisher = self.publishers.get(channel)

            if not publisher:
                logger.warning(f"No publisher for channel: {channel}", correlation_id=correlation_id)
                publishing_results.append({
                    "channel": channel,
                    "status": "failed",
                    "error": f"Unsupported platform: {channel}"
                })
                continue

            try:
                # Delegate to platform-specific agent
                account_id = account_ids.get(channel)

                if channel == "linkedin":
                    result = await linkedin_agent.post_to_linkedin(
                        variant=content_data,
                        workspace_id=workspace_id,
                        account_type="profile",
                        account_id=account_id,
                        schedule_time=schedule_time,
                        correlation_id=correlation_id
                    )
                elif channel == "email":
                    result = await email_agent.send_email(
                        variant=content_data,
                        workspace_id=workspace_id,
                        schedule_time=schedule_time,
                        correlation_id=correlation_id
                    )
                else:
                    # Generic handler for other platforms
                    result = await self._publish_to_platform(
                        publisher,
                        content_data,
                        workspace_id,
                        channel,
                        account_id,
                        schedule_time,
                        correlation_id
                    )

                publishing_results.append({
                    "channel": channel,
                    **result
                })

            except Exception as e:
                logger.error(
                    f"Failed to publish to {channel}",
                    error=str(e),
                    correlation_id=correlation_id
                )
                publishing_results.append({
                    "channel": channel,
                    "status": "failed",
                    "error": str(e)
                })

        # Create publishing job record
        job_id = str(uuid4())
        await self._create_publishing_job(
            job_id=job_id,
            content_id=content_id,
            workspace_id=workspace_id,
            channels=channels,
            results=publishing_results,
            correlation_id=correlation_id
        )

        return {
            "status": "completed",
            "job_id": job_id,
            "results": publishing_results,
            "total_channels": len(channels),
            "successful": len([r for r in publishing_results if r.get("status") == "published"]),
            "failed": len([r for r in publishing_results if r.get("status") == "failed"]),
            "scheduled": len([r for r in publishing_results if r.get("status") == "scheduled"]),
            "correlation_id": correlation_id
        }

    async def schedule_content(
        self,
        payload: Dict[str, Any],
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Schedules content for future publication.

        Args:
            payload: {
                "content_ids": List[UUID],
                "workspace_id": UUID,
                "move_id": UUID,
                "start_date": datetime,
                "end_date": datetime,
                "platforms": List[str]
            }

        Returns:
            Schedule confirmation with timestamps
        """
        correlation_id = correlation_id or get_correlation_id()

        workspace_id = payload.get("workspace_id")
        move_id = payload.get("move_id")
        content_ids = payload.get("content_ids", [])
        start_date = payload.get("start_date")
        end_date = payload.get("end_date")
        platforms = payload.get("platforms", ["linkedin"])

        logger.info(
            "Scheduling content batch",
            content_count=len(content_ids),
            move_id=move_id,
            correlation_id=correlation_id
        )

        # Fetch content variants
        content_variants = []
        for content_id in content_ids:
            content = await supabase_client.fetch_one(
                "generated_content",
                {"id": str(content_id), "workspace_id": str(workspace_id)}
            )
            if content:
                content_variants.append({
                    "id": content_id,
                    "platform": platforms[0] if platforms else "linkedin",
                    "content": content
                })

        # Delegate to scheduler agent
        scheduled_posts = await self.scheduler.schedule_content_batch(
            workspace_id=workspace_id,
            move_id=move_id,
            content_variants=content_variants,
            start_date=start_date,
            end_date=end_date,
            correlation_id=correlation_id
        )

        # Save schedule to database
        for scheduled_post in scheduled_posts:
            await supabase_client.insert("scheduled_posts", {
                "id": str(uuid4()),
                "workspace_id": str(workspace_id),
                "move_id": str(move_id),
                "content_id": scheduled_post["content_id"],
                "platform": scheduled_post["platform"],
                "scheduled_time": scheduled_post["scheduled_time"],
                "status": "scheduled",
                "created_at": datetime.utcnow().isoformat()
            })

        return {
            "status": "scheduled",
            "scheduled_count": len(scheduled_posts),
            "schedule": scheduled_posts,
            "correlation_id": correlation_id
        }

    async def get_publishing_status(
        self,
        payload: Dict[str, Any],
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Gets the status of a publishing job.

        Args:
            payload: {"job_id": str}

        Returns:
            Job status and results
        """
        correlation_id = correlation_id or get_correlation_id()
        job_id = payload.get("job_id")

        logger.info("Fetching job status", job_id=job_id, correlation_id=correlation_id)

        job_data = await supabase_client.fetch_one("publishing_jobs", {"id": job_id})

        if not job_data:
            return {
                "status": "not_found",
                "job_id": job_id,
                "correlation_id": correlation_id
            }

        return {
            "status": "found",
            "job": job_data,
            "correlation_id": correlation_id
        }

    async def _validate_content_for_publishing(
        self,
        content_id: UUID,
        variant_id: str,
        workspace_id: UUID,
        correlation_id: str
    ) -> Dict[str, Any]:
        """
        Validates that content is approved and ready for publishing.

        Returns:
            Dict with is_valid, reason, and content data
        """
        logger.info(
            "Validating content for publishing",
            content_id=content_id,
            correlation_id=correlation_id
        )

        # Fetch content from database
        content_data = await supabase_client.fetch_one(
            "generated_content",
            {"id": str(content_id), "workspace_id": str(workspace_id)}
        )

        if not content_data:
            return {
                "is_valid": False,
                "reason": "Content not found",
                "content": None
            }

        # Check approval status
        status = content_data.get("status")
        if status != "approved":
            return {
                "is_valid": False,
                "reason": f"Content must be approved before publishing (current status: {status})",
                "content": None
            }

        # Find the specific variant
        variants = content_data.get("variants", [])
        selected_variant = None

        for variant in variants:
            if variant.get("variant_id") == variant_id:
                selected_variant = variant
                break

        if not selected_variant:
            return {
                "is_valid": False,
                "reason": f"Variant {variant_id} not found",
                "content": None
            }

        return {
            "is_valid": True,
            "reason": None,
            "content": selected_variant
        }

    async def _publish_to_platform(
        self,
        publisher: Any,
        content: Dict[str, Any],
        workspace_id: UUID,
        platform: str,
        account_id: Optional[str],
        schedule_time: Optional[datetime],
        correlation_id: str
    ) -> Dict[str, Any]:
        """
        Generic platform publishing handler.
        """
        # This would be implemented based on the specific publisher's interface
        # For now, return a placeholder
        return {
            "status": "pending",
            "message": f"Publishing to {platform} not yet implemented",
            "platform": platform
        }

    async def _create_publishing_job(
        self,
        job_id: str,
        content_id: UUID,
        workspace_id: UUID,
        channels: List[str],
        results: List[Dict[str, Any]],
        correlation_id: str
    ) -> None:
        """
        Creates a publishing job record in the database.
        """
        try:
            await supabase_client.insert("publishing_jobs", {
                "id": job_id,
                "workspace_id": str(workspace_id),
                "content_id": str(content_id),
                "channels": channels,
                "results": results,
                "status": "completed",
                "created_at": datetime.utcnow().isoformat(),
                "correlation_id": correlation_id
            })
            logger.info("Publishing job created", job_id=job_id, correlation_id=correlation_id)
        except Exception as e:
            logger.error(f"Failed to create publishing job: {e}", correlation_id=correlation_id)


# Global instance
execution_supervisor = ExecutionSupervisor()
