#!/usr/bin/env python3
"""Run the LVM coverage migration as root.

LVMMigrationService copies config trees onto the LV, recreates their mountpoints
and bind-mounts them back. Every one of those steps needs root: reading 0600
files (/etc/NetworkManager/system-connections, /etc/ssl/private, /var/spool/cron),
creating mountpoints under root-owned directories, and — critically — owning the
recreated mountpoints. Run under `uvicorn`, the copies come out truncated and a
mountpoint like /etc/sudoers.d ends up owned by uid 1002, which makes sudo refuse
to run at all.

So the web view never migrates in-process: it launches this runner as root and
polls the job file the service writes.

Usage: lvm_migration_runner.py <job_id> [id1,id2,...]
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path("/asguard/asguard")


def main():
    if len(sys.argv) not in (2, 3):
        print("usage: lvm_migration_runner.py <job_id> [ids,comma,separated]", file=sys.stderr)
        return 2

    job_id = sys.argv[1]
    ids = [i for i in sys.argv[2].split(",") if i] if len(sys.argv) == 3 else None

    if os.geteuid() != 0:
        print("must run as root", file=sys.stderr)
        return 1

    sys.path.insert(0, str(PROJECT_ROOT))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "asguard.settings")
    import django
    django.setup()

    from backend.backup.system_backup.lvm_migration_service import (
        LVMMigrationService, JOBS_DIR, _write_job,
    )

    try:
        LVMMigrationService.apply(dry_run=False, ids=ids, job_id=job_id)
    except Exception as exc:
        import traceback
        traceback.print_exc()
        _write_job(JOBS_DIR / f"{job_id}.json", {
            "job_id": job_id, "status": "error", "error": str(exc),
        })
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
