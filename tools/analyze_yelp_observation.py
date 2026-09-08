#!/usr/bin/env python3
"""Classify one ordinary Yelp physical observation from a JSON file or stdin."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis_tools"))

from yelp_observation_analysis import (
    analyze_observation,
    canonical_bytes,
    load_model,
    strict_json_loads,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path, help="JSON observation file; omit to read stdin")
    args = parser.parse_args(argv)
    try:
        raw = args.input.read_text(encoding="utf-8") if args.input else sys.stdin.read()
        observation = strict_json_loads(raw)
        result = analyze_observation(observation, load_model())
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    sys.stdout.buffer.write(canonical_bytes(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
