"""
Agent Persistence for Raptorflow Backend
===================================

This module provides persistent storage for agent state and learned data
to ensure agent learning is preserved between restarts.

Features:
- Database storage for agent models and learned preferences
- Performance data persistence and trend analysis
- Agent state serialization and recovery
- Learned behavior patterns storage
- Configuration persistence across restarts
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from enum import Enum

try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False

from .base import BaseAgent
from .state import AgentState
from .exceptions import PersistenceError

logger = logging.getLogger(__name__)


class PersistenceLevel(Enum):
    """Persistence levels for agent data."""
    VOLATILE = "volatile"      # Not persisted
    SESSION = "session"          # Current session only
    PERSISTENT = "persistent"    # Across restarts
    PERMANENT = "permanent"      # Never expires


@dataclass
class AgentLearnedData:
    """Learned data from agent execution."""
    
    agent_name: str
    learned_at: datetime
    data_type: str  # preference, pattern, optimization, etc.
    data: Dict[str, Any]
    confidence: float = 0.0  # Confidence in learned data
    usage_count: int = 0
    last_used: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    persistence_level: PersistenceLevel = PersistenceLevel.SESSION


@dataclass
class AgentPerformanceProfile:
    """Performance profile for an agent."""
    
    agent_name: str
    created_at: datetime
    updated_at: datetime
    
    # Performance metrics
    avg_response_time: float = 0.0
    success_rate: float = 0.0
    error_rate: float = 0.0
    throughput_per_hour: float = 0.0
    
    # Usage patterns
    peak_hours: List[int] = field(default_factory=list)
    common_errors: List[str] = field(default_factory=list)
    optimal_concurrency: int = 1
    resource_usage: Dict[str, float] = field(default_factory=dict)
    
    # Learned optimizations
    preferred_timeout: int = 120
    optimal_batch_size: int = 1
    retry_strategy: str = "exponential_backoff"


@dataclass
class AgentPersistenceConfig:
    """Configuration for agent persistence."""
    
    enable_persistence: bool = True
    cleanup_interval: int = 3600  # 1 hour
    max_learned_data: int = 10000
    max_performance_profiles: int = 100
    data_retention_days: int = 30
    enable_compression: bool = True
    batch_size: int = 100


class AgentPersistence:
    """Persistent storage manager for agent data."""
    
    def __init__(self, config: AgentPersistenceConfig):
        self.config = config
        self.db_pool = None
        self._is_connected = False
        self._cache: Dict[str, Any] = {}
        
    async def initialize(self) -> bool:
        """Initialize persistence system."""
        if not self.config.enable_persistence:
            logger.info("Agent persistence disabled")
            return True
        
        try:
            # Initialize database connection
            if ASYNCPG_AVAILABLE:
                import os
                database_url = os.getenv("DATABASE_URL")
                if database_url and database_url.startswith("postgresql://"):
                    self.db_pool = await asyncpg.create_pool(
                        database_url,
                        min_size=1,
                        max_size=5,
                        command_timeout=30
                    )
                    self._is_connected = True
                    logger.info("Agent persistence initialized with PostgreSQL")
                    return True
            
            # Fallback to file-based persistence
            logger.warning("PostgreSQL not available, using file-based persistence")
            return await self._initialize_file_persistence()
            
        except Exception as e:
            logger.error(f"Failed to initialize agent persistence: {e}")
            return False
    
    async def _initialize_file_persistence(self) -> bool:
        """Initialize file-based persistence."""
        import os
        persist_dir = os.getenv("AGENT_PERSISTENCE_DIR", "./data/agent_persistence")
        
        # Create directory if it doesn't exist
        os.makedirs(persist_dir, exist_ok=True)
        
        logger.info(f"File-based persistence initialized at: {persist_dir}")
        return True
    
    async def store_agent_state(self, agent: BaseAgent, state: AgentState) -> bool:
        """Store agent state for recovery."""
        try:
            state_data = {
                "agent_name": agent.name,
                "state": state,
                "timestamp": datetime.now().isoformat(),
                "version": "1.0",
            }
            
            if self.db_pool:
                await self._store_in_database("agent_states", state_data)
            else:
                await self._store_in_file(f"agent_state_{agent.name}.json", state_data)
            
            logger.debug(f"Stored state for agent {agent.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store agent state for {agent.name}: {e}")
            return False
    
    async def retrieve_agent_state(self, agent_name: str) -> Optional[AgentState]:
        """Retrieve stored agent state."""
        try:
            if self.db_pool:
                data = await self._retrieve_from_database("agent_states", {"agent_name": agent_name})
            else:
                data = await self._retrieve_from_file(f"agent_state_{agent_name}.json")
            
            if data and "state" in data:
                logger.debug(f"Retrieved state for agent {agent_name}")
                return AgentState(**data["state"])
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve agent state for {agent_name}: {e}")
            return None
    
    async def store_learned_data(self, learned_data: AgentLearnedData) -> bool:
        """Store learned data from agent execution."""
        try:
            if self.db_pool:
                await self._store_in_database("learned_data", asdict(learned_data))
            else:
                await self._store_in_file(f"learned_{learned_data.agent_name}_{learned_data.data_type}.json", asdict(learned_data))
            
            logger.debug(f"Stored learned data for {learned_data.agent_name}: {learned_data.data_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store learned data: {e}")
            return False
    
    async def retrieve_learned_data(self, agent_name: str, data_type: Optional[str] = None, limit: int = 100) -> List[AgentLearnedData]:
        """Retrieve learned data for an agent."""
        try:
            if self.db_pool:
                if data_type:
                    data = await self._retrieve_from_database("learned_data", {"agent_name": agent_name, "data_type": data_type})
                else:
                    data = await self._retrieve_from_database("learned_data", {"agent_name": agent_name})
            else:
                if data_type:
                    data = await self._retrieve_from_file(f"learned_{agent_name}_{data_type}.json")
                else:
                    # Get all learned data files for agent
                    import os
                    persist_dir = os.getenv("AGENT_PERSISTENCE_DIR", "./data/agent_persistence")
                    pattern = f"learned_{agent_name}_*.json"
                    data = []
                    
                    for filename in os.listdir(persist_dir):
                        if filename.startswith(f"learned_{agent_name}_") and filename.endswith(".json"):
                            file_data = await self._retrieve_from_file(filename)
                            if file_data:
                                data.append(AgentLearnedData(**file_data))
            
            # Convert to AgentLearnedData objects
            learned_items = []
            if isinstance(data, list):
                for item in data[:limit]:
                    learned_items.append(AgentLearnedData(**item))
            elif data:
                learned_items.append(AgentLearnedData(**data))
            
            logger.debug(f"Retrieved {len(learned_items)} learned data items for {agent_name}")
            return learned_items
            
        except Exception as e:
            logger.error(f"Failed to retrieve learned data for {agent_name}: {e}")
            return []
    
    async def store_performance_profile(self, profile: AgentPerformanceProfile) -> bool:
        """Store agent performance profile."""
        try:
            profile.updated_at = datetime.now()
            
            if self.db_pool:
                await self._store_in_database("performance_profiles", asdict(profile))
            else:
                await self._store_in_file(f"performance_{profile.agent_name}.json", asdict(profile))
            
            logger.debug(f"Stored performance profile for {profile.agent_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store performance profile for {profile.agent_name}: {e}")
            return False
    
    async def retrieve_performance_profile(self, agent_name: str) -> Optional[AgentPerformanceProfile]:
        """Retrieve agent performance profile."""
        try:
            if self.db_pool:
                data = await self._retrieve_from_database("performance_profiles", {"agent_name": agent_name})
            else:
                data = await self._retrieve_from_file(f"performance_{agent_name}.json")
            
            if data:
                logger.debug(f"Retrieved performance profile for {agent_name}")
                return AgentPerformanceProfile(**data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve performance profile for {agent_name}: {e}")
            return None
    
    async def update_performance_metrics(self, agent_name: str, execution_time: float, success: bool, error: Optional[str] = None) -> None:
        """Update performance metrics for an agent."""
        try:
            profile = await self.retrieve_performance_profile(agent_name)
            if not profile:
                # Create new profile
                profile = AgentPerformanceProfile(
                    agent_name=agent_name,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
            
            # Update metrics with exponential moving average
            alpha = 0.1  # Smoothing factor
            profile.avg_response_time = (alpha * execution_time) + ((1 - alpha) * profile.avg_response_time)
            
            if success:
                profile.success_rate = (profile.success_rate * 0.9) + 0.1
                profile.error_rate = profile.error_rate * 0.9
            else:
                profile.success_rate = profile.success_rate * 0.9
                profile.error_rate = (profile.error_rate * 0.9) + 0.1
            
            # Track common errors
            if error and error not in profile.common_errors:
                profile.common_errors.append(error)
                # Keep only last 10 errors
                if len(profile.common_errors) > 10:
                    profile.common_errors = profile.common_errors[-10:]
            
            # Update peak hours
            current_hour = datetime.now().hour
            if current_hour not in profile.peak_hours:
                profile.peak_hours.append(current_hour)
                # Keep only last 24 hours
                if len(profile.peak_hours) > 24:
                    profile.peak_hours = profile.peak_hours[-24:]
            
            await self.store_performance_profile(profile)
            logger.debug(f"Updated performance metrics for {agent_name}")
            
        except Exception as e:
            logger.error(f"Failed to update performance metrics for {agent_name}: {e}")
    
    async def cleanup_expired_data(self) -> int:
        """Clean up expired data."""
        try:
            cleaned_count = 0
            cutoff_date = datetime.now() - timedelta(days=self.config.data_retention_days)
            
            if self.db_pool:
                # Clean up database
                async with self.db_pool.acquire() as conn:
                    await conn.execute(
                        "DELETE FROM learned_data WHERE created_at < $1",
                        cutoff_date
                    )
                    await conn.execute(
                        "DELETE FROM performance_profiles WHERE updated_at < $1",
                        cutoff_date
                    )
                    cleaned_count = conn.rowcount
            else:
                # Clean up files
                import os
                persist_dir = os.getenv("AGENT_PERSISTENCE_DIR", "./data/agent_persistence")
                
                for filename in os.listdir(persist_dir):
                    filepath = os.path.join(persist_dir, filename)
                    if os.path.getmtime(filepath) < cutoff_date.timestamp():
                        os.remove(filepath)
                        cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} expired persistence records")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired data: {e}")
            return 0
    
    async def _store_in_database(self, table: str, data: Dict[str, Any]) -> None:
        """Store data in PostgreSQL database."""
        if not self.db_pool:
            raise PersistenceError("Database not available")
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(f"""
                INSERT INTO {table} (data, created_at)
                VALUES ($1, $2)
                ON CONFLICT (data) DO UPDATE SET 
                    data = EXCLUDED.data, 
                    updated_at = CURRENT_TIMESTAMP
            """, json.dumps(data), datetime.now())
    
    async def _retrieve_from_database(self, table: str, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Retrieve data from PostgreSQL database."""
        if not self.db_pool:
            raise PersistenceError("Database not available")
        
        # Build query
        where_clauses = []
        params = []
        
        for key, value in filters.items():
            where_clauses.append(f"{key} = ${len(params) + 1}")
            params.append(value)
        
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(f"""
                SELECT data FROM {table} 
                WHERE {where_clause} 
                ORDER BY created_at DESC 
                LIMIT 1
            """, *params)
            
            return dict(row) if row else None
    
    async def _store_in_file(self, filename: str, data: Dict[str, Any]) -> None:
        """Store data in file."""
        import os
        persist_dir = os.getenv("AGENT_PERSISTENCE_DIR", "./data/agent_persistence")
        filepath = os.path.join(persist_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    async def _retrieve_from_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """Retrieve data from file."""
        import os
        persist_dir = os.getenv("AGENT_PERSISTENCE_DIR", "./data/agent_persistence")
        filepath = os.path.join(persist_dir, filename)
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in file: {filename}")
            return None
    
    async def get_persistence_stats(self) -> Dict[str, Any]:
        """Get persistence system statistics."""
        try:
            stats = {
                "is_connected": self._is_connected,
                "config": asdict(self.config),
                "cache_size": len(self._cache),
                "storage_type": "database" if self.db_pool else "file",
            }
            
            if self.db_pool:
                # Get database stats
                async with self.db_pool.acquire() as conn:
                    learned_count = await conn.fetchval("SELECT COUNT(*) FROM learned_data")
                    profile_count = await conn.fetchval("SELECT COUNT(*) FROM performance_profiles")
                    state_count = await conn.fetchval("SELECT COUNT(*) FROM agent_states")
                    
                    stats.update({
                        "learned_data_count": learned_count,
                        "performance_profiles_count": profile_count,
                        "agent_states_count": state_count,
                    })
            else:
                # Get file stats
                import os
                persist_dir = os.getenv("AGENT_PERSISTENCE_DIR", "./data/agent_persistence")
                
                if os.path.exists(persist_dir):
                    files = os.listdir(persist_dir)
                    learned_files = [f for f in files if f.startswith("learned_")]
                    profile_files = [f for f in files if f.startswith("performance_")]
                    state_files = [f for f in files if f.startswith("agent_state_")]
                    
                    stats.update({
                        "learned_data_count": len(learned_files),
                        "performance_profiles_count": len(profile_files),
                        "agent_states_count": len(state_files),
                    })
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get persistence stats: {e}")
            return {"error": str(e)}


# Global persistence instance
_agent_persistence: Optional[AgentPersistence] = None


def get_agent_persistence(config: Optional[AgentPersistenceConfig] = None) -> AgentPersistence:
    """Get or create agent persistence instance."""
    global _agent_persistence
    if _agent_persistence is None:
        _agent_persistence = AgentPersistence(config or AgentPersistenceConfig())
    return _agent_persistence


async def initialize_agent_persistence() -> bool:
    """Initialize global agent persistence."""
    persistence = get_agent_persistence()
    return await persistence.initialize()


# Convenience functions for backward compatibility
async def store_agent_state(agent: BaseAgent, state: AgentState) -> bool:
    """Store agent state for recovery."""
    persistence = get_agent_persistence()
    return await persistence.store_agent_state(agent, state)


async def retrieve_agent_state(agent_name: str) -> Optional[AgentState]:
    """Retrieve stored agent state."""
    persistence = get_agent_persistence()
    return await persistence.retrieve_agent_state(agent_name)


async def store_learned_data(learned_data: AgentLearnedData) -> bool:
    """Store learned data from agent execution."""
    persistence = get_agent_persistence()
    return await persistence.store_learned_data(learned_data)


async def retrieve_learned_data(agent_name: str, data_type: Optional[str] = None, limit: int = 100) -> List[AgentLearnedData]:
    """Retrieve learned data for an agent."""
    persistence = get_agent_persistence()
    return await persistence.retrieve_learned_data(agent_name, data_type, limit)


async def update_performance_metrics(agent_name: str, execution_time: float, success: bool, error: Optional[str] = None) -> None:
    """Update performance metrics for an agent."""
    persistence = get_agent_persistence()
    return await persistence.update_performance_metrics(agent_name, execution_time, success, error)


async def get_persistence_stats() -> Dict[str, Any]:
    """Get persistence system statistics."""
    persistence = get_agent_persistence()
    return await persistence.get_persistence_stats()
