# 04 - Projection integration architecture

Updated 2026-09-06. This document defines the smallest evidence-backed bridge
between stock RA4 Uconnect and a legitimate CarPlay/Android Auto projection
engine. It is not a replacement HMI, a radio-write procedure, or a license,
signature, or authentication workaround.

## Product boundary

Stock Uconnect remains authoritative for Radio, Media, Climate, Controls, Phone,
Messaging, Settings, camera, vehicle configuration, Bluetooth services and
critical/eCall behavior. Projection is one first-class application that may use
the full 640x480 display while selected.

```text
phone / projection engine
        |
        | video, touch, audio, session lifecycle
        | (backend contract not yet recovered)
        v
tiny RA4-resident projection adapter
        |
        | complete volatile snapshots and bounded intents
        v
transport-free ownership arbiter
        |
        +-- request stock foreground / navigate stock stack
        +-- default-open ordinary call/message presentation lease
        |
        v
stock app arbiter, popups, camera, display, touch and audio services
```

The resident adapter is required even if the projection engine later proves
`EXTERNAL_COMPUTE_REQUIRED`. External compute may move codec/protocol work;
it may not become the ordinary vehicle HMI or bypass stock arbitration.

## Evidence boundary

### Confirmed stock observations

- `IPhoneProjection.sessionActive` is read by
  `AppStateManager.onPhoneProjectionStatus` at reconstructed FWS
  `0x002588DF`. The enclosing handler is `0x002588C5-0x002589A8`.
- An active session and visible `DEVICE_PROJECTION` branch are separate.
  Auto-show may navigate to that branch at `0x0025892C`.
- `PhoneProjection.startProjection(ppId)` at
  `0x002B5177-0x002B519E` is a distinct operation from branch navigation.
- Stock foreground requests are admitted or rejected by
  `checkForegroundAvailability` / `onAppRequestForeground` at
  `0x0025250E-0x002525D2`; a pending request is retried at
  `0x002524C4-0x002524FD`.
- Native Bluetooth call presentation begins in `processBTCallState` at
  `0x00257983`; its ordinary phone goto, incoming-call popup and previous
  screen return are downstream of HFP state ingestion.
- Native SMS popup and TTS presentation are isolated at
  `0x002B6C35-0x002B6C96` and `0x002B85C2-0x002B8750`.
- DisplayManager and LayerManager handle camera observation, takeover and stack
  return at `0x002BA764-0x002BA89F` and
  `0x002D4D6F-0x002D4EF8`.
- The stock PopupManager can overlay the current branch without replacing it.
  The recovered HVAC example is `0x0026DA68-0x0026DAB9`.
- `phoneProjectionService`, ModuleLink, a localhost endpoint,
  servicebroker, QNX Screen, MME, `audioApp -> MME` and AudioCtrlSvc are
  present in the recovered corpus.

Addresses prove control-flow observations only. They are not stable APIs and do
not authorize direct invocation or patching.

### High-confidence deductions

- Returning to an already active projection session should navigate to the stock
  projection branch; it must not issue another start command.
- Camera return can restore projection when projection was underneath because
  the stock stack unwinds after the session-independent camera layer clears.
- The narrowest duplicate-call control point is native presentation after HFP
  state ingestion, not disabling Bluetooth/HFP.
- SMS needs both visual and TTS gates. Suppressing only the popup can still create
  duplicate audio.
- A permitted comfort popup should remain a stock popup above the current owner;
  it must not be reimplemented in the projection application.

### Unproved contracts

- The implementation and legitimate registration schema for
  `phoneProjectionService`.
- Complete consumers of `PROJECTION_BACKTO_CAR` and the exact stock
  Return-to-Uconnect previous-branch rule.
- A supported default-open policy hook for ordinary call/SMS presentation.
- Projection/HFP media, prompt, call, microphone and speaker focus ownership.
- The projection video-buffer producer, QNX Screen consumer and touch-routing
  contract.
- Heated-seat/heated-wheel event-to-popup consumers.
- A legitimate app/package loader and compatible target toolchain.
- A legitimate local projection engine and its authentication/resource costs.

No adapter may invent values for these gaps.

## Session and foreground sequence

The confirmed session handler and required product policy combine as follows:

```text
backend reports sessionActive
        |
        v
AppStateManager reads session independently of currentBranch
        |
        +-- inactive while projection visible
        |      -> source-derived stock branch or MAIN_PHONE fallback
        |
        +-- active and auto-show permitted
        |      -> stock navigation to DEVICE_PROJECTION
        |
        +-- active but user returned / auto-show disabled
               -> stock branch remains visible; session remains active
                  and projection still owns ordinary projected interactions
```

The last case is essential: foreground visibility never grants or revokes
call/message ownership.

Required explicit navigation:

```text
Return to Uconnect
  -> reveal a stock branch
  -> do not stop session
  -> do not re-enable native ordinary projected call/message presentation

Return to Projection
  -> validate fresh active session
  -> request stock foreground
  -> navigate to DEVICE_PROJECTION only after stock permits it
  -> never call startProjection for that existing session
```

The exact stock Return-to-Uconnect action remains an evidence gate.

## Camera and popup sequence

```text
camera layer visible
  -> stock DisplayManager/LayerManager owns takeover
  -> adapter observes only
  -> projection session and presentation lease remain active when safe
camera layer clears
  -> stock dequeues camera popup / backs out camera screen
  -> preempted projection returns only if it was underneath and is still active

permitted comfort event
  -> stock PopupManager shows stock popup
  -> current branch and projection session do not change
popup dismissed
  -> underlying stock or projection foreground is revealed
```

The adapter issues no camera or comfort command. Emergency/eCall bypasses ordinary
projection ownership and remains stock-owned.

## Presentation lease sequence

Ordinary native call popup/goto, SMS popup and SMS TTS may be suppressed only by
a volatile, session-scoped, default-open lease:

```text
fresh complete active-session snapshot
  -> validate version, enum domain, sequence/epoch and service health
  -> renew short ordinary-presentation lease
  -> projection owns ordinary call/message presentation

invalid / stale / inactive / disconnected / process death / restart
  -> lease absent or expired without cleanup
  -> native Phone/Messaging presentation enabled

critical/eCall
  -> stock presentation immediately wins regardless of ordinary lease
```

Every presentation decision checks freshness at the point of use. The current
2,000 ms model value is a test constant, not a recovered production duration.
The actual stock-side mechanism must have owner-death, lease expiry or equivalent
default-open semantics; a persistent disable flag is unacceptable.

## Service-discovery sequence

Only the endpoints and roles are confirmed; the binding details are not:

```text
stock HMI ModuleLink client
        |
        | requests expected service name/interface
        v
localhost servicebroker / ModuleLink infrastructure       CONFIRMED role
        |
        | registration, version, owner death, reconnect    UNKNOWN schema
        v
phoneProjectionService implementation                      NOT LOCATED
```

The first adapter implementation is therefore read-only and output-disabled. It
may normalize complete stock observations and exercise lease expiry in bounded
host logs, but it must not connect to an inferred socket, claim the expected
service name, or send guessed wire fields.

## QNX CAR 2.1 reference boundary

Official QNX SDP 6.6 / QNX CAR 2.1 documentation supplies an era-compatible
reference architecture, not a recovered RA4 contract:

- application/window management publishes and subscribes through PPS under
  `/pps/system/navigator` and renders through QNX Screen;
- the HMI asks Launcher to start an application through
  `/pps/services/launcher/control`, and Launcher consults Authman;
- HMI Notification Manager (HNM) arbitrates asynchronous multimodal events by
  configured priority and publishes status/messaging results through PPS;
- QNX's reference window layering places rear camera above all applications and
  allows transient prompts/overlays above ordinary application content.

Sources:

- https://support7.qnx.com/download/download/26216/Application_and_Window_Management.pdf
- https://www.qnx.com/developers/docs/6.6.0.update/com.qnx.doc.car.arch/topic/app_support.html
- https://www.qnx.com/developers/docs/6.6.0_anm11_wf10/com.qnx.doc.am.system_services/topic/applauncher.html
- https://www.qnx.com/download/download/26205/HMI_Notification_Manager.pdf

These semantics are a useful cross-check for OEM-style integration, especially
authorized launch, independent application processes, top-priority camera, and
restorable transient notifications. They do **not** prove that stock RA4 ships
the generic QNX CAR UI Core, Navigator, Launcher, Authman, HNM, QtQnxCar2,
NowPlaying, or their documented PPS objects. The exact RA4 evidence instead
shows a customized Adobe AIR/SWF HMI with Harman AppManager/AMS, ModuleLink,
servicebroker, PopupManager, DisplayManager and LayerManager paths.

Therefore an adapter must not issue the QNX manual-launch example, create or
write a documented reference PPS object, or substitute HNM for the recovered
stock popup/call/SMS paths unless the component and caller contract are first
proved in the RA4 image. The updated recovered-tree probe performs the bounded
name census needed to decide whether these reference services exist locally.

## Display, touch and audio boundaries

| Path | Stock evidence | Resident responsibility | Remaining gate |
| --- | --- | --- | --- |
| video | QNX Screen and stock window/buffer users exist | present one projection surface only | legitimate projection surface/window ownership and measured buffers |
| touch | mtouch and `screen_get_event` exist in factory tooling | route touch only while projection is the permitted active surface | stock app focus/routing and coordinate contract |
| media audio | MME, AudioCtrlSvc and `audioApp -> MME` are present | register/use a stock logical source | lifecycle, focus and stock-source restoration |
| prompts | projection navigation/audio events exist | request the supported transient prompt path | ducking/mixing contract |
| calls/voice | HFP and projection call state coexist | arbitrate call/mic/speaker ownership without disabling ingestion | supported call/mic focus API and emergency priority |
| USB | QNX USB and Apple accessory components exist | use only a legitimate authenticated engine/device path | CarPlay/Android Auto backend and authentication requirements |

String or import presence does not prove access permission, ABI compatibility or
runtime behavior.

## Resource contract

The complete product remains capped at 15 MB installed, 4 MB normal writable
growth and 8 MB additional staging/update peak while protecting 45 MB of the
approximately 77 MB observed free space. The initial stock-facing adapter target
is smaller:

| Component | Ceiling |
| --- | ---: |
| adapter plus arbiter installed | 256 KiB |
| live event/snapshot buffers | 4 KiB |
| persistent configuration | 4 KiB |
| bounded logs including rotations | 256 KiB |
| cache and normal temp | 0 |
| initial complete stock-facing trial | 3 MB installed / 1 MB writable / 6 MB staging |

No bundled maps, media databases, speech models, browsers, fonts, codecs or
duplicate stock assets are allowed. Reused stock libraries count as zero new
installed bytes only after their ABI and permitted access are proved; attributable
runtime state and cache still count.

## Ordered proof path

1. Run bounded XREFs on the hash-identified ignored SWF for return/resume,
   seat/wheel popup and projection/HFP audio.
2. Locate a supported service and presentation-policy registration boundary.
3. Compile both host models; compare identical event sequences and produce a
   target linked map.
4. Build a read-only, output-disabled adapter with complete snapshots, point-of-use
   freshness and bounded removable logs.
5. Establish a legitimate stock screen/app lifecycle and show a no-engine surface.
6. On separately authorized spare hardware, test return/resume, camera, overlays,
   call/SMS fail-open behavior, process death and resource peaks.
7. Select a legitimate engine only after local storage, RAM, CPU, graphics, USB,
   authentication and latency measurements. Mark only the engine
   `EXTERNAL_COMPUTE_REQUIRED` if local gates fail.

The current evidence authorizes none of steps 4-7 on a radio. See
[the adapter boundary](09_projection_adapter_boundary.md),
[the completion matrix](08_projection_completion_matrix.md), and
[the resource budget](ra4_resource_budget.md).
