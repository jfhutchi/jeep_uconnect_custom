import io
import hashlib
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import analysis_tools.jamaica_rom_strings as rom_strings
from analysis_tools.jamaica_rom_strings import (
    RomFormatError,
    decode_front_coded_entries,
)


def _full(value: bytes) -> bytes:
    return bytes([len(value)]) + value


def _delta(prefix_length: int, suffix: bytes) -> bytes:
    return bytes([0x80 | len(suffix), prefix_length]) + suffix


def _extended_full(value: bytes) -> bytes:
    return b"\xff" + len(value).to_bytes(2, "big") + value


class FrontCodedStringTests(unittest.TestCase):
    def test_decodes_full_anchor_and_prefix_suffix_entries(self) -> None:
        data = (
            _full(b"getDeveloperToken")
            + _delta(5, b"vice")
            + _delta(9, b"Token")
        )

        entries = decode_front_coded_entries(data, 0, 3)

        self.assertEqual(
            [entry.value for entry in entries],
            ["getDeveloperToken", "getDevice", "getDeviceToken"],
        )
        self.assertEqual([entry.offset for entry in entries], [0, 18, 24])

    def test_resets_to_a_full_anchor_at_each_block(self) -> None:
        data = (
            _full(b"alpha")
            + _delta(0, b"beta")
            + _full(b"gamma")
            + _delta(0, b"zeta")
        )

        entries = decode_front_coded_entries(data, 0, 4, block_size=2)

        self.assertEqual(
            [entry.value for entry in entries],
            ["alpha", "beta", "gamma", "zeta"],
        )

    def test_accepts_an_early_full_reset_before_the_maximum_block_size(self) -> None:
        data = _full(b"alpha") + _full(b"beta") + _delta(0, b"zeta")

        try:
            entries = decode_front_coded_entries(data, 0, 3, block_size=26)
        except RomFormatError as error:
            self.fail(f"early full reset was rejected: {error}")

        self.assertEqual(
            [entry.value for entry in entries],
            ["alpha", "beta", "zeta"],
        )
        self.assertEqual([entry.is_anchor for entry in entries], [True, True, False])

    def test_decodes_big_endian_extended_full_entry(self) -> None:
        value = b"a" * 129

        try:
            entries = decode_front_coded_entries(_extended_full(value), 0, 1)
        except RomFormatError as error:
            self.fail(f"extended full entry was rejected: {error}")

        self.assertEqual(entries[0].value, value.decode("ascii"))
        self.assertEqual(entries[0].suffix_length, 129)
        self.assertTrue(entries[0].is_anchor)

    def test_stream_stops_at_zero_terminator_and_preserves_boundary(self) -> None:
        data = _full(b"alpha") + _delta(0, b"beta") + b"\x00trailing"
        self.assertTrue(
            hasattr(rom_strings, "decode_front_coded_stream"),
            "terminator-bounded stream decoder is missing",
        )

        stream = rom_strings.decode_front_coded_stream(
            data,
            0,
            max_entries=10,
            max_bytes=100,
        )

        self.assertEqual([entry.value for entry in stream.entries], ["alpha", "beta"])
        self.assertEqual(stream.terminator_offset, 12)
        self.assertEqual(stream.next_offset, 13)

    def test_stream_rejects_entry_that_crosses_byte_limit(self) -> None:
        data = _full(b"alpha") + b"\x00"

        with self.assertRaisesRegex(RomFormatError, "entry exceeds byte limit"):
            rom_strings.decode_front_coded_stream(
                data,
                0,
                max_entries=10,
                max_bytes=1,
            )

    def test_decodes_big_endian_member_name_and_descriptor_ids(self) -> None:
        pool = decode_front_coded_entries(_full(b"install") + _full(b"(String)V"), 0, 2)
        data = b"head" + (1).to_bytes(4, "big") + (2).to_bytes(4, "big")
        self.assertTrue(
            hasattr(rom_strings, "decode_member_records"),
            "member-record decoder is missing",
        )

        records = rom_strings.decode_member_records(data, pool, 4, 1)

        self.assertEqual(records[0].offset, 4)
        self.assertEqual(records[0].name_id, 1)
        self.assertEqual(records[0].descriptor_id, 2)
        self.assertEqual(records[0].name, "install")
        self.assertEqual(records[0].descriptor, "(String)V")

    def test_rejects_zero_member_pool_id(self) -> None:
        pool = decode_front_coded_entries(_full(b"install") + _full(b"()V"), 0, 2)
        data = (0).to_bytes(4, "big") + (2).to_bytes(4, "big")

        with self.assertRaisesRegex(RomFormatError, "one-based"):
            rom_strings.decode_member_records(data, pool, 0, 1)

    def test_rejects_truncated_member_record(self) -> None:
        pool = decode_front_coded_entries(_full(b"install") + _full(b"()V"), 0, 2)

        with self.assertRaisesRegex(RomFormatError, "truncated member record"):
            rom_strings.decode_member_records((1).to_bytes(4, "big"), pool, 0, 1)

    def test_decodes_big_endian_literal_pool_ids(self) -> None:
        pool = decode_front_coded_entries(_full(b"alpha") + _full(b"beta"), 0, 2)
        data = (0).to_bytes(4, "big") + (2).to_bytes(4, "big")
        self.assertTrue(
            hasattr(rom_strings, "decode_literal_records"),
            "literal-record decoder is missing",
        )

        records = rom_strings.decode_literal_records(data, pool, 0, 2)

        self.assertEqual(records[0].literal_index, 0)
        self.assertEqual(records[0].pool_id, 0)
        self.assertIsNone(records[0].value)
        self.assertEqual(records[1].literal_index, 1)
        self.assertEqual(records[1].pool_id, 2)
        self.assertEqual(records[1].value, "beta")

    def test_rejects_invalid_literal_pool_id(self) -> None:
        pool = decode_front_coded_entries(_full(b"alpha"), 0, 1)

        try:
            rom_strings.decode_literal_records((2).to_bytes(4, "big"), pool, 0, 1)
        except RomFormatError as error:
            self.assertRegex(str(error), "literal.*pool ID")
        except IndexError as error:
            self.fail(f"invalid pool ID leaked IndexError: {error}")
        else:
            self.fail("invalid literal pool ID was accepted")

    def test_rejects_truncated_literal_record(self) -> None:
        pool = decode_front_coded_entries(_full(b"alpha"), 0, 1)

        with self.assertRaisesRegex(RomFormatError, "truncated literal record"):
            rom_strings.decode_literal_records(b"\x00\x00\x00", pool, 0, 1)

    def test_metadata_decoders_reject_negative_record_count(self) -> None:
        pool = decode_front_coded_entries(_full(b"alpha"), 0, 1)

        for decoder in (
            rom_strings.decode_literal_records,
            rom_strings.decode_member_records,
        ):
            with self.subTest(decoder=decoder.__name__):
                with self.assertRaisesRegex(ValueError, "record_count"):
                    decoder(b"", pool, 0, -1)

    def test_metadata_decoders_reject_negative_offset(self) -> None:
        pool = decode_front_coded_entries(_full(b"alpha"), 0, 1)

        for decoder in (
            rom_strings.decode_literal_records,
            rom_strings.decode_member_records,
        ):
            with self.subTest(decoder=decoder.__name__):
                try:
                    decoder(b"\x00" * 8, pool, -1, 1)
                except RomFormatError as error:
                    self.fail(f"negative offset leaked a format error: {error}")
                except ValueError as error:
                    self.assertRegex(str(error), "offset")
                else:
                    self.fail("negative metadata offset was accepted")

    def test_cli_accepts_terminator_bounded_mode(self) -> None:
        data = _full(b"alpha") + _delta(0, b"beta") + b"\x00"
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "rom.bin"
            image.write_bytes(data)
            stdout = io.StringIO()
            stderr = io.StringIO()
            argv = [
                "jamaica_rom_strings.py",
                str(image),
                "--offset",
                "0",
                "--until-terminator",
                "--max-entries",
                "10",
                "--max-bytes",
                "100",
            ]
            with patch.object(sys, "argv", argv):
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    try:
                        result = rom_strings.main()
                    except SystemExit as error:
                        self.fail(f"stream CLI mode was rejected: {error}")

        self.assertEqual(result, 0)
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(
            stdout.getvalue().splitlines(),
            ["0x00000000\talpha", "0x00000006\tbeta"],
        )

    def test_cli_accepts_hexadecimal_numeric_bounds(self) -> None:
        data = _full(b"alpha") + _delta(0, b"beta") + b"\x00"
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "rom.bin"
            image.write_bytes(data)
            stdout = io.StringIO()
            stderr = io.StringIO()
            argv = [
                "jamaica_rom_strings.py",
                str(image),
                "--offset",
                "0x0",
                "--until-terminator",
                "--max-entries",
                "0xA",
                "--max-bytes",
                "0x64",
                "--block-size",
                "0x1A",
            ]
            with patch.object(sys, "argv", argv):
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    try:
                        result = rom_strings.main()
                    except SystemExit as error:
                        self.fail(f"hexadecimal numeric bounds were rejected: {error}")

        self.assertEqual(result, 0)
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(
            stdout.getvalue().splitlines(),
            ["0x00000000\talpha", "0x00000006\tbeta"],
        )

    def test_cli_summary_reports_stream_hash_and_entry_kinds(self) -> None:
        data = _full(b"alpha") + _delta(0, b"beta") + b"\x00"
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "rom.bin"
            image.write_bytes(data)
            stderr = io.StringIO()
            argv = [
                "jamaica_rom_strings.py",
                str(image),
                "--offset",
                "0",
                "--until-terminator",
                "--max-entries",
                "10",
                "--max-bytes",
                "100",
                "--summary",
            ]
            with patch.object(sys, "argv", argv):
                with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                    try:
                        result = rom_strings.main()
                    except SystemExit as error:
                        self.fail(f"stream summary mode was rejected: {error}")

        self.assertEqual(result, 0)
        self.assertEqual(
            stderr.getvalue().strip(),
            " ".join(
                [
                    "entries=2",
                    "terminator=0x0000000C",
                    "raw_bytes=13",
                    f"sha256={hashlib.sha256(data).hexdigest()}",
                    "short_full=1",
                    "extended_full=0",
                    "front_coded=1",
                    "max_reset_gap=0",
                ]
            ),
        )

    def test_cli_prints_member_records_against_decoded_pool(self) -> None:
        pool_data = _full(b"install") + _full(b"()V") + b"\x00"
        member_offset = 16
        data = pool_data.ljust(member_offset, b"\x00")
        data += (1).to_bytes(4, "big") + (2).to_bytes(4, "big")
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "rom.bin"
            image.write_bytes(data)
            stdout = io.StringIO()
            stderr = io.StringIO()
            argv = [
                "jamaica_rom_strings.py",
                str(image),
                "--offset",
                "0",
                "--until-terminator",
                "--max-entries",
                "10",
                "--max-bytes",
                "100",
                "--member-offset",
                str(member_offset),
                "--member-count",
                "1",
            ]
            with patch.object(sys, "argv", argv):
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    try:
                        result = rom_strings.main()
                    except SystemExit as error:
                        self.fail(f"member CLI mode was rejected: {error}")

        self.assertEqual(result, 0)
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(stdout.getvalue(), "0x00000010\tinstall\t()V\n")

    def test_cli_prints_selected_literal_record(self) -> None:
        pool_data = _full(b"alpha") + _full(b"beta") + b"\x00"
        table_offset = 16
        data = pool_data.ljust(table_offset, b"\x00")
        data += (0).to_bytes(4, "big") + (2).to_bytes(4, "big")
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "rom.bin"
            image.write_bytes(data)
            stdout = io.StringIO()
            stderr = io.StringIO()
            argv = [
                "jamaica_rom_strings.py",
                str(image),
                "--offset",
                "0",
                "--until-terminator",
                "--max-entries",
                "10",
                "--max-bytes",
                "100",
                "--literal-table-offset",
                str(table_offset),
                "--literal-count",
                "2",
                "--literal-index",
                "1",
            ]
            with patch.object(sys, "argv", argv):
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    try:
                        result = rom_strings.main()
                    except SystemExit as error:
                        self.fail(f"literal CLI mode was rejected: {error}")

        self.assertEqual(result, 0)
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(stdout.getvalue(), "0x00000014\t1\t2\tbeta\n")

    def test_rejects_prefix_longer_than_previous_entry(self) -> None:
        data = _full(b"short") + _delta(6, b"er")

        with self.assertRaisesRegex(RomFormatError, "prefix length"):
            decode_front_coded_entries(data, 0, 2)

    def test_rejects_truncated_suffix(self) -> None:
        data = _full(b"anchor") + bytes([0x85, 1]) + b"xy"

        with self.assertRaisesRegex(RomFormatError, "truncated"):
            decode_front_coded_entries(data, 0, 2)

    def test_requires_full_entry_at_block_boundary(self) -> None:
        data = _full(b"alpha") + _delta(0, b"beta")

        with self.assertRaisesRegex(RomFormatError, "block anchor"):
            decode_front_coded_entries(data, 0, 2, block_size=1)


if __name__ == "__main__":
    unittest.main()
