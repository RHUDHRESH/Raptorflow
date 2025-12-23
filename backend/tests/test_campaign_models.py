import pytest
from datetime import datetime, timedelta
from backend.models.campaigns import GanttItem, GanttChart

def test_gantt_item_validation():
    """Verify that GanttItem handles dates correctly."""
    start = datetime.now()
    end = start + timedelta(days=30)
    
    item = GanttItem(
        task="Launch LinkedIn Ads",
        start_date=start,
        end_date=end,
        dependency_ids=[]
    )
    
    assert item.task == "Launch LinkedIn Ads"
    assert item.end_date > item.start_date

def test_gantt_chart_structure():
    start = datetime.now()
    item1 = GanttItem(task="Setup", start_date=start, end_date=start + timedelta(days=7))
    item2 = GanttItem(task="Execution", start_date=start + timedelta(days=7), end_date=start + timedelta(days=14))
    
    chart = GanttChart(items=[item1, item2])
    assert len(chart.items) == 2
