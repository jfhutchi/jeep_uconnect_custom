# RA4 18.45.01 engineering/development-security UI

## Scope and result

The stock RA4 ROV HMI does not expose a recovered literal label Developer Mode. The physical entry is now proved: the ICS hard-key service synthesizes engineerMode when driver temperature up and driver temperature down remain pressed through a 5,000 ms timer. MainSupplement.swf receives that event and opens the Apps List engineering menu.

Within that menu, the Service item is conditional on Peripheral.versionInfo.serviceMenu. That flag is now traced to platform get_service_flags.eng_menu and a cryptographically verified, head-unit-serial-bound, expiring service certificate whose EngineeringMenu field equals 1. A separate factory-oriented diagnostic bridge can stage and request validation of that same certificate, but it cannot bypass the verifier and its external diagnostic authorization gate remains unknown. The flag is not produced by the factory anti-theft PIN state machine.

The engineering service menu contains an unconditional action whose visible label alternates between Enable Development Security and Enable Production Security according to /fs/etfs/AMS_DEVELOPMENT. Selecting the action directly creates or deletes the marker. Its separate `Delete Service Key` action directly deletes `/fs/etfs/service.key` in ActionScript; it does not call the platform service-certificate evaluator or a removal IPC. The gesture, service-certificate flag producer, constructors, selection handlers, and marker toggle do not invoke checkAntiTheftPIN. No marker-specific watcher was found in all 778 hidden-HBC regular files; the marker is known to take effect when jvm.sh is next invoked.

## Artifact provenance and offset convention

SWF offsets are offsets in reconstructed, uncompressed FWS streams, not in the on-disk CWS files.

| Artifact | Exact evidence |
| --- | --- |
| Event bridge and hard-control handler | `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/MainSupplement.swf`; CWS 1,407,783 bytes; SHA-256 `e9d796ea4b4c83ed518bfe3b3c341e54e510a1ae0f78ebbffbd655b7c36a3258`; FWS 3,639,060 bytes; DoABC `0x264EB` |
| Engineering menus | `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/skins/default/swf/AppsListScreen.swf`; CWS 117,093 bytes; SHA-256 `5bc1630f567c82494ab86e73c308ad2a8b9d341494a5f5de5f66a1505f1416e5`; FWS 282,644 bytes; DoABC `0x3728` |
| ModuleLink endpoint | `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/ModuleLink.xml`, lines 1-4; `127.0.0.1:4400` |
| ICS ingress | `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/vehicle/keys.lua`; Lua 5.1; 31,553 bytes; image offset `0x1C47A1B`; SHA-256 `620809fd91f2ddd3d48d874db62ab6afd11a3501e2a5a2d4812922cfa4d40040` |
| Hard-key producer | `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/vehicle/icsHardKeys.lua`; Lua 5.1; 31,153 bytes; image offset `0x1C4F55C`; SHA-256 `86aba0d0c5fbfdeb9d5da36edd66c81e3e76cf16744740d9778612f41a7a1ea5` |
| Service-flag producer | `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/platform_troubleshoot.lua`; Lua 5.1; 13,931 bytes; image offset `0x1CE07C2`; SHA-256 `8beab38ab164479a9fd815116dbfa02a48e3fa661724fa9c4273dc5884a1ba45` |
| Diagnostic certificate bridge | `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/usr/bin/cmc/service/diagserv.lua`; Lua 5.1; 282,802 bytes; SHA-256 `777d96dfa3461caa6ebf4765784f9ba2f4d766fd1ddfe54590a655121353bd64`; routines `0xF010`/`0xF011` in prototypes 254/255 |
| AMS restart supervisor | `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/platform_ams_restart.lua`; Lua 5.1; 7,514 bytes; image offset `0x1D1E7C8`; SHA-256 `264e5aaa6e2e09e8bb86a881f4919a66220d1cad2c7ce9443416e5d35f9f720f` |
| Embedded-app catalog gate | analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/bin/appManager; 1,268,061 bytes; image offset 0xCF000; SHA-256 608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591 |

## Entry into the engineering menu

`com.nfuzion.moduleLink::ICS::messageHandler`, code offset `0x2A728C`, debug lines 125-127, compares the incoming object's `key.key` with `engineerMode` at `0x2A73EA` through `0x2A73F7`. A match dispatches `ICSEvent.ENGINEERING_MODE` at `0x2A73FB` through `0x2A7409`.

`ICSEvent::<cinit>`, code offset `0x2F1994`, assigns `ENGINEERING_MODE` the string `engineeringmode` at `0x2F1ADD` through `0x2F1AE5`.

`peripheral::HardControls::<iinit>`, code offset `0x271F4D`, debug lines 87-88, registers an `ICSEvent.ENGINEERING_MODE` listener at `0x2721BA` through `0x2721CA`.

`HardControls::onEngineeringMode`, code offset `0x272F49`, debug lines 507-517, checks whether the current extension belongs to `Extensions.ENGINEERING_MODE_EXTENSIONS` at `0x272F5D` through `0x272F76`. If not, it calls `Framework.structure.goto(Screens.APPS_LIST,{ext:Extensions.LIST_ENG_MENU})` at `0x272F7D` through `0x272F99`; if already inside an engineering extension, it calls `structure.exit()` at `0x272FA2` through `0x272FAD`.

The upstream producer is now CONFIRMED. keys.lua function 18, source/debug lines 579-619, loads and initializes vehicle.icsHardKeys, opens the IOC control channel at lines 609-610, and opens front-key IPC channel 25 at lines 612-613. Its processMessage function 16, lines 531-551, decodes ICS button matrices and calls icshkeys.processKnob.

icsHardKeys.lua function 32, lines 652-665, handles ICS_btn_26: on press it stores state 1 and restarts ModeTimer5s for 5000 ms. Function 33, lines 670-683, does the same for ICS_btn_27. Those handlers emit drvTempUp and drvTempDn respectively. Function 11, ModeTimerfunc5s, lines 237-279, tests both stored states at lines 265-267 and emits {key="engineerMode", pressed=true} at bytecode PCs 140-145.

The anti-theft state does not gate this event. Function 5, onAntiTheftStateChange, updates antiTheftStateUnlocked, but only function 15 (volume knob, lines 316-374) and function 17 (audio power, lines 437-452) capture/test that variable. Function 40, processICS, lines 791-805, iterates all hard-key handlers without an anti-theft test, and function 11 does not capture the state.

## Service-menu reachability

`AppsListEngMenuScreen::<iinit>`, code offset `0x300D7`, debug lines 108-114, reads `Peripheral.versionInfo.serviceMenu` at `0x3030C` through `0x30315`. When true it pushes `{label:"Service", id:SERVICE}` at `0x30319` through `0x30333`, then calls `requestServiceFlags()` at `0x3033B` through `0x30343`.

`AppsListEngMenuScreen::onService`, code offset `0x31240`, debug lines 429-435, can also add the Service item dynamically when that flag becomes true.

`AppsListEngMenuScreen::onItem`, code offset `0x308E3`, debug line 275, routes a selected `SERVICE` entry to `Screens.APPS_LIST` with `{ext:Extensions.LIST_ENG_SERVICE_MENU}` at `0x30B67` through `0x30B81`.

`AppsListScreen::initExtension`, code offset `0x2625B`, maps `LIST_ENG_SERVICE_MENU` to `AppsListEngServiceMenu`: the matching extension constant is handled at `0x2684C`, with construction at `0x26326` through `0x2632A`.

This makes serviceMenu the direct UI gate before constructing the engineering service menu. Its producer and authorization semantics are now resolved.

MainSupplement.swf VersionInfo::requestServiceFlags, method 8185 at 0x2D35B6, sends the platform command get_service_flags. VersionInfo::platformMessageHandler, method 8192 at 0x2D3745, reads get_service_flags.eng_menu at absolute offsets 0x2D3A64-0x2D3A6E, stores it as mServiceMenu, and dispatches ServiceEvent.SERVICE through 0x2D3A8C.

platform_troubleshoot.lua initializes service_flags.eng_menu=false at source/debug lines 29-45 and returns the flags in function 1, lines 54-56. Function 15, lines 465-490, registers get_service_flags. Functions 11/12, lines 406-427/408-422, ingest service.cert from SERVICEKEY media. Function 7, lines 255-304, requires successful verification by /fs/mmc0/app/security/scv, checks the certificate HUSerialNumber against /fs/fram/serialnumber, evaluates validity/expiry, and only then sets service_flags.valid=true and emits the flags at lines 281-290. Function 2, lines 63-127, maps EngineeringMenu numeric 1 to service_flags.eng_menu=true at lines 82-90. Functions 5/6, lines 188-248, reset/delete invalid or expired service state.

`diagserv.lua` supplies a second confirmed stock ingress to the same evaluator. IPC channel 7 reaches `onIpcMessage` prototype 298 (`0x3FC23-0x3FCD7`, lines 7562-7569), then `msgHandler[49]` and the routine dispatcher prototype 268 (`0x3A79A-0x3A88C`, lines 6876-6886). Routine `0xF010`, prototype 254 (`0x34D52-0x354C8`, lines 6249-6307), stages the fixed `/etc/security/service.cert` path and its finalize branch calls `com.harman.service.platform.evaluate_service_file`; only a returned table with `valid=true` is accepted. Routine `0xF011`, prototype 255 (`0x354C8-0x35804`, lines 6312-6333), removes that fixed path. These are internal IPC handlers, not the separately registered diagserv D-Bus methods, and the recovered routines contain no local diagnostic-session or SecurityAccess predicate. That does not prove external unauthenticated reachability: the IOC/gateway/tester gate before IPC channel 7 is still untraced.

The diagnostic staging operation is not transactional. Its first segment opens the active path with `w+b`, later segments append through `rb+`, and it has no temporary file, atomic rename, backup, fsync, or checked mount/write result. The same internal success tuple is emitted after a successful open and after an open failure (`0x34E4E-0x34E6E`). Thus a transport acknowledgment is not proof of durable or authentic service authorization; the platform verifier, HU serial check, and lifetime checks remain the authorization boundary.

Accordingly, serviceMenu is a service-certificate gate, bound to the head unit and constrained by expiry. No anti-theft PIN state is read in this producer/consumer chain.

AppManager has a separate embedded-application catalog check that must not be conflated with this HMI flag. Native function file offset 0x29E08 (VA 0x129E08) tests /fs/etfs/enableEngMenu with numeric mode 4 at 0x29E20-0x29E30 and returns enabled/disabled. Its only direct caller, file offset 0x3D1C0 (VA 0x13D1C0) in createEmbeddedApps, uses the result while processing appId engineering from appManager.cfg line 84. A false result reaches the skip diagnostic at file offset 0x105C58. No writer for enableEngMenu was found in the complete materialized primary-plus-hidden corpus. This controls AppManager's embedded engineering application entry; it is a different pathname, producer, and effect from Peripheral.versionInfo.serviceMenu and AMS_DEVELOPMENT.

### `Delete Service Key` rollback action

This menu item is a direct local file operation, not a ModuleLink or platform command:

- `AppsListEngServiceMenu::<cinit>` assigns `DELETE_SERVICE_KEY=20` at `0x36C77` through `0x36C7C`.
- The constructor unconditionally appends the visible label `Delete Service Key` at debug line 154, `0x370C4` through `0x370D6`.
- `AppsListEngServiceMenu::onItem` compares the selected ID with `DELETE_SERVICE_KEY` and selects switch value 20 at debug line 498, `0x37EF7` through `0x37F01`. Lookup-switch case 20 targets `0x37D11`.
- That case constructs `flash.filesystem.File("file:///fs/etfs/service.key")` at `0x37D17` through `0x37D24`, tests `.exists` at `0x37D3E` through `0x37D45`, and, when true, calls `.deleteFile()` directly at `0x37D59` through `0x37D61`. The false branch only traces `service.key does NOT exit.` at `0x37D65` through `0x37D6E`; both paths then leave the switch. There is no `Peripheral`, ModuleLink, D-Bus, or platform-service call in this case block.

`platform_troubleshoot.lua` does not expose a matching removal method. Its init function 15 registers exactly `get_service_flags`, `test_service_flag`, and `evaluate_service_file` at source/debug lines 469-471. Its `delete_service_file` function 5, lines 188-205, is an internal upvalue used only while invalidating the active service certificate: it makes `/fs/mmc0` writable, removes `service_cert_file`, and makes the filesystem read-only again at bytecode PCs 23-44. The active path is `/etc/security/service.cert`; `standard_boot/inventory.tsv` line 20 proves `/etc/security` is a symlink to `/fs/mmc0`. Function 14 (`evaluate_service_file`, lines 446-457) may reach that internal deletion through certificate validation, but the ActionScript item-20 block does not invoke it.

The separately recovered diagserv `0xF011` internal IPC routine can also remove `/etc/security/service.cert`, but item 20 does not call diagserv or IPC channel 7. Its presence therefore strengthens, rather than weakens, the boundary: the UI item, platform invalidation, and diagnostic removal are three distinct owners/paths. `0xF011` does not call the evaluator, reset `service_flags`, or notify the HMI, so it proves persistent-file removal rather than immediate live revocation; a supported refresh/restart boundary remains unknown.

Therefore `/fs/etfs/service.key` and `/etc/security/service.cert` are CONFIRMED distinct pathnames with distinct recovered deletion paths. No recovered alias or joining call proves that deleting the former revokes, reloads, or deletes the latter; that relationship remains UNKNOWN.

## Development-security item

`AppsListEngServiceMenu::<iinit>`, code offset `0x36C99`, debug line 145, calls `isDevepSecurityKeyEnabled()` at `0x37082` through `0x37087`. If the marker exists, it pushes label `Enable Production Security` at `0x3708B` through `0x370A0`; otherwise it pushes `Enable Development Security` at `0x370A8` through `0x370BD`.

The spelling `DevepSecurityKeyEnabled` is preserved from the SWF method name. Once this class is constructed, the development-security item block is unconditional; it has no PIN or authentication predicate.

`AppsListEngServiceMenu::<cinit>`, code offset `0x36B57`, sets these relevant item IDs:

| Constant | Value | Exact bytecode |
| --- | ---: | --- |
| `ENABLE_ANTITHEFT` | 4 | `0x36B97` through `0x36B9C` |
| `ENABLE_DEVP_SECURITY_KEY` | 19 | `0x36C69` through `0x36C6E` |
| `DELETE_SERVICE_KEY` | 20 | `0x36C77` through `0x36C7C` |

In `AppsListEngServiceMenu::onItem`, code offset `0x37743`, anti-theft enablement is a separate switch action: source/debug line 313 invokes `Peripheral.antiTheft.enableAntiTheft()` at `0x377FA` through `0x37804`. The development-security action is switch case 19, compared at `0x37EE3` through `0x37EF0`; source/debug lines 493 and 495 invoke `DevepSecurityKeyEnabled()` at `0x37D01` through `0x37D0D`.

`AppsListEngServiceMenu::isDevepSecurityKeyEnabled`, code offset `0x3896B`, debug lines 756-759, constructs `flash.filesystem.File("file:///fs/etfs/AMS_DEVELOPMENT")` at `0x3897D` through `0x38987` and returns `.exists` at `0x3898E` through `0x38992`.

`AppsListEngServiceMenu::DevepSecurityKeyEnabled`, code offset `0x3899D`, debug lines 761-790, implements the toggle:

- it constructs the same target file at `0x389BB` through `0x389CA`;
- if absent, it calls `File.createTempFile()` at `0x389DC` through `0x389E8`, moves the temporary file to the target with overwrite enabled at `0x38A18` through `0x38A21`, and changes the displayed label to `Enable Production Security`;
- if present, it calls `deleteFile()` at `0x38A55` through `0x38A5C` and changes the label to `Enable Development Security`;
- it invalidates the display at `0x38A79` through `0x38A7D`;
- its move-error catch only traces `Error:**` plus the message at `0x38A2C` through `0x38A4A`.

No reboot, AMS restart, token getter, anti-theft PIN request, or service IPC appears in this method.

## Evidence-graded UI path

| Edge | Grade and exact basis | Alternative or gap |
| --- | --- | --- |
| ICS button matrix --[CONFIRMED]--> icsHardKeys.processKnob | keys.lua functions 16-18, lines 531-619 | input arrives over IOC control/front-key IPC channels |
| driver temp up + down held through 5000 ms --[CONFIRMED]--> engineerMode key event | icsHardKeys.lua functions 32/33 and function 11 lines 265-267, PCs 140-145 | other product-specific chords also exist |
| anti-theft locked state --[CONFIRMED NO EDGE]--> engineerMode suppression | only volume/audio-power closures capture antiTheftStateUnlocked | engineering chord remains in generic processICS |
| engineerMode --[CONFIRMED]--> ICSEvent.ENGINEERING_MODE | MainSupplement.swf 0x2A73EA-0x2A7409 | none after message arrival |
| engineering event --[CONFIRMED]--> Apps List engineering extension | listener 0x2721BA-0x2721CA; navigation 0x272F7D-0x272F99 | toggles exit if already in engineering extension |
| HMI request --[CONFIRMED]--> platform get_service_flags | VersionInfo::requestServiceFlags 0x2D35B6 | none for request |
| verified, HU-bound, unexpired service certificate with EngineeringMenu=1 --[CONFIRMED]--> eng_menu=true | platform_troubleshoot.lua functions 2, 6, 7, 11, 12, and 15 | certificate provisioning authority/process remains outside this report |
| get_service_flags.eng_menu --[CONFIRMED]--> Peripheral.versionInfo.serviceMenu | VersionInfo::platformMessageHandler 0x2D3A64-0x2D3A8C | no PIN transform |
| enableEngMenu marker --[CONFIRMED]--> AppManager embedded engineering app inclusion | appManager function 0x129E08; createEmbeddedApps caller 0x13D1C0 | separate catalog gate, not Peripheral.versionInfo.serviceMenu |
| serviceMenu=true --[CONFIRMED]--> visible Service item | AppsListEngMenuScreen::<iinit> 0x3030C-0x30333 | none after valid flag |
| Service selection --[CONFIRMED]--> LIST_ENG_SERVICE_MENU | onItem 0x30B67-0x30B81 | none in HMI |
| service-menu construction --[CONFIRMED]--> development-security item | AppsListEngServiceMenu::<iinit> 0x37082-0x370BD | gate is reachability via serviceMenu |
| internal diagserv `0xF010` finalize --[CONFIRMED]--> platform certificate evaluation | diagserv prototype 254 PCs 71-72, files `0x34E82-0x34E86`; platform prototype 14 lines 446-457 | staging alone grants nothing; external diagnostic gate remains unknown |
| internal diagserv `0xF011` --[CONFIRMED]--> `/etc/security/service.cert` removal | diagserv prototype 255, files `0x354F8-0x35524` | separate from UI item 20 and `/fs/etfs/service.key` |
| marker exists/absent --[CONFIRMED]--> inverse action label | existence method 0x3896B; label branches 0x3708B-0x370BD | label describes the next action |
| item ID 19 --[CONFIRMED]--> direct marker toggle | comparison 0x37EE3-0x37EF0; call 0x37D01-0x37D0D | no auth callback is interposed |
| absent/present marker --[CONFIRMED]--> create/delete marker | 0x389DC-0x38A21 and 0x38A55-0x38A5C | failures receive limited UI surfacing |
| anti-theft PIN success --[CONFIRMED NO DIRECT EDGE]--> serviceMenu or item 19 | serviceMenu has the separate certificate producer; traced marker method has no PIN call/state | no recovered joining edge |
| marker toggle --[UNKNOWN]--> immediate running-policy activation | writer sends no restart/notification; all 778 hidden regular files contain no marker literal | next jvm.sh invocation re-samples the marker |

## Label and corpus survey

An in-memory survey of all 610 ROV SWFs, covering 113,007,867 reconstructed bytes, found no literal `Developer Mode`. `Development Security` and `AMS_DEVELOPMENT` occur only in `AppsListScreen.swf`. `MainSupplement.swf` separately contains `engineerMode` and anti-theft vocabulary.

This is strong negative evidence for the stock label, but localized or dynamically assembled text outside the surveyed ROV SWFs remains possible. The documented UI should therefore be called the Engineering menu's development-security toggle, not a proven screen named Developer Mode.

The three hidden HBCIFS inventories contain 778 regular files totaling 89,007,481 bytes. A complete exact scan found no AMS_DEVELOPMENT literal. platform_ams_restart.lua watches com.aicas.xlet.manager.AMS D-Bus ownership and a 120-second timer, not the marker. Its function 7, lines 183-209, can reinvoke jvm.sh after an AMS timeout/disappearance; that later invocation re-samples the marker. This is an AMS service-failure/startup supervisor, not a marker watcher.

## Reproducible read-only operations

- In-memory zlib inflation of CWS files, SWF tag walking, DoABC extraction, AVM2 constant-pool parsing, method disassembly, branch decoding, and debug-line recovery.
- A complete ROV SWF literal survey after in-memory reconstruction.
- Direct read of `ModuleLink.xml`; SHA-256 hashing with Node crypto.
- Bounded operand/name scans of the engineering menu constructors, listener registration, selection handlers, and marker toggle.
- Static Lua 5.1 prototype/constant/local/debug-line/instruction decoding for keys.lua, icsHardKeys.lua, platform_troubleshoot.lua, and platform_ams_restart.lua.
- Static Lua 5.1 control-flow decoding of diagserv prototypes 254, 255, 268, and 298, including fixed-path ownership and internal IPC registration; no diagnostic operation was sent.
- Exact scan of all 778 regular files (89,007,481 bytes) in the three hidden HBCIFS inventories.

## Unresolved gaps

1. The issuing authority and normal operational process for a valid RA4 service certificate, plus the external tester/IOC route and required diagnostic session/SecurityAccess state upstream of diagserv IPC channel 7; no attempt was made to forge, inject, or bypass one.
2. No recovered edge connects anti-theft PIN success to serviceMenu, the engineering event, or item 19; the positive evidence instead identifies separate controls.
3. No marker-specific watcher was found. The exact safe supported mechanism for intentionally reinvoking jvm.sh after an owner-authorized marker change remains unresolved.
4. The development-security item changes only the persistent marker; verification of the active running security policy remains a separate implementation requirement.
5. The producer of the separate /fs/etfs/enableEngMenu AppManager catalog marker is not present in the current primary-plus-hidden corpus.
