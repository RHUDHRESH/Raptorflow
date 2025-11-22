# Analytics Domain Implementation

The Analytics domain provides comprehensive performance tracking, insights generation, and strategic recommendations for marketing campaigns (moves).

## Architecture

### Components

1. **metrics_collector_agent.py** - Collects and normalizes metrics from multiple platforms
2. **insight_agent.py** - Generates insights, detects anomalies, and creates visualizations
3. **analytics_supervisor.py** - Orchestrates the analytics workflow
4. **analytics_graph.py** - LangGraph workflow definition

### Workflow

```
Validate Move → Collect Metrics → Generate Insights → Generate Charts →
Analyze Content → Suggest Pivot → Compile Report → Save Report
```

## Usage

### Option 1: Using the Supervisor (Recommended)

```python
from backend.agents.analytics.analytics_supervisor import analytics_supervisor
from uuid import UUID

# Complete analytics for a move
report = await analytics_supervisor.analyze_move(
    workspace_id=UUID("your-workspace-id"),
    move_id=UUID("your-move-id"),
    time_period_days=30,
    include_charts=True,
    include_content_analysis=True,
    correlation_id="optional-correlation-id"
)

print(report["executive_summary"])
print(f"Insights: {len(report['insights'])}")
print(f"Recommendations: {report['recommendations']}")
```

### Option 2: Using the LangGraph Workflow

```python
from backend.graphs.analytics_graph import analytics_graph
from uuid import UUID

# Run the full workflow
report = await analytics_graph.run_analytics(
    workspace_id=UUID("your-workspace-id"),
    move_id=UUID("your-move-id"),
    time_period_days=30,
    include_charts=True,
    include_content_analysis=True,
    include_pivot_suggestions=True
)
```

### Option 3: Quick Health Check

```python
from backend.agents.analytics.analytics_supervisor import analytics_supervisor
from uuid import UUID

# Quick 24-hour pulse check
pulse = await analytics_supervisor.quick_pulse_check(
    workspace_id=UUID("your-workspace-id"),
    move_id=UUID("your-move-id")
)

print(f"Health Score: {pulse['health_score']}/100")
print(f"Status: {pulse['status']}")
```

### Option 4: Individual Components

```python
from backend.agents.analytics.metrics_collector_agent import metrics_collector_agent
from backend.agents.analytics.insight_agent import insight_agent
from uuid import UUID

# Just collect metrics
metrics = await metrics_collector_agent.collect_metrics(
    workspace_id=UUID("your-workspace-id"),
    move_id=UUID("your-move-id"),
    platforms=["linkedin", "twitter"],
    time_range_days=7
)

# Just generate insights
insights = await insight_agent.analyze_performance(
    workspace_id=UUID("your-workspace-id"),
    move_id=UUID("your-move-id"),
    time_period_days=30
)

# Just generate chart data
charts = await insight_agent.generate_chart_data(
    workspace_id=UUID("your-workspace-id"),
    move_id=UUID("your-move-id"),
    time_period_days=30
)

# Just analyze content performance
content_analysis = await insight_agent.analyze_content_type_performance(
    workspace_id=UUID("your-workspace-id"),
    move_id=UUID("your-move-id")
)

# Just get pivot suggestion
pivot = await insight_agent.suggest_pivot(
    workspace_id=UUID("your-workspace-id"),
    move_id=UUID("your-move-id")
)
```

## Requirements

### Prerequisites

Before running analytics:
1. Move/campaign must exist in the database
2. Move must have at least one published asset
3. Platform integrations should be connected (for real-time metrics)

### Platform Support

The metrics collector supports:
- **LinkedIn** - Page/profile analytics
- **Twitter/X** - Tweet analytics and engagement
- **Instagram** - Post insights and profile metrics
- **YouTube** - Video and channel analytics
- **Email** - Campaign metrics from database

## Output Structure

### Analytics Report

```json
{
  "move_id": "uuid",
  "move_name": "Campaign Name",
  "move_status": "active",
  "analysis_period_days": 30,
  "analyzed_at": "2025-11-22T10:30:00Z",
  "metrics": {
    "platform_metrics": {
      "linkedin": {
        "impressions": 15000,
        "engagements": 450,
        "engagement_rate": 0.03
      }
    },
    "aggregated": {
      "total_impressions": 50000,
      "total_engagements": 1500,
      "engagement_rate": 0.03,
      "total_clicks": 350
    }
  },
  "insights": [
    {
      "type": "opportunity",
      "title": "LinkedIn performing 45% above average",
      "description": "...",
      "recommendation": "Double down on LinkedIn content",
      "priority": "high"
    }
  ],
  "anomalies": [
    {
      "type": "performance_drop",
      "severity": "medium",
      "description": "Twitter engagement dropped 30%"
    }
  ],
  "charts": {
    "time_series": {
      "labels": ["2025-11-01", "2025-11-02", ...],
      "datasets": {
        "impressions": [1000, 1200, ...],
        "engagements": [30, 35, ...]
      }
    },
    "platform_comparison": {...},
    "engagement_funnel": {...}
  },
  "content_analysis": {
    "ranked_by_engagement": [
      {"content_type": "blog_post", "engagement_rate": 0.045},
      {"content_type": "social_post", "engagement_rate": 0.028}
    ]
  },
  "recommendations": [
    "Increase posting frequency on LinkedIn",
    "Experiment with video content"
  ],
  "executive_summary": "..."
}
```

## Error Handling

The system handles:
- **404 errors** - Move not found or has no published content
- **Missing data** - Gracefully degrades with partial data
- **Platform API failures** - Continues with available platforms
- **Invalid inputs** - Returns clear error messages

Example error response:
```json
{
  "error": "Move {move_id} has no published content yet. Complete content creation and execution stages first.",
  "validation_passed": false
}
```

## Caching

- Metrics are cached for **5 minutes**
- Analytics reports are cached for **5 minutes**
- Historical data is permanently stored in `metrics_snapshot` table

## Logging

All operations include structured logging with:
- Correlation IDs for request tracing
- Performance metrics (execution time, data points)
- Error details with context

## Database Tables

### metrics_snapshot
Stores point-in-time metric snapshots:
```sql
{
  "id": UUID,
  "workspace_id": UUID,
  "move_id": UUID,
  "platform": VARCHAR,
  "metrics": JSONB,
  "collected_at": TIMESTAMP
}
```

### analytics_reports (optional)
Stores generated analytics reports:
```sql
{
  "id": UUID,
  "workspace_id": UUID,
  "move_id": UUID,
  "report": JSONB,
  "generated_at": TIMESTAMP
}
```

## Future Enhancements

- [ ] Predictive analytics using ML models
- [ ] Automated A/B test analysis
- [ ] Competitive benchmarking
- [ ] Real-time alerts for anomalies
- [ ] Custom metric definitions
- [ ] Advanced visualization export (PDF, PPT)

## Testing

To test the analytics system:

```python
# Test with a sample move that has published content
from backend.graphs.analytics_graph import analytics_graph
from uuid import UUID

result = await analytics_graph.run_analytics(
    workspace_id=UUID("your-workspace-id"),
    move_id=UUID("your-move-id"),
    time_period_days=7,  # Short period for testing
    include_charts=True,
    include_content_analysis=True
)

assert result["metrics"] is not None
assert len(result["insights"]) > 0
print("✅ Analytics workflow completed successfully")
```

## Integration

The analytics domain integrates with:
- **Master Supervisor** - Routed via `analytics` tier-1 supervisor
- **Content Domain** - Analyzes content performance
- **Execution Domain** - Collects post-publishing metrics
- **Strategy Domain** - Informs campaign pivots and adjustments
