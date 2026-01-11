"""
MoveWorkflow - End-to-end move execution orchestration.
Handles move creation, execution, and completion with full agent coordination.
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


class MoveWorkflow:
    """
    End-to-end move workflow orchestrator.

    Handles the complete move lifecycle from planning through execution
    to completion and analysis.
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

    async def create_move(
        self, workspace_id: str, goal: str, move_type: str = "strategic"
    ) -> Dict[str, Any]:
        """
        Create a new move with planning and validation.

        Args:
            workspace_id: Workspace ID
            goal: Move goal
            move_type: Type of move (strategic, tactical, operational)

        Returns:
            Move creation result
        """
        try:
            logger.info(f"Creating move: {goal} for workspace {workspace_id}")

            # Get workspace context
            context = await self._get_workspace_context(workspace_id)

            # Step 1: Plan the move
            plan_result = await self._plan_move(workspace_id, goal, move_type, context)

            if not plan_result["success"]:
                return plan_result

            # Step 2: Validate the plan
            validation_result = await self._validate_move_plan(
                workspace_id, plan_result["plan"], context
            )

            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": "Move plan validation failed",
                    "validation_issues": validation_result["issues"],
                }

            # Step 3: Create move record
            move_record = {
                "workspace_id": workspace_id,
                "title": plan_result["plan"]["title"],
                "description": plan_result["plan"]["description"],
                "goal": goal,
                "type": move_type,
                "status": "planned",
                "priority": plan_result["plan"]["priority"],
                "estimated_duration": plan_result["plan"]["estimated_duration"],
                "estimated_cost": plan_result["plan"]["estimated_cost"],
                "risk_level": plan_result["plan"]["risk_level"],
                "created_at": time.time(),
            }

            result = self.db_client.table("moves").insert(move_record).execute()

            if not result.data:
                return {"success": False, "error": "Failed to create move record"}

            move_id = result.data[0]["id"]

            # Step 4: Store move tasks
            await self._create_move_tasks(move_id, plan_result["plan"]["tasks"])

            # Step 5: Store in memory
            await self._store_move_in_memory(workspace_id, move_id, plan_result["plan"])

            return {
                "success": True,
                "move_id": move_id,
                "move_data": result.data[0],
                "plan": plan_result["plan"],
                "tasks_created": len(plan_result["plan"]["tasks"]),
            }

        except Exception as e:
            logger.error(f"Error creating move: {e}")
            return {"success": False, "error": str(e)}

    async def execute_move(self, move_id: str) -> Dict[str, Any]:
        """
        Execute a move with full task orchestration.

        Args:
            move_id: Move ID to execute

        Returns:
            Move execution result
        """
        try:
            logger.info(f"Executing move: {move_id}")

            # Get move details
            move_result = (
                self.db_client.table("moves").select("*").eq("id", move_id).execute()
            )

            if not move_result.data:
                return {"success": False, "error": "Move not found"}

            move = move_result.data[0]
            workspace_id = move["workspace_id"]

            # Get move tasks
            tasks_result = (
                self.db_client.table("move_tasks")
                .select("*")
                .eq("move_id", move_id)
                .order("priority", desc=True)
                .execute()
            )

            if not tasks_result.data:
                return {"success": False, "error": "No tasks found for move"}

            # Update move status
            self.db_client.table("moves").update(
                {"status": "executing", "execution_started_at": time.time()}
            ).eq("id", move_id).execute()

            # Execute tasks
            execution_results = []
            for task in tasks_result.data:
                task_result = await self._execute_task(move_id, task, workspace_id)
                execution_results.append(task_result)

                if not task_result["success"]:
                    # Handle task failure
                    await self._handle_task_failure(move_id, task, task_result)

            # Calculate execution summary
            successful_tasks = [r for r in execution_results if r["success"]]
            failed_tasks = [r for r in execution_results if not r["success"]]

            # Update move status
            final_status = (
                "completed" if len(failed_tasks) == 0 else "completed_with_errors"
            )

            self.db_client.table("moves").update(
                {
                    "status": final_status,
                    "execution_completed_at": time.time(),
                    "successful_tasks": len(successful_tasks),
                    "failed_tasks": len(failed_tasks),
                }
            ).eq("id", move_id).execute()

            return {
                "success": True,
                "move_id": move_id,
                "execution_summary": {
                    "total_tasks": len(execution_results),
                    "successful_tasks": len(successful_tasks),
                    "failed_tasks": len(failed_tasks),
                    "success_rate": (len(successful_tasks) / len(execution_results))
                    * 100,
                },
                "results": execution_results,
            }

        except Exception as e:
            logger.error(f"Error executing move {move_id}: {e}")
            return {"success": False, "error": str(e)}

    async def complete_move(self, move_id: str) -> Dict[str, Any]:
        """
        Complete a move with analysis and cleanup.

        Args:
            move_id: Move ID to complete

        Returns:
            Move completion result
        """
        try:
            logger.info(f"Completing move: {move_id}")

            # Get move details
            move_result = (
                self.db_client.table("moves").select("*").eq("id", move_id).execute()
            )

            if not move_result.data:
                return {"success": False, "error": "Move not found"}

            move = move_result.data[0]
            workspace_id = move["workspace_id"]

            # Step 1: Analyze results
            analysis_result = await self._analyze_move_results(move_id, workspace_id)

            # Step 2: Generate insights
            insights_result = await self._generate_move_insights(
                move_id, analysis_result
            )

            # Step 3: Update knowledge base
            await self._update_knowledge_base(move_id, insights_result, workspace_id)

            # Step 4: Create follow-up recommendations
            recommendations = await self._generate_follow_up_recommendations(
                move_id, insights_result
            )

            # Step 5: Update move status
            self.db_client.table("moves").update(
                {
                    "status": "completed",
                    "completed_at": time.time(),
                    "analysis": analysis_result,
                    "insights": insights_result,
                    "recommendations": recommendations,
                }
            ).eq("id", move_id).execute()

            return {
                "success": True,
                "move_id": move_id,
                "analysis": analysis_result,
                "insights": insights_result,
                "recommendations": recommendations,
                "completed_at": time.time(),
            }

        except Exception as e:
            logger.error(f"Error completing move {move_id}: {e}")
            return {"success": False, "error": str(e)}

    async def _plan_move(
        self, workspace_id: str, goal: str, move_type: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Plan a move using move strategist agent."""
        try:
            agent = self.agent_dispatcher.get_agent("move_strategist")

            state = AgentState()
            state.update(
                {
                    "workspace_id": workspace_id,
                    "user_id": context["user_id"],
                    "goal": goal,
                    "move_type": move_type,
                    "context": context,
                }
            )

            result = await agent.execute(state)

            plan = result.get("move_plan", {})

            if not plan:
                return {"success": False, "error": "Failed to generate move plan"}

            return {"success": True, "plan": plan}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _validate_move_plan(
        self, workspace_id: str, plan: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate move plan using cognitive engine."""
        try:
            # Use cognitive reflection for validation
            reflection_result = await self.cognitive_engine.reflection.reflect(
                output=str(plan),
                goal="Validate move plan",
                context=context,
                max_iterations=2,
            )

            issues = []
            if reflection_result.quality_score < 0.7:
                issues.append("Plan quality score below threshold")

            if not plan.get("tasks"):
                issues.append("No tasks defined in plan")

            if plan.get("estimated_cost", 0) > 1000:  # Example cost limit
                issues.append("Estimated cost exceeds budget")

            return {
                "valid": len(issues) == 0,
                "issues": issues,
                "quality_score": reflection_result.quality_score,
                "feedback": reflection_result.feedback,
            }

        except Exception as e:
            return {"valid": False, "issues": [str(e)]}

    async def _create_move_tasks(self, move_id: str, tasks: List[Dict[str, Any]]):
        """Create move tasks in database."""
        try:
            for i, task in enumerate(tasks):
                task_record = {
                    "move_id": move_id,
                    "title": task.get("title"),
                    "description": task.get("description"),
                    "agent": task.get("agent"),
                    "priority": task.get("priority", 5),
                    "estimated_duration": task.get("estimated_duration"),
                    "dependencies": task.get("dependencies", []),
                    "status": "pending",
                    "order": i,
                    "created_at": time.time(),
                }

                self.db_client.table("move_tasks").insert(task_record).execute()

        except Exception as e:
            logger.error(f"Error creating move tasks: {e}")

    async def _store_move_in_memory(
        self, workspace_id: str, move_id: str, plan: Dict[str, Any]
    ):
        """Store move in memory system."""
        try:
            content = f"""
            Move: {plan.get('title')}
            Goal: {plan.get('goal')}
            Type: {plan.get('type')}
            Priority: {plan.get('priority')}
            Tasks: {len(plan.get('tasks', []))}
            """

            await self.memory_controller.store(
                workspace_id=workspace_id,
                memory_type="move",
                content=content,
                metadata={
                    "move_id": move_id,
                    "title": plan.get("title"),
                    "type": plan.get("type"),
                    "priority": plan.get("priority"),
                },
            )

        except Exception as e:
            logger.error(f"Error storing move in memory: {e}")

    async def _execute_task(
        self, move_id: str, task: Dict[str, Any], workspace_id: str
    ) -> Dict[str, Any]:
        """Execute a single task."""
        try:
            logger.info(f"Executing task: {task['title']} for move {move_id}")

            # Update task status
            self.db_client.table("move_tasks").update(
                {"status": "executing", "started_at": time.time()}
            ).eq("id", task["id"]).execute()

            # Get appropriate agent
            agent_name = task.get("agent")
            agent = self.agent_dispatcher.get_agent(agent_name)

            if not agent:
                return {"success": False, "error": f"Agent {agent_name} not available"}

            # Prepare agent state
            state = AgentState()
            state.update(
                {
                    "workspace_id": workspace_id,
                    "move_id": move_id,
                    "task_id": task["id"],
                    "task": task,
                    "messages": [],
                }
            )

            # Execute agent
            start_time = time.time()
            result = await agent.execute(state)
            execution_time = time.time() - start_time

            # Update task with results
            task_update = {
                "status": "completed" if result.get("success", True) else "failed",
                "completed_at": time.time(),
                "execution_time": execution_time,
                "result": result,
            }

            self.db_client.table("move_tasks").update(task_update).eq(
                "id", task["id"]
            ).execute()

            return {
                "success": result.get("success", True),
                "task_id": task["id"],
                "execution_time": execution_time,
                "result": result,
            }

        except Exception as e:
            logger.error(f"Error executing task {task['id']}: {e}")

            # Update task status to failed
            self.db_client.table("move_tasks").update(
                {"status": "failed", "failed_at": time.time(), "error": str(e)}
            ).eq("id", task["id"]).execute()

            return {"success": False, "error": str(e)}

    async def _handle_task_failure(
        self, move_id: str, task: Dict[str, Any], task_result: Dict[str, Any]
    ):
        """Handle task failure with recovery options."""
        try:
            logger.warning(f"Task {task['id']} failed: {task_result.get('error')}")

            # Check if task is critical
            if task.get("priority", 5) <= 2:  # High priority tasks
                # Try to retry or use fallback agent
                fallback_agent = task.get("fallback_agent")
                if fallback_agent:
                    logger.info(f"Trying fallback agent: {fallback_agent}")
                    # Implement retry logic here

            # Log failure for analysis
            failure_record = {
                "move_id": move_id,
                "task_id": task["id"],
                "error": task_result.get("error"),
                "failed_at": time.time(),
            }

            self.db_client.table("task_failures").insert(failure_record).execute()

        except Exception as e:
            logger.error(f"Error handling task failure: {e}")

    async def _analyze_move_results(
        self, move_id: str, workspace_id: str
    ) -> Dict[str, Any]:
        """Analyze move execution results."""
        try:
            # Get move tasks and results
            tasks_result = (
                self.db_client.table("move_tasks")
                .select("*")
                .eq("move_id", move_id)
                .execute()
            )

            if not tasks_result.data:
                return {"error": "No tasks found"}

            # Calculate metrics
            total_tasks = len(tasks_result.data)
            successful_tasks = len(
                [t for t in tasks_result.data if t["status"] == "completed"]
            )
            failed_tasks = len(
                [t for t in tasks_result.data if t["status"] == "failed"]
            )
            total_time = sum(t.get("execution_time", 0) for t in tasks_result.data)

            # Get move details
            move_result = (
                self.db_client.table("moves").select("*").eq("id", move_id).execute()
            )
            move = move_result.data[0] if move_result.data else {}

            analysis = {
                "move_id": move_id,
                "execution_metrics": {
                    "total_tasks": total_tasks,
                    "successful_tasks": successful_tasks,
                    "failed_tasks": failed_tasks,
                    "success_rate": (
                        (successful_tasks / total_tasks) * 100 if total_tasks > 0 else 0
                    ),
                    "total_execution_time": total_time,
                    "average_task_time": (
                        total_time / total_tasks if total_tasks > 0 else 0
                    ),
                },
                "goal_achievement": self._assess_goal_achievement(
                    move, tasks_result.data
                ),
                "cost_analysis": self._analyze_execution_costs(
                    move_id, tasks_result.data
                ),
                "quality_metrics": self._calculate_quality_metrics(tasks_result.data),
            }

            return analysis

        except Exception as e:
            return {"error": str(e)}

    def _assess_goal_achievement(
        self, move: Dict[str, Any], tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess how well the move achieved its goal."""
        try:
            # Simple assessment based on task success rate
            successful_tasks = len([t for t in tasks if t["status"] == "completed"])
            total_tasks = len(tasks)

            achievement_rate = (
                (successful_tasks / total_tasks) * 100 if total_tasks > 0 else 0
            )

            return {
                "achievement_rate": achievement_rate,
                "goal_met": achievement_rate >= 80,  # 80% threshold
                "assessment": (
                    "High"
                    if achievement_rate >= 90
                    else "Medium" if achievement_rate >= 70 else "Low"
                ),
            }

        except Exception:
            return {"achievement_rate": 0, "goal_met": False, "assessment": "Unknown"}

    def _analyze_execution_costs(
        self, move_id: str, tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze execution costs."""
        try:
            # This would integrate with billing system
            # For now, return placeholder
            return {
                "estimated_cost": 0.0,
                "actual_cost": 0.0,
                "cost_variance": 0.0,
                "cost_per_task": 0.0,
            }

        except Exception:
            return {"error": "Cost analysis failed"}

    def _calculate_quality_metrics(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate quality metrics for execution."""
        try:
            # Calculate average quality scores from task results
            quality_scores = []

            for task in tasks:
                result = task.get("result", {})
                if isinstance(result, dict) and "quality_score" in result:
                    quality_scores.append(result["quality_score"])

            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)
                min_quality = min(quality_scores)
                max_quality = max(quality_scores)
            else:
                avg_quality = min_quality = max_quality = 0.0

            return {
                "average_quality_score": avg_quality,
                "min_quality_score": min_quality,
                "max_quality_score": max_quality,
                "quality_variance": max_quality - min_quality,
            }

        except Exception:
            return {"error": "Quality metrics calculation failed"}

    async def _generate_move_insights(
        self, move_id: str, analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate insights from move analysis."""
        try:
            # Use analytics agent for insights
            agent = self.agent_dispatcher.get_agent("analytics_agent")

            state = AgentState()
            state.update({"task": "generate_move_insights", "move_analysis": analysis})

            result = await agent.execute(state)

            return result.get("insights", {})

        except Exception as e:
            return {"error": str(e)}

    async def _update_knowledge_base(
        self, move_id: str, insights: Dict[str, Any], workspace_id: str
    ):
        """Update knowledge base with move insights."""
        try:
            # Store insights in memory
            content = f"""
            Move Insights for {move_id}:
            {str(insights)}
            """

            await self.memory_controller.store(
                workspace_id=workspace_id,
                memory_type="knowledge",
                content=content,
                metadata={
                    "type": "move_insights",
                    "move_id": move_id,
                    "timestamp": time.time(),
                },
            )

        except Exception as e:
            logger.error(f"Error updating knowledge base: {e}")

    async def _generate_follow_up_recommendations(
        self, move_id: str, insights: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate follow-up recommendations."""
        try:
            # Use move strategist for recommendations
            agent = self.agent_dispatcher.get_agent("move_strategist")

            state = AgentState()
            state.update(
                {
                    "task": "generate_follow_up_recommendations",
                    "move_insights": insights,
                    "move_id": move_id,
                }
            )

            result = await agent.execute(state)

            return result.get("recommendations", [])

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []

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
