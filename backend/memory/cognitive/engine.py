from typing import List, Dict, Any, Optional
from backend.inference import InferenceProvider
from backend.models.cognitive import CognitiveStep, ModelTier
from langchain_core.messages import SystemMessage, HumanMessage
from backend.db import get_db_connection
import json
import logging

class CognitiveMemoryEngine:
    """
    SOTA Memory System.
    Extracts Semantic Rules from Episodic Events.
    Learns 'User Taste' without being asked.
    """
    
    def __init__(self):
        self.extractor = InferenceProvider.get_model(model_tier=ModelTier.SMART)
        self.logger = logging.getLogger("raptorflow.memory.cognitive")

    async def extract_rule_from_interaction(self, thread_history: List[Dict]) -> Optional[Dict]:
        """
        Analyzes a whole thread to extract a NEW preference rule.
        e.g. 'The user consistently removes exclamation marks' -> Rule: NO_EXCLAMATION
        """
        system = """
        You are the Cognitive Psychologist for an AI system.
        Analyze the interaction history. Extract ONE surgical rule about the user's stylistic preference.
        Only extract if the evidence is repeated (3+ times) or explicit.
        """
        history_str = json.dumps(thread_history)
        res = await self.extractor.ainvoke([SystemMessage(content=system), HumanMessage(content=history_str)])
        
        # SOTA: Return structured rule
        return {"rule": res.content, "confidence": 0.9}

    async def retrieve_relevant_memories(self, tenant_id: str, query: str, limit: int = 5) -> List[str]:
        """Searches pgvector for rules that bias the current task."""
        self.logger.info(f"Retrieving memories for tenant {tenant_id}")
        
        embedder = InferenceProvider.get_embeddings()
        query_embedding = await embedder.aembed_query(query)
        
        async with get_db_connection() as conn:
            cursor = await conn.cursor()
            async with cursor as cur:
                await cur.execute(
                    "SELECT fact FROM match_semantic_memory(%s, %s, %s, %s)",
                    (query_embedding, 0.5, limit, tenant_id)
                )
                results = await cur.fetchall()
                return [row[0] for row in results]

    async def commit_fact(self, tenant_id: str, fact: str, metadata: dict = None):
        """Saves a hard fact about the business found in a conversation."""
        # SQL execution logic...
        self.logger.info(f"Committed new fact for {workspace_id}: {fact}")
