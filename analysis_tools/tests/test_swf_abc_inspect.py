import struct
import unittest
import zlib
from analysis_tools.swf_abc_inspect import Reader, abc_tags, parse_abc, disassemble


def synthetic_abc():
    # Empty pools, one void method, no classes, one script and one returnvoid body.
    return (struct.pack('<HH', 16, 46) + bytes([1] * 7)
            + bytes([1, 0, 0, 0, 0, 0, 0, 1, 0, 0,
                     1, 0, 0, 1, 0, 0, 1, 0x47, 0, 0]))


def swf(compressed=False):
    payload = b'\0' * 4 + b'test\0' + synthetic_abc()
    body = b'\x08\0\0\0\0\0' + struct.pack('<H', (82 << 6) | len(payload)) + payload + b'\0\0'
    return ((b'CWS' if compressed else b'FWS') + b'\x0a'
            + struct.pack('<I', len(body) + 8) + (zlib.compress(body) if compressed else body))


class AbcTests(unittest.TestCase):
    def test_fws_and_cws_offsets(self):
        for compressed in (False, True):
            tags = abc_tags(swf(compressed))
            self.assertEqual(tags[0][0], 25)
            abc = parse_abc(tags[0][1], tags[0][0])
            self.assertEqual(abc['bodies'][0]['code'], b'\x47')

    def test_reject_truncated_and_trailing_swf(self):
        for data in (swf()[:-1], swf() + b'x', swf(True)[:-2], swf(True) + b'x'):
            with self.assertRaises(ValueError):
                abc_tags(data)

    def test_integer_limits(self):
        self.assertEqual(Reader(b'\xff\xff\xff\xff\x03').u30(), (1 << 30) - 1)
        for data in (b'\x80', b'\xff\xff\xff\xff\x04', b'\x80' * 5):
            with self.assertRaises(ValueError):
                Reader(data).u30()

    def test_all_abc_truncations(self):
        data = synthetic_abc()
        for end in range(len(data)):
            with self.subTest(end=end), self.assertRaises(ValueError):
                parse_abc(data[:end])
        with self.assertRaises(ValueError):
            parse_abc(data + b'x')

    def test_operand_alignment_and_branch(self):
        abc = parse_abc(synthetic_abc())
        abc['bodies'][0] = {'offset': 100, 'code': bytes([
            0x24, 255, 0x23, 0x10, 0xfc, 0xff, 0xff, 0x47])}
        lines = list(disassemble(abc, 0))
        self.assertEqual([offset for offset, _ in lines], [100, 102, 103, 107])
        self.assertIn('[-1]', lines[0][1])
        self.assertIn('nextvalue', lines[1][1])
        self.assertIn('-> 0x67', lines[2][1])

    def test_unknown_opcode_fails_closed(self):
        abc = parse_abc(synthetic_abc())
        abc['bodies'][0]['code'] = b'\xff'
        with self.assertRaisesRegex(ValueError, 'unsupported opcode'):
            list(disassemble(abc, 0))

    def test_declared_size_cap(self):
        data = swf(True)
        with self.assertRaises(ValueError):
            abc_tags(data[:4] + struct.pack('<I', 100_000_000) + data[8:])

    def test_named_class_typed_getter_and_optional_parameter(self):
        strings = [b'pkg', b'Thing', b'value', b'String', b'argument']
        pools = (bytes([1, 1, 1, 6])
                 + b''.join(bytes([len(s)]) + s for s in strings)
                 + bytes([2, 0x16, 1, 1, 4,
                          7, 1, 2, 7, 1, 3, 7, 1, 4]))
        # Three methods: initializer, getter, and static initializer. The
        # getter is parameterless; a fourth method tests optional/parameter names.
        methods = bytes([4, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0,
                         1, 3, 3, 0, 0x88, 1, 0, 0x0a, 5])
        classes = bytes([0, 1, 1, 0, 0, 0, 0, 1, 2, 2, 0, 1, 2, 0, 0])
        bodies = bytes([1, 1, 1, 1, 0, 0, 3, 0x2c, 4, 0x48, 0, 0])
        abc = parse_abc(struct.pack('<HH', 16, 46) + pools + methods + classes + bodies)
        self.assertEqual(abc['methods'][1]['owners'], ['pkg::Thing/pkg::value [get]'])
        self.assertEqual(abc['methods'][1]['returns'], 'pkg::String')
        self.assertEqual(abc['methods'][3]['params'], ['pkg::String'])
        self.assertEqual(abc['methods'][3]['returns'], 'pkg::String')
        self.assertIn("'String'", list(disassemble(abc, 1))[0][1])


if __name__ == '__main__':
    unittest.main()
