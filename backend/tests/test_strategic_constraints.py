import pytest

from core.constraints import ConstraintChecker, ResourceLimits


def test_constraint_checker_logic():
    """
    Phase 55: Verify that the ConstraintChecker flags violations correctly.
    """
    limits = ResourceLimits(
        budget_usd=5000.0,
        time_weeks=8,  # Limit to 2 months
        agent_slots=5,
        allowed_tools=["Firecrawl", "Search"],
    )

    # 1. Failing plan (3 months = 12 weeks)
    long_plan = {"monthly_arcs": [{"month": 1}, {"month": 2}, {"month": 3}]}
    audit = ConstraintChecker.audit_plan(long_plan, limits)
    assert audit.is_feasible is False
    assert "exceeds limit" in audit.violations[0]

    # 2. Passing plan (2 months = 8 weeks)
    valid_plan = {"monthly_arcs": [{"month": 1}, {"month": 2}]}
    audit_valid = ConstraintChecker.audit_plan(valid_plan, limits)
    assert audit_valid.is_feasible is True
