"""
Customer Intelligence Supervisor - Coordinates ICP building sub-agents.

This supervisor orchestrates the research domain workflow:
1. ICP Builder → Builds structured ICP profiles
2. Tag Assignment → Assigns psychographic/demographic tags
3. Persona Narrative → Generates human narratives
4. Pain Point Miner → Extracts categorized pain points

All results are cached in Redis and logged with correlation IDs.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from backend.agents.base_agent import BaseSupervisor
from backend.models.persona import ICPResponse
from backend.utils.cache import cache
from backend.utils.correlation import get_correlation_id


logger = logging.getLogger(__name__)


class CustomerIntelligenceSupervisor(BaseSupervisor):
    """
    Tier 1 supervisor for customer intelligence / research domain.

    Coordinates sub-agents:
    - ICPBuilderAgent: Builds structured ICP from company info
    - TagAssignmentAgent: Assigns 5-15 relevant tags
    - PersonaNarrativeAgent: Creates human narrative
    - PainPointMinerAgent: Categorizes pain points

    Flow:
    1. Build ICP → structured profile with demographics
    2. Assign Tags → enrich with psychographic tags
    3. Generate Narrative → create persona story
    4. Mine Pain Points → categorize operational/financial/strategic
    5. Aggregate results and cache
    """

    def __init__(self):
        super().__init__(name="CustomerIntelligenceSupervisor")
        self._initialized = False

    async def _lazy_init(self) -> None:
        """Lazy load sub-agents to avoid circular imports."""
        if self._initialized:
            return

        from backend.agents.research.icp_builder_agent import icp_builder_agent
        from backend.agents.research.tag_assignment_agent import tag_assignment_agent
        from backend.agents.research.persona_narrative_agent import persona_narrative_agent
        from backend.agents.research.pain_point_miner_agent import pain_point_miner_agent

        self.sub_agents = {
            "icp_builder": icp_builder_agent,
            "tag_assignment": tag_assignment_agent,
            "persona_narrative": persona_narrative_agent,
            "pain_point_miner": pain_point_miner_agent,
        }
        self._initialized = True

    async def execute(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate sub-agents to build a complete ICP.

        Args:
            goal: High-level goal (e.g., "Build ICP for B2B SaaS startup")
            context: Contains icp_request payload with company_name, industry,
                    product_description, target_market

        Returns:
            Aggregated results with ICP, tags, narrative, and pain points
        """
        correlation_id = get_correlation_id()
        self.log(f"Starting customer intelligence workflow: {goal}")

        await self._lazy_init()

        # Extract ICP request from context
        icp_request = context.get("icp_request", {})
        if not icp_request:
            error_msg = "Missing icp_request in context"
            self.log(error_msg, level="error")
            return {
                "success": False,
                "error": error_msg,
                "correlation_id": correlation_id,
            }

        # Initialize results container
        results = {
            "correlation_id": correlation_id,
            "goal": goal,
            "steps": [],
            "errors": [],
        }

        # Cache key for intermediate results
        cache_key = f"{correlation_id}_research"

        try:
            # Step 1: Build ICP
            self.log("Step 1: Building ICP profile")
            icp_result = await self._execute_with_retry(
                agent_name="icp_builder",
                payload=icp_request,
                step_name="build_icp",
            )

            if not icp_result.get("success", False):
                results["errors"].append(f"ICP building failed: {icp_result.get('error')}")
                return {**results, "success": False}

            icp_output = icp_result.get("output", {})
            results["steps"].append({"step": "build_icp", "status": "completed"})
            results["icp"] = icp_output

            # Cache intermediate result
            await cache.set("research", cache_key, results, ttl=3600)  # 1 hour TTL

            # Step 2: Assign Tags
            self.log("Step 2: Assigning psychographic tags")
            tag_payload = {
                "icp_description": icp_output.get("executive_summary", ""),
                "demographics": icp_output.get("demographics", {}),
                "psychographics": icp_output.get("psychographics", {}),
            }

            tag_result = await self._execute_with_retry(
                agent_name="tag_assignment",
                payload=tag_payload,
                step_name="assign_tags",
            )

            if tag_result.get("success", False):
                results["tags"] = tag_result.get("output", {}).get("tags", [])
                results["steps"].append({"step": "assign_tags", "status": "completed"})
            else:
                results["errors"].append(f"Tag assignment failed: {tag_result.get('error')}")
                results["tags"] = []  # Continue with empty tags

            await cache.set("research", cache_key, results, ttl=3600)

            # Step 3: Generate Narrative
            self.log("Step 3: Generating persona narrative")
            narrative_payload = {
                "icp_name": icp_output.get("icp_name", "Customer Persona"),
                "demographics": icp_output.get("demographics", {}),
                "psychographics": icp_output.get("psychographics", {}),
                "pain_points": icp_output.get("pain_points", []),
                "goals": icp_output.get("goals", []),
            }

            narrative_result = await self._execute_with_retry(
                agent_name="persona_narrative",
                payload=narrative_payload,
                step_name="generate_narrative",
            )

            if narrative_result.get("success", False):
                results["narrative"] = narrative_result.get("output", {})
                results["steps"].append({"step": "generate_narrative", "status": "completed"})
            else:
                results["errors"].append(f"Narrative generation failed: {narrative_result.get('error')}")
                results["narrative"] = None

            await cache.set("research", cache_key, results, ttl=3600)

            # Step 4: Mine Pain Points
            self.log("Step 4: Mining and categorizing pain points")
            pain_point_payload = {
                "icp_description": icp_output.get("executive_summary", ""),
                "existing_pain_points": icp_output.get("pain_points", []),
                "product_description": icp_request.get("product_description", ""),
            }

            pain_point_result = await self._execute_with_retry(
                agent_name="pain_point_miner",
                payload=pain_point_payload,
                step_name="mine_pain_points",
            )

            if pain_point_result.get("success", False):
                results["categorized_pain_points"] = pain_point_result.get("output", {})
                results["steps"].append({"step": "mine_pain_points", "status": "completed"})
            else:
                results["errors"].append(f"Pain point mining failed: {pain_point_result.get('error')}")
                results["categorized_pain_points"] = None

            # Final cache update with 24 hour TTL
            await cache.set("research", cache_key, results, ttl=86400)

            # Build final response
            self.log("Customer intelligence workflow completed successfully")
            results["success"] = True
            results["completed"] = True

            return results

        except Exception as e:
            error_msg = f"Customer intelligence workflow failed: {str(e)}"
            self.log(error_msg, level="error", exc_info=True)
            results["errors"].append(error_msg)
            results["success"] = False
            return results

    async def _execute_with_retry(
        self,
        agent_name: str,
        payload: Dict[str, Any],
        step_name: str,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Execute a sub-agent with exponential backoff retry.

        Args:
            agent_name: Name of sub-agent in self.sub_agents
            payload: Payload to pass to agent
            step_name: Name of step for logging
            max_retries: Maximum retry attempts

        Returns:
            Agent result dict with success flag
        """
        agent = self.sub_agents.get(agent_name)
        if not agent:
            return {
                "success": False,
                "error": f"Agent {agent_name} not found",
            }

        last_error = None
        for attempt in range(max_retries):
            try:
                self.log(f"Executing {step_name} (attempt {attempt + 1}/{max_retries})")
                result = await agent.execute(payload)

                # Wrap result if agent doesn't return dict with success flag
                if isinstance(result, dict) and "agent" in result and "output" in result:
                    return {"success": True, **result}
                elif isinstance(result, dict):
                    return {"success": True, "output": result}
                else:
                    return {"success": True, "output": {"result": result}}

            except Exception as e:
                last_error = str(e)
                self.log(
                    f"{step_name} failed (attempt {attempt + 1}/{max_retries}): {e}",
                    level="warning",
                )

                if attempt < max_retries - 1:
                    # Exponential backoff: 2^attempt seconds
                    wait_time = 2 ** attempt
                    self.log(f"Retrying {step_name} in {wait_time}s")
                    await asyncio.sleep(wait_time)

        return {
            "success": False,
            "error": f"Failed after {max_retries} attempts: {last_error}",
        }


# Global instance
customer_intelligence_supervisor = CustomerIntelligenceSupervisor()
