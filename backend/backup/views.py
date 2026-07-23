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
from backend.backup.observability import append_backup_event

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


# Structural / non-rule lines in `nft list ruleset` output — never counted
# as duplicate "rules" because they legitimately repeat across chains.
_NFT_STRUCTURAL_PREFIXES = (
    "table ", "chain ", "set ", "map ", "element", "type ", "policy ",
    "comment ", "flags ", "elements ", "}", "{",
)


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


# ═════════════════════════════════════════════════════════════════════════════
#  SECTION: DASHBOARD & RISK AI  — overview, risk analysis, ping, metrics
# ═════════════════════════════════════════════════════════════════════════════
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
    append_backup_event(kind="backup", title="DB backup started", severity="info", status="running", source="api")
    result = SystemBackupService.create_db_backup()
    _invalidate_backup_results_cache()
    ok = result.get("status") == "ok"
    backup_id = result.get("backup_id") or Path(result.get("file", "")).stem
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
    _ok = result.get("status") in {"ok", "partial"}
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
    _summary = result.get("summary", {}) or {}
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
