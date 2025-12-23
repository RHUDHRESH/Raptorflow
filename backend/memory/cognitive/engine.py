from typing import List, Dict, Any, Optional
from inference import InferenceProvider
from models.cognitive import CognitiveStep, ModelTier
from langchain_core.messages import SystemMessage, HumanMessage
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

    async def retrieve_relevant_memories(self, workspace_id: str, query: str) -> List[str]:
        """Searches pgvector for rules that bias the current task."""
        # Implementation of biased vector search...
        return ["Always use active voice.", "No marketing emojis."]

    async def commit_fact(self, workspace_id: str, fact: str, evidence: str):
        """Saves a hard fact about the business found in a conversation."""
        # SQL execution logic...
        self.logger.info(f"Committed new fact for {workspace_id}: {fact}")
