import io
import re
import struct
import unittest
import zipfile

from analysis_tools.jvm_call_inventory import inspect_class, inspect_jar


def class_fixture(code=b'\xb8\x00\x0c\xb1'):
    def utf(value):
        data = value.encode('ascii')
        return b'\x01' + struct.pack('>H', len(data)) + data

    pool = [utf('Example'), b'\x07\x00\x01', utf('java/lang/Object'),
            b'\x07\x00\x03', utf('run'), utf('()V'), utf('Code'),
            utf('example/View'), b'\x07\x00\x08', utf('show'),
            b'\x0c\x00\x0a\x00\x06', b'\x0a\x00\x09\x00\x0b']
    body = struct.pack('>HHI', 1, 0, len(code)) + code + bytes(4)
    return (bytes.fromhex('cafebabe00000032') + struct.pack('>H', len(pool) + 1)
            + b''.join(pool) + struct.pack('>7H', 0x21, 2, 4, 0, 0, 1, 9)
            + struct.pack('>HHHHI', 5, 6, 1, 7, len(body)) + body + bytes(2))


class JvmCallInventoryTests(unittest.TestCase):
    def test_resolves_actual_invocation_and_caller_signature(self):
        result = inspect_class(class_fixture(), re.compile('example/View'), re.compile('show'))
        self.assertEqual(result['class'], 'Example')
        self.assertEqual(result['calls'], [{'caller': 'run', 'caller_descriptor': '()V',
            'bci': 0, 'opcode': 'invokestatic', 'owner': 'example/View',
            'name': 'show', 'descriptor': '()V'}])

    def test_constant_pool_reference_alone_is_not_a_call(self):
        result = inspect_class(class_fixture(b'\xb1'), re.compile('.*'), re.compile('.*'))
        self.assertEqual(result['calls'], [])

    def test_instruction_operands_do_not_become_false_calls(self):
        # sipush's operands contain the same opcode/index prefix as the real call.
        result = inspect_class(class_fixture(b'\x11\xb8\x00\x57\xb1'),
                               re.compile('.*'), re.compile('.*'))
        self.assertEqual(result['calls'], [])

    def test_member_selection_reads_only_class_members(self):
        data = io.BytesIO()
        with zipfile.ZipFile(data, 'w') as jar:
            jar.writestr('Example.class', class_fixture())
            jar.writestr('resource.txt', 'not a class')
            jar.writestr('Ignored.class', b'invalid')
        data.seek(0)
        result = inspect_jar(data, re.compile('^Example.class$'), re.compile('.*'), re.compile('.*'))
        self.assertEqual(result['selected_classes'], 1)
        self.assertEqual(result['classes'][0]['member'], 'Example.class')

    def test_bad_magic_and_oversized_member_fail_explicitly(self):
        with self.assertRaisesRegex(ValueError, 'magic'):
            inspect_class(b'not a class', re.compile('.*'), re.compile('.*'))
        data = io.BytesIO()
        with zipfile.ZipFile(data, 'w') as jar:
            jar.writestr('Example.class', class_fixture())
        data.seek(0)
        with self.assertRaisesRegex(ValueError, 'size'):
            inspect_jar(data, re.compile('.*'), re.compile('.*'), re.compile('.*'), max_class_bytes=4)


if __name__ == '__main__':
    unittest.main()
