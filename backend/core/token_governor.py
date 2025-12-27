import logging
from typing import Optional

from memory.short_term import L1ShortTermMemory

logger = logging.getLogger("raptorflow.core.token_governor")


class TokenGovernor:
    """
    SOTA Token Budget Manager.
    Prevents agentic loops from burning excessive budget.
    """

    def __init__(self, memory: Optional[L1ShortTermMemory] = None):
        self.memory = memory or L1ShortTermMemory()
        # Default limits
        self.DAILY_TOKEN_CAP = 1_000_000  # 1M tokens
        self.RUN_TOKEN_CAP = 100_000  # 100k tokens per graph run

    async def check_budget(self, workspace_id: str, requested_tokens: int = 0) -> bool:
        """
        Checks if the workspace has enough budget for the request.
        """
        key = f"token_usage:{workspace_id}"
        current_usage = await self.memory.retrieve(key) or 0

        if int(current_usage) + requested_tokens > self.DAILY_TOKEN_CAP:
            logger.warning(f"Workspace {workspace_id} exceeded DAILY token budget!")
            return False

        return True

    async def record_usage(self, workspace_id: str, tokens: int):
        """
        Records token consumption.
        """
        key = f"token_usage:{workspace_id}"
        await self.memory.increment(key, tokens)
        logger.info(f"Recorded {tokens} tokens for Workspace {workspace_id}")


def get_token_governor() -> TokenGovernor:
    return TokenGovernor()
