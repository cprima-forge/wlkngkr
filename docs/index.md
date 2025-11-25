# wlkngkr

`wlkngkr` is a modular environment probing framework.

- Each probe is a small, focused Python class.
- The runner orchestrates multiple probes and aggregates results.
- The CLI exposes common use cases:
  - list probes
  - run all or selected probes

## Distribution targets

- Source is packaged with `hatchling`.
- PyPI artifact exposes the `wlkngkr` console script.
- `uv` tooling is used for development, building, and publishing.

## Release workflow

1. Update version + changelog.
2. Tag releases as `vX.Y.Z` and push the tag.
3. GitHub Actions (`.github/workflows/release.yml`) will:
   - run tests via `uv run pytest`
   - build distributions via `uv build`
   - publish to PyPI with the `PYPI_API_TOKEN` secret
