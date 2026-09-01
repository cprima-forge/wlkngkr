# Architecture

## Core concepts

- **Probe**: small class that inspects a specific aspect of the environment
  and returns a `ProbeResult`.
- **Registry**: mapping from probe name to Probe class.
- **Runner**: selects probes from the registry, executes them, aggregates
  results into an `EnvReport`.
- **CLI**: thin layer that instantiates the runner and prints the report.

## Data model

- `ProbeMetadata`: name, version, description.
- `ProbeResult`: status, data payload, warnings, error, duration.
- `EnvReport`: mapping of probe name → `ProbeResult` plus timing metadata.
