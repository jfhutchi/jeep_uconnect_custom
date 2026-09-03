# 03 - Projection Contract

Status: **in reconstruction**.

The purpose of this document is to recover the interface the stock RA4 HMI expects from the missing/incomplete phone-projection backend.

## VERIFIED HMI-facing names

The following names appear in the factory HMI/runtime artifacts:

| Symbol / object | Current interpretation |
|---|---|
| `IPhoneProjection` | HMI-facing projection interface |
| `PhoneProjectionEvent` | event class / event family used by HMI |
| `phoneProjectionService` | expected backend service name |
| `DeviceProjection.swf` | projection UI/screen artifact referenced by the HMI |
| `isDeviceProjectionActive` | projection session state check |
| `isSourceCarPlay` | CarPlay media-source awareness |
| `isSourceGAL` | Google Automotive Link / Android Auto-era source awareness |
| `KEY_PROJECTION_AUTO_SHOW` | persistency/UI preference |
| `CONNECT_PROJECTION_DEVICE` | connection-state UI path |
| `PROJECTION_DISPLAY_LOADING` | loading-state UI path |
| `PROJECTION_DEVICE_CONNECT_ERROR` | error-state UI path |
| `DEVICE_PROJECTION` | projection device/source concept |

## VERIFIED persistency properties

The runtime persistency schema includes:

- `enableCarplay`
- `enableAndroidAuto`
- `enableMirrorLink`
- `Projection_AutoShow`
- `projectionAutoPlay`

Some of these are enabled by default in the analyzed build. Therefore these settings are not sufficient on their own to activate projection.

## Observed HMI behavior

### Status bar

Projection-aware status-bar code references `IPhoneProjection`, projection events and shortcut behavior.

### Media

Media source logic distinguishes CarPlay and GAL sources.

### Bluetooth/settings

Some settings behavior checks whether a projection session is active and can disable conflicting actions while projection is running.

### Display settings

Projection auto-show is exposed through persistency-backed display settings.

## Initial inferred state machine

This state machine is a hypothesis assembled from UI strings and symbols, not yet a recovered protocol definition.

```text
DISCONNECTED
   |
   | device detected / projection requested
   v
CONNECTING
   |
   +--> ERROR
   |
   v
LOADING
   |
   v
SESSION_ACTIVE
   |
   | disconnect / user exit / fault
   v
DISCONNECTED
```

## Questions to resolve

1. How does the HMI locate `phoneProjectionService`?
2. Which ModuleLink/servicebroker interface does it request?
3. What methods and properties are exposed by `IPhoneProjection`?
4. Which events signal connection, source availability, loading, activation, deactivation and failure?
5. Does the projection backend own a QNX Screen window directly or request a surface through another service?
6. How are touch events handed to the projection session?
7. How is projection audio registered with MME / AudioCtrlSvc?
8. Can the HMI contract be satisfied by a compatibility bridge while the signed stock image remains unchanged?

## Success criterion

Produce a minimal, evidence-backed interface specification sufficient to build a bench-only mock service that can satisfy the stock HMI's projection-facing state transitions without sending vehicle-control commands.
