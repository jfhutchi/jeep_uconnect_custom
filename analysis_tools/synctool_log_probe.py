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
    # Privacy-preserving identity-plane markers found in NNG Synctool logs.
    "device_id": b"Device ID:",
    "swid": b"SWID:",
    "device_code": b"DeviceCode:",
    "content_code": b"ContentCode:",
    "platform_id": b"Platform ID:",
    "using_ids": b"Using IDs",
    "application_license_records": b"# of license record for license type Application",
}

IDENTITY_LINE_MARKERS = frozenset({
    "device_id", "swid", "device_code", "content_code", "platform_id"
})


@dataclass(frozen=True)
class MarkerHit:
    marker: str
    offset: int
    kind: str
    app_sku: int | None = None
    value_token: str | None = None
    target_match: bool = False
    identity_tokens: tuple[str, ...] = ()
    record_count: int | None = None


def runtime_value_token(suffix: bytes) -> str | None:
    """Fingerprint one complete printable <...> value without disclosing it."""
    end = suffix.find(b">")
    if end <= 0 or end > MAX_RUNTIME_FIELD_BYTES:
        return None
    value = suffix[:end]
    if any(byte < 32 or byte >= 127 for byte in value):
        return None
    return hashlib.sha256(value).hexdigest()[:TOKEN_HEX_CHARS]


def runtime_line_token(suffix: bytes) -> str | None:
    """Fingerprint one complete printable line value after a marker."""
    value = suffix.lstrip(b" \t\r\n")
    end_positions = [position for position in (value.find(b"\r"), value.find(b"\n"))
                     if position >= 0]
    if end_positions:
        value = value[:min(end_positions)]
    elif len(value) > MAX_RUNTIME_FIELD_BYTES:
        return None
    if not value or len(value) > MAX_RUNTIME_FIELD_BYTES:
        return None
    if value.startswith(b"%") or any(byte < 32 or byte >= 127 for byte in value):
        return None
    return hashlib.sha256(value).hexdigest()[:TOKEN_HEX_CHARS]


def angle_value_tokens(suffix: bytes, *, expected: int = 2) -> tuple[str, ...]:
    """Fingerprint a bounded sequence of printable <...> values."""
    tokens: list[str] = []
    cursor = 0
    for _ in range(expected):
        start = suffix.find(b"<", cursor)
        if start < 0:
            return ()
        end = suffix.find(b">", start + 1)
        if end < 0 or end - start - 1 > MAX_RUNTIME_FIELD_BYTES:
            return ()
        value = suffix[start + 1:end]
        if (not value or value.startswith(b"%")
                or any(byte < 32 or byte >= 127 for byte in value)):
            return ()
        tokens.append(hashlib.sha256(value).hexdigest()[:TOKEN_HEX_CHARS])
        cursor = end + 1
    return tuple(tokens)


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
                identity_tokens: tuple[str, ...] = ()
                record_count = None
                stripped = suffix.lstrip(b" \t")
                prefix = data[max(0, start - 96):start]
                if stripped.startswith(b"%") or b"<%" in suffix[:MAX_RUNTIME_FIELD_BYTES]:
                    kind = "format_string"
                elif name in IDENTITY_LINE_MARKERS:
                    line_token = runtime_line_token(suffix)
                    if line_token is not None:
                        kind = "runtime_candidate"
                        identity_tokens = (line_token,)
                elif name == "using_ids":
                    identity_tokens = angle_value_tokens(suffix)
                    if identity_tokens:
                        kind = "runtime_candidate"
                elif name == "application_license_records":
                    count_match = re.search(
                        rb"Returning\s+(-?[0-9]{1,10})\s*$", prefix
                    )
                    if count_match:
                        kind = "runtime_candidate"
                        record_count = int(count_match.group(1))
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
                    identity_tokens,
                    record_count,
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
    target_counts: Counter[str] = Counter()
    with args.image.open("rb") as stream:
        for index, hit in enumerate(scan_markers(stream)):
            counts[(hit.marker, hit.kind)] += 1
            if hit.target_match:
                target_counts[hit.marker] += 1
            if index < args.max_hits:
                sku = f" app_sku={hit.app_sku}" if hit.app_sku is not None else ""
                token = (
                    f" value_token=sha256:{hit.value_token}"
                    if hit.value_token is not None else ""
                )
                target = " target=my14_reva" if hit.target_match else ""
                identities = (
                    " identity_tokens=" + ",".join(
                        f"sha256:{value}" for value in hit.identity_tokens
                    ) if hit.identity_tokens else ""
                )
                records = (
                    f" record_count={hit.record_count}"
                    if hit.record_count is not None else ""
                )
                print(
                    f"offset=0x{hit.offset:X} marker={hit.marker} "
                    f"kind={hit.kind}{sku}{token}{target}{identities}{records}",
                    flush=True,
                )
        print(f"bytes_scanned={stream.tell()}")
    for (marker, kind), count in sorted(counts.items()):
        print(f"count={count} marker={marker} kind={kind}")
    for marker, count in sorted(target_counts.items()):
        print(f"target_count={count} target=my14_reva marker={marker}")
    print(f"target_total={sum(target_counts.values())} target=my14_reva")
    print(f"total_hits={sum(counts.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
