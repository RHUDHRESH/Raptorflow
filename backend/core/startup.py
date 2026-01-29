"""
Application startup module for Raptorflow backend.
Handles initialization of all services and dependencies.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from cache.redis_client import RedisClient
from database.connection import DatabaseManager

from .agents.core.dispatcher import AgentDispatcher
from .agents.core.executor import AgentExecutor
from .agents.core.gateway import AgentGateway
from .agents.core.memory import AgentMemoryManager
from .agents.core.metrics import AgentMetricsCollector
from .agents.core.monitor import AgentMonitor
from .agents.core.orchestrator import AgentOrchestrator
from .agents.core.registry import AgentRegistry
from .agents.core.state import AgentStateManager
from .llm.vertex_client import VertexAIClient

logger = logging.getLogger(__name__)


class StartupManager:
    """Manages application startup and initialization."""

    def __init__(self):
        self.db_manager: Optional[DatabaseManager] = None
        self.redis_client: Optional[RedisClient] = None
        self.vertex_client: Optional[VertexAIClient] = None
        self.registry: Optional[AgentRegistry] = None
        self.dispatcher: Optional[AgentDispatcher] = None
        self.gateway: Optional[AgentGateway] = None
        self.orchestrator: Optional[AgentOrchestrator] = None
        self.monitor: Optional[AgentMonitor] = None
        self.state_manager: Optional[AgentStateManager] = None
        self.memory_manager: Optional[AgentMemoryManager] = None
        self.executor: Optional[AgentExecutor] = None
        self.metrics: Optional[AgentMetricsCollector] = None

        self.startup_time: Optional[datetime] = None
        self.initialization_errors: list = []

    async def initialize_app(self, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Initialize all application components."""
        self.startup_time = datetime.now()
        logger.info("Starting Raptorflow backend initialization...")

        try:
            # Initialize core services
            await self._initialize_core_services(config)

            # Initialize agent system
            await self._initialize_agent_system()

            # Warm up agents
            await self._warm_up_agents()

            # Compile graphs and optimize
            await self._compile_system_graphs()

            # Verify system health
            health_status = await self._verify_system_health()

            startup_time = (datetime.now() - self.startup_time).total_seconds()

            logger.info(
                f"Raptorflow backend initialized successfully in {startup_time:.2f}s"
            )

            return {
                "status": "healthy",
                "startup_time_seconds": startup_time,
                "services_initialized": self._get_initialized_services(),
                "health_status": health_status,
                "errors": self.initialization_errors,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Application initialization failed: {e}")
            self.initialization_errors.append(str(e))

            return {
                "status": "unhealthy",
                "startup_time_seconds": (
                    datetime.now() - self.startup_time
                ).total_seconds(),
                "services_initialized": self._get_initialized_services(),
                "errors": self.initialization_errors,
                "timestamp": datetime.now().isoformat(),
            }

    async def _initialize_core_services(self, config: Dict[str, Any] = None):
        """Initialize core infrastructure services."""
        logger.info("Initializing core services...")

        # Initialize database connection
        try:
            self.db_manager = DatabaseManager(config.get("database", {}))
            await self.db_manager.connect()
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            self.initialization_errors.append(f"Database: {e}")
            raise

        # Initialize Redis cache
        try:
            self.redis_client = RedisClient(config.get("redis", {}))
            await self.redis_client.connect()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Redis initialization failed: {e}")
            self.initialization_errors.append(f"Redis: {e}")
            raise

        # Initialize Vertex AI client
        try:
            self.vertex_client = VertexAIClient(config.get("vertex_ai", {}))
            await self.vertex_client.initialize()
            logger.info("Vertex AI client initialized")
        except Exception as e:
            logger.error(f"Vertex AI initialization failed: {e}")
            self.initialization_errors.append(f"Vertex AI: {e}")
            raise

        # Initialize metrics collector
        try:
            self.metrics = AgentMetricsCollector(config.get("metrics", {}))
            await self.metrics.record_metric("system_startup", 1.0)
            logger.info("Metrics collector initialized")
        except Exception as e:
            logger.error(f"Metrics initialization failed: {e}")
            self.initialization_errors.append(f"Metrics: {e}")

    async def _initialize_agent_system(self):
        """Initialize agent system components."""
        logger.info("Initializing agent system...")

        # Initialize state manager
        try:
            self.state_manager = AgentStateManager()
            logger.info("State manager initialized")
        except Exception as e:
            logger.error(f"State manager initialization failed: {e}")
            self.initialization_errors.append(f"State Manager: {e}")
            raise

        # Initialize memory manager
        try:
            self.memory_manager = AgentMemoryManager()
            logger.info("Memory manager initialized")
        except Exception as e:
            logger.error(f"Memory manager initialization failed: {e}")
            self.initialization_errors.append(f"Memory Manager: {e}")
            raise

        # Initialize agent registry
        try:
            self.registry = AgentRegistry()
            await self.registry.discover_agents()
            logger.info(
                f"Agent registry initialized with {len(await self.registry.list_agents())} agents"
            )
        except Exception as e:
            logger.error(f"Registry initialization failed: {e}")
            self.initialization_errors.append(f"Registry: {e}")
            raise

        # Initialize dispatcher
        try:
            self.dispatcher = AgentDispatcher(self.registry, self.metrics)
            logger.info("Agent dispatcher initialized")
        except Exception as e:
            logger.error(f"Dispatcher initialization failed: {e}")
            self.initialization_errors.append(f"Dispatcher: {e}")
            raise

        # Initialize gateway
        try:
            self.gateway = AgentGateway(self.dispatcher, self.registry, self.metrics)
            logger.info("Agent gateway initialized")
        except Exception as e:
            logger.error(f"Gateway initialization failed: {e}")
            self.initialization_errors.append(f"Gateway: {e}")
            raise

        # Initialize executor
        try:
            self.executor = AgentExecutor(
                self.registry, self.state_manager, self.memory_manager, self.metrics
            )
            logger.info("Agent executor initialized")
        except Exception as e:
            logger.error(f"Executor initialization failed: {e}")
            self.initialization_errors.append(f"Executor: {e}")
            raise

        # Initialize orchestrator
        try:
            self.orchestrator = AgentOrchestrator(
                self.dispatcher,
                self.registry,
                self.state_manager,
                self.memory_manager,
                self.metrics,
            )
            logger.info("Agent orchestrator initialized")
        except Exception as e:
            logger.error(f"Orchestrator initialization failed: {e}")
            self.initialization_errors.append(f"Orchestrator: {e}")
            raise

        # Initialize monitor
        try:
            self.monitor = AgentMonitor(self.registry, self.metrics)
            await self.monitor.start_monitoring()
            logger.info("Agent monitor started")
        except Exception as e:
            logger.error(f"Monitor initialization failed: {e}")
            self.initialization_errors.append(f"Monitor: {e}")
            raise

    async def _warm_up_agents(self):
        """Warm up agents for optimal performance."""
        logger.info("Warming up agents...")

        try:
            # Get all registered agents
            agents = await self.registry.list_agents()

            warmup_tasks = []
            for agent_info in agents:
                # Create warmup task for each agent
                task = asyncio.create_task(self._warmup_agent(agent_info["agent_id"]))
                warmup_tasks.append(task)

            # Wait for all warmup tasks to complete
            results = await asyncio.gather(*warmup_tasks, return_exceptions=True)

            successful_warmups = sum(1 for r in results if not isinstance(r, Exception))
            logger.info(f"Warmed up {successful_warmups}/{len(agents)} agents")

            # Record metrics
            await self.metrics.record_metric(
                "agents_warmed_up",
                successful_warmups,
                {"total_agents": str(len(agents))},
            )

        except Exception as e:
            logger.error(f"Agent warmup failed: {e}")
            self.initialization_errors.append(f"Agent Warmup: {e}")

    async def _warmup_agent(self, agent_id: str):
        """Warm up a specific agent."""
        try:
            # Create a test execution to warm up the agent
            await self.executor.execute(
                agent_id=agent_id,
                input_data={"warmup": True},
                workspace_id="system",
                user_id="system",
                timeout_seconds=30,
            )

            logger.debug(f"Agent {agent_id} warmed up successfully")

        except Exception as e:
            logger.warning(f"Agent {agent_id} warmup failed: {e}")
            # Don't fail startup for individual agent warmup failures

    async def _compile_system_graphs(self):
        """Compile system graphs and optimize performance."""
        logger.info("Compiling system graphs...")

        try:
            # Compile agent dependency graph
            await self._compile_dependency_graph()

            # Compile workflow graphs
            await self._compile_workflow_graphs()

            # Optimize routing tables
            await self._optimize_routing_tables()

            logger.info("System graphs compiled successfully")

        except Exception as e:
            logger.error(f"Graph compilation failed: {e}")
            self.initialization_errors.append(f"Graph Compilation: {e}")

    async def _compile_dependency_graph(self):
        """Compile agent dependency graph."""
        agents = await self.registry.list_agents()

        # Build dependency matrix
        dependency_matrix = {}
        for agent in agents:
            agent_id = agent["agent_id"]
            dependencies = agent.get("dependencies", [])
            dependency_matrix[agent_id] = dependencies

        # Store in memory for quick lookup
        await self.memory_manager.store_memory(
            memory_type="semantic",
            agent_id="system",
            workspace_id="system",
            content={"dependency_matrix": dependency_matrix},
            tags=["system", "dependencies"],
        )

        logger.debug(f"Compiled dependency graph for {len(agents)} agents")

    async def _compile_workflow_graphs(self):
        """Compile workflow execution graphs."""
        # Pre-compile common workflow patterns
        common_patterns = [
            "sequential_execution",
            "parallel_execution",
            "conditional_execution",
            "error_handling",
        ]

        for pattern in common_patterns:
            await self.memory_manager.store_memory(
                memory_type="procedural",
                agent_id="system",
                workspace_id="system",
                content={"pattern": pattern, "compiled": True},
                tags=["system", "workflow", pattern],
            )

        logger.debug("Compiled workflow graphs for common patterns")

    async def _optimize_routing_tables(self):
        """Optimize agent routing tables."""
        # Build capability lookup table
        agents = await self.registry.list_agents()
        capability_lookup = {}

        for agent in agents:
            for capability in agent.get("capabilities", []):
                if capability not in capability_lookup:
                    capability_lookup[capability] = []
                capability_lookup[capability].append(agent["agent_id"])

        # Store optimized lookup table
        await self.memory_manager.store_memory(
            memory_type="semantic",
            agent_id="system",
            workspace_id="system",
            content={"capability_lookup": capability_lookup},
            tags=["system", "routing", "optimized"],
        )

        logger.debug(
            f"Optimized routing tables for {len(capability_lookup)} capabilities"
        )

    async def _verify_system_health(self) -> Dict[str, Any]:
        """Verify overall system health."""
        logger.info("Verifying system health...")

        health_status = {
            "overall": "healthy",
            "components": {},
            "timestamp": datetime.now().isoformat(),
        }

        # Check database health
        try:
            await self.db_manager.health_check()
            health_status["components"]["database"] = "healthy"
        except Exception as e:
            health_status["components"]["database"] = f"unhealthy: {e}"
            health_status["overall"] = "degraded"

        # Check Redis health
        try:
            await self.redis_client.ping()
            health_status["components"]["redis"] = "healthy"
        except Exception as e:
            health_status["components"]["redis"] = f"unhealthy: {e}"
            health_status["overall"] = "degraded"

        # Check Vertex AI health
        try:
            await self.vertex_client.health_check()
            health_status["components"]["vertex_ai"] = "healthy"
        except Exception as e:
            health_status["components"]["vertex_ai"] = f"unhealthy: {e}"
            health_status["overall"] = "degraded"

        # Check agent system health
        try:
            agent_stats = await self.registry.get_registry_statistics()
            health_status["components"]["agent_registry"] = "healthy"
            health_status["components"]["agent_count"] = agent_stats["total_agents"]
        except Exception as e:
            health_status["components"]["agent_registry"] = f"unhealthy: {e}"
            health_status["overall"] = "degraded"

        # Check monitoring health
        try:
            monitor_stats = await self.monitor.get_monitoring_summary()
            health_status["components"]["monitoring"] = "healthy"
            health_status["components"]["healthy_agents"] = monitor_stats[
                "agent_health"
            ]["healthy"]
        except Exception as e:
            health_status["components"]["monitoring"] = f"unhealthy: {e}"
            health_status["overall"] = "degraded"

        logger.info(f"System health verification completed: {health_status['overall']}")

        return health_status

    def _get_initialized_services(self) -> list:
        """Get list of successfully initialized services."""
        services = []

        if self.db_manager:
            services.append("database")
        if self.redis_client:
            services.append("redis")
        if self.vertex_client:
            services.append("vertex_ai")
        if self.metrics:
            services.append("metrics")
        if self.state_manager:
            services.append("state_manager")
        if self.memory_manager:
            services.append("memory_manager")
        if self.registry:
            services.append("agent_registry")
        if self.dispatcher:
            services.append("agent_dispatcher")
        if self.gateway:
            services.append("agent_gateway")
        if self.executor:
            services.append("agent_executor")
        if self.orchestrator:
            services.append("agent_orchestrator")
        if self.monitor:
            services.append("agent_monitor")

        return services

    async def get_startup_status(self) -> Dict[str, Any]:
        """Get current startup status."""
        return {
            "startup_time": (
                self.startup_time.isoformat() if self.startup_time else None
            ),
            "services_initialized": self._get_initialized_services(),
            "initialization_errors": self.initialization_errors,
            "is_initialized": len(self._get_initialized_services()) > 0,
        }


# Global startup manager instance
_startup_manager = StartupManager()


async def initialize_app(config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Initialize the Raptorflow application."""
    return await _startup_manager.initialize_app(config)


async def get_startup_status() -> Dict[str, Any]:
    """Get current startup status."""
    return await _startup_manager.get_startup_status()


def get_startup_manager() -> StartupManager:
    """Get the startup manager instance."""
    return _startup_manager
