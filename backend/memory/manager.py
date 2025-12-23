import json
import logging
from typing import Any, Dict, List, Optional
from backend.memory.short_term import L1ShortTermMemory
from backend.memory.episodic_l2 import L2EpisodicMemory
from backend.memory.semantic_l3 import L3SemanticMemory
from backend.inference import InferenceProvider

logger = logging.getLogger("raptorflow.memory.manager")

class MemoryManager:
    """
    SOTA Memory Manager.
    Orchestrates L1 (Short-Term), L2 (Episodic), and L3 (Semantic) memory tiers.
    Ensures unified trace storage and multi-tier retrieval for agentic systems.
    """

    def __init__(self):
        self.l1 = L1ShortTermMemory()
        self.l2 = L2EpisodicMemory()
        self.l3 = L3SemanticMemory()

    async def store_trace(
        self, 
        workspace_id: str, 
        thread_id: str, 
        content: Any, 
        important: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Stores an agent trace across memory tiers.
        Always stores in L1 for immediate recall.
        Conditionally stores in L2 (Episodic) if marked as 'important'.
        """
        try:
            # 1. Store in L1 (Redis)
            l1_key = f"trace:{thread_id}"
            await self.l1.store(l1_key, content, ttl=3600 * 24) # 24h default TTL
            
            # 2. If important, store in L2 (pgvector)
            if important:
                logger.info(f"Storing important trace from thread {thread_id} in L2 episodic memory.")
                
                # Generate embedding for the content
                embedder = InferenceProvider.get_embeddings()
                text_content = json.dumps(content)
                embedding = await embedder.aembed_query(text_content)
                
                await self.l2.store_episode(
                    workspace_id=workspace_id,
                    content=text_content,
                    embedding=embedding,
                    metadata=metadata
                )
            
            return True
        except Exception as e:
            logger.error(f"MemoryManager store_trace failed: {e}")
            return False

    async def retrieve_context(
        self, 
        workspace_id: str, 
        query: str, 
        thread_id: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieves unified context from all relevant memory tiers.
        """
        context = {
            "short_term": [],
            "episodic": [],
            "semantic": []
        }
        
        try:
            # 1. Try L1 if thread_id provided
            if thread_id:
                l1_data = await self.l1.retrieve(f"trace:{thread_id}")
                if l1_data:
                    context["short_term"] = [l1_data]
            
            # 2. Search L2 and L3
            embedder = InferenceProvider.get_embeddings()
            query_embedding = await embedder.aembed_query(query)
            
            context["episodic"] = await self.l2.recall_similar(workspace_id, query_embedding, limit=3)
            context["semantic"] = await self.l3.search_foundation(workspace_id, query, limit=3)
            
            return context
        except Exception as e:
            logger.error(f"MemoryManager retrieve_context failed: {e}")
            return context
