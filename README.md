# Jeep Uconnect Custom

Modernize a 2014 Jeep Grand Cherokee WK2 RA4 infotainment experience while preserving factory vehicle functionality.

## Product goal

Build a newer-Uconnect-inspired interface with native Android Auto and Apple CarPlay integration while retaining the stock RA4 as the vehicle-services authority for Jeep-specific functions.

Target experience:

- Modern Jeep/Uconnect-style 640x480 HMI
- Native Android Auto for Android phones
- Native Apple CarPlay for iPhone
- Heated seats preserved
- Heated steering wheel preserved
- Dual-zone HVAC preserved
- Factory backup camera preserved
- Vehicle settings preserved
- Factory steering-wheel controls preserved
- Factory audio path preserved
- Safe fallback to the stock RA4 UI

## Architecture direction

The working architecture is **RA4-resident first, integration rather than
firmware replacement**. Approximately 77 MB observed free space is shared with
the stock system, not an app allocation. The mandatory
[resource budget](docs/ra4_resource_budget.md) protects 45 MB and provisionally
caps installed app size at 15 MB, runtime growth at 4 MB and additional peak
update/rollback overhead at 8 MB. These are planning caps, not measured artifacts.

```text
Tiny RA4-native HMI / integration process (feasibility target)
  |-- existing display / touch / assets
  |-- existing audio / media services
  |-- existing Harman / PPS vehicle services --> CAN
  `-- optional external capabilities only when local limits require them
```

The original RA4 remains responsible for vehicle-specific logic. New code should consume high-level existing services where possible rather than reimplementing raw CAN behavior.

This supersedes the earlier external-renderer-first proposal. First determine
the largest credible software-only HMI; do not add external hardware solely for
development convenience. Projection-engine feasibility and size are unresolved.
Capabilities that cannot fit or execute locally must be explicitly classified
`EXTERNAL_COMPUTE_REQUIRED`, not deferred to hypothetical optimization. PC mocks
and analysis tooling must remain outside the deployable package.

## Verified research findings

Current analysis of RA4 18.45.01 shows:

- QNX on 32-bit ARM, with TI OMAP3730 evidence
- Adobe AIR / SWF HMI targeting 640x480
- QNX Screen / mtouch infrastructure for display and touch
- Harman ModuleLink / service-oriented middleware
- QNX PPS used around vehicle data and CAN services
- Factory HMI references projection-related concepts including CarPlay, GAL, `IPhoneProjection`, `PhoneProjectionEvent`, and `phoneProjectionService`
- Persistency schema includes projection properties such as `enableCarplay`, `enableAndroidAuto`, `Projection_AutoShow`, and `projectionAutoPlay`
- Core runtime includes QNX display, USB, audio and iPhone-accessory infrastructure
- An original 2017Q2 VP4 navigation-update image has been recovered and analyzed read-only, including FAT corruption/recovery, nested SWDL/installer ISOs, a successful MY14 runtime update log, and the stripped ARM32 Synctool license-classification flow

These findings do **not** imply that a hidden switch alone enables CarPlay or Android Auto. The actual projection backend appears to be absent or incomplete in the RA4 build.

Detailed navigation-update findings: [`reports/map_update_2017q2_reverse_engineering.md`](reports/map_update_2017q2_reverse_engineering.md).

The focused [Synctool device/license-selection report](reports/synctool_device_license_selection.md)
traces the App-SKU virtual query, corrects the SWID-property data-flow direction,
identifies the scanner key as a runtime source-container ordinal, and follows
record-group pruning into filename exclusion from the copy plan.
[Reusable analysis tools](analysis_tools/README.md) include hash-gated static
evidence checks and a read-only diagnostic-marker probe. The exact numerical
MY14 REVA record mapping remains unobserved; the successful filename and the
generic selection mechanism are established separately.

## Safety / scope

This project is analysis-first.

- Do not modify or generate flashable RA4 firmware as an initial strategy.
- Do not bypass FCA/Harman signing protections.
- Do not execute unknown firmware binaries on development workstations.
- Do not use direct CAN control for safety-critical systems.
- Bench-test integration work before testing on the vehicle's only working radio.
- Preserve a stock-UI fallback path.

## Current milestones

1. Reconstruct the projection-facing HMI contract.
2. Document RA4 display, touch, audio and vehicle-service interfaces.
3. Design a modern Uconnect-inspired 640x480 HMI.
4. Validate the resident-first resource budget and isolate any capabilities that genuinely require external compute.
5. Build bench-test tooling around a spare RA4.
6. Prototype display/touch/audio integration.
7. Integrate a legitimate Android Auto / CarPlay projection engine.
8. Validate vehicle controls and fallback behavior.

See `docs/` and the GitHub issue tracker for the detailed plan.
