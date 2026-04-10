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

    @classmethod
    def restore_full(cls, backup_id: str) -> dict:
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

        # restore application LAST
        runners = {
            # core
            "users_groups": cls._restore_users_groups,
            "packages": cls._restore_packages,
            "system_config": cls._restore_extract_only,
            "network": cls._restore_extract_only,
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

            # new UI-aligned modules
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

            # application last
            "application": cls._restore_application,
        }

        for component_name, runner in runners.items():
            comp_meta = metadata.get("components", {}).get(component_name)
            if not comp_meta:
                results[component_name] = ComponentResult.skipped(
                    component_name, "No metadata for component"
                ).to_dict()
                continue

            if comp_meta.get("status") != "success":
                results[component_name] = ComponentResult.skipped(
                    component_name, f"Component status is {comp_meta.get('status')}"
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
            "results": results,
            "summary": {
                "success": success,
                "failed": failed,
                "skipped": skipped,
            },
        }

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
    def _healthcheck_backend(cls) -> tuple[bool, str]:
        result = run_cmd(["curl", "-fsS", "http://127.0.0.1:8000/swagger/"], timeout=20)
        if not result["success"]:
            return False, result.get("error", "backend healthcheck failed")
        return True, ""

    @classmethod
    def _extract_archive_to_root(cls, archive: Path, timeout: int = 120) -> tuple[bool, str]:
        """
        Extract a backup tar.gz archive to / using tar directly.
        This avoids safe_extract(..., Path("/")) issues with archived absolute paths.
        """
        res = run_cmd(["sudo", "/usr/bin/tar", "-xzf", str(archive), "-C", "/"], timeout=timeout)
        if not res["success"]:
            return False, res.get("error", res.get("stderr", "archive extraction failed"))
        return True, ""

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

    @staticmethod
    def _component_name_from_meta(component_meta: dict) -> str:
        rel = component_meta.get("file", "")
        if "/" in rel:
            return rel.split("/", 1)[0]
        return "component"

    @classmethod
    def _restore_extract_only(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = cls._component_name_from_meta(component_meta)
        archive_rel = component_meta["file"]
        archive = backup_dir / archive_rel

        with Timer() as t:
            ok, msg = cls._extract_archive_to_root(archive, timeout=180)
            if not ok:
                return ComponentResult.failed(name, msg)

        return ComponentResult(
            name=name,
            status="success",
            file=archive_rel,
            size_mb=archive.stat().st_size / (1024 ** 2),
            sha256=component_meta.get("sha256", ""),
            duration_s=t.elapsed,
        )

    @classmethod
    def _restore_database(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "database"
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
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

                validate = run_cmd(["sudo", "nft", "-c", "-f", str(staged_conf)], timeout=30)
                if not validate["success"]:
                    return ComponentResult.failed(name, validate.get("error", "nft validation failed"))

                current_conf = Path("/etc/nftables.conf")
                backup_conf = Path("/tmp/nftables.conf.before_restore")
                if current_conf.exists():
                    shutil.copy2(current_conf, backup_conf)

                try:
                    ok, msg = cls._extract_archive_to_root(archive, timeout=120)
                    if not ok:
                        return ComponentResult.failed(name, msg)

                    apply_res = run_cmd(["sudo", "nft", "-f", "/etc/nftables.conf"], timeout=30)
                    if not apply_res["success"]:
                        if backup_conf.exists():
                            shutil.copy2(backup_conf, current_conf)
                            run_cmd(["sudo", "nft", "-f", "/etc/nftables.conf"], timeout=30)
                        return ComponentResult.failed(name, apply_res.get("error", "nft reload failed"))
                finally:
                    if backup_conf.exists():
                        backup_conf.unlink(missing_ok=True)

        return ComponentResult(
            name=name,
            status="success",
            file=component_meta["file"],
            duration_s=t.elapsed,
        )

    @classmethod
    def _restore_web(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "web"
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
            with TemporaryDirectory(prefix="restore_web_") as tmp:
                tmp_path = Path(tmp)
                safe_extract(archive, tmp_path)

                staged_nginx = tmp_path / "etc" / "nginx"
                if not staged_nginx.exists():
                    return ComponentResult.failed(name, "staged nginx config not found")

                current_nginx = Path("/etc/nginx")
                backup_nginx = Path("/tmp/nginx_before_restore")

                if backup_nginx.exists():
                    shutil.rmtree(backup_nginx, ignore_errors=True)
                if current_nginx.exists():
                    shutil.copytree(current_nginx, backup_nginx, dirs_exist_ok=True)

                try:
                    ok, msg = cls._extract_archive_to_root(archive, timeout=180)
                    if not ok:
                        return ComponentResult.failed(name, msg)

                    test = run_cmd(["sudo", "nginx", "-t"], timeout=30)
                    if not test["success"]:
                        if backup_nginx.exists():
                            shutil.rmtree(current_nginx, ignore_errors=True)
                            shutil.copytree(backup_nginx, current_nginx, dirs_exist_ok=True)
                        return ComponentResult.failed(name, test.get("error", "nginx config test failed"))

                    reload_res = run_cmd(["sudo", "systemctl", "reload", "nginx"], timeout=30)
                    if not reload_res["success"]:
                        if backup_nginx.exists():
                            shutil.rmtree(current_nginx, ignore_errors=True)
                            shutil.copytree(backup_nginx, current_nginx, dirs_exist_ok=True)
                            run_cmd(["sudo", "systemctl", "reload", "nginx"], timeout=30)
                        return ComponentResult.failed(name, reload_res.get("error", "nginx reload failed"))
                finally:
                    if backup_nginx.exists():
                        shutil.rmtree(backup_nginx, ignore_errors=True)

        return ComponentResult(
            name=name,
            status="success",
            file=component_meta["file"],
            duration_s=t.elapsed,
        )

    @classmethod
    def _restore_vpn(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "vpn"
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
            ok, msg = cls._extract_archive_to_root(archive, timeout=180)
            if not ok:
                return ComponentResult.failed(name, msg)

            strongswan_check = run_cmd(["systemctl", "list-unit-files", "strongswan.service"], timeout=10)
            openvpn_check = run_cmd(["systemctl", "list-unit-files", "openvpn-server@server.service"], timeout=10)

            strongswan_exists = strongswan_check["success"]
            openvpn_exists = openvpn_check["success"]

            strongswan_res = {"success": True, "error": ""}
            openvpn_res = {"success": True, "error": ""}

            if strongswan_exists:
                strongswan_res = run_cmd(["sudo", "systemctl", "restart", "strongswan"], timeout=30)

            if openvpn_exists:
                openvpn_res = run_cmd(["sudo", "systemctl", "restart", "openvpn-server@server.service"], timeout=30)

            if not strongswan_res["success"] and not openvpn_res["success"] and strongswan_exists and openvpn_exists:
                return ComponentResult.failed(
                    name,
                    f"Both VPN restarts failed: strongswan={strongswan_res.get('error', '')} | "
                    f"openvpn={openvpn_res.get('error', '')}"
                )

        return ComponentResult(name=name, status="success", file=component_meta["file"], duration_s=t.elapsed)

    @classmethod
    def _restore_ids(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "ids"
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
            ok, msg = cls._extract_archive_to_root(archive, timeout=180)
            if not ok:
                return ComponentResult.failed(name, msg)

            restart_res = run_cmd(["sudo", "systemctl", "restart", "suricata"], timeout=30)
            if not restart_res["success"]:
                return ComponentResult.failed(name, restart_res.get("error", "suricata restart failed"))

        return ComponentResult(name=name, status="success", file=component_meta["file"], duration_s=t.elapsed)

    @classmethod
    def _restore_proxy(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "proxy"
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
            ok, msg = cls._extract_archive_to_root(archive, timeout=120)
            if not ok:
                return ComponentResult.failed(name, msg)

        return ComponentResult(
            name=name,
            status="success",
            file=component_meta["file"],
            duration_s=t.elapsed,
            message="Squid config extracted. Restart skipped; final reboot will apply state.",
        )

    @classmethod
    def _restore_security(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "security"
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
            ok, msg = cls._extract_archive_to_root(archive, timeout=120)
            if not ok:
                return ComponentResult.failed(name, msg)

            fail2ban_check = run_cmd(["systemctl", "list-unit-files", "fail2ban.service"], timeout=10)
            if fail2ban_check["success"]:
                fail2ban_res = run_cmd(["sudo", "systemctl", "restart", "fail2ban"], timeout=30)
                if not fail2ban_res["success"]:
                    logger.warning("fail2ban restart failed: %s", fail2ban_res.get("error", ""))

            svc = "sshd" if Path("/usr/lib/systemd/system/sshd.service").exists() else "ssh"
            ssh_res = run_cmd(["sudo", "systemctl", "reload", svc], timeout=30)
            if not ssh_res["success"]:
                return ComponentResult.failed(name, ssh_res.get("error", f"{svc} reload failed"))

        return ComponentResult(name=name, status="success", file=component_meta["file"], duration_s=t.elapsed)

    @classmethod
    def _restore_packages(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "packages"
        pkg_file = backup_dir / component_meta["file"]

        with Timer() as t:
            if pkg_file.name.endswith("pacman_packages.txt") or "pacman" in pkg_file.name:
                return ComponentResult.skipped(name, "Package restore not auto-applied for pacman yet")
            elif pkg_file.name.endswith("dpkg_selections.txt"):
                r = run_cmd(
                    ["sudo", "dpkg", "--set-selections"],
                    input_data=pkg_file.read_text(encoding="utf-8"),
                    timeout=30,
                )
                if not r["success"]:
                    return ComponentResult.failed(name, r.get("error", "dpkg --set-selections failed"))
            else:
                return ComponentResult.skipped(name, "Unknown package format")

        return ComponentResult(name=name, status="success", file=component_meta["file"], duration_s=t.elapsed)

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
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
            return ComponentResult.skipped(
                name,
                f"Systemd services restore not auto-applied from snapshot file: {archive.name}"
            )

    @classmethod
    def _restore_logs(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "logs"
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
            return ComponentResult.skipped(
                name,
                f"Logs archive present but not auto-restored to avoid overwriting live evidence: {archive.name}"
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

            route_dump_meta = payload.get("route_dump_status", {})
            msg = "Routing backend restored; route dump kept as reference only."
            if route_dump_meta.get("status") == "success":
                msg = "Routing backend restored; ip route snapshot preserved for audit."

        return ComponentResult(
            name=name,
            status="success",
            file=component_meta["file"],
            duration_s=t.elapsed,
            message=msg,
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

            reload_res = run_cmd(["sudo", "systemctl", "reload", "nginx"], timeout=30)
            if not reload_res["success"]:
                return ComponentResult.failed(name, reload_res.get("error", "nginx reload failed after WAF restore"))

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
            restart_errors = []

            for svc in candidates:
                check = run_cmd(["systemctl", "list-unit-files", f"{svc}.service"], timeout=10)
                if check["success"]:
                    restart = run_cmd(["sudo", "systemctl", "restart", svc], timeout=30)
                    if restart["success"]:
                        restarted = True
                        break
                    restart_errors.append(f"{svc}: {restart.get('error', 'restart failed')}")

            if restart_errors and not restarted:
                logger.warning("DHCP restart attempts failed: %s", " | ".join(restart_errors))

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

                logger.info("[APP] Found application root: %s", extracted_root)

                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                app_parent = cls.APP_ROOT.parent
                staged_dir = app_parent / f".asguard_restored_{ts}"
                previous_dir = app_parent / f".asguard_previous_{ts}"

                if staged_dir.exists():
                    shutil.rmtree(staged_dir, ignore_errors=True)
                if previous_dir.exists():
                    shutil.rmtree(previous_dir, ignore_errors=True)

                logger.info("[APP] Staging restored app into %s", staged_dir)
                shutil.copytree(extracted_root, staged_dir, symlinks=True)

                logger.info("[APP] Stopping uvicorn...")
                stop_res = run_cmd(["systemctl", "stop", "uvicorn"], timeout=30)
                if not stop_res["success"]:
                    shutil.rmtree(staged_dir, ignore_errors=True)
                    return ComponentResult.failed(name, stop_res.get("error", "failed to stop uvicorn"))

                logger.info("[APP] Uvicorn stopped successfully")

                swapped = False
                try:
                    os.chdir("/")

                    if not cls.APP_ROOT.exists():
                        run_cmd(["systemctl", "start", "uvicorn"], timeout=30)
                        shutil.rmtree(staged_dir, ignore_errors=True)
                        return ComponentResult.failed(name, f"live application root not found: {cls.APP_ROOT}")

                    logger.info("[APP] Swapping live app with restored app")
                    os.rename(cls.APP_ROOT, previous_dir)
                    os.rename(staged_dir, cls.APP_ROOT)
                    swapped = True
                    logger.info("[APP] Application directory swapped successfully")

                except Exception as e:
                    logger.exception("[APP] Application swap failed: %s", e)

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

                    run_cmd(["systemctl", "start", "uvicorn"], timeout=30)
                    return ComponentResult.failed(name, f"application swap failed: {e}")

                if swapped and previous_dir.exists():
                    logger.info("[APP] Previous application kept at %s", previous_dir)

        logger.info("[APP] Application restored on disk; uvicorn intentionally left stopped; reboot required")
        return ComponentResult(
            name=name,
            status="success",
            file=component_meta["file"],
            size_mb=archive.stat().st_size / (1024 ** 2),
            sha256=component_meta.get("sha256", ""),
            duration_s=t.elapsed,
            message="Application restored on disk. Uvicorn intentionally left stopped; final reboot required.",
        )