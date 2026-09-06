"""Small, reproducible ELF32/ARM static-analysis helpers.

The module intentionally handles only file-backed ELF32 little-endian load
segments and static Capstone disassembly. It never executes the target image.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from capstone import (
    CS_ARCH_ARM,
    CS_MODE_ARM,
    CS_MODE_LITTLE_ENDIAN,
    CS_MODE_THUMB,
    Cs,
    CsInsn,
)
from capstone.arm import ARM_OP_IMM, ARM_OP_MEM, ARM_REG_PC, ARM_INS_BL, ARM_INS_BLX, ARM_INS_LDR


PT_LOAD = 1
PF_X = 1
EM_ARM = 40


class ElfFormatError(ValueError):
    """Raised when the input is not a supported ELF32 image."""


@dataclass(frozen=True)
class ProgramSegment:
    kind: int
    offset: int
    vaddr: int
    paddr: int
    file_size: int
    memory_size: int
    flags: int
    alignment: int

    @property
    def executable(self) -> bool:
        return bool(self.flags & PF_X)

    @property
    def file_end_vaddr(self) -> int:
        return self.vaddr + self.file_size


@dataclass(frozen=True)
class Elf32Image:
    data: bytes
    elf_type: int
    machine: int
    entry: int
    flags: int
    program_segments: tuple[ProgramSegment, ...]

    @classmethod
    def from_bytes(cls, data: bytes) -> "Elf32Image":
        if len(data) < 52 or data[:4] != b"\x7fELF":
            raise ElfFormatError("input is not an ELF file")
        if data[4] != 1:
            raise ElfFormatError("only ELF32 images are supported")
        if data[5] != 1:
            raise ElfFormatError("only little-endian ELF images are supported")
        if data[6] != 1:
            raise ElfFormatError("unsupported ELF identification version")

        (
            elf_type,
            machine,
            version,
            entry,
            program_offset,
            _section_offset,
            flags,
            header_size,
            program_entry_size,
            program_count,
            _section_entry_size,
            _section_count,
            _section_names,
        ) = struct.unpack_from("<HHIIIIIHHHHHH", data, 16)
        if version != 1 or header_size < 52:
            raise ElfFormatError("unsupported ELF header")
        if program_entry_size < 32 and program_count:
            raise ElfFormatError("ELF program header entry is too small")
        program_table_end = program_offset + program_entry_size * program_count
        if program_table_end > len(data):
            raise ElfFormatError("truncated ELF program header table")

        segments: list[ProgramSegment] = []
        for index in range(program_count):
            record_offset = program_offset + index * program_entry_size
            values = struct.unpack_from("<IIIIIIII", data, record_offset)
            segment = ProgramSegment(*values)
            if segment.offset + segment.file_size > len(data):
                raise ElfFormatError("ELF segment extends beyond end of file")
            if segment.kind == PT_LOAD and segment.file_size > segment.memory_size:
                raise ElfFormatError("ELF load segment file size exceeds memory size")
            segments.append(segment)

        return cls(data, elf_type, machine, entry, flags, tuple(segments))

    @classmethod
    def from_path(cls, path: Path) -> "Elf32Image":
        return cls.from_bytes(path.read_bytes())

    @property
    def load_segments(self) -> tuple[ProgramSegment, ...]:
        return tuple(segment for segment in self.program_segments if segment.kind == PT_LOAD)

    def segment_for_vaddr(self, address: int, size: int = 1) -> ProgramSegment:
        if size < 0:
            raise ValueError("size must be nonnegative")
        for segment in self.load_segments:
            if segment.vaddr <= address and address + size <= segment.file_end_vaddr:
                return segment
        raise ValueError(f"range at 0x{address:08X} is not in a file-backed load segment")

    def vaddr_to_offset(self, address: int, size: int = 1) -> int:
        segment = self.segment_for_vaddr(address, size)
        return segment.offset + address - segment.vaddr

    def read_vaddr(self, address: int, size: int) -> bytes:
        offset = self.vaddr_to_offset(address, size)
        return self.data[offset : offset + size]


class ArmElfAnalyzer:
    def __init__(self, image: Elf32Image):
        if image.machine != EM_ARM:
            raise ElfFormatError(f"ELF machine {image.machine} is not ARM")
        self.image = image

    def plt_imports(self) -> dict[int, tuple[int, str]]:
        """Resolve classic ARM ADD/ADD/LDR PLT candidates via ELF32 REL entries.

        Requires section headers. Supports R_ARM_JUMP_SLOT only, not Thumb,
        RELA or arbitrary linker stubs. No target execution or broad decoding.
        A matching stub is not proof that a caller reaches it at runtime.
        """
        data = self.image.data
        section_offset = struct.unpack_from('<I', data, 32)[0]
        entry_size, count = struct.unpack_from('<HH', data, 46)
        if not count:
            if section_offset:
                raise ElfFormatError('extended section numbering is unsupported')
            return {}
        if entry_size < 40 or section_offset + entry_size * count > len(data):
            raise ElfFormatError('invalid section header table')
        sections = [struct.unpack_from('<10I', data, section_offset + i * entry_size)
                    for i in range(count)]

        def section_bytes(index: int, kind: int) -> tuple[tuple[int, ...], bytes]:
            if not 0 <= index < count or sections[index][1] != kind:
                raise ElfFormatError('invalid linked section')
            section = sections[index]
            offset, size = section[4:6]
            if offset + size > len(data):
                raise ElfFormatError('truncated section')
            return section, data[offset:offset + size]

        imports: dict[int, str] = {}
        for index, section in enumerate(sections):
            if section[1] != 9:  # SHT_REL
                continue
            rel, records = section_bytes(index, 9)
            symbols, symbol_data = section_bytes(rel[6], 11)  # SHT_DYNSYM
            _, names = section_bytes(symbols[6], 3)  # SHT_STRTAB
            if rel[9] != 8 or len(records) % 8 or symbols[9] != 16 or len(symbol_data) % 16:
                raise ElfFormatError('unsupported relocation/symbol entry size')
            for offset, info in struct.iter_unpack('<II', records):
                if info & 255 != 22:  # R_ARM_JUMP_SLOT
                    continue
                symbol_offset = (info >> 8) * 16
                if symbol_offset + 16 > len(symbol_data):
                    raise ElfFormatError('invalid relocation symbol index')
                name_offset = struct.unpack_from('<I', symbol_data, symbol_offset)[0]
                end = names.find(b'\0', name_offset)
                if name_offset >= len(names) or end < 0:
                    raise ElfFormatError('invalid symbol name')
                imports[offset] = names[name_offset:end].decode('ascii', errors='backslashreplace')

        def arm_immediate(word: int) -> int:
            rotate = ((word >> 8) & 15) * 2
            byte = word & 255
            return ((byte >> rotate) | (byte << (32 - rotate))) & 0xFFFFFFFF

        result: dict[int, tuple[int, str]] = {}
        for address, first in self.arm_words():
            if first & 0xFFFFF000 != 0xE28FC000:
                continue
            segment = self.image.segment_for_vaddr(address)
            if address + 12 > segment.file_end_vaddr:
                continue
            second, third = struct.unpack('<II', self.image.read_vaddr(address + 4, 8))
            if second & 0xFFFFF000 != 0xE28CC000 or third & 0xFFFFF000 != 0xE5BCF000:
                continue
            slot = (address + 8 + arm_immediate(first) + arm_immediate(second)
                    + (third & 0xFFF)) & 0xFFFFFFFF
            if slot in imports:
                result[address] = (slot, imports[slot])
        return result

    def arm_words(self) -> Iterable[tuple[int, int]]:
        """Enumerate aligned candidate words; data words can be false positives."""
        for segment in self.image.load_segments:
            if segment.executable:
                delta = (-segment.vaddr) % 4
                stop = segment.offset + segment.file_size - 3
                for offset in range(segment.offset + delta, stop, 4):
                    yield segment.vaddr + offset - segment.offset, struct.unpack_from(
                        "<I", self.image.data, offset
                    )[0]

    def read_ascii(self, address: int, limit: int = 256) -> str:
        if limit <= 0:
            raise ValueError("limit must be positive")
        segment = self.image.segment_for_vaddr(address)
        raw = self.image.read_vaddr(address, min(limit, segment.file_end_vaddr - address))
        return raw.split(b"\0", 1)[0].decode("ascii", errors="backslashreplace")

    def word_xrefs(self, value: int) -> list[int]:
        needle = struct.pack("<I", value)
        result = []
        for segment in self.image.load_segments:
            start = segment.offset
            stop = start + segment.file_size
            position = self.image.data.find(needle, start, stop)
            while position >= 0:
                if (segment.vaddr + position - start) % 4 == 0:
                    result.append(segment.vaddr + position - start)
                position = self.image.data.find(needle, position + 1, stop)
        return result

    def immediate_candidates(self, value: int) -> Iterable[CsInsn]:
        """Find ARM MOV/MOVW/CMP/ADD/SUB immediates, not synthesized constants."""
        decoder = self._disassembler(False)
        for address, word in self.arm_words():
            immediate = None
            if word & 0x0FF00000 == 0x03000000:  # MOVW
                immediate = ((word >> 4) & 0xF000) | (word & 0xFFF)
            elif word & 0x0E000000 == 0x02000000:
                rotate = ((word >> 8) & 15) * 2
                byte = word & 255
                immediate = ((byte >> rotate) | (byte << (32 - rotate))) & 0xFFFFFFFF
            if immediate == value:
                for instruction in decoder.disasm(struct.pack("<I", word), address):
                    if any(op.type == ARM_OP_IMM and op.imm == value
                           for op in instruction.operands):
                        yield instruction

    @staticmethod
    def _disassembler(thumb: bool) -> Cs:
        mode = (CS_MODE_THUMB if thumb else CS_MODE_ARM) | CS_MODE_LITTLE_ENDIAN
        disassembler = Cs(CS_ARCH_ARM, mode)
        disassembler.detail = True
        return disassembler

    def disassemble(self, start: int, end: int, *, thumb: bool = False) -> list[CsInsn]:
        if end <= start:
            raise ValueError("end must be greater than start")
        code = self.image.read_vaddr(start, end - start)
        return list(self._disassembler(thumb).disasm(code, start))

    def _thumb_call_candidates(self) -> Iterable[tuple[int, bytes]]:
        for segment in self.image.load_segments:
            if not segment.executable:
                continue
            delta = (-segment.vaddr) % 2
            for offset in range(segment.offset + delta,
                                segment.offset + segment.file_size - 3, 2):
                first, second = struct.unpack_from("<HH", self.image.data, offset)
                if first & 0xF800 == 0xF000 and second & 0xC000 == 0xC000:
                    yield (segment.vaddr + offset - segment.offset,
                           self.image.data[offset:offset + 4])

    def direct_callers(self, target: int, *, thumb: bool = False) -> list[CsInsn]:
        """Find aligned BL/BLX candidates, including after embedded data.

        The caller chooses the instruction set. No code/data or interworking
        reachability inference is made, and indirect/tail calls are excluded.
        """
        candidates = self._thumb_call_candidates() if thumb else (
            (address, struct.pack("<I", word)) for address, word in self.arm_words()
            if word & 0x0F000000 == 0x0B000000 or word & 0xFE000000 == 0xFA000000
        )
        decoder = self._disassembler(thumb)
        normalized_target = target & ~1
        callers: list[CsInsn] = []
        for address, raw in candidates:
            for instruction in decoder.disasm(raw, address, count=1):
                if instruction.id not in {ARM_INS_BL, ARM_INS_BLX}:
                    continue
                operand = instruction.operands[0]
                if operand.type == ARM_OP_IMM and (operand.imm & ~1) == normalized_target:
                    callers.append(instruction)
        return callers

    def function_starts(self) -> list[int]:
        starts: list[int] = []
        for address, word in self.arm_words():
            is_push_with_lr = (
                word & 0x0FFF0000 == 0x092D0000 and bool(word & (1 << 14))
            )
            is_str_lr_predecrement = word & 0x0FFFFFFF == 0x052DE004
            if is_push_with_lr or is_str_lr_predecrement:
                starts.append(address)
        return starts

    def nearest_function_start(self, address: int) -> int | None:
        candidates = [start for start in self.function_starts() if start <= address]
        return max(candidates, default=None)

    def next_function_start(self, address: int) -> int | None:
        candidates = [start for start in self.function_starts() if start > address]
        return min(candidates, default=None)

    def resolve_pc_literal(self, instruction: CsInsn) -> tuple[int, int]:
        if instruction.id != ARM_INS_LDR or len(instruction.operands) < 2:
            raise ValueError("instruction is not an LDR literal")
        operand = instruction.operands[1]
        if operand.type != ARM_OP_MEM or operand.mem.base != ARM_REG_PC:
            raise ValueError("instruction is not PC-relative")
        if operand.mem.index or instruction.writeback:
            raise ValueError("instruction is not a static PC-relative literal")
        pc_bias = 4 if instruction._cs.mode & CS_MODE_THUMB else 8
        pc = (instruction.address + pc_bias) & ~3
        literal_address = pc + operand.mem.disp
        value = struct.unpack("<I", self.image.read_vaddr(literal_address, 4))[0]
        return literal_address, value

    def pc_literals(self) -> Iterable[tuple[CsInsn, int, int]]:
        decoder = self._disassembler(False)
        for address, word in self.arm_words():
            if word & 0x0F7F0000 != 0x051F0000:
                continue
            for instruction in decoder.disasm(struct.pack("<I", word), address):
                try:
                    literal_address, value = self.resolve_pc_literal(instruction)
                except ValueError:
                    continue
                yield instruction, literal_address, value

    def find_ascii(self, text: str) -> list[int]:
        needle = text.encode("ascii")
        if not needle:
            raise ValueError("text must not be empty")
        results: list[int] = []
        for segment in self.image.load_segments:
            raw = self.image.data[segment.offset : segment.offset + segment.file_size]
            position = 0
            while True:
                position = raw.find(needle, position)
                if position < 0:
                    break
                results.append(segment.vaddr + position)
                position += 1
        return results

    def string_xrefs(self, text: str) -> list[tuple[CsInsn, int, int]]:
        targets = set(self.find_ascii(text))
        return [entry for entry in self.pc_literals() if entry[2] in targets]

    def ascii_strings(self, pattern: str) -> Iterable[tuple[int, str]]:
        """Find matching printable strings, preserving their actual start address."""
        matcher = re.compile(pattern, re.IGNORECASE)
        for segment in self.image.load_segments:
            raw = self.image.data[segment.offset:segment.offset + segment.file_size]
            for match in re.finditer(rb"[\x20-\x7e]{4,}", raw):
                value = match.group().decode("ascii")
                if matcher.search(value):
                    yield segment.vaddr + match.start(), value

    def virtual_selector_loads(self, selector: int) -> list[CsInsn]:
        """Candidate positive LDR offsets, not proof of a virtual dispatch.

        Excludes byte, register-indexed, PC-relative and writeback loads.
        Executable segments can still contain data that decodes as instructions.
        """
        matches: list[CsInsn] = []
        decoder = self._disassembler(False)
        for address, word in self.arm_words():
            if (word & 0x0FF00000 == 0x05900000
                    and (word >> 16) & 15 != 15 and word & 0xFFF == selector):
                matches.extend(decoder.disasm(struct.pack("<I", word), address))
        return matches

    def memory_offsets(self, offset: int, mnemonic: str) -> Iterable[CsInsn]:
        """Find immediate LDR/STR field candidates, including negative offsets."""
        decoder = self._disassembler(False)
        for address, word in self.arm_words():
            if word & 0x0E000000 != 0x04000000 or word & 0xFFF != abs(offset):
                continue
            for instruction in decoder.disasm(struct.pack("<I", word), address):
                if not instruction.mnemonic.startswith(mnemonic):
                    continue
                for operand in instruction.operands:
                    if (operand.type == ARM_OP_MEM and operand.mem.base != ARM_REG_PC
                            and operand.mem.disp == offset and not instruction.writeback):
                        yield instruction
                        break


def _number(value: str) -> int:
    return int(value, 0)


def _format_instruction(instruction: CsInsn) -> str:
    raw = instruction.bytes.hex()
    return f"0x{instruction.address:08X}: {raw:<8} {instruction.mnemonic:<8} {instruction.op_str}"


def _load(path: Path) -> tuple[Elf32Image, ArmElfAnalyzer]:
    image = Elf32Image.from_path(path)
    return image, ArmElfAnalyzer(image)


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only ELF32/ARM static analysis")
    subparsers = parser.add_subparsers(dest="command", required=True)

    metadata = subparsers.add_parser("metadata")
    metadata.add_argument("image", type=Path)

    imports = subparsers.add_parser("imports", help="classic ARM PLT candidates from REL symbols")
    imports.add_argument("image", type=Path)

    disassembly = subparsers.add_parser("disasm")
    disassembly.add_argument("image", type=Path)
    disassembly.add_argument("--start", required=True, type=_number)
    disassembly.add_argument("--end", required=True, type=_number)
    disassembly.add_argument("--thumb", action="store_true")
    disassembly.add_argument("--literals", action="store_true")

    callers = subparsers.add_parser("callers")
    callers.add_argument("image", type=Path)
    callers.add_argument("--target", required=True, type=_number)
    callers.add_argument("--thumb", action="store_true")

    function = subparsers.add_parser("function")
    function.add_argument("image", type=Path)
    function.add_argument("--address", required=True, type=_number)

    strings = subparsers.add_parser("string-xrefs")
    strings.add_argument("image", type=Path)
    strings.add_argument("--text", required=True)

    string_list = subparsers.add_parser("strings")
    string_list.add_argument("image", type=Path)
    string_list.add_argument("--pattern", required=True)
    string_list.add_argument("--xrefs", action="store_true")

    refs = subparsers.add_parser("references")
    refs.add_argument("image", type=Path)
    refs.add_argument("--value", required=True, type=_number)

    memory = subparsers.add_parser("memory")
    memory.add_argument("image", type=Path)
    memory.add_argument("--offset", required=True, type=_number)
    memory.add_argument("--kind", choices=("ldr", "str"), required=True)

    virtual = subparsers.add_parser("virtual-loads")
    virtual.add_argument("image", type=Path)
    virtual.add_argument("--selector", required=True, type=_number)

    immediate = subparsers.add_parser("immediate")
    immediate.add_argument("image", type=Path)
    immediate.add_argument("--value", required=True, type=_number)
    words = subparsers.add_parser("words")
    words.add_argument("image", type=Path)
    words.add_argument("--value", type=_number)
    words.add_argument("--start", type=_number)
    words.add_argument("--count", type=_number, default=16)
    string = subparsers.add_parser("string")
    string.add_argument("image", type=Path)
    string.add_argument("--address", required=True, type=_number)

    args = parser.parse_args()
    image, analyzer = _load(args.image)

    if args.command == "metadata":
        print(f"size={len(image.data)}")
        print(f"sha256={hashlib.sha256(image.data).hexdigest()}")
        print(
            f"class=ELF32 endian=little type={image.elf_type} machine={image.machine} "
            f"entry=0x{image.entry:08X} flags=0x{image.flags:08X}"
        )
        for index, segment in enumerate(image.program_segments):
            print(
                f"phdr[{index}] type={segment.kind} offset=0x{segment.offset:X} "
                f"vaddr=0x{segment.vaddr:08X} filesz=0x{segment.file_size:X} "
                f"memsz=0x{segment.memory_size:X} flags=0x{segment.flags:X}"
            )
    elif args.command == "imports":
        for address, (slot, name) in analyzer.plt_imports().items():
            print(f"plt=0x{address:08X} slot=0x{slot:08X} symbol={name}")
    elif args.command == "disasm":
        decoded_end = args.start
        for instruction in analyzer.disassemble(args.start, args.end, thumb=args.thumb):
            decoded_end = instruction.address + instruction.size
            line = _format_instruction(instruction)
            if args.literals:
                try:
                    literal_address, value = analyzer.resolve_pc_literal(instruction)
                except ValueError:
                    pass
                else:
                    line += f" ; [0x{literal_address:08X}]=0x{value:08X}"
            print(line)
        if decoded_end != args.end:
            print(f"Disassembly stopped at 0x{decoded_end:08X}; requested end "
                  f"0x{args.end:08X}. Undecoded bytes remain (data or invalid encoding).",
                  file=sys.stderr)
            return 2
    elif args.command == "callers":
        for instruction in analyzer.direct_callers(args.target, thumb=args.thumb):
            print(_format_instruction(instruction))
    elif args.command == "function":
        start = analyzer.nearest_function_start(args.address)
        end = analyzer.next_function_start(args.address)
        print("Heuristic prologues only; verify entry loads, tails and literal pools.")
        print(f"prologue={None if start is None else f'0x{start:08X}'}")
        print(f"next_prologue={None if end is None else f'0x{end:08X}'}")
    elif args.command == "string-xrefs":
        for address in analyzer.find_ascii(args.text):
            print(f"string=0x{address:08X}")
        for instruction, literal_address, value in analyzer.string_xrefs(args.text):
            print(
                f"xref=0x{instruction.address:08X} "
                f"literal=0x{literal_address:08X} value=0x{value:08X}"
            )
    elif args.command == "virtual-loads":
        for instruction in analyzer.virtual_selector_loads(args.selector):
            print(_format_instruction(instruction))
    elif args.command == "strings":
        matches = dict(analyzer.ascii_strings(args.pattern))
        for address, value in matches.items():
            print(f"0x{address:08X}: {value}")
        if args.xrefs:
            for instruction, literal, value in analyzer.pc_literals():
                if value in matches:
                    print(f"xref=0x{instruction.address:08X} literal=0x{literal:08X} "
                          f"string=0x{value:08X}")
    elif args.command == "immediate":
        for instruction in analyzer.immediate_candidates(args.value):
            print(_format_instruction(instruction))
    elif args.command == "memory":
        for instruction in analyzer.memory_offsets(args.offset, args.kind):
            print(_format_instruction(instruction))
    elif args.command == "references":
        for address in analyzer.word_xrefs(args.value):
            print(f"word=0x{address:08X}")
        for instruction, literal, value in analyzer.pc_literals():
            if value == args.value:
                print(f"xref=0x{instruction.address:08X} literal=0x{literal:08X}")
    elif args.command == "words":
        if args.value is not None:
            for address in analyzer.word_xrefs(args.value):
                print(f"0x{address:08X}")
        elif args.start is not None and args.count > 0:
            for index in range(args.count):
                address = args.start + index * 4
                value = struct.unpack("<I", image.read_vaddr(address, 4))[0]
                print(f"0x{address:08X}: 0x{value:08X}")
        else:
            parser.error("words needs --value or --start with positive --count")
    elif args.command == "string":
        print(analyzer.read_ascii(args.address))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
