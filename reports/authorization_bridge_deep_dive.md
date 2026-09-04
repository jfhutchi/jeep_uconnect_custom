# RA4 18.45.01 authorization bridge deep dive

## Scope and bottom line

This report addresses the previously open authorization-bridge questions using the hidden QNX IFS payloads inside the stock RA4 18.45.01 ifs-cmc.bin and the recovered RA4 HMI bytecode. All work was static and read-only. No vendor executable, script, JAR, installer, or update payload was run.

The evidence does not support a single flow of engineering gesture -> anti-theft PIN -> development marker. It supports three distinct controls:

1. A five-second hard-key state machine emits the HMI event 'engineerMode'. It is not gated by the anti-theft state.
2. The Service item inside the engineering menu is gated by 'get_service_flags.eng_menu', which is derived from a verified, head-unit-bound, expiring service certificate.
3. The anti-theft keypad is proxied to the onOff service and then to an external IOC over IPC channel 2. The IOC returns state, counter, and lock-time information. On the relevant product variants, a successful transition after PIN entry invokes the broad AppManager factory-app reset 'xletsReturnToNew'.

Neither the service-certificate path nor the anti-theft path creates or deletes /fs/etfs/AMS_DEVELOPMENT in the recovered code. The marker writer remains the engineering service-menu ActionScript method documented in developer_mode_ui.md.

## Evidence grades

- CONFIRMED: direct control flow, data flow, file operation, or IPC operation is present in the artifact.
- HIGH: multiple direct artifacts establish the boundary, but one implementation endpoint is outside the recovered CPU/domain.
- INFERRED: a semantic interpretation is strongly suggested by names or surrounding behavior but is not itself a direct operation.
- UNKNOWN: the recovered evidence does not establish the claim.

## Container and artifact provenance

The parent image is:

- analysis_ra4_18.45.01/work/primary_iso/usr/share/IFS/ifs-cmc.bin
- size 42,122,670 bytes
- SHA-256 ea6797be141763f35f3059ad858eefbf54f730af0155bebc7af411c47d80ba92

The ignored extraction root is analysis_ra4_18.45.01/work/hidden_hbc_ifs. It exists only as a local research work product and is not tracked.

| Decompressed image | Size | Entries | SHA-256 |
| --- | ---: | ---: | --- |
| HBCIFS at parent offset 0x001A0000 | 30,909,752 | 513 | 996c5a52cf7e72bb73d95e34e684196ca702061c6c5d9977415b014fbea57fbb |
| HBCIFS at parent offset 0x00F20000 | 23,083,796 | 261 | 57feaf9cfde58172f8a94049227ec895eb2f88607466297e31f8732f201b8512 |
| HBCIFS at parent offset 0x019A0000 | 35,478,140 | 141 | aae02c6ea6873e66cde49e814299d43cbeb38e686352fd86324ac91a1feafc42 |

The HBCIFS compression byte is 0x88. Static analysis of memifs2 showed that bit 0x80 selects a QNX two-byte big-endian length-framed decompressor and low type 8 selects the corresponding decompression routine. The materialized inventories contain 778 regular files totaling 89,007,481 bytes (433/30,769,956; 219/22,931,139; 126/35,306,386 by segment). An exact scan of all 778 files, including the one zero-length file segment_001a0000/files/etc/openssl/openssl.cnf, found zero AMS_DEVELOPMENT literals.

## 1. Physical producer of engineerMode

### CAN/IPC ingress

CONFIRMED: analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/vehicle/keys.lua is a Lua 5.1 chunk, 31,553 bytes, HBC image offset 0x1C47A1B, SHA-256 620809fd91f2ddd3d48d874db62ab6afd11a3501e2a5a2d4812922cfa4d40040.

- Function 18, source/debug lines 579-619, requires vehicle.icsHardKeys at line 583 and initializes it at line 590.
- The same function opens the IOC control channel through ipc.open(can_utils.ctrlChan) at lines 609-610 and binds processMessage. It opens the separate front-key IPC channel 25 at lines 612-613 and binds FtKeyMessage.
- Function 16, processMessage, lines 531-551, decodes ICSKEYS_BUTTON_MATRIX and calls icshkeys.processKnob at lines 534-537. It handles the alternate ICS matrix similarly at lines 539-542.
- Function 17, FtKeyMessage, lines 553-575, decodes the front-key channel and also calls icshkeys.processKnob.

The getAntiTheftStatus check in keys.lua function 16 is confined to the steering-wheel-control branch at lines 545-547. It does not wrap the ICS matrix branches.

### Five-second hard-key state machine

CONFIRMED: analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/vehicle/icsHardKeys.lua is a Lua 5.1 chunk, 31,153 bytes, HBC image offset 0x1C4F55C, SHA-256 86aba0d0c5fbfdeb9d5da36edd66c81e3e76cf16744740d9778612f41a7a1ea5.

- Function 9, source/debug lines 146-166, maps the driver-temperature events to ICS_btn_26 and ICS_btn_27.
- Function 32, lines 652-665, handles ICS_btn_26. A press stores state "1", stops and starts ModeTimer5s with the numeric duration 5000, and emits drvTempUp pressed=true. The timer calls occupy bytecode PCs 13-19.
- Function 33, lines 670-683, performs the same operations for ICS_btn_27 and emits drvTempDn.
- Function 11, ModeTimerfunc5s, lines 237-279, tests both saved button states at lines 265-267 and emits {key="engineerMode", pressed=true}. The exact emission is bytecode PCs 140-145.
- Function 40, processICS, lines 791-805, iterates every hard-key handler. It contains no anti-theft check.
- Function 41, processKnob, lines 810-813, directly invokes processICS.
- Function 48, init, lines 854-905, registers com.harman.service.ICS, creates the timer objects, and subscribes the emitted key and knob signals.

CONFIRMED separation: icsHardKeys.lua does track anti-theft state, but it does not gate engineerMode. Function 5, onAntiTheftStateChange, lines 84-90, updates antiTheftStateUnlocked. Only function 15, the volume-knob handler at lines 316-374, and function 17, the audio-power handler at lines 437-452, capture that variable and return early while it is false. The driver-temperature handlers, processICS, and ModeTimerfunc5s do not capture or test it.

The HMI endpoint remains MainSupplement.swf, ICS::messageHandler at reconstructed FWS code offset 0x2A728C. It checks key.pressed, compares key.key with engineerMode at 0x2A73EA-0x2A73F7, and dispatches ICSEvent.ENGINEERING_MODE at 0x2A73FB-0x2A7409.

Result: driver temperature up plus driver temperature down held through the 5,000 ms timer is a CONFIRMED physical producer of engineerMode. The compiled script contains other product-dependent multi-key branches, but they are not needed to establish this RA4 entry route.

## 2. Producer and meaning of serviceMenu

### HMI request and response

CONFIRMED: MainSupplement.swf VersionInfo::<cinit>, method 8165 at reconstructed offset 0x2D3211, assigns its platform D-Bus identifier. VersionInfo::requestServiceFlags, method 8185 at 0x2D35B6, sends a platform command whose packet is get_service_flags at PCs 0x0C-0x1E.

VersionInfo::platformMessageHandler, method 8192 at 0x2D3745, reads get_service_flags.eng_menu at absolute offsets 0x2D3A64-0x2D3A6E, stores that value as mServiceMenu, and dispatches ServiceEvent.SERVICE through 0x2D3A8C. There is no PIN-state transform in that method.

### Platform service-certificate producer

CONFIRMED: analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/platform_troubleshoot.lua is a Lua 5.1 chunk, 13,931 bytes, HBC image offset 0x1CE07C2, SHA-256 8beab38ab164479a9fd815116dbfa02a48e3fa661724fa9c4273dc5884a1ba45.

- Root source/debug lines 29-45 initialize service_flags.valid=false and service_flags.eng_menu=false.
- Function 1, lines 54-56, returns service_flags.
- Function 15, init, lines 465-490, registers the platform method get_service_flags and the service-file evaluation methods.
- Function 11, notifyOnService, lines 406-427, registers the SERVICEKEY media event.
- Nested function 12, lines 408-422, copies service.cert from the mounted media location to /etc/security/service.cert and calls processservice_cert_file(true).
- Function 7, lines 255-304, invokes the stock verifier /fs/mmc0/app/security/scv using the service certificate and /etc/keys/serv_cert_key.pem. It requires a zero return, reads the head-unit serial from /fs/fram/serialnumber, requires equality with the parsed HUSerialNumber, validates the certificate fields/expiry, then sets service_flags.valid=true and emits the service flags at lines 281-290.
- Function 2, lines 63-127, parses certificate fields. EngineeringMenu numeric value 1 becomes Boolean true and is stored in service_flags.eng_menu at lines 82-90.
- Function 6, lines 214-248, checks ignition-cycle and date expiry. Function 5, lines 188-205, clears all flags and deletes the service file on invalidation.

The init function also observes com.harman.service.authenticationService ownership at lines 480-483, causing service-certificate evaluation when that service becomes available. This is not evidence that authenticationService handles the anti-theft PIN.

### Diagnostic service-certificate transport

CONFIRMED: `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/usr/bin/cmc/service/diagserv.lua` is a 282,802-byte Lua 5.1 chunk with SHA-256 `777d96dfa3461caa6ebf4765784f9ba2f4d766fd1ddfe54590a655121353bd64`. It owns a second ingress and a removal path for the same fixed `/etc/security/service.cert` file:

- Root PCs 2300-2305 (`0x2469-0x247D`, line 7683) open IPC channel 7; PCs 2313-2317 (`0x249D-0x24AD`, line 7689) attach `onIpcMessage` prototype 298 (`0x3FC23-0x3FCD7`, lines 7562-7569).
- `msgHandler[49]` reaches routine dispatcher prototype 268 (`0x3A79A-0x3A88C`, lines 6876-6886), which constructs the 16-bit routine ID and invokes its registered handler.
- Routine `0xF010`, prototype 254 (`0x34D52-0x354C8`, lines 6249-6307), stages the fixed certificate path. Its finalize branch calls captured `validateServiceKey` at PCs 71-72 (`0x34E82-0x34E86`); validator prototype 1 (`0x4206-0x4567`, lines 325-342) invokes `com.harman.service.platform.evaluate_service_file` and accepts only a returned table with `valid=true`.
- Routine `0xF011`, prototype 255 (`0x354C8-0x35804`, lines 6312-6333), removes the fixed path and reports success only after a separate absence test. It does not call the evaluator, clear already-published `service_flags`, or notify the HMI, so immediate live revocation is unproved. It is distinct from HMI item 20, which deletes `/fs/etfs/service.key` and makes no IPC call.

The transport cannot itself create service authorization. `platform_troubleshoot.lua` prototype 14 (`0x2C39-0x2DD8`, lines 446-457) calls `processservice_cert_file(true)`, which still requires stock-verifier success, exact HU-serial equality, and valid date/ignition limits before setting `service_flags.valid` and `eng_menu`.

The diagnostic write is also non-atomic: first-segment mode truncates the active path with `w+b`; continuation uses `rb+` and seeks to the end; there is no temporary file, rename, backup, fsync, or checked mount result. Open failure only logs, and the same internal acknowledgment tuple is emitted after open success and failure at PCs 58-66 (`0x34E4E-0x34E6E`). A staging acknowledgment is therefore not proof of a complete, persistent, or valid certificate.

No explicit diagnostic-session, authentication, or SecurityAccess predicate appears in the four traced Lua prototypes or the static diagserv handler table. This is a bounded local result, not proof of unauthenticated external reachability. `dev-ipc` identifies IOC traffic, so an upstream vehicle gateway, IOC diagnostic stack, or factory tester may enforce the missing authorization before channel 7. The external route, address, framing, required session/security state, certificate issuer, and private signing process remain unknown.

The boot image launches authenticationService at standard_boot/files/bin/boot.sh lines 648-649 with /etc/system/config/authenticationServiceKeyFile.json. The config file is 11,359 bytes with SHA-256 5968ff07dba7a0316a7fc76687cbef5147699d96538d14a10def0bfd5211ad11; no key material is reproduced here. The service binary is segment_019a0000/files/usr/bin/authenticationService, 273,340 bytes, HBC image offset 0x28000, SHA-256 9c7c057fbffceb2dc0b77690b6eb07dcd90721de6f89c5a05150fa18cea84699. Its service/crypto vocabulary does not include checkAntiTheftPIN or the anti-theft state terms.

Result: serviceMenu=true is a CONFIRMED valid-service-certificate authorization, bound to the head-unit serial and constrained by expiry. It is not the factory anti-theft PIN result.

### `Delete Service Key` item 20

CONFIRMED: the engineering service menu's apparent rollback item does not send a backend command. In the ROV `AppsListScreen.swf` (117,093-byte CWS, SHA-256 `5bc1630f567c82494ab86e73c308ad2a8b9d341494a5f5de5f66a1505f1416e5`; 282,644-byte reconstructed FWS, DoABC `0x3728`):

- `AppsListEngServiceMenu::<cinit>` assigns `DELETE_SERVICE_KEY=20` at FWS offsets `0x36C77-0x36C7C`.
- The constructor unconditionally pushes visible label `Delete Service Key` at debug line 154, `0x370C4-0x370D6`.
- `AppsListEngServiceMenu::onItem` compares that constant and maps it to lookup-switch case 20 at debug line 498, `0x37EF7-0x37F01`; case 20 targets `0x37D11`.
- The case constructs `flash.filesystem.File("file:///fs/etfs/service.key")` at `0x37D17-0x37D24`, tests `.exists` at `0x37D3E-0x37D45`, and calls `.deleteFile()` directly at `0x37D59-0x37D61` when present. The absent branch only emits a trace at `0x37D65-0x37D6E`. No `Peripheral`, ModuleLink, D-Bus, or platform-service call occurs anywhere in the case block (`0x37D11-0x37D75`).

CONFIRMED negative boundary: `platform_troubleshoot.lua` does not register a corresponding delete/remove method. Its init function 15 registers exactly `get_service_flags`, `test_service_flag`, and `evaluate_service_file` at source/debug lines 469-471 (bytecode PCs 5-19). Function 5, `delete_service_file`, lines 188-205, is an internal upvalue: bytecode PCs 23-44 make `/fs/mmc0` writable, remove the configured `service_cert_file`, and remount it read-only. Functions 6 and 7 invoke it when certificate evaluation proves invalid, expired, serial-mismatched, or verifier-failed; function 14 (`evaluate_service_file`, lines 446-457) can enter that evaluation path, but item 20 never invokes function 14.

The configured backend path is `/etc/security/service.cert`. The recovered standard-boot inventory line 20 maps `/etc/security` to `/fs/mmc0`, so this resolves under `/fs/mmc0`; no recovered filesystem entry aliases it to `/fs/etfs/service.key`. Thus the UI action and platform invalidation path are CONFIRMED distinct. Whether `/fs/etfs/service.key` has a separate runtime consumer, or deleting it has any later effect on `/etc/security/service.cert`, remains UNKNOWN.

### Separate AppManager embedded-engineering gate

CONFIRMED and distinct: native appManager contains a second engineering control for its embedded-application catalog. Function file offset 0x29E08 (VA 0x129E08) loads /fs/etfs/enableEngMenu at 0x29E20-0x29E24, supplies numeric mode 4 at 0x29E28, calls the file predicate at 0x29E2C, and tests its zero/nonzero result at 0x29E30. It logs Menu is enabled through the string at file offset 0x101A58 or Menu is disabled through 0x101A84 and returns true/false.

Its sole direct branch-and-link caller is file offset 0x3D1C0 (VA 0x13D1C0) inside createEmbeddedApps. That caller compares the current application ID with the engineering string at file offset 0x105C4C; a false marker result reaches the skip diagnostic at 0x105C58, while a true result reaches the embedded-app creation path. appManager.cfg line 84 lists the corresponding embedded application with appId engineering.

The complete materialized primary extraction plus all hidden-HBC regular files contains the enableEngMenu literal only in appManager; no writer was found. This AppManager catalog marker is not Peripheral.versionInfo.serviceMenu, service.cert, or AMS_DEVELOPMENT. It must not be used as evidence that any of those other controls are equivalent.

## 3. checkAntiTheftPIN receiver and decision boundary

### ModuleLink destination bridge

CONFIRMED: analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/bin/hmiGateway is 153,124 bytes, HBC image offset 0x43A000, SHA-256 8d7fe8789bb012a66fbebd1bd44eefa506c672a5d70c90fbf92b3a5a6f01ec82.

- Its destination resolver at file offset 0x7BE0, VA 0x107BE0, compares the destination literal AntiTheft and selects the associated handler.
- Its request-proxy dispatch at file offset 0x8E18, VA 0x108E18, compares AntiTheft.
- The equal branch reaches file offset 0x9E3C, VA 0x109E3C, where the literal com.harman.service.onOff is loaded, and file offset 0x9E4C, VA 0x109E4C, where /com/harman/service/onOff is loaded.

This proves the local route from ModuleLink Dest=AntiTheft to the onOff D-Bus service.

### Linux/QNX marshalling endpoint

CONFIRMED: analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/onoff/main.lua is a Lua 5.1 chunk, 66,272 bytes, HBC image offset 0x1B5CE58, SHA-256 41c0f3f2709c49d4a4f9b150b8c08c735515a9c50bbfbc2e4c36664d6466e698.

- Its method table registers checkAntiTheftPIN to function 28.
- Root initialization assigns AntiTheftPinMsg the numeric value 224 (0xE0).
- Function 28, source/debug lines 1116-1126, creates a five-byte message, writes byte 1 as 0xE0, writes the four supplied input bytes into bytes 2-5, calls chan2.write(msg), and returns an empty table immediately. It performs no local comparison and returns no synchronous authentication Boolean.
- Root startup opens IPC channel 2 at source/debug line 1596 and registers onIpcCh2Message.
- Function 23, onIpcCh2Message, lines 687-1055, decodes byte 7 as raw antiTheftState, byte 8 as antiTheftCounter, and byte 10 as antiTheftLockTime after checking the channel interface version.
- The same function maps raw state 0 to locked at lines 921-923, raw state 1 to waitForVIN at lines 927-928, raw state 2 with counter zero to enterPIN at lines 932-934, raw state 2 with a nonzero counter to wrongPIN at lines 933-940, raw state 3 to unlocked at lines 944-947, and raw state 5 to forcedFotaUpdate at lines 952-953.

HIGH boundary conclusion: the external IOC behind IPC channel 2 is the recovered decision boundary. Linux/QNX marshals the four input bytes and later receives state, retry-counter, and lock-time fields. The correct-PIN source, comparison routine, retry threshold/progression, and lockout-duration policy are UNKNOWN because their implementation is not in onoff/main.lua, hmiGateway, or the HMI.

No PIN value, comparison material, bypass procedure, or brute-force logic was derived or reproduced.

## 4. AppManager xletsReturnToNew receiver and effect

CONFIRMED: analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/bin/appManager is 1,268,061 bytes, HBC image offset 0xCF000, SHA-256 608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591.

- Native parseRequest compares xletsReturnToNew at file offset 0x5C460, VA 0x15C460. The equal branch at 0x5C46C reaches a call to the handler at file offset 0x2AA7C, VA 0x12AA7C, through the branch-and-link at file offset 0x5C4A8.
- xletsReset is a separate parser branch and handler; the two commands must not be conflated.
- Handler 0x12AA7C requests writable media, removes shared record-store files, removes record-store folders, removes Xlet installation folders, and removes /fs/mmc1/resource contents. Its exact diagnostic strings are stored at file offsets 0x101DDC, 0x101E24, 0x101E7C, 0x101EC8, and 0x101F1C.
- It calls helper 0x12A95C. That helper restores pre-installed Xlets using a cp -cpR command, removes the AMS temporary folder, and requests a head-unit reset. Its diagnostic strings are at file offsets 0x101D04, 0x101D5C, and 0x101DA8.
- Reset helper 0x12A890 logs a head-unit reset warning and invokes requestReset.

The associated configuration file is segment_00f20000/files/etc/system/config/appManager.cfg, 5,802 bytes, SHA-256 ab9ed180574d2c9f83c45217f05b132af24abd364ecf59c8447d1ba0cdb9c2d7. Lines 8-10 define /fs/mmc1/kona/preload, /fs/mmc1/xletsdir, and /fs/etfs/usr/var/appman/xletRMS respectively.

Result: xletsReturnToNew is a CONFIRMED broad, destructive factory-app-state restoration followed by a head-unit reset. It is not a Java lifecycle transition to state NEW, is not an AMS_DEVELOPMENT toggle, and is not a developer-token operation. It must not be invoked during read-only research.

## 5. AMS restart/reload behavior

CONFIRMED: analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/platform_ams_restart.lua is a Lua 5.1 chunk, 7,514 bytes, HBC image offset 0x1D1E7C8, SHA-256 264e5aaa6e2e09e8bb86a881f4919a66220d1cad2c7ce9443416e5d35f9f720f. Standard boot.sh line 747 launches it.

- Function 10, init, lines 237-250, creates/starts a 120,000 ms timer, subscribes to owner changes for com.aicas.xlet.manager.AMS, and checks whether the service already has an owner.
- Function 9, onOwnerChanged, lines 218-234, tracks whether AMS has appeared or disappeared and calls restartAMS on those transitions.
- Function 7, restartAMS, lines 183-209, handles two cases. If AMS never appears before the timer expires, it terminates AMS and executes /fs/mmc0/app/bin/jvm.sh. If AMS appeared and then disappeared, it terminates AMS and appManager, restarts appManager, waits for it, then executes jvm.sh.
- The restarted appManager command includes -d only when /fs/etfs/disableDRM exists. This pathname is distinct from /fs/etfs/AMS_DEVELOPMENT.

The script contains no AMS_DEVELOPMENT string, file test, subscription, or inotify-style watch. The complete hidden-HBC payload scan likewise found zero AMS_DEVELOPMENT literals.

At initial boot, standard_boot/files/bin/boot.sh lines 367/371 and 461/465 assign disableDRMArg=-d and pass it to appManager unconditionally. This is a separate AppManager/DRM command-line control. It must not be conflated with the marker-driven AMS security.jar selection in primary_iso/usr/share/MMC_IFS_EXTENSION/bin/jvm.sh lines 58-63.

Result:

- CONFIRMED: AMS service loss or startup timeout can cause platform_ams_restart.lua to reinvoke jvm.sh, at which point jvm.sh re-samples AMS_DEVELOPMENT.
- CONFIRMED: xletsReturnToNew requests a full head-unit reset, which later reaches ordinary boot/AMS startup.
- UNKNOWN/negative bound: no component recovered so far watches AMS_DEVELOPMENT itself or immediately reloads policy when only that file changes.

## Separation matrix

| Proposed edge | Grade | Evidence-backed result |
| --- | --- | --- |
| driver temp up + down held 5 s -> engineerMode | CONFIRMED | icsHardKeys.lua functions 32, 33, and 11 |
| anti-theft unlocked state -> permission to emit engineerMode | CONFIRMED ABSENT in traced path | antiTheftStateUnlocked is used only by volume and audio-power handlers |
| service.cert valid, HU serial matches, not expired, EngineeringMenu=1 -> serviceMenu=true | CONFIRMED | platform_troubleshoot.lua functions 2, 6, 7, 11, 12, and 15 |
| diagserv internal `0xF010` finalize -> platform `evaluate_service_file` | CONFIRMED | prototypes 254 and 1; files `0x34E82-0x34E86` and `0x421A-0x4242` |
| diagserv staging acknowledgment -> durable/valid certificate | CONFIRMED NOT EQUIVALENT | open failure reaches the same tuple; platform validation is a separate finalize step |
| diagserv internal `0xF011` -> `/etc/security/service.cert` removal | CONFIRMED | prototype 255 files `0x354F8-0x35524`; upstream diagnostic gate unknown |
| engineering item 20 -> `/fs/etfs/service.key` deletion | CONFIRMED | AppsListEngServiceMenu::onItem `0x37D11-0x37D75` directly uses `File.deleteFile()` |
| engineering item 20 -> platform removal IPC or `/etc/security/service.cert` deletion | CONFIRMED ABSENT in traced block | item 20 makes no backend call; platform registers no delete/remove method and uses a different path |
| /fs/etfs/enableEngMenu readable -> AppManager embedded engineering app retained | CONFIRMED | appManager function 0x129E08 and createEmbeddedApps caller 0x13D1C0 |
| enableEngMenu -> serviceMenu or AMS_DEVELOPMENT | CONFIRMED SEPARATE | different pathnames, consumers, and effects; no joining call |
| anti-theft PIN success -> serviceMenu=true | UNKNOWN; no direct edge | different producer, state, and credentials |
| checkAntiTheftPIN -> local comparison in HMI/onOff | CONFIRMED ABSENT | HMI is asynchronous; onOff writes IPC channel 2 and returns immediately |
| IOC response -> wrongPIN/unlocked/lock-time state | CONFIRMED | onoff/main.lua function 23 |
| entered-PIN unlock on VP4 -> xletsReturnToNew request | CONFIRMED | MainSupplement.swf AntiTheft::MessageHandler |
| xletsReturnToNew -> Xlet/RMS/resource wipe, preload restore, HU reset | CONFIRMED | appManager parser and handlers above |
| xletsReturnToNew -> AMS_DEVELOPMENT change | CONFIRMED ABSENT in receiver | no marker operation in the traced handler |
| AMS_DEVELOPMENT change -> immediate watcher/reload | UNKNOWN with strong negative bound | no marker literal in the 89,007,481-byte hidden regular-file inventory; writer itself sends no notification |
| subsequent jvm.sh execution -> current marker re-sampled | CONFIRMED | jvm.sh lines 58-63 |

## Safe design implications

1. Preserve the service-certificate gate when exposing or using the engineering Service menu; it is the recovered factory authorization control for that menu.
2. Do not treat the internal diagserv routine as a self-service provisioning or revocation API. Use would require a proved, authorized external factory route and must account for its non-atomic active-file staging.
3. Do not treat the vehicle anti-theft PIN as a developer credential. Its recovered purpose and endpoint are the anti-theft IOC state machine.
4. Do not invoke xletsReturnToNew as a development-mode activation mechanism. It deletes application state and resets the head unit.
5. Do not assume touching AMS_DEVELOPMENT changes the running AMS. A safe design must use a controlled, reversible restart boundary and verify the selected policy after restart.
6. Do not treat `Delete Service Key` as a proved revocation of the active service certificate. It deletes `/fs/etfs/service.key`; the verified platform path is `/etc/security/service.cert` and no joining call was recovered.
7. Keep AppManager -d and /fs/etfs/disableDRM separate from AMS_DEVELOPMENT and development/security.jar. They are independent controls in the recovered boot/restart scripts.

## Reproducible static method

- QNX boot-image and imagefs parsing, including static reconstruction of the HBCIFS type-8 length-framed decompression scheme.
- Lua 5.1 chunk parsing with constant, prototype, local-variable, source/debug-line, and instruction decoding.
- ARM ELF section/segment mapping, literal-table cross-references, and bounded static instruction analysis for hmiGateway and appManager.
- In-memory CWS inflation, SWF tag/DoABC parsing, and AVM2 method-body disassembly.
- Exact byte scans and SHA-256 hashing with no target execution.

## Remaining unknowns

1. The IOC implementation containing the correct-PIN source, comparison routine, retry threshold/progression, and lockout-duration policy.
2. The issuing authority and operational process for a valid RA4 service certificate, plus the external diagnostic route, framing, session, and SecurityAccess requirements upstream of diagserv IPC channel 7; no attempt was made to forge, inject, or bypass one.
3. Any marker watcher outside the standard IFS, all three hidden HBCIFS payloads, and primary MMC extension already searched.
4. The safest supported process-control entry point for an owner-authorized, reversible AMS restart after a marker transition.
5. The separate AMS developer-token/trust chain; none of the evidence here joins it to anti-theft authentication.
6. The producer of /fs/etfs/enableEngMenu; the current primary-plus-hidden corpus contains only the AppManager reader.
7. The runtime consumer, if any, of `/fs/etfs/service.key` and any relationship between that file and `/etc/security/service.cert`.
