"""
README for Competitor Intelligence Integration
"""

# Competitor Intelligence for Swarm Agent Background

This comprehensive competitor intelligence system provides advanced tracking, analysis, and monitoring capabilities for swarm operations. The implementation includes over 3,000 lines of code with full integration into the swarm framework.

## Architecture Overview

### Core Components

1. **Models** (`backend/models/swarm.py`)
   - `CompetitorProfile` - Detailed competitor information
   - `CompetitorGroup` - Competitor categorization
   - `CompetitorInsight` - Individual intelligence findings
   - `CompetitorAnalysis` - Comprehensive analysis results
   - Extended `SwarmState` with competitor tracking fields

2. **Agent** (`backend/agents/specialists/swarm_competitor_intelligence.py`)
   - `SwarmCompetitorIntelligenceAgent` - Specialist for competitor operations
   - Discovery, analysis, insight tracking, and grouping capabilities

3. **Memory** (`backend/memory/swarm_l1.py`)
   - Extended L1 memory manager with competitor storage
   - Redis-based persistence for profiles, insights, and analyses

4. **Services** (`backend/services/competitor_monitoring.py`)
   - `CompetitorMonitoringService` - Automated monitoring and alerting
   - `CompetitorAnalysisService` - Deep analysis capabilities

5. **Node** (`backend/nodes/competitor_intelligence.py`)
   - `CompetitorIntelligenceNode` - Swarm integration point
   - Handles routing and operation orchestration

6. **Integration Layer** (`backend/competitor_intelligence/`)
   - Unified manager interface
   - Configuration and utilities
   - Swarm adapters

## Key Features

### Discovery & Tracking
- Automated competitor discovery
- Manual competitor addition
- Profile management with confidence scoring
- Competitor grouping and categorization

### Analysis Capabilities
- SWOT analysis
- Competitive positioning analysis
- Market gap identification
- Benchmarking and comparison
- Threat level assessment

### Monitoring & Intelligence
- Real-time monitoring with configurable frequencies
- Automated insight generation
- Alert system for significant changes
- Historical tracking and trend analysis

### Integration Points
- Seamless swarm orchestrator integration
- Intent routing for competitor-related queries
- Context enhancement for swarm operations
- Unified API for all competitor operations

## Usage Examples

### Basic Discovery
```python
from competitor_intelligence import CompetitorIntelligenceManager

manager = CompetitorIntelligenceManager("thread_123")
result = await manager.discover_competitors({
    "shared_knowledge": {"objective": "Analyze SaaS competitors"},
    "competitive_landscape_summary": "Focus on project management tools"
})
```

### Analysis Operations
```python
# Analyze specific competitors
analysis = await manager.analyze_competitors(["comp_1", "comp_2"])

# SWOT analysis
swot = await manager.perform_swot_analysis()

# Identify market gaps
gaps = await manager.identify_competitive_gaps()
```

### Monitoring Setup
```python
# Start monitoring
await manager.start_monitoring(
    competitor_ids=["comp_1", "comp_2"],
    frequency="daily"
)

# Generate intelligence report
report = await manager.generate_intelligence_report()
```

### Swarm Integration
```python
# Enhanced swarm state with competitor context
state = await adapter.enhance_swarm_state(swarm_state)

# Route to competitor intelligence
result = await adapter.route_to_competitor_intelligence(state)
```

## Configuration

### Default Settings
- Monitoring frequency: 24 hours
- Confidence threshold: 0.3
- Max competitors per thread: 100
- Max insights per thread: 1000

### Custom Configuration
```python
config = {
    "monitoring_frequency": 12,  # hours
    "confidence_threshold": 0.7,
    "max_competitors_per_analysis": 15
}

manager = CompetitorIntelligenceManager("thread_123", config)
```

## Data Models

### CompetitorProfile
```python
{
    "id": "comp_abc123",
    "name": "Competitor Name",
    "competitor_type": "direct",
    "threat_level": "medium",
    "website": "https://example.com",
    "market_share": 15.5,
    "target_audience": ["enterprise", "startup"],
    "key_features": ["feature1", "feature2"],
    "pricing_model": "subscription",
    "strengths": ["strong brand"],
    "weaknesses": ["high price"],
    "confidence_score": 0.8
}
```

### CompetitorInsight
```python
{
    "id": "insight_xyz789",
    "competitor_id": "comp_abc123",
    "insight_type": "pricing_change",
    "title": "Price Increase Detected",
    "description": "Competitor increased prices by 10%",
    "impact_assessment": "medium",
    "confidence": 0.9,
    "source": "web_scraping"
}
```

## API Reference

### Manager Operations
- `discover_competitors(context)` - Find new competitors
- `analyze_competitors(ids)` - Analyze specific competitors
- `start_monitoring(ids, frequency)` - Begin monitoring
- `stop_monitoring()` - Stop all monitoring
- `generate_intelligence_report()` - Create comprehensive report
- `add_competitor_manually(data)` - Add competitor manually
- `get_competitor_profiles(ids)` - Retrieve profiles
- `add_competitor_insight(data)` - Add new insight

### Swarm Integration
- `enhance_swarm_state(state)` - Add competitor context
- `route_to_competitor_intelligence(state)` - Handle competitor operations
- `get_swarm_context()` - Get competitor context for swarm

## Testing

Comprehensive test suite included:
- Model validation tests
- Agent operation tests
- Memory management tests
- Service functionality tests
- Integration tests

Run tests:
```bash
pytest backend/tests/test_competitor_intelligence.py -v
```

## Performance Considerations

### Memory Usage
- Profiles stored in Redis hashes for efficient access
- Insights stored as JSON arrays with pagination support
- Automatic cleanup of old data based on retention policies

### Monitoring Overhead
- Configurable monitoring frequencies to balance timeliness vs. resource usage
- Batch processing for multiple competitors
- Efficient change detection algorithms

### Scalability
- Thread-based isolation for concurrent operations
- Async/await pattern throughout for non-blocking operations
- Resource pooling for Redis connections

## Security & Privacy

- All competitor data stored with thread isolation
- Configurable data retention policies
- Source attribution for all insights
- Confidence scoring to indicate reliability

## Future Enhancements

### Planned Features
- Machine learning for predictive analysis
- Integration with external data sources
- Advanced visualization dashboards
- Real-time alert notifications
- Competitive intelligence APIs

### Extension Points
- Custom analysis plugins
- Additional data source integrations
- Custom alerting rules
- Specialized competitor types

## Troubleshooting

### Common Issues
1. **Redis Connection Failures**: Check Redis configuration and connectivity
2. **Memory Limits**: Adjust MAX_PROFILES_PER_THREAD and MAX_INSIGHTS_PER_THREAD
3. **Monitoring Not Starting**: Verify competitor IDs exist and frequency is valid
4. **Analysis Timeouts**: Reduce MAX_COMPETITORS_PER_ANALYSIS for large datasets

### Debug Logging
Enable debug logging for detailed operation traces:
```python
import logging
logging.getLogger("raptorflow.competitor_intelligence").setLevel(logging.DEBUG)
```

## Support

For issues and questions:
- Check the comprehensive test suite for usage examples
- Review the configuration options in `config.py`
- Examine the adapter patterns in `adapters.py` for integration guidance
