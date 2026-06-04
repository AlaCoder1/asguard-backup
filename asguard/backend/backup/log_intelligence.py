"""
AI Log Intelligence — Anomaly / Incident / Forecast engine
==========================================================

Replaces the old "Chaos Engineering Lab" + "DR Readiness Drill" hero on
the Logs & Audit page with something operators actually use day-to-day:

  1. Anomaly detection  — per-source 5-min bucketing over 24 h, EWMA
                          baseline, z-score flagging (no ML, no model
                          download — pure stdlib statistics).
  2. Incident correlation — sliding-window grouping of related
                          error/critical events across services, with
                          a regex/heuristic "probable cause" hint
                          driven by a small service-dependency map.
  3. Predictive forecast — linear regression on error rate over the
                          last hour, projected 30 min forward, with
                          R² used as a confidence proxy.
  4. Natural-language summary — template-driven French paragraph.
                          NO external LLM call. Runs in <50 ms on the
                          appliance.

Data source: re-uses `views_logs._aggregate()` so the engine sees
exactly the same events the timeline shows.  No new disk reads, no
new caches to invalidate.
"""

from __future__ import annotations

import math
import statistics
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from django.http import JsonResponse
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.permissions import AllowAny

from .views_logs import _aggregate

# ── Tunables ──────────────────────────────────────────────────────────────────
WINDOW_MIN              = 5         # bucket width for anomaly detection
LOOKBACK_HOURS          = 24
INCIDENT_GAP_SEC        = 10 * 60   # events within 10 min collapse into 1 incident
INCIDENT_MIN_EVENTS     = 2         # below that it's just a single event
ANOMALY_MIN_COUNT       = 4         # ignore microscopic spikes ("1 vs 0.1")
ANOMALY_Z_THRESHOLD     = 2.8       # ~99.5 % single-tail
FORECAST_HORIZON_MIN    = 30
FORECAST_BUCKETS        = 12        # last 12 × 5-min = 1 h of history

# Service dependency hints — only used to suggest a probable cause.
# "If A goes critical and B errors right after, blame A."
DEPENDENCY_HINTS = [
    ("squid",       ["nginx", "proxy"],
     "Squid s'est arrêté → les requêtes proxy remontent en 502 sur nginx."),
    ("postgresql",  ["uvicorn", "django", "backup"],
     "PostgreSQL est tombé → Django/uvicorn rejette les requêtes, les backups DB échouent."),
    ("strongswan",  ["ipsec", "vpn"],
     "strongSwan a redémarré → les tunnels IPsec ont rebattu, sessions VPN coupées."),
    ("nftables",    ["firewall", "nat", "rules"],
     "nftables a été rechargé → règles firewall/NAT temporairement absentes."),
    ("suricata",    ["ids", "ips"],
     "Suricata est en échec → l'IDS/IPS ne filtre plus, fenêtre d'exposition."),
    ("redis",       ["celery", "tasks"],
     "Redis indisponible → Celery ne consomme plus, tâches planifiées en retard."),
]


# ── Helpers ───────────────────────────────────────────────────────────────────
def _parse_iso(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def _bucket_index(dt: datetime, now: datetime, width_min: int, total_min: int) -> int:
    """Return bucket index (0 = oldest, last = most recent) or -1 if out of range."""
    delta_min = (now - dt).total_seconds() / 60.0
    if delta_min < 0 or delta_min >= total_min:
        return -1
    n_buckets = total_min // width_min
    return n_buckets - 1 - int(delta_min // width_min)


def _ewma_baseline(values: list[float], alpha: float = 0.25) -> tuple[float, float]:
    """EWMA mean + simple residual std. Robust on short, spiky series."""
    if not values:
        return 0.0, 0.0
    m = values[0]
    for v in values[1:]:
        m = alpha * v + (1 - alpha) * m
    if len(values) > 1:
        try:
            std = statistics.pstdev(values)
        except statistics.StatisticsError:
            std = 0.0
    else:
        std = 0.0
    return m, std


def _linreg(ys: list[float]) -> tuple[float, float, float]:
    """Plain OLS on (i, y). Returns (slope, intercept, r_squared)."""
    n = len(ys)
    if n < 2:
        return 0.0, ys[0] if ys else 0.0, 0.0
    xs = list(range(n))
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return 0.0, my, 0.0
    slope = num / den
    intercept = my - slope * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
    return slope, intercept, max(0.0, min(1.0, r2))


def _kind_fr(k: str) -> str:
    return {"backup": "Backups", "restore": "Restaurations", "snapshot": "Snapshots",
            "migration": "Migration", "notify": "Notifications",
            "auth": "Authentification", "alert": "Alertes"}.get(k, k)


# ── 1. Anomaly detection ──────────────────────────────────────────────────────
def _detect_anomalies(events: list[dict], now: datetime) -> list[dict]:
    """Bucket every event by (source, 5-min slot) over last 24 h.
    Flag the most recent bucket of each source if it sits > ANOMALY_Z_THRESHOLD
    stddevs above the EWMA baseline of the preceding buckets.
    """
    total_min = LOOKBACK_HOURS * 60
    n_buckets = total_min // WINDOW_MIN
    by_source: dict[str, list[int]] = defaultdict(lambda: [0] * n_buckets)

    for ev in events:
        dt = _parse_iso(ev.get("ts"))
        if not dt:
            continue
        idx = _bucket_index(dt, now, WINDOW_MIN, total_min)
        if idx < 0:
            continue
        src = ev.get("source") or ev.get("kind") or "system"
        by_source[src][idx] += 1

    anomalies = []
    for src, series in by_source.items():
        if sum(series) == 0:
            continue
        # Consider the LAST non-empty bucket as the "current" reading.
        # Looking at exactly bucket[-1] would miss a spike that just landed
        # 1-2 min ago in a still-filling bucket.
        recent = series[-3:]
        current = max(recent)
        if current < ANOMALY_MIN_COUNT:
            continue
        baseline_window = series[:-3] if len(series) > 3 else series
        baseline_mean, baseline_std = _ewma_baseline(
            [float(x) for x in baseline_window]
        )
        # Avoid division-by-zero on perfectly flat history; use 1 as floor.
        denom = max(baseline_std, 1.0)
        z = (current - baseline_mean) / denom
        if z < ANOMALY_Z_THRESHOLD:
            continue
        anomalies.append({
            "id":        f"anom-{src}-{int(now.timestamp())}",
            "source":    src,
            "observed":  int(current),
            "baseline":  round(baseline_mean, 2),
            "z_score":   round(z, 2),
            "severity":  "critical" if z >= 5 else "warning",
            "window":    f"{WINDOW_MIN} min",
            "title":     f"Activité inhabituelle sur {src}",
            "detail": (f"{int(current)} événements observés sur {WINDOW_MIN} min, "
                       f"vs ~{baseline_mean:.1f} en moyenne (z = {z:.1f}σ)."),
        })

    # Sort by severity then z-score descending.
    anomalies.sort(key=lambda a: (a["severity"] != "critical", -a["z_score"]))
    return anomalies[:6]


# ── 2. Incident correlation ───────────────────────────────────────────────────
def _root_cause_hint(components: list[str], events: list[dict]) -> str:
    """Walk the dependency map. If a 'parent' component had a critical event
    BEFORE its dependants started failing, point at it."""
    comps_lower = {c.lower() for c in components}
    # Build chronological list of (component, severity) pairs.
    timed = []
    for ev in sorted(events, key=lambda e: e.get("ts") or ""):
        src = (ev.get("source") or "").lower()
        timed.append((src, ev.get("severity", "info")))
    for parent, deps, hint in DEPENDENCY_HINTS:
        if parent not in " ".join(comps_lower):
            continue
        # Did parent fire before any dep?
        parent_idx = next(
            (i for i, (s, sv) in enumerate(timed)
             if parent in s and sv in ("error", "critical")),
            -1,
        )
        if parent_idx < 0:
            continue
        dep_later = any(
            any(d in s for d in deps) and sv in ("error", "critical", "warning")
            for s, sv in timed[parent_idx + 1:]
        )
        if dep_later:
            return hint
    # Generic fallback hints.
    if len(components) == 1:
        return (f"Toutes les erreurs proviennent de « {components[0]} ». "
                "Vérifier l'état du service et ses dépendances en amont.")
    return ("Plusieurs composants ont émis des erreurs dans la même fenêtre. "
            "Chercher un événement déclencheur commun (réseau, alimentation, "
            "redémarrage planifié).")


def _correlate_incidents(events: list[dict], now: datetime) -> list[dict]:
    """Sliding window over error/critical events. Consecutive events whose
    timestamps are within INCIDENT_GAP_SEC of the running cluster boundary
    collapse into a single incident."""
    bad = []
    for ev in events:
        if ev.get("severity") not in ("error", "critical", "warning"):
            continue
        dt = _parse_iso(ev.get("ts"))
        if not dt:
            continue
        if (now - dt).total_seconds() > LOOKBACK_HOURS * 3600:
            continue
        bad.append((dt, ev))

    if not bad:
        return []

    # Sort chronologically — oldest first — so cluster boundaries are stable.
    bad.sort(key=lambda x: x[0])

    clusters: list[list[tuple[datetime, dict]]] = []
    for dt, ev in bad:
        if clusters and (dt - clusters[-1][-1][0]).total_seconds() <= INCIDENT_GAP_SEC:
            clusters[-1].append((dt, ev))
        else:
            clusters.append([(dt, ev)])

    incidents = []
    for i, cluster in enumerate(clusters):
        if len(cluster) < INCIDENT_MIN_EVENTS:
            continue
        components = sorted({(ev.get("source") or "system") for _, ev in cluster})
        sev_rank = {"warning": 1, "error": 2, "critical": 3}
        top_sev = max((ev.get("severity", "warning") for _, ev in cluster),
                      key=lambda s: sev_rank.get(s, 0))
        started = cluster[0][0]
        ended   = cluster[-1][0]
        duration_min = max(1, int((ended - started).total_seconds() / 60))
        events_only = [ev for _, ev in cluster]
        hint = _root_cause_hint(components, events_only)

        # Stable, human-friendly incident id (date + first 4 chars of first ref).
        first_ref = (events_only[0].get("ref_id") or "")[:4] or f"{i+1:03d}"
        inc_id = f"INC-{started.strftime('%m%d')}-{first_ref}"

        # Newest 4 events first — that's what the UI card previews.
        preview = sorted(
            events_only, key=lambda e: e.get("ts") or "", reverse=True
        )[:4]

        incidents.append({
            "id":           inc_id,
            "started_at":   started.isoformat(),
            "ended_at":     ended.isoformat(),
            "duration_min": duration_min,
            "components":   components,
            "severity":     top_sev,
            "event_count":  len(cluster),
            "root_cause":   hint,
            "events":       [{
                "ts":       ev.get("ts"),
                "source":   ev.get("source"),
                "severity": ev.get("severity"),
                "title":    ev.get("title"),
            } for ev in preview],
        })

    # Newest incidents first, capped.
    incidents.sort(key=lambda x: x["started_at"], reverse=True)
    return incidents[:5]


# ── 3. 30-min forecast ────────────────────────────────────────────────────────
def _forecast(events: list[dict], now: datetime) -> dict:
    """Project the next 30 min of error volume from the last 12 × 5-min buckets."""
    width_min = WINDOW_MIN
    total_min = FORECAST_BUCKETS * width_min
    series = [0] * FORECAST_BUCKETS
    for ev in events:
        if ev.get("severity") not in ("error", "critical"):
            continue
        dt = _parse_iso(ev.get("ts"))
        if not dt:
            continue
        idx = _bucket_index(dt, now, width_min, total_min)
        if idx < 0:
            continue
        series[idx] += 1

    slope, intercept, r2 = _linreg([float(v) for v in series])
    # Project FORECAST_HORIZON_MIN / WINDOW_MIN buckets forward → average.
    horizon_buckets = FORECAST_HORIZON_MIN // width_min
    projected = [max(0.0, slope * (len(series) + i) + intercept)
                 for i in range(horizon_buckets)]
    projected_avg = sum(projected) / max(1, len(projected))
    current_avg = sum(series[-3:]) / 3.0

    # Decision rules (intentionally explainable, not a black box).
    # `direction` drives the client-facing trend chip; `rationale` is kept in
    # plain language (no rates / slopes / confidence figures) so the product
    # never exposes its internal model to the end customer.
    if projected_avg < 0.5 and current_avg < 0.5:
        state, direction = "stable", "flat"
        rationale = "Aucune erreur récente, situation stable."
    elif slope > 0.4 and current_avg > 1.0:
        state, direction = "risk", "up"
        rationale = "Les erreurs augmentent, à surveiller de près."
    elif current_avg > 1.5:
        state, direction = "watch", "flat"
        rationale = "Niveau d'erreurs élevé mais stable."
    elif slope < -0.3:
        state, direction = "stable", "down"
        rationale = "Les erreurs diminuent, retour à la normale."
    else:
        state, direction = "stable", "flat"
        rationale = "Activité normale."

    # Convert R² + sample size into a 0-100 confidence score. Kept internally
    # (drives nothing client-facing) but no longer surfaced in the UI.
    confidence = int(round(50 + 50 * r2 * min(1.0, len(series) / 12.0)))
    return {
        "horizon_min":     FORECAST_HORIZON_MIN,
        "predicted_state": state,
        "direction":       direction,       # up | flat | down
        "confidence_pct":  confidence,
        "rationale":       rationale,
        "series":          series,
    }


# ── 4. Natural-language summary ───────────────────────────────────────────────
def _summarize(events: list[dict], anomalies: list[dict],
               incidents: list[dict], forecast: dict) -> str:
    n_total = len(events)
    n_errors = sum(1 for e in events
                   if e.get("severity") in ("error", "critical"))
    n_success = sum(1 for e in events if e.get("severity") == "success")
    n_backups_ok = sum(1 for e in events
                       if e.get("kind") == "backup" and e.get("severity") == "success")
    n_backups_ko = sum(1 for e in events
                       if e.get("kind") == "backup"
                       and e.get("severity") in ("error", "critical"))

    parts = []

    # Headline tone.
    if forecast["predicted_state"] == "risk":
        parts.append("⚠ Le système montre des signes de dégradation.")
    elif incidents:
        parts.append(
            f"Le système a connu {len(incidents)} incident"
            f"{'s' if len(incidents) > 1 else ''} corrélé"
            f"{'s' if len(incidents) > 1 else ''} sur les dernières 24 h.")
    elif n_errors == 0:
        parts.append("Système stable sur les dernières 24 h. Aucune erreur.")
    else:
        parts.append(
            f"Activité nominale : {n_errors} erreur{'s' if n_errors > 1 else ''} "
            f"isolée{'s' if n_errors > 1 else ''} sur {n_total} événements.")

    # Anomaly mention (plain language — no statistical figures exposed).
    if anomalies:
        first = anomalies[0]
        parts.append(f"Pic d'activité détecté sur « {first['source']} ».")

    # Backups.
    if n_backups_ok or n_backups_ko:
        if n_backups_ko:
            parts.append(
                f"{n_backups_ok} backup{'s' if n_backups_ok > 1 else ''} OK, "
                f"{n_backups_ko} en échec — à vérifier.")
        else:
            parts.append(
                f"{n_backups_ok} backup{'s' if n_backups_ok > 1 else ''} "
                f"réussi{'s' if n_backups_ok > 1 else ''}, aucun échec.")

    # Forecast — plain wording, no confidence percentage.
    state_fr = {"stable": "tendance stable",
                "watch":  "à surveiller",
                "risk":   "tendance à la hausse"}
    parts.append(f"Prochaines 30 min : {state_fr[forecast['predicted_state']]}.")

    return " ".join(parts)


def _overall_state(forecast: dict, incidents: list[dict],
                   anomalies: list[dict]) -> str:
    if forecast["predicted_state"] == "risk":
        return "critical"
    if any(i["severity"] == "critical" for i in incidents):
        return "critical"
    if incidents or any(a["severity"] == "critical" for a in anomalies):
        return "degraded"
    if anomalies or forecast["predicted_state"] == "watch":
        return "watch"
    return "healthy"


# ── Endpoint ──────────────────────────────────────────────────────────────────
@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def logs_intelligence(request):
    """GET /backup/logs/intelligence → AI Log Intelligence snapshot.

    Computes everything on the fly from the same event stream the timeline
    uses. Cheap enough (<50 ms on a typical 1000-event window) that we don't
    bother caching — the UI polls every 15 s and we want fresh truth.
    """
    now = datetime.now(timezone.utc)
    since_iso = (now - timedelta(hours=LOOKBACK_HOURS)).isoformat()
    events = _aggregate(since_iso=since_iso, limit=2000)

    anomalies = _detect_anomalies(events, now)
    incidents = _correlate_incidents(events, now)
    forecast  = _forecast(events, now)
    summary   = _summarize(events, anomalies, incidents, forecast)
    state     = _overall_state(forecast, incidents, anomalies)

    # Plain, client-facing counts for the status banner.
    counts = {
        "total":      len(events),
        "errors":     sum(1 for e in events
                          if e.get("severity") in ("error", "critical")),
        "backups_ok": sum(1 for e in events
                          if e.get("kind") == "backup"
                          and e.get("severity") == "success"),
        "backups_ko": sum(1 for e in events
                          if e.get("kind") == "backup"
                          and e.get("severity") in ("error", "critical")),
    }

    return JsonResponse({
        "generated_at":   now.isoformat(),
        "overall_state":  state,            # healthy | watch | degraded | critical
        "summary":        summary,
        "counts":         counts,
        "anomalies":      anomalies,
        "incidents":      incidents,
        "forecast":       forecast,
        "stats": {
            "events_analyzed":  len(events),
            "lookback_hours":   LOOKBACK_HOURS,
            "anomaly_count":    len(anomalies),
            "incident_count":   len(incidents),
        },
    })
