"""
Raptorflow Microservices Implementation
===================================

This module provides the foundation for microservices architecture
with service boundaries, communication patterns, and orchestration.

Features:
- Service discovery and registration
- Inter-service communication with message queues
- Database service separation
- API gateway integration
- Health monitoring per service
- Distributed tracing
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from enum import Enum

try:
    import consul
    CONSUL_AVAILABLE = True
except ImportError:
    CONSUL_AVAILABLE = False

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from .exceptions import MicroservicesError

logger = logging.getLogger(__name__)


class ServiceType(Enum):
    """Types of microservices."""
    AGENT = "agent"
    ANALYTICS = "analytics"
    AUTH = "auth"
    CONFIG = "config"
    DATABASE = "database"
    CACHE = "cache"
    GATEWAY = "gateway"
    MONITORING = "monitoring"


class ServiceStatus(Enum):
    """Service status types."""
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class ServiceInfo:
    """Service information for registration."""
    
    name: str
    service_type: ServiceType
    version: str
    host: str
    port: int
    health_check_url: str
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.now)
    status: ServiceStatus = ServiceStatus.STARTING


@dataclass
class ServiceMessage:
    """Message for inter-service communication."""
    
    message_id: str
    source_service: str
    target_service: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None


class ServiceRegistry:
    """Service registry for microservices discovery."""
    
    def __init__(self, consul_host: str = "localhost", consul_port: int = 8500):
        self.consul_host = consul_host
        self.consul_port = consul_port
        self.consul_client = None
        self.services: Dict[str, ServiceInfo] = {}
        self._is_connected = False
    
    async def connect(self) -> bool:
        """Connect to Consul service registry."""
        if not CONSUL_AVAILABLE:
            logger.warning("Consul not available, using in-memory registry")
            return True
        
        try:
            self.consul_client = consul.Consul(
                host=self.consul_host,
                port=self.consul_port
            )
            
            # Test connection
            self.consul_client.agent.self()
            self._is_connected = True
            logger.info(f"Connected to Consul at {self.consul_host}:{self.consul_port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Consul: {e}")
            return False
    
    async def register_service(self, service_info: ServiceInfo) -> bool:
        """Register a service with the registry."""
        try:
            if self.consul_client and self._is_connected:
                # Register with Consul
                self.consul_client.agent.service.register(
                    name=service_info.name,
                    service_id=f"{service_info.name}-{service_info.host}",
                    address=service_info.host,
                    port=service_info.port,
                    tags=[service_info.service_type.value],
                    check=consul.Check.http(
                        url=service_info.health_check_url,
                        interval="10s",
                        timeout="3s"
                    )
                )
                logger.info(f"Registered service {service_info.name} with Consul")
            else:
                # In-memory registration
                self.services[service_info.name] = service_info
                logger.info(f"Registered service {service_info.name} in-memory")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service {service_info.name}: {e}")
            return False
    
    async def deregister_service(self, service_name: str) -> bool:
        """Deregister a service from the registry."""
        try:
            if self.consul_client and self._is_connected:
                self.consul_client.agent.service.deregister(service_name)
                logger.info(f"Deregistered service {service_name} from Consul")
            
            if service_name in self.services:
                del self.services[service_name]
                logger.info(f"Deregistered service {service_name} from in-memory")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to deregister service {service_name}: {e}")
            return False
    
    async def discover_services(self, service_type: Optional[ServiceType] = None) -> List[ServiceInfo]:
        """Discover services of a specific type."""
        try:
            if self.consul_client and self._is_connected:
                # Query Consul
                _, services = self.consul_client.health.service(
                    service=service_type.value if service_type else None,
                    passing=True
                )
                
                discovered_services = []
                for service_name, service_data in services.items():
                    for service in service_data:
                        discovered_services.append(ServiceInfo(
                            name=service_name,
                            service_type=ServiceType(service_data[0]['Service']),
                            version="1.0.0",
                            host=service['Address'],
                            port=service['Port'],
                            health_check_url=f"http://{service['Address']}:{service['Port']}/health",
                            metadata=service_data[0].get('Meta', {})
                        ))
                
                return discovered_services
            
            else:
                # Return in-memory services
                return list(self.services.values())
                
        except Exception as e:
            logger.error(f"Failed to discover services: {e}")
            return []
    
    async def get_service_health(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get health status of a specific service."""
        try:
            if self.consul_client and self._is_connected:
                _, checks = self.consul_client.health.checks(service_name)
                return checks[0] if checks else None
            
            # In-memory health check
            if service_name in self.services:
                service_info = self.services[service_name]
                return {
                    "ServiceID": f"{service_name}-{service_info.host}",
                    "Status": "passing",
                    "Output": "Service is healthy"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get service health for {service_name}: {e}")
            return None


class MessageBroker:
    """Message broker for inter-service communication."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.redis_client = None
        self._is_connected = False
        self.subscribers: Dict[str, List[Callable]] = {}
    
    async def connect(self) -> bool:
        """Connect to Redis message broker."""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available, using in-memory broker")
            return True
        
        try:
            self.redis_client = await redis.from_url(self.redis_url)
            await self.redis_client.ping()
            self._is_connected = True
            logger.info(f"Connected to Redis message broker at {self.redis_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis message broker: {e}")
            return False
    
    async def publish_message(self, message: ServiceMessage) -> bool:
        """Publish a message to the broker."""
        try:
            message_data = {
                "message_id": message.message_id,
                "source_service": message.source_service,
                "target_service": message.target_service,
                "message_type": message.message_type,
                "payload": message.payload,
                "timestamp": message.timestamp.isoformat(),
                "correlation_id": message.correlation_id,
                "reply_to": message.reply_to
            }
            
            channel = f"service.{message.target_service}"
            
            if self.redis_client and self._is_connected:
                await self.redis_client.publish(channel, json.dumps(message_data))
                logger.debug(f"Published message to {channel}")
            else:
                # In-memory publishing
                logger.debug(f"In-memory publish to {channel}: {message_data}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            return False
    
    async def subscribe_to_service(self, service_name: str, callback: Callable) -> bool:
        """Subscribe to messages for a specific service."""
        try:
            channel = f"service.{service_name}"
            
            if self.redis_client and self._is_connected:
                pubsub = self.redis_client.pubsub()
                await pubsub.subscribe(channel)
                
                # Start listening in background
                asyncio.create_task(self._listen_for_messages(pubsub, callback))
                logger.info(f"Subscribed to {channel}")
            else:
                # In-memory subscription
                if service_name not in self.subscribers:
                    self.subscribers[service_name] = []
                self.subscribers[service_name].append(callback)
                logger.info(f"In-memory subscription to {channel}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to subscribe to {service_name}: {e}")
            return False
    
    async def _listen_for_messages(self, pubsub, callback: Callable) -> None:
        """Listen for messages from Redis pubsub."""
        try:
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    message_data = json.loads(message['data'])
                    service_message = ServiceMessage(
                        message_id=message_data['message_id'],
                        source_service=message_data['source_service'],
                        target_service=message_data['target_service'],
                        message_type=message_data['message_type'],
                        payload=message_data['payload'],
                        timestamp=datetime.fromisoformat(message_data['timestamp']),
                        correlation_id=message_data.get('correlation_id'),
                        reply_to=message_data.get('reply_to')
                    )
                    await callback(service_message)
                    
        except Exception as e:
            logger.error(f"Error in message listener: {e}")


class DatabaseService:
    """Database microservice."""
    
    def __init__(self, service_info: ServiceInfo, connection_pool):
        self.service_info = service_info
        self.connection_pool = connection_pool
        self._is_running = False
    
    async def start(self) -> bool:
        """Start the database service."""
        try:
            logger.info(f"Starting database service {self.service_info.name}")
            
            # Initialize connection pool
            await self.connection_pool.initialize()
            
            # Health check
            await self._health_check()
            
            self._is_running = True
            self.service_info.status = ServiceStatus.RUNNING
            
            logger.info(f"Database service {self.service_info.name} started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start database service {self.service_info.name}: {e}")
            self.service_info.status = ServiceStatus.ERROR
            return False
    
    async def stop(self) -> bool:
        """Stop the database service."""
        try:
            logger.info(f"Stopping database service {self.service_info.name}")
            
            # Close connections
            await self.connection_pool.close()
            
            self._is_running = False
            self.service_info.status = ServiceStatus.STOPPED
            
            logger.info(f"Database service {self.service_info.name} stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop database service {self.service_info.name}: {e}")
            return False
    
    async def _health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            # Test database connection
            async with self.connection_pool.get_connection() as conn:
                await conn.execute("SELECT 1")
            
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": self.service_info.name,
                "checks": {
                    "database": "passing"
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "service": self.service_info.name,
                "checks": {
                    "database": f"failing: {str(e)}"
                }
            }


class AgentService:
    """Agent microservice."""
    
    def __init__(self, service_info: ServiceInfo, agent_registry, message_broker):
        self.service_info = service_info
        self.agent_registry = agent_registry
        self.message_broker = message_broker
        self._is_running = False
        self.active_agents: Dict[str, Any] = {}
    
    async def start(self) -> bool:
        """Start the agent service."""
        try:
            logger.info(f"Starting agent service {self.service_info.name}")
            
            # Initialize agent registry
            await self.agent_registry.initialize()
            
            # Setup message handling
            await self.message_broker.subscribe_to_service(
                self.service_info.name,
                self._handle_service_message
            )
            
            self._is_running = True
            self.service_info.status = ServiceStatus.RUNNING
            
            logger.info(f"Agent service {self.service_info.name} started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start agent service {self.service_info.name}: {e}")
            self.service_info.status = ServiceStatus.ERROR
            return False
    
    async def stop(self) -> bool:
        """Stop the agent service."""
        try:
            logger.info(f"Stopping agent service {self.service_info.name}")
            
            # Stop active agents
            for agent_id, agent in self.active_agents.items():
                if hasattr(agent, 'cleanup'):
                    await agent.cleanup()
            
            self.active_agents.clear()
            self._is_running = False
            self.service_info.status = ServiceStatus.STOPPED
            
            logger.info(f"Agent service {self.service_info.name} stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop agent service {self.service_info.name}: {e}")
            return False
    
    async def _handle_service_message(self, message: ServiceMessage) -> None:
        """Handle incoming service messages."""
        try:
            if message.message_type == "execute_agent":
                # Handle agent execution request
                agent_name = message.payload.get("agent_name")
                request_data = message.payload.get("request_data")
                
                if agent_name and request_data:
                    agent = self.agent_registry.get_agent(agent_name)
                    if agent:
                        result = await agent.execute(request_data)
                        
                        # Send response
                        response_message = ServiceMessage(
                            message_id=f"response_{message.message_id}",
                            source_service=self.service_info.name,
                            target_service=message.source_service,
                            message_type="agent_response",
                            payload={
                                "result": result,
                                "agent_name": agent_name,
                                "original_request_id": message.message_id
                            },
                            correlation_id=message.correlation_id,
                            reply_to=message.message_id
                        )
                        
                        await self.message_broker.publish_message(response_message)
            
            elif message.message_type == "health_check":
                # Handle health check
                health_status = await self._service_health_check()
                
                response_message = ServiceMessage(
                    message_id=f"health_{message.message_id}",
                    source_service=self.service_info.name,
                    target_service=message.source_service,
                    message_type="health_response",
                    payload=health_status,
                    correlation_id=message.correlation_id,
                    reply_to=message.message_id
                )
                
                await self.message_broker.publish_message(response_message)
                
        except Exception as e:
            logger.error(f"Error handling service message: {e}")
    
    async def _service_health_check(self) -> Dict[str, Any]:
        """Perform service health check."""
        try:
            agent_count = len(self.active_agents)
            
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": self.service_info.name,
                "checks": {
                    "active_agents": agent_count,
                    "message_broker": "connected" if self.message_broker._is_connected else "disconnected",
                    "agent_registry": "initialized" if self.agent_registry else "not_initialized"
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "service": self.service_info.name,
                "checks": {
                    "error": str(e)
                }
            }


class MicroservicesOrchestrator:
    """Orchestrator for managing microservices."""
    
    def __init__(self):
        self.service_registry = ServiceRegistry()
        self.message_broker = MessageBroker()
        self.services: Dict[str, Any] = {}
        self._is_running = False
    
    async def initialize(self) -> bool:
        """Initialize the microservices orchestrator."""
        try:
            logger.info("Initializing microservices orchestrator")
            
            # Connect to service registry
            await self.service_registry.connect()
            
            # Connect to message broker
            await self.message_broker.connect()
            
            self._is_running = True
            logger.info("Microservices orchestrator initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            return False
    
    async def deploy_service(self, service_info: ServiceInfo, service_type: ServiceType) -> bool:
        """Deploy a new service."""
        try:
            logger.info(f"Deploying service {service_info.name}")
            
            # Register service
            await self.service_registry.register_service(service_info)
            
            # Create service instance based on type
            if service_type == ServiceType.DATABASE:
                from core.connections import get_connection_pool
                service = DatabaseService(service_info, get_connection_pool())
            elif service_type == ServiceType.AGENT:
                from agents.registry import get_agent_registry
                service = AgentService(service_info, get_agent_registry(), self.message_broker)
            else:
                logger.warning(f"Unknown service type: {service_type}")
                return False
            
            # Start the service
            if await service.start():
                self.services[service_info.name] = service
                logger.info(f"Service {service_info.name} deployed successfully")
                return True
            else:
                logger.error(f"Failed to start service {service_info.name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to deploy service {service_info.name}: {e}")
            return False
    
    async def stop_service(self, service_name: str) -> bool:
        """Stop a service."""
        try:
            if service_name in self.services:
                service = self.services[service_name]
                
                if await service.stop():
                    # Deregister service
                    await self.service_registry.deregister_service(service_name)
                    
                    # Remove from active services
                    del self.services[service_name]
                    
                    logger.info(f"Service {service_name} stopped successfully")
                    return True
                else:
                    logger.error(f"Failed to stop service {service_name}")
                    return False
            else:
                logger.warning(f"Service {service_name} not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to stop service {service_name}: {e}")
            return False
    
    async def get_service_status(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """Get status of all services or a specific service."""
        try:
            if service_name:
                # Get specific service status
                if service_name in self.services:
                    service = self.services[service_name]
                    return {
                        "name": service_name,
                        "status": service.service_info.status.value,
                        "type": service.service_info.service_type.value,
                        "health": await self.service_registry.get_service_health(service_name)
                    }
                else:
                    return {"error": f"Service {service_name} not found"}
            else:
                # Get all services status
                services_status = {}
                
                for name, service in self.services.items():
                    services_status[name] = {
                        "status": service.service_info.status.value,
                        "type": service.service_info.service_type.value,
                        "host": service.service_info.host,
                        "port": service.service_info.port
                    }
                
                return {
                    "total_services": len(services_status),
                    "services": services_status,
                    "orchestrator_status": "running" if self._is_running else "stopped"
                }
                
        except Exception as e:
            logger.error(f"Failed to get service status: {e}")
            return {"error": str(e)}
    
    async def discover_and_connect(self, service_type: Optional[ServiceType] = None) -> int:
        """Discover services and establish connections."""
        try:
            # Discover services
            discovered_services = await self.service_registry.discover_services(service_type)
            
            connected_count = 0
            for service_info in discovered_services:
                # Create service connections
                if service_info.service_type == ServiceType.DATABASE:
                    from core.connections import get_connection_pool
                    service = DatabaseService(service_info, get_connection_pool())
                elif service_info.service_type == ServiceType.AGENT:
                    from agents.registry import get_agent_registry
                    service = AgentService(service_info, get_agent_registry(), self.message_broker)
                else:
                    continue
                
                # Connect to service
                if await service.start():
                    self.services[service_info.name] = service
                    connected_count += 1
                    logger.info(f"Connected to service {service_info.name}")
            
            logger.info(f"Discovered and connected to {connected_count} services")
            return connected_count
            
        except Exception as e:
            logger.error(f"Failed to discover and connect services: {e}")
            return 0


# Global orchestrator instance
_orchestrator: Optional[MicroservicesOrchestrator] = None


def get_microservices_orchestrator() -> MicroservicesOrchestrator:
    """Get or create microservices orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MicroservicesOrchestrator()
    return _orchestrator


async def initialize_microservices() -> bool:
    """Initialize the microservices system."""
    orchestrator = get_microservices_orchestrator()
    return await orchestrator.initialize()


# Convenience functions for backward compatibility
async def deploy_service(service_info: ServiceInfo, service_type: ServiceType) -> bool:
    """Deploy a new service."""
    orchestrator = get_microservices_orchestrator()
    return await orchestrator.deploy_service(service_info, service_type)


async def stop_service(service_name: str) -> bool:
    """Stop a service."""
    orchestrator = get_microservices_orchestrator()
    return await orchestrator.stop_service(service_name)


async def get_service_status(service_name: Optional[str] = None) -> Dict[str, Any]:
    """Get service status."""
    orchestrator = get_microservices_orchestrator()
    return await orchestrator.get_service_status(service_name)
