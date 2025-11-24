"""
Agent Registry for Service Discovery and Load Balancing

Agents register their capabilities, and tasks discover agents dynamically.
Load balancing ensures work is distributed to least-loaded agents.
"""

import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import redis


class AgentCapability(BaseModel):
    """Agent registration record"""

    agent_id: str
    agent_name: str
    capabilities: List[str]  # ["content_generation", "email", "tone_professional"]
    current_load: int = 0
    max_concurrent: int = 5
    avg_latency_ms: float = 0.0
    success_rate: float = 0.95
    last_heartbeat: datetime = None
    version: str = "1.0"
    pod: str = ""  # Sector pod: "strategy", "creation", "signals", "risk"

    def __init__(self, **data):
        super().__init__(**data)
        if not self.last_heartbeat:
            self.last_heartbeat = datetime.utcnow()

    def to_json(self) -> str:
        return json.dumps(self.model_dump(mode='json', exclude_none=True))

    @classmethod
    def from_json(cls, data: str) -> 'AgentCapability':
        return cls(**json.loads(data))

    @property
    def load_percentage(self) -> float:
        """Current load as percentage of max capacity"""
        if self.max_concurrent == 0:
            return 0.0
        return (self.current_load / self.max_concurrent) * 100

    @property
    def is_available(self) -> bool:
        """Check if agent is available (not at max capacity)"""
        return self.current_load < self.max_concurrent


class AgentRegistry:
    """Dynamic agent discovery and load balancing"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.heartbeat_ttl = 120  # 2 minutes

    def register(self, capability: AgentCapability) -> bool:
        """Register agent capabilities"""

        key = f"agent:{capability.agent_id}"

        # Store agent record
        self.redis.setex(
            key,
            self.heartbeat_ttl,
            capability.to_json()
        )

        # Index by capability
        for cap in capability.capabilities:
            self.redis.sadd(f"capability:{cap}", capability.agent_id)

        # Index by pod
        if capability.pod:
            self.redis.sadd(f"pod:{capability.pod}", capability.agent_id)

        return True

    def heartbeat(self, agent_id: str) -> bool:
        """Refresh agent's heartbeat (keep it registered)"""

        key = f"agent:{agent_id}"
        data = self.redis.get(key)

        if data:
            capability = AgentCapability.from_json(data.decode('utf-8'))
            capability.last_heartbeat = datetime.utcnow()

            self.redis.setex(
                key,
                self.heartbeat_ttl,
                capability.to_json()
            )
            return True

        return False

    def unregister(self, agent_id: str) -> bool:
        """Unregister agent"""

        key = f"agent:{agent_id}"
        data = self.redis.get(key)

        if data:
            capability = AgentCapability.from_json(data.decode('utf-8'))

            # Remove from capability sets
            for cap in capability.capabilities:
                self.redis.srem(f"capability:{cap}", agent_id)

            # Remove from pod set
            if capability.pod:
                self.redis.srem(f"pod:{capability.pod}", agent_id)

            # Delete main record
            self.redis.delete(key)
            return True

        return False

    def get_agent(self, agent_id: str) -> Optional[AgentCapability]:
        """Get agent record by ID"""

        key = f"agent:{agent_id}"
        data = self.redis.get(key)

        if data:
            return AgentCapability.from_json(data.decode('utf-8'))

        return None

    def find_agents(
        self,
        required_capabilities: List[str],
        pod: Optional[str] = None,
        available_only: bool = True
    ) -> List[AgentCapability]:
        """
        Find agents matching required capabilities

        Args:
            required_capabilities: ALL of these must be present
            pod: Filter by pod/sector
            available_only: Only return agents not at max capacity

        Returns:
            Sorted by load (least busy first), then by success rate (highest first)
        """

        # Find intersection of all capability sets
        if not required_capabilities:
            agent_ids = self.redis.keys("agent:*")
            agent_ids = [id.decode('utf-8').split(":")[-1] for id in agent_ids]
        else:
            sets = [f"capability:{cap}" for cap in required_capabilities]
            agent_ids_bytes = self.redis.sinter(*sets)
            agent_ids = [id.decode('utf-8') for id in agent_ids_bytes]

        # Filter by pod if specified
        if pod:
            pod_members = self.redis.smembers(f"pod:{pod}")
            pod_members = {m.decode('utf-8') if isinstance(m, bytes) else m for m in pod_members}
            agent_ids = [id for id in agent_ids if id in pod_members]

        # Fetch agent records
        agents = []
        for agent_id in agent_ids:
            agent = self.get_agent(agent_id)
            if agent:
                if available_only and not agent.is_available:
                    continue
                agents.append(agent)

        # Sort by load (ascending), then success_rate (descending)
        agents.sort(
            key=lambda a: (a.load_percentage, -a.success_rate)
        )

        return agents

    def find_best_agent(
        self,
        required_capabilities: List[str],
        pod: Optional[str] = None
    ) -> Optional[AgentCapability]:
        """Find single best agent for task"""

        agents = self.find_agents(required_capabilities, pod, available_only=True)
        return agents[0] if agents else None

    def update_load(self, agent_id: str, delta: int) -> bool:
        """Update agent's current load"""

        agent = self.get_agent(agent_id)

        if agent:
            agent.current_load = max(0, agent.current_load + delta)
            agent.last_heartbeat = datetime.utcnow()

            self.register(agent)
            return True

        return False

    def update_metrics(
        self,
        agent_id: str,
        latency_ms: float,
        success: bool
    ) -> bool:
        """Update agent's performance metrics after task execution"""

        agent = self.get_agent(agent_id)

        if agent:
            # Update latency (simple moving average)
            agent.avg_latency_ms = (agent.avg_latency_ms + latency_ms) / 2

            # Update success rate (simple moving average)
            success_value = 1.0 if success else 0.0
            agent.success_rate = (agent.success_rate + success_value) / 2

            agent.last_heartbeat = datetime.utcnow()

            self.register(agent)
            return True

        return False

    def list_all_agents(self) -> List[AgentCapability]:
        """Get all registered agents"""

        keys = self.redis.keys("agent:*")
        agents = []

        for key in keys:
            data = self.redis.get(key)
            if data:
                agents.append(AgentCapability.from_json(data.decode('utf-8')))

        return agents

    def list_agents_by_pod(self, pod: str) -> List[AgentCapability]:
        """Get all agents in a pod/sector"""

        agent_ids = self.redis.smembers(f"pod:{pod}")
        agents = []

        for agent_id_bytes in agent_ids:
            agent_id = agent_id_bytes.decode('utf-8')
            agent = self.get_agent(agent_id)
            if agent:
                agents.append(agent)

        return agents

    def get_registry_stats(self) -> Dict:
        """Get overall registry statistics"""

        agents = self.list_all_agents()

        if not agents:
            return {
                "total_agents": 0,
                "total_capacity": 0,
                "total_load": 0,
                "avg_success_rate": 0.0
            }

        return {
            "total_agents": len(agents),
            "total_capacity": sum(a.max_concurrent for a in agents),
            "total_load": sum(a.current_load for a in agents),
            "avg_success_rate": sum(a.success_rate for a in agents) / len(agents),
            "available_agents": sum(1 for a in agents if a.is_available),
            "agents_by_pod": {
                pod: len(self.list_agents_by_pod(pod))
                for pod in ["strategy", "creation", "signals", "risk", "cohort_intelligence"]
            }
        }


# Example usage:
"""
from backend.messaging.agent_registry import AgentRegistry, AgentCapability

registry = AgentRegistry(redis_client)

# Agent startup - register
registry.register(AgentCapability(
    agent_id="COPY-01",
    agent_name="LyraQuill",
    capabilities=["content_generation", "copywriting", "email", "linkedin", "tone_professional"],
    current_load=0,
    max_concurrent=5,
    avg_latency_ms=2500,
    success_rate=0.94,
    pod="creation"
))

# Task needs an agent
agents = registry.find_agents(
    required_capabilities=["content_generation", "email", "tone_professional"],
    available_only=True
)

if agents:
    best_agent = agents[0]  # Least loaded agent with required skills
    registry.update_load(best_agent.agent_id, +1)
    # ... execute task ...
    registry.update_metrics(best_agent.agent_id, latency_ms=2500, success=True)
    registry.update_load(best_agent.agent_id, -1)

# Get stats
stats = registry.get_registry_stats()
print(f"Total load: {stats['total_load']}/{stats['total_capacity']}")
"""
