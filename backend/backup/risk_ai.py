"""
Adaptive Risk Engine — Asguard
================================
Pure-Python statistical anomaly detection + EWMA smoothing + trend forecast.

Pipeline:
  1. Per-feature normalization to a 0-100 risk via piecewise-linear pressure curves
     (CPU, RAM, load, disk usage, services, backup health).
  2. Per-feature anomaly score using robust median + MAD z-scores against history,
     blended with the absolute pressure (anomaly weight scales with history quality).
  3. Weighted fusion → raw composite score.
  4. EWMA smoothing (alpha=0.28) persisted on disk so the score does not jump
     between requests when a single CPU spike hits.
  5. Hysteresis on the categorical level (stable / watch / high / critical):
     need N consecutive samples above the threshold to escalate.
  6. Linear-regression slope on the last samples → trend direction + 15-min forecast.
  7. Per-feature contribution explanation: which signals are pushing the score up.

State is persisted in /var/log/asguard/risk_ai_state.json (JSON list of last
60 readings) so smoothing survives Django reloads / worker restarts.
"""

from __future__ import annotations

import json
import math
import statistics
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

STATE_FILE = Path("/var/log/asguard/risk_ai_state.json")
HISTORY_KEEP = 60                # samples kept on disk (~30 min @ 30 s polling)
EWMA_ALPHA = 0.28                # smoothing strength (lower = smoother)
HYSTERESIS_UP = 1                # consecutive samples to escalate level (reactive)
HYSTERESIS_DOWN = 2              # consecutive samples to de-escalate level
MODEL_NAME = "Adaptive Risk Engine"
MODEL_VERSION = "2.0"
MODEL_METHOD = "Robust MAD + EWMA + Trend regression"

LEVEL_THRESHOLDS = [
    ("critical", 75),
    ("high", 55),
    ("watch", 35),
    ("stable", 0),
]

# ───────────────────────── helpers ──────────────────────────
def _clamp(value, lo=0.0, hi=100.0):
    return max(lo, min(hi, float(value)))


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_load(value):
    try:
        return _safe_float(str(value or "").split(",")[0].strip())
    except Exception:
        return 0.0


def _piecewise_pressure(value, points):
    """Convert a raw metric to 0-100 risk using a piecewise-linear curve.
    points = [(input_threshold, risk_at_threshold), ...] sorted ascending.
    """
    if value <= points[0][0]:
        return points[0][1]
    for i in range(1, len(points)):
        x0, y0 = points[i - 1]
        x1, y1 = points[i]
        if value <= x1:
            ratio = (value - x0) / (x1 - x0) if x1 > x0 else 0
            return y0 + ratio * (y1 - y0)
    return points[-1][1]


def _robust_anomaly(value, samples, min_mad=3.0):
    """Modified z-score (median + MAD) → 0-100 anomaly risk. Precision-tuned:
    - direction-aware: only UPWARD deviations are a risk (memory/CPU dropping is
      not an anomaly to worry about) → no more false '+100' when a signal falls;
    - MAD floor: a flat baseline (e.g. RAM steady at 31%) has ~0 MAD, which makes
      the z-score explode on trivial jitter. Flooring MAD ignores insignificant
      wobble so we only flag genuine, meaningful jumps."""
    if len(samples) < 6:
        return 0.0
    median = statistics.median(samples)
    mad = max(statistics.median([abs(s - median) for s in samples]), min_mad)
    dev = value - median
    if dev <= 0:
        return 0.0
    z = 0.6745 * dev / mad
    return _clamp((z / 6.0) * 100.0)


def _linear_slope(samples):
    """Least-squares slope (units / sample). Returns 0 for <3 samples."""
    n = len(samples)
    if n < 3:
        return 0.0
    xs = list(range(n))
    mean_x = sum(xs) / n
    mean_y = sum(samples) / n
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, samples))
    den = sum((x - mean_x) ** 2 for x in xs) or 1.0
    return num / den


# ───────────────────────── state I/O ────────────────────────
def _load_state():
    try:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"history": [], "level": "stable", "level_streak": 0,
            "level_since": None, "service_state": {}}


def _detect_service_transitions(state, services):
    """Compare current service running-state against the previous snapshot
    and fire a notification only when a service has been down for at least
    `_DOWN_STREAK_REQUIRED` consecutive polls. This eliminates false positives
    from transient restarts — e.g. nginx getting bounced when the user opens
    a VS Code SSH session, or when WAF/settings code legitimately reloads it.

    State shape (per service): { "running": bool, "down_streak": int,
    "alerted": bool }. Legacy bool entries are migrated on first read.
    """
    _DOWN_STREAK_REQUIRED = 2   # ≈ 60 s with the 30 s poll cadence

    prev_raw = state.get("service_state") or {}
    prev: dict = {}
    for name, entry in prev_raw.items():
        if isinstance(entry, bool):
            prev[name] = {"running": entry, "down_streak": 0, "alerted": False}
        elif isinstance(entry, dict):
            prev[name] = {
                "running":     bool(entry.get("running")),
                "down_streak": int(entry.get("down_streak", 0)),
                "alerted":     bool(entry.get("alerted", False)),
            }

    current: dict = {}
    transitions_down = []

    for svc in services or []:
        name = svc.get("name")
        if not name:
            continue
        running = bool(svc.get("running"))
        prev_entry = prev.get(name) or {"running": None, "down_streak": 0, "alerted": False}

        if running:
            # Recovery — reset streak/alerted so a real future down can alert again.
            current[name] = {"running": True, "down_streak": 0, "alerted": False}
            continue

        new_streak = (prev_entry.get("down_streak") or 0) + 1
        already_alerted = bool(prev_entry.get("alerted"))
        should_alert = (new_streak >= _DOWN_STREAK_REQUIRED) and not already_alerted

        current[name] = {
            "running":     False,
            "down_streak": new_streak,
            "alerted":     already_alerted or should_alert,
        }
        if should_alert:
            transitions_down.append(svc)

    state["service_state"] = current

    if transitions_down:
        try:
            from backend.backup.notifications import notify_service_action
        except Exception:
            notify_service_action = None
        if notify_service_action:
            for svc in transitions_down:
                try:
                    notify_service_action(
                        service_name=svc.get("name"),
                        action="stop",
                        success=False,
                        display_name=svc.get("label") or svc.get("name"),
                    )
                except Exception:
                    pass

    return transitions_down


def _save_state(state):
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception:
        pass


# ───────────────────────── feature scoring ──────────────────
@dataclass
class FeatureScore:
    name: str
    label: str
    pressure: float    # 0-100 absolute risk based on current value
    anomaly: float     # 0-100 deviation from baseline
    weight: float      # contribution weight in fusion
    raw_value: float
    display: str       # human-readable value


def _score_features(live_metrics, services, root_disk_usage, backup_risk, history):
    cpu = _safe_float(live_metrics.get("cpu_percentage") or live_metrics.get("cpu"))
    ram = _safe_float(live_metrics.get("memory_percentage") or live_metrics.get("memory"))
    load = _parse_load(live_metrics.get("load_average") or live_metrics.get("loadAverage"))
    disk = _safe_float(root_disk_usage)

    # Service health: ratio of failing critical services
    total_svc = max(1, len(services))
    failing = [s for s in services if not s.get("running")]
    critical_failing = [s for s in failing if s.get("category") in
                        {"access", "platform", "data", "security", "network"}]
    svc_ratio = len(failing) / total_svc * 100
    critical_boost = min(40, len(critical_failing) * 20)

    # Pressure curves (piecewise-linear, calibrated for a firewall appliance)
    cpu_p = _piecewise_pressure(cpu, [(0, 0), (50, 8), (70, 25), (85, 55), (95, 85), (100, 96)])
    ram_p = _piecewise_pressure(ram, [(0, 0), (60, 10), (80, 35), (90, 65), (95, 85), (100, 96)])
    load_p = _piecewise_pressure(load, [(0, 0), (1, 8), (2, 28), (4, 60), (6, 82), (8, 95)])
    disk_p = _piecewise_pressure(disk, [(0, 0), (60, 5), (80, 25), (90, 55), (95, 80), (100, 96)])
    svc_p = _clamp(svc_ratio + critical_boost)
    bkp_p = _clamp(_safe_float(backup_risk))

    # Historical samples per feature for anomaly detection
    cpu_hist = [_safe_float(p.get("cpu")) for p in history]
    ram_hist = [_safe_float(p.get("memory")) for p in history]

    cpu_anom = _robust_anomaly(cpu, cpu_hist)
    ram_anom = _robust_anomaly(ram, ram_hist)

    return [
        FeatureScore("cpu", "CPU",
                     pressure=cpu_p, anomaly=cpu_anom, weight=0.22,
                     raw_value=cpu, display=f"{cpu:.0f}%"),
        FeatureScore("ram", "Mémoire",
                     pressure=ram_p, anomaly=ram_anom, weight=0.24,
                     raw_value=ram, display=f"{ram:.0f}%"),
        FeatureScore("load", "Charge système",
                     pressure=load_p, anomaly=0.0, weight=0.12,
                     raw_value=load, display=f"{load:.2f}"),
        FeatureScore("disk", "Disque /",
                     pressure=disk_p, anomaly=0.0, weight=0.14,
                     raw_value=disk, display=f"{disk:.0f}%"),
        FeatureScore("services", "Services critiques",
                     pressure=svc_p, anomaly=0.0, weight=0.18,
                     raw_value=svc_ratio,
                     display=f"{total_svc - len(failing)}/{total_svc} OK"),
        FeatureScore("backup", "Backup health",
                     pressure=bkp_p, anomaly=0.0, weight=0.10,
                     raw_value=bkp_p, display=f"{int(bkp_p)}%"),
    ]


# ───────────────────────── level + hysteresis ───────────────
def _raw_level(score):
    for label, threshold in LEVEL_THRESHOLDS:
        if score >= threshold:
            return label
    return "stable"


def _apply_hysteresis(state, raw_level, smoothed_score):
    """Prevent level flapping. Need N consecutive same-level samples to flip."""
    current = state.get("level", "stable")
    streak = int(state.get("level_streak", 0))

    if raw_level == current:
        streak += 1
    else:
        # Direction-aware threshold
        order = ["stable", "watch", "high", "critical"]
        try:
            going_up = order.index(raw_level) > order.index(current)
        except ValueError:
            going_up = True
        needed = HYSTERESIS_UP if going_up else HYSTERESIS_DOWN
        if streak + 1 >= needed:
            current = raw_level
            streak = 1
            state["level_since"] = datetime.now(timezone.utc).isoformat()
        else:
            streak += 1

    state["level"] = current
    state["level_streak"] = streak
    if not state.get("level_since"):
        state["level_since"] = datetime.now(timezone.utc).isoformat()
    return current


# ───────────────────────── trend / forecast ─────────────────
def _eta_to(threshold, current, slope_per_min):
    """Minutes until the score reaches `threshold` at the current rate. Only
    returns a credible near-term ETA (0<eta<=120 min), else None."""
    if slope_per_min <= 0.3 or current >= threshold:
        return None
    eta = int((threshold - current) / slope_per_min)
    return eta if 0 < eta <= 120 else None


def _update_disk_history(state, disk_pct):
    """Keep a sparse long-term disk-usage series (≥1 sample/hour, 14 days) so we
    can forecast when the disk will fill — impossible from the 30-min score
    history alone."""
    now = datetime.now(timezone.utc).timestamp()
    samples = state.get("disk_samples", [])
    if not samples or (now - samples[-1][0]) >= 3600:
        samples.append([now, round(_safe_float(disk_pct), 1)])
        samples = [s for s in samples if now - s[0] <= 14 * 86400][-400:]
        state["disk_samples"] = samples
    return samples


def _capacity_forecast(samples, current_disk):
    """Days until the disk reaches 100%, from the long-term fill rate."""
    cur = round(_safe_float(current_disk))
    if len(samples) < 2:
        return {"disk_pct": cur, "eta_days": None, "trend": "collecting", "rate_per_day": 0.0}
    t0, d0 = samples[0]
    t1, d1 = samples[-1]
    span_days = (t1 - t0) / 86400.0
    if span_days < 0.25:  # <6h of data → not credible yet
        return {"disk_pct": cur, "eta_days": None, "trend": "collecting", "rate_per_day": 0.0}
    rate = (d1 - d0) / span_days  # %/day
    if rate <= 0.05:
        return {"disk_pct": cur, "eta_days": None, "trend": "stable", "rate_per_day": round(rate, 2)}
    eta = (100 - cur) / rate
    eta = int(eta) if 0 < eta <= 3650 else None
    return {"disk_pct": cur, "eta_days": eta, "trend": "rising", "rate_per_day": round(rate, 2)}


def _trend_analysis(score_history):
    if len(score_history) < 5:
        return {
            "direction": "stable",
            "slope_per_min": 0.0,
            "forecast_15min": int(score_history[-1] if score_history else 0),
            "confidence": 0.3,
            "time_to_high_min": None,
            "time_to_critical_min": None,
        }
    recent = score_history[-12:]
    slope = _linear_slope(recent)
    # Polling cadence ≈ 30 s → 2 samples/min
    slope_per_min = slope * 2.0
    direction = "stable"
    if slope_per_min > 1.2:
        direction = "rising"
    elif slope_per_min < -1.2:
        direction = "falling"

    forecast = recent[-1] + slope_per_min * 15
    forecast = int(_clamp(forecast))

    # Confidence higher when more samples & lower variance
    var = statistics.pvariance(recent) if len(recent) > 1 else 0
    confidence = max(0.4, min(0.95, 0.95 - var / 800.0))

    cur = recent[-1]
    return {
        "direction": direction,
        "slope_per_min": round(slope_per_min, 2),
        "forecast_15min": forecast,
        "confidence": round(confidence, 2),
        # Predictive ETA to the next danger thresholds (55 = high, 75 = critical).
        "time_to_high_min": _eta_to(55, cur, slope_per_min),
        "time_to_critical_min": _eta_to(75, cur, slope_per_min),
    }


# ───────────────────────── recommendations ──────────────────
def _build_recommendations(features, level, services):
    recs = []
    by_name = {f.name: f for f in features}
    sorted_feats = sorted(features, key=lambda f: f.pressure, reverse=True)
    top = sorted_feats[0]

    if level == "critical":
        recs.append({
            "title": "Créer un point de restauration LVM immédiatement",
            "detail": "Niveau critique détecté — sécurisez l'état actuel avant intervention.",
            "priority": "critical",
            "icon": "mdi mdi-camera-plus",
            "action": "snapshot_lvm",
            "action_label": "Créer snapshot",
            "action_kind": "intrusive",
        })

    if by_name["cpu"].pressure >= 55:
        recs.append({
            "title": "Identifier les processus CPU élevés",
            "detail": f"CPU à {by_name['cpu'].display}. Top 15 processus par usage CPU.",
            "priority": "high" if by_name["cpu"].pressure >= 75 else "warning",
            "icon": "mdi mdi-chip",
            "action": "cpu_top",
            "action_label": "Diagnostiquer",
            "action_kind": "safe",
        })

    if by_name["ram"].pressure >= 55:
        recs.append({
            "title": "Libérer la mémoire vive",
            "detail": f"RAM à {by_name['ram'].display}. Diagnostic des processus + libération des caches.",
            "priority": "high" if by_name["ram"].pressure >= 75 else "warning",
            "icon": "mdi mdi-memory",
            "action": "ram_caches",
            "action_label": "Libérer caches",
            "action_kind": "intrusive",
            "action_secondary": "ram_top",
            "action_secondary_label": "Diagnostiquer",
        })

    if by_name["disk"].pressure >= 55:
        recs.append({
            "title": "Libérer le disque système",
            "detail": f"Disque / à {by_name['disk'].display}. Purger les journaux systemd > 7 jours.",
            "priority": "high",
            "icon": "mdi mdi-harddisk",
            "action": "disk_journal",
            "action_label": "Purger logs",
            "action_kind": "intrusive",
            "action_secondary": "disk_usage",
            "action_secondary_label": "Diagnostiquer",
        })

    if by_name["load"].pressure >= 55:
        recs.append({
            "title": "Investiguer la charge système",
            "detail": f"Load à {by_name['load'].display}. Vérifier les processus bloquants.",
            "priority": "high" if by_name["load"].pressure >= 75 else "warning",
            "icon": "mdi mdi-speedometer",
            "action": "load_top",
            "action_label": "Diagnostiquer",
            "action_kind": "safe",
        })

    failing = [s for s in services if not s.get("running")]
    if failing:
        names = ", ".join((s.get("label") or s.get("name") or "service") for s in failing[:3])
        recs.append({
            "title": "Relancer les services arrêtés",
            "detail": f"Services impactés : {names}",
            "priority": "critical" if by_name["services"].pressure >= 60 else "warning",
            "icon": "mdi mdi-cog-alert",
            "action": "services_restart",
            "action_label": "Redémarrer",
            "action_kind": "intrusive",
            "action_secondary": "services_status",
            "action_secondary_label": "Voir détails",
        })

    if not recs:
        recs.append({
            "title": "Tout est sous contrôle",
            "detail": f"Aucun signal critique. {top.label} reste le facteur dominant à {top.display}.",
            "priority": "info",
            "icon": "mdi mdi-shield-check",
        })

    return recs[:5]


# ───────────────────────── public API ───────────────────────
def analyze_vm_and_services(history_points, live_metrics, services,
                            root_disk_usage=0, backup_risk=0):
    state = _load_state()
    history_scores = [s["score"] for s in state.get("history", [])]

    # Watchdog: detect services that flipped running → stopped between two
    # analysis cycles, and fire a ntfy + email alert. This is the only path
    # that turns silent appliance failures into actual alerts.
    _detect_service_transitions(state, services)

    features = _score_features(live_metrics, services, root_disk_usage,
                               backup_risk, history_points)

    # Anomaly weight grows with history quality (more data = more trust)
    history_quality = min(1.0, len(history_points) / 30.0)
    weighted_sum = 0.0
    weight_sum = 0.0
    contributions = []

    for f in features:
        # Blend pressure (always available) with anomaly (when history is rich)
        score = f.pressure * (1 - 0.4 * history_quality) + f.anomaly * (0.4 * history_quality)
        contribution = score * f.weight
        weighted_sum += contribution
        weight_sum += f.weight
        contributions.append({
            "name": f.name,
            "label": f.label,
            "value": f.display,
            "pressure": round(f.pressure, 1),
            "anomaly": round(f.anomaly, 1),
            "weight_pct": round(f.weight * 100),
            "contribution": round(contribution, 2),
        })

    raw_score = weighted_sum / (weight_sum or 1.0)
    raw_score = _clamp(raw_score)

    # Compound risk: several signals stressed at once is more dangerous than the
    # plain weighted average implies (correlated failure). Amplify accordingly.
    stressed = [c for c in contributions if c["pressure"] >= 60 or c["anomaly"] >= 65]
    compound_boost = min(15.0, max(0, len(stressed) - 1) * 7.0)
    if compound_boost:
        raw_score = _clamp(raw_score + compound_boost)
    compound = {
        "count": len(stressed),
        "boost": round(compound_boost, 1),
        "signals": [c["label"] for c in stressed],
    }

    # EWMA smoothing
    previous = history_scores[-1] if history_scores else raw_score
    smoothed = EWMA_ALPHA * raw_score + (1 - EWMA_ALPHA) * previous
    smoothed = round(_clamp(smoothed))

    # Append + trim history
    now_iso = datetime.now(timezone.utc).isoformat()
    state.setdefault("history", []).append({
        "ts": now_iso,
        "score": smoothed,
        "raw": round(raw_score, 1),
    })
    state["history"] = state["history"][-HISTORY_KEEP:]

    # Hysteresis-stabilized level
    raw_level = _raw_level(smoothed)
    level = _apply_hysteresis(state, raw_level, smoothed)

    # Trend & forecast
    trend = _trend_analysis([s["score"] for s in state["history"]])

    # Long-term capacity forecast (disk-full ETA in days).
    capacity = _capacity_forecast(_update_disk_history(state, root_disk_usage), root_disk_usage)

    # Top contributors (sorted by impact on the final score)
    contributions_sorted = sorted(contributions, key=lambda c: c["contribution"], reverse=True)
    top_contributors = contributions_sorted[:3]

    # Plain-language explanation
    top = top_contributors[0]
    if level == "stable":
        explanation = (f"Système stable. {top['label']} reste le signal dominant "
                       f"à {top['value']} mais sans dépassement critique.")
    elif level == "watch":
        explanation = (f"À surveiller : {top['label']} ({top['value']}) tire le score "
                       f"vers le haut. Tendance {trend['direction']}.")
    elif level == "high":
        explanation = (f"Risque élevé porté par {top['label']} ({top['value']}). "
                       f"Forecast 15min : {trend['forecast_15min']}/100.")
    else:
        explanation = (f"État critique : {top['label']} à {top['value']} dépasse "
                       f"largement la baseline. Action immédiate recommandée.")

    delta = smoothed - (history_scores[-1] if history_scores else smoothed)
    confidence = round(min(95, 60 + history_quality * 35))

    # NEW analysis — "now vs your normal": compare the live score to the
    # historical baseline (median) so the operator sees deviation from normal,
    # not just an absolute number. Plus a short alert-likelihood read.
    all_scores = [s["score"] for s in state["history"]]
    baseline = int(round(statistics.median(all_scores))) if len(all_scores) >= 5 else smoothed
    vs_normal = int(round(smoothed - baseline))
    if trend.get("time_to_critical_min") is not None or level == "critical":
        alert_likelihood = "élevée"
    elif trend.get("time_to_high_min") is not None or level == "high" or vs_normal >= 12:
        alert_likelihood = "modérée"
    else:
        alert_likelihood = "faible"
    insight = {
        "baseline": baseline,
        "vs_normal": vs_normal,
        "alert_likelihood": alert_likelihood,
        "peak": int(max(all_scores)) if all_scores else smoothed,
    }

    _save_state(state)

    return {
        "model": {
            "name": MODEL_NAME,
            "version": MODEL_VERSION,
            "method": MODEL_METHOD,
            "status": "active",
            "family": "anomaly_detection",
            "trained_on_points": len(history_points),
            "history_quality": round(history_quality * 100),
            "stability": confidence,
            "generated_at": now_iso,
        },
        "scores": {
            "raw": round(raw_score),
            "smoothed": smoothed,
            "global": smoothed,
            "delta": int(round(delta)),
            "level": level,
            "level_since": state.get("level_since"),
            # Backward compatibility with existing UI
            "vm_crash": int(round(max(features[0].pressure, features[1].pressure))),
            "services_crash": int(round(features[4].pressure)),
        },
        "trend": trend,
        "compound": compound,
        "capacity": capacity,
        "insight": insight,
        "contributors": top_contributors,
        "all_contributors": contributions_sorted,
        "features": {
            "cpu": features[0].raw_value,
            "memory": features[1].raw_value,
            "load_average_1m": features[2].raw_value,
            "root_disk_usage": features[3].raw_value,
            "failing_services": int(features[4].raw_value * len(services) / 100) if services else 0,
        },
        "history": state["history"][-30:],
        "recommendations": _build_recommendations(features, level, services),
        "explanation": explanation,
        "confidence": confidence,
    }
