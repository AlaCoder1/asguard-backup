"""
full_backup_service.py — Full system backup for Asguard

Modes supportés :
-----------------
1) create_full_backup()
   -> Backup complet Disaster Recovery / bare-metal / clone VM

2) create_safe_backup()
   -> Backup SAFE destiné à l'interface admin
      (ne contient que les composants métier/configuration restaurables
       sans casser la plateforme elle-même)
"""

import json
import logging
import platform
import shutil
import socket
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from zoneinfo import ZoneInfo

from distro import name

from backend.rules.models import Rule
from .base import ComponentResult, Timer, compute_sha256, run_cmd

logger = logging.getLogger(__name__)

SCHEMA_VERSION = "4.1"
LOCAL_TZ = ZoneInfo("Africa/Tunis")

class FullBackupService:
    BACKUP_ROOT = Path("/var/backups/asguard")
    DB_CONTAINER = "app-db-container"
    DB_NAME = "postgres"
    APP_ROOT = Path("/asguard/asguard")
    BACKEND_ROOT = APP_ROOT / "backend"

    FULL_COMPONENTS = [
        "vm_snapshot",
        "database",
        "firewall",
        "vpn",
        "web",
        "ids",
        "proxy",
        "network",
        "security",
        "certificates",
        "application",
        "system_config",
        "scheduled_tasks",
        "packages",
        "systemd_services",
        "docker_state",
        "logs",
        "users_groups",
        "ztna",
        "ldap",
        "ipsec_detailed",
        "routing",
        "vlan",
        "vxlan",
        "sdwan",
        "waf",
        "nat",
        "dhcp",
        "gateway",
        "double_mask",
    ]

    SAFE_COMPONENTS = [
        "firewall",
        "vpn",
        "ids",
        "proxy",
        "network",
        "certificates",
        "routing",
        "nat",
        "dhcp",
        "waf",
        "ztna",
        "ipsec_detailed",
        "vlan",
        "vxlan",
        "sdwan",
        "gateway",
        "double_mask",
    ]

    @classmethod
    def create_full_backup(cls, progress_callback=None) -> dict:
        timestamp = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d_%H-%M-%S")
        backup_id = f"backup_{timestamp}"
        backup_dir = cls.BACKUP_ROOT / backup_id
        backup_dir.mkdir(parents=True, exist_ok=True)

        for sub in (
            "db",
            "firewall",
            "vpn",
            "web",
            "ids",
            "proxy",
            "network",
            "security",
            "certificates",
            "application",
            "system_config",
            "scheduled_tasks",
            "packages",
            "systemd_services",
            "docker_state",
            "logs",
            "users_groups",
            "vm_snapshot",
            # nouveaux composants UI/fonctionnels
            "ztna",
            "ldap",
            "ipsec_detailed",
            "routing",
            "vlan",
            "vxlan",
            "sdwan",
            "waf",
            "nat",
            "dhcp",
            "gateway",
            "double_mask",
        ):
            (backup_dir / sub).mkdir(parents=True, exist_ok=True)

        runners = [
            cls._backup_vm_snapshot,      # volontairement skipped
            cls._backup_database,
            cls._backup_firewall,
            cls._backup_vpn,
            cls._backup_web,
            cls._backup_ids,
            cls._backup_proxy,
            cls._backup_network,
            cls._backup_security,
            cls._backup_certificates,
            cls._backup_application,
            cls._backup_system_config,
            cls._backup_scheduled_tasks,
            cls._backup_packages,
            cls._backup_systemd_services,
            cls._backup_docker_state,
            cls._backup_logs,
            cls._backup_users_groups,
            # nouveaux modules alignés avec l’UI
            cls._backup_ztna,
            cls._backup_ldap,
            cls._backup_ipsec_detailed,
            cls._backup_routing,
            cls._backup_vlan,
            cls._backup_vxlan,
            cls._backup_sdwan,
            cls._backup_waf,
            cls._backup_nat,
            cls._backup_dhcp,
            cls._backup_gateway,
            cls._backup_double_mask,
        ]

        results = cls._run_backup_runners(backup_dir, runners, progress_callback=progress_callback)
        return cls._finalize_backup(
            backup_id=backup_id,
            backup_dir=backup_dir,
            results=results,
            backup_scope="bare_metal_disaster_recovery",
        )

    @classmethod
    def create_safe_backup(cls, progress_callback=None) -> dict:
        """
        Backup SAFE pour l'interface admin :
        composants métier/configuration restaurables depuis l'UI.
        """
        timestamp = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d_%H-%M-%S")        
        backup_id = f"backup_safe_{timestamp}"
        backup_dir = cls.BACKUP_ROOT / backup_id
        backup_dir.mkdir(parents=True, exist_ok=True)

        for sub in (
            "firewall",
            "vpn",
            "ids",
            "proxy",
            "network",
            "certificates",
            "routing",
            "nat",
            "dhcp",
            "waf",
            "ztna",
            "ipsec_detailed",
            "vlan",
            "vxlan",
            "sdwan",
            "gateway",
            "double_mask",
        ):
            (backup_dir / sub).mkdir(parents=True, exist_ok=True)

        runners = [
            cls._backup_firewall,
            cls._backup_vpn,
            cls._backup_ids,
            cls._backup_proxy,
            cls._backup_network,
            cls._backup_certificates,
            cls._backup_routing,
            cls._backup_nat,
            cls._backup_dhcp,
            cls._backup_waf,
            cls._backup_ztna,
            cls._backup_ipsec_detailed,
            cls._backup_vlan,
            cls._backup_vxlan,
            cls._backup_sdwan,
            cls._backup_gateway,
            cls._backup_double_mask,
        ]

        results = cls._run_backup_runners(backup_dir, runners, progress_callback=progress_callback)
        return cls._finalize_backup(
            backup_id=backup_id,
            backup_dir=backup_dir,
            results=results,
            backup_scope="safe_restore_ui",
        )

    @classmethod
    def create_custom_backup(cls, components: list[str]) -> dict:
        selected = cls._normalize_components(components)
        if not selected:
            return {
                "status": "error",
                "message": "No valid backup components selected.",
                "available_components": cls.available_components(),
            }

        timestamp = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d_%H-%M-%S")
        backup_id = f"backup_custom_{timestamp}"
        backup_dir = cls.BACKUP_ROOT / backup_id

        try:
            backup_dir.mkdir(parents=True, exist_ok=True)

            for component in selected:
                subdir = "db" if component == "database" else component
                (backup_dir / subdir).mkdir(parents=True, exist_ok=True)

            runners_map = cls._component_runners()
            runners = [runners_map[component] for component in selected]
            results = cls._run_backup_runners(backup_dir, runners)
            return cls._finalize_backup(
                backup_id=backup_id,
                backup_dir=backup_dir,
                results=results,
                backup_scope="selected_components",
                selected_components=selected,
            )
        except Exception as exc:
            logger.exception("Custom backup failed before finalization")
            if backup_dir.exists():
                shutil.rmtree(backup_dir, ignore_errors=True)
            return {
                "status": "error",
                "backup_id": backup_id,
                "message": f"Custom backup failed: {exc}",
                "selected_components": selected,
            }

    @classmethod
    def _run_backup_runners(cls, backup_dir: Path, runners: list, progress_callback=None) -> dict[str, ComponentResult]:
        results: dict[str, ComponentResult] = {}
        total = len(runners)
        components_progress: dict[str, str] = {}

        if progress_callback:
            try:
                progress_callback({
                    "components_progress": {},
                    "current_component": None,
                    "progress_pct": 0,
                    "done": 0,
                    "total": total,
                })
            except Exception:
                pass

        for idx, runner in enumerate(runners):
            result = runner(backup_dir)
            results[result.name] = result
            components_progress[result.name] = result.status

            if progress_callback:
                try:
                    progress_callback({
                        "components_progress": dict(components_progress),
                        "current_component": result.name,
                        "progress_pct": int((idx + 1) / total * 100) if total else 100,
                        "done": idx + 1,
                        "total": total,
                    })
                except Exception:
                    pass

            if result.status == "failed":
                logger.warning("Backup '%s' failed: %s", result.name, result.message)
            elif result.status == "skipped":
                logger.debug("Backup '%s' skipped: %s", result.name, result.message)

        return results

    @classmethod
    def _finalize_backup(
        cls,
        backup_id: str,
        backup_dir: Path,
        results: dict[str, ComponentResult],
        backup_scope: str,
        selected_components: list[str] | None = None,
    ) -> dict:
        metadata = cls._build_metadata(
            backup_id=backup_id,
            results=results,
            backup_scope=backup_scope,
            selected_components=selected_components,
        )

        with open(backup_dir / "backup_metadata.json", "w", encoding="utf-8") as fh:
            json.dump(metadata, fh, indent=2)

        counts = {"success": 0, "failed": 0, "skipped": 0}
        for r in results.values():
            counts[r.status] = counts.get(r.status, 0) + 1

        overall_status = cls._compute_overall_status(counts)

        return {
            "status": overall_status,
            "backup_id": backup_id,
            "backup_dir": str(backup_dir),
            "components": {name: r.to_dict() for name, r in results.items()},
            "summary": counts,
            "message": cls._build_summary_message(counts),
            "metadata": metadata,
        }

    @classmethod
    def _compute_overall_status(cls, counts: dict[str, int]) -> str:
        if counts.get("failed", 0) > 0:
            return "error"
        if counts.get("skipped", 0) > 0:
            return "partial"
        return "ok"

    @classmethod
    def _build_summary_message(cls, counts: dict[str, int]) -> str:
        success = counts.get("success", 0)
        failed = counts.get("failed", 0)
        skipped = counts.get("skipped", 0)

        if failed > 0:
            return f"Backup completed with errors: {success} succeeded, {failed} failed, {skipped} skipped."
        if skipped > 0:
            return f"Backup completed partially: {success} succeeded, {skipped} skipped."
        return f"Backup completed successfully: {success} component(s) saved."

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    @classmethod
    def available_components(cls) -> list[str]:
        return list(cls._component_runners().keys())

    @classmethod
    def _normalize_components(cls, components: list[str]) -> list[str]:
        available = cls._component_runners()
        selected: list[str] = []
        for component in components or []:
            name = str(component).strip()
            if name in available and name not in selected:
                selected.append(name)
        return selected

    @classmethod
    def _component_runners(cls) -> dict:
        return {
            "vm_snapshot": cls._backup_vm_snapshot,
            "database": cls._backup_database,
            "firewall": cls._backup_firewall,
            "vpn": cls._backup_vpn,
            "web": cls._backup_web,
            "ids": cls._backup_ids,
            "proxy": cls._backup_proxy,
            "network": cls._backup_network,
            "security": cls._backup_security,
            "certificates": cls._backup_certificates,
            "application": cls._backup_application,
            "system_config": cls._backup_system_config,
            "scheduled_tasks": cls._backup_scheduled_tasks,
            "packages": cls._backup_packages,
            "systemd_services": cls._backup_systemd_services,
            "docker_state": cls._backup_docker_state,
            "logs": cls._backup_logs,
            "users_groups": cls._backup_users_groups,
            "ztna": cls._backup_ztna,
            "ldap": cls._backup_ldap,
            "ipsec_detailed": cls._backup_ipsec_detailed,
            "routing": cls._backup_routing,
            "vlan": cls._backup_vlan,
            "vxlan": cls._backup_vxlan,
            "sdwan": cls._backup_sdwan,
            "waf": cls._backup_waf,
            "nat": cls._backup_nat,
            "dhcp": cls._backup_dhcp,
            "gateway": cls._backup_gateway,
            "double_mask": cls._backup_double_mask,
        }

    @classmethod
    def _build_component_result_from_file(
        cls,
        name: str,
        relative: str,
        dest: Path,
        elapsed: float,
        message: str = "",
    ) -> ComponentResult:
        if not dest.exists():
            return ComponentResult.failed(name, "Output file not created")

        return ComponentResult(
            name=name,
            status="success",
            file=relative,
            size_mb=dest.stat().st_size / (1024 ** 2),
            sha256=compute_sha256(dest) if dest.is_file() and dest.stat().st_size > 0 else "",
            duration_s=elapsed,
            message=message,
        )

    @classmethod
    def _backup_paths_as_tar(
        cls,
        *,
        backup_dir: Path,
        name: str,
        relative: str,
        paths: list[str],
        timeout: int = 120,
        message_if_empty: str = "No paths found",
    ) -> ComponentResult:
        dest = backup_dir / relative
        sources = [p for p in paths if Path(p).exists()]

        if not sources:
            return ComponentResult.skipped(name, message_if_empty)

        with Timer() as t:
            try:
                r = run_cmd(["tar", "--ignore-failed-read", "-czf", str(dest)] + sources, timeout=timeout)
                if not r["success"]:
                    return ComponentResult.failed(name, r.get("error", r.get("stderr", "tar failed")))
            except Exception as exc:
                return ComponentResult.failed(name, str(exc))

        return cls._build_component_result_from_file(name, relative, dest, t.elapsed)

    @classmethod
    def _write_text_component(
        cls,
        *,
        backup_dir: Path,
        name: str,
        relative: str,
        content: str,
        message: str = "",
    ) -> ComponentResult:
        dest = backup_dir / relative
        dest.parent.mkdir(parents=True, exist_ok=True)

        with Timer() as t:
            try:
                dest.write_text(content, encoding="utf-8")
            except Exception as exc:
                return ComponentResult.failed(name, str(exc))

        return cls._build_component_result_from_file(name, relative, dest, t.elapsed, message=message)

    @classmethod
    def _run_cmd_to_text_component(
        cls,
        *,
        backup_dir: Path,
        name: str,
        relative: str,
        cmd: list[str],
        timeout: int = 60,
        success_message: str = "",
    ) -> ComponentResult:
        with Timer() as t:
            try:
                r = run_cmd(cmd, timeout=timeout)
                if not r["success"]:
                    return ComponentResult.failed(name, r.get("error", r.get("stderr", "command failed")))

                dest = backup_dir / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(r.get("stdout", ""), encoding="utf-8")
            except Exception as exc:
                return ComponentResult.failed(name, str(exc))

        return cls._build_component_result_from_file(name, relative, dest, t.elapsed, message=success_message)

    @classmethod
    def _backup_backend_module_dir(
        cls,
        *,
        backup_dir: Path,
        name: str,
        module_dir_name: str,
        relative: str,
        extra_paths: list[str] | None = None,
        timeout: int = 120,
    ) -> ComponentResult:
        paths: list[str] = []
        module_dir = cls.BACKEND_ROOT / module_dir_name
        if module_dir.exists():
            paths.append(str(module_dir))
        if extra_paths:
            paths.extend(extra_paths)

        return cls._backup_paths_as_tar(
            backup_dir=backup_dir,
            name=name,
            relative=relative,
            paths=paths,
            timeout=timeout,
            message_if_empty=f"No backend/config paths found for {name}",
        )

    # -------------------------------------------------------------------------
    # Core components
    # -------------------------------------------------------------------------

    @classmethod
    def _backup_database(cls, backup_dir: Path) -> ComponentResult:
        name = "database"
        relative = "db/postgres.dump"
        dest = backup_dir / relative

        with Timer() as t:
            try:
                r = run_cmd(
                    [
                        "docker", "exec", "-u", "postgres", cls.DB_CONTAINER,
                        "pg_dump", "-F", "c", "-d", cls.DB_NAME,
                        "-f", "/tmp/pg_backup.dump",
                    ],
                    timeout=300,
                )
                if not r["success"]:
                    return ComponentResult.failed(name, r.get("error", r.get("stderr", "pg_dump failed")))

                r2 = run_cmd(
                    ["docker", "cp", f"{cls.DB_CONTAINER}:/tmp/pg_backup.dump", str(dest)],
                    timeout=60,
                )
                if not r2["success"]:
                    return ComponentResult.failed(name, r2.get("error", r2.get("stderr", "docker cp failed")))

                run_cmd(["docker", "exec", cls.DB_CONTAINER, "rm", "-f", "/tmp/pg_backup.dump"], timeout=30)

            except Exception as exc:
                return ComponentResult.failed(name, str(exc))

        return cls._build_component_result_from_file(name, relative, dest, t.elapsed)

    @classmethod
    def _backup_firewall(cls, backup_dir: Path) -> ComponentResult:
        name = "firewall"
        relative = "firewall/firewall_rules.tar.gz"
        dest = backup_dir / relative
        sources = [p for p in ["/etc/nftables.conf", "/etc/rules", "/etc/iptables"] if Path(p).exists()]

        with Timer() as t:
            try:
                with TemporaryDirectory(prefix="backup_firewall_") as tmp:
                    tmp_path = Path(tmp)
                    snapshot_root = tmp_path / "snapshot"
                    snapshot_root.mkdir(parents=True, exist_ok=True)

                    metadata_dir = snapshot_root / "var" / "backups" / "asguard"
                    metadata_dir.mkdir(parents=True, exist_ok=True)
                    firewall_rules_file = metadata_dir / "firewall_rules_db.json"

                    firewall_rows = []
                    for rule in Rule.objects.select_related("interface").order_by(
                        "interface__name_interface",
                        "type_rule",
                        "position",
                        "id",
                    ):
                        firewall_rows.append({
                            "rule": rule.rule,
                            "rule_description": rule.rule_description,
                            "rule_status": rule.rule_status,
                            "type_rule": rule.type_rule,
                            "policy": rule.policy,
                            "protocol": rule.protocol,
                            "saddr": rule.saddr,
                            "sport": rule.sport,
                            "daddr": rule.daddr,
                            "dport": rule.dport,
                            "position": rule.position,
                            "interface_ifname": getattr(rule.interface, "ifname", None),
                            "interface_name": getattr(rule.interface, "name_interface", None),
                        })

                    firewall_rules_file.write_text(
                        json.dumps({"rules": firewall_rows}, indent=2),
                        encoding="utf-8",
                    )

                    tar_sources = [str(snapshot_root)] + sources
                    r = run_cmd(
                        ["tar", "--ignore-failed-read", "-czf", str(dest)] + tar_sources,
                        timeout=60,
                    )
                    if not r["success"]:
                        return ComponentResult.failed(name, r.get("error", r.get("stderr", "tar failed")))
            except Exception as exc:
                return ComponentResult.failed(name, str(exc))

        return cls._build_component_result_from_file(
            name,
            relative,
            dest,
            t.elapsed,
            message="Firewall files and firewall DB rules snapshot saved.",
        )

    @classmethod
    def _backup_vpn(cls, backup_dir: Path) -> ComponentResult:
        return cls._backup_paths_as_tar(
            backup_dir=backup_dir,
            name="vpn",
            relative="vpn/vpn_configs.tar.gz",
            paths=[
                "/etc/openvpn",
                "/etc/strongswan.d",
                "/etc/swanctl",
                "/etc/ipsec.conf",
                "/etc/ipsec.d",
            ],
            timeout=120,
            message_if_empty="No VPN config found",
        )

    @classmethod
    def _backup_web(cls, backup_dir: Path) -> ComponentResult:
        return cls._backup_paths_as_tar(
            backup_dir=backup_dir,
            name="web",
            relative="web/nginx.tar.gz",
            paths=["/etc/nginx"],
            timeout=60,
            message_if_empty="/etc/nginx not found",
        )

    @classmethod
    def _backup_ids(cls, backup_dir: Path) -> ComponentResult:
        return cls._backup_paths_as_tar(
            backup_dir=backup_dir,
            name="ids",
            relative="ids/suricata.tar.gz",
            paths=["/etc/suricata", "/var/lib/suricata/rules"],
            timeout=180,
            message_if_empty="Suricata not installed",
        )

    @classmethod
    def _backup_proxy(cls, backup_dir: Path) -> ComponentResult:
        return cls._backup_paths_as_tar(
            backup_dir=backup_dir,
            name="proxy",
            relative="proxy/squid.tar.gz",
            paths=["/etc/squid"],
            timeout=60,
            message_if_empty="Squid not installed",
        )

    @classmethod
    def _backup_network(cls, backup_dir: Path) -> ComponentResult:
        return cls._backup_paths_as_tar(
            backup_dir=backup_dir,
            name="network",
            relative="network/network.tar.gz",
            paths=[
                "/etc/network",
                "/etc/NetworkManager",
                "/etc/netplan",
                "/etc/systemd/network",
                "/etc/systemd/networkd.conf",
                "/etc/resolv.conf",
            ],
            timeout=60,
            message_if_empty="No network config found",
        )

    @classmethod
    def _backup_security(cls, backup_dir: Path) -> ComponentResult:
        return cls._backup_paths_as_tar(
            backup_dir=backup_dir,
            name="security",
            relative="security/security.tar.gz",
            paths=["/etc/fail2ban", "/etc/ssh", "/etc/pam.d"],
            timeout=60,
            message_if_empty="No security config found",
        )

    @classmethod
    def _backup_certificates(cls, backup_dir: Path) -> ComponentResult:
        return cls._backup_paths_as_tar(
            backup_dir=backup_dir,
            name="certificates",
            relative="certificates/certificates.tar.gz",
            paths=["/etc/easy-rsa", "/etc/ssl/certs", "/etc/ssl/private", "/asguard/asguard/pki"],
            timeout=120,
            message_if_empty="No certificate paths found",
        )

    @classmethod
    def _backup_application(cls, backup_dir: Path) -> ComponentResult:
        name = "application"
        relative = "application/asguard_app.tar.gz"
        dest = backup_dir / relative

        app_dir = cls.APP_ROOT
        if not app_dir.exists():
            return ComponentResult.skipped(name, f"App directory {app_dir} not found")

        with Timer() as t:
            try:
                r = run_cmd(
                    [
                        "tar",
                        "--exclude=__pycache__",
                        "--exclude=.git",
                        "--exclude=venv",
                        "--exclude=node_modules",
                        "-czf",
                        str(dest),
                        str(app_dir),
                    ],
                    timeout=300,
                )
                if not r["success"]:
                    return ComponentResult.failed(name, r.get("error", r.get("stderr", "tar failed")))
            except Exception as exc:
                return ComponentResult.failed(name, str(exc))

        return cls._build_component_result_from_file(name, relative, dest, t.elapsed)

    @classmethod
    def _backup_system_config(cls, backup_dir: Path) -> ComponentResult:
        name = "system_config"
        relative = "system_config/etc.tar.gz"
        dest = backup_dir / relative

        with Timer() as t:
            try:
                r = run_cmd(
                    [
                        "tar",
                        "--ignore-failed-read",
                        "--exclude=/etc/mtab",
                        "-czf",
                        str(dest),
                        "/etc",
                    ],
                    timeout=300,
                )
                if not r["success"]:
                    return ComponentResult.failed(name, r.get("error", r.get("stderr", "tar failed")))
            except Exception as exc:
                return ComponentResult.failed(name, str(exc))

        return cls._build_component_result_from_file(name, relative, dest, t.elapsed)

    @classmethod
    def _backup_scheduled_tasks(cls, backup_dir: Path) -> ComponentResult:
        return cls._backup_paths_as_tar(
            backup_dir=backup_dir,
            name="scheduled_tasks",
            relative="scheduled_tasks/scheduled_tasks.tar.gz",
            paths=[
                "/etc/crontab",
                "/etc/cron.d",
                "/etc/cron.daily",
                "/etc/cron.hourly",
                "/etc/cron.weekly",
                "/etc/cron.monthly",
                "/var/spool/cron",
            ],
            timeout=60,
            message_if_empty="No cron paths found",
        )

    @classmethod
    def _backup_packages(cls, backup_dir: Path) -> ComponentResult:
        name = "packages"
        pkg_dir = backup_dir / "packages"
        pkg_dir.mkdir(parents=True, exist_ok=True)

        with Timer() as t:
            try:
                if Path("/usr/bin/pacman").exists():
                    pkg_list_file = pkg_dir / "pacman_packages.txt"
                    r = run_cmd(["pacman", "-Qqe"], timeout=30)
                    if not r["success"]:
                        return ComponentResult.failed(name, f"pacman failed: {r.get('error', '')}")
                    pkg_list_file.write_text(r["stdout"], encoding="utf-8")
                    target_file = pkg_list_file
                    message = "Packages saved in pacman format"

                elif Path("/usr/bin/dpkg").exists():
                    pkg_list_file = pkg_dir / "dpkg_selections.txt"
                    r = run_cmd(["dpkg", "--get-selections"], timeout=30)
                    if not r["success"]:
                        return ComponentResult.failed(name, f"dpkg failed: {r.get('error', '')}")
                    pkg_list_file.write_text(r["stdout"], encoding="utf-8")
                    target_file = pkg_list_file
                    message = "Packages saved in dpkg format"

                else:
                    return ComponentResult.skipped(name, "No supported package manager found")

            except Exception as exc:
                return ComponentResult.failed(name, str(exc))

        return ComponentResult(
            name=name,
            status="success",
            file=str(target_file.relative_to(backup_dir)),
            size_mb=target_file.stat().st_size / (1024 ** 2),
            sha256=compute_sha256(target_file),
            duration_s=t.elapsed,
            message=message,
        )

    @classmethod
    def _backup_systemd_services(cls, backup_dir: Path) -> ComponentResult:
        name = "systemd_services"
        dest_dir = backup_dir / "systemd_services"
        dest_dir.mkdir(parents=True, exist_ok=True)

        with Timer() as t:
            try:
                r = run_cmd(
                    ["systemctl", "list-unit-files", "--type=service", "--state=enabled", "--no-pager", "--no-legend"],
                    timeout=30,
                )
                if r["success"]:
                    (dest_dir / "enabled_services.txt").write_text(r["stdout"], encoding="utf-8")

                r2 = run_cmd(
                    ["systemctl", "list-units", "--type=service", "--state=active", "--no-pager", "--no-legend"],
                    timeout=30,
                )
                if r2["success"]:
                    (dest_dir / "active_services.txt").write_text(r2["stdout"], encoding="utf-8")

                custom_systemd = Path("/etc/systemd/system")
                if custom_systemd.exists():
                    run_cmd(
                        [
                            "tar",
                            "--ignore-failed-read",
                            "-czf",
                            str(dest_dir / "custom_units.tar.gz"),
                            str(custom_systemd),
                        ],
                        timeout=60,
                    )

            except Exception as exc:
                return ComponentResult.failed(name, str(exc))

        enabled_file = dest_dir / "enabled_services.txt"
        if not enabled_file.exists():
            return ComponentResult.failed(name, "Service list not created")

        size_mb = sum(f.stat().st_size for f in dest_dir.rglob("*") if f.is_file()) / (1024 ** 2)
        return ComponentResult(
            name=name,
            status="success",
            file="systemd_services/enabled_services.txt",
            size_mb=size_mb,
            duration_s=t.elapsed,
        )

    @classmethod
    def _backup_docker_state(cls, backup_dir: Path) -> ComponentResult:
        name = "docker_state"
        dest_dir = backup_dir / "docker_state"
        dest_dir.mkdir(parents=True, exist_ok=True)

        with Timer() as t:
            try:
                r = run_cmd(["docker", "images", "--format", "{{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.Size}}"], timeout=30)
                if r["success"]:
                    (dest_dir / "docker_images.txt").write_text(r["stdout"], encoding="utf-8")

                r2 = run_cmd(
                    ["docker", "ps", "-a", "--format", "{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"],
                    timeout=30,
                )
                if r2["success"]:
                    (dest_dir / "docker_containers.txt").write_text(r2["stdout"], encoding="utf-8")

                r3 = run_cmd(["docker", "volume", "ls", "--format", "{{.Name}}\t{{.Driver}}"], timeout=30)
                if r3["success"]:
                    (dest_dir / "docker_volumes.txt").write_text(r3["stdout"], encoding="utf-8")

                r4 = run_cmd(["docker", "network", "ls", "--format", "{{.Name}}\t{{.Driver}}\t{{.Scope}}"], timeout=30)
                if r4["success"]:
                    (dest_dir / "docker_networks.txt").write_text(r4["stdout"], encoding="utf-8")

            except Exception as exc:
                return ComponentResult.failed(name, str(exc))

        images_file = dest_dir / "docker_images.txt"
        if not images_file.exists():
            return ComponentResult.failed(name, "Docker state not saved")

        size_mb = sum(f.stat().st_size for f in dest_dir.rglob("*") if f.is_file()) / (1024 ** 2)
        return ComponentResult(
            name=name,
            status="success",
            file="docker_state/docker_images.txt",
            size_mb=size_mb,
            duration_s=t.elapsed,
        )

    @classmethod
    def _backup_logs(cls, backup_dir: Path) -> ComponentResult:
        name = "logs"
        logs_dir = backup_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)

        archive = logs_dir / "system_logs.tar.gz"

        log_sources = [
            "/var/log/nginx",
            "/var/log/openvpn",
            "/var/log/suricata",
            "/var/log/asguard",
            "/var/log/syslog",
            "/var/log/messages",
            "/var/log/auth.log",
        ]

        existing_sources = [p for p in log_sources if Path(p).exists()]

        with Timer() as t:
            if not existing_sources:
                return ComponentResult.skipped(name, "No log sources found to back up")

            cmd = ["sudo", "/usr/bin/tar", "-czf", str(archive)] + existing_sources
            res = run_cmd(cmd, timeout=180)

            if not res["success"]:
                return ComponentResult.failed(name, res.get("error", "logs backup failed"))

        return ComponentResult(
            name=name,
            status="success",
            file="logs/system_logs.tar.gz",
            size_mb=archive.stat().st_size / (1024 ** 2),
            sha256=compute_sha256(archive),
            duration_s=t.elapsed,
        )
    
    @classmethod
    def _backup_users_groups(cls, backup_dir: Path) -> ComponentResult:
        name = "users_groups"
        relative = "users_groups/users_groups.tar.gz"
        dest = backup_dir / relative
        sources = [
            p for p in [
                "/etc/passwd",
                "/etc/shadow",
                "/etc/group",
                "/etc/gshadow",
                "/etc/sudoers",
                "/etc/sudoers.d",
            ] if Path(p).exists()
        ]
        if not sources:
            return ComponentResult.skipped(name, "No files")

        with Timer() as t:
            try:
                r = run_cmd(["sudo", "tar", "--ignore-failed-read", "-czf", str(dest)] + sources, timeout=60)
                if not r["success"]:
                    return ComponentResult.failed(name, r.get("error", r.get("stderr", "tar failed")))
            except Exception as exc:
                return ComponentResult.failed(name, str(exc))

        return cls._build_component_result_from_file(name, relative, dest, t.elapsed)

    @classmethod
    def _backup_vm_snapshot(cls, backup_dir: Path) -> ComponentResult:
        name = "vm_snapshot"
        snapshot_info_file = backup_dir / "vm_snapshot" / "snapshot_info.json"
        msg = "VM snapshot temporarily disabled to avoid blocking full backup."

        try:
            snapshot_info_file.write_text(
                json.dumps({"status": "skipped", "message": msg}, indent=2),
                encoding="utf-8",
            )
        except Exception as exc:
            return ComponentResult.failed(name, f"Could not write snapshot_info.json: {exc}")

        return ComponentResult.skipped(name, msg)

    # -------------------------------------------------------------------------
    # New UI-aligned modules
    # -------------------------------------------------------------------------

    @classmethod
    def _backup_ztna(cls, backup_dir: Path) -> ComponentResult:
        return cls._backup_backend_module_dir(
            backup_dir=backup_dir,
            name="ztna",
            module_dir_name="ztna",
            relative="ztna/ztna.tar.gz",
            extra_paths=[],
            timeout=120,
        )

    @classmethod
    def _backup_ldap(cls, backup_dir: Path) -> ComponentResult:
        return cls._backup_backend_module_dir(
            backup_dir=backup_dir,
            name="ldap",
            module_dir_name="LdapServer",
            relative="ldap/ldap.tar.gz",
            extra_paths=["/etc/ldap", "/etc/openldap"],
            timeout=120,
        )

    @classmethod
    def _backup_ipsec_detailed(cls, backup_dir: Path) -> ComponentResult:
        return cls._backup_backend_module_dir(
            backup_dir=backup_dir,
            name="ipsec_detailed",
            module_dir_name="ipsec",
            relative="ipsec_detailed/ipsec_detailed.tar.gz",
            extra_paths=[
                "/etc/ipsec.conf",
                "/etc/ipsec.secrets",
                "/etc/ipsec.d",
                "/etc/strongswan.d",
                "/etc/swanctl",
            ],
            timeout=180,
        )

    @classmethod
    def _backup_routing(cls, backup_dir: Path) -> ComponentResult:
        name = "routing"
        dest_dir = backup_dir / "routing"
        dest_dir.mkdir(parents=True, exist_ok=True)

        backend_result = cls._backup_backend_module_dir(
            backup_dir=backup_dir,
            name="routing",
            module_dir_name="routing",
            relative="routing/routing_backend.tar.gz",
            extra_paths=[],
            timeout=120,
        )

        route_dump = cls._run_cmd_to_text_component(
            backup_dir=backup_dir,
            name="routing",
            relative="routing/ip_route_show.txt",
            cmd=["ip", "route", "show"],
            timeout=30,
            success_message="Routing table exported",
        )

        if backend_result.status == "failed" and route_dump.status == "failed":
            return ComponentResult.failed(name, "Routing backend and ip route export both failed")

        # composant final synthétique
        summary_file = dest_dir / "routing_summary.json"
        payload = {
            "backend_status": backend_result.to_dict(),
            "route_dump_status": route_dump.to_dict(),
        }
        with Timer() as t:
            summary_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        return cls._build_component_result_from_file(
            name=name,
            relative="routing/routing_summary.json",
            dest=summary_file,
            elapsed=t.elapsed,
            message="Routing backup completed (backend + route dump)",
        )

    @classmethod
    def _backup_vlan(cls, backup_dir: Path) -> ComponentResult:
        return cls._backup_backend_module_dir(
            backup_dir=backup_dir,
            name="vlan",
            module_dir_name="vlan",
            relative="vlan/vlan.tar.gz",
            extra_paths=["/etc/systemd/network", "/etc/network"],
            timeout=120,
        )

    @classmethod
    def _backup_vxlan(cls, backup_dir: Path) -> ComponentResult:
        return cls._backup_backend_module_dir(
            backup_dir=backup_dir,
            name="vxlan",
            module_dir_name="vxlan",
            relative="vxlan/vxlan.tar.gz",
            extra_paths=["/etc/systemd/network", "/etc/network"],
            timeout=120,
        )

    @classmethod
    def _backup_sdwan(cls, backup_dir: Path) -> ComponentResult:
        return cls._backup_backend_module_dir(
            backup_dir=backup_dir,
            name="sdwan",
            module_dir_name="sdwan",
            relative="sdwan/sdwan.tar.gz",
            extra_paths=[],
            timeout=120,
        )

    @classmethod
    def _backup_waf(cls, backup_dir: Path) -> ComponentResult:
        return cls._backup_backend_module_dir(
            backup_dir=backup_dir,
            name="waf",
            module_dir_name="waf",
            relative="waf/waf.tar.gz",
            extra_paths=["/etc/nginx", "/etc/nginx/modsec", "/etc/nginx/modsecurity"],
            timeout=180,
        )

    @classmethod
    def _backup_nat(cls, backup_dir: Path) -> ComponentResult:
        name = "nat"
        dest_dir = backup_dir / "nat"
        dest_dir.mkdir(parents=True, exist_ok=True)

        backend_result = cls._backup_backend_module_dir(
            backup_dir=backup_dir,
            name="nat",
            module_dir_name="nat",
            relative="nat/nat_backend.tar.gz",
            extra_paths=[],
            timeout=120,
        )

        nft_dump = cls._run_cmd_to_text_component(
            backup_dir=backup_dir,
            name="nat",
            relative="nat/nft_ruleset.txt",
            cmd=["nft", "list", "ruleset"],
            timeout=30,
            success_message="NAT/firewall ruleset exported",
        )

        if backend_result.status == "failed" and nft_dump.status == "failed":
            return ComponentResult.failed(name, "NAT backend and nft rules export both failed")

        summary_file = dest_dir / "nat_summary.json"
        payload = {
            "backend_status": backend_result.to_dict(),
            "nft_dump_status": nft_dump.to_dict(),
        }
        with Timer() as t:
            summary_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        return cls._build_component_result_from_file(
            name=name,
            relative="nat/nat_summary.json",
            dest=summary_file,
            elapsed=t.elapsed,
            message="NAT backup completed (backend + nft rules)",
        )

    @classmethod
    def _backup_dhcp(cls, backup_dir: Path) -> ComponentResult:
        return cls._backup_backend_module_dir(
            backup_dir=backup_dir,
            name="dhcp",
            module_dir_name="server_dhcp4",
            relative="dhcp/dhcp.tar.gz",
            extra_paths=["/etc/dhcp", "/etc/dhcpd.conf"],
            timeout=120,
        )

    @classmethod
    def _backup_gateway(cls, backup_dir: Path) -> ComponentResult:
        return cls._backup_backend_module_dir(
            backup_dir=backup_dir,
            name="gateway",
            module_dir_name="gateway",
            relative="gateway/gateway.tar.gz",
            extra_paths=[],
            timeout=120,
        )

    @classmethod
    def _backup_double_mask(cls, backup_dir: Path) -> ComponentResult:
        return cls._backup_backend_module_dir(
            backup_dir=backup_dir,
            name="double_mask",
            module_dir_name="double_mask",
            relative="double_mask/double_mask.tar.gz",
            extra_paths=[],
            timeout=120,
        )

    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------

    @classmethod
    def _build_metadata(
        cls,
        backup_id: str,
        results: dict,
        backup_scope: str,
        selected_components: list[str] | None = None,
    ) -> dict:
        counts = {"success": 0, "failed": 0, "skipped": 0}
        for r in results.values():
            counts[r.status] = counts.get(r.status, 0) + 1

        total_size = sum(r.size_mb for r in results.values())
        total_duration = sum(r.duration_s for r in results.values())
        non_skipped = counts["success"] + counts["failed"]
        health_score = round(100 * counts["success"] / non_skipped) if non_skipped > 0 else 0
        overall_status = cls._compute_overall_status(counts)

        metadata = {
            "schema_version": SCHEMA_VERSION,
            "backup_id": backup_id,
            "created_at": datetime.now(LOCAL_TZ).isoformat(),            
            "backup_scope": backup_scope,
            "overall_status": overall_status,
            "health_score": health_score,
            "system": {
                "hostname": _get_hostname(),
                "os": platform.platform(),
                "python_version": platform.python_version(),
            },
            "components": {name: r.to_dict() for name, r in results.items()},
            "totals": {
                "size_mb": round(total_size, 3),
                "duration_seconds": round(total_duration, 2),
                "components_success": counts["success"],
                "components_failed": counts["failed"],
                "components_skipped": counts["skipped"],
            },
        }
        if selected_components is not None:
            metadata["selected_components"] = selected_components
        return metadata


def _get_hostname() -> str:
    try:
        return socket.gethostname()
    except Exception:
        return "unknown"
