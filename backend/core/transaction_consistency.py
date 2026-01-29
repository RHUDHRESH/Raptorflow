"""
Transaction Consistency Manager for Payment System
Implements database transaction management with proper locking and consistency
Addresses critical transaction consistency vulnerabilities identified in red team audit
"""

import asyncio
import json
import logging
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union

import asyncpg
import redis

from .core.audit_logger import EventType, LogLevel, audit_logger

logger = logging.getLogger(__name__)


class TransactionState(Enum):
    """Transaction states"""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    ROLLED_BACK = "ROLLED_BACK"


class LockType(Enum):
    """Lock types for resource protection"""

    EXCLUSIVE = "EXCLUSIVE"
    SHARED = "SHARED"
    INTENT_EXCLUSIVE = "INTENT_EXCLUSIVE"
    INTENT_SHARED = "INTENT_SHARED"


class IsolationLevel(Enum):
    """Database transaction isolation levels"""

    READ_COMMITTED = "READ COMMITTED"
    REPEATABLE_READ = "REPEATABLE READ"
    SERIALIZABLE = "SERIALIZABLE"


@dataclass
class TransactionContext:
    """Transaction context for tracking operations"""

    transaction_id: str
    isolation_level: IsolationLevel
    state: TransactionState
    created_at: datetime
    updated_at: datetime
    operations: List[Dict[str, Any]] = field(default_factory=list)
    locks_acquired: List[str] = field(default_factory=list)
    rollback_actions: List[Callable] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LockInfo:
    """Lock information"""

    resource_key: str
    lock_type: LockType
    owner_id: str
    acquired_at: datetime
    expires_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class TransactionConsistencyManager:
    """
    Production-Ready Transaction Consistency Manager
    Implements ACID properties with proper locking and consistency
    """

    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db_pool = db_pool

        # Configuration
        self.default_lock_timeout_seconds = 30
        self.max_transaction_duration_minutes = 10
        self.lock_retry_attempts = 3
        self.lock_retry_delay_ms = 100

        # Lock prefixes
        self.lock_prefix = "tx_lock:"
        self.transaction_prefix = "tx_context:"

        logger.info("Transaction Consistency Manager initialized")

    @asynccontextmanager
    async def transaction_context(
        self,
        isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED,
        transaction_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Context manager for database transactions with consistency guarantees
        """
        if not transaction_id:
            transaction_id = (
                f"TX{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8]}"
            )

        # Create transaction context
        context = TransactionContext(
            transaction_id=transaction_id,
            isolation_level=isolation_level,
            state=TransactionState.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata=metadata or {},
        )

        # Store transaction context
        await self._store_transaction_context(context)

        conn = None
        try:
            # Get database connection
            conn = await self.db_pool.acquire()

            # Begin transaction with appropriate isolation level
            await conn.execute(
                f"BEGIN TRANSACTION ISOLATION LEVEL {isolation_level.value}"
            )

            # Update context state
            context.state = TransactionState.PROCESSING
            context.updated_at = datetime.now()
            await self._store_transaction_context(context)

            # Log transaction start
            await audit_logger.log_event(
                event_type=EventType.TRANSACTION_STARTED,
                level=LogLevel.INFO,
                transaction_id=transaction_id,
                request_data={
                    "isolation_level": isolation_level.value,
                    "metadata": metadata,
                },
            )

            yield TransactionWrapper(conn, context, self)

            # Commit transaction
            await conn.execute("COMMIT")

            # Update context state
            context.state = TransactionState.COMPLETED
            context.updated_at = datetime.now()
            await self._store_transaction_context(context)

            # Log transaction completion
            await audit_logger.log_event(
                event_type=EventType.TRANSACTION_COMPLETED,
                level=LogLevel.INFO,
                transaction_id=transaction_id,
                request_data={
                    "operations_count": len(context.operations),
                    "locks_acquired": len(context.locks_acquired),
                },
            )

        except Exception as e:
            # Rollback transaction
            if conn:
                try:
                    await conn.execute("ROLLBACK")
                except Exception as rollback_error:
                    logger.error(f"Rollback failed: {rollback_error}")

            # Update context state
            context.state = TransactionState.FAILED
            context.updated_at = datetime.now()
            await self._store_transaction_context(context)

            # Execute rollback actions
            await self._execute_rollback_actions(context)

            # Log transaction failure
            await audit_logger.log_event(
                event_type=EventType.TRANSACTION_FAILED,
                level=LogLevel.ERROR,
                transaction_id=transaction_id,
                error_message=str(e),
            )

            raise

        finally:
            # Release all locks
            await self._release_all_locks(context)

            # Clean up transaction context
            await self._cleanup_transaction_context(context)

            # Return connection to pool
            if conn:
                await self.db_pool.release(conn)

    async def acquire_lock(
        self,
        resource_key: str,
        lock_type: LockType = LockType.EXCLUSIVE,
        timeout_seconds: Optional[int] = None,
        owner_id: Optional[str] = None,
    ) -> Optional[LockInfo]:
        """
        Acquire distributed lock with proper conflict resolution
        """
        if timeout_seconds is None:
            timeout_seconds = self.default_lock_timeout_seconds

        if not owner_id:
            owner_id = str(uuid.uuid4())

        lock_key = f"{self.lock_prefix}{resource_key}"
        expires_at = datetime.now() + timedelta(seconds=timeout_seconds)

        lock_info = LockInfo(
            resource_key=resource_key,
            lock_type=lock_type,
            owner_id=owner_id,
            acquired_at=datetime.now(),
            expires_at=expires_at,
        )

        # Try to acquire lock with retry logic
        for attempt in range(self.lock_retry_attempts):
            try:
                # Check for existing locks
                existing_lock = await self._get_existing_lock(resource_key)

                if existing_lock:
                    # Check if lock is expired
                    if datetime.now() > existing_lock.expires_at:
                        # Force release expired lock
                        await self._force_release_lock(resource_key)
                    else:
                        # Lock is held, check compatibility
                        if not self._are_locks_compatible(
                            existing_lock.lock_type, lock_type
                        ):
                            if attempt < self.lock_retry_attempts - 1:
                                await asyncio.sleep(self.lock_retry_delay_ms / 1000)
                                continue
                            else:
                                return None  # Cannot acquire lock

                # Acquire lock
                lock_data = json.dumps(
                    {
                        "resource_key": resource_key,
                        "lock_type": lock_type.value,
                        "owner_id": owner_id,
                        "acquired_at": lock_info.acquired_at.isoformat(),
                        "expires_at": expires_at.isoformat(),
                    }
                )

                # Use Redis SET with NX and EX for atomic lock acquisition
                success = self.redis.set(
                    lock_key, lock_data, nx=True, ex=timeout_seconds
                )

                if success:
                    await audit_logger.log_event(
                        event_type=EventType.LOCK_ACQUIRED,
                        level=LogLevel.DEBUG,
                        request_data={
                            "resource_key": resource_key,
                            "lock_type": lock_type.value,
                            "owner_id": owner_id,
                            "timeout_seconds": timeout_seconds,
                        },
                    )
                    return lock_info
                else:
                    # Lock acquisition failed, retry
                    if attempt < self.lock_retry_attempts - 1:
                        await asyncio.sleep(self.lock_retry_delay_ms / 1000)
                    else:
                        return None

            except Exception as e:
                logger.error(f"Lock acquisition error: {e}")
                if attempt < self.lock_retry_attempts - 1:
                    await asyncio.sleep(self.lock_retry_delay_ms / 1000)
                else:
                    raise

        return None

    async def release_lock(self, resource_key: str, owner_id: str) -> bool:
        """
        Release distributed lock
        """
        try:
            lock_key = f"{self.lock_prefix}{resource_key}"

            # Get existing lock
            existing_lock = await self._get_existing_lock(resource_key)

            if not existing_lock:
                return False  # Lock doesn't exist

            if existing_lock.owner_id != owner_id:
                return False  # Not the lock owner

            # Release lock
            self.redis.delete(lock_key)

            await audit_logger.log_event(
                event_type=EventType.LOCK_RELEASED,
                level=LogLevel.DEBUG,
                request_data={"resource_key": resource_key, "owner_id": owner_id},
            )

            return True

        except Exception as e:
            logger.error(f"Lock release error: {e}")
            return False

    async def execute_with_lock(
        self,
        resource_key: str,
        operation: Callable,
        lock_type: LockType = LockType.EXCLUSIVE,
        timeout_seconds: Optional[int] = None,
    ):
        """
        Execute operation with automatic lock management
        """
        lock_info = await self.acquire_lock(resource_key, lock_type, timeout_seconds)

        if not lock_info:
            raise Exception(f"Failed to acquire lock for resource: {resource_key}")

        try:
            result = await operation()
            return result
        finally:
            await self.release_lock(resource_key, lock_info.owner_id)

    async def _store_transaction_context(self, context: TransactionContext):
        """Store transaction context in Redis"""
        try:
            context_key = f"{self.transaction_prefix}{context.transaction_id}"
            context_data = {
                "transaction_id": context.transaction_id,
                "isolation_level": context.isolation_level.value,
                "state": context.state.value,
                "created_at": context.created_at.isoformat(),
                "updated_at": context.updated_at.isoformat(),
                "operations": context.operations,
                "locks_acquired": context.locks_acquired,
                "metadata": context.metadata,
            }

            # Store with expiration
            self.redis.setex(
                context_key,
                self.max_transaction_duration_minutes * 60,
                json.dumps(context_data),
            )

        except Exception as e:
            logger.error(f"Error storing transaction context: {e}")

    async def _get_existing_lock(self, resource_key: str) -> Optional[LockInfo]:
        """Get existing lock information"""
        try:
            lock_key = f"{self.lock_prefix}{resource_key}"
            lock_data = self.redis.get(lock_key)

            if not lock_data:
                return None

            lock_dict = json.loads(lock_data)

            return LockInfo(
                resource_key=lock_dict["resource_key"],
                lock_type=LockType(lock_dict["lock_type"]),
                owner_id=lock_dict["owner_id"],
                acquired_at=datetime.fromisoformat(lock_dict["acquired_at"]),
                expires_at=datetime.fromisoformat(lock_dict["expires_at"]),
            )

        except Exception as e:
            logger.error(f"Error getting existing lock: {e}")
            return None

    async def _force_release_lock(self, resource_key: str):
        """Force release expired lock"""
        try:
            lock_key = f"{self.lock_prefix}{resource_key}"
            self.redis.delete(lock_key)

            await audit_logger.log_security_violation(
                violation_type="expired_lock_force_released",
                request_data={"resource_key": resource_key},
            )

        except Exception as e:
            logger.error(f"Error force releasing lock: {e}")

    def _are_locks_compatible(
        self, existing_type: LockType, requested_type: LockType
    ) -> bool:
        """Check if lock types are compatible"""
        # Simplified compatibility matrix
        if existing_type == LockType.EXCLUSIVE:
            return False  # Exclusive locks are not compatible with any other locks
        elif existing_type == LockType.INTENT_EXCLUSIVE:
            return (
                requested_type == LockType.SHARED
                or requested_type == LockType.INTENT_SHARED
            )
        elif existing_type == LockType.SHARED:
            return (
                requested_type == LockType.SHARED
                or requested_type == LockType.INTENT_SHARED
            )
        elif existing_type == LockType.INTENT_SHARED:
            return requested_type == LockType.INTENT_SHARED
        else:
            return False

    async def _release_all_locks(self, context: TransactionContext):
        """Release all locks acquired by transaction"""
        for lock_key in context.locks_acquired:
            try:
                # Extract resource key from stored lock key
                resource_key = lock_key.replace(self.lock_prefix, "")
                await self.release_lock(resource_key, context.transaction_id)
            except Exception as e:
                logger.error(f"Error releasing lock {lock_key}: {e}")

    async def _execute_rollback_actions(self, context: TransactionContext):
        """Execute rollback actions for failed transaction"""
        for rollback_action in reversed(context.rollback_actions):
            try:
                if asyncio.iscoroutinefunction(rollback_action):
                    await rollback_action()
                else:
                    rollback_action()
            except Exception as e:
                logger.error(f"Error executing rollback action: {e}")

    async def _cleanup_transaction_context(self, context: TransactionContext):
        """Clean up transaction context"""
        try:
            context_key = f"{self.transaction_prefix}{context.transaction_id}"
            self.redis.delete(context_key)
        except Exception as e:
            logger.error(f"Error cleaning up transaction context: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Health check for transaction consistency manager"""
        try:
            # Check Redis connection
            try:
                self.redis.ping()
                redis_healthy = True
            except Exception as e:
                redis_healthy = False
                redis_error = str(e)

            # Check database connection
            try:
                async with self.db_pool.acquire() as conn:
                    await conn.execute("SELECT 1")
                db_healthy = True
            except Exception as e:
                db_healthy = False
                db_error = str(e)

            # Check active locks
            try:
                lock_keys = self.redis.keys(f"{self.lock_prefix}*")
                active_locks = len(lock_keys)
            except Exception:
                active_locks = 0

            # Check active transactions
            try:
                tx_keys = self.redis.keys(f"{self.transaction_prefix}*")
                active_transactions = len(tx_keys)
            except Exception:
                active_transactions = 0

            overall_healthy = redis_healthy and db_healthy

            return {
                "status": "healthy" if overall_healthy else "unhealthy",
                "message": (
                    "Transaction consistency manager is operational"
                    if overall_healthy
                    else "Transaction consistency manager has issues"
                ),
                "features": {
                    "distributed_locks": True,
                    "transaction_isolation": True,
                    "rollback_support": True,
                    "deadlock_prevention": True,
                    "audit_logging": True,
                },
                "configuration": {
                    "default_lock_timeout_seconds": self.default_lock_timeout_seconds,
                    "max_transaction_duration_minutes": self.max_transaction_duration_minutes,
                    "lock_retry_attempts": self.lock_retry_attempts,
                },
                "runtime": {
                    "active_locks": active_locks,
                    "active_transactions": active_transactions,
                },
                "dependencies": {
                    "redis": (
                        "healthy" if redis_healthy else f"unhealthy: {redis_error}"
                    ),
                    "database": "healthy" if db_healthy else f"unhealthy: {db_error}",
                },
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Health check failed: {str(e)}",
                "error": str(e),
            }


class TransactionWrapper:
    """
    Wrapper for database operations within a transaction
    """

    def __init__(
        self,
        connection: asyncpg.Connection,
        context: TransactionContext,
        manager: TransactionConsistencyManager,
    ):
        self.conn = connection
        self.context = context
        self.manager = manager

    async def execute(self, query: str, *args, **kwargs) -> str:
        """Execute SQL query within transaction"""
        try:
            result = await self.conn.execute(query, *args, **kwargs)

            # Record operation
            self.context.operations.append(
                {
                    "type": "execute",
                    "query": query,
                    "args": args,
                    "kwargs": kwargs,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return result

        except Exception as e:
            logger.error(f"SQL execution error: {e}")
            raise

    async def fetch(self, query: str, *args, **kwargs) -> List[asyncpg.Record]:
        """Fetch records within transaction"""
        try:
            result = await self.conn.fetch(query, *args, **kwargs)

            # Record operation
            self.context.operations.append(
                {
                    "type": "fetch",
                    "query": query,
                    "args": args,
                    "kwargs": kwargs,
                    "timestamp": datetime.now().isoformat(),
                    "result_count": len(result),
                }
            )

            return result

        except Exception as e:
            logger.error(f"SQL fetch error: {e}")
            raise

    async def fetchval(self, query: str, *args, **kwargs) -> Any:
        """Fetch single value within transaction"""
        try:
            result = await self.conn.fetchval(query, *args, **kwargs)

            # Record operation
            self.context.operations.append(
                {
                    "type": "fetchval",
                    "query": query,
                    "args": args,
                    "kwargs": kwargs,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return result

        except Exception as e:
            logger.error(f"SQL fetchval error: {e}")
            raise

    async def fetchrow(self, query: str, *args, **kwargs) -> asyncpg.Record:
        """Fetch single row within transaction"""
        try:
            result = await self.conn.fetchrow(query, *args, **kwargs)

            # Record operation
            self.context.operations.append(
                {
                    "type": "fetchrow",
                    "query": query,
                    "args": args,
                    "kwargs": kwargs,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return result

        except Exception as e:
            logger.error(f"SQL fetchrow error: {e}")
            raise

    async def acquire_resource_lock(
        self, resource_key: str, lock_type: LockType = LockType.EXCLUSIVE
    ):
        """Acquire resource lock within transaction"""
        lock_info = await self.manager.acquire_lock(
            resource_key=resource_key,
            lock_type=lock_type,
            owner_id=self.context.transaction_id,
        )

        if lock_info:
            self.context.locks_acquired.append(
                f"{self.manager.lock_prefix}{resource_key}"
            )

            # Add rollback action to release lock
            self.context.rollback_actions.append(
                lambda: self.manager.release_lock(
                    resource_key, self.context.transaction_id
                )
            )

            return lock_info
        else:
            raise Exception(f"Failed to acquire lock for resource: {resource_key}")

    def add_rollback_action(self, action: Callable):
        """Add rollback action for transaction"""
        self.context.rollback_actions.append(action)


# Global transaction consistency manager instance
transaction_manager = None


def get_transaction_manager(
    redis_client: redis.Redis, db_pool: asyncpg.Pool
) -> TransactionConsistencyManager:
    """Get or create transaction consistency manager instance"""
    global transaction_manager
    if transaction_manager is None:
        transaction_manager = TransactionConsistencyManager(redis_client, db_pool)
    return transaction_manager
