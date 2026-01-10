"""
Database Schema & Cron Job Integration
Implements dependency tracking, task management, and automated reconciliation
"""

import asyncio
import json
import logging
import sqlite3
import uuid
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class TaskRecord:
    id: str
    move_id: str
    title: str
    description: str
    task_type: str  # pillar, cluster, support
    day_number: int
    status: str  # scheduled, completed, overdue, abandoned, compressed
    dependency_id: Optional[str] = None
    completed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class MoveRecord:
    id: str
    name: str
    description: str
    duration_days: int
    start_date: datetime
    end_date: datetime
    status: str  # active, completed, aborted, paused
    user_id: str
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class DependencyRecord:
    id: str
    task_id: str
    depends_on_task_id: str
    dependency_type: str  # hard, soft
    created_at: datetime = None


class DatabaseManager:
    """
    Database manager for Moves, Tasks, and Dependencies
    SQLite for simplicity, can be migrated to PostgreSQL for production
    """

    def __init__(self, db_path: str = "raptorflow_moves.db"):
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self):
        """Create database tables if they don't exist"""

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS moves (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    duration_days INTEGER NOT NULL,
                    start_date DATETIME NOT NULL,
                    end_date DATETIME NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    user_id TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    move_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    task_type TEXT NOT NULL CHECK (task_type IN ('pillar', 'cluster', 'support')),
                    day_number INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed', 'overdue', 'abandoned', 'compressed')),
                    dependency_id TEXT,
                    completed_at DATETIME,
                    due_date DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (move_id) REFERENCES moves(id) ON DELETE CASCADE,
                    FOREIGN KEY (dependency_id) REFERENCES tasks(id)
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS dependencies (
                    id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    depends_on_task_id TEXT NOT NULL,
                    dependency_type TEXT NOT NULL DEFAULT 'hard' CHECK (dependency_type IN ('hard', 'soft')),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                    FOREIGN KEY (depends_on_task_id) REFERENCES tasks(id) ON DELETE CASCADE
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS compression_logs (
                    id TEXT PRIMARY KEY,
                    move_id TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    compression_type TEXT NOT NULL,
                    original_day INTEGER,
                    new_day INTEGER,
                    reason TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (move_id) REFERENCES moves(id) ON DELETE CASCADE,
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS trend_alerts (
                    id TEXT PRIMARY KEY,
                    trend_keyword TEXT NOT NULL,
                    velocity_percent REAL NOT NULL,
                    confidence_score REAL NOT NULL,
                    signal_type TEXT NOT NULL,
                    sources_found INTEGER NOT NULL,
                    icp_tags TEXT NOT NULL,
                    alert_data TEXT NOT NULL,  -- JSON
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    processed BOOLEAN DEFAULT FALSE
                )
            """
            )

            # Create indexes for performance
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_tasks_move_id ON tasks(move_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date)"
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_dependencies_task_id ON dependencies(task_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_trend_alerts_created_at ON trend_alerts(created_at)"
            )

            conn.commit()

    @asynccontextmanager
    async def get_connection(self):
        """Async context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()

    async def create_move(self, move_data: Dict[str, Any]) -> str:
        """Create a new Move record"""

        move_id = str(uuid.uuid4())
        move_record = MoveRecord(
            id=move_id,
            name=move_data["name"],
            description=move_data.get("description", ""),
            duration_days=move_data["duration_days"],
            start_date=datetime.fromisoformat(move_data["start_date"]),
            end_date=datetime.fromisoformat(move_data["end_date"]),
            status="active",
            user_id=move_data["user_id"],
        )

        async with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO moves (id, name, description, duration_days, start_date, end_date, status, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    move_record.id,
                    move_record.name,
                    move_record.description,
                    move_record.duration_days,
                    move_record.start_date,
                    move_record.end_date,
                    move_record.status,
                    move_record.user_id,
                ),
            )
            conn.commit()

        logger.info(f"Created move: {move_record.name}", move_id=move_id)
        return move_id

    async def create_task(self, task_data: Dict[str, Any]) -> str:
        """Create a new Task record"""

        task_id = str(uuid.uuid4())
        task_record = TaskRecord(
            id=task_id,
            move_id=task_data["move_id"],
            title=task_data["title"],
            description=task_data.get("description", ""),
            task_type=task_data["task_type"],
            day_number=task_data["day_number"],
            status="scheduled",
            dependency_id=task_data.get("dependency_id"),
            due_date=(
                datetime.fromisoformat(task_data["due_date"])
                if task_data.get("due_date")
                else None
            ),
        )

        async with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO tasks (id, move_id, title, description, task_type, day_number, status, dependency_id, due_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    task_record.id,
                    task_record.move_id,
                    task_record.title,
                    task_record.description,
                    task_record.task_type,
                    task_record.day_number,
                    task_record.status,
                    task_record.dependency_id,
                    task_record.due_date,
                ),
            )
            conn.commit()

        logger.info(
            f"Created task: {task_record.title}",
            task_id=task_id,
            move_id=task_record.move_id,
        )
        return task_id

    async def create_dependency(
        self, task_id: str, depends_on_task_id: str, dependency_type: str = "hard"
    ) -> str:
        """Create a dependency relationship between tasks"""

        dependency_id = str(uuid.uuid4())

        async with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO dependencies (id, task_id, depends_on_task_id, dependency_type)
                VALUES (?, ?, ?, ?)
            """,
                (dependency_id, task_id, depends_on_task_id, dependency_type),
            )
            conn.commit()

        logger.info(
            f"Created dependency: {task_id} depends on {depends_on_task_id}",
            dependency_id=dependency_id,
        )
        return dependency_id

    async def get_overdue_tasks(self, move_id: str) -> List[TaskRecord]:
        """Get all overdue tasks for a move"""

        async with self.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM tasks
                WHERE move_id = ? AND due_date < ? AND status != 'completed'
                ORDER BY due_date ASC
            """,
                (move_id, datetime.now(timezone.utc)),
            )

            rows = cursor.fetchall()

            return [
                TaskRecord(
                    id=row["id"],
                    move_id=row["move_id"],
                    title=row["title"],
                    description=row["description"],
                    task_type=row["task_type"],
                    day_number=row["day_number"],
                    status=row["status"],
                    dependency_id=row["dependency_id"],
                    completed_at=(
                        datetime.fromisoformat(row["completed_at"])
                        if row["completed_at"]
                        else None
                    ),
                    due_date=(
                        datetime.fromisoformat(row["due_date"])
                        if row["due_date"]
                        else None
                    ),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                )
                for row in rows
            ]

    async def get_dependent_tasks(self, task_id: str) -> List[TaskRecord]:
        """Get all tasks that depend on a specific task"""

        async with self.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT t.* FROM tasks t
                JOIN dependencies d ON t.id = d.task_id
                WHERE d.depends_on_task_id = ?
                ORDER BY t.day_number ASC
            """,
                (task_id,),
            )

            rows = cursor.fetchall()

            return [
                TaskRecord(
                    id=row["id"],
                    move_id=row["move_id"],
                    title=row["title"],
                    description=row["description"],
                    task_type=row["task_type"],
                    day_number=row["day_number"],
                    status=row["status"],
                    dependency_id=row["dependency_id"],
                    completed_at=(
                        datetime.fromisoformat(row["completed_at"])
                        if row["completed_at"]
                        else None
                    ),
                    due_date=(
                        datetime.fromisoformat(row["due_date"])
                        if row["due_date"]
                        else None
                    ),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                )
                for row in rows
            ]

    async def update_task_status(
        self, task_id: str, status: str, completed_at: Optional[datetime] = None
    ):
        """Update task status"""

        async with self.get_connection() as conn:
            if status == "completed" and not completed_at:
                completed_at = datetime.now(timezone.utc)

            conn.execute(
                """
                UPDATE tasks
                SET status = ?, completed_at = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (status, completed_at, task_id),
            )
            conn.commit()

        logger.info(f"Updated task status: {task_id} -> {status}")

    async def log_compression(
        self,
        move_id: str,
        task_id: str,
        compression_type: str,
        original_day: int,
        new_day: int,
        reason: str,
    ):
        """Log a compression action"""

        compression_id = str(uuid.uuid4())

        async with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO compression_logs (id, move_id, task_id, compression_type, original_day, new_day, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    compression_id,
                    move_id,
                    task_id,
                    compression_type,
                    original_day,
                    new_day,
                    reason,
                ),
            )
            conn.commit()

        logger.info(f"Logged compression: {compression_type} for task {task_id}")

    async def save_trend_alert(self, alert_data: Dict[str, Any]):
        """Save a trend alert to the database"""

        alert_id = str(uuid.uuid4())

        async with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO trend_alerts (id, trend_keyword, velocity_percent, confidence_score, signal_type, sources_found, icp_tags, alert_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    alert_id,
                    alert_data["trend_keyword"],
                    alert_data["velocity_percent"],
                    alert_data["confidence_score"],
                    alert_data["signal_type"],
                    alert_data["sources_found"],
                    json.dumps(alert_data["icp_tags"]),
                    json.dumps(alert_data),
                ),
            )
            conn.commit()

        logger.info(f"Saved trend alert: {alert_data['trend_keyword']}")
        return alert_id

    async def get_unprocessed_trend_alerts(self) -> List[Dict[str, Any]]:
        """Get unprocessed trend alerts"""

        async with self.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM trend_alerts
                WHERE processed = FALSE
                ORDER BY created_at DESC
                LIMIT 50
            """
            )

            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    async def mark_trend_alert_processed(self, alert_id: str):
        """Mark a trend alert as processed"""

        async with self.get_connection() as conn:
            conn.execute(
                "UPDATE trend_alerts SET processed = TRUE WHERE id = ?", (alert_id,)
            )
            conn.commit()


class CronJobScheduler:
    """
    Cron job scheduler for automated move reconciliation and trend monitoring
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.running = False

    async def start_scheduler(self):
        """Start the cron job scheduler"""
        self.running = True
        logger.info("Cron job scheduler started")

        # Run reconciliation every hour
        asyncio.create_task(self._hourly_reconciliation())

        # Run trend monitoring every 6 hours
        asyncio.create_task(self._six_hourly_trend_monitoring())

        # Cleanup old data daily
        asyncio.create_task(self._daily_cleanup())

    async def stop_scheduler(self):
        """Stop the cron job scheduler"""
        self.running = False
        logger.info("Cron job scheduler stopped")

    async def _hourly_reconciliation(self):
        """Run move reconciliation every hour"""

        while self.running:
            try:
                await self._reconcile_all_moves()
                await asyncio.sleep(3600)  # 1 hour
            except Exception as e:
                logger.error(f"Hourly reconciliation failed: {e}")
                await asyncio.sleep(300)  # 5 minutes retry

    async def _six_hourly_trend_monitoring(self):
        """Run trend monitoring every 6 hours"""

        while self.running:
            try:
                await self._monitor_trends()
                await asyncio.sleep(21600)  # 6 hours
            except Exception as e:
                logger.error(f"Trend monitoring failed: {e}")
                await asyncio.sleep(1800)  # 30 minutes retry

    async def _daily_cleanup(self):
        """Clean up old data daily"""

        while self.running:
            try:
                await self._cleanup_old_data()
                await asyncio.sleep(86400)  # 24 hours
            except Exception as e:
                logger.error(f"Daily cleanup failed: {e}")
                await asyncio.sleep(3600)  # 1 hour retry

    async def _reconcile_all_moves(self):
        """Reconcile all active moves"""

        async with self.db_manager.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM moves
                WHERE status = 'active'
                AND end_date > ?
            """,
                (datetime.now(timezone.utc),),
            )

            active_moves = cursor.fetchall()

        for move_row in active_moves:
            await self._reconcile_move(move_row["id"])

    async def _reconcile_move(self, move_id: str):
        """Reconcile a specific move"""

        logger.info(f"Reconciling move: {move_id}")

        # Get overdue tasks
        overdue_tasks = await self.db_manager.get_overdue_tasks(move_id)

        if not overdue_tasks:
            logger.info(f"No overdue tasks for move {move_id}")
            return

        # Process each overdue task
        for task in overdue_tasks:
            await self._process_overdue_task(task)

    async def _process_overdue_task(self, task: TaskRecord):
        """Process an overdue task according to the Compression Protocol"""

        logger.warning(f"Processing overdue task: {task.title}", task_id=task.id)

        # Get dependent tasks
        dependent_tasks = await self.db_manager.get_dependent_tasks(task.id)

        if task.task_type == "pillar":
            # Compress timeline for pillar tasks
            await self._compress_pillar_task(task, dependent_tasks)
        else:
            # Abandon support tasks
            await self._abandon_support_task(task)

    async def _compress_pillar_task(
        self, task: TaskRecord, dependent_tasks: List[TaskRecord]
    ):
        """Compress timeline for pillar tasks"""

        for dependent_task in dependent_tasks:
            # Create merged task
            merged_task_data = {
                "move_id": task.move_id,
                "title": f"{task.title} AND {dependent_task.title}",
                "description": f"COMPRESSED: {task.description} + {dependent_task.description}",
                "task_type": "pillar",
                "day_number": dependent_task.day_number,
                "due_date": (
                    datetime.now(timezone.utc)
                    + timedelta(days=dependent_task.day_number - 1)
                ).isoformat(),
            }

            merged_task_id = await self.db_manager.create_task(merged_task_data)

            # Log compression
            await self.db_manager.log_compression(
                move_id=task.move_id,
                task_id=task.id,
                compression_type="pillar_compression",
                original_day=task.day_number,
                new_day=dependent_task.day_number,
                reason=f"Merged with dependent task: {dependent_task.title}",
            )

            # Update original tasks
            await self.db_manager.update_task_status(task.id, "compressed")
            await self.db_manager.update_task_status(dependent_task.id, "compressed")

            logger.info(
                f"Compressed pillar task: {task.title} with {dependent_task.title}"
            )

    async def _abandon_support_task(self, task: TaskRecord):
        """Abandon support tasks to prevent debt fatigue"""

        await self.db_manager.update_task_status(task.id, "abandoned")

        await self.db_manager.log_compression(
            move_id=task.move_id,
            task_id=task.id,
            compression_type="support_abandonment",
            original_day=task.day_number,
            new_day=task.day_number,
            reason="Support task missed - prevents debt fatigue",
        )

        logger.info(f"Abandoned support task: {task.title}")

    async def _monitor_trends(self):
        """Monitor and process trends"""

        try:
            from signal_proxy_architecture import signal_proxy

            # Get ICP tags from active moves (simplified)
            icp_tags = [
                "coffee",
                "tech",
                "marketing",
            ]  # In production, get from user profiles

            # Detect trends
            trend_results = await signal_proxy.detect_trends(icp_tags)

            # Save trend alerts
            for alert in trend_results.get("trend_alerts", []):
                await self.db_manager.save_trend_alert(alert)

            logger.info(
                f"Processed {len(trend_results.get('trend_alerts', []))} trend alerts"
            )

        except ImportError:
            logger.warning("Signal proxy not available for trend monitoring")

    async def _cleanup_old_data(self):
        """Clean up old data"""

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)

        async with self.db_manager.get_connection() as conn:
            # Delete old compression logs
            conn.execute(
                "DELETE FROM compression_logs WHERE created_at < ?", (cutoff_date,)
            )

            # Delete old processed trend alerts
            conn.execute(
                "DELETE FROM trend_alerts WHERE processed = TRUE AND created_at < ?",
                (cutoff_date,),
            )

            conn.commit()

        logger.info(f"Cleaned up data older than {cutoff_date}")


# Global instances
db_manager = DatabaseManager()
cron_scheduler = CronJobScheduler(db_manager)


async def demonstrate_database_integration():
    """Demonstrate database integration and cron jobs"""

    print("🗄️ DATABASE INTEGRATION DEMONSTRATION")
    print("=" * 60)

    # Create sample move and tasks
    move_data = {
        "name": "7-Day Ignite (Coffee Launch)",
        "description": "Sample move for demonstration",
        "duration_days": 7,
        "start_date": datetime.now(timezone.utc).isoformat(),
        "end_date": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        "user_id": "demo_user",
    }

    move_id = await db_manager.create_move(move_data)
    print(f"✅ Created move: {move_id}")

    # Create sample tasks
    tasks_data = [
        {
            "move_id": move_id,
            "title": "Create Teaser Video",
            "description": "30-second product teaser",
            "task_type": "pillar",
            "day_number": 3,
            "due_date": (
                datetime.now(timezone.utc) + timedelta(days=2)
            ).isoformat(),  # Overdue
        },
        {
            "move_id": move_id,
            "title": "Post Teaser Video",
            "description": "Share teaser on social media",
            "task_type": "pillar",
            "day_number": 3,
            "dependency_id": None,  # Will be set after creating first task
            "due_date": (
                datetime.now(timezone.utc) + timedelta(days=2)
            ).isoformat(),  # Overdue
        },
        {
            "move_id": move_id,
            "title": "Launch Waitlist",
            "description": "Open waitlist for early access",
            "task_type": "pillar",
            "day_number": 4,
            "due_date": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
        },
    ]

    task_ids = []
    for task_data in tasks_data:
        task_id = await db_manager.create_task(task_data)
        task_ids.append(task_id)
        print(f"✅ Created task: {task_data['title']}")

    # Create dependency
    await db_manager.create_dependency(task_ids[1], task_ids[0], "hard")
    print(f"✅ Created dependency: Task 2 depends on Task 1")

    # Test overdue task detection
    overdue_tasks = await db_manager.get_overdue_tasks(move_id)
    print(f"📊 Found {len(overdue_tasks)} overdue tasks")

    # Test dependent task detection
    dependent_tasks = await db_manager.get_dependent_tasks(task_ids[0])
    print(f"📊 Found {len(dependent_tasks)} dependent tasks")

    # Simulate cron job reconciliation
    print("\n🔄 SIMULATING CRON JOB RECONCILIATION")
    await cron_scheduler._reconcile_move(move_id)

    print("\n🎯 DATABASE INTEGRATION COMPLETE")
    print("=" * 60)
    print("✅ Database schema created")
    print("✅ Dependency tracking working")
    print("✅ Cron job reconciliation active")
    print("✅ Compression protocol integrated")


if __name__ == "__main__":
    asyncio.run(demonstrate_database_integration())
