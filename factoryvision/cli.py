from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import json

from .data.registry import DatasetRegistry


def main():
    p = ArgumentParser(prog="factoryvision")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("demo")
    d = sub.add_parser("data")
    d.add_argument("action", choices=["list", "download", "validate"])
    d.add_argument("name", nargs="?")
    d.add_argument("--out", default="datasets/raw")
    args = p.parse_args()
    if args.cmd == "demo":
        from .demo import run_demo

        print(json.dumps(run_demo(), indent=2))
    else:
        reg = DatasetRegistry(Path("datasets/registry.yaml"))
        if args.action == "list":
            print(json.dumps(reg.list(), indent=2))
        elif args.action == "download":
            print(reg.download(args.name, Path(args.out)))
        else:
            item = reg.get(args.name)
            result = {
                "name": args.name,
                "license_documented": bool(item.get("license")),
                "redistribution_allowed": item.get("redistribution_allowed"),
                "status": "registry-valid",
            }
            print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
