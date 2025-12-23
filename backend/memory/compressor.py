import logging
from typing import List, Any
from backend.db import summarize_recursively
from backend.inference import InferenceProvider
from backend.memory.pruning import count_tokens_heuristic

logger = logging.getLogger("raptorflow.memory.compressor")

class ContextWindowCompressor:
    """
    SOTA Context Window Compressor.
    Uses recursive summarization and surgical pruning to fit context into LLM limits.
    Ensures maximum information density for agentic thought-loops.
    """

    def __init__(self, max_tokens: int = 4000, model_tier: str = "fast"):
        self.max_tokens = max_tokens
        self.model_tier = model_tier

    async def compress(self, text: str) -> str:
        """Compresses a single large text string if it exceeds max_tokens."""
        tokens = count_tokens_heuristic(text)
        
        if tokens <= self.max_tokens:
            return text
            
        logger.info(f"Compressor: text ({tokens} tokens) exceeds limit ({self.max_tokens}). Summarizing...")
        
        try:
            llm = InferenceProvider.get_model(model_tier=self.model_tier)
            return await summarize_recursively(text, llm, max_tokens=self.max_tokens)
        except Exception as e:
            logger.error(f"Context compression failed: {e}")
            # Fallback: Hard prune
            return text[:self.max_tokens * 4]

    async def compress_list(self, items: List[str]) -> List[str]:
        """Compresses a list of context snippets by pruning and potentially summarizing."""
        # For now, we use simple pruning as defined in pruning.py but could be more advanced
        from backend.memory.pruning import MemoryDecayPolicy
        policy = MemoryDecayPolicy(max_tokens=self.max_tokens)
        return policy.prune_by_tokens(items)
