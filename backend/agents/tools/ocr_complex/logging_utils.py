"""
PROGRESS TRACKING AND LOGGING
Thread-safe structured logs to file or stdout.
"""

import json
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional


class ProgressLogger:
    def __init__(self, log_path: Optional[str] = None):
        self.log_path = Path(log_path) if log_path else None
        self.lock = threading.Lock()

    def log(self, event: str, payload: Dict[str, Any]):
        record = {
            "ts": time.time(),
            "event": event,
            "payload": payload,
        }
        line = json.dumps(record, ensure_ascii=False)
        with self.lock:
            if self.log_path:
                self.log_path.parent.mkdir(parents=True, exist_ok=True)
                with self.log_path.open("a", encoding="utf-8") as f:
                    f.write(line + "\n")
            else:
                sys.stdout.write(line + "\n")
