import pytest

from graphs.swarm_orchestrator import SwarmController


def test_aggregate_findings_logic():
    """Test that the supervisor can aggregate multiple specialist findings."""
    supervisor = SwarmController()

    findings = [
        {"analysis_summary": "Drift detected in zone A", "drift_detected": True},
        {"analysis_summary": "Budget is healthy", "risk_level": "low"},
    ]

    summary = supervisor.aggregate_findings(findings)
    assert "Drift detected" in summary
    assert "Budget is healthy" in summary
    assert "SUMMARY" in summary
