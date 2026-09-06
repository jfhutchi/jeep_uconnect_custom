# 11 - Legitimate projection-engine feasibility

Updated 2026-09-06. This is a current official-source screen for a legitimate
CarPlay/Android Auto engine that could preserve the resident-first RA4
architecture. It does not approve an SDK, establish access rights, prove target
compatibility, or authorize installation.

## Decision

**CURRENT QUALIFICATION:** QNX SDK for Smartphone Connectivity and Cinemo CORE
Projection are legitimate provider-contact candidates. The stock HMI's Cinemo
error constants now give the latter a specific RA4 research connection. Neither
provider has confirmed an available, authorized QNX 6.5/RA4 build. No provider
was contacted and no proprietary binary was obtained in this run.

**PUBLIC 2.0 DIRECT-BINARY PATH REJECTED FOR RA4:** the official documentation
collection places Smartphone Connectivity 2.0 with QNX SDP 7.x-compatible
products, and its license supplement explicitly requires QNX SDP 7.x developer
licenses. Recovered RA4 startup identifies QNX 6.5 (`qnx650`), ARM32;
the previous QNX 6.6 target assertion was incorrect. No cross-version ABI
compatibility may be assumed, including between the 6.6 references and RA4.
Version 2.0 can advance only if QNX supplies a supported RA4-compatible build or
an authorized source-port path. Public 2.0 binaries are not a deployable candidate.

**LEGACY QNX 6.6 CARPLAY TRANSPORT CONFIRMED REFERENCE:** QNX's 6.6-era
Device Publishers guide explicitly documents `usblauncher`,
`RoleSwap_DigitaliPodOut`, host-to-device stack transition, and
`io-usb-dcd` for Apple CarPlay, and directs integrators to QNX support for the
automotive iOS drivers. This proves a supported legacy transport family existed. TI confirms the SoC
has a dual-role OTG controller, but QNX's public OMAP3730 BSP feature table lists
OTG only as host; it does not identify the receiver binary, establish the custom
RA4 DCD/port route, or supply licensed components.

**NOT BUDGET-APPROVED / TARGET COMPATIBILITY UNKNOWN:** No public source supplies
a compatible RA4 build, exact target ABI/OS support, installed/runtime size, RAM,
CPU, GPU, USB/authentication requirements or redistribution permission.
Therefore the engine remains an evidence gate. It is not yet classified
EXTERNAL_COMPUTE_REQUIRED because local feasibility has not been tested with a
legitimate compatible build.

## Current provider qualification matrix

Checked 2026-09-06 against primary provider/program sources. Every candidate
must preserve the existing Uconnect HMI and independent camera/critical paths;
CarPlay Ultra or a replacement digital cockpit is outside this project's scope.

| Provider/path | Engine | OS / ARM evidence | Transport / hardware-video assumptions | Authorization / availability | Installed bytes, RAM, CPU / <=15 MB cap |
| --- | --- | --- | --- | --- | --- |
| QNX Smartphone Connectivity supported legacy build or authorized port | Android Auto | Product family names ARM; public 2.0 license is SDP 7.x; exact QNX 6.5 ARM32 build UNKNOWN | Projection-manager USB/media integration; exact RA4 codec/Screen ABI and 640x480 support UNKNOWN | EXTERNAL_PROVIDER_GATE: QNX supply/support and Google receiver/program qualification; no public app SDK substitutes | All target measurements UNKNOWN; not budget-approved |
| QNX legacy Apple transport plus supported receiver | CarPlay | QNX 6.6 transport documented; RA4 6.5 DCD/receiver compatibility UNKNOWN | Documented host-to-device transition; automotive iOS drivers, DCD, reversible hub/PHY path and decoder required for that route | EXTERNAL_PROVIDER_GATE: QNX support and Apple MFi; no installed receiver identified | All target measurements UNKNOWN; every added driver/dependency counts |
| Cinemo CORE Projection authorized QNX 6.5 port/build | Android Auto | Current SDK advertises cross-platform OS/SoC support; exact 6.5/ARMv7 ABI support UNKNOWN | Provider advertises USB and wireless; exact decoder/GPU/memory contract and minimum hardware UNKNOWN | EXTERNAL_PROVIDER_GATE: commercial provider and Google qualification; project eligibility/legacy support unconfirmed | Marketing says low CPU/memory; no numeric installed/RAM/CPU figures; cap UNKNOWN |
| Cinemo CORE Projection authorized legacy integration | CarPlay | Current family supports QNX; local HMI names Cinemo CarPlay errors, but no engine binary/version | USB/wireless advertised; RA4 transport/authentication hardware/video requirements UNKNOWN | EXTERNAL_PROVIDER_GATE: Cinemo/Harman integration contract plus Apple MFi, permitted distribution and package authorization | No numeric target figures; all added runtime dependencies count; cap UNKNOWN |
| Harman/OEM supplies the matching optional service + screen package | Android Auto and CarPlay, separately qualified | Exact `phoneProjectionService` client contract STATIC_PROVED; native package identity/OS build UNKNOWN | Must disclose `DeviceConnectionManager`, service registration, screen loader, codec/audio/USB interfaces | EXTERNAL_PROVIDER_GATE: matching release manifest and legitimate package issuer; current Harman engineering services do not prove an RA4 retrofit offer | Package manifest, per-engine bytes and measurements UNKNOWN |

The [Cinemo CORE Projection page](https://automotive.cinemo.com/products-and-services/cinemo-core/core-projection/)
offers an integration SDK for Android Auto and CarPlay with USB/wireless
transports. Its platform and footprint claims provide no minimum RAM/CPU,
installed-size figure or QNX release/ABI guarantee. Cinemo's
[QNX platform statement](https://automotive.cinemo.com/carplay-ultra-integration-for-oems/)
concerns its current product family, including Ultra; it is not evidence that
this RA4 can run that package or a reason to adopt Ultra.

The original [local backend census](../reports/ra4_usb_stack_backend_census.md)
links HMI constants `CARPLAY_CINEMO_START_ERROR=1000` and
`CARPLAY_CINEMO_STOP_ERROR=1001` to the wrapper that sends `startProjection`.
**INFERRED:** Cinemo/Harman can be asked a much more specific legacy-component
question. **UNKNOWN:** the intended provider version, whether code was ever
shipped for this hardware and whether an individual owner can license it.

[Harman's engineering-services page](https://car.harman.com/solutions/automotive-engineering-services/software-integrator-services/digital-cockpit-engineering-services)
lists QNX platform work and Android Auto/CarPlay integration. This supports an
engineering/provider inquiry, not an available RA4 product. The decisive request
is the signed component manifest and API contract for the named stock services,
not a generic promise of smartphone integration.

For every row, request separate Android Auto and CarPlay bills of materials,
exact QNX 6.5/ARM little-endian toolchain/ABI support, incremental installed and
peak writable bytes, RAM/CPU, hardware decode assumptions, 640x480 modes,
transport interfaces, authorization/certification responsibilities, maintenance
and redistribution terms. Apple's [vehicle-system guidance](https://developer.apple.com/carplay/)
routes CarPlay implementers to MFi. Google's [Android for Cars material](https://developers.google.com/cars/)
does not establish public head-unit receiver redistribution rights; confirm the
actual receiver/program route with the provider and Google. Public AOA transport
documentation alone supplies no Android Auto engine authorization.

The QNX [2.0 license supplement](https://www.qnx.com/download/download/40452/QNX_Smartphone2.0_LicenseSupplement_v1.0.pdf)
still explicitly refers to commercial SDP 7.x licenses and Apple-license/MFi
status for its CarPlay components. Its dependencies and source-port rights must
be qualified for this project; a license document is not a binary ABI test.
The older product-brief URL now redirected to the QNX homepage when opened;
the indexed brief and current connectivity page establish a family, not access
to a supported legacy download.

No measured local storage, RAM, CPU or transport failure has selected external
compute. Lack of a provider response is an external gate, not such a failure.
The PC DHU remains a development reference, not a redistributable RA4 engine.

## Why the QNX candidate matches

The current QNX connectivity page states that QNX Multimedia Suite is designed
to work with QNX SDK for Smartphone Connectivity and names Apple CarPlay and
Android Auto as integrated projection experiences:

- https://qnx.software/en/software/technologies/middleware/connectivity

QNX's official product brief describes a projection-manager framework with
CarPlay and Android Auto plug-ins. It also identifies the exact integration
surfaces this project recovered independently: HMI, video rendering/display
composition, touch/hard buttons, audio management, USB, Wi-Fi, Bluetooth,
NowPlaying audio-source arbitration and optional acoustic echo/noise handling:

- https://blackberry.qnx.com/content/dam/qnx/products/qnxcar/QNX_SDKForSmartphone_ProductBrief_Online_FINAL.pdf

This is a strong architectural match. It supports the resident-first sequence:

```text
licensed phone-projection plug-in
        |
QNX projection manager
        |
stock-facing RA4 adapter
        |
stock HMI / Screen / MME / AudioCtrlSvc / USB / Bluetooth
```

It does not prove that the product can be installed beside the RA4 18.45.01
stack, fit the resource envelope, or bind to Harman's existing
phoneProjectionService contract.

## Licensing and access gates

Apple's official CarPlay page directs vehicle-system implementers interested in
supporting CarPlay to the MFi program. Apple's accessory page states that MFi
provides licensed technical specifications, hardware components, certification
tools and related resources:

- https://developer.apple.com/carplay/
- https://developer.apple.com/accessories/

The official QNX Smartphone Connectivity 2.0 license supplement says the
examined product is licensed per development project and depends on valid
commercial QNX SDP 7.x developer licenses. For the CarPlay integration package,
QNX may distribute the components only to Apple licensees and requires disclosure
of MFi license status before providing the components/documentation. It also
names a dependency on QNX Multimedia Interface for Apple iPod 2.0.0:

- https://www.qnx.com/download/download/40452/QNX_Smartphone2.0_LicenseSupplement_v1.0.pdf

These are product-access requirements, not technical obstacles to bypass. This
project will not source leaked SDKs, reuse OEM credentials, emulate protected
authentication, or create unsigned/unlicensed projection packages.

Google's public Android for Cars material confirms that Android Auto is
phone-based projection to compatible head units. Public app-developer guidance
covers phone apps, while partner/early-access information routes implementers to
their Google point of contact; it does not expose a general public head-unit
receiver SDK:

- https://developers.google.com/cars/

Accordingly, a legitimate Android Auto head-unit implementation also requires an
authorized provider/partner path. The Android for Cars App Library is not a
head-unit projection engine.

## Version and lifecycle risk

The official QNX CAR Platform for Infotainment 2.1 download page says that
platform uses QNX SDP 6.6 and is end-of-life as of 2024-02-29. Its host
development packages are hundreds of megabytes, but those download sizes are not
target runtime footprint measurements and must not be charged directly to the
77 MB radio budget:

- https://qdn.qnx.com/download/group.html?programid=26076

The public Smartphone Connectivity 2.0 license material instead references QNX
SDP 7.x. The RA4 corpus proves 32-bit little-endian ARM/QNX but does not yet
establish a supported QNX SDK release/ABI for this package. No cross-version
binary compatibility may be assumed.

A bounded search of QNX's product archive found Smartphone Connectivity 2.0
documentation in the collection for SDP 7.x/8.0-compatible products, but no
public 1.x Smartphone Connectivity package. Separately, QNX 6.6-era Device
Publishers documentation explicitly supports the CarPlay USB transport/role-swap
sequence and says the required automotive iOS drivers come through QNX support.
Therefore the archive cannot close receiver availability, but legacy CarPlay
transport is no longer merely hypothetical:

- https://www.qnx.com/download/group.html?programid=29183
- https://www.qnx.com/developers/docs/6.6.0_anm11_wf10/com.qnx.doc.dev_pub.ref_guide/topic/usblauncher_config_supported_applications.html
- https://get.qnx.com/developers/docs/6.6.0.update/com.qnx.doc.dev_pub.ref_guide/topic/usblauncher.html

QNX 7's official `usblauncher_otg` documentation describes dedicated Android
and Apple modules that support projection-related USB personality/role behavior
and directs integrators to the Smartphone Connectivity Developer's Guide. This
is further evidence that a legitimate engine includes platform USB integration,
not only a small video decoder:

- https://get.qnx.com/developers/docs/7.0.0/com.qnx.doc.dev_pub.ref_guide/topic/usblauncher_usage.html

The tracked RA4 evidence confirms QNX USB infrastructure, `libusbdi`, `itun`
and legacy Apple media integration. The QNX 6.6 reference now identifies exact
legacy candidates: `usblauncher`, `io-usb-dcd`, role-swap rules/descriptors and
support-supplied automotive iOS drivers. The current
[structured census](../reports/ra4_usb_stack_backend_census.md) found no matching
named bundle across materialized files, dynamic metadata and ZIP/JAR member
names. This bounded negative does not exclude private/renamed or unmaterialized
code and does not establish that a compatible external provider package exists.

This produces three legitimate routes to evaluate:

| Route | Current status | Required evidence |
| --- | --- | --- |
| QNX supplies the legacy QNX 6.6 CarPlay transport drivers plus a compatible licensed receiver for the RA4 generation | TRANSPORT FAMILY CONFIRMED REFERENCE / RECEIVER UNKNOWN | exact driver/receiver names, ARMv7/SoC/BSP/controller support, package manifest, dependencies, certification and redistribution terms |
| QNX/provider ports the current projection manager to the authorized RA4 platform | UNKNOWN | written support scope, toolchain/BSP requirements, resource estimate and integration contract |
| no supported local package exists or it exceeds measured limits | NOT YET PROVED | failed compatibility/resource gate; then classify only the engine EXTERNAL_COMPUTE_REQUIRED |

An end-of-life page is not proof that licensed legacy support is impossible.
Conversely, an advertised QNX product is not proof of RA4 compatibility.

## Hardware and media-runtime boundary

The [RA4 hardware/codec feasibility report](12_ra4_projection_hardware_feasibility.md)
now separates silicon capability from installed runtime availability. Exact RA4
configuration and TI documentation make 640x480 accelerated projection
plausible, but no stock H.264/DSP decoder ABI is yet proved. QNX's public
QNX 6.4-era OMAP Codec Engine example confirms an integration family existed,
but its prebuilt MME filter was audio-only and its example reserved 40 MiB of
RAM for codec-engine/DSPLink regions. That reference is neither an RA4 footprint
nor a reason to reject local execution; it makes the recovered codec/startup
census and actual RAM measurement mandatory.

## Information request for candidate qualification

Before obtaining binaries or beginning integration, request written answers from
QNX and the applicable Apple/Google program contacts:

1. Exact supported QNX Neutrino/SDP releases, ARM instruction set/ABI, libc/C++
   ABI and BSP/SoC prerequisites.
2. Whether an ARM32 build compatible with the RA4 generation exists and may be
   evaluated on owner-controlled spare hardware.
3. Per-component target runtime package sizes for projection manager, CarPlay,
   Android Auto, multimedia patches, USB/network plug-ins and mandatory private
   libraries.
4. Steady and peak RAM, graphics/video buffers, CPU, hardware-codec requirements,
   startup time and supported 640x480 modes.
5. Writable configuration, pairing/authentication state, logs, cache, crash data
   and update/rollback staging requirements.
6. Required Bluetooth, HFP, MAP, iAP2, USB, Wi-Fi, audio, microphone and
   NowPlaying interfaces, including whether `usblauncher_otg` or an older
   equivalent is mandatory.
7. HMI/service API for foreground, Return to Car, session resume, calls,
   messaging, camera/overlay coexistence and owner-death fallback.
8. MFi/CarPlay and Google Android Auto partner/certification steps for a retrofit
   owner project, including whether evaluation or distribution is permitted.
9. Whether stock codecs, QNX Screen, MME/AudioCtrlSvc and existing Harman services
   can be reused without bundling duplicate runtime components.
10. Supported security/update/package lifecycle; no signature or authentication
    bypass is acceptable.

A useful response contains component-level target bytes, not a host SDK download
size or marketing statement.

## Resource qualification

The complete product caps remain:

| Resource | Gate |
| --- | ---: |
| installed total including private engine dependencies | <=15 MB |
| normal writable growth | <=4 MB |
| additional update/staging/rollback peak | <=8 MB |
| protected stock-system reserve | >=45 MB |
| planned peak residual margin from approximately 77 MB | >=5 MB |

The stock-facing adapter retains its 256 KiB installed sub-budget. Candidate
qualification must count every new runtime file and allocated block. Existing
stock facilities count as zero new installed bytes only after ABI and permitted
reuse are proved; their attributable runtime state/cache still counts.

The QNX product brief indicates modularity and stock-service integration, which
is favorable but supplies no sizes. TI codec download-package sizes are also not
target installed sizes and receive no budget credit or charge. The candidate is rejected locally if any
mandatory component forces the complete package above the caps or if RAM/CPU/GPU
and latency fail on spare hardware. Do not reduce the stock reserve to make it
fit.

## Open-source and unofficial implementations

No open-source or unofficial receiver is accepted as a production candidate in
this pass. Public source availability alone does not establish current protocol
authorization, Apple/Google certification, authentication hardware, QNX/ARM32
support, vehicle-safe audio/call behavior, or redistribution rights. Such code
may inform non-protocol host mocks only; it cannot close the legitimate-engine
gate.

## Outcome

The local-first architecture is strengthened by two first-party lines: a QNX
6.6-era CarPlay USB transport contract and the later modular projection-manager
product family. The exact RA4 receiver, driver bundle and supported integration
remain unavailable from public material. The next technical decision depends on authorized QNX/Apple/
Google compatibility and component-size data, followed by a spare-radio
measurement. Until then:

- tiny RA4 resident adapter: required and within the provisional architecture;
- complete resident projection engine: legitimate candidate exists, feasibility
  UNKNOWN;
- external engine: contingency only, not selected;
- replacement HMI: rejected;
- signing/authentication workaround: rejected.

## Resource effect

This research adds documentation only: 0 installed radio bytes, 0 radio writable
growth and 0 radio staging bytes.
