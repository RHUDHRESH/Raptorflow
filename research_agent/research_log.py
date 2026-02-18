from __future__ import annotations

import json
import queue
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Source:
    url: str
    title: str = ""
    snippet: str = ""
    score: Optional[float] = None
    published: Optional[str] = None
    tool: Optional[str] = None

    def to_json(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "url": self.url,
        }
        if self.title:
            out["title"] = self.title
        if self.snippet:
            out["snippet"] = self.snippet
        if self.score is not None:
            out["score"] = self.score
        if self.published is not None:
            out["published"] = self.published
        if self.tool is not None:
            out["tool"] = self.tool
        return out


@dataclass
class ResearchLogEntry:
    iteration: int
    timestamp: str
    research_question: str
    search_tools_used: List[str] = field(default_factory=list)
    queries: List[str] = field(default_factory=list)
    top_sources: List[Dict[str, Any]] = field(default_factory=list)
    key_insights: List[str] = field(default_factory=list)
    design_updates: List[str] = field(default_factory=list)
    next_steps_hint: str = ""

    def to_json(self) -> Dict[str, Any]:
        return {
            "iteration": int(self.iteration),
            "timestamp": str(self.timestamp),
            "research_question": str(self.research_question),
            "search_tools_used": list(self.search_tools_used),
            "queries": list(self.queries),
            "top_sources": list(self.top_sources),
            "key_insights": list(self.key_insights),
            "design_updates": list(self.design_updates),
            "next_steps_hint": str(self.next_steps_hint),
        }

    @staticmethod
    def from_parts(
        *,
        iteration: int,
        research_question: str,
        search_tools_used: Iterable[str],
        queries: Iterable[str],
        top_sources: Iterable[Source | Dict[str, Any]],
        key_insights: Iterable[str],
        design_updates: Iterable[str],
        next_steps_hint: str,
        timestamp: Optional[str] = None,
    ) -> "ResearchLogEntry":
        ts = utc_now_iso() if timestamp is None else timestamp

        sources_out: List[Dict[str, Any]] = []
        for s in top_sources:
            if isinstance(s, Source):
                sources_out.append(s.to_json())
            elif isinstance(s, dict):
                sources_out.append(dict(s))
            else:
                sources_out.append({"value": repr(s)})

        return ResearchLogEntry(
            iteration=int(iteration),
            timestamp=str(ts),
            research_question=str(research_question),
            search_tools_used=list(search_tools_used),
            queries=list(queries),
            top_sources=sources_out,
            key_insights=[str(x) for x in key_insights],
            design_updates=[str(x) for x in design_updates],
            next_steps_hint=str(next_steps_hint),
        )


class JSONLResearchLogger:
    def __init__(
        self,
        file_path: str,
        *,
        flush_every: int = 5,
        max_queue_size: int = 10_000,
    ) -> None:
        self._file_path = file_path
        self._flush_every = max(1, int(flush_every))
        self._q: "queue.Queue[Optional[Dict[str, Any]]]" = queue.Queue(
            maxsize=max_queue_size
        )
        self._stop = threading.Event()
        self._thread = threading.Thread(
            target=self._run, name="research-jsonl-logger", daemon=True
        )
        self._thread.start()

    @property
    def file_path(self) -> str:
        return self._file_path

    def log(self, entry: ResearchLogEntry | Dict[str, Any]) -> None:
        if isinstance(entry, ResearchLogEntry):
            payload = entry.to_json()
        else:
            payload = dict(entry)
        try:
            self._q.put_nowait(payload)
        except queue.Full:
            return

    def close(self, timeout_s: float = 5.0) -> None:
        if self._stop.is_set():
            return
        self._stop.set()
        try:
            self._q.put_nowait(None)
        except queue.Full:
            pass
        self._thread.join(timeout=timeout_s)

    def __enter__(self) -> "JSONLResearchLogger":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _run(self) -> None:
        buffer: List[Dict[str, Any]] = []
        with open(self._file_path, "a", encoding="utf-8") as f:
            while True:
                try:
                    item = self._q.get(timeout=0.25)
                except queue.Empty:
                    item = None

                if item is None:
                    if self._stop.is_set():
                        break
                    if buffer:
                        for obj in buffer:
                            f.write(json.dumps(obj, ensure_ascii=True) + "\n")
                        f.flush()
                        buffer.clear()
                    continue

                buffer.append(item)
                if len(buffer) >= self._flush_every:
                    for obj in buffer:
                        f.write(json.dumps(obj, ensure_ascii=True) + "\n")
                    f.flush()
                    buffer.clear()

            while True:
                try:
                    item2 = self._q.get_nowait()
                except queue.Empty:
                    break
                if item2 is None:
                    continue
                buffer.append(item2)
            if buffer:
                for obj in buffer:
                    f.write(json.dumps(obj, ensure_ascii=True) + "\n")
                f.flush()
