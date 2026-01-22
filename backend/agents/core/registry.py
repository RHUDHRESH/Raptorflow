"""
AgentRegistry for Raptorflow agent system.
Manages agent registration, discovery, and lifecycle management.
"""

import asyncio
import importlib
import inspect
import json
import logging
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type

from ..base import BaseAgent
from backend.agents.config import ModelTier
from ..exceptions import RegistryError, ValidationError

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent registration status."""

    REGISTERED = "registered"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISABLED = "disabled"
    ERROR = "error"


class RegistrationType(Enum):
    """Registration types."""

    STATIC = "static"  # Registered at startup
    DYNAMIC = "dynamic"  # Registered at runtime
    DISCOVERED = "discovered"  # Auto-discovered


@dataclass
class AgentInfo:
    """Agent registration information."""

    agent_id: str
    name: str
    description: str
    agent_class: Type[BaseAgent]
    model_tier: ModelTier
    capabilities: List[str]
    tools: List[str]
    config: Dict[str, Any]
    registration_type: RegistrationType
    registered_at: datetime
    last_heartbeat: datetime
    status: AgentStatus
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    health_check_url: Optional[str] = None
    metrics_url: Optional[str] = None


@dataclass
class AgentInstance:
    """Agent instance information."""

    instance_id: str
    agent_id: str
    workspace_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    status: AgentStatus
    config: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    error_count: int = 0
    last_error: Optional[str] = None


@dataclass
class RegistryConfig:
    """Registry configuration."""

    auto_discovery_enabled: bool = True
    health_check_interval_seconds: int = 30
    instance_cleanup_interval_hours: int = 24
    max_instances_per_agent: int = 100
    registration_timeout_seconds: int = 60
    enable_metrics: bool = True
    enable_health_checks: bool = True


class AgentRegistry:
    """Registry for managing agent registration and discovery."""

    def __init__(self, config: RegistryConfig = None):
        self.config = config or RegistryConfig()

        # Agent storage
        self._agents: Dict[str, AgentInfo] = {}
        self._instances: Dict[str, AgentInstance] = {}
        self._agent_instances: Dict[str, List[str]] = defaultdict(
            list
        )  # agent_id -> instance_ids

        # Indexes
        self._capability_index: Dict[str, List[str]] = defaultdict(
            list
        )  # capability -> agent_ids
        self._tool_index: Dict[str, List[str]] = defaultdict(list)  # tool -> agent_ids
        self._tag_index: Dict[str, List[str]] = defaultdict(list)  # tag -> agent_ids

        # Event handlers
        self._event_handlers: Dict[str, List[Callable]] = defaultdict(list)

        # Locks
        self._registry_lock = asyncio.Lock()

        # Background tasks
        self._background_tasks: Set[asyncio.Task] = set()
        self._running = False

        # Statistics
        self._stats = {
            "agents_registered": 0,
            "instances_created": 0,
            "instances_destroyed": 0,
            "health_checks_performed": 0,
            "discoveries_performed": 0,
        }

        # Start background tasks
        self._start_background_tasks()

    async def register_agent(
        self,
        agent_class: Type[BaseAgent],
        config: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None,
        registration_type: RegistrationType = RegistrationType.STATIC,
    ) -> str:
        """Register an agent class."""
        async with self._registry_lock:
            # Validate agent class
            if not issubclass(agent_class, BaseAgent):
                raise ValidationError("Agent class must inherit from BaseAgent")

            # Create agent instance to get info
            try:
                agent_instance = agent_class()
            except Exception as e:
                raise RegistryError(f"Failed to instantiate agent: {e}")

            # Generate agent ID
            agent_id = self._generate_agent_id(agent_instance.name)

            # Get agent information
            agent_info = AgentInfo(
                agent_id=agent_id,
                name=agent_instance.name,
                description=agent_instance.description,
                agent_class=agent_class,
                model_tier=agent_instance.model_tier,
                capabilities=agent_instance.capabilities,
                tools=agent_instance.tools,
                config=config or {},
                registration_type=registration_type,
                registered_at=datetime.now(),
                last_heartbeat=datetime.now(),
                status=AgentStatus.REGISTERED,
                metadata=metadata or {},
                version=getattr(agent_instance, "version", "1.0.0"),
                dependencies=getattr(agent_instance, "dependencies", []),
                tags=getattr(agent_instance, "tags", []),
            )

            # Register agent
            self._agents[agent_id] = agent_info

            # Update indexes
            await self._update_indexes(agent_info)

            # Update statistics
            self._stats["agents_registered"] += 1

            # Emit event
            await self._emit_event(
                "agent_registered",
                {
                    "agent_id": agent_id,
                    "name": agent_info.name,
                    "registration_type": registration_type.value,
                },
            )

            logger.info(f"Registered agent: {agent_info.name} ({agent_id})")

            return agent_id

    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent."""
        async with self._registry_lock:
            agent_info = self._agents.get(agent_id)

            if not agent_info:
                raise RegistryError(f"Agent not found: {agent_id}")

            # Check if agent has active instances
            if agent_id in self._agent_instances and self._agent_instances[agent_id]:
                raise RegistryError(
                    f"Cannot unregister agent with active instances: {agent_id}"
                )

            # Remove from storage
            del self._agents[agent_id]

            # Remove from indexes
            await self._remove_from_indexes(agent_id)

            # Emit event
            await self._emit_event(
                "agent_unregistered", {"agent_id": agent_id, "name": agent_info.name}
            )

            logger.info(f"Unregistered agent: {agent_info.name} ({agent_id})")

            return True

    async def create_instance(
        self,
        agent_id: str,
        workspace_id: str,
        user_id: str,
        config: Dict[str, Any] = None,
    ) -> str:
        """Create an agent instance."""
        async with self._registry_lock:
            agent_info = self._agents.get(agent_id)

            if not agent_info:
                raise RegistryError(f"Agent not found: {agent_id}")

            # Check instance limit
            if (
                len(self._agent_instances[agent_id])
                >= self.config.max_instances_per_agent
            ):
                raise RegistryError(f"Maximum instances reached for agent: {agent_id}")

            # Generate instance ID
            instance_id = str(uuid.uuid4())

            # Create instance
            instance = AgentInstance(
                instance_id=instance_id,
                agent_id=agent_id,
                workspace_id=workspace_id,
                user_id=user_id,
                created_at=datetime.now(),
                last_activity=datetime.now(),
                status=AgentStatus.ACTIVE,
                config=config or {},
            )

            # Store instance
            self._instances[instance_id] = instance
            self._agent_instances[agent_id].append(instance_id)

            # Update agent status
            if agent_info.status == AgentStatus.REGISTERED:
                agent_info.status = AgentStatus.ACTIVE

            # Update statistics
            self._stats["instances_created"] += 1

            # Emit event
            await self._emit_event(
                "instance_created",
                {
                    "instance_id": instance_id,
                    "agent_id": agent_id,
                    "workspace_id": workspace_id,
                    "user_id": user_id,
                },
            )

            logger.info(f"Created instance: {instance_id} for agent {agent_info.name}")

            return instance_id

    async def destroy_instance(self, instance_id: str) -> bool:
        """Destroy an agent instance."""
        async with self._registry_lock:
            instance = self._instances.get(instance_id)

            if not instance:
                raise RegistryError(f"Instance not found: {instance_id}")

            agent_id = instance.agent_id

            # Remove from storage
            del self._instances[instance_id]
            self._agent_instances[agent_id].remove(instance_id)

            # Update agent status if no more instances
            if not self._agent_instances[agent_id]:
                agent_info = self._agents[agent_id]
                if agent_info.status == AgentStatus.ACTIVE:
                    agent_info.status = AgentStatus.REGISTERED

            # Update statistics
            self._stats["instances_destroyed"] += 1

            # Emit event
            await self._emit_event(
                "instance_destroyed", {"instance_id": instance_id, "agent_id": agent_id}
            )

            logger.info(f"Destroyed instance: {instance_id}")

            return True

    async def get_agent_info(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent information."""
        return self._agents.get(agent_id)

    async def get_instance_info(self, instance_id: str) -> Optional[AgentInstance]:
        """Get instance information."""
        return self._instances.get(instance_id)

    async def list_agents(
        self,
        status: Optional[AgentStatus] = None,
        capability: Optional[str] = None,
        tool: Optional[str] = None,
        tag: Optional[str] = None,
        model_tier: Optional[ModelTier] = None,
    ) -> List[Dict[str, Any]]:
        """List agents with optional filtering."""
        agents = []

        for agent_info in self._agents.values():
            # Apply filters
            if status and agent_info.status != status:
                continue

            if capability and capability not in agent_info.capabilities:
                continue

            if tool and tool not in agent_info.tools:
                continue

            if tag and tag not in agent_info.tags:
                continue

            if model_tier and agent_info.model_tier != model_tier:
                continue

            # Convert to dict
            agents.append(
                {
                    "agent_id": agent_info.agent_id,
                    "name": agent_info.name,
                    "description": agent_info.description,
                    "model_tier": agent_info.model_tier.value,
                    "capabilities": agent_info.capabilities,
                    "tools": agent_info.tools,
                    "status": agent_info.status.value,
                    "registered_at": agent_info.registered_at.isoformat(),
                    "last_heartbeat": agent_info.last_heartbeat.isoformat(),
                    "version": agent_info.version,
                    "tags": agent_info.tags,
                    "instance_count": len(self._agent_instances[agent_info.agent_id]),
                }
            )

        # Sort by name
        agents.sort(key=lambda a: a["name"])

        return agents

    async def list_instances(
        self,
        agent_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        status: Optional[AgentStatus] = None,
    ) -> List[Dict[str, Any]]:
        """List instances with optional filtering."""
        instances = []

        for instance_info in self._instances.values():
            # Apply filters
            if agent_id and instance_info.agent_id != agent_id:
                continue

            if workspace_id and instance_info.workspace_id != workspace_id:
                continue

            if user_id and instance_info.user_id != user_id:
                continue

            if status and instance_info.status != status:
                continue

            # Get agent name
            agent_info = self._agents.get(instance_info.agent_id)
            agent_name = agent_info.name if agent_info else "Unknown"

            # Convert to dict
            instances.append(
                {
                    "instance_id": instance_info.instance_id,
                    "agent_id": instance_info.agent_id,
                    "agent_name": agent_name,
                    "workspace_id": instance_info.workspace_id,
                    "user_id": instance_info.user_id,
                    "created_at": instance_info.created_at.isoformat(),
                    "last_activity": instance_info.last_activity.isoformat(),
                    "status": instance_info.status.value,
                    "error_count": instance_info.error_count,
                    "last_error": instance_info.last_error,
                }
            )

        # Sort by created_at (most recent first)
        instances.sort(key=lambda i: i["created_at"], reverse=True)

        return instances

    async def find_agents_by_capability(self, capability: str) -> List[str]:
        """Find agents that have a specific capability."""
        return self._capability_index.get(capability, []).copy()

    async def find_agents_by_tool(self, tool: str) -> List[str]:
        """Find agents that use a specific tool."""
        return self._tool_index.get(tool, []).copy()

    async def find_agents_by_tag(self, tag: str) -> List[str]:
        """Find agents with a specific tag."""
        return self._tag_index.get(tag, []).copy()

    async def update_agent_status(self, agent_id: str, status: AgentStatus):
        """Update agent status."""
        async with self._registry_lock:
            agent_info = self._agents.get(agent_id)

            if not agent_info:
                raise RegistryError(f"Agent not found: {agent_id}")

            old_status = agent_info.status
            agent_info.status = status
            agent_info.last_heartbeat = datetime.now()

            # Emit event
            await self._emit_event(
                "agent_status_updated",
                {
                    "agent_id": agent_id,
                    "old_status": old_status.value,
                    "new_status": status.value,
                },
            )

    async def update_instance_status(self, instance_id: str, status: AgentStatus):
        """Update instance status."""
        async with self._registry_lock:
            instance = self._instances.get(instance_id)

            if not instance:
                raise RegistryError(f"Instance not found: {instance_id}")

            old_status = instance.status
            instance.status = status
            instance.last_activity = datetime.now()

            # Emit event
            await self._emit_event(
                "instance_status_updated",
                {
                    "instance_id": instance_id,
                    "old_status": old_status.value,
                    "new_status": status.value,
                },
            )

    async def record_instance_error(self, instance_id: str, error_message: str):
        """Record an error for an instance."""
        async with self._registry_lock:
            instance = self._instances.get(instance_id)

            if not instance:
                raise RegistryError(f"Instance not found: {instance_id}")

            instance.error_count += 1
            instance.last_error = error_message
            instance.last_activity = datetime.now()

            # Auto-disable if too many errors
            if instance.error_count >= 5:
                instance.status = AgentStatus.ERROR
                await self._emit_event(
                    "instance_disabled",
                    {
                        "instance_id": instance_id,
                        "reason": "Too many errors",
                        "error_count": instance.error_count,
                    },
                )

    async def discover_agents(self, module_path: str = None):
        """Auto-discover agents in modules."""
        if not self.config.auto_discovery_enabled:
            return

        discovered_count = 0

        try:
            if module_path:
                # Discover in specific module
                discovered_count += await self._discover_in_module(module_path)
            else:
                # Discover in default locations
                default_paths = ["backend.agents.specialists", "backend.agents.general"]

                for path in default_paths:
                    try:
                        discovered_count += await self._discover_in_module(path)
                    except ImportError:
                        continue

            # Update statistics
            self._stats["discoveries_performed"] += 1

            logger.info(f"Discovered {discovered_count} agents")

        except Exception as e:
            logger.error(f"Agent discovery failed: {e}")

    async def _discover_in_module(self, module_path: str) -> int:
        """Discover agents in a specific module."""
        discovered_count = 0

        try:
            module = importlib.import_module(module_path)

            # Get all classes in module
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Check if it's an agent class
                if (
                    issubclass(obj, BaseAgent)
                    and obj != BaseAgent
                    and obj.__module__ == module.__name__
                ):

                    # Check if already registered
                    agent_id = self._generate_agent_id(
                        obj.name if hasattr(obj, "name") else name
                    )

                    if agent_id not in self._agents:
                        await self.register_agent(
                            obj, registration_type=RegistrationType.DISCOVERED
                        )
                        discovered_count += 1

        except ImportError as e:
            logger.debug(f"Module not found: {module_path} - {e}")
        except Exception as e:
            logger.error(f"Error discovering agents in {module_path}: {e}")

        return discovered_count

    async def get_registry_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        async with self._registry_lock:
            # Count by status
            status_counts = defaultdict(int)
            for agent in self._agents.values():
                status_counts[agent.status.value] += 1

            # Count by model tier
            tier_counts = defaultdict(int)
            for agent in self._agents.values():
                tier_counts[agent.model_tier.value] += 1

            # Count instances by status
            instance_status_counts = defaultdict(int)
            for instance in self._instances.values():
                instance_status_counts[instance.status.value] += 1

            return {
                "total_agents": len(self._agents),
                "total_instances": len(self._instances),
                "agent_statuses": dict(status_counts),
                "agent_tiers": dict(tier_counts),
                "instance_statuses": dict(instance_status_counts),
                "capability_index_size": len(self._capability_index),
                "tool_index_size": len(self._tool_index),
                "tag_index_size": len(self._tag_index),
                "statistics": self._stats.copy(),
            }

    async def cleanup_inactive_instances(self) -> int:
        """Clean up inactive instances."""
        async with self._registry_lock:
            cleanup_count = 0
            cutoff_time = datetime.now() - timedelta(
                hours=self.config.instance_cleanup_interval_hours
            )

            instances_to_remove = []

            for instance_id, instance in self._instances.items():
                # Remove instances inactive for too long
                if instance.last_activity < cutoff_time:
                    instances_to_remove.append(instance_id)

            # Remove instances
            for instance_id in instances_to_remove:
                await self.destroy_instance(instance_id)
                cleanup_count += 1

            logger.info(f"Cleaned up {cleanup_count} inactive instances")

            return cleanup_count

    def _generate_agent_id(self, name: str) -> str:
        """Generate agent ID from name."""
        # Convert to lowercase and replace spaces with underscores
        base_id = name.lower().replace(" ", "_").replace("-", "_")

        # Remove special characters
        import re

        base_id = re.sub(r"[^a-z0-9_]", "", base_id)

        # Ensure uniqueness
        counter = 1
        agent_id = base_id

        while agent_id in self._agents:
            agent_id = f"{base_id}_{counter}"
            counter += 1

        return agent_id

    async def _update_indexes(self, agent_info: AgentInfo):
        """Update search indexes for agent."""
        # Capability index
        for capability in agent_info.capabilities:
            if agent_info.agent_id not in self._capability_index[capability]:
                self._capability_index[capability].append(agent_info.agent_id)

        # Tool index
        for tool in agent_info.tools:
            if agent_info.agent_id not in self._tool_index[tool]:
                self._tool_index[tool].append(agent_info.agent_id)

        # Tag index
        for tag in agent_info.tags:
            if agent_info.agent_id not in self._tag_index[tag]:
                self._tag_index[tag].append(agent_info.agent_id)

    async def _remove_from_indexes(self, agent_id: str):
        """Remove agent from search indexes."""
        # Remove from capability index
        for capability, agent_ids in self._capability_index.items():
            if agent_id in agent_ids:
                agent_ids.remove(agent_id)
                if not agent_ids:
                    del self._capability_index[capability]

        # Remove from tool index
        for tool, agent_ids in self._tool_index.items():
            if agent_id in agent_ids:
                agent_ids.remove(agent_id)
                if not agent_ids:
                    del self._tool_index[tool]

        # Remove from tag index
        for tag, agent_ids in self._tag_index.items():
            if agent_id in agent_ids:
                agent_ids.remove(agent_id)
                if not agent_ids:
                    del self._tag_index[tag]

    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit registry event."""
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

        # Health check task
        if self.config.enable_health_checks:
            self._background_tasks.add(asyncio.create_task(self._health_check_loop()))

        # Cleanup task
        self._background_tasks.add(asyncio.create_task(self._cleanup_loop()))

    async def _health_check_loop(self):
        """Background health check loop."""
        while self._running:
            try:
                async with self._registry_lock:
                    # Check agent heartbeats
                    now = datetime.now()
                    timeout = timedelta(
                        seconds=self.config.health_check_interval_seconds * 3
                    )

                    for agent_id, agent_info in self._agents.items():
                        if now - agent_info.last_heartbeat > timeout:
                            if agent_info.status == AgentStatus.ACTIVE:
                                await self.update_agent_status(
                                    agent_id, AgentStatus.INACTIVE
                                )
                                await self._emit_event(
                                    "agent_timeout",
                                    {
                                        "agent_id": agent_id,
                                        "last_heartbeat": agent_info.last_heartbeat.isoformat(),
                                    },
                                )

                self._stats["health_checks_performed"] += 1

                # Sleep until next check
                await asyncio.sleep(self.config.health_check_interval_seconds)

            except Exception as e:
                logger.error(f"Health check loop failed: {e}")
                await asyncio.sleep(10)

    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while self._running:
            try:
                await self.cleanup_inactive_instances()

                # Sleep for 1 hour
                await asyncio.sleep(3600)

            except Exception as e:
                logger.error(f"Cleanup loop failed: {e}")
                await asyncio.sleep(300)  # Retry after 5 minutes

    async def stop(self):
        """Stop registry."""
        self._running = False

        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self._background_tasks, return_exceptions=True)

        self._background_tasks.clear()

        logger.info("Agent registry stopped")
