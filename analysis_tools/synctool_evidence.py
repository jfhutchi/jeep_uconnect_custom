"""Hash-gated checks of safe static anchors in the 2017Q2 Synctool ELF.

These checks detect evidence/version drift. They verify selected instructions,
table entries and schema names, not the correctness of an entire recovered
control-flow interpretation. They never execute firmware or parse a license.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
from pathlib import Path
import struct

from analysis_tools.arm_elf_analysis import ArmElfAnalyzer, Elf32Image


EXPECTED_SHA256 = "aa2e2c425d42a5f60427a89817f676b0d32b3ce73057d89355248acc24d4e330"


@dataclass(frozen=True)
class Anchor:
    label: str
    address: int
    kind: str
    expected: str


@dataclass(frozen=True)
class AnchorResult:
    anchor: Anchor
    passed: bool
    actual: str


ANCHORS = (
    Anchor("caller context", 0x11A9C0, "instruction", "mov r4, r0"),
    Anchor("seventh argument byte", 0x11A9D4, "instruction", "ldrb r3, [fp, #0xc]"),
    Anchor("saved flag", 0x11A9D8, "instruction", "str r3, [fp, #-0xa0]"),
    Anchor("App SKU call", 0x11ACD0, "instruction", "bl #0x110e6c"),
    Anchor("parent context field", 0x123774, "instruction", "ldr r0, [r7, #0x154]"),
    Anchor("forwarded stack argument", 0x123790, "instruction", "str ip, [sp, #8]"),
    Anchor("query selector", 0x110FB8, "instruction", "mov r1, #0x284"),
    Anchor("App SKU store", 0x110FD8, "instruction", "str r0, [r4, #0x24]"),
    Anchor("manager factory", 0x30C888, "word", "0x287FBC"),
    Anchor("manager query table slot", 0x3127D8, "word", "0x2466BC"),
    Anchor("application factory", 0x30C8A8, "word", "0x2A84E4"),
    Anchor("application query table slot", 0x312878, "word", "0x26414C"),
    Anchor("application collection slot", 0x312874, "word", "0x2723A0"),
    Anchor("encoded selector prefix", 0x264158, "instruction", "orr r1, r1, #0x42000000"),
    Anchor("SKU metadata load", 0x2640FC, "instruction", "ldr r1, [r0, #8]"),
    Anchor("wrapper SKU slot", 0x310874, "word", "0x262C30"),
    Anchor("wrapper inner record slot", 0x310890, "word", "0x26283C"),
    Anchor("record const metadata slot", 0x311750, "word", "0x2627CC"),
    Anchor("record mutable metadata slot", 0x311754, "word", "0x2627E4"),
    Anchor("const metadata object offset", 0x2627D0, "instruction", "add r0, r0, #0x54"),
    Anchor("mutable metadata object offset", 0x2627E8, "instruction", "add r0, r0, #0x54"),
    Anchor("application property name", 0x313814, "string", "application_skuid"),
    Anchor("license model property name", 0x313720, "string", "license_model"),
    Anchor("SWID property name", 0x3137FC, "string", "swid_info"),
    Anchor("device property name", 0x313808, "string", "device_swid"),
    Anchor("property formats query result", 0x240004, "instruction", "bl #0x142dcc"),
    Anchor("property assignment", 0x240010, "instruction", "bl #0x16ee2c"),
    Anchor("vector retained allocation", 0x11D49C, "instruction", "str r3, [r6, #0x38]"),
    Anchor("device collection selector", 0x11D4A8, "instruction", "movw r1, #0x5ff"),
    Anchor("skip already valid", 0x11D514, "instruction", "bne #0x11d4dc"),
    Anchor("container identifier store", 0x2578B8, "instruction", "str r7, [r4, #0x34]"),
    Anchor("map count load", 0x26F938, "instruction", "ldr r3, [r5, #4]"),
    Anchor("map count increment", 0x26F940, "instruction", "add r3, r3, #1"),
    Anchor("map count store", 0x26F944, "instruction", "str r3, [r5, #4]"),
    Anchor("ordinal from manager count", 0x257D38, "instruction", "ldreq r3, [r5, #0x208]"),
    Anchor("retain assigned ordinal", 0x257D3C, "instruction", "streq r3, [r7, #0x20]"),
    Anchor("container ordinal to loader", 0x2544F0, "instruction", "ldr r2, [lr, #0x34]"),
    Anchor("loader temporary metadata key", 0x254504, "instruction", "str r2, [fp, #-0x98]"),
    Anchor("record identifier store", 0x245138, "instruction", "str r3, [r4, #0x64]"),
    Anchor("scanner first caller", 0x1250F8, "instruction", "bl #0x11d454"),
    Anchor("scanner second caller", 0x125898, "instruction", "bl #0x11d454"),
    Anchor("discard wrapper tail call", 0x124D70, "instruction", "b #0x12445c"),
    Anchor("discard key load", 0x12452C, "instruction", "ldr r5, [r0, #0x10]"),
    Anchor("constructor invalid policy", 0x114D4C, "instruction", "strb r2, [r4, #0x51]"),
    Anchor("scanner copies discard policy", 0x11D7B0, "instruction", "strb r3, [r8]"),
    Anchor("invalid-state assignment conditional", 0x11D8A8, "instruction", "streq r1, [fp, #-0x78]"),
    Anchor("invalid list prune caller", 0x1253B0, "instruction", "bl #0x124d4c"),
    Anchor("filename exclusion callback", 0x124D44, "word", "0x113160"),
    Anchor("planned filename compare", 0x11321C, "instruction", "bl #0x149534"),
    Anchor("clear excluded plan entry", 0x113340, "instruction", "str r3, [r4, #8]"),
    Anchor("filename exclusion diagnostic", 0x2F40A4, "string", "  Removing file from file copy: <%s>"),
)


def check_anchor(image: Elf32Image, anchor: Anchor) -> AnchorResult:
    analyzer = ArmElfAnalyzer(image)
    if anchor.kind not in {"word", "instruction", "string"}:
        raise ValueError(f"unknown anchor kind: {anchor.kind}")
    try:
        if anchor.kind == "word":
            value = struct.unpack("<I", image.read_vaddr(anchor.address, 4))[0]
            actual = f"0x{value:X}"
            passed = value == int(anchor.expected, 0)
        elif anchor.kind == "string":
            actual = analyzer.read_ascii(anchor.address, len(anchor.expected) + 1)
            passed = actual == anchor.expected
        else:
            instructions = analyzer.disassemble(anchor.address, anchor.address + 4)
            actual = " ".join((instructions[0].mnemonic, instructions[0].op_str)) if instructions else "undecodable"
            passed = actual == anchor.expected
    except ValueError as error:
        return AnchorResult(anchor, False, str(error))
    return AnchorResult(anchor, passed, actual)


def verify_image(image: Elf32Image) -> list[AnchorResult]:
    digest = hashlib.sha256(image.data).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError(f"unsupported Synctool SHA-256: {digest}")
    return [check_anchor(image, anchor) for anchor in ANCHORS]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    results = verify_image(Elf32Image.from_path(args.image))
    for result in results:
        if args.verbose or not result.passed:
            state = "PASS" if result.passed else "FAIL"
            print(f"{state} 0x{result.anchor.address:08X} {result.anchor.label}")
            if not result.passed:
                print(f"  expected: {result.anchor.expected}; actual: {result.actual}")
    count = sum(result.passed for result in results)
    print(f"SHA-256 matched; anchors_passed={count}/{len(results)}")
    return 0 if count == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
