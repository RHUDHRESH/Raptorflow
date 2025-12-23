import json
from typing import Any, List

from backend.services.cache import get_cache

class EpisodicMemory:
    """
    SOTA Episodic Memory Manager.
    Handles short-term session state and conversation history using Redis.
    """
    
    def __init__(self, client: Any = None):
        self.client = client or get_cache()
        self.prefix = "episodic:"

    def _get_key(self, session_id: str) -> str:
        return f"{self.prefix}{session_id}"

    async def add_message(self, session_id: str, message: str):
        """Adds a message to the session's episodic history."""
        key = self._get_key(session_id)
        current_history_raw = await self.client.get(key)
        
        if current_history_raw:
            history = json.loads(current_history_raw)
        else:
            history = []
            
        history.append(message)
        # Limit history size to 20 messages for SOTA performance
        history = history[-20:]
        
        await self.client.set(key, json.dumps(history), ex=3600 * 24) # 24h TTL

    async def get_history(self, session_id: str) -> List[str]:
        """Retrieves the full episodic history for a session."""
        key = self._get_key(session_id)
        raw = await self.client.get(key)
        if raw:
            return json.loads(raw)
        return []

    async def clear(self, session_id: str):
        """Wipes episodic memory for a session."""
        key = self._get_key(session_id)
        await self.client.delete(key)
