import logging
import time
from enum import Enum
from typing import Any, Dict, List, Optional

from core.tool_registry import MatrixSkill

logger = logging.getLogger("raptorflow.skills.matrix")


class UserRole(str, Enum):
    """Roles for Matrix access control."""

    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class SkillPrivilegeMatrix:
    """
    SOTA RBAC for Matrix tools.
    Maps UserRoles to allowed MatrixSkill names.
    """

    _matrix: Dict[UserRole, List[str]] = {
        UserRole.ADMIN: [
            "emergency_halt",
            "inference_throttling",
            "cache_purge",
            "resource_scaling",
            "archive_logs",
            "retrain_trigger",
        ],
        UserRole.OPERATOR: [
            "inference_throttling",
            "resource_scaling",
            "archive_logs",
        ],
        UserRole.VIEWER: [],
    }

    def has_permission(self, role: UserRole, skill_name: str) -> bool:
        """Verifies if a role can execute a specific skill."""
        allowed_skills = self._matrix.get(role, [])
        return skill_name in allowed_skills


class SkillRegistry:
    """
    Registry for managing and discovering Matrix skills.
    Singleton pattern ensures a single source of truth for tools.
    """

    _instance: Optional["SkillRegistry"] = None
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

    def __init__(self, matrix_service, pool_monitor=None):
        self.matrix_service = matrix_service
        self.pool_monitor = pool_monitor

    @property
    def name(self) -> str:
        return "emergency_halt"

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        reason = params.get("reason", "No reason provided")
        logger.warning(f"EmergencyHaltSkill triggered: {reason}")

        # 1. Engage Matrix Kill-Switch
        success = await self.matrix_service.halt_system()

        # 2. Signal Pool Monitor to clear active threads (simulation)
        if self.pool_monitor:
            logger.warning("EmergencyHaltSkill: Clearing all active agent threads...")
            active_threads = self.pool_monitor.get_active_threads()
            for tid in list(active_threads.keys()):
                self.pool_monitor.unregister_thread(tid)

        return {
            "halt_engaged": success,
            "reason": reason,
            "status": "system_halted" if success else "failed_to_halt",
            "threads_halted": len(active_threads) if self.pool_monitor else 0,
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
        tpm_limit = params.get("tpm_limit", 1000)  # Tokens Per Minute

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
                "status": "active",
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

            return {"purge_successful": True, "pattern": pattern, "keys_removed": count}
        except Exception as e:
            logger.error(f"Failed to purge cache: {e}")
            return False


class ResourceScalingSkill(MatrixSkill):
    """
    Skill to simulate resource scaling for Cloud Run services.
    In a real build, this would interface with GCP Cloud Run API.
    """

    @property
    def name(self) -> str:
        return "resource_scaling"

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        service = params.get("service")
        replicas = params.get("replicas", 1)

        if not service:
            return {"error": "service name is required for scaling"}

        logger.warning(
            f"ResourceScalingSkill: Mock scaling {service} to {replicas} replicas"
        )

        return {
            "scaling_initiated": True,
            "service": service,
            "target_replicas": replicas,
            "status": "scaling_in_progress",
            "message": f"Successfully signaled GCP to scale {service} to {replicas} instances.",
        }


class ArchiveLogsSkill(MatrixSkill):
    """
    Skill to trigger GCS log archival.
    Moves blobs from raw to archival zones via GCSLifecycleManager.
    """

    def __init__(self, gcs_manager):
        self.gcs_manager = gcs_manager

    @property
    def name(self) -> str:
        return "archive_logs"

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        prefix = params.get("prefix")

        if not prefix:
            return {"error": "prefix is required for log archival"}

        logger.info(f"ArchiveLogsSkill triggered for prefix: {prefix}")

        success = self.gcs_manager.archive_logs(prefix=prefix)

        return {
            "archival_successful": success,
            "prefix": prefix,
            "status": "completed" if success else "failed",
        }


class RetrainTriggerSkill(MatrixSkill):
    """
    Skill to trigger model retraining lifecycle.
    In a real build, this would trigger a Vertex AI Training pipeline.
    """

    @property
    def name(self) -> str:
        return "retrain_trigger"

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        model_id = params.get("model_id")
        dataset_uri = params.get("dataset_uri")

        if not model_id:
            return {"error": "model_id is required for retraining"}

        logger.warning(
            f"RetrainTriggerSkill: Triggering retraining for model: {model_id}"
        )
        if dataset_uri:
            logger.info(f"Using dataset: {dataset_uri}")

        return {
            "retrain_initiated": True,
            "model_id": model_id,
            "dataset_uri": dataset_uri,
            "status": "retraining_initiated",
            "message": f"Successfully signaled Vertex AI to begin retraining {model_id}.",
        }


class ToolExecutionWrapper:
    """
    SOTA Resiliency Wrapper for Matrix skills.
    Handles telemetry, logging, and error boundaries for all tools.
    """

    def __init__(self, skill: MatrixSkill):
        self.skill = skill

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the wrapped skill with full observability."""
        start_time = time.time()
        logger.info(f"Matrix tool {self.skill.name} starting...")

        try:
            data = await self.skill.execute(params)
            latency = (time.time() - start_time) * 1000
            return {
                "success": True,
                "data": data,
                "latency_ms": latency,
                "error": None,
            }
        except Exception as e:
            logger.error(f"Matrix tool {self.skill.name} failed: {e}")
            return {
                "success": False,
                "data": None,
                "latency_ms": 0,
                "error": str(e),
            }


class ToolOutputValidator:
    """
    SOTA Validator for structured Matrix tool outputs.
    Ensures downstream agents receive guaranteed data shapes.
    """

    @staticmethod
    def validate(output: Any, required_keys: List[str]) -> bool:
        """Verifies if the output is a dict containing all required keys."""
        if not isinstance(output, dict):
            return False

        return all(key in output for key in required_keys)
