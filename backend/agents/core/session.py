"""
Session management for Raptorflow agents.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def get_session_manager():
    """Get session manager instance."""
    return SessionManager()


class SessionManager:
    """Session manager for agent operations."""

    def __init__(self):
        self.sessions = {}

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID."""
        return self.sessions.get(session_id)

    def create_session(self, session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new session."""
        self.sessions[session_id] = data
        return data

    def update_session(
        self, session_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update an existing session."""
        if session_id in self.sessions:
            self.sessions[session_id].update(data)
            return self.sessions[session_id]
        return None

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
