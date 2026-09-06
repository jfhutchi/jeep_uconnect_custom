# 02 - Current RA4 Architecture

This document records the current evidence from static analysis of RA4 18.45.01.

## Mandatory resource constraint

The owner reports approximately 77 MB free writable storage, shared with stock
operation. The [resource budget](ra4_resource_budget.md) protects 45 MB, with
provisional app caps of 15 MB installed, 4 MB writable growth and 8 MB additional
peak staging/rollback. Sizes and runtime peaks remain unmeasured. Architecture
must prioritize a tiny resident HMI/integration layer, reuse stock assets
and services, and justify any `EXTERNAL_COMPUTE_REQUIRED` feature individually.
The presence of stock facilities below does not yet prove their APIs/ABIs are
usable by a new app, nor that a complete projection backend fits locally.

The [resident implementation decision](resident_hmi_decision.md) compares stock
AIR/SWF, native QNX, hybrid and existing Java/Lua facilities. It provisionally
prefers stock AIR/SWF reuse, not native code by default; installation and
independent fallback remain UNKNOWN. A PC-only mock shell now exists.

## VERIFIED

### Platform

- QNX on 32-bit ARM.
- TI OMAP3730 platform evidence exists in device/boot/graphics component names.
- Factory HMI targets 640x480.

### HMI

- Adobe AIR / SWF-based interface.
- Modular screens for HVAC, comfort controls, settings, camera, media and phone functions.
- HMI code references Harman ModuleLink APIs rather than embedding raw CAN logic in each screen.

### Vehicle integration

- QNX PPS is used around vehicle/CAN data.
- Heated-seat state definitions were found in PPS-backed sensor/property configuration.
- Writable vehicle-side PPS objects also exist.
- Existing HMI code exposes higher-level HVAC and comfort methods such as heated-seat/steering-wheel capability checks and HVAC state changes.

### Display and touch

- QNX Screen is present.
- `libscreen` and QNX Screen APIs are used by factory utilities.
- Touch calibration code consumes QNX Screen events and mtouch infrastructure.

### Audio

- Factory audio configuration maps logical sources into the multimedia/audio stack.
- Existing source mappings include MME-backed media sources and an `audioApp` path.

### USB / phone connectivity

- QNX USB stack is present.
- Existing iPod/iPhone accessory integration and an iPhone tunnel adapter are present.

### Projection-facing HMI scaffolding

The RA4 HMI contains code-facing projection concepts including:

- `IPhoneProjection`
- `PhoneProjectionEvent`
- `phoneProjectionService`
- `DeviceProjection.swf`
- `isSourceCarPlay`
- `isSourceGAL`
- projection active/loading/error state handling

Persistency configuration contains projection-related properties including:

- `enableCarplay`
- `enableAndroidAuto`
- `enableMirrorLink`
- `Projection_AutoShow`
- `projectionAutoPlay`

## STRONG EVIDENCE

The RA4 uses a shared Harman/FCA HMI codebase that contains projection-aware UI behavior even though the complete projection backend does not appear to be installed in this product build.

## UNKNOWN

- Exact complete interface contract for `IPhoneProjection`.
- Whether a compatible replacement `phoneProjectionService` can be supplied without modifying signed firmware.
- Exact display-surface arbitration rules between stock HMI, camera and an external projection surface.
- Exact touch routing behavior during an active projection session.
- Exact application-audio registration/control path required for a new projection source.

## Security constraint

RA4 USB updates verify signed content. The project should not depend on bypassing that signing chain.
