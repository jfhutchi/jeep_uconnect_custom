"""Read selected JVM invocation references from a JAR without executing classes.

Reports instruction references, not a runtime call graph or verifier result.
Requires jawa==2.2.0 on the host. No resource payloads or string values are emitted.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import re
from typing import BinaryIO
import zipfile

from jawa.cf import ClassFile


def inspect_class(data: bytes, owner: re.Pattern, method: re.Pattern) -> dict:
    if data[:4] != b'\xca\xfe\xba\xbe':
        raise ValueError('invalid JVM class magic')
    cf = ClassFile(io.BytesIO(data))
    calls = []
    methods = dynamic = 0
    for caller in cf.methods:
        if caller.code is None:
            continue
        methods += 1
        for instruction in caller.code.disassemble():
            if instruction.mnemonic == 'invokedynamic':
                dynamic += 1
                continue
            if instruction.mnemonic not in ('invokevirtual', 'invokespecial',
                                            'invokestatic', 'invokeinterface'):
                continue
            reference = cf.constants.get(instruction.operands[0].value)
            target_owner = reference.class_.name.value
            target_name = reference.name_and_type.name.value
            if owner.search(target_owner) and method.search(target_name):
                calls.append({'caller': caller.name.value,
                              'caller_descriptor': caller.descriptor.value,
                              'bci': instruction.pos, 'opcode': instruction.mnemonic,
                              'owner': target_owner, 'name': target_name,
                              'descriptor': reference.name_and_type.descriptor.value})
    return {'class': cf.this.name.value, 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest(),
            'methods_with_code': methods, 'invokedynamic_unresolved': dynamic,
            'calls': calls}


def inspect_jar(source: Path | BinaryIO, member: re.Pattern, owner: re.Pattern,
                method: re.Pattern, *, max_class_bytes: int = 8 * 1024 * 1024,
                max_total_bytes: int = 256 * 1024 * 1024) -> dict:
    if max_class_bytes <= 0 or max_total_bytes <= 0:
        raise ValueError('size limits must be positive')
    classes = []
    total = 0
    with zipfile.ZipFile(source) as jar:
        selected = [i for i in jar.infolist()
                    if not i.is_dir() and i.filename.endswith('.class')
                    and member.search(i.filename)]
        for info in selected:
            total += info.file_size
            if info.file_size > max_class_bytes or total > max_total_bytes:
                raise ValueError(f'class size limit exceeded: {info.filename}')
            with jar.open(info) as stream:
                data = stream.read(max_class_bytes + 1)
            if len(data) != info.file_size or len(data) > max_class_bytes:
                raise ValueError(f'class size mismatch: {info.filename}')
            result = inspect_class(data, owner, method)
            classes.append({'member': info.filename, **result})
    return {'selected_classes': len(classes), 'uncompressed_class_bytes': total,
            'classes': classes}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar', type=Path)
    parser.add_argument('--member', default='.*', help='class member name regex')
    parser.add_argument('--owner', required=True, help='invoked owner internal-name regex')
    parser.add_argument('--method', default='.*', help='invoked method name regex')
    args = parser.parse_args()
    result = inspect_jar(args.jar, re.compile(args.member), re.compile(args.owner),
                         re.compile(args.method))
    result['jar'] = str(args.jar)
    with args.jar.open('rb') as stream:
        result['jar_sha256'] = hashlib.file_digest(stream, 'sha256').hexdigest()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
