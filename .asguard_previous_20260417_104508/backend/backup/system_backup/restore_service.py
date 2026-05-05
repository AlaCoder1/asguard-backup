import json
import os
import logging
import shutil
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from .base import ComponentResult, run_cmd, safe_extract, Timer, compute_sha256

logger = logging.getLogger(__name__)


class RestoreService:
    BACKUP_ROOT = Path("/var/backups/asguard")
    DB_CONTAINER = "app-db-container"
    DB_NAME = "postgres"
    APP_ROOT = Path("/asguard/asguard")
    RESTORE_MODE = "safe"

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    @classmethod
    def restore_full_safe(cls, backup_id: str) -> dict:
        component_names = cls._ordered_component_names(include_application=False)
        return cls._restore_components(
            backup_id=backup_id,
            component_names=component_names,
            include_application=False,
            mode_label="full_safe",
        )

    @classmethod
    def restore_full_complete(cls, backup_id: str) -> dict:
        component_names = cls._ordered_component_names(include_application=True)
        return cls._restore_components(
            backup_id=backup_id,
            component_names=component_names,
            include_application=True,
            mode_label="full_complete",
        )

    @classmethod
    def restore_full(cls, backup_id: str) -> dict:
        return cls.restore_full_safe(backup_id)

    @classmethod
    def restore_component_safe(cls, backup_id: str, component_name: str) -> dict:
        return cls.restore_components_safe(backup_id, [component_name])

    @classmethod
    def restore_component_complete(cls, backup_id: str, component_name: str) -> dict:
        return cls.restore_components_complete(backup_id, [component_name])

    @classmethod
    def restore_components_safe(cls, backup_id: str, component_names: list[str]) -> dict:
        return cls._restore_components(
            backup_id=backup_id,
            component_names=component_names,
            include_application=False,
            mode_label="selected_components_safe",
        )

    @classmethod
    def restore_components_complete(cls, backup_id: str, component_names: list[str]) -> dict:
        return cls._restore_components(
            backup_id=backup_id,
            component_names=component_names,
            include_application=True,
            mode_label="selected_components_complete",
        )

    # -------------------------------------------------------------------------
    # Registry / ordering / validation
    # -------------------------------------------------------------------------

    @classmethod
    def _component_restore_registry(cls, include_application: bool) -> dict[str, callable]:
        runners = {
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

        if include_application:
            runners["application"] = cls._restore_application
        else:
            runners["application"] = cls._restore_application_skipped

        return runners

    @classmethod
    def _ordered_component_names(cls, include_application: bool) -> list[str]:
        ordered = [
            "users_groups",
            "packages",
            "system_config",
            "network",
            "certificates",
            "security",
            "firewall",
            "nat",
            "vpn",
            "web",
            "waf",
            "ids",
            "proxy",
            "scheduled_tasks",
            "database",
            "docker_state",
            "systemd_services",
            "logs",
            "vm_snapshot",
            "ztna",
            "ldap",
            "ipsec_detailed",
            "routing",
            "vlan",
            "vxlan",
            "sdwan",
            "dhcp",
            "gateway",
            "double_mask",
        ]

        if include_application:
            ordered.append("application")

        return ordered

    @classmethod
    def _validate_requested_components(
        cls,
        requested_components: list[str],
        include_application: bool,
    ) -> tuple[list[str], list[str]]:
        allowed = set(cls._component_restore_registry(include_application=include_application).keys())
        ordering = cls._ordered_component_names(include_application=include_application)

        seen = set()
        cleaned = []
        invalid = []

        for name in requested_components:
            n = (name or "").strip()
            if not n:
                continue
            if n in seen:
                continue
            seen.add(n)

            if n in allowed:
                cleaned.append(n)
            else:
                invalid.append(n)

        cleaned_set = set(cleaned)
        ordered_cleaned = [name for name in ordering if name in cleaned_set]
        return ordered_cleaned, invalid

    # -------------------------------------------------------------------------
    # Core restore orchestration
    # -------------------------------------------------------------------------

    @classmethod
    def _restore_components(
        cls,
        backup_id: str,
        component_names: list[str],
        include_application: bool,
        mode_label: str,
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

        requested_components, invalid_components = cls._validate_requested_components(
            component_names,
            include_application=include_application,
        )

        if not requested_components:
            return {
                "status": "error",
                "message": "No valid components requested for restore.",
                "invalid_components": invalid_components,
            }

        runners = cls._component_restore_registry(include_application=include_application)
        results = {}

        for component_name in requested_components:
            runner = runners[component_name]
            comp_meta = metadata.get("components", {}).get(component_name)

            if not comp_meta:
                results[component_name] = ComponentResult.skipped(
                    component_name, "No metadata for component"
                ).to_dict()
                continue

            if comp_meta.get("status") != "success":
                results[component_name] = ComponentResult.skipped(
                    component_name,
                    f"Component status is {comp_meta.get('status')}"
                ).to_dict()
                continue

            ok, msg = cls._verify_component_file(backup_dir, component_name, comp_meta)
            if not ok:
                results[component_name] = ComponentResult.failed(component_name, msg).to_dict()
                continue

            try:
                result = runner(backup_dir, comp_meta)
                results[component_name] = result.to_dict()
            except Exception as e:
                logger.exception("Restore failed for component %s", component_name)
                results[component_name] = ComponentResult.failed(component_name, str(e)).to_dict()

        success = sum(1 for r in results.values() if r["status"] == "success")
        failed = sum(1 for r in results.values() if r["status"] == "failed")
        skipped = sum(1 for r in results.values() if r["status"] == "skipped")

        global_status = "success" if failed == 0 else ("failed" if success == 0 else "partial_success")

        return {
            "status": global_status,
            "backup_id": backup_id,
            "mode": mode_label,
            "requested_components": requested_components,
            "invalid_components": invalid_components,
            "results": results,
            "summary": {
                "success": success,
                "failed": failed,
                "skipped": skipped,
            },
        }

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

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

    @classmethod
    def _extract_archive_to_root(cls, archive: Path, timeout: int = 180) -> tuple[bool, str]:
        res = run_cmd(["sudo", "/usr/bin/tar", "-xzf", str(archive), "-C", "/"], timeout=timeout)
        if not res["success"]:
            return False, res.get("error", res.get("stderr", "archive extraction failed"))
        return True, ""

    @classmethod
    def _service_exists(cls, service_name: str) -> bool:
        res = run_cmd(["systemctl", "list-unit-files", f"{service_name}.service"], timeout=15)
        return res["success"]

    @classmethod
    def _service_restart_if_exists(cls, service_name: str, timeout: int = 30) -> tuple[bool, str]:
        if not cls._service_exists(service_name):
            return True, "service_not_installed"

        res = run_cmd(["sudo", "systemctl", "restart", service_name], timeout=timeout)
        if not res["success"]:
            return False, res.get("error", f"{service_name} restart failed")

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

    # -------------------------------------------------------------------------
    # Generic restores
    # -------------------------------------------------------------------------

    @classmethod
    def _restore_extract_only(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = cls._component_name_from_meta(component_meta)
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
            ok, msg = cls._extract_archive_to_root(archive, timeout=180)
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

    # -------------------------------------------------------------------------
    # Component restores
    # -------------------------------------------------------------------------

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

                    apply_res = run_cmd(["sudo", "/usr/bin/nft", "-f", "/etc/nftables.conf"], timeout=30)
                    if not apply_res["success"]:
                        if backup_conf.exists():
                            shutil.copy2(backup_conf, current_conf)
                            run_cmd(["sudo", "/usr/bin/nft", "-f", "/etc/nftables.conf"], timeout=30)
                        return ComponentResult.failed(name, apply_res.get("error", "nft reload failed"))
                finally:
                    if backup_conf.exists():
                        backup_conf.unlink(missing_ok=True)

        return ComponentResult(name=name, status="success", file=component_meta["file"], duration_s=t.elapsed)

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
                strongswan_ok, strongswan_msg = cls._service_restart_if_exists("strongswan", timeout=30)

            if openvpn_exists:
                openvpn_ok, openvpn_msg = cls._service_restart_if_exists("openvpn-server@server", timeout=30)

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
                ok_restart, restart_msg = cls._service_restart_if_exists("suricata", timeout=30)
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
                ok_restart, restart_msg = cls._service_restart_if_exists("squid", timeout=90)
                if not ok_restart:
                    return ComponentResult.failed(name, restart_msg)

        return ComponentResult(name=name, status="success", file=component_meta["file"], duration_s=t.elapsed)

    @classmethod
    def _restore_network(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "network"
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
            ok, msg = cls._extract_archive_to_root(archive, timeout=120)
            if not ok:
                return ComponentResult.failed(name, msg)

        return ComponentResult(
            name=name,
            status="success",
            file=component_meta["file"],
            size_mb=archive.stat().st_size / (1024 ** 2),
            sha256=component_meta.get("sha256", ""),
            duration_s=t.elapsed,
            message="Network config restored on disk.",
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

            # supporte les deux noms d'archive
            custom_units_archive = backup_dir / "systemd_services" / "custom_units.tar.gz"
            legacy_units_archive = backup_dir / "systemd_services" / "systemd_units.tar.gz"

            units_archive = custom_units_archive if custom_units_archive.exists() else legacy_units_archive
            if units_archive.exists():
                ok, msg = cls._extract_archive_to_root(units_archive, timeout=120)
                if not ok:
                    return ComponentResult.failed(name, f"failed to restore systemd units archive: {msg}")

            reload_res = run_cmd(["sudo", "systemctl", "daemon-reload"], timeout=30)
            if not reload_res["success"]:
                return ComponentResult.failed(name, reload_res.get("error", "systemctl daemon-reload failed"))

            try:
                lines = snapshot_file.read_text(encoding="utf-8", errors="ignore").splitlines()
            except Exception as e:
                return ComponentResult.failed(name, f"failed to read services snapshot: {e}")

            services = []
            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                svc = line.split()[0]
                if not svc.endswith(".service"):
                    continue

                services.append(svc)

            if not services:
                return ComponentResult.skipped(name, "No services found in snapshot file")

            enabled_count = 0
            skipped_count = 0
            failed_services = []

            for svc in services:
                check = run_cmd(["systemctl", "list-unit-files", svc], timeout=15)
                if not check["success"]:
                    skipped_count += 1
                    continue

                enable_res = run_cmd(["sudo", "systemctl", "enable", svc], timeout=20)
                if enable_res["success"]:
                    enabled_count += 1
                else:
                    failed_services.append(f"{svc}: {enable_res.get('error', 'enable failed')}")

            if failed_services and enabled_count == 0:
                return ComponentResult.failed(
                    name,
                    "No service could be enabled. " + " | ".join(failed_services[:5])
                )

            message = f"{enabled_count} service(s) enabled from snapshot; {skipped_count} skipped."
            if failed_services:
                message += f" {len(failed_services)} enable operation(s) failed."

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