# 03 - Projection Contract

Status: **foreground ownership reconstructed in part; backend incomplete**.

Production treats projection as an application inside stock Uconnect. See the
address-level [foreground report](../reports/projection_foreground_ownership.md)
and the fail-safe [adapter boundary](09_projection_adapter_boundary.md).

## Verified names and semantics

| Symbol | Interpretation |
| --- | --- |
| `IPhoneProjection.sessionActive` | session state independent of visible branch |
| `startProjection(ppId)` | distinct session-start command |
| `PhoneProjectionEvent` | status, status-bar and back-to-car events |
| `phoneProjectionService` | expected backend |
| `DeviceProjection.swf` / `DEVICE_PROJECTION` | stock projection screen/branch |
| `projectionCallState` | projection-owned call status and caller |
| `KEY_PROJECTION_AUTO_SHOW` | optional foreground-on-start preference |
| `PROJECTION_BACKTO_CAR` | return event; complete consumers still unknown |

Persistency also contains `enableCarplay`, `enableAndroidAuto`,
`enableMirrorLink`, `Projection_AutoShow` and `projectionAutoPlay`.
Names/defaults do not prove a complete backend.

## State model

```text
session: disconnected | connected/inactive | active-visible | active-backgrounded
foreground priority:
camera/critical stock > permitted stock overlay > projection > ordinary stock HMI
```

- Return to Uconnect changes foreground, not session lifetime.
- Return to projection navigates to `DEVICE_PROJECTION` if already active; it
  does not call `startProjection` again.
- Camera and comfort overlays preserve the session.
- Projection call/message ownership follows session state, not screen visibility.
- Inactive/disconnected projection restores native Phone/Messaging presentation.
- Emergency/eCall remains stock-owned.

## Confirmed reuse points

- `AppStateManager.checkForegroundAvailability`: camera/display/popup/full-screen
  rejection plus pending retry.
- `IStructure.goto/back/removeFromStack`: application navigation and return.
- `DisplayManager` / `LayerManager`: camera layers and stack unwind.
- `PopupManager`: temporary overlays without replacing underlying branch.
- `processBTCallState`: native call goto/popup downstream of HFP.
- `SMSManager`: native SMS popup and TTS announcement.
- `PhoneProjection`: projection call/audio/navigation status and stock status bar.

## Required narrow arbitration

While projection owns presentation, suppress native `MAIN_PHONE` navigation,
incoming-call popup, incoming/full SMS popup and duplicate SMS TTS. Preserve
connectivity, ingestion, required audio services, camera, emergency/eCall and
permitted stock overlays. This is a design contract, not authorization to patch
the radio; a supported policy bit/API remains unknown.

## Open questions

1. Complete consumer XREF for `PROJECTION_BACKTO_CAR`.
2. Projection screen Return-to-Uconnect control and exact stack action.
3. Supported native call/SMS presentation policy.
4. Projection/HFP microphone, speaker and audio-focus ownership.
5. Video surface, touch, USB, complete service events and disconnect semantics.
6. Legitimate local engine resource feasibility.

## Success criterion

A bench-only mock separates session from foreground, exercises camera/popup/call/
SMS transitions and resumes an active projection session without reconnecting.
