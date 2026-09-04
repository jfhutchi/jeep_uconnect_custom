# RA4 18.45.01 minimal-change development and application design

## Status and safety boundary

This is a design for a possible future, owner-authorized implementation. It is not an instruction to modify or flash a head unit now. It does not derive, bypass, brute-force, disable, or short-circuit the factory anti-theft PIN, service-certificate verification, application-signature verification, or software-update signatures.

The central correction is important: the recovered RA4 code does not implement the originally hypothesized chain `anti-theft PIN -> developer authorization`. It implements separate controls. A safe design must preserve that separation rather than manufacture a connection that the stock system does not have.

Evidence grades in this report are:

- `CONFIRMED`: directly present in the named stock artifact.
- `HIGH`: supported by several artifacts, with a remaining native/runtime boundary.
- `DESIGN`: proposed future behavior; not yet executed or proved on hardware.
- `STOP`: a condition that must be resolved before any on-unit mutation.

No stock archive, executable, JAR, certificate, key, ISO, or decoded filesystem belongs in Git. No raw developer-token value is reproduced here.

## Corrected factory control model

The smallest defensible design starts from the recovered control flow relevant to the Development Security item. It is not an inventory of every engineering-related control in AppManager:

```text
driver-temperature up + down held for 5 seconds
  -> ICS hard-key event engineerMode                         CONFIRMED
  -> engineering menu                                       CONFIRMED

legitimate SERVICEKEY media event
  -> candidate service.cert copied by stock platform code   CONFIRMED
  -> RSA verification with stock public key                 CONFIRMED
  -> HUSerialNumber must match this head unit                CONFIRMED
  -> date / ignition-cycle limit must remain valid           CONFIRMED
  -> EngineeringMenu=1 becomes service_flags.eng_menu        CONFIRMED
  -> Service item becomes reachable                          CONFIRMED

Service item -> Development Security item 19
  -> create or delete /fs/etfs/AMS_DEVELOPMENT               CONFIRMED
  -> no immediate AMS restart or policy reload               CONFIRMED absence in writer

next execution of /fs/mmc0/app/bin/jvm.sh
  -> marker absent: production security.jar                  CONFIRMED
  -> marker present: development/security.jar                CONFIRMED
  -> AMS still starts with -secure in both cases              CONFIRMED

authorized application medium / package
  -> stock metadata preview                                  CONFIRMED
  -> secure AMS install or upgrade                           CONFIRMED API boundary
  -> signed descriptor, code, and requested policy           CONFIRMED package binding
  -> signer/developer-token acceptance                       UNKNOWN native decision
```

The physical event is recovered in `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/vehicle/icsHardKeys.lua` (31,153 bytes, SHA-256 `86aba0d0c5fbfdeb9d5da36edd66c81e3e76cf16744740d9778612f41a7a1ea5`). Functions 32 and 33, source/debug lines 652-683, start a 5,000 ms timer for the two driver-temperature buttons; function 11, lines 237-279, emits `{key="engineerMode", pressed=true}` when both saved states are set. `MainSupplement.swf` receives that key in `ICS::messageHandler` at reconstructed FWS offset `0x2A728C` and dispatches `ICSEvent.ENGINEERING_MODE` at `0x2A73FB`-`0x2A7409`.

The service authorization is recovered in `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/platform_troubleshoot.lua` (13,931 bytes, SHA-256 `8beab38ab164479a9fd815116dbfa02a48e3fa661724fa9c4273dc5884a1ba45`). Function 11, lines 406-427, registers the `SERVICEKEY` event; its nested function, lines 408-422, copies `service.cert` and calls the evaluator. Function 7, lines 255-304, invokes `/fs/mmc0/app/security/scv`, uses `/etc/keys/serv_cert_key.pem`, compares the parsed `HUSerialNumber` with `/fs/fram/serialnumber`, checks validity, and emits the flags. Function 2, lines 63-127, maps `EngineeringMenu=1` to `service_flags.eng_menu=true`; function 6, lines 214-248, enforces date and ignition-cycle limits; function 5, lines 188-205, clears flags and removes an invalid service file.

The verifier `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/security/scv` is 1,596,550 bytes with SHA-256 `08bb7992d95b27b98bcb222021015cda152eef9fafa573720845d28c837c7fe1`. The recovered `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/etc/keys/serv_cert_key.pem` is a 451-byte, 2,048-bit RSA public key with SHA-256 `07e7a63fd528cdd4b4d23bc6aaac03adda4ca9659d0b4a86ddd5d26b8608831e`. These are verification artifacts, not credentials that permit issuance. A legitimate certificate still requires the corresponding authorized issuer.

In `AppsListScreen.swf`, `AppsListEngMenuScreen::<iinit>` exposes Service only when `Peripheral.versionInfo.serviceMenu` is true (`0x3030C`-`0x30333`). `AppsListEngServiceMenu::<cinit>` assigns Development Security item ID 19 at `0x36C69`-`0x36C6E`. `AppsListEngServiceMenu::DevepSecurityKeyEnabled`, reconstructed FWS offset `0x3899D`, creates the absent marker with `File.createTempFile()` plus `moveTo(target,true)` at `0x389DC`-`0x38A21`, or deletes the present marker at `0x38A55`-`0x38A5C`. The method contains no PIN callback, token request, restart, or AppManager call.

`analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/jvm.sh` is 2,795 bytes with SHA-256 `9bd3c63a2c22c17f96e037102283f453afca43eb093bc1291d607a9805f829ec`. Lines 58-59 select the production or development JAR, line 61 logs the choice, and line 63 launches AMS with the selected `-securityConfiguration` and unconditional `-secure`. The HBC supervisor `platform_ams_restart.lua` (7,514 bytes, SHA-256 `264e5aaa6e2e09e8bb86a881f4919a66220d1cad2c7ce9443416e5d35f9f720f`) reinvokes `jvm.sh` after AMS loss or startup timeout, but contains no `AMS_DEVELOPMENT` watcher. A normal, controlled boot is therefore the least ambiguous activation point; deliberately killing AMS is not part of this design.

The recovered `analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/files/bin/boot.sh` is 29,268 bytes with SHA-256 `c801d473b0b49e8242114635f4022cc67ccbe03093fec188de3b7188dd636ecf`. Its two initial AppManager branches assign `disableDRMArg=-d` at lines 367 and 461 and pass it at lines 371 and 465. The restart supervisor separately tests `/fs/etfs/disableDRM` when choosing AppManager command text. Native `appManager` analysis does not establish a functioning `-d` control: `main` at VA `0x197CB0` calls `processOptions` at `0x195FFC`, whose option set at `0x196028` registers `silent/s`, `json/j`, `presub/p`, `watchdog/w`, `config/c`, `tp`, and `help/h`, but not `drm/d`. A later normalized `drm` handler exists at `0x19718C`, with no located registration that can reach it. The observed `-d` may therefore be ignored or reach only dead/indirect code. Regardless, this boot/restart command-line artifact is separate from the AMS security-JAR selector, and the design neither changes nor relies on it.

A fourth, separate engineering-related gate exists in native AppManager. Function file offset `0x29E08` (VA `0x129E08`) tests `/fs/etfs/enableEngMenu`; its only direct branch-and-link caller is `createEmbeddedApps` at file offset `0x3D1C0` (VA `0x13D1C0`), where it filters embedded application ID `engineering`. No writer was found in the materialized primary-plus-hidden corpus. This embedded-application catalog gate is not `service.cert`, `Peripheral.versionInfo.serviceMenu`, item 19, or `/fs/etfs/AMS_DEVELOPMENT`, and the proposed design does not change it.

## Anti-theft is preserved, not repurposed

`CONFIRMED`: the hard-key engineering route does not test anti-theft state. In `icsHardKeys.lua`, anti-theft state gates volume and audio-power handlers, not the two driver-temperature handlers, the five-second timer, or `processICS`.

`CONFIRMED`: the anti-theft keypad is a different asynchronous path. The HMI sends `checkAntiTheftPIN`; `hmiGateway` routes `Dest=AntiTheft` to `com.harman.service.onOff`; `onoff/main.lua` function 28, source/debug lines 1116-1126, writes the four supplied bytes to IOC IPC channel 2 and returns without a local comparison. Later IOC state supplies locked, wait-for-VIN, enter-PIN, wrong-PIN, unlocked, counter, and lock-time state.

`DESIGN`: the future application path must not call, wrap, monitor, derive from, or alter the anti-theft PIN flow. Normal vehicle anti-theft behavior stays byte-for-byte stock. Owner authorization for research is administrative; it is not evidence that the factory PIN is a development credential.

This also means the phrase "preserve the factory PIN gate" has a precise implementation meaning: leave the factory anti-theft gate and its IOC protocol untouched. It must not be described as the gate for Development Security because the recovered firmware does not use it that way.

## Candidate approaches

### Approach A - stock service authorization plus authorized developer package (recommended)

Use a legitimately issued, head-unit-specific, unexpired `service.cert` through an authorized stock provisioning route to make the stock Service menu reachable. Use stock item 19 to select the already-shipped development security configuration. At the next normal AMS start, use a package signed by an explicitly authorized developer identity and install it through the stock live application path.

Advantages:

- reuses every located factory authorization and trust boundary;
- bounds the intended platform changes to a stock-copied service certificate, the stock-managed ETFS marker, and AMS-managed staging, registry, package, and app-data state for one application;
- leaves both security JARs, `cacerts`, boot scripts, AMS, AppManager, signed firmware/update artifacts, and stock system/update code unchanged, while necessarily adding AMS-managed application state under `/fs/mmc1`;
- keeps AMS `-secure` active;
- exposes the stock item-19 marker-deletion operation as the candidate production-security return path, contingent on valid service authorization, independently verified deletion, and a later verified AMS start.

Limit: this is not actionable until the native acceptance rule for the development signer/token and the live-package schema are proved, an authorized issuer supplies stock-valid external installer media, authorized application credentials exist, the confirmed native per-app uninstall path is dynamically validated for the chosen package and its postconditions, and valid service authorization is available for both enablement and return. Internal diagserv staging/removal routines are now proved, but their external tester/IOC route and required diagnostic session/SecurityAccess state are not; no service-certificate issuance/reissuance or external-installer issuance process is currently proved.

### Approach B - authorized production-signed application without Development Security

If the owner can obtain normal production application signing/provisioning, keep `/fs/etfs/AMS_DEVELOPMENT` absent and install through the same stock live path. This is technically even smaller because it avoids a global AMS mode change.

Limit: the owner does not presently have a proved production signer/DRM provisioning path or legitimately issued external installer medium. Production `key.jar` signer reuse and the stock SWDL public verification key do not confer signing authority.

### Approach C - complete signed software update

Use an OEM-authorized, correctly signed update package to add or restore application content through the `Apps` manifest unit.

This is not recommended for routine development. It crosses many more failure domains, writes multiple system and peripheral units, and has resume/retry rather than a proved transaction rollback. It remains a recovery mechanism of last resort, not the preferred application installer.

The design rejects certificate-store edits, modified `security.jar`, direct copies into `/fs/mmc1/xletsdir`, a forged or repacked `swdl.upd`, manipulation of `/fs/etfs/disableDRM`, raw AMSClient experimentation, and intentional use of `xletsReturnToNew`.

## Trust and package requirements

The stock package evidence requires more than a JAR containing classes.

Across 135 factory applications, every executable JAR member is covered by a digest record in its companion `key.jar`; 82,938 of 82,938 digest records recomputed, all 137 full-manifest digests in signature files matched, and all 137 PKCS#7 signatures verified against their embedded signer certificate. `key.jar!/xlet.properties` is in the same signed envelope. See `reports/kona_application_authorization.md` for the complete census.

`CONFIRMED`: six token-bearing applications also place `xlet.developerToken` in signed `key.jar!/xlet.properties`. The normalized value is package-static across two Tweddle application IDs, Base64-decodes to 256 bytes, and has redacted decoded-value SHA-256 `126a6126acb7832b1385e3caa9db7c6e78340acb92d020fabe4c86193b5f1045`. AMS loads it through `VerificationClassLoader`; `SignedId` Base64-decodes it, and RA4's ROMized JCE resolves the RSA candidate to SunJCE `RSA/ECB/PKCS1Padding`, public-decrypt/internal-verify mode, and type-1 unpadding before exact equality with `developerId`. Immutable `rom:/internal.jar` signer keys authenticate the selected security JAR before that second-stage key promotion. An exhaustive 300-JAR/72,507-class census found no usable reflected ID provider. A live-unit overlay, legitimate issuer workflow, and policy assignment remain stop gates. The stock token must not be copied, reused, guessed, or generated.

`CONFIRMED`: production and development security JARs contain byte-identical policy files and `Device.class`. Production JAR SHA-256 is `29a8a350ef0facc30c1c98e5250563a4020ad9c1a243f13e795e2e68e3bd74e7`; development JAR SHA-256 is `fbe5314ab304e122162aae20ace46999b93832fc4c7451439f4ada430eccc8a7`. Their visible semantic differences are security revision 13 versus 17 and the primary signer identity (Chrysler UConnect Application CA versus Xlet Developer). Development behavior therefore likely depends on native interpretation of signer/revision, not a visibly broader policy text. That interpretation is still `UNKNOWN`.

`CONFIRMED`: `full.policy` SHA-256 `623e870a36dea05b9c5c33b16ccb68bf77a66675d008a2f6d46aa5e859bb2a14` grants `AppMgrPermission("appMgr")` and `AppMgrPermission("chain")`; `complete.policy` grants `AllPermission`. In `kona.jar`, `MethodPermission.checkPermission()` calls the active `SecurityManager`; `AppManagerImpl.installApp`, `uninstallApp`, `startApp`, `pauseApp`, and `stopApp` each construct/check `AppMgrPermission("appMgr")` before SvcIPC.

`DESIGN`: the first custom application must not be an installer or privileged package manager. The stock installer should perform installation. The application must request only the permissions needed for its narrow purpose, must not request `AllPermission`, AppManager control, arbitrary filesystem write, vehicle-bus access, firmware-update control, or network-interface access unless each permission is separately justified and its runtime combination semantics are proved. It must not autostart or run as a daemon in the first trial. It must use a new application ID and write only to its own assigned data area.

A legitimately provisioned developer credential must be embedded in the signed descriptor and must decrypt under one of the selected security configuration's promoted signer keys to the runtime `developerId`. No issuer, issuance process, private complementary operation, live ID provider, or effective permission mapping is proved. The enumerated v1.5/PSS interpretations remain a bounded negative and must not be replaced with guessed padding or a home-grown credential. The token is not created by entering the anti-theft PIN or by enabling the marker.

## Preferred live-install boundary

The stock application-media installer is the narrowest located candidate ingress, not an operationally proved end-to-end delivery surface. Its resident normal-runtime recognizer and environment supplier are now confirmed. `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/usr/bin/cmc/service/swdlMediaDetect/loader.lua` (22,538 bytes, SHA-256 `f562650958dc487d8558571744cc517ba583550b29c79dba4f335fc07c47e885`) configures media rule `SWDL`, expects `/fs/usb0/swdl.upd`, mounts the outer image at `/fs/swdl`, authenticates each present nested ISO, requires and mounts `installer.iso` at `/fs/installer`, and loads its `etc/manifest.lua` (`loader.lua:70-80,497-568`).

`analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/usr/bin/cmc/service/swdlMediaDetect/swdlMediaDetect.lua` (18,115 bytes, SHA-256 `0bf54e5866ad0a8bff467e592e5ee46d877ba957ee6f1f266f7d94191001088c`) reads `manifest.external.start_script` from that authenticated installer manifest and passes the relative script path to `loader.executeExternalScript` instead of entering the normal full-update confirmation/reset path (`swdlMediaDetect.lua:242-266`). The loader exports `ISO_PATH=/fs/swdl`, sets `USB_PATH` to the detected USB mount, exports `INSTALLERISO_PATH=/fs/installer`, and then executes the selected script from the authenticated installer ISO (`loader.lua:595-621`). This closes the former recognizer and `ISO_PATH`-supplier gaps.

Fresh off-unit verification with the recovered SWDL public key succeeds for all three stock nested images: each RSA-SHA256 block-0 signature verifies over header bytes 256-32,767, and RSA public-decryption of block 127 returns the 32-byte SHA-256 of bytes 32,768 through EOF. The matched data hashes are installer `880561a00022ea658a211a76947abb2e2cef1882e64372c6209b3ec7ee7337c1`, primary `fd5e4ab6409eb6e583c7ccf82d0a7be08980a8b081677efc32f0b0fe94dbe5c6`, and secondary `22468c3ba91c125559f6269c444a5c32fa437c08cac8d4b304f55e8ec5761898`. This validates the recovered authentication model and these stock artifacts only; it neither supplies a signing private key nor authorizes new external media.

`analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/app-install/us-app-install.sh` (SHA-256 `9c199f28d595b61107a04d4e63a31d5f252302d4b3163f265819ce81dbc326bf`) resides in the authenticated installer image, requires the exported `ISO_PATH` and `USB_PATH`, and invokes `us-app-install.lua` with those paths. This establishes the compatible external-script environment for the application wrapper, but the corpus has no external manifest sample proving the exact `external.start_script` value that factory application media uses to select it. In `us-app-install.lua` (7,754 bytes, SHA-256 `f3de29bef88d1a92fec3cf7e0c84c065eadc71ca898d9b674c6ff15b682ba7ec`):

- prototype 10, source/debug lines 325-352, discovers JARs under `usr/share/APPS` and queries properties/package information;
- prototype 8, lines 265-298, stages an offered JAR under `/fs/mmc0/xlets/temp` and performs two `getPackageInfo` calls with `auth=false`;
- prototype 15, lines 382-445, checks Kona compatibility, calls secure AMS `install` or `upgrade`, requires `status=ok`, and removes the staging file.

The `auth=false` field is confined to metadata preview. The subsequent install/upgrade call does not pass it, and AMS is launched with `-secure`. This design must never relabel metadata preview as an authentication bypass.

`STOP`: stock 18.45.01 `installer_iso/etc/manifest.lua:230-237` has a normal `parts` table and no `external` member, and the corpus has no factory external-install manifest or sample `usr/share/APPS` live-install package. Factory KIM directory layout is not proof of the live outer-JAR schema. A future trial requires a legitimately issued installer ISO whose valid stock signature/hash covers an approved `external.start_script`, plus official/authorized tooling or a legitimately produced reference application package that proves the accepted container, descriptor normalization, companion `key.jar` placement, signer principal, developer-token requirement, and DRM requirement. The recovered `segment_001a0000/files/etc/keys/swdl.pub` is a 451-byte, 2,048-bit RSA public key with SHA-256 `804e7cdf410c74a2b6ac52084d9b24c7b5becfd5bbb66a32819356d01f5b676e`; it can verify but cannot fabricate or authorize a new installer signature. Do not edit/repack the stock full-update manifest or substitute an unsigned external installer.

Factory KIM population is not an alternative narrow installer or rollback path. Recovered `qkcp -h` uses shared memory only for progress; KIM supplies no checkpoint/recovery flags, and the copier directly merges/truncates final destinations without an atomic rename or restore path. A failed factory Apps-unit copy can leave mixed Xlet/preload state (`reports/qkcp_kim_copy_semantics.md`).

## Confirmed per-app uninstall boundary

`CONFIRMED`: native AppManager (SHA-256 `608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591`) dispatches `uninstallApp` at file offset `0x54058` (VA `0x154058`) to `startUninstallApp` at VA `0x191158` (file `0x91158`). That function stops a non-stopped application when needed and proceeds through `uninstallNow` at VA `0x190FAC` (file `0x90FAC`). Successful asynchronous completion enters `onUninstalled` at VA `0x18FE94` (file `0x8FE94`), queues `finishUninstallation`, and the dispatcher at file `0x5CF74` invokes the finish routine at VA `0x193910` (file `0x93910`).

The finish path calls `cleanUpXletResources` at VA `0x13B0CC` (file `0x3B0CC`) and queues `deleteAppFromHashMap`; the event loop at file `0x5C058` invokes handlers at VAs `0x156DFC` and `0x133C4C`. `cleanUpXletResources` calls `removeRMSFiles` at VA `0x131B94` (file `0x31B94`). With `xletRMSDir=/fs/etfs/usr/var/appman/xletRMS`, the stock function deletes `/fs/etfs/usr/var/appman/xletRMS/<appId>` using `rm -R` and `/fs/etfs/usr/var/appman/xletRMS/common/<appId>.rs` using `rm` when those targets exist. After map deletion the dispatcher emits `appListUpdated` and queues a complete `AppManager_JavaApps` save through files `0x5C130..0x5C1C4`.

This proves a scoped per-application cleanup path for Xlet resources, the native application map, the AppManager persistent catalog, the app-specific RMS directory, and the common per-app RMS record. It does **not** prove AMS payload deletion, atomicity across those asynchronous stages, a safe resume point after interruption, cleanup of every possible application-owned path, or restoration of a previous version. The future design still requires dynamic postcondition checks and must never issue the recovered `rm` commands directly.

## Confirmed registry and interruption boundary

`CONFIRMED`: `AppManager_JavaApps` (string file `0x101C54`) is one whole-list JSON value in PersistentKeyValue, not one row per app. `readJavaAppsList` begins at VA `0x130050` / file `0x30050`. `saveJavaAppsList` begins at VA `0x157698` / file `0x57698`, performs a separate `read` through `0x57704..0x577C0`, rebuilds the list from the native map, and performs a separate `write` through `0x58818..0x58858`; dispatcher file `0x5C348` is its sole direct caller. No CAS, generation, transaction ID, or retry loop was found.

`CONFIRMED`: the default PersistentKeyValue rule stores this key in QDB `/usr/var/qdb/key_value` (`pmem_keyvalue.ini:14-20`; `qdb.cfg:41-44`), table `keyvalueTbl(key TEXT PRIMARY KEY,value TEXT NOT NULL)`, using `journal_mode=truncate`. The key-value section has no backup directory, and `qdb_recover.sh:21-22` deletes `key_value*` after detected corruption. Install queues the full-list save only after AMS success/native finalization and `appListUpdated` (`0x91580..0x9160C`); uninstall queues it after AMS completion, cleanup, and map deletion. Those layers can diverge after interruption.

`CONFIRMED OWNERSHIP / UNKNOWN RECOVERY SEMANTICS`: AMS class-object metadata assigns `install(String)Application` at file `0x5BFCC0`, `recoverProgIfNeeded(String)V` at `0x5BFDFD`, and `upgrade(String)Application` at `0x5BFE8C` to `Installer`. The recovery method loads exact `prog.bak` at `0x5BFE1B` and `0x5BFEE3`; install/upgrade load their exact rename diagnostics at `0x5BFD56`, `0x5BFF2E`, and `0x5BFF5C`. The normal-upgrade trigger, parent path, exact restore/delete order, completeness, and crash behavior remain unknown. AppManager's tracked resource `rm` and `mv` calls at files `0x8DE6C/0x8DFC8` also ignore the shell result before clearing their vectors. See `reports/appmanager_registry_atomicity.md`.

## Confirmed start boundary

`CONFIRMED`: native installation completion calls conditional `autoStartApp`. An ordinary app without DRM launcher-mask bit 2 or the stock super-app override reaches successful `INSTALLATION DONE` at native files `0x91A30/0x91A64` without calling App start. Its later explicit stock launch route is ROV `AppsMainScreen.onItem` (method/body/code `0x9F17/0xBDA0/0xBDA7`) calling `IAppManager.startXlet(selected.appId,"MoreScreen")` at FWS `0xC1E6`; module `AppManager.startXlet` in `MainSupplement.swf` (`0x1E7A0B/0x2A9712/0x2A971A`) emits `startApp` at `0x2A97E1` and sends it at `0x2A97E7/0x2A9AF6`. Native dispatch at files `0x53DD0/0x53DF0` then calls `findAndStartApp` with DRM checking enabled. This generic HMI route does not traverse Java `AppMgrPermission`; the separate Java `AppManagerImpl.startApp` API checks `AppMgrPermission("appMgr")` and invokes SvcIPC at class offsets `0x3565/0x356E/0x35A7/0x35B0`.

`CONFIRMED bounded negative`: neither the complete native 56-method parser census nor the Java public AppManager API contains a per-app enable/disable operation. The global `/fs/etfs/No_AutoStart_App` gate and DRM launcher entitlement are not substitutes for one. The stock UI caller is no longer a stop gate. Remaining launch validation is dynamic: confirm the target unit returns the newly authorized helper through `getAppList` with the intended name/icon/category and that selecting it follows the recovered generic Apps route. Native AppManager may still suppress an entry upstream even though no downstream generic HMI `enabled`, `hidden`, or `suppressed` field was found.

## Hard preconditions and stop gates

Every item in this table is mandatory. Failure means stop before mutation.

| Gate | Required proof | Why it is mandatory |
| --- | --- | --- |
| Ownership and bench safety | Documented owner authorization, stationary bench/test vehicle, stable power, known-good display/input and normal boot | Prevents a research failure from becoming a vehicle-safety event |
| Stock baseline | Read-only version, part number, installed-app inventory, marker state, AMS selection, update-state, and health capture | Defines the state to which rollback must return |
| Service authorization | Legitimately issued `service.cert`, correct HU serial, `EngineeringMenu=1`, adequate date/ignition validity, stock `scv` acceptance | The public key verifies; it cannot issue a certificate |
| Return access | Prove the same authorized session remains available long enough to select Enable Production Security, and independently observe marker removal | The UI can update its label even when marker creation fails; service authorization also expires |
| Developer trust | Prove the exact accepted developer signer/principal and whether `xlet.developerToken` is required; possess an explicitly authorized private signing path | Stock developer certificate presence is not possession of its private key or proof of app acceptance |
| External installer media | Obtain a legitimately issued nested installer ISO whose stock-valid signature/hash covers an approved `external.start_script`; verify resident loader acceptance off-unit where possible | The resident recognizer is known, but the stock public key cannot sign, and the 18.45.01 full-update manifest has no `external` member |
| Package format | Produce a harmless reference package with official/authorized tooling and independently verify every signed member and descriptor field off-unit | The live package schema is presently unknown |
| Permission semantics | Prove how global policy, signed per-app policy, signer principal, and development mode combine; approve a least-privilege policy | `full.policy` and `complete.policy` are too broad as unexplained defaults |
| Uninstall | Dynamically validate the confirmed native per-app path for the new app ID on disposable test state; verify AMS/package state, process/native catalog, stock-owned `AppManager_JavaApps` view, both known RMS targets, and every package-documented data path | Static cleanup/persistence ordering is scoped but non-atomic; AMS payload deletion, interruption recovery, exhaustive ownership, and prior-version restoration remain unknown |
| Recovery media | Preserve an unmodified, compatible, OEM-signed stock update and its published/local hashes; verify media before the trial | Signed update is a candidate last-resort recovery layer, contingent on exact-unit acceptance and an authorized procedure, not an excuse to omit app rollback |
| Repository hygiene | `git diff --cached --name-only` contains no stock/vendor artifact, key, token, ISO, JAR, SWF, binary, or decoded filesystem | Prevents vendor redistribution and credential leakage |

Additional stop conditions:

- Do not continue if the unit is already in an update, retry, anti-theft enrollment, or degraded boot state.
- Do not continue if `/fs/etfs/disableDRM` state changes or if any step would depend on it.
- Do not continue if the development JAR or stock launcher hash differs from the recorded 18.45.01 baseline.
- Do not continue if the harmless package requests unreviewed permissions, daemon/autostart behavior, or access outside its own data boundary.
- Do not continue if AMS package-info and install results disagree on app ID, version, signer, compatibility, or policy.
- Do not continue if the confirmed stock per-app uninstall path cannot be demonstrated for the chosen package, its known cleanup postconditions cannot be observed, or removal would require a global reset.

## Future staged implementation

This sequence is a design, not authorization to execute it now.

### Stage 0 - off-unit proof

Build only an original, inert proof application. It should display a version/health indicator, perform no vehicle control, install no other package, make no network connection, and persist only a small canary in its own data directory. Produce its signed descriptor and detached content envelope through the authorized signing path. Independently recompute the package member digests and signature chain before it is ever placed on media.

### Stage 1 - read-only baseline and rollback rehearsal

Capture the stock hashes and states named above. Rehearse the no-mutation abort path and verify access to legitimate recovery media. Confirm the service certificate's remaining time/ignition-cycle window covers enable, test, uninstall, production return, and verification with margin.

### Stage 2 - stock development selection

Present the legitimate service certificate through the stock `SERVICEKEY` path, verify `service_flags.eng_menu`, and reach the Service menu through the stock hard-key event. Use item 19 once. Independently verify that `/fs/etfs/AMS_DEVELOPMENT` now exists; do not trust the displayed label alone. Do not touch `/fs/etfs/disableDRM`.

Do not substitute a raw call to diagserv routine `0xF010`. Although stock Lua proves that the internal routine can stage `/etc/security/service.cert` and invoke the same platform evaluator, its external diagnostic authorization gate is unknown and its active-file write is non-atomic: initial staging truncates with `w+b`, open failure can receive the same internal acknowledgment as success, and there is no temporary-file/rename/fsync/backup transaction. It becomes an eligible route only if an authorized service organization supplies the official tester workflow and the upstream session/security requirements are independently proved.

Perform a normal, controlled head-unit boot while stationary and on stable power. Verify the line-61 `jvm.sh` diagnostic or equivalent read-only process evidence shows the stock development JAR and verify AMS still runs with `-secure`. Do not induce an AMS crash to force selection.

### Stage 3 - stock live install

The resident SWDL recognizer, nested-installer authentication, manifest dispatcher, and `ISO_PATH`/`USB_PATH`/`INSTALLERISO_PATH` handoff are confirmed and need not be treated as missing. Proceed only with a legitimately issued external installer medium accepted by the stock signature/hash checks and with a live application package whose complete schema and authorized signer have already passed the stop gates. The stock 18.45.01 full-update medium is not that sample: its manifest has no `external` member and its outer image has no demonstrated sample application JAR. Use the resident application-media path instead of repacking full firmware or invoking services directly. Require metadata preview to match the approved application ID, version, Kona range, signer identity, and policy. Allow stock AMS to make the authenticated install decision. Treat every response other than explicit success as failure. Do not retry blindly after an ambiguous result: compare AMS/package state, native catalog state, and the stock-owned `AppManager_JavaApps` view first because their confirmed update phases are not atomic.

### Stage 4 - bounded validation

First verify the successful install left the inert, non-autostart proof app stopped, as the recovered native rule predicts. Launch only from the generic stock Apps entry whose static route is now proved, after dynamically confirming that the target unit's `getAppList` exposes the approved helper with the expected metadata and that selection reaches the native DRM-checked `startApp` transition. Verify normal radio, climate display, audio, anti-theft state, update-service readiness, and AppManager/AMS health before exercising the proof application's single function. Keep the unit stationary. Do not test factory PIN failure/lockout as part of developer validation.

### Stage 5 - normal removal and production return

After the stop/uninstall semantics have been dynamically demonstrated as required by the uninstall gate, stop and request removal of only the new application through the stock per-app boundary. Verify it is absent from AMS package information, installed Xlet inventory, the native/Apps catalog, the stock-owned `AppManager_JavaApps` view, running Xlets, `/fs/etfs/usr/var/appman/xletRMS/<appId>`, `/fs/etfs/usr/var/appman/xletRMS/common/<appId>.rs`, and every additional package-documented data area; a returned status alone is insufficient. Do not edit QDB or payload directories directly and do not infer atomic completion or prior-version restoration from those deletions. While the legitimate service authorization is still valid, select Enable Production Security through item 19 and independently verify the marker is absent. Perform another normal controlled boot and verify `jvm.sh` selected the stock production JAR with `-secure`.

Only after production state and normal functionality are verified should the service authorization be allowed to expire or be removed through a separately proved stock mechanism. Item 20 is now statically complete, but it is not that mechanism: `AppsListEngServiceMenu::onItem` case 20 (`0x37D11`-`0x37D75`) constructs `file:///fs/etfs/service.key`, tests `.exists`, and calls `File.deleteFile()` directly at `0x37D59`-`0x37D61`, with no Peripheral, ModuleLink, D-Bus, or platform-service call. The platform certificate is separately configured as `/etc/security/service.cert`, resolving under `/fs/mmc0`; no filesystem alias, runtime relationship, or revocation edge joins it to `/fs/etfs/service.key`. Therefore this design does not prescribe `DELETE_SERVICE_KEY` as service-certificate rollback.

Diagserv routine `0xF011` is a confirmed internal remover for `/etc/security/service.cert`, but it is not prescribed here either. The external authorized route is unproved, its local handler performs direct removal without a transactional backup, and item 20 does not call it. It also does not clear the platform's already-published `service_flags` or notify the HMI, so persistent deletion is not proof of immediate live revocation. A future rollback may use it only through a documented, owner-authorized factory service workflow whose external gate, refresh boundary, and postconditions have been proved.

## Invariants that must remain true

The future implementation is acceptable only while all of these invariants hold:

1. The anti-theft PIN implementation, IOC protocol, retry counter, lock-time state, and HMI callbacks are unchanged.
2. Stock `security.jar`, development `security.jar`, `cacerts`, `serv_cert_key.pem`, `scv`, `jvm.sh`, AMS, AppManager, boot scripts, and update public keys are unchanged.
3. AMS runs with `-secure` in both production and development selection.
4. `/fs/etfs/disableDRM` is neither created, deleted, nor used as a prerequisite.
5. `/fs/etfs/enableEngMenu` is unchanged and is not treated as a substitute for service authorization or Development Security.
6. Planned state changes are limited to the stock-managed service certificate and `AMS_DEVELOPMENT` marker plus AMS-managed staging, registry, package, data, and ordinary diagnostic state for the one custom application; no other persistent mutation is permitted.
7. The first application has no daemon/autostart behavior and no application-management or firmware-update capability.
8. Production security is restored and verified before any normal firmware update.
9. The original OEM-signed update remains usable; no custom file is inserted into or substituted for its signed ISO contents.
10. Logs and project reports contain hashes and metadata only, never a raw developer token, private key, anti-theft PIN, or reusable authentication key.

## Why this is the smallest safe design

Approach A is designed around one factory-provided authorization surface, one stock ETFS marker selector, one ordinary AMS start, one securely installed application, and one intended per-app removal. Each operational step remains contingent on the stop gates and dynamic proof above. It does not modify system code or globally add trust. The candidate production return uses the stock marker-deletion operation only while valid service authorization and independent state verification are available, then verifies selection after a normal boot.

The design remains conditional because the most security-critical link is unresolved: which native principal/key rule accepts a developer package and how development selection changes that rule. Until that is proved with authorized credentials, the correct implementation is no implementation. A modified trust store, copied vendor token, disabled check, or full-firmware repack would be larger, less reversible, and contrary to the recovered factory model.

## Evidence references

- `reports/qnx_boot_filesystems.md` - recovered HBC filesystems, service-certificate chain, boot and restart evidence.
- `reports/service_certificate_diagnostic_transport.md` - internal diagserv staging/validation/removal graph, platform-verifier boundary, upstream-authentication unknowns, and interruption hazards.
- `reports/authorization_bridge_deep_dive.md` - hard-key producer, service flag, anti-theft receiver, `xletsReturnToNew`, and separation matrix.
- `reports/developer_mode_ui.md` - item 19 and exact marker create/delete bytecode.
- `reports/ams_startup_chain.md` - complete `jvm.sh` arguments and stock artifact identities.
- `reports/security_jar_diff.md` - byte-level production/development security-bundle comparison.
- `reports/kona_application_authorization.md` - detached package-signature chain, developer-token binding, permissions, and AppManager boundary.
- `reports/application_install_pipeline.md` - live app media, KIM installation, lifecycle, and unresolved atomicity.
- `reports/app_launch_ui_path.md` - generic Apps item flow, HMI module envelope, native DRM-checked launch, and bounded caller census.
- `reports/appmanager_registry_atomicity.md` - AppManager whole-list QDB catalog, lifecycle ordering, interruption windows, and AMS backup bounds.
- `reports/usb_update_pipeline.md` - signed update authentication, ordered update state machine, and rollback limits.

## Repository safety

Before every future commit, verify:

```text
Stock/vendor firmware staged: NO
Secrets or raw developer token staged: NO
```

Only original reports, parsers/tests, diagrams, and original application source or independently authored package metadata are eligible to commit. The legitimate service certificate, even when owner-specific, should be treated as operational authentication material and kept out of Git.
