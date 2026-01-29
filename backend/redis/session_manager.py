"""
Onboarding Session Manager using Redis

Provides specialized session management for the 23-step onboarding process
with connection pooling, TTL management, and error handling with retries.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, ValidationError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .client import get_redis

logger = logging.getLogger(__name__)


# =============================================================================
# SCHEMA DEFINITIONS
# =============================================================================


class StepDataSchema(BaseModel):
    """Schema for individual step data validation."""

    step_id: int = Field(ge=1, le=23, description="Step number (1-23)")
    data: Dict[str, Any] = Field(description="Step-specific data")
    saved_at: str = Field(description="ISO timestamp when saved")
    version: int = Field(default=1, description="Data version")
    is_draft: bool = Field(default=False, description="Whether this is a draft")


class SessionMetadataSchema(BaseModel):
    """Schema for session metadata validation."""

    session_id: str = Field(description="Unique session identifier")
    user_id: str = Field(description="User ID")
    workspace_id: str = Field(description="Workspace ID")
    started_at: str = Field(description="ISO timestamp when session started")
    is_draft: bool = Field(
        default=False, description="Whether session is in draft mode"
    )
    draft_step: Optional[int] = Field(
        None, ge=1, le=23, description="Current draft step"
    )
    additional_metadata: Dict[str, Any] = Field(default_factory=dict)


class ProgressSchema(BaseModel):
    """Schema for progress tracking validation."""

    completed: int = Field(ge=0, le=23, description="Number of completed steps")
    total: int = Field(default=23, description="Total number of steps")
    percentage: float = Field(ge=0, le=100, description="Completion percentage")
    started_at: str = Field(description="ISO timestamp when started")
    last_updated: str = Field(description="ISO timestamp of last update")
    is_draft: bool = Field(
        default=False, description="Whether progress is for draft session"
    )


class OnboardingSessionManager:
    """Redis-based session manager for onboarding workflow."""

    # Redis key schema
    STEP_KEY_PREFIX = "onboarding:{}:step:{}"
    PROGRESS_KEY_PREFIX = "onboarding:{}:progress"
    METADATA_KEY_PREFIX = "onboarding:{}:metadata"
    DRAFT_KEY_PREFIX = "onboarding:{}:draft"
    CLEANUP_LOCK_KEY = "onboarding:cleanup_lock"

    # Configuration
    SESSION_TTL = 7 * 24 * 60 * 60  # 7 days in seconds
    DRAFT_TTL = 24 * 60 * 60  # 24 hours for drafts
    TOTAL_STEPS = 23
    MAX_RETRIES = 3
    RETRY_BASE_DELAY = 1  # seconds
    CLEANUP_BATCH_SIZE = 100
    CLEANUP_INTERVAL = 3600  # 1 hour between cleanups

    def __init__(self):
        self.redis = get_redis()
        self._connection_pool = None

    async def _get_connection_pool(self):
        """Get or create Redis connection pool."""
        if self._connection_pool is None:
            # Use the existing async client from RedisClient
            self._connection_pool = self.redis.async_client
        return self._connection_pool

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        before_sleep=lambda retry_state: logger.warning(
            f"Redis operation failed (attempt {retry_state.attempt_number}), retrying..."
        ),
    )
    async def save_step(self, session_id: str, step_id: int, data: dict) -> bool:
        """
        Save onboarding step data to Redis with TTL.

        Args:
            session_id: Unique session identifier
            step_id: Step number (1-23)
            data: Step data to store

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate inputs
            if (
                not session_id
                or not isinstance(step_id, int)
                or step_id < 1
                or step_id > self.TOTAL_STEPS
            ):
                raise ValueError(
                    f"Invalid step_id: {step_id}. Must be 1-{self.TOTAL_STEPS}"
                )

            if not isinstance(data, dict):
                raise ValueError("Step data must be a dictionary")

            # Prepare step data with metadata
            step_data = {
                "step_id": step_id,
                "data": data,
                "saved_at": datetime.utcnow().isoformat(),
                "version": 1,
                "is_draft": False,  # Default to non-draft unless specified
            }

            # Generate Redis key
            key = self.STEP_KEY_PREFIX.format(session_id, step_id)

            # Validate step data schema
            try:
                validated_data = StepDataSchema(**step_data)
                step_data = validated_data.model_dump()
            except ValidationError as e:
                logger.error(f"Step data validation failed for step {step_id}: {e}")
                raise ValueError(f"Invalid step data: {e}")

            # Save to Redis with TTL
            success = await self.redis.set_json(key, step_data, ex=self.SESSION_TTL)

            if success:
                logger.info(f"Saved step {step_id} for session {session_id}")
                # Update progress
                await self.update_progress(session_id, step_id)
            else:
                logger.error(f"Failed to save step {step_id} for session {session_id}")

            return success

        except Exception as e:
            logger.error(
                f"Error saving step {step_id} for session {session_id}: {str(e)}"
            )
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    )
    async def get_step(self, session_id: str, step_id: int) -> Optional[dict]:
        """
        Retrieve onboarding step data from Redis.

        Args:
            session_id: Unique session identifier
            step_id: Step number (1-23)

        Returns:
            Step data dictionary or None if not found
        """
        try:
            # Validate inputs
            if (
                not session_id
                or not isinstance(step_id, int)
                or step_id < 1
                or step_id > self.TOTAL_STEPS
            ):
                return None

            # Generate Redis key
            key = self.STEP_KEY_PREFIX.format(session_id, step_id)

            # Retrieve from Redis
            step_data = await self.redis.get_json(key)

            if step_data:
                logger.debug(f"Retrieved step {step_id} for session {session_id}")
                return step_data
            else:
                logger.debug(f"Step {step_id} not found for session {session_id}")
                return None

        except Exception as e:
            logger.error(
                f"Error retrieving step {step_id} for session {session_id}: {str(e)}"
            )
            return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    )
    async def update_progress(self, session_id: str, completed_step: int) -> dict:
        """
        Update session progress tracking.

        Args:
            session_id: Unique session identifier
            completed_step: Highest completed step number

        Returns:
            Updated progress dictionary
        """
        try:
            # Get current progress
            current_progress = await self.get_progress(session_id)

            if not current_progress:
                current_progress = {
                    "completed": 0,
                    "total": self.TOTAL_STEPS,
                    "started_at": datetime.utcnow().isoformat(),
                    "last_updated": datetime.utcnow().isoformat(),
                }

            # Update progress if this step is higher than previously completed
            if completed_step > current_progress.get("completed", 0):
                current_progress["completed"] = completed_step
                current_progress["last_updated"] = datetime.utcnow().isoformat()

                # Calculate completion percentage
                percentage = (completed_step / self.TOTAL_STEPS) * 100
                current_progress["percentage"] = round(percentage, 2)

                # Save to Redis
                key = self.PROGRESS_KEY_PREFIX.format(session_id)
                success = await self.redis.set_json(
                    key, current_progress, ex=self.SESSION_TTL
                )

                if success:
                    logger.info(
                        f"Updated progress for session {session_id}: {completed_step}/{self.TOTAL_STEPS}"
                    )
                else:
                    logger.error(f"Failed to update progress for session {session_id}")

            return current_progress

        except Exception as e:
            logger.error(f"Error updating progress for session {session_id}: {str(e)}")
            return {"completed": 0, "total": self.TOTAL_STEPS, "error": str(e)}

    async def get_progress(self, session_id: str) -> Optional[dict]:
        """
        Get current session progress.

        Args:
            session_id: Unique session identifier

        Returns:
            Progress dictionary or None if not found
        """
        try:
            if not session_id:
                return None

            key = self.PROGRESS_KEY_PREFIX.format(session_id)
            progress = await self.redis.get_json(key)

            if progress:
                logger.debug(f"Retrieved progress for session {session_id}")
                return progress
            else:
                logger.debug(f"Progress not found for session {session_id}")
                return None

        except Exception as e:
            logger.error(
                f"Error retrieving progress for session {session_id}: {str(e)}"
            )
            return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    )
    async def get_all_steps(self, session_id: str) -> dict:
        """
        Retrieve all steps for a session.

        Args:
            session_id: Unique session identifier

        Returns:
            Dictionary with all step data
        """
        try:
            if not session_id:
                return {}

            all_steps = {}

            # Retrieve all steps (1 to 23)
            for step_id in range(1, self.TOTAL_STEPS + 1):
                step_data = await self.get_step(session_id, step_id)
                if step_data:
                    all_steps[str(step_id)] = step_data

            logger.info(f"Retrieved {len(all_steps)} steps for session {session_id}")
            return all_steps

        except Exception as e:
            logger.error(
                f"Error retrieving all steps for session {session_id}: {str(e)}"
            )
            return {}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    )
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete all data for a session.

        Args:
            session_id: Unique session identifier

        Returns:
            True if successful, False otherwise
        """
        try:
            if not session_id:
                return False

            deleted_count = 0

            # Delete all step keys
            for step_id in range(1, self.TOTAL_STEPS + 1):
                step_key = self.STEP_KEY_PREFIX.format(session_id, step_id)
                result = await self.redis.delete(step_key)
                if result > 0:
                    deleted_count += 1

            # Delete progress key
            progress_key = self.PROGRESS_KEY_PREFIX.format(session_id)
            result = await self.redis.delete(progress_key)
            if result > 0:
                deleted_count += 1

            # Delete metadata key
            metadata_key = self.METADATA_KEY_PREFIX.format(session_id)
            result = await self.redis.delete(metadata_key)
            if result > 0:
                deleted_count += 1

            logger.info(f"Deleted session {session_id}: {deleted_count} keys removed")
            return deleted_count > 0

        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {str(e)}")
            return False

    async def set_metadata(
        self,
        session_id: str,
        user_id: str,
        workspace_id: str,
        additional_metadata: Optional[dict] = None,
    ) -> bool:
        """
        Set session metadata.

        Args:
            session_id: Unique session identifier
            user_id: User ID
            workspace_id: Workspace ID
            additional_metadata: Additional metadata to store

        Returns:
            True if successful, False otherwise
        """
        try:
            metadata = {
                "session_id": session_id,
                "user_id": user_id,
                "workspace_id": workspace_id,
                "started_at": datetime.utcnow().isoformat(),
                "additional_metadata": additional_metadata or {},
            }

            key = self.METADATA_KEY_PREFIX.format(session_id)
            success = await self.redis.set_json(key, metadata, ex=self.SESSION_TTL)

            if success:
                logger.info(f"Set metadata for session {session_id}")
            else:
                logger.error(f"Failed to set metadata for session {session_id}")

            return success

        except Exception as e:
            logger.error(f"Error setting metadata for session {session_id}: {str(e)}")
            return False

    async def get_metadata(self, session_id: str) -> Optional[dict]:
        """
        Get session metadata.

        Args:
            session_id: Unique session identifier

        Returns:
            Metadata dictionary or None if not found
        """
        try:
            if not session_id:
                return None

            key = self.METADATA_KEY_PREFIX.format(session_id)
            metadata = await self.redis.get_json(key)

            if metadata:
                logger.debug(f"Retrieved metadata for session {session_id}")
                return metadata
            else:
                logger.debug(f"Metadata not found for session {session_id}")
                return None

        except Exception as e:
            logger.error(
                f"Error retrieving metadata for session {session_id}: {str(e)}"
            )
            return None

    async def get_session_summary(self, session_id: str) -> dict:
        """
        Get complete session summary including progress, metadata, and step count.

        Args:
            session_id: Unique session identifier

        Returns:
            Session summary dictionary
        """
        try:
            # Get all components
            progress = await self.get_progress(session_id)
            metadata = await self.get_metadata(session_id)
            all_steps = await self.get_all_steps(session_id)

            # Calculate summary stats
            completed_steps = len(all_steps)
            total_steps = self.TOTAL_STEPS
            completion_percentage = (
                (completed_steps / total_steps) * 100 if total_steps > 0 else 0
            )

            # Get session age
            session_age = None
            if metadata and metadata.get("started_at"):
                started_at = datetime.fromisoformat(
                    metadata["started_at"].replace("Z", "+00:00")
                )
                session_age = (datetime.utcnow() - started_at).total_seconds()

            summary = {
                "session_id": session_id,
                "progress": progress,
                "metadata": metadata,
                "stats": {
                    "completed_steps": completed_steps,
                    "total_steps": total_steps,
                    "completion_percentage": round(completion_percentage, 2),
                    "session_age_seconds": session_age,
                    "last_updated": progress.get("last_updated") if progress else None,
                },
            }

            return summary

        except Exception as e:
            logger.error(f"Error getting session summary for {session_id}: {str(e)}")
            return {
                "session_id": session_id,
                "error": str(e),
                "stats": {
                    "completed_steps": 0,
                    "total_steps": self.TOTAL_STEPS,
                    "completion_percentage": 0,
                },
            }

    async def health_check(self) -> dict:
        """
        Check Redis connection and basic operations.

        Returns:
            Health check results
        """
        try:
            # Test Redis connection
            ping_result = await self.redis.ping()

            # Test basic operations
            test_key = "health_check_test"
            test_value = {"test": True, "timestamp": datetime.utcnow().isoformat()}

            # Test set
            set_result = await self.redis.set_json(test_key, test_value, ex=60)

            # Test get
            get_result = await self.redis.get_json(test_key)

            # Test delete
            delete_result = await self.redis.delete(test_key)

            health_status = {
                "redis_connection": ping_result,
                "set_operation": set_result,
                "get_operation": get_result == test_value,
                "delete_operation": delete_result > 0,
                "overall_healthy": all(
                    [
                        ping_result,
                        set_result,
                        get_result == test_value,
                        delete_result > 0,
                    ]
                ),
            }

            return health_status

        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "redis_connection": False,
                "set_operation": False,
                "get_operation": False,
                "delete_operation": False,
                "overall_healthy": False,
                "error": str(e),
            }

    async def save_draft(self, session_id: str, step_id: int, data: dict) -> bool:
        """
        Save onboarding step data as a draft.

        Args:
            session_id: Unique session identifier
            step_id: Step number (1-23)
            data: Step data to store

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate inputs
            if (
                not session_id
                or not isinstance(step_id, int)
                or step_id < 1
                or step_id > self.TOTAL_STEPS
            ):
                raise ValueError(
                    f"Invalid step_id: {step_id}. Must be 1-{self.TOTAL_STEPS}"
                )

            if not isinstance(data, dict):
                raise ValueError("Step data must be a dictionary")

            # Prepare draft step data
            step_data = {
                "step_id": step_id,
                "data": data,
                "saved_at": datetime.utcnow().isoformat(),
                "version": 1,
                "is_draft": True,
            }

            # Validate draft data schema
            try:
                validated_data = StepDataSchema(**step_data)
                step_data = validated_data.model_dump()
            except ValidationError as e:
                logger.error(f"Draft data validation failed for step {step_id}: {e}")
                raise ValueError(f"Invalid draft data: {e}")

            # Generate Redis key for draft
            key = self.DRAFT_KEY_PREFIX.format(session_id, step_id)

            # Save draft to Redis with shorter TTL
            success = await self.redis.set_json(key, step_data, ex=self.DRAFT_TTL)

            if success:
                logger.info(f"Saved draft step {step_id} for session {session_id}")
                # Update session metadata to mark as draft
                await self.mark_session_draft(session_id, step_id)
            else:
                logger.error(
                    f"Failed to save draft step {step_id} for session {session_id}"
                )

            return success

        except Exception as e:
            logger.error(
                f"Error saving draft step {step_id} for session {session_id}: {str(e)}"
            )
            return False

    async def get_draft(self, session_id: str, step_id: int) -> Optional[dict]:
        """
        Retrieve draft step data from Redis.

        Args:
            session_id: Unique session identifier
            step_id: Step number (1-23)

        Returns:
            Draft step data dictionary or None if not found
        """
        try:
            # Validate inputs
            if (
                not session_id
                or not isinstance(step_id, int)
                or step_id < 1
                or step_id > self.TOTAL_STEPS
            ):
                return None

            # Generate Redis key for draft
            key = self.DRAFT_KEY_PREFIX.format(session_id, step_id)

            # Retrieve draft from Redis
            draft_data = await self.redis.get_json(key)

            if draft_data:
                logger.debug(f"Retrieved draft step {step_id} for session {session_id}")
                return draft_data
            else:
                logger.debug(f"Draft step {step_id} not found for session {session_id}")
                return None

        except Exception as e:
            logger.error(
                f"Error retrieving draft step {step_id} for session {session_id}: {str(e)}"
            )
            return None

    async def promote_draft_to_step(self, session_id: str, step_id: int) -> bool:
        """
        Promote a draft step to a regular step.

        Args:
            session_id: Unique session identifier
            step_id: Step number (1-23)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get draft data
            draft_data = await self.get_draft(session_id, step_id)
            if not draft_data:
                logger.warning(
                    f"No draft found for step {step_id} in session {session_id}"
                )
                return False

            # Update draft to non-draft status
            draft_data["is_draft"] = False
            draft_data["saved_at"] = datetime.utcnow().isoformat()

            # Save as regular step
            success = await self.save_step(session_id, step_id, draft_data["data"])

            if success:
                # Remove draft
                draft_key = self.DRAFT_KEY_PREFIX.format(session_id, step_id)
                await self.redis.delete(draft_key)

                # Update session metadata
                await self.unmark_session_draft(session_id)

                logger.info(
                    f"Promoted draft step {step_id} to regular step for session {session_id}"
                )

            return success

        except Exception as e:
            logger.error(
                f"Error promoting draft step {step_id} for session {session_id}: {str(e)}"
            )
            return False

    async def mark_session_draft(self, session_id: str, current_step: int) -> bool:
        """
        Mark session as being in draft mode.

        Args:
            session_id: Unique session identifier
            current_step: Current step being worked on

        Returns:
            True if successful, False otherwise
        """
        try:
            metadata = await self.get_metadata(session_id)
            if metadata:
                metadata["is_draft"] = True
                metadata["draft_step"] = current_step
                metadata["last_updated"] = datetime.utcnow().isoformat()

                key = self.METADATA_KEY_PREFIX.format(session_id)
                success = await self.redis.set_json(key, metadata, ex=self.SESSION_TTL)

                if success:
                    logger.info(
                        f"Marked session {session_id} as draft at step {current_step}"
                    )

                return success

            return False

        except Exception as e:
            logger.error(f"Error marking session {session_id} as draft: {str(e)}")
            return False

    async def unmark_session_draft(self, session_id: str) -> bool:
        """
        Remove draft status from session.

        Args:
            session_id: Unique session identifier

        Returns:
            True if successful, False otherwise
        """
        try:
            metadata = await self.get_metadata(session_id)
            if metadata and metadata.get("is_draft"):
                metadata["is_draft"] = False
                metadata.pop("draft_step", None)
                metadata["last_updated"] = datetime.utcnow().isoformat()

                key = self.METADATA_KEY_PREFIX.format(session_id)
                success = await self.redis.set_json(key, metadata, ex=self.SESSION_TTL)

                if success:
                    logger.info(f"Unmarked session {session_id} as draft")

                return success

            return True  # Already not a draft

        except Exception as e:
            logger.error(f"Error unmarking session {session_id} as draft: {str(e)}")
            return False

    async def refresh_session_ttl(self, session_id: str) -> bool:
        """
        Refresh TTL for all session keys to prevent expiration.

        Args:
            session_id: Unique session identifier

        Returns:
            True if successful, False otherwise
        """
        try:
            if not session_id:
                return False

            refreshed_count = 0

            # Refresh all step keys
            for step_id in range(1, self.TOTAL_STEPS + 1):
                step_key = self.STEP_KEY_PREFIX.format(session_id, step_id)
                result = await self.redis.expire(step_key, self.SESSION_TTL)
                if result:
                    refreshed_count += 1

            # Refresh progress key
            progress_key = self.PROGRESS_KEY_PREFIX.format(session_id)
            result = await self.redis.expire(progress_key, self.SESSION_TTL)
            if result:
                refreshed_count += 1

            # Refresh metadata key
            metadata_key = self.METADATA_KEY_PREFIX.format(session_id)
            result = await self.redis.expire(metadata_key, self.SESSION_TTL)
            if result:
                refreshed_count += 1

            logger.info(
                f"Refreshed TTL for {refreshed_count} keys in session {session_id}"
            )
            return refreshed_count > 0

        except Exception as e:
            logger.error(f"Error refreshing TTL for session {session_id}: {str(e)}")
            return False

    async def cleanup_expired_sessions(self, force: bool = False) -> int:
        """
        Clean up expired sessions and orphaned keys.

        Args:
            force: Force cleanup even if recently run

        Returns:
            Number of keys cleaned up
        """
        try:
            # Check if cleanup is already running
            if not force:
                lock_exists = await self.redis.exists(self.CLEANUP_LOCK_KEY)
                if lock_exists:
                    logger.info("Cleanup already running, skipping")
                    return 0

                # Set cleanup lock
                lock_set = await self.redis.setex(
                    self.CLEANUP_LOCK_KEY, self.CLEANUP_INTERVAL, "cleanup_running"
                )
                if not lock_set:
                    logger.info("Could not acquire cleanup lock, skipping")
                    return 0

            cleaned_count = 0

            # Find all onboarding keys
            all_keys = []
            cursor = 0

            while True:
                cursor, keys = await self.redis.scan(
                    cursor, match="onboarding:*", count=self.CLEANUP_BATCH_SIZE
                )
                all_keys.extend(keys)

                if cursor == 0:
                    break

            # Check each key for expiration
            for key in all_keys:
                try:
                    ttl = await self.redis.ttl(key)

                    # Clean up keys with no TTL or expired TTL
                    if ttl == -1 or ttl == -2:
                        # -1: no expiration set, -2: key doesn't exist (shouldn't happen)
                        if ttl == -1:
                            # Key exists but has no expiration - set one
                            await self.redis.expire(key, self.SESSION_TTL)
                            logger.debug(f"Set TTL for key without expiration: {key}")

                    elif ttl <= 0:
                        # Key is expired, delete it
                        result = await self.redis.delete(key)
                        if result > 0:
                            cleaned_count += 1
                            logger.debug(f"Cleaned up expired key: {key}")

                except Exception as e:
                    logger.warning(f"Error checking key {key}: {e}")
                    continue

            # Clean up orphaned draft keys (drafts without corresponding sessions)
            await self._cleanup_orphaned_drafts()

            # Release cleanup lock
            await self.redis.delete(self.CLEANUP_LOCK_KEY)

            logger.info(f"Cleanup completed: {cleaned_count} keys removed")
            return cleaned_count

        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            # Ensure lock is released on error
            try:
                await self.redis.delete(self.CLEANUP_LOCK_KEY)
            except:
                pass
            return 0

    async def _cleanup_orphaned_drafts(self) -> int:
        """
        Clean up draft keys that don't have corresponding session metadata.

        Returns:
            Number of orphaned drafts cleaned up
        """
        try:
            cleaned_count = 0

            # Find all draft keys
            cursor = 0
            draft_keys = []

            while True:
                cursor, keys = await self.redis.scan(
                    cursor, match="onboarding:*:draft", count=self.CLEANUP_BATCH_SIZE
                )
                draft_keys.extend(keys)

                if cursor == 0:
                    break

            # Check each draft key
            for draft_key in draft_keys:
                try:
                    # Extract session_id from draft key
                    parts = draft_key.split(":")
                    if len(parts) >= 2:
                        session_id = parts[1]

                        # Check if session metadata exists
                        metadata_key = self.METADATA_KEY_PREFIX.format(session_id)
                        metadata_exists = await self.redis.exists(metadata_key)

                        if not metadata_exists:
                            # No session metadata, clean up the draft
                            result = await self.redis.delete(draft_key)
                            if result > 0:
                                cleaned_count += 1
                                logger.debug(f"Cleaned up orphaned draft: {draft_key}")

                except Exception as e:
                    logger.warning(f"Error checking draft key {draft_key}: {e}")
                    continue

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up orphaned drafts: {str(e)}")
            return 0

    async def get_session_statistics(self) -> dict:
        """
        Get statistics about all onboarding sessions.

        Returns:
            Session statistics dictionary
        """
        try:
            stats = {
                "total_sessions": 0,
                "active_sessions": 0,
                "draft_sessions": 0,
                "completed_sessions": 0,
                "average_completion": 0.0,
                "oldest_session_age_hours": 0,
                "newest_session_age_hours": 0,
            }

            # Find all session metadata keys
            cursor = 0
            session_ids = set()

            while True:
                cursor, keys = await self.redis.scan(
                    cursor, match="onboarding:*:metadata", count=self.CLEANUP_BATCH_SIZE
                )

                for key in keys:
                    parts = key.split(":")
                    if len(parts) >= 2:
                        session_ids.add(parts[1])

                if cursor == 0:
                    break

            stats["total_sessions"] = len(session_ids)

            if not session_ids:
                return stats

            completion_percentages = []
            session_ages = []
            current_time = datetime.utcnow()

            for session_id in session_ids:
                try:
                    # Get session summary
                    summary = await self.get_session_summary(session_id)

                    if summary.get("error"):
                        continue

                    # Check if session is a draft
                    metadata = summary.get("metadata", {})
                    if metadata.get("is_draft"):
                        stats["draft_sessions"] += 1
                    else:
                        stats["active_sessions"] += 1

                    # Get completion percentage
                    session_stats = summary.get("stats", {})
                    completion = session_stats.get("completion_percentage", 0)
                    completion_percentages.append(completion)

                    # Check if completed
                    if session_stats.get("completed_steps", 0) >= self.TOTAL_STEPS:
                        stats["completed_sessions"] += 1

                    # Calculate session age
                    if metadata.get("started_at"):
                        started_at = datetime.fromisoformat(
                            metadata["started_at"].replace("Z", "+00:00")
                        )
                        age_hours = (current_time - started_at).total_seconds() / 3600
                        session_ages.append(age_hours)

                except Exception as e:
                    logger.warning(f"Error getting stats for session {session_id}: {e}")
                    continue

            # Calculate averages
            if completion_percentages:
                stats["average_completion"] = sum(completion_percentages) / len(
                    completion_percentages
                )

            if session_ages:
                stats["oldest_session_age_hours"] = max(session_ages)
                stats["newest_session_age_hours"] = min(session_ages)

            return stats

        except Exception as e:
            logger.error(f"Error getting session statistics: {str(e)}")
            return {"error": str(e)}


# Singleton instance
_session_manager: Optional[OnboardingSessionManager] = None


def get_onboarding_session_manager() -> OnboardingSessionManager:
    """Get singleton onboarding session manager."""
    global _session_manager
    if _session_manager is None:
        _session_manager = OnboardingSessionManager()
    return _session_manager
