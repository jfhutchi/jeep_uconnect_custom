# RA4 18.45.01 AMS Startup Chain

## Scope and safety boundary

This report verifies the actual RA4 18.45.01 boot-to-AMS chain: the standard boot script, connectivity launcher, `jvm.sh`, AppManager startup, and the AMS service-loss supervisor. All evidence comes from the canonical materialized corpus plus statically extracted hidden QNX IFS sections. No vendor executable was run and no stock firmware file was changed.

Canonical roots used:

- `analysis_ra4_18.45.01/work/primary_iso/`
- `analysis_ra4_18.45.01/work/secondary_iso/`
- `analysis_ra4_18.45.01/work/installer_iso/`
- `analysis_ra4_18.45.01/work/hidden_hbc_ifs/` (ignored local static extraction)

The stock source ZIP, `swdl.upd`, and the three ISO files were not opened or modified in this pass.

## Result

The initial startup predecessor is now CONFIRMED. The standard boot script starts AppManager, starts connectivity_startup.sh in either wake path, and that script invokes qon -d jvm.sh. jvm.sh selects one of two factory security-configuration JARs and starts AMS with -secure unchanged.

The recovered chain is:

    standard boot /bin/boot.sh
      -> embCell path: AppManager line 371, connectivity_startup.sh line 396
      -> CAN path: AppManager line 465, connectivity_startup.sh line 712
         -> /bin/connectivity_startup.sh lines 23-24
            -> qon -d jvm.sh
               -> /fs/mmc0/app/bin/jvm.sh
                  -> production security.jar by default
                  -> development/security.jar iff -f /fs/etfs/AMS_DEVELOPMENT
                  -> AMS ... -securityConfiguration selected.jar -secure &
      -> waits for com.aicas.xlet.manager.AMS at boot lines 398 or 722
      -> boot line 747 launches platform_ams_restart.lua

platform_ams_restart.lua is a service-availability supervisor, not a marker watcher. It subscribes to com.aicas.xlet.manager.AMS and uses a 120,000 ms timer. If AMS never appears or later disappears, it terminates/restarts the relevant processes and executes /fs/mmc0/app/bin/jvm.sh, which then re-samples AMS_DEVELOPMENT.

The exact caller is resolved, while bare-name command resolution for connectivity_startup.sh and jvm.sh still depends on the inherited boot/qon environment.

## Artifact identities

| Role | Canonical extracted path | Runtime path or command | Size | SHA-256 |
|---|---|---|---:|---|
| Parent boot image | `analysis_ra4_18.45.01/work/primary_iso/usr/share/IFS/ifs-cmc.bin` | QNX multi-section boot image | 42,122,670 | `ea6797be141763f35f3059ad858eefbf54f730af0155bebc7af411c47d80ba92` |
| Standard boot controller | `analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/files/bin/boot.sh` | `/bin/boot.sh` | 29,268 | `c801d473b0b49e8242114635f4022cc67ccbe03093fec188de3b7188dd636ecf` |
| Connectivity launcher | `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/bin/connectivity_startup.sh` | `/bin/connectivity_startup.sh` | 939 | `2d693484a49539ae1f83512bac068580014b1c2dcbb2c5885609e01726e3502f` |
| Launcher | `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/jvm.sh` | `/fs/mmc0/app/bin/jvm.sh` | 2,795 | `9bd3c63a2c22c17f96e037102283f453afca43eb093bc1291d607a9805f829ec` |
| AMS supervisor | `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/platform_ams_restart.lua` | `/usr/bin/cmc/service/platform/platform_ams_restart.lua` | 7,514 | `264e5aaa6e2e09e8bb86a881f4919a66220d1cad2c7ce9443416e5d35f9f720f` |
| AppManager | `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/bin/appManager` | `/bin/appManager` | 1,268,061 | `608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591` |
| AMS executable | `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/AMS` | `/fs/mmc0/app/bin/AMS` | 11,956,352 | `96683b789ecf06a8575915d0b446b532e1f4ee87feb31d925cb7ba3d7d324d27` |
| Runtime inventory | `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/sys_ref.txt` | maps primary files into `/fs/mmc0/app` | 212,887 | `5661157dde84c863f4f2bac6bbbe87f8f34121daeb6326a806c82fa948994b70` |
| AMS properties | `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/data/ams.properties` | `/fs/mmc1/kona/data/ams.properties` | 287 | `790847a3a00a62cf0886565f49d103f5a16fd20fe975fced96d3427cafd0fde0` |
| Initializer | `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/extension/ams_initializer.jar` | `/fs/mmc1/kona/extension/ams_initializer.jar` | 21,917 | `b40c69ff6cfd3e31e097c5ae33e71f1a314ce8aee2e3a734589f3025a98e959c` |
| Xlet extension library | `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/lib/kona.jar` | `/fs/mmc1/kona/lib/kona.jar` | 3,062,680 | `19390472018f02d998690b982f00eb68da5d40d7a8d6fba91499677651015f92` |
| Production security configuration | `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/security/security.jar` | `/fs/mmc1/kona/security/security.jar` | 7,504 | `29a8a350ef0facc30c1c98e5250563a4020ad9c1a243f13e795e2e68e3bd74e7` |
| Development security configuration | `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/security/development/security.jar` | `/fs/mmc1/kona/security/development/security.jar` | 7,371 | `fbe5314ab304e122162aae20ace46999b93832fc4c7451439f4ada430eccc8a7` |

The MD5 values in the firmware reference manifests also match the materialized files. In particular, `sys_ref.txt` line 1 maps MD5 `3bcbb69024a980f90818fdae56717ff1` to `/fs/mmc0/app/bin/AMS`, and line 61 maps MD5 `d5bf474c67d037f419c1cf2aa8610d24` to `/fs/mmc0/app/bin/jvm.sh`. `kona_ref.txt` lines 1, 4, 6, 11, and 12 map the properties, initializer, Kona library, development security JAR, and production security JAR to their `/fs/mmc1/kona/...` runtime paths.

## Recovered boot and restart chain

### Initial launch

CONFIRMED: boot.sh is the standard IFS entry at decompressed-image offset 0x179EF0. It starts onoff/main.lua at line 336, derives boottype at lines 339-354, and has two mutually selected startup paths:

- embCell: lines 362-371 create the Xlet RMS directory if necessary and start appManager; lines 395-398 start connectivity_startup.sh and wait up to 30 seconds for the AMS service.
- CAN: lines 455-465 perform the same AppManager start; lines 704-712 start connectivity_startup.sh; lines 720-722 wait for the AMS service.

connectivity_startup.sh is at hidden HBC image offset 0x637BC6. Lines 23-24 say start AMS and execute qon -d jvm.sh. Here -d is an option to qon, not an AMS or jvm.sh option. This is the direct initial predecessor that was absent from the earlier materialized-only analysis.

boot.sh line 747 later starts Lua platform_ams_restart.lua.

### Service-loss recovery

platform_ams_restart.lua is a compiled Lua 5.1 chunk at hidden image offset 0x1D1E7C8.

- Function 10, source/debug lines 237-250, creates and starts the 120,000 ms timer, subscribes to owner changes for com.aicas.xlet.manager.AMS, and checks current ownership.
- Function 9, lines 218-234, records service appearance/disappearance and calls restartAMS.
- Function 7, lines 183-209, handles the actual recovery. If AMS never appeared and the timer expires, lines 187-191 terminate AMS, execute /fs/mmc0/app/bin/jvm.sh, and re-arm the timer. If AMS appeared then disappeared, lines 194-207 terminate AMS and AppManager, restart AppManager, wait for com.harman.service.AppManager, execute jvm.sh, and re-arm.

This proves a later jvm.sh re-evaluation after AMS failure. It does not establish that changing AMS_DEVELOPMENT triggers a restart: the script contains no such pathname or file check, and the complete 778-file hidden-HBC census found no AMS_DEVELOPMENT literal.

### AppManager -d boundary

boot.sh unconditionally assigns disableDRMArg=-d at lines 367 and 461 and includes it in the AppManager commands at lines 371 and 465. On the service-loss path, platform_ams_restart.lua function 7 selects command text without -d at line 199 when /fs/etfs/disableDRM is absent and with -d at line 201 when it is present.

Those scripts prove only that the argument is supplied or omitted. The completed native analysis resolves its effect for this binary. `processOptions` at VA `0x195FFC` constructs a new local Poco `OptionSet` at `0x196028` and registers only `silent/s`, `json/j`, `presub/p`, `watchdog/w`, `config/c`, `tp`, and `help/h`. The `OptionProcessor` stores that sole local set at `0x1D9FC8`; the single-dash path at `0x1DA96C` looks up the substring after `-` as a short option, and the common lookup begins from that local set at `0x1DA1C8`. Therefore `-d` cannot resolve through an inherited set, short-option clustering, or long-name-prefix behavior. The process-level exception handler at `0x196E00` logs the diagnostic at VA `0x21284C` that an unknown option is ignored.

A dormant normalized-name branch for `drm` at `0x19718C` calls setter `0x16D548`, but `drm` is also absent from the option set, so no parsed route reaches it. The DRM-checker subobject constructor at `0x181318` initializes its enable byte to `1` at `0x181338`; install preparation calls the checker at `0x1957A4`, and checker `0x1801D4` reads that same enable byte at `0x1802C0`. The confirmed result is that DRM checking defaults enabled and stock `-d` is unregistered and ignored. The variable and marker retain historical configuration vocabulary but do not implement a DRM-disable transition in RA4 18.45.01.

This AppManager argument is separate from AMS_DEVELOPMENT and jvm.sh's securityConfiguration selection.

## Exact launcher reconstruction

The executable line in the stock file is one physical shell line at `jvm.sh` line 63:

```sh
AMS -installationDirectory /fs/mmc1/xletsdir -extensionDirectory /fs/mmc1/kona/extension -initializerJar ams_initializer.jar -xletExtensionDirectory /fs/mmc1/kona/lib -amsPropertyFile /fs/mmc1/kona/data/ams.properties -securityConfiguration "$AMS_SECURITY_JAR" -secure &
```

Reformatted without changing its arguments:

```sh
AMS \
  -installationDirectory /fs/mmc1/xletsdir \
  -extensionDirectory /fs/mmc1/kona/extension \
  -initializerJar ams_initializer.jar \
  -xletExtensionDirectory /fs/mmc1/kona/lib \
  -amsPropertyFile /fs/mmc1/kona/data/ams.properties \
  -securityConfiguration "$AMS_SECURITY_JAR" \
  -secure &
```

The trailing `&` backgrounds AMS. The shell therefore does not wait for AMS to initialize or exit before it begins the OTA and SMM tail at lines 69-92.

## Line-by-line verification

Blank lines are omitted from this table, but every executable statement and comment block in the 94-line file is accounted for.

| Lines | Exact role | Evidence-based interpretation |
|---:|---|---|
| 1 | `#!/bin/sh` | Requests the target system shell. The exact QNX shell implementation/version is not identified here. |
| 3-5 | Exports `KD_QNX_WINDOWPROPERTY_CLASS=FlashWindow`, `KD_QNX_WINDOWPROPERTY_ID_STRING=AMS`, and `KD_WINDOWPROPERTY_VISIBILITY=false` | Supplies window identity/visibility state to AMS or its child runtime. |
| 9-11 | Exports `SCREENSIZE=640x480`, `WIDTH=640`, and `HEIGHT=480` | Fixes the AMS/HMI display dimensions used by this launch. |
| 15-17 | Exports `AMS_CLIP_WITH_SCISSORS=false`, `AMS_JAVA_STACK_SIZE=20k`, and `AMS_NATIVE_STACK_SIZE=64k` | Configures clipping and per-thread Java/native stack settings. |
| 20-22 | Exports `AMS_HEAP_SIZE=50M`, `AMS_NUM_THREADS=140`, and `AMS_MAX_NUM_THREADS=140` | Configures heap and thread limits. |
| 25-30 | Comments call the default priority map optimal; line 29 exports `AMS_PRIORITY_MAP=0=1,1=7,2..4=9,5..37=10,38..39=11`; line 30 exports `AMS_TEXTURE_CACHE_SIZE=14336` | Supplies scheduler mapping and texture-cache size. The comments advise retaining the map. |
| 34 | Exports `AMS_MAX_NUMBER_GC_CALLS=6` | Caps an AMS garbage-collection setting; exact native enforcement is not traced here. |
| 37-42 | Comments say the variables force Xlet budgets when an Xlet omits them and are required for AMS 1.0.48; exports period `10000ms`, running `6000ms`, paused `2000ms` | Establishes the stock fallback Xlet budget values. |
| 44-47 | Comments identify GL ES renderer budgets; exports period `10000ms` and budget `6000ms` | Establishes renderer scheduling budget values. |
| 49-52 | Comment identifies Jamaica boosting; exports all three boost switches as `no` | Disables the three named boost mechanisms for this launch. |
| 54-56 | Echoes the three Jamaica boost values | Writes diagnostic values to inherited standard output. These lines do not redirect to `/dev/ser3`. |
| 58 | Exports production `AMS_SECURITY_JAR` path | Unconditional default for every invocation. |
| 59 | Tests `[ -f /fs/etfs/AMS_DEVELOPMENT ]` and, only on success, overwrites `AMS_SECURITY_JAR` with the development path | The shell selector is a regular-file test, not a content, signature, token, or PIN test. |
| 61 | Writes `Launching AMS with $AMS_SECURITY_JAR` to `/dev/ser3` | Provides a direct runtime observation point for the selected path. |
| 63 | Starts the reconstructed AMS command with fixed `-secure` and backgrounds it | This is the only AMS launch statement in the script. |
| 69-84 | Conditionally copies four Redbend OTA metadata files from `/fs/mmc0/dupd/rb/ota/` to `/fs/mmc3/update/ota/` | Runs after AMS was started; it does not feed an option into that already-created process. |
| 86-87 | Explains the SMM dependency and waits up to 120 seconds for `/tmp/SoftwareUpdateInitDone` | This wait occurs after the background AMS launch. It does not gate AMS startup. |
| 89-92 | If `smm.exe` exists, changes to its directory and runs it with `nice -n1` in the background | The only `cd` in the file is after AMS was launched, so it cannot establish AMS's launch directory. |

There is no `PATH` assignment, no `cd` before line 63, no `source`/`.` statement, no selected-JAR existence/readability check, no retry, and no foreground wait for AMS. These absent operations are material when reconstructing what is inherited versus set locally.

## Dynamic input analysis

| Command input | Proven source | What remains dynamic or unresolved |
|---|---|---|
| Bare executable name `AMS` | `jvm.sh` line 63; native file mapped to `/fs/mmc0/app/bin/AMS` by `sys_ref.txt` line 1 | `jvm.sh` does not set `PATH`. The expected runtime file is confirmed, but actual command resolution depends on the launcher's inherited environment. |
| `/fs/mmc1/xletsdir` | `jvm.sh` line 63 | This is mutable installed-Xlet state. The stock base tree contains only `xlets/magic.txt`, while KIM reference manifests enumerate runtime Xlet content. `factory_cleanup.sh` lines 71-72 erase installed Xlets and repopulate from `/fs/mmc1/kona/preload/xlets/`. |
| `/fs/mmc1/kona/extension` and `ams_initializer.jar` | `jvm.sh` line 63; `kona_ref.txt` line 4 | Native AMS usage at file offset 10,900,989 describes the initializer JAR as relative to `extensionDirectory`. In-memory JAR inspection found `META-INF/MANIFEST.MF` line 4: `AMS-Initializer-Class: com.harman.ams.initializer.Initializer` (entry local-header offset 43, uncompressed length 166). |
| `/fs/mmc1/kona/lib` | `jvm.sh` line 63; `kona_ref.txt` line 6 | The directory includes `kona.jar`; AMS class loading behavior beyond the command option is not reconstructed here. |
| `/fs/mmc1/kona/data/ams.properties` | `jvm.sh` line 63; `kona_ref.txt` line 1 | The stock file supplies Xlet timeouts (lines 1-4), memory limits (5-6), priorities (7-11), and `maxGLESNativeData` (12). Runtime replacement or mutation was not evaluated. |
| `AMS_SECURITY_JAR` | `jvm.sh` lines 58-59 | Its value depends on the marker's file type at this exact launch. Contents of the marker are never read. |
| `-secure` | Fixed at `jvm.sh` line 63 | It is present in both branches. Development selection is not equivalent to turning secure mode off. |
| Process environment and working directory | boot.sh -> connectivity_startup.sh -> qon -d jvm.sh | The caller is confirmed, but neither boot.sh nor connectivity_startup.sh sets PATH; qon/bare-name resolution, user/group, and current directory remain inherited. |

The native AMS executable independently corroborates the command syntax. Its SHA-256 is shown above, and direct byte searches locate:

| Native AMS decimal file offset | String |
|---:|---|
| 10,810,699 | `No Public Keys are available. The AMS cannot run any xlets...` diagnostic |
| 10,810,781 | `-secure` within the diagnostic |
| 10,810,810 | `-securityConfiguration` within the diagnostic |
| 10,900,811 | `-secure` in the CLI usage text |
| 10,900,821 | `-securityConfiguration` in the CLI usage text |
| 10,900,861 | `-installationDirectory` |
| 10,900,893 | `-extensionDirectory` |
| 10,900,921 | `-xletExtensionDirectory` |
| 10,900,953 | `-amsPropertyFile` |
| 10,900,989 | `-initializerJar` |

The diagnostic explicitly says that `-secure` also requires `-securityConfiguration`. This supports the interpretation that line 63 passes the selected JAR as a security configuration, not as an ordinary application JAR.

## Findings in mission evidence format

### Finding 1 - canonical launcher and runtime identity

**Finding:** The canonical extracted `jvm.sh` is the stock file mapped to `/fs/mmc0/app/bin/jvm.sh`.

**Confidence:** CONFIRMED

**Evidence:** `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/jvm.sh`; `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/sys_ref.txt`

**Location:** complete launcher; `sys_ref.txt` line 61

**Supporting artifact:** launcher size 2,795; MD5 `d5bf474c67d037f419c1cf2aa8610d24`; SHA-256 `9bd3c63a2c22c17f96e037102283f453afca43eb093bc1291d607a9805f829ec`

**Interpretation:** The launcher analyzed here is anchored both by content hash and the firmware's runtime-path manifest.

**Alternative explanation:** A running unit could contain a locally changed `/fs/mmc0/app/bin/jvm.sh`; that would be a runtime-state difference, not a difference in this stock 18.45.01 corpus.

**Next validation:** On an owner-controlled unit, hash the runtime file read-only and compare it with the stock MD5/SHA-256.

### Finding 2 - complete AMS invocation

**Finding:** `jvm.sh` launches one background AMS process with the seven options reconstructed above; `-secure` is unconditional.

**Confidence:** CONFIRMED

**Evidence:** `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/jvm.sh`

**Location:** line 63

**Supporting artifact:** native option strings in `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/AMS`, especially decimal offsets 10,900,811-10,900,989; AMS SHA-256 `96683b789ecf06a8575915d0b446b532e1f4ee87feb31d925cb7ba3d7d324d27`

**Interpretation:** Development selection changes the security-configuration input but does not suppress AMS secure mode.

**Alternative explanation:** Native option parsing behavior was not dynamically executed, so an undocumented parser quirk is possible; the stock script and native usage/diagnostic strings agree on the intended syntax.

**Next validation:** Capture the process argument vector and line 61 serial diagnostic during a normal, owner-authorized boot without altering files.

### Finding 3 - launch inputs are partly fixed and partly runtime state

**Finding:** The extension, library, property, and security paths are fixed in `jvm.sh`, while installed Xlets, the flag, `PATH`, current directory, and filesystem contents remain dynamic.

**Confidence:** CONFIRMED for the script and stock path mappings; HIGH for the expected runtime interpretation

**Evidence:** `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/jvm.sh`; `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/kona_ref.txt`; `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/factory_cleanup.sh`

**Location:** `jvm.sh` lines 58-63; `kona_ref.txt` lines 1, 4, 6, 11, 12; `factory_cleanup.sh` lines 71-72

**Supporting artifact:** hashes in the artifact-identity table; `factory_cleanup.sh` SHA-256 `56d7213cc768f5e3c9b5606a3c49a7e70832f12024697c8121a0a55a6edf9aa5`

**Interpretation:** A reproducible launch analysis must capture runtime state in addition to matching stock files.

**Alternative explanation:** Other boot-time mount or overlay logic, not materialized here, could replace a fixed-looking runtime path.

**Next validation:** Record mounts, hashes, `PATH`, current directory, and Xlet directory inventory immediately before `jvm.sh` on an owner-controlled unit.

### Finding 4 - the script samples the marker only at process creation

**Finding:** The selected security JAR is computed once before AMS is started, so a later marker change cannot alter the already-created AMS process through this script.

**Confidence:** CONFIRMED

**Evidence:** `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/jvm.sh`

**Location:** selection at lines 58-59; expansion into the new process at line 63

**Supporting artifact:** launcher SHA-256 `9bd3c63a2c22c17f96e037102283f453afca43eb093bc1291d607a9805f829ec`

**Interpretation:** A marker change affects a future execution of the launch chain. No dynamic reload instruction appears in `jvm.sh`.

**Alternative explanation:** AMS or another component could independently monitor the marker after launch, but no such reader was found in the execution-relevant corpus search documented in `reports/ams_development_flag.md`.

**Next validation:** Observe whether any process accesses the marker after AMS startup and compare AMS process arguments before/after an owner-authorized UI toggle.

### Finding 5 - startup and recovery predecessors recovered

**Finding:** boot.sh starts connectivity_startup.sh, which invokes qon -d jvm.sh; platform_ams_restart.lua separately reinvokes the absolute jvm.sh path after AMS startup failure or service disappearance.

**Confidence:** CONFIRMED

**Evidence:** analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/files/bin/boot.sh; hidden segment_001a0000 files bin/connectivity_startup.sh and usr/bin/cmc/service/platform/platform_ams_restart.lua

**Location:** boot.sh lines 396, 712, and 747; connectivity_startup.sh lines 23-24; supervisor functions 7, 9, and 10 at source/debug lines 183-250

**Supporting artifact:** boot.sh SHA-256 c801d473b0b49e8242114635f4022cc67ccbe03093fec188de3b7188dd636ecf; connectivity launcher SHA-256 2d693484a49539ae1f83512bac068580014b1c2dcbb2c5885609e01726e3502f; supervisor SHA-256 264e5aaa6e2e09e8bb86a881f4919a66220d1cad2c7ce9443416e5d35f9f720f

**Interpretation:** Initial boot and service-loss recovery both reach the same stock jvm.sh selector. Only the latter uses the absolute path directly.

**Alternative explanation:** The initial bare jvm.sh command could resolve differently if the inherited qon environment differs from the firmware's intended PATH; the referenced stock runtime mapping remains the expected target.

**Next validation:** Read-only capture of the qon child command, process executable, and argv on an owner-controlled unit.

## Commands and tests run

- Parsed the standard and three hidden QNX imagefs sections statically; no vendor executable or target script was run.
- Read boot.sh and connectivity_startup.sh line-by-line and matched both wake branches to qon -d jvm.sh.
- Decoded platform_ams_restart.lua as Lua 5.1, including all instructions, constants, upvalues, source/debug lines, and service/timer branches in functions 7, 9, and 10.
- Re-ran an exact AMS_DEVELOPMENT scan across all 778 hidden regular files totaling 89,007,481 bytes; zero hits.
- Mapped AppManager ARM MOVW/MOVT operands and its defineOptions registrations; no drm/d registration was present in that routine.
- Reverified source artifact sizes/SHA-256 values and the jvm.sh/kona runtime path manifests.
- Used direct read-only Git child processes; no staging, commit, or firmware mutation occurred.

## Unresolved gaps

1. Initial bare-name jvm.sh resolution still depends on the inherited qon/PATH environment, although its direct caller and expected stock target are now known.
2. The inherited working directory, user/group, capabilities, and exact process environment at both initial and recovery launch remain unknown.
3. The runtime failure mode for a missing/unreadable selected security JAR was not executed.
4. No live argv or /dev/ser3 capture confirms the selected branch on a particular head unit.
5. No marker-specific restart/reload watcher was found; a controlled, reversible supported restart mechanism must still be designed.
6. AppManager's native treatment of the supplied -d argument is UNKNOWN because its local option registry contains no drm/d registration.
7. The complete mutable contents and mount/overlay history of /fs/mmc1/xletsdir remain installation-state dependent.
