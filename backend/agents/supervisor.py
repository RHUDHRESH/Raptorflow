"""
Master Supervisor Agent (Tier 0)
Routes high-level user requests to appropriate Tier 1 supervisor agents.
Manages cross-supervisor coordination and maintains global state.
"""

from typing import Dict, List, Optional, Any, Literal
from uuid import UUID
import logging

from backend.config.settings import get_settings
from backend.config.prompts import MASTER_SUPERVISOR_SYSTEM_PROMPT
from backend.services.vertex_ai_client import vertex_ai_client
from backend.utils.correlation import get_correlation_id

logger = logging.getLogger(__name__)
settings = get_settings()


class MasterSupervisor:
    """
    Tier 0: Master Orchestrator
    
    Responsibilities:
    - Route user requests to appropriate Tier 1 supervisors
    - Manage workflow orchestration across multiple supervisors
    - Track correlation IDs for distributed tracing
    - Enforce ADAPT framework stage ordering
    - Aggregate results from multiple supervisor agents
    """
    
    def __init__(self):
        self.available_supervisors = {
            "onboarding": {
                "description": "Handles user onboarding questionnaire and profile building",
                "capabilities": ["profile_creation", "entity_classification", "goal_setting"]
            },
            "customer_intelligence": {
                "description": "Builds and enriches Ideal Customer Profiles (ICPs)",
                "capabilities": ["icp_creation", "persona_narrative", "pain_point_mining", "psychographic_profiling"]
            },
            "strategy": {
                "description": "Generates marketing strategies following ADAPT framework",
                "capabilities": ["campaign_planning", "market_research", "ambient_search", "synthesis"]
            },
            "content": {
                "description": "Generates all forms of marketing content",
                "capabilities": ["blog_writing", "email_creation", "social_posts", "hooks", "brand_voice"]
            },
            "execution": {
                "description": "Publishes content to platforms and manages scheduling",
                "capabilities": ["platform_publishing", "scheduling", "canva_integration", "image_generation"]
            },
            "analytics": {
                "description": "Tracks performance and provides insights",
                "capabilities": ["metrics_collection", "insight_generation", "campaign_review"]
            },
            "safety": {
                "description": "Reviews content quality and enforces guardrails",
                "capabilities": ["content_critique", "compliance_check", "quality_assurance"]
            }
        }
    
    async def route_request(
        self, 
        goal: str, 
        context: Dict[str, Any],
        workspace_id: UUID
    ) -> Dict[str, Any]:
        """
        Routes a user request to the appropriate supervisor(s).
        
        Args:
            goal: High-level user goal (e.g., "Create a new campaign", "Generate blog post")
            context: Additional context (user profile, previous state, etc.)
            workspace_id: User's workspace ID
            
        Returns:
            Routing decision with selected supervisor(s) and next steps
        """
        correlation_id = get_correlation_id()
        logger.info(f"Routing request - Goal: {goal}", extra={"correlation_id": correlation_id})
        
        # Build routing prompt
        supervisor_list = "\n".join([
            f"- {name}: {info['description']}"
            for name, info in self.available_supervisors.items()
        ])
        
        routing_prompt = f"""
{MASTER_SUPERVISOR_SYSTEM_PROMPT}

Available Tier 1 Supervisors:
{supervisor_list}

User Goal: {goal}

Context:
- Workspace ID: {workspace_id}
- Has completed onboarding: {context.get('has_onboarding_profile', False)}
- Active campaigns: {context.get('active_campaigns', [])}
- Available ICPs: {len(context.get('cohorts', []))}

Task: Determine which supervisor(s) should handle this request. Consider:
1. Dependencies (e.g., strategy requires ICPs)
2. Workflow order (ADAPT framework stages)
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
            {"role": "system", "content": MASTER_SUPERVISOR_SYSTEM_PROMPT},
            {"role": "user", "content": routing_prompt}
        ]
        
        try:
            response = await vertex_ai_client.chat_completion(
                messages=messages,
                temperature=0.3,  # Lower temperature for more deterministic routing
                response_format={"type": "json_object"}
            )
            
            import json
            routing_decision = json.loads(response)
            
            logger.info(
                f"Routing decision: {routing_decision['primary_supervisor']}",
                extra={
                    "correlation_id": correlation_id,
                    "decision": routing_decision
                }
            )
            
            return routing_decision
            
        except Exception as e:
            logger.error(f"Routing failed: {e}", extra={"correlation_id": correlation_id})
            raise
    
    async def orchestrate_workflow(
        self,
        goal: str,
        workspace_id: UUID,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Orchestrates a complete workflow across multiple supervisors.
        
        This is used for complex requests that require multiple supervisor agents
        to collaborate (e.g., "Create and launch a new campaign").
        
        Args:
            goal: High-level user goal
            workspace_id: User's workspace ID
            context: Workflow context and state
            
        Returns:
            Orchestration result with steps executed and final output
        """
        correlation_id = get_correlation_id()
        logger.info(f"Orchestrating workflow for: {goal}", extra={"correlation_id": correlation_id})
        
        # Get routing decision
        routing = await self.route_request(goal, context, workspace_id)
        
        # Check prerequisites
        if routing.get("prerequisites"):
            return {
                "status": "prerequisites_missing",
                "missing": routing["prerequisites"],
                "message": f"Please complete: {', '.join(routing['prerequisites'])}",
                "suggested_action": self._suggest_prerequisite_action(routing["prerequisites"][0])
            }
        
        # Execute workflow
        workflow_state = {
            "goal": goal,
            "workspace_id": str(workspace_id),
            "correlation_id": correlation_id,
            "steps_completed": [],
            "current_step": 0,
            "total_steps": 1 + len(routing.get("supporting_supervisors", [])),
            "results": {}
        }
        
        # Primary supervisor execution (to be implemented when graphs are built)
        primary_supervisor = routing["primary_supervisor"]
        logger.info(f"Executing primary supervisor: {primary_supervisor}")
        
        # For now, return the routing decision
        # When graphs are implemented, this will actually invoke them
        return {
            "status": "routed",
            "routing_decision": routing,
            "workflow_state": workflow_state,
            "message": f"Request routed to {primary_supervisor} supervisor",
            "next_steps": self._get_next_steps(primary_supervisor, goal)
        }
    
    def _suggest_prerequisite_action(self, prerequisite: str) -> Dict[str, str]:
        """Suggests an action to complete a missing prerequisite."""
        suggestions = {
            "onboarding_profile": {
                "action": "start_onboarding",
                "endpoint": "/api/v1/onboarding/start",
                "message": "Complete your profile to get personalized strategies"
            },
            "customer_profiles": {
                "action": "create_icp",
                "endpoint": "/api/v1/icps/create",
                "message": "Define your target customer profiles first"
            },
            "global_strategy": {
                "action": "generate_strategy",
                "endpoint": "/api/v1/strategy/generate",
                "message": "Generate your marketing strategy foundation"
            }
        }
        return suggestions.get(prerequisite, {
            "action": "unknown",
            "message": f"Please complete: {prerequisite}"
        })
    
    def _get_next_steps(self, supervisor: str, goal: str) -> List[str]:
        """Provides next steps based on the supervisor handling the request."""
        next_steps_map = {
            "onboarding": [
                "Answer profile questions",
                "Define your target audience",
                "Set marketing goals"
            ],
            "customer_intelligence": [
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
            ]
        }
        return next_steps_map.get(supervisor, ["Continue with the flow"])
    
    async def monitor_progress(self, correlation_id: str) -> Dict[str, Any]:
        """
        Monitors the progress of a multi-step workflow.
        
        Args:
            correlation_id: Unique identifier for the workflow
            
        Returns:
            Progress status with completed steps and remaining work
        """
        # TODO: Implement progress tracking with Redis or database
        # For now, return a placeholder
        return {
            "correlation_id": correlation_id,
            "status": "in_progress",
            "steps_completed": 0,
            "total_steps": 1,
            "current_supervisor": "unknown"
        }
    
    async def aggregate_results(
        self,
        graph_outputs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Aggregates results from multiple supervisor agents into a unified response.
        
        Args:
            graph_outputs: List of outputs from different supervisor graphs
            
        Returns:
            Aggregated result combining all supervisor outputs
        """
        correlation_id = get_correlation_id()
        logger.info(
            f"Aggregating results from {len(graph_outputs)} supervisors",
            extra={"correlation_id": correlation_id}
        )
        
        aggregated = {
            "correlation_id": correlation_id,
            "supervisors_involved": [
                output.get("supervisor_name") for output in graph_outputs
            ],
            "combined_results": {},
            "summary": "",
            "next_actions": []
        }
        
        # Combine results
        for output in graph_outputs:
            supervisor_name = output.get("supervisor_name", "unknown")
            aggregated["combined_results"][supervisor_name] = output.get("result", {})
            
            # Collect next actions
            if "next_actions" in output:
                aggregated["next_actions"].extend(output["next_actions"])
        
        # Generate summary using LLM
        try:
            summary_prompt = f"""
Summarize the results from the following supervisor agents:

{graph_outputs}

Provide a concise, user-friendly summary of what was accomplished and what comes next.
"""
            messages = [
                {"role": "system", "content": "You are a helpful assistant summarizing workflow results."},
                {"role": "user", "content": summary_prompt}
            ]
            
            summary = await vertex_ai_client.chat_completion(messages=messages, temperature=0.5)
            aggregated["summary"] = summary
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            aggregated["summary"] = "Workflow completed successfully."
        
        return aggregated


# Global instance
master_supervisor = MasterSupervisor()

