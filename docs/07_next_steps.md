# 07 - Next Steps

## Phase 1 - Finish the contract map

1. Reconstruct `IPhoneProjection` properties, methods and events from SWF bytecode and related artifacts.
2. Trace how the HMI discovers `phoneProjectionService` through ModuleLink/servicebroker.
3. Trace display, touch and audio dependencies for a projection-active session.
4. Document stock comfort/HVAC interfaces needed by the modern HMI.

### Exit criterion

An evidence-backed interface inventory exists with clear VERIFIED / STRONG EVIDENCE / HYPOTHESIS / UNKNOWN labels.

## Phase 2 - Bench hardware

Acquire a spare compatible RA4 and build a bench harness.

Bench goals:

- power radio safely outside the vehicle
- access USB and display-related interfaces where practical
- observe normal boot behavior
- preserve an unmodified reference unit/image

### Exit criterion

The spare RA4 can boot reliably on the bench and be restored to stock behavior after every experiment.

## Phase 3 - Non-invasive runtime proofs

Prototype only non-destructive experiments:

1. Create a test QNX Screen surface/window.
2. Observe touch events without blocking stock input.
3. Determine whether application audio can be registered/routed through stock audio services.
4. Determine stock camera priority behavior while a custom surface exists.

### Exit criterion

Display, touch and audio integration paths are demonstrated without modifying signed firmware.

## Phase 4 - Modern HMI prototype

Build a 640x480 desktop/embedded prototype with mocked RA4 state.

Screens:

- Home
- Radio
- Media
- Climate
- Controls
- Phone
- Projection
- Settings

### Exit criterion

The UI is usable at native resolution and all vehicle controls are represented through an abstract service API rather than direct CAN calls.

## Phase 5 - RA4 bridge

Implement adapters from the abstract HMI service API to verified stock RA4 interfaces.

Start read-only:

- temperatures
- HVAC state
- seat/wheel capability and state
- media state
- phone/projection state

Then enable low-risk comfort commands through the same high-level factory service paths.

## Phase 6 - Projection integration

Integrate a legitimate CarPlay/Android Auto projection engine/module with the hidden compute layer.

Required:

- automatic phone-type detection
- projection video into the factory display path
- factory touchscreen coordinates into projection
- audio into stock audio stack
- steering-wheel media controls where supported
- clean exit to modern Jeep UI

## Phase 7 - Vehicle validation

Only after bench success:

- install reversible prototype in vehicle
- validate boot/fallback
- validate reverse camera
- validate HVAC/comfort controls
- validate Android Auto
- validate CarPlay
- validate steering-wheel controls
- run long-duration stability tests

## Definition of done

The system feels like a newer Jeep infotainment system, supports native Android Auto and CarPlay, preserves all required 2014 WK2 comfort/vehicle features, and falls back safely to the original RA4 behavior if the modernization layer fails.
