from wlkngkr.probes import register_builtin_probes
from wlkngkr.runner import ProbeRunner


def main() -> None:
    register_builtin_probes()
    runner = ProbeRunner()
    report = runner.run()
    print(report.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
