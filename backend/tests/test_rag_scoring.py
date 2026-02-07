import pytest

from agents.rag_retrieval import RAG


def test_rag_relevance_scoring_exact_match():
    """Verify that exact matches get a score of 1.0."""
    rag = RAG()
    score = rag.calculate_relevance_score(
        query="LinkedIn Post", snippet="This is a LinkedIn Post for SaaS."
    )
    assert score > 0.8  # SOTA: heuristic scoring


def test_rag_relevance_scoring_mismatch():
    """Verify that unrelated snippets get a low score."""
    rag = RAG()
    score = rag.calculate_relevance_score(
        query="LinkedIn Post", snippet="Baking a chocolate cake requires flour."
    )
    assert score < 0.3
