"""Bounded JVM classfile structure and bytecode reader.

This module parses bytes only.  It does not load, verify, initialize, link, or
execute Java classes.  Invocation records are syntactic bytecode references;
virtual and interface dispatch remain unresolved runtime choices.
"""

from __future__ import annotations

from dataclasses import dataclass
import struct
from typing import Any


@dataclass(frozen=True)
class Instruction:
    offset: int
    opcode: int
    mnemonic: str
    operands: tuple[int, ...] = ()
    target_offsets: tuple[int, ...] = ()


@dataclass(frozen=True)
class MemberEdge:
    offset: int
    kind: str
    owner: str
    name: str
    descriptor: str
    opcode: str
    cp_index: int


@dataclass(frozen=True)
class TypeEdge:
    offset: int
    kind: str
    owner: str
    opcode: str
    cp_index: int


@dataclass(frozen=True)
class LiteralEdge:
    offset: int
    kind: str
    value: Any
    opcode: str
    cp_index: int


@dataclass(frozen=True)
class ExceptionHandler:
    start_pc: int
    end_pc: int
    handler_pc: int
    catch_type: str | None


@dataclass(frozen=True)
class FieldModel:
    name: str
    descriptor: str
    access_flags: int
    constant_value: Any = None
    attributes: tuple[str, ...] = ()


@dataclass(frozen=True)
class MethodModel:
    name: str
    descriptor: str
    access_flags: int
    instructions: tuple[Instruction, ...]
    member_edges: tuple[MemberEdge, ...]
    type_edges: tuple[TypeEdge, ...]
    literal_edges: tuple[LiteralEdge, ...]
    exception_handlers: tuple[ExceptionHandler, ...]
    attributes: tuple[str, ...] = ()

    @property
    def is_native(self) -> bool:
        return bool(self.access_flags & 0x0100)

    @property
    def is_abstract(self) -> bool:
        return bool(self.access_flags & 0x0400)


@dataclass(frozen=True)
class ClassModel:
    minor_version: int
    major_version: int
    access_flags: int
    name: str
    super_name: str | None
    interfaces: tuple[str, ...]
    fields: tuple[FieldModel, ...]
    methods: tuple[MethodModel, ...]
    attributes: tuple[str, ...]
    utf8_constants: tuple[str, ...]
    string_constants: tuple[str, ...]
    class_references: tuple[str, ...]

    def method(self, name: str, descriptor: str) -> MethodModel:
        matches = [
            method for method in self.methods
            if method.name == name and method.descriptor == descriptor
        ]
        if len(matches) != 1:
            raise ValueError(
                f"expected one method {name}{descriptor}, found {len(matches)}"
            )
        return matches[0]


@dataclass(frozen=True)
class _CpEntry:
    tag: int
    value: Any


class _Reader:
    def __init__(self, data: bytes, description: str = "classfile"):
        self.data = data
        self.position = 0
        self.description = description

    def take(self, size: int) -> bytes:
        if size < 0 or self.position + size > len(self.data):
            raise ValueError(
                f"truncated {self.description} at 0x{self.position:x}: need {size} bytes"
            )
        result = self.data[self.position:self.position + size]
        self.position += size
        return result

    def u1(self) -> int:
        return self.take(1)[0]

    def u2(self) -> int:
        return struct.unpack(">H", self.take(2))[0]

    def u4(self) -> int:
        return struct.unpack(">I", self.take(4))[0]


_NAMES = {
    0x00: "nop", 0x01: "aconst_null", 0x02: "iconst_m1",
    0x03: "iconst_0", 0x04: "iconst_1", 0x05: "iconst_2",
    0x06: "iconst_3", 0x07: "iconst_4", 0x08: "iconst_5",
    0x09: "lconst_0", 0x0A: "lconst_1", 0x0B: "fconst_0",
    0x0C: "fconst_1", 0x0D: "fconst_2", 0x0E: "dconst_0",
    0x0F: "dconst_1", 0x10: "bipush", 0x11: "sipush", 0x12: "ldc",
    0x13: "ldc_w", 0x14: "ldc2_w", 0x15: "iload", 0x16: "lload",
    0x17: "fload", 0x18: "dload", 0x19: "aload", 0x1A: "iload_0",
    0x1B: "iload_1", 0x1C: "iload_2", 0x1D: "iload_3",
    0x1E: "lload_0", 0x1F: "lload_1", 0x20: "lload_2", 0x21: "lload_3",
    0x22: "fload_0", 0x23: "fload_1", 0x24: "fload_2", 0x25: "fload_3",
    0x26: "dload_0", 0x27: "dload_1", 0x28: "dload_2", 0x29: "dload_3",
    0x2A: "aload_0", 0x2B: "aload_1", 0x2C: "aload_2", 0x2D: "aload_3",
    0x2E: "iaload", 0x2F: "laload", 0x30: "faload", 0x31: "daload",
    0x32: "aaload", 0x33: "baload", 0x34: "caload", 0x35: "saload",
    0x36: "istore", 0x37: "lstore", 0x38: "fstore", 0x39: "dstore",
    0x3A: "astore", 0x3B: "istore_0", 0x3C: "istore_1",
    0x3D: "istore_2", 0x3E: "istore_3", 0x3F: "lstore_0",
    0x40: "lstore_1", 0x41: "lstore_2", 0x42: "lstore_3",
    0x43: "fstore_0", 0x44: "fstore_1", 0x45: "fstore_2",
    0x46: "fstore_3", 0x47: "dstore_0", 0x48: "dstore_1",
    0x49: "dstore_2", 0x4A: "dstore_3", 0x4B: "astore_0",
    0x4C: "astore_1", 0x4D: "astore_2", 0x4E: "astore_3",
    0x4F: "iastore", 0x50: "lastore", 0x51: "fastore", 0x52: "dastore",
    0x53: "aastore", 0x54: "bastore", 0x55: "castore", 0x56: "sastore",
    0x57: "pop", 0x58: "pop2", 0x59: "dup", 0x5A: "dup_x1",
    0x5B: "dup_x2", 0x5C: "dup2", 0x5D: "dup2_x1", 0x5E: "dup2_x2",
    0x5F: "swap", 0x60: "iadd", 0x61: "ladd", 0x62: "fadd",
    0x63: "dadd", 0x64: "isub", 0x65: "lsub", 0x66: "fsub",
    0x67: "dsub", 0x68: "imul", 0x69: "lmul", 0x6A: "fmul",
    0x6B: "dmul", 0x6C: "idiv", 0x6D: "ldiv", 0x6E: "fdiv",
    0x6F: "ddiv", 0x70: "irem", 0x71: "lrem", 0x72: "frem",
    0x73: "drem", 0x74: "ineg", 0x75: "lneg", 0x76: "fneg",
    0x77: "dneg", 0x78: "ishl", 0x79: "lshl", 0x7A: "ishr",
    0x7B: "lshr", 0x7C: "iushr", 0x7D: "lushr", 0x7E: "iand",
    0x7F: "land", 0x80: "ior", 0x81: "lor", 0x82: "ixor", 0x83: "lxor",
    0x84: "iinc", 0x85: "i2l", 0x86: "i2f", 0x87: "i2d",
    0x88: "l2i", 0x89: "l2f", 0x8A: "l2d", 0x8B: "f2i",
    0x8C: "f2l", 0x8D: "f2d", 0x8E: "d2i", 0x8F: "d2l",
    0x90: "d2f", 0x91: "i2b", 0x92: "i2c", 0x93: "i2s",
    0x94: "lcmp", 0x95: "fcmpl", 0x96: "fcmpg", 0x97: "dcmpl",
    0x98: "dcmpg", 0x99: "ifeq", 0x9A: "ifne", 0x9B: "iflt",
    0x9C: "ifge", 0x9D: "ifgt", 0x9E: "ifle", 0x9F: "if_icmpeq",
    0xA0: "if_icmpne", 0xA1: "if_icmplt", 0xA2: "if_icmpge",
    0xA3: "if_icmpgt", 0xA4: "if_icmple", 0xA5: "if_acmpeq",
    0xA6: "if_acmpne", 0xA7: "goto", 0xA8: "jsr", 0xA9: "ret",
    0xAA: "tableswitch", 0xAB: "lookupswitch", 0xAC: "ireturn",
    0xAD: "lreturn", 0xAE: "freturn", 0xAF: "dreturn",
    0xB0: "areturn", 0xB1: "return", 0xB2: "getstatic",
    0xB3: "putstatic", 0xB4: "getfield", 0xB5: "putfield",
    0xB6: "invokevirtual", 0xB7: "invokespecial", 0xB8: "invokestatic",
    0xB9: "invokeinterface", 0xBA: "invokedynamic", 0xBB: "new",
    0xBC: "newarray", 0xBD: "anewarray", 0xBE: "arraylength",
    0xBF: "athrow", 0xC0: "checkcast", 0xC1: "instanceof",
    0xC2: "monitorenter", 0xC3: "monitorexit", 0xC4: "wide",
    0xC5: "multianewarray", 0xC6: "ifnull", 0xC7: "ifnonnull",
    0xC8: "goto_w", 0xC9: "jsr_w", 0xCA: "breakpoint",
    0xFE: "impdep1", 0xFF: "impdep2",
}

_OPERAND_BYTES = {
    0x10: 1, 0x11: 2, 0x12: 1, 0x13: 2, 0x14: 2,
    **{opcode: 1 for opcode in range(0x15, 0x1A)},
    **{opcode: 1 for opcode in range(0x36, 0x3B)},
    0x84: 2,
    **{opcode: 2 for opcode in range(0x99, 0xA9)},
    0xA9: 1,
    **{opcode: 2 for opcode in range(0xB2, 0xB9)},
    0xB9: 4, 0xBA: 4, 0xBB: 2, 0xBC: 1, 0xBD: 2,
    0xC0: 2, 0xC1: 2, 0xC5: 3, 0xC6: 2, 0xC7: 2,
    0xC8: 4, 0xC9: 4,
}

_SHORT_BRANCHES = frozenset(range(0x99, 0xA9)) | {0xC6, 0xC7}
_WIDE_BRANCHES = frozenset({0xC8, 0xC9})


def _signed(value: bytes) -> int:
    return int.from_bytes(value, "big", signed=True)


def decode_instructions(code: bytes) -> tuple[Instruction, ...]:
    """Decode all JVM instruction boundaries in one Code byte array."""
    result = []
    offset = 0
    while offset < len(code):
        opcode = code[offset]
        mnemonic = _NAMES.get(opcode, f"opcode_{opcode:02x}")
        if opcode in (0xAA, 0xAB):
            cursor = offset + 1
            cursor += (-cursor) % 4
            if cursor + 8 > len(code):
                raise ValueError(f"truncated {mnemonic} at bytecode offset {offset}")
            default = _signed(code[cursor:cursor + 4])
            cursor += 4
            targets = [offset + default]
            operands = []
            if opcode == 0xAA:
                low = _signed(code[cursor:cursor + 4])
                high = _signed(code[cursor + 4:cursor + 8])
                cursor += 8
                if high < low or high - low > 1_000_000:
                    raise ValueError(f"invalid tableswitch range at bytecode offset {offset}")
                count = high - low + 1
                if cursor + count * 4 > len(code):
                    raise ValueError(f"truncated tableswitch at bytecode offset {offset}")
                operands.extend((low, high))
                for index in range(count):
                    relative = _signed(code[cursor + index * 4:cursor + index * 4 + 4])
                    targets.append(offset + relative)
                cursor += count * 4
            else:
                pairs = _signed(code[cursor:cursor + 4])
                cursor += 4
                if pairs < 0 or pairs > 1_000_000 or cursor + pairs * 8 > len(code):
                    raise ValueError(f"invalid lookupswitch at bytecode offset {offset}")
                operands.append(pairs)
                for index in range(pairs):
                    match = _signed(code[cursor + index * 8:cursor + index * 8 + 4])
                    relative = _signed(code[cursor + index * 8 + 4:cursor + index * 8 + 8])
                    operands.append(match)
                    targets.append(offset + relative)
                cursor += pairs * 8
            result.append(Instruction(offset, opcode, mnemonic, tuple(operands), tuple(targets)))
            offset = cursor
            continue
        if opcode == 0xC4:
            if offset + 4 > len(code):
                raise ValueError(f"truncated wide at bytecode offset {offset}")
            widened = code[offset + 1]
            local = int.from_bytes(code[offset + 2:offset + 4], "big")
            if widened == 0x84:
                if offset + 6 > len(code):
                    raise ValueError(f"truncated wide iinc at bytecode offset {offset}")
                constant = _signed(code[offset + 4:offset + 6])
                result.append(Instruction(offset, opcode, mnemonic, (widened, local, constant)))
                offset += 6
            elif widened in set(range(0x15, 0x1A)) | set(range(0x36, 0x3B)) | {0xA9}:
                result.append(Instruction(offset, opcode, mnemonic, (widened, local)))
                offset += 4
            else:
                raise ValueError(f"invalid wide opcode 0x{widened:02x} at {offset}")
            continue
        operand_size = _OPERAND_BYTES.get(opcode, 0)
        end = offset + 1 + operand_size
        if end > len(code):
            raise ValueError(f"truncated {mnemonic} at bytecode offset {offset}")
        raw = code[offset + 1:end]
        targets: tuple[int, ...] = ()
        if opcode in _SHORT_BRANCHES:
            relative = _signed(raw)
            operands = (relative,)
            targets = (offset + relative,)
        elif opcode in _WIDE_BRANCHES:
            relative = _signed(raw)
            operands = (relative,)
            targets = (offset + relative,)
        elif opcode == 0x84:
            operands = (raw[0], _signed(raw[1:2]))
        elif opcode in (0x10, 0x11):
            operands = (_signed(raw),)
        elif opcode in (0xB9, 0xBA):
            operands = (int.from_bytes(raw[:2], "big"), raw[2], raw[3])
        elif opcode == 0xC5:
            operands = (int.from_bytes(raw[:2], "big"), raw[2])
        elif operand_size == 2:
            operands = (int.from_bytes(raw, "big"),)
        elif operand_size == 1:
            operands = (raw[0],)
        elif operand_size:
            operands = tuple(raw)
        else:
            operands = ()
        result.append(Instruction(offset, opcode, mnemonic, operands, targets))
        offset = end
    return tuple(result)


def _decode_modified_utf8(raw: bytes) -> str:
    try:
        return raw.replace(b"\xc0\x80", b"\x00").decode("utf-8", "surrogatepass")
    except UnicodeDecodeError as error:
        raise ValueError(f"invalid modified UTF-8 constant: {error}") from error


class _Pool:
    def __init__(self, entries: list[_CpEntry | None]):
        self.entries = entries

    def entry(self, index: int, *tags: int) -> _CpEntry:
        if not 0 < index < len(self.entries) or self.entries[index] is None:
            raise ValueError(f"invalid constant-pool index {index}")
        entry = self.entries[index]
        assert entry is not None
        if tags and entry.tag not in tags:
            raise ValueError(
                f"constant-pool index {index} has tag {entry.tag}, expected {tags}"
            )
        return entry

    def utf(self, index: int) -> str:
        return self.entry(index, 1).value

    def class_name(self, index: int) -> str:
        return self.utf(self.entry(index, 7).value)

    def name_type(self, index: int) -> tuple[str, str]:
        name_index, descriptor_index = self.entry(index, 12).value
        return self.utf(name_index), self.utf(descriptor_index)

    def member(self, index: int) -> tuple[int, str, str, str]:
        entry = self.entry(index, 9, 10, 11)
        class_index, name_type_index = entry.value
        name, descriptor = self.name_type(name_type_index)
        return entry.tag, self.class_name(class_index), name, descriptor

    def literal(self, index: int) -> tuple[str, Any]:
        entry = self.entry(index)
        if entry.tag == 8:
            return "string_literal", self.utf(entry.value)
        if entry.tag == 7:
            return "class_literal", self.class_name(index)
        if entry.tag in (3, 4, 5, 6):
            return "numeric_literal", entry.value
        if entry.tag == 15:
            return "method_handle", entry.value
        if entry.tag == 16:
            return "method_type", self.utf(entry.value)
        if entry.tag in (17, 18):
            _, name_type_index = entry.value
            return "dynamic_literal", self.name_type(name_type_index)
        raise ValueError(f"unsupported ldc constant tag {entry.tag} at index {index}")


def _parse_pool(reader: _Reader) -> _Pool:
    count = reader.u2()
    if count == 0:
        raise ValueError("constant-pool count cannot be zero")
    entries: list[_CpEntry | None] = [None]
    index = 1
    while index < count:
        tag = reader.u1()
        if tag == 1:
            raw = reader.take(reader.u2())
            value = _decode_modified_utf8(raw)
        elif tag == 3:
            value = struct.unpack(">i", reader.take(4))[0]
        elif tag == 4:
            value = struct.unpack(">f", reader.take(4))[0]
        elif tag == 5:
            value = struct.unpack(">q", reader.take(8))[0]
        elif tag == 6:
            value = struct.unpack(">d", reader.take(8))[0]
        elif tag in (7, 8, 16, 19, 20):
            value = reader.u2()
        elif tag in (9, 10, 11, 12, 17, 18):
            value = (reader.u2(), reader.u2())
        elif tag == 15:
            value = (reader.u1(), reader.u2())
        else:
            raise ValueError(f"unsupported constant-pool tag {tag} at index {index}")
        entries.append(_CpEntry(tag, value))
        if tag in (5, 6):
            entries.append(None)
            index += 2
        else:
            index += 1
    if len(entries) != count:
        raise ValueError("invalid two-slot constant at end of constant pool")
    return _Pool(entries)


def _attribute_headers(reader: _Reader, pool: _Pool) -> list[tuple[str, bytes]]:
    result = []
    for _ in range(reader.u2()):
        name = pool.utf(reader.u2())
        length = reader.u4()
        result.append((name, reader.take(length)))
    return result


def _resolve_edges(
    instructions: tuple[Instruction, ...], pool: _Pool,
) -> tuple[tuple[MemberEdge, ...], tuple[TypeEdge, ...], tuple[LiteralEdge, ...]]:
    members = []
    types = []
    literals = []
    field_kinds = {
        0xB2: "field_read", 0xB3: "field_write",
        0xB4: "field_read", 0xB5: "field_write",
    }
    invoke_kinds = {
        0xB6: "invoke_virtual", 0xB7: "invoke_special",
        0xB8: "invoke_static", 0xB9: "invoke_interface",
    }
    type_kinds = {
        0xBB: "construct", 0xBD: "array_type", 0xC0: "checkcast",
        0xC1: "instanceof", 0xC5: "multi_array_type",
    }
    for instruction in instructions:
        if instruction.opcode in field_kinds | invoke_kinds:
            index = instruction.operands[0]
            _, owner, name, descriptor = pool.member(index)
            kind = field_kinds.get(instruction.opcode, invoke_kinds.get(instruction.opcode))
            assert kind is not None
            members.append(MemberEdge(
                instruction.offset, kind, owner, name, descriptor,
                instruction.mnemonic, index,
            ))
        elif instruction.opcode == 0xBA:
            index = instruction.operands[0]
            _, name_type_index = pool.entry(index, 18).value
            name, descriptor = pool.name_type(name_type_index)
            members.append(MemberEdge(
                instruction.offset, "invoke_dynamic", "<dynamic>", name,
                descriptor, instruction.mnemonic, index,
            ))
        elif instruction.opcode in type_kinds:
            index = instruction.operands[0]
            types.append(TypeEdge(
                instruction.offset, type_kinds[instruction.opcode],
                pool.class_name(index), instruction.mnemonic, index,
            ))
        elif instruction.opcode in (0x12, 0x13, 0x14):
            index = instruction.operands[0]
            kind, value = pool.literal(index)
            literals.append(LiteralEdge(
                instruction.offset, kind, value, instruction.mnemonic, index,
            ))
    return tuple(members), tuple(types), tuple(literals)


def _parse_field(reader: _Reader, pool: _Pool) -> FieldModel:
    access_flags = reader.u2()
    name = pool.utf(reader.u2())
    descriptor = pool.utf(reader.u2())
    attributes = _attribute_headers(reader, pool)
    constant = None
    for attribute_name, payload in attributes:
        if attribute_name == "ConstantValue":
            if len(payload) != 2:
                raise ValueError("invalid ConstantValue attribute length")
            constant_index = struct.unpack(">H", payload)[0]
            _, constant = pool.literal(constant_index)
    return FieldModel(
        name, descriptor, access_flags, constant,
        tuple(attribute_name for attribute_name, _ in attributes),
    )


def _parse_method(
    reader: _Reader, pool: _Pool, *, max_code_bytes: int,
) -> MethodModel:
    access_flags = reader.u2()
    name = pool.utf(reader.u2())
    descriptor = pool.utf(reader.u2())
    attributes = _attribute_headers(reader, pool)
    instructions: tuple[Instruction, ...] = ()
    handlers: tuple[ExceptionHandler, ...] = ()
    members: tuple[MemberEdge, ...] = ()
    types: tuple[TypeEdge, ...] = ()
    literals: tuple[LiteralEdge, ...] = ()
    code_seen = False
    for attribute_name, payload in attributes:
        if attribute_name != "Code":
            continue
        if code_seen:
            raise ValueError(f"duplicate Code attribute on {name}{descriptor}")
        code_seen = True
        code_reader = _Reader(payload, f"Code attribute for {name}{descriptor}")
        code_reader.u2()  # max_stack
        code_reader.u2()  # max_locals
        code_length = code_reader.u4()
        if code_length > max_code_bytes:
            raise ValueError(f"Code size limit exceeded on {name}{descriptor}")
        code = code_reader.take(code_length)
        instructions = decode_instructions(code)
        parsed_handlers = []
        for _ in range(code_reader.u2()):
            start_pc = code_reader.u2()
            end_pc = code_reader.u2()
            handler_pc = code_reader.u2()
            catch_index = code_reader.u2()
            if not (0 <= start_pc <= end_pc <= code_length):
                raise ValueError(f"invalid exception range on {name}{descriptor}")
            if handler_pc >= code_length and code_length:
                raise ValueError(f"invalid exception handler on {name}{descriptor}")
            parsed_handlers.append(ExceptionHandler(
                start_pc, end_pc, handler_pc,
                pool.class_name(catch_index) if catch_index else None,
            ))
        _attribute_headers(code_reader, pool)
        if code_reader.position != len(payload):
            raise ValueError(f"trailing bytes in Code attribute on {name}{descriptor}")
        handlers = tuple(parsed_handlers)
        members, types, literals = _resolve_edges(instructions, pool)
    if (access_flags & (0x0100 | 0x0400)) and code_seen:
        raise ValueError(f"native/abstract method has Code: {name}{descriptor}")
    if not (access_flags & (0x0100 | 0x0400)) and not code_seen:
        raise ValueError(f"concrete method lacks Code: {name}{descriptor}")
    return MethodModel(
        name, descriptor, access_flags, instructions, members, types, literals,
        handlers, tuple(attribute_name for attribute_name, _ in attributes),
    )


def parse_class(
    data: bytes, *, max_class_bytes: int = 8 * 1024 * 1024,
    max_code_bytes: int = 2 * 1024 * 1024,
) -> ClassModel:
    """Parse one complete classfile, failing closed on malformed structure."""
    if max_class_bytes <= 0 or max_code_bytes <= 0:
        raise ValueError("size limits must be positive")
    if len(data) > max_class_bytes:
        raise ValueError("class size limit exceeded")
    if len(data) < 4 or data[:4] != b"\xca\xfe\xba\xbe":
        raise ValueError("invalid JVM class magic")
    reader = _Reader(data)
    reader.take(4)
    minor_version = reader.u2()
    major_version = reader.u2()
    pool = _parse_pool(reader)
    access_flags = reader.u2()
    name = pool.class_name(reader.u2())
    super_index = reader.u2()
    super_name = pool.class_name(super_index) if super_index else None
    interfaces = tuple(pool.class_name(reader.u2()) for _ in range(reader.u2()))
    fields = tuple(_parse_field(reader, pool) for _ in range(reader.u2()))
    methods = tuple(
        _parse_method(reader, pool, max_code_bytes=max_code_bytes)
        for _ in range(reader.u2())
    )
    attributes = _attribute_headers(reader, pool)
    if reader.position != len(data):
        raise ValueError(f"trailing classfile bytes at 0x{reader.position:x}")

    utf8_constants = tuple(
        entry.value for entry in pool.entries[1:]
        if entry is not None and entry.tag == 1
    )
    string_constants = tuple(
        pool.utf(entry.value) for entry in pool.entries[1:]
        if entry is not None and entry.tag == 8
    )
    class_references = tuple(
        pool.utf(entry.value) for entry in pool.entries[1:]
        if entry is not None and entry.tag == 7
    )
    return ClassModel(
        minor_version, major_version, access_flags, name, super_name,
        interfaces, fields, methods,
        tuple(attribute_name for attribute_name, _ in attributes),
        utf8_constants, string_constants, class_references,
    )
