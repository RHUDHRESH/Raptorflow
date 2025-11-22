"""
Agent swarm orchestration module for RaptorFlow.

This module provides multi-agent collaboration capabilities:
- Expert agent registry with specialized capabilities
- Debate-driven consensus mechanisms
- Multi-perspective problem solving
- Collaborative refinement processes

Components:
- ExpertAgentRegistry: Registry of hyper-specialized agents
- AgentDebateOrchestrator: Orchestrates multi-agent debates and consensus
"""

from backend.agents.swarm.expert_agent_registry import ExpertAgentRegistry
from backend.agents.swarm.agent_debate_orchestrator import AgentDebateOrchestrator

__all__ = [
    "ExpertAgentRegistry",
    "AgentDebateOrchestrator",
]
