# 04 - Bridge Architecture

## Objective

Add a modern HMI and native phone projection without replacing the RA4's role as the Jeep vehicle-services authority.

## Proposed architecture

**Resident-first revision, 2026-09-05:** the previous default of rendering the
entire modern HMI on hidden external compute is superseded. Follow the mandatory
[RA4 resource budget](ra4_resource_budget.md): 45 MB protected stock reserve,
15 MB provisional installed allowance, 4 MB runtime growth and 8 MB additional
peak update/rollback overhead. Expected remaining space is 58 MB steady / 50 MB
peak from an approximately 77 MB baseline; actual sizes and peaks are unmeasured.
The deployable core should be tiny native code reusing stock services and assets.
No complete projection engine has yet been sized or proved runnable locally.

```text
Tiny RA4-resident HMI / integration process
  |-- QNX display/touch and reused stock assets
  |-- stock MME / audio services
  |-- stock Harman / PPS services --> CAN
  `-- optional external capability interface
       (only for functions proved infeasible within local limits)
```

## Responsibilities

### RA4-resident core: feasibility targets

- Render a minimal modern Uconnect-inspired UI using lightweight native facilities.
- Translate high-level user actions into supported RA4 service calls.
- Maintain a watchdog/fallback policy.
- Reuse stock fonts, icons, codecs, media services and platform libraries after ABI/access verification; do not package duplicates.

### Optional external capabilities

First measure local feasibility, including installed dependencies, runtime
writes, update peaks, RAM/CPU and service access. Mark a capability
`EXTERNAL_COMPUTE_REQUIRED` if it cannot fit or execute safely; do not make the
entire HMI external by default. A legitimate CarPlay/Android Auto engine remains
an unresolved feasibility item, not an assumed resident dependency. Large new
maps, media libraries and speech models are excluded from the app footprint.
PC prototype tooling must not silently enter the RA4 deployment architecture.

### Stock RA4

- Remain responsible for Jeep-specific state and commands.
- Continue to own vehicle configuration, HVAC/comfort integration, camera behavior and factory service logic.
- Continue to communicate with vehicle ECUs through its existing middleware and CAN services.

## Display path

### VERIFIED

- QNX Screen is present.
- Factory utilities can create Screen windows/buffers and access display properties.

### HYPOTHESIS

A bridge or companion process may be able to present a full-screen surface through supported QNX Screen mechanisms without replacing the stock HMI.

### Required behavior

- Stock backup camera must preempt the custom UI immediately.
- A crash or bridge disconnect must return control to stock UI.
- No boot dependency may prevent normal RA4 startup.

## Touch path

### VERIFIED

- Factory touch tooling consumes QNX Screen / mtouch events.

### HYPOTHESIS

Projection-active mode can route coordinates to the projection layer while preserving stock behavior outside the projection surface/session.

## Audio path

### VERIFIED

The system has logical multimedia sources, and an `audioApp` source is mapped into MME in analyzed configuration.

### HYPOTHESIS

The projection layer can register or use an application audio source and allow AudioCtrlSvc/MME to retain volume, mute and amplifier behavior.

## Vehicle-control path

The modern HMI should use high-level existing RA4 services for comfort and vehicle functions.

Preferred order:

1. Existing Harman ModuleLink API
2. Existing PPS writable object intended for that feature
3. Existing servicebroker/SVCIPC/DBus contract
4. Raw CAN only for passive observation during research, not as the product architecture

## Failure model

Any bridge failure must degrade to stock RA4 behavior.

The bridge must never be required for:

- vehicle startup
- HVAC safety behavior
- backup-camera availability
- safety-critical ECU operation

## Bench-first rule

Runtime experiments belong on a spare/bench RA4 before they are attempted on the vehicle's only working unit.
