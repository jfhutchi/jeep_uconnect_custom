import struct
import unittest

from analysis_tools.qnx_ifs_inventory import (
    FormatError,
    decompress_qnx_lzo_stream,
    find_hbc_segments,
    parse_imagefs,
)


def _align4(value: int) -> int:
    return (value + 3) & ~3


def _common_entry(path_payload: bytes, *, inode: int, mode: int, tail: bytes = b"") -> bytes:
    size = _align4(24 + len(tail) + len(path_payload))
    record = struct.pack("<HHIIIII", size, 0, inode, mode, 0, 0, 1_569_331_634)
    record += tail + path_payload
    return record.ljust(size, b"\0")


def _synthetic_imagefs() -> bytes:
    root = _common_entry(b"\0", inode=1, mode=0o040755)
    regular = _common_entry(
        b"bin/demo\0",
        inode=2,
        mode=0o100755,
        tail=struct.pack("<II", 0x200, 4),
    )
    link_name = b"lib/demo\0"
    link_target = b"/bin/demo\0"
    symlink = _common_entry(
        link_name + link_target,
        inode=3,
        mode=0o120777,
        tail=struct.pack("<HH", len(link_name), len(link_target)),
    )
    directory = root + regular + symlink + b"\0\0\0\0"
    image_size = 0x204
    header_and_directory_size = 92 + len(directory)
    header = b"imagefs" + b"\x04" + struct.pack(
        "<III", image_size, header_and_directory_size, 92
    )
    image = bytearray(header.ljust(92, b"\0"))
    image.extend(directory)
    image.extend(b"\0" * (image_size - len(image)))
    image[0x200:0x204] = b"DEMO"
    return bytes(image)


class FramedLzoTests(unittest.TestCase):
    def test_decompresses_big_endian_length_framed_blocks(self) -> None:
        stream = b"\x00\x03abc\x00\x02de"

        output, consumed, block_count = decompress_qnx_lzo_stream(
            stream,
            expected_size=5,
            decompress_block=lambda block, expected: block,
            block_size=3,
        )

        self.assertEqual(output, b"abcde")
        self.assertEqual(consumed, len(stream))
        self.assertEqual(block_count, 2)

    def test_consumes_zero_terminator_after_expected_output(self) -> None:
        stream = b"\x00\x03abc\x00\x00"

        output, consumed, block_count = decompress_qnx_lzo_stream(
            stream,
            expected_size=3,
            decompress_block=lambda block, expected: block,
        )

        self.assertEqual(output, b"abc")
        self.assertEqual(consumed, len(stream))
        self.assertEqual(block_count, 1)

    def test_rejects_a_truncated_framed_block(self) -> None:
        with self.assertRaisesRegex(FormatError, "truncated QNX LZO block"):
            decompress_qnx_lzo_stream(
                b"\x00\x04abc",
                expected_size=4,
                decompress_block=lambda block, expected: block,
            )


class HbcHeaderTests(unittest.TestCase):
    def test_finds_hbc_header_and_exposes_compression_byte(self) -> None:
        header = bytearray(64)
        header[:8] = b"hbcifs\0\0"
        struct.pack_into("<II", header, 8, 0x123456, 0x654321)
        header[26] = 0x88
        blob = b"prefix" + bytes(header) + b"payload"

        segments = find_hbc_segments(blob)

        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0].header_offset, 6)
        self.assertEqual(segments[0].payload_offset, 70)
        self.assertEqual(segments[0].decompressed_size, 0x123456)
        self.assertEqual(segments[0].compressed_size, 0x654321)
        self.assertEqual(segments[0].compression_type, 0x88)


class ImagefsTests(unittest.TestCase):
    def test_parses_directory_regular_file_and_symlink_entries(self) -> None:
        try:
            image = parse_imagefs(_synthetic_imagefs())
        except FormatError as error:
            self.fail(f"valid header-and-directory-size field was rejected: {error}")

        self.assertEqual(image.image_size, 0x204)
        self.assertEqual([entry.path for entry in image.entries], ["", "bin/demo", "lib/demo"])
        self.assertEqual(image.entries[1].data_offset, 0x200)
        self.assertEqual(image.entries[1].data_size, 4)
        self.assertEqual(image.entries[2].link_target, "/bin/demo")

    def test_rejects_directory_table_outside_image(self) -> None:
        image = bytearray(_synthetic_imagefs())
        struct.pack_into("<I", image, 12, len(image) + 1)

        with self.assertRaisesRegex(FormatError, "directory table exceeds image"):
            parse_imagefs(bytes(image))


if __name__ == "__main__":
    unittest.main()
