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
from backend.backup.notifications import (
    notify_backup_started,
    notify_backup_completed,
    notify_backup_scheduled,
    notify_missed_backup_catchup,
    notify_restore_completed,
    notify_vm_resource_risk,
    notify_vm_resource_resolved,
)
from backend.backup.observability import append_backup_event, read_backup_events
from backend.backup.risk_ai import analyze_vm_and_services
from backend.backup.system_backup.cloud_storage import CloudStorageService

from django.http import JsonResponse, FileResponse
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """SessionAuthentication that does NOT enforce CSRF.

    The backup import endpoint is an AllowAny multipart upload; DRF's default
    SessionAuthentication still runs CSRF enforcement for an authenticated
    session, and the browser's multipart upload doesn't carry a usable CSRF
    token → every import returned HTTP 403. Skipping CSRF here is safe: the
    endpoint is already AllowAny and lives behind the appliance's auth UI.
    """

    def enforce_csrf(self, request):
        return  # no CSRF check for this endpoint
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
RESOURCE_RISK_STATE_FILE = Path("/var/log/asguard/resource_risk_notify.json")
IN_APP_ALERTS_FILE = Path("/var/backups/asguard/in_app_alerts.json")

RESTORE_JOBS_DIR = BACKUP_DIR / "restore_jobs"
BACKUP_JOBS_DIR = BACKUP_DIR / "backup_jobs"
SYNC_SUMMARY_CACHE_FILE = BACKUP_DIR / "dashboard_last_sync_summary.json"
FULL_RESTORE_RUNNER = Path("/asguard/asguard/full_restore_runner.py")
PYTHON_BIN = "/usr/bin/python"
_LAST_DASHBOARD_SYNC_SUMMARY = None
_BACKUP_RESULTS_CACHE = {"expires_at": 0.0, "results": None}
_DASHBOARD_SERVICES_CACHE = {"expires_at": 0.0, "services": None}
_DASHBOARD_OVERVIEW_CACHE = {}
_CACHE_LOCK = threading.RLock()
BACKUP_RESULTS_CACHE_SECONDS = 8
DASHBOARD_SERVICES_CACHE_SECONDS = 8
DASHBOARD_OVERVIEW_CACHE_SECONDS = 4

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
    now = time.time()
    with _CACHE_LOCK:
        cached = _BACKUP_RESULTS_CACHE.get("results")
        if cached is not None and now < float(_BACKUP_RESULTS_CACHE.get("expires_at", 0)):
            return list(cached)

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
    with _CACHE_LOCK:
        _BACKUP_RESULTS_CACHE["results"] = list(results)
        _BACKUP_RESULTS_CACHE["expires_at"] = time.time() + BACKUP_RESULTS_CACHE_SECONDS
    return results


def _invalidate_backup_results_cache() -> None:
    with _CACHE_LOCK:
        _BACKUP_RESULTS_CACHE["results"] = None
        _BACKUP_RESULTS_CACHE["expires_at"] = 0.0
        _DASHBOARD_OVERVIEW_CACHE.clear()


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


def _write_backup_job_state(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, path)


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


def _db_port_reachable() -> bool:
    """Truthful 'is the database up' check.

    On this appliance PostgreSQL runs inside the `app-db-container` Docker
    container, NOT as a systemd unit — so `systemctl is-active postgresql` is
    always "inactive" and would wrongly flag the database as down in the drift
    scan. A reachable DB port is the real signal. Uses the Django DB settings
    so it stays correct if host/port change.
    """
    import socket
    from django.conf import settings
    db = settings.DATABASES.get("default", {})
    host = db.get("HOST") or "127.0.0.1"
    if host in ("", "localhost"):
        host = "127.0.0.1"
    try:
        port = int(db.get("PORT") or 5432)
    except (TypeError, ValueError):
        port = 5432
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except OSError:
        return False


def _load_dashboard_services() -> list[dict]:
    now = time.time()
    with _CACHE_LOCK:
        cached = _DASHBOARD_SERVICES_CACHE.get("services")
        if cached is not None and now < float(_DASHBOARD_SERVICES_CACHE.get("expires_at", 0)):
            return list(cached)

    try:
        info = json.loads(get_system_infomations())
        services = []
        seen_names: set[str] = set()
        for item in info.get("list_info_services", []):
            parsed = json.loads(item)
            name = parsed.get("service_name")
            if not name or name in seen_names:
                continue
            running = bool(parsed.get("status_started"))
            # "ipsec" is a legacy alias: there is no `ipsec` systemd unit, the
            # real IPsec daemon is `strongswan`. So the DB row is always probed
            # as stopped and showed a false drift even while IPsec is up. If
            # strongswan is active, the IPsec service IS running.
            if not running and name == "ipsec":
                sw_out, _, sw_code = _run_readonly_command(
                    ["systemctl", "is-active", "strongswan"], timeout=8)
                if sw_code == 0 and sw_out.strip() == "active":
                    running = True
            services.append({
                "name": name,
                "label": parsed.get("description") or name,
                "description": parsed.get("description") or f"Service {name}",
                "enabled": bool(parsed.get("status_enabled")),
                "running": running,
                "installed": bool(parsed.get("status_install")),
                "manageable": True,
                "kind": "service",
                "category": "application",
                "status_detail": "running" if running else "stopped",
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

            # PostgreSQL runs in Docker (app-db-container), not via systemd, so
            # the is-active check above always reports it stopped. Trust the
            # actual DB port instead — otherwise the drift scan shows a scary
            # (and false) "Base de données arrêtée".
            if service_def["key"] == "postgresql" and _db_port_reachable():
                resolved_name = resolved_name or "postgresql"
                if state is None:
                    state = {"enabled": True, "installed": True}
                state["running"] = True
                state.setdefault("installed", True)

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
        with _CACHE_LOCK:
            _DASHBOARD_SERVICES_CACHE["services"] = list(services)
            _DASHBOARD_SERVICES_CACHE["expires_at"] = time.time() + DASHBOARD_SERVICES_CACHE_SECONDS
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


# Structural / non-rule lines in `nft list ruleset` output — never counted
# as duplicate "rules" because they legitimately repeat across chains.
_NFT_STRUCTURAL_PREFIXES = (
    "table ", "chain ", "set ", "map ", "element", "type ", "policy ",
    "comment ", "flags ", "elements ", "}", "{",
)


def _detect_nft_duplicates(table_filter: str | None = None) -> list[dict]:
    """
    Parse `nft list ruleset` and report rule lines that appear more than
    once inside the SAME chain — the kernel-side duplication bug.

    `nft -f` only ADDS rules; a restore that reloads a config without a
    prior `nft flush ruleset` leaves N copies of every rule. A substring
    "is the rule present?" check cannot see this — the rule IS present,
    just N times. This helper counts occurrences per (table, chain, line)
    so the sync analysis can flag real duplication.

    `table_filter` (e.g. "nat") restricts the scan to tables whose
    declaration line contains that keyword; None scans every table.

    Returns a list of drift dicts ready to append to a sync module.
    """
    stdout, stderr, code = _run_readonly_command(["nft", "list", "ruleset"], timeout=10)
    if code != 0 or not stdout:
        # Retry with sudo — nft often needs root to read the ruleset.
        stdout, stderr, code = _run_readonly_command(
            ["sudo", "-n", "nft", "list", "ruleset"], timeout=10
        )
        if code != 0 or not stdout:
            return []

    drifts: list[dict] = []
    current_table = ""
    current_chain = ""
    # {(table, chain): {rule_line: count}}
    seen: dict[tuple[str, str], dict[str, int]] = {}

    for raw in stdout.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("table "):
            current_table = line[len("table "):].rstrip(" {").strip()
            current_chain = ""
            continue
        if line.startswith("chain "):
            current_chain = line[len("chain "):].rstrip(" {").strip()
            continue
        if line.startswith(_NFT_STRUCTURAL_PREFIXES):
            continue
        if not current_chain:
            continue
        if table_filter and table_filter.lower() not in current_table.lower():
            continue
        # Drop the trailing "# handle N" so identical rules with different
        # kernel handles still compare equal.
        rule_line = line.split("# handle", 1)[0].strip()
        if not rule_line:
            continue
        bucket = seen.setdefault((current_table, current_chain), {})
        bucket[rule_line] = bucket.get(rule_line, 0) + 1

    for (table, chain), bucket in seen.items():
        for rule_line, count in bucket.items():
            if count > 1:
                drifts.append({
                    "kind": "rule_duplicated",
                    "label": f"{chain}: {rule_line[:60]}",
                    "detail": (
                        f"Regle presente {count}x dans la chaine '{chain}' "
                        f"(table {table}) — duplication noyau detectee. "
                        f"Attendu: 1 occurrence. Cause probable: rechargement "
                        f"`nft -f` sans `nft flush ruleset` prealable lors d'une restauration."
                    ),
                })
    return drifts


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

    # Kernel-side duplication check restricted to the `nat` table.
    for dup in _detect_nft_duplicates(table_filter="nat"):
        drifts.append(dup)

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

    # Kernel-side duplication check — catches the "restore reloaded the
    # ruleset without flushing it" bug that a substring presence check
    # above can never detect. Skip the dedicated `nat` table (covered by
    # _scan_nat_sync) so each drift is reported by exactly one module.
    for dup in _detect_nft_duplicates():
        if "table nat" in dup.get("detail", "").lower():
            continue
        drifts.append(dup)
        entities.append({
            "label": dup["label"],
            "status": "drift",
            "detail": "duplication noyau",
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


# Sustained-pressure thresholds. The frontend (TheHeading.vue) polls
# /backup/dashboard-overview every 30 s, so each streak tick ≈ 30 s. A signal
# must stay above its line for RESOURCE_RISK_REQUIRED_STREAK consecutive
# polls before we fire a notification. This kills the "spike → instant alert
# → score back to 17/100" false-positive loop. Single-sample spikes are
# visible in the UI but no longer page the operator.
RESOURCE_RISK_POLL_SECONDS = 30
RESOURCE_RISK_REQUIRED_STREAK = 4        # ~2 min sustained
RESOURCE_RISK_CRITICAL_CPU = 95          # %
RESOURCE_RISK_HIGH_CPU = 92              # %
RESOURCE_RISK_CRITICAL_MEM = 95          # %
RESOURCE_RISK_HIGH_MEM = 92              # %
# Resolution hysteresis: how many consecutive polls with no alert before we
# declare the incident resolved. Without this, a brief CPU dip from 100→91→100
# triggers a "résolu" notification then a fresh critical alert seconds later —
# flapping that spams the operator.
RESOURCE_RISK_RESOLVE_STREAK = 3         # ~1m30s sustained calm
# Global cooldown: minimum interval between two alerts of any kind. Even if
# incident_active was cleared (flapping safety net), do not re-page within
# this window.
RESOURCE_RISK_GLOBAL_COOLDOWN = 600      # 10 min


def _resource_risk_alert(live_metrics: dict) -> dict | None:
    """Detect a *sustained* resource-pressure condition.

    Single-sample spikes never escalate to an alert: each tick we either
    increment or reset a per-signal streak counter stored in
    RESOURCE_RISK_STATE_FILE. Only when the streak crosses
    RESOURCE_RISK_REQUIRED_STREAK do we return an alert payload. As soon as
    the metric drops back below the high threshold the streak is reset to 0,
    so a brief overload that comes back down on its own stays silent.
    """
    cpu = float(live_metrics.get("cpu_percentage") or 0)
    memory = float(live_metrics.get("memory_percentage") or 0)
    try:
        load1 = float(str(live_metrics.get("load_average", "")).split(",")[0].strip())
    except Exception:
        load1 = 0.0
    cores = max(psutil.cpu_count() or 1, 1)

    try:
        state = json.loads(RESOURCE_RISK_STATE_FILE.read_text()) if RESOURCE_RISK_STATE_FILE.exists() else {}
    except Exception:
        state = {}
    streaks = state.get("streaks") or {"cpu": 0, "memory": 0, "load": 0}

    def _tick(key: str, pressed: bool) -> int:
        new_val = int(streaks.get(key, 0)) + 1 if pressed else 0
        streaks[key] = new_val
        return new_val

    cpu_streak = _tick("cpu", cpu >= RESOURCE_RISK_HIGH_CPU)
    mem_streak = _tick("memory", memory >= RESOURCE_RISK_HIGH_MEM)
    load_streak = _tick("load", load1 >= cores * 2)

    state["streaks"] = streaks
    try:
        RESOURCE_RISK_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        RESOURCE_RISK_STATE_FILE.write_text(json.dumps(state, indent=2))
    except Exception:
        pass

    def _fmt_duration(streak: int) -> str:
        secs = streak * RESOURCE_RISK_POLL_SECONDS
        if secs < 60:
            return f"{secs}s"
        return f"{secs // 60}min{secs % 60:02d}s" if secs % 60 else f"{secs // 60}min"

    reasons = []
    critical = False
    if cpu_streak >= RESOURCE_RISK_REQUIRED_STREAK:
        label = "critique" if cpu >= RESOURCE_RISK_CRITICAL_CPU else "eleve"
        reasons.append(f"CPU {label} {cpu:.0f}% depuis {_fmt_duration(cpu_streak)}")
        critical = critical or cpu >= RESOURCE_RISK_CRITICAL_CPU
    if mem_streak >= RESOURCE_RISK_REQUIRED_STREAK:
        label = "critique" if memory >= RESOURCE_RISK_CRITICAL_MEM else "elevee"
        reasons.append(f"RAM {label} {memory:.0f}% depuis {_fmt_duration(mem_streak)}")
        critical = critical or memory >= RESOURCE_RISK_CRITICAL_MEM
    if load_streak >= RESOURCE_RISK_REQUIRED_STREAK:
        reasons.append(
            f"Load {load1:.2f} pour {cores} vCPU depuis {_fmt_duration(load_streak)}"
        )
        critical = critical or load1 >= cores * 2.5

    if not reasons:
        return None

    return {
        "severity": "critical" if critical else "warning",
        "time": datetime.now().isoformat(),
        "service": "vmware-vm",
        "message": "Surcharge soutenue — risque d'instabilite VM",
        "cause": " ; ".join(reasons),
        "action": None,
        "action_label": "",
    }


def _collect_top_processes(limit: int = 5) -> list[dict]:
    """Snapshot of the top resource consumers. Sorted by CPU+RAM combined,
    so a process that's hammering either dimension surfaces."""
    procs = []
    try:
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                info = p.info
                procs.append({
                    "pid": info.get("pid"),
                    "name": info.get("name") or "?",
                    "cpu": float(info.get("cpu_percent") or 0.0),
                    "mem": float(info.get("memory_percent") or 0.0),
                })
            except Exception:
                continue
    except Exception:
        return []
    procs.sort(key=lambda p: (p["cpu"] + p["mem"]), reverse=True)
    return procs[:limit]


def _attempt_resource_auto_fix(alert: dict, live_metrics: dict) -> str:
    """Try a safe auto-remediation matching the alert cause. Returns a
    human-readable summary of what was done (or empty string when nothing
    safe is available — we never kill processes automatically).

    Currently implemented:
      • RAM ≥ 92%  → drop page/inode/dentry caches (always safe, just frees
                     reclaimable memory; never affects running processes).
    For CPU/Load no auto-fix is safe — we only diagnose.
    """
    cause = (alert.get("cause") or "").lower()
    memory = float(live_metrics.get("memory_percentage") or 0)

    if "ram" in cause and memory >= RESOURCE_RISK_HIGH_MEM:
        try:
            before = subprocess.check_output(
                ["bash", "-c", "free -m | awk '/^Mem:/ {print $7}'"],
                text=True, timeout=5,
            ).strip()
            subprocess.run(
                ["bash", "-c", "sync; echo 3 > /proc/sys/vm/drop_caches"],
                capture_output=True, text=True, timeout=10, check=False,
            )
            after = subprocess.check_output(
                ["bash", "-c", "free -m | awk '/^Mem:/ {print $7}'"],
                text=True, timeout=5,
            ).strip()
            try:
                freed = int(after) - int(before)
                return (f"Caches RAM purgés — {freed} MB libérés "
                        f"(disponible {before} → {after} MB)")
            except ValueError:
                return "Caches RAM purgés (sync + drop_caches)"
        except Exception as exc:
            return f"Tentative de purge caches échouée: {exc}"

    return ""


def _build_recommendation(alert: dict, top_processes: list[dict]) -> str:
    """One-line, operator-actionable recommendation derived from the alert
    cause and the live diagnostic. Designed to be readable from a phone
    notification — no jargon, includes a concrete next step."""
    cause = (alert.get("cause") or "").lower()
    top = top_processes[0] if top_processes else None
    top_label = (f"{top['name']} (PID {top['pid']}, CPU {top['cpu']:.0f}%, "
                 f"RAM {top['mem']:.0f}%)") if top else "le processus dominant"

    if "cpu" in cause and "ram" in cause:
        return (f"Système saturé sur deux axes. Identifier {top_label} et "
                f"`kill -15 {top['pid'] if top else '<PID>'}` si non critique, "
                f"sinon augmenter les vCPU/RAM de la VM.")
    if "cpu" in cause:
        return (f"Vérifier {top_label}. Si non critique → "
                f"`kill -15 {top['pid'] if top else '<PID>'}`. "
                f"Sinon → augmenter les vCPU de la VM.")
    if "ram" in cause:
        return ("Caches déjà purgés automatiquement. Si la RAM reste haute, "
                f"surveiller {top_label} (fuite mémoire probable).")
    if "load" in cause:
        return ("Charge I/O ou processus bloquants. Vérifier disque saturé "
                "(`iostat -x 2`) ou attente network.")
    return f"Investiguer {top_label} et libérer la ressource saturée."


def _maybe_notify_resource_risk(alert: dict | None, live_metrics: dict):
    """Main alerting loop. Four responsibilities:
      1. On NEW sustained alert: gather diagnostic, attempt safe auto-fix,
         fire enriched notification, persist incident state.
      2. While the incident is ongoing: stay silent (throttle).
      3. Anti-flapping: when pressure briefly drops, do NOT immediately
         declare resolution — require RESOURCE_RISK_RESOLVE_STREAK consecutive
         clear polls. This prevents the "alert → 1s later résolu → 30s later
         alert again" cycle caused by a micro-dip in raw cpu_percent.
      4. On confirmed resolution: fire a "back to normal" follow-up.

    Also enforces a global cooldown so even if state corruption clears
    incident_active, two alerts can't fire within RESOURCE_RISK_GLOBAL_COOLDOWN.
    """
    now = time.time()
    try:
        state = json.loads(RESOURCE_RISK_STATE_FILE.read_text()) if RESOURCE_RISK_STATE_FILE.exists() else {}
    except Exception:
        state = {}

    incident_active = bool(state.get("incident_active"))
    clear_streak = int(state.get("clear_streak", 0))

    # --- No current alert ---
    if not alert:
        if not incident_active:
            # Already calm, nothing to do. Reset clear_streak so it doesn't
            # grow indefinitely.
            if clear_streak != 0:
                state["clear_streak"] = 0
                _safe_write_state(state)
            return

        # Incident was active but this poll is clean. Increment the calm
        # streak — only fire the "résolu" notification once it crosses the
        # hysteresis threshold (no flapping).
        clear_streak += 1
        state["clear_streak"] = clear_streak
        if clear_streak < RESOURCE_RISK_RESOLVE_STREAK:
            _safe_write_state(state)
            return

        # Confirmed resolution
        started_at = float(state.get("incident_started_at") or now)
        duration = max(0, int(now - started_at))
        reason = state.get("incident_cause") or "Surcharge ressources"
        auto_fix = state.get("incident_auto_fix") or ""
        state["incident_active"] = False
        state["incident_resolved_at"] = now
        state["clear_streak"] = 0
        _safe_write_state(state)
        threading.Thread(
            target=notify_vm_resource_resolved,
            args=(reason, duration, auto_fix),
            daemon=True,
        ).start()
        return

    # --- Alert present: reset clear_streak (any new alert breaks the calm) ---
    if clear_streak:
        state["clear_streak"] = 0

    # --- Throttle: same incident, don't re-alert ---
    throttle_seconds = 1800 if alert.get("severity") == "critical" else 3600
    if incident_active and (now - float(state.get("last_sent", 0)) < throttle_seconds):
        _safe_write_state(state)
        return

    # --- Global cooldown: even if incident_active was cleared, refuse to
    #     re-page within the cooldown window. Prevents flap-induced spam.
    if (now - float(state.get("last_sent", 0))) < RESOURCE_RISK_GLOBAL_COOLDOWN:
        _safe_write_state(state)
        return

    # --- New incident: diagnose, auto-fix, alert ---
    top_processes = _collect_top_processes(limit=5)
    auto_fix = _attempt_resource_auto_fix(alert, live_metrics)
    recommendation = _build_recommendation(alert, top_processes)

    state["last_sent"] = now
    state["alert"] = alert
    state["incident_active"] = True
    state["incident_cause"] = alert.get("cause") or ""
    state["incident_auto_fix"] = auto_fix
    if not state.get("incident_started_at") or not incident_active:
        state["incident_started_at"] = now
    _safe_write_state(state)

    threading.Thread(
        target=notify_vm_resource_risk,
        args=(
            float(live_metrics.get("cpu_percentage") or 0),
            float(live_metrics.get("memory_percentage") or 0),
            live_metrics.get("load_average") or "",
            alert.get("cause") or "Risque d'instabilite VM",
            top_processes,
            auto_fix,
            recommendation,
        ),
        daemon=True,
    ).start()


def _safe_write_state(state: dict) -> None:
    try:
        RESOURCE_RISK_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        RESOURCE_RISK_STATE_FILE.write_text(json.dumps(state, indent=2))
    except Exception:
        pass


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


def _build_dashboard_alerts(backups: list[dict], services: list[dict], live_metrics: dict | None = None) -> list[dict]:
    alerts: list[dict] = []

    resource_alert = _resource_risk_alert(live_metrics or {})
    if resource_alert:
        alerts.append(resource_alert)

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


# ═════════════════════════════════════════════════════════════════════════════
#  SECTION: DASHBOARD & RISK AI  — overview, risk analysis, ping, metrics
# ═════════════════════════════════════════════════════════════════════════════
@swagger_auto_schema("GET", responses={200: "OK"}, operation_summary="BACKUP DASHBOARD OVERVIEW")
@api_view(["GET"])
@require_http_methods(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def get_dashboard_overview(request):
    selected_components = _parse_selected_sync_components(request)
    skip_sync_scan = str(request.GET.get("skip_sync_scan", "")).lower() in {"1", "true", "yes"}
    cache_key = (
        "skip" if skip_sync_scan else "scan",
        tuple(selected_components or []),
    )
    now = time.time()
    if skip_sync_scan:
        with _CACHE_LOCK:
            cached = _DASHBOARD_OVERVIEW_CACHE.get(cache_key)
            if cached and now < cached.get("expires_at", 0):
                return JsonResponse(cached["payload"])

    schedule_config = _read_schedule_config()
    _queue_due_schedule_catchups(schedule_config)
    backups = _collect_backup_results()
    services = _load_dashboard_services()
    if skip_sync_scan:
        sync_summary = _load_cached_sync_summary(selected_components) or _build_idle_sync_summary(selected_components)
    else:
        sync_summary = _build_global_sync_summary(services, selected_components)
        _save_cached_sync_summary(sync_summary)
    live_metrics = _get_live_metrics()
    alerts = _build_dashboard_alerts(backups, services, live_metrics)
    _maybe_notify_resource_risk(_resource_risk_alert(live_metrics), live_metrics)

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
    notif_configured = False
    try:
        wd = Path("/etc/asguard/watchdog_config.json")
        if wd.exists():
            wd_cfg = json.loads(wd.read_text()).get("notifications", {})
            ntfy  = wd_cfg.get("ntfy", {})
            email = wd_cfg.get("email", {})
            notif_configured = bool(
                (ntfy.get("enabled") and ntfy.get("topic")) or
                (email.get("enabled") and email.get("recipients"))
            )
    except Exception:
        pass

    auto_backup_on = any(t.get("enabled", True) for t in schedule_config.get("tasks", []))

    payload = {
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
        "notifications_configured": notif_configured,
        "auto_backup_on": auto_backup_on,
    }
    if skip_sync_scan:
        with _CACHE_LOCK:
            _DASHBOARD_OVERVIEW_CACHE[cache_key] = {
                "payload": payload,
                "expires_at": time.time() + DASHBOARD_OVERVIEW_CACHE_SECONDS,
            }
    return JsonResponse(payload)


RISK_ACTIONS = {
    "cpu_top": {
        "kind": "safe",
        "title": "Top 15 processus CPU",
        "cmd": ["bash", "-c", "ps -eo pid,user,pcpu,pmem,comm --sort=-pcpu | head -16"],
    },
    "ram_top": {
        "kind": "safe",
        "title": "Top 15 processus RAM",
        "cmd": ["bash", "-c", "ps -eo pid,user,pcpu,pmem,comm --sort=-pmem | head -16"],
    },
    "load_top": {
        "kind": "safe",
        "title": "Charge système — top processus",
        "cmd": ["bash", "-c", "uptime; echo; ps -eo pid,user,pcpu,pmem,stat,comm --sort=-pcpu | head -16"],
    },
    "disk_usage": {
        "kind": "safe",
        "title": "Utilisation disque par dossier",
        "cmd": ["bash", "-c", "df -h /; echo; du -sh /var/log /var/backups /tmp /var/cache 2>/dev/null"],
    },
    "services_status": {
        "kind": "safe",
        "title": "Services en échec",
        "cmd": ["bash", "-c", "systemctl --failed --no-legend --no-pager; echo; systemctl list-units --state=failed --no-legend --no-pager"],
    },
    "services_restart": {
        "kind": "intrusive",
        "title": "Redémarrer les services critiques arrêtés",
        # Best-effort restart of every unit currently in "failed" or inactive
        # state for our critical service candidates. We restart sequentially
        # and capture per-service status so the UI shows which came back.
        "internal": "services_restart",
    },
    "ram_caches": {
        "kind": "intrusive",
        "title": "Vider les caches page/inode/dentry",
        "cmd": ["bash", "-c", "BEFORE=$(free -m | awk '/^Mem:/ {print $7}'); sync; echo 3 > /proc/sys/vm/drop_caches; AFTER=$(free -m | awk '/^Mem:/ {print $7}'); echo \"Mémoire disponible avant: ${BEFORE} MB\"; echo \"Mémoire disponible après: ${AFTER} MB\"; echo \"Libéré: $((AFTER-BEFORE)) MB\""],
    },
    "disk_journal": {
        "kind": "intrusive",
        "title": "Purger les journaux systemd (> 7 jours)",
        "cmd": ["bash", "-c", "journalctl --vacuum-time=7d 2>&1 | tail -10"],
    },
    "snapshot_lvm": {
        "kind": "intrusive",
        "title": "Créer un snapshot LVM",
        "internal": "lvm_snapshot",
    },
}


def _run_risk_action(action_key: str) -> dict:
    spec = RISK_ACTIONS.get(action_key)
    if not spec:
        return {"ok": False, "error": "Action inconnue", "action": action_key}

    if spec.get("internal") == "lvm_snapshot":
        try:
            from backend.backup.system_backup.lvm_snapshot_service import LVMSnapshotService
            res = LVMSnapshotService.create_snapshot(description="AI Risk Center — point de restauration auto")
            ok = res.get("status") != "error"
            return {"ok": ok, "title": spec["title"], "kind": spec["kind"],
                    "action": action_key,
                    "output": json.dumps(res, indent=2, ensure_ascii=False)}
        except Exception as exc:
            return {"ok": False, "error": str(exc), "action": action_key,
                    "title": spec["title"], "kind": spec["kind"]}

    if spec.get("internal") == "services_restart":
        lines = []
        any_ok = False
        try:
            services = _load_dashboard_services()
        except Exception as exc:
            return {"ok": False, "error": f"Impossible de lister les services: {exc}",
                    "action": action_key, "title": spec["title"], "kind": spec["kind"]}

        # Restart every service flagged as not running. Limit to the critical
        # candidates so we never touch random user units.
        critical_keys = {sd["key"] for sd in CRITICAL_SERVICE_CANDIDATES}
        critical_names = set()
        for sd in CRITICAL_SERVICE_CANDIDATES:
            for cand in sd["candidates"]:
                critical_names.add(cand.replace(".service", ""))

        failing = [s for s in services if not s.get("running")
                   and (s.get("name") in critical_names or s.get("key") in critical_keys)]
        if not failing:
            return {"ok": True, "title": spec["title"], "kind": spec["kind"],
                    "action": action_key,
                    "output": "Aucun service critique en panne — rien à redémarrer."}

        try:
            from backend.backup.notifications import notify_service_action
        except Exception:
            notify_service_action = None

        for svc in failing:
            unit = svc.get("name")
            label = svc.get("label") or unit
            try:
                proc = subprocess.run(
                    ["systemctl", "restart", unit],
                    capture_output=True, text=True, timeout=25,
                )
                success = proc.returncode == 0
                any_ok = any_ok or success
                lines.append(f"[{('OK' if success else 'KO')}] {label} ({unit})"
                             + (f" — {proc.stderr.strip()}" if proc.stderr else ""))
                if notify_service_action:
                    try:
                        notify_service_action(unit, "restart", success, display_name=label)
                    except Exception:
                        pass
            except subprocess.TimeoutExpired:
                lines.append(f"[KO] {label} ({unit}) — timeout 25s")
            except Exception as exc:
                lines.append(f"[KO] {label} ({unit}) — {exc}")

        return {
            "ok": any_ok,
            "title": spec["title"],
            "kind": spec["kind"],
            "action": action_key,
            "output": "\n".join(lines),
        }

    try:
        proc = subprocess.run(spec["cmd"], capture_output=True, text=True, timeout=20)
        output = (proc.stdout or "") + (("\n[stderr]\n" + proc.stderr) if proc.stderr else "")
        return {
            "ok": proc.returncode == 0,
            "title": spec["title"],
            "kind": spec["kind"],
            "action": action_key,
            "exit_code": proc.returncode,
            "output": output.strip() or "(aucune sortie)",
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Action expirée (timeout 20s)", "action": action_key,
                "title": spec["title"], "kind": spec["kind"]}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "action": action_key,
                "title": spec["title"], "kind": spec["kind"]}


@swagger_auto_schema("POST", responses={200: "OK"}, operation_summary="RUN AI RISK ACTION")
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def run_risk_action(request, action_key: str):
    # No DB-backed authentication here: the AI Risk Center exists precisely to
    # diagnose situations where PostgreSQL itself may be down. SessionAuthentication
    # would query django_session and block the whole worker when the DB is gone.
    spec = RISK_ACTIONS.get(action_key)
    if not spec:
        return JsonResponse({"ok": False, "error": "Action inconnue"}, status=404)
    if spec["kind"] == "intrusive":
        confirm = None
        try:
            confirm = json.loads(request.body or b"{}").get("confirm")
        except Exception:
            confirm = None
        if not confirm:
            return JsonResponse({"ok": False, "error": "Confirmation requise",
                                 "needs_confirm": True, "title": spec["title"],
                                 "kind": spec["kind"]}, status=400)
    result = _run_risk_action(action_key)
    return JsonResponse(result)


@swagger_auto_schema("GET", responses={200: "OK"}, operation_summary="AI RISK ANALYSIS")
@api_view(["GET"])
@require_http_methods(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def get_risk_ai_analysis(request):
    services = _load_dashboard_services()
    live_metrics = _get_live_metrics()
    history = _load_monitoring_history(limit=80)
    try:
        root_total, root_used, _ = shutil.disk_usage("/")
        root_usage = round((root_used / root_total) * 100) if root_total else 0
    except Exception:
        root_usage = 0

    latest_backup = (_collect_backup_results() or [None])[0]
    backup_risk = 0
    if latest_backup:
        backup_risk = 100 - int(latest_backup.get("health_score", 100) or 100)
        if latest_backup.get("overall_status") in {"error", "failed"}:
            backup_risk = 95
        elif latest_backup.get("overall_status") == "partial":
            backup_risk = max(backup_risk, 70)

    return JsonResponse(
        analyze_vm_and_services(
            history_points=history,
            live_metrics=live_metrics,
            services=services,
            root_disk_usage=root_usage,
            backup_risk=backup_risk,
        )
    )


@swagger_auto_schema("GET", responses={200: "OK"}, operation_summary="PING BACKUP MODULE")
@api_view(["GET"])
@require_http_methods(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def ping(request):
    return JsonResponse({"status": "ok", "module": "backup"})


def _restore_history_entries_for_metrics() -> list[dict]:
    entries = []
    RESTORE_JOBS_DIR.mkdir(parents=True, exist_ok=True)
    for state_file in RESTORE_JOBS_DIR.glob("*.json"):
        try:
            payload = json.loads(state_file.read_text(encoding="utf-8"))
            entries.append(payload)
        except Exception:
            continue
    return entries


def _build_backup_metrics_payload() -> dict:
    backups = _collect_backup_results()
    schedule_config = _read_schedule_config()
    services = _load_dashboard_services()
    restore_entries = _restore_history_entries_for_metrics()

    now = datetime.now()
    latest_backup = backups[0] if backups else None
    latest_dt = _safe_parse_iso_datetime(latest_backup.get("modified_at") if latest_backup else None)
    rpo_hours = None
    if latest_dt:
        try:
            rpo_hours = round((datetime.now(latest_dt.tzinfo) - latest_dt).total_seconds() / 3600, 2)
        except Exception:
            rpo_hours = None

    total_backups = len(backups)
    successful_backups = sum(1 for item in backups if item.get("overall_status") == "ok")
    degraded_backups = sum(1 for item in backups if item.get("overall_status") == "partial")
    failed_backups = sum(1 for item in backups if item.get("overall_status") in {"error", "failed"})
    success_rate = round((successful_backups / total_backups) * 100, 2) if total_backups else 0

    restore_total = len(restore_entries)
    restore_success = sum(1 for item in restore_entries if item.get("status") == "success")
    restore_failed = sum(1 for item in restore_entries if item.get("status") not in {"success", "partial_success", "running", "queued"})
    restore_durations = [
        _duration_seconds_between(item.get("started_at"), item.get("finished_at"))
        for item in restore_entries
    ]
    restore_durations = [value for value in restore_durations if value > 0]

    backup_disk_total, backup_disk_used, backup_disk_free = shutil.disk_usage(BACKUP_DIR)
    root_disk_total, root_disk_used, root_disk_free = shutil.disk_usage("/")
    enabled_tasks = [task for task in schedule_config.get("tasks", []) if task.get("enabled", True)]
    next_task = _get_next_scheduled_task(schedule_config.get("tasks", []), _get_schedule_tz(schedule_config))
    failing_services = [service for service in services if not service.get("running")]

    return {
        "status": "ok",
        "generated_at": datetime.now().isoformat(),
        "rpo": {
            "hours": rpo_hours,
            "status": "unknown" if rpo_hours is None else ("ok" if rpo_hours <= 24 else "warning" if rpo_hours <= 48 else "critical"),
        },
        "backups": {
            "total": total_backups,
            "successful": successful_backups,
            "degraded": degraded_backups,
            "failed": failed_backups,
            "success_rate": success_rate,
            "average_health": round(sum(int(item.get("health_score", 0) or 0) for item in backups) / total_backups, 2) if total_backups else 0,
            "latest": {
                "id": latest_backup.get("id") if latest_backup else None,
                "status": latest_backup.get("overall_status") if latest_backup else "missing",
                "health_score": latest_backup.get("health_score", 0) if latest_backup else 0,
                "timestamp": latest_backup.get("modified_at") if latest_backup else None,
                "size_bytes": latest_backup.get("size_bytes", 0) if latest_backup else 0,
            },
        },
        "restores": {
            "total": restore_total,
            "successful": restore_success,
            "failed": restore_failed,
            "success_rate": round((restore_success / restore_total) * 100, 2) if restore_total else 0,
            "avg_duration_seconds": round(sum(restore_durations) / len(restore_durations), 2) if restore_durations else 0,
        },
        "storage": {
            "backup_used_bytes": backup_disk_used,
            "backup_total_bytes": backup_disk_total,
            "backup_free_bytes": backup_disk_free,
            "backup_used_pct": round((backup_disk_used / backup_disk_total) * 100, 2) if backup_disk_total else 0,
            "root_used_bytes": root_disk_used,
            "root_total_bytes": root_disk_total,
            "root_free_bytes": root_disk_free,
            "root_used_pct": round((root_disk_used / root_disk_total) * 100, 2) if root_disk_total else 0,
        },
        "schedule": {
            "tasks_total": len(schedule_config.get("tasks", [])),
            "tasks_enabled": len(enabled_tasks),
            "auto_backup_on": bool(enabled_tasks),
            "next_run": next_task.get("next_run") if next_task else None,
            "next_task": next_task,
            "last_retention_applied": schedule_config.get("last_retention_applied"),
        },
        "services": {
            "total": len(services),
            "running": len(services) - len(failing_services),
            "failing": len(failing_services),
            "failing_names": [service.get("name") for service in failing_services[:12]],
        },
        "events": {
            "recent": read_backup_events(limit=20, since_hours=24),
        },
    }


def _prometheus_metrics(payload: dict) -> str:
    lines = [
        "# HELP asguard_backup_rpo_hours Hours since the latest known backup.",
        "# TYPE asguard_backup_rpo_hours gauge",
        f"asguard_backup_rpo_hours {payload['rpo']['hours'] if payload['rpo']['hours'] is not None else -1}",
        "# HELP asguard_backup_total Number of known local backups.",
        "# TYPE asguard_backup_total gauge",
        f"asguard_backup_total {payload['backups']['total']}",
        "# HELP asguard_backup_success_rate Backup success rate percent.",
        "# TYPE asguard_backup_success_rate gauge",
        f"asguard_backup_success_rate {payload['backups']['success_rate']}",
        "# HELP asguard_backup_latest_health Latest backup health score.",
        "# TYPE asguard_backup_latest_health gauge",
        f"asguard_backup_latest_health {payload['backups']['latest']['health_score']}",
        "# HELP asguard_restore_success_rate Restore success rate percent.",
        "# TYPE asguard_restore_success_rate gauge",
        f"asguard_restore_success_rate {payload['restores']['success_rate']}",
        "# HELP asguard_backup_storage_used_pct Backup storage usage percent.",
        "# TYPE asguard_backup_storage_used_pct gauge",
        f"asguard_backup_storage_used_pct {payload['storage']['backup_used_pct']}",
        "# HELP asguard_backup_schedule_enabled_tasks Enabled scheduled backup tasks.",
        "# TYPE asguard_backup_schedule_enabled_tasks gauge",
        f"asguard_backup_schedule_enabled_tasks {payload['schedule']['tasks_enabled']}",
        "# HELP asguard_backup_services_failing Failing services visible from backup dashboard.",
        "# TYPE asguard_backup_services_failing gauge",
        f"asguard_backup_services_failing {payload['services']['failing']}",
    ]
    return "\n".join(lines) + "\n"


@swagger_auto_schema("GET", responses={200: "OK"}, operation_summary="BACKUP DRP METRICS")
@api_view(["GET"])
@require_http_methods(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def get_backup_metrics(request):
    payload = _build_backup_metrics_payload()
    if str(request.GET.get("output", "")).lower() in {"prometheus", "prom"}:
        from django.http import HttpResponse
        return HttpResponse(_prometheus_metrics(payload), content_type="text/plain; version=0.0.4")
    return JsonResponse(payload)


@swagger_auto_schema("GET", responses={200: "OK"}, operation_summary="BACKUP DRP PROMETHEUS METRICS")
@api_view(["GET"])
@require_http_methods(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def get_backup_metrics_prometheus(request):
    from django.http import HttpResponse
    return HttpResponse(
        _prometheus_metrics(_build_backup_metrics_payload()),
        content_type="text/plain; version=0.0.4",
    )


@swagger_auto_schema("GET", responses={200: "OK"}, operation_summary="BACKUP OBSERVABILITY EVENTS")
@api_view(["GET"])
@require_http_methods(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def get_backup_events(request):
    try:
        limit = int(request.GET.get("limit", 200))
    except Exception:
        limit = 200
    since_hours = request.GET.get("since_hours")
    try:
        since_hours = int(since_hours) if since_hours else None
    except Exception:
        since_hours = None
    events = read_backup_events(limit=limit, since_hours=since_hours)
    return JsonResponse({"count": len(events), "results": events})


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


# ═════════════════════════════════════════════════════════════════════════════
#  SECTION: BACKUP CREATION  — db / full / safe / custom backup endpoints
# ═════════════════════════════════════════════════════════════════════════════
@swagger_auto_schema("POST", responses={200: "OK"}, operation_summary="CREATE DATABASE BACKUP (LEGACY)")
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def create_db_backup(request):
    threading.Thread(target=notify_backup_started, args=("db_backup",), daemon=True).start()
    append_backup_event(kind="backup", title="DB backup started", severity="info", status="running", source="api")
    result = SystemBackupService.create_db_backup()
    _invalidate_backup_results_cache()
    ok = result.get("status") == "ok"
    backup_id = result.get("backup_id") or Path(result.get("file", "")).stem
    threading.Thread(target=notify_backup_completed, args=("db_backup", backup_id, ok), daemon=True).start()
    CloudStorageService.async_upload_after_backup(backup_id, None, "db_backup", result)
    append_backup_event(
        kind="backup",
        title="DB backup completed" if ok else "DB backup failed",
        severity="success" if ok else "error",
        status="success" if ok else "error",
        source="api",
        ref_id=backup_id,
        detail=result.get("message", ""),
        extra={"backup_type": "db_backup", "file": result.get("file", "")},
    )
    return JsonResponse(result)


@swagger_auto_schema("POST", responses={200: "OK"}, operation_summary="CREATE FULL BACKUP (DISASTER RECOVERY)")
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def create_full_backup(request):
    from datetime import timezone as _tz
    from zoneinfo import ZoneInfo as _ZI
    _local_tz = _ZI("Africa/Tunis")
    ts = datetime.now(_local_tz).strftime("%Y-%m-%d_%H-%M-%S")
    job_id = f"backup_{ts}"
    job_file = BACKUP_JOBS_DIR / f"{job_id}.json"
    started_at = datetime.now(_tz.utc).isoformat()

    _write_backup_job_state(job_file, {
        "job_id": job_id,
        "backup_type": "full",
        "status": "running",
        "started_at": started_at,
        "finished_at": None,
        "components_progress": {},
        "current_component": None,
        "progress_pct": 0,
        "done": 0,
        "total": 0,
        "result": None,
    })

    def _make_cb():
        def _cb(progress):
            try:
                try:
                    with open(job_file, "r", encoding="utf-8") as _f:
                        current = json.load(_f)
                except Exception:
                    current = {}
                current.update(progress)
                _write_backup_job_state(job_file, current)
            except Exception:
                pass
        return _cb

    def _run():
        from datetime import timezone as _tz2
        try:
            threading.Thread(target=notify_backup_started, args=("full_backup",), daemon=True).start()
            append_backup_event(kind="backup", title="Full backup started", severity="info", status="running", source="api", ref_id=job_id)
            result = FullBackupService.create_full_backup(progress_callback=_make_cb())
            ok = result.get("status") in {"ok", "partial"}
            backup_id_result = result.get("backup_id", job_id)
            components_progress = {n: d.get("status", "unknown") for n, d in (result.get("components") or {}).items()}
            try:
                with open(job_file, "r", encoding="utf-8") as _f:
                    current = json.load(_f)
            except Exception:
                current = {}
            current.update({
                "job_id": job_id,
                "backup_id": backup_id_result,
                "backup_type": "full",
                "status": "success" if ok else "error",
                "started_at": started_at,
                "finished_at": datetime.now(_tz2.utc).isoformat(),
                "progress_pct": 100,
                "components_progress": components_progress,
                "result": result,
            })
            _write_backup_job_state(job_file, current)
            _invalidate_backup_results_cache()
            threading.Thread(target=notify_backup_completed, args=("full_backup", backup_id_result, ok), daemon=True).start()
            CloudStorageService.async_upload_after_backup(backup_id_result, result.get("backup_dir"), "full_backup", result)
            append_backup_event(
                kind="backup",
                title="Full backup completed" if ok else "Full backup failed",
                severity="success" if result.get("status") == "ok" else ("warning" if ok else "error"),
                status=current["status"],
                source="api",
                ref_id=backup_id_result,
                detail=result.get("message", ""),
                extra={"job_id": job_id, "backup_type": "full_backup", "summary": result.get("summary", {})},
            )
        except Exception as exc:
            import traceback
            try:
                with open(job_file, "r", encoding="utf-8") as _f:
                    current = json.load(_f)
            except Exception:
                current = {}
            current.update({
                "job_id": job_id,
                "backup_type": "full",
                "status": "error",
                "started_at": started_at,
                "finished_at": datetime.now(_tz2.utc).isoformat(),
                "result": {"message": str(exc), "traceback": traceback.format_exc()},
            })
            _write_backup_job_state(job_file, current)
            append_backup_event(
                kind="backup",
                title="Full backup failed",
                severity="error",
                status="error",
                source="api",
                ref_id=job_id,
                detail=str(exc),
                extra={"job_id": job_id},
            )

    threading.Thread(target=_run, daemon=True).start()
    return JsonResponse({"status": "queued", "job_id": job_id, "message": "Backup démarré en arrière-plan."}, status=202)


@swagger_auto_schema("POST", responses={200: "OK"}, operation_summary="CREATE SAFE BACKUP (ADMIN UI)")
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def create_safe_backup(request):
    from datetime import timezone as _tz
    from zoneinfo import ZoneInfo as _ZI
    _local_tz = _ZI("Africa/Tunis")
    ts = datetime.now(_local_tz).strftime("%Y-%m-%d_%H-%M-%S")
    job_id = f"backup_safe_{ts}"
    job_file = BACKUP_JOBS_DIR / f"{job_id}.json"
    started_at = datetime.now(_tz.utc).isoformat()

    _write_backup_job_state(job_file, {
        "job_id": job_id,
        "backup_type": "safe",
        "status": "running",
        "started_at": started_at,
        "finished_at": None,
        "components_progress": {},
        "current_component": None,
        "progress_pct": 0,
        "done": 0,
        "total": 0,
        "result": None,
    })
    append_backup_event(kind="backup", title="Full backup queued", severity="info", status="queued", source="api", ref_id=job_id)

    def _make_cb():
        def _cb(progress):
            try:
                try:
                    with open(job_file, "r", encoding="utf-8") as _f:
                        current = json.load(_f)
                except Exception:
                    current = {}
                current.update(progress)
                _write_backup_job_state(job_file, current)
            except Exception:
                pass
        return _cb

    def _run():
        from datetime import timezone as _tz2
        try:
            threading.Thread(target=notify_backup_started, args=("safe_backup",), daemon=True).start()
            append_backup_event(kind="backup", title="Safe backup started", severity="info", status="running", source="api", ref_id=job_id)
            result = FullBackupService.create_safe_backup(progress_callback=_make_cb())
            ok = result.get("status") in {"ok", "partial"}
            backup_id_result = result.get("backup_id", job_id)
            components_progress = {n: d.get("status", "unknown") for n, d in (result.get("components") or {}).items()}
            try:
                with open(job_file, "r", encoding="utf-8") as _f:
                    current = json.load(_f)
            except Exception:
                current = {}
            current.update({
                "job_id": job_id,
                "backup_id": backup_id_result,
                "backup_type": "safe",
                "status": "success" if ok else "error",
                "started_at": started_at,
                "finished_at": datetime.now(_tz2.utc).isoformat(),
                "progress_pct": 100,
                "components_progress": components_progress,
                "result": result,
            })
            _write_backup_job_state(job_file, current)
            _invalidate_backup_results_cache()
            threading.Thread(target=notify_backup_completed, args=("safe_backup", backup_id_result, ok), daemon=True).start()
            CloudStorageService.async_upload_after_backup(backup_id_result, result.get("backup_dir"), "safe_backup", result)
            append_backup_event(
                kind="backup",
                title="Safe backup completed" if ok else "Safe backup failed",
                severity="success" if result.get("status") == "ok" else ("warning" if ok else "error"),
                status=current["status"],
                source="api",
                ref_id=backup_id_result,
                detail=result.get("message", ""),
                extra={"job_id": job_id, "backup_type": "safe_backup", "summary": result.get("summary", {})},
            )
        except Exception as exc:
            import traceback
            try:
                with open(job_file, "r", encoding="utf-8") as _f:
                    current = json.load(_f)
            except Exception:
                current = {}
            current.update({
                "job_id": job_id,
                "backup_type": "safe",
                "status": "error",
                "started_at": started_at,
                "finished_at": datetime.now(_tz2.utc).isoformat(),
                "result": {"message": str(exc), "traceback": traceback.format_exc()},
            })
            _write_backup_job_state(job_file, current)
            append_backup_event(
                kind="backup",
                title="Safe backup failed",
                severity="error",
                status="error",
                source="api",
                ref_id=job_id,
                detail=str(exc),
                extra={"job_id": job_id},
            )

    threading.Thread(target=_run, daemon=True).start()
    append_backup_event(kind="backup", title="Safe backup queued", severity="info", status="queued", source="api", ref_id=job_id)
    return JsonResponse({"status": "queued", "job_id": job_id, "message": "Backup démarré en arrière-plan."}, status=202)


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

    threading.Thread(target=notify_backup_started, args=("custom_backup",), daemon=True).start()
    result = FullBackupService.create_custom_backup(components)
    _invalidate_backup_results_cache()
    status_code = 200 if result["status"] == "ok" else (400 if result["status"] == "error" else 207)
    append_backup_event(
        kind="backup",
        title="Custom backup completed" if result.get("status") in {"ok", "partial"} else "Custom backup failed",
        severity="success" if result.get("status") == "ok" else ("warning" if result.get("status") == "partial" else "error"),
        status=result.get("status", "unknown"),
        source="api",
        ref_id=result.get("backup_id", ""),
        detail=result.get("message", ""),
        extra={"backup_type": "custom", "components": components, "summary": result.get("summary", {})},
    )
    # Push/email notification — custom backups were previously silent.
    _ok = result.get("status") in {"ok", "partial"}
    threading.Thread(
        target=notify_backup_completed,
        args=("custom_backup", result.get("backup_id", ""), _ok),
        kwargs={"message": f"Composants : {', '.join(components)}"},
        daemon=True,
    ).start()
    return JsonResponse(result, status=status_code)


# ═════════════════════════════════════════════════════════════════════════════
#  SECTION: BACKUP LISTING  — list backups, component catalog, details
# ═════════════════════════════════════════════════════════════════════════════
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


# ═════════════════════════════════════════════════════════════════════════════
#  SECTION: RESTORE  — safe / ui_full / custom restore, preview, history
# ═════════════════════════════════════════════════════════════════════════════
# Restore behaviour model:
#   • "Safe"  (this endpoint)        → UI-safe: only the Asguard system config
#       (firewall, VPN, IDS, proxy, network, NAT…). Leaves the OS, the app code
#       and the machine identity untouched → the web UI never drops.
#   • "Full"  (restore_full_backup)  → COMPLETE: the whole VM, application code
#       included. Runs in a detached systemd unit that restarts uvicorn at the
#       end (so hot-rewriting the code is safe). It still PRESERVES the host
#       identity — the target keeps its own IP (NetworkManager profiles) and its
#       own /etc/fstab, and on a VM without the 2nd LVM disk the LVM mounts are
#       stripped (native mode). See restore_service.py _HOST_IDENTITY_EXCLUDES
#       and _reconcile_fstab_native.
@swagger_auto_schema("POST", responses={202: "Accepted"}, operation_summary="SAFE RESTORE (UI-SAFE — ASGUARD SYSTEM ONLY)")
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def restore_backup(request, backup_id):
    return _launch_detached_restore(backup_id=backup_id, mode="ui_full")


@swagger_auto_schema("POST", responses={202: "Accepted"}, operation_summary="FULL RESTORE (COMPLETE — WHOLE VM)")
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def restore_full_backup(request, backup_id):
    return _launch_detached_restore(backup_id=backup_id, mode="complete")


# ── Pre-restore preview ──────────────────────────────────────────────────────
# Static metadata that explains why some components are intentionally excluded
# from the UI-safe restore. Surfaced both to the operator (decision support
# in the confirmation modal) and to the eventual sales pitch ("Asguard tells
# you what it will and won't touch before doing anything").
_UI_FULL_EXCLUSION_REASONS = {
    "application":      ("Code de l'application (/asguard/asguard)",
                         "Réécrire à chaud le code Python pendant qu'uvicorn tourne "
                         "ferait crasher l'interface. Restauration possible uniquement "
                         "en mode DR offline (script asguard-dr-restore en console)."),
    "system_config":    ("Configuration /etc système globale",
                         "Contient hostname, fstab, locale, sudoers — un restore à chaud "
                         "couperait votre session SSH/web. Mode DR offline uniquement."),
    "systemd_services": ("Unit files systemd custom",
                         "Un daemon-reload massif provoque un timeout D-Bus qui gèle le "
                         "système plusieurs minutes. Mode DR offline uniquement."),
    "users_groups":     ("Comptes Linux (uvicorn, postgres)",
                         "Les utilisateurs applicatifs Asguard sont restaurés via la DB. "
                         "Les comptes système Linux ne doivent jamais bouger à chaud."),
    "packages":         ("Liste des paquets RPM/DEB installés",
                         "Liste sauvegardée pour DR. L'installation des paquets manquants "
                         "se fait uniquement en mode console (peut bloquer dépendances)."),
    "docker_state":     ("Images et volumes Docker",
                         "Recréer les containers à chaud redémarre PostgreSQL — perte de "
                         "connexion garantie. Mode DR offline uniquement."),
    "logs":             ("Logs historiques /var/log",
                         "Données forensiques sans valeur opérationnelle pour un restore "
                         "à chaud. Restaurées en mode DR seulement si besoin d'audit."),
    "vm_snapshot":      ("Métadonnées de snapshot LVM",
                         "Géré via l'onglet VM Snapshot dédié — pas inclus dans ce backup."),
}


@swagger_auto_schema("GET", responses={200: "OK", 404: "Not Found"},
                     operation_summary="RESTORE PREVIEW (UI-SAFE)")
@api_view(["GET"])
@require_http_methods(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def restore_preview(request, backup_id):
    """Return what would happen if the user clicks 'Restore' on this backup.
    Splits every component into three buckets:

      - included : will be restored (config-only or DB-backed)
      - excluded : explicitly skipped for safety (engine components)
      - missing  : present in the backup but with no restore handler

    Each entry carries a `reason` (for excluded) or `size_mb` so the operator
    can make an informed decision. Pure read-only — no side effects.
    """
    import os
    from pathlib import Path
    import json as _json

    from backend.backup.system_backup.restore_service import RestoreService

    backup_dir = Path(_BACKUP_ROOT) / backup_id
    if not backup_dir.exists():
        return JsonResponse(
            {"status": "error", "message": f"Backup '{backup_id}' introuvable"},
            status=404,
        )

    meta_file = backup_dir / "backup_metadata.json"
    if not meta_file.exists():
        return JsonResponse(
            {"status": "error", "message": "backup_metadata.json manquant"},
            status=400,
        )
    try:
        meta = _json.loads(meta_file.read_text(encoding="utf-8"))
    except Exception as exc:
        return JsonResponse(
            {"status": "error", "message": f"Lecture metadata: {exc}"},
            status=500,
        )

    components_meta = meta.get("components", {})
    excluded_set   = RestoreService.UI_FULL_EXCLUDED_COMPONENTS

    # ── Per-component DB inventory ──────────────────────────────────────────
    # For every data-driven component we read its component_db.json
    # (counts written at backup time) and compare those numbers against
    # the current live DB. This is what produces the "5 NAT DNAT in
    # backup vs 7 currently — 2 will be deleted" preview the operator sees.
    try:
        from backend.backup.component_db import (
            COMPONENT_MODELS, MODEL_LABELS, DB_SNAPSHOT_FILENAME, _resolve_model,
        )
    except Exception:
        COMPONENT_MODELS, MODEL_LABELS, DB_SNAPSHOT_FILENAME, _resolve_model = (
            {}, {}, "component_db.json", lambda _p: None,
        )

    def _read_backup_counts(component: str) -> dict:
        snap = backup_dir / component / DB_SNAPSHOT_FILENAME
        if not snap.exists():
            return {}
        try:
            data = _json.loads(snap.read_text(encoding="utf-8"))
            return data.get("counts", {}) or {}
        except Exception:
            return {}

    def _current_db_counts(component: str) -> dict:
        out = {}
        for path in COMPONENT_MODELS.get(component, []):
            Model = _resolve_model(path)
            if Model is None:
                continue
            try:
                out[path] = Model.objects.count()
            except Exception:
                out[path] = None
        return out

    def _component_inventory(component: str) -> list[dict]:
        """Per-model rows ready to render in the preview table."""
        backup_counts = _read_backup_counts(component)
        current_counts = _current_db_counts(component)
        all_paths = list(dict.fromkeys(
            list(COMPONENT_MODELS.get(component, [])) + list(backup_counts.keys())
        ))
        rows = []
        for path in all_paths:
            in_backup = backup_counts.get(path)
            current = current_counts.get(path)
            # Delta = how the live DB count will move once restored.
            # Only meaningful when both sides are known integers.
            if isinstance(in_backup, int) and isinstance(current, int):
                delta = in_backup - current
            else:
                delta = None
            rows.append({
                "model":     path,
                "label":     MODEL_LABELS.get(path, path),
                "in_backup": in_backup,
                "current":   current,
                "delta":     delta,
            })
        return rows

    included: list[dict] = []
    excluded: list[dict] = []
    for name, comp in components_meta.items():
        size_mb = float(comp.get("size_mb", 0) or 0)
        if name in excluded_set:
            label, reason = _UI_FULL_EXCLUSION_REASONS.get(
                name, (name, "Composant moteur — restore offline uniquement.")
            )
            excluded.append({
                "name":    name,
                "label":   label,
                "size_mb": round(size_mb, 3),
                "reason":  reason,
                "status":  comp.get("status", "?"),
            })
        else:
            inventory = _component_inventory(name)
            total_in_backup = sum(
                r["in_backup"] for r in inventory if isinstance(r["in_backup"], int)
            )
            total_current = sum(
                r["current"] for r in inventory if isinstance(r["current"], int)
            )
            included.append({
                "name":             name,
                "size_mb":          round(size_mb, 3),
                "status":           comp.get("status", "?"),
                "inventory":        inventory,
                "total_in_backup":  total_in_backup,
                "total_current":    total_current,
                "has_db_inventory": bool(inventory),
            })

    # Contrôle d'intégrité signé : un backup altéré ne doit jamais être
    # restauré tel quel. Lecture seule, n'empêche pas l'aperçu de répondre.
    try:
        from backend.backup.integrity import verify_manifest
        integrity = verify_manifest(backup_dir)
    except Exception as exc:
        integrity = {"status": "error", "message": f"Vérification impossible: {exc}"}

    included.sort(key=lambda c: -c["size_mb"])
    excluded.sort(key=lambda c: c["name"])

    total_included_mb = round(sum(c["size_mb"] for c in included), 2)
    total_excluded_mb = round(sum(c["size_mb"] for c in excluded), 2)

    return JsonResponse({
        "status":            "ok",
        "backup_id":         backup_id,
        "backup_type":       meta.get("backup_type") or (
            "full" if "application" in components_meta else "safe"
        ),
        "created_at":        meta.get("created_at", ""),
        "mode":              "ui_full",
        "included":          included,
        "excluded":          excluded,
        "counts": {
            "included": len(included),
            "excluded": len(excluded),
        },
        "total_included_mb": total_included_mb,
        "total_excluded_mb": total_excluded_mb,
        "integrity": integrity,
        "dr_hint": (
            "Pour restaurer aussi les composants moteur (clone complet d'appliance "
            "sur nouvelle VM), utilisez le script 'asguard-dr-restore' depuis la "
            "console TTY après redémarrage."
        ),
    })


@swagger_auto_schema("GET", responses={200: "OK", 404: "Not Found"},
                     operation_summary="VERIFY BACKUP INTEGRITY")
@api_view(["GET"])
@require_http_methods(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def verify_backup_integrity(request, backup_id):
    """Contrôle anti-falsification d'un backup.

    Recalcule l'empreinte SHA-256 de chaque fichier du backup et la compare au
    manifeste signé (HMAC) écrit à la création. Détecte : fichier altéré
    (ransomware/corruption), fichier manquant, fichier intrus, manifeste
    falsifié. Lecture seule — aucun effet de bord.
    """
    backup_dir = Path(_BACKUP_ROOT) / backup_id
    if not backup_dir.exists():
        return JsonResponse(
            {"status": "error", "message": f"Backup '{backup_id}' introuvable"},
            status=404,
        )
    try:
        from backend.backup.integrity import verify_manifest
        report = verify_manifest(backup_dir)
    except Exception as exc:
        return JsonResponse(
            {"status": "error", "message": f"Vérification impossible: {exc}"},
            status=500,
        )

    report["backup_id"] = backup_id
    return JsonResponse(report)


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
        payload = request.data if isinstance(request.data, dict) else {}
    except Exception:
        payload = {}

    components = payload.get("components", [])
    if not isinstance(components, list):
        return JsonResponse({"status": "error", "message": "components must be a list."}, status=400)

    started_at = datetime.now().isoformat()
    result = RestoreService.restore_components(backup_id, components)
    finished_at = datetime.now().isoformat()

    job_id = f"restore_custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{backup_id}"
    RESTORE_JOBS_DIR.mkdir(parents=True, exist_ok=True)
    state = {
        "job_id": job_id,
        "backup_id": backup_id,
        "mode": "custom_restore",
        "status": result.get("status"),
        "started_at": started_at,
        "finished_at": finished_at,
        "log_file": None,
        "result": result,
    }
    try:
        with open(RESTORE_JOBS_DIR / f"{job_id}.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception:
        pass

    status_code = 200 if result.get("status") in ("success", "partial_success") else 400
    append_backup_event(
        kind="restore",
        title="Custom restore completed" if status_code == 200 else "Custom restore failed",
        severity="success" if result.get("status") == "success" else ("warning" if result.get("status") == "partial_success" else "error"),
        status=result.get("status", "unknown"),
        source="api",
        ref_id=backup_id,
        detail=result.get("message", ""),
        extra={"job_id": job_id, "components": components, "summary": result.get("summary", {})},
    )
    # Push/email notification — custom restores were previously silent.
    _summary = result.get("summary", {}) or {}
    threading.Thread(
        target=notify_restore_completed,
        args=(backup_id, "custom", result.get("status") == "success"),
        kwargs={
            "components_ok":     _summary.get("success", 0),
            "components_failed": _summary.get("failed", 0),
        },
        daemon=True,
    ).start()
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
        "progress_pct": 0,
        "done": 0,
        "total": 0,
        "components_progress": {},
        "components_order": [],
        "current_component": None,
    }

    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(initial_state, f, indent=2)
    append_backup_event(
        kind="restore",
        title=f"{mode} restore queued",
        severity="warning",
        status="queued",
        source="api",
        ref_id=backup_id,
        extra={"job_id": job_id, "mode": mode},
    )

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
            append_backup_event(
                kind="restore",
                title=f"{mode} restore launch failed",
                severity="error",
                status="error",
                source="systemd-run",
                ref_id=backup_id,
                detail=launch.stdout.strip(),
                extra={"job_id": job_id, "unit_name": unit_name, "returncode": launch.returncode, "mode": mode},
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
        append_backup_event(
            kind="restore",
            title=f"{mode} restore started",
            severity="warning",
            status="running",
            source="systemd-run",
            ref_id=backup_id,
            detail=launch.stdout.strip(),
            extra={"job_id": job_id, "unit_name": unit_name, "mode": mode},
        )

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
        append_backup_event(
            kind="restore",
            title=f"{mode} restore launch failed",
            severity="error",
            status="error",
            source="systemd-run",
            ref_id=backup_id,
            detail=str(e),
            extra={"job_id": job_id, "mode": mode},
        )
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
                "type": "backup",
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
                # Row-level diff produced by backend/backup/restore_diff.py.
                # Persisted as result.diff at restore time. Surfaced here so
                # the Historique Restores view can render "rule X added,
                # rule Y removed" retroactively, not just live.
                "diff": result.get("diff") or None,
            })
        except Exception:
            logger.warning("Could not read restore job file %s", state_file.name)

    # LVM snapshot restores
    try:
        from backend.backup.system_backup.lvm_snapshot_service import LVMSnapshotService as _Svc
        _snap_jobs_dir = _Svc.JOBS_DIR
        if _snap_jobs_dir.exists():
            for snap_file in _snap_jobs_dir.glob("snap_restore_*.json"):
                try:
                    with open(snap_file, "r", encoding="utf-8") as f:
                        sp = json.load(f)
                    raw_status = sp.get("status", "unknown")
                    norm_status = "success" if raw_status == "done" else raw_status
                    sp_result = sp.get("result") or {}
                    entries.append({
                        # Frontend keeps the legacy 'vm_snapshot' type for
                        # filter compatibility — only the displayed label is
                        # changed to "LVM Snapshot".
                        "type": "vm_snapshot",
                        "job_id": sp.get("job_id"),
                        "backup_id": sp.get("snap_id"),
                        "snap_id": sp.get("snap_id"),
                        "mode": "vm_snapshot",
                        "status": norm_status,
                        "started_at": sp.get("started_at"),
                        "finished_at": sp.get("finished_at"),
                        "duration_seconds": _duration_seconds_between(
                            sp.get("started_at"), sp.get("finished_at")
                        ),
                        "message": sp.get("message", ""),
                        "error": sp.get("error", ""),
                        # Captured at restore-time in views_vm_snapshot.py.
                        "description": sp.get("description", ""),
                        "created_by": sp.get("created_by", ""),
                        "created_at": sp.get("snapshot_created_at", ""),
                        "phases": sp.get("phases", []),
                        # What the restore actually touched. These come from
                        # restore_snapshot's result dict — they are the proof
                        # of coverage shown in the detail panel.
                        "binds_restored":       sp_result.get("binds_restored",       []),
                        "services_restarted":   sp_result.get("services_restarted",   []),
                        "containers_restarted": sp_result.get("containers_restarted", []),
                        "snapshot_preserved":   sp_result.get("snapshot_preserved", False),
                        "recreated_snap_id":    sp_result.get("recreated_snap_id",  ""),
                        "restore_warning":      sp_result.get("warning",            ""),
                        # Content-level proof of rollback: list of
                        # {table,label,group,before,after,delta,changed} entries
                        # captured by lvm_snapshot_service.restore_snapshot().
                        "db_changes":               sp_result.get("db_changes", []),
                        "db_changes_total_delta":   sp_result.get("db_changes_total_delta", 0),
                        "db_changes_tables_touched":sp_result.get("db_changes_tables_touched", 0),
                        "summary": {
                            "success": 1 if norm_status == "success" else 0,
                            "failed": 1 if norm_status == "error" else 0,
                            "skipped": 0,
                        },
                        "components_detail": [],
                        "stabilization_status": None,
                        "slowest_components": [],
                        "log_file": None,
                    })
                except Exception:
                    pass
    except Exception:
        pass

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


@swagger_auto_schema("GET", responses={200: "OK"}, operation_summary="GET BACKUP JOB PROGRESS")
@api_view(["GET"])
@require_http_methods(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def get_backup_progress(request, job_id):
    job_file = BACKUP_JOBS_DIR / f"{job_id}.json"
    if not job_file.exists():
        return JsonResponse({"status": "error", "message": f"Backup job {job_id} not found."}, status=404)
    try:
        with open(job_file, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return JsonResponse(payload, status=200)
    except Exception as e:
        logger.exception("Failed to read backup job %s", job_id)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# ═════════════════════════════════════════════════════════════════════════════
#  SECTION: BACKUP LIFECYCLE  — delete, export
# ═════════════════════════════════════════════════════════════════════════════
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
        _invalidate_backup_results_cache()
        append_backup_event(
            kind="backup",
            title="Backup deleted",
            severity="warning",
            status="success",
            source="api",
            ref_id=backup_id,
        )
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


def _get_system_tz() -> str:
    """Return the system's IANA timezone name (e.g. 'Africa/Tunis')."""
    from pathlib import Path as _Path
    tz_file = _Path('/etc/timezone')
    if tz_file.exists():
        return tz_file.read_text().strip()
    link = _Path('/etc/localtime')
    if link.is_symlink():
        target = str(link.resolve())
        if '/zoneinfo/' in target:
            return target.split('/zoneinfo/')[-1]
    return 'UTC'


def _get_schedule_tz(config: dict) -> str:
    """Return the configured schedule timezone, falling back to system timezone."""
    return config.get("schedule_timezone") or _get_system_tz()


def _cron_local_to_utc(cron_expr: str, tz_name: str | None = None) -> str:
    """Convert a simple cron expression from a local timezone to UTC.

    Django sets TZ=UTC so datetime.now() returns UTC. Cronie uses the crontab's TZ=UTC
    header. This converts a simple 'minute hour dom month dow' expression so that
    cronie fires at the right UTC time to match the user's intended local time.
    Only handles numeric hour fields; complex expressions are returned unchanged.
    """
    try:
        from zoneinfo import ZoneInfo
        from datetime import datetime as _dt, timezone as _tzutc
        if not tz_name:
            tz_name = _get_system_tz()
        offset_secs = ZoneInfo(tz_name).utcoffset(_dt.now(_tzutc.utc)).total_seconds()
        offset_hours = int(offset_secs / 3600)
        if offset_hours == 0:
            return cron_expr
        parts = cron_expr.split()
        if len(parts) != 5:
            return cron_expr
        minute, hour, dom, month, dow = parts
        if not hour.isdigit():
            return cron_expr
        utc_hour = (int(hour) - offset_hours) % 24
        return f"{minute} {utc_hour} {dom} {month} {dow}"
    except Exception:
        return cron_expr


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


def _get_next_scheduled_task(tasks: list[dict], tz_name: str | None = None) -> dict | None:
    scheduled = []
    for task in tasks:
        if not task.get("enabled", True):
            continue
        next_run = _compute_cron_run(_cron_local_to_utc(task.get("cron", ""), tz_name))
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
    task_name = task.get("label", task.get("name", task_id))
    now = datetime.now().isoformat()

    if not runner:
        task["last_run_at"] = now
        task["last_run_status"] = "error"
        task["last_run_message"] = "Unknown backup task type."
        _write_schedule_config(config)
        append_backup_event(
            kind="schedule",
            title="Scheduled backup task failed",
            severity="error",
            status="error",
            source="scheduler",
            ref_id=task_id,
            detail="Unknown backup task type.",
            extra={"backup_type": backup_type, "task_name": task_name},
        )
        return

    # Non-daemon so notifications complete even if spawning thread exits
    t_started = threading.Thread(target=notify_backup_started, args=(backup_type,), daemon=False)
    t_scheduled = threading.Thread(target=notify_backup_scheduled, args=(task_name, backup_type, task.get("cron", "")), daemon=False)
    t_started.start()
    t_scheduled.start()

    t0 = time.monotonic()
    try:
        append_backup_event(
            kind="schedule",
            title="Scheduled backup task started",
            severity="info",
            status="running",
            source="scheduler",
            ref_id=task_id,
            extra={"backup_type": backup_type, "task_name": task_name},
        )
        result = runner()
        duration = time.monotonic() - t0
        task["last_run_at"] = now
        task["last_run_status"] = result.get("status", "ok")
        task["last_run_message"] = result.get("message", "")
        ok = result.get("status") in ("ok", "success", None)
        backup_id = result.get("backup_id", "")
        t_completed = threading.Thread(
            target=notify_backup_completed,
            args=(backup_type, backup_id, ok, duration, result.get("message", "")),
            daemon=False,
        )
        t_completed.start()
        CloudStorageService.async_upload_after_backup(backup_id, result.get("backup_dir"), backup_type, result)
        append_backup_event(
            kind="schedule",
            title="Scheduled backup task completed" if ok else "Scheduled backup task failed",
            severity="success" if ok else "error",
            status="success" if ok else "error",
            source="scheduler",
            ref_id=backup_id or task_id,
            detail=result.get("message", ""),
            extra={"task_id": task_id, "backup_type": backup_type, "duration_seconds": round(duration, 2)},
        )

        # Auto-apply GFS retention right after a successful scheduled backup.
        # Previously retention only ran when the operator clicked "Appliquer la
        # rétention" — meaning a long-running appliance would keep accumulating
        # backups indefinitely between manual clicks. The retention computation
        # is cheap (filesystem stat only) and the actual deletion is bounded by
        # the policy (keep N daily / N weekly / N monthly / absolute cap).
        if ok:
            try:
                retention_cfg = {**DEFAULT_RETENTION, **config.get("retention", {})}
                ret_result = _apply_gfs_retention(retention_cfg)
                deleted = ret_result.get("total_deleted", 0)
                config["last_retention_applied"] = datetime.utcnow().isoformat()
                if deleted:
                    append_backup_event(
                        kind="retention",
                        title="Backup retention applied (auto)",
                        severity="info",
                        status="success",
                        source="scheduler",
                        ref_id=task_id,
                        detail=f"{deleted} backup(s) deleted after scheduled run",
                        extra=ret_result,
                    )
            except Exception as ret_exc:
                # Retention failure must NOT mark the backup itself as failed.
                logger.warning("Auto-retention after task %s failed: %s", task_id, ret_exc)
    except Exception as exc:
        duration = time.monotonic() - t0
        logger.exception("Scheduled backup task %s failed", task_id)
        task["last_run_at"] = now
        task["last_run_status"] = "error"
        task["last_run_message"] = str(exc)
        t_completed = threading.Thread(
            target=notify_backup_completed,
            args=(backup_type, "", False, duration, str(exc)),
            daemon=False,
        )
        t_completed.start()
        append_backup_event(
            kind="schedule",
            title="Scheduled backup task failed",
            severity="error",
            status="error",
            source="scheduler",
            ref_id=task_id,
            detail=str(exc),
            extra={"backup_type": backup_type, "task_name": task_name, "duration_seconds": round(duration, 2)},
        )
    _write_schedule_config(config)


def _mark_scheduled_task_queued(task: dict, *, reason: str):
    task["last_queued_at"] = datetime.now().isoformat()
    task["last_queue_reason"] = reason


def _start_scheduled_task_thread(task_id: str):
    thread = threading.Thread(target=_execute_scheduled_task, args=(task_id,), daemon=True)
    thread.start()


# How long after a scheduled slot we wait before the page-load/startup fallback
# treats it as missed. Must comfortably exceed the cron retry window (~5 min)
# plus the longest backup duration so we never race a run that fired on time.
_MISSED_RUN_GRACE = timedelta(minutes=15)

# Off-LV marker written by LVMSnapshotService.restore_snapshot for the duration
# of a merge. While it is present the data volume (backups + schedule_config)
# is mid-rollback, so every past slot looks "missed" — we must NOT catch up or
# we flood the operator with bogus backups + "Sauvegarde manquée" alerts.
_LVM_RESTORE_LOCK     = Path("/var/lib/asguard/lvm/.restore_in_progress")
_RESTORE_LOCK_MAX_AGE = timedelta(minutes=30)


def _lvm_restore_in_progress() -> bool:
    """True while an LVM snapshot restore is merging the volume. Auto-expires so
    a crashed restore can never wedge the scheduler permanently."""
    try:
        age = time.time() - _LVM_RESTORE_LOCK.stat().st_mtime
    except OSError:
        return False
    return age <= _RESTORE_LOCK_MAX_AGE.total_seconds()


def _queue_due_schedule_catchups(config: dict, *, at_startup: bool = False) -> bool:
    # A restore is rolling the volume back — any "missed" slot is an artifact of
    # the rollback, not a real miss. Stay quiet until the restore completes.
    if _lvm_restore_in_progress():
        return False
    changed = False
    queued_task_ids = []
    queued_tasks_meta = []
    now = datetime.now()
    tz_name = _get_schedule_tz(config)
    for task in config.get("tasks", []):
        if not task.get("enabled", True):
            continue
        # Use UTC-adjusted cron so the computed slot matches Django's UTC datetime.now()
        cron_utc = _cron_local_to_utc(task.get("cron", ""), tz_name)
        previous_run = _compute_cron_run(cron_utc, after=now, reverse=True)
        if not previous_run:
            continue
        # Grace period — but ONLY on a running system (page-load / endpoint
        # triggers). On a live system the crontab fires *at* the slot, then
        # waits up to ~5 min for uvicorn before the backup starts; treating the
        # slot as "missed" any sooner races that on-time run and emits a false
        # alert. At STARTUP we skip the grace: if the VM was off (or booting)
        # at the slot, cron could never have fired it and never will — this is
        # the genuine "VM démarrée après l'heure planifiée" case, so we recover
        # immediately. `_latest_backup_after` below still suppresses the
        # catchup if the run actually did happen.
        if not at_startup and (now - previous_run) < _MISSED_RUN_GRACE:
            continue
        last_run = _safe_parse_datetime(task.get("last_run_at"))
        last_queued_for = task.get("last_queued_for")
        previous_run_key = previous_run.isoformat()
        # Only skip if this exact scheduled slot was already queued/handled.
        # Do NOT use last_run >= previous_run — manual runs after the slot would
        # wrongly suppress the catchup for the scheduled slot.
        if last_queued_for == previous_run_key:
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
        queued_tasks_meta.append((task.get("name", task["id"]), task.get("type", ""), previous_run_key))
        changed = True
    if changed:
        _write_schedule_config(config)
    for task_id in queued_task_ids:
        _start_scheduled_task_thread(task_id)
    for task_name, backup_type, missed_at in queued_tasks_meta:
        append_backup_event(
            kind="schedule",
            title="Missed backup catchup queued",
            severity="warning",
            status="queued",
            source="scheduler",
            detail=f"Missed slot {missed_at}",
            extra={"task_name": task_name, "backup_type": backup_type, "missed_at": missed_at},
        )
        threading.Thread(
            target=notify_missed_backup_catchup,
            args=(task_name, backup_type, missed_at),
            daemon=True,
        ).start()
    return changed


def _sync_crontab(tasks, tz_name: str | None = None):
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    existing = result.stdout.splitlines() if result.returncode == 0 else []
    # Strip old asguard task lines and any previous TZ= / CRON_TZ= overrides we
    # may have written before. We no longer inject a timezone header: cronie
    # IGNORES `TZ=` for schedule evaluation (it only honors `CRON_TZ=`), so the
    # old `TZ=UTC` header silently made jobs fire in *system local* time, i.e.
    # one hour early here, when uvicorn was still booting → the run was missed
    # and the catchup wrongly reported it. We now schedule in the system's
    # local time, exactly matching the hour the user picked. Django keeps
    # computing the slot in UTC (via _cron_local_to_utc) — same wall-clock
    # instant — so the catchup stays consistent.
    clean = [line for line in existing
             if "# asguard_task:" not in line
             and not line.startswith("TZ=")
             and not line.startswith("CRON_TZ=")]
    for task in tasks:
        if not task.get("enabled", True):
            continue
        endpoint = f"schedule/run/{task['id']}" if TASK_ENDPOINT_MAP.get(task.get("type", "")) else ""
        if not endpoint:
            continue
        # Cron fires in system local time — use the user's cron expression as-is.
        cron_local = task['cron']
        # Retry loop: wait up to 5 minutes for uvicorn to be reachable, then POST
        # the backup. Uses `if/then/else/fi` (no brace groups) so the back-off
        # branch is valid shell — the previous `{{ }}` form was invalid and the
        # `sleep`/retry never ran, so a not-yet-ready uvicorn meant no backup.
        url = "http://127.0.0.1:8000"
        retry_cmd = (
            "/bin/bash -c '"
            "for i in $(seq 1 30); do "
            f"if curl -sf --max-time 3 {url}/swagger/ >/dev/null 2>&1; then "
            f"curl -s -X POST {url}/backup/{endpoint}; break; "
            "else echo \"[$(date)] uvicorn not ready ($i/30)\"; sleep 10; fi; "
            "done'"
        )
        line = (
            f"{cron_local} "
            f"{retry_cmd}"
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

    # Per-task next/previous-run enrichment.
    # The frontend was computing this client-side with a buggy weekday loop that
    # always rendered "demain" for anything > 24 h in the future and ignored the
    # configured scheduler timezone entirely. Backend has the correct helpers —
    # convert local cron → UTC, then match against UTC `now` (Django runs in UTC).
    tz_name = _get_schedule_tz(config)
    now_utc = datetime.utcnow()
    enriched_tasks = []
    for task in config.get("tasks", []):
        item = dict(task)
        cron = task.get("cron", "")
        try:
            cron_utc = _cron_local_to_utc(cron, tz_name)
            nxt = _compute_cron_run(cron_utc, after=now_utc) if task.get("enabled", True) else None
            prv = _compute_cron_run(cron_utc, after=now_utc, reverse=True)
            # Returned datetimes are naive UTC — tag them so JS parses correctly.
            item["next_run"]     = nxt.isoformat() + "Z" if nxt else None
            item["previous_run"] = prv.isoformat() + "Z" if prv else None
        except Exception:
            # Don't break the whole listing if one cron is malformed.
            item["next_run"] = None
            item["previous_run"] = None
        enriched_tasks.append(item)

    return JsonResponse({
        "tasks": enriched_tasks,
        "retention": {**DEFAULT_RETENTION, **config.get("retention", {})},
        "schedule_timezone": tz_name,
        # Surfaced so the UI's "Revenir au précédent" undo button knows
        # what to roll back to after a page reload.
        "previous_timezone": config.get("previous_timezone"),
        "timezone_changed_at": config.get("timezone_changed_at"),
        "server_now": now_utc.isoformat() + "Z",     # lets the UI compute "dans X" without clock drift
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
        _sync_crontab(tasks, _get_schedule_tz(config))
    except Exception as exc:
        logger.warning("Crontab sync failed: %s", exc)
    append_backup_event(
        kind="schedule",
        title="Scheduled backup task saved",
        severity="info",
        status="success",
        source="api",
        ref_id=task_id or tasks[-1].get("id", ""),
        extra={"task": data},
    )
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
    # Run backup in a non-daemon thread so the cron curl returns immediately
    # and all notification threads complete independently of the HTTP lifecycle
    _start_scheduled_task_thread(task_id)
    append_backup_event(
        kind="schedule",
        title="Scheduled backup task queued manually",
        severity="info",
        status="queued",
        source="api",
        ref_id=task_id,
        extra={"backup_type": task.get("type"), "task_name": task.get("label", task_id)},
    )
    return JsonResponse({"status": "queued", "task_id": task_id, "message": "Backup task started in background."}, status=202)


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
        _sync_crontab(tasks, _get_schedule_tz(config))
    except Exception as exc:
        logger.warning("Crontab sync failed: %s", exc)
    append_backup_event(
        kind="schedule",
        title="Scheduled backup task deleted",
        severity="warning",
        status="success",
        source="api",
        ref_id=task_id,
    )
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
    append_backup_event(
        kind="retention",
        title="Backup retention policy updated",
        severity="info",
        status="success",
        source="api",
        extra={"retention": config["retention"]},
    )
    return JsonResponse({"status": "ok", "retention": config["retention"]})


@swagger_auto_schema("POST", responses={200: "OK"}, operation_summary="UPDATE SCHEDULE TIMEZONE")
@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def update_schedule_timezone(request):
    """Change the scheduler timezone with two safety guarantees:

    1) **No retroactive backups.** Re-interpreting an existing cron in a new
       timezone shifts every past "slot" to a different UTC instant. The
       catchup logic (_queue_due_schedule_catchups) would then see those
       freshly-shifted slots as "missed" and trigger them — meaning a simple
       Tunis→New_York switch could fire a Safe backup immediately. We
       prevent that by stamping each enabled task's `last_queued_for` with
       the new TZ's current previous slot, so the catchup logic treats it as
       already handled. Future runs fire normally at the next *future* slot.

    2) **Reversible.** We persist `previous_timezone` so the UI can offer a
       one-click "revert" within the same session.
    """
    tz = (request.data.get("timezone") or "").strip()
    if not tz:
        return JsonResponse({"status": "error", "message": "timezone required"}, status=400)
    try:
        from zoneinfo import ZoneInfo
        ZoneInfo(tz)  # validate IANA name
    except Exception:
        return JsonResponse({"status": "error", "message": f"Invalid timezone: {tz}"}, status=400)

    config = _read_schedule_config()
    old_tz = _get_schedule_tz(config)
    # No-op short-circuit — avoid pointless writes / log spam if the user
    # re-selects the timezone that's already active.
    if old_tz == tz:
        return JsonResponse({"status": "ok", "schedule_timezone": tz,
                             "previous_timezone": old_tz, "noop": True})

    # Pre-stamp every enabled task with its new-TZ previous-slot key so the
    # catchup logic in _queue_due_schedule_catchups skips it (the matching
    # branch is `if last_queued_for == previous_run_key: continue`).
    now_utc = datetime.utcnow()
    for task in config.get("tasks", []):
        if not task.get("enabled", True):
            continue
        try:
            cron_utc_new = _cron_local_to_utc(task.get("cron", ""), tz)
            prev = _compute_cron_run(cron_utc_new, after=now_utc, reverse=True)
            if prev:
                task["last_queued_for"] = prev.isoformat()
                # Don't touch `last_run_at` — that's a real historical fact.
        except Exception:
            # Bad cron in one task must not block the timezone change.
            pass

    config["previous_timezone"] = old_tz
    config["schedule_timezone"] = tz
    config["timezone_changed_at"] = now_utc.isoformat() + "Z"
    _write_schedule_config(config)
    try:
        _sync_crontab(config.get("tasks", []), tz)
    except Exception as exc:
        logger.warning("Crontab sync after tz change failed: %s", exc)

    append_backup_event(
        kind="schedule",
        title="Scheduler timezone changed",
        severity="info",
        status="success",
        source="api",
        detail=f"{old_tz} → {tz}",
        extra={"previous_timezone": old_tz, "new_timezone": tz},
    )

    return JsonResponse({"status": "ok",
                         "schedule_timezone": tz,
                         "previous_timezone": old_tz})


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
    append_backup_event(
        kind="retention",
        title="Backup retention applied",
        severity="warning" if result.get("total_deleted", 0) else "info",
        status="success",
        source="api",
        detail=f"{result.get('total_deleted', 0)} backup(s) deleted",
        extra=result,
    )
    return JsonResponse({"status": "ok", **result})


# ═════════════════════════════════════════════════════════════════════════════
#  SECTION: IMPORT  — restore an exported backup archive
# ═════════════════════════════════════════════════════════════════════════════

@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([AllowAny])
def import_backup(request):
    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return JsonResponse({"status": "error", "message": "No file uploaded."}, status=400)

    result = ExportImportService.import_backup(uploaded_file)
    _invalidate_backup_results_cache()
    status_code = 200 if result.get("status") == "success" else 400
    append_backup_event(
        kind="backup",
        title="Backup imported" if status_code == 200 else "Backup import failed",
        severity="success" if status_code == 200 else "error",
        status=result.get("status", "unknown"),
        source="api",
        ref_id=result.get("backup_id", ""),
        detail=result.get("message", ""),
        extra={"filename": getattr(uploaded_file, "name", "")},
    )
    return JsonResponse(result, status=status_code)


# ── Cloud Storage API ──────────────────────────────────────────────────────────
# Extracted to views_cloud.py during the code-review cleanup. The endpoints
# (cloud_config, cloud_test, cloud_list, cloud_sync, cloud_backup_history)
# remain reachable under /backup/cloud/* — see urls.py for the route map.


# ── In-app alerts ──────────────────────────────────────────────────────────────

@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def get_in_app_alerts(request):
    try:
        data = json.loads(IN_APP_ALERTS_FILE.read_text()) if IN_APP_ALERTS_FILE.exists() else {"alerts": [], "last_read": ""}
    except Exception:
        data = {"alerts": [], "last_read": ""}
    return JsonResponse(data)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def mark_in_app_alerts_read(request):
    try:
        data = json.loads(IN_APP_ALERTS_FILE.read_text()) if IN_APP_ALERTS_FILE.exists() else {"alerts": [], "last_read": ""}
        for alert in data.get("alerts", []):
            alert["read"] = True
        from datetime import timezone as _tz
        data["last_read"] = datetime.now(_tz.utc).isoformat()
        IN_APP_ALERTS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception:
        pass
    return JsonResponse({"ok": True})
