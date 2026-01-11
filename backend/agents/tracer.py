"""
Execution tracer for LangChain agent workflows.
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.tracers.base import BaseTracer
from langchain_core.tracers.schemas import Run

from ..state import AgentState


@dataclass
class TraceStep:
    """Single step in execution trace."""

    step_id: str
    step_name: str
    step_type: str  # "agent", "tool", "chain", "llm"
    input_data: Any
    output_data: Any
    latency_ms: float
    tokens_used: int = 0
    cost_usd: float = 0.0
    error: Optional[str] = None
    parent_step_id: Optional[str] = None
    child_step_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "step_id": self.step_id,
            "step_name": self.step_name,
            "step_type": self.step_type,
            "input_data": self._serialize_data(self.input_data),
            "output_data": self._serialize_data(self.output_data),
            "latency_ms": self.latency_ms,
            "tokens_used": self.tokens_used,
            "cost_usd": self.cost_usd,
            "error": self.error,
            "parent_step_id": self.parent_step_id,
            "child_step_ids": self.child_step_ids,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }

    def _serialize_data(self, data: Any) -> Any:
        """Serialize data for JSON output."""
        if isinstance(data, (str, int, float, bool, type(None))):
            return data
        elif isinstance(data, dict):
            return {k: self._serialize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._serialize_data(item) for item in data]
        else:
            return str(data)


@dataclass
class ExecutionTrace:
    """Complete execution trace for a session."""

    trace_id: str
    session_id: str
    workspace_id: str
    user_id: str
    agent_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    steps: List[TraceStep] = field(default_factory=list)
    root_step_id: Optional[str] = None
    total_latency_ms: float = 0.0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_step(self, step: TraceStep) -> None:
        """Add a step to the trace."""
        self.steps.append(step)

        # Update totals
        self.total_latency_ms += step.latency_ms
        self.total_tokens += step.tokens_used
        self.total_cost_usd += step.cost_usd

        # Update success status
        if step.error:
            self.success = False
            self.error = step.error

        # Set root step if not set
        if not self.root_step_id:
            self.root_step_id = step.step_id

    def finish_trace(self, success: bool = True, error: Optional[str] = None) -> None:
        """Mark trace as finished."""
        self.end_time = datetime.now()
        self.success = success
        if error:
            self.error = error
            self.success = False

    def get_step_by_id(self, step_id: str) -> Optional[TraceStep]:
        """Get a step by ID."""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None

    def get_steps_by_type(self, step_type: str) -> List[TraceStep]:
        """Get all steps of a specific type."""
        return [step for step in self.steps if step.step_type == step_type]

    def get_execution_tree(self) -> Dict[str, Any]:
        """Get execution tree structure."""
        if not self.root_step_id:
            return {}

        def build_tree(step_id: str) -> Dict[str, Any]:
            step = self.get_step_by_id(step_id)
            if not step:
                return {}

            tree = step.to_dict()
            tree["children"] = []

            for child_id in step.child_step_ids:
                child_tree = build_tree(child_id)
                if child_tree:
                    tree["children"].append(child_tree)

            return tree

        return build_tree(self.root_step_id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "trace_id": self.trace_id,
            "session_id": self.session_id,
            "workspace_id": self.workspace_id,
            "user_id": self.user_id,
            "agent_name": self.agent_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_latency_ms": self.total_latency_ms,
            "total_tokens": self.total_tokens,
            "total_cost_usd": self.total_cost_usd,
            "success": self.success,
            "error": self.error,
            "step_count": len(self.steps),
            "execution_tree": self.get_execution_tree(),
            "metadata": self.metadata,
        }


class ExecutionTracer(BaseTracer, BaseCallbackHandler):
    """
    LangChain tracer for Raptorflow agent execution.

    Tracks all steps, tool calls, and performance metrics.
    """

    def __init__(self):
        super().__init__()
        self.active_traces: Dict[str, ExecutionTrace] = {}
        self.completed_traces: List[ExecutionTrace] = []
        self.max_completed_traces = 1000

    def start_trace(
        self,
        session_id: str,
        workspace_id: str,
        user_id: str,
        agent_name: str,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """
        Start a new execution trace.

        Args:
            session_id: Session identifier
            workspace_id: Workspace ID
            user_id: User ID
            agent_name: Name of the agent
            metadata: Additional metadata

        Returns:
            Trace ID
        """
        trace_id = str(uuid.uuid4())

        trace = ExecutionTrace(
            trace_id=trace_id,
            session_id=session_id,
            workspace_id=workspace_id,
            user_id=user_id,
            agent_name=agent_name,
            start_time=datetime.now(),
            metadata=metadata or {},
        )

        self.active_traces[trace_id] = trace
        return trace_id

    def add_step(
        self,
        trace_id: str,
        step_name: str,
        step_type: str,
        input_data: Any,
        output_data: Any,
        latency_ms: float,
        tokens_used: int = 0,
        cost_usd: float = 0.0,
        error: Optional[str] = None,
        parent_step_id: Optional[str] = None,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """
        Add a step to an active trace.

        Args:
            trace_id: Trace identifier
            step_name: Name of the step
            step_type: Type of step
            input_data: Input data
            output_data: Output data
            latency_ms: Execution time
            tokens_used: Tokens used
            cost_usd: Cost in USD
            error: Error if any
            parent_step_id: Parent step ID
            metadata: Additional metadata

        Returns:
            Step ID
        """
        if trace_id not in self.active_traces:
            raise ValueError(f"Trace {trace_id} not found or not active")

        step_id = str(uuid.uuid4())

        step = TraceStep(
            step_id=step_id,
            step_name=step_name,
            step_type=step_type,
            input_data=input_data,
            output_data=output_data,
            latency_ms=latency_ms,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            error=error,
            parent_step_id=parent_step_id,
            metadata=metadata or {},
        )

        # Add step to trace
        trace = self.active_traces[trace_id]
        trace.add_step(step)

        # Update parent-child relationships
        if parent_step_id:
            parent_step = trace.get_step_by_id(parent_step_id)
            if parent_step:
                parent_step.child_step_ids.append(step_id)

        return step_id

    def finish_trace(
        self, trace_id: str, success: bool = True, error: Optional[str] = None
    ) -> None:
        """
        Finish an active trace.

        Args:
            trace_id: Trace identifier
            success: Whether execution was successful
            error: Error if any
        """
        if trace_id not in self.active_traces:
            return

        trace = self.active_traces[trace_id]
        trace.finish_trace(success, error)

        # Move to completed traces
        self.completed_traces.append(trace)
        del self.active_traces[trace_id]

        # Limit completed traces
        if len(self.completed_traces) > self.max_completed_traces:
            self.completed_traces = self.completed_traces[-self.max_completed_traces :]

    def get_trace(self, trace_id: str) -> Optional[ExecutionTrace]:
        """Get a trace by ID (active or completed)."""
        if trace_id in self.active_traces:
            return self.active_traces[trace_id]

        for trace in self.completed_traces:
            if trace.trace_id == trace_id:
                return trace

        return None

    def get_traces_by_session(self, session_id: str) -> List[ExecutionTrace]:
        """Get all traces for a session."""
        traces = []

        # Active traces
        for trace in self.active_traces.values():
            if trace.session_id == session_id:
                traces.append(trace)

        # Completed traces
        for trace in self.completed_traces:
            if trace.session_id == session_id:
                traces.append(trace)

        return sorted(traces, key=lambda x: x.start_time, reverse=True)

    def get_traces_by_workspace(
        self, workspace_id: str, limit: int = 50
    ) -> List[ExecutionTrace]:
        """Get traces for a workspace."""
        traces = []

        # Active traces
        for trace in self.active_traces.values():
            if trace.workspace_id == workspace_id:
                traces.append(trace)

        # Completed traces
        for trace in self.completed_traces:
            if trace.workspace_id == workspace_id:
                traces.append(trace)

        # Sort and limit
        traces.sort(key=lambda x: x.start_time, reverse=True)
        return traces[:limit]

    def get_trace_summary(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of a trace."""
        trace = self.get_trace(trace_id)
        if not trace:
            return None

        return {
            "trace_id": trace.trace_id,
            "agent_name": trace.agent_name,
            "success": trace.success,
            "total_latency_ms": trace.total_latency_ms,
            "total_tokens": trace.total_tokens,
            "total_cost_usd": trace.total_cost_usd,
            "step_count": len(trace.steps),
            "start_time": trace.start_time.isoformat(),
            "end_time": trace.end_time.isoformat() if trace.end_time else None,
            "error": trace.error,
        }

    # LangChain BaseTracer methods
    def _persist_run(self, run: Run) -> None:
        """Persist a LangChain run."""
        # Convert LangChain run to our trace format
        if not run.parent_run_id:
            # This is a root run, create a new trace
            trace_id = self.start_trace(
                session_id=run.id.split("-")[0],  # Extract session ID
                workspace_id=run.extra.get("workspace_id", ""),
                user_id=run.extra.get("user_id", ""),
                agent_name=run.name or "unknown",
                metadata=run.extra,
            )

    def _on_run_create(self, run: Run) -> None:
        """Handle run creation."""
        self._persist_run(run)

    def _on_run_update(self, run: Run) -> None:
        """Handle run update."""
        # Update corresponding trace step
        pass

    def _on_run_end(self, run: Run) -> None:
        """Handle run end."""
        # Finish corresponding trace
        trace_id = run.extra.get("trace_id")
        if trace_id:
            success = run.error is None
            error = str(run.error) if run.error else None
            self.finish_trace(trace_id, success, error)

    # BaseCallbackHandler methods
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Any, **kwargs) -> None:
        """Handle chain start."""
        pass

    def on_chain_end(self, outputs: Any, **kwargs) -> None:
        """Handle chain end."""
        pass

    def on_chain_error(self, error: Exception, **kwargs) -> None:
        """Handle chain error."""
        pass

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs
    ) -> None:
        """Handle LLM start."""
        pass

    def on_llm_end(self, response: Any, **kwargs) -> None:
        """Handle LLM end."""
        pass

    def on_llm_error(self, error: Exception, **kwargs) -> None:
        """Handle LLM error."""
        pass

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs
    ) -> None:
        """Handle tool start."""
        pass

    def on_tool_end(self, output: Any, **kwargs) -> None:
        """Handle tool end."""
        pass

    def on_tool_error(self, error: Exception, **kwargs) -> None:
        """Handle tool error."""
        pass

    def on_text(self, text: str, **kwargs) -> None:
        """Handle text output."""
        pass

    def on_agent_action(self, action: Any, **kwargs) -> None:
        """Handle agent action."""
        pass

    def on_agent_finish(self, finish: Any, **kwargs) -> None:
        """Handle agent finish."""
        pass


# Global tracer instance
execution_tracer = ExecutionTracer()


# Convenience functions
def start_trace(
    session_id: str,
    workspace_id: str,
    user_id: str,
    agent_name: str,
    metadata: Dict[str, Any] = None,
) -> str:
    """Start a new execution trace."""
    return execution_tracer.start_trace(
        session_id, workspace_id, user_id, agent_name, metadata
    )


def add_trace_step(
    trace_id: str,
    step_name: str,
    step_type: str,
    input_data: Any,
    output_data: Any,
    latency_ms: float,
    **kwargs,
) -> str:
    """Add a step to a trace."""
    return execution_tracer.add_step(
        trace_id, step_name, step_type, input_data, output_data, latency_ms, **kwargs
    )


def finish_trace(
    trace_id: str, success: bool = True, error: Optional[str] = None
) -> None:
    """Finish a trace."""
    execution_tracer.finish_trace(trace_id, success, error)


def get_trace(trace_id: str) -> Optional[ExecutionTrace]:
    """Get a trace by ID."""
    return execution_tracer.get_trace(trace_id)


def get_session_traces(session_id: str) -> List[ExecutionTrace]:
    """Get all traces for a session."""
    return execution_tracer.get_traces_by_session(session_id)


def export_trace(trace_id: str, format: str = "json") -> str:
    """Export a trace in specified format."""
    trace = execution_tracer.get_trace(trace_id)
    if not trace:
        return "Trace not found"

    if format.lower() == "json":
        return json.dumps(trace.to_dict(), indent=2)
    else:
        raise ValueError(f"Unsupported format: {format}")
