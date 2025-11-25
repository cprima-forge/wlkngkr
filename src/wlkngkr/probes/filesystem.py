from __future__ import annotations

import os
import subprocess
from time import perf_counter
from typing import Any, Dict, List

from ..models import ProbeResult, ProbeStatus
from .base import Probe


class FilesystemProbe(Probe):
    """Filesystem access, disk space, and container indicators."""

    name = "filesystem"
    description = "Disk space, writable locations, and container detection."
    tags = ("core", "storage", "container")

    def run(self) -> ProbeResult:
        start = perf_counter()
        meta = self.metadata()
        data: Dict[str, Any] = {}
        warnings: List[str] = []

        try:
            # Disk space on key mounts
            mounts_to_check = ["/", "/tmp", "/home", "/var"]
            data["disk_space"] = {}
            for mount in mounts_to_check:
                try:
                    result = subprocess.run(
                        ["df", "-h", mount],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if result.returncode == 0:
                        lines = result.stdout.strip().split("\n")
                        if len(lines) > 1:
                            data["disk_space"][mount] = lines[1]
                except Exception:
                    pass

            # Check writable locations
            test_locations = [
                "/tmp",
                "/var/tmp",
                os.path.expanduser("~"),
                "/opt",
                "/usr/local",
            ]
            data["writable"] = {}
            for loc in test_locations:
                if os.path.exists(loc):
                    data["writable"][loc] = os.access(loc, os.W_OK)
                else:
                    data["writable"][loc] = "not exists"

            # List interesting directories
            dirs_to_list = ["/", "/tmp", os.path.expanduser("~")]
            data["directory_contents"] = {}
            for d in dirs_to_list:
                try:
                    data["directory_contents"][d] = os.listdir(d)
                except Exception as e:
                    data["directory_contents"][d] = str(e)

            # Check for container indicators
            data["container_indicators"] = {
                "dockerenv": os.path.exists("/.dockerenv"),
                "cgroup": os.path.exists("/proc/1/cgroup"),
            }
            try:
                with open("/proc/1/cgroup") as f:
                    cgroup_content = f.read()
                    data["container_indicators"]["cgroup_content"] = cgroup_content
            except Exception:
                pass

            status = ProbeStatus.SUCCESS
            error = None

        except Exception as exc:
            status = ProbeStatus.FAILURE
            error = str(exc)

        duration_ms = (perf_counter() - start) * 1000.0
        return ProbeResult(
            meta=meta,
            status=status,
            data=data,
            warnings=warnings,
            error=error,
            duration_ms=duration_ms,
        )
