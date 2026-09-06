# 07 - Product-first next steps

Updated 2026-09-06. Production is projection inside stock Uconnect, not a
replacement six-screen shell. The PC prototype remains useful only for state,
adapter, legibility and failure-policy tests.

## Next highest-value static task

1. Add reusable property/multiname consumer XREFs to `swf_abc_inspect`.
2. Trace `PROJECTION_BACKTO_CAR`, `DEVICE_PROJECTION` and the projection
   screen's Return-to-Uconnect control.
3. Trace heated-seat/heated-wheel popup events.
4. Trace projection/HFP audio focus separately from visual foreground ownership.

Current evidence: [projection foreground ownership](../reports/projection_foreground_ownership.md).

Continue the [driver-temperature trace](../reports/ra4_driver_temperature_contract.md)
independently: close units-change/service-restart quality and stale-cache behavior
without adding a live radio subscription or replacement Climate screen.

## Static-contract exit

Recover session versus foreground lifecycle, return/resume behavior, call/SMS
visual and audio gates, camera stack return, permitted overlays and temperature
quality with explicit CONFIRMED/HIGH/INFERRED/UNKNOWN evidence.

## Authorized lifecycle/resource proof

Establish a supported screen/app boundary and compatible toolchain. Build only a
tiny integration trial. Measure installed bytes, runtime writes, update peak, RAM,
CPU and startup. Preserve the 45 MB stock reserve. No roadmap step authorizes radio
modification.

## Bench-only proofs

Under separate authorization on spare hardware: show/hide projection through the
stock arbiter; verify camera/popup priority; verify Return to Uconnect and session
resume; verify no duplicate call/SMS foreground or TTS while active and normal
behavior while inactive; verify crash fallback.

## Engine feasibility

Evaluate a legitimate engine against local storage, RAM, CPU, video, touch, USB
and audio contracts. Do not choose external hardware merely for convenience. Mark
the engine `EXTERNAL_COMPUTE_REQUIRED` only if resident feasibility fails while
keeping the RA4 integration layer tiny.

## Definition of done

Projection behaves like an OEM Uconnect application: full-screen when selected,
easy to leave/resume, subordinate to camera/critical overlays, compatible with
temporary comfort popups, and sole presenter of projected calls/messages while
active. Ordinary factory screens and disconnected behavior remain stock.
