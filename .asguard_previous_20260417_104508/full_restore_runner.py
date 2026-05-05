#!/usr/bin/env python3
import json
import os
import sys
import time
import traceback
import subprocess
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


def run_cmd(cmd, timeout=30):
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        check=False,
    )


def wait_for_system_stabilization(max_attempts=15, delay_seconds=2):
    last_info = {}

    for _ in range(max_attempts):
        try:
            jobs = run_cmd(["systemctl", "list-jobs"], timeout=15)
            jobs_output = (jobs.stdout or "").strip()

            uvicorn = run_cmd(["systemctl", "is-active", "uvicorn"], timeout=15)
            nginx = run_cmd(["systemctl", "is-active", "nginx"], timeout=15)
            swagger = run_cmd(["curl", "-fsS", "http://127.0.0.1:8000/swagger/"], timeout=15)

            no_jobs = "No jobs running." in jobs_output
            uvicorn_ok = (uvicorn.stdout or "").strip() == "active"
            nginx_ok = (nginx.stdout or "").strip() == "active"
            swagger_ok = swagger.returncode == 0

            last_info = {
                "jobs": jobs_output,
                "uvicorn": (uvicorn.stdout or uvicorn.stderr or "").strip(),
                "nginx": (nginx.stdout or nginx.stderr or "").strip(),
                "swagger_rc": swagger.returncode,
            }

            if no_jobs and uvicorn_ok and nginx_ok and swagger_ok:
                return True, last_info

        except Exception as exc:
            last_info = {"exception": str(exc)}

        time.sleep(delay_seconds)

    return False, last_info


def main():
    if len(sys.argv) not in (3, 4):
        print("Usage: full_restore_runner.py <backup_id> <job_id> [safe|complete]")
        return 2

    backup_id = sys.argv[1]
    job_id = sys.argv[2]
    mode = sys.argv[3] if len(sys.argv) == 4 else "safe"

    if mode not in ("safe", "complete"):
        print("Mode must be 'safe' or 'complete'")
        return 2

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
            "mode": mode,
            "status": "running",
            "started_at": started_at,
            "finished_at": None,
            "log_file": str(log_file),
            "result": None,
        })

        print(f"[{utc_now()}] FULL RESTORE STARTED: backup_id={backup_id}, job_id={job_id}, mode={mode}")

        if mode == "complete":
            result = RestoreService.restore_full_complete(backup_id)
        else:
            result = RestoreService.restore_full_safe(backup_id)

        print(f"[{utc_now()}] RESTORE CORE FINISHED: raw_status={result.get('status', 'error')}, mode={mode}")
        print(f"[{utc_now()}] STARTING POST-RESTORE STABILIZATION...")

        stabilize_ok, stabilize_info = wait_for_system_stabilization(max_attempts=15, delay_seconds=2)

        if isinstance(result, dict):
            result["stabilization"] = {
                "status": "success" if stabilize_ok else "partial",
                "details": stabilize_info,
            }

        final_status = result.get("status", "error")
        if final_status == "success" and not stabilize_ok:
            final_status = "partial_success"

        final_status_label = (
            "success" if final_status == "success"
            else ("error" if final_status == "error" else "partial_success")
        )

        write_json(state_file, {
            "job_id": job_id,
            "backup_id": backup_id,
            "mode": mode,
            "status": final_status_label,
            "started_at": started_at,
            "finished_at": utc_now(),
            "log_file": str(log_file),
            "result": result,
        })

        print(f"[{utc_now()}] FULL RESTORE FINISHED: status={final_status}, mode={mode}")
        print(json.dumps(result, indent=2))

        return 0 if final_status == "success" else 1

    except Exception as exc:
        tb = traceback.format_exc()

        try:
            write_json(state_file, {
                "job_id": job_id,
                "backup_id": backup_id,
                "mode": mode,
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