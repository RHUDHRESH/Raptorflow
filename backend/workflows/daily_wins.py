"""
DailyWinsWorkflow - End-to-end daily wins orchestration.
Handles daily win generation, expansion, and scheduling.
"""

import logging
import time
from typing import Any, Dict, List, Optional

from backend.agents.dispatcher import AgentDispatcher
from backend.agents.state import AgentState
from backend.cognitive import CognitiveEngine
from backend.memory.controller import MemoryController

from supabase import Client

logger = logging.getLogger(__name__)


class DailyWinsWorkflow:
    """
    End-to-end daily wins workflow orchestrator.

    Handles the complete daily wins process from generation
    through content expansion, scheduling, and publishing.
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

    async def generate_today(self, workspace_id: str) -> Dict[str, Any]:
        """
        Generate today's daily wins with full orchestration.

        Args:
            workspace_id: Workspace ID

        Returns:
            Daily wins generation result
        """
        try:
            logger.info(f"Generating daily wins for workspace {workspace_id}")

            # Get workspace context
            context = await self._get_workspace_context(workspace_id)

            # Step 1: Get today's context
            today_context = await self._get_today_context(workspace_id, context)

            # Step 2: Generate daily wins
            wins_result = await self._generate_daily_wins(
                workspace_id, today_context, context
            )

            if not wins_result["success"]:
                return wins_result

            # Step 3: Store daily wins
            storage_result = await self._store_daily_wins(
                workspace_id, wins_result["wins"], today_context
            )

            # Step 4: Create expansion tasks
            await self._create_expansion_tasks(storage_result["daily_wins_id"])

            return {
                "success": True,
                "daily_wins_id": storage_result["daily_wins_id"],
                "wins": wins_result["wins"],
                "context": today_context,
                "generated_at": time.time(),
            }

        except Exception as e:
            logger.error(f"Error generating daily wins: {e}")
            return {"success": False, "error": str(e)}

    async def expand_win(self, win_id: str) -> Dict[str, Any]:
        """
        Expand a daily win into full content.

        Args:
            win_id: Win ID to expand

        Returns:
            Win expansion result
        """
        try:
            logger.info(f"Expanding daily win: {win_id}")

            # Get win details
            win_result = (
                self.db_client.table("daily_wins")
                .select("*")
                .eq("id", win_id)
                .execute()
            )

            if not win_result.data:
                return {"success": False, "error": "Daily win not found"}

            win = win_result.data[0]
            workspace_id = win["workspace_id"]

            # Get workspace context
            context = await self._get_workspace_context(workspace_id)

            # Step 1: Generate expanded content
            expansion_result = await self._generate_expanded_content(win, context)

            if not expansion_result["success"]:
                return expansion_result

            # Step 2: Quality check
            quality_result = await self._quality_check_content(
                expansion_result["content"], workspace_id, context
            )

            # Step 3: Store expanded content
            storage_result = await self._store_expanded_content(
                win_id, expansion_result["content"], quality_result
            )

            # Step 4: Update win status
            self.db_client.table("daily_wins").update(
                {
                    "status": "expanded",
                    "expanded_at": time.time(),
                    "content_id": storage_result.get("content_id"),
                    "quality_score": quality_result["score"],
                }
            ).eq("id", win_id).execute()

            return {
                "success": True,
                "win_id": win_id,
                "expanded_content": expansion_result["content"],
                "content_id": storage_result.get("content_id"),
                "quality_score": quality_result["score"],
                "expanded_at": time.time(),
            }

        except Exception as e:
            logger.error(f"Error expanding win {win_id}: {e}")
            return {"success": False, "error": str(e)}

    async def schedule_win(
        self, win_id: str, platform: str, schedule_options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Schedule a daily win for publishing.

        Args:
            win_id: Win ID to schedule
            platform: Platform to schedule for
            schedule_options: Scheduling options

        Returns:
            Scheduling result
        """
        try:
            logger.info(f"Scheduling daily win {win_id} for {platform}")

            # Get win details
            win_result = (
                self.db_client.table("daily_wins")
                .select("*")
                .eq("id", win_id)
                .execute()
            )

            if not win_result.data:
                return {"success": False, "error": "Daily win not found"}

            win = win_result.data[0]
            workspace_id = win["workspace_id"]

            # Validate win is expanded
            if win["status"] != "expanded":
                return {
                    "success": False,
                    "error": "Win must be expanded before scheduling",
                }

            # Step 1: Prepare content for platform
            prepared_content = await self._prepare_content_for_platform(
                win, platform, schedule_options
            )

            # Step 2: Schedule publishing
            schedule_result = await self._schedule_content_publishing(
                win_id, prepared_content, platform, schedule_options
            )

            # Step 3: Update win status
            self.db_client.table("daily_wins").update(
                {
                    "status": "scheduled",
                    "scheduled_platform": platform,
                    "scheduled_at": time.time(),
                    "publishing_options": schedule_options,
                }
            ).eq("id", win_id).execute()

            return {
                "success": True,
                "win_id": win_id,
                "platform": platform,
                "schedule_id": schedule_result.get("schedule_id"),
                "scheduled_at": time.time(),
                "publish_time": schedule_result.get("publish_time"),
            }

        except Exception as e:
            logger.error(f"Error scheduling win {win_id}: {e}")
            return {"success": False, "error": str(e)}

    async def _get_today_context(
        self, workspace_id: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get today's context for daily wins generation."""
        try:
            today_context = {
                "date": time.strftime("%Y-%m-%d"),
                "day_of_week": time.strftime("%A"),
                "workspace_id": workspace_id,
                "recent_activities": [],
                "upcoming_events": [],
                "current_focus": [],
                "team_mood": "positive",  # Could be enhanced with actual data
                "business_context": {},
            }

            # Get recent moves
            recent_moves = (
                self.db_client.table("moves")
                .select("*")
                .eq("workspace_id", workspace_id)
                .order("created_at", desc=True)
                .limit(5)
                .execute()
            )
            if recent_moves.data:
                today_context["recent_activities"] = [
                    {"type": "move", "title": move["title"], "status": move["status"]}
                    for move in recent_moves.data
                ]

            # Get upcoming campaigns
            upcoming_campaigns = (
                self.db_client.table("campaigns")
                .select("*")
                .eq("workspace_id", workspace_id)
                .eq("status", "active")
                .execute()
            )
            if upcoming_campaigns.data:
                today_context["upcoming_events"] = [
                    {
                        "type": "campaign",
                        "name": campaign["name"],
                        "status": campaign["status"],
                    }
                    for campaign in upcoming_campaigns.data
                ]

            # Get foundation data for business context
            foundation_result = (
                self.db_client.table("foundations")
                .select("*")
                .eq("workspace_id", workspace_id)
                .execute()
            )
            if foundation_result.data:
                foundation = foundation_result.data[0]
                today_context["business_context"] = {
                    "business_name": foundation.get("business_name"),
                    "industry": foundation.get("industry"),
                    "value_proposition": foundation.get("value_proposition"),
                }

            # Get ICP context
            icp_result = (
                self.db_client.table("icp_profiles")
                .select("*")
                .eq("workspace_id", workspace_id)
                .limit(3)
                .execute()
            )
            if icp_result.data:
                today_context["current_focus"] = [
                    {
                        "type": "icp",
                        "name": icp["name"],
                        "description": icp["description"],
                    }
                    for icp in icp_result.data
                ]

            return today_context

        except Exception as e:
            logger.error(f"Error getting today's context: {e}")
            return {"date": time.strftime("%Y-%m-%d"), "workspace_id": workspace_id}

    async def _generate_daily_wins(
        self, workspace_id: str, today_context: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate daily wins using daily wins agent."""
        try:
            agent = self.agent_dispatcher.get_agent("daily_wins")

            state = AgentState()
            state.update(
                {
                    "workspace_id": workspace_id,
                    "user_id": context["user_id"],
                    "today_context": today_context,
                    "task": "generate_daily_wins",
                }
            )

            result = await agent.execute(state)

            wins = result.get("daily_wins", [])

            if not wins:
                return {"success": False, "error": "No daily wins generated"}

            return {"success": True, "wins": wins, "total_wins": len(wins)}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _store_daily_wins(
        self,
        workspace_id: str,
        wins: List[Dict[str, Any]],
        today_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Store daily wins in database."""
        try:
            daily_wins_record = {
                "workspace_id": workspace_id,
                "date": today_context["date"],
                "context": today_context,
                "wins": wins,
                "status": "generated",
                "created_at": time.time(),
            }

            result = (
                self.db_client.table("daily_wins").insert(daily_wins_record).execute()
            )

            if result.data:
                return {"daily_wins_id": result.data[0]["id"], "success": True}
            else:
                return {"success": False, "error": "Failed to store daily wins"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _create_expansion_tasks(self, daily_wins_id: str):
        """Create expansion tasks for each win."""
        try:
            # Get daily wins
            daily_wins_result = (
                self.db_client.table("daily_wins")
                .select("wins")
                .eq("id", daily_wins_id)
                .execute()
            )

            if not daily_wins_result.data:
                return

            wins = daily_wins_result.data[0]["wins"]

            # Create expansion task for each win
            for i, win in enumerate(wins):
                expansion_task = {
                    "daily_wins_id": daily_wins_id,
                    "win_index": i,
                    "win_title": win.get("title"),
                    "status": "pending",
                    "created_at": time.time(),
                }

                self.db_client.table("win_expansion_tasks").insert(
                    expansion_task
                ).execute()

        except Exception as e:
            logger.error(f"Error creating expansion tasks: {e}")

    async def _generate_expanded_content(
        self, win: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate expanded content for a win."""
        try:
            # Use daily wins agent for expansion
            agent = self.agent_dispatcher.get_agent("daily_wins")

            state = AgentState()
            state.update(
                {
                    "workspace_id": context["workspace_id"],
                    "user_id": context["user_id"],
                    "task": "expand_win_content",
                    "win": win,
                }
            )

            result = await agent.execute(state)

            content = result.get("expanded_content", "")

            if not content:
                return {"success": False, "error": "No expanded content generated"}

            return {"success": True, "content": content}

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
                goal="Assess content quality for daily win",
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

    async def _store_expanded_content(
        self, win_id: str, content: str, quality_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store expanded content in database."""
        try:
            content_record = {
                "win_id": win_id,
                "content": content,
                "content_type": "daily_win_expanded",
                "quality_score": quality_result["score"],
                "status": "ready",
                "created_at": time.time(),
            }

            result = (
                self.db_client.table("win_content").insert(content_record).execute()
            )

            if result.data:
                return {"content_id": result.data[0]["id"], "success": True}
            else:
                return {"success": False, "error": "Failed to store expanded content"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _prepare_content_for_platform(
        self, win: Dict[str, Any], platform: str, schedule_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare content for specific platform."""
        try:
            # Get expanded content
            content_result = (
                self.db_client.table("win_content")
                .select("*")
                .eq("win_id", win["id"])
                .execute()
            )

            if not content_result.data:
                return {"error": "No expanded content found"}

            content = content_result.data[0]["content"]

            # Platform-specific preparation
            if platform == "linkedin":
                prepared = {
                    "content": self._prepare_for_linkedin(content, win),
                    "format": "linkedin_post",
                    "character_limit": 3000,
                    "hashtags": self._generate_hashtags(win, "linkedin"),
                }
            elif platform == "twitter":
                prepared = {
                    "content": self._prepare_for_twitter(content, win),
                    "format": "tweet",
                    "character_limit": 280,
                    "hashtags": self._generate_hashtags(win, "twitter"),
                }
            elif platform == "instagram":
                prepared = {
                    "content": self._prepare_for_instagram(content, win),
                    "format": "instagram_post",
                    "character_limit": 2200,
                    "hashtags": self._generate_hashtags(win, "instagram"),
                }
            elif platform == "facebook":
                prepared = {
                    "content": self._prepare_for_facebook(content, win),
                    "format": "facebook_post",
                    "character_limit": 5000,
                    "hashtags": self._generate_hashtags(win, "facebook"),
                }
            elif platform == "email":
                prepared = {
                    "content": self._prepare_for_email(content, win),
                    "format": "email_newsletter",
                    "subject": f"Daily Win: {win['title']}",
                    "hashtags": [],
                }
            else:
                prepared = {
                    "content": content,
                    "format": "general",
                    "character_limit": 1000,
                    "hashtags": [],
                }

            # Add platform-specific options
            if schedule_options:
                prepared.update(
                    {
                        "publishing_options": schedule_options,
                        "customizations": schedule_options.get("customizations", {}),
                    }
                )

            return prepared

        except Exception as e:
            return {"error": str(e)}

    def _prepare_for_linkedin(self, content: str, win: Dict[str, Any]) -> str:
        """Prepare content for LinkedIn."""
        # LinkedIn professional tone
        lines = content.split("\n")
        if len(lines) > 3:
            # Keep first few lines for LinkedIn
            content = "\n".join(lines[:3])

        # Add professional closing
        return f"{content}\n\n#DailyWin #BusinessSuccess"

    def _prepare_for_twitter(self, content: str, win: Dict[str, Any]) -> str:
        """Prepare content for Twitter."""
        # Twitter concise format
        lines = content.split("\n")
        if len(lines) > 2:
            content = lines[0]  # Keep first line

        # Make it tweet-friendly
        return f"{content[:240]} #DailyWin"

    def _prepare_for_instagram(self, content: str, win: Dict[str, Any]) -> str:
        """Prepare content for Instagram."""
        # Instagram visual-friendly format
        lines = content.split("\n")
        if len(lines) > 2:
            content = "\n".join(lines[:2])

        return f"{content}\n\n#DailyWin #Motivation"

    def _prepare_for_facebook(self, content: str, win: Dict[str, Any]) -> str:
        """Prepare content for Facebook."""
        # Facebook conversational tone
        return f"{content}\n\n🎉 Today's Daily Win! #BusinessSuccess #Motivation"

    def _prepare_for_email(self, content: str, win: Dict[str, Any]) -> str:
        """Prepare content for email."""
        # Email newsletter format
        return f"""
        <h2>Daily Win: {win['title']}</h2>
        <p>{content}</p>
        <p>Keep up the great work!</p>
        """

    def _generate_hashtags(self, win: Dict[str, Any], platform: str) -> List[str]:
        """Generate relevant hashtags."""
        base_hashtags = ["#DailyWin", "#BusinessSuccess", "#Motivation"]

        platform_hashtags = {
            "linkedin": ["#ProfessionalDevelopment", "#BusinessGrowth"],
            "twitter": ["#Success", "#Achievement"],
            "instagram": ["#Motivation", "#SuccessStory"],
            "facebook": ["#Business", "#Achievement"],
            "email": [],
        }

        return base_hashtags + platform_hashtags.get(platform, [])

    async def _schedule_content_publishing(
        self,
        win_id: str,
        prepared_content: Dict[str, Any],
        platform: str,
        schedule_options: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Schedule content publishing."""
        try:
            # Determine publish time
            publish_time = (
                schedule_options.get("publish_time") if schedule_options else None
            )

            if not publish_time:
                # Default to next business hour
                publish_time = self._get_next_business_hour()

            # Create schedule record
            schedule_record = {
                "win_id": win_id,
                "platform": platform,
                "content": prepared_content,
                "publish_time": publish_time,
                "status": "scheduled",
                "created_at": time.time(),
            }

            result = (
                self.db_client.table("content_schedules")
                .insert(schedule_record)
                .execute()
            )

            if result.data:
                return {
                    "schedule_id": result.data[0]["id"],
                    "publish_time": publish_time,
                }
            else:
                return {"error": "Failed to create schedule"}

        except Exception as e:
            return {"error": str(e)}

    def _get_next_business_hour(self) -> str:
        """Get next business hour timestamp."""
        # Simple implementation - next hour
        next_hour = time.time() + 3600
        return time.strftime("%Y-%m-%d %H:00:00", time.localtime(next_hour))

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
