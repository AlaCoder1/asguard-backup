import json
import os
import logging
import shutil
import threading
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from django.db import transaction

from backend.network.models import Interface
from backend.rules.models import Rule
from .base import ComponentResult, run_cmd, safe_extract, Timer, compute_sha256

logger = logging.getLogger(__name__)


def _run_bounded(fn, timeout: float, default):
    """Run `fn()` on a daemon thread and give up after `timeout` seconds.

    The post-restore DB diff runs right after a COMPLETE restore has restarted
    uvicorn and reloaded PostgreSQL — connections can be in a half-broken state
    with no statement timeout, so a naive call can hang the whole restore runner
    forever (the exact failure that strands the progress banner). This caps it:
    a slow/hung diff is dropped, never blocking the terminal-status write."""
    box = {"value": default}

    def _target():
        try:
            box["value"] = fn()
        except Exception:
            logger.exception("bounded call failed (non-fatal)")

    t = threading.Thread(target=_target, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        logger.warning("bounded call exceeded %ss — using default", timeout)
        return default
    return box["value"]


class RestoreService:
    BACKUP_ROOT = Path("/var/backups/asguard")
    DB_CONTAINER = "app-db-container"
    DB_NAME = "postgres"
    APP_ROOT = Path("/asguard/asguard")
    RESTORE_MODE = "safe"
    # Set by _restore_network during a clone restore; read into the top-level
    # result so the UI can tell the operator the target IP to reconnect to.
    _LAST_CLONE_NETWORK: dict | None = None
    # Set at the start of every restore: which LVM snapshots are present (kept,
    # not touched). Surfaced in the report so the operator knows the restore ran
    # under low I/O priority because copy-on-write amplification was in play.
    _LAST_LVM_SNAPSHOTS: dict | None = None
    UI_FULL_EXCLUDED_COMPONENTS = {
        "application",
        "system_config",
        "systemd_services",
        "logs",
        "users_groups",
        "packages",
        "docker_state",
        "vm_snapshot",
    }

    @classmethod
    def restore_full_safe(cls, backup_id: str, progress_callback=None) -> dict:
        return cls._restore_full(backup_id, include_application=False, progress_callback=progress_callback)

    @classmethod
    def restore_full_complete(cls, backup_id: str, progress_callback=None) -> dict:
        return cls._restore_full(backup_id, include_application=True, progress_callback=progress_callback)

    @classmethod
    def restore_full_ui_safe(cls, backup_id: str, progress_callback=None) -> dict:
        return cls._restore_full(
            backup_id,
            include_application=False,
            excluded_components=cls.UI_FULL_EXCLUDED_COMPONENTS,
            mode_name="full_ui_safe",
            progress_callback=progress_callback,
        )

    @classmethod
    def restore_full(cls, backup_id: str) -> dict:
        return cls.restore_full_safe(backup_id)

    @classmethod
    def restore_components(cls, backup_id: str, components: list[str]) -> dict:
        return cls._restore_full(
            backup_id,
            include_application=True,
            selected_components=components,
            mode_name="selected_components",
        )

    @classmethod
    def _restore_full(
        cls,
        backup_id: str,
        include_application: bool,
        selected_components: list[str] | None = None,
        excluded_components: set[str] | None = None,
        mode_name: str | None = None,
        progress_callback=None,
    ) -> dict:
        cls.RESTORE_MODE = "complete" if include_application else "safe"
        cls._LAST_CLONE_NETWORK = None   # reset per-run clone network info

        backup_dir = cls.BACKUP_ROOT / backup_id
        if not backup_dir.exists():
            return {"status": "error", "message": f"Backup {backup_id} not found."}

        # ── LVM snapshots & restore safety ──────────────────────────────────────
        # The appliance bind-mounts /etc/* + PostgreSQL + backups onto the asguard-vg
        # data LV. An active snapshot of that LV copy-on-write amplifies every
        # restore write, which can saturate I/O and take the VM down. Snapshots are
        # VM-local (never part of a backup, never cloned). Per operator decision, a
        # COMPLETE (whole-VM/DR) restore REMOVES active snapshots up front so the
        # amplification can't happen; the target re-creates its own afterwards if it
        # has a 2nd disk. Lighter restores only record what's present.
        if include_application:
            cls._LAST_LVM_SNAPSHOTS = cls._clear_snapshots_before_restore()
        else:
            cls._LAST_LVM_SNAPSHOTS = cls._detect_lvm_snapshots()

        metadata_file = backup_dir / "backup_metadata.json"
        if not metadata_file.exists():
            return {"status": "error", "message": f"Backup metadata missing for {backup_id}."}

        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except Exception as e:
            return {"status": "error", "message": f"Could not read metadata: {e}"}

        results = {}

        runners = cls._component_runners()

        if include_application:
            runners["application"] = cls._restore_application
        else:
            runners["application"] = cls._restore_application_skipped

        excluded_components = excluded_components or set()
        for component_name in excluded_components:
            if component_name in runners:
                runners[component_name] = cls._restore_skipped_runner(
                    component_name,
                    "Skipped by UI-safe full restore to keep the appliance control plane online. "
                    "Use offline/console DR restore for this boot/runtime component.",
                )

        if selected_components is not None:
            selected = cls._normalize_components(selected_components, runners, metadata)
            if not selected:
                return {
                    "status": "error",
                    "message": "No valid restore components selected.",
                    "available_components": sorted(metadata.get("components", {}).keys()),
                }
            runners = {name: runners[name] for name in selected}

        all_runner_names = list(runners.keys())
        total = len(all_runner_names)
        components_progress = {c: "pending" for c in all_runner_names}

        # Pre-restore DB snapshot — captured *before* any component runs so
        # we can produce a row-level diff once the restore finishes. We
        # only snapshot components whose runner is actually about to fire
        # (selected/non-excluded) to keep the dump small.
        pre_snapshot: dict = {}
        try:
            from backend.backup.restore_diff import snapshot_db_state
            pre_snapshot = snapshot_db_state(all_runner_names)
        except Exception:
            logger.exception("Pre-restore DB snapshot failed (non-fatal)")
            pre_snapshot = {}

        # System identity BEFORE the restore (root password hash, system users,
        # hostname) so we can report the system-level changes — not just DB rows.
        pre_system = cls._capture_system_identity()

        if progress_callback:
            try:
                progress_callback({
                    "components_order": all_runner_names,
                    "components_progress": dict(components_progress),
                    "current_component": None,
                    "progress_pct": 0,
                    "done": 0,
                    "total": total,
                })
            except Exception:
                pass

        done = 0
        for component_name, runner in runners.items():
            components_progress[component_name] = "running"
            if progress_callback:
                try:
                    progress_callback({
                        "components_order": all_runner_names,
                        "components_progress": dict(components_progress),
                        "current_component": component_name,
                        "progress_pct": int(done / total * 100) if total else 0,
                        "done": done,
                        "total": total,
                    })
                except Exception:
                    pass

            comp_meta = metadata.get("components", {}).get(component_name)
            if not comp_meta:
                results[component_name] = ComponentResult.skipped(
                    component_name, "No metadata for component"
                ).to_dict()
            elif comp_meta.get("status") != "success":
                results[component_name] = ComponentResult.skipped(
                    component_name,
                    f"Component status is {comp_meta.get('status')}"
                ).to_dict()
            else:
                ok, msg = cls._verify_component_file(backup_dir, component_name, comp_meta)
                if not ok:
                    results[component_name] = ComponentResult.failed(component_name, msg).to_dict()
                else:
                    try:
                        result = runner(backup_dir, comp_meta)
                        results[component_name] = result.to_dict()
                        # After the component's config files are restored,
                        # replay its PostgreSQL rows from the per-component
                        # DB snapshot so the database matches what the UI
                        # shows (NAT rules, routes, WAF rules, …).
                        if results[component_name].get("status") != "failed":
                            db_ok, db_msg = cls._restore_component_db(backup_dir, component_name)
                            if db_msg:
                                existing = results[component_name].get("message", "") or ""
                                # DB detail FIRST — it is the most meaningful
                                # part and the UI column truncates long text.
                                results[component_name]["message"] = (
                                    f"{db_msg} · {existing}".strip(" ·")
                                )
                                results[component_name]["db_restore"] = {
                                    "ok": db_ok, "message": db_msg,
                                }
                            if not db_ok:
                                results[component_name]["status"] = "partial_success"
                    except Exception as e:
                        logger.exception("Restore failed for component %s", component_name)
                        results[component_name] = ComponentResult.failed(component_name, str(e)).to_dict()

            components_progress[component_name] = results[component_name]["status"]
            done += 1
            if progress_callback:
                try:
                    progress_callback({
                        "components_order": all_runner_names,
                        "components_progress": dict(components_progress),
                        "current_component": component_name,
                        "progress_pct": int(done / total * 100) if total else 100,
                        "done": done,
                        "total": total,
                    })
                except Exception:
                    pass

        success = sum(1 for r in results.values() if r["status"] == "success")
        failed = sum(1 for r in results.values() if r["status"] == "failed")
        skipped = sum(1 for r in results.values() if r["status"] == "skipped")

        global_status = "success" if failed == 0 else ("failed" if success == 0 else "partial_success")

        # Network DB ↔ system reconcile. The file-based restore brings back the
        # NM profiles (network component) and/or the DB (database component)
        # independently; re-derive the DB network rows from the just-restored
        # profiles so UI ↔ system ↔ DB agree without waiting for the startup
        # reconcile. Best-effort: never turns a successful restore into a failure.
        network_db_reconcile: dict = {}
        if all_runner_names and any(
            c in all_runner_names for c in ("network", "vlan", "vxlan", "database")
        ):
            try:
                from backend.network.reconcile import reconcile_network_db_from_system
                network_db_reconcile = reconcile_network_db_from_system()
            except Exception:
                logger.exception("post-restore network reconcile failed (non-fatal)")

        # Reconcile /etc/fstab with THIS host: if the LVM volume group isn't
        # present (restored onto a VM without the 2nd disk), strip the LVM/bind
        # lines so the box runs natively instead of hanging on missing devices.
        # Best-effort — must never turn a successful restore into a failure.
        fstab_reconcile: dict = {}
        try:
            fstab_reconcile = cls._reconcile_fstab_native()
        except Exception:
            logger.exception("fstab reconcile failed (non-fatal)")
            fstab_reconcile = {"mode": "unknown", "changed": False}

        # Re-assert write access to the backup root. A COMPLETE/DR restore swaps
        # the LV / bind mount carrying /var/backups/asguard, which can reset its
        # owner to root:root and — worse — leave the POSIX ACL mask at r-x, which
        # silently strips the write bit even from the `user:uvicorn:rwx` entry
        # (`#effective:r-x`). Django runs as uvicorn, so every subsequent
        # scheduled backup then dies with `[Errno 13] Permission denied` creating
        # its folder. Repair the mask/ACL here so backups keep working after a
        # restore. Best-effort — must never turn a successful restore into a failure.
        try:
            cls._reconcile_backup_root_permissions()
        except Exception:
            logger.exception("backup-root permission reconcile failed (non-fatal)")

        # Post-restore diff — capture the live DB state again and compare
        # against the pre-snapshot to give the operator a row-level
        # report (which rules vanished, which ZTNA identities reappeared,
        # which NAT entries changed). Whole block is best-effort: a
        # broken diff must never mask a successful restore.
        # `available: False` marks a diff that could NOT be computed (timed out /
        # DB unreachable) — distinct from a diff that ran and found no changes. The
        # UI must say "report unavailable", NOT the misleading "identical".
        _empty_diff = {"components": {}, "totals": {
            "added": 0, "removed": 0, "modified": 0, "changed_components": 0,
        }, "available": False}

        def _resync_runtime():
            from backend.backup.post_restore_resync import resync_all
            return resync_all()

        def _compute_post_diff():
            from backend.backup.restore_diff import snapshot_db_state, diff_db_states
            post_snapshot = snapshot_db_state(all_runner_names)
            out = diff_db_states(pre_snapshot, post_snapshot)
            out["available"] = True
            return out

        # Bounded so a hung query can't strand the runner. Now that the restore runs
        # under an I/O cap, the DB stays responsive, so a generous 120s is safe.
        diff_payload = _run_bounded(_compute_post_diff, timeout=120, default=_empty_diff)

        # System-level changes (root password, system users, hostname) — what the
        # restore actually changed at the OS level, which the DB row-diff can't show.
        post_system = cls._capture_system_identity()
        system_changes = cls._diff_system_identity(pre_system, post_system)

        # Push the restored DB state back into the kernel (nft ruleset, routing
        # table, NAT). The components restore files + DB rows; without this the UI
        # would list routes and rules the kernel never received. Bounded and
        # non-fatal: a failed resync must not turn a good restore into a failure.
        resync_payload = _run_bounded(
            _resync_runtime, timeout=120,
            default={"status": "error", "message": "resync timed out"},
        )

        return {
            "status": global_status,
            "backup_id": backup_id,
            "mode": mode_name or ("full_complete" if include_application else "full_safe"),
            "results": results,
            "summary": {
                "success": success,
                "failed": failed,
                "skipped": skipped,
            },
            "resync": resync_payload,
            "diff": diff_payload,
            "system_changes": system_changes,
            "fstab_reconcile": fstab_reconcile,
            "network_db_reconcile": network_db_reconcile,
            "clone_network": cls._LAST_CLONE_NETWORK,
            "lvm_snapshots": cls._LAST_LVM_SNAPSHOTS,
        }

    @classmethod
    def available_restore_components(cls, backup_id: str | None = None) -> list[str]:
        if not backup_id:
            return list(cls._component_runners().keys())

        metadata_file = cls.BACKUP_ROOT / backup_id / "backup_metadata.json"
        if not metadata_file.exists():
            return []
        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            return [
                name
                for name, data in metadata.get("components", {}).items()
                if data.get("status") == "success" and name in cls._component_runners()
            ]
        except Exception:
            return []

    @classmethod
    def _normalize_components(
        cls,
        components: list[str],
        runners: dict,
        metadata: dict,
    ) -> list[str]:
        available = metadata.get("components", {})
        selected: list[str] = []
        for component in components or []:
            name = str(component).strip()
            if name in runners and name in available and name not in selected:
                selected.append(name)
        return selected

    @classmethod
    def _component_runners(cls) -> dict:
        return {
            "users_groups": cls._restore_users_groups,
            "packages": cls._restore_packages,
            "system_config": cls._restore_extract_only,
            "network": cls._restore_network,
            "certificates": cls._restore_extract_only,
            "security": cls._restore_security,
            "firewall": cls._restore_firewall,
            "vpn": cls._restore_vpn,
            "web": cls._restore_web,
            "ids": cls._restore_ids,
            "proxy": cls._restore_proxy,
            "scheduled_tasks": cls._restore_extract_only,
            "database": cls._restore_database,
            "docker_state": cls._restore_docker_state,
            "systemd_services": cls._restore_systemd_services,
            "logs": cls._restore_logs,
            "vm_snapshot": cls._restore_vm_snapshot,
            "ztna": cls._restore_extract_only,
            "ldap": cls._restore_extract_only,
            "ipsec_detailed": cls._restore_extract_only,
            "routing": cls._restore_routing,
            "vlan": cls._restore_extract_only,
            "vxlan": cls._restore_extract_only,
            "sdwan": cls._restore_extract_only,
            "waf": cls._restore_waf,
            "nat": cls._restore_nat,
            "dhcp": cls._restore_dhcp,
            "gateway": cls._restore_extract_only,
            "double_mask": cls._restore_extract_only,
        }

    @classmethod
    def _restore_skipped_runner(cls, name: str, reason: str):
        def _runner(_backup_dir: Path, _component_meta: dict) -> ComponentResult:
            return ComponentResult.skipped(name, reason)

        return _runner

    @classmethod
    def _verify_component_file(cls, backup_dir: Path, component_name: str, component_meta: dict) -> tuple[bool, str]:
        rel_file = component_meta.get("file", "")
        expected_sha = component_meta.get("sha256", "")

        if not rel_file:
            return False, f"{component_name}: missing file path in metadata"

        target = backup_dir / rel_file
        if not target.exists():
            return False, f"{component_name}: backup file not found: {rel_file}"

        if expected_sha:
            actual_sha = compute_sha256(target)
            if actual_sha != expected_sha:
                return False, f"{component_name}: sha256 mismatch"

        return True, ""

    # /etc/fstab describes THIS host's physical disks + LVM layout. It is ALWAYS
    # excluded from extraction (and reconciled separately): adopting a backed-up
    # machine's fstab with an LVM volume that doesn't exist here makes mounts fail
    # → emergency mode on reboot. fstab is disk geometry, not "config", so excluding
    # it does not affect the clone the operator sees.
    _FSTAB_EXCLUDES = ("etc/fstab", "./etc/fstab")

    # NetworkManager connection profiles pin the LAN/WAN IP. They are the network
    # IDENTITY of the appliance. A COMPLETE (DR) restore reproduces the exact VM —
    # same IP — so it RESTORES them. Lighter modes (safe / ui_full) keep the
    # target's current IP to avoid disrupting a live box, so they exclude these.
    _NETWORK_IDENTITY_EXCLUDES = (
        "etc/NetworkManager/system-connections",
        "etc/NetworkManager/system-connections/*",
        "./etc/NetworkManager/system-connections",
        "./etc/NetworkManager/system-connections/*",
    )

    # Back-compat alias (fstab + network identity) for any external caller.
    _HOST_IDENTITY_EXCLUDES = _FSTAB_EXCLUDES + _NETWORK_IDENTITY_EXCLUDES

    @classmethod
    def _clone_excludes(cls) -> tuple:
        """Extraction excludes for an /etc-bearing archive. fstab is always out
        (disk safety); network identity is out only when NOT doing a complete/DR
        clone. In complete mode this returns just the fstab excludes, so the source
        machine's IP / NM profiles ARE restored → a true clone."""
        if cls.RESTORE_MODE == "complete":
            return cls._FSTAB_EXCLUDES
        return cls._FSTAB_EXCLUDES + cls._NETWORK_IDENTITY_EXCLUDES

    @classmethod
    def _extract_archive_to_root(cls, archive: Path, timeout: int = 180,
                                 preserve_identity: bool = False,
                                 excludes: tuple | None = None) -> tuple[bool, str]:
        cmd = ["sudo", "/usr/bin/tar", "--overwrite"]
        patterns = excludes if excludes is not None else (
            cls._HOST_IDENTITY_EXCLUDES if preserve_identity else ()
        )
        for pattern in patterns:
            cmd.append(f"--exclude={pattern}")
        cmd += ["-xzf", str(archive), "-C", "/"]
        res = run_cmd(cmd, timeout=timeout)
        if not res["success"]:
            return False, res.get("error", res.get("stderr", "archive extraction failed"))
        return True, ""

    # ── fstab safety (full-VM restore onto a possibly-different machine) ──────
    # /etc/fstab describes THIS host's physical disks + LVM layout. Adopting a
    # backed-up machine's fstab is dangerous: mismatched partition UUIDs or an
    # LVM volume that doesn't exist here (no 2nd disk) make mounts fail → the
    # box becomes slow, loses nginx/uvicorn, and can drop to emergency mode on
    # reboot. So we never let the restore overwrite the target's fstab, and we
    # strip the asguard LVM/bind lines when LVM isn't available (native mode).
    _FSTAB              = Path("/etc/fstab")
    _FSTAB_LVM_MARKER   = "# asguard-lvm-migration"

    @classmethod
    def _write_root_file(cls, path: str, content: str) -> bool:
        try:
            tmp = Path("/tmp/.asguard_fstab.tmp")
            tmp.write_text(content)
            res = run_cmd(["sudo", "/usr/bin/cp", str(tmp), path], timeout=20)
            try:
                tmp.unlink()
            except Exception:
                pass
            return bool(res.get("success"))
        except Exception as exc:
            logger.warning("write %s failed: %s", path, exc)
            return False

    @classmethod
    def _lvm_volume_group_present(cls) -> bool:
        """True if the asguard LVM is present. MUST NOT return a false negative:
        a wrong "absent" makes _reconcile_fstab_native strip the LVM/bind lines
        from fstab, which unmounts the volume that holds PostgreSQL data, the
        backups and all /etc binds → total outage. So we trust strong, cheap
        signals first (device exists / volume mounted) and only fall back to
        `vgs` with retries to ride out transient failures under I/O load."""
        # Strongest signals — if true, LVM is unquestionably present.
        try:
            if (os.path.exists("/dev/asguard-vg/asguard-data")
                    or os.path.exists("/dev/mapper/asguard--vg-asguard--data")
                    or os.path.ismount("/var/asguard_data")):
                return True
        except Exception:
            pass
        # Retry vgs to survive a transient timeout under heavy restore I/O.
        for attempt in range(3):
            try:
                res = run_cmd(["sudo", "-n", "vgs", "--noheadings", "asguard-vg"], timeout=15)
                if res.get("success"):
                    return True
            except Exception:
                pass
            if attempt < 2:
                run_cmd(["sleep", "2"], timeout=4)
        return False

    @classmethod
    def _reconcile_backup_root_permissions(cls) -> dict:
        """Ensure the uvicorn service account can still create backup folders
        under /var/backups/asguard after a restore. A COMPLETE restore swaps the
        underlying LV/bind mount and can reset the backup root to root:root with
        an ACL mask of r-x — which cancels the write bit on the uvicorn ACL entry
        (`user:uvicorn:rwx  #effective:r-x`), so scheduled backups then fail with
        Permission denied. We re-grant the uvicorn/UpApp ACLs, force the mask back
        to rwx, and set the same defaults so newly created backup folders inherit
        write access. Best-effort via sudo -n; failures are logged, never raised."""
        root = str(cls.BACKUP_ROOT)
        acl_spec = "u:uvicorn:rwx,u:UpApp:rwx,m::rwx"
        cmds = [
            # setgid + group-write so new subfolders inherit the group and stay writable
            ["sudo", "-n", "chmod", "2775", root],
            # live ACL entries + mask (fixes the r-x mask that strips write)
            ["sudo", "-n", "setfacl", "-m", acl_spec, root],
            # default ACL so future backup folders inherit the write grant
            ["sudo", "-n", "setfacl", "-d", "-m", acl_spec, root],
        ]
        results = {}
        for cmd in cmds:
            r = run_cmd(cmd, timeout=15)
            results[cmd[2]] = bool(r.get("success"))
        changed = any(results.values())
        logger.info("backup-root permission reconcile: %s", results)
        return {"changed": changed, "results": results}

    @classmethod
    def _reconcile_fstab_native(cls) -> dict:
        """If the asguard LVM volume group is absent here (e.g. restored onto a
        VM without the 2nd disk), strip the LVM mount + bind-mount lines from
        /etc/fstab so the appliance boots and runs natively (configs in /etc,
        backups in /var/backups, postgres in its Docker volume) instead of
        hanging on missing devices. No-op when LVM IS present. Best-effort."""
        # 2nd disk + asguard LVM present → keep the fstab LVM/bind lines AND bring
        # the volume online automatically (activate VG + mount) so the data volume
        # is usable immediately, without waiting for a reboot. No 2nd disk → fall
        # through to native mode below so the box never hangs on a missing device.
        if cls._lvm_volume_group_present():
            activated = run_cmd(["sudo", "vgchange", "-ay", "asguard-vg"], timeout=30)
            # Only run `mount -a` if the data volume isn't already mounted (e.g.
            # restored onto a fresh 2nd-disk VM that hasn't mounted it yet). On a
            # normally-booted appliance it's already mounted, so we skip the churn.
            already = os.path.ismount("/var/asguard_data")
            mounted = {"success": True}
            if not already:
                mounted = run_cmd(["sudo", "mount", "-a"], timeout=45)
            return {
                "mode": "lvm",
                "changed": False,
                "activated": bool(activated.get("success")),
                "mounted": bool(mounted.get("success")),
                "mount_skipped": already,
            }
        # Defense-in-depth: NEVER strip mount lines while the device exists or the
        # volume is mounted. The bind mounts carry PostgreSQL data, backups and the
        # /etc configs — stripping them on a live LVM box is catastrophic. If we got
        # here but these are present, treat it as LVM mode (no change).
        try:
            if (os.path.exists("/dev/asguard-vg/asguard-data")
                    or os.path.exists("/dev/mapper/asguard--vg-asguard--data")
                    or os.path.ismount("/var/asguard_data")):
                logger.warning("fstab reconcile: refusing to strip — LVM device/mount present")
                return {"mode": "lvm", "changed": False, "guard": "device_or_mount_present"}
        except Exception:
            pass

        try:
            lines = cls._FSTAB.read_text().splitlines()
        except Exception as exc:
            return {"mode": "native", "changed": False, "error": str(exc)}

        kept, removed = [], 0
        for line in lines:
            is_lvm_mount = ("asguard-vg/asguard-data" in line
                            or "asguard--vg-asguard--data" in line) and "/var/asguard_data" in line
            if cls._FSTAB_LVM_MARKER in line or is_lvm_mount:
                removed += 1
                continue
            kept.append(line)

        if removed == 0:
            return {"mode": "native", "changed": False}

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_cmd(["sudo", "/usr/bin/cp", str(cls._FSTAB),
                 f"/etc/fstab.asguard-pre-restore.{ts}"], timeout=20)
        ok = cls._write_root_file(str(cls._FSTAB), "\n".join(kept).rstrip("\n") + "\n")
        if ok:
            run_cmd(["sudo", "systemctl", "daemon-reload"], timeout=30)
        return {"mode": "native", "changed": ok, "removed": removed,
                "backup": f"/etc/fstab.asguard-pre-restore.{ts}"}

    @staticmethod
    def _capture_system_identity() -> dict:
        """Read OS-level identity (root password hash, system users, hostname) so
        a restore can report what it changed at the system level. The detached
        complete restore runs as root and can read /etc/shadow; under uvicorn it
        is unreadable → root_hash stays None (best-effort)."""
        out = {"root_hash": None, "users": [], "hostname": None}
        try:
            for line in Path("/etc/shadow").read_text(errors="ignore").splitlines():
                if line.startswith("root:"):
                    out["root_hash"] = line.split(":")[1]
                    break
        except Exception:
            pass
        try:
            out["users"] = sorted(
                l.split(":")[0] for l in Path("/etc/passwd").read_text(errors="ignore").splitlines()
                if l.strip() and not l.startswith("#")
            )
        except Exception:
            pass
        try:
            out["hostname"] = Path("/etc/hostname").read_text().strip()
        except Exception:
            pass
        return out

    @staticmethod
    def _diff_system_identity(pre: dict, post: dict) -> dict:
        """Compare two _capture_system_identity() snapshots (pre vs post restore)
        into a human-facing summary of what the restore changed at the OS level."""
        pre = pre or {}
        post = post or {}
        pre_u, post_u = set(pre.get("users") or []), set(post.get("users") or [])
        pwd_changed = bool(
            pre.get("root_hash") and post.get("root_hash")
            and pre["root_hash"] != post["root_hash"]
        )
        users_removed = sorted(pre_u - post_u)   # were present, gone after restore
        users_added = sorted(post_u - pre_u)     # appeared after restore
        host_changed = bool(
            pre.get("hostname") is not None and post.get("hostname") is not None
            and pre["hostname"] != post["hostname"]
        )
        return {
            "root_password_changed": pwd_changed,
            "users_removed": users_removed,
            "users_added": users_added,
            "hostname_changed": host_changed,
            "hostname_from": pre.get("hostname"),
            "hostname_to": post.get("hostname"),
            "any": bool(pwd_changed or users_removed or users_added or host_changed),
            "checked": bool(pre.get("root_hash") or pre.get("users")),
        }

    @classmethod
    def _list_active_snapshots(cls) -> list[str]:
        """Names of real LVM snapshots on asguard-vg (best-effort, never raises)."""
        names = []
        try:
            from .lvm_snapshot_service import LVMSnapshotService as _Svc
            for s in _Svc.list_snapshots() or []:
                name = s.get("lv_name") or s.get("name") or ""
                attr = s.get("attr", "") or ""
                origin = s.get("origin", "") or ""
                if name and (attr[:1] in ("s", "S") or bool(origin)):
                    names.append(name)
        except Exception as exc:
            logger.warning("LVM snapshot list: %s", exc)
        return names

    @classmethod
    def _detect_lvm_snapshots(cls) -> dict:
        """Record active snapshots WITHOUT touching them (lighter restore modes)."""
        present = cls._list_active_snapshots()
        return {"checked": True, "present": present, "count": len(present), "removed": []}

    @classmethod
    def _clear_snapshots_before_restore(cls) -> dict:
        """Remove active LVM snapshots before a COMPLETE restore so their copy-on-
        write amplification can't saturate I/O and take the VM down. Snapshots are
        VM-local and recreatable. Best-effort; never raises, never fails the
        restore. Runs as root in the detached restore unit (lvremove in sudoers)."""
        result = {"checked": True, "present": [], "removed": [], "errors": []}
        names = cls._list_active_snapshots()
        result["present"] = list(names)
        for name in names:
            res = run_cmd(["sudo", "lvremove", "-f", f"asguard-vg/{name}"], timeout=180)
            if res.get("success"):
                logger.info("Restore: removed LVM snapshot %s (avoid I/O amplification)", name)
                result["removed"].append(name)
            else:
                err = res.get("error") or res.get("stderr") or "lvremove failed"
                logger.warning("Restore: could not remove snapshot %s: %s", name, err)
                result["errors"].append({"name": name, "error": err})
        result["count"] = len(result["removed"])
        return result

    @classmethod
    def _service_exists(cls, service_name: str) -> bool:
        unit = service_name if service_name.endswith(".service") else f"{service_name}.service"
        for root in (Path("/etc/systemd/system"), Path("/usr/lib/systemd/system"), Path("/lib/systemd/system")):
            if (root / unit).exists():
                return True

        res = run_cmd(["systemctl", "list-unit-files", unit], timeout=15)
        return res["success"]

    @classmethod
    def _service_restart_if_exists(cls, service_name: str, timeout: int = 30, no_block: bool = False) -> tuple[bool, str]:
        if not cls._service_exists(service_name):
            return True, "service_not_installed"

        cmd = ["sudo", "systemctl", "restart"]
        if no_block:
            cmd.append("--no-block")
        cmd.append(service_name)

        res = run_cmd(cmd, timeout=timeout)
        if not res["success"]:
            return False, res.get("error", f"{service_name} restart failed")

        if no_block:
            return True, ""

        active = run_cmd(["systemctl", "is-active", service_name], timeout=15)
        if active["success"] and active.get("stdout", "").strip() == "active":
            return True, ""

        return False, f"{service_name} is not active after restart"

    @classmethod
    def _service_reload_if_exists(cls, service_name: str, timeout: int = 30) -> tuple[bool, str]:
        if not cls._service_exists(service_name):
            return True, "service_not_installed"

        res = run_cmd(["sudo", "systemctl", "reload", service_name], timeout=timeout)
        if not res["success"]:
            return False, res.get("error", f"{service_name} reload failed")

        return True, ""

    @classmethod
    def _component_name_from_meta(cls, component_meta: dict) -> str:
        rel = component_meta.get("file", "")
        if "/" in rel:
            return rel.split("/", 1)[0]
        return "component"

    @classmethod
    def _find_app_payload_root(cls, extracted_root: Path) -> Path | None:
        exact = extracted_root / "asguard" / "asguard"
        if exact.exists() and (exact / "manage.py").exists():
            return exact

        candidates = []
        for p in extracted_root.rglob("manage.py"):
            parent = p.parent
            if (parent / "asguard").exists() or (parent / "backend").exists():
                candidates.append(parent)

        if candidates:
            candidates.sort(key=lambda x: len(x.parts))
            return candidates[0]

        return None

    @classmethod
    def _wait_for_backend(cls, attempts: int = 10, delay_seconds: int = 2) -> tuple[bool, str]:
        last_error = "unknown backend error"

        for _ in range(attempts):
            result = run_cmd(["curl", "-fsS", "http://127.0.0.1:8000/swagger/"], timeout=20)
            if result["success"]:
                return True, ""

            last_error = result.get("error", result.get("stderr", "backend healthcheck failed"))
            run_cmd(["sleep", str(delay_seconds)], timeout=delay_seconds + 2)

        return False, last_error

    @classmethod
    def _restore_extract_only(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = cls._component_name_from_meta(component_meta)
        archive = backup_dir / component_meta["file"]

        # system_config's etc.tar.gz carries the SOURCE machine's /etc/fstab AND
        # its NetworkManager connection profiles (the IP). fstab is always excluded
        # (disk safety); the IP profiles are restored in a COMPLETE/DR clone but
        # kept in lighter modes — see _clone_excludes().
        excludes = cls._clone_excludes() if name == "system_config" else ()

        with Timer() as t:
            ok, msg = cls._extract_archive_to_root(archive, timeout=180,
                                                   excludes=excludes)
            if not ok:
                return ComponentResult.failed(name, msg)

        return ComponentResult(
            name=name,
            status="success",
            file=component_meta["file"],
            size_mb=archive.stat().st_size / (1024 ** 2),
            sha256=component_meta.get("sha256", ""),
            duration_s=t.elapsed,
        )

    @classmethod
    def _restore_application_skipped(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "application"
        with Timer() as t:
            return ComponentResult.skipped(
                name,
                "Application restore intentionally skipped to preserve current running code."
            )

    @classmethod
    def _restore_database(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "database"
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
            container_check = run_cmd(["docker", "ps", "--format", "{{.Names}}"], timeout=20)
            if not container_check["success"]:
                return ComponentResult.failed(name, "docker is not available")

            copy_res = run_cmd(
                ["docker", "cp", str(archive), f"{cls.DB_CONTAINER}:/tmp/postgres_restore.dump"],
                timeout=120,
            )
            if not copy_res["success"]:
                return ComponentResult.failed(name, copy_res.get("error", "docker cp failed"))

            # ATOMIC restore: --single-transaction makes the whole drop+recreate
            # one transaction, so an interruption (container restart, I/O stall)
            # rolls back to the previous DB instead of leaving it half-dropped /
            # empty. --if-exists avoids DROP errors aborting the transaction.
            restore_res = run_cmd(
                [
                    "docker", "exec", "-u", "postgres", cls.DB_CONTAINER,
                    "pg_restore", "-c", "--if-exists", "--single-transaction",
                    "-d", cls.DB_NAME, "/tmp/postgres_restore.dump",
                ],
                timeout=300,
            )
            if not restore_res["success"]:
                return ComponentResult.failed(name, restore_res.get("error", "pg_restore failed"))

            run_cmd(["docker", "exec", cls.DB_CONTAINER, "rm", "-f", "/tmp/postgres_restore.dump"], timeout=30)

        return ComponentResult(
            name=name,
            status="success",
            file=component_meta["file"],
            size_mb=archive.stat().st_size / (1024 ** 2),
            sha256=component_meta.get("sha256", ""),
            duration_s=t.elapsed,
        )

    @classmethod
    def _restore_firewall(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "firewall"
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
            with TemporaryDirectory(prefix="restore_firewall_") as tmp:
                tmp_path = Path(tmp)
                safe_extract(archive, tmp_path)

                staged_conf = tmp_path / "etc" / "nftables.conf"
                if not staged_conf.exists():
                    return ComponentResult.failed(name, "staged /etc/nftables.conf not found")

                validate = run_cmd(["sudo", "/usr/bin/nft", "-c", "-f", str(staged_conf)], timeout=30)
                if not validate["success"]:
                    return ComponentResult.failed(name, validate.get("error", "nft validation failed"))

                current_conf = Path("/etc/nftables.conf")
                backup_conf = Path("/tmp/nftables.conf.before_restore")
                if current_conf.exists():
                    shutil.copy2(current_conf, backup_conf)

                try:
                    ok, msg = cls._extract_archive_to_root(archive, timeout=60)
                    if not ok:
                        return ComponentResult.failed(name, msg)

                    # Flush the kernel ruleset BEFORE reloading. `nft -f`
                    # only ADDS, so without an explicit flush every restore
                    # would append the rules again — producing duplicate
                    # lines in the running ruleset.
                    run_cmd(["sudo", "/usr/bin/nft", "flush", "ruleset"], timeout=15)
                    apply_res = run_cmd(["sudo", "/usr/bin/nft", "-f", "/etc/nftables.conf"], timeout=30)
                    if not apply_res["success"]:
                        if backup_conf.exists():
                            shutil.copy2(backup_conf, current_conf)
                            run_cmd(["sudo", "/usr/bin/nft", "flush", "ruleset"], timeout=15)
                            run_cmd(["sudo", "/usr/bin/nft", "-f", "/etc/nftables.conf"], timeout=30)
                        return ComponentResult.failed(name, apply_res.get("error", "nft reload failed"))

                    sync_ok, sync_message = cls._restore_firewall_rules_db(tmp_path)
                    if not sync_ok:
                        return ComponentResult.failed(name, sync_message)
                finally:
                    if backup_conf.exists():
                        backup_conf.unlink(missing_ok=True)

        return ComponentResult(
            name=name,
            status="success",
            file=component_meta["file"],
            duration_s=t.elapsed,
            message="Firewall config restored and firewall rule database synchronized.",
        )

    @classmethod
    def _restore_component_db(cls, backup_dir: Path, component_name: str) -> tuple[bool, str]:
        """Replay a component's PostgreSQL rows from its per-component DB
        snapshot (component_db.json), written at backup time. Returns
        (ok, message). No snapshot / no DB models → (True, "") so legacy
        backups and files-only components are silently fine."""
        try:
            from backend.backup.component_db import (
                has_db_snapshot, restore_component_db, DB_SNAPSHOT_FILENAME,
            )
        except Exception as exc:
            return True, ""  # component_db unavailable — skip silently

        if not has_db_snapshot(component_name):
            return True, ""

        snap_file = backup_dir / component_name / DB_SNAPSHOT_FILENAME
        if not snap_file.exists():
            return True, "base de données non incluse (ancien format de backup)"

        try:
            snapshot = json.loads(snap_file.read_text(encoding="utf-8"))
        except Exception as exc:
            return False, f"lecture snapshot DB impossible : {exc}"

        return restore_component_db(component_name, snapshot)

    @classmethod
    def _restore_firewall_rules_db(cls, extracted_root: Path) -> tuple[bool, str]:
        # The archive may embed the DB snapshot under a temp-prefixed path
        # (e.g. tmp/backup_firewall_xxx/snapshot/var/backups/asguard/firewall_rules_db.json)
        # so we search recursively instead of relying on a fixed relative path.
        matches = list(extracted_root.rglob("firewall_rules_db.json"))
        if not matches:
            return True, "firewall db snapshot missing; nftables config restored only"
        snapshot_file = matches[0]

        try:
            payload = json.loads(snapshot_file.read_text(encoding="utf-8"))
        except Exception as exc:
            return False, f"Could not read firewall DB snapshot: {exc}"

        rows = payload.get("rules", [])
        if not isinstance(rows, list):
            return False, "Invalid firewall DB snapshot format"

        rules_to_create: list[Rule] = []
        missing_interfaces: list[str] = []

        for row in rows:
            interface = None
            interface_ifname = row.get("interface_ifname")
            interface_name = row.get("interface_name")

            if interface_ifname:
                interface = Interface.objects.filter(ifname=interface_ifname).first()
            if interface is None and interface_name:
                interface = Interface.objects.filter(name_interface=interface_name).first()

            if interface is None:
                missing_interfaces.append(interface_name or interface_ifname or "unknown-interface")
                continue

            rules_to_create.append(
                Rule(
                    rule=row.get("rule"),
                    rule_description=row.get("rule_description"),
                    rule_status=bool(row.get("rule_status", True)),
                    type_rule=row.get("type_rule"),
                    policy=row.get("policy"),
                    protocol=row.get("protocol"),
                    saddr=row.get("saddr"),
                    sport=row.get("sport"),
                    daddr=row.get("daddr"),
                    dport=row.get("dport"),
                    position=row.get("position") or 0,
                    interface=interface,
                )
            )

        if missing_interfaces:
            missing_list = ", ".join(sorted(set(missing_interfaces))[:5])
            return False, f"Firewall rules reference missing interfaces: {missing_list}"

        with transaction.atomic():
            Rule.objects.all().delete()
            if rules_to_create:
                Rule.objects.bulk_create(rules_to_create)

        return True, ""

    @classmethod
    def _restore_web(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "web"
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
            ok, msg = cls._extract_archive_to_root(archive, timeout=180)
            if not ok:
                return ComponentResult.failed(name, msg)

            test = run_cmd(["sudo", "nginx", "-t"], timeout=30)
            if not test["success"]:
                return ComponentResult.failed(name, test.get("error", "nginx config test failed"))

            ok_reload, reload_msg = cls._service_reload_if_exists("nginx", timeout=30)
            if not ok_reload:
                return ComponentResult.failed(name, reload_msg)

        return ComponentResult(name=name, status="success", file=component_meta["file"], duration_s=t.elapsed)

    @classmethod
    def _restore_vpn(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "vpn"
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
            ok, msg = cls._extract_archive_to_root(archive, timeout=180)
            if not ok:
                return ComponentResult.failed(name, msg)

            strongswan_exists = cls._service_exists("strongswan")
            openvpn_exists = cls._service_exists("openvpn-server@server")

            strongswan_ok, strongswan_msg = (True, "")
            openvpn_ok, openvpn_msg = (True, "")

            if strongswan_exists:
                strongswan_ok, strongswan_msg = cls._service_restart_if_exists("strongswan", timeout=30, no_block=True)

            if openvpn_exists:
                openvpn_ok, openvpn_msg = cls._service_restart_if_exists("openvpn-server@server", timeout=30, no_block=True)

            if strongswan_exists and openvpn_exists:
                if not strongswan_ok and not openvpn_ok:
                    return ComponentResult.failed(
                        name,
                        f"Both VPN restarts failed: strongswan={strongswan_msg} | openvpn={openvpn_msg}"
                    )
            elif strongswan_exists and not strongswan_ok:
                return ComponentResult.failed(name, strongswan_msg)
            elif openvpn_exists and not openvpn_ok:
                return ComponentResult.failed(name, openvpn_msg)

        return ComponentResult(name=name, status="success", file=component_meta["file"], duration_s=t.elapsed)

    @classmethod
    def _restore_ids(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "ids"
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
            ok, msg = cls._extract_archive_to_root(archive, timeout=180)
            if not ok:
                return ComponentResult.failed(name, msg)

            if cls._service_exists("suricata"):
                ok_restart, restart_msg = cls._service_restart_if_exists("suricata", timeout=30, no_block=True)
                if not ok_restart:
                    return ComponentResult.failed(name, restart_msg)

        return ComponentResult(name=name, status="success", file=component_meta["file"], duration_s=t.elapsed)

    @classmethod
    def _restore_proxy(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "proxy"
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
            ok, msg = cls._extract_archive_to_root(archive, timeout=120)
            if not ok:
                return ComponentResult.failed(name, msg)

            squid_conf = Path("/etc/squid/squid.conf")
            if squid_conf.exists():
                test_res = run_cmd(
                    ["sudo", "/usr/sbin/squid", "-k", "parse", "-f", str(squid_conf)],
                    timeout=30
                )
                if not test_res["success"]:
                    return ComponentResult.failed(name, test_res.get("error", "squid config validation failed"))

            if cls._service_exists("squid"):
                ok_restart, restart_msg = cls._service_restart_if_exists("squid", timeout=90, no_block=True)
                if not ok_restart:
                    return ComponentResult.failed(name, restart_msg)

        return ComponentResult(name=name, status="success", file=component_meta["file"], duration_s=t.elapsed)

    @classmethod
    def _restore_network(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "network"
        archive = backup_dir / component_meta["file"]
        clone = (cls.RESTORE_MODE == "complete")

        with Timer() as t:
            # COMPLETE / DR clone → restore the NetworkManager profiles too (the
            # source IP), so the rebuilt VM is identical. Lighter modes keep the
            # target's current IP to avoid disrupting a live appliance.
            excludes = () if clone else cls._NETWORK_IDENTITY_EXCLUDES
            ok, msg = cls._extract_archive_to_root(archive, timeout=120,
                                                   excludes=excludes)
            if not ok:
                return ComponentResult.failed(name, msg)

            restored_ips: list[str] = []
            ui_net_restored: list[str] = []
            applied = "preserved"
            if clone:
                # tar --overwrite brings the backup's profiles IN, but never
                # DELETES profiles that exist here yet were absent from the backup
                # (e.g. a VLAN/connection created after the snapshot). A true clone
                # must not keep those stray interfaces — prune them so the restored
                # box matches the backup exactly.
                cls._prune_stale_nm_profiles(archive)
                restored_ips = cls._restored_nm_ips()
                # Re-read the profile files into NetworkManager WITHOUT bouncing
                # interfaces (so we never drop the live session mid-restore). The
                # new IP fully applies on the next reboot — which the UI recommends.
                applied = "reloaded"
                reload_res = run_cmd(["sudo", "nmcli", "connection", "reload"], timeout=30)
                if not reload_res["success"]:
                    # Fall back to a NM service reload; still best-effort.
                    run_cmd(["sudo", "systemctl", "reload-or-restart", "--no-block", "NetworkManager"], timeout=15)
            else:
                # UI-SAFE: the physical NIC identity (ens33/ens34 IP) stays
                # excluded so the live session never drops — BUT the UI-managed
                # VLAN/VXLAN objects ARE restored (additive, never touch the
                # physical NIC). So a VLAN/VXLAN deleted since the backup comes
                # back on a UI-safe restore, matching what the operator sees in
                # the interface.
                ui_net_restored = cls._restore_ui_vlan_vxlan_profiles(archive)

        if clone:
            ip_txt = ", ".join(restored_ips) if restored_ips else "DHCP/auto"
            message = (f"Identité réseau restaurée (clone) — IP cible: {ip_txt}. "
                       f"Redémarrage recommandé pour appliquer entièrement.")
        elif ui_net_restored:
            message = ("Config réseau restaurée — identité IP préservée ; "
                       f"VLAN/VXLAN rétablis : {', '.join(ui_net_restored)}.")
        else:
            message = "Network config restored (host IP identity preserved)."

        if clone:
            # Surface where to reconnect after a clone restore (read at result level).
            cls._LAST_CLONE_NETWORK = {"restored_ips": restored_ips, "applied": applied}

        return ComponentResult(
            name=name,
            status="success",
            file=component_meta["file"],
            size_mb=archive.stat().st_size / (1024 ** 2),
            sha256=component_meta.get("sha256", ""),
            duration_s=t.elapsed,
            message=message,
        )

    @classmethod
    def _restore_ui_vlan_vxlan_profiles(cls, archive: Path) -> list[str]:
        """UI-SAFE restore only. Bring back ONLY the VLAN/VXLAN NetworkManager
        profiles from the network archive — the UI-managed, additive network
        objects — and never the physical NIC profiles (ens33/ens34) that carry
        the host IP. So a VLAN/VXLAN deleted since the backup is restored on a
        UI-safe restore, while the live session's IP is never touched.

        Returns the list of connection names restored (for the result message).
        """
        restored: list[str] = []
        listing = run_cmd(["sudo", "/usr/bin/tar", "tzf", str(archive)], timeout=60)
        if not listing["success"]:
            return restored
        profiles = [
            ln for ln in listing["stdout"].splitlines()
            if "NetworkManager/system-connections/" in ln
            and ln.rstrip("/").endswith(".nmconnection")
        ]
        if not profiles:
            return restored

        tmp = Path("/tmp/.asguard_nm_ui")
        run_cmd(["sudo", "/usr/bin/rm", "-rf", str(tmp)], timeout=15)
        run_cmd(["sudo", "/usr/bin/mkdir", "-p", str(tmp)], timeout=15)
        # Extract only the profile members into tmp (they keep their archive path).
        if not run_cmd(["sudo", "/usr/bin/tar", "-xzf", str(archive), "-C", str(tmp), *profiles],
                       timeout=90)["success"]:
            run_cmd(["sudo", "/usr/bin/rm", "-rf", str(tmp)], timeout=15)
            return restored

        nm_dir = Path("/etc/NetworkManager/system-connections")
        for rel in profiles:
            src = tmp / rel
            content = run_cmd(["sudo", "/usr/bin/cat", str(src)], timeout=15)
            if not content["success"]:
                continue
            body = content["stdout"]
            # Keep ONLY VLAN/VXLAN profiles — physical NIC profiles are skipped
            # so the host IP identity is never re-applied on a live box.
            if "[vlan]" not in body and "[vxlan]" not in body:
                continue
            dst = nm_dir / Path(rel).name
            if not run_cmd(["sudo", "/usr/bin/cp", str(src), str(dst)], timeout=15)["success"]:
                continue
            run_cmd(["sudo", "/usr/bin/chmod", "600", str(dst)], timeout=15)
            restored.append(Path(rel).name[:-len(".nmconnection")])

        if restored:
            # Re-read profiles into NM, then activate each VLAN/VXLAN. Bringing a
            # VLAN up never disturbs its parent NIC's own address.
            run_cmd(["sudo", "nmcli", "connection", "reload"], timeout=30)
            for conn in restored:
                run_cmd(["sudo", "nmcli", "connection", "up", conn], timeout=30)
        run_cmd(["sudo", "/usr/bin/rm", "-rf", str(tmp)], timeout=15)
        return restored

    @classmethod
    def _prune_stale_nm_profiles(cls, archive: Path) -> None:
        """COMPLETE restore only. Remove live NetworkManager *.nmconnection
        profiles that the backup did NOT contain, so a restored clone keeps no
        stray VLANs/connections created after the snapshot.

        SAFETY: if the archive carries no profiles at all (e.g. an older backup
        made before profiles were captured — empty system-connections/), we prune
        NOTHING. Wiping the live identity in that case could lock the operator
        out. Pruning therefore only kicks in for backups that actually hold the
        network identity."""
        nm_dir = Path("/etc/NetworkManager/system-connections")
        if not nm_dir.exists():
            return
        listing = run_cmd(["sudo", "/usr/bin/tar", "tzf", str(archive)], timeout=60)
        if not listing["success"]:
            return  # can't read the archive → never risk deleting live profiles
        archived = {
            Path(line).name
            for line in listing["stdout"].splitlines()
            if "NetworkManager/system-connections/" in line
            and line.rstrip("/").endswith(".nmconnection")
        }
        if not archived:
            return  # backup has no profiles → preserve live identity (safety)
        for prof in nm_dir.glob("*.nmconnection"):
            if prof.name not in archived:
                run_cmd(["sudo", "rm", "-f", str(prof)], timeout=15)
                logger.info("Restore clone: pruned stale NM profile %s", prof.name)

    @classmethod
    def _restored_nm_ips(cls) -> list[str]:
        """Parse static IPs from the NetworkManager profiles that were just
        restored into /etc/NetworkManager/system-connections. Best-effort; used
        only to tell the operator where to reconnect after a clone restore. The
        detached complete restore runs as root, so it can read the 0600 files."""
        ips: list[str] = []
        nm_dir = Path("/etc/NetworkManager/system-connections")
        try:
            for f in nm_dir.glob("*.nmconnection"):
                try:
                    for line in f.read_text(errors="ignore").splitlines():
                        line = line.strip()
                        if line.startswith("address1="):
                            ip = line.split("=", 1)[1].split("/")[0].strip()
                            if ip and ip not in ips:
                                ips.append(ip)
                except Exception:
                    continue
        except Exception:
            logger.exception("Could not parse restored NM IPs (non-fatal)")
        return ips

    @classmethod
    def _restore_security(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "security"
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
            ok, msg = cls._extract_archive_to_root(archive, timeout=120)
            if not ok:
                return ComponentResult.failed(name, msg)

            if cls._service_exists("fail2ban"):
                ok_restart, restart_msg = cls._service_restart_if_exists("fail2ban", timeout=30)
                if not ok_restart:
                    logger.warning("fail2ban restart failed: %s", restart_msg)

            svc = "sshd" if Path("/usr/lib/systemd/system/sshd.service").exists() else "ssh"
            reload_res = run_cmd(["sudo", "systemctl", "reload", svc], timeout=30)
            if not reload_res["success"]:
                return ComponentResult.failed(name, reload_res.get("error", f"{svc} reload failed"))

        return ComponentResult(name=name, status="success", file=component_meta["file"], duration_s=t.elapsed)

    @classmethod
    def _has_network(cls) -> bool:
        """Quick reachability probe — without repos we can't (re)install packages."""
        for host, port in (("8.8.8.8", 53), ("1.1.1.1", 53)):
            res = run_cmd(["bash", "-c",
                           f"timeout 4 bash -c 'cat < /dev/null > /dev/tcp/{host}/{port}' 2>/dev/null && echo ok"],
                          timeout=8)
            if res.get("success") and "ok" in (res.get("stdout") or ""):
                return True
        return False

    @classmethod
    def _installed_package_set(cls, is_pacman: bool) -> set:
        """Set of currently-installed package names on the target."""
        cmd = ["pacman", "-Qq"] if is_pacman else ["dpkg-query", "-W", "-f=${Package}\n"]
        res = run_cmd(cmd, timeout=60)
        if not res.get("success"):
            return set()
        return {l.strip() for l in (res.get("stdout") or "").splitlines() if l.strip()}

    @classmethod
    def _restore_packages(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        """Reproduce the backed-up package set on the target.

        On a COMPLETE (DR clone) restore we detect which packages from the backup
        are MISSING here and best-effort (re)install them so a rebuilt/cloned VM
        actually gets the operator's added packages. It is deliberately careful:
        only runs in complete mode, requires network (else reports the gap instead
        of guessing), and NEVER crashes the restore. Lighter modes just report the
        list. (A guaranteed byte-identical OS — exact versions, every file — needs
        a disk-image backup; this brings back the *installed package set*.)"""
        name = "packages"
        pkg_file = backup_dir / component_meta["file"]

        with Timer() as t:
            if not pkg_file.exists():
                return ComponentResult.skipped(name, "Aucune liste de paquets dans la sauvegarde.")

            is_pacman = "pacman" in pkg_file.name or Path("/usr/bin/pacman").exists()
            is_dpkg = "dpkg" in pkg_file.name or Path("/usr/bin/apt-get").exists()

            pkgs = [l.split()[0].strip()
                    for l in pkg_file.read_text(encoding="utf-8", errors="ignore").splitlines()
                    if l.strip() and not l.startswith("#") and l.split()[0] != "install"]
            # dpkg --set-selections lines look like "pkg\tinstall" — keep the name.
            pkgs = [p for p in pkgs if p and p not in ("install", "deinstall")]
            if not pkgs:
                return ComponentResult.skipped(name, "Liste de paquets vide.")

            # Lighter restores don't touch the OS package set — just record it.
            if cls.RESTORE_MODE != "complete":
                return ComponentResult.skipped(
                    name, f"{len(pkgs)} paquets listés (réinstallation auto uniquement en restauration complète).")

            installed = cls._installed_package_set(is_pacman)
            missing = [p for p in pkgs if p not in installed] if installed else pkgs

            if not missing:
                return ComponentResult(
                    name=name, status="success", file=component_meta["file"], duration_s=t.elapsed,
                    message=f"{len(pkgs)} paquets de la sauvegarde déjà présents sur la cible.")

            if not cls._has_network():
                return ComponentResult.failed(
                    name,
                    f"{len(missing)} paquet(s) manquant(s) mais aucun réseau pour les installer "
                    f"(restauration des configs OK). Manquants: "
                    f"{', '.join(missing[:8])}{'…' if len(missing) > 8 else ''}.")

            if is_pacman:
                install_res = run_cmd(["sudo", "pacman", "-S", "--needed", "--noconfirm"] + missing, timeout=1200)
            else:
                run_cmd(["sudo", "apt-get", "update"], timeout=240)
                install_res = run_cmd(["sudo", "apt-get", "install", "-y"] + missing, timeout=1200)

            still_missing = [p for p in missing if p not in cls._installed_package_set(is_pacman)]
            done = len(missing) - len(still_missing)
            if not still_missing:
                return ComponentResult(
                    name=name, status="success", file=component_meta["file"], duration_s=t.elapsed,
                    message=f"{done} paquet(s) réinstallés depuis la sauvegarde.")
            return ComponentResult.failed(
                name,
                f"{done}/{len(missing)} paquet(s) réinstallés ; échec sur "
                f"{', '.join(still_missing[:8])}{'…' if len(still_missing) > 8 else ''}. "
                f"{(install_res.get('error') or '')[:150]}")

    @classmethod
    def _restore_users_groups(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "users_groups"
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
            ok, msg = cls._extract_archive_to_root(archive, timeout=120)
            if not ok:
                return ComponentResult.failed(name, msg)

        return ComponentResult(name=name, status="success", file=component_meta["file"], duration_s=t.elapsed)

    @classmethod
    def _restore_docker_state(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "docker_state"
        archive = backup_dir / component_meta["file"]
        with Timer() as t:
            return ComponentResult.skipped(
                name,
                f"Docker state restore not auto-applied from snapshot file: {archive.name}"
            )

    @classmethod
    def _restore_systemd_services(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "systemd_services"
        snapshot_file = backup_dir / component_meta["file"]

        with Timer() as t:
            if not snapshot_file.exists():
                return ComponentResult.failed(name, f"systemd services file not found: {snapshot_file.name}")

        # 1) Si une archive des unités custom existe, on la restaure
            units_archive = backup_dir / "systemd_services" / "systemd_units.tar.gz"
            if not units_archive.exists():
                units_archive = backup_dir / "systemd_services" / "custom_units.tar.gz"
            if units_archive.exists():
                ok, msg = cls._extract_archive_to_root(units_archive, timeout=120)
                if not ok:
                    return ComponentResult.failed(name, f"failed to restore systemd units archive: {msg}")

        # 2) daemon-reload
            reload_res = run_cmd(["sudo", "systemctl", "daemon-reload"], timeout=30)
            if not reload_res["success"]:
                return ComponentResult.failed(name, reload_res.get("error", "systemctl daemon-reload failed"))

        # 3) Lecture de enabled_services.txt
            try:
                lines = snapshot_file.read_text(encoding="utf-8", errors="ignore").splitlines()
            except Exception as e:
                return ComponentResult.failed(name, f"failed to read services snapshot: {e}")

            services = []
            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

            # garde seulement la première colonne si format tabulaire
                svc = line.split()[0]

                if not svc.endswith(".service"):
                    continue

                services.append(svc)

            if not services:
                return ComponentResult.skipped(name, "No services found in snapshot file")

            existing_services = []
            for svc in services:
                if cls._service_exists(svc):
                    existing_services.append(svc)

            skipped_count = len(services) - len(existing_services)
            if not existing_services:
                return ComponentResult.skipped(name, "No services from snapshot exist on this system")

            enable_res = run_cmd(
                ["sudo", "systemctl", "enable", "--no-reload", *existing_services],
                timeout=max(60, len(existing_services) * 10),
            )
            if not enable_res["success"]:
                return ComponentResult.failed(
                    name,
                    enable_res.get("error", enable_res.get("stderr", "systemctl enable failed")),
                )

            reload_res = run_cmd(["sudo", "systemctl", "daemon-reload"], timeout=60)
            if not reload_res["success"]:
                return ComponentResult.failed(name, reload_res.get("error", "systemctl daemon-reload failed after enable"))

            enabled_count = len(existing_services)
            message = f"{enabled_count} service(s) enabled from snapshot; {skipped_count} skipped."

            return ComponentResult(
                name=name,
                status="success",
                file=component_meta["file"],
                duration_s=t.elapsed,
                message=message,
            )
        
    @classmethod
    def _restore_logs(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "logs"
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
            if cls.RESTORE_MODE == "safe":
                target_dir = Path("/var/backups/asguard/restored_logs") / backup_dir.name
                target_dir.mkdir(parents=True, exist_ok=True)

                res = run_cmd(
                    ["sudo", "/usr/bin/tar", "-xzf", str(archive), "-C", str(target_dir)],
                    timeout=180,
                )
                if not res["success"]:
                    return ComponentResult.failed(name, res.get("error", "logs restore failed"))

                return ComponentResult(
                    name=name,
                    status="success",
                    file=component_meta["file"],
                    duration_s=t.elapsed,
                    message=f"Logs restored safely to {target_dir}",
                )

            ok, msg = cls._extract_archive_to_root(archive, timeout=180)
            if not ok:
                return ComponentResult.failed(name, msg)

        return ComponentResult(
            name=name,
            status="success",
            file=component_meta["file"],
            duration_s=t.elapsed,
            message="Logs restored to original system locations.",
        )

    @classmethod
    def _restore_vm_snapshot(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "vm_snapshot"
        snapshot_file = backup_dir / component_meta["file"]
        with Timer() as t:
            return ComponentResult.skipped(
                name,
                f"VM snapshot restore not supported automatically from metadata file: {snapshot_file.name}"
            )

    @classmethod
    def _restore_routing(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "routing"
        summary = backup_dir / component_meta["file"]

        with Timer() as t:
            try:
                payload = json.loads(summary.read_text(encoding="utf-8"))
            except Exception as exc:
                return ComponentResult.failed(name, f"Could not read routing summary: {exc}")

            backend_meta = payload.get("backend_status", {})
            if backend_meta.get("status") == "success" and backend_meta.get("file"):
                backend_archive = backup_dir / backend_meta["file"]
                if backend_archive.exists():
                    ok, msg = cls._extract_archive_to_root(backend_archive, timeout=120)
                    if not ok:
                        return ComponentResult.failed(name, msg)

        return ComponentResult(
            name=name,
            status="success",
            file=component_meta["file"],
            duration_s=t.elapsed,
            message="Routing backend restored; route dump preserved for audit.",
        )

    @classmethod
    def _restore_nat(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "nat"
        summary = backup_dir / component_meta["file"]

        with Timer() as t:
            try:
                payload = json.loads(summary.read_text(encoding="utf-8"))
            except Exception as exc:
                return ComponentResult.failed(name, f"Could not read nat summary: {exc}")

            backend_meta = payload.get("backend_status", {})
            if backend_meta.get("status") == "success" and backend_meta.get("file"):
                backend_archive = backup_dir / backend_meta["file"]
                if backend_archive.exists():
                    ok, msg = cls._extract_archive_to_root(backend_archive, timeout=120)
                    if not ok:
                        return ComponentResult.failed(name, msg)

            if Path("/etc/nftables.conf").exists():
                validate = run_cmd(["sudo", "nft", "-c", "-f", "/etc/nftables.conf"], timeout=30)
                if not validate["success"]:
                    return ComponentResult.failed(name, validate.get("error", "nft validation failed after NAT restore"))

                # Flush before reload — `nft -f` only adds, so without this
                # every NAT restore would duplicate the running rules.
                run_cmd(["sudo", "nft", "flush", "ruleset"], timeout=15)
                apply_res = run_cmd(["sudo", "nft", "-f", "/etc/nftables.conf"], timeout=30)
                if not apply_res["success"]:
                    return ComponentResult.failed(name, apply_res.get("error", "nft reload failed after NAT restore"))

        return ComponentResult(
            name=name,
            status="success",
            file=component_meta["file"],
            duration_s=t.elapsed,
            message="NAT backend restored; nftables re-applied from live firewall config.",
        )

    @classmethod
    def _restore_waf(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "waf"
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
            ok, msg = cls._extract_archive_to_root(archive, timeout=180)
            if not ok:
                return ComponentResult.failed(name, msg)

            test = run_cmd(["sudo", "nginx", "-t"], timeout=30)
            if not test["success"]:
                return ComponentResult.failed(name, test.get("error", "nginx test failed after WAF restore"))

            ok_reload, reload_msg = cls._service_reload_if_exists("nginx", timeout=30)
            if not ok_reload:
                return ComponentResult.failed(name, reload_msg)

        return ComponentResult(name=name, status="success", file=component_meta["file"], duration_s=t.elapsed)

    @classmethod
    def _restore_dhcp(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "dhcp"
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
            ok, msg = cls._extract_archive_to_root(archive, timeout=120)
            if not ok:
                return ComponentResult.failed(name, msg)

            candidates = ["dhcpd", "isc-dhcp-server"]
            restarted = False

            for svc in candidates:
                if cls._service_exists(svc):
                    ok_restart, _ = cls._service_restart_if_exists(svc, timeout=30)
                    if ok_restart:
                        restarted = True
                        break

        return ComponentResult(
            name=name,
            status="success",
            file=component_meta["file"],
            duration_s=t.elapsed,
            message="DHCP config restored." + (" Service restarted." if restarted else " No DHCP service restart applied."),
        )

    @classmethod
    def _restore_application(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "application"
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
            with TemporaryDirectory(prefix="restore_app_") as tmp:
                tmp_path = Path(tmp)

                logger.info("[APP] Extracting application archive: %s", archive.name)
                safe_extract(archive, tmp_path)

                extracted_root = cls._find_app_payload_root(tmp_path)
                if not extracted_root:
                    return ComponentResult.failed(
                        name,
                        "Could not locate restored application root in extracted archive",
                    )

                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                app_parent = cls.APP_ROOT.parent
                staged_dir = app_parent / f".asguard_restored_{ts}"
                previous_dir = app_parent / f".asguard_previous_{ts}"

                if staged_dir.exists():
                    shutil.rmtree(staged_dir, ignore_errors=True)
                if previous_dir.exists():
                    shutil.rmtree(previous_dir, ignore_errors=True)

                shutil.copytree(extracted_root, staged_dir, symlinks=True)

                # Under a heavy restore (service-restart + systemd/D-Bus storm) a
                # 30s `systemctl stop uvicorn` times out and wrongly fails the whole
                # `application` component. Reset stale state, give it 120s, and retry
                # once so a busy box tolerates it.
                run_cmd(["systemctl", "reset-failed", "uvicorn"], timeout=15)
                stop_res = run_cmd(["systemctl", "stop", "uvicorn"], timeout=120)
                if not stop_res["success"]:
                    run_cmd(["systemctl", "reset-failed", "uvicorn"], timeout=15)
                    stop_res = run_cmd(["systemctl", "stop", "uvicorn"], timeout=120)
                if not stop_res["success"]:
                    shutil.rmtree(staged_dir, ignore_errors=True)
                    return ComponentResult.failed(name, stop_res.get("error", "failed to stop uvicorn"))

                swapped = False
                try:
                    os.chdir("/")

                    if not cls.APP_ROOT.exists():
                        run_cmd(["systemctl", "start", "uvicorn"], timeout=120)
                        shutil.rmtree(staged_dir, ignore_errors=True)
                        return ComponentResult.failed(name, f"live application root not found: {cls.APP_ROOT}")

                    os.rename(cls.APP_ROOT, previous_dir)
                    os.rename(staged_dir, cls.APP_ROOT)
                    swapped = True

                    start_res = run_cmd(["systemctl", "start", "uvicorn"], timeout=120)
                    if not start_res["success"]:
                        raise RuntimeError(start_res.get("error", "failed to start uvicorn after application restore"))

                    if cls._service_exists("nginx"):
                        run_cmd(["systemctl", "reload", "nginx"], timeout=30)

                    ok, msg = cls._wait_for_backend(attempts=10, delay_seconds=2)
                    if not ok:
                        raise RuntimeError(f"backend healthcheck failed after app restore: {msg}")

                except Exception as e:
                    logger.exception("[APP] Application swap/start failed: %s", e)

                    try:
                        run_cmd(["systemctl", "stop", "uvicorn"], timeout=120)
                    except Exception:
                        pass

                    try:
                        if cls.APP_ROOT.exists():
                            shutil.rmtree(cls.APP_ROOT, ignore_errors=True)
                    except Exception:
                        logger.exception("[APP] Failed to clean broken APP_ROOT during rollback")

                    try:
                        if previous_dir.exists():
                            os.rename(previous_dir, cls.APP_ROOT)
                    except Exception:
                        logger.exception("[APP] Failed to rollback previous app directory")

                    rollback_start = run_cmd(["systemctl", "start", "uvicorn"], timeout=120)
                    if not rollback_start["success"]:
                        logger.exception("[APP] Failed to restart uvicorn after rollback")

                    return ComponentResult.failed(name, f"application restore failed with rollback: {e}")

                if swapped and previous_dir.exists():
                    logger.info("[APP] Previous application kept at %s", previous_dir)

                # Backups EXCLUDE node_modules (huge), so the swapped-in app dir
                # has none — which breaks `yarn build` and any node tooling after
                # every restore. Re-point a symlink to the stable, never-swapped
                # /asguard/node_modules so node_modules survives EVERY restore.
                cls._ensure_node_modules_symlink()

        return ComponentResult(
            name=name,
            status="success",
            file=component_meta["file"],
            size_mb=archive.stat().st_size / (1024 ** 2),
            sha256=component_meta.get("sha256", ""),
            duration_s=t.elapsed,
            message="Application restored and uvicorn restarted automatically.",
        )

    _STABLE_NODE_MODULES = Path("/asguard/node_modules")

    @classmethod
    def _ensure_node_modules_symlink(cls) -> None:
        """Guarantee <app>/node_modules resolves to the stable external copy after
        an app swap. Non-fatal — the UI runs from prebuilt static/ assets, so a
        missing stable dir only affects rebuilding, not serving."""
        link = cls.APP_ROOT / "node_modules"
        try:
            if link.is_symlink():
                # Drop a dangling or wrong-target symlink so we can recreate it.
                try:
                    if not link.exists() or link.resolve() != cls._STABLE_NODE_MODULES.resolve():
                        link.unlink()
                except Exception:
                    link.unlink()
            if link.exists():
                return  # valid symlink or a real node_modules dir already present
            if cls._STABLE_NODE_MODULES.exists():
                os.symlink(cls._STABLE_NODE_MODULES, link)
                logger.info("[APP] node_modules symlink recreated -> %s", cls._STABLE_NODE_MODULES)
            else:
                logger.warning("[APP] stable node_modules %s missing; build will need `yarn install`",
                               cls._STABLE_NODE_MODULES)
        except Exception:
            logger.exception("[APP] node_modules symlink recreation failed (non-fatal)")
