"""Create the deterministic original-class-only Hello Uconnect JAR."""

from __future__ import annotations

import argparse
from pathlib import Path

from .artifact_tools import write_deterministic_jar


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("classes", type=Path)
    parser.add_argument("jar", type=Path)
    args = parser.parse_args()
    for member in write_deterministic_jar(args.classes, args.jar):
        print(member)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
