"""
Monitoring Service

Provides system health monitoring and agent activity analysis.
Realizes the "Console of Loads" concept by offering comprehensive
visibility into agent operations and system status.
"""

import structlog
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
from uuid import UUID

from backend.services.supabase_client import supabase_client
from backend.services.vertex_ai_client import vertex_ai_client

logger = structlog.get_logger(__name__)


class MonitoringService:
    """
    Service for monitoring system health and agent activity.

    This service provides the "Console of Loads" - comprehensive visibility
    into agent operations, system health, and performance metrics. It tracks
    costs, errors, and system status to help operators understand what's
    happening in the RaptorFlow system at a glance.

    Key Capabilities:
    - Cost monitoring and reporting (24h activity summaries)
    - Agent performance tracking (top active agents)
    - System health checks (database, LLM API status)
    - Real-time operational metrics
    - Administrative dashboard data

    Integration Points:
    - External monitoring APIs (Vertex AI, Supabase)
    - Cost tracking system (queries cost_logs table)
    - Administrative dashboards and alerts
    - Performance monitoring and alerting systems
    """

    def __init__(self):
        """Initialize the monitoring service."""
        logger.info("Monitoring Service initialized - 'Console of Loads' activated")
        self.supabase = supabase_client

    async def get_agent_activity_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive agent activity summary for the last 24 hours.

        Queries the cost_logs table to provide real-time insights into
        agent operations, costs, and activity patterns. This method
        realizes the core "Console of Loads" vision.

        Returns:
            Dictionary containing:
            - total_actions_last_24h: Total number of agent actions in past 24h
            - total_cost_last_24h: Total estimated cost in USD for past 24h
            - top_5_active_agents: List of top 5 agents by action count

        Example:
            {
                "total_actions_last_24h": 245,
                "total_cost_last_24h": 12.45,
                "top_5_active_agents": [
                    {"agent_name": "ResearchAgent", "action_count": 45},
                    {"agent_name": "StrategyAgent", "action_count": 38},
                    ...
                ]
            }
        """
        logger.info("Generating 24h agent activity summary")

        try:
            # Calculate time range for past 24 hours
            twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)

            # Query total actions and costs in past 24h
            query = self.supabase.client.table("cost_logs").select(
                "agent_name, action_name, estimated_cost_usd"
            ).gte("created_at", twenty_four_hours_ago.isoformat())

            result = query.execute()
            records = result.data or []

            # Calculate totals
            total_actions = len(records)
            total_cost = sum(float(record["estimated_cost_usd"]) for record in records)

            # Aggregate by agent for top performers
            agent_counts = {}
            for record in records:
                agent_name = record["agent_name"]
                agent_counts[agent_name] = agent_counts.get(agent_name, 0) + 1

            # Get top 5 active agents
            top_agents = sorted(agent_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            top_5_active_agents = [
                {"agent_name": agent_name, "action_count": count}
                for agent_name, count in top_agents
            ]

            summary = {
                "total_actions_last_24h": total_actions,
                "total_cost_last_24h": round(total_cost, 4),
                "top_5_active_agents": top_5_active_agents,
                "period_start": twenty_four_hours_ago.isoformat(),
                "period_end": datetime.utcnow().isoformat()
            }

            logger.info(
                "Agent activity summary generated",
                total_actions=total_actions,
                total_cost=total_cost,
                unique_agents=len(agent_counts)
            )

            return summary

        except Exception as e:
            logger.error("Failed to generate agent activity summary", error=str(e))

            # Return minimal fallback data
            return {
                "total_actions_last_24h": 0,
                "total_cost_last_24h": 0.0,
                "top_5_active_agents": [],
                "error": str(e),
                "period_start": None,
                "period_end": None
            }

    async def get_system_health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive system health check.

        Checks critical external dependencies and internal systems to provide
        a complete health assessment. This mirrors infrastructure monitoring
        but focuses on AI/agent system components.

        Returns:
            Dictionary containing health status for each component:
            - database_connection: OK/FAIL
            - llm_api_status: OK/FAIL
            - overall_status: HEALTHY/DEGRADED/UNHEALTHY

        Example:
            {
                "database_connection": "OK",
                "llm_api_status": "OK",
                "overall_status": "HEALTHY",
                "check_timestamp": "2025-01-27T12:34:56Z",
                "response_time_ms": 245
            }
        """
        start_time = datetime.utcnow()
        logger.info("Performing system health check")

        health_checks = {}

        try:
            # 1. Database connectivity check
            try:
                # Simple query to test database connection
                test_query = self.supabase.client.table("cost_logs").select("id").limit(1)
                result = test_query.execute()
                health_checks["database_connection"] = "OK"
                logger.debug("Database connection check passed")
            except Exception as db_error:
                health_checks["database_connection"] = "FAIL"
                logger.warning("Database connection check failed", error=str(db_error))

            # 2. LLM API status check
            try:
                # Simple LLM call to test API connectivity
                test_response = await vertex_ai_client.generate_text(
                    prompt="Test connectivity - respond with 'OK'",
                    model_type="fast",
                    max_tokens=10,
                    temperature=0.0
                )

                if test_response and len(test_response.strip()) > 0:
                    health_checks["llm_api_status"] = "OK"
                    logger.debug("LLM API connectivity check passed")
                else:
                    health_checks["llm_api_status"] = "FAIL"
                    logger.warning("LLM API response check failed")

            except Exception as llm_error:
                health_checks["llm_api_status"] = "FAIL"
                logger.warning("LLM API connectivity check failed", error=str(llm_error))

            # Determine overall status
            ok_checks = sum(1 for status in health_checks.values() if status == "OK")
            total_checks = len(health_checks)

            if ok_checks == total_checks:
                overall_status = "HEALTHY"
            elif ok_checks >= total_checks / 2:  # At least half services working
                overall_status = "DEGRADED"
            else:
                overall_status = "UNHEALTHY"

            health_checks["overall_status"] = overall_status

            # Add metadata
            end_time = datetime.utcnow()
            health_checks["check_timestamp"] = end_time.isoformat()
            health_checks["response_time_ms"] = int((end_time - start_time).total_seconds() * 1000)

            logger.info(
                "System health check completed",
                overall_status=overall_status,
                ok_checks=f"{ok_checks}/{total_checks}",
                response_time_ms=health_checks["response_time_ms"]
            )

            return health_checks

        except Exception as e:
            logger.error("System health check failed catastrophically", error=str(e))

            # Return minimal emergency data
            return {
                "database_connection": "UNKNOWN",
                "llm_api_status": "UNKNOWN",
                "overall_status": "UNKNOWN",
                "error": str(e),
                "check_timestamp": datetime.utcnow().isoformat()
            }

    async def get_cost_overview_by_agent(self, days: int = 7) -> Dict[str, Any]:
        """
        Get detailed cost breakdown by agent over a specified period.

        Provides granular visibility into which agents are consuming costs,
        useful for optimization and resource allocation decisions.

        Args:
            days: Number of days to analyze (default 7)

        Returns:
            Dictionary with agent-by-agent cost breakdown and trends
        """
        logger.info("Generating cost overview by agent", days=days)

        try:
            # Calculate start date
            start_date = datetime.utcnow() - timedelta(days=days)

            # Query cost data
            query = self.supabase.client.table("cost_logs").select(
                "agent_name, estimated_cost_usd, created_at"
            ).gte("created_at", start_date.isoformat()).order("created_at")

            result = query.execute()
            records = result.data or []

            # Aggregate costs by agent
            agent_costs = {}
            for record in records:
                agent_name = record["agent_name"]
                cost = float(record["estimated_cost_usd"])
                created_at = datetime.fromisoformat(record["created_at"])

                if agent_name not in agent_costs:
                    agent_costs[agent_name] = {
                        "total_cost": 0.0,
                        "action_count": 0,
                        "daily_costs": {},
                        "first_action": created_at,
                        "last_action": created_at
                    }

                agent_data = agent_costs[agent_name]
                agent_data["total_cost"] += cost
                agent_data["action_count"] += 1

                # Track daily costs
                day_key = created_at.strftime("%Y-%m-%d")
                agent_data["daily_costs"][day_key] = agent_data["daily_costs"].get(day_key, 0) + cost

                # Update first/last timestamps
                if created_at < agent_data["first_action"]:
                    agent_data["first_action"] = created_at
                if created_at > agent_data["last_action"]:
                    agent_data["last_action"] = created_at

            # Calculate additional metrics
            for agent_data in agent_costs.values():
                agent_data["avg_cost_per_action"] = agent_data["total_cost"] / agent_data["action_count"] if agent_data["action_count"] > 0 else 0

            return {
                "period_days": days,
                "start_date": start_date.isoformat(),
                "total_cost": sum(agent["total_cost"] for agent in agent_costs.values()),
                "total_actions": sum(agent["action_count"] for agent in agent_costs.values()),
                "agent_costs": agent_costs
            }

        except Exception as e:
            logger.error("Agent cost overview generation failed", error=str(e))
            return {"error": str(e)}

    async def get_system_status_summary(self) -> Dict[str, Any]:
        """
        Get complete system monitoring snapshot.

        This is the primary API endpoint that combines all monitoring data
        into a comprehensive "Console of Loads" view. It provides immediate
        visibility into system health, agent activity, and operational status.

        Returns:
            Complete monitoring snapshot combining:
            - Agent activity summary (24h)
            - System health status
            - Cost breakdowns
            - Operational metadata
        """
        logger.info("Generating complete system monitoring snapshot")

        try:
            # Gather all monitoring data concurrently
            activity_summary = await self.get_agent_activity_summary()
            health_status = await self.get_system_health_check()
            cost_overview = await self.get_cost_overview_by_agent(days=7)

            # Combine into comprehensive snapshot
            system_snapshot = {
                # Core health indicators
                "timestamp": datetime.utcnow().isoformat(),
                "overall_status": health_status.get("overall_status", "UNKNOWN"),

                # Agent activity metrics (last 24h)
                "agent_activity": {
                    "total_actions": activity_summary["total_actions_last_24h"],
                    "total_cost": activity_summary["total_cost_last_24h"],
                    "period_start": activity_summary.get("period_start"),
                    "period_end": activity_summary.get("period_end")
                },

                # System health components
                "system_health": {
                    "database_connection": health_status.get("database_connection", "UNKNOWN"),
                    "llm_api_status": health_status.get("llm_api_status", "UNKNOWN"),
                    "response_time_ms": health_status.get("response_time_ms", 0)
                },

                # Agent performance leaderboard
                "top_agents": activity_summary["top_5_active_agents"],

                # Weekly cost trends (for trending analysis)
                "weekly_cost_breakdown": {
                    "total_cost": cost_overview.get("total_cost", 0),
                    "total_actions": cost_overview.get("total_actions", 0),
                    "cost_by_agent_count": len(cost_overview.get("agent_costs", {}))
                },

                # Metadata for monitoring systems
                "monitoring_metadata": {
                    "check_duration_ms": health_status.get("response_time_ms", 0),
                    "is_real_time": True,
                    "version": "1.0.0"
                }
            }

            # Add error indicators if present
            if activity_summary.get("error"):
                system_snapshot["errors"] = [activity_summary["error"]]
            if health_status.get("error"):
                if "errors" not in system_snapshot:
                    system_snapshot["errors"] = []
                system_snapshot["errors"].append(health_status["error"])

            logger.info(
                "System monitoring snapshot completed",
                overall_status=system_snapshot["overall_status"],
                total_actions=system_snapshot["agent_activity"]["total_actions"],
                total_cost=system_snapshot["agent_activity"]["total_cost"]
            )

            return system_snapshot

        except Exception as e:
            logger.error("Failed to generate system monitoring snapshot", error=str(e))

            # Return critical emergency status
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "overall_status": "CRITICAL_ERROR",
                "error": str(e),
                "agent_activity": {"total_actions": 0, "total_cost": 0.0},
                "system_health": {"database_connection": "UNKNOWN", "llm_api_status": "UNKNOWN"},
                "top_agents": []
            }


# Global service instance
monitoring_service = MonitoringService()
