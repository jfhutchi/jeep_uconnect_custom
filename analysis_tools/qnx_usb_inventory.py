"""Read-only structured USB/projection census; requires host pyelftools.

Read file headers, ELF dynamic metadata and ZIP/JAR central directories instead
of searching raw firmware bytes. Name matches are candidates, never proof that
a component is installed, loadable, running or authorized. No archives are
extracted and no target binaries are executed. Keep output in ignored storage:
relative paths and ELF symbol names are metadata, not guaranteed anonymous.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
from typing import BinaryIO
import zipfile

from elftools.common.exceptions import ELFError
from elftools.elf.elffile import ELFFile


NAME = re.compile(r'usb|devu-|dcd|device.?stack|gadget|accessory|aoa|'
                  r'projection|cinemo|modulelink|appmanager|servicebroker', re.I)
SYMBOL = re.compile(r'^usbd_|dcd|usbdci|device.?stack|accessory|aoa|'
                    r'projection|cinemo', re.I)


def elf_metadata(stream: BinaryIO) -> dict:
    """Read program dynamic tables even when QNX has stripped their sections."""
    try:
        elf = ELFFile(stream)
        imports, exports, needed = set(), set(), set()
        dynamic_tables = 0
        for segment in elf.iter_segments():
            if segment['p_type'] == 'PT_DYNAMIC':
                for tag in segment.iter_tags('DT_NEEDED'):
                    needed.add(tag.needed)
                if next(segment.iter_tags('DT_SYMTAB'), None) is not None:
                    dynamic_tables += 1
                    for symbol in segment.iter_symbols():
                        if symbol.name:
                            destination = imports if symbol['st_shndx'] == 'SHN_UNDEF' else exports
                            destination.add(symbol.name)
        have_segment_symbols = dynamic_tables > 0
        for section in elf.iter_sections():
            if section['sh_type'] == 'SHT_DYNSYM' and not have_segment_symbols:
                dynamic_tables += 1
                for symbol in section.iter_symbols():
                    if symbol.name:
                        destination = imports if symbol['st_shndx'] == 'SHN_UNDEF' else exports
                        destination.add(symbol.name)
            elif section['sh_type'] == 'SHT_DYNAMIC':
                for tag in section.iter_tags('DT_NEEDED'):
                    needed.add(tag.needed)
        return {
            'bits': elf.elfclass, 'little_endian': elf.little_endian,
            'machine': elf['e_machine'], 'type': elf['e_type'],
            'flags': elf['e_flags'], 'dynamic_symbol_tables': dynamic_tables,
            'imports': sorted(imports), 'exports': sorted(exports),
            'needed': sorted(needed),
        }
    except ELFError as exc:
        raise ValueError(f'invalid ELF metadata: {exc}') from exc


def inventory(roots: list[Path]) -> dict:
    result = {
        'format': 'qnx-usb-structured-inventory-v1',
        'boundary': 'Regular files; ELF program/section dynamic tables; ZIP/JAR member names only. '
                    'No archive payload inspection or runtime loadability claim.',
        'totals': dict(files=0, header_bytes=0, elf_files=0, archives=0,
                       archive_members=0, skipped_links=0, elf_without_dynsym=0),
        'roots': [], 'file_name_candidates': [], 'archive_name_candidates': [],
        'elf_candidates': [],
    }
    totals = result['totals']
    for index, root in enumerate(roots):
        if not root.is_dir():
            raise FileNotFoundError(f'root is not a directory: {root}')
        if root.is_symlink() or root.is_junction():
            raise ValueError(f'root must not be a link: {root}')
        label = f'root{index}'
        root_row = {'label': label, 'name': root.name, 'files': 0}
        result['roots'].append(root_row)
        def walk_error(error):
            raise error
        for directory, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
            for name in dirs[:]:
                entry = Path(directory) / name
                if entry.is_symlink() or entry.is_junction():
                    dirs.remove(name)
                    totals['skipped_links'] += 1
            dirs.sort()
            for name in sorted(files):
                path = Path(directory) / name
                if path.is_symlink():
                    totals['skipped_links'] += 1
                    continue
                relative = path.relative_to(root).as_posix()
                identity = {'root': label, 'path': relative}
                totals['files'] += 1
                root_row['files'] += 1
                if NAME.search(name):
                    result['file_name_candidates'].append(identity)
                with path.open('rb') as stream:
                    header = stream.read(20)
                    totals['header_bytes'] += len(header)
                    stream.seek(0)
                    if header.startswith(b'\x7fELF'):
                        try:
                            metadata = elf_metadata(stream)
                        except ValueError as exc:
                            raise ValueError(f'{label}/{relative}: {exc}') from exc
                        totals['elf_files'] += 1
                        if not metadata['dynamic_symbol_tables']:
                            totals['elf_without_dynsym'] += 1
                        hits = {key: [s for s in metadata[key] if SYMBOL.search(s)]
                                for key in ('imports', 'exports')}
                        if NAME.search(name) or any(hits.values()) or any(
                                NAME.search(dep) for dep in metadata['needed']):
                            stream.seek(0)
                            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
                            result['elf_candidates'].append({
                                **identity, 'size': path.stat().st_size, 'sha256': digest,
                                **{k: v for k, v in metadata.items()
                                   if k not in ('imports', 'exports')},
                                'import_count': len(metadata['imports']),
                                'export_count': len(metadata['exports']), **hits,
                            })
                    elif header.startswith((b'PK\x03\x04', b'PK\x05\x06')):
                        with zipfile.ZipFile(stream) as archive:
                            members = archive.infolist()
                            totals['archives'] += 1
                            totals['archive_members'] += len(members)
                            for member in members:
                                if NAME.search(member.filename):
                                    result['archive_name_candidates'].append({
                                        **identity, 'member': member.filename,
                                        'uncompressed_size': member.file_size,
                                    })
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('roots', nargs='+', type=Path)
    args = parser.parse_args()
    print(json.dumps(inventory(args.roots), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
