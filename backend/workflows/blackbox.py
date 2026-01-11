"""
BlackboxWorkflow - End-to-end blackbox strategy orchestration.
Handles bold strategy generation, review, and conversion to actionable moves.
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


class BlackboxWorkflow:
    """
    End-to-end blackbox strategy workflow orchestrator.

    Handles the complete blackbox strategy process from bold idea
    generation through risk assessment, review, and conversion to moves.
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

    async def generate_strategy(self, workspace_id: str) -> Dict[str, Any]:
        """
        Generate bold blackbox strategy with full orchestration.

        Args:
            workspace_id: Workspace ID

        Returns:
            Strategy generation result
        """
        try:
            logger.info(f"Generating blackbox strategy for workspace {workspace_id}")

            # Get workspace context
            context = await self._get_workspace_context(workspace_id)

            # Step 1: Gather context data
            context_data = await self._gather_strategy_context(workspace_id, context)

            # Step 2: Generate bold strategy
            strategy_result = await self._generate_bold_strategy(
                workspace_id, context_data, context
            )

            if not strategy_result["success"]:
                return strategy_result

            # Step 3: Risk assessment
            risk_result = await self._assess_strategy_risks(
                workspace_id, strategy_result["strategy"], context
            )

            # Step 4: Create strategy record
            strategy_record = {
                "workspace_id": workspace_id,
                "title": strategy_result["strategy"]["title"],
                "description": strategy_result["strategy"]["description"],
                "bold_idea": strategy_result["strategy"]["bold_idea"],
                "risk_level": risk_result["risk_level"],
                "risk_score": risk_result["risk_score"],
                "status": "generated",
                "generated_at": time.time(),
            }

            result = (
                self.db_client.table("blackbox_strategies")
                .insert(strategy_record)
                .execute()
            )

            if not result.data:
                return {"success": False, "error": "Failed to create strategy record"}

            strategy_id = result.data[0]["id"]

            # Step 5: Store in memory
            await self._store_strategy_in_memory(
                workspace_id, strategy_id, strategy_result["strategy"]
            )

            # Step 6: Create review request
            review_result = await self._create_strategy_review(strategy_id, risk_result)

            return {
                "success": True,
                "strategy_id": strategy_id,
                "strategy": strategy_result["strategy"],
                "risk_assessment": risk_result,
                "review_request": review_result,
                "generated_at": time.time(),
            }

        except Exception as e:
            logger.error(f"Error generating strategy: {e}")
            return {"success": False, "error": str(e)}

    async def review_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """
        Review blackbox strategy with comprehensive assessment.

        Args:
            strategy_id: Strategy ID to review

        Returns:
            Strategy review result
        """
        try:
            logger.info(f"Reviewing blackbox strategy: {strategy_id}")

            # Get strategy details
            strategy_result = (
                self.db_client.table("blackbox_strategies")
                .select("*")
                .eq("id", strategy_id)
                .execute()
            )

            if not strategy_result.data:
                return {"success": False, "error": "Strategy not found"}

            strategy = strategy_result.data[0]
            workspace_id = strategy["workspace_id"]

            # Get workspace context
            context = await self._get_workspace_context(workspace_id)

            # Step 1: Comprehensive strategy analysis
            analysis_result = await self._analyze_strategy_comprehensive(
                strategy, context
            )

            # Step 2: Feasibility assessment
            feasibility_result = await self._assess_strategy_feasibility(
                strategy, analysis_result, context
            )

            # Step 3: Generate review feedback
            feedback_result = await self._generate_strategy_feedback(
                strategy, analysis_result, feasibility_result
            )

            # Step 4: Update strategy record
            self.db_client.table("blackbox_strategies").update(
                {
                    "review_status": "completed",
                    "analysis": analysis_result,
                    "feasibility": feasibility_result,
                    "feedback": feedback_result,
                    "reviewed_at": time.time(),
                }
            ).eq("id", strategy_id).execute()

            # Step 5: Determine conversion readiness
            conversion_ready = (
                feasibility_result["feasibility_score"] >= 0.7
                and analysis_result["quality_score"] >= 0.7
            )

            return {
                "success": True,
                "strategy_id": strategy_id,
                "analysis": analysis_result,
                "feasibility": feasibility_result,
                "feedback": feedback_result,
                "conversion_ready": conversion_ready,
                "review_completed": True,
            }

        except Exception as e:
            logger.error(f"Error reviewing strategy {strategy_id}: {e}")
            return {"success": False, "error": str(e)}

    async def convert_to_move(self, strategy_id: str) -> Dict[str, Any]:
        """
        Convert blackbox strategy to actionable moves.

        Args:
            strategy_id: Strategy ID to convert

        Returns:
            Conversion result
        """
        try:
            logger.info(f"Converting strategy to moves: {strategy_id}")

            # Get strategy details
            strategy_result = (
                self.db_client.table("blackbox_strategies")
                .select("*")
                .eq("id", strategy_id)
                .execute()
            )

            if not strategy_result.data:
                return {"success": False, "error": "Strategy not found"}

            strategy = strategy_result.data[0]
            workspace_id = strategy["workspace_id"]

            # Get workspace context
            context = await self._get_workspace_context(workspace_id)

            # Step 1: Decompose strategy into moves
            decomposition_result = await self._decompose_strategy_to_moves(
                strategy, context
            )

            if not decomposition_result["success"]:
                return decomposition_result

            # Step 2: Create move records
            move_results = []
            for move_data in decomposition_result["moves"]:
                move_result = await self._create_move_from_strategy(
                    workspace_id, move_data, strategy_id, context
                )
                move_results.append(move_result)

            # Step 3: Create move relationships
            await self._create_move_relationships(move_results, strategy_id)

            # Step 4: Update strategy status
            successful_moves = [r for r in move_results if r["success"]]

            self.db_client.table("blackbox_strategies").update(
                {
                    "status": "converted",
                    "converted_at": time.time(),
                    "moves_created": len(successful_moves),
                    "conversion_summary": {
                        "total_moves": len(move_results),
                        "successful_moves": len(successful_moves),
                        "conversion_rate": (len(successful_moves) / len(move_results))
                        * 100,
                    },
                }
            ).eq("id", strategy_id).execute()

            return {
                "success": len(successful_moves) > 0,
                "strategy_id": strategy_id,
                "moves_created": len(successful_moves),
                "move_ids": [r["move_id"] for r in successful_moves],
                "conversion_summary": {
                    "total_moves": len(move_results),
                    "successful_moves": len(successful_moves),
                    "conversion_rate": (len(successful_moves) / len(move_results))
                    * 100,
                },
            }

        except Exception as e:
            logger.error(f"Error converting strategy {strategy_id}: {e}")
            return {"success": False, "error": str(e)}

    async def _gather_strategy_context(
        self, workspace_id: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gather comprehensive context for strategy generation."""
        try:
            context_data = {
                "workspace_id": workspace_id,
                "foundation": {},
                "icps": [],
                "existing_moves": [],
                "campaigns": [],
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
                context_data["foundation"] = foundation_result.data[0]

            # Get ICPs
            icp_result = (
                self.db_client.table("icp_profiles")
                .select("*")
                .eq("workspace_id", workspace_id)
                .execute()
            )
            if icp_result.data:
                context_data["icps"] = icp_result.data

            # Get existing moves
            moves_result = (
                self.db_client.table("moves")
                .select("*")
                .eq("workspace_id", workspace_id)
                .execute()
            )
            if moves_result.data:
                context_data["existing_moves"] = moves_result.data

            # Get campaigns
            campaigns_result = (
                self.db_client.table("campaigns")
                .select("*")
                .eq("workspace_id", workspace_id)
                .execute()
            )
            if campaigns_result.data:
                context_data["campaigns"] = campaigns_result.data

            # Get market insights from memory
            try:
                market_insights = await self.memory_controller.search(
                    workspace_id=workspace_id,
                    query="market trends competitor analysis",
                    memory_types=["research", "conversation"],
                    limit=10,
                )
                context_data["market_insights"] = market_insights
            except Exception as e:
                logger.warning(f"Error getting market insights: {e}")

            return context_data

        except Exception as e:
            logger.error(f"Error gathering strategy context: {e}")
            return {"workspace_id": workspace_id}

    async def _generate_bold_strategy(
        self, workspace_id: str, context_data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate bold strategy using blackbox strategist agent."""
        try:
            agent = self.agent_dispatcher.get_agent("blackbox_strategist")

            state = AgentState()
            state.update(
                {
                    "workspace_id": workspace_id,
                    "user_id": context["user_id"],
                    "context_data": context_data,
                    "task": "generate_bold_strategy",
                }
            )

            result = await agent.execute(state)

            strategy = result.get("strategy", {})

            if not strategy:
                return {"success": False, "error": "No strategy generated"}

            return {"success": True, "strategy": strategy}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _assess_strategy_risks(
        self, workspace_id: str, strategy: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess strategy risks using cognitive engine."""
        try:
            # Use adversarial critic for risk assessment
            critic_result = await self.cognitive_engine.critic.analyze(
                output=str(strategy), context=context, analysis_type="risk_assessment"
            )

            # Calculate risk metrics
            risk_score = critic_result.get("risk_score", 0.5)
            risk_level = self._determine_risk_level(risk_score)

            return {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_factors": critic_result.get("risk_factors", []),
                "mitigation_suggestions": critic_result.get(
                    "mitigation_suggestions", []
                ),
                "confidence": critic_result.get("confidence", 0.5),
            }

        except Exception as e:
            return {"risk_score": 0.5, "error": str(e)}

    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level from score."""
        if risk_score >= 0.8:
            return "high"
        elif risk_score >= 0.6:
            return "medium"
        else:
            return "low"

    async def _store_strategy_in_memory(
        self, workspace_id: str, strategy_id: str, strategy: Dict[str, Any]
    ):
        """Store strategy in memory system."""
        try:
            content = f"""
            Blackbox Strategy: {strategy.get('title')}
            Bold Idea: {strategy.get('bold_idea')}
            Description: {strategy.get('description')}
            Innovation Level: {strategy.get('innovation_level')}
            Market Disruption: {strategy.get('market_disruption')}
            """

            await self.memory_controller.store(
                workspace_id=workspace_id,
                memory_type="strategy",
                content=content,
                metadata={
                    "strategy_id": strategy_id,
                    "type": "blackbox_strategy",
                    "title": strategy.get("title"),
                    "innovation_level": strategy.get("innovation_level"),
                },
            )

        except Exception as e:
            logger.error(f"Error storing strategy in memory: {e}")

    async def _create_strategy_review(
        self, strategy_id: str, risk_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create strategy review request."""
        try:
            review_request = {
                "strategy_id": strategy_id,
                "risk_score": risk_result["risk_score"],
                "risk_level": risk_result["risk_level"],
                "status": "pending",
                "created_at": time.time(),
            }

            result = (
                self.db_client.table("strategy_reviews")
                .insert(review_request)
                .execute()
            )

            return {
                "review_needed": True,
                "review_id": result.data[0]["id"] if result.data else None,
                "risk_level": risk_result["risk_level"],
            }

        except Exception as e:
            return {"review_needed": False, "error": str(e)}

    async def _analyze_strategy_comprehensive(
        self, strategy: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Comprehensive strategy analysis."""
        try:
            # Use cognitive engine for analysis
            analysis_result = await self.cognitive_engine.reflection.reflect(
                output=str(strategy),
                goal="Analyze strategy comprehensively",
                context=context,
                max_iterations=3,
            )

            return {
                "quality_score": analysis_result.quality_score,
                "innovation_score": analysis_result.get("innovation_score", 0.5),
                "feasibility_score": analysis_result.get("feasibility_score", 0.5),
                "market_alignment": analysis_result.get("market_alignment", 0.5),
                "strengths": analysis_result.get("strengths", []),
                "weaknesses": analysis_result.get("weaknesses", []),
                "opportunities": analysis_result.get("opportunities", []),
                "threats": analysis_result.get("threats", []),
            }

        except Exception as e:
            return {"quality_score": 0.0, "error": str(e)}

    async def _assess_strategy_feasibility(
        self,
        strategy: Dict[str, Any],
        analysis_result: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Assess strategy feasibility."""
        try:
            # Use move strategist for feasibility assessment
            agent = self.agent_dispatcher.get_agent("move_strategist")

            state = AgentState()
            state.update(
                {
                    "workspace_id": context["workspace_id"],
                    "user_id": context["user_id"],
                    "task": "assess_strategy_feasibility",
                    "strategy": strategy,
                    "analysis": analysis_result,
                }
            )

            result = await agent.execute(state)

            feasibility = result.get("feasibility_assessment", {})

            return {
                "feasibility_score": feasibility.get("score", 0.5),
                "resource_requirements": feasibility.get("resource_requirements", {}),
                "timeline_estimate": feasibility.get("timeline_estimate"),
                "cost_estimate": feasibility.get("cost_estimate"),
                "implementation_complexity": feasibility.get("complexity", "medium"),
                "success_probability": feasibility.get("success_probability", 0.5),
            }

        except Exception as e:
            return {"feasibility_score": 0.0, "error": str(e)}

    async def _generate_strategy_feedback(
        self,
        strategy: Dict[str, Any],
        analysis_result: Dict[str, Any],
        feasibility_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate comprehensive strategy feedback."""
        try:
            # Use content creator for feedback
            agent = self.agent_dispatcher.get_agent("content_creator")

            state = AgentState()
            state.update(
                {
                    "task": "generate_strategy_feedback",
                    "strategy": strategy,
                    "analysis": analysis_result,
                    "feasibility": feasibility_result,
                }
            )

            result = await agent.execute(state)

            return result.get("feedback", {})

        except Exception as e:
            return {"error": str(e)}

    async def _decompose_strategy_to_moves(
        self, strategy: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Decompose strategy into actionable moves."""
        try:
            # Use move strategist for decomposition
            agent = self.agent_dispatcher.get_agent("move_strategist")

            state = AgentState()
            state.update(
                {
                    "workspace_id": context["workspace_id"],
                    "user_id": context["user_id"],
                    "task": "decompose_strategy_to_moves",
                    "strategy": strategy,
                }
            )

            result = await agent.execute(state)

            moves = result.get("decomposed_moves", [])

            if not moves:
                return {"success": False, "error": "No moves decomposed"}

            return {"success": True, "moves": moves, "total_moves": len(moves)}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _create_move_from_strategy(
        self,
        workspace_id: str,
        move_data: Dict[str, Any],
        strategy_id: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create move record from strategy decomposition."""
        try:
            move_record = {
                "workspace_id": workspace_id,
                "title": move_data.get("title"),
                "description": move_data.get("description"),
                "goal": move_data.get("goal"),
                "type": "strategic",
                "priority": move_data.get("priority", 5),
                "status": "planned",
                "source": "blackbox_strategy",
                "source_strategy_id": strategy_id,
                "estimated_duration": move_data.get("estimated_duration"),
                "estimated_cost": move_data.get("estimated_cost"),
                "created_at": time.time(),
            }

            result = self.db_client.table("moves").insert(move_record).execute()

            if result.data:
                return {"success": True, "move_id": result.data[0]["id"]}
            else:
                return {"success": False, "error": "Failed to create move"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _create_move_relationships(
        self, move_results: List[Dict[str, Any]], strategy_id: str
    ):
        """Create relationships between strategy-derived moves."""
        try:
            successful_moves = [r for r in move_results if r["success"]]

            if len(successful_moves) < 2:
                return

            # Create move relationships
            for i, move_result in enumerate(successful_moves):
                if i < len(successful_moves) - 1:
                    # Create dependency relationship
                    relationship_record = {
                        "parent_move_id": move_result["move_id"],
                        "child_move_id": successful_moves[i + 1]["move_id"],
                        "relationship_type": "sequence",
                        "strategy_id": strategy_id,
                        "created_at": time.time(),
                    }

                    self.db_client.table("move_relationships").insert(
                        relationship_record
                    ).execute()

        except Exception as e:
            logger.error(f"Error creating move relationships: {e}")

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
