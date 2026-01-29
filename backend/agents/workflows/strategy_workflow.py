"""
Strategy workflow for Raptorflow agent system.
Handles strategic planning, analysis, and decision-making workflows.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..base_workflow import (
    BaseWorkflow,
    NodeType,
    WorkflowConfig,
    WorkflowEdge,
    WorkflowNode,
    WorkflowState,
)
from ..exceptions import WorkflowError
from ..state import AgentState

logger = logging.getLogger(__name__)


class StrategyWorkflow(BaseWorkflow):
    """Workflow for strategic planning and decision-making."""

    def define_workflow(self) -> WorkflowConfig:
        """Define the strategy workflow structure."""

        # Define workflow nodes
        nodes = [
            # Entry point
            StrategyWorkflow(
                node_id="strategy_request",
                node_type=NodeType.ACTION,
                name="Strategy Request",
                description="Initialize strategic planning request",
                action_function=self._initialize_strategy_request,
                metadata={"phase": "request", "category": "initialization"},
            ),
            # Situation Analysis
            WorkflowNode(
                node_id="situation_analysis",
                node_type=NodeType.AGENT,
                name="Situation Analysis",
                description="Analyze current business situation",
                agent_name="MarketResearch",
                input_mapping={
                    "strategy_request": "strategy_params",
                    "workspace_id": "workspace_id",
                    "user_id": "user_id",
                },
                output_mapping={
                    "market_analysis": "analysis_result",
                    "situation_assessment": "assessment_data",
                    "workflow_state": "workflow_data",
                },
                metadata={"phase": "analysis", "category": "research"},
            ),
            # Competitive Analysis
            WorkflowNode(
                node_id="competitive_analysis",
                node_type=NodeType.AGENT,
                name="Competitive Analysis",
                description="Analyze competitive landscape",
                agent_name="MarketResearch",
                input_mapping={
                    "market_analysis": "analysis_result",
                    "workspace_id": "workspace_id",
                    "user_id": "user_id",
                },
                output_mapping={
                    "competitive_intelligence": "competitive_data",
                    "market_position": "position_data",
                    "workflow_state": "workflow_data",
                },
                metadata={"phase": "analysis", "category": "research"},
            ),
            # Strategic Options Generation
            WorkflowNode(
                node_id="options_generation",
                node_type=NodeType.AGENT,
                name="Strategic Options Generation",
                description="Generate strategic options",
                agent_name="BlackboxStrategist",
                input_mapping={
                    "situation_assessment": "assessment_data",
                    "competitive_intelligence": "competitive_data",
                    "market_position": "position_data",
                    "workspace_id": "workspace_id",
                    "user_id": "user_id",
                },
                output_mapping={
                    "strategic_options": "options_data",
                    "risk_assessment": "risk_data",
                    "workflow_state": "workflow_data",
                },
                metadata={"phase": "planning", "category": "strategy"},
            ),
            # Options Evaluation
            WorkflowNode(
                node_id="options_evaluation",
                node_type=NodeType.AGENT,
                name="Options Evaluation",
                description="Evaluate strategic options",
                agent_name="BlackboxStrategist",
                input_mapping={
                    "strategic_options": "options_data",
                    "risk_assessment": "risk_data",
                    "market_analysis": "analysis_result",
                    "workspace_id": "workspace_id",
                    "user_id": "user_id",
                },
                output_mapping={
                    "evaluation_results": "evaluation_data",
                    "recommended_option": "recommendation",
                    "workflow_state": "workflow_data",
                },
                metadata={"phase": "evaluation", "category": "decision"},
            ),
            # Implementation Planning
            WorkflowNode(
                node_id="implementation_planning",
                node_type=NodeType.AGENT,
                name="Implementation Planning",
                description="Plan implementation of chosen strategy",
                agent_name="MoveStrategist",
                input_mapping={
                    "recommended_option": "recommendation",
                    "evaluation_results": "evaluation_data",
                    "market_analysis": "analysis_result",
                    "workspace_id": "workspace_id",
                    "user_id": "user_id",
                },
                output_mapping={
                    "implementation_plan": "plan_data",
                    "resource_requirements": "resource_data",
                    "timeline": "timeline_data",
                    "workflow_state": "workflow_data",
                },
                metadata={"phase": "planning", "category": "implementation"},
            ),
            # Risk Assessment
            WorkflowNode(
                node_id="risk_assessment",
                node_type=NodeType.AGENT,
                name="Risk Assessment",
                description="Assess implementation risks",
                agent_name="BlackboxStrategist",
                input_mapping={
                    "implementation_plan": "plan_data",
                    "resource_requirements": "resource_data",
                    "market_analysis": "analysis_result",
                    "workspace_id": "workspace_id",
                    "user_id": "user_id",
                },
                output_mapping={
                    "risk_analysis": "risk_data",
                    "mitigation_strategies": "mitigation_data",
                    "contingency_plans": "contingency_data",
                    "workflow_state": "workflow_data",
                },
                metadata={"phase": "assessment", "category": "risk"},
            ),
            # Resource Allocation
            WorkflowNode(
                node_id="resource_allocation",
                node_type=NodeType.AGENT,
                name="Resource Allocation",
                description="Allocate resources for implementation",
                agent_name="MoveStrategist",
                input_mapping={
                    "implementation_plan": "plan_data",
                    "resource_requirements": "resource_data",
                    "risk_analysis": "risk_data",
                    "workspace_id": "workspace_id",
                    "user_id": "user_id",
                },
                output_mapping={
                    "resource_allocation": "allocation_data",
                    "budget_plan": "budget_data",
                    "team_structure": "team_data",
                    "workflow_state": "workflow_data",
                },
                metadata={"phase": "planning", "category": "resources"},
            ),
            # Success Metrics Definition
            WorkflowNode(
                node_id="success_metrics",
                node_type=NodeType.AGENT,
                name="Success Metrics Definition",
                description="Define success metrics and KPIs",
                agent_name="AnalyticsAgent",
                input_mapping={
                    "implementation_plan": "plan_data",
                    "strategic_objectives": "strategy_objectives",
                    "resource_allocation": "allocation_data",
                    "workspace_id": "workspace_id",
                    "user_id": "user_id",
                },
                output_mapping={
                    "success_metrics": "metrics_data",
                    "kpi_definitions": "kpi_data",
                    "tracking_plan": "tracking_data",
                    "workflow_state": "workflow_data",
                },
                metadata={"phase": "measurement", "category": "analytics"},
            ),
            # Strategy Finalization
            WorkflowNode(
                node_id="strategy_finalization",
                node_type=NodeType.AGENT,
                name="Strategy Finalization",
                description="Finalize strategic plan",
                agent_name="BlackboxStrategist",
                input_mapping={
                    "success_metrics": "metrics_data",
                    "implementation_plan": "plan_data",
                    "resource_allocation": "allocation_data",
                    "workflow_state": "workflow_data",
                },
                output_mapping={
                    "final_strategy": "strategy_data",
                    "executive_summary": "summary_data",
                    "action_items": "action_items",
                    "workflow_state": "workflow_data",
                },
                metadata={"phase": "finalization", "category": "completion"},
            ),
            # Workflow Completion
            WorkflowNode(
                node_id="workflow_completion",
                node_type=NodeType.ACTION,
                name="Workflow Completion",
                description="Complete strategy workflow",
                action_function=self._complete_workflow,
                metadata={"phase": "completion", "category": "finalization"},
            ),
        ]

        # Define workflow edges
        edges = [
            # Sequential flow
            WorkflowEdge("strategy_request", "situation_analysis"),
            WorkflowEdge("situation_analysis", "competitive_analysis"),
            WorkflowEdge("competitive_analysis", "options_generation"),
            WorkflowEdge("options_generation", "options_evaluation"),
            WorkflowEdge("options_evaluation", "implementation_planning"),
            WorkflowEdge("implementation_planning", "risk_assessment"),
            WorkflowEdge("risk_assessment", "resource_allocation"),
            WorkflowEdge("resource_allocation", "success_metrics"),
            WorkflowEdge("success_metrics", "strategy_finalization"),
            WorkflowEdge("strategy_finalization", "workflow_completion"),
        ]

        return WorkflowConfig(
            workflow_id="strategy_workflow",
            name="Strategic Planning Workflow",
            description="Comprehensive strategic planning and decision-making",
            version="1.0.0",
            nodes=nodes,
            edges=edges,
            entry_point="strategy_request",
            exit_points=["workflow_completion"],
            checkpoint_enabled=True,
            timeout=3600,  # 1 hour
            retry_policy="exponential",
            max_execution_time=7200,  # 2 hours
            parallel_execution=False,
            error_handling="continue",
            metadata={
                "phases": 9,
                "estimated_duration": "45-60 minutes",
                "required_agents": [
                    "MarketResearch",
                    "BlackboxStrategist",
                    "MoveStrategist",
                    "AnalyticsAgent",
                ],
                "strategy_types": [
                    "market_entry",
                    "competitive_advantage",
                    "growth_acceleration",
                    "transformation",
                    "product_launch",
                    "partnership",
                ],
            },
        )

    def _initialize_strategy_request(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize strategic planning request."""
        try:
            # Initialize workflow state
            workflow_state = {
                "workflow_id": "strategy_workflow",
                "current_phase": "request",
                "progress": 0,
                "start_time": datetime.now().isoformat(),
                "user_id": state.get("user_id"),
                "workspace_id": state.get("workspace_id"),
                "status": "in_progress",
                "strategy_type": state.get("strategy_type", "competitive_advantage"),
                "business_objectives": state.get("business_objectives", []),
                "time_horizon": state.get("time_horizon", "medium_term"),
                "risk_tolerance": state.get("risk_tolerance", "moderate"),
                "resource_constraints": state.get("resource_constraints", {}),
                "stakeholders": state.get("stakeholders", []),
                "success_criteria": state.get("success_criteria", []),
            }

            # Add to shared data
            state["workflow_state"] = workflow_state

            logger.info(
                f"Strategy workflow started for strategy type: {workflow_state.get('strategy_type')}"
            )

            return state

        except Exception as e:
            logger.error(f"Failed to initialize strategy request: {e}")
            raise WorkflowError(f"Failed to initialize strategy request: {str(e)}")

    def _complete_workflow(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Complete the strategy workflow."""
        try:
            # Update workflow state
            workflow_state = state.get("workflow_state", {})
            workflow_state.update(
                {
                    "status": "completed",
                    "end_time": datetime.now().isoformat(),
                    "progress": 100,
                    "completion_summary": self._generate_completion_summary(state),
                }
            )

            # Add completion data
            state["workflow_completion"] = {
                "completed_at": datetime.now().isoformat(),
                "total_duration": self._calculate_duration(workflow_state),
                "phases_completed": len(workflow_state.get("completed_phases", [])),
                "final_progress": workflow_state.get("progress", 0),
                "strategy_data": state.get("strategy_data", {}),
                "success_metrics": state.get("metrics_data", {}),
                "implementation_plan": state.get("plan_data", {}),
                "resource_allocation": state.get("allocation_data", {}),
            }

            logger.info(
                f"Strategy workflow completed for strategy type: {workflow_state.get('strategy_type')}"
            )

            return state

        except Exception as e:
            logger.error(f"Failed to complete strategy workflow: {e}")
            raise WorkflowError(f"Failed to complete strategy workflow: {str(e)}")

    def _generate_completion_summary(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate workflow completion summary."""
        try:
            summary = {
                "user_id": state.get("user_id"),
                "workspace_id": state.get("workspace_id"),
                "strategy_type": state.get("workflow_state", {}).get("strategy_type"),
                "business_objectives": state.get("workflow_state", {}).get(
                    "business_objectives", []
                ),
                "final_strategy": state.get("strategy_data", {}),
                "success_metrics": state.get("metrics_data", {}),
                "implementation_plan": state.get("plan_data", {}),
                "resource_allocation": state.get("allocation_data", {}),
                "next_steps": self._get_next_steps(state),
            }

            return summary

        except Exception as e:
            logger.error(f"Failed to generate completion summary: {e}")
            return {}

    def _calculate_duration(self, workflow_state: Dict[str, Any]) -> str:
        """Calculate workflow duration."""
        try:
            start_time = workflow_state.get("start_time")
            end_time = workflow_state.get("end_time")

            if start_time and end_time:
                start = datetime.fromisoformat(start_time)
                end = datetime.fromisoformat(end_time)
                duration = end - start

                minutes = duration.total_seconds() / 60

                if minutes >= 60:
                    hours = minutes // 60
                    mins = minutes % 60
                    return f"{int(hours)}h {int(mins)}m"
                else:
                    return f"{int(minutes)}m"

            return "Unknown"

        except Exception:
            return "Unknown"

    def _get_next_steps(self, state: Dict[str, Any]) -> List[str]:
        """Get recommended next steps after strategy completion."""
        try:
            next_steps = [
                "Begin implementation of strategic plan",
                "Monitor success metrics and KPIs",
                "Adjust strategy based on performance data",
                "Review and update strategic objectives",
                "Plan next strategic review cycle",
            ]

            # Customize based on strategy type and results
            strategy_type = state.get("workflow_state", {}).get("strategy_type")
            success_metrics = state.get("metrics_data", {})

            if strategy_type == "market_entry":
                next_steps.insert(0, "Prepare market entry materials")
                next_steps.insert(1, "Establish market presence")

            elif strategy_type == "competitive_advantage":
                next_steps.insert(0, "Implement competitive differentiation")
                next_steps.insert(1, "Monitor competitive responses")

            elif strategy_type == "growth_acceleration":
                next_steps.insert(0, "Scale up successful initiatives")
                next_steps.insert(1, "Expand into new markets")

            # Add performance-based recommendations
            if success_metrics and success_metrics.get("success_probability", 0) < 0.7:
                next_steps.insert(0, "Adjust strategy based on low success probability")

            return next_steps

        except Exception:
            return ["Continue monitoring strategic performance"]

    def get_workflow_progress(self) -> Dict[str, Any]:
        """Get current workflow progress."""
        if not self.state:
            return {"error": "Workflow not initialized"}

        workflow_state = self.state.shared_data.get("workflow_state", {})

        return {
            "workflow_id": self.config.workflow_id,
            "current_phase": workflow_state.get("current_phase", "request"),
            "progress": workflow_state.get("progress", 0),
            "status": workflow_state.get("status", "unknown"),
            "strategy_type": workflow_state.get("strategy_type"),
            "business_objectives": workflow_state.get("business_objectives", []),
            "time_horizon": workflow_state.get("time_horizon"),
            "start_time": workflow_state.get("start_time"),
            "estimated_remaining": self._estimate_remaining_time(workflow_state),
        }

    def _estimate_remaining_time(self, workflow_state: Dict[str, Any]) -> str:
        """Estimate remaining workflow time."""
        try:
            current_phase = workflow_state.get("current_phase", "request")
            progress = workflow_state.get("progress", 0)

            # Phase durations in minutes
            phase_durations = {
                "request": 2,
                "analysis": 8,
                "planning": 10,
                "evaluation": 5,
                "implementation": 10,
                "assessment": 5,
                "measurement": 5,
                "finalization": 5,
            }

            phases = [
                "request",
                "analysis",
                "planning",
                "evaluation",
                "implementation",
                "assessment",
                "measurement",
                "finalization",
            ]

            # Find current phase index
            if current_phase in phases:
                current_index = phases.index(current_phase)
                remaining_phases = phases[current_index + 1 :]

                remaining_minutes = sum(
                    phase_durations.get(phase, 0) for phase in remaining_phases
                )

                if remaining_minutes >= 60:
                    hours = remaining_minutes // 60
                    mins = remaining_minutes % 60
                    return f"{hours}h {mins}m"
                else:
                    return f"{remaining_minutes}m"

            return "Unknown"

        except Exception:
            return "Unknown"

    def get_phase_info(self, phase_name: str) -> Dict[str, Any]:
        """Get information about a specific workflow phase."""
        try:
            for node in self.config.nodes:
                if node.metadata.get("phase") == phase_name:
                    return {
                        "phase": phase_name,
                        "node_id": node.node_id,
                        "name": node.name,
                        "description": node.description,
                        "category": node.metadata.get("category", "unknown"),
                        "agent": node.agent_name,
                        "estimated_duration": self._get_phase_duration(phase_name),
                    }

            return {"error": f"Phase {phase_name} not found"}

        except Exception as e:
            logger.error(f"Failed to get phase info: {e}")
            return {"error": str(e)}

    def _get_phase_duration(self, phase_name: str) -> str:
        """Get estimated duration for a phase."""
        durations = {
            "request": "2 minutes",
            "analysis": "8 minutes",
            "planning": "10 minutes",
            "evaluation": "5 minutes",
            "implementation": "10 minutes",
            "assessment": "5 minutes",
            "measurement": "5 minutes",
            "finalization": "5 minutes",
        }
        return durations.get(phase_name, "Unknown")

    def get_all_phases(self) -> List[Dict[str, Any]]:
        """Get information about all workflow phases."""
        try:
            phases = []

            for node in self.config.nodes:
                if node.metadata.get("phase"):
                    phases.append(
                        {
                            "phase": node.metadata.get("phase"),
                            "node_id": node.node_id,
                            "name": node.name,
                            "description": node.description,
                            "category": node.metadata.get("category", "unknown"),
                            "agent": node.agent_name,
                            "estimated_duration": self._get_phase_duration(
                                node.metadata.get("phase")
                            ),
                        }
                    )

            return phases

        except Exception as e:
            logger.error(f"Failed to get all phases: {e}")
            return []

    def skip_current_phase(self) -> bool:
        """Skip current workflow phase."""
        try:
            if not self.state or not self.state.current_node:
                return False

            current_phase = self.state.shared_data.get("workflow_state", {}).get(
                "current_phase", "request"
            )

            # Add to skipped phases
            if "workflow_state" in self.state.shared_data:
                self.state.shared_data["workflow_state"]["skipped_phases"].append(
                    current_phase
                )

            # Move to next phase
            next_edges = [
                e for e in self.config.edges if e.from_node == self.state.current_node
            ]
            if next_edges:
                self.state.current_node = next_edges[0].to_node

            logger.info(f"Skipped workflow phase {current_phase}")
            return True

        except Exception as e:
            logger.error(f"Failed to skip current phase: {e}")
            return False

    def go_to_phase(self, phase_name: str) -> bool:
        """Go to specific workflow phase."""
        try:
            if not self.state:
                return False

            # Find node for phase
            target_node = None
            for node in self.config.nodes:
                if node.metadata.get("phase") == phase_name:
                    target_node = node.node_id
                    break

            if not target_node:
                logger.error(f"Phase {phase_name} not found")
                return False

            # Update current node
            self.state.current_node = target_node

            # Update phase in state
            if "workflow_state" in self.state.shared_data:
                self.state.shared_data["workflow_state"]["current_phase"] = phase_name

            logger.info(f"Moved to workflow phase {phase_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to go to phase {phase_name}: {e}")
            return False

    def pause_workflow(self) -> bool:
        """Pause the strategy workflow."""
        try:
            self.pause()
            logger.info("Strategy workflow paused")
            return True

        except Exception as e:
            logger.error(f"Failed to pause workflow: {e}")
            return False

    def resume_workflow(self) -> bool:
        """Resume the strategy workflow."""
        try:
            self.resume()
            logger.info("Strategy workflow resumed")
            return True

        except Exception as e:
            logger.error(f"Failed to resume workflow: {e}")
            return False

    def reset_workflow(self) -> bool:
        """Reset the strategy workflow."""
        try:
            # Reset state
            self.state = None

            # Re-initialize
            if self.agent_registry:
                self.initialize(self.agent_registry)

            logger.info("Strategy workflow reset")
            return True

        except Exception as e:
            logger.error(f"Failed to reset workflow: {e}")
            return False

    def get_strategy_result(self) -> Dict[str, Any]:
        """Get the final strategy result."""
        if not self.state:
            return {"error": "Workflow not completed"}

        if not self.is_completed():
            return {"error": "Workflow not completed"}

        return {
            "final_strategy": self.state.shared_data.get("strategy_data", {}),
            "success_metrics": self.state.shared_data.get("metrics_data", {}),
            "implementation_plan": self.state.shared_data.get("plan_data", {}),
            "resource_allocation": self.state.shared_data.get("allocation_data", {}),
            "workflow_completion": self.state.shared_data.get(
                "workflow_completion", {}
            ),
            "executive_summary": self.state.shared_data.get("summary_data", {}),
        }

    def get_success_metrics(self) -> Dict[str, Any]:
        """Get strategy success metrics."""
        if not self.state:
            return {"error": "No metrics available"}

        return self.state.shared_data.get("metrics_data", {})

    def update_strategy_request(self, updates: Dict[str, Any]) -> bool:
        """Update strategy request parameters."""
        try:
            if "workflow_state" in self.state.shared_data:
                self.state.shared_data["workflow_state"].update(updates)
                logger.info(f"Updated strategy request: {list(updates.keys())}")
                return True

        except Exception as e:
            logger.error(f"Failed to update strategy request: {e}")
            return False

    def add_strategic_objective(self, objective: str) -> bool:
        """Add strategic objective to workflow."""
        try:
            if "workflow_state" in self.state.shared_data:
                objectives = self.state.shared_data["workflow_state"].get(
                    "business_objectives", []
                )
                objectives.append(objective)
                logger.info(f"Added strategic objective: {objective}")
                return True

        except Exception as e:
            logger.error(f"Failed to add strategic objective: {e}")
            return False

    def add_stakeholder(self, stakeholder: str) -> bool:
        """Add stakeholder to workflow."""
        try:
            if "workflow_state" in self.state.shared_data:
                stakeholders = self.state.shared_data["workflow_state"].get(
                    "stakeholders", []
                )
                stakeholders.append(stakeholder)
                logger.info(f"Added stakeholder: {stakeholder}")
                return True

        except Exception as e:
            logger.error(f"Failed to add stakeholder: {e}")
            return False

    def set_success_criteria(self, criteria: List[str]) -> bool:
        """Set success criteria for the strategy."""
        try:
            if "workflow_state" in self.state.shared_data:
                self.state.shared_data["workflow_state"]["success_criteria"] = criteria
                logger.info(f"Set success criteria: {criteria}")
                return True

        except Exception as e:
            logger.error(f"Failed to set success criteria: {e}")
            return False

    def get_strategic_insights(self) -> Dict[str, Any]:
        """Get strategic insights from workflow."""
        try:
            insights = {
                "workflow_id": self.config.workflow_id,
                "analysis_results": self.state.shared_data.get("analysis_result", {}),
                "competitive_intelligence": self.state.shared_data.get(
                    "competitive_data", {}
                ),
                "strategic_options": self.state.shared_data.get("options_data", {}),
                "evaluation_results": self.state.shared_data.get("evaluation_data", {}),
                "risk_analysis": self.state.shared_data.get("risk_data", {}),
                "recommendations": self.state.shared_data.get("recommendation", {}),
            }

            return insights

        except Exception as e:
            logger.error(f"Failed to get strategic insights: {e}")
            return {}
