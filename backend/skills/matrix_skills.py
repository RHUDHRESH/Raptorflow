import abc
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("raptorflow.skills.matrix")

class MatrixSkill(abc.ABC):
    """
    Base class for all Matrix specialized skills.
    Skills are deterministic tools that agents can use to manipulate system state.
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """The unique name of the skill."""
        pass

    @abc.abstractmethod
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the skill logic."""
        pass


class SkillRegistry:
    """
    Registry for managing and discovering Matrix skills.
    Singleton pattern ensures a single source of truth for tools.
    """
    _instance: Optional['SkillRegistry'] = None
    _skills: Dict[str, MatrixSkill] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SkillRegistry, cls).__new__(cls)
        return cls._instance

    def register(self, skill: MatrixSkill):
        """Registers a new skill in the system."""
        logger.info(f"Registering Matrix skill: {skill.name}")
        self._skills[skill.name] = skill

    def get(self, name: str) -> Optional[MatrixSkill]:
        """Retrieves a skill by name."""
        return self._skills.get(name)

    def list_skills(self) -> List[str]:
        """Returns a list of all registered skill names."""
        return list(self._skills.keys())


class EmergencyHaltSkill(MatrixSkill):
    """
    Skill to engage the global system kill-switch.
    """

    def __init__(self, matrix_service):
        self.matrix_service = matrix_service

    @property
    def name(self) -> str:
        return "emergency_halt"

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        reason = params.get("reason", "No reason provided")
        logger.warning(f"EmergencyHaltSkill triggered: {reason}")
        
        success = await self.matrix_service.halt_system()
        
        return {
            "halt_engaged": success,
            "reason": reason,
            "status": "system_halted" if success else "failed_to_halt"
        }


class InferenceThrottlingSkill(MatrixSkill):
    """
    Skill to manage agent-specific rate limits and throttling.
    Updates throttle keys in Upstash Redis to control inference flow.
    """

    def __init__(self, redis_client):
        self.redis = redis_client

    @property
    def name(self) -> str:
        return "inference_throttling"

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        agent_id = params.get("agent_id")
        tpm_limit = params.get("tpm_limit", 1000) # Tokens Per Minute
        
        if not agent_id:
            return {"error": "agent_id is required"}
            
        logger.info(f"Applying throttling to {agent_id}: {tpm_limit} TPM")
        
        # Persist throttle setting in Redis
        try:
            key = f"throttle:{agent_id}"
            await self.redis.set(key, tpm_limit)
            
            return {
                "throttling_applied": True,
                "agent_id": agent_id,
                "tpm_limit": tpm_limit,
                "status": "active"
            }
        except Exception as e:
            logger.error(f"Failed to apply throttling: {e}")
            return False


class CachePurgeSkill(MatrixSkill):
    """
    Skill to manually clear cache keys or patterns from Upstash Redis.
    """

    def __init__(self, redis_client):
        self.redis = redis_client

    @property
    def name(self) -> str:
        return "cache_purge"

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        pattern = params.get("pattern", "*")
        logger.warning(f"CachePurgeSkill triggered for pattern: {pattern}")
        
        try:
            # In a real build with a rich redis client, we'd list and delete.
            # Upstash http client has a simpler delete.
            # For now we simulate/implement basic delete.
            count = await self.redis.delete(pattern)
            
            return {
                "purge_successful": True,
                "pattern": pattern,
                "keys_removed": count
            }
        except Exception as e:
            logger.error(f"Failed to purge cache: {e}")
            return False
