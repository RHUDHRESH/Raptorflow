"""
Bounded in-memory job tracking for async AI Hub runs.
"""

from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from typing import Any, Dict, Optional


class InMemoryJobStore:
    def __init__(self, *, max_entries: int = 500, ttl_seconds: int = 3600) -> None:
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
        self._max_entries = max(50, int(max_entries))
        self._ttl_seconds = max(60, int(ttl_seconds))

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    @classmethod
    def _now_iso(cls) -> str:
        return cls._now().isoformat()

    @staticmethod
    def _to_dt(value: str | None) -> Optional[datetime]:
        if not value:
            return None
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            return None

    def _prune_locked(self) -> None:
        now = self._now()

        expired_ids = []
        for job_id, job in self._jobs.items():
            status = str(job.get("status") or "")
            if status not in {"succeeded", "failed"}:
                continue
            completed_at = self._to_dt(
                str(job.get("completed_at") or job.get("updated_at") or "")
            )
            if completed_at is None:
                continue
            age_seconds = int((now - completed_at).total_seconds())
            if age_seconds >= self._ttl_seconds:
                expired_ids.append(job_id)

        for job_id in expired_ids:
            self._jobs.pop(job_id, None)

        if len(self._jobs) <= self._max_entries:
            return

        ordered = sorted(
            self._jobs.items(), key=lambda item: str(item[1].get("accepted_at") or "")
        )

        for job_id, job in ordered:
            if len(self._jobs) <= self._max_entries:
                break
            if str(job.get("status") or "") in {"succeeded", "failed"}:
                self._jobs.pop(job_id, None)

        if len(self._jobs) <= self._max_entries:
            return

        ordered = sorted(
            self._jobs.items(), key=lambda item: str(item[1].get("accepted_at") or "")
        )
        to_delete = len(self._jobs) - self._max_entries
        for job_id, _ in ordered[:to_delete]:
            self._jobs.pop(job_id, None)

    def create(self, *, job_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        now = self._now_iso()
        row = {
            "job_id": job_id,
            "status": "queued",
            "accepted_at": now,
            "updated_at": now,
            "request": request,
        }
        with self._lock:
            self._jobs[job_id] = row
            self._prune_locked()
            return dict(row)

    def mark_running(self, *, job_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            job["status"] = "running"
            job["started_at"] = self._now_iso()
            job["updated_at"] = job["started_at"]
            return dict(job)

    def complete(
        self,
        *,
        job_id: str,
        status: str,
        result: Dict[str, Any],
        run_id: str,
    ) -> Optional[Dict[str, Any]]:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            completed_at = self._now_iso()
            job["status"] = status
            job["result"] = result
            job["run_id"] = run_id
            job["completed_at"] = completed_at
            job["updated_at"] = completed_at
            self._prune_locked()
            return dict(job)

    def fail(self, *, job_id: str, error: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            completed_at = self._now_iso()
            job["status"] = "failed"
            job["error"] = error
            job["completed_at"] = completed_at
            job["updated_at"] = completed_at
            self._prune_locked()
            return dict(job)

    def get(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            self._prune_locked()
            job = self._jobs.get(job_id)
            return dict(job) if job else None

    def reset(self) -> None:
        with self._lock:
            self._jobs = {}

