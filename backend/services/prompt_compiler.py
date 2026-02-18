"""
Backward compatibility shim for prompt_compiler.

This module provides the legacy import path for prompt compilation functions,
redirecting to the new modular location.
"""

from backend.ai.prompts import build_user_prompt, compile_system_prompt


def get_or_compile_system_prompt(
    manifest: dict,
    content_type: str = "general",
    target_icp: str = None,
    memories: list = None,
) -> str:
    """Compile system prompt from manifest. Wrapper for backward compatibility."""
    return compile_system_prompt(
        manifest=manifest,
        content_type=content_type,
        target_icp=target_icp,
        memories=memories,
    )


__all__ = [
    "get_or_compile_system_prompt",
    "build_user_prompt",
    "compile_system_prompt",
]
