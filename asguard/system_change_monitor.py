#!/usr/bin/env python3
"""Asguard system-change monitor.

Detects changes to the appliance's OS-level identity made OUTSIDE the web UI
(e.g. from the console: `passwd`, `useradd`, `hostnamectl`, edits to sshd_config
or sudoers) and pushes a notification (ntfy + email) describing exactly what
changed. Runs periodically from a systemd timer. Stdlib only — no Django.

Baseline is stored at /var/backups/asguard/system_baseline.json. First run just
establishes the baseline (silent). Every later run diffs against it, notifies on
change, then updates the baseline.
"""
import hashlib
import json
import smtplib
import ssl
from datetime import datetime, timezone
from email.mime.text import MIMEText
from pathlib import Path

WATCHDOG_CONFIG = Path("/etc/asguard/watchdog_config.json")
BASELINE_FILE = Path("/var/backups/asguard/system_baseline.json")

# Files whose content we fingerprint (sha256) — a change to any of these is a
# security-relevant system change worth a heads-up.
WATCHED_FILES = [
    "/etc/ssh/sshd_config",
    "/etc/sudoers",
    "/etc/hostname",
]


def utc_now() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _sha256_file(path: str) -> str | None:
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except Exception:
        return None


def capture_state() -> dict:
    state = {"root_pw": None, "users": {}, "files": {}}
    # Root password hash (proves a password change without storing the password).
    try:
        for line in Path("/etc/shadow").read_text(errors="ignore").splitlines():
            if line.startswith("root:"):
                state["root_pw"] = line.split(":")[1]
                break
    except Exception:
        pass
    # username -> uid, so we see adds, removals AND uid changes.
    try:
        for line in Path("/etc/passwd").read_text(errors="ignore").splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            p = line.split(":")
            if len(p) >= 3:
                state["users"][p[0]] = p[2]
    except Exception:
        pass
    for f in WATCHED_FILES:
        state["files"][f] = _sha256_file(f)
    return state


def diff_states(old: dict, new: dict) -> list[str]:
    changes = []
    if old.get("root_pw") and new.get("root_pw") and old["root_pw"] != new["root_pw"]:
        changes.append("🔑 Mot de passe ROOT modifié")
    old_u, new_u = old.get("users", {}), new.get("users", {})
    for u in sorted(set(new_u) - set(old_u)):
        changes.append(f"👤 Utilisateur AJOUTÉ : {u} (uid {new_u[u]})")
    for u in sorted(set(old_u) - set(new_u)):
        changes.append(f"👤 Utilisateur SUPPRIMÉ : {u}")
    for u in sorted(set(old_u) & set(new_u)):
        if old_u[u] != new_u[u]:
            changes.append(f"👤 UID de {u} changé : {old_u[u]} → {new_u[u]}")
    for f, h in new.get("files", {}).items():
        old_h = old.get("files", {}).get(f)
        if old_h and h and old_h != h:
            changes.append(f"📄 Fichier modifié : {f}")
        elif old_h and not h:
            changes.append(f"📄 Fichier supprimé : {f}")
    return changes


def _read_notif_config() -> dict:
    try:
        cfg = json.loads(WATCHDOG_CONFIG.read_text())
        return cfg.get("notifications", {}) or {}
    except Exception:
        return {}


def send_ntfy(title: str, body: str) -> None:
    nt = (_read_notif_config().get("ntfy") or {})
    if not (nt.get("enabled") and nt.get("topic")):
        return
    try:
        import urllib.request as ur
        req = ur.Request(f"https://ntfy.sh/{nt['topic'].strip()}",
                         data=body.encode("utf-8"), method="POST")
        req.add_header("Title", title.encode("ascii", "replace").decode())
        req.add_header("Priority", "high")
        req.add_header("Tags", "warning,closed_lock_with_key")
        with ur.urlopen(req, timeout=10):
            pass
    except Exception as e:
        print(f"[ntfy] {e}")


def send_email(subject: str, body: str) -> None:
    em = (_read_notif_config().get("email") or {})
    if not em.get("enabled"):
        return
    host = em.get("smtp_host") or em.get("host")
    port = int(em.get("smtp_port") or em.get("port") or 587)
    user = em.get("smtp_user") or em.get("user") or em.get("username")
    pwd = em.get("smtp_password") or em.get("password")
    recipients = em.get("recipients") or em.get("to") or []
    if isinstance(recipients, str):
        recipients = [recipients]
    if not (host and user and recipients):
        return
    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = user
        msg["To"] = ", ".join(recipients)
        ctx = ssl.create_default_context()
        with smtplib.SMTP(host, port, timeout=20) as s:
            s.starttls(context=ctx)
            if pwd:
                s.login(user, pwd)
            s.sendmail(user, recipients, msg.as_string())
    except Exception as e:
        print(f"[email] {e}")


def main() -> int:
    new_state = capture_state()
    try:
        old_state = json.loads(BASELINE_FILE.read_text())
    except Exception:
        old_state = None

    if old_state is None:
        BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE_FILE.write_text(json.dumps(new_state, indent=2))
        print(f"[{utc_now()}] baseline established (no notification on first run)")
        return 0

    changes = diff_states(old_state, new_state)
    if changes:
        title = "🛡️ Changement système détecté — Asguard"
        body = (f"{len(changes)} changement(s) détecté(s) le "
                f"{datetime.now().strftime('%d/%m/%Y %H:%M')} :\n\n" + "\n".join(changes))
        print(f"[{utc_now()}] {len(changes)} change(s): {changes}")
        send_ntfy(title, body)
        send_email(title, body)
    else:
        print(f"[{utc_now()}] no system change")

    BASELINE_FILE.write_text(json.dumps(new_state, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
