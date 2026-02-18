"""Autonomous research agent package.

Core modules:
- research_agent.py: main agent loop and state machine
- research_log.py: structured JSON logging utilities
- search_tools.py: web search tool integrations
"""

from .research_agent import ResearchAgent, ResearchAgentConfig

__all__ = ["ResearchAgent", "ResearchAgentConfig"]
