"""
Master Orchestrator (Tier 0) - Top-level supervisor for RaptorFlow 2.0

This module implements the Master Orchestrator, the highest-level agent in the
RaptorFlow multi-agent hierarchy. It is responsible for:

1. Request Routing: Analyze incoming goals and dispatch to appropriate domain supervisors
2. ADAPT Stage Enforcement: Ensure proper stage ordering (Onboarding → Research → Strategy → Content → Execution → Analytics)
3. Correlation ID Management: Generate and propagate IDs throughout the agent hierarchy
4. Result Aggregation: Combine outputs from multiple supervisors into unified responses
5. Workflow Orchestration: Coordinate complex multi-supervisor workflows

Responsibilities:
- Route requests to domain supervisors (onboarding, research, strategy, content, execution, analytics)
- Enforce prerequisite completion (e.g., can't run Strategy without completing Research)
- Use Vertex AI for intelligent classification and routing
- Cache classification results in Redis to reduce LLM calls
- Log all operations with correlation IDs for distributed tracing

Assumptions:
- Domain supervisors must be initialized before routing begins
- Correlation IDs are set at the request middleware level (main.py)
- Redis is available for caching (graceful degradation if unavailable)
"""

from __future__ import annotations

import json
import hashlib
from typing import Any, Dict, List, Optional
from uuid import UUID
from enum import Enum

from backend.agents.base_agent import BaseSupervisor
from backend.config.settings import get_settings
from backend.config.prompts import MASTER_SUPERVISOR_SYSTEM_PROMPT
from backend.services.vertex_ai_client import vertex_ai_client
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
        """Initialize the Master Orchestrator with domain supervisor metadata."""
        super().__init__("master_orchestrator")

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


# Global instance
master_orchestrator = MasterOrchestrator()
