"""
Onboarding State Service - Centralized state management for onboarding workflow
Handles synchronization, locking, and persistence across all onboarding steps.
"""

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from supabase import Client

from .services.upstash_client import UpstashClient

logger = logging.getLogger(__name__)


class StepStatus(Enum):
    """Step execution status"""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StepState:
    """Individual step state"""

    step_id: str
    status: StepStatus
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    data_hash: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None


@dataclass
class OnboardingState:
    """Complete onboarding state for a workspace"""

    workspace_id: str
    current_step: Optional[str] = None
    steps: Dict[str, StepState] = None
    created_at: float = None
    updated_at: float = None
    lock_expires_at: Optional[float] = None
    lock_owner: Optional[str] = None

    def __post_init__(self):
        if self.steps is None:
            self.steps = {}
        if self.created_at is None:
            self.created_at = time.time()
        self.updated_at = time.time()


class OnboardingStateService:
    """
    Centralized onboarding state management service.
    Handles Redis caching, database persistence, and step synchronization.
    """

    def __init__(self, db_client: Client, redis_client: UpstashClient):
        self.db_client = db_client
        self.redis = redis_client
        self.lock_timeout = 300  # 5 minutes
        self.state_cache_ttl = 3600  # 1 hour

        # Define step dependencies
        self.step_dependencies = {
            "evidence_upload": [],
            "evidence_extraction": ["evidence_upload"],
            "business_classification": ["evidence_extraction"],
            "industry_analysis": ["evidence_extraction"],
            "competitor_analysis": ["industry_analysis"],
            "value_proposition": ["competitor_analysis"],
            "target_audience": ["value_proposition"],
            "messaging_framework": ["target_audience"],
            "foundation_creation": ["messaging_framework"],
            "icp_generation": ["foundation_creation"],
            "move_planning": ["icp_generation"],
            "campaign_setup": ["move_planning"],
            "onboarding_complete": ["campaign_setup"],
        }

    async def get_state(self, workspace_id: str) -> Optional[OnboardingState]:
        """Get onboarding state for workspace"""
        try:
            # Try Redis cache first
            cache_key = f"onboarding_state:{workspace_id}"
            cached_state = await self.redis.get(cache_key)

            if cached_state:
                state_data = json.loads(cached_state)
                return self._deserialize_state(state_data)

            # Fallback to database
            db_state = await self._load_from_db(workspace_id)
            if db_state:
                # Cache in Redis
                await self._cache_state(db_state)
                return db_state

            # Create new state
            return await self._create_new_state(workspace_id)

        except Exception as e:
            logger.error(f"Error getting onboarding state: {e}")
            return None

    async def update_step_state(
        self,
        workspace_id: str,
        step_id: str,
        status: StepStatus,
        result_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ) -> bool:
        """Update step state with validation and persistence"""
        try:
            # Get current state
            state = await self.get_state(workspace_id)
            if not state:
                logger.error(f"No state found for workspace {workspace_id}")
                return False

            # Validate step transition
            if not await self._validate_step_transition(state, step_id, status):
                return False

            # Update step
            step_state = state.steps.get(
                step_id, StepState(step_id=step_id, status=StepStatus.NOT_STARTED)
            )
            step_state.status = status

            if status == StepStatus.IN_PROGRESS:
                step_state.started_at = time.time()
                state.current_step = step_id
            elif status == StepStatus.COMPLETED:
                step_state.completed_at = time.time()
                step_state.result_data = result_data
                # Calculate data hash for integrity
                if result_data:
                    step_state.data_hash = hashlib.sha256(
                        json.dumps(result_data, sort_keys=True).encode()
                    ).hexdigest()
            elif status == StepStatus.FAILED:
                step_state.error_message = error_message
                step_state.retry_count += 1

            state.updated_at = time.time()
            state.steps[step_id] = step_state

            # Persist changes
            await self._save_state(state)

            # Cache in Redis
            await self._cache_state(state)

            return True

        except Exception as e:
            logger.error(f"Error updating step state: {e}")
            return False

    async def can_execute_step(
        self, workspace_id: str, step_id: str
    ) -> tuple[bool, str]:
        """Check if step can be executed based on dependencies and state"""
        try:
            state = await self.get_state(workspace_id)
            if not state:
                return False, "No onboarding state found"

            # Check if workspace is locked
            if await self._is_locked(workspace_id):
                return False, "Workspace is locked by another operation"

            # Check dependencies
            dependencies = self.step_dependencies.get(step_id, [])
            for dep_step in dependencies:
                dep_state = state.steps.get(dep_step)
                if not dep_state or dep_state.status != StepStatus.COMPLETED:
                    return False, f"Dependency {dep_step} not completed"

            # Check if step already completed
            current_step_state = state.steps.get(step_id)
            if current_step_state and current_step_state.status == StepStatus.COMPLETED:
                return False, "Step already completed"

            return True, "Step can be executed"

        except Exception as e:
            logger.error(f"Error checking step execution: {e}")
            return False, f"Error: {str(e)}"

    async def acquire_lock(self, workspace_id: str, owner_id: str) -> bool:
        """Acquire workspace lock for exclusive operation"""
        try:
            state = await self.get_state(workspace_id)
            if not state:
                return False

            # Check existing lock
            if state.lock_expires_at and state.lock_expires_at > time.time():
                return False

            # Acquire lock
            state.lock_expires_at = time.time() + self.lock_timeout
            state.lock_owner = owner_id
            state.updated_at = time.time()

            await self._save_state(state)
            await self._cache_state(state)

            return True

        except Exception as e:
            logger.error(f"Error acquiring lock: {e}")
            return False

    async def release_lock(self, workspace_id: str, owner_id: str) -> bool:
        """Release workspace lock"""
        try:
            state = await self.get_state(workspace_id)
            if not state:
                return False

            # Verify lock ownership
            if state.lock_owner != owner_id:
                return False

            # Release lock
            state.lock_expires_at = None
            state.lock_owner = None
            state.updated_at = time.time()

            await self._save_state(state)
            await self._cache_state(state)

            return True

        except Exception as e:
            logger.error(f"Error releasing lock: {e}")
            return False

    async def get_progress_summary(self, workspace_id: str) -> Dict[str, Any]:
        """Get comprehensive progress summary"""
        try:
            state = await self.get_state(workspace_id)
            if not state:
                return {"error": "No state found"}

            total_steps = len(self.step_dependencies)
            completed_steps = len(
                [s for s in state.steps.values() if s.status == StepStatus.COMPLETED]
            )
            failed_steps = len(
                [s for s in state.steps.values() if s.status == StepStatus.FAILED]
            )
            in_progress_steps = len(
                [s for s in state.steps.values() if s.status == StepStatus.IN_PROGRESS]
            )

            # Calculate next available step
            next_step = await self._get_next_available_step(state)

            return {
                "workspace_id": workspace_id,
                "total_steps": total_steps,
                "completed_steps": completed_steps,
                "failed_steps": failed_steps,
                "in_progress_steps": in_progress_steps,
                "progress_percentage": (
                    (completed_steps / total_steps) * 100 if total_steps > 0 else 0
                ),
                "current_step": state.current_step,
                "next_step": next_step,
                "steps": {
                    step_id: asdict(step_state)
                    for step_id, step_state in state.steps.items()
                },
                "created_at": state.created_at,
                "updated_at": state.updated_at,
                "is_locked": state.lock_expires_at
                and state.lock_expires_at > time.time(),
            }

        except Exception as e:
            logger.error(f"Error getting progress summary: {e}")
            return {"error": str(e)}

    async def resume_onboarding(self, workspace_id: str) -> Dict[str, Any]:
        """Resume onboarding from last known state"""
        try:
            state = await self.get_state(workspace_id)
            if not state:
                return {"error": "No onboarding state found"}

            # Find next available step
            next_step = await self._get_next_available_step(state)

            # Get data from completed steps
            step_data = {}
            for step_id, step_state in state.steps.items():
                if step_state.status == StepStatus.COMPLETED and step_state.result_data:
                    step_data[step_id] = step_state.result_data

            return {
                "success": True,
                "next_step": next_step,
                "step_data": step_data,
                "progress": await self.get_progress_summary(workspace_id),
            }

        except Exception as e:
            logger.error(f"Error resuming onboarding: {e}")
            return {"error": str(e)}

    # Private methods

    async def _validate_step_transition(
        self, state: OnboardingState, step_id: str, status: StepStatus
    ) -> bool:
        """Validate step transition rules"""
        current_step_state = state.steps.get(step_id)

        if not current_step_state:
            # New step - can only start with IN_PROGRESS
            return status == StepStatus.IN_PROGRESS

        # Existing step - validate state transitions
        if current_step_state.status == StepStatus.NOT_STARTED:
            return status == StepStatus.IN_PROGRESS
        elif current_step_state.status == StepStatus.IN_PROGRESS:
            return status in [
                StepStatus.COMPLETED,
                StepStatus.FAILED,
                StepStatus.SKIPPED,
            ]
        elif current_step_state.status == StepStatus.FAILED:
            # Can retry failed steps (max 3 retries)
            if status == StepStatus.IN_PROGRESS and current_step_state.retry_count < 3:
                return True
            return False
        else:
            # COMPLETED or SKIPPED - no further transitions
            return False

    async def _is_locked(self, workspace_id: str) -> bool:
        """Check if workspace is locked"""
        state = await self.get_state(workspace_id)
        return state and state.lock_expires_at and state.lock_expires_at > time.time()

    async def _get_next_available_step(self, state: OnboardingState) -> Optional[str]:
        """Find next step that can be executed"""
        for step_id, dependencies in self.step_dependencies.items():
            # Skip if already completed
            step_state = state.steps.get(step_id)
            if step_state and step_state.status == StepStatus.COMPLETED:
                continue

            # Check dependencies
            all_deps_met = True
            for dep_step in dependencies:
                dep_state = state.steps.get(dep_step)
                if not dep_state or dep_state.status != StepStatus.COMPLETED:
                    all_deps_met = False
                    break

            if all_deps_met:
                return step_id

        return None

    async def _create_new_state(self, workspace_id: str) -> OnboardingState:
        """Create new onboarding state"""
        state = OnboardingState(workspace_id=workspace_id)

        # Initialize all steps
        for step_id in self.step_dependencies.keys():
            state.steps[step_id] = StepState(
                step_id=step_id, status=StepStatus.NOT_STARTED
            )

        await self._save_state(state)
        await self._cache_state(state)

        return state

    async def _save_state(self, state: OnboardingState) -> bool:
        """Save state to database"""
        try:
            state_data = self._serialize_state(state)

            result = (
                self.db_client.table("onboarding_states").upsert(state_data).execute()
            )
            return bool(result.data)

        except Exception as e:
            logger.error(f"Error saving state to DB: {e}")
            return False

    async def _load_from_db(self, workspace_id: str) -> Optional[OnboardingState]:
        """Load state from database"""
        try:
            result = (
                self.db_client.table("onboarding_states")
                .select("*")
                .eq("workspace_id", workspace_id)
                .order("updated_at", desc=True)
                .limit(1)
                .execute()
            )

            if result.data:
                return self._deserialize_state(result.data[0])

            return None

        except Exception as e:
            logger.error(f"Error loading state from DB: {e}")
            return None

    async def _cache_state(self, state: OnboardingState) -> bool:
        """Cache state in Redis"""
        try:
            cache_key = f"onboarding_state:{state.workspace_id}"
            state_data = self._serialize_state(state)

            await self.redis.set(
                cache_key, json.dumps(state_data), ex=self.state_cache_ttl
            )
            return True

        except Exception as e:
            logger.error(f"Error caching state: {e}")
            return False

    def _serialize_state(self, state: OnboardingState) -> Dict[str, Any]:
        """Serialize state for storage"""
        return {
            "workspace_id": state.workspace_id,
            "current_step": state.current_step,
            "steps": {
                step_id: asdict(step_state)
                for step_id, step_state in state.steps.items()
            },
            "created_at": state.created_at,
            "updated_at": state.updated_at,
            "lock_expires_at": state.lock_expires_at,
            "lock_owner": state.lock_owner,
        }

    def _deserialize_state(self, data: Dict[str, Any]) -> OnboardingState:
        """Deserialize state from storage"""
        steps = {}
        for step_id, step_data in data.get("steps", {}).items():
            steps[step_id] = StepState(
                step_id=step_data["step_id"],
                status=StepStatus(step_data["status"]),
                started_at=step_data.get("started_at"),
                completed_at=step_data.get("completed_at"),
                error_message=step_data.get("error_message"),
                retry_count=step_data.get("retry_count", 0),
                data_hash=step_data.get("data_hash"),
                result_data=step_data.get("result_data"),
            )

        return OnboardingState(
            workspace_id=data["workspace_id"],
            current_step=data.get("current_step"),
            steps=steps,
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            lock_expires_at=data.get("lock_expires_at"),
            lock_owner=data.get("lock_owner"),
        )
