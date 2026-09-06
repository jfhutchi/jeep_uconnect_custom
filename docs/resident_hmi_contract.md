# Resident HMI MVP contract v1

Implementation-neutral semantics; field names here are original application
names, **not** recovered Harman/PPS/ModuleLink wire keys. Reference code lives in
`prototype/resident_hmi/model.mjs`; the DOM renderer is replaceable.

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

Modes: `stock`, `app`, `camera`. Start in stock/waiting. The PC demonstration
explicitly activates after its first valid mock snapshot; real activation must
come through an independently verified stock-supported lifecycle boundary.

- Camera observation cancels pending intent and replaces all custom controls.
- Camera clear leaves stock mode; an explicit resume is required.
- Disconnect, stale state, invalid snapshot or manual fallback cancels intent
  and requests stock UI. Fresh data alone never retakes foreground.
- The `Stock UI` control is always present. In the PC it changes state only.
- A real fallback adapter must release its own surface/input/resources and let
  stock retain authority, including on crash. Exact API and crash supervision
  remain UNKNOWN; an in-process timer cannot guarantee recovery from a crash.

## Minimum real adapter seams

| Seam | Evidence level | What can replace a mock next / missing proof |
| --- | --- | --- |
| Climate state | CONFIRMED `IHvac` references; HIGH high-level service seam | First target: driver temperature property/event, units, capability/validity in MainSupplement + stock hvac publisher; no live subscription yet. |
| Climate/comfort actions | CONFIRMED capability/action vocabulary; UNKNOWN complete command contract | Keep disabled. Per-zone/seat/wheel availability, units, ranges, permission, acknowledgment and failure semantics needed. |
| Heated-seat state | CONFIRMED `HeatedSeatFL/FR`, `FL_HS_STAT/FR_HS_STAT` mapping in existing inventory | HIGH adapter route, but raw PPS value encoding, subscription and equipment variability not closed. |
| Media | CONFIRMED source mapping to MME | State/title subscription and playback intent ownership UNKNOWN; do not open audio devices or decode media. |
| Vehicle settings | CONFIRMED stock settings screens/services; UNKNOWN per-setting API | Read-only/unavailable. No custom persistent vehicle state or mutations. |
| Camera/preemption | CONFIRMED graphics classes/resources; INFERRED integration via stock foreground arbiter | Exact event, z-order, release ordering and latency UNKNOWN. PC panel is not camera video. |
| Phone/projection | CONFIRMED stock-facing references; UNKNOWN complete backend | State placeholder only; no pairing, call or projection actions. |
| Stock fallback | CONFIRMED stock lifecycle/foreground code exists; UNKNOWN independent app handover | Prove release, process death and restart behavior before any resident trial. |

The [decision report](resident_hmi_decision.md) links primary local evidence and
the existing launch/interface reports. No confidence label for a *name's presence*
should be read as proof that the full adapter is implemented or safe to call.

## Portability and UI

640x480 logical pixels; header 56, content 330, status 26, navigation 68.
Six routes, original text/rectangles and minimum 48px-high action controls. No
animations, video, fonts, vendor icons or heavy assets. PC can horizontally
scroll on narrower viewports; it never reflows into a misleading radio layout.
Implement snapshots, intents and state tests in the eventual resident language;
HTML, CSS and JavaScript syntax are not the RA4 API contract.

## Out of scope

Defrost/vent/sync/vented-seat controls until individual contracts are known;
arbitrary vehicle settings; audio registration; call handling; projection;
boot modification; installation/update media; security bypasses. Stock UI
continues to provide omitted factory functions.
