"""
Asguard — Notification helper
Email (critiques) + Telegram (temps réel) pour tous les événements firewall/backup.
Config dans /etc/asguard/watchdog_config.json → clé "notifications".
"""

import json
import logging
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

logger = logging.getLogger(__name__)

_WD_CONFIG        = Path("/etc/asguard/watchdog_config.json")
_ENV_FILE         = Path("/asguard/asguard/.env")
_IN_APP_ALERTS    = Path("/var/backups/asguard/in_app_alerts.json")


# ── Event catalog ─────────────────────────────────────────────────────────────
# The user-facing list of subscribable events. Every notify_* function below
# tags itself with a category from this catalog; the routing layer then checks
# the per-category × per-channel subscription matrix in the config.
#
# group           — UI section the category belongs to (Operations / Security / Identity / Network).
# severity_default — the lowest severity at which the category fires. Used by
#                    the global "minimum severity threshold" filter.
CATEGORIES = [
    # Operations
    {"id": "backup",          "label": "Sauvegardes",                    "group": "Opérations",  "severity_default": "info"},
    {"id": "restore",         "label": "Restaurations",                   "group": "Opérations",  "severity_default": "warning"},
    {"id": "drp",             "label": "Exercices de reprise (DR Drill)", "group": "Opérations",  "severity_default": "info"},
    {"id": "vm_risk",         "label": "Pression ressources (CPU/RAM)",   "group": "Opérations",  "severity_default": "critical"},
    {"id": "service_status",  "label": "Services système",                "group": "Opérations",  "severity_default": "warning"},
    # Security
    {"id": "firewall_rule",   "label": "Règles firewall",                 "group": "Sécurité",    "severity_default": "info"},
    {"id": "waf_alert",       "label": "Alertes WAF (ModSecurity)",       "group": "Sécurité",    "severity_default": "warning"},
    {"id": "ids_alert",       "label": "Alertes IDS/IPS (Suricata)",      "group": "Sécurité",    "severity_default": "warning"},
    # Identity & PKI
    {"id": "auth_login",      "label": "Connexions administrateurs",      "group": "Identité",    "severity_default": "info"},
    {"id": "user_change",     "label": "Comptes utilisateurs",            "group": "Identité",    "severity_default": "info"},
    {"id": "certificate",     "label": "Certificats PKI",                 "group": "Identité",    "severity_default": "info"},
    # Network
    {"id": "ipsec_change",    "label": "Tunnels IPsec",                   "group": "Réseau",      "severity_default": "info"},
    {"id": "nat_change",      "label": "NAT (DNAT/SNAT)",                 "group": "Réseau",      "severity_default": "info"},
    {"id": "routing_change",  "label": "Routes statiques",                "group": "Réseau",      "severity_default": "info"},
    {"id": "network_change",  "label": "Interfaces réseau",               "group": "Réseau",      "severity_default": "info"},
]
CATEGORY_IDS = {c["id"] for c in CATEGORIES}
# Channels = enterprise transports. Twilio SMS is for on-call escalation on
# critical events; ntfy keeps the self-hosted mobile push option; Slack covers
# team incident channels; Email is the always-available baseline.
CHANNELS = ["email", "ntfy", "slack", "twilio"]
SEVERITY_RANK = {"info": 0, "warning": 1, "critical": 2}


# ── In-app alert log ───────────────────────────────────────────────────────────

def write_in_app_alert(alert_type: str, title: str, message: str,
                       severity: str = "warning", details: dict | None = None):
    """Persist an alert to the JSON file so the UI can show a real-time toast + badge.

    `details` is an optional structured payload (cause, last_logs, exit_code,
    unit name, …) that the UI uses to render a "Why did this fail?" panel.
    Keep it small — large logs go into views_logs, not in-app alerts."""
    import uuid as _uuid
    alert = {
        "id":       f"alert_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{str(_uuid.uuid4())[:6]}",
        "type":     alert_type,
        "title":    title,
        "message":  message,
        "severity": severity,
        "time":     datetime.now(timezone.utc).isoformat(),
        "read":     False,
    }
    if details:
        alert["details"] = details
    try:
        data = {"alerts": [], "last_read": ""}
        if _IN_APP_ALERTS.exists():
            try:
                data = json.loads(_IN_APP_ALERTS.read_text())
            except Exception:
                pass
        alerts = data.get("alerts", [])

        # Edge-triggered de-duplication. A level-based caller (e.g. a drift /
        # service-health scan that runs every poll) calls this every cycle while
        # a service stays down. Without dedup we'd mint a NEW id each time, the UI
        # would treat it as a brand-new alert and re-toast it forever → spam.
        # If an UNREAD alert with the same (type, title) already exists, just
        # refresh its timestamp in place (same id) instead of inserting a clone.
        # The alert therefore fires ONCE; it can only fire again after the user
        # marks it read (resolves it) or the condition changes (different title).
        for existing in alerts:
            if (not existing.get("read")
                    and existing.get("type") == alert_type
                    and existing.get("title") == title):
                existing["time"] = alert["time"]
                existing["message"] = message
                if details:
                    existing["details"] = details
                tmp = _IN_APP_ALERTS.with_suffix(".tmp")
                tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False))
                tmp.replace(_IN_APP_ALERTS)
                return

        alerts.insert(0, alert)
        data["alerts"] = alerts[:50]
        tmp = _IN_APP_ALERTS.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        tmp.replace(_IN_APP_ALERTS)
    except Exception as exc:
        logger.error("write_in_app_alert failed: %s", exc)


# ── Config helpers ─────────────────────────────────────────────────────────────

def _load_full_config() -> dict:
    try:
        return json.loads(_WD_CONFIG.read_text())
    except Exception:
        return {}


def _load_notif_config():
    return _load_full_config().get("notifications", {})


def _env_vars():
    env = {}
    if _ENV_FILE.exists():
        for line in _ENV_FILE.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env


# ── Email ──────────────────────────────────────────────────────────────────────

def _build_html(title, color, badge_label, badge_color, rows, footer_note=""):
    rows_html = ""
    for label, value, val_color in rows:
        vc = f"color:{val_color};font-weight:600;" if val_color else "color:#374151;"
        rows_html += f"""
        <tr>
          <td style="padding:8px 16px;color:#6b7280;font-size:13px;border-bottom:1px solid #f3f4f6;white-space:nowrap;">{label}</td>
          <td style="padding:8px 16px;font-size:13px;{vc}border-bottom:1px solid #f3f4f6;">{value}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f3f4f6;padding:32px 0;">
    <tr><td align="center">
      <table width="580" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">

        <tr>
          <td style="background:{color};padding:26px 32px;">
            <table width="100%" cellpadding="0" cellspacing="0"><tr>
              <td>
                <div style="color:rgba(255,255,255,0.8);font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;">Asguard</div>
                <div style="color:#fff;font-size:22px;font-weight:700;">{title}</div>
              </td>
              <td align="right" style="font-size:36px;line-height:1;">🛡</td>
            </tr></table>
          </td>
        </tr>

        <tr>
          <td style="padding:20px 32px 8px;">
            <span style="background:{badge_color}18;color:{badge_color};border:1px solid {badge_color}33;
                         font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
                         padding:4px 12px;border-radius:20px;">{badge_label}</span>
          </td>
        </tr>

        <tr>
          <td style="padding:12px 32px 24px;">
            <table width="100%" cellpadding="0" cellspacing="0"
                   style="border:1px solid #f3f4f6;border-radius:8px;overflow:hidden;">
              {rows_html}
            </table>
          </td>
        </tr>

        <tr>
          <td style="background:#f9fafb;padding:14px 32px;border-top:1px solid #f3f4f6;">
            <p style="margin:0;font-size:11px;color:#9ca3af;">
              {footer_note or "Généré automatiquement par Asguard. Ne pas répondre."}
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body></html>"""


def _get_admin_emails():
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return list(
            User.objects.filter(is_active=True, is_staff=True)
            .exclude(email="")
            .values_list("email", flat=True)
        )
    except Exception:
        return []


def send_notification(subject, html, plain, extra_recipients=None):
    """Send email — reserved for critical events only."""
    notif = _load_notif_config()
    if not notif.get("email_enabled"):
        return

    recipients = list(notif.get("recipients", []))
    for email in _get_admin_emails():
        if email not in recipients:
            recipients.append(email)
    if extra_recipients:
        for email in extra_recipients:
            if email and email not in recipients:
                recipients.append(email)
    if not recipients:
        return

    env = _env_vars()
    smtp_host    = notif.get("smtp_host")     or env.get("EMAIL_HOST", "smtp.office365.com")
    smtp_port    = int(notif.get("smtp_port") or env.get("EMAIL_PORT", 587))
    smtp_user    = notif.get("smtp_user")     or env.get("EMAIL_HOST_USER", "")
    smtp_pass    = notif.get("smtp_password") or env.get("EMAIL_HOST_PASSWORD", "")
    sender_name  = notif.get("sender_name",  "Asguard Watchdog")
    sender_email = notif.get("sender_email", smtp_user)

    if not smtp_user or not smtp_pass:
        logger.warning("Notifications email: identifiants SMTP manquants")
        return

    try:
        msg = EmailMessage()
        msg["Subject"] = f"[Asguard] {subject}"
        msg["From"]    = f"{sender_name} <{sender_email}>"
        msg["To"]      = ", ".join(recipients)
        msg.set_content(plain)
        msg.add_alternative(html, subtype="html")
        # timeout is ESSENTIAL: without it, SMTP connect (DNS + TCP to the mail
        # server) hangs ~2 min when the WAN is down, holding a uvicorn worker
        # thread hostage and freezing the local UI. Bound every SMTP step.
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as s:
            s.ehlo()
            s.starttls()
            s.login(smtp_user, smtp_pass)
            s.send_message(msg)
        logger.info(f"Email envoyé : {subject} → {recipients}")
    except Exception as exc:
        logger.error(f"Échec email : {exc}")


# ── ntfy.sh ────────────────────────────────────────────────────────────────────

def _send_ntfy(title: str, body: str, priority: str = "default", tags: str = "shield"):
    """Send a push notification via ntfy.sh (free, no account needed)."""
    import requests as _req
    notif = _load_notif_config()
    nt = notif.get("ntfy", {})
    if not nt.get("enabled"):
        return
    topic = nt.get("topic", "").strip()
    if not topic:
        logger.warning("ntfy: topic manquant dans watchdog_config.json")
        return
    try:
        safe_title = title.encode("ascii", "replace").decode("ascii")
        _req.post(
            f"https://ntfy.sh/{topic}",
            data=body.encode("utf-8"),
            headers={
                "Title":    safe_title,
                "Priority": priority,
                "Tags":     tags,
            },
            timeout=10,
        )
        logger.info(f"ntfy notification envoyée : {title}")
    except Exception as exc:
        logger.error(f"ntfy notification échouée : {exc}")


# ── Slack / Discord (webhook-based, no SDK required) ──────────────────────────
# ── Backup events ──────────────────────────────────────────────────────────────

# ── VM Snapshot restore events ────────────────────────────────────────────────

# ── Restore events ────────────────────────────────────────────────────────────

def notify_restore_started(backup_id: str, mode: str = "safe"):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    mode_label = "Full UI Safe" if mode == "ui_full" else ("Full DR" if mode == "complete" else "Safe")
    availability = (
        "Mode UI-safe : l'interface reste disponible, sauf brève latence."
        if mode == "ui_full"
        else "L'interface sera indisponible ~2-3 min."
    )
    _send_ntfy(
        title=f"Restauration démarrée — {mode_label}",
        body=f"Backup : {backup_id}\nMode : {mode_label}\nHeure : {ts}\n{availability}",
        priority="high",
        tags="arrows_counterclockwise,rotating_light,shield",
    )
    html = _build_html(
        title=f"🔄 Restauration {mode_label} démarrée",
        color="#d97706",
        badge_label="RESTAURATION EN COURS",
        badge_color="#d97706",
        rows=[
            ("Backup",   backup_id,   None),
            ("Mode",     mode_label,  None),
            ("Heure",    ts,          None),
            ("Statut",   f"En cours — {availability}", "#d97706"),
        ],
    )
    send_notification(
        f"Restauration {mode_label} démarrée",
        html,
        f"Restauration démarrée\nBackup: {backup_id}\nMode: {mode_label}\nHeure: {ts}",
    )


def notify_restore_completed(backup_id: str, mode: str, success: bool,
                              duration_s=None, components_ok=0, components_failed=0):
    ts      = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    mode_label = "Full UI Safe" if mode == "ui_full" else ("Full DR" if mode == "complete" else "Safe")
    ok      = success
    color   = "#16a34a" if ok else "#dc2626"
    badge   = "RESTAURATION RÉUSSIE" if ok else "RESTAURATION ÉCHOUÉE"
    status  = "✓ Système restauré et opérationnel" if ok else "✗ Erreur durant la restauration"
    dur_str = f"{int(duration_s)}s" if duration_s else "—"

    _send_ntfy(
        title=f"Restauration {'réussie' if ok else 'ÉCHOUÉE'} — {mode_label}",
        body=(
            f"Backup : {backup_id}\nMode : {mode_label}\n"
            f"Composants OK : {components_ok} | Échecs : {components_failed}\n"
            f"Durée : {dur_str}\nHeure : {ts}"
        ),
        priority="default" if ok else "urgent",
        tags="white_check_mark,shield" if ok else "x,shield,rotating_light",
    )
    html = _build_html(
        title=f"{'✓' if ok else '✗'} Restauration {mode_label} {'réussie' if ok else 'échouée'}",
        color=color, badge_label=badge, badge_color=color,
        rows=[
            ("Backup",           backup_id,             None),
            ("Mode",             mode_label,            None),
            ("Statut",           status,                color),
            ("Composants OK",    str(components_ok),    "#16a34a"),
            ("Composants KO",    str(components_failed), "#dc2626" if components_failed else None),
            ("Durée",            dur_str,               None),
            ("Heure",            ts,                    None),
        ],
    )
    send_notification(
        f"Restauration {mode_label} {'réussie ✓' if ok else 'échouée ✗'}",
        html,
        f"Restauration {'réussie' if ok else 'échouée'}\nBackup: {backup_id}\nStatut: {status}\nHeure: {ts}",
    )
    # In-app alert (bell icon) — restore events were previously push/email only.
    write_in_app_alert(
        "restore",
        f"Restauration {mode_label} {'réussie' if ok else 'échouée'}",
        f"{backup_id} · {components_ok} OK"
        + (f" / {components_failed} KO" if components_failed else ""),
        "success" if ok else "error",
    )


# ── Firewall events ────────────────────────────────────────────────────────────

def notify_firewall_rule_change(action, rule_desc="", interface="", policy="", rule_type=""):
    """Called when a firewall rule is added, updated, or deleted."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    color_map    = {"ajoutée": "#16a34a", "supprimée": "#dc2626", "modifiée": "#f59e0b"}
    tags_map     = {"ajoutée": "white_check_mark,lock", "supprimée": "wastebasket,lock", "modifiée": "pencil,lock"}
    color = color_map.get(action.lower(), "#2563eb")

    _send_ntfy(
        title=f"Firewall — Règle {action}",
        body=f"{rule_desc or '—'}\nInterface : {interface or '—'}\nPolitique : {policy or '—'} | {rule_type or '—'}\nHeure : {ts}",
        priority="default",
        tags=tags_map.get(action.lower(), "lock,shield"),
    )
    html = _build_html(
        title=f"🔒 Règle firewall {action}",
        color=color,
        badge_label=f"RÈGLE {action.upper()}",
        badge_color=color,
        rows=[
            ("Action",      action,           color),
            ("Description", rule_desc or "—", None),
            ("Interface",   interface or "—", None),
            ("Politique",   policy or "—",    None),
            ("Direction",   rule_type or "—", None),
            ("Heure",       ts,               None),
        ],
    )
    send_notification(
        f"Firewall – Règle {action}",
        html,
        f"Règle firewall {action} : {rule_desc} sur {interface} à {ts}",
    )
    write_in_app_alert(
        "firewall_rule",
        f"Règle firewall {action}",
        f"{rule_desc or '—'} · {interface or '—'} · {policy or '—'}",
        "warning" if action.lower() in ("supprimée", "deleted") else "info",
    )


# ── WAF events ─────────────────────────────────────────────────────────────────

def notify_waf_alert(new_count, samples=None):
    """Called when WAF synchronization finds new violations."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [f"{new_count} violation(s) ModSecurity détectée(s)"]
    if samples:
        for i, s in enumerate(samples[:3], 1):
            src = s.get("source") or "?"
            msg = (s.get("message") or "—")[:80]
            lines.append(f"{i}. {src} — {msg}")
    lines.append(f"Heure : {ts}")
    _send_ntfy(
        title=f"Alerte WAF — {new_count} violation(s)",
        body="\n".join(lines),
        priority="high",
        tags="warning,shield",
    )

    rows = [
        ("Nouvelles violations", str(new_count), "#dc2626"),
        ("Heure de détection",   ts,             None),
    ]
    if samples:
        for i, s in enumerate(samples[:3], 1):
            src = s.get("source") or "—"
            msg = (s.get("message") or "—")[:80]
            rows.append((f"Alerte #{i}", f"{src} — {msg}", "#dc2626"))
    html = _build_html(
        title="⚠ Alerte WAF – Violations détectées",
        color="#dc2626", badge_label="ALERTE WAF", badge_color="#dc2626", rows=rows,
    )
    send_notification(
        f"WAF : {new_count} violation(s) détectée(s)",
        html,
        f"WAF : {new_count} nouvelles violation(s) détectée(s) à {ts}",
    )
    write_in_app_alert(
        "waf_alert",
        f"WAF : {new_count} violation(s)",
        f"ModSecurity a détecté {new_count} nouvelle(s) violation(s)",
        "warning",
    )


# ── IDS/IPS events ─────────────────────────────────────────────────────────────

def notify_ids_alert(new_count, sample_log=""):
    """Called when IDS/IPS (Suricata) detects new alert lines."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    body = f"{new_count} alerte(s) Suricata détectée(s)\nMoteur : Suricata IDS/IPS\nHeure : {ts}"
    if sample_log:
        body += f"\n---\n{sample_log[:200]}"
    _send_ntfy(
        title=f"Alerte IDS/IPS — {new_count} alerte(s) Suricata",
        body=body,
        priority="urgent",
        tags="rotating_light,shield",
    )

    rows = [
        ("Nouvelles alertes", str(new_count),     "#f59e0b"),
        ("Moteur",            "Suricata IDS/IPS", None),
        ("Heure",             ts,                 None),
    ]
    if sample_log:
        rows.append(("Extrait", sample_log[:120], "#f59e0b"))
    html = _build_html(
        title="🔍 Alerte IDS/IPS – Suricata",
        color="#f59e0b", badge_label="ALERTE IDS/IPS", badge_color="#f59e0b", rows=rows,
    )
    send_notification(
        f"IDS/IPS Suricata : {new_count} alerte(s)",
        html,
        f"Suricata : {new_count} alerte(s) IDS/IPS détectée(s) à {ts}",
    )
    write_in_app_alert(
        "ids_alert",
        f"IDS/IPS : {new_count} alerte(s) Suricata",
        f"Suricata a détecté {new_count} nouvelle(s) alerte(s) IDS/IPS",
        "warning",
    )


# ── Service events ─────────────────────────────────────────────────────────────

# Heuristic cause patterns — matched against journalctl output to give the
# operator a one-line "why" instead of raw logs. Ordered by specificity:
# more specific patterns must come first.
_SERVICE_CAUSE_PATTERNS: list[tuple[str, str]] = [
    (r"Address already in use",
     "Port déjà utilisé par un autre processus (collision de port)"),
    (r"bind\(\) to .*:(\d+) failed.*?\((\d+):",
     "Échec du bind() sur le port — adresse occupée ou permission refusée"),
    (r"Permission denied",
     "Accès refusé (capacité manquante ou permission filesystem)"),
    (r"No such file or directory",
     "Fichier de configuration ou binaire introuvable"),
    (r"could not load .*?certificate",
     "Certificat TLS introuvable ou illisible"),
    (r"emerg.*?\[crit\].*?config",
     "Erreur fatale dans la configuration"),
    (r"unknown directive",
     "Directive inconnue dans la configuration"),
    (r"syntax error|Configuration parsing error",
     "Erreur de syntaxe dans le fichier de configuration"),
    (r"Failed to start.*?Dependency failed",
     "Dépendance systemd échouée"),
    (r"Failed to start.*?Condition.*?failed",
     "Condition de démarrage non satisfaite (ConditionPath/ConditionUser…)"),
    (r"Main process exited.*?code=exited.*?status=(\d+)",
     "Le processus principal a quitté avec un code d'erreur"),
    (r"Killed.*?signal=SIGKILL|out-of-memory",
     "Processus tué par OOM killer (mémoire insuffisante)"),
    (r"timed out",
     "Démarrage trop lent — timeout systemd dépassé"),
    (r"connection refused",
     "Connexion refusée vers une dépendance (DB, upstream, socket)"),
    (r"nginx: \[emerg\] (.+)",
     "Erreur nginx : {0}"),
    (r"could not bind .*?:(\d+)",
     "Impossible de binder le port — conflit ou privilège insuffisant"),
]


def _diagnose_service_failure(unit: str) -> dict:
    """Probe systemctl + journalctl to extract a structured technical cause
    for a failed service. Never raises — returns an empty dict on any error.
    The returned dict is safe to embed in notifications and in-app alerts.

    Shape:
        {
          "unit":         "nginx.service",
          "active_state": "failed" | "inactive" | ...,
          "sub_state":    "failed" | "dead" | ...,
          "result":       "exit-code" | "signal" | "core-dump" | ...,
          "exit_code":    "1",
          "main_pid":     "0",
          "since":        "Mon 2026-05-18 16:30:00 UTC; 5min ago",
          "load_error":   "",                   # optional, set when unit not found
          "cause":        "Port déjà utilisé… (heuristique)",
          "last_logs":    ["line1", "line2", ...],  # up to 8 lines, latest first
        }
    """
    import re
    import subprocess as _sub

    # "ipsec" is a legacy alias kept in a few service tables, but there is NO
    # `ipsec.service` systemd unit on this appliance — the real IPsec daemon is
    # `strongswan`. Probing "ipsec" returns "NoSuchUnit: ipsec.service not found",
    # which surfaced as a scary false "Unit illisible" alert. Map it to the real
    # unit so the diagnosis reflects strongswan's actual state.
    if unit in ("ipsec", "ipsec.service"):
        unit = "strongswan"

    if not unit:
        return {}
    # Allow either "nginx" or "nginx.service" / "uvicorn.service" etc.
    full_unit = unit if "." in unit else f"{unit}.service"

    info: dict = {"unit": full_unit, "cause": "", "last_logs": []}

    # 1. `systemctl show` — machine-parseable key=value, no localisation.
    try:
        r = _sub.run(
            ["sudo", "-n", "systemctl", "show", full_unit,
             "--property=ActiveState,SubState,Result,ExecMainStatus,"
             "ExecMainPID,LoadError,ActiveEnterTimestamp,InvocationID"],
            capture_output=True, text=True, timeout=5,
        )
        for line in (r.stdout or "").splitlines():
            if "=" not in line:
                continue
            k, _, v = line.partition("=")
            k = k.strip(); v = v.strip()
            if k == "ActiveState":            info["active_state"] = v
            elif k == "SubState":             info["sub_state"]    = v
            elif k == "Result":               info["result"]       = v
            elif k == "ExecMainStatus":       info["exit_code"]    = v
            elif k == "ExecMainPID":          info["main_pid"]     = v
            elif k == "LoadError":            info["load_error"]   = v
            elif k == "ActiveEnterTimestamp": info["since"]        = v
    except Exception:
        pass

    # 2. Last logs from the journal — `--no-pager` so it doesn't block on stdin,
    # `-n 8 -o cat` to keep only the raw message text without the timestamp
    # spam (we already have ActiveEnterTimestamp for that).
    try:
        r = _sub.run(
            ["sudo", "-n", "journalctl", "-u", full_unit,
             "-n", "8", "--no-pager", "-o", "cat"],
            capture_output=True, text=True, timeout=8,
        )
        lines = [ln.strip() for ln in (r.stdout or "").splitlines() if ln.strip()]
        # Filter out the noisy "Started X" / "Stopped X" lines that surround
        # every restart attempt — they aren't a cause, they're a consequence.
        lines = [ln for ln in lines
                 if not (ln.startswith("Started ") or ln.startswith("Stopped "))]
        info["last_logs"] = lines[-8:]
    except Exception:
        pass

    # 3. Heuristic root-cause from the log patterns.
    joined = "\n".join(info["last_logs"])
    for pattern, template in _SERVICE_CAUSE_PATTERNS:
        m = re.search(pattern, joined, re.IGNORECASE)
        if m:
            try:
                info["cause"] = template.format(*m.groups())
            except (IndexError, KeyError):
                info["cause"] = template
            break

    # Fallback: if we have a non-zero exit code but no pattern matched, surface
    # the code itself so the operator at least knows it's not just "down".
    if not info["cause"]:
        if info.get("load_error"):
            info["cause"] = f"Unit illisible : {info['load_error']}"
        elif info.get("result") and info["result"] not in ("success", ""):
            info["cause"] = (
                f"Échec systemd (result={info['result']}, "
                f"exit_code={info.get('exit_code', '?')})"
            )
        elif info.get("active_state") in ("inactive", "failed"):
            info["cause"] = (
                f"Service {info['active_state']} — aucune cause précise détectée "
                f"dans les 8 dernières lignes du journal"
            )

    return info


def notify_service_action(service_name: str, action: str, success: bool, display_name: str = ""):
    """Called when a service is started, stopped, restarted, enabled or disabled."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    label = display_name or service_name
    action_labels = {
        "start": "démarré", "stop": "arrêté", "restart": "redémarré",
        "enable": "activé", "disable": "désactivé",
    }
    action_fr = action_labels.get(action.lower(), action)
    ok = success
    color = "#16a34a" if ok else "#dc2626"
    badge = f"SERVICE {action_fr.upper()}" if ok else f"ÉCHEC {action_fr.upper()}"
    icon_map = {
        "start": "▶", "stop": "⏹", "restart": "↺", "enable": "✓", "disable": "✗",
    }
    icon = icon_map.get(action.lower(), "⚙")
    priority = "default" if ok else "high"
    tags = "gear,white_check_mark" if ok else "gear,x"

    # When the action FAILED, probe systemd for the actual technical cause
    # so the notification tells the operator *why* rather than just *what*.
    diag = _diagnose_service_failure(service_name) if not ok else {}
    cause     = diag.get("cause", "") if diag else ""
    last_logs = diag.get("last_logs", []) if diag else []

    # Compose a multi-line body that includes the cause + tail of the journal.
    ntfy_body_lines = [
        f"Service : {label}",
        f"Action  : {action_fr}",
        f"Statut  : {'Succès' if ok else 'Échec'}",
        f"Heure   : {ts}",
    ]
    if cause:
        ntfy_body_lines.append(f"Cause   : {cause}")
    if diag.get("active_state"):
        ntfy_body_lines.append(
            f"État    : {diag['active_state']} / {diag.get('sub_state', '?')}"
            + (f" (exit={diag['exit_code']})" if diag.get("exit_code") not in (None, "", "0") else "")
        )
    if last_logs:
        ntfy_body_lines.append("Logs    :")
        for ln in last_logs[-4:]:           # ntfy is short — keep the last 4
            ntfy_body_lines.append(f"  {ln[:140]}")

    _send_ntfy(
        title=f"Service {label} — {action_fr}",
        body="\n".join(ntfy_body_lines),
        priority=priority,
        tags=tags,
    )

    # Build the email/HTML — richer than the ntfy body, with the full 8-line
    # journal tail in a <pre> block.
    rows = [
        ("Service", label,                           None),
        ("Action",  action_fr,                       color),
        ("Statut",  "✓ Succès" if ok else "✗ Échec", color),
        ("Heure",   ts,                              None),
    ]
    if cause:
        rows.append(("Cause technique", cause, "#dc2626"))
    if diag.get("active_state"):
        rows.append((
            "État systemd",
            f"{diag['active_state']} / {diag.get('sub_state', '?')}"
            + (f"  •  exit={diag['exit_code']}" if diag.get("exit_code") not in (None, "", "0") else ""),
            None,
        ))
    if diag.get("since"):
        rows.append(("Depuis", diag["since"], None))

    html = _build_html(
        title=f"{icon} Service {label} {action_fr}",
        color=color, badge_label=badge, badge_color=color,
        rows=rows,
        footer_note=(
            "Dernières lignes du journal systemd :<br/><pre style='background:#f3f4f6;"
            "padding:8px;border-radius:6px;font-size:11px;line-height:1.45;"
            "white-space:pre-wrap;color:#1f2937'>"
            + "\n".join(ln.replace("<", "&lt;") for ln in last_logs)
            + "</pre>"
        ) if last_logs else "",
    )
    send_notification(
        f"Service {label} {action_fr}",
        html,
        f"Service {label} {action_fr} — {'Succès' if ok else 'Échec'} — {ts}"
        + (f" — {cause}" if cause else ""),
    )

    # In-app alert: keep the visible message short, push the diagnostic into
    # `details` so the UI can render a collapsible "Why did this fail?" panel.
    in_app_message = (
        f"{'Succès' if ok else 'Échec'} · {label}"
        + (f" — {cause}" if cause else "")
    )
    write_in_app_alert(
        "service_action",
        f"Service {label} {action_fr}",
        in_app_message,
        "info" if ok else "warning",
        details=({
            "unit":         diag.get("unit"),
            "cause":        cause,
            "active_state": diag.get("active_state"),
            "sub_state":    diag.get("sub_state"),
            "result":       diag.get("result"),
            "exit_code":    diag.get("exit_code"),
            "since":        diag.get("since"),
            "last_logs":    last_logs,
        } if diag else None),
    )


# ── Auth events ────────────────────────────────────────────────────────────────

def notify_user_login(username: str, ip: str = "", success: bool = True, action: str = "login"):
    """Called on user login or logout."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    action_map = {"login": "connecté", "logout": "déconnecté", "failed": "tentative échouée"}
    action_fr = action_map.get(action, action)
    ok = success
    color = "#16a34a" if ok else "#dc2626"
    badge = f"AUTH — {action_fr.upper()}"
    priority = "default" if ok else "high"
    tags = "key,white_check_mark" if ok else "key,warning"

    _send_ntfy(
        title=f"Asguard — Utilisateur {action_fr}",
        body=f"Utilisateur : {username}\nAction : {action_fr}\nIP : {ip or '—'}\nHeure : {ts}",
        priority=priority,
        tags=tags,
    )
    html = _build_html(
        title=f"🔑 Utilisateur {action_fr}",
        color=color, badge_label=badge, badge_color=color,
        rows=[
            ("Utilisateur", username,              None),
            ("Action",      action_fr,             color),
            ("IP source",   ip or "—",             None),
            ("Heure",       ts,                    None),
        ],
    )
    send_notification(
        f"Auth — {username} {action_fr}",
        html,
        f"Utilisateur {username} {action_fr} depuis {ip or '?'} à {ts}",
    )
    write_in_app_alert(
        "auth_login",
        f"Utilisateur {username} {action_fr}",
        f"Depuis {ip or 'IP inconnue'}",
        "info" if ok else "warning",
    )


# ── User management events ─────────────────────────────────────────────────────

def notify_user_change(action: str, username: str, changed_by: str = ""):
    """Called when a user account is created, deleted or modified."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    action_map = {"créé": "#16a34a", "supprimé": "#dc2626", "modifié": "#f59e0b"}
    color = action_map.get(action, "#2563eb")
    tags_map = {"créé": "bust_in_silhouette,white_check_mark", "supprimé": "bust_in_silhouette,wastebasket", "modifié": "bust_in_silhouette,pencil"}
    tags = tags_map.get(action, "bust_in_silhouette")

    _send_ntfy(
        title=f"Gestion utilisateurs — Compte {action}",
        body=f"Utilisateur : {username}\nAction : {action}\nPar : {changed_by or '—'}\nHeure : {ts}",
        priority="default",
        tags=tags,
    )
    html = _build_html(
        title=f"👤 Compte utilisateur {action}",
        color=color, badge_label=f"UTILISATEUR {action.upper()}", badge_color=color,
        rows=[
            ("Utilisateur", username,          None),
            ("Action",      action,            color),
            ("Par",         changed_by or "—", None),
            ("Heure",       ts,                None),
        ],
    )
    send_notification(
        f"Utilisateur {action} : {username}",
        html,
        f"Compte utilisateur {action} : {username} — par {changed_by or '?'} à {ts}",
    )
    write_in_app_alert(
        "user_change",
        f"Compte utilisateur {action} : {username}",
        f"Par {changed_by or 'utilisateur inconnu'}",
        "warning" if action == "supprimé" else "info",
    )


# ── Certificate events ─────────────────────────────────────────────────────────

def notify_certificate_change(action: str, cert_name: str, cert_type: str = ""):
    """Called when a certificate or CA is created, deleted or revoked."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    color_map = {"créé": "#16a34a", "supprimé": "#dc2626", "révoqué": "#f59e0b", "non-révoqué": "#2563eb"}
    color = color_map.get(action, "#2563eb")
    tags_map = {"créé": "lock,white_check_mark", "supprimé": "lock,wastebasket", "révoqué": "lock,warning", "non-révoqué": "lock"}
    tags = tags_map.get(action, "lock")

    _send_ntfy(
        title=f"Certificat {action} — {cert_name}",
        body=f"Certificat : {cert_name}\nType : {cert_type or '—'}\nAction : {action}\nHeure : {ts}",
        priority="default",
        tags=tags,
    )
    html = _build_html(
        title=f"🔐 Certificat {action}",
        color=color, badge_label=f"CERTIFICAT {action.upper()}", badge_color=color,
        rows=[
            ("Certificat", cert_name,      None),
            ("Type",       cert_type or "—", None),
            ("Action",     action,         color),
            ("Heure",      ts,             None),
        ],
    )
    send_notification(
        f"Certificat {action} : {cert_name}",
        html,
        f"Certificat {action} : {cert_name} ({cert_type or '?'}) à {ts}",
    )
    write_in_app_alert(
        "certificate",
        f"Certificat {action} : {cert_name}",
        f"Type : {cert_type or 'inconnu'}",
        "warning" if action in ("supprimé", "révoqué") else "info",
    )


# ── IPSec events ───────────────────────────────────────────────────────────────

def notify_ipsec_change(action: str, tunnel_name: str = "", details: str = ""):
    """Called when an IPSec tunnel is created, deleted or updated."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    color_map = {"créé": "#16a34a", "supprimé": "#dc2626", "modifié": "#f59e0b"}
    color = color_map.get(action, "#2563eb")
    tags_map = {"créé": "shield,white_check_mark", "supprimé": "shield,wastebasket", "modifié": "shield,pencil"}
    tags = tags_map.get(action, "shield")

    _send_ntfy(
        title=f"IPSec — Tunnel {action}",
        body=f"Tunnel : {tunnel_name or '—'}\nAction : {action}\n{('Détail : ' + details) if details else ''}\nHeure : {ts}",
        priority="default",
        tags=tags,
    )
    rows = [
        ("Tunnel", tunnel_name or "—", None),
        ("Action", action,             color),
        ("Heure",  ts,                 None),
    ]
    if details:
        rows.insert(2, ("Détail", details, None))
    html = _build_html(
        title=f"🛡 IPSec — Tunnel {action}",
        color=color, badge_label=f"IPSEC {action.upper()}", badge_color=color, rows=rows,
    )
    send_notification(
        f"IPSec — Tunnel {action} : {tunnel_name}",
        html,
        f"IPSec tunnel {action} : {tunnel_name} à {ts}",
    )
    write_in_app_alert(
        "ipsec_change",
        f"Tunnel IPsec {action}",
        f"{tunnel_name or '—'}" + (f" · {details}" if details else ""),
        "warning" if action == "supprimé" else "info",
    )


# ── NAT events ─────────────────────────────────────────────────────────────────

def notify_nat_change(action: str, rule_type: str = "", rule_desc: str = ""):
    """Called when a NAT rule (DNAT/SNAT/1-to-1) is created, deleted or updated."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    color_map = {"créée": "#16a34a", "supprimée": "#dc2626", "modifiée": "#f59e0b"}
    color = color_map.get(action, "#2563eb")
    tags_map = {"créée": "arrows_counterclockwise,white_check_mark", "supprimée": "arrows_counterclockwise,wastebasket", "modifiée": "arrows_counterclockwise,pencil"}
    tags = tags_map.get(action, "arrows_counterclockwise")

    _send_ntfy(
        title=f"NAT — Règle {action}",
        body=f"Type : {rule_type or '—'}\nRègle : {rule_desc or '—'}\nHeure : {ts}",
        priority="default",
        tags=tags,
    )
    html = _build_html(
        title=f"↔ Règle NAT {action}",
        color=color, badge_label=f"NAT {action.upper()}", badge_color=color,
        rows=[
            ("Type",   rule_type or "—",  None),
            ("Règle",  rule_desc or "—",  None),
            ("Action", action,            color),
            ("Heure",  ts,                None),
        ],
    )
    send_notification(
        f"NAT — Règle {action} ({rule_type})",
        html,
        f"Règle NAT {action} ({rule_type}) : {rule_desc or '?'} à {ts}",
    )
    write_in_app_alert(
        "nat_change",
        f"Règle NAT {action}",
        f"{rule_type or '—'} · {rule_desc or '—'}",
        "warning" if action == "supprimée" else "info",
    )


# ── Routing events ─────────────────────────────────────────────────────────────

def notify_routing_change(action: str, dest: str = "", gateway: str = ""):
    """Called when a static route is created, deleted or updated."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    color_map = {"créée": "#16a34a", "supprimée": "#dc2626", "modifiée": "#f59e0b"}
    color = color_map.get(action, "#2563eb")

    _send_ntfy(
        title=f"Routage — Route {action}",
        body=f"Destination : {dest or '—'}\nPasserelle : {gateway or '—'}\nHeure : {ts}",
        priority="default",
        tags="arrows_counterclockwise,shield",
    )
    html = _build_html(
        title=f"🗺 Route statique {action}",
        color=color, badge_label=f"ROUTAGE {action.upper()}", badge_color=color,
        rows=[
            ("Destination", dest or "—",    None),
            ("Passerelle",  gateway or "—", None),
            ("Action",      action,         color),
            ("Heure",       ts,             None),
        ],
    )
    send_notification(
        f"Routage — Route {action}",
        html,
        f"Route statique {action} : {dest or '?'} via {gateway or '?'} à {ts}",
    )
    write_in_app_alert(
        "routing_change",
        f"Route statique {action}",
        f"{dest or '—'} via {gateway or '—'}",
        "warning" if action == "supprimée" else "info",
    )


# ── Network/Interface events ───────────────────────────────────────────────────
