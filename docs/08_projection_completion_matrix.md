# 08 - Projection completion matrix

Updated 2026-09-06. This is the completion audit for the OEM-style projection
goal. It distinguishes recovered stock behavior, host-model conformance and
actual RA4 target proof. A host test or string reference never substitutes for
target behavior.

Status vocabulary:

- **STATIC_PROVED**: direct read-only artifact/control-flow evidence.
- **MODEL_PROVED**: original host implementation exercises the required policy.
- **TARGET_UNPROVED**: architecture exists, but no legitimate RA4 build/run proves it.
- **EXTERNAL_EVIDENCE_REQUIRED**: completion needs an artifact, supported interface
  or authorized spare-hardware observation not currently accessible.

| Requirement | Current evidence | Status | Evidence still required for production |
| --- | --- | --- | --- |
| Preserve stock Radio/Media/Climate/Controls/Phone/Messaging/Settings | Product contract and current prototype render no replacement factory screens | MODEL_PROVED / TARGET_UNPROVED | Supported stock application/screen loading boundary and target observation |
| Full 640x480 projection while selected | `DEVICE_PROJECTION`; graphics.conf has OMAP3730/SGX530, CMC mtouch and `video_hmi`; QNX reference proves managed groups/focus | STATIC_PROVED / TARGET_UNPROVED | Exact stock group/class, buffer, z-order, focus/sensitivity, owner-death and render proof |
| Return to Uconnect without ending session | `sessionActive` is independent of current branch at FWS `0x002588C5-0x0025892C`; host model preserves session | STATIC_PROVED / MODEL_PROVED / TARGET_UNPROVED | Complete `PROJECTION_BACKTO_CAR` consumer and supported stock navigation action |
| Return to active projection without reconnect | `startProjection` at `0x002B5177` is distinct from `goto(DEVICE_PROJECTION)`; model changes foreground only | STATIC_PROVED / MODEL_PROVED / TARGET_UNPROVED | Exact return control and target session continuity measurement |
| Factory camera priority and return | DisplayManager `0x002BA764`; LayerManager preemption/stack unwind `0x002D4D6F-0x002D4EF8` | STATIC_PROVED / MODEL_PROVED / TARGET_UNPROVED | Spare-bench latency, every camera variant and projection restoration |
| Temporary comfort overlay | HVAC popup path `0x0026DA68-0x0026DAB9` proves branch-independent popup layering; model preserves owner/session | STATIC_PROVED / MODEL_PROVED / TARGET_UNPROVED | Heated-seat/wheel event-to-popup consumers and target overlay dismissal |
| Projection owns ordinary call presentation while active | Projection call event `0x002B4E18-0x002B4EBC`; native HFP presentation starts `0x00257983` | STATIC_PROVED / MODEL_PROVED / TARGET_UNPROVED | Supported policy/API that gates only native goto/popup, not HFP ingestion |
| Projection owns ordinary message presentation and audio | Native SMS popup `0x002B6C35-0x002B6C96` and TTS `0x002B85C2-0x002B8750` isolated | STATIC_PROVED / MODEL_PROVED / TARGET_UNPROVED | Supported popup plus TTS gate while preserving MAP/message ingestion |
| Emergency/eCall remains stock-owned | Emergency branch precedes ordinary BT processing; critical owner is explicit in both reference models | STATIC_PROVED / MODEL_PROVED / TARGET_UNPROVED | Configuration-specific target behavior and audio-priority confirmation |
| Inactive/disconnected/invalid/stale restores stock presentation | Host models invalidate state, retain sequence watermark and reject delayed replay | MODEL_PROVED / TARGET_UNPROVED | Real service epoch/sequence contract and failure/restart observation |
| Projection/HFP audio and microphone arbitration | `P/share/audioDSP/audioMgrCMC.conf:24-29` maps stock `audioApp` to MME; QNX reference separates HFP, visual, routing/ducking, playback and acoustic input | STATIC_PROVED (configuration/reference) / TARGET_UNPROVED | Recovered service census; exact source registration, priority, callbacks, mic owner-death; spare-bench tests |
| Tiny resident arbitration implementation | JavaScript model plus C99 no-heap candidate; C source is 19,404 bytes across four files | MODEL_PROVED / TARGET_UNPROVED | C compile/tests, target ABI, linked map, allocated package bytes |
| Protected 77 MB envelope | Caps are 15 MB installed, 4 MB writable, 8 MB extra peak, 45 MB protected, 5 MB residual | MODEL_PROVED / TARGET_UNPROVED | Mount-specific boot/use/update measurements and target package accounting |
| Existing stock projection-screen reuse | `DeviceProjection.swf`, `PROJECTION_BACKTO_CAR` and service/session symbols are referenced by stock HMI | STATIC_PROVED (references) / TARGET_UNPROVED | Complete physical screen artifact, descriptor/loader and supported backend binding |
| Stock lifecycle for an already authorized resident Xlet | Secure AMS startup, non-autostart install state, generic Apps tile, DRM-checked native `startApp` and later foreground arbitration are recovered | STATIC_PROVED / TARGET_UNPROVED | Legitimately authorized inert package returned by target `getAppList`, target launch/fallback observation |
| Authorization of a new resident component | Detached signature/DRM/developer-token binding is recovered; no legitimate new-project issuer or credential is available | EXTERNAL_EVIDENCE_REQUIRED | Written supported package/DRM/developer route or legitimately issued inert signed sample; no bypass |
| Complete CarPlay/Android Auto engine | QNX 6.6-era docs prove a legacy CarPlay USB role-swap transport family; later Smartphone Connectivity is a modular vendor lead, but public 2.0 remains QNX 7.x | EXTERNAL_EVIDENCE_REQUIRED | Support-supplied legacy drivers plus compatible receiver or authorized port, Apple/Google access, target ABI and measured CPU/RAM/storage |
| USB device-role path | OMAP3730 supports OTG host/peripheral; FCC identifies BE2800; Mopar distinguishes the SD/USB/AUX data hub from charging-only ports; Chrysler-attributed D2784B data maps one power/D-/D+/ground path to Radio C2; QNX 6.6 has generic `io-usb-dcd`, but the public OMAP3730 BSP lists OTG Host only | STATIC_PROVED (silicon/platform/products); HIGH external circuit map / TARGET_UNPROVED | Active hub/controller or mux identity and reversibility, VBUS behavior, D2784B-to-rear-board-to-main-board/OMAP route, installed DCD/function driver, startup and role-switch proof; FCC block diagram/schematics are permanently confidential |
| No signing, license or activation bypass | Repository/PR path audit contains no vendor payload, license, key, certificate or activation material | STATIC_PROVED | Re-audit every future package and deployment design |

## Current implementation evidence

The browser-based bench in `prototype/resident_hmi` is development-host only.
At exact head `94791f6`, all eight modules parse and all 20 committed test bodies
execute in the isolated V8 fallback harness; 89 assertions pass. Coverage includes
return/resume, camera, critical takeover, comfort overlay, disconnect,
stale/invalid fallback, replay rejection and point-of-use lease expiry. This is
not the unavailable Node runner. The bench installs zero radio bytes.

The C99 candidate in `prototype/projection_arbiter_c` carries the same policy
without heap or I/O and enforces `sizeof(PA_Arbiter) <= 128` at compile time.
Its time-aware presentation accessor is designed to expire stale ownership at
the point of use. Structural inspection finds ten matched public functions and
70 assertions, but it has not yet been compiled. Local command execution is unavailable. GitHub
Actions runs `34038125932` and `34038125990` each created the conformance job
but terminated before runner allocation: `runner_id` was 0 and the step list was
empty. No checkout, compiler or test command ran. The workflow is manual-only
until hosted runners are available, preventing infrastructure failures from
masquerading as code failures. The C test remains intended coverage, not a
passing target or host build.

## Closest completion path

1. Recover local command execution and run both host suites plus the ignored
   `MainSupplement.swf` consumer XREFs.
2. Run the 122-marker recovered-tree probe and schema-validating correlator;
   inspect exact `DeviceProjection.swf`, RA4 AMS/AppManager/Xlet lifecycle,
   service, startup, audio and Screen candidates in tier order.
3. Resolve `PROJECTION_BACKTO_CAR` and heated comfort popup consumers from
   the hash-identified firmware; recover source registration, ducking/playback
   callbacks, call route and microphone ownership.
4. Use the proved Xlet launch lane only with legitimate package authorization;
   establish the screen/service contract and compile the transport-free arbiter.
5. Select and size a legitimate projection backend. Keep it local only if it
   passes storage, RAM and CPU gates; otherwise mark only that engine
   `EXTERNAL_COMPUTE_REQUIRED`.
6. Under separate authorization, use spare hardware to measure camera/overlay/
   call/message/fallback behavior and all storage peaks.

The project goal is not complete until every TARGET_UNPROVED row has direct
target evidence. The [evidence-gate manifest](10_evidence_gates.md) identifies
the exact artifact, interface or measurement that closes each row. No step here
authorizes a radio write, modified firmware, credential derivation or
safety-feature bypass.
