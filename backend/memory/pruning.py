from typing import List

def count_tokens_heuristic(text: str) -> int:
    """SOTA Heuristic for token counting (approx 4 chars per token)."""
    return len(text) // 4

def prune_context(context: List[str], max_tokens: int = 4000) -> List[str]:
    """
    SOTA Context Pruning (Taulli Pattern).
    Ensures that the total business context fits within the LLM's surgical window.
    Prioritizes early snippets (assuming they are most relevant/recent).
    """
    if not context:
        return []
        
    pruned_list = []
    current_tokens = 0
    
    for snippet in context:
        snippet_tokens = count_tokens_heuristic(snippet)
        if current_tokens + snippet_tokens <= max_tokens:
            pruned_list.append(snippet)
            current_tokens += snippet_tokens
        else:
            # SOTA: Stop adding once limit is reached
            break
            
    return pruned_list
