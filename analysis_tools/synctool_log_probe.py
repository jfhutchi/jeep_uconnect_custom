"""Locate non-secret Synctool diagnostic markers without extracting payloads.

This exact-byte scan is useful on files and raw images, including unallocated
space. It cannot rule out compressed, fragmented or bit-corrupted log records.
Runtime-looking hits are candidates, not authenticated execution evidence.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re
from typing import BinaryIO, Iterator


MARKERS = {
    "app_sku": b"App SKU ID ",
    "device_identity": b"Device.nng read, valid:",
    "activatable_record": b"Found activable license record <",
    "incompatible_record": b"Found incompatible activable license record <",
    "invalid_record": b"Found invalid license record <",
    "excluded_file": b"Removing file from file copy: <",
    "discard_records": b"Discarding ",
}


@dataclass(frozen=True)
class MarkerHit:
    marker: str
    offset: int
    kind: str
    app_sku: int | None = None


def scan_markers(stream: BinaryIO, *, chunk_size: int = 4 * 1024 * 1024) -> Iterator[MarkerHit]:
    """Stream hits, emitting only offsets, categories and a numeric App SKU.

    Hold enough trailing bytes to decide every marker's suffix at a chunk
    boundary. Starts before the retained tail are finalized exactly once.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    overlap = max(map(len, MARKERS.values())) + 32
    tail = b""
    consumed = 0
    while True:
        chunk = stream.read(chunk_size)
        data = tail + chunk
        base = consumed - len(tail)
        consumed += len(chunk)
        finalizable = len(data) if not chunk else max(0, len(data) - overlap)
        hits = []
        for name, marker in MARKERS.items():
            start = data.find(marker)
            while 0 <= start < finalizable:
                suffix = data[start + len(marker):start + len(marker) + 32]
                kind = "unclassified"
                sku = None
                if suffix.startswith(b"%"):
                    kind = "format_string"
                elif ((name.endswith("_record") or name == "excluded_file")
                      and suffix and 32 <= suffix[0] < 127):
                    kind = "runtime_candidate"
                elif re.match(rb"-?[0-9]+(?:[^0-9]|$)", suffix):
                    kind = "runtime_candidate"
                    if name == "app_sku":
                        number = re.match(rb"-?[0-9]{1,10}(?![0-9])", suffix)
                        if number:
                            sku = int(number.group())
                hits.append(MarkerHit(name, base + start, kind, sku))
                start = data.find(marker, start + 1)
        yield from sorted(hits, key=lambda hit: hit.offset)
        if not chunk:
            return
        tail = data[finalizable:]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--max-hits", type=int, default=100,
                        help="maximum displayed hits; counting always scans the entire input")
    args = parser.parse_args()
    if args.max_hits < 0:
        parser.error("--max-hits must be nonnegative")
    counts: Counter[tuple[str, str]] = Counter()
    with args.image.open("rb") as stream:
        for index, hit in enumerate(scan_markers(stream)):
            counts[(hit.marker, hit.kind)] += 1
            if index < args.max_hits:
                sku = f" app_sku={hit.app_sku}" if hit.app_sku is not None else ""
                print(f"offset=0x{hit.offset:X} marker={hit.marker} kind={hit.kind}{sku}",
                      flush=True)
        print(f"bytes_scanned={stream.tell()}")
    for (marker, kind), count in sorted(counts.items()):
        print(f"count={count} marker={marker} kind={kind}")
    print(f"total_hits={sum(counts.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
