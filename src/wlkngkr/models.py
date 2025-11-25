from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ProbeMetadata(BaseModel):
    """Metadata common to all probes."""

    name: str
    version: str = "0.1.0"
    description: Optional[str] = None


class ProbeStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    SKIPPED = "skipped"
    PARTIAL = "partial"


class ProbeResult(BaseModel):
    """Container for a probe's result payload and status."""

    meta: ProbeMetadata
    status: ProbeStatus = Field(default=ProbeStatus.SUCCESS)
    data: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    error: Optional[str] = None
    duration_ms: Optional[float] = None


class EnvReport(BaseModel):
    """Aggregate result for a full wlkngkr run."""

    probes: Dict[str, ProbeResult]
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    host_identifier: Optional[str] = None
    tags: Dict[str, str] = Field(default_factory=dict)
