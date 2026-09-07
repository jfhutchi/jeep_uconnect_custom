# RA4 Xlet foreground admission, return and display release

Date: 2026-09-06. Starting canonical head `679d73ba5582431ad309cd9cde8925e749eca470`.
Read-only host analysis of existing owner-supplied artifacts; no target execution.

## Decision

**STATIC_PROVED stock behavior:** the recovered 640x480 AppsActiveScreen requests
the `ams` display on entry. On screen exit it requests a pause of the running
Xlet, when applicable, and then releases the `ams` display request. Its Close
handler instead sends a stop request and marks the app stopped to avoid the
ordinary exit pause. Re-entry can request the last paused app through `Resume`.

**Follow-up qualification:** the [native pause-policy trace](ra4_xlet_pause_watchdog.md)
proves `pauseApp` selects `stop` when the effective `xlet.PauseAllowed` field
is false. Its recovered default is false. The screen requests a pause, but the
downstream action is conditional; Return cannot be assumed to preserve every
Xlet or a future engine session.

The foreground API reaches a native HMI-admission check. The HMI rejects for
rear camera, display off, blocking popup or its eCall error-screen state. A
positive response permits native processing to continue into the existing
find/start path; it does not establish successful launch or presentation.

**STATIC_PROVED restriction:** the normal native `requestBackground(appId)`
path validates the supplied ID but builds its outgoing back event using the
configured **SuperApp UUID**, not that supplied ID. The HMI navigates only when
the event ID matches its running app and `APPS_ACTIVE` is current. This is not
evidence of a generic custom-Xlet background API. No identity substitution or
SuperApp configuration change is proposed.

**HIGH integration direction:** stock screen navigation, Xlet lifecycle and
display ownership are distinct operations. A supported Return action should
use the stock path qualified for the new application's identity. A stop/close
operation cannot stand in for a session-preserving Return. **UNKNOWN:** engine
continuity across pause, supported custom permissions, physical surface/input
release, camera/critical coexistence, and bounded reclaim of a hung app.

## Artifacts and coordinate conventions

Paths are relative to ignored `analysis_ra4_18.45.01/work/`. Hashes are SHA-256.

| Artifact | Path | Bytes | Hash |
| --- | --- | ---: | --- |
| Native AppManager | `hidden_hbc_ifs/segment_00f20000/files/bin/appManager` | 1268061 | `608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591` |
| Shared HMI | `primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/MainSupplement.swf` | 1407783 | `e9d796ea4b4c83ed518bfe3b3c341e54e510a1ae0f78ebbffbd655b7c36a3258` |
| 640x480 app screen | `primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/skins/default/swf/AppsActiveScreen.swf` | 6467 | `235c091f1bebcb0af388b05da09a0f61349022ccf3ab00365e544f08c677d888` |
| Kona library | `secondary_iso/usr/share/XLETS/base/kona/lib/kona.jar` | 3062680 | `19390472018f02d998690b982f00eb68da5d40d7a8d6fba91499677651015f92` |

Kona member `com/harman/appManager/AppManagerImpl.class` is 26295 bytes, hash
`2ddb5e6efd235a3b85b6743585325351d178bbab7c7dff2e476ad2ad08978714`.
Java BCIs are relative to each method's Code array. Native addresses are ARM
virtual addresses, not file offsets. SWF addresses refer to reconstructed FWS
offsets: MainSupplement ABC 0 base `0x264EB`, 15157 methods; AppsActiveScreen
ABC 0 base `0x85D`, 36 methods. Complete selected method bodies and branch
operands were inspected; only original analysis and selected anchors are recorded.

## Foreground admission chain

| Layer | Anchor | Static consequence |
| --- | --- | --- |
| Java AppManagerImpl | Both `requestForeground(String)I` and `requestBackground(String)I`, BCI `0x06` / `0x09` | Construct `AppMgrPermission("appMgr")` and call `checkPermission` before IPC |
| Java request construction | BCI `0x25`, `0x3D`, `0x44` in both methods | Put supplied `appId` in a map, select the respective request name, invoke SvcIpcClient |
| Java IPC arguments | BCI `0x40` / `0x41` / `0x42` | Pass two true flags and integer `2147483647`; the meaning/units of the final argument are not established here, so no bounded timeout is claimed |
| Native dispatch | `0x15694C` / `0x156960` | Compare `requestForeground`, call handler `0x142CDC` |
| Native handler | `0x142E70` | Call HMI foreground-check routine `0x142468` after parameter validation |
| HMI request | `0x1426A4`, `0x1426A8`, `0x1426D0` | Materialize `isForegroundClear`, serialize parameters and invoke through the interface vtable |
| HMI local decision | MainSupplement method 593, `0x25250E` | Return a String: `RearCamera`, `DisplayOff`, `Popup`, `FullPopScreen`, or literal `"true"` |
| HMI reply | Methods 594 / 2804, `0x252616`, `0x25263A`, `0x2786E5`, `0x2786F2` | Convert admission into a JSON Boolean `foregroundClear` in `rsp_isForegroundClear`; local String `"true"` is not the wire type |
| Native reply parsing | `0x1427F8`, `0x142808` | Require JSON `isBool`, then read `asBool`; a string-valued Boolean would fail this checked response path |
| Denied / allowed | `0x1428F8`, `0x1428FC`, `0x142970` | False selects result `0x33` (51) and skips find/start; true can reach existing find/start routine `0x13B2DC` |

Null/malformed foreground replies are rejected on observed paths with result
`0x19` (25); example calls are `0x142854`, `0x1428A0`, `0x142920` and
`0x142940`. These observations are admission/error handling, not a timeout,
hang-recovery or authorization bypass proof. Existing entitlement/start checks
and errors remain part of the downstream launch path.

Method 594 suppresses an additional immediate response while `mPendingChange`
is already true. Its denial path sets that flag. Method 592 `onStateChange`
rechecks availability at `0x2524D1`; when clear it calls
`appRequestForegroundReturnSignal(true, "stateChanged")` at `0x2524F4` and
clears the flag at `0x2524FD`. Method 2806 emits a `foregroundClear` signal with
Boolean true at `0x278793` / `0x2787A4`. This does not prove an application
resumes automatically or that the original synchronous request stays pending.
The native denied request and the later HMI signal are separate observations.

## Background request identity restriction

Native dispatch compares `requestBackground` at `0x156970` and calls handler
`0x139BE0` at `0x156984`. The handler rejects missing/non-string appId, reads
and logs the supplied ID, and checks pending operation state at `0x139D70`.
The pending branch calls helper `0x13968C` and returns `0x21` (33); its eventual
deferred behavior is not resolved in this report.

On the non-pending path:

1. The outgoing `appId` JSON slot is obtained at `0x139E04`.
2. `0x139E0C` calls the AppManagerCore singleton accessor `0x16CF74`.
3. `0x139E18` calls getter `0x16E848`. That getter reads the string member at
   core offset `0x240` and logs `AM:getSuperAppUUID()` using literal `0x20B9A8`
   at `0x16E87C` / `0x16E880`. Thus this value comes from configured SuperApp
   state; it is not the request's local appId string.
4. `appToStart` is set to the empty string at `0x139E70` through `0x139E98`.
5. `invokeAppBackButton` is built at `0x139EBC` / `0x139EC0` and sent through
   helper `0x17C98C` at `0x139ED0`; response code zero is issued at `0x139EFC`.

A zero response here is not a pause, stop or display-release acknowledgment.
MainSupplement method 6410 loads the back-event property name at `0x2A7D18`
and checks its presence at `0x2A7D1C`.
With empty appToStart it constructs `INVOKE_BACK` using the event's appId and
dispatches at `0x2A7D55`. Nonempty appToStart takes a different startXlet path.
Method 564 binds INVOKE_BACK to `onInvokeBack` at `0x250A5C` / `0x250A61`.

Method 569 `onInvokeBack` compares the event ID to `getRunningAppId` and checks
current branch `APPS_ACTIVE` at `0x251A6A` through `0x251A8E`. If both hold,
VP3/VP4/MP4 variants navigate to `APPS_HOME` at `0x251AED`; other variants go
to `MORE_MAIN` at `0x251B09`. Otherwise it returns without that navigation.
It does not itself invoke pause or stop. The following stock screen lifecycle
supplies those operations when the active app screen is actually exited.

## Stock app screen: Return, release, resume and Close

The decoded class is explicitly
`screens.NA_EU.RES_640x480::AppsActiveScreen`. This identifies a 640x480 HMI
screen implementation; it does not measure the app-owned drawable area or
prove the live unit's asset selection.

| Method | FWS anchor | Behavior |
| --- | --- | --- |
| `screenIn`, 2 | `0x24B6` | `requestDisplay("ams", true)` |
| `screenIn`, 2 | `0x2554` | If running and last-running IDs differ, or a pause is pending, call `startLastPausedApp("Resume")` |
| `screenIn`, 2 | `0x258C` | If both running and last-running IDs are empty, navigate to MAIN_APPS |
| `screenOut`, 3 | `0x25CD`, `0x25DA` | With nonempty running ID and `mStopped == false`, call `pauseXlet(runningId)` |
| `screenOut`, 3 | `0x25E9`, `0x25F9` | Call screenOutComplete, then `requestDisplay("ams", false)` on the normal return path, without a conditional pause-ack check in this method |
| `onClose`, 6 | `0x2778`, `0x2781` | With nonempty running ID, call `stopXlet` and set mStopped true, then navigate |

MainSupplement method 6444 serializes `pauseApp` and sends it at `0x2A98AD`.
Method 6443 separately serializes `stopApp` and sends it at `0x2A982C`.
Method 6469 returns false for an empty last-running ID, otherwise delegates to
`startXlet(lastId, suppliedArgument)` at `0x2AA0EB` and returns true. That
Boolean represents this wrapper's dispatch decision, not a completed resume.

MainSupplement DisplayManager method 7327 serializes a command to destination
`DisplayManager`, packet `requestDisplay`, with `requester` and **string-valued**
`value: "true"` / `"false"`, then sends at `0x2BA717`. Do not confuse that
wire schema with the Boolean foregroundClear reply. No raw surface handle or
replacement display command is inferred from this wrapper.

**Limit:** no explicit wait for a pause acknowledgment occurs between the
screenOut pause call and display-release request. Called functions may still
block or fail, and no deadline, independent watchdog, native compositor
completion or physical focus release has been proved. The presence of a release
call is not a fail-open guarantee for a hung Xlet or shared AMS VM.

## Product and next evidence

The [resident milestone](../docs/21_first_resident_runtime_proof.md) now treats
Return/pause/display release separately from explicit Close/stop. The supported
SDK must confirm both operations for a legitimate custom app identity; the
observed `appMgr` permission does not grant it. Do not label the app SuperApp,
enable daemon behavior or change factory identity/configuration to make a trace fit.

The [stock Xlet/AWT/LWUIT evidence](ra4_resident_xlet_view_path.md) proves a
candidate graphics API family. It does not show that a paused Xlet may retain
engine transport/audio, that resource limits permit it, or that provider
contracts allow it. A supported engine session owner and pause/resume contract
are needed before claiming Return preserves Android Auto/CarPlay.

**Follow-up:** the [display-owner report](ra4_display_owner_reclaim.md) now
resolves the HMI destination to LayerManager, follows `ams` release to native
Screen visibility, and identifies the AMS service-owner hide/order callback.
Device results are discarded by the Lua helper, and service-owner changes do
not establish per-Xlet failure detection while AMS stays present.

**Remaining technical target:** AMS/AppManager's per-Xlet pause/resume/error
acknowledgments and container/input removal while the shared service remains
alive. The [pause/watchdog follow-up](ra4_xlet_pause_watchdog.md) resolves
the pause-versus-stop policy and asynchronous submission, and identifies an
enabled per-app watchdog's queued stop request. It does not prove completion.
Determine whether display reclaim can complete independently when the
Xlet/VM is unresponsive. Keep camera, critical/eCall and comfort priority under
the stock owners. No target failure injection or deployment is authorized by
these static findings.

## Reproduction and validation

Use the existing host tools without executing recovered code:

```powershell
$py = 'analysis_work/post_reboot_20260906/venv/Scripts/python.exe'
$hmi = 'analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov'
& $py -m analysis_tools.swf_abc_inspect "$hmi/skins/default/swf/AppsActiveScreen.swf" --method 3 --count 100
& $py -m analysis_tools.swf_abc_inspect "$hmi/MainSupplement.swf" --method 569 --count 100
& $py -m analysis_tools.swf_abc_inspect "$hmi/MainSupplement.swf" --method 7327 --count 100
```

Native reconstruction uses `ArmElfAnalyzer(Elf32Image.from_path(path))`,
`disassemble(start, end)` and `plt_imports()`. Include paired ARM MOVW/MOVT
constants: the older PC-relative string-xref helper alone misses many references
in this executable. Jawa 2.2.0 decodes the two selected Java method bodies;
the original JVM inventory resolves their actual invocation references.

All committed additions are analysis/specification text. Vendor images,
disassembly outputs and Java artifacts stay in ignored local evidence paths.
Installed target bytes, normal growth and staging from this continuation are zero.

Fresh verification: four artifact hashes/sizes, one class hash/size, 29 SWF
instruction anchors, 16 native instructions and eight Java invocation BCIs
passed direct comparisons. Both SWF ABC bases/method counts, native Boolean
imports, SuperApp getter label and Java request/argument constants were also
checked. All 87 local links in the seven changed Markdown documents resolved.
The unchanged full host Python suite passed **150 tests, no skips**. No new
runtime claim follows from those host checks; no JavaScript/C99, target or
independent phone-bench test ran in this continuation.
