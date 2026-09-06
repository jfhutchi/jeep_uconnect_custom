import struct
import unittest

from analysis_tools.arm_elf_analysis import ArmElfAnalyzer, Elf32Image, ElfFormatError
from analysis_tools.tests.test_arm_elf_analysis import _elf32


def import_fixture():
    payload = bytearray(0x100)
    struct.pack_into('<III', payload, 0, 0xE28FC000, 0xE28CC000, 0xE5BCF018)
    data = bytearray(_elf32(bytes(payload)))
    names = b'\0example_write\0'
    names_offset = len(data)
    data.extend(names)
    symbols_offset = len(data)
    data.extend(bytes(16) + struct.pack('<IIIBBH', 1, 0, 0, 0x12, 0, 0))
    reloc_offset = len(data)
    data.extend(struct.pack('<II', 0x1020, (1 << 8) | 22))
    sections_offset = len(data)
    data.extend(bytes(40))
    for kind, offset, size, link, entsize in (
        (3, names_offset, len(names), 0, 0),
        (11, symbols_offset, 32, 1, 16),
        (9, reloc_offset, 8, 2, 8),
    ):
        data.extend(struct.pack('<10I', 0, kind, 0, 0, offset, size, link, 0, 4, entsize))
    struct.pack_into('<I', data, 32, sections_offset)
    struct.pack_into('<HH', data, 46, 40, 4)
    return data, reloc_offset, sections_offset


class ImportTests(unittest.TestCase):
    def test_resolves_rel_symbol_and_arm_plt_without_executing_target(self):
        self.assertTrue(hasattr(ArmElfAnalyzer, 'plt_imports'), 'PLT resolver missing')
        data, _, _ = import_fixture()
        analyzer = ArmElfAnalyzer(Elf32Image.from_bytes(bytes(data)))
        self.assertEqual(analyzer.plt_imports(), {0x1000: (0x1020, 'example_write')})

    def test_ignores_non_jump_slot_and_non_matching_plt(self):
        self.assertTrue(hasattr(ArmElfAnalyzer, 'plt_imports'), 'PLT resolver missing')
        data, reloc_offset, _ = import_fixture()
        struct.pack_into('<I', data, reloc_offset + 4, (1 << 8) | 2)
        self.assertEqual(ArmElfAnalyzer(Elf32Image.from_bytes(bytes(data))).plt_imports(), {})
        data, _, _ = import_fixture()
        struct.pack_into('<I', data, 0x104, 0xE28C0000)
        self.assertEqual(ArmElfAnalyzer(Elf32Image.from_bytes(bytes(data))).plt_imports(), {})

    def test_rejects_bad_section_links_and_symbol_indices(self):
        self.assertTrue(hasattr(ArmElfAnalyzer, 'plt_imports'), 'PLT resolver missing')
        data, reloc_offset, section_offset = import_fixture()
        for offset, value in ((reloc_offset + 4, (99 << 8) | 22),
                              (section_offset + 3 * 40 + 24, 99),
                              (32, len(data))):
            damaged = bytearray(data)
            struct.pack_into('<I', damaged, offset, value)
            with self.subTest(offset=offset), self.assertRaises(ElfFormatError):
                ArmElfAnalyzer(Elf32Image.from_bytes(bytes(damaged))).plt_imports()

    def test_no_sections_has_no_imports(self):
        analyzer = ArmElfAnalyzer(Elf32Image.from_bytes(_elf32(bytes(12))))
        self.assertEqual(analyzer.plt_imports(), {})

    def test_rotated_arm_immediates_and_truncated_stub(self):
        data, reloc_offset, _ = import_fixture()
        struct.pack_into('<III', data, 0x100, 0xE28FC601, 0xE28CCA01, 0xE5BCF018)
        slot = 0x1008 + 0x100000 + 0x1000 + 0x18
        struct.pack_into('<I', data, reloc_offset, slot)
        self.assertEqual(ArmElfAnalyzer(Elf32Image.from_bytes(bytes(data))).plt_imports(),
                         {0x1000: (slot, 'example_write')})
        struct.pack_into('<I', data, 52 + 16, 4)
        self.assertEqual(ArmElfAnalyzer(Elf32Image.from_bytes(bytes(data))).plt_imports(), {})

    def test_rejects_unterminated_name_and_bad_entry_sizes(self):
        data, _, section_offset = import_fixture()
        for offset, value in ((section_offset + 40 + 20, 5),
                              (section_offset + 3 * 40 + 36, 0),
                              (section_offset + 2 * 40 + 36, 8)):
            damaged = bytearray(data)
            struct.pack_into('<I', damaged, offset, value)
            with self.subTest(offset=offset), self.assertRaises(ElfFormatError):
                ArmElfAnalyzer(Elf32Image.from_bytes(bytes(damaged))).plt_imports()


if __name__ == '__main__':
    unittest.main()
