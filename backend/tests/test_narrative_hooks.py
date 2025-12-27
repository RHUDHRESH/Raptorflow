from core.prompts import MarketingFrameworks


def test_marketing_frameworks_contains_narrative_hook():
    """Verify that MarketingFrameworks has been equipped with Narrative Hook."""
    assert hasattr(MarketingFrameworks, "NARRATIVE_HOOK")
    hook = MarketingFrameworks.NARRATIVE_HOOK
    assert "instructions" in hook
    assert "Why Now" in hook["description"]
    assert "The Catalyst" in hook["instructions"]
