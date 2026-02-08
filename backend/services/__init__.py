"""
Services package for RaptorFlow.

Keep this package lightweight: importing `services` should not eagerly import
optional/heavy integrations (payments, Vertex AI, etc).
"""

from __future__ import annotations

from typing import Any

__all__ = ["vertex_ai_service"]


def __getattr__(name: str) -> Any:
    if name == "vertex_ai_service":
        try:
            from .vertex_ai_service import vertex_ai_service  # noqa: PLC0415
        except Exception as exc:  # pragma: no cover - optional dependency
            raise AttributeError(name) from exc
        return vertex_ai_service
    raise AttributeError(name)


def __dir__() -> list[str]:
    return sorted(set(__all__) | set(globals().keys()))
