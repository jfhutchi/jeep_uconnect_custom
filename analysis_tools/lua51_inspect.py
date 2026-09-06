"""Bounded read-only Lua 5.1 LE bytecode inspection; never executes input."""
import argparse
import hashlib
import re
import struct
from pathlib import Path

OPS = ('MOVE LOADK LOADBOOL LOADNIL GETUPVAL GETGLOBAL GETTABLE SETGLOBAL SETUPVAL '
       'SETTABLE NEWTABLE SELF ADD SUB MUL DIV MOD POW UNM NOT LEN CONCAT JMP EQ LT '
       'LE TEST TESTSET CALL TAILCALL RETURN FORLOOP FORPREP TFORLOOP SETLIST CLOSE '
       'CLOSURE VARARG').split()


class Reader:
    def __init__(self, data):
        self.data, self.pos = data, 0

    def take(self, count):
        if count < 0 or self.pos + count > len(self.data):
            raise ValueError(f'truncated input at {self.pos:#x}')
        value = self.data[self.pos:self.pos + count]
        self.pos += count
        return value

    def u(self, size=4):
        return int.from_bytes(self.take(size), 'little')

    def count(self):
        value = self.u()
        if value > len(self.data) - self.pos:
            raise ValueError('implausible vector count')
        return value

    def string(self):
        size = self.u()
        if not size:
            return ''
        data = self.take(size)
        if data[-1] != 0:
            raise ValueError('nonterminated Lua string')
        return data[:-1].decode('utf-8', errors='backslashreplace')


def parse(data):
    reader = Reader(data)
    if reader.take(12) != b'\x1bLua\x51\x00\x01\x04\x04\x04\x08\x00':
        raise ValueError('requires Lua 5.1 LE, 32-bit int/size_t/instruction, float64')
    functions = []

    def function(depth=0):
        if depth > 100:
            raise ValueError('prototype nesting limit')
        result = {'id': len(functions), 'offset': reader.pos, 'source': reader.string(),
                  'first_line': reader.u(), 'last_line': reader.u()}
        functions.append(result)
        result['nups'], result['params'], result['vararg'], result['stack'] = reader.take(4)
        count = reader.count()
        result['code_offset'] = reader.pos
        result['code'] = [reader.u() for _ in range(count)]
        result['constants'] = []
        for _ in range(reader.count()):
            offset, kind = reader.pos, reader.u(1)
            if kind == 0:
                value = None
            elif kind == 1:
                value = bool(reader.u(1))
            elif kind == 3:
                value = struct.unpack('<d', reader.take(8))[0]
            elif kind == 4:
                value = reader.string()
            else:
                raise ValueError(f'unsupported constant {kind}')
            result['constants'].append({'offset': offset, 'value': value})
        result['children'] = [function(depth + 1)['id'] for _ in range(reader.count())]
        result['lines'] = [reader.u() for _ in range(reader.count())]
        result['locals'] = [(reader.string(), reader.u(), reader.u()) for _ in range(reader.count())]
        result['upvalues'] = [reader.string() for _ in range(reader.count())]
        result['end'] = reader.pos
        return result

    function()
    if reader.pos != len(data):
        raise ValueError(f'trailing data at {reader.pos:#x}')
    return functions


def instruction(function, pc):
    word = function['code'][pc]
    op, a, b, c = word & 63, (word >> 6) & 255, word >> 23, (word >> 14) & 511
    bx = word >> 14
    name = OPS[op] if op < len(OPS) else f'UNKNOWN_{op}'
    note = ''
    constants = function['constants']
    if name in ('LOADK', 'GETGLOBAL', 'SETGLOBAL'):
        note = f'K{bx}={constants[bx]["value"]!r}' if bx < len(constants) else 'INVALID constant'
    elif name == 'CLOSURE':
        note = f'child {function["children"][bx]}' if bx < len(function['children']) else 'INVALID child'
    elif name in ('JMP', 'FORLOOP', 'FORPREP'):
        note = f'-> PC {pc + 1 + bx - 131071}'
    elif name in ('GETUPVAL', 'SETUPVAL'):
        note = f'upvalue {b}: {function["upvalues"][b:b+1]}'
    else:
        rk = [c] if name in ('GETTABLE', 'SELF') else [b, c] if name in (
            'SETTABLE', 'ADD', 'SUB', 'MUL', 'DIV', 'MOD', 'POW', 'EQ', 'LT', 'LE') else []
        note = ', '.join(f'K{v & 255}={constants[v & 255]["value"]!r}'
                         for v in rk if v & 256 and (v & 255) < len(constants))
    line = function['lines'][pc] if pc < len(function['lines']) else '?'
    return f'{function["code_offset"] + pc * 4:08X} PC{pc:04} L{line} {name:10} A={a} B={b} C={c} {note}'


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('path', type=Path)
    cli.add_argument('--match', default='temp|Temp')
    cli.add_argument('--function', type=int)
    cli.add_argument('--start', type=int, default=0)
    cli.add_argument('--count', type=int, default=120)
    args = cli.parse_args()
    if args.path.stat().st_size > 16_000_000:
        cli.error('16 MB input cap')
    data = args.path.read_bytes()
    functions = parse(data)
    print(f'SHA256 {hashlib.sha256(data).hexdigest()} bytes={len(data)} prototypes={len(functions)}')
    if args.function is not None:
        if not 0 <= args.function < len(functions) or args.start < 0 or not 1 <= args.count <= 1000:
            cli.error('invalid function/range; count capped at 1000')
        f = functions[args.function]
        print({k: f[k] for k in ('id', 'offset', 'first_line', 'last_line', 'locals', 'upvalues')})
        for pc in range(args.start, min(len(f['code']), args.start + args.count)):
            print(instruction(f, pc))
    else:
        pattern = re.compile(args.match)
        for f in functions:
            matches = [(k['offset'], k['value']) for k in f['constants'] if pattern.search(str(k['value']))]
            if matches:
                print(f'function {f["id"]} @{f["offset"]:#x} lines={f["first_line"]}-{f["last_line"]} {matches}')


if __name__ == '__main__':
    main()
