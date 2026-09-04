# RA4 18.45.01 anti-theft authentication flow

## Scope and result

This report traces the stock RA4 ROV PIN user interface through ModuleLink, the native gateway, the onOff service, the IOC decision routine, asynchronous state callbacks, popup behavior, and the post-unlock AppManager action. It does not derive, test, expose, or brute-force any PIN, comparator, challenge, diagnostic request, or secret. Static V850 analysis locates the IOC comparison and proves its successful branch without reproducing its contents.

The PIN flow is asynchronous. The keypad sends `checkAntiTheftPIN`; hmiGateway routes the AntiTheft destination to `com.harman.service.onOff`; `onoff/main.lua` writes the four input bytes to IPC channel 2 and returns immediately. The IOC compares them only in its enter-PIN state, updates a distinct anti-theft state on equality, and later publishes the state/counter/lock-time response. When a VP4 unit entered PIN state and subsequently receives unlocked, the HMI sends AppManager command `xletsReturnToNew`. Receiver-side analysis proves that this is a broad factory-app-state restoration followed by a head-unit reset, not a Java lifecycle transition and not a developer-mode toggle.

## Artifact provenance and offset convention

SWF code offsets below are offsets in reconstructed, uncompressed FWS byte streams produced in memory from the on-disk CWS files. They are not offsets in the compressed files.

| Artifact | Exact evidence |
| --- | --- |
| Keypad | `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/skins/default/swf/PopupAntiTheftKeypad.swf`; CWS 16,327 bytes; SHA-256 `27c7aa18abe9f95b05ab8d8f8314043a103a61f52be70946cb8bbba6c8ed7ddc`; FWS 30,731 bytes; DoABC offset `0x14F9` |
| Status popup | `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/skins/default/swf/PopupAntiTheft.swf`; CWS 6,976 bytes; SHA-256 `14b972fdd0f967713844e50109219715922eb2a9e479126b5e443128e3450b5e`; FWS 13,004 bytes; DoABC offset `0xA37` |
| ModuleLink and state manager | `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/MainSupplement.swf`; CWS 1,407,783 bytes; SHA-256 `e9d796ea4b4c83ed518bfe3b3c341e54e510a1ae0f78ebbffbd655b7c36a3258`; FWS 3,639,060 bytes; DoABC offset `0x264EB` |
| Local transport configuration | `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/ModuleLink.xml`, lines 1-4; span host `127.0.0.1`, port `4400` |
| Native ModuleLink gateway | `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/bin/hmiGateway`; 153,124 bytes; HBC image offset `0x43A000`; SHA-256 `8d7fe8789bb012a66fbebd1bd44eefa506c672a5d70c90fbf92b3a5a6f01ec82` |
| onOff service | `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/onoff/main.lua`; Lua 5.1 chunk; 66,272 bytes; HBC image offset `0x1B5CE58`; SHA-256 `41c0f3f2709c49d4a4f9b150b8c08c735515a9c50bbfbc2e4c36664d6466e698` |
| IOC firmware | `analysis_ra4_18.45.01/work/primary_iso/usr/share/V850/hs/cmcioc.bin`; 458,752 bytes; SHA-256 `c7bf247bfdb10b5dfda2802df1210671f6a1872140cdeebc014c109a9c77e012`; flat mapping `VA = file + 0x10000` |
| AppManager receiver | `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/bin/appManager`; 1,268,061 bytes; HBC image offset `0xCF000`; SHA-256 `608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591` |

## PIN submission

`PopupAntiTheftKeypad::onDone`, code offset `0x5892`, ActionScript debug lines 114, 116, and 117, loads `Peripheral.antiTheft`, loads the keypad's `mInput`, invokes `checkAntiTheftPin`, and returns. There is no conditional on a return value in this method.

The supporting keypad methods are `addListeners` at `0x557E`, `initScreen` at `0x5738`, `onKey` at `0x5801`, and `onDelete` at `0x584F`. They establish input mechanics; none locally validates the PIN.

`com.harman.moduleLink::AntiTheft::checkAntiTheftPin`, code offset `0x2AC4E7`, debug lines 254-258 in `MainSupplement.swf`, serializes and sends this command shape:

```json
{"Type":"Command","Dest":"AntiTheft","packet":{"checkAntiTheftPIN":{"pin":"<user input>"}}}
```

The JSON construction and `client.send` occupy `0x2AC4FA` through `0x2AC513`. `AntiTheft::<cinit>`, code offset `0x2ABEF4`, initializes `mDbusIdentifier` to `AntiTheft` at `0x2ABEFD` through `0x2ABF04`. `AntiTheft::<iinit>`, code offset `0x2ABF4A`, obtains the shared span connection and registers `ConnectionEvent.ANTI_THEFT` with `MessageHandler` at `0x2ABFC1` through `0x2ABFCF`.

## Native/backend route and decision boundary

CONFIRMED: hmiGateway maps the HMI destination AntiTheft to the onOff D-Bus service. Its destination resolver at file offset 0x7BE0 (VA 0x107BE0) compares AntiTheft. The request-proxy dispatch at file offset 0x8E18 (VA 0x108E18) performs the same comparison; the equal branch loads com.harman.service.onOff at file offset 0x9E3C (VA 0x109E3C) and /com/harman/service/onOff at file offset 0x9E4C (VA 0x109E4C).

CONFIRMED: onoff/main.lua registers checkAntiTheftPIN to Lua function 28. Root initialization assigns AntiTheftPinMsg=224 (0xE0). Function 28, source/debug lines 1116-1126, creates a five-byte IPC message, places 0xE0 in byte 1 and the four supplied input bytes in bytes 2-5, calls chan2.write(msg), and immediately returns an empty table. It performs no local comparison. Root startup opens IPC channel 2 at source/debug line 1596 and registers function 23, onIpcCh2Message.

Function 23, lines 687-1055, checks the channel interface version and decodes byte 7 as raw antiTheftState, byte 8 as antiTheftCounter, and byte 10 as antiTheftLockTime. Its state conversion at lines 921-953 maps raw 0 to locked, raw 1 to waitForVIN, raw 2 plus counter zero to enterPIN, raw 2 plus a nonzero counter to wrongPIN, raw 3 to unlocked, and raw 5 to forcedFotaUpdate.

The IOC behind channel 2 is the confirmed authentication decision boundary. Channel 2 registers through VA `0x2A258`/call `0x2A26A`, the receive loop reaches dispatcher `0x2B668`, and the channel switch at `0x2B934` selects the anti-theft branch at `0x2B694`. That branch calls PIN-decision routine VA/file `0x25658/0x15658`. The submitted bytes are compared only while the separate anti-theft state is in enter-PIN mode; equality at `0x256AE..0x256C2` changes that anti-theft state and publication flags. Publisher VA/file `0x2AD6C/0x1AD6C` reads and sends the changed state. Retry and lockout policy beyond this bounded success branch remain unknown; no PIN/comparator content is reproduced.

## IOC authorization domains and one-way relationship

The IOC also contains a separate proprietary diagnostic-authorization state machine used by diagnostic/manufacturing handlers. It is not the anti-theft state:

| State | Storage and exact evidence |
| --- | --- |
| proprietary authorization | `GP-0x7B38`, RAM `0x03FF75D4`; getter VA/file `0x54228/0x44228` |
| finite authorization allowance | persistent slot `0x11A`; shadow `GP-0x7B34`, RAM `0x03FF75D8` |
| anti-theft state | `GP-0x229A`, RAM `0x03FFCE72`; read/written by PIN-decision/publisher path |
| anti-theft comparator | separate `GP-0x2298` value; contents intentionally omitted |

The authorization getter has exactly 12 direct callsites: VAs `0x6C394`, `0x6C5CA`, `0x6C612`, `0x6D202`, `0x6D430`, `0x6D4AC`, `0x6D592`, `0x6D73C`, `0x6D7D6`, `0x6D8FE`, `0x6D9B6`, and `0x70FCE`. Every callsite is an authorization read in a diagnostic-handler surface; there are no getter function-pointer references.

The allowance mutator VA/file `0x54180/0x44180` has exactly two direct callers and no indirect references. The setter at `0x53BBC/0x43BBC` is reachable only after request validation and an existing state-4 check at `0x53B92..0x53BA0`; the other caller at `0x5136E/0x4136E` only decrements an allowance after a sustained network-received raw ignition `start`-state event. No unauthenticated allowance provisioner appears in this image.

One manufacturing/write handler at VA/file `0x6C388/0x5C388` directly joins the domains in only one direction. It calls the authorization getter at `0x6C394`, requires state 4 at `0x6C39A..0x6C39C`, validates a replacement, persists it through the helper call at `0x6C42C`, and copies it into the live anti-theft comparator at `0x6C446..0x6C452`. Anti-theft initialization at `0x2524C` loads the same persistent field through the helper call at `0x252E4`.

This proves:

```text
proprietary diagnostic authorization state 4
  -> permits factory anti-theft comparator provisioning
```

The reverse edge is absent. PIN decision `0x25658`, its equality branch `0x256AE..0x256C2`, and publisher `0x2AD6C` have zero references to `GP-0x7B38`, `GP-0x7B34`, getter `0x54228`, or mutator `0x54180`. They neither create state 4 nor replenish the allowance. The HBC/HMI success callback only reaches `xletsReturnToNew`; it contains no service flag, development marker, developer-ID, or developer-token edge.

Within the exhaustive direct GP/address xref inventory, direct-call inventory, exact persistent-slot inventory, and recovered HBC method/literal census:

```text
PIN success -/-> proprietary authorization state 4
PIN success -/-> persistent allowance slot 0x11A
PIN success -/-> serviceMenu or service-certificate authorization
PIN success -/-> AMS_DEVELOPMENT
PIN success -/-> developerId or xlet.developerToken
```

The full diagnostic-state and allowance evidence is recorded in `reports/service_certificate_diagnostic_transport.md`.

## Asynchronous result path

`AntiTheft::connected`, code offset `0x2ABFE0`, debug lines 113-124, subscribes to `antiTheftState`, `antiTheftLockTime`, `battConnect`, and related signals after dispatching readiness.

`AntiTheft::MessageHandler`, code offset `0x2AC0C4`, parses `antiTheftState.value` at `0x2AC0EA` through `0x2AC110` and stores it at `0x2AC114` through `0x2AC116`. Its state branches are:

| State branch | Exact bytecode evidence | Event behavior |
| --- | --- | --- |
| `locked` | `0x2AC11C` through `0x2AC137` | dispatches the locked event |
| `waitForVIN` | `0x2AC142` through `0x2AC15D` | dispatches the wait-for-VIN event |
| `enterPIN` | `0x2AC168` through `0x2AC18C` | dispatches enter-PIN and sets `m_EnterPin=true` |
| `unlocked` | `0x2AC193` through `0x2AC1B1` | dispatches unlocked |
| `wrongPIN` | `0x2AC214` through `0x2AC22F` | dispatches wrong-PIN |
| forced FOTA state | begins `0x2AC23A` | dispatches the forced-update branch |

`AntiTheftStates::<cinit>`, code offset `0x2F9CE8`, establishes the exact string values `waitForVIN`, `enterPIN`, `wrongPIN`, `unlocked`, `locked`, and the forced-FOTA value.

`peripheral::AntiTheftManager::<iinit>`, code offset `0x2C08C7`, debug lines 21-26, wires the AntiTheft state events to `onWait`, `onEnter`, `onWrong`, `onUnlocked`, and `onLocked`. Those callbacks converge on `showAntiTheftScreen`, code offset `0x2C0A4A`:

- wait-for-VIN selects `PopupAntiTheft`;
- enter-PIN selects `PopupAntiTheftKeypad`;
- wrong-PIN selects the bad-code `PopupAntiTheft` presentation;
- unlocked, at `0x2C0B43` through `0x2C0B8D` and debug lines 83-87, removes the after-navigation listener and dequeues both anti-theft popups;
- locked selects the status popup and requests lock-time state.

`PopupAntiTheft::initScreen`, code offset `0x2942`, chooses wrong-code/locked messaging and lock-time presentation. Its related handlers are `addListeners` at `0x2845`, `onRefresh` at `0x2A69`, `onOkButtonClick` at `0x2A9C`, and `onLockTime` at `0x2B60`.

## Post-unlock AppManager command

In AntiTheft::MessageHandler, the unlocked branch performs an additional conditional at 0x2AC1B8 through 0x2AC202: if m_EnterPin is true and the product variant is VP2, VP3, or VP4, it clears the flag and calls AppManager.getInstance().xletReturnToNew() at 0x2AC202 through 0x2AC209.

AppManager::xletReturnToNew, code offset 0x2A9A76, debug lines 1008-1013, passes command name xletsReturnToNew and an empty payload to sendAppMgrCommand. AppManager::sendAppMgrCommand, code offset 0x2A9AAB, debug lines 1015-1020, serializes a Type=Command, Dest=AppManager packet and sends it on the shared client.

CONFIRMED receiver effect: native appManager parseRequest compares xletsReturnToNew at file offset 0x5C460 (VA 0x15C460); the equal branch reaches handler 0x12AA7C through the call at file offset 0x5C4A8. The handler obtains writable media, removes shared RMS records/files, RMS folders, Xlet installation folders, and /fs/mmc1/resource contents. Helper 0x12A95C restores pre-installed Xlets, removes the AMS temporary folder, and calls reset helper 0x12A890, which invokes requestReset. Diagnostic strings anchoring those actions are at file offsets 0x101D04, 0x101D5C, 0x101DA8, 0x101DDC, 0x101E24, 0x101E7C, 0x101EC8, and 0x101F1C.

xletsReturnToNew is therefore a broad, destructive factory-app reset followed by a head-unit reset. It does not access AMS_DEVELOPMENT and must not be invoked during read-only research.

## Evidence-graded flow

| Edge | Grade and exact basis | Boundary or alternative |
| --- | --- | --- |
| Done button --[CONFIRMED]--> PopupAntiTheftKeypad::onDone | keypad code 0x5892, debug lines 114-117 | no synchronous result is consumed |
| checkAntiTheftPin --[CONFIRMED]--> AntiTheft-destination JSON command | MainSupplement.swf 0x2AC4E7; construction/send 0x2AC4FA-0x2AC513 | none for packet creation |
| shared span client --[HIGH]--> local 127.0.0.1:4400 ModuleLink endpoint | ModuleLink.xml lines 1-4 and shared span connection | runtime overrides were not excluded |
| Dest=AntiTheft --[CONFIRMED]--> com.harman.service.onOff | hmiGateway file offsets 0x7BE0, 0x8E18, 0x9E3C, and 0x9E4C | none for the local route |
| checkAntiTheftPIN --[CONFIRMED]--> IPC channel 2 message 0xE0 plus four input bytes | onoff/main.lua function 28, lines 1116-1126 | no Linux-side comparison or synchronous Boolean |
| IOC response --[CONFIRMED]--> anti-theft state/counter/lock-time fields | onoff/main.lua function 23, lines 687-1055 | policy is IOC-controlled |
| submitted PIN --[CONFIRMED]--> IOC comparison and later state publication | decision VA/file `0x25658/0x15658`; equality branch `0x256AE..0x256C2`; publisher `0x2AD6C/0x1AD6C` | comparator contents and retry/lockout policy intentionally unresolved |
| incoming antiTheftState --[CONFIRMED]--> HMI event dispatch | MainSupplement.swf 0x2AC0EA-0x2AC22F | none for HMI dispatch |
| state event --[CONFIRMED]--> AntiTheftManager popup update | listener wiring at 0x2C08C7; selector at 0x2C0A4A | none for HMI UI selection |
| entered-PIN plus supported product plus unlocked --[CONFIRMED]--> xletsReturnToNew request | 0x2AC1B8-0x2AC209 | prior enterPIN and product conditions both matter |
| xletsReturnToNew request --[CONFIRMED]--> factory-app-state wipe, preload restore, and head-unit reset | appManager parser 0x5C460 and handlers 0x12AA7C, 0x12A95C, 0x12A890 | destructive; not Java state NEW |
| diagnostic state 4 --[CONFIRMED ONE-WAY]--> permission to provision anti-theft comparator | handler `0x6C388` requires getter state 4, persists and copies the comparator at `0x6C42C/0x6C446..0x6C452` | this is provisioning authority, not PIN authentication |
| PIN success --[CONFIRMED BOUNDED ABSENCE]--> state 4, allowance, serviceMenu, developer token, or marker | exhaustive direct state/getter/mutator xrefs plus HBC callback census contain no reverse edge | cannot exclude an unrecovered/dynamic component, but none has affirmative evidence |
| PIN success --[CONFIRMED INDIRECT]--> later ordinary boot after xletsReturnToNew reset | native receiver invokes requestReset | reset does not itself prove a marker transition |

## Failure behavior and safety boundary

The HMI clearly distinguishes wrongPIN, locked, and lock-time feedback. The recovered onOff service exposes the returned retry counter and lock time, but the IOC computes them. Retry limits, PIN provenance, comparator content, lockout timing policy, VIN coupling, and any recovery credential remain unknown and outside this project's developer-authorization needs.

The former negative native-search result is superseded twice: hidden-HBC evidence identifies hmiGateway/onOff as proxy and receiver, while static `cmcioc.bin` analysis locates the comparison/success path and proves separation from proprietary diagnostic authorization. No brute-force, guessing, bypass work, request construction, or target execution was performed.

## Reproducible read-only operations

- In-memory CWS inflation with Node zlib, SWF tag walking, DoABC extraction, AVM2 constant-pool parsing, method-body disassembly, and debug-line recovery.
- Exact-name and operand scans around the named classes and methods rather than printable-string proximity alone.
- Node `fs` reads, SHA-256 hashing, and a bounded recursive scan of extracted RA4 files.
- Direct text read of `ModuleLink.xml` with line numbering.
- Static V850 decode of `cmcioc.bin` with Python 3.12.14 and pypcode 4.0.0 (`V850:LE:32:default`), exhaustive direct-call/GP/persistent-slot xrefs, and table-driven receive-destination tracing.

## Unresolved gaps

1. The protected source/authorized provisioning process for the anti-theft comparator, retry threshold/progression, lockout-duration policy, and any VIN coupling.
2. The exact source ECU/bus, vendor message/signal name, product-variant meaning, and scheduler timebase behind the now-confirmed network-received raw ignition-state field that consumes the finite diagnostic allowance.
3. The legitimate OEM authority/process that first establishes proprietary state 4 and replenishes its finite allowance; successful owner PIN use is proved not to do so.
4. `xletsReturnToNew` is understood, but exact reset sequencing after `requestReset` remains a platform-wide boot concern rather than an authentication decision.
