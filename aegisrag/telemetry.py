from __future__ import annotations

import json
import threading
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class AuditLogger:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = threading.Lock()

    @staticmethod
    def _safe(value: Any) -> Any:
        if is_dataclass(value):
            return asdict(value)
        if isinstance(value, Path):
            return str(value)
        return value

    def write(self, event: str, trace_id: str, payload: dict[str, Any]) -> None:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "trace_id": trace_id,
            **{key: self._safe(value) for key, value in payload.items()},
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

