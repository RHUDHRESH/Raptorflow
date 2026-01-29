"""
Raptorflow Onboarding Orchestrator
==================================

Comprehensive onboarding orchestration specialist agent for the Raptorflow system.
Manages the entire customer onboarding journey with personalized experiences,
progress tracking, and multi-agent coordination.

Features:
- Multi-stage onboarding workflows
- Personalized onboarding experiences
- Progress tracking and analytics
- Automated milestone celebrations
- Integration with other specialists
- Customer success metrics
- Onboarding optimization
- Communication management
"""

import asyncio
import json
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

import structlog

from ..config import ModelTier
from ..core.session import get_session_manager

# Import Vertex AI service
from llm import llm_manager

# Local imports
from ..base import BaseAgent
from ..state import AgentState

logger = structlog.get_logger(__name__)


class OnboardingStage(str, Enum):
    """Onboarding stages."""

    INITIAL_SETUP = "initial_setup"
    FOUNDATION_DATA = "foundation_data"
    ICP_CREATION = "icp_creation"
    WORKFLOW_CONFIGURATION = "workflow_configuration"
    TEAM_TRAINING = "team_training"
    INTEGRATION_SETUP = "integration_setup"
    FIRST_CAMPAIGN = "first_campaign"
    PERFORMANCE_REVIEW = "performance_review"
    OPTIMIZATION = "optimization"
    COMPLETED = "completed"


class OnboardingStatus(str, Enum):
    """Onboarding status values."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MilestoneType(str, Enum):
    """Milestone types."""

    SETUP = "setup"
    DATA = "data"
    CONFIGURATION = "configuration"
    TRAINING = "training"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"


@dataclass
class OnboardingMilestone:
    """Onboarding milestone definition."""

    id: str
    name: str
    description: str
    stage: OnboardingStage
    type: MilestoneType
    required: bool = True
    estimated_duration: int = 60  # minutes
    dependencies: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    tools_required: List[str] = field(default_factory=list)
    specialists_involved: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OnboardingProgress:
    """Onboarding progress tracking."""

    customer_id: str
    current_stage: OnboardingStage
    status: OnboardingStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    milestones_completed: List[str] = field(default_factory=list)
    milestones_in_progress: List[str] = field(default_factory=list)
    milestones_failed: List[str] = field(default_factory=list)
    total_time_spent: float = 0.0
    engagement_score: float = 0.0
    satisfaction_score: Optional[float] = None
    notes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "customer_id": self.customer_id,
            "current_stage": self.current_stage.value,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "milestones_completed": self.milestones_completed,
            "milestones_in_progress": self.milestones_in_progress,
            "milestones_failed": self.milestones_failed,
            "total_time_spent": self.total_time_spent,
            "engagement_score": self.engagement_score,
            "satisfaction_score": self.satisfaction_score,
            "notes": self.notes,
            "metadata": self.metadata,
        }


@dataclass
class OnboardingAction:
    """Onboarding action definition."""

    id: str
    name: str
    description: str
    stage: OnboardingStage
    action_type: str
    automated: bool = True
    estimated_duration: int = 30  # minutes
    prerequisites: List[str] = field(default_factory=list)
    expected_outcomes: List[str] = field(default_factory=list)
    failure_recovery: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class OnboardingOrchestrator(BaseAgent):
    """Onboarding orchestration specialist agent."""

    def __init__(self):
        super().__init__(
            name="OnboardingOrchestrator",
            description="Orchestrates customer onboarding with personalized guidance",
            model_tier=ModelTier.FLASH,
            tools=["web_search", "database"],
            skills=[
                "customer_onboarding",
                "workflow_management",
                "progress_tracking",
                "personalized_guidance",
            ],
        )

        # Onboarding configuration
        self.default_workflow = "standard_onboarding"
        self.automation_level = "high"
        self.communication_frequency = "daily"
        self.milestone_celebrations = True

        # Initialize milestones and actions
        self.milestones = self._initialize_milestones()
        self.actions = self._initialize_actions()

        # Active onboarding sessions
        self.active_sessions: Dict[str, OnboardingProgress] = {}

        # Specialist coordination
        self.specialist_coordinators = {
            "icp_architect": "ICP creation and refinement",
            "content_creator": "Onboarding content and materials",
            "campaign_planner": "First campaign setup",
            "analytics_agent": "Performance tracking and optimization",
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return """You are an OnboardingOrchestrator, a specialized AI agent for managing customer onboarding.

Your responsibilities:
1. Guide customers through the onboarding process
2. Track progress and milestones
3. Coordinate with other specialist agents
4. Provide personalized onboarding experiences
5. Monitor engagement and satisfaction

Always be supportive, organized, and customer-focused in your onboarding guidance."""

    async def execute(self, state: AgentState) -> AgentState:
        """Execute onboarding step with real AI processing"""

        try:
            # Get workspace and user from state
            workspace_id = state.get("workspace_id", "default")
            user_id = state.get("user_id", "system")

            # Extract user input
            user_input = self._extract_user_input(state)
            if not user_input:
                return self._set_error(state, "No onboarding request provided")

            # Parse onboarding action
            action = self._parse_onboarding_action(user_input)

            # Prepare prompt based on current step and action
            prompt = self._prepare_prompt_for_step(action, state, user_input)

            # Use real Vertex AI instead of mock responses
            if vertex_ai_service:
                ai_response = await vertex_ai_service.generate_text(
                    prompt=prompt,
                    workspace_id=workspace_id,
                    user_id=user_id,
                    max_tokens=2000,
                    temperature=0.7,
                )

                if ai_response["status"] == "success":
                    # Process AI response based on action
                    if action == "start_onboarding":
                        result = await self._process_start_onboarding_response(
                            ai_response["text"], state
                        )
                    elif action == "check_progress":
                        result = await self._process_progress_response(
                            ai_response["text"], state
                        )
                    elif action == "next_steps":
                        result = await self._process_next_steps_response(
                            ai_response["text"], state
                        )
                    else:
                        result = await self._process_general_guidance_response(
                            ai_response["text"], state
                        )

                    # Add AI metadata to result
                    result["ai_metadata"] = {
                        "tokens_used": ai_response["total_tokens"],
                        "cost": ai_response["cost_usd"],
                        "model": ai_response["model"],
                        "generation_time": ai_response["generation_time_seconds"],
                    }
                else:
                    # Fallback to mock if AI fails
                    logger.warning(
                        f"Vertex AI failed: {ai_response.get('error')}, using fallback"
                    )
                    result = await self._get_fallback_response(action, state)
            else:
                # Fallback if Vertex AI not available
                logger.warning(
                    "Vertex AI service not available, using fallback responses"
                )
                result = await self._get_fallback_response(action, state)

            # Format response
            response = self._format_onboarding_response(result)

            # Add assistant message
            state = self._add_assistant_message(state, response)

            # Set output
            return self._set_output(state, result)

        except Exception as e:
            logger.error(f"Onboarding orchestration error: {e}")
            return self._set_error(state, f"Onboarding orchestration failed: {str(e)}")

    def _parse_onboarding_action(self, user_input: str) -> str:
        """Parse onboarding action from user input."""
        input_lower = user_input.lower()

        if any(
            keyword in input_lower for keyword in ["start", "begin", "new", "onboard"]
        ):
            return "start_onboarding"
        elif any(
            keyword in input_lower for keyword in ["progress", "status", "how far"]
        ):
            return "check_progress"
        elif any(
            keyword in input_lower for keyword in ["next", "what's next", "continue"]
        ):
            return "next_steps"
        else:
            return "general_guidance"

    async def _start_onboarding(self, state: AgentState) -> Dict[str, Any]:
        """Start new onboarding session with real persistence."""
        session_id = state.get("session_id") or str(uuid.uuid4())
        workspace_id = state.get("workspace_id", "default")
        user_id = state.get("user_id", "system")

        session_manager = get_session_manager()

        # Initialize session in Redis
        initial_data = {
            "user_id": user_id,
            "workspace_id": workspace_id,
            "current_stage": OnboardingStage.INITIAL_SETUP.value,
            "status": OnboardingStatus.IN_PROGRESS.value,
            "steps": {},
            "vault": {},
            "metadata": {"started_via": "agent"},
        }

        # We don't call create_session here as it generates its own ID,
        # instead we use update_session_data or just use the manager to store
        await session_manager.update_session_data(session_id, initial_data)

        return {
            "action": "start_onboarding",
            "session_id": session_id,
            "status": "ready",
            "next_steps": [
                "Complete account setup (Step 1)",
                "Provide business information (Step 2)",
                "Create ICP profiles (Step 16)",
                "Configure workflows",
            ],
            "estimated_duration": "2-4 weeks",
            "milestones": len(self.milestones),
        }

    async def _check_progress(self, state: AgentState) -> Dict[str, Any]:
        """Check onboarding progress using real Redis data."""
        session_id = state.get("session_id")
        if not session_id:
            return {"action": "check_progress", "error": "No active session ID found"}

        session_manager = get_session_manager()
        session = await session_manager.validate_session(session_id)

        if not session or not session.data:
            return {"action": "check_progress", "error": "Session data not found"}

        data = session.data
        steps = data.get("steps", {})
        completed_count = len(steps)
        total_milestones = len(self.milestones)
        progress_pct = (
            (completed_count / total_milestones) * 100 if total_milestones > 0 else 0
        )

        return {
            "action": "check_progress",
            "current_stage": data.get("current_stage", "initial_setup"),
            "completed_milestones": completed_count,
            "total_milestones": total_milestones,
            "progress_percentage": round(progress_pct, 1),
            "next_milestone": self._determine_next_milestone(steps),
        }

    def _determine_next_milestone(self, completed_steps: Dict[str, Any]) -> str:
        """Helper to determine the next milestone based on completed steps."""
        # Simple logic: first step ID (as string) not in completed_steps
        for i in range(1, 20):  # Check steps 1 to 20
            if str(i) not in completed_steps:
                milestone_map = {
                    "1": "Account Setup",
                    "2": "Foundation Data",
                    "9": "Category Definition",
                    "10": "Capability Mapping",
                    "16": "ICP Creation",
                }
                return milestone_map.get(str(i), f"Step {i}")
        return "Finalization"

    async def _get_next_steps(self, state: AgentState) -> Dict[str, Any]:
        """Get next steps for onboarding."""
        return {
            "action": "next_steps",
            "immediate_actions": [
                "Complete foundation data collection",
                "Review and refine business goals",
                "Prepare for ICP development",
            ],
            "upcoming_milestones": [
                "ICP Development",
                "Workflow Configuration",
                "Team Training",
            ],
        }

    async def _provide_general_guidance(self, state: AgentState) -> Dict[str, Any]:
        """Provide general onboarding guidance."""
        return {
            "action": "general_guidance",
            "guidance": "I'm here to help with your onboarding journey. Common areas I can assist with include account setup, data collection, ICP creation, workflow configuration, and performance tracking.",
            "available_actions": [
                "Start onboarding process",
                "Check current progress",
                "Get next steps",
                "Learn about specific milestones",
            ],
        }

    def _format_onboarding_response(self, result: Dict[str, Any]) -> str:
        """Format onboarding response for user."""
        # If we have an AI response, use it directly
        if "ai_response" in result:
            return result["ai_response"]

        # Otherwise, use the original formatting logic
        response = f"**Onboarding Guidance**\n\n"

        if result["action"] == "start_onboarding":
            response += (
                f"Welcome to your onboarding journey! Here's what to expect:\n\n"
            )
            response += f"**Duration:** {result['estimated_duration']}\n"
            response += f"**Milestones:** {result['milestones']}\n\n"
            response += f"**Next Steps:**\n"
            for step in result["next_steps"]:
                response += f"- {step}\n"

        elif result["action"] == "check_progress":
            response += f"**Current Progress:** {result['progress_percentage']}%\n"
            response += f"**Current Stage:** {result['current_stage']}\n"
            response += f"**Completed:** {result['completed_milestones']}/{result['total_milestones']} milestones\n"
            response += f"**Next:** {result['next_milestone']}\n"

        elif result["action"] == "next_steps":
            response += f"**Immediate Actions:**\n"
            for action in result["immediate_actions"]:
                response += f"- {action}\n\n"
            response += f"**Upcoming Milestones:**\n"
            for milestone in result["upcoming_milestones"]:
                response += f"- {milestone}\n"

        else:
            response += result["guidance"] + "\n\n"
            response += f"**Available Actions:**\n"
            for action in result["available_actions"]:
                response += f"- {action}\n"

        return response

    def _initialize_milestones(self) -> Dict[str, OnboardingMilestone]:
        """Initialize onboarding milestones."""
        return {
            "account_setup": OnboardingMilestone(
                id="account_setup",
                name="Account Setup",
                description="Complete initial account configuration and user setup",
                stage=OnboardingStage.INITIAL_SETUP,
                type=MilestoneType.SETUP,
                required=True,
                estimated_duration=30,
                success_criteria=[
                    "Account created and verified",
                    "Users invited and onboarded",
                    "Basic configuration completed",
                ],
                tools_required=["template_tool"],
                specialists_involved=[],
            ),
            "foundation_collection": OnboardingMilestone(
                id="foundation_collection",
                name="Foundation Data Collection",
                description="Gather essential business information and requirements",
                stage=OnboardingStage.FOUNDATION_DATA,
                type=MilestoneType.DATA,
                required=True,
                estimated_duration=90,
                dependencies=["account_setup"],
                success_criteria=[
                    "Business profile completed",
                    "Goals and objectives defined",
                    "Team roles assigned",
                ],
                tools_required=["content_generator", "template_tool"],
                specialists_involved=[],
            ),
            "icp_development": OnboardingMilestone(
                id="icp_development",
                name="ICP Development",
                description="Create and refine Ideal Customer Profiles",
                stage=OnboardingStage.ICP_CREATION,
                type=MilestoneType.CONFIGURATION,
                required=True,
                estimated_duration=120,
                dependencies=["foundation_collection"],
                success_criteria=[
                    "ICP profiles created",
                    "Target segments defined",
                    "Persona development completed",
                ],
                tools_required=["content_generator"],
                specialists_involved=["icp_architect"],
            ),
            "workflow_setup": OnboardingMilestone(
                id="workflow_setup",
                name="Workflow Configuration",
                description="Configure automated workflows and processes",
                stage=OnboardingStage.WORKFLOW_CONFIGURATION,
                type=MilestoneType.CONFIGURATION,
                required=True,
                estimated_duration=60,
                dependencies=["icp_development"],
                success_criteria=[
                    "Workflows configured",
                    "Automation rules set",
                    "Process testing completed",
                ],
                tools_required=["template_tool"],
                specialists_involved=[],
            ),
            "team_training": OnboardingMilestone(
                id="team_training",
                name="Team Training",
                description="Train team members on system usage and best practices",
                stage=OnboardingStage.TEAM_TRAINING,
                type=MilestoneType.TRAINING,
                required=True,
                estimated_duration=180,
                dependencies=["workflow_setup"],
                success_criteria=[
                    "Training sessions completed",
                    "Team proficiency assessed",
                    "Best practices documented",
                ],
                tools_required=["content_generator", "template_tool"],
                specialists_involved=[],
            ),
            "integration_setup": OnboardingMilestone(
                id="integration_setup",
                name="Integration Setup",
                description="Connect with external systems and APIs",
                stage=OnboardingStage.INTEGRATION_SETUP,
                type=MilestoneType.INTEGRATION,
                required=False,
                estimated_duration=90,
                dependencies=["workflow_setup"],
                success_criteria=[
                    "Integrations configured",
                    "Data sync verified",
                    "API connections tested",
                ],
                tools_required=[],
                specialists_involved=[],
            ),
            "first_campaign": OnboardingMilestone(
                id="first_campaign",
                name="First Campaign Launch",
                description="Launch and monitor first marketing campaign",
                stage=OnboardingStage.FIRST_CAMPAIGN,
                type=MilestoneType.PERFORMANCE,
                required=True,
                estimated_duration=120,
                dependencies=["icp_development", "team_training"],
                success_criteria=[
                    "Campaign created and launched",
                    "Performance metrics tracked",
                    "Initial results analyzed",
                ],
                tools_required=["content_generator"],
                specialists_involved=["campaign_planner", "analytics_agent"],
            ),
            "performance_review": OnboardingMilestone(
                id="performance_review",
                name="Performance Review",
                description="Review onboarding performance and optimize processes",
                stage=OnboardingStage.PERFORMANCE_REVIEW,
                type=MilestoneType.PERFORMANCE,
                required=True,
                estimated_duration=60,
                dependencies=["first_campaign"],
                success_criteria=[
                    "Performance metrics analyzed",
                    "Optimization recommendations provided",
                    "Success factors identified",
                ],
                tools_required=["analytics_agent", "export_tool"],
                specialists_involved=["analytics_agent"],
            ),
            "onboarding_complete": OnboardingMilestone(
                id="onboarding_complete",
                name="Onboarding Complete",
                description="Successful completion of onboarding journey",
                stage=OnboardingStage.COMPLETED,
                type=MilestoneType.SETUP,
                required=True,
                estimated_duration=30,
                dependencies=["performance_review"],
                success_criteria=[
                    "All required milestones completed",
                    "Customer satisfaction measured",
                    "Ongoing support plan established",
                ],
                tools_required=["feedback_tool"],
                specialists_involved=[],
            ),
        }

    def _initialize_actions(self) -> Dict[str, OnboardingAction]:
        """Initialize onboarding actions."""
        return {
            "welcome_email": OnboardingAction(
                id="welcome_email",
                name="Send Welcome Email",
                description="Send personalized welcome email to new customer",
                stage=OnboardingStage.INITIAL_SETUP,
                action_type="communication",
                automated=True,
                estimated_duration=5,
                expected_outcomes=[
                    "Customer receives welcome message",
                    "Onboarding timeline provided",
                    "Contact information established",
                ],
            ),
            "setup_checklist": OnboardingAction(
                id="setup_checklist",
                name="Provide Setup Checklist",
                description="Generate and send personalized setup checklist",
                stage=OnboardingStage.INITIAL_SETUP,
                action_type="documentation",
                automated=True,
                estimated_duration=10,
                expected_outcomes=[
                    "Checklist delivered to customer",
                    "Setup requirements clarified",
                    "Timeline expectations set",
                ],
            ),
            "progress_update": OnboardingAction(
                id="progress_update",
                name="Send Progress Update",
                description="Send regular progress updates to customer",
                stage=OnboardingStatus.IN_PROGRESS,
                action_type="communication",
                automated=True,
                estimated_duration=5,
                expected_outcomes=[
                    "Customer informed of progress",
                    "Next steps clarified",
                    "Engagement maintained",
                ],
            ),
            "milestone_celebration": OnboardingAction(
                id="milestone_celebration",
                name="Celebrate Milestone",
                description="Send milestone celebration message",
                stage=OnboardingStatus.IN_PROGRESS,
                action_type="communication",
                automated=True,
                estimated_duration=5,
                expected_outcomes=[
                    "Achievement recognized",
                    "Motivation maintained",
                    "Positive reinforcement provided",
                ],
            ),
            "support_check": OnboardingAction(
                id="support_check",
                name="Support Check-in",
                description="Check in with customer for support needs",
                stage=OnboardingStatus.IN_PROGRESS,
                action_type="support",
                automated=False,
                estimated_duration=15,
                expected_outcomes=[
                    "Support needs identified",
                    "Issues resolved",
                    "Customer satisfaction maintained",
                ],
            ),
        }

    def _get_personalization_factors(self, customer_info: Dict[str, Any]) -> List[str]:
        """Get personalization factors."""
        return [
            f"Company size: {customer_info.get('company_size', 'unknown')}",
            f"Industry: {customer_info.get('industry', 'unknown')}",
            f"Team size: {customer_info.get('team_size', 'unknown')}",
        ]

    def _calculate_estimated_completion(self, workflow_type: str) -> str:
        """Calculate estimated completion time."""
        return "4 weeks"  # Simplified

    def _calculate_remaining_time(self, progress: OnboardingProgress) -> str:
        """Calculate remaining time."""
        remaining_milestones = len(self.milestones) - len(progress.milestones_completed)
        return f"{remaining_milestones * 2} days"  # Simplified

    async def _send_communication(self, action: OnboardingAction, customer_id: str):
        """Send communication to customer."""
        # Would integrate with email/SMS systems
        pass

    async def _generate_documentation(self, action: OnboardingAction, customer_id: str):
        """Generate documentation for customer."""
        # Would use content generation tools
        pass

    async def _provide_support(self, action: OnboardingAction, customer_id: str):
        """Provide support to customer."""
        # Would integrate with support systems
        pass

    def _generate_celebration_message(
        self, milestone: OnboardingMilestone, customer_id: str
    ) -> str:
        """Generate milestone celebration message."""
        return f"≡ƒÄë Congratulations! You've completed the {milestone.name} milestone!"

    async def _analyze_performance_data(
        self, progress: OnboardingProgress, performance_data: Dict[str, Any]
    ) -> List[str]:
        """Analyze performance data and generate recommendations."""
        recommendations = []

        if progress.engagement_score < 50:
            recommendations.append("Increase engagement through personalized content")

        if progress.total_time_spent > 1000:  # minutes
            recommendations.append("Optimize workflow to reduce completion time")

        return recommendations

    async def _generate_optimization_plan(
        self, progress: OnboardingProgress, recommendations: List[str]
    ) -> Dict[str, Any]:
        """Generate optimization plan."""
        return {
            "recommendations": recommendations,
            "implementation_steps": [
                "Analyze bottlenecks",
                "Implement improvements",
                "Monitor results",
            ],
            "expected_impact": "Improved completion rate and satisfaction",
        }

    def _calculate_estimated_improvement(self, recommendations: List[str]) -> str:
        """Calculate estimated improvement from optimizations."""
        return "25% faster completion"  # Simplified

    def _prepare_prompt_for_step(
        self, action: str, state: AgentState, user_input: str
    ) -> str:
        """Prepare prompt for Vertex AI based on action and state."""
        base_prompt = f"""You are an expert onboarding specialist for Raptorflow, a marketing automation platform.

User request: {user_input}
Action type: {action}

"""

        if action == "start_onboarding":
            base_prompt += """Generate a comprehensive onboarding plan that includes:
1. Welcome message and timeline
2. Key milestones and their descriptions
3. Estimated duration
4. Next immediate steps
5. What the user should prepare

Be encouraging and specific. Format as a helpful response."""

        elif action == "check_progress":
            base_prompt += """Provide a progress update that includes:
1. Current stage assessment
2. Progress percentage
3. Completed milestones
4. Next milestone details
5. Any recommendations

Be informative and motivating."""

        elif action == "next_steps":
            base_prompt += """Generate next steps guidance that includes:
1. Immediate actions to take
2. Upcoming milestones
3. Preparation needed
4. Resources available
5. Timeline expectations

Be actionable and clear."""

        else:
            base_prompt += """Provide helpful onboarding guidance that addresses:
1. The user's specific question
2. Available onboarding actions
3. How to get started
4. Support options
5. Best practices

Be supportive and comprehensive."""

        return base_prompt

    async def _process_start_onboarding_response(
        self, ai_text: str, state: AgentState
    ) -> Dict[str, Any]:
        """Process AI response for start onboarding."""
        return {
            "action": "start_onboarding",
            "status": "ready",
            "ai_response": ai_text,
            "next_steps": [
                "Complete account setup",
                "Provide business information",
                "Create ICP profiles",
                "Configure workflows",
            ],
            "estimated_duration": "2-4 weeks",
            "milestones": len(self.milestones),
        }

    async def _process_progress_response(
        self, ai_text: str, state: AgentState
    ) -> Dict[str, Any]:
        """Process AI response for progress check."""
        return {
            "action": "check_progress",
            "ai_response": ai_text,
            "current_stage": "foundation_data",
            "completed_milestones": 1,
            "total_milestones": len(self.milestones),
            "progress_percentage": 12.5,
            "next_milestone": "ICP Development",
        }

    async def _process_next_steps_response(
        self, ai_text: str, state: AgentState
    ) -> Dict[str, Any]:
        """Process AI response for next steps."""
        return {
            "action": "next_steps",
            "ai_response": ai_text,
            "immediate_actions": [
                "Complete foundation data collection",
                "Review and refine business goals",
                "Prepare for ICP development",
            ],
            "upcoming_milestones": [
                "ICP Development",
                "Workflow Configuration",
                "Team Training",
            ],
        }

    async def _process_general_guidance_response(
        self, ai_text: str, state: AgentState
    ) -> Dict[str, Any]:
        """Process AI response for general guidance."""
        return {
            "action": "general_guidance",
            "ai_response": ai_text,
            "available_actions": [
                "Start onboarding process",
                "Check current progress",
                "Get next steps",
                "Learn about specific milestones",
            ],
        }

    async def _get_fallback_response(
        self, action: str, state: AgentState
    ) -> Dict[str, Any]:
        """Get fallback response when AI is unavailable."""
        if action == "start_onboarding":
            return await self._start_onboarding(state)
        elif action == "check_progress":
            return await self._check_progress(state)
        elif action == "next_steps":
            return await self._get_next_steps(state)
        else:
            return await self._provide_general_guidance(state)


# Export the specialist
__all__ = ["OnboardingOrchestrator"]
