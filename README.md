# wlkngkr

Modular, extensible environment probing framework.

- Probes live in separate modules (system, user, etc.)
- A central runner orchestrates execution
- Results are structured Pydantic models
- CLI powered by `uv` + `typer`

## Quick start (with uv)

```bash
# inside cloned cprima-forge/wlkngkr
uv sync
uv run wlkngkr --list
uv run wlkngkr --probe system --probe user
```
