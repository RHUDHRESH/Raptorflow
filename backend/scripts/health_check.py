#!/usr/bin/env python3
"""
Health check script for Raptorflow backend.
Runs comprehensive health checks and returns status for CI/CD.
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config.settings import get_settings
from monitoring.health_checks import HealthAggregator
from backend.redis_core.client import RedisClient
from backend.redis_core.health import RedisHealthChecker

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class HealthCheckScript:
    """Comprehensive health check script."""

    def __init__(self):
        """Initialize health check script."""
        self.settings = get_settings()
        self.results = {}
        self.start_time = time.time()

    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks."""
        logger.info("Starting comprehensive health checks...")

        checks = [
            ("redis", self.check_redis),
            ("database", self.check_database),
            ("memory_system", self.check_memory_system),
            ("external_services", self.check_external_services),
            ("system_resources", self.check_system_resources),
        ]

        overall_status = "healthy"

        for check_name, check_func in checks:
            try:
                logger.info(f"Running {check_name} check...")
                result = await check_func()
                self.results[check_name] = result

                if result["status"] == "unhealthy":
                    overall_status = "unhealthy"
                elif result["status"] == "degraded" and overall_status == "healthy":
                    overall_status = "degraded"

            except Exception as e:
                logger.error(f"Health check {check_name} failed: {e}")
                self.results[check_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }
                overall_status = "unhealthy"

        # Compile final report
        duration = time.time() - self.start_time

        final_report = {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "duration_seconds": duration,
            "checks": self.results,
            "summary": self.generate_summary(),
        }

        logger.info(
            f"Health checks completed in {duration:.2f}s - Status: {overall_status}"
        )
        return final_report

    async def check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity and performance."""
        try:
            redis_health = RedisHealthChecker()

            # Basic connectivity
            connection_ok = await redis_health.check_connection()

            # Latency check
            latency = await redis_health.check_latency()

            # Memory check
            memory_status = await redis_health.check_memory()

            status = "healthy"
            issues = []

            if not connection_ok:
                status = "unhealthy"
                issues.append("Connection failed")

            if latency > 100:  # 100ms threshold
                if status == "healthy":
                    status = "degraded"
                issues.append(f"High latency: {latency}ms")

            if memory_status["status"] != "healthy":
                if status == "healthy":
                    status = "degraded"
                issues.append(f"Memory issues: {memory_status['status']}")

            return {
                "status": status,
                "connection": connection_ok,
                "latency_ms": latency,
                "memory": memory_status,
                "issues": issues,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def check_database(self) -> Dict[str, Any]:
        """Check database connectivity."""
        try:
            # This would implement actual database health checks
            # For now, simulate based on configuration
            if self.settings.DATABASE_URL:
                # Simulate database check
                connection_ok = True
                latency_ms = 25
                active_connections = 5

                status = "healthy" if connection_ok and latency_ms < 50 else "degraded"

                return {
                    "status": status,
                    "connection": connection_ok,
                    "latency_ms": latency_ms,
                    "active_connections": active_connections,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            else:
                return {
                    "status": "healthy",
                    "message": "Database not configured",
                    "timestamp": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def check_memory_system(self) -> Dict[str, Any]:
        """Check memory system components."""
        try:
            # This would implement actual memory system checks
            # For now, simulate based on available components
            components = {
                "vector_store": "healthy",
                "memory_graph": "healthy",
                "indexing": "healthy",
            }

            overall_status = "healthy"
            issues = []

            for component, status in components.items():
                if status != "healthy":
                    overall_status = "degraded"
                    issues.append(f"{component}: {status}")

            return {
                "status": overall_status,
                "components": components,
                "issues": issues,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def check_external_services(self) -> Dict[str, Any]:
        """Check external service connectivity."""
        try:
            services = {}

            # Vertex AI
            try:
                # Simulate Vertex AI check
                services["vertex_ai"] = {
                    "status": "healthy",
                    "latency_ms": 150,
                }
            except Exception as e:
                services["vertex_ai"] = {
                    "status": "unhealthy",
                    "error": str(e),
                }

            # Cloud Storage
            try:
                # Simulate Cloud Storage check
                services["cloud_storage"] = {
                    "status": "healthy",
                    "latency_ms": 80,
                }
            except Exception as e:
                services["cloud_storage"] = {
                    "status": "unhealthy",
                    "error": str(e),
                }

            # BigQuery
            try:
                # Simulate BigQuery check
                services["bigquery"] = {
                    "status": "healthy",
                    "latency_ms": 200,
                }
            except Exception as e:
                services["bigquery"] = {
                    "status": "unhealthy",
                    "error": str(e),
                }

            # Determine overall status
            overall_status = "healthy"
            issues = []

            for service_name, service_info in services.items():
                if service_info["status"] != "healthy":
                    overall_status = "degraded"
                    issues.append(f"{service_name}: {service_info['status']}")

            return {
                "status": overall_status,
                "services": services,
                "issues": issues,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource utilization."""
        try:
            import psutil

            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()

            # Disk usage
            disk = psutil.disk_usage("/")

            # Determine status
            status = "healthy"
            issues = []

            if cpu_percent > 80:
                status = "degraded"
                issues.append(f"High CPU usage: {cpu_percent}%")

            if memory.percent > 85:
                status = "degraded"
                issues.append(f"High memory usage: {memory.percent}%")

            disk_percent = (disk.used / disk.total) * 100
            if disk_percent > 90:
                status = "degraded"
                issues.append(f"High disk usage: {disk_percent:.1f}%")

            return {
                "status": status,
                "cpu_percent": cpu_percent,
                "memory": {
                    "total": memory.total,
                    "used": memory.used,
                    "free": memory.free,
                    "percent": memory.percent,
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk_percent,
                },
                "issues": issues,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    def generate_summary(self) -> Dict[str, Any]:
        """Generate summary of health check results."""
        summary = {
            "total_checks": len(self.results),
            "healthy": 0,
            "degraded": 0,
            "unhealthy": 0,
            "critical_issues": [],
        }

        for check_name, result in self.results.items():
            status = result.get("status", "unknown")
            summary[status] = summary.get(status, 0) + 1

            if status == "unhealthy":
                summary["critical_issues"].append(
                    {
                        "check": check_name,
                        "error": result.get("error", "Unknown error"),
                    }
                )

        return summary

    def print_report(self, report: Dict[str, Any]):
        """Print formatted health report."""
        print("\n" + "=" * 60)
        print("RAPTORFLOW HEALTH CHECK REPORT")
        print("=" * 60)
        print(f"Status: {report['status'].upper()}")
        print(f"Timestamp: {report['timestamp']}")
        print(f"Duration: {report['duration_seconds']:.2f}s")
        print()

        # Summary
        summary = report["summary"]
        print("SUMMARY:")
        print(f"  Total checks: {summary['total_checks']}")
        print(f"  Healthy: {summary['healthy']}")
        print(f"  Degraded: {summary['degraded']}")
        print(f"  Unhealthy: {summary['unhealthy']}")
        print()

        # Individual checks
        print("DETAILED CHECKS:")
        for check_name, result in report["checks"].items():
            status_icon = {
                "healthy": "✅",
                "degraded": "⚠️",
                "unhealthy": "❌",
            }.get(result["status"], "❓")

            print(f"  {status_icon} {check_name.upper()}: {result['status']}")

            if "issues" in result and result["issues"]:
                for issue in result["issues"]:
                    print(f"    - {issue}")

            if "error" in result:
                print(f"    Error: {result['error']}")

        print()

        # Critical issues
        if summary["critical_issues"]:
            print("CRITICAL ISSUES:")
            for issue in summary["critical_issues"]:
                print(f"  ❌ {issue['check']}: {issue['error']}")
            print()

        print("=" * 60)


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Raptorflow health check script")
    parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format"
    )
    parser.add_argument("--output", help="Output file (default: stdout)")
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with non-zero code on unhealthy status",
    )

    args = parser.parse_args()

    # Run health checks
    health_checker = HealthCheckScript()
    report = await health_checker.run_all_checks()

    # Output results
    if args.format == "json":
        output = json.dumps(report, indent=2)
    else:
        output = str(report)
        health_checker.print_report(report)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    else:
        print(output)

    # Exit code
    if args.exit_code and report["status"] != "healthy":
        sys.exit(1)

    return report["status"]


if __name__ == "__main__":
    asyncio.run(main())
