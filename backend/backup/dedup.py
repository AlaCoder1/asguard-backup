"""
Backup de-duplication engine — "Analyse intelligente du stockage".

Detects backups that hold the SAME configuration and lets the operator reclaim
space by keeping one copy per identical group. 100% deterministic (no LLM): a
content fingerprint is computed from the actual managed configuration, so two
backups match iff their configuration is truly identical — no false positives.

Why not the existing per-component sha256?
    Those hashes are taken over the produced `.tar.gz` / `.dump`, which embed
    timestamps (and, for firewall, live nftables packet counters), so they differ
    on every single backup even when nothing changed. Useless for dedup.

Fingerprint strategy (validated on real backups):
    For each CONFIG component we hash its STABLE content:
      • if `component_db.json` exists  → hash the serialized Django models
        (the pure, managed configuration — ignores runtime noise in the tar);
      • else                           → hash the tar members' *content*
        (path + bytes, mtime-stripped) — for file-only config (certificates…).
    The backup fingerprint = sha256 over the sorted per-component hashes.

    Only the user-facing CONFIG components are fingerprinted; volatile/runtime
    components (logs, raw DB dump, package lists, systemd/docker state, app code)
    are deliberately excluded so identical configuration always matches.
"""
import hashlib
import json
import logging
import tarfile
from pathlib import Path

logger = logging.getLogger(__name__)

BACKUP_ROOT = Path("/var/backups/asguard")
_CACHE_DIR = BACKUP_ROOT / "dedup_cache"

# Canonical user-facing CONFIGURATION components (the "safe backup" set). The
# fingerprint is computed ONLY over these; everything else is runtime noise.
CONFIG_COMPONENTS = frozenset({
    "firewall", "vpn", "ids", "proxy", "network", "certificates", "routing",
    "nat", "dhcp", "waf", "ztna", "ipsec_detailed", "vlan", "vxlan", "sdwan",
    "gateway", "double_mask",
})

# Human labels for the UI (per-component diff readout).
COMPONENT_LABELS = {
    "firewall": "Pare-feu", "vpn": "VPN", "ids": "IDS/IPS", "proxy": "Proxy",
    "network": "Réseau", "certificates": "Certificats", "routing": "Routage",
    "nat": "NAT", "dhcp": "DHCP", "waf": "WAF", "ztna": "ZTNA",
    "ipsec_detailed": "IPsec", "vlan": "VLAN", "vxlan": "VXLAN", "sdwan": "SD-WAN",
    "gateway": "Passerelle", "double_mask": "Double masque",
}


def _component_content_hash(comp_dir: Path) -> str | None:
    """Stable content hash of one component (see module docstring)."""
    db_file = comp_dir / "component_db.json"
    if db_file.exists():
        try:
            models = json.loads(db_file.read_text(encoding="utf-8")).get("models", {})
            return "db:" + hashlib.sha256(
                json.dumps(models, sort_keys=True, ensure_ascii=False).encode("utf-8")
            ).hexdigest()
        except Exception:
            logger.warning("dedup: unreadable component_db.json in %s", comp_dir)
            return None
    h = hashlib.sha256()
    seen = False
    for tar in sorted(comp_dir.glob("*.tar.gz")):
        try:
            with tarfile.open(tar, "r:gz") as tf:
                for member in sorted(tf.getmembers(), key=lambda m: m.name):
                    h.update(member.name.encode("utf-8"))
                    seen = True
                    if member.isfile():
                        fh = tf.extractfile(member)
                        if fh is not None:
                            h.update(fh.read())
        except Exception:
            logger.warning("dedup: unreadable archive %s", tar)
            return None
    return "tar:" + h.hexdigest() if seen else None


def component_hashes(backup_dir: Path) -> dict[str, str]:
    """Per-config-component content hash for a backup (present components only)."""
    out: dict[str, str] = {}
    for name in sorted(CONFIG_COMPONENTS):
        cdir = backup_dir / name
        if cdir.is_dir():
            hsh = _component_content_hash(cdir)
            if hsh:
                out[name] = hsh
    return out


def _fingerprint_from_hashes(hashes: dict[str, str]) -> str:
    blob = "\n".join(f"{k}={v}" for k, v in sorted(hashes.items()))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def fingerprint_for(backup_id: str, *, use_cache: bool = True) -> dict:
    """Return {fingerprint, components, n_components} for a backup.

    Backups are immutable once finalized, so the result is cached in a sidecar
    under dedup_cache/ (NOT inside the backup dir — that would break the signed
    integrity manifest)."""
    cache_file = _CACHE_DIR / f"{backup_id}.json"
    if use_cache and cache_file.exists():
        try:
            return json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    backup_dir = BACKUP_ROOT / backup_id
    hashes = component_hashes(backup_dir) if backup_dir.is_dir() else {}
    data = {
        "fingerprint": _fingerprint_from_hashes(hashes),
        "components": hashes,
        "n_components": len(hashes),
    }
    try:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps(data), encoding="utf-8")
    except Exception:
        logger.warning("dedup: could not cache fingerprint for %s", backup_id)
    return data


def compare(backup_id_a: str, backup_id_b: str) -> dict:
    """Config similarity between two backups: % identical + which components changed."""
    a = fingerprint_for(backup_id_a).get("components", {})
    b = fingerprint_for(backup_id_b).get("components", {})
    names = sorted(set(a) | set(b))
    identical, changed, only_a, only_b = [], [], [], []
    for n in names:
        if n in a and n in b:
            (identical if a[n] == b[n] else changed).append(n)
        elif n in a:
            only_a.append(n)
        else:
            only_b.append(n)
    total = len(names) or 1
    label = lambda names_: [COMPONENT_LABELS.get(n, n) for n in names_]
    return {
        "a": backup_id_a,
        "b": backup_id_b,
        "identical_count": len(identical),
        "changed_count": len(changed),
        "total": len(names),
        "similarity_pct": round(100 * len(identical) / total),
        "identical": identical,
        "changed": changed,
        "only_in_a": only_a,
        "only_in_b": only_b,
        "identical_labels": label(identical),
        "changed_labels": label(changed),
        "only_in_a_labels": label(only_a),
        "only_in_b_labels": label(only_b),
        "is_identical": not changed and not only_a and not only_b and bool(identical),
    }


def find_duplicate_groups(items: list[dict]) -> dict:
    """Group backups by (type, fingerprint) and flag redundant copies.

    `items`: dicts with at least id, type, size_bytes, modified_at (as returned
    by _collect_backup_results). In each identical group the NEWEST backup is
    kept and the older ones are marked redundant (reclaimable space)."""
    buckets: dict[tuple[str, str], list[dict]] = {}
    for it in items:
        bid = it.get("id")
        if not bid:
            continue
        # Only dedup real component backups (skip legacy .dump-only entries).
        if not (BACKUP_ROOT / bid).is_dir():
            continue
        fp = fingerprint_for(bid)
        if fp["n_components"] == 0:
            continue  # nothing to compare (e.g. non-config backup)
        key = (it.get("type", "?"), fp["fingerprint"])
        buckets.setdefault(key, []).append({**it, "_fp": fp["fingerprint"]})

    groups = []
    total_reclaimable = 0
    total_redundant = 0
    for (btype, fp), members in buckets.items():
        if len(members) < 2:
            continue
        members.sort(key=lambda x: x.get("modified_at", ""), reverse=True)
        keep = members[0]
        redundant = members[1:]
        reclaimable = sum(int(m.get("size_bytes", 0) or 0) for m in redundant)
        total_reclaimable += reclaimable
        total_redundant += len(redundant)
        groups.append({
            "fingerprint": fp,
            "backup_type": btype,
            "count": len(members),
            "keep_id": keep["id"],
            "reclaimable_bytes": reclaimable,
            "members": [
                {
                    "id": m["id"],
                    "modified_at": m.get("modified_at"),
                    "size_bytes": int(m.get("size_bytes", 0) or 0),
                    "keep": m["id"] == keep["id"],
                }
                for m in members
            ],
        })

    groups.sort(key=lambda g: g["reclaimable_bytes"], reverse=True)
    return {
        "groups": groups,
        "duplicate_groups": len(groups),
        "redundant_backups": total_redundant,
        "reclaimable_bytes": total_reclaimable,
    }


def redundant_ids(items: list[dict], *, only_group: str | None = None) -> list[str]:
    """Backup ids that can be safely deleted (all but the newest of each identical
    group). If `only_group` (a fingerprint) is given, restrict to that group."""
    analysis = find_duplicate_groups(items)
    ids: list[str] = []
    for g in analysis["groups"]:
        if only_group and g["fingerprint"] != only_group:
            continue
        ids.extend(m["id"] for m in g["members"] if not m["keep"])
    return ids
