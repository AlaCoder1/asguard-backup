import subprocess
from datetime import datetime
from pathlib import Path


class SystemBackupService:

    DB_CONTAINER = "app-db-container"
    DB_NAME = "postgres"
    BACKUP_DIR = Path("/var/backups/asguard")

    @classmethod
    def create_db_backup(cls):

        cls.BACKUP_DIR.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        backup_file = cls.BACKUP_DIR / f"asguard_db_{timestamp}.dump"

        subprocess.run([
            "docker", "exec",
            "-u", "postgres",
            cls.DB_CONTAINER,
            "pg_dump",
            "-F", "c",
            "-d", cls.DB_NAME,
            "-f", f"/tmp/{backup_file.name}"
        ], check=True)

        subprocess.run([
            "docker", "cp",
            f"{cls.DB_CONTAINER}:/tmp/{backup_file.name}",
            str(backup_file)
        ], check=True)

        return {
            "status": "ok",
            "file": str(backup_file)
        }