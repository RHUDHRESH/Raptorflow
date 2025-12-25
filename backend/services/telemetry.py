import time

from backend.utils.logger import logger


class Telemetry:
    """
    SOTA Telemetry Service for Cognitive Intelligence Engine.
    Tracks agent latency, token usage, and graph traversal success.
    """

    @staticmethod
    def capture_agent_start(agent_name: str, task_id: str):
        logger.info(
            f"AGENT_START: {agent_name}",
            extra={
                "event_type": "agent_start",
                "agent_name": agent_name,
                "task_id": task_id,
                "start_time": time.time(),
            },
        )

    @staticmethod
    def capture_agent_end(
        agent_name: str, task_id: str, duration: float, success: bool
    ):
        logger.info(
            f"AGENT_END: {agent_name}",
            extra={
                "event_type": "agent_end",
                "agent_name": agent_name,
                "task_id": task_id,
                "duration_ms": duration * 1000,
                "success": success,
            },
        )

    @staticmethod
    def capture_token_usage(
        agent_name: str, model: str, prompt_tokens: int, completion_tokens: int
    ):
        logger.info(
            f"TOKEN_USAGE: {agent_name} ({model})",
            extra={
                "event_type": "token_usage",
                "agent_name": agent_name,
                "model": model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
        )


def get_telemetry() -> Telemetry:
    return Telemetry()
