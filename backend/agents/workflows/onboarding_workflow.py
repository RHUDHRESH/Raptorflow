"""
Onboarding workflow for Raptorflow agent system.
Handles user onboarding with step-by-step guidance and progress tracking.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..exceptions import WorkflowError
from ..state import AgentState
from .base_workflow import (
    BaseWorkflow,
    NodeType,
    WorkflowConfig,
    WorkflowEdge,
    WorkflowNode,
    WorkflowState,
)

logger = logging.getLogger(__name__)


class OnboardingWorkflow(BaseWorkflow):
    """Workflow for user onboarding process."""

    def define_workflow(self) -> WorkflowConfig:
        """Define the onboarding workflow structure."""

        # Define workflow nodes
        nodes = [
            # Entry point
            WorkflowNode(
                node_id="start_onboarding",
                node_type=NodeType.ACTION,
                name="Start Onboarding",
                description="Initialize onboarding process",
                action_function=self._start_onboarding,
                metadata={"step": 0, "category": "initialization"},
            ),
            # Step 1: Welcome and Setup
            WorkflowNode(
                node_id="welcome_setup",
                node_type=NodeType.AGENT,
                name="Welcome and Setup",
                description="Welcome user and initial setup",
                agent_name="OnboardingOrchestrator",
                input_mapping={
                    "user_input": "user_message",
                    "workspace_id": "workspace_id",
                    "user_id": "user_id",
                },
                output_mapping={
                    "onboarding_step": "current_step",
                    "user_profile": "profile_data",
                    "progress": "progress_data",
                },
                metadata={"step": 1, "category": "welcome"},
            ),
            # Step 2: Company Information
            WorkflowNode(
                node_id="company_info",
                node_type=NodeType.AGENT,
                name="Company Information",
                description="Collect company information",
                agent_name="OnboardingOrchestrator",
                input_mapping={
                    "user_input": "user_message",
                    "workspace_id": "workspace_id",
                    "user_id": "user_id",
                },
                output_mapping={
                    "company_data": "company_info",
                    "onboarding_step": "current_step",
                    "progress": "progress_data",
                },
                metadata={"step": 2, "category": "company"},
            ),
            # Step 3: Target Audience
            WorkflowNode(
                node_id="target_audience",
                node_type=NodeType.AGENT,
                name="Target Audience",
                description="Define target audience",
                agent_name="OnboardingOrchestrator",
                input_mapping={
                    "user_input": "user_message",
                    "workspace_id": "workspace_id",
                    "user_id": "user_id",
                },
                output_mapping={
                    "audience_data": "audience_info",
                    "onboarding_step": "current_step",
                    "progress": "progress_data",
                },
                metadata={"step": 3, "category": "audience"},
            ),
            # Step 4: Goals and Objectives
            WorkflowNode(
                node_id="goals_objectives",
                node_type=NodeType.AGENT,
                name="Goals and Objectives",
                description="Define business goals",
                agent_name="OnboardingOrchestrator",
                input_mapping={
                    "user_input": "user_message",
                    "workspace_id": "workspace_id",
                    "user_id": "user_id",
                },
                output_mapping={
                    "goals_data": "goals_info",
                    "onboarding_step": "current_step",
                    "progress": "progress_data",
                },
                metadata={"step": 4, "category": "goals"},
            ),
            # Step 5: ICP Generation
            WorkflowNode(
                node_id="icp_generation",
                node_type=NodeType.AGENT,
                name="ICP Generation",
                description="Generate Ideal Customer Profiles",
                agent_name="ICPArchitect",
                input_mapping={
                    "company_data": "company_info",
                    "audience_data": "audience_info",
                    "goals_data": "goals_info",
                    "workspace_id": "workspace_id",
                    "user_id": "user_id",
                },
                output_mapping={
                    "icp_profiles": "generated_icps",
                    "onboarding_step": "current_step",
                    "progress": "progress_data",
                },
                metadata={"step": 5, "category": "icp"},
            ),
            # Step 6: Content Strategy
            WorkflowNode(
                node_id="content_strategy",
                node_type=NodeType.AGENT,
                name="Content Strategy",
                description="Define content strategy",
                agent_name="ContentCreator",
                input_mapping={
                    "icp_profiles": "generated_icps",
                    "goals_data": "goals_info",
                    "workspace_id": "workspace_id",
                    "user_id": "user_id",
                },
                output_mapping={
                    "content_strategy": "strategy_data",
                    "onboarding_step": "current_step",
                    "progress": "progress_data",
                },
                metadata={"step": 6, "category": "content"},
            ),
            # Step 7: Campaign Planning
            WorkflowNode(
                node_id="campaign_planning",
                node_type=NodeType.AGENT,
                name="Campaign Planning",
                description="Plan initial campaigns",
                agent_name="CampaignPlanner",
                input_mapping={
                    "content_strategy": "strategy_data",
                    "icp_profiles": "generated_icps",
                    "workspace_id": "workspace_id",
                    "user_id": "user_id",
                },
                output_mapping={
                    "campaign_plan": "campaign_data",
                    "onboarding_step": "current_step",
                    "progress": "progress_data",
                },
                metadata={"step": 7, "category": "campaign"},
            ),
            # Step 8: Analytics Setup
            WorkflowNode(
                node_id="analytics_setup",
                node_type=NodeType.AGENT,
                name="Analytics Setup",
                description="Configure analytics and tracking",
                agent_name="AnalyticsAgent",
                input_mapping={
                    "campaign_plan": "campaign_data",
                    "goals_data": "goals_info",
                    "workspace_id": "workspace_id",
                    "user_id": "user_id",
                },
                output_mapping={
                    "analytics_config": "analytics_data",
                    "onboarding_step": "current_step",
                    "progress": "progress_data",
                },
                metadata={"step": 8, "category": "analytics"},
            ),
            # Step 9: Review and Finalize
            WorkflowNode(
                node_id="review_finalize",
                node_type=NodeType.AGENT,
                name="Review and Finalize",
                description="Review setup and finalize",
                agent_name="OnboardingOrchestrator",
                input_mapping={
                    "all_data": "shared_data",
                    "workspace_id": "workspace_id",
                    "user_id": "user_id",
                },
                output_mapping={
                    "final_review": "review_data",
                    "onboarding_step": "current_step",
                    "progress": "progress_data",
                    "completion_status": "completion",
                },
                metadata={"step": 9, "category": "review"},
            ),
            # Completion
            WorkflowNode(
                node_id="completion",
                node_type=NodeType.ACTION,
                name="Onboarding Complete",
                description="Finalize onboarding",
                action_function=self._complete_onboarding,
                metadata={"step": 10, "category": "completion"},
            ),
        ]

        # Define workflow edges
        edges = [
            # Sequential flow
            WorkflowEdge("start_onboarding", "welcome_setup"),
            WorkflowEdge("welcome_setup", "company_info"),
            WorkflowEdge("company_info", "target_audience"),
            WorkflowEdge("target_audience", "goals_objectives"),
            WorkflowEdge("goals_objectives", "icp_generation"),
            WorkflowEdge("icp_generation", "content_strategy"),
            WorkflowEdge("content_strategy", "campaign_planning"),
            WorkflowEdge("campaign_planning", "analytics_setup"),
            WorkflowEdge("analytics_setup", "review_finalize"),
            WorkflowEdge("review_finalize", "completion"),
        ]

        return WorkflowConfig(
            workflow_id="onboarding_workflow",
            name="User Onboarding Workflow",
            description="Guided onboarding process for new users",
            version="1.0.0",
            nodes=nodes,
            edges=edges,
            entry_point="start_onboarding",
            exit_points=["completion"],
            checkpoint_enabled=True,
            timeout=3600,  # 1 hour
            retry_policy="exponential",
            max_execution_time=7200,  # 2 hours
            parallel_execution=False,
            error_handling="continue",
            metadata={
                "total_steps": 9,
                "estimated_duration": "45-60 minutes",
                "required_agents": [
                    "OnboardingOrchestrator",
                    "ICPArchitect",
                    "ContentCreator",
                    "CampaignPlanner",
                    "AnalyticsAgent",
                ],
            },
        )

    def _start_onboarding(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Start the onboarding process."""
        try:
            # Initialize onboarding state
            onboarding_state = {
                "workflow_id": "onboarding_workflow",
                "current_step": 0,
                "total_steps": 9,
                "progress": 0,
                "start_time": datetime.now().isoformat(),
                "user_id": state.get("user_id"),
                "workspace_id": state.get("workspace_id"),
                "status": "in_progress",
                "completed_steps": [],
                "skipped_steps": [],
            }

            # Add to shared data
            state["onboarding_state"] = onboarding_state

            logger.info(
                f"Onboarding started for user {state.get('user_id')} in workspace {state.get('workspace_id')}"
            )

            return state

        except Exception as e:
            logger.error(f"Failed to start onboarding: {e}")
            raise WorkflowError(f"Failed to start onboarding: {str(e)}")

    def _complete_onboarding(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Complete the onboarding process."""
        try:
            # Update onboarding state
            onboarding_state = state.get("onboarding_state", {})
            onboarding_state.update(
                {
                    "status": "completed",
                    "end_time": datetime.now().isoformat(),
                    "progress": 100,
                    "completion_summary": self._generate_completion_summary(state),
                }
            )

            # Add completion data
            state["onboarding_completion"] = {
                "completed_at": datetime.now().isoformat(),
                "total_duration": self._calculate_duration(onboarding_state),
                "steps_completed": len(onboarding_state.get("completed_steps", [])),
                "final_progress": onboarding_state.get("progress", 0),
            }

            logger.info(
                f"Onboarding completed for user {state.get('user_id')} in workspace {state.get('workspace_id')}"
            )

            return state

        except Exception as e:
            logger.error(f"Failed to complete onboarding: {e}")
            raise WorkflowError(f"Failed to complete onboarding: {str(e)}")

    def _generate_completion_summary(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate completion summary."""
        try:
            summary = {
                "user_id": state.get("user_id"),
                "workspace_id": state.get("workspace_id"),
                "completed_steps": state.get("onboarding_state", {}).get(
                    "completed_steps", []
                ),
                "generated_icps": state.get("generated_icps", {}),
                "content_strategy": state.get("strategy_data", {}),
                "campaign_plan": state.get("campaign_data", {}),
                "analytics_config": state.get("analytics_data", {}),
                "next_steps": self._get_next_steps(state),
            }

            return summary

        except Exception as e:
            logger.error(f"Failed to generate completion summary: {e}")
            return {}

    def _calculate_duration(self, onboarding_state: Dict[str, Any]) -> str:
        """Calculate onboarding duration."""
        try:
            start_time = onboarding_state.get("start_time")
            end_time = onboarding_state.get("end_time")

            if start_time and end_time:
                start = datetime.fromisoformat(start_time)
                end = datetime.fromisoformat(end_time)
                duration = end - start

                hours = duration.total_seconds() / 3600
                minutes = (duration.total_seconds() % 3600) / 60

                if hours > 0:
                    return f"{int(hours)}h {int(minutes)}m"
                else:
                    return f"{int(minutes)}m"

            return "Unknown"

        except Exception:
            return "Unknown"

    def _get_next_steps(self, state: Dict[str, Any]) -> List[str]:
        """Get recommended next steps after onboarding."""
        try:
            next_steps = [
                "Review your generated ICP profiles",
                "Start creating content based on your strategy",
                "Launch your first campaign",
                "Monitor analytics and adjust strategy",
                "Explore advanced features and tools",
            ]

            # Customize based on generated data
            if state.get("generated_icps"):
                next_steps.insert(
                    0, "Refine your ICP profiles with more specific details"
                )

            if state.get("campaign_data"):
                next_steps.insert(1, "Review and customize your campaign plan")

            return next_steps

        except Exception:
            return ["Continue exploring the platform"]

    def get_onboarding_progress(self) -> Dict[str, Any]:
        """Get current onboarding progress."""
        if not self.state:
            return {"error": "Workflow not initialized"}

        onboarding_state = self.state.shared_data.get("onboarding_state", {})

        return {
            "workflow_id": self.config.workflow_id,
            "current_step": onboarding_state.get("current_step", 0),
            "total_steps": self.config.metadata.get("total_steps", 9),
            "progress": onboarding_state.get("progress", 0),
            "status": onboarding_state.get("status", "unknown"),
            "completed_steps": onboarding_state.get("completed_steps", []),
            "skipped_steps": onboarding_state.get("skipped_steps", []),
            "start_time": onboarding_state.get("start_time"),
            "estimated_remaining": self._estimate_remaining_time(onboarding_state),
        }

    def _estimate_remaining_time(self, onboarding_state: Dict[str, Any]) -> str:
        """Estimate remaining onboarding time."""
        try:
            current_step = onboarding_state.get("current_step", 0)
            total_steps = self.config.metadata.get("total_steps", 9)
            remaining_steps = total_steps - current_step

            # Estimate 5-7 minutes per step
            minutes_per_step = 6
            remaining_minutes = remaining_steps * minutes_per_step

            if remaining_minutes >= 60:
                hours = remaining_minutes // 60
                mins = remaining_minutes % 60
                return f"{hours}h {mins}m"
            else:
                return f"{remaining_minutes}m"

        except Exception:
            return "Unknown"

    def skip_current_step(self) -> bool:
        """Skip current onboarding step."""
        try:
            if not self.state or not self.state.current_node:
                return False

            current_step = self.state.shared_data.get("onboarding_state", {}).get(
                "current_step", 0
            )

            # Add to skipped steps
            if "onboarding_state" in self.state.shared_data:
                self.state.shared_data["onboarding_state"]["skipped_steps"].append(
                    current_step
                )

            # Move to next step
            next_edges = [
                e for e in self.config.edges if e.from_node == self.state.current_node
            ]
            if next_edges:
                self.state.current_node = next_edges[0].to_node

            logger.info(f"Skipped onboarding step {current_step}")
            return True

        except Exception as e:
            logger.error(f"Failed to skip current step: {e}")
            return False

    def go_to_step(self, step_number: int) -> bool:
        """Go to specific onboarding step."""
        try:
            if not self.state:
                return False

            # Find node for step
            target_node = None
            for node in self.config.nodes:
                if node.metadata.get("step") == step_number:
                    target_node = node.node_id
                    break

            if not target_node:
                logger.error(f"Step {step_number} not found")
                return False

            # Update current node
            self.state.current_node = target_node

            # Update step in state
            if "onboarding_state" in self.state.shared_data:
                self.state.shared_data["onboarding_state"]["current_step"] = step_number

            logger.info(f"Moved to onboarding step {step_number}")
            return True

        except Exception as e:
            logger.error(f"Failed to go to step {step_number}: {e}")
            return False

    def get_step_info(self, step_number: int) -> Dict[str, Any]:
        """Get information about a specific onboarding step."""
        try:
            for node in self.config.nodes:
                if node.metadata.get("step") == step_number:
                    return {
                        "step": step_number,
                        "node_id": node.node_id,
                        "name": node.name,
                        "description": node.description,
                        "category": node.metadata.get("category", "unknown"),
                        "agent": node.agent_name,
                        "estimated_duration": "5-7 minutes",
                    }

            return {"error": f"Step {step_number} not found"}

        except Exception as e:
            logger.error(f"Failed to get step info: {e}")
            return {"error": str(e)}

    def get_all_steps(self) -> List[Dict[str, Any]]:
        """Get information about all onboarding steps."""
        try:
            steps = []

            for node in self.config.nodes:
                if node.metadata.get("step"):
                    steps.append(
                        {
                            "step": node.metadata.get("step"),
                            "node_id": node.node_id,
                            "name": node.name,
                            "description": node.description,
                            "category": node.metadata.get("category", "unknown"),
                            "agent": node.agent_name,
                            "estimated_duration": "5-7 minutes",
                        }
                    )

            # Sort by step number
            steps.sort(key=lambda x: x["step"])

            return steps

        except Exception as e:
            logger.error(f"Failed to get all steps: {e}")
            return []

    def pause_onboarding(self) -> bool:
        """Pause the onboarding process."""
        try:
            self.pause()
            logger.info("Onboarding paused")
            return True

        except Exception as e:
            logger.error(f"Failed to pause onboarding: {e}")
            return False

    def resume_onboarding(self) -> bool:
        """Resume the onboarding process."""
        try:
            self.resume()
            logger.info("Onboarding resumed")
            return True

        except Exception as e:
            logger.error(f"Failed to resume onboarding: {e}")
            return False

    def reset_onboarding(self) -> bool:
        """Reset the onboarding process."""
        try:
            # Reset state
            self.state = None

            # Re-initialize
            if self.agent_registry:
                self.initialize(self.agent_registry)

            logger.info("Onboarding reset")
            return True

        except Exception as e:
            logger.error(f"Failed to reset onboarding: {e}")
            return False
