"""
Raptorflow State Management
==========================

Comprehensive state management system for the Raptorflow AI agent system.
Supports distributed state, persistence, and real-time synchronization.

Features:
- Distributed state management with Redis
- State persistence and recovery
- Real-time state synchronization
- State versioning and history
- State validation and schema enforcement
- State conflict resolution
- Performance monitoring and metrics
"""

import asyncio
import hashlib
import json
import pickle
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, Generic, List, Optional, Set, TypeVar, Union

# External imports
try:
    import redis.asyncio as redis_client
except ImportError:
    # Fallback for older redis versions
    import redis
    redis_client = redis
import structlog
from pydantic import BaseModel, ValidationError

# Local imports
from .config import settings

logger = structlog.get_logger(__name__)

T = TypeVar("T")


class StateType(str, Enum):
    """State types."""

    AGENT = "agent"
    WORKFLOW = "workflow"
    SESSION = "session"
    SYSTEM = "system"
    USER = "user"
    CACHE = "cache"
    TEMP = "temp"


class StateStatus(str, Enum):
    """State status values."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ERROR = "error"
    ARCHIVED = "archived"


class StateOperation(str, Enum):
    """State operations."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    MERGE = "merge"
    PATCH = "patch"
    REPLACE = "replace"


@dataclass
class StateMetadata:
    """State metadata."""

    id: str
    type: StateType
    status: StateStatus
    created_at: datetime
    updated_at: datetime
    version: int = 1
    checksum: str = ""
    size: int = 0
    ttl: Optional[int] = None
    tags: Set[str] = field(default_factory=set)
    owner: Optional[str] = None
    workspace: Optional[str] = None
    parent_id: Optional[str] = None
    children_ids: Set[str] = field(default_factory=set)
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StateSnapshot:
    """State snapshot for versioning."""

    id: str
    state_id: str
    version: int
    data: Dict[str, Any]
    metadata: StateMetadata
    created_at: datetime
    operation: StateOperation
    checksum: str
    size: int
    compressed: bool = False


@dataclass
class StateTransition:
    """State transition record."""

    id: str
    state_id: str
    from_version: int
    to_version: int
    operation: StateOperation
    changes: Dict[str, Any]
    applied_at: datetime
    applied_by: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class StateSchema(BaseModel):
    """State schema for validation."""

    type: str
    version: str
    required_fields: List[str] = []
    optional_fields: List[str] = []
    field_types: Dict[str, str] = {}
    constraints: Dict[str, Any] = {}
    indexes: List[str] = []


class StateValidator:
    """State validation utility."""

    def __init__(self):
        self.schemas: Dict[str, StateSchema] = {}

    def register_schema(self, schema: StateSchema):
        """Register a state schema."""
        self.schemas[schema.type] = schema

    def validate(self, state_type: str, data: Dict[str, Any]) -> bool:
        """Validate state data against schema."""
        if state_type not in self.schemas:
            return True  # No schema validation required

        schema = self.schemas[state_type]

        try:
            # Check required fields
            for field in schema.required_fields:
                if field not in data:
                    raise ValueError(f"Required field missing: {field}")

            # Check field types
            for field, field_type in schema.field_types.items():
                if field in data:
                    if not self._check_type(data[field], field_type):
                        raise ValueError(
                            f"Invalid type for field {field}: expected {field_type}"
                        )

            # Check constraints
            for field, constraint in schema.constraints.items():
                if field in data:
                    if not self._check_constraint(data[field], constraint):
                        raise ValueError(
                            f"Constraint violation for field {field}: {constraint}"
                        )

            return True

        except Exception as e:
            logger.error("State validation failed", state_type=state_type, error=str(e))
            return False

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type."""
        type_map = {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
            "datetime": datetime,
        }

        expected_python_type = type_map.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)

        return True

    def _check_constraint(self, value: Any, constraint: Dict[str, Any]) -> bool:
        """Check if value meets constraint."""
        if "min" in constraint and value < constraint["min"]:
            return False
        if "max" in constraint and value > constraint["max"]:
            return False
        if "min_length" in constraint and len(value) < constraint["min_length"]:
            return False
        if "max_length" in constraint and len(value) > constraint["max_length"]:
            return False
        if "pattern" in constraint and not re.match(constraint["pattern"], str(value)):
            return False
        if "enum" in constraint and value not in constraint["enum"]:
            return False

        return True


class StateSerializer:
    """State serialization utility."""

    @staticmethod
    def serialize(data: Dict[str, Any]) -> bytes:
        """Serialize state data."""
        try:
            return pickle.dumps(data)
        except Exception as e:
            logger.error("State serialization failed", error=str(e))
            raise

    @staticmethod
    def deserialize(data: bytes) -> Dict[str, Any]:
        """Deserialize state data."""
        try:
            return pickle.loads(data)
        except Exception as e:
            logger.error("State deserialization failed", error=str(e))
            raise

    @staticmethod
    def serialize_json(data: Dict[str, Any]) -> str:
        """Serialize state data to JSON."""
        try:
            return json.dumps(data, default=str)
        except Exception as e:
            logger.error("State JSON serialization failed", error=str(e))
            raise

    @staticmethod
    def deserialize_json(data: str) -> Dict[str, Any]:
        """Deserialize state data from JSON."""
        try:
            return json.loads(data)
        except Exception as e:
            logger.error("State JSON deserialization failed", error=str(e))
            raise


class StateStorage(ABC):
    """Abstract base class for state storage."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get state by key."""
        pass

    @abstractmethod
    async def set(
        self, key: str, value: Dict[str, Any], ttl: Optional[int] = None
    ) -> bool:
        """Set state with optional TTL."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete state by key."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if state exists."""
        pass

    @abstractmethod
    async def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern."""
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """Clear all states."""
        pass


class RedisStateStorage(StateStorage):
    """Redis-based state storage."""

    def __init__(self, redis_url: str = None):
        import os

        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_client: Optional[redis_client.Redis] = None
        self._connected = False

    async def connect(self):
        """Connect to Redis."""
        if not self._connected:
            try:
                self.redis_client = redis_client.from_url(self.redis_url)
                await self.redis_client.ping()
                self._connected = True
                logger.info("Connected to Redis state storage")
            except Exception as e:
                logger.error("Failed to connect to Redis", error=str(e))
                raise

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            self._connected = False

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get state by key."""
        await self.connect()
        try:
            data = await self.redis_client.get(key)
            if data:
                return StateSerializer.deserialize(data)
            return None
        except Exception as e:
            logger.error("Failed to get state", key=key, error=str(e))
            return None

    async def set(
        self, key: str, value: Dict[str, Any], ttl: Optional[int] = None
    ) -> bool:
        """Set state with optional TTL."""
        await self.connect()
        try:
            data = StateSerializer.serialize(value)
            if ttl:
                return await self.redis_client.setex(key, ttl, data)
            else:
                return await self.redis_client.set(key, data)
        except Exception as e:
            logger.error("Failed to set state", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete state by key."""
        await self.connect()
        try:
            return await self.redis_client.delete(key) > 0
        except Exception as e:
            logger.error("Failed to delete state", key=key, error=str(e))
            return False

    async def exists(self, key: str) -> bool:
        """Check if state exists."""
        await self.connect()
        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error("Failed to check state existence", key=key, error=str(e))
            return False

    async def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern."""
        await self.connect()
        try:
            keys = await self.redis_client.keys(pattern)
            return [key.decode() for key in keys]
        except Exception as e:
            logger.error("Failed to get keys", pattern=pattern, error=str(e))
            return []

    async def clear(self) -> bool:
        """Clear all states."""
        await self.connect()
        try:
            return await self.redis_client.flushdb()
        except Exception as e:
            logger.error("Failed to clear states", error=str(e))
            return False


class MemoryStateStorage(StateStorage):
    """In-memory state storage for testing and development."""

    def __init__(self):
        self._storage: Dict[str, Dict[str, Any]] = {}
        self._ttl: Dict[str, datetime] = {}

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get state by key."""
        if key in self._ttl and datetime.now() > self._ttl[key]:
            await self.delete(key)
            return None

        return self._storage.get(key)

    async def set(
        self, key: str, value: Dict[str, Any], ttl: Optional[int] = None
    ) -> bool:
        """Set state with optional TTL."""
        self._storage[key] = value
        if ttl:
            self._ttl[key] = datetime.now() + timedelta(seconds=ttl)
        return True

    async def delete(self, key: str) -> bool:
        """Delete state by key."""
        self._storage.pop(key, None)
        self._ttl.pop(key, None)
        return True

    async def exists(self, key: str) -> bool:
        """Check if state exists."""
        if key in self._ttl and datetime.now() > self._ttl[key]:
            await self.delete(key)
            return False

        return key in self._storage

    async def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern."""
        import fnmatch

        return [key for key in self._storage.keys() if fnmatch.fnmatch(key, pattern)]

    async def clear(self) -> bool:
        """Clear all states."""
        self._storage.clear()
        self._ttl.clear()
        return True


class StateManager:
    """Main state manager with distributed storage and synchronization."""

    def __init__(self, storage: Optional[StateStorage] = None):
        self.storage = storage or RedisStateStorage()
        self.validator = StateValidator()
        self.serializer = StateSerializer()
        self.snapshots: Dict[str, List[StateSnapshot]] = {}
        self.transitions: Dict[str, List[StateTransition]] = {}
        self.locks: Dict[str, asyncio.Lock] = {}
        self._metrics = {
            "gets": 0,
            "sets": 0,
            "deletes": 0,
            "hits": 0,
            "misses": 0,
            "errors": 0,
        }

    def _get_lock(self, key: str) -> asyncio.Lock:
        """Get or create lock for key."""
        if key not in self.locks:
            self.locks[key] = asyncio.Lock()
        return self.locks[key]

    def _generate_checksum(self, data: Dict[str, Any]) -> str:
        """Generate checksum for state data."""
        content = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()

    def _generate_key(self, state_type: StateType, state_id: str) -> str:
        """Generate storage key for state."""
        return f"state:{state_type.value}:{state_id}"

    async def get_state(
        self, state_type: StateType, state_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get state by type and ID."""
        key = self._generate_key(state_type, state_id)

        try:
            self._metrics["gets"] += 1

            state_data = await self.storage.get(key)
            if state_data:
                self._metrics["hits"] += 1

                # Update access metadata
                if "metadata" in state_data:
                    state_data["metadata"]["access_count"] += 1
                    state_data["metadata"]["last_accessed"] = datetime.now()
                    await self.storage.set(key, state_data)

                return state_data
            else:
                self._metrics["misses"] += 1
                return None

        except Exception as e:
            self._metrics["errors"] += 1
            logger.error(
                "Failed to get state",
                state_type=state_type,
                state_id=state_id,
                error=str(e),
            )
            return None

    async def set_state(
        self,
        state_type: StateType,
        state_id: str,
        data: Dict[str, Any],
        ttl: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Set state with validation and metadata."""
        key = self._generate_key(state_type, state_id)
        lock = self._get_lock(key)

        async with lock:
            try:
                self._metrics["sets"] += 1

                # Validate state data
                if not self.validator.validate(state_type.value, data):
                    raise ValueError(f"State validation failed for {state_type}")

                # Create or update metadata
                now = datetime.now()
                existing_state = await self.get_state(state_type, state_id)

                if existing_state:
                    # Update existing state
                    state_metadata = existing_state.get("metadata", {})
                    state_metadata["updated_at"] = now
                    state_metadata["version"] += 1
                    state_metadata["status"] = StateStatus.ACTIVE
                else:
                    # Create new state
                    state_metadata = StateMetadata(
                        id=state_id,
                        type=state_type,
                        status=StateStatus.ACTIVE,
                        created_at=now,
                        updated_at=now,
                        version=1,
                        owner=metadata.get("owner") if metadata else None,
                        workspace=metadata.get("workspace") if metadata else None,
                        tags=set(metadata.get("tags", [])) if metadata else set(),
                    )

                # Update checksum and size
                serialized_data = self.serializer.serialize_json(data)
                state_metadata["checksum"] = self._generate_checksum(data)
                state_metadata["size"] = len(serialized_data)
                state_metadata["ttl"] = ttl

                # Merge additional metadata
                if metadata:
                    for key, value in metadata.items():
                        if key not in state_metadata:
                            state_metadata[key] = value

                # Create state object
                state_obj = {
                    "id": state_id,
                    "type": state_type.value,
                    "data": data,
                    "metadata": asdict(state_metadata),
                }

                # Store state
                success = await self.storage.set(key, state_obj, ttl)

                if success:
                    # Create snapshot
                    await self._create_snapshot(
                        state_id, state_obj, StateOperation.CREATE
                    )
                    logger.debug(
                        "State set successfully",
                        state_type=state_type,
                        state_id=state_id,
                    )

                return success

            except Exception as e:
                self._metrics["errors"] += 1
                logger.error(
                    "Failed to set state",
                    state_type=state_type,
                    state_id=state_id,
                    error=str(e),
                )
                return False

    async def update_state(
        self,
        state_type: StateType,
        state_id: str,
        updates: Dict[str, Any],
        operation: StateOperation = StateOperation.UPDATE,
    ) -> bool:
        """Update existing state."""
        key = self._generate_key(state_type, state_id)
        lock = self._get_lock(key)

        async with lock:
            try:
                # Get existing state
                existing_state = await self.get_state(state_type, state_id)
                if not existing_state:
                    logger.warning(
                        "State not found for update",
                        state_type=state_type,
                        state_id=state_id,
                    )
                    return False

                # Apply updates based on operation
                if operation == StateOperation.UPDATE:
                    existing_state["data"].update(updates)
                elif operation == StateOperation.PATCH:
                    for key, value in updates.items():
                        if "." in key:
                            # Support nested key updates
                            keys = key.split(".")
                            current = existing_state["data"]
                            for k in keys[:-1]:
                                if k not in current:
                                    current[k] = {}
                                current = current[k]
                            current[keys[-1]] = value
                        else:
                            existing_state["data"][key] = value
                elif operation == StateOperation.MERGE:
                    # Deep merge for dictionaries
                    for key, value in updates.items():
                        if (
                            key in existing_state["data"]
                            and isinstance(existing_state["data"][key], dict)
                            and isinstance(value, dict)
                        ):
                            existing_state["data"][key].update(value)
                        else:
                            existing_state["data"][key] = value

                # Update metadata
                existing_state["metadata"]["updated_at"] = datetime.now()
                existing_state["metadata"]["version"] += 1
                existing_state["metadata"]["status"] = StateStatus.ACTIVE

                # Recalculate checksum
                existing_state["metadata"]["checksum"] = self._generate_checksum(
                    existing_state["data"]
                )

                # Store updated state
                success = await self.storage.set(key, existing_state)

                if success:
                    # Create snapshot and transition
                    await self._create_snapshot(state_id, existing_state, operation)
                    await self._create_transition(
                        state_id,
                        existing_state["metadata"]["version"] - 1,
                        existing_state["metadata"]["version"],
                        operation,
                        updates,
                    )

                return success

            except Exception as e:
                self._metrics["errors"] += 1
                logger.error(
                    "Failed to update state",
                    state_type=state_type,
                    state_id=state_id,
                    error=str(e),
                )
                return False

    async def delete_state(self, state_type: StateType, state_id: str) -> bool:
        """Delete state."""
        key = self._generate_key(state_type, state_id)
        lock = self._get_lock(key)

        async with lock:
            try:
                self._metrics["deletes"] += 1

                # Get existing state for snapshot
                existing_state = await self.get_state(state_type, state_id)

                # Delete from storage
                success = await self.storage.delete(key)

                if success and existing_state:
                    # Create final snapshot
                    existing_state["metadata"]["status"] = StateStatus.ARCHIVED
                    await self._create_snapshot(
                        state_id, existing_state, StateOperation.DELETE
                    )

                    # Clean up snapshots and transitions
                    if state_id in self.snapshots:
                        del self.snapshots[state_id]
                    if state_id in self.transitions:
                        del self.transitions[state_id]

                return success

            except Exception as e:
                self._metrics["errors"] += 1
                logger.error(
                    "Failed to delete state",
                    state_type=state_type,
                    state_id=state_id,
                    error=str(e),
                )
                return False

    async def list_states(self, state_type: StateType, pattern: str = "*") -> List[str]:
        """List state IDs by type and pattern."""
        try:
            key_pattern = self._generate_key(state_type, pattern)
            keys = await self.storage.keys(key_pattern)

            # Extract state IDs from keys
            state_ids = []
            for key in keys:
                parts = key.split(":")
                if len(parts) >= 3:
                    state_ids.append(parts[2])

            return state_ids

        except Exception as e:
            logger.error(
                "Failed to list states",
                state_type=state_type,
                pattern=pattern,
                error=str(e),
            )
            return []

    async def get_state_history(
        self, state_id: str, limit: int = 10
    ) -> List[StateSnapshot]:
        """Get state history snapshots."""
        if state_id in self.snapshots:
            return self.snapshots[state_id][-limit:]
        return []

    async def get_state_transitions(
        self, state_id: str, limit: int = 10
    ) -> List[StateTransition]:
        """Get state transitions."""
        if state_id in self.transitions:
            return self.transitions[state_id][-limit:]
        return []

    async def _create_snapshot(
        self, state_id: str, state_obj: Dict[str, Any], operation: StateOperation
    ):
        """Create state snapshot."""
        snapshot = StateSnapshot(
            id=str(uuid.uuid4()),
            state_id=state_id,
            version=state_obj["metadata"]["version"],
            data=state_obj["data"].copy(),
            metadata=state_obj["metadata"],
            created_at=datetime.now(),
            operation=operation,
            checksum=state_obj["metadata"]["checksum"],
            size=state_obj["metadata"]["size"],
        )

        if state_id not in self.snapshots:
            self.snapshots[state_id] = []

        self.snapshots[state_id].append(snapshot)

        # Keep only recent snapshots
        if len(self.snapshots[state_id]) > 100:
            self.snapshots[state_id] = self.snapshots[state_id][-100:]

    async def _create_transition(
        self,
        state_id: str,
        from_version: int,
        to_version: int,
        operation: StateOperation,
        changes: Dict[str, Any],
    ):
        """Create state transition record."""
        transition = StateTransition(
            id=str(uuid.uuid4()),
            state_id=state_id,
            from_version=from_version,
            to_version=to_version,
            operation=operation,
            changes=changes.copy(),
            applied_at=datetime.now(),
        )

        if state_id not in self.transitions:
            self.transitions[state_id] = []

        self.transitions[state_id].append(transition)

        # Keep only recent transitions
        if len(self.transitions[state_id]) > 100:
            self.transitions[state_id] = self.transitions[state_id][-100:]

    def get_metrics(self) -> Dict[str, Any]:
        """Get state manager metrics."""
        return {
            "operations": self._metrics,
            "snapshots_count": sum(
                len(snapshots) for snapshots in self.snapshots.values()
            ),
            "transitions_count": sum(
                len(transitions) for transitions in self.transitions.values()
            ),
            "locks_count": len(self.locks),
        }

    async def cleanup_expired_states(self):
        """Clean up expired states."""
        try:
            keys = await self.storage.keys("state:*")
            now = datetime.now()

            for key in keys:
                state_data = await self.storage.get(key)
                if state_data and "metadata" in state_data:
                    metadata = state_data["metadata"]

                    # Check TTL
                    if metadata.get("expires_at") and now > metadata["expires_at"]:
                        await self.storage.delete(key)
                        logger.info("Cleaned up expired state", key=key)

                    # Check inactive states
                    elif (
                        metadata.get("status") == StateStatus.INACTIVE
                        and metadata.get("updated_at")
                        and now - metadata["updated_at"] > timedelta(days=7)
                    ):
                        await self.storage.delete(key)
                        logger.info("Cleaned up inactive state", key=key)

        except Exception as e:
            logger.error("Failed to cleanup expired states", error=str(e))

    async def close(self):
        """Close state manager and cleanup resources."""
        if hasattr(self.storage, "disconnect"):
            await self.storage.disconnect()

        self.locks.clear()
        self.snapshots.clear()
        self.transitions.clear()


# Global state manager instance
state_manager = StateManager()

# Export main components
__all__ = [
    "StateManager",
    "StateType",
    "StateStatus",
    "StateOperation",
    "StateMetadata",
    "StateSnapshot",
    "StateTransition",
    "StateSchema",
    "StateValidator",
    "StateSerializer",
    "StateStorage",
    "RedisStateStorage",
    "MemoryStateStorage",
    "state_manager",
]
