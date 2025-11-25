from __future__ import annotations

import os
import platform
from typing import Any, Dict

from ..models import ProbeResult, ProbeStatus
from .base import Probe


class SystemProbe(Probe):
    """Basic OS and hardware info."""

    name = "system"
    description = "Basic OS, Python, and hardware information."
    tags = ("core", "host")

    def run(self) -> ProbeResult:
        from time import perf_counter

        start = perf_counter()
        meta = self.metadata()
        data: Dict[str, Any] = {}

        try:
            uname = platform.uname()
            data.update(
                {
                    "os_system": uname.system,
                    "os_node": uname.node,
                    "os_release": uname.release,
                    "os_version": uname.version,
                    "os_machine": uname.machine,
                    "os_processor": uname.processor,
                    "python_version": platform.python_version(),
                    "cpu_count": os.cpu_count(),
                }
            )
            status = ProbeStatus.SUCCESS
            error = None
        except Exception as exc:  # pragma: no cover - defensive
            status = ProbeStatus.FAILURE
            error = str(exc)

        duration_ms = (perf_counter() - start) * 1000.0
        return ProbeResult(
            meta=meta,
            status=status,
            data=data,
            error=error,
            duration_ms=duration_ms,
        )
