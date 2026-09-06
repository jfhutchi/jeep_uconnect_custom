"""Read-only FWS/CWS ABC index and selected-method disassembly. No execution."""
import argparse
import hashlib
import re
import struct
import zlib
from pathlib import Path

CAP = 32_000_000


class Reader:
    def __init__(self, data, base=0):
        self.data, self.pos, self.base = data, 0, base

    def take(self, n):
        if n < 0 or n > len(self.data) - self.pos:
            raise ValueError(f'truncated at {self.base + self.pos:#x}')
        result = self.data[self.pos:self.pos + n]
        self.pos += n
        return result

    def byte(self):
        return self.take(1)[0]

    def uint(self):
        result = 0
        for shift in range(0, 35, 7):
            b = self.byte()
            if shift == 28 and b > 15:
                raise ValueError('overflowing encoded u32')
            result |= (b & 127) << shift
            if b < 128:
                return result
        raise ValueError('unterminated encoded integer')

    def u30(self):
        value = self.uint()
        if value >= 1 << 30:
            raise ValueError('overflowing u30')
        return value

    def count(self):
        n = self.u30()
        if n > len(self.data) - self.pos:
            raise ValueError('implausible count')
        return n


def abc_tags(data):
    if len(data) < 8 or len(data) > CAP or data[:3] not in (b'FWS', b'CWS'):
        raise ValueError('requires bounded FWS/CWS')
    size = int.from_bytes(data[4:8], 'little')
    if not 8 <= size <= CAP:
        raise ValueError('invalid declared SWF size')
    if data[:3] == b'CWS':
        inflater = zlib.decompressobj()
        try:
            body = inflater.decompress(data[8:], size - 8 + 1)
        except zlib.error as exc:
            raise ValueError('invalid zlib stream') from exc
        if not inflater.eof or inflater.unused_data or inflater.unconsumed_tail:
            raise ValueError('truncated, oversized or trailing compressed SWF')
        data = b'FWS' + data[3:8] + body
    if len(data) != size:
        raise ValueError('SWF length mismatch')
    r = Reader(data)
    r.take(8)
    bits = r.take(1)[0] >> 3
    r.take((5 + 4 * bits + 7) // 8 - 1 + 4)
    result = []
    while r.pos < len(data):
        header = int.from_bytes(r.take(2), 'little')
        kind, size = header >> 6, header & 63
        if size == 63:
            size = int.from_bytes(r.take(4), 'little')
        start = r.pos
        payload = r.take(size)
        if kind == 82:
            end = payload.find(b'\0', 4)
            if end < 0:
                raise ValueError('unterminated DoABC name')
            result.append((start + end + 1, payload[end + 1:]))
        if kind == 0:
            if size or r.pos != len(data):
                raise ValueError('invalid End tag/trailing data')
            return result
    raise ValueError('missing SWF End tag')


def parse_abc(data, base=0):
    r = Reader(data, base)
    minor, major = struct.unpack('<HH', r.take(4))
    if (minor, major) != (16, 46):
        raise ValueError(f'unsupported ABC version {major}.{minor}')

    def pool(read, zero):
        return [zero] + [read() for _ in range(max(0, r.count() - 1))]

    ints = pool(r.uint, 0)
    ints = [v - (1 << 32) if v & (1 << 31) else v for v in ints]
    uints = pool(r.uint, 0)
    doubles = pool(lambda: struct.unpack('<d', r.take(8))[0], float('nan'))
    strings = pool(lambda: r.take(r.u30()).decode('utf-8', errors='backslashreplace'), '')
    namespaces = pool(lambda: (r.byte(), r.u30()), (0, 0))
    nssets = pool(lambda: [r.u30() for _ in range(r.count())], [])
    multinames = [('*',)]
    for _ in range(max(0, r.count() - 1)):
        kind = r.byte()
        if kind in (7, 13, 9, 14):
            args = (r.u30(), r.u30())
        elif kind in (15, 16, 27, 28):
            args = (r.u30(),)
        elif kind in (17, 18):
            args = ()
        elif kind == 29:
            args = (r.u30(), [r.u30() for _ in range(r.count())])
        else:
            raise ValueError(f'unknown multiname kind {kind:#x}')
        multinames.append((kind, *args))

    def name(index, depth=0):
        if depth > 30:
            raise ValueError('recursive multiname')
        m = multinames[index]
        if index == 0:
            return '*'
        if m[0] in (7, 13):
            namespace = strings[namespaces[m[1]][1]]
            return (namespace + '::' if namespace else '') + strings[m[2]]
        if m[0] in (9, 14, 15, 16):
            return strings[m[1]]
        if m[0] == 29:
            return name(m[1], depth + 1) + '<' + ','.join(name(i, depth + 1) for i in m[2]) + '>'
        return '<runtime-name>'

    methods = []
    for _ in range(r.count()):
        offset = base + r.pos
        count, returns = r.count(), r.u30()
        params = [r.u30() for _ in range(count)]
        method_name, flags = r.u30(), r.byte()
        if flags & 8:
            for _ in range(r.count()):
                r.u30()
                r.byte()
        if flags & 128:
            for _ in range(count):
                r.u30()
        methods.append({'offset': offset, 'name': strings[method_name], 'owners': [],
                        'params': [name(i) for i in params], 'returns': name(returns)})
    for _ in range(r.count()):
        r.u30()
        for _ in range(r.count() * 2):
            r.u30()

    def bind(method, owner):
        methods[method]['owners'].append(owner)

    def traits(owner):
        for _ in range(r.count()):
            trait_name, flags = name(r.u30()), r.byte()
            kind = flags & 15
            r.u30()  # slot or dispatch ID
            if kind in (0, 6):
                r.u30()
                if r.u30():
                    r.byte()
            elif kind in (1, 2, 3, 5):
                bind(r.u30(), owner + '/' + trait_name + (' [get]' if kind == 2 else ' [set]' if kind == 3 else ''))
            elif kind == 4:
                r.u30()
            else:
                raise ValueError(f'unknown trait kind {kind}')
            if flags & 64:
                for _ in range(r.count()):
                    r.u30()

    classes = []
    for _ in range(r.count()):
        owner = name(r.u30())
        classes.append(owner)
        r.u30()
        if r.byte() & 8:
            r.u30()
        for _ in range(r.count()):
            r.u30()
        bind(r.u30(), owner + '/<init>')
        traits(owner)
    for owner in classes:
        bind(r.u30(), owner + '/<cinit>')
        traits(owner + ' [static]')
    for i in range(r.count()):
        bind(r.u30(), f'script{i}/<init>')
        traits(f'script{i}')
    bodies = {}
    for _ in range(r.count()):
        method = r.u30()
        limits = [r.u30() for _ in range(4)]
        length = r.u30()
        offset = base + r.pos
        code = r.take(length)
        for _ in range(r.count()):
            for _ in range(5):
                r.u30()
        traits(f'method{method}')
        if method >= len(methods) or method in bodies:
            raise ValueError('invalid/duplicate method body')
        bodies[method] = {'offset': offset, 'code': code, 'limits': limits}
    if r.pos != len(data):
        raise ValueError('trailing ABC data')
    return {'methods': methods, 'bodies': bodies, 'strings': strings, 'name': name,
            'ints': ints, 'uints': uints, 'doubles': doubles, 'nssets': nssets}


# Only documented operand forms are accepted; unknown instructions stop decoding.
NO_ARGS = dict(zip([0x02, 0x03, 0x09, 0x1c, 0x1d, 0x1e, 0x1f, 0x20, 0x21,
                    0x26, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x30, 0x47, 0x48,
                    0x57, 0x64, 0x70, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78,
                    0x82, 0x85, 0x87, 0x90, 0x91, 0x93, 0x95, 0x96, 0x97],
                   'nop throw label pushwith popscope nextname hasnext pushnull pushundefined '
                   'pushtrue pushfalse pushnan pop dup swap pushscope returnvoid returnvalue '
                   'newactivation getglobalscope convert_s convert_i convert_u convert_d convert_b '
                   'convert_o checkfilter coerce_a coerce_s astypelate negate increment decrement '
                   'typeof not bitnot'.split()))
NO_ARGS.update({0xa0 + i: n for i, n in enumerate('add subtract multiply divide modulo lshift rshift urshift bitand bitor bitxor equals strictequals lessthan lessequals greaterthan greaterequals instanceof'.split())})
NO_ARGS.update({0xd0 + i: f'getlocal_{i}' for i in range(4)})
NO_ARGS.update({0xd4 + i: f'setlocal_{i}' for i in range(4)})
NO_ARGS.update({0x23: 'nextvalue', 0xb3: 'istypelate', 0xb4: 'in',
                0xc0: 'increment_i', 0xc1: 'decrement_i', 0xc4: 'negate_i',
                0xc5: 'add_i', 0xc6: 'subtract_i', 0xc7: 'multiply_i'})
ONE = {0x04:'getsuper', 0x05:'setsuper', 0x06:'dxns', 0x08:'kill', 0x25:'pushshort',
       0x2c:'pushstring', 0x2d:'pushint', 0x2e:'pushuint', 0x2f:'pushdouble',
       0x31:'pushnamespace', 0x40:'newfunction', 0x41:'call', 0x42:'construct',
       0x49:'constructsuper', 0x53:'applytype', 0x55:'newobject', 0x56:'newarray',
       0x58:'newclass', 0x59:'getdescendants', 0x5d:'findpropstrict', 0x5e:'findproperty',
       0x5f:'finddef', 0x60:'getlex', 0x61:'setproperty', 0x62:'getlocal', 0x63:'setlocal',
       0x66:'getproperty', 0x67:'getouterscope', 0x68:'initproperty', 0x6a:'deleteproperty',
       0x6c:'getslot', 0x6d:'setslot', 0x6e:'getglobalslot', 0x6f:'setglobalslot',
       0x80:'coerce', 0x86:'astype', 0x92:'inclocal', 0x94:'declocal', 0xb2:'istype',
       0xc2:'inclocal_i', 0xc3:'declocal_i', 0xf0:'debugline', 0xf1:'debugfile'}
TWO = {0x32:'hasnext2', 0x43:'callmethod', 0x44:'callstatic', 0x45:'callsuper',
       0x46:'callproperty', 0x4a:'constructprop', 0x4c:'callproplex',
       0x4e:'callsupervoid', 0x4f:'callpropvoid'}
MN = {4,5,0x59,0x5d,0x5e,0x5f,0x60,0x61,0x66,0x68,0x6a,0x80,0x86,0xb2,
      0x45,0x46,0x4a,0x4c,0x4e,0x4f}
BRANCH = 'ifnlt ifnle ifngt ifnge jump iftrue iffalse ifeq ifne iflt ifle ifgt ifge ifstricteq ifstrictne'.split()


def disassemble(abc, method):
    body = abc['bodies'][method]
    r = Reader(body['code'], body['offset'])
    while r.pos < len(r.data):
        offset, op = r.base + r.pos, r.byte()
        args, note = [], ''
        if op in NO_ARGS:
            name = NO_ARGS[op]
        elif op in ONE:
            name, args = ONE[op], [r.u30()]
        elif op in TWO:
            name, args = TWO[op], [r.u30(), r.u30()]
        elif op in (0x24, 0x65):
            name, args = ('pushbyte' if op == 0x24 else 'getscopeobject'), [r.byte()]
            if op == 0x24 and args[0] > 127:
                args[0] -= 256
        elif 0x0c <= op <= 0x1a:
            name = BRANCH[op - 0x0c]
            delta = int.from_bytes(r.take(3), 'little', signed=True)
            note = f'-> {r.base + r.pos + delta:#x}'
        elif op == 0x1b:
            name = 'lookupswitch'
            default = int.from_bytes(r.take(3), 'little', signed=True)
            count = r.count()
            args = [offset + default] + [offset + int.from_bytes(r.take(3), 'little', signed=True) for _ in range(count + 1)]
        elif op == 0xef:
            name, args = 'debug', [r.byte(), r.u30(), r.byte(), r.u30()]
        else:
            raise ValueError(f'unsupported opcode {op:#x} at {offset:#x}')
        if op in MN:
            note = abc['name'](args[0])
        elif op in (0x2c, 0x06, 0xf1):
            note = repr(abc['strings'][args[0]])
        elif op in (0x2d, 0x2e, 0x2f):
            note = repr(abc[{0x2d:'ints', 0x2e:'uints', 0x2f:'doubles'}[op]][args[0]])
        yield offset, f'{offset:08X} {name:18} {args} {note}'


def find_references(abc, pattern, limit=150):
    """Return bounded instruction XREFs matching a case-insensitive regex."""
    if not 1 <= limit <= 1000:
        raise ValueError('reference result cap must be 1..1000')
    matcher = re.compile(pattern, re.I) if isinstance(pattern, str) else pattern
    matches = []
    for method in sorted(abc['bodies']):
        for offset, line in disassemble(abc, method):
            if matcher.search(line):
                matches.append((method, offset, line))
                if len(matches) == limit:
                    return matches, True
    return matches, False


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('path', type=Path)
    cli.add_argument('--match', default='IHvac|Hvac')
    cli.add_argument('--abc', type=int, default=0)
    cli.add_argument('--method', type=int)
    cli.add_argument('--xref', help='regex over decoded instructions across all method bodies')
    cli.add_argument('--start', type=lambda s: int(s, 0), default=0)
    cli.add_argument('--count', type=int, default=150)
    args = cli.parse_args()
    if args.path.stat().st_size > CAP or not 1 <= args.count <= 1000:
        cli.error('32 MB input / 1000 instruction output cap')
    data = args.path.read_bytes()
    tags = abc_tags(data)
    if not 0 <= args.abc < len(tags):
        cli.error('invalid ABC index')
    base, data_abc = tags[args.abc]
    abc = parse_abc(data_abc, base)
    print(f'SHA256 {hashlib.sha256(data).hexdigest()} ABC={args.abc} FWS_base={base:#x} methods={len(abc["methods"])}')
    if args.xref is not None:
        if args.method is not None:
            cli.error('--method and --xref are mutually exclusive')
        try:
            references, truncated = find_references(abc, args.xref, args.count)
        except re.error as exc:
            cli.error(f'invalid --xref regex: {exc}')
        current = None
        for method, _, line in references:
            if method != current:
                print(f'method {method}', abc['methods'][method])
                current = method
            print(line)
        if truncated:
            print(f'XREF output capped at {args.count} matches')
    elif args.method is None:
        pattern = re.compile(args.match, re.I)
        for i, m in enumerate(abc['methods']):
            if pattern.search(str(m)):
                body = abc['bodies'].get(i)
                print(i, m, f'code={body["offset"]:#x} length={len(body["code"])}' if body else 'no body')
    else:
        if args.method not in abc['bodies']:
            cli.error('method has no body')
        print(abc['methods'][args.method])
        printed = 0
        for offset, line in disassemble(abc, args.method):
            if offset >= args.start and printed < args.count:
                print(line)
                printed += 1


if __name__ == '__main__':
    main()
