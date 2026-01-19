"Expert Council Agentic Swarm System (Ultra-Premium)"
"A LangGraph-powered multi-agent system with an Infinite Skill System."

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Annotated, TypedDict, Type
from datetime import datetime, UTC

from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

from backend.services.vertex_ai_client import get_vertex_ai_client
from backend.agents.skills.registry import get_skills_registry
from backend.agents.skills.harness import get_skill_harness
from backend.schemas import (
    CouncilAgent, 
    CouncilContribution, 
    CouncilDiscussion, 
    SkillDefinition,
    AgentSkillSet
)

logger = logging.getLogger(__name__)

# --- Expert Council Workflow State ---
class ExpertCouncilSwarmState(TypedDict):
    """Ultra-Premium Swarm State"""
    mission: str
    workspace_context: Dict[str, Any]
    discussion: CouncilDiscussion
    iteration_count: int
    max_iterations: int
    swarm_status: str # deliberating, executing, escalating, finalized
    active_agent_id: str
    skills_loaded: Dict[str, List[str]] # agent_id -> skill_names
    performance_metrics: Dict[str, float] # accuracy, latency, throughput
    escalation_required: bool
    final_report: Optional[str]

class ExpertCouncilSwarm:
    """
    Ultra-Premium Agentic OS: The Expert Council Swarm.
    
    Architecture:
    - LangGraph Multi-Agent Swarm
    - Infinite Skill System (Deep Logic Harness)
    - Protocol: Hybrid (Sync deliberation / Async skill execution)
    """
    
    def __init__(self, demo_mode: bool = False):
        self.vertex_ai_client = get_vertex_ai_client()
        self.skill_registry = get_skills_registry()
        self.skill_harness = get_skill_harness()
        self.demo_mode = demo_mode
        
        # Define the High-Level Experts (Marketing interpretation of mandated roles)
        self.agents = {
            "architect": CouncilAgent(
                id="architect",
                name="Marcus",
                role="Strategy Architect",
                avatar="🏛️",
                description="Senior Strategy Architect focusing on category design, moats, and systemic positioning.",
                specialization="Category creation and market structure.",
                personality="Visionary, authoritative, and precise."
            ),
            "analyst": CouncilAgent(
                id="analyst",
                name="Sera",
                role="Performance Analyst",
                avatar="📈",
                description="Data-driven performance analyst for ROI projection, CAC modeling, and market feasibility.",
                specialization="Competitive intelligence and unit economics.",
                personality="Skeptical, rigorous, and evidence-based."
            ),
            "developer": CouncilAgent(
                id="developer",
                name="Jax",
                role="GTM Developer",
                avatar="🛠️",
                description="Technical executioner for GTM stacks, conversion funnels, and automated marketing sequences.",
                specialization="Funnel architecture and growth engineering.",
                personality="Pragmatic, efficient, and execution-oriented."
            ),
            "qa": CouncilAgent(
                id="qa",
                name="Elena",
                role="Brand QA",
                avatar="🛡️",
                description="Guardian of brand integrity, messaging compliance, and strategic risk mitigation.",
                specialization="Quality control and brand-voice alignment.",
                personality="Meticulous, ethical, and protective."
            )
        }
        
        self.workflow = self._build_swarm_graph()

    def _build_swarm_graph(self) -> StateGraph:
        """Construct the LangGraph swarm with Escalation Path."""
        builder = StateGraph(ExpertCouncilSwarmState)
        
        # Nodes
        builder.add_node("orchestrate", self.orchestrator_node)
        builder.add_node("architect_deliberate", self.architect_node)
        builder.add_node("analyst_deliberate", self.analyst_node)
        builder.add_node("developer_deliberate", self.developer_node)
        builder.add_node("qa_deliberate", self.qa_node)
        builder.add_node("execute_skills", self.skill_execution_node)
        builder.add_node("escalate", self.escalate_node)
        builder.add_node("synthesize_report", self.synthesizer_node)
        
        # Define edges
        builder.set_entry_point("orchestrate")
        
        builder.add_conditional_edges(
            "orchestrate",
            self.swarm_router,
            {
                "architect": "architect_deliberate",
                "analyst": "analyst_deliberate",
                "developer": "developer_deliberate",
                "qa": "qa_deliberate",
                "execute": "execute_skills",
                "escalate": "escalate",
                "finalize": "synthesize_report"
            }
        )
        
        # Experts return to orchestrator
        builder.add_edge("architect_deliberate", "orchestrate")
        builder.add_edge("analyst_deliberate", "orchestrate")
        builder.add_edge("developer_deliberate", "orchestrate")
        builder.add_edge("qa_deliberate", "orchestrate")
        builder.add_edge("execute_skills", "orchestrate")
        builder.add_edge("escalate", "orchestrate")
        builder.add_edge("synthesize_report", END)
        
        return builder.compile()

    def swarm_router(self, state: ExpertCouncilSwarmState) -> str:
        """Determines the next phase of the swarm, including Escalation."""
        if state["escalation_required"]:
            return "escalate"
            
        if state["iteration_count"] >= state["max_iterations"] or state["discussion"].consensus_reached:
            return "finalize"
        
        target = state.get("active_agent_id", "architect")
        if target in self.agents:
            return target
        
        return "finalize"

    async def escalate_node(self, state: ExpertCouncilSwarmState) -> ExpertCouncilSwarmState:
        """
        Escalation Node: Triggered when consensus fails.
        Path: [Lead] - In a real system, this triggers a notification to the Founder.
        """
        logger.warning(f"Swarm Escalation Triggered for mission: {state['mission']}")
        state["swarm_status"] = "escalated"
        
        escalation_msg = "[SYSTEM_ALERT]: Consensus cannot be reached. The Analyst (Sera) and Architect (Marcus) have fundamental misalignments. Escalating to SWARM_LEAD for tie-breaking decision."
        
        state["discussion"].contributions.append(CouncilContribution(
            agent_id="system",
            agent_name="Escalation Engine",
            content=escalation_msg,
            type="decision"
        ))
        
        # Force a synthetic decision to unblock
        state["escalation_required"] = False
        state["discussion"].consensus_reached = True
        return state

    async def orchestrator_node(self, state: ExpertCouncilSwarmState) -> ExpertCouncilSwarmState:
        """The Swarm Lead (The Chair) manages the deliberation flow."""
        logger.info(f"Swarm Orchestrator: Iteration {state['iteration_count']}")
        
        # Logic to decide next speaker or if skill execution is needed
        if self.demo_mode:
            # Simple rotation for demo
            order = ["architect", "analyst", "developer", "qa"]
            idx = state["iteration_count"] % len(order)
            state["active_agent_id"] = order[idx]
            
            if state["iteration_count"] >= 4:
                state["discussion"].consensus_reached = True
                
            summary = f"Orchestrator: Passing the floor to {self.agents[state['active_agent_id']].name}."
        else:
            # Real AI routing logic
            history = self._format_history(state["discussion"])
            prompt = f"""
            You are the Swarm Lead for the Expert Council. 
            Mission: {state['mission']}
            Discussion: {history}
            
            Based on progress, who should speak next?
            - architect (Systemic Strategy)
            - analyst (Feasibility/ROI)
            - developer (Technical execution)
            - qa (Quality/Risk)
            
            Return JSON: {{'next_agent': '...', 'reasoning': '...', 'consensus': bool}}
            """
            resp = await self.vertex_ai_client.generate_text(prompt)
            decision = self._parse_json(resp)
            state["active_agent_id"] = decision.get("next_agent", "architect")
            state["discussion"].consensus_reached = decision.get("consensus", False)
            summary = decision.get("reasoning", "Continuing deliberation.")

        state["discussion"].contributions.append(CouncilContribution(
            agent_id="orchestrator",
            agent_name="The Swarm Lead",
            content=summary,
            type="moderation"
        ))
        state["iteration_count"] += 1
        return state

    async def architect_node(self, state: ExpertCouncilSwarmState) -> ExpertCouncilSwarmState:
        """Architect: Category Design & Moats."""
        return await self._agent_deliberate("architect", state)

    async def analyst_node(self, state: ExpertCouncilSwarmState) -> ExpertCouncilSwarmState:
        """Analyst: Feasibility & Market Data."""
        return await self._agent_deliberate("analyst", state)

    async def developer_node(self, state: ExpertCouncilSwarmState) -> ExpertCouncilSwarmState:
        """Developer: Implementation & Funnel Tech."""
        return await self._agent_deliberate("developer", state)

    async def qa_node(self, state: ExpertCouncilSwarmState) -> ExpertCouncilSwarmState:
        """QA: Integrity & Risk."""
        return await self._agent_deliberate("qa", state)

    async def _agent_deliberate(self, agent_id: str, state: ExpertCouncilSwarmState) -> ExpertCouncilSwarmState:
        """Common logic for agent deliberation with deep logic injection."""
        agent = self.agents[agent_id]
        logger.info(f"Agent {agent.name} ingesting high-density protocols.")
        
        # Deep injection via Harness
        expert_protocols = self.skill_harness.load_expert_skills(agent_id)
        
        if self.demo_mode:
            resp = self._get_demo_response(agent_id)
        else:
            history = self._format_history(state["discussion"])
            prompt = f"""
            SYSTEM PROTOCOLS:
            {expert_protocols}
            
            ROLE:
            You are {agent.name}, the {agent.role}. {agent.description}
            
            MISSION:
            {state['mission']}
            
            DISCUSSION HISTORY:
            {history}
            
            CONTEXT:
            {json.dumps(state['workspace_context'], indent=2)}
            
            TASK:
            Contribute to the council discussion. 
            MANDATE: You MUST follow the 'PROCEDURAL EXECUTION' steps defined in your SYSTEM PROTOCOLS. 
            Maintain the 'Quiet Luxury' tone: Calm, Expensive, Decisive.
            """
            resp = await self.vertex_ai_client.generate_text(prompt)

        state["discussion"].contributions.append(CouncilContribution(
            agent_id=agent_id,
            agent_name=agent.name,
            content=resp or f"CRITICAL_ERROR: Agent {agent.name} failed to generate a strategic response. Check API Key.",
            type="suggestion"
        ))
        
        if not resp:
            logger.error(f"Agent {agent.name} produced NO output. Mission stalled.")
            
        return state

    async def skill_execution_node(self, state: ExpertCouncilSwarmState) -> ExpertCouncilSwarmState:
        """Node for executing specialized skills (Async)."""
        # In a real swarm, this would trigger actual Skill.execute() calls
        logger.info("Executing swarm skills across N-agents.")
        state["swarm_status"] = "executing"
        return state

    async def synthesizer_node(self, state: ExpertCouncilSwarmState) -> ExpertCouncilSwarmState:
        """Consolidates the swarm's output into a master report."""
        logger.info("Swarm synthesizing final report.")
        
        if self.demo_mode:
            report = f"# SWARM STRATEGY REPORT: {state['mission']}\n\n## ARCHITECTURAL VISION\n{self._get_demo_response('architect')}\n\n## ANALYTIC VALIDATION\n{self._get_demo_response('analyst')}\n\n## TECHNICAL ROADMAP\n{self._get_demo_response('developer')}\n\n## QUALITY ASSURANCE\n{self._get_demo_response('qa')}"
        else:
            history = self._format_history(state["discussion"])
            prompt = f"Synthesize this Expert Council session into a surgical professional report: {history}"
            report = await self.vertex_ai_client.generate_text(prompt)
            
        state["final_report"] = report
        state["swarm_status"] = "finalized"
        return state

    def _get_demo_response(self, agent_id: str) -> str:
        responses = {
            "architect": "We must build a Category of One. The current market is commoditized; our moat will be the cognitive-first alignment of brand and execution.",
            "analyst": "Projected ROI for this GTM is 4.2x within 6 months. I've flagged the Series A founder segment as having the lowest CAC-to-LTV ratio for our current model.",
            "developer": "The tech stack is ready. We'll deploy the funnel using a decoupled Next.js frontend with Supabase Edge Functions for real-time lead scoring.",
            "qa": "Messaging is compliant with industry standards. I recommend a final sweep of the one-liner to ensure it doesn't over-promise on AI capabilities."
        }
        return responses.get(agent_id, "Analyzing...")

    def _format_history(self, discussion: CouncilDiscussion) -> str:
        return "\n".join([f"[{c.agent_name}]: {c.content}" for c in discussion.contributions])

    def _parse_json(self, text: str) -> Dict[str, Any]:
        if not text: return {}
        try:
            cleaned = text.strip()
            if "```json" in cleaned: cleaned = cleaned.split("```json")[1].split("```")[0]
            elif "```" in cleaned: cleaned = cleaned.split("```")[1].split("```")[0]
            return json.loads(cleaned)
        except: return {}

# Helper to create initial swarm state
def create_swarm_session(mission: str, workspace_context: Dict[str, Any]) -> ExpertCouncilSwarmState:
    return {
        "mission": mission,
        "workspace_context": workspace_context,
        "discussion": CouncilDiscussion(
            session_id=f"swarm_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
            mission=mission,
            contributions=[]
        ),
        "iteration_count": 0,
        "max_iterations": 8,
        "swarm_status": "deliberating",
        "active_agent_id": "architect",
        "skills_loaded": {},
        "performance_metrics": {"accuracy": 0.95, "throughput": 1.0, "latency": 0.0},
        "escalation_required": False,
        "final_report": None
    }

# Singleton Swarm
_swarm_instance: Optional[ExpertCouncilSwarm] = None

def get_expert_council_swarm() -> ExpertCouncilSwarm:
    global _swarm_instance
    if _swarm_instance is None:
        _swarm_instance = ExpertCouncilSwarm()
    return _swarm_instance
