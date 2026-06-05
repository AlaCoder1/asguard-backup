import json
import os
import logging
import shutil
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from django.db import transaction

from backend.network.models import Interface
from backend.rules.models import Rule
from .base import ComponentResult, run_cmd, safe_extract, Timer, compute_sha256

logger = logging.getLogger(__name__)


class RestoreService:
    BACKUP_ROOT = Path("/var/backups/asguard")
    DB_CONTAINER = "app-db-container"
    DB_NAME = "postgres"
    APP_ROOT = Path("/asguard/asguard")
    RESTORE_MODE = "safe"
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

        backup_dir = cls.BACKUP_ROOT / backup_id
        if not backup_dir.exists():
            return {"status": "error", "message": f"Backup {backup_id} not found."}

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

        # Post-restore diff — capture the live DB state again and compare
        # against the pre-snapshot to give the operator a row-level
        # report (which rules vanished, which ZTNA identities reappeared,
        # which NAT entries changed). Whole block is best-effort: a
        # broken diff must never mask a successful restore.
        diff_payload: dict = {}
        try:
            from backend.backup.restore_diff import snapshot_db_state, diff_db_states
            post_snapshot = snapshot_db_state(all_runner_names)
            diff_payload = diff_db_states(pre_snapshot, post_snapshot)
        except Exception:
            logger.exception("Post-restore diff computation failed (non-fatal)")
            diff_payload = {"components": {}, "totals": {
                "added": 0, "removed": 0, "modified": 0, "changed_components": 0,
            }}

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
            "diff": diff_payload,
            "fstab_reconcile": fstab_reconcile,
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

    # Host-identity files that describe THIS physical machine, not the backed-up
    # one. Restoring them onto a different box breaks boot (fstab: wrong UUIDs /
    # missing LVM disk) or causes IP conflicts (the NetworkManager connection
    # profiles pin the LAN/WAN IP — two appliances would claim the same address).
    # We exclude them from extraction so the target keeps its own identity.
    _HOST_IDENTITY_EXCLUDES = (
        "etc/fstab", "./etc/fstab",
        "etc/NetworkManager/system-connections",
        "etc/NetworkManager/system-connections/*",
        "./etc/NetworkManager/system-connections",
        "./etc/NetworkManager/system-connections/*",
    )

    @classmethod
    def _extract_archive_to_root(cls, archive: Path, timeout: int = 180,
                                 preserve_identity: bool = False) -> tuple[bool, str]:
        cmd = ["sudo", "/usr/bin/tar", "--overwrite"]
        if preserve_identity:
            for pattern in cls._HOST_IDENTITY_EXCLUDES:
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
        try:
            res = run_cmd(["sudo", "-n", "vgs", "--noheadings", "asguard-vg"], timeout=15)
            return bool(res.get("success"))
        except Exception:
            return False

    @classmethod
    def _reconcile_fstab_native(cls) -> dict:
        """If the asguard LVM volume group is absent here (e.g. restored onto a
        VM without the 2nd disk), strip the LVM mount + bind-mount lines from
        /etc/fstab so the appliance boots and runs natively (configs in /etc,
        backups in /var/backups, postgres in its Docker volume) instead of
        hanging on missing devices. No-op when LVM IS present. Best-effort."""
        if cls._lvm_volume_group_present():
            return {"mode": "lvm", "changed": False}
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
        # its NetworkManager connection profiles (the IP). Never adopt those —
        # exclude them so the target keeps its own boot + network identity.
        preserve_identity = (name == "system_config")

        with Timer() as t:
            ok, msg = cls._extract_archive_to_root(archive, timeout=180,
                                                   preserve_identity=preserve_identity)
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

            restore_res = run_cmd(
                [
                    "docker", "exec", "-u", "postgres", cls.DB_CONTAINER,
                    "pg_restore", "-c", "-d", cls.DB_NAME, "/tmp/postgres_restore.dump",
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

        with Timer() as t:
            # Preserve the target's NetworkManager connection profiles (its IP
            # assignment) — restoring the backed-up machine's IP onto another
            # box causes IP conflicts. Other network config is still restored.
            ok, msg = cls._extract_archive_to_root(archive, timeout=120,
                                                   preserve_identity=True)
            if not ok:
                return ComponentResult.failed(name, msg)

        return ComponentResult(
            name=name,
            status="success",
            file=component_meta["file"],
            size_mb=archive.stat().st_size / (1024 ** 2),
            sha256=component_meta.get("sha256", ""),
            duration_s=t.elapsed,
            message="Network config restored (host IP identity preserved).",
        )

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
    def _restore_packages(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "packages"
        pkg_file = backup_dir / component_meta["file"]

        with Timer() as t:
            if pkg_file.name.endswith("pacman_packages.txt") or "pacman" in pkg_file.name:
                return ComponentResult.skipped(name, "Package restore not auto-applied for pacman yet")

            if pkg_file.name.endswith("dpkg_selections.txt"):
                r = run_cmd(
                    ["sudo", "dpkg", "--set-selections"],
                    input_data=pkg_file.read_text(encoding="utf-8"),
                    timeout=30,
                )
                if not r["success"]:
                    return ComponentResult.failed(name, r.get("error", "dpkg --set-selections failed"))

                return ComponentResult(name=name, status="success", file=component_meta["file"], duration_s=t.elapsed)

        return ComponentResult.skipped(name, "Unknown package format")

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

                stop_res = run_cmd(["systemctl", "stop", "uvicorn"], timeout=30)
                if not stop_res["success"]:
                    shutil.rmtree(staged_dir, ignore_errors=True)
                    return ComponentResult.failed(name, stop_res.get("error", "failed to stop uvicorn"))

                swapped = False
                try:
                    os.chdir("/")

                    if not cls.APP_ROOT.exists():
                        run_cmd(["systemctl", "start", "uvicorn"], timeout=30)
                        shutil.rmtree(staged_dir, ignore_errors=True)
                        return ComponentResult.failed(name, f"live application root not found: {cls.APP_ROOT}")

                    os.rename(cls.APP_ROOT, previous_dir)
                    os.rename(staged_dir, cls.APP_ROOT)
                    swapped = True

                    start_res = run_cmd(["systemctl", "start", "uvicorn"], timeout=30)
                    if not start_res["success"]:
                        raise RuntimeError(start_res.get("error", "failed to start uvicorn after application restore"))

                    if cls._service_exists("nginx"):
                        run_cmd(["systemctl", "reload", "nginx"], timeout=30)

                    ok, msg = cls._wait_for_backend(attempts=10, delay_seconds=2)
                    if not ok:
                        raise RuntimeError(f"backend healthcheck failed after app restore: {msg}")

                    # The app archive intentionally excludes node_modules — but
                    # the swap above leaves the new APP_ROOT without it, which
                    # breaks `yarn build` after a restore (encore missing). Carry
                    # the previous install over (same filesystem → instant rename).
                    try:
                        nm_new = cls.APP_ROOT / "node_modules"
                        nm_old = previous_dir / "node_modules"
                        if not nm_new.exists() and nm_old.is_dir():
                            os.rename(nm_old, nm_new)
                            logger.info("[APP] carried node_modules over from previous install")
                    except Exception:
                        logger.warning("[APP] could not carry node_modules over after restore", exc_info=True)

                except Exception as e:
                    logger.exception("[APP] Application swap/start failed: %s", e)

                    try:
                        run_cmd(["systemctl", "stop", "uvicorn"], timeout=30)
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

                    rollback_start = run_cmd(["systemctl", "start", "uvicorn"], timeout=30)
                    if not rollback_start["success"]:
                        logger.exception("[APP] Failed to restart uvicorn after rollback")

                    return ComponentResult.failed(name, f"application restore failed with rollback: {e}")

                if swapped and previous_dir.exists():
                    logger.info("[APP] Previous application kept at %s", previous_dir)

        return ComponentResult(
            name=name,
            status="success",
            file=component_meta["file"],
            size_mb=archive.stat().st_size / (1024 ** 2),
            sha256=component_meta.get("sha256", ""),
            duration_s=t.elapsed,
            message="Application restored and uvicorn restarted automatically.",
        )
