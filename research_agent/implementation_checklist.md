# Implementation Checklist

This checklist is organized by priority and risk.

## Now (Production-Critical)
- Logging schema is exact and validated against required keys.
- JSONL writer is non-blocking (background thread) and robust to backpressure.
- Agent loop runs exactly 300 iterations by default.
- Batch planning + concurrent search prevents 300 sequential blocking calls.
- Memory is bounded (rolling windows + capped long-term chunks).
- Synthesis/reconstruction runs on schedule and resets working context.
- Query redundancy guardrails (cooldown + similarity threshold).
- Search tool errors are handled and logged; agent never crashes on tool failure.
- Tool circuit breaker disables repeatedly failing tools temporarily.
- Example script runs end-to-end and produces a JSONL log.

## Experimental (Quality/Performance)
- Add LLM-based synthesis option (pluggable) with strict token budgets.
- Add domain allow/deny lists and source scoring heuristics.
- Add multi-query expansion per theme (deep search) with novelty constraints.
- Add resume-from-log support (rebuild state from JSONL).
- Add structured evaluation: coverage per theme, redundancy metrics, insight novelty.

## Long-Term (Productization)
- Integrate trace-level observability (LangSmith/OpenTelemetry) with trace IDs.
- Add persistent memory store (SQLite/Postgres) with retrieval + dedupe.
- Add human-in-the-loop feedback hooks (approve sources, flag errors).
- Add multi-process scheduling for larger workloads; queue-based tool execution.
- Add policy checks (PII filtering, risky content detection) before storing insights.
- Add benchmark harness comparing strategies (IterResearch-style ablations).
