"""Diagnostic technique d'un service systemd en échec.

Sonde systemctl + journalctl et renvoie une cause structurée, affichée par
l'onglet Logs dans la bannière « Cause technique ». Ne lève jamais d'exception.
"""

import re

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
