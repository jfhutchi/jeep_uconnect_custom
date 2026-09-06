# Resident projection integration contract v2

This contract governs the executable PC reference model in
`prototype/resident_hmi`. Field names are original application names, not
recovered Harman/PPS/ModuleLink wire keys. There is no radio transport.

## Product boundary

Production preserves stock Radio, Media, Climate, Controls, Phone, Messaging and
Settings. The resident component integrates projection as a first-class stock
application. The former six-screen contract is superseded; driver-temperature
research remains independently documented and does not imply a replacement
Climate screen.

## Snapshot schema

A complete version-2 mock snapshot contains:

| Field | Contract |
| --- | --- |
| `version` | exactly 2 |
| `sequence` | nonnegative increasing safe integer |
| `serviceConnected` | integration-state availability, strict boolean |
| `camera`, `critical` | mutually exclusive highest-priority stock takeover observations |
| `comfortOverlay` | permitted temporary stock overlay observation |
| `projection.session` | `disconnected`, `connected`, or `active` |
| `projection.platform` | null only when disconnected; otherwise `carplay` or `android_auto` |
| `projection.autoShow` | mock preference applied only on inactive-to-active transition |
| `projection.callActive`, `messagePending` | synthetic projected interaction state |

Snapshots are copied. Invalid data fails to ordinary stock Uconnect. Duplicate or
older sequence values are ignored. The 2,000 ms freshness threshold remains a PC
test constant, not a recovered radio timing guarantee.

## Independent state dimensions

Session:

```text
disconnected -> connected -> active
```

Foreground:

```text
stock camera/critical takeover > projection > ordinary stock Uconnect
```

A permitted comfort overlay is orthogonal: it can cover projection or ordinary
Uconnect without changing the underlying foreground owner. Camera/critical
takeover suppresses that overlay.

## Required transitions

- Inactive-to-active with mock auto-show selects projection.
- Return to Uconnect changes foreground only; session remains active.
- Return to Projection requires fresh active state and changes no session field or
  sequence number. It is therefore a resume, not a reconnect.
- Camera/critical takeover remembers whether projection or Uconnect was underneath.
- Clearing takeover restores projection only if it was underneath and remains
  active; otherwise it restores Uconnect.
- Projection disconnect while visible returns to Uconnect.
- Integration disconnect, invalid state or stale state fails to Uconnect.
- Fresh state alone does not foreground an already-active session after a user
  explicitly returned to Uconnect.
- Emergency/critical stock takeover cannot be overridden by a projection request.

## Phone and message ownership

While `projection.session == active`, interaction presentation owner is
`projection` regardless of whether projection or ordinary Uconnect is visible.
The model reports native incoming-call foreground, message foreground and SMS TTS
as suppressed.

When projection is connected-but-inactive or disconnected, presentation owner is
`uconnect` and normal native behavior is allowed.

These are policy outputs only. The model does not disable Bluetooth, HFP, MAP,
message ingestion, microphones, speakers or audio focus.

## Static evidence mapping

- Session/branch separation: `AppStateManager.onPhoneProjectionStatus`,
  reconstructed FWS `0x002588C5`.
- Start command: `PhoneProjection.startProjection`, `0x002B5177`.
- Projection call status: message handler `0x002B4E18-0x002B4EBC`.
- Native call presentation: `processBTCallState`, starting `0x00257983`.
- Native SMS popup/TTS: `0x002B6C35` and `0x002B85C2`.
- Foreground availability: `0x0025250E`.
- Camera stack return: `LayerManager.onLayerChange`, `0x002D4D6F`.
- HVAC popup layering: left-temperature path `0x0026DA68-0x0026DAB9`.

See [the focused report](../reports/projection_foreground_ownership.md) for exact
confidence labels and unknowns.

## Resource and safety effect

The reference model is development-host only. It installs 0 radio bytes, writes
0 radio bytes and needs 0 radio staging bytes. No browser, Node, Python, test
runner or mock asset belongs in deployment.

Production caps remain 15 MB installed, 4 MB runtime growth, 8 MB additional
update peak, 45 MB protected stock reserve and 5 MB planned-peak margin. A
complete legitimate engine is `EXTERNAL_COMPUTE_REQUIRED` only if measured local
storage/CPU/RAM/platform feasibility fails.
