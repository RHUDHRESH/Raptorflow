from core.prompts import MarketingFrameworks


def test_marketing_frameworks_contains_positioning_canvas():
    """Verify that MarketingFrameworks has been equipped with Positioning Canvas."""
    assert hasattr(MarketingFrameworks, "POSITIONING_CANVAS")
    canvas = MarketingFrameworks.POSITIONING_CANVAS
    assert "Category" in canvas["instructions"]
    assert "Unique Value" in canvas["instructions"]
    assert "Proof" in canvas["instructions"]
