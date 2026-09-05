# Read-only analysis tools

Run commands from the repository root. Firmware inputs stay in ignored local
paths; none of these tools needs a tracked vendor fixture. Do not execute a
vendor ELF, patch an image, or commit license/activation material.

## ELF32 / ARM inspection

`arm_elf_analysis.py` uses Python 3.10+ and Capstone (`python -m pip install capstone`
in your chosen development environment). It parses ELF32 little-endian
load segments itself; pyelftools is not required.

```powershell
python -m analysis_tools.arm_elf_analysis metadata analysis_work/Synctool.elf
python -m analysis_tools.arm_elf_analysis disasm analysis_work/Synctool.elf --start 0x11A9B4 --end 0x11A9DC --literals
python -m analysis_tools.arm_elf_analysis callers analysis_work/Synctool.elf --target 0x110E6C
python -m analysis_tools.arm_elf_analysis words analysis_work/Synctool.elf --start 0x3127D8 --count 1
python -m analysis_tools.arm_elf_analysis strings analysis_work/Synctool.elf --pattern 'application_skuid|license_model' --xrefs
python -m analysis_tools.arm_elf_analysis references analysis_work/Synctool.elf --value 0x2466BC
python -m analysis_tools.arm_elf_analysis memory analysis_work/Synctool.elf --offset 0x51 --kind str
```

All disassembly ends are exclusive. `disasm --thumb` explicitly chooses Thumb;
there is no automatic instruction-set detection. Disassembly returns exit 2 if
it stops before the requested end, for example on a literal pool. Revisit the
range instead of treating a truncated listing as a complete function.

Whole-segment caller, prologue, immediate, field-access and PC-literal scans
are **candidates**: executable load segments can contain headers and data.
Verify surrounding code and actual installed vtables. `callers` includes
direct BL/BLX candidates, including conditional ARM calls and Thumb candidates
after embedded data; it excludes tail branches and indirect calls. `function`
finds nearby ARM prologues, which need not coincide with actual entries or ends.
`virtual-loads --selector` is only a candidate LDR displacement search, not a
resolved virtual call or a module-selector search. Use `immediate --value` for
immediate constants; synthesized constants can still be missed.

## Synctool evidence anchors

```powershell
python -m analysis_tools.synctool_evidence analysis_work/Synctool.elf --verbose
```

The verifier refuses an unknown SHA-256, then checks selected table entries,
instructions and schema strings used in the
[device/license report](../reports/synctool_device_license_selection.md).
It detects binary/version drift and transcription mistakes. Passing checks
are not a substitute for manually following the surrounding control/data flow.
Only derived, non-secret addresses and assertions are stored in the script;
it contains no license payload, activation data or decompiled vendor source.

## Find existing diagnostic evidence

```powershell
python -m analysis_tools.synctool_log_probe uconnectmapimage.img --max-hits 30
python -m analysis_tools.synctool_log_probe recovered_root_helpers/swdlLog_recovered.txt
```

This standard-library-only streaming probe distinguishes embedded format
strings from runtime-looking marker occurrences. It reports byte offsets,
categories and, when present, a signed decimal App SKU. It never prints record
names or surrounding arbitrary log contents. The display cap does not stop
the full scan. No matches cannot exclude compressed, fragmented, damaged or
differently spelled messages. Even a runtime-looking hit is a candidate, not
authenticated execution evidence.

## Tests

```powershell
python -m unittest analysis_tools.tests.test_arm_elf_analysis analysis_tools.tests.test_synctool_evidence analysis_tools.tests.test_synctool_log_probe -v
python -m unittest discover -s analysis_tools/tests -v
```

The new tests use synthetic in-memory ELF/log data only. The broader existing
suite also requires `cryptography` for its separate developer-token probe
tests; that dependency is not needed for the Synctool tools. Existing
`jamaica_rom_strings.py` and `qnx_ifs_inventory.py` have their own CLI help
and tests and are unchanged by this investigation.
