import pytest

from agents.shared.handoff import HandoffProtocol


def test_handoff_message_creation():
    """Test creating a handoff packet."""
    handoff = HandoffProtocol.create_packet(
        source="DriftAnalyzer",
        target="Governor",
        context={"drift_detected": True},
        priority="high",
    )
    assert handoff["source"] == "DriftAnalyzer"
    assert handoff["priority"] == "high"
    assert "drift_detected" in handoff["context"]


def test_handoff_validation():
    """Test validating a handoff packet."""
    valid_packet = {"source": "A", "target": "B", "context": {}, "priority": "normal"}
    assert HandoffProtocol.validate(valid_packet) is True

    invalid_packet = {"source": "A"}
    assert HandoffProtocol.validate(invalid_packet) is False
