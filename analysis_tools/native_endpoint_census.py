"""Candidate-led, read-only native endpoint and QNX API correlation.

The scanner reads explicit roots without following links. It records hashes,
relative paths, string offsets, and structured dynamic-symbol metadata when the
optional ELF parser is available. A string is never promoted to an import,
call edge, running service, or reachable endpoint.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any, Iterable, Mapping

from analysis_tools.evidence_model import write_json


TOOL_VERSION = "1.0"
API_FAMILIES = (
    "socket", "bind", "listen", "accept", "connect", "shutdown",
    "MsgSend", "MsgReceive", "MsgReply", "ChannelCreate", "ConnectAttach",
    "name_attach", "name_open", "dispatch_create", "resmgr_attach",
)
_ASCII = re.compile(rb"[\x20-\x7e]{3,}")


def _artifact(label: str, root: Path, path: Path) -> str:
    return f"{label}/{path.relative_to(root).as_posix()}"


def _elf_metadata(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        from analysis_tools.qnx_usb_inventory import elf_metadata
    except ModuleNotFoundError as error:
        if error.name == "elftools" or (error.name or "").startswith("elftools."):
            return None, "optional pyelftools dependency unavailable"
        raise
    try:
        with path.open("rb") as stream:
            return elf_metadata(stream), None
    except ValueError as error:
        return None, f"ELF metadata error: {error}"


def _candidate_offsets(data: bytes, candidates: Iterable[str]) -> list[tuple[str, int]]:
    matches = []
    for candidate in sorted(set(candidates)):
        needle = candidate.encode("utf-8")
        start = 0
        while True:
            offset = data.find(needle, start)
            if offset < 0:
                break
            matches.append((candidate, offset))
            start = offset + len(needle)
    return sorted(matches, key=lambda item: (item[1], item[0]))


def scan_native_roots(
    roots: Mapping[str, Path],
    candidates: Iterable[str],
    *,
    max_file_bytes: int = 64 * 1024 * 1024,
    max_files: int = 100_000,
) -> dict[str, Any]:
    candidate_list = sorted({value for value in candidates if value})
    if not candidate_list:
        raise ValueError("at least one nonempty candidate is required")
    if max_file_bytes <= 0 or max_files <= 0:
        raise ValueError("size and file limits must be positive")
    records = []
    errors = []
    coverage = {
        "files": 0,
        "bytes_read": 0,
        "matched_files": 0,
        "elf_files": 0,
        "oversized_files": 0,
        "skipped_links": 0,
        "structured_imports": 0,
        "structured_exports": 0,
    }
    dependency_reported = False
    for label, root_value in sorted(roots.items()):
        root = Path(root_value)
        if not label or "/" in label or "\\" in label:
            raise ValueError(f"invalid root label: {label!r}")
        if not root.is_dir():
            raise ValueError(f"root is not a directory: {label}")
        if root.is_symlink() or root.is_junction():
            raise ValueError(f"root must not be a link: {label}")
        for current, directories, files in os.walk(root, followlinks=False):
            current_path = Path(current)
            kept = []
            for directory in sorted(directories, key=str.lower):
                path = current_path / directory
                if path.is_symlink() or path.is_junction():
                    coverage["skipped_links"] += 1
                else:
                    kept.append(directory)
            directories[:] = kept
            for filename in sorted(files, key=str.lower):
                path = current_path / filename
                artifact = _artifact(label, root, path)
                if path.is_symlink():
                    coverage["skipped_links"] += 1
                    continue
                coverage["files"] += 1
                if coverage["files"] > max_files:
                    raise ValueError("file count limit exceeded")
                size = path.stat().st_size
                if size > max_file_bytes:
                    coverage["oversized_files"] += 1
                    errors.append({
                        "artifact": artifact,
                        "message": "file size limit exceeded",
                        "size": size,
                    })
                    continue
                with path.open("rb") as stream:
                    data = stream.read(max_file_bytes + 1)
                if len(data) > max_file_bytes:
                    raise ValueError(f"file grew beyond size limit: {artifact}")
                coverage["bytes_read"] += len(data)
                if data.startswith((b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")):
                    errors.append({
                        "artifact": artifact,
                        "message": "archive-like file skipped",
                    })
                    continue
                digest = None
                matches = _candidate_offsets(data, candidate_list)
                marker_matches = _candidate_offsets(data, API_FAMILIES)
                if matches:
                    digest = hashlib.sha256(data).hexdigest()
                    coverage["matched_files"] += 1
                for value, offset in matches:
                    records.append({
                        "id": f"{artifact}@{offset}:{value}",
                        "artifact": artifact,
                        "kind": "bounded_string_presence",
                        "name": value,
                        "offset": offset,
                        "sha256": digest,
                        "classification": "PROVED",
                        "production_enabled": "UNKNOWN",
                        "externally_reachable": "UNKNOWN",
                    })
                for value, offset in marker_matches if matches else ():
                    records.append({
                        "id": f"{artifact}@{offset}:api:{value}",
                        "artifact": artifact,
                        "kind": "api_name_string_presence",
                        "name": value,
                        "offset": offset,
                        "sha256": digest,
                        "classification": "PROVED",
                        "production_enabled": "UNKNOWN",
                        "externally_reachable": "UNKNOWN",
                    })
                if not data.startswith(b"\x7fELF"):
                    continue
                coverage["elf_files"] += 1
                metadata, metadata_error = _elf_metadata(path)
                if metadata_error is not None:
                    if metadata_error != "optional pyelftools dependency unavailable" or not dependency_reported:
                        errors.append({"artifact": artifact, "message": metadata_error})
                    dependency_reported |= metadata_error == "optional pyelftools dependency unavailable"
                    continue
                assert metadata is not None
                if digest is None:
                    digest = hashlib.sha256(data).hexdigest()
                selected = set(candidate_list) | set(API_FAMILIES)
                for direction, kind in (("imports", "structured_import"), ("exports", "structured_export")):
                    for name in metadata[direction]:
                        if not any(value in name for value in selected):
                            continue
                        coverage[direction.replace("imports", "structured_imports").replace("exports", "structured_exports")] += 1
                        records.append({
                            "id": f"{artifact}:{kind}:{name}",
                            "artifact": artifact,
                            "kind": kind,
                            "name": name,
                            "offset": None,
                            "sha256": digest,
                            "classification": "PROVED",
                            "production_enabled": "UNKNOWN",
                            "externally_reachable": "UNKNOWN",
                        })
    records.sort(key=lambda row: (row["artifact"], row["offset"] is None, row["offset"] or -1, row["kind"], row["name"]))
    errors.sort(key=lambda row: (row["artifact"], row["message"]))
    return {
        "schema_version": 1,
        "tool_version": TOOL_VERSION,
        "boundary": "Static metadata only; strings are not calls and imports are not runtime use.",
        "candidates": candidate_list,
        "coverage": coverage,
        "records": records,
        "errors": errors,
    }


def correlate(
    java_endpoints: Iterable[Mapping[str, Any]],
    native_records: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    correlations = []
    for endpoint in java_endpoints:
        name = endpoint.get("endpoint") or endpoint.get("name")
        if not isinstance(name, str) or not name:
            continue
        for record in native_records:
            native_name = record.get("name")
            if native_name == name:
                match_kind = "exact_endpoint_name"
            elif isinstance(native_name, str) and name in native_name:
                match_kind = "endpoint_name_substring"
            else:
                continue
            correlations.append({
                "java_endpoint_id": endpoint.get("id"),
                "native_record_id": record.get("id"),
                "endpoint": name,
                "match_kind": match_kind,
                "classification": "PROVED",
                "production_enabled": "UNKNOWN",
                "externally_reachable": "UNKNOWN",
            })
    return sorted(correlations, key=lambda row: (
        str(row["endpoint"]), str(row["java_endpoint_id"]),
        str(row["native_record_id"]),
    ))


def _root_argument(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("root must be LABEL=PATH")
    label, path = value.split("=", 1)
    if not label or not path:
        raise argparse.ArgumentTypeError("root must be LABEL=PATH")
    return label, Path(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", required=True, type=_root_argument)
    parser.add_argument("--candidate", action="append", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-file-bytes", type=int, default=64 * 1024 * 1024)
    args = parser.parse_args()
    roots = dict(args.root)
    if len(roots) != len(args.root):
        parser.error("duplicate root label")
    try:
        result = scan_native_roots(
            roots, args.candidate, max_file_bytes=args.max_file_bytes,
        )
        write_json(args.output, result)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
