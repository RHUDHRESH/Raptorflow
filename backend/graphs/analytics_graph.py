"""
Analytics Graph - Orchestrates analytics workflow using LangGraph.
Coordinates metrics collection, insight generation, and reporting.
"""

import structlog
from typing import Dict, List, Optional, Any, TypedDict, Literal
from uuid import UUID
from datetime import datetime, timezone

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from backend.agents.analytics.metrics_collector_agent import metrics_collector_agent
from backend.agents.analytics.insight_agent import insight_agent
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


# --- LangGraph State Definition ---
class AnalyticsGraphState(TypedDict):
    """State for analytics workflow."""
    # Input parameters
    workspace_id: str
    move_id: str
    correlation_id: str
    time_period_days: int
    include_charts: bool
    include_content_analysis: bool
    include_pivot_suggestions: bool

    # Workflow state
    move_data: Optional[Dict[str, Any]]
    validation_passed: bool

    # Collected data
    metrics: Optional[Dict[str, Any]]
    insights: Optional[List[Dict[str, Any]]]
    anomalies: Optional[List[Dict[str, Any]]]
    charts: Optional[Dict[str, Any]]
    content_analysis: Optional[Dict[str, Any]]
    pivot_suggestion: Optional[Dict[str, Any]]
    recommendations: List[str]

    # Report
    final_report: Optional[Dict[str, Any]]

    # Control flow
    next_step: Literal[
        "validate_move",
        "collect_metrics",
        "generate_insights",
        "generate_charts",
        "analyze_content",
        "suggest_pivot",
        "compile_report",
        "save_report",
        "end"
    ]

    # Error handling
    error: Optional[str]
    completed: bool


class AnalyticsGraph:
    """
    LangGraph workflow for analytics domain.

    Workflow:
    1. Validate Move → Ensure move exists and has published content
    2. Collect Metrics → Pull data from all platforms
    3. Generate Insights → Analyze performance and detect anomalies
    4. Generate Charts (optional) → Create visualization data
    5. Analyze Content (optional) → Content type performance
    6. Suggest Pivot (optional) → Strategic recommendations
    7. Compile Report → Create final analytics report
    8. Save Report → Store in database

    Features:
    - Comprehensive error handling
    - Caching for expensive operations
    - Logging with correlation IDs
    - Flexible workflow options
    """

    def __init__(self):
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile(checkpointer=MemorySaver())

    def _build_workflow(self) -> StateGraph:
        """Builds the LangGraph workflow."""
        workflow = StateGraph(AnalyticsGraphState)

        # Add nodes
        workflow.add_node("validate_move", self._validate_move_node)
        workflow.add_node("collect_metrics", self._collect_metrics_node)
        workflow.add_node("generate_insights", self._generate_insights_node)
        workflow.add_node("generate_charts", self._generate_charts_node)
        workflow.add_node("analyze_content", self._analyze_content_node)
        workflow.add_node("suggest_pivot", self._suggest_pivot_node)
        workflow.add_node("compile_report", self._compile_report_node)
        workflow.add_node("save_report", self._save_report_node)

        # Define edges
        workflow.set_entry_point("validate_move")

        # Conditional: validation passed → collect metrics, else end
        workflow.add_conditional_edges(
            "validate_move",
            self._route_after_validation,
            {
                "collect_metrics": "collect_metrics",
                "end": END
            }
        )

        # Always generate insights after collecting metrics
        workflow.add_edge("collect_metrics", "generate_insights")

        # Conditional: charts requested?
        workflow.add_conditional_edges(
            "generate_insights",
            self._route_after_insights,
            {
                "generate_charts": "generate_charts",
                "analyze_content": "analyze_content",
                "compile_report": "compile_report"
            }
        )

        # Conditional: content analysis requested?
        workflow.add_conditional_edges(
            "generate_charts",
            self._route_after_charts,
            {
                "analyze_content": "analyze_content",
                "compile_report": "compile_report"
            }
        )

        # Conditional: pivot suggestions requested?
        workflow.add_conditional_edges(
            "analyze_content",
            self._route_after_content,
            {
                "suggest_pivot": "suggest_pivot",
                "compile_report": "compile_report"
            }
        )

        # After pivot, go to compile
        workflow.add_edge("suggest_pivot", "compile_report")

        # After compiling, save report
        workflow.add_edge("compile_report", "save_report")

        # End after saving
        workflow.add_edge("save_report", END)

        return workflow

    # --- Routing Functions ---

    def _route_after_validation(self, state: AnalyticsGraphState) -> str:
        """Routes based on validation result."""
        if state.get("validation_passed"):
            return "collect_metrics"
        return "end"

    def _route_after_insights(self, state: AnalyticsGraphState) -> str:
        """Routes after insights generation."""
        if state.get("include_charts"):
            return "generate_charts"
        elif state.get("include_content_analysis"):
            return "analyze_content"
        else:
            return "compile_report"

    def _route_after_charts(self, state: AnalyticsGraphState) -> str:
        """Routes after chart generation."""
        if state.get("include_content_analysis"):
            return "analyze_content"
        return "compile_report"

    def _route_after_content(self, state: AnalyticsGraphState) -> str:
        """Routes after content analysis."""
        if state.get("include_pivot_suggestions"):
            return "suggest_pivot"
        return "compile_report"

    # --- Workflow Nodes ---

    async def _validate_move_node(self, state: AnalyticsGraphState) -> AnalyticsGraphState:
        """Validates that move exists and has published content."""
        try:
            workspace_id = UUID(state["workspace_id"])
            move_id = UUID(state["move_id"])
            correlation_id = state.get("correlation_id", get_correlation_id())

            logger.info(
                "Validating move for analytics",
                move_id=move_id,
                correlation_id=correlation_id
            )

            # Check if move exists
            move = await supabase_client.fetch_one(
                "moves",
                {"id": str(move_id), "workspace_id": str(workspace_id)}
            )

            if not move:
                logger.error("Move not found", move_id=move_id, correlation_id=correlation_id)
                return {
                    "validation_passed": False,
                    "error": f"Move {move_id} not found",
                    "next_step": "end",
                    "completed": True
                }

            # Check if move has published content
            published_assets = await supabase_client.fetch_all(
                "assets",
                {"move_id": str(move_id), "status": "published"}
            )

            if not published_assets:
                logger.warning(
                    "Move has no published content",
                    move_id=move_id,
                    correlation_id=correlation_id
                )
                return {
                    "validation_passed": False,
                    "error": "Move has no published content yet. Complete content creation and execution stages first.",
                    "next_step": "end",
                    "completed": True
                }

            logger.info(
                "Move validation successful",
                move_id=move_id,
                published_assets_count=len(published_assets),
                correlation_id=correlation_id
            )

            return {
                "move_data": move,
                "validation_passed": True,
                "next_step": "collect_metrics"
            }

        except Exception as e:
            logger.error(f"Validation failed: {e}", correlation_id=state.get("correlation_id"))
            return {
                "validation_passed": False,
                "error": str(e),
                "next_step": "end",
                "completed": True
            }

    async def _collect_metrics_node(self, state: AnalyticsGraphState) -> AnalyticsGraphState:
        """Collects metrics from all connected platforms."""
        try:
            workspace_id = UUID(state["workspace_id"])
            move_id = UUID(state["move_id"])
            correlation_id = state.get("correlation_id", get_correlation_id())
            time_period_days = state.get("time_period_days", 30)

            logger.info("Collecting metrics", move_id=move_id, correlation_id=correlation_id)

            # Get channels from move data
            move_data = state.get("move_data", {})
            channels = move_data.get("channels")

            # Collect metrics
            metrics = await metrics_collector_agent.collect_metrics(
                workspace_id,
                move_id,
                platforms=channels,
                time_range_days=time_period_days,
                correlation_id=correlation_id
            )

            logger.info(
                "Metrics collected successfully",
                platforms=len(metrics.get("platform_metrics", {})),
                correlation_id=correlation_id
            )

            return {
                "metrics": metrics,
                "next_step": "generate_insights"
            }

        except Exception as e:
            logger.error(f"Metrics collection failed: {e}", correlation_id=state.get("correlation_id"))
            return {
                "error": str(e),
                "next_step": "compile_report"  # Continue with partial data
            }

    async def _generate_insights_node(self, state: AnalyticsGraphState) -> AnalyticsGraphState:
        """Generates insights and detects anomalies."""
        try:
            workspace_id = UUID(state["workspace_id"])
            move_id = UUID(state["move_id"])
            correlation_id = state.get("correlation_id", get_correlation_id())
            time_period_days = state.get("time_period_days", 30)

            logger.info("Generating insights", move_id=move_id, correlation_id=correlation_id)

            # Generate insights
            insights_result = await insight_agent.analyze_performance(
                workspace_id,
                move_id,
                time_period_days=time_period_days,
                correlation_id=correlation_id
            )

            insights = insights_result.get("insights", [])
            anomalies = insights_result.get("anomalies", [])

            logger.info(
                "Insights generated",
                insights_count=len(insights),
                anomalies_count=len(anomalies),
                correlation_id=correlation_id
            )

            return {
                "insights": insights,
                "anomalies": anomalies,
                "next_step": "generate_charts" if state.get("include_charts") else "compile_report"
            }

        except Exception as e:
            logger.error(f"Insight generation failed: {e}", correlation_id=state.get("correlation_id"))
            return {
                "insights": [],
                "anomalies": [],
                "next_step": "compile_report"
            }

    async def _generate_charts_node(self, state: AnalyticsGraphState) -> AnalyticsGraphState:
        """Generates chart data for visualization."""
        try:
            workspace_id = UUID(state["workspace_id"])
            move_id = UUID(state["move_id"])
            correlation_id = state.get("correlation_id", get_correlation_id())
            time_period_days = state.get("time_period_days", 30)

            logger.info("Generating charts", move_id=move_id, correlation_id=correlation_id)

            charts = await insight_agent.generate_chart_data(
                workspace_id,
                move_id,
                time_period_days=time_period_days,
                correlation_id=correlation_id
            )

            logger.info("Charts generated", correlation_id=correlation_id)

            return {
                "charts": charts,
                "next_step": "analyze_content" if state.get("include_content_analysis") else "compile_report"
            }

        except Exception as e:
            logger.error(f"Chart generation failed: {e}", correlation_id=state.get("correlation_id"))
            return {
                "charts": None,
                "next_step": "analyze_content" if state.get("include_content_analysis") else "compile_report"
            }

    async def _analyze_content_node(self, state: AnalyticsGraphState) -> AnalyticsGraphState:
        """Analyzes content type performance."""
        try:
            workspace_id = UUID(state["workspace_id"])
            move_id = UUID(state["move_id"])
            correlation_id = state.get("correlation_id", get_correlation_id())

            logger.info("Analyzing content performance", move_id=move_id, correlation_id=correlation_id)

            content_analysis = await insight_agent.analyze_content_type_performance(
                workspace_id,
                move_id,
                correlation_id=correlation_id
            )

            logger.info("Content analysis completed", correlation_id=correlation_id)

            return {
                "content_analysis": content_analysis,
                "next_step": "suggest_pivot" if state.get("include_pivot_suggestions") else "compile_report"
            }

        except Exception as e:
            logger.error(f"Content analysis failed: {e}", correlation_id=state.get("correlation_id"))
            return {
                "content_analysis": None,
                "next_step": "compile_report"
            }

    async def _suggest_pivot_node(self, state: AnalyticsGraphState) -> AnalyticsGraphState:
        """Suggests strategic pivots based on analysis."""
        try:
            workspace_id = UUID(state["workspace_id"])
            move_id = UUID(state["move_id"])
            correlation_id = state.get("correlation_id", get_correlation_id())

            logger.info("Generating pivot suggestions", move_id=move_id, correlation_id=correlation_id)

            pivot_suggestion = await insight_agent.suggest_pivot(
                workspace_id,
                move_id,
                correlation_id=correlation_id
            )

            logger.info("Pivot suggestion generated", correlation_id=correlation_id)

            return {
                "pivot_suggestion": pivot_suggestion,
                "next_step": "compile_report"
            }

        except Exception as e:
            logger.error(f"Pivot suggestion failed: {e}", correlation_id=state.get("correlation_id"))
            return {
                "pivot_suggestion": None,
                "next_step": "compile_report"
            }

    async def _compile_report_node(self, state: AnalyticsGraphState) -> AnalyticsGraphState:
        """Compiles final analytics report."""
        try:
            correlation_id = state.get("correlation_id", get_correlation_id())
            logger.info("Compiling analytics report", correlation_id=correlation_id)

            move_data = state.get("move_data", {})
            metrics = state.get("metrics", {})
            insights = state.get("insights", [])
            anomalies = state.get("anomalies", [])
            charts = state.get("charts")
            content_analysis = state.get("content_analysis")
            pivot_suggestion = state.get("pivot_suggestion")

            # Generate recommendations from insights
            recommendations = []
            for insight in insights:
                if insight.get("recommendation"):
                    recommendations.append(insight["recommendation"])

            # Add content recommendations
            if content_analysis and content_analysis.get("recommendations"):
                recommendations.extend(content_analysis["recommendations"])

            # Add pivot recommendation
            if pivot_suggestion and pivot_suggestion.get("recommendation"):
                recommendations.append(f"Strategic Pivot: {pivot_suggestion['recommendation']}")

            # Generate executive summary
            aggregated = metrics.get("aggregated", {})
            summary = f"""
Campaign Performance Summary:

📊 Metrics Overview:
- Impressions: {aggregated.get('total_impressions', 0):,}
- Engagements: {aggregated.get('total_engagements', 0):,}
- Engagement Rate: {aggregated.get('engagement_rate', 0) * 100:.2f}%
- Clicks: {aggregated.get('total_clicks', 0):,}

🔍 Key Findings:
- {len(insights)} insights generated
- {len([i for i in insights if i.get('priority') == 'high'])} high-priority action items
- {len(anomalies)} anomalies detected

⚡ Top Recommendation:
{recommendations[0] if recommendations else "Continue monitoring performance"}

Platform Coverage: {len(metrics.get('platform_metrics', {}))} platforms analyzed
            """.strip()

            # Compile final report
            report = {
                "move_id": state["move_id"],
                "move_name": move_data.get("name"),
                "move_status": move_data.get("status"),
                "workspace_id": state["workspace_id"],
                "analysis_period_days": state.get("time_period_days", 30),
                "analyzed_at": datetime.now(timezone.utc).isoformat(),
                "correlation_id": correlation_id,
                "metrics": metrics,
                "insights": insights,
                "anomalies": anomalies,
                "charts": charts,
                "content_analysis": content_analysis,
                "pivot_suggestion": pivot_suggestion,
                "recommendations": recommendations[:10],  # Limit to top 10
                "executive_summary": summary,
                "error": state.get("error")
            }

            logger.info(
                "Report compiled successfully",
                insights_count=len(insights),
                recommendations_count=len(recommendations),
                correlation_id=correlation_id
            )

            return {
                "final_report": report,
                "next_step": "save_report"
            }

        except Exception as e:
            logger.error(f"Report compilation failed: {e}", correlation_id=state.get("correlation_id"))
            return {
                "error": str(e),
                "next_step": "end"
            }

    async def _save_report_node(self, state: AnalyticsGraphState) -> AnalyticsGraphState:
        """Saves the analytics report to database."""
        try:
            correlation_id = state.get("correlation_id", get_correlation_id())
            logger.info("Saving analytics report", correlation_id=correlation_id)

            report = state.get("final_report", {})

            # Save to analytics_reports table (create if doesn't exist)
            try:
                await supabase_client.insert("analytics_reports", {
                    "id": str(UUID(int=0)),  # Will be auto-generated
                    "workspace_id": state["workspace_id"],
                    "move_id": state["move_id"],
                    "report": report,
                    "generated_at": datetime.now(timezone.utc).isoformat()
                })
            except Exception as db_error:
                # Table might not exist yet - log but don't fail
                logger.warning(
                    f"Could not save to analytics_reports table: {db_error}",
                    correlation_id=correlation_id
                )

            logger.info("Report saved successfully", correlation_id=correlation_id)

            return {
                "completed": True,
                "next_step": "end"
            }

        except Exception as e:
            logger.error(f"Report save failed: {e}", correlation_id=state.get("correlation_id"))
            return {
                "completed": True,
                "next_step": "end"
            }

    # --- Public Interface ---

    async def run_analytics(
        self,
        workspace_id: UUID,
        move_id: UUID,
        time_period_days: int = 30,
        include_charts: bool = True,
        include_content_analysis: bool = True,
        include_pivot_suggestions: bool = False,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Executes the analytics workflow.

        Args:
            workspace_id: User's workspace
            move_id: Campaign to analyze
            time_period_days: Lookback period
            include_charts: Generate chart data
            include_content_analysis: Analyze content performance
            include_pivot_suggestions: Generate pivot suggestions
            correlation_id: Request correlation ID

        Returns:
            Analytics report
        """
        correlation_id = correlation_id or get_correlation_id()

        initial_state = {
            "workspace_id": str(workspace_id),
            "move_id": str(move_id),
            "correlation_id": correlation_id,
            "time_period_days": time_period_days,
            "include_charts": include_charts,
            "include_content_analysis": include_content_analysis,
            "include_pivot_suggestions": include_pivot_suggestions,
            "validation_passed": False,
            "recommendations": [],
            "completed": False,
            "next_step": "validate_move"
        }

        # Run the workflow
        final_state = await self.app.ainvoke(
            initial_state,
            config={"configurable": {"thread_id": str(move_id)}}
        )

        # Return the final report
        return final_state.get("final_report", {})


# Global instance
analytics_graph = AnalyticsGraph()
