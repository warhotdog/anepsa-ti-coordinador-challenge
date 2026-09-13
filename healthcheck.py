import argparse
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


def monitor(endpoint: str, interval: float, timeout: float, once: bool = False, checker: HttpCheck = default_http_check) -> int:
    while True:
        healthy = checker(endpoint, timeout)
        print("health_ok" if healthy else "health_fail")
        if once or not healthy:
            return 0 if healthy else 1
        time.sleep(interval)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ANEPSA HTTP healthcheck")
    parser.add_argument("--endpoint", default="http://localhost:3000/health")
    parser.add_argument("--interval", type=float, default=30)
    parser.add_argument("--timeout", type=float, default=2)
    parser.add_argument("--once", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return monitor(args.endpoint, args.interval, args.timeout, once=args.once)


if __name__ == "__main__":
    raise SystemExit(main())