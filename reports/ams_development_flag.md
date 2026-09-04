# RA4 18.45.01 `AMS_DEVELOPMENT` Flag

## Scope and safety boundary

This report addresses immediate priorities 2 and 3 from the project mission:

1. prove exactly how `/fs/etfs/AMS_DEVELOPMENT` changes `-securityConfiguration`; and
2. locate and classify every literal reader, creator, deleter, and reference in the existing canonical materialized RA4 18.45.01 corpus.

The pass was read-only. It used the materialized `primary_iso`, `secondary_iso`, and `installer_iso` trees plus the statically decoded standard and hidden IFS sections under `analysis_ra4_18.45.01/work/hidden_hbc_ifs`. No stock ZIP, update image, ISO, JAR, SWF, native binary, or firmware payload was modified or executed.

## Result

The recovered authorization/startup chain is:

    driver-temperature up + down held through 5000 ms
      -> ICS service emits engineerMode
      -> HMI opens engineering menu

    service.cert presented through SERVICEKEY media
      -> platform_troubleshoot verifies certificate
      -> requires matching head-unit serial and valid expiry
      -> EngineeringMenu=1 produces get_service_flags.eng_menu=true
      -> Peripheral.versionInfo.serviceMenu=true
      -> Service item becomes reachable
      -> AppsListEngServiceMenu item 19
         -> absent marker: createTempFile then moveTo AMS_DEVELOPMENT
         -> present marker: deleteFile AMS_DEVELOPMENT
         -> no restart, PIN, token, or service call in marker method

    initial boot:
      boot.sh -> connectivity_startup.sh -> qon -d jvm.sh

    recovery:
      platform_ams_restart.lua -> jvm.sh after AMS timeout/disappearance

    each jvm.sh execution:
      -> production security.jar by default
      -> development/security.jar iff -f /fs/etfs/AMS_DEVELOPMENT
      -> -secure remains present

This proves the service-certificate authorization upstream of the menu, the exact marker writer/deleter, the initial launcher, and a service-loss recovery launcher. It disproves the former assumption that anti-theft PIN success is the located menu gate: the recovered PIN path is a separate IOC state machine.

Two other controls remain separate. /fs/etfs/enableEngMenu controls whether AppManager includes its embedded appId engineering. AppManager's optional command text containing -d is selected from /fs/etfs/disableDRM on the recovery path, but completed native analysis proves that `-d` is unregistered and ignored while the DRM checker initializes enabled. Neither control reads or writes AMS_DEVELOPMENT.

## Consumer truth table

`jvm.sh` uses `[ -f ... ]`, so the decisive condition is a successful regular-file test at the moment the script executes. It never opens or reads marker contents.

| Marker state at `jvm.sh` line 59 | `AMS_SECURITY_JAR` after line 59 | Exact line 63 effect | `-secure` |
|---|---|---|---|
| Path absent | `/fs/mmc1/kona/security/security.jar` | `-securityConfiguration /fs/mmc1/kona/security/security.jar` | present |
| Regular file present | `/fs/mmc1/kona/security/development/security.jar` | `-securityConfiguration /fs/mmc1/kona/security/development/security.jar` | present |
| Path exists but is not accepted by shell `-f` | `/fs/mmc1/kona/security/security.jar` | production configuration remains selected | present |

The third row matters because the HMI reader uses the ActionScript `File.exists` property while the shell uses `-f`. A non-regular object could therefore make the HMI appear to see the marker while the launcher retains production configuration. QNX shell behavior for symbolic links and the exact AIR `File.exists` treatment of unusual filesystem objects still require target validation.

The shell has no selected-JAR readability/existence check. It records the chosen path at line 61 with:

```sh
echo "Launching AMS with $AMS_SECURITY_JAR" > /dev/ser3
```

That line is the strongest non-invasive runtime observation point for a future owner-authorized validation.

## Canonical artifacts

| Artifact | Size | SHA-256 |
|---|---:|---|
| `analysis_ra4_18.45.01/work/primary_iso/usr/share/IFS/ifs-cmc.bin` | 42,122,670 | `ea6797be141763f35f3059ad858eefbf54f730af0155bebc7af411c47d80ba92` |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/files/bin/boot.sh` | 29,268 | `c801d473b0b49e8242114635f4022cc67ccbe03093fec188de3b7188dd636ecf` |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/bin/connectivity_startup.sh` | 939 | `2d693484a49539ae1f83512bac068580014b1c2dcbb2c5885609e01726e3502f` |
| `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/jvm.sh` | 2,795 | `9bd3c63a2c22c17f96e037102283f453afca43eb093bc1291d607a9805f829ec` |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/platform_troubleshoot.lua` | 13,931 | `8beab38ab164479a9fd815116dbfa02a48e3fa661724fa9c4273dc5884a1ba45` |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/platform_ams_restart.lua` | 7,514 | `264e5aaa6e2e09e8bb86a881f4919a66220d1cad2c7ce9443416e5d35f9f720f` |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/bin/appManager` | 1,268,061 | `608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591` |
| `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/MainSupplement.swf` | 1,407,783 | `e9d796ea4b4c83ed518bfe3b3c341e54e510a1ae0f78ebbffbd655b7c36a3258` |
| `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_ru/skins/default/swf/AppsListScreen.swf` | 112,253 | `ac817adc1471c07631e80eccddf8f3231b549d9fc725d8b27cb2d13d54212d67` |
| `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/skins/default/swf/AppsListScreen.swf` | 117,093 | `5bc1630f567c82494ab86e73c308ad2a8b9d341494a5f5de5f66a1505f1416e5` |
| `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/security/security.jar` | 7,504 | `29a8a350ef0facc30c1c98e5250563a4020ad9c1a243f13e795e2e68e3bd74e7` |
| `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/security/development/security.jar` | 7,371 | `fbe5314ab304e122162aae20ace46999b93832fc4c7451439f4ada430eccc8a7` |

The two AppsList SWFs are distinct locale/variant builds, not duplicate copies. They contain equivalent AppsListEngServiceMenu flag logic with different method and stream offsets.

## Upstream authorization and independent controls

### Factory service-certificate gate

MainSupplement.swf VersionInfo::requestServiceFlags at reconstructed FWS offset 0x2D35B6 sends get_service_flags to platform. VersionInfo::platformMessageHandler reads get_service_flags.eng_menu at 0x2D3A64-0x2D3A6E, stores mServiceMenu, and dispatches ServiceEvent.SERVICE through 0x2D3A8C.

platform_troubleshoot.lua is a compiled Lua 5.1 chunk at hidden image offset 0x1CE07C2. It initializes service_flags.eng_menu=false at source/debug lines 29-45 and registers get_service_flags in function 15, lines 465-490. Functions 11/12, lines 406-427/408-422, ingest service.cert from a SERVICEKEY media event. Function 7, lines 255-304, requires successful stock scv verification, compares the parsed certificate serial with /fs/fram/serialnumber, parses the certificate, validates date/ignition-cycle expiry, and only then marks the service flags valid and emits them at lines 281-290. Function 2 maps EngineeringMenu numeric 1 to eng_menu=true at lines 82-90. Invalid/expired state is cleared and the service file deleted by functions 5/6, lines 188-248.

This is the positive factory authorization gate for Service-menu reachability. No anti-theft PIN state is read in the producer/consumer chain.

### Separate AppManager embedded-engineering gate

Native AppManager function file offset 0x29E08 (VA 0x129E08) tests /fs/etfs/enableEngMenu with numeric mode 4 at 0x29E20-0x29E30. Its sole direct caller at file offset 0x3D1C0 (VA 0x13D1C0) is createEmbeddedApps, where it filters appId engineering. A false result reaches the skip diagnostic at file offset 0x105C58. The complete materialized primary-plus-hidden search contains this literal only in AppManager; no writer was found.

This marker controls an AppManager embedded catalog entry. It is not Peripheral.versionInfo.serviceMenu and does not select AMS security.jar.

### Separate AppManager -d argument

boot.sh lines 367/371 and 461/465 unconditionally put -d in the initial AppManager command. platform_ams_restart.lua function 7 instead chooses command text without -d at source/debug line 199 when /fs/etfs/disableDRM is absent and with -d at line 201 when it is present.

AppManager's `processOptions` routine at VA `0x195FFC` constructs a sole local Poco option set at `0x196028` containing `silent/s`, `json/j`, `presub/p`, `watchdog/w`, `config/c`, `tp`, and `help/h`; it has no `drm/d` registration. The processor stores only that set at `0x1D9FC8`, its single-dash path at `0x1DA96C` performs a short-name lookup through the local set at `0x1DA1C8`, and the process-level handler at `0x196E00` reports that an unknown option is ignored. A dormant `drm` branch exists at `0x19718C`, but the long name is unregistered as well. Separately, the DRM-checker constructor at `0x181318` initializes enable byte `+5` to one at `0x181338`, and install preparation calls checker `0x1801D4` at `0x1957A4`. Therefore the scripts confirm argument selection and native analysis confirms the result: `-d` is ignored and DRM checking remains enabled. This control is also independent of AMS_DEVELOPMENT.

## UI reader, creator, and deleter

The embedded ActionScript debug path in both SWFs is:

```text
H:\Jenkins\Slave\workspace\CMC_MY16_Trunk\apps\hmi\NFUZION\Framework\src;extensions\apps;AppsListEngServiceMenu.as
```

This is historical compiler metadata. It identifies source/function positions but is not a path expected to exist on the head unit.

### Menu construction and action dispatch

`screens.NA_EU.RES_640x480:AppsListScreen/private:initExtension` constructs `extensions.apps::AppsListEngServiceMenu` with the screen object as its one argument. In the RU build this is method 8, ABC code offset 143,220, instruction offsets 203-211, embedded debug source line 213. The ROV build has the same instruction offsets in method 8 at ABC code offset 142,131.

Inside the service-menu class:

- static constant `ENABLE_DEVP_SECURITY_KEY` has integer value 19;
- the constructor calls `isDevepSecurityKeyEnabled()` at embedded debug source line 145;
- when the reader returns true, the constructor adds label `Enable Production Security` at source line 147;
- when it returns false, it adds label `Enable Development Security` at source line 151; and
- `onItem` maps the constant to switch value 19 and calls `DevepSecurityKeyEnabled()` at source line 495.

The vendor symbol spelling is `Devep`, not `Develop`.

### Reader semantics

`isDevepSecurityKeyEnabled()` performs only these substantive operations:

```text
destination = new flash.filesystem.File("file:///fs/etfs/AMS_DEVELOPMENT")
return destination.exists
```

The URI construction is embedded debug source line 758; `exists` is returned at line 759. There is no service request or authentication operation in the reader.

### Writer/deleter semantics

`DevepSecurityKeyEnabled()` constructs the same destination at source line 763, calls the reader at line 764, and branches:

| Prior state | Embedded source lines | Bytecode behavior | Resulting action label |
|---|---:|---|---|
| Reader returns false | 767, 770, 774 | Calls `File.createTempFile()`, sets the label, then calls `tempFile.moveTo(destination, true)` | `Enable Production Security` |
| Reader returns true | 785-786 | Calls `destination.deleteFile()`, then sets the label | `Enable Development Security` |

The `true` argument to `moveTo` is the overwrite argument. The creator therefore moves a newly created temporary file onto the destination rather than writing marker contents directly. Since the shell checks only `-f`, marker content is irrelevant to the observed selector.

The move operation is enclosed by one ActionScript exception handler (method-relative bytecode offsets 120-136, handler at 143), which logs `Error:**` plus the exception message at source line 779. The label is changed before the move is attempted, and execution continues to `mParent.invalidate()` at source line 789 even after the caught move error. Consequently, a failed creation can temporarily leave the UI label indicating the opposite state. The deletion operation is outside that local exception range.

The method ends after `mParent.invalidate()` and `return`. Its calls are limited to the reader, File operations, UI property updates, and the error trace. It contains no process launch, reboot, AMS signal/restart, filesystem `sync`, token request, anti-theft API, or IPC/service call.

## Bytecode locations

Both files use compressed `CWS` containers. Offsets below are decimal. `ABC offset` is relative to the start of the DoABC ABC stream; `uncompressed SWF offset` is relative to the corresponding in-memory `FWS` representation after inflating the CWS body. These are not offsets into the compressed on-disk bytes, so the on-disk SHA-256 is the primary artifact anchor.

### RU AppsListScreen

Path: `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_ru/skins/default/swf/AppsListScreen.swf`  
CWS size: 112,253; uncompressed SWF size: 278,207; ABC stream begins at uncompressed SWF offset 7,724.

| Evidence | Method | Method-relative offset | ABC offset | Uncompressed SWF offset |
|---|---:|---:|---:|---:|
| Constructor reader call | 730 | 1,002 | 213,066 | 220,790 |
| `onItem` toggle call | 741 | 1,475 | 216,269 | 223,993 |
| Reader URI string | 759 | 21 | 219,463 | 227,187 |
| Toggler URI string | 760 | 35 | 219,527 | 227,251 |
| `createTempFile` call | 760 | 68 | 219,560 | 227,284 |
| `moveTo` call | 760 | 132 | 219,624 | 227,348 |
| `deleteFile` call | 760 | 191 | 219,683 | 227,407 |
| `invalidate` call | 760 | 224 | 219,716 | 227,440 |

`onItem` method 741 first compares the selected item ID with `ENABLE_DEVP_SECURITY_KEY` at offsets 1,955-1,963, produces switch case 19 at 1,963, and its lookup table at 2,000 maps case 19 to method offset 1,470. The call to `DevepSecurityKeyEnabled()` is then at 1,475.

### ROV AppsListScreen

Path: `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/skins/default/swf/AppsListScreen.swf`  
CWS size: 117,093; uncompressed SWF size: 282,644; ABC stream begins at uncompressed SWF offset 14,120.

| Evidence | Method | Method-relative offset | ABC offset | Uncompressed SWF offset |
|---|---:|---:|---:|---:|
| Constructor reader call | 707 | 1,002 | 211,291 | 225,411 |
| `onItem` toggle call | 718 | 1,475 | 214,494 | 228,614 |
| Reader URI string | 736 | 21 | 217,688 | 231,808 |
| Toggler URI string | 737 | 35 | 217,752 | 231,872 |
| `createTempFile` call | 737 | 68 | 217,785 | 231,905 |
| `moveTo` call | 737 | 132 | 217,849 | 231,969 |
| `deleteFile` call | 737 | 191 | 217,908 | 232,028 |
| `invalidate` call | 737 | 224 | 217,941 | 232,061 |

The ROV methods have the same instruction sequence and embedded source-line mapping as the RU methods.

## Literal-reference census

The census searched the exact case-sensitive token `AMS_DEVELOPMENT` as ASCII and UTF-16LE where applicable. It also parsed ZIP/JAR and SWF compression rather than relying only on raw container bytes.

| Scope | Coverage | Result |
|---|---|---|
| Plain scripts, configs, resources, and native candidates | 848 files; 101,123,903 bytes | One hit: `jvm.sh` byte offset 1,493, line 59 |
| Native executables within that set | Every 188 ELF files; 86,650,026 bytes | Zero native-binary hits; `jvm.sh` remains the sole raw-set hit |
| JAR/ZIP containers | All 300 JARs and 21 ZIPs; 693,234,682 compressed bytes; 179 unique SHA-256 identities | 44,203 directory/entry records parsed; 35,253 non-media entry bodies (256,096,605 uncompressed bytes) searched; zero token hits in names or searched bodies; zero encrypted entries, unsupported compression methods, or parser errors |
| Residual non-media binary resources | 204 files; 24,389,410 bytes | Zero hits |
| SWF containers | All 1,086 physical SWFs; 141,193,109 compressed bytes; 482 unique identities; 102,440,607 unique uncompressed bytes | Exactly two unique flag-bearing files: RU and ROV `AppsListScreen.swf`; both decoded successfully |
| Parent boot image, historical opaque scan | `analysis_ra4_18.45.01/work/primary_iso/usr/share/IFS/ifs-cmc.bin`; 42,122,670 bytes | No raw ASCII/UTF-16LE hit; compressed hidden sections required decoding |
| Standard IFS materialization | 46 regular files; 2,949,863 bytes | Zero `AMS_DEVELOPMENT` hits; contains boot.sh |
| Three decoded hidden HBCIFS inventories | 778 regular files; 89,007,481 bytes (433/30,769,956; 219/22,931,139; 126/35,306,386) | Zero `AMS_DEVELOPMENT` hits, including the one zero-length file |
| Other opaque firmware payloads, exact raw search only | two Sierra Wireless CWE files and `analysis_ra4_18.45.01/work/installer_iso/usr/share/swdl.bin`; 60,921,110 bytes | Zero ASCII/UTF-16LE token hits |

Media bodies were intentionally excluded from the literal-body census: 6,009 media entries inside archives (101,467,818 declared uncompressed bytes), standalone speech datasets, raster/audio resources, and fonts. Their container names and surrounding manifests were still inventoried. Duplicate SWFs were hash-deduplicated for decompression but every physical path was assigned to an identity. The root source ZIP, `swdl.upd`, and ISO files were not reopened because their materialized canonical trees were the authorized analysis source.

Therefore, the strongest supportable statement is: the only positive literal consumer/writers remain jvm.sh and the equivalent RU/ROV AppsListScreen methods. The decoded standard IFS and all three hidden HBCIFS sections add no marker literal, and platform_ams_restart.lua is proved to watch AMS service ownership rather than the file. This is not proof against dynamically constructed strings, encrypted/encoded data, or a component outside the recovered images.

## Persistence and restart implications

### ETFS backing

The marker is placed at the root of the ETFS mount. The firmware identifies ETFS as a NAND partition:

- `analysis_ra4_18.45.01/work/primary_iso/etc/nand_partition.txt` lines 23-24 define `ETFS, 1156, 2047`.
- `analysis_ra4_18.45.01/work/primary_iso/usr/share/OTA/rb/ota/ifs_part_list` line 7 maps `/fs/etfs` with `name=ETFS`.
- `analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/etfs.sh` lines 183-197 select `fs-etfs-omap3530_micron` and mount it at `/fs/etfs`; lines 116-120 set `-e` for `format` or `erase` modes.

This is strong evidence that a successfully created marker is persistent filesystem state rather than a `/tmp`-style boot marker. Ordinary reboot persistence is highly likely, but it was not tested on hardware and the materialized corpus does not expose the normal boot driver's complete mount sequence.

### Update/format behavior

`analysis_ra4_18.45.01/work/primary_iso/usr/share/OTA/fota_installer/usr/share/scripts/fota_etfs.sh` makes the limitation explicit:

- lines 4-6 describe backing up, formatting, and restoring ETFS when the old driver/ECC path is detected;
- line 74 starts the new driver with `-e`, erasing ETFS on startup;
- line 84 restores the backup archive; and
- line 128 defines `FILE_TO_BACKUP=/fs/etfs/usr/`.

Because `/fs/etfs/AMS_DEVELOPMENT` is at the filesystem root rather than under `/fs/etfs/usr/`, that script does not include it in its declared backup set. If the old-driver backup/erase/restore path executes, this script cannot restore the marker. A later component could recreate it, but no such additional literal writer was found.

`analysis_ra4_18.45.01/work/primary_iso/etc/system_etfs_postinstall.txt` begins its explicit `[remove]` list at line 19 and does not name `AMS_DEVELOPMENT`. That negative fact does not protect the marker from whole-filesystem erase/format behavior.

### When the new state takes effect

The HMI method changes only the filesystem object and displayed label. The initial chain is now known: boot.sh starts connectivity_startup.sh at line 396 or 712; connectivity_startup.sh lines 23-24 invoke qon -d jvm.sh; jvm.sh samples the marker at lines 58-59 and creates AMS at line 63.

platform_ams_restart.lua provides a second, recovery-only route. Its functions 9/10, lines 218-250, subscribe to com.aicas.xlet.manager.AMS and start a 120,000 ms timer. Function 7, lines 183-209, executes the absolute jvm.sh path when AMS never appears or after AMS appears then disappears. Because jvm.sh re-samples the marker, that recovery can activate a persisted marker state.

It is not a marker watcher. It contains no AMS_DEVELOPMENT literal or file check, and the full 778-file hidden census contains no such literal. Thus:

1. the toggle does not alter an already-running AMS through its own method;
2. the state is guaranteed to affect the next initial or recovery execution of jvm.sh;
3. AMS failure/disappearance is a confirmed reinvocation trigger; and
4. marker change by itself is not a confirmed restart trigger.

## Findings in mission evidence format

### Finding 1 - exact effect on `-securityConfiguration`

**Finding:** A regular `/fs/etfs/AMS_DEVELOPMENT` file changes line 63's `-securityConfiguration` argument from the production JAR to the factory development JAR; `-secure` is unchanged.

**Confidence:** CONFIRMED

**Evidence:** `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/jvm.sh`

**Location:** production assignment line 58; `-f` override line 59; serial diagnostic line 61; AMS argument expansion line 63

**Supporting artifact:** launcher SHA-256 `9bd3c63a2c22c17f96e037102283f453afca43eb093bc1291d607a9805f829ec`; security-JAR hashes in the canonical-artifacts table

**Interpretation:** The marker is an existing stock selector for which signed factory security configuration AMS receives. It is not a patch and does not disable secure mode.

**Alternative explanation:** The native AMS parser was not executed, but its embedded usage and diagnostic strings independently describe the same `-secure` plus `-securityConfiguration` relationship.

**Next validation:** Read `/dev/ser3` and the AMS argument vector during two owner-authorized launches with known marker states.

### Finding 2 - HMI reader

**Finding:** `AppsListEngServiceMenu.isDevepSecurityKeyEnabled()` constructs `file:///fs/etfs/AMS_DEVELOPMENT` and returns `File.exists`.

**Confidence:** CONFIRMED

**Evidence:** the RU and ROV `AppsListScreen.swf` paths in the canonical-artifacts table

**Location:** RU method 759, ABC offsets 219,463 and 219,478 for URI/`exists`; ROV method 736, ABC offsets 217,688 and 217,703; embedded source lines 758-759

**Supporting artifact:** RU SHA-256 `ac817adc1471c07631e80eccddf8f3231b549d9fc725d8b27cb2d13d54212d67`; ROV SHA-256 `5bc1630f567c82494ab86e73c308ad2a8b9d341494a5f5de5f66a1505f1416e5`

**Interpretation:** The UI reads filesystem existence directly; it does not ask AMS or a service for the state.

**Alternative explanation:** The runtime implementation of `flash.filesystem.File.exists` could have platform-specific behavior for unusual path types.

**Next validation:** On an owner-controlled unit, compare the menu label with `stat`-equivalent file type results for the normal absent/regular-file states.

### Finding 3 - creator

**Finding:** When the reader returns false, `AppsListEngServiceMenu.DevepSecurityKeyEnabled()` creates a temporary file and moves it to the marker path with overwrite enabled.

**Confidence:** CONFIRMED

**Evidence:** the RU and ROV `AppsListScreen.swf` paths in the canonical-artifacts table

**Location:** embedded source lines 763-774; RU method 760 `createTempFile`/`moveTo` at ABC offsets 219,560/219,624; ROV method 737 at ABC offsets 217,785/217,849

**Supporting artifact:** on-disk hashes and offset table above

**Interpretation:** The engineering service-menu code is a direct filesystem creator. No intermediate service is needed by this bytecode path.

**Alternative explanation:** File creation can fail due to permissions, mount state, space, or cross-filesystem move behavior; the exception is caught and traced.

**Next validation:** With legitimate menu access, observe the destination's type, owner, mode, size, and timestamps immediately after a toggle; retain the stock authentication boundary.

### Finding 4 - deleter

**Finding:** When the reader returns true, the same method directly calls `deleteFile()` on the marker.

**Confidence:** CONFIRMED

**Evidence:** the RU and ROV `AppsListScreen.swf` paths in the canonical-artifacts table

**Location:** embedded source line 785; RU method 760 ABC offset 219,683; ROV method 737 ABC offset 217,908

**Supporting artifact:** on-disk hashes and offset table above

**Interpretation:** The factory menu option is a two-state toggle whose production action removes the development marker.

**Alternative explanation:** A deletion error may abort before the label update because the local exception table covers only the creation move, not the deletion instruction.

**Next validation:** Observe error handling and final marker state on a read-only or otherwise non-deletable test condition without changing security checks.

### Finding 5 - direct UI caller and upstream authorization

**Finding:** AppsListEngServiceMenu.onItem dispatches item 19 directly to the toggle, while reachability of that Service menu is positively gated by platform get_service_flags.eng_menu from a verified, head-unit-bound, unexpired service certificate.

**Confidence:** CONFIRMED

**Evidence:** RU/ROV AppsListScreen.swf; MainSupplement.swf VersionInfo methods; hidden platform_troubleshoot.lua

**Location:** RU/ROV item-19 offsets above; VersionInfo request 0x2D35B6 and response 0x2D3A64-0x2D3A8C; platform functions 2, 5, 6, 7, 11, 12, and 15

**Supporting artifact:** ROV AppsList SHA-256 5bc1630f567c82494ab86e73c308ad2a8b9d341494a5f5de5f66a1505f1416e5; MainSupplement SHA-256 e9d796ea4b4c83ed518bfe3b3c341e54e510a1ae0f78ebbffbd655b7c36a3258; troubleshoot SHA-256 8beab38ab164479a9fd815116dbfa02a48e3fa661724fa9c4273dc5884a1ba45

**Interpretation:** The factory menu gate is service-certificate authorization, not anti-theft PIN success. Once the menu is legitimately reached, item 19 performs the direct file toggle.

**Alternative explanation:** The service certificate's issuing/provisioning workflow remains outside these binaries; no attempt was made to forge or bypass it.

**Next validation:** Document the legitimate owner/factory service-certificate provisioning process without changing the verifier or gate.

### Finding 6 - no immediate AMS reload

**Finding:** The toggle method does not restart/reload AMS or reboot the unit; initial boot and AMS timeout/disappearance are the two recovered routes that later execute `jvm.sh` and re-sample the marker.

**Confidence:** CONFIRMED for the writer, initial chain, and recovered supervisor; HIGH negative bound for a marker-specific watcher in the decoded images

**Evidence:** RU method 760 and ROV method 737; `jvm.sh`; hidden `boot.sh`, `connectivity_startup.sh`, and `platform_ams_restart.lua`

**Location:** toggle source lines 761-790; jvm.sh lines 58-63; boot lines 396/712/747; connectivity lines 23-24; supervisor lines 183-250

**Supporting artifact:** hashes above; corpus-wide literal census found no additional execution-relevant reader

**Interpretation:** A label change is immediate. Activation occurs at a later jvm.sh evaluation; service failure is a proved trigger, marker change is not.

**Alternative explanation:** A dynamically constructed or out-of-corpus watcher remains possible, but no such edge appears in the standard or three hidden IFS inventories.

**Next validation:** Monitor process identity/arguments and filesystem access around a legitimate toggle, then trace any observed relaunch initiator.

### Finding 7 - ETFS persistence has an update boundary

**Finding:** The marker is stored on the ETFS NAND partition and should survive ordinary process restarts, but the documented FOTA erase/restore path backs up only `/fs/etfs/usr/` and therefore does not preserve this root-level file.

**Confidence:** HIGH for ordinary persistence; CONFIRMED for exclusion from this FOTA script's backup set

**Evidence:** `analysis_ra4_18.45.01/work/primary_iso/etc/nand_partition.txt`; `analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/etfs.sh`; `analysis_ra4_18.45.01/work/primary_iso/usr/share/OTA/fota_installer/usr/share/scripts/fota_etfs.sh`

**Location:** partition lines 23-24; mount/erase lines 116-120 and 183-197; FOTA erase/restore lines 74 and 84 and backup root line 128

**Supporting artifact:** `fota_etfs.sh` SHA-256 `f4e6a9a1e3cc353bd7ba43f7258c79047c9d68ba0882e042fbfd0870cd7eb842`; `etfs.sh` SHA-256 `dc85bb10caa81dddf76032dd93bea212c9d07b7ea27358bb8a6b60ca5563462c`; `nand_partition.txt` SHA-256 `338970e18000c8ebfdbbda321782a3ad61c58ae0605b9b0be140af1cca31a175`

**Interpretation:** Treat the flag as persistent operational state but not as guaranteed update- or format-surviving state.

**Alternative explanation:** Another post-update component could recreate or separately preserve the marker without containing the literal in the searched materialized corpus.

**Next validation:** Exercise ordinary reboot and the relevant authorized update path on recoverable test hardware while recording the flag before and after; do not infer factory-reset behavior from FOTA alone.

### Finding 8 - literal census completeness and limit

**Finding:** The only positive execution-relevant literal sites remain the shell consumer and equivalent RU/ROV HMI reader/writer/deleter implementations.

**Confidence:** HIGH within the documented decoded/searchable scope

**Evidence:** the materialized census plus 46 standard-IFS regular files and all 778 hidden-HBCIFS regular files

**Location:** jvm.sh line 59; RU methods 759-760; ROV methods 736-737

**Supporting artifact:** hidden segment image hashes 996c5a52cf7e72bb73d95e34e684196ca702061c6c5d9977415b014fbea57fbb, 57feaf9cfde58172f8a94049227ec895eb2f88607466297e31f8732f201b8512, and aae02c6ea6873e66cde49e814299d43cbeb38e686352fd86324ac91a1feafc42

**Interpretation:** No recovered hidden native service or Lua script directly reads the marker. The AMS supervisor's restart effect is indirect through jvm.sh.

**Alternative explanation:** Dynamic string construction, encrypted/encoded resources, or code outside the recovered images can evade literal searching.

**Next validation:** Trace filesystem APIs with constructed paths and capture runtime file opens on owner-controlled hardware.

## Commands and tests run

- Reused the complete prior primary/secondary/installer script, ELF, archive, and SWF census.
- Parsed the standard IFS and all three type-8 length-framed hidden HBCIFS sections statically; no vendor payload was run.
- Exact-scanned 46 standard-IFS regular files (2,949,863 bytes) and 778 hidden-HBCIFS regular files (89,007,481 bytes) for AMS_DEVELOPMENT; zero hits.
- Decoded platform_troubleshoot.lua and platform_ams_restart.lua as Lua 5.1 with function/source-line/instruction-level traces.
- Traced boot.sh and connectivity_startup.sh to the initial qon -d jvm.sh call.
- Mapped native AppManager enableEngMenu and defineOptions ARM references; no AMS_DEVELOPMENT or drm/d option registration was found.
- Reverified artifact paths, sizes, SHA-256 values, Markdown tables, and Git staging state.

## Unresolved gaps

1. The legitimate issuing/provisioning process for a valid RA4 service certificate remains outside the recovered code; no bypass or forgery was attempted.
2. No connection to developerId, getDeveloperToken, or xlet.developerToken is established by the flag methods.
3. No marker-specific automatic restart is established. A controlled, reversible supported AMS restart mechanism still must be designed.
4. Marker permissions, owner/group, exact content/size, and power-loss durability have not been observed on hardware.
5. Ordinary reboot persistence is strongly supported by NAND-backed ETFS but not dynamically demonstrated.
6. Factory-reset behavior and update variants beyond the documented FOTA ETFS path remain unknown.
7. The producer of the separate /fs/etfs/enableEngMenu AppManager catalog marker is not in the current corpus.
8. AppManager `-d` is conclusively unregistered and ignored in this binary; the DRM checker initializes enabled and is called during install preparation. The script variable and `/fs/etfs/disableDRM` marker preserve historical configuration vocabulary but do not disable the checker (`appManager` VAs `0x195FFC`, `0x196028`, `0x1D9FC8`, `0x1DA96C`, `0x1DA1C8`, `0x181318`, `0x181338`, `0x1957A4`, and `0x1802C0`).
9. Dynamic path construction and components outside the decoded standard/hidden images remain outside the literal census.
