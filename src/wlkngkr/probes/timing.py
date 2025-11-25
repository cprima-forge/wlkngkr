from __future__ import annotations

import os
import time
from time import perf_counter
from typing import Any, Dict, List

from ..models import ProbeResult, ProbeStatus
from .base import Probe

# Capture module load time at import
_module_load_time = time.time()


class TimingProbe(Probe):
    """Timing and cold start analysis."""

    name = "timing"
    description = "Module load timing, process age, cold start analysis."
    tags = ("runtime", "performance", "timing")

    def run(self) -> ProbeResult:
        start = perf_counter()
        meta = self.metadata()
        data: Dict[str, Any] = {}
        warnings: List[str] = []

        try:
            now = time.time()

            data["module_load_timestamp"] = _module_load_time
            data["function_call_timestamp"] = now
            data["seconds_since_module_load"] = now - _module_load_time

            # Try to get process start time (Unix)
            try:
                with open(f"/proc/{os.getpid()}/stat") as f:
                    stat = f.read().split()
                    # Field 22 is starttime in clock ticks since boot
                    starttime_ticks = int(stat[21])
                    # Get system boot time and clock ticks per second
                    with open("/proc/uptime") as f2:
                        uptime = float(f2.read().split()[0])
                    clock_ticks = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
                    process_age = uptime - (starttime_ticks / clock_ticks)
                    data["process_age_seconds"] = process_age
            except Exception:
                data["process_age_seconds"] = "not available"

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
