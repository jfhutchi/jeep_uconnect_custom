# RA4 18.45.01 Master Findings

Updated: 2026-09-04

This is the authoritative evidence index for the owner-authorized RA4 18.45.01 reverse-engineering project. It reconciles the detailed reports and records what is proved, what remains unknown, and what must be true before any on-unit implementation. It is not a modification or flashing procedure.

## Status and non-negotiable boundary

The most important correction is now evidence-backed:

> RA4 18.45.01 does not implement one chain from factory anti-theft PIN success to Development Security. The recovered firmware implements separate security domains with different producers, consumers, state, and effects.

This project will not derive, disclose, brute-force, bypass, disable, short-circuit, or repurpose the anti-theft PIN. It will not forge a service certificate, application signature, developer credential, DRM grant, or software-update signature. It will not modify or flash stock firmware until explicitly authorized after every stop gate is closed.

Evidence labels used here are:

- **[CONFIRMED]** directly present in a named stock artifact.
- **[HIGH]** supported by independent artifacts but still crossing a closed native/runtime boundary.
- **[INFERRED]** best current explanation, not proof.
- **[UNKNOWN]** not established by the recovered corpus.
- **[DESIGN]** a proposed future owner-authorized approach, not executed.
- **[STOP]** unresolved evidence that forbids on-unit mutation.

No stock FCA/Chrysler/Harman archive, ISO, executable, JAR, SWF, certificate, key, decoded filesystem, or decompiled vendor code may be committed. Raw developer-token values and authentication-service key material are intentionally omitted.

## Executive correction: four separate controls

| Security/control domain | Confirmed input | Confirmed decision/state | Confirmed effect | Not proved |
| --- | --- | --- | --- | --- |
| Engineering-menu entry | Driver-temperature up and down held for 5 seconds | `engineerMode` hard-key event | Opens the engineering UI route | Anti-theft authorization |
| Service authorization and AMS Development Security | Authentically issued, HU-bound, valid `service.cert` with `EngineeringMenu=1`, introduced by a stock path | IOC diagnostic session + proprietary authorization state 4 gate the internal diagnostic transport; platform evaluation, `service_flags.eng_menu`, UI item 19, then `/fs/etfs/AMS_DEVELOPMENT` | A later `jvm.sh` execution selects development `security.jar`; AMS remains `-secure` | legitimate external session/challenge authority, certificate issuer, immediate policy reload, developer-token issuance |
| Factory anti-theft | Keypad request routed through onOff to IOC | IOC compares against its protected comparator and publishes independent anti-theft state/counter/lock time | In the entered-PIN VP2/VP3/VP4 path, unlock requests destructive `xletsReturnToNew` factory-app restoration and HU reset | Marker creation, service authorization, developer-token creation; PIN success is proved not to create diagnostic state 4 |
| Embedded engineering app catalog | Native AppManager tests `/fs/etfs/enableEngMenu` | Boolean file-presence gate | Includes or suppresses embedded app ID `engineering` | A writer; equivalence to service-menu access or AMS development policy |

The first row is a physical entry gesture, not authorization. The second row is the recovered authorization path to Development Security. The third row protects factory anti-theft state and has a destructive application-reset side effect in one specific transition. The fourth row controls a native embedded-app catalog entry. Joining them into a single "PIN -> Developer Mode" chain would be unsupported and unsafe.

## 1. Confirmed Development Security control flow

The exact recovered path is:

    driver-temperature up + down held for 5 seconds
      -> icsHardKeys.lua emits engineerMode
      -> MainSupplement dispatches ICSEvent.ENGINEERING_MODE
      -> engineering menu opens

    legitimately issued service.cert
      -> stock SERVICEKEY media handler
         OR IOC-session/state-4-gated diagserv 0xF010 staging/finalize
            (legitimate external session/challenge authority remains unknown)
      -> stock platform_troubleshoot evaluates service.cert
      -> RSA verification with the stock public verification key
      -> HUSerialNumber must equal /fs/fram/serialnumber
      -> date / ignition-cycle validity must pass
      -> EngineeringMenu=1 becomes service_flags.eng_menu=true
      -> MainSupplement publishes Peripheral.versionInfo.serviceMenu=true
      -> AppsList exposes Service
      -> Service item 19 toggles /fs/etfs/AMS_DEVELOPMENT

    later execution of /fs/mmc0/app/bin/jvm.sh
      -> marker absent: production security.jar
      -> marker present: development/security.jar
      -> AMS starts with selected -securityConfiguration and -secure

### 1.1 Physical engineering-menu producer

**[CONFIRMED]** `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/vehicle/icsHardKeys.lua` is 31,153 bytes, SHA-256 `86aba0d0c5fbfdeb9d5da36edd66c81e3e76cf16744740d9778612f41a7a1ea5`. Decoded functions 32 and 33, source/debug lines 652-683, start a 5,000 ms timer for the two driver-temperature buttons. Function 11, lines 237-279, emits the `engineerMode` key when both saved button states are set.

**[CONFIRMED]** `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/MainSupplement.swf` is SHA-256 `e9d796ea4b4c83ed518bfe3b3c341e54e510a1ae0f78ebbffbd655b7c36a3258`. Its reconstructed `ICS::messageHandler` begins at FWS offset `0x2A728C`, compares `engineerMode` at `0x2A73EA-0x2A73F7`, and dispatches `ICSEvent.ENGINEERING_MODE` at `0x2A73FB-0x2A7409`.

**[CONFIRMED ABSENCE]** Anti-theft state in `icsHardKeys.lua` gates volume/audio-power behavior, not the two temperature handlers, their timer, or `engineerMode`. The gesture opens a route; it does not grant service or developer authorization.

### 1.2 Service-certificate authorization and serviceMenu producer

**[CONFIRMED]** `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/platform_troubleshoot.lua` is 13,931 bytes, SHA-256 `8beab38ab164479a9fd815116dbfa02a48e3fa661724fa9c4273dc5884a1ba45`.

- Function 11, source/debug lines 406-427, registers `SERVICEKEY`; its nested function at lines 408-422 copies the candidate `service.cert` and invokes evaluation.
- Function 7, lines 255-304, invokes `/fs/mmc0/app/security/scv`, supplies `/etc/keys/serv_cert_key.pem`, compares `HUSerialNumber` with `/fs/fram/serialnumber`, and evaluates the certificate.
- Functions 5 and 6, lines 188-248, clear invalid state and enforce date/ignition-cycle limits.
- Function 2, lines 63-127, maps `EngineeringMenu=1` to `service_flags.eng_menu=true`.
- Function 15, lines 465-490, registers `get_service_flags`, `test_service_flag`, and `evaluate_service_file`.

**[CONFIRMED]** A second factory-oriented stock ingress is owned by `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/usr/bin/cmc/service/diagserv.lua` (282,802 bytes; SHA-256 `777d96dfa3461caa6ebf4765784f9ba2f4d766fd1ddfe54590a655121353bd64`). IPC channel 7 reaches `onIpcMessage` prototype 298 (`0x3FC23-0x3FCD7`), `msgHandler[49]`, and dispatcher prototype 268 (`0x3A79A-0x3A88C`). Registered routine `0xF010`, prototype 254 (`0x34D52-0x354C8`, lines 6249-6307), stages `/etc/security/service.cert`; its finalize branch calls `evaluate_service_file` through validator prototype 1 (`0x4206-0x4567`, lines 325-342). Registered routine `0xF011`, prototype 255 (`0x354C8-0x35804`, lines 6312-6333), removes that path.

**[CONFIRMED BOUND / STOP]** This bridge does not weaken or replace certificate authentication. The platform still requires verifier success, exact HU-serial match, and date/ignition validity before setting `service_flags.valid`. The Lua routines contain no local gate, but the active IOC/V850 image does: RoutineControl descriptor 8 requires a non-default diagnostic session, condition state, a generic security-mask intersection, and proprietary authorization state 4 before handlers `0x6D730/0x6D7D0` forward through channel 7. State 4 is reached by a separate challenge/response state machine with retry/lockout; no secret, value, or framing is reproduced. The legitimate external authority remains unknown, so no direct invocation is safe or authorized.

**[CONFIRMED]** Runtime state `GP-0x7B38` has a closed direct-read/write census; getter `0x54228` has exactly 12 direct callsites and all are diagnostic-handler authorization reads. Finite allowance slot `0x11A` can restore state 4, but its only setter is already state-4-gated; its other mutator caller only decrements it after a sustained network-received raw ignition `start`-state event. Getter `0x4A694` selects the low three bits of one of two packed receive words, the IOC forwards that value as raw ignition state, and HBC `onoff/main.lua` independently maps value 4 to `start`; derived `powerModeState` is a separate record field. The upstream source ECU/bus/message, product-variant selector meaning, and scheduler timebase remain unresolved. Staging itself remains non-atomic: the first segment truncates the active path, there is no temporary file/rename/fsync/backup, and open failure reaches the same internal acknowledgment tuple as open success at `0x34E4E-0x34E6E`.

The verifier `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/security/scv` is 1,596,550 bytes, SHA-256 `08bb7992d95b27b98bcb222021015cda152eef9fafa573720845d28c837c7fe1`. The 2,048-bit RSA public verification key at `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/etc/keys/serv_cert_key.pem` is 451 bytes, SHA-256 `07e7a63fd528cdd4b4d23bc6aaac03adda4ca9659d0b4a86ddd5d26b8608831e`. A public key can verify authorization; it cannot issue it.

**[CONFIRMED]** MainSupplement's VersionInfo client requests method 8185 at reconstructed FWS offset `0x2D35B6`. Handler method 8192 begins at `0x2D3745`, reads `get_service_flags.eng_menu` at `0x2D3A64-0x2D3A6E`, and dispatches the result at `0x2D3A8C`. This is the upstream producer for `Peripheral.versionInfo.serviceMenu`.

**[CONFIRMED]** `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/skins/default/swf/AppsListScreen.swf` is 117,093 bytes, SHA-256 `5bc1630f567c82494ab86e73c308ad2a8b9d341494a5f5de5f66a1505f1416e5`, and reconstructs to 282,644-byte FWS. `AppsListEngMenuScreen::<iinit>` exposes Service only when `Peripheral.versionInfo.serviceMenu` is true at `0x3030C-0x30333`.

### 1.3 Item 19 is the marker creator and deleter

**[CONFIRMED]** `AppsListEngServiceMenu::<cinit>` assigns Development Security item ID 19 at FWS `0x36C69-0x36C6E`. Stock method `DevepSecurityKeyEnabled` starts at `0x3899D`:

- absent marker: `File.createTempFile()` plus `moveTo(target,true)` creates `/fs/etfs/AMS_DEVELOPMENT` at `0x389DC-0x38A21`;
- present marker: `deleteFile()` removes it at `0x38A55-0x38A5C`.

Companion reader `isDevepSecurityKeyEnabled` starts at `0x3896B`, constructs the path at `0x3897D-0x38987`, and reads `.exists` at `0x3898E-0x38992`.

**[CONFIRMED ABSENCE]** The item-19 method contains no anti-theft callback, token request, D-Bus/SvcIPC request, AppManager command, AMS restart, or reload notification. A changed UI label does not prove that the running AMS changed configurations.

### 1.4 The marker is sampled at AMS startup

**[CONFIRMED]** `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/jvm.sh` is 2,795 bytes, SHA-256 `9bd3c63a2c22c17f96e037102283f453afca43eb093bc1291d607a9805f829ec`. Lines 58-59 choose production `/fs/mmc1/kona/security/security.jar` or development `/fs/mmc1/kona/security/development/security.jar`. Line 61 logs the choice. Line 63 launches AMS with that `-securityConfiguration`, `-installationDirectory /fs/mmc1/xletsdir`, and unconditional `-secure`.

**[CONFIRMED]** `analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/files/bin/boot.sh` is 29,268 bytes, SHA-256 `c801d473b0b49e8242114635f4022cc67ccbe03093fec188de3b7188dd636ecf`. It creates AppManager RMS and launches AppManager at lines 362-371 and 456-465, waits for `/dev/serv-mon/com.aicas.xlet.manager.AMS` at lines 398 and 722, and launches `platform_ams_restart.lua` at line 747. `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/bin/connectivity_startup.sh` is 939 bytes, SHA-256 `2d693484a49539ae1f83512bac068580014b1c2dcbb2c5885609e01726e3502f`; its lines 23-24 invoke `qon -d jvm.sh`. That `-d` is a `qon` option, not AppManager or AMS.

**[CONFIRMED]** `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/platform_ams_restart.lua` is 7,514 bytes, SHA-256 `264e5aaa6e2e09e8bb86a881f4919a66220d1cad2c7ce9443416e5d35f9f720f`. Decoded functions 7, 9, and 10, source/debug lines 183-250, supervise AMS D-Bus ownership and a 120-second startup timer. AMS loss/startup timeout can eventually invoke `jvm.sh` again, which re-samples the marker.

**[CONFIRMED ABSENCE / UNKNOWN DYNAMIC]** The restart Lua has no `AMS_DEVELOPMENT` literal, file test, subscription, or inotify-like watch. No recovered component immediately reloads policy merely because item 19 changed the file. Deliberately killing AMS is not an approved activation step; controlled ordinary boot is the least ambiguous future boundary.

## 2. Exact marker ownership and persistence

| Operation | Confirmed owner | Evidence | Result |
| --- | --- | --- | --- |
| Read for UI label | `AppsListEngServiceMenu::isDevepSecurityKeyEnabled` | FWS `0x3896B-0x38992` | Reports marker presence |
| Create | `AppsListEngServiceMenu::DevepSecurityKeyEnabled` | FWS `0x389DC-0x38A21` | Temp file moved to `/fs/etfs/AMS_DEVELOPMENT` |
| Delete | Same item-19 method | FWS `0x38A55-0x38A5C` | Removes marker |
| Read for policy selection | `jvm.sh` | lines 58-63 | Chooses security JAR before AMS launch |
| Restart after unrelated AMS failure | `platform_ams_restart.lua` | functions 7/9/10, lines 183-250 | Reinvokes `jvm.sh`; not a marker watcher |
| Any other actor | **[UNKNOWN with bounded negative evidence]** | census below | None found in materialized corpus |

The three decoded hidden HBC inventories contain exactly 778 regular files totaling 89,007,481 bytes:

- segment `0x001a0000`: 433 files, 30,769,956 bytes;
- segment `0x00f20000`: 219 files, 22,931,139 bytes;
- segment `0x019a0000`: 126 files, 35,306,386 bytes.

An exact scan of all 778 files, including the one zero-length file, found zero `AMS_DEVELOPMENT` literals. The standard-boot inventory adds 46 regular files totaling 2,949,863 bytes and also has zero marker literals. Together with the materialized primary extraction, the only proved actors are the AppsList reader/writer/deleter and `jvm.sh` reader. This is a bounded corpus result, not proof against unmaterialized or dynamically constructed paths.

## 3. Anti-theft is separate and must remain stock

The exact path is:

    PopupAntiTheftKeypad::onDone
      -> MainSupplement AntiTheft.checkAntiTheftPin
      -> Dest=AntiTheft / checkAntiTheftPIN
      -> hmiGateway
      -> com.harman.service.onOff
      -> onoff/main.lua writes request to IOC IPC channel 2
      -> immediate empty response; no local comparison
      -> cmcioc PIN-decision routine compares only in enter-PIN state
      -> success updates independent anti-theft state/publication flags
      -> later IOC state/counter/lock-time messages
      -> entered-PIN + VP2/VP3/VP4 + unlocked transition
      -> AppManager xletsReturnToNew
      -> Xlet/RMS/resource wipe, preload restore, HU reset

**[CONFIRMED]** `PopupAntiTheftKeypad::onDone` is at MainSupplement FWS `0x5892`. `AntiTheft::checkAntiTheftPin` is at `0x2AC4E7` and sends `checkAntiTheftPIN`. No submitted PIN material is reproduced.

**[CONFIRMED]** `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/bin/hmiGateway` is 153,124 bytes, SHA-256 `8d7fe8789bb012a66fbebd1bd44eefa506c672a5d70c90fbf92b3a5a6f01ec82`. Routing anchors occur at file offsets `0x7BE0` and `0x8E18`; service/object strings occur at `0x9E3C` and `0x9E4C`.

**[CONFIRMED]** `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/onoff/main.lua` is 66,272 bytes, SHA-256 `41c0f3f2709c49d4a4f9b150b8c08c735515a9c50bbfbc2e4c36664d6466e698`. Function 28, lines 1116-1126, writes the request to IOC IPC channel 2 and returns empty. Function 23, lines 687-1055, decodes returned state, retry counter, and lock time; state mapping is at lines 921-953.

**[CONFIRMED]** `analysis_ra4_18.45.01/work/primary_iso/usr/share/V850/hs/cmcioc.bin` is 458,752 bytes, SHA-256 `c7bf247bfdb10b5dfda2802df1210671f6a1872140cdeebc014c109a9c77e012`, mapped `VA=file+0x10000`. Channel-2 dispatch reaches PIN-decision VA/file `0x25658/0x15658`; equality branch `0x256AE..0x256C2` changes distinct anti-theft state `GP-0x229A` and publication flags. Publisher `0x2AD6C/0x1AD6C` emits the state. Comparator contents, retry threshold, and lockout schedule remain intentionally out of scope.

**[CONFIRMED]** MainSupplement `AntiTheft::MessageHandler` begins at `0x2AC0C4`. The entered-PIN and VP2/VP3/VP4 checks followed by unlocked occur at `0x2AC1B8-0x2AC209`, then issue `xletsReturnToNew`; command construction is anchored at `0x2A9A76`.

### 3.1 xletsReturnToNew is destructive reset, not Developer Mode

**[CONFIRMED]** Native `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/bin/appManager` is 1,268,061 bytes, SHA-256 `608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591`.

- `parseRequest` compares `xletsReturnToNew` at file offset `0x5C460` (VA `0x15C460`).
- The equal branch reaches handler file offset `0x2AA7C` (VA `0x12AA7C`) through the call at `0x5C4A8`.
- The handler removes shared RMS records/files, RMS folders, Xlet installation folders, and `/fs/mmc1/resource` contents.
- Helper `0x12A95C` restores preinstalled Xlets, removes the AMS temporary folder, and calls reset helper `0x12A890`.

This is not Java lifecycle state NEW, marker rollback, or developer authorization. It is prohibited for activation and routine rollback.

**[CONFIRMED ONE-WAY EDGE]** A manufacturing handler at VA/file `0x6C388/0x5C388` requires proprietary authorization state 4 through getter `0x54228`, persists an authorized anti-theft comparator replacement, and copies it live at `0x6C446..0x6C452`. Thus state 4 can authorize comparator provisioning.

**[CONFIRMED BOUNDED ABSENCE]** The reverse does not exist in the complete direct xref/call inventory: the channel-2 dispatcher, PIN-decision/success branch, and publisher contain zero references to proprietary state `GP-0x7B38`, allowance `GP-0x7B34`, getter `0x54228`, or mutator `0x54180`. No HBC/HMI PIN-success callback reads or writes `service.cert`, `service_flags.eng_menu`, `AMS_DEVELOPMENT`, `enableEngMenu`, `developerId`, or a developer token. Factory anti-theft must remain byte-for-byte stock, but owner PIN success is proved not to be the Development Security gate.

## 4. Other similarly named controls are distinct

### 4.1 Native enableEngMenu

**[CONFIRMED]** Native AppManager function file offset `0x29E08` (VA `0x129E08`) tests `/fs/etfs/enableEngMenu` with mode 4. Its only located direct caller is `createEmbeddedApps` at file offset `0x3D1C0` (VA `0x13D1C0`), where it filters embedded application ID `engineering` (strings at `0x105C4C` and `0x105C58`). `appManager.cfg:84` supplies the embedded definition.

No writer was found in the materialized primary-plus-hidden corpus. This controls one embedded app, not the physical gesture, service certificate, `serviceMenu`, item 19, or AMS security configuration.

### 4.2 Delete Service Key item 20

**[CONFIRMED]** `AppsListEngServiceMenu::<cinit>` assigns `DELETE_SERVICE_KEY=20` at FWS `0x36C77-0x36C7C`; its label is at `0x370C4-0x370D6`. `onItem` selects case 20 at `0x37EF7-0x37F01` and enters its block at `0x37D11`.

The block constructs `file:///fs/etfs/service.key` at `0x37D17-0x37D24`, tests `.exists` at `0x37D3E-0x37D45`, and directly calls `.deleteFile()` at `0x37D59-0x37D61`. It makes no Peripheral, ModuleLink, D-Bus, SvcIPC, or platform-service call.

The verified platform path is `/etc/security/service.cert`; standard-boot inventory line 20 maps `/etc/security` to `/fs/mmc0`. `platform_troubleshoot.lua` function 5, lines 188-205, removes that configured certificate on invalidation. No recovered alias or call connects it to `/fs/etfs/service.key`.

Item 20 and platform certificate invalidation are **[CONFIRMED DISTINCT]**. The runtime consumer of `/fs/etfs/service.key`, if any, is **[UNKNOWN]**. Item 20 is not proved revocation of active `service.cert` and is not Development Security rollback.

Diagserv `0xF011` is a third, distinct internal deletion path for `/etc/security/service.cert`. Item 20 does not call it. `0xF011` does not call the evaluator, clear already-published `service_flags`, or notify the HMI, so immediate live revocation is not proved. Its external authorized invocation path, supported refresh boundary, and interruption/postcondition contract remain **[UNKNOWN]**.

## 5. AppManager -d is unregistered and ignored

**[CONFIRMED]** `boot.sh` assigns `disableDRMArg=-d` at lines 367 and 461 and passes it at lines 371 and 465. `platform_ams_restart.lua` lines 183-209 tests `/fs/etfs/disableDRM` and selects command text without or with `-d` (constants `0x1375/0x137A` and `0x13E0/0x13E5`).

**[CONFIRMED]** Native `appManager::processOptions` at VA `0x195FFC` creates the sole local Poco `OptionSet` at `0x196028` and registers only `silent/s`, `json/j`, `presub/p`, `watchdog/w`, `config/c`, `tp`, and `help/h`. It registers neither `drm` nor `d`. Single-dash lookup reaches `0x1DAA00`; no inherited/global set, clustering, or prefix route supplies the entry. The "unknown option ignored" diagnostic at file offset `0x11284C` is loaded at `0x196E00`.

A dormant normalized `drm` handler exists at `0x19718C` and calls setter `0x16D548`, but no option registration reaches it. DRM checker constructor `0x181318` initializes enable byte `+5` to 1 at `0x181338`. Install preparation calls checker `0x1801D4` at `0x1957A4`; enabled missing-grant state returns error `0x1B`.

For this exact binary, `-d` is ignored and DRM checking defaults enabled. It is not an alternate development control or a bypass. `/fs/etfs/disableDRM` is distinct from `/fs/etfs/AMS_DEVELOPMENT`.

## 6. AMS/Kona trust model

### 6.1 Production versus development security configuration

The canonical source artifacts are `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/security/security.jar` and `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/security/development/security.jar`.

| Property | Production | Development |
| --- | --- | --- |
| Path | `/fs/mmc1/kona/security/security.jar` | `/fs/mmc1/kona/security/development/security.jar` |
| Size | 7,504 bytes | 7,371 bytes |
| SHA-256 | `29a8a350ef0facc30c1c98e5250563a4020ad9c1a243f13e795e2e68e3bd74e7` | `fbe5314ab304e122162aae20ace46999b93832fc4c7451439f4ada430eccc8a7` |
| Visible revision | 13 | 17 |
| Primary signer | Chrysler UConnect Application CA | Xlet Developer |
| AMS mode | `-secure` | `-secure` |

**[CONFIRMED]** Both archives have 17 entries. `Device.class` and inspected policy resources are byte-identical, including `complete.policy` SHA-256 `82059f870a65e76465b1da1948e7eaed83cfbb2e3cc33dcef0ecd9a94980b71c` and `full.policy` SHA-256 `623e870a36dea05b9c5c33b16ccb68bf77a66675d008a2f6d46aa5e859bb2a14`. Visible functional difference is `security.properties` revision/comment data plus signer material.

**[CONFIRMED/PARTLY UNKNOWN]** Development selection changes the final promoted token/certificate verifier-key candidates from Chrysler+aicas to Xlet Developer+aicas, not visibly broader policy text. Whether revision and signer identity also change principal construction, application acceptance, or policy combination remains unrecovered.

`complete.policy` contains `AllPermission`; `full.policy` grants `AppMgrPermission("appMgr")` and `AppMgrPermission("chain")`. Presence does not prove every development-signed app receives them. No helper may request or assume these grants without proof.

### 6.2 cacerts is not proved application-signer trust

`analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/security/cacerts` has SHA-256 `2b931d5574d94c886a2ec13c3301585e405f2d68abf90fed3287383e55c7d0d0`. Its seven parsed certificate fingerprints do not equal embedded signer fingerprints in the two security JARs, and observed app signers do not establish a direct match.

**[UNKNOWN]** Complete AMS trust-anchor and chain-building rules. Adding a certificate to `cacerts`, replacing a security JAR, or treating this JKS as a simple allow-list is unsupported.

### 6.3 key.jar binds code and metadata

**[CONFIRMED]** Across 135 factory applications:

- all 78,756 regular executable-JAR members have matching companion-`key.jar` digest records;
- all 82,938 recomputed manifest entry digests match;
- all 137 full-manifest signature-file digests match;
- all 137 PKCS#7 signatures verify mathematically against their embedded signer certificate, without claiming trust-chain validation.

Signer-envelope counts are 123 Chrysler, 12 VP4, and two dual Accenture. No app `key.jar` carries the Xlet Developer certificate in the development security configuration.

`key.jar!/xlet.properties` is in the same signed envelope as executable-member digests. Installed external descriptors may rename app JARs, but the signed descriptor preserves the bound name. `key.jar` is the visible detached payload-and-metadata integrity envelope, not merely a certificate bundle.

**[CONFIRMED installed-launch association / UNKNOWN AOT details]** `Installer.getKeyJarFile` ignores its `Properties` argument and constructs the fixed sibling `<appId>/prog/jars/key.jar` at `0x5C05BE`. `AMSController.loadXlet` obtains payload and key paths at `0x5BB432/0x5BB43C`; `XletManager` checks key existence and converts it to a URL at `0x5C5FD9..0x5C5FF3`; and `VerificationClassLoader` stores it in `keyJar_`. Its signer lookup calls `getJarEntryCertificates(keyJar_,"xlet.properties")` at `0x5C2AFE..0x5C2B08`. Missing-key fallback uses primary-resource signers. The certificate extractor and `SigningKeys.verify(Object[])` are AOT/native-form, so exact runtime cross-JAR digest recomputation, chain ordering, revocation/time behavior, and final principal assignment remain unknown (`reports/keyjar_runtime_association.md`).

### 6.4 DRM.jar is separate entitlement

**[CONFIRMED]** Twenty-six KIM roots contain `DRM.jar`; all 26 manifest/signature envelopes verify mathematically. Embedded properties carry application/grant/provisioning state. `DRM.jar` does not replace `key.jar` payload integrity, and native DRM checking is enabled.

### 6.5 Developer token is package metadata, not PIN state

**[CONFIRMED]** Six installed descriptors contain `xlet.developerToken`; the same opaque value is present in signed `key.jar!/xlet.properties`, binding it to package metadata. The value is intentionally omitted.

**[CONFIRMED negative boundary]** A read-only census of 300 JARs, 163 signed JARs, Kona `cacerts`, and recovered standalone public-key structures produced 19 distinct SPKI identities: 17 RSA and two non-RSA, with 15 RSA keys compatible with the token's 256-byte decoded length. No recovered block yielded a valid PKCS#1 v1.5 or strict PSS structure. The exact bounded matrix made 418,320 comparisons: 30 compatible key/byte-order recoveries times 332 plausible package/identity/digest messages times six PKCS#1 v1.5 hashes plus all 36 PSS message-hash/MGF1-hash pairs. Every comparison failed and positive controls passed. This rules out those conventional signature interpretations; the AOT consumer below proves a different API shape and does not turn the probe into a credential recipe.

**[CONFIRMED ROM metadata and call graph]** `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/AMS` is 11,956,352 bytes, SHA-256 `96683b789ecf06a8575915d0b446b532e1f4ee87feb31d925cb7ba3d7d324d27`. Its tag-driven name/descriptor pool spans file `0x9C2071..0xAB8ECC`, contains 60,877 entries, and has inclusive-byte SHA-256 `3663f3ee68908e0625de021a53537f33264786fb350e54b8fd5614786ed888fb`. Exact entries include:

- `developerId` at `0xA72B3C`;
- `developerToken` at `0xA72B42`;
- `getDeveloperId` at `0xA78AE5`;
- `getDeveloperToken` at `0xA78AF0`;
- `verifyDeveloperKey` at `0xAA0296`;
- `xlet.developerToken` at `0xAA146C`.

The literal table (`0xAB8ED0..0xAD1E9C`), 28,142-record global member-selector table (`0xAD1EA0..0xB08E10`), and 4,599-entry class-pointer table (`0xB1BC48..0xB20424`) assign exact owners and bodies. `XletProperties.DEVELOPER_KEY_PROPERTY` resolves through CP#8/literal index `0x4924` to `xlet.developerToken`. `VerificationClassLoader.getDeveloperToken()String` loads that property at `0x5C2BF3..0x5C2BFA`.

Private `VerificationClassLoader.verify(Object[])` (`0x5C2AD1..0x5C2AEA`) passes developer and device tokens to `KeyVerifier.verifyAllCertificates`. That method (`0x5C1AE6..0x5C1AFF`) first calls `verifyDeveloperKey`; success returns immediately, while failure enters the device/certificate alternative. `verifyDeveloperKey` (`0x5C1B0A..0x5C1B25`) constructs `SignedId(token,SecurityParameter.getDeveloperId())` and verifies it against the final selected-security-JAR signing keys.

**[CONFIRMED token predicate]** `SignedId.decrypt(PublicKey)`, bytecode `0x5C2335..0x5C2364`, obtains `key.getAlgorithm()`, calls `Cipher.getInstance(algorithm)`, initializes decrypt mode with the public key, Base64-decodes the property, calls `doFinal`, and constructs a platform-default-charset `String`. `verify(PublicKey)`, `0x5C22F1..0x5C2326`, rejects null ID and accepts only `decrypted.equals(developerId)`; exceptions return false. `verify(PublicKey[])`, `0x5C22BC..0x5C22E6`, tries every key and returns on the first match. No explicit provider, transformation, padding, hash, Java `Signature`, PIN, nonce, time, IPC, or marker operand appears.

**[CONFIRMED JCE resolution]** RA4's embedded security resource places SunJCE at provider 4 (`0x899EDB`; provider block `[0x899E43,0x899FE5)`, SHA-256 `18e2f729eb57da4f2ed0abe2f6a4957ee845a21c6d53060c8a89e535f3893e9b`), while `SunJCE$1.run` registers `Cipher.RSA -> com.sun.crypto.provider.RSACipher`, supported mode `ECB`, and the padding set at `0x5E5CF7..0x5E5FE2`. Bare `RSA` produces null mode/padding fields in `Cipher.getTransforms` (`0x6E6FD0..0x6E70C7`), and `Cipher$Transform.setModePadding` skips both SPI setters (`0x6E81FC..0x6E821C`). The `RSACipher` constructor stores `PKCS1Padding` (`0x5E4F6F..0x5E4F8F`); public-key decrypt mode maps to internal `MODE_VERIFY`, selects PKCS#1 block type 1, performs the public RSA primitive, and unpads (`0x5E5123..0x5E53AF`). The exact conventional label is therefore `RSA/ECB/PKCS1Padding`, not OAEP or Java `Signature`. Full class bounds and slice hashes are in `reports/signedid_jce_semantics.md`.

**[CONFIRMED two-stage trust bootstrap]** `AMSController.<clinit>` reads certificates on `rom:/internal.jar!/xlet.security`, extracts their public keys, and stores `_internalKeys_` at `0x5BBC1C..0x5BBD1C`. The embedded JAR is pointer-bounded at AMS file `[0x988778,0x9892AD)`, 2,869 bytes, SHA-256 `2dbf7986c70e16d7bb047b897492c6ce164a1b5954837590708ee65b73759dab`; all manifest digests and both detached signatures verify. Its roots are an aicas DSA certificate (SHA-256 `9f28ad4b65f3eca46049b9f6abfb5c169b8c1ea35dde01380c689dbceab10d4c`) and aicas RSA certificate (`0654d97249cd24168cffbd7987ba6a05b76550dc95d765a9dafc59aaf11afe07`). A temporary VCL authenticates the selected production/development `security.jar` with those roots at `0x5BA8C2..0x5BA8D0`; selected-JAR `xlet.security` certificates are promoted at `0x5BA8F9..0x5BA940` into the final `SecurityParameter` at `0x5BA958..0x5BA965`. Production promotes Chrysler+aicas candidates; development promotes Xlet Developer+aicas. Kona `cacerts` is not the first-stage store.

`AMSController` obtains developer/device IDs by reflectively calling `com.aicas.xlet.manager.Device.getDeveloperId/getDeviceId`. An exhaustive 300-JAR census covered 88,666 entries and 72,507 decompressed classes, plus loose files, nested archives, and launch configuration. The only three `Device.class` copies are the same 481-byte getter-free stub, SHA-256 `a452ac3005bbf0bdf18c7dd6d8fed766f7d130524170b4cfbae037efb2edc6e8`; no class contains `getDeveloperId`. VCL inherits the system loader, but its system-visible Kona copy is the same stub and no stock classpath/boot overlay option exists. Recovered stock therefore returns null; only unrecovered live-unit mutable state remains a theoretical provider. No IPC/native/Java edge joins PIN success or item 19 to token creation.

**[CONFIRMED false-lead closure]** `verifyWithSeparateSigningKey` elsewhere in the same ROM name table is the standard Java `CrlRevocationChecker` method, corroborated by local diagnostics at AMS file offsets `0xA2BD2F`, `0xA2FDF1`, `0xA2FE69`, `0xA2FEC1`/`0xA2FF3E`, and `0xA2FF12`. It concerns PKIX CRL verification and is not evidence for RA4's detached `key.jar` format.

Boot launches `authenticationService` with stock configuration at `boot.sh:648-649`. Static evidence does not connect it to anti-theft, item 19, token issuance, or package verification. Its key material is not reproduced; startup proximity is not a call edge.

## 7. Application Manager and Xlet lifecycle

### 7.1 Permissioned API and native boundary

**[CONFIRMED]** Kona `AppManagerImpl` checks `AppMgrPermission("appMgr")` before SvcIPC service `com.harman.service.AppManager` operations:

| Operation | Class-file evidence |
| --- | --- |
| Install | code `0x2B28`; check `0x2B31`; operation/invoke `0x2B65/0x2B6C` |
| Uninstall | `0x2E8C`; check `0x2E95`; operation/invoke `0x2EBC/0x2EC3` |
| Start | `0x3565`; check `0x356E`; operation/invoke `0x35A7/0x35B0` |
| Pause | `0x36CB`; check `0x36D4`; operation/invoke `0x36FE/0x3706` |
| Stop | `0x3813`; check `0x381C`; operation/invoke `0x3846/0x384E` |

Native AppManager binds AMS service/object at file offsets `0x1156D0/0x1156EC`. Install preparation builds package-info with `auth:true` around VAs `0x19206C`, `0x1920F0`, `0x192878`, and `0x19288C`; `getPackageInfo` is at `0x1928C8`, wrapper call `0x192904`. AMS token-verifier ordering, exact SunJCE RSA predicate, internal bootstrap identities, security-configuration key promotion, fixed installed `key.jar` association, and signer-object source are direct. The remaining gaps are the AOT certificate-extraction/`SigningKeys` bodies, incoming external-package association, legitimate issuer/live ID state, and signer-to-principal/policy mapping.

### 7.2 Package shape

Factory KIM shape is confirmed:

    <KIM>/xlets/<appId>/prog/xlet.properties
    <KIM>/xlets/<appId>/prog/jars/<application>.jar
    <KIM>/xlets/<appId>/prog/jars/key.jar
    <KIM>/xlets/<appId>/prog/jars/magic.txt
    optional KIM-root DRM.jar and resources

`magic.txt` is consistently six-byte `HB_CMC`, SHA-256 `0ffe9823746d76b9fb74480676a68d052b3a11634f2dfe67bd9fe9c8f3cd1f80`, not a credential. Factory layout does not prove the live app JAR's outer schema.

Factory KIM copy semantics are now closed at the file-mutation layer. Recovered `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/bin/qkcp` is 50,222 bytes, SHA-256 `aa5605bdd69581aad74c05213553ccac2468399de18f539cf1c2029d58207198` (`inventory.tsv:120`). Its `-h` option creates/maps a 56-byte shared-memory progress record (`shm_open`, `ftruncate64(...,0x38)`, and `mmap64` at VAs `0x105A78..0x105AE8`); it is not manifest authentication. The KIM caller passes no `-f/-r` checkpoint pair and contains no `xletsdir_ref`/MD5 consumer. `qkcp` traverses with `nftw64`, writes/truncates each final destination directly, and imports no `rename`, `unlink`, `remove`, or `rmdir`. **[CONFIRMED]** Factory KIM copying is a monitored, non-atomic merge/overwrite that can leave partial or mixed destination state; it does not enforce the visible MD5/length records or provide rollback (`reports/qkcp_kim_copy_semantics.md`).

### 7.3 Confirmed authenticated USB app-media dispatcher

The normal-operation recognizer is now proved.

**[CONFIRMED]** `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/usr/bin/cmc/service/swdlMediaDetect/loader.lua` is 22,538 bytes, SHA-256 `f562650958dc487d8558571744cc517ba583550b29c79dba4f335fc07c47e885` (inventory line 223). It configures MCD rule `SWDL`, accepts `usb0`, mounts `/fs/usb0/swdl.upd` at `/fs/swdl`, authenticates nested ISOs, requires/mounts `installer.iso` at `/fs/installer`, and loads `etc/manifest.lua` (`loader.lua:70-80,497-568`).

**[CONFIRMED]** `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/usr/bin/cmc/service/swdlMediaDetect/swdlMediaDetect.lua` is 18,115 bytes, SHA-256 `0bf54e5866ad0a8bff467e592e5ee46d877ba957ee6f1f266f7d94191001088c`. `processManifest` dispatches `manifest.external.start_script` at lines 242-266. `loader.executeExternalScript` exports `ISO_PATH`, `USB_PATH`, and `INSTALLERISO_PATH`, then runs the signed-installer-selected script at `loader.lua:595-621`.

`analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/app-install/us-app-install.sh`, SHA-256 `9c199f28d595b61107a04d4e63a31d5f252302d4b3163f265819ce81dbc326bf`, invokes `analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/app-install/us-app-install.lua`, 7,754 bytes, SHA-256 `f3de29bef88d1a92fec3cf7e0c84c065eadc71ca898d9b674c6ff15b682ba7ec`:

- prototype 10, lines 325-352, walks `<ISO_PATH>/usr/share/APPS`;
- prototype 8, lines 265-298, stages at `/fs/mmc0/xlets/temp/<jar-filename>` and uses `auth=false` only for metadata-preview `getPackageInfo`;
- prototype 15, lines 382-445, enforces Kona compatibility, calls secure AMS `install` or `upgrade`, requires `status=ok`, and removes staging.

Install/upgrade does not carry `auth=false`; AMS remains `-secure`. Metadata preview is not authentication bypass.

**[STOP]** Stock manifest `analysis_ra4_18.45.01/work/installer_iso/etc/manifest.lua:230-237` has no `external` member. No factory external app manifest, `usr/share/APPS` sample, or complete live JAR exists in the corpus. Dispatcher is proved; authorized signed installer and exact live schema are not.

### 7.4 Other ingress and lifecycle

**[CONFIRMED]** KIM3 Application Manager stages `/fs/mmc1/download/<huFileName>`, verifies CRC32 transport integrity, optionally performs server-directed uninstall-first through `filesToDelete`, and calls Kona `installApp(appId,basename)`; `DeleteTask` calls `uninstallApp`. `BaseUpdateInstallTask` enables cleanup plus uninstall-first handling, while its Install/Update subclasses differ primarily in the current version sent to the server. CRC32 is not signer authorization.

**[CONFIRMED]** Native catalog `installApp` performs the authenticated `getPackageInfo` preflight, then `installNow` calls adapter file `0xEA84` from `0x91C40`. That adapter emits request key `uri` and exact AMS method `upgrade` at files `0xEAD4/0xEAD8` and `0xEB34/0xEB38`. Thus catalog fresh install and update converge on AMS `upgrade`; only the USB application script explicitly chooses AMS `install` for an absent app. Whether `upgrade` is implemented as a general upsert remains unknown.

**[CONFIRMED]** Signed full-update Apps unit at `installer_iso/etc/manifest.lua:113-126` uses Xlets installer, `secondary.iso:/usr/share/XLETS`, and destination `/fs/mmc1/`. It is broad factory population, not preferred development ingress.

**[CONFIRMED]** Native AppManager proves the per-app uninstall/cleanup chain through its recovered boundaries. The dispatcher recognizes `uninstallApp` at file offset `0x54058` (VA `0x154058`) and enters `startUninstallApp` at file offset `0x91158` (VA `0x191158`). That method validates the application ID and startup/pending state, stops a running application, and reaches `uninstallNow` at file offset `0x90FAC` (VA `0x190FAC`). Its call at `0x910B0` targets AMS adapter file `0xE854`, which emits request key `appId` at `0xE8DC/0xE8E0` and exact method `uninstall` at `0xE964/0xE968`. Successful asynchronous completion enters `onUninstalled` at file offset `0x8FE94` (VA `0x18FE94`), which queues `finishUninstallation`; the dispatcher at file offset `0x5CF74` calls its implementation at file offset `0x93910` (VA `0x193910`).

`finishUninstallation` calls `cleanUpXletResources` at file offset `0x3B0CC` (VA `0x13B0CC`) and queues `deleteAppFromHashMap`; the event loop at file offset `0x5C058` invokes deletion handlers at VAs `0x156DFC` and `0x133C4C`. Resource cleanup calls `removeRMSFiles` at file offset `0x31B94` (VA `0x131B94`), which removes `<xletRMSDir>/<appId>` recursively and `<xletRMSDir>/common/<appId>.rs`. The configured root is `/fs/etfs/usr/var/appman/xletRMS` at `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/etc/system/config/appManager.cfg:8-14`.

After cleanup, the dispatcher deletes the native-map entry, emits `appListUpdated`, and queues a complete `AppManager_JavaApps` JSON save through files `0x5C130..0x5C1C4`. This proves application-scoped resource/RMS/native-map/catalog cleanup, but not one atomic operation. AMS payload mutation, resource cleanup, map deletion, and QDB persistence are separate phases.

**[CONFIRMED]** `AppManager_JavaApps` is one whole-list PersistentKeyValue record (string file `0x101C54`), not a row per app. `readJavaAppsList` begins at VA `0x130050` / file `0x30050`. `saveJavaAppsList` begins at VA `0x157698` / file `0x57698`, performs separate `read` and `write` IPCs through `0x57704..0x577C0` and `0x58818..0x58858`, and is called only by dispatcher file `0x5C348`. No CAS, generation, transaction ID, or retry loop was found. Install queues this save only after AMS success/native finalization and `appListUpdated` (`0x91580..0x9160C`); uninstall queues it after cleanup and map deletion.

The default PersistentKeyValue rule (`pmem_keyvalue.ini:14-20`) routes this key to QDB `/usr/var/qdb/key_value` (`qdb.cfg:41-44`), table `keyvalueTbl(key TEXT PRIMARY KEY,value TEXT NOT NULL)`, with `journal_mode=truncate`. The `keyvalue` section has no backup directory; `qdb_recover.sh:21-22` deletes `key_value*` on detected corruption.

Jamaica class-object metadata assigns `install(String)Application` at file `0x5BFCC0`, `recoverProgIfNeeded(String)V` at `0x5BFDFD`, and `upgrade(String)Application` at `0x5BFE8C` directly to AMS `Installer`. `recoverProgIfNeeded` loads exact `prog.bak` at `0x5BFE1B` and `0x5BFEE3`; install/upgrade load the exact rename diagnostics at `0x5BFD56`, `0x5BFF2E`, and `0x5BFF5C`. Ownership is confirmed, while parent path, rename order, normal-upgrade invocation, commit/delete behavior, and crash guarantee remain **[UNKNOWN]** (`reports/appmanager_registry_atomicity.md`).

**[CONFIRMED]** Native post-install behavior is conditional, not an unconditional launch. `onInstalledSignal` (VA `0x1938A8`) reaches `finishInstall` (VA `0x1935BC`), which calls `autoStartApp` at file `0x93858`. That function starts only when `(DRM mAppLauncherMask bit 2 OR the stock super-app override) AND the global autostart gate`; mask load/test/extract occur at files `0x1BB38/0x1BB3C/0x1BB64`. Otherwise it reaches `INSTALLATION DONE` and success completion at `0x91A30/0x91A64` without calling App start.

An ordinary non-autostart app therefore remains stopped until a later explicit request. The stock human-facing route is now proved. ROV `AppsMainScreen.swf` (SHA-256 `5df0c52056d9495c439e8c90d1826be132f43bc7d4a61951acd4f1adfccbd04d`) handles the generic item selection in `onItem` (method/body/code `0x9F17/0xBDA0/0xBDA7`) and calls `IAppManager.startXlet(selected.appId,"MoreScreen")` at FWS `0xC1E6`. ROV `MainSupplement.swf` (SHA-256 `e9d796ea4b4c83ed518bfe3b3c341e54e510a1ae0f78ebbffbd655b7c36a3258`) implements module `AppManager.startXlet` at `0x1E7A0B/0x2A9712/0x2A971A`, emits `startApp` at `0x2A97E1`, and sends the AppManager JSON request at `0x2A97E7/0x2A9AF6`.

Native `parseRequest` compares that `startApp` at file `0x53DD0`, dispatches at `0x53DF0` to VA `0x14FDB0`, and calls `findAndStartApp` with DRM checking enabled at `0x50650/0x5066C`; the App start primitive is reached at `0x3C328`. The generic HMI path does not traverse the Java permission check. Java `AppManagerImpl.startApp` is a separate caller surface that independently proves its own permission check and SvcIPC boundary at class offsets `0x3565/0x356E/0x35A7/0x35B0`.

**[CONFIRMED bounded negative]** Native `parseRequest` spans VA `0x1516D4..0x156DFC` and has 56 constant method comparisons but no per-app enable/disable/launch operation. Full-file ASCII/case-insensitive/UTF-16LE scans find no `enableApp`, `disableApp`, or `launchApp`; the Java public API also has no enable/disable method. This bounds the recovered operation surfaces, while a hidden numeric-only or external suppression state remains possible.

| Lifecycle step | Current status |
| --- | --- |
| Discover/list/package info | **[HIGH]** client APIs exist; AppManager whole-list JSON/QDB catalog is confirmed, hidden AMS package registry remains unknown |
| Validate | **[PARTLY CONFIRMED]** key.jar/signer/descriptor/DRM/secure-AMS layers, fixed installed companion association, verifier order, two-stage signer-key bootstrap, and Base64/SunJCE `RSA/ECB/PKCS1Padding`/exact-ID developer-token predicate proved; AOT certificate extraction/SigningKeys, incoming-package association, legitimate issuer/live ID source, and principal mapping unknown |
| Install/upgrade | **[CONFIRMED]** stock USB calls AMS install/upgrade; catalog calls native installApp, which always converges on AMS upgrade |
| Uninstall/remove | **[CONFIRMED PARTIAL]** native flow stops a running app, performs asynchronous AMS completion, removes per-app RMS/resource state, deletes the native-map entry, and queues full-list QDB persistence; AMS payload deletion, exhaustive paths, and interruption recovery remain unknown |
| Start/pause/stop | **[CONFIRMED UI/module/native route plus API dispatch]** the generic Apps item route sends native `startApp`, which performs the DRM gate before AMS-facing start; separate permissioned Java methods cover start/pause/stop |
| Enable/disable | **[CONFIRMED bounded negative]** no explicit per-app operation exists in the recovered native parser or Java API; do not conflate this with launcher entitlement/global autostart |
| Post-install launch | **[CONFIRMED]** ordinary app completes stopped; only DRM launcher-mask bit 2/stock super-app override plus global gate autostarts it, otherwise the generic `AppsMainScreen` -> module `AppManager` -> native DRM-checked `startApp` route launches it |
| Persistence | **[CONFIRMED PARTIAL]** code under `/fs/mmc1/xletsdir`; RMS under `/fs/etfs/usr/var/appman/xletRMS`; native catalog in QDB `AppManager_JavaApps`; hidden AMS registry/reconciliation unknown |
| Atomicity/version rollback | **[CONFIRMED non-atomic visible boundary / UNKNOWN AMS recovery]** callback, resource, map, and QDB phases are separate; AMS `Installer.recoverProgIfNeeded` owns `prog.bak`, but no complete rename/restore contract is proved |

No trial may direct-copy into `xletsdir`, invoke raw `AMSClient`, or equate directory deletion with uninstall.

## 8. USB update trust and recovery boundary

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| Owner ZIP `Uconnect_VP4,18.45.01-My13-17.zip` | 1,266,203,571 | `5388d9310737dc52a65f2825131043362254b3592da2584302b81bc0447f9fdd` |
| `analysis_ra4_18.45.01/extracted/swdl.upd` | 1,426,147,328 | `c704eb723d6697fd98959888274dda18362c23ce6f66b505e01ce1983148c344` |
| `analysis_ra4_18.45.01/work/swdl_iso/installer.iso` | 34,830,624 | `893c1e9dbc16b42d3a0eba8f8470336ec84618d59980735a1e61a58499b830a5` |
| `analysis_ra4_18.45.01/work/swdl_iso/primary.iso` | 375,191,552 | `8086b7b6a413c9fd2718d21bd7d027c79c0dc36a1e1d43ea1f7358fd33b890ff` |
| `analysis_ra4_18.45.01/work/swdl_iso/secondary.iso` | 1,015,750,656 | `cd6df921c1da876cb5652f011bd3f1cc6a751a818b3455f478b4e1f7fc7edcb5` |

**[CONFIRMED]** PC-side MD5 is distribution convenience only. `analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/update/isochk.lua` is 9,509 bytes, SHA-256 `51b4777fa98e8a0f338336b2ebacd7cdccd9e1493817c76f3ef41cad33be2e9f`. Source/debug lines 170-392 parse a 32 KiB header, verify RSA/SHA-256 header material with `/etc/keys/swdl.pub`, enforce product/market/model/downgrade constraints, verify full ISO data hash/size, and validate install-monitor hash material.

**[CONFIRMED, independently verified]** The referenced public key is materialized at `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/etc/keys/swdl.pub` (451 bytes, SHA-256 `804e7cdf410c74a2b6ac52084d9b24c7b5becfd5bbb66a32819356d01f5b676e`; segment inventory line 53). Node's RSA-SHA256 verifier accepts block 0 as the signature over header bytes 256-32767 for all three nested ISOs. RSA public recovery of block 127 yields exactly the SHA-256 of each ISO data region from byte 32768 through EOF:

| ISO | Header signature | Signed data-region SHA-256 |
| --- | --- | --- |
| `installer.iso` | valid | `880561a00022ea658a211a76947abb2e2cef1882e64372c6209b3ec7ee7337c1` |
| `primary.iso` | valid | `fd5e4ab6409eb6e583c7ccf82d0a7be08980a8b081677efc32f0b0fe94dbe5c6` |
| `secondary.iso` | valid | `22468c3ba91c125559f6269c444a5c32fa437c08cac8d4b304f55e8ec5761898` |

This proves the stock header signatures and signed full-data hashes against the recovered public key. A public verification key cannot sign or authorize newly built media.

**[CONFIRMED]** The 13-unit manifest spans System, System Data, Apps, IOC, modem, XM, HD, OTA, and other units. It has resume/retry and narrow MMC Take Back preservation. No general A/B slot, per-unit undo log, or reverse sequence was found. Resume/retry is not rollback.

Unmodified OEM-signed stock update is last-resort recovery, contingent on exact-unit compatibility and authorized procedure. It is not routine app installation or transaction rollback and must never be repacked.

## 9. Smallest safe future design

The recommendation is conditional, not executable.

### 9.1 Preferred approach

**[DESIGN]** After every stop gate is closed:

1. Baseline a healthy, stationary, stably powered owner unit read-only.
2. Use only a legitimately issued, HU-specific, unexpired `service.cert` accepted by stock `scv`.
3. Use stock item 19 to create `AMS_DEVELOPMENT`; independently verify state.
4. Activate through normal boot; verify logged development JAR and `-secure`.
5. Install one inert, unique, least-privilege app through proved authenticated-media/secure-AMS using explicitly authorized signing/provisioning.
6. Verify identity, signer/principal, policy, no autostart/daemon, and normal vehicle/update function.
7. Use stock per-app uninstall; verify package, registry, RMS, resources, and app-owned data.
8. While legitimate service authorization remains, use item 19 to remove the marker; verify absence.
9. Normal boot and verify production JAR, `-secure`, stock apps, vehicle function, and update recognition.

If authorized production signing is available, production-signed app with marker absent is smaller because it avoids a global AMS configuration change.

### 9.2 Prohibited approaches

- Do not modify `cacerts`, either `security.jar`, launchers, boot scripts, AMS, AppManager, stock apps, or update artifacts.
- Do not use `xletsReturnToNew`; it destroys broad state.
- Do not toggle the marker by ad hoc shell/helper; preserve stock service-authorized item 19.
- Do not depend on `-d` or `disableDRM`; the option is ignored and checker enabled.
- Do not direct-copy into `xletsdir`, manipulate hidden registry, or use raw AMSClient.
- Do not reuse a stock token, certificate, key, signature envelope, or DRM grant.
- Do not request `AllPermission`, AppManager, arbitrary filesystem, vehicle-bus, firmware-update, or network-interface access for the first helper.
- Do not induce AMS crash or repack/forge `swdl.upd` or nested ISOs.

### 9.3 Hard stop gates

| Gate | Required proof |
| --- | --- |
| Ownership/bench | Documented owner authority; stationary unit; stable power; healthy input/display/boot |
| Baseline | Version, part number, apps, marker, selected JAR, update state, health captured |
| Service authorization | Legitimate HU-bound cert; `EngineeringMenu=1`; adequate validity; stock `scv` acceptance |
| Return window | Authorization remains for Production Security; deletion independently observable |
| Developer trust | Accepted signer/principal/token rule proved; authorized private signing path exists |
| Package format | Harmless reference from authorized tooling; every signed member/descriptor verified off-unit |
| Signed installer | Legitimate authenticated external manifest/installer; no self-signed/repacked ISO |
| Permission semantics | Global/per-app/signer/development policy combination proved and least privilege approved |
| Uninstall | Per-app removal demonstrated on disposable state including registry/RMS/resources/data |
| Recovery | Compatible unmodified OEM-signed stock media and authorized exact-unit recovery known |
| Git hygiene | No vendor artifact, decoded filesystem, credential, or derived binary staged |

Stop on package-info/install disagreement, unknown signer/policy, changed stock hashes, unexpected autostart, failed uninstall, expired return authorization, degraded boot, anti-theft enrollment, active update, or ambiguous persistent state.

## 10. Rollback and recovery

Routine rollback is application-scoped:

    stop custom app
      -> stock per-app uninstall
      -> verify package/registry/RMS/app-data removal
      -> stock item 19 removes AMS_DEVELOPMENT
      -> normal boot
      -> verify production security.jar and -secure
      -> verify stock apps, vehicle function, update recognition

**[CONFIRMED PARTIAL / STOP]** Native AppManager proves per-app RMS/resource cleanup, native-map deletion, and a later queued `AppManager_JavaApps` QDB-list save. Those steps are not atomic with AMS payload mutation, and `system()` results for tracked resource `rm`/`mv` operations are ignored before their vectors are cleared. Exhaustive app-owned-path deletion, AMS/QDB reconciliation, interruption recovery, and prior-version restoration remain unproved. The sequence therefore remains a design until stock uninstall is dynamically demonstrated on disposable test state.

`xletsReturnToNew` is excluded because it wipes factory app state. Item 20 is excluded because it deletes `/fs/etfs/service.key`, not proved active cert or development marker. Signed update is disaster recovery, not normal rollback. If state is ambiguous, stop and preserve evidence.

## 11. RA4 versus UAS 21.9

RA4 conclusions derive from the canonical owner ZIP, nested images, materialized installer/primary/secondary trees, reconstructed SWFs, and decoded QNX boot/HBC filesystems.

Local UAS 21.9 tree has 44 files totaling 1,077,907,214 bytes but lacks parent-package provenance. Its outer package has signed manifest/metadata, encrypted payloads, two detached signatures mathematically verified against embedded certificate, and nine declared payload hashes that recompute.

UAS application/HMI runtime remains encrypted. Its wrapper is materially different from RA4 `swdl.upd` plus authenticated nested ISOs. No UAS observation proves RA4 runtime behavior; no RA4 `second.ifs` handling may be projected to UAS; no payload/key/updater/recovery method may be adapted between platforms.

## 12. Highest-value unresolved questions

1. **[STOP]** What exact certificate extraction, chain ordering, revocation/time, and cache rules exist behind AOT `getJarEntryCertificates(URL,String)` and `SigningKeys.verify(Object[])`, and how are accepted signer principals combined with production/development policies? The installed `key.jar` path and `key.jar!/xlet.properties` signer-object association are now confirmed.
2. **[STOP]** What signer/private-key authority, runtime `developerId` provider, and token-issuance path is legitimately authorized for owner-developed RA4 apps? The exact SunJCE consumer predicate is proved; legitimate credential creation is not.
3. **[STOP]** Who legitimately issues/renews RA4 service certificates, establishes the required IOC diagnostic session and proprietary state 4, answers the protected challenge, and authorizes diagserv `0xF010`/`0xF011`? The IOC gate and allowance are proved; the external authority/workflow is not.
4. **[STOP]** What exact outer JAR schema is accepted below `usr/share/APPS`, and what authorized signed external manifest invokes it?
5. **[STOP]** What AMS registry/payload state exists beyond the confirmed AppManager whole-list QDB catalog, per-app RMS/common record, resource cleanup, and native-map update; what exact rename/restore contract does `Installer.recoverProgIfNeeded` implement; and how do boot reconciliation and interruption recovery behave?
6. **[UNKNOWN]** Does the target unit's native `getAppList` response expose a newly authorized helper with the intended name/icon/category, and does selecting it reproduce the statically proved generic Apps launch behavior? No downstream generic HMI `enabled`, `hidden`, or `suppressed` field was found, but upstream native omission remains possible.
7. **[UNKNOWN]** Does anything consume `/fs/etfs/service.key` or join it to `service.cert`?
8. **[UNKNOWN]** What writes `/fs/etfs/enableEngMenu`?
9. **[UNKNOWN]** Does an authorized unit supply a mutable system/boot overlay with the otherwise absent `Device` getters, and what exact certificate-array ordering/filtering reaches the now-resolved RSA verifier?
10. **[UNKNOWN]** What exact-unit recovery exists inside closed peripheral flashers after interruption?

None permits security weakening. Blocked work remains static, off-unit, and evidence-preserving.

## 13. Canonical report index

This master resolves cross-report claims at the highest proved level:

| Report | Authoritative role |
| --- | --- |
| `reports/corpus_inventory.md` | Artifact identities, provenance, duplicate and Git/vendor audit |
| `reports/qnx_boot_filesystems.md` | QNX multi-section recovery, HBC inventories, boot assets/services |
| `reports/service_certificate_diagnostic_transport.md` | IOC session/state-4/allowance gate, internal certificate staging/validation/removal, anti-theft directionality, and interruption hazards |
| `reports/authorization_bridge_deep_dive.md` | Gesture, serviceMenu, anti-theft backend, item 20, native gate, reset, restart bounds |
| `reports/developer_mode_ui.md` | HMI/AppsList engineering and Development Security offsets |
| `reports/developer_mode_control_flow.md` | Integrated separation of development, anti-theft, and startup |
| `reports/anti_theft_auth_flow.md` | Keypad -> gateway -> onOff -> IOC -> state -> reset |
| `reports/ams_development_flag.md` | Marker actors, census, persistence |
| `reports/ams_startup_chain.md` | Boot, AppManager, JVM/AMS, supervisor |
| `reports/security_jar_diff.md` | Production/development JAR byte comparison |
| `reports/developer_token_analysis.md` | Redacted token census, Jamaica metadata schema, exact AMS property/verifier call graph, and runtime identity-provider blocker |
| `reports/signedid_jce_semantics.md` | ROMized provider order, bare-RSA resolution, RSACipher defaults, and public-decrypt/type-1 semantics |
| `reports/kona_trust_model.md` | cacerts/signers and trust limits |
| `reports/keyjar_runtime_association.md` | Fixed installed key.jar ownership, loader propagation, signer-entry association, and verifier ordering |
| `reports/kona_application_authorization.md` | key.jar/DRM verification, permissions, native boundary, definitive `-d` result |
| `reports/application_install_pipeline.md` | USB/KIM ingress, package, lifecycle, persistence/registry gaps |
| `reports/app_launch_ui_path.md` | Generic Apps catalog/item event, HMI module command, native DRM-checked launch, and bounded caller census |
| `reports/appmanager_registry_atomicity.md` | AppManager JavaApps QDB registry, lifecycle ordering, non-atomic resource handling, AMS backup bounds |
| `reports/qkcp_kim_copy_semantics.md` | Factory KIM copier provenance, progress option, non-atomic failure and checkpoint bounds |
| `reports/usb_update_pipeline.md` | USB detector, ISO authentication, update/recovery limits |
| `reports/minimal_change_design.md` | Conditional least-change design and stop gates |
| `reports/rollback_recovery.md` | Return plan, failure checkpoints, recovery boundary |
| `reports/uas_comparison.md` | Strictly separated UAS wrapper evidence |

All current reports now use the exhaustive launch, token, persistence, and IOC-domain conclusions: AppManager `-d` is unregistered and ignored while DRM remains enabled; an ordinary non-autostart install finishes without launch; the generic Apps route sends native DRM-checked `startApp`; and no explicit per-app enable/disable operation exists. `VerificationClassLoader` directly loads `xlet.developerToken`; `SignedId` Base64-decodes it, and RA4's SunJCE path applies `RSA/ECB/PKCS1Padding` public-decrypt/internal-verify/type-1 semantics with the selected-security-JAR RSA key promoted through an internal-root bootstrap, then requires exact runtime `developerId` equality before the device/certificate fallback. The recovered stock corpus has no usable ID provider. Catalog install converges on AMS `upgrade`, per-app uninstall reaches AMS `uninstall`, and `Installer.recoverProgIfNeeded` owns `prog.bak`; the visible lifecycle remains non-atomic. IOC proprietary state 4 gates both F010/F011 and protected anti-theft comparator provisioning, but successful PIN authentication has no reverse edge to state 4, its finite allowance, service authorization, marker state, or developer credentials.

## 14. Repository and evidence safety

Firmware extraction and hidden-filesystem trees are research inputs and must remain ignored/untracked as vendor material. Only original documentation, diagrams, metadata, hashes, original tooling, patches/deltas, and owner-created source may be committed.

Before every commit:

1. run `git diff --cached --name-only`;
2. inspect every staged path and blob type;
3. verify no archive, ISO, update image, executable, JAR, SWF, certificate, key, token, decoded filesystem, or decompiled vendor source is staged;
4. record exactly: **Stock/vendor firmware staged: NO**.

Current verification state: `unittest` discovery passes all 47 original-tool tests (six QNX imagefs, 22 Jamaica metadata-decoder, and 19 developer-token probe tests); the Jamaica CLI reproduction accepts the documented hexadecimal bounds and recovers the cited pool/property/member anchors.

Current implementation state: **analysis/design only; no firmware modification, no flash, no anti-theft bypass, no on-unit application installation.**
