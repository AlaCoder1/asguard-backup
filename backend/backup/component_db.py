"""
Per-component database snapshot — generic dump/restore of the DB rows that
belong to each backup component.

Background
----------
Backup components historically saved only their *config files* (nftables
config, /etc dirs, app source). The actual operator-facing data —
NAT rules, static routes, VPN servers, WAF rules, … — lives in PostgreSQL
tables. A component-level restore that touched only files therefore did NOT
roll back what the UI shows. Only `firewall` had a bespoke DB sync
(`_restore_firewall_rules_db`).

This module generalises that idea: a registry maps every data-driven
component to its Django models, and two helpers serialise / restore those
rows. The custom backup writes one `component_db.json` per component; the
custom restore replays it. Result: a component restore is now honest —
it brings back both the files AND the database state.

Design notes
------------
* Uses django.core.serializers — model-agnostic, FK stored as PK.
* Log / alert / stats models are deliberately EXCLUDED: they are transient
  telemetry, not configuration, and restoring stale logs is misleading.
* Models are listed parent-first; restore deletes child-first (reversed)
  and recreates parent-first so intra-app FKs resolve.
* Cross-app FKs (e.g. nat.DNat -> network.Interface) are NOT touched — the
  referenced rows must already exist, which they do for an in-place restore.
"""

from __future__ import annotations

import json
import logging

logger = logging.getLogger(__name__)

# Registry: backup component name -> ordered list of "app_label.ModelName".
# Order = creation order (parents first). `firewall` is intentionally absent:
# it keeps its own bespoke `_restore_firewall_rules_db` path.
COMPONENT_MODELS: dict[str, list[str]] = {
    "nat":            ["nat.SNat", "nat.OneToOneNat", "nat.DNat"],
    "routing":        ["routing.Routing"],
    "vpn":            ["openvpn.ServerOpenvpn", "openvpn.ClientOpenvpn"],
    "ipsec_detailed": ["ipsec.ServerIPsec"],
    "ids":            ["ids_ips.SuricataInterface"],
    "waf":            ["waf.ConfigWaf", "waf.ApplicationWaf",
                       "waf.RulesWaf", "waf.ApplicationRulesWaf"],
    "proxy":          ["proxy.ServerSatus", "proxy.ProxyRules", "proxy.ProxyUser"],
    "dhcp":           ["server_dhcp4.ServerDhcp"],
    "vlan":           ["vlan.Vlan"],
    "vxlan":          ["vxlan.Vxlan"],
    "sdwan":          ["sdwan.Area", "sdwan.SdwanRules", "sdwan.AreaInterface"],
    "gateway":        ["gateway.Gateway", "gateway.GatewayInterface"],
    "ztna":           ["ztna.Identities", "ztna.Enrollements",
                       "ztna.InterceptConfigs", "ztna.HostConfigs",
                       "ztna.Services", "ztna.Relays", "ztna.RelaysPolicy",
                       "ztna.ServicesPolicy", "ztna.ServicesRelaysPolicy"],
    "double_mask":    ["double_mask.DoubleMask"],
    "certificates":   ["managementCertificates.CertificateAuthority",
                       "managementCertificates.Certificate"],
}

# Filename written inside each component's backup folder.
DB_SNAPSHOT_FILENAME = "component_db.json"

# Human-friendly labels per model path — used to build a precise restore
# message ("1 NAT DNAT, 0 NAT SNAT" instead of "across 3 tables").
MODEL_LABELS: dict[str, str] = {
    "nat.SNat": "NAT SNAT", "nat.OneToOneNat": "NAT 1-to-1", "nat.DNat": "NAT DNAT",
    "routing.Routing": "routes statiques",
    "openvpn.ServerOpenvpn": "serveurs OpenVPN", "openvpn.ClientOpenvpn": "clients OpenVPN",
    "ipsec.ServerIPsec": "tunnels IPsec",
    "ids_ips.SuricataInterface": "interfaces IDS",
    "waf.ConfigWaf": "config WAF", "waf.ApplicationWaf": "applications WAF",
    "waf.RulesWaf": "règles WAF", "waf.ApplicationRulesWaf": "règles app WAF",
    "proxy.ServerSatus": "état proxy", "proxy.ProxyRules": "règles proxy",
    "proxy.ProxyUser": "utilisateurs proxy",
    "server_dhcp4.ServerDhcp": "serveurs DHCP",
    "vlan.Vlan": "VLAN", "vxlan.Vxlan": "VXLAN",
    "sdwan.Area": "zones SD-WAN", "sdwan.SdwanRules": "règles SD-WAN",
    "sdwan.AreaInterface": "interfaces SD-WAN",
    "gateway.Gateway": "passerelles", "gateway.GatewayInterface": "interfaces passerelle",
    "ztna.Identities": "identités ZTNA", "ztna.Enrollements": "enrôlements ZTNA",
    "ztna.InterceptConfigs": "configs interception", "ztna.HostConfigs": "configs hôte",
    "ztna.Services": "services ZTNA", "ztna.Relays": "relais ZTNA",
    "ztna.RelaysPolicy": "politiques relais", "ztna.ServicesPolicy": "politiques services",
    "ztna.ServicesRelaysPolicy": "politiques services-relais",
    "double_mask.DoubleMask": "règles Double Mask",
    "managementCertificates.CertificateAuthority": "autorités de certification",
    "managementCertificates.Certificate": "certificats",
}


def has_db_snapshot(component: str) -> bool:
    """True when `component` has DB-backed models worth snapshotting."""
    return component in COMPONENT_MODELS


def _resolve_model(path: str):
    """Return the Django model class for an 'app_label.ModelName' path.
    Returns None (and logs) if the model can't be resolved, so a single
    bad registry entry never aborts the whole backup/restore."""
    from django.apps import apps as django_apps
    try:
        app_label, model_name = path.split(".", 1)
        return django_apps.get_model(app_label, model_name)
    except Exception as exc:
        logger.warning("component_db: cannot resolve model %s (%s)", path, exc)
        return None


def dump_component_db(component: str) -> dict:
    """
    Serialise every registered model of `component` into a JSON-able dict:

        {
          "component": "nat",
          "models": {
              "nat.SNat":       "<django-json-string>",
              "nat.OneToOneNat":"<django-json-string>",
              "nat.DNat":       "<django-json-string>",
          },
          "counts": {"nat.SNat": 0, "nat.OneToOneNat": 0, "nat.DNat": 3},
        }

    Never raises — a failing model is skipped and noted in `errors`.
    """
    from django.core import serializers

    models = COMPONENT_MODELS.get(component, [])
    payload: dict = {"component": component, "models": {}, "counts": {}, "errors": []}

    for path in models:
        Model = _resolve_model(path)
        if Model is None:
            payload["errors"].append(f"unresolved model {path}")
            continue
        try:
            qs = Model.objects.all()
            payload["models"][path] = serializers.serialize("json", qs)
            payload["counts"][path] = qs.count()
        except Exception as exc:
            logger.warning("component_db: dump failed for %s (%s)", path, exc)
            payload["errors"].append(f"{path}: {exc}")

    return payload


def restore_component_db(component: str, snapshot: dict) -> tuple[bool, str]:
    """
    Replay a `dump_component_db` payload back into the database.

    Strategy: inside one transaction, delete the component's tables
    child-first (reversed registry order) then recreate parent-first.
    Returns (ok, message). Never raises.
    """
    from django.db import transaction
    from django.core import serializers

    models = COMPONENT_MODELS.get(component, [])
    if not models:
        return True, f"{component}: no DB models registered (files-only component)"

    model_data = (snapshot or {}).get("models", {})
    if not model_data:
        return True, f"{component}: no DB snapshot in backup (older backup format)"

    restored_counts: dict[str, int] = {}
    try:
        with transaction.atomic():
            from django.db import connection
            # Defer FK checks until COMMIT. Django FKs are DEFERRABLE
            # INITIALLY DEFERRED, so the constraint is only validated at
            # COMMIT — by then every row has been recreated with its
            # original PK (serializers preserve PKs), so references resolve.
            with connection.cursor() as cur:
                cur.execute("SET CONSTRAINTS ALL DEFERRED")

                # 1. Wipe child-first. We use raw SQL DELETE rather than the
                #    ORM `.delete()` because some FKs use on_delete=PROTECT
                #    (e.g. routing.Routing.gateway): the ORM refuses such a
                #    delete at the Python level before any SQL runs. Raw SQL
                #    + deferred constraints sidesteps that — the DB-level
                #    check still happens, just at COMMIT when state is whole.
                for path in reversed(models):
                    Model = _resolve_model(path)
                    if Model is None:
                        continue
                    cur.execute(f'DELETE FROM "{Model._meta.db_table}"')

            # 2. Recreate parent-first, preserving primary keys.
            for path in models:
                raw = model_data.get(path)
                if not raw:
                    restored_counts[path] = 0
                    continue
                n = 0
                for obj in serializers.deserialize("json", raw):
                    obj.save()
                    n += 1
                restored_counts[path] = n
    except Exception as exc:
        logger.exception("component_db: restore failed for %s", component)
        return False, f"{component}: DB restore failed — {exc}"

    # Build a precise, human-readable summary: only mention tables that
    # actually have rows, with their friendly label.
    parts = [
        f"{n} {MODEL_LABELS.get(path, path)}"
        for path, n in restored_counts.items() if n > 0
    ]
    total = sum(restored_counts.values())
    if parts:
        detail = ", ".join(parts)
        return True, f"Base de données : {detail} restauré(s)"
    return True, "Base de données : aucune ligne (tables vides dans le snapshot)"
