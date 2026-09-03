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

The working architecture is **integration, not firmware replacement**:

```text
Phone(s)
  |-- Android Auto
  `-- Apple CarPlay
        |
        v
Hidden projection / modern-HMI compute layer
        |
        |-- video --> factory display path
        |-- touch <-- factory QNX Screen / mtouch path
        |-- audio --> factory multimedia/audio path
        `-- vehicle controls <--> stock RA4 services
                                  |
                                  v
                           PPS / Harman middleware
                                  |
                                  v
                                 CAN
```

The original RA4 remains responsible for vehicle-specific logic. New code should consume high-level existing services where possible rather than reimplementing raw CAN behavior.

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

These findings do **not** imply that a hidden switch alone enables CarPlay or Android Auto. The actual projection backend appears to be absent or incomplete in the RA4 build.

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
4. Define the hidden-compute bridge architecture.
5. Build bench-test tooling around a spare RA4.
6. Prototype display/touch/audio integration.
7. Integrate a legitimate Android Auto / CarPlay projection engine.
8. Validate vehicle controls and fallback behavior.

See `docs/` and the GitHub issue tracker for the detailed plan.
