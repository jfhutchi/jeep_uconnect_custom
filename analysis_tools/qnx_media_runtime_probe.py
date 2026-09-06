#!/usr/bin/env python3
"""Inventory recovered QNX trees for projection runtime evidence.

The probe covers media/graphics candidates, era-compatible QNX CAR integration
services, and the Harman-specific service family already observed in RA4. It is
read-only and reports only controlled marker names, relative paths, sizes,
SHA-256 hashes, counts, and offsets; it never emits file contents.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import BinaryIO, Iterable

DEFAULT_MAX_FILE_BYTES = 128 * 1024 * 1024
DEFAULT_CHUNK_BYTES = 1024 * 1024
DEFAULT_MAX_OFFSETS = 16

MARKERS: dict[str, bytes] = {
    "libcodecengine": b"libcodecengine",
    "decodecombo": b"decodecombo",
    "dsplink": b"dsplink",
    "ce_loader": b"ce_loader",
    "cmem_parameters": b"cmem_parameters",
    "ce_audio_decoder": b"ce_audio_decoder",
    "h264": b"h264",
    "avc_decoder": b"avc_decoder",
    "openmax": b"openmax",
    "libomx": b"libomx",
    "omx_symbol": b"omx_",
    "gstreamer": b"gstreamer",
    "libgst": b"libgst",
    "sgx530": b"sgx530",
    "libimggles": b"libimggles",
    "pvrsrv": b"pvrsrv",
    "libpvr2d": b"libpvr2d",
    "libscreen": b"libscreen",
    "screen_window_buffers": b"screen_create_window_buffers",
    "startup_omap": b"startup-omap",
    # Era-compatible QNX CAR 2.1 / SDP 6.6 reference interfaces.
    "pps_launcher": b"/pps/services/launcher",
    "pps_app_launcher": b"/pps/services/app-launcher",
    "pps_navigator": b"/pps/system/navigator",
    "hmi_notification": b"hmi-notification",
    "libhnm": b"libhnm",
    "hnm_handsfree_plugin": b"event-source-handsfree",
    "hnm_hfp_call_incoming": b"hfp_call_incoming",
    "hnm_event_priorities": b"event-priorities",
    "pps_bluetooth_handsfree": b"/pps/services/bluetooth/handsfree",
    "pps_handsfree": b"/pps/services/handsfree",
    "authman": b"authman",
    "qtqnxcar2": b"qtqnxcar2",
    "bar_descriptor": b"bar-descriptor.xml",
    "qnx_elf_asset": b"qnx/elf",
    "run_native": b"run_native",
    "appinst_manager": b"/pps/services/appinst-mgr",
    "qthomescreen": b"qthomescreen",
    "nowplaying": b"nowplaying",
    "mm_control": b"mm-control",
    "mm_player": b"mm-player",
    "mm_renderer": b"mm-renderer",
    "pps_multimedia_renderer": b"/pps/services/multimedia/renderer",
    "screen_window_group": b"screen_create_window_group",
    # Stock-specific comparison markers already evidenced in the RA4 corpus.
    "servicebroker": b"servicebroker",
    "modulelink": b"modulelink",
    "phone_projection_service": b"phoneprojectionservice",
    "iphone_projection": b"iphoneprojection",
}

_MAX_MARKER_BYTES = max(map(len, MARKERS.values()))


def _relative_name(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _filename_tags(path: Path) -> list[str]:
    lowered = path.name.casefold().encode("utf-8", "ignore")
    return sorted(name for name, marker in MARKERS.items() if marker in lowered)


def _scan_stream(
    stream: BinaryIO,
    *,
    chunk_bytes: int = DEFAULT_CHUNK_BYTES,
    max_offsets: int = DEFAULT_MAX_OFFSETS,
) -> tuple[str, dict[str, dict[str, object]], int]:
    if chunk_bytes <= 0:
        raise ValueError("chunk_bytes must be positive")
    if max_offsets < 0:
        raise ValueError("max_offsets must not be negative")

    digest = hashlib.sha256()
    counts = {name: 0 for name in MARKERS}
    offsets: dict[str, list[int]] = {name: [] for name in MARKERS}
    tail = b""
    consumed = 0

    while True:
        chunk = stream.read(chunk_bytes)
        if not chunk:
            break
        digest.update(chunk)
        window = tail + chunk
        lowered = window.lower()
        window_base = consumed - len(tail)
        new_data_start = consumed

        for name, marker in MARKERS.items():
            cursor = 0
            while True:
                found = lowered.find(marker, cursor)
                if found < 0:
                    break
                absolute = window_base + found
                # A match wholly inside the retained tail was counted previously.
                if absolute + len(marker) > new_data_start:
                    counts[name] += 1
                    if len(offsets[name]) < max_offsets:
                        offsets[name].append(absolute)
                cursor = found + 1

        consumed += len(chunk)
        tail = window[-(_MAX_MARKER_BYTES - 1) :] if _MAX_MARKER_BYTES > 1 else b""

    matches = {
        name: {
            "count": counts[name],
            "offsets": offsets[name],
            "offsets_truncated": counts[name] > len(offsets[name]),
        }
        for name in sorted(MARKERS)
        if counts[name]
    }
    return digest.hexdigest(), matches, consumed


def scan_root(
    root: Path,
    *,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    chunk_bytes: int = DEFAULT_CHUNK_BYTES,
    max_offsets: int = DEFAULT_MAX_OFFSETS,
) -> dict[str, object]:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"not a directory: {root}")
    if max_file_bytes <= 0:
        raise ValueError("max_file_bytes must be positive")

    findings: list[dict[str, object]] = []
    skipped: list[dict[str, object]] = []
    files_scanned = 0
    bytes_scanned = 0

    for directory, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames.sort()
        filenames.sort()
        base = Path(directory)
        for filename in filenames:
            path = base / filename
            if path.is_symlink() or not path.is_file():
                continue
            size = path.stat().st_size
            relative = _relative_name(path, root)
            if size > max_file_bytes:
                skipped.append({"path": relative, "size": size, "reason": "max_file_bytes"})
                continue

            with path.open("rb") as stream:
                digest, marker_matches, read_size = _scan_stream(
                    stream, chunk_bytes=chunk_bytes, max_offsets=max_offsets
                )
            if read_size != size:
                raise OSError(f"short read for {relative}: expected {size}, got {read_size}")
            files_scanned += 1
            bytes_scanned += read_size
            name_tags = _filename_tags(path)
            if name_tags or marker_matches:
                findings.append(
                    {
                        "path": relative,
                        "size": size,
                        "sha256": digest,
                        "filename_tags": name_tags,
                        "content_markers": marker_matches,
                    }
                )

    return {
        "root_label": root.name,
        "files_scanned": files_scanned,
        "bytes_scanned": bytes_scanned,
        "files_skipped": len(skipped),
        "skipped": skipped,
        "findings": findings,
    }


def build_report(
    roots: Iterable[Path],
    *,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    chunk_bytes: int = DEFAULT_CHUNK_BYTES,
    max_offsets: int = DEFAULT_MAX_OFFSETS,
) -> dict[str, object]:
    reports = [
        scan_root(
            root,
            max_file_bytes=max_file_bytes,
            chunk_bytes=chunk_bytes,
            max_offsets=max_offsets,
        )
        for root in roots
    ]
    return {
        "format": "qnx-media-runtime-evidence-v1",
        "markers": sorted(MARKERS),
        "max_file_bytes": max_file_bytes,
        "max_offsets_per_marker": max_offsets,
        "roots": reports,
        "totals": {
            "roots": len(reports),
            "files_scanned": sum(int(item["files_scanned"]) for item in reports),
            "bytes_scanned": sum(int(item["bytes_scanned"]) for item in reports),
            "files_skipped": sum(int(item["files_skipped"]) for item in reports),
            "findings": sum(len(item["findings"]) for item in reports),
        },
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only QNX media-runtime marker census"
    )
    parser.add_argument("roots", nargs="+", type=Path)
    parser.add_argument("--max-file-bytes", type=int, default=DEFAULT_MAX_FILE_BYTES)
    parser.add_argument("--chunk-bytes", type=int, default=DEFAULT_CHUNK_BYTES)
    parser.add_argument("--max-offsets", type=int, default=DEFAULT_MAX_OFFSETS)
    parser.add_argument("--pretty", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    report = build_report(
        args.roots,
        max_file_bytes=args.max_file_bytes,
        chunk_bytes=args.chunk_bytes,
        max_offsets=args.max_offsets,
    )
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
