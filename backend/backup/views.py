import json
import logging
import os
import re
import shlex
import shutil
import subprocess
import threading
import time
from datetime import datetime, timedelta, timezone
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
from backend.backup.observability import append_backup_event
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
        # The real instance on this appliance is server_asguard (the only
        # /etc/openvpn/server/*.conf). @server has no config → always fails.
        "candidates": ["openvpn-server@server_asguard", "openvpn-server@server.service", "openvpn-server@server", "openvpn"],
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
        # A single failed component out of many is a PARTIAL backup, not a total
        # loss: the other components are still fully restorable. Only call it a
        # hard "error" when nothing succeeded at all. This keeps the status honest
        # ("Incomplet" instead of a scary red "Echec") and — crucially — keeps the
        # backup visible with its per-component detail so the operator can see
        # exactly which component failed and why.
        overall_status = "partial" if counts["success"] > 0 else "error"
    elif critical_skipped:
        overall_status = "partial"
    else:
        overall_status = "ok"

    normalized["components"] = normalized_components
    normalized["totals"] = totals
    normalized["health_score"] = health_score
    normalized["overall_status"] = overall_status
    return normalized


# A backup folder without metadata younger than this is treated as in-progress;
# older than this it is treated as an interrupted run and surfaced as failed.
# Comfortably longer than any real backup (safe ≈ 2 s, full ≈ 6 s) yet short
# enough that a dead run shows up on the next dashboard poll.
_INCOMPLETE_BACKUP_STALE_SECONDS = 600  # 10 minutes


def _write_json_atomic(path: Path, payload) -> None:
    """Write JSON via a temp file + atomic rename so a reader never sees a
    half-written (and thus corrupt) file. Preserves owner/mode when possible."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, path)


def _load_backup_metadata_resilient(meta_file: Path):
    """Read backup_metadata.json, tolerating (and self-healing) common on-disk
    corruption so a damaged file never makes a backup vanish from the UI.

    Returns the parsed dict, or None if nothing usable could be recovered.

    Strategy: a strict json.load fails on the most common real-world corruption
    we've seen — a trailing stray '}' or other junk appended after an otherwise
    valid document (e.g. a metadata writer that ran twice). json.JSONDecoder.
    raw_decode parses the first complete JSON value from the start and ignores
    anything after it, which recovers exactly those cases. When we recover a doc
    that differs from the raw bytes, we rewrite the file cleanly (best-effort) so
    it's healthy on the next read."""
    try:
        raw = meta_file.read_text(encoding="utf-8")
    except Exception:
        return None
    stripped = raw.strip()
    if not stripped:
        return None  # empty file — nothing to recover
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass
    # Salvage: decode the first valid JSON value, ignore trailing garbage.
    try:
        obj, _end = json.JSONDecoder().raw_decode(stripped)
    except Exception:
        return None
    if not isinstance(obj, dict):
        return None
    # Self-heal the file so it's clean going forward (best-effort, never fatal).
    try:
        _write_json_atomic(meta_file, obj)
        logger.info("Self-healed corrupt backup metadata: %s", meta_file.parent.name)
    except Exception:
        logger.warning("Could not rewrite salvaged metadata for %s", meta_file.parent.name)
    return obj


def _append_damaged_backup_entry(results: list[dict], d: Path, now: float) -> None:
    """Surface an on-disk backup whose metadata is unreadable as a VISIBLE entry
    instead of dropping it. Only for folders that (a) actually contain real data
    and (b) are old enough not to be an in-progress run — a fresh metadata-less
    folder is a backup mid-write, and a zero-byte folder is a dead leftover swept
    by retention. The entry is flagged damaged so the UI can show/inspect/delete
    it without pretending it's a healthy, restorable backup."""
    try:
        real_size = sum(p.stat().st_size for p in d.rglob("*") if p.is_file())
    except Exception:
        real_size = 0
    if real_size <= 0:
        return  # empty/dead leftover — nothing restorable
    if (now - d.stat().st_mtime) < _INCOMPLETE_BACKUP_STALE_SECONDS:
        return  # too new — likely an in-progress backup still writing metadata
    name = d.name
    if name.startswith("backup_safe_"):
        backup_type = "safe"
    elif name.startswith("backup_custom_"):
        backup_type = "custom"
    else:
        backup_type = "full"
    results.append({
        "type": backup_type,
        "scope": "metadata_damaged",
        "id": name,
        "filename": name,
        "size_bytes": real_size,
        "modified_at": datetime.fromtimestamp(d.stat().st_mtime).isoformat(),
        "health_score": 0,
        "overall_status": "metadata_damaged",
        "components_success": 0,
        "components_failed": 0,
        "components_skipped": 0,
        "metadata": {},
    })


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
                    raw_meta = _load_backup_metadata_resilient(meta_file)
                    if raw_meta is None:
                        # Metadata present but unreadable (empty/garbage) — do NOT
                        # silently drop the backup. If the folder holds real data,
                        # surface it as a visible "damaged" entry so the operator
                        # can inspect/delete it; if empty, it's a dead leftover.
                        _append_damaged_backup_entry(results, d, now)
                        continue
                    meta = _normalize_backup_metadata(d, raw_meta)

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
                    # Never let a parse/normalize error hide an on-disk backup:
                    # fall back to a visible "damaged" entry when real data exists.
                    try:
                        _append_damaged_backup_entry(results, d, now)
                    except Exception:
                        logger.exception("damaged-entry fallback failed for %s", d.name)
            # A metadata-less folder is either an IN-PROGRESS backup (metadata is
            # written last) or dead leftover — it is never restorable, so it is
            # intentionally NOT listed here. Showing them as red "Echec" entries
            # only created confusion (e.g. a folder mid-deletion briefly loses its
            # metadata and would flash as a phantom failure). Dead leftovers are
            # reclaimed silently by _sweep_stale_orphan_backups() during retention.

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
            # Name + reason for each component that did NOT restore, so the UI can
            # show exactly what failed (e.g. "application — uvicorn stop timed out")
            # instead of a vague global "échec".
            "failed_details": [
                {"name": n, "message": (d.get("message") or "")[:200]}
                for n, d in component_results.items() if d.get("status") == "failed"
            ],
            "skipped_details": [
                {"name": n, "message": (d.get("message") or "")[:200]}
                for n, d in component_results.items() if d.get("status") == "skipped"
            ],
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
            # PostgreSQL runs inside docker (app-db-container), not as a host
            # systemd unit — probing `postgresql.service` always says stopped
            # and produces a false "database down" everywhere.
            if not running and name in ("postgresql", "postgres"):
                dk_out, _, dk_code = _run_readonly_command(
                    ["docker", "ps", "--filter", "name=app-db-container",
                     "--format", "{{.Names}}"], timeout=8)
                if dk_code == 0 and "app-db-container" in dk_out:
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
    # Sauvegardes automatiques retirées : on projette seulement une estimation à
    # partir de la dernière sauvegarde (indicatif), sans tâche planifiée.
    next_scheduled_task = None
    projected_next_backup = None
    next_backup_mode = "unplanned"
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

    auto_backup_on = False   # automatisation retirée de cette version

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


@swagger_auto_schema("GET", responses={200: "OK"}, operation_summary="PING BACKUP MODULE")
@api_view(["GET"])
@require_http_methods(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def ping(request):
    return JsonResponse({"status": "ok", "module": "backup"})


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
            if ok:
                _auto_apply_retention_after_backup(backup_id_result)
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
            if ok:
                _auto_apply_retention_after_backup(backup_id_result)
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
        # Which components each preset actually captures — lets the UI show
        # exactly what Full vs Safe include instead of a flat identical list.
        "safe_components": list(FullBackupService.SAFE_COMPONENTS),
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
    # DRF (@api_view) already consumes the request stream into request.data, so
    # reading request.body here raises RawPostDataException. Use request.data,
    # like the other backup/restore views.
    try:
        payload = request.data if isinstance(request.data, dict) else {}
    except Exception:
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
    if _ok:
        _auto_apply_retention_after_backup(result.get("backup_id", ""))
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
    return _launch_detached_restore(backup_id=backup_id, mode="ui_full", request=request)


@swagger_auto_schema("POST", responses={202: "Accepted"}, operation_summary="FULL RESTORE (COMPLETE — WHOLE VM)")
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def restore_full_backup(request, backup_id):
    return _launch_detached_restore(backup_id=backup_id, mode="complete", request=request)


# ── Pre-restore preview ──────────────────────────────────────────────────────
def _current_system_state() -> dict:
    """Best-effort snapshot of the LIVE OS identity, to diff against the backup
    in the restore preview. Runs as the uvicorn user; the root shadow hash is
    read via `sudo -n` (compare-only — never returned to the client)."""
    import socket
    state = {"hostname": None, "root_hash": None, "login_users": [], "packages": set()}
    try:
        state["hostname"] = socket.gethostname()
    except Exception:
        pass
    real_shells = ("/bin/bash", "/bin/sh", "/usr/bin/bash", "/bin/zsh", "/usr/bin/zsh")
    try:
        with open("/etc/passwd") as fh:
            for line in fh:
                parts = line.strip().split(":")
                if len(parts) >= 7 and parts[6] in real_shells and parts[0]:
                    state["login_users"].append(parts[0])
    except Exception:
        pass
    try:
        r = subprocess.run(["sudo", "-n", "grep", "^root:", "/etc/shadow"],
                           capture_output=True, text=True, timeout=5)
        if r.returncode == 0 and ":" in r.stdout:
            state["root_hash"] = r.stdout.split(":")[1]
    except Exception:
        pass
    try:
        r = subprocess.run(["pacman", "-Qq"], capture_output=True, text=True, timeout=20)
        if r.returncode == 0:
            state["packages"] = {ln.strip() for ln in r.stdout.splitlines() if ln.strip()}
    except Exception:
        pass
    return state


def _preview_system_section(backup_dir, components_meta: dict) -> dict:
    """Plain-language summary of the SYSTEM/SECURITY content a COMPLETE restore
    would re-apply: root password, Linux accounts, hostname, installed packages,
    application code. Read straight from the backup's archives (read-only). This
    is what tells a non-technical operator 'restoring this will also reset your
    root password and these accounts' — beyond the per-component DB counts."""
    import tarfile

    def _member_text(archive_rel: str, member: str) -> str | None:
        path = backup_dir / archive_rel
        if not path.exists():
            return None
        try:
            with tarfile.open(path, "r:*") as tar:
                for cand in (member, "./" + member, member.lstrip("/")):
                    try:
                        fh = tar.extractfile(cand)
                    except KeyError:
                        fh = None
                    if fh is not None:
                        return fh.read().decode("utf-8", "ignore")
        except Exception:
            return None
        return None

    ug = (components_meta.get("users_groups") or {}).get("file")
    sc = (components_meta.get("system_config") or {}).get("file")
    has_app = "application" in components_meta
    has_users = bool(ug)
    has_syscfg = bool(sc)

    # Root password presence (a real hash, not '*'/'!') from the backup's shadow.
    root_password = False
    backup_root_hash = None
    login_users: list[str] = []
    users_count = 0
    shadow = _member_text(ug, "etc/shadow") if ug else None
    if shadow:
        for line in shadow.splitlines():
            if line.startswith("root:"):
                h = line.split(":")[1] if ":" in line else ""
                backup_root_hash = h
                root_password = bool(h) and h not in ("*", "!", "!!")
                break
    passwd = (_member_text(ug, "etc/passwd") if ug else None) or (
        _member_text(sc, "etc/passwd") if sc else None
    )
    if passwd:
        real_shells = ("/bin/bash", "/bin/sh", "/usr/bin/bash", "/bin/zsh")
        for line in passwd.splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split(":")
            if len(parts) < 7:
                continue
            users_count += 1
            name, shell = parts[0], parts[6]
            # Surface only accounts a human can log into — hides ~25 daemon users.
            if shell in real_shells and name != "":
                login_users.append(name)

    hostname = None
    hn = _member_text(sc, "etc/hostname") if sc else None
    if hn:
        hostname = hn.strip().splitlines()[0] if hn.strip() else None

    packages_count = None
    backup_pkgs: set[str] = set()
    pkg_meta = components_meta.get("packages") or {}
    pkg_file = pkg_meta.get("file")
    if pkg_file:
        p = backup_dir / pkg_file
        try:
            if p.exists():
                lines = [ln.strip() for ln in p.read_text(errors="ignore").splitlines() if ln.strip()]
                packages_count = len(lines)
                backup_pkgs = {ln.split()[0] for ln in lines if ln.split()}
        except Exception:
            packages_count = None

    # ── Diff against the LIVE system: what will actually CHANGE vs stay identical.
    cur = _current_system_state()
    backup_users = set(login_users)
    cur_users = set(cur["login_users"])
    root_pw_changes = None
    if backup_root_hash and cur["root_hash"] is not None:
        root_pw_changes = (backup_root_hash.strip() != cur["root_hash"].strip())
    pkg_missing = sorted(backup_pkgs - cur["packages"]) if (backup_pkgs and cur["packages"]) else None
    diff = {
        "root_password": {"changes": root_pw_changes},
        "hostname": {
            "current": cur["hostname"],
            "backup": hostname,
            "changes": bool(hostname and cur["hostname"] and hostname != cur["hostname"]),
        },
        "users": {
            "current": sorted(cur_users),
            "backup": sorted(backup_users),
            "added": sorted(backup_users - cur_users),      # created by the restore
            "removed": sorted(cur_users - backup_users),    # exist now, absent from backup
        },
        "packages": {
            "backup_count": packages_count,
            "missing": (pkg_missing or [])[:20],
            "missing_count": (len(pkg_missing) if pkg_missing is not None else None),
        },
    }

    return {
        # 'applicable' = this backup carries OS-level identity (only complete
        # restore re-applies it; safe/ui_full restores never touch these).
        "applicable": bool(has_app or has_users or has_syscfg),
        "whole_vm": has_app,
        "root_password": root_password,
        "login_users": sorted(set(login_users)),
        "users_count": users_count,
        "hostname": hostname,
        "packages_count": packages_count,
        "has_application": has_app,
        "has_system_config": has_syscfg,
        "has_users_groups": has_users,
        "diff": diff,
    }


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

    def _component_changes(component: str) -> dict:
        """Real CONTENT diff between the live DB and the backup for a component.

        Count-deltas miss a row that was *modified* in place (same count). Here
        we compare actual rows by primary key + fields, so a changed firewall
        rule shows up. Returns what restoring this backup WOULD do to the live
        DB: added (back), removed (your post-backup rows), modified (reverted).
        """
        snap = backup_dir / component / DB_SNAPSHOT_FILENAME
        if not snap.exists():
            return {"added": 0, "removed": 0, "modified": 0, "available": False}
        try:
            bdata = _json.loads(snap.read_text(encoding="utf-8"))
        except Exception:
            return {"added": 0, "removed": 0, "modified": 0, "available": False}
        from django.core import serializers as _ser
        added = removed = modified = 0
        for path, blob in (bdata.get("models") or {}).items():
            Model = _resolve_model(path)
            if Model is None:
                continue
            try:
                backup_rows = _json.loads(blob) if isinstance(blob, str) else (blob or [])
                live_rows = _json.loads(_ser.serialize("json", Model.objects.all()))
            except Exception:
                continue
            b = {r.get("pk"): r.get("fields", {}) for r in backup_rows}
            l = {r.get("pk"): r.get("fields", {}) for r in live_rows}
            bk, lk = set(b), set(l)
            added += len(bk - lk)        # in backup, missing now → would reappear
            removed += len(lk - bk)      # added after backup → would be deleted
            modified += sum(1 for pk in (bk & lk) if b[pk] != l[pk])  # changed → reverted
        return {
            "added": added, "removed": removed, "modified": modified,
            "available": True, "total": added + removed + modified,
        }

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
            changes = _component_changes(name)
            included.append({
                "name":             name,
                "size_mb":          round(size_mb, 3),
                "status":           comp.get("status", "?"),
                "inventory":        inventory,
                "total_in_backup":  total_in_backup,
                "total_current":    total_current,
                "has_db_inventory": bool(inventory),
                "changes":          changes,
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

    changes_total = {
        "added":    sum((c.get("changes") or {}).get("added", 0) for c in included),
        "removed":  sum((c.get("changes") or {}).get("removed", 0) for c in included),
        "modified": sum((c.get("changes") or {}).get("modified", 0) for c in included),
    }
    changes_total["total"] = changes_total["added"] + changes_total["removed"] + changes_total["modified"]

    try:
        system_section = _preview_system_section(backup_dir, components_meta)
    except Exception as exc:
        logger.warning("preview system section failed: %s", exc)
        system_section = {"applicable": False}

    return JsonResponse({
        "status":            "ok",
        "backup_id":         backup_id,
        "changes_total":     changes_total,
        "system":            system_section,
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


def _capture_operator_session(request) -> dict | None:
    """Snapshot the operator's current Django session row so it can be re-injected
    AFTER a restore overwrites django_session — keeping the browser logged in
    instead of bouncing it to the login page. Best-effort; never raises."""
    try:
        if request is None:
            return None
        sk = getattr(getattr(request, "session", None), "session_key", None)
        if not sk:
            return None
        from django.contrib.sessions.models import Session
        row = Session.objects.filter(session_key=sk).first()
        if row is None:
            return None
        return {
            "session_key": row.session_key,
            "session_data": row.session_data,
            "expire_date": row.expire_date.isoformat(),
            "applied": False,
        }
    except Exception as exc:
        logger.warning("capture operator session failed: %s", exc)
        return None


def _reinject_preserved_session(payload: dict, state_file) -> dict:
    """Once a restore reaches a terminal state, re-create the operator's session
    row (wiped when django_session was restored) so the live browser cookie keeps
    resolving and the user is NOT sent back to the login page. Runs in the uvicorn
    Django process (full ORM + DB), idempotent via the 'applied' flag."""
    ps = payload.get("preserve_session")
    if not isinstance(ps, dict) or ps.get("applied"):
        return payload
    if payload.get("status") not in ("success", "partial_success"):
        return payload
    try:
        # Force a fresh DB connection: the restore dropped/recreated the DB, so a
        # pooled connection from before the restore may be stale.
        from django.db import connection
        connection.close()
        from django.contrib.sessions.models import Session
        from django.utils.dateparse import parse_datetime
        Session.objects.update_or_create(
            session_key=ps["session_key"],
            defaults={
                "session_data": ps["session_data"],
                "expire_date": parse_datetime(ps["expire_date"]),
            },
        )
        ps["applied"] = True
        payload["session_preserved"] = True
    except Exception as exc:
        # Don't fail the status poll — worst case the user logs in again.
        logger.warning("re-inject operator session failed: %s", exc)
        ps["applied"] = True
        payload["session_preserved"] = False
        payload["session_preserve_error"] = str(exc)
    try:
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except Exception:
        pass
    return payload


def _launch_detached_restore(backup_id: str, mode: str, request=None):
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

    # Rough ETA so the UI can show "estimated time / wait to stabilize" instead of
    # an open-ended spinner. complete = whole-VM (code swap + uvicorn restart +
    # service stabilization), so it's the longest.
    eta_seconds = {"complete": 210, "ui_full": 80, "safe": 50}.get(mode, 120)
    stabilize_eta_seconds = 120 if mode == "complete" else 30

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
        "estimated_seconds": eta_seconds,
        "stabilize_estimate_seconds": stabilize_eta_seconds,
        # Whole-VM restores reset kernel-level state (network profiles, systemd
        # units, /etc); a clean reboot is the safest way to finish bringing the
        # restored system up. The overlay surfaces this to the operator.
        "reboot_recommended": mode == "complete",
        # Keep the operator logged in across the django_session overwrite.
        "preserve_session": _capture_operator_session(request),
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
        # Survive memory pressure: a COMPLETE restore is I/O- and memory-heavy and
        # restarts uvicorn from within itself. Make the OOM killer / systemd-oomd
        # avoid this unit so it is never SIGKILL'd mid-stabilization (which used to
        # strand the job at status="running" and freeze the progress banner).
        "--property=OOMScoreAdjust=-900",
        "--property=OOMPolicy=continue",
        # Keep the VM responsive while LVM snapshots are active WITHOUT removing
        # them: the appliance bind-mounts /etc onto the snapshot'd data LV (on
        # /dev/sdb), so restore writes are copy-on-write amplified and can saturate
        # that disk until PostgreSQL/dbus time out ("Could not get property") and
        # the VM freezes. This disk uses mq-deadline, so ionice/IOWeight do nothing
        # — the lever that works on cgroup-v2 is an absolute write-bandwidth CAP on
        # the snapshot's disk. We cap writes to /dev/sdb so the COW amplification
        # can't monopolise it, and lower CPU weight. The /etc payload is small, so
        # this barely slows the restore but stops the I/O storm.
        "--property=IOWriteBandwidthMax=/dev/sdb 40M",
        "--property=IOReadBandwidthMax=/dev/sdb 80M",
        "--property=CPUWeight=30",
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


# ── Self-healing for stranded restore jobs ───────────────────────────────────
# A COMPLETE (whole-VM) restore swaps /asguard/asguard and restarts uvicorn from
# inside a detached systemd unit. If that unit is SIGKILL'd (OOM, a daemon-reload
# triggered by the system_config/systemd restore, the uvicorn restart it performs
# itself…) AFTER the component loop but BEFORE it writes the terminal status, the
# job file is stranded at status="running" forever: the banner never releases and
# the restore never appears as finished in history.
#
# These helpers let any reader (status poll, /restore/active, history) finalize
# such a job from the progress it already recorded. The reader runs *inside* the
# restarted uvicorn, so the mere fact that it executes proves the appliance is
# back up — we can truthfully report a terminal state.
_RESTORE_STALE_SECONDS = 150  # no progress write for this long ⇒ runner is dead/hung
_RESTORE_LOCK_FILE = RESTORE_JOBS_DIR / ".in_restore"


def _restore_runner_alive(job_id: str) -> bool:
    """True if a full_restore_runner.py process for this job is still running.
    Best-effort: if we can't tell, assume alive (don't finalize prematurely)."""
    try:
        for proc in psutil.process_iter(["cmdline"]):
            cmd = " ".join(proc.info.get("cmdline") or [])
            if "full_restore_runner.py" in cmd and job_id in cmd:
                return True
    except Exception:
        return True
    return False


def _derive_restore_result_from_progress(payload: dict) -> dict:
    """Reconstruct a result dict (results/summary/status) from components_progress
    so a stranded job can be finalized + rendered in history/verification."""
    cp = payload.get("components_progress") or {}
    results = {}
    success = failed = skipped = 0
    for name, status in cp.items():
        # Components left "running"/"pending" never completed → count as failed.
        norm = status if status in ("success", "failed", "skipped") else "failed"
        if norm == "success":
            success += 1
        elif norm == "skipped":
            skipped += 1
        else:
            failed += 1
        results[name] = {
            "status": norm,
            "message": (
                "Restauré." if norm == "success"
                else "Ignoré." if norm == "skipped"
                else "Interrompu avant la fin (suivi perdu)."
            ),
        }
    status = "success" if (failed == 0 and success > 0) else (
        "partial_success" if success > 0 else "error"
    )
    return {
        "status": status,
        "backup_id": payload.get("backup_id"),
        "mode": payload.get("mode"),
        "results": results,
        "summary": {"success": success, "failed": failed, "skipped": skipped},
    }


def _maybe_finalize_stale_restore(payload: dict, state_file: Path) -> dict:
    """If `payload` is a 'running' restore job whose runner is gone, finalize it
    in place (write terminal status to disk, clear the stale watchdog lock) and
    return the updated payload. No-op for already-terminal or genuinely-live jobs."""
    if not isinstance(payload, dict):
        return payload
    if payload.get("status") in ("success", "partial_success", "error"):
        return payload
    # "running" (loop in progress) and "stabilizing" (loop done, verifying
    # services) are the two non-terminal states a stranded job can be left in.
    if payload.get("status") not in ("running", "stabilizing"):
        return payload

    try:
        mtime = state_file.stat().st_mtime
    except Exception:
        mtime = time.time()
    age = time.time() - mtime
    done = payload.get("done") or 0
    total = payload.get("total") or 0

    loop_finished = total > 0 and done >= total
    runner_gone = (age > _RESTORE_STALE_SECONDS) and not _restore_runner_alive(payload.get("job_id", ""))

    # Finalize when the component loop completed (only post-work was interrupted)
    # or the runner has clearly died mid-restore and stopped reporting progress.
    if not (loop_finished or runner_gone):
        return payload

    # Prefer the detailed result the runner already persisted (full per-component
    # detail + row-level diff); fall back to reconstructing it from progress.
    existing = payload.get("result") or {}
    if existing.get("results"):
        result = dict(existing)
        summ = result.get("summary") or {}
        if not result.get("status"):
            result["status"] = "success" if (summ.get("failed", 0) == 0 and summ.get("success", 0) > 0) else (
                "partial_success" if summ.get("success", 0) > 0 else "error"
            )
    else:
        result = _derive_restore_result_from_progress(payload)
    # We're executing inside uvicorn ⇒ the app control-plane is up. Confirm nginx
    # so the operator gets a truthful "système opérationnel" signal.
    stabilized = True
    try:
        ng = subprocess.run(["systemctl", "is-active", "nginx"],
                            capture_output=True, text=True, timeout=8)
        stabilized = (ng.stdout or "").strip() == "active"
    except Exception:
        stabilized = True
    result["stabilization"] = {
        "status": "success" if stabilized else "partial",
        "details": {"note": "État finalisé automatiquement après reprise du suivi."},
    }
    result["self_healed"] = True
    result["self_heal_note"] = (
        "Le suivi de la restauration a été interrompu (processus arrêté pendant la "
        "stabilisation). L'état a été reconstitué depuis la progression enregistrée."
    )

    final_status = result["status"]
    if final_status == "success" and not stabilized:
        final_status = "partial_success"

    payload["status"] = final_status
    payload["result"] = result
    payload["self_healed"] = True
    if not payload.get("finished_at"):
        payload["finished_at"] = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()

    try:
        _write_backup_job_state(state_file, payload)
    except Exception:
        logger.exception("Failed to persist self-healed restore job %s", payload.get("job_id"))

    # Drop the stale watchdog lock if it still points at this job, otherwise the
    # service watchdog stays hands-off forever.
    try:
        if _RESTORE_LOCK_FILE.exists():
            lock = json.loads(_RESTORE_LOCK_FILE.read_text())
            if lock.get("job_id") == payload.get("job_id"):
                _RESTORE_LOCK_FILE.unlink(missing_ok=True)
    except Exception:
        pass

    return payload


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
            payload = _maybe_finalize_stale_restore(payload, state_file)

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
                # OS-level changes (root password, system users, hostname) the
                # restore made — what the row-diff can't show.
                "system_changes": result.get("system_changes") or None,
                # LVM snapshots that were present (kept) during the restore.
                "lvm_snapshots": result.get("lvm_snapshots") or None,
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
        payload = _maybe_finalize_stale_restore(payload, state_file)
        payload = _reinject_preserved_session(payload, state_file)
        payload["verification"] = _build_restore_verification(payload)
        return JsonResponse(payload, status=200)
    except Exception as e:
        logger.exception("Failed to read restore job status %s", job_id)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@swagger_auto_schema("GET", responses={200: "OK"}, operation_summary="GET ACTIVE/LATEST RESTORE")
@api_view(["GET"])
@require_http_methods(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def restore_active(request):
    """Latest restore job + whether it's still running.

    Source of truth is the on-disk job file (not the browser), so the UI can
    re-attach to an in-progress restore after a page reload, a browser
    close/reopen, or the uvicorn restart that a COMPLETE restore triggers.
    """
    try:
        files = list(RESTORE_JOBS_DIR.glob("*.json")) if RESTORE_JOBS_DIR.exists() else []
    except Exception:
        files = []
    if not files:
        return JsonResponse({"active": False})
    latest = max(files, key=lambda p: p.stat().st_mtime)
    try:
        data = json.loads(latest.read_text())
    except Exception:
        return JsonResponse({"active": False})
    data = _maybe_finalize_stale_restore(data, latest)
    status = data.get("status", "running")
    finished = status in ("success", "partial_success", "error")
    age = time.time() - latest.stat().st_mtime

    # Has the VM rebooted SINCE this restore finished? If so the restore is history
    # and the overlay must NOT re-appear on page load (the annoying banner that
    # comes back after the post-restore reboot). Compare the job file's mtime to
    # the system boot time.
    rebooted_since = False
    try:
        with open("/proc/uptime") as _f:
            boot_time = time.time() - float(_f.read().split()[0])
        rebooted_since = bool(finished and latest.stat().st_mtime < boot_time)
    except Exception:
        rebooted_since = False

    return JsonResponse({
        "active": (not finished) and age < 1800,   # running + updated within 30 min
        "finished": finished,
        "rebooted_since": rebooted_since,
        "job_id": data.get("job_id") or latest.stem,
        "backup_id": data.get("backup_id"),
        "mode": data.get("mode"),
        "status": status,
        "age_seconds": int(age),
        "reboot_at": data.get("reboot_at"),
    })


@swagger_auto_schema("POST", responses={202: "Accepted"}, operation_summary="REBOOT THE APPLIANCE")
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def system_reboot(request):
    """Reboot the appliance. Offered to the operator from the restore overlay when
    a restore ends degraded and a clean reboot is the safest way to finish bringing
    the rolled-back system up. Scheduled a few seconds out so the HTTP response is
    delivered before the box goes down."""
    try:
        # `sudo -n systemctl reboot` (state-changing systemctl must use sudo -n,
        # uvicorn cannot reboot directly). `--no-block` returns immediately.
        proc = subprocess.run(
            ["sudo", "-n", "systemctl", "reboot", "--no-block"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=15,
        )
        if proc.returncode != 0:
            return JsonResponse(
                {"status": "error", "message": proc.stdout.strip() or "reboot failed"},
                status=500,
            )
        append_backup_event(
            kind="restore", title="Appliance reboot requested", severity="warning",
            status="running", source="restore-overlay",
        )
        return JsonResponse(
            {"status": "rebooting", "message": "Redémarrage de la VM en cours…"},
            status=202,
        )
    except Exception as e:
        logger.exception("system reboot failed")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# No progress write for this long while still "running" ⇒ the backup worker
# (daemon thread or detached unit) died mid-run. Comfortably longer than any real
# config backup (safe ≈ 2 s, full ≈ 6 s) so a live-but-busy run is never killed.
_BACKUP_STALE_SECONDS = 180


def _maybe_finalize_stale_backup(payload: dict, job_file: Path) -> dict:
    """If `payload` is a 'running' backup job whose worker has stopped writing
    progress, finalize it as an error so the UI stops polling forever.

    A manual backup runs in a daemon thread (no systemd unit to probe), so the
    single reliable liveness signal is the job file's freshness: the progress
    callback rewrites it on every component, so a stale mtime while still
    "running" means the worker was killed (e.g. uvicorn reload) mid-backup.
    Mirrors _maybe_finalize_stale_restore for the restore side."""
    if not isinstance(payload, dict) or payload.get("status") != "running":
        return payload
    try:
        age = time.time() - job_file.stat().st_mtime
    except OSError:
        return payload
    if age <= _BACKUP_STALE_SECONDS:
        return payload
    payload = dict(payload)
    payload["status"] = "error"
    payload["finished_at"] = datetime.now(timezone.utc).isoformat()
    existing = payload.get("result") or {}
    if not existing.get("message"):
        payload["result"] = {**existing,
                             "message": "Sauvegarde interrompue : le worker s'est arrêté "
                                        "avant la fin (probable redémarrage). Relancez la sauvegarde."}
    try:
        _write_backup_job_state(job_file, payload)
        _invalidate_backup_results_cache()
        append_backup_event(
            kind="backup", title="Backup finalized as interrupted", severity="warning",
            status="error", source="self-heal", ref_id=payload.get("job_id", ""),
            detail="Worker stopped writing progress; job auto-finalized.",
        )
    except Exception:
        logger.warning("Could not persist stale-backup finalization for %s", payload.get("job_id"))
    return payload


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
        payload = _maybe_finalize_stale_backup(payload, job_file)
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
        if backup_dir.exists() and backup_dir.is_dir():
            # Atomic-ish full removal (with sudo rm -rf fallback for root-owned
            # component archives) so a delete never leaves a metadata-less stump.
            if not _remove_backup_dir(backup_dir):
                return JsonResponse(
                    {"status": "error", "message": f"Backup {backup_id} could not be fully deleted."},
                    status=500,
                )
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


def _remove_backup_dir(d: Path) -> bool:
    """Delete a backup folder completely, even though some component archives are
    root-owned (created via `sudo tar`). shutil.rmtree works when the *directories*
    are uvicorn-owned (they are), but we fall back to `sudo -n rm -rf` so a delete
    can NEVER leave a half-removed, metadata-less stump behind (which used to show
    up as a phantom "Echec" entry)."""
    try:
        shutil.rmtree(d)
    except Exception as exc:
        logger.warning("rmtree failed for %s (%s) — trying sudo rm -rf", d.name, exc)
        try:
            subprocess.run(["sudo", "-n", "rm", "-rf", str(d)], timeout=60, check=False)
        except Exception:
            logger.exception("sudo rm -rf also failed for %s", d.name)
    gone = not d.exists()
    if gone:
        # Drop the cached dedup fingerprint so it can't pile up after deletions.
        try:
            (BACKUP_DIR / "dedup_cache" / f"{d.name}.json").unlink(missing_ok=True)
        except Exception:
            pass
    return gone


def _sweep_stale_orphan_backups() -> int:
    """Silently reclaim dead, metadata-less backup folders (interrupted runs).

    A folder with no backup_metadata.json older than the stale grace is never an
    in-progress backup (those finalize in seconds) and is not restorable, so it is
    pure wasted space. We delete it instead of displaying it — surfacing these as
    red failures only confused operators. Best-effort; never raises."""
    swept = 0
    try:
        for d in BACKUP_DIR.glob("backup_*"):
            if not d.is_dir() or (d / "backup_metadata.json").exists():
                continue
            try:
                age = time.time() - d.stat().st_mtime
            except OSError:
                continue
            if age >= _INCOMPLETE_BACKUP_STALE_SECONDS and _remove_backup_dir(d):
                swept += 1
                logger.info("Swept interrupted backup leftover: %s", d.name)
    except Exception:
        logger.exception("Orphan backup sweep failed")
    if swept:
        _invalidate_backup_results_cache()
    return swept


def _apply_gfs_retention(retention):
    _sweep_stale_orphan_backups()
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

    # Deleting folders changes the listing — drop the cached results so the very
    # next GET /backup (list) reflects the pruning immediately. Without this the
    # UI kept showing the just-deleted backups until the 8 s cache TTL expired,
    # forcing a manual page refresh. (Also covers the auto-retention paths.)
    if deleted:
        _invalidate_backup_results_cache()

    return {"kept": len(keep), "deleted": deleted, "total_deleted": len(deleted)}


def _auto_apply_retention_after_backup(ref_id: str = "", source: str = "api"):
    """Apply GFS retention after ANY successful backup (manual or scheduled).

    Previously only *scheduled* backups pruned old copies; manual backups
    ("+ Nouveau backup") accumulated until the operator clicked "Appliquer la
    rétention". Now every successful backup enforces the same policy so the
    store never grows unbounded between manual retention clicks. Best-effort:
    a retention failure must never mark the backup itself as failed."""
    try:
        config = _read_schedule_config()
        retention_cfg = {**DEFAULT_RETENTION, **config.get("retention", {})}
        ret_result = _apply_gfs_retention(retention_cfg)
        config["last_retention_applied"] = datetime.utcnow().isoformat()
        _write_schedule_config(config)
        deleted = ret_result.get("total_deleted", 0)
        if deleted:
            append_backup_event(
                kind="retention",
                title="Backup retention applied (auto)",
                severity="info",
                status="success",
                source=source,
                ref_id=ref_id,
                detail=f"{deleted} backup(s) deleted after backup",
                extra=ret_result,
            )
        return ret_result
    except Exception as ret_exc:
        logger.warning("Auto-retention after backup %s failed: %s", ref_id, ret_exc)
        return None


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
