# RA4 Mentor USB PHY reset and stock power control

Date: 2026-09-06. Analyzed with repository revision `52546ed8a8e993402143daa1b26f2a78c68cd089`.
This follows the [post-reboot checkpoint](ra4_post_reboot_checkpoint.md).
It records original static analysis, artifact metadata and reproducible host
commands. No recovered executable, Lua program or target service was run.

## Decision

**CONFIRMED STATIC:** RA4 has a stock software path that requests changes to
ULPI PHY VBUS-drive control through the OMAP OTG controller at `0x480ab000`.
`onoff/main.lua` calls `usbPowerSwitch` for load-shed and resume-related power
management. That utility writes ULPI OTG Control register `0x0a`, selecting
`0x86` or `0xe6`; the difference is the two VBUS-drive bits, `0x60`.

**CONFIRMED STATIC:** the Mentor driver's board initialization instead requests
a PHY reset: it writes `0x20` to ULPI register `0x05`, the SET alias of Function
Control `0x04`. Its port-status recovery can repeat that reset and write the
MUSB `DEVCTL.SESSION` bit. These operations do not establish device-role startup.

**UNKNOWN:** actual VBUS voltage/direction, PHY and external power-switch part
numbers, Radio C2 routing, active media-hub reversibility, and an installed
OMAP-compatible device controller/function stack. The software control path
narrows the earlier blanket PHY/VBUS unknown; it does not close the physical
or DCD gate for wired CarPlay.

The stock utility's polling control flow can return success without observing
completion. Its four recovered Lua call sites discard command results. Neither
an exit status nor a log message would establish electrical success.

## Artifacts and address convention

Paths below are relative to local, ignored
`analysis_ra4_18.45.01/work/hidden_hbc_ifs/`.

| Artifact | Relative path | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| Mentor host driver | `standard_boot/files/lib/dll/devu-omap3530-mg.so` | 45936 | `6916bd0f398f28bf111ace6c3a08e425a90127f283e0105e2bb6f0b58df881a1` |
| Power utility | `segment_001a0000/files/usr/bin/usbPowerSwitch` | 8226 | `9290f73bd2e5248a6fb0675919a3157ff1e9ce899b6b33b5b5591c79bb6979e4` |
| Power-management Lua | `segment_001a0000/files/usr/bin/onoff/main.lua` | 66272 | `41c0f3f2709c49d4a4f9b150b8c08c735515a9c50bbfbc2e4c36664d6466e698` |
| Boot command stream | `standard_boot/files/proc/boot/.script` | 16856 | `fb0e5b3df3295951740818b081fc11f2b69a4bcc50386237b4aea7629cf17086` |

Both native artifacts are ELF32 little-endian ARM. Mentor is ET_DYN: addresses
here are ELF virtual addresses, without a runtime load bias. Its RX segment
begins at VA/file offset zero. The utility is ET_EXEC with RX VA `0x100000`
at file offset zero; subtract `0x100000` for the code file offsets here.
Lua addresses are bytecode file offsets; PC indices are zero-based within the
numbered prototype, and line numbers are recovered debug/source lines.

Boot `.script` identifies the Mentor instance at `0x480ab000`, IRQ 92, and the
separate EHCI instance at `0x48064800`, IRQ 77. Its environment says `qnx650`.
The public QNX 6.6 role-swap sequence remains reference evidence, not an
assertion that this recovered build uses that ABI or has that device stack.

## Mentor initialization and recovery

| Operation | ELF VA evidence | Interpretation and limit |
| --- | --- | --- |
| Map controller | `0x54cc` calls the `mmap_device_memory` PLT entry; `0x54d0` stores the result at context `+0x14` | Subsequent base-relative byte accesses use the mapped controller. Mapping length is `0x2000`; boot argv identifies this instance. |
| First board hook | `0x86c0` through `0x86d0` | ORs context `+0x50` with `0x100`, then returns zero. This hook sets a software flag. |
| Initial controller state | stores at `0x5780`, `0x578c` | Clear TESTMODE at base `+0x0f` and DEVCTL at base `+0x60`. This initialization clear alone is not a role-transition implementation. |
| Second board hook | called at `0x57b8`; write sequence `0x8a34` through `0x8a60` | Writes address `5` at base `+0x75`, data `0x20` at `+0x74`, request `1` at `+0x76`: ULPI Function Control RESET via its SET alias. |
| Reset completion | `0x8a68` / `0x8a90` reads, bit test `0x8a6c` / `0x8a94` | Polls ULPI completion bit `2`; timeout path logs and continues to initialization's zero return at `0x8b5c`. No successful reset is proved by that return alone. |
| Start session | stores at `0x58d4`, `0x58e4` | Writes POWER `0x60` and DEVCTL `1`. Generic MUSB names are HSENAB/SOFTCONN and SESSION; these bits alone do not prove the live host/device role. |
| Generic ULPI write | `0x598c` through `0x5a5c` | Takes a register and byte value, writes the same address/data/control registers, and polls completion. |
| Port-status recovery | `0x5b18`, `0x5b1c`, call `0x5b20` | Under the recovered flag/session conditions, calls the ULPI helper with register `5`, value `0x20`; ignores its return, delays, then writes DEVCTL `1` at `0x5b38`. |
| Numeric bus-state selectors | function `0x3460` through `0x34ac` | Selector `5` ORs DEVCTL with `1`; selector `6` ANDs DEVCTL with `1`. The latter retains SESSION, rather than clearing it. Do not name these selectors disconnect/device mode without their enum contract. |

The ULPI reset bit is `0x20`, not Function Control SUSPENDM (`0x40`). The
register number matters: `0x20` in OTG Control instead names a VBUS-drive bit.
The inspected reset/recovery paths neither read PHY vendor/product registers
nor establish a complete host-stack shutdown/device-stack startup transition.
This is a bounded statement about those paths, not all driver code.

The QNX artifact lacks a conventional section table usable by the existing
section-based import resolver. `readelf --use-dynamic --symbols` exposes the
dynamic symbols, although it also diagnoses the missing `.dynamic` section.
The Mentor PT_DYNAMIC data independently gives SYMTAB `0x5d0`, STRTAB `0x10f0`,
JMPREL `0x1ff0`, and REL entry size 8. PLT `0x22c8` resolves through GOT
`0xac9c` to `mmap_device_memory`; PLT `0x2364` resolves through `0xacd0` to
`delay`. These are static import associations, not target calls made here.

## Separate stock VBUS-drive request

The utility's main function begins at `0x100aa4`. Its zero-valued power branch
passes register `0x0a` and data `0x86` to helper `0x100a04` at `0x100b60`.
The nonzero branch passes `0x0a` and `0xe6` at `0x100b8c`.

The helper materializes physical addresses with MOVW/MOVT pairs:

| Purpose | Physical address | Instruction pair |
| --- | --- | --- |
| ULPI register address | `0x480ab075` | `0x100a10`, `0x100a14` |
| ULPI data | `0x480ab074` | `0x100a20`, `0x100a24` |
| ULPI request/completion control | `0x480ab076` | `0x100a30`, `0x100a34` |

The byte writer at `0x100940` maps one physical byte, stores at `0x100988`,
then unmaps it. The reader at `0x1009a4` similarly maps, reads at `0x1009e8`,
and unmaps. This is direct MMIO access to the same controller base as Mentor;
no GPIO or PMIC-service call is needed in this utility's recovered write path.
That fact does not identify the external PHY or its board wiring.

| ULPI OTG Control field | Mask | Data `0x86` | Data `0xe6` |
| --- | --- | --- | --- |
| External VBUS indicator selection | `0x80` | set | set |
| External VBUS drive | `0x40` | clear | set |
| VBUS drive | `0x20` | clear | set |
| D- and D+ pulldowns | `0x06` | set | set |
| ID pullup | `0x01` | clear | clear |

The utility writes the whole OTG Control byte, not a read/modify/write or SET/CLR
alias. The two selected bytes differ only by `0x60`. This establishes a stock
request to change VBUS drive; actual supply removal, discharge, backfeed
protection, port selection and readiness to receive phone-supplied VBUS still
depend on unproved hardware behavior.

### Completion reporting defect

The helper starts a counter at 100 (`0x100a40`) and tests completion bit `2`
at `0x100a64`. Without completion, it decrements the counter (`0x100a6c`) and
loops until the counter is -1. That exhaustion branch at `0x100a78` reaches
the zero return at `0x100a98`. Conversely, completion observed when the counter
is exactly zero reaches the diagnostic and -1 return (`0x100a7c` through
`0x100a94`). The ordinary completion path also returns zero.

Thus, static control flow confirms a success return for an exhausted poll.
Main marks success when the helper returns zero (`0x100b98`). This is not a
claim that a timeout occurred on a radio, and no vendor patch is proposed.

## Stock power-management caller

`onoff/main.lua` parses as Lua 5.1 with 70 prototypes. Prototype 23 begins at
file `0x54fd`, covers recovered source lines 687-1055, and handles a message
with the matching interface-version branch. The four calls below use
`os.execute`; the quoted utility arguments are evidence constants, not
instructions to run them.

| Condition within the recovered handler | Command constant | LOADK / CALL file offsets | PC / source line of CALL |
| --- | --- | --- | --- |
| Incoming `immShutdownReq` is 0 and stored property is `loadShed` | `usbPowerSwitch -p1` | `0x56bd` / `0x56c1` | 108 / 755 |
| Incoming `immShutdownReq` is 2 and stored property is not already `loadShed` | `usbPowerSwitch -p0` | `0x5705` / `0x5709` | 126 / 763 |
| New converted wake reason is `resumeMode`, previous reason differs, on the enclosing wake-reason path | `usbPowerSwitch -p0` | `0x5861` / `0x5865` | 213 / 796 |
| Ignition state changes while previous ignition is `lock` and `wakeupfromResume` is true | `usbPowerSwitch -p1` | `0x5959` / `0x595d` | 275 / 826 |

The exit-from-resume branch sets `wakeupfromResume` at PC226. It does not
immediately power USB on; the later ignition-state branch consumes that flag.
All four CALL instructions have `C=1`, requesting zero Lua return values.
Their following property/flag updates therefore do not test the command result.
The call sites establish factory lifecycle ownership of this power request.
They do not establish a supported additive-application API or projection swap.

`usb_hub_oc` is a separate recovered program whose metadata describes hub-port
overcurrent monitoring and port re-enabling. Its presence and `libusbdi` APIs
must not be substituted for this direct ULPI path or for a device-role driver.

## Reproduction and verification

Only host parsers/disassemblers were executed. Output is local and ignored at
`analysis_work/mentor_usb_static_20260906/`; firmware stays outside Git.
Use the existing post-reboot virtual environment (Capstone 5.0.9):

```powershell
$py = 'analysis_work/post_reboot_20260906/venv/Scripts/python.exe'
$root = 'analysis_ra4_18.45.01/work/hidden_hbc_ifs'
$mentor = "$root/standard_boot/files/lib/dll/devu-omap3530-mg.so"
$power = "$root/segment_001a0000/files/usr/bin/usbPowerSwitch"
$onoff = "$root/segment_001a0000/files/usr/bin/onoff/main.lua"
Get-FileHash -Algorithm SHA256 -LiteralPath $mentor, $power, $onoff
& $py -m analysis_tools.arm_elf_analysis disasm $mentor --start 0x8a18 --end 0x8b74 --literals
& $py -m analysis_tools.arm_elf_analysis disasm $power --start 0x100a04 --end 0x100aa0 --literals
& $py -m analysis_tools.arm_elf_analysis disasm $power --start 0x100aa4 --end 0x100bc0 --literals
& $py -m analysis_tools.lua51_inspect $onoff --function 23 --start 96 --count 190
```

Fresh validation checked all three SHA-256 values against this report, decoded
the following 12 ARM ranges without gaps (1,022 instructions total), parsed all
70 Lua prototypes, and checked all four command CALL opcodes and `C=1` fields.
The complete host check output is `verification.txt` in the local output
directory. This is evidence-boundary validation, not target functional testing.

| Artifact | Start VA | Exclusive code end | Instructions |
| --- | --- | --- | ---: |
| Mentor controller init | `0x5094` | `0x5954` | 560 |
| Mentor board init 1 | `0x86c0` | `0x86d4` | 5 |
| Mentor board init 2 | `0x8a18` | `0x8b74` | 87 |
| Mentor ULPI write | `0x598c` | `0x5a60` | 53 |
| Mentor port status | `0x5a68` | `0x5be0` | 94 |
| Mentor bus state | `0x3460` | `0x34b0` | 20 |
| Mentor clear feature | `0x3368` | `0x33c0` | 22 |
| Mentor set feature | `0x33c0` | `0x3420` | 24 |
| Power byte write | `0x100940` | `0x1009a0` | 24 |
| Power byte read | `0x1009a4` | `0x100a00` | 23 |
| Power ULPI transaction | `0x100a04` | `0x100aa0` | 39 |
| Power main | `0x100aa4` | `0x100bc0` | 71 |

Initial disassembly ranges included trailing literal pools and some stopped
with exit 2 or decoded data words. The corrected exclusive ends above exclude
those pools. No interpretation relies on treating literal data as instructions.
No tool/model source changed in this checkpoint; the previous 135 Python,
20 JavaScript and strict C99 host results remain the preceding checkpoint's
results, not newly claimed test executions.

## Register-reference sources and remaining gate

The register-name interpretation uses primary Linux source definitions:
[ULPI register map](https://raw.githubusercontent.com/torvalds/linux/master/include/linux/ulpi/regs.h)
and [MUSB register map](https://raw.githubusercontent.com/torvalds/linux/master/drivers/usb/musb/musb_regs.h),
consulted 2026-09-06. They corroborate standard fields, not the RA4 PHY identity.
The vendor artifact instructions and hashes establish the RA4-specific writes.

**Next bounded local target:** inspect recovered startup/I2C/PMIC configuration
for an explicit USB PHY identity and power-switch connection, correlating any
result to the now-known `0x480ab000` ULPI path. A PMIC name or generic BSP option
alone is not a PHY part-number or D2784B net proof. The physical hub/radio route
still needs authorized schematic or passive spare-board evidence; compatible
DCD, device function, projection backend and legitimate package authorization
remain independent gates.

This work installs zero radio bytes and changes no firmware or vehicle state.
The >=45 MB stock reserve, 15 MB installed, 4 MB normal growth, 8 MB staging,
>=5 MB residual and <=3 MB no-engine trial limits remain unchanged. The
projection design must preserve factory power-management ownership and stock
camera/critical priority; this report supplies no live control adapter.
