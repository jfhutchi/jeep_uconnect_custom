# RA4 18.45.01 Application Install and Xlet Lifecycle

## Scope and method

This report reconstructs the stock RA4 application path from the canonical 18.45.01 extraction. It is a static analysis only: no vendor binary was executed, no archive or ISO was unpacked again, no install package was built, and no stock file was changed. Most evidence is from the already-materialized trees, including the ignored read-only HBC IFS extractions identified by their parent offsets and decoded-image hashes. The canonical-tree requirement comes from `reports/corpus_inventory.md:62`; the current KIM/Xlet corpus counts are recorded at `reports/corpus_inventory.md:162`.

Confidence labels mean:

- **[CONFIRMED]** Directly encoded in a stock script, property file, archive member, manifest, binary string, or reproducible hash/digest calculation.
- **[HIGH]** Several independent artifacts support the conclusion, but the complete runtime call path is not statically visible.
- **[INFERRED]** The conclusion best fits the visible evidence but has a plausible alternative.
- **[UNKNOWN]** The canonical extraction does not prove the behavior.

## Reconstructed path

The best-supported end-to-end model is:

```text
factory software update                         live application delivery
secondary.iso/KIM package                      mounted app ISO or catalog download
        |                                                   |
        v                                                   v
xlets.lua selects part-number KIM               stage under /fs/mmc0/xlets/temp
and qkcp copies factory tree                    or /fs/mmc1/download
        |                                                   |
        |                                                   v
        |                                      metadata/version preview
        |                                                   |
        |                                                   v
        |                                      secure AMS/Kona install/upgrade
        |                                                   |
        +------------------------+--------------------------+
                                 |
                                 v
             /fs/mmc1/xletsdir/xlets/<appId>/prog/...
                 plus AMS-owned package/index state
                                 |
                                 v
               xlet.properties selects JAR, main class,
                 policy and lifecycle metadata; DRM
                       supplies launcher entitlement
                                 |
                                 v
                    AMS/native install finalization
                                 |
                    +------------+-------------+
                    |                          |
                    v                          v
       entitled conditional autostart     ordinary app remains
          (plus global gate)                   stopped
                    |                          |
                    |                          v
                    |               later permissioned startApp
                    +------------+-------------+
                                 |
                                 v
                       running -> pause/stop/destroy
```

**[CONFIRMED]** `/fs/mmc1/xletsdir` is the AMS installation root. The stock startup script selects the production security bundle unless `/fs/etfs/AMS_DEVELOPMENT` exists, then launches `AMS` with `-installationDirectory /fs/mmc1/xletsdir`, the Kona extension/library/data directories, `ams_initializer.jar`, and `-secure` (`analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/jvm.sh:58-63`, SHA-256 `9bd3c63a2c22c17f96e037102283f453afca43eb093bc1291d607a9805f829ec`).

**[CONFIRMED / BOUNDED]** AMS maintains package/filesystem state in addition to the visible directory tree, and native AppManager separately persists its Java-application catalog as the whole-value `AppManager_JavaApps` JSON record through PersistentKeyValue into QDB `/usr/var/qdb/key_value`. The AppManager key, schema, and lifecycle ordering are now recovered; AMS's own internal package registry and its reconciliation with AppManager remain **[UNKNOWN]**. The layers are not one visible atomic transaction (`reports/appmanager_registry_atomicity.md`).

## Ingress A: stock application media installer

**[CONFIRMED]** The normal-runtime dispatcher is now recovered from the decoded QNX HBC image. `swdlMediaDetect/loader.lua` sets media rule `SWDL`, expects `/fs/usb0/swdl.upd`, mounts that image at `/fs/swdl`, authenticates every present nested `installer.iso`/`primary.iso`/`secondary.iso`, requires `installer.iso`, mounts it at `/fs/installer`, and loads `/fs/installer/etc/manifest.lua` (`analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/usr/bin/cmc/service/swdlMediaDetect/loader.lua:70-80,497-568`; 22,538 bytes; SHA-256 `f562650958dc487d8558571744cc517ba583550b29c79dba4f335fc07c47e885`; inventory line 223). `swdlMediaDetect.lua::processManifest` treats `manifest.external.start_script` as an external installer, unregisters the normal Software Update service, and passes that relative script to `loader.executeExternalScript` (`.../swdlMediaDetect.lua:242-266`; 18,115 bytes; SHA-256 `0bf54e5866ad0a8bff467e592e5ee46d877ba957ee6f1f266f7d94191001088c`; inventory line 228). The loader then exports `ISO_PATH=/fs/swdl`, `USB_PATH=<detected USB mount>`, and `INSTALLERISO_PATH=/fs/installer`, and executes the selected script from the authenticated installer ISO (`loader.lua:595-621`).

**[CONFIRMED]** `us-app-install.sh` requires both `ISO_PATH` and `USB_PATH`, prefers tools and libraries from the mounted ISO, and invokes the stripped Lua 5.1 installer with those two arguments (`analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/app-install/us-app-install.sh:4-29`, SHA-256 `9c199f28d595b61107a04d4e63a31d5f252302d4b3163f265819ce81dbc326bf`). The stock 18.45.01 `manifest.lua` has a normal `parts` table and no `external` member (`analysis_ra4_18.45.01/work/installer_iso/etc/manifest.lua:230-237`), so this particular full-update medium does not demonstrate the external manifest that selects `us-app-install.sh`.

Static disassembly of `analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/app-install/us-app-install.lua` (7,754 bytes, SHA-256 `f3de29bef88d1a92fec3cf7e0c84c065eadc71ca898d9b674c6ff15b682ba7ec`) establishes the following path:

1. **[CONFIRMED]** The main prototype (embedded source-line metadata 458-501) validates exactly two directory arguments, registers `SoftwareInstaller`, and waits for/subscribes to AMS. Exact raw string starts are `com.harman.service.SoftwareInstaller` at file offset `0x28E`, `com.aicas.xlet.manager.AMS` at `0x2B8`, `/var/kona/xletslib/Kona.jar` at `0x2D8`, `/fs/mmc0/xlets` at `0x2F9`, `/temp` at `0x30D`, `/user` at `0x318`, `factory` at `0x323`, and `usr/share/APPS` at `0x330`.
2. **[CONFIRMED]** Prototype 10 (source-line metadata 325-352) walks per-application directories under `<ISO_PATH>/usr/share/APPS`, locates JARs, calls AMS `getAllProperties`, and queries the installed `Kona.jar` package version. The raw `getAllProperties` and `getPackageInfo` strings occur at `0x1484` and `0x14b0`.
3. **[CONFIRMED]** Prototype 8 (source-line metadata 265-298) captures parent directory in Lua register R0 and JAR filename in R1 with `/([^/]+)/([^/]+%.jar)$`, then copies the offered JAR with the stock `cp` command into `/fs/mmc0/xlets/temp/<jar-filename>` (instruction records `0x0F27..0x0F53` concatenate the temp root, `/`, and R1). It calls `getPackageInfo` for the staged file URI with `auth=false` (`0x0F73..0x0FA3`), queries the installed application ID with `auth=false` (`0x0FBB..0x0FEB`), and publishes `updateMediaAvailable`.
4. **[CONFIRMED]** Prototype 15 (source-line metadata 382-445) compares the package's `kona.minimum.version` and `kona.maximum.version`. It calls AMS `install` when there is no installed package (`0x176c-0x1798`) or `upgrade` when one exists (`0x17a0-0x17cc`), requires returned status `ok`, and removes the staged file (`0x1850-0x1864`).

**[HIGH]** `auth=false` is a metadata-preview option for the two `getPackageInfo` calls, not a demonstrated signature bypass. The actual `install` and `upgrade` requests do not pass that flag, and AMS itself is launched in secure mode. No stock validation was modified or disabled during this analysis.

**[CONFIRMED]** `USB_PATH` comes from the media path delivered by `mcd.notify("SWDL", inserted)`, while application JARs are read from the mounted outer `swdl.upd` at `<ISO_PATH>/usr/share/APPS`. The signed nested installer ISO controls which external script is executed: `authenticateISO` verifies its header signature with `/etc/keys/swdl.pub`, copies it to `/fs/mmc0/installer.iso`, recovers and compares its signed data hash, and only then is its manifest loaded (`loader.lua:250-428,519-565`). **[UNKNOWN]** No external-install `manifest.lua` sample or live application JAR exists in this corpus, so the exact `external.start_script` value used by factory application media and the complete live JAR schema remain unproved. The local public verification key cannot authorize a newly built installer ISO.

## Ingress B: KIM3 Application Manager

**[CONFIRMED]** KIM3 contains a normal Xlet named `Application Manager`, app ID `c1d77320-6335-48b2-aa22-21912f657311`, main class `com.tweddle.updatemanager.UpdateManagerXlet`, version `1.0.4825`, with `security.policy`, `full.policy`, write permission, pause support, and `xlet.daemon=false` (`analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages/KIM3/xlets/c1d77320-6335-48b2-aa22-21912f657311/prog/xlet.properties:3-19`, file SHA-256 `cf1ad2e4326821d334dd591a48d29ac30d886d9730844865655749278f8a53ff`).

Its application JAR is `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages/KIM3/xlets/c1d77320-6335-48b2-aa22-21912f657311/prog/jars/c1d77320-6335-48b2-aa22-21912f657311.jar`, 836,379 bytes with SHA-256 `bcc4b7de1c7aad3c683c2831ef7f9d2b79e557d2c8bf1a2c6d2b7c252bc187d9`. Its detached envelope is `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages/KIM3/xlets/c1d77320-6335-48b2-aa22-21912f657311/prog/jars/key.jar`, 39,080 bytes with SHA-256 `13a2d3c861e6b02f61b1c86e5770b8766e64489604fc66e06b4daed7b4852202`.

Read-only classfile inspection provides the application-side install sequence:

- **[CONFIRMED]** `com/tweddle/updatemanager/util/InstallHelper.class` (10,442 bytes, entry SHA-256 `1210b6d0eb6d780429854b9d9e80b7e1a4f30e26b1482f7efe50e3073a637cb9`) contains `/fs/mmc1/download` at class offset `0x0cbb`, `prepareInstaller` at `0x0421`, cleanup logic at `0x05f6`, download retry/success diagnostics, delete-before-install logic, and `java/util/zip/CRC32` at `0x118a`.
- **[CONFIRMED]** `InstallHelper$InstallerImpl.class` (2,469 bytes, entry SHA-256 `efcffd495cdf9726371dfdf48e2f4235961a7e839d358a2f574d1797e1f4a121`) has constant-pool entries for Kona AppManager, `uninstallApp` at `0x063c`, `installApp` at `0x0664`, and AppNotFound handling.
- **[CONFIRMED]** `BaseUpdateInstallTask.class` (entry SHA-256 `8c6fc4b04d99052185ba2ada6b66a6286a0ce0d3e59cd5a9fbc696b34ccbfc6d`) calls the prepare/download/install helpers. `DeleteTask.class` (entry SHA-256 `a26276f2a1e035843b1ec3bcdbac248796c3519d6f1db2e55c390ca9174e5d69`) invokes `uninstallApp`.

**[CONFIRMED]** `InstallHelper.prepareInstaller` (method record/code `0x1D21/0x1D37`) builds `/fs/mmc1/download/<huFileName>`, retries `SocketTimeoutException` at most three times with a 20,000 ms delay, parses the expected CRC, and can mark the operation uninstall-first when the server's `filesToDelete` contains the current app ID. `writeFile` (record/code `0x22E5/0x22FB`) streams through `CheckedOutputStream` plus `CRC32` and calls `CRCHelper.checkCRC`. `UpdateAppDataResponseModel` maps `crc`, `huFileName`, `downloadUrl`, and `filesToDelete` to `data/update/files/file/crc`, `data/update/files/file/hu-url`, `data/update/files/file/server-url`, and `data/update/files-to-delete`.

**[CONFIRMED]** `BaseUpdateInstallTask.doInBackground` (record/code `0x101F/0x1035`) calls `prepareInstaller(appId,params,listener,true,true)`, enabling downloaded-file cleanup and server-directed uninstall-first behavior. `InstallTask` reports current version `0.0.1`; `UpdateTask` reads the installed version outside emulator mode; both converge on `InstallerImpl.install` (record/code `0x7ED/0x803`). That method optionally invokes `uninstallApp(appId)`, tolerating only `AppNotFoundException`, then calls `installApp(appId,jarFile.getName())` at class offsets `0x881..0x88D`. Passing only the basename proves that native AppManager resolves the artifact against its fixed download directory.

**[HIGH]** This is the catalog/network application path: transfer is staged in `/fs/mmc1/download`, checked with CRC32 for transport corruption, then handed to Kona AppManager. CRC32 is not a signer check. The later secure AMS/Kona package-validation layer is a separate control. The catalog's install/update distinction changes the version submitted to its server and whether server metadata requests uninstall-first; both operations use the same native `installApp` route.

## Factory KIM population during a software update

**[CONFIRMED]** The main software-update manifest defines an `Apps` unit sourced from `secondary.iso`, using installer `xlets`, source `usr/share/XLETS`, destination `/fs/mmc1/`, and pre-install cleanup config `etc/xlets_mmc1_preinstall.txt` (`analysis_ra4_18.45.01/work/installer_iso/etc/manifest.lua:113-126`, SHA-256 `104d18836f41919f1f789110697eebc5e6deee998de79fb5a4c0af35a042770f`). The cleanup removes the legacy `/fs/mmc1/kona/extension/kona-fiat-permissions.jar` and `/fs/mmc1/kona/data/DRM.jar` (`analysis_ra4_18.45.01/work/secondary_iso/etc/xlets_mmc1_preinstall.txt:18-20`, SHA-256 `97cab785a51b949b71bfc8d255776233e97db80c895758725b2a8dbf0aec12b3`).

**[CONFIRMED]** `kim_pkg_map.lua` maps head-unit part numbers to KIM selections, with KIM0 explicitly meaning no KIM package (`analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages/kim_pkg_map.lua:2`, examples at lines 14 and 290-294; SHA-256 `4f219f18f84afe346f68844fb8f618a031eeb49aa158ba7c81d4de83fb381daa`).

Static disassembly of `analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/update/installer/xlets.lua` (8,006 bytes, SHA-256 `e6849b1260417cdc89762ae76cac1b0f01bab28a833d2211b80498ae0d4466cc`) shows:

- **[CONFIRMED]** It reads `/dev/fram/partnumber` (raw string offset `0x0109`), loads `kim_pkg_map.lua` (`0x0f20`), and defaults to KIM0 when there is no selection.
- **[CONFIRMED]** It builds a base tree, removes from the working Xlet tree applications already present in preload, clears the preload Xlet area, and uses `qkcp` to copy the base package.
- **[CONFIRMED]** For non-KIM0 systems it invokes `qkcp -h` for the selected KIM's preload/resources and copies selected Xlets into `<destination>/xletsdir/xlets` (instruction records `0x1221-0x14d5`). A failed working-tree copy returns false (`0x1581-0x1599`). KIM0 instead clears `/fs/mmc1/xletsdir/xlets/*` and `/fs/mmc1/kona/preload` (`0x1675-0x16f5`). It finishes with recursive mode `550`; the raw `chmod -R 550` string is at `0x1f1c`.

**[CONFIRMED]** KIM copy manifests contain MD5, byte length, and absolute destination triples. For example, KIM1 lines 5-12 describe the Slacker application JAR, `key.jar`, `magic.txt`, and `xlet.properties` under both `/fs/mmc1/xletsdir/xlets/...` and `/fs/mmc1/kona/preload/xlets/...` (`analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages/KIM1/xlets/xletsdir_ref.txt:5-12`, SHA-256 `448608f2ff928807be2ab062b45481601d86725f50e04fdb83be3b495ba17cd5`). KIM3 lines 18-25 do the same for Application Manager (`analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages/KIM3/xlets/xletsdir_ref.txt:18-25`, SHA-256 `474a0df6b2623d4d026c86c2ee27a4f21a5444a705def53784cd9ebd0d872466`).

**[CONFIRMED]** Hidden-HBC recovery identifies `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/bin/qkcp`, 50,222 bytes, SHA-256 `aa5605bdd69581aad74c05213553ccac2468399de18f539cf1c2029d58207198` (`inventory.tsv:120`). Its `-h` option creates a 56-byte shared-memory progress object; it is not a hash-manifest option. The KIM caller passes no checkpoint/recovery option, and neither the caller nor `qkcp` consumes `xletsdir_ref.txt`. Native copy flow writes/truncates the final destination directly and imports no `rename`, `unlink`, `remove`, or `rmdir`, so a failure can leave mixed or partial destination state. The complete offset-level proof is in `reports/qkcp_kim_copy_semantics.md`.

## Observed package formats

| Delivery context | Confirmed format and metadata | Limit |
|---|---|---|
| USB application medium | Normal-runtime `swdlMediaDetect` mounts `swdl.upd`, authenticates and mounts nested `installer.iso`, loads its manifest, and can execute `manifest.external.start_script`; `us-app-install.lua` then expects JARs below `<ISO_PATH>/usr/share/APPS/<application-directory>/`, stages each JAR, and passes its `file:` URI to AMS `getPackageInfo` and `install`/`upgrade`. | **[UNKNOWN]** The stock full-update manifest has no `external` member and the corpus contains no `usr/share/APPS` sample, so the exact factory external manifest and complete internal schema of a live install JAR are not established. |
| Catalog/Application Manager | A downloaded JAR is staged below `/fs/mmc1/download`; Application Manager tracks download/CRC state and hands the local artifact to Kona AppManager `installApp`. | **[UNKNOWN]** Network catalog metadata and a complete downloaded sample are not present. CRC32 is transport integrity, not signer trust. |
| Factory KIM | `<KIM>/xlets/<appId>/prog/` contains external `xlet.properties`; `prog/jars/` contains the application JAR, `key.jar`, and `magic.txt`. The KIM root can also contain `DRM.jar`, resources, and `xlets/xletsdir_ref.txt`. | **[CONFIRMED]** for the 18.45.01 factory corpus. It must not be assumed that the on-media live-install JAR has this same outer directory layout. |

The fields visibly used for identity and compatibility are application ID, version, main class, application JAR filename, policy/default policy, daemon/autostart metadata, Kona minimum/maximum version, package source URI, installed/factory state, and the signed-manifest/DRM metadata described below.

## Package identity and trust layers

These artifacts have different roles and should not be collapsed into one "signature" concept.

### `xlet.properties`

**[CONFIRMED]** There are 135 KIM Xlet property files across 27 KIM families (`reports/corpus_inventory.md:162`). All 135 contain app ID, version, default policy, main class, name, and JAR filename. The directory app ID matches the declared app ID in every instance.

The KIM1 Slacker example declares app ID and version at lines 12-13, `full.policy` at line 15, main class and explicit policy at lines 17-18, and JAR filename at line 20 (`analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages/KIM1/xlets/05096915-cc7e-4881-b53e-278f6d799862/prog/xlet.properties`, SHA-256 `ea6550eeb9b1774d8ef356ae2165da7cd7bd20a775380107e9fae7f71fa5a53a`).

**[CONFIRMED]** The lifecycle census is 33 `xlet.daemon=true`, 13 `xlet.daemon=false`, and 89 without that field. Exactly three property files set `xlet.autostart=true`; they are app ID `999`, main class `com.accenture.uconnect.ota.UConnectOtaXlet`, in KIM6, KIM11, and KIM25. A representative is `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages/KIM25/xlets/999/prog/xlet.properties:7-18`.

**[HIGH]** These properties are AMS launch descriptors and policy selectors. They do not by themselves grant trust; they are protected only when included in a verified package envelope.

### `key.jar`

**[CONFIRMED]** Every one of the 135 application instances has `key.jar` (`reports/corpus_inventory.md:162`). The signer census finds 123 Chrysler UConnect Application CA occurrences and 12 FCA VP4 Application occurrences; two of the FCA files also carry Accenture (`reports/kona_trust_model.md:59-73`). No application `key.jar` carries the isolated Xlet Developer certificate.

The representative KIM1 Slacker package proves the detached-envelope structure:

- Application JAR: `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages/KIM1/xlets/05096915-cc7e-4881-b53e-278f6d799862/prog/jars/05096915-cc7e-4881-b53e-278f6d799862.jar`, 925,156 bytes, SHA-256 `329098c01cd0cbef808ca06778e57411be979108dfb35965ba2992c6fd5c8a47`, 557 ZIP entries, and no embedded `META-INF` signature block.
- Detached envelope: `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages/KIM1/xlets/05096915-cc7e-4881-b53e-278f6d799862/prog/jars/key.jar`, 52,183 bytes, SHA-256 `91a031d22e62e129177470e64533df772f1faad57a532cd4caddcb45518d1aa0`, containing only `META-INF/MANIFEST.MF`, `META-INF/CVP_APP_.SF`, `META-INF/CVP_APP_.RSA`, and `xlet.properties`.
- **[CONFIRMED]** A read-only recomputation matched all 513 named SHA-1 digest sections against all 513 non-directory application-JAR members: 512 other payload members plus `xlet.properties`. The manifest begins with named payload digests at `key.jar!META-INF/MANIFEST.MF:4-10`; its SHA-256 is `3ae4c6ef1633de54c3167db35ee9d1e058e0262114a12da6aa903c6cb552873f`.
- **[CONFIRMED]** `key.jar` also embeds a byte-identical copy of the payload's `xlet.properties` (1,051 bytes, SHA-256 `89b72dcc065b5319caf379bffc6dec65c901dec4fdfd6c33653615e4f264fdf9`). It agrees on app ID, main class, name, version, and policy (`key.jar!xlet.properties:2-12`), although its historical JAR filename differs from the externally installed filename.

**[CONFIRMED/PARTLY UNKNOWN]** `key.jar` is therefore a signed detached manifest binding application bytes and descriptor metadata. At installed launch, `Installer.getKeyJarFile` constructs the fixed sibling `<appId>/prog/jars/key.jar`; `AMSController` passes it through `XletManager` and `XletClassLoader` to `VerificationClassLoader.keyJar_`; and signer lookup obtains certificate objects from exactly `key.jar!/xlet.properties`. The path and signer-object association are confirmed. The AOT certificate extractor, runtime recomputation of the demonstrated cross-JAR digests, `SigningKeys` key-match details, and signer-to-principal mapping remain unknown (`reports/keyjar_runtime_association.md`).

The KIM3 Application Manager independently reproduces the same contract: its executable JAR has 580 non-directory members and no internal signature block; companion `key.jar` has 580 manifest member sections; all 580 names are present and all 580 digests recompute. Its executable-root and embedded descriptors are byte-identical (504 bytes, SHA-256 `f048fa1b7a4aa7885c3bb30c0fd173b9a99e8afd88701a85beeabd7bebd09c0d`). The separately installed descriptor preserves the same 17 semantic keys while normalizing `xlet.jarFile` from the signed historical filename to the installed UUID filename.

### Secure AMS and verifier evidence

**[CONFIRMED]** The stock AMS binary is 11,956,352 bytes with SHA-256 `96683b789ecf06a8575915d0b446b532e1f4ee87feb31d925cb7ba3d7d324d27`. Its static strings include:

- the `[-secure]`, `-securityConfiguration`, `-installationDirectory`, and `-start <appId>` usage family around file offsets `0xa6554a-0xa6563a`;
- `No Public Keys are available. The AMS cannot run any xlets.` at `0xa4f54b`;
- `verify signature block file` at `0xa6b283`;
- `JarVerifier` references, including `0xa6ed7e`;
- `xlet.properties` references at `0xa639b6`, `0xa70a91`, and `0xa8b03e`.

**[CONFIRMED/PARTLY UNKNOWN]** The direct ROM call graph now goes beyond strings: installed launch constructs and propagates the fixed companion path, uses `key.jar!/xlet.properties` as the signer-object source, then enters the developer/device/certificate verifier. `SigningKeys` receives the promoted selected-security-JAR keys. Its AOT body and the certificate-extraction method remain opaque, so exact old-SHA-1 handling, chain ordering, revocation/time behavior, and runtime cross-JAR digest recomputation are not claimed.

### `DRM.jar`

**[CONFIRMED]** Twenty-six KIM roots have `DRM.jar`. In each, the signed manifest binds its embedded `xlet.properties`; all 26 manifest SHA-1 digests recompute. The signer distribution is 22 Chrysler and four FCA VP4 EMEA packages.

KIM1's `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages/KIM1/DRM.jar` is 3,484 bytes with SHA-256 `0a4cb4ead688547658a7ac5d0beecd0b242c36aa5bdf0f1f887cad5707f06ad2`. `DRM.jar!META-INF/MANIFEST.MF:4-5` names and digests `xlet.properties`. The signed property member (`SHA-256 57f3f994c25e4653bf1722ef0e2470684ea4528d7c80e55ec145876b0c47e35c`) contains AMS/native/NGTP grant state, VIN placeholder, application IDs, versions, filenames, lengths, content IDs, feature masks, and `installerType=DRM_SYNC` (`DRM.jar!xlet.properties:1-5`). Its application `fileChecksum` values are null.

**[HIGH]** `DRM.jar` is signed entitlement/provisioning state, not the payload-byte signature mechanism. `key.jar` supplies the visible payload binding.

### `xlet.developerToken`

**[CONFIRMED]** Six descriptors contain `xlet.developerToken`, covering two app IDs across KIM1, KIM12, and KIM16. All six encode the same 256-byte value; the decoded-value SHA-256 is `126a6126acb7832b1385e3caa9db7c6e78340acb92d020fabe4c86193b5f1045`. The token bytes are intentionally not reproduced here.

| Property path | Line | Property-file SHA-256 |
|---|---:|---|
| `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages/KIM1/xlets/079aa169-df8f-48b4-b331-4ed51dbf6b12/prog/xlet.properties` | 10 | `7319c16b876610a6c9b2fbeb40164b791a8ae1c5ec839ae38b2a9f3fb13ac430` |
| `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages/KIM1/xlets/4c74b232-3360-42ff-a05f-d098ba85b220/prog/xlet.properties` | 8 | `3039a43fe562e40175cfb112374eba3e091ce05c9cc610ad9761880f74b1ade4` |
| `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages/KIM12/xlets/079aa169-df8f-48b4-b331-4ed51dbf6b12/prog/xlet.properties` | 10 | `f3e8aed51c4ac7628f07a5ca8212f79e7e356ee7af83d6422966f6fcdadaed06` |
| `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages/KIM12/xlets/4c74b232-3360-42ff-a05f-d098ba85b220/prog/xlet.properties` | 8 | `fd7e52e9f3c06118b80c5b280491609a7404e7aed61313aaa4d439e6aced843a` |
| `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages/KIM16/xlets/079aa169-df8f-48b4-b331-4ed51dbf6b12/prog/xlet.properties` | 10 | `3cd2657c07b58ca45751c2e390813ea8dc2f7324d86545d38a9c99188e67002e` |
| `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages/KIM16/xlets/4c74b232-3360-42ff-a05f-d098ba85b220/prog/xlet.properties` | 8 | `c7d797ba83b263d944853aa7572c07a739998bce11876632c732ed11015f5c08` |

**[CONFIRMED AMS CONSUMPTION AND TOKEN PREDICATE]** `VerificationClassLoader.getDeveloperToken()` loads this exact property from `xlet.properties`, then the private verifier passes it to `KeyVerifier.verifyAllCertificates`. The first branch evaluates `SignedId(token,SecurityParameter.getDeveloperId()).verify(SecurityParameter.getSigningKeys())`; `SignedId` Base64-decodes the token, decrypts it with `Cipher.getInstance(key.getAlgorithm())` in public-key decrypt mode, converts the plaintext with the platform-default charset, and requires exact equality with `developerId`. RA4's ROMized provider path resolves the RSA candidate to SunJCE `RSA/ECB/PKCS1Padding`, internal verify mode, and PKCS#1 v1.5 block type 1. The final keys are promoted from certificates attached to the selected production/development `security.jar!/xlet.security`, after `_internalKeys_` from `rom:/internal.jar` authenticate that configuration. On failure AMS falls back to the device-token/certificate path. The missing runtime ID provider, legitimate private-key issuer, detached-`key.jar` association, and signer-to-policy effect remain unresolved (`reports/developer_token_analysis.md`, `reports/signedid_jce_semantics.md`).

### `magic.txt`

**[CONFIRMED]** The materialized primary and secondary trees contain 245 `magic.txt` files (83 primary, 162 secondary). Every file is exactly the six ASCII bytes `HB_CMC` with SHA-256 `0ffe9823746d76b9fb74480676a68d052b3a11634f2dfe67bd9fe9c8f3cd1f80`. A literal scan of the materialized trees finds no non-`magic.txt` consumer; the raw ISO containers naturally include copies of those bytes. The broader duplicate-family observation is recorded at `reports/corpus_inventory.md:191`.

**[INFERRED]** `magic.txt` is a generic build/copy sentinel. **[UNKNOWN]** No evidence establishes it as an authentication, signer, developer-mode, or licensing secret.

## AMS lifecycle and running Xlets

**[CONFIRMED]** `ams.properties` contains start/init/pause timeout keys and a default callback timeout, plus init/start/pause/destroy/callback priorities (`analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/data/ams.properties:1-11`, SHA-256 `790847a3a00a62cf0886565f49d103f5a16fd20fe975fced96d3427cafd0fde0`). It has no explicit destroy-timeout key; use of the default callback timeout for destroy is not established. The [pause/watchdog trace](ra4_xlet_pause_watchdog.md) separates these configuration values from native request submission and completed recovery.

**[CONFIRMED]** `AMSClient` is 3,593,200 bytes with SHA-256 `12439c3e2554d388c43ca7f1023e96ad2183f5ae22a20991041b833eaa4eec9`. Its compiled constant pool contains an install example `install { "uri":"file:test.jar"}` at `0x2d6a85`, `package-info` at `0x2ef308`, `factory is already installed` at `0x2f1906`, `StartXlets` at `0x3102c4`, a command-form `remove` at `0x323672`, `auth` at `0x323d56`, and list-related strings at `0x32a574` and `0x32a8b0`.

**[HIGH]** These strings establish the package/lifecycle API surface, but not a complete safe CLI grammar. They are evidence, not instructions for installing an untrusted package.

The externally visible operation evidence is:

| Operation | Confidence | Static evidence and limit |
|---|---|---|
| Discover/list/package info | **[HIGH]** | USB Lua calls AMS `getAllProperties`/`getPackageInfo`; `AMSClient` contains `package-info` and list strings. AppManager's separate `AppManager_JavaApps` JSON/QDB catalog is recovered, but the backing AMS package-registry schema remains unknown. |
| Install | **[CONFIRMED]** | USB Lua invokes AMS `install` with a staged file URI; KIM3 invokes Kona AppManager `installApp`; native `installApp` performs authenticated package-info preflight and converges on AMS method `upgrade`; `AMSClient` contains an install request example. |
| Upgrade | **[CONFIRMED]** | USB Lua chooses AMS `upgrade` when an app ID is already installed; native catalog installation always invokes the AMS adapter named `upgrade`, including its fresh-install task. Whether AMS `upgrade` is an upsert remains unknown. |
| Enable/disable | **[CONFIRMED bounded negative]** | The Java public AppManager API has no enable/disable method. Native `parseRequest` contains 56 constant method comparisons but no enable/disable/launch token, and a full-file ASCII/UTF-16 census finds no `enableApp`, `disableApp`, or `launchApp`. This exact binary has no proved per-app enable/disable operation; installation, launcher entitlement, global autostart, and lifecycle state remain distinct. |
| Start | **[CONFIRMED UI/module/native route]** | The generic stock Apps surface calls `IAppManager.startXlet(selected.appId,"MoreScreen")`; the HMI module emits an AppManager `startApp` JSON request, and native AppManager dispatches to `findAndStartApp` with DRM checking enabled before the AMS-facing App start operation. The separate Java `startApp(String,String)` API performs `AppMgrPermission("appMgr")` and SvcIPC checks. A normal non-autostart install completes without launch and requires this later explicit start route. |
| Pause/stop/destroy | **[CONFIRMED API/native dispatch]** | Java `pauseApp`/`stopApp` perform `AppMgrPermission("appMgr")` checks and SvcIPC calls; native `parseRequest` dispatches both. AMS initializer evidence covers controlled Xlet destruction. The supported user-facing pause/stop grammar still requires runtime validation. |
| Uninstall/remove | **[CONFIRMED]** | KIM3 invokes `uninstallApp`; native AppManager stops/waits, submits asynchronous uninstall, removes Xlet resources and per-app/shared RMS state, then queues native-map deletion. Atomicity and prior-version restore remain unknown. |

**[CONFIRMED]** The application-media Lua uses a service/IPC boundary: it registers `SoftwareInstaller`, subscribes for AMS availability, and issues property/install/upgrade requests to AMS. **[UNKNOWN]** The stripped bytecode and AOT-compiled client do not expose a complete, independently validated D-Bus signature for every method.

### Native catalog-install convergence

**[CONFIRMED]** Native `appManager` builds an artifact URI, adds `auth=true` at file `0x192878/0x19288C`, constructs AMS method `getPackageInfo` at `0x1928C8`, and invokes the asynchronous AMS wrapper at `0x192904` with callback `0x193E9C`. This is the authenticated preflight after KIM3's CRC-only download check.

**[CONFIRMED]** `installNow` calls from file `0x91C40` to adapter file `0xEA84` (VA `0x10EA84`). That adapter materializes diagnostic `AM:upgrade()[%i]` through `0xEAB4/0xEAB8`, request key `uri` through `0xEAD4/0xEAD8`, and exact AMS method `upgrade` through `0xEB34/0xEB38`. Therefore the catalog's native `installApp`, including the catalog fresh-install task, reaches AMS `upgrade`; the USB script is the recovered path that explicitly selects `install` for an absent app and `upgrade` for a present one.

The native completion order is authenticated package info -> AMS `upgrade` -> response plus `onInstalled` signal -> `finishInstall` -> native app mutation -> resource moves -> write-access revocation -> conditional autostart -> `appListUpdated` -> queued whole-list persistence. This order is confirmed; how AMS `upgrade` branches for an absent app is not.

### Native per-application uninstall and cleanup

The native AppManager closes much of the previously unknown removal path:

1. **[CONFIRMED]** Its request dispatcher compares the operation name with `uninstallApp` at file offsets `0x54058-0x54064` (VA `0x154058`) and calls `startUninstallApp` at VA `0x191158` when equal (`0x5406C-0x54078`).
2. **[CONFIRMED]** `startUninstallApp` is file offsets `0x91158-0x91478`. It parses `appId`, rejects a missing app, unfinished startup, or another pending request using diagnostics at `0x1112F8-0x1113E3`, and either requests a stop for a non-stopped app or proceeds to `uninstallNow` at VA `0x190FAC`.
3. **[CONFIRMED]** `uninstallNow` is file offsets `0x90FAC-0x91154`. It waits when the app is not stopped, obtains write access, and calls from file `0x910B0` to AMS adapter file `0xE854` (VA `0x10E854`). The adapter materializes diagnostic `AM:uninstall()[%i] appId="%s"` at `0xE89C/0xE8A0`, request key `appId` at `0xE8DC/0xE8E0`, and exact AMS method `uninstall` at `0xE964/0xE968`; failures use the diagnostic at `0xE9F8/0xE9FC`.
4. **[CONFIRMED]** The asynchronous callback `onUninstalled` starts at file offset `0x8FE94` (VA `0x18FE94`). On a successful result it queues event `finishUninstallation`; the event dispatcher recognizes that name at `0x5CF74` and calls `finishUninstall` at VA `0x193910`.
5. **[CONFIRMED]** `finishUninstall` (`0x93910-0x93B3C`) waits until its required signal/response state is complete, calls `cleanUpXletResources` at VA `0x13B0CC` from `0x93A10`, and then queues `deleteAppFromHashMap`. The main event loop recognizes `deleteAppFromHashMap` at `0x5C058-0x5C064` and invokes its map/list handlers at `0x5C07C-0x5C088`.
6. **[CONFIRMED]** `cleanUpXletResources` (`0x3B0CC-0x3B2D8`) looks up the exact app ID, removes its Xlet resources, and calls `removeRMSFiles` at VA `0x131B94` from `0x3B288`. `removeRMSFiles` (`0x31B94-0x31EF4`) builds `<configured xletRMSDir>/<appId>` with `%s/%s`; if present it executes `rm -R %s`. It separately builds `<configured xletRMSDir>/common/<appId>.rs`; if present it executes `rm %s`. The exact diagnostics and command templates are at file offsets `0x103A7C-0x103BAB`. The configured root is `/fs/etfs/usr/var/appman/xletRMS` in `appManager.cfg:10`.

This proves that stock per-app uninstall is not merely a registry flag: its success path removes the app's resources, app-specific RMS directory, shared RMS record, and native map entry. It then emits `appListUpdated` and queues a complete `AppManager_JavaApps` JSON save through files `0x5C130..0x5C1C4`. **[UNKNOWN]** remains whether AMS deletes or retains the installed payload directory, which intermediate state survives power loss, whether every application-owned path is covered, and whether a previous version can be restored.

### Native install completion, autostart, and explicit launch

The same native AppManager closes the static post-install launch rule:

1. **[CONFIRMED]** `onInstalledSignal` at VA `0x1938A8` / file `0x938A8` calls `finishInstall` at VA `0x1935BC` from file `0x938E4`. `finishInstall` calls `onAppInstalled()` at file `0x936EC`, clears App byte `+0x2AD` at `0x936F4`, calls `changeIntermediateState(app,5,0)` at `0x93700`, revokes write access at `0x93850`, and calls `autoStartApp` at file `0x93858`.
2. **[CONFIRMED]** `autoStartApp` is conditional. For a stopped app it asks DRM whether the application is autostart-entitled. The DRM entry's `mAppLauncherMask` is loaded at file `0x1BB38`, tested with mask `#4` at `0x1BB3C`, and returned as bit 2 at `0x1BB64`. The complete launch predicate is `(DRM launcher-mask bit 2 OR stock super-app override) AND global autostart gate`.
3. **[CONFIRMED]** When that predicate is false, control reaches `INSTALLATION DONE` at file `0x91A30` and the success completion helper at `0x91A64` without calling the App start primitive. Installation of an ordinary non-autostart app therefore succeeds without launching it.
4. **[CONFIRMED]** The explicit native request token `startApp` is at file `0x108084`; `parseRequest` compares it at `0x53DD0` and calls handler VA `0x14FDB0` at `0x53DF0`. That handler passes a literal DRM-check byte of one at `0x50650` and calls `findAndStartApp` at VA `0x13B2DC` from `0x5066C`. Its failure paths include no service, failed DRM, and app not found (`0x105474`, `0x1054BC`, `0x105510`), and its sole App-start call is file `0x3C328` to VA `0x10EE68`. App start constructs operation `start` and invokes the AMS-facing helper at file `0xF008`.
5. **[CONFIRMED]** Java `AppManagerImpl.startApp(String,String)` starts at class-file offset `0x3565`, checks `AppMgrPermission("appMgr")` at `0x356E`, loads SvcIPC operation `startApp` at `0x35A7`, and invokes it at `0x35B0`. Pause and stop use the same boundary at `0x36CB/0x36D4/0x36FE/0x3706` and `0x3813/0x381C/0x3846/0x384E`.
6. **[CONFIRMED]** The stock human-facing caller is the generic Apps screen, not the Java API. ROV `AppsMainScreen.swf` (36,208 bytes, SHA-256 `5df0c52056d9495c439e8c90d1826be132f43bc7d4a61951acd4f1adfccbd04d`) registers the `ITEM` listener in `addListeners` at FWS `0xB79D..0xB7A7`. `onItem` (method/body/code `0x9F17/0xBDA0/0xBDA7`) rejects the already-running selection, special-cases Performance Pages through `fullStartDaemonXlet`, and for an ordinary selection calls `IAppManager.startXlet(selected.appId,"MoreScreen")` at FWS `0xC1E6` (reason at `0xC1E3`). ROV `MainSupplement.swf` (1,407,783 bytes, SHA-256 `e9d796ea4b4c83ed518bfe3b3c341e54e510a1ae0f78ebbffbd655b7c36a3258`) implements `AppManager.startXlet` at method/body/code `0x1E7A0B/0x2A9712/0x2A971A`, applies a duplicate running gate at `0x2A977E..0x2A9794`, emits the `startApp` command at `0x2A97E1`, and sends it at `0x2A97E7` through `sendAppMgrCommand` (method/body/code `0x1E7A65/0x2A9AA4/0x2A9AAB`, final send `0x2A9AF6`). For an ordinary app the logical envelope is `{"Type":"Command","Dest":"AppManager","packet":{"startApp":{"appId":"<selected-id>"}}}`.
7. **[CONFIRMED bounded HMI census]** `AppsMainScreen.init` requests `getAppList` at FWS `0xBBCE/0xBBE8`; the module builds `mApplications` from the response at `0x2A7E0D..0x2A7E27`, and `createApplicationList` generically appends entries at `0x2A8FC7..0x2A8FCD`. No downstream generic `enabled`, `hidden`, or `suppressed` field was found in this HMI route. Native AppManager could still omit an application before returning `getAppList`, so actual visibility and metadata for a newly authorized helper require target-unit observation.

The global gate is not per-app enablement. `parseConfigFile` handles `alwaysAutostartApps` at file `0x76BAC..0x76BF8`; when absent it tests `/fs/etfs/No_AutoStart_App` at `0x76C28`, storing disabled at `0x76C50` or enabled at `0x76C6C`. Recovered `appManager.cfg` contains no `alwaysAutostartApps`; its `delayedStartApps` entries are two fixed stock UUIDs (`appManager.cfg:26`, with empty variant overrides at lines 42, 58, 83, and 107). An arbitrary helper is not selected by that list.

Post-install data movement is also bounded. `finishInstall` constructs `<configured base>/xlets/<appId>/data/` and calls VA `0x18DF38` at file `0x93758`; that helper formats `mv %s %s` from string file `0x110BB8`, executes each pending move at `0x8DFC8`, and clears its vector. This is an additional mutation to include in atomicity and rollback tests.

### AppManager catalog persistence and interruption boundary

**[CONFIRMED]** Native AppManager initializes persistent key `AppManager_JavaApps` at string file `0x101C54`. `readJavaAppsList` begins at VA `0x130050` / file `0x30050`. `saveJavaAppsList` begins at VA `0x157698` / file `0x57698`: it performs a separate persistence `read` through `0x57704..0x577C0`, rebuilds the entire JSON array from the native application map at controller `+0xAC`, and sends a separate `write` through `0x58818..0x58858`. Its only direct call is dispatcher file `0x5C348`; no caller-side compare-and-swap value, generation, transaction ID, or retry loop is present.

**[CONFIRMED]** `pmem_keyvalue.ini:14-20` routes unmatched keys to database `keyvalue`. `qdb.cfg:41-44` maps that database to `/usr/var/qdb/key_value` with schema `/etc/sql/persistency_mgr/key_value.sql`; the schema defines `keyvalueTbl(key TEXT PRIMARY KEY,value TEXT NOT NULL)` and `PRAGMA journal_mode=truncate`. Runtime persistence uses one SQL `UPDATE` or `INSERT OR REPLACE`, while the `keyvalue` configuration has no `Backup Dir`. On detected corruption, `qdb_recover.sh:21-22` deletes `key_value*` and resets rather than restoring a configured backup.

**[CONFIRMED]** Install success reaches `finishInstall`, updates native state, moves tracked resources, emits `appListUpdated` at `0x91580..0x91584`, and only then queues the full-list save at `0x91608..0x9160C`. Uninstall crosses the AMS response/signal handshake, `finishUninstall`, resource/RMS cleanup, queued native-map deletion, `appListUpdated`, and only then the queued full-list save. AppManager's `rm` at `0x8DE6C` and post-install `mv` at `0x8DFC8` ignore `system()` return values and clear their tracking vectors. These are confirmed divergence windows, not a cross-layer transaction.

**[CONFIRMED OWNERSHIP / UNKNOWN RECOVERY SEMANTICS]** Jamaica class-object metadata assigns `install(String)Application` (selector `0xAD7BE8`, body/marker `0x5BFCC0`), `recoverProgIfNeeded(String)V` (`0xAD7BF0`, `0x5BFDFD`), and `upgrade(String)Application` (`0xAD7CA8`, `0x5BFE8C`) directly to `Installer`. `install` loads the installation-directory rename diagnostic at `0x5BFD56`; `recoverProgIfNeeded` loads exact `prog.bak` at `0x5BFE1B` and `0x5BFEE3` plus the missing/backup diagnostic at `0x5BFE42`; `upgrade` loads its two rename diagnostics at `0x5BFF2E` and `0x5BFF5C`. The parent path, exact rename order, backup deletion/restoration, ordinary-upgrade trigger details, and crash contract remain unknown. The complete evidence and interruption matrix are in `reports/appmanager_registry_atomicity.md`.

The exact native parser range is VA `0x1516D4..0x156DFC` / file `0x516D4..0x56DFC`. Its exhaustive 56-method constant comparison inventory includes install, upgrade, uninstall, start, pause, stop, daemon, delayed, assist, embedded, foreground/background, status, list, reset, and DRM operations. It contains no per-app enable/disable/launch operation. This is a bounded negative for this binary, not proof against a numeric-only or external component not present in the corpus.

**[CONFIRMED]** The materialized HCP routing configuration names AMS object path `/com/aicas/xlet/manager/AMS` and its `alarm` signal with name/domain/appId/message fields (`analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hcp/HCPConfig.conf:471-488`, SHA-256 `9a275298dff2e3e98e8d2ac6e7237fb879c7838097735f7f3a5b14001fc17326`). This anchors the service object used by the clients without supplying unverified method signatures.

**[CONFIRMED]** Application persistent state is not limited to `/fs/mmc1/xletsdir`: the VSBClient descriptor points `app.rmsPath` to `/fs/etfs/usr/var/appman/xletRMS` (`analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages/KIM1/xlets/f7583530-8d53-11e0-91e4-0800200c9a66/prog/xlet.properties:7`, file SHA-256 `04ada865fe9b9b22d7b76c5f8909006f7114350009712742ce4a7d4f6b3677b9`). The contents and schema of that RMS state are **[UNKNOWN]**.

### Boot and native AppManager orchestration

The canonical parent image is `analysis_ra4_18.45.01/work/primary_iso/usr/share/IFS/ifs-cmc.bin`, 42,122,670 bytes, SHA-256 `ea6797be141763f35f3059ad858eefbf54f730af0155bebc7af411c47d80ba92`. The standard boot image payload begins at parent offset 102,672 (`0x19110`); its 53 framed blocks consume 1,512,821 bytes through exclusive end offset 1,615,493 (`0x18a685`) and decode to SHA-256 `503d46f0ac412fcff594a9b37cc859d2e029e257a2d2367275c723a5f77d22ab` (`analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/imagefs.sha256:1`). A separate HBC header is present at parent offset `0x00f20000`; the four-byte little-endian compressed-size field at `0x00f2000c` is `f1 f4 a7 00`, or 11,007,217 bytes. That materialized decoded image is SHA-256 `57feaf9cfde58172f8a94049227ec895eb2f88607466297e31f8732f201b8512` (`analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/imagefs.sha256:1`). The other boot-service image begins at parent offset `0x001a0000` and has decoded-image SHA-256 `996c5a52cf7e72bb73d95e34e684196ca702061c6c5d9977415b014fbea57fbb` (`analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/imagefs.sha256:1`). These are provenance anchors for the following files; no recovered executable was run.

- **[CONFIRMED]** The materialized `/bin/boot.sh` is 29,268 bytes, SHA-256 `c801d473b0b49e8242114635f4022cc67ccbe03093fec188de3b7188dd636ecf` (`analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/inventory.tsv:51`). The embedded-cell branch creates `/fs/etfs/usr/var/appman/xletRMS`, assigns `disableDRMArg=-d` unconditionally, and passes it to `appManager -s -j -v` (`analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/files/bin/boot.sh:362-371`); the CAN branch repeats the same sequence (`analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/files/bin/boot.sh:456-465`). Native `processOptions` at VA `0x195FFC` creates a sole local option set containing `silent/s`, `json/j`, `presub/p`, `watchdog/w`, `config/c`, `tp`, and `help/h`, but no `drm/d`. The processor stores only that set at `0x1D9FC8`; its single-dash path at `0x1DA96C` looks up short name `d` from that set at `0x1DA1C8`, so neither inheritance, clustering, nor prefix matching provides a route. The unknown-option handler at `0x196E00` says it is ignored. Although dormant branch `0x19718C` handles normalized name `drm`, that long name is unregistered too. The DRM-checker constructor at `0x181318` initializes enable byte `+5` to one at `0x181338`, and install preparation calls checker `0x1801D4` at `0x1957A4`. Thus DRM checking is **[CONFIRMED]** enabled and stock `-d` is ignored; it does not bypass package/signature validation.
- **[CONFIRMED]** The same script waits for `/dev/serv-mon/com.aicas.xlet.manager.AMS` in the embedded-cell and CAN paths (`analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/files/bin/boot.sh:398`, `analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/files/bin/boot.sh:722`), anchoring native AppManager startup to AMS service readiness, and starts `platform_ams_restart.lua` at `analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/files/bin/boot.sh:747`.
- **[CONFIRMED]** Boot also starts `authenticationService` with `/etc/system/config/authenticationServiceKeyFile.json` (`analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/files/bin/boot.sh:648-649`). Whether that native service participates in AMS JAR/signature validation is **[UNKNOWN]**; proximity in the boot sequence is not a trust-path link.
- **[CONFIRMED]** The native ARM ELF `/bin/appManager` is 1,268,061 bytes, SHA-256 `608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591` (`analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/inventory.tsv:40`). Its static strings bind it to AMS service/object `com.aicas.xlet.manager.AMS` and `/com/aicas/xlet/manager/AMS` at file offsets `0x1156d0` and `0x1156ec`, include `registerWithAMS` at `0x0ff690`, and expose app-result paths for `start`, `stop`, `uninstall`, and `upgrade` at `0x100920`, `0x1007e0`, `0x100814`, and `0x10086c`. This confirms that the native process is an AMS-facing application coordinator; the exact D-Bus method signatures remain **[UNKNOWN]**.
- **[CONFIRMED]** Its configuration is 5,802 bytes, SHA-256 `ab9ed180574d2c9f83c45217f05b132af24abd364ecf59c8447d1ba0cdb9c2d7` (`analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/inventory.tsv:252`). The default block defines preload `/fs/mmc1/kona/preload`, Xlet root `/fs/mmc1/xletsdir`, RMS `/fs/etfs/usr/var/appman/xletRMS`, live DRM `/fs/mmc1/kona/data/DRM.jar`, and restore DRM `/fs/mmc1/kona/preload/DRM.jar` (`analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/etc/system/config/appManager.cfg:8-14`). Matching native strings parse `xletRMSDir`, `xletsDir`, `drmFileLocation`, and `restoreDRMFileLocation` at offsets `0x10c5e8`, `0x109134`, `0x10d18c`, and `0x10d220`.
- **[CONFIRMED]** `platform_ams_restart.lua` is Lua 5.1 bytecode, 7,514 bytes, SHA-256 `264e5aaa6e2e09e8bb86a881f4919a66220d1cad2c7ce9443416e5d35f9f720f` (`analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/inventory.tsv:447`). Decoded functions 7, 9, and 10 (source/debug lines 183-250) watch AMS D-Bus ownership and a 120-second startup timer. If AMS never appears, the supervisor terminates/relaunches the JVM; if AMS disappears, it kills AMS and AppManager, relaunches AppManager, waits for its service, and invokes `/fs/mmc0/app/bin/jvm.sh`. During that recovery path it tests `/fs/etfs/disableDRM` to choose command text without or with `-d` (constants `0x137A` and `0x13E5`). This proves the supervisor branch; the native analysis above proves the selected `-d` is ignored and leaves DRM checking enabled. The bytecode contains no `AMS_DEVELOPMENT` literal or marker watcher.

This separates three similarly named layers: the native `appManager` process launched by the boot IFS, the secure AMS Java/Xlet runtime launched through `jvm.sh`, and the KIM3 `Application Manager` Xlet that downloads and submits application packages.

**[CONFIRMED]** `ams_initializer.jar` has SHA-256 `b40c69ff6cfd3e31e097c5ae33e71f1a314ce8aee2e3a734589f3025a98e959c`. Its manifest selects `com.harman.ams.initializer.Initializer` (`META-INF/MANIFEST.MF:4`). `com/aicas/xlet/manager/AmsAccessor.class` contains `destroyXlets` at class offset `0x008a` and running/paused application state at `0x02c4`/`0x0397` (entry SHA-256 `4278e83a4d0bdf967ec26ba99d463d5417e84ac28a146d731fcf8fa0394bb950`). The SIGTERM handler in `Initializer$1.class` contains `destroyXlets`, `java/lang/System`, and `exit` at offsets `0x019b`, `0x01b4`, and `0x01bd` (entry SHA-256 `654ef04d9eaa1d33b7b4fecc0057c7b8aa5ff822dd75a716001d040046655b5a`).

**[CONFIRMED through the recovered stock UI/module/native route]** AMS/AppManager discovers and finalizes an installed package, but an ordinary non-autostart app completes installation in stopped state. Native conditional autostart requires DRM launcher-mask bit 2 or the stock super-app override plus the global gate. The generic Apps screen then supplies the human-facing explicit-launch route: `AppsMainScreen.onItem` calls module `AppManager.startXlet`, which sends the native `startApp` request; native AppManager retains DRM checking and reaches the AMS-facing start operation. This HMI route does not traverse Java `AppMgrPermission`; the permissioned `AppManagerImpl.startApp` API is a separate Java caller surface. Pause/stop have matching permissioned Java/native dispatches, and the initializer destroys Xlets during controlled AMS shutdown.

## Restart, failure, and rollback

- **[CONFIRMED] Live app install:** The USB application Lua calls AMS `install`/`upgrade`, deletes only its staging file, and contains no reboot/reset action. **[HIGH]** It is designed as a live AMS operation rather than a head-unit software-update reset path.
- **[CONFIRMED] Post-install launch rule:** The installer does not explicitly call `StartXlets`. Native `finishInstall` calls conditional `autoStartApp`; an ordinary app without DRM launcher-mask bit 2 or the stock super-app override reaches successful completion without launch. Its later explicit launch is statically proved through the generic stock Apps entry: `AppsMainScreen.onItem` -> module `AppManager.startXlet` -> native AppManager `startApp` with DRM checking enabled. Whether a newly authorized helper is returned by `getAppList`, rendered with the intended name/icon/category, and behaves identically on the target unit remains a dynamic validation question.
- **[CONFIRMED] Catalog cleanup, not rollback:** KIM3 `InstallHelper` has staging cleanup and optional uninstall-first behavior and contains no prior-payload reinstall-on-failure path. AMS `Installer.recoverProgIfNeeded` directly owns `prog.bak` handling, but the exact rename, restoration, commit, and crash semantics remain unproved.
- **[CONFIRMED] Factory KIM copy is non-atomic:** `xlets.lua` pre-deletes selected state and invokes `qkcp -h` without `-f/-r`. `-h` is progress only. `qkcp` directly creates/truncates final destinations and has no rename/remove rollback step; failure can leave an incomplete mixed tree (`reports/qkcp_kim_copy_semantics.md`).
- **[CONFIRMED] Limited partition preservation:** `mmc.sh` backs up `/fs/mmc1` to `/fs/mmc0/mmc1_bk` only for `MMC_TB` Take Back repartitioning (`analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/mmc.sh:111-152,488-499`) and restores it after repartition (`analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/mmc.sh:154-204,598-600`). This is preservation around repartitioning, not a generic application rollback.
- **[CONFIRMED non-atomic visible boundary / UNKNOWN AMS recovery]:** AppManager's AMS callback, resource moves, native-map mutation, and QDB whole-list write are separate phases and can diverge after interruption. No end-to-end A/B slot or cross-layer transaction is proved. AMS `prog.bak`/rename vocabulary exists, but restoration of an earlier version after an ordinary failed live install remains unknown. Factory KIM file-copy non-atomicity is independently confirmed.

## Open gaps

1. **[UNKNOWN]** A factory external-install manifest that selects `us-app-install.sh`, a sample `<ISO_PATH>/usr/share/APPS` tree, and the complete live application JAR schema. The detector, authentication, environment handoff, and external-script dispatcher are now confirmed.
2. **[PARTLY CONFIRMED / UNKNOWN]** The complete `xlet.developerToken` consumer, two-stage signing-key bootstrap, fixed installed `key.jar` path, `key.jar!/xlet.properties` signer-object association, and verifier branch order are confirmed. Immutable `rom:/internal.jar` roots authenticate the selected security configuration, whose `xlet.security` RSA signer key drives SunJCE `RSA/ECB/PKCS1Padding` public-decrypt/type-1 unpadding and exact `developerId` equality. AOT certificate extraction/`SigningKeys`, runtime ID provisioning, legitimate credential issuance, application signer/principal mapping, and production/development policy effects remain unknown.
3. **[UNKNOWN]** Hidden AMS package-registry files/schema, exact `prog.bak` parent/use and rename recovery, boot reconciliation with the recovered AppManager JSON/QDB catalog, and interruption behavior across payload, descriptor, native map, resources, and persistent list.
4. **[UNKNOWN]** Whether the target unit's native `getAppList` response includes a newly authorized helper with the intended name/icon/category and whether selecting it follows the statically proved generic Apps route at runtime. The human-facing caller and its direct native DRM-checked request are no longer unknown.
5. **[UNKNOWN]** General app-version rollback. The only confirmed restoration is the narrow Take Back repartition backup in `mmc.sh`; `qkcp` factory copying is directly non-atomic and supplies no rollback.
6. **[CONFIRMED boundary]** `appManager -d` has no non-diagnostic effect in this binary: it is absent from the sole local Poco option set and reaches the unknown-option-is-ignored handler, while the DRM checker initializes enabled and is invoked by install preparation. The `/fs/etfs/disableDRM` restart branch and stale boot argument remain historical configuration vocabulary, not an unresolved bypass candidate.

## Read-only verification commands

From the repository root:

```powershell
Get-FileHash analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/app-install/us-app-install.lua -Algorithm SHA256
Get-FileHash analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/update/installer/xlets.lua -Algorithm SHA256
Get-FileHash analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/AMS -Algorithm SHA256
Get-FileHash analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/AMSClient -Algorithm SHA256
Get-FileHash analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/extension/ams_initializer.jar -Algorithm SHA256
Get-FileHash analysis_ra4_18.45.01/work/primary_iso/usr/share/IFS/ifs-cmc.bin -Algorithm SHA256
Get-Content analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/imagefs.sha256
Get-FileHash analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/files/bin/boot.sh -Algorithm SHA256
Get-Content analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/imagefs.sha256
Get-Content analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/imagefs.sha256
Get-FileHash analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/bin/appManager -Algorithm SHA256
Get-FileHash analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/etc/system/config/appManager.cfg -Algorithm SHA256
Get-FileHash analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/platform_ams_restart.lua -Algorithm SHA256
Select-String -Path analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/jvm.sh -Pattern 'AMS_SECURITY_JAR','installationDirectory','-secure'
Select-String -Path analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages/KIM3/xlets/c1d77320-6335-48b2-aa22-21912f657311/prog/xlet.properties -Pattern 'xlet.appId','xlet.mainClass','xlet.version'
Select-String -Path analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/etc/system/config/appManager.cfg -Pattern 'preloadXletsDir','xletsDir','xletRMSDir','drmFileLocation','restoreDRMFileLocation'
git diff --check -- reports/application_install_pipeline.md
```
