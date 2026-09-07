"""Audit Hello Uconnect and emit deterministic host-side reports."""

from __future__ import annotations

import argparse
from pathlib import Path

from .artifact_tools import audit_artifact, write_reports


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("jar", type=Path)
    parser.add_argument("descriptor", type=Path)
    parser.add_argument("allowlist", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    report = audit_artifact(args.jar, args.descriptor, args.allowlist)
    write_reports(report, args.output)
    print((args.output / "BUILD-STATUS.txt").read_text(encoding="ascii"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
