import argparse
import subprocess
import time
from typing import Callable

import requests


HttpCheck = Callable[[str, float], bool]


def default_http_check(endpoint: str, timeout: float) -> bool:
    try:
        response = requests.get(endpoint, timeout=timeout)
        return response.status_code == 200 and response.elapsed.total_seconds() <= timeout
    except requests.RequestException:
        return False


def run_restart(command: str) -> int:
    if command.strip().lower() in {"simulate", "simulated", "noop"}:
        return 0
    completed = subprocess.run(command, shell=True, check=False)
    return completed.returncode


def monitor(
    endpoint: str,
    interval: float,
    timeout: float,
    max_failures: int,
    restart_command: str,
    once: bool = False,
    checker: HttpCheck = default_http_check,
) -> int:
    failures = 0
    while True:
        healthy = checker(endpoint, timeout)
        if healthy:
            failures = 0
            print("health_ok")
            if once:
                return 0
            time.sleep(interval)
            continue

        failures += 1
        print(f"health_fail consecutive_failures={failures}")
        if failures >= max_failures:
            run_restart(restart_command)
            return 2 if not checker(endpoint, timeout) else 0
        if once:
            return 1
        time.sleep(interval)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ANEPSA HTTP healthcheck con auto-recuperacion simulada")
    parser.add_argument("--endpoint", default="http://localhost:3000/health")
    parser.add_argument("--interval", type=float, default=30)
    parser.add_argument("--timeout", type=float, default=2)
    parser.add_argument("--max-failures", type=int, default=3)
    parser.add_argument("--restart-command", default="simulate")
    parser.add_argument("--once", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return monitor(args.endpoint, args.interval, args.timeout, args.max_failures, args.restart_command, once=args.once)


if __name__ == "__main__":
    raise SystemExit(main())