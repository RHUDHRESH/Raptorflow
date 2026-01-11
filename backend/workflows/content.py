"""
ContentWorkflow - End-to-end content generation orchestration.
Handles content generation, review, and publishing with full quality control.
"""

import logging
import time
from typing import Any, Dict, List, Optional

from agents.dispatcher import AgentDispatcher
from agents.state import AgentState
from cognitive import CognitiveEngine
from memory.controller import MemoryController

from supabase import Client

logger = logging.getLogger(__name__)


class ContentWorkflow:
    """
    End-to-end content workflow orchestrator.

    Handles the complete content lifecycle from generation request
    through creation, review, revision, and publishing.
    """

    def __init__(
        self,
        db_client: Client,
        memory_controller: MemoryController,
        cognitive_engine: CognitiveEngine,
        agent_dispatcher: AgentDispatcher,
    ):
        self.db_client = db_client
        self.memory_controller = memory_controller
        self.cognitive_engine = cognitive_engine
        self.agent_dispatcher = agent_dispatcher

    async def generate_content(
        self, workspace_id: str, request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate content based on request with full orchestration.

        Args:
            workspace_id: Workspace ID
            request: Content generation request

        Returns:
            Content generation result
        """
        try:
            logger.info(f"Generating content for workspace {workspace_id}")

            # Get workspace context
            context = await self._get_workspace_context(workspace_id)

            # Step 1: Route to appropriate agent
            routing_result = await self._route_content_request(
                workspace_id, request, context
            )

            if not routing_result["success"]:
                return routing_result

            # Step 2: Generate content
            generation_result = await self._generate_content_with_agent(
                workspace_id, request, routing_result["agent"], context
            )

            if not generation_result["success"]:
                return generation_result

            # Step 3: Quality check
            quality_result = await self._quality_check_content(
                generation_result["content"], workspace_id, context
            )

            # Step 4: Store content
            storage_result = await self._store_content(
                workspace_id, generation_result["content"], request, quality_result
            )

            # Step 5: Create review request if needed
            review_needed = quality_result["score"] < 0.8 or request.get(
                "require_review", False
            )

            if review_needed:
                review_result = await self._create_review_request(
                    storage_result["content_id"], quality_result
                )
            else:
                review_result = {"review_needed": False}

            return {
                "success": True,
                "content_id": storage_result["content_id"],
                "content": generation_result["content"],
                "agent_used": routing_result["agent"],
                "quality_score": quality_result["score"],
                "review_needed": review_needed,
                "review_request": review_result,
            }

        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return {"success": False, "error": str(e)}

    async def review_content(self, content_id: str) -> Dict[str, Any]:
        """
        Review content with quality assessment and feedback.

        Args:
            content_id: Content ID to review

        Returns:
            Content review result
        """
        try:
            logger.info(f"Reviewing content: {content_id}")

            # Get content details
            content_result = (
                self.db_client.table("muse_assets")
                .select("*")
                .eq("id", content_id)
                .execute()
            )

            if not content_result.data:
                return {"success": False, "error": "Content not found"}

            content = content_result.data[0]
            workspace_id = content["workspace_id"]

            # Get workspace context
            context = await self._get_workspace_context(workspace_id)

            # Step 1: Quality assessment
            quality_result = await self._quality_check_content(
                content["content"], workspace_id, context
            )

            # Step 2: Generate feedback
            feedback_result = await self._generate_content_feedback(
                content["content"], quality_result, context
            )

            # Step 3: Update content record
            self.db_client.table("muse_assets").update(
                {
                    "quality_score": quality_result["score"],
                    "review_status": "reviewed",
                    "review_feedback": feedback_result,
                    "reviewed_at": time.time(),
                }
            ).eq("id", content_id).execute()

            # Step 4: Determine if revision needed
            revision_needed = quality_result["score"] < 0.7 or feedback_result.get(
                "major_issues", []
            )

            return {
                "success": True,
                "content_id": content_id,
                "quality_score": quality_result["score"],
                "feedback": feedback_result,
                "revision_needed": revision_needed,
                "review_completed": True,
            }

        except Exception as e:
            logger.error(f"Error reviewing content {content_id}: {e}")
            return {"success": False, "error": str(e)}

    async def revise_content(
        self, content_id: str, feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Revise content based on feedback.

        Args:
            content_id: Content ID to revise
            feedback: Review feedback

        Returns:
            Content revision result
        """
        try:
            logger.info(f"Revising content: {content_id}")

            # Get content details
            content_result = (
                self.db_client.table("muse_assets")
                .select("*")
                .eq("id", content_id)
                .execute()
            )

            if not content_result.data:
                return {"success": False, "error": "Content not found"}

            content = content_result.data[0]
            workspace_id = content["workspace_id"]

            # Get workspace context
            context = await self._get_workspace_context(workspace_id)

            # Step 1: Generate revised content
            revision_result = await self._generate_content_revision(
                content["content"], feedback, content["agent_generated"], context
            )

            if not revision_result["success"]:
                return revision_result

            # Step 2: Quality check revised content
            quality_result = await self._quality_check_content(
                revision_result["content"], workspace_id, context
            )

            # Step 3: Update content record
            self.db_client.table("muse_assets").update(
                {
                    "content": revision_result["content"],
                    "quality_score": quality_result["score"],
                    "revision_count": content.get("revision_count", 0) + 1,
                    "last_revised_at": time.time(),
                    "review_status": "revised",
                }
            ).eq("id", content_id).execute()

            # Step 4: Store revision history
            await self._store_revision_history(
                content_id, content["content"], revision_result["content"]
            )

            return {
                "success": True,
                "content_id": content_id,
                "revised_content": revision_result["content"],
                "quality_score": quality_result["score"],
                "revision_count": content.get("revision_count", 0) + 1,
            }

        except Exception as e:
            logger.error(f"Error revising content {content_id}: {e}")
            return {"success": False, "error": str(e)}

    async def publish_content(
        self, content_id: str, publish_options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Publish content to specified channels.

        Args:
            content_id: Content ID to publish
            publish_options: Publishing options

        Returns:
            Content publishing result
        """
        try:
            logger.info(f"Publishing content: {content_id}")

            # Get content details
            content_result = (
                self.db_client.table("muse_assets")
                .select("*")
                .eq("id", content_id)
                .execute()
            )

            if not content_result.data:
                return {"success": False, "error": "Content not found"}

            content = content_result.data[0]
            workspace_id = content["workspace_id"]

            # Validate content is ready for publishing
            if content["quality_score"] < 0.7:
                return {
                    "success": False,
                    "error": "Content quality too low for publishing",
                }

            # Step 1: Prepare content for publishing
            prepared_content = await self._prepare_content_for_publishing(
                content, publish_options
            )

            # Step 2: Publish to channels
            publish_results = []
            channels = (
                publish_options.get("channels", ["internal"])
                if publish_options
                else ["internal"]
            )

            for channel in channels:
                channel_result = await self._publish_to_channel(
                    content_id, prepared_content, channel, workspace_id
                )
                publish_results.append(channel_result)

            # Step 3: Update content status
            successful_publishes = [r for r in publish_results if r["success"]]

            self.db_client.table("muse_assets").update(
                {
                    "status": "published" if successful_publishes else "publish_failed",
                    "published_at": time.time() if successful_publishes else None,
                    "publish_channels": successful_publishes,
                    "publish_results": publish_results,
                }
            ).eq("id", content_id).execute()

            # Step 4: Track analytics
            await self._track_content_analytics(content_id, successful_publishes)

            return {
                "success": len(successful_publishes) > 0,
                "content_id": content_id,
                "published_channels": successful_publishes,
                "publish_results": publish_results,
                "published_at": time.time() if successful_publishes else None,
            }

        except Exception as e:
            logger.error(f"Error publishing content {content_id}: {e}")
            return {"success": False, "error": str(e)}

    async def _route_content_request(
        self, workspace_id: str, request: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route content request to appropriate agent."""
        try:
            content_type = request.get("content_type", "general")

            # Define routing rules
            routing_map = {
                "email": "email_specialist",
                "blog": "blog_writer",
                "social": "social_media_agent",
                "ad_copy": "content_creator",
                "newsletter": "content_creator",
                "website": "content_creator",
                "marketing": "content_creator",
                "general": "content_creator",
            }

            agent_name = routing_map.get(content_type, "content_creator")

            # Verify agent is available
            agent = self.agent_dispatcher.get_agent(agent_name)
            if not agent:
                return {"success": False, "error": f"Agent {agent_name} not available"}

            return {"success": True, "agent": agent_name, "content_type": content_type}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _generate_content_with_agent(
        self,
        workspace_id: str,
        request: Dict[str, Any],
        agent_name: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate content using specified agent."""
        try:
            agent = self.agent_dispatcher.get_agent(agent_name)

            state = AgentState()
            state.update(
                {
                    "workspace_id": workspace_id,
                    "user_id": context["user_id"],
                    "content_request": request,
                    "messages": [],
                }
            )

            result = await agent.execute(state)

            content = result.get("generated_content", "")

            if not content:
                return {"success": False, "error": "No content generated"}

            return {"success": True, "content": content, "agent_result": result}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _quality_check_content(
        self, content: str, workspace_id: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform quality check on content."""
        try:
            # Use cognitive engine for quality check
            quality_result = await self.cognitive_engine.reflection.reflect(
                output=content,
                goal="Assess content quality",
                context=context,
                max_iterations=2,
            )

            return {
                "score": quality_result.quality_score,
                "feedback": quality_result.feedback,
                "approved": quality_result.approved,
                "improvements": quality_result.improvements,
            }

        except Exception as e:
            return {"score": 0.0, "error": str(e)}

    async def _store_content(
        self,
        workspace_id: str,
        content: str,
        request: Dict[str, Any],
        quality_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Store content in database."""
        try:
            content_record = {
                "workspace_id": workspace_id,
                "title": request.get("title", "Generated Content"),
                "content": content,
                "content_type": request.get("content_type", "general"),
                "agent_generated": True,
                "quality_score": quality_result["score"],
                "status": "draft",
                "revision_count": 0,
                "created_at": time.time(),
            }

            result = (
                self.db_client.table("muse_assets").insert(content_record).execute()
            )

            if result.data:
                return {"content_id": result.data[0]["id"], "success": True}
            else:
                return {"success": False, "error": "Failed to store content"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _create_review_request(
        self, content_id: str, quality_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create review request for content."""
        try:
            review_request = {
                "content_id": content_id,
                "quality_score": quality_result["score"],
                "feedback": quality_result["feedback"],
                "status": "pending",
                "created_at": time.time(),
            }

            result = (
                self.db_client.table("content_reviews").insert(review_request).execute()
            )

            return {
                "review_needed": True,
                "review_id": result.data[0]["id"] if result.data else None,
            }

        except Exception as e:
            return {"review_needed": False, "error": str(e)}

    async def _generate_content_feedback(
        self, content: str, quality_result: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate detailed feedback for content."""
        try:
            # Use content creator agent for feedback
            agent = self.agent_dispatcher.get_agent("content_creator")

            state = AgentState()
            state.update(
                {
                    "task": "generate_content_feedback",
                    "content": content,
                    "quality_assessment": quality_result,
                    "context": context,
                }
            )

            result = await agent.execute(state)

            return result.get("feedback", {})

        except Exception as e:
            return {"error": str(e)}

    async def _generate_content_revision(
        self,
        original_content: str,
        feedback: Dict[str, Any],
        agent_generated: bool,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate revised content based on feedback."""
        try:
            # Use same agent that generated original content
            agent_name = "content_creator"  # Default, could be enhanced
            agent = self.agent_dispatcher.get_agent(agent_name)

            state = AgentState()
            state.update(
                {
                    "task": "revise_content",
                    "original_content": original_content,
                    "feedback": feedback,
                    "context": context,
                }
            )

            result = await agent.execute(state)

            revised_content = result.get("revised_content", "")

            if not revised_content:
                return {"success": False, "error": "No revised content generated"}

            return {"success": True, "content": revised_content}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _store_revision_history(
        self, content_id: str, original_content: str, revised_content: str
    ):
        """Store revision history for content."""
        try:
            revision_record = {
                "content_id": content_id,
                "original_content": original_content,
                "revised_content": revised_content,
                "revision_timestamp": time.time(),
            }

            self.db_client.table("content_revisions").insert(revision_record).execute()

        except Exception as e:
            logger.error(f"Error storing revision history: {e}")

    async def _prepare_content_for_publishing(
        self, content: Dict[str, Any], publish_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare content for publishing."""
        try:
            prepared = {
                "title": content.get("title"),
                "content": content.get("content"),
                "content_type": content.get("content_type"),
                "metadata": {
                    "content_id": content["id"],
                    "quality_score": content.get("quality_score"),
                    "created_at": content.get("created_at"),
                },
            }

            # Apply publishing options
            if publish_options:
                prepared.update(
                    {
                        "publishing_options": publish_options,
                        "customizations": publish_options.get("customizations", {}),
                    }
                )

            return prepared

        except Exception as e:
            return {"error": str(e)}

    async def _publish_to_channel(
        self,
        content_id: str,
        prepared_content: Dict[str, Any],
        channel: str,
        workspace_id: str,
    ) -> Dict[str, Any]:
        """Publish content to specific channel."""
        try:
            if channel == "internal":
                # Internal publishing - just mark as published
                return {
                    "success": True,
                    "channel": channel,
                    "published_at": time.time(),
                    "publish_url": f"/content/{content_id}",
                }
            elif channel == "email":
                # Email publishing - would integrate with email service
                return await self._publish_via_email(prepared_content, workspace_id)
            elif channel == "social":
                # Social media publishing - would integrate with social APIs
                return await self._publish_via_social(prepared_content, workspace_id)
            else:
                return {"success": False, "error": f"Unknown channel: {channel}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _publish_via_email(
        self, content: Dict[str, Any], workspace_id: str
    ) -> Dict[str, Any]:
        """Publish content via email."""
        try:
            # This would integrate with email service
            # For now, return success
            return {
                "success": True,
                "channel": "email",
                "published_at": time.time(),
                "email_id": f"email_{int(time.time())}",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _publish_via_social(
        self, content: Dict[str, Any], workspace_id: str
    ) -> Dict[str, Any]:
        """Publish content via social media."""
        try:
            # This would integrate with social media APIs
            # For now, return success
            return {
                "success": True,
                "channel": "social",
                "published_at": time.time(),
                "social_post_id": f"social_{int(time.time())}",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _track_content_analytics(
        self, content_id: str, publish_results: List[Dict[str, Any]]
    ):
        """Track content analytics after publishing."""
        try:
            # Create analytics record
            analytics_record = {
                "content_id": content_id,
                "publish_results": publish_results,
                "tracked_at": time.time(),
            }

            self.db_client.table("content_analytics").insert(analytics_record).execute()

        except Exception as e:
            logger.error(f"Error tracking content analytics: {e}")

    async def _get_workspace_context(self, workspace_id: str) -> Dict[str, Any]:
        """Get workspace context."""
        try:
            workspace_result = (
                self.db_client.table("workspaces")
                .select("*")
                .eq("id", workspace_id)
                .execute()
            )

            if workspace_result.data:
                workspace = workspace_result.data[0]
                return {
                    "workspace_id": workspace_id,
                    "user_id": workspace["user_id"],
                    "workspace": workspace,
                }
            else:
                return {"workspace_id": workspace_id, "user_id": None}

        except Exception as e:
            logger.error(f"Error getting workspace context: {e}")
            return {"workspace_id": workspace_id, "user_id": None}
