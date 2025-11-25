from __future__ import annotations

import os
from time import perf_counter
from typing import Any, Dict, List

from ..models import ProbeResult, ProbeStatus
from .base import Probe


class EnvironmentProbe(Probe):
    """Environment variables and cloud provider detection."""

    name = "environment"
    description = "Environment variables and cloud provider indicators."
    tags = ("core", "env", "cloud")

    def run(self) -> ProbeResult:
        start = perf_counter()
        meta = self.metadata()
        data: Dict[str, Any] = {}
        warnings: List[str] = []

        try:
            # Interesting env vars (sanitized - no secrets)
            safe_vars = [
                "PATH",
                "HOME",
                "USER",
                "SHELL",
                "LANG",
                "LC_ALL",
                "PYTHONPATH",
                "VIRTUAL_ENV",
                "CONDA_DEFAULT_ENV",
                "HOSTNAME",
                "PWD",
                "TERM",
                "HTTP_PROXY",
                "HTTPS_PROXY",
                "NO_PROXY",
                "UIPATH_FOLDER_KEY",
                "UIPATH_ROBOT_KEY",
            ]

            data["env_vars"] = {}
            for var in safe_vars:
                val = os.environ.get(var)
                if val:
                    data["env_vars"][var] = val

            # Count total env vars
            data["total_env_vars"] = len(os.environ)

            # List ALL env var names (not values) to find interesting ones
            data["all_env_var_names"] = sorted(os.environ.keys())

            # Check for cloud provider indicators
            cloud_indicators = {
                "AWS": [
                    "AWS_REGION",
                    "AWS_LAMBDA_FUNCTION_NAME",
                    "ECS_CONTAINER_METADATA_URI",
                    "AWS_EXECUTION_ENV",
                ],
                "GCP": [
                    "GOOGLE_CLOUD_PROJECT",
                    "K_SERVICE",
                    "CLOUD_RUN_JOB",
                    "GCP_PROJECT",
                ],
                "Azure": [
                    "AZURE_FUNCTIONS_ENVIRONMENT",
                    "WEBSITE_SITE_NAME",
                    "AZURE_CLIENT_ID",
                ],
                "Kubernetes": [
                    "KUBERNETES_SERVICE_HOST",
                    "KUBERNETES_PORT",
                    "KUBERNETES_SERVICE_PORT",
                ],
            }
            data["cloud_indicators"] = {}
            for provider, vars in cloud_indicators.items():
                for var in vars:
                    if var in os.environ:
                        data["cloud_indicators"][provider] = var
                        break

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
