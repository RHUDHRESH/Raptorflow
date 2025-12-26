from typing import Any, List

from memory.policy import DEFAULT_IMPORTANCE, get_memory_policy


def count_tokens_heuristic(text: str) -> int:
    """SOTA Heuristic for token counting (approx 4 chars per token)."""
    return len(text) // 4


def prune_context(
    context: List[str],
    max_tokens: int | None = None,
    workspace_importance: str = DEFAULT_IMPORTANCE,
    agent_importance: str = DEFAULT_IMPORTANCE,
) -> List[str]:
    """
    SOTA Context Pruning (Taulli Pattern).
    Ensures that the total business context fits within the LLM's surgical window.
    Prioritizes early snippets (assuming they are most relevant/recent).
    """
    if not context:
        return []

    if max_tokens is None:
        policy = get_memory_policy()
        max_tokens = policy.resolve(workspace_importance, agent_importance).max_tokens

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


class MemoryDecayPolicy:
    """
    SOTA Memory Decay Policy.
    Implements rules for pruning and compressing short-term state.
    Supports count-based and token-based decay.
    """

    def __init__(
        self,
        max_items: int | None = None,
        max_tokens: int | None = None,
        workspace_importance: str = DEFAULT_IMPORTANCE,
        agent_importance: str = DEFAULT_IMPORTANCE,
    ):
        policy = get_memory_policy()
        rule = policy.resolve(workspace_importance, agent_importance)
        self.max_items = rule.max_items if max_items is None else max_items
        self.max_tokens = rule.max_tokens if max_tokens is None else max_tokens

    def prune_by_count(self, items: List[Any]) -> List[Any]:
        """Prunes a list of items to fit within max_items, keeping the newest."""
        if not items:
            return []
        return items[-self.max_items :]

    def prune_by_tokens(self, items: List[str]) -> List[str]:
        """Prunes a list of strings to fit within max_tokens."""
        if not items:
            return []

        pruned_list = []
        current_tokens = 0

        # SOTA: Process from newest to oldest (reverse)
        for snippet in reversed(items):
            tokens = count_tokens_heuristic(snippet)
            if current_tokens + tokens <= self.max_tokens:
                pruned_list.insert(0, snippet)  # Keep order
                current_tokens += tokens
            else:
                break

        return pruned_list
