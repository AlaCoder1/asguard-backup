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


# After a COMPLETE (whole-VM) restore, networking/internet only fully comes back
# once the box reboots (restored NetworkManager profiles + routing need a clean
# init). The web reboot button is unreliable here because uvicorn's single worker
# is starved by the post-restore I/O storm. So we let SYSTEMD schedule the reboot
# from the root runner — it fires even if the VM is saturated and uvicorn is dead.
POST_RESTORE_REBOOT_DELAY = 300          # seconds before the auto-reboot fires
POST_RESTORE_REBOOT_UNIT  = "asguard-post-restore-reboot"


def schedule_post_restore_reboot(delay: int = POST_RESTORE_REBOOT_DELAY):
    """Schedule a one-shot reboot via a transient systemd timer (we run as root).
    Returns (ok, reboot_at_epoch, unit). Best-effort — never raises."""
    try:
        # Clear any stale unit from a previous restore so --unit is free to reuse.
        subprocess.run(
            ["systemctl", "reset-failed", f"{POST_RESTORE_REBOOT_UNIT}.timer",
             f"{POST_RESTORE_REBOOT_UNIT}.service"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15, check=False,
        )
        subprocess.run(["systemctl", "stop", f"{POST_RESTORE_REBOOT_UNIT}.timer"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15, check=False)
        proc = subprocess.run(
            ["systemd-run", f"--on-active={int(delay)}", "--timer-property=AccuracySec=1s",
             "--unit", POST_RESTORE_REBOOT_UNIT, "/usr/bin/systemctl", "reboot"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=20, check=False,
        )
        ok = proc.returncode == 0
        if not ok:
            print(f"[{utc_now()}] schedule reboot failed rc={proc.returncode}: {proc.stdout.strip()}")
        return ok, (time.time() + int(delay) if ok else None), POST_RESTORE_REBOOT_UNIT
    except Exception as exc:
        print(f"[{utc_now()}] schedule_post_restore_reboot crashed: {exc}")
        return False, None, POST_RESTORE_REBOOT_UNIT


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
    # A slow `systemctl daemon-reload` under the post-restore I/O storm can blow
    # past the timeout and raise TimeoutExpired. That MUST NOT crash the runner
    # (it used to, wiping a successful restore's summary to a false "Erreur").
    # Swallow it and return a non-zero result the callers already tolerate.
    try:
        return subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print(f"[{utc_now()}] run_cmd timed out ({timeout}s, non-fatal): {' '.join(cmd)}")
        return subprocess.CompletedProcess(cmd, returncode=124, stdout="", stderr="timeout")
    except Exception as exc:
        print(f"[{utc_now()}] run_cmd error (non-fatal): {' '.join(cmd)} -> {exc}")
        return subprocess.CompletedProcess(cmd, returncode=1, stdout="", stderr=str(exc))


# ── post-restore recovery ─────────────────────────────────────────────────────

def force_uvicorn_recovery():
    """Reset systemd StartLimit and ensure uvicorn is running after restore."""
    print(f"[{utc_now()}] POST-RESTORE: resetting uvicorn StartLimit and ensuring service is up...")

    # Reset the failed counter so systemd will restart it again even after 5 crashes.
    # daemon-reload gets a generous timeout: under the post-restore I/O storm systemd
    # can take well over 30s, and run_cmd no longer crashes on timeout anyway.
    run_cmd(["systemctl", "reset-failed", "uvicorn"], timeout=30)
    run_cmd(["systemctl", "daemon-reload"], timeout=120)

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


def force_db_recovery(max_attempts=20, delay_seconds=3):
    """Ensure the PostgreSQL Docker container is up and accepting connections
    after a restore. A full restore rolls back the LVM volume holding the pgdb
    data and can leave the container stopped (its restart policy metadata lives
    on the root disk, which a complete restore may revert). The CLI login menu
    queries port 5391 immediately, so if the DB isn't back yet it shows
    'Connection refused'. This brings it up, re-asserts restart=always, and
    waits until pg_isready succeeds. Best-effort, non-fatal."""
    print(f"[{utc_now()}] POST-RESTORE: ensuring PostgreSQL container is up...")
    db_container = "app-db-container"

    # Docker daemon itself may still be coming up after the reboot/restore.
    run_cmd(["systemctl", "start", "docker"], timeout=60)

    # Start the container (no-op if already running) and re-assert the policy so
    # it survives the next reboot even if the metadata was reverted by restore.
    run_cmd(["docker", "start", db_container], timeout=60)
    run_cmd(["docker", "update", "--restart", "always", db_container], timeout=30)

    for attempt in range(1, max_attempts + 1):
        ready = run_cmd(
            ["docker", "exec", "-u", "postgres", db_container, "pg_isready", "-q"],
            timeout=15,
        )
        if ready.returncode == 0:
            print(f"[{utc_now()}] PostgreSQL ready after {attempt} attempt(s).")
            return True
        # If the container died, try starting it again before the next probe.
        run_cmd(["docker", "start", db_container], timeout=30)
        time.sleep(delay_seconds)

    print(f"[{utc_now()}] PostgreSQL STILL not ready after {max_attempts} attempts.")
    return False


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
        print("Usage: full_restore_runner.py <backup_id> <job_id> [safe|complete|ui_full]")
        return 2

    backup_id = sys.argv[1]
    job_id    = sys.argv[2]
    mode      = sys.argv[3] if len(sys.argv) == 4 else "safe"

    if mode not in ("safe", "complete", "ui_full"):
        print("Mode must be 'safe', 'complete', or 'ui_full'")
        return 2

    state_file = JOBS_ROOT / f"{job_id}.json"
    log_file   = JOBS_ROOT / "logs" / f"{job_id}.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    started_at = utc_now()
    mode_label = "Full UI Safe" if mode == "ui_full" else ("Full DR" if mode == "complete" else "Safe")

    # Signal watchdog: don't interfere with service restarts during restore
    set_restore_mode(job_id)

    result = None   # holds the component result so a late crash can preserve it
    duration_s = 0
    try:
        os.chdir(PROJECT_ROOT)
        sys.path.insert(0, str(PROJECT_ROOT))
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "asguard.settings")

        import django
        django.setup()

        from backend.backup.system_backup.restore_service import RestoreService
        from backend.backup.notifications import notify_restore_started, notify_restore_completed

        # Merge so the ETA fields the API seeded (estimated_seconds /
        # stabilize_estimate_seconds) survive into the running state.
        try:
            base_state = json.loads(state_file.read_text())
        except Exception:
            base_state = {}
        base_state.update({
            "job_id":     job_id,
            "backup_id":  backup_id,
            "mode":       mode,
            "status":     "running",
            "started_at": started_at,
            "finished_at": None,
            "log_file":   str(log_file),
            "result":     None,
        })
        write_json(state_file, base_state)

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
                +
                (
                    "Mode UI-safe : le moteur applicatif et les services de boot ne seront pas remplacés à chaud.\n"
                    if mode == "ui_full"
                    else "⚠️  L'interface sera indisponible ~2-5 min.\n"
                )
                + "Des notifications seront envoyées à chaque étape."
            ),
            priority="high",
            tags="arrows_counterclockwise,rotating_light,shield",
        )

        print(f"[{utc_now()}] FULL RESTORE STARTED: backup_id={backup_id}, job_id={job_id}, mode={mode}")

        t0 = time.time()
        progress_cb = make_progress_callback(state_file)
        if mode == "complete":
            result = RestoreService.restore_full_complete(backup_id, progress_callback=progress_cb)
        elif mode == "ui_full":
            result = RestoreService.restore_full_ui_safe(backup_id, progress_callback=progress_cb)
        else:
            result = RestoreService.restore_full_safe(backup_id, progress_callback=progress_cb)
        duration_s = time.time() - t0

        print(f"[{utc_now()}] RESTORE CORE FINISHED: raw_status={result.get('status', 'error')}, mode={mode}")

        # ── EARLY checkpoint: persist the full component result BEFORE the
        # (potentially fatal) stabilization phase. A COMPLETE restore restarts
        # uvicorn / triggers daemon-reloads from inside this very process; if it
        # gets SIGKILL'd during stabilization, this checkpoint is what lets the
        # UI + history finalize the job instead of showing "running" forever.
        # status stays non-terminal ("stabilizing") so the overlay keeps showing
        # the "verifying services" phase until the final write below. We MERGE so
        # the live components_progress / progress_pct stay intact for the overlay.
        try:
            try:
                checkpoint = json.loads(state_file.read_text())
            except Exception:
                checkpoint = {}
            checkpoint.update({
                "job_id":      job_id,
                "backup_id":   backup_id,
                "mode":        mode,
                "status":      "stabilizing",
                "phase":       "stabilizing",
                "started_at":  started_at,
                "finished_at": None,
                "log_file":    str(log_file),
                "result":      result,
            })
            write_json(state_file, checkpoint)
        except Exception as _e:
            print(f"[{utc_now()}] early checkpoint write failed (non-blocking): {_e}")

        # ── Post-restore recovery + stabilization ───────────────────────────
        # The component restore is already DONE (result holds the real summary +
        # system_changes + diff). Everything below is best-effort verification, so
        # it is wrapped: a slow daemon-reload or a stabilization hiccup during the
        # post-restore I/O storm must NEVER crash the runner and turn a successful
        # restore into a false "Erreur" in the history. Worst case → stabilization
        # is reported "partial/unconfirmed", but the restore is still recorded.
        stabilize_ok = False
        stabilize_info = {}
        try:
            # PostgreSQL must be back before uvicorn is useful: the app and the
            # CLI login menu both query port 5391. Bring the DB container up first.
            try:
                db_recovered = force_db_recovery()
                if not db_recovered:
                    send_ntfy_direct(
                        title="⚠️  PostgreSQL ne répond pas après restauration",
                        body="La base de données n'est pas encore disponible — nouvelle tentative automatique...",
                        priority="urgent",
                        tags="warning,floppy_disk,rotating_light",
                    )
            except Exception as _dbe:
                print(f"[{utc_now()}] DB recovery step failed (non-fatal): {_dbe}")

            # UI-safe full restore deliberately avoids touching the application
            # control plane, so don't daemon-reload/restart uvicorn unless it's down.
            if mode == "ui_full":
                uvicorn_active = run_cmd(["systemctl", "is-active", "uvicorn"], timeout=10)
                uvicorn_recovered = (uvicorn_active.stdout or "").strip() == "active"
            else:
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
        except Exception as _se:
            print(f"[{utc_now()}] post-restore stabilization step failed (non-fatal): {_se}")
            stabilize_info = {"error": str(_se), "note": "stabilization step crashed; restore itself completed"}

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

        # COMPLETE restore + verified success → schedule a RELIABLE auto-reboot via
        # systemd (root, survives the post-restore load). Required because internet/
        # networking only fully recovers after the box reboots into the restored
        # config. The UI shows the countdown from reboot_at and can cancel it.
        reboot_at = None
        if mode == "complete" and final_status_label == "success":
            r_ok, reboot_at, r_unit = schedule_post_restore_reboot()
            print(f"[{utc_now()}] post-restore reboot scheduled={r_ok} unit={r_unit} at={reboot_at}")

        write_json(state_file, {
            "job_id":      job_id,
            "backup_id":   backup_id,
            "mode":        mode,
            "status":      final_status_label,
            "phase":       "done",
            "started_at":  started_at,
            "finished_at": utc_now(),
            "log_file":    str(log_file),
            "result":      result,
            "reboot_at":   reboot_at,                 # epoch when systemd will reboot
            "reboot_unit": POST_RESTORE_REBOOT_UNIT if reboot_at else None,
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

        # Summarise the OS-level changes the restore made, so the push tells the
        # operator exactly what reverted (password, system users, hostname).
        sysc = (result or {}).get("system_changes") or {}
        sys_lines = []
        if sysc.get("root_password_changed"):
            sys_lines.append("🔑 mot de passe root restauré")
        for u in (sysc.get("users_removed") or []):
            sys_lines.append(f"👤 utilisateur système supprimé : {u}")
        for u in (sysc.get("users_added") or []):
            sys_lines.append(f"👤 utilisateur système ajouté : {u}")
        if sysc.get("hostname_changed"):
            sys_lines.append(f"🏷️ hostname : {sysc.get('hostname_from')} → {sysc.get('hostname_to')}")
        sys_block = ("\nChangements système :\n" + "\n".join(sys_lines)) if sys_lines else ""

        snaps = (result or {}).get("lvm_snapshots") or {}
        _removed = snaps.get("removed") or []
        snap_block = (f"\n📸 Snapshots LVM retirés (anti-amplification I/O) : {len(_removed)}"
                      if _removed else "")

        # Direct ntfy final status (independent of Django)
        ok = final_status_label in ("success", "partial_success")
        send_ntfy_direct(
            title=f"{'✅ Restauration terminée' if ok else '❌ Restauration échouée'} — {mode_label}",
            body=(
                f"Backup : {backup_id}\n"
                f"Composants OK : {components_ok} | KO : {components_failed}\n"
                f"Durée : {int(duration_s)}s\n"
                f"{'✅ Système opérationnel.' if stabilize_ok else '⚠️  Stabilisation incomplète — vérifiez uvicorn.'}"
                f"{sys_block}{snap_block}"
            ),
            priority="default" if ok else "urgent",
            tags="white_check_mark,shield" if ok else "x,shield,rotating_light",
        )

        print(f"[{utc_now()}] FULL RESTORE FINISHED: status={final_status_label}, mode={mode}")
        print(json.dumps(result, indent=2))

        return 0 if final_status_label in ("success", "partial_success") else 1

    except Exception as exc:
        tb = traceback.format_exc()

        # If the component restore ALREADY finished (result carries a summary), a
        # late crash — e.g. a slow daemon-reload in post-restore bookkeeping during
        # the I/O storm — must NOT be recorded as a failed restore. Preserve the
        # real result (with system_changes + diff) and record it as partial_success
        # (stabilization just couldn't be confirmed), so the history shows the truth.
        if isinstance(result, dict) and result.get("summary"):
            summ = result.get("summary") or {}
            recovered_status = ("partial_success" if summ.get("success", 0) > 0 else "error")
            result.setdefault("stabilization", {
                "status": "partial",
                "details": {"error": str(exc),
                            "note": "post-restore step crashed; components were restored"},
            })
            try:
                write_json(state_file, {
                    "job_id": job_id, "backup_id": backup_id, "mode": mode,
                    "status": recovered_status, "phase": "done",
                    "started_at": started_at, "finished_at": utc_now(),
                    "log_file": str(log_file), "result": result,
                })
            except Exception:
                pass
            clear_restore_mode()
            try:
                send_ntfy_direct(
                    title=f"✅ Restauration terminée (vérif. partielle) — {mode_label}",
                    body=(f"Backup : {backup_id}\n"
                          f"Composants OK : {summ.get('success', 0)} | KO : {summ.get('failed', 0)}\n"
                          f"La restauration s'est appliquée ; la stabilisation finale n'a pas pu être "
                          f"confirmée (système chargé). Rechargez l'interface."),
                    priority="default", tags="white_check_mark,shield",
                )
            except Exception:
                pass
            print(f"[{utc_now()}] RESTORE COMPLETED but post-step crashed → {recovered_status}: {exc}")
            print(tb)
            return 0

        # Genuine early crash (no component result yet) → record the failure.
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
