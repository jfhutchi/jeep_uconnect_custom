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

**RA4 BOARD/BSP UNKNOWN:** the physical head-unit port must be wired to the
dual-role controller and suitable PHY/VBUS/ID path, and the installed runtime
must include an OMAP-compatible `io-usb-dcd` controller DLL plus the
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
| RA4 host path | `io-usb`, `libusbdi`/usbd APIs and factory USB utility evidence | CONFIRMED |
| RA4 Apple-adjacent path | `itun`, `libipod`, iPod/media integration and CarPlay HMI vocabulary | CONFIRMED adjacent capability |
| RA4 device stack | `io-usb-dcd`, controller DLL, function driver, descriptors, startup and port mapping | UNKNOWN |
| physical port | actual SoC controller, PHY, ID/VBUS switching, hub path and connector wiring | EXTERNAL_EVIDENCE_REQUIRED |
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

The 94-marker recovered-tree probe now includes:

- `io-usb-dcd`
- `devu-dcd`
- `ulink_ctrl`
- `usblauncher`
- `RoleSwap_DigitaliPodOut`
- `RoleSwap_AppleDevice`
- iAP2/iPod and projection-service anchors

For every hit, preserve only relative path, size, SHA-256 and controlled marker
metadata, then establish:

1. ELF architecture/imports without execution.
2. Startup command and loaded DCD DLL name.
3. Controller base/IRQ and OMAP/board association.
4. Host/device stack transition and descriptor/function-driver configuration.
5. Mapping from that controller instance to the external phone port.
6. Version/permission/owner-death behavior and licensed caller contract.

A complete recovered-tree negative for `io-usb-dcd`/DCD/startup would make an
authorized QNX/Harman driver addition necessary. It would not justify copying a
generic DCD, changing boot files, or experimenting on the vehicle radio.

## Bench closure

Only separately authorized spare hardware can close physical routing and
electrical role switching. The first observation should be passive inventory:
controller/driver argv, loaded modules, device nodes and port topology. Any
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
