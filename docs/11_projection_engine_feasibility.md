# 11 - Legitimate projection-engine feasibility

Updated 2026-09-06. This is a current official-source screen for a legitimate
CarPlay/Android Auto engine that could preserve the resident-first RA4
architecture. It does not approve an SDK, establish access rights, prove target
compatibility, or authorize installation.

## Decision

**CANDIDATE FAMILY IDENTIFIED:** QNX SDK for Smartphone Connectivity is the only
currently identified first-party product family whose public description matches
the required resident projection boundary closely enough to advance.

**NOT BUDGET-APPROVED / TARGET COMPATIBILITY UNKNOWN:** No public source supplies
a compatible RA4 build, exact target ABI/OS support, installed/runtime size, RAM,
CPU, GPU, USB/authentication requirements or redistribution permission.
Therefore the engine remains an evidence gate. It is not yet classified
EXTERNAL_COMPUTE_REQUIRED because local feasibility has not been tested with a
legitimate compatible build.

## Why this candidate matches

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

A bounded search of QNX's public archive found Smartphone Connectivity 2.0
documentation in the collection for SDP 7.x/8.0-compatible products, but no
public 1.x or SDP 6.x Smartphone Connectivity package. This does not prove a
licensed legacy build never existed; it means the public archive cannot close
the compatibility gate:

- https://www.qnx.com/download/group.html?programid=29183

QNX 7's official `usblauncher_otg` documentation describes dedicated Android
and Apple modules that support projection-related USB personality/role behavior
and directs integrators to the Smartphone Connectivity Developer's Guide. This
is further evidence that a legitimate engine includes platform USB integration,
not only a small video decoder:

- https://get.qnx.com/developers/docs/7.0.0/com.qnx.doc.dev_pub.ref_guide/topic/usblauncher_usage.html

The tracked RA4 evidence confirms QNX USB infrastructure, `libusbdi`, `itun`
and legacy Apple media integration, but does not confirm this launcher, its
projection modules or an equivalent compatible contract. Absence from the
tracked evidence is not a full firmware-corpus negative until local search runs.

This produces three legitimate routes to evaluate:

| Route | Current status | Required evidence |
| --- | --- | --- |
| QNX provides an older compatible licensed projection package for the RA4 generation | UNKNOWN | supported OS release, ARMv7/SoC/BSP, package manifest, dependencies, certification and redistribution terms |
| QNX/provider ports the current projection manager to the authorized RA4 platform | UNKNOWN | written support scope, toolchain/BSP requirements, resource estimate and integration contract |
| no supported local package exists or it exceeds measured limits | NOT YET PROVED | failed compatibility/resource gate; then classify only the engine EXTERNAL_COMPUTE_REQUIRED |

An end-of-life page is not proof that licensed legacy support is impossible.
Conversely, an advertised QNX product is not proof of RA4 compatibility.

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
is favorable but supplies no sizes. The candidate is rejected locally if any
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

The local-first architecture remains credible enough to investigate because a
first-party QNX projection-manager product family exists and maps to the recovered
platform services. The exact RA4 implementation is not currently obtainable from
public material. The next technical decision depends on authorized QNX/Apple/
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
