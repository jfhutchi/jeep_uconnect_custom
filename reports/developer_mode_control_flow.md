# RA4 18.45.01 development-security control flow

## Integrated finding

The recovered RA4 evidence resolves three separate controls, not the originally hypothesized single authentication chain:

1. ICS hard-key code emits engineerMode after driver temperature up and down remain pressed for five seconds. The HMI opens the engineering menu. Its Service item becomes reachable only when a verified, head-unit-bound, unexpired service certificate grants EngineeringMenu. Stock code accepts candidates from the SERVICEKEY media handler and from a factory-oriented internal diagnostic staging routine; both converge on the same verifier. Item 19 then directly creates or deletes /fs/etfs/AMS_DEVELOPMENT.
2. jvm.sh samples that marker only when invoked and selects the production or development security.jar. A supervisor can reinvoke jvm.sh after AMS startup timeout/service disappearance, but it watches AMS D-Bus ownership rather than the marker.
3. The anti-theft keypad routes through hmiGateway to onOff, which sends the four input bytes to the IOC over IPC channel 2. Static `cmcioc.bin` analysis locates the comparison/success branch: it updates a distinct anti-theft state and publishes the result. After a qualifying entered-PIN unlock, the HMI invokes xletsReturnToNew, whose native receiver wipes factory application state, restores preload, and requests a head-unit reset.

An exhaustive IOC direct-state/getter/mutator census proves no reverse edge from PIN success to proprietary diagnostic authorization state 4 or its finite allowance. No recovered operand, call, signal, listener, packet field, state field, or file access makes PIN success authorize serviceMenu, toggle AMS_DEVELOPMENT, or create a developer token. `xlet.developerToken` remains signed package metadata loaded and verified inside AMS.

## Primary artifacts

| Role | Artifact and exact anchor |
| --- | --- |
| Engineering event bridge | `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/MainSupplement.swf`; `ICS::messageHandler` code `0x2A728C`; `HardControls::onEngineeringMode` code `0x272F49` |
| Engineering menu and marker writer | `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/skins/default/swf/AppsListScreen.swf`; `AppsListEngServiceMenu::onItem` code `0x37743`; `DevepSecurityKeyEnabled` code `0x3899D` |
| Anti-theft bridge | same `MainSupplement.swf`; `AntiTheft::checkAntiTheftPin` code `0x2AC4E7`; `AntiTheft::MessageHandler` code `0x2AC0C4` |
| AMS launcher | `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/jvm.sh`, lines 58-63; SHA-256 `9bd3c63a2c22c17f96e037102283f453afca43eb093bc1291d607a9805f829ec` |
| AMS token verifier | `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/AMS`; VCL getter/body `0x5C2BB4/0x5C2BF3..0x5C2BFA`; private verifier `0x5C2AD1..0x5C2AEA`; KeyVerifier branch `0x5C1AE6..0x5C1B25` |
| ICS producer | `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/vehicle/icsHardKeys.lua`; SHA-256 `86aba0d0c5fbfdeb9d5da36edd66c81e3e76cf16744740d9778612f41a7a1ea5`; `keys.lua` SHA-256 `620809fd91f2ddd3d48d874db62ab6afd11a3501e2a5a2d4812922cfa4d40040` |
| Service flag producer | `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/platform_troubleshoot.lua`; SHA-256 `8beab38ab164479a9fd815116dbfa02a48e3fa661724fa9c4273dc5884a1ba45` |
| Diagnostic certificate staging/removal | `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/usr/bin/cmc/service/diagserv.lua`; 282,802 bytes; SHA-256 `777d96dfa3461caa6ebf4765784f9ba2f4d766fd1ddfe54590a655121353bd64`; prototypes 254/255 and IPC channel-7 dispatcher |
| Anti-theft proxy | hidden HBC `bin/hmiGateway`, SHA-256 `8d7fe8789bb012a66fbebd1bd44eefa506c672a5d70c90fbf92b3a5a6f01ec82`; `usr/bin/onoff/main.lua`, SHA-256 `41c0f3f2709c49d4a4f9b150b8c08c735515a9c50bbfbc2e4c36664d6466e698` |
| IOC diagnostic/PIN domains | `analysis_ra4_18.45.01/work/primary_iso/usr/share/V850/hs/cmcioc.bin`; 458,752 bytes; SHA-256 `c7bf247bfdb10b5dfda2802df1210671f6a1872140cdeebc014c109a9c77e012`; `VA=file+0x10000` |
| AppManager receiver | hidden HBC `segment_00f20000/files/bin/appManager`; SHA-256 `608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591` |
| AMS supervisor and boot | hidden HBC `platform_ams_restart.lua`, SHA-256 `264e5aaa6e2e09e8bb86a881f4919a66220d1cad2c7ce9443416e5d35f9f720f`; `standard_boot/files/bin/boot.sh`, SHA-256 `c801d473b0b49e8242114635f4022cc67ccbe03093fec188de3b7188dd636ecf` |

SWF offsets are reconstructed uncompressed FWS offsets. AMS offsets are executable file offsets. Script lines are physical text lines.

## Flow A: physical gesture to authorized marker action

| Edge | Grade and exact evidence | Qualification |
| --- | --- | --- |
| ICS matrices/front-key IPC --[CONFIRMED]--> hard-key processor | keys.lua functions 16-18, source/debug lines 531-619 | IOC control channel and channel 25 are the ingress paths |
| driver temperature up + down held 5000 ms --[CONFIRMED]--> engineerMode | icsHardKeys.lua functions 32/33, lines 652-683; timer function 11 lines 265-267 and PCs 140-145 | anti-theft state is not tested in this path |
| engineerMode --[CONFIRMED]--> ICSEvent.ENGINEERING_MODE | MainSupplement.swf 0x2A73EA-0x2A7409 | none after HMI message arrival |
| engineering event --[CONFIRMED]--> LIST_ENG_MENU | listener 0x2721BA-0x2721CA; handler/navigation 0x272F49 and 0x272F7D-0x272F99 | repeat event exits an engineering extension |
| HMI --[CONFIRMED]--> platform get_service_flags | VersionInfo::requestServiceFlags 0x2D35B6 | local request |
| IOC session + state 4 --[CONFIRMED]--> F010/F011 channel-7 forwarding | cmcioc dispatcher `0x557CC`; session gate `0x45896..0x458AC`; state getter `0x54228`; handlers `0x6D730/0x6D7D0`; forwarder `0x52FB0` | legitimate external session/challenge authority remains unknown |
| internal diagserv `0xF010` staged finalize --[CONFIRMED]--> `evaluate_service_file` | prototype 254 PCs 68-72, files `0x34E76-0x34E86`; validator prototype 1 files `0x421A-0x4242` | stock certificate/HU/lifetime validation still required |
| verified certificate, matching HU serial, valid expiry, EngineeringMenu=1 --[CONFIRMED]--> eng_menu=true | platform_troubleshoot.lua functions 2, 6, 7, 11, 12, 15; source lines 63-304 and 406-490 | factory service-certificate authorization |
| get_service_flags.eng_menu --[CONFIRMED]--> serviceMenu=true | VersionInfo::platformMessageHandler 0x2D3A64-0x2D3A8C | no anti-theft/PIN transform |
| serviceMenu=true --[CONFIRMED]--> Service item | AppsListEngMenuScreen::<iinit> 0x3030C-0x30333 | certificate validity controls reachability |
| Service selection --[CONFIRMED]--> LIST_ENG_SERVICE_MENU | AppsListEngMenuScreen::onItem 0x30B67-0x30B81 | none in HMI |
| service-menu construction --[CONFIRMED]--> item 19 | AppsListEngServiceMenu::<iinit> 0x37082-0x370BD | action label reflects marker existence |
| item 19 --[CONFIRMED]--> DevepSecurityKeyEnabled | onItem 0x37EE3-0x37EF0 and call 0x37D01-0x37D0D | no PIN callback interposed |
| marker absent/present --[CONFIRMED]--> marker create/delete | method 0x389BB-0x38A5C | no process signal or notification |

The physical gesture itself is not the authorization gate for the Service item. The positive factory gate is the service certificate. `icsHardKeys.lua` tracks antiTheftStateUnlocked only for volume-knob and audio-power closures; its generic processICS and engineerMode timer do not test it. No local authentication test appears in diagserv prototypes 254/255/268/298 because the active IOC enforces diagnostic session, condition, and proprietary state 4 before forwarding. The external authority that establishes that state and issues the valid certificate remains unknown.

AppManager separately filters the embedded application whose appId is engineering. Native function file offset 0x29E08 (VA 0x129E08) tests /fs/etfs/enableEngMenu with numeric mode 4 at 0x29E20-0x29E30. Its sole direct caller at file offset 0x3D1C0 (VA 0x13D1C0) is in createEmbeddedApps; a false result reaches the skip diagnostic at 0x105C58. This is an embedded-app catalog gate. It has a different pathname, producer, consumer, and effect from the HMI serviceMenu certificate flag and AMS_DEVELOPMENT security selector. No writer for enableEngMenu was found in the materialized primary-plus-hidden corpus.

## Flow B: marker to AMS security policy

`jvm.sh` contains the known consumer:

- line 58 initializes the production security-JAR selection;
- line 59 tests `-f /fs/etfs/AMS_DEVELOPMENT` and switches to the development security JAR when present;
- line 61 logs the selected security configuration;
- line 63 launches `AMS` with `-securityConfiguration "$AMS_SECURITY_JAR" -secure` and the Kona installation, extension, initializer, property, and Xlet-directory arguments.

| Edge | Grade and exact evidence | Qualification |
| --- | --- | --- |
| marker present at jvm.sh evaluation --[CONFIRMED]--> development security.jar selected | jvm.sh lines 58-59 | applies only when launcher runs |
| marker absent at jvm.sh evaluation --[CONFIRMED]--> production security.jar selected | jvm.sh line 58 plus failed line-59 condition | applies only when launcher runs |
| selected JAR --[CONFIRMED]--> AMS -securityConfiguration argument | jvm.sh line 63 | direct script argument |
| AMS service startup timeout/disappearance --[CONFIRMED]--> supervisor executes jvm.sh | platform_ams_restart.lua functions 7, 9, 10, lines 183-250 | watches D-Bus ownership/timer, not marker |
| marker toggle --[CONFIRMED NO DIRECT RELOAD]--> writer completion | ActionScript method ends after file/display operations | no restart or notification in writer |
| marker toggle --[UNKNOWN]--> automatic immediate restart | no AMS_DEVELOPMENT literal in 778 hidden regular files totaling 89,007,481 bytes | watcher outside searched corpora remains theoretically possible |
| later jvm.sh invocation while marker state persists --[CONFIRMED]--> changed policy selection | exact shared path in writer and launcher | controlled restart mechanism still must be designed |

The earliest proved activation point is a later jvm.sh evaluation. platform_ams_restart.lua provides a failure/startup recovery route, not a marker-change route. A full device reboot is sufficient by architecture, but the evidence does not make it the only possible restart boundary.

A separate AppManager control must not be conflated with this path. standard_boot/files/bin/boot.sh lines 367/371 and 461/465 assign disableDRMArg=-d and pass it to appManager. On restart, platform_ams_restart.lua decides whether to pass -d from /fs/etfs/disableDRM. Neither control reads AMS_DEVELOPMENT; AMS security.jar selection remains in jvm.sh.

## Flow C: anti-theft PIN, IOC decision, and factory-app reset

| Edge | Grade and exact evidence | Qualification |
| --- | --- | --- |
| keypad Done --[CONFIRMED]--> checkAntiTheftPin(mInput) | PopupAntiTheftKeypad.swf 0x5892 and 0x58A1-0x58AA | no synchronous result |
| HMI method --[CONFIRMED]--> Dest=AntiTheft/checkAntiTheftPIN packet | MainSupplement.swf 0x2AC4E7 and 0x2AC4FA-0x2AC513 | none for packet creation |
| Dest=AntiTheft --[CONFIRMED]--> com.harman.service.onOff | hmiGateway file offsets 0x7BE0, 0x8E18, 0x9E3C, 0x9E4C | native local proxy |
| checkAntiTheftPIN --[CONFIRMED]--> IPC ch2 message 0xE0 plus four input bytes | onoff/main.lua function 28, lines 1116-1126 | returns immediately; no local comparison |
| submitted PIN --[CONFIRMED]--> IOC decision and published state | cmcioc decision VA/file `0x25658/0x15658`; equality branch `0x256AE..0x256C2`; publisher `0x2AD6C/0x1AD6C` | comparator content and retry/lockout policy remain protected unknowns |
| IOC response --[CONFIRMED]--> state/counter/lock-time | onoff/main.lua function 23, lines 687-1055 | asynchronous result mapping |
| IOC state --[CONFIRMED]--> locked/wait/enter/wrong/unlocked/forced-update HMI state | onOff mapping lines 921-953 and MainSupplement.swf MessageHandler 0x2AC0C4 | asynchronous path |
| prior enterPIN plus supported product plus unlocked --[CONFIRMED]--> xletsReturnToNew | MainSupplement.swf 0x2AC1B8-0x2AC209 | both state-history and product conditions matter |
| xletsReturnToNew --[CONFIRMED]--> native handler 0x12AA7C | appManager parseRequest comparison 0x5C460 and call 0x5C4A8 | xletsReset is a distinct command |
| native handler --[CONFIRMED]--> RMS/Xlet/resource wipe, preload restore, AMS temp removal, HU reset | appManager 0x12AA7C, 0x12A95C, 0x12A890; strings 0x101D04-0x101F1C | destructive factory-app restoration |
| xletsReturnToNew --[CONFIRMED NO EDGE]--> marker/token operation | no AMS_DEVELOPMENT or developer-token operation in receiver | reset later causes ordinary boot only |
| proprietary state 4 --[CONFIRMED ONE-WAY]--> anti-theft comparator provisioning | manufacturing handler `0x6C388` requires getter state 4 and persists/copies comparator at `0x6C42C/0x6C446..0x6C452` | provisioning authority, not PIN authentication |
| PIN success --[CONFIRMED BOUNDED ABSENCE]--> state 4/allowance | PIN decision/publisher have zero `GP-0x7B38`, `GP-0x7B34`, getter, or mutator references | no reverse edge in exhaustive direct xrefs |

The comparison/success routine is located in the IOC. Protected comparator provenance, retry threshold/progression, and lockout-duration policy remain intentionally unresolved. They are unnecessary to the developer-authorization path.

## Separation matrix

This matrix distinguishes direct evidence from tempting name-based conflation.

| Proposed relationship | Grade | Exact control-flow result | Evidence-backed model |
| --- | --- | --- | --- |
| anti-theft unlock required to emit engineerMode | CONFIRMED ABSENT | only volume/audio-power handlers test antiTheftStateUnlocked | engineering gesture is independent |
| successful anti-theft PIN -> serviceMenu=true | CONFIRMED BOUNDED ABSENCE with positive alternative | IOC PIN-success direct xrefs and HBC callbacks have no service/diagnostic state edge; serviceMenu is assigned from get_service_flags.eng_menu | valid service certificate is the proved producer |
| enableEngMenu -> serviceMenu or AMS_DEVELOPMENT | CONFIRMED SEPARATE | native AppManager only uses it while filtering appId engineering | separate embedded-app catalog control |
| serviceMenu=true -> item 19 reachability | CONFIRMED | AppsList constructor/selection flow | service certificate gates the Service item |
| diagserv staging response -> certificate accepted | CONFIRMED FALSE EQUIVALENCE | the same staging tuple follows both open success and open failure; finalize separately invokes platform validation | only verifier/HU/lifetime success creates valid service state |
| successful anti-theft PIN -> AMS_DEVELOPMENT | CONFIRMED BOUNDED ABSENCE | PIN route updates independent IOC state and optional xletsReturnToNew reset; no state4/allowance/marker/token reference | item 19 is the proved writer |
| xletsReturnToNew -> marker change | CONFIRMED ABSENT in receiver | native handler wipes app state/restores preload/resets HU | later boot may re-sample pre-existing marker |
| AMS_DEVELOPMENT -> policy selection | CONFIRMED at launcher | jvm.sh lines 58-63 | marker is persistent launch-time selector |
| AMS_DEVELOPMENT -> automatic immediate restart | UNKNOWN with negative bound | no marker watcher in full hidden regular-file inventory | explicit safe restart remains to be designed |
| AppManager -d or disableDRM -> AMS development security.jar | CONFIRMED SEPARATE | boot/restart AppManager commands use -d; jvm.sh uses AMS_DEVELOPMENT | independent DRM/AppManager and AMS-policy controls |
| development policy -> token generation | CONFIRMED BOUNDED ABSENCE | item 19/launcher only select security JAR; VCL reads package-carried `xlet.developerToken` | policy may change acceptance/principal assignment, not shown generation |

The strongest positive model is therefore: an engineering gesture, a factory service-certificate reachability gate, a direct persistent marker, a launch-time AMS policy selector, an independent IOC anti-theft state machine, and package-carried developer credentials.

## Negative evidence with bounds

- All 610 ROV SWFs (113,007,867 reconstructed bytes) were surveyed; Developer Mode was absent, while Development Security and AMS_DEVELOPMENT were confined to AppsListScreen.swf.
- Engineering constructors/handlers were operand-scanned. Anti-theft item ID 4 is separate from development-security item ID 19.
- All 778 regular files in the three hidden HBCIFS inventories, totaling 89,007,481 bytes, were exact-scanned for AMS_DEVELOPMENT; there were zero hits. This census includes the one zero-length regular file.
- platform_ams_restart.lua was fully decoded. Its inputs are AMS D-Bus ownership, a 120-second timer, and /fs/etfs/disableDRM for the AppManager command; it does not read the development marker.
- Decompressed entry/constant scans of kona.jar, ams_initializer.jar, and both policy JARs found no target anti-theft-PIN terms.
- The former missing-receiver/comparison bound is superseded: hidden hmiGateway/onOff prove the proxy, and static `cmcioc.bin` analysis locates the comparison/success branch and its separation from proprietary diagnostic state.

These bounds prevent interpreting a negative result as a system-wide impossibility.

## Reproducible read-only operations

- Node `fs` traversal/read/stat, SHA-256 hashing, bounded exact byte searches, and line-numbered script/property parsing.
- Node zlib in-memory CWS reconstruction, SWF tag and DoABC parsing, AVM2 constant-pool decoding, method-body disassembly, switch/branch decoding, and debug-line recovery.
- Complete tag-driven Jamaica ROM pool/literal/member/class-object decoding over `AMS`.
- QNX hidden-HBC decompression, imagefs inventory, Lua 5.1 bytecode decoding, ARM ELF analysis, and static V850 direct-call/GP/persistent-slot/receive-table tracing.
- JSZip in-memory inspection of Java archives; no archive was installed or executed.
- `git status --short` through direct `git` process invocation for workspace-state verification; no commit or index mutation.

No vendor binary, Java archive, installer, firmware updater, or target script was executed. No firmware ZIP was unpacked into or written over the supplied stock input, and no flash/install package was created.

## Unresolved gaps

1. The protected anti-theft comparator provenance, retry threshold/progression, lockout-duration policy, and VIN coupling; the comparison/success branch itself is located.
2. The normal issuance workflow for a valid RA4 service certificate and legitimate external authority that establishes the proved IOC diagnostic session/state 4 before diagserv channel 7; no bypass or forgery was attempted.
3. The safest supported, reversible mechanism to reinvoke jvm.sh and verify the active policy after an owner-authorized marker transition.
4. Any marker watcher outside the standard IFS, all three hidden HBCIFS payloads, and primary MMC extension already searched.
5. The update corpus contains no usable reflected `Device` ID provider after an exhaustive 300-JAR/72,507-class census. The exact `SignedId` Base64/SunJCE `RSA/ECB/PKCS1Padding`/exact-ID predicate and two-stage signer-key bootstrap are confirmed; the remaining live boundary is an unrecovered system/boot overlay, a legitimate credential issuer, and the production/development signer-to-policy rules.
6. The complete direct IOC/HBC census confirms no bridge from PIN success to diagnostic state 4, the service-certificate gate, development marker, or developer token; the positive evidence identifies separate security domains.
7. The producer of the separate /fs/etfs/enableEngMenu AppManager catalog marker.
