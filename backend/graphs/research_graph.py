"""
Research Graph - LangGraph workflow for customer intelligence.

Orchestrates the research domain using LangGraph StateGraph:
1. Build ICP → structured profile
2. Assign Tags → psychographic enrichment
3. Generate Narrative → persona story
4. Mine Pain Points → categorized pain points

Includes error handling, retries, and state management.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict

from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from backend.agents.research.icp_builder_agent import icp_builder_agent
from backend.agents.research.tag_assignment_agent import tag_assignment_agent
from backend.agents.research.persona_narrative_agent import persona_narrative_agent
from backend.agents.research.pain_point_miner_agent import pain_point_miner_agent
from backend.models.agent_state import ResearchState
from backend.utils.cache import cache
from backend.utils.correlation import get_correlation_id


logger = logging.getLogger(__name__)


class ResearchGraph:
    """
    LangGraph workflow for customer intelligence research.

    Nodes:
    - build_icp: Creates structured ICP profile
    - assign_tags: Enriches with psychographic tags
    - generate_narrative: Creates persona story
    - mine_pain_points: Categorizes pain points

    Edges:
    - Sequential flow with error handling
    - Retry logic (up to 3 attempts with exponential backoff)
    - State management via ResearchState
    """

    def __init__(self):
        self.graph = self._build_graph()
        self.app = self.graph.compile(checkpointer=MemorySaver())

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph StateGraph.

        Returns:
            Compiled StateGraph
        """
        # Define state graph with ResearchState schema
        workflow = StateGraph(ResearchState)

        # Add nodes for each agent
        workflow.add_node("build_icp", self._build_icp_node)
        workflow.add_node("assign_tags", self._assign_tags_node)
        workflow.add_node("generate_narrative", self._generate_narrative_node)
        workflow.add_node("mine_pain_points", self._mine_pain_points_node)
        workflow.add_node("finalize", self._finalize_node)

        # Define edges (sequential workflow)
        workflow.set_entry_point("build_icp")
        workflow.add_edge("build_icp", "assign_tags")
        workflow.add_edge("assign_tags", "generate_narrative")
        workflow.add_edge("generate_narrative", "mine_pain_points")
        workflow.add_edge("mine_pain_points", "finalize")
        workflow.add_edge("finalize", END)

        return workflow

    async def _build_icp_node(self, state: ResearchState) -> ResearchState:
        """
        Node 1: Build ICP profile.

        Args:
            state: Current research state

        Returns:
            Updated state with ICP data
        """
        logger.info("Research Graph - Node: build_icp")

        try:
            # Extract ICP request from state
            icp_request = state.icp_request
            if not icp_request:
                raise ValueError("Missing icp_request in state")

            # Execute with retry
            result = await self._execute_with_retry(
                agent=icp_builder_agent,
                payload=icp_request.model_dump() if hasattr(icp_request, "model_dump") else icp_request,
                node_name="build_icp",
            )

            # Update state
            icp_output = result.get("output", {})
            state.icp = icp_output
            state.context["icp_built"] = True

            # Add to history
            state.history.append({
                "node": "build_icp",
                "status": "success",
                "output_keys": list(icp_output.keys()) if icp_output else [],
            })

            logger.info("ICP built successfully")
            return state

        except Exception as e:
            error_msg = f"build_icp node failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            state.errors.append(error_msg)
            state.history.append({
                "node": "build_icp",
                "status": "failed",
                "error": error_msg,
            })
            # Continue workflow even with error (graceful degradation)
            return state

    async def _assign_tags_node(self, state: ResearchState) -> ResearchState:
        """
        Node 2: Assign psychographic tags.

        Args:
            state: Current research state

        Returns:
            Updated state with tags
        """
        logger.info("Research Graph - Node: assign_tags")

        try:
            icp = state.icp
            if not icp:
                raise ValueError("No ICP data available for tag assignment")

            # Prepare payload
            payload = {
                "icp_description": icp.get("executive_summary", ""),
                "demographics": icp.get("demographics", {}),
                "psychographics": icp.get("psychographics", {}),
            }

            # Execute with retry
            result = await self._execute_with_retry(
                agent=tag_assignment_agent,
                payload=payload,
                node_name="assign_tags",
            )

            # Update state
            tag_output = result.get("output", {})
            state.tags = tag_output.get("tags", [])
            state.context["tags_assigned"] = True
            state.context["tag_confidences"] = tag_output.get("tag_confidences", {})

            # Add to history
            state.history.append({
                "node": "assign_tags",
                "status": "success",
                "tags_count": len(state.tags),
            })

            logger.info(f"Assigned {len(state.tags)} tags")
            return state

        except Exception as e:
            error_msg = f"assign_tags node failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            state.errors.append(error_msg)
            state.history.append({
                "node": "assign_tags",
                "status": "failed",
                "error": error_msg,
            })
            state.tags = []  # Continue with empty tags
            return state

    async def _generate_narrative_node(self, state: ResearchState) -> ResearchState:
        """
        Node 3: Generate persona narrative.

        Args:
            state: Current research state

        Returns:
            Updated state with narrative
        """
        logger.info("Research Graph - Node: generate_narrative")

        try:
            icp = state.icp
            if not icp:
                raise ValueError("No ICP data available for narrative generation")

            # Prepare payload
            payload = {
                "icp_name": icp.get("icp_name", "Customer Persona"),
                "demographics": icp.get("demographics", {}),
                "psychographics": icp.get("psychographics", {}),
                "pain_points": icp.get("pain_points", []),
                "goals": icp.get("goals", []),
            }

            # Execute with retry
            result = await self._execute_with_retry(
                agent=persona_narrative_agent,
                payload=payload,
                node_name="generate_narrative",
            )

            # Update state
            narrative_output = result.get("output", {})
            state.persona_narrative = narrative_output
            state.context["narrative_generated"] = True

            # Add to history
            state.history.append({
                "node": "generate_narrative",
                "status": "success",
                "persona_name": narrative_output.get("persona_name", ""),
            })

            logger.info("Persona narrative generated")
            return state

        except Exception as e:
            error_msg = f"generate_narrative node failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            state.errors.append(error_msg)
            state.history.append({
                "node": "generate_narrative",
                "status": "failed",
                "error": error_msg,
            })
            state.persona_narrative = None
            return state

    async def _mine_pain_points_node(self, state: ResearchState) -> ResearchState:
        """
        Node 4: Mine and categorize pain points.

        Args:
            state: Current research state

        Returns:
            Updated state with categorized pain points
        """
        logger.info("Research Graph - Node: mine_pain_points")

        try:
            icp = state.icp
            icp_request = state.icp_request

            if not icp:
                raise ValueError("No ICP data available for pain point mining")

            # Prepare payload
            payload = {
                "icp_description": icp.get("executive_summary", ""),
                "existing_pain_points": icp.get("pain_points", []),
                "product_description": (
                    icp_request.product_description
                    if icp_request and hasattr(icp_request, "product_description")
                    else ""
                ),
            }

            # Execute with retry
            result = await self._execute_with_retry(
                agent=pain_point_miner_agent,
                payload=payload,
                node_name="mine_pain_points",
            )

            # Update state
            pain_point_output = result.get("output", {})
            state.context["categorized_pain_points"] = pain_point_output
            state.context["pain_points_mined"] = True

            # Add to history
            state.history.append({
                "node": "mine_pain_points",
                "status": "success",
                "total_pain_points": pain_point_output.get("total_pain_points", 0),
            })

            logger.info("Pain points mined and categorized")
            return state

        except Exception as e:
            error_msg = f"mine_pain_points node failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            state.errors.append(error_msg)
            state.history.append({
                "node": "mine_pain_points",
                "status": "failed",
                "error": error_msg,
            })
            return state

    async def _finalize_node(self, state: ResearchState) -> ResearchState:
        """
        Finalize node: Mark workflow as complete and cache results.

        Args:
            state: Current research state

        Returns:
            Finalized state
        """
        logger.info("Research Graph - Node: finalize")

        # Mark as completed
        state.completed = True

        # Cache final results with 24-hour TTL
        correlation_id = state.correlation_id or get_correlation_id()
        cache_key = f"{correlation_id}_final"

        try:
            final_result = {
                "icp": state.icp,
                "tags": state.tags,
                "persona_narrative": state.persona_narrative,
                "categorized_pain_points": state.context.get("categorized_pain_points"),
                "history": state.history,
                "errors": state.errors,
            }

            await cache.set("research", cache_key, final_result, ttl=86400)
            logger.info(f"Research results cached: {cache_key}")

        except Exception as e:
            logger.warning(f"Failed to cache results: {e}")

        # Add finalization to history
        state.history.append({
            "node": "finalize",
            "status": "success",
            "errors_count": len(state.errors),
        })

        logger.info("Research workflow completed")
        return state

    async def _execute_with_retry(
        self,
        agent: Any,
        payload: Dict[str, Any],
        node_name: str,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Execute an agent with exponential backoff retry.

        Args:
            agent: Agent instance to execute
            payload: Payload to pass to agent
            node_name: Node name for logging
            max_retries: Maximum retry attempts

        Returns:
            Agent result dict

        Raises:
            Exception: If all retries fail
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                logger.info(f"{node_name}: Attempt {attempt + 1}/{max_retries}")
                result = await agent.execute(payload)
                return result

            except Exception as e:
                last_error = e
                logger.warning(
                    f"{node_name} failed (attempt {attempt + 1}/{max_retries}): {e}"
                )

                if attempt < max_retries - 1:
                    # Exponential backoff: 2^attempt seconds
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying {node_name} in {wait_time}s")
                    await asyncio.sleep(wait_time)

        # All retries failed
        error_msg = f"{node_name} failed after {max_retries} attempts: {last_error}"
        logger.error(error_msg)
        raise Exception(error_msg)

    async def run(
        self,
        icp_request: Dict[str, Any],
        workspace_id: str | None = None,
        goal: str | None = None,
    ) -> Dict[str, Any]:
        """
        Execute the research graph workflow.

        Args:
            icp_request: ICP request payload (company_name, industry, etc.)
            workspace_id: Optional workspace ID
            goal: Optional goal description

        Returns:
            Final research results
        """
        correlation_id = get_correlation_id()
        logger.info(f"Starting research graph workflow: {correlation_id}")

        # Initialize state
        initial_state = ResearchState(
            correlation_id=correlation_id,
            workspace_id=workspace_id,
            goal=goal or "Build comprehensive ICP profile",
            icp_request=icp_request,
            context={},
            history=[],
            errors=[],
            completed=False,
        )

        # Run workflow
        config = {"configurable": {"thread_id": correlation_id}}

        try:
            final_state = await self.app.ainvoke(initial_state, config)

            # Extract results
            return {
                "success": final_state.completed and len(final_state.errors) == 0,
                "correlation_id": correlation_id,
                "icp": final_state.icp,
                "tags": final_state.tags,
                "persona_narrative": final_state.persona_narrative,
                "categorized_pain_points": final_state.context.get("categorized_pain_points"),
                "history": final_state.history,
                "errors": final_state.errors,
            }

        except Exception as e:
            error_msg = f"Research graph workflow failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "correlation_id": correlation_id,
                "error": error_msg,
                "errors": [error_msg],
            }


def compile_research_graph() -> ResearchGraph:
    """
    Compile and return the research graph.

    Returns:
        Compiled ResearchGraph instance
    """
    return ResearchGraph()


# Global instance
research_graph = compile_research_graph()
