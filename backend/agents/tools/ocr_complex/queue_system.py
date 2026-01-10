"""
BATCH PROCESSING QUEUE
Lightweight in-memory queue with worker threads.
Explicit success/failure.
"""

import queue
import threading
from typing import Any, Callable, Dict


class TaskResult:
    def __init__(self, task_id: str, success: bool, data=None, error: str = None):
        self.task_id = task_id
        self.success = success
        self.data = data
        self.error = error


class BatchQueue:
    def __init__(
        self,
        worker_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
        num_workers: int = 2,
    ):
        self.worker_fn = worker_fn
        self.num_workers = num_workers
        self.q = queue.Queue()
        self.results = {}
        self.lock = threading.Lock()
        self.threads = []
        self._start_workers()

    def _start_workers(self):
        for _ in range(self.num_workers):
            t = threading.Thread(target=self._worker, daemon=True)
            t.start()
            self.threads.append(t)

    def _worker(self):
        while True:
            task_id, payload = self.q.get()
            try:
                res = self.worker_fn(payload)
                with self.lock:
                    self.results[task_id] = TaskResult(task_id, True, res)
            except Exception as e:
                with self.lock:
                    self.results[task_id] = TaskResult(task_id, False, error=str(e))
            finally:
                self.q.task_done()

    def submit(self, task_id: str, payload: Dict[str, Any]):
        self.q.put((task_id, payload))

    def get_result(self, task_id: str):
        with self.lock:
            return self.results.get(task_id)

    def pending(self):
        return self.q.qsize()
