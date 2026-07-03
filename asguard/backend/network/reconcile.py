"""
Network DB reconciliation — make the DB reflect the REAL system network config.

The appliance has three layers that must agree:
  1. UI (Asguard)      ← reads the DB
  2. System CLI         ← NetworkManager profiles / `ip` (the source of truth)
  3. DB (Django models) ← Interface / IP4Config / Vlan / Vxlan

A change made directly in CLI (nmcli, ip) updates the system but NOT the DB, so
the UI goes stale. `reconcile_network_db_from_system()` reads the NetworkManager
profiles and writes the DB to match — so CLI edits flow back into the UI, and a
DR restore (which restores NM profiles + DB independently) ends up consistent.

System is authoritative. User-defined labels (Interface.name_interface,
is_main) are preserved. Nothing is deleted — stale DB rows are only reported.
"""
import logging
import subprocess

from backend.network.models import Interface, IP4Config

logger = logging.getLogger(__name__)

# Virtual/bridge interfaces that are not part of the appliance network identity.
_EXCLUDE_PREFIXES = ("lo", "docker", "br-", "veth", "vmnet", "virbr", "ip_vti")


def _nmcli(*args, timeout=15):
    try:
        r = subprocess.run(["nmcli", *args], capture_output=True,
                           text=True, timeout=timeout)
        return r.stdout if r.returncode == 0 else ""
    except Exception as exc:
        logger.warning("reconcile: nmcli %s failed: %s", " ".join(args), exc)
        return ""


def _get(conn, fields):
    """Return nmcli -g values for one connection as a list, '' for missing."""
    out = _nmcli("-g", ",".join(fields), "connection", "show", conn)
    # nmcli -g emits one line per requested field, in order.
    lines = out.split("\n")
    vals = [lines[i].strip() if i < len(lines) else "" for i in range(len(fields))]
    return vals


def _excluded(ifname):
    return not ifname or ifname.startswith(_EXCLUDE_PREFIXES)


def _live_ipv4(ifname):
    """Return (ip, prefix) of the interface's current live IPv4, or (None, None).
    Used for DHCP interfaces whose address isn't in the static profile."""
    out = _nmcli("-g", "IP4.ADDRESS", "device", "show", ifname)
    first = (out.split("\n")[0] if out else "").strip()
    if "/" in first:
        ip, _, pfx = first.partition("/")
        return (ip or None), (int(pfx) if pfx.isdigit() else None)
    return None, None


def _ensure_interface(ifname, default_label):
    """get-or-create an Interface by ifname, preserving user label/is_main."""
    iface = Interface.objects.filter(ifname=ifname).first()
    if iface:
        return iface, False
    # New interface (e.g. a VLAN created via CLI). Pick a non-colliding label.
    label = default_label or ifname
    if Interface.objects.filter(name_interface=label).exclude(ifname=ifname).exists():
        label = ifname
    iface = Interface.objects.create(ifname=ifname, name_interface=label)
    return iface, True


def reconcile_network_db_from_system():
    """Sync DB (Interface/IP4Config/Vlan/Vxlan) from the live NM profiles.
    Idempotent. Returns a report dict."""
    report = {"created": [], "updated": [], "stale": [], "errors": []}

    listing = _nmcli("-t", "-f", "NAME,TYPE,DEVICE", "connection", "show")
    if not listing:
        report["errors"].append("nmcli returned nothing")
        return report

    seen_ifnames = set()
    seen_vlan_tags = set()
    seen_vxlan_ids = set()

    for line in listing.splitlines():
        # NAME may contain ':'? nmcli -t escapes field separators with '\:'.
        parts = line.replace("\\:", "\x00").split(":")
        if len(parts) < 2:
            continue
        name = parts[0].replace("\x00", ":")
        ctype = parts[1]

        if ctype not in ("802-3-ethernet", "ethernet", "vlan", "vxlan"):
            continue

        try:
            ifn, method, addrs, gw = _get(
                name, ["connection.interface-name", "ipv4.method",
                       "ipv4.addresses", "ipv4.gateway"])
            if _excluded(ifn):
                continue
            seen_ifnames.add(ifn)

            iface, created = _ensure_interface(ifn, name)
            if created:
                report["created"].append(f"interface:{ifn}")

            _reconcile_ip4(iface, method, addrs, gw, report)

            if ctype == "vlan":
                _reconcile_vlan(name, ifn, report, seen_vlan_tags)
            elif ctype == "vxlan":
                _reconcile_vxlan(name, ifn, report, seen_vxlan_ids)

        except Exception as exc:
            logger.exception("reconcile: connection %s failed", name)
            report["errors"].append(f"{name}: {exc}")

    _collect_stale(seen_ifnames, seen_vlan_tags, seen_vxlan_ids, report)
    logger.info("reconcile_network_db_from_system: created=%d updated=%d stale=%d",
                len(report["created"]), len(report["updated"]), len(report["stale"]))
    return report


def _reconcile_ip4(iface, method, addrs, gw, report):
    existing = IP4Config.objects.filter(interface=iface).first()

    if method != "manual":
        # auto/dhcp: store the CURRENT live lease so the UI + console menu can
        # show the address (they read ip_address from the DB).
        live_ip, live_pfx = _live_ipv4(iface.ifname)
        if not live_ip:
            # DHCP interface with no current lease (e.g. an idle VLAN). The app
            # originally kept NO ip4config row for these, so the console menu
            # never listed them. Don't create one; drop a stale blank row if we
            # made one earlier — keeps the original behaviour.
            if existing and not existing.ip_address:
                existing.delete()
                report["updated"].append(f"ip4:{iface.ifname} removed (DHCP, no lease)")
            return

    cfg = existing or IP4Config(interface=iface)
    before = (cfg.typeip4, cfg.ip_address, cfg.netmask, cfg.addrgw, cfg.typedhcp)

    if method == "manual":
        # static: DB stores ip/netmask/gateway
        ip, _, prefix = (addrs.split(";")[0] if addrs else "").partition("/")
        cfg.typeip4 = "STATIC"
        cfg.typedhcp = ""
        cfg.ip_address = ip or None
        cfg.netmask = int(prefix) if prefix.isdigit() else None
        cfg.addrgw = gw or None
    else:
        cfg.typeip4 = "DHCP"
        cfg.typedhcp = cfg.typedhcp or "Base"
        cfg.ip_address = live_ip
        cfg.netmask = live_pfx
        cfg.addrgw = None

    after = (cfg.typeip4, cfg.ip_address, cfg.netmask, cfg.addrgw, cfg.typedhcp)
    if cfg.pk is None or before != after:
        cfg.save()
        report["updated"].append(
            f"ip4:{iface.ifname} {before[0]}/{before[1]} -> {after[0]}/{after[1]}")


def _reconcile_vlan(conn, ifname, report, seen_tags):
    from backend.vlan.models import Vlan
    vid, parent = _get(conn, ["vlan.id", "vlan.parent"])
    if not vid.isdigit():
        return
    tag = int(vid)
    seen_tags.add(tag)
    parent_if = Interface.objects.filter(ifname=parent).first()
    if parent_if is None:
        report["errors"].append(f"vlan {tag}: parent {parent} not in DB")
        return
    obj, created = Vlan.objects.update_or_create(
        vlan_tag=tag, defaults={"parent_interface": parent_if})
    report["created" if created else "updated"].append(f"vlan:{tag} parent={parent}")


def _reconcile_vxlan(conn, ifname, report, seen_ids):
    from backend.vxlan.models import Vxlan
    vid, parent, local, remote, port = _get(
        conn, ["vxlan.id", "vxlan.parent", "vxlan.local",
               "vxlan.remote", "vxlan.destination-port"])
    if not vid.isdigit():
        return
    vx_id = int(vid)
    seen_ids.add(vx_id)
    parent_if = Interface.objects.filter(ifname=parent).first()
    if parent_if is None:
        report["errors"].append(f"vxlan {vx_id}: parent {parent} not in DB")
        return
    defaults = {
        "parent_interface": parent_if,
        "vxlan_interface_name": ifname,
        "vxlan_source_address": local or None,
        "vxlan_destination_address": remote or None,
        "vxlan_destination_port": port or "4789",
        "vxlan_connection_uuid": conn,
    }
    obj, created = Vxlan.objects.update_or_create(vxlan_id=vx_id, defaults=defaults)
    report["created" if created else "updated"].append(f"vxlan:{vx_id} parent={parent}")


def _collect_stale(seen_ifnames, seen_vlan_tags, seen_vxlan_ids, report):
    """Reconcile DB rows that have no matching system config.

    Only reached when the nmcli listing succeeded (the caller returns early
    otherwise), so the `seen_*` sets are trustworthy. VLAN/VXLAN and their
    virtual interfaces are network-derived → safe to DELETE so the DB matches
    the system exactly (e.g. a VLAN removed in CLI / pruned by a restore).
    PHYSICAL interfaces are never deleted (FK cascade to firewall rules) — only
    reported."""
    from backend.vlan.models import Vlan
    from backend.vxlan.models import Vxlan

    for v in Vlan.objects.all():
        if v.vlan_tag not in seen_vlan_tags:
            v.delete()
            report["stale"].append(f"vlan:{v.vlan_tag} (deleted)")
    for vx in Vxlan.objects.all():
        if vx.vxlan_id not in seen_vxlan_ids:
            vx.delete()
            report["stale"].append(f"vxlan:{vx.vxlan_id} (deleted)")
    for i in Interface.objects.all():
        if not i.ifname or _excluded(i.ifname) or i.ifname in seen_ifnames:
            continue
        if i.ifname.startswith(("vlan", "vxlan")):
            i.delete()   # virtual interface, its config is gone
            report["stale"].append(f"interface:{i.ifname} (deleted)")
        else:
            report["stale"].append(f"interface:{i.ifname} (name={i.name_interface}, kept)")
