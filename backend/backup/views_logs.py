"""
Backup & Restore — Logs / Audit Timeline / System tail
======================================================
Single aggregated view of everything the backup/recovery subsystem did:
  • backups, restores, snapshots, migrations
  • notifications fired (in-app alerts file)
  • AI Risk Center transitions
  • plus a live system-log tail (journalctl)

Every event is normalized to the same shape so the UI renders one timeline.
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny

# ── Data sources ──────────────────────────────────────────────────────────────
BACKUP_DIR        = Path("/var/backups/asguard")
BACKUP_JOBS_DIR   = BACKUP_DIR / "backup_jobs"
RESTORE_JOBS_DIR  = BACKUP_DIR / "restore_jobs"
RESTORED_LOGS_DIR = BACKUP_DIR / "restored_logs"
IN_APP_ALERTS     = BACKUP_DIR / "in_app_alerts.json"

LVM_STATE_ROOT    = Path("/var/lib/asguard/lvm")
SNAPSHOT_JOBS_DIR = LVM_STATE_ROOT / "snapshot_jobs"
LVM_AUDIT_DIR     = Path("/var/log/asguard")          # migration_*.json
RESOURCE_NOTIFY   = Path("/var/log/asguard/resource_risk_notify.json")
RISK_AI_STATE     = Path("/var/log/asguard/risk_ai_state.json")
OBS_EVENTS_FILE   = BACKUP_DIR / "events.ndjson"


# ── Severity helpers ──────────────────────────────────────────────────────────
SEVERITY_RANK = {"info": 0, "success": 0, "warning": 1, "error": 2, "critical": 3}


def _sev_from_status(status: str | None) -> str:
    if status in ("done", "success"):     return "success"
    if status in ("partial_success",):    return "warning"
    if status in ("error", "failed"):     return "error"
    if status in ("running", "queued"):   return "info"
    return "info"


import re as _re
_JOBID_TS_RE = _re.compile(r"(?:^|_)(\d{8})_(\d{6})(?:_|$)")


def _ts_from_job_id(job_id: str) -> str | None:
    """Extract an ISO timestamp from a job_id like 'snap_job_20260505_153135'."""
    if not job_id:
        return None
    m = _JOBID_TS_RE.search(job_id)
    if not m:
        return None
    try:
        ymd, hms = m.group(1), m.group(2)
        return f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:8]}T{hms[:2]}:{hms[2:4]}:{hms[4:6]}+01:00"
    except Exception:
        return None


def _parse_iso(s: str | None, fallback_job_id: str | None = None) -> str:
    """Return an ISO8601 timestamp.
    Priority: parseable input → job_id-derived timestamp → epoch zero.
    We DO NOT fall back to 'now' anymore — that polluted the 24h filter with
    decade-old jobs that lacked a started_at field."""
    if s:
        try:
            datetime.fromisoformat(s.replace("Z", "+00:00"))
            return s
        except Exception:
            pass
    if fallback_job_id:
        derived = _ts_from_job_id(fallback_job_id)
        if derived:
            return derived
    # Last resort: 1970 so it sorts to the bottom AND is excluded by any
    # reasonable "since" filter ("24h", "7d", "30d").
    return "1970-01-01T00:00:00+00:00"


# Category classification for the timeline.
#   operation     — backup/restore/snapshot/migration (backup subsystem)
#   system_change — firewall/nat/service/cert/user/network/routing config CRUD
#   alert         — risk pressure, WAF/IDS violations
#   auth          — login / logout / failed login
ALERT_TYPE_TO_CATEGORY = {
    "firewall_rule":            ("system_change", "Règle firewall"),
    "nat_change":               ("system_change", "NAT"),
    "ipsec_change":             ("system_change", "Tunnel IPsec"),
    "openvpn_change":           ("system_change", "OpenVPN"),
    "vpn_change":               ("system_change", "VPN"),
    "certificate":              ("system_change", "Certificat"),
    "cert_change":              ("system_change", "Certificat"),
    "user_change":              ("system_change", "Utilisateur"),
    "user_create":              ("system_change", "Utilisateur"),
    "user_delete":              ("system_change", "Utilisateur"),
    "network_change":           ("system_change", "Interface réseau"),
    "routing_change":           ("system_change", "Route statique"),
    "service_action":           ("system_change", "Service système"),
    "service_status":           ("system_change", "Service système"),
    "ztna_change":              ("system_change", "ZTNA"),
    "sdwan_change":             ("system_change", "SD-WAN"),
    "dhcp_change":              ("system_change", "DHCP"),
    "waf_change":               ("system_change", "WAF"),
    "resource_risk":            ("alert", "Risque ressources"),
    "resource_risk_resolved":   ("alert", "Risque ressources"),
    "waf_alert":                ("alert", "WAF"),
    "ids_alert":                ("alert", "IDS/IPS"),
    "auth_login":               ("auth",  "Authentification"),
    "user_login":               ("auth",  "Authentification"),
    "user_logout":              ("auth",  "Authentification"),
}


def _event(kind: str, source: str, title: str, detail: str,
           severity: str, ts: str, ref_id: str = "",
           extra: dict | None = None,
           category: str = "operation",
           entity: str = "",
           action: str = "") -> dict:
    return {
        "kind":     kind,
        "source":   source,
        "title":    title,
        "detail":   detail,
        "severity": severity,
        "ts":       ts,
        "ref_id":   ref_id,
        "category": category,   # operation | system_change | alert | auth
        "entity":   entity,     # eg "Règle firewall" — what changed
        "action":   action,     # eg "Créé" / "Supprimé" / "Modifié"
        "extra":    extra or {},
    }


def _classify_alert(alert_type: str, title: str) -> tuple[str, str, str]:
    """Return (category, entity, action) for an in-app alert.
    Action is inferred from keywords in the title for nicer audit display."""
    cat, entity = ALERT_TYPE_TO_CATEGORY.get(
        alert_type, ("alert" if "alert" in (alert_type or "") else "operation",
                     alert_type.replace("_", " ").title() if alert_type else ""))
    low = (title or "").lower()
    if   any(k in low for k in ("créé", "ajout", "added", "create", "nouveau")): action = "Créé"
    elif any(k in low for k in ("supprim", "delete", "removed", "retir")):       action = "Supprimé"
    elif any(k in low for k in ("modif", "updat", "changement", "edited")):      action = "Modifié"
    elif any(k in low for k in ("démarr", "started", "lancé", "actif")):         action = "Démarré"
    elif any(k in low for k in ("arrêt", "stopped", "stoppé")):                  action = "Arrêté"
    elif any(k in low for k in ("redémarr", "restart")):                          action = "Redémarré"
    elif "résolu" in low or "resolved" in low:                                    action = "Résolu"
    else:                                                                          action = ""
    return cat, entity, action


# ── Aggregators ───────────────────────────────────────────────────────────────
def _collect_backup_jobs() -> list[dict]:
    out = []
    if not BACKUP_JOBS_DIR.exists():
        return out
    for p in BACKUP_JOBS_DIR.glob("*.json"):
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        status = d.get("status", "?")
        btype  = d.get("backup_type", "backup")
        comp_count = (d.get("done") or 0)
        total      = (d.get("total") or 0)
        out.append(_event(
            category="operation",
            kind="backup", source="Backup",
            title=f"Backup {btype} — {status}",
            detail=(f"{comp_count}/{total} composants · {d.get('progress_pct', 0)}%"
                    + (f" · {d.get('current_component') or ''}" if status == "running" else "")),
            severity=_sev_from_status(status),
            ts=_parse_iso(d.get("started_at") or d.get("created_at"),
                          d.get("job_id") or p.stem),
            ref_id=d.get("backup_id") or d.get("job_id") or "",
            extra={"job_id": d.get("job_id"), "status": status,
                   "duration": d.get("duration_seconds")},
        ))
    return out


def _collect_restore_jobs() -> list[dict]:
    out = []
    if not RESTORE_JOBS_DIR.exists():
        return out
    for p in RESTORE_JOBS_DIR.glob("*.json"):
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        status = d.get("status", "?")
        mode   = d.get("mode", "restore")
        result = d.get("result") or {}
        summary = result.get("summary") or {}
        ok  = summary.get("success", 0)
        ko  = summary.get("failed", 0)
        out.append(_event(
            category="operation",
            kind="restore", source="Restore",
            title=f"Restore {mode} — {status}",
            detail=f"{ok} OK · {ko} échec(s) · backup {d.get('backup_id', '?')}",
            severity=_sev_from_status(status),
            ts=_parse_iso(d.get("started_at"), d.get("job_id") or p.stem),
            ref_id=d.get("backup_id") or d.get("job_id") or "",
            extra={"job_id": d.get("job_id"), "mode": mode},
        ))
    return out


def _collect_snapshot_jobs() -> list[dict]:
    out = []
    if not SNAPSHOT_JOBS_DIR.exists():
        return out
    for p in SNAPSHOT_JOBS_DIR.glob("*.json"):
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        status = d.get("status", "?")
        is_restore = p.name.startswith("snap_restore_")
        kind = "Restauration LVM" if is_restore else "Snapshot LVM"
        title_verb = "restauré" if is_restore else "créé"
        snap = d.get("snap_id", "?")
        result = d.get("result") or {}
        binds = result.get("binds_restored") or []
        ctrs  = result.get("containers_restarted") or []
        detail = f"Snapshot {title_verb} : {snap}"
        if is_restore and binds:
            detail += f" · {len(binds)} bind-mount(s) rétablis"
            if ctrs:
                detail += f" · {', '.join(ctrs)} redémarré(s)"
        out.append(_event(
            category="operation",
            kind="snapshot", source=kind,
            title=f"{kind} — {status}",
            detail=detail,
            severity=_sev_from_status(status),
            ts=_parse_iso(d.get("started_at"), d.get("job_id") or p.stem),
            ref_id=snap or d.get("job_id") or "",
            extra={"job_id": d.get("job_id"), "snap_id": snap,
                   "duration": d.get("duration_seconds")},
        ))
    return out


def _collect_migration_audits() -> list[dict]:
    out = []
    if not LVM_AUDIT_DIR.exists():
        return out
    for p in LVM_AUDIT_DIR.glob("migration_*.json"):
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        items   = d.get("items") or []
        ok      = sum(1 for it in items if it.get("success"))
        ko      = sum(1 for it in items if not it.get("success") and not it.get("skipped"))
        total   = len(items)
        sev     = "success" if ko == 0 and total > 0 else ("warning" if ok > 0 else "error")
        out.append(_event(
            category="operation",
            kind="migration", source="Migration LVM",
            title=f"Migration LVM — {d.get('status', '?')}",
            detail=f"{ok}/{total} modules migrés"
                   + (f" · {ko} échec(s)" if ko else ""),
            severity=sev,
            ts=_parse_iso(d.get("started_at") or d.get("completed_at"),
                          d.get("job_id") or p.stem),
            ref_id=d.get("job_id") or p.stem,
            extra={"job_id": d.get("job_id")},
        ))
    return out


def _collect_observability_events() -> list[dict]:
    out = []
    if not OBS_EVENTS_FILE.exists():
        return out
    try:
        lines = OBS_EVENTS_FILE.read_text(encoding="utf-8").splitlines()[-1000:]
    except Exception:
        return out
    for line in lines:
        if not line.strip():
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue
        out.append(_event(
            category="operation",
            kind=d.get("kind", "backup"),
            source=d.get("source", "Observability"),
            title=d.get("title", "Backup event"),
            detail=d.get("detail", ""),
            severity=d.get("severity", "info"),
            ts=_parse_iso(d.get("ts")),
            ref_id=d.get("ref_id", ""),
            extra=d.get("extra") or {},
            entity=d.get("kind", "backup"),
            action=d.get("status", ""),
        ))
    return out


def _collect_in_app_alerts() -> list[dict]:
    """Notifications fired (any notify_* call writes here). Each entry is
    classified into category + entity + action so the UI can split between
    'system changes' and pure 'alerts'."""
    if not IN_APP_ALERTS.exists():
        return []
    try:
        data = json.loads(IN_APP_ALERTS.read_text())
    except Exception:
        return []
    out = []
    for a in (data.get("alerts") or [])[:300]:
        sev = a.get("severity") or "info"
        if sev not in SEVERITY_RANK:
            sev = "info"
        atype = a.get("type") or ""
        category, entity, action = _classify_alert(atype, a.get("title") or "")
        # System changes display as "notify" kind but render differently — the
        # category field is what the UI tab/filter switches on.
        source = entity or "Notification"
        out.append(_event(
            kind="notify", source=source,
            title=a.get("title") or atype or "Notification",
            detail=a.get("message") or "",
            severity=sev,
            ts=_parse_iso(a.get("time")),
            ref_id=a.get("id") or "",
            category=category, entity=entity, action=action,
            extra={"type": atype, "read": a.get("read")},
        ))
    return out


def _aggregate(since_iso: str | None = None,
               kind_filter: str | None = None,
               severity_filter: str | None = None,
               category_filter: str | None = None,
               q: str | None = None,
               limit: int = 200) -> list[dict]:
    events = []
    for collector in (_collect_backup_jobs, _collect_restore_jobs,
                       _collect_snapshot_jobs, _collect_migration_audits,
                       _collect_observability_events, _collect_in_app_alerts):
        try:
            events.extend(collector())
        except Exception:
            pass

    events.sort(key=lambda e: e["ts"] or "", reverse=True)

    if since_iso:
        events = [e for e in events if e["ts"] >= since_iso]
    if kind_filter and kind_filter != "all":
        events = [e for e in events if e["kind"] == kind_filter]
    if severity_filter and severity_filter != "all":
        events = [e for e in events if e["severity"] == severity_filter]
    if category_filter and category_filter != "all":
        events = [e for e in events if e.get("category") == category_filter]
    if q:
        ql = str(q).lower()
        events = [e for e in events
                  if ql in (e["title"] + " " + e["detail"] + " " + e["ref_id"]
                            + " " + (e.get("entity") or "")).lower()]

    return events[:limit]


# ── Endpoints ─────────────────────────────────────────────────────────────────
@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def logs_timeline(request):
    kind     = request.GET.get("kind")
    severity = request.GET.get("severity")
    category = request.GET.get("category")
    q        = request.GET.get("q")
    since    = request.GET.get("since")  # ISO timestamp or "24h" / "7d" / "30d"
    try:
        limit = int(request.GET.get("limit", "200"))
    except ValueError:
        limit = 200

    since_iso = None
    if since:
        try:
            now = datetime.now(timezone.utc)
            if since.endswith("h"):
                from datetime import timedelta
                since_iso = (now - timedelta(hours=int(since[:-1]))).isoformat()
            elif since.endswith("d"):
                from datetime import timedelta
                since_iso = (now - timedelta(days=int(since[:-1]))).isoformat()
            else:
                since_iso = since
        except Exception:
            since_iso = None

    events = _aggregate(since_iso, kind, severity, category, q, limit)
    return JsonResponse({"events": events, "count": len(events),
                         "filtered": bool(kind or severity or category or q or since)})


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def logs_stats(request):
    """Counters + 24h sparkline for the dashboard row."""
    all_events = _aggregate(limit=1000)

    counts = {"total": len(all_events), "info": 0, "success": 0,
              "warning": 0, "error": 0, "critical": 0}
    by_kind = {}
    for e in all_events:
        counts[e["severity"]] = counts.get(e["severity"], 0) + 1
        by_kind[e["kind"]] = by_kind.get(e["kind"], 0) + 1

    # 24-bucket sparkline (1h resolution over last 24h)
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    sparkline = [0] * 24
    for e in all_events:
        try:
            dt = datetime.fromisoformat(e["ts"].replace("Z", "+00:00"))
            delta = now - dt
            if 0 <= delta.total_seconds() < 24 * 3600:
                idx = 23 - int(delta.total_seconds() // 3600)
                if 0 <= idx < 24:
                    sparkline[idx] += 1
        except Exception:
            pass

    return JsonResponse({
        "counts":    counts,
        "by_kind":   by_kind,
        "sparkline": sparkline,
    })


# Journalctl prefix : "Sep 12 14:38:21 Asguard uvicorn[8139]: <message>"
_JCTL_PREFIX = _re.compile(
    r"^[A-Z][a-z]+\s+\d+\s+(?P<ts>\d{2}:\d{2}:\d{2})\s+\S+\s+"
    r"(?P<svc>\S+?)(?:\[\d+\])?:\s*(?P<msg>.*)$"
)
# Uvicorn HTTP access line :
# "[2026-05-15 ...] INFO | [ACCESS] 127.0.0.1 - GET /backup/foo (200) | user=asguard"
_HTTP_RE = _re.compile(
    r"\[ACCESS\]\s+(?P<ip>[\d.:]+)\s+-\s+(?P<method>[A-Z]+)\s+"
    r"(?P<path>\S+)\s+\((?P<status>\d+)\)"
    r"(?:\s+\|\s+user=(?P<user>\S+))?"
)
# Uvicorn structured non-access line :
# "[2026-05-15 ...] WARNING | something happened"
_LVLPIPE_RE = _re.compile(
    r"\[(?P<dt>[\d\-]+\s[\d:,.]+)\]\s+(?P<level>\w+)\s+\|\s+(?P<msg>.*)$"
)


def _parse_log_line(raw_line: str, unit: str) -> dict:
    """Turn a raw journalctl line into a structured record so the UI can
    render it as a tidy table instead of opaque syslog text."""
    # 1) Strip the syslog prefix to get the actual message
    m = _JCTL_PREFIX.match(raw_line)
    if m:
        ts     = m.group("ts")
        source = m.group("svc")
        body   = m.group("msg").strip()
    else:
        ts, source, body = "", unit, raw_line

    # 2) HTTP access line — most informative pattern, extract everything
    hm = _HTTP_RE.search(body)
    if hm:
        status = int(hm.group("status"))
        level = ("success" if status < 400
                 else "warning" if status < 500
                 else "error")
        return {
            "ts":       ts,
            "source":   source,
            "level":    level,
            "category": "http",
            "method":   hm.group("method"),
            "path":     hm.group("path"),
            "status":   status,
            "ip":       hm.group("ip"),
            "user":     hm.group("user") or "—",
            "summary":  f"{hm.group('method')} {hm.group('path')}",
        }

    # 3) Uvicorn structured log line with LEVEL | message
    lm = _LVLPIPE_RE.search(body)
    if lm:
        lvl = lm.group("level").lower()
        level = ("error" if lvl in ("error", "critical", "fatal")
                 else "warning" if lvl in ("warning", "warn")
                 else "info")
        return {
            "ts":       ts,
            "source":   source,
            "level":    level,
            "category": "log",
            "summary":  lm.group("msg").strip()[:300],
        }

    # 4) Fallback — generic line, infer severity from keywords
    low = body.lower()
    level = ("error"   if any(k in low for k in ("error", "fatal", "traceback", "denied"))
             else "warning" if "warn" in low
             else "success" if any(k in low for k in ("started", "active", "listening"))
             else "info")
    return {
        "ts":       ts,
        "source":   source,
        "level":    level,
        "category": "raw",
        "summary":  body[:300] if body else raw_line[:300],
    }


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def logs_tail(request):
    """Last N lines from a systemd unit, parsed into structured records.
    The frontend renders these as a tidy 'server activity' table — readable
    by an operator, not raw journalctl noise."""
    unit = request.GET.get("unit", "uvicorn")
    try:
        lines = max(20, min(int(request.GET.get("lines", "120")), 500))
    except ValueError:
        lines = 120

    ALLOWED = {"uvicorn", "nginx", "postgresql", "strongswan", "ipsec",
               "squid", "nftables", "suricata", "sshd", "asguard-watchdog",
               "openvpn-server@server", "dhcpd4", "dhcpd6"}
    if unit not in ALLOWED:
        return JsonResponse({"error": f"Unit non autorisée: {unit}",
                             "allowed": sorted(ALLOWED)}, status=400)

    try:
        cmd = ["journalctl", "-u", unit, "-n", str(lines), "--no-pager"]
        if os.geteuid() != 0:
            cmd = ["sudo", "-n"] + cmd
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        raw = (out.stdout or "") + (out.stderr if out.returncode else "")

        entries = []
        counts  = {"info": 0, "success": 0, "warning": 0, "error": 0}
        for ln in raw.splitlines():
            if not ln.strip():
                continue
            entry = _parse_log_line(ln, unit)
            entries.append(entry)
            counts[entry["level"]] = counts.get(entry["level"], 0) + 1
        # Always include the systemd-level diagnostic so the UI can display
        # a "Cause technique" banner above the log feed when the unit is
        # failed/inactive — without the operator having to dig through logs.
        diag = {}
        try:
            from backend.backup.notifications import _diagnose_service_failure
            diag = _diagnose_service_failure(unit) or {}
        except Exception:
            pass

        return JsonResponse({
            "unit":       unit,
            "entries":    entries,
            "counts":     counts,
            "allowed":    sorted(ALLOWED),
            "diagnostic": {
                "active_state": diag.get("active_state", ""),
                "sub_state":    diag.get("sub_state",    ""),
                "result":       diag.get("result",       ""),
                "exit_code":    diag.get("exit_code",    ""),
                "since":        diag.get("since",        ""),
                "cause":        diag.get("cause",        ""),
                "is_failed":    diag.get("active_state") in ("failed", "inactive"),
            },
        })
    except subprocess.TimeoutExpired:
        return JsonResponse({"error": "journalctl timeout"}, status=504)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)
