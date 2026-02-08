"""
Pydantic models for business_context.json and BCM manifest.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ── business_context.json models ──────────────────────────────────────────────

class CompanyProfile(BaseModel):
    name: str
    website: str = ""
    industry: str = ""
    stage: str = ""
    description: str = ""


class Fact(BaseModel):
    id: str
    category: str
    label: str
    value: str
    confidence: float = 0.0


class ICPDemographics(BaseModel):
    ageRange: str = ""
    income: str = ""
    location: str = ""
    role: str = ""
    stage: str = ""


class ICPPsychographics(BaseModel):
    beliefs: str = ""
    identity: str = ""
    fears: str = ""
    values: List[str] = Field(default_factory=list)
    hangouts: List[str] = Field(default_factory=list)
    triggers: List[str] = Field(default_factory=list)


class ICP(BaseModel):
    name: str
    demographics: ICPDemographics = Field(default_factory=ICPDemographics)
    psychographics: ICPPsychographics = Field(default_factory=ICPPsychographics)
    painPoints: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    objections: List[str] = Field(default_factory=list)
    marketSophistication: int = 3


class Competitor(BaseModel):
    name: str
    type: str = "direct"
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)


class Positioning(BaseModel):
    category: str = ""
    categoryPath: str = "safe"
    uvp: str = ""
    differentiators: List[str] = Field(default_factory=list)
    competitors: List[Competitor] = Field(default_factory=list)


class ValueProp(BaseModel):
    title: str
    description: str = ""


class BrandVoice(BaseModel):
    tone: List[str] = Field(default_factory=list)
    doList: List[str] = Field(default_factory=list)
    dontList: List[str] = Field(default_factory=list)


class Messaging(BaseModel):
    oneLiner: str = ""
    positioningStatement: str = ""
    valueProps: List[ValueProp] = Field(default_factory=list)
    brandVoice: BrandVoice = Field(default_factory=BrandVoice)
    soundbites: List[str] = Field(default_factory=list)
    guardrails: List[str] = Field(default_factory=list)


class Channel(BaseModel):
    name: str
    priority: str = "secondary"


class Market(BaseModel):
    tam: str = ""
    sam: str = ""
    som: str = ""
    verticals: List[str] = Field(default_factory=list)
    geo: str = ""


class Intelligence(BaseModel):
    evidence_count: int = 0
    facts: List[Fact] = Field(default_factory=list)
    icps: List[ICP] = Field(default_factory=list)
    positioning: Positioning = Field(default_factory=Positioning)
    messaging: Messaging = Field(default_factory=Messaging)
    channels: List[Channel] = Field(default_factory=list)
    market: Market = Field(default_factory=Market)


class BusinessContext(BaseModel):
    """Full business_context.json as produced by onboarding."""

    version: str = "2.0"
    generated_at: str = ""
    session_id: str = ""
    company_profile: CompanyProfile
    intelligence: Intelligence = Field(default_factory=Intelligence)


# ── BCM manifest models ──────────────────────────────────────────────────────

class BCMFoundation(BaseModel):
    company: str
    industry: str = ""
    stage: str = ""
    mission: str = ""
    value_prop: str = ""


class BCMICP(BaseModel):
    name: str
    role: str = ""
    pains: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    channels: List[str] = Field(default_factory=list)
    triggers: List[str] = Field(default_factory=list)


class BCMAlternative(BaseModel):
    name: str
    type: str = "direct"


class BCMCompetitive(BaseModel):
    category: str = ""
    path: str = "safe"
    alternatives: List[BCMAlternative] = Field(default_factory=list)
    differentiation: str = ""


class BCMMessaging(BaseModel):
    one_liner: str = ""
    positioning: str = ""
    tone: List[str] = Field(default_factory=list)
    guardrails: List[str] = Field(default_factory=list)
    soundbites: List[str] = Field(default_factory=list)


class BCMChannel(BaseModel):
    name: str
    priority: str = "secondary"


class BCMMarket(BaseModel):
    tam: str = ""
    sam: str = ""
    som: str = ""


class BCMMeta(BaseModel):
    source: str = "onboarding"
    token_estimate: int = 0
    facts_count: int = 0
    icps_count: int = 0
    competitors_count: int = 0


class BCMManifest(BaseModel):
    """Compact Business Context Manifest (target: <=4KB, ~1200 tokens)."""

    version: int = 1
    generated_at: str = ""
    workspace_id: str = ""
    checksum: str = ""
    foundation: BCMFoundation
    icps: List[BCMICP] = Field(default_factory=list)
    competitive: BCMCompetitive = Field(default_factory=BCMCompetitive)
    messaging: BCMMessaging = Field(default_factory=BCMMessaging)
    channels: List[BCMChannel] = Field(default_factory=list)
    market: BCMMarket = Field(default_factory=BCMMarket)
    meta: BCMMeta = Field(default_factory=BCMMeta)
