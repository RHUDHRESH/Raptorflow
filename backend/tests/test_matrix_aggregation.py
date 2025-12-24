from unittest.mock import MagicMock

import pytest

from backend.agents.supervisor import HierarchicalSupervisor


def test_aggregate_findings_logic():
    """Test that the supervisor can aggregate multiple specialist findings."""
    mock_llm = MagicMock()
    supervisor = HierarchicalSupervisor(
        llm=mock_llm, team_members=[], system_prompt="..."
    )

    findings = [
        {"analysis_summary": "Drift detected in zone A", "drift_detected": True},
        {"analysis_summary": "Budget is healthy", "risk_level": "low"},
    ]

    summary = supervisor.aggregate_findings(findings)
    assert "Drift detected" in summary
    assert "Budget is healthy" in summary
    assert "SUMMARY" in summary
