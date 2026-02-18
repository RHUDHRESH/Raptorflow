"""
BCM Types - Core type definitions for the BCM system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class MemoryType(str, Enum):
    CORRECTION = "correction"
    PREFERENCE = "preference"
    PATTERN = "pattern"
    INSIGHT = "insight"


class MemorySource(str, Enum):
    USER_FEEDBACK = "user_feedback"
    GENERATION_ANALYSIS = "generation_analysis"
    REFLECTION = "reflection"


@dataclass
class BCMIdentity:
    """Brand identity synthesized from business context."""

    voice_archetype: str = ""
    communication_style: str = ""
    emotional_register: str = ""
    vocabulary_dna: List[str] = field(default_factory=list)
    anti_vocabulary: List[str] = field(default_factory=list)
    sentence_patterns: List[str] = field(default_factory=list)
    perspective: str = "we"


@dataclass
class BCMPromptKit:
    """Pre-built prompts and templates for content generation."""

    system_prompt: str = ""
    content_templates: Dict[str, str] = field(default_factory=dict)
    few_shot_examples: Dict[str, List[str]] = field(default_factory=dict)
    icp_voice_map: Dict[str, str] = field(default_factory=dict)


@dataclass
class BCMGuardrails:
    """Rules and constraints for content generation."""

    positive_patterns: List[str] = field(default_factory=list)
    negative_patterns: List[str] = field(default_factory=list)
    competitive_rules: List[str] = field(default_factory=list)
    tone_calibration: Dict[str, float] = field(default_factory=dict)


@dataclass
class BCMFoundation:
    """Core business information."""

    company: str = ""
    industry: str = ""
    stage: str = ""
    mission: str = ""
    value_prop: str = ""


@dataclass
class BCMICP:
    """Ideal Customer Profile."""

    name: str = ""
    role: str = ""
    pains: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    channels: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)


@dataclass
class BCMManifest:
    """
    Business Context Manifest - The core data structure.

    A BCM contains all the context needed to generate on-brand,
    audience-aware content. It's derived from business_context.json
    and enriched through AI synthesis and user feedback.

    Attributes:
        version: Manifest version number
        workspace_id: Associated workspace
        foundation: Core business info
        icps: Target customer profiles
        competitive: Competitive positioning
        messaging: Brand messaging
        channels: Distribution channels
        market: Market size info
        identity: AI-synthesized brand identity
        prompt_kit: Pre-built prompts and templates
        guardrails_v2: Content generation rules
        meta: Metadata including checksum and token estimate
    """

    version: int
    workspace_id: str
    foundation: BCMFoundation
    icps: List[BCMICP] = field(default_factory=list)
    competitive: Dict[str, Any] = field(default_factory=dict)
    messaging: Dict[str, Any] = field(default_factory=dict)
    channels: List[Dict[str, Any]] = field(default_factory=list)
    market: Dict[str, Any] = field(default_factory=dict)
    identity: Optional[BCMIdentity] = None
    prompt_kit: Optional[BCMPromptKit] = None
    guardrails_v2: Optional[BCMGuardrails] = None
    meta: Dict[str, Any] = field(default_factory=dict)

    @property
    def checksum(self) -> str:
        return self.meta.get("checksum", "")

    @property
    def token_estimate(self) -> int:
        return self.meta.get("token_estimate", 0)

    @property
    def synthesized(self) -> bool:
        return self.meta.get("synthesized", False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BCMManifest:
        """Create a BCMManifest from a dictionary."""
        foundation_data = data.get("foundation", {})
        foundation = BCMFoundation(
            company=foundation_data.get("company", ""),
            industry=foundation_data.get("industry", ""),
            stage=foundation_data.get("stage", ""),
            mission=foundation_data.get("mission", ""),
            value_prop=foundation_data.get("value_prop", ""),
        )

        icps = [
            BCMICP(
                name=icp.get("name", ""),
                role=icp.get("role", ""),
                pains=icp.get("pains", []),
                goals=icp.get("goals", []),
                channels=icp.get("channels", []),
                triggers=icp.get("triggers", []),
            )
            for icp in data.get("icps", [])
        ]

        identity_data = data.get("identity") or {}
        identity = (
            BCMIdentity(
                voice_archetype=identity_data.get("voice_archetype", ""),
                communication_style=identity_data.get("communication_style", ""),
                emotional_register=identity_data.get("emotional_register", ""),
                vocabulary_dna=identity_data.get("vocabulary_dna", []),
                anti_vocabulary=identity_data.get("anti_vocabulary", []),
                sentence_patterns=identity_data.get("sentence_patterns", []),
                perspective=identity_data.get("perspective", "we"),
            )
            if identity_data
            else None
        )

        prompt_kit_data = data.get("prompt_kit") or {}
        prompt_kit = (
            BCMPromptKit(
                system_prompt=prompt_kit_data.get("system_prompt", ""),
                content_templates=prompt_kit_data.get("content_templates", {}),
                few_shot_examples=prompt_kit_data.get("few_shot_examples", {}),
                icp_voice_map=prompt_kit_data.get("icp_voice_map", {}),
            )
            if prompt_kit_data
            else None
        )

        guardrails_data = data.get("guardrails_v2") or {}
        guardrails = (
            BCMGuardrails(
                positive_patterns=guardrails_data.get("positive_patterns", []),
                negative_patterns=guardrails_data.get("negative_patterns", []),
                competitive_rules=guardrails_data.get("competitive_rules", []),
                tone_calibration=guardrails_data.get("tone_calibration", {}),
            )
            if guardrails_data
            else None
        )

        return cls(
            version=data.get("version", 1),
            workspace_id=data.get("workspace_id", ""),
            foundation=foundation,
            icps=icps,
            competitive=data.get("competitive", {}),
            messaging=data.get("messaging", {}),
            channels=data.get("channels", []),
            market=data.get("market", {}),
            identity=identity,
            prompt_kit=prompt_kit,
            guardrails_v2=guardrails,
            meta=data.get("meta", {}),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        result = {
            "version": self.version,
            "workspace_id": self.workspace_id,
            "foundation": {
                "company": self.foundation.company,
                "industry": self.foundation.industry,
                "stage": self.foundation.stage,
                "mission": self.foundation.mission,
                "value_prop": self.foundation.value_prop,
            },
            "icps": [
                {
                    "name": icp.name,
                    "role": icp.role,
                    "pains": icp.pains,
                    "goals": icp.goals,
                    "channels": icp.channels,
                    "triggers": icp.triggers,
                }
                for icp in self.icps
            ],
            "competitive": self.competitive,
            "messaging": self.messaging,
            "channels": self.channels,
            "market": self.market,
            "meta": self.meta,
        }

        if self.identity:
            result["identity"] = {
                "voice_archetype": self.identity.voice_archetype,
                "communication_style": self.identity.communication_style,
                "emotional_register": self.identity.emotional_register,
                "vocabulary_dna": self.identity.vocabulary_dna,
                "anti_vocabulary": self.identity.anti_vocabulary,
                "sentence_patterns": self.identity.sentence_patterns,
                "perspective": self.identity.perspective,
            }
        else:
            result["identity"] = None

        if self.prompt_kit:
            result["prompt_kit"] = {
                "system_prompt": self.prompt_kit.system_prompt,
                "content_templates": self.prompt_kit.content_templates,
                "few_shot_examples": self.prompt_kit.few_shot_examples,
                "icp_voice_map": self.prompt_kit.icp_voice_map,
            }
        else:
            result["prompt_kit"] = None

        if self.guardrails_v2:
            result["guardrails_v2"] = {
                "positive_patterns": self.guardrails_v2.positive_patterns,
                "negative_patterns": self.guardrails_v2.negative_patterns,
                "competitive_rules": self.guardrails_v2.competitive_rules,
                "tone_calibration": self.guardrails_v2.tone_calibration,
            }
        else:
            result["guardrails_v2"] = None

        return result


@dataclass
class Memory:
    """A learned preference, correction, or insight."""

    id: str
    workspace_id: str
    memory_type: MemoryType
    content: Dict[str, Any]
    source: MemorySource
    confidence: float
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Memory:
        return cls(
            id=data.get("id", ""),
            workspace_id=data.get("workspace_id", ""),
            memory_type=MemoryType(data.get("memory_type", "insight")),
            content=data.get("content", {}),
            source=MemorySource(data.get("source", "reflection")),
            confidence=data.get("confidence", 0.5),
            created_at=datetime.fromisoformat(data["created_at"])
            if data.get("created_at")
            else None,
        )


@dataclass
class GenerationLog:
    """Log of a content generation for feedback tracking."""

    id: str
    workspace_id: str
    content_type: str
    prompt_used: str
    output: str
    bcm_version: int
    tokens_used: int
    cost_usd: float
    feedback_score: Optional[int] = None
    user_edits: Optional[str] = None
    created_at: Optional[datetime] = None
