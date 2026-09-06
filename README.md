# Jeep Uconnect Custom

Modernize a 2014 Jeep Grand Cherokee WK2 RA4 infotainment experience while preserving factory vehicle functionality.

## Product goal

Integrate native Android Auto and Apple CarPlay as first-class projection
applications inside stock RA4 Uconnect. Production does **not** replace the
factory Radio, Media, Climate, Controls, Phone, Messaging or Settings screens.

Target experience:

- Stock Uconnect remains the ordinary HMI and vehicle-services authority.
- Projection may use the full 640x480 display while active.
- Return to Uconnect and Return to Projection are explicit and easy.
- Returning to projection resumes the session instead of reconnecting it.
- Factory camera and permitted comfort overlays preempt projection and reveal it
  again afterward.
- During an active projection session, projection owns call/message presentation;
  duplicate stock Phone/Messaging foreground UI and audio are suppressed without
  globally disabling Bluetooth/HFP/MAP.
- Emergency/eCall and critical stock presentation remain stock-owned; an ordinary
  camera takeover preserves projection interaction ownership.
- Normal stock phone/message behavior returns when projection is inactive.

## Architecture direction

The working architecture is **RA4-resident first, integration rather than
firmware replacement**. Approximately 77 MB observed free space is shared with
the stock system, not an app allocation. The mandatory
[resource budget](docs/ra4_resource_budget.md) protects 45 MB and provisionally
caps installed app size at 15 MB, runtime growth at 4 MB and additional peak
update/rollback overhead at 8 MB. These are planning caps, not measured artifacts.

```text
Small RA4-resident projection integration (stock AIR/SWF reuse preferred)
  |-- existing display / touch / assets
  |-- existing audio / media services
  |-- existing Harman / PPS vehicle services --> CAN
  `-- optional external capabilities only when local limits require them
```

The original RA4 remains responsible for vehicle-specific logic. New code should consume high-level existing services where possible rather than reimplementing raw CAN behavior.

This supersedes both the earlier external-renderer-first proposal and the later
six-screen replacement-shell interpretation. First determine the largest credible
software-only projection integration. A complete legitimate projection engine
remains unresolved; classify it `EXTERNAL_COMPUTE_REQUIRED` only when measured
local storage/CPU/RAM feasibility fails. PC mocks and analysis tools remain
outside deployment.

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

Current product integration: the [projection foreground-ownership report](reports/projection_foreground_ownership.md)
traces stock session/display separation, call/SMS presentation, foreground
arbitration, camera return and comfort-popup reuse. The separate
[read-only driver-temperature contract](reports/ra4_driver_temperature_contract.md)
remains active research; its prototype stays mock-only and no radio subscription
or control is enabled.

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

The resident product slice is a tiny projection integration layer inside stock
Uconnect. The refocused [PC prototype](prototype/resident_hmi/README.md) is an
executable projection-ownership and failure-policy bench; it contains no
replacement Radio, Media, Climate, Controls, Phone, Messaging or Settings UI.

1. Complete projection foreground and Return-to-Uconnect contract recovery.
2. Trace projection-back, comfort-popup and audio-focus XREFs.
3. Establish authorized app/screen lifecycle and measure a tiny target trial.
4. Prove camera, popup, phone/message arbitration, fallback and resource headroom.
5. Continue read-only temperature-quality research independently.

See `docs/` and the GitHub issue tracker for the detailed plan.
