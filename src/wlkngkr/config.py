from typing import Dict, List, Optional
from pydantic import BaseModel


class RunnerConfig(BaseModel):
    """Configuration for a wlkngkr run.

    This can later be loaded from env, CLI, or a config file.
    """

    enabled_probes: Optional[List[str]] = None
    disabled_probes: List[str] = []
    tags: List[str] = []
    output_format: str = "json"  # json | text (keep simple for now)
    fail_on_error: bool = False
    extra_metadata: Dict[str, str] = {}
