# 09 - Projection adapter boundary

Updated 2026-09-06. This is the minimum stock-facing boundary for the resident
projection integration. It converts recovered stock observations into the
transport-free arbiter contract and applies only narrowly scoped presentation
and navigation results. Names below are architectural names unless an address or
stock symbol is cited; no Harman wire schema is invented.

## Boundary shape

```text
stock session / branch / call / message observations
                         |
                         v
              complete adapter snapshot
                         |
                         v
       no-heap projection ownership arbiter
                 |                 |
                 v                 v
      navigation intent     presentation lease
                 |                 |
                 v                 v
 stock foreground/stack     narrow native UI gates

stock camera, emergency and popup managers remain autonomous
and never depend on this adapter to perform their safety behavior
```

The adapter is not a vehicle controller, projection engine, Bluetooth stack,
camera manager or audio manager. It does not originate raw CAN/PPS writes.

## Inputs

| Adapter input | Recovered source | Confidence | Normalization rule |
| --- | --- | --- | --- |
| projection session | `IPhoneProjection.sessionActive`, read at FWS `0x002588DF` | CONFIRMED | Map only a proved active/inactive observation; disconnected versus connected-inactive still needs backend evidence |
| projection platform | active projection ID/source handled by AppStateManager/PhoneProjection | HIGH | Accept only CarPlay or Android Auto after a recognized backend identity; otherwise disconnected/unavailable |
| current foreground | `IStructure.currentBranch`; `DEVICE_PROJECTION` comparisons around `0x002588F7` | CONFIRMED | Visibility never substitutes for session state |
| projection call state | `projectionCallState`, `0x002B4E18-0x002B4EBC` | CONFIRMED | Presentation ownership follows active session; call fields are status only |
| camera takeover | DisplayManager/LayerManager, `0x002BA764` and `0x002D4D6F` | CONFIRMED | Observation only; factory camera independently owns preemption and return |
| critical/eCall takeover | emergency branch before ordinary BT processing; full-popup foreground denial | CONFIRMED/HIGH | Critical stock ownership overrides projection; never gate emergency presentation |
| comfort overlay | PopupManager; HVAC example `0x0026DA68-0x0026DAB9` | CONFIRMED for HVAC / UNKNOWN for seat-wheel chain | Observation only; stock popup manager independently shows and dismisses |
| service health | integration-process lease | ARCHITECTURAL | Missing, invalid or expired lease restores stock presentation |
| sequence/epoch | integration-process generated | ARCHITECTURAL | Strictly increasing within one epoch; reset only by explicit arbiter reinitialization |

A snapshot is complete and copied. Do not refresh the lease from a partial,
malformed or unrelated stock event. Do not synthesize an active session from
the current screen or from a persisted preference.

## Outputs

| Arbiter result | Intended stock seam | Required behavior | Gate before implementation |
| --- | --- | --- | --- |
| foreground projection | stock app foreground request and pending retry at `0x0025250E-0x002525D2`, `0x002524C4-0x002524FD` | Request, never seize, foreground; stock denial remains authoritative | Supported caller/registration boundary |
| resume active projection | Stock BacktoCar/start precedes sessionActive/goto in AppPhone.press | Preserve session; do not infer backend effects from the command name | Missing screen/listener and backend meaning of callStartProjection; see post-reboot checkpoint |
| return to Uconnect | stock navigation stack | Leave session running and reveal a stock branch | Exact stock Return-to-Uconnect action and previous-branch rule |
| suppress native call presentation | presentation actions inside `processBTCallState`, beginning `0x00257983` | Gate ordinary `MAIN_PHONE` goto and incoming-call popup only | Supported policy hook; preserve HFP state/audio and emergency path |
| suppress native message presentation | SMS popup path `0x002B6C35-0x002B6C96` | Gate incoming/full-message foreground only | Supported policy hook; preserve MAP ingestion |
| suppress duplicate SMS audio | TTS path `0x002B85C2-0x002B8750` | Gate announcement with the visual gate | Supported policy hook and audio-focus trace |
| projection media source | `P/share/audioDSP/audioMgrCMC.conf:24-29` maps stock `audioApp` to MME | Acquire only a proved stock logical source; follow stock pause/resume | Registration/lifecycle, priority and restoration contract |
| projection prompt/call audio | projection audio/navigation/call events plus stock HFP coexist | Use separately proved prompt and voice routes | Ducking/mixing, call route and emergency priority |
| projection microphone | no exact RA4 acquire/release API recovered | Short exclusive lease only for active call/assistant phase | Owner-death, timeout, acoustic path and stock restoration |
| stock presentation restored | same native call/SMS paths | Default behavior when inactive, disconnected, invalid, stale or crashed | Must be the no-lease/default state |
| camera/critical/comfort | no adapter command | Observe for model/status only; stock managers retain control | Never interpose on factory safety path |

No output authorizes calling an address directly or patching SWF/native code.
Addresses identify static evidence, not stable external APIs.

## Presentation lease

Duplicate-UI suppression must be volatile and session-scoped:

1. The default with no adapter is stock Phone/Messaging presentation enabled.
2. A fresh, valid active-projection snapshot may acquire a short presentation
   lease for ordinary projected interactions.
3. Every renewal validates session, epoch and critical/eCall state.
4. Invalid data, timeout, disconnect, projection inactivity, adapter death or
   arbiter restart releases the lease and restores stock presentation.
5. Camera alone does not release the lease because projection still owns ordinary
   call/message presentation behind the camera.
6. Critical/eCall bypasses the lease immediately.
7. The visual lease is never persisted and never disables Bluetooth, HFP, MAP,
   message ingestion, microphone or speaker services.
8. Media, prompt, call-audio and microphone ownership are separate shorter leases;
   no visual state alone may grant an audio route or microphone.

The 2,000 ms host-model timeout is a test constant, not a recovered production
period. Select a target lease only after measuring service cadence and worst-case
latency. The expiry path must not wait on the projection backend.

Every external presentation decision must enforce freshness at the point of use;
it must not assume that a periodic callback ran. The browser reference calls
`nativePresentationAt(now)` before rendering policy, and the C candidate exposes
`pa_native_presentation_at` for the same purpose. The stock-side implementation
still needs a default-open owner-death/lease primitive so process death restores
native presentation even if no adapter cleanup or timer executes.

## Navigation invariants

- A visible projection screen with inactive session falls back through the stock
  source-derived or `MAIN_PHONE` paths already recovered.
- Return to Uconnect changes foreground only.
- Resume requires a fresh active session and changes neither session nor sequence.
- An active-state heartbeat after explicit Return to Uconnect does not auto-show.
- Camera/critical takeover remembers the underlying owner; clearing it restores
  projection only if projection was underneath and remains active.
- Temporary comfort overlay changes no foreground or session field.
- A delayed snapshot at or below the sequence watermark cannot recreate a session
  after stale/invalid fallback.

These invariants are implemented in both host reference models. Target behavior
remains unproved.

## Failure ownership

| Failure | Required result |
| --- | --- |
| adapter crash or no heartbeat | native presentation enabled; stock foreground |
| malformed/partial event | reject snapshot; do not renew lease |
| sequence replay | ignore; do not restore prior session |
| projection backend crash | session inactive/unavailable; stock behavior |
| UI/render failure | release projection foreground; stock managers continue |
| camera or critical event during integration failure | factory path operates without adapter |
| logging/storage failure | no retry storm or unbounded file growth; policy remains in memory |

A real integration must not require cleanup code to run in order to restore stock
call/message behavior. The supported stock gate therefore needs default-open,
lease, owner-death or equivalent semantics. A persistent disable flag is not an
acceptable implementation.

## Resource contract

This boundary adds no media, map, speech, font, icon, browser or projection-engine
payload. Planning sublimits for the complete adapter, excluding the separately
measured screen/engine, are:

| Resource | Target |
| --- | ---: |
| installed adapter plus arbiter | <=256 KiB |
| live event/snapshot buffers | <=4 KiB |
| persistent configuration | <=4 KiB |
| bounded diagnostic logs including rotations | <=256 KiB |
| cache | 0 |
| normal temporary files | 0 |
| standalone staging | 0; account inside the <=6 MB trial peak |

These are unmeasured ceilings, not permission to consume them. The current C
arbiter source is 19,404 bytes and its state has a <=128-byte compile-time guard;
compiled and linked bytes remain UNKNOWN. Stock service growth attributable to
the adapter must be measured too.

## Implementation sequence

1. Complete the ignored-firmware XREFs for return, seat/wheel popup and audio.
2. Identify a supported session subscription and presentation-policy boundary.
3. Implement a read-only adapter first; all outputs disabled, complete snapshots
   and lease expiry observable in bounded host logs.
4. Compile and run the C conformance test; compare outputs with the JavaScript
   reference for the same event sequences.
5. Build one legitimate stock-integrated projection screen with no engine.
6. On separately authorized spare hardware, verify stock camera, emergency,
   popup, call/message restoration and crash behavior before enabling suppression.
7. Add a legitimate projection engine only after local resource and ABI gates pass;
   otherwise classify only that engine `EXTERNAL_COMPUTE_REQUIRED`.

The current evidence does not authorize steps 3-7 on a radio. This document
defines the implementation boundary and the proof required to cross it.
