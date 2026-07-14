import json
import logging
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from django.db import transaction

from backend.network.models import Interface
from backend.rules.models import Rule
from .base import ComponentResult, run_cmd, safe_extract, Timer, compute_sha256

logger = logging.getLogger(__name__)


class SafeRestoreService:
    """
    Restore SAFE destiné à l'interface admin.

    Il ne restaure que les composants métier/configuration
    sans toucher au socle applicatif :
    - pas d'application
    - pas de nginx/web
    - pas de system_config
    - pas de systemd global
    - pas de docker
    - pas de database complète
    - pas de security/ssh (réservé au full restore)
    """

    BACKUP_ROOT = Path("/var/backups/asguard")

    @classmethod
    def restore_safe(cls, backup_id: str) -> dict:
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

        runners = {
            "firewall": cls._restore_firewall,
            "vpn": cls._restore_vpn,
            "ids": cls._restore_ids,
            "proxy": cls._restore_proxy,
            "network": cls._restore_network,
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
                logger.exception("Safe restore failed for component %s", component_name)
                results[component_name] = ComponentResult.failed(component_name, str(e)).to_dict()

        success = sum(1 for r in results.values() if r["status"] == "success")
        failed = sum(1 for r in results.values() if r["status"] == "failed")
        skipped = sum(1 for r in results.values() if r["status"] == "skipped")

        global_status = "success" if failed == 0 else ("failed" if success == 0 else "partial_success")

        # Restoring the components rolls back the DB and the config files, but the
        # kernel keeps whatever was loaded before (nft ruleset, routing table).
        # Without this the UI would show restored routes/rules the kernel doesn't
        # have — the console DR script already does the same in its phase 12.
        resync = cls._resync_runtime()

        return {
            "status": global_status,
            "backup_id": backup_id,
            "mode": "safe_restore_ui",
            "results": results,
            "resync": resync,
            "summary": {
                "success": success,
                "failed": failed,
                "skipped": skipped,
            },
        }

    @classmethod
    def _resync_runtime(cls) -> dict:
        """Re-apply the restored DB state to the kernel. Never raises: a restore
        that succeeded must not be reported as failed because the resync did."""
        try:
            from backend.backup.post_restore_resync import resync_all
            return resync_all()
        except Exception as e:
            logger.exception("Post-restore resync failed")
            return {"status": "error", "message": str(e)}

    @classmethod
    def _verify_component_file(
        cls,
        backup_dir: Path,
        component_name: str,
        component_meta: dict
    ) -> tuple[bool, str]:
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
    def _sudo_extract_archive(cls, archive: Path, timeout: int = 120) -> dict:
        """
        Extract archive to / using sudo tar, so root-owned files
        can be restored correctly.

        `--overwrite` is required: config files like /etc/nftables.conf carry
        extended ACLs (UpApp/uvicorn rwx), and without it GNU tar refuses to
        replace the existing file ("Cannot open: File exists"), failing the
        whole component restore on a same-VM restore. Matches the full-restore
        helper `_extract_archive_to_root`.
        """
        return run_cmd(["sudo", "/usr/bin/tar", "--overwrite", "-xzf", str(archive), "-C", "/"], timeout=timeout)

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
                    extract_res = cls._sudo_extract_archive(archive, timeout=60)
                    if not extract_res["success"]:
                        return ComponentResult.failed(name, extract_res.get("error", "firewall extract failed"))

                    apply_res = run_cmd(["sudo", "/usr/bin/nft", "-f", "/etc/nftables.conf"], timeout=30)
                    if not apply_res["success"]:
                        if backup_conf.exists():
                            shutil.copy2(backup_conf, current_conf)
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
    def _restore_firewall_rules_db(cls, extracted_root: Path) -> tuple[bool, str]:
        snapshot_file = extracted_root / "var" / "backups" / "asguard" / "firewall_rules_db.json"
        if not snapshot_file.exists():
            return True, "firewall db snapshot missing; nftables config restored only"

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

        warning_msg = ""
        if missing_interfaces:
            missing_list = ", ".join(sorted(set(missing_interfaces))[:5])
            warning_msg = f"Interfaces absentes ignorées (cross-VM): {missing_list}"
            logger.warning("Firewall DB restore: %s", warning_msg)

        with transaction.atomic():
            Rule.objects.all().delete()
            if rules_to_create:
                Rule.objects.bulk_create(rules_to_create)

        return True, warning_msg

    @classmethod
    def _restore_vpn(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "vpn"
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
            extract_res = cls._sudo_extract_archive(archive, timeout=120)
            if not extract_res["success"]:
                return ComponentResult.failed(name, extract_res.get("error", "vpn extract failed"))

            strongswan_res = run_cmd(
                ["sudo", "/usr/bin/systemctl", "restart", "strongswan"],
                timeout=60
            )
            openvpn_res = run_cmd(
                ["sudo", "/usr/bin/systemctl", "restart", "openvpn-server@server.service"],
                timeout=60
            )

            if not strongswan_res["success"] and not openvpn_res["success"]:
                return ComponentResult.failed(
                    name,
                    f"Both VPN restarts failed: strongswan={strongswan_res.get('error', '')} | openvpn={openvpn_res.get('error', '')}"
                )

        return ComponentResult(
            name=name,
            status="success",
            file=component_meta["file"],
            duration_s=t.elapsed,
        )

    @classmethod
    def _restore_ids(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "ids"
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
            extract_res = cls._sudo_extract_archive(archive, timeout=120)
            if not extract_res["success"]:
                return ComponentResult.failed(name, extract_res.get("error", "ids extract failed"))

            restart_res = run_cmd(
                ["sudo", "/usr/bin/systemctl", "restart", "suricata"],
                timeout=60
            )
            if not restart_res["success"]:
                return ComponentResult.failed(name, restart_res.get("error", "suricata restart failed"))

        return ComponentResult(
            name=name,
            status="success",
            file=component_meta["file"],
            duration_s=t.elapsed,
        )

    @classmethod
    def _restore_proxy(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "proxy"
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
            extract_res = cls._sudo_extract_archive(archive, timeout=120)
            if not extract_res["success"]:
                return ComponentResult.failed(name, extract_res.get("error", "proxy extract failed"))

            test_res = run_cmd(
                ["sudo", "/usr/sbin/squid", "-k", "parse", "-f", "/etc/squid/squid.conf"],
                timeout=30
            )
            if not test_res["success"]:
                return ComponentResult.failed(name, test_res.get("error", "squid config validation failed"))

            restart_res = run_cmd(
                ["sudo", "/usr/bin/systemctl", "restart", "squid"],
                timeout=90
            )
            if not restart_res["success"]:
                return ComponentResult.failed(name, restart_res.get("error", "squid restart failed"))

            status_res = run_cmd(
                ["sudo", "/usr/bin/systemctl", "is-active", "squid"],
                timeout=20
            )
            if not status_res["success"] or status_res.get("stdout", "").strip() != "active":
                return ComponentResult.failed(name, "squid service is not active after restart")

        return ComponentResult(
            name=name,
            status="success",
            file=component_meta["file"],
            duration_s=t.elapsed,
        )

    @classmethod
    def _restore_network(cls, backup_dir: Path, component_meta: dict) -> ComponentResult:
        name = "network"
        archive = backup_dir / component_meta["file"]

        with Timer() as t:
            extract_res = cls._sudo_extract_archive(archive, timeout=120)
            if not extract_res["success"]:
                return ComponentResult.failed(name, extract_res.get("error", "network extract failed"))

        return ComponentResult(
            name=name,
            status="success",
            file=component_meta["file"],
            size_mb=archive.stat().st_size / (1024**2),
            sha256=component_meta.get("sha256", ""),
            duration_s=t.elapsed,
        )

    @staticmethod
    def _component_name_from_meta(component_meta: dict) -> str:
        rel = component_meta.get("file", "")
        if "/" in rel:
            return rel.split("/", 1)[0]
        return "component"
