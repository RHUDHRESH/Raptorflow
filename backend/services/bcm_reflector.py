"""
BCM Reflector: periodic self-reflection that analyzes feedback and improves the BCM.

Collects recent generation logs + feedback, sends them to Gemini Flash for
pattern analysis, then creates new memories and optionally triggers a BCM rebuild
with enriched data.

Trigger mechanisms:
- Manual: POST /api/context/reflect
- Automatic: after every N generations (configurable, default 20)
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

REFLECTION_GENERATION_THRESHOLD = 20

REFLECTION_PROMPT = """You are analyzing the performance of a business content generation system to improve its future output.

## RECENT GENERATIONS WITH FEEDBACK

{generations_json}

## CURRENT BCM IDENTITY

{identity_json}

## TASK

Analyze the generations and feedback above. Produce a JSON object with:

{{
  "insights": [
    {{
      "type": "preference|correction|pattern",
      "summary": "One-sentence description of what you learned",
      "confidence": 0.0-1.0,
      "evidence": "Brief reference to which generation(s) support this"
    }}
  ],
  "updated_guardrails": {{
    "add_positive": ["New positive patterns to add (if any)"],
    "add_negative": ["New negative patterns to add (if any)"],
    "remove": ["Existing patterns that should be removed (if any)"]
  }},
  "few_shot_updates": {{
    "content_type": ["New example to replace a weak one (only if a generation scored 5/5)"]
  }},
  "voice_refinements": {{
    "add_vocabulary": ["Words that appeared in highly-rated outputs"],
    "add_anti_vocabulary": ["Words that appeared in poorly-rated outputs"]
  }}
}}

Rules:
- Only produce insights supported by actual feedback data
- Be conservative — only suggest changes with clear evidence
- If there isn't enough data to draw conclusions, return empty arrays
- Output ONLY valid JSON, no markdown fences
"""


def _get_vertex_service():
    """Lazy import to avoid circular deps."""
    try:
        from backend.services.vertex_ai_service import vertex_ai_service
        return vertex_ai_service
    except Exception:
        return None


def _parse_reflection_response(raw_text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON from model response."""
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        start = 1
        end = len(lines) - 1
        for i in range(len(lines) - 1, 0, -1):
            if lines[i].strip() == "```":
                end = i
                break
        text = "\n".join(lines[start:end])

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        brace_start = text.find("{")
        brace_end = text.rfind("}")
        if brace_start != -1 and brace_end != -1:
            try:
                return json.loads(text[brace_start:brace_end + 1])
            except json.JSONDecodeError:
                pass
    return None


async def reflect(workspace_id: str) -> Dict[str, Any]:
    """Run a reflection cycle for a workspace.

    1. Fetch recent rated generations
    2. Fetch current BCM identity
    3. Send to Gemini Flash for analysis
    4. Store insights as memories
    5. Update BCM meta with reflection timestamp

    Returns a summary of what was learned.
    """
    from backend.services import bcm_service, bcm_generation_logger, bcm_memory

    # 0. Garbage collection — prune old data before analysis
    try:
        bcm_memory.cleanup_old_memories(workspace_id)
        bcm_generation_logger.cleanup_old_generations(workspace_id)
    except Exception as exc:
        logger.warning("Cleanup failed during reflection: %s", exc)

    # 1. Get rated generations
    rated = bcm_generation_logger.get_rated_generations(workspace_id, limit=20)
    if not rated:
        return {"status": "skipped", "reason": "No rated generations to reflect on"}

    # 2. Get current BCM
    bcm_row = bcm_service.get_latest(workspace_id)
    manifest = bcm_row["manifest"] if bcm_row else {}
    identity = manifest.get("identity", {})

    # 3. Prepare generation summaries for the prompt
    gen_summaries = []
    for g in rated:
        gen_summaries.append({
            "content_type": g.get("content_type", ""),
            "output_preview": (g.get("output", ""))[:300],
            "feedback_score": g.get("feedback_score"),
            "user_edits": g.get("user_edits", ""),
        })

    # 4. Call Gemini Flash for reflection
    vertex = _get_vertex_service()
    if not vertex:
        return {"status": "error", "reason": "Vertex AI not available"}

    prompt = REFLECTION_PROMPT.format(
        generations_json=json.dumps(gen_summaries, indent=2),
        identity_json=json.dumps(identity, indent=2) if identity else "{}",
    )

    result = await vertex.generate_text(
        prompt=prompt,
        workspace_id=workspace_id,
        user_id="bcm_reflector",
        max_tokens=2000,
        temperature=0.3,
    )

    if result.get("status") != "success":
        return {"status": "error", "reason": result.get("error", "Generation failed")}

    parsed = _parse_reflection_response(result.get("text", ""))
    if not parsed:
        return {"status": "error", "reason": "Failed to parse reflection response"}

    # 5. Store insights as memories
    insights = parsed.get("insights", [])
    memories_created = 0
    for insight in insights:
        try:
            bcm_memory.add_memory(
                workspace_id=workspace_id,
                memory_type=insight.get("type", "insight"),
                content={
                    "summary": insight.get("summary", ""),
                    "evidence": insight.get("evidence", ""),
                    "source_data": "reflection",
                },
                source="reflection",
                confidence=insight.get("confidence", 0.5),
            )
            memories_created += 1
        except Exception as exc:
            logger.warning("Failed to store reflection insight: %s", exc)

    # 6. Store guardrail/vocabulary updates as memories
    guardrail_updates = parsed.get("updated_guardrails", {})
    if any(guardrail_updates.get(k) for k in ("add_positive", "add_negative", "remove")):
        try:
            bcm_memory.add_memory(
                workspace_id=workspace_id,
                memory_type="pattern",
                content={
                    "summary": "Guardrail updates from reflection",
                    "guardrail_updates": guardrail_updates,
                },
                source="reflection",
                confidence=0.7,
            )
            memories_created += 1
        except Exception as exc:
            logger.warning("Failed to store guardrail update: %s", exc)

    voice_updates = parsed.get("voice_refinements", {})
    if any(voice_updates.get(k) for k in ("add_vocabulary", "add_anti_vocabulary")):
        try:
            bcm_memory.add_memory(
                workspace_id=workspace_id,
                memory_type="preference",
                content={
                    "summary": "Voice refinements from reflection",
                    "voice_updates": voice_updates,
                },
                source="reflection",
                confidence=0.6,
            )
            memories_created += 1
        except Exception as exc:
            logger.warning("Failed to store voice update: %s", exc)

    # 7. Rebuild BCM with enriched data (triggers new synthesis with latest memories)
    try:
        from backend.services.bcm_synthesizer import synthesize_business_context

        source = bcm_row.get("source_context")
        if source:
            new_version = manifest.get("version", 0) + 1
            new_manifest = await synthesize_business_context(
                business_context=source,
                workspace_id=workspace_id,
                version=new_version,
                source="reflection",
            )
            # Update meta with reflection timestamp and memory count
            new_manifest["meta"]["last_reflection_at"] = datetime.now(timezone.utc).isoformat()
            new_manifest["meta"]["memory_count"] = bcm_memory.get_memory_summary(workspace_id).get(
                "total_count", 0
            )
            # Recompute checksum with updated meta
            new_manifest["checksum"] = ""
            manifest_json = json.dumps(new_manifest, sort_keys=True, separators=(",", ":"))
            new_manifest["checksum"] = hashlib.sha256(manifest_json.encode()).hexdigest()[:16]
            new_manifest["meta"]["token_estimate"] = len(manifest_json) // 4

            from backend.services import bcm_cache
            bcm_cache.invalidate(workspace_id)
            bcm_service.store_manifest(workspace_id, new_manifest, source)
    except Exception as exc:
        logger.warning("Failed to rebuild BCM after reflection: %s", exc)

    logger.info(
        "Reflection complete for workspace %s: %d insights, %d memories created",
        workspace_id, len(insights), memories_created,
    )

    return {
        "status": "success",
        "insights_found": len(insights),
        "memories_created": memories_created,
        "guardrail_updates": bool(any(guardrail_updates.get(k) for k in ("add_positive", "add_negative", "remove"))),
        "voice_updates": bool(any(voice_updates.get(k) for k in ("add_vocabulary", "add_anti_vocabulary"))),
        "generations_analyzed": len(rated),
    }


def should_auto_reflect(workspace_id: str) -> bool:
    """Check if a workspace has enough new generations to trigger auto-reflection."""
    from backend.services import bcm_generation_logger, bcm_service

    bcm_row = bcm_service.get_latest(workspace_id)
    if not bcm_row:
        return False

    manifest = bcm_row.get("manifest", {})
    last_reflection = manifest.get("meta", {}).get("last_reflection_at")

    if not last_reflection:
        # Never reflected — check if we have enough rated generations
        rated = bcm_generation_logger.get_rated_generations(workspace_id, limit=1)
        all_gens = bcm_generation_logger.get_recent_generations(workspace_id, limit=REFLECTION_GENERATION_THRESHOLD + 1)
        return len(all_gens) >= REFLECTION_GENERATION_THRESHOLD and len(rated) > 0

    # Check generations since last reflection
    recent = bcm_generation_logger.get_recent_generations(
        workspace_id, limit=REFLECTION_GENERATION_THRESHOLD + 1,
    )
    new_since = [
        g for g in recent
        if g.get("created_at", "") > last_reflection
    ]
    return len(new_since) >= REFLECTION_GENERATION_THRESHOLD
