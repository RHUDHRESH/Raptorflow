"""
Content workflow for Raptorflow agent system.
Handles content creation, optimization, and distribution workflows.
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


class ContentWorkflow(BaseWorkflow):
    """Workflow for content creation and management."""

    def define_workflow(self) -> WorkflowConfig:
        """Define the content workflow structure."""

        # Define workflow nodes
        nodes = [
            # Entry point
            WorkflowNode(
                node_id="content_request",
                node_type=NodeType.ACTION,
                name="Content Request",
                description="Initialize content creation request",
                action_function=self._initialize_content_request,
                metadata={"phase": "request", "category": "initialization"},
            ),
            # Content Analysis
            WorkflowNode(
                node_id="content_analysis",
                node_type=NodeType.AGENT,
                name="Content Analysis",
                description="Analyze content requirements and context",
                agent_name="ContentCreator",
                input_mapping={
                    "content_request": "content_params",
                    "workspace_id": "workspace_id",
                    "user_id": "user_id",
                },
                output_mapping={
                    "content_analysis": "analysis_result",
                    "content_plan": "content_plan",
                    "workflow_state": "workflow_data",
                },
                metadata={"phase": "analysis", "category": "planning"},
            ),
            # Content Generation
            WorkflowNode(
                node_id="content_generation",
                node_type=NodeType.AGENT,
                name="Content Generation",
                description="Generate content based on analysis",
                agent_name="ContentCreator",
                input_mapping={
                    "content_plan": "content_plan",
                    "content_analysis": "analysis_result",
                    "workspace_id": "workspace_id",
                    "user_id": "user_id",
                },
                output_mapping={
                    "generated_content": "content_data",
                    "content_metadata": "content_info",
                    "workflow_state": "workflow_data",
                },
                metadata={"phase": "generation", "category": "creation"},
            ),
            # Content Optimization
            WorkflowNode(
                node_id="content_optimization",
                node_type=NodeType.AGENT,
                name="Content Optimization",
                description="Optimize content for performance",
                agent_name="ContentCreator",
                input_mapping={
                    "generated_content": "content_data",
                    "content_metadata": "content_info",
                    "workspace_id": "workspace_id",
                    "user_id": "user_id",
                },
                output_mapping={
                    "optimized_content": "optimized_data",
                    "optimization_metrics": "optimization_info",
                    "workflow_state": "workflow_data",
                },
                metadata={"phase": "optimization", "category": "enhancement"},
            ),
            # Quality Check
            WorkflowNode(
                node_id="quality_check",
                node_type=NodeType.AGENT,
                name="Quality Check",
                description="Check content quality and compliance",
                agent_name="ContentCreator",
                input_mapping={
                    "optimized_content": "optimized_data",
                    "content_metadata": "content_info",
                    "workspace_id": "workspace_id",
                    "user_id": "user_id",
                },
                output_mapping={
                    "quality_assessment": "quality_result",
                    "compliance_check": "compliance_data",
                    "workflow_state": "workflow_data",
                },
                metadata={"phase": "validation", "category": "quality"},
            ),
            # Template Application
            WorkflowNode(
                node_id="template_application",
                node_type=NodeType.AGENT,
                name="Template Application",
                description="Apply content template if specified",
                agent_name="TemplateTool",
                input_mapping={
                    "optimized_content": "optimized_data",
                    "template_id": "template_id",
                    "template_variables": "template_vars",
                    "workspace_id": "workspace_id",
                },
                output_mapping={
                    "templated_content": "templated_data",
                    "template_info": "template_result",
                    "workflow_state": "workflow_data",
                },
                metadata={"phase": "formatting", "category": "templating"},
            ),
            # Content Review
            WorkflowNode(
                node_id="content_review",
                node_type=NodeType.AGENT,
                name="Content Review",
                description="Review and finalize content",
                agent_name="ContentCreator",
                input_mapping={
                    "templated_content": "templated_data",
                    "quality_assessment": "quality_result",
                    "workflow_state": "workflow_data",
                },
                output_mapping={
                    "final_content": "final_data",
                    "review_summary": "review_info",
                    "workflow_state": "workflow_data",
                },
                metadata={"phase": "review", "category": "validation"},
            ),
            # Distribution Planning
            WorkflowNode(
                node_id="distribution_planning",
                node_type=NodeType.AGENT,
                name="Distribution Planning",
                description="Plan content distribution",
                agent_name="ContentCreator",
                input_mapping={
                    "final_content": "final_data",
                    "content_metadata": "content_info",
                    "distribution_channels": "channels",
                    "workspace_id": "workspace_id",
                    "user_id": "user_id",
                },
                output_mapping={
                    "distribution_plan": "distribution_data",
                    "schedule_info": "schedule_data",
                    "workflow_state": "workflow_data",
                },
                metadata={"phase": "distribution", "category": "publishing"},
            ),
            # Content Publishing
            WorkflowNode(
                node_id="content_publishing",
                node_type=NodeType.AGENT,
                name="Content Publishing",
                description="Publish content to channels",
                agent_name="ContentCreator",
                input_mapping={
                    "final_content": "final_data",
                    "distribution_plan": "distribution_data",
                    "schedule_info": "schedule_data",
                    "workspace_id": "workspace_id",
                    "user_id": "user_id",
                },
                output_mapping={
                    "published_content": "published_data",
                    "publishing_results": "publishing_info",
                    "workflow_state": "workflow_data",
                },
                metadata={"phase": "publishing", "category": "distribution"},
            ),
            # Performance Tracking
            WorkflowNode(
                node_id="performance_tracking",
                node_type=NodeType.AGENT,
                name="Performance Tracking",
                description="Track content performance metrics",
                agent_name="AnalyticsAgent",
                input_mapping={
                    "published_content": "published_data",
                    "publishing_results": "publishing_info",
                    "workspace_id": "workspace_id",
                    "user_id": "user_id",
                },
                output_mapping={
                    "performance_metrics": "metrics_data",
                    "engagement_analytics": "analytics_data",
                    "workflow_state": "workflow_data",
                },
                metadata={"phase": "tracking", "category": "analytics"},
            ),
            # Workflow Completion
            WorkflowNode(
                node_id="workflow_completion",
                node_type=NodeType.ACTION,
                name="Workflow Completion",
                description="Complete content workflow",
                action_function=self._complete_workflow,
                metadata={"phase": "completion", "category": "finalization"},
            ),
        ]

        # Define workflow edges
        edges = [
            # Sequential flow
            WorkflowEdge("content_request", "content_analysis"),
            WorkflowEdge("content_analysis", "content_generation"),
            WorkflowEdge("content_generation", "content_optimization"),
            WorkflowEdge("content_optimization", "quality_check"),
            WorkflowEdge("quality_check", "template_application"),
            WorkflowEdge("template_application", "content_review"),
            WorkflowEdge("content_review", "distribution_planning"),
            WorkflowEdge("distribution_planning", "content_publishing"),
            WorkflowEdge("content_publishing", "performance_tracking"),
            WorkflowEdge("performance_tracking", "workflow_completion"),
        ]

        return WorkflowConfig(
            workflow_id="content_workflow",
            name="Content Creation Workflow",
            description="End-to-end content creation and distribution",
            version="1.0.0",
            nodes=nodes,
            edges=edges,
            entry_point="content_request",
            exit_points=["workflow_completion"],
            checkpoint_enabled=True,
            timeout=1800,  # 30 minutes
            retry_policy="exponential",
            max_execution_time=3600,  # 1 hour
            parallel_execution=False,
            error_handling="continue",
            metadata={
                "phases": 10,
                "estimated_duration": "20-30 minutes",
                "required_agents": ["ContentCreator", "TemplateTool", "AnalyticsAgent"],
                "content_types": [
                    "blog",
                    "social",
                    "email",
                    "ad_copy",
                    "newsletter",
                    "product_description",
                    "landing_page",
                ],
            },
        )

    def _initialize_content_request(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize content creation request."""
        try:
            # Initialize workflow state
            workflow_state = {
                "workflow_id": "content_workflow",
                "current_phase": "request",
                "progress": 0,
                "start_time": datetime.now().isoformat(),
                "user_id": state.get("user_id"),
                "workspace_id": state.get("workspace_id"),
                "status": "in_progress",
                "content_type": state.get("content_type", "blog"),
                "content_topic": state.get("content_topic", ""),
                "target_audience": state.get("target_audience", "general"),
                "content_tone": state.get("content_tone", "professional"),
                "content_length": state.get("content_length", "medium"),
                "distribution_channels": state.get("distribution_channels", []),
                "template_id": state.get("template_id"),
                "template_variables": state.get("template_variables", {}),
                "optimization_level": state.get("optimization_level", "standard"),
            }

            # Add to shared data
            state["workflow_state"] = workflow_state

            logger.info(
                f"Content workflow started for content type: {workflow_state.get('content_type')}"
            )

            return state

        except Exception as e:
            logger.error(f"Failed to initialize content request: {e}")
            raise WorkflowError(f"Failed to initialize content request: {str(e)}")

    def _complete_workflow(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Complete the content workflow."""
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
                "content_id": state.get("final_content", {}).get("content_id"),
                "performance_metrics": state.get("metrics_data", {}),
            }

            logger.info(
                f"Content workflow completed for content type: {workflow_state.get('content_type')}"
            )

            return state

        except Exception as e:
            logger.error(f"Failed to complete content workflow: {e}")
            raise WorkflowError(f"Failed to complete content workflow: {str(e)}")

    def _generate_completion_summary(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate workflow completion summary."""
        try:
            summary = {
                "user_id": state.get("user_id"),
                "workspace_id": state.get("workspace_id"),
                "content_type": state.get("workflow_state", {}).get("content_type"),
                "content_topic": state.get("workflow_state", {}).get("content_topic"),
                "final_content": state.get("final_data", {}),
                "performance_metrics": state.get("metrics_data", {}),
                "distribution_results": state.get("publishing_info", {}),
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
        """Get recommended next steps after content creation."""
        try:
            next_steps = [
                "Monitor content performance metrics",
                "Create similar content based on performance",
                "Update content strategy based on analytics",
                "Expand distribution to additional channels",
                "A/B test different content variations",
            ]

            # Customize based on content type and performance
            content_type = state.get("workflow_state", {}).get("content_type")
            metrics = state.get("metrics_data", {})

            if content_type == "blog":
                next_steps.insert(0, "Create internal links to related blog posts")
                next_steps.insert(1, "Optimize for SEO based on performance data")

            elif content_type == "social":
                next_steps.insert(0, "Monitor engagement and adjust posting schedule")
                next_steps.insert(1, "Create social media content calendar")

            elif content_type == "email":
                next_steps.insert(0, "Analyze email open and click rates")
                next_steps.insert(1, "Segment audience for targeted campaigns")

            # Add performance-based recommendations
            if metrics and metrics.get("engagement_score", 0) < 0.5:
                next_steps.insert(0, "Improve content based on low engagement metrics")

            return next_steps

        except Exception:
            return ["Continue monitoring content performance"]

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
            "content_type": workflow_state.get("content_type"),
            "content_topic": workflow_state.get("content_topic"),
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
                "request": 1,
                "analysis": 2,
                "generation": 5,
                "optimization": 3,
                "validation": 2,
                "templating": 1,
                "review": 2,
                "distribution": 2,
                "publishing": 3,
                "tracking": 2,
            }

            phases = [
                "request",
                "analysis",
                "generation",
                "optimization",
                "validation",
                "templating",
                "review",
                "distribution",
                "publishing",
                "tracking",
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
            "request": "1 minute",
            "analysis": "2 minutes",
            "generation": "5 minutes",
            "optimization": "3 minutes",
            "validation": "2 minutes",
            "templating": "1 minute",
            "review": "2 minutes",
            "distribution": "2 minutes",
            "publishing": "3 minutes",
            "tracking": "2 minutes",
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
        """Pause the content workflow."""
        try:
            self.pause()
            logger.info("Content workflow paused")
            return True

        except Exception as e:
            logger.error(f"Failed to pause workflow: {e}")
            return False

    def resume_workflow(self) -> bool:
        """Resume the content workflow."""
        try:
            self.resume()
            logger.info("Content workflow resumed")
            return True

        except Exception as e:
            logger.error(f"Failed to resume workflow: {e}")
            return False

    def reset_workflow(self) -> bool:
        """Reset the content workflow."""
        try:
            # Reset state
            self.state = None

            # Re-initialize
            if self.agent_registry:
                self.initialize(self.agent_registry)

            logger.info("Content workflow reset")
            return True

        except Exception as e:
            logger.error(f"Failed to reset workflow: {e}")
            return False

    def get_content_result(self) -> Dict[str, Any]:
        """Get the final content result."""
        if not self.state:
            return {"error": "Workflow not completed"}

        if not self.is_completed():
            return {"error": "Workflow not completed"}

        return {
            "final_content": self.state.shared_data.get("final_data", {}),
            "content_metadata": self.state.shared_data.get("content_info", {}),
            "performance_metrics": self.state.shared_data.get("metrics_data", {}),
            "distribution_results": self.state.shared_data.get("publishing_info", {}),
            "workflow_completion": self.state.shared_data.get(
                "workflow_completion", {}
            ),
        }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get content performance metrics."""
        if not self.state:
            return {"error": "No metrics available"}

        return self.state.shared_data.get("metrics_data", {})

    def update_content_request(self, updates: Dict[str, Any]) -> bool:
        """Update content request parameters."""
        try:
            if "workflow_state" in self.state.shared_data:
                self.state.shared_data["workflow_state"].update(updates)
                logger.info(f"Updated content request: {list(updates.keys())}")
                return True

        except Exception as e:
            logger.error(f"Failed to update content request: {e}")
            return False
