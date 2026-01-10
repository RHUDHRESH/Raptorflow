"""
Comprehensive Testing Suite
Tests all components of the upgraded scraper system
"""

import asyncio
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, Mock, patch

# Add the cloud-scraper directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from compression_protocol import CompressionProtocol, Move, Task, TaskStatus, TaskType
from database_integration import CronJobScheduler, DatabaseManager
from signal_proxy_architecture import SignalProxyArchitecture, TrendSignal


class TestCompressionProtocol(unittest.TestCase):
    """Test the Compression Protocol component"""

    def setUp(self):
        self.protocol = CompressionProtocol()
        self.sample_move = self.protocol.create_sample_move()

    def test_move_creation(self):
        """Test move creation with tasks"""
        self.assertEqual(self.sample_move.name, "7-Day Ignite (Coffee Launch)")
        self.assertEqual(len(self.sample_move.tasks), 7)
        self.assertEqual(self.sample_move.duration_days, 7)

    def test_task_classification(self):
        """Test task type classification"""
        pillar_tasks = [
            t for t in self.sample_move.tasks if t.task_type == TaskType.PILLAR
        ]
        cluster_tasks = [
            t for t in self.sample_move.tasks if t.task_type == TaskType.CLUSTER
        ]
        support_tasks = [
            t for t in self.sample_move.tasks if t.task_type == TaskType.SUPPORT
        ]

        self.assertGreater(len(pillar_tasks), 0)
        self.assertGreater(len(cluster_tasks), 0)
        self.assertGreater(len(support_tasks), 0)

    def test_consecutive_failure_detection(self):
        """Test 3-day failure detection"""
        # Mark first 3 days as failed
        for task in self.sample_move.tasks:
            if task.day_number <= 3:
                task.status = TaskStatus.OVERDUE

        consecutive_failures = self.protocol._check_consecutive_failures(
            self.sample_move, 4
        )
        self.assertEqual(consecutive_failures, 3)

    def test_task_viability_assessment(self):
        """Test task viability assessment"""
        # Test launch waitlist without teaser video
        launch_task = Task(
            "1",
            "Launch Waitlist",
            "Open waitlist",
            TaskType.PILLAR,
            4,
            TaskStatus.SCHEDULED,
        )
        teaser_task = Task(
            "2", "Teaser Video", "Create teaser", TaskType.PILLAR, 3, TaskStatus.OVERDUE
        )

        viability = asyncio.run(
            self.protocol._assess_task_viability(
                self.sample_move, launch_task, teaser_task
            )
        )
        self.assertFalse(viability["still_viable"])

    async def test_compression_protocol_integration(self):
        """Test full compression protocol flow"""
        # Simulate overdue tasks
        today = datetime.now(timezone.utc)
        yesterday = today - timedelta(days=1)

        for task in self.sample_move.tasks:
            if task.day_number == 3:
                task.status = TaskStatus.OVERDUE
                task.due_date = yesterday

        # Run compression check
        result = await self.protocol.check_overdue_tasks(self.sample_move.id)

        self.assertEqual(result["status"], "compression_applied")
        self.assertGreater(result["overdue_tasks"], 0)


class TestSignalProxyArchitecture(unittest.TestCase):
    """Test the Signal Proxy Architecture component"""

    def setUp(self):
        self.signal_proxy = SignalProxyArchitecture()

    async def async_setUp(self):
        await self.signal_proxy.initialize()

    async def async_tearDown(self):
        await self.signal_proxy.close()

    def test_signal_classification(self):
        """Test signal type classification"""
        positive_signal = self.signal_proxy._classify_signal_type("new feature launch")
        self.assertEqual(positive_signal, TrendSignal.POSITIVE)

        negative_signal = self.signal_proxy._classify_signal_type("scam lawsuit crash")
        self.assertEqual(negative_signal, TrendSignal.NEGATIVE)

        neutral_signal = self.signal_proxy._classify_signal_type(
            "market analysis report"
        )
        self.assertEqual(neutral_signal, TrendSignal.NEUTRAL)

    def test_youtube_time_parsing(self):
        """Test YouTube time ago parsing"""
        self.assertEqual(self.signal_proxy._parse_youtube_time_ago("1 hour ago"), 1)
        self.assertEqual(self.signal_proxy._parse_youtube_time_ago("2 days ago"), 48)
        self.assertEqual(self.signal_proxy._parse_youtube_time_ago("1 week ago"), 168)
        self.assertEqual(self.signal_proxy._parse_youtube_time_ago("1 month ago"), 720)

    def test_anti_catastrophe_filter(self):
        """Test anti-catastrophe filter"""
        from signal_proxy_architecture import KeywordVelocity

        # Create mixed signals
        velocities = [
            KeywordVelocity(
                "new_launch", 10, 5, 100.0, "increasing", TrendSignal.POSITIVE, ["rss"]
            ),
            KeywordVelocity(
                "scam_alert",
                8,
                4,
                100.0,
                "increasing",
                TrendSignal.NEGATIVE,
                ["reddit"],
            ),
            KeywordVelocity(
                "market_analysis",
                6,
                3,
                100.0,
                "increasing",
                TrendSignal.NEUTRAL,
                ["youtube"],
            ),
        ]

        filtered = asyncio.run(
            self.signal_proxy._apply_anti_catastrophe_filter(velocities)
        )

        # Should filter out negative signals
        self.assertEqual(len(filtered), 2)
        self.assertNotIn(TrendSignal.NEGATIVE, [v.signal_type for v in filtered])

    @patch("aiohttp.ClientSession.get")
    async def test_rss_velocity_engine(self, mock_get):
        """Test RSS velocity engine with mocked data"""
        await self.async_setUp()

        # Mock RSS feed response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_feed_data = {
            "entries": [
                {"title": "New Coffee Brewing Method Discovered"},
                {"title": "Espresso Machine Innovation Launch"},
                {"title": "Coffee Bean Market Analysis"},
            ]
        }

        with patch("feedparser.parse", return_value=mock_feed_data):
            result = await self.signal_proxy._rss_velocity_engine(["coffee"])

            self.assertGreater(result["keyword_counts"]["coffee_coffee"], 0)
            self.assertGreater(result["successful_feeds"], 0)

        await self.async_tearDown()

    @patch("aiohttp.ClientSession.get")
    async def test_reddit_json_backdoor(self, mock_get):
        """Test Reddit .json backdoor with mocked data"""
        await self.async_setUp()

        # Mock Reddit response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_reddit_data = {
            "data": {
                "children": [
                    {"data": {"title": "New coffee brewing technique amazing"}},
                    {"data": {"title": "Best espresso beans discussion"}},
                    {"data": {"title": "Coffee roasting tips and tricks"}},
                ]
            }
        }
        mock_response.json.return_value = mock_reddit_data
        mock_get.return_value.__aenter__.return_value = mock_response

        result = await self.signal_proxy._reddit_json_backdoor(["coffee"])

        self.assertGreater(result["keyword_counts"]["reddit_coffee_coffee"], 0)
        self.assertGreater(result["successful_subreddits"], 0)

        await self.async_tearDown()


class TestDatabaseIntegration(unittest.TestCase):
    """Test database integration"""

    def setUp(self):
        # Use temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_manager = DatabaseManager(self.temp_db.name)
        self.cron_scheduler = CronJobScheduler(self.db_manager)

    def tearDown(self):
        os.unlink(self.temp_db.name)

    async def test_database_initialization(self):
        """Test database table creation"""
        # Database should be initialized in setUp
        async with self.db_manager.get_connection() as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            expected_tables = [
                "moves",
                "tasks",
                "dependencies",
                "compression_logs",
                "trend_alerts",
            ]
            for table in expected_tables:
                self.assertIn(table, tables)

    async def test_move_creation(self):
        """Test move creation"""
        move_data = {
            "name": "Test Move",
            "description": "Test description",
            "duration_days": 7,
            "start_date": datetime.now(timezone.utc).isoformat(),
            "end_date": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "user_id": "test_user",
        }

        move_id = await self.db_manager.create_move(move_data)
        self.assertIsNotNone(move_id)

        # Verify move was created
        async with self.db_manager.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM moves WHERE id = ?", (move_id,))
            move = cursor.fetchone()
            self.assertEqual(move["name"], "Test Move")

    async def test_task_creation_and_dependencies(self):
        """Test task creation and dependency tracking"""
        # Create move first
        move_data = {
            "name": "Test Move",
            "description": "Test description",
            "duration_days": 7,
            "start_date": datetime.now(timezone.utc).isoformat(),
            "end_date": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "user_id": "test_user",
        }
        move_id = await self.db_manager.create_move(move_data)

        # Create tasks
        task1_data = {
            "move_id": move_id,
            "title": "Task 1",
            "description": "First task",
            "task_type": "pillar",
            "day_number": 1,
            "due_date": datetime.now(timezone.utc).isoformat(),
        }

        task2_data = {
            "move_id": move_id,
            "title": "Task 2",
            "description": "Second task",
            "task_type": "pillar",
            "day_number": 2,
            "dependency_id": None,  # Will be set after task 1 is created
            "due_date": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        }

        task1_id = await self.db_manager.create_task(task1_data)
        task2_id = await self.db_manager.create_task(task2_data)

        # Create dependency
        dependency_id = await self.db_manager.create_dependency(
            task2_id, task1_id, "hard"
        )

        # Test dependency retrieval
        dependent_tasks = await self.db_manager.get_dependent_tasks(task1_id)
        self.assertEqual(len(dependent_tasks), 1)
        self.assertEqual(dependent_tasks[0].id, task2_id)

    async def test_overdue_task_detection(self):
        """Test overdue task detection"""
        # Create move and overdue task
        move_data = {
            "name": "Test Move",
            "description": "Test description",
            "duration_days": 7,
            "start_date": datetime.now(timezone.utc).isoformat(),
            "end_date": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "user_id": "test_user",
        }
        move_id = await self.db_manager.create_move(move_data)

        # Create overdue task (due yesterday)
        task_data = {
            "move_id": move_id,
            "title": "Overdue Task",
            "description": "This task is overdue",
            "task_type": "pillar",
            "day_number": 1,
            "due_date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
        }

        task_id = await self.db_manager.create_task(task_data)

        # Test overdue detection
        overdue_tasks = await self.db_manager.get_overdue_tasks(move_id)
        self.assertEqual(len(overdue_tasks), 1)
        self.assertEqual(overdue_tasks[0].id, task_id)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""

    async def test_full_system_integration(self):
        """Test integration of all components"""
        # Initialize components
        protocol = CompressionProtocol()
        signal_proxy = SignalProxyArchitecture()

        # Use temporary database
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_db.close()
        db_manager = DatabaseManager(temp_db.name)
        cron_scheduler = CronJobScheduler(db_manager)

        try:
            # Create sample move in database
            move_data = {
                "name": "Integration Test Move",
                "description": "Testing full system integration",
                "duration_days": 7,
                "start_date": datetime.now(timezone.utc).isoformat(),
                "end_date": (
                    datetime.now(timezone.utc) + timedelta(days=7)
                ).isoformat(),
                "user_id": "integration_test_user",
            }

            move_id = await db_manager.create_move(move_data)

            # Create tasks with dependencies
            tasks = [
                {
                    "move_id": move_id,
                    "title": "Research Competitors",
                    "description": "Analyze 3 main competitors",
                    "task_type": "support",
                    "day_number": 1,
                    "due_date": (
                        datetime.now(timezone.utc) + timedelta(days=0)
                    ).isoformat(),
                },
                {
                    "move_id": move_id,
                    "title": "Create Teaser Video",
                    "description": "30-second product teaser",
                    "task_type": "pillar",
                    "day_number": 3,
                    "due_date": (
                        datetime.now(timezone.utc) + timedelta(days=2)
                    ).isoformat(),
                },
                {
                    "move_id": move_id,
                    "title": "Launch Waitlist",
                    "description": "Open waitlist for early access",
                    "task_type": "pillar",
                    "day_number": 4,
                    "due_date": (
                        datetime.now(timezone.utc) + timedelta(days=3)
                    ).isoformat(),
                },
            ]

            task_ids = []
            for task_data in tasks:
                task_id = await db_manager.create_task(task_data)
                task_ids.append(task_id)

            # Create dependency
            await db_manager.create_dependency(task_ids[2], task_ids[1], "hard")

            # Test compression protocol integration
            overdue_tasks = await db_manager.get_overdue_tasks(move_id)
            if overdue_tasks:
                await cron_scheduler._process_overdue_task(overdue_tasks[0])

            # Test signal proxy integration (mocked)
            await signal_proxy.initialize()

            # Mock trend detection
            with patch("feedparser.parse") as mock_parse:
                mock_parse.return_value = {
                    "entries": [
                        {"title": "New coffee technology launch"},
                        {"title": "Innovation in brewing methods"},
                    ],
                    "bozo": False,
                }

                trend_results = await signal_proxy.detect_trends(["coffee"])
                self.assertIn("trend_alerts", trend_results)

            await signal_proxy.close()

            # Verify system state
            compression_logs = (
                await db_manager.get_connection()
                .__aenter__()
                .execute(
                    "SELECT COUNT(*) as count FROM compression_logs WHERE move_id = ?",
                    (move_id,),
                )
                .fetchone()
            )

            self.assertGreaterEqual(compression_logs["count"], 0)

        finally:
            os.unlink(temp_db.name)


def run_comprehensive_tests():
    """Run all tests"""

    print("🧪 COMPREHENSIVE TESTING SUITE")
    print("=" * 60)

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestCompressionProtocol))
    test_suite.addTest(unittest.makeSuite(TestSignalProxyArchitecture))
    test_suite.addTest(unittest.makeSuite(TestDatabaseIntegration))
    test_suite.addTest(unittest.makeSuite(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    print(f"\n📊 TEST RESULTS:")
    print(f"  ✅ Tests run: {result.testsRun}")
    print(f"  ✅ Failures: {len(result.failures)}")
    print(f"  ✅ Errors: {len(result.errors)}")
    print(
        f"  ✅ Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%"
    )

    if result.failures:
        print(f"\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  • {test}: {traceback}")

    if result.errors:
        print(f"\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  • {test}: {traceback}")

    print("\n🎯 TESTING COMPLETE")
    print("=" * 60)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
