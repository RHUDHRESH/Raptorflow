# PHASE 1: PROJECT STRUCTURE & FOUNDATION INFRASTRUCTURE

---

## 1.1 Complete Directory Structure

```
backend/
├── main.py                          # FastAPI entry point
├── requirements.txt                 # Production dependencies
├── Dockerfile                       # Multi-stage build
├── docker-compose.yml               # Local development
├── pytest.ini                       # Test configuration
├── .env.example                     # Environment template
│
├── alembic/                         # Database migrations
│   ├── versions/
│   │   ├── 001_initial_schema.py
│   │   ├── 002_add_events.py
│   │   └── 003_add_indian_market.py
│   ├── env.py
│   └── alembic.ini
│
├── core/
│   ├── __init__.py
│   ├── config.py                    # Pydantic settings
│   ├── database.py                  # Async connection pools
│   ├── redis_client.py              # Redis with connection pool
│   ├── event_store.py               # Event sourcing
│   ├── transaction.py               # Transaction management
│   ├── resilience.py                # Circuit breakers
│   ├── cancellation.py              # Request cancellation
│   ├── call_stack.py                # Agent recursion control
│   └── exceptions.py                # Custom exceptions
│
├── security/
│   ├── __init__.py
│   ├── sanitizer.py                 # Input sanitization
│   ├── pii_scanner.py               # PII detection
│   ├── secret_vault.py              # Secret management
│   ├── rate_limiter.py              # Rate limiting
│   ├── audit_logger.py              # Audit logging
│   └── rls_policies.py              # Row-level security
│
├── skills/
│   ├── __init__.py
│   ├── compiler.py                  # Skill compiler
│   ├── registry.py                  # Skill registry with hot-reload
│   ├── validator.py                 # Schema validation
│   ├── versioning.py                # Semantic versioning
│   ├── codegen.py                   # TypeScript type generation
│   │
│   └── definitions/                 # Markdown skill files (20+)
│       ├── research/
│       ├── content/
│       ├── campaigns/
│       ├── indian/
│       ├── muse/
│       └── moves/
│
├── agents/
│   ├── __init__.py
│   ├── queen_router.py              # Central task routing
│   ├── swarm_node.py                # Generic agent executor
│   ├── critic.py                    # QA validation
│   ├── overseer.py                  # Final approval
│   └── model_cascade.py             # Fallback handling
│
├── cognition/
│   ├── __init__.py
│   ├── context_manager.py           # Context optimization
│   ├── hallucination_detector.py    # Fact verification
│   ├── adversarial_critic.py        # Quality checker
│   ├── summarizer.py                # Context compression
│   └── user_constitution.py         # Preference learning
│
├── memory/
│   ├── __init__.py
│   ├── vector_store.py              # Embedding storage
│   ├── graph_store.py               # Knowledge graph (GraphRAG)
│   ├── conversation.py              # Chat history
│   ├── foundation_store.py          # User Foundation data
│   └── decay_manager.py             # Memory cleanup
│
├── tools/
│   ├── __init__.py
│   ├── registry.py                  # Tool registry
│   ├── base.py                      # Tool base class
│   ├── sandbox.py                   # Sandboxed execution
│   │
│   ├── search/
│   │   ├── web_search.py
│   │   └── news_search.py
│   │
│   ├── scrapers/
│   │   ├── generic_scraper.py
│   │   ├── vision_scraper.py        # Screenshot-based
│   │   ├── justdial_scraper.py
│   │   ├── indiamart_scraper.py
│   │   └── linkedin_scraper.py
│   │
│   ├── database/
│   │   ├── reader.py
│   │   └── writer.py
│   │
│   └── indian/
│       ├── gst_calculator.py
│       └── regional_translator.py
│
├── economics/
│   ├── __init__.py
│   ├── cost_predictor.py            # Pre-execution estimates
│   ├── budget_enforcer.py           # Budget controls
│   ├── semantic_cache.py            # Query caching
│   ├── anomaly_detector.py          # Cost alerts
│   └── usage_tracker.py             # Per-user tracking
│
├── products/
│   ├── __init__.py
│   ├── blackbox/
│   │   ├── strategy_engine.py
│   │   └── risk_calculator.py
│   │
│   ├── moves/
│   │   ├── move_generator.py
│   │   └── execution_tracker.py
│   │
│   ├── campaigns/
│   │   ├── campaign_planner.py
│   │   └── calendar_optimizer.py
│   │
│   ├── muse/
│   │   ├── creative_engine.py
│   │   └── brand_enforcer.py
│   │
│   └── onboarding/
│       ├── foundation_builder.py
│       └── icp_generator.py
│
├── indian_market/
│   ├── __init__.py
│   ├── phonepe_gateway.py           # Payment processing
│   ├── gst_service.py               # GST invoicing
│   ├── festival_calendar.py         # Indian holidays
│   ├── regional_languages.py        # Hindi/Tamil/Telugu
│   └── local_sources.py             # Indian data sources
│
├── api/
│   ├── __init__.py
│   ├── deps.py                      # Dependency injection
│   │
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── agents.py                # Agent endpoints
│   │   ├── skills.py                # Skill management
│   │   ├── campaigns.py             # Campaign endpoints
│   │   ├── moves.py                 # Moves endpoints
│   │   ├── muse.py                  # Creative endpoints
│   │   ├── blackbox.py              # Strategy endpoints
│   │   ├── foundation.py            # Onboarding endpoints
│   │   └── billing.py               # Payment endpoints
│   │
│   └── webhooks/
│       ├── phonepe.py               # Payment webhooks
│       └── external.py              # External integrations
│
├── workers/
│   ├── __init__.py
│   ├── queue.py                     # Task queue (Redis-based)
│   ├── scheduler.py                 # Cron jobs
│   └── processors/
│       ├── agent_processor.py
│       └── campaign_processor.py
│
├── observability/
│   ├── __init__.py
│   ├── metrics.py                   # Prometheus metrics
│   ├── tracing.py                   # Distributed tracing
│   └── health.py                    # Health checks
│
└── tests/
    ├── __init__.py
    ├── conftest.py                  # Pytest fixtures
    ├── unit/
    ├── integration/
    └── golden_datasets/             # LLM evaluation data
```

---

## 1.2 Core Configuration

```python
# backend/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    All secrets come from environment, never hardcoded.
    """

    # Application
    APP_NAME: str = "Raptorflow Neural Nexus"
    APP_VERSION: str = "4.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"  # development, staging, production

    # API
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["https://app.raptorflow.com"]

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30

    # Redis
    REDIS_URL: str
    REDIS_POOL_SIZE: int = 50
    REDIS_SOCKET_TIMEOUT: int = 5

    # AI Models (Vertex AI)
    GCP_PROJECT_ID: str
    GCP_LOCATION: str = "us-central1"
    VERTEX_AI_ENABLED: bool = True

    # Model Defaults
    DEFAULT_MODEL: str = "gemini-2.0-flash"
    FALLBACK_MODEL: str = "gemini-2.0-pro"
    ROUTER_MODEL: str = "gemini-2.0-flash-lite"

    # Cost Controls
    MAX_COST_PER_REQUEST: float = 1.0  # USD
    MAX_TOKENS_PER_REQUEST: int = 100000
    DEFAULT_TIMEOUT_SECONDS: int = 60

    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # Indian Market
    PHONEPE_CLIENT_ID: str
    PHONEPE_CLIENT_SECRET: str
    PHONEPE_ENVIRONMENT: str = "PRODUCTION"  # UAT or PRODUCTION
    GST_ENABLED: bool = True
    DEFAULT_CURRENCY: str = "INR"

    # Observability
    SENTRY_DSN: Optional[str] = None
    ENABLE_TRACING: bool = True
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

---

## 1.3 Database Connection Pool

```python
# backend/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Create async engine with connection pooling
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_pre_ping=True,  # Verify connections before use
    echo=settings.DEBUG,
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base for models
Base = declarative_base()


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.
    Automatically handles commit/rollback.
    """
    session = async_session_maker()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        await session.close()


class TransactionManager:
    """
    ACID-compliant transaction management for multi-step operations.
    """

    def __init__(self):
        self.session_maker = async_session_maker

    @asynccontextmanager
    async def atomic(self):
        """
        Execute multiple operations atomically.
        All succeed or all fail.
        """
        async with self.session_maker() as session:
            async with session.begin():
                try:
                    yield session
                except Exception:
                    await session.rollback()
                    raise


# Singleton instance
transaction_manager = TransactionManager()
```

---

## 1.4 Redis Client with Connection Pool

```python
# backend/core/redis_client.py
import redis.asyncio as redis
from typing import Optional, Any
import json
import logging

from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RedisClient:
    """
    Redis client with connection pooling and helper methods.
    Used for: caching, queues, pub/sub, rate limiting, distributed locks.
    """

    def __init__(self):
        self.pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_POOL_SIZE,
            socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
            decode_responses=True,
        )
        self._client: Optional[redis.Redis] = None

    async def get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.Redis(connection_pool=self.pool)
        return self._client

    # ===== Basic Operations =====

    async def get(self, key: str) -> Optional[str]:
        client = await self.get_client()
        return await client.get(key)

    async def set(self, key: str, value: str, ex: int = None, nx: bool = False) -> bool:
        client = await self.get_client()
        return await client.set(key, value, ex=ex, nx=nx)

    async def delete(self, *keys: str) -> int:
        client = await self.get_client()
        return await client.delete(*keys)

    async def exists(self, key: str) -> bool:
        client = await self.get_client()
        return await client.exists(key) > 0

    # ===== JSON Operations =====

    async def get_json(self, key: str) -> Optional[Any]:
        value = await self.get(key)
        return json.loads(value) if value else None

    async def set_json(self, key: str, value: Any, ex: int = None) -> bool:
        return await self.set(key, json.dumps(value), ex=ex)

    # ===== Distributed Locking =====

    async def acquire_lock(self, key: str, ttl: int = 30) -> bool:
        """
        Acquire a distributed lock. Returns True if acquired.
        """
        lock_key = f"lock:{key}"
        return await self.set(lock_key, "locked", ex=ttl, nx=True)

    async def release_lock(self, key: str) -> bool:
        """
        Release a distributed lock.
        """
        lock_key = f"lock:{key}"
        return await self.delete(lock_key) > 0

    # ===== Rate Limiting =====

    async def check_rate_limit(self, key: str, limit: int, window: int) -> dict:
        """
        Check rate limit using sliding window.
        Returns: {"allowed": bool, "remaining": int, "reset_in": int}
        """
        client = await self.get_client()
        rate_key = f"rate:{key}"

        current = await client.incr(rate_key)
        if current == 1:
            await client.expire(rate_key, window)

        ttl = await client.ttl(rate_key)

        return {
            "allowed": current <= limit,
            "remaining": max(0, limit - current),
            "reset_in": ttl if ttl > 0 else window
        }

    # ===== Pub/Sub =====

    async def publish(self, channel: str, message: Any):
        client = await self.get_client()
        await client.publish(channel, json.dumps(message))

    async def subscribe(self, *channels: str):
        client = await self.get_client()
        pubsub = client.pubsub()
        await pubsub.subscribe(*channels)
        return pubsub

    # ===== Stream Operations (for Event Sourcing) =====

    async def xadd(self, stream: str, fields: dict, maxlen: int = 10000) -> str:
        client = await self.get_client()
        return await client.xadd(stream, fields, maxlen=maxlen)

    async def xread(self, streams: dict, count: int = 100, block: int = 0) -> list:
        client = await self.get_client()
        return await client.xread(streams, count=count, block=block)

    # ===== Cleanup =====

    async def close(self):
        if self._client:
            await self._client.close()
            await self.pool.disconnect()


# Singleton instance
redis_client = RedisClient()
```

---

## 1.5 Event Sourcing System

```python
# backend/core/event_store.py
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel
import json
import logging

from .redis_client import redis_client
from .database import async_session_maker

logger = logging.getLogger(__name__)


class Event(BaseModel):
    """
    Immutable event record.
    """
    event_id: str
    aggregate_id: str  # e.g., "execution:exec_123"
    event_type: str    # e.g., "SKILL_STARTED", "TOOL_CALLED", "OUTPUT_GENERATED"
    data: Dict[str, Any]
    timestamp: datetime
    version: int
    user_id: Optional[str] = None


class EventStore:
    """
    Event sourcing for complete audit trail.
    Every agent decision, tool call, and output is recorded.

    Benefits:
    - Complete audit trail for compliance
    - Replay capability for debugging
    - Time-travel for analysis
    """

    # Event types
    EXECUTION_STARTED = "EXECUTION_STARTED"
    SKILL_SELECTED = "SKILL_SELECTED"
    CONTEXT_LOADED = "CONTEXT_LOADED"
    TOOL_CALLED = "TOOL_CALLED"
    TOOL_RESULT = "TOOL_RESULT"
    LLM_REQUEST = "LLM_REQUEST"
    LLM_RESPONSE = "LLM_RESPONSE"
    VALIDATION_PASSED = "VALIDATION_PASSED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    RETRY_TRIGGERED = "RETRY_TRIGGERED"
    OUTPUT_GENERATED = "OUTPUT_GENERATED"
    EXECUTION_COMPLETED = "EXECUTION_COMPLETED"
    EXECUTION_FAILED = "EXECUTION_FAILED"
    COST_RECORDED = "COST_RECORDED"

    def __init__(self):
        self.redis = redis_client

    async def append(
        self,
        aggregate_id: str,
        event_type: str,
        data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Event:
        """
        Append an immutable event to the event stream.
        """
        # Get next version
        version = await self._get_next_version(aggregate_id)

        event = Event(
            event_id=f"evt_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
            aggregate_id=aggregate_id,
            event_type=event_type,
            data=data,
            timestamp=datetime.utcnow(),
            version=version,
            user_id=user_id
        )

        # Write to Redis stream for real-time processing
        await self.redis.xadd(
            f"events:{aggregate_id}",
            {"data": event.model_dump_json()}
        )

        # Write to Postgres for durability (async, non-blocking)
        await self._persist_to_postgres(event)

        logger.debug(f"Event appended: {event_type} for {aggregate_id}")
        return event

    async def get_events(
        self,
        aggregate_id: str,
        from_version: int = 0,
        event_types: Optional[List[str]] = None
    ) -> List[Event]:
        """
        Retrieve events for an aggregate, optionally filtered.
        """
        async with async_session_maker() as session:
            query = """
                SELECT * FROM events
                WHERE aggregate_id = :aggregate_id AND version >= :from_version
            """
            params = {"aggregate_id": aggregate_id, "from_version": from_version}

            if event_types:
                query += " AND event_type = ANY(:event_types)"
                params["event_types"] = event_types

            query += " ORDER BY version ASC"

            result = await session.execute(query, params)
            rows = result.fetchall()

            return [Event(**dict(row)) for row in rows]

    async def replay(self, aggregate_id: str) -> Dict[str, Any]:
        """
        Replay all events to rebuild current state.
        Useful for debugging and auditing.
        """
        events = await self.get_events(aggregate_id)

        state = {
            "aggregate_id": aggregate_id,
            "version": 0,
            "status": "UNKNOWN",
            "timeline": []
        }

        for event in events:
            state["version"] = event.version
            state["timeline"].append({
                "type": event.event_type,
                "timestamp": event.timestamp.isoformat(),
                "data": event.data
            })

            # Update status based on event type
            if event.event_type == self.EXECUTION_COMPLETED:
                state["status"] = "COMPLETED"
            elif event.event_type == self.EXECUTION_FAILED:
                state["status"] = "FAILED"
            elif event.event_type == self.EXECUTION_STARTED:
                state["status"] = "IN_PROGRESS"

        return state

    async def _get_next_version(self, aggregate_id: str) -> int:
        """
        Get the next version number for an aggregate.
        """
        key = f"event_version:{aggregate_id}"
        client = await self.redis.get_client()
        return await client.incr(key)

    async def _persist_to_postgres(self, event: Event):
        """
        Persist event to PostgreSQL for durability.
        """
        async with async_session_maker() as session:
            await session.execute(
                """
                INSERT INTO events (event_id, aggregate_id, event_type, data, timestamp, version, user_id)
                VALUES (:event_id, :aggregate_id, :event_type, :data, :timestamp, :version, :user_id)
                """,
                {
                    "event_id": event.event_id,
                    "aggregate_id": event.aggregate_id,
                    "event_type": event.event_type,
                    "data": json.dumps(event.data),
                    "timestamp": event.timestamp,
                    "version": event.version,
                    "user_id": event.user_id
                }
            )
            await session.commit()


# Singleton
event_store = EventStore()
```

---

## 1.6 Resilience Patterns

```python
# backend/core/resilience.py
from enum import Enum
from datetime import datetime, timedelta
from typing import Callable, Any, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """
    Prevents cascade failures by stopping calls to failing services.

    States:
    - CLOSED: Normal operation, calls pass through
    - OPEN: Service failing, all calls rejected immediately
    - HALF_OPEN: Testing if service recovered
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_max_calls: int = 3
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_calls = 0

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function through the circuit breaker.
        """
        # Check if we should try to recover
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                logger.info(f"Circuit {self.name}: OPEN -> HALF_OPEN")
            else:
                raise CircuitOpenError(f"Circuit {self.name} is OPEN")

        # Limit calls in half-open state
        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_calls >= self.half_open_max_calls:
                raise CircuitOpenError(f"Circuit {self.name} is HALF_OPEN, max calls reached")
            self.half_open_calls += 1

        # Execute the function
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info(f"Circuit {self.name}: HALF_OPEN -> CLOSED (recovered)")
        self.failure_count = 0

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit {self.name}: CLOSED -> OPEN (failures: {self.failure_count})")

    def _should_attempt_reset(self) -> bool:
        if self.last_failure_time is None:
            return True
        return datetime.now() > self.last_failure_time + timedelta(seconds=self.recovery_timeout)


class CancellationToken:
    """
    Allows cancellation of long-running operations.
    Critical for Cloud Run to avoid zombie processes.
    """

    def __init__(self):
        self._cancelled = False
        self._callbacks: list = []

    def cancel(self):
        self._cancelled = True
        for callback in self._callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Cancellation callback error: {e}")

    @property
    def is_cancelled(self) -> bool:
        return self._cancelled

    def on_cancel(self, callback: Callable):
        self._callbacks.append(callback)

    def throw_if_cancelled(self):
        if self._cancelled:
            raise OperationCancelledError("Operation was cancelled")


class OperationCancelledError(Exception):
    """Raised when an operation is cancelled."""
    pass


class RecursionLimitError(Exception):
    """Raised when agent call depth is exceeded."""
    pass


class AgentCallStack:
    """
    Prevents recursive agent loops by tracking call depth.
    Agent A -> Agent B -> Agent A = ERROR
    """

    MAX_DEPTH = 5

    def __init__(self):
        self._stack: list = []

    def push(self, skill_id: str):
        if len(self._stack) >= self.MAX_DEPTH:
            raise RecursionLimitError(
                f"Max agent depth ({self.MAX_DEPTH}) exceeded. "
                f"Stack: {' -> '.join(self._stack)}"
            )

        if skill_id in self._stack:
            raise RecursionLimitError(
                f"Circular dependency detected: {skill_id}. "
                f"Stack: {' -> '.join(self._stack)} -> {skill_id}"
            )

        self._stack.append(skill_id)

    def pop(self):
        if self._stack:
            self._stack.pop()

    @property
    def depth(self) -> int:
        return len(self._stack)

    @property
    def current_skill(self) -> Optional[str]:
        return self._stack[-1] if self._stack else None


# Registry of circuit breakers for different services
circuit_breakers: dict[str, CircuitBreaker] = {}


def get_circuit_breaker(service_name: str) -> CircuitBreaker:
    """
    Get or create a circuit breaker for a service.
    """
    if service_name not in circuit_breakers:
        circuit_breakers[service_name] = CircuitBreaker(name=service_name)
    return circuit_breakers[service_name]
```

---

## 1.7 Main Application Entry Point

```python
# backend/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from core.config import get_settings
from core.database import engine, Base
from core.redis_client import redis_client
from core.exceptions import RaptorflowException
from security.rate_limiter import rate_limit_middleware
from observability.health import health_router
from observability.metrics import metrics_middleware

from api.v1 import agents, skills, campaigns, moves, muse, blackbox, foundation, billing
from api.webhooks import phonepe

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    Startup: Initialize connections
    Shutdown: Clean up resources
    """
    # Startup
    logger.info("Starting Raptorflow Neural Nexus...")

    # Initialize database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Verify Redis connection
    try:
        client = await redis_client.get_client()
        await client.ping()
        logger.info("Redis connection verified")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        raise

    # Load skill registry
    from skills.registry import skill_registry
    await skill_registry.load_all_skills()
    logger.info(f"Loaded {len(skill_registry.skills)} skills")

    yield

    # Shutdown
    logger.info("Shutting down Raptorflow Neural Nexus...")
    await redis_client.close()
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Cognitive Operating System for Marketing",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Metrics middleware
app.middleware("http")(metrics_middleware)


# Global exception handler
@app.exception_handler(RaptorflowException)
async def raptorflow_exception_handler(request: Request, exc: RaptorflowException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )


# Include routers
app.include_router(health_router, tags=["Health"])

# API v1 routes
app.include_router(agents.router, prefix=f"{settings.API_PREFIX}/agents", tags=["Agents"])
app.include_router(skills.router, prefix=f"{settings.API_PREFIX}/skills", tags=["Skills"])
app.include_router(campaigns.router, prefix=f"{settings.API_PREFIX}/campaigns", tags=["Campaigns"])
app.include_router(moves.router, prefix=f"{settings.API_PREFIX}/moves", tags=["Moves"])
app.include_router(muse.router, prefix=f"{settings.API_PREFIX}/muse", tags=["Muse"])
app.include_router(blackbox.router, prefix=f"{settings.API_PREFIX}/blackbox", tags=["BlackBox"])
app.include_router(foundation.router, prefix=f"{settings.API_PREFIX}/foundation", tags=["Foundation"])
app.include_router(billing.router, prefix=f"{settings.API_PREFIX}/billing", tags=["Billing"])

# Webhooks
app.include_router(phonepe.router, prefix="/webhooks/phonepe", tags=["Webhooks"])


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational"
    }
```
