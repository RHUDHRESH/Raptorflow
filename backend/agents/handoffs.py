import logging
from typing import Any, Dict

from swarm import Agent

logger = logging.getLogger("raptorflow.handoffs")


def handoff_to_brief_builder():
    """Handoff the mission to the Brief Builder to formalize requirements."""
    logger.info("Swarm Handoff: -> Brief Builder")
    from agents.brief_builder import get_swarm_brief_builder

    return get_swarm_brief_builder()


def handoff_to_router():
    """Handoff to the Intent Router to classify the request."""
    logger.info("Swarm Handoff: -> Intent Router")
    from agents.router import get_swarm_intent_router

    return get_swarm_intent_router()


def handoff_to_supervisor():
    """Handoff back to the Supervisor for coordination."""
    logger.info("Swarm Handoff: -> Supervisor")
    from agents.supervisor import get_swarm_supervisor

    return get_swarm_supervisor()


def handoff_to_muse():
    """Handoff to Muse for asset generation."""
    logger.info("Swarm Handoff: -> Muse")
    from agents.creatives import get_swarm_muse

    return get_swarm_muse()
