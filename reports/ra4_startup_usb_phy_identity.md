# RA4 startup USB PHY identity and controller separation

Date: 2026-09-06. Analysis baseline: `712f2607d3da31ec8de821466c0e9a84bdc3f8f5`.
This completes the bounded startup/I2C/PMIC follow-up to the
[Mentor and stock power-control trace](ra4_usb_phy_power_control.md).
Only owner-supplied bytes and host analysis tools were used. No startup code,
driver, utility or target service was executed.

## Result

**CONFIRMED STATIC / HIGH INTENDED PHY FAMILY:** the uncompressed startup
portion of RA4 `ifs-cmc.bin` contains a board-specific EHCI initialization path
that announces `USB83340C`. The corresponding code accesses the EHCI ULPI
instruction register at `0x480648a4`, using encoded port selector `2`. It pulses
GPIO-bank-2 bit 6, reads PHY identity registers 0-3, and configures OTG Control
and Interface Control. Microchip documents the USB83340 family, but the exact
fitted part, suffix/revision and board nets are not established by this image.

**CONFIRMED STATIC:** the same startup routine separately configures the
Mentor/OTG controller at `0x480ab000`. It writes Interface Control `0x40` and
OTG Control `0x86` through that controller's ULPI viewport. Those writes precede
the named EHCI initialization. The name `USB83340C` therefore cannot be carried
over to the Mentor PHY merely because both paths occur in one function.

**STILL UNKNOWN:** Mentor PHY identity, the external VBUS switch and its board
connection, Radio C2-to-controller routing, media-hub reversibility, and a
compatible installed DCD/function stack. This investigation narrows the
hardware evidence but does not qualify the phone-facing port for device role.

## Source and startup boundary

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `analysis_ra4_18.45.01/work/primary_iso/usr/share/IFS/ifs-cmc.bin` | 42122670 | `ea6797be141763f35f3059ad858eefbf54f730af0155bebc7af411c47d80ba92` |
| Source prefix `[0, 0x19110)`, including the 8-byte preboot | 102672 | `7e7a2763fd708d862b959beb4cfbc7ee66efe05729a61a6c89039a3afc412a82` |
| `standard_boot/files/bin/i2c-omap35xx` | 24620 | `23156bb506cddde8c02967c38546ee7a0645219d79c27f1df8905892907fcdd8` |
| `standard_boot/files/etc/system/config/gpio.conf` | 1406 | `d37066a23ca22b571e57bc7ba510f213a8a23ee0228dc996a26ea9d66b551b9d` |
| `segment_001a0000/files/usr/lib/graphics/omap3730/graphics.conf` | 2389 | `984bfe3e698cf33f565c7698d98ea6aff2a59d568799e8a8d5a0ba0986204e93` |

The last three paths are relative to ignored
`analysis_ra4_18.45.01/work/hidden_hbc_ifs/`.

The QNX startup header begins at file offset `0x8`, signature `0x00ff7eeb`.
Its fields give startup entry `0x801004c0`, RAM address `0x80100008`, startup
size `0x19108`, and preboot size `8`. Thus the uncompressed startup boundary is
`8 + 0x19108 = 0x19110`, matching the existing imagefs recovery boundary.
The code-address correspondence used here is **VA = `0x80100000` + file offset**.
Literal pointers into the startup strings corroborate that correspondence.
The prefix is not an ELF; it was decoded directly as little-endian ARM.

The embedded startup argument record names `startup-omap3730cmc` at file
`0x180a0`. Board provenance in the diagnostic source path at `0xeeec` names
`boards/omap3730cmc/init_hwinfo.c` in the Fiat BSP tree. These are build-time
identifiers, not proof of runtime observations on the user's installed radio.

QNX's [startup-header reference](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.building/topic/ipl/ipl_startup_header.html)
explains the uncompressed startup size and preboot fields. The field values
above come from the RA4 artifact; use of current format documentation does not
imply a QNX 8 runtime. Recovered `.script` still identifies `qnx650`.

## Two independent controller paths in startup

All code locations in the following tables are **file offsets**; add
`0x80100000` to obtain startup VAs. The initialization caller at `0x1378`
branches directly to USB setup at `0x0a8c`.

| Path | Static operations | Call offsets |
| --- | --- | --- |
| Mentor/OTG | ULPI Interface Control register `7` gets `0x40`; OTG Control register `0x0a` gets `0x86` | `0x0ac8`, `0x0ad4` -> helper `0x0984` |
| EHCI | Named PHY initialization message followed by EHCI setup | `0x0b64` loads the message pointer; `0x0b6c` -> `0x0938` |
| EHCI reset/identity | Pulse GPIO, then read PHY registers 0, 1, 2, 3 with port selector `2` | `0x0940` -> `0x0774`; reads at `0x0800`, `0x0810`, `0x0820`, `0x0830` |
| EHCI configuration | OTG Control register `0x0a` gets `0x66`; Interface Control register `7` gets `0x10`, both with selector `2` | `0x0960`, `0x0970` -> helper `0x0888` |

Mentor helper `0x0984` writes byte addresses `0x480ab075`, `0x480ab074` and
`0x480ab076`: ULPI address, data, and request/control. Its sibling read helper
at `0x0a0c` uses that same viewport. The aligned direct-branch census found no
direct caller of that read helper within the startup prefix; this does not
exclude indirect use. In particular, no Mentor vendor/product read is proved.

EHCI helpers `0x06b4` and `0x0888` instead pack port, operation, register and
data fields into the 32-bit register at `0x480648a4`. Both use physical
`0x48064850` around access enablement; the report does not assign a board net
to that register. The [TI-authored OMAP EHCI driver definitions](https://raw.githubusercontent.com/torvalds/linux/v6.1/drivers/usb/host/ehci-omap.c)
corroborate offset `0xa4` and the field positions (port at bit 24, operation at
22, register at 16). Encoded selector `2` does not identify Radio C2 or a cabin
connector; it is a controller field.

Standard ULPI definitions identify Mentor's `0x40` Interface Control setting
as IndicatorPassThru. Its `0x86` OTG Control setting clears both drive-request
bits while retaining the external-indicator selection and D+/D- pulldowns.
The later stock power utility selects `0x86`/`0xe6` on this same controller.
EHCI's `0x66` sets both drive-request bits and the pulldowns, while `0x10` in
Interface Control selects AutoResume. These are requested register states,
not measured electrical states. Source: [ULPI register definitions](https://raw.githubusercontent.com/torvalds/linux/v6.1/include/linux/ulpi/regs.h).

## Named EHCI PHY, reset GPIO, and weak identity check

The message at startup file `0xf0e0` names `USB83340C` and explicitly labels
the EHCI PHY. It is loaded through literal `0x0b80` on the path that calls
EHCI setup. This is more specific than an unused generic driver string.

Reset helper `0x0774` performs the following sequence:

1. Read `0x4905003c`, clear mask `0x40`, and write back at call `0x0794`.
2. Read `0x49050034`, clear mask `0x40`, and write back at `0x07b0`.
3. Execute a software delay, then set mask `0x40` in `0x4905003c` at `0x07d8`.
4. Delay again, then read EHCI PHY identity bytes.

The [OMAP3 controller map](https://raw.githubusercontent.com/torvalds/linux/v6.1/arch/arm/boot/dts/omap3.dtsi)
identifies `0x49050000` as GPIO bank 2; the [OMAP GPIO definitions](https://raw.githubusercontent.com/torvalds/linux/v6.1/include/linux/platform_data/gpio-omap.h)
identify `+0x34` as OE and `+0x3c` as DATAOUT. This is GPIO bank 2 bit 6
(SoC GPIO 38). The code therefore establishes a low-to-high output sequence
associated with EHCI PHY reset. **HIGH intended reset connection**, but the
physical connection to the chip's RESETB pin is still untraced. It must not be
renamed a VBUS-enable GPIO.

The helper reads all four identity registers, but the sole identity comparison
is `cmp r6, #0x24` at `0x0848`: vendor ID low byte. The other bytes are used
for a diagnostic. The mismatch path also returns to the caller, which proceeds
with configuration writes. This is not an enforced full VID/PID part check.

Microchip's [USB83340 data sheet](https://ww1.microchip.com/downloads/aemDocuments/documents/UNG/ProductDocuments/DataSheets/USB83340-Data-Sheet-60001311.pdf)
lists default identity bytes `24 04 09 00` and an active-high CPEN output that
controls an external VBUS supply switch (sections 5.6.3, 7.1.1). This supplies
a plausible external-power-control mechanism for the named EHCI family. It
does not establish a fitted switch model, wiring, or measured output.
The [USB3340 data sheet](https://www.microchip.com/content/dam/mchp/documents/UNG/ProductDocuments/DataSheets/USB3340-Data-Sheet-DS00001678E.pdf)
lists the same identity bytes; even a complete observed VID/PID would not by
itself distinguish those two families. No observed ID values are available here.

## Why the I2C/PMIC candidates do not close the gap

| Candidate | Exact evidence | Bounded conclusion |
| --- | --- | --- |
| I2C manager | Boot `.script` at `0x0b14` names `i2c-omap35xx`; arguments at `0x0b2e` onward include `-a2`, `-i57`, `-p0x48072000`, `--u2`, `--b40000` | Establishes a configured I2C manager, not its attached device identities. Arguments are recorded as data, not execution instructions. |
| I2C driver TWL name | Driver help text at ELF file `0x4f9b` mentions a TWL4030 audio-codec I2C slave | Generic help/driver support does not establish a fitted TWL4030 or a USB PHY. |
| Graphics support | `libWFDomap35xx.so` contains symbol name `twl4030_setup_graphics` at file `0x1a1d`; recovered graphics config line 33 says `tw4030 = 0` | Optional graphics support and a disabled configuration value are not evidence of an active USB PMIC path. No claim about every runtime configuration is made. |
| Audio driver metadata | `deva-ctrl-omap35xx-dsp.so` at file `0x4613`, sibling `-bt.so` at `0x4316`, describe a TWL4030 audio system | Descriptions alone do not identify the USB PHY or prove board wiring. |
| GPIO configuration | `USBFault` is input GPIO 164 at line 4; no USB-named output is declared in this configuration | A fault input does not identify its electrical source or a power-enable output. Startup's separate GPIO reset sequence is outside this runtime table. |

The recovered USB register helpers use direct MMIO, independently of the I2C
manager. No I2C-address-to-PHY or PMIC-to-VBUS-switch connection was established.
There is no claim that this radio contains no PMIC, or that the whole firmware
lacks other USB initialization code.

## Reproduction and validation

Analysis outputs remain ignored under `analysis_work/usb_startup_20260906/`.
Fresh validation checked the complete source and startup-prefix SHA-256 values,
startup signature and size/preboot boundary, eight gap-free ARM ranges (310
instructions), and seven selected instruction anchors. It also hashed the
three configuration/driver artifacts listed above. No implementation source
changed, so the preceding host test-suite results were not rerun or relabeled.

| File-offset start | Exclusive code end | Purpose | Instructions |
| --- | --- | --- | ---: |
| `0x06b4` | `0x0768` | EHCI PHY read | 45 |
| `0x0774` | `0x0880` | EHCI reset and ID reads | 67 |
| `0x0888` | `0x092c` | EHCI PHY write | 41 |
| `0x0938` | `0x0984` | EHCI PHY setup | 19 |
| `0x0984` | `0x0a08` | Mentor ULPI write | 33 |
| `0x0a0c` | `0x0a88` | Mentor ULPI read | 31 |
| `0x0a8c` | `0x0b80` | Combined USB initialization | 61 |
| `0x1368` | `0x139c` | Startup caller fragment | 13 |

The ends exclude literal pools; the last row is a caller fragment, not a claim
to have decoded the entire startup main routine. A simple host reproduction,
using the existing post-reboot Python environment with Capstone 5.0.9:

```python
from pathlib import Path
from hashlib import sha256
import struct
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_LITTLE_ENDIAN

path = Path('analysis_ra4_18.45.01/work/primary_iso/usr/share/IFS/ifs-cmc.bin')
data = path.read_bytes()
assert sha256(data).hexdigest() == 'ea6797be141763f35f3059ad858eefbf54f730af0155bebc7af411c47d80ba92'
assert struct.unpack_from('<I', data, 8)[0] == 0x00ff7eeb
end = struct.unpack_from('<I', data, 0x28)[0] + struct.unpack_from('<H', data, 0x38)[0]
assert end == 0x19110
assert sha256(data[:end]).hexdigest() == '7e7a2763fd708d862b959beb4cfbc7ee66efe05729a61a6c89039a3afc412a82'
decoder = Cs(CS_ARCH_ARM, CS_MODE_ARM | CS_MODE_LITTLE_ENDIAN)
ranges = [(0x6b4, 0x768), (0x774, 0x880), (0x888, 0x92c),
          (0x938, 0x984), (0x984, 0xa08), (0xa0c, 0xa88),
          (0xa8c, 0xb80), (0x1368, 0x139c)]
for start, stop in ranges:
    code = list(decoder.disasm(data[start:stop], 0x80100000 + start))
    assert [i.address for i in code] == list(range(0x80100000 + start, 0x80100000 + stop, 4))
    for i in code:
        print(f'{i.address:#010x}: {i.mnemonic} {i.op_str}')
```

## Next evidence and implementation boundary

This startup target is complete within the inspected artifact. The concrete
next hardware evidence is an existing owner-supplied topology/boot capture or
authorized passive schematic/board evidence connecting the cabin media hub and
Radio C2 to one of the two controllers. Use the EHCI USB83340-family/GPIO-38
lead and the separate Mentor ULPI path as distinct correlation targets.
Do not infer a physical port from an encoded port number or from a power log.

The matching projection screen/backend and legitimate package/provider route
remain independent acquisition gates. Further broad searches for generic PMIC
names will not substitute for the missing net or observed topology.
The additive projection design, factory lifecycle/camera/critical priority and
storage envelope remain unchanged. This checkpoint installs zero radio bytes
and authorizes no live MMIO, GPIO, I2C, USB role change or firmware modification.
