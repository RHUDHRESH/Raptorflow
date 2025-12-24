import pytest

from backend.memory.pruning import MemoryDecayPolicy


def test_decay_policy_simple_pruning():
    """Verify that decay policy prunes based on count."""
    policy = MemoryDecayPolicy(max_items=3)
    items = ["item1", "item2", "item3", "item4"]
    pruned = policy.prune_by_count(items)
    assert len(pruned) == 3
    assert pruned == ["item2", "item3", "item4"]  # Keeps newest (last)


def test_decay_policy_token_pruning():
    """Verify that decay policy prunes based on tokens."""
    policy = MemoryDecayPolicy(max_tokens=10)  # 10 tokens ~ 40 chars
    items = ["This is a long string that exceeds limit", "Short"]
    pruned = policy.prune_by_tokens(items)
    assert len(pruned) == 1
    assert pruned == ["Short"]
