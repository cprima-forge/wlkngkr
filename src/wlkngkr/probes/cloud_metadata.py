from __future__ import annotations

import subprocess
from time import perf_counter
from typing import Any, Dict, List

from ..models import ProbeResult, ProbeStatus
from .base import Probe


class CloudMetadataProbe(Probe):
    """Cloud provider metadata service access."""

    name = "cloud_metadata"
    description = "Probe AWS, GCP, and Azure metadata endpoints."
    tags = ("cloud", "metadata", "security")

    def run(self) -> ProbeResult:
        start = perf_counter()
        meta = self.metadata()
        data: Dict[str, Any] = {}
        warnings: List[str] = []

        try:
            # AWS metadata
            try:
                result = subprocess.run(
                    [
                        "curl",
                        "-s",
                        "--max-time",
                        "2",
                        "http://169.254.169.254/latest/meta-data/",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if (
                    result.returncode == 0
                    and result.stdout
                    and "404" not in result.stdout
                ):
                    data["aws_metadata"] = "accessible"
                    data["aws_metadata_content"] = result.stdout
                else:
                    data["aws_metadata"] = "not accessible"
            except Exception:
                data["aws_metadata"] = "not accessible"

            # GCP metadata
            try:
                result = subprocess.run(
                    [
                        "curl",
                        "-s",
                        "--max-time",
                        "2",
                        "-H",
                        "Metadata-Flavor: Google",
                        "http://metadata.google.internal/computeMetadata/v1/",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if (
                    result.returncode == 0
                    and result.stdout
                    and "404" not in result.stdout
                ):
                    data["gcp_metadata"] = "accessible"
                    data["gcp_metadata_content"] = result.stdout
                else:
                    data["gcp_metadata"] = "not accessible"
            except Exception:
                data["gcp_metadata"] = "not accessible"

            # Azure metadata
            try:
                result = subprocess.run(
                    [
                        "curl",
                        "-s",
                        "--max-time",
                        "2",
                        "-H",
                        "Metadata: true",
                        "http://169.254.169.254/metadata/instance?api-version=2021-02-01",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if (
                    result.returncode == 0
                    and result.stdout
                    and "404" not in result.stdout
                ):
                    data["azure_metadata"] = "accessible"
                    data["azure_metadata_content"] = result.stdout
                else:
                    data["azure_metadata"] = "not accessible"
            except Exception:
                data["azure_metadata"] = "not accessible"

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
