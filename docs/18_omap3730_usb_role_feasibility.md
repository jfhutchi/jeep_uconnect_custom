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

**RA4 EXTERNAL USB CIRCUITS HIGH / INTERNAL ROUTE UNKNOWN:** the exact Harman
BE2800 platform and remote Mopar data hub/cable are identified. A Chrysler-
attributed connector-end view maps the cable to Radio C2 `D2784B`: `X455`
power, `X458` D-, `X457` D+, and `X456` ground on two cavities. The combined
SD-reader/USB module exposes only this one upstream pair, so active hub,
multifunction-controller, or multiplexer logic is required. Its role behavior,
D2784B-to-OMAP nets, PHY/VBUS switching and installed DCD remain unknown. The
runtime must include an OMAP-compatible `io-usb-dcd` controller DLL plus the
CarPlay function/descriptor path.

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
| cabin media port | Mopar lists the 2014 Grand Cherokee SD/USB/aux hub and separate UCI USB jumper; separately lists 68145567AA/AB as dual charging ports | CONFIRMED product/topology distinction |
| radio cable endpoint | Chrysler-attributed connector view maps Radio C2 D2784B to X455 power, X458 D-, X457 D+, X456 ground | HIGH exact external circuit map |
| media-hub internals | SD reader and user USB share one upstream D+/D- pair, requiring active hub/controller/mux logic | HIGH architecture inference / silicon UNKNOWN |
| RA4 host path | `io-usb`, `libusbdi`/usbd APIs and factory USB utility evidence | CONFIRMED |
| RA4 Apple-adjacent path | `itun`, `libipod`, iPod/media integration and CarPlay HMI vocabulary | CONFIRMED adjacent capability |
| RA4 device stack | `io-usb-dcd`, controller DLL, function driver, descriptors, startup and port mapping | UNKNOWN |
| physical role route | hub silicon/role behavior, D2784B-to-BE2800 nets, SoC controller, PHY and VBUS switching | EXTERNAL_EVIDENCE_REQUIRED |
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
- Official Mopar dual charging-port 68145567AB page:
  https://store.mopar.com/oem-parts/mopar-media-hub-usb-port-68145567ab
- Official 2014 Grand Cherokee user guide, including the functional-versus-
  charging USB table:
  https://vehicleinfo.mopar.com/assets/publications/en-us/Jeep/2014/Grand_Cherokee/100303_14_WK_UG_EN_USC_E11_V1_DIGITAL.pdf
- Chrysler-attributed Radio C2 D2784B connector-end view (service-manual
  mirror; supporting rather than primary authority):
  https://lemon-manuals.org.ua/Jeep/2014/Grand%20Cherokee%20Limited%2C%205.7L%20Eng%20VIN%20T%2C%20RWD/Repair%20and%20Diagnosis%20%28Single%20Page%29/Electrical/Body%20Electrical/Connector%20End%20Views%20%26%20Electrical%20Component%20Locations%20%288%20Of%2011%29/Radio%20C2%20%28D2784B%29/

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

**HIGH EXTERNAL CIRCUIT MAP:** the Chrysler-attributed D2784B connector view
maps the UCI cable at the radio to one USB power circuit, D-, D+, and duplicate
USB ground cavities. The official user guide and Mopar catalog separately
identify the functional SD/USB/AUX data hub and the optional charging-only USB
modules. Therefore 68145567AA/AB is not a second RA4 data path.

**HIGH ACTIVE-MODULE INFERENCE:** the stock module presents both an SD reader
and a user USB port over the single upstream D+/D- pair. It therefore cannot be
a passive receptacle assembly; active hub, multifunction-controller, or
multiplexer logic is required. Its exact silicon and ability to reverse or
bypass the path remain unknown.

The board-level unknown is now narrower but still decisive:

```text
cabin media hub 68141322AA / 68289895AA
  -> unknown active hub/reader or mux behavior
  -> USB jumper 68141323AA
  -> Radio C2 D2784B: X455 power, X458 D-, X457 D+, X456 ground
  -> unproved BE2800 rear-board/main-board route
  -> unproved OMAP3730 OTG controller and PHY/VBUS switching
```

The absence of a separate ID circuit at D2784B is not by itself a blocker:
QNX's documented CarPlay transition is a protocol-requested role swap followed
by host-stack shutdown and device-stack startup. The active media hub is the
stronger concern. It must be role-aware, bypassable, or transparent after the
phone becomes host; an ordinary fixed-direction hub would not establish that
path. Exact hub silicon, VBUS behavior and board net names remain required.
See [RA4 media-hub USB data path](19_ra4_media_hub_usb_path.md).

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
