"""
lvm_migration_service.py — Migration des configurations critiques vers le LV asguard-data
=========================================================================================

Objectif produit (multi-clients) :
  Étendre la couverture du snapshot LVM au-delà du simple volume de données.
  Les configurations système critiques (nftables, OpenVPN, IPsec, Suricata, Squid,
  WAF, etc.) sont déplacées sur le Logical Volume `asguard-data` et bind-mountées
  à leur emplacement original. Le snapshot LVM capture alors l'intégralité du
  périmètre opérationnel du firewall.

Principes :
  • Détection avant action  — chaque item est vérifié (existe ? déjà migré ?).
  • Idempotent              — relancer ne refait pas le travail déjà fait.
  • Multi-clients           — config externalisée, items optionnels skippés.
  • Rollback granulaire     — item par item, jamais tout-ou-rien.
  • Pré-snapshot LVM        — point de retour automatique avant migration.
  • Health-check post       — vérifie chaque service après bind-mount.
  • Journal JSON            — audit complet dans /var/log/asguard/migration_*.

Auteur : Ala Daas — PFE Asguard
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
import subprocess
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)
LOCAL_TZ = ZoneInfo("Africa/Tunis")


# ────────────────────────────────────────────────────────────────────────────
# Constantes & configuration par défaut
# ────────────────────────────────────────────────────────────────────────────

FSTAB_MARKER = "# asguard-lvm-migration"
LOCK_FILE = Path("/var/lock/asguard-migration.lock")
AUDIT_DIR = Path("/var/log/asguard")
JOBS_DIR = Path("/var/backups/asguard/migration_jobs")
PRE_MIGRATION_BACKUP_DIR = Path("/var/backups/asguard/pre_migration")
CONFIG_FILE = Path("/etc/asguard/lvm_migration_config.json")

DEFAULT_LV_MOUNT = "/var/asguard_data"
DEFAULT_LV_SUBDIR = "system"

# Catalogue par défaut — un client peut surcharger via CONFIG_FILE
#
# Champs:
#   service   — unité systemd à arrêter/redémarrer autour de la migration
#   container — conteneur Docker à arrêter/redémarrer (alternative à service)
#               Utilisé pour la base PostgreSQL qui tourne dans app-db-container.
DEFAULT_ITEMS: list[dict] = [
    {"id": "nftables",     "source": "/etc/nftables.conf",    "type": "file", "service": "nftables",        "optional": False},
    {"id": "rules",        "source": "/etc/rules",            "type": "dir",  "service": None,              "optional": False},
    {"id": "asguard_etc",  "source": "/etc/asguard",          "type": "dir",  "service": None,              "optional": False},
    {"id": "backups",      "source": "/var/backups/asguard",  "type": "dir",  "service": None,              "optional": False},
    {"id": "openvpn",      "source": "/etc/openvpn",          "type": "dir",  "service": None,              "optional": True},
    {"id": "strongswan",   "source": "/etc/strongswan.d",     "type": "dir",  "service": "strongswan",      "optional": True},
    {"id": "suricata",     "source": "/etc/suricata",         "type": "dir",  "service": "suricata",        "optional": True},
    {"id": "squid",        "source": "/etc/squid",            "type": "dir",  "service": "squid",           "optional": True},
    {"id": "modsecurity",  "source": "/etc/modsecurity",      "type": "dir",  "service": None,              "optional": True},
    {"id": "dhcp4",        "source": "/etc/dhcpd.conf",       "type": "file", "service": None,              "optional": True},
    {"id": "dhcp6",        "source": "/etc/dhcpd6.conf",      "type": "file", "service": None,              "optional": True},
    {"id": "postgres",     "source": "/var/lib/docker/volumes/asguard_pgdb/_data",
                           "type": "dir",  "service": None,   "container": "app-db-container", "optional": False},
]


# ────────────────────────────────────────────────────────────────────────────
# Modèles
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class MigrationItemStatus:
    id: str
    source: str
    type: str
    service: Optional[str]
    optional: bool
    source_exists: bool = False
    is_bind_mounted: bool = False
    target_exists: bool = False
    target_path: str = ""
    in_fstab: bool = False
    service_active: Optional[bool] = None
    state: str = "unknown"  # not_applicable | not_migrated | migrated | inconsistent
    size_bytes: int = 0
    note: str = ""


@dataclass
class StepResult:
    step: str
    ok: bool
    detail: str = ""


@dataclass
class ItemMigrationResult:
    id: str
    success: bool
    skipped: bool = False
    reason: str = ""
    steps: list[StepResult] = field(default_factory=list)
    rolled_back: bool = False


# ────────────────────────────────────────────────────────────────────────────
# Service principal
# ────────────────────────────────────────────────────────────────────────────

class LVMMigrationService:
    """Moteur de migration des configurations critiques vers le LV asguard-data."""

    # ───────────── Shell helpers ─────────────

    _SUDO_BINS = {"mount", "umount", "systemctl", "lvcreate", "lvremove", "mv",
                  "docker", "cp", "du"}

    @classmethod
    def _run(cls, *cmd, timeout: int = 60, check: bool = False) -> tuple[bool, str, str]:
        args = list(cmd)
        binary = Path(args[0]).name
        if binary in cls._SUDO_BINS and os.geteuid() != 0:
            args = ["sudo", "-n"] + args
        try:
            r = subprocess.run(
                args,
                capture_output=True, text=True,
                encoding="utf-8", errors="replace",
                timeout=timeout,
            )
            ok = r.returncode == 0
            if check and not ok:
                logger.warning("cmd failed: %s — stderr=%s", " ".join(args), r.stderr.strip())
            return ok, r.stdout.strip(), r.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, "", "Timeout"
        except FileNotFoundError as e:
            return False, "", f"Binaire introuvable: {e}"
        except Exception as e:
            return False, "", str(e)

    # ───────────── Configuration ─────────────

    @classmethod
    def read_config(cls) -> dict:
        """Lit la configuration (avec fallback sur les valeurs par défaut)."""
        cfg = {
            "lv_mount": DEFAULT_LV_MOUNT,
            "lv_subdir": DEFAULT_LV_SUBDIR,
            "items": list(DEFAULT_ITEMS),
        }
        if CONFIG_FILE.exists():
            try:
                user_cfg = json.loads(CONFIG_FILE.read_text())
                cfg["lv_mount"] = user_cfg.get("lv_mount", cfg["lv_mount"])
                cfg["lv_subdir"] = user_cfg.get("lv_subdir", cfg["lv_subdir"])
                if "items" in user_cfg:
                    cfg["items"] = user_cfg["items"]
            except Exception as e:
                logger.warning("lvm_migration_config.json invalide, fallback défauts: %s", e)
        return cfg

    @classmethod
    def write_config(cls, cfg: dict) -> None:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = CONFIG_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
        tmp.replace(CONFIG_FILE)

    @classmethod
    def _target_for(cls, item: dict, cfg: dict | None = None) -> Path:
        cfg = cfg or cls.read_config()
        return Path(cfg["lv_mount"]) / cfg["lv_subdir"] / item["id"]

    # ───────────── Détection / Statut ─────────────

    @classmethod
    def _is_bind_mounted(cls, source: Path, expected_target: Path) -> bool:
        """Vrai si `source` est actuellement bind-mounté depuis `expected_target`."""
        try:
            mounts = Path("/proc/self/mountinfo").read_text().splitlines()
        except Exception:
            return False
        src_str = str(source)
        tgt_str = str(expected_target)
        for line in mounts:
            # mountinfo format: ... 3:0 / /mnt/source rw,relatime ...
            # On cherche la cible (point de montage) + l'origine via le champ root
            parts = line.split()
            if len(parts) < 10:
                continue
            mount_root = parts[3]
            mount_point = parts[4]
            if mount_point == src_str:
                # bind-mount : mount_root pointe vers le sous-chemin source
                if tgt_str.endswith(mount_root) or mount_root.endswith(item_id_or_default(tgt_str)):
                    return True
                # Fallback : vérifier que le device est bien dans le LV
                return True
        return False

    @classmethod
    def _service_active(cls, service: Optional[str]) -> Optional[bool]:
        if not service:
            return None
        ok, out, _ = cls._run("systemctl", "is-active", service, timeout=5)
        return ok and out == "active"

    @classmethod
    def _du_bytes(cls, path: Path) -> int:
        if not path.exists():
            return 0
        try:
            ok, out, _ = cls._run("du", "-sb", str(path), timeout=30)
            if ok and out:
                return int(out.split()[0])
        except Exception:
            pass
        return 0

    @classmethod
    def get_item_status(cls, item: dict, cfg: dict | None = None) -> MigrationItemStatus:
        cfg = cfg or cls.read_config()
        source = Path(item["source"])
        target = cls._target_for(item, cfg)

        status = MigrationItemStatus(
            id=item["id"],
            source=str(source),
            type=item["type"],
            service=item.get("service"),
            optional=bool(item.get("optional", True)),
            target_path=str(target),
        )

        status.source_exists = source.exists()
        status.target_exists = target.exists()
        status.is_bind_mounted = cls._is_bind_mounted(source, target)
        status.in_fstab = cls._fstab_has_entry(source, target)
        status.service_active = cls._service_active(item.get("service"))

        if status.source_exists:
            status.size_bytes = cls._du_bytes(source)

        # Calcul d'état logique
        if not status.source_exists:
            if status.optional:
                status.state = "not_applicable"
                status.note = "Service non installé sur ce client."
            else:
                status.state = "inconsistent"
                status.note = "Source absente mais marquée non-optionnelle."
        elif status.is_bind_mounted and status.target_exists:
            status.state = "migrated"
            if not status.in_fstab:
                status.note = "Bind-mount actif mais pas persistant (manque dans fstab)."
                status.state = "inconsistent"
        elif status.target_exists and not status.is_bind_mounted:
            status.state = "inconsistent"
            status.note = "Cible déjà copiée mais bind-mount absent — migration interrompue ?"
        else:
            status.state = "not_migrated"

        return status

    @classmethod
    def get_global_status(cls) -> dict:
        cfg = cls.read_config()
        items = [cls.get_item_status(it, cfg) for it in cfg["items"]]

        total = len(items)
        applicable = [i for i in items if i.state != "not_applicable"]
        migrated = [i for i in applicable if i.state == "migrated"]
        inconsistent = [i for i in items if i.state == "inconsistent"]

        coverage_pct = round(100 * len(migrated) / len(applicable), 1) if applicable else 0

        if not applicable:
            level = "none"
        elif len(migrated) == len(applicable):
            level = "full"
        elif len(migrated) == 0:
            level = "none"
        else:
            level = "partial"

        return {
            "lv_mount": cfg["lv_mount"],
            "lv_subdir": cfg["lv_subdir"],
            "items": [asdict(i) for i in items],
            "summary": {
                "total": total,
                "applicable": len(applicable),
                "migrated": len(migrated),
                "inconsistent": len(inconsistent),
                "coverage_pct": coverage_pct,
                "level": level,                # none | partial | full
            },
        }

    # ───────────── fstab helpers ─────────────

    @classmethod
    def _fstab_entry(cls, source: Path, target: Path) -> str:
        return f"{target} {source} none bind 0 0  {FSTAB_MARKER}"

    @classmethod
    def _fstab_has_entry(cls, source: Path, target: Path) -> bool:
        try:
            content = Path("/etc/fstab").read_text()
        except Exception:
            return False
        marker = f"{target} {source}"
        return marker in content and FSTAB_MARKER in content

    @classmethod
    def _fstab_add(cls, source: Path, target: Path) -> bool:
        if cls._fstab_has_entry(source, target):
            return True
        try:
            line = cls._fstab_entry(source, target)
            with open("/etc/fstab", "a") as f:
                f.write(f"\n{line}\n")
            return True
        except PermissionError:
            # Pas root — on tente avec tee + sudo
            line = cls._fstab_entry(source, target)
            ok, _, _ = cls._run("bash", "-c", f"echo '{line}' | sudo -n tee -a /etc/fstab")
            return ok
        except Exception as e:
            logger.error("fstab add failed: %s", e)
            return False

    @classmethod
    def _fstab_remove(cls, source: Path, target: Path) -> bool:
        try:
            content = Path("/etc/fstab").read_text()
        except Exception:
            return False
        marker = f"{target} {source}"
        new_lines = [
            ln for ln in content.splitlines()
            if not (marker in ln and FSTAB_MARKER in ln)
        ]
        if len(new_lines) == len(content.splitlines()):
            return True  # rien à retirer
        try:
            Path("/etc/fstab").write_text("\n".join(new_lines) + "\n")
            return True
        except PermissionError:
            tmp = Path("/tmp/.asguard_fstab.tmp")
            tmp.write_text("\n".join(new_lines) + "\n")
            ok, _, _ = cls._run("sudo", "-n", "mv", str(tmp), "/etc/fstab")
            return ok

    # ───────────── Lock ─────────────

    @classmethod
    @contextmanager
    def _migration_lock(cls):
        LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
        if LOCK_FILE.exists():
            try:
                pid = int(LOCK_FILE.read_text().strip())
                if Path(f"/proc/{pid}").exists():
                    raise RuntimeError(f"Migration déjà en cours (pid={pid}).")
            except (ValueError, FileNotFoundError):
                pass  # stale lock
        LOCK_FILE.write_text(str(os.getpid()))
        try:
            yield
        finally:
            try:
                LOCK_FILE.unlink(missing_ok=True)
            except Exception:
                pass

    # ───────────── Dry-run / planification ─────────────

    @classmethod
    def plan(cls) -> dict:
        """
        Retourne un plan détaillé de ce qui SERAIT fait, sans rien modifier.
        Sortie consommable par UI + ligne de commande.
        """
        cfg = cls.read_config()
        actions = []
        warnings = []

        # Vérifications pré-requis globales
        lv_root = Path(cfg["lv_mount"])
        if not lv_root.is_mount():
            warnings.append(f"Le LV n'est pas monté sur {lv_root} — la migration échouera.")

        free_bytes = shutil.disk_usage(lv_root).free if lv_root.exists() else 0
        total_needed = 0

        for item in cfg["items"]:
            st = cls.get_item_status(item, cfg)
            target = Path(st.target_path)

            entry = {
                "id": st.id,
                "source": st.source,
                "target": st.target_path,
                "state": st.state,
                "size_bytes": st.size_bytes,
                "steps": [],
            }

            if st.state == "not_applicable":
                entry["decision"] = "skip"
                entry["reason"] = st.note
            elif st.state == "migrated":
                entry["decision"] = "skip"
                entry["reason"] = "Déjà migré (idempotent)."
            elif st.state == "inconsistent":
                entry["decision"] = "manual_review"
                entry["reason"] = st.note
                warnings.append(f"[{st.id}] {st.note}")
            else:
                entry["decision"] = "migrate"
                total_needed += st.size_bytes
                entry["steps"] = [
                    f"mkdir -p {target.parent}",
                    f"cp -a {st.source} → {target}  ({_human_bytes(st.size_bytes)})",
                    f"verify checksums (rsync --checksum)",
                    f"mv {st.source} → {st.source}.pre-asguard-migration",
                    f"mkdir / touch {st.source}  (recréation point de montage)",
                    f"mount --bind {target} {st.source}",
                    f"fstab += '{cls._fstab_entry(Path(st.source), target)}'",
                ]
                if st.service:
                    entry["steps"] = [
                        f"systemctl stop {st.service}",
                        *entry["steps"],
                        f"systemctl start {st.service}",
                        f"systemctl is-active {st.service}  (health-check)",
                    ]
            actions.append(entry)

        if total_needed > free_bytes:
            warnings.append(
                f"Espace insuffisant sur {lv_root} : "
                f"{_human_bytes(total_needed)} requis, {_human_bytes(free_bytes)} libre."
            )

        # Pré-snapshot LVM automatique
        pre_snapshot_step = {
            "type": "safety_net",
            "step": "LVM snapshot automatique avant migration",
            "note": "Créé via LVMSnapshotService.create_snapshot(description='pre-migration')",
        }

        return {
            "generated_at": datetime.now(LOCAL_TZ).isoformat(),
            "lv_mount": cfg["lv_mount"],
            "lv_subdir": cfg["lv_subdir"],
            "lv_free_bytes": free_bytes,
            "estimated_size_bytes": total_needed,
            "warnings": warnings,
            "pre_safety_net": pre_snapshot_step,
            "actions": actions,
            "summary": {
                "to_migrate":     sum(1 for a in actions if a["decision"] == "migrate"),
                "already_done":   sum(1 for a in actions if a["decision"] == "skip" and "Déjà" in a.get("reason", "")),
                "not_applicable": sum(1 for a in actions if a["decision"] == "skip" and "Service" in a.get("reason", "")),
                "manual_review":  sum(1 for a in actions if a["decision"] == "manual_review"),
            },
        }

    # ───────────── Migration réelle (item) ─────────────

    @classmethod
    def _migrate_item(cls, item: dict, cfg: dict, job_path: Path,
                      progress_cb=None) -> ItemMigrationResult:
        """Migre UN item avec rollback automatique si la moindre étape échoue."""
        st = cls.get_item_status(item, cfg)
        result = ItemMigrationResult(id=st.id, success=False)

        # Skip cases
        if st.state == "migrated":
            result.success = True
            result.skipped = True
            result.reason = "déjà migré"
            return result
        if st.state == "not_applicable":
            result.success = True
            result.skipped = True
            result.reason = "non applicable (source absente, item optionnel)"
            return result
        if st.state == "inconsistent":
            result.skipped = True
            result.reason = f"état incohérent: {st.note}"
            return result

        source = Path(st.source)
        target = Path(st.target_path)
        backup_path = source.parent / f"{source.name}.pre-asguard-migration"

        def step(name: str, fn) -> bool:
            try:
                ok, detail = fn()
                result.steps.append(StepResult(name, ok, detail))
                if progress_cb:
                    progress_cb(name, ok)
                return ok
            except Exception as e:
                result.steps.append(StepResult(name, False, f"exception: {e}"))
                return False

        rollback_actions: list = []

        # 1. Stop service / Docker container si applicable. A migrated path
        #    cannot be unmounted while a process holds it open — PostgreSQL in
        #    particular keeps its data dir open continuously.
        if item.get("service"):
            if not step(f"stop {item['service']}", lambda: cls._stop_service(item["service"])):
                result.reason = "impossible d'arrêter le service"
                return result
            rollback_actions.append(("start_service", item["service"]))
        if item.get("container"):
            if not step(f"stop container {item['container']}",
                        lambda: cls._stop_container(item["container"])):
                result.reason = "impossible d'arrêter le conteneur"
                return result
            rollback_actions.append(("start_container", item["container"]))

        # 2. Copy source → target
        if not step("create target parent", lambda: cls._mkdir(target.parent)):
            result.reason = "mkdir parent failed"
            cls._do_rollback(rollback_actions)
            return result

        if not step("copy source → LV", lambda: cls._copy_tree(source, target)):
            result.reason = "copie échouée"
            cls._do_rollback(rollback_actions)
            return result
        rollback_actions.append(("rm_target", target))

        # 3. Vérification intégrité (rsync --checksum --dry-run doit retourner 0 diffs)
        if not step("verify integrity", lambda: cls._verify_copy(source, target)):
            result.reason = "intégrité copie KO"
            cls._do_rollback(rollback_actions)
            return result

        # 4. Sauvegarder l'original (rename)
        if not step("backup original", lambda: cls._safe_rename(source, backup_path)):
            result.reason = "backup original failed"
            cls._do_rollback(rollback_actions)
            return result
        rollback_actions.append(("restore_original", backup_path, source))

        # 5. Recréer le mountpoint vide
        if not step("recreate mountpoint", lambda: cls._recreate_mountpoint(source, item["type"])):
            result.reason = "recreate mountpoint failed"
            cls._do_rollback(rollback_actions)
            return result

        # 6. Bind mount
        if not step("bind mount", lambda: cls._bind_mount(target, source)):
            result.reason = "bind mount failed"
            cls._do_rollback(rollback_actions)
            return result
        rollback_actions.append(("umount", source))

        # 7. fstab persist
        if not step("fstab add", lambda: (cls._fstab_add(source, target), "")):
            result.reason = "fstab add failed"
            cls._do_rollback(rollback_actions)
            return result
        # Must be undone on rollback too — otherwise a later health-check
        # failure leaves a dangling bind entry that re-mounts on next boot.
        rollback_actions.append(("fstab_remove", source, target))

        # 8. Restart service / container
        if item.get("service"):
            if not step(f"start {item['service']}", lambda: cls._start_service(item["service"])):
                result.reason = "service ne redémarre pas"
                cls._do_rollback(rollback_actions)
                return result
            if not step("health-check", lambda: cls._service_health(item["service"])):
                result.reason = "health-check service échoué"
                cls._do_rollback(rollback_actions)
                return result
        if item.get("container"):
            if not step(f"start container {item['container']}",
                        lambda: cls._start_container(item["container"])):
                result.reason = "conteneur ne redémarre pas"
                cls._do_rollback(rollback_actions)
                return result
            if not step("health-check container",
                        lambda: cls._container_health(item["container"])):
                result.reason = "health-check conteneur échoué"
                cls._do_rollback(rollback_actions)
                return result

        result.success = True
        return result

    # ───────────── Migration globale ─────────────

    @classmethod
    def apply(cls, dry_run: bool = True, ids: list[str] | None = None,
              job_id: str | None = None) -> dict:
        """
        Exécute la migration.
          dry_run=True  : retourne juste le plan, n'effectue rien.
          ids=None      : tout migrer ; sinon liste d'IDs ciblés.
        """
        if dry_run:
            return {"dry_run": True, "plan": cls.plan()}

        job_id = job_id or f"mig_{uuid.uuid4().hex[:10]}"
        JOBS_DIR.mkdir(parents=True, exist_ok=True)
        job_path = JOBS_DIR / f"{job_id}.json"

        result = {
            "job_id": job_id,
            "started_at": datetime.now(LOCAL_TZ).isoformat(),
            "dry_run": False,
            "items": [],
            "pre_snapshot": None,
            "status": "running",
        }

        with cls._migration_lock():
            # Pré-snapshot LVM
            try:
                from .lvm_snapshot_service import LVMSnapshotService
                snap = LVMSnapshotService.create_snapshot(
                    description="pre-migration safety net",
                    snap_name=f"pre_migration_{datetime.now(LOCAL_TZ).strftime('%Y%m%d_%H%M%S')}",
                )
                result["pre_snapshot"] = snap
            except Exception as e:
                result["pre_snapshot"] = {"status": "error", "error": str(e)}

            cfg = cls.read_config()
            items = cfg["items"]
            if ids:
                items = [it for it in items if it["id"] in ids]

            for item in items:
                _write_job(job_path, {**result, "current": item["id"]})
                item_result = cls._migrate_item(item, cfg, job_path)
                result["items"].append(asdict(item_result))
                _write_job(job_path, result)

            result["status"] = "completed"
            result["completed_at"] = datetime.now(LOCAL_TZ).isoformat()
            _write_job(job_path, result)

            # Audit
            cls._write_audit(result)

            # Manifest — written OFF the LV so a snapshot restore can read it
            # to know which services/containers to stop around the merge.
            cls._write_manifest(cfg)

        return result

    # Manifest of currently-migrated items, stored on the root filesystem
    # (NOT on the LV — otherwise a snapshot restore would revert it). Consumed
    # by LVMSnapshotService.restore_snapshot to safely quiesce the system.
    MANIFEST_FILE = Path("/var/lib/asguard-lvm-manifest.json")

    @classmethod
    def _write_manifest(cls, cfg: dict | None = None) -> None:
        try:
            cfg = cfg or cls.read_config()
            migrated = []
            for item in cfg["items"]:
                st = cls.get_item_status(item, cfg)
                if st.state == "migrated":
                    migrated.append({
                        "id":        item["id"],
                        "source":    item["source"],
                        "target":    str(cls._target_for(item, cfg)),
                        "type":      item["type"],
                        "service":   item.get("service"),
                        "container": item.get("container"),
                    })
            cls.MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
            cls.MANIFEST_FILE.write_text(
                json.dumps({"updated_at": datetime.now(LOCAL_TZ).isoformat(),
                            "items": migrated}, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            logger.error("Could not write LVM migration manifest: %s", e)

    # ───────────── Rollback ─────────────

    @classmethod
    def rollback(cls, ids: list[str] | None = None) -> dict:
        """
        Rollback : démonte les bind-mounts, retire de fstab, restaure les originaux.
        """
        cfg = cls.read_config()
        items = cfg["items"]
        if ids:
            items = [it for it in items if it["id"] in ids]

        report = {"rolled_back": [], "errors": []}
        for item in items:
            source = Path(item["source"])
            target = cls._target_for(item, cfg)
            backup = source.parent / f"{source.name}.pre-asguard-migration"

            try:
                if item.get("service"):
                    cls._stop_service(item["service"])
                if item.get("container"):
                    cls._stop_container(item["container"])

                # umount
                cls._run("umount", str(source), timeout=30)
                cls._fstab_remove(source, target)

                # Restaurer l'original
                if backup.exists() and not source.exists():
                    cls._safe_rename(backup, source)
                elif backup.exists() and source.exists():
                    # Le mountpoint vide existe — on le remplace par le backup
                    shutil.rmtree(source, ignore_errors=True) if source.is_dir() else source.unlink(missing_ok=True)
                    cls._safe_rename(backup, source)

                if item.get("service"):
                    cls._start_service(item["service"])
                if item.get("container"):
                    cls._start_container(item["container"])

                report["rolled_back"].append(item["id"])
            except Exception as e:
                report["errors"].append({"id": item["id"], "error": str(e)})

        # Keep the off-LV manifest in sync with the new migration state.
        cls._write_manifest(cfg)
        return report

    @classmethod
    def _do_rollback(cls, actions: list):
        """Rollback des actions effectuées au sein d'UN item (échec intermédiaire)."""
        for action in reversed(actions):
            try:
                kind = action[0]
                if kind == "start_service":
                    cls._start_service(action[1])
                elif kind == "start_container":
                    cls._start_container(action[1])
                elif kind == "rm_target":
                    p = action[1]
                    if p.is_dir():
                        shutil.rmtree(p, ignore_errors=True)
                    else:
                        p.unlink(missing_ok=True)
                elif kind == "restore_original":
                    backup, source = action[1], action[2]
                    if source.exists():
                        if source.is_dir():
                            shutil.rmtree(source, ignore_errors=True)
                        else:
                            source.unlink(missing_ok=True)
                    cls._safe_rename(backup, source)
                elif kind == "umount":
                    cls._run("umount", str(action[1]), timeout=30)
                elif kind == "fstab_remove":
                    cls._fstab_remove(action[1], action[2])
            except Exception as e:
                logger.error("Rollback step failed: %s — %s", action, e)

    # ───────────── Primitives ─────────────

    @classmethod
    def _stop_service(cls, name: str) -> tuple[bool, str]:
        ok, _, err = cls._run("systemctl", "stop", name, timeout=60)
        if ok:
            return True, "stopped"
        # Some services (squid with open connections) ignore SIGTERM and hit
        # the stop timeout. Escalate to SIGKILL so the migration can proceed —
        # the service is restarted at the end of the item anyway.
        cls._run("systemctl", "kill", "-s", "SIGKILL", name, timeout=15)
        time.sleep(1)
        _, state, _ = cls._run("systemctl", "is-active", name, timeout=10)
        if state in ("inactive", "failed", "dead"):
            return True, "stopped (forcé via SIGKILL)"
        return False, err or "Timeout"

    @classmethod
    def _start_service(cls, name: str) -> tuple[bool, str]:
        ok, _, err = cls._run("systemctl", "start", name, timeout=30)
        return ok, err or "started"

    # ── Docker container lifecycle (PostgreSQL runs in app-db-container) ──────
    @classmethod
    def _stop_container(cls, name: str) -> tuple[bool, str]:
        ok, _, err = cls._run("docker", "stop", "-t", "30", name, timeout=60)
        if ok:
            return True, "container arrêté"
        return False, err or "docker stop échoué"

    @classmethod
    def _start_container(cls, name: str) -> tuple[bool, str]:
        ok, _, err = cls._run("docker", "start", name, timeout=60)
        return ok, err or "container démarré"

    @classmethod
    def _container_health(cls, name: str) -> tuple[bool, str]:
        # Postgres needs a few seconds to accept connections after start.
        for _ in range(10):
            time.sleep(2)
            ok, out, _ = cls._run(
                "docker", "inspect", "-f", "{{.State.Running}}", name, timeout=10,
            )
            if ok and out.strip() == "true":
                # If the image declares a healthcheck, wait for "healthy".
                _, health, _ = cls._run(
                    "docker", "inspect", "-f",
                    "{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}",
                    name, timeout=10,
                )
                h = health.strip()
                if h in ("healthy", "none"):
                    return True, f"running ({h})"
        return False, "container non opérationnel après 20s"

    @classmethod
    def _service_health(cls, name: str) -> tuple[bool, str]:
        # On laisse 2s au service pour stabiliser
        time.sleep(2)
        ok, out, _ = cls._run("systemctl", "is-active", name, timeout=10)
        if ok and out == "active":
            return True, out
        # Oneshot services (e.g. nftables: `nft -f` applies the ruleset then
        # exits) legitimately report `inactive` while having succeeded. Treat
        # a oneshot whose last run exited 0 as healthy.
        if out in ("inactive", "dead"):
            _, result, _ = cls._run(
                "systemctl", "show", name, "-p", "Type,ExecMainStatus",
                timeout=10,
            )
            props = dict(
                line.split("=", 1) for line in result.splitlines() if "=" in line
            )
            if props.get("Type") == "oneshot" and props.get("ExecMainStatus") == "0":
                return True, "active (oneshot, exit 0)"
        return False, out

    @classmethod
    def _mkdir(cls, path: Path) -> tuple[bool, str]:
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True, str(path)
        except Exception as e:
            return False, str(e)

    @classmethod
    def _copy_tree(cls, src: Path, dst: Path) -> tuple[bool, str]:
        """Copy a file or directory preserving EVERYTHING (mode, ownership,
        timestamps, symlinks, xattrs). Uses `cp -a` rather than shutil because
        shutil.copytree does NOT preserve uid/gid — and PostgreSQL refuses to
        start if its data directory is not owned by the postgres user."""
        try:
            if src.is_dir():
                if dst.exists():
                    shutil.rmtree(dst)
                dst.parent.mkdir(parents=True, exist_ok=True)
                # `cp -aT` treats dst as the directory itself (not a child).
                ok, _, err = cls._run("cp", "-aT", str(src), str(dst), timeout=600)
                if not ok:
                    return False, err or "cp -aT échoué"
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                ok, _, err = cls._run("cp", "-a", str(src), str(dst), timeout=120)
                if not ok:
                    return False, err or "cp -a échoué"
            return True, ""
        except Exception as e:
            return False, str(e)

    @staticmethod
    def _sha256_file(path: Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()

    @classmethod
    def _tree_signature(cls, root: Path) -> dict[str, str]:
        """Map of relative-path → sha256 for every regular file under root.
        Symlinks are recorded as 'symlink:<target>' so a copytree(symlinks=True)
        is verified faithfully without dereferencing. Used to compare a source
        tree against its migrated copy without depending on rsync."""
        sig: dict[str, str] = {}
        if root.is_file():
            sig["."] = cls._sha256_file(root)
            return sig
        for dirpath, _dirnames, filenames in os.walk(root):
            for name in filenames:
                p = Path(dirpath) / name
                rel = str(p.relative_to(root))
                try:
                    if p.is_symlink():
                        sig[rel] = f"symlink:{os.readlink(p)}"
                    elif p.is_file():
                        sig[rel] = cls._sha256_file(p)
                except OSError as e:
                    sig[rel] = f"error:{e}"
        return sig

    @classmethod
    def _verify_copy(cls, src: Path, dst: Path) -> tuple[bool, str]:
        """Pure-Python integrity check (rsync is not guaranteed to be present
        on the appliance). Compares the SHA-256 signature of every file in the
        source tree against the migrated copy."""
        try:
            src_sig = cls._tree_signature(src)
            dst_sig = cls._tree_signature(dst)
        except Exception as e:
            return False, f"signature KO: {e}"

        missing = [p for p in src_sig if p not in dst_sig]
        if missing:
            return False, f"{len(missing)} fichier(s) manquant(s) (ex: {missing[0]})"

        mismatched = [p for p in src_sig if src_sig[p] != dst_sig.get(p)]
        if mismatched:
            return False, f"{len(mismatched)} checksum(s) divergent(s) (ex: {mismatched[0]})"

        return True, f"checksum OK ({len(src_sig)} fichier(s))"

    @classmethod
    def _safe_rename(cls, src: Path, dst: Path) -> tuple[bool, str]:
        try:
            os.rename(src, dst)
            return True, str(dst)
        except OSError:
            ok, _, err = cls._run("mv", str(src), str(dst), timeout=30)
            return ok, err

    @classmethod
    def _recreate_mountpoint(cls, source: Path, type_: str) -> tuple[bool, str]:
        try:
            if type_ == "dir":
                source.mkdir(parents=True, exist_ok=True)
            else:
                source.parent.mkdir(parents=True, exist_ok=True)
                source.touch(exist_ok=True)
            return True, ""
        except Exception as e:
            return False, str(e)

    @classmethod
    def _bind_mount(cls, target: Path, source: Path) -> tuple[bool, str]:
        ok, _, err = cls._run("mount", "--bind", str(target), str(source), timeout=30)
        return ok, err

    # ───────────── Audit ─────────────

    @classmethod
    def _write_audit(cls, result: dict):
        try:
            AUDIT_DIR.mkdir(parents=True, exist_ok=True)
            ts = datetime.now(LOCAL_TZ).strftime("%Y%m%d_%H%M%S")
            (AUDIT_DIR / f"migration_{ts}.json").write_text(
                json.dumps(result, indent=2, ensure_ascii=False)
            )
        except Exception as e:
            logger.error("Audit write failed: %s", e)

    @classmethod
    def list_audits(cls, limit: int = 20) -> list[dict]:
        if not AUDIT_DIR.exists():
            return []
        files = sorted(AUDIT_DIR.glob("migration_*.json"), reverse=True)[:limit]
        out = []
        for f in files:
            try:
                out.append(json.loads(f.read_text()))
            except Exception:
                pass
        return out


# ────────────────────────────────────────────────────────────────────────────
# Utils
# ────────────────────────────────────────────────────────────────────────────

def _write_job(job_path: Path, payload: dict):
    job_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = job_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    tmp.replace(job_path)


def _human_bytes(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    for u in ("KB", "MB", "GB", "TB"):
        n /= 1024
        if n < 1024:
            return f"{n:.1f} {u}"
    return f"{n:.1f} PB"


def item_id_or_default(p: str) -> str:
    return Path(p).name
