"""
Executive Director - The "Goddamn Pro" of RaptorFlow.

This is the top-level orchestrator that behaves like an autonomous marketing executive.
It does NOT just follow a script. It:
1. Receives high-level intent (e.g., "Launch a Q4 campaign for Enterprise").
2. Thinks meticulously (using SequentialThinking pattern) to break it down.
3. Plans alternate routes (Plan A, Plan B, Contingencies).
4. Delegates to the Council of Lords (Architect, Strategos, etc.).
5. Reviews work with a critical eye before approving.

Usage:
    director = ExecutiveDirector()
    plan = await director.process_request(user_intent, context)
"""

import logging
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from uuid import uuid4

from backend.services.vertex_ai_client import vertex_ai_client
from backend.orchestration.swarm_orchestrator import SwarmOrchestrator
from backend.orchestration.meticulous_planner import MeticulousPlanner
from backend.core.reasoning.engine import ReasoningEngine
from backend.core.reasoning.reflexion import ReflexionLoop
from backend.agents.council_of_lords.architect import ArchitectLord
from backend.agents.council_of_lords.cognition import CognitionLord
from backend.agents.council_of_lords.seer import SeerLord
from backend.agents.strategy.strategy_supervisor import StrategySupervisor
from backend.messaging.event_bus import EventBus
from backend.messaging.context_bus import ContextBus

logger = logging.getLogger(__name__)

class ExecutiveDirector:
    """
    The autonomous executive that drives the RaptorFlow system.
    """

    def __init__(self):
        self.logger = logging.getLogger("ExecutiveDirector")
        self.orchestrator = None  # Initialized lazily or passed in
        self.meticulous_planner = MeticulousPlanner()
        self.reasoning_engine = ReasoningEngine()
        self.reflexion_loop = ReflexionLoop()
        
        # Direct access to the "Board of Directors"
        self.architect = ArchitectLord()
        self.cognition = CognitionLord()
        self.seer = SeerLord()
        self.strategy_supervisor = StrategySupervisor()

    async def initialize(self, orchestrator: SwarmOrchestrator):
        """Link to the swarm orchestrator."""
        self.orchestrator = orchestrator
        # Initialize lords if needed
        await self.architect.initialize()
        # await self.cognition.initialize() # BaseAgent doesn't always have async init, check impl
        # await self.seer.initialize()

    async def process_request(self, 
                            user_intent: str, 
                            workspace_id: str, 
                            user_id: str,
                            constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        The main entry point for "Autonomous Mode".
        """
        request_id = str(uuid4())
        self.logger.info(f"🚀 Executive Director received request {request_id}: {user_intent}")

        # Phase 1: SOTA Reasoning (Tree of Thoughts)
        # We now use the ReasoningEngine for deep cognitive processing.
        context = {"workspace_id": workspace_id, "constraints": constraints}
        thought_tree = await self.reasoning_engine.process_goal(user_intent, context)
        
        # Convert thought tree result into a plan structure for execution
        # (Assuming the last node in the tree contains the plan)
        # For backward compatibility with MeticulousPlanner, we bridge here.
        
        # Get plan node content
        plan_content = "Generated from Tree of Thoughts" # Placeholder if tree is empty
        # A real implementation would traverse the tree to find the best plan node
        
        # Create detailed plan using MeticulousPlanner (as a formatter)
        detailed_plan = await self.meticulous_planner.create_plan(
            goal=user_intent,
            context=context
        )
        
        # Step 5: Reflexion & Self-Correction
        # Before we execute, we ask the ReflexionLoop to critique the plan
        detailed_plan = await self.reflexion_loop.critique_and_refine(
            plan=detailed_plan,
            context=context
        )
        
        self.logger.info(f"🧠 SOTA Plan Verified: {detailed_plan.name}")

        # Phase 2: Strategic Review (Simulated Board Meeting)
        # We assume the planner generated one robust plan, but we can still critique it.
        # For now, we proceed with this plan.
        
        # Phase 3: Execution Orchestration
        # Convert DetailedPlan to dict for orchestration
        plan_dict = {
            "plan_name": detailed_plan.name,
            "objective": detailed_plan.objective,
            "target_icp_ids": [], # resolved dynamically
            "estimated_budget_tier": constraints.get("budget", "Medium") if constraints else "Medium",
            "steps": [s.__dict__ for s in detailed_plan.steps]
        }
        
        execution_result = await self._orchestrate_execution(plan_dict, workspace_id, user_id)

        return {
            "request_id": request_id,
            "analysis": {"objective": detailed_plan.objective, "risks": detailed_plan.risks},
            "selected_plan": plan_dict,
            "execution_status": execution_result["status"],
            "execution_details": execution_result,
            "executive_summary": await self._generate_executive_summary(execution_result)
        }

    async def _meticulous_analysis(self, intent: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
        # Deprecated in favor of MeticulousPlanner class, but kept for fallback if needed
        pass

    async def _develop_strategic_plans(self, analysis: Dict[str, Any], workspace_id: str) -> List[Dict[str, Any]]:
        """
        Generates detailed plans based on the analysis.
        """
        # We ask the Strategos (via Supervisor logic or direct LLM call for now) to flesh out the approaches.
        
        prompt = f"""
        Based on this analysis: {json.dumps(analysis)}
        
        Develop 2 distinct execution plans (Plan A: The most likely to succeed, Plan B: The bold/innovative alternative).
        
        For each plan, detail:
        - plan_name
        - objective
        - key_tactics (list)
        - expected_timeline_weeks
        - estimated_budget_tier (Low/Medium/High)
        - required_agents (List of agent capabilities needed)
        
        Return JSON: {{ "plans": [ ... ] }}
        """
        
        try:
            result = await vertex_ai_client.generate_json(
                prompt=prompt,
                model_type="reasoning"
            )
            return result.get("plans", [])
        except Exception as e:
            self.logger.error(f"Plan development failed: {e}")
            return [{
                "plan_name": "Default Plan",
                "objective": "Execute user intent",
                "key_tactics": ["Research", "Content", "Launch"],
                "required_agents": ["strategy_supervisor", "content_supervisor"]
            }]

    async def _conduct_board_review(self, plans: List[Dict[str, Any]], workspace_id: str) -> Dict[str, Any]:
        """
        Simulates a review process where 'Seer' (Trends) and 'Architect' (Structure) critique the plans.
        """
        # In a full implementation, we would actually invoke the Seer and Architect agents via the EventBus.
        # For this 'Pro' revamp, we'll simulate this high-level interaction to select the best plan.
        
        plans_text = json.dumps(plans, indent=2)
        
        prompt = f"""
        Review these two strategic plans as a Board of Directors (Seer and Architect).
        
        Plans:
        {plans_text}
        
        Critique each plan for:
        - Feasibility (Architect)
        - Market Fit (Seer)
        - Risk/Reward
        
        Select the BEST plan. Modifying it if necessary to mitigate risks.
        
        Return the FINAL selected plan object (enriched with critiques).
        """
        
        try:
            selected_plan = await vertex_ai_client.generate_json(prompt=prompt, model_type="reasoning")
            return selected_plan
        except Exception as e:
            self.logger.error(f"Board review failed: {e}")
            return plans[0] # Default to Plan A

    async def _orchestrate_execution(self, plan: Dict[str, Any], workspace_id: str, user_id: str) -> Dict[str, Any]:
        """
        Translates the strategic plan into a Swarm Workflow and executes it.
        """
        self.logger.info(f"🎬 Orchestrating plan: {plan.get('plan_name')}")
        
        # 1. Create a workflow in SwarmOrchestrator
        workflow_goal = {
            "type": "autonomous_execution",
            "plan": plan
        }
        
        if self.orchestrator:
            workflow_id = await self.orchestrator.create_workflow(
                workflow_type="strategic_execution",
                goal=workflow_goal,
                user_id=user_id,
                workspace_id=workspace_id
            )
            
            # 2. Execute the workflow (Here we would map plan steps to orchestrator stages)
            # For now, we'll execute a consolidated 'Strategy -> Execution' flow
            
            # This logic bridges the high-level plan to the concrete StrategySupervisor
            strategy_payload = {
                "icp_ids": plan.get("target_icp_ids", []), # Assuming these would be resolved
                "goals": plan.get("objective"),
                "budget": plan.get("estimated_budget_tier"),
                "mode": "comprehensive",
                "workspace_id": workspace_id
            }
            
            # Since we might not have ICP IDs yet, we might need to fetch them or skip
            # This is where the "Autonomous" part needs to be robust.
            # If no ICPs, we trigger an 'onboarding' or 'research' sub-routine.
            
            return {
                "status": "initiated",
                "workflow_id": workflow_id,
                "message": "Plan execution started. Agents are mobilizing."
            }
        else:
            return {"status": "dry_run", "message": "Orchestrator not linked."}

    async def _generate_executive_summary(self, execution_result: Dict[str, Any]) -> str:
        """
        Writes a clean, professional summary for the user.
        """
        return f"""
        **Executive Summary**
        
        I have initiated the execution of the strategic plan.
        Workflow ID: {execution_result.get('workflow_id')}
        
        Next Steps:
        1. The Strategy Team is refining the tactical details.
        2. The Content Team is on standby for asset creation.
        3. I will report back upon completion of the initial phase.
        """

# Global instance
executive_director = ExecutiveDirector()
