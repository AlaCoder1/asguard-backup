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


def _alerts_block(cfg: dict) -> dict:
    """The new "alerts" sub-section. Created on first access with sensible
    defaults so a fresh appliance does not start completely silent."""
    block = cfg.get("alerts")
    if not isinstance(block, dict):
        block = {}
    block.setdefault("severity_threshold", "info")
    block.setdefault("quiet_hours", {"enabled": False, "start_hour": 22, "end_hour": 7,
                                      "exempt_critical": True})
    block.setdefault("slack",  {"enabled": False, "webhook_url": ""})
    # Twilio: enterprise SMS via REST. account_sid + auth_token + a sender
    # number, and a list of recipient phone numbers (E.164 format).
    block.setdefault("twilio", {"enabled": False, "account_sid": "",
                                 "auth_token": "", "from_number": "",
                                 "recipients": [], "min_severity": "critical"})
    # Subscription matrix: by default email + ntfy fire on every category.
    # Twilio SMS is opt-in per category (intended for on-call escalation),
    # Slack is opt-in per team preference.
    subs = block.get("subscriptions") or {}
    for cat in CATEGORIES:
        cur = subs.get(cat["id"]) or {}
        for ch in CHANNELS:
            cur.setdefault(ch, ch in ("email", "ntfy"))
        subs[cat["id"]] = cur
    block["subscriptions"] = subs
    return block


def _should_notify(category: str | None, channel: str, severity: str = "info") -> bool:
    """Routing gate. Returns False to suppress a notification when:
      • the category is not subscribed to this channel,
      • the event severity is below the global threshold,
      • we're inside the configured quiet hours (and the event isn't critical
        when 'exempt_critical' is on).
    Backward compat: when no category is supplied the legacy on/off toggle
    (email_enabled / ntfy.enabled) is used as before — older notify_* calls
    keep working unchanged."""
    cfg = _load_notif_config()

    if not category:
        # No tag = legacy path; just respect the per-channel master switch.
        if channel == "email":
            return bool(cfg.get("email_enabled"))
        if channel == "ntfy":
            return bool((cfg.get("ntfy") or {}).get("enabled"))
        return False

    alerts = _alerts_block(cfg)

    # Subscription matrix
    sub = (alerts.get("subscriptions") or {}).get(category) or {}
    if not sub.get(channel):
        return False

    # Channel master switch
    if channel == "email" and not cfg.get("email_enabled"):
        return False
    if channel == "ntfy" and not (cfg.get("ntfy") or {}).get("enabled"):
        return False
    if channel == "slack" and not (alerts.get("slack") or {}).get("enabled"):
        return False
    if channel == "twilio":
        tw = alerts.get("twilio") or {}
        if not tw.get("enabled"):
            return False
        # SMS is expensive — enforce a per-channel severity floor on top of
        # the global threshold so info-level events never trigger an SMS even
        # if mistakenly subscribed.
        tw_floor = SEVERITY_RANK.get(tw.get("min_severity", "critical"), 2)
        if SEVERITY_RANK.get(severity, 0) < tw_floor:
            return False

    # Severity threshold
    rank = SEVERITY_RANK.get(severity, 0)
    threshold = SEVERITY_RANK.get(alerts.get("severity_threshold", "info"), 0)
    if rank < threshold:
        return False

    # Quiet hours
    qh = alerts.get("quiet_hours") or {}
    if qh.get("enabled"):
        if qh.get("exempt_critical") and severity == "critical":
            pass  # critical bypasses quiet hours
        else:
            now_h = datetime.now().hour
            start, end = int(qh.get("start_hour", 22)), int(qh.get("end_hour", 7))
            in_quiet = (start <= now_h or now_h < end) if start > end else (start <= now_h < end)
            if in_quiet:
                return False

    return True


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


def _save_notif_config(notif: dict) -> bool:
    """Persist the 'notifications' sub-section back to watchdog_config.json.
    Atomic via tmp + rename so a concurrent read never sees a half-written file."""
    try:
        full = _load_full_config()
        full["notifications"] = notif
        tmp = _WD_CONFIG.with_suffix(".tmp")
        tmp.write_text(json.dumps(full, indent=2, ensure_ascii=False))
        tmp.replace(_WD_CONFIG)
        return True
    except Exception as exc:
        logger.error("save notif config failed: %s", exc)
        return False


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
        with smtplib.SMTP(smtp_host, smtp_port) as s:
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


def ntfy_test():
    """Send a test notification to verify ntfy setup."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    _send_ntfy(
        title="Asguard — Test de connexion",
        body=f"ntfy est correctement configuré.\nHeure : {ts}",
        priority="default",
        tags="white_check_mark,shield",
    )


# ── Slack / Discord (webhook-based, no SDK required) ──────────────────────────
def _send_slack(title: str, body: str, severity: str = "info") -> None:
    import requests as _req
    alerts = _alerts_block(_load_notif_config())
    slack = alerts.get("slack") or {}
    if not slack.get("enabled"):
        return
    url = (slack.get("webhook_url") or "").strip()
    if not url:
        return
    color = {"critical": "#dc2626", "warning": "#f59e0b", "info": "#3b82f6"}.get(severity, "#3b82f6")
    payload = {
        "username": "Asguard",
        "icon_emoji": ":shield:",
        "attachments": [{
            "color": color,
            "title": f"[Asguard] {title}",
            "text": body,
            "footer": "Asguard Watchdog",
            "ts": int(datetime.now(timezone.utc).timestamp()),
        }],
    }
    try:
        _req.post(url, json=payload, timeout=10)
        logger.info(f"Slack notification envoyée : {title}")
    except Exception as exc:
        logger.error(f"Slack notification échouée : {exc}")


def _send_twilio_sms(title: str, body: str, severity: str = "info") -> None:
    """Twilio SMS via direct REST call (no SDK dependency). Used for on-call
    escalation — SMS is the highest-priority, lowest-bandwidth channel, so we
    send a single compact message per recipient."""
    import requests as _req
    alerts = _alerts_block(_load_notif_config())
    tw = alerts.get("twilio") or {}
    if not tw.get("enabled"):
        return
    sid   = (tw.get("account_sid") or "").strip()
    token = (tw.get("auth_token")  or "").strip()
    sender = (tw.get("from_number") or "").strip()
    recipients = [r.strip() for r in (tw.get("recipients") or []) if r and r.strip()]
    if not (sid and token and sender and recipients):
        logger.warning("Twilio: configuration incomplète (SID/token/from/recipients)")
        return

    # Compact body — SMS is 160 chars/segment, so we keep it short and
    # information-dense rather than dumping the full HTML.
    sev_tag = {"critical": "[CRIT]", "warning": "[WARN]", "info": "[INFO]"}.get(severity, "")
    sms = f"Asguard {sev_tag} {title}\n{body}"[:480]   # ≈ 3 segments max
    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"

    for to in recipients:
        try:
            r = _req.post(
                url,
                data={"From": sender, "To": to, "Body": sms},
                auth=(sid, token),
                timeout=15,
            )
            if r.status_code >= 400:
                logger.error("Twilio SMS rejected for %s: %s", to, r.text[:200])
            else:
                logger.info("Twilio SMS envoyé → %s", to)
        except Exception as exc:
            logger.error("Twilio SMS exception → %s : %s", to, exc)


def dispatch(category: str, title: str, body: str,
             severity: str = "info",
             html: str | None = None, plain: str | None = None,
             ntfy_priority: str = "default", ntfy_tags: str = "shield") -> None:
    """Single fan-out point. Each notify_* function should call this with its
    category — the routing matrix decides which channels actually fire."""
    if _should_notify(category, "email", severity):
        send_notification(title, html or f"<p>{body}</p>", plain or body)
    if _should_notify(category, "ntfy", severity):
        _send_ntfy(title=title, body=body, priority=ntfy_priority, tags=ntfy_tags)
    if _should_notify(category, "slack", severity):
        _send_slack(title, body, severity)
    if _should_notify(category, "twilio", severity):
        _send_twilio_sms(title, body, severity)


# ── Backup events ──────────────────────────────────────────────────────────────

def notify_backup_started(backup_type, backup_id=""):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    type_labels = {
        "safe_backup": "Sauvegarde Safe",
        "full_backup": "Sauvegarde Full DR",
        "db_backup":   "Sauvegarde Base de données",
    }
    label = type_labels.get(backup_type, backup_type)

    _send_ntfy(
        title=f"Sauvegarde démarrée — {label}",
        body=f"Type : {label}\nID : {backup_id or '—'}\nHeure : {ts}",
        priority="default",
        tags="arrows_counterclockwise,shield",
    )
    html = _build_html(
        title=f"🔄 {label} démarrée",
        color="#2563eb",
        badge_label="SAUVEGARDE EN COURS",
        badge_color="#2563eb",
        rows=[
            ("Type",   label,            None),
            ("ID",     backup_id or "—", None),
            ("Heure",  ts,               None),
            ("Statut", "En cours...",    "#2563eb"),
        ],
    )
    send_notification(f"{label} démarrée", html, f"Sauvegarde démarrée\nType: {label}\nHeure: {ts}")


def notify_backup_completed(backup_type, backup_id, success, duration_s=None, message=""):
    ts      = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    type_labels = {
        "safe_backup": "Sauvegarde Safe",
        "full_backup": "Sauvegarde Full DR",
        "db_backup":   "Sauvegarde Base de données",
    }
    type_labels.setdefault("custom_backup", "Sauvegarde personnalisée")
    label   = type_labels.get(backup_type, backup_type)
    ok      = success
    color   = "#16a34a" if ok else "#dc2626"
    badge   = "SUCCÈS" if ok else "ÉCHEC"
    status  = "✓ Terminée avec succès" if ok else "✗ Échec de la sauvegarde"
    dur_str = f"{int(duration_s)}s" if duration_s else "—"

    body = f"Type : {label}\nID : {backup_id or '—'}\nDurée : {dur_str}\nHeure : {ts}"
    if not ok and message:
        body += f"\nErreur : {message[:200]}"
    _send_ntfy(
        title=f"Sauvegarde {'réussie' if ok else 'ÉCHOUÉE'} — {label}",
        body=body,
        priority="default" if ok else "high",
        tags="white_check_mark,shield" if ok else "x,shield,rotating_light",
    )

    rows = [
        ("Type",   label,            None),
        ("ID",     backup_id or "—", None),
        ("Statut", status,           "#16a34a" if ok else "#dc2626"),
        ("Durée",  dur_str,          None),
        ("Heure",  ts,               None),
    ]
    if message:
        rows.append(("Détail", message, None))
    html = _build_html(
        title=f"{'✓' if ok else '✗'} {label} {'réussie' if ok else 'échouée'}",
        color=color, badge_label=badge, badge_color=color, rows=rows,
    )
    send_notification(
        f"{label} {'réussie ✓' if ok else 'échouée ✗'}",
        html,
        f"Sauvegarde {'réussie' if ok else 'échouée'}\nType: {label}\nStatut: {status}\nHeure: {ts}",
    )
    # In-app alert (bell icon) — backup events were previously push/email only.
    write_in_app_alert(
        "backup",
        f"{label} {'réussie' if ok else 'échouée'}",
        f"{backup_id or '—'}" + (f" · {message}" if message else ""),
        "success" if ok else "error",
    )


def notify_backup_scheduled(task_name, backup_type, cron_expr=""):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    type_labels = {
        "safe_backup": "Sauvegarde Safe",
        "full_backup": "Sauvegarde Full DR",
        "db_backup":   "Sauvegarde Base de données",
    }
    label = type_labels.get(backup_type, backup_type)

    _send_ntfy(
        title=f"Backup automatique déclenché — {label}",
        body=f"Tâche : {task_name}\nType : {label}\nCron : {cron_expr or '—'}\nHeure : {ts}",
        priority="low",
        tags="alarm_clock,shield",
    )
    html = _build_html(
        title="⏰ Sauvegarde automatique déclenchée",
        color="#7c3aed",
        badge_label="PLANIFIÉE",
        badge_color="#7c3aed",
        rows=[
            ("Tâche",         task_name,        None),
            ("Type",          label,            None),
            ("Planification", cron_expr or "—", None),
            ("Déclenchée à",  ts,               None),
        ],
    )
    send_notification(
        f"Sauvegarde automatique : {task_name}",
        html,
        f"Sauvegarde automatique déclenchée\nTâche: {task_name}\nType: {label}\nHeure: {ts}",
    )


def notify_missed_backup_catchup(task_name, backup_type, missed_at=""):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    type_labels = {
        "safe_backup": "Sauvegarde Safe",
        "full_backup": "Sauvegarde Full DR",
        "db_backup":   "Sauvegarde Base de données",
    }
    label = type_labels.get(backup_type, backup_type)

    _send_ntfy(
        title=f"⚠️ Sauvegarde manquée — Récupération déclenchée",
        body=f"Tâche : {task_name}\nType : {label}\nHeure prévue manquée : {missed_at or '—'}\nRécupération lancée à : {ts}",
        priority="high",
        tags="warning,arrows_counterclockwise,shield",
    )
    html = _build_html(
        title="⚠️ Sauvegarde manquée — Récupération en cours",
        color="#d97706",
        badge_label="MANQUÉE — RÉCUPÉRATION",
        badge_color="#d97706",
        rows=[
            ("Tâche",            task_name,       None),
            ("Type",             label,           None),
            ("Heure manquée",    missed_at or "—", "#d97706"),
            ("Récupération à",   ts,              None),
            ("Cause probable",   "Tâche planifiée non exécutée à l'heure prévue "
                                 "(VM éteinte au moment prévu, ou planificateur indisponible). "
                                 "Rattrapage automatique effectué.", None),
        ],
    )
    send_notification(
        f"⚠️ Sauvegarde manquée : {task_name}",
        html,
        f"Sauvegarde manquée détectée\nTâche: {task_name}\nType: {label}\nHeure manquée: {missed_at}\nRécupération lancée à: {ts}",
    )


# ── VM Snapshot restore events ────────────────────────────────────────────────

def notify_vm_snapshot_restore_started(snap_id: str):
    """Send alert BEFORE the snapshot restore kills the guest — Django won't be alive after."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    _send_ntfy(
        title="Restauration snapshot VM lancée",
        body=(
            f"Snapshot : {snap_id}\n"
            f"Heure : {ts}\n"
            "La VM va être restaurée puis redémarrée automatiquement.\n"
            "L'interface sera indisponible ~60 secondes."
        ),
        priority="high",
        tags="arrows_counterclockwise,rotating_light,computer,shield",
    )
    html = _build_html(
        title="🔄 Restauration snapshot VMware lancée",
        color="#d97706",
        badge_label="SNAPSHOT RESTORE",
        badge_color="#d97706",
        rows=[
            ("Snapshot", snap_id, None),
            ("Heure",    ts,      None),
            ("Impact",   "VM en cours de restauration — interface indisponible ~60s", "#d97706"),
            ("Action",   "Redémarrage automatique après restauration", None),
        ],
    )
    send_notification(
        "Restauration snapshot VM lancée",
        html,
        f"Restauration snapshot VM\nSnapshot: {snap_id}\nHeure: {ts}\nLa VM va redémarrer automatiquement.",
    )
    write_in_app_alert(
        "vm_snapshot_restore",
        "Restauration snapshot lancée",
        f"Snapshot : {snap_id} — interface indisponible ~120s",
        "warning",
    )


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


def notify_vm_resource_risk(cpu: float, memory: float, load_average: str = "",
                            reason: str = "Risque d'instabilite VM",
                            top_processes: list | None = None,
                            auto_fix: str = "",
                            recommendation: str = ""):
    """Critical resource pressure warning before a VM crash/service loss.

    Enriched with a live diagnostic (top processes) + the auto-remediation
    result (when one was attempted safely) + a one-line recommendation the
    operator can act on immediately. The goal is that the user reading the
    notification on their phone knows *what* is wrong, *what was tried*, and
    *what to do next* without having to log in.
    """
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    cpu_s = f"{cpu:.0f}%"
    mem_s = f"{memory:.0f}%"

    proc_lines = []
    for proc in (top_processes or [])[:5]:
        proc_lines.append(
            f"  • {proc.get('name', '?')} (PID {proc.get('pid', '?')}) "
            f"— CPU {proc.get('cpu', 0):.0f}% RAM {proc.get('mem', 0):.0f}%"
        )
    proc_block = ("\nTop processus :\n" + "\n".join(proc_lines)) if proc_lines else ""

    body = (
        f"{reason}\n"
        f"CPU : {cpu_s}\n"
        f"RAM : {mem_s}\n"
        f"Load average : {load_average or '—'}\n"
        + (f"\nAction automatique : {auto_fix}\n" if auto_fix else "")
        + (f"\nRecommandation : {recommendation}\n" if recommendation else "")
        + proc_block
        + f"\n\nHeure : {ts}"
    )
    _send_ntfy(
        title="Risque critique VM Asguard",
        body=body,
        priority="urgent",
        tags="warning,rotating_light,computer,shield",
    )

    rows = [
        ("Cause", reason, "#dc2626"),
        ("CPU", cpu_s, "#dc2626" if cpu >= 95 else "#d97706"),
        ("RAM", mem_s, "#dc2626" if memory >= 95 else "#d97706"),
        ("Load average", load_average or "—", None),
    ]
    if auto_fix:
        rows.append(("Action auto", auto_fix, "#16a34a"))
    if recommendation:
        rows.append(("Recommandation", recommendation, "#2563eb"))
    if proc_lines:
        rows.append(("Top processus",
                     "<br>".join(line.lstrip("  • ") for line in proc_lines),
                     None))
    rows.append(("Impact",
                 "Perte SSH/VS Code/API, services stoppés, VM suspendue/éteinte",
                 "#dc2626"))
    rows.append(("Heure", ts, None))

    html = _build_html(
        title="Risque critique VM Asguard",
        color="#dc2626",
        badge_label="RISQUE DE CRASH",
        badge_color="#dc2626",
        rows=rows,
        footer_note=(recommendation or
                     "Alerte proactive Asguard : réduire la charge ou prendre un snapshot stable avant intervention."),
    )
    send_notification(
        "Risque critique VM Asguard",
        html,
        body,
    )
    severity = "critical" if (cpu >= 95 or memory >= 95) else "warning"
    write_in_app_alert(
        "resource_risk",
        f"Risque {'critique' if severity == 'critical' else 'eleve'} VM",
        f"{reason} — CPU {cpu_s} · RAM {mem_s}"
        + (f" · {recommendation}" if recommendation else ""),
        severity,
    )


def notify_vm_resource_resolved(reason: str, duration_seconds: int,
                                auto_fix: str = ""):
    """Follow-up sent when sustained pressure drops back to normal.

    Confirms to the operator that the previously-alerted incident is over,
    so they don't keep wondering. Sent with low priority.
    """
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    mins = duration_seconds // 60
    secs = duration_seconds % 60
    duration = f"{mins}min{secs:02d}s" if mins else f"{secs}s"

    body = (
        f"La surcharge précédente est résolue.\n"
        f"Cause initiale : {reason}\n"
        f"Durée totale : {duration}\n"
        + (f"Action automatique appliquée : {auto_fix}\n" if auto_fix else "")
        + f"Heure : {ts}"
    )
    _send_ntfy(
        title="✓ VM Asguard — retour à la normale",
        body=body,
        priority="low",
        tags="white_check_mark,computer",
    )
    rows = [
        ("Statut",          "Résolu ✓",  "#16a34a"),
        ("Cause initiale",  reason,      None),
        ("Durée",           duration,    None),
    ]
    if auto_fix:
        rows.append(("Action auto",     auto_fix,    "#16a34a"))
    rows.append(("Heure",               ts,          None))
    html = _build_html(
        title="✓ VM Asguard — retour à la normale",
        color="#16a34a",
        badge_label="RÉSOLU",
        badge_color="#16a34a",
        rows=rows,
        footer_note="Aucune action requise. Conservé pour traçabilité.",
    )
    send_notification(
        "VM Asguard — retour à la normale",
        html,
        body,
    )
    write_in_app_alert(
        "resource_risk_resolved",
        "Retour à la normale",
        f"Surcharge résolue après {duration} — {reason}",
        "info",
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

def notify_network_change(action: str, interface: str = "", details: str = ""):
    """Called when a network interface is configured or deleted."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    color_map = {"configurée": "#16a34a", "supprimée": "#dc2626", "modifiée": "#f59e0b"}
    color = color_map.get(action, "#2563eb")

    _send_ntfy(
        title=f"Réseau — Interface {action}",
        body=f"Interface : {interface or '—'}\n{('Détail : ' + details) if details else ''}\nHeure : {ts}",
        priority="default",
        tags="satellite,shield",
    )
    rows = [
        ("Interface", interface or "—", None),
        ("Action",    action,           color),
        ("Heure",     ts,               None),
    ]
    if details:
        rows.insert(2, ("Détail", details, None))
    html = _build_html(
        title=f"🌐 Interface réseau {action}",
        color=color, badge_label=f"RÉSEAU {action.upper()}", badge_color=color, rows=rows,
    )
    send_notification(
        f"Réseau — Interface {action} : {interface}",
        html,
        f"Interface réseau {action} : {interface} à {ts}",
    )
    write_in_app_alert(
        "network_change",
        f"Interface {interface} {action}",
        details or "—",
        "warning" if action == "supprimée" else "info",
    )
