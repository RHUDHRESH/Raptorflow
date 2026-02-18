"""
Workspaces API

Canonical tenant identifier: workspace id (UUID).
Authentication is handled by the auth service (demo/supabase).

This module now owns the BCM-first onboarding contract:
- canonical onboarding steps schema
- workspace onboarding status
- onboarding completion -> business_context.json generation -> BCM seeding
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Depends, Header, status
from pydantic import BaseModel, Field

from backend.agents import format_bcm_row, langgraph_context_orchestrator
from backend.config.settings import get_settings
from backend.infrastructure.database.supabase import get_supabase_client
from backend.services import bcm_service
from backend.services.bcm.templates import (
    TemplateType,
    extract_foundation_data,
    get_template,
)
from backend.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

logger = logging.getLogger(__name__)

ONBOARDING_SCHEMA_VERSION = "2026.02"

CANONICAL_ONBOARDING_STEPS: List[Dict[str, Any]] = [
    {
        "id": "company_name",
        "label": "Company Name",
        "description": "Legal or public-facing name of the business.",
        "kind": "short_text",
        "required": True,
        "placeholder": "Acme Labs",
    },
    {
        "id": "company_website",
        "label": "Company Website",
        "description": "Primary website URL for the business.",
        "kind": "url",
        "required": False,
        "placeholder": "https://acme.com",
    },
    {
        "id": "industry",
        "label": "Industry",
        "description": "Market category the company operates in.",
        "kind": "short_text",
        "required": True,
        "placeholder": "SaaS / FinTech / E-commerce",
    },
    {
        "id": "business_stage",
        "label": "Business Stage",
        "description": "Current maturity stage (pre-seed, seed, growth, etc.).",
        "kind": "short_text",
        "required": True,
        "placeholder": "Seed",
    },
    {
        "id": "company_description",
        "label": "Company Description",
        "description": "What the company does and why it exists.",
        "kind": "long_text",
        "required": True,
        "placeholder": "Two to five sentence company description.",
    },
    {
        "id": "primary_offer",
        "label": "Primary Offer",
        "description": "Main product/service sold to customers.",
        "kind": "short_text",
        "required": True,
        "placeholder": "AI-powered project management platform",
    },
    {
        "id": "core_problem",
        "label": "Core Problem Solved",
        "description": "Most painful problem solved for customers.",
        "kind": "long_text",
        "required": True,
        "placeholder": "What painful outcome is prevented?",
    },
    {
        "id": "ideal_customer_title",
        "label": "Ideal Customer Title",
        "description": "Role or persona of the primary buyer/user.",
        "kind": "short_text",
        "required": True,
        "placeholder": "VP Engineering",
    },
    {
        "id": "ideal_customer_profile",
        "label": "Ideal Customer Profile",
        "description": "Demographic and firmographic description of the ICP.",
        "kind": "long_text",
        "required": True,
        "placeholder": "B2B SaaS companies, 20-200 employees, remote teams.",
    },
    {
        "id": "top_pain_points",
        "label": "Top Pain Points",
        "description": "Top customer pains (comma-separated or newline-separated).",
        "kind": "list",
        "required": True,
        "placeholder": "Low conversion rates, poor retention, unclear attribution",
    },
    {
        "id": "top_goals",
        "label": "Top Customer Goals",
        "description": "Goals customers want to achieve (list).",
        "kind": "list",
        "required": True,
        "placeholder": "Increase pipeline velocity, reduce churn",
    },
    {
        "id": "key_differentiator",
        "label": "Key Differentiator",
        "description": "What makes this solution different and defensible.",
        "kind": "long_text",
        "required": True,
        "placeholder": "Our mechanism competitors cannot replicate easily.",
    },
    {
        "id": "competitors",
        "label": "Competitors",
        "description": "Direct and indirect competitors (list).",
        "kind": "list",
        "required": True,
        "placeholder": "Competitor A, Competitor B",
    },
    {
        "id": "brand_tone",
        "label": "Brand Tone",
        "description": "How the brand should sound (list of tone descriptors).",
        "kind": "list",
        "required": True,
        "placeholder": "Direct, confident, practical",
    },
    {
        "id": "banned_phrases",
        "label": "Banned Words/Phrases",
        "description": "Words and phrases the brand should avoid.",
        "kind": "list",
        "required": False,
        "placeholder": "Revolutionary, game-changing, synergy",
    },
    {
        "id": "channel_priorities",
        "label": "Channel Priorities",
        "description": "Primary go-to-market channels in priority order (list).",
        "kind": "list",
        "required": True,
        "placeholder": "LinkedIn, Email, YouTube",
    },
    {
        "id": "geographic_focus",
        "label": "Geographic Focus",
        "description": "Primary markets or geographies served.",
        "kind": "short_text",
        "required": False,
        "placeholder": "United States and EU",
    },
    {
        "id": "pricing_model",
        "label": "Pricing Model",
        "description": "How the product is priced and sold.",
        "kind": "short_text",
        "required": False,
        "placeholder": "Per-seat monthly SaaS",
    },
    {
        "id": "proof_points",
        "label": "Proof Points",
        "description": "Evidence, traction, metrics, or testimonials (list).",
        "kind": "list",
        "required": False,
        "placeholder": "2.1M ARR, 40% MoM growth, NPS 62",
    },
    {
        "id": "acquisition_goal",
        "label": "Primary Acquisition Goal",
        "description": "Short-term growth objective for the system to optimize.",
        "kind": "short_text",
        "required": True,
        "placeholder": "Generate 60 SQLs per month",
    },
    {
        "id": "constraints_and_guardrails",
        "label": "Constraints and Guardrails",
        "description": "Hard constraints for messaging and execution (list).",
        "kind": "list",
        "required": True,
        "placeholder": "No legal claims without proof, no competitor bashing",
    },
]

_REQUIRED_STEP_IDS = [
    step["id"] for step in CANONICAL_ONBOARDING_STEPS if step["required"]
]
_VALUE_SPLIT_RE = re.compile(r"[\n,;]+")
_SLUG_RE = re.compile(r"[^a-z0-9-]+")


def _generate_slug(company_name: str) -> str:
    """Generate a URL-safe slug from company name."""
    import uuid

    slug = _SLUG_RE.sub("-", company_name.lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return f"{slug}-{uuid.uuid4().hex[:6]}"


async def _get_or_create_demo_workspace() -> Dict[str, Any]:
    """Get or create a demo workspace for demo mode."""
    from backend.config import settings

    demo_workspace_id = getattr(settings, "DEMO_WORKSPACE_ID", "demo-workspace-001")

    supabase = get_supabase_client()

    # Try to get existing workspace
    try:
        result = (
            supabase.table("workspaces")
            .select("*")
            .eq("id", demo_workspace_id)
            .execute()
        )
        if result.data:
            return result.data[0]
    except Exception:
        pass

    # Create demo workspace
    demo_name = "Demo Workspace"
    demo_slug = "demo-workspace"

    try:
        result = (
            supabase.table("workspaces")
            .insert(
                {
                    "id": demo_workspace_id,
                    "name": demo_name,
                    "slug": demo_slug,
                    "settings": {"demo": True},
                }
            )
            .execute()
        )

        if result.data:
            return result.data[0]
    except Exception as e:
        logger.warning(f"Could not create demo workspace: {e}")

    # Return mock workspace if DB not available
    return {
        "id": demo_workspace_id,
        "name": demo_name,
        "slug": demo_slug,
        "settings": {"demo": True},
    }


class WorkspaceCreate(BaseModel):
    name: str = Field(..., min_length=1)
    slug: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class WorkspaceResponse(BaseModel):
    id: str
    name: str
    slug: Optional[str] = None
    settings: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class OnboardingStepOut(BaseModel):
    id: str
    label: str
    description: str
    kind: str
    required: bool
    placeholder: str = ""


class OnboardingStepsResponse(BaseModel):
    schema_version: str
    total_steps: int
    required_steps: int
    steps: List[OnboardingStepOut]


class OnboardingStatusResponse(BaseModel):
    workspace_id: str
    schema_version: str
    completed: bool
    bcm_ready: bool
    completion_pct: int
    answered_steps: int
    total_steps: int
    required_steps: int
    missing_required_steps: List[str] = Field(default_factory=list)
    next_step_id: Optional[str] = None
    answers: Dict[str, Any] = Field(default_factory=dict)
    updated_at: Optional[str] = None


class OnboardingCompleteRequest(BaseModel):
    answers: Dict[str, Any] = Field(default_factory=dict)


class OnboardingCompleteResponse(BaseModel):
    workspace: WorkspaceResponse
    onboarding: OnboardingStatusResponse
    bcm: Dict[str, Any]
    business_context: Dict[str, Any]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slugify(name: str) -> str:
    slug = name.strip().lower()
    slug = slug.replace("_", "-").replace(" ", "-")
    slug = _SLUG_RE.sub("", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or f"workspace-{uuid4().hex[:8]}"


def _is_slug_collision_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return ("23505" in msg or "duplicate" in msg or "unique" in msg) and "slug" in msg


def _normalize_list(value: Any) -> List[str]:
    if value is None:
        return []

    raw_items: List[Any]
    if isinstance(value, list):
        raw_items = value
    elif isinstance(value, str):
        raw_items = _VALUE_SPLIT_RE.split(value)
    else:
        raw_items = [value]

    deduped: List[str] = []
    seen = set()
    for raw in raw_items:
        item = str(raw).strip()
        if not item:
            continue
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        deduped.append(item)
    return deduped


def _normalize_onboarding_answers(raw_answers: Dict[str, Any]) -> Dict[str, Any]:
    normalized: Dict[str, Any] = {}
    for step in CANONICAL_ONBOARDING_STEPS:
        step_id = step["id"]
        kind = step["kind"]
        raw_value = raw_answers.get(step_id)

        if kind == "list":
            normalized[step_id] = _normalize_list(raw_value)
        else:
            normalized[step_id] = "" if raw_value is None else str(raw_value).strip()
    return normalized


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return len(value.strip()) > 0
    if isinstance(value, list):
        return len([v for v in value if str(v).strip()]) > 0
    if isinstance(value, dict):
        return any(_has_value(v) for v in value.values())
    return True


def _missing_required_steps(answers: Dict[str, Any]) -> List[str]:
    missing: List[str] = []
    for step_id in _REQUIRED_STEP_IDS:
        if not _has_value(answers.get(step_id)):
            missing.append(step_id)
    return missing


def _answered_steps_count(answers: Dict[str, Any]) -> int:
    return sum(
        1 for step in CANONICAL_ONBOARDING_STEPS if _has_value(answers.get(step["id"]))
    )


def _required_completion_pct(answers: Dict[str, Any]) -> int:
    required_total = len(_REQUIRED_STEP_IDS)
    if required_total == 0:
        return 100
    answered_required = required_total - len(_missing_required_steps(answers))
    return int((answered_required / required_total) * 100)


def _workspace_settings(row: Dict[str, Any]) -> Dict[str, Any]:
    settings = row.get("settings") or {}
    return settings if isinstance(settings, dict) else {}


def _build_business_context(
    workspace_row: Dict[str, Any], answers: Dict[str, Any]
) -> Dict[str, Any]:
    company_name = (
        answers.get("company_name") or workspace_row.get("name") or "Workspace"
    )
    company_website = answers.get("company_website") or ""
    industry = answers.get("industry") or ""
    stage = answers.get("business_stage") or ""
    description = answers.get("company_description") or ""
    primary_offer = answers.get("primary_offer") or ""
    core_problem = answers.get("core_problem") or ""
    customer_title = answers.get("ideal_customer_title") or "Primary Buyer"
    customer_profile = answers.get("ideal_customer_profile") or ""
    pain_points = _normalize_list(answers.get("top_pain_points"))
    goals = _normalize_list(answers.get("top_goals"))
    differentiator = answers.get("key_differentiator") or ""
    competitor_names = _normalize_list(answers.get("competitors"))
    tone = _normalize_list(answers.get("brand_tone"))
    banned = _normalize_list(answers.get("banned_phrases"))
    channels = _normalize_list(answers.get("channel_priorities"))
    geography = answers.get("geographic_focus") or ""
    pricing_model = answers.get("pricing_model") or ""
    proof_points = _normalize_list(answers.get("proof_points"))
    acquisition_goal = answers.get("acquisition_goal") or ""
    constraints = _normalize_list(answers.get("constraints_and_guardrails"))

    one_liner_parts = [part for part in [primary_offer, differentiator] if part]
    one_liner = f"{company_name}: {' '.join(one_liner_parts)}".strip()
    if not one_liner_parts:
        one_liner = company_name

    positioning_statement = (
        f"For {customer_title}, {company_name} solves {core_problem}. "
        f"We do this through {primary_offer}. "
        f"Our edge is {differentiator}."
    ).strip()

    competitor_objects = [
        {"name": name, "type": "direct"} for name in competitor_names[:8]
    ]
    channel_objects: List[Dict[str, str]] = []
    for index, channel in enumerate(channels[:8]):
        priority = (
            "primary" if index == 0 else "secondary" if index <= 2 else "experimental"
        )
        channel_objects.append({"name": channel, "priority": priority})

    facts: List[Dict[str, Any]] = []
    if pricing_model:
        facts.append(
            {
                "id": "f-pricing",
                "category": "pricing",
                "label": "Pricing Model",
                "value": pricing_model,
                "confidence": 0.8,
            }
        )
    if acquisition_goal:
        facts.append(
            {
                "id": "f-goal",
                "category": "growth",
                "label": "Acquisition Goal",
                "value": acquisition_goal,
                "confidence": 0.82,
            }
        )
    for idx, item in enumerate(proof_points[:10], start=1):
        facts.append(
            {
                "id": f"f-proof-{idx}",
                "category": "traction",
                "label": f"Proof Point {idx}",
                "value": item,
                "confidence": 0.86,
            }
        )

    business_context = {
        "version": "2.1",
        "generated_at": _utc_now_iso(),
        "session_id": str(uuid4()),
        "company_profile": {
            "name": company_name,
            "website": company_website,
            "industry": industry,
            "stage": stage,
            "description": description,
        },
        "intelligence": {
            "evidence_count": len(facts),
            "facts": facts,
            "icps": [
                {
                    "name": customer_title,
                    "demographics": {
                        "role": customer_title,
                        "stage": stage,
                        "location": geography,
                        "ageRange": "",
                        "income": "",
                    },
                    "psychographics": {
                        "beliefs": customer_profile,
                        "identity": customer_profile,
                        "fears": core_problem,
                        "values": goals[:5],
                        "hangouts": channels[:5],
                        "triggers": pain_points[:5],
                    },
                    "painPoints": pain_points,
                    "goals": goals,
                    "objections": [],
                    "marketSophistication": 3,
                }
            ],
            "positioning": {
                "category": primary_offer,
                "categoryPath": "bold",
                "uvp": differentiator or primary_offer,
                "differentiators": [differentiator] + proof_points[:3]
                if differentiator
                else proof_points[:4],
                "competitors": competitor_objects,
            },
            "messaging": {
                "oneLiner": one_liner,
                "positioningStatement": positioning_statement,
                "valueProps": [
                    {"title": "Primary Offer", "description": primary_offer}
                ],
                "brandVoice": {
                    "tone": tone,
                    "doList": constraints[:5],
                    "dontList": banned[:5],
                },
                "soundbites": [one_liner],
                "guardrails": constraints
                + [f"Avoid phrase: {item}" for item in banned[:3]],
            },
            "channels": channel_objects,
            "market": {
                "tam": "",
                "sam": "",
                "som": "",
                "geo": geography,
                "primary_goal": acquisition_goal,
            },
        },
    }

    return business_context


def _build_onboarding_status(
    workspace_id: str,
    settings: Dict[str, Any],
) -> OnboardingStatusResponse:
    onboarding = (
        settings.get("onboarding")
        if isinstance(settings.get("onboarding"), dict)
        else {}
    )
    raw_answers = (
        onboarding.get("answers") if isinstance(onboarding.get("answers"), dict) else {}
    )
    answers = _normalize_onboarding_answers(raw_answers)

    missing_required = _missing_required_steps(answers)
    completion_pct = _required_completion_pct(answers)
    answered_steps = _answered_steps_count(answers)

    bcm_from_settings = bool(settings.get("bcm_ready")) or bool(
        (settings.get("bcm") or {}).get("ready")
    )
    bcm_from_store = bcm_service.get_latest(workspace_id) is not None
    bcm_ready = bcm_from_settings or bcm_from_store

    completed = bool(onboarding.get("completed")) and not missing_required and bcm_ready
    if not completed and not missing_required and bcm_ready:
        completed = True
    if completed:
        completion_pct = 100

    next_step_id = missing_required[0] if missing_required else None

    return OnboardingStatusResponse(
        workspace_id=workspace_id,
        schema_version=str(
            onboarding.get("schema_version") or ONBOARDING_SCHEMA_VERSION
        ),
        completed=completed,
        bcm_ready=bcm_ready,
        completion_pct=completion_pct,
        answered_steps=answered_steps,
        total_steps=len(CANONICAL_ONBOARDING_STEPS),
        required_steps=len(_REQUIRED_STEP_IDS),
        missing_required_steps=missing_required,
        next_step_id=next_step_id,
        answers=answers,
        updated_at=onboarding.get("updated_at"),
    )


def _ensure_workspace_id(workspace_id: str) -> None:
    try:
        UUID(workspace_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid workspace_id"
        )


def _get_workspace_row(workspace_id: str) -> Dict[str, Any]:
    supabase = get_supabase_client()
    result = (
        supabase.table("workspaces")
        .select("*")
        .eq("id", workspace_id)
        .limit(1)
        .execute()
    )
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
        )
    return result.data[0]


def _update_workspace_settings(
    workspace_id: str, settings: Dict[str, Any]
) -> Dict[str, Any]:
    supabase = get_supabase_client()
    result = (
        supabase.table("workspaces")
        .update({"settings": settings})
        .eq("id", workspace_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update settings",
        )
    return result.data[0]


def _mark_bcm_ready(
    workspace_row: Dict[str, Any],
    onboarding_answers: Dict[str, Any],
    bcm_payload: Dict[str, Any],
    business_context: Dict[str, Any],
) -> Dict[str, Any]:
    settings = _workspace_settings(workspace_row).copy()
    now_iso = _utc_now_iso()

    settings["onboarding"] = {
        "schema_version": ONBOARDING_SCHEMA_VERSION,
        "completed": True,
        "completed_at": now_iso,
        "updated_at": now_iso,
        "answers": onboarding_answers,
        "total_steps": len(CANONICAL_ONBOARDING_STEPS),
        "required_steps": len(_REQUIRED_STEP_IDS),
    }
    settings["business_context"] = business_context
    settings["bcm"] = {
        "ready": True,
        "version": bcm_payload.get("version"),
        "checksum": bcm_payload.get("checksum"),
        "completion_pct": bcm_payload.get("completion_pct", 0),
        "synthesized": bcm_payload.get("synthesized", False),
        "updated_at": now_iso,
    }
    settings["bcm_ready"] = True
    settings["orchestrator"] = "langgraph"

    return settings


def _is_workspace_settings_patch_valid(settings_patch: Dict[str, Any]) -> bool:
    return isinstance(settings_patch, dict)


def _build_default_settings(
    existing: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    base = existing.copy() if isinstance(existing, dict) else {}
    onboarding = (
        base.get("onboarding") if isinstance(base.get("onboarding"), dict) else {}
    )

    onboarding.setdefault("schema_version", ONBOARDING_SCHEMA_VERSION)
    onboarding.setdefault("completed", False)
    onboarding.setdefault("answers", {})
    onboarding.setdefault("total_steps", len(CANONICAL_ONBOARDING_STEPS))
    onboarding.setdefault("required_steps", len(_REQUIRED_STEP_IDS))
    onboarding.setdefault("updated_at", _utc_now_iso())

    base["onboarding"] = onboarding
    base.setdefault("bcm_ready", False)
    base.setdefault("orchestrator", "langgraph")
    return base


async def _insert_workspace(payload: Dict[str, Any]) -> Dict[str, Any]:
    supabase = get_supabase_client()
    result = supabase.table("workspaces").insert(payload).execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create workspace",
        )
    return result.data[0]


def _upsert_foundation_from_business_context(
    workspace_id: str, business_context: Dict[str, Any]
) -> None:
    try:
        supabase = get_supabase_client()
        company = business_context.get("company_profile", {})
        intel = business_context.get("intelligence", {})
        messaging = intel.get("messaging", {})

        row = {
            "workspace_id": workspace_id,
            "company_info": {
                "name": company.get("name", ""),
                "website": company.get("website", ""),
                "industry": company.get("industry", ""),
                "stage": company.get("stage", ""),
                "description": company.get("description", ""),
            },
            "mission": company.get("description", ""),
            "value_proposition": (intel.get("positioning", {}) or {}).get("uvp", ""),
            "brand_voice": messaging.get("brandVoice", {}),
            "messaging": messaging,
            "status": "active",
        }
        supabase.table("foundations").upsert(row, on_conflict="workspace_id").execute()
    except Exception as exc:
        logger.warning(
            "Failed to upsert foundation during onboarding completion: %s", exc
        )


async def _seed_workspace_foundation(
    workspace_id: str, template_type: TemplateType
) -> None:
    """Seed foundation data for a workspace from template."""
    try:
        supabase = get_supabase_client()
        template = get_template(template_type)
        foundation_data = extract_foundation_data(template)
        foundation_data["workspace_id"] = workspace_id

        result = supabase.table("foundations").insert(foundation_data).execute()
        if result.data:
            logger.info(
                "Seeded foundation for workspace %s from %s template",
                workspace_id,
                template_type,
            )
        else:
            logger.warning("Failed to seed foundation for workspace %s", workspace_id)
    except Exception as exc:
        logger.error("Error seeding foundation for workspace %s: %s", workspace_id, exc)


@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(workspace: WorkspaceCreate) -> WorkspaceResponse:
    """
    Create a workspace with deterministic onboarding defaults.

    If DEFAULT_BUSINESS_TEMPLATE is configured, foundation data is seeded from that template.
    """
    base_slug = workspace.slug or _slugify(workspace.name)
    settings = _build_default_settings(workspace.settings or {})

    last_error: Optional[Exception] = None
    created_workspace: Optional[Dict[str, Any]] = None
    for attempt in range(0, 6):
        slug = base_slug if attempt == 0 else f"{base_slug}-{uuid4().hex[:6]}"
        payload = {
            "id": str(uuid4()),
            "name": workspace.name,
            "slug": slug,
            "settings": settings,
        }
        try:
            created_workspace = await _insert_workspace(payload)
            break
        except Exception as exc:
            last_error = exc
            if _is_slug_collision_error(exc):
                continue
            raise

    if not created_workspace:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workspace (slug collision). Last error: {last_error}",
        )

    config = get_settings()
    if config.DEFAULT_BUSINESS_TEMPLATE:
        await _seed_workspace_foundation(
            workspace_id=created_workspace["id"],
            template_type=config.DEFAULT_BUSINESS_TEMPLATE,
        )

    return WorkspaceResponse(**created_workspace)


@router.get("/onboarding/steps", response_model=OnboardingStepsResponse)
async def get_onboarding_steps() -> OnboardingStepsResponse:
    steps = [OnboardingStepOut(**step) for step in CANONICAL_ONBOARDING_STEPS]
    return OnboardingStepsResponse(
        schema_version=ONBOARDING_SCHEMA_VERSION,
        total_steps=len(CANONICAL_ONBOARDING_STEPS),
        required_steps=len(_REQUIRED_STEP_IDS),
        steps=steps,
    )


@router.get(
    "/{workspace_id}/onboarding/status", response_model=OnboardingStatusResponse
)
async def get_onboarding_status(workspace_id: str) -> OnboardingStatusResponse:
    _ensure_workspace_id(workspace_id)
    row = _get_workspace_row(workspace_id)
    settings = _workspace_settings(row)
    status_payload = _build_onboarding_status(workspace_id, settings)
    return status_payload


@router.post(
    "/{workspace_id}/onboarding/complete", response_model=OnboardingCompleteResponse
)
async def complete_onboarding(
    workspace_id: str,
    payload: OnboardingCompleteRequest,
) -> OnboardingCompleteResponse:
    _ensure_workspace_id(workspace_id)
    workspace_row = _get_workspace_row(workspace_id)
    settings = _workspace_settings(workspace_row)

    normalized_answers = _normalize_onboarding_answers(payload.answers)
    missing_required = _missing_required_steps(normalized_answers)
    if missing_required:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Missing required onboarding steps",
                "missing_required_steps": missing_required,
            },
        )

    business_context = _build_business_context(workspace_row, normalized_answers)
    bcm_row = await langgraph_context_orchestrator.seed(workspace_id, business_context)
    bcm_payload = format_bcm_row(bcm_row)

    _upsert_foundation_from_business_context(workspace_id, business_context)

    next_settings = settings.copy()
    next_settings.update(
        _mark_bcm_ready(
            workspace_row=workspace_row,
            onboarding_answers=normalized_answers,
            bcm_payload=bcm_payload,
            business_context=business_context,
        )
    )
    updated_workspace = _update_workspace_settings(workspace_id, next_settings)

    onboarding_status = _build_onboarding_status(workspace_id, next_settings)
    workspace_response = WorkspaceResponse(**updated_workspace)

    return OnboardingCompleteResponse(
        workspace=workspace_response,
        onboarding=onboarding_status,
        bcm=bcm_payload,
        business_context=business_context,
    )


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(workspace_id: str) -> WorkspaceResponse:
    _ensure_workspace_id(workspace_id)
    row = _get_workspace_row(workspace_id)
    row["settings"] = _build_default_settings(_workspace_settings(row))
    return WorkspaceResponse(**row)


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: str, updates: WorkspaceUpdate
) -> WorkspaceResponse:
    _ensure_workspace_id(workspace_id)

    update_data: Dict[str, Any] = {}
    if updates.name is not None:
        update_data["name"] = updates.name
    if updates.slug is not None:
        update_data["slug"] = updates.slug
    if updates.settings is not None:
        if not _is_workspace_settings_patch_valid(updates.settings):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid settings payload",
            )
        current_row = _get_workspace_row(workspace_id)
        existing_settings = _workspace_settings(current_row)
        merged_settings = existing_settings.copy()
        merged_settings.update(updates.settings)
        update_data["settings"] = merged_settings

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update"
        )

    supabase = get_supabase_client()
    result = (
        supabase.table("workspaces")
        .update(update_data)
        .eq("id", workspace_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
        )

    row = result.data[0]
    row["settings"] = _build_default_settings(_workspace_settings(row))
    return WorkspaceResponse(**row)
