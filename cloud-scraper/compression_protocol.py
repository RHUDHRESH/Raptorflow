"""
Move Compression Protocol - Task Failure Handling System
Implements the "Compression Protocol" for tactical sprint management
"""

import asyncio
import json
import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class TaskType(Enum):
    PILLAR = "pillar"  # Critical path tasks
    CLUSTER = "cluster"  # Support tasks
    SUPPORT = "support"  # Optional tasks


class TaskStatus(Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    ABANDONED = "abandoned"
    COMPRESSED = "compressed"


@dataclass
class Task:
    id: str
    title: str
    description: str
    task_type: TaskType
    day_number: int
    status: TaskStatus
    dependency_id: Optional[str] = None
    completed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None


@dataclass
class Move:
    id: str
    name: str
    duration_days: int
    start_date: datetime
    tasks: List[Task]
    status: str = "active"


class CompressionProtocol:
    """
    Implements the Compression Protocol for tactical sprint management.
    Handles task failures by recalculating routes instead of just bumping tasks.
    """

    def __init__(self):
        self.moves: Dict[str, Move] = {}
        self.compression_history: List[Dict] = []

    async def check_overdue_tasks(self, move_id: str) -> Dict[str, Any]:
        """
        Midnight check for overdue tasks - the Architect Agent wakes up
        """
        move = self.moves.get(move_id)
        if not move:
            return {"error": "Move not found"}

        today = datetime.now(timezone.utc).date()
        current_day = (today - move.start_date.date()).days + 1

        overdue_tasks = [
            task
            for task in move.tasks
            if task.due_date
            and task.due_date.date() < today
            and task.status != TaskStatus.COMPLETED
        ]

        if not overdue_tasks:
            return {"status": "no_overdue_tasks", "move_id": move_id}

        compression_results = []

        for overdue_task in overdue_tasks:
            result = await self._handle_overdue_task(move, overdue_task, current_day)
            compression_results.append(result)

        # Check for 3-day failure condition
        consecutive_failures = self._check_consecutive_failures(move, current_day)
        if consecutive_failures >= 3:
            return await self._abort_move(move, consecutive_failures)

        return {
            "status": "compression_applied",
            "move_id": move_id,
            "current_day": current_day,
            "overdue_tasks": len(overdue_tasks),
            "compressions": compression_results,
        }

    async def _handle_overdue_task(
        self, move: Move, overdue_task: Task, current_day: int
    ) -> Dict[str, Any]:
        """
        Handle individual overdue task based on type and dependencies
        """

        # Logic Tree Implementation
        if overdue_task.task_type == TaskType.PILLAR:
            return await self._compress_critical_path(move, overdue_task, current_day)
        else:
            return await self._abandon_support_task(move, overdue_task, current_day)

    async def _compress_critical_path(
        self, move: Move, pillar_task: Task, current_day: int
    ) -> Dict[str, Any]:
        """
        If missed task was Critical Path (Pillar): Compress timeline
        """

        # Find dependent tasks
        dependent_tasks = [
            task
            for task in move.tasks
            if task.dependency_id == pillar_task.id and task.day_number > current_day
        ]

        compression_actions = []

        for dependent_task in dependent_tasks:
            # Check if dependent task still works without the pillar task
            viability = await self._assess_task_viability(
                move, dependent_task, pillar_task
            )

            if viability["still_viable"]:
                # Merge tasks - compress timeline
                merged_task = await self._merge_tasks(move, pillar_task, dependent_task)
                compression_actions.append(
                    {
                        "action": "compressed",
                        "pillar_task": pillar_task.title,
                        "dependent_task": dependent_task.title,
                        "merged_task": merged_task.title,
                        "new_day": dependent_task.day_number,
                        "compression_ratio": 2.0,  # Two days merged into one
                    }
                )

                # Update tasks
                pillar_task.status = TaskStatus.COMPRESSED
                dependent_task.status = TaskStatus.COMPRESSED

                # Add merged task
                move.tasks.append(merged_task)

            else:
                # Cannot proceed - need to reschedule or abort
                compression_actions.append(
                    {
                        "action": "failed_compression",
                        "pillar_task": pillar_task.title,
                        "dependent_task": dependent_task.title,
                        "reason": "Task not viable without pillar dependency",
                        "recommendation": "reschedule_move",
                    }
                )

        # Log compression
        self._log_compression(move.id, pillar_task, compression_actions)

        return {
            "task_type": "pillar",
            "compression_applied": True,
            "actions": compression_actions,
        }

    async def _abandon_support_task(
        self, move: Move, support_task: Task, current_day: int
    ) -> Dict[str, Any]:
        """
        If missed task was Cluster/Support: Abandon it to prevent Debt Fatigue
        """

        # Mark as abandoned
        support_task.status = TaskStatus.ABANDONED

        # Log abandonment
        abandonment_log = {
            "move_id": move.id,
            "task_id": support_task.id,
            "task_title": support_task.title,
            "task_type": support_task.task_type.value,
            "day_number": support_task.day_number,
            "abandoned_at": datetime.now(timezone.utc).isoformat(),
            "reason": "Support task missed - too late to complete",
            "psychology_note": "Prevents Debt Fatigue - user starts day clean",
        }

        self.compression_history.append(abandonment_log)

        return {
            "task_type": "support",
            "abandoned": True,
            "task_title": support_task.title,
            "day_clean": True,
            "psychology": "Debt Fatigue prevented",
        }

    async def _assess_task_viability(
        self, move: Move, task: Task, missed_dependency: Task
    ) -> Dict[str, Any]:
        """
        Assess if a task is still viable without its missed dependency
        """

        # Business logic for viability assessment
        viability_rules = {
            # Launch tasks require teaser videos
            "launch_waitlist": {"requires": "teaser_video", "viable": False},
            # Social media posts can be done independently
            "twitter_thread": {"requires": None, "viable": True},
            # Email campaigns require landing pages
            "email_campaign": {"requires": "landing_page", "viable": False},
        }

        task_key = task.title.lower().replace(" ", "_")
        dependency_key = missed_dependency.title.lower().replace(" ", "_")

        rule = viability_rules.get(task_key, {"viable": True})  # Default to viable

        if rule.get("requires") and rule["requires"] in dependency_key:
            return {
                "still_viable": False,
                "reason": f"Task requires {rule['requires']}",
            }

        return {"still_viable": True, "reason": "Task can proceed independently"}

    async def _merge_tasks(self, move: Move, task1: Task, task2: Task) -> Task:
        """
        Merge two tasks into one compressed day
        """

        merged_task = Task(
            id=str(uuid.uuid4()),
            title=f"{task1.title} AND {task2.title}",
            description=f"COMPRESSED: {task1.description} + {task2.description}",
            task_type=TaskType.PILLAR,  # Merged tasks are critical
            day_number=task2.day_number,  # Use the later day
            status=TaskStatus.SCHEDULED,
            dependency_id=None,  # No dependencies after compression
            due_date=move.start_date + timedelta(days=task2.day_number - 1),
        )

        return merged_task

    def _check_consecutive_failures(self, move: Move, current_day: int) -> int:
        """
        Check if user has missed 3 days in a row
        """

        consecutive_failures = 0

        # Check backwards from current day
        for day_offset in range(3):
            check_day = current_day - day_offset
            if check_day < 1:
                break

            day_tasks = [task for task in move.tasks if task.day_number == check_day]

            # Check if all tasks for this day are overdue/abandoned
            all_failed = all(
                task.status in [TaskStatus.OVERDUE, TaskStatus.ABANDONED]
                for task in day_tasks
            )

            if all_failed:
                consecutive_failures += 1
            else:
                break

        return consecutive_failures

    async def _abort_move(
        self, move: Move, consecutive_failures: int
    ) -> Dict[str, Any]:
        """
        Abort the move after 3 consecutive days of failure
        """

        move.status = "aborted"

        abort_log = {
            "move_id": move.id,
            "move_name": move.name,
            "aborted_at": datetime.now(timezone.utc).isoformat(),
            "consecutive_failures": consecutive_failures,
            "reason": "3-day failure threshold reached",
            "recommendation": "restart_move_or_downgrade_intensity",
        }

        self.compression_history.append(abort_log)

        return {
            "status": "move_aborted",
            "move_id": move.id,
            "consecutive_failures": consecutive_failures,
            "message": f"You have missed {consecutive_failures} days. The '{move.name}' strategy is broken. Do you want to restart the move or downgrade to a 'Light Intensity' plan?",
            "options": ["restart_move", "downgrade_intensity", "abort_campaign"],
        }

    def _log_compression(self, move_id: str, task: Task, actions: List[Dict]):
        """Log compression actions for analysis"""

        compression_log = {
            "move_id": move_id,
            "task_id": task.id,
            "task_title": task.title,
            "task_type": task.task_type.value,
            "compression_timestamp": datetime.now(timezone.utc).isoformat(),
            "actions": actions,
        }

        self.compression_history.append(compression_log)
        logger.info(
            f"Compression applied",
            move_id=move_id,
            task=task.title,
            actions=len(actions),
        )

    def create_sample_move(self) -> Move:
        """Create a sample 7-Day Ignite move for testing"""

        tasks = [
            Task(
                "1",
                "Research Competitors",
                "Analyze 3 main competitors",
                TaskType.SUPPORT,
                1,
                TaskStatus.SCHEDULED,
            ),
            Task(
                "2",
                "Create Teaser Video",
                "30-second product teaser",
                TaskType.PILLAR,
                3,
                TaskStatus.SCHEDULED,
            ),
            Task(
                "3",
                "Post Teaser Video",
                "Share teaser on social media",
                TaskType.PILLAR,
                3,
                TaskStatus.SCHEDULED,
                dependency_id="2",
            ),
            Task(
                "4",
                "Launch Waitlist",
                "Open waitlist for early access",
                TaskType.PILLAR,
                4,
                TaskStatus.SCHEDULED,
                dependency_id="3",
            ),
            Task(
                "5",
                "Twitter Thread",
                "Post announcement thread",
                TaskType.CLUSTER,
                4,
                TaskStatus.SCHEDULED,
            ),
            Task(
                "6",
                "Email Campaign",
                "Send launch announcement",
                TaskType.PILLAR,
                5,
                TaskStatus.SCHEDULED,
            ),
            Task(
                "7",
                "Launch Day",
                "Full product launch",
                TaskType.PILLAR,
                7,
                TaskStatus.SCHEDULED,
            ),
        ]

        move = Move(
            id="ignite_coffee_launch",
            name="7-Day Ignite (Coffee Launch)",
            duration_days=7,
            start_date=datetime.now(timezone.utc),
            tasks=tasks,
        )

        # Set due dates
        for task in tasks:
            task.due_date = move.start_date + timedelta(days=task.day_number - 1)

        self.moves[move.id] = move
        return move


# Global compression protocol instance
compression_protocol = CompressionProtocol()


async def demonstrate_compression_protocol():
    """Demonstrate the compression protocol in action"""

    print("🔄 COMPRESSION PROTOCOL DEMONSTRATION")
    print("=" * 60)

    # Create sample move
    move = compression_protocol.create_sample_move()

    print(f"📋 Created Move: {move.name}")
    print(f"📅 Duration: {move.duration_days} days")
    print(f"📝 Tasks: {len(move.tasks)}")
    print()

    # Simulate missing Day 3 (Teaser Video)
    print("🚨 SIMULATING: User missed Day 3 - Teaser Video")

    # Mark Day 3 tasks as overdue
    today = datetime.now(timezone.utc)
    yesterday = today - timedelta(days=1)

    for task in move.tasks:
        if task.day_number == 3:
            task.status = TaskStatus.OVERDUE
            task.due_date = yesterday

    # Run compression check
    result = await compression_protocol.check_overdue_tasks(move.id)

    print(f"📊 Compression Result: {result['status']}")

    if result["status"] == "compression_applied":
        print(f"🔄 Overdue Tasks: {result['overdue_tasks']}")
        print(f"⚡ Compressions Applied:")

        for compression in result["compressions"]:
            if compression["task_type"] == "pillar":
                print(f"  • PILLAR: {compression['compression_applied']}")
                for action in compression["actions"]:
                    print(
                        f"    - {action['action']}: {action.get('merged_task', 'N/A')}"
                    )
            else:
                print(
                    f"  • SUPPORT: {compression['abandoned']} - {compression['task_title']}"
                )
                print(f"    - Psychology: {compression['psychology']}")

    print()
    print("🎯 COMPRESSION PROTOCOL COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(demonstrate_compression_protocol())
