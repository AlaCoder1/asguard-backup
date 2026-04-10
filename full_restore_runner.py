#!/usr/bin/env python3
import json
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path("/asguard/asguard")
JOBS_ROOT = Path("/var/backups/asguard/restore_jobs")


def utc_now():
    return datetime.now(tz=timezone.utc).isoformat()


def write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, path)
    os.chmod(path, 0o644)


def main():
    if len(sys.argv) != 3:
        print("Usage: full_restore_runner.py <backup_id> <job_id>")
        return 2

    backup_id = sys.argv[1]
    job_id = sys.argv[2]

    state_file = JOBS_ROOT / f"{job_id}.json"
    log_file = JOBS_ROOT / "logs" / f"{job_id}.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    started_at = utc_now()

    try:
        os.chdir(PROJECT_ROOT)
        sys.path.insert(0, str(PROJECT_ROOT))
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "asguard.settings")

        import django
        django.setup()

        from backend.backup.system_backup.restore_service import RestoreService

        write_json(state_file, {
            "job_id": job_id,
            "backup_id": backup_id,
            "status": "running",
            "started_at": started_at,
            "finished_at": None,
            "log_file": str(log_file),
            "result": None,
        })

        print(f"[{utc_now()}] FULL RESTORE STARTED: backup_id={backup_id}, job_id={job_id}")

        result = RestoreService.restore_full(backup_id)
        final_status = result.get("status", "error")

        # FIXED: Update status to "completed" instead of leaving it as "running"
        final_status_label = "success" if final_status == "success" else ("error" if final_status == "error" else "partial_success")

        write_json(state_file, {
            "job_id": job_id,
            "backup_id": backup_id,
            "status": final_status_label,  # NOW: success, error, or partial_success (not "running")
            "started_at": started_at,
            "finished_at": utc_now(),
            "log_file": str(log_file),
            "result": result,
        })

        print(f"[{utc_now()}] FULL RESTORE FINISHED: status={final_status}")
        print(json.dumps(result, indent=2))

        return 0 if final_status == "success" else 1

    except Exception as exc:
        tb = traceback.format_exc()

        try:
            write_json(state_file, {
                "job_id": job_id,
                "backup_id": backup_id,
                "status": "error",
                "started_at": started_at,
                "finished_at": utc_now(),
                "log_file": str(log_file),
                "result": {
                    "message": str(exc),
                    "traceback": tb,
                },
            })
        except Exception:
            pass

        print(f"[{utc_now()}] FULL RESTORE CRASHED: {exc}")
        print(tb)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())