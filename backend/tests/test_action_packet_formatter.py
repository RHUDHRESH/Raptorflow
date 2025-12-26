import pytest

from agents.specialists.move_generator import ActionItem, WeeklyMove
from core.formatter import ActionPacketFormatter


def test_action_packet_formatting_logic():
    """
    Phase 54: Verify that the ActionPacketFormatter transforms moves correctly.
    """
    move = WeeklyMove(
        week_number=1,
        title="Brand Extraction",
        description="Extract brand kit from context.",
        action_items=[
            ActionItem(
                task="Analyze text", owner="researcher", tool_requirements=["Firecrawl"]
            )
        ],
        desired_outcome="Structured JSON.",
    )

    packets = ActionPacketFormatter.format_packet(move)

    assert len(packets) == 1
    assert packets[0]["task"] == "Analyze text"
    assert packets[0]["tools"] == ["Firecrawl"]
    assert "MOVE-W1" in packets[0]["industrial_id"]

    md = ActionPacketFormatter.to_markdown(packets)
    assert "⚡ INDUSTRIAL ACTION PACKET" in md
    assert "Analyze text" in md
