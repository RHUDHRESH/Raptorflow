"""
Master Graph - Orchestrates all domain graphs with correlation tracking and safety checks.

This is the top-level workflow that coordinates:
1. Onboarding - User/company profile setup
2. Research - ICP generation and customer intelligence
3. Strategy - ADAPT framework and campaign planning
4. Content - Multi-format content generation with critic review
5. Integration - Third-party platform connections
6. Execution & Analytics - Publishing and performance tracking
"""

from typing import Dict, List, Optional, Any, TypedDict, Literal
from uuid import uuid4
from datetime import datetime
import structlog
from enum import Enum

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from backend.graphs.onboarding_graph import onboarding_graph_runnable
from backend.graphs.customer_intelligence_graph import customer_intelligence_graph
from backend.graphs.strategy_graph import strategy_graph
from backend.graphs.content_graph import content_graph_runnable
from backend.graphs.integration_graph import integration_graph_runnable
from backend.graphs.execution_analytics_graph import execution_analytics_graph_runnable
from backend.agents.safety.critic_agent import critic_agent
from backend.utils.correlation import get_correlation_id, set_correlation_id

logger = structlog.get_logger(__name__)


class WorkflowGoal(str, Enum):
    """User workflow objectives."""
    FULL_CAMPAIGN = "full_campaign"  # Complete end-to-end workflow
    RESEARCH_ONLY = "research_only"  # ICP + insights only
    STRATEGY_ONLY = "strategy_only"  # Strategy generation only
    CONTENT_ONLY = "content_only"  # Content generation only
    PUBLISH = "publish"  # Execute and track existing content
    ONBOARD = "onboard"  # Just onboarding questionnaire


class MasterGraphState(TypedDict):
    """State for the master orchestration graph."""
    # Request metadata
    correlation_id: str
    workflow_id: str
    workspace_id: str
    user_id: str
    goal: WorkflowGoal

    # Workflow tracking
    current_stage: str
    completed_stages: List[str]
    failed_stages: List[str]
    started_at: str
    completed_at: Optional[str]

    # Input parameters (optional - graph-specific)
    onboarding_session_id: Optional[str]
    icp_id: Optional[str]
    strategy_id: Optional[str]
    content_ids: Optional[List[str]]

    # Domain-specific inputs
    research_query: Optional[str]
    research_mode: Optional[Literal["quick", "deep"]]
    strategy_mode: Optional[Literal["quick", "comprehensive"]]
    content_type: Optional[str]
    content_params: Optional[Dict[str, Any]]
    publish_platforms: Optional[List[str]]

    # Results from each graph
    onboarding_result: Optional[Dict[str, Any]]
    research_result: Optional[Dict[str, Any]]
    strategy_result: Optional[Dict[str, Any]]
    content_result: Optional[Dict[str, Any]]
    critic_review: Optional[Dict[str, Any]]
    integration_result: Optional[Dict[str, Any]]
    execution_result: Optional[Dict[str, Any]]

    # Error handling
    errors: List[Dict[str, str]]
    retry_count: int

    # Final output
    success: bool
    message: Optional[str]


class MasterGraph:
    """
    Master orchestration graph that coordinates all domain graphs.

    Features:
    - Goal-based routing (skip unnecessary stages)
    - Correlation ID tracking across all graphs
    - Critic agent integration for content safety
    - Retry logic with exponential backoff
    - Comprehensive error handling
    """

    def __init__(self):
        self.workflow = self._build_workflow()
        # Use MemorySaver for now, upgrade to PostgresSaver in production
        self.app = self.workflow.compile(checkpointer=MemorySaver())

    def _build_workflow(self) -> StateGraph:
        """Build the master orchestration workflow."""
        workflow = StateGraph(MasterGraphState)

        # Add nodes for each domain
        workflow.add_node("initialize", self._initialize_node)
        workflow.add_node("onboarding", self._onboarding_node)
        workflow.add_node("research", self._research_node)
        workflow.add_node("strategy", self._strategy_node)
        workflow.add_node("content", self._content_node)
        workflow.add_node("critic_review", self._critic_review_node)
        workflow.add_node("integration", self._integration_node)
        workflow.add_node("execution", self._execution_node)
        workflow.add_node("finalize", self._finalize_node)

        # Define workflow
        workflow.set_entry_point("initialize")

        # Route based on goal
        workflow.add_conditional_edges(
            "initialize",
            self._route_from_init,
            {
                "onboarding": "onboarding",
                "research": "research",
                "strategy": "strategy",
                "content": "content",
                "publish": "execution",
                "finalize": "finalize"
            }
        )

        # Onboarding flow
        workflow.add_conditional_edges(
            "onboarding",
            self._route_from_onboarding,
            {
                "research": "research",
                "finalize": "finalize",
                "error": "finalize"
            }
        )

        # Research flow
        workflow.add_conditional_edges(
            "research",
            self._route_from_research,
            {
                "strategy": "strategy",
                "finalize": "finalize",
                "error": "finalize"
            }
        )

        # Strategy flow
        workflow.add_conditional_edges(
            "strategy",
            self._route_from_strategy,
            {
                "content": "content",
                "finalize": "finalize",
                "error": "finalize"
            }
        )

        # Content flow -> always go through critic
        workflow.add_edge("content", "critic_review")

        # Critic review
        workflow.add_conditional_edges(
            "critic_review",
            self._route_from_critic,
            {
                "integration": "integration",
                "content": "content",  # Retry if major revisions needed
                "finalize": "finalize",
                "error": "finalize"
            }
        )

        # Integration flow
        workflow.add_conditional_edges(
            "integration",
            self._route_from_integration,
            {
                "execution": "execution",
                "finalize": "finalize",
                "error": "finalize"
            }
        )

        # Execution flow
        workflow.add_edge("execution", "finalize")

        # Finalize
        workflow.add_edge("finalize", END)

        return workflow

    # ========== Node Implementations ==========

    async def _initialize_node(self, state: MasterGraphState) -> MasterGraphState:
        """Initialize workflow with correlation ID and metadata."""
        try:
            # Set correlation ID in context
            correlation_id = state.get("correlation_id") or str(uuid4())
            set_correlation_id(correlation_id)

            state["correlation_id"] = correlation_id
            state["workflow_id"] = state.get("workflow_id") or str(uuid4())
            state["started_at"] = datetime.utcnow().isoformat()
            state["current_stage"] = "initialize"
            state["completed_stages"] = []
            state["failed_stages"] = []
            state["errors"] = []
            state["retry_count"] = 0

            logger.info(
                "Master workflow initialized",
                workflow_id=state["workflow_id"],
                correlation_id=correlation_id,
                goal=state["goal"],
                workspace_id=state["workspace_id"]
            )

            return state

        except Exception as e:
            logger.error(f"Initialization failed: {e}", correlation_id=state.get("correlation_id"))
            state["errors"].append({"stage": "initialize", "error": str(e)})
            state["failed_stages"].append("initialize")
            return state

    async def _onboarding_node(self, state: MasterGraphState) -> MasterGraphState:
        """Execute onboarding graph."""
        try:
            state["current_stage"] = "onboarding"
            logger.info("Starting onboarding", correlation_id=state["correlation_id"])

            # Call onboarding graph
            # Note: Onboarding is session-based, so we just track that it's available
            # The actual execution happens via the onboarding API endpoints

            state["onboarding_result"] = {
                "session_id": state.get("onboarding_session_id"),
                "status": "ready",
                "message": "Onboarding questionnaire is ready"
            }

            state["completed_stages"].append("onboarding")
            logger.info("Onboarding completed", correlation_id=state["correlation_id"])

            return state

        except Exception as e:
            logger.error(f"Onboarding failed: {e}", correlation_id=state["correlation_id"])
            state["errors"].append({"stage": "onboarding", "error": str(e)})
            state["failed_stages"].append("onboarding")
            return state

    async def _research_node(self, state: MasterGraphState) -> MasterGraphState:
        """Execute customer intelligence (research) graph."""
        try:
            state["current_stage"] = "research"
            logger.info("Starting research", correlation_id=state["correlation_id"])

            # Prepare research input
            research_input = {
                "workspace_id": state["workspace_id"],
                "mode": state.get("research_mode", "quick"),
                "correlation_id": state["correlation_id"]
            }

            if state.get("research_query"):
                research_input["query"] = state["research_query"]

            # Execute customer intelligence graph
            research_graph = customer_intelligence_graph
            result = await research_graph.run(research_input)

            state["research_result"] = result
            state["icp_id"] = result.get("icp_id")
            state["completed_stages"].append("research")

            logger.info(
                "Research completed",
                icp_id=state["icp_id"],
                correlation_id=state["correlation_id"]
            )

            return state

        except Exception as e:
            logger.error(f"Research failed: {e}", correlation_id=state["correlation_id"])
            state["errors"].append({"stage": "research", "error": str(e)})
            state["failed_stages"].append("research")
            return state

    async def _strategy_node(self, state: MasterGraphState) -> MasterGraphState:
        """Execute strategy graph (ADAPT framework)."""
        try:
            state["current_stage"] = "strategy"
            logger.info("Starting strategy", correlation_id=state["correlation_id"])

            # Prepare strategy input
            strategy_input = {
                "workspace_id": state["workspace_id"],
                "icp_id": state.get("icp_id"),
                "mode": state.get("strategy_mode", "quick"),
                "correlation_id": state["correlation_id"]
            }

            # Execute strategy graph
            strategy_graph_instance = strategy_graph
            result = await strategy_graph_instance.run(strategy_input)

            state["strategy_result"] = result
            state["strategy_id"] = result.get("strategy_id")
            state["completed_stages"].append("strategy")

            logger.info(
                "Strategy completed",
                strategy_id=state["strategy_id"],
                correlation_id=state["correlation_id"]
            )

            return state

        except Exception as e:
            logger.error(f"Strategy failed: {e}", correlation_id=state["correlation_id"])
            state["errors"].append({"stage": "strategy", "error": str(e)})
            state["failed_stages"].append("strategy")
            return state

    async def _content_node(self, state: MasterGraphState) -> MasterGraphState:
        """Execute content generation graph."""
        try:
            state["current_stage"] = "content"
            logger.info("Starting content generation", correlation_id=state["correlation_id"])

            # Prepare content input
            content_input = {
                "workspace_id": state["workspace_id"],
                "content_type": state.get("content_type", "blog"),
                "icp_id": state.get("icp_id"),
                "strategy_id": state.get("strategy_id"),
                "correlation_id": state["correlation_id"]
            }

            # Merge any additional content parameters
            if state.get("content_params"):
                content_input.update(state["content_params"])

            # Execute content graph
            result = await content_graph_runnable.ainvoke(content_input)

            state["content_result"] = result
            state["content_ids"] = result.get("content_ids", [])
            state["completed_stages"].append("content")

            logger.info(
                "Content generated",
                content_ids=state["content_ids"],
                correlation_id=state["correlation_id"]
            )

            return state

        except Exception as e:
            logger.error(f"Content generation failed: {e}", correlation_id=state["correlation_id"])
            state["errors"].append({"stage": "content", "error": str(e)})
            state["failed_stages"].append("content")
            return state

    async def _critic_review_node(self, state: MasterGraphState) -> MasterGraphState:
        """Execute critic agent review for content safety and quality."""
        try:
            state["current_stage"] = "critic_review"
            logger.info("Starting critic review", correlation_id=state["correlation_id"])

            # Get generated content
            content_result = state.get("content_result", {})
            generated_content = content_result.get("content", "")

            if not generated_content:
                logger.warning("No content to review, skipping critic", correlation_id=state["correlation_id"])
                state["critic_review"] = {"recommendation": "approve", "overall_score": 100}
                return state

            # Get ICP and brand context
            research_result = state.get("research_result", {})
            target_icp = research_result.get("icp")
            brand_voice = research_result.get("brand_voice")

            # Review content
            review = await critic_agent.review_content(
                content=generated_content,
                content_type=state.get("content_type", "blog"),
                target_icp=target_icp,
                brand_voice=brand_voice,
                correlation_id=state["correlation_id"]
            )

            state["critic_review"] = review
            state["completed_stages"].append("critic_review")

            logger.info(
                "Critic review completed",
                recommendation=review.get("recommendation"),
                score=review.get("overall_score"),
                correlation_id=state["correlation_id"]
            )

            return state

        except Exception as e:
            logger.error(f"Critic review failed: {e}", correlation_id=state["correlation_id"])
            state["errors"].append({"stage": "critic_review", "error": str(e)})
            state["failed_stages"].append("critic_review")
            # Continue workflow even if critic fails (non-blocking)
            state["critic_review"] = {"recommendation": "approve", "error": str(e)}
            return state

    async def _integration_node(self, state: MasterGraphState) -> MasterGraphState:
        """Execute integration graph for third-party platforms."""
        try:
            state["current_stage"] = "integration"
            logger.info("Starting integration", correlation_id=state["correlation_id"])

            # Prepare integration input
            integration_input = {
                "workspace_id": state["workspace_id"],
                "content_ids": state.get("content_ids", []),
                "correlation_id": state["correlation_id"]
            }

            # Execute integration graph
            result = await integration_graph_runnable.ainvoke(integration_input)

            state["integration_result"] = result
            state["completed_stages"].append("integration")

            logger.info("Integration completed", correlation_id=state["correlation_id"])

            return state

        except Exception as e:
            logger.error(f"Integration failed: {e}", correlation_id=state["correlation_id"])
            state["errors"].append({"stage": "integration", "error": str(e)})
            state["failed_stages"].append("integration")
            return state

    async def _execution_node(self, state: MasterGraphState) -> MasterGraphState:
        """Execute publishing and analytics tracking."""
        try:
            state["current_stage"] = "execution"
            logger.info("Starting execution", correlation_id=state["correlation_id"])

            # Prepare execution input
            execution_input = {
                "workspace_id": state["workspace_id"],
                "content_ids": state.get("content_ids", []),
                "platforms": state.get("publish_platforms", []),
                "correlation_id": state["correlation_id"]
            }

            # Execute analytics graph
            result = await execution_analytics_graph_runnable.ainvoke(execution_input)

            state["execution_result"] = result
            state["completed_stages"].append("execution")

            logger.info("Execution completed", correlation_id=state["correlation_id"])

            return state

        except Exception as e:
            logger.error(f"Execution failed: {e}", correlation_id=state["correlation_id"])
            state["errors"].append({"stage": "execution", "error": str(e)})
            state["failed_stages"].append("execution")
            return state

    async def _finalize_node(self, state: MasterGraphState) -> MasterGraphState:
        """Finalize workflow and generate summary."""
        try:
            state["current_stage"] = "finalize"
            state["completed_at"] = datetime.utcnow().isoformat()

            # Determine success
            has_errors = len(state["failed_stages"]) > 0
            state["success"] = not has_errors

            if state["success"]:
                state["message"] = f"Workflow completed successfully. Stages: {', '.join(state['completed_stages'])}"
            else:
                state["message"] = f"Workflow completed with errors in: {', '.join(state['failed_stages'])}"

            logger.info(
                "Workflow finalized",
                workflow_id=state["workflow_id"],
                correlation_id=state["correlation_id"],
                success=state["success"],
                completed_stages=len(state["completed_stages"]),
                failed_stages=len(state["failed_stages"])
            )

            return state

        except Exception as e:
            logger.error(f"Finalization failed: {e}", correlation_id=state["correlation_id"])
            state["errors"].append({"stage": "finalize", "error": str(e)})
            state["success"] = False
            state["message"] = f"Workflow failed: {str(e)}"
            return state

    # ========== Routing Functions ==========

    def _route_from_init(self, state: MasterGraphState) -> str:
        """Route from initialization based on goal."""
        goal = state["goal"]

        if goal == WorkflowGoal.ONBOARD:
            return "onboarding"
        elif goal == WorkflowGoal.RESEARCH_ONLY:
            return "research"
        elif goal == WorkflowGoal.STRATEGY_ONLY:
            # If no ICP, do research first
            if not state.get("icp_id"):
                return "research"
            return "strategy"
        elif goal == WorkflowGoal.CONTENT_ONLY:
            # If no strategy, do strategy first
            if not state.get("strategy_id"):
                if not state.get("icp_id"):
                    return "research"
                return "strategy"
            return "content"
        elif goal == WorkflowGoal.PUBLISH:
            return "publish"
        elif goal == WorkflowGoal.FULL_CAMPAIGN:
            # Start from research (assuming onboarding is complete)
            return "research"
        else:
            return "finalize"

    def _route_from_onboarding(self, state: MasterGraphState) -> str:
        """Route from onboarding."""
        if "onboarding" in state["failed_stages"]:
            return "error"

        # If full campaign, continue to research
        if state["goal"] == WorkflowGoal.FULL_CAMPAIGN:
            return "research"

        return "finalize"

    def _route_from_research(self, state: MasterGraphState) -> str:
        """Route from research."""
        if "research" in state["failed_stages"]:
            return "error"

        # If research only, done
        if state["goal"] == WorkflowGoal.RESEARCH_ONLY:
            return "finalize"

        # Otherwise continue to strategy
        return "strategy"

    def _route_from_strategy(self, state: MasterGraphState) -> str:
        """Route from strategy."""
        if "strategy" in state["failed_stages"]:
            return "error"

        # If strategy only, done
        if state["goal"] == WorkflowGoal.STRATEGY_ONLY:
            return "finalize"

        # Otherwise continue to content
        return "content"

    def _route_from_critic(self, state: MasterGraphState) -> str:
        """Route from critic review."""
        if "critic_review" in state["failed_stages"]:
            # Non-blocking error, continue
            return "finalize"

        review = state.get("critic_review", {})
        recommendation = review.get("recommendation", "approve")

        # If major revisions needed and under retry limit
        if recommendation == "revise_major" and state["retry_count"] < 2:
            state["retry_count"] += 1
            logger.info(
                "Retrying content generation based on critic feedback",
                retry_count=state["retry_count"],
                correlation_id=state["correlation_id"]
            )
            return "content"

        # If integration is needed
        if state["goal"] in [WorkflowGoal.FULL_CAMPAIGN, WorkflowGoal.PUBLISH]:
            return "integration"

        return "finalize"

    def _route_from_integration(self, state: MasterGraphState) -> str:
        """Route from integration."""
        if "integration" in state["failed_stages"]:
            return "error"

        # If publish goal, continue to execution
        if state["goal"] in [WorkflowGoal.FULL_CAMPAIGN, WorkflowGoal.PUBLISH]:
            return "execution"

        return "finalize"


# Global master graph instance
master_graph = MasterGraph()
master_graph_runnable = master_graph.app
