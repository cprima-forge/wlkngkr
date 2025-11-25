"""Builtin probes for wlkngkr."""

from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

from .system import SystemProbe
from .user import UserProbe
from .filesystem import FilesystemProbe
from .network import NetworkProbe
from .process import ProcessProbe
from .environment import EnvironmentProbe
from .kubernetes import KubernetesProbe
from .geolocation import GeolocationProbe
from .execution import ExecutionContextProbe
from .timing import TimingProbe
from .imports import ImportsProbe
from .cloud_metadata import CloudMetadataProbe
from .packages import PackagesProbe

if TYPE_CHECKING:
    from ..registry import ProbeRegistry
    from .base import Probe

BUILTIN_PROBES: Tuple[type["Probe"], ...] = (
    SystemProbe,
    UserProbe,
    FilesystemProbe,
    NetworkProbe,
    ProcessProbe,
    EnvironmentProbe,
    KubernetesProbe,
    GeolocationProbe,
    ExecutionContextProbe,
    TimingProbe,
    ImportsProbe,
    CloudMetadataProbe,
    PackagesProbe,
)


def register_builtin_probes(
    registry: "ProbeRegistry | None" = None,
) -> None:
    """Register all builtin probes on the default registry."""

    from ..registry import default_registry

    target = registry or default_registry
    existing = set(target.all())

    # Idempotency guard: repeated calls should not explode.
    for probe_cls in BUILTIN_PROBES:
        name = probe_cls.name
        if name in existing:
            continue
        target.register(probe_cls)
        existing.add(name)
