"""
Lightweight observability helpers for Backup & DRP.

The backup engine intentionally keeps most runtime state on disk so it can
continue to report progress even when PostgreSQL is unavailable. This module
follows the same model: append-only NDJSON events plus small read helpers for
dashboards and external monitoring.
"""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path

BACKUP_ROOT = Path("/var/backups/asguard")
EVENTS_FILE = BACKUP_ROOT / "events.ndjson"
MAX_EVENT_LINES = 5000

_EVENT_LOCK = threading.RLock()


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def append_backup_event(
    *,
    kind: str,
    title: str,
    severity: str = "info",
    status: str = "info",
    source: str = "backup",
    ref_id: str = "",
    detail: str = "",
    extra: dict | None = None,
) -> dict:
    event = {
        "ts": _utc_now(),
        "kind": kind,
        "source": source,
        "title": title,
        "severity": severity,
        "status": status,
        "ref_id": ref_id,
        "detail": detail,
        "extra": extra or {},
    }

    try:
        BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
        with _EVENT_LOCK:
            with open(EVENTS_FILE, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
            _trim_events_locked()
    except Exception:
        pass
    return event


def _trim_events_locked() -> None:
    try:
        lines = EVENTS_FILE.read_text(encoding="utf-8").splitlines()
        if len(lines) <= MAX_EVENT_LINES:
            return
        tmp = EVENTS_FILE.with_suffix(".tmp")
        tmp.write_text("\n".join(lines[-MAX_EVENT_LINES:]) + "\n", encoding="utf-8")
        tmp.replace(EVENTS_FILE)
    except Exception:
        pass

