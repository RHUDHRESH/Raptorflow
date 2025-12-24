import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("raptorflow.agents.pool_monitor")


class AgentPoolMonitor:
    """
    Singleton monitor for real-time tracking of active agent threads.
    Provides telemetry for the Matrix dashboard on system-wide agent activity.
    """

    _instance: Optional["AgentPoolMonitor"] = None
    _active_threads: Dict[str, Dict[str, Any]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentPoolMonitor, cls).__new__(cls)
        return cls._instance

    def register_thread(
        self, thread_id: str, agent_type: str, metadata: Optional[Dict[str, Any]] = None
    ):
        """Registers a new active agent thread."""
        logger.info(f"Registering agent thread: {thread_id} ({agent_type})")
        self._active_threads[thread_id] = {
            "agent_type": agent_type,
            "metadata": metadata or {},
            "status": "active",
        }

    def unregister_thread(self, thread_id: str):
        """Unregisters an agent thread when it completes or fails."""
        if thread_id in self._active_threads:
            logger.info(f"Unregistering agent thread: {thread_id}")
            del self._active_threads[thread_id]

    def get_active_thread_count(self) -> int:
        """Returns the current number of active agent threads."""
        return len(self._active_threads)

    def get_active_threads(self) -> Dict[str, Dict[str, Any]]:
        """Returns details of all currently active agent threads."""
        return self._active_threads.copy()
