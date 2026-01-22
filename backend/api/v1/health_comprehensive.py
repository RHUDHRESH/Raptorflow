"""
Comprehensive health check system for RaptorFlow
Monitors all critical services and provides detailed status information
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from infrastructure.secrets import get_secrets_manager

from backend.core.celery_manager import get_celery_health
from backend.core.circuit_breaker import get_resilient_client
from backend.core.migrations import get_migration_health
from backend.core.posthog import get_health_status as get_posthog_health
from backend.core.redis import get_redis_client
from backend.core.sentry import get_health_status
from backend.dependencies import get_db, get_redis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


class HealthStatus:
    """Health status enumeration"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheck:
    """Individual health check result"""

    def __init__(
        self,
        name: str,
        status: str,
        message: str = "",
        details: Optional[Dict[str, Any]] = None,
        response_time_ms: Optional[float] = None,
    ):
        self.name = name
        self.status = status
        self.message = message
        self.details = details or {}
        self.response_time_ms = response_time_ms
        self.timestamp = datetime.utcnow()


async def check_database_health() -> HealthCheck:
    """Check database connectivity and basic operations"""
    start_time = datetime.now()

    try:
        db = get_db()

        # Test basic query
        result = db.table("users").select("id").limit(1).execute()

        # Get connection info
        response_time = (datetime.now() - start_time).total_seconds() * 1000

        return HealthCheck(
            name="database",
            status=HealthStatus.HEALTHY,
            message="Database connection successful",
            details={
                "connection_pool": "active",
                "query_executed": True,
                "rows_returned": len(result.data) if result.data else 0,
            },
            response_time_ms=response_time,
        )

    except Exception as e:
        response_time = (datetime.now() - start_time).total_seconds() * 1000

        return HealthCheck(
            name="database",
            status=HealthStatus.UNHEALTHY,
            message=f"Database connection failed: {str(e)}",
            details={"error": str(e)},
            response_time_ms=response_time,
        )


@router.get("/redis")
async def check_redis_only():
    """Redis-specific health check endpoint"""
    try:
        from redis_core.client import get_redis

        redis_client = get_redis()

        # Test Redis connection
        is_healthy = await redis_client.ping()

        if is_healthy:
            # Get basic Redis info
            try:
                # Test basic operations
                test_key = "health_check_test"
                await redis_client.set(test_key, "test_value", ex=10)
                value = await redis_client.get(test_key)
                await redis_client.delete(test_key)

                return {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "details": {
                        "connection": "ok",
                        "basic_operations": "ok" if value == "test_value" else "failed",
                        "test_value": value,
                    },
                }
            except Exception as e:
                return {
                    "status": "degraded",
                    "timestamp": datetime.now().isoformat(),
                    "details": {
                        "connection": "ok",
                        "basic_operations": "failed",
                        "error": str(e),
                    },
                }
        else:
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "details": {"connection": "failed", "error": "Redis ping failed"},
            }

    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }


async def check_redis_health() -> HealthCheck:
    """Check Redis connectivity and basic operations"""
    start_time = datetime.now()

    try:
        redis_client = get_redis_client()

        # Test basic operations
        test_key = "health_check_test"
        await redis_client.set(test_key, "test_value", ex=10)
        value = await redis_client.get(test_key)
        await redis_client.delete(test_key)

        response_time = (datetime.now() - start_time).total_seconds() * 1000

        if value == "test_value":
            return HealthCheck(
                name="redis",
                status=HealthStatus.HEALTHY,
                message="Redis connection successful",
                details={
                    "set_operation": True,
                    "get_operation": True,
                    "delete_operation": True,
                },
                response_time_ms=response_time,
            )
        else:
            return HealthCheck(
                name="redis",
                status=HealthStatus.DEGRADED,
                message="Redis data integrity issue",
                details={"expected": "test_value", "received": value},
                response_time_ms=response_time,
            )

    except Exception as e:
        response_time = (datetime.now() - start_time).total_seconds() * 1000

        return HealthCheck(
            name="redis",
            status=HealthStatus.UNHEALTHY,
            message=f"Redis connection failed: {str(e)}",
            details={"error": str(e)},
            response_time_ms=response_time,
        )


async def check_external_services_health() -> List[HealthCheck]:
    """Check external API services health"""
    services = []

    # Check OpenAI
    try:
        start_time = datetime.now()
        client = get_resilient_client()
        response = await client.get("openai", "https://api.openai.com/v1/models")
        response_time = (datetime.now() - start_time).total_seconds() * 1000

        services.append(
            HealthCheck(
                name="openai",
                status=HealthStatus.HEALTHY,
                message="OpenAI API accessible",
                details={"status_code": response.status_code},
                response_time_ms=response_time,
            )
        )

    except Exception as e:
        services.append(
            HealthCheck(
                name="openai",
                status=HealthStatus.DEGRADED,
                message=f"OpenAI API issue: {str(e)}",
                details={"error": str(e)},
            )
        )

    # Check Serper (search API)
    try:
        start_time = datetime.now()
        client = get_resilient_client()
        response = await client.get(
            "serper", "https://google.serper.dev/search", params={"q": "test"}
        )
        response_time = (datetime.now() - start_time).total_seconds() * 1000

        services.append(
            HealthCheck(
                name="serper",
                status=HealthStatus.HEALTHY,
                message="Serper API accessible",
                details={"status_code": response.status_code},
                response_time_ms=response_time,
            )
        )

    except Exception as e:
        services.append(
            HealthCheck(
                name="serper",
                status=HealthStatus.DEGRADED,
                message=f"Serper API issue: {str(e)}",
                details={"error": str(e)},
            )
        )

    return services


async def check_memory_system_health() -> HealthCheck:
    """Check memory system components"""
    start_time = datetime.now()

    try:
        from backend.memory.controller import MemoryController
        from backend.memory.embeddings import get_embedding_model

        # Test memory controller
        controller = MemoryController()

        # Test embedding model
        model = get_embedding_model()
        if not model:
            raise ValueError("Embedding model not available")

        # Test basic embedding
        test_text = "Health check test"
        embedding = model.encode([test_text])

        response_time = (datetime.now() - start_time).total_seconds() * 1000

        return HealthCheck(
            name="memory_system",
            status=HealthStatus.HEALTHY,
            message="Memory system operational",
            details={
                "controller_available": True,
                "embedding_model_available": True,
                "embedding_dimension": (
                    len(embedding[0]) if len(embedding) > 0 else None
                ),
            },
            response_time_ms=response_time,
        )

    except Exception as e:
        response_time = (datetime.now() - start_time).total_seconds() * 1000

        return HealthCheck(
            name="memory_system",
            status=HealthStatus.DEGRADED,
            message=f"Memory system issue: {str(e)}",
            details={"error": str(e)},
            response_time_ms=response_time,
        )


async def check_cognitive_engine_health() -> HealthCheck:
    """Check cognitive engine components"""
    start_time = datetime.now()

    try:
        from backend.cognitive import CognitiveEngine

        engine = CognitiveEngine()

        response_time = (datetime.now() - start_time).total_seconds() * 1000

        return HealthCheck(
            name="cognitive_engine",
            status=HealthStatus.HEALTHY,
            message="Cognitive engine operational",
            details={"engine_initialized": True},
            response_time_ms=response_time,
        )

    except Exception as e:
        response_time = (datetime.now() - start_time).total_seconds() * 1000

        return HealthCheck(
            name="cognitive_engine",
            status=HealthStatus.DEGRADED,
            message=f"Cognitive engine issue: {str(e)}",
            details={"error": str(e)},
            response_time_ms=response_time,
        )


async def check_circuit_breakers_health() -> List[HealthCheck]:
    """Check circuit breaker status"""
    client = get_resilient_client()
    checks = []

    for service_name, breaker in client.circuit_breakers.items():
        stats = breaker.get_stats()
        state = breaker.get_state()

        status = HealthStatus.HEALTHY
        if state.value == "open":
            status = HealthStatus.UNHEALTHY
        elif state.value == "half_open":
            status = HealthStatus.DEGRADED

        checks.append(
            HealthCheck(
                name=f"circuit_breaker_{service_name}",
                status=status,
                message=f"Circuit breaker state: {state.value}",
                details={
                    "state": state.value,
                    "failures": stats.failures,
                    "successes": stats.successes,
                    "total_requests": stats.total_requests,
                    "state_changes": stats.state_changes,
                },
            )
        )

    return checks


async def check_monitoring_health() -> HealthCheck:
    """Check monitoring systems"""
    start_time = datetime.now()

    try:
        # Check Sentry
        sentry_status = get_health_status()

        response_time = (datetime.now() - start_time).total_seconds() * 1000

        status = (
            HealthStatus.HEALTHY
            if sentry_status["status"] == "healthy"
            else HealthStatus.DEGRADED
        )

        return HealthCheck(
            name="monitoring",
            status=status,
            message="Monitoring systems check",
            details={
                "sentry": sentry_status,
                "environment": os.getenv("ENVIRONMENT", "unknown"),
            },
            response_time_ms=response_time,
        )

    except Exception as e:
        response_time = (datetime.now() - start_time).total_seconds() * 1000

        return HealthCheck(
            name="monitoring",
            status=HealthStatus.DEGRADED,
            message=f"Monitoring issue: {str(e)}",
            details={"error": str(e)},
            response_time_ms=response_time,
        )


async def check_analytics_health() -> HealthCheck:
    """Check analytics systems (PostHog)"""
    start_time = datetime.now()

    try:
        # Check PostHog
        posthog_status = get_posthog_health()

        response_time = (datetime.now() - start_time).total_seconds() * 1000

        status = (
            HealthStatus.HEALTHY
            if posthog_status["status"] == "healthy"
            else HealthStatus.DEGRADED
        )

        return HealthCheck(
            name="analytics",
            status=status,
            message="Analytics systems check",
            details={
                "posthog": posthog_status,
            },
            response_time_ms=response_time,
        )

    except Exception as e:
        response_time = (datetime.now() - start_time).total_seconds() * 1000

        return HealthCheck(
            name="analytics",
            status=HealthStatus.DEGRADED,
            message=f"Analytics issue: {str(e)}",
            details={"error": str(e)},
            response_time_ms=response_time,
        )


async def check_background_workers_health() -> HealthCheck:
    """Check background worker systems (Celery)"""
    start_time = datetime.now()

    try:
        # Check Celery
        celery_status = await get_celery_health()

        response_time = (datetime.now() - start_time).total_seconds() * 1000

        status = (
            HealthStatus.HEALTHY
            if celery_status["status"] == "healthy"
            else HealthStatus.DEGRADED
        )

        return HealthCheck(
            name="background_workers",
            status=status,
            message="Background worker systems check",
            details={
                "celery": celery_status,
            },
            response_time_ms=response_time,
        )

    except Exception as e:
        response_time = (datetime.now() - start_time).total_seconds() * 1000

        return HealthCheck(
            name="background_workers",
            status=HealthStatus.DEGRADED,
            message=f"Background workers issue: {str(e)}",
            details={"error": str(e)},
            response_time_ms=response_time,
        )


async def check_database_migrations_health() -> HealthCheck:
    """Check database migration system"""
    start_time = datetime.now()

    try:
        # Check migrations
        migration_status = await get_migration_health()

        response_time = (datetime.now() - start_time).total_seconds() * 1000

        status = (
            HealthStatus.HEALTHY
            if migration_status["status"] == "healthy"
            else HealthStatus.DEGRADED
        )

        return HealthCheck(
            name="database_migrations",
            status=status,
            message="Database migration system check",
            details={
                "migrations": migration_status,
            },
            response_time_ms=response_time,
        )

    except Exception as e:
        response_time = (datetime.now() - start_time).total_seconds() * 1000

        return HealthCheck(
            name="database_migrations",
            status=HealthStatus.DEGRADED,
            message=f"Migration system issue: {str(e)}",
            details={"error": str(e)},
            response_time_ms=response_time,
        )


def calculate_overall_status(checks: List[HealthCheck]) -> str:
    """Calculate overall system status from individual checks"""
    if not checks:
        return HealthStatus.UNHEALTHY

    statuses = [check.status for check in checks]

    if HealthStatus.UNHEALTHY in statuses:
        return HealthStatus.UNHEALTHY
    elif HealthStatus.DEGRADED in statuses:
        return HealthStatus.DEGRADED
    else:
        return HealthStatus.HEALTHY


@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "RaptorFlow Backend",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/detailed")
async def detailed_health_check():
    """Comprehensive health check of all systems"""
    start_time = datetime.now()

    # Run all health checks concurrently
    checks = await asyncio.gather(
        check_database_health(),
        check_redis_health(),
        check_memory_system_health(),
        check_cognitive_engine_health(),
        check_monitoring_health(),
        check_analytics_health(),
        check_background_workers_health(),
        check_database_migrations_health(),
        return_exceptions=True,
    )

    # Add external services checks
    external_checks = await check_external_services_health()
    circuit_breaker_checks = await check_circuit_breakers_health()

    # Process results
    all_checks = []

    for check in checks:
        if isinstance(check, Exception):
            all_checks.append(
                HealthCheck(
                    name="unknown",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check error: {str(check)}",
                )
            )
        else:
            all_checks.append(check)

    all_checks.extend(external_checks)
    all_checks.extend(circuit_breaker_checks)

    # Calculate overall status
    overall_status = calculate_overall_status(all_checks)

    # Calculate total response time
    total_time = (datetime.now() - start_time).total_seconds() * 1000

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "response_time_ms": total_time,
        "checks": [
            {
                "name": check.name,
                "status": check.status,
                "message": check.message,
                "details": check.details,
                "response_time_ms": check.response_time_ms,
                "timestamp": check.timestamp.isoformat(),
            }
            for check in all_checks
        ],
        "summary": {
            "total_checks": len(all_checks),
            "healthy": len([c for c in all_checks if c.status == HealthStatus.HEALTHY]),
            "degraded": len(
                [c for c in all_checks if c.status == HealthStatus.DEGRADED]
            ),
            "unhealthy": len(
                [c for c in all_checks if c.status == HealthStatus.UNHEALTHY]
            ),
        },
    }


@router.get("/readiness")
async def readiness_check():
    """Kubernetes readiness probe"""
    try:
        # Check critical services only
        db_check = await check_database_health()
        redis_check = await check_redis_health()

        if (
            db_check.status == HealthStatus.HEALTHY
            and redis_check.status == HealthStatus.HEALTHY
        ):
            return {
                "status": "ready",
                "timestamp": datetime.utcnow().isoformat(),
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service not ready",
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Readiness check failed: {str(e)}",
        )


@router.get("/liveness")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/metrics")
async def health_metrics():
    """Health check metrics for monitoring"""
    detailed = await detailed_health_check()

    # Extract metrics
    metrics = {
        "overall_status": detailed["status"],
        "total_response_time_ms": detailed["response_time_ms"],
        "check_count": detailed["summary"]["total_checks"],
        "healthy_count": detailed["summary"]["healthy"],
        "degraded_count": detailed["summary"]["degraded"],
        "unhealthy_count": detailed["summary"]["unhealthy"],
    }

    # Add individual check metrics
    for check in detailed["checks"]:
        if check["response_time_ms"]:
            metrics[f"{check['name']}_response_time_ms"] = check["response_time_ms"]
        metrics[f"{check['name']}_status"] = check["status"]

    return metrics
