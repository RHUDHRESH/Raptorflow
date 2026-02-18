"""
BCM Reducer - Transforms raw business context into compact BCM manifest.

Pure function — no I/O, no side effects.
Target: <=4KB JSON, ~1200 tokens.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict

from backend.bcm.core.types import BCMManifest, BCMFoundation, BCMICP


def reduce_business_context(
    business_context: Dict[str, Any],
    workspace_id: str,
    version: int = 1,
    source: str = "onboarding",
) -> Dict[str, Any]:
    """
    Convert a full business_context.json into a compact BCM manifest.

    This is a pure transformation that extracts the essential information
    needed for content generation from a potentially large business context.

    Args:
        business_context: Raw business context dictionary
        workspace_id: Associated workspace ID
        version: Manifest version number
        source: Source of the context (onboarding, rebuild, etc.)

    Returns:
        Compact BCM manifest dictionary
    """
    company = business_context.get("company_profile", {})
    intel = business_context.get("intelligence", {})
    positioning = intel.get("positioning", {})
    messaging = intel.get("messaging", {})
    market = intel.get("market", {})
    facts = intel.get("facts", [])
    raw_icps = intel.get("icps", [])
    raw_channels = intel.get("channels", [])
    competitors = positioning.get("competitors", [])

    foundation = BCMFoundation(
        company=company.get("name", ""),
        industry=company.get("industry", ""),
        stage=company.get("stage", ""),
        mission=company.get("description", "")[:200],
        value_prop=positioning.get("uvp", "")[:300],
    )

    icps = []
    for raw in raw_icps[:5]:
        demo = raw.get("demographics", {})
        psycho = raw.get("psychographics", {})
        icps.append(
            BCMICP(
                name=raw.get("name", ""),
                role=demo.get("role", ""),
                pains=raw.get("painPoints", [])[:3],
                goals=raw.get("goals", [])[:3],
                channels=[h for h in psycho.get("hangouts", [])[:3]],
                triggers=psycho.get("triggers", [])[:3],
            )
        )

    alternatives = [
        {"name": c.get("name", ""), "type": c.get("type", "direct")}
        for c in competitors[:5]
    ]
    differentiators = positioning.get("differentiators", [])
    competitive = {
        "category": positioning.get("category", ""),
        "path": positioning.get("categoryPath", "safe"),
        "alternatives": alternatives,
        "differentiation": differentiators[0] if differentiators else "",
    }

    brand_voice = messaging.get("brandVoice", {})
    bcm_messaging = {
        "one_liner": messaging.get("oneLiner", ""),
        "positioning": messaging.get("positioningStatement", "")[:300],
        "tone": brand_voice.get("tone", [])[:3],
        "guardrails": messaging.get("guardrails", [])[:3],
        "soundbites": messaging.get("soundbites", [])[:3],
    }

    channels = [
        {"name": ch.get("name", ""), "priority": ch.get("priority", "secondary")}
        for ch in raw_channels[:6]
    ]

    bcm_market = {
        "tam": market.get("tam", ""),
        "sam": market.get("sam", ""),
        "som": market.get("som", ""),
    }

    manifest = {
        "version": version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace_id": workspace_id,
        "checksum": "",
        "foundation": {
            "company": foundation.company,
            "industry": foundation.industry,
            "stage": foundation.stage,
            "mission": foundation.mission,
            "value_prop": foundation.value_prop,
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
            for icp in icps
        ],
        "competitive": competitive,
        "messaging": bcm_messaging,
        "channels": channels,
        "market": bcm_market,
        "identity": None,
        "prompt_kit": None,
        "guardrails_v2": None,
        "meta": {
            "source": source,
            "token_estimate": 0,
            "facts_count": len(facts),
            "icps_count": len(icps),
            "competitors_count": len(competitors),
            "synthesized": False,
        },
    }

    manifest_json = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
    manifest["checksum"] = hashlib.sha256(manifest_json.encode()).hexdigest()[:16]
    manifest["meta"]["token_estimate"] = len(manifest_json) // 4

    return manifest
