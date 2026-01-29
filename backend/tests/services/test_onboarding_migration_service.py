"""
Tests for Onboarding Migration Service

Comprehensive tests for migrating from legacy onboarding status to the new Redis-based session system
with Business Context Manifest (BCM) integration.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from pydantic import ValidationError

from services.onboarding_migration_service import (
    OnboardingMigrationService,
    MigrationStatus,
    LegacyOnboardingStatus,
    MigrationResult,
    MigrationStats,
    migrate_onboarding_status_batch,
    rollback_onboarding_status_batch
)

# Mock the dependencies
@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client."""
    client = AsyncMock()
    return client

@pytest.fixture
def mock_session_manager():
    """Mock Redis session manager."""
    manager = AsyncMock()
    return manager

@pytest.fixture
def mock_bcm_reducer():
    """Mock BCM reducer."""
    reducer = AsyncMock()
    return reducer

@pytest.fixture
def migration_service(mock_supabase_client, mock_session_manager, mock_bcm_reducer):
    """Create migration service with mocked dependencies."""
    return OnboardingService()

@pytest.fixture
def sample_legacy_user():
    """Sample legacy user data."""
    return {
        "id": "user-123",
        "email": "test@example.com",
        "full_name": "Test User",
        "onboarding_status": "active",
        "onboarding_step": "brand",
        "has_completed_onboarding": False,
        "preferences": {},
        "metadata": {},
        "created_at": datetime.utcnow() - timedelta(days=30),
        "updated_at": datetime.utcnow() - timedelta(days=5)
    }

@pytest.fixture
def sample_completed_legacy_user():
    """Sample legacy user with completed onboarding."""
    return {
        "id": "user-456",
        "email": "completed@example.com",
        "full_name": "Completed User",
        "onboarding_status": "completed",
        "onboarding_step": "export",
        "has_completed_onboarding": True,
        "preferences": {},
        "metadata": {},
        "created_at": datetime.utcnow() - timedelta(days=60),
        "updated_at": datetime.utcnow() - timedelta(days=10)
    }

@pytest.fixture
def sample_workspace():
    """Sample workspace data."""
    return {
        "id": "workspace-123",
        "name": "Test Workspace",
        "owner_id": "user-123",
        "slug": "test-workspace",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

class TestOnboardingMigrationService:
    """Test suite for OnboardingMigrationService."""

    def test_init_service(self):
        """Test service initialization."""
        service = OnboardingService()
        assert service.step_mapping is not None
        assert service.phase_mapping is not None
        assert service.required_steps is not None

    def test_calculate_current_step(self, migration_service):
        """Test step calculation from legacy data."""
        # Test various legacy steps
        assert migration_service._calculate_current_step({"onboarding_step": "welcome"}) == 1
        assert migration_service._calculate_current_step({"onboarding_step": "brand"}) == 3
        assert migration_service._calculate_current_step({"onboarding_step": "export"}) == 26
        assert migration_service._calculate_current_step({"onboarding_step": "invalid"}) == 1  # Fallback

    def test_calculate_completion_percentage(self, migration_service):
        """Test completion percentage calculation."""
        # Test completed user
        completed_user = {"has_completed_onboarding": True}
        assert migration_service._calculate_completion_percentage(completed_user) == 100.0

        # Test active user at different steps
        active_user_1 = {"onboarding_step": "welcome"}
        assert migration_service._calculate_completion_percentage(active_user_1) == 4.17  # 1/24 * 100

        active_user_2 = {"onboarding_step": "positioning"}
        assert migration_service._calculate_completion_percentage(active_user_2) == 50.0  # 12/24 * 100

        # Test user with no step data
        no_step_user = {}
        assert migration_service._calculate_completion_percentage(no_step_user) == 0.0

    def test_get_phase_number(self, migration_service):
        """Test phase number calculation."""
        assert migration_service._get_phase_number(1) == 1
        assert migration_service._get_phase_number(5) == 2
        assert migration_service._get_phase_number(12) == 4
        assert migration_service._get_phase_number(20) == 6
        assert migration_service._get_phase_number(25) == 6  # Cap at Tactics

    def test_get_step_name(self, migration_service):
        """Test step name mapping."""
        assert migration_service._get_step_name(1) == "Evidence Vault"
        assert migration_service._get_step_name(14) == "Positioning Statements"
        assert migration_service._get_step_name(24) == "Export & Launch"
        assert migration_service._get_step_name(99) == "Step 99"  # Fallback

    def test_generate_session_id(self, migration_service):
        """Test session ID generation."""
        user_id = "user-123-456-789"
        session_id1 = migration_service._generate_session_id(user_id)
        session_id2 = migration_service._generate_session_id(user_id)

        assert session_id1.startswith("session-")
        assert session_id2.startswith("session-")
        assert session_id1 != session_id2  # Should be unique due to timestamp

    async def test_migrate_user_success(self, migration_service, sample_legacy_user, sample_workspace):
        """Test successful user migration."""
        # Mock dependencies
        migration_service._get_user_legacy_data.return_value = sample_legacy_user
        migration_service._get_user_workspace.return_value = sample_workspace["id"]
        migration_service._is_user_migrated.return_value = False
        migration_service._create_migration_log.return_value = "log-123"
        migration_service._create_onboarding_session.return_value = None
        migration_service._create_step_records.return_value = None
        migration_service._generate_bcm_for_session.return_value = True
        migration_service._update_user_migration_status.return_value = None

        # Perform migration
        result = await migration_service.migrate_user(sample_legacy_user["id"])

        # Verify result
        assert result.user_id == sample_legacy_user["id"]
        assert result.session_id.startswith("session-")
        assert result.workspace_id == sample_workspace["id"]
        assert result.legacy_status == sample_legacy_user["onboarding_status"]
        assert result.legacy_step == sample_legacy_user["onboarding_step"]
        assert result.legacy_completed == sample_legacy_user["has_completed_onboarding"]
        assert result.new_status == "completed"
        assert result.current_step == 26  # All steps completed
        assert result.completion_percentage == 100.0
        assert result.bcm_generated is True
        assert result.migrated_at is not None

    async def test_migrate_user_incomplete(self, migration_service, sample_legacy_user, sample_workspace):
        """Test migration of incomplete user."""
        # Mock dependencies
        migration_service._get_user_legacy_data.return_value = sample_legacy_user
        migration_service._get_user_workspace.return_value = sample_workspace["id"]
        migration_service._is_user_migrated.return_value = False
        migration_service._create_migration_log.return_value = "log-123"
        migration_service._create_onboarding_session.return_value = None
        migration_service._create_step_records.return_value = None
        migration_service._generate_bcm_for_session.return_value = False

        # Perform migration
        result = await migration_service.migrate_user(sample_legacy_user["id"])

        # Verify result
        assert result.user_id == sample_legacy_user["id"]
        assert result.legacy_status == sample_legacy_user["onboarding_status"]
        assert result.legacy_step == sample_legacy_user["onboarding_step"]
        assert result.legacy_completed == sample_legacy_user["has_completed_onboarding"]
        assert result.new_status == "active"
        assert result.current_step == 3  # "brand" step
        assert result.completion_percentage == 12.5  # 3/24 * 100
        assert result.bcm_generated is False

    async def test_migrate_user_no_legacy_data(self, migration_service):
        """Test migration when user has no legacy data."""
        # Mock dependencies
        migration_service._get_user_legacy_data.return_value = None

        with pytest.raises(ValueError, match="User .* not found"):
            await migration_service.migrate_user("non-existent-user")

    async def test_migrate_already_migrated(self, migration_service, sample_legacy_user, sample_workspace):
        """Test migration when user is already migrated."""
        # Mock dependencies
        migration_service._get_user_legacy_data.return_value = sample_legacy_user
        migration_service._is_user_migrated.return_value = True

        result = await migration_service.migrate_user(sample_legacy_user["id"])

        # Should return existing migration result
        assert result.user_id == sample_legacy_user["id"]
        assert result.migrated_at is not None

    async def test_migrate_user_with_bcm_generation_error(self, migration_service, sample_completed_legacy_user, sample_workspace):
        """Test migration when BCM generation fails."""
        # Mock dependencies
        migration_service._get_user_legacy_data.return_value = sample_completed_legacy_user
        migration_service._get_user_workspace.return_value = sample_workspace["id"]
        migration_service._is_user_migrated.return_value = False
        migration_service._create_migration_log.return_value = "log-123"
        migration_service._create_onboarding_session.return_value = None
        migration_service._create_step_records.return_value = None
        migration_service._generate_bcm_for_session.return_value = False

        # Mock BCM generation failure
        migration_service._generate_bcm_for_session.side_effect = Exception("BCM generation failed")

        # Migration should still succeed, but without BCM
        result = await migration_service.migrate_user(sample_completed_legacy_user["id"])

        assert result.success is True
        assert result.bcm_generated is False

    async def test_rollback_success(self, migration_service, sample_legacy_user, sample_workspace):
        """Test successful rollback."""
        # Mock dependencies
        migration_service._get_user_legacy_data.return_value = sample_legacy_user
        migration_service._get_existing_migration_result.return_value = MigrationResult(
            user_id=sample_legacy_user["id"],
            session_id="session-123",
            workspace_id=sample_workspace["id"],
            legacy_status=sample_legacy_user["onboarding_status"],
            legacy_step=sample_legacy_user["onboarding_step"],
            legacy_completed=sample_legacy_user["has_completed_onboarding"],
            new_status="completed",
            current_step=26,
            completion_percentage=100.0,
            bcm_generated=True,
            migrated_at=datetime.utcnow()
        )

        # Perform rollback
        success = await migration_service.rollback_user(sample_legacy_user["id"])

        assert success is True

        # Verify user is no longer migrated
        assert not await migration_service._is_user_migrated(sample_legacy_user["id"])

        # Verify legacy status is restored
        legacy_data = await migration_service._get_user_legacy_data(sample_legacy_user["id"])
        assert legacy_data["onboarding_status"] == sample_legacy_user["onboarding_status"]
        assert legacy_data["onboarding_step"] == sample_legacy_user["onboarding_step"]

    async def test_rollback_not_migrated(self, migration_service, sample_legacy_user):
        """Test rollback when user was never migrated."""
        # Mock dependencies
        migration_service._get_user_legacy_data.return_value = sample_legacy_user
        migration_service._get_existing_migration_result.return_value = None

        success = await migration_service.rollback_user(sample_legacy_user["id"])

        assert success is False  # User was never migrated

    async def test_validate_migration_success(self, migration_service, sample_completed_legacy_user, sample_workspace):
        """Test successful migration validation."""
        # Mock dependencies
        migration_service._get_user_legacy_data.return_value = sample_completed_legacy_user
        migration_service._get_existing_migration_result.return_value = MigrationResult(
            user_id=sample_completed_legacy_user["id"],
            session_id="session-123",
            workspace_id=sample_workspace["id"],
            legacy_status=sample_completed_legacy_user["onboarding_status"],
            legacy_step=sample_completed_legacy_user["onboarding_step"],
            legacy_completed=sample_completed_legacy_user["has_completed_onboarding"],
            new_status="completed",
            current_step=26,
            completion_percentage=100.0,
            bcm_generated=True,
            migrated_at=datetime.utcnow()
        )

        result = await migration_service.validate_migration(sample_completed_legacy_user["id"])

        assert result["valid"] is True
        assert result["user_id"] == sample_completed_legacy_user["id"]
        assert result["session_id"] == "session-123"
        assert result["workspace_id"] == sample_workspace["id"]
        assert result["legacy_status"] == "completed"
        assert result["new_status"] == "completed"
        assert result["completion_percentage"] == 100.0
        assert result["bcm_generated"] is True

    async def test_validate_not_migrated(self, migration_service, sample_legacy_user):
        """Test validation when user is not migrated."""
        # Mock dependencies
        migration_service._get_user_legacy_data.return_value = sample_legacy_user
        migration_service._get_existing_migration_result.return_value = None

        result = await migration_service.validate_migration(sample_legacy_user["id"])

        assert result["valid"] is False
        assert result["error"] == "No migration found"

    async def test_get_migration_stats(self, migration_service):
        """Test migration statistics retrieval."""
        # Mock stats
        mock_stats = MigrationStats(
            total_users=100,
            migrated_users=75,
            failed_users=5,
            legacy_completed_users=30,
            legacy_active_users=20,
            avg_completion_time=45.5,
            migration_start_time=datetime.utcnow() - timedelta(days=30),
            migration_end_time=datetime.utcnow() - timedelta(days=1),
            total_migrations=80,
            completed_migrations=75,
            failed_migrations=5
        )

        migration_service.get_migration_stats.return_value = mock_stats

        stats = await migration_service.get_migration_stats()

        assert stats.total_users == 100
        assert stats.migrated_users == 75
        assert stats.failed_users == 5
        assert stats.legacy_completed_users == 30
        assert stats.legacy_active_users == 20
        assert stats.avg_completion_time == 45.5
        assert stats.migration_start_time is not None
        assert stats.migration_end_time is not None

    async def test_cleanup_failed_migrations(self, migration_service):
        """Test cleanup of failed migration logs."""
        # Mock cleanup
        migration_service._cleanup_failed_migrations.return_value = None

        # Call cleanup
        await migration_service._cleanup_failed_migrations(7)

        # Verify cleanup was called (mocked)
        migration_service._cleanup_failed_migrations.assert_called_once_with("older_than_days")

    async def test_migrate_all_users_batch_processing(self, migration_service):
        """Test batch processing of all users."""
        # Mock user data
        users = [
            {"id": f"user-{i}", "email": f"user{i}@example.com", "full_name": f"User {i}",
             "onboarding_status": "active" if i % 3 == 0 else "completed",
             "onboarding_step": ["welcome", "brand", "truth", "offer", "market"][i % 4],
             "has_completed_onboarding": i % 3 == 0}
            for i in range(1, 11)
        ]

        # Mock migration service
        migration_service.get_migration_stats.return_value = MigrationStats(
            total_users=10,
            migrated_users=0,
            failed_users=0,
            legacy_completed_users=3,
            legacy_active_users=7,
            avg_completion_time=None,
            migration_start_time=datetime.utcnow(),
            migration_end_time=None
        )

        # Mock batch migration
        migrate_onboarding_status_batch.return_value = [
            {"user_id": user["id"], "success": True}
            for user in users
        ]

        # Perform migration
        stats = await migration_service.migrate_all_users(batch_size=3)

        assert stats.total_users == 10
        assert stats.migrated_users == 10
        assert stats.failed_users == 0
        assert stats.legacy_completed_users == 3
        assert stats.legacy_active_users == 7

    async def test_error_handling_invalid_user_id(self, migration_service):
        """Test error handling for invalid user ID."""
        with pytest.raises(HTTPException) as exc_info:
            await migration_service.migrate_user("invalid-id")

        assert exc_info.value.status_code == 404
        assert "User not found" in str(exc_info.value.detail)

    async def test_error_handling_no_legacy_data(self, migration_service):
        """Test error handling when user has no legacy data."""
        # Mock user with no legacy data
        migration_service._get_user_legacy_data.return_value = None

        with pytest.raises(ValueError) as exc_info:
            await migration_service.migrate_user("user-123")

        assert "User .* not found" in str(exc_info.value)

    async def test_error_handling_database_error(self, migration_service):
        """Test error handling for database errors."""
        # Mock database failure
        migration_service._get_user_legacy_data.side_effect = Exception("Database connection failed")

        with pytest.raises(Exception) as exc_info:
            await migration_service.migrate_user("user-123")

        assert "Migration failed" in str(exc_info.value)

    async def test_step_mapping_completeness(self, migration_service):
        """Test that all legacy steps are mapped."""
        expected_steps = set(LegacyOnboardingStatus)
        mapped_steps = set(migration_service.step_mapping.values())

        # Check that all expected steps are mapped
        unmapped = expected_steps - mapped_steps
        assert len(unmapped) == 0, f"Unmapped steps: {unmapped}"

        # Check that no extra steps are mapped
        extra_steps = mapped_steps - expected_steps
        assert len(extra_steps) == 0, f"Extra mapped steps: {extra_steps}"

    def test_phase_mapping_completeness(self, migration_service):
        """Test that all step numbers are mapped to phases."""
        # Test key step numbers
        assert migration_service._get_phase_number(1) == 1  # Calibration
        assert migration_service._get_phase_number(5) == 2  # Commerce
        assert migration_service._get_phase_number(12) == 4  # Strategy
        assert migration_service._get_phase_number(19) == 5  # Messaging
        assert migration_service._get_phase_number(24) == 6  # Tactics

    def test_required_steps_definition(self, migration_service):
        """Test required steps definition."""
        # First 12 steps should be required
        for step_num in range(1, 13):
            assert step_num in migration_service.required_steps

        # Steps beyond 12 should not be required
        for step_num in range(13, 25):
            assert step_num not in migration_service.required_steps

    def test_session_id_uniqueness(self, migration_service):
        """Test session ID uniqueness."""
        user_id = "user-123"

        # Generate multiple session IDs
        session_id1 = migration_service._generate_session_id(user_id)
        session_id2 = migration_service._generate_session_id(user_id)
        session_id3 = migration_service._generate_session_id(user_id)

        # All should be unique
        assert session_id1 != session_id2
        assert session_id2 != session_id3
        assert session_id1 != session_id3

    def test_migration_result_serialization(self, migration_service):
        """Test migration result can be serialized."""
        result = MigrationResult(
            user_id="user-123",
            session_id="session-123",
            workspace_id="workspace-123",
            legacy_status="completed",
            legacy_step="export",
            legacy_completed=True,
            new_status="completed",
            current_step=26,
            completion_percentage=100.0,
            bcm_generated=True,
            migrated_at=datetime.utcnow()
        )

        # Test JSON serialization
        json_str = result.json()
        assert json_str is not None

        # Test JSON deserialization
        parsed_result = MigrationResult(**json.loads(json_str))
        assert parsed_result.user_id == result.user_id
        assert parsed_result.session_id == result.session_id
        assert parsed_result.workspace_id == result.workspace_id

    async def test_validation_with_bcm_data(self, migration_service):
        """Test validation with BCM data."""
        # Mock BCM data
        bcm_data = {
            "version": "2.0",
            "checksum": "abc123",
            "generated_at": "2026-01-27T12:00:00Z",
            "size_bytes": 2048,
            "token_count": 512
        }

        migration_service.get_existing_migration_result.return_value = MigrationResult(
            user_id="user-123",
            session_id="session-123",
            workspace_id="workspace-123",
            legacy_status="completed",
            legacy_step="export",
            legacy_completed=True,
            new_status="completed",
            current_step=26,
            completion_percentage=100.0,
            bcm_generated=True,
            migrated_at=datetime.utcnow()
        )

        # Mock BCM query
        migration_service.supabase_client.execute.return_value = [bcm_data]

        result = await migration_service.validate_migration("user-123")

        assert result["valid"] is True
        assert result["bcm_generated"] is True
        assert result["workspace_id"] == "workspace-123"
        assert result["session_id"] == "session-123"

    async def test_validation_without_session_data(self, migration_service):
        """Test validation when session data is missing."""
        migration_service.get_existing_migration_result.return_value = None

        result = await migration_service.validate_migration("user-123")

        assert result["valid"] is False
        assert result["error"] == "No migration found"

    def test_error_handling_rollback(self, migration_service):
        """Test error handling in rollback operations."""
        # Mock rollback failure
        migration_service._delete_onboarding_session.side_effect = Exception("Delete failed")

        with pytest.raises(Exception) as exc_info:
            await migration_service.rollback_user("user-123")

        assert "Rollback failed" in str(exc_info.value)

    def test_get_user_migration_status_migrated(self, migration_service):
        """Test getting migration status for migrated user."""
        # Mock migration result
        migration_service.get_existing_migration_result.return_value = MigrationResult(
            user_id="user-123",
            session_id="session-123",
            workspace_id="workspace-123",
            legacy_status="completed",
            new_status="completed",
            current_step=26,
            completion_percentage=100.0,
            bcm_generated=True,
            migrated_at=datetime.utcnow()
        )

        result = await migration_service.get_user_migration_status("user-123")

        assert result["migration_status"] == "migrated"
        assert result["session_id"] == "session-123"
        assert result["workspace_id"] == "workspace-123"
        assert result["new_status"] == "completed"
        assert result["completion_percentage"] == 100.0
        assert result["bcm_generated"] is True

    def test_get_user_migration_status_legacy(self, migration_service):
        """Test getting migration status for legacy user."""
        # Mock legacy user data
        migration_service._get_user_legacy_data.return_value = {
            "id": "user-123",
            "onboarding_status": "active",
            "onboarding_step": "brand",
            "has_completed_onboarding": False
        }

        result = await migration_service.get_user_migration_status("user-123")

        assert result["migration_status"] == "legacy"
        assert result["legacy_status"] == "active"
        assert result["new_status"] is None  # No new status yet
        assert result["completion_percentage"] is None
        assert result["bcm_generated"] is None

    def test_get_workspace_migration_summary(self, migration_service, sample_workspace):
        """Test workspace migration summary."""
        # Mock workspace data
        migration_service.supabase_client.execute.return_value = [sample_workspace]

        # Mock session data
        session_data = [
            {"id": "session-1", "status": "completed", "completion_percentage": 100.0, "bcm_generated": True},
            {"id": "session-2", "status": "active", "completion_percentage": 50.0, "bcm_generated": False},
            {"id": "session-3", "status": "active", "completion_percentage": 25.0, "bcm_generated": False}
        ]

        migration_service.supabase_client.execute.return_value = session_data

        result = await migration_service.get_workspace_migration_summary(sample_workspace["id"])

        assert result["workspace_id"] == sample_workspace["id"]
        assert result["total_sessions"] == 3
        assert result["completed_sessions"] == 1
        assert result["active_sessions"] == 2
        assert result["avg_completion"] == 58.33  # (100 + 50 + 25) / 3
        assert result["bcm_generated_sessions"] == 1
        assert result["bcm_finalized_sessions"] == 0
        assert result["last_completion_at"] is not None

    def test_get_unmigrated_users(self, migration_service):
        """Test getting list of unmigrated users."""
        # Mock unmigrated users
        migration_service.supabase_client.execute.return_value = [
            {"id": "user-1", "email": "user1@example.com", "onboarding_status": "active"},
            {"id": "user-2", "email": "user2@example.com", "onboarding_status": "none"},
            {"id": "user-3", "email": "user3@example.com", "onboarding_status": "in_progress"}
        ]

        result = await migration_service.get_unmigrated_users()

        assert len(result) == 3
        assert result[0]["user_id"] == "user-1"
        assert result[0]["onboarding_status"] == "active"
        assert result[1]["onboarding_status"] == "none"
        assert result[2]["onboarding_status"] == "in_progress"

    def test_get_migrated_users(self, migration_service):
        """Test getting list of migrated users."""
        # Mock migrated users
        migration_service.supabase_client.execute.return_value = [
            {"id": "user-1", "email": "user1@example.com", "session_id": "session-1"},
            {"id": "user-2", "email": "user2@example.com", "session_id": "session-2"}
        ]

        result = migration_service.get_migrated_users()

        assert len(result) == 2
        assert result[0]["user_id"] == "user-1"
        assert result[0]["session_id"] == "session-1"
        assert result[1]["user_id"] == "user-2"
        assert result[0]["email"] == "user1@example.com"
        assert result[1]["email"] == "user2@example.com"

    def test_get_detailed_migration_details(self, migration_service):
        """Test detailed migration details for admin dashboard."""
        # Mock stats
        stats = MigrationStats(
            total_users=100,
            migrated_users=75,
            failed_users=5,
            legacy_completed_users=30,
            legacy_active_users=20,
            avg_completion_time=45.5,
            migration_start_time=datetime.utcnow() - timedelta(days=30),
            migration_end_time=datetime.utcnow() - timedelta(days=1),
            total_migrations=80,
            completed_migrations=75,
            failed_migrations=5
        )

        migration_service.get_migration_stats.return_value = stats

        # Mock logs
        logs = [
            {
                "id": "log-1", "status": "completed", "error_message": None},
                "id": "log-2", "status": "failed", "error_message": "Database error"},
                "id": "log-3", "status": "completed", "error_message": None}
            ]

        migration_service.get_detailed_migration_details.return_value = {
            "stats": stats,
            "recent_logs": logs,
            "checked_at": datetime.utcnow().isoformat()
        }

        details = migration_service.get_detailed_migration_details()

        assert details["stats"]["total_users"] == 100
        assert details["stats"]["migrated_users"] == 75
        assert details["stats"]["failed_users"] == 5
        assert details["recent_logs"][0]["status"] == "completed"
        assert len(details["recent_logs"]) == 3

    def test_error_handling_database_connection(self, migration_service):
        """Test database connection errors."""
        # Mock database failure
        migration_service.supabase_client.execute.side_effect = Exception("Database connection failed")

        with pytest.raises(Exception) as exc_info:
            await migration_service.get_migration_stats()

        assert "Database connection failed" in str(exc_info.value)

    def test_health_check(self, migration_service):
        """Test health check functionality."""
        # Mock healthy components
        migration_service.supabase_client.execute.return_value = [{"id": "1"}]
        migration_service.get_migration_stats.return_value = MigrationStats(
            total_users=50,
            migrated_users=25,
            failed_users=0,
            legacy_completed_users=10,
            legacy_active_users=15,
            avg_completion_time=30.0,
            migration_start_time=datetime.utcnow() - timedelta(days=15),
            migration_end_time=datetime.utcnow() - timedelta(days=1),
            total_migrations=25,
            completed_migrations=25,
            failed_migrations=0
        )

        health = await migration_service.health_check()

        assert health["healthy"] is True
        assert health["database"] == "connected"
        assert health["migration_service"] == "operational"
        assert health["total_users"] == 50
        assert health["migrated_users"] == 25
        assert health["failed_users"] == 0

    def test_large_batch_processing(self, migration_service):
        """Test large batch processing."""
        # Mock user data for large batch
        users = [
            {"id": f"user-{i}", "email": f"user{i}@example.com", "full_name": f"User {i}",
             "onboarding_status": "active" if i % 3 == 0 else "completed",
             "onboarding_step": ["welcome", "brand", "truth", "offer", "market", "competitors", "angle", "category", "capabilities", "perceptual", "positioning", "gap", "positioning_statements", "focus", "icp", "process", "messaging", "soundbites", "hierarchy", "augmentation", "channels", "market_size", "todos", "synthesis", "export"][i % 4]
            }
            for i in range(1, 51)
        ]

        # Mock migration service
        migration_service.get_migration_stats.return_value = MigrationStats(
            total_users=50,
            migrated_users=0,
            failed_users=0,
            legacy_completed_users=0,
            legacy_active_users=0,
            avg_completion_time=None,
            migration_start_time=datetime.utcnow(),
            migration_end_time=None,
            total_migrations=0,
            completed_migrations=0,
            failed_migrations=0
        )

        # Mock batch processing
        migration_service.migrate_large_batch.return_value = None

        # The function should be called via background task
        # This test verifies the setup, actual execution happens in background

        # Verify setup
        assert migration_service.migrate_large_batch.called is True
        assert migration_service.migrate_large_batch.called_with("user_ids", len(users))
        assert migration_service.migrate_large_batch.called_with("batch_size", 10))

    def test_concurrent_migration_limits(self, migration_service):
        """Test concurrent migration limits."""
        # This would test concurrent migration limits
        # In a real implementation, you'd test actual concurrent processing
        pass

    def test_memory_usage(self, migration_service):
        """Test memory usage during migration."""
        # This would test memory usage during large batch processing
        # In a real implementation, you'd monitor memory usage
        pass

    def test_data_integrity_preservation(self, migration_service):
        """Test that data integrity is preserved during migration."""
        # This would test that all data is correctly preserved
        # In a real implementation, you'd verify checksums and data consistency
        pass

    def test_performance_optimization(self, migration_service):
        """Test performance optimization techniques."""
        # This would test performance optimizations
        # In a real implementation, you'd benchmark and optimize
        pass


if __name__ == "__main__":
    pytest.main()
