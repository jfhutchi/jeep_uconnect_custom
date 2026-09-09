"""Synthetic, firmware-free checks for explicit Jamaica registration ranges."""

import struct
import unittest
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
import json
from unittest import mock

from analysis_tools.arm_elf_analysis import Elf32Image, ProgramSegment
from analysis_tools.jamaica_aot_registry import main, read_registry


def fixture():
    blob = bytearray(0x300)
    struct.pack_into('<6I', blob, 0x100, 0, 0x9080, 0, 7, 0x9020, 2)
    struct.pack_into('<8I', blob, 0x120, 1, 0x9084, 0, 0, 3, 0x4000, 0x4004, 0)
    struct.pack_into('<8I', blob, 0x140, 2, 0x9088, 0, 0, 5, 0, 0, 0)
    return Elf32Image(bytes(blob), 2, 40, 0x4000, 0, (
        ProgramSegment(1, 0x80, 0x4000, 0x4000, 0x20, 0x20, 5, 4),
        ProgramSegment(1, 0x100, 0x9000, 0x9000, 0x80, 0x100, 6, 4),
    ))


def changed(image, offset, value):
    blob = bytearray(image.data)
    struct.pack_into('<I', blob, offset, value)
    return Elf32Image(bytes(blob), image.elf_type, image.machine, image.entry,
                      image.flags, image.program_segments)


class RegistryTests(unittest.TestCase):
    def test_translates_each_load_segment_and_keeps_null_entry(self):
        result = read_registry(fixture(), 0x9000, 1)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].class_slot, 7)
        self.assertEqual(result[0].file_offset, 0x100)
        first, second = result[0].members
        self.assertEqual((first.kind, first.member_ordinal, first.file_offset), ('method', 3, 0x120))
        self.assertEqual((first.adapter_va, first.function_va), (0x4000, 0x4004))
        self.assertEqual((first.adapter_offset, first.function_offset), (0x80, 0x84))
        self.assertEqual((second.kind, second.member_ordinal), ('field', 5))
        self.assertIsNone(second.function_offset)

    def test_rejects_method_array_in_unbacked_bss(self):
        with self.assertRaisesRegex(ValueError, 'file-backed'):
            read_registry(changed(fixture(), 0x110, 0x9080), 0x9000, 1)

    def test_rejects_nonexecutable_function(self):
        with self.assertRaisesRegex(ValueError, 'executable'):
            read_registry(changed(fixture(), 0x138, 0x9060), 0x9000, 1)

    def test_rejects_one_sided_adapter_function_pair(self):
        with self.assertRaisesRegex(ValueError, 'pair'):
            read_registry(changed(fixture(), 0x134, 0), 0x9000, 1)

    def test_rejects_unknown_reserved_words(self):
        for offset in (0x108, 0x128, 0x12c, 0x13c):
            with self.subTest(offset=offset), self.assertRaisesRegex(ValueError, 'reserved'):
                read_registry(changed(fixture(), offset, 1), 0x9000, 1)

    def test_rejects_duplicate_method_ordinals(self):
        image = changed(changed(fixture(), 0x140, 1), 0x150, 3)
        with self.assertRaisesRegex(ValueError, 'duplicate member'):
            read_registry(image, 0x9000, 1)

    def test_preserves_field_and_method_with_same_ordinal(self):
        rows = read_registry(changed(fixture(), 0x150, 3), 0x9000, 1)[0].members
        self.assertEqual([(r.kind, r.member_ordinal) for r in rows], [('method', 3), ('field', 3)])

    def test_rejects_unbounded_or_negative_counts(self):
        for count in (-1, 100_001):
            with self.subTest(count=count), self.assertRaises(ValueError):
                read_registry(fixture(), 0x9000, count)
        with self.assertRaisesRegex(ValueError, 'member limit'):
            read_registry(fixture(), 0x9000, 1, max_members=1)

    def test_keeps_a_class_with_no_method_array(self):
        image = changed(changed(fixture(), 0x110, 0), 0x114, 0)
        self.assertEqual(read_registry(image, 0x9000, 1)[0].members, ())

    def test_rejects_unknown_member_kind_and_field_function(self):
        for kind, message in [(0, 'member kind'), (2, 'field record')]:
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, message):
                read_registry(changed(fixture(), 0x120, kind), 0x9000, 1)

    def test_cli_filters_and_reports_complete_range_counts(self):
        stdout = StringIO()
        with mock.patch('sys.argv', ['registry', 'synthetic.elf', '--registry-va', '0x9000',
                                     '--class-count', '1', '--class-slot', '7']), \
                mock.patch.object(Elf32Image, 'from_path', return_value=fixture()), \
                redirect_stdout(stdout):
            self.assertEqual(main(), 0)
        result = json.loads(stdout.getvalue())
        self.assertEqual((result['member_count'], result['method_count'], result['field_count']), (2, 1, 1))
        self.assertEqual(result['compiled_method_count'], 1)
        self.assertEqual(result['classes'][0]['class_slot'], 7)

    def test_cli_absent_class_fails_without_success_json(self):
        stdout, stderr = StringIO(), StringIO()
        with mock.patch('sys.argv', ['registry', 'synthetic.elf', '--registry-va', '0x9000',
                                     '--class-count', '1', '--class-slot', '8']), \
                mock.patch.object(Elf32Image, 'from_path', return_value=fixture()), \
                redirect_stdout(stdout), redirect_stderr(stderr), \
                self.assertRaises(SystemExit) as error:
            main()
        self.assertEqual(error.exception.code, 2)
        self.assertEqual(stdout.getvalue(), '')
        self.assertIn('absent from range', stderr.getvalue())


if __name__ == '__main__':
    unittest.main()
