import struct
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
from unittest import mock

from analysis_tools.arm_elf_analysis import ArmElfAnalyzer, Elf32Image, ElfFormatError, main


def _arm_bl(source: int, target: int) -> bytes:
    displacement = target - (source + 8)
    if displacement % 4:
        raise ValueError("ARM BL target must be word aligned")
    return struct.pack("<I", 0xEB000000 | ((displacement >> 2) & 0x00FFFFFF))


def _elf32(payload: bytes, *, vaddr: int = 0x1000, flags: int = 5) -> bytes:
    ident = b"\x7fELF\x01\x01\x01" + b"\x00" * 9
    header = ident + struct.pack(
        "<HHIIIIIHHHHHH",
        2,
        40,
        1,
        vaddr,
        52,
        0,
        0x05000200,
        52,
        32,
        1,
        40,
        0,
        0,
    )
    segment_offset = 0x100
    program_header = struct.pack(
        "<IIIIIIII",
        1,
        segment_offset,
        vaddr,
        vaddr,
        len(payload),
        len(payload),
        flags,
        0x1000,
    )
    return (header + program_header).ljust(segment_offset, b"\x00") + payload


class Elf32ImageTests(unittest.TestCase):
    def test_parses_arm_little_endian_load_segment_and_maps_addresses(self) -> None:
        image = Elf32Image.from_bytes(_elf32(b"ABCD"))

        self.assertEqual(image.machine, 40)
        self.assertEqual(image.entry, 0x1000)
        self.assertEqual(image.vaddr_to_offset(0x1002, 2), 0x102)
        self.assertEqual(image.read_vaddr(0x1001, 2), b"BC")
        self.assertEqual(len(image.load_segments), 1)
        self.assertTrue(image.load_segments[0].executable)

    def test_rejects_address_range_outside_file_backed_segment(self) -> None:
        image = Elf32Image.from_bytes(_elf32(b"ABCD"))

        with self.assertRaisesRegex(ValueError, "file-backed"):
            image.vaddr_to_offset(0x1003, 2)

    def test_rejects_truncated_header_table_and_segment(self) -> None:
        original = _elf32(b"ABCD")
        for data in (original[:40], original[:70], original[:-1]):
            with self.subTest(length=len(data)), self.assertRaises(ElfFormatError):
                Elf32Image.from_bytes(data)

    def test_rejects_load_segment_larger_than_memory_size(self) -> None:
        original = bytearray(_elf32(b"ABCD"))
        struct.pack_into("<I", original, 52 + 20, 3)
        with self.assertRaisesRegex(ElfFormatError, "memory size"):
            Elf32Image.from_bytes(bytes(original))

    def test_analyzer_rejects_non_arm_machine(self) -> None:
        original = bytearray(_elf32(b"ABCD"))
        struct.pack_into("<H", original, 18, 3)
        with self.assertRaisesRegex(ElfFormatError, "not ARM"):
            ArmElfAnalyzer(Elf32Image.from_bytes(bytes(original)))


class ArmElfAnalyzerTests(unittest.TestCase):
    def test_cli_reports_undecoded_tail_instead_of_silent_success(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "synthetic.elf"
            image.write_bytes(_elf32(bytes.fromhex("1eff2fe1ffffffff")))
            stderr = StringIO()
            argv = ["arm_elf_analysis", "disasm", str(image),
                    "--start", "0x1000", "--end", "0x1008"]
            with mock.patch("sys.argv", argv), redirect_stdout(StringIO()), redirect_stderr(stderr):
                self.assertEqual(main(), 2)
            self.assertIn("Undecoded bytes remain", stderr.getvalue())

    def test_disassembles_arm_and_thumb_with_explicit_mode(self) -> None:
        arm = ArmElfAnalyzer(Elf32Image.from_bytes(_elf32(b"\x1e\xff\x2f\xe1")))
        thumb = ArmElfAnalyzer(Elf32Image.from_bytes(_elf32(b"\x00\xb5\x70\x47")))

        self.assertEqual(arm.disassemble(0x1000, 0x1004)[0].mnemonic, "bx")
        self.assertEqual(thumb.disassemble(0x1000, 0x1004, thumb=True)[0].mnemonic, "push")

    def test_finds_direct_arm_callers(self) -> None:
        payload = b"\x10\x40\x2d\xe9" + _arm_bl(0x1004, 0x1020) + b"\x1e\xff\x2f\xe1"
        analyzer = ArmElfAnalyzer(Elf32Image.from_bytes(_elf32(payload.ljust(0x24, b"\x00"))))

        callers = analyzer.direct_callers(0x1020)

        self.assertEqual([instruction.address for instruction in callers], [0x1004])

    def test_direct_arm_blx_preserves_halfword_destination(self) -> None:
        analyzer = ArmElfAnalyzer(Elf32Image.from_bytes(_elf32(
            struct.pack("<I", 0xFB000000))))
        self.assertEqual([i.address for i in analyzer.direct_callers(0x100B)], [0x1000])
        self.assertEqual(analyzer.direct_callers(0x1008), [])

    def test_thumb_call_scan_continues_after_invalid_encoding(self) -> None:
        analyzer = ArmElfAnalyzer(Elf32Image.from_bytes(_elf32(
            bytes.fromhex("ffff00f00df8"))))
        self.assertEqual([i.address for i in analyzer.direct_callers(0x1021, thumb=True)],
                         [0x1002])

    def test_arm_scans_align_virtual_addresses_not_segment_start(self) -> None:
        payload = b"\0" * 3 + _arm_bl(0x1004, 0x1020)
        analyzer = ArmElfAnalyzer(Elf32Image.from_bytes(_elf32(payload, vaddr=0x1001)))
        self.assertEqual([i.address for i in analyzer.direct_callers(0x1020)], [0x1004])

    def test_finds_nearest_arm_function_prologue(self) -> None:
        payload = b"\x00\x00\xa0\xe1" + b"\x10\x40\x2d\xe9" + b"\x00\x00\xa0\xe1"
        analyzer = ArmElfAnalyzer(Elf32Image.from_bytes(_elf32(payload)))

        self.assertEqual(analyzer.nearest_function_start(0x100B), 0x1004)

    def test_resolves_pc_relative_ldr_literal(self) -> None:
        payload = b"\x04\x00\x9f\xe5" + b"\x1e\xff\x2f\xe1" + b"\x00" * 4
        payload += struct.pack("<I", 0xDEADBEEF)
        analyzer = ArmElfAnalyzer(Elf32Image.from_bytes(_elf32(payload)))
        instruction = analyzer.disassemble(0x1000, 0x1004)[0]

        literal_address, value = analyzer.resolve_pc_literal(instruction)

        self.assertEqual(literal_address, 0x100C)
        self.assertEqual(value, 0xDEADBEEF)

    def test_finds_nul_terminated_ascii_string_virtual_addresses(self) -> None:
        analyzer = ArmElfAnalyzer(
            Elf32Image.from_bytes(_elf32(b"prefix\x00application_skuid\x00suffix"))
        )

        self.assertEqual(analyzer.find_ascii("application_skuid"), [0x1007])

    def test_immediates_exclude_movt_encoding_false_positive(self) -> None:
        payload = struct.pack("<III", 0xE3A01FA1, 0xE3421FA0, 0xE3001284)
        analyzer = ArmElfAnalyzer(Elf32Image.from_bytes(_elf32(payload)))
        self.assertEqual([i.address for i in analyzer.immediate_candidates(0x284)],
                         [0x1000, 0x1008])
        self.assertEqual(list(analyzer.immediate_candidates(0x280)), [])

    def test_strings_return_start_of_containing_string(self) -> None:
        analyzer = ArmElfAnalyzer(Elf32Image.from_bytes(
            _elf32(b"\0Invalid sku_intervals\0abc\0")))
        self.assertEqual(list(analyzer.ascii_strings("sku")),
                         [(0x1001, "Invalid sku_intervals")])

    def test_offset_loads_exclude_pc_byte_and_postindex(self) -> None:
        payload = struct.pack("<IIII", 0xE5901010, 0xE5D01010, 0xE4901010, 0xE59F1010)
        analyzer = ArmElfAnalyzer(Elf32Image.from_bytes(_elf32(payload)))
        self.assertEqual([i.address for i in analyzer.virtual_selector_loads(0x10)],
                         [0x1000])

    def test_conditional_negative_pc_literal(self) -> None:
        payload = struct.pack("<II", 0x12345678, 0x051F000C)
        analyzer = ArmElfAnalyzer(Elf32Image.from_bytes(_elf32(payload)))
        self.assertEqual(analyzer.resolve_pc_literal(analyzer.disassemble(0x1004, 0x1008)[0]),
                         (0x1000, 0x12345678))

    def test_wide_thumb_literal_uses_thumb_pc_bias(self) -> None:
        payload = bytes.fromhex("dff80400") + b"\0" * 4 + struct.pack("<I", 123)
        analyzer = ArmElfAnalyzer(Elf32Image.from_bytes(_elf32(payload)))
        self.assertEqual(analyzer.resolve_pc_literal(
            analyzer.disassemble(0x1000, 0x1004, thumb=True)[0]), (0x1008, 123))

    def test_register_indexed_pc_load_is_not_a_static_literal(self) -> None:
        analyzer = ArmElfAnalyzer(Elf32Image.from_bytes(_elf32(
            struct.pack("<III", 0xE79F0001, 0, 123))))
        with self.assertRaisesRegex(ValueError, "static"):
            analyzer.resolve_pc_literal(analyzer.disassemble(0x1000, 0x1004)[0])

    def test_memory_offsets_support_sign_and_exclude_pc_and_writeback(self) -> None:
        payload = struct.pack("<IIIIII", 0xE5101024, 0xE5901024, 0xE5801024,
                              0xE59F1024, 0xE4901024, 0xE5D01024)
        analyzer = ArmElfAnalyzer(Elf32Image.from_bytes(_elf32(payload)))
        self.assertEqual([i.address for i in analyzer.memory_offsets(-0x24, "ldr")],
                         [0x1000])
        self.assertEqual([i.address for i in analyzer.memory_offsets(0x24, "ldr")],
                         [0x1004, 0x1014])
        self.assertEqual([i.address for i in analyzer.memory_offsets(0x24, "str")],
                         [0x1008])

    def test_ascii_reads_are_bounded_at_segment_end(self) -> None:
        analyzer = ArmElfAnalyzer(Elf32Image.from_bytes(_elf32(b"abc")))
        self.assertEqual(analyzer.read_ascii(0x1001), "bc")
        self.assertEqual(analyzer.read_ascii(0x1000, 1), "a")


if __name__ == "__main__":
    unittest.main()
