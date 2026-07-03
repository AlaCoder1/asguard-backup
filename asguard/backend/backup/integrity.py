"""
Intégrité & anti-falsification des backups.

But
---
Garantir qu'un backup n'a pas été altéré — ransomware, corruption disque,
suppression partielle, falsification — entre sa création et sa restauration.
Une restauration à partir d'un backup compromis est pire que pas de backup :
elle propage l'attaque. Ce module permet de le détecter avant.

Comment
-------
À la fin de chaque backup on écrit DEUX petits fichiers dans le dossier :

  MANIFEST.sha256 : une ligne par fichier  "<sha256>  <chemin relatif>"
  MANIFEST.sig    : HMAC-SHA256 du MANIFEST.sha256 signé avec le secret de
                    l'appliance (settings.ENCRYPT_KEY).

Avant restauration, `verify_manifest()` recalcule les empreintes :
  - fichier modifié        -> hash différent      -> ALTÉRÉ
  - fichier disparu         -> manquant
  - fichier ajouté          -> intrus
  - MANIFEST.sig invalide   -> le manifeste lui-même a été falsifié

Le HMAC est la clé de voûte : un attaquant qui modifie un fichier PUIS
régénère un faux MANIFEST.sha256 ne peut pas produire de `MANIFEST.sig`
valide sans le secret de l'appliance. La falsification est donc toujours
détectée.

Non-intrusif (exigence : ne rien casser de l'existant)
------------------------------------------------------
* N'AJOUTE que 2 fichiers au dossier ; ne modifie aucun fichier existant.
* Ne lève jamais d'exception — un échec est journalisé, le backup continue.
* Un ancien backup sans manifeste est classé "non vérifiable" (`no_manifest`),
  jamais "corrompu" : aucune régression sur les backups déjà créés.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

MANIFEST_FILE = "MANIFEST.sha256"
SIGNATURE_FILE = "MANIFEST.sig"

# Fichiers exclus du manifeste (eux-mêmes : sinon référence circulaire).
_EXCLUDED = {MANIFEST_FILE, SIGNATURE_FILE}

# Taille de lecture par bloc — gros fichiers sans saturer la RAM.
_CHUNK = 1024 * 1024


def _secret() -> bytes:
    """Secret HMAC = secret de l'appliance. Sans lui, aucune signature valide."""
    key = ""
    try:
        from django.conf import settings
        key = getattr(settings, "ENCRYPT_KEY", "") or getattr(settings, "SECRET_KEY", "")
    except Exception:
        key = ""
    return str(key).encode("utf-8")


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(_CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def _iter_files(backup_dir: Path):
    """Tous les fichiers du backup, triés, hors fichiers de manifeste."""
    for p in sorted(backup_dir.rglob("*")):
        if p.is_file() and p.name not in _EXCLUDED:
            yield p


def write_manifest(backup_dir: Path) -> tuple[bool, str]:
    """
    Calcule et écrit MANIFEST.sha256 + MANIFEST.sig dans le dossier du backup.
    À appeler en TOUTE FIN de backup (tous les fichiers présents). Ne lève jamais.
    """
    backup_dir = Path(backup_dir)
    try:
        lines = []
        for f in _iter_files(backup_dir):
            rel = f.relative_to(backup_dir).as_posix()
            lines.append(f"{_sha256_file(f)}  {rel}")
        manifest = "\n".join(lines) + "\n"

        (backup_dir / MANIFEST_FILE).write_text(manifest, encoding="utf-8")
        signature = hmac.new(_secret(), manifest.encode("utf-8"), hashlib.sha256).hexdigest()
        (backup_dir / SIGNATURE_FILE).write_text(signature, encoding="utf-8")

        return True, f"Manifeste d'intégrité signé ({len(lines)} fichiers)."
    except Exception as exc:
        logger.warning("integrity: write_manifest failed for %s (%s)", backup_dir, exc)
        return False, f"Échec écriture manifeste : {exc}"


def verify_manifest(backup_dir: Path) -> dict:
    """
    Vérifie l'intégrité d'un backup.

    Retour :
        {
          "status":  "ok" | "tampered" | "no_manifest" | "error",
          "message": "<résumé lisible>",
          "modified": [...], "missing": [...], "extra": [...],
          "checked":  <nombre de fichiers contrôlés>,
        }
    """
    backup_dir = Path(backup_dir)
    result = {
        "status": "error",
        "message": "",
        "modified": [],
        "missing": [],
        "extra": [],
        "checked": 0,
    }

    manifest_path = backup_dir / MANIFEST_FILE
    sig_path = backup_dir / SIGNATURE_FILE

    if not manifest_path.exists():
        result["status"] = "no_manifest"
        result["message"] = "Backup sans manifeste d'intégrité (ancien format) — non vérifiable."
        return result

    try:
        manifest = manifest_path.read_text(encoding="utf-8")
    except Exception as exc:
        result["message"] = f"Manifeste illisible : {exc}"
        return result

    # 1. Le manifeste lui-même a-t-il été falsifié ? (signature HMAC)
    expected_sig = hmac.new(_secret(), manifest.encode("utf-8"), hashlib.sha256).hexdigest()
    actual_sig = sig_path.read_text(encoding="utf-8").strip() if sig_path.exists() else ""
    if not hmac.compare_digest(expected_sig, actual_sig):
        result["status"] = "tampered"
        result["message"] = (
            "Signature du manifeste invalide — le manifeste a été falsifié, "
            "ou le backup provient d'une autre appliance."
        )
        return result

    # 2. Recalcul des empreintes fichier par fichier.
    recorded: dict[str, str] = {}
    for line in manifest.splitlines():
        line = line.strip()
        if not line:
            continue
        digest, _, rel = line.partition("  ")
        if rel:
            recorded[rel] = digest

    on_disk = {
        f.relative_to(backup_dir).as_posix(): f
        for f in _iter_files(backup_dir)
    }

    modified, missing = [], []
    for rel, digest in recorded.items():
        f = on_disk.get(rel)
        if f is None:
            missing.append(rel)
        elif _sha256_file(f) != digest:
            modified.append(rel)
    extra = [rel for rel in on_disk if rel not in recorded]

    result["checked"] = len(recorded)
    result["modified"] = modified
    result["missing"] = missing
    result["extra"] = extra

    if modified or missing or extra:
        parts = []
        if modified:
            parts.append(f"{len(modified)} fichier(s) altéré(s)")
        if missing:
            parts.append(f"{len(missing)} fichier(s) manquant(s)")
        if extra:
            parts.append(f"{len(extra)} fichier(s) intrus")
        result["status"] = "tampered"
        result["message"] = "Intégrité compromise : " + ", ".join(parts) + "."
    else:
        result["status"] = "ok"
        result["message"] = f"Intégrité confirmée — {len(recorded)} fichiers intacts et signés."

    return result
