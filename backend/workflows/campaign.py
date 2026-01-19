"""
CampaignWorkflow - End-to-end campaign orchestration.
Handles campaign planning, move addition, launch, and reporting.
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


class CampaignWorkflow:
    """
    End-to-end campaign workflow orchestrator.

    Handles the complete campaign lifecycle from planning through
    execution, monitoring, and results reporting.
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

    async def plan_campaign(self, workspace_id: str, goal: str) -> Dict[str, Any]:
        """
        Plan a comprehensive campaign.

        Args:
            workspace_id: Workspace ID
            goal: Campaign goal

        Returns:
            Campaign planning result
        """
        try:
            logger.info(f"Planning campaign: {goal} for workspace {workspace_id}")

            # Get workspace context
            context = await self._get_workspace_context(workspace_id)

            # Step 1: Gather campaign context
            campaign_context = await self._gather_campaign_context(
                workspace_id, context
            )

            # Step 2: Generate campaign plan
            planning_result = await self._generate_campaign_plan(
                workspace_id, goal, campaign_context, context
            )

            if not planning_result["success"]:
                return planning_result

            # Step 3: Validate campaign plan
            validation_result = await self._validate_campaign_plan(
                workspace_id, planning_result["plan"], context
            )

            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": "Campaign plan validation failed",
                    "validation_issues": validation_result["issues"],
                }

            # Step 4: Create campaign record
            campaign_record = {
                "workspace_id": workspace_id,
                "name": planning_result["plan"]["name"],
                "description": planning_result["plan"]["description"],
                "goal": goal,
                "status": "planned",
                "target_icps": planning_result["plan"]["target_icps"],
                "estimated_duration": planning_result["plan"]["estimated_duration"],
                "estimated_budget": planning_result["plan"]["estimated_budget"],
                "risk_level": planning_result["plan"]["risk_level"],
                "created_at": time.time(),
            }

            result = self.db_client.table("campaigns").insert(campaign_record).execute()

            if not result.data:
                return {"success": False, "error": "Failed to create campaign record"}

            campaign_id = result.data[0]["id"]

            # Step 5: Store campaign in memory
            await self._store_campaign_in_memory(
                workspace_id, campaign_id, planning_result["plan"]
            )

            return {
                "success": True,
                "campaign_id": campaign_id,
                "plan": planning_result["plan"],
                "validation": validation_result,
                "created_at": time.time(),
            }

        except Exception as e:
            logger.error(f"Error planning campaign: {e}")
            return {"success": False, "error": str(e)}

    async def add_moves(self, campaign_id: str, moves: List[str]) -> Dict[str, Any]:
        """
        Add moves to campaign.

        Args:
            campaign_id: Campaign ID
            moves: List of move IDs to add

        Returns:
            Move addition result
        """
        try:
            logger.info(f"Adding moves to campaign {campaign_id}")

            # Get campaign details
            campaign_result = (
                self.db_client.table("campaigns")
                .select("*")
                .eq("id", campaign_id)
                .execute()
            )

            if not campaign_result.data:
                return {"success": False, "error": "Campaign not found"}

            campaign = campaign_result.data[0]
            workspace_id = campaign["workspace_id"]

            # Validate moves exist and belong to workspace
            valid_moves = []
            for move_id in moves:
                move_result = (
                    self.db_client.table("moves")
                    .select("*")
                    .eq("id", move_id)
                    .eq("workspace_id", workspace_id)
                    .execute()
                )
                if move_result.data:
                    valid_moves.append(move_id)
                else:
                    logger.warning(
                        f"Move {move_id} not found or doesn't belong to workspace"
                    )

            if not valid_moves:
                return {"success": False, "error": "No valid moves to add"}

            # Add moves to campaign
            campaign_moves = []
            for move_id in valid_moves:
                campaign_move = {
                    "campaign_id": campaign_id,
                    "move_id": move_id,
                    "added_at": time.time(),
                }
                campaign_moves.append(campaign_move)

            # Batch insert campaign moves
            if campaign_moves:
                self.db_client.table("campaign_moves").insert(campaign_moves).execute()

            # Update campaign status
            self.db_client.table("campaigns").update(
                {
                    "status": "ready",
                    "moves_count": len(valid_moves),
                    "updated_at": time.time(),
                }
            ).eq("id", campaign_id).execute()

            return {
                "success": True,
                "campaign_id": campaign_id,
                "moves_added": len(valid_moves),
                "valid_moves": valid_moves,
                "total_moves": len(valid_moves),
            }

        except Exception as e:
            logger.error(f"Error adding moves to campaign {campaign_id}: {e}")
            return {"success": False, "error": str(e)}

    async def launch_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        Launch campaign with full orchestration.

        Args:
            campaign_id: Campaign ID to launch

        Returns:
            Campaign launch result
        """
        try:
            logger.info(f"Launching campaign: {campaign_id}")

            # Get campaign details
            campaign_result = (
                self.db_client.table("campaigns")
                .select("*")
                .eq("id", campaign_id)
                .execute()
            )

            if not campaign_result.data:
                return {"success": False, "error": "Campaign not found"}

            campaign = campaign_result.data[0]
            workspace_id = campaign["workspace_id"]

            # Validate campaign is ready
            if campaign["status"] != "ready":
                return {"success": False, "error": "Campaign not ready for launch"}

            # Get campaign moves
            moves_result = (
                self.db_client.table("campaign_moves")
                .select("*, moves.*")
                .eq("campaign_id", campaign_id)
                .execute()
            )

            if not moves_result.data:
                return {"success": False, "error": "No moves found in campaign"}

            # Update campaign status
            self.db_client.table("campaigns").update(
                {"status": "launching", "launched_at": time.time()}
            ).eq("id", campaign_id).execute()

            # Step 1: Execute campaign phases
            execution_results = await self._execute_campaign_phases(
                campaign_id, moves_result.data, workspace_id
            )

            # Step 2: Monitor campaign performance
            monitoring_result = await self._monitor_campaign_performance(
                campaign_id, execution_results
            )

            # Step 3: Generate campaign report
            report_result = await self._generate_campaign_report(
                campaign_id, execution_results, monitoring_result
            )

            # Step 4: Update campaign status
            self.db_client.table("campaigns").update(
                {
                    "status": "active",
                    "active_at": time.time(),
                    "execution_summary": {
                        "total_moves": len(execution_results),
                        "successful_moves": len(
                            [r for r in execution_results if r["success"]]
                        ),
                        "failed_moves": len(
                            [r for r in execution_results if not r["success"]]
                        ),
                    },
                    "performance_metrics": monitoring_result,
                    "report": report_result,
                }
            ).eq("id", campaign_id).execute()

            return {
                "success": True,
                "campaign_id": campaign_id,
                "execution_results": execution_results,
                "performance_metrics": monitoring_result,
                "report": report_result,
                "launched_at": time.time(),
            }

        except Exception as e:
            logger.error(f"Error launching campaign {campaign_id}: {e}")
            return {"success": False, "error": str(e)}

    async def report_results(self, campaign_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive campaign results report.

        Args:
            campaign_id: Campaign ID to report on

        Returns:
            Campaign results report
        """
        try:
            logger.info(f"Generating campaign report: {campaign_id}")

            # Get campaign details
            campaign_result = (
                self.db_client.table("campaigns")
                .select("*")
                .eq("id", campaign_id)
                .execute()
            )

            if not campaign_result.data:
                return {"success": False, "error": "Campaign not found"}

            campaign = campaign_result.data[0]
            workspace_id = campaign["workspace_id"]

            # Get campaign execution data
            execution_result = (
                self.db_client.table("campaign_executions")
                .select("*")
                .eq("campaign_id", campaign_id)
                .execute()
            )

            # Get campaign performance data
            performance_result = (
                self.db_client.table("campaign_performance")
                .select("*")
                .eq("campaign_id", campaign_id)
                .execute()
            )

            # Get workspace context
            context = await self._get_workspace_context(workspace_id)

            # Step 1: Generate comprehensive report
            report_result = await self._generate_comprehensive_report(
                campaign, execution_result.data, performance_result.data, context
            )

            # Step 2: Store report
            report_record = {
                "campaign_id": campaign_id,
                "report_data": report_result,
                "generated_at": time.time(),
            }

            result = (
                self.db_client.table("campaign_reports").insert(report_record).execute()
            )

            if result.data:
                return {
                    "success": True,
                    "report_id": result.data[0]["id"],
                    "report": report_result,
                    "generated_at": time.time(),
                }
            else:
                return {"success": False, "error": "Failed to store report"}

        except Exception as e:
            logger.error(f"Error generating campaign report {campaign_id}: {e}")
            return {"success": False, "error": str(e)}

    async def _gather_campaign_context(
        self, workspace_id: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gather comprehensive context for campaign planning."""
        try:
            campaign_context = {
                "workspace_id": workspace_id,
                "foundation": {},
                "icps": [],
                "available_moves": [],
                "past_campaigns": [],
                "market_insights": {},
            }

            # Get foundation data
            foundation_result = (
                self.db_client.table("foundations")
                .select("*")
                .eq("workspace_id", workspace_id)
                .execute()
            )
            if foundation_result.data:
                campaign_context["foundation"] = foundation_result.data[0]

            # Get ICPs
            icp_result = (
                self.db_client.table("icp_profiles")
                .select("*")
                .eq("workspace_id", workspace_id)
                .execute()
            )
            if icp_result.data:
                campaign_context["icps"] = icp_result.data

            # Get available moves
            moves_result = (
                self.db_client.table("moves")
                .select("*")
                .eq("workspace_id", workspace_id)
                .eq("status", "planned")
                .execute()
            )
            if moves_result.data:
                campaign_context["available_moves"] = moves_result.data

            # Get past campaigns
            past_campaigns_result = (
                self.db_client.table("campaigns")
                .select("*")
                .eq("workspace_id", workspace_id)
                .eq("status", "completed")
                .execute()
            )
            if past_campaigns_result.data:
                campaign_context["past_campaigns"] = past_campaigns_result.data

            # Get market insights from memory
            try:
                market_insights = await self.memory_controller.search(
                    workspace_id=workspace_id,
                    query="campaign performance market analysis",
                    memory_types=["research", "conversation"],
                    limit=10,
                )
                campaign_context["market_insights"] = market_insights
            except Exception as e:
                logger.warning(f"Error getting market insights: {e}")

            return campaign_context

        except Exception as e:
            logger.error(f"Error gathering campaign context: {e}")
            return {"workspace_id": workspace_id}

    async def _generate_campaign_plan(
        self,
        workspace_id: str,
        goal: str,
        campaign_context: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate campaign plan using campaign planner agent."""
        try:
            agent = self.agent_dispatcher.get_agent("campaign_planner")

            state = AgentState()
            state.update(
                {
                    "workspace_id": workspace_id,
                    "user_id": context["user_id"],
                    "goal": goal,
                    "campaign_context": campaign_context,
                    "task": "generate_campaign_plan",
                }
            )

            result = await agent.execute(state)

            plan = result.get("campaign_plan", {})

            if not plan:
                return {"success": False, "error": "No campaign plan generated"}

            return {"success": True, "plan": plan}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _validate_campaign_plan(
        self, workspace_id: str, plan: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate campaign plan using cognitive engine."""
        try:
            # Use cognitive reflection for validation
            reflection_result = await self.cognitive_engine.reflection.reflect(
                output=str(plan),
                goal="Validate campaign plan",
                context=context,
                max_iterations=2,
            )

            issues = []
            if reflection_result.quality_score < 0.7:
                issues.append("Plan quality score below threshold")

            if not plan.get("target_icps"):
                issues.append("No target ICPs defined")

            if not plan.get("phases"):
                issues.append("No campaign phases defined")

            if plan.get("estimated_budget", 0) > 10000:  # Example budget limit
                issues.append("Estimated budget exceeds limit")

            return {
                "valid": len(issues) == 0,
                "issues": issues,
                "quality_score": reflection_result.quality_score,
                "feedback": reflection_result.feedback,
            }

        except Exception as e:
            return {"valid": False, "issues": [str(e)]}

    async def _store_campaign_in_memory(
        self, workspace_id: str, campaign_id: str, plan: Dict[str, Any]
    ):
        """Store campaign in memory system."""
        try:
            content = f"""
            Campaign: {plan.get('name')}
            Goal: {plan.get('goal')}
            Target ICPs: {plan.get('target_icps', [])}
            Duration: {plan.get('estimated_duration')}
            Budget: ${plan.get('estimated_budget', 0)}
            Phases: {len(plan.get('phases', []))}
            """

            await self.memory_controller.store(
                workspace_id=workspace_id,
                memory_type="campaign",
                content=content,
                metadata={
                    "campaign_id": campaign_id,
                    "name": plan.get("name"),
                    "goal": plan.get("goal"),
                    "target_icps": plan.get("target_icps", []),
                },
            )

        except Exception as e:
            logger.error(f"Error storing campaign in memory: {e}")

    async def _execute_campaign_phases(
        self, campaign_id: str, campaign_moves: List[Dict[str, Any]], workspace_id: str
    ) -> List[Dict[str, Any]]:
        """Execute campaign phases with move orchestration."""
        try:
            execution_results = []

            # Group moves by priority or sequence
            move_groups = self._group_moves_for_execution(campaign_moves)

            for group in move_groups:
                group_result = await self._execute_move_group(
                    campaign_id, group, workspace_id
                )
                execution_results.append(group_result)

                # Update campaign progress
                await self._update_campaign_progress(campaign_id, group, group_result)

            return execution_results

        except Exception as e:
            logger.error(f"Error executing campaign phases: {e}")
            return []

    def _group_moves_for_execution(
        self, campaign_moves: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """Group moves for execution."""
        # Simple grouping by priority
        high_priority = [m for m in campaign_moves if m.get("priority", 5) <= 2]
        medium_priority = [m for m in campaign_moves if 2 < m.get("priority", 5) <= 4]
        low_priority = [m for m in campaign_moves if m.get("priority", 5) > 4]

        groups = []
        if high_priority:
            groups.append(high_priority)
        if medium_priority:
            groups.append(medium_priority)
        if low_priority:
            groups.append(low_priority)

        return groups

    async def _execute_move_group(
        self, campaign_id: str, move_group: List[Dict[str, Any]], workspace_id: str
    ) -> Dict[str, Any]:
        """Execute a group of moves."""
        try:
            group_name = f"Phase_{len(move_group)}_{'_'.join([m['moves']['title'] for m in move_group[:3]])}"

            # Execute moves in parallel
            move_tasks = []
            for move_data in move_group:
                move = move_data["moves"]

                # Create move execution task
                task = asyncio.create_task(
                    self._execute_single_move(campaign_id, move, workspace_id)
                )
                move_tasks.append(task)

            # Wait for all moves to complete
            results = await asyncio.gather(*move_tasks, return_exceptions=True)

            # Process results
            successful_moves = []
            failed_moves = []

            for i, result in enumerate(results):
                move = move_group[i]["moves"]
                if isinstance(result, Exception):
                    failed_moves.append({"move_id": move["id"], "error": str(result)})
                elif result["success"]:
                    successful_moves.append(result)
                else:
                    failed_moves.append(
                        {"move_id": move["id"], "error": "Move execution failed"}
                    )

            return {
                "success": len(success_moves) > 0,
                "group_name": group_name,
                "total_moves": len(move_group),
                "successful_moves": len(successful_moves),
                "failed_moves": len(failed_moves),
                "results": results,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _execute_single_move(
        self, campaign_id: str, move: Dict[str, Any], workspace_id: str
    ) -> Dict[str, Any]:
        """Execute a single move within campaign context."""
        try:
            # Use move workflow to execute move
            from .move import MoveWorkflow

            move_workflow = MoveWorkflow(
                self.db_client,
                self.memory_controller,
                self.cognitive_engine,
                self.agent_dispatcher,
            )

            # Execute move
            execution_result = await move_workflow.execute_move(move["id"])

            # Add campaign context to result
            execution_result["campaign_id"] = campaign_id

            return execution_result

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _update_campaign_progress(
        self,
        campaign_id: str,
        move_group: List[Dict[str, Any]],
        group_result: Dict[str, Any],
    ):
        """Update campaign progress."""
        try:
            progress_record = {
                "campaign_id": campaign_id,
                "group_name": group_result["group_name"],
                "status": "completed" if group_result["success"] else "failed",
                "completed_at": time.time(),
                "total_moves": group_result["total_moves"],
                "successful_moves": group_result["successful_moves"],
                "failed_moves": group_result["failed_moves"],
            }

            self.db_client.table("campaign_progress").insert(progress_record).execute()

        except Exception as e:
            logger.error(f"Error updating campaign progress: {e}")

    async def _monitor_campaign_performance(
        self, campaign_id: str, execution_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Monitor campaign performance metrics."""
        try:
            # Calculate performance metrics
            total_moves = sum(
                r["total_moves"] for r in execution_results if "total_moves" in r
            )
            successful_moves = sum(
                r["successful_moves"]
                for r in execution_results
                if "successful_moves" in r
            )
            failed_moves = sum(
                r["failed_moves"] for r in execution_results if "failed_moves" in r
            )

            success_rate = (
                (successful_moves / total_moves) * 100 if total_moves > 0 else 0
            )

            # Get campaign details for cost analysis
            campaign_result = (
                self.db_client.table("campaigns")
                .select("*")
                .eq("id", campaign_id)
                .execute()
            )
            campaign = campaign_result.data[0] if campaign_result.data else {}

            performance_metrics = {
                "total_moves": total_moves,
                "successful_moves": successful_moves,
                "failed_moves": failed_moves,
                "success_rate": success_rate,
                "estimated_budget": campaign.get("estimated_budget", 0),
                "actual_cost": 0.0,  # Would integrate with billing
                "roi": 0.0,  # Would calculate based on results
                "engagement_metrics": {
                    "impressions": 0,
                    "clicks": 0,
                    "conversions": 0,
                    "engagement_rate": 0.0,
                },
            }

            return performance_metrics

        except Exception as e:
            return {"error": str(e)}

    async def _generate_campaign_report(
        self,
        campaign_id: str,
        execution_results: List[Dict[str, Any]],
        performance_metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate comprehensive campaign report."""
        try:
            # Get campaign details
            campaign_result = (
                self.db_client.table("campaigns")
                .select("*")
                .eq("id", campaign_id)
                .execute()
            )
            campaign = campaign_result.data[0] if campaign_result.data else {}

            # Use analytics agent for report generation
            agent = self.agent_dispatcher.get_agent("analytics_agent")

            state = AgentState()
            state.update(
                {
                    "task": "generate_campaign_report",
                    "campaign": campaign,
                    "execution_results": execution_results,
                    "performance_metrics": performance_metrics,
                }
            )

            result = await agent.execute(state)

            report = result.get("campaign_report", {})

            return {
                "executive_summary": report.get("executive_summary"),
                "detailed_analysis": report.get("detailed_analysis"),
                "recommendations": report.get("recommendations"),
                "appendix": report.get("appendix", {}),
                "generated_at": time.time(),
            }

        except Exception as e:
            return {"error": str(e)}

    async def _generate_comprehensive_report(
        self,
        campaign: Dict[str, Any],
        execution_results: List[Dict[str, Any]],
        performance_metrics: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate comprehensive campaign report."""
        try:
            # Calculate comprehensive metrics
            total_phases = len(execution_results)
            successful_phases = len([r for r in execution_results if r["success"]])

            # Generate insights
            insights = []

            if performance_metrics["success_rate"] >= 80:
                insights.append(
                    "Campaign performed exceptionally well with high success rate"
                )
            elif performance_metrics["success_rate"] >= 60:
                insights.append(
                    "Campaign performed adequately with moderate success rate"
                )
            else:
                insights.append("Campaign performance needs improvement")

            if performance_metrics["success_rate"] < 100:
                failed_phases = [r for r in execution_results if not r["success"]]
                insights.append(
                    f"Failed phases: {', '.join([r.get('group_name', 'Unknown') for r in failed_phases])}"
                )

            return {
                "campaign_summary": {
                    "name": campaign["name"],
                    "goal": campaign["goal"],
                    "status": campaign["status"],
                    "created_at": campaign["created_at"],
                    "launched_at": campaign.get("launched_at"),
                },
                "execution_summary": {
                    "total_phases": total_phases,
                    "successful_phases": successful_phases,
                    "failed_phases": total_phases - successful_phases,
                    "success_rate": performance_metrics["success_rate"],
                },
                "performance_analysis": performance_metrics,
                "key_insights": insights,
                "recommendations": self._generate_recommendations(
                    campaign, performance_metrics
                ),
                "generated_at": time.time(),
            }

        except Exception as e:
            return {"error": str(e)}

    def _generate_recommendations(
        self, campaign: Dict[str, Any], performance_metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on campaign performance."""
        recommendations = []

        if performance_metrics["success_rate"] < 50:
            recommendations.append(
                "Consider revising campaign strategy and move selection"
            )

        if performance_metrics["success_rate"] < 70:
            recommendations.append("Improve move execution quality and coordination")

        if campaign.get("estimated_budget", 0) > performance_metrics.get(
            "actual_cost", 0
        ):
            recommendations.append("Optimize budget allocation and cost management")

        if performance_metrics["engagement_metrics"]["engagement_rate"] < 2.0:
            recommendations.append("Enhance content quality and targeting")

        if not recommendations:
            recommendations.append(
                "Campaign performance is good, consider scaling successful elements"
            )

        return recommendations

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
