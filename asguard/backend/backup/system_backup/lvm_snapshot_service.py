"""
lvm_snapshot_service.py — LVM snapshot management for Asguard

Uses lvcreate / lvremove / lvconvert (lvm2) to manage snapshots
of the asguard-data logical volume.

Layout:
  /dev/sdb        → Physical Volume
  asguard-vg      → Volume Group  (30 GB)
  asguard-data    → Logical Volume (25 GB, mounted /var/asguard_data)
  [5 GB free]     → CoW space for snapshots
"""

import json
import logging
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)
LOCAL_TZ = ZoneInfo("Africa/Tunis")


class LVMSnapshotService:
    VG_NAME     = "asguard-vg"
    LV_NAME     = "asguard-data"
    MOUNT_POINT = Path("/var/asguard_data")

    # Operational state lives on the root filesystem, NOT under
    # /var/backups/asguard — that path is bind-mounted onto the snapshotable
    # LV once the migration is applied, which would mean a restore reverts the
    # job-tracking files themselves (freezing a "running" job forever and
    # hanging the UI). /var/lib/asguard is on sda4 and survives every merge.
    STATE_ROOT  = Path("/var/lib/asguard/lvm")
    META_DIR    = STATE_ROOT / "snapshots_meta"
    CONFIG_FILE = STATE_ROOT / "snapshot_config.json"
    JOBS_DIR    = STATE_ROOT / "snapshot_jobs"

    # Where backups + schedule are staged (off the snapshotable LV) during a
    # restore so a point-in-time rollback doesn't erase backups taken after the
    # snapshot, and an off-LV marker the scheduler checks to suppress the
    # missed-run catchup while a merge is in flight (the on-LV `.in_restore`
    # lock gets reverted by the merge itself, so it can't cover this window).
    STAGING_DIR        = STATE_ROOT / "restore_staging"
    RESTORE_LOCK_FILE  = STATE_ROOT / ".restore_in_progress"
    # Path on the snapshotable LV that holds the backup archives + schedule.
    BACKUPS_ROOT       = Path("/var/backups/asguard")

    # Previous (on-LV) locations — migrated automatically on first use.
    _LEGACY_META_DIR    = Path("/var/backups/asguard/lvm_snapshots_meta")
    _LEGACY_CONFIG_FILE = Path("/var/backups/asguard/lvm_snapshot_config.json")
    _LEGACY_JOBS_DIR    = Path("/var/backups/asguard/snapshot_jobs")

    DEFAULT_CONFIG = {
        "auto_before_full_backup": True,
        "max_snapshots": 3,
        "snap_size_gb": 4,
    }

    # ── State directory bootstrap (off-LV) ────────────────────────────────────
    _state_migrated = False

    @classmethod
    def _ensure_state_dirs(cls) -> None:
        """Make sure STATE_ROOT exists. On first call, also migrate any pre-
        existing files from the legacy on-LV locations so we don't lose the
        history of past snapshots/jobs."""
        if cls._state_migrated and cls.STATE_ROOT.exists():
            return
        try:
            cls.STATE_ROOT.mkdir(parents=True, exist_ok=True)
            cls.JOBS_DIR.mkdir(parents=True, exist_ok=True)
            cls.META_DIR.mkdir(parents=True, exist_ok=True)
        except Exception:
            return

        # One-shot copy of legacy state into the new location. We copy rather
        # than move so that if someone reverts the code, nothing is lost.
        legacy = [
            (cls._LEGACY_JOBS_DIR, cls.JOBS_DIR),
            (cls._LEGACY_META_DIR, cls.META_DIR),
        ]
        for src, dst in legacy:
            try:
                if src.exists() and src.is_dir():
                    for f in src.iterdir():
                        if f.is_file() and not (dst / f.name).exists():
                            (dst / f.name).write_bytes(f.read_bytes())
            except Exception:
                pass
        try:
            if cls._LEGACY_CONFIG_FILE.exists() and not cls.CONFIG_FILE.exists():
                cls.CONFIG_FILE.write_bytes(cls._LEGACY_CONFIG_FILE.read_bytes())
        except Exception:
            pass
        cls._state_migrated = True

    # ── Shell helpers ──────────────────────────────────────────────────────────

    # LVM/mount/service commands that require root when invoked from the
    # uvicorn user — prepend sudo. systemctl + docker are here because the
    # restore_snapshot quiesce path stops services and the Postgres container.
    _SUDO_CMDS = {"vgs", "lvs", "lvcreate", "lvremove", "lvconvert", "lvchange",
                  "mount", "umount", "systemctl", "docker"}

    @classmethod
    def _run(cls, *cmd, timeout: int = 60) -> tuple[bool, str, str]:
        import os
        cls._ensure_state_dirs()  # cheap, idempotent
        args = list(cmd)
        binary = Path(args[0]).name
        if binary in cls._SUDO_CMDS and os.geteuid() != 0:
            args = ["sudo", "-n"] + args
        try:
            r = subprocess.run(
                args,
                capture_output=True, text=True,
                encoding="utf-8", errors="replace",
                timeout=timeout,
            )
            return r.returncode == 0, r.stdout.strip(), r.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, "", "Timeout"
        except Exception as e:
            return False, "", str(e)

    # ── System / LVM info ──────────────────────────────────────────────────────

    @classmethod
    def get_lvm_info(cls) -> dict:
        vg_info = {}
        ok, out, _ = cls._run(
            "vgs", "--noheadings", "--units", "g",
            "-o", "vg_name,vg_size,vg_free,lv_count",
            "--separator", "|", cls.VG_NAME,
        )
        if ok and out:
            p = [x.strip() for x in out.split("|")]
            if len(p) >= 4:
                vg_info = {"vg_name": p[0], "vg_size": p[1], "vg_free": p[2], "lv_count": p[3]}

        lv_info = {}
        ok2, out2, _ = cls._run(
            "lvs", "--noheadings", "--units", "g",
            "-o", "lv_name,lv_size,lv_attr",
            "--separator", "|",
            f"/dev/{cls.VG_NAME}/{cls.LV_NAME}",
        )
        if ok2 and out2:
            p = [x.strip() for x in out2.split("|")]
            if len(p) >= 3:
                lv_info = {"lv_name": p[0], "lv_size": p[1], "lv_attr": p[2]}

        mounted = False
        try:
            mounted = any(
                cls.MOUNT_POINT.as_posix() in line
                for line in Path("/proc/mounts").read_text().splitlines()
            )
        except Exception:
            pass

        disk_usage = {}
        if mounted:
            ok3, out3, _ = cls._run("df", "-h", str(cls.MOUNT_POINT))
            if ok3 and out3:
                lines = out3.strip().splitlines()
                if len(lines) >= 2:
                    p = lines[1].split()
                    if len(p) >= 5:
                        disk_usage = {
                            "total": p[1], "used": p[2],
                            "available": p[3], "use_percent": p[4],
                        }

        hostname = "Asguard"
        try:
            hostname = subprocess.check_output(["hostname"], text=True).strip()
        except Exception:
            pass

        os_name = "Linux"
        try:
            oi: dict[str, str] = {}
            with open("/etc/os-release") as f:
                for line in f:
                    k, _, v = line.strip().partition("=")
                    oi[k] = v.strip('"')
            os_name = oi.get("PRETTY_NAME", oi.get("NAME", os_name))
        except Exception:
            pass

        ram_gb = 0.0
        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        ram_gb = round(int(line.split()[1]) / 1024 / 1024, 1)
                        break
        except Exception:
            pass

        vcpus = 1
        try:
            vcpus = int(subprocess.check_output(["nproc"], text=True).strip())
        except Exception:
            pass

        snap_count = len(cls.list_snapshots())

        # Coverage info: what's actually protected by the snapshot
        coverage = {"level": "unknown", "coverage_pct": 0, "migrated": 0, "applicable": 0}
        try:
            from .lvm_migration_service import LVMMigrationService
            summary = LVMMigrationService.get_global_status()["summary"]
            coverage = {
                "level":        summary["level"],          # none | partial | full
                "coverage_pct": summary["coverage_pct"],
                "migrated":     summary["migrated"],
                "applicable":   summary["applicable"],
                "inconsistent": summary["inconsistent"],
            }
        except Exception as e:
            logger.debug("coverage lookup skipped: %s", e)

        return {
            "name": hostname,
            "os": os_name,
            "ram_gb": ram_gb,
            "vcpus": vcpus,
            "lvm_available": ok,
            "vg": vg_info,
            "lv": lv_info,
            "mount_point": str(cls.MOUNT_POINT),
            "mounted": mounted,
            "disk_usage": disk_usage,
            "snap_count": snap_count,
            "snapshot_estimated_seconds": cls.estimated_snapshot_seconds(),
            "coverage": coverage,
        }

    @classmethod
    def test_connection(cls) -> dict:
        ok, _, err = cls._run("vgs", "--noheadings", cls.VG_NAME)
        if not ok:
            return {"connected": False, "error": f"VG '{cls.VG_NAME}' introuvable: {err}"}
        ok2, _, err2 = cls._run("lvs", "--noheadings", f"/dev/{cls.VG_NAME}/{cls.LV_NAME}")
        if not ok2:
            return {"connected": True, "lv_ok": False, "error": f"LV '{cls.LV_NAME}' introuvable: {err2}"}
        snap_count = len(cls.list_snapshots())
        return {"connected": True, "lv_ok": True, "snapshot_count": snap_count}

    # ── Config ─────────────────────────────────────────────────────────────────

    @classmethod
    def read_config(cls) -> dict:
        if not cls.CONFIG_FILE.exists():
            return dict(cls.DEFAULT_CONFIG)
        try:
            return json.loads(cls.CONFIG_FILE.read_text())
        except Exception:
            return dict(cls.DEFAULT_CONFIG)

    @classmethod
    def write_config(cls, cfg: dict):
        cls.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = cls.CONFIG_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
        tmp.replace(cls.CONFIG_FILE)

    # ── Metadata ───────────────────────────────────────────────────────────────

    @classmethod
    def _meta_path(cls, snap_name: str) -> Path:
        cls.META_DIR.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", snap_name).strip("._") or "snapshot"
        return cls.META_DIR / f"{safe}.json"

    @classmethod
    def _save_meta(cls, snap_name: str, description: str = "",
                   created_by: str = "manual", extra: dict | None = None):
        meta = {
            "name": snap_name,
            "description": description or "Snapshot LVM",
            "created_at": datetime.now(LOCAL_TZ).isoformat(),
            "created_by": created_by,
        }
        if extra:
            meta.update(extra)
        cls._meta_path(snap_name).write_text(json.dumps(meta, indent=2, ensure_ascii=False))

    @classmethod
    def _load_meta(cls, snap_name: str) -> dict:
        p = cls._meta_path(snap_name)
        if p.exists():
            try:
                return json.loads(p.read_text())
            except Exception:
                pass
        return {"name": snap_name, "description": "—", "created_at": "", "created_by": "manual"}

    @classmethod
    def _delete_meta(cls, snap_name: str):
        p = cls._meta_path(snap_name)
        if p.exists():
            p.unlink(missing_ok=True)

    # ── Jobs ───────────────────────────────────────────────────────────────────

    @classmethod
    def _write_job(cls, job_file: Path, payload: dict):
        job_file.parent.mkdir(parents=True, exist_ok=True)
        tmp = job_file.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        tmp.replace(job_file)

    @classmethod
    def read_job(cls, job_id: str) -> dict | None:
        job_file = cls.JOBS_DIR / f"{job_id}.json"
        if not job_file.exists():
            return None
        try:
            return json.loads(job_file.read_text())
        except Exception:
            return None

    # Maximum age of a "running" job before we consider it a ghost (process
    # killed mid-write, file frozen by a snapshot/restore, etc.) and ignore it.
    # Both create (~8s) and restore (~30s) finish well within 10 minutes.
    _RUNNING_JOB_MAX_AGE_SECONDS = 10 * 60

    @classmethod
    def list_running_jobs(cls) -> list[dict]:
        cls._ensure_state_dirs()
        running: list[dict] = []
        now_ts = time.time()
        try:
            all_jobs = sorted(
                list(cls.JOBS_DIR.glob("snap_job_*.json")) +
                list(cls.JOBS_DIR.glob("snap_restore_*.json")),
                reverse=True,
            )
            for path in all_jobs:
                try:
                    data = json.loads(path.read_text())
                    if data.get("status") != "running":
                        continue
                    # Ghost protection: a job that has been "running" for
                    # longer than the operation could ever take is dead state
                    # — most often a job file frozen by a snapshot taken
                    # mid-write. Don't surface it to the UI.
                    started = data.get("started_at") or ""
                    try:
                        dt = datetime.fromisoformat(started)
                        age = now_ts - dt.timestamp()
                    except Exception:
                        # No usable timestamp → fall back to file mtime.
                        age = now_ts - path.stat().st_mtime
                    if age > cls._RUNNING_JOB_MAX_AGE_SECONDS:
                        continue
                    running.append(data)
                except Exception:
                    pass
        except Exception:
            pass
        return running

    @classmethod
    def get_last_restore(cls, max_age_minutes: int = 10) -> dict | None:
        try:
            files = sorted(cls.JOBS_DIR.glob("snap_restore_*.json"), reverse=True)
            if not files:
                return None
            data = json.loads(files[0].read_text())
            started_str = data.get("started_at", "")
            if started_str:
                age = time.time() - datetime.fromisoformat(started_str).timestamp()
                if age < max_age_minutes * 60:
                    return data
        except Exception:
            pass
        return None

    # ── List snapshots ─────────────────────────────────────────────────────────

    @classmethod
    def list_snapshots(cls, use_cache: bool = False) -> list[dict]:
        ok, out, _ = cls._run(
            "lvs", "--noheadings", "--units", "g",
            "-o", "lv_name,lv_size,lv_attr,origin,data_percent",
            "--separator", "|", cls.VG_NAME,
        )
        if not ok:
            return []

        results = []
        for line in out.splitlines():
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 4:
                continue
            lv_name, lv_size, lv_attr, origin = parts[0], parts[1], parts[2], parts[3]
            data_pct = parts[4] if len(parts) > 4 else "0"

            if origin != cls.LV_NAME:
                continue

            meta = cls._load_meta(lv_name)
            results.append({
                "snap_id":        lv_name,
                "size":           lv_size,
                "attr":           lv_attr,
                "data_percent":   data_pct,
                "description":    meta.get("description", "—"),
                "created_at":     meta.get("created_at", ""),
                "created_by":     meta.get("created_by", "manual"),
                "duration_seconds": meta.get("duration_seconds", 0),
            })

        results.sort(key=lambda x: x.get("created_at") or "", reverse=True)
        return results

    # ── Create ─────────────────────────────────────────────────────────────────

    @classmethod
    def _get_vg_free_gb(cls) -> float:
        """Return the VG free space in GB. 0.0 if vgs fails."""
        ok, out, _ = cls._run(
            "vgs", "--noheadings", "--units", "g", "--nosuffix",
            "-o", "vg_free", cls.VG_NAME,
        )
        if not ok or not out:
            return 0.0
        try:
            return float(out.strip())
        except ValueError:
            return 0.0

    @classmethod
    def _list_existing_for_cleanup(cls) -> list[dict]:
        """Build a list of existing snapshots the operator could delete to
        free space. Sorted oldest-first so the UI naturally suggests the
        oldest one for cleanup."""
        snaps = cls.list_snapshots()
        return sorted(
            [{
                "snap_id":      s.get("name") or s.get("snap_id"),
                "description":  s.get("description") or "",
                "size_gb":      s.get("size_gb") or s.get("lv_size") or 0,
                "created_at":   s.get("created_at") or "",
                "created_by":   s.get("created_by") or "manual",
            } for s in (snaps or [])],
            key=lambda s: s["created_at"] or "",
        )

    @classmethod
    def create_snapshot(cls, description: str = "",
                        snap_name: str | None = None,
                        job_id: str | None = None) -> dict:
        if not snap_name:
            ts = datetime.now(LOCAL_TZ).strftime("%Y%m%d_%H%M%S")
            snap_name = f"asguard_snap_{ts}"

        cfg = cls.read_config()
        snap_size_gb = float(cfg.get("snap_size_gb", 4))
        snap_size = f"{snap_size_gb:g}G"

        # ── Phase: pre-flight space check ──────────────────────────────
        # lvcreate's native error ("insufficient free space (255 extents):
        # 1024 required") is incomprehensible to a non-LVM user. We catch
        # the condition upfront and return a structured payload the UI can
        # turn into an actionable "delete X to free Y GB" dialog.
        vg_free_gb = cls._get_vg_free_gb()
        if vg_free_gb < snap_size_gb:
            # Round to one decimal for display; never claim more free than
            # what's actually there.
            return {
                "status":       "error",
                "error_type":   "insufficient_space",
                "snap_id":      None,
                "phase":        "validating",
                "phase_label":  "Vérification d'espace",
                "error": (
                    f"Espace insuffisant dans le groupe de volumes "
                    f"« {cls.VG_NAME} » : il reste {vg_free_gb:.1f} Go libres, "
                    f"mais le snapshot nécessite {snap_size_gb:.0f} Go. "
                    f"Supprimez un snapshot existant ou réduisez la taille "
                    f"dans Réglages."
                ),
                "vg_name":           cls.VG_NAME,
                "vg_free_gb":        round(vg_free_gb, 2),
                "required_gb":       snap_size_gb,
                "shortfall_gb":      round(snap_size_gb - vg_free_gb, 2),
                "existing_snapshots": cls._list_existing_for_cleanup(),
                "suggested_action":  "delete_oldest_snapshot",
            }

        cls._save_meta(snap_name, description or "Snapshot LVM", created_by="manual")

        started = time.time()
        ok, out, err = cls._run(
            "lvcreate", "-L", snap_size, "-s",
            "-n", snap_name,
            f"/dev/{cls.VG_NAME}/{cls.LV_NAME}",
            timeout=120,
        )
        duration = round(time.time() - started, 2)

        if not ok:
            cls._delete_meta(snap_name)
            # Race: another op grabbed the space between our pre-check and
            # lvcreate. Translate to the same actionable payload.
            err_lower = (err or "").lower()
            if "insufficient" in err_lower or "free space" in err_lower:
                return {
                    "status":            "error",
                    "error_type":        "insufficient_space",
                    "snap_id":           None,
                    "phase":             "lvcreate",
                    "phase_label":       "Capture LVM",
                    "error": (
                        f"Espace insuffisant pour le snapshot. "
                        f"Supprimez un snapshot existant ou réduisez la taille."
                    ),
                    "vg_name":            cls.VG_NAME,
                    "required_gb":        snap_size_gb,
                    "existing_snapshots": cls._list_existing_for_cleanup(),
                    "suggested_action":   "delete_oldest_snapshot",
                }
            return {
                "status":      "error",
                "error_type":  "lvcreate_failed",
                "snap_id":     None,
                "phase":       "lvcreate",
                "phase_label": "Capture LVM",
                "error":       err or "lvcreate échoué",
            }

        cls._save_meta(snap_name, description or "Snapshot LVM",
                       created_by="manual", extra={"duration_seconds": duration})
        cls._apply_retention()

        return {
            "status": "success",
            "snap_id": snap_name,
            "message": f"Snapshot LVM '{snap_name}' créé avec succès.",
            "duration_seconds": duration,
        }

    # ── Restore ────────────────────────────────────────────────────────────────

    # fstab marker used by LVMMigrationService for its bind-mounts. We read
    # these back so a snapshot restore can tear them down before the merge
    # and re-establish them afterwards — otherwise /etc/openvpn, /etc/nftables.conf
    # etc. would be left dangling until the next reboot.
    _MIGRATION_FSTAB_MARKER = "# asguard-lvm-migration"
    # Off-LV manifest written by LVMMigrationService — tells us which services
    # and Docker containers hold files on the snapshotable volume and therefore
    # must be quiesced before the merge.
    _MIGRATION_MANIFEST = Path("/var/lib/asguard-lvm-manifest.json")

    @classmethod
    def _read_migration_binds(cls) -> list[tuple[str, str]]:
        """Return [(lv_source, etc_target), ...] for every asguard bind-mount
        declared in /etc/fstab. Ordered as in fstab."""
        binds: list[tuple[str, str]] = []
        try:
            for line in Path("/etc/fstab").read_text().splitlines():
                if cls._MIGRATION_FSTAB_MARKER not in line:
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    binds.append((parts[0], parts[1]))
        except Exception:
            pass
        return binds

    # Business tables we surface to the operator as a "what was reverted"
    # diff after a snapshot restore. We query the live PostgreSQL container
    # both before and after the merge, then compute (before - after) so the
    # user can see e.g. "12 → 5 firewall rules (-7 lignes restaurées)".
    # Labels are user-facing; keep them short and in French.
    _DB_DIFF_TABLES: list[tuple[str, str, str]] = [
        # (table_name, user_label, group)
        ("rule",                 "Règles firewall",       "Pare-feu"),
        ("nat_dnat",             "NAT DNAT",              "NAT"),
        ("nat_snat",             "NAT SNAT",              "NAT"),
        ("nat_one_to_one",       "NAT 1-to-1",            "NAT"),
        ("ids_ips_rules",        "Règles IDS/IPS",        "IDS/IPS"),
        ("rules_waf",            "Règles WAF",            "WAF"),
        ("application_waf",      "Applications WAF",      "WAF"),
        ("sdwan_rules",          "Règles SD-WAN",         "SD-WAN"),
        ("proxy_rules",          "Règles proxy",          "Proxy"),
        ("routing",              "Routes statiques",      "Réseau"),
        ("gateway",              "Passerelles",           "Réseau"),
        ("interface",            "Interfaces",            "Réseau"),
        ("certificate",          "Certificats",           "PKI"),
        ("certificate_authority","Autorités de certif.",  "PKI"),
        ("client_openvpn",       "Clients OpenVPN",       "VPN"),
        ("server",               "Serveurs",              "VPN"),
        ("server_dhcp4",         "Plages DHCPv4",         "DHCP"),
        ("vlan",                 "VLAN",                  "Réseau"),
        ("vxlan",                "VXLAN",                 "Réseau"),
        ("ad_server",            "Serveurs LDAP/AD",      "Identité"),
        ("identities",           "Identités ZTNA",        "ZTNA"),
        ("relaypolicy",          "Politiques ZTNA",       "ZTNA"),
    ]

    @classmethod
    def _capture_db_summary(cls) -> dict:
        """
        Return `{table_name: count}` for every business table we track that
        actually exists in the live PostgreSQL container. Tables that don't
        exist are silently skipped (Postgres parses each subquery even with
        `to_regclass` guards, so we do existence detection in a first round
        trip and only count the survivors in a second one).

        Used by restore_snapshot() to build a "what was reverted" diff that
        proves the database actually rolled back. Failures here are not fatal:
        the restore still proceeds, the UI just doesn't show the diff.
        """
        wanted = [t for t, _, _ in cls._DB_DIFF_TABLES]
        if not wanted:
            return {}

        # Step 1: figure out which of our target tables exist in 'public'.
        in_list = ",".join(f"'{t}'" for t in wanted)
        detect_sql = (
            f"SELECT tablename FROM pg_tables "
            f"WHERE schemaname='public' AND tablename IN ({in_list});"
        )
        ok, out, _ = cls._run(
            "docker", "exec", "app-db-container",
            "psql", "-U", "postgres", "-d", "postgres", "-At", "-F", "|",
            "-c", detect_sql,
            timeout=15,
        )
        if not ok or not out:
            return {}
        existing = [t.strip() for t in out.splitlines() if t.strip()]
        if not existing:
            return {}

        # Step 2: a single UNION ALL counting only the tables that exist.
        union = "\nUNION ALL\n".join(
            f"SELECT '{t}'::text AS t, count(*)::bigint AS c FROM \"{t}\""
            for t in existing
        )
        ok2, out2, _ = cls._run(
            "docker", "exec", "app-db-container",
            "psql", "-U", "postgres", "-d", "postgres", "-At", "-F", "|",
            "-c", f"SELECT t, c FROM ({union}) s;",
            timeout=20,
        )
        if not ok2 or not out2:
            return {}
        result: dict = {}
        for line in out2.splitlines():
            line = line.strip()
            if not line or "|" not in line:
                continue
            name, _, count = line.partition("|")
            try:
                result[name.strip()] = int(count.strip())
            except (ValueError, TypeError):
                continue
        return result

    @classmethod
    def _build_db_diff(cls, before: dict, after: dict) -> list[dict]:
        """
        Turn two count snapshots into a UI-ready diff. Each entry:
            {table, label, group, before, after, delta, changed}
        where `delta = before - after` (positive = rows removed by the restore).
        Only tables that EXIST in either snapshot are returned. Tables with no
        change are still included so the UI can show "intact" rows if it wants.
        """
        diff: list[dict] = []
        for table, label, group in cls._DB_DIFF_TABLES:
            if table not in before and table not in after:
                continue
            b = before.get(table, 0)
            a = after.get(table, 0)
            diff.append({
                "table":   table,
                "label":   label,
                "group":   group,
                "before":  b,
                "after":   a,
                "delta":   b - a,
                "changed": b != a,
            })
        return diff

    @classmethod
    def _read_migration_manifest(cls) -> list[dict]:
        """Migrated items with their service/container, read from the off-LV
        manifest. Empty list if no migration has been applied."""
        try:
            if cls._MIGRATION_MANIFEST.exists():
                data = json.loads(cls._MIGRATION_MANIFEST.read_text(encoding="utf-8"))
                return data.get("items", [])
        except Exception:
            pass
        return []

    # ── Backup preservation across a merge ──────────────────────────────────
    # /var/backups/asguard is bind-mounted onto the snapshotable LV, so a merge
    # rolls it back to the snapshot's point-in-time — erasing every backup (and
    # the schedule) created afterwards. We stage those off-LV before the merge
    # and put them back after, so the backup LIST survives the restore while the
    # system/config still reverts to the checkpoint.
    @staticmethod
    def _is_preserved(item: Path) -> bool:
        n = item.name
        # Transient job-progress dirs are not backups — let them revert.
        if n in ("backup_jobs", "restore_jobs"):
            return False
        return (
            n.startswith("backup_")        # backup_, backup_safe_, backup_custom_
            or n.startswith("asguard_db_") # raw pg_dump files
            or n in ("restored_logs", "schedule_config.json")
        )

    @classmethod
    def _stage_preserved_backups(cls) -> list[str]:
        """Copy backups + schedule off the LV BEFORE the merge. Best-effort:
        never raises — returns a list of non-fatal errors."""
        import shutil
        errors: list[str] = []
        staging = cls.STAGING_DIR
        try:
            if staging.exists():
                shutil.rmtree(staging, ignore_errors=True)
            staging.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            return [f"init staging: {exc}"]
        if not cls.BACKUPS_ROOT.exists():
            return errors
        for item in cls.BACKUPS_ROOT.iterdir():
            if not cls._is_preserved(item):
                continue
            dest = staging / item.name
            try:
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)
            except Exception as exc:
                errors.append(f"stage {item.name}: {exc}")
        return errors

    @classmethod
    def _restore_preserved_backups(cls) -> list[str]:
        """After the merge + remount, put staged items back. Backup archives are
        ADDED only when missing (identical otherwise); schedule_config.json is
        OVERWRITTEN with the pre-restore version so the schedule is not reverted
        and the scheduler doesn't see stale slots as 'missed'. Best-effort."""
        import shutil
        errors: list[str] = []
        staging = cls.STAGING_DIR
        if not staging.exists():
            return errors
        try:
            cls.BACKUPS_ROOT.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        for item in staging.iterdir():
            dest = cls.BACKUPS_ROOT / item.name
            try:
                if item.name == "schedule_config.json":
                    shutil.copy2(item, dest)          # keep CURRENT schedule
                elif item.is_dir():
                    if not dest.exists():
                        shutil.copytree(item, dest)
                    else:
                        for child in item.iterdir():   # merge missing children
                            cdest = dest / child.name
                            if cdest.exists():
                                continue
                            if child.is_dir():
                                shutil.copytree(child, cdest)
                            else:
                                shutil.copy2(child, cdest)
                elif not dest.exists():
                    shutil.copy2(item, dest)
            except Exception as exc:
                errors.append(f"restore {item.name}: {exc}")
        try:
            shutil.rmtree(staging, ignore_errors=True)
        except Exception:
            pass
        return errors

    @classmethod
    def _set_restore_lock(cls, on: bool) -> None:
        """Off-LV marker the scheduler honors to suppress the missed-run catchup
        during a merge (the on-LV `.in_restore` lock is reverted by the merge)."""
        try:
            cls._ensure_state_dirs()
            if on:
                cls.RESTORE_LOCK_FILE.write_text(datetime.now(LOCAL_TZ).isoformat())
            elif cls.RESTORE_LOCK_FILE.exists():
                cls.RESTORE_LOCK_FILE.unlink()
        except Exception:
            pass

    @classmethod
    def restore_snapshot(cls, snap_id: str) -> dict:
        """
        Merge a snapshot back to the origin LV — safely, even when the LVM
        migration has placed Asguard's configs *and the PostgreSQL data dir*
        on the snapshotable volume.

        Sequence:
          1. Stop every service / Docker container that holds files on the LV
             (PostgreSQL especially — merging the LV under a live DB corrupts it).
          2. Release the asguard bind-mounts (they sit on top of /var/asguard_data).
          3. Unmount the LV → lvconvert --merge → deactivate/reactivate → remount.
          4. Re-establish the bind-mounts.
          5. Restart the services / containers.
        """
        snap_path   = f"/dev/{cls.VG_NAME}/{snap_id}"
        origin_path = f"/dev/{cls.VG_NAME}/{cls.LV_NAME}"

        # Suppress the scheduler's missed-run catchup for the whole restore
        # window (off-LV marker — the on-LV `.in_restore` lock is reverted by
        # the merge itself, so it cannot cover this). Cleared before every
        # return below; also auto-expires on the scheduler side if we crash.
        cls._set_restore_lock(True)

        binds    = cls._read_migration_binds()
        manifest = cls._read_migration_manifest()
        services   = [m["service"]   for m in manifest if m.get("service")]
        containers = [m["container"] for m in manifest if m.get("container")]

        rebound: list[str] = []
        quiesce_errors: list[str] = []
        stage_errors: list[str] = []
        restore_preserve_errors: list[str] = []

        # 0. Capture snapshot metadata BEFORE the merge consumes everything.
        # We use this to recreate an identical snapshot at the end so the
        # operator does not lose their restore point (LVM merge is destructive
        # to the snapshot itself).
        original_meta = cls._load_meta(snap_id) or {}
        preserved_description = (original_meta.get("description") or "Snapshot LVM").strip()
        preserved_created_by  = original_meta.get("created_by") or "manual"
        preserved_original_at = original_meta.get("created_at") or ""

        # 0bis. Snapshot the current database row counts so we can prove —
        # after the restore — what was actually reverted. Must run before
        # the postgres container is stopped in step 1.
        db_before = cls._capture_db_summary()

        # 1. Quiesce — stop services then containers that hold the LV open.
        for svc in services:
            cls._run("systemctl", "stop", svc, timeout=60)
        for ctr in containers:
            cls._run("docker", "stop", "-t", "30", ctr, timeout=60)

        # 1bis. Stage the backup archives + schedule OFF the LV while it is still
        # mounted, so the merge below doesn't erase backups taken after the
        # snapshot (/var/backups/asguard is bind-mounted on the LV). Best-effort:
        # a staging failure is reported but never aborts the restore.
        stage_errors = cls._stage_preserved_backups()

        # 2. Release bind-mounts (reverse order) so the LV can be unmounted.
        for _src, target in reversed(binds):
            cls._run("umount", target, timeout=30)

        # 3. Unmount the LV itself.
        cls._run("umount", str(cls.MOUNT_POINT), timeout=30)

        # 4. Mark for merge
        ok, out, err = cls._run("lvconvert", "--merge", snap_path, timeout=180)
        if not ok:
            # Best-effort restore of the previous layout + services before bailing.
            cls._run("mount", origin_path, str(cls.MOUNT_POINT), timeout=30)
            for src, target in binds:
                cls._run("mount", "--bind", src, target, timeout=30)
            for ctr in containers:
                cls._run("docker", "start", ctr, timeout=60)
            for svc in services:
                cls._run("systemctl", "start", svc, timeout=30)
            # Merge never happened, so the LV (and its backups) is untouched —
            # just drop the staging copy and release the scheduler lock.
            cls._restore_preserved_backups()
            cls._set_restore_lock(False)
            return {"status": "error", "error": err or "lvconvert --merge échoué"}

        # 5. Deactivate → reactivate (triggers immediate merge for non-root LVs)
        cls._run("lvchange", "-an", f"/dev/{cls.VG_NAME}/{cls.LV_NAME}", timeout=30)
        cls._run("lvchange", "-ay", f"/dev/{cls.VG_NAME}/{cls.LV_NAME}", timeout=30)

        # 6. Remount the LV
        cls.MOUNT_POINT.mkdir(parents=True, exist_ok=True)
        ok_mnt, _, err_mnt = cls._run("mount", origin_path, str(cls.MOUNT_POINT), timeout=30)

        # 7. Re-establish the asguard bind-mounts on top of the reverted LV.
        bind_errors: list[str] = []
        if ok_mnt:
            for src, target in binds:
                try:
                    Path(target).mkdir(parents=True, exist_ok=True)
                except Exception:
                    # /etc/nftables.conf is a file mountpoint — touch it.
                    try:
                        Path(target).parent.mkdir(parents=True, exist_ok=True)
                        Path(target).touch(exist_ok=True)
                    except Exception:
                        pass
                bok, _, berr = cls._run("mount", "--bind", src, target, timeout=30)
                if bok:
                    rebound.append(target)
                else:
                    bind_errors.append(f"{target}: {berr}")

        # 7bis. Put the staged backups + current schedule back onto the now-
        # reverted LV so the FULL backup list survives the restore (only the
        # system/config reverts to the checkpoint). Must run after the bind in
        # step 7 so /var/backups/asguard points at the LV again.
        if ok_mnt:
            restore_preserve_errors = cls._restore_preserved_backups()

        # 8. Restart services then containers (containers last — Postgres needs
        #    its data dir bind-mount back in place first).
        for svc in services:
            sok, _, serr = cls._run("systemctl", "start", svc, timeout=30)
            if not sok:
                quiesce_errors.append(f"service {svc}: {serr}")
        for ctr in containers:
            cok, _, cerr = cls._run("docker", "start", ctr, timeout=60)
            if not cok:
                quiesce_errors.append(f"container {ctr}: {cerr}")

        # 8bis. Snapshot the post-restore row counts. Postgres needs a couple
        # of seconds after `docker start` before it accepts connections, so we
        # retry a few times rather than racing the boot.
        db_after: dict = {}
        if db_before:
            for _ in range(8):
                db_after = cls._capture_db_summary()
                if db_after:
                    break
                time.sleep(1.5)
        db_changes = cls._build_db_diff(db_before, db_after) if db_before else []

        # 8ter. Full post-restore resync — realign EVERY firewall component
        # (rules, NAT, routing, daemons) with the rolled-back DB. The DB is
        # the single source of truth; the LVM rollback brought config files
        # back but kernel state and orphan rules need to be reconciled.
        # See backend/backup/post_restore_resync.py for the full pipeline.
        # Failure here is reported in `warning` but does not fail the restore.
        nft_rebuild: dict = {}
        try:
            from backend.backup.post_restore_resync import resync_all
            nft_rebuild = resync_all()
        except Exception as exc:
            nft_rebuild = {"status": "error", "error": str(exc)}

        cls._delete_meta(snap_id)

        # 9. **Snapshot persistence** — recreate the snapshot under the same
        #    name with the preserved metadata so the operator keeps their
        #    restore point. LVM merge is destructive to snapshots by design,
        #    but a freshly-taken snapshot of the just-reverted LV represents
        #    the exact same logical state and is functionally equivalent.
        recreated_snap = None
        recreate_error = None
        try:
            recreate_description = (
                f"{preserved_description} · Recréé après restauration "
                f"(état identique au snapshot original)"
            )
            recreate_extra = {
                "recreated_from_restore": True,
                "restored_at": datetime.now(LOCAL_TZ).isoformat(),
            }
            if preserved_original_at:
                recreate_extra["original_created_at"] = preserved_original_at

            new_snap = cls.create_snapshot(
                description=recreate_description,
                snap_name=snap_id,
            )
            if new_snap.get("status") == "success":
                # Augment the metadata with the "recreated" markers so the UI
                # can show a badge like "Point recréé après restauration".
                cls._save_meta(
                    snap_id,
                    recreate_description,
                    created_by=preserved_created_by,
                    extra=recreate_extra,
                )
                recreated_snap = snap_id
            else:
                recreate_error = (
                    new_snap.get("error")
                    or "création post-restore impossible"
                )
        except Exception as exc:
            recreate_error = str(exc)

        result = {
            "status": "success",
            "message": (
                f"Snapshot '{snap_id}' restauré. Système revenu à l'état du checkpoint."
                + (f" Point de restauration recréé sous le même nom." if recreated_snap
                   else " (Point de restauration non recréé — créez-en un nouveau.)")
            ),
            "snap_id": snap_id,
            "mounted": ok_mnt,
            "binds_restored": rebound,
            "services_restarted": services,
            "containers_restarted": containers,
            "snapshot_preserved": bool(recreated_snap),
            "recreated_snap_id": recreated_snap,
            "db_changes": db_changes,
            "db_changes_total_delta": sum(c["delta"] for c in db_changes),
            "db_changes_tables_touched": sum(1 for c in db_changes if c["changed"]),
            "nft_rebuild": nft_rebuild,
        }
        # Restore window is over — let the scheduler resume normal catchup.
        cls._set_restore_lock(False)

        problems = bind_errors + quiesce_errors + stage_errors + restore_preserve_errors
        if recreate_error:
            problems.append(f"recréation snapshot : {recreate_error}")
        if nft_rebuild.get("status") == "error":
            problems.append(f"resynchronisation nftables : {nft_rebuild.get('error', '?')}")
        elif nft_rebuild.get("total_errors", 0):
            problems.append(
                f"resynchronisation nftables : {nft_rebuild['total_errors']} "
                f"règle(s) en erreur"
            )
        if problems:
            result["warning"] = (
                f"{len(problems)} élément(s) à vérifier après restauration : "
                f"{'; '.join(problems)}. Un redémarrage corrige les montages."
            )
        return result

    # ── Delete ─────────────────────────────────────────────────────────────────

    @classmethod
    def delete_snapshot(cls, snap_id: str) -> dict:
        ok, _, err = cls._run("lvremove", "-f",
                               f"/dev/{cls.VG_NAME}/{snap_id}", timeout=60)
        if not ok:
            return {"status": "error", "error": err or "lvremove échoué"}
        cls._delete_meta(snap_id)
        return {"status": "success"}

    # ── Retention ──────────────────────────────────────────────────────────────

    @classmethod
    def _apply_retention(cls):
        cfg = cls.read_config()
        max_snap = int(cfg.get("max_snapshots", 3))
        snapshots = cls.list_snapshots()
        for snap in snapshots[max_snap:]:
            cls.delete_snapshot(snap["snap_id"])

    @classmethod
    def estimated_snapshot_seconds(cls) -> int:
        return 8  # LVM snapshots are nearly instant (CoW metadata only)


# Compatibility alias
SnapshotService = LVMSnapshotService
VMwareSnapshotService = LVMSnapshotService
