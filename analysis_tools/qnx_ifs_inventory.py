"""Inventory QNX imagefs containers without modifying or executing vendor data."""

from __future__ import annotations

from dataclasses import dataclass
import struct
from typing import Callable


class FormatError(ValueError):
    """Raised when a purported QNX container is structurally invalid."""


@dataclass(frozen=True)
class HbcSegment:
    header_offset: int
    payload_offset: int
    decompressed_size: int
    compressed_size: int
    compression_type: int


@dataclass(frozen=True)
class ImagefsEntry:
    path: str
    inode: int
    mode: int
    uid: int
    gid: int
    mtime: int
    data_offset: int | None = None
    data_size: int | None = None
    link_target: str | None = None


@dataclass(frozen=True)
class ImagefsImage:
    image_size: int
    directory_size: int
    directory_offset: int
    entries: tuple[ImagefsEntry, ...]


BlockDecompressor = Callable[[bytes, int], bytes]


def _lzokay_decompress(block: bytes, expected_size: int) -> bytes:
    try:
        import lzokay
    except ImportError as error:
        raise RuntimeError(
            "lzokay is required for compressed data; install lzokay or supply decompress_block"
        ) from error
    return lzokay.decompress(block, expected_size)


def decompress_qnx_lzo_stream(
    stream: bytes,
    expected_size: int,
    *,
    decompress_block: BlockDecompressor | None = None,
    block_size: int = 65_536,
) -> tuple[bytes, int, int]:
    """Decode QNX's big-endian length-framed sequence of LZO blocks."""

    if expected_size < 0 or block_size <= 0:
        raise ValueError("expected_size must be nonnegative and block_size must be positive")
    decode = decompress_block or _lzokay_decompress
    output = bytearray()
    position = 0
    block_count = 0

    while len(output) < expected_size:
        if position + 2 > len(stream):
            raise FormatError("truncated QNX LZO block length")
        compressed_size = struct.unpack_from(">H", stream, position)[0]
        position += 2
        if compressed_size == 0:
            raise FormatError("QNX LZO stream ended before expected output size")
        block_end = position + compressed_size
        if block_end > len(stream):
            raise FormatError("truncated QNX LZO block payload")
        expected_block_size = min(block_size, expected_size - len(output))
        decoded = decode(stream[position:block_end], expected_block_size)
        if len(decoded) != expected_block_size:
            raise FormatError(
                f"QNX LZO block produced {len(decoded)} bytes, expected {expected_block_size}"
            )
        output.extend(decoded)
        position = block_end
        block_count += 1

    if position + 2 <= len(stream) and stream[position : position + 2] == b"\0\0":
        position += 2

    return bytes(output), position, block_count


def find_hbc_segments(blob: bytes) -> tuple[HbcSegment, ...]:
    """Find 64-byte Harman HBC image headers in a larger boot image."""

    signature = b"hbcifs\0\0"
    segments: list[HbcSegment] = []
    start = 0
    while True:
        header_offset = blob.find(signature, start)
        if header_offset < 0:
            break
        if header_offset + 64 <= len(blob):
            decompressed_size, compressed_size = struct.unpack_from("<II", blob, header_offset + 8)
            segments.append(
                HbcSegment(
                    header_offset=header_offset,
                    payload_offset=header_offset + 64,
                    decompressed_size=decompressed_size,
                    compressed_size=compressed_size,
                    compression_type=blob[header_offset + 26],
                )
            )
        start = header_offset + len(signature)
    return tuple(segments)


def _decode_path(raw: bytes) -> str:
    return raw.split(b"\0", 1)[0].decode("utf-8", errors="surrogateescape")


def parse_imagefs(data: bytes) -> ImagefsImage:
    """Parse the QNX imagefs header and directory table."""

    if len(data) < 20 or data[:7] != b"imagefs":
        raise FormatError("missing imagefs signature or header")
    image_size, header_and_directory_size, directory_offset = struct.unpack_from("<III", data, 8)
    available_size = min(image_size, len(data))
    directory_end = header_and_directory_size
    if directory_offset < 20 or directory_end < directory_offset or directory_end > available_size:
        raise FormatError("directory table exceeds image")
    directory_size = directory_end - directory_offset

    entries: list[ImagefsEntry] = []
    position = directory_offset
    while position < directory_end:
        if not data[position:directory_end].strip(b"\0"):
            break
        if position + 24 > directory_end:
            raise FormatError("truncated imagefs directory entry")
        record_size, _extattr, inode, mode, uid, gid, mtime = struct.unpack_from(
            "<HHIIIII", data, position
        )
        record_end = position + record_size
        if record_size < 24 or record_end > directory_end:
            raise FormatError("invalid imagefs directory entry size")

        file_type = mode & 0o170000
        data_offset: int | None = None
        data_size: int | None = None
        link_target: str | None = None
        if file_type == 0o100000:
            if record_size < 32:
                raise FormatError("truncated imagefs regular-file entry")
            data_offset, data_size = struct.unpack_from("<II", data, position + 24)
            if data_offset + data_size > available_size:
                raise FormatError("imagefs file data exceeds image")
            path = _decode_path(data[position + 32 : record_end])
        elif file_type == 0o120000:
            if record_size < 28:
                raise FormatError("truncated imagefs symlink entry")
            path_size, target_size = struct.unpack_from("<HH", data, position + 24)
            strings_start = position + 28
            strings_end = strings_start + path_size + target_size
            if strings_end > record_end:
                raise FormatError("imagefs symlink strings exceed entry")
            path = _decode_path(data[strings_start : strings_start + path_size])
            link_target = _decode_path(data[strings_start + path_size : strings_end])
        else:
            path = _decode_path(data[position + 24 : record_end])

        entries.append(
            ImagefsEntry(
                path=path,
                inode=inode,
                mode=mode,
                uid=uid,
                gid=gid,
                mtime=mtime,
                data_offset=data_offset,
                data_size=data_size,
                link_target=link_target,
            )
        )
        position = record_end

    return ImagefsImage(
        image_size=image_size,
        directory_size=directory_size,
        directory_offset=directory_offset,
        entries=tuple(entries),
    )
