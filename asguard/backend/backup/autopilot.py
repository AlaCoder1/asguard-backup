"""
Auto-Pilot — autonomous remediation for the AI Risk Center.

When enabled, the appliance repairs itself without a human click:
  - a critical service is down        → restart it        (rule "services")
  - RAM usage crosses the threshold   → drop page caches  (rule "ram")
  - disk usage crosses the threshold  → vacuum journals   (rule "disk")

Design constraints (this is a firewall appliance shipped to clients):
  - reuses the EXACT same action runners as the 1-click playbook
    (views._run_risk_action) → same permissions, same behaviour, no new attack
    surface;
  - per-action cooldown so a persistent condition can't loop-fire;
  - every intervention is journaled (JSON, capped) and pushed via ntfy;
  - a single kill-switch (`enabled`) plus per-rule toggles.
"""
import json
import logging
import threading
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

CONFIG_FILE  = Path("/etc/asguard/autopilot_config.json")
JOURNAL_FILE = Path("/var/log/asguard/autopilot_journal.json")

DEFAULT_CONFIG = {
    "enabled": False,           # opt-in: the operator flips the switch in the UI
    "rules": {"services": True, "ram": True, "disk": True},
    "ram_threshold_pct": 90,
    "disk_threshold_pct": 90,
    "cooldown_min": 30,
}

_lock = threading.Lock()
_last_fired: dict[str, float] = {}   # action_key -> epoch seconds (cooldown)


# ── config / journal I/O ─────────────────────────────────────────────────────

def load_config() -> dict:
    try:
        cfg = json.loads(CONFIG_FILE.read_text())
        merged = dict(DEFAULT_CONFIG)
        merged.update(cfg or {})
        merged["rules"] = {**DEFAULT_CONFIG["rules"], **(cfg.get("rules") or {})}
        return merged
    except Exception:
        return dict(DEFAULT_CONFIG)


def save_config(cfg: dict) -> dict:
    merged = load_config()
    for key in ("enabled", "ram_threshold_pct", "disk_threshold_pct", "cooldown_min"):
        if key in cfg:
            merged[key] = cfg[key]
    if isinstance(cfg.get("rules"), dict):
        merged["rules"].update({k: bool(v) for k, v in cfg["rules"].items()
                                if k in DEFAULT_CONFIG["rules"]})
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(merged, indent=2, ensure_ascii=False))
    return merged


def load_journal() -> list:
    try:
        return json.loads(JOURNAL_FILE.read_text())
    except Exception:
        return []


def _append_journal(entry: dict) -> None:
    entries = load_journal()
    entries.append(entry)
    JOURNAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    JOURNAL_FILE.write_text(json.dumps(entries[-100:], indent=2, ensure_ascii=False))


# ── remediation ──────────────────────────────────────────────────────────────

def _cooled_down(action: str, cooldown_min: int, now: float) -> bool:
    return (now - _last_fired.get(action, 0.0)) >= cooldown_min * 60


def _boot_enabled(unit: str) -> bool:
    """True if the unit is meant to run at boot. Auto-Pilot only restarts these:
    services the operator intentionally keeps off must never be force-started."""
    try:
        import subprocess
        r = subprocess.run(["systemctl", "is-enabled", unit],
                           capture_output=True, text=True, timeout=5)
        return r.stdout.strip() in ("enabled", "enabled-runtime", "static")
    except Exception:
        return False


def assess() -> dict:
    """Live, read-only health snapshot: what Auto-Pilot sees *right now* and what
    it would (or would not) do. Powers the 'Dernière vérification' heartbeat so the
    operator always gets feedback — even when the correct action is to do nothing."""
    cfg = load_config()
    rules = cfg.get("rules", {})
    would_restart, skipped_disabled = [], []
    ram_pct = disk_pct = None

    if rules.get("services", True):
        try:
            from backend.backup.views import (_load_dashboard_services,
                                              CRITICAL_SERVICE_CANDIDATES)
            critical = set()
            for sd in CRITICAL_SERVICE_CANDIDATES:
                critical.update(c.replace(".service", "") for c in sd["candidates"])
            for s in _load_dashboard_services():
                if s.get("running") or s.get("name") not in critical:
                    continue
                label = s.get("label") or s.get("name")
                (would_restart if _boot_enabled(s.get("name")) else skipped_disabled).append(label)
        except Exception:
            logger.exception("[autopilot] assess services failed")

    if rules.get("ram", True):
        try:
            import psutil
            ram_pct = round(psutil.virtual_memory().percent)
        except Exception:
            pass
    if rules.get("disk", True):
        try:
            import shutil
            du = shutil.disk_usage("/")
            disk_pct = round(du.used / du.total * 100)
        except Exception:
            pass

    ram_hot = ram_pct is not None and ram_pct >= float(cfg.get("ram_threshold_pct", 90))
    disk_hot = disk_pct is not None and disk_pct >= float(cfg.get("disk_threshold_pct", 90))
    pending = bool(would_restart) or ram_hot or disk_hot

    if not cfg.get("enabled"):
        verdict, tone = "Auto-Pilot désactivé — supervision en pause.", "off"
    elif pending:
        bits = []
        if would_restart:
            bits.append(f"{len(would_restart)} service(s) à relancer")
        if ram_hot:
            bits.append(f"RAM {ram_pct}%")
        if disk_hot:
            bits.append(f"disque {disk_pct}%")
        verdict, tone = "Intervention imminente : " + ", ".join(bits) + ".", "act"
    elif skipped_disabled:
        verdict = (f"Système sain. {len(skipped_disabled)} service(s) arrêté(s) "
                   f"volontairement (ignorés) : " + ", ".join(skipped_disabled[:6]) + ".")
        tone = "healthy"
    else:
        verdict, tone = "Système sain — rien à réparer.", "healthy"

    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "tone": tone,                     # off | healthy | act
        "would_restart": would_restart,
        "skipped_disabled": skipped_disabled,
        "ram_pct": ram_pct,
        "disk_pct": disk_pct,
    }


def _fire(action_key: str, trigger: str, cfg: dict, now: float) -> None:
    """Run one remediation via the shared playbook runner + journal + notify."""
    from backend.backup.views import _run_risk_action  # runtime import (no cycle)
    _last_fired[action_key] = now
    res = _run_risk_action(action_key)
    ok = bool(res.get("ok"))
    output = (res.get("output") or res.get("error") or "").strip()
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "trigger": trigger,
        "action": action_key,
        "title": res.get("title", action_key),
        "ok": ok,
        "summary": output.splitlines()[-1][:180] if output else "",
    }
    _append_journal(entry)
    logger.info("[autopilot] %s → %s (%s)", trigger, action_key, "OK" if ok else "KO")
    try:
        from backend.backup.notifications import _send_ntfy
        _send_ntfy(
            title=f"🤖 Auto-Pilot — {res.get('title', action_key)}",
            body=f"Déclencheur : {trigger}\nRésultat : {'réussi' if ok else 'échec'}\n{entry['summary']}",
            priority="high" if not ok else "default",
            tags="robot,shield",
        )
    except Exception:
        pass


def autopilot_tick() -> None:
    """One evaluation cycle. Called from the background monitor thread (~60s).
    Never raises."""
    with _lock:
        try:
            cfg = load_config()
            if not cfg.get("enabled"):
                return
            now = datetime.now(timezone.utc).timestamp()
            rules = cfg.get("rules", {})
            cooldown = int(cfg.get("cooldown_min", 30))

            # 1) critical service down → restart. ONLY units enabled at boot:
            #    "repair" means restoring what is MEANT to run. Services the
            #    operator intentionally keeps off (suricata is RAM-heavy, VPNs
            #    unconfigured…) must never be force-started — doing so overloaded
            #    the appliance and spammed alerts.
            if rules.get("services") and _cooled_down("services_restart", cooldown, now):
                try:
                    import subprocess
                    from backend.backup.views import (_load_dashboard_services,
                                                      CRITICAL_SERVICE_CANDIDATES)
                    critical = set()
                    for sd in CRITICAL_SERVICE_CANDIDATES:
                        critical.update(c.replace(".service", "") for c in sd["candidates"])

                    down = [s for s in _load_dashboard_services()
                            if not s.get("running") and s.get("name") in critical
                            and _boot_enabled(s.get("name"))]
                    if down:
                        _last_fired["services_restart"] = now
                        lines, any_ok = [], False
                        for svc in down[:5]:
                            unit = svc.get("name")
                            label = svc.get("label") or unit
                            try:
                                proc = subprocess.run(
                                    ["sudo", "-n", "systemctl", "restart", unit],
                                    capture_output=True, text=True, timeout=25)
                                ok1 = proc.returncode == 0
                            except Exception:
                                ok1 = False
                            any_ok = any_ok or ok1
                            lines.append(f"[{'OK' if ok1 else 'KO'}] {label}")
                        names = ", ".join(s.get("label") or s.get("name") for s in down[:4])
                        entry = {
                            "ts": datetime.now(timezone.utc).isoformat(),
                            "trigger": f"Service(s) prévu(s) au boot arrêté(s) : {names}",
                            "action": "services_restart",
                            "title": "Relance des services prévus au démarrage",
                            "ok": any_ok,
                            "summary": " · ".join(lines)[:180],
                        }
                        _append_journal(entry)
                        try:
                            from backend.backup.notifications import _send_ntfy
                            _send_ntfy(title="🤖 Auto-Pilot — relance de services",
                                       body=f"{entry['trigger']}\n{entry['summary']}",
                                       priority="high" if not any_ok else "default",
                                       tags="robot,shield")
                        except Exception:
                            pass
                except Exception:
                    logger.exception("[autopilot] services check failed")

            # 2) RAM saturated → drop caches.
            if rules.get("ram") and _cooled_down("ram_caches", cooldown, now):
                try:
                    import psutil
                    pct = psutil.virtual_memory().percent
                    if pct >= float(cfg.get("ram_threshold_pct", 90)):
                        _fire("ram_caches", f"Mémoire à {pct:.0f}%", cfg, now)
                except Exception:
                    logger.exception("[autopilot] ram check failed")

            # 3) disk nearly full → vacuum systemd journals.
            if rules.get("disk") and _cooled_down("disk_journal", cooldown, now):
                try:
                    import shutil
                    du = shutil.disk_usage("/")
                    pct = du.used / du.total * 100
                    if pct >= float(cfg.get("disk_threshold_pct", 90)):
                        _fire("disk_journal", f"Disque à {pct:.0f}%", cfg, now)
                except Exception:
                    logger.exception("[autopilot] disk check failed")
        except Exception:
            logger.exception("[autopilot] tick failed")


def status() -> dict:
    cfg = load_config()
    journal = load_journal()
    return {
        "config": cfg,
        "journal": list(reversed(journal[-20:])),
        "interventions": len(journal),
        "last_intervention": journal[-1]["ts"] if journal else None,
        "assessment": assess(),
    }
