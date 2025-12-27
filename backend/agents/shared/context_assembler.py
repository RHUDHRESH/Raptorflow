from typing import Dict, List

from db import get_db_connection
from memory.semantic_l3 import L3SemanticMemory


class MemoryReaderAgent:
    """
    A04: Returns the top user preferences and workspace constraints.
    """

    async def get_memories(self, workspace_id: str, user_id: str) -> List[str]:
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                query = """
                    SELECT value FROM memories
                    WHERE workspace_id = %s OR (user_id = %s AND scope = 'user')
                    ORDER BY weight DESC, created_at DESC
                    LIMIT 10;
                """
                await cur.execute(query, (workspace_id, user_id))
                rows = await cur.fetchall()
                return [row[0] for row in rows]


class ContextAssemblerAgent:
    """
    A03: Combines Brand Voice + RAG + Learned Memories.
    """

    async def assemble(self, workspace_id: str, user_id: str, goal: str) -> Dict:
        reader = MemoryReaderAgent()
        try:
            memories = await reader.get_memories(workspace_id, user_id)
        except Exception:
            memories = []

        foundation_context = []
        try:
            l3 = L3SemanticMemory()
            foundation_results = await l3.search_foundation(
                workspace_id=workspace_id, query=goal
            )
            foundation_context = [item["content"] for item in foundation_results]
        except Exception:
            foundation_context = []

        # In a full implementation, this would also trigger RAGRetrievalAgent
        return {
            "brand_voice": "ChatGPT simplicity + MasterClass polish + Editorial restraint.",
            "learned_preferences": memories,
            "foundation_context": foundation_context,
            "taboo_words": ["unlock", "game-changer", "delighted", "journey"],
            "base_constraints": ["Surgical brevity", "No conversational filler"],
        }
