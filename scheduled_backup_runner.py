#!/usr/bin/env python3
"""Detached runner for a scheduled backup task.

Why this exists
---------------
Scheduled backups used to run inside a *daemon* thread of the uvicorn worker
(``_start_scheduled_task_thread``). Any uvicorn reload/restart — which happens
routinely on this appliance (VM boot, code reload, OOM, post-restore) — kills
that thread instantly, leaving a half-written backup folder with no
``backup_metadata.json``. The result: the backup silently dies mid-run, the UI
list hides the folder (no metadata), and the schedule wrongly reports "OK".

Running the backup as a transient ``systemd-run`` unit (exactly like the restore
pipeline) decouples it from uvicorn's lifecycle: the backup finishes even if the
web worker is reloaded or killed underneath it.

Usage
-----
    scheduled_backup_runner.py <task_id>

It simply re-uses ``_execute_scheduled_task`` from the backup views, so all the
existing behaviour (notifications, event log, GFS retention, cloud upload,
schedule_config update) is preserved verbatim — this file only changes *where*
that function runs, not *what* it does.
"""
import os
import sys
import threading
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path("/asguard/asguard")

# Upper bound for waiting on background worker threads (cloud upload, e-mail,
# ntfy) that _execute_scheduled_task spawns. In uvicorn these outlive the request
# on the long-lived process; here the process is short-lived, so we must NOT exit
# until they finish or the cloud upload dies with "cannot schedule new futures
# after interpreter shutdown". A full backup tarball (~40 MB) upload is the worst
# case; 10 min is comfortably safe.
_BACKGROUND_THREAD_WAIT_SECONDS = 600


def _log(msg: str):
    print(f"[{datetime.now(tz=timezone.utc).isoformat()}] {msg}", flush=True)


def _wait_for_background_threads(timeout: float):
    """Block until every worker thread the backup spawned has finished.

    _execute_scheduled_task fires the cloud upload in a *daemon* thread and the
    notifications in non-daemon threads. On a short-lived detached process the
    interpreter would tear down immediately after the task returns, aborting the
    in-flight cloud upload. Joining the daemon threads here (a daemon thread can
    still be joined — the flag only governs auto-exit) keeps us alive until the
    upload + notifications are genuinely done."""
    deadline = time.monotonic() + timeout
    main = threading.main_thread()
    while True:
        pending = [t for t in threading.enumerate() if t is not main and t.is_alive()]
        if not pending:
            return
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            _log(f"WARN: {len(pending)} background thread(s) still running after "
                 f"{timeout}s — exiting anyway: {[t.name for t in pending]}")
            return
        pending[0].join(min(remaining, 5))


def main() -> int:
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        _log("ERROR: missing task_id argument")
        return 2
    task_id = sys.argv[1].strip()

    os.chdir(PROJECT_ROOT)
    sys.path.insert(0, str(PROJECT_ROOT))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "asguard.settings")

    try:
        import django
        django.setup()
    except Exception:
        _log("ERROR: django.setup() failed")
        traceback.print_exc()
        return 3

    try:
        from backend.backup.views import _execute_scheduled_task
    except Exception:
        _log("ERROR: could not import _execute_scheduled_task")
        traceback.print_exc()
        return 4

    _log(f"Scheduled backup runner starting for task {task_id}")
    rc = 0
    try:
        _execute_scheduled_task(task_id)
        _log(f"Scheduled backup runner finished for task {task_id}")
    except Exception:
        # _execute_scheduled_task already records its own error into
        # schedule_config + the event log; this is just a last-resort trace.
        _log(f"ERROR: scheduled backup runner crashed for task {task_id}")
        traceback.print_exc()
        rc = 1

    # Let the cloud upload + notification threads finish before the interpreter
    # tears down (otherwise the upload aborts mid-flight on this short process).
    _wait_for_background_threads(_BACKGROUND_THREAD_WAIT_SECONDS)
    _log(f"Scheduled backup runner exiting (rc={rc}) for task {task_id}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
