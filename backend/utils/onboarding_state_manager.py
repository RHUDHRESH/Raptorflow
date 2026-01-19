"""
Onboarding State Management Utilities
Manages 23-step onboarding workflow state and transitions
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)


class OnboardingStep(str, Enum):
    """23-step onboarding process"""
    EVIDENCE_VAULT = "evidence_vault"
    AUTO_EXTRACTION = "auto_extraction"
    CONTRADICTION_CHECK = "contradiction_check"
    REDDIT_RESEARCH = "reddit_research"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    CATEGORY_PATHS = "category_paths"
    CAPABILITY_RATING = "capability_rating"
    PERCEPTUAL_MAP = "perceptual_map"
    NEUROSCIENCE_COPY = "neuroscience_copy"
    FOCUS_SACRIFICE = "focus_sacrifice"
    ICP_GENERATION = "icp_generation"
    MESSAGING_RULES = "messaging_rules"
    SOUNDBITES_MERGE = "soundbites_merge"
    CHANNEL_STRATEGY = "channel_strategy"
    TAM_SAM_SOM = "tam_sam_som"
    BRAND_VOICE = "brand_voice"
    GUARDRAILS = "guardrails"
    ICP_COHORTS = "icp_cohorts"
    MARKET_RESEARCH = "market_research"
    DIFFERENTIATORS = "differentiators"
    PROOF_POINTS = "proof_points"
    MUSE_CALIBRATION = "muse_calibration"
    MOVE_STRATEGY = "move_strategy"
    CAMPAIGN_PLANNING = "campaign_planning"
    BLACKBOX_ACTIVATION = "blackbox_activation"
    LAUNCH = "launch"


class StepStatus(str, Enum):
    """Step completion status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class StepType(str, Enum):
    """Step execution type"""
    USER_INPUT = "user_input"
    AI_PROCESSING = "ai_processing"
    REVIEW = "review"
    VALIDATION = "validation"


@dataclass
class StepDefinition:
    """Definition of an onboarding step"""
    step: OnboardingStep
    name: str
    description: str
    type: StepType
    estimated_duration: int  # minutes
    required: bool = True
    dependencies: List[OnboardingStep] = field(default_factory=list)
    ai_agent: Optional[str] = None
    data_schema: Dict[str, Any] = field(default_factory=dict)
    success_criteria: List[str] = field(default_factory=list)


@dataclass
class StepState:
    """Current state of an onboarding step"""
    step: OnboardingStep
    status: StepStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    progress_percentage: float = 0.0
    ai_results: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "step": self.step.value,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "data": self.data,
            "errors": self.errors,
            "progress_percentage": self.progress_percentage,
            "ai_results": self.ai_results
        }


@dataclass
class OnboardingState:
    """Complete onboarding session state"""
    session_id: str
    workspace_id: str
    current_step: OnboardingStep
    steps: Dict[OnboardingStep, StepState] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_progress_percentage(self) -> float:
        """Calculate overall progress percentage"""
        if not self.steps:
            return 0.0
        
        completed_steps = sum(1 for step_state in self.steps.values() 
                              if step_state.status == StepStatus.COMPLETED)
        return (completed_steps / len(self.steps)) * 100
    
    def get_current_step_state(self) -> Optional[StepState]:
        """Get state of current step"""
        return self.steps.get(self.current_step)
    
    def can_advance_to_step(self, target_step: OnboardingStep) -> Tuple[bool, List[str]]:
        """Check if can advance to target step"""
        step_def = STEP_DEFINITIONS.get(target_step)
        if not step_def:
            return False, ["Step definition not found"]
        
        # Check dependencies
        missing_deps = []
        for dep in step_def.dependencies:
            dep_state = self.steps.get(dep)
            if not dep_state or dep_state.status != StepStatus.COMPLETED:
                missing_deps.append(dep.value)
        
        if missing_deps:
            return False, [f"Missing dependencies: {', '.join(missing_deps)}"]
        
        return True, []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "session_id": self.session_id,
            "workspace_id": self.workspace_id,
            "current_step": self.current_step.value,
            "steps": {step.value: state.to_dict() for step, state in self.steps.items()},
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
            "progress_percentage": self.get_progress_percentage()
        }


# Step definitions for the 23-step process
STEP_DEFINITIONS: Dict[OnboardingStep, StepDefinition] = {
    OnboardingStep.EVIDENCE_VAULT: StepDefinition(
        step=OnboardingStep.EVIDENCE_VAULT,
        name="Evidence Vault Collection",
        description="Collect and organize all business evidence documents",
        type=StepType.USER_INPUT,
        estimated_duration=30,
        required=True,
        data_schema={
            "files": {"type": "array", "items": {"type": "object"}},
            "urls": {"type": "array", "items": {"type": "string"}},
            "notes": {"type": "string"}
        },
        success_criteria=["At least 3 evidence items collected", "Files processed successfully"]
    ),
    
    OnboardingStep.AUTO_EXTRACTION: StepDefinition(
        step=OnboardingStep.AUTO_EXTRACTION,
        name="AI-Powered Extraction",
        description="Automatically extract facts and insights from evidence",
        type=StepType.AI_PROCESSING,
        estimated_duration=15,
        required=True,
        dependencies=[OnboardingStep.EVIDENCE_VAULT],
        ai_agent="extraction_orchestrator",
        success_criteria=["Facts extracted from all evidence", "Confidence scores calculated"]
    ),
    
    OnboardingStep.CONTRADICTION_CHECK: StepDefinition(
        step=OnboardingStep.CONTRADICTION_CHECK,
        name="Contradiction Detection",
        description="Identify inconsistencies and contradictions in extracted data",
        type=StepType.AI_PROCESSING,
        estimated_duration=10,
        required=True,
        dependencies=[OnboardingStep.AUTO_EXTRACTION],
        ai_agent="contradiction_detector",
        success_criteria=["All contradictions identified", "Resolution suggestions provided"]
    ),
    
    OnboardingStep.REDDIT_RESEARCH: StepDefinition(
        step=OnboardingStep.REDDIT_RESEARCH,
        name="Reddit Market Research",
        description="Analyze Reddit for pain points and market intelligence",
        type=StepType.AI_PROCESSING,
        estimated_duration=20,
        required=True,
        dependencies=[OnboardingStep.AUTO_EXTRACTION],
        ai_agent="reddit_researcher",
        success_criteria=["Reddit data analyzed", "Market insights generated"]
    ),
    
    OnboardingStep.COMPETITOR_ANALYSIS: StepDefinition(
        step=OnboardingStep.COMPETITOR_ANALYSIS,
        name="Competitor Analysis",
        description="Analyze competitive landscape and positioning",
        type=StepType.USER_INPUT,
        estimated_duration=25,
        required=True,
        dependencies=[OnboardingStep.AUTO_EXTRACTION],
        data_schema={
            "competitors": {"type": "array", "items": {"type": "object"}},
            "analysis_notes": {"type": "string"}
        },
        success_criteria=["At least 3 competitors identified", "Analysis completed"]
    ),
    
    OnboardingStep.CATEGORY_PATHS: StepDefinition(
        step=OnboardingStep.CATEGORY_PATHS,
        name="Category Strategy Paths",
        description="Define safe/clever/bold strategic positioning options",
        type=StepType.AI_PROCESSING,
        estimated_duration=15,
        required=True,
        dependencies=[OnboardingStep.COMPETITOR_ANALYSIS],
        ai_agent="perceptual_map_generator",
        success_criteria=["3 strategic paths defined", "Risk assessment completed"]
    ),
    
    OnboardingStep.CAPABILITY_RATING: StepDefinition(
        step=OnboardingStep.CAPABILITY_RATING,
        name="Capability Assessment",
        description="Rate capabilities (Only You/Unique/Competitive/Table Stakes)",
        type=StepType.USER_INPUT,
        estimated_duration=20,
        required=True,
        dependencies=[OnboardingStep.AUTO_EXTRACTION],
        data_schema={
            "capabilities": {"type": "array", "items": {"type": "object"}},
            "ratings": {"type": "object"}
        },
        success_criteria=["All capabilities rated", "Rationale documented"]
    ),
    
    OnboardingStep.PERCEPTUAL_MAP: StepDefinition(
        step=OnboardingStep.PERCEPTUAL_MAP,
        name="AI Perceptual Mapping",
        description="Generate 3 strategic positioning options with AI",
        type=StepType.AI_PROCESSING,
        estimated_duration=15,
        required=True,
        dependencies=[OnboardingStep.COMPETITOR_ANALYSIS, OnboardingStep.CATEGORY_PATHS],
        ai_agent="perceptual_map_generator",
        success_criteria=["Perceptual map generated", "3 positioning options created"]
    ),
    
    OnboardingStep.NEUROSCIENCE_COPY: StepDefinition(
        step=OnboardingStep.NEUROSCIENCE_COPY,
        name="Neuroscience Copywriting",
        description="Create compelling copy using 6 neuroscience principles",
        type=StepType.AI_PROCESSING,
        estimated_duration=20,
        required=True,
        dependencies=[OnboardingStep.PERCEPTUAL_MAP],
        ai_agent="neuroscience_copywriter",
        success_criteria=["Copy variants generated", "Effectiveness scores calculated"]
    ),
    
    OnboardingStep.FOCUS_SACRIFICE: StepDefinition(
        step=OnboardingStep.FOCUS_SACRIFICE,
        name="Focus & Sacrifice",
        description="Define what to focus on and what to sacrifice",
        type=StepType.USER_INPUT,
        estimated_duration=15,
        required=True,
        dependencies=[OnboardingStep.PERCEPTUAL_MAP],
        data_schema={
            "focus_areas": {"type": "array", "items": {"type": "string"}},
            "sacrifice_areas": {"type": "array", "items": {"type": "string"}},
            "rationale": {"type": "string"}
        },
        success_criteria=["Focus areas defined", "Sacrifice decisions made"]
    ),
    
    OnboardingStep.ICP_GENERATION: StepDefinition(
        step=OnboardingStep.ICP_GENERATION,
        name="Deep ICP Generation",
        description="Generate detailed Ideal Customer Profiles",
        type=StepType.AI_PROCESSING,
        estimated_duration=25,
        required=True,
        dependencies=[OnboardingStep.AUTO_EXTRACTION, OnboardingStep.REDDIT_RESEARCH],
        ai_agent="icp_architect",
        success_criteria=["ICP profiles generated", "Validation completed"]
    ),
    
    OnboardingStep.MESSAGING_RULES: StepDefinition(
        step=OnboardingStep.MESSAGING_RULES,
        name="Messaging Rules",
        description="Define core messaging principles and rules",
        type=StepType.USER_INPUT,
        estimated_duration=20,
        required=True,
        dependencies=[OnboardingStep.NEUROSCIENCE_COPY],
        data_schema={
            "rules": {"type": "array", "items": {"type": "object"}},
            "principles": {"type": "array", "items": {"type": "string"}}
        },
        success_criteria=["Messaging rules defined", "Principles established"]
    ),
    
    OnboardingStep.SOUNDBITES_MERGE: StepDefinition(
        step=OnboardingStep.SOUNDBITES_MERGE,
        name="Soundbites Integration",
        description="Merge and optimize key messaging soundbites",
        type=StepType.USER_INPUT,
        estimated_duration=15,
        required=True,
        dependencies=[OnboardingStep.MESSAGING_RULES, OnboardingStep.NEUROSCIENCE_COPY],
        data_schema={
            "soundbites": {"type": "array", "items": {"type": "object"}},
            "final_selection": {"type": "array", "items": {"type": "string"}}
        },
        success_criteria=["Soundbites merged", "Final selection made"]
    ),
    
    OnboardingStep.CHANNEL_STRATEGY: StepDefinition(
        step=OnboardingStep.CHANNEL_STRATEGY,
        name="Channel Strategy",
        description="AI-powered channel recommendations and strategy",
        type=StepType.AI_PROCESSING,
        estimated_duration=20,
        required=True,
        dependencies=[OnboardingStep.ICP_GENERATION],
        ai_agent="channel_recommender",
        success_criteria=["Channel recommendations generated", "Budget allocation created"]
    ),
    
    OnboardingStep.TAM_SAM_SOM: StepDefinition(
        step=OnboardingStep.TAM_SAM_SOM,
        name="Market Sizing Visualization",
        description="Create TAM/SAM/SOM market size analysis",
        type=StepType.AI_PROCESSING,
        estimated_duration=15,
        required=True,
        dependencies=[OnboardingStep.ICP_GENERATION],
        ai_agent="market_analyzer",
        success_criteria=["Market sizing completed", "Visualization created"]
    ),
    
    OnboardingStep.BRAND_VOICE: StepDefinition(
        step=OnboardingStep.BRAND_VOICE,
        name="Brand Voice Definition",
        description="Define brand personality and communication style",
        type=StepType.USER_INPUT,
        estimated_duration=20,
        required=True,
        dependencies=[OnboardingStep.NEUROSCIENCE_COPY],
        data_schema={
            "personality": {"type": "object"},
            "tone": {"type": "string"},
            "style_guide": {"type": "object"}
        },
        success_criteria=["Brand voice defined", "Style guide created"]
    ),
    
    OnboardingStep.GUARDRAILS: StepDefinition(
        step=OnboardingStep.GUARDRAILS,
        name="Strategic Guardrails",
        description="Set boundaries and constraints for strategy",
        type=StepType.USER_INPUT,
        estimated_duration=15,
        required=True,
        dependencies=[OnboardingStep.FOCUS_SACRIFICE],
        data_schema={
            "boundaries": {"type": "array", "items": {"type": "object"}},
            "constraints": {"type": "array", "items": {"type": "string"}}
        },
        success_criteria=["Guardrails defined", "Constraints documented"]
    ),
    
    OnboardingStep.ICP_COHORTS: StepDefinition(
        step=OnboardingStep.ICP_COHORTS,
        name="ICP Cohort Creation",
        description="Create detailed customer cohorts and segments",
        type=StepType.USER_INPUT,
        estimated_duration=25,
        required=True,
        dependencies=[OnboardingStep.ICP_GENERATION],
        data_schema={
            "cohorts": {"type": "array", "items": {"type": "object"}},
            "segments": {"type": "array", "items": {"type": "object"}}
        },
        success_criteria=["Cohorts created", "Segments defined"]
    ),
    
    OnboardingStep.MARKET_RESEARCH: StepDefinition(
        step=OnboardingStep.MARKET_RESEARCH,
        name="Market Research",
        description="Comprehensive market analysis and insights",
        type=StepType.USER_INPUT,
        estimated_duration=30,
        required=True,
        dependencies=[OnboardingStep.REDDIT_RESEARCH],
        data_schema={
            "research_findings": {"type": "object"},
            "insights": {"type": "array", "items": {"type": "string"}}
        },
        success_criteria=["Research completed", "Insights documented"]
    ),
    
    OnboardingStep.DIFFERENTIATORS: StepDefinition(
        step=OnboardingStep.DIFFERENTIATORS,
        name="Differentiator Definition",
        description="Define and validate competitive differentiators",
        type=StepType.USER_INPUT,
        estimated_duration=20,
        required=True,
        dependencies=[OnboardingStep.COMPETITOR_ANALYSIS],
        data_schema={
            "differentiators": {"type": "array", "items": {"type": "object"}},
            "validation": {"type": "object"}
        },
        success_criteria=["Differentiators defined", "Validation completed"]
    ),
    
    OnboardingStep.PROOF_POINTS: StepDefinition(
        step=OnboardingStep.PROOF_POINTS,
        name="Proof Points Collection",
        description="Gather evidence and proof for claims",
        type=StepType.USER_INPUT,
        estimated_duration=25,
        required=True,
        dependencies=[OnboardingStep.DIFFERENTIATORS],
        data_schema={
            "proof_points": {"type": "array", "items": {"type": "object"}},
            "evidence": {"type": "array", "items": {"type": "object"}}
        },
        success_criteria=["Proof points collected", "Evidence gathered"]
    ),
    
    OnboardingStep.MUSE_CALIBRATION: StepDefinition(
        step=OnboardingStep.MUSE_CALIBRATION,
        name="Muse Calibration",
        description="Calibrate AI assistant with brand knowledge",
        type=StepType.AI_PROCESSING,
        estimated_duration=15,
        required=True,
        dependencies=[OnboardingStep.BRAND_VOICE, OnboardingStep.MESSAGING_RULES],
        ai_agent="muse_calibrator",
        success_criteria=["AI calibrated", "Knowledge base updated"]
    ),
    
    OnboardingStep.MOVE_STRATEGY: StepDefinition(
        step=OnboardingStep.MOVE_STRATEGY,
        name="Move Strategy Planning",
        description="Plan strategic moves and initiatives",
        type=StepType.USER_INPUT,
        estimated_duration=30,
        required=True,
        dependencies=[OnboardingStep.CHANNEL_STRATEGY, OnboardingStep.FOCUS_SACRIFICE],
        data_schema={
            "strategic_moves": {"type": "array", "items": {"type": "object"}},
            "initiatives": {"type": "array", "items": {"type": "object"}}
        },
        success_criteria=["Strategy planned", "Initiatives defined"]
    ),
    
    OnboardingStep.CAMPAIGN_PLANNING: StepDefinition(
        step=OnboardingStep.CAMPAIGN_PLANNING,
        name="Campaign Planning",
        description="Plan initial marketing campaigns",
        type=StepType.USER_INPUT,
        estimated_duration=25,
        required=True,
        dependencies=[OnboardingStep.CHANNEL_STRATEGY, OnboardingStep.SOUNDBITES_MERGE],
        data_schema={
            "campaigns": {"type": "array", "items": {"type": "object"}},
            "timeline": {"type": "object"}
        },
        success_criteria=["Campaigns planned", "Timeline created"]
    ),
    
    OnboardingStep.BLACKBOX_ACTIVATION: StepDefinition(
        step=OnboardingStep.BLACKBOX_ACTIVATION,
        name="Blackbox Activation",
        description="Activate AI-powered growth engine",
        type=StepType.AI_PROCESSING,
        estimated_duration=20,
        required=True,
        dependencies=[OnboardingStep.MUSE_CALIBRATION, OnboardingStep.CHANNEL_STRATEGY],
        ai_agent="blackbox",
        success_criteria=["Blackbox activated", "Growth engine running"]
    ),
    
    OnboardingStep.LAUNCH: StepDefinition(
        step=OnboardingStep.LAUNCH,
        name="Launch Preparation",
        description="Final preparation for go-to-market",
        type=StepType.REVIEW,
        estimated_duration=15,
        required=True,
        dependencies=[OnboardingStep.CAMPAIGN_PLANNING, OnboardingStep.BLACKBOX_ACTIVATION],
        success_criteria=["Launch checklist completed", "Ready to go live"]
    )
}


class OnboardingStateManager:
    """Manages onboarding state transitions and validation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_sessions: Dict[str, OnboardingState] = {}
    
    def create_session(self, session_id: str, workspace_id: str) -> OnboardingState:
        """Create new onboarding session"""
        # Initialize all steps
        steps = {}
        for step in OnboardingStep:
            steps[step] = StepState(
                step=step,
                status=StepStatus.NOT_STARTED
            )
        
        state = OnboardingState(
            session_id=session_id,
            workspace_id=workspace_id,
            current_step=OnboardingStep.EVIDENCE_VAULT,
            steps=steps
        )
        
        self.active_sessions[session_id] = state
        self.logger.info(f"Created onboarding session {session_id} for workspace {workspace_id}")
        
        return state
    
    def get_session(self, session_id: str) -> Optional[OnboardingState]:
        """Get onboarding session"""
        return self.active_sessions.get(session_id)
    
    def start_step(self, session_id: str, step: OnboardingStep) -> Tuple[bool, str]:
        """Start a step"""
        session = self.get_session(session_id)
        if not session:
            return False, "Session not found"
        
        # Check if can advance to this step
        can_advance, reasons = session.can_advance_to_step(step)
        if not can_advance:
            return False, "; ".join(reasons)
        
        # Update step state
        step_state = session.steps[step]
        step_state.status = StepStatus.IN_PROGRESS
        step_state.started_at = datetime.now()
        
        # Update current step
        session.current_step = step
        session.updated_at = datetime.now()
        
        self.logger.info(f"Started step {step.value} for session {session_id}")
        return True, "Step started successfully"
    
    def complete_step(self, session_id: str, step: OnboardingStep, data: Dict[str, Any] = None, ai_results: Dict[str, Any] = None) -> Tuple[bool, str]:
        """Complete a step"""
        session = self.get_session(session_id)
        if not session:
            return False, "Session not found"
        
        step_state = session.steps[step]
        if step_state.status != StepStatus.IN_PROGRESS:
            return False, f"Step {step.value} is not in progress"
        
        # Update step state
        step_state.status = StepStatus.COMPLETED
        step_state.completed_at = datetime.now()
        step_state.progress_percentage = 100.0
        
        if data:
            step_state.data.update(data)
        
        if ai_results:
            step_state.ai_results.update(ai_results)
        
        session.updated_at = datetime.now()
        
        self.logger.info(f"Completed step {step.value} for session {session_id}")
        return True, "Step completed successfully"
    
    def fail_step(self, session_id: str, step: OnboardingStep, error: str) -> Tuple[bool, str]:
        """Mark a step as failed"""
        session = self.get_session(session_id)
        if not session:
            return False, "Session not found"
        
        step_state = session.steps[step]
        step_state.status = StepStatus.FAILED
        step_state.errors.append(error)
        session.updated_at = datetime.now()
        
        self.logger.error(f"Step {step.value} failed for session {session_id}: {error}")
        return True, "Step marked as failed"
    
    def advance_to_next_step(self, session_id: str) -> Tuple[bool, OnboardingStep, str]:
        """Advance to next available step"""
        session = self.get_session(session_id)
        if not session:
            return False, None, "Session not found"
        
        # Get current step index
        step_order = list(OnboardingStep)
        current_index = step_order.index(session.current_step)
        
        # Find next step that can be advanced to
        for i in range(current_index + 1, len(step_order)):
            next_step = step_order[i]
            can_advance, reasons = session.can_advance_to_step(next_step)
            
            if can_advance:
                success, message = self.start_step(session_id, next_step)
                if success:
                    return True, next_step, message
                else:
                    continue
        
        return False, None, "No more steps available or dependencies not met"
    
    def get_step_progress(self, session_id: str, step: OnboardingStep) -> Optional[StepState]:
        """Get progress for specific step"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        return session.steps.get(step)
    
    def update_step_progress(self, session_id: str, step: OnboardingStep, progress_percentage: float, data: Dict[str, Any] = None) -> Tuple[bool, str]:
        """Update step progress"""
        session = self.get_session(session_id)
        if not session:
            return False, "Session not found"
        
        step_state = session.steps.get(step)
        if not step_state:
            return False, "Step not found"
        
        step_state.progress_percentage = max(0.0, min(100.0, progress_percentage))
        
        if data:
            step_state.data.update(data)
        
        session.updated_at = datetime.now()
        
        return True, "Step progress updated"
    
    def validate_step_completion(self, session_id: str, step: OnboardingStep) -> Tuple[bool, List[str]]:
        """Validate if step is properly completed"""
        session = self.get_session(session_id)
        if not session:
            return False, ["Session not found"]
        
        step_state = session.steps.get(step)
        if not step_state:
            return False, ["Step not found"]
        
        step_def = STEP_DEFINITIONS.get(step)
        if not step_def:
            return False, ["Step definition not found"]
        
        errors = []
        
        # Check status
        if step_state.status != StepStatus.COMPLETED:
            errors.append("Step is not completed")
        
        # Check success criteria
        for criterion in step_def.success_criteria:
            # This would need more sophisticated validation based on criteria
            if "at least" in criterion.lower() and "evidence" in criterion.lower():
                evidence_count = len(step_state.data.get("files", [])) + len(step_state.data.get("urls", []))
                if evidence_count < 3:
                    errors.append("Not enough evidence items collected")
        
        # Check required data
        if step_def.data_schema:
            for required_field, schema in step_def.data_schema.items():
                if schema.get("required", False) and required_field not in step_state.data:
                    errors.append(f"Required field {required_field} missing")
        
        return len(errors) == 0, errors
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive session summary"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        completed_steps = [step for step, state in session.steps.items() 
                          if state.status == StepStatus.COMPLETED]
        failed_steps = [step for step, state in session.steps.items() 
                       if state.status == StepStatus.FAILED]
        in_progress_steps = [step for step, state in session.steps.items() 
                           if state.status == StepStatus.IN_PROGRESS]
        
        return {
            "session_id": session.session_id,
            "workspace_id": session.workspace_id,
            "current_step": session.current_step.value,
            "progress_percentage": session.get_progress_percentage(),
            "total_steps": len(session.steps),
            "completed_steps": len(completed_steps),
            "failed_steps": len(failed_steps),
            "in_progress_steps": len(in_progress_steps),
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "estimated_completion_time": self._estimate_completion_time(session),
            "next_actions": self._get_next_actions(session)
        }
    
    def _estimate_completion_time(self, session: OnboardingState) -> str:
        """Estimate time to complete remaining steps"""
        remaining_steps = [step for step, state in session.steps.items() 
                          if state.status != StepStatus.COMPLETED]
        
        total_minutes = sum(STEP_DEFINITIONS[step].estimated_duration for step in remaining_steps)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        if hours > 0:
            return f"~{hours}h {minutes}m"
        else:
            return f"~{minutes}m"
    
    def _get_next_actions(self, session: OnboardingState) -> List[str]:
        """Get recommended next actions"""
        actions = []
        
        current_step_def = STEP_DEFINITIONS.get(session.current_step)
        if current_step_def:
            if current_step_def.type == StepType.USER_INPUT:
                actions.append(f"Complete {current_step_def.name}")
            elif current_step_def.type == StepType.AI_PROCESSING:
                actions.append("Wait for AI processing to complete")
            elif current_step_def.type == StepType.REVIEW:
                actions.append("Review and validate results")
        
        # Check for failed steps
        failed_steps = [step for step, state in session.steps.items() 
                       if state.status == StepStatus.FAILED]
        if failed_steps:
            actions.append("Resolve failed steps")
        
        return actions


# Export utilities
__all__ = [
    "OnboardingStateManager",
    "OnboardingState", 
    "StepState",
    "OnboardingStep",
    "StepStatus",
    "StepType",
    "STEP_DEFINITIONS"
]
