"""
Validation utilities for Raptorflow agents.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def get_validator():
    """Get validator instance."""
    return Validator()


class Validator:
    """Validator for agent operations."""

    def __init__(self):
        self.rules = []

    def validate_input(self, data: Any) -> bool:
        """Validate input data."""
        # Simple implementation - can be extended
        return True

    def validate_output(self, data: Any) -> bool:
        """Validate output data."""
        return True

    def add_rule(self, rule_func):
        """Add a validation rule."""
        self.rules.append(rule_func)
