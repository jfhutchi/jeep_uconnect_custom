import struct
import unittest

from analysis_tools.java_classfile import decode_instructions, parse_class


class Pool:
    def __init__(self):
        self.entries = []

    def add(self, data):
        self.entries.append(data)
        return len(self.entries)

    def utf(self, value):
        raw = value.encode("utf-8")
        return self.add(b"\x01" + struct.pack(">H", len(raw)) + raw)

    def class_(self, name):
        return self.add(b"\x07" + struct.pack(">H", self.utf(name)))

    def name_type(self, name, descriptor):
        return self.add(
            b"\x0c" + struct.pack(">HH", self.utf(name), self.utf(descriptor))
        )

    def fieldref(self, owner, name, descriptor):
        return self.add(
            b"\x09"
            + struct.pack(">HH", self.class_(owner), self.name_type(name, descriptor))
        )

    def methodref(self, owner, name, descriptor, interface=False):
        return self.add(
            bytes([11 if interface else 10])
            + struct.pack(">HH", self.class_(owner), self.name_type(name, descriptor))
        )

    def build(self):
        return struct.pack(">H", len(self.entries) + 1) + b"".join(self.entries)


def u2(value):
    return struct.pack(">H", value)


def member(pool, name, descriptor, code=None, access=0x0001, exceptions=()):
    header = struct.pack(">HHH", access, pool.utf(name), pool.utf(descriptor))
    if code is None:
        return header + u2(0)
    body = struct.pack(">HHI", 4, 4, len(code)) + code
    body += u2(len(exceptions))
    for start, end, handler, catch_type in exceptions:
        body += struct.pack(">HHHH", start, end, handler, catch_type)
    body += u2(0)
    return header + u2(1) + struct.pack(">HI", pool.utf("Code"), len(body)) + body


def class_fixture():
    pool = Pool()
    this_class = pool.class_("example/Server")
    super_class = pool.class_("java/lang/Object")
    runnable = pool.class_("java/lang/Runnable")
    port_ref = pool.fieldref("example/Server", "port", "I")
    server_ref = pool.fieldref(
        "example/Server", "server", "Ljava/net/ServerSocket;"
    )
    object_init = pool.methodref("java/lang/Object", "<init>", "()V")
    server_socket = pool.class_("java/net/ServerSocket")
    socket_init = pool.methodref("java/net/ServerSocket", "<init>", "(I)V")
    pool.methodref("example/Unused", "unusedDecoy", "()V")

    constructor = (
        b"\x2a\xb7" + u2(object_init)
        + b"\x2a\x1b\xb5" + u2(port_ref)
        + b"\xb1"
    )
    run = (
        b"\xbb" + u2(server_socket)
        + b"\x59\x2a\xb4" + u2(port_ref)
        + b"\xb7" + u2(socket_init)
        + b"\x4c\x2a\x2b\xb5" + u2(server_ref)
        + b"\xb1"
    )
    fields = (
        member(pool, "port", "I", access=0x0012),
        member(pool, "server", "Ljava/net/ServerSocket;", access=0x0012),
    )
    methods = (
        member(pool, "<init>", "(I)V", constructor),
        member(pool, "run", "()V", run, exceptions=((0, len(run) - 1, len(run) - 1, 0),)),
        member(pool, "nativeEntry", "()V", access=0x0101),
    )
    return (
        bytes.fromhex("cafebabe00000031")
        + pool.build()
        + struct.pack(">HHHH", 0x0021, this_class, super_class, 1)
        + u2(runnable)
        + u2(len(fields)) + b"".join(fields)
        + u2(len(methods)) + b"".join(methods)
        + u2(0)
    )


class JavaClassfileTests(unittest.TestCase):
    def test_parses_structure_fields_methods_and_real_bytecode_edges(self):
        model = parse_class(class_fixture())
        self.assertEqual((model.minor_version, model.major_version), (0, 49))
        self.assertEqual(model.name, "example/Server")
        self.assertEqual(model.super_name, "java/lang/Object")
        self.assertEqual(model.interfaces, ("java/lang/Runnable",))
        self.assertEqual(
            [(field.name, field.descriptor) for field in model.fields],
            [("port", "I"), ("server", "Ljava/net/ServerSocket;")],
        )
        constructor = model.method("<init>", "(I)V")
        self.assertEqual(
            [(edge.kind, edge.owner, edge.name) for edge in constructor.member_edges],
            [
                ("invoke_special", "java/lang/Object", "<init>"),
                ("field_write", "example/Server", "port"),
            ],
        )
        run = model.method("run", "()V")
        self.assertEqual(
            [(instruction.offset, instruction.mnemonic) for instruction in run.instructions],
            [
                (0, "new"), (3, "dup"), (4, "aload_0"), (5, "getfield"),
                (8, "invokespecial"), (11, "astore_1"), (12, "aload_0"),
                (13, "aload_1"), (14, "putfield"), (17, "return"),
            ],
        )
        self.assertEqual([edge.name for edge in run.member_edges], ["port", "<init>", "server"])
        self.assertEqual(
            [(edge.kind, edge.owner) for edge in run.type_edges],
            [("construct", "java/net/ServerSocket")],
        )
        self.assertNotIn("unusedDecoy", [edge.name for edge in run.member_edges])
        self.assertEqual(len(run.exception_handlers), 1)
        self.assertTrue(model.method("nativeEntry", "()V").is_native)
        self.assertEqual(model.method("nativeEntry", "()V").instructions, ())

    def test_decodes_switch_wide_and_five_byte_invocations(self):
        table = b"\xaa\x00\x00\x00" + struct.pack(">iii", 20, 1, 2) + struct.pack(">ii", 4, 12)
        instructions = decode_instructions(table)
        self.assertEqual(instructions[0].mnemonic, "tableswitch")
        self.assertEqual(instructions[0].target_offsets, (20, 4, 12))

        lookup = b"\xab\x00\x00\x00" + struct.pack(">ii", 16, 2) + struct.pack(">iiii", 3, 4, 9, 12)
        instructions = decode_instructions(lookup)
        self.assertEqual(instructions[0].mnemonic, "lookupswitch")
        self.assertEqual(instructions[0].target_offsets, (16, 4, 12))

        code = b"\xc4\x84\x00\x02\x00\x05\xb9\x00\x01\x01\x00\xba\x00\x02\x00\x00\xb1"
        instructions = decode_instructions(code)
        self.assertEqual(
            [(item.offset, item.mnemonic, item.operands) for item in instructions],
            [
                (0, "wide", (0x84, 2, 5)),
                (6, "invokeinterface", (1, 1, 0)),
                (11, "invokedynamic", (2, 0, 0)),
                (16, "return", ()),
            ],
        )

    def test_rejects_bad_magic_truncation_and_invalid_switch(self):
        with self.assertRaisesRegex(ValueError, "magic"):
            parse_class(b"not a class")
        fixture = class_fixture()
        for cut in (4, 10, len(fixture) - 1):
            with self.subTest(cut=cut), self.assertRaises(ValueError):
                parse_class(fixture[:cut])
        with self.assertRaisesRegex(ValueError, "tableswitch"):
            decode_instructions(b"\xaa\x00")

    def test_class_size_limit_fails_closed(self):
        fixture = class_fixture()
        with self.assertRaisesRegex(ValueError, "size limit"):
            parse_class(fixture, max_class_bytes=len(fixture) - 1)


if __name__ == "__main__":
    unittest.main()
