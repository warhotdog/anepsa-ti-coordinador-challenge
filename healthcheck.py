import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ANEPSA HTTP healthcheck")
    parser.add_argument("--endpoint", default="http://localhost:3000/health")
    parser.add_argument("--interval", type=float, default=30)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print(f"monitor endpoint={args.endpoint} interval={args.interval}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())