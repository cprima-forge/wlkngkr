from __future__ import annotations

import os
import socket
from time import perf_counter
from typing import Any, Dict, List

from ..models import ProbeResult, ProbeStatus
from .base import Probe


class KubernetesProbe(Probe):
    """Kubernetes-specific environment detection."""

    name = "kubernetes"
    description = "Kubernetes environment, service account, and DNS configuration."
    tags = ("cloud", "k8s", "container")

    def run(self) -> ProbeResult:
        start = perf_counter()
        meta = self.metadata()
        data: Dict[str, Any] = {}
        warnings: List[str] = []

        try:
            # Check K8s env vars
            k8s_vars = [
                "KUBERNETES_SERVICE_HOST",
                "KUBERNETES_SERVICE_PORT",
                "KUBERNETES_PORT",
                "HOSTNAME",
            ]
            data["k8s_env"] = {}
            for var in k8s_vars:
                val = os.environ.get(var)
                if val:
                    data["k8s_env"][var] = val

            # Check for service account
            sa_paths = [
                "/var/run/secrets/kubernetes.io/serviceaccount/token",
                "/var/run/secrets/kubernetes.io/serviceaccount/namespace",
                "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt",
            ]
            data["service_account"] = {}
            for path in sa_paths:
                if os.path.exists(path):
                    data["service_account"][os.path.basename(path)] = "exists"
                    if "namespace" in path:
                        try:
                            with open(path) as f:
                                data["service_account"]["namespace_value"] = (
                                    f.read().strip()
                                )
                        except Exception:
                            pass

            # Check /etc/resolv.conf for K8s DNS
            try:
                with open("/etc/resolv.conf") as f:
                    data["resolv_conf"] = f.read()
            except Exception:
                pass

            # Check for K8s-style hostname (usually pod name)
            data["hostname"] = socket.gethostname()

            # Try to detect node info from /etc/hosts
            try:
                with open("/etc/hosts") as f:
                    data["etc_hosts"] = f.read()
            except Exception:
                pass

            # Check downward API mounts
            downward_paths = [
                "/etc/podinfo",
                "/etc/podinfo/labels",
                "/etc/podinfo/annotations",
            ]
            data["downward_api"] = {}
            for path in downward_paths:
                if os.path.exists(path):
                    if os.path.isfile(path):
                        try:
                            with open(path) as f:
                                data["downward_api"][path] = f.read()[:500]
                        except Exception:
                            data["downward_api"][path] = "exists (unreadable)"
                    else:
                        try:
                            data["downward_api"][path] = os.listdir(path)
                        except Exception:
                            data["downward_api"][path] = "exists (dir)"

            # Determine if likely K8s
            data["is_kubernetes"] = bool(data["k8s_env"]) or "Kubernetes" in data.get(
                "etc_hosts", ""
            )

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
