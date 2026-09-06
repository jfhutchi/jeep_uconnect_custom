import importlib.util
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest
import zipfile

from analysis_tools.tests.test_elf32_imports import import_fixture
from analysis_tools.tests.test_arm_elf_analysis import _elf32


class UsbInventoryTests(unittest.TestCase):
    def api(self):
        self.assertIsNotNone(importlib.util.find_spec('analysis_tools.qnx_usb_inventory'),
                             'structured USB inventory is not implemented')
        from analysis_tools.qnx_usb_inventory import inventory, elf_metadata
        return inventory, elf_metadata

    def test_dynamic_symbol_is_an_import_not_an_export(self):
        _, metadata = self.api()
        data, _, _ = import_fixture()
        # The fixture has no section names, just like stripped section metadata.
        result = metadata(io.BytesIO(data))
        self.assertEqual(result['machine'], 'EM_ARM')
        self.assertEqual(result['imports'], ['example_write'])
        self.assertEqual(result['exports'], [])

    def test_defined_symbol_is_an_export(self):
        _, metadata = self.api()
        data, _, sections = import_fixture()
        symbols_offset = struct.unpack_from('<I', data, sections + 2 * 40 + 16)[0]
        struct.pack_into('<H', data, symbols_offset + 16 + 14, 1)
        result = metadata(io.BytesIO(data))
        self.assertEqual(result['imports'], [])
        self.assertEqual(result['exports'], ['example_write'])

    def test_program_dynamic_table_survives_removed_section_headers(self):
        _, metadata = self.api()
        payload = bytearray(0x140)
        strings = b'\0usbd_setup_vendor\0libc.so.3\0'
        payload[0x80:0x80 + len(strings)] = strings
        struct.pack_into('<IIIBBH', payload, 0xD0, 1, 0x1120, 4, 0x12, 0, 1)
        struct.pack_into('<IIIII', payload, 0x110, 1, 2, 1, 0, 0)
        tags = [(5, 0x1080), (10, len(strings)), (6, 0x10C0), (11, 16),
                (4, 0x1110), (1, strings.index(b'libc')), (0, 0)]
        for i, pair in enumerate(tags):
            struct.pack_into('<II', payload, 8 * i, *pair)
        data = bytearray(_elf32(payload))
        struct.pack_into('<H', data, 44, 2)
        struct.pack_into('<8I', data, 84, 2, 0x100, 0x1000, 0x1000, 56, 56, 4, 4)
        result = metadata(io.BytesIO(data))
        self.assertEqual(result['needed'], ['libc.so.3'])
        self.assertEqual(result['exports'], ['usbd_setup_vendor'])
        self.assertEqual(result['dynamic_symbol_tables'], 1)

    def test_names_and_archive_members_do_not_become_runtime_proof(self):
        inventory, _ = self.api()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'device-stack-notes.txt').write_text('io-usb-dcd SECRET_PAYLOAD')
            with zipfile.ZipFile(root / 'optional.jar', 'w') as archive:
                archive.writestr('docs/io-usb-dcd.txt', 'SECRET_PAYLOAD')
                archive.writestr('lib/devu-dcd-example.so', 'SECRET_PAYLOAD')
            result = inventory([root])
            self.assertEqual(result['totals']['files'], 2)
            self.assertEqual(result['totals']['elf_files'], 0)
            self.assertEqual(result['totals']['archive_members'], 2)
            self.assertEqual(len(result['archive_name_candidates']), 2)
            self.assertNotIn('SECRET_PAYLOAD', json.dumps(result))
            self.assertEqual(result['elf_candidates'], [])

    def test_absent_root_and_malformed_elf_fail_loudly(self):
        inventory, _ = self.api()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaises(FileNotFoundError):
                inventory([root / 'missing'])
            (root / 'devu-broken.so').write_bytes(b'\x7fELF' + bytes(16))
            with self.assertRaises(ValueError):
                inventory([root])


if __name__ == '__main__':
    unittest.main()
