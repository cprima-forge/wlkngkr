from __future__ import annotations

import getpass
import os
from typing import Any, Dict

from ..models import ProbeResult, ProbeStatus
from .base import Probe


class UserProbe(Probe):
    """Information about the current user/session."""

    name = "user"
    description = "Current user and related identifiers."
    tags = ("core", "user")

    def run(self) -> ProbeResult:
        from time import perf_counter

        start = perf_counter()
        meta = self.metadata()
        data: Dict[str, Any] = {}

        try:
            username = getpass.getuser()
            data["username"] = username

            # Platform-tolerant UID/GID
            uid = getattr(os, "getuid", lambda: None)()
            gid = getattr(os, "getgid", lambda: None)()
            data["uid"] = uid
            data["gid"] = gid

            home = os.path.expanduser("~")
            data["home"] = home

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
