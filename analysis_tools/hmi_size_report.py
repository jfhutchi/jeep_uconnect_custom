"""Read-only host/package inventory. Allocation is an estimate, never a radio measurement."""

import argparse
import json
from pathlib import Path


def inventory(root: Path, allocation_unit: int = 4096) -> dict:
    if allocation_unit <= 0:
        raise ValueError('allocation unit must be positive')
    if not root.is_dir():
        raise FileNotFoundError(root)
    if root.is_symlink() or root.is_junction():
        raise ValueError('root links/junctions are not supported')
    files = []
    for path in sorted(root.rglob('*')):
        if path.is_symlink() or path.is_junction():
            raise ValueError(f'links/junctions are not supported: {path}')
        if path.is_file():
            size = path.stat().st_size
            files.append({'path': path.relative_to(root).as_posix(), 'logical_bytes': size,
                          'estimated_allocated_bytes': ((size + allocation_unit - 1) // allocation_unit) * allocation_unit})
    return {'file_count': len(files), 'logical_bytes': sum(f['logical_bytes'] for f in files),
            'estimated_allocated_bytes': sum(f['estimated_allocated_bytes'] for f in files),
            'assumed_allocation_unit': allocation_unit, 'files': files}


def budget(installed: int, writable: int, temporary: int) -> dict:
    if any(not isinstance(n, int) or n < 0 for n in (installed, writable, temporary)):
        raise ValueError('budget inputs must be nonnegative integer bytes')
    remaining = 77_000_000 - installed - writable - temporary
    return {'within_envelope': installed <= 15_000_000 and writable <= 4_000_000
            and temporary <= 8_000_000 and remaining >= 50_000_000,
            'remaining_bytes': remaining, 'protected_stock_bytes': 45_000_000,
            'margin_above_stock_reserve_bytes': remaining - 45_000_000,
            'baseline_bytes': 77_000_000, 'baseline_status': 'owner approximation, not measured'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--kind', choices=['pc-source', 'target-package'], default='pc-source')
    parser.add_argument('--allocation-unit', type=int, default=4096)
    parser.add_argument('--writable-bytes', type=int)
    parser.add_argument('--temporary-bytes', type=int)
    args = parser.parse_args()
    report = inventory(args.root, args.allocation_unit)
    report['kind'] = args.kind
    report['measured_ra4_installed_bytes'] = None
    report['caveat'] = 'Logical bytes measured on host; allocation estimated; metadata/compression/stock variation excluded.'
    report['budget'] = None
    if args.kind == 'target-package':
        if args.writable_bytes is None or args.temporary_bytes is None:
            parser.error('target-package requires explicit --writable-bytes and --temporary-bytes')
        if report['logical_bytes'] == 0:
            parser.error('empty target-package is not a built artifact')
        report['budget'] = budget(report['estimated_allocated_bytes'], args.writable_bytes, args.temporary_bytes)
    print(json.dumps(report, indent=2))
    return 0 if report['budget'] is None or report['budget']['within_envelope'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
