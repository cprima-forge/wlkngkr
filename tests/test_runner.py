from __future__ import annotations

from typing import Any, Dict

from wlkngkr.models import ProbeResult, ProbeStatus
from wlkngkr.probes.base import Probe
from wlkngkr.registry import ProbeRegistry
from wlkngkr.runner import ProbeRunner


class DummyProbe(Probe):
    name = "dummy"
    description = "Dummy probe for testing."
    tags = ("test",)

    def run(self) -> ProbeResult:
        data: Dict[str, Any] = {"value": 42}
        return ProbeResult(
            meta=self.metadata(),
            status=ProbeStatus.SUCCESS,
            data=data,
        )


def test_runner_executes_registered_probe() -> None:
    registry = ProbeRegistry()
    registry.register(DummyProbe)

    runner = ProbeRunner(registry=registry)
    report = runner.run()

    assert "dummy" in report.probes
    result = report.probes["dummy"]
    assert result.status == ProbeStatus.SUCCESS
    assert result.data["value"] == 42
