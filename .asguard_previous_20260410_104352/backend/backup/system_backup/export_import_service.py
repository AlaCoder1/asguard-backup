import json
import logging
import shutil
import tarfile
from pathlib import Path
from tempfile import NamedTemporaryFile

from .base import safe_extract

logger = logging.getLogger(__name__)


class ExportImportService:
    BACKUP_ROOT = Path("/var/backups/asguard")
    REQUIRED_METADATA = "backup_metadata.json"
    ALLOWED_PREFIXES = (
        "db/", "firewall/", "vpn/", "web/", "ids/",
        "proxy/", "network/", "security/", "certificates/",
        "application/", "system_config/", "scheduled_tasks/",
        "packages/", "systemd_services/", "docker_state/",
        "logs/", "users_groups/", "vm_snapshot/",
        "backup_metadata.json"
    )

    @classmethod
    def export_backup(cls, backup_id: str) -> Path | None:
        backup_dir = cls.BACKUP_ROOT / backup_id
        if not backup_dir.exists() or not backup_dir.is_dir():
            logger.error("Export failed: Backup %s not found", backup_id)
            return None

        export_path = Path(f"/tmp/asguard_export_{backup_id}.tar.gz")
        try:
            with tarfile.open(export_path, "w:gz") as tar:
                tar.add(backup_dir, arcname=backup_id)
            return export_path
        except Exception as e:
            logger.error("Failed to export backup %s: %s", backup_id, e)
            if export_path.exists():
                export_path.unlink()
            return None

    @classmethod
    def import_backup(cls, uploaded_file) -> dict:
        temp_path = None
        dest_dir = None
        extract_root = None

        try:
            with NamedTemporaryFile(delete=False, suffix=".tar.gz") as temp:
                for chunk in uploaded_file.chunks():
                    temp.write(chunk)
                temp_path = Path(temp.name)

            validation = cls._validate_archive(temp_path)
            backup_id = validation["backup_id"]
            dest_dir = cls.BACKUP_ROOT / backup_id

            if dest_dir.exists():
                return {"status": "error", "message": f"Backup {backup_id} already exists."}

            extract_root = cls.BACKUP_ROOT / f".tmp_import_{backup_id}"
            if extract_root.exists():
                shutil.rmtree(extract_root)
            extract_root.mkdir(parents=True, exist_ok=True)

            safe_extract(temp_path, extract_root)

            extracted_backup_dir = extract_root / backup_id
            if not extracted_backup_dir.exists() or not extracted_backup_dir.is_dir():
                return {"status": "error", "message": "Imported archive root directory is invalid."}

            metadata_file = extracted_backup_dir / cls.REQUIRED_METADATA
            if not metadata_file.exists():
                return {"status": "error", "message": "backup_metadata.json not found after extraction."}

            shutil.move(str(extracted_backup_dir), str(dest_dir))

            with open(dest_dir / cls.REQUIRED_METADATA, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            return {
                "status": "success",
                "backup_id": backup_id,
                "message": "Backup imported successfully.",
                "metadata": metadata,
            }

        except ValueError as e:
            logger.warning("Import validation failed: %s", e)
            return {"status": "error", "message": str(e)}
        except Exception as e:
            logger.exception("Unexpected error during import")
            if dest_dir and dest_dir.exists():
                shutil.rmtree(dest_dir, ignore_errors=True)
            return {"status": "error", "message": str(e)}
        finally:
            if extract_root and extract_root.exists():
                shutil.rmtree(extract_root, ignore_errors=True)
            if temp_path and temp_path.exists():
                temp_path.unlink(missing_ok=True)

    @classmethod
    def _validate_archive(cls, archive_path: Path) -> dict:
        backup_id = None
        has_metadata = False

        with tarfile.open(archive_path, "r:gz") as tar:
            members = tar.getmembers()

            if not members:
                raise ValueError("Archive is empty.")

            for member in members:
                if member.issym() or member.islnk():
                    raise ValueError(f"Links are not allowed: '{member.name}'")

                parts = member.name.split("/")

                if backup_id is None:
                    backup_id = parts[0]
                    if not backup_id.startswith("backup_"):
                        raise ValueError(f"Invalid root directory name '{backup_id}', must start with 'backup_'")
                elif parts[0] != backup_id:
                    raise ValueError(
                        f"Archive contains multiple root directories. Found '{parts[0]}', expected '{backup_id}'."
                    )

                if len(parts) > 1:
                    relative_path = "/".join(parts[1:])

                    if ".." in relative_path or relative_path.startswith("/"):
                        raise ValueError(f"Path traversal detected in '{member.name}'")

                    if relative_path == cls.REQUIRED_METADATA:
                        has_metadata = True
                    elif relative_path and not any(relative_path.startswith(prefix) for prefix in cls.ALLOWED_PREFIXES):
                        raise ValueError(f"Unexpected path in archive: '{relative_path}'")

        if not backup_id:
            raise ValueError("Could not determine backup_id from archive.")
        if not has_metadata:
            raise ValueError("Archive missing backup_metadata.json")

        return {"backup_id": backup_id}