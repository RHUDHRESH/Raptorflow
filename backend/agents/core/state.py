"""
AgentStateManager for Raptorflow agent system.
Manages agent state persistence, recovery, and synchronization.
"""

import asyncio
import hashlib
import json
import logging
import pickle
import threading
import uuid
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from ..base import BaseAgent
from ..config import ModelTier
from ..exceptions import StateError, ValidationError
from ..state import AgentState

logger = logging.getLogger(__name__)


class StateType(Enum):
    """State types."""

    AGENT_STATE = "agent_state"
    WORKFLOW_STATE = "workflow_state"
    SESSION_STATE = "session_state"
    SYSTEM_STATE = "system_state"
    CACHE_STATE = "cache_state"


class StateStatus(Enum):
    """State status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"
    CORRUPTED = "corrupted"
    ARCHIVED = "archived"


class StorageBackend(Enum):
    """Storage backends."""

    MEMORY = "memory"
    FILE = "file"
    DATABASE = "database"
    REDIS = "redis"


@dataclass
class StateMetadata:
    """State metadata."""

    state_id: str
    state_type: StateType
    owner_id: str
    workspace_id: str
    created_at: datetime
    updated_at: datetime
    version: int
    checksum: str
    size_bytes: int
    status: StateStatus
    tags: List[str] = field(default_factory=list)
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None


@dataclass
class StateSnapshot:
    """State snapshot."""

    snapshot_id: str
    state_id: str
    data: Dict[str, Any]
    metadata: StateMetadata
    created_at: datetime
    description: str = ""


@dataclass
class StateTransition:
    """State transition record."""

    transition_id: str
    state_id: str
    from_version: int
    to_version: int
    changes: Dict[str, Any]
    timestamp: datetime
    user_id: str
    description: str = ""


@dataclass
class StateConfig:
    """State manager configuration."""

    default_backend: StorageBackend = StorageBackend.MEMORY
    backup_enabled: bool = True
    backup_interval_seconds: int = 300
    max_snapshots_per_state: int = 10
    state_ttl_hours: int = 24
    compression_enabled: bool = True
    encryption_enabled: bool = False
    sync_enabled: bool = True
    lock_timeout_seconds: int = 30
    max_state_size_mb: int = 100


class StateLock:
    """State lock for concurrent access control."""

    def __init__(self, state_id: str, owner_id: str, timeout_seconds: int = 30):
        self.state_id = state_id
        self.owner_id = owner_id
        self.created_at = datetime.now()
        self.expires_at = datetime.now() + timedelta(seconds=timeout_seconds)
        self.lock_id = str(uuid.uuid4())

    def is_expired(self) -> bool:
        """Check if lock is expired."""
        return datetime.now() > self.expires_at

    def extend(self, seconds: int):
        """Extend lock duration."""
        self.expires_at = datetime.now() + timedelta(seconds=seconds)


class AgentStateManager:
    """Manages agent state with persistence, recovery, and synchronization."""

    def __init__(self, config: StateConfig = None):
        self.config = config or StateConfig()

        # State storage
        self._states: Dict[str, Dict[str, Any]] = {}
        self._metadata: Dict[str, StateMetadata] = {}
        self._snapshots: Dict[str, List[StateSnapshot]] = defaultdict(list)
        self._transitions: Dict[str, List[StateTransition]] = defaultdict(list)
        self._locks: Dict[str, StateLock] = {}

        # Storage backends
        self._backends: Dict[StorageBackend, Any] = {}
        self._initialize_backends()

        # Background tasks
        self._background_tasks: Set[asyncio.Task] = set()
        self._running = False

        # Event handlers
        self._event_handlers: Dict[str, List[Callable]] = defaultdict(list)

        # Locks for thread safety
        self._state_lock = asyncio.Lock()
        self._lock_lock = threading.Lock()

        # Statistics
        self._stats = {
            "states_created": 0,
            "states_updated": 0,
            "states_deleted": 0,
            "snapshots_created": 0,
            "locks_acquired": 0,
            "transitions_recorded": 0,
        }

        # Start background tasks
        self._start_background_tasks()

    def _initialize_backends(self):
        """Initialize storage backends."""
        # Memory backend (always available)
        self._backends[StorageBackend.MEMORY] = {}

        # File backend
        if self.config.default_backend in [
            StorageBackend.FILE,
            StorageBackend.DATABASE,
        ]:
            self._initialize_file_backend()

        # Database backend (placeholder)
        if self.config.default_backend == StorageBackend.DATABASE:
            self._initialize_database_backend()

        # Redis backend (placeholder)
        if self.config.default_backend == StorageBackend.REDIS:
            self._initialize_redis_backend()

    def _initialize_file_backend(self):
        """Initialize file-based storage."""
        storage_dir = Path("state_storage")
        storage_dir.mkdir(exist_ok=True)

        self._backends[StorageBackend.FILE] = {
            "storage_dir": storage_dir,
            "states_file": storage_dir / "states.json",
            "metadata_file": storage_dir / "metadata.json",
            "snapshots_dir": storage_dir / "snapshots",
        }

        # Create snapshots directory
        self._backends[StorageBackend.FILE]["snapshots_dir"].mkdir(exist_ok=True)

    def _initialize_database_backend(self):
        """Initialize database storage (placeholder)."""
        self._backends[StorageBackend.DATABASE] = {
            "connection": None,  # Would be actual DB connection
            "initialized": False,
        }

    def _initialize_redis_backend(self):
        """Initialize Redis storage (placeholder)."""
        self._backends[StorageBackend.REDIS] = {
            "connection": None,  # Would be actual Redis connection
            "initialized": False,
        }

    async def create_state(
        self,
        state_type: StateType,
        owner_id: str,
        workspace_id: str,
        initial_data: Dict[str, Any],
        tags: List[str] = None,
        ttl_hours: int = None,
    ) -> str:
        """Create a new state."""
        async with self._state_lock:
            # Generate state ID
            state_id = str(uuid.uuid4())

            # Create metadata
            metadata = StateMetadata(
                state_id=state_id,
                state_type=state_type,
                owner_id=owner_id,
                workspace_id=workspace_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                version=1,
                checksum=self._calculate_checksum(initial_data),
                size_bytes=len(json.dumps(initial_data)),
                status=StateStatus.ACTIVE,
                tags=tags or [],
                expires_at=datetime.now()
                + timedelta(hours=ttl_hours or self.config.state_ttl_hours),
            )

            # Store state and metadata
            self._states[state_id] = initial_data.copy()
            self._metadata[state_id] = metadata

            # Create initial snapshot
            if self.config.backup_enabled:
                await self._create_snapshot(state_id, "Initial state")

            # Persist to backend
            await self._persist_state(state_id)

            # Update statistics
            self._stats["states_created"] += 1

            # Emit event
            await self._emit_event(
                "state_created",
                {
                    "state_id": state_id,
                    "state_type": state_type.value,
                    "owner_id": owner_id,
                    "workspace_id": workspace_id,
                },
            )

            logger.info(f"Created state: {state_id}")

            return state_id

    async def get_state(
        self, state_id: str, include_metadata: bool = False
    ) -> Union[Dict[str, Any], tuple]:
        """Get state data."""
        async with self._state_lock:
            # Check if state exists
            if state_id not in self._states:
                raise StateError(f"State not found: {state_id}")

            # Check if state is expired
            metadata = self._metadata[state_id]
            if metadata.expires_at and datetime.now() > metadata.expires_at:
                await self._expire_state(state_id)
                raise StateError(f"State expired: {state_id}")

            # Update access statistics
            metadata.access_count += 1
            metadata.last_accessed = datetime.now()

            # Return data
            if include_metadata:
                return self._states[state_id].copy(), metadata
            else:
                return self._states[state_id].copy()

    async def update_state(
        self,
        state_id: str,
        updates: Dict[str, Any],
        user_id: str,
        description: str = "",
    ) -> bool:
        """Update state data."""
        async with self._state_lock:
            # Check if state exists and is not locked
            if state_id not in self._states:
                raise StateError(f"State not found: {state_id}")

            if self._metadata[state_id].status == StateStatus.LOCKED:
                raise StateError(f"State is locked: {state_id}")

            # Record transition
            old_data = self._states[state_id].copy()
            old_metadata = self._metadata[state_id]

            # Apply updates
            new_data = old_data.copy()
            new_data.update(updates)

            # Update metadata
            new_metadata = StateMetadata(
                state_id=state_id,
                state_type=old_metadata.state_type,
                owner_id=old_metadata.owner_id,
                workspace_id=old_metadata.workspace_id,
                created_at=old_metadata.created_at,
                updated_at=datetime.now(),
                version=old_metadata.version + 1,
                checksum=self._calculate_checksum(new_data),
                size_bytes=len(json.dumps(new_data)),
                status=old_metadata.status,
                tags=old_metadata.tags.copy(),
                expires_at=old_metadata.expires_at,
                access_count=old_metadata.access_count,
                last_accessed=old_metadata.last_accessed,
            )

            # Store updated state
            self._states[state_id] = new_data
            self._metadata[state_id] = new_metadata

            # Record transition
            transition = StateTransition(
                transition_id=str(uuid.uuid4()),
                state_id=state_id,
                from_version=old_metadata.version,
                to_version=new_metadata.version,
                changes=updates,
                timestamp=datetime.now(),
                user_id=user_id,
                description=description,
            )
            self._transitions[state_id].append(transition)

            # Create snapshot
            if (
                self.config.backup_enabled and new_metadata.version % 5 == 0
            ):  # Every 5 versions
                await self._create_snapshot(state_id, f"Version {new_metadata.version}")

            # Persist to backend
            await self._persist_state(state_id)

            # Update statistics
            self._stats["states_updated"] += 1
            self._stats["transitions_recorded"] += 1

            # Emit event
            await self._emit_event(
                "state_updated",
                {
                    "state_id": state_id,
                    "version": new_metadata.version,
                    "user_id": user_id,
                    "changes": updates,
                },
            )

            logger.info(f"Updated state: {state_id} to version {new_metadata.version}")

            return True

    async def delete_state(self, state_id: str, user_id: str) -> bool:
        """Delete state."""
        async with self._state_lock:
            # Check if state exists
            if state_id not in self._states:
                raise StateError(f"State not found: {state_id}")

            # Create final snapshot
            if self.config.backup_enabled:
                await self._create_snapshot(state_id, "Before deletion")

            # Remove state
            del self._states[state_id]
            del self._metadata[state_id]

            # Clean up snapshots and transitions
            if state_id in self._snapshots:
                del self._snapshots[state_id]
            if state_id in self._transitions:
                del self._transitions[state_id]

            # Remove from backend
            await self._remove_from_backend(state_id)

            # Update statistics
            self._stats["states_deleted"] += 1

            # Emit event
            await self._emit_event(
                "state_deleted", {"state_id": state_id, "user_id": user_id}
            )

            logger.info(f"Deleted state: {state_id}")

            return True

    async def lock_state(
        self, state_id: str, owner_id: str, timeout_seconds: int = None
    ) -> str:
        """Lock state for exclusive access."""
        with self._lock_lock:
            # Check if state exists
            if state_id not in self._states:
                raise StateError(f"State not found: {state_id}")

            # Check if already locked
            if state_id in self._locks and not self._locks[state_id].is_expired():
                existing_lock = self._locks[state_id]
                raise StateError(f"State already locked by {existing_lock.owner_id}")

            # Create lock
            timeout = timeout_seconds or self.config.lock_timeout_seconds
            lock = StateLock(state_id, owner_id, timeout)
            self._locks[state_id] = lock

            # Update metadata
            self._metadata[state_id].status = StateStatus.LOCKED

            # Update statistics
            self._stats["locks_acquired"] += 1

            logger.info(f"Locked state: {state_id} by {owner_id}")

            return lock.lock_id

    async def unlock_state(self, state_id: str, lock_id: str, owner_id: str) -> bool:
        """Unlock state."""
        with self._lock_lock:
            # Check if lock exists
            if state_id not in self._locks:
                raise StateError(f"No lock found for state: {state_id}")

            lock = self._locks[state_id]

            # Verify lock ownership
            if lock.lock_id != lock_id or lock.owner_id != owner_id:
                raise StateError(f"Invalid lock credentials for state: {state_id}")

            # Remove lock
            del self._locks[state_id]

            # Update metadata
            self._metadata[state_id].status = StateStatus.ACTIVE

            logger.info(f"Unlocked state: {state_id} by {owner_id}")

            return True

    async def create_snapshot(self, state_id: str, description: str = "") -> str:
        """Create manual snapshot."""
        return await self._create_snapshot(state_id, description)

    async def restore_snapshot(
        self, state_id: str, snapshot_id: str, user_id: str
    ) -> bool:
        """Restore state from snapshot."""
        async with self._state_lock:
            # Check if state exists
            if state_id not in self._states:
                raise StateError(f"State not found: {state_id}")

            # Get snapshot
            snapshots = self._snapshots[state_id]
            target_snapshot = None

            for snapshot in snapshots:
                if snapshot.snapshot_id == snapshot_id:
                    target_snapshot = snapshot
                    break

            if not target_snapshot:
                raise StateError(f"Snapshot not found: {snapshot_id}")

            # Restore state
            old_data = self._states[state_id].copy()
            self._states[state_id] = target_snapshot.data.copy()

            # Update metadata
            old_metadata = self._metadata[state_id]
            self._metadata[state_id] = StateMetadata(
                state_id=state_id,
                state_type=old_metadata.state_type,
                owner_id=old_metadata.owner_id,
                workspace_id=old_metadata.workspace_id,
                created_at=old_metadata.created_at,
                updated_at=datetime.now(),
                version=old_metadata.version + 1,
                checksum=self._calculate_checksum(target_snapshot.data),
                size_bytes=len(json.dumps(target_snapshot.data)),
                status=old_metadata.status,
                tags=old_metadata.tags.copy(),
                expires_at=old_metadata.expires_at,
                access_count=old_metadata.access_count,
                last_accessed=datetime.now(),
            )

            # Record transition
            transition = StateTransition(
                transition_id=str(uuid.uuid4()),
                state_id=state_id,
                from_version=old_metadata.version,
                to_version=self._metadata[state_id].version,
                changes={"restored_from": snapshot_id},
                timestamp=datetime.now(),
                user_id=user_id,
                description=f"Restored from snapshot: {description}",
            )
            self._transitions[state_id].append(transition)

            # Persist to backend
            await self._persist_state(state_id)

            logger.info(f"Restored state {state_id} from snapshot {snapshot_id}")

            return True

    async def list_states(
        self,
        state_type: Optional[StateType] = None,
        owner_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        status: Optional[StateStatus] = None,
    ) -> List[StateMetadata]:
        """List states with optional filtering."""
        async with self._state_lock:
            states = []

            for state_id, metadata in self._metadata.items():
                # Apply filters
                if state_type and metadata.state_type != state_type:
                    continue

                if owner_id and metadata.owner_id != owner_id:
                    continue

                if workspace_id and metadata.workspace_id != workspace_id:
                    continue

                if tags and not any(tag in metadata.tags for tag in tags):
                    continue

                if status and metadata.status != status:
                    continue

                # Check if state is expired
                if metadata.expires_at and datetime.now() > metadata.expires_at:
                    continue

                states.append(metadata)

            # Sort by updated_at (most recent first)
            states.sort(key=lambda m: m.updated_at, reverse=True)

            return states

    async def get_state_history(
        self, state_id: str, limit: int = 50
    ) -> List[StateTransition]:
        """Get state transition history."""
        transitions = self._transitions.get(state_id, [])

        # Sort by timestamp (most recent first)
        transitions.sort(key=lambda t: t.timestamp, reverse=True)

        return transitions[:limit]

    async def get_snapshots(self, state_id: str) -> List[StateSnapshot]:
        """Get state snapshots."""
        return self._snapshots.get(state_id, [])

    async def cleanup_expired_states(self) -> int:
        """Clean up expired states."""
        async with self._state_lock:
            expired_states = []

            for state_id, metadata in self._metadata.items():
                if metadata.expires_at and datetime.now() > metadata.expires_at:
                    expired_states.append(state_id)

            for state_id in expired_states:
                await self._expire_state(state_id)

            logger.info(f"Cleaned up {len(expired_states)} expired states")

            return len(expired_states)

    async def _expire_state(self, state_id: str):
        """Expire a state."""
        # Create final snapshot
        if self.config.backup_enabled:
            await self._create_snapshot(state_id, "State expired")

        # Update status
        self._metadata[state_id].status = StateStatus.INACTIVE

        # Remove from active storage but keep metadata
        if state_id in self._states:
            del self._states[state_id]

    async def _create_snapshot(self, state_id: str, description: str) -> str:
        """Create state snapshot."""
        if state_id not in self._states:
            raise StateError(f"State not found: {state_id}")

        snapshot_id = str(uuid.uuid4())

        snapshot = StateSnapshot(
            snapshot_id=snapshot_id,
            state_id=state_id,
            data=self._states[state_id].copy(),
            metadata=self._metadata[state_id],
            created_at=datetime.now(),
            description=description,
        )

        # Add to snapshots
        self._snapshots[state_id].append(snapshot)

        # Limit snapshots per state
        if len(self._snapshots[state_id]) > self.config.max_snapshots_per_state:
            self._snapshots[state_id] = self._snapshots[state_id][
                -self.config.max_snapshots_per_state :
            ]

        # Persist snapshot
        await self._persist_snapshot(snapshot)

        # Update statistics
        self._stats["snapshots_created"] += 1

        return snapshot_id

    async def _persist_state(self, state_id: str):
        """Persist state to backend."""
        backend = self._backends[self.config.default_backend]

        if self.config.default_backend == StorageBackend.MEMORY:
            # Already in memory
            pass
        elif self.config.default_backend == StorageBackend.FILE:
            await self._persist_to_file(state_id)
        elif self.config.default_backend == StorageBackend.DATABASE:
            await self._persist_to_database(state_id)
        elif self.config.default_backend == StorageBackend.REDIS:
            await self._persist_to_redis(state_id)

    async def _persist_to_file(self, state_id: str):
        """Persist state to file."""
        backend = self._backends[StorageBackend.FILE]

        # Save states
        states_file = backend["states_file"]
        with open(states_file, "w") as f:
            json.dump(self._states, f, indent=2, default=str)

        # Save metadata
        metadata_file = backend["metadata_file"]
        metadata_dict = {k: asdict(v) for k, v in self._metadata.items()}
        with open(metadata_file, "w") as f:
            json.dump(metadata_dict, f, indent=2, default=str)

    async def _persist_to_database(self, state_id: str):
        """Persist state to database (placeholder)."""
        # In production, would use actual database operations
        pass

    async def _persist_to_redis(self, state_id: str):
        """Persist state to Redis (placeholder)."""
        # In production, would use actual Redis operations
        pass

    async def _persist_snapshot(self, snapshot: StateSnapshot):
        """Persist snapshot to backend."""
        backend = self._backends[self.config.default_backend]

        if self.config.default_backend == StorageBackend.FILE:
            snapshots_dir = backend["snapshots_dir"]
            snapshot_file = snapshots_dir / f"{snapshot.snapshot_id}.json"

            snapshot_data = {
                "snapshot_id": snapshot.snapshot_id,
                "state_id": snapshot.state_id,
                "data": snapshot.data,
                "metadata": asdict(snapshot.metadata),
                "created_at": snapshot.created_at.isoformat(),
                "description": snapshot.description,
            }

            with open(snapshot_file, "w") as f:
                json.dump(snapshot_data, f, indent=2, default=str)

    async def _remove_from_backend(self, state_id: str):
        """Remove state from backend."""
        backend = self._backends[self.config.default_backend]

        if self.config.default_backend == StorageBackend.FILE:
            # Remove from files
            if state_id in self._states:
                del self._states[state_id]
            if state_id in self._metadata:
                del self._metadata[state_id]

            # Remove snapshots
            snapshots_dir = backend["snapshots_dir"]
            for snapshot in self._snapshots.get(state_id, []):
                snapshot_file = snapshots_dir / f"{snapshot.snapshot_id}.json"
                if snapshot_file.exists():
                    snapshot_file.unlink()

    def _calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calculate checksum of state data."""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()

    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit state management event."""
        event_data = {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            **data,
        }

        # Call event handlers
        for handler in self._event_handlers[event_type]:
            try:
                await handler(event_data)
            except Exception as e:
                logger.error(f"Event handler failed: {e}")

    def add_event_handler(self, event_type: str, handler: Callable):
        """Add event handler."""
        self._event_handlers[event_type].append(handler)

    def _start_background_tasks(self):
        """Start background tasks."""
        self._running = True

        # Cleanup task
        self._background_tasks.add(asyncio.create_task(self._cleanup_loop()))

        # Backup task
        if self.config.backup_enabled:
            self._background_tasks.add(asyncio.create_task(self._backup_loop()))

    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while self._running:
            try:
                # Clean up expired states
                await self.cleanup_expired_states()

                # Clean up expired locks
                with self._lock_lock:
                    expired_locks = []
                    for state_id, lock in self._locks.items():
                        if lock.is_expired():
                            expired_locks.append(state_id)

                    for state_id in expired_locks:
                        del self._locks[state_id]
                        if state_id in self._metadata:
                            self._metadata[state_id].status = StateStatus.ACTIVE

                # Sleep for 1 hour
                await asyncio.sleep(3600)

            except Exception as e:
                logger.error(f"Cleanup loop failed: {e}")
                await asyncio.sleep(300)  # Retry after 5 minutes

    async def _backup_loop(self):
        """Background backup loop."""
        while self._running:
            try:
                # Persist all states to backend
                async with self._state_lock:
                    for state_id in list(self._states.keys()):
                        await self._persist_state(state_id)

                # Sleep for backup interval
                await asyncio.sleep(self.config.backup_interval_seconds)

            except Exception as e:
                logger.error(f"Backup loop failed: {e}")
                await asyncio.sleep(60)  # Retry after 1 minute

    async def get_statistics(self) -> Dict[str, Any]:
        """Get state manager statistics."""
        async with self._state_lock:
            return {
                "total_states": len(self._states),
                "active_states": len(
                    [
                        m
                        for m in self._metadata.values()
                        if m.status == StateStatus.ACTIVE
                    ]
                ),
                "locked_states": len(
                    [
                        m
                        for m in self._metadata.values()
                        if m.status == StateStatus.LOCKED
                    ]
                ),
                "total_snapshots": sum(
                    len(snapshots) for snapshots in self._snapshots.values()
                ),
                "total_transitions": sum(
                    len(transitions) for transitions in self._transitions.values()
                ),
                "active_locks": len(self._locks),
                "statistics": self._stats.copy(),
                "backend": self.config.default_backend.value,
                "backup_enabled": self.config.backup_enabled,
            }

    async def stop(self):
        """Stop state manager."""
        self._running = False

        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self._background_tasks, return_exceptions=True)

        self._background_tasks.clear()

        logger.info("State manager stopped")
