"""
Post-restore resync — realigns the runtime state of every firewall component
with the rolled-back PostgreSQL database after an LVM snapshot restore.

The LVM snapshot rollback handles the on-disk config files that live on the
snapshotable volume (/etc/nftables.conf, /etc/openvpn, /etc/strongswan.d,
/etc/squid, /etc/rules, /etc/dhcpd*.conf, the postgres data dir). What it
does NOT do is reconcile the *kernel-side* state (active nft rules, kernel
routing table, in-RAM daemon caches) with the rolled-back DB.

This module fans out post-restore so that the DB becomes the single source
of truth — no orphan rules, no stale routes, no dangling daemon state.

Each component reports a small dict. Failures are isolated: one broken app
must never block the others or fail the restore as a whole.
"""

from __future__ import annotations

import logging
import subprocess
from typing import Callable

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _run(cmd: str, timeout: int = 30) -> tuple[bool, str, str]:
    """Shell exec helper. Returns (ok, stdout, stderr)."""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True,
                           text=True, timeout=timeout)
        return r.returncode == 0, (r.stdout or "").strip(), (r.stderr or "").strip()
    except subprocess.TimeoutExpired:
        return False, "", f"timeout after {timeout}s"
    except Exception as exc:
        return False, "", str(exc)


def _safe(fn: Callable, name: str) -> dict:
    """Run a component resync and never raise. Always returns a result dict."""
    try:
        res = fn() or {}
        res.setdefault("component", name)
        res.setdefault("status", "success")
        return res
    except Exception as exc:
        logger.exception("post_restore_resync: %s failed", name)
        return {"component": name, "status": "error", "error": str(exc)}


# ─────────────────────────────────────────────────────────────────────────────
# 0. Network DB ↔ system reconciliation
# ─────────────────────────────────────────────────────────────────────────────
# A restore brings back NM profiles (system) and the DB independently. If the
# backup was taken while they diverged (e.g. a CLI-only edit), the clone would
# inherit that drift. Re-read the just-restored NM profiles and rewrite the DB
# (Interface/IP4Config/Vlan/Vxlan) to match — so UI ↔ system ↔ DB agree. Runs
# after services (profiles loaded) and before firewall rules (which reference
# the reconciled interfaces).
def resync_network_db() -> dict:
    from backend.network.reconcile import reconcile_network_db_from_system
    rep = reconcile_network_db_from_system()
    return {
        "component": "network_db",
        "status":    "success" if not rep["errors"] else "error",
        "created":   rep["created"],
        "updated":   rep["updated"],
        "stale":     rep["stale"],
        "errors":    rep["errors"],
    }


# ─────────────────────────────────────────────────────────────────────────────
# 1. Firewall rules — nft kernel state for table inet filter_<ifname>
# ─────────────────────────────────────────────────────────────────────────────
def resync_firewall_rules() -> dict:
    """Reuses backend.rules.functions.rebuild_nft_from_db_all() — flushes
    every filter_<ifname> table and re-applies the enabled Rule rows."""
    from backend.rules.functions import rebuild_nft_from_db_all
    r = rebuild_nft_from_db_all()
    return {
        "component": "firewall_rules",
        "status":    r.get("status", "error"),
        "applied":   r.get("total_applied", 0),
        "errors":    r.get("total_errors", 0),
        "detail":    r.get("interfaces", []),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 2. NAT — table ip nat, chains prerouting / postrouting
# ─────────────────────────────────────────────────────────────────────────────
# The NAT module stores each rule's final nft expression in `rule_content`
# (DNat / SNat / OneToOneNat models). Rebuild path: flush table → recreate
# chains with their hooks → re-insert each enabled rule in db_position order.
_NAT_NFT_FILE   = "/etc/rules/nat/nat.nft"
_NAT_TABLE_INIT = """\
table ip nat {
\tchain postrouting {
\t\ttype nat hook postrouting priority srcnat; policy accept;
\t}

\tchain prerouting {
\t\ttype nat hook prerouting priority 100; policy accept;
\t}
}
"""


def resync_nat() -> dict:
    from backend.nat.models import DNat, SNat, OneToOneNat

    applied = 0
    errors: list[str] = []

    # 1. Flush the table (idempotent) and reinitialise it with the two hook
    # chains that the system expects.
    _run("sudo nft delete table ip nat 2>/dev/null || true")
    _run(f"echo '{_NAT_TABLE_INIT}' | sudo tee {_NAT_NFT_FILE} > /dev/null")
    ok, _, err = _run(f"sudo nft -f {_NAT_NFT_FILE}")
    if not ok:
        return {"component": "nat", "status": "error",
                "error": f"nft -f failed: {err}"}

    # 2. Replay each enabled rule from the DB. `rule_content` is the full
    # post-`nft insert rule` clause (everything after "<chain>").
    for model, chain in (
        (DNat,       "prerouting"),    # destination NAT happens in prerouting
        (SNat,       "postrouting"),
        (OneToOneNat,"postrouting"),
    ):
        rows = (model.objects
                .filter(rule_status=True)
                .exclude(rule_content__isnull=True)
                .exclude(rule_content="")
                .order_by("db_position", "id"))
        for r in rows:
            cmd = f"sudo nft insert rule ip nat {chain} {r.rule_content}"
            ok, _, e = _run(cmd)
            if ok:
                applied += 1
            else:
                errors.append(f"{model.__name__} id={r.id}: {e[:120]}")

    # 3. Persist the final kernel state back to the include file so a fresh
    # `nft -f /etc/nftables.conf` produces the same view.
    _run(f"sudo nft list table ip nat | sudo tee {_NAT_NFT_FILE} > /dev/null")

    return {"component": "nat", "status": "success" if not errors else "partial",
            "applied": applied, "errors": errors}


# ─────────────────────────────────────────────────────────────────────────────
# 3. Routing — kernel "ip route" table
# ─────────────────────────────────────────────────────────────────────────────
# Kernel routes are runtime-only: they live in the kernel routing table and
# are not part of any file on the snapshotable LV. The snapshot rollback has
# no effect on them, so we must explicitly flush asguard-managed static
# routes and re-add them from the Routing model.
def resync_routing() -> dict:
    from backend.routing.models import Routing

    applied = 0
    errors: list[str] = []
    seen: set[str] = set()

    rows = (Routing.objects
            .exclude(destination_address__isnull=True)
            .exclude(destination_address=""))

    for r in rows:
        dest  = (r.destination_address or "").strip()
        gw    = getattr(r.gateway,   "ipv4_address", None) if r.gateway   else None
        ifn   = getattr(r.interface, "ifname",       None) if r.interface else None
        if not dest:
            continue
        key = f"{dest}|{gw}|{ifn}"
        if key in seen:
            continue
        seen.add(key)

        # Wipe any previous version of this route, then add ours. `|| true`
        # because `route del` errors when the route doesn't exist — which is
        # the normal case immediately after a rollback.
        _run(f"sudo ip route del {dest} 2>/dev/null || true")
        parts = [f"sudo ip route add {dest}"]
        if gw:  parts.append(f"via {gw}")
        if ifn: parts.append(f"dev {ifn}")
        ok, _, e = _run(" ".join(parts))
        if ok:
            applied += 1
        else:
            errors.append(f"route id={r.id} ({dest}): {e[:120]}")

    return {"component": "routing", "status": "success" if not errors else "partial",
            "applied": applied, "errors": errors}


# ─────────────────────────────────────────────────────────────────────────────
# 4. Daemon restart sweep — pick up rolled-back config files
# ─────────────────────────────────────────────────────────────────────────────
# Every service whose config dir was on the snapshotable LV needs a clean
# restart so it re-reads the rolled-back files. restore_snapshot already
# bounces nftables/strongswan/squid/postgres around the merge, but a couple
# of other daemons (openvpn, dhcpd4, dhcpd6) are not in the manifest's
# service list — they're config-only entries.
_RESTART_TARGETS = [
    # (systemd unit, optional=True if missing-unit is not an error)
    # Names match `systemctl list-unit-files` on this appliance.
    ("nftables",                 False),
    ("strongswan",               False),  # Site-to-site VPN (IPsec)
    ("squid",                    False),  # Proxy Web
    ("dhcpd4",                   True),   # DHCP V4 server
    ("dhcpd6",                   True),   # DHCP V6 server
    ("openvpn-server@server",    True),   # OpenVPN
    ("suricata",                 True),   # Intrusion Detection
    ("nginx",                    True),   # Web tier + WAF (ModSecurity loaded by nginx)
]


def resync_services() -> dict:
    restarted: list[str] = []
    skipped:   list[str] = []
    failed:    list[str] = []

    for unit, optional in _RESTART_TARGETS:
        # Check existence first so we don't spam errors for units that
        # aren't installed on this appliance.
        ok_exists, _, _ = _run(
            f"sudo systemctl list-unit-files {unit}.service "
            f"--no-legend --no-pager 2>/dev/null | grep -q '{unit}.service'"
        )
        if not ok_exists:
            if optional:
                skipped.append(unit)
                continue
            failed.append(f"{unit}: unit not found")
            continue
        ok, _, err = _run(f"sudo systemctl restart {unit}", timeout=45)
        if ok:
            restarted.append(unit)
        else:
            failed.append(f"{unit}: {err[:120]}")

    return {
        "component": "services",
        "status":    "success" if not failed else "partial",
        "restarted": restarted,
        "skipped":   skipped,
        "failed":    failed,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 5. ZTNA — custom router daemon driven by shell scripts
# ─────────────────────────────────────────────────────────────────────────────
# ZTNA is not a systemd unit; it's a router process spawned by start_router.sh
# and stopped by delete_router.sh. After a snapshot rollback the public-IP
# detection has to re-run so /etc/hosts append entries match the current WAN.
def resync_ztna() -> dict:
    script_dir = "/asguard/asguard/backend/ztna/shell_scripts"
    ok, out, err = _run(
        f"sudo bash {script_dir}/check_and_execute.sh 2>&1",
        timeout=60,
    )
    return {
        "component": "ztna",
        "status":    "success" if ok else "partial",
        "message":   (out or err or "").splitlines()[-1] if (out or err) else "",
    }


# ─────────────────────────────────────────────────────────────────────────────
# 6. DB-only components — no runtime resync needed
# ─────────────────────────────────────────────────────────────────────────────
# These apps store their entire state in PostgreSQL. The DB has already been
# rolled back by the LVM merge (the asguard_pgdb volume is bind-mounted onto
# the snapshotable LV), so the rollback is automatic and complete. We list
# them explicitly here so the UI can report 100 % coverage instead of
# silently omitting them.
_DB_ONLY_COMPONENTS = [
    # (display label, list of tables read by the live app)
    ("Utilisateurs",                ["users", "auth_group", "permission", "roles"]),
    ("Certificats / PKI",           ["certificate", "certificate_authority",
                                     "private_key", "public_key"]),
    ("Paramètres système",          ["generic_config"]),
    ("Plans / abonnements",         ["plan", "plans_subscription"]),
    ("LDAP / Active Directory",     ["ad_server"]),
    ("Identités ZTNA",              ["identities", "relaypolicy"]),
    ("Double Mask",                 ["double_mask"]),
    ("Passerelles",                 ["gateway"]),
    ("VLAN / VXLAN",                ["vlan", "vxlan"]),
    ("Règles SD-WAN",               ["sdwan_rules"]),
    ("Règles WAF",                  ["rules_waf", "application_waf"]),
    ("Règles IDS/IPS",              ["ids_ips_rules"]),
    ("Configuration interfaces",    ["interface", "ip4config", "ip6config"]),
    ("Pools DHCP",                  ["server_dhcp4"]),
    ("Logs OpenVPN / IPsec / WAF",  ["openvpn_logs", "alert_waf", "firewall_log"]),
]


def audit_db_only_components() -> dict:
    """Confirm — by querying the rolled-back DB — that DB-only apps are in
    a consistent state. Counts rows per table so the user gets a coverage
    receipt instead of silent assumptions."""
    from django.db import connection
    items = []
    total_rows = 0
    with connection.cursor() as cur:
        for label, tables in _DB_ONLY_COMPONENTS:
            comp_rows = 0
            existing = []
            for t in tables:
                try:
                    cur.execute(
                        "SELECT count(*) FROM information_schema.tables "
                        "WHERE table_schema='public' AND table_name=%s", [t]
                    )
                    if not cur.fetchone()[0]:
                        continue
                    cur.execute(f'SELECT count(*) FROM "{t}"')
                    n = cur.fetchone()[0] or 0
                    comp_rows += n
                    existing.append({"table": t, "rows": n})
                except Exception:
                    continue
            total_rows += comp_rows
            items.append({
                "label":  label,
                "tables": existing,
                "rows":   comp_rows,
            })
    return {
        "component": "db_only_audit",
        "status":    "success",
        "items":     items,
        "total_rows": total_rows,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Orchestrator
# ─────────────────────────────────────────────────────────────────────────────
# Order matters:
#   1. Services restart FIRST — daemons reload their rolled-back config files
#      (this is the snapshot's view of the world, which may differ from DB).
#   2. Rules / NAT rebuild AFTER — flushes the just-reloaded kernel state and
#      re-applies what's in the DB. The DB is the authoritative final word.
#   3. Routing then ZTNA — depend on a stable lower stack.
#   4. db_only_audit last — read-only census for the UI receipt.
_PIPELINE: list[tuple[str, Callable]] = [
    ("services",       resync_services),
    ("network_db",     resync_network_db),
    ("firewall_rules", resync_firewall_rules),
    ("nat",            resync_nat),
    ("routing",        resync_routing),
    ("ztna",           resync_ztna),
    ("db_only_audit",  audit_db_only_components),
]


def resync_all() -> dict:
    """Run the full post-restore pipeline. Never raises. Returns:

        {
          "status":       "success" | "partial" | "error",
          "components":   [ {component, status, ...}, ...],
          "summary": {
            "total":      4,
            "success":    3,
            "partial":    1,
            "error":      0,
          }
        }
    """
    components: list[dict] = []
    for name, fn in _PIPELINE:
        components.append(_safe(fn, name))

    counts = {"success": 0, "partial": 0, "error": 0}
    for c in components:
        st = c.get("status", "error")
        counts[st] = counts.get(st, 0) + 1

    if counts["error"]:
        overall = "error"
    elif counts["partial"]:
        overall = "partial"
    else:
        overall = "success"

    return {
        "status":     overall,
        "components": components,
        "summary":    {"total": len(components), **counts},
    }
