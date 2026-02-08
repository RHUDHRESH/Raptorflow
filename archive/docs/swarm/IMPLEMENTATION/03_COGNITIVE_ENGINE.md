# COGNITIVE ENGINE

> Planning, Reflection, Reasoning, Human-in-the-Loop

---

## 1. COGNITIVE ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COGNITIVE ENGINE                                    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     PERCEPTION MODULE                               │   │
│  │                                                                     │   │
│  │  Input → Entity Extraction → Intent Detection → Context Assembly   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     PLANNING MODULE                                 │   │
│  │                                                                     │   │
│  │  Task Decomposition → Dependency Graph → Resource Estimation       │   │
│  │                           │                                         │   │
│  │                           ▼                                         │   │
│  │  Execution Plan → Skill Selection → Tool Requirements              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     EXECUTION MODULE                                │   │
│  │                                                                     │   │
│  │  Agent Selection → Skill Execution → Tool Calling → Output Gen     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     REFLECTION MODULE                               │   │
│  │                                                                     │   │
│  │  Output Validation → Quality Scoring → Self-Correction Loop        │   │
│  │                           │                                         │   │
│  │                           ▼                                         │   │
│  │  [If failed] → Replanning → Alternative Strategy → Retry           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     APPROVAL MODULE                                 │   │
│  │                                                                     │   │
│  │  Risk Assessment → Approval Gates → Human Review → Feedback Loop   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. PERCEPTION MODULE

**Purpose**: Understand and contextualize user input.

```python
# backend/cognitive/perception.py
from pydantic import BaseModel, Field
from langchain_google_vertexai import ChatVertexAI
from typing import Any

class PerceivedInput(BaseModel):
    """Structured perception of user input."""

    # Raw input
    raw_input: str

    # Extracted entities
    entities: list[dict] = Field(
        description="Named entities: people, companies, products, dates, amounts"
    )

    # Intent classification
    primary_intent: str = Field(description="Main intent")
    secondary_intents: list[str] = Field(default=[], description="Additional intents")

    # Sentiment and tone
    sentiment: str = Field(description="positive, negative, neutral, urgent")
    formality: str = Field(description="formal, casual, urgent")

    # Context signals
    references_previous: bool = Field(
        description="Does this reference previous conversation?"
    )
    requires_clarification: bool = Field(
        description="Is clarification needed before proceeding?"
    )
    clarification_questions: list[str] = Field(
        default=[],
        description="Questions to ask if clarification needed"
    )

    # Constraints detected
    time_constraints: str | None = Field(description="Any time/deadline mentioned")
    budget_constraints: str | None = Field(description="Any budget mentioned")
    quality_requirements: list[str] = Field(
        default=[],
        description="Quality/style requirements"
    )

PERCEPTION_PROMPT = """You are the Perception Module for Raptorflow.

Analyze the user input and extract structured information:

1. ENTITIES: Extract all named entities (companies, people, products, dates, amounts)
2. INTENT: What does the user want to accomplish?
3. SENTIMENT: Is this urgent? Positive/negative?
4. CONTEXT: Does this reference previous conversation?
5. CONSTRAINTS: Any time, budget, or quality requirements?
6. CLARIFICATION: Do we need more info before proceeding?

User Context:
- Workspace: {workspace_name}
- Onboarding: {onboarding_status}
- Last Agent: {last_agent}

Recent Conversation:
{recent_messages}

User Input: {input}

Analyze comprehensively."""

class PerceptionModule:
    def __init__(self):
        self.llm = ChatVertexAI(
            model_name="gemini-2.0-flash-lite",
            temperature=0.0,
            max_tokens=800
        )

    async def perceive(
        self,
        raw_input: str,
        workspace_context: dict,
        recent_messages: list[dict]
    ) -> PerceivedInput:
        """Perceive and structure user input."""

        messages_text = "\n".join([
            f"{m['role']}: {m['content']}"
            for m in recent_messages[-5:]
        ])

        chain = PERCEPTION_PROMPT | self.llm.with_structured_output(PerceivedInput)

        return await chain.ainvoke({
            "input": raw_input,
            "workspace_name": workspace_context.get("name", ""),
            "onboarding_status": workspace_context.get("onboarding_completed", False),
            "last_agent": workspace_context.get("last_agent", "none"),
            "recent_messages": messages_text
        })
```

---

## 3. PLANNING MODULE

**Purpose**: Decompose complex tasks, create execution plans.

```python
# backend/cognitive/planning.py
from pydantic import BaseModel, Field
from typing import Literal
from enum import Enum

class TaskPriority(Enum):
    CRITICAL = "critical"  # Must complete
    HIGH = "high"          # Should complete
    MEDIUM = "medium"      # Nice to have
    LOW = "low"            # Optional

class PlanStep(BaseModel):
    """Single step in execution plan."""
    step_id: str
    description: str
    agent: str
    skill: str

    # Dependencies
    depends_on: list[str] = Field(default=[], description="Step IDs this depends on")

    # Resources
    estimated_tokens: int
    estimated_cost: float
    estimated_time_ms: int

    # Requirements
    requires_tools: list[str] = Field(default=[])
    requires_context: list[str] = Field(default=[])  # foundation, icps, etc.

    # Risk
    can_fail_gracefully: bool = Field(
        description="Can we continue if this step fails?"
    )
    fallback_strategy: str | None = None

    priority: TaskPriority = TaskPriority.HIGH

class ExecutionPlan(BaseModel):
    """Complete execution plan."""
    plan_id: str
    query: str

    # Steps
    steps: list[PlanStep]

    # Execution strategy
    strategy: Literal["sequential", "parallel", "hybrid"]

    # Resource totals
    total_estimated_tokens: int
    total_estimated_cost: float
    total_estimated_time_ms: int

    # Risk assessment
    risk_level: Literal["low", "medium", "high"]
    requires_approval: bool
    approval_reason: str | None = None

    # Alternatives
    alternative_plans: list[str] = Field(
        default=[],
        description="Brief descriptions of alternative approaches"
    )

PLANNING_PROMPT = """You are the Planning Module for Raptorflow.

Create an execution plan for the user's request.

AVAILABLE AGENTS:
{available_agents}

AVAILABLE SKILLS:
{available_skills}

AVAILABLE TOOLS:
{available_tools}

USER REQUEST:
Intent: {intent}
Entities: {entities}
Constraints: {constraints}

USER CONTEXT:
Foundation: {has_foundation}
ICPs: {num_icps}
Budget Remaining: ${budget:.4f}

PLANNING RULES:
1. Break complex tasks into atomic steps
2. Identify dependencies between steps
3. Estimate resource usage conservatively
4. Mark steps that need human approval
5. Provide fallback strategies for risky steps
6. Consider budget constraints

Create an optimal execution plan."""

class PlanningModule:
    def __init__(self):
        self.llm = ChatVertexAI(
            model_name="gemini-2.0-flash",
            temperature=0.2,
            max_tokens=2000
        )

        self.agents = [
            "moves_generator", "campaign_planner", "muse_engine",
            "blackbox_engine", "daily_wins_engine", "market_researcher",
            "icp_architect", "vault_processor", "truth_extractor"
        ]

        self.skills = [
            "move_planning", "campaign_strategy", "copywriting",
            "risk_assessment", "trend_analysis", "market_research",
            "icp_generation", "fact_extraction", "positioning"
        ]

        self.tools = [
            "web_search", "scrape_website", "scrape_reviews",
            "process_pdf", "ocr_extract", "get_foundation",
            "get_icps", "calculate_gst"
        ]

    async def create_plan(
        self,
        perceived_input: PerceivedInput,
        user_context: dict
    ) -> ExecutionPlan:
        """Create execution plan."""

        chain = PLANNING_PROMPT | self.llm.with_structured_output(ExecutionPlan)

        return await chain.ainvoke({
            "available_agents": ", ".join(self.agents),
            "available_skills": ", ".join(self.skills),
            "available_tools": ", ".join(self.tools),
            "intent": perceived_input.primary_intent,
            "entities": perceived_input.entities,
            "constraints": {
                "time": perceived_input.time_constraints,
                "budget": perceived_input.budget_constraints,
                "quality": perceived_input.quality_requirements
            },
            "has_foundation": user_context.get("has_foundation", False),
            "num_icps": user_context.get("num_icps", 0),
            "budget": user_context.get("budget_remaining", 10.0)
        })

    async def replan_on_failure(
        self,
        original_plan: ExecutionPlan,
        failed_step: PlanStep,
        error: str
    ) -> ExecutionPlan:
        """Create new plan after step failure."""

        replan_prompt = f"""
The following step failed:
Step: {failed_step.description}
Error: {error}

Original plan: {original_plan.model_dump_json()}

Create an alternative plan that:
1. Works around the failed step
2. Uses the fallback strategy if available
3. Maintains the original goal
4. May use different agents/skills
"""

        result = await self.llm.ainvoke(replan_prompt)
        # Parse and return new plan
        return ExecutionPlan(**result)
```

---

## 4. REFLECTION MODULE

**Purpose**: Validate outputs, self-correct, improve quality.

```python
# backend/cognitive/reflection.py
from pydantic import BaseModel, Field
from typing import Any

class QualityScore(BaseModel):
    """Quality assessment of agent output."""

    # Scores (0-100)
    relevance: int = Field(description="How relevant to the request")
    completeness: int = Field(description="How complete is the response")
    accuracy: int = Field(description="How accurate/factual")
    coherence: int = Field(description="How well-structured and clear")
    actionability: int = Field(description="How actionable is this")

    # Overall
    overall_score: int = Field(description="Weighted average")

    # Issues found
    issues: list[str] = Field(default=[], description="Specific issues found")

    # Recommendations
    improvements: list[str] = Field(
        default=[],
        description="How to improve the output"
    )

    # Verdict
    passes_quality: bool = Field(description="Does this meet quality threshold?")
    needs_revision: bool = Field(description="Should this be revised?")
    revision_instructions: str | None = None

REFLECTION_PROMPT = """You are the Reflection Module for Raptorflow.

Evaluate this agent output for quality.

ORIGINAL REQUEST:
{request}

AGENT OUTPUT:
{output}

USER CONTEXT:
- Brand Voice: {brand_voice}
- Target ICP: {target_icp}

EVALUATION CRITERIA:
1. RELEVANCE (0-100): Does this address the request?
2. COMPLETENESS (0-100): Is anything missing?
3. ACCURACY (0-100): Are there factual errors?
4. COHERENCE (0-100): Is it well-structured and clear?
5. ACTIONABILITY (0-100): Can the user act on this?

QUALITY THRESHOLD: 70 overall

Be critical but fair. Identify specific issues and provide actionable improvements."""

class ReflectionModule:
    def __init__(self):
        self.llm = ChatVertexAI(
            model_name="gemini-2.0-flash",
            temperature=0.1,
            max_tokens=1000
        )
        self.quality_threshold = 70
        self.max_revisions = 3

    async def evaluate(
        self,
        request: str,
        output: Any,
        user_context: dict
    ) -> QualityScore:
        """Evaluate output quality."""

        chain = REFLECTION_PROMPT | self.llm.with_structured_output(QualityScore)

        return await chain.ainvoke({
            "request": request,
            "output": str(output),
            "brand_voice": user_context.get("brand_voice", "professional"),
            "target_icp": user_context.get("target_icp", "general")
        })

    async def self_correct(
        self,
        original_output: Any,
        quality_score: QualityScore,
        agent_name: str,
        revision_count: int = 0
    ) -> tuple[Any, bool]:
        """Attempt to self-correct based on reflection."""

        if revision_count >= self.max_revisions:
            return original_output, False

        if quality_score.passes_quality:
            return original_output, True

        correction_prompt = f"""
You generated this output: {original_output}

It has these issues:
{chr(10).join(quality_score.issues)}

Improve it following these instructions:
{quality_score.revision_instructions}

Improvements needed:
{chr(10).join(quality_score.improvements)}

Generate an improved version:
"""

        improved = await self.llm.ainvoke(correction_prompt)

        # Re-evaluate
        new_score = await self.evaluate(
            request="",  # Original request should be passed
            output=improved.content,
            user_context={}
        )

        if new_score.passes_quality:
            return improved.content, True

        # Recursive correction
        return await self.self_correct(
            improved.content,
            new_score,
            agent_name,
            revision_count + 1
        )


class CriticAgent:
    """Adversarial critic for high-stakes outputs."""

    def __init__(self):
        self.llm = ChatVertexAI(
            model_name="gemini-2.0-flash",
            temperature=0.3,
            max_tokens=800
        )

    async def critique(
        self,
        output: Any,
        output_type: str,
        user_context: dict
    ) -> dict:
        """Provide adversarial critique."""

        critique_prompt = f"""
You are an adversarial critic. Your job is to find problems.

OUTPUT TYPE: {output_type}
OUTPUT: {output}

USER BUSINESS: {user_context.get('business_summary', '')}
USER ICP: {user_context.get('icp_summary', '')}

Find problems with:
1. FACTUAL ACCURACY: Any claims that can't be verified?
2. BRAND ALIGNMENT: Does this match their voice/values?
3. ICP RELEVANCE: Would their target customer respond to this?
4. ETHICAL ISSUES: Any problematic content?
5. LEGAL RISKS: Any claims that could cause issues?
6. EFFECTIVENESS: Will this actually work?

Be harsh but constructive. Give specific, actionable feedback.
"""

        result = await self.llm.ainvoke(critique_prompt)
        return {"critique": result.content}
```

---

## 5. HUMAN-IN-THE-LOOP MODULE

**Purpose**: Handle approval gates, feedback collection, preference learning.

```python
# backend/cognitive/human_loop.py
from pydantic import BaseModel, Field
from typing import Literal, Any
from enum import Enum
from datetime import datetime

class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    EXPIRED = "expired"

class ApprovalGate(BaseModel):
    """Human approval checkpoint."""
    gate_id: str
    workspace_id: str
    session_id: str

    # What needs approval
    gate_type: Literal["content", "strategy", "payment", "deletion", "external_action"]
    description: str

    # The output awaiting approval
    pending_output: dict

    # Why approval needed
    risk_level: Literal["low", "medium", "high", "critical"]
    risk_reasons: list[str]

    # Approval options
    can_modify: bool = True
    can_partial_approve: bool = False

    # Status
    status: ApprovalStatus = ApprovalStatus.PENDING

    # Timestamps
    created_at: datetime
    expires_at: datetime | None = None
    resolved_at: datetime | None = None

    # Resolution
    approved_by: str | None = None
    modifications: dict | None = None
    rejection_reason: str | None = None

class FeedbackRecord(BaseModel):
    """User feedback on agent output."""
    feedback_id: str
    workspace_id: str

    # What was the output
    output_type: str
    output_id: str

    # Feedback
    rating: int = Field(ge=1, le=5, description="1-5 star rating")
    feedback_type: Literal["helpful", "not_helpful", "wrong", "good", "needs_improvement"]

    # Specific feedback
    what_was_good: list[str] = Field(default=[])
    what_needs_improvement: list[str] = Field(default=[])
    free_text: str | None = None

    # Preference signals
    tone_preference: str | None = None
    length_preference: Literal["shorter", "just_right", "longer"] | None = None
    detail_preference: Literal["less_detail", "just_right", "more_detail"] | None = None

    timestamp: datetime

class HumanLoopModule:
    def __init__(self, supabase, redis):
        self.supabase = supabase
        self.redis = redis

    # ═══════════════════════════════════════════════════════════════════
    # APPROVAL GATES
    # ═══════════════════════════════════════════════════════════════════

    async def create_approval_gate(
        self,
        workspace_id: str,
        session_id: str,
        gate_type: str,
        pending_output: dict,
        risk_level: str,
        risk_reasons: list[str]
    ) -> ApprovalGate:
        """Create an approval gate."""
        import uuid
        from datetime import timedelta

        gate = ApprovalGate(
            gate_id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            session_id=session_id,
            gate_type=gate_type,
            description=f"Approval required for {gate_type}",
            pending_output=pending_output,
            risk_level=risk_level,
            risk_reasons=risk_reasons,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=24)
        )

        # Store in database
        self.supabase.table("approval_gates").insert(
            gate.model_dump(mode="json")
        ).execute()

        # Also cache in Redis for fast access
        self.redis.setex(
            f"approval:{gate.gate_id}",
            86400,  # 24 hours
            gate.model_dump_json()
        )

        return gate

    async def resolve_approval(
        self,
        gate_id: str,
        status: ApprovalStatus,
        user_id: str,
        modifications: dict | None = None,
        rejection_reason: str | None = None
    ) -> ApprovalGate:
        """Resolve an approval gate."""

        # Get gate
        result = self.supabase.table("approval_gates").select("*").eq(
            "gate_id", gate_id
        ).single().execute()

        if not result.data:
            raise ValueError(f"Gate {gate_id} not found")

        gate = ApprovalGate(**result.data)

        # Update
        gate.status = status
        gate.resolved_at = datetime.now()
        gate.approved_by = user_id
        gate.modifications = modifications
        gate.rejection_reason = rejection_reason

        # Save
        self.supabase.table("approval_gates").update(
            gate.model_dump(mode="json")
        ).eq("gate_id", gate_id).execute()

        # Clear from Redis
        self.redis.delete(f"approval:{gate_id}")

        return gate

    def should_require_approval(
        self,
        output_type: str,
        risk_signals: dict
    ) -> tuple[bool, str, list[str]]:
        """Determine if output needs approval."""

        APPROVAL_RULES = {
            # Content that goes external
            "email": {
                "condition": lambda s: s.get("is_cold_outreach", False),
                "level": "medium",
                "reasons": ["Cold outreach can affect brand reputation"]
            },
            "ad_copy": {
                "condition": lambda s: True,  # Always approve ads
                "level": "high",
                "reasons": ["Ad spend involved", "Public visibility"]
            },

            # Strategies
            "blackbox_strategy": {
                "condition": lambda s: s.get("risk_level", 0) >= 7,
                "level": "high",
                "reasons": ["High-risk strategy", "Significant business impact"]
            },

            # Payments
            "payment": {
                "condition": lambda s: True,
                "level": "critical",
                "reasons": ["Financial transaction"]
            },

            # Data operations
            "deletion": {
                "condition": lambda s: True,
                "level": "high",
                "reasons": ["Irreversible action"]
            },

            # External actions
            "api_call": {
                "condition": lambda s: s.get("is_write_operation", False),
                "level": "medium",
                "reasons": ["External system modification"]
            }
        }

        rule = APPROVAL_RULES.get(output_type)
        if not rule:
            return False, "low", []

        if rule["condition"](risk_signals):
            return True, rule["level"], rule["reasons"]

        return False, "low", []

    # ═══════════════════════════════════════════════════════════════════
    # FEEDBACK COLLECTION
    # ═══════════════════════════════════════════════════════════════════

    async def collect_feedback(
        self,
        workspace_id: str,
        output_type: str,
        output_id: str,
        rating: int,
        feedback_type: str,
        details: dict
    ) -> FeedbackRecord:
        """Collect user feedback."""
        import uuid

        feedback = FeedbackRecord(
            feedback_id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            output_type=output_type,
            output_id=output_id,
            rating=rating,
            feedback_type=feedback_type,
            what_was_good=details.get("good", []),
            what_needs_improvement=details.get("improve", []),
            free_text=details.get("text"),
            tone_preference=details.get("tone"),
            length_preference=details.get("length"),
            detail_preference=details.get("detail"),
            timestamp=datetime.now()
        )

        # Store
        self.supabase.table("feedback_records").insert(
            feedback.model_dump(mode="json")
        ).execute()

        # Update preference model
        await self._update_preferences(workspace_id, feedback)

        return feedback

    async def _update_preferences(
        self,
        workspace_id: str,
        feedback: FeedbackRecord
    ):
        """Update user preference model based on feedback."""

        # Get current preferences
        pref_key = f"preferences:{workspace_id}"
        current = self.redis.hgetall(pref_key) or {}

        # Update based on feedback
        if feedback.tone_preference:
            # Increment tone preference counter
            tone_key = f"tone:{feedback.tone_preference}"
            current[tone_key] = int(current.get(tone_key, 0)) + 1

        if feedback.length_preference:
            length_key = f"length:{feedback.length_preference}"
            current[length_key] = int(current.get(length_key, 0)) + 1

        # Update output type preferences
        type_key = f"type:{feedback.output_type}:rating"
        ratings = current.get(type_key, "")
        ratings += f",{feedback.rating}"
        current[type_key] = ratings[-50:]  # Keep last ~10 ratings

        # Save
        self.redis.hset(pref_key, mapping=current)

    async def get_preference_context(
        self,
        workspace_id: str
    ) -> dict:
        """Get learned preferences for context injection."""

        pref_key = f"preferences:{workspace_id}"
        prefs = self.redis.hgetall(pref_key) or {}

        # Analyze preferences
        tone_prefs = {}
        length_prefs = {}

        for key, value in prefs.items():
            if key.startswith("tone:"):
                tone = key.replace("tone:", "")
                tone_prefs[tone] = int(value)
            elif key.startswith("length:"):
                length = key.replace("length:", "")
                length_prefs[length] = int(value)

        # Determine dominant preferences
        preferred_tone = max(tone_prefs, key=tone_prefs.get) if tone_prefs else "professional"
        preferred_length = max(length_prefs, key=length_prefs.get) if length_prefs else "just_right"

        return {
            "preferred_tone": preferred_tone,
            "preferred_length": preferred_length,
            "tone_confidence": max(tone_prefs.values()) if tone_prefs else 0,
            "feedback_count": sum(tone_prefs.values()) + sum(length_prefs.values())
        }
```

---

## 6. PROTOCOL STANDARDIZATION

**Purpose**: Standardize communication between agents.

```python
# backend/cognitive/protocol.py
from pydantic import BaseModel, Field
from typing import Any, Literal
from datetime import datetime
from enum import Enum

class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    STATUS = "status"
    HANDOFF = "handoff"

class AgentMessage(BaseModel):
    """Standardized agent-to-agent message."""

    # Envelope
    message_id: str
    correlation_id: str  # Links related messages
    timestamp: datetime

    # Routing
    source_agent: str
    target_agent: str
    message_type: MessageType

    # Payload
    action: str
    parameters: dict[str, Any]

    # Context passed between agents
    context: dict[str, Any] = Field(default={})

    # Metadata
    priority: int = Field(default=5, ge=1, le=10)
    ttl_seconds: int = Field(default=300)
    requires_response: bool = True

class AgentResponse(BaseModel):
    """Standardized agent response."""

    # Envelope
    message_id: str
    correlation_id: str
    timestamp: datetime

    # Source
    source_agent: str

    # Result
    success: bool
    result: Any | None = None
    error: str | None = None

    # Metrics
    tokens_used: int = 0
    cost: float = 0.0
    latency_ms: int = 0

    # Next steps
    next_action: str | None = None
    handoff_to: str | None = None
    context_updates: dict[str, Any] = Field(default={})

class ToolCall(BaseModel):
    """Standardized tool call."""

    tool_name: str
    parameters: dict[str, Any]

    # Execution control
    timeout_seconds: int = 30
    retry_count: int = 0
    max_retries: int = 3

    # Result
    success: bool | None = None
    result: Any | None = None
    error: str | None = None

    # Metrics
    latency_ms: int | None = None

class ExecutionTrace(BaseModel):
    """Complete execution trace for debugging/audit."""

    trace_id: str
    workspace_id: str
    session_id: str

    # Request
    original_request: str
    perceived_input: dict
    execution_plan: dict

    # Execution
    messages: list[AgentMessage | AgentResponse]
    tool_calls: list[ToolCall]

    # Reflection
    quality_scores: list[dict]
    corrections_made: int

    # Approval
    approval_gates: list[dict]

    # Final output
    final_output: Any

    # Metrics
    total_tokens: int
    total_cost: float
    total_latency_ms: int

    # Timestamps
    started_at: datetime
    completed_at: datetime
```

---

## 7. COGNITIVE ENGINE INTEGRATION

```python
# backend/cognitive/engine.py
from .perception import PerceptionModule, PerceivedInput
from .planning import PlanningModule, ExecutionPlan
from .reflection import ReflectionModule, CriticAgent
from .human_loop import HumanLoopModule
from .protocol import AgentMessage, AgentResponse, ExecutionTrace

class CognitiveEngine:
    """Unified cognitive engine coordinating all modules."""

    def __init__(self, supabase, redis):
        self.perception = PerceptionModule()
        self.planning = PlanningModule()
        self.reflection = ReflectionModule()
        self.critic = CriticAgent()
        self.human_loop = HumanLoopModule(supabase, redis)

        self.supabase = supabase
        self.redis = redis

    async def process(
        self,
        raw_input: str,
        workspace_id: str,
        session_id: str,
        user_context: dict
    ) -> ExecutionTrace:
        """Full cognitive processing pipeline."""
        import uuid
        from datetime import datetime

        trace = ExecutionTrace(
            trace_id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            session_id=session_id,
            original_request=raw_input,
            perceived_input={},
            execution_plan={},
            messages=[],
            tool_calls=[],
            quality_scores=[],
            corrections_made=0,
            approval_gates=[],
            final_output=None,
            total_tokens=0,
            total_cost=0.0,
            total_latency_ms=0,
            started_at=datetime.now(),
            completed_at=datetime.now()
        )

        # 1. PERCEPTION
        perceived = await self.perception.perceive(
            raw_input=raw_input,
            workspace_context=user_context,
            recent_messages=user_context.get("recent_messages", [])
        )
        trace.perceived_input = perceived.model_dump()

        # Check if clarification needed
        if perceived.requires_clarification:
            trace.final_output = {
                "type": "clarification_needed",
                "questions": perceived.clarification_questions
            }
            return trace

        # 2. PLANNING
        plan = await self.planning.create_plan(perceived, user_context)
        trace.execution_plan = plan.model_dump()

        # Check if approval needed before execution
        if plan.requires_approval:
            gate = await self.human_loop.create_approval_gate(
                workspace_id=workspace_id,
                session_id=session_id,
                gate_type="strategy",
                pending_output=plan.model_dump(),
                risk_level=plan.risk_level,
                risk_reasons=[plan.approval_reason] if plan.approval_reason else []
            )
            trace.approval_gates.append(gate.model_dump(mode="json"))
            trace.final_output = {
                "type": "approval_required",
                "gate_id": gate.gate_id,
                "plan": plan.model_dump()
            }
            return trace

        # 3. EXECUTION
        output = await self._execute_plan(plan, user_context, trace)

        # 4. REFLECTION
        quality = await self.reflection.evaluate(
            request=raw_input,
            output=output,
            user_context=user_context
        )
        trace.quality_scores.append(quality.model_dump())

        # Self-correct if needed
        if quality.needs_revision:
            output, success = await self.reflection.self_correct(
                original_output=output,
                quality_score=quality,
                agent_name="",
                revision_count=0
            )
            trace.corrections_made += 1

        # 5. CRITIC (for high-stakes outputs)
        if plan.risk_level in ["high", "critical"]:
            critique = await self.critic.critique(
                output=output,
                output_type=perceived.primary_intent,
                user_context=user_context
            )
            # Could add another correction round based on critique

        # 6. FINAL APPROVAL CHECK
        needs_approval, risk_level, reasons = self.human_loop.should_require_approval(
            output_type=perceived.primary_intent,
            risk_signals={"risk_level": plan.risk_level}
        )

        if needs_approval:
            gate = await self.human_loop.create_approval_gate(
                workspace_id=workspace_id,
                session_id=session_id,
                gate_type="content",
                pending_output={"output": output},
                risk_level=risk_level,
                risk_reasons=reasons
            )
            trace.approval_gates.append(gate.model_dump(mode="json"))
            trace.final_output = {
                "type": "approval_required",
                "gate_id": gate.gate_id,
                "output": output
            }
        else:
            trace.final_output = output

        trace.completed_at = datetime.now()

        # Save trace
        await self._save_trace(trace)

        return trace

    async def _execute_plan(
        self,
        plan: ExecutionPlan,
        user_context: dict,
        trace: ExecutionTrace
    ) -> Any:
        """Execute the plan steps."""

        results = {}

        for step in plan.steps:
            # Check dependencies
            for dep_id in step.depends_on:
                if dep_id not in results:
                    raise ValueError(f"Dependency {dep_id} not satisfied")

            # Execute step
            # This would dispatch to the appropriate agent
            result = await self._execute_step(step, results, user_context)
            results[step.step_id] = result

            trace.total_tokens += step.estimated_tokens
            trace.total_cost += step.estimated_cost

        # Return final step result
        return results.get(plan.steps[-1].step_id)

    async def _execute_step(
        self,
        step,
        previous_results: dict,
        user_context: dict
    ) -> Any:
        """Execute a single plan step."""
        # This would dispatch to agents based on step.agent
        pass

    async def _save_trace(self, trace: ExecutionTrace):
        """Save execution trace for debugging/audit."""
        self.supabase.table("execution_traces").insert(
            trace.model_dump(mode="json")
        ).execute()
```
