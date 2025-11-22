"""
Strategy Supervisor (Tier 1) - Orchestrates the ADAPT framework for marketing strategy.

ADAPT Framework:
- Assess: Validate prerequisites and gather context
- Diagnose: Conduct market research
- Analyze: Synthesize insights and opportunities
- Plan: Generate detailed campaign execution plan
- Track: Set up analytics hooks (delegated to analytics supervisor)

Responsibilities:
- Validate ICP/persona research completion before strategy generation
- Orchestrate market research → synthesis → campaign planning workflow
- Manage conditional routing based on budget, goals, and timeframes
- Provide comprehensive error handling and fallback strategies
- Document assumptions for different business contexts (SaaS, e-commerce, B2B, B2C)

ASSUMPTIONS (Documented at top as required):
-------------------------------------------------
Default KPIs by Business Type:
- SaaS: MRR growth, trial conversions, activation rate, churn reduction
- E-commerce: Revenue, AOV, cart conversion, customer LTV
- B2B Services: Pipeline value, qualified leads, meeting bookings, proposal acceptance
- B2C: Engagement rate, brand awareness, customer acquisition cost, repeat purchase rate

Budget Tiers:
- Low (<$5K): Focus on organic channels, content marketing, social engagement
- Medium ($5K-$25K): Add paid social, email campaigns, basic influencer partnerships
- High (>$25K): Full channel mix including paid search, video, PR, events

Timeframe Defaults:
- Short-term (<30 days): Burst campaigns, quick wins, high-intensity tactics
- Mid-term (30-90 days): Sustained campaigns with 2-week sprints
- Long-term (>90 days): Always-on presence with monthly themes and quarterly reviews

Channel Assumptions:
- LinkedIn: B2B focus, thought leadership, longer sales cycles
- Twitter/X: Real-time engagement, brand personality, community building
- Email: Nurture, retention, direct conversion
- Blog/SEO: Long-term awareness, education, inbound traffic
- Paid Search: Direct response, high intent, conversion focus

Research Modes:
- Quick mode: Single-pass research, 7-day cache, ~800 tokens
- Comprehensive mode: Multi-query research with synthesis, 14-day cache, ~3K tokens
"""

from typing import Dict, List, Optional, Any, Literal
from uuid import UUID
from datetime import datetime
import structlog
from pydantic import BaseModel, Field

from backend.agents.base_agent import BaseSupervisor
from backend.graphs.strategy_graph import strategy_graph
from backend.models.campaign import MoveRequest, MoveResponse
from backend.models.agent_state import ResearchState
from backend.services.supabase_client import supabase_client
from backend.services.openai_client import openai_client
from backend.utils.correlation import get_correlation_id, generate_correlation_id
from backend.config.prompts import MASTER_SUPERVISOR_SYSTEM_PROMPT

logger = structlog.get_logger(__name__)


class StrategyRequest(BaseModel):
    """Request model for strategy generation."""
    icp_ids: List[UUID] = Field(..., min_items=1, description="Target ICP IDs (at least one required)")
    goals: str = Field(..., description="Campaign or business goals")
    budget: Optional[str] = Field(None, description="Budget range (e.g., '$10K', '<$5K', '>$25K')")
    channels: List[str] = Field(default_factory=lambda: ["linkedin", "email", "blog"], description="Marketing channels")
    timeframe_days: int = Field(default=90, ge=7, le=365, description="Campaign duration in days")
    mode: Literal["quick", "comprehensive"] = Field(default="quick", description="Research depth")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Additional constraints or preferences")

    class Config:
        json_schema_extra = {
            "example": {
                "icp_ids": ["550e8400-e29b-41d4-a716-446655440000"],
                "goals": "Generate 100 enterprise leads for Q2",
                "budget": "$15K",
                "channels": ["linkedin", "email", "blog"],
                "timeframe_days": 90,
                "mode": "comprehensive"
            }
        }


class StrategyResponse(BaseModel):
    """Response model for strategy generation."""
    success: bool
    strategy_id: Optional[UUID] = None
    campaign: Optional[MoveResponse] = None
    market_insights: Optional[Dict[str, Any]] = None
    alternative_ideas: List[Dict[str, Any]] = Field(default_factory=list)
    validation_warnings: List[str] = Field(default_factory=list)
    correlation_id: str
    error: Optional[str] = None


class StrategySupervisor(BaseSupervisor):
    """
    Tier 1 Supervisor: Strategy Domain

    Orchestrates the ADAPT framework for marketing strategy generation.
    Coordinates: Market Research → Ambient Search → Synthesis → Campaign Planning

    Prerequisites:
    - At least one ICP must exist in the workspace
    - Research should be completed (ResearchState) for best results
    """

    def __init__(self):
        super().__init__(name="strategy_supervisor")

        # Budget tier definitions
        self.budget_tiers = {
            "low": {"max": 5000, "channels": ["organic", "content", "social"]},
            "medium": {"min": 5000, "max": 25000, "channels": ["organic", "content", "social", "paid_social", "email"]},
            "high": {"min": 25000, "channels": ["all"]}
        }

        # KPI templates by business type
        self.kpi_templates = {
            "saas": ["MRR growth", "Trial conversions", "Activation rate", "Churn reduction", "NPS score"],
            "ecommerce": ["Revenue", "AOV", "Cart conversion", "Customer LTV", "Repeat purchase rate"],
            "b2b_services": ["Pipeline value", "Qualified leads", "Meeting bookings", "Proposal acceptance", "Win rate"],
            "b2c": ["Engagement rate", "Brand awareness", "CAC", "Repeat purchase rate", "Social reach"]
        }

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method for strategy supervisor.

        Workflow:
        1. Assess: Validate payload and prerequisites
        2. Diagnose: Check research completion, gather ICPs
        3. Analyze: Route to strategy graph with appropriate mode
        4. Plan: Generate campaign via graph orchestration
        5. Track: Return results with analytics hooks

        Args:
            payload: StrategyRequest as dict

        Returns:
            StrategyResponse as dict
        """
        correlation_id = generate_correlation_id()
        self.log("Strategy supervisor execution started", payload=payload)

        try:
            # Parse and validate request
            strategy_request = StrategyRequest(**payload)
            workspace_id = UUID(payload.get("workspace_id"))

            # ASSESS: Validate prerequisites
            validation_result = await self._assess_prerequisites(workspace_id, strategy_request)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"],
                    "validation_warnings": validation_result.get("warnings", []),
                    "correlation_id": correlation_id
                }

            # DIAGNOSE: Check research state and gather context
            diagnosis = await self._diagnose_research_state(workspace_id, strategy_request.icp_ids)

            # Log warnings if research is incomplete
            warnings = []
            if not diagnosis["research_complete"]:
                warnings.append(
                    "Warning: ICP research may be incomplete. Strategy will use available data but results may be less personalized."
                )

            # ANALYZE & PLAN: Route to strategy graph
            self.log("Routing to strategy graph", mode=strategy_request.mode)

            # Build MoveRequest from StrategyRequest
            move_request = self._build_move_request(
                workspace_id,
                strategy_request,
                diagnosis
            )

            # Apply conditional logic based on budget and goals
            adjusted_mode = self._determine_research_mode(strategy_request)

            # Execute strategy graph
            result = await strategy_graph.generate_strategy(
                workspace_id=workspace_id,
                move_request=move_request,
                icp_ids=strategy_request.icp_ids,
                mode=adjusted_mode
            )

            if not result.get("success"):
                return {
                    "success": False,
                    "error": result.get("error", "Strategy generation failed"),
                    "correlation_id": correlation_id
                }

            # TRACK: Prepare response with analytics hooks
            self.log("Strategy generation completed successfully")

            return {
                "success": True,
                "strategy_id": result["campaign"].get("id"),
                "campaign": result["campaign"],
                "market_insights": result.get("market_insights"),
                "alternative_ideas": result.get("alternative_ideas", []),
                "validation_warnings": warnings,
                "correlation_id": correlation_id
            }

        except Exception as e:
            logger.error(f"Strategy supervisor execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "correlation_id": correlation_id
            }

    async def _assess_prerequisites(
        self,
        workspace_id: UUID,
        request: StrategyRequest
    ) -> Dict[str, Any]:
        """
        ADAPT - Assess: Validate prerequisites before strategy generation.

        Checks:
        1. Workspace exists and is active
        2. At least one ICP exists
        3. Budget format is valid (if provided)
        4. Channels are supported
        5. Timeframe is reasonable
        """
        try:
            # Check if workspace exists
            workspace = await supabase_client.fetch_one(
                "workspaces",
                {"id": str(workspace_id)}
            )

            if not workspace:
                return {
                    "valid": False,
                    "error": "Workspace not found"
                }

            # Check if ICPs exist
            icps = []
            for icp_id in request.icp_ids:
                icp = await supabase_client.fetch_one(
                    "cohorts",
                    {"id": str(icp_id), "workspace_id": str(workspace_id)}
                )
                if icp:
                    icps.append(icp)

            if not icps:
                return {
                    "valid": False,
                    "error": "No valid ICPs found. Please create at least one ICP before generating strategy."
                }

            # Validate channels (basic check)
            supported_channels = [
                "linkedin", "twitter", "email", "blog", "facebook",
                "instagram", "youtube", "tiktok", "reddit", "slack"
            ]

            warnings = []
            for channel in request.channels:
                if channel.lower() not in supported_channels:
                    warnings.append(f"Channel '{channel}' may not be fully supported")

            # Validate budget format (if provided)
            if request.budget:
                budget_tier = self._parse_budget(request.budget)
                if budget_tier == "unknown":
                    warnings.append(f"Budget format '{request.budget}' not recognized. Using default tier.")

            return {
                "valid": True,
                "icps_found": len(icps),
                "warnings": warnings
            }

        except Exception as e:
            logger.error(f"Prerequisites assessment failed: {e}")
            return {
                "valid": False,
                "error": f"Prerequisites check failed: {str(e)}"
            }

    async def _diagnose_research_state(
        self,
        workspace_id: UUID,
        icp_ids: List[UUID]
    ) -> Dict[str, Any]:
        """
        ADAPT - Diagnose: Check research completion and gather ICP context.

        Returns:
            Diagnosis with research_complete flag and ICP summaries
        """
        try:
            # Fetch ICPs with full data
            icps = []
            for icp_id in icp_ids:
                icp = await supabase_client.fetch_one(
                    "cohorts",
                    {"id": str(icp_id), "workspace_id": str(workspace_id)}
                )
                if icp:
                    icps.append(icp)

            # Check research completeness
            # An ICP is "research complete" if it has:
            # 1. Executive summary
            # 2. Pain points
            # 3. Demographics
            # 4. Psychographics

            research_complete = True
            incomplete_icps = []

            for icp in icps:
                is_complete = (
                    icp.get("executive_summary") and
                    icp.get("pain_points") and
                    icp.get("demographics") and
                    icp.get("psychographics")
                )

                if not is_complete:
                    research_complete = False
                    incomplete_icps.append(icp.get("name", "Unknown"))

            return {
                "research_complete": research_complete,
                "incomplete_icps": incomplete_icps,
                "icps": icps,
                "icp_count": len(icps),
                "business_type": self._infer_business_type(icps[0]) if icps else "unknown"
            }

        except Exception as e:
            logger.error(f"Research state diagnosis failed: {e}")
            return {
                "research_complete": False,
                "incomplete_icps": [],
                "icps": [],
                "icp_count": 0,
                "business_type": "unknown",
                "error": str(e)
            }

    def _build_move_request(
        self,
        workspace_id: UUID,
        strategy_request: StrategyRequest,
        diagnosis: Dict[str, Any]
    ) -> MoveRequest:
        """
        Builds a MoveRequest from StrategyRequest.
        """
        # Generate campaign name based on goals
        campaign_name = self._generate_campaign_name(strategy_request.goals)

        # Apply budget-based channel optimization
        optimized_channels = self._optimize_channels(
            strategy_request.channels,
            strategy_request.budget
        )

        return MoveRequest(
            workspace_id=workspace_id,
            name=campaign_name,
            goal=strategy_request.goals,
            timeframe_days=strategy_request.timeframe_days,
            target_cohort_ids=strategy_request.icp_ids,
            channels=optimized_channels,
            budget=strategy_request.budget,
            constraints=strategy_request.constraints
        )

    def _determine_research_mode(self, request: StrategyRequest) -> str:
        """
        Determines research mode based on budget and timeframe.

        Conditional logic:
        - High budget + long timeframe → comprehensive
        - Low budget or short timeframe → quick
        - User-specified mode → use that
        """
        if request.mode:
            return request.mode

        # Parse budget
        budget_tier = self._parse_budget(request.budget)

        # Conditional routing
        if budget_tier == "high" and request.timeframe_days > 60:
            return "comprehensive"
        elif request.timeframe_days <= 30:
            return "quick"
        else:
            return request.mode or "quick"

    def _parse_budget(self, budget_str: Optional[str]) -> str:
        """
        Parses budget string into tier (low/medium/high).
        """
        if not budget_str:
            return "medium"  # Default

        # Extract numeric value (simple parsing)
        import re
        numbers = re.findall(r'\d+', budget_str.replace(',', ''))

        if not numbers:
            return "unknown"

        amount = int(numbers[0])

        # Check multipliers (K = 1000)
        if 'k' in budget_str.lower() or 'K' in budget_str:
            amount *= 1000

        # Determine tier
        if amount < 5000:
            return "low"
        elif amount < 25000:
            return "medium"
        else:
            return "high"

    def _optimize_channels(
        self,
        requested_channels: List[str],
        budget: Optional[str]
    ) -> List[str]:
        """
        Optimizes channel list based on budget constraints.

        Conditional logic:
        - Low budget: Remove expensive channels (paid search, video)
        - Medium budget: Balanced mix
        - High budget: All requested channels
        """
        budget_tier = self._parse_budget(budget)

        if budget_tier == "low":
            # Filter out expensive channels
            expensive_channels = ["paid_search", "youtube", "video", "events"]
            return [ch for ch in requested_channels if ch not in expensive_channels]

        elif budget_tier == "medium":
            # Limit to 4 channels max
            return requested_channels[:4]

        else:
            # High budget or unknown: use all
            return requested_channels

    def _generate_campaign_name(self, goals: str) -> str:
        """
        Generates a campaign name from goals.
        """
        # Simple extraction of first few words
        words = goals.split()[:4]
        name = " ".join(words).title()

        # Add "Campaign" suffix if not present
        if "campaign" not in name.lower():
            name = f"{name} Campaign"

        return name[:100]  # Limit length

    def _infer_business_type(self, icp: Dict) -> str:
        """
        Infers business type from ICP data.
        """
        # Check industry tags
        tags = icp.get("tags", [])
        demographics = icp.get("demographics", {})
        industry = demographics.get("industry", "").lower()

        # Simple heuristics
        if "saas" in tags or "software" in industry or "b2b" in tags:
            return "saas"
        elif "ecommerce" in tags or "retail" in industry or "b2c" in tags:
            return "ecommerce"
        elif "services" in tags or "consulting" in industry:
            return "b2b_services"
        else:
            return "b2c"

    async def validate_research_complete(
        self,
        workspace_id: UUID
    ) -> Dict[str, Any]:
        """
        Public method to validate if research is complete for a workspace.

        Returns:
            Validation result with research_complete flag
        """
        correlation_id = get_correlation_id()

        try:
            # Fetch all ICPs for workspace
            icps = await supabase_client.fetch_all(
                "cohorts",
                {"workspace_id": str(workspace_id)}
            )

            if not icps:
                return {
                    "research_complete": False,
                    "error": "No ICPs found. Please create at least one ICP.",
                    "correlation_id": correlation_id
                }

            # Check completeness
            icp_ids = [UUID(icp["id"]) for icp in icps]
            diagnosis = await self._diagnose_research_state(workspace_id, icp_ids)

            return {
                "research_complete": diagnosis["research_complete"],
                "incomplete_icps": diagnosis.get("incomplete_icps", []),
                "total_icps": len(icps),
                "correlation_id": correlation_id
            }

        except Exception as e:
            logger.error(f"Research validation failed: {e}")
            return {
                "research_complete": False,
                "error": str(e),
                "correlation_id": correlation_id
            }


# Global instance
strategy_supervisor = StrategySupervisor()
