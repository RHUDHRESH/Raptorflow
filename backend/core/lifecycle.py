from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from models.cognitive import CognitiveStatus, LifecycleState
from services.telemetry import get_telemetry


def _normalize_state(value: Any) -> str:
    if isinstance(value, Enum):
        return value.value
    return str(value)


def apply_lifecycle_transition(
    state: Dict[str, Any],
    next_status: CognitiveStatus | str,
    actor: str,
    updates: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    updates = updates or {}
    previous = (
        state.get("lifecycle_state") or state.get("status") or CognitiveStatus.IDLE
    )
    previous_value = _normalize_state(previous)
    status = (
        next_status
        if isinstance(next_status, CognitiveStatus)
        else CognitiveStatus(str(next_status))
    )
    next_state = LifecycleState(status.value)

    transition = None
    if previous_value != next_state.value:
        transition = {
            "from": previous_value,
            "to": next_state.value,
            "actor": actor,
            "timestamp": datetime.now().isoformat(),
        }
        get_telemetry().capture_state_transition(
            actor=actor,
            from_state=previous_value,
            to_state=next_state.value,
        )

    merged = {**updates, "status": status, "lifecycle_state": next_state}
    if transition:
        merged["lifecycle_transitions"] = [transition]
    return merged
