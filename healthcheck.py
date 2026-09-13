import argparse
import json
import signal
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import requests


HttpCheck = Callable[[str, float], bool]


class GracefulStop:
    def __init__(self) -> None:
        self.stop = False

    def handler(self, signum, frame) -> None:  # noqa: ANN001
        self.stop = True

    def wait(self, seconds: float) -> None:
        deadline = time.monotonic() + max(0, seconds)
        while not self.stop and time.monotonic() < deadline:
            time.sleep(min(0.25, deadline - time.monotonic()))


def timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_log(log_file: Path, message: str) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    if log_file.exists() and not log_file.is_file():
        raise RuntimeError(f"log path is not a file: {log_file}")
    with log_file.open("a", encoding="utf-8") as handle:
        handle.write(f"{timestamp()} {message}\n")


def default_http_check(endpoint: str, timeout: float) -> bool:
    try:
        response = requests.get(endpoint, timeout=timeout)
        return response.status_code == 200 and response.elapsed.total_seconds() <= timeout
    except requests.RequestException:
        return False


def run_restart(command: str, log_file: Path) -> int:
    write_log(log_file, f"restart_attempt command={command!r}")
    if command.strip().lower() in {"simulate", "simulated", "noop"}:
        write_log(log_file, "restart_result simulated success")
        return 0
    completed = subprocess.run(command, shell=True, check=False, capture_output=True, text=True)
    write_log(log_file, f"restart_result exit_code={completed.returncode}")
    if completed.stderr.strip():
        write_log(log_file, f"restart_stderr {completed.stderr.strip()}")
    return completed.returncode


def notification_payload(endpoint: str, consecutive_failures: int) -> dict[str, object]:
    return {
        "service": "anepsa-api",
        "severity": "critical",
        "event": "healthcheck_failed_after_restart",
        "endpoint": endpoint,
        "consecutive_failures": consecutive_failures,
        "timestamp": timestamp(),
        "target": "slack_or_pagerduty_simulated",
    }


def monitor(
    endpoint: str,
    interval: float,
    timeout: float,
    max_failures: int,
    restart_command: str,
    log_file: Path,
    once: bool = False,
    checker: HttpCheck = default_http_check,
) -> int:
    stopper = GracefulStop()
    signal.signal(signal.SIGINT, stopper.handler)
    signal.signal(signal.SIGTERM, stopper.handler)

    failures = 0
    write_log(log_file, f"monitor_start endpoint={endpoint} interval={interval} timeout={timeout}")

    while not stopper.stop:
        iteration_started = time.monotonic()
        healthy = checker(endpoint, timeout)
        if healthy:
            if failures:
                write_log(log_file, f"service_recovered endpoint={endpoint}")
            failures = 0
            write_log(log_file, f"health_ok endpoint={endpoint}")
            if once:
                break
            stopper.wait(interval - (time.monotonic() - iteration_started))
            continue

        failures += 1
        write_log(log_file, f"health_fail endpoint={endpoint} consecutive_failures={failures}")

        if failures >= max_failures:
            run_restart(restart_command, log_file)
            if checker(endpoint, timeout):
                write_log(log_file, "post_restart_health_ok")
                failures = 0
            else:
                payload = notification_payload(endpoint, failures)
                write_log(log_file, f"notify {json.dumps(payload, sort_keys=True)}")
                print(json.dumps(payload, indent=2, sort_keys=True))
                return 2

        if once:
            break
        stopper.wait(interval - (time.monotonic() - iteration_started))

    write_log(log_file, "monitor_stop graceful=true")
    return 0


def self_test() -> int:
    log_file = Path("healthcheck_selftest.log")
    if log_file.exists():
        log_file.unlink()

    print("Scenario 1: servicio sano")
    ok_code = monitor(
        endpoint="http://healthy.local",
        interval=0.1,
        timeout=2,
        max_failures=3,
        restart_command="simulate",
        log_file=log_file,
        once=True,
        checker=lambda endpoint, timeout: True,
    )

    print("Scenario 2: servicio caido")
    attempts = {"count": 0}

    def down_checker(endpoint: str, timeout: float) -> bool:
        attempts["count"] += 1
        return False

    down_code = monitor(
        endpoint="http://down.local",
        interval=0.1,
        timeout=2,
        max_failures=3,
        restart_command="simulate",
        log_file=log_file,
        once=False,
        checker=down_checker,
    )
    print(f"Self-test log: {log_file}")
    return 0 if ok_code == 0 and down_code == 2 else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ANEPSA HTTP healthcheck con auto-recuperacion simulada")
    parser.add_argument("--endpoint", default="http://localhost:3000/health")
    parser.add_argument("--interval", type=float, default=30)
    parser.add_argument("--timeout", type=float, default=2)
    parser.add_argument("--max-failures", type=int, default=3)
    parser.add_argument("--restart-command", default="simulate")
    parser.add_argument("--log-file", default="healthcheck.log")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return self_test()
    return monitor(
        endpoint=args.endpoint,
        interval=args.interval,
        timeout=args.timeout,
        max_failures=args.max_failures,
        restart_command=args.restart_command,
        log_file=Path(args.log_file),
        once=args.once,
    )


if __name__ == "__main__":
    raise SystemExit(main())