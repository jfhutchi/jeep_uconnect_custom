# 10 - Evidence gates and acquisition manifest

Updated 2026-09-06. This is the exact evidence still needed to turn the current
static/model architecture into a deployable OEM-style projection application.
It separates work that is locally present but temporarily inaccessible from
evidence that does not exist in the current corpus.

This document is not a radio-write, flashing, credential, signing, activation,
or license-extraction procedure. Vendor artifacts remain ignored and must never
be committed.

## Gate classes

| Class | Meaning | Current response |
| --- | --- | --- |
| LOCAL_EXECUTION_RECOVERY | Closed 2026-09-06: Python, Node, static inspection and WSL C99 execution work | See post-reboot checkpoint; recovered artifacts remain outside Git |
| ARTIFACT_NOT_FOUND | Required historical evidence was not found in the image/recovered files | Search existing off-radio copies and backups; do not create high-volume radio logs |
| LEGITIMATE_CONTRACT_REQUIRED | A compatible backend, SDK, package identity or supported policy API is not present in the recovered corpus | Obtain authorized vendor/provider documentation or implementation; do not guess wire fields or bypass authentication |
| SPARE_HARDWARE_REQUIRED | Static/model evidence cannot prove runtime priority, timing, resource use or crash fallback | Use only a separately authorized spare RA4 bench after the lifecycle gate is legitimate |
| MEASUREMENT_REQUIRED | A build or runtime exists but exact bytes/CPU/RAM/latency are unknown | Measure before accepting the feature; never consume the 45 MB stock reserve |

## Gate A - local static closure

These artifacts are already represented by hashes and derived evidence in the
repository. The runner recovered after reboot. The
[checkpoint](../reports/ra4_post_reboot_checkpoint.md) records executed host tests,
strict C99 build, 122-marker census and HMI XREFs. Remaining static questions
are evidence gaps, not command-runner blockers.

| Artifact | Expected SHA-256 | Required read-only query | Closure supplied |
| --- | --- | --- | --- |
| MainSupplement.swf | e9d796ea4b4c83ed518bfe3b3c341e54e510a1ae0f78ebbffbd655b7c36a3258 | bounded AVM2 consumer XREF for PROJECTION_BACKTO_CAR, DEVICE_PROJECTION, native call/SMS names and seat/wheel popup names | exact Return-to-Uconnect consumer, resume action, comfort popup chain |
| HVACHomeScreen.swf | cf894eb59e31b7e7b426dfc2eeb2ab9fc3bd14c90082408e8367e54a404f1f18 | units/ready and cache consumers only | units-epoch behavior visible to the stock screen |
| hvac.lua | 3ddadef2296acb475b307893b9a61fa8c7324dce336dcb3baaef1ff89a5b0b50 | PersonalConfig temperatureUnits/ready producer and restart paths | whether units/restart invalidates cached temperature |
| hmiGateway | 8d7fe8789bb012a66fbebd1bd44eefa506c672a5d70c90fbf92b3a5a6f01ec82 | HVAC callback wrapping plus audio/service references | native delivery and service-loss ordering |
| Synctool.elf | aa2e2c425d42a5f60427a89817f676b0d32b3ce73057d89355248acc24d4e330 | hash-gated evidence anchors and any newly bounded selector-name references | version-drift check and remaining static selector evidence |
| Recovered RA4 filesystem trees | source-image and decoded-tree hashes in the current handoff | complete bounded 122-marker census for media/codec, exact `DeviceProjection.swf`/return events, RA4 AMS/AppManager/Xlet lifecycle, QNX CAR reference lifecycle/notification/audio, legacy QNX 6.6 Apple USB role swap/device mode/DCD, and Harman ModuleLink/servicebroker/projection names | whether the physical stock projection screen, backend/service path, authorized-app lifecycle components, audio/Screen runtime or codec path is present and boot-configured |

Required tools are already tracked:

- analysis_tools/swf_abc_inspect.py
- analysis_tools/lua51_inspect.py
- analysis_tools/arm_elf_analysis.py
- analysis_tools/synctool_evidence.py
- analysis_tools/qnx_media_runtime_probe.py
- analysis_tools/qnx_runtime_correlation.py

Run `qnx_media_runtime_probe.py` first, then pass its redacted JSON to
`qnx_runtime_correlation.py`. Inspect tier-1 configuration, startup and
stock-specific candidates before cross-family and single-family candidates.
The correlator's tier is only a deterministic inspection order: a positive hit
must still be closed with imports, XREFs, process-start evidence and an
authorized interface contract. Roots that share a basename receive deterministic
ordinal labels, and the correlator rejects stale marker inventories or duplicate
root/path identities so evidence from separate recovered segments cannot merge.

A valid result must include the input hash, bounded method/function/address range
and tool version/commit. A string hit alone is not a consumer or ABI proof.
Complete disassemblies and vendor files do not belong in Git.

## Gate B - historical Synctool correlation

The exact numerical relationship for the successful
Harman_CMC_VP4_NA_VP4_2017Q2_UPDATE_MY14_REVA.lyc selection needs one
contemporaneous runtime evidence set.

Preferred existing evidence, in order:

1. An old copy of /hbsystem/multicore/navi/3/LOGFILE.DAT from the successful
   17.11.17 map-update run.
2. Its existing rotated/index/old companions, if they were captured at the same
   time.
3. An existing off-radio backup of the Synctool stdout/file sink.
4. A legitimate non-secret installed-license inventory from the same device/run.

Minimum useful fields in one run:

| Field | Why it is needed |
| --- | --- |
| App SKU ID decimal | identifies the selected module-0x284 Application SKU |
| device.nng valid/status line | establishes the same run/device context |
| activable/incompatible/invalid record event | supplies per-record classification |
| full-scan target=my14_reva marker/count | ties the known successful filename to a known diagnostic field without printing other names |
| discard and file-copy exclusion events | ties source-container ordinal grouping to the final copy plan |
| update/run timestamp or outer-log correlation | proves contemporaneity with the successful update |

Use analysis_tools/synctool_log_probe.py read-only. It prints offsets, marker
classes, numeric App SKU, full SHA-256 value tokens, and a specific
target=my14_reva label/count. It never prints arbitrary record/file values.
Matching tokens correlate field bytes; event markers supply context. Neither
fact alone establishes the semantic meaning of selector 0x284 or a record.

The original 16,034,824,192-byte image and recovered outer SWDL log were already
scanned completely for intact plain-text markers. Repeating that identical scan
cannot produce the missing runtime trace. The next search must target a distinct
existing diagnostic capture or backup.

Do not enable diagnostic capture on the radio, stage a large archive into the
approximately 77 MB writable pool, parse license payloads, derive activation
material, or commit a raw log if it contains vendor/private data. A sanitized
tool report containing hashes, offsets, counts and non-secret numeric identifiers
is sufficient for Git.

## Gate C - legitimate stock integration contract

Static names prove expected components but not an authorized caller contract.
The following must come from an existing stock implementation, authorized SDK,
or vendor/provider documentation:

| Contract | Exact missing evidence |
| --- | --- |
| phoneProjectionService | registration name, interface/version, transport framing, owner-death and reconnect semantics |
| stock app/screen lifecycle | accepted package identity, descriptor/entry point, foreground request caller and deterministic unload/crash fallback; census `bar-descriptor.xml`, `Qnx/Elf`, `run_native`, app-installer and service-start markers, but do not assume QNX reference BAR acceptance |
| QNX CAR reference services | whether `/pps/system/navigator`, Launcher/Authman, HNM, UI Core, QtQnxCar2, Audio Manager, Now Playing, `io-acoustic` or mm services are installed/started; official names alone are not a stock contract |
| Return to Uconnect | complete PROJECTION_BACKTO_CAR consumer and previous-stock-branch rule |
| native presentation policy | supported volatile/default-open gate for ordinary call popup/goto, SMS popup and SMS TTS; if HNM exists, prove its HandsFreePhone policy/plugin relationship to the traced Harman SWF paths without editing the policy |
| video surface | start from confirmed graphics.conf 640x480 OMAP3730/SGX530 plus `video_hmi`; prove stock group owner/name, window type, z-order, buffer format/count/stride, post synchronization, lifecycle and owner-death |
| touch | start from confirmed CMC mtouch/scaling and factory Screen event use; prove focus/sensitivity owner, coordinate transform, cancellation at preemption, and delivery only to selected projection |
| audio | start from confirmed `P/share/audioDSP/audioMgrCMC.conf:24-29` `audioApp` -> MME mapping; prove AudioCtrlSvc/MME registration, source types, media/prompt/call priority, ducking versus pause/resume callbacks, mic/speaker ownership, owner-death and stock restoration |
| USB/authentication | legitimate CarPlay/Android Auto device/session/authentication interface; QNX 7 documents projection-aware Android/Apple `usblauncher_otg` modules, but RA4 equivalence is unknown |
| projection engine | authorized ARM32/QNX-compatible implementation and redistribution/runtime requirements; QNX Smartphone Connectivity is the identified candidate family, not yet a compatible build |
| hardware video decode | installed decoder/DSP server and supported client ABI, boot reservation, licensing, buffer contract and measured CPU/RAM; OMAP3730 silicon capability alone is insufficient |
| USB device role | Exact Harman BE2800 platform, data-hub versus charging-port distinction, UCI cable and HIGH Radio C2 D2784B power/D-/D+/ground mapping are identified; still require active hub/controller or mux identity and role behavior, VBUS control, D2784B-to-OMAP route, compatible DCD/function driver, startup and host/device transition |

No direct localhost socket, SWF/native address call, guessed ModuleLink field,
generic QNX CAR PPS write copied from a reference manual, monolithic Full
Screen HMI replacement, persistent disable preference or unsigned/development
package is an acceptable substitute.

## Gate D - spare-hardware proof

Only after Gate C supplies a legitimate lifecycle may a separately authorized
spare RA4 run a benign, reversible trial. The first trial has no projection
engine and no phone/message suppression; it proves only registration, foreground,
surface teardown and stock fallback.

Required observations in later staged trials:

| Scenario | Required result |
| --- | --- |
| explicit Return to Uconnect | stock screen appears; active projection session continues |
| Return to Projection | same session resumes; prove backend effect of stock BacktoCar/start and exclude teardown/reconnect |
| backup/front/cargo camera | stock takeover is immediate and autonomous; prior foreground restores correctly |
| permitted comfort popup | stock popup overlays and dismisses without session loss |
| ordinary projected call/message | projection owns presentation; no duplicate native popup/goto/TTS |
| critical/eCall | stock UI/audio always wins |
| inactive/disconnected/stale/adapter death | native Phone/Messaging behavior is default-open and restored without cleanup |
| malformed/replayed snapshot | rejected; cannot reacquire expired ownership |
| renderer/backend crash | stock HMI and camera remain usable |
| boot and removal | stock behavior returns with no persistent disable state |

Do not use the vehicle's only working radio for first execution. The bench
wiring/power/network details require authoritative part-specific references and
are outside this static manifest.

## Gate E - resource and engine decision

The first stock-facing trial must remain at or below 3 MB installed, 1 MB normal
writable growth and 6 MB additional staging. The complete product caps remain
15 MB installed, 4 MB normal writable growth and 8 MB additional staging while
protecting 45 MB of the approximately 77 MB observed free space.

Measure, in bytes and on the actual mount:

- every installed file and private dependency, logical and allocated size;
- configuration, state, rotated logs, crash data, cache and temp growth;
- simultaneous old/new/staging/rollback peak, including failed update;
- minimum free space across boot, stock UI, navigation and Bluetooth/phone use;
- resident RAM, graphics buffers, CPU, startup and end-to-end latency;
- stock-service growth attributable to the adapter.

A local engine is accepted only if its legitimate build passes storage, RAM,
CPU, graphics, USB, authentication and latency gates. If it fails, classify only
the engine EXTERNAL_COMPUTE_REQUIRED. The tiny RA4-resident stock-facing adapter
remains required.

## Evidence-to-decision map

| Evidence acquired | Decision it unlocks |
| --- | --- |
| Gate A projection XREFs | exact return/resume and popup/audio static contract |
| Gate A media/runtime census | installed decoder/DSP plus QNX Audio Manager/Now Playing/acoustic and Harman AudioCtrlSvc/audioMgrCMC candidates, or a bounded exact-tree negative |
| Gate C audio contract | exact stock logical-source, playback, call-route and microphone owner-death boundary without disabling HFP/MAP |
| Gate A temperature trace | safe read-only quality model; still no replacement Climate screen |
| Gate B historical log | actual App SKU and MY14 record/container/copy-plan relationship |
| Gate C lifecycle/policy | legitimate read-only adapter and no-engine screen build |
| Gate D spare bench | OEM-style foreground/camera/overlay/fallback acceptance |
| Gate E measurements | resident engine acceptance or evidence-backed external classification |

Until these gates are satisfied, the current deliverable is an evidence-backed
architecture and tested host policy model, not a deployable RA4 product. This
manifest turns each unknown into a named artifact, interface or measurement and
prevents an unknown from being silently implemented as an assumption.

## Resource effect

This document and its PC-only tools install 0 bytes on the radio, create 0 radio
runtime writes and require 0 radio staging bytes.
