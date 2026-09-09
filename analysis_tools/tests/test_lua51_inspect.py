import struct
import unittest
from analysis_tools.lua51_inspect import parse, instruction


def chunk():
    u = lambda n: struct.pack('<I', n)
    # Synthetic empty-source prototype with one LOADK, one string, one debug line.
    return (b'\x1bLua\x51\x00\x01\x04\x04\x04\x08\x00' + u(0) + u(1) + u(2)
            + bytes([0, 0, 0, 2]) + u(1) + u(1) + u(1) + b'\x04' + u(5)
            + b'temp\0' + u(0) + u(1) + u(1) + u(0) + u(0))


class LuaTests(unittest.TestCase):
    def test_synthetic_chunk(self):
        functions = parse(chunk())
        self.assertEqual(functions[0]['constants'][0]['value'], 'temp')
        self.assertIn("'temp'", instruction(functions[0], 0))

    def test_truncation_and_header(self):
        for data in [chunk()[:-1], b'not lua', chunk() + b'x']:
            with self.assertRaises(ValueError):
                parse(data)

    def test_every_truncated_prefix(self):
        for end in range(len(chunk())):
            with self.subTest(end=end), self.assertRaises(ValueError):
                parse(chunk()[:end])

    def test_branch_and_rk_annotations(self):
        f = parse(chunk())[0]
        f['code'] = [22 | ((131071 - 1) << 14)]
        self.assertIn('-> PC 0', instruction(f, 0))
        f['code'] = [6 | (256 << 14)]
        self.assertIn("K0='temp'", instruction(f, 0))


if __name__ == '__main__':
    unittest.main()
