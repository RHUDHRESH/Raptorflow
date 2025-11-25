"""
Background Agent Jobs

Scheduled tasks for agents that run periodically:
- Trend scanning (PulseSeer)
- Competitor analysis (MirrorScout)
- Analytics aggregation (OptiMatrix)
- Metric collection
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any

from celery import shared_task
from backend.agents.signals.pulse_seer import PulseSeeerAgent
from backend.agents.signals.mirror_scout import MirrorScoutAgent
from backend.messaging.event_bus import EventBus, AgentMessage, EventType


# ============================================================================
# TREND SCANNING JOB
# ============================================================================

@shared_task(name="trends.scan_daily")
def scan_trends_job():
    """
    Daily trend scanning job

    Runs every morning at 9 AM to scan for emerging trends
    relevant to each workspace's cohorts.
    """

    print("[TASK] Starting daily trend scan...")

    # This would be executed in an async context
    asyncio.run(_scan_trends_async())


async def _scan_trends_async():
    """Async implementation of trend scanning"""

    try:
        from backend.dependencies import get_redis, get_db

        # Get clients
        redis_client = get_redis()
        db_client = get_db()

        # Initialize PulseSeer
        pulse_seer = PulseSeeerAgent(redis_client, db_client, None)

        # Get all active workspaces
        workspaces = await db_client.workspaces.find(status="active")

        for workspace in workspaces:
            workspace_id = workspace.get("id")

            # Get cohorts for this workspace
            cohorts = await db_client.cohorts.find(workspace_id=workspace_id)

            if not cohorts:
                continue

            print(f"  [Workspace {workspace_id}] Scanning trends for {len(cohorts)} cohorts...")

            # Scan for trends
            alerts = await pulse_seer.scan_trends(
                cohorts,
                correlation_id=f"daily_scan_{workspace_id}_{datetime.utcnow().isoformat()}"
            )

            print(f"    Found {len(alerts)} relevant trends")

            # Publish trend alerts
            event_bus = EventBus(redis_client)

            for alert in alerts:
                event_bus.publish(AgentMessage(
                    type=EventType.TREND_ALERT,
                    origin="TREND-01",
                    targets=["STRAT-01", "IDEA-01"],
                    payload=alert.model_dump(),
                    correlation_id=f"workspace_{workspace_id}",
                    priority="HIGH"
                ))

        print("[TASK] Trend scan complete")

    except Exception as e:
        print(f"[TASK ERROR] Trend scan failed: {e}")
        raise


# ============================================================================
# COMPETITOR ANALYSIS JOB
# ============================================================================

@shared_task(name="competitors.analyze_weekly")
def analyze_competitors_job():
    """
    Weekly competitor analysis job

    Runs every Monday morning to analyze competitors
    for each workspace.
    """

    print("[TASK] Starting weekly competitor analysis...")

    asyncio.run(_analyze_competitors_async())


async def _analyze_competitors_async():
    """Async implementation of competitor analysis"""

    try:
        from backend.dependencies import get_redis, get_db

        redis_client = get_redis()
        db_client = get_db()

        # Initialize MirrorScout
        mirror_scout = MirrorScoutAgent(redis_client, db_client, None)

        # Get all active workspaces
        workspaces = await db_client.workspaces.find(status="active")

        for workspace in workspaces:
            workspace_id = workspace.get("id")

            # Get competitors for this workspace
            competitors = await db_client.competitors.find(workspace_id=workspace_id)

            if not competitors:
                print(f"  [Workspace {workspace_id}] No competitors configured")
                continue

            print(f"  [Workspace {workspace_id}] Analyzing {len(competitors)} competitors...")

            # Analyze each competitor
            for competitor in competitors:
                try:
                    intel = await mirror_scout.analyze_competitor(
                        competitor_url=competitor.get("website_url"),
                        competitor_name=competitor.get("name"),
                        workspace_id=workspace_id,
                        correlation_id=f"weekly_analysis_{workspace_id}"
                    )

                    print(f"    ✓ {competitor['name']}: {intel.risk_level} risk")

                except Exception as e:
                    print(f"    ✗ {competitor['name']}: {e}")

        print("[TASK] Competitor analysis complete")

    except Exception as e:
        print(f"[TASK ERROR] Competitor analysis failed: {e}")
        raise


# ============================================================================
# METRIC AGGREGATION JOB
# ============================================================================

@shared_task(name="analytics.aggregate_daily")
def aggregate_metrics_job():
    """
    Daily metrics aggregation job

    Aggregates performance metrics from all platforms
    and updates move performance tracking.
    """

    print("[TASK] Starting daily metrics aggregation...")

    asyncio.run(_aggregate_metrics_async())


async def _aggregate_metrics_async():
    """Async implementation of metrics aggregation"""

    try:
        from backend.dependencies import get_db

        db_client = get_db()

        # Get all active moves
        moves = await db_client.moves.find(status="active")

        print(f"  Aggregating metrics for {len(moves)} active moves...")

        for move in moves:
            move_id = move.get("id")

            # Fetch metrics from all assets
            assets = await db_client.assets.find(move_id=move_id)

            if not assets:
                continue

            # Aggregate metrics
            total_impressions = 0
            total_clicks = 0
            total_conversions = 0

            for asset in assets:
                # In production, fetch from platform APIs
                total_impressions += asset.get("impressions", 0)
                total_clicks += asset.get("clicks", 0)
                total_conversions += asset.get("conversions", 0)

            # Update move metrics
            engagement_rate = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0

            await db_client.move_metrics.insert({
                "move_id": move_id,
                "impressions": total_impressions,
                "clicks": total_clicks,
                "conversions": total_conversions,
                "engagement_rate": engagement_rate,
                "conversion_rate": conversion_rate,
                "timestamp": datetime.utcnow()
            })

            print(f"    {move['name']}: {total_impressions} impressions, {engagement_rate:.1f}% engagement")

        print("[TASK] Metrics aggregation complete")

    except Exception as e:
        print(f"[TASK ERROR] Metrics aggregation failed: {e}")
        raise


# ============================================================================
# HEALTH CHECK JOB
# ============================================================================

@shared_task(name="swarm.health_check_hourly")
def health_check_job():
    """
    Hourly swarm health check

    Monitors agent health, connectivity, and performance.
    Alerts if issues detected.
    """

    print("[TASK] Running swarm health check...")

    try:
        from backend.dependencies import get_redis
        from backend.messaging.agent_registry import AgentRegistry

        redis_client = get_redis()
        registry = AgentRegistry(redis_client)

        # Get all agents
        agents = registry.list_all_agents()

        if not agents:
            print("  ⚠ No agents registered")
            return

        # Check health metrics
        available = sum(1 for a in agents if a.is_available)
        healthy = sum(1 for a in agents if a.success_rate > 0.8)
        slow = sum(1 for a in agents if a.avg_latency_ms > 5000)

        print(f"  Agents: {available}/{len(agents)} available")
        print(f"  Healthy: {healthy}/{len(agents)}")
        print(f"  Slow: {slow} agents with >5s latency")

        # Alert if issues
        if available < len(agents) * 0.7:
            print("  🔴 CRITICAL: Less than 70% agents available")
            # TODO: Send alert

        if slow > 0:
            print(f"  🟡 WARNING: {slow} agents experiencing high latency")

        print("[TASK] Health check complete")

    except Exception as e:
        print(f"[TASK ERROR] Health check failed: {e}")


# ============================================================================
# SCHEDULED TASK REGISTRY
# ============================================================================

SCHEDULED_TASKS = {
    "trends.scan_daily": {
        "task": "backend.tasks.agent_jobs.scan_trends_job",
        "schedule": {
            "hour": 9,  # 9 AM every day
            "minute": 0
        },
        "options": {"expires": 3600}
    },

    "competitors.analyze_weekly": {
        "task": "backend.tasks.agent_jobs.analyze_competitors_job",
        "schedule": {
            "day_of_week": "mon",  # Every Monday
            "hour": 9,
            "minute": 0
        },
        "options": {"expires": 86400}
    },

    "analytics.aggregate_daily": {
        "task": "backend.tasks.agent_jobs.aggregate_metrics_job",
        "schedule": {
            "hour": 0,  # Midnight every day
            "minute": 0
        },
        "options": {"expires": 3600}
    },

    "swarm.health_check_hourly": {
        "task": "backend.tasks.agent_jobs.health_check_job",
        "schedule": {
            "minute": 0  # Every hour
        },
        "options": {"expires": 600}
    }
}


def register_scheduled_tasks(celery_app):
    """
    Register all scheduled tasks with Celery

    Usage in main.py:
        from backend.tasks.agent_jobs import register_scheduled_tasks
        register_scheduled_tasks(celery_app)
    """

    for task_name, task_config in SCHEDULED_TASKS.items():
        celery_app.conf.beat_schedule[task_name] = {
            "task": task_config["task"],
            "schedule": task_config["schedule"],
            "options": task_config.get("options", {})
        }

    print(f"[Tasks] Registered {len(SCHEDULED_TASKS)} scheduled tasks")


# ============================================================================
# CELERY BEAT SCHEDULE (Alternative Config)
# ============================================================================

"""
If not using register_scheduled_tasks, add to celery_config:

celery_beat_schedule = {
    'scan-trends-daily': {
        'task': 'backend.tasks.agent_jobs.scan_trends_job',
        'schedule': crontab(hour=9, minute=0),
    },
    'analyze-competitors-weekly': {
        'task': 'backend.tasks.agent_jobs.analyze_competitors_job',
        'schedule': crontab(day_of_week=0, hour=9, minute=0),  # Monday 9 AM
    },
    'aggregate-metrics-daily': {
        'task': 'backend.tasks.agent_jobs.aggregate_metrics_job',
        'schedule': crontab(hour=0, minute=0),  # Midnight
    },
    'health-check-hourly': {
        'task': 'backend.tasks.agent_jobs.health_check_job',
        'schedule': crontab(minute=0),  # Every hour
    },
}
"""
