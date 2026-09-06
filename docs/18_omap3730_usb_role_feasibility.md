# 18 - OMAP3730 USB role feasibility

Updated 2026-09-06. This report asks one narrow question needed by the QNX 6.6
CarPlay transport sequence: can the RA4 hardware and its actual QNX BSP switch
the phone-facing port from USB host to USB device mode? It uses official TI/QNX
reference material plus existing RA4 static evidence. No radio, USB
configuration, driver, descriptor, or target service was changed.

## Decision

**CONFIRMED SILICON CAPABILITY:** TI's OMAP36xx technical reference manual
documents a high-speed USB OTG controller and separate host, peripheral, and
host/peripheral programming modes. OMAP3730 therefore does not fail the
CarPlay device-role requirement at the SoC block level.

**PUBLIC QNX BSP DEVICE ROLE UNPROVED:** QNX's public OMAP3730 EVM support page
lists `USB EHCI Host` and `USB OTG Host` as completed binary features. It
does not list an OMAP3730 USB device-controller driver. This is a bounded
negative for that public BSP feature table, not proof that Harman's customized
RA4 BSP lacks a private DCD.

**RA4 PORT ROUTE/BSP UNKNOWN:** the exact Harman BE2800 platform and remote
Mopar media hub/cable are now identified, but the hub-to-radio nets must still
reach the dual-role controller through a suitable PHY/VBUS/ID path. The installed
runtime must include an OMAP-compatible `io-usb-dcd` controller DLL plus the
CarPlay function/descriptor path. Existing tracked evidence proves only host
USB infrastructure and legacy Apple media components.

The local CarPlay transport path remains plausible but now has a precise stop
condition: no board-wired device role or no supported OMAP DCD means QNX 6.6
CarPlay cannot run locally without an authorized BSP/driver addition.

## Evidence chain

| Layer | Evidence | Status |
| --- | --- | --- |
| SoC | TI OMAP36xx/37xx high-speed USB OTG block; TRM includes host, peripheral and combined programming modes | CONFIRMED REFERENCE |
| stock QNX capability | QNX 6.6 `io-usb-dcd` is the generic device-side server and loads hardware-specific DCD DLLs | CONFIRMED REFERENCE |
| public OMAP3730 BSP | feature list names USB EHCI Host and USB OTG Host only | CONFIRMED BOUNDED TABLE / device support absent from list |
| RA4 platform | FCC exhibit 1790035 identifies Harman BE2800, type CMC, models VP4 NA/CA | CONFIRMED |
| cabin media port | Mopar lists the 2014 Grand Cherokee SD/USB/aux hub and separate UCI USB jumper | CONFIRMED remote hub/cable topology |
| RA4 host path | `io-usb`, `libusbdi`/usbd APIs and factory USB utility evidence | CONFIRMED |
| RA4 Apple-adjacent path | `itun`, `libipod`, iPod/media integration and CarPlay HMI vocabulary | CONFIRMED adjacent capability |
| RA4 device stack | `io-usb-dcd`, controller DLL, function driver, descriptors, startup and port mapping | UNKNOWN |
| physical role route | hub silicon, cable/harness pinout, BE2800 nets, SoC controller, PHY and ID/VBUS switching | EXTERNAL_EVIDENCE_REQUIRED |
| CarPlay receiver | licensed driver/receiver/manager, MFi authentication and service ABI | EXTERNAL_EVIDENCE_REQUIRED |

Primary sources:

- TI OMAP36xx Multimedia Device Technical Reference Manual (SWPU177):
  https://www.ti.com/lit/ug/swpu177aa/swpu177aa.pdf
- QNX 6.6 `io-usb-dcd` utility reference:
  https://qnx.com/developers/docs/6.6.0_anm11_wf10/com.qnx.doc.neutrino.utilities/topic/i/io-usb-dcd.html
- QNX TI OMAP3730 EVM support package feature table:
  https://community.qnx.com/sf/wiki/do/viewPdf/projects.bsp/wiki/Bspdown_ti_omap_3730_mistral
- QNX 6.6 CarPlay transport reference:
  https://www.qnx.com/developers/docs/6.6.0_anm11_wf10/com.qnx.doc.dev_pub.ref_guide/topic/usblauncher_config_supported_applications.html
- FCC exhibit 1790035, Harman BE2800 VP4 NA/CA internal photos (mirror
  preserving the filing metadata and FCC source link):
  https://fccid.io/QNG-BE2800/Internal-Photos/VP4-NA-and-VP4-CA-Internal-Photos-1790035
- Official Mopar 2014 Grand Cherokee instrument-panel parts catalog:
  https://store.mopar.ca/v-2014-jeep-grand-cherokee--limited--5-7l-v8-gas/electrical--wiring-instrument-panel
- Official Mopar USB cable 68141323AA:
  https://store.mopar.com/oem-parts/mopar-usb-cable-68141323aa

## Exact RA4 board and cabin-port evidence

**CONFIRMED PLATFORM ID:** FCC exhibit 1790035 identifies FCC ID
`QNG-BE2800`, type `CMC`, and models `VP4 NA / VP4 CA`. Its table of
contents and photographs separately identify the main board, NAND board and
rear I/O board. The exhibit metadata reports 20 pages, 1,021,760 bytes and
SHA-256
`5ace25dafa22c606f239bccdadba8705cc277ebb9cec4ed94467eabc61d2056a`.
This closes the previously missing public board-family identifier.

**CONFIRMED REMOTE MEDIA HUB:** the official Mopar catalog for a 2014 Jeep
Grand Cherokee lists media-center hub `68141322AA` (superseded by
`68289895AA`) as the SD/USB/auxiliary hub and `68141323AA` as the
Universal Consumer Interface USB jumper. The separate official part page calls
`68141323AA` a USB cable. This proves that the user-facing USB receptacle is
part of a remote media hub connected by a cable, not a USB-A receptacle mounted
directly on the BE2800 chassis.

**HIGH TOPOLOGY EVIDENCE, NOT A PINOUT:** the FCC rear-board photograph shows
the large vehicle harness connector but does not label its USB pins. The main-
and rear-board photographs are too coarse to follow D+/D-, VBUS, ground, an
ID pin, or a switched role path. No published exhibit or catalog page found in
this pass maps the remote hub through the harness to a specific OMAP controller,
PHY or role-switch circuit.

Therefore the board-level unknown is narrower but still decisive:

```text
cabin media hub 68141322AA / 68289895AA
  -> USB jumper 68141323AA
  -> unproved vehicle-harness pins
  -> unproved BE2800 rear-board/main-board route
  -> unproved OMAP3730 OTG controller and PHY/VBUS/ID switching
```

A remote hub is not automatically a blocker: it may be a passive connector
assembly or a compatible switching design. It also is not proof of device
role. The exact hub silicon, cable pinout, harness connector pins and board
net names remain required.

## Why SoC capability is insufficient

The TI controller is only one block in the chain. A working target needs:

```text
RA4 phone connector
  -> board PHY, VBUS and ID/role switching
  -> OMAP3730 OTG controller
  -> hardware-specific QNX DCD DLL
  -> io-usb-dcd device-side server
  -> CarPlay descriptors/function driver
  -> support-supplied automotive iOS components
  -> licensed receiver/projection manager
```

A host-only board route, fixed hub, absent ID/VBUS switching, or missing DCD
breaks the chain even though the silicon supports peripheral mode. Likewise,
finding `io-usb-dcd` without its controller DLL/port configuration is not
proof that the RA4 phone connector can switch roles.

## Exact static closure

The 98-marker recovered-tree probe now includes:

- `io-usb-dcd`
- `devu-dcd`
- `ulink_ctrl`
- `omap3530-mg`
- `ehci-omap3`
- `pmic_tw4030_cfg`
- OMAP3 OTG base `0x480ab000`
- `usblauncher`
- `RoleSwap_DigitaliPodOut`
- `RoleSwap_AppleDevice`
- iAP2/iPod and projection-service anchors

For every hit, preserve only relative path, size, SHA-256 and controlled marker
metadata, then establish:

1. ELF architecture/imports without execution.
2. Startup command and loaded DCD DLL name.
3. Controller base/IRQ and OMAP/board association, including whether the
   public-BSP `omap3530-mg` / `0x480ab000` host path appears.
4. Host/device stack transition and descriptor/function-driver configuration.
5. Mapping from that controller instance to the external phone port.
6. Version/permission/owner-death behavior and licensed caller contract.

A complete recovered-tree negative for `io-usb-dcd`/DCD/startup would make an
authorized QNX/Harman driver addition necessary. It would not justify copying a
generic DCD, changing boot files, or experimenting on the vehicle radio.

## Bench closure

Exact physical closure can come from an authorized BE2800 schematic/net list,
a connector pinout plus hub component identification, or separately authorized
spare hardware. Useful passive evidence is: macro photographs of both sides of
the media-hub and radio PCBs; cable continuity from hub pins to the BE2800 rear
connector; controller/driver argv; loaded modules; device nodes; and port
topology. The first powered observation should remain passive inventory. Any
later role transition requires an approved QNX/Harman procedure, current-limited
bench wiring, recovery path and factory USB/camera/HMI regression plan. This
document does not authorize that experiment.

## Resource effect

This report and marker update consume 0 radio bytes. If the device-side server,
DCD, descriptors, function driver or private CarPlay transport components are
not already present, every added file and its update copy counts against the
15 MB installed and 8 MB staging caps. Driver logs/state count against the 4 MB
normal writable limit; no storage allowance is taken from the 45 MB stock
reserve.
