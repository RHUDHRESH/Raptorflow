"""
Agent state management and context classes with persistence.
"""

import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict

try:
    import redis
except ImportError:
    redis = None


class AgentState(TypedDict):
    """Main agent state for LangGraph."""

    # Core identification
    messages: List[Dict[str, Any]]  # LangChain message format
    workspace_id: str
    user_id: str
    session_id: str

    # Agent execution
    current_agent: Optional[str]
    routing_path: List[str]

    # Memory and context
    memory_context: Dict[str, Any]
    foundation_summary: Optional[str]
    brand_voice: Optional[str]
    active_icps: List[Dict[str, Any]]

    # Workflow state
    pending_approval: bool
    approval_gate_id: Optional[str]

    # Results
    output: Optional[Any]
    error: Optional[str]

    # Usage tracking
    tokens_used: int
    cost_usd: float

    # Metadata
    created_at: datetime
    updated_at: datetime


@dataclass
class WorkspaceContext:
    """Context for a specific workspace."""

    workspace_id: str
    user_id: str

    # Foundation data
    foundation_summary: Optional[str] = None
    brand_voice: Optional[str] = None
    messaging_guardrails: List[str] = None

    # ICP data
    active_icps: List[Dict[str, Any]] = None
    primary_icp: Optional[Dict[str, Any]] = None

    # Campaign and move data
    active_moves: List[Dict[str, Any]] = None
    active_campaigns: List[Dict[str, Any]] = None

    # User preferences
    preferences: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.messaging_guardrails is None:
            self.messaging_guardrails = []
        if self.active_icps is None:
            self.active_icps = []
        if self.active_moves is None:
            self.active_moves = []
        if self.active_campaigns is None:
            self.active_campaigns = []
        if self.preferences is None:
            self.preferences = {}


@dataclass
class ExecutionTrace:
    """Trace of agent execution for debugging."""

    session_id: str
    agent_name: str
    start_time: datetime
    end_time: Optional[datetime] = None

    # Execution details
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Any] = None
    error: Optional[str] = None

    # Performance metrics
    tokens_used: int = 0
    cost_usd: float = 0.0
    latency_ms: Optional[int] = None

    # Routing information
    routing_path: List[str] = None
    tools_used: List[str] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.routing_path is None:
            self.routing_path = []
        if self.tools_used is None:
            self.tools_used = []


def create_initial_state(
    workspace_id: str, user_id: str, session_id: Optional[str] = None
) -> AgentState:
    """Create initial agent state."""
    if session_id is None:
        session_id = str(uuid.uuid4())

    now = datetime.now()

    return {
        "messages": [],
        "workspace_id": workspace_id,
        "user_id": user_id,
        "session_id": session_id,
        "current_agent": None,
        "routing_path": [],
        "memory_context": {},
        "foundation_summary": None,
        "brand_voice": None,
        "active_icps": [],
        "pending_approval": False,
        "approval_gate_id": None,
        "output": None,
        "error": None,
        "tokens_used": 0,
        "cost_usd": 0.0,
        "created_at": now,
        "updated_at": now,
    }


def update_state(state: AgentState, **updates) -> AgentState:
    """Update agent state with new values."""
    state.update(updates)
    state["updated_at"] = datetime.now()
    return state


def add_message(state: AgentState, role: str, content: str, **metadata) -> AgentState:
    """Add a message to the state."""
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        **metadata,
    }
    state["messages"].append(message)
    state["updated_at"] = datetime.now()
    return state


def get_last_message(
    state: AgentState, role: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Get the last message, optionally filtered by role."""
    messages = state["messages"]
    if role:
        messages = [m for m in messages if m.get("role") == role]

    return messages[-1] if messages else None


def get_recent_context(
    state: AgentState, max_messages: int = 10
) -> List[Dict[str, Any]]:
    """Get recent message context."""
    return state["messages"][-max_messages:]


def calculate_total_cost(state: AgentState) -> float:
    """Calculate total cost from all LLM calls in the state."""
    return state.get("cost_usd", 0.0)


def get_agent_summary(state: AgentState) -> Dict[str, Any]:
    """Get a summary of the agent state."""
    return {
        "session_id": state["session_id"],
        "current_agent": state["current_agent"],
        "routing_path": state["routing_path"],
        "pending_approval": state["pending_approval"],
        "has_output": state["output"] is not None,
        "has_error": state["error"] is not None,
        "message_count": len(state["messages"]),
        "tokens_used": state["tokens_used"],
        "cost_usd": state["cost_usd"],
        "duration_minutes": (datetime.now() - state["created_at"]).total_seconds() / 60,
    }


# State persistence functions
def get_redis_client():
    """Get Redis client for state persistence."""
    if not redis:
        return None

    try:
        # Try to get Redis URL from environment
        import os

        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        client = redis.from_url(redis_url, decode_responses=True)
        # Test connection
        client.ping()
        return client
    except Exception:
        return None


def persist_state(state: AgentState, ttl: int = 3600) -> bool:
    """Persist agent state to Redis."""
    try:
        client = get_redis_client()
        if not client:
            return False

        key = f"agent_state:{state['workspace_id']}:{state['user_id']}:{state['session_id']}"

        # Convert datetime objects to strings for JSON serialization
        state_copy = state.copy()
        state_copy["created_at"] = state["created_at"].isoformat()
        state_copy["updated_at"] = state["updated_at"].isoformat()

        # Store as JSON
        client.setex(key, ttl, json.dumps(state_copy))
        return True
    except Exception:
        return False


def retrieve_state(
    workspace_id: str, user_id: str, session_id: str
) -> Optional[AgentState]:
    """Retrieve agent state from Redis."""
    try:
        client = get_redis_client()
        if not client:
            return None

        key = f"agent_state:{workspace_id}:{user_id}:{session_id}"
        data = client.get(key)

        if not data:
            return None

        state = json.loads(data)

        # Convert string timestamps back to datetime objects
        state["created_at"] = datetime.fromisoformat(state["created_at"])
        state["updated_at"] = datetime.fromisoformat(state["updated_at"])

        return state
    except Exception:
        return None


def clear_state(workspace_id: str, user_id: str, session_id: str) -> bool:
    """Clear agent state from Redis."""
    try:
        client = get_redis_client()
        if not client:
            return False

        key = f"agent_state:{workspace_id}:{user_id}:{session_id}"
        client.delete(key)
        return True
    except Exception:
        return False


def get_user_sessions(workspace_id: str, user_id: str) -> List[str]:
    """Get all session IDs for a user."""
    try:
        client = get_redis_client()
        if not client:
            return []

        pattern = f"agent_state:{workspace_id}:{user_id}:*"
        keys = client.keys(pattern)

        # Extract session IDs from keys
        sessions = []
        for key in keys:
            parts = key.split(":")
            if len(parts) >= 4:
                sessions.append(parts[3])

        return sessions
    except Exception:
        return []


def cleanup_expired_states() -> int:
    """Clean up expired states (called by background job)."""
    try:
        client = get_redis_client()
        if not client:
            return 0

        # Redis automatically handles TTL expiration
        # This function can be used for manual cleanup if needed
        pattern = "agent_state:*"
        keys = client.keys(pattern)

        expired_count = 0
        for key in keys:
            ttl = client.ttl(key)
            if ttl == -1:  # No TTL set, set one
                client.expire(key, 3600)  # 1 hour default
                expired_count += 1

        return expired_count
    except Exception:
        return 0


# AgentStateManager for backward compatibility
class AgentStateManager:
    """Agent state manager (backward compatibility)."""

    def __init__(self):
        self.states = {}

    def get_state(self, agent_id: str):
        """Get state for agent."""
        return self.states.get(agent_id)

    def set_state(self, agent_id: str, state: dict):
        """Set state for agent."""
        self.states[agent_id] = state

    def delete_state(self, agent_id: str):
        """Delete state for agent."""
        if agent_id in self.states:
            del self.states[agent_id]
