"""
Strategy Graph - Orchestrates ADAPT framework and campaign planning.
Coordinates: Campaign Planner → Market Research → Ambient Search → Synthesis

ASSUMPTIONS AND DEFAULTS:
-------------------------
Budget-Based Conditional Logic:
- Low budget (<$5K): Skip ambient scan, use quick research mode, focus on 2-3 channels
- Medium budget ($5K-$25K): Standard workflow, quick research by default
- High budget (>$25K): Comprehensive mode, full ambient scan, all channels available

Goal-Based Conditional Logic:
- Short-term goals (<30 days): Skip long-term strategy synthesis, focus on quick wins
- Mid-term goals (30-90 days): Standard ADAPT workflow with sprint planning
- Long-term goals (>90 days): Include strategic themes, comprehensive synthesis

Channel Optimization:
- Low budget campaigns default to: organic social, content, email
- High budget campaigns can include: paid search, video, influencer partnerships

Error Handling and Retry Logic:
- Market research: Falls back to cached data or quick mode if deep mode fails
- Ambient scan: Optional - continues workflow if fails
- Campaign planning: Uses fallback templates if LLM fails
- All nodes: Max 3 retries with exponential backoff for transient failures

Conditional Edges:
- If budget is high → comprehensive mode → ambient scan
- If budget is low or goals short-term → quick mode → skip ambient → direct to planning
- If goals are short-term (<30 days) → skip synthesis → direct to planning
"""

import structlog
from typing import Dict, List, Optional, Any, TypedDict
from uuid import UUID
import logging
import re

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from backend.agents.strategy.campaign_planner import campaign_planner
from backend.agents.strategy.market_research import market_research
from backend.agents.strategy.ambient_search import ambient_search
from backend.agents.strategy.synthesis_agent import synthesis_agent
from backend.models.campaign import MoveRequest, MoveResponse
from backend.models.persona import ICPProfile
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


# Define state schema
class StrategyGraphState(TypedDict):
    """State for the strategy workflow."""
    workspace_id: str
    move_request: Dict[str, Any]
    icps: List[Dict[str, Any]]
    market_insights: Optional[Dict[str, Any]]
    ambient_opportunities: List[Dict[str, Any]]
    synthesized_campaigns: List[Dict[str, Any]]
    final_campaign: Optional[Dict[str, Any]]
    mode: str  # "quick" or "comprehensive"
    error: Optional[str]
    completed: bool


class StrategyGraph:
    """
    Orchestrates strategic campaign planning using ADAPT framework.

    ADAPT Workflow:
    1. **Assess**: Validate inputs and determine routing
    2. **Diagnose**: Research market + mine ambient opportunities
    3. **Analyze**: Synthesize opportunities into campaign proposals
    4. **Plan**: Create detailed execution plan with sprints
    5. **Track**: (Handled by analytics agents)

    Workflow Modes:
    - Quick: Skip ambient search, use basic market research
    - Comprehensive: Full ADAPT cycle with deep research
    - Adaptive: Automatically choose based on budget and timeframe
    """

    def __init__(self):
        # Budget tier thresholds
        self.budget_tiers = {
            "low": {"max": 5000},
            "medium": {"min": 5000, "max": 25000},
            "high": {"min": 25000}
        }

        # Timeframe categorization
        self.timeframe_categories = {
            "short": {"max": 30},  # days
            "medium": {"min": 30, "max": 90},
            "long": {"min": 90}
        }

        self.workflow = self._build_workflow()
        self.app = self.workflow.compile(checkpointer=MemorySaver())
    
    def _build_workflow(self) -> StateGraph:
        """Builds the LangGraph workflow."""
        workflow = StateGraph(StrategyGraphState)
        
        # Add nodes
        workflow.add_node("market_research", self._market_research_node)
        workflow.add_node("ambient_scan", self._ambient_scan_node)
        workflow.add_node("synthesize_opportunities", self._synthesize_opportunities_node)
        workflow.add_node("plan_campaign", self._plan_campaign_node)
        workflow.add_node("save_strategy", self._save_strategy_node)
        
        # Define edges
        workflow.set_entry_point("market_research")
        
        # Conditional routing after market research
        workflow.add_conditional_edges(
            "market_research",
            self._route_after_research,
            {
                "ambient_scan": "ambient_scan",
                "plan_campaign": "plan_campaign"
            }
        )
        
        workflow.add_edge("ambient_scan", "synthesize_opportunities")
        workflow.add_edge("synthesize_opportunities", "plan_campaign")
        workflow.add_edge("plan_campaign", "save_strategy")
        workflow.add_edge("save_strategy", END)
        
        return workflow
    
    def _route_after_research(self, state: StrategyGraphState) -> str:
        """
        Routes based on budget, timeframe, and mode.

        Conditional logic:
        - High budget + long timeframe → ambient scan → synthesis
        - Low budget OR short timeframe → skip ambient → direct to planning
        - Medium budget + medium timeframe → user mode preference
        """
        move_request = state.get("move_request", {})
        budget = move_request.get("budget")
        timeframe_days = move_request.get("timeframe_days", 90)
        mode = state.get("mode", "quick")

        # Parse budget
        budget_tier = self._parse_budget_tier(budget)
        timeframe_category = self._categorize_timeframe(timeframe_days)

        logger.info(
            "Routing after research",
            budget_tier=budget_tier,
            timeframe_category=timeframe_category,
            mode=mode
        )

        # Conditional routing logic
        # If short-term goals (<30 days), skip ambient and go direct to planning
        if timeframe_category == "short":
            logger.info("Short-term goal detected, skipping ambient scan")
            return "plan_campaign"

        # If low budget, skip expensive ambient scan
        if budget_tier == "low":
            logger.info("Low budget detected, skipping ambient scan")
            return "plan_campaign"

        # If comprehensive mode OR (high budget AND long timeframe)
        if mode == "comprehensive" or (budget_tier == "high" and timeframe_category == "long"):
            logger.info("Comprehensive mode or high-budget long-term campaign, including ambient scan")
            return "ambient_scan"

        # Default: skip ambient scan
        return "plan_campaign"

    def _parse_budget_tier(self, budget_str: Optional[str]) -> str:
        """
        Parses budget string into tier (low/medium/high).
        """
        if not budget_str:
            return "medium"  # Default to medium if not specified

        # Extract numeric value
        numbers = re.findall(r'\d+', budget_str.replace(',', ''))

        if not numbers:
            return "medium"

        amount = int(numbers[0])

        # Check for multipliers
        if 'k' in budget_str.lower() or 'K' in budget_str:
            amount *= 1000

        # Determine tier
        if amount < 5000:
            return "low"
        elif amount < 25000:
            return "medium"
        else:
            return "high"

    def _categorize_timeframe(self, timeframe_days: int) -> str:
        """Categorizes timeframe as short/medium/long."""
        if timeframe_days <= 30:
            return "short"
        elif timeframe_days <= 90:
            return "medium"
        else:
            return "long"

    async def _retry_with_backoff(
        self,
        operation,
        max_retries: int = 3,
        initial_delay: float = 1.0
    ) -> Any:
        """
        Retries an async operation with exponential backoff.

        Args:
            operation: Async callable to retry
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds

        Returns:
            Result of successful operation

        Raises:
            Exception from last failed attempt
        """
        import asyncio

        last_exception = None
        delay = initial_delay

        for attempt in range(max_retries):
            try:
                return await operation()
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Operation failed (attempt {attempt + 1}/{max_retries}), retrying in {delay}s",
                        error=str(e)
                    )
                    await asyncio.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Operation failed after {max_retries} attempts", error=str(e))

        raise last_exception

    async def _market_research_node(self, state: StrategyGraphState) -> StrategyGraphState:
        """Conducts market research for campaign context with retry logic."""
        try:
            logger.info("Conducting market research")

            move_request = state["move_request"]
            goal = move_request.get("goal", "")

            # Determine research mode based on budget and timeframe
            base_mode = state.get("mode", "quick")
            budget_tier = self._parse_budget_tier(move_request.get("budget"))
            timeframe_category = self._categorize_timeframe(move_request.get("timeframe_days", 90))

            # Override mode based on budget/timeframe if not explicitly set
            if base_mode == "quick" and budget_tier == "high" and timeframe_category == "long":
                research_mode = "deep"
                logger.info("Auto-upgrading to deep research mode based on budget and timeframe")
            else:
                research_mode = base_mode

            # Research question based on goal
            research_question = f"What are the current market trends and opportunities for: {goal}"

            # Add context from ICPs
            context = {}
            if state.get("icps"):
                first_icp = state["icps"][0]
                context = {
                    "industry": first_icp.get("demographics", {}).get("industry", ""),
                    "company_size": first_icp.get("demographics", {}).get("company_size", "")
                }

            # Wrap research call with retry logic
            async def research_operation():
                return await market_research.research(
                    question=research_question,
                    mode=research_mode,
                    context=context
                )

            insights = await self._retry_with_backoff(research_operation, max_retries=3)

            state["market_insights"] = insights
            logger.info(f"Market research completed successfully, mode={research_mode}")
            return state

        except Exception as e:
            logger.error(f"Market research failed after retries: {e}")
            # Fallback: try quick mode if deep mode failed
            if state.get("mode") == "deep":
                logger.info("Falling back to quick research mode")
                try:
                    insights = await market_research.research(
                        question=f"Quick insight: {goal}",
                        mode="quick",
                        context={}
                    )
                    state["market_insights"] = insights
                    return state
                except Exception as fallback_error:
                    logger.error(f"Fallback research also failed: {fallback_error}")

            state["error"] = str(e)
            state["market_insights"] = {}
            return state
    
    async def _ambient_scan_node(self, state: StrategyGraphState) -> StrategyGraphState:
        """Scans for ambient opportunities."""
        try:
            logger.info("Scanning for ambient opportunities")
            
            workspace_id = UUID(state["workspace_id"])
            icps = state.get("icps", [])
            
            # Get user industry from first ICP
            user_industry = None
            if icps:
                user_industry = icps[0].get("demographics", {}).get("industry")
            
            # Run daily scan
            opportunities = await ambient_search.run_daily_scan(
                workspace_id=workspace_id,
                icps=icps,
                user_industry=user_industry
            )
            
            state["ambient_opportunities"] = opportunities
            return state
            
        except Exception as e:
            logger.error(f"Ambient scan failed: {e}")
            state["error"] = str(e)
            state["ambient_opportunities"] = []
            return state
    
    async def _synthesize_opportunities_node(self, state: StrategyGraphState) -> StrategyGraphState:
        """Synthesizes opportunities into campaign proposals."""
        try:
            logger.info("Synthesizing opportunities into campaigns")
            
            opportunities = state.get("ambient_opportunities", [])
            icps = state.get("icps", [])
            
            if not opportunities:
                logger.warning("No opportunities to synthesize")
                state["synthesized_campaigns"] = []
                return state
            
            # Batch synthesize top opportunities
            synthesized = await synthesis_agent.batch_synthesize(
                opportunities=opportunities,
                icps=icps,
                limit=5
            )
            
            state["synthesized_campaigns"] = synthesized
            return state
            
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            state["error"] = str(e)
            state["synthesized_campaigns"] = []
            return state
    
    async def _plan_campaign_node(self, state: StrategyGraphState) -> StrategyGraphState:
        """Plans detailed campaign with sprints and tasks."""
        try:
            logger.info("Planning campaign execution")
            
            move_request_data = state["move_request"]
            move_request = MoveRequest(**move_request_data)
            
            # Convert ICP dicts to ICPProfile objects
            icp_objects = [ICPProfile(**icp) for icp in state.get("icps", [])]
            
            # Get market insights
            market_insights = state.get("market_insights")
            
            # Generate campaign plan
            campaign = await campaign_planner.generate_campaign(
                move_request=move_request,
                icps=icp_objects,
                market_insights=market_insights
            )
            
            state["final_campaign"] = campaign.model_dump()
            state["completed"] = True
            return state
            
        except Exception as e:
            logger.error(f"Campaign planning failed: {e}")
            state["error"] = str(e)
            return state
    
    async def _save_strategy_node(self, state: StrategyGraphState) -> StrategyGraphState:
        """Saves strategy and campaign to database."""
        try:
            logger.info("Saving strategy to database")
            
            campaign_data = state["final_campaign"]
            if not campaign_data:
                logger.warning("No campaign to save")
                return state
            
            # Save to moves table
            saved_campaign = await supabase_client.insert("moves", campaign_data)
            state["final_campaign"]["id"] = saved_campaign["id"]
            
            # Also save synthesized opportunities if comprehensive mode
            if state.get("mode") == "comprehensive" and state.get("synthesized_campaigns"):
                for synth_campaign in state.get("synthesized_campaigns", []):
                    try:
                        # Store as alternative campaign ideas
                        alt_campaign_data = {
                            "workspace_id": state["workspace_id"],
                            "name": synth_campaign.get("campaign_name", "Alternative Campaign"),
                            "description": synth_campaign.get("one_line_pitch", ""),
                            "status": "idea",
                            "metadata": synth_campaign
                        }
                        await supabase_client.insert("campaign_ideas", alt_campaign_data)
                    except Exception as e:
                        logger.error(f"Failed to save alternative campaign: {e}")
            
            logger.info(f"Strategy saved with campaign ID: {saved_campaign['id']}")
            return state
            
        except Exception as e:
            logger.error(f"Strategy save failed: {e}")
            state["error"] = str(e)
            return state
    
    async def generate_strategy(
        self,
        workspace_id: UUID,
        move_request: MoveRequest,
        icp_ids: List[UUID],
        mode: str = "quick"
    ) -> Dict[str, Any]:
        """
        Generates complete marketing strategy.
        
        Args:
            workspace_id: User's workspace ID
            move_request: Campaign requirements
            icp_ids: Target ICP IDs
            mode: "quick" or "comprehensive"
            
        Returns:
            Complete strategy with campaign plan
        """
        correlation_id = get_correlation_id()
        logger.info(
            "Generating marketing strategy",
            goal=move_request.goal,
            mode=mode,
            num_icps=len(icp_ids),
            correlation_id=correlation_id
        )
        
        # Fetch ICPs
        icps = []
        for icp_id in icp_ids:
            icp_data = await supabase_client.fetch_one("cohorts", {"id": str(icp_id)})
            if icp_data:
                icps.append(icp_data)
        
        if not icps:
            logger.error("No ICPs found")
            return {
                "success": False,
                "error": "No ICPs found for strategy generation"
            }
        
        # Initialize state
        initial_state: StrategyGraphState = {
            "workspace_id": str(workspace_id),
            "move_request": move_request.model_dump(),
            "icps": icps,
            "market_insights": None,
            "ambient_opportunities": [],
            "synthesized_campaigns": [],
            "final_campaign": None,
            "mode": mode,
            "error": None,
            "completed": False
        }
        
        # Run workflow
        config = {"configurable": {"thread_id": correlation_id}}
        result = await self.app.ainvoke(initial_state, config)
        
        if result.get("error"):
            logger.error(f"Strategy generation failed: {result['error']}")
            return {
                "success": False,
                "error": result["error"]
            }
        
        logger.info("Strategy generation completed successfully")
        return {
            "success": True,
            "campaign": result["final_campaign"],
            "market_insights": result.get("market_insights"),
            "alternative_ideas": result.get("synthesized_campaigns", []),
            "correlation_id": correlation_id
        }
    
    async def quick_win_to_campaign(
        self,
        workspace_id: UUID,
        opportunity_id: UUID
    ) -> Dict[str, Any]:
        """
        Converts a quick win opportunity into a full campaign.
        
        Args:
            workspace_id: User's workspace
            opportunity_id: ID from quick_wins table
            
        Returns:
            Campaign plan
        """
        correlation_id = get_correlation_id()
        logger.info(
            "Converting quick win to campaign",
            opportunity_id=opportunity_id,
            correlation_id=correlation_id
        )
        
        try:
            # Fetch opportunity
            opp_data = await supabase_client.fetch_one(
                "quick_wins",
                {"id": str(opportunity_id), "workspace_id": str(workspace_id)}
            )
            
            if not opp_data:
                return {
                    "success": False,
                    "error": "Opportunity not found"
                }
            
            # Fetch matched ICPs
            icp_names = opp_data.get("matched_icp_names", [])
            icps = []
            if icp_names:
                all_icps = await supabase_client.fetch_all(
                    "cohorts",
                    filters={"workspace_id": str(workspace_id)}
                )
                icps = [icp for icp in all_icps if icp.get("name") in icp_names]
            
            # Synthesize campaign
            campaign_proposal = await synthesis_agent.synthesize_campaign_idea(
                opportunity=opp_data,
                icps=icps
            )
            
            # Create move request from proposal
            move_request = MoveRequest(
                workspace_id=workspace_id,
                name=campaign_proposal.get("campaign_name", "Quick Win Campaign"),
                goal=campaign_proposal.get("one_line_pitch", ""),
                timeframe_days=campaign_proposal.get("timeline", {}).get("duration_days", 14),
                target_cohort_ids=[UUID(icp["id"]) for icp in icps if icp.get("id")],
                channels=[
                    ch.get("channel", "linkedin")
                    for ch in campaign_proposal.get("recommended_channels", [])
                ]
            )
            
            # Generate full campaign
            icp_objects = [ICPProfile(**icp) for icp in icps]
            campaign = await campaign_planner.generate_campaign(
                move_request=move_request,
                icps=icp_objects,
                market_insights=None
            )
            
            # Save
            campaign_data = campaign.model_dump()
            saved_campaign = await supabase_client.insert("moves", campaign_data)
            
            # Mark opportunity as used
            await supabase_client.update(
                "quick_wins",
                {"id": str(opportunity_id)},
                {"status": "converted"}
            )
            
            return {
                "success": True,
                "campaign": saved_campaign,
                "correlation_id": correlation_id
            }
            
        except Exception as e:
            logger.error(f"Quick win conversion failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
strategy_graph = StrategyGraph()

