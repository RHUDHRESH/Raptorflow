"""
Backward compatibility shim for move_service.

This module provides the legacy import path for move_service,
redirecting to the new modular service location.
"""

from backend.services.move.service import MoveService

# Create singleton instance for backward compatibility
move_service = MoveService()

__all__ = ["move_service", "MoveService"]
