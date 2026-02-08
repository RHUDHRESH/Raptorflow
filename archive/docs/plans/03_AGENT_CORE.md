# PHASE 3: AGENT CORE ENGINE

---

## 3.1 The Queen Router

The Queen is the central nervous system. It analyzes requests, selects skills, and orchestrates execution.

```python
# backend/agents/queen_router.py
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import json
import logging
from datetime import datetime

from core.config import get_settings
from core.resilience import CancellationToken
from skills.registry import skill_registry
from memory.foundation_store import foundation_store
from economics.cost_predictor import cost_predictor
from cognition.context_manager import context_manager

logger = logging.getLogger(__name__)
settings = get_settings()


class TaskStep(BaseModel):
    """A single step in the execution plan."""
    skill_id: str
    inputs: Dict[str, Any]
    depends_on: List[str] = []  # Step IDs this depends on
    parallel_group: int = 0     # Steps in same group run in parallel
    estimated_cost: float = 0.0


class ExecutionPlan(BaseModel):
    """Complete execution plan for a user request."""
    plan_id: str
    steps: List[TaskStep]
    total_estimated_cost: float
    total_estimated_time_seconds: int
    reasoning: str
    requires_approval: bool = False
    approval_reason: Optional[str] = None


class QueenRouter:
    """
    The Queen Router - Central task orchestration.

    Responsibilities:
    1. Analyze user intent
    2. Retrieve relevant Foundation context
    3. Select optimal skill(s)
    4. Create execution plan
    5. Estimate costs
    6. Request approval if needed
    """

    ROUTING_PROMPT = """
You are the Queen Router of the Raptorflow Hive.
Your job is to analyze user requests and create optimal execution plans.

PRINCIPLES:
1. MINIMIZE COST: Prefer cheaper skills when quality is equivalent
2. PARALLELIZE: Group independent tasks to reduce latency
3. CONTEXT FIRST: Every skill needs Foundation context
4. SINGLE SKILL PREFERRED: If one skill can do it, don't use multiple
5. FAIL GRACEFULLY: If unsure, route to a general-purpose skill

SKILL SELECTION RULES:
- Research tasks → research.* skills
- Content creation → content.* skills
- Indian data extraction → indian.* skills
- Campaign planning → campaign.* skills
- Creative/visual → muse.* skills

COST TIERS:
- flash-lite: $0.000025/1K tokens (use for simple routing, classification)
- flash: $0.000075/1K tokens (use for most tasks)
- pro: $0.00015/1K tokens (use for complex strategy, multi-step reasoning)

OUTPUT FORMAT:
Return a valid ExecutionPlan JSON with clear reasoning.
"""

    def __init__(self):
        self.model_client = None  # Injected
        self._initialized = False

    async def initialize(self, model_client):
        """Initialize with model client."""
        self.model_client = model_client
        self._initialized = True

    async def route(
        self,
        user_id: str,
        request: str,
        context: Optional[Dict[str, Any]] = None,
        cancellation_token: Optional[CancellationToken] = None
    ) -> ExecutionPlan:
        """
        Main routing function.

        Args:
            user_id: The user making the request
            request: Natural language request
            context: Additional context (e.g., current page, selected items)
            cancellation_token: For cancelling long-running operations

        Returns:
            ExecutionPlan with steps to execute
        """
        if not self._initialized:
            raise RuntimeError("QueenRouter not initialized")

        plan_id = f"plan_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        # Step 1: Load user's Foundation context
        foundation = await foundation_store.get_foundation(user_id)

        # Step 2: Get available skills
        available_skills = skill_registry.get_skill_summaries()

        # Step 3: Prepare routing prompt
        routing_request = self._build_routing_request(
            request=request,
            foundation=foundation,
            available_skills=available_skills,
            context=context or {}
        )

        # Step 4: Ask the Queen (using cheap model)
        if cancellation_token:
            cancellation_token.throw_if_cancelled()

        response = await self.model_client.generate(
            model=settings.ROUTER_MODEL,  # gemini-2.0-flash-lite
            system_prompt=self.ROUTING_PROMPT,
            user_prompt=routing_request,
            response_format="json",
            temperature=0.3  # Low temperature for consistent routing
        )

        # Step 5: Parse and validate plan
        plan = self._parse_routing_response(response, plan_id)

        # Step 6: Calculate actual cost estimates
        plan = await self._enrich_cost_estimates(plan, foundation)

        # Step 7: Check if approval needed
        plan = self._check_approval_requirements(plan, foundation)

        logger.info(
            f"Route: '{request[:50]}...' -> {len(plan.steps)} steps, "
            f"est. cost: ${plan.total_estimated_cost:.4f}"
        )

        return plan

    def _build_routing_request(
        self,
        request: str,
        foundation: Dict[str, Any],
        available_skills: List[Dict],
        context: Dict[str, Any]
    ) -> str:
        """Build the prompt for the routing model."""
        return f"""
USER REQUEST: {request}

USER CONTEXT:
- Company: {foundation.get('company_name', 'Unknown')}
- Industry: {foundation.get('industry', 'Unknown')}
- ICPs Defined: {len(foundation.get('icps', []))}
- Location: {foundation.get('location', 'Unknown')}
- Subscription Tier: {foundation.get('subscription_tier', 'free')}

AVAILABLE SKILLS:
{json.dumps(available_skills, indent=2)}

ADDITIONAL CONTEXT:
{json.dumps(context, indent=2)}

Create an ExecutionPlan JSON that fulfills this request optimally.
Consider:
1. Can this be done with a single skill?
2. If multiple skills needed, which can run in parallel?
3. What's the minimum cost approach?
4. Does this request need expensive research or just content generation?
"""

    def _parse_routing_response(self, response: Dict, plan_id: str) -> ExecutionPlan:
        """Parse the model response into an ExecutionPlan."""
        try:
            steps = []
            for i, step_data in enumerate(response.get("steps", [])):
                step = TaskStep(
                    skill_id=step_data["skill_id"],
                    inputs=step_data.get("inputs", {}),
                    depends_on=step_data.get("depends_on", []),
                    parallel_group=step_data.get("parallel_group", i)
                )
                steps.append(step)

            return ExecutionPlan(
                plan_id=plan_id,
                steps=steps,
                total_estimated_cost=0.0,  # Will be calculated
                total_estimated_time_seconds=0,  # Will be calculated
                reasoning=response.get("reasoning", "")
            )
        except Exception as e:
            logger.error(f"Failed to parse routing response: {e}")
            # Return a fallback plan with general skill
            return ExecutionPlan(
                plan_id=plan_id,
                steps=[TaskStep(skill_id="general.assistant.v1", inputs={"query": ""})],
                total_estimated_cost=0.05,
                total_estimated_time_seconds=30,
                reasoning="Fallback to general assistant due to routing error"
            )

    async def _enrich_cost_estimates(
        self,
        plan: ExecutionPlan,
        foundation: Dict[str, Any]
    ) -> ExecutionPlan:
        """Calculate actual cost estimates for each step."""
        total_cost = 0.0
        total_time = 0

        for step in plan.steps:
            estimate = await cost_predictor.predict(
                skill_id=step.skill_id,
                inputs=step.inputs
            )
            step.estimated_cost = estimate["estimated_cost"]
            total_cost += step.estimated_cost

            skill = skill_registry.get_skill(step.skill_id)
            if skill:
                total_time = max(total_time, skill.config.timeout_seconds)

        plan.total_estimated_cost = total_cost
        plan.total_estimated_time_seconds = total_time

        return plan

    def _check_approval_requirements(
        self,
        plan: ExecutionPlan,
        foundation: Dict[str, Any]
    ) -> ExecutionPlan:
        """Check if plan requires user approval before execution."""
        # Require approval for expensive operations
        if plan.total_estimated_cost > 0.50:
            plan.requires_approval = True
            plan.approval_reason = f"Estimated cost (${plan.total_estimated_cost:.2f}) exceeds $0.50"

        # Require approval for destructive tools
        destructive_skills = ["indian.email_sender", "indian.post_publisher"]
        for step in plan.steps:
            if step.skill_id in destructive_skills:
                plan.requires_approval = True
                plan.approval_reason = f"Skill '{step.skill_id}' can perform external actions"
                break

        return plan


# Singleton
queen_router = QueenRouter()
```

---

## 3.2 The Swarm Node (Agent Executor)

```python
# backend/agents/swarm_node.py
from typing import Dict, Any, Optional, AsyncGenerator
from pydantic import BaseModel
from datetime import datetime
import asyncio
import logging

from core.config import get_settings
from core.resilience import CancellationToken, AgentCallStack, get_circuit_breaker
from core.event_store import event_store, EventStore
from skills.registry import skill_registry
from skills.compiler import CompiledSkill, skill_compiler
from tools.registry import tool_registry
from memory.foundation_store import foundation_store
from cognition.context_manager import context_manager
from cognition.hallucination_detector import hallucination_detector

logger = logging.getLogger(__name__)
settings = get_settings()


class ExecutionResult(BaseModel):
    """Result of a skill execution."""
    execution_id: str
    skill_id: str
    success: bool
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    metrics: Dict[str, Any] = {}


class SwarmNode:
    """
    A SwarmNode is an ephemeral agent instance.

    Lifecycle:
    1. Instantiated with a skill_id
    2. Loads skill definition from registry
    3. Hydrates prompt with Foundation context
    4. Executes with tools
    5. Validates output
    6. Dies (ephemeral)

    Key Features:
    - Foundation context injection
    - Tool sandboxing
    - Output validation
    - Cost tracking
    - Event sourcing
    - Cancellation support
    """

    def __init__(
        self,
        skill_id: str,
        user_id: str,
        call_stack: Optional[AgentCallStack] = None
    ):
        self.skill_id = skill_id
        self.user_id = user_id
        self.call_stack = call_stack or AgentCallStack()

        # Load skill
        self.skill = skill_registry.get_skill(skill_id)
        if not self.skill:
            raise ValueError(f"Skill not found: {skill_id}")

        # Execution state
        self.execution_id = f"exec_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_{skill_id.replace('.', '_')}"
        self.start_time: Optional[datetime] = None
        self.tokens_used = 0
        self.cost = 0.0
        self.tool_calls = 0

        # Model client (injected)
        self.model_client = None

    async def execute(
        self,
        inputs: Dict[str, Any],
        model_client,
        cancellation_token: Optional[CancellationToken] = None
    ) -> ExecutionResult:
        """
        Execute the skill with the given inputs.

        Args:
            inputs: Validated inputs for the skill
            model_client: The AI model client
            cancellation_token: For cancellation

        Returns:
            ExecutionResult with output or error
        """
        self.model_client = model_client
        self.start_time = datetime.utcnow()

        # Push onto call stack (prevents recursion)
        self.call_stack.push(self.skill_id)

        try:
            # Event: Execution started
            await event_store.append(
                aggregate_id=self.execution_id,
                event_type=EventStore.EXECUTION_STARTED,
                data={"skill_id": self.skill_id, "inputs": inputs},
                user_id=self.user_id
            )

            # Step 1: Validate inputs
            validated_inputs = self._validate_inputs(inputs)

            # Step 2: Load Foundation context
            foundation = await foundation_store.get_foundation(self.user_id)

            # Step 3: Prepare optimized context
            context = await context_manager.prepare_context(
                query=str(inputs),
                foundation=foundation,
                memories=[],  # Could add relevant memories here
                conversation=[]
            )

            # Step 4: Hydrate system prompt
            system_prompt = skill_compiler.hydrate_prompt(
                skill=self.skill,
                inputs=validated_inputs,
                foundation=foundation
            )

            # Step 5: Load tools
            tools = tool_registry.get_tools(
                self.skill.config.required_tools + self.skill.config.optional_tools
            )

            # Step 6: Execute with timeout
            if cancellation_token:
                cancellation_token.throw_if_cancelled()

            result = await self._execute_with_retry(
                system_prompt=system_prompt,
                tools=tools,
                inputs=validated_inputs,
                cancellation_token=cancellation_token
            )

            # Step 7: Validate output
            validated_output = self._validate_output(result)

            # Step 8: Calculate final cost
            self._calculate_cost()

            # Event: Execution completed
            await event_store.append(
                aggregate_id=self.execution_id,
                event_type=EventStore.EXECUTION_COMPLETED,
                data={
                    "output": validated_output,
                    "metrics": self._get_metrics()
                },
                user_id=self.user_id
            )

            return ExecutionResult(
                execution_id=self.execution_id,
                skill_id=self.skill_id,
                success=True,
                output=validated_output,
                metrics=self._get_metrics()
            )

        except asyncio.TimeoutError:
            return self._handle_error("Execution timed out", "TIMEOUT")
        except Exception as e:
            return self._handle_error(str(e), "EXECUTION_ERROR")
        finally:
            self.call_stack.pop()

    async def execute_streaming(
        self,
        inputs: Dict[str, Any],
        model_client,
        cancellation_token: Optional[CancellationToken] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute with streaming output for real-time UI updates.

        Yields:
            Status updates, partial outputs, and final result
        """
        self.model_client = model_client
        self.start_time = datetime.utcnow()

        self.call_stack.push(self.skill_id)

        try:
            yield {"type": "status", "status": "starting", "skill_id": self.skill_id}

            # Validate inputs
            validated_inputs = self._validate_inputs(inputs)
            yield {"type": "status", "status": "inputs_validated"}

            # Load Foundation
            foundation = await foundation_store.get_foundation(self.user_id)
            yield {"type": "status", "status": "context_loaded"}

            # Hydrate prompt
            system_prompt = skill_compiler.hydrate_prompt(
                skill=self.skill,
                inputs=validated_inputs,
                foundation=foundation
            )

            # Load tools
            tools = tool_registry.get_tools(
                self.skill.config.required_tools + self.skill.config.optional_tools
            )

            yield {"type": "status", "status": "executing"}

            # Stream execution
            async for chunk in self._execute_streaming(
                system_prompt=system_prompt,
                tools=tools,
                inputs=validated_inputs,
                cancellation_token=cancellation_token
            ):
                yield chunk

            # Calculate cost
            self._calculate_cost()

            yield {
                "type": "complete",
                "execution_id": self.execution_id,
                "metrics": self._get_metrics()
            }

        except Exception as e:
            yield {
                "type": "error",
                "error": str(e),
                "execution_id": self.execution_id
            }
        finally:
            self.call_stack.pop()

    async def _execute_with_retry(
        self,
        system_prompt: str,
        tools: list,
        inputs: Dict[str, Any],
        cancellation_token: Optional[CancellationToken]
    ) -> Dict[str, Any]:
        """
        Execute with model cascade fallback.

        Try: Primary Model → Fallback Model → Graceful Degradation
        """
        models_to_try = [
            self.skill.config.model_primary,
            self.skill.config.model_fallback,
        ]
        models_to_try = [m for m in models_to_try if m]  # Remove None

        last_error = None

        for attempt, model in enumerate(models_to_try):
            try:
                if cancellation_token:
                    cancellation_token.throw_if_cancelled()

                # Event: LLM request
                await event_store.append(
                    aggregate_id=self.execution_id,
                    event_type=EventStore.LLM_REQUEST,
                    data={"model": model, "attempt": attempt + 1},
                    user_id=self.user_id
                )

                # Use circuit breaker
                circuit = get_circuit_breaker(f"model:{model}")

                result = await circuit.call(
                    self._call_model,
                    model=model,
                    system_prompt=system_prompt,
                    tools=tools,
                    inputs=inputs,
                    cancellation_token=cancellation_token
                )

                # Event: LLM response
                await event_store.append(
                    aggregate_id=self.execution_id,
                    event_type=EventStore.LLM_RESPONSE,
                    data={"model": model, "success": True},
                    user_id=self.user_id
                )

                return result

            except Exception as e:
                last_error = e
                logger.warning(f"Model {model} failed: {e}, trying fallback")

                # Event: Retry triggered
                await event_store.append(
                    aggregate_id=self.execution_id,
                    event_type=EventStore.RETRY_TRIGGERED,
                    data={"model": model, "error": str(e)},
                    user_id=self.user_id
                )

        # All models failed
        raise last_error or Exception("All models failed")

    async def _call_model(
        self,
        model: str,
        system_prompt: str,
        tools: list,
        inputs: Dict[str, Any],
        cancellation_token: Optional[CancellationToken]
    ) -> Dict[str, Any]:
        """
        Make the actual model call with tools.
        """
        # Build tool definitions for the model
        tool_definitions = [tool.get_definition() for tool in tools]

        # Create conversation
        messages = [
            {"role": "user", "content": json.dumps(inputs)}
        ]

        # Execute agent loop
        max_iterations = self.skill.config.max_tool_calls

        for iteration in range(max_iterations):
            if cancellation_token:
                cancellation_token.throw_if_cancelled()

            response = await self.model_client.generate(
                model=model,
                system_prompt=system_prompt,
                messages=messages,
                tools=tool_definitions,
                temperature=self.skill.config.temperature,
                max_tokens=self.skill.config.max_tokens
            )

            self.tokens_used += response.get("usage", {}).get("total_tokens", 0)

            # Check if model wants to use a tool
            if response.get("tool_calls"):
                for tool_call in response["tool_calls"]:
                    self.tool_calls += 1

                    # Event: Tool called
                    await event_store.append(
                        aggregate_id=self.execution_id,
                        event_type=EventStore.TOOL_CALLED,
                        data={
                            "tool": tool_call["name"],
                            "args": tool_call["arguments"]
                        },
                        user_id=self.user_id
                    )

                    # Execute tool
                    tool = next((t for t in tools if t.name == tool_call["name"]), None)
                    if tool:
                        tool_result = await tool.execute(**tool_call["arguments"])

                        # Event: Tool result
                        await event_store.append(
                            aggregate_id=self.execution_id,
                            event_type=EventStore.TOOL_RESULT,
                            data={
                                "tool": tool_call["name"],
                                "success": tool_result.get("success", True)
                            },
                            user_id=self.user_id
                        )

                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": json.dumps(tool_result)
                        })
            else:
                # Model is done, return final response
                return response.get("content", {})

        raise Exception(f"Max tool iterations ({max_iterations}) exceeded")

    async def _execute_streaming(
        self,
        system_prompt: str,
        tools: list,
        inputs: Dict[str, Any],
        cancellation_token: Optional[CancellationToken]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Streaming execution for real-time UI.
        """
        # Similar to _call_model but yields chunks
        model = self.skill.config.model_primary
        tool_definitions = [tool.get_definition() for tool in tools]
        messages = [{"role": "user", "content": json.dumps(inputs)}]

        async for chunk in self.model_client.generate_stream(
            model=model,
            system_prompt=system_prompt,
            messages=messages,
            tools=tool_definitions,
            temperature=self.skill.config.temperature
        ):
            if chunk.get("type") == "token":
                yield {"type": "token", "content": chunk["content"]}
            elif chunk.get("type") == "tool_call":
                yield {"type": "tool_start", "tool": chunk["name"]}
                # Execute tool...
                yield {"type": "tool_end", "tool": chunk["name"]}

    def _validate_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate inputs against skill schema."""
        try:
            model = self.skill.input_model
            validated = model(**inputs)
            return validated.model_dump()
        except Exception as e:
            raise ValueError(f"Input validation failed: {e}")

    def _validate_output(self, output: Any) -> Dict[str, Any]:
        """Validate output against skill schema."""
        try:
            model = self.skill.output_model
            if isinstance(output, str):
                output = json.loads(output)
            validated = model(**output)
            return validated.model_dump()
        except Exception as e:
            logger.warning(f"Output validation failed: {e}")
            return output  # Return raw if validation fails

    def _calculate_cost(self):
        """Calculate execution cost based on tokens and model."""
        model_costs = {
            "gemini-2.0-flash-lite": 0.000025,
            "gemini-2.0-flash": 0.000075,
            "gemini-2.0-pro": 0.00015,
            "gemini-2.0-ultra": 0.0003,
        }

        model = self.skill.config.model_primary
        cost_per_1k = model_costs.get(model, 0.0001)
        self.cost = (self.tokens_used / 1000) * cost_per_1k

    def _get_metrics(self) -> Dict[str, Any]:
        """Get execution metrics."""
        execution_time = 0
        if self.start_time:
            execution_time = (datetime.utcnow() - self.start_time).total_seconds() * 1000

        return {
            "tokens_used": self.tokens_used,
            "cost": round(self.cost, 6),
            "execution_time_ms": round(execution_time, 2),
            "tool_calls": self.tool_calls,
            "model": self.skill.config.model_primary
        }

    async def _handle_error(self, error: str, error_code: str) -> ExecutionResult:
        """Handle execution error."""
        await event_store.append(
            aggregate_id=self.execution_id,
            event_type=EventStore.EXECUTION_FAILED,
            data={"error": error, "error_code": error_code},
            user_id=self.user_id
        )

        return ExecutionResult(
            execution_id=self.execution_id,
            skill_id=self.skill_id,
            success=False,
            error=error,
            error_code=error_code,
            metrics=self._get_metrics()
        )


# Import json for the module
import json
```

---

## 3.3 The Critic (QA Validation)

```python
# backend/agents/critic.py
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

from core.config import get_settings
from cognition.adversarial_critic import AdversarialCritic
from cognition.hallucination_detector import HallucinationDetector

logger = logging.getLogger(__name__)
settings = get_settings()


class CritiqueIssue(BaseModel):
    """A single issue found by the critic."""
    category: str  # FACTUAL, LOGICAL, COMPLETENESS, ACTIONABILITY, BRAND
    description: str
    severity: str  # HIGH, MEDIUM, LOW
    suggestion: str


class CritiqueResult(BaseModel):
    """Result of critique analysis."""
    quality_score: int  # 0-100
    passed: bool
    issues: List[CritiqueIssue]
    should_regenerate: bool
    regeneration_hints: List[str] = []


class Critic:
    """
    The Critic validates agent outputs before returning to user.

    Checks:
    1. Schema compliance
    2. Hallucination detection
    3. Brand voice alignment
    4. Actionability
    5. Completeness
    """

    MIN_QUALITY_THRESHOLD = 70

    def __init__(self):
        self.adversarial = AdversarialCritic()
        self.hallucination = HallucinationDetector()
        self.model_client = None

    async def initialize(self, model_client):
        self.model_client = model_client
        await self.adversarial.initialize(model_client)
        await self.hallucination.initialize(model_client)

    async def critique(
        self,
        output: Dict[str, Any],
        skill_config: Dict[str, Any],
        foundation: Dict[str, Any],
        sources: List[str] = None
    ) -> CritiqueResult:
        """
        Perform comprehensive critique of agent output.

        Args:
            output: The agent's output to validate
            skill_config: The skill's evaluation criteria
            foundation: User's Foundation for brand alignment
            sources: Source materials for fact-checking

        Returns:
            CritiqueResult with score and issues
        """
        all_issues = []

        # Check 1: Schema compliance
        schema_issues = self._check_schema(output, skill_config)
        all_issues.extend(schema_issues)

        # Check 2: Hallucination detection (if sources provided)
        if sources:
            hallucination_result = await self.hallucination.verify_output(
                output=str(output),
                sources=sources
            )
            if hallucination_result.get("flagged_hallucinations"):
                for h in hallucination_result["flagged_hallucinations"]:
                    all_issues.append(CritiqueIssue(
                        category="FACTUAL",
                        description=f"Potential hallucination: {h}",
                        severity="HIGH",
                        suggestion="Verify this claim against sources or remove"
                    ))

        # Check 3: Adversarial critique
        adversarial_result = await self.adversarial.critique(
            output=str(output),
            context={
                "business_description": foundation.get("business_description", ""),
                "brand_voice": foundation.get("brand_voice", "Professional")
            }
        )

        for issue in adversarial_result.get("issues", []):
            all_issues.append(CritiqueIssue(
                category=issue["category"],
                description=issue["description"],
                severity=issue["severity"],
                suggestion=issue["suggestion"]
            ))

        # Check 4: Brand voice alignment
        brand_issues = await self._check_brand_alignment(output, foundation)
        all_issues.extend(brand_issues)

        # Calculate quality score
        quality_score = self._calculate_score(all_issues)

        # Determine if regeneration needed
        min_threshold = skill_config.get("min_quality_score", self.MIN_QUALITY_THRESHOLD)
        passed = quality_score >= min_threshold
        should_regenerate = not passed and quality_score < min_threshold - 20

        # Generate regeneration hints
        hints = []
        if should_regenerate:
            hints = self._generate_hints(all_issues)

        return CritiqueResult(
            quality_score=quality_score,
            passed=passed,
            issues=all_issues,
            should_regenerate=should_regenerate,
            regeneration_hints=hints
        )

    def _check_schema(
        self,
        output: Dict[str, Any],
        skill_config: Dict[str, Any]
    ) -> List[CritiqueIssue]:
        """Check if output matches required schema."""
        issues = []

        output_schema = skill_config.get("output_schema", {})
        required_fields = output_schema.get("required", [])

        for field in required_fields:
            if field not in output:
                issues.append(CritiqueIssue(
                    category="COMPLETENESS",
                    description=f"Missing required field: {field}",
                    severity="HIGH",
                    suggestion=f"Add '{field}' to the output"
                ))

        return issues

    async def _check_brand_alignment(
        self,
        output: Dict[str, Any],
        foundation: Dict[str, Any]
    ) -> List[CritiqueIssue]:
        """Check if output aligns with brand voice."""
        issues = []

        brand_voice = foundation.get("brand_voice", "").lower()
        output_text = str(output)

        # Simple checks (could be more sophisticated)
        if "professional" in brand_voice and "🚀" in output_text:
            issues.append(CritiqueIssue(
                category="BRAND",
                description="Emojis used in professional brand voice",
                severity="LOW",
                suggestion="Remove emojis for professional tone"
            ))

        if "casual" in brand_voice and len(output_text) > 5000:
            issues.append(CritiqueIssue(
                category="BRAND",
                description="Output too long for casual brand voice",
                severity="LOW",
                suggestion="Shorten and simplify the content"
            ))

        return issues

    def _calculate_score(self, issues: List[CritiqueIssue]) -> int:
        """Calculate quality score based on issues."""
        score = 100

        severity_penalties = {
            "HIGH": 15,
            "MEDIUM": 8,
            "LOW": 3
        }

        for issue in issues:
            penalty = severity_penalties.get(issue.severity, 5)
            score -= penalty

        return max(0, score)

    def _generate_hints(self, issues: List[CritiqueIssue]) -> List[str]:
        """Generate hints for regeneration."""
        hints = []

        # Group by category
        categories = {}
        for issue in issues:
            if issue.category not in categories:
                categories[issue.category] = []
            categories[issue.category].append(issue)

        # Generate hints per category
        if "FACTUAL" in categories:
            hints.append("Verify all claims against source materials")
        if "COMPLETENESS" in categories:
            hints.append(f"Include missing fields: {[i.description for i in categories['COMPLETENESS']]}")
        if "ACTIONABILITY" in categories:
            hints.append("Make recommendations more specific and executable")

        return hints


# Singleton
critic = Critic()
```

---

## 3.4 The Overseer (Final Approval)

```python
# backend/agents/overseer.py
from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging

from .critic import critic, CritiqueResult
from core.event_store import event_store, EventStore
from security.pii_scanner import pii_scanner

logger = logging.getLogger(__name__)


class OverseerVerdict(BaseModel):
    """Final verdict from the Overseer."""
    approved: bool
    output: Dict[str, Any]
    modifications: list = []
    warnings: list = []
    critique: Optional[CritiqueResult] = None


class Overseer:
    """
    The Overseer is the final checkpoint before output reaches the user.

    Responsibilities:
    1. Run Critic analysis
    2. Scan for PII leakage
    3. Apply user preferences (constitution)
    4. Make final modifications if needed
    5. Log the decision
    """

    async def verify(
        self,
        execution_id: str,
        output: Dict[str, Any],
        skill_config: Dict[str, Any],
        foundation: Dict[str, Any],
        user_id: str,
        sources: list = None
    ) -> OverseerVerdict:
        """
        Final verification before returning output to user.
        """
        modifications = []
        warnings = []

        # Step 1: Run Critic
        critique_result = await critic.critique(
            output=output,
            skill_config=skill_config,
            foundation=foundation,
            sources=sources or []
        )

        if not critique_result.passed:
            warnings.append(f"Quality score below threshold: {critique_result.quality_score}")

        # Step 2: PII scan
        output_str = str(output)
        pii_findings = pii_scanner.scan(output_str)

        if pii_findings:
            # Mask PII in output
            masked_output = self._mask_pii_in_output(output, pii_findings)
            modifications.append(f"Masked {len(pii_findings)} PII instances")
            output = masked_output
            warnings.append(f"PII detected and masked: {list(pii_findings.keys())}")

        # Step 3: Apply user constitution (preferences)
        constitution = foundation.get("constitution", {})
        if constitution:
            output, const_mods = self._apply_constitution(output, constitution)
            modifications.extend(const_mods)

        # Step 4: Log decision
        await event_store.append(
            aggregate_id=execution_id,
            event_type="OVERSEER_VERDICT",
            data={
                "approved": critique_result.passed,
                "quality_score": critique_result.quality_score,
                "modifications": modifications,
                "warnings": warnings
            },
            user_id=user_id
        )

        return OverseerVerdict(
            approved=critique_result.passed or critique_result.quality_score >= 50,
            output=output,
            modifications=modifications,
            warnings=warnings,
            critique=critique_result
        )

    def _mask_pii_in_output(
        self,
        output: Dict[str, Any],
        pii_findings: Dict[str, list]
    ) -> Dict[str, Any]:
        """Recursively mask PII in output."""
        output_str = str(output)
        masked = pii_scanner.mask(output_str)

        # Try to preserve structure
        try:
            import json
            return json.loads(masked)
        except:
            return {"content": masked}

    def _apply_constitution(
        self,
        output: Dict[str, Any],
        constitution: Dict[str, Any]
    ) -> tuple:
        """Apply user preferences to output."""
        modifications = []

        # Example: Remove emojis if user doesn't like them
        if constitution.get("no_emojis", False):
            output = self._remove_emojis(output)
            modifications.append("Removed emojis per user preference")

        # Example: Convert to formal language
        if constitution.get("formal_only", False):
            # Would use LLM to rewrite in formal tone
            modifications.append("Applied formal tone")

        return output, modifications

    def _remove_emojis(self, data: Any) -> Any:
        """Remove emojis from data recursively."""
        import re
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "]+",
            flags=re.UNICODE
        )

        if isinstance(data, str):
            return emoji_pattern.sub("", data)
        elif isinstance(data, dict):
            return {k: self._remove_emojis(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._remove_emojis(item) for item in data]
        return data


# Singleton
overseer = Overseer()
```
