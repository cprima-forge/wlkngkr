from __future__ import annotations

import importlib
import importlib.util
from time import perf_counter
from typing import Any, Dict, List

from ..models import ProbeResult, ProbeStatus
from .base import Probe


class ImportsProbe(Probe):
    """Dynamic module loading capabilities."""

    name = "imports"
    description = "Test dynamic imports, conditional imports, find_spec."
    tags = ("runtime", "imports", "modules")

    def run(self) -> ProbeResult:
        start = perf_counter()
        meta = self.metadata()
        data: Dict[str, Any] = {}
        warnings: List[str] = []

        try:
            # Test importlib.import_module
            try:
                json_mod = importlib.import_module("json")
                data["importlib_import_module"] = "success"
                data["json_module_file"] = getattr(json_mod, "__file__", "builtin")
            except Exception as e:
                data["importlib_import_module"] = f"error: {e}"

            # Test __import__
            try:
                __import__("csv")
                data["__import__"] = "success"
            except Exception as e:
                data["__import__"] = f"error: {e}"

            # Test importing a module that may not exist
            try:
                importlib.import_module("nonexistent_module_12345")
                data["nonexistent_import"] = "unexpected success"
            except ModuleNotFoundError:
                data["nonexistent_import"] = "correctly raised ModuleNotFoundError"
            except Exception as e:
                data["nonexistent_import"] = f"unexpected error: {e}"

            # Test lazy/conditional import
            try:
                import sqlite3

                data["conditional_import_sqlite3"] = "success"
                data["sqlite3_version"] = sqlite3.sqlite_version
            except Exception as e:
                data["conditional_import_sqlite3"] = f"error: {e}"

            # Test importing from a string path
            try:
                spec = importlib.util.find_spec("os.path")
                data["find_spec_os_path"] = "found" if spec else "not found"
            except Exception as e:
                data["find_spec_os_path"] = f"error: {e}"

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
