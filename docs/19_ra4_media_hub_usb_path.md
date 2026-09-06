# 19 - RA4 media-hub USB data path

Updated 2026-09-06. This report narrows the physical USB path between the
2014 Grand Cherokee cabin media port and the Harman BE2800 RA4. It is a
read-only correlation of official Mopar catalog/user-guide data, a
Chrysler-attributed connector-end view reproduced by a service-manual mirror,
and official QNX 6.6 CarPlay role-swap behavior. No vehicle, radio, cable,
connector, USB role, or software configuration was changed.

## Decision

**CONFIRMED PRODUCT DISTINCTION:** Mopar lists two different cabin components.
`68141322AA` (superseded by `68289895AA`) is the SD/USB/AUX media-center
hub. `68145567AA` (superseded by `68145567AB`) is a dual USB charging
port. The charging-only part is not evidence for the RA4 data path and must not
be used to infer a second radio-facing USB controller.

**HIGH RADIO-CONNECTOR CLOSURE:** A 2014 Grand Cherokee service-manual mirror
reproduces the Chrysler connector-end view for Radio C2 `D2784B`, a five-
cavity connector. It assigns one USB power circuit, D-, D+, and two cavities
of the same USB ground circuit. This closes the external hub-to-radio cable to
a single USB 2.0-style power/data pair at the radio connector. It does not
identify the BE2800 PCB net or OMAP controller behind that connector.

**HIGH ACTIVE-HUB/MULTIPLEXER INFERENCE:** The stock media-center component
contains both an SD-card reader and a user USB port, while the radio-facing C2
connector exposes only one D+/D- pair. Both data functions therefore cannot be
independent passive conductors to the radio. The module must contain an active
USB hub, a combined reader/hub controller, or a data multiplexer. The exact
silicon and switching behavior remain unknown.

**ROLE-SWAP CONSEQUENCE:** QNX 6.6 CarPlay starts with the radio as USB host,
asks the Apple device to become host, stops `io-usb`, and starts
`io-usb-dcd`. That protocol-controlled swap does not require a cable ID
conductor, so the absence of an ID circuit at D2784B is not by itself a
failure. However, an ordinary fixed-direction active hub between the phone and
the RA4 device controller would not automatically become a reversible path.
The stock hub must be proved role-aware, bypassable, or transparent in the
required state before local wired CarPlay can pass the physical gate.

## Connector evidence

The reproduced Chrysler D2784B table identifies:

| Cavity | Circuit | Function |
| ---: | --- | --- |
| 1 | `X455` | UCI USB power to radio |
| 2 | `X458` | UCI USB radio data (-) |
| 3 | `X457` | UCI USB radio data (+) |
| 4 | `X456` | UCI USB ground to radio |
| 5 | `X456` | UCI USB ground to radio |

The table calls D2784B a five-cavity radio connector and gives Chrysler figure
IDs `GCWD1006600` and `GCWD1003767`. Because the accessible source is a
mirror rather than a live Stellantis service subscription, the pin assignment
is classified HIGH rather than CONFIRMED. It is independently consistent with
the official Mopar catalog's dedicated UCI USB cable `68141323AA` and with
the official user guide's fully functional SD/USB/AUX media hub.

The known external chain is now:

```text
phone / storage device
  -> user USB receptacle in media hub 68141322AA / 68289895AA
  -> active hub/reader or multiplexer behavior (exact silicon unknown)
  -> one upstream USB power, D-, D+, ground path
  -> UCI USB cable 68141323AA
  -> Radio C2 D2784B
       cavity 1 X455 power
       cavity 2 X458 D-
       cavity 3 X457 D+
       cavities 4/5 X456 ground
  -> BE2800 back-board connector field and board-to-board boundary (confirmed)
  -> exact D+/D- pins/nets through the boundary (unknown)
  -> OMAP3730 controller/PHY/VBUS switch (unknown)
```

This replaces the broader "unknown vehicle-harness pins" gap. The cable endpoint
and external circuit family are now identified; the decisive unknowns begin
inside the media hub and behind D2784B on the BE2800 boards.

## Source hierarchy

Primary official sources:

- Mopar 2014 Grand Cherokee instrument-panel catalog, which lists the
  SD/USB/AUX hub and UCI jumper:
  https://store.mopar.com/v-2014-jeep-grand-cherokee--limited--5-7l-v8-gas/electrical--wiring-instrument-panel
- Mopar USB cable `68141323AA`:
  https://store.mopar.com/oem-parts/mopar-usb-cable-68141323aa
- Mopar `68145567AB`, which explicitly describes the superseded AA part as a
  dual USB charging port:
  https://store.mopar.com/oem-parts/mopar-media-hub-usb-port-68145567ab
- 2014 Grand Cherokee user guide, whose media-hub table distinguishes the
  functional media hub, fully functional remote USB, charging-only remote USB,
  and dual charging ports:
  https://vehicleinfo.mopar.com/assets/publications/en-us/Jeep/2014/Grand_Cherokee/100303_14_WK_UG_EN_USC_E11_V1_DIGITAL.pdf
- QNX 6.6 usblauncher service and CarPlay configuration:
  https://www.qnx.com/developers/docs/6.6.0.update/com.qnx.doc.dev_pub.ref_guide/topic/usblauncher.html
  https://www.qnx.com/developers/docs/6.6.0_anm11_wf10/com.qnx.doc.dev_pub.ref_guide/topic/usblauncher_config_supported_applications.html

Supporting service evidence:

- Chrysler-attributed Radio C2 D2784B connector-end view:
  https://lemon-manuals.org.ua/Jeep/2014/Grand%20Cherokee%20Limited%2C%205.7L%20Eng%20VIN%20T%2C%20RWD/Repair%20and%20Diagnosis%20%28Single%20Page%29/Electrical/Body%20Electrical/Connector%20End%20Views%20%26%20Electrical%20Component%20Locations%20%288%20Of%2011%29/Radio%20C2%20%28D2784B%29/

Third-party product photographs are useful only for locating the module and
connector shells. They are not used as proof of circuit function or silicon
identity.

## Official BE2800 board-photo boundary

**CONFIRMED:** pages 13/14 and 17/18 of the official internal-photo exhibit
separately show the main-board and back-board assemblies. The back-board rear
view contains the vehicle-facing connector field, and both assemblies expose
large board-to-board connectors. This establishes an internal rear-I/O to main-
board boundary behind the external D2784B circuit.

**NOT PROVED BY THE PHOTOS:** the exhibit does not label D2784B on the PCB,
show inner-layer copper, identify which board-to-board pins carry D+/D-, or
resolve a USB controller/PHY marking at sufficient quality. Package shape and
proximity are not used as chip identification.

**EXTERNAL_EVIDENCE_REQUIRED:** Harman's FCC confidentiality letter expressly
requests permanent withholding of the BE2800 block diagram, schematics, parts
list, tune-up procedure and operational description. The FCC exhibit index
lists the VP4 NA/CA schematic and block diagram as unavailable. Consequently,
the public FCC record has been exhausted for this net; exact closure now needs
authorized schematic access, macro photographs plus passive continuity on a
spare board, or recovered controller/startup configuration.

Primary filing references:

- internal photographs: https://fccid.io/QNG-BE2800/Internal-Photos/VP4-NA-and-VP4-CA-Internal-Photos-1790035
- permanent-confidentiality request: https://fcc.report/FCC-ID/QNGBE2800/1790067.pdf

## What this proves and does not prove

CONFIRMED:

- the SD/USB/AUX data hub and dual USB charging port are separate products;
- `68141323AA` is the dedicated UCI USB cable;
- QNX's legacy CarPlay swap is protocol-controlled and restarts the car side
  from host stack to device stack.

HIGH:

- the cable terminates at Radio C2 D2784B with one power line, one D-/D+ pair,
  and ground;
- the combined SD-reader/user-USB module necessarily contains active selection,
  hub, or multifunction-controller logic.

UNKNOWN:

- hub controller/multiplexer manufacturer, part number and role behavior;
- whether the phone receptacle can be isolated from the SD reader and presented
  bidirectionally during CarPlay role swap;
- whether VBUS can be removed or reversed safely;
- D2784B-to-OMAP PCB nets, PHY, power switch and controller instance;
- installed OMAP-compatible DCD, descriptors, function driver and startup rule.

## Exact next evidence

The most efficient closure is passive identification of the stock data hub:

1. Obtain authorized macro photographs of both PCB sides of a spare
   `68141322AA` or `68289895AA`, including every IC marking and connector.
2. Record continuity only, unpowered, from user USB D+/D-/VBUS/GND to the
   radio-facing connector and identify any hub/mux/power-switch components.
3. Obtain the D2784B mating connector and BE2800 schematic/net names, or trace a
   spare radio board without powering or modifying it.
4. Correlate recovered startup/configuration evidence for `usblauncher`,
   `io-usb-dcd`, the OMAP DCD DLL, VBUS control and device descriptors.

A fixed hub with no reversible/bypass route makes the stock cabin data path
unsuitable for wired CarPlay, even if OMAP3730 device mode exists. That result
would classify the transport path--not the complete OEM-style HMI--as requiring
an authorized hardware change or external transport. Until the hub silicon is
identified, local wired CarPlay remains plausible but unproved.

## Resource effect

This finding consumes zero radio storage. If the stock hub and DCD path are
reusable, they add no installed bytes. A replacement driver, device function,
or role-control service must be charged to the 15 MB installed cap and 8 MB
staging cap; its logs and state count against the 4 MB writable-growth cap.
No allowance is taken from the 45 MB stock-system reserve.
