# 07 - Product-first next steps

Updated 2026-09-05. The current slice is a small resident shell, not projection,
external hardware or unrelated Synctool research. The completed
[PC prototype](../prototype/resident_hmi/README.md),
[resident decision](resident_hmi_decision.md) and
[adapter contract](resident_hmi_contract.md) move software prototyping ahead of
bench integration. Historical phase numbers below are backlog categories, not a
requirement to acquire hardware before building the UI.

## Next single highest-value task

Trace one **read-only driver-temperature subscription** from the ROV
`IHvac`/MainSupplement client through ModuleLink into `vehicle/hvac.lua`.
Record exact type, units, capability/validity and change-event fields with
bytecode offsets. No radio calls, commands or raw CAN writes. Exit: a concrete
adapter field contract and fixture independent of guessed mock encodings.

Before any resident trial, independently close authorized screen/app loading,
compatible toolchain, stock camera/display/touch ownership and crash fallback.
Measure the complete target package, RAM/CPU/startup and storage peaks; never
borrow the protected 45 MB stock reserve. This roadmap authorizes no deployment
or bench/radio mutation by itself.

## Phase 1 - Finish the contract map

1. Start with the single read-only temperature subscription above.
2. Document capability/validity semantics before replacing further state mocks.
3. Establish supported app/screen loading and stock foreground/fallback contracts.
4. Defer projection and new audio-source registration until the shell is useful.

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

The minimal PC slice now exists. Remaining items below are later expansion,
not claims of resident deployment or projection support.

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

Only under a separately authorized plan, enable individual comfort commands
after units, equipment capabilities, permissions, acknowledgment and failure
semantics are established. Do not use raw CAN control.

## Phase 6 - Projection integration

Deferred: evaluate a legitimate CarPlay/Android Auto engine only after the shell.
There is no assumed hidden compute layer. Require external compute only for a
capability demonstrated infeasible within stock storage/CPU/RAM and service limits.

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
