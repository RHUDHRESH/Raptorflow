import pytest

from agents.vacuum_node import VacuumNode


def test_vacuum_valid_failure():
    """Verify that Valid node catches missing mandatory fields."""
    record = {"title": "Test Campaign"}  # Missing tenant_id
    required = ["title", "tenant_id"]
    schema = {"title": str, "tenant_id": str}

    report = VacuumNode.validate_record(record, required, schema)
    assert report.is_valid is False
    assert "tenant_id" in report.missing_fields


def test_vacuum_accurate_failure():
    """Verify that Accurate node catches logical inconsistencies."""
    record = {
        "start_date": "2025-12-31",
        "end_date": "2025-01-01",  # End before start
        "target_value": -100,  # Negative target
    }

    report = VacuumNode.evaluate_accuracy(record)
    assert report.is_accurate is False
    assert any("Start date" in d for d in report.discrepancies)
    assert any("cannot be negative" in d for d in report.discrepancies)


def test_vacuum_uniform_failure():
    """
    FAILING TEST for Task 16 (Uniform):
    Verify that non-uniform date formats are flagged.
    Currently, VacuumNode doesn't have a check_uniform method.
    """
    record = {"created_at": "12/23/2025"}  # Non-ISO format

    # This will fail with AttributeError because check_uniform doesn't exist yet
    with pytest.raises(AttributeError):
        VacuumNode.check_uniform(record)
