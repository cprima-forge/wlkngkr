from __future__ import annotations

import json
import subprocess
from time import perf_counter
from typing import Any, Dict, List

from ..models import ProbeResult, ProbeStatus
from .base import Probe


class GeolocationProbe(Probe):
    """Geographic location detection via external IP services."""

    name = "geolocation"
    description = "Geographic location, timezone, and IP information."
    tags = ("network", "geo", "ip")

    def run(self) -> ProbeResult:
        start = perf_counter()
        meta = self.metadata()
        data: Dict[str, Any] = {}
        warnings: List[str] = []

        try:
            # Use external services to determine location
            geo_services = [
                ("https://ipinfo.io/json", "ipinfo"),
                ("https://ifconfig.co/json", "ifconfig"),
                ("http://ip-api.com/json", "ip-api"),
            ]

            for url, name in geo_services:
                try:
                    result = subprocess.run(
                        ["curl", "-s", "--max-time", "5", url],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    if result.returncode == 0 and result.stdout:
                        geo_data = json.loads(result.stdout)
                        data[name] = {
                            "ip": geo_data.get("ip", geo_data.get("query")),
                            "city": geo_data.get("city"),
                            "region": geo_data.get(
                                "region", geo_data.get("regionName")
                            ),
                            "country": geo_data.get(
                                "country", geo_data.get("countryCode")
                            ),
                            "org": geo_data.get("org"),
                            "timezone": geo_data.get("timezone"),
                        }
                        # One successful result is enough
                        break
                except Exception as e:
                    warnings.append(f"{name}_error: {e}")

            # Check system timezone
            try:
                result = subprocess.run(
                    ["cat", "/etc/timezone"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                data["system_timezone"] = result.stdout.strip()
            except Exception:
                pass

            # Check timedatectl if available
            try:
                result = subprocess.run(
                    ["timedatectl", "status"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    data["timedatectl"] = result.stdout[:500]
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
