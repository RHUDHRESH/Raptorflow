"""
Production-ready database health monitoring for RaptorFlow
Checks database connectivity, RLS policies, and performance
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..core.supabase import get_supabase_client

logger = logging.getLogger(__name__)


@dataclass
class HealthCheckResult:
    """Health check result"""

    status: str  # healthy, degraded, unhealthy
    message: str
    timestamp: datetime
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


@dataclass
class DatabaseHealthMetrics:
    """Database health metrics"""

    connection_status: bool
    response_time_ms: float
    rls_enabled: bool
    table_count: int
    index_count: int
    active_connections: Optional[int] = None
    database_size_mb: Optional[float] = None


class DatabaseHealthChecker:
    """Production-ready database health monitoring"""

    def __init__(self):
        self.supabase = get_supabase_client()

    async def check_connection(self) -> HealthCheckResult:
        """
        Check database connectivity

        Returns:
            HealthCheckResult with connection status
        """
        start_time = datetime.now()

        try:
            # Simple query to test connectivity
            result = (
                self.supabase.table("users").select("count", count="exact").execute()
            )

            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000

            if hasattr(result, "data"):
                return HealthCheckResult(
                    status="healthy",
                    message="Database connection successful",
                    timestamp=end_time,
                    details={
                        "response_time_ms": response_time,
                        "query_executed": "SELECT COUNT FROM users",
                    },
                )
            else:
                return HealthCheckResult(
                    status="unhealthy",
                    message="Database query failed",
                    timestamp=end_time,
                    details={"error": "No data returned from query"},
                )

        except Exception as e:
            end_time = datetime.now()
            logger.error(f"Database connection check failed: {e}")

            return HealthCheckResult(
                status="unhealthy",
                message=f"Database connection failed: {str(e)}",
                timestamp=end_time,
                details={"error": str(e)},
            )

    async def check_rls_enabled(self) -> HealthCheckResult:
        """
        Check if Row Level Security is enabled on critical tables

        Returns:
            HealthCheckResult with RLS status
        """
        critical_tables = ["users", "workspaces", "foundations", "icp_profiles"]
        rls_status = {}

        try:
            for table in critical_tables:
                # Check if RLS is enabled by querying information_schema
                query = """
                SELECT relrowsecurity
                FROM pg_class
                JOIN pg_namespace ON pg_namespace.oid = pg_class.relnamespace
                WHERE pg_class.relname = %s AND pg_namespace.nspname = 'public'
                """

                try:
                    result = self.supabase.rpc(
                        "check_rls_enabled", {"table_name": table}
                    ).execute()
                    if result.data:
                        rls_status[table] = bool(
                            result.data[0].get("relrowsecurity", False)
                        )
                    else:
                        rls_status[table] = False
                except Exception as e:
                    logger.warning(f"Could not check RLS for table {table}: {e}")
                    rls_status[table] = False

            all_enabled = all(rls_status.values())

            return HealthCheckResult(
                status="healthy" if all_enabled else "degraded",
                message="RLS check completed",
                timestamp=datetime.now(),
                details={
                    "rls_enabled": all_enabled,
                    "table_status": rls_status,
                    "tables_checked": critical_tables,
                },
            )

        except Exception as e:
            logger.error(f"RLS check failed: {e}")
            return HealthCheckResult(
                status="unhealthy",
                message=f"RLS check failed: {str(e)}",
                timestamp=datetime.now(),
                details={"error": str(e)},
            )

    async def check_indexes(self) -> HealthCheckResult:
        """
        Check critical database indexes exist

        Returns:
            HealthCheckResult with index status
        """
        required_indexes = [
            {"table": "users", "columns": ["id"]},
            {"table": "users", "columns": ["email"]},
            {"table": "workspaces", "columns": ["user_id"]},
            {"table": "workspaces", "columns": ["slug"]},
            {"table": "foundations", "columns": ["workspace_id"]},
            {"table": "icp_profiles", "columns": ["workspace_id"]},
            {"table": "icp_profiles", "columns": ["workspace_id", "is_primary"]},
        ]

        index_status = {}

        try:
            for index_req in required_indexes:
                table = index_req["table"]
                columns = index_req["columns"]

                # Check if index exists
                try:
                    result = self.supabase.rpc(
                        "check_index_exists",
                        {"table_name": table, "column_names": columns},
                    ).execute()

                    exists = bool(result.data and result.data[0].get("exists", False))
                    index_status[f"{table}({','.join(columns)})"] = exists

                except Exception as e:
                    logger.warning(f"Could not check index for {table} {columns}: {e}")
                    index_status[f"{table}({','.join(columns)})"] = False

            missing_indexes = [k for k, v in index_status.items() if not v]

            return HealthCheckResult(
                status="healthy" if not missing_indexes else "degraded",
                message="Index check completed",
                timestamp=datetime.now(),
                details={
                    "missing_indexes": missing_indexes,
                    "total_indexes": len(index_status),
                    "present_indexes": len(index_status) - len(missing_indexes),
                    "index_status": index_status,
                },
            )

        except Exception as e:
            logger.error(f"Index check failed: {e}")
            return HealthCheckResult(
                status="unhealthy",
                message=f"Index check failed: {str(e)}",
                timestamp=datetime.now(),
                details={"error": str(e)},
            )

    async def check_performance(self) -> HealthCheckResult:
        """
        Check database performance metrics

        Returns:
            HealthCheckResult with performance metrics
        """
        try:
            # Test query performance
            start_time = datetime.now()
            result = self.supabase.table("users").select("*").limit(10).execute()
            end_time = datetime.now()

            query_time = (end_time - start_time).total_seconds() * 1000

            # Get database size (if available)
            size_result = None
            try:
                size_result = self.supabase.rpc("get_database_size").execute()
            except Exception:
                pass  # Size function might not exist

            # Get connection count (if available)
            connection_result = None
            try:
                connection_result = self.supabase.rpc(
                    "get_active_connections"
                ).execute()
            except Exception:
                pass  # Connection function might not exist

            metrics = {
                "query_time_ms": query_time,
                "database_size_mb": (
                    size_result.data[0].get("size_mb")
                    if size_result and size_result.data
                    else None
                ),
                "active_connections": (
                    connection_result.data[0].get("count")
                    if connection_result and connection_result.data
                    else None
                ),
                "records_returned": len(result.data) if result.data else 0,
            }

            # Determine health based on performance
            status = "healthy"
            issues = []

            if query_time > 1000:  # > 1 second
                status = "degraded"
                issues.append("Slow query performance")

            if metrics.get("active_connections", 0) > 100:
                status = "degraded"
                issues.append("High connection count")

            return HealthCheckResult(
                status=status,
                message=f"Performance check completed{': ' + ', '.join(issues) if issues else ''}",
                timestamp=end_time,
                details=metrics,
            )

        except Exception as e:
            logger.error(f"Performance check failed: {e}")
            return HealthCheckResult(
                status="unhealthy",
                message=f"Performance check failed: {str(e)}",
                timestamp=datetime.now(),
                details={"error": str(e)},
            )

    async def get_comprehensive_health(self) -> Dict[str, HealthCheckResult]:
        """
        Get comprehensive database health report

        Returns:
            Dictionary with all health check results
        """
        logger.info("Starting comprehensive database health check")

        results = {}

        # Run all health checks
        results["connection"] = await self.check_connection()
        results["rls"] = await self.check_rls_enabled()
        results["indexes"] = await self.check_indexes()
        results["performance"] = await self.check_performance()

        # Determine overall health
        statuses = [result.status for result in results.values()]

        if "unhealthy" in statuses:
            overall_status = "unhealthy"
        elif "degraded" in statuses:
            overall_status = "degraded"
        else:
            overall_status = "healthy"

        results["overall"] = HealthCheckResult(
            status=overall_status,
            message=f"Database health: {overall_status}",
            timestamp=datetime.now(),
            details={
                "checks_performed": list(results.keys())[:-1],  # Exclude overall
                "individual_statuses": {
                    k: v.status for k, v in results.items() if k != "overall"
                },
            },
        )

        logger.info(f"Database health check completed: {overall_status}")
        return results

    async def get_health_metrics(self) -> DatabaseHealthMetrics:
        """
        Get detailed database health metrics

        Returns:
            DatabaseHealthMetrics with current metrics
        """
        try:
            # Connection test
            start_time = datetime.now()
            connection_result = (
                self.supabase.table("users").select("count", count="exact").execute()
            )
            end_time = datetime.now()

            connection_status = hasattr(connection_result, "data")
            response_time = (end_time - start_time).total_seconds() * 1000

            # Get table count
            table_result = self.supabase.rpc("get_table_count").execute()
            table_count = (
                table_result.data[0].get("count", 0)
                if table_result and table_result.data
                else 0
            )

            # Get index count
            index_result = self.supabase.rpc("get_index_count").execute()
            index_count = (
                index_result.data[0].get("count", 0)
                if index_result and index_result.data
                else 0
            )

            # Check RLS
            rls_result = await self.check_rls_enabled()
            rls_enabled = rls_result.status == "healthy"

            return DatabaseHealthMetrics(
                connection_status=connection_status,
                response_time_ms=response_time,
                rls_enabled=rls_enabled,
                table_count=table_count,
                index_count=index_count,
            )

        except Exception as e:
            logger.error(f"Error getting health metrics: {e}")
            return DatabaseHealthMetrics(
                connection_status=False,
                response_time_ms=0,
                rls_enabled=False,
                table_count=0,
                index_count=0,
            )


# Global health checker instance
_health_checker: Optional[DatabaseHealthChecker] = None


def get_health_checker() -> DatabaseHealthChecker:
    """Get global health checker singleton"""
    global _health_checker
    if _health_checker is None:
        _health_checker = DatabaseHealthChecker()
    return _health_checker


# Convenience functions
async def check_database_health() -> Dict[str, HealthCheckResult]:
    """Get comprehensive database health report"""
    return await get_health_checker().get_comprehensive_health()


async def get_database_metrics() -> DatabaseHealthMetrics:
    """Get database health metrics"""
    return await get_health_checker().get_health_metrics()
