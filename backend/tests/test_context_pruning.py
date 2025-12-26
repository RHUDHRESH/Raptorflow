import pytest

from memory.pruning import prune_context


def test_context_pruning_basic():
    """Verify that pruning reduces context size to fit within limit."""
    long_context = ["snippet 1" * 100, "snippet 2" * 100, "snippet 3" * 100]
    # Each snippet is ~900 chars (~225 tokens)
    # Total context is ~675 tokens

    # Prune to max 500 tokens
    pruned = prune_context(long_context, max_tokens=500)

    assert len(pruned) < len(long_context)
    assert len(pruned) == 2  # Should keep first 2


def test_context_pruning_empty():
    assert prune_context([], max_tokens=100) == []


def test_context_pruning_no_op():
    short_context = ["short"]
    assert prune_context(short_context, max_tokens=100) == short_context
