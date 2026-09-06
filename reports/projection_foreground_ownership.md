# RA4 projection foreground ownership

## Scope and corrected product contract

This report records static, read-only analysis of the stock RA4 18.45.01 HMI.
It does not prescribe radio writes, disable Bluetooth services, or modify camera
behavior. The current PC prototype is a focused projection-ownership bench and
contains no replacement factory screens.

The product target is an OEM-style CarPlay/Android Auto projection application
inside stock Uconnect. Stock Radio, Media, Climate, Controls, Phone, Messaging
and Settings remain the ordinary HMI. Projection may occupy the full 640x480
display while visible, but temporary foreground changes must not destroy its
session.

Projection session state and foreground ownership are separate:

```text
foreground priority:
camera / critical stock takeover
  > permitted temporary stock overlay
  > active projection
  > ordinary stock HMI

projection session:
disconnected | connected/inactive | active (visible or backgrounded)
```

Therefore Return to Uconnect changes only the foreground screen. Returning to
projection navigates to the existing active session. Camera and permitted comfort
overlays preserve that session. While a projection session owns phone/message
presentation, native Uconnect must suppress duplicate foreground UI and
announcement audio without globally disabling Bluetooth, HFP, MAP, or message
ingestion. Emergency/eCall remains stock-owned.

## Evidence base

- `MainSupplement.swf`
- SHA-256: `e9d796ea4b4c83ed518bfe3b3c341e54e510a1ae0f78ebbffbd655b7c36a3258`
- reconstructed FWS base: `0x264EB`
- ABC block 0, 15,157 methods
- addresses below are reconstructed uncompressed FWS offsets from
  `analysis_tools.swf_abc_inspect`

Corroborating wrappers:

- `ScreenCamera.swf`: `b34c3054d688dbe6ab726d4113b5988e78e3b52403d2c1f39f5174f7cf019208`
- `StatusBar.swf`: `d8a9715d818f3f29752f62160234a3f4c53bcb0efc0f354274f29f8b1abb1c9f`
- `PopupHVAC.swf`: `5dae4f7bca1e4e8a48e2a8105337eb8729916ce32bd53f0ef6de55d0b8dbbbee`

## Confirmed mechanisms

### Projection session versus visible branch

**CONFIRMED.** `AppStateManager.onPhoneProjectionStatus` at `0x002588C5`
reads `IPhoneProjection.sessionActive` at `0x002588DF`. If active while
`currentBranch` is not `DEVICE_PROJECTION`, it consults
`KEY_PROJECTION_AUTO_SHOW` and may call `IStructure.goto(DEVICE_PROJECTION)`
at `0x0025892C`. An active session can therefore exist while another branch is
visible.

When projection becomes inactive while its screen is current, the handler maps
`audioManager.source` through `branchNameFromSource` and calls `goto` at
`0x00258981-0x00258997`. `onProjectionDeviceDisconnected` at
`0x002589A9` separately moves a current projection screen to `MAIN_PHONE`
at `0x002589EC-0x002589FC`.

**CONFIRMED.** `PhoneProjection.startProjection` at `0x002B5177` sends the
start command with `ppId` at `0x002B518B-0x002B5195` and clears
`mBacktoCar` at `0x002B519C-0x002B519E`.
`AppStateManager.callStartProjection` at `0x00258A0E` calls that API and
records `activePpId`.

**HIGH.** Resuming an already-active session should navigate to
`DEVICE_PROJECTION`, not issue a new `startProjection` command. The complete
consumer XREF for `PROJECTION_BACKTO_CAR` remains unknown.

### Projection-owned call status

**CONFIRMED.** `PhoneProjection.phoneProjectionMessageHandler` at
`0x002B4B62` recognizes `projectionCallState` at `0x002B4E18`. When
`CallState == Active`, it sets `mCallState`, marks the projection shortcut
active, records current status `Call` and `CallerName`, then dispatches
`PhoneProjectionEvent.PROJECTION_STATUS_BAR` at
`0x002B4E42-0x002B4EBC`.

The same handler tracks projection audio and navigation. In `StatusBar.swf`,
`onPhoneProjectionShortCut` at `0x0001CBA9` selects status-bar state
`PhoneProjection` at `0x0001CBBB-0x0001CBBF`.

**HIGH.** Stock already receives a projection-owned call signal and provides a
dedicated status surface. This is the strongest existing input for preventing
duplicate native phone presentation.

### Native incoming-call takeover

**CONFIRMED.** Bluetooth call state enters `AppStateManager.onCallState` at
`0x002578CB`. Outside the emergency-call branch it calls
`processBTCallState` at `0x00257983`.

`processBTCallState`:

- can force `goto(MAIN_PHONE)` for dialing at `0x00257A25-0x00257A35`;
- closes SMS popups for ringing/waiting outside Phone at `0x00257A8E`;
- saves the source-derived branch or `currentBranch` in
  `mPrevScreenBeforeActiveCall` at `0x00257AF1-0x00257B35`;
- shows `PHONE_INCOMING_CALL` / `incomingcall` at
  `0x00257B66-0x00257B86` or `0x00257BBB-0x00257BDB`;
- when calls end, calls `IStructure.back()` at
  `0x00257C80-0x00257C88` and clears the saved branch.

**CONFIRMED.** These are presentation-layer actions downstream of HFP state, so
they are a narrower control point than disabling Bluetooth/HFP.

**INFERRED PRODUCT RULE.** While an active projection session owns call
presentation, preserve state ingestion and required audio services but bypass
native `goto(MAIN_PHONE)` and `PHONE_INCOMING_CALL` presentation. Never apply
that gate to emergency/eCall.

### Native SMS popup and audio

**CONFIRMED.** `SMSManager.onIncomingSMSMessage` at `0x002B6C35` calls
`checkForActivePopup`. For `pendingNewSMS` with no active Bluetooth call it
shows `SMS_INCOMING_MESSAGE` / `popupincomingsms` as a PRIMARY popup at
`0x002B6C75-0x002B6C96`; otherwise it calls `announceSMSMessage` at
`0x002B6CA2`.

**CONFIRMED.** `announceSMSMessage` at `0x002B85C2` can show the same popup
at `0x002B8717-0x002B8738` and invokes TTS `readout` at
`0x002B8740-0x002B8750`. `AppStateManager.closeSmsPopups` at
`0x0025817B` dequeues `SMS_INCOMING_MESSAGE` and `SMS_MESSAGE_FULL`.

**INFERRED PRODUCT RULE.** Projection ownership needs two narrow SMS gates:
native popup/full-screen suppression and native announcement/TTS suppression.
MAP/message ingestion may remain alive. Gating only the popup can still produce
duplicate audio.

### General foreground arbitration

**CONFIRMED.** `AppStateManager.checkForegroundAvailability` at
`0x0025250E` rejects app foreground requests for `RearCamera`,
`DisplayOff`, a blocking `Popup`, or `FullPopScreen`; otherwise it returns
`true`. `onAppRequestForeground` at `0x002525D2` returns the result and
reason through `IHMIRequest`. `onStateChange` at `0x002523DB` publishes
popup state and re-evaluates a pending foreground request at
`0x002524C4-0x002524FD`.

**HIGH.** This stock pending/retry foreground path is the preferred OEM
integration seam. Projection should participate in it rather than run as an
independent replacement shell.

### Camera preemption and return

**CONFIRMED.** `DisplayManager.displayMessageHandler` at `0x002BA764`
accepts `rearCameraStatus`, updates `mRearCameraStatus`, and dispatches
`DISPLAY_REARCAMERA_STATUS` at `0x002BA7CF-0x002BA7FA`. It tracks display
layers and normalizes middleware layer `short_term_cam_full` to
`LAYER_CAMERA_FRONTSIDE` at `0x002BA812-0x002BA89F`.

**CONFIRMED.** `LayerManager.onLayerChange` at `0x002D4D6F` handles backup,
cargo, and front/side camera layers:

- backup/cargo visibility shows `POPUP_CAMERAS` with CAMERA type at
  `0x002D4DEA-0x002D4E10`;
- front/side visibility removes an incompatible Controls popup, shows
  `POPUP_CAMERAS` with DTV_CAMERA type, and calls
  `goto(SCREEN_CAMERA)` at `0x002D4E30-0x002D4E9D`;
- after camera visibility clears it dequeues the camera popup, calls
  `IStructure.back()` if `SCREEN_CAMERA` is current at
  `0x002D4EBF-0x002D4EE1`, then removes that screen from the stack at
  `0x002D4EE8-0x002D4EF8`.

Camera priority is also a foreground-request rejection. Stock therefore already
provides both preemption and navigation-stack return; projection can resume if it
was underneath and its session remains active.

### Temporary stock overlays

**CONFIRMED.** `HVACManager.onHVACZoneLeftTemp` at `0x0026DA06` and the
right equivalent at `0x0026DACC` compare new values with cached state.
Outside `MAIN_HVAC`, a qualifying change uses `popupManager.show` for stock
`POPUP_HVAC` with climate type, zone, and temperature. The left show sequence is
`0x0026DA68-0x0026DAB9`.

The popup manager is independent of `currentBranch`; popup activation and
dismissal do not replace the underlying branch.

**HIGH.** This is the correct mechanism for temporary comfort overlays on top of
projection. The heated-seat/heated-wheel event route itself is not yet proved;
the temperature path proves the reusable popup-layer behavior, not every comfort
control.

### Era-compatible QNX HNM comparison

**CONFIRMED REFERENCE / UNKNOWN ON RA4.** QNX CAR 2.1 HNM documents
a HandsFreePhone event-source that subscribes to Bluetooth HFP status and
emits prioritized presentation events. `HFP_CALL_INCOMING` is a policy entry,
and HNM display events support less-intrusive fallback window types plus
restoration of the previously displayed event after a transient event ends.

This proves that an era-compatible QNX design can keep HFP ingestion active
while separately arbitrating its foreground presentation. It strengthens the
product rule above, but it is not evidence that RA4 contains HNM or that its
policy may be modified. The exact RA4 SWF still performs native call goto/popup
actions downstream of HFP, and SMS TTS is a separate traced path. A recovered
HNM hit would require import/startup/policy correlation before it could become
a candidate seam; absent that, the Harman presentation paths remain the target.

Official references:

- https://www.qnx.com/download/download/26205/HMI_Notification_Manager.pdf
- https://support7.qnx.com/download/download/26319/PPS_Objects_Reference.pdf

### Reference audio separation and RA4 consequence

**CONFIRMED REFERENCE / UNKNOWN ON RA4.** Official QNX CAR 2.1 keeps HFP
command/status, HNM visual events, Audio Manager routing/ducking, Now Playing
pause/resume coordination, and the io-bluetooth/io-acoustic/io-audio handsfree
speech path separate.

This supports preserving HFP while projection owns ordinary call/message
presentation. It also proves why the visual lease is insufficient: audio source,
playback, and microphone/voice path need separate fail-open ownership.

**CONFIRMED RA4:** ignored recovered plaintext
`P/share/audioDSP/audioMgrCMC.conf:24-29` maps stock sources including
`audioApp` to MME; AudioCtrlSvc is separately identified in the corpus.
projection call state reaches the status bar; native call and SMS/TTS
presentation are separately traced. **UNKNOWN:** generic QNX service use,
actual source types/priorities, playback callbacks, projected call/assistant
microphone handoff, speaker routing, and owner-death cleanup.

The recovered-tree probe now includes exact reference audio PPS paths, Audio
Manager symbols, media-player phone/status, io-audio, io-acoustic, and
pps-bluetooth. It also groups the exact recovered RA4 projection-session,
projection-call, foreground-request, native call/SMS/TTS, previous-screen,
camera-layer and HVAC-popup strings as `ra4_foreground_policy`. Co-occurrence
with projection-service markers is a tier-1 manual-XREF target, not permission to
change the stock policy. A hit remains a candidate until architecture, imports,
startup, and client/server role are correlated.

Official references:

- https://www.qnx.com/developers/docs/6.6.0_anm11_wf10/com.qnx.doc.am.system_services/topic/audio_management.html
- https://support7.qnx.com/download/download/26213/System_Services_Reference.pdf
- https://www.qnx.com/download/download/26838/PPS_Objects_Reference.pdf
- https://support7.qnx.com/download/download/26201/Bluetooth_Architectural_Overview_and_Configuration_Guide.pdf

## Arbitration contract

| Condition | Foreground | Projection session | Native Phone/SMS presentation |
| --- | --- | --- | --- |
| camera or critical/eCall | stock takeover | preserve when safe | critical stock policy wins |
| permitted comfort overlay | stock popup over current screen | preserve | no unrelated takeover |
| projection active and visible | projection full screen | active | suppress native popup/goto/TTS |
| projection active, user in Uconnect | ordinary stock screen | active | projection still owns projected interactions |
| projection inactive/disconnected | ordinary stock behavior | inactive | restore normal native presentation |

The fourth row is session-based, not visibility-based. Returning to Radio while
CarPlay stays connected must not re-enable duplicate native call/message
foregrounding.

Return behavior:

- Return to Uconnect: remember/navigate to a stock branch without stopping the
  projection session.
- Return to projection: if `sessionActive`, navigate to `DEVICE_PROJECTION`;
  only start when no session exists.
- Temporary popup: do not change branch.
- Camera: reuse existing `goto` / `back` / `removeFromStack`.
- Disconnect/error: reuse existing source-derived or `MAIN_PHONE` fallback.

## Unknowns and next targets

- **UNKNOWN:** complete consumers of `PROJECTION_BACKTO_CAR` and the exact stock
  Return-to-Uconnect screen transition.
- **UNKNOWN:** a supported stock policy bit/API for suppressing native call/SMS
  presentation. Presentation seams are proved; sanctioned configuration is not.
- **UNKNOWN:** exact RA4 logical audio sources, ducking/pause-resume callbacks,
  speaker route, and microphone ownership. Reference separation is known; the
  Harman contract is not.
- **UNKNOWN:** heated-seat/heated-wheel event-to-popup chain.
- **UNKNOWN:** exact return behavior for every camera variant/configuration;
  backup/cargo use popup layers while front/side explicitly enters a screen here.

Best next static targets:

1. run the bounded `swf_abc_inspect --xref` mode added in commit
   `b4cc616` on `PROJECTION_BACKTO_CAR`, `DEVICE_PROJECTION`,
   `mPrevScreenBeforeActiveCall`, `SMS_INCOMING_MESSAGE`, and HVAC popup names;
2. trace the projection screen's Return-to-Uconnect control from those consumers;
3. trace heated-seat/heated-wheel ICS events into the popup manager;
4. run the 122-marker recovered-tree census, prioritizing files where
   `ra4_foreground_policy` and `projection_service` co-occur, then correlate HNM/
   HandsFreePhone candidates with startup configuration and the SWF call graph;
5. trace audio focus separately before proposing runtime integration.

## Resource effect

This investigation adds documentation only: 0 radio installed bytes, 0 radio
runtime writes, and 0 radio staging bytes. Product caps remain 15 MB installed,
4 MB runtime growth, 8 MB additional update peak, 45 MB protected stock reserve,
and 5 MB unallocated planned-peak margin. No complete projection engine is
declared resident or external until measured; an engine that cannot meet local
storage/CPU/RAM constraints is `EXTERNAL_COMPUTE_REQUIRED`.
