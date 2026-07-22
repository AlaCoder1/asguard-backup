"""
base.py — Shared utilities for the Asguard backup system.

Provides:
- ComponentResult : structured per-component result dataclass
- run_cmd         : safe subprocess wrapper (no shell=True, captures output, timeout)
- safe_extract    : tar extraction hardened against path traversal
- compute_sha256  : SHA-256 checksum of a file
- get_system_info : hostname, OS, kernel, for backup metadata
"""

import hashlib
import logging
import platform
import socket
import subprocess
import tarfile
import time
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import tarfile

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# ComponentResult
# ---------------------------------------------------------------------------

@dataclass
class ComponentResult:
    """
    Structured result for a single backup or restore component.

    Attributes
    ----------
    name       : component identifier (e.g. "database", "firewall")
    status     : "success" | "failed" | "skipped"
    message    : human-readable detail (error message or empty string)
    file       : relative path to the produced archive/dump inside the backup dir
    size_mb    : file size in megabytes (0.0 if not applicable)
    sha256     : SHA-256 hex digest of the produced file (empty if not applicable)
    duration_s : wall-clock seconds the operation took
    """

    name: str
    status: str = "success"         # "success" | "failed" | "skipped"
    message: str = ""
    file: str = ""                  # relative path inside backup dir
    size_mb: float = 0.0
    sha256: str = ""
    duration_s: float = 0.0

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "message": self.message,
            "file": self.file,
            "size_mb": round(self.size_mb, 3),
            "sha256": self.sha256,
            "duration_seconds": round(self.duration_s, 2),
        }

    @classmethod
    def skipped(cls, name: str, reason: str = "") -> "ComponentResult":
        return cls(name=name, status="skipped", message=reason)

    @classmethod
    def failed(cls, name: str, reason: str) -> "ComponentResult":
        return cls(name=name, status="failed", message=reason)


# ---------------------------------------------------------------------------
# Safe subprocess wrapper
# ---------------------------------------------------------------------------

def run_cmd(
    cmd: list[str],
    timeout: int = 120,
    env: dict | None = None,
    input_data: str | None = None,
) -> dict:
    if not isinstance(cmd, list) or not all(isinstance(c, str) for c in cmd):
        raise TypeError("run_cmd: cmd must be a list of plain strings")

    logger.debug("run_cmd: %s", " ".join(cmd))
    try:
        proc = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            input=input_data,
        )
        return {
            "success": True,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
            "returncode": proc.returncode,
        }
    except subprocess.CalledProcessError as exc:
        logger.error(
            "run_cmd failed (rc=%d): %s\nstderr: %s",
            exc.returncode,
            " ".join(cmd),
            exc.stderr,
        )
        return {
            "success": False,
            "stdout": exc.stdout.strip() if exc.stdout else "",
            "stderr": exc.stderr.strip() if exc.stderr else "",
            "returncode": exc.returncode,
            "error": exc.stderr.strip() if exc.stderr else f"Command exited with code {exc.returncode}",
        }
    except subprocess.TimeoutExpired:
        logger.error("run_cmd timed out (%ds): %s", timeout, " ".join(cmd))
        return {
            "success": False,
            "stdout": "",
            "stderr": "",
            "returncode": -1,
            "error": f"Command timed out after {timeout}s: {' '.join(cmd)}",
        }
    except FileNotFoundError:
        logger.error("run_cmd: executable not found: %s", cmd[0])
        return {
            "success": False,
            "stdout": "",
            "stderr": "",
            "returncode": -1,
            "error": f"Executable not found: {cmd[0]}",
        }
    except Exception as exc:
        logger.exception("run_cmd unexpected error: %s", " ".join(cmd))
        return {
            "success": False,
            "stdout": "",
            "stderr": "",
            "returncode": -1,
            "error": str(exc),
        }

# ---------------------------------------------------------------------------
# Safe tar extraction (anti path-traversal)
# ---------------------------------------------------------------------------

def safe_extract(archive_path: Path, dest: Path) -> None:
    """
    Safe enough for controlled Asguard backup archives.

    Rules:
    - reject absolute member names
    - reject '..' in member names
    - allow symlinks/hardlinks as stored in the archive
    """
    archive_path = Path(archive_path).resolve()
    dest = Path(dest).resolve()
    dest.mkdir(parents=True, exist_ok=True)

    with tarfile.open(archive_path, "r:gz") as tar:
        members = tar.getmembers()

        for member in members:
            member_path = PurePosixPath(member.name)

            if member_path.is_absolute():
                raise ValueError(f"Absolute path not allowed in archive member: '{member.name}'")

            if ".." in member_path.parts:
                raise ValueError(f"Path traversal detected in archive member: '{member.name}'")

        tar.extractall(path=dest, members=members)
        logger.debug("safe_extract: extracted %d members to %s", len(members), dest)  
# ---------------------------------------------------------------------------
# Checksum
# ---------------------------------------------------------------------------

def compute_sha256(path: Path, chunk_size: int = 65536) -> str:
    """
    Compute the SHA-256 hex digest of a file.

    Parameters
    ----------
    path       : path to the file
    chunk_size : read buffer size in bytes (default 64 KB)

    Returns
    -------
    Lowercase hex string (64 chars)
    """
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


# ---------------------------------------------------------------------------
# System info
# ---------------------------------------------------------------------------

def get_system_info() -> dict:
    """
    Collect basic system information for backup metadata.

    Returns
    -------
    dict with keys: hostname, os, kernel, python_version
    """
    try:
        hostname = socket.gethostname()
    except Exception:
        hostname = "unknown"

    try:
        os_info = platform.platform()
    except Exception:
        os_info = "unknown"

    try:
        kernel = platform.release()
    except Exception:
        kernel = "unknown"

    return {
        "hostname": hostname,
        "os": os_info,
        "kernel": kernel,
        "python_version": platform.python_version(),
    }


# ---------------------------------------------------------------------------
# Timing helper
# ---------------------------------------------------------------------------

class Timer:
    """Simple context-manager timer returning elapsed seconds."""

    def __init__(self):
        self._start: float = 0.0
        self.elapsed: float = 0.0

    def __enter__(self) -> "Timer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, *_) -> None:
        self.elapsed = time.perf_counter() - self._start
