"""Locate non-secret Synctool diagnostic markers without extracting payloads.

This exact-byte scan is useful on files and raw images, including unallocated
space. It cannot rule out compressed, fragmented or bit-corrupted log records.
Runtime-looking hits are candidates, not authenticated execution evidence.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from dataclasses import dataclass
from pathlib import Path
import re
from typing import BinaryIO, Iterator


MAX_RUNTIME_FIELD_BYTES = 512
TOKEN_HEX_CHARS = 64
TARGET_LICENSE_FILENAME = (
    b"Harman_CMC_VP4_NA_VP4_2017Q2_UPDATE_MY14_REVA.lyc"
)
TARGET_LICENSE_TOKEN = hashlib.sha256(TARGET_LICENSE_FILENAME).hexdigest()

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
    value_token: str | None = None
    target_match: bool = False


def runtime_value_token(suffix: bytes) -> str | None:
    """Fingerprint one complete printable <...> value without disclosing it."""
    end = suffix.find(b">")
    if end <= 0 or end > MAX_RUNTIME_FIELD_BYTES:
        return None
    value = suffix[:end]
    if any(byte < 32 or byte >= 127 for byte in value):
        return None
    return hashlib.sha256(value).hexdigest()[:TOKEN_HEX_CHARS]


def scan_markers(stream: BinaryIO, *, chunk_size: int = 4 * 1024 * 1024) -> Iterator[MarkerHit]:
    """Stream hits, emitting only offsets, categories and a numeric App SKU.

    Hold enough trailing bytes to decide every marker's suffix at a chunk
    boundary. Starts before the retained tail are finalized exactly once.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    overlap = max(map(len, MARKERS.values())) + MAX_RUNTIME_FIELD_BYTES + 1
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
                suffix = data[
                    start + len(marker):
                    start + len(marker) + MAX_RUNTIME_FIELD_BYTES + 1
                ]
                kind = "unclassified"
                sku = None
                token = None
                if suffix.startswith(b"%"):
                    kind = "format_string"
                elif ((name.endswith("_record") or name == "excluded_file")
                      and suffix and 32 <= suffix[0] < 127):
                    kind = "runtime_candidate"
                    token = runtime_value_token(suffix)
                elif re.match(rb"-?[0-9]+(?:[^0-9]|$)", suffix):
                    kind = "runtime_candidate"
                    if name == "app_sku":
                        number = re.match(rb"-?[0-9]{1,10}(?![0-9])", suffix)
                        if number:
                            sku = int(number.group())
                hits.append(MarkerHit(
                    name,
                    base + start,
                    kind,
                    sku,
                    token,
                    token == TARGET_LICENSE_TOKEN,
                ))
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
                token = (
                    f" value_token=sha256:{hit.value_token}"
                    if hit.value_token is not None else ""
                )
                target = " target=my14_reva" if hit.target_match else ""
                print(
                    f"offset=0x{hit.offset:X} marker={hit.marker} "
                    f"kind={hit.kind}{sku}{token}{target}",
                    flush=True,
                )
        print(f"bytes_scanned={stream.tell()}")
    for (marker, kind), count in sorted(counts.items()):
        print(f"count={count} marker={marker} kind={kind}")
    print(f"total_hits={sum(counts.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
