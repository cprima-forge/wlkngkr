from __future__ import annotations

import socket
import subprocess
from time import perf_counter
from typing import Any, Dict, List

from ..models import ProbeResult, ProbeStatus
from .base import Probe


class NetworkProbe(Probe):
    """Network connectivity, DNS resolution, and port binding tests."""

    name = "network"
    description = "DNS resolution, outbound HTTP, and port binding capabilities."
    tags = ("core", "network", "connectivity")

    def run(self) -> ProbeResult:
        start = perf_counter()
        meta = self.metadata()
        data: Dict[str, Any] = {}
        warnings: List[str] = []

        try:
            # Basic network info
            data["hostname"] = socket.gethostname()
            try:
                data["fqdn"] = socket.getfqdn()
            except Exception:
                pass

            # Get IP addresses
            try:
                result = subprocess.run(
                    ["ip", "addr"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                data["ip_addr"] = (
                    result.stdout if result.returncode == 0 else "failed"
                )
            except Exception:
                data["ip_addr"] = "ip command not available"

            # DNS resolution test
            test_hosts = ["google.com", "github.com", "pypi.org", "cloud.uipath.com"]
            data["dns_resolution"] = {}
            for host in test_hosts:
                try:
                    ip = socket.gethostbyname(host)
                    data["dns_resolution"][host] = ip
                except Exception as e:
                    data["dns_resolution"][host] = str(e)

            # Test outbound connectivity
            test_urls = [
                ("https://httpbin.org/ip", "HTTPS to httpbin"),
                ("https://api.github.com", "GitHub API"),
                ("https://pypi.org/simple/", "PyPI"),
            ]
            data["outbound_http"] = {}
            for url, desc in test_urls:
                try:
                    result = subprocess.run(
                        [
                            "curl",
                            "-s",
                            "-o",
                            "/dev/null",
                            "-w",
                            "%{http_code}",
                            "--max-time",
                            "5",
                            url,
                        ],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    data["outbound_http"][desc] = f"HTTP {result.stdout}"
                except Exception as e:
                    data["outbound_http"][desc] = str(e)

            # Check if we can bind to ports
            data["port_binding"] = {}
            for port in [8080, 3000, 5000]:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.bind(("0.0.0.0", port))
                    sock.close()
                    data["port_binding"][port] = "can bind"
                except Exception as e:
                    data["port_binding"][port] = str(e)

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
