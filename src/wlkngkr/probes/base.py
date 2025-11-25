from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, Sequence

from ..models import ProbeMetadata, ProbeResult


class Probe(ABC):
    """Base class for all probes.

    Subclasses should keep side effects minimal and return a ProbeResult.
    """

    # These must be overridden by subclasses
    name: ClassVar[str]
    description: ClassVar[str] = ""
    tags: ClassVar[Sequence[str]] = ()

    @classmethod
    def metadata(cls) -> ProbeMetadata:
        return ProbeMetadata(
            name=cls.name,
            description=cls.description,
        )

    @abstractmethod
    def run(self) -> ProbeResult:
        """Execute the probe and return a ProbeResult."""
        raise NotImplementedError
