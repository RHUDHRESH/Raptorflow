"""
Master Orchestrator (Tier 0) - Memory-Aware Top-level supervisor for RaptorFlow 2.0

This module implements the Master Orchestrator, the highest-level agent in the
RaptorFlow multi-agent hierarchy with intelligent memory-based orchestration.

KEY FEATURES:
1. Memory-Aware Routing: Uses historical task data to suggest optimal agent sequences
2. Adaptive Agent Selection: Selects agents based on workspace-specific performance metrics
3. Self-Correction Loops: Iteratively improves outputs through critique and revision
4. Human-in-the-Loop Checkpoints: Pauses for approval at critical stages with auto-approval rules
5. Context Propagation: Passes comprehensive AgentContext through entire execution chain
6. ADAPT Stage Enforcement: Ensures proper stage ordering
7. Result Aggregation: Combines outputs from multiple supervisors

Responsibilities:
- Route requests using memory of past successful task executions
- Swap agents based on performance metrics (success rate, quality, speed)
- Coordinate self-correction loops for content/strategy generation
- Manage workflow checkpoints with configurable approval rules
- Propagate rich context (brand voice, ICPs, preferences) to all agents
- Learn from successes and failures to improve future routing
- Cache intelligent routing decisions in Redis

Assumptions:
- Domain supervisors must be initialized before routing begins
- Correlation IDs are set at the request middleware level (main.py)
- Redis is available for caching and memory storage
- MemoryManager stores task history and performance metrics
"""

from __future__ import annotations

import asyncio
import json
import hashlib
import time
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
from enum import Enum

from backend.agents.base_agent import BaseSupervisor
from backend.config.settings import get_settings
from backend.config.prompts import MASTER_SUPERVISOR_SYSTEM_PROMPT
from backend.services.vertex_ai_client import vertex_ai_client
from backend.services.memory_manager import memory_manager
from backend.models.orchestration import (
    AgentContext,
    WorkflowCheckpoints,
    WorkflowCheckpoint,
    CheckpointCondition,
    CheckpointAction,
    SelfCorrectionConfig,
)
from backend.utils.correlation import get_correlation_id, set_correlation_id, generate_correlation_id
from backend.utils.cache import redis_cache

settings = get_settings()


class ADAPTStage(str, Enum):
    """
    ADAPT Framework stages in required execution order.

    Each stage must be completed before subsequent stages can execute.
    """
    ONBOARDING = "onboarding"           # Stage 0: Capture business context
    RESEARCH = "research"               # Stage 1: Build ICPs and personas (customer_intelligence)
    STRATEGY = "strategy"               # Stage 2: Generate campaign plans
    CONTENT = "content"                 # Stage 3: Create marketing assets
    EXECUTION = "execution"             # Stage 4: Publish and schedule
    ANALYTICS = "analytics"             # Stage 5: Track and analyze performance

    @classmethod
    def get_order(cls, stage: ADAPTStage) -> int:
        """Get numeric order of stage (0-5)."""
        order_map = {
            cls.ONBOARDING: 0,
            cls.RESEARCH: 1,
            cls.STRATEGY: 2,
            cls.CONTENT: 3,
            cls.EXECUTION: 4,
            cls.ANALYTICS: 5,
        }
        return order_map.get(stage, -1)

    @classmethod
    def validate_order(cls, required_stage: ADAPTStage, completed_stages: List[ADAPTStage]) -> tuple[bool, Optional[str]]:
        """
        Validate that all prerequisite stages have been completed.

        Args:
            required_stage: Stage that user wants to execute
            completed_stages: List of stages already completed

        Returns:
            Tuple of (is_valid, error_message)
        """
        required_order = cls.get_order(required_stage)

        for i in range(required_order):
            prerequisite = list(cls)[i]
            if prerequisite not in completed_stages:
                return False, f"Cannot execute {required_stage.value} stage before completing {prerequisite.value} stage"

        return True, None


class MasterOrchestrator(BaseSupervisor):
    """
    Tier 0: Master Orchestrator

    The top-level supervisor that routes requests to domain supervisors and
    enforces the ADAPT framework stage ordering.

    Domain Supervisors (Tier 1):
    - onboarding: Captures business context via dynamic questionnaire
    - research: Builds ICPs and customer personas (customer_intelligence)
    - strategy: Creates ADAPT-based marketing campaigns
    - content: Generates all marketing content assets
    - execution: Publishes content to platforms and manages scheduling
    - analytics: Tracks performance and generates insights
    - safety: Reviews content quality and enforces guardrails

    Usage:
        orchestrator = MasterOrchestrator()
        result = await orchestrator.execute(
            goal="Create a new campaign",
            context={"workspace_id": "...", "user_id": "..."}
        )
    """

    def __init__(self):
        """Initialize the Master Orchestrator with memory-aware capabilities."""
        super().__init__("master_orchestrator")

        # Inject MemoryManager for intelligent routing
        self.memory = memory_manager

        # Self-correction configuration
        self.self_correction_config = SelfCorrectionConfig()

        # Domain supervisor definitions
        # Note: Actual supervisor instances will be registered in main.py startup
        self.supervisor_metadata = {
            "onboarding": {
                "description": "Handles user onboarding questionnaire and profile building",
                "capabilities": ["profile_creation", "entity_classification", "goal_setting"],
                "stage": ADAPTStage.ONBOARDING,
            },
            "research": {  # Also known as customer_intelligence
                "description": "Builds and enriches Ideal Customer Profiles (ICPs)",
                "capabilities": ["icp_creation", "persona_narrative", "pain_point_mining", "psychographic_profiling"],
                "stage": ADAPTStage.RESEARCH,
            },
            "strategy": {
                "description": "Generates marketing strategies following ADAPT framework",
                "capabilities": ["campaign_planning", "market_research", "ambient_search", "synthesis"],
                "stage": ADAPTStage.STRATEGY,
            },
            "content": {
                "description": "Generates all forms of marketing content",
                "capabilities": ["blog_writing", "email_creation", "social_posts", "hooks", "brand_voice"],
                "stage": ADAPTStage.CONTENT,
            },
            "execution": {
                "description": "Publishes content to platforms and manages scheduling",
                "capabilities": ["platform_publishing", "scheduling", "canva_integration", "image_generation"],
                "stage": ADAPTStage.EXECUTION,
            },
            "analytics": {
                "description": "Tracks performance and provides insights",
                "capabilities": ["metrics_collection", "insight_generation", "campaign_review"],
                "stage": ADAPTStage.ANALYTICS,
            },
            "safety": {
                "description": "Reviews content quality and enforces guardrails",
                "capabilities": ["content_critique", "compliance_check", "quality_assurance"],
                "stage": None,  # Safety is cross-cutting, not part of ADAPT sequence
            }
        }

        self.log("Master Orchestrator initialized", supervisor_count=len(self.supervisor_metadata))

    async def execute(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute high-level orchestration: route request to appropriate supervisor(s).

        Args:
            goal: High-level user objective (e.g., "Create a new campaign")
            context: Execution context with workspace_id, user_id, completed_stages, etc.

        Returns:
            Routing decision or orchestration result
        """
        # Ensure correlation ID exists
        correlation_id = get_correlation_id() or generate_correlation_id()
        if not get_correlation_id():
            set_correlation_id(correlation_id)

        workspace_id = context.get("workspace_id")

        self.log(
            f"Orchestrating request: {goal}",
            workspace_id=workspace_id,
            has_context=bool(context)
        )

        # Get routing decision
        routing = await self.route_request(goal, context, workspace_id)

        # Check if prerequisites are missing
        if routing.get("status") == "prerequisites_missing":
            return routing

        # Check ADAPT stage ordering
        primary_supervisor = routing.get("primary_supervisor")
        if primary_supervisor in self.supervisor_metadata:
            stage = self.supervisor_metadata[primary_supervisor].get("stage")
            if stage:
                completed_stages = context.get("completed_stages", [])
                is_valid, error_msg = ADAPTStage.validate_order(stage, completed_stages)

                if not is_valid:
                    self.log(
                        f"ADAPT stage validation failed: {error_msg}",
                        level="warning",
                        required_stage=stage.value,
                        completed_stages=[s.value for s in completed_stages]
                    )
                    return {
                        "status": "stage_order_violation",
                        "error": error_msg,
                        "required_stage": stage.value,
                        "completed_stages": [s.value for s in completed_stages],
                        "suggestion": self._suggest_next_stage(completed_stages),
                        "correlation_id": correlation_id
                    }

        # Return routing decision
        # In future iterations, this will actually invoke the supervisor
        return {
            "status": "routed",
            "routing_decision": routing,
            "correlation_id": correlation_id,
            "message": f"Request routed to {primary_supervisor} supervisor",
            "next_steps": self._get_next_steps(primary_supervisor, goal)
        }

    async def route_request(
        self,
        goal: str,
        context: Dict[str, Any],
        workspace_id: Optional[str]
    ) -> Dict[str, Any]:
        """
        Intelligently route a user request to the appropriate domain supervisor(s).

        Uses Vertex AI (Gemini) for classification and caches results in Redis
        to avoid redundant LLM calls for similar requests.

        Args:
            goal: High-level user goal
            context: Additional context (user profile, previous state, etc.)
            workspace_id: User's workspace ID

        Returns:
            Routing decision with primary supervisor, supporting supervisors, and prerequisites
        """
        correlation_id = get_correlation_id()

        # Generate cache key from goal + context
        cache_key = self._generate_cache_key(goal, context)

        # Check cache first
        cached_routing = await self._get_cached_routing(cache_key)
        if cached_routing:
            self.log("Using cached routing decision", cache_key=cache_key)
            return cached_routing

        # Build classification prompt
        supervisor_list = "\n".join([
            f"- {name}: {info['description']} (Capabilities: {', '.join(info['capabilities'])})"
            for name, info in self.supervisor_metadata.items()
        ])

        classification_prompt = f"""
{MASTER_SUPERVISOR_SYSTEM_PROMPT}

Available Tier 1 Supervisors:
{supervisor_list}

User Goal: {goal}

Context:
- Workspace ID: {workspace_id}
- Has completed onboarding: {context.get('has_onboarding_profile', False)}
- Active campaigns: {context.get('active_campaigns', [])}
- Available ICPs: {len(context.get('cohorts', []))}
- Completed ADAPT stages: {[s.value for s in context.get('completed_stages', [])]}

Task: Determine which supervisor(s) should handle this request. Consider:
1. Dependencies (e.g., strategy requires ICPs from research)
2. ADAPT workflow order (onboarding → research → strategy → content → execution → analytics)
3. Prerequisites (e.g., onboarding before strategy)

Respond in JSON format:
{{
    "primary_supervisor": "supervisor_name",
    "supporting_supervisors": ["supervisor_name"],
    "reasoning": "explanation",
    "prerequisites": ["any missing prerequisites"],
    "estimated_complexity": "low|medium|high"
}}
"""

        messages = [
            {"role": "system", "content": "You are an intelligent routing assistant for a marketing platform."},
            {"role": "user", "content": classification_prompt}
        ]

        try:
            response = await vertex_ai_client.chat_completion(
                messages=messages,
                temperature=0.3,  # Lower temperature for more deterministic routing
                response_format={"type": "json_object"}
            )

            routing_decision = response

            # Validate routing decision
            if "primary_supervisor" not in routing_decision:
                raise ValueError("LLM response missing 'primary_supervisor' field")

            # Check for missing prerequisites
            prerequisites = routing_decision.get("prerequisites", [])
            if prerequisites:
                routing_decision["status"] = "prerequisites_missing"
                routing_decision["suggested_action"] = self._suggest_prerequisite_action(prerequisites[0])

            # Cache the routing decision
            await self._cache_routing(cache_key, routing_decision)

            self.log(
                f"Routing decision: {routing_decision['primary_supervisor']}",
                decision=routing_decision
            )

            return routing_decision

        except Exception as e:
            self.log(f"Routing failed: {e}", level="error")
            # Fallback: basic keyword-based routing
            return self._fallback_routing(goal, context)

    def _generate_cache_key(self, goal: str, context: Dict[str, Any]) -> str:
        """
        Generate a cache key for routing decisions.

        Args:
            goal: User goal
            context: Request context

        Returns:
            MD5 hash of goal + relevant context fields
        """
        # Include only stable context fields that affect routing
        cache_input = {
            "goal": goal.lower().strip(),
            "has_onboarding": context.get("has_onboarding_profile", False),
            "has_icps": len(context.get("cohorts", [])) > 0,
            "completed_stages": sorted([s.value for s in context.get("completed_stages", [])])
        }
        cache_str = json.dumps(cache_input, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()

    async def _get_cached_routing(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached routing decision from Redis."""
        try:
            return await redis_cache.get("routing", cache_key)
        except Exception as e:
            self.log(f"Cache retrieval failed: {e}", level="warning")
            return None

    async def _cache_routing(self, cache_key: str, routing: Dict[str, Any]) -> None:
        """Store routing decision in Redis with 1-hour TTL."""
        try:
            # Cache for 1 hour (routing decisions can change as user progresses)
            await redis_cache.set("routing", cache_key, routing, ttl=3600)
        except Exception as e:
            self.log(f"Cache storage failed: {e}", level="warning")

    def _fallback_routing(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simple keyword-based routing fallback when LLM classification fails.

        Args:
            goal: User goal
            context: Request context

        Returns:
            Basic routing decision
        """
        goal_lower = goal.lower()

        # Simple keyword matching
        if any(kw in goal_lower for kw in ["onboard", "profile", "setup", "start"]):
            primary = "onboarding"
        elif any(kw in goal_lower for kw in ["icp", "persona", "customer", "audience", "research"]):
            primary = "research"
        elif any(kw in goal_lower for kw in ["strategy", "campaign", "plan"]):
            primary = "strategy"
        elif any(kw in goal_lower for kw in ["content", "blog", "email", "post", "write"]):
            primary = "content"
        elif any(kw in goal_lower for kw in ["publish", "schedule", "post", "execute"]):
            primary = "execution"
        elif any(kw in goal_lower for kw in ["analytics", "metrics", "performance", "insights"]):
            primary = "analytics"
        else:
            primary = "onboarding"  # Default to onboarding

        self.log(f"Using fallback routing: {primary}", level="warning")

        return {
            "primary_supervisor": primary,
            "supporting_supervisors": [],
            "reasoning": "Fallback keyword-based routing",
            "prerequisites": [],
            "estimated_complexity": "medium"
        }

    def _suggest_prerequisite_action(self, prerequisite: str) -> Dict[str, str]:
        """
        Suggest an action to complete a missing prerequisite.

        Args:
            prerequisite: Missing prerequisite identifier

        Returns:
            Action suggestion with endpoint and message
        """
        suggestions = {
            "onboarding_profile": {
                "action": "start_onboarding",
                "endpoint": "/api/v1/onboarding/start",
                "message": "Complete your profile to get personalized strategies"
            },
            "customer_profiles": {
                "action": "create_icp",
                "endpoint": "/api/v1/cohorts/create",
                "message": "Define your target customer profiles first"
            },
            "global_strategy": {
                "action": "generate_strategy",
                "endpoint": "/api/v1/strategy/generate",
                "message": "Generate your marketing strategy foundation"
            },
            "content_assets": {
                "action": "generate_content",
                "endpoint": "/api/v1/content/generate",
                "message": "Create content assets before publishing"
            }
        }
        return suggestions.get(prerequisite, {
            "action": "unknown",
            "message": f"Please complete: {prerequisite}"
        })

    def _suggest_next_stage(self, completed_stages: List[ADAPTStage]) -> Dict[str, Any]:
        """
        Suggest the next stage user should complete.

        Args:
            completed_stages: List of completed ADAPT stages

        Returns:
            Suggestion with next stage and action
        """
        all_stages = list(ADAPTStage)

        for stage in all_stages:
            if stage not in completed_stages:
                supervisor = None
                for sup_name, sup_meta in self.supervisor_metadata.items():
                    if sup_meta.get("stage") == stage:
                        supervisor = sup_name
                        break

                return {
                    "next_stage": stage.value,
                    "supervisor": supervisor,
                    "message": f"Complete {stage.value} stage next",
                    "description": self.supervisor_metadata.get(supervisor, {}).get("description", "")
                }

        return {
            "next_stage": None,
            "message": "All ADAPT stages completed"
        }

    def _get_next_steps(self, supervisor: str, goal: str) -> List[str]:
        """
        Provide next steps based on the supervisor handling the request.

        Args:
            supervisor: Supervisor name
            goal: User goal

        Returns:
            List of next steps
        """
        next_steps_map = {
            "onboarding": [
                "Answer profile questions",
                "Define your target audience",
                "Set marketing goals"
            ],
            "research": [
                "Provide initial persona inputs",
                "Review AI-generated ICP profiles",
                "Refine psychographic attributes"
            ],
            "strategy": [
                "Select target ICPs",
                "Define campaign goal",
                "Review generated strategy",
                "Approve execution plan"
            ],
            "content": [
                "Specify content type and topic",
                "Review generated variants",
                "Select and approve content"
            ],
            "execution": [
                "Connect platforms",
                "Review posting schedule",
                "Approve and publish"
            ],
            "analytics": [
                "View performance metrics",
                "Review insights",
                "Optimize campaigns"
            ]
        }
        return next_steps_map.get(supervisor, ["Continue with the flow"])

    async def aggregate_results(
        self,
        supervisor_outputs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Aggregate results from multiple supervisor agents into a unified response.

        This is used when a complex workflow involves multiple supervisors
        (e.g., Research → Strategy → Content pipeline).

        Args:
            supervisor_outputs: List of outputs from different supervisor executions

        Returns:
            Aggregated result combining all outputs
        """
        correlation_id = get_correlation_id()

        self.log(
            f"Aggregating results from {len(supervisor_outputs)} supervisors",
        )

        aggregated = {
            "correlation_id": correlation_id,
            "supervisors_involved": [
                output.get("supervisor_name") for output in supervisor_outputs
            ],
            "combined_results": {},
            "summary": "",
            "next_actions": []
        }

        # Combine results
        for output in supervisor_outputs:
            supervisor_name = output.get("supervisor_name", "unknown")
            aggregated["combined_results"][supervisor_name] = output.get("result", {})

            # Collect next actions
            if "next_actions" in output:
                aggregated["next_actions"].extend(output["next_actions"])

        # Generate summary using Vertex AI
        try:
            summary_prompt = f"""
Summarize the results from the following supervisor agents:

{json.dumps(supervisor_outputs, indent=2)}

Provide a concise, user-friendly summary of:
1. What was accomplished
2. Key outputs and results
3. What comes next

Keep it under 150 words.
"""
            messages = [
                {"role": "system", "content": "You are a helpful assistant summarizing workflow results."},
                {"role": "user", "content": summary_prompt}
            ]

            summary = await vertex_ai_client.chat_completion(messages=messages, temperature=0.5)
            aggregated["summary"] = summary

        except Exception as e:
            self.log(f"Summary generation failed: {e}", level="error")
            aggregated["summary"] = "Workflow completed successfully. Review individual supervisor results for details."

        return aggregated

    def get_supervisor_health(self) -> Dict[str, Any]:
        """
        Get health status of all registered supervisors.

        Returns:
            Dictionary with supervisor statuses and metadata
        """
        health = {
            "master_orchestrator": {
                "status": "healthy",
                "registered_supervisors": len(self.sub_agents),
                "available_supervisors": list(self.supervisor_metadata.keys())
            },
            "supervisors": {}
        }

        for sup_name, sup_meta in self.supervisor_metadata.items():
            sup_instance = self.sub_agents.get(sup_name)
            health["supervisors"][sup_name] = {
                "description": sup_meta["description"],
                "capabilities": sup_meta["capabilities"],
                "stage": sup_meta["stage"].value if sup_meta["stage"] else None,
                "registered": sup_instance is not None,
                "sub_agents": sup_instance.list_agents() if sup_instance else []
            }

        return health

    async def route_with_context(
        self,
        goal: str,
        workspace_id: UUID,
        user_id: Optional[UUID] = None,
        context_override: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[str], AgentContext]:
        """
        Memory-aware routing that uses historical data to suggest optimal agent sequences.

        This method:
        1. Searches memory for similar successful tasks (confidence > 0.8)
        2. If found, returns the proven agent sequence
        3. Otherwise, calls LLM planner to suggest a new sequence
        4. Stores the chosen sequence in memory for future learning

        Args:
            goal: High-level task objective
            workspace_id: Workspace identifier
            user_id: User making the request
            context_override: Optional context values to override defaults

        Returns:
            Tuple of (agent_sequence, agent_context)
        """
        correlation_id = get_correlation_id() or generate_correlation_id()
        if not get_correlation_id():
            set_correlation_id(correlation_id)

        self.log(
            f"Memory-aware routing for goal: {goal}",
            workspace_id=str(workspace_id),
            goal=goal,
        )

        # Build comprehensive agent context
        agent_context = await self._get_agent_context(
            workspace_id=workspace_id,
            user_id=user_id,
            goal=goal,
            correlation_id=correlation_id,
            context_override=context_override,
        )

        # Search memory for similar successful tasks
        similar_tasks = await self.memory.search(
            query=goal,
            memory_type="task_history",
            workspace_id=workspace_id,
            limit=5,
        )

        # Filter for high-confidence successful tasks
        high_confidence_tasks = [
            task for task in similar_tasks
            if task.confidence > 0.8 and task.content.get("success", False)
        ]

        if high_confidence_tasks:
            # Use the best performing sequence from memory
            best_task = max(high_confidence_tasks, key=lambda t: t.confidence)
            agent_sequence = best_task.content.get("agent_sequence", [])

            self.log(
                f"Using proven agent sequence from memory",
                sequence=agent_sequence,
                confidence=best_task.confidence,
                similar_goal=best_task.content.get("goal"),
            )

            # Store that we're reusing this sequence
            agent_context.past_successes.append({
                "goal": best_task.content.get("goal"),
                "sequence": agent_sequence,
                "confidence": best_task.confidence,
            })

            return agent_sequence, agent_context

        # No high-confidence match found, use LLM planner
        self.log("No high-confidence match in memory, calling LLM planner")

        agent_sequence = await self._plan_agent_sequence(goal, agent_context)

        self.log(
            f"LLM planned agent sequence",
            sequence=agent_sequence,
        )

        return agent_sequence, agent_context

    async def _get_agent_context(
        self,
        workspace_id: UUID,
        user_id: Optional[UUID],
        goal: str,
        correlation_id: str,
        context_override: Optional[Dict[str, Any]] = None,
    ) -> AgentContext:
        """
        Build comprehensive AgentContext for execution.

        Args:
            workspace_id: Workspace identifier
            user_id: User identifier
            goal: Task goal
            correlation_id: Correlation ID
            context_override: Optional override values

        Returns:
            Fully populated AgentContext
        """
        # Get task history from memory
        task_history = await self.memory.search(
            query="",  # Get all tasks
            memory_type="task_history",
            workspace_id=workspace_id,
            limit=20,
        )

        # Get performance data for agents
        performance_data = {}
        for supervisor_name in self.supervisor_metadata.keys():
            best_agent = await self.memory.get_best_performing_agent(
                task_type=supervisor_name,
                workspace_id=workspace_id,
            )
            if best_agent:
                performance_data[supervisor_name] = {
                    "best_agent": best_agent,
                }

        # Build context
        context = AgentContext(
            workspace_id=workspace_id,
            correlation_id=correlation_id,
            user_id=user_id,
            task_history=[task.to_dict() for task in task_history],
            performance_data=performance_data,
        )

        # Apply overrides if provided
        if context_override:
            for key, value in context_override.items():
                if hasattr(context, key):
                    setattr(context, key, value)

        return context

    async def _plan_agent_sequence(
        self,
        goal: str,
        context: AgentContext,
    ) -> List[str]:
        """
        Use LLM to plan an optimal agent sequence for a new task.

        Args:
            goal: Task goal
            context: Agent context with workspace data

        Returns:
            List of agent names in execution order
        """
        # Build supervisor list
        supervisor_list = "\n".join([
            f"- {name}: {info['description']}"
            for name, info in self.supervisor_metadata.items()
        ])

        # Build performance insights
        performance_insights = ""
        if context.performance_data:
            performance_insights = "\n\nPast Performance Insights:\n" + "\n".join([
                f"- {task_type}: Best agent is {data.get('best_agent', 'unknown')}"
                for task_type, data in context.performance_data.items()
            ])

        planning_prompt = f"""
{MASTER_SUPERVISOR_SYSTEM_PROMPT}

Available Supervisors:
{supervisor_list}
{performance_insights}

Task Goal: {goal}

Workspace Context:
- Has brand voice: {bool(context.brand_voice)}
- Target ICPs: {len(context.target_icps)}
- Past successful tasks: {len(context.past_successes)}

Based on this goal and the available supervisors, suggest the optimal sequence
of agents to accomplish this task.

Respond in JSON format:
{{
    "agent_sequence": ["supervisor1", "supervisor2", ...],
    "reasoning": "explanation of why this sequence is optimal"
}}
"""

        messages = [
            {"role": "system", "content": "You are an intelligent agent orchestration planner."},
            {"role": "user", "content": planning_prompt}
        ]

        try:
            response = await vertex_ai_client.chat_completion(
                messages=messages,
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            agent_sequence = response.get("agent_sequence", ["onboarding"])
            reasoning = response.get("reasoning", "")

            self.log(
                "LLM planned agent sequence",
                sequence=agent_sequence,
                reasoning=reasoning,
            )

            return agent_sequence

        except Exception as e:
            self.log(f"Agent sequence planning failed: {e}", level="error")
            # Fallback to basic routing
            return [self._fallback_routing(goal, context.to_dict())["primary_supervisor"]]

    async def select_best_agent(
        self,
        task_type: str,
        workspace_id: UUID,
        fallback_agent: Optional[str] = None,
    ) -> str:
        """
        Adaptive agent selection based on workspace-specific performance metrics.

        Args:
            task_type: Type of task (content_generation, strategy_planning, etc.)
            workspace_id: Workspace identifier
            fallback_agent: Fallback agent if no performance data exists

        Returns:
            Name of best performing agent for this task type
        """
        self.log(
            f"Selecting best agent for task type: {task_type}",
            workspace_id=str(workspace_id),
        )

        best_agent = await self.memory.get_best_performing_agent(
            task_type=task_type,
            workspace_id=workspace_id,
        )

        if best_agent:
            self.log(
                f"Selected high-performing agent",
                agent=best_agent,
                task_type=task_type,
            )
            return best_agent

        # No performance data, use fallback or default
        if fallback_agent:
            self.log(
                f"No performance data, using fallback",
                agent=fallback_agent,
                task_type=task_type,
            )
            return fallback_agent

        # Default mapping
        default_agents = {
            "content_generation": "content",
            "strategy_planning": "strategy",
            "research": "research",
            "execution": "execution",
            "analytics": "analytics",
        }

        return default_agents.get(task_type, "onboarding")

    async def execute_with_self_correction(
        self,
        agent_name: str,
        payload: Dict[str, Any],
        context: AgentContext,
        config: Optional[SelfCorrectionConfig] = None,
    ) -> Dict[str, Any]:
        """
        Execute an agent with self-correction loops for quality improvement.

        This method:
        1. Calls the content/strategy agent to generate initial output
        2. Critiques the output against quality thresholds
        3. Revises based on critique
        4. Repeats until quality meets threshold or max iterations reached
        5. Stores failed attempts in memory for learning

        Args:
            agent_name: Name of agent to execute
            payload: Execution payload
            context: Agent context
            config: Self-correction configuration (uses default if not provided)

        Returns:
            Final result after self-correction
        """
        config = config or self.self_correction_config

        self.log(
            f"Starting self-correction execution",
            agent=agent_name,
            max_iterations=config.max_iterations,
        )

        iteration = 0
        best_result = None
        best_score = 0.0
        attempts = []

        while iteration < config.max_iterations:
            iteration += 1

            self.log(f"Self-correction iteration {iteration}/{config.max_iterations}")

            # Execute agent
            result = await self._execute_agent_with_context(agent_name, payload, context)

            # Evaluate quality
            quality_score = await self._calculate_quality_score(
                result=result,
                aspects=config.critique_aspects,
                context=context,
            )

            self.log(
                f"Iteration {iteration} quality score: {quality_score}",
                score=quality_score,
                threshold=config.min_quality_score,
            )

            attempts.append({
                "iteration": iteration,
                "result": result,
                "quality_score": quality_score,
            })

            # Track best result
            if quality_score > best_score:
                best_score = quality_score
                best_result = result

            # Check if quality threshold met
            if quality_score >= config.min_quality_score:
                self.log(
                    f"Quality threshold met on iteration {iteration}",
                    score=quality_score,
                )
                break

            # Check if improvement is too small to continue
            if iteration > 1:
                previous_score = attempts[-2]["quality_score"]
                improvement = quality_score - previous_score

                if improvement < config.improvement_threshold:
                    self.log(
                        f"Improvement below threshold, stopping",
                        improvement=improvement,
                        threshold=config.improvement_threshold,
                    )
                    break

            # Generate critique and revise payload for next iteration
            if iteration < config.max_iterations:
                critique = await self._generate_critique(
                    result=result,
                    aspects=config.critique_aspects,
                    quality_score=quality_score,
                    context=context,
                )

                # Update payload with critique for revision
                payload["critique"] = critique
                payload["previous_attempt"] = result

        # Store failed attempts if configured
        if config.store_failures and best_score < config.min_quality_score:
            for attempt in attempts:
                await self.memory.store_critique(
                    content_id=f"{context.correlation_id}_{attempt['iteration']}",
                    critique=f"Quality score: {attempt['quality_score']}",
                    issues=[f"Failed to meet threshold of {config.min_quality_score}"],
                    workspace_id=context.workspace_id,
                )

        return {
            **best_result,
            "self_correction_metadata": {
                "iterations": iteration,
                "final_quality_score": best_score,
                "threshold_met": best_score >= config.min_quality_score,
                "attempts": len(attempts),
            }
        }

    async def _execute_agent_with_context(
        self,
        agent_name: str,
        payload: Dict[str, Any],
        context: AgentContext,
    ) -> Dict[str, Any]:
        """
        Execute an agent with full context propagation.

        Args:
            agent_name: Agent to execute
            payload: Execution payload
            context: Agent context to propagate

        Returns:
            Agent execution result
        """
        # Add context to payload
        payload["agent_context"] = context.to_dict()

        # Get agent instance
        agent = self.sub_agents.get(agent_name)

        if not agent:
            self.log(
                f"Agent not found: {agent_name}",
                level="warning",
            )
            return {
                "status": "error",
                "error": f"Agent {agent_name} not registered",
            }

        # Execute agent
        return await agent.execute(payload)

    async def _calculate_quality_score(
        self,
        result: Dict[str, Any],
        aspects: List[str],
        context: AgentContext,
    ) -> float:
        """
        Calculate quality score for generated content/strategy.

        Uses LLM to evaluate specific aspects and return a score.

        Args:
            result: Agent execution result
            aspects: Aspects to evaluate
            context: Agent context

        Returns:
            Quality score between 0.0 and 1.0
        """
        # Extract content to evaluate
        content = result.get("result", result.get("content", ""))

        evaluation_prompt = f"""
Evaluate the following output on these aspects: {', '.join(aspects)}

Output to evaluate:
{json.dumps(content, indent=2)}

Brand voice requirements: {json.dumps(context.brand_voice) if context.brand_voice else "None specified"}

For each aspect, rate from 0-10. Then provide an overall score from 0.0 to 1.0.

Respond in JSON format:
{{
    "aspect_scores": {{{', '.join([f'"{aspect}": 0-10' for aspect in aspects])}}},
    "overall_score": 0.0-1.0,
    "reasoning": "brief explanation"
}}
"""

        messages = [
            {"role": "system", "content": "You are a quality evaluation expert."},
            {"role": "user", "content": evaluation_prompt}
        ]

        try:
            response = await vertex_ai_client.chat_completion(
                messages=messages,
                temperature=0.2,
                response_format={"type": "json_object"}
            )

            return float(response.get("overall_score", 0.5))

        except Exception as e:
            self.log(f"Quality evaluation failed: {e}", level="error")
            return 0.5  # Default middle score

    async def _generate_critique(
        self,
        result: Dict[str, Any],
        aspects: List[str],
        quality_score: float,
        context: AgentContext,
    ) -> str:
        """
        Generate constructive critique for content revision.

        Args:
            result: Agent execution result
            aspects: Aspects to critique
            quality_score: Current quality score
            context: Agent context

        Returns:
            Critique text
        """
        content = result.get("result", result.get("content", ""))

        critique_prompt = f"""
The following output scored {quality_score}/1.0 on quality evaluation.

Output:
{json.dumps(content, indent=2)}

Provide specific, actionable critique on these aspects: {', '.join(aspects)}

Brand voice requirements: {json.dumps(context.brand_voice) if context.brand_voice else "None specified"}

Focus on concrete improvements that would increase the quality score.
"""

        messages = [
            {"role": "system", "content": "You are a constructive content critic."},
            {"role": "user", "content": critique_prompt}
        ]

        try:
            response = await vertex_ai_client.chat_completion(
                messages=messages,
                temperature=0.3,
            )

            # Handle both dict and string responses
            if isinstance(response, dict):
                return response.get("critique", str(response))
            return str(response)

        except Exception as e:
            self.log(f"Critique generation failed: {e}", level="error")
            return f"Improve quality score from {quality_score} to meet threshold."

    async def evaluate_checkpoint(
        self,
        checkpoint_name: str,
        checkpoints_config: WorkflowCheckpoints,
        context: AgentContext,
        execution_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Evaluate a workflow checkpoint and determine if approval is needed.

        This implements human-in-the-loop checkpoints with:
        - Configurable trigger conditions
        - Auto-approval rules
        - Timeout handling
        - User notifications

        Args:
            checkpoint_name: Name of the checkpoint
            checkpoints_config: Checkpoint configuration
            context: Agent context
            execution_data: Current execution data (quality scores, results, etc.)

        Returns:
            Checkpoint evaluation result with approval status
        """
        self.log(
            f"Evaluating checkpoint: {checkpoint_name}",
            workspace_id=str(context.workspace_id),
        )

        checkpoint = checkpoints_config.get_checkpoint(checkpoint_name)

        if not checkpoint:
            self.log(
                f"Checkpoint not found: {checkpoint_name}",
                level="warning",
            )
            return {
                "status": "auto_approved",
                "reason": "Checkpoint not configured",
            }

        # Build checkpoint context
        checkpoint_context = {
            **context.to_dict(),
            **execution_data,
        }

        # Check if should pause for approval
        should_pause = checkpoints_config.should_pause(
            checkpoint_name=checkpoint_name,
            context=checkpoint_context,
        )

        if not should_pause:
            self.log(
                f"Checkpoint auto-approved",
                checkpoint=checkpoint_name,
            )
            return {
                "status": "auto_approved",
                "reason": "Auto-approval conditions met",
                "checkpoint": checkpoint.name,
            }

        # Pause for approval (mock implementation - in production would notify user)
        self.log(
            f"Checkpoint requires approval",
            checkpoint=checkpoint_name,
            timeout=checkpoint.timeout_seconds,
        )

        # Mock approval interface - in production this would:
        # 1. Send notification to user(s)
        # 2. Wait for approval with timeout
        # 3. Return approval decision

        # For now, simulate based on timeout
        if checkpoint.timeout_seconds and checkpoint.timeout_seconds > 0:
            # Simulate immediate auto-approval for testing
            # In production, this would wait for user input
            return {
                "status": "approved",
                "reason": "User approval received (mock)",
                "checkpoint": checkpoint.name,
                "approver": str(context.user_id) if context.user_id else "system",
            }
        else:
            # No timeout means must wait for manual approval
            return {
                "status": "pending_approval",
                "reason": "Awaiting user approval",
                "checkpoint": checkpoint.name,
                "notify_users": [str(uid) for uid in checkpoint.notify_users],
            }


# Global instance
master_orchestrator = MasterOrchestrator()
