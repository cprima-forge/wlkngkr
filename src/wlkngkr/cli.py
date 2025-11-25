from __future__ import annotations

import json
from typing import List, Optional

import typer

from .config import RunnerConfig
from .probes import register_builtin_probes
from .registry import default_registry
from .runner import ProbeRunner


app = typer.Typer(help="wlkngkr - modular environment probes")


def _list_probes() -> None:
    register_builtin_probes()
    for name, probe_cls in default_registry.all().items():
        desc = getattr(probe_cls, "description", "") or ""
        tags = ",".join(getattr(probe_cls, "tags", ()))
        line = f"{name:10s}  {desc}"
        if tags:
            line += f"  [tags: {tags}]"
        typer.echo(line)


def _run_probes(
    probe: Optional[List[str]],
    tag: Optional[List[str]],
    output_format: str,
    fail_on_error: bool,
) -> None:
    register_builtin_probes()

    config = RunnerConfig(
        enabled_probes=probe,
        tags=tag or [],
        output_format=output_format,
        fail_on_error=fail_on_error,
    )

    runner = ProbeRunner()
    report = runner.run(config=config)

    if output_format == "text":
        for name, result in report.probes.items():
            typer.echo(f"[{name}] status={result.status.value}")
        return

    typer.echo(report.model_dump_json(indent=2))


@app.command("list")
def list_probes() -> None:
    """List all available probes."""
    _list_probes()


@app.command("run")
def run(
    probe: Optional[List[str]] = typer.Option(
        None,
        "--probe",
        "-p",
        help="Probe name to run (can be given multiple times).",
    ),
    tag: Optional[List[str]] = typer.Option(
        None,
        "--tag",
        "-t",
        help="Tag(s) to select probes by (alternative to --probe).",
    ),
    output_format: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="Output format: json | text",
    ),
    fail_on_error: bool = typer.Option(
        False,
        "--fail-on-error",
        help="Exit with error if any probe fails.",
    ),
) -> None:
    """Run selected probes and print an EnvReport."""
    _run_probes(probe, tag, output_format, fail_on_error)


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    list_probes_flag: bool = typer.Option(
        False,
        "--list",
        help="List all available probes and exit.",
    ),
    probe: Optional[List[str]] = typer.Option(
        None,
        "--probe",
        "-p",
        help="Probe name to run (can be given multiple times).",
    ),
    tag: Optional[List[str]] = typer.Option(
        None,
        "--tag",
        "-t",
        help="Tag(s) to select probes by (alternative to --probe).",
    ),
    output_format: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="Output format: json | text",
    ),
    fail_on_error: bool = typer.Option(
        False,
        "--fail-on-error",
        help="Exit with error if any probe fails.",
    ),
) -> None:
    if ctx.invoked_subcommand:
        return

    if list_probes_flag:
        _list_probes()
        raise typer.Exit()

    _run_probes(probe, tag, output_format, fail_on_error)


def main() -> None:
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
