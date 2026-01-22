"""
Enhanced AgentStateManager for Raptorflow agent system.
Manages agent state persistence, recovery, and synchronization with improved error handling.
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

from backend.agents.config import ModelTier

from ..base import BaseAgent
from ..exceptions import StateError, ValidationError
from ..memory.controller import SimpleMemoryController

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


@dataclass
class AgentState:
    """Represents the state of an agent."""

    agent_id: str
    state_data: Dict[str, Any]
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_id": self.agent_id,
            "state_data": self.state_data,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class AgentStateManager:
    """Enhanced agent state manager with improved error handling, recovery, and synchronization."""

    def __init__(
        self,
        config: StateConfig = None,
        memory_controller: Optional[SimpleMemoryController] = None,
    ):
        self.config = config or StateConfig()
        self.memory_controller = memory_controller

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

        # Enhanced statistics
        self._stats = {
            "states_created": 0,
            "states_updated": 0,
            "states_deleted": 0,
            "snapshots_created": 0,
            "locks_acquired": 0,
            "transitions_recorded": 0,
            "errors_recovered": 0,
            "backup_operations": 0,
            "sync_operations": 0,
        }

        # Error recovery configuration
        self._recovery_config = {
            "max_retries": 3,
            "retry_delay": 1.0,  # seconds
            "corruption_threshold": 5,  # consecutive errors before marking as corrupted
            "auto_backup": True,
            "health_check_interval": 300,  # seconds
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
        """Create a new state with enhanced error handling."""
        max_retries = self._recovery_config["max_retries"]
        retry_delay = self._recovery_config["retry_delay"]

        for attempt in range(max_retries):
            try:
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
                        access_count=0,
                        last_accessed=datetime.now(),
                    )

                    # Store state and metadata
                    self._states[state_id] = initial_data.copy()
                    self._metadata[state_id] = metadata

                    # Create initial snapshot
                    if self.config.backup_enabled:
                        await self._create_snapshot(state_id, "Initial state")

                    # Persist to backend with retry logic
                    await self._persist_state_with_retry(state_id)

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

            except Exception as e:
                logger.error(
                    f"State creation failed (attempt {attempt + 1}/{max_retries}): {e}"
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    # Final attempt failed
                    logger.error(
                        f"State creation failed after {max_retries} attempts: {e}"
                    )
                    raise StateError(
                        f"Failed to create state after {max_retries} attempts: {e}"
                    )

    async def get_state(
        self, state_id: str, include_metadata: bool = False
    ) -> Union[Dict[str, Any], tuple]:
        """Get state data with enhanced error handling."""
        max_retries = self._recovery_config["max_retries"]
        retry_delay = self._recovery_config["retry_delay"]

        for attempt in range(max_retries):
            try:
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

            except Exception as e:
                logger.error(
                    f"State retrieval failed (attempt {attempt + 1}/{max_retries}): {e}"
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    logger.error(
                        f"State retrieval failed after {max_retries} attempts: {e}"
                    )
                    raise StateError(
                        f"Failed to retrieve state after {max_retries} attempts: {e}"
                    )

    async def update_state(
        self,
        state_id: str,
        updates: Dict[str, Any],
        user_id: str,
        description: str = "",
    ) -> bool:
        """Update state data with enhanced error handling."""
        max_retries = self._recovery_config["max_retries"]
        retry_delay = self._recovery_config["retry_delay"]

        for attempt in range(max_retries):
            try:
                async with self._state_lock:
                    # Check if state exists and is not locked
                    if state_id not in self._states:
                        raise StateError(f"State not found: {state_id}")

                    if (
                        state_id in self._locks
                        and not self._locks[state_id].is_expired()
                    ):
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
                        access_count=old_metadata.access_count + 1,
                        last_accessed=datetime.now(),
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

                    # Create snapshot if configured
                    if self.config.backup_enabled and new_metadata.version % 5 == 0:
                        await self._create_snapshot(
                            state_id, f"Version {new_metadata.version}"
                        )

                    # Persist to backend with retry logic
                    await self._persist_state_with_retry(state_id)

                    # Update statistics
                    self._stats["states_updated"] += 1
                    self._stats["transitions_recorded"] += 1

                    # Emit event
                    await self._emit_event(
                        "state_updated",
                        {
                            "state_id": state_id,
                            "state_type": new_metadata.state_type.value,
                            "owner_id": new_metadata.owner_id,
                            "workspace_id": new_metadata.workspace_id,
                            "version": new_metadata.version,
                            "changes": updates,
                            "user_id": user_id,
                            "description": description,
                        },
                    )

                    logger.info(
                        f"Updated state: {state_id} to version {new_metadata.version}"
                    )
                    return True

            except Exception as e:
                logger.error(
                    f"State update failed (attempt {attempt + 1}/{max_retries}): {e}"
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    logger.error(
                        f"State update failed after {max_retries} attempts: {e}"
                    )
                    raise StateError(
                        f"Failed to update state after {max_retries} attempts: {e}"
                    )

    async def delete_state(self, state_id: str, user_id: str) -> bool:
        """Delete state with enhanced error handling."""
        max_retries = self._recovery_config["max_retries"]
        retry_delay = self._recovery_config["retry_delay"]

        for attempt in range(max_retries):
            try:
                async with self._state_lock:
                    # Check if state exists
                    if state_id not in self._states:
                        raise StateError(f"State not found: {state_id}")

                    # Create final snapshot
                    if self.config.backup_enabled:
                        await self._create_snapshot(state_id, "Before deletion")

                    # Remove state
                    del self._states[state_id]
                    if state_id in self._metadata:
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
                        "state_deleted",
                        {
                            "state_id": state_id,
                            "state_type": (
                                self._metadata[state_id].state_type.value
                                if state_id in self._metadata
                                else StateType.AGENT_STATE
                            ),
                            "owner_id": (
                                self._metadata[state_id].owner_id
                                if state_id in self._metadata
                                else ""
                            ),
                            "workspace_id": (
                                self._metadata[state_id].workspace_id
                                if state_id in self._metadata
                                else ""
                            ),
                            "user_id": user_id,
                        },
                    )

                    logger.info(f"Deleted state: {state_id}")
                    return True

            except Exception as e:
                logger.error(
                    f"State deletion failed (attempt {attempt + 1}/{max_retries}): {e}"
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    logger.error(
                        f"State deletion failed after {max_retries} attempts: {e}"
                    )
                    raise StateError(
                        f"Failed to delete state after {max_retries} attempts: {e}"
                    )

    async def _persist_state_with_retry(self, state_id: str):
        """Persist state with retry logic."""
        max_retries = self._recovery_config["max_retries"]
        retry_delay = self._recovery_config["retry_delay"]

        for attempt in range(max_retries):
            try:
                await self._persist_state(state_id)
                return  # Success

            except Exception as e:
                logger.error(
                    f"State persistence failed (attempt {attempt + 1}/{max_retries}): {e}"
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    # Mark state as potentially corrupted
                    if state_id in self._states:
                        metadata = self._metadata[state_id]
                        metadata.status = StateStatus.CORRUPTED
                        self._metadata[state_id] = metadata
                        self._stats["errors_recovered"] += 1

                    logger.error(
                        f"State persistence failed after {max_retries} attempts: {e}"
                    )
                    # Continue to next operation
                    return

    async def _expire_state(self, state_id: str):
        """Expire a state."""
        if state_id in self._states:
            metadata = self._metadata[state_id]
            metadata.status = StateStatus.INACTIVE
            metadata.expires_at = datetime.now()

            # Update access statistics
            metadata.last_accessed = datetime.now()

            logger.info(f"Expired state: {state_id}")

    async def _persist_state(self, state_id: str):
        """Persist state to backend with memory controller integration."""
        try:
            # Get state data
            state_data = self._states[state_id]
            metadata = self._metadata[state_id]

            # Store in memory controller
            if self.memory_controller:
                memory_key = f"state:{state_id}"
                await self.memory_controller.store_memory(
                    memory_key, json.dumps(state_data), memory_type="vector"
                )
                await self.memory_controller.store_memory(
                    f"metadata:{state_id}",
                    json.dumps(asdict(metadata)),
                    memory_type="vector",
                )

            # Persist to backend
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

            # Update statistics
            self._stats["backup_operations"] += 1

        except Exception as e:
            logger.error(f"State persistence failed: {e}")
            # Mark state as potentially corrupted if this is a critical state
            if state_id in self._states:
                metadata = self._metadata[state_id]
                metadata.status = StateStatus.CORRUPTED
                self._metadata[state_id] = metadata
                self._stats["errors_recovered"] += 1
            raise StateError(f"State persistence failed: {e}")

    async def _create_snapshot(self, state_id: str, description: str) -> str:
        """Create state snapshot."""
        snapshot_id = str(uuid.uuid4())

        snapshot = StateSnapshot(
            snapshot_id=snapshot_id,
            state_id=state_id,
            data=self._states[state_id].copy(),
            metadata=self._metadata[state_id],
            created_at=datetime.now(),
            description=description,
        )

        self._snapshots[state_id].append(snapshot)

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
