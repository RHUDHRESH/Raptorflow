# ADR-0005: BCM Cognitive Identity

## Status
Accepted

## Context
The Business Context Manifest (BCM) is currently a static data compressor — `bcm_reducer.py` truncates/extracts fields from `business_context.json` into a ~4KB JSON blob. The Muse AI content generator injects this blob as a flat `Context: {json}` string into prompts sent to Gemini 2.0 Flash. This produces mediocre output because:

1. No brand identity/voice synthesis — the BCM is anonymous data
2. No structured prompt engineering — flat context dump wastes the model's attention
3. No memory/learning — each generation is independent, no feedback loop
4. No caching — every request hits Supabase cold

## Decision
Transform the BCM into a **full cognitive identity system** with 5 pillars:

1. **AI-Powered Synthesis Engine** — Replace the static reducer with a Gemini Flash-powered synthesizer that generates brand DNA, few-shot prompt templates, and smart guardrails at ingestion time
2. **Upstash Redis Caching** — Hot cache for manifests and pre-compiled system prompts
3. **Structured Prompt Engineering** — Replace flat context injection with proper system prompts using BCM identity, ICP voice maps, and few-shot examples
4. **Memory + Feedback Loop** — New tables for generation logs, user feedback, and accumulated memories
5. **Periodic Self-Reflection** — Background job that analyzes feedback and re-synthesizes BCM

**Model strategy:** Keep Gemini 2.0 Flash. Front-load strategic thinking into the BCM at ingestion time so Flash just follows a pre-built playbook at runtime.

**Caching strategy:** Upstash Redis (hot, TTL-based) + Supabase (cold, persistent).

## Alternatives Considered
- **Multi-model pipeline** (use Pro for synthesis, Flash for runtime) — rejected to avoid cost/complexity
- **Fine-tuning** — rejected; not practical for per-workspace customization
- **Supabase-only caching** — rejected; Redis provides ~2ms vs ~200ms reads

## Consequences
- BCM manifest grows beyond 4KB (new identity/prompt_kit/guardrails sections)
- Ingestion becomes async (AI synthesis takes ~2-5s)
- New Supabase tables: `bcm_memories`, `bcm_generation_log`
- New dependency: `upstash-redis` Python package
- Backward compatible: existing API contracts preserved, static reducer kept as fallback
