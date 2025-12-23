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
