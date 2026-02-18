from __future__ import annotations

from backend.api.v1.ai_hub.job_store import InMemoryJobStore


def test_job_store_lifecycle() -> None:
    store = InMemoryJobStore(max_entries=10, ttl_seconds=3600)

    created = store.create(job_id="job-1", request={"intent": "test"})
    assert created["status"] == "queued"
    assert created["job_id"] == "job-1"

    running = store.mark_running(job_id="job-1")
    assert running is not None
    assert running["status"] == "running"

    completed = store.complete(
        job_id="job-1",
        status="succeeded",
        result={"trace_id": "trace-1", "status": "success"},
        run_id="trace-1",
    )
    assert completed is not None
    assert completed["status"] == "succeeded"
    assert completed["run_id"] == "trace-1"

    stored = store.get("job-1")
    assert stored is not None
    assert stored["status"] == "succeeded"
    assert stored["result"]["trace_id"] == "trace-1"


def test_job_store_prunes_when_over_capacity() -> None:
    store = InMemoryJobStore(max_entries=50, ttl_seconds=3600)

    for index in range(55):
        job_id = f"job-{index}"
        store.create(job_id=job_id, request={"idx": index})
        store.complete(
            job_id=job_id,
            status="succeeded",
            result={"idx": index},
            run_id=f"trace-{index}",
        )

    assert store.get("job-0") is None
    assert store.get("job-54") is not None

