from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Iterable, List, Optional, Type

if TYPE_CHECKING:
    from .probes.base import Probe


class ProbeRegistry:
    """Registry mapping probe names to Probe classes."""

    def __init__(self) -> None:
        self._probes: Dict[str, Type["Probe"]] = {}

    def register(self, probe_cls: Type["Probe"]) -> None:
        name = probe_cls.name
        if name in self._probes:
            raise ValueError(f"Probe '{name}' already registered")
        self._probes[name] = probe_cls

    def get(self, name: str) -> Type["Probe"]:
        return self._probes[name]

    def all(self) -> Dict[str, Type["Probe"]]:
        return dict(self._probes)

    def filter_by_names(
        self,
        names: Optional[Iterable[str]] = None,
    ) -> List[Type["Probe"]]:
        if names is None:
            return list(self._probes.values())
        return [self._probes[n] for n in names if n in self._probes]

    def filter_by_tags(
        self,
        tags: Optional[Iterable[str]] = None,
    ) -> List[Type["Probe"]]:
        if not tags:
            return list(self._probes.values())
        tag_set = set(tags)
        return [
            cls
            for cls in self._probes.values()
            if tag_set.intersection(getattr(cls, "tags", []))
        ]


# Default global registry
default_registry = ProbeRegistry()
