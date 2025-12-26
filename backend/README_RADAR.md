# RaptorFlow Radar Implementation

## Overview

Radar is RaptorFlow's competitive intelligence system that transforms web scraping data into actionable competitive signals. It provides real-time monitoring of competitor activities, market trends, and strategic opportunities.

## Architecture

### Core Services

1. **SignalExtractionService** - Extracts meaningful signals from scraped content
2. **SignalProcessingService** - Clusters, deduplicates, and scores signals
3. **RadarIntegrationService** - Maps signals to campaign moves and generates dossiers
4. **RadarAnalyticsService** - Provides trend analysis and market intelligence
5. **RadarSchedulerService** - Manages automated scanning and monitoring
6. **RadarNotificationService** - Handles alerts and notifications
7. **RadarService** - Main orchestration service

### API Endpoints

#### `/v1/radar/scan`
- `POST /recon` - Perform competitive reconnaissance scan
- `POST /dossier` - Generate intelligence dossier

#### `/v1/radar/analytics`
- `GET /trends` - Get signal trends over time
- `GET /competitors` - Analyze competitor patterns
- `GET /intelligence` - Get comprehensive market intelligence
- `GET /opportunities` - Identify strategic opportunities

#### `/v1/radar/scheduler`
- `POST /start` - Start automated scanning
- `POST /stop` - Stop automated scanning
- `POST /scan/manual` - Schedule manual scan
- `GET /health` - Get source health status
- `GET /status` - Get scheduler status

#### `/v1/radar/notifications`
- `POST /process` - Process signals for notifications
- `GET /digest/daily` - Get daily digest

## Signal Categories

### Offer
- Pricing changes, plan updates, value propositions
- **Patterns**: Pricing mentions, plan names, discount offers, guarantees

### Hook
- Marketing angles, value propositions, attention-grabbing content
- **Patterns**: Superlatives, pain points, secret revelations, authority claims

### Proof
- Customer evidence, testimonials, case studies, results
- **Patterns**: Customer mentions, quantitative results, social proof

### CTA
- Call-to-action language, urgency tactics, conversion optimization
- **Patterns**: Action verbs, urgency/scarcity, low-friction actions

### Objection
- Customer objections, concerns, risk factors
- **Patterns**: Price objections, complexity concerns, time/risk issues

### Trend
- Market movements, launches, updates, business changes
- **Patterns**: New launches, partnerships, funding, market shifts

## Signal Strength

- **High**: Strong evidence, recent activity, high confidence
- **Medium**: Moderate evidence, some recent activity
- **Low**: Limited evidence, older activity

## Signal Freshness

- **Fresh**: 0-7 days old
- **Warm**: 8-30 days old
- **Stale**: 31-90 days old

## Database Schema

### Core Tables

- `radar_sources` - Source configuration and health
- `radar_signals` - Core signal entities
- `radar_signal_evidence` - Evidence supporting signals
- `radar_signal_clusters` - Clustered similar signals
- `radar_signal_move_mappings` - Signal-to-move relationships
- `radar_dossiers` - Intelligence dossiers
- `radar_scan_jobs` - Background scan jobs

## Integration Points

### Existing Infrastructure

- **AdvancedCrawler** - Web scraping with Firecrawl/Jina/BeautifulSoup
- **CrawlCache** - Content hashing and freshness tracking
- **CompetitorMonitoringService** - Scheduled monitoring
- **Vertex AI** - LLM-powered signal analysis
- **PostgreSQL** - Signal storage and retrieval

### Campaign Integration

- **Moves** - Signal-to-move mapping for campaign optimization
- **Matrix** - Strategic planning with competitive insights
- **Blackbox** - Experiment generation from signal intelligence

## Configuration

### Environment Variables

```bash
# Required for signal extraction
FIRECRAWL_API_KEY=your_firecrawl_key
VERTEX_AI_PROJECT_ID=your_project_id
VERTEX_AI_LOCATION=us-central1

# Optional for enhanced features
REDIS_URL=redis://localhost:6379
UPSTASH_REDIS_URL=your_upstash_url
```

### Notification Rules

```json
{
  "high_strength_signals": {
    "enabled": true,
    "threshold": 1,
    "categories": ["offer", "hook", "trend"]
  },
  "competitor_activity_spikes": {
    "enabled": true,
    "threshold": 5,
    "window_hours": 24
  },
  "pricing_changes": {
    "enabled": true,
    "threshold": 1,
    "strength_filter": ["high", "medium"]
  }
}
```

## Usage Examples

### Manual Scan

```python
# Perform recon scan
response = await client.post("/v1/radar/scan/recon", json={
    "icp_id": "icp-123",
    "source_urls": [
        "https://competitor.com/pricing",
        "https://competitor.com/about"
    ]
})

signals = response.json()
print(f"Found {len(signals)} signals")
```

### Get Market Intelligence

```python
# Get comprehensive intelligence
response = await client.get("/v1/radar/analytics/intelligence")
intelligence = response.json()

print(f"Market activity: {intelligence['market_dynamics']['activity_level']}")
print(f"Top competitors: {intelligence['competitor_analysis']['market_leaders']}")
```

### Start Automated Monitoring

```python
# Start scheduler
await client.post("/v1/radar/scheduler/start")

# Check status
status = await client.get("/v1/radar/scheduler/status")
print(f"Scheduler active: {status['is_active']}")
```

## Performance Considerations

### Signal Processing

- **Batching**: Process signals in batches of 100-500
- **Caching**: Cache content hashes for change detection
- **Indexing**: Proper database indexes on tenant_id, category, created_at

### Scaling

- **Horizontal**: Multiple scheduler instances for different tenants
- **Vertical**: Increase crawler concurrency for high-volume sources
- **Storage**: Archive old signals (>90 days) to cold storage

### Monitoring

- **Source Health**: Automatic health scoring and alerting
- **Signal Velocity**: Monitor signal generation rates
- **Error Rates**: Track extraction and processing failures

## Troubleshooting

### Common Issues

1. **Low Signal Detection**
   - Check source health scores
   - Verify scraping tools are working
   - Review pattern matching rules

2. **High False Positives**
   - Adjust similarity thresholds
   - Review signal categorization
   - Fine-tune strength scoring

3. **Performance Issues**
   - Monitor database query performance
   - Check crawler concurrency limits
   - Review cache hit rates

### Debug Mode

Enable debug logging for detailed signal processing:

```python
import logging
logging.getLogger("raptorflow.signal_extraction").setLevel(logging.DEBUG)
logging.getLogger("raptorflow.signal_processing").setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features

- **Multi-language Support**: Signal extraction in different languages
- **Image Analysis**: Visual signal detection from screenshots
- **Social Media Integration**: Enhanced social platform monitoring
- **Predictive Analytics**: Machine learning for trend prediction
- **Custom Signal Types**: User-defined signal categories

### API Extensions

- **Webhook Support**: Real-time signal notifications
- **Export Capabilities**: CSV/JSON export of signals and dossiers
- **Custom Dashboards**: Tenant-specific analytics dashboards
- **Signal Sharing**: Cross-tenant signal intelligence sharing

## Security Considerations

### Data Privacy

- **Tenant Isolation**: Strict tenant-based data separation
- **Content Filtering**: Remove sensitive information from signals
- **Retention Policies**: Automatic cleanup of old signal data

### Access Control

- **Role-Based Access**: Different permissions for different user types
- **API Rate Limiting**: Prevent abuse of scanning endpoints
- **Source Validation**: Verify source URLs are allowed for scanning

## Support

For issues or questions about Radar implementation:

1. Check logs for signal extraction errors
2. Verify database schema is properly migrated
3. Review configuration settings
4. Monitor source health and scheduler status

## License

Radar implementation is part of RaptorFlow and follows the same licensing terms.
