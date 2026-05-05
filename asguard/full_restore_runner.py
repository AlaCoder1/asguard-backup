#!/usr/bin/env python3
import json
import os
import sys
import time
import traceback
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT   = Path("/asguard/asguard")
JOBS_ROOT      = Path("/var/backups/asguard/restore_jobs")
RESTORE_LOCK   = Path("/var/backups/asguard/restore_jobs/.in_restore")

# Components that warrant a "heads-up" push notification when they start
_PHASE_NOTIFS = {
    "network":     ("🌐 Restauration réseau en cours", "La connexion peut être interrompue ~30s — c'est normal.", "warning"),
    "database":    ("🗄️  Restauration base de données", "La base PostgreSQL est en cours de restauration.", "default"),
    "application": ("⚙️  Redémarrage application (uvicorn)", "L'interface sera brièvement indisponible.", "high"),
}


def utc_now():
    return datetime.now(tz=timezone.utc).isoformat()


def write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, path)
    os.chmod(path, 0o644)


# ── ntfy direct (stdlib only, no Django/requests needed) ─────────────────────

def _read_ntfy_config():
    try:
        cfg = json.loads(Path("/etc/asguard/watchdog_config.json").read_text())
        nt = cfg.get("notifications", {}).get("ntfy", {})
        return nt if nt.get("enabled") and nt.get("topic") else None
    except Exception:
        return None


def send_ntfy_direct(title: str, body: str, priority: str = "default", tags: str = "shield"):
    """Send ntfy push notification using only stdlib (no requests/Django needed)."""
    nt = _read_ntfy_config()
    if not nt:
        return
    topic = nt["topic"].strip()
    try:
        import urllib.request as _ur
        req = _ur.Request(
            f"https://ntfy.sh/{topic}",
            data=body.encode("utf-8"),
            method="POST",
        )
        req.add_header("Title", title.encode("ascii", "replace").decode())
        req.add_header("Priority", priority)
        req.add_header("Tags", tags)
        with _ur.urlopen(req, timeout=10):
            pass
    except Exception as exc:
        print(f"[ntfy_direct] {exc}")


# ── restore mode lock (tells watchdog: don't interfere) ──────────────────────

def set_restore_mode(job_id: str):
    RESTORE_LOCK.parent.mkdir(parents=True, exist_ok=True)
    RESTORE_LOCK.write_text(json.dumps({
        "job_id": job_id,
        "started_at": utc_now(),
    }))


def clear_restore_mode():
    try:
        RESTORE_LOCK.unlink(missing_ok=True)
    except Exception:
        pass


# ── progress callback + phase notifications ───────────────────────────────────

def make_progress_callback(state_file: Path):
    last_phase_notified: dict = {}

    def _callback(progress: dict):
        nonlocal last_phase_notified
        # Merge progress into state file
        try:
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    current = json.load(f)
            except Exception:
                current = {}
            current.update(progress)
            tmp = state_file.with_suffix(state_file.suffix + ".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(current, f, indent=2)
            os.replace(tmp, state_file)
        except Exception as exc:
            print(f"[progress_callback] write failed: {exc}")

        # Send per-phase ntfy notifications
        current_comp = progress.get("current_component")
        comp_progress = progress.get("components_progress", {})
        if current_comp and current_comp in _PHASE_NOTIFS:
            comp_status = comp_progress.get(current_comp)
            if comp_status == "running" and last_phase_notified.get(current_comp) != "running":
                last_phase_notified[current_comp] = "running"
                title, body, priority = _PHASE_NOTIFS[current_comp]
                send_ntfy_direct(title, body, priority, "arrows_counterclockwise,shield")

    return _callback


def run_cmd(cmd, timeout=30):
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        check=False,
    )


# ── post-restore recovery ─────────────────────────────────────────────────────

def force_uvicorn_recovery():
    """Reset systemd StartLimit and ensure uvicorn is running after restore."""
    print(f"[{utc_now()}] POST-RESTORE: resetting uvicorn StartLimit and ensuring service is up...")

    # Reset the failed counter so systemd will restart it again even after 5 crashes
    run_cmd(["systemctl", "reset-failed", "uvicorn"], timeout=15)
    run_cmd(["systemctl", "daemon-reload"], timeout=30)

    active = run_cmd(["systemctl", "is-active", "uvicorn"], timeout=15)
    if (active.stdout or "").strip() != "active":
        print(f"[{utc_now()}] uvicorn not active — forcing restart...")
        run_cmd(["systemctl", "restart", "uvicorn"], timeout=60)
        time.sleep(5)
        active2 = run_cmd(["systemctl", "is-active", "uvicorn"], timeout=15)
        is_up = (active2.stdout or "").strip() == "active"
        print(f"[{utc_now()}] uvicorn after forced restart: {'active' if is_up else 'STILL DOWN'}")
        return is_up
    return True


def wait_for_system_stabilization(max_attempts=30, delay_seconds=4):
    last_info = {}

    for attempt in range(1, max_attempts + 1):
        try:
            jobs   = run_cmd(["systemctl", "list-jobs"], timeout=15)
            uvicorn = run_cmd(["systemctl", "is-active", "uvicorn"], timeout=15)
            nginx   = run_cmd(["systemctl", "is-active", "nginx"], timeout=15)
            swagger = run_cmd(["curl", "-fsS", "--max-time", "8", "http://127.0.0.1:8000/swagger/"], timeout=15)

            no_jobs    = "No jobs running." in (jobs.stdout or "")
            uvicorn_ok = (uvicorn.stdout or "").strip() == "active"
            nginx_ok   = (nginx.stdout or "").strip() == "active"
            swagger_ok = swagger.returncode == 0

            last_info = {
                "attempt": attempt,
                "jobs": (jobs.stdout or "").strip(),
                "uvicorn": (uvicorn.stdout or uvicorn.stderr or "").strip(),
                "nginx": (nginx.stdout or nginx.stderr or "").strip(),
                "swagger_rc": swagger.returncode,
            }

            print(f"[{utc_now()}] Stabilization check {attempt}/{max_attempts}: "
                  f"uvicorn={'ok' if uvicorn_ok else 'DOWN'} "
                  f"nginx={'ok' if nginx_ok else 'DOWN'} "
                  f"swagger={'ok' if swagger_ok else 'FAIL'}")

            # If uvicorn is down, try to recover immediately
            if not uvicorn_ok and attempt > 5:
                run_cmd(["systemctl", "reset-failed", "uvicorn"], timeout=10)
                run_cmd(["systemctl", "start", "uvicorn"], timeout=30)

            if no_jobs and uvicorn_ok and nginx_ok and swagger_ok:
                return True, last_info

        except Exception as exc:
            last_info = {"exception": str(exc), "attempt": attempt}
            print(f"[{utc_now()}] Stabilization attempt {attempt} exception: {exc}")

        time.sleep(delay_seconds)

    return False, last_info


def main():
    if len(sys.argv) not in (3, 4):
        print("Usage: full_restore_runner.py <backup_id> <job_id> [safe|complete]")
        return 2

    backup_id = sys.argv[1]
    job_id    = sys.argv[2]
    mode      = sys.argv[3] if len(sys.argv) == 4 else "safe"

    if mode not in ("safe", "complete"):
        print("Mode must be 'safe' or 'complete'")
        return 2

    state_file = JOBS_ROOT / f"{job_id}.json"
    log_file   = JOBS_ROOT / "logs" / f"{job_id}.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    started_at = utc_now()
    mode_label = "Full DR" if mode == "complete" else "Safe"

    # Signal watchdog: don't interfere with service restarts during restore
    set_restore_mode(job_id)

    try:
        os.chdir(PROJECT_ROOT)
        sys.path.insert(0, str(PROJECT_ROOT))
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "asguard.settings")

        import django
        django.setup()

        from backend.backup.system_backup.restore_service import RestoreService
        from backend.backup.notifications import notify_restore_started, notify_restore_completed

        write_json(state_file, {
            "job_id":     job_id,
            "backup_id":  backup_id,
            "mode":       mode,
            "status":     "running",
            "started_at": started_at,
            "finished_at": None,
            "log_file":   str(log_file),
            "result":     None,
        })

        # ── Notify: restore started ─────────────────────────────────────────
        try:
            notify_restore_started(backup_id, mode)
        except Exception as _e:
            print(f"[{utc_now()}] notify_restore_started failed (non-blocking): {_e}")

        # Direct ntfy backup (in case Django/email path fails after network restore)
        send_ntfy_direct(
            title=f"🔄 Restauration {mode_label} démarrée",
            body=(
                f"Backup : {backup_id}\n"
                f"⚠️  L'interface sera indisponible ~2-5 min.\n"
                f"Des notifications seront envoyées à chaque étape."
            ),
            priority="high",
            tags="arrows_counterclockwise,rotating_light,shield",
        )

        print(f"[{utc_now()}] FULL RESTORE STARTED: backup_id={backup_id}, job_id={job_id}, mode={mode}")

        t0 = time.time()
        progress_cb = make_progress_callback(state_file)
        if mode == "complete":
            result = RestoreService.restore_full_complete(backup_id, progress_callback=progress_cb)
        else:
            result = RestoreService.restore_full_safe(backup_id, progress_callback=progress_cb)
        duration_s = time.time() - t0

        print(f"[{utc_now()}] RESTORE CORE FINISHED: raw_status={result.get('status', 'error')}, mode={mode}")

        # ── Force uvicorn recovery before stabilization check ───────────────
        uvicorn_recovered = force_uvicorn_recovery()
        if not uvicorn_recovered:
            send_ntfy_direct(
                title="⚠️  Uvicorn ne répond pas après restauration",
                body="L'interface n'est pas encore disponible — nouvelle tentative automatique...",
                priority="urgent",
                tags="warning,shield,rotating_light",
            )

        print(f"[{utc_now()}] STARTING POST-RESTORE STABILIZATION...")
        stabilize_ok, stabilize_info = wait_for_system_stabilization(max_attempts=30, delay_seconds=4)

        if isinstance(result, dict):
            result["stabilization"] = {
                "status":  "success" if stabilize_ok else "partial",
                "details": stabilize_info,
            }

        final_status = result.get("status", "error")
        if final_status == "success" and not stabilize_ok:
            final_status = "partial_success"

        final_status_label = (
            "success" if final_status == "success"
            else ("error" if final_status == "error" else "partial_success")
        )

        summary           = result.get("summary", {})
        components_ok     = summary.get("success", 0)
        components_failed = summary.get("failed", 0)

        write_json(state_file, {
            "job_id":      job_id,
            "backup_id":   backup_id,
            "mode":        mode,
            "status":      final_status_label,
            "started_at":  started_at,
            "finished_at": utc_now(),
            "log_file":    str(log_file),
            "result":      result,
        })

        # ── Clear restore lock BEFORE sending notifications ─────────────────
        clear_restore_mode()

        # ── Notify: restore completed ───────────────────────────────────────
        try:
            notify_restore_completed(
                backup_id=backup_id,
                mode=mode,
                success=(final_status_label == "success"),
                duration_s=duration_s,
                components_ok=components_ok,
                components_failed=components_failed,
            )
        except Exception as _e:
            print(f"[{utc_now()}] notify_restore_completed failed (non-blocking): {_e}")

        # Direct ntfy final status (independent of Django)
        ok = final_status_label in ("success", "partial_success")
        send_ntfy_direct(
            title=f"{'✅ Restauration terminée' if ok else '❌ Restauration échouée'} — {mode_label}",
            body=(
                f"Backup : {backup_id}\n"
                f"Composants OK : {components_ok} | KO : {components_failed}\n"
                f"Durée : {int(duration_s)}s\n"
                f"{'✅ Système opérationnel.' if stabilize_ok else '⚠️  Stabilisation incomplète — vérifiez uvicorn.'}"
            ),
            priority="default" if ok else "urgent",
            tags="white_check_mark,shield" if ok else "x,shield,rotating_light",
        )

        print(f"[{utc_now()}] FULL RESTORE FINISHED: status={final_status_label}, mode={mode}")
        print(json.dumps(result, indent=2))

        return 0 if final_status_label in ("success", "partial_success") else 1

    except Exception as exc:
        tb = traceback.format_exc()

        try:
            write_json(state_file, {
                "job_id":      job_id,
                "backup_id":   backup_id,
                "mode":        mode,
                "status":      "error",
                "started_at":  started_at,
                "finished_at": utc_now(),
                "log_file":    str(log_file),
                "result":      {"message": str(exc), "traceback": tb},
            })
        except Exception:
            pass

        clear_restore_mode()

        send_ntfy_direct(
            title="❌ Erreur critique — Restauration plantée",
            body=f"Backup : {backup_id}\nErreur : {str(exc)[:200]}\nConsultez les logs : {log_file}",
            priority="urgent",
            tags="x,shield,rotating_light",
        )

        print(f"[{utc_now()}] FULL RESTORE CRASHED: {exc}")
        print(tb)
        return 1

    finally:
        # Always clear the restore lock even on unexpected exit
        clear_restore_mode()


if __name__ == "__main__":
    raise SystemExit(main())
