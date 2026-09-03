# 04 - Bridge Architecture

## Objective

Add a modern HMI and native phone projection without replacing the RA4's role as the Jeep vehicle-services authority.

## Proposed architecture

```text
Android phone -----------------------+
                                      |
iPhone ------------------------------+--> Projection engine
                                                |
                                                v
                                   Modern HMI / bridge compute
                                      |      |       |
                              video --+      |       +-- audio
                                             |
                                           touch
                                             |
                                             v
                                        Stock RA4
                                      /    |     \
                                   Screen  MME   Harman/PPS
                                                   |
                                                   v
                                                  CAN
```

## Responsibilities

### Hidden compute layer

- Render the modern Uconnect-inspired UI.
- Host or integrate a legitimate CarPlay / Android Auto projection implementation.
- Translate high-level user actions into supported RA4 service calls.
- Present projection video and consume touch input.
- Maintain a watchdog/fallback policy.

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
