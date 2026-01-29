"""
Streaming utilities for real-time agent responses.
"""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

from .state import AgentState


class StreamEventType(Enum):
    """Types of streaming events."""

    START = "start"
    ROUTING = "routing"
    ROUTED = "routed"
    EXECUTING = "executing"
    PROGRESS = "progress"
    THINKING = "thinking"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    CONTENT = "content"
    ERROR = "error"
    COMPLETE = "complete"
    APPROVAL_REQUIRED = "approval_required"
    METRICS = "metrics"


@dataclass
class StreamEvent:
    """Streaming event data structure."""

    event_type: StreamEventType
    data: Dict[str, Any]
    timestamp: datetime
    session_id: str
    agent_name: Optional[str] = None
    step: Optional[str] = None
    progress: Optional[float] = None

    def to_sse_format(self) -> str:
        """Convert to Server-Sent Events format."""
        event_data = {
            "type": self.event_type.value,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
        }

        if self.agent_name:
            event_data["agent"] = self.agent_name

        if self.step:
            event_data["step"] = self.step

        if self.progress is not None:
            event_data["progress"] = self.progress

        return f"event: {self.event_type.value}\ndata: {json.dumps(event_data)}\n\n"


class StreamingResponseHandler:
    """
    Handler for streaming agent responses.

    Manages real-time streaming of agent execution progress and results.
    """

    def __init__(self):
        self.active_streams: Dict[str, asyncio.Queue] = {}
        self.stream_metadata: Dict[str, Dict[str, Any]] = {}

    async def create_stream(
        self, session_id: str, metadata: Dict[str, Any] = None
    ) -> asyncio.Queue:
        """
        Create a new stream for a session.

        Args:
            session_id: Unique session identifier
            metadata: Optional stream metadata

        Returns:
            Queue for stream events
        """
        queue = asyncio.Queue(maxsize=100)  # Limit queue size
        self.active_streams[session_id] = queue
        self.stream_metadata[session_id] = {
            "created_at": datetime.now(),
            "metadata": metadata or {},
            "events_sent": 0,
            "last_activity": datetime.now(),
        }

        return queue

    async def send_event(self, session_id: str, event: StreamEvent) -> bool:
        """
        Send an event to a stream.

        Args:
            session_id: Session identifier
            event: Event to send

        Returns:
            True if sent successfully, False if stream not found or queue full
        """
        if session_id not in self.active_streams:
            return False

        queue = self.active_streams[session_id]

        try:
            # Try to send event (non-blocking)
            queue.put_nowait(event)

            # Update metadata
            if session_id in self.stream_metadata:
                self.stream_metadata[session_id]["events_sent"] += 1
                self.stream_metadata[session_id]["last_activity"] = datetime.now()

            return True
        except asyncio.QueueFull:
            return False

    async def close_stream(self, session_id: str) -> None:
        """
        Close a stream and clean up resources.

        Args:
            session_id: Session identifier
        """
        if session_id in self.active_streams:
            # Send completion event if not already sent
            queue = self.active_streams[session_id]
            try:
                completion_event = StreamEvent(
                    event_type=StreamEventType.COMPLETE,
                    data={"message": "Stream completed"},
                    timestamp=datetime.now(),
                    session_id=session_id,
                )
                queue.put_nowait(completion_event)
            except asyncio.QueueFull:
                pass  # Queue is full, skip completion event

            # Clean up
            del self.active_streams[session_id]
            if session_id in self.stream_metadata:
                del self.stream_metadata[session_id]

    async def get_stream_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a stream.

        Args:
            session_id: Session identifier

        Returns:
            Stream metadata if found
        """
        return self.stream_metadata.get(session_id)

    def list_active_streams(self) -> List[Dict[str, Any]]:
        """
        List all active streams.

        Returns:
            List of stream information
        """
        streams = []
        for session_id, metadata in self.stream_metadata.items():
            streams.append(
                {
                    "session_id": session_id,
                    "created_at": metadata["created_at"].isoformat(),
                    "events_sent": metadata["events_sent"],
                    "last_activity": metadata["last_activity"].isoformat(),
                    "metadata": metadata["metadata"],
                    "is_active": session_id in self.active_streams,
                }
            )

        return sorted(streams, key=lambda x: x["created_at"], reverse=True)


async def stream_agent_response(
    state: AgentState, session_id: str, handler: StreamingResponseHandler
) -> AsyncGenerator[str, None]:
    """
    Stream agent response in real-time.

    Args:
        state: Agent state
        session_id: Session identifier
        handler: Streaming response handler

    Yields:
        Server-Sent Events formatted strings
    """
    try:
        # Create stream
        queue = await handler.create_stream(
            session_id,
            {
                "workspace_id": state.get("workspace_id"),
                "user_id": state.get("user_id"),
                "agent": state.get("current_agent"),
            },
        )

        # Send start event
        start_event = StreamEvent(
            event_type=StreamEventType.START,
            data={"message": "Starting agent execution"},
            timestamp=datetime.now(),
            session_id=session_id,
        )
        await handler.send_event(session_id, start_event)
        yield start_event.to_sse_format()

        # Simulate agent execution with progress updates
        # In a real implementation, this would hook into actual agent execution
        agent_name = state.get("current_agent", "unknown")

        # Routing phase
        routing_event = StreamEvent(
            event_type=StreamEventType.ROUTING,
            data={"message": "Determining best approach"},
            timestamp=datetime.now(),
            session_id=session_id,
            agent_name=agent_name,
            step="routing",
        )
        await handler.send_event(session_id, routing_event)
        yield routing_event.to_sse_format()

        await asyncio.sleep(0.5)

        routed_event = StreamEvent(
            event_type=StreamEventType.ROUTED,
            data={"agent": agent_name, "confidence": 0.85},
            timestamp=datetime.now(),
            session_id=session_id,
            agent_name=agent_name,
            step="routed",
        )
        await handler.send_event(session_id, routed_event)
        yield routed_event.to_sse_format()

        # Execution phase with progress
        execution_steps = [
            ("Analyzing request", 0.2),
            ("Gathering context", 0.4),
            ("Processing with AI", 0.6),
            ("Generating response", 0.8),
            ("Finalizing output", 1.0),
        ]

        for step_name, progress in execution_steps:
            # Progress event
            progress_event = StreamEvent(
                event_type=StreamEventType.PROGRESS,
                data={"message": step_name},
                timestamp=datetime.now(),
                session_id=session_id,
                agent_name=agent_name,
                step=step_name.lower().replace(" ", "_"),
                progress=progress * 100,
            )
            await handler.send_event(session_id, progress_event)
            yield progress_event.to_sse_format()

            # Thinking event for some steps
            if "Processing" in step_name:
                thinking_event = StreamEvent(
                    event_type=StreamEventType.THINKING,
                    data={"message": "AI model is thinking..."},
                    timestamp=datetime.now(),
                    session_id=session_id,
                    agent_name=agent_name,
                    step="thinking",
                )
                await handler.send_event(session_id, thinking_event)
                yield thinking_event.to_sse_format()

            await asyncio.sleep(0.3)

        # Content event with actual output
        output = state.get("output", "Response generated successfully")
        content_event = StreamEvent(
            event_type=StreamEventType.CONTENT,
            data={"content": output},
            timestamp=datetime.now(),
            session_id=session_id,
            agent_name=agent_name,
            step="content",
        )
        await handler.send_event(session_id, content_event)
        yield content_event.to_sse_format()

        # Metrics event
        metrics_event = StreamEvent(
            event_type=StreamEventType.METRICS,
            data={
                "tokens_used": state.get("tokens_used", 0),
                "cost_usd": state.get("cost_usd", 0.0),
                "execution_time_ms": 2500,
            },
            timestamp=datetime.now(),
            session_id=session_id,
            agent_name=agent_name,
            step="metrics",
        )
        await handler.send_event(session_id, metrics_event)
        yield metrics_event.to_sse_format()

        # Check if approval is required
        if state.get("requires_approval", False):
            approval_event = StreamEvent(
                event_type=StreamEventType.APPROVAL_REQUIRED,
                data={
                    "approval_gate_id": state.get("approval_gate_id"),
                    "risk_level": "medium",
                },
                timestamp=datetime.now(),
                session_id=session_id,
                agent_name=agent_name,
                step="approval",
            )
            await handler.send_event(session_id, approval_event)
            yield approval_event.to_sse_format()

        # Complete event
        complete_event = StreamEvent(
            event_type=StreamEventType.COMPLETE,
            data={"message": "Execution completed successfully"},
            timestamp=datetime.now(),
            session_id=session_id,
            agent_name=agent_name,
            step="complete",
            progress=100.0,
        )
        await handler.send_event(session_id, complete_event)
        yield complete_event.to_sse_format()

    except Exception as e:
        # Error event
        error_event = StreamEvent(
            event_type=StreamEventType.ERROR,
            data={"error": str(e), "message": "Execution failed"},
            timestamp=datetime.now(),
            session_id=session_id,
            agent_name=state.get("current_agent"),
            step="error",
        )
        await handler.send_event(session_id, error_event)
        yield error_event.to_sse_format()
    finally:
        # Clean up stream
        await handler.close_stream(session_id)


def format_sse_event(event_type: str, data: Dict[str, Any]) -> str:
    """
    Format data as Server-Sent Events.

    Args:
        event_type: Type of event
        data: Event data

    Returns:
        Formatted SSE string
    """
    event_data = {
        "type": event_type,
        "data": data,
        "timestamp": datetime.now().isoformat(),
    }

    return f"event: {event_type}\ndata: {json.dumps(event_data)}\n\n"


class EventStream:
    """
    Utility class for managing event streams.
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.events: List[StreamEvent] = []
        self.started_at = datetime.now()

    def add_event(
        self, event_type: StreamEventType, data: Dict[str, Any], **kwargs
    ) -> None:
        """Add an event to the stream."""
        event = StreamEvent(
            event_type=event_type,
            data=data,
            timestamp=datetime.now(),
            session_id=self.session_id,
            **kwargs,
        )
        self.events.append(event)

    def get_events(
        self, event_type: Optional[StreamEventType] = None
    ) -> List[StreamEvent]:
        """Get events, optionally filtered by type."""
        if event_type:
            return [e for e in self.events if e.event_type == event_type]
        return self.events

    def to_sse_stream(self) -> AsyncGenerator[str, None]:
        """Convert events to SSE stream."""
        for event in self.events:
            yield event.to_sse_format()

    def get_duration(self) -> float:
        """Get stream duration in seconds."""
        return (datetime.now() - self.started_at).total_seconds()

    def get_summary(self) -> Dict[str, Any]:
        """Get stream summary."""
        event_counts = {}
        for event in self.events:
            event_counts[event.event_type.value] = (
                event_counts.get(event.event_type.value, 0) + 1
            )

        return {
            "session_id": self.session_id,
            "started_at": self.started_at.isoformat(),
            "duration_seconds": self.get_duration(),
            "total_events": len(self.events),
            "event_counts": event_counts,
        }


# Global streaming handler instance
streaming_handler = StreamingResponseHandler()


# Convenience functions
async def create_stream(
    session_id: str, metadata: Dict[str, Any] = None
) -> asyncio.Queue:
    """Create a new stream."""
    return await streaming_handler.create_stream(session_id, metadata)


async def send_stream_event(
    session_id: str, event_type: StreamEventType, data: Dict[str, Any], **kwargs
) -> bool:
    """Send an event to a stream."""
    event = StreamEvent(
        event_type=event_type,
        data=data,
        timestamp=datetime.now(),
        session_id=session_id,
        **kwargs,
    )
    return await streaming_handler.send_event(session_id, event)


async def close_stream(session_id: str) -> None:
    """Close a stream."""
    await streaming_handler.close_stream(session_id)


def list_active_streams() -> List[Dict[str, Any]]:
    """List all active streams."""
    return streaming_handler.list_active_streams()
