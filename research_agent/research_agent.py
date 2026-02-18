from __future__ import annotations

import asyncio
import hashlib
import os
import re
from collections import Counter, deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, List, Optional, Sequence, Tuple

from .research_log import JSONLResearchLogger, ResearchLogEntry, Source, utc_now_iso
from .search_tools import (
    AsyncHTTPClient,
    ExaSearchTool,
    GoogleCSESearchTool,
    SerpAPISearchTool,
    ToolRunner,
    ToolSearchResult,
    merge_tool_results,
)


def _normalize_text(s: str) -> str:
    s2 = s.lower().strip()
    s2 = re.sub(r"\s+", " ", s2)
    s2 = re.sub(r"[^a-z0-9 _\-:/\.]+", "", s2)
    return s2


def _tokenize(s: str) -> List[str]:
    s2 = _normalize_text(s)
    toks = re.findall(r"[a-z0-9]{2,}", s2)
    return toks


def _jaccard(a: Sequence[str], b: Sequence[str]) -> float:
    sa = set(a)
    sb = set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    inter = len(sa.intersection(sb))
    union = len(sa.union(sb))
    return inter / float(union)


def _stable_hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="replace")).hexdigest()[:16]


@dataclass
class ResearchAgentConfig:
    research_topic: str
    total_iterations: int = 300
    batch_size: int = 6
    queries_per_iteration: int = 2
    results_per_query: int = 5
    top_sources_per_iteration: int = 8
    log_path: str = "research_agent/research_log.jsonl"
    flush_every: int = 5
    max_recent_queries: int = 250
    query_cooldown_iters: int = 12
    query_similarity_threshold: float = 0.88
    synthesis_every: int = 20
    keep_recent_insights: int = 60
    keep_long_term_chunks: int = 18
    max_insights_per_chunk: int = 12
    max_design_notes: int = 80
    max_concurrency: int = 10
    per_request_timeout_s: float = 20.0
    enabled_tools: Sequence[str] = ("exa", "google", "serpapi")
    tool_circuit_breaker_failures: int = 10
    tool_circuit_breaker_disable_iters: int = 25


@dataclass(frozen=True)
class IterationPlan:
    iteration: int
    research_question: str
    queries: List[str]


@dataclass
class MemoryChunk:
    chunk_id: str
    created_at: str
    iteration_start: int
    iteration_end: int
    insights: List[str]
    sources: List[Dict[str, Any]]


class LongTermMemory:
    def __init__(
        self,
        *,
        keep_chunks: int,
        max_insights_per_chunk: int,
    ) -> None:
        self._keep_chunks = int(keep_chunks)
        self._max_insights_per_chunk = int(max_insights_per_chunk)
        self._chunks: Deque[MemoryChunk] = deque()

    def add_chunk(
        self,
        *,
        iteration_start: int,
        iteration_end: int,
        insights: Sequence[str],
        sources: Sequence[Source],
    ) -> Optional[MemoryChunk]:
        clean_insights = [x.strip() for x in insights if x and x.strip()]
        clean_insights = clean_insights[: self._max_insights_per_chunk]
        if not clean_insights:
            return None
        chunk_id = _stable_hash(
            f"{iteration_start}:{iteration_end}:{'|'.join(clean_insights[:3])}"
        )
        chunk = MemoryChunk(
            chunk_id=chunk_id,
            created_at=utc_now_iso(),
            iteration_start=int(iteration_start),
            iteration_end=int(iteration_end),
            insights=list(clean_insights),
            sources=[s.to_json() for s in sources][:25],
        )
        self._chunks.append(chunk)
        while len(self._chunks) > self._keep_chunks:
            self._chunks.popleft()
        return chunk

    def combined_insights(self, limit: int = 80) -> List[str]:
        out: List[str] = []
        for c in reversed(self._chunks):
            out.extend(c.insights)
            if len(out) >= limit:
                break
        return out[:limit]

    def summary_text(self, limit: int = 50) -> str:
        bullets = self.combined_insights(limit=limit)
        if not bullets:
            return ""
        return "\n".join(f"- {b}" for b in bullets)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "chunks": [c.__dict__ for c in list(self._chunks)],
        }


class QuestionPlanner:
    def __init__(self, topic: str) -> None:
        self._topic = topic.strip()
        self._themes = [
            "agent architectures",
            "tool use strategies",
            "prompting and guardrails",
            "memory and context management",
            "logging, evaluation, observability",
            "robustness and safety",
            "production deployment patterns",
        ]

    def theme_for_iteration(self, i: int, total: int) -> str:
        if total <= 0:
            return self._themes[0]
        idx = int((max(0, i - 1) / float(total)) * len(self._themes))
        idx = max(0, min(len(self._themes) - 1, idx))
        return self._themes[idx]

    def build_question(self, i: int, total: int, memory: LongTermMemory) -> str:
        theme = self.theme_for_iteration(i, total)
        base = self._topic
        focus = ""
        mem = memory.combined_insights(limit=40)
        if mem:
            counts = Counter()
            for ins in mem:
                for t in _tokenize(ins):
                    if len(t) >= 4:
                        counts[t] += 1
            for w, _c in counts.most_common(20):
                if w in {
                    "agent",
                    "agents",
                    "research",
                    "model",
                    "models",
                    "memory",
                    "tools",
                }:
                    continue
                focus = w
                break
        focus_suffix = f" Focus: {focus}." if focus else ""
        if i % 10 == 0:
            return f"What are failure modes and mitigations for long-horizon research agents in {theme}? ({base}){focus_suffix}"
        if i % 7 == 0:
            return f"What are best practices and concrete patterns for {theme} in autonomous research agents? ({base}){focus_suffix}"
        if i % 5 == 0:
            return f"What evaluation and logging approaches are recommended for {theme} in production agents? ({base}){focus_suffix}"
        return f"What practical implementation patterns exist for {theme} in autonomous research agents? ({base}){focus_suffix}"

    def propose_queries(self, question: str, *, k: int) -> List[str]:
        q = question.strip()
        variants = [
            q,
            q + " implementation",
            q + " best practices",
            q + " pitfalls",
            q + " open-source",
        ]
        out: List[str] = []
        for v in variants:
            if v not in out:
                out.append(v)
            if len(out) >= k:
                break
        return out


class Monitor:
    def __init__(
        self,
        *,
        cooldown_iters: int,
        similarity_threshold: float,
    ) -> None:
        self._cooldown_iters = int(cooldown_iters)
        self._sim_threshold = float(similarity_threshold)

    def should_skip_query(
        self,
        query: str,
        *,
        iteration: int,
        recent_queries: Deque[Tuple[int, str, List[str]]],
    ) -> bool:
        toks = _tokenize(query)
        for it, q_norm, q_toks in reversed(recent_queries):
            if iteration - it > self._cooldown_iters:
                break
            if q_norm == _normalize_text(query):
                return True
            if _jaccard(toks, q_toks) >= self._sim_threshold:
                return True
        return False

    def next_steps_hint(self, *, iteration: int, tool_errors: Dict[str, Any]) -> str:
        if tool_errors.get("errors"):
            return "Diversify tools/queries; reduce reliance on failing tools; increase backoff."
        if iteration % 20 == 0:
            return "Synthesize and compress; update plan for next theme chunk."
        return "Probe gaps; vary query phrasing; focus on actionable patterns and failure modes."


class Architect:
    def propose_design_updates(
        self,
        *,
        iteration: int,
        key_insights: Sequence[str],
        tool_errors: Dict[str, Any],
    ) -> List[str]:
        updates: List[str] = []
        if tool_errors.get("errors"):
            updates.append(
                "Add tool failure budget and per-tool circuit breaker; fall back to alternate providers."
            )
        if iteration % 20 == 0 and key_insights:
            updates.append(
                "Run periodic workspace reconstruction; keep only summaries + recent window for planning."
            )
        text = " ".join(key_insights).lower()
        if "rate limit" in text or "429" in text:
            updates.append(
                "Implement exponential backoff + jitter and token-bucket rate limiter per tool."
            )
        if "evaluation" in text or "langsmith" in text or "trace" in text:
            updates.append(
                "Add trace IDs per iteration and record tool latencies + errors for observability."
            )
        return updates


class InsightExtractor:
    def __init__(self) -> None:
        self._seen: set[str] = set()

    def extract(
        self, question: str, sources: Sequence[Source], limit: int = 6
    ) -> List[str]:
        out: List[str] = []
        q_tokens = set(_tokenize(question))
        for s in sources:
            parts = []
            if s.title:
                parts.append(s.title)
            if s.snippet:
                parts.append(s.snippet)
            text = " - ".join(parts).strip()
            if not text:
                continue
            tokens = set(_tokenize(text))
            overlap = len(q_tokens.intersection(tokens))
            if overlap <= 1 and len(q_tokens) > 6:
                continue
            insight = text
            key = _stable_hash(_normalize_text(insight))
            if key in self._seen:
                continue
            self._seen.add(key)
            out.append(insight)
            if len(out) >= limit:
                break
        return out


@dataclass
class ResearchState:
    topic: str
    total_iterations: int
    memory: LongTermMemory
    recent_queries: Deque[Tuple[int, str, List[str]]]
    recent_insights: Deque[str]
    design_notes: Deque[str]
    last_synthesis_iter: int = 0
    last_synthesis_start: int = 1
    recent_sources: Deque[Source] = field(default_factory=lambda: deque())
    tool_health: Dict[str, Dict[str, Any]] = field(default_factory=dict)


class StateGraph:
    def __init__(self) -> None:
        self._nodes: List[Tuple[str, Any]] = []

    def add_node(self, name: str, fn: Any) -> "StateGraph":
        self._nodes.append((name, fn))
        return self

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        cur = dict(state)
        for _, fn in self._nodes:
            r = fn(cur)
            if asyncio.iscoroutine(r):
                cur = await r
            else:
                cur = r
        return cur


class ResearchAgent:
    def __init__(self, config: ResearchAgentConfig) -> None:
        self.config = config

        tools = []
        enabled = set(config.enabled_tools)
        if "exa" in enabled:
            tools.append(ExaSearchTool())
        if "google" in enabled:
            tools.append(GoogleCSESearchTool())
        if "serpapi" in enabled:
            tools.append(SerpAPISearchTool())

        self._tool_runner = ToolRunner(
            tools,
            max_concurrency=config.max_concurrency,
            per_request_timeout_s=config.per_request_timeout_s,
        )
        self._planner = QuestionPlanner(config.research_topic)
        self._monitor = Monitor(
            cooldown_iters=config.query_cooldown_iters,
            similarity_threshold=config.query_similarity_threshold,
        )
        self._architect = Architect()
        self._extractor = InsightExtractor()

        self._state = ResearchState(
            topic=config.research_topic,
            total_iterations=config.total_iterations,
            memory=LongTermMemory(
                keep_chunks=config.keep_long_term_chunks,
                max_insights_per_chunk=config.max_insights_per_chunk,
            ),
            recent_queries=deque(maxlen=config.max_recent_queries),
            recent_insights=deque(maxlen=config.keep_recent_insights),
            design_notes=deque(maxlen=config.max_design_notes),
            recent_sources=deque(maxlen=250),
        )

    async def run(self) -> str:
        os.makedirs(os.path.dirname(self.config.log_path) or ".", exist_ok=True)

        with JSONLResearchLogger(
            self.config.log_path, flush_every=self.config.flush_every
        ) as logger:
            async with AsyncHTTPClient(
                timeout_s=self.config.per_request_timeout_s
            ) as http:
                total = int(self.config.total_iterations)
                batch = max(1, int(self.config.batch_size))
                i = 1
                while i <= total:
                    end = min(total, i + batch - 1)
                    plans = self._plan_batch(i, end)
                    batch_results = await self._search_batch(http, plans)
                    for plan in plans:
                        r = batch_results.get(plan.iteration) or []
                        await self._run_iteration(plan, r, logger)
                    i = end + 1
        return self.config.log_path

    def run_sync(self) -> str:
        return asyncio.run(self.run())

    def _plan_batch(self, start_iter: int, end_iter: int) -> List[IterationPlan]:
        plans: List[IterationPlan] = []
        for it in range(int(start_iter), int(end_iter) + 1):
            question = self._planner.build_question(
                it, self.config.total_iterations, self._state.memory
            )
            queries = self._planner.propose_queries(
                question, k=self.config.queries_per_iteration
            )
            filtered: List[str] = []
            for q in queries:
                q2 = q.strip()
                if not q2:
                    continue
                if self._monitor.should_skip_query(
                    q2, iteration=it, recent_queries=self._state.recent_queries
                ):
                    continue
                filtered.append(q2)
            if not filtered:
                filtered = [question]
            plans.append(
                IterationPlan(
                    iteration=it, research_question=question, queries=filtered
                )
            )
        return plans

    async def _search_batch(
        self,
        http: AsyncHTTPClient,
        plans: Sequence[IterationPlan],
    ) -> Dict[int, List[ToolSearchResult]]:
        configured = [
            t
            for t in self._tool_runner.configured_tools()
            if not self._tool_disabled(t.name, plans[0].iteration if plans else 1)
        ]
        out: Dict[int, List[ToolSearchResult]] = {p.iteration: [] for p in plans}
        if not configured:
            return out

        tasks: List[asyncio.Task[Tuple[int, ToolSearchResult]]] = []
        for p in plans:
            for q in p.queries:
                for tool in configured:

                    async def _one(it: int, t, qq: str) -> Tuple[int, ToolSearchResult]:
                        r = await self._tool_runner.run_one(
                            http, t, qq, num_results=self.config.results_per_query
                        )
                        return it, r

                    tasks.append(asyncio.create_task(_one(p.iteration, tool, q)))
        if not tasks:
            return out

        for it, res in await asyncio.gather(*tasks):
            out.setdefault(it, []).append(res)
        return out

    def _tool_disabled(self, tool_name: str, iteration: int) -> bool:
        h = self._state.tool_health.get(tool_name)
        if not h:
            return False
        disabled_until = int(h.get("disabled_until", 0))
        return iteration <= disabled_until

    def _record_tool_result(self, r: ToolSearchResult, iteration: int) -> None:
        h = self._state.tool_health.setdefault(
            r.tool_name,
            {
                "consecutive_failures": 0,
                "disabled_until": 0,
                "total_failures": 0,
                "total_successes": 0,
            },
        )
        if r.error:
            h["consecutive_failures"] = int(h.get("consecutive_failures", 0)) + 1
            h["total_failures"] = int(h.get("total_failures", 0)) + 1
            if int(h["consecutive_failures"]) >= int(
                self.config.tool_circuit_breaker_failures
            ):
                h["disabled_until"] = int(iteration) + int(
                    self.config.tool_circuit_breaker_disable_iters
                )
        else:
            h["total_successes"] = int(h.get("total_successes", 0)) + 1
            h["consecutive_failures"] = 0

    async def _run_iteration(
        self,
        plan: IterationPlan,
        tool_results: Sequence[ToolSearchResult],
        logger: JSONLResearchLogger,
    ) -> None:
        it = int(plan.iteration)

        used_tools: List[str] = []
        for r in tool_results:
            self._record_tool_result(r, it)
            if r.tool_name not in used_tools:
                used_tools.append(r.tool_name)

        sources, tool_meta = merge_tool_results(
            tool_results, top_k=self.config.top_sources_per_iteration
        )
        insights = self._extractor.extract(plan.research_question, sources, limit=6)
        design_updates = self._architect.propose_design_updates(
            iteration=it,
            key_insights=insights,
            tool_errors=tool_meta,
        )

        for q in plan.queries:
            self._state.recent_queries.append((it, _normalize_text(q), _tokenize(q)))
        for ins in insights:
            self._state.recent_insights.append(ins)
        for upd in design_updates:
            upd2 = upd.strip()
            if not upd2:
                continue
            if upd2 in self._state.design_notes:
                continue
            self._state.design_notes.append(upd2)
        for s in sources:
            self._state.recent_sources.append(s)

        if self._should_synthesize(it):
            self._synthesize(it)

        next_steps_hint = self._monitor.next_steps_hint(
            iteration=it, tool_errors=tool_meta
        )

        graph = StateGraph()
        graph.add_node(
            "log",
            lambda st: self._emit_log(
                logger=logger,
                iteration=st["iteration"],
                research_question=st["research_question"],
                used_tools=st["used_tools"],
                queries=st["queries"],
                sources=st["sources"],
                insights=st["insights"],
                design_updates=st["design_updates"],
                next_steps_hint=st["next_steps_hint"],
            ),
        )
        await graph.run(
            {
                "iteration": it,
                "research_question": plan.research_question,
                "used_tools": used_tools,
                "queries": plan.queries,
                "sources": sources,
                "insights": insights,
                "design_updates": design_updates,
                "next_steps_hint": next_steps_hint,
            }
        )

    def _emit_log(
        self,
        *,
        logger: JSONLResearchLogger,
        iteration: int,
        research_question: str,
        used_tools: Sequence[str],
        queries: Sequence[str],
        sources: Sequence[Source],
        insights: Sequence[str],
        design_updates: Sequence[str],
        next_steps_hint: str,
    ) -> Dict[str, Any]:
        top_sources_json = [s.to_json() for s in sources]
        entry = ResearchLogEntry.from_parts(
            iteration=int(iteration),
            research_question=str(research_question),
            search_tools_used=list(used_tools),
            queries=list(queries),
            top_sources=list(sources),
            key_insights=list(insights),
            design_updates=list(design_updates),
            next_steps_hint=str(next_steps_hint),
            timestamp=utc_now_iso(),
        )
        payload = entry.to_json()
        payload["top_sources"] = top_sources_json
        logger.log(payload)
        return payload

    def _should_synthesize(self, iteration: int) -> bool:
        every = max(1, int(self.config.synthesis_every))
        if iteration == 1:
            return False
        if iteration - self._state.last_synthesis_iter >= every:
            return True
        if iteration == self.config.total_iterations:
            return True
        return False

    def _synthesize(self, iteration: int) -> None:
        start = int(self._state.last_synthesis_start)
        end = int(iteration)
        recent = list(self._state.recent_insights)
        if not recent:
            self._state.last_synthesis_iter = end
            self._state.last_synthesis_start = end + 1
            return

        counts = Counter()
        for ins in recent:
            for t in _tokenize(ins):
                counts[t] += 1

        keywords = [w for w, c in counts.most_common(12) if c >= 3]
        ranked: List[Tuple[int, str]] = []
        for ins in recent:
            toks = set(_tokenize(ins))
            score = sum(1 for k in keywords if k in toks)
            ranked.append((score, ins))
        ranked.sort(key=lambda x: (x[0], len(x[1])), reverse=True)
        keep: List[str] = []
        for _, ins in ranked:
            n = _normalize_text(ins)
            if any(
                _jaccard(_tokenize(n), _tokenize(_normalize_text(k))) > 0.92
                for k in keep
            ):
                continue
            keep.append(ins)
            if len(keep) >= self.config.max_insights_per_chunk:
                break

        srcs = list(self._state.recent_sources)
        self._state.memory.add_chunk(
            iteration_start=start,
            iteration_end=end,
            insights=keep,
            sources=srcs[-25:],
        )

        self._state.recent_insights.clear()
        self._state.recent_sources.clear()
        self._state.last_synthesis_iter = end
        self._state.last_synthesis_start = end + 1
