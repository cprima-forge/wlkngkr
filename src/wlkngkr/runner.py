from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, Optional, Sequence, Type

from .config import RunnerConfig
from .models import EnvReport, ProbeResult, ProbeStatus
from .registry import ProbeRegistry, default_registry
from .probes.base import Probe


class ProbeRunner:
    """Coordinates execution of probes and aggregates results."""

    def __init__(self, registry: ProbeRegistry | None = None) -> None:
        self.registry = registry or default_registry

    def _select_probes(
        self,
        config: RunnerConfig,
    ) -> Sequence[Type[Probe]]:
        # Start from enabled_probes or all
        if config.enabled_probes is not None:
            candidates = self.registry.filter_by_names(config.enabled_probes)
        elif config.tags:
            candidates = self.registry.filter_by_tags(config.tags)
        else:
            candidates = list(self.registry.all().values())

        # Filter out disabled
        disabled = set(config.disabled_probes)
        return [cls for cls in candidates if cls.name not in disabled]

    def run(self, config: Optional[RunnerConfig] = None) -> EnvReport:
        config = config or RunnerConfig()
        started_at = datetime.now(timezone.utc).isoformat()

        selected = self._select_probes(config)
        results: dict[str, ProbeResult] = {}

        for probe_cls in selected:
            probe = probe_cls()
            try:
                result = probe.run()
            except Exception as exc:  # pragma: no cover - defensive
                # Hard failure in probe logic
                result = ProbeResult(
                    meta=probe_cls.metadata(),
                    status=ProbeStatus.FAILURE,
                    data={},
                    error=str(exc),
                )
            results[probe_cls.name] = result

        finished_at = datetime.now(timezone.utc).isoformat()

        report = EnvReport(
            probes=results,
            started_at=started_at,
            finished_at=finished_at,
            tags=config.extra_metadata,
        )

        if config.fail_on_error:
            # Raise if any probe failed
            failures = [
                name
                for name, r in results.items()
                if r.status == ProbeStatus.FAILURE
            ]
            if failures:
                # Keep it simple: ValueError with list of failing probe names
                raise ValueError(f"Probes failed: {', '.join(failures)}")

        return report
