# Autonomous Research Agent (300 Iterations) - Design Spec

## Goal
Build a production-oriented autonomous research agent that runs for exactly 300 iterations, performs web search, extracts actionable insights, continuously updates an evolving design, and logs every iteration with a strict machine-readable JSON schema.

The implementation prioritizes:
- Long-horizon reliability (bounded drift, bounded memory)
- Explicit provenance (queries, tools, sources)
- Graceful degradation (tool failures, missing API keys)
- Batching and concurrency (avoid 300 sequential blocking I/O calls)

## Core References (Mapped to Implementation)

### IterResearch (Markovian State Reconstruction)
Principle: do not grow context unbounded; periodically reconstruct a compact workspace representation that is sufficient for the next decision.

Implementation mapping:
- `LongTermMemory` stores compressed insight chunks.
- `recent_insights` and `recent_sources` are capped rolling windows.
- `synthesis_every` triggers periodic compression; after synthesis, the working set is reset to prevent context suffocation.

### ADP-MA (Hierarchical Meta-Agents)
Principle: separate responsibilities into meta-agents to improve stability.

Implementation mapping:
- `QuestionPlanner` acts as the Orchestrator (theme scheduling and question generation).
- `Architect` proposes design updates from observations.
- `Monitor` enforces redundancy constraints and provides next-step guidance.

### AICL (Control Loop Architecture)
Principle: structured plan -> execution -> monitoring -> adaptation with bounded budgets.

Implementation mapping:
- Batched loop: plan batch -> search batch -> per-iteration synthesis/reflection -> log.
- Tool circuit breaker: disable a tool temporarily after repeated failures.

## Repository Layout
All implementation lives in `research_agent/`:
- `research_agent.py` - main agent, 300-iteration runner, state machine
- `research_log.py` - strict JSON schema + JSONL writer
- `search_tools.py` - async web search tools + aggregation
- `design_spec.md` - this document
- `implementation_checklist.md` - engineering plan
- `example_usage.py` - runnable example

## External Integrations
Search tools are optional and independently configured via environment variables:
- Exa: `EXA_API_KEY`
- Google Programmable Search: `GOOGLE_CSE_API_KEY`, `GOOGLE_CSE_CX`
- SerpAPI: `SERPAPI_API_KEY`

If a tool is not configured or errors, the system continues and logs the failure in the iteration's provenance.

## Data Contracts

### Per-Iteration JSON Log Schema (Required)
Each iteration emits one JSON object (JSONL) with exactly these keys:

```json
{
  "iteration": 1,
  "timestamp": "2026-02-15T12:00:00+00:00",
  "research_question": "<focused question>",
  "search_tools_used": ["google", "exa"],
  "queries": ["<query 1>", "<query 2>"],
  "top_sources": [
    {"url": "https://...", "title": "...", "snippet": "...", "tool": "exa"}
  ],
  "key_insights": ["..."],
  "design_updates": ["..."],
  "next_steps_hint": "<strategy>"
}
```

### Source Objects
`top_sources` is a list of objects with at least `url`, and may include:
- `title`
- `snippet`
- `score`
- `published`
- `tool`

## State Model (LangGraph-Style)

The agent uses an explicit state object (`ResearchState`) and a small graph-like executor (`StateGraph`) to model a node pipeline.

Conceptual nodes:
1. `plan` - choose iteration question and queries
2. `search` - run tool queries concurrently
3. `synthesize` - extract insights, update memory, update design notes
4. `monitor` - redundancy checks, tool health checks
5. `log` - emit strict JSON entry

Implementation note:
- Search is executed in batches to avoid per-iteration blocking.
- Logging is non-blocking via a background writer thread.

## Research Loop (300 Iterations)

### Batch Planning
The loop advances in batches of size `batch_size`:
- Plan `IterationPlan` objects for `[i..i+batch_size-1]`.
- Each plan has a single focused question and `queries_per_iteration` query variants.

### Batch Search Execution
All planned queries are searched concurrently across configured tools.
- Concurrency is bounded by `max_concurrency`.
- Each tool call is time-bounded by `per_request_timeout_s`.

### Per-Iteration Processing
For each iteration in the batch:
- Merge and dedupe sources across tools.
- Extract `key_insights` from sources.
- Generate `design_updates` using rule-based signals.
- Apply redundancy guardrails (query cooldown, similarity threshold).
- Optionally synthesize (compress memory) every `synthesis_every` iterations.
- Emit strict JSON log entry.

## Memory Management

### Working Memory
Bounded deques:
- `recent_queries`: last N normalized queries + token sets
- `recent_insights`: last M extracted insights
- `recent_sources`: last K sources

### Long-Term Memory (Reconstruction)
`LongTermMemory` stores bounded `MemoryChunk` objects:
- Each chunk summarizes a window of iterations with a small set of deduped insights.
- Chunks are capped by `keep_long_term_chunks`.

### Synthesis Algorithm
At `synthesis_every`:
- Rank insights by repeated keywords.
- Deduplicate by high similarity.
- Store top insights + recent sources in a memory chunk.
- Clear working insight/source windows to prevent context suffocation.

## Reflection / Redundancy Control

### Query Redundancy
Before scheduling a query:
- Normalize and tokenize.
- Skip if exact match appeared within `query_cooldown_iters`.
- Skip if Jaccard similarity >= `query_similarity_threshold` within the cooldown window.

### Next-Step Guidance
`Monitor.next_steps_hint` produces a short strategy hint based on:
- Tool failures (diversify tools/queries)
- Synthesis boundaries (compress and update plan)

## Graceful Degradation

Failure modes handled:
- Missing API keys: tool is treated as unconfigured.
- HTTP failures, rate limits, timeouts: recorded and the iteration continues.
- Logger queue pressure: log entries may be dropped rather than blocking.

## Stability Budgets / Circuit Breakers

Tool circuit breaker:
- Track consecutive failures per tool.
- Disable a tool for `tool_circuit_breaker_disable_iters` after `tool_circuit_breaker_failures` consecutive failures.

This bounds latency and reduces repeated error loops.

## Production Notes
Recommended additions for deployment:
- Persist agent state snapshots (resume after crash)
- Token/latency accounting per tool call
- Configurable source allow/deny lists
- Pluggable LLM-based summarization (optional) for higher-quality synthesis
