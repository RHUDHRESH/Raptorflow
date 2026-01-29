"""
Cognitive Tracer for Integration Components

Detailed tracing and debugging for cognitive processing.
Implements PROMPT 66 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import json
import time
import traceback
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .models import ExecutionPlan, PerceivedInput, ReflectionResult


class TraceLevel(Enum):
    """Trace levels for different detail levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class TraceEventType(Enum):
    """Types of trace events."""

    STAGE_START = "stage_start"
    STAGE_END = "stage_end"
    STAGE_ERROR = "stage_error"
    STEP_START = "step_start"
    STEP_END = "step_end"
    STEP_ERROR = "step_error"
    METRIC = "metric"
    LOG = "log"
    CUSTOM = "custom"


@dataclass
class TraceEvent:
    """A single trace event."""

    event_id: str
    trace_id: str
    event_type: TraceEventType
    level: TraceLevel
    timestamp: datetime
    stage: Optional[str]
    step: Optional[str]
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[int] = None
    parent_event_id: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class CognitiveTrace:
    """Complete trace for a cognitive execution."""

    trace_id: str
    execution_id: str
    workspace_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_ms: Optional[int]
    status: str
    events: List[TraceEvent] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Performance metrics
    stage_timings: Dict[str, int] = field(default_factory=dict)
    step_timings: Dict[str, int] = field(default_factory=dict)
    error_count: int = 0
    warning_count: int = 0

    # Configuration
    max_events: int = 10000
    capture_level: TraceLevel = TraceLevel.INFO


class CognitiveTracer:
    """
    Detailed tracing and debugging for cognitive processing.

    Provides comprehensive visibility into execution flow.
    """

    def __init__(self, storage_client=None, config: Dict[str, Any] = None):
        """
        Initialize the cognitive tracer.

        Args:
            storage_client: Client for persistent storage
            config: Tracing configuration
        """
        self.storage_client = storage_client

        # Configuration
        self.config = {
            "enable_tracing": True,
            "default_level": TraceLevel.INFO,
            "max_events_per_trace": 10000,
            "trace_retention_hours": 72,
            "enable_performance_tracking": True,
            "enable_error_capture": True,
            "auto_capture_exceptions": True,
        }

        if config:
            self.config.update(config)

        # Active traces
        self.active_traces: Dict[str, CognitiveTrace] = {}

        # Event hooks
        self.event_hooks: List[Callable] = []

        # Trace statistics
        self.stats = {
            "total_traces": 0,
            "total_events": 0,
            "error_events": 0,
            "warning_events": 0,
        }

    async def start_trace(
        self,
        execution_id: str,
        workspace_id: str,
        user_id: str,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """Start a new cognitive trace."""
        if not self.config["enable_tracing"]:
            return ""

        trace_id = str(uuid.uuid4())

        trace = CognitiveTrace(
            trace_id=trace_id,
            execution_id=execution_id,
            workspace_id=workspace_id,
            user_id=user_id,
            start_time=datetime.now(),
            end_time=None,
            duration_ms=None,
            status="running",
            metadata=metadata or {},
            max_events=self.config["max_events_per_trace"],
            capture_level=self.config["default_level"],
        )

        self.active_traces[trace_id] = trace
        self.stats["total_traces"] += 1

        # Record trace start event
        await self._record_event(
            trace_id=trace_id,
            event_type=TraceEventType.CUSTOM,
            level=TraceLevel.INFO,
            message="Trace started",
            data={
                "execution_id": execution_id,
                "workspace_id": workspace_id,
                "user_id": user_id,
                "metadata": metadata,
            },
        )

        return trace_id

    async def end_trace(
        self, trace_id: str, status: str = "completed", final_output: Any = None
    ) -> None:
        """End a cognitive trace."""
        trace = self.active_traces.get(trace_id)
        if not trace:
            return

        trace.end_time = datetime.now()
        trace.duration_ms = int(
            (trace.end_time - trace.start_time).total_seconds() * 1000
        )
        trace.status = status

        # Record trace end event
        await self._record_event(
            trace_id=trace_id,
            event_type=TraceEventType.CUSTOM,
            level=TraceLevel.INFO,
            message="Trace ended",
            data={
                "status": status,
                "duration_ms": trace.duration_ms,
                "final_output": str(final_output)[:500] if final_output else None,
                "events_count": len(trace.events),
                "error_count": trace.error_count,
                "warning_count": trace.warning_count,
            },
        )

        # Archive trace
        await self._archive_trace(trace)
        self.active_traces.pop(trace_id, None)

    async def trace_stage(
        self,
        trace_id: str,
        stage_name: str,
        level: TraceLevel = TraceLevel.INFO,
        message: str = None,
        data: Dict[str, Any] = None,
    ) -> str:
        """Trace a stage start."""
        if not self.config["enable_tracing"]:
            return ""

        trace = self.active_traces.get(trace_id)
        if not trace:
            return ""

        event_id = await self._record_event(
            trace_id=trace_id,
            event_type=TraceEventType.STAGE_START,
            level=level,
            stage=stage_name,
            message=message or f"Stage {stage_name} started",
            data=data or {},
        )

        return event_id

    async def trace_stage_end(
        self,
        trace_id: str,
        stage_name: str,
        event_id: str = None,
        message: str = None,
        data: Dict[str, Any] = None,
    ) -> None:
        """Trace a stage end."""
        if not self.config["enable_tracing"]:
            return

        trace = self.active_traces.get(trace_id)
        if not trace:
            return

        # Find the matching start event
        start_event = None
        if event_id:
            start_event = next(
                (e for e in trace.events if e.event_id == event_id), None
            )
        else:
            # Find the most recent start event for this stage
            start_event = next(
                (
                    e
                    for e in reversed(trace.events)
                    if e.event_type == TraceEventType.STAGE_START
                    and e.stage == stage_name
                ),
                None,
            )

        duration_ms = None
        if start_event:
            duration_ms = int(
                (datetime.now() - start_event.timestamp).total_seconds() * 1000
            )
            trace.stage_timings[stage_name] = duration_ms

        await self._record_event(
            trace_id=trace_id,
            event_type=TraceEventType.STAGE_END,
            level=TraceLevel.INFO,
            stage=stage_name,
            message=message or f"Stage {stage_name} completed",
            data=data or {},
            duration_ms=duration_ms,
            parent_event_id=start_event.event_id if start_event else None,
        )

    async def trace_step(
        self,
        trace_id: str,
        step_id: str,
        step_name: str,
        level: TraceLevel = TraceLevel.INFO,
        message: str = None,
        data: Dict[str, Any] = None,
    ) -> str:
        """Trace a step start."""
        if not self.config["enable_tracing"]:
            return ""

        trace = self.active_traces.get(trace_id)
        if not trace:
            return ""

        event_id = await self._record_event(
            trace_id=trace_id,
            event_type=TraceEventType.STEP_START,
            level=level,
            step=step_name,
            message=message or f"Step {step_name} started",
            data={"step_id": step_id, **(data or {})},
        )

        return event_id

    async def trace_step_end(
        self,
        trace_id: str,
        step_id: str,
        step_name: str,
        event_id: str = None,
        message: str = None,
        data: Dict[str, Any] = None,
    ) -> None:
        """Trace a step end."""
        if not self.config["enable_tracing"]:
            return

        trace = self.active_traces.get(trace_id)
        if not trace:
            return

        # Find the matching start event
        start_event = None
        if event_id:
            start_event = next(
                (e for e in trace.events if e.event_id == event_id), None
            )
        else:
            # Find the most recent start event for this step
            start_event = next(
                (
                    e
                    for e in reversed(trace.events)
                    if e.event_type == TraceEventType.STEP_START and e.step == step_name
                ),
                None,
            )

        duration_ms = None
        if start_event:
            duration_ms = int(
                (datetime.now() - start_event.timestamp).total_seconds() * 1000
            )
            trace.step_timings[step_name] = duration_ms

        await self._record_event(
            trace_id=trace_id,
            event_type=TraceEventType.STEP_END,
            level=TraceLevel.INFO,
            step=step_name,
            message=message or f"Step {step_name} completed",
            data={"step_id": step_id, **(data or {})},
            duration_ms=duration_ms,
            parent_event_id=start_event.event_id if start_event else None,
        )

    async def trace_error(
        self,
        trace_id: str,
        error: Exception,
        stage: str = None,
        step: str = None,
        message: str = None,
        data: Dict[str, Any] = None,
    ) -> None:
        """Trace an error."""
        if not self.config["enable_tracing"]:
            return

        trace = self.active_traces.get(trace_id)
        if not trace:
            return

        trace.error_count += 1
        self.stats["error_events"] += 1

        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            **(data or {}),
        }

        await self._record_event(
            trace_id=trace_id,
            event_type=TraceEventType.STAGE_ERROR,
            level=TraceLevel.ERROR,
            stage=stage,
            step=step,
            message=message or f"Error: {str(error)}",
            data=error_data,
        )

    async def trace_metric(
        self,
        trace_id: str,
        metric_name: str,
        value: float,
        unit: str = None,
        tags: Dict[str, str] = None,
    ) -> None:
        """Trace a metric."""
        if not self.config["enable_tracing"]:
            return

        trace = self.active_traces.get(trace_id)
        if not trace:
            return

        await self._record_event(
            trace_id=trace_id,
            event_type=TraceEventType.METRIC,
            level=TraceLevel.DEBUG,
            message=f"Metric: {metric_name} = {value} {unit or ''}",
            data={
                "metric_name": metric_name,
                "value": value,
                "unit": unit,
                "tags": tags or {},
            },
        )

    async def trace_log(
        self,
        trace_id: str,
        message: str,
        level: TraceLevel = TraceLevel.INFO,
        data: Dict[str, Any] = None,
    ) -> None:
        """Trace a log message."""
        if not self.config["enable_tracing"]:
            return

        trace = self.active_traces.get(trace_id)
        if not trace:
            return

        if level == TraceLevel.WARNING:
            trace.warning_count += 1
            self.stats["warning_events"] += 1

        await self._record_event(
            trace_id=trace_id,
            event_type=TraceEventType.LOG,
            level=level,
            message=message,
            data=data or {},
        )

    async def trace_custom(
        self,
        trace_id: str,
        event_type: TraceEventType,
        level: TraceLevel,
        message: str,
        data: Dict[str, Any] = None,
    ) -> None:
        """Trace a custom event."""
        if not self.config["enable_tracing"]:
            return

        await self._record_event(
            trace_id=trace_id,
            event_type=event_type,
            level=level,
            message=message,
            data=data or {},
        )

    async def _record_event(
        self,
        trace_id: str,
        event_type: TraceEventType,
        level: TraceLevel,
        message: str,
        stage: str = None,
        step: str = None,
        data: Dict[str, Any] = None,
        duration_ms: int = None,
        parent_event_id: str = None,
        tags: Dict[str, str] = None,
    ) -> str:
        """Record a trace event."""
        trace = self.active_traces.get(trace_id)
        if not trace:
            return ""

        # Check if we should capture this level
        if not self._should_capture_level(level, trace.capture_level):
            return ""

        event_id = str(uuid.uuid4())

        event = TraceEvent(
            event_id=event_id,
            trace_id=trace_id,
            event_type=event_type,
            level=level,
            timestamp=datetime.now(),
            stage=stage,
            step=step,
            message=message,
            data=data or {},
            duration_ms=duration_ms,
            parent_event_id=parent_event_id,
            tags=tags or {},
        )

        # Add to trace (respect max events limit)
        if len(trace.events) >= trace.max_events:
            # Remove oldest event
            trace.events.pop(0)

        trace.events.append(event)
        self.stats["total_events"] += 1

        # Run event hooks
        for hook in self.event_hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook(event)
                else:
                    hook(event)
            except Exception as e:
                print(f"Trace hook error: {e}")

        return event_id

    def _should_capture_level(
        self, level: TraceLevel, capture_level: TraceLevel
    ) -> bool:
        """Check if we should capture this level."""
        level_priority = {
            TraceLevel.DEBUG: 0,
            TraceLevel.INFO: 1,
            TraceLevel.WARNING: 2,
            TraceLevel.ERROR: 3,
            TraceLevel.CRITICAL: 4,
        }

        return level_priority[level] >= level_priority[capture_level]

    async def get_trace(self, trace_id: str) -> Optional[CognitiveTrace]:
        """Get a trace by ID."""
        return self.active_traces.get(trace_id)

    async def get_trace_events(
        self,
        trace_id: str,
        event_type: TraceEventType = None,
        level: TraceLevel = None,
        stage: str = None,
        step: str = None,
        limit: int = None,
    ) -> List[TraceEvent]:
        """Get events from a trace with optional filtering."""
        trace = self.active_traces.get(trace_id)
        if not trace:
            return []

        events = trace.events

        # Filter by event type
        if event_type:
            events = [e for e in events if e.event_type == event_type]

        # Filter by level
        if level:
            events = [e for e in events if e.level == level]

        # Filter by stage
        if stage:
            events = [e for e in events if e.stage == stage]

        # Filter by step
        if step:
            events = [e for e in events if e.step == step]

        # Limit results
        if limit:
            events = events[-limit:]

        return events

    async def get_trace_summary(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of a trace."""
        trace = self.active_traces.get(trace_id)
        if not trace:
            return None

        # Calculate statistics
        event_counts = defaultdict(int)
        level_counts = defaultdict(int)
        stage_counts = defaultdict(int)

        for event in trace.events:
            event_counts[event.event_type.value] += 1
            level_counts[event.level.value] += 1
            if event.stage:
                stage_counts[event.stage] += 1

        return {
            "trace_id": trace.trace_id,
            "execution_id": trace.execution_id,
            "workspace_id": trace.workspace_id,
            "user_id": trace.user_id,
            "status": trace.status,
            "start_time": trace.start_time.isoformat(),
            "end_time": trace.end_time.isoformat() if trace.end_time else None,
            "duration_ms": trace.duration_ms,
            "events_count": len(trace.events),
            "event_types": dict(event_counts),
            "levels": dict(level_counts),
            "stages": dict(stage_counts),
            "stage_timings": trace.stage_timings,
            "step_timings": trace.step_timings,
            "error_count": trace.error_count,
            "warning_count": trace.warning_count,
            "metadata": trace.metadata,
        }

    async def search_traces(
        self,
        workspace_id: str = None,
        user_id: str = None,
        status: str = None,
        start_time: datetime = None,
        end_time: datetime = None,
    ) -> List[str]:
        """Search for traces matching criteria."""
        matching_trace_ids = []

        for trace_id, trace in self.active_traces.items():
            # Filter by workspace
            if workspace_id and trace.workspace_id != workspace_id:
                continue

            # Filter by user
            if user_id and trace.user_id != user_id:
                continue

            # Filter by status
            if status and trace.status != status:
                continue

            # Filter by time range
            if start_time and trace.start_time < start_time:
                continue

            if end_time and trace.start_time > end_time:
                continue

            matching_trace_ids.append(trace_id)

        return matching_trace_ids

    def add_event_hook(self, hook: Callable) -> None:
        """Add an event hook."""
        self.event_hooks.append(hook)

    def remove_event_hook(self, hook: Callable) -> None:
        """Remove an event hook."""
        if hook in self.event_hooks:
            self.event_hooks.remove(hook)

    async def _archive_trace(self, trace: CognitiveTrace) -> None:
        """Archive a trace to storage."""
        if self.storage_client:
            await self.storage_client.set(
                "cognitive_traces",
                trace.trace_id,
                {
                    "trace_id": trace.trace_id,
                    "execution_id": trace.execution_id,
                    "workspace_id": trace.workspace_id,
                    "user_id": trace.user_id,
                    "start_time": trace.start_time.isoformat(),
                    "end_time": trace.end_time.isoformat() if trace.end_time else None,
                    "duration_ms": trace.duration_ms,
                    "status": trace.status,
                    "events": [
                        {
                            "event_id": e.event_id,
                            "event_type": e.event_type.value,
                            "level": e.level.value,
                            "timestamp": e.timestamp.isoformat(),
                            "stage": e.stage,
                            "step": e.step,
                            "message": e.message,
                            "data": e.data,
                            "duration_ms": e.duration_ms,
                            "parent_event_id": e.parent_event_id,
                            "tags": e.tags,
                        }
                        for e in trace.events
                    ],
                    "stage_timings": trace.stage_timings,
                    "step_timings": trace.step_timings,
                    "error_count": trace.error_count,
                    "warning_count": trace.warning_count,
                    "metadata": trace.metadata,
                },
            )

    def get_tracer_stats(self) -> Dict[str, Any]:
        """Get tracer statistics."""
        return {
            "active_traces": len(self.active_traces),
            "total_traces": self.stats["total_traces"],
            "total_events": self.stats["total_events"],
            "error_events": self.stats["error_events"],
            "warning_events": self.stats["warning_events"],
            "event_hooks": len(self.event_hooks),
            "tracing_enabled": self.config["enable_tracing"],
            "default_level": self.config["default_level"].value,
        }
