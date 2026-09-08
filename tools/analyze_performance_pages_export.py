#!/usr/bin/env python3
"""Generate or verify deterministic Performance Pages export reports."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analysis_tools.performance_pages_export_analysis import generate_reports


DEFAULT_PRODUCER_NOTES = ROOT / "analysis_tools" / "performance_pages_export_notes.json"
DEFAULT_STORAGE_NOTES = (
    ROOT / "analysis_tools" / "performance_pages_storage_consumer_notes.json"
)
DEFAULT_REPORT_DIR = ROOT / "reports" / "kim19_runtime_analysis"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--producer-notes", type=Path, default=DEFAULT_PRODUCER_NOTES)
    parser.add_argument("--storage-notes", type=Path, default=DEFAULT_STORAGE_NOTES)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument(
        "--corpus",
        type=Path,
        help="optional recovered work tree used only to rehash bound source artifacts",
    )
    parser.add_argument("--check", action="store_true", help="fail if any report is stale")
    args = parser.parse_args(argv)
    try:
        return generate_reports(
            args.producer_notes,
            args.storage_notes,
            args.report_dir,
            check=args.check,
            corpus=args.corpus,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
