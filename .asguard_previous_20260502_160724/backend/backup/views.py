import json
import logging
import os
import re
import shlex
import shutil
import subprocess
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from backend.backup.notifications import notify_backup_started, notify_backup_completed, notify_backup_scheduled
from backend.backup.system_backup.cloud_storage import CloudStorageService

from django.http import JsonResponse, FileResponse
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
import psutil

from .system_backup.backup_service import SystemBackupService
from .system_backup.full_backup_service import FullBackupService
from .system_backup.restore_service import RestoreService
from .system_backup.export_import_service import ExportImportService
from .system_backup.base import compute_sha256
from backend.dashboard.functions import get_system_infomations
from backend.dashboard.models import MonitoringData
from backend.network.models import Interface, IP4Config, IP6Config
from backend.nat.models import SNat, OneToOneNat, DNat
from backend.nat import utils_system as nat_utils_system
from backend.rules.models import Rule
from backend.openvpn.models import ServerOpenvpn
from backend.ipsec.models import ServerIPsec
from backend.ids_ips.models import suricatafile, SuricataInterface
from backend.proxy.models import ProxyRules, ProxyUser, ServerSatus
from backend.proxy.function import extract_names_from_file

logger = logging.getLogger(__name__)

BACKUP_DIR = Path("/var/backups/asguard")
BACKUP_PATTERNS = ["asguard_backup_*.dump", "asguard_db_*.dump"]

RESTORE_JOBS_DIR = BACKUP_DIR / "restore_jobs"
SYNC_SUMMARY_CACHE_FILE = BACKUP_DIR / "dashboard_last_sync_summary.json"
FULL_RESTORE_RUNNER = Path("/asguard/asguard/full_restore_runner.py")
PYTHON_BIN = "/usr/bin/python"
_LAST_DASHBOARD_SYNC_SUMMARY = None

# Components that are expected to be absent/skipped on a firewall appliance.
# Their absence does NOT degrade backup status or restore readiness.
NON_CRITICAL_COMPONENTS = {"vm_snapshot", "vm_snapshot_pre", "vm_snapshot_post"}

CRITICAL_SERVICE_CANDIDATES = [
    {
        "key": "sshd",
        "label": "SSH",
        "description": "Acces d'administration distant",
        "candidates": ["sshd", "ssh"],
        "category": "access",
    },
    {
        "key": "nginx",
        "label": "Nginx",
        "description": "Publication web et reverse proxy",
        "candidates": ["nginx"],
        "category": "platform",
    },
    {
        "key": "uvicorn",
        "label": "Uvicorn",
        "description": "Runtime applicatif principal",
        "candidates": ["uvicorn", "asguard", "gunicorn"],
        "category": "platform",
    },
    {
        "key": "postgresql",
        "label": "PostgreSQL",
        "description": "Base de donnees systeme",
        "candidates": ["postgresql", "postgresql.service"],
        "category": "data",
    },
    {
        "key": "docker",
        "label": "Docker",
        "description": "Moteur de conteneurs local",
        "candidates": ["docker"],
        "category": "platform",
    },
    {
        "key": "nftables",
        "label": "Firewall nftables",
        "description": "Application des regles firewall systeme",
        "candidates": ["nftables"],
        "category": "security",
    },
    {
        "key": "suricata",
        "label": "Suricata",
        "description": "Moteur IDS / IPS",
        "candidates": ["suricata"],
        "category": "security",
    },
    {
        "key": "squid",
        "label": "Squid",
        "description": "Proxy et filtrage web",
        "candidates": ["squid"],
        "category": "security",
    },
    {
        "key": "openvpn",
        "label": "OpenVPN",
        "description": "Service tunnel VPN",
        "candidates": ["openvpn-server@server.service", "openvpn-server@server", "openvpn"],
        "category": "network",
    },
    {
        "key": "ipsec",
        "label": "IPsec / StrongSwan",
        "description": "Service tunnel IPsec",
        "candidates": ["strongswan", "strongswan-starter", "ipsec"],
        "category": "network",
    },
    {
        "key": "fail2ban",
        "label": "Fail2ban",
        "description": "Protection d'administration",
        "candidates": ["fail2ban"],
        "category": "security",
    },
]

LEGACY_COMPONENT_PATHS = {
    "database": "db/postgres.dump",
    "firewall": "firewall/firewall_rules.tar.gz",
    "vpn": "vpn/vpn_configs.tar.gz",
    "web": "web/nginx.tar.gz",
    "ids": "ids/suricata.tar.gz",
    "proxy": "proxy/squid.tar.gz",
    "network": "network/network.tar.gz",
    "security": "security/security.tar.gz",
    "certificates": "certificates/certificates.tar.gz",
    "application": "application/application.tar.gz",
    "system_config": "system_config/etc.tar.gz",
    "scheduled_tasks": "scheduled_tasks/scheduled_tasks.tar.gz",
}

components_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["components"],
    properties={
        "components": openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING),
            description="List of component names, e.g. firewall, vpn, certificates.",
            example=["firewall", "vpn", "certificates"],
        ),
    },
)


def _infer_component_file(backup_dir: Path, component_name: str, component_data: dict) -> str:
    declared = component_data.get("file")
    if declared and (backup_dir / declared).exists():
        return declared

    legacy_path = LEGACY_COMPONENT_PATHS.get(component_name)
    if legacy_path and (backup_dir / legacy_path).exists():
        return legacy_path

    component_dir = backup_dir / ("db" if component_name == "database" else component_name)
    if component_dir.exists():
        files = sorted(p for p in component_dir.rglob("*") if p.is_file())
        if files:
            return str(files[0].relative_to(backup_dir))

    return declared or ""


def _normalize_backup_metadata(backup_dir: Path, metadata: dict) -> dict:
    normalized = dict(metadata or {})
    raw_components = normalized.get("components", {}) or {}
    normalized_components = {}
    counts = {"success": 0, "failed": 0, "skipped": 0}

    for component_name, raw_data in raw_components.items():
        component_data = dict(raw_data or {})
        rel_file = _infer_component_file(backup_dir, component_name, component_data)
        file_path = backup_dir / rel_file if rel_file else None
        file_exists = bool(file_path and file_path.exists() and file_path.is_file())
        has_size_hint = float(component_data.get("size_mb", 0) or 0) > 0

        status = component_data.get("status")
        if status not in {"success", "failed", "skipped"}:
            status = "success" if (file_exists or has_size_hint) else "failed"

        if file_exists:
            component_data["file"] = rel_file
            component_data["size_mb"] = round(file_path.stat().st_size / (1024 ** 2), 3)
            if not component_data.get("sha256") and file_path.stat().st_size > 0:
                try:
                    component_data["sha256"] = compute_sha256(file_path)
                except Exception:
                    component_data["sha256"] = ""
        else:
            component_data.setdefault("file", rel_file)
            component_data.setdefault("sha256", "")
            component_data.setdefault("size_mb", 0)

        component_data.setdefault("message", "")
        component_data.setdefault("duration_seconds", 0)
        component_data["status"] = status
        normalized_components[component_name] = component_data
        counts[status] += 1

    totals = dict(normalized.get("totals", {}) or {})
    totals["components_success"] = counts["success"]
    totals["components_failed"] = counts["failed"]
    totals["components_skipped"] = counts["skipped"]
    if "duration_seconds" not in totals:
        totals["duration_seconds"] = round(
            sum(float(component.get("duration_seconds", 0) or 0) for component in normalized_components.values()),
            2,
        )
    if "size_mb" not in totals:
        totals["size_mb"] = round(
            sum(float(component.get("size_mb", 0) or 0) for component in normalized_components.values()),
            3,
        )

    non_skipped = counts["success"] + counts["failed"]
    health_score = round(100 * counts["success"] / non_skipped) if non_skipped > 0 else 0

    skipped_names = {name for name, data in normalized_components.items() if data.get("status") == "skipped"}
    critical_skipped = skipped_names - NON_CRITICAL_COMPONENTS
    if counts["failed"] > 0:
        overall_status = "error"
    elif critical_skipped:
        overall_status = "partial"
    else:
        overall_status = "ok"

    normalized["components"] = normalized_components
    normalized["totals"] = totals
    normalized["health_score"] = health_score
    normalized["overall_status"] = overall_status
    return normalized


def _collect_backup_results() -> list[dict]:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    for d in BACKUP_DIR.glob("backup_*"):
        if d.is_dir():
            meta_file = d / "backup_metadata.json"
            if meta_file.exists():
                try:
                    with open(meta_file, "r", encoding="utf-8") as f:
                        meta = _normalize_backup_metadata(d, json.load(f))

                    backup_scope = meta.get("backup_scope", "unknown")
                    if backup_scope == "safe_restore_ui":
                        backup_type = "safe"
                    elif backup_scope == "selected_components" or d.name.startswith("backup_custom_"):
                        backup_type = "custom"
                    else:
                        backup_type = "full"

                    totals = meta.get("totals", {})
                    components_success = totals.get("components_success", 0)
                    components_failed = totals.get("components_failed", 0)
                    components_skipped = totals.get("components_skipped", 0)
                    size_bytes = int(
                        totals.get("size_mb", 0) * 1024 * 1024
                    ) if totals.get("size_mb") is not None else 0

                    if size_bytes <= 0:
                        size_bytes = sum(
                            p.stat().st_size
                            for p in d.rglob("*")
                            if p.is_file()
                        )

                    results.append({
                        "type": backup_type,
                        "scope": backup_scope,
                        "id": d.name,
                        "filename": d.name,
                        "size_bytes": size_bytes,
                        "modified_at": meta.get("created_at", datetime.fromtimestamp(d.stat().st_mtime).isoformat()),
                        "health_score": meta.get("health_score", 0),
                        "overall_status": meta.get("overall_status"),
                        "components_success": components_success,
                        "components_failed": components_failed,
                        "components_skipped": components_skipped,
                        "selected_components": meta.get("selected_components", []),
                        "metadata": meta,
                    })
                except Exception:
                    logger.warning("Could not read metadata for backup %s", d.name)

    for pattern in BACKUP_PATTERNS:
        for p in BACKUP_DIR.glob(pattern):
            st = p.stat()
            results.append({
                "type": "database_only",
                "scope": "legacy_database_only",
                "id": p.name,
                "filename": p.name,
                "size_bytes": st.st_size,
                "modified_at": datetime.fromtimestamp(st.st_mtime).isoformat(),
                "health_score": 100,
                "overall_status": "ok",
                "components_success": 1,
                "components_failed": 0,
                "components_skipped": 0,
            })

    results.sort(key=lambda x: x["modified_at"], reverse=True)
    return results


def _safe_parse_iso_datetime(value: str | None):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def _duration_seconds_between(started_at: str | None, finished_at: str | None) -> float:
    start = _safe_parse_iso_datetime(started_at)
    end = _safe_parse_iso_datetime(finished_at)
    if not start or not end:
        return 0.0
    try:
        return round(max((end - start).total_seconds(), 0), 2)
    except Exception:
        return 0.0


def _build_restore_verification(job_payload: dict) -> dict:
    result = job_payload.get("result") or {}
    result_summary = result.get("summary") or {}
    component_results = result.get("results") or {}
    stabilization = result.get("stabilization") or {}
    backup_id = job_payload.get("backup_id")

    backup_metadata = {}
    metadata_file = BACKUP_DIR / str(backup_id) / "backup_metadata.json"
    if metadata_file.exists():
        try:
            with open(metadata_file, "r", encoding="utf-8") as fh:
                backup_metadata = _normalize_backup_metadata(BACKUP_DIR / str(backup_id), json.load(fh))
        except Exception:
            backup_metadata = {}

    restored_components = [
        name for name, data in component_results.items()
        if data.get("status") == "success"
    ]
    failed_components = [
        name for name, data in component_results.items()
        if data.get("status") == "failed"
    ]
    skipped_components = [
        name for name, data in component_results.items()
        if data.get("status") == "skipped"
    ]

    verification_checks = [
        {
            "key": "restore_result",
            "label": "Execution restore",
            "status": "passed" if job_payload.get("status") == "success" else (
                "warning" if job_payload.get("status") == "partial_success" else "failed"
            ),
            "detail": f"{result_summary.get('success', 0)} composant(s) restaures avec succes.",
        },
        {
            "key": "stabilization",
            "label": "Stabilisation services",
            "status": "passed" if stabilization.get("status") == "success" else (
                "warning" if stabilization else "unknown"
            ),
            "detail": "Backend/nginx verifiés après restore." if stabilization else "Verification systeme indisponible.",
        },
        {
            "key": "backup_source",
            "label": "Source backup",
            "status": "passed" if backup_metadata else "unknown",
            "detail": f"Backup source: {backup_id}" if backup_id else "Backup source non determine.",
        },
    ]

    firewall_result = component_results.get("firewall") or {}
    if firewall_result:
        verification_checks.append({
            "key": "firewall",
            "label": "Firewall applique",
            "status": "passed" if firewall_result.get("status") == "success" else (
                "warning" if firewall_result.get("status") == "skipped" else "failed"
            ),
            "detail": firewall_result.get("message") or "Verification firewall terminee.",
        })

    return {
        "job_id": job_payload.get("job_id"),
        "backup_id": backup_id,
        "mode": job_payload.get("mode"),
        "status": job_payload.get("status"),
        "started_at": job_payload.get("started_at"),
        "finished_at": job_payload.get("finished_at"),
        "duration_seconds": _duration_seconds_between(
            job_payload.get("started_at"),
            job_payload.get("finished_at"),
        ),
        "summary": {
            "success": result_summary.get("success", 0),
            "failed": result_summary.get("failed", 0),
            "skipped": result_summary.get("skipped", 0),
            "restored_components": restored_components,
            "failed_components": failed_components,
            "skipped_components": skipped_components,
        },
        "checks": verification_checks,
        "stabilization": stabilization,
    }


def _load_dashboard_services() -> list[dict]:
    try:
        info = json.loads(get_system_infomations())
        services = []
        seen_names: set[str] = set()
        for item in info.get("list_info_services", []):
            parsed = json.loads(item)
            name = parsed.get("service_name")
            if not name or name in seen_names:
                continue
            services.append({
                "name": name,
                "label": parsed.get("description") or name,
                "description": parsed.get("description") or f"Service {name}",
                "enabled": bool(parsed.get("status_enabled")),
                "running": bool(parsed.get("status_started")),
                "installed": bool(parsed.get("status_install")),
                "manageable": True,
                "kind": "service",
                "category": "application",
                "status_detail": "running" if parsed.get("status_started") else "stopped",
                "source": "dashboard services table",
            })
            seen_names.add(name)

        for service_def in CRITICAL_SERVICE_CANDIDATES:
            resolved_name = None
            state = None
            for candidate in service_def["candidates"]:
                normalized = candidate.replace(".service", "")
                stdout, _, code = _run_readonly_command(["systemctl", "status", normalized], timeout=10)
                if code == 0 or "Loaded:" in stdout:
                    resolved_name = normalized
                    enabled_out, enabled_err, enabled_code = _run_readonly_command(
                        ["systemctl", "is-enabled", normalized],
                        timeout=8,
                    )
                    active_out, active_err, active_code = _run_readonly_command(
                        ["systemctl", "is-active", normalized],
                        timeout=8,
                    )
                    state = {
                        "enabled": enabled_code == 0 and enabled_out.strip() == "enabled",
                        "running": active_code == 0 and active_out.strip() == "active",
                        "installed": "not-found" not in (enabled_out + enabled_err + active_err).lower(),
                    }
                    break

            if resolved_name and resolved_name not in seen_names and state:
                services.append({
                    "name": resolved_name,
                    "label": service_def["label"],
                    "description": service_def["description"],
                    "enabled": state["enabled"],
                    "running": state["running"],
                    "installed": state["installed"],
                    "manageable": True,
                    "kind": "service",
                    "category": service_def["category"],
                    "status_detail": "running" if state["running"] else "stopped",
                    "source": "critical system service",
                })
                seen_names.add(resolved_name)

        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        backup_total, backup_used, backup_free = shutil.disk_usage(BACKUP_DIR)
        root_total, root_used, root_free = shutil.disk_usage("/")
        virt_out, _, virt_code = _run_readonly_command(["systemd-detect-virt"], timeout=8)
        vm_detail = virt_out.strip() if virt_code == 0 and virt_out.strip() else "bare-metal-or-undetected"

        runtime_checks = [
            {
                "name": "vm-runtime",
                "label": "Etat VM",
                "description": "Presence de la virtualisation et disponibilite de l'hote",
                "enabled": True,
                "running": True,
                "installed": True,
                "manageable": False,
                "kind": "runtime_check",
                "category": "vm",
                "status_detail": f"virtualisation: {vm_detail}",
                "source": "systemd-detect-virt",
            },
            {
                "name": "root-filesystem",
                "label": "Filesystem /",
                "description": "Occupation de la partition systeme",
                "enabled": True,
                "running": int((root_used / root_total) * 100) < 90 if root_total else True,
                "installed": True,
                "manageable": False,
                "kind": "runtime_check",
                "category": "system",
                "status_detail": f"{round((root_used / root_total) * 100) if root_total else 0}% utilise · {round(root_free / (1024 ** 3), 1)} GB libres",
                "source": "filesystem usage",
            },
            {
                "name": "backup-volume",
                "label": "Volume backup",
                "description": "Capacite restante sur le stockage de sauvegarde",
                "enabled": True,
                "running": int((backup_used / backup_total) * 100) < 90 if backup_total else True,
                "installed": True,
                "manageable": False,
                "kind": "runtime_check",
                "category": "backup",
                "status_detail": f"{round((backup_used / backup_total) * 100) if backup_total else 0}% utilise · {round(backup_free / (1024 ** 3), 1)} GB libres",
                "source": "backup storage usage",
            },
        ]
        services.extend(runtime_checks)
        services.sort(key=lambda item: (0 if item.get("kind") == "service" else 1, item.get("label") or item.get("name") or ""))
        return services
    except Exception:
        logger.exception("Failed to load dashboard services")
        return []


def _run_readonly_command(command: list[str], timeout: int = 8) -> tuple[str, str, int]:
    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return process.stdout.strip(), process.stderr.strip(), process.returncode
    except Exception as exc:
        return "", str(exc), 1


def _read_text_file(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except Exception:
        return ""


def _safe_percent(value: int, total: int) -> int:
    if total <= 0:
        return 100
    return round((value / total) * 100)


def _build_sync_module(
    key: str,
    label: str,
    checked_items: int,
    drifts: list[dict],
    note: str,
    source: str,
    entities: list[dict] | None = None,
) -> dict:
    status = "ok" if len(drifts) == 0 else "drift"
    ok_count = max(checked_items - len(drifts), 0)
    return {
        "key": key,
        "label": label,
        "status": status,
        "checked_items": checked_items,
        "ok_count": ok_count,
        "drift_count": len(drifts),
        "score": _safe_percent(max(0, checked_items - len(drifts)), checked_items),
        "summary": "Aucun ecart detecte." if len(drifts) == 0 else f"{len(drifts)} ecart(s) detecte(s).",
        "headline": f"{ok_count} OK · {len(drifts)} a corriger" if checked_items > 0 else "Aucune verification disponible",
        "note": note,
        "source": source,
        "entities": entities or [],
        "drifts": drifts[:8],
    }


def _scan_network_sync() -> dict:
    drifts: list[dict] = []
    stdout, _, _ = _run_readonly_command(["ip", "-o", "link", "show"])
    system_interfaces = set()
    for line in stdout.splitlines():
        match = re.match(r"^\d+:\s+([^:@]+)", line)
        if match:
            name = match.group(1)
            if name != "lo":
                system_interfaces.add(name)

    db_interfaces = list(
        Interface.objects.exclude(Q(ifname__startswith="tun_") | Q(ifname__startswith="tap_")).order_by("ifname")
    )
    checked_items = len(db_interfaces)
    for interface in db_interfaces:
        if interface.ifname not in system_interfaces:
            drifts.append({
                "kind": "missing_interface",
                "label": interface.name_interface or interface.ifname,
                "detail": f"Interface {interface.ifname} presente en base mais absente du systeme.",
            })

    for cfg in IP4Config.objects.filter(interface__in=db_interfaces, typeip4="static").exclude(ip_address__isnull=True).exclude(ip_address=""):
        stdout, _, _ = _run_readonly_command(["ip", "-4", "-o", "addr", "show", "dev", cfg.interface.ifname])
        if cfg.ip_address not in stdout:
            drifts.append({
                "kind": "ipv4_mismatch",
                "label": cfg.interface.name_interface or cfg.interface.ifname,
                "detail": f"IPv4 {cfg.ip_address} attendue en base mais non visible sur {cfg.interface.ifname}.",
            })

    for cfg in IP6Config.objects.filter(interface__in=db_interfaces, typeip6="static").exclude(ip_address6__isnull=True).exclude(ip_address6=""):
        stdout, _, _ = _run_readonly_command(["ip", "-6", "-o", "addr", "show", "dev", cfg.interface.ifname])
        expected = str(cfg.ip_address6).split("/")[0]
        if expected and expected not in stdout:
            drifts.append({
                "kind": "ipv6_mismatch",
                "label": cfg.interface.name_interface or cfg.interface.ifname,
                "detail": f"IPv6 {expected} attendue en base mais non visible sur {cfg.interface.ifname}.",
            })

    return _build_sync_module(
        "network",
        "Reseau",
        checked_items + IP4Config.objects.filter(interface__in=db_interfaces).count() + IP6Config.objects.filter(interface__in=db_interfaces).count(),
        drifts,
        "Compare les interfaces et adresses configurees en base avec l'etat observe sur le systeme via `ip link` et `ip addr`.",
        "system interfaces + DB interface/IP config",
    )


def _scan_nat_sync() -> dict:
    drifts: list[dict] = []
    try:
        system_postrouting, system_prerouting = nat_utils_system.get_list_nat_rules_from_system()
    except Exception as exc:
        return _build_sync_module(
            "nat",
            "NAT",
            0,
            [{"kind": "scan_error", "label": "NAT", "detail": f"Lecture systeme impossible: {exc}"}],
            "Compare les regles NAT actives en base avec les regles presentes dans `nftables`.",
            "nftables nat table + DB NAT rules",
        )

    active_snat = list(SNat.objects.filter(rule_status=True))
    active_one = list(OneToOneNat.objects.filter(rule_status=True))
    active_dnat = list(DNat.objects.filter(rule_status=True))
    checked_items = len(active_snat) + len(active_one) + len(active_dnat)

    for rule in active_snat:
        if not any((rule.rule_content or "") in item for item in system_postrouting):
            drifts.append({
                "kind": "missing_snat_rule",
                "label": rule.description or rule.rule_content or f"SNAT #{rule.pk}",
                "detail": "Regle SNAT active en base mais absente de nftables/postrouting.",
            })
    for rule in active_one:
        if not any((rule.rule_content or "") in item for item in system_postrouting):
            drifts.append({
                "kind": "missing_one_to_one_rule",
                "label": rule.description or rule.rule_content or f"OneToOne #{rule.pk}",
                "detail": "Regle One-to-One active en base mais absente de nftables/postrouting.",
            })
    for rule in active_dnat:
        if not any((rule.rule_content or "") in item for item in system_prerouting):
            drifts.append({
                "kind": "missing_dnat_rule",
                "label": rule.description or rule.rule_content or f"DNAT #{rule.pk}",
                "detail": "Regle DNAT active en base mais absente de nftables/prerouting.",
            })

    db_rule_contents = {(rule.rule_content or "").strip() for rule in [*active_snat, *active_one, *active_dnat] if rule.rule_content}
    extra_system = [
        rule for rule in [*system_postrouting, *system_prerouting]
        if rule and "# handle" in rule and not any(content and content in rule for content in db_rule_contents)
    ]
    for rule in extra_system[:3]:
        drifts.append({
            "kind": "extra_system_rule",
            "label": "Regle systeme non referencee",
            "detail": f"Une regle NAT existe dans nftables sans correspondance claire en base: {rule.split('# handle', 1)[0].strip()}",
        })

    return _build_sync_module(
        "nat",
        "NAT",
        checked_items,
        drifts,
        "Compare les regles NAT actives de la base avec les chaines `postrouting` et `prerouting` de nftables.",
        "nftables nat table + DB NAT rules",
    )


def _scan_firewall_sync() -> dict:
    drifts: list[dict] = []
    entities: list[dict] = []
    active_rules = list(
        Rule.objects.filter(rule_status=True)
        .select_related("interface")
        .order_by("interface__ifname", "type_rule", "position")
    )

    for rule in active_rules:
        interface_name = rule.interface.ifname if rule.interface_id and rule.interface else "unknown"
        candidate_files = [
            Path(f"/etc/rules/{interface_name}/nftables.conf"),
            Path("/etc/nftables.conf"),
        ]
        file_content = ""
        source_path = None
        for candidate in candidate_files:
            if candidate.exists():
                try:
                    file_content = candidate.read_text(encoding="utf-8", errors="ignore")
                    source_path = candidate
                    break
                except Exception:
                    continue

        label = rule.rule_description or rule.rule or f"Firewall rule #{rule.pk}"
        if not file_content:
            drifts.append({
                "kind": "firewall_source_missing",
                "label": label,
                "detail": f"Impossible de lire la source firewall pour l'interface {interface_name}.",
            })
            entities.append({
                "label": label,
                "status": "drift",
                "detail": f"source absente pour {interface_name}",
            })
            continue

        if (rule.rule or "") not in file_content:
            drifts.append({
                "kind": "firewall_rule_missing",
                "label": label,
                "detail": f"Regle firewall active en base absente de {source_path}.",
            })
            entities.append({
                "label": label,
                "status": "drift",
                "detail": f"absente de {source_path.name}",
            })
        else:
            entities.append({
                "label": label,
                "status": "ok",
                "detail": f"visible dans {source_path.name}",
            })

    checked_items = len(active_rules)
    return _build_sync_module(
        "firewall",
        "Firewall",
        checked_items,
        drifts,
        "Controle les regles firewall actives de la base contre les fichiers nftables deployes sur le systeme.",
        "DB firewall rules + /etc/rules/*/nftables.conf",
        entities[:10],
    )


def _scan_vpn_sync() -> dict:
    drifts: list[dict] = []
    checked_items = 0

    openvpn_servers = list(ServerOpenvpn.objects.all().order_by("name"))
    checked_items += len(openvpn_servers)
    for server in openvpn_servers:
        conf_path = Path(f"/etc/openvpn/server/server_{server.name}.conf")
        if not conf_path.exists():
            drifts.append({
                "kind": "missing_openvpn_conf",
                "label": server.name,
                "detail": f"Configuration OpenVPN absente: {conf_path}.",
            })
        stdout, _, code = _run_readonly_command(["systemctl", "is-active", f"openvpn-server@server_{server.name}"])
        is_active = code == 0 and stdout.strip() == "active"
        if bool(server.server_status) != is_active:
            drifts.append({
                "kind": "openvpn_status_mismatch",
                "label": server.name,
                "detail": f"Statut OpenVPN different entre base ({'running' if server.server_status else 'stopped'}) et systeme ({'running' if is_active else 'stopped'}).",
            })

    ipsec_conf = _read_text_file("/etc/ipsec.conf")
    system_postrouting, _ = nat_utils_system.get_list_nat_rules_from_system() if Path("/etc/nftables.conf").exists() else ([], [])
    ipsec_servers = list(ServerIPsec.objects.all().order_by("conn_name"))
    checked_items += len(ipsec_servers)
    for server in ipsec_servers:
        plain_conn = f"conn {server.conn_name}"
        commented_conn = f"#conn {server.conn_name}"
        if plain_conn not in ipsec_conf and commented_conn not in ipsec_conf:
            drifts.append({
                "kind": "missing_ipsec_conn",
                "label": server.conn_name,
                "detail": "Bloc `conn` IPsec absent de `/etc/ipsec.conf`.",
            })
        elif server.server_status and plain_conn not in ipsec_conf:
            drifts.append({
                "kind": "disabled_ipsec_conn",
                "label": server.conn_name,
                "detail": "Tunnel marque actif en base mais commente/desactive dans `/etc/ipsec.conf`.",
            })
        elif not server.server_status and commented_conn not in ipsec_conf:
            drifts.append({
                "kind": "enabled_ipsec_conn",
                "label": server.conn_name,
                "detail": "Tunnel marque inactif en base mais encore actif dans `/etc/ipsec.conf`.",
            })
        if server.server_status and server.postrouting_rule_content:
            if not any(server.postrouting_rule_content in item for item in system_postrouting):
                drifts.append({
                    "kind": "missing_ipsec_nat_rule",
                    "label": server.conn_name,
                    "detail": "Regle NAT d'accompagnement IPsec absente de nftables/postrouting.",
                })

    return _build_sync_module(
        "vpn",
        "VPN",
        checked_items,
        drifts,
        "Controle des configurations OpenVPN et IPsec entre base, fichiers de conf et etat runtime.",
        "OpenVPN conf/systemd + IPsec conf/nftables + DB VPN",
    )


def _scan_ids_sync() -> dict:
    drifts: list[dict] = []
    checked_items = 0
    yaml_path = Path("/etc/suricata/suricata.yaml")
    yaml_text = _read_text_file(str(yaml_path))
    configs = list(suricatafile.objects.all())
    interfaces = list(SuricataInterface.objects.select_related("interface").all())
    checked_items += len(configs) + len(interfaces)

    if not yaml_path.exists():
        drifts.append({
            "kind": "missing_suricata_yaml",
            "label": "Suricata",
            "detail": "Fichier `/etc/suricata/suricata.yaml` introuvable.",
        })
    else:
        for config in configs:
            if config.home_net and config.home_net not in yaml_text:
                drifts.append({
                    "kind": "home_net_mismatch",
                    "label": "HOME_NET",
                    "detail": f"HOME_NET `{config.home_net}` presente en base mais non retrouvee dans `suricata.yaml`.",
                })
            if config.profile and str(config.profile) not in yaml_text:
                drifts.append({
                    "kind": "profile_mismatch",
                    "label": "Profile IDS/IPS",
                    "detail": f"Profil `{config.profile}` non retrouve dans `suricata.yaml`.",
                })
        for item in interfaces:
            if item.interface and item.interface.ifname and item.interface.ifname not in yaml_text:
                drifts.append({
                    "kind": "suricata_interface_missing",
                    "label": item.interface.ifname,
                    "detail": f"Interface surveillee en base mais non visible dans `suricata.yaml`: {item.interface.ifname}.",
                })

    stdout, _, code = _run_readonly_command(["systemctl", "is-enabled", "suricata.service"])
    system_enabled = code == 0 and stdout.strip() == "enabled"
    for config in configs:
        if bool(config.status_enabled) != system_enabled:
            drifts.append({
                "kind": "suricata_enable_mismatch",
                "label": "Suricata service",
                "detail": f"Etat active/enabled different entre base ({'enabled' if config.status_enabled else 'disabled'}) et systeme ({'enabled' if system_enabled else 'disabled'}).",
            })
            break

    return _build_sync_module(
        "ids_ips",
        "IDS / IPS",
        checked_items,
        drifts,
        "Verifie la coherence entre la base IDS/IPS, `suricata.yaml` et l'etat du service Suricata.",
        "suricata.yaml + systemd + DB IDS/IPS",
    )


def _proxy_rule_exists_in_system(rule: ProxyRules, squid_conf: str) -> bool:
    if not rule.allow_by_auth and rule.type == "domain" and rule.time_from and rule.time_to:
        acl_name = f"block_{rule.value}"
        time_name = f"time_{acl_name}"
        return (
            f"acl {acl_name} url_regex {rule.value}" in squid_conf
            and f"acl {time_name} time" in squid_conf
            and f"http_access deny {acl_name} {time_name}" in squid_conf
        )

    if rule.allow_by_auth:
        if rule.type == "ip":
            path = "/etc/squid/allowed_ip_by_auth.acl"
        elif rule.type == "domain":
            path = "/etc/squid/allowed_domain_by_auth.acl"
        else:
            path = "/etc/squid/allowed_subnet_by_auth.acl"
    else:
        if rule.type == "ip":
            path = "/etc/squid/blocked_ip.acl"
        elif rule.type == "domain":
            path = "/etc/squid/blocked_domain.acl"
        else:
            path = "/etc/squid/blocked_subnet.acl"
    acl_content = _read_text_file(path)
    expected = f"#{rule.value}" if not rule.status else str(rule.value)
    return expected in acl_content


def _scan_proxy_sync() -> dict:
    drifts: list[dict] = []
    squid_conf = _read_text_file("/etc/squid/squid.conf")
    users_path = Path("/etc/squid/squid_passwd")
    checked_items = 0

    proxy_status = ServerSatus.objects.filter(pk=1).first()
    checked_items += 1 if proxy_status else 0
    stdout, _, code = _run_readonly_command(["systemctl", "is-active", "squid"])
    squid_running = code == 0 and stdout.strip() == "active"
    if proxy_status and bool(proxy_status.status_server) != squid_running:
        drifts.append({
            "kind": "proxy_status_mismatch",
            "label": "Service squid",
            "detail": f"Statut proxy different entre base ({'up' if proxy_status.status_server else 'down'}) et systeme ({'up' if squid_running else 'down'}).",
        })

    proxy_rules = list(ProxyRules.objects.all().order_by("rule_name"))
    checked_items += len(proxy_rules)
    for rule in proxy_rules:
        if not _proxy_rule_exists_in_system(rule, squid_conf):
            drifts.append({
                "kind": "proxy_rule_missing",
                "label": rule.rule_name or rule.value,
                "detail": f"Regle proxy `{rule.value}` presente en base mais non retrouvee dans la configuration Squid/ACL.",
            })

    proxy_users = list(ProxyUser.objects.all().order_by("username"))
    checked_items += len(proxy_users)
    system_users = set(extract_names_from_file(str(users_path)) or []) if users_path.exists() else set()
    for user in proxy_users:
        if user.username not in system_users:
            drifts.append({
                "kind": "proxy_user_missing",
                "label": user.username,
                "detail": "Utilisateur proxy present en base mais absent du fichier `squid_passwd`.",
            })

    return _build_sync_module(
        "proxy",
        "Proxy",
        checked_items,
        drifts,
        "Compare les regles et utilisateurs proxy en base avec les ACL Squid, `squid.conf` et le mot de passe Squid.",
        "squid.conf + ACL files + squid_passwd + DB proxy",
    )


def _scan_services_sync(services: list[dict]) -> dict:
    entities = [
        {
            "label": service.get("label") or service.get("name"),
            "status": "ok" if service.get("running") else "drift",
            "detail": service.get("status_detail") or ("running" if service.get("running") else "stopped"),
        }
        for service in services
    ]
    drifts = [
        {
            "kind": "service_down",
            "label": service.get("label") or service.get("name"),
            "detail": f"{service.get('label') or service.get('name')} signale un etat degradé: {service.get('status_detail') or 'service inactif'}.",
        }
        for service in services
        if not service.get("running")
    ]
    return _build_sync_module(
        "services",
        "Services & etat VM",
        len(services),
        drifts,
        "Controle les services critiques du systeme, les briques metier connues et quelques checks runtime (VM, stockage).",
        "systemd + dashboard services + runtime checks",
        entities,
    )


def _build_global_sync_summary(services: list[dict], selected_components: list[str] | None = None) -> dict:
    scanners = {
        "services": lambda: _scan_services_sync(services),
        "firewall": _scan_firewall_sync,
        "network": _scan_network_sync,
        "nat": _scan_nat_sync,
        "vpn": _scan_vpn_sync,
        "ids_ips": _scan_ids_sync,
        "proxy": _scan_proxy_sync,
    }
    available_components = list(scanners.keys())
    requested_components = [
        component for component in (selected_components or available_components)
        if component in scanners
    ] or available_components

    modules = [scanners[component]() for component in requested_components]
    total_checked = sum(module.get("checked_items", 0) for module in modules)
    total_drifts = sum(module.get("drift_count", 0) for module in modules)
    healthy_modules = sum(1 for module in modules if module.get("status") == "ok")

    overall_status = "synchronized" if total_drifts == 0 else "drift"
    return {
        "status": overall_status,
        "direction": "system_files_runtime_to_database",
        "scope": "services_firewall_network_nat_vpn_ids_proxy",
        "scope_label": " + ".join(module.get("label", component) for module, component in zip(modules, requested_components)),
        "last_check_at": datetime.now().isoformat(),
        "verification_mode": "dashboard_refresh_scan",
        "verification_mode_label": "analyse relancee au refresh du dashboard ou au clic sur analyser",
        "verified_entities": total_checked,
        "module_count": len(modules),
        "healthy_modules": healthy_modules,
        "desync_detected": total_drifts,
        "score": _safe_percent(max(0, total_checked - total_drifts), total_checked),
        "selected_components": requested_components,
        "available_components": available_components,
        "modules": modules,
        "note": "Le scan compare la base avec des sources reelles: fichiers de configuration, etat runtime et services systeme. Il ne corrige rien automatiquement; il signale les derives pour revue.",
    }


def _sync_component_signature(summary: dict | None) -> set[str]:
    if not summary:
        return set()
    selected = summary.get("selected_components") or []
    return {str(component) for component in selected if component}


def _load_cached_sync_summary(selected_components: list[str] | None = None) -> dict | None:
    global _LAST_DASHBOARD_SYNC_SUMMARY
    cached = _LAST_DASHBOARD_SYNC_SUMMARY
    if cached:
        cached = dict(cached)
    else:
        try:
            with SYNC_SUMMARY_CACHE_FILE.open("r", encoding="utf-8") as fh:
                cached = json.load(fh)
        except Exception:
            return None

    if not cached or cached.get("status") == "idle" or not cached.get("last_check_at"):
        return None

    requested = set(selected_components or cached.get("available_components") or [])
    cached_signature = _sync_component_signature(cached)
    if requested and cached_signature and requested != cached_signature:
        return None

    cached["_retained_from_last_scan"] = True
    cached["verification_mode_label"] = "dernier resultat conserve, aucun scan relance pendant le refresh automatique"
    return cached

def _save_cached_sync_summary(sync_summary: dict) -> None:
    global _LAST_DASHBOARD_SYNC_SUMMARY
    if not sync_summary or sync_summary.get("status") == "idle" or not sync_summary.get("last_check_at"):
        return
    _LAST_DASHBOARD_SYNC_SUMMARY = dict(sync_summary)
    try:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        with SYNC_SUMMARY_CACHE_FILE.open("w", encoding="utf-8") as fh:
            json.dump(sync_summary, fh, ensure_ascii=False)
    except Exception as exc:
        logger.warning("Unable to cache dashboard sync summary: %s", exc)


def _build_idle_sync_summary(selected_components: list[str] | None = None) -> dict:
    component_meta = {
        "services": "Services & etat VM",
        "firewall": "Firewall",
        "network": "Reseau",
        "nat": "NAT",
        "vpn": "VPN",
        "ids_ips": "IDS / IPS",
        "proxy": "Proxy",
    }
    available_components = list(component_meta.keys())
    requested_components = [
        component for component in (selected_components or available_components)
        if component in component_meta
    ] or available_components

    modules = [
        {
            "key": component,
            "label": component_meta[component],
            "status": "idle",
            "checked_items": 0,
            "ok_count": 0,
            "drift_count": 0,
            "score": 0,
            "summary": "Analyse non lancee.",
            "headline": "En attente d'analyse",
            "note": "Le scan de synchronisation sera lance manuellement.",
            "source": "manual scan",
            "entities": [],
            "drifts": [],
        }
        for component in requested_components
    ]

    return {
        "status": "idle",
        "direction": "system_files_runtime_to_database",
        "scope": "services_firewall_network_nat_vpn_ids_proxy",
        "scope_label": " + ".join(component_meta.get(component, component) for component in requested_components),
        "last_check_at": None,
        "verification_mode": "manual_on_demand",
        "verification_mode_label": "analyse uniquement sur action manuelle",
        "verified_entities": 0,
        "module_count": len(modules),
        "healthy_modules": 0,
        "desync_detected": 0,
        "score": 0,
        "selected_components": requested_components,
        "available_components": available_components,
        "modules": modules,
        "note": "Le dashboard se charge sans lancer de scan. Lance l'analyse manuellement pour comparer le systeme live, les services critiques, l'etat VM et la base.",
    }


def _parse_selected_sync_components(request) -> list[str] | None:
    raw_values = request.GET.getlist("components")
    if not raw_values:
        single_value = request.GET.get("components")
        raw_values = [single_value] if single_value else []

    selected_components: list[str] = []
    for raw_value in raw_values:
        for component in str(raw_value).split(","):
            normalized = component.strip().lower()
            if normalized and normalized not in selected_components:
                selected_components.append(normalized)

    return selected_components or None


def _build_integrity_summary(latest_backup: dict | None, average_health: int) -> dict:
    if not latest_backup:
        return {
            "status": "error",
            "last_check_at": None,
            "average_health": average_health,
            "components_success": 0,
            "components_failed": 0,
            "components_skipped": 0,
            "issues": [],
            "critical_components_ok": 0,
            "critical_components_total": 0,
            "coverage_percent": 0,
            "critical_components": [],
            "method": "archive_consistency",
            "note": "Controle de la derniere archive disponible, pas de la coherence live entre le systeme et la base de donnees.",
        }

    metadata = latest_backup.get("metadata", {}) or {}
    component_totals = metadata.get("totals", {}) or {}
    components = metadata.get("components", {}) or {}
    issues = []
    critical_components = [
        ("database", "Base de donnees"),
        ("network", "Reseau"),
        ("firewall", "Firewall"),
        ("vpn", "VPN"),
        ("ids", "IDS / IPS"),
        ("proxy", "Proxy"),
        ("certificates", "Certificats"),
        ("system_config", "Configuration systeme"),
    ]
    critical_available = [item for item in critical_components if item[0] in components]
    critical_ok = sum(1 for name, _label in critical_available if components.get(name, {}).get("status") == "success")

    for name, data in components.items():
        status = data.get("status")
        if status in {"failed", "skipped"}:
            message = data.get("message") or ("Composant echoue." if status == "failed" else "Composant saute.")
            restore_support = "restorable"
            if name == "vm_snapshot":
                restore_support = "manual_only"
                if "temporarily disabled" in message.lower():
                    message = f"{message} La restauration automatique n'est donc pas disponible pour ce composant."
            issues.append({
                "component": name,
                "label": name.replace("_", " "),
                "status": status,
                "message": message,
                "restore_support": restore_support,
                "impact": (
                    "Absent du backup final; il faudra une action manuelle ou un autre mecanisme de reprise."
                    if status == "skipped"
                    else "Le composant est present mais inutilisable dans ce backup."
                ),
            })

    return {
        "status": latest_backup.get("overall_status") if latest_backup else "error",
        "last_check_at": latest_backup.get("modified_at") if latest_backup else None,
        "average_health": average_health,
        "components_success": component_totals.get("components_success", 0),
        "components_failed": component_totals.get("components_failed", 0),
        "components_skipped": component_totals.get("components_skipped", 0),
        "issues": issues[:10],
        "critical_components_ok": critical_ok,
        "critical_components_total": len(critical_available),
        "coverage_percent": _safe_percent(critical_ok, len(critical_available)) if critical_available else 100,
        "critical_components": [
            {
                "key": name,
                "label": label,
                "status": components.get(name, {}).get("status", "missing"),
                "included": name in components,
            }
            for name, label in critical_components
            if name in components
        ],
        "method": "archive_consistency",
        "note": "Mesure la qualite de la derniere archive et sa couverture des composants critiques du systeme. Le ratio de couverture correspond au nombre de composants critiques presents et reussis dans cette archive.",
    }


def _build_dashboard_insights(latest_backup: dict | None, services: list[dict], sync_summary: dict, alerts: list[dict]) -> dict:
    latest_backup_at = _safe_parse_iso_datetime(latest_backup.get("modified_at") if latest_backup else None)
    backup_health = int(latest_backup.get("health_score", 0) or 0) if latest_backup else 0
    service_score = _safe_percent(sum(1 for service in services if service.get("running")), len(services))
    sync_score = int(sync_summary.get("score", 0) or 0)
    metadata = (latest_backup or {}).get("metadata", {}) or {}
    components = metadata.get("components", {}) or {}
    skipped_components = [
        {
            "name": name,
            "message": data.get("message") or "Composant saute",
        }
        for name, data in components.items()
        if data.get("status") == "skipped"
    ]
    failed_components = [
        {
            "name": name,
            "message": data.get("message") or "Composant en echec",
        }
        for name, data in components.items()
        if data.get("status") == "failed"
    ]
    critical_skipped = [c for c in skipped_components if c["name"] not in NON_CRITICAL_COMPONENTS]
    non_critical_skipped = [c for c in skipped_components if c["name"] in NON_CRITICAL_COMPONENTS]

    freshness_hours = None
    freshness_score = 0
    freshness_label = "Aucun backup"
    if latest_backup_at is not None:
        freshness_hours = round((datetime.now(latest_backup_at.tzinfo) - latest_backup_at).total_seconds() / 3600, 1)
        if freshness_hours <= 24:
            freshness_score = 100
            freshness_label = "Fenetre ideale"
        elif freshness_hours <= 48:
            freshness_score = 75
            freshness_label = "Encore frais"
        elif freshness_hours <= 72:
            freshness_score = 45
            freshness_label = "A rafraichir"
        else:
            freshness_score = 15
            freshness_label = "Ancien"

    weights = {
        "backup_health": 0.40,
        "sync_score": 0.35,
        "service_score": 0.15,
        "freshness_score": 0.10,
    }
    protection_score = round(
        (backup_health * weights["backup_health"])
        + (sync_score * weights["sync_score"])
        + (service_score * weights["service_score"])
        + (freshness_score * weights["freshness_score"])
    )
    restore_readiness = "ready"
    restore_reason = "Backup exploitable, synchronisation stable et aucun signal bloquant majeur."
    if not latest_backup:
        restore_readiness = "attention"
        restore_reason = "Aucun backup exploitable n'est disponible pour un restore."
    elif failed_components or latest_backup.get("overall_status") in {"error", "failed"}:
        first_failed = failed_components[0] if failed_components else {"name": "backup", "message": "etat en echec"}
        restore_readiness = "attention"
        restore_reason = (
            f"Le backup contient {len(failed_components) or 1} composant(s) en echec. Exemple: "
            f"{first_failed['name']} - {first_failed['message']}"
        )
    elif critical_skipped:
        first_skipped = critical_skipped[0]
        restore_readiness = "attention"
        restore_reason = (
            f"Backup avec {len(critical_skipped)} composant(s) manquants. Exemple: "
            f"{first_skipped['name']} - {first_skipped['message']}"
        )
    elif non_critical_skipped:
        names = ", ".join(c["name"] for c in non_critical_skipped)
        restore_reason = (
            f"Backup sain et restaurable. {names} est desactive automatiquement sur ce type de deploiement, "
            f"cela n'impacte pas la restauration du firewall."
        )

    # Smart context-aware recommendations — prioritized by severity
    recommendations = []
    services_down = [s for s in services if not s.get("running")]
    has_sync_drift = sync_summary.get("desync_detected", 0) > 0

    if failed_components:
        names = ", ".join(item["name"] for item in failed_components[:2])
        recommendations.append(
            f"Relancer un backup complet: {names} a echoue et doit etre recupere pour garantir un restore fiable."
        )
    if critical_skipped:
        names = ", ".join(item["name"] for item in critical_skipped[:2])
        recommendations.append(
            f"Verifier pourquoi {names} a ete ignore lors du backup et corriger avant le prochain restore."
        )
    if services_down:
        first_down = services_down[0]
        label = first_down.get("label") or first_down.get("name", "service")
        if len(services_down) == 1:
            recommendations.append(
                f"{label} est arrete. Relancez-le avant tout restore pour eviter une interruption de service."
            )
        else:
            recommendations.append(
                f"{len(services_down)} services sont arretes dont {label}. Corrigez-les avant un restore."
            )
    if has_sync_drift:
        drift_count = sync_summary.get("desync_detected", 0)
        recommendations.append(
            f"{drift_count} ecart{'s' if drift_count > 1 else ''} detecte{'s' if drift_count > 1 else ''} entre "
            f"systeme et base. Revisez les modules en derive avant une operation de restore."
        )
    if not recommendations and freshness_hours is not None and freshness_hours > 48:
        recommendations.append(
            f"Votre backup date de {int(freshness_hours)}h. Planifiez un backup safe ce soir "
            f"pour maintenir une fenetre de restore optimale."
        )
    if not recommendations and non_critical_skipped and not failed_components:
        names = ", ".join(c["name"] for c in non_critical_skipped)
        recommendations.append(
            f"Backup sain et restaurable. {names} est desactive automatiquement, c'est le comportement attendu "
            f"sur un firewall sans hyperviseur embarque."
        )
    if not recommendations:
        if freshness_hours is not None and freshness_hours <= 24:
            recommendations.append(
                "Systeme en ordre. Backup frais, plateforme stable et aucun signal bloquant. "
                "Continuez la surveillance reguliere."
            )
        else:
            recommendations.append(
                "Le systeme est globalement coherent. Continuez la surveillance reguliere."
            )

    score_breakdown = [
        {
            "key": "backup_health",
            "label": "Sante backup",
            "value": backup_health,
            "weight_percent": int(weights["backup_health"] * 100),
            "contribution": round(backup_health * weights["backup_health"]),
            "why": "Monte si le dernier backup est sain et complet; baisse s'il est partiel ou en erreur.",
        },
        {
            "key": "sync_score",
            "label": "Synchronisation",
            "value": sync_score,
            "weight_percent": int(weights["sync_score"] * 100),
            "contribution": round(sync_score * weights["sync_score"]),
            "why": "Depend du scope scanne et des ecarts detectes entre systeme reel et base.",
        },
        {
            "key": "service_score",
            "label": "Services",
            "value": service_score,
            "weight_percent": int(weights["service_score"] * 100),
            "contribution": round(service_score * weights["service_score"]),
            "why": "Baisse si des services critiques surveilles sont arretes.",
        },
        {
            "key": "freshness_score",
            "label": "Fraicheur",
            "value": freshness_score,
            "weight_percent": int(weights["freshness_score"] * 100),
            "contribution": round(freshness_score * weights["freshness_score"]),
            "why": "Baisse naturellement quand le dernier backup vieillit.",
        },
    ]

    return {
        "protection_score": protection_score,
        "service_score": service_score,
        "sync_score": sync_score,
        "freshness_score": freshness_score,
        "freshness_hours": freshness_hours,
        "freshness_label": freshness_label,
        "restore_readiness": restore_readiness,
        "restore_reason": restore_reason,
        "active_alerts": len(alerts),
        "critical_services_down": sum(1 for service in services if not service.get("running")),
        "service_checks_ok": sum(1 for service in services if service.get("running")),
        "service_checks_total": len(services),
        "skipped_components": skipped_components[:6],
        "failed_components": failed_components[:6],
        "recommendations": recommendations[:3],
        "score_breakdown": score_breakdown,
        "score_explainer": "Le score change si le dernier backup vieillit, si les services critiques ou checks VM se degradent, ou si la synchronisation varie selon le scope analyse.",
        "score_scope_label": sync_summary.get("scope_label") or "scope global",
    }


def _load_monitoring_history(limit: int = 20) -> list[dict]:
    points = list(MonitoringData.objects.order_by("-timestamp")[:limit])
    points.reverse()
    return [
        {
            "timestamp": int(point.timestamp),
            "cpu": round(float(point.cpu_percentage), 2),
            "memory": round(float(point.memory_percentage), 2),
        }
        for point in points
    ]


def _get_live_metrics() -> dict:
    uptime_seconds = max(0, int(time.time() - psutil.boot_time()))
    uptime_days = uptime_seconds // 86400
    uptime_hours = (uptime_seconds % 86400) // 3600
    uptime_minutes = (uptime_seconds % 3600) // 60
    if uptime_days > 0:
        uptime = f"{uptime_days}j {uptime_hours}h {uptime_minutes}min"
    elif uptime_hours > 0:
        uptime = f"{uptime_hours}h {uptime_minutes}min"
    else:
        uptime = f"{uptime_minutes}min"

    try:
        load_average = ", ".join(f"{value:.2f}" for value in os.getloadavg())
    except (AttributeError, OSError):
        load_average = ""

    return {
        "cpu_percentage": psutil.cpu_percent(interval=None),
        "memory_percentage": psutil.virtual_memory().percent,
        "uptime": uptime,
        "load_average": load_average,
        "current_date": time.strftime("%a %b %d %H:%M:%S %Y"),
    }


def _build_chart_payloads(backups: list[dict], sync_summary: dict) -> dict:
    monitoring_history = _load_monitoring_history()
    backup_history = [
        {
            "id": backup.get("id"),
            "timestamp": backup.get("modified_at"),
            "health_score": int(backup.get("health_score", 0) or 0),
            "status": backup.get("overall_status"),
        }
        for backup in backups[:8]
    ]
    backup_history.reverse()

    sync_modules = [
        {
            "label": module.get("label"),
            "drift_count": int(module.get("drift_count", 0) or 0),
            "score": int(module.get("score", 0) or 0),
        }
        for module in sync_summary.get("modules", [])
    ]

    return {
        "resources_history": monitoring_history,
        "backup_health_history": backup_history,
        "sync_modules": sync_modules,
    }


def _build_dashboard_alerts(backups: list[dict], services: list[dict]) -> list[dict]:
    alerts: list[dict] = []

    for service in services:
        if not service.get("running"):
            alerts.append({
                "severity": "critical",
                "time": datetime.now().isoformat(),
                "service": service.get("name"),
                "message": "Service arrete",
                "cause": "Service systemd inactif ou non demarre",
                "action": "restart_service",
                "action_label": "Restart",
            })

    latest_backup = backups[0] if backups else None
    if latest_backup:
        status = latest_backup.get("overall_status")
        if status in {"error", "partial"}:
            alerts.append({
                "severity": "warning" if status == "partial" else "critical",
                "time": latest_backup.get("modified_at"),
                "service": "backup",
                "message": "Backup incomplet — composant(s) critique(s) manquants" if status == "partial" else "Backup en echec",
                "cause": f"Health {latest_backup.get('health_score', 0)}/100 — des composants critiques sont absents ou en erreur",
                "action": "open_backup",
                "action_label": "Voir backup",
            })

        latest_backup_at = _safe_parse_iso_datetime(latest_backup.get("modified_at"))
        if latest_backup_at is not None:
            age_hours = (datetime.now(latest_backup_at.tzinfo) - latest_backup_at).total_seconds() / 3600
            if age_hours > 48:
                alerts.append({
                    "severity": "warning",
                    "time": latest_backup.get("modified_at"),
                    "service": "backup",
                    "message": "Dernier backup ancien",
                    "cause": "Aucun backup recent detecte depuis plus de 48h",
                    "action": "create_backup",
                    "action_label": "Nouveau backup",
                })
    else:
        alerts.append({
            "severity": "critical",
            "time": datetime.now().isoformat(),
            "service": "backup",
            "message": "Aucun backup disponible",
            "cause": "Le systeme n'a pas encore de sauvegarde exploitable",
            "action": "create_backup",
            "action_label": "Creer backup",
        })

    severity_order = {"critical": 0, "warning": 1, "info": 2}
    alerts.sort(
        key=lambda item: (
            severity_order.get(item["severity"], 99),
            -(_safe_parse_iso_datetime(item.get("time")).timestamp() if _safe_parse_iso_datetime(item.get("time")) else 0),
        )
    )
    return alerts[:8]


@swagger_auto_schema("GET", responses={200: "OK"}, operation_summary="BACKUP DASHBOARD OVERVIEW")
@api_view(["GET"])
@require_http_methods(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def get_dashboard_overview(request):
    schedule_config = _read_schedule_config()
    _queue_due_schedule_catchups(schedule_config)
    backups = _collect_backup_results()
    services = _load_dashboard_services()
    selected_components = _parse_selected_sync_components(request)
    skip_sync_scan = str(request.GET.get("skip_sync_scan", "")).lower() in {"1", "true", "yes"}
    if skip_sync_scan:
        sync_summary = _load_cached_sync_summary(selected_components) or _build_idle_sync_summary(selected_components)
    else:
        sync_summary = _build_global_sync_summary(services, selected_components)
        _save_cached_sync_summary(sync_summary)
    alerts = _build_dashboard_alerts(backups, services)

    latest_backup = backups[0] if backups else None
    average_health = round(
        sum(int(item.get("health_score", 0) or 0) for item in backups) / len(backups)
    ) if backups else 0

    running_services = sum(1 for service in services if service.get("running"))
    failing_services = [service for service in services if not service.get("running")]

    backup_disk_total, backup_disk_used, backup_disk_free = shutil.disk_usage(BACKUP_DIR)
    root_disk_total, root_disk_used, root_disk_free = shutil.disk_usage("/")

    latest_backup_at = _safe_parse_iso_datetime(latest_backup.get("modified_at") if latest_backup else None)
    next_scheduled_task = _get_next_scheduled_task(schedule_config.get("tasks", []))
    projected_next_backup = next_scheduled_task.get("next_run") if next_scheduled_task else None
    next_backup_mode = "scheduled_task" if next_scheduled_task else "unplanned"
    if projected_next_backup is None and latest_backup_at is not None:
        try:
            projected_next_backup = (latest_backup_at + timedelta(days=1)).replace(microsecond=0).isoformat()
            next_backup_mode = "projection_daily"
        except Exception:
            projected_next_backup = latest_backup.get("modified_at")
            next_backup_mode = "projection_daily"

    integrity_summary = _build_integrity_summary(latest_backup, average_health)
    insights = _build_dashboard_insights(latest_backup, services, sync_summary, alerts)
    charts = _build_chart_payloads(backups, sync_summary)
    live_metrics = _get_live_metrics()

    return JsonResponse({
        "status": "ok",
        "cards": {
            "latest_backup": {
                "status": latest_backup.get("overall_status") if latest_backup else "error",
                "label": latest_backup.get("id") if latest_backup else "Aucun backup",
                "timestamp": latest_backup.get("modified_at") if latest_backup else None,
                "health_score": latest_backup.get("health_score", 0) if latest_backup else 0,
            },
            "services": {
                "running": running_services,
                "total": len(services),
                "failing": len(failing_services),
            },
            "backup_storage": {
                "used_bytes": sum(item.get("size_bytes", 0) for item in backups),
                "count": len(backups),
                "disk_total_bytes": backup_disk_total,
                "disk_used_bytes": backup_disk_used,
                "disk_free_bytes": backup_disk_free,
            },
            "next_backup": {
                "planned_at": projected_next_backup,
                "mode": next_backup_mode,
                "task": {
                    "id": next_scheduled_task.get("id"),
                    "label": next_scheduled_task.get("label"),
                    "cron": next_scheduled_task.get("cron"),
                    "type": next_scheduled_task.get("type"),
                } if next_scheduled_task else None,
            },
        },
        "integrity": integrity_summary,
        "sync": sync_summary,
        "insights": insights,
        "charts": charts,
        "live_metrics": live_metrics,
        "services": services,
        "resources": {
            "backup_disk": {
                "used_bytes": backup_disk_used,
                "total_bytes": backup_disk_total,
                "free_bytes": backup_disk_free,
            },
            "root_disk": {
                "used_bytes": root_disk_used,
                "total_bytes": root_disk_total,
                "free_bytes": root_disk_free,
            },
        },
        "alerts": alerts,
    })


@swagger_auto_schema("GET", responses={200: "OK"}, operation_summary="PING BACKUP MODULE")
@api_view(["GET"])
@require_http_methods(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def ping(request):
    return JsonResponse({"status": "ok", "module": "backup"})


@swagger_auto_schema("POST", responses={200: "OK", 500: "Erreur"}, operation_summary="TEST TELEGRAM NOTIFICATION")
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def test_telegram(request):
    try:
        from backend.backup.notifications import ntfy_test
        ntfy_test()
        return JsonResponse({"status": "ok", "message": "Notification ntfy envoyée."})
    except Exception as exc:
        return JsonResponse({"status": "error", "message": str(exc)}, status=500)


@swagger_auto_schema("POST", responses={200: "OK"}, operation_summary="CREATE DATABASE BACKUP (LEGACY)")
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def create_db_backup(request):
    threading.Thread(target=notify_backup_started, args=("db_backup",), daemon=True).start()
    result = SystemBackupService.create_db_backup()
    ok = result.get("status") == "ok"
    backup_id = result.get("backup_id") or Path(result.get("file", "")).stem
    threading.Thread(target=notify_backup_completed, args=("db_backup", backup_id, ok), daemon=True).start()
    CloudStorageService.async_upload_after_backup(backup_id, None, "db_backup", result)
    return JsonResponse(result)


@swagger_auto_schema("POST", responses={200: "OK"}, operation_summary="CREATE FULL BACKUP (DISASTER RECOVERY)")
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def create_full_backup(request):
    threading.Thread(target=notify_backup_started, args=("full_backup",), daemon=True).start()
    result = FullBackupService.create_full_backup()
    ok = result.get("status") == "ok"
    backup_id = result.get("backup_id", "")
    threading.Thread(target=notify_backup_completed, args=("full_backup", backup_id, ok), daemon=True).start()
    CloudStorageService.async_upload_after_backup(backup_id, result.get("backup_dir"), "full_backup", result)
    status_code = 200 if result["status"] == "ok" else (400 if result["status"] == "error" else 207)
    return JsonResponse(result, status=status_code)


@swagger_auto_schema("POST", responses={200: "OK"}, operation_summary="CREATE SAFE BACKUP (ADMIN UI)")
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def create_safe_backup(request):
    threading.Thread(target=notify_backup_started, args=("safe_backup",), daemon=True).start()
    result = FullBackupService.create_safe_backup()
    ok = result.get("status") == "ok"
    backup_id = result.get("backup_id", "")
    threading.Thread(target=notify_backup_completed, args=("safe_backup", backup_id, ok), daemon=True).start()
    CloudStorageService.async_upload_after_backup(backup_id, result.get("backup_dir"), "safe_backup", result)
    status_code = 200 if result["status"] == "ok" else (400 if result["status"] == "error" else 207)
    return JsonResponse(result, status=status_code)


@swagger_auto_schema(
    "GET",
    manual_parameters=[
        openapi.Parameter(
            "backup_id",
            openapi.IN_QUERY,
            description="Optional backup id. When provided, restore_components contains only restorable components from that backup.",
            type=openapi.TYPE_STRING,
            required=False,
        ),
    ],
    responses={200: "OK"},
    operation_summary="LIST BACKUP/RESTORE COMPONENTS",
)
@api_view(["GET"])
@require_http_methods(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def get_backup_components(request):
    return JsonResponse({
        "status": "ok",
        "backup_components": FullBackupService.available_components(),
        "restore_components": RestoreService.available_restore_components(
            request.GET.get("backup_id")
        ),
    })


@swagger_auto_schema(
    "POST",
    request_body=components_body_schema,
    responses={200: "OK", 400: "Bad Request"},
    operation_summary="CREATE CUSTOM BACKUP (SELECTED COMPONENTS)",
)
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def create_custom_backup(request):
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON body."}, status=400)

    components = payload.get("components", [])
    if not isinstance(components, list):
        return JsonResponse({"status": "error", "message": "components must be a list."}, status=400)

    result = FullBackupService.create_custom_backup(components)
    status_code = 200 if result["status"] == "ok" else (400 if result["status"] == "error" else 207)
    return JsonResponse(result, status=status_code)


@swagger_auto_schema("GET", responses={200: "OK"}, operation_summary="LIST ALL BACKUPS")
@api_view(["GET"])
@require_http_methods(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def get_all_backups(request):
    results = _collect_backup_results()
    return JsonResponse({"count": len(results), "results": results})


@swagger_auto_schema("GET", responses={200: "OK"}, operation_summary="GET BACKUP DETAILS")
@api_view(["GET"])
@require_http_methods(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def get_backup_details(request, backup_id):
    backup_dir = BACKUP_DIR / backup_id
    if not backup_dir.exists() or not backup_dir.is_dir():
        return JsonResponse({"status": "error", "message": f"Backup {backup_id} not found."}, status=404)

    metadata_file = backup_dir / "backup_metadata.json"
    if not metadata_file.exists():
        return JsonResponse({"status": "error", "message": "backup_metadata.json not found."}, status=404)

    try:
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = _normalize_backup_metadata(backup_dir, json.load(f))

        files = []
        total_size = 0
        for p in backup_dir.rglob("*"):
            if p.is_file():
                rel = str(p.relative_to(backup_dir))
                size = p.stat().st_size
                total_size += size
                files.append({
                    "path": rel,
                    "size_bytes": size,
                    "modified_at": datetime.fromtimestamp(p.stat().st_mtime).isoformat(),
                })

        return JsonResponse({
            "status": "ok",
            "backup_id": backup_id,
            "backup_dir": str(backup_dir),
            "total_size_bytes": total_size,
            "metadata": metadata,
            "files": files,
        })
    except Exception as e:
        logger.exception("Failed to read backup details for %s", backup_id)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@swagger_auto_schema("POST", responses={202: "Accepted"}, operation_summary="SAFE FULL RESTORE (WITHOUT APPLICATION)")
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def restore_backup(request, backup_id):
    return _launch_detached_restore(backup_id=backup_id, mode="safe")


@swagger_auto_schema("POST", responses={202: "Accepted"}, operation_summary="FULL RESTORE COMPLETE (WITH APPLICATION)")
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def restore_full_backup(request, backup_id):
    return _launch_detached_restore(backup_id=backup_id, mode="complete")


@swagger_auto_schema(
    "POST",
    request_body=components_body_schema,
    responses={200: "OK", 400: "Bad Request"},
    operation_summary="RESTORE SELECTED COMPONENTS",
)
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def restore_components(request, backup_id):
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON body."}, status=400)

    components = payload.get("components", [])
    if not isinstance(components, list):
        return JsonResponse({"status": "error", "message": "components must be a list."}, status=400)

    result = RestoreService.restore_components(backup_id, components)
    status_code = 200 if result.get("status") in ("success", "partial_success") else 400
    return JsonResponse(result, status=status_code)


def _launch_detached_restore(backup_id: str, mode: str):
    backup_dir = BACKUP_DIR / backup_id
    if not backup_dir.exists() or not backup_dir.is_dir():
        return JsonResponse({"status": "error", "message": f"Backup {backup_id} not found."}, status=404)

    metadata_file = backup_dir / "backup_metadata.json"
    if not metadata_file.exists():
        return JsonResponse({"status": "error", "message": "backup_metadata.json not found."}, status=404)

    RESTORE_JOBS_DIR.mkdir(parents=True, exist_ok=True)
    (RESTORE_JOBS_DIR / "logs").mkdir(parents=True, exist_ok=True)

    job_id = f"restore_{mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{backup_id}"
    state_file = RESTORE_JOBS_DIR / f"{job_id}.json"
    log_file = RESTORE_JOBS_DIR / "logs" / f"{job_id}.log"

    initial_state = {
        "job_id": job_id,
        "backup_id": backup_id,
        "mode": mode,
        "status": "queued",
        "started_at": None,
        "finished_at": None,
        "log_file": str(log_file),
        "result": None,
    }

    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(initial_state, f, indent=2)

    unit_name = f"asguard-restore-{mode}-{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    shell_cmd = (
        f"exec {shlex.quote(PYTHON_BIN)} "
        f"{shlex.quote(str(FULL_RESTORE_RUNNER))} "
        f"{shlex.quote(backup_id)} "
        f"{shlex.quote(job_id)} "
        f"{shlex.quote(mode)} "
        f">> {shlex.quote(str(log_file))} 2>&1"
    )

    cmd = [
        "sudo",
        "-n",
        "systemd-run",
        "--unit", unit_name,
        "--description", f"Asguard {mode} restore {backup_id}",
        "--property=WorkingDirectory=/asguard/asguard",
        "/usr/bin/bash",
        "-lc",
        shell_cmd,
    ]

    try:
        launch = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=20,
            check=False,
        )

        if launch.returncode != 0:
            logger.error(
                "systemd-run failed rc=%s output=%s",
                launch.returncode,
                launch.stdout.strip(),
            )
            return JsonResponse({
                "status": "error",
                "message": "Failed to launch detached restore unit.",
                "returncode": launch.returncode,
                "launcher_output": launch.stdout.strip(),
                "unit_name": unit_name,
                "mode": mode,
            }, status=500)

        logger.info("%s restore unit started: %s | output=%s", mode, unit_name, launch.stdout.strip())

        return JsonResponse({
            "status": "started",
            "message": f"{mode} restore launched in detached systemd unit.",
            "backup_id": backup_id,
            "job_id": job_id,
            "mode": mode,
            "state_file": str(state_file),
            "log_file": str(log_file),
            "unit_name": unit_name,
            "launcher_output": launch.stdout.strip(),
        }, status=202)

    except Exception as e:
        logger.exception("Failed to launch %s restore for %s", mode, backup_id)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@swagger_auto_schema("GET", responses={200: "OK"}, operation_summary="LIST ALL RESTORE JOBS (HISTORY)")
@api_view(["GET"])
@require_http_methods(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def get_restore_history(request):
    RESTORE_JOBS_DIR.mkdir(parents=True, exist_ok=True)
    entries = []

    for state_file in RESTORE_JOBS_DIR.glob("*.json"):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                payload = json.load(f)

            result = payload.get("result") or {}
            summary = result.get("summary") or {}
            component_results = result.get("results") or {}

            restored = [n for n, d in component_results.items() if d.get("status") == "success"]
            failed   = [n for n, d in component_results.items() if d.get("status") == "failed"]
            skipped  = [n for n, d in component_results.items() if d.get("status") == "skipped"]

            slowest = sorted(
                [(n, d.get("duration_seconds", 0)) for n, d in component_results.items() if d.get("duration_seconds", 0) > 0],
                key=lambda x: -x[1],
            )[:3]

            components_detail = sorted(
                [
                    {
                        "name": name,
                        "status": d.get("status"),
                        "message": d.get("message") or "",
                        "file": d.get("file") or "",
                        "size_mb": d.get("size_mb"),
                        "duration_seconds": round(d.get("duration_seconds") or 0, 2),
                    }
                    for name, d in component_results.items()
                    if d.get("status") in ("success", "failed")
                ],
                key=lambda x: (0 if x["status"] == "failed" else 1, x["name"]),
            )

            entries.append({
                "job_id": payload.get("job_id"),
                "backup_id": payload.get("backup_id"),
                "mode": payload.get("mode"),
                "status": payload.get("status"),
                "started_at": payload.get("started_at"),
                "finished_at": payload.get("finished_at"),
                "duration_seconds": _duration_seconds_between(
                    payload.get("started_at"), payload.get("finished_at")
                ),
                "summary": {
                    "success": summary.get("success", 0),
                    "failed": summary.get("failed", 0),
                    "skipped": summary.get("skipped", 0),
                    "restored_components": restored,
                    "failed_components": failed,
                    "skipped_components": skipped,
                },
                "components_detail": components_detail,
                "stabilization_status": (result.get("stabilization") or {}).get("status"),
                "slowest_components": [{"name": n, "duration_seconds": round(d, 2)} for n, d in slowest],
                "log_file": payload.get("log_file"),
            })
        except Exception:
            logger.warning("Could not read restore job file %s", state_file.name)

    entries.sort(key=lambda x: x.get("started_at") or "", reverse=True)
    total = len(entries)
    success_count = sum(1 for e in entries if e.get("status") == "success")
    avg_duration = round(
        sum(e.get("duration_seconds", 0) for e in entries) / total, 1
    ) if total else 0

    return JsonResponse({
        "count": total,
        "stats": {
            "total": total,
            "success": success_count,
            "failed": total - success_count,
            "success_rate": round(100 * success_count / total) if total else 0,
            "avg_duration_seconds": avg_duration,
        },
        "results": entries,
    })


@swagger_auto_schema("GET", responses={200: "OK"}, operation_summary="GET FULL RESTORE JOB STATUS")
@api_view(["GET"])
@require_http_methods(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def get_restore_full_status(request, job_id):
    state_file = RESTORE_JOBS_DIR / f"{job_id}.json"
    if not state_file.exists():
        return JsonResponse({"status": "error", "message": f"Restore job {job_id} not found."}, status=404)

    try:
        with open(state_file, "r", encoding="utf-8") as f:
            payload = json.load(f)
        payload["verification"] = _build_restore_verification(payload)
        return JsonResponse(payload, status=200)
    except Exception as e:
        logger.exception("Failed to read restore job status %s", job_id)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@swagger_auto_schema("DELETE", responses={200: "OK"}, operation_summary="DELETE BACKUP")
@api_view(["DELETE"])
@require_http_methods(["DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def delete_backup(request, backup_id):
    if not (
        backup_id.startswith("backup_")
        or backup_id.startswith("asguard_backup_")
        or backup_id.startswith("asguard_db_")
    ):
        return JsonResponse({"status": "error", "message": "Invalid backup id."}, status=400)

    backup_dir = BACKUP_DIR / backup_id
    legacy_backup = None
    for pattern in BACKUP_PATTERNS:
        match = next((p for p in BACKUP_DIR.glob(pattern) if p.name == backup_id), None)
        if match:
            legacy_backup = match
            break

    if not backup_dir.exists() and not legacy_backup:
        return JsonResponse({"status": "error", "message": f"Backup {backup_id} not found."}, status=404)

    try:
        import shutil
        if backup_dir.exists() and backup_dir.is_dir():
            shutil.rmtree(backup_dir)
        elif legacy_backup and legacy_backup.is_file():
            legacy_backup.unlink()
        return JsonResponse({"status": "success", "message": f"Backup {backup_id} deleted."})
    except Exception as e:
        logger.exception("Failed to delete backup %s", backup_id)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@swagger_auto_schema("GET", responses={200: "OK"}, operation_summary="EXPORT BACKUP")
@api_view(["GET"])
@require_http_methods(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def export_backup(request, backup_id):
    export_path = ExportImportService.export_backup(backup_id)
    if not export_path:
        return JsonResponse(
            {"status": "error", "message": "Backup export failed or not found."},
            status=404
        )

    response = FileResponse(open(export_path, "rb"), content_type="application/gzip")
    response["Content-Disposition"] = f'attachment; filename="asguard_export_{backup_id}.tar.gz"'
    return response


# ─────────────────────────────────────────────────────────────────────────────
#  BACKUP SCHEDULE & RETENTION
# ─────────────────────────────────────────────────────────────────────────────

SCHEDULE_CONFIG_FILE = Path("/var/backups/asguard/schedule_config.json")
_BACKUP_ROOT = Path("/var/backups/asguard")

DEFAULT_RETENTION = {
    "recent_keep_hours": 24,
    "daily_keep_days": 7,
    "weekly_keep_weeks": 4,
    "monthly_keep_months": 6,
    "max_total": 30,
    "min_free_gb": 5,
}

TASK_ENDPOINT_MAP = {
    "safe_backup": "create-safe-backup",
    "full_backup": "create-full-backup",
    "db_backup": "create-db-backup",
}

TASK_SERVICE_MAP = {
    "safe_backup": FullBackupService.create_safe_backup,
    "full_backup": FullBackupService.create_full_backup,
    "db_backup": SystemBackupService.create_db_backup,
}


def _read_schedule_config():
    if SCHEDULE_CONFIG_FILE.exists():
        try:
            return json.loads(SCHEDULE_CONFIG_FILE.read_text())
        except Exception:
            pass
    return {"tasks": [], "retention": DEFAULT_RETENTION.copy()}


def _write_schedule_config(config):
    SCHEDULE_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    SCHEDULE_CONFIG_FILE.write_text(json.dumps(config, indent=2, ensure_ascii=False))


def _cron_field_matches(part: str, value: int) -> bool:
    if part == "*":
        return True
    if part.startswith("*/"):
        try:
            step = int(part[2:])
            return step > 0 and value % step == 0
        except ValueError:
            return False
    try:
        return int(part) == value
    except ValueError:
        return False


def _cron_matches(expr: str, moment: datetime) -> bool:
    parts = (expr or "").strip().split()
    if len(parts) != 5:
        return False
    minute, hour, day, month, weekday = parts
    cron_weekday = (moment.weekday() + 1) % 7
    return (
        _cron_field_matches(minute, moment.minute)
        and _cron_field_matches(hour, moment.hour)
        and _cron_field_matches(day, moment.day)
        and _cron_field_matches(month, moment.month)
        and _cron_field_matches(weekday, cron_weekday)
    )


def _compute_cron_run(expr: str, *, after: datetime | None = None, reverse: bool = False, limit_days: int = 8):
    if not expr:
        return None
    cursor = (after or datetime.now()).replace(second=0, microsecond=0)
    step = -timedelta(minutes=1) if reverse else timedelta(minutes=1)
    cursor += step
    limit = (after or datetime.now()) + (-timedelta(days=limit_days) if reverse else timedelta(days=limit_days))
    while cursor >= limit if reverse else cursor <= limit:
        if _cron_matches(expr, cursor):
            return cursor
        cursor += step
    return None


def _safe_parse_datetime(value: str | None):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is not None:
            return parsed.astimezone().replace(tzinfo=None)
        return parsed
    except Exception:
        return None


def _latest_backup_after(moment: datetime) -> bool:
    return any(backup_dt >= moment for _, backup_dt in _list_backups_with_dates())


def _get_next_scheduled_task(tasks: list[dict]) -> dict | None:
    scheduled = []
    for task in tasks:
        if not task.get("enabled", True):
            continue
        next_run = _compute_cron_run(task.get("cron"))
        if next_run:
            scheduled.append({**task, "next_run": next_run.isoformat()})
    if not scheduled:
        return None
    return min(scheduled, key=lambda item: item["next_run"])


def _execute_scheduled_task(task_id: str):
    config = _read_schedule_config()
    tasks = config.get("tasks", [])
    task = next((item for item in tasks if item.get("id") == task_id), None)
    if not task or not task.get("enabled", True):
        return

    runner = TASK_SERVICE_MAP.get(task.get("type"))
    backup_type = task.get("type", "")
    task_name = task.get("name", task_id)
    now = datetime.now().isoformat()

    if not runner:
        task["last_run_at"] = now
        task["last_run_status"] = "error"
        task["last_run_message"] = "Unknown backup task type."
        _write_schedule_config(config)
        return

    threading.Thread(target=notify_backup_started, args=(backup_type,), daemon=True).start()
    threading.Thread(target=notify_backup_scheduled, args=(task_name, backup_type, task.get("cron", "")), daemon=True).start()

    t0 = time.monotonic()
    try:
        result = runner()
        duration = time.monotonic() - t0
        task["last_run_at"] = now
        task["last_run_status"] = result.get("status", "ok")
        task["last_run_message"] = result.get("message", "")
        ok = result.get("status") in ("ok", "success", None)
        backup_id = result.get("backup_id", "")
        threading.Thread(
            target=notify_backup_completed,
            args=(backup_type, backup_id, ok, duration, result.get("message", "")),
            daemon=True,
        ).start()
        CloudStorageService.async_upload_after_backup(backup_id, result.get("backup_dir"), backup_type, result)
    except Exception as exc:
        duration = time.monotonic() - t0
        logger.exception("Scheduled backup task %s failed", task_id)
        task["last_run_at"] = now
        task["last_run_status"] = "error"
        task["last_run_message"] = str(exc)
        threading.Thread(
            target=notify_backup_completed,
            args=(backup_type, "", False, duration, str(exc)),
            daemon=True,
        ).start()
    _write_schedule_config(config)


def _mark_scheduled_task_queued(task: dict, *, reason: str):
    task["last_queued_at"] = datetime.now().isoformat()
    task["last_queue_reason"] = reason


def _start_scheduled_task_thread(task_id: str):
    thread = threading.Thread(target=_execute_scheduled_task, args=(task_id,), daemon=True)
    thread.start()


def _queue_due_schedule_catchups(config: dict) -> bool:
    changed = False
    queued_task_ids = []
    now = datetime.now()
    for task in config.get("tasks", []):
        if not task.get("enabled", True):
            continue
        previous_run = _compute_cron_run(task.get("cron"), after=now, reverse=True)
        if not previous_run or previous_run.date() != now.date():
            continue
        last_run = _safe_parse_datetime(task.get("last_run_at"))
        last_queued_for = task.get("last_queued_for")
        previous_run_key = previous_run.isoformat()
        if (last_run and last_run >= previous_run) or last_queued_for == previous_run_key:
            continue
        if _latest_backup_after(previous_run):
            task["last_run_at"] = previous_run_key
            task["last_run_status"] = "ok"
            task["last_run_message"] = "Backup already found after scheduled time."
            changed = True
            continue
        task["last_queued_for"] = previous_run_key
        _mark_scheduled_task_queued(task, reason="missed_run_catchup")
        queued_task_ids.append(task["id"])
        changed = True
    if changed:
        _write_schedule_config(config)
    for task_id in queued_task_ids:
        _start_scheduled_task_thread(task_id)
    return changed


def _sync_crontab(tasks):
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    existing = result.stdout.splitlines() if result.returncode == 0 else []
    clean = [line for line in existing if "# asguard_task:" not in line]
    for task in tasks:
        if not task.get("enabled", True):
            continue
        endpoint = f"schedule/run/{task['id']}" if TASK_ENDPOINT_MAP.get(task.get("type", "")) else ""
        if not endpoint:
            continue
        line = (
            f"{task['cron']} "
            f"curl -s -X POST http://127.0.0.1:8000/backup/{endpoint}"
            f" >> /var/log/asguard/backup-cron.log 2>&1"
            f" # asguard_task:{task['id']}"
        )
        clean.append(line)
    crontab_content = "\n".join(clean)
    if clean:
        crontab_content += "\n"
    subprocess.run(["crontab", "-"], input=crontab_content, text=True, check=True)


def _list_backups_with_dates():
    result = []
    for d in _BACKUP_ROOT.iterdir():
        if not d.is_dir() or not d.name.startswith("backup_"):
            continue
        meta_file = d / "backup_metadata.json"
        dt = None
        if meta_file.exists():
            try:
                meta = json.loads(meta_file.read_text())
                raw = meta.get("created_at", "")
                from datetime import timezone as _tz
                dt = datetime.fromisoformat(raw)
                if dt.tzinfo is not None:
                    dt = dt.astimezone(_tz.utc).replace(tzinfo=None)
            except Exception:
                pass
        if dt is None:
            try:
                parts = d.name.split("_")
                for i, p in enumerate(parts):
                    if len(p) == 10 and p.count("-") == 2:
                        ts = parts[i + 1] if i + 1 < len(parts) else "00-00-00"
                        dt = datetime.fromisoformat(f"{p}T{ts.replace('-', ':')}")
                        break
            except Exception:
                pass
        if dt:
            result.append((d, dt))
    return sorted(result, key=lambda x: x[1], reverse=True)


def _apply_gfs_retention(retention):
    now = datetime.utcnow()
    recent_hours = int(retention.get("recent_keep_hours", 24))
    daily_days = int(retention.get("daily_keep_days", 7))
    weekly_weeks = int(retention.get("weekly_keep_weeks", 4))
    monthly_months = int(retention.get("monthly_keep_months", 6))
    max_total = int(retention.get("max_total", 30))
    min_free_gb = float(retention.get("min_free_gb", 5))

    backups = _list_backups_with_dates()
    keep = set()

    if backups:
        keep.add(backups[0][0])

    t_recent = now - timedelta(hours=recent_hours)
    t_daily = now - timedelta(days=daily_days)
    t_weekly = now - timedelta(weeks=weekly_weeks)
    t_monthly = now - timedelta(days=monthly_months * 30)

    daily_seen, weekly_seen, monthly_seen = set(), set(), set()

    for d, dt in backups:
        if dt >= t_recent:
            keep.add(d)
        elif dt >= t_daily:
            key = dt.strftime("%Y-%m-%d")
            if key not in daily_seen:
                daily_seen.add(key)
                keep.add(d)
        elif dt >= t_weekly:
            key = f"{dt.year}-W{dt.isocalendar()[1]:02d}"
            if key not in weekly_seen:
                weekly_seen.add(key)
                keep.add(d)
        elif dt >= t_monthly:
            key = dt.strftime("%Y-%m")
            if key not in monthly_seen:
                monthly_seen.add(key)
                keep.add(d)

    if len(keep) > max_total:
        dt_map = {d: dt for d, dt in backups}
        sorted_keep = sorted(keep, key=lambda x: dt_map.get(x, datetime.min), reverse=True)
        keep = set(sorted_keep[:max_total])

    stat = shutil.disk_usage(str(_BACKUP_ROOT))
    free_gb = stat.free / (1024 ** 3)
    if free_gb < min_free_gb and len(keep) > 1:
        for d, _ in reversed(backups):
            if free_gb >= min_free_gb or len(keep) <= 1:
                break
            if d in keep:
                try:
                    freed = sum(f.stat().st_size for f in d.rglob("*") if f.is_file()) / (1024 ** 3)
                    keep.discard(d)
                    free_gb += freed
                except Exception:
                    pass

    to_delete = [d for d, _ in backups if d not in keep]
    deleted = []
    for d in to_delete:
        try:
            size_gb = round(sum(f.stat().st_size for f in d.rglob("*") if f.is_file()) / (1024 ** 3), 3)
            shutil.rmtree(str(d))
            deleted.append({"name": d.name, "size_gb": size_gb})
        except Exception as exc:
            logger.warning("Could not delete backup %s: %s", d, exc)

    return {"kept": len(keep), "deleted": deleted, "total_deleted": len(deleted)}


@swagger_auto_schema("GET", responses={200: "OK"}, operation_summary="GET BACKUP SCHEDULE & RETENTION CONFIG")
@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def get_schedule(request):
    config = _read_schedule_config()
    _queue_due_schedule_catchups(config)
    backups = _list_backups_with_dates()
    total_size = 0
    for d, _ in backups:
        try:
            total_size += sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
        except Exception:
            pass
    stat = shutil.disk_usage(str(_BACKUP_ROOT))
    return JsonResponse({
        "tasks": config.get("tasks", []),
        "retention": {**DEFAULT_RETENTION, **config.get("retention", {})},
        "stats": {
            "total_backups": len(backups),
            "total_size_gb": round(total_size / (1024 ** 3), 2),
            "free_gb": round(stat.free / (1024 ** 3), 1),
            "total_gb": round(stat.total / (1024 ** 3), 1),
        },
        "last_retention_applied": config.get("last_retention_applied"),
    })


@swagger_auto_schema("POST", responses={200: "OK"}, operation_summary="CREATE OR UPDATE SCHEDULED TASK")
@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def save_schedule_task(request):
    import uuid
    data = request.data
    task_id = data.get("id")
    config = _read_schedule_config()
    tasks = config.get("tasks", [])
    if task_id:
        updated = False
        for i, t in enumerate(tasks):
            if t["id"] == task_id:
                tasks[i] = {**t, **data, "updated_at": datetime.utcnow().isoformat()}
                updated = True
                break
        if not updated:
            return JsonResponse({"error": "Task not found"}, status=404)
    else:
        tasks.append({
            **data,
            "id": f"task_{uuid.uuid4().hex[:8]}",
            "created_at": datetime.utcnow().isoformat(),
            "enabled": data.get("enabled", True),
        })
    config["tasks"] = tasks
    _write_schedule_config(config)
    try:
        _sync_crontab(tasks)
    except Exception as exc:
        logger.warning("Crontab sync failed: %s", exc)
    return JsonResponse({"status": "ok", "tasks": tasks})


@swagger_auto_schema("POST", responses={200: "OK"}, operation_summary="RUN SCHEDULED BACKUP TASK")
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def run_scheduled_task(request, task_id):
    config = _read_schedule_config()
    task = next((item for item in config.get("tasks", []) if item.get("id") == task_id), None)
    if not task:
        return JsonResponse({"status": "error", "message": "Task not found."}, status=404)
    if not task.get("enabled", True):
        return JsonResponse({"status": "error", "message": "Task disabled."}, status=400)
    _mark_scheduled_task_queued(task, reason="scheduled_run")
    task["last_queued_for"] = datetime.now().replace(second=0, microsecond=0).isoformat()
    _write_schedule_config(config)
    _execute_scheduled_task(task_id)
    refreshed = _read_schedule_config()
    updated = next((item for item in refreshed.get("tasks", []) if item.get("id") == task_id), task)
    status_code = 200 if updated.get("last_run_status") in {"ok", "success"} else 207
    return JsonResponse({"status": updated.get("last_run_status", "ok"), "task": updated}, status=status_code)


@swagger_auto_schema("DELETE", responses={200: "OK"}, operation_summary="DELETE SCHEDULED TASK")
@api_view(["DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def delete_schedule_task(request, task_id):
    config = _read_schedule_config()
    tasks = [t for t in config.get("tasks", []) if t["id"] != task_id]
    config["tasks"] = tasks
    _write_schedule_config(config)
    try:
        _sync_crontab(tasks)
    except Exception as exc:
        logger.warning("Crontab sync failed: %s", exc)
    return JsonResponse({"status": "ok", "tasks": tasks})


@swagger_auto_schema("PUT", responses={200: "OK"}, operation_summary="UPDATE RETENTION POLICY")
@api_view(["PUT"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def update_retention(request):
    data = request.data
    config = _read_schedule_config()
    config["retention"] = {**DEFAULT_RETENTION, **data}
    _write_schedule_config(config)
    return JsonResponse({"status": "ok", "retention": config["retention"]})


@swagger_auto_schema("POST", responses={200: "OK"}, operation_summary="APPLY GFS RETENTION NOW")
@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def apply_retention_now(request):
    config = _read_schedule_config()
    retention = {**DEFAULT_RETENTION, **config.get("retention", {})}
    result = _apply_gfs_retention(retention)
    config["last_retention_applied"] = datetime.utcnow().isoformat()
    _write_schedule_config(config)
    return JsonResponse({"status": "ok", **result})


# ─────────────────────────────────────────────────────────────────────────────

@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def import_backup(request):
    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return JsonResponse({"status": "error", "message": "No file uploaded."}, status=400)

    result = ExportImportService.import_backup(uploaded_file)
    status_code = 200 if result.get("status") == "success" else 400
    return JsonResponse(result, status=status_code)


# ── Cloud Storage API ──────────────────────────────────────────────────────────

@api_view(["GET", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def cloud_config(request):
    """GET: return current cloud config. POST: save cloud config."""
    from backend.backup.models import CloudStorageConfig

    if request.method == "GET":
        cfg = CloudStorageConfig.objects.first()
        if not cfg:
            return JsonResponse({"configured": False})
        return JsonResponse({
            "configured":             True,
            "id":                     cfg.pk,
            "provider":               cfg.provider,
            "endpoint_url":           cfg.endpoint_url,
            "access_key_id":          cfg.access_key_id,
            "secret_access_key":      "••••••••",
            "bucket_name":            cfg.bucket_name,
            "region":                 cfg.region,
            "prefix":                 cfg.prefix,
            "enabled":                cfg.enabled,
            "auto_upload":            cfg.auto_upload,
            "upload_db_only_to_cloud": cfg.upload_db_only_to_cloud,
            "max_cloud_copies":       cfg.max_cloud_copies,
        })

    # POST — save config
    data = request.data if hasattr(request, "data") else json.loads(request.body)
    cfg  = CloudStorageConfig.objects.first() or CloudStorageConfig()
    cfg.provider        = data.get("provider", "backblaze_b2")
    cfg.endpoint_url    = data.get("endpoint_url", "")
    cfg.access_key_id   = data.get("access_key_id", "")
    cfg.bucket_name     = data.get("bucket_name", "")
    cfg.region          = data.get("region", "us-east-1")
    cfg.prefix          = data.get("prefix", "asguard-backups/")
    cfg.enabled         = bool(data.get("enabled", True))
    cfg.auto_upload     = bool(data.get("auto_upload", True))
    cfg.upload_db_only_to_cloud = bool(data.get("upload_db_only_to_cloud", False))
    cfg.max_cloud_copies = int(data.get("max_cloud_copies", 10))
    # only update secret if provided (not masked)
    secret = data.get("secret_access_key", "")
    if secret and secret != "••••••••":
        cfg.secret_access_key = secret
    cfg.save()
    return JsonResponse({"status": "ok", "id": cfg.pk})


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def cloud_test(request):
    """Test connection to the configured cloud bucket."""
    from backend.backup.models import CloudStorageConfig

    cfg = CloudStorageConfig.objects.filter(enabled=True).first()
    if not cfg:
        return JsonResponse({"ok": False, "message": "No cloud storage configured."}, status=400)
    result = CloudStorageService(cfg).test_connection()
    status = 200 if result["ok"] else 400
    return JsonResponse(result, status=status)


@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def cloud_list(request):
    """List all backups currently stored in the cloud bucket."""
    from backend.backup.models import CloudStorageConfig

    cfg = CloudStorageConfig.objects.filter(enabled=True).first()
    if not cfg:
        return JsonResponse({"ok": False, "backups": [], "message": "No cloud storage configured."})
    backups = CloudStorageService(cfg).list_cloud_backups()
    return JsonResponse({"ok": True, "backups": backups, "count": len(backups)})


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def cloud_sync(request, backup_id):
    """Manually push a local backup to cloud."""
    from backend.backup.models import CloudStorageConfig, BackupRecord
    from django.utils import timezone as tz

    cfg = CloudStorageConfig.objects.filter(enabled=True).first()
    if not cfg:
        return JsonResponse({"ok": False, "message": "No cloud storage configured."}, status=400)

    backup_dir = _BACKUP_ROOT / backup_id
    if not backup_dir.exists():
        return JsonResponse({"ok": False, "message": f"Backup {backup_id} not found locally."}, status=404)

    service = CloudStorageService(cfg)
    result  = service.upload_backup_folder(backup_id, backup_dir)

    if result.get("ok"):
        BackupRecord.objects.filter(backup_id=backup_id).update(
            cloud_uploaded=True,
            cloud_provider=cfg.provider,
            cloud_bucket=cfg.bucket_name,
            cloud_key=result.get("key", ""),
            cloud_size_mb=result.get("size_mb"),
            cloud_uploaded_at=tz.now(),
            cloud_error="",
        )

    return JsonResponse(result)


@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def cloud_backup_history(request):
    """Return backup history from DB (BackupRecord)."""
    from backend.backup.models import BackupRecord

    records = BackupRecord.objects.all()[:50]
    return JsonResponse({"records": [r.to_dict() for r in records]})
