from unittest.mock import MagicMock, patch

import pytest

from backend.services.telemetry import Telemetry


def test_telemetry_captures_agent_metrics():
    """Verify that telemetry calls log essential agent performance data."""
    with patch("backend.services.telemetry.logger.info") as mock_log:
        telemetry = Telemetry()
        telemetry.capture_agent_end(
            agent_name="Researcher", task_id="task_123", duration=0.5, success=True
        )

        mock_log.assert_called_once()
        args, kwargs = mock_log.call_args
        assert "AGENT_END: Researcher" in args[0]
        assert kwargs["extra"]["duration_ms"] == 500.0
        assert kwargs["extra"]["success"] is True


def test_telemetry_captures_tokens():
    """Verify that token usage is correctly formatted in logs."""
    with patch("backend.services.telemetry.logger.info") as mock_log:
        telemetry = Telemetry()
        telemetry.capture_token_usage(
            agent_name="Strategist",
            model="gemini-2.5-flash",
            prompt_tokens=100,
            completion_tokens=50,
        )

        mock_log.assert_called_once()
        kwargs = mock_log.call_args[1]
        assert kwargs["extra"]["total_tokens"] == 150
        assert kwargs["extra"]["model"] == "gemini-2.5-flash"


def test_telemetry_captures_state_transition():
    """Verify lifecycle state transitions are logged."""
    with patch("backend.services.telemetry.logger.info") as mock_log:
        telemetry = Telemetry()
        telemetry.capture_state_transition(
            actor="planner",
            from_state="idle",
            to_state="planning",
            task_id="task_999",
            metadata={"node": "router"},
        )

        mock_log.assert_called_once()
        args, kwargs = mock_log.call_args
        assert "STATE_TRANSITION: planner idle -> planning" in args[0]
        assert kwargs["extra"]["from_state"] == "idle"
        assert kwargs["extra"]["to_state"] == "planning"
