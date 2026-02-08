"""
BCM Synthesizer: AI-powered synthesis of business_context.json into a cognitive BCM manifest.

Replaces the static bcm_reducer with Gemini Flash-powered analysis that produces:
- Brand identity (voice archetype, communication style, vocabulary DNA)
- Prompt kit (system prompts, few-shot examples per content type, ICP voice maps)
- Evolved guardrails (positive + negative patterns, competitive rules, tone calibration)

Falls back to the static reducer if AI synthesis fails.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from backend.services.bcm_reducer import reduce_business_context

logger = logging.getLogger(__name__)

# ── Synthesis prompt ─────────────────────────────────────────────────────────

SYNTHESIS_PROMPT = """You are a brand strategist and cognitive scientist. Your job is to deeply understand a business from raw data and produce a structured brand identity document.

Analyze the business context below like a CMO who has spent 6 months immersed in this business. You must produce ONLY valid JSON matching the exact schema specified.

## SCHEMA

{
  "identity": {
    "voice_archetype": "A short archetype label, e.g. 'The Technical Mentor', 'The Bold Challenger', 'The Trusted Advisor'",
    "communication_style": "2-3 sentence description of how this brand communicates",
    "emotional_register": "The emotional tone, e.g. 'Confident but empathetic', 'Urgent and passionate'",
    "vocabulary_dna": ["5-8 power words the brand should use frequently"],
    "anti_vocabulary": ["5-8 words the brand should NEVER use"],
    "sentence_patterns": ["3-5 characteristic sentence structures, e.g. 'Lead with the problem, then the solution'"],
    "perspective": "How the brand refers to itself: 'we', 'I', or company name"
  },
  "prompt_kit": {
    "system_prompt": "A 150-250 word system prompt that encodes this brand's identity for an AI content generator. Written in second person ('You are...'). Must include voice, positioning, audience awareness, and key constraints.",
    "content_templates": {
      "email": "A 50-word instruction template for generating emails in this brand's voice",
      "blog": "A 50-word instruction template for generating blog posts",
      "social": "A 50-word instruction template for generating social media posts",
      "ad_copy": "A 50-word instruction template for generating ad copy"
    },
    "few_shot_examples": {
      "email": ["One example email subject line + first paragraph in this brand's voice (100-150 words)"],
      "social": ["One example social media post in this brand's voice (50-80 words)"],
      "blog": ["One example blog intro paragraph in this brand's voice (100-150 words)"]
    },
    "icp_voice_map": {
      "<icp_name>": "A 30-word note on how to adapt the voice for this specific audience"
    }
  },
  "guardrails_v2": {
    "positive_patterns": ["5-7 rules of what the brand SHOULD always do, e.g. 'Always lead with the customer pain point before presenting the solution'"],
    "negative_patterns": ["5-7 rules of what the brand should NEVER do"],
    "competitive_rules": ["3-5 rules for how to handle competitor mentions"],
    "tone_calibration": {
      "formality": 0.0-1.0,
      "technical_depth": 0.0-1.0,
      "urgency": 0.0-1.0,
      "warmth": 0.0-1.0,
      "confidence": 0.0-1.0
    }
  }
}

## EXAMPLE INPUT (SaaS company)

{
  "company_profile": {"name": "AcmeSync", "industry": "SaaS / Data Integration", "stage": "Series B"},
  "intelligence": {
    "positioning": {"uvp": "Real-time data sync for enterprise teams", "differentiators": ["Sub-second latency", "No-code setup"]},
    "messaging": {"oneLiner": "AcmeSync: Your data, everywhere, instantly.", "brandVoice": {"tone": ["technical but friendly", "confident"]}},
    "icps": [{"name": "Data Engineer", "painPoints": ["Manual ETL pipelines break weekly"]}]
  }
}

## EXAMPLE OUTPUT

{
  "identity": {
    "voice_archetype": "The Reliable Engineer",
    "communication_style": "Speaks like a senior engineer explaining to a peer — precise, no fluff, respects the reader's time. Uses concrete numbers and real scenarios instead of marketing abstractions.",
    "emotional_register": "Calm confidence with technical empathy",
    "vocabulary_dna": ["real-time", "zero-config", "pipeline", "latency", "scale", "ship"],
    "anti_vocabulary": ["synergy", "leverage", "disrupt", "revolutionary", "game-changing", "seamless"],
    "sentence_patterns": ["State the pain, then the fix in the same sentence", "Use numbers before adjectives", "Short sentences for impact, longer for explanation"],
    "perspective": "we"
  },
  "prompt_kit": {
    "system_prompt": "You are the voice of AcmeSync, a data integration platform for enterprise teams. You speak like a senior engineer — precise, no fluff, technically credible. Always lead with the specific problem the reader faces, then show how real-time sync solves it. Use concrete numbers (latency, uptime, time saved). Never use corporate buzzwords. Your audience is data engineers and technical leaders who are skeptical of marketing claims. Ground every statement in a real workflow scenario. Tone: confident but not arrogant, technical but accessible.",
    "content_templates": {
      "email": "Write a concise email in AcmeSync's voice. Lead with the recipient's pain point. One clear CTA. No buzzwords. Include a specific metric or scenario.",
      "blog": "Write a technical blog post intro for AcmeSync. Start with a real engineering scenario. Be specific about the problem. Transition to the solution with data.",
      "social": "Write a LinkedIn post for AcmeSync. Hook with a surprising stat or pain point. Keep under 150 words. End with a question or insight, not a sales pitch.",
      "ad_copy": "Write ad copy for AcmeSync. Lead with the outcome (time/money saved). One sentence max for the product description. Strong CTA."
    },
    "few_shot_examples": {
      "email": ["Subject: Your ETL pipeline broke again last Tuesday\\n\\nEvery Tuesday at 3am, your Airflow DAG fails on the customer_events table. Your team spends 4 hours fixing it. Every week.\\n\\nAcmeSync eliminates that entirely. Real-time sync with sub-second latency, zero config. Your data just works — Tuesday, Wednesday, every day.\\n\\nWant to see it running on your stack? 15-minute demo, no slides."],
      "social": ["Hot take: If your data team spends more time fixing pipelines than building products, you don't have a data problem — you have a plumbing problem.\\n\\nWe built AcmeSync because 73% of data engineering time goes to maintenance, not innovation. Sub-second sync. Zero config. Your data, everywhere, instantly.\\n\\nWhat's your team's pipeline-to-product ratio?"],
      "blog": ["Last month, a Series C fintech lost $340K because a batch job failed silently at 2am. Their customer churn dashboard showed green for 18 hours while actual churn spiked 40%.\\n\\nThis isn't a horror story — it's Tuesday for most data teams running batch ETL. At AcmeSync, we built real-time sync because we lived this pain ourselves."]
    },
    "icp_voice_map": {
      "Data Engineer": "Speak peer-to-peer. Use technical specifics (DAGs, latency numbers). Skip the business case — they already know."
    }
  },
  "guardrails_v2": {
    "positive_patterns": ["Always lead with a specific customer pain point before presenting the solution", "Include at least one concrete metric or number in every piece", "Reference real engineering workflows and tools the audience uses", "End emails with a low-friction CTA (demo, not 'contact sales')", "Use active voice and short sentences for key claims"],
    "negative_patterns": ["Never use words like synergy, leverage, disrupt, or game-changing", "Never make claims without grounding them in data or a scenario", "Never start with 'In today's fast-paced world' or similar cliches", "Never use more than one exclamation mark per piece", "Never lead with the product — lead with the problem"],
    "competitive_rules": ["Never name competitors directly in public content", "Position as the technical alternative without bashing", "Focus on what we do differently, not what they do wrong"],
    "tone_calibration": {"formality": 0.4, "technical_depth": 0.8, "urgency": 0.5, "warmth": 0.5, "confidence": 0.85}
  }
}

## YOUR INPUT

"""


def _get_vertex_service():
    """Lazy import to avoid circular deps and allow fallback."""
    try:
        from backend.services.vertex_ai_service import vertex_ai_service
        return vertex_ai_service
    except Exception:
        return None


def _parse_synthesis_response(raw_text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON from model response, handling markdown code fences."""
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        start = 1
        end = len(lines) - 1
        if lines[0].startswith("```json"):
            start = 1
        for i in range(len(lines) - 1, 0, -1):
            if lines[i].strip() == "```":
                end = i
                break
        text = "\n".join(lines[start:end])

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object in the text
        brace_start = text.find("{")
        brace_end = text.rfind("}")
        if brace_start != -1 and brace_end != -1:
            try:
                return json.loads(text[brace_start:brace_end + 1])
            except json.JSONDecodeError:
                pass
    return None


async def synthesize_identity(
    business_context: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Use Gemini Flash to synthesize brand identity from business context.

    Returns dict with keys: identity, prompt_kit, guardrails_v2
    Returns None if synthesis fails (caller should fall back to static reducer).
    """
    vertex = _get_vertex_service()
    if not vertex:
        logger.warning("Vertex AI not available — skipping identity synthesis")
        return None

    prompt = SYNTHESIS_PROMPT + json.dumps(business_context, indent=2)

    try:
        result = await vertex.generate_text(
            prompt=prompt,
            workspace_id="system",
            user_id="bcm_synthesizer",
            max_tokens=4000,
            temperature=0.4,
        )

        if result.get("status") != "success":
            logger.error("Synthesis generation failed: %s", result.get("error"))
            return None

        raw_text = result.get("text", "")
        parsed = _parse_synthesis_response(raw_text)

        if not parsed:
            logger.error("Failed to parse synthesis response as JSON")
            return None

        # Validate expected top-level keys
        expected_keys = {"identity", "prompt_kit", "guardrails_v2"}
        if not expected_keys.issubset(parsed.keys()):
            missing = expected_keys - parsed.keys()
            logger.error("Synthesis response missing keys: %s", missing)
            return None

        logger.info(
            "Identity synthesis succeeded: archetype=%s",
            parsed.get("identity", {}).get("voice_archetype", "unknown"),
        )
        return parsed

    except Exception as exc:
        logger.error("Identity synthesis error: %s", exc, exc_info=True)
        return None


async def synthesize_business_context(
    business_context: Dict[str, Any],
    workspace_id: str,
    version: int = 1,
    source: str = "onboarding",
) -> Dict[str, Any]:
    """Full BCM synthesis: static reduction + AI identity enrichment.

    1. Run the static reducer to get the baseline manifest.
    2. Attempt AI synthesis for identity/prompt_kit/guardrails_v2.
    3. Merge results. If AI fails, the static manifest is returned as-is.
    """
    # Phase 1: Static baseline (always works)
    manifest = reduce_business_context(
        business_context=business_context,
        workspace_id=workspace_id,
        version=version,
        source=source,
    )

    # Phase 2: AI enrichment (best-effort)
    synthesis = await synthesize_identity(business_context)

    if synthesis:
        manifest["identity"] = synthesis.get("identity", {})
        manifest["prompt_kit"] = synthesis.get("prompt_kit", {})
        manifest["guardrails_v2"] = synthesis.get("guardrails_v2", {})
        manifest["meta"]["synthesized"] = True

        # Recompute checksum with enriched content
        manifest["checksum"] = ""
        manifest_json = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
        manifest["checksum"] = hashlib.sha256(manifest_json.encode()).hexdigest()[:16]
        manifest["meta"]["token_estimate"] = len(manifest_json) // 4
    else:
        manifest["identity"] = None
        manifest["prompt_kit"] = None
        manifest["guardrails_v2"] = None
        manifest["meta"]["synthesized"] = False

    return manifest
