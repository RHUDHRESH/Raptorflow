"""
Business Context Generator
Uses Vertex AI to generate comprehensive business context from company data
"""

import json
import logging
from typing import Dict, Any, List, Optional

from .services.vertex_ai_client import get_vertex_ai_client
from .services.business_context_graph import (
    get_business_context_graph,
    create_initial_workflow_state,
)
from schemas import BusinessContextState, MessagingStrategy
from db.messaging import MessagingRepository
from db.icps import ICPRepository

logger = logging.getLogger(__name__)


class BusinessContextGenerator:
    """Generates business context using LangGraph analysis"""

    def __init__(self):
        self.vertex_ai_client = get_vertex_ai_client()
        self.graph = get_business_context_graph()
        self.messaging_repo = MessagingRepository()
        self.icp_repo = ICPRepository()

    async def generate_from_foundation(
        self, foundation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate business context from foundation data using LangGraph"""
        try:
            workspace_id = foundation_data.get("workspace_id", "unknown")
            if not self.vertex_ai_client or not self.vertex_ai_client.get_model():
                logger.warning("Vertex AI client not available, using fallback")
                return self.graph.get_fallback_context(foundation_data).model_dump()

            # Create initial state
            state = create_initial_workflow_state(
                workspace_id=workspace_id,
                user_id=foundation_data.get("user_id", "unknown"),
                foundation_data=foundation_data,
            )

            # Execute graph
            result = await self.graph.workflow.ainvoke(state)
            context = result["context_data"]

            # Persist derived items
            if context.messaging_strategy:
                await self.messaging_repo.upsert(
                    workspace_id, context.messaging_strategy.model_dump()
                )

            if context.ricps:
                for ricp in context.ricps:
                    # Map to DB schema
                    db_data = {
                        "name": ricp.name,
                        "persona_name": ricp.persona_name,
                        "avatar": ricp.avatar,
                        "demographics": ricp.demographics.model_dump(),
                        "psychographics": ricp.psychographics.model_dump(),
                        "market_sophistication": {"stage": ricp.market_sophistication},
                        "confidence": ricp.confidence,
                        "fit_score": ricp.confidence,
                    }
                    await self.icp_repo.create(workspace_id, db_data)

            return context.model_dump()

        except Exception as e:
            logger.error(f"Business context generation failed: {e}")
            return self.graph.get_fallback_context(foundation_data).model_dump()

    async def enhance_icp_context(
        self, icp_data: Dict[str, Any], foundation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance ICP data with AI-generated insights using LangGraph"""
        try:
            if not self.vertex_ai_client or not self.vertex_ai_client.get_model():
                return self.graph.get_fallback_icp(icp_data).model_dump()

            # For direct ICP enhancement, we run a partial graph or just the enhance_icp node
            # For simplicity and robustness, we'll use the full state initialization
            state = create_initial_workflow_state(
                workspace_id=foundation_data.get("workspace_id", "unknown"),
                user_id=foundation_data.get("user_id", "unknown"),
                foundation_data=foundation_data,
                icp_list=[icp_data],
            )

            # Manually trigger the enhance_icp node
            result = await self.graph.enhance_icp_node(state)

            enhanced_map = result["context_data"].icp_enhancements
            icp_id = icp_data.get("id") or icp_data.get("name")

            if icp_id in enhanced_map:
                return enhanced_map[icp_id].model_dump()

            return self.graph.get_fallback_icp(icp_data).model_dump()

        except Exception as e:
            logger.error(f"ICP enhancement failed: {e}")
            return self.graph.get_fallback_icp(icp_data).model_dump()

    async def generate_messaging_strategy(
        self, business_context: Dict[str, Any], icp_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive messaging strategy using LangGraph"""
        try:
            if not self.vertex_ai_client or not self.vertex_ai_client.get_model():
                return self.graph.get_fallback_messaging().model_dump()

            # Initialize state with existing context and ICPs
            state = create_initial_workflow_state(
                workspace_id="unknown",
                user_id="unknown",
                foundation_data={},  # Not strictly needed if business_context is provided
            )

            # Load provided context into state
            state["context_data"] = BusinessContextState(**business_context)
            state["icp_list"] = icp_data

            # First enhance ICPs if not already done, then generate messaging
            state = await self.graph.enhance_icp_node(state)
            result = await self.graph.generate_messaging_node(state)

            if result["context_data"].messaging_strategy:
                return result["context_data"].messaging_strategy.model_dump()

            return self.graph.get_fallback_messaging().model_dump()

        except Exception as e:
            logger.error(f"Messaging strategy generation failed: {e}")
            return self.graph.get_fallback_messaging().model_dump()

    def get_fallback_context(self, foundation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic context without AI"""
        return self.graph.get_fallback_context(foundation_data).model_dump()

    def get_fallback_messaging(self) -> Dict[str, Any]:
        """Generate basic messaging without AI"""
        return self.graph.get_fallback_messaging().model_dump()


# Global instance
business_context_generator = BusinessContextGenerator()


def get_business_context_generator() -> BusinessContextGenerator:
    """Get business context generator instance"""
    return business_context_generator
