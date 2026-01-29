#!/usr/bin/env python3
"""
Absolute Infinity Campaign Ticker
Refactored for Supabase-backed job queuing and Fluid Rescheduling (Breathing Arcs).
"""

import asyncio
import logging
from datetime import datetime, timedelta, UTC
from typing import Dict, List, Any, Optional

from synapse import brain
from core.supabase_mgr import get_supabase_client

logger = logging.getLogger("ticker")


class CampaignTicker:
    """
    Background loop for scheduled strategic execution.
    Uses the Supabase 'scheduled_tasks' table as a high-fidelity job queue.
    """

    def __init__(self):
        self.client = get_supabase_client()
        self.running = False
        self.check_interval = 60  # seconds

    def _calculate_next_run(self, schedule: str) -> datetime:
        """Calculate next run time based on schedule string"""
        now = datetime.now(UTC)
        if schedule == "hourly":
            return now + timedelta(hours=1)
        elif schedule == "daily":
            return now + timedelta(days=1)
        elif schedule == "weekly":
            return now + timedelta(weeks=1)
        else:
            return now + timedelta(hours=1)  # Default

    async def add_task(
        self,
        workspace_id: str,
        task_type: str,
        payload: Dict,
        scheduled_for: datetime,
        move_id: Optional[str] = None,
    ):
        """Add a new task to the persistent Supabase queue"""
        try:
            self.client.table("scheduled_tasks").insert(
                {
                    "workspace_id": workspace_id,
                    "move_id": move_id,
                    "task_type": task_type,
                    "payload": payload,
                    "scheduled_for": scheduled_for.isoformat(),
                    "status": "pending",
                }
            ).execute()
            logger.info(f"📅 Task added: {task_type} for workspace {workspace_id}")
        except Exception as e:
            logger.error(f"❌ Ticker: Failed to add task: {e}")

    async def start_ticker(self):
        """Start the background ticker loop"""
        self.running = True
        logger.info("🚀 Absolute Infinity Ticker Started")

        while self.running:
            try:
                await self._process_due_tasks()
                await self._handle_pushbacks()  # Fluid rescheduling logic
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"🔥 Ticker main loop error: {e}")
                await asyncio.sleep(self.check_interval)

    async def _process_due_tasks(self):
        """Process tasks that are due for execution"""
        try:
            now = datetime.now(UTC).isoformat()

            # 1. Fetch pending tasks due now
            result = (
                self.client.table("scheduled_tasks")
                .select("*")
                .eq("status", "pending")
                .lte("scheduled_for", now)
                .order("priority", desc=True)
                .limit(10)
                .execute()
            )

            tasks = result.data or []

            for task in tasks:
                await self._execute_task(task)

        except Exception as e:
            logger.error(f"❌ Ticker: Error checking due tasks: {e}")

    async def _execute_task(self, task: Dict):
        """Execute a single task via Synapse nodes"""
        task_id = task["id"]
        task_type = task["task_type"]
        payload = task["payload"]
        workspace_id = task["workspace_id"]

        logger.info(f"⚡ Executing Task {task_id}: {task_type}")

        try:
            # Mark as processing
            self.client.table("scheduled_tasks").update({"status": "processing"}).eq(
                "id", task_id
            ).execute()

            start_time = datetime.now(UTC)

            # Context for Synapse
            context = {
                "workspace_id": workspace_id,
                "task_id": task_id,
                "move_id": task.get("move_id"),
                **payload,
            }

            # Logic branch by task_type
            if task_type == "move_execution":
                move_name = payload.get("move_name")
                result = await brain.run_move(
                    move_name, context, flow_id=task.get("move_id") or "task_run"
                )
            elif task_type == "node_execution":
                node_name = payload.get("node_name")
                result = await brain.run_node(node_name, context)
            else:
                logger.warning(f"⚠️ Unknown task type: {task_type}")
                result = {"status": "error", "error": "Unknown task type"}

            # Finalize status
            status = "completed" if result.get("status") != "error" else "failed"
            duration = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

            self.client.table("scheduled_tasks").update(
                {
                    "status": status,
                    "executed_at": datetime.now(UTC).isoformat(),
                    "execution_duration_ms": duration,
                    "last_error": result.get("error"),
                }
            ).eq("id", task_id).execute()

            logger.info(f"✅ Task {task_id} {status}")

        except Exception as e:
            logger.error(f"🔥 Task execution crash: {e}")
            self.client.table("scheduled_tasks").update(
                {"status": "failed", "last_error": str(e)}
            ).eq("id", task_id).execute()

    async def _handle_pushbacks(self):
        """
        Fluid Rescheduling Logic (The Breathing Arc)
        If a task is missed (scheduled in the past but still pending),
        push it back to 'Today' and adjust the strategic arc.
        """
        try:
            # Find tasks that are 'pending' but were supposed to run more than 24 hours ago
            cutoff = (datetime.now(UTC) - timedelta(hours=24)).isoformat()

            result = (
                self.client.table("scheduled_tasks")
                .select("id, move_id, scheduled_for")
                .eq("status", "pending")
                .lt("scheduled_for", cutoff)
                .execute()
            )

            missed_tasks = result.data or []

            for task in missed_tasks:
                new_date = datetime.now(UTC) + timedelta(minutes=5)
                logger.info(f"🌀 Rescheduling missed task {task['id']} to {new_date}")

                self.client.table("scheduled_tasks").update(
                    {
                        "scheduled_for": new_date.isoformat(),
                        "status": "pushed_back",  # Marker for the UI to show 'Rescheduled'
                    }
                ).eq("id", task["id"]).execute()

                # TODO: Trigger Arc Recalculation via Synapse for subsequent tasks

        except Exception as e:
            logger.error(f"❌ Ticker: Failed pushback check: {e}")

    def stop_ticker(self):
        """Stop the ticker loop"""
        self.running = False
        logger.info("⏹️ Ticker Stopped")


# Global ticker instance
ticker = CampaignTicker()
