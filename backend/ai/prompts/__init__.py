"""
AI Prompts - Prompt compilation utilities.

Compiles BCM manifests into effective system prompts for AI generation.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def compile_system_prompt(
    manifest: Dict[str, Any],
    content_type: str = "general",
    target_icp: Optional[str] = None,
    memories: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    Build a complete system prompt from a BCM manifest.

    If the manifest has synthesized identity/prompt_kit/guardrails_v2,
    uses those directly. Otherwise builds from foundation data.

    Args:
        manifest: BCM manifest dictionary
        content_type: Type of content (email, social, blog, etc.)
        target_icp: Target ICP name for voice adaptation
        memories: List of learned preferences/insights

    Returns:
        Compiled system prompt string
    """
    identity = manifest.get("identity")
    prompt_kit = manifest.get("prompt_kit")
    guardrails_v2 = manifest.get("guardrails_v2")

    if identity and prompt_kit and guardrails_v2:
        return _compile_from_synthesis(
            manifest,
            identity,
            prompt_kit,
            guardrails_v2,
            content_type,
            target_icp,
            memories,
        )
    else:
        return _compile_from_foundation(
            manifest,
            content_type,
            target_icp,
            memories,
        )


def _compile_from_synthesis(
    manifest: Dict[str, Any],
    identity: Dict[str, Any],
    prompt_kit: Dict[str, Any],
    guardrails_v2: Dict[str, Any],
    content_type: str,
    target_icp: Optional[str],
    memories: Optional[List[Dict[str, Any]]],
) -> str:
    """Build system prompt from AI-synthesized BCM sections."""
    foundation = manifest.get("foundation", {})
    messaging = manifest.get("messaging", {})
    competitive = manifest.get("competitive", {})
    icps = manifest.get("icps", [])

    parts = []

    parts.append(
        f"You are {identity.get('voice_archetype', 'a content specialist')} "
        f"for {foundation.get('company', 'the company')}."
    )

    parts.append(f"\n## YOUR IDENTITY")
    parts.append(f"- Communication style: {identity.get('communication_style', '')}")
    parts.append(f"- Emotional register: {identity.get('emotional_register', '')}")
    if identity.get("vocabulary_dna"):
        parts.append(f"- Power words to use: {', '.join(identity['vocabulary_dna'])}")
    if identity.get("anti_vocabulary"):
        parts.append(f"- Words to NEVER use: {', '.join(identity['anti_vocabulary'])}")
    if identity.get("sentence_patterns"):
        parts.append("- Writing patterns:")
        for p in identity["sentence_patterns"]:
            parts.append(f"  * {p}")
    parts.append(f"- Perspective: {identity.get('perspective', 'we')}")

    parts.append(f"\n## BUSINESS CONTEXT")
    parts.append(
        f"- Company: {foundation.get('company', '')} "
        f"({foundation.get('industry', '')}, {foundation.get('stage', '')})"
    )
    parts.append(f"- Value proposition: {foundation.get('value_prop', '')}")
    parts.append(f"- One-liner: {messaging.get('one_liner', '')}")
    if messaging.get("positioning"):
        parts.append(f"- Positioning: {messaging['positioning'][:200]}")

    selected_icp = None
    if target_icp and icps:
        selected_icp = next((i for i in icps if i.get("name") == target_icp), None)
    if not selected_icp and icps:
        selected_icp = icps[0]

    if selected_icp:
        parts.append(f"\n## TARGET AUDIENCE: {selected_icp.get('name', '')}")
        parts.append(f"- Role: {selected_icp.get('role', '')}")
        if selected_icp.get("pains"):
            parts.append(f"- Pain points: {', '.join(selected_icp['pains'][:3])}")
        if selected_icp.get("goals"):
            parts.append(f"- Goals: {', '.join(selected_icp['goals'][:3])}")
        if selected_icp.get("triggers"):
            parts.append(f"- Triggers: {', '.join(selected_icp['triggers'][:3])}")
        icp_voice = prompt_kit.get("icp_voice_map", {}).get(
            selected_icp.get("name", ""), ""
        )
        if icp_voice:
            parts.append(f"- Voice adaptation: {icp_voice}")

    if competitive.get("category") or competitive.get("differentiation"):
        parts.append(f"\n## COMPETITIVE POSITIONING")
        if competitive.get("category"):
            parts.append(f"- Category: {competitive['category']}")
        if competitive.get("differentiation"):
            parts.append(f"- Key differentiator: {competitive['differentiation']}")
        if guardrails_v2.get("competitive_rules"):
            for rule in guardrails_v2["competitive_rules"]:
                parts.append(f"- {rule}")

    parts.append(f"\n## GUARDRAILS")
    if guardrails_v2.get("positive_patterns"):
        parts.append("DO:")
        for g in guardrails_v2["positive_patterns"][:5]:
            parts.append(f"  + {g}")
    if guardrails_v2.get("negative_patterns"):
        parts.append("DON'T:")
        for g in guardrails_v2["negative_patterns"][:5]:
            parts.append(f"  - {g}")

    ct_template = prompt_kit.get("content_templates", {}).get(content_type, "")
    if ct_template:
        parts.append(f"\n## CONTENT TYPE INSTRUCTIONS ({content_type.upper()})")
        parts.append(ct_template)

    examples = prompt_kit.get("few_shot_examples", {}).get(content_type, [])
    if examples:
        parts.append(f"\n## EXAMPLES OF YOUR BEST WORK")
        for i, ex in enumerate(examples[:2], 1):
            parts.append(f"\nExample {i}:\n{ex}")

    if memories:
        parts.append(f"\n## LEARNED PREFERENCES")
        for mem in memories[:5]:
            parts.append(
                f"- {mem.get('content', {}).get('summary', str(mem.get('content', '')))}"
            )

    return "\n".join(parts)


def _compile_from_foundation(
    manifest: Dict[str, Any],
    content_type: str,
    target_icp: Optional[str],
    memories: Optional[List[Dict[str, Any]]],
) -> str:
    """Build a reasonable system prompt from a legacy (non-synthesized) BCM."""
    foundation = manifest.get("foundation", {})
    messaging = manifest.get("messaging", {})
    icps = manifest.get("icps", [])
    competitive = manifest.get("competitive", {})

    parts = []

    company = foundation.get("company", "the company")
    industry = foundation.get("industry", "")
    stage = foundation.get("stage", "")

    parts.append(
        f"You are a marketing content specialist for {company}"
        f"{f', a {industry} company' if industry else ''}"
        f"{f' at {stage} stage' if stage else ''}."
    )

    if foundation.get("value_prop"):
        parts.append(f"\nValue proposition: {foundation['value_prop']}")

    if messaging.get("one_liner"):
        parts.append(f"One-liner: {messaging['one_liner']}")

    if messaging.get("tone"):
        parts.append(f"Tone: {', '.join(messaging['tone'][:3])}")

    if messaging.get("guardrails"):
        parts.append("\nGuardrails:")
        for g in messaging["guardrails"][:3]:
            parts.append(f"- {g}")

    selected_icp = None
    if target_icp and icps:
        selected_icp = next((i for i in icps if i.get("name") == target_icp), None)
    if not selected_icp and icps:
        selected_icp = icps[0]

    if selected_icp:
        parts.append(f"\nTarget audience: {selected_icp.get('name', '')}")
        parts.append(f"Role: {selected_icp.get('role', '')}")
        if selected_icp.get("pains"):
            parts.append(f"Pain points: {', '.join(selected_icp['pains'][:3])}")

    if competitive.get("differentiation"):
        parts.append(f"\nKey differentiator: {competitive['differentiation']}")

    parts.append(
        "\nWrite content that is on-brand, audience-aware, and actionable. "
        "Be specific and concrete — avoid generic marketing language."
    )

    return "\n".join(parts)


def build_user_prompt(
    task: str,
    content_type: str = "general",
    tone: str = "",
    target_audience: str = "",
) -> str:
    """
    Build the user-facing prompt (separate from system prompt).

    Args:
        task: The main task/prompt
        content_type: Type of content
        tone: Tone override
        target_audience: Target audience description

    Returns:
        Formatted user prompt
    """
    parts = [f"Task: {task}"]

    if content_type and content_type != "general":
        parts.append(f"Content type: {content_type}")
    if tone:
        parts.append(f"Tone override: {tone}")
    if target_audience:
        parts.append(f"Target audience: {target_audience}")

    return "\n".join(parts)


__all__ = [
    "compile_system_prompt",
    "build_user_prompt",
]
