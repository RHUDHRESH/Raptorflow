from core.prompts import MarketingFrameworks


def test_marketing_frameworks_contains_cialdini():
    """Verify that MarketingFrameworks has been equipped with Cialdini's principles."""
    assert hasattr(MarketingFrameworks, "CIALDINI_PRINCIPLES")
    principles = MarketingFrameworks.CIALDINI_PRINCIPLES
    assert "Reciprocity" in principles["instructions"]
    assert "Social Proof" in principles["instructions"]
    assert "Scarcity" in principles["instructions"]
