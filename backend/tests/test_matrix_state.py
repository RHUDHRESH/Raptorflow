from typing import get_type_hints

import pytest
from langchain_core.messages import BaseMessage

from agents.supervisor import MatrixState


def test_matrix_state_structure():
    """Verify the structure of MatrixState TypedDict."""
    hints = get_type_hints(MatrixState)
    assert "messages" in hints
    assert "next" in hints
    assert "instructions" in hints
    assert "system_health" in hints


def test_matrix_state_defaults():
    """Verify that we can initialize a dict matching MatrixState."""
    state: MatrixState = {
        "messages": [],
        "next": "START",
        "instructions": "",
        "system_health": {"status": "ok"},
    }
    assert state["next"] == "START"
    assert len(state["messages"]) == 0
