"""Extract the bounded EcoDrive storage follow-up; no native code is executed."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from analysis_tools.arm_elf_analysis import ArmElfAnalyzer, Elf32Image
from analysis_tools.kim19_runtime_analysis import encode, native_window

ARTIFACT = 'primary_iso/usr/share/MMC_IFS_EXTENSION/bin/EcoDriveSvc'
SHA256 = '9877299e99772a0ec7a03988bd7521abd8b2c9ceac499c820d3722392d15246e'
REPORT = Path('reports/kim19_runtime_analysis/performance_pages_native_storage.json')
FUNCTIONS = (
    ('EcoDriveCore::startUSBTransfer', 0x12D768, 624),
    ('EcoDriveUSBHandler::transferSingleFile', 0x182798, 2420),
    ('EcoDriveUSBHandler::transferFile', 0x1813FC, 2060),
    ('EcoDriveUSBInsertDetection::getPathToInsertedUSBDevice', 0x17EE7C, 984),
    ('EcoDriveTypes static initialization', 0x17C3D8, 3484),
    ('EcoDriveStorageManager::freeSpaceOnUSB', 0x173850, 52),
    ('EcoDriveStorageManager::copyFile', 0x173A0C, 276),
    ('EcoDriveStorageManager::moveFile', 0x173B20, 1484),
)
WINDOWS = (
    ('global_base', 0x17C3D8, 0x17C3F8),
    ('flash_data_initialization', 0x17C9C4, 0x17C9D8),
    ('usb_data_initialization', 0x17CD54, 0x17CD90),
    ('all_files_dispatch', 0x12D8D4, 0x12D8F0),
    ('single_file_dispatch', 0x12D910, 0x12D930),
    ('single_file_source', 0x12D9C0, 0x12D9D4),
    ('inserted_device', 0x1813FC, 0x181434),
    ('free_space_call', 0x1815F0, 0x181614),
    ('uconnect_destination', 0x1817E4, 0x181808),
    ('ifiat_destination', 0x1818A4, 0x1818C8),
    ('move_dispatch', 0x181A74, 0x181A88),
    ('free_space_implementation', 0x173850, 0x173884),
    ('copy_file_implementation', 0x173A0C, 0x173B20),
    ('copy_dispatch', 0x173E34, 0x173E58),
    ('rename_dispatch', 0x173FC0, 0x174024),
)
LITERALS = (
    (0x20D8A4, '/fs/etfs/usr/var/ecoDrive/data'),
    (0x20DA8C, '/iFiat/ecodrive/data'),
    (0x20DAA4, '/Uconnect/ecodrive/data'),
    (0x20C6EC, '/tmp.tmp'),
    (0x207904, 'All'),
    (0x207908, 'all'),
)


def require_source(data: bytes) -> None:
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError('EcoDriveSvc source SHA-256 differs from reviewed artifact')


def build_report(corpus: Path) -> dict:
    source = (corpus / ARTIFACT).resolve(strict=True)
    if not source.is_relative_to(corpus.resolve(strict=True)):
        raise ValueError('EcoDriveSvc source resolves outside corpus')
    data = source.read_bytes()
    require_source(data)
    analyzer = ArmElfAnalyzer(Elf32Image.from_bytes(data))
    literals = []
    for address, value in LITERALS:
        expected = value.encode('ascii') + b'\0'
        if analyzer.image.read_vaddr(address, len(expected)) != expected:
            raise ValueError('reviewed EcoDrive literal mismatch')
        literals.append({'va': hex(address), 'value': value})
    functions = []
    for name, start, size in FUNCTIONS:
        body = analyzer.image.read_vaddr(start, size)
        functions.append({'symbol_name': name, 'va': hex(start), 'size': size,
                          'sha256': hashlib.sha256(body).hexdigest()})
    windows = [{'id': name, **native_window(analyzer, start, end)}
               for name, start, end in WINDOWS]
    require_source(source.read_bytes())
    return {
        'schema_version': 1,
        'source': {'artifact': ARTIFACT, 'sha256': SHA256, 'bytes': len(data)},
        'scope': 'Bounded static follow-up of the common Kona EcoDrive API; no target execution',
        'evidence_label': 'PROVED',
        'interpretation': 'Reviewed dataflow is documented separately; extraction does not infer runtime authorization.',
        'functions': functions, 'literals': literals, 'windows': windows,
        'uncertainty': 'No KIM19 caller, live service, media state, or Performance Pages file handoff is established.',
    }


def write_or_check(output: Path, report: dict, check: bool) -> int:
    expected = encode(report)
    if check:
        return 0 if output.is_file() and output.read_bytes() == expected else 1
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(expected)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus', required=True, type=Path)
    parser.add_argument('--output', type=Path, default=REPORT)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    if args.output.resolve().is_relative_to(args.corpus.resolve()):
        parser.error('output must be outside recovered corpus')
    result = write_or_check(args.output, build_report(args.corpus), args.check)
    print('EcoDrive native evidence ' + ('verified' if args.check and not result else 'stale' if result else 'written'))
    return result


if __name__ == '__main__':
    raise SystemExit(main())
