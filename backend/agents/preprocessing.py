"""
Preprocessing module for loading context before agent execution.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from tools.database import DatabaseTool
from tools.registry import get_tool_registry

from .exceptions import DatabaseError, ValidationError
from .state import AgentState, update_state

logger = logging.getLogger(__name__)


class RequestPreprocessor:
    """Preprocesses requests and loads context before agent execution."""

    def __init__(self):
        self.context_loader = ContextLoader()

    async def preprocess(self, state: AgentState) -> AgentState:
        """Preprocess the request and load context."""
        try:
            workspace_id = state.get("workspace_id")
            user_id = state.get("user_id")
            session_id = state.get("session_id")

            if not all([workspace_id, user_id, session_id]):
                raise ValidationError(
                    "Missing required state fields: workspace_id, user_id, session_id"
                )

            # Load context
            context = await self.context_loader.load_context(
                workspace_id=workspace_id,
                user_id=user_id,
                session_id=session_id,
                context_type="full",
            )

            # Validate context
            if not self.context_loader.validate_context(context):
                logger.warning(
                    "Context validation failed, proceeding with minimal context"
                )

            # Update state with context
            state = self.context_loader.update_context_in_state(state, context)

            # Add preprocessing metadata
            state = update_state(
                state,
                preprocessed_at=datetime.now().isoformat(),
                preprocessing_success=True,
            )

            logger.info(
                f"Successfully preprocessed request for workspace {workspace_id}"
            )
            return state

        except Exception as e:
            logger.error(f"Preprocessing failed: {e}")
            state = update_state(
                state, preprocessing_success=False, preprocessing_error=str(e)
            )
            raise DatabaseError(f"Preprocessing failed: {str(e)}")


class ContextLoader:
    """Loads and prepares context for agent execution."""

    def __init__(self):
        self.database_tool = DatabaseTool()
        self.tool_registry = get_tool_registry()
        from services.bcm_projector import BCMProjector

        self.bcm_projector = BCMProjector()

    async def load_context(
        self,
        workspace_id: str,
        user_id: str,
        session_id: str,
        context_type: str = "full",
    ) -> Dict[str, Any]:
        """Load context data for the agent, including evolved BCM state."""
        try:
            context = {}

            # 1. Load Evolved BCM State (Highest-fidelity strategic context)
            try:
                # We use a default UCID or retrieve the active one from workspace
                # For now, we'll project the latest unified state
                evolved_bcm = await self.bcm_projector.get_latest_state(
                    workspace_id, ucid="RF-BASELINE"
                )
                context["evolved_bcm"] = evolved_bcm.model_dump()
                context["evolution_index"] = evolved_bcm.history.evolution_index
                context["evolved_insights"] = evolved_bcm.evolved_insights

                # Ground foundation fields in evolved BCM
                context["company_name"] = evolved_bcm.identity.name
                context["industry"] = evolved_bcm.identity.industry
                context["brand_voice"] = evolved_bcm.identity.brand_voice
            except Exception as bcm_err:
                logger.warning(f"Failed to load evolved BCM context: {bcm_err}")

            # 2. Load foundation data (as backup/fallback)
            foundation_data = await self._load_foundation_data(workspace_id)
            if foundation_data and "company_name" not in context:
                context["foundation_summary"] = foundation_data.get("summary", "")
                context["company_name"] = foundation_data.get("company_name", "")
                context["industry"] = foundation_data.get("industry", "")
                context["onboarding_completed"] = foundation_data.get(
                    "onboarding_completed", False
                )

            # Load active ICPs if available
            icp_data = await self._load_icp_data(workspace_id)
            if icp_data:
                context["active_icps"] = icp_data
                context["icp_count"] = len(icp_data)

            # Load recent moves if available
            moves_data = await self._load_moves_data(workspace_id)
            if moves_data:
                context["recent_moves"] = moves_data
                context["active_moves_count"] = len(moves_data)

            # Load recent campaigns if available
            campaigns_data = await self._load_campaigns_data(workspace_id)
            if campaigns_data:
                context["recent_campaigns"] = campaigns_data
                context["active_campaigns_count"] = len(campaigns_data)

            # Load user profile if available
            user_profile = await self._load_user_profile(workspace_id, user_id)
            if user_profile:
                context["user_profile"] = user_profile

            # Load recent agent executions if available
            executions_data = await self._load_agent_executions(
                workspace_id, user_id, limit=5
            )
            if executions_data:
                context["recent_executions"] = executions_data
                context["execution_count"] = len(executions_data)

            # Load muse assets if available
            muse_data = await self._load_muse_assets(workspace_id)
            if muse_data:
                context["muse_assets"] = muse_data
                context["muse_assets_count"] = len(muse_data)

            # Add metadata
            context["context_type"] = context_type
            context["loaded_at"] = datetime.now().isoformat()
            context["workspace_id"] = workspace_id
            context["user_id"] = user_id
            context["session_id"] = session_id

            logger.info(f"Loaded {context_type} context for workspace {workspace_id}")
            return context

        except Exception as e:
            logger.error(f"Failed to load context: {e}")
            raise DatabaseError(f"Context loading failed: {str(e)}")

    async def _load_foundation_data(
        self, workspace_id: str
    ) -> Optional[Dict[str, Any]]:
        """Load foundation data for the workspace."""
        try:
            # Set workspace context for database tool
            self.database_tool.set_workspace_id(workspace_id)

            # Query foundation data
            result = await self.database_tool.arun(
                table="foundations", workspace_id=workspace_id, limit=1
            )

            if result.success and result.data["data"]:
                foundation = result.data["data"][0]
                return foundation

            return None

        except Exception as e:
            logger.error(f"Failed to load foundation data: {e}")
            return None

    async def _load_icp_data(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Load active ICPs for the workspace."""
        try:
            self.database_tool.set_workspace_id(workspace_id)

            result = await self.database_tool.arun(
                table="icp_profiles",
                workspace_id=workspace_id,
                filters={"is_primary": True},
                limit=3,
            )

            if result.success and result.data["data"]:
                return result.data["data"]

            return []

        except Exception as e:
            logger.error(f"Failed to load ICP data: {e}")
            return []

    async def _load_moves_data(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Load recent moves for the workspace."""
        try:
            self.database_tool.set_workspace_id(workspace_id)

            result = await self.database_tool.arun(
                table="moves",
                workspace_id=workspace_id,
                filters={"status": "active"},
                limit=10,
            )

            if result.success and result.data["data"]:
                return result.data["data"]

            return []

        except Exception as e:
            logger.error(f"Failed to load moves data: {e}")
            return []

    async def _load_campaigns_data(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Load recent campaigns for the workspace."""
        try:
            self.database_tool.set_workspace_id(workspace_id)

            result = await self.database_tool.arun(
                table="campaigns",
                workspace_id=workspace_id,
                filters={"status": "active"},
                limit=10,
            )

            if result.success and result.data["data"]:
                return result.data["data"]

            return []

        except Exception as e:
            logger.error(f"Failed to load campaigns data: {e}")
            return []

    async def _load_user_profile(
        self, workspace_id: str, user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Load user profile for the workspace."""
        try:
            # In a real implementation, this would query a user_profiles table
            # For now, return mock data
            return {
                "user_id": user_id,
                "preferences": {
                    "language": "en",
                    "timezone": "UTC",
                    "notifications": True,
                },
            }

        except Exception as e:
            logger.error(f"Failed to load user profile: {e}")
            return None

    async def _load_agent_executions(
        self, workspace_id: str, user_id: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Load recent agent executions for the user."""
        try:
            self.database_tool.set_workspace_id(workspace_id)

            result = await self.database_tool.arun(
                table="agent_executions",
                workspace_id=workspace_id,
                filters={"user_id": user_id},
                limit=limit,
            )

            if result.success and result.data["data"]:
                return result.data["data"]

            return []

        except Exception as e:
            logger.error(f"Failed to load agent executions: {e}")
            return []

    async def _load_muse_assets(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Load muse assets for the workspace."""
        try:
            self.database_tool.set_workspace_id(workspace_id)

            result = await self.database_tool.arun(
                table="muse_assets",
                workspace_id=workspace_id,
                filters={"status": "published"},
                limit=20,
            )

            if result.success and result.data["data"]:
                return result.data["data"]

            return []

        except Exception as e:
            logger.error(f"Failed to load muse assets: {e}")
            return []

    async def load_context_for_agent(
        self,
        agent_name: str,
        workspace_id: str,
        user_id: str,
        session_id: str,
        context_type: str = "agent_specific",
    ) -> Dict[str, Any]:
        """Load context specific to an agent."""
        # Load general context first
        general_context = await self.load_context(
            workspace_id, user_id, session_id, "general"
        )

        # Add agent-specific context
        agent_context = {
            "agent_name": agent_name,
            "agent_tools": self._get_agent_tools(agent_name),
            "agent_context_type": context_type,
        }

        # Merge contexts
        merged_context = {**general_context, **agent_context}

        return merged_context

    def _get_agent_tools(self, agent_name: str) -> List[str]:
        """Get tools available for a specific agent."""
        # Get agent metadata
        agent_registry = get_tool_registry()
        agent = agent_registry.get_agent(agent_name)

        if agent:
            return agent.get_tools()

        return []

    async def preload_context(
        self, workspace_id: str, user_id: str, session_id: str
    ) -> Dict[str, Any]:
        """Preload all context data for faster agent execution."""
        try:
            # Load all context types in parallel
            tasks = [
                self.load_context(workspace_id, user_id, session_id, "full"),
                self.load_context(workspace_id, user_id, session_id, "minimal"),
                self.load_context(workspace_id, user_id, session_id, "tools"),
            ]

            contexts = await asyncio.gather(*tasks)

            return {"full": contexts[0], "minimal": contexts[1], "tools": contexts[2]}

        except Exception as e:
            logger.error(f"Failed to preload context: {e}")
            return {}

    async def update_context_in_state(
        self, state: AgentState, context: Dict[str, Any]
    ) -> AgentState:
        """Update state with loaded context."""
        # Add context to state
        state = update_state(
            state, context=context, context_loaded_at=datetime.now().isoformat()
        )

        # Add context summary
        context_summary = self._create_context_summary(context)
        state = update_state(state, context_summary=context_summary)

        return state

    def _create_context_summary(self, context: Dict[str, Any]) -> str:
        """Create a summary of the loaded context."""
        summary_parts = []

        if context.get("company_name"):
            summary_parts.append(f"Company: {context['company_name']}")

        if context.get("industry"):
            summary_parts.append(f"Industry: {context['industry']}")

        if context.get("icp_count", 0) > 0:
            summary_parts.append(f"ICPs: {context['icp_count']}")

        if context.get("active_moves_count", 0) > 0:
            summary_parts.append(f"Active Moves: {context['active_moves_count']}")

        if context.get("active_campaigns_count", 0) > 0:
            summary_parts.append(
                f"Active Campaigns: {context['active_campaigns_count']}"
            )

        if context.get("muse_assets_count", 0) > 0:
            summary_parts.append(f"Muse Assets: {context['muse_assets_count']}")

        return (
            ", ".join(summary_parts)
            if summary_parts
            else "No additional context available"
        )

    def validate_context(self, context: Dict[str, Any]) -> bool:
        """Validate that context data is properly structured."""
        try:
            # Check required fields
            if not context.get("workspace_id"):
                return False

            # Validate data types
            if isinstance(context.get("icp_count"), int) and context["icp_count"] < 0:
                return False

            if (
                isinstance(context.get("active_moves_count"), int)
                and context["active_moves_count"] < 0
            ):
                return False

            return True

        except Exception as e:
            logger.error(f"Context validation failed: {e}")
            return False

    def get_context_loading_stats(self) -> Dict[str, Any]:
        """Get statistics about context loading."""
        return {
            "database_tool_available": self.database_tool is not None,
            "tool_registry_available": self.tool_registry is not None,
            "supported_tables": self.database_tool.get_available_tables(),
            "available_tools": self.tool_registry.list_tools(),
        }
