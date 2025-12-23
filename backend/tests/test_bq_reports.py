import os

def test_bq_reports_sql_exists():
    """Verify that the Matrix daily reports SQL file exists."""
    assert os.path.exists("backend/ml/matrix_daily_reports.sql")

def test_bq_reports_sql_content():
    """Verify that the SQL file contains expected queries."""
    with open("backend/ml/matrix_daily_reports.sql", "r") as f:
        content = f.read()
        
    assert "daily_cost_report" in content
    assert "daily_performance_matrix" in content
    assert "daily_campaign_roi" in content
    assert "telemetry_stream" in content
    assert "outcomes_stream" in content
