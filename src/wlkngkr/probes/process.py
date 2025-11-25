from __future__ import annotations

import os
import shutil
import subprocess
from time import perf_counter
from typing import Any, Dict, List

from ..models import ProbeResult, ProbeStatus
from .base import Probe

# Windows compatibility - resource module only on Unix
try:
    import resource
except ImportError:
    resource = None  # type: ignore


class ProcessProbe(Probe):
    """Process capabilities, resource limits, and available tools."""

    name = "process"
    description = "Resource limits, memory info, subprocess capabilities."
    tags = ("core", "process", "limits")

    def run(self) -> ProbeResult:
        start = perf_counter()
        meta = self.metadata()
        data: Dict[str, Any] = {}
        warnings: List[str] = []

        try:
            # Resource limits (Unix only)
            data["resource_limits"] = {}
            if resource is not None:
                limits = [
                    ("RLIMIT_CPU", resource.RLIMIT_CPU),
                    ("RLIMIT_FSIZE", resource.RLIMIT_FSIZE),
                    ("RLIMIT_DATA", resource.RLIMIT_DATA),
                    ("RLIMIT_STACK", resource.RLIMIT_STACK),
                    ("RLIMIT_CORE", resource.RLIMIT_CORE),
                    ("RLIMIT_RSS", resource.RLIMIT_RSS),
                    ("RLIMIT_NPROC", resource.RLIMIT_NPROC),
                    ("RLIMIT_NOFILE", resource.RLIMIT_NOFILE),
                    ("RLIMIT_MEMLOCK", resource.RLIMIT_MEMLOCK),
                    ("RLIMIT_AS", resource.RLIMIT_AS),
                ]
                for name, res in limits:
                    try:
                        soft, hard = resource.getrlimit(res)
                        data["resource_limits"][name] = {"soft": soft, "hard": hard}
                    except Exception:
                        pass
            else:
                data["resource_limits"] = "not available on Windows"

            # Memory info
            try:
                with open("/proc/meminfo") as f:
                    meminfo = f.read()
                    data["mem"] = {}
                    for line in meminfo.split("\n")[:10]:
                        if line:
                            parts = line.split(":")
                            if len(parts) == 2:
                                key = parts[0].strip()
                                val = parts[1].strip()
                                data["mem"][key] = val
            except Exception:
                pass

            # Check subprocess capabilities
            data["subprocess_tests"] = {}

            # Can we run common tools?
            tools = [
                "python3",
                "pip",
                "git",
                "curl",
                "wget",
                "apt",
                "docker",
                "systemctl",
                "ssh",
            ]
            for tool in tools:
                data["subprocess_tests"][tool] = shutil.which(tool) is not None

            # Can we fork/exec freely?
            try:
                result = subprocess.run(
                    ["echo", "test"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                data["subprocess_tests"]["basic_exec"] = result.returncode == 0
            except Exception as e:
                data["subprocess_tests"]["basic_exec"] = str(e)

            # Check seccomp/apparmor
            try:
                with open("/proc/self/status") as f:
                    for line in f:
                        if "Seccomp" in line:
                            data["seccomp"] = line.strip()
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
