"""
Services package for RaptorFlow.

Keep this package lightweight: importing `services` should not eagerly import
optional/heavy integrations (payments, Vertex AI, etc).
"""

from __future__ import annotations

from typing import Any

__all__ = ["EmailService", "PaymentService", "vertex_ai_service"]


def __getattr__(name: str) -> Any:
    if name == "EmailService":
        from .email_service import EmailService  # noqa: PLC0415

        return EmailService
    if name == "PaymentService":
        from .payment_service import PaymentService  # noqa: PLC0415

        return PaymentService
    if name == "vertex_ai_service":
        try:
            from .vertex_ai_service import vertex_ai_service  # noqa: PLC0415
        except Exception as exc:  # pragma: no cover - optional dependency
            raise AttributeError(name) from exc
        return vertex_ai_service
    raise AttributeError(name)


def __dir__() -> list[str]:
    return sorted(set(__all__) | set(globals().keys()))
