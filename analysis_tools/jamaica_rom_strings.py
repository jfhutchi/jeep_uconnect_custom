"""Decode bounded JamaicaVM ROM name, literal, and member metadata."""

from __future__ import annotations

import argparse
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path


class RomFormatError(ValueError):
    """Raised when a requested ROM string range is structurally invalid."""


@dataclass(frozen=True)
class RomStringEntry:
    offset: int
    value: str
    prefix_length: int
    suffix_length: int
    is_anchor: bool


@dataclass(frozen=True)
class RomStringStream:
    entries: tuple[RomStringEntry, ...]
    terminator_offset: int
    next_offset: int


@dataclass(frozen=True)
class RomMemberRecord:
    offset: int
    name_id: int
    descriptor_id: int
    name: str
    descriptor: str


@dataclass(frozen=True)
class RomLiteralRecord:
    offset: int
    literal_index: int
    pool_id: int
    value: str | None


def decode_literal_records(
    data: bytes,
    pool: tuple[RomStringEntry, ...],
    offset: int,
    record_count: int,
) -> tuple[RomLiteralRecord, ...]:
    """Decode a big-endian literal-index to one-based name-pool-ID table."""

    if offset < 0 or offset > len(data):
        raise ValueError("offset must be inside data")
    if record_count < 0:
        raise ValueError("record_count must be nonnegative")
    records: list[RomLiteralRecord] = []
    for literal_index in range(record_count):
        record_offset = offset + literal_index * 4
        if record_offset + 4 > len(data):
            raise RomFormatError("truncated literal record")
        pool_id = int.from_bytes(data[record_offset : record_offset + 4], "big")
        if pool_id > len(pool):
            raise RomFormatError("ROM literal record has invalid one-based pool ID")
        records.append(
            RomLiteralRecord(
                offset=record_offset,
                literal_index=literal_index,
                pool_id=pool_id,
                value=None if pool_id == 0 else pool[pool_id - 1].value,
            )
        )
    return tuple(records)


def decode_member_records(
    data: bytes,
    pool: tuple[RomStringEntry, ...],
    offset: int,
    record_count: int,
) -> tuple[RomMemberRecord, ...]:
    """Decode big-endian, one-based name/descriptor ID pairs."""

    if offset < 0 or offset > len(data):
        raise ValueError("offset must be inside data")
    if record_count < 0:
        raise ValueError("record_count must be nonnegative")
    records: list[RomMemberRecord] = []
    position = offset
    for _ in range(record_count):
        if position + 8 > len(data):
            raise RomFormatError("truncated member record")
        name_id = int.from_bytes(data[position : position + 4], "big")
        descriptor_id = int.from_bytes(data[position + 4 : position + 8], "big")
        if not 1 <= name_id <= len(pool) or not 1 <= descriptor_id <= len(pool):
            raise RomFormatError("ROM member record has invalid one-based pool ID")
        records.append(
            RomMemberRecord(
                offset=position,
                name_id=name_id,
                descriptor_id=descriptor_id,
                name=pool[name_id - 1].value,
                descriptor=pool[descriptor_id - 1].value,
            )
        )
        position += 8
    return tuple(records)


def _decode_entry(
    data: bytes,
    position: int,
    previous: str,
    index: int,
    last_anchor_index: int | None,
    block_size: int,
    encoding: str,
) -> tuple[RomStringEntry, int, int | None]:
    entry_offset = position
    if position >= len(data):
        raise RomFormatError("truncated ROM string entry tag")
    tag = data[position]
    position += 1
    is_extended_anchor = tag == 0xFF
    is_anchor = 0 < tag < 0x80 or is_extended_anchor

    if is_anchor:
        last_anchor_index = index
        prefix_length = 0
        if is_extended_anchor:
            length_end = position + 2
            if length_end > len(data):
                raise RomFormatError("truncated ROM string extended entry length")
            suffix_length = int.from_bytes(data[position:length_end], "big")
            position = length_end
        else:
            suffix_length = tag
    else:
        if tag == 0:
            raise RomFormatError("unexpected ROM string terminator")
        if last_anchor_index is None or index - last_anchor_index >= block_size:
            raise RomFormatError("ROM string block anchor exceeds configured block size")
        suffix_length = tag & 0x7F
        if position >= len(data):
            raise RomFormatError("truncated ROM string prefix length")
        prefix_length = data[position]
        position += 1
        if prefix_length > len(previous):
            raise RomFormatError("ROM string prefix length exceeds previous entry")

    suffix_end = position + suffix_length
    if suffix_end > len(data):
        raise RomFormatError("truncated ROM string suffix")
    try:
        suffix = data[position:suffix_end].decode(encoding)
    except UnicodeDecodeError as error:
        raise RomFormatError("ROM string suffix does not match the requested encoding") from error
    value = suffix if is_anchor else previous[:prefix_length] + suffix
    return (
        RomStringEntry(
            offset=entry_offset,
            value=value,
            prefix_length=prefix_length,
            suffix_length=suffix_length,
            is_anchor=is_anchor,
        ),
        suffix_end,
        last_anchor_index,
    )


def decode_front_coded_entries(
    data: bytes,
    offset: int,
    entry_count: int,
    *,
    block_size: int = 26,
    encoding: str = "latin-1",
) -> tuple[RomStringEntry, ...]:
    """Decode a known JamaicaVM name range without scanning unrelated data.

    Tags 0x01..0x7f encode short full/reset entries, 0x80..0xfe encode
    prefix/suffix entries, and 0xff encodes a big-endian extended full entry.
    ``block_size`` is the maximum permitted reset-index gap; resets may occur
    earlier. Callers must supply a confirmed offset and bounded entry count.
    """

    if offset < 0 or offset > len(data):
        raise ValueError("offset must be inside data")
    if entry_count < 0:
        raise ValueError("entry_count must be nonnegative")
    if block_size <= 0:
        raise ValueError("block_size must be positive")

    entries: list[RomStringEntry] = []
    position = offset
    previous = ""
    last_anchor_index: int | None = None

    for index in range(entry_count):
        entry, position, last_anchor_index = _decode_entry(
            data,
            position,
            previous,
            index,
            last_anchor_index,
            block_size,
            encoding,
        )
        entries.append(entry)
        previous = entry.value

    return tuple(entries)


def decode_front_coded_stream(
    data: bytes,
    offset: int,
    *,
    max_entries: int,
    max_bytes: int,
    block_size: int = 26,
    encoding: str = "latin-1",
) -> RomStringStream:
    """Decode a zero-terminated JamaicaVM name stream within explicit limits."""

    if offset < 0 or offset > len(data):
        raise ValueError("offset must be inside data")
    if max_entries <= 0:
        raise ValueError("max_entries must be positive")
    if max_bytes <= 0:
        raise ValueError("max_bytes must be positive")
    if block_size <= 0:
        raise ValueError("block_size must be positive")

    entries: list[RomStringEntry] = []
    position = offset
    previous = ""
    last_anchor_index: int | None = None

    while True:
        if position - offset >= max_bytes:
            raise RomFormatError("ROM string stream exceeded byte limit before terminator")
        if position >= len(data):
            raise RomFormatError("truncated ROM string stream terminator")
        if data[position] == 0:
            return RomStringStream(tuple(entries), position, position + 1)
        if len(entries) >= max_entries:
            raise RomFormatError("ROM string stream exceeded entry limit before terminator")

        entry, position, last_anchor_index = _decode_entry(
            data,
            position,
            previous,
            len(entries),
            last_anchor_index,
            block_size,
            encoding,
        )
        if position - offset > max_bytes:
            raise RomFormatError("ROM string entry exceeds byte limit")
        entries.append(entry)
        previous = entry.value


def _parse_int(value: str) -> int:
    return int(value, 0)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Decode a bounded JamaicaVM front-coded ROM string range or stream"
    )
    parser.add_argument("image", type=Path)
    parser.add_argument("--offset", required=True, type=_parse_int)
    range_mode = parser.add_mutually_exclusive_group(required=True)
    range_mode.add_argument("--count", type=_parse_int)
    range_mode.add_argument("--until-terminator", action="store_true")
    parser.add_argument("--max-entries", type=_parse_int, default=100_000)
    parser.add_argument("--max-bytes", type=_parse_int, default=16 * 1024 * 1024)
    parser.add_argument("--block-size", type=_parse_int, default=26)
    parser.add_argument("--find", action="append", default=[])
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--member-offset", type=_parse_int)
    parser.add_argument("--member-count", type=_parse_int)
    parser.add_argument("--literal-table-offset", type=_parse_int)
    parser.add_argument("--literal-count", type=_parse_int)
    parser.add_argument("--literal-index", action="append", type=_parse_int, default=[])
    args = parser.parse_args()

    data = args.image.read_bytes()
    stream: RomStringStream | None = None
    if args.count is not None:
        entries = decode_front_coded_entries(
            data,
            args.offset,
            args.count,
            block_size=args.block_size,
        )
    else:
        stream = decode_front_coded_stream(
            data,
            args.offset,
            max_entries=args.max_entries,
            max_bytes=args.max_bytes,
            block_size=args.block_size,
        )
        entries = stream.entries

    if args.summary:
        if stream is None:
            parser.error("--summary requires --until-terminator")
        tags = [data[entry.offset] for entry in entries]
        anchor_indexes = [index for index, entry in enumerate(entries) if entry.is_anchor]
        reset_gaps = [
            current - previous
            for previous, current in zip(anchor_indexes, anchor_indexes[1:])
        ]
        raw = data[args.offset : stream.next_offset]
        print(
            " ".join(
                [
                    f"entries={len(entries)}",
                    f"terminator=0x{stream.terminator_offset:08X}",
                    f"raw_bytes={len(raw)}",
                    f"sha256={hashlib.sha256(raw).hexdigest()}",
                    f"short_full={sum(0 < tag < 0x80 for tag in tags)}",
                    f"extended_full={tags.count(0xFF)}",
                    f"front_coded={sum(0x80 <= tag < 0xFF for tag in tags)}",
                    f"max_reset_gap={max(reset_gaps, default=0)}",
                ]
            ),
            file=sys.stderr,
        )
    requested = set(args.find)
    if (args.member_offset is None) != (args.member_count is None):
        parser.error("--member-offset and --member-count must be supplied together")
    if (args.literal_table_offset is None) != (args.literal_count is None):
        parser.error("--literal-table-offset and --literal-count must be supplied together")
    if args.member_offset is not None and args.literal_table_offset is not None:
        parser.error("member and literal decoding modes are mutually exclusive")
    if args.literal_table_offset is not None:
        if stream is None:
            parser.error("literal decoding requires --until-terminator")
        literal_records = decode_literal_records(
            data,
            stream.entries,
            args.literal_table_offset,
            args.literal_count,
        )
        selected_indexes = set(args.literal_index)
        for record in literal_records:
            if selected_indexes and record.literal_index not in selected_indexes:
                continue
            if requested and record.value not in requested:
                continue
            value = "<null>" if record.value is None else record.value
            print(
                f"0x{record.offset:08X}\t{record.literal_index}\t{record.pool_id}\t{value}"
            )
    elif args.member_offset is not None:
        if stream is None:
            parser.error("member decoding requires --until-terminator")
        records = decode_member_records(
            data,
            stream.entries,
            args.member_offset,
            args.member_count,
        )
        for record in records:
            if requested and record.name not in requested:
                continue
            print(f"0x{record.offset:08X}\t{record.name}\t{record.descriptor}")
    else:
        for entry in entries:
            if requested and entry.value not in requested:
                continue
            print(f"0x{entry.offset:08X}\t{entry.value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
