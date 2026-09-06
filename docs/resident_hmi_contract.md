# Resident HMI MVP contract v1

Implementation-neutral semantics for the **PC technical scaffold**; field names
are original application names, not recovered Harman/PPS/ModuleLink wire keys.
Reference code lives in `prototype/resident_hmi/model.mjs`; the DOM renderer is
replaceable.

## Product-contract correction

The six scaffold routes are not a production replacement HMI. Production keeps
stock Radio, Media, Climate, Controls, Phone, Messaging and Settings and adds
projection as a first-class stock application. This snapshot/intent model remains
useful for tests, but its `stock/app/camera` demonstration is superseded by the
session/foreground contract in
[projection_foreground_ownership.md](../reports/projection_foreground_ownership.md).

## Ownership and layers

```text
View (SWF/native later; HTML on PC today)
  -> Shell state machine: route, pending intent, foreground policy
  -> Adapter: snapshot / abstract intent / acknowledgment
  -> Stock RA4 services (not implemented; MockAdapter only today)
```

Stock remains vehicle authority. A command is a request, never proof of a
physical change. The UI updates actual values only from a valid newer snapshot.
An acknowledgment must carry the observed snapshot; it may differ from the
requested value. No raw CAN, guessed PPS writes, radio sockets or transport
configuration exists in this scaffold. The web CSP prohibits `connect-src`.

## Snapshot

Schema version 1, one complete snapshot per adapter session:

| Field | Contract |
| --- | --- |
| `version` | Exactly 1 |
| `sequence` | Nonnegative increasing safe integer; stale/duplicate snapshots ignored. New service session requires a new Shell and explicit activation; sequence rollback is not auto-accepted. |
| `connected`, `camera` | Strict booleans. Camera is a preemption observation, not an instruction to acquire video. |
| `capabilities.climate/comfort/media` | Strict booleans; coarse MVP command availability. Real adapter must additionally validate each equipment/operation-specific capability; default all false until proved. |
| `climate.driverC/passengerC` | Integer Celsius 16..30, **mock-only envelope**, not recovered factory limits or LO/HI encoding |
| `climate.fan`, `climate.auto` | Integer 0..7 and boolean; mock encoding only |
| `comfort.driverSeat/passengerSeat`, `comfort.wheel` | Integer 0..2 (off/low/high), boolean; mock encoding only |
| `media.title/playing` | Text <=80 characters; boolean. Title escaped by renderer. No audio data. |
| `phone.connection/projection` | `disconnected` or `connected`; projection always `unavailable` in v1 |

Invalid required data invalidates freshness, cancels pending intent, requests
stock fallback and raises a visible error. No guessed default values. Real
integration needs explicit unavailable/quality state and per-field freshness;
the complete-snapshot mock deliberately does not pretend to have that contract.
Adapters copy data; renderer has no authority to mutate observed values.

## Intents and replies

Intent `{id, path, value}` uses the model's exact field allowlist: driver and
passenger temperature, fan, auto, both heated-seat levels, wheel heat and media
playing. Phone/projection and vehicle settings are read-only placeholders.
No endpoints, message framing or numeric factory commands are defined here.

At most one outstanding intent, with a monotonically increasing local ID.
`{id, status:'applied', snapshot}` carries observed state;
`{id, status:'rejected'}` leaves values unchanged. Unknown reply statuses reject.
Replies without the pending ID are ignored. Validation is repeated in the mock
adapter. A real adapter must enforce bounds, permission and current capability
at dispatch, not just trust the view.

The 1,000 ms command timeout and 2,000 ms freshness limit are PC design constants,
not radio service timings. Use a monotonic local clock. The PC polls at 500 ms,
so visible idle timeout detection can lag by one poll; request dispatch checks
freshness synchronously. No automatic command retry or replay after reconnect.
Already-dispatched physical actions cannot generally be cancelled: cancelling
the UI intent does not undo a stock action. Reconcile later observed state.

## Foreground and fallback

Production separates projection session state from foreground ownership.

Foreground priority: camera/critical stock takeover, permitted temporary stock
overlay, active projection, ordinary stock HMI. An active projection session may
be visible or backgrounded.

- Return to Uconnect changes the foreground branch without ending projection.
- Return to projection navigates to the existing active session.
- Camera uses factory takeover and navigation-stack return.
- Permitted comfort popups overlay the branch and dismiss back to it.
- Active projection owns projected call/message presentation even while the user
  temporarily views an ordinary stock screen.
- Native call goto/popup and SMS popup/TTS are suppressed only for that ownership
  interval; Bluetooth/HFP/MAP ingestion remains available.
- Inactive/disconnected projection restores normal stock Phone/Messaging.
- Emergency/eCall remains stock-owned.

The PC scaffold's old `stock/app/camera` panels only test fail-closed transitions.
They are not a recovered lifecycle or the product navigation model.

## Minimum real adapter seams

| Seam | Evidence level | What can replace a mock next / missing proof |
| --- | --- | --- |
| Climate state | CONFIRMED string-valued temperature, zone events, units gates and gateway service mapping; HIGH endpoint linkage | See the [driver-temperature trace](../reports/ra4_driver_temperature_contract.md). Silent `127` suppression and `SNA` cache retention prevent treating events/getters as fresh physical samples. Resolve quality/units ordering before replacing mocks; no live subscription. |
| Climate/comfort actions | CONFIRMED capability/action vocabulary; UNKNOWN complete command contract | Keep disabled. Per-zone/seat/wheel availability, units, ranges, permission, acknowledgment and failure semantics needed. |
| Heated-seat state | CONFIRMED `HeatedSeatFL/FR`, `FL_HS_STAT/FR_HS_STAT` mapping in existing inventory | HIGH adapter route, but raw PPS value encoding, subscription and equipment variability not closed. |
| Media | CONFIRMED source mapping to MME | State/title subscription and playback intent ownership UNKNOWN; do not open audio devices or decode media. |
| Vehicle settings | CONFIRMED stock settings screens/services; UNKNOWN per-setting API | Read-only/unavailable. No custom persistent vehicle state or mutations. |
| Camera/preemption | CONFIRMED DisplayManager/LayerManager layers, foreground rejection and stack return | Reuse stock priority; configuration-specific behavior and runtime latency remain UNKNOWN. PC panel is not camera video. |
| Phone/projection | CONFIRMED session/branch separation, projection call status and native call/SMS presentation seams | Backend, supported presentation policy and audio focus remain UNKNOWN; no pairing, call or projection action is implemented. |
| Stock fallback | CONFIRMED stock lifecycle/foreground code exists; UNKNOWN independent app handover | Prove release, process death and restart behavior before any resident trial. |

The [decision report](resident_hmi_decision.md) links primary local evidence and
the existing launch/interface reports. No confidence label for a *name's presence*
should be read as proof that the full adapter is implemented or safe to call.

The recovered read-only seam requires numeric/LO/HI/unavailable states, fractional
values, separate units and verified physical-to-driver mapping. The original
fixture in `analysis_tools/fixtures/ra4_driver_temperature_cases.json` records this
without changing v1's mock schema. Never feed stock string events straight into
`driverC`, and never reset the complete-snapshot freshness timer merely because
a stock generic temperature event or cached getter response arrived.

## Portability and UI

640x480 logical pixels; header 56, content 330, status 26, navigation 68.
Six PC-only routes, original text/rectangles and minimum 48px-high action controls.
They are a technical scaffold, not production replacement screens. No animations,
video, fonts, vendor icons or heavy assets. PC can horizontally
scroll on narrower viewports; it never reflows into a misleading radio layout.
Implement snapshots, intents and state tests in the eventual resident language;
HTML, CSS and JavaScript syntax are not the RA4 API contract.

## Out of scope for the current PC scaffold

Live projection backend, radio transport, screen registration, audio registration,
call/SMS handling, boot modification, installation/update media, security bypasses
and vehicle writes. These implementation exclusions do not change the product
goal: projection integrates inside stock Uconnect rather than replacing it.
