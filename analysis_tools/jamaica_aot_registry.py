"""Read an explicitly bounded Jamaica class/member registration table.

This host-only reader reports raw class slots and member ordinals, not Java
names, live registration, execution, or a complete Jamaica format definition.
It supports the observed 24-byte class / 32-byte member record layout.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import struct

from analysis_tools.arm_elf_analysis import Elf32Image


@dataclass(frozen=True)
class MemberRegistration:
    file_offset: int
    kind: str
    storage_va: int
    member_ordinal: int
    adapter_va: int
    function_va: int
    adapter_offset: int | None
    function_offset: int | None


@dataclass(frozen=True)
class ClassRegistration:
    file_offset: int
    flags: int
    storage_va: int
    class_slot: int
    members: tuple[MemberRegistration, ...]


def _code_offset(image: Elf32Image, address: int) -> int | None:
    if address == 0:
        return None
    location = address & ~1  # ARM function pointers can carry the Thumb bit.
    segment = image.segment_for_vaddr(location)
    if not segment.executable:
        raise ValueError(f'function pointer 0x{address:x} is not executable')
    return image.vaddr_to_offset(location)


def read_registry(
    image: Elf32Image, registry_va: int, class_count: int, *, max_members: int = 100_000,
) -> tuple[ClassRegistration, ...]:
    """Decode the caller-selected range, rejecting unsupported/truncated records.

    All pointers use PT_LOAD translation. Storage pointers can refer to BSS;
    they are reported as addresses and are never read as initialized objects.
    Null adapter/function pairs are retained as metadata-only entries. Kind 1
    records address methods; kind 2 records address fields in a separate namespace.
    """
    if image.machine != 40:
        raise ValueError('registry reader requires ARM ELF32')
    if not 0 <= class_count <= 100_000 or max_members < 0:
        raise ValueError('invalid registry count or member limit')
    if registry_va < 0 or registry_va % 4:
        raise ValueError('registry address must be nonnegative and word aligned')
    if class_count == 0:
        return ()
    table = image.read_vaddr(registry_va, class_count * 24)
    classes = []
    seen_classes = set()
    total_members = 0
    for index in range(class_count):
        flags, storage, reserved, slot, method_va, count = struct.unpack_from(
            '<6I', table, index * 24)
        if reserved:
            raise ValueError(f'nonzero reserved class word at index {index}')
        if slot in seen_classes:
            raise ValueError(f'duplicate class slot {slot}')
        seen_classes.add(slot)
        total_members += count
        if total_members > max_members:
            raise ValueError('registry exceeds member limit')
        if bool(count) != bool(method_va):
            raise ValueError(f'inconsistent member array/count for class {slot}')
        if method_va % 4:
            raise ValueError(f'unaligned member array for class {slot}')
        members = []
        seen_members = set()
        raw = image.read_vaddr(method_va, count * 32) if count else b''
        for ordinal in range(count):
            mf, ms, z1, z2, number, adapter, function, z3 = struct.unpack_from(
                '<8I', raw, ordinal * 32)
            if z1 or z2 or z3:
                raise ValueError(f'nonzero reserved member word in class {slot}')
            if mf not in (1, 2):
                raise ValueError(f'unsupported member kind {mf} in class {slot}')
            if (mf, number) in seen_members:
                raise ValueError(f'duplicate member ordinal {number} in class {slot}')
            seen_members.add((mf, number))
            if bool(adapter) != bool(function):
                raise ValueError(f'incomplete adapter/function pair in class {slot}')
            if mf == 2 and function:
                raise ValueError(f'field record has a function in class {slot}')
            members.append(MemberRegistration(
                image.vaddr_to_offset(method_va + ordinal * 32, 32),
                'method' if mf == 1 else 'field', ms, number,
                adapter, function, _code_offset(image, adapter), _code_offset(image, function)))
        classes.append(ClassRegistration(
            image.vaddr_to_offset(registry_va + index * 24, 24), flags, storage,
            slot, tuple(members)))
    return tuple(classes)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('--registry-va', required=True, type=lambda value: int(value, 0))
    parser.add_argument('--class-count', required=True, type=int)
    parser.add_argument('--class-slot', action='append', type=int)
    parser.add_argument('--max-members', type=int, default=100_000)
    args = parser.parse_args()
    try:
        image = Elf32Image.from_path(args.image)
        classes = read_registry(image, args.registry_va, args.class_count,
                                max_members=args.max_members)
        selected = classes if args.class_slot is None else tuple(
            row for row in classes if row.class_slot in args.class_slot)
        if args.class_slot is not None:
            missing = set(args.class_slot) - {row.class_slot for row in selected}
            if missing:
                raise ValueError(f'requested class slots absent from range: {sorted(missing)}')
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps({
        'image': str(args.image), 'sha256': hashlib.sha256(image.data).hexdigest(),
        'registry_va': args.registry_va, 'class_count': len(classes),
        'member_count': sum(len(row.members) for row in classes),
        'method_count': sum(member.kind == 'method' for row in classes for member in row.members),
        'field_count': sum(member.kind == 'field' for row in classes for member in row.members),
        'compiled_method_count': sum(bool(member.function_va) for row in classes for member in row.members),
        'classes': [asdict(row) for row in selected],
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
