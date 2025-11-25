from __future__ import annotations

import asyncio
import os
import sys
from time import perf_counter
from typing import Any, Dict, List

from ..models import ProbeResult, ProbeStatus
from .base import Probe


class ExecutionContextProbe(Probe):
    """Execution context for comparing local vs cloud environments."""

    name = "execution_context"
    description = "Runtime identification, asyncio state, module loading context."
    tags = ("runtime", "uipath", "context")

    def run(self) -> ProbeResult:
        start = perf_counter()
        meta = self.metadata()
        data: Dict[str, Any] = {}
        warnings: List[str] = []

        try:
            # Runtime identification - check for UiPath cloud markers
            # Note: UIPATH_JOB_KEY is set, not UIPATH_JOB_ID
            data["is_cloud"] = os.environ.get("UIPATH_JOB_KEY") is not None
            data["job_id"] = os.environ.get("UIPATH_JOB_ID")
            data["job_key"] = os.environ.get("UIPATH_JOB_KEY")
            data["folder_key"] = os.environ.get("UIPATH_FOLDER_KEY")
            data["folder_path"] = os.environ.get("UIPATH_FOLDER_PATH")
            data["robot_key"] = os.environ.get("UIPATH_ROBOT_KEY")

            # Asyncio state
            try:
                loop = asyncio.get_running_loop()
                data["asyncio_loop_running"] = True
                data["asyncio_loop_type"] = type(loop).__name__
            except RuntimeError:
                data["asyncio_loop_running"] = False
                data["asyncio_loop_type"] = None

            # Module loading context
            data["__name__"] = __name__
            data["sys_path"] = sys.path
            data["sys_executable"] = sys.executable

            # Working directory vs script location
            data["cwd"] = os.getcwd()
            script_dir = os.path.dirname(os.path.abspath(__file__))
            data["script_dir"] = script_dir
            data["cwd_equals_script_dir"] = os.getcwd() == script_dir

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
