"""
Onboarding Status Migration Service

Migrates users from legacy onboarding status to the new Redis-based session system
with Business Context Manifest (BCM) integration.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..services.supabase_client import get_supabase_client
from ..redis.session_manager import get_onboarding_session_manager
from ..integration.bcm_reducer import BCMReducer
from ..schemas.bcm_schema import BusinessContextManifest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
supabase_client = get_supabase_client()
session_manager = get_onboarding_session_manager()
bcm_reducer = BCMReducer()


class MigrationStatus(Enum):
    """Migration status enumeration."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class LegacyOnboardingStatus(Enum):
    """Legacy onboarding status enumeration."""

    NONE = "none"
    WELCOME = "welcome"
    EVIDENCE = "evidence"
    BRAND = "brand"
    TRUTH = "truth"
    OFFER = "offer"
    MARKET = "market"
    COMPETITORS = "competitors"
    ANGLE = "angle"
    CATEGORY = "category"
    CAPABILITIES = "capabilities"
    PERCEPTUAL = "perceptual"
    POSITIONING = "positioning"
    GAP = "gap"
    POSITIONING_STATEMENTS = "positioning_statements"
    FOCUS = "focus"
    ICP = "icp"
    PROCESS = "process"
    MESSAGING = "messaging"
    SOUNDBITES = "soundbites"
    HIERARCHY = "hierarchy"
    AUGMENTATION = "augmentation"
    CHANNELS = "channels"
    MARKET_SIZE = "market_size"
    TODOS = "todos"
    SYNTHESIS = "synthesis"
    EXPORT = "export"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass
class MigrationResult:
    """Result of a migration operation."""

    user_id: str
    session_id: str
    workspace_id: str
    legacy_status: str
    legacy_step: str
    legacy_completed: bool
    new_status: str
    current_step: int
    completion_percentage: float
    bcm_generated: bool
    migrated_at: datetime
    error_message: Optional[str] = None


@dataclass
class MigrationStats:
    """Statistics for migration operations."""

    total_users: int
    migrated_users: int
    failed_users: int
    legacy_completed_users: int
    legacy_active_users: int
    avg_completion_time: Optional[float]
    migration_start_time: datetime
    migration_end_time: Optional[datetime]


class OnboardingMigrationService:
    """Service for migrating onboarding status from legacy to new system."""

    def __init__(self):
        self.step_mapping = {
            LegacyOnboardingStatus.NONE: 0,
            LegacyOnboardingStatus.WELCOME: 1,
            LegacyOnboardingStatus.EVIDENCE: 2,
            LegacyOnboardingStatus.BRAND: 3,
            LegacyOnboardingStatus.TRUTH: 4,
            LegacyOnboardingStatus.OFFER: 5,
            LegacyOnboardingStatus.MARKET: 6,
            LegacyOnboardingStatus.COMPETITORS: 7,
            LegacyOnboardingStatus.ANGLE: 8,
            LegacyOnboardingStatus.CATEGORY: 9,
            LegacyOnboardingStatus.CAPABILITIES: 10,
            LegacyOnboardingStatus.PERCEPTUAL: 11,
            LegacyOnboardingStatus.POSITIONING: 12,
            LegacyOnboardingStatus.GAP: 13,
            LegacyOnboardingStatus.POSITIONING_STATEMENTS: 14,
            LegacyOnboardingStatus.FOCUS: 15,
            LegacyOnboardingStatus.ICP: 16,
            LegacyOnboardingStatus.PROCESS: 17,
            LegacyOnboardingStatus.MESSAGING: 18,
            LegacyOnboardingStatus.SOUNDBITES: 19,
            LegacyOnboardingStatus.HIERARCHY: 20,
            LegacyOnboardingStatus.AUGMENTATION: 21,
            LegacyOnboardingStatus.CHANNELS: 22,
            LegacyOnboardingStatus.MARKET_SIZE: 23,
            LegacyOnboardingStatus.TODOS: 24,
            LegacyOnboardingStatus.SYNTHESIS: 25,
            LegacyOnboardingStatus.EXPORT: 26,
        }

        self.phase_mapping = {
            1: "Calibration",
            2: "Commerce",
            3: "Intelligence",
            4: "Strategy",
            5: "Messaging",
            6: "Tactics",
        }

        self.required_steps = set(range(1, 13))  # First 12 steps are required

    async def migrate_user(self, user_id: str) -> MigrationResult:
        """
        Migrate a single user from legacy onboarding status to new session system.

        Args:
            user_id: The user's UUID

        Returns:
            MigrationResult with details of the migration
        """
        try:
            # Get user's legacy onboarding status
            user_data = await self._get_user_legacy_data(user_id)
            if not user_data:
                raise ValueError(f"User {user_id} not found")

            # Check if already migrated
            if await self._is_user_migrated(user_id):
                logger.info(f"User {user_id} already migrated")
                return await self._get_existing_migration_result(user_id)

            # Get user's workspace
            workspace_id = await self._get_user_workspace(user_id)
            if not workspace_id:
                raise ValueError(f"No workspace found for user {user_id}")

            # Create migration log entry
            migration_log_id = await self._create_migration_log(
                user_id=user_id,
                legacy_status=user_data.get("onboarding_status"),
                legacy_step=user_data.get("onboarding_step"),
                legacy_completed=user_data.get("has_completed_onboarding", False),
            )

            # Create new session
            session_id = self._generate_session_id(user_id)
            await self._create_onboarding_session(
                session_id=session_id,
                user_id=user_id,
                workspace_id=workspace_id,
                legacy_data=user_data,
            )

            # Create step records
            await self._create_step_records(
                session_id=session_id, legacy_data=user_data
            )

            # Generate BCM if user completed onboarding
            bcm_generated = False
            if user_data.get("has_completed_onboarding"):
                bcm_generated = await self._generate_bcm_for_session(
                    session_id=session_id, workspace_id=workspace_id
                )

            # Update migration log
            await self._update_migration_log(
                log_id=migration_log_id,
                status=MigrationStatus.COMPLETED,
                session_id=session_id,
                error_message=None,
            )

            # Update user status
            await self._update_user_migration_status(user_id)

            # Create migration result
            result = MigrationResult(
                user_id=user_id,
                session_id=session_id,
                workspace_id=workspace_id,
                legacy_status=user_data.get("onboarding_status", "none"),
                legacy_step=user_data.get("onboarding_step", "welcome"),
                legacy_completed=user_data.get("has_completed_onboarding", False),
                new_status=(
                    "completed"
                    if user_data.get("has_completed_onboarding")
                    else "active"
                ),
                current_step=self._calculate_current_step(user_data),
                completion_percentage=self._calculate_completion_percentage(user_data),
                bcm_generated=bcm_generated,
                migrated_at=datetime.utcnow(),
            )

            logger.info(f"Successfully migrated user {user_id} to session {session_id}")
            return result

        except Exception as e:
            logger.error(f"Failed to migrate user {user_id}: {str(e)}")

            # Update migration log with error
            if "migration_log_id" in locals():
                await self._update_migration_log(
                    log_id=migration_log_id,
                    status=MigrationStatus.FAILED,
                    error_message=str(e),
                )

            raise

    async def migrate_all_users(self, batch_size: int = 50) -> MigrationStats:
        """
        Migrate all users from legacy onboarding status to new session system.

        Args:
            batch_size: Number of users to migrate in each batch

        Returns:
            MigrationStats with overall migration statistics
        """
        start_time = datetime.utcnow()

        try:
            # Get all users with onboarding data
            users_query = """
                SELECT id, onboarding_status, onboarding_step, has_completed_onboarding,
                       full_name, email, created_at, updated_at
                FROM users
                WHERE onboarding_status IS NOT NULL
                AND onboarding_status != 'migrated'
                ORDER BY created_at
            """

            users = await supabase_client.execute(users_query)

            total_users = len(users)
            migrated_users = 0
            failed_users = 0
            legacy_completed_users = 0
            legacy_active_users = 0

            # Count legacy statuses
            for user in users:
                if user.get("has_completed_onboarding"):
                    legacy_completed_users += 1
                elif user.get("onboarding_status") in ["active", "in_progress"]:
                    legacy_active_users += 1

            # Process users in batches
            for i in range(0, total_users, batch_size):
                batch = users[i : i + batch_size]

                logger.info(
                    f"Processing batch {i//batch_size + 1}/{(total_users + batch_size - 1)//batch_size}"
                )

                for user in batch:
                    try:
                        await self.migrate_user(user["id"])
                        migrated_users += 1
                    except Exception as e:
                        logger.error(f"Failed to migrate user {user['id']}: {str(e)}")
                        failed_users += 1

                # Small delay between batches
                if i + batch_size < total_users:
                    await asyncio.sleep(1)

            end_time = datetime.utcnow()

            stats = MigrationStats(
                total_users=total_users,
                migrated_users=migrated_users,
                failed_users=failed_users,
                legacy_completed_users=legacy_completed_users,
                legacy_active_users=legacy_active_users,
                avg_completion_time=None,  # Could calculate from timestamps
                migration_start_time=start_time,
                migration_end_time=end_time,
            )

            logger.info(
                f"Migration completed: {migrated_users}/{total_users} users migrated, {failed_users} failed"
            )
            return stats

        except Exception as e:
            logger.error(f"Failed to migrate users: {str(e)}")
            raise

    async def rollback_user(self, user_id: str) -> bool:
        """
        Rollback a user's migration, restoring legacy status.

        Args:
            user_id: The user's UUID

        Returns:
            True if rollback was successful
        """
        try:
            # Get migration log entry
            log_query = """
                SELECT id, session_id, legacy_onboarding_status, legacy_onboarding_step,
                       legacy_has_completed_onboarding, status
                FROM onboarding_migration_log
                WHERE source_user_id = $1
                ORDER BY created_at DESC
                LIMIT 1
            """

            log_result = await supabase_client.execute(log_query, [user_id])
            if not log_result:
                logger.warning(f"No migration log found for user {user_id}")
                return False

            migration_log = log_result[0]

            # Delete new session data
            if migration_log["session_id"]:
                await self._delete_onboarding_session(migration_log["session_id"])

            # Restore legacy status
            await self._restore_legacy_status(user_id, migration_log)

            # Update migration log
            await self._update_migration_log(
                log_id=migration_log["id"],
                status=MigrationStatus.FAILED,
                error_message="Rollback requested",
            )

            logger.info(f"Successfully rolled back migration for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to rollback user {user_id}: {str(e)}")
            return False

    async def get_migration_stats(self) -> MigrationStats:
        """
        Get current migration statistics.

        Returns:
            MigrationStats with current statistics
        """
        try:
            # Get user counts
            users_query = """
                SELECT
                    COUNT(*) as total_users,
                    COUNT(CASE WHEN migrated_from_legacy = TRUE THEN 1 END) as migrated_users,
                    COUNT(CASE WHEN has_completed_onboarding = TRUE THEN 1 END) as legacy_completed_users,
                    COUNT(CASE WHEN onboarding_status IN ('active', 'in_progress') THEN 1 END) as legacy_active_users
                FROM users
            """

            result = await supabase_client.execute(users_query)
            stats_data = result[0] if result else {}

            # Get migration log stats
            log_query = """
                SELECT
                    COUNT(*) as total_migrations,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_migrations,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_migrations,
                    MIN(started_at) as earliest_migration,
                    MAX(completed_at) as latest_migration
                FROM onboarding_migration_log
            """

            log_result = await supabase_client.execute(log_query)
            log_data = log_result[0] if log_result else {}

            # Calculate average completion time
            avg_completion_time = None
            if log_data["earliest_migration"] and log_data["latest_migration"]:
                time_diff = (
                    log_data["latest_migration"] - log_data["earliest_migration"]
                )
                avg_completion_time = (
                    time_diff.total_seconds() / log_data["completed_migrations"]
                    if log_data["completed_migrations"] > 0
                    else None
                )

            return MigrationStats(
                total_users=stats_data.get("total_users", 0),
                migrated_users=stats_data.get("migrated_users", 0),
                failed_users=log_data.get("failed_migrations", 0),
                legacy_completed_users=stats_data.get("legacy_completed_users", 0),
                legacy_active_users=stats_data.get("legacy_active_users", 0),
                avg_completion_time=avg_completion_time,
                migration_start_time=log_data.get("earliest_migration"),
                migration_end_time=log_data.get("latest_migration"),
            )

        except Exception as e:
            logger.error(f"Failed to get migration stats: {str(e)}")
            raise

    async def validate_migration(self, user_id: str) -> Dict[str, Any]:
        """
        Validate a user's migration integrity.

        Args:
            user_id: The user's UUID

        Returns:
            Dictionary with validation results
        """
        try:
            # Get migration result
            migration_result = await self._get_existing_migration_result(user_id)
            if not migration_result:
                return {"valid": False, "error": "No migration found"}

            # Validate session data
            session_data = await session_manager.get_all_steps(
                migration_result.session_id
            )
            if not session_data:
                return {"valid": False, "error": "Session data not found"}

            # Validate BCM if generated
            if migration_result.bcm_generated:
                bcm_query = """
                    SELECT version, checksum, generated_at
                    FROM business_context_manifests
                    WHERE workspace_id = $1
                    ORDER BY version DESC
                    LIMIT 1
                """

                bcm_result = await supabase_client.execute(
                    bcm_query, [migration_result.workspace_id]
                )
                if not bcm_result:
                    return {"valid": False, "error": "BCM not found in database"}

            return {
                "valid": True,
                "user_id": user_id,
                "session_id": migration_result.session_id,
                "workspace_id": migration_result.workspace_id,
                "legacy_status": migration_result.legacy_status,
                "new_status": migration_result.new_status,
                "completion_percentage": migration_result.completion_percentage,
                "bcm_generated": migration_result.bcm_generated,
                "migrated_at": migration_result.migrated_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to validate migration for user {user_id}: {str(e)}")
            return {"valid": False, "error": str(e)}

    # Private helper methods

    async def _get_user_legacy_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's legacy onboarding data."""
        query = """
            SELECT id, onboarding_status, onboarding_step, has_completed_onboarding,
                   full_name, email, preferences, metadata, created_at, updated_at
            FROM users
            WHERE id = $1
        """

        result = await supabase_client.execute(query, [user_id])
        return result[0] if result else None

    async def _is_user_migrated(self, user_id: str) -> bool:
        """Check if user has been migrated."""
        query = """
            SELECT 1 FROM onboarding_sessions
            WHERE user_id = $1 AND migrated_from_legacy = TRUE
            LIMIT 1
        """

        result = await supabase_client.execute(query, [user_id])
        return len(result) > 0

    async def _get_existing_migration_result(
        self, user_id: str
    ) -> Optional[MigrationResult]:
        """Get existing migration result for a user."""
        query = """
            SELECT session_id, workspace_id, legacy_onboarding_status, legacy_onboarding_step,
                   legacy_has_completed_onboarding, status, current_step, completion_percentage,
                   bcm_generated, bcm_version, bcm_finalized, migrated_at
            FROM onboarding_sessions
            WHERE user_id = $1 AND migrated_from_legacy = TRUE
            LIMIT 1
        """

        result = await supabase_client.execute(query, [user_id])
        if not result:
            return None

        session_data = result[0]
        return MigrationResult(
            user_id=user_id,
            session_id=session_data["session_id"],
            workspace_id=session_data["workspace_id"],
            legacy_status=session_data["legacy_onboarding_status"],
            legacy_step=session_data["legacy_onboarding_step"],
            legacy_completed=session_data["legacy_has_completed_onboarding"],
            new_status=session_data["status"],
            current_step=session_data["current_step"],
            completion_percentage=float(session_data["completion_percentage"]),
            bcm_generated=session_data["bcm_generated"],
            migrated_at=session_data["migrated_at"],
        )

    async def _get_user_workspace(self, user_id: str) -> Optional[str]:
        """Get user's workspace ID."""
        query = """
            SELECT id FROM workspaces
            WHERE owner_id = $1
            LIMIT 1
        """

        result = await supabase_client.execute(query, [user_id])
        return result[0]["id"] if result else None

    def _generate_session_id(self, user_id: str) -> str:
        """Generate a unique session ID."""
        timestamp = int(datetime.utcnow().timestamp())
        user_hash = user_id[:8] if len(user_id) >= 8 else user_id
        return f"session-{timestamp}-{user_hash}"

    async def _create_migration_log(
        self, user_id: str, legacy_status: str, legacy_step: str, legacy_completed: bool
    ) -> str:
        """Create a migration log entry."""
        query = """
            INSERT INTO onboarding_migration_log (
                migration_type, migration_version, source_user_id,
                legacy_onboarding_status, legacy_onboarding_step, legacy_has_completed_onboarding,
                status, started_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
            RETURNING id
        """

        result = await supabase_client.execute(
            query,
            [
                "legacy_to_redis",
                "1.0",
                user_id,
                legacy_status,
                legacy_step,
                legacy_completed,
                MigrationStatus.PENDING.value,
            ],
        )

        return result[0]["id"]

    async def _update_migration_log(
        self,
        log_id: str,
        status: MigrationStatus,
        session_id: Optional[str] = None,
        error_message: Optional[str] = None,
    ):
        """Update migration log entry."""
        updates = ["status = $1", "updated_at = NOW()"]
        params = [status.value]

        if session_id:
            updates.append("target_session_id = $2")
            params.append(session_id)

        if error_message:
            updates.append("error_message = $2")
            params.append(error_message)

        query = (
            f"UPDATE onboarding_migration_log SET {', '.join(updates)} WHERE id = $3"
        )

        await supabase_client.execute(query, params + [log_id])

    async def _create_onboarding_session(
        self,
        session_id: str,
        user_id: str,
        workspace_id: str,
        legacy_data: Dict[str, Any],
    ):
        """Create new onboarding session."""
        query = """
            INSERT INTO onboarding_sessions (
                session_id, user_id, workspace_id, client_name,
                current_step, total_steps, completion_percentage, status,
                migrated_from_legacy, legacy_onboarding_status, legacy_onboarding_step,
                session_data, metadata
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            RETURNING id
        """

        await supabase_client.execute(
            query,
            [
                session_id,
                user_id,
                workspace_id,
                legacy_data.get("full_name", "Unknown"),
                self._calculate_current_step(legacy_data),
                24,  # Total steps in new system
                self._calculate_completion_percentage(legacy_data),
                (
                    "completed"
                    if legacy_data.get("has_completed_onboarding")
                    else "active"
                ),
                True,  # migrated_from_legacy
                legacy_data.get("onboarding_status", "none"),
                legacy_data.get("onboarding_step", "welcome"),
                json.dumps(
                    {
                        "legacy_status": legacy_data.get("onboarding_status"),
                        "legacy_step": legacy_data.get("onboarding_step"),
                        "legacy_completed": legacy_data.get("has_completed_onboarding"),
                        "preferences": legacy_data.get("preferences", {}),
                        "migrated_at": datetime.utcnow().isoformat(),
                    }
                ),
                json.dumps(
                    {"migration_version": "1.0", "migration_source": "legacy_status"}
                ),
            ],
        )

    async def _create_step_records(self, session_id: str, legacy_data: Dict[str, Any]):
        """Create step records for migrated session."""
        if not legacy_data.get("has_completed_onboarding"):
            return

        # Create step records for completed steps
        current_step = self._calculate_current_step(legacy_data)

        for step_num in range(1, current_step + 1):
            phase_num = self._get_phase_number(step_num)
            step_name = self._get_step_name(step_num)
            is_required = step_num in self.required_steps

            query = """
                INSERT INTO onboarding_steps (
                    session_id, step_number, step_name, phase_number, status,
                    step_data, started_at, completed_at, updated_at, is_required
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), $9)
            """

            await supabase_client.execute(
                query,
                [
                    session_id,
                    step_num,
                    step_name,
                    phase_num,
                    "complete",
                    json.dumps({"migrated_from_legacy": True}),
                    legacy_data.get("created_at", datetime.utcnow()),
                    legacy_data.get("updated_at", datetime.utcnow()),
                    is_required,
                ],
            )

    async def _generate_bcm_for_session(
        self, session_id: str, workspace_id: str
    ) -> bool:
        """Generate BCM for a migrated session."""
        try:
            # Get session data from Redis
            session_data = await session_manager.get_all_steps(session_id)
            if not session_data:
                logger.warning(f"No session data found for session {session_id}")
                return False

            # Add metadata to session data
            session_data["metadata"] = {
                "session_id": session_id,
                "workspace_id": workspace_id,
            }

            # Generate BCM
            manifest = await bcm_reducer.reduce(session_data)

            # Persist BCM to database
            persist_query = """
                INSERT INTO business_context_manifests (
                    workspace_id, session_id, version, checksum, manifest_json,
                    generated_at, token_count, size_bytes
                ) VALUES ($1, $2, $3, $4, $5, NOW(), $6, $7)
                RETURNING id
            """

            manifest_json = manifest.dict()
            manifest_size = len(json.dumps(manifest_json))
            token_count = manifest_size // 4  # Rough estimation

            await supabase_client.execute(
                persist_query,
                [
                    workspace_id,
                    session_id,
                    manifest.version.value,
                    manifest.checksum,
                    manifest_json,
                    token_count,
                    manifest_size,
                ],
            )

            # Update session with BCM info
            update_query = """
                UPDATE onboarding_sessions
                SET bcm_generated = TRUE, bcm_version = $1, bcm_checksum = $2,
                    bcm_generated_at = NOW(), session_data = $3
                WHERE session_id = $4
            """

            await supabase_client.execute(
                update_query, [manifest.checksum, json.dumps(session_data), session_id]
            )

            logger.info(f"Generated BCM for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to generate BCM for session {session_id}: {str(e)}")
            return False

    async def _update_user_migration_status(self, user_id: str):
        """Update user to mark migration complete."""
        query = """
            UPDATE users
            SET onboarding_status = 'migrated', updated_at = NOW()
            WHERE id = $1
        """

        await supabase_client.execute(query, [user_id])

    async def _delete_onboarding_session(self, session_id: str):
        """Delete onboarding session and related data."""
        # Delete steps first
        await supabase_client.execute(
            "DELETE FROM onboarding_steps WHERE session_id = $1", [session_id]
        )

        # Delete session
        await supabase_client.execute(
            "DELETE FROM onboarding_sessions WHERE session_id = $1", [session_id]
        )

    async def _restore_legacy_status(self, user_id: str, migration_log: Dict[str, Any]):
        """Restore user's legacy onboarding status."""
        query = """
            UPDATE users
            SET onboarding_status = $1, onboarding_step = $2, has_completed_onboarding = $3,
                updated_at = NOW()
            WHERE id = $4
        """

        await supabase_client.execute(
            query,
            [
                migration_log["legacy_onboarding_status"],
                migration_log["legacy_onboarding_step"],
                migration_log["legacy_has_completed_onboarding"],
                user_id,
            ],
        )

    def _calculate_current_step(self, legacy_data: Dict[str, Any]) -> int:
        """Calculate current step number from legacy data."""
        legacy_step = legacy_data.get("onboarding_step", "welcome")

        try:
            return self.step_mapping.get(LegacyOnboardingStatus(legacy_step.upper()), 1)
        except (ValueError, KeyError):
            return 1

    def _calculate_completion_percentage(self, legacy_data: Dict[str, Any]) -> float:
        """Calculate completion percentage from legacy data."""
        if legacy_data.get("has_completed_onboarding"):
            return 100.0

        current_step = self._calculate_current_step(legacy_data)
        return min((current_step / 24) * 100, 99.9)  # Cap at 99.9%

    def _get_phase_number(self, step_number: int) -> int:
        """Get phase number for a step."""
        if step_number <= 4:
            return 1  # Calibration
        elif step_number <= 5:
            return 2  # Commerce
        elif step_number <= 8:
            return 3  # Intelligence
        elif step_number <= 13:
            return 4  # Strategy
        elif step_number <= 19:
            return 5  # Messaging
        else:
            return 6  # Tactics

    def _get_step_name(self, step_number: int) -> str:
        """Get step name for a step number."""
        step_names = {
            1: "Evidence Vault",
            2: "Brand Synthesis",
            3: "Strategic Integrity",
            4: "Truth Confirmation",
            5: "The Offer",
            6: "Market Intelligence",
            7: "Competitive Landscape",
            8: "Comparative Angle",
            9: "Market Category",
            10: "Product Capabilities",
            11: "Perceptual Map",
            12: "Position Grid",
            13: "Gap Analysis",
            14: "Positioning Statements",
            15: "Focus & Sacrifice",
            16: "ICP Personas",
            17: "Market Education",
            18: "Messaging Rules",
            19: "Soundbites Library",
            20: "Channel Strategy",
            21: "Market Size",
            22: "Validation Tasks",
            23: "Final Synthesis",
            24: "Export & Launch",
        }

        return step_names.get(step_number, f"Step {step_number}")

    async def _cleanup_failed_migrations(self, older_than_days: int = 7):
        """Clean up failed migration logs older than specified days."""
        cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)

        query = """
            DELETE FROM onboarding_migration_log
            WHERE status = 'failed' AND started_at < $1
        """

        await supabase_client.execute(query, [cutoff_date])
        logger.info(f"Cleaned up migration logs older than {older_than_days} days")


# Migration utility functions
async def migrate_onboarding_status_batch(user_ids: List[str]) -> List[MigrationResult]:
    """Migrate a batch of users from legacy onboarding status."""
    migration_service = OnboardingMigrationService()
    results = []

    for user_id in user_ids:
        try:
            result = await migration_service.migrate_user(user_id)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to migrate user {user_id}: {str(e)}")
            # Could create a failed result here

    return results


async def rollback_onboarding_status_batch(user_ids: List[str]) -> List[bool]:
    """Rollback a batch of user migrations."""
    migration_service = OnboardingMigrationService()
    results = []

    for user_id in user_ids:
        try:
            result = await migration_service.rollback_user(user_id)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to rollback user {user_id}: {str(e)}")
            results.append(False)

    return results
