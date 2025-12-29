import logging
from typing import Any, AsyncIterator, Dict

from swarm import Swarm

from models.cognitive import AgentMessage

logger = logging.getLogger("raptorflow.agents.swarm_streaming")


async def swarm_stream_processor(
    client: Swarm, agent: Any, messages: list, context_variables: dict
) -> AsyncIterator[Dict[str, Any]]:
    """
    SOTA Streaming Wrapper for OpenAI Swarm.
    Yields events as they happen in the swarm.
    """
    logger.info(f"Initiating swarm stream for agent: {agent.name}")

    # Note: Swarm library's stream mode returns a generator
    stream = client.run(
        agent=agent,
        messages=messages,
        context_variables=context_variables,
        stream=True,
        debug=True,
    )

    for chunk in stream:
        if "content" in chunk:
            yield {"type": "content", "delta": chunk["content"], "agent": agent.name}
        if "sender" in chunk:
            yield {
                "type": "handoff",
                "from": chunk["sender"],
                "to": chunk.get("recipient"),
            }
        if "delim" in chunk and chunk["delim"] == "end":
            yield {"type": "end"}
