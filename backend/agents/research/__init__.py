"""
Research agents for building Ideal Customer Profiles (ICPs).

This module contains:
- Customer Intelligence Supervisor: Orchestrates research workflow
- ICP Builder Agent: Creates structured ICP profiles
- Tag Assignment Agent: Assigns psychographic/demographic tags
- Persona Narrative Agent: Generates human narratives
- Pain Point Miner Agent: Categorizes pain points
"""

from backend.agents.research.customer_intelligence_supervisor import (
    customer_intelligence_supervisor,
)
from backend.agents.research.icp_builder_agent import icp_builder_agent
from backend.agents.research.tag_assignment_agent import tag_assignment_agent
from backend.agents.research.persona_narrative_agent import persona_narrative_agent
from backend.agents.research.pain_point_miner_agent import pain_point_miner_agent

__all__ = [
    "customer_intelligence_supervisor",
    "icp_builder_agent",
    "tag_assignment_agent",
    "persona_narrative_agent",
    "pain_point_miner_agent",
]
