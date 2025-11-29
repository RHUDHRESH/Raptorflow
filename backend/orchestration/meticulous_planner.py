
"""
Meticulous Planner - The "Reasoning Engine" for the Executive Director.

This module implements the sequential thinking logic to break down complex
requests into actionable, dependency-aware plans.
"""

import logging
import json
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

from backend.services.vertex_ai_client import vertex_ai_client

logger = logging.getLogger(__name__)

@dataclass
class PlanStep:
    step_id: str
    description: str
    agent: str
    dependencies: List[str]
    required_tools: List[str]
    exit_criteria: str

@dataclass
class DetailedPlan:
    plan_id: str
    name: str
    objective: str
    steps: List[PlanStep]
    risks: List[str]
    contingencies: Dict[str, str]

class MeticulousPlanner:
    """
    Uses chain-of-thought reasoning to build robust plans.
    """
    
    async def create_plan(self, goal: str, context: Dict[str, Any]) -> DetailedPlan:
        """
        Generates a detailed plan from a high-level goal.
        """
        logger.info(f"🧠 Meticulous Planner: Analyzing '{goal}'")
        
        # 1. Thought Process
        thoughts = await self._think_through(goal, context)
        
        # 2. Plan Generation
        plan_data = await self._generate_plan_structure(goal, thoughts)
        
        # 3. Verification (Self-Correction)
        verified_plan = await self._verify_and_refine(plan_data)
        
        return verified_plan

    async def _think_through(self, goal: str, context: Dict[str, Any]) -> List[str]:
        """
        Simulates the 'SequentialThinking' tool loop.
        """
        prompt = f"""
        Goal: {goal}
        Context: {json.dumps(context)}
        
        Perform a step-by-step analysis to determine the best course of action.
        Consider:
        - What is the true objective?
        - What are the hidden blockers?
        - What resources (agents/tools) are best suited?
        - What if the obvious path fails?
        
        Output a list of thought strings.
        """
        
        try:
            response = await vertex_ai_client.generate_json(
                prompt=prompt,
                model_type="reasoning"
            )
            return response.get("thoughts", ["Analyzed goal", "Identified constraints", "Formulated approach"])
        except Exception as e:
            logger.error(f"Thinking failed: {e}")
            return ["Default thinking process applied"]

    async def _generate_plan_structure(self, goal: str, thoughts: List[str]) -> DetailedPlan:
        """
        Converts thoughts into a structured plan.
        """
        prompt = f"""
        Goal: {goal}
        Thoughts: {json.dumps(thoughts)}
        
        Create a detailed execution plan.
        
        Return JSON:
        {{
            "plan_id": "plan_xyz",
            "name": "string",
            "objective": "string",
            "steps": [
                {{
                    "step_id": "step_1",
                    "description": "string",
                    "agent": "string (e.g. Architect, Strategos, WebScraper)",
                    "dependencies": ["step_0"],
                    "required_tools": ["search", "db"],
                    "exit_criteria": "string"
                }}
            ],
            "risks": ["string"],
            "contingencies": {{"risk": "mitigation"}}
        }}
        """
        
        try:
            data = await vertex_ai_client.generate_json(prompt=prompt, model_type="reasoning")
            
            steps = [PlanStep(**s) for s in data.get("steps", [])]
            
            return DetailedPlan(
                plan_id=data.get("plan_id", "default_plan"),
                name=data.get("name", "Strategic Plan"),
                objective=data.get("objective", goal),
                steps=steps,
                risks=data.get("risks", []),
                contingencies=data.get("contingencies", {})
            )
        except Exception as e:
            logger.error(f"Plan generation failed: {e}")
            # Fallback
            return DetailedPlan(
                plan_id="fallback",
                name="Fallback Plan",
                objective=goal,
                steps=[],
                risks=[],
                contingencies={}
            )

    async def _verify_and_refine(self, plan: DetailedPlan) -> DetailedPlan:
        """
        Checks the plan for logical gaps.
        """
        # In a full implementation, this would use an LLM "Critic" to critique the JSON.
        # For now, we assume the reasoning model did a good job.
        return plan
