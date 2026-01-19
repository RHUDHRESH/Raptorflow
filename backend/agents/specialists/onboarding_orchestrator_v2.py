"""
Raptorflow Onboarding Orchestrator V2
=====================================

Enhanced onboarding orchestration specialist agent for the 23-step Raptorflow system.
Integrates with all new AI agents for comprehensive onboarding experience.

Features:
- 23-step onboarding workflow management
- AI agent coordination and orchestration
- Real-time progress tracking and validation
- Evidence classification and fact extraction
- Contradiction detection and resolution
- Reddit market research integration
- Perceptual mapping and positioning
- Neuroscience-based copywriting
- Channel strategy recommendations
- State management and persistence
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import structlog

# Local imports
from ..base import BaseAgent
from backend.agents.config import ModelTier
from ..state import AgentState

# Import new AI agents
from .evidence_classifier import EvidenceClassifier
from .extraction_orchestrator import ExtractionOrchestrator
from .contradiction_detector import ContradictionDetector
from .reddit_researcher import RedditResearcher
from .perceptual_map_generator import PerceptualMapGenerator
from .neuroscience_copywriter import NeuroscienceCopywriter
from .channel_recommender import ChannelRecommender

# Import state management
from ...utils.onboarding_state_manager import (
    OnboardingStateManager,
    OnboardingStep,
    StepStatus,
    StepType
)

logger = structlog.get_logger(__name__)


class OrchestratorAction(str, Enum):
    """Orchestrator action types"""
    START_SESSION = "start_session"
    ADVANCE_STEP = "advance_step"
    PROCESS_STEP = "process_step"
    VALIDATE_STEP = "validate_step"
    GET_PROGRESS = "get_progress"
    HANDLE_ERROR = "handle_error"
    COORDINATE_AGENTS = "coordinate_agents"


@dataclass
class AgentTask:
    """Task for AI agent execution"""
    agent_name: str
    task_type: str
    input_data: Dict[str, Any]
    priority: int = 1
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: int = 300


@dataclass
class OrchestrationResult:
    """Result of orchestration operation"""
    success: bool
    action: OrchestratorAction
    session_id: str
    step: Optional[OnboardingStep] = None
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    agent_results: Dict[str, Any] = field(default_factory=dict)
    next_actions: List[str] = field(default_factory=list)
    execution_time: float = 0.0


class OnboardingOrchestratorV2(BaseAgent):
    """Enhanced onboarding orchestration specialist agent for 23-step process"""

    def __init__(self):
        super().__init__(
            name="OnboardingOrchestratorV2",
            description="Orchestrates 23-step onboarding with AI agent coordination",
            model_tier=ModelTier.FLASH,
            tools=["database", "state_management"],
            skills=[
                "onboarding_orchestration",
                "agent_coordination",
                "workflow_management",
                "progress_tracking",
                "error_handling",
                "state_persistence"
            ]
        )

        # Initialize AI agents
        self.evidence_classifier = EvidenceClassifier()
        self.extraction_orchestrator = ExtractionOrchestrator()
        self.contradiction_detector = ContradictionDetector()
        self.reddit_researcher = RedditResearcher()
        self.perceptual_map_generator = PerceptualMapGenerator()
        self.neuroscience_copywriter = NeuroscienceCopywriter()
        self.channel_recommender = ChannelRecommender()

        # Initialize state manager
        self.state_manager = OnboardingStateManager()

        # Agent mapping for step execution
        self.step_agent_mapping = {
            OnboardingStep.AUTO_EXTRACTION: self.extraction_orchestrator,
            OnboardingStep.CONTRADICTION_CHECK: self.contradiction_detector,
            OnboardingStep.REDDIT_RESEARCH: self.reddit_researcher,
            OnboardingStep.CATEGORY_PATHS: self.perceptual_map_generator,
            OnboardingStep.PERCEPTUAL_MAP: self.perceptual_map_generator,
            OnboardingStep.NEUROSCIENCE_COPY: self.neuroscience_copywriter,
            OnboardingStep.ICP_GENERATION: self.evidence_classifier,  # Could be ICP architect
            OnboardingStep.CHANNEL_STRATEGY: self.channel_recommender,
            OnboardingStep.TAM_SAM_SOM: self.channel_recommender,  # Could be market analyzer
            OnboardingStep.MUSE_CALIBRATION: self.evidence_classifier,  # Could be muse calibrator
            OnboardingStep.BLACKBOX_ACTIVATION: self.evidence_classifier  # Could be blackbox
        }

    async def update_universal_state(self, state: Any, updates: Dict[str, Any]) -> Any:
        """Helper to perform incremental sync of business_context and BCM."""
        if "business_context" not in state or state["business_context"] is None:
            state["business_context"] = {"ucid": state.get("ucid", "PENDING")}
            
        state["business_context"].update(updates)
        
        # Recalculate BCM in real-time
        try:
            from ...services.bcm_service import BCMService
            bcm = BCMService.sync_context_to_bcm(state["business_context"])
            state["bcm_state"] = bcm
        except Exception as e:
            logger.error(f"Failed to recalculate BCM: {e}")
            
        return state

    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return """You are an OnboardingOrchestratorV2, a specialized AI agent for managing the 23-step Raptorflow onboarding process.

Your responsibilities:
1. Coordinate and orchestrate the 23-step onboarding workflow
2. Manage AI agent execution and dependencies
3. Track progress and validate step completion
4. Handle errors and recovery scenarios
5. Maintain state and persistence
6. Provide intelligent guidance and next steps

You work with specialized AI agents:
- EvidenceClassifier: Document classification and categorization
- ExtractionOrchestrator: Fact extraction from evidence
- ContradictionDetector: Inconsistency detection and resolution
- RedditResearcher: Market research and intelligence
- PerceptualMapGenerator: Positioning and strategy mapping
- NeuroscienceCopywriter: Advanced copywriting
- ChannelRecommender: Channel strategy and recommendations

Always be systematic, thorough, and user-focused in your orchestration."""

    async def execute(self, state: AgentState) -> AgentState:
        """Execute orchestration with real AI processing"""
        
        try:
            # Get session and action from state
            session_id = state.get("session_id", "default")
            action_str = state.get("action", "start_session")
            action = OrchestratorAction(action_str)
            
            # Extract user input
            user_input = self._extract_user_input(state)
            
            # Execute based on action
            if action == OrchestratorAction.START_SESSION:
                result = await self._start_session(session_id, state)
            elif action == OrchestratorAction.ADVANCE_STEP:
                result = await self._advance_step(session_id, state)
            elif action == OrchestratorAction.PROCESS_STEP:
                result = await self._process_step(session_id, state)
            elif action == OrchestratorAction.VALIDATE_STEP:
                result = await self._validate_step(session_id, state)
            elif action == OrchestratorAction.GET_PROGRESS:
                result = await self._get_progress(session_id, state)
            elif action == OrchestratorAction.COORDINATE_AGENTS:
                result = await self._coordinate_agents(session_id, state)
            else:
                result = await self._handle_unknown_action(session_id, action, state)
            
            # Format response
            response = self._format_orchestration_response(result)
            
            # Add assistant message
            state = self._add_assistant_message(state, response)
            
            # Set output
            return self._set_output(state, result.data)
            
        except Exception as e:
            logger.error(f"Orchestration error: {e}")
            return self._set_error(state, f"Orchestration failed: {str(e)}")

    async def _start_session(self, session_id: str, state: AgentState) -> OrchestrationResult:
        """Start new onboarding session"""
        try:
            workspace_id = state.get("workspace_id", "default")
            
            # Create session in state manager
            onboarding_state = self.state_manager.create_session(session_id, workspace_id)
            
            # Start first step
            success, message = self.state_manager.start_step(session_id, OnboardingStep.EVIDENCE_VAULT)
            
            if not success:
                return OrchestrationResult(
                    success=False,
                    action=OrchestratorAction.START_SESSION,
                    session_id=session_id,
                    errors=[message]
                )
            
            return OrchestrationResult(
                success=True,
                action=OrchestratorAction.START_SESSION,
                session_id=session_id,
                step=OnboardingStep.EVIDENCE_VAULT,
                data={
                    "session_created": True,
                    "current_step": OnboardingStep.EVIDENCE_VAULT.value,
                    "total_steps": 23,
                    "estimated_duration": "4-6 weeks",
                    "next_actions": [
                        "Upload evidence documents",
                        "Add website URLs",
                        "Provide business context"
                    ]
                },
                next_actions=[
                    "Complete Evidence Vault collection",
                    "Wait for AI processing",
                    "Review extracted facts"
                ]
            )
            
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            return OrchestrationResult(
                success=False,
                action=OrchestratorAction.START_SESSION,
                session_id=session_id,
                errors=[str(e)]
            )

    async def _advance_step(self, session_id: str, state: AgentState) -> OrchestrationResult:
        """Advance to next step"""
        try:
            # Get current session
            session = self.state_manager.get_session(session_id)
            if not session:
                return OrchestrationResult(
                    success=False,
                    action=OrchestratorAction.ADVANCE_STEP,
                    session_id=session_id,
                    errors=["Session not found"]
                )
            
            # Complete current step if needed
            current_step_state = session.get_current_step_state()
            if current_step_state and current_step_state.status == StepStatus.IN_PROGRESS:
                success, _ = self.state_manager.complete_step(session_id, session.current_step)
                if not success:
                    return OrchestrationResult(
                        success=False,
                        action=OrchestratorAction.ADVANCE_STEP,
                        session_id=session_id,
                        errors=["Cannot complete current step"]
                    )
            
            # Advance to next step
            success, next_step, message = self.state_manager.advance_to_next_step(session_id)
            
            if not success:
                return OrchestrationResult(
                    success=False,
                    action=OrchestratorAction.ADVANCE_STEP,
                    session_id=session_id,
                    errors=[message]
                )
            
            # Check if next step requires AI processing
            step_def = self._get_step_definition(next_step)
            requires_ai = step_def.type == StepType.AI_PROCESSING if step_def else False
            
            return OrchestrationResult(
                success=True,
                action=OrchestratorAction.ADVANCE_STEP,
                session_id=session_id,
                step=next_step,
                data={
                    "advanced_to": next_step.value,
                    "requires_ai_processing": requires_ai,
                    "step_type": step_def.type.value if step_def else "unknown",
                    "estimated_duration": step_def.estimated_duration if step_def else 0
                },
                next_actions=[
                    f"Complete {next_step.value.replace('_', ' ').title()}" if not requires_ai else "Wait for AI processing"
                ]
            )
            
        except Exception as e:
            logger.error(f"Error advancing step: {e}")
            return OrchestrationResult(
                success=False,
                action=OrchestratorAction.ADVANCE_STEP,
                session_id=session_id,
                errors=[str(e)]
            )

    async def _process_step(self, session_id: str, state: AgentState) -> OrchestrationResult:
        """Process current step with AI agents"""
        try:
            session = self.state_manager.get_session(session_id)
            if not session:
                return OrchestrationResult(
                    success=False,
                    action=OrchestratorAction.PROCESS_STEP,
                    session_id=session_id,
                    errors=["Session not found"]
                )
            
            current_step = session.current_step
            step_def = self._get_step_definition(current_step)
            
            if not step_def or step_def.type != StepType.AI_PROCESSING:
                return OrchestrationResult(
                    success=False,
                    action=OrchestratorAction.PROCESS_STEP,
                    session_id=session_id,
                    step=current_step,
                    errors=["Step does not require AI processing"]
                )
            
            # Get AI agent for this step
            agent = self.step_agent_mapping.get(current_step)
            if not agent:
                return OrchestrationResult(
                    success=False,
                    action=OrchestratorAction.PROCESS_STEP,
                    session_id=session_id,
                    step=current_step,
                    errors=[f"No agent available for step {current_step.value}"]
                )
            
            # Prepare input data for agent
            input_data = self._prepare_agent_input(session_id, current_step, state)
            
            # Execute agent task
            agent_result = await self._execute_agent_task(agent, current_step, input_data)
            
            if not agent_result.get("success", False):
                return OrchestrationResult(
                    success=False,
                    action=OrchestratorAction.PROCESS_STEP,
                    session_id=session_id,
                    step=current_step,
                    errors=[agent_result.get("error", "Agent execution failed")]
                )
            
            # Update step with AI results
            success, _ = self.state_manager.complete_step(
                session_id, 
                current_step, 
                data={"processed": True},
                ai_results=agent_result
            )
            
            return OrchestrationResult(
                success=True,
                action=OrchestratorAction.PROCESS_STEP,
                session_id=session_id,
                step=current_step,
                data={
                    "processing_completed": True,
                    "agent_results": agent_result
                },
                agent_results={current_step.value: agent_result},
                next_actions=[
                    "Review AI results",
                    "Advance to next step",
                    "Make any necessary adjustments"
                ]
            )
            
        except Exception as e:
            logger.error(f"Error processing step: {e}")
            return OrchestrationResult(
                success=False,
                action=OrchestratorAction.PROCESS_STEP,
                session_id=session_id,
                errors=[str(e)]
            )

    async def _validate_step(self, session_id: str, state: AgentState) -> OrchestrationResult:
        """Validate step completion"""
        try:
            session = self.state_manager.get_session(session_id)
            if not session:
                return OrchestrationResult(
                    success=False,
                    action=OrchestratorAction.VALIDATE_STEP,
                    session_id=session_id,
                    errors=["Session not found"]
                )
            
            current_step = session.current_step
            is_valid, errors = self.state_manager.validate_step_completion(session_id, current_step)
            
            return OrchestrationResult(
                success=is_valid,
                action=OrchestratorAction.VALIDATE_STEP,
                session_id=session_id,
                step=current_step,
                data={
                    "validation_passed": is_valid,
                    "validation_errors": errors
                },
                errors=errors if not is_valid else [],
                next_actions=[
                    "Fix validation errors" if not is_valid else "Advance to next step"
                ]
            )
            
        except Exception as e:
            logger.error(f"Error validating step: {e}")
            return OrchestrationResult(
                success=False,
                action=OrchestratorAction.VALIDATE_STEP,
                session_id=session_id,
                errors=[str(e)]
            )

    async def _get_progress(self, session_id: str, state: AgentState) -> OrchestrationResult:
        """Get comprehensive progress"""
        try:
            summary = self.state_manager.get_session_summary(session_id)
            
            if not summary:
                return OrchestrationResult(
                    success=False,
                    action=OrchestratorAction.GET_PROGRESS,
                    session_id=session_id,
                    errors=["Session not found"]
                )
            
            return OrchestrationResult(
                success=True,
                action=OrchestratorAction.GET_PROGRESS,
                session_id=session_id,
                data=summary,
                next_actions=summary.get("next_actions", [])
            )
            
        except Exception as e:
            logger.error(f"Error getting progress: {e}")
            return OrchestrationResult(
                success=False,
                action=OrchestratorAction.GET_PROGRESS,
                session_id=session_id,
                errors=[str(e)]
            )

    async def _coordinate_agents(self, session_id: str, state: AgentState) -> OrchestrationResult:
        """Coordinate multiple AI agents"""
        try:
            # Get pending agent tasks
            tasks = self._get_pending_agent_tasks(session_id)
            
            if not tasks:
                return OrchestrationResult(
                    success=True,
                    action=OrchestratorAction.COORDINATE_AGENTS,
                    session_id=session_id,
                    data={"no_pending_tasks": True},
                    next_actions=["Continue with current step"]
                )
            
            # Execute tasks in dependency order
            results = {}
            for task in tasks:
                agent = self.step_agent_mapping.get(task.step)
                if agent:
                    result = await self._execute_agent_task(agent, task.step, task.input_data)
                    results[task.step.value] = result
            
            return OrchestrationResult(
                success=True,
                action=OrchestratorAction.COORDINATE_AGENTS,
                session_id=session_id,
                data={"tasks_completed": len(tasks)},
                agent_results=results,
                next_actions=["Review coordinated results"]
            )
            
        except Exception as e:
            logger.error(f"Error coordinating agents: {e}")
            return OrchestrationResult(
                success=False,
                action=OrchestratorAction.COORDINATE_AGENTS,
                session_id=session_id,
                errors=[str(e)]
            )

    async def _handle_unknown_action(self, session_id: str, action: OrchestratorAction, state: AgentState) -> OrchestrationResult:
        """Handle unknown or unsupported actions"""
        return OrchestrationResult(
            success=False,
            action=action,
            session_id=session_id,
            errors=[f"Unknown action: {action.value}"],
            next_actions=[
                "Start new session",
                "Check progress",
                "Process current step"
            ]
        )

    def _get_step_definition(self, step: OnboardingStep):
        """Get step definition"""
        from ...utils.onboarding_state_manager import STEP_DEFINITIONS
        return STEP_DEFINITIONS.get(step)

    def _prepare_agent_input(self, session_id: str, step: OnboardingStep, state: AgentState) -> Dict[str, Any]:
        """Prepare input data for AI agent"""
        session = self.state_manager.get_session(session_id)
        if not session:
            return {}
        
        # Base input data
        input_data = {
            "session_id": session_id,
            "step": step.value,
            "workspace_id": session.workspace_id
        }
        
        # Add step-specific data
        if step == OnboardingStep.AUTO_EXTRACTION:
            # Get evidence from previous step
            evidence_data = session.steps.get(OnboardingStep.EVIDENCE_VAULT, {}).data
            input_data["evidence"] = evidence_data.get("files", []) + evidence_data.get("urls", [])
        
        elif step == OnboardingStep.CONTRADICTION_CHECK:
            # Get extracted facts
            facts_data = session.steps.get(OnboardingStep.AUTO_EXTRACTION, {}).ai_results
            input_data["facts"] = facts_data.get("facts", [])
        
        elif step == OnboardingStep.REDDIT_RESEARCH:
            # Get company info from evidence
            evidence_data = session.steps.get(OnboardingStep.EVIDENCE_VAULT, {}).data
            input_data["company_info"] = self._extract_company_info(evidence_data)
        
        elif step == OnboardingStep.PERCEPTUAL_MAP:
            # Get competitors and company info
            competitors_data = session.steps.get(OnboardingStep.COMPETITOR_ANALYSIS, {}).data
            input_data["company_info"] = self._extract_company_info(session.steps.get(OnboardingStep.EVIDENCE_VAULT, {}).data)
            input_data["competitors"] = competitors_data.get("competitors", [])
        
        elif step == OnboardingStep.NEUROSCIENCE_COPY:
            # Get product info from positioning
            positioning_data = session.steps.get(OnboardingStep.PERCEPTUAL_MAP, {}).ai_results
            input_data["product_info"] = self._extract_product_info(positioning_data)
        
        elif step == OnboardingStep.CHANNEL_STRATEGY:
            # Get company info and competitors
            input_data["company_info"] = self._extract_company_info(session.steps.get(OnboardingStep.EVIDENCE_VAULT, {}).data)
            competitors_data = session.steps.get(OnboardingStep.COMPETITOR_ANALYSIS, {}).data
            input_data["competitors"] = competitors_data.get("competitors", [])
        
        return input_data

    async def _execute_agent_task(self, agent, step: OnboardingStep, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task with specific AI agent"""
        try:
            if step == OnboardingStep.AUTO_EXTRACTION:
                result = await agent.extract_facts_from_evidence(input_data.get("evidence", []))
                return {"success": True, "result": result}
            
            elif step == OnboardingStep.CONTRADICTION_CHECK:
                result = await agent.detect_contradictions(input_data.get("facts", []))
                return {"success": True, "result": result}
            
            elif step == OnboardingStep.REDDIT_RESEARCH:
                result = await agent.analyze_reddit_market(input_data.get("company_info", {}))
                return {"success": True, "result": result}
            
            elif step == OnboardingStep.PERCEPTUAL_MAP:
                result = await agent.generate_perceptual_map(
                    input_data.get("company_info", {}),
                    input_data.get("competitors", [])
                )
                return {"success": True, "result": result}
            
            elif step == OnboardingStep.NEUROSCIENCE_COPY:
                result = await agent.generate_copywriting_campaign(input_data.get("product_info", {}))
                return {"success": True, "result": result}
            
            elif step == OnboardingStep.CHANNEL_STRATEGY:
                result = await agent.analyze_channels(
                    input_data.get("company_info", {}),
                    input_data.get("competitors", [])
                )
                return {"success": True, "result": result}
            
            else:
                return {"success": False, "error": f"Unknown step: {step.value}"}
            
        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            return {"success": False, "error": str(e)}

    def _extract_company_info(self, evidence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract company information from evidence data"""
        # Mock extraction - would use real NLP in production
        return {
            "name": "RaptorFlow Dynamics",
            "industry": "Marketing Technology",
            "business_model": "B2B SaaS",
            "target_market": "SaaS companies",
            "product_description": "AI-powered marketing automation platform"
        }

    def _extract_product_info(self, positioning_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract product information from positioning data"""
        # Mock extraction - would use real data in production
        return {
            "name": "RaptorFlow",
            "key_benefit": "Automated marketing intelligence",
            "target_emotion": "confidence",
            "target_audience": "B2B SaaS founders"
        }

    def _get_pending_agent_tasks(self, session_id: str) -> List[AgentTask]:
        """Get pending agent tasks for session"""
        # Mock implementation - would check actual pending tasks
        return []

    def _format_orchestration_response(self, result: OrchestrationResult) -> str:
        """Format orchestration response for user"""
        if not result.success:
            return f"**Orchestration Error**\n\nErrors:\n" + "\n".join(f"- {error}" for error in result.errors)
        
        response = f"**{result.action.value.replace('_', ' ').title()}**\n\n"
        
        if result.step:
            response += f"Current Step: {result.step.value.replace('_', ' ').title()}\n\n"
        
        if result.data:
            for key, value in result.data.items():
                if key != "agent_results":
                    response += f"**{key.replace('_', ' ').title()}:** {value}\n"
        
        if result.next_actions:
            response += f"\n**Next Actions:**\n"
            for action in result.next_actions:
                response += f"- {action}\n"
        
        return response

    def _extract_user_input(self, state: AgentState) -> str:
        """Extract user input from state"""
        messages = state.get("messages", [])
        if messages:
            return messages[-1].get("content", "")
        return ""

    def _add_assistant_message(self, state: AgentState, content: str) -> AgentState:
        """Add assistant message to state"""
        messages = state.get("messages", [])
        messages.append({
            "role": "assistant",
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        state["messages"] = messages
        return state

    def _set_output(self, state: AgentState, data: Dict[str, Any]) -> AgentState:
        """Set output in state"""
        state["output"] = data
        return state

    def _set_error(self, state: AgentState, error: str) -> AgentState:
        """Set error in state"""
        state["error"] = error
        return state


# Export the specialist
__all__ = ["OnboardingOrchestratorV2"]
