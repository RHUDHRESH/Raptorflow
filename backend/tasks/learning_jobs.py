"""
Learning System Scheduled Jobs

Celery tasks for running meta-learning cycles and maintaining
the self-improving loop system.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

from celery import shared_task
from backend.services.recommendation_tracker import RecommendationTracker
from backend.services.trust_scorer import TrustScorer
from backend.agents.executive.meta_learner import MetaLearnerAgent

logger = logging.getLogger(__name__)


# ============================================================================
# META-LEARNING CYCLE
# ============================================================================


@shared_task(name="learning.run_meta_learning_cycle")
def run_meta_learning_cycle(workspace_id: str):
    """
    Run a complete meta-learning cycle

    Discovers patterns, profiles agents, and generates decision rules.
    Runs daily to continuously improve the swarm.
    """

    logger.info(f"[LEARNING TASK] Starting meta-learning cycle for {workspace_id}")

    asyncio.run(_run_learning_cycle_async(workspace_id))


async def _run_learning_cycle_async(workspace_id: str):
    """Async implementation of learning cycle"""

    try:
        from backend.dependencies import get_redis, get_db

        redis_client = get_redis()
        db_client = get_db()

        # Initialize services
        tracker = RecommendationTracker(db_client, redis_client)
        trust_scorer = TrustScorer(db_client, tracker)

        # Initialize meta-learner
        meta_learner = MetaLearnerAgent(
            redis_client,
            db_client,
            None,  # LLM client
            tracker,
            trust_scorer,
        )

        # Run learning cycle
        result = await meta_learner.trigger_learning_cycle(
            workspace_id,
            {
                "lookback_days": 7,
                "min_pattern_confidence": 0.7,
            },
        )

        logger.info(
            f"[LEARNING TASK] Meta-learning cycle complete: "
            f"{result.get('patterns_discovered')} patterns, "
            f"{result.get('rules_updated')} rules"
        )

    except Exception as e:
        logger.error(f"[LEARNING TASK ERROR] Meta-learning cycle failed: {e}")
        raise


# ============================================================================
# TRUST SCORE MAINTENANCE
# ============================================================================


@shared_task(name="learning.update_trust_scores")
def update_trust_scores(workspace_id: str):
    """
    Update all trust scores for a workspace

    Recalculates trust scores based on recent recommendation outcomes.
    Runs every 6 hours to keep scores fresh.
    """

    logger.info(f"[LEARNING TASK] Updating trust scores for {workspace_id}")

    asyncio.run(_update_trust_scores_async(workspace_id))


async def _update_trust_scores_async(workspace_id: str):
    """Async implementation of trust score updates"""

    try:
        from backend.dependencies import get_redis, get_db

        redis_client = get_redis()
        db_client = get_db()

        tracker = RecommendationTracker(db_client, redis_client)
        trust_scorer = TrustScorer(db_client, tracker)

        # Recalculate all trust scores
        count = await trust_scorer.recalculate_all_trust_scores(workspace_id)

        logger.info(f"[LEARNING TASK] Updated trust scores for {count} agents")

    except Exception as e:
        logger.error(f"[LEARNING TASK ERROR] Trust score update failed: {e}")
        raise


# ============================================================================
# RECOMMENDATION CLEANUP
# ============================================================================


@shared_task(name="learning.cleanup_old_recommendations")
def cleanup_old_recommendations(workspace_id: str, days: int = 90):
    """
    Clean up old recommendations

    Removes recommendations older than specified days.
    Runs weekly to maintain database performance.
    """

    logger.info(
        f"[LEARNING TASK] Cleaning up recommendations older than {days} days"
    )

    asyncio.run(_cleanup_recommendations_async(workspace_id, days))


async def _cleanup_recommendations_async(workspace_id: str, days: int = 90):
    """Async implementation of cleanup"""

    try:
        from backend.dependencies import get_db

        db_client = get_db()

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Delete old recommendations
        deleted = await db_client.agent_recommendations.delete(
            workspace_id=workspace_id,
            created_at={"$lt": cutoff_date},
        )

        logger.info(
            f"[LEARNING TASK] Deleted {deleted} old recommendations "
            f"older than {cutoff_date}"
        )

    except Exception as e:
        logger.error(f"[LEARNING TASK ERROR] Cleanup failed: {e}")
        raise


# ============================================================================
# PATTERN REFRESH
# ============================================================================


@shared_task(name="learning.refresh_patterns")
def refresh_patterns(workspace_id: str):
    """
    Refresh discovered patterns

    Removes patterns with low confidence and re-validates existing patterns.
    Runs daily before meta-learning cycle.
    """

    logger.info(f"[LEARNING TASK] Refreshing patterns for {workspace_id}")

    asyncio.run(_refresh_patterns_async(workspace_id))


async def _refresh_patterns_async(workspace_id: str):
    """Async implementation of pattern refresh"""

    try:
        from backend.dependencies import get_db

        db_client = get_db()

        # Get all patterns
        patterns = await db_client.recommendation_patterns.find(
            workspace_id=workspace_id
        )

        if not patterns:
            logger.info("[LEARNING TASK] No patterns to refresh")
            return

        # Remove low-confidence patterns
        deleted_count = 0
        for pattern in patterns:
            if pattern.get("confidence_level", 0) < 0.5:
                await db_client.recommendation_patterns.delete(id=pattern.get("id"))
                deleted_count += 1

        logger.info(
            f"[LEARNING TASK] Refreshed patterns: "
            f"removed {deleted_count} low-confidence patterns, "
            f"kept {len(patterns) - deleted_count}"
        )

    except Exception as e:
        logger.error(f"[LEARNING TASK ERROR] Pattern refresh failed: {e}")
        raise


# ============================================================================
# SCHEDULED TASK REGISTRY
# ============================================================================

LEARNING_SCHEDULED_TASKS = {
    "learning.run_meta_learning_cycle": {
        "task": "backend.tasks.learning_jobs.run_meta_learning_cycle",
        "schedule": {
            "hour": 2,  # 2 AM every day
            "minute": 0,
        },
        "options": {"expires": 3600},
    },
    "learning.update_trust_scores": {
        "task": "backend.tasks.learning_jobs.update_trust_scores",
        "schedule": {
            "hour": "*/6",  # Every 6 hours
            "minute": 0,
        },
        "options": {"expires": 3600},
    },
    "learning.refresh_patterns": {
        "task": "backend.tasks.learning_jobs.refresh_patterns",
        "schedule": {
            "hour": 1,  # 1 AM every day (before learning cycle)
            "minute": 0,
        },
        "options": {"expires": 3600},
    },
    "learning.cleanup_old_recommendations": {
        "task": "backend.tasks.learning_jobs.cleanup_old_recommendations",
        "schedule": {
            "day_of_week": "sun",  # Every Sunday
            "hour": 3,
            "minute": 0,
        },
        "options": {"expires": 86400},
    },
}


def register_learning_tasks(celery_app):
    """
    Register all learning tasks with Celery

    Usage in main.py:
        from backend.tasks.learning_jobs import register_learning_tasks
        register_learning_tasks(celery_app)
    """

    for task_name, task_config in LEARNING_SCHEDULED_TASKS.items():
        celery_app.conf.beat_schedule[task_name] = {
            "task": task_config["task"],
            "schedule": task_config["schedule"],
            "options": task_config.get("options", {}),
        }

    logger.info(f"[LEARNING TASKS] Registered {len(LEARNING_SCHEDULED_TASKS)} learning tasks")


# ============================================================================
# CELERY BEAT SCHEDULE (Alternative Config)
# ============================================================================

"""
If not using register_learning_tasks, add to celery_config:

celery_beat_schedule = {
    'run-meta-learning-cycle': {
        'task': 'backend.tasks.learning_jobs.run_meta_learning_cycle',
        'schedule': crontab(hour=2, minute=0),
    },
    'update-trust-scores': {
        'task': 'backend.tasks.learning_jobs.update_trust_scores',
        'schedule': crontab(hour='*/6', minute=0),  # Every 6 hours
    },
    'refresh-patterns': {
        'task': 'backend.tasks.learning_jobs.refresh_patterns',
        'schedule': crontab(hour=1, minute=0),
    },
    'cleanup-old-recommendations': {
        'task': 'backend.tasks.learning_jobs.cleanup_old_recommendations',
        'schedule': crontab(day_of_week=0, hour=3, minute=0),  # Sunday 3 AM
    },
}
"""
