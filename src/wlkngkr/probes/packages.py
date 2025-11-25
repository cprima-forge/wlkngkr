from __future__ import annotations

import importlib.metadata
from time import perf_counter
from typing import Any, Dict, List

from ..models import ProbeResult, ProbeStatus
from .base import Probe


class PackagesProbe(Probe):
    """Installed Python packages inspection."""

    name = "packages"
    description = "List installed Python packages and versions."
    tags = ("runtime", "python", "dependencies")

    def run(self) -> ProbeResult:
        start = perf_counter()
        meta = self.metadata()
        data: Dict[str, Any] = {}
        warnings: List[str] = []

        try:
            packages = {}
            for dist in importlib.metadata.distributions():
                name = dist.metadata.get("Name", "unknown")
                version = dist.metadata.get("Version", "unknown")
                packages[name] = version

            data["total_packages"] = len(packages)

            # Key packages we care about
            key_packages = ["uipath", "playwright", "aiohttp", "pydantic", "httpx"]
            data["key_packages"] = {
                pkg: packages.get(pkg, "not installed") for pkg in key_packages
            }

            # All packages (truncated)
            data["all_packages"] = dict(sorted(packages.items())[:50])

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
