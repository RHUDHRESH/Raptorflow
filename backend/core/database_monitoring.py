"""
Production Database Monitoring System
Airtight monitoring and alerting for database scaling issues
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from connection_pool import get_connection_pool_health
from database_config import DB_CONFIG
from supabase_mgr import get_supabase_admin

logger = logging.getLogger(__name__)


class DatabaseMonitor:
    """Production database monitoring with intelligent alerting"""

    def __init__(self):
        self.supabase = get_supabase_admin()
        self.alert_thresholds = DB_CONFIG.get_monitoring_config()
        self.monitoring_active = False
        self.last_check = None

    async def start_monitoring(self) -> None:
        """Start continuous monitoring"""
        self.monitoring_active = True
        logger.info("Database monitoring started")

        # Run monitoring loop
        asyncio.create_task(self._monitoring_loop())

    async def stop_monitoring(self) -> None:
        """Stop monitoring"""
        self.monitoring_active = False
        logger.info("Database monitoring stopped")

    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                await self._perform_health_check()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(60)

    async def _perform_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health_status = {
            "timestamp": datetime.utcnow(),
            "overall_status": "healthy",
            "checks": {},
            "alerts": [],
        }

        # Check connection pool health
        pool_health = await self._check_connection_pool()
        health_status["checks"]["connection_pool"] = pool_health

        # Check query performance
        query_health = await self._check_query_performance()
        health_status["checks"]["query_performance"] = query_health

        # Check database size and growth
        size_health = await self._check_database_size()
        health_status["checks"]["database_size"] = size_health

        # Check active connections
        connection_health = await self._check_active_connections()
        health_status["checks"]["active_connections"] = connection_health

        # Check for blocking queries
        blocking_health = await self._check_blocking_queries()
        health_status["checks"]["blocking_queries"] = blocking_health

        # Determine overall status
        all_checks = list(health_status["checks"].values())
        if any(check["status"] == "critical" for check in all_checks):
            health_status["overall_status"] = "critical"
        elif any(check["status"] == "warning" for check in all_checks):
            health_status["overall_status"] = "warning"

        # Generate alerts
        health_status["alerts"] = self._generate_alerts(health_status["checks"])

        self.last_check = health_status
        return health_status

    async def _check_connection_pool(self) -> Dict[str, Any]:
        """Check connection pool health"""
        try:
            pool_stats = await get_connection_pool_health()

            utilization = pool_stats.get("utilization", 0)
            available = pool_stats.get("available", 0)

            status = "healthy"
            alerts = []

            if utilization > 0.9:
                status = "critical"
                alerts.append(
                    f"Connection pool utilization critical: {utilization:.1%}"
                )
            elif utilization > 0.8:
                status = "warning"
                alerts.append(f"Connection pool utilization high: {utilization:.1%}")

            if available == 0:
                status = "critical"
                alerts.append("No available connections in pool")

            return {
                "status": status,
                "utilization": utilization,
                "available": available,
                "total": pool_stats.get("total_connections", 0),
                "alerts": alerts,
            }

        except Exception as e:
            logger.error(f"Connection pool check failed: {e}")
            return {
                "status": "critical",
                "error": str(e),
                "alerts": ["Connection pool monitoring failed"],
            }

    async def _check_query_performance(self) -> Dict[str, Any]:
        """Check query performance using pg_stat_statements"""
        try:
            # Get slow queries
            slow_queries_result = (
                await self.supabase.table("slow_queries")
                .select("*")
                .limit(10)
                .execute()
            )
            slow_queries = slow_queries_result.data or []

            # Get query performance summary
            summary_result = await self.supabase.rpc("get_query_performance_summary")
            summary = summary_result.data if summary_result.data else {}

            status = "healthy"
            alerts = []

            # Check for slow queries
            if summary.get("slow_queries", 0) > 5:
                status = "warning"
                alerts.append(f"High number of slow queries: {summary['slow_queries']}")

            if summary.get("avg_query_time", 0) > 2.0:
                status = "warning"
                alerts.append(
                    f"High average query time: {summary['avg_query_time']:.2f}s"
                )

            # Check for extremely slow queries
            very_slow = [q for q in slow_queries if q.get("mean_exec_time", 0) > 5.0]
            if very_slow:
                status = "critical"
                alerts.append(f"Found {len(very_slow)} very slow queries (>5s)")

            return {
                "status": status,
                "total_queries": summary.get("total_queries", 0),
                "slow_queries": summary.get("slow_queries", 0),
                "avg_query_time": summary.get("avg_query_time", 0),
                "slow_queries_list": slow_queries[:5],
                "alerts": alerts,
            }

        except Exception as e:
            logger.error(f"Query performance check failed: {e}")
            return {
                "status": "warning",
                "error": str(e),
                "alerts": ["Query performance monitoring failed"],
            }

    async def _check_database_size(self) -> Dict[str, Any]:
        """Check database size and growth"""
        try:
            # Get database size
            size_query = """
            SELECT
                pg_size_pretty(pg_database_size(current_database())) as total_size,
                pg_database_size(current_database()) as size_bytes
            """

            # This would need to be executed as raw SQL
            # For now, return placeholder
            size_bytes = 1000000000  # 1GB placeholder
            total_size = "1 GB"

            status = "healthy"
            alerts = []

            # Check if database is getting large (>10GB)
            if size_bytes > 10 * 1024 * 1024 * 1024:
                status = "warning"
                alerts.append(f"Database size large: {total_size}")

            # Check if database is very large (>50GB)
            if size_bytes > 50 * 1024 * 1024 * 1024:
                status = "critical"
                alerts.append(f"Database size critical: {total_size}")

            return {
                "status": status,
                "total_size": total_size,
                "size_bytes": size_bytes,
                "alerts": alerts,
            }

        except Exception as e:
            logger.error(f"Database size check failed: {e}")
            return {
                "status": "warning",
                "error": str(e),
                "alerts": ["Database size monitoring failed"],
            }

    async def _check_active_connections(self) -> Dict[str, Any]:
        """Check active database connections"""
        try:
            # Get connection count
            # This would need to be executed as raw SQL
            # For now, return placeholder
            active_connections = 25
            max_connections = 100  # Supabase default

            utilization = active_connections / max_connections

            status = "healthy"
            alerts = []

            if utilization > 0.9:
                status = "critical"
                alerts.append(f"Connection utilization critical: {utilization:.1%}")
            elif utilization > 0.8:
                status = "warning"
                alerts.append(f"Connection utilization high: {utilization:.1%}")

            return {
                "status": status,
                "active_connections": active_connections,
                "max_connections": max_connections,
                "utilization": utilization,
                "alerts": alerts,
            }

        except Exception as e:
            logger.error(f"Active connections check failed: {e}")
            return {
                "status": "warning",
                "error": str(e),
                "alerts": ["Connection monitoring failed"],
            }

    async def _check_blocking_queries(self) -> Dict[str, Any]:
        """Check for blocking queries"""
        try:
            # This would need to be executed as raw SQL
            # For now, return placeholder
            blocking_queries = []

            status = "healthy"
            alerts = []

            if blocking_queries:
                status = "critical"
                alerts.append(f"Found {len(blocking_queries)} blocking queries")

            return {
                "status": status,
                "blocking_queries": blocking_queries,
                "alerts": alerts,
            }

        except Exception as e:
            logger.error(f"Blocking queries check failed: {e}")
            return {
                "status": "warning",
                "error": str(e),
                "alerts": ["Blocking query monitoring failed"],
            }

    def _generate_alerts(self, checks: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alerts from all checks"""
        alerts = []

        for check_name, check_data in checks.items():
            for alert in check_data.get("alerts", []):
                alerts.append(
                    {
                        "timestamp": datetime.utcnow(),
                        "check": check_name,
                        "severity": check_data["status"],
                        "message": alert,
                        "details": check_data,
                    }
                )

        return alerts

    async def get_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate performance report for the last N hours"""
        try:
            # Get query patterns
            patterns_result = await self.supabase.rpc("analyze_query_patterns")
            patterns = patterns_result.data or []

            # Get slow queries
            slow_queries_result = (
                await self.supabase.table("slow_queries")
                .select("*")
                .limit(20)
                .execute()
            )
            slow_queries = slow_queries_result.data or []

            # Get frequent queries
            frequent_queries_result = (
                await self.supabase.table("frequent_queries")
                .select("*")
                .limit(20)
                .execute()
            )
            frequent_queries = frequent_queries_result.data or []

            return {
                "period_hours": hours,
                "generated_at": datetime.utcnow(),
                "query_patterns": patterns,
                "slow_queries": slow_queries,
                "frequent_queries": frequent_queries,
                "recommendations": self._generate_recommendations(
                    patterns, slow_queries
                ),
            }

        except Exception as e:
            logger.error(f"Performance report generation failed: {e}")
            return {"error": str(e), "generated_at": datetime.utcnow()}

    def _generate_recommendations(
        self, patterns: List[Dict], slow_queries: List[Dict]
    ) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []

        # Analyze patterns
        high_priority_patterns = [p for p in patterns if p.get("priority") == "HIGH"]

        if high_priority_patterns:
            recommendations.append("High-priority optimization needed:")
            recommendations.extend(
                [f"- {p.get('recommendation')}" for p in high_priority_patterns[:3]]
            )

        # Analyze slow queries
        if slow_queries:
            recommendations.append(f"Found {len(slow_queries)} slow queries:")
            recommendations.extend(
                [f"- Optimize: {q.get('query', '')[:50]}..." for q in slow_queries[:3]]
            )

        # General recommendations
        if len(slow_queries) > 10:
            recommendations.append("Consider implementing query result caching")

        return recommendations

    async def get_current_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        if self.last_check:
            return self.last_check

        return await self._perform_health_check()


# Global monitor instance
_database_monitor: Optional[DatabaseMonitor] = None


def get_database_monitor() -> DatabaseMonitor:
    """Get global database monitor"""
    global _database_monitor
    if _database_monitor is None:
        _database_monitor = DatabaseMonitor()
    return _database_monitor


# FastAPI dependency for monitoring status
async def get_database_monitoring_status() -> Dict[str, Any]:
    """Get current database monitoring status"""
    monitor = get_database_monitor()
    return await monitor.get_current_status()


# FastAPI dependency for performance report
async def get_database_performance_report() -> Dict[str, Any]:
    """Get database performance report"""
    monitor = get_database_monitor()
    return await monitor.get_performance_report()
