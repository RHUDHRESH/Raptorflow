"""
Agent Executions repository for database operations
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from filters import Filter, build_query
from pagination import PaginatedResult, Pagination

from .base import Repository
from .core.supabase_mgr import get_supabase_client


class AgentExecutionRepository(Repository):
    """Repository for agent execution operations"""

    def __init__(self):
        super().__init__(get_supabase_client())

    async def create_execution(
        self,
        workspace_id: str,
        user_id: str,
        session_id: str,
        agent_name: str,
        input_data: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Create a new agent execution"""
        execution_data = {
            "workspace_id": workspace_id,
            "user_id": user_id,
            "session_id": session_id,
            "agent_name": agent_name,
            "input": input_data,
            "status": "running",
            "tokens_used": 0,
            "cost_usd": 0,
            "started_at": datetime.utcnow().isoformat(),
        }

        result = self.client.table("agent_executions").insert(execution_data).execute()

        if result.data:
            return result.data[0]
        return None

    async def complete_execution(
        self,
        execution_id: str,
        output_data: Dict[str, Any],
        tokens_used: int,
        cost_usd: float,
    ) -> Optional[Dict[str, Any]]:
        """Complete an agent execution with results"""
        update_data = {
            "output": output_data,
            "tokens_used": tokens_used,
            "cost_usd": cost_usd,
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
        }

        result = (
            self.client.table("agent_executions")
            .update(update_data)
            .eq("id", execution_id)
            .execute()
        )

        if result.data:
            return result.data[0]
        return None

    async def fail_execution(
        self, execution_id: str, error_message: str
    ) -> Optional[Dict[str, Any]]:
        """Mark an agent execution as failed"""
        update_data = {
            "status": "failed",
            "error": error_message,
            "completed_at": datetime.utcnow().isoformat(),
        }

        result = (
            self.client.table("agent_executions")
            .update(update_data)
            .eq("id", execution_id)
            .execute()
        )

        if result.data:
            return result.data[0]
        return None

    async def get_by_session(
        self, session_id: str, pagination: Optional[Pagination] = None
    ) -> PaginatedResult:
        """Get all executions for a session"""
        query = (
            self.client.table("agent_executions")
            .select("*")
            .eq("session_id", session_id)
        )

        if pagination:
            query = query.order("started_at", desc=True).range(
                pagination.page * pagination.page_size,
                (pagination.page + 1) * pagination.page_size - 1,
            )

        result = query.execute()

        if pagination:
            count_result = (
                self.client.table("agent_executions")
                .select("id", count="exact")
                .eq("session_id", session_id)
                .execute()
            )
            total = count_result.count or 0

            return PaginatedResult(
                items=result.data or [],
                total=total,
                page=pagination.page,
                page_size=pagination.page_size,
                total_pages=(total + pagination.page_size - 1) // pagination.page_size,
            )

        return PaginatedResult(
            items=result.data or [],
            total=len(result.data or []),
            page=0,
            page_size=len(result.data or []),
            total_pages=1,
        )

    async def get_running_executions(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get all currently running executions for a workspace"""
        result = (
            self.client.table("agent_executions")
            .select("*")
            .eq("workspace_id", workspace_id)
            .eq("status", "running")
            .order("started_at", desc=True)
            .execute()
        )
        return result.data or []

    async def get_executions_by_agent(
        self,
        workspace_id: str,
        agent_name: str,
        pagination: Optional[Pagination] = None,
    ) -> PaginatedResult:
        """Get executions for a specific agent"""
        query = (
            self.client.table("agent_executions")
            .select("*")
            .eq("workspace_id", workspace_id)
            .eq("agent_name", agent_name)
        )

        if pagination:
            query = query.order("started_at", desc=True).range(
                pagination.page * pagination.page_size,
                (pagination.page + 1) * pagination.page_size - 1,
            )

        result = query.execute()

        if pagination:
            count_result = (
                self.client.table("agent_executions")
                .select("id", count="exact")
                .eq("workspace_id", workspace_id)
                .eq("agent_name", agent_name)
                .execute()
            )
            total = count_result.count or 0

            return PaginatedResult(
                items=result.data or [],
                total=total,
                page=pagination.page,
                page_size=pagination.page_size,
                total_pages=(total + pagination.page_size - 1) // pagination.page_size,
            )

        return PaginatedResult(
            items=result.data or [],
            total=len(result.data or []),
            page=0,
            page_size=len(result.data or []),
            total_pages=1,
        )

    async def get_execution_metrics(
        self, workspace_id: str, hours: int = 24
    ) -> Dict[str, Any]:
        """Get execution metrics for recent time period"""
        from datetime import timedelta

        cutoff_time = (datetime.utcnow() - timedelta(hours=hours)).isoformat()

        # Get recent executions
        result = (
            self.client.table("agent_executions")
            .select("*")
            .eq("workspace_id", workspace_id)
            .gte("started_at", cutoff_time)
            .execute()
        )
        executions = result.data or []

        if not executions:
            return {
                "workspace_id": workspace_id,
                "hours_analyzed": hours,
                "total_executions": 0,
            }

        # Calculate metrics
        total_executions = len(executions)
        completed_executions = len(
            [e for e in executions if e.get("status") == "completed"]
        )
        failed_executions = len([e for e in executions if e.get("status") == "failed"])
        running_executions = len(
            [e for e in executions if e.get("status") == "running"]
        )

        # Token and cost metrics
        total_tokens = sum(e.get("tokens_used", 0) for e in executions)
        total_cost = sum(e.get("cost_usd", 0) for e in executions)

        # Performance metrics
        completed_executions_with_duration = [
            e
            for e in executions
            if e.get("status") == "completed"
            and e.get("started_at")
            and e.get("completed_at")
        ]
        execution_times = []

        for exec_data in completed_executions_with_duration:
            start_time = datetime.fromisoformat(
                exec_data["started_at"].replace("Z", "+00:00")
            )
            end_time = datetime.fromisoformat(
                exec_data["completed_at"].replace("Z", "+00:00")
            )
            duration_seconds = (end_time - start_time).total_seconds()
            execution_times.append(duration_seconds)

        avg_execution_time = (
            sum(execution_times) / len(execution_times) if execution_times else 0
        )

        # Success rate
        success_rate = (
            (completed_executions / total_executions * 100)
            if total_executions > 0
            else 0
        )

        # Agent breakdown
        agent_stats = {}
        for execution in executions:
            agent = execution.get("agent_name", "unknown")
            if agent not in agent_stats:
                agent_stats[agent] = {
                    "total": 0,
                    "completed": 0,
                    "failed": 0,
                    "tokens": 0,
                    "cost": 0,
                }

            agent_stats[agent]["total"] += 1
            agent_stats[agent]["tokens"] += execution.get("tokens_used", 0)
            agent_stats[agent]["cost"] += execution.get("cost_usd", 0)

            if execution.get("status") == "completed":
                agent_stats[agent]["completed"] += 1
            elif execution.get("status") == "failed":
                agent_stats[agent]["failed"] += 1

        return {
            "workspace_id": workspace_id,
            "hours_analyzed": hours,
            "total_executions": total_executions,
            "completed_executions": completed_executions,
            "failed_executions": failed_executions,
            "running_executions": running_executions,
            "success_rate": success_rate,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "avg_execution_time_seconds": avg_execution_time,
            "agent_breakdown": agent_stats,
        }

    async def get_agent_performance_history(
        self, workspace_id: str, agent_name: str, days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get performance history for a specific agent"""
        from datetime import timedelta

        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

        result = (
            self.client.table("agent_executions")
            .select("*")
            .eq("workspace_id", workspace_id)
            .eq("agent_name", agent_name)
            .gte("started_at", start_date)
            .order("started_at")
            .execute()
        )
        executions = result.data or []

        # Group by day
        daily_stats = {}
        for execution in executions:
            date = execution["started_at"][:10]  # Extract date part

            if date not in daily_stats:
                daily_stats[date] = {
                    "date": date,
                    "total_executions": 0,
                    "completed_executions": 0,
                    "failed_executions": 0,
                    "total_tokens": 0,
                    "total_cost": 0,
                    "avg_execution_time": 0,
                    "execution_times": [],
                }

            stats = daily_stats[date]
            stats["total_executions"] += 1
            stats["total_tokens"] += execution.get("tokens_used", 0)
            stats["total_cost"] += execution.get("cost_usd", 0)

            if execution.get("status") == "completed":
                stats["completed_executions"] += 1
            elif execution.get("status") == "failed":
                stats["failed_executions"] += 1

            # Calculate execution time
            if execution.get("started_at") and execution.get("completed_at"):
                start_time = datetime.fromisoformat(
                    execution["started_at"].replace("Z", "+00:00")
                )
                end_time = datetime.fromisoformat(
                    execution["completed_at"].replace("Z", "+00:00")
                )
                duration_seconds = (end_time - start_time).total_seconds()
                stats["execution_times"].append(duration_seconds)

        # Calculate averages
        for date, stats in daily_stats.items():
            if stats["execution_times"]:
                stats["avg_execution_time"] = sum(stats["execution_times"]) / len(
                    stats["execution_times"]
                )
            else:
                stats["avg_execution_time"] = 0

            # Remove temporary array
            del stats["execution_times"]

        return list(daily_stats.values())

    async def get_error_analysis(
        self, workspace_id: str, days: int = 7
    ) -> Dict[str, Any]:
        """Analyze errors from failed executions"""
        from collections import Counter
        from datetime import timedelta

        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

        # Get failed executions
        result = (
            self.client.table("agent_executions")
            .select("*")
            .eq("workspace_id", workspace_id)
            .eq("status", "failed")
            .gte("started_at", start_date)
            .execute()
        )
        failed_executions = result.data or []

        if not failed_executions:
            return {
                "workspace_id": workspace_id,
                "days_analyzed": days,
                "total_failures": 0,
            }

        # Analyze errors
        error_messages = [e.get("error", "Unknown error") for e in failed_executions]
        error_counter = Counter(error_messages)

        # Group by agent
        agent_errors = {}
        for execution in failed_executions:
            agent = execution.get("agent_name", "unknown")
            if agent not in agent_errors:
                agent_errors[agent] = {"total": 0, "errors": []}

            agent_errors[agent]["total"] += 1
            agent_errors[agent]["errors"].append(
                execution.get("error", "Unknown error")
            )

        # Most common errors
        common_errors = error_counter.most_common(10)

        return {
            "workspace_id": workspace_id,
            "days_analyzed": days,
            "total_failures": len(failed_executions),
            "failure_rate": (len(failed_executions) / (len(failed_executions) + 1))
            * 100,  # Rough estimate
            "common_errors": [
                {"error": error, "count": count} for error, count in common_errors
            ],
            "agent_errors": agent_errors,
        }

    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running execution"""
        # Check if execution is running
        execution = await self.get(execution_id)
        if not execution or execution.get("status") != "running":
            return False

        update_data = {
            "status": "cancelled",
            "completed_at": datetime.utcnow().isoformat(),
            "error": "Execution cancelled by user",
        }

        result = (
            self.client.table("agent_executions")
            .update(update_data)
            .eq("id", execution_id)
            .execute()
        )
        return len(result.data or []) > 0

    async def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of all executions in a session"""
        executions_result = (
            self.client.table("agent_executions")
            .select("*")
            .eq("session_id", session_id)
            .execute()
        )
        executions = executions_result.data or []

        if not executions:
            return {"session_id": session_id, "total_executions": 0}

        # Calculate summary metrics
        total_executions = len(executions)
        completed_executions = len(
            [e for e in executions if e.get("status") == "completed"]
        )
        failed_executions = len([e for e in executions if e.get("status") == "failed"])
        running_executions = len(
            [e for e in executions if e.get("status") == "running"]
        )

        total_tokens = sum(e.get("tokens_used", 0) for e in executions)
        total_cost = sum(e.get("cost_usd", 0) for e in executions)

        # Session duration
        if executions:
            start_time = min(e["started_at"] for e in executions)
            end_time = max(e.get("completed_at", e["started_at"]) for e in executions)
            start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            duration_seconds = (end_dt - start_dt).total_seconds()
        else:
            duration_seconds = 0

        # Agent breakdown
        agents_used = list(set(e.get("agent_name", "unknown") for e in executions))

        return {
            "session_id": session_id,
            "total_executions": total_executions,
            "completed_executions": completed_executions,
            "failed_executions": failed_executions,
            "running_executions": running_executions,
            "success_rate": (
                (completed_executions / total_executions * 100)
                if total_executions > 0
                else 0
            ),
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "duration_seconds": duration_seconds,
            "agents_used": agents_used,
            "started_at": start_time if executions else None,
            "ended_at": end_time if executions else None,
        }

    async def cleanup_old_executions(
        self, workspace_id: str, days_old: int = 30
    ) -> int:
        """Clean up old completed executions"""
        from datetime import timedelta

        cutoff_date = (datetime.utcnow() - timedelta(days=days_old)).isoformat()

        result = (
            self.client.table("agent_executions")
            .delete()
            .eq("workspace_id", workspace_id)
            .lt("started_at", cutoff_date)
            .in_("status", ["completed", "failed", "cancelled"])
            .execute()
        )

        return len(result.data or [])

    async def get_cost_analysis(
        self, workspace_id: str, days: int = 30
    ) -> Dict[str, Any]:
        """Get cost analysis for executions"""
        from datetime import timedelta

        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

        # Get executions in date range
        result = (
            self.client.table("agent_executions")
            .select("*")
            .eq("workspace_id", workspace_id)
            .gte("started_at", start_date)
            .execute()
        )
        executions = result.data or []

        if not executions:
            return {
                "workspace_id": workspace_id,
                "days_analyzed": days,
                "total_cost": 0,
            }

        # Calculate cost metrics
        total_cost = sum(e.get("cost_usd", 0) for e in executions)
        total_tokens = sum(e.get("tokens_used", 0) for e in executions)

        # Cost by agent
        agent_costs = {}
        for execution in executions:
            agent = execution.get("agent_name", "unknown")
            if agent not in agent_costs:
                agent_costs[agent] = {"cost": 0, "tokens": 0, "executions": 0}

            agent_costs[agent]["cost"] += execution.get("cost_usd", 0)
            agent_costs[agent]["tokens"] += execution.get("tokens_used", 0)
            agent_costs[agent]["executions"] += 1

        # Daily cost breakdown
        daily_costs = {}
        for execution in executions:
            date = execution["started_at"][:10]
            if date not in daily_costs:
                daily_costs[date] = 0
            daily_costs[date] += execution.get("cost_usd", 0)

        # Calculate averages
        avg_cost_per_execution = total_cost / len(executions) if executions else 0
        avg_cost_per_token = total_cost / total_tokens if total_tokens > 0 else 0

        return {
            "workspace_id": workspace_id,
            "days_analyzed": days,
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "total_executions": len(executions),
            "avg_cost_per_execution": avg_cost_per_execution,
            "avg_cost_per_token": avg_cost_per_token,
            "agent_costs": agent_costs,
            "daily_costs": daily_costs,
        }
