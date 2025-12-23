import uuid
from typing import Dict, Any
from backend.models.telemetry import TelemetryEvent, TelemetryEventType


class ModelServer:
    """Centralized inference server for logging model metadata."""

    def __init__(self, matrix_service):
        self.matrix_service = matrix_service

    async def log_inference(self, source: str, metadata: Dict[str, Any]) -> bool:
        """Logs metadata for an inference call to the Matrix telemetry stream."""
        event = TelemetryEvent(
            event_id=str(uuid.uuid4()),
            event_type=TelemetryEventType.INFERENCE_END,
            source=source,
            payload=metadata
        )
        return await self.matrix_service.emit_event(event)
