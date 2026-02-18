"""
Tool registry and policy-enforced execution for AI Hub.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Tuple

from backend.ai.hub.contracts import ToolPolicy
from backend.services.exceptions import ServiceError, ValidationError


ToolHandler = Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]


@dataclass
class ToolSpec:
    name: str
    description: str
    mutating_external: bool = False
    risk_tier: str = "low"
    idempotent: bool = True
    required_input_keys: Tuple[str, ...] = ()
    max_payload_bytes: int = 16_384


class ToolRegistry:
    def __init__(self) -> None:
        self._handlers: Dict[str, ToolHandler] = {}
        self._specs: Dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec, handler: ToolHandler) -> None:
        self._specs[spec.name] = spec
        self._handlers[spec.name] = handler

    def list_specs(self) -> Dict[str, Dict[str, Any]]:
        return {
            name: {
                "description": spec.description,
                "mutating_external": spec.mutating_external,
                "risk_tier": spec.risk_tier,
                "idempotent": spec.idempotent,
                "required_input_keys": list(spec.required_input_keys),
                "max_payload_bytes": spec.max_payload_bytes,
            }
            for name, spec in self._specs.items()
        }

    @staticmethod
    def _payload_size_bytes(payload: Dict[str, Any]) -> int:
        try:
            return len(json.dumps(payload, default=str, ensure_ascii=True).encode("utf-8"))
        except Exception:
            return len(str(payload).encode("utf-8"))

    @staticmethod
    def _validate_required_inputs(spec: ToolSpec, payload: Dict[str, Any]) -> None:
        missing = [
            key
            for key in spec.required_input_keys
            if key not in payload or payload[key] in (None, "")
        ]
        if missing:
            raise ValidationError(
                f"Tool '{spec.name}' is missing required inputs: {', '.join(missing)}"
            )

    async def execute(
        self, *, name: str, payload: Dict[str, Any], policy: ToolPolicy
    ) -> Dict[str, Any]:
        if name not in self._handlers:
            raise ValidationError(f"Tool '{name}' is not registered")

        spec = self._specs[name]
        allowed_tools = policy.allowed_tools
        if not allowed_tools:
            raise ValidationError("No tools are allowed by policy")
        if name not in allowed_tools:
            raise ValidationError(f"Tool '{name}' is not allowed by policy")

        if spec.mutating_external and not policy.allow_mutating_external:
            raise ValidationError(
                f"Tool '{name}' requires mutating external permission"
            )

        self._validate_required_inputs(spec, payload)
        payload_size = self._payload_size_bytes(payload)
        if payload_size > spec.max_payload_bytes:
            raise ValidationError(
                f"Tool '{name}' payload too large ({payload_size} > {spec.max_payload_bytes})"
            )

        started = time.perf_counter()
        try:
            raw_result = await self._handlers[name](payload)
            duration_ms = int((time.perf_counter() - started) * 1000)
            if not isinstance(raw_result, dict):
                raw_result = {"value": raw_result}
            raw_result["_tool"] = name
            raw_result["_meta"] = {
                "duration_ms": duration_ms,
                "payload_bytes": payload_size,
                "risk_tier": spec.risk_tier,
                "idempotent": spec.idempotent,
            }
            return raw_result
        except Exception as exc:
            raise ServiceError(f"Tool '{name}' execution failed: {exc}") from exc


async def _echo_context_tool(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = payload.get("context", {})
    if not isinstance(context, dict):
        context = {}
    return {
        "tool": "echo_context",
        "summary": f"context_keys={sorted(context.keys())}",
    }


async def _stable_hash_tool(payload: Dict[str, Any]) -> Dict[str, Any]:
    raw = str(payload.get("text", ""))
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return {"tool": "stable_hash", "sha256": digest}


def create_default_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            name="echo_context",
            description="Return a deterministic summary of context keys.",
            mutating_external=False,
            risk_tier="low",
            idempotent=True,
            required_input_keys=("context",),
        ),
        _echo_context_tool,
    )
    registry.register(
        ToolSpec(
            name="stable_hash",
            description="Compute stable sha256 hash for a text payload.",
            mutating_external=False,
            risk_tier="low",
            idempotent=True,
            required_input_keys=("text",),
        ),
        _stable_hash_tool,
    )
    return registry
