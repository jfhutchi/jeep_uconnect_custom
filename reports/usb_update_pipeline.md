# RA4 18.45.01 Legitimate USB Software-Update Pipeline

## Scope and method

This report reconstructs the stock update path from the owner-supplied RA4 18.45.01 package and its canonical materialized trees. It does not describe how to forge an update, does not recover or replace signing keys, and does not weaken any check. No vendor executable was run and no container was unpacked again. `reports/corpus_inventory.md:62` identifies the materialized `work/*_iso/` directories as the analysis source of record.

Confidence labels are **[CONFIRMED]** for direct evidence, **[HIGH]** for independently supported reconstruction, **[INFERRED]** for the most likely explanation, and **[UNKNOWN]** where a closed or unmaterialized stage prevents proof.

## Container topology and identities

**[CONFIRMED]** The authoritative source and update-image identities are recorded at `reports/corpus_inventory.md:64-73`:

| Layer | Bytes | SHA-256 | Role |
|---|---:|---|---|
| `Uconnect_VP4,18.45.01-My13-17.zip` | 1,266,203,571 | `5388d9310737dc52a65f2825131043362254b3592da2584302b81bc0447f9fdd` | Owner-supplied distribution archive |
| `analysis_ra4_18.45.01/extracted/swdl.upd` | 1,426,147,328 | `c704eb723d6697fd98959888274dda18362c23ce6f66b505e01ce1983148c344` | USB software-download image |
| `analysis_ra4_18.45.01/work/swdl_iso/installer.iso` | 34,830,624 | `893c1e9dbc16b42d3a0eba8f8470336ec84618d59980735a1e61a58499b830a5` | Installer runtime, scripts, and bootstrap material |
| `analysis_ra4_18.45.01/work/swdl_iso/primary.iso` | 375,191,552 | `8086b7b6a413c9fd2718d21bd7d027c79c0dc36a1e1d43ea1f7358fd33b890ff` | System, native services, AMS, firmware, and OTA payloads |
| `analysis_ra4_18.45.01/work/swdl_iso/secondary.iso` | 1,015,750,656 | `cd6df921c1da876cb5652f011bd3f1cc6a751a818b3455f478b4e1f7fc7edcb5` | Kona/KIM/Xlets, speech, and application data |

The static route is:

```text
USB root: swdl.upd
        |
        v
mcd rule SWDL -> resident swdlMediaDetect/loader.lua
        |
        v
mount outer image; authenticate nested ISOs; load installer manifest
        |
        +--> installer.iso -> installer runtime and validation/update scripts
        +--> primary.iso   -> copied to MMC, authenticated, then mounted
        +--> secondary.iso -> mounted from USB, authenticated and monitored
                                 |
                                 v
                      manifest.lua ordered units
                                 |
                                 v
                 softwareupdate.lua state machine
                                 |
                                 v
             IFS/MMC/Xlets/modem/XM/HD/OTA destinations
                                 |
                                 v
                   completion state + head-unit reset
```

## Distribution checksum versus device trust

**[CONFIRMED]** The Windows helper `checkswdl.bat` invokes `md5deep.exe -l -m swdl.upd.md5 swdl.upd` and prints good/bad status (`analysis_ra4_18.45.01/extracted/checkswdl.bat:5-49`, SHA-256 `07bf9f4ec9fc113f3aa6aa314a0d63a85f6c83745ee5e8acc7f4492a9ad7eaf1`). `analysis_ra4_18.45.01/extracted/swdl.upd.md5:1` contains `0898515ad6bfdd25406e91a17b364e71` (file SHA-256 `9ad6cb0ac8bece58f4bd5d89c64ddbdb9ea73bb80757befb801144dd7a7bb7c4`).

**[CONFIRMED]** That MD5 is a PC-side distribution-integrity convenience only. The head-unit code has a separate RSA/SHA-256 ISO authentication path described below. Treating the MD5 file as an on-device authorization mechanism would be incorrect.

## USB recognition and bootstrap boundary

**[CONFIRMED]** `analysis_ra4_18.45.01/work/installer_iso/usr/share/swdl.bin` is a 33,027,366-byte QNX IFS/bootstrap image with SHA-256 `9e2006d5531ba3dbae30cd23d61f85850de7be052965e363e03c3ff27ce69eec`. It contains `SWDL` at file offset `0xaa13a7` and `swdl.upd,a` at `0xaa13ca`.

**[CONFIRMED]** The decoded runtime HBC image supplies the previously missing normal-operation detector. `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/usr/bin/cmc/service/swdlMediaDetect/loader.lua` is 22,538 bytes, SHA-256 `f562650958dc487d8558571744cc517ba583550b29c79dba4f335fc07c47e885` (inventory line 223). It configures MCD insertion rule `SWDL`, image name `swdl.upd`, outer mount `/fs/swdl`, installer mount `/fs/installer`, manifest `etc/manifest.lua`, nested names `installer.iso`/`primary.iso`/`secondary.iso`, and key `/etc/keys/swdl.pub` (`loader.lua:70-80`). `notifyOnInsert` accepts only the `usb0` event, mounts the outer image, authenticates each present nested ISO, requires and mounts `installer.iso`, and loads its manifest (`loader.lua:497-568`).

**[CONFIRMED]** `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/usr/bin/cmc/service/swdlMediaDetect/swdlMediaDetect.lua` is 18,115 bytes, SHA-256 `0bf54e5866ad0a8bff467e592e5ee46d877ba957ee6f1f266f7d94191001088c` (inventory line 228). Its `processManifest` dispatches a manifest with `external.start_script` without entering the normal update-confirm/reset path (`swdlMediaDetect.lua:242-266`). `loader.executeExternalScript` exports `ISO_PATH`, `USB_PATH`, and `INSTALLERISO_PATH`, then executes the manifest-selected script beneath the authenticated installer ISO (`loader.lua:595-621`). For the stock 18.45.01 manifest, no `external` member exists; its normal `parts` table is at `installer_iso/etc/manifest.lua:230-237`.

**[UNKNOWN]** The `swdl.bin` strings `SWDL` and `swdl.upd,a` still leave the update-mode bootstrap's exact `,a` flag and boot handoff opaque. This no longer blocks the resident USB-recognition, mount, nested-ISO authentication, manifest-load, or external-script environment chain. The outer `swdl.upd` is mounted before the visible nested-ISO checks; the trusted executable/manifest boundary is the fully authenticated nested installer ISO.

## Signed ISO header format and authentication

**[CONFIRMED]** Each nested ISO starts with a 32,768-byte custom header organized as 128 256-byte blocks. Block 1 contains an ASCII build descriptor beginning with `10 184501 MY17 NA VP4`; the exact raw strings and header hashes are:

| ISO | Block-1 ASCII prefix | SHA-256 of first 32 KiB | Block 126 SHA-256 | Block 127 SHA-256 |
|---|---|---|---|---|
| `installer.iso` | `10184501MY17NAVP434799616` | `9ab684c1b6af57f03f9658f3a8c314c297a8e5563f74b81419155c7db97630ed` | `e15d4c5eae3f37cc843b14e204fbbd3441ac6226d6fe01ba9088fb8f3f023340` | `37bf87a3e1fb7e6ae36dddfd5f7c70c46aaee0123f64af8fa558e5b2e6069b49` |
| `primary.iso` | `10184501MY17NAVP4375191552` | `f82c15e76146315bd76ae6072386c345f5d1ff63f0df36c2c900675a71988606` | `5341e6b2646979a70e57653007a1f310169421ec9bdd9f1a5648f75ade005af1` | `b8b0897bcd65ebc956b79d27954da75eb60231a9d4316083082550d4f052f060` |
| `secondary.iso` | `10184501MY17NAVP41015750656` | `2bc7708b314d462fac259a90969c8646dee50366aa28d4e5467b702f1ca72ff4` | `5341e6b2646979a70e57653007a1f310169421ec9bdd9f1a5648f75ade005af1` | `e3d88b8227e77d9ab3ef397d1c1d12c9de8d9960973235e5bd3c18fad4f225b6` |

The field interpretation is based on the parser, not just visual guessing: ISO format version 1.0, build 18.45.01, model MY17, market NA, product VP4, followed by a size field. The installer size field does not cleanly equal the outer file size, so this report does not over-interpret that value.

Static disassembly of `analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/update/isochk.lua` (9,509 bytes, SHA-256 `51b4777fa98e8a0f338336b2ebacd7cdccd9e1493817c76f3ef41cad33be2e9f`) shows this validation order in its main validation prototype (embedded source-line metadata 170-392):

1. **[CONFIRMED]** Read the first 32,768 bytes (`0x15ce-0x15da`) and parse build information from block 1.
2. **[CONFIRMED]** Treat block 0 as the header signature, block 127 as signed ISO-hash material, and blocks 1-127 as the signed header region (`0x1626-0x170f`). Verify the header with RSA/SHA-256 using `/etc/keys/swdl.pub` (`0x178f`; the key-path string occurs at raw offset `0x17b1`).
3. **[CONFIRMED]** Compare target variant/product/market/model-year values and reject a prohibited downgrade (`0x190b-0x1c40`). The manifest independently requires NA, VP4, MY17, and SHA-256 (`analysis_ra4_18.45.01/work/installer_iso/etc/manifest.lua:8-20`).
4. **[CONFIRMED]** Recover the signed ISO hash with RSA, SHA-256 the ISO data section, compare hashes, and verify the declared size (`0x1cad-0x1ee9`).
5. **[CONFIRMED]** Extract the install-monitor hash file (IMHF), hash it, recover signed block 126, and compare (`0x1fac-0x2185`).

`analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/update/isochkSingleIso.lua` (6,233 bytes, SHA-256 `465a1bf350b680c8cf30db7ea6420f5b8710e68f83c49123408b6c80525d6254`) implements the same header/signature/data-hash/size checks for one ISO (validation prototype source-line metadata 128-300; instruction records `0x0f6a-0x17f2`) without the multi-ISO IMHF phase.

**[CONFIRMED]** The validation public key is recovered at `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/etc/keys/swdl.pub`: 451 bytes, SHA-256 `804e7cdf410c74a2b6ac52084d9b24c7b5becfd5bbb66a32819356d01f5b676e`, inventory line 53. It is an RSA-2048 `PUBLIC KEY`, not signing material.

An independent read-only reproduction of the stock algorithm verified all three nested ISOs. For each image, Node's RSA/SHA-256 verifier accepted block 0 as the signature over header bytes 256 through 32,767. RSA PKCS#1 public recovery of block 127 returned exactly 32 bytes, and that value equaled SHA-256 of the complete ISO data region from byte 32,768 through EOF:

| ISO | Header signature | Recovered block-127 data hash | Recomputed data hash |
|---|---|---|---|
| `installer.iso` | valid | `880561a00022ea658a211a76947abb2e2cef1882e64372c6209b3ec7ee7337c1` | match |
| `primary.iso` | valid | `fd5e4ab6409eb6e583c7ccf82d0a7be08980a8b081677efc32f0b0fe94dbe5c6` | match |
| `secondary.iso` | valid | `22468c3ba91c125559f6269c444a5c32fa437c08cac8d4b304f55e8ec5761898` | match |

This proves the stock header-signature and full-data-hash layers with the recovered device public key. It does not expose a private key, authorize a changed ISO, or prove every later IMHF sampling transition.

## Installer startup, staging, and continuous checking

`analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/install.sh` is SHA-256 `92ef7c2bcc475fe8e15c6e9b0a5c61d6ec8782ac86377e5f3003fb1aa668ff4e`. Its stock sequence is:

1. **[CONFIRMED]** Select `/fs/usb0` or `/mnt/usb0` as `USB_STICK` and prefer installer-ISO binaries/libraries (`install.sh:8-21`).
2. **[CONFIRMED]** Start the update-side network/IPC, DBus/SvcIPC, and HMI runtime before the validated installer state machine (`install.sh:25-55`).
3. **[CONFIRMED]** Unless persistent `ISO_COPY_MMC_AUTHENTICATED` already exists, copy `primary.iso` from USB to MMC with `isoCopy.lua`, then run `isochk.lua`; copy or verification failures exit immediately (`install.sh:63-92`). `analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/update/isoCopy.lua` has SHA-256 `1b4cbb7e441e18ff56c374d42eb223439a26b990c85a639ef8efc12b1da4d9eb`.
4. **[CONFIRMED]** Mount the authenticated primary ISO from MMC and mount `secondary.iso` directly from USB (`install.sh:94-116`).
5. **[CONFIRMED]** Start the update watchdog. On a fresh run, start `installmonitor.lua` against `secondary.iso`, save `/tmp/imhf.txt` to MMC, set the RAM-only `/tmp/SECONDARY_ISO_AUTHENTICATED`, and persist `TOTAL_PREUNITS`; on a resumed run, reload these values from MMC (`install.sh:118-142`).
6. **[CONFIRMED]** If the installer-authenticated flag is present, persist `ISO_COPY_MMC_AUTHENTICATED`, sync, and invoke `softwareupdate.lua` with the installer/primary/secondary mount paths and hash/size inputs (`install.sh:144-155`).

`analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/update/installmonitor.lua` (SHA-256 `4a00f74ff195528310d45375608361744142a1990e42701fc5837da5c0d28dad`) chooses a random monitored block, reads the expected 32-byte value from `/tmp/imhf.txt`, SHA-256 hashes the corresponding ISO block, and reports a mismatch (instruction/constant region `0x0585-0x083c`).

**[HIGH]** Authentication is therefore not just a one-time header check: the streamed secondary medium is also sampled continuously against signed IMHF material while installation proceeds. The exact sampling strength and full IMHF construction algorithm remain **[UNKNOWN]**.

## Ordered manifest and destinations

**[CONFIRMED]** The manifest declares version `18.45.01`, module type `APP`, target version file `/etc/version.txt`, and the exact 13-unit order (`analysis_ra4_18.45.01/work/installer_iso/etc/manifest.lua:226-236`; manifest SHA-256 `104d18836f41919f1f789110697eebc5e6deee998de79fb5a4c0af35a042770f`).

| Order | Unit | ISO | Installer / destination evidence |
|---:|---|---|---|
| 1 | SYSTEM CHECK | installer | Target compatibility and SHA-256 requirement, lines 8-20 |
| 2 | IOC-BOOTLOADER | primary | `ioc_bootloader`, firmware paths, lines 22-38 |
| 3 | IOC | primary | `ioc`, with FOTA copy destination `/fs/mmc0/fota_fw/usr/share/V850`, lines 39-59 |
| 4 | System | primary | `ifs`, NAND IPL/IFS payloads, lines 60-75 |
| 5 | System Data | primary | `mmc` -> `/fs/mmc0/app`, lines 76-89 |
| 6 | Speech | secondary | `mmc` -> `/fs/mmc0/speech_service`, lines 90-103 |
| 7 | EQ | primary | `mmc` -> `/fs/mmc0/eq`, lines 104-112 |
| 8 | Apps | secondary | `xlets` -> `/fs/mmc1/`, source `usr/share/XLETS`, lines 113-126 |
| 9 | Embedded Air Card | primary | Sierra flasher; retained FOTA copy -> `/fs/mmc0/fota_fw/usr/share/SIERRA_WIRELESS`, lines 127-156 |
| 10 | XM Pre Update | primary | Intermediate XM firmware and IOC prerequisite, lines 157-172 |
| 11 | XM Update | primary | XM flasher; retained FOTA copy -> `/fs/mmc0/fota_fw/usr/share/XM_FIRMWARE`, lines 173-197 |
| 12 | HD Update | primary | HD flasher; retained FOTA copy -> `/fs/mmc0/fota_fw/usr/share/HD_FIRMWARE`, lines 198-214 |
| 13 | OTA Update | primary | `mmc` -> `/fs/mmc0/dupd`, lines 215-223 |

**[CONFIRMED]** `analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/update/installer/files_pre_post_modifier.lua` (SHA-256 `65d5d8b0c1f8679924d0341842eacb519f30071e7fd75847bb9d080e32e948b8`) delegates update file actions to `analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/update/parseConfig.lua` (SHA-256 `aefeeb8b58e7241ea01dd30ca7bd7391fbfa0b74eb0e4510edb34064124e929a`). The bytecode recognizes create, remove, copy, link, chmod, backup, and restore sections. A literal scan found no active `[backup]` or `[restore]` section in the canonical text/config files, so parser capability is not evidence of stock general rollback.

## Storage and operating modes

**[CONFIRMED]** `mmc.sh` assigns `/fs/mmc0` to application/system data, `/fs/mmc1` to Xlets, `/fs/mmc2` to Xlet data, and `/fs/mmc3` to OTA data (`analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/mmc.sh:24-40`, SHA-256 `25ba3eb651531317a6a4db7176198c93c26868d88da286db36d06696b39a344a`).

- **[CONFIRMED] Application mode:** `/fs/mmc0` and `/fs/mmc1` are automatically mounted read-only, while `/fs/mmc2` and `/fs/mmc3` are writable (`mmc.sh:407-435`).
- **[CONFIRMED] Update mode:** The script uses writable update settings and explicitly mounts all four filesystems (`mmc.sh:436-444,549-600`).
- **[HIGH]** The update environment is therefore the privileged write window for system and Xlet payloads; normal application mode protects the two code-bearing partitions with read-only mounts.

## Resume, restart, failure modes, and rollback

Static disassembly of `analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/update/softwareupdate.lua` (12,709 bytes, SHA-256 `64d42e3d2fa73ac94c60ebbb2f659d7b79c7eaf98c9c6e9fa0daceb3c7a3d85a`) and the readable stock FOTA sibling (`analysis_ra4_18.45.01/work/primary_iso/usr/share/OTA/fota_installer/usr/share/scripts/update/softwareupdate.lua`, SHA-256 `77ea2cb8134596b6c8bab1b0dcd868d665db661533ee7fcdd60ecf9de629af6`) establish the state machine.

### Resume and restart

- **[CONFIRMED]** The installer reads `getUpdateInProgress` before iterating units (readable sibling `:285-299`; direct bytecode prototype 8, source-line metadata 265-456).
- **[CONFIRMED]** Before a unit that requires a different IOC mode, it persists the current unit/expected mode and resets into that mode (readable sibling `:330-348`; direct bytecode `0x18c4-0x190c`).
- **[CONFIRMED]** `RETRY_SWDL_UNIT` persists the unit and substate, sets the expected IOC mode, and resets to retry (readable sibling `:360-395,421-432`; direct bytecode `0x1ad8-0x1b50`).
- **[CONFIRMED]** Persistent `ISO_COPY_MMC_AUTHENTICATED`, `TOTAL_PREUNITS`, and `imhf.txt` allow the primary-copy/authentication work and monitor setup to survive those resets (`install.sh:68-69,121-150`).
- **[CONFIRMED]** Direct-update success syncs, cleans temporary authentication/resume files, clears update mode, resets update-in-progress, sets update-done, writes the software version, and resets the head unit (direct bytecode prototype 16, source-line metadata 589-661, instruction records `0x2a48-0x2acc`).

### Failure modes

| Result | Confirmed behavior |
|---|---|
| `STOP_SWDL_DONT_CLEAR_UPDATE` | Send error and remain in SWDL/update mode (`analysis_ra4_18.45.01/work/primary_iso/usr/share/OTA/fota_installer/usr/share/scripts/update/softwareupdate.lua:401-405`) |
| `STOP_SWDL_CLEAR_UPDATE` | Send error and clear update mode (`:406-416`) |
| `CONTINUE_SWDL` | Report a unit error but continue with later units (`:417-420`) |
| `RETRY_SWDL_UNIT` | Save unit/substate and reset into the required IOC mode (`:421-432`) |
| Unexpected/no error code | Stop the update (`:433-447`) |
| Direct-update terminal failure | Sync, log failure, reset update-in-progress, and wait for USB ejection to reset (direct bytecode `0x2ad4-0x2b04`) |
| USB eject / reset service | Clear or normalize update state and reset (`0x2f87-0x300b`, `0x30fd-0x3131`) |

### What rollback does and does not mean here

- **[CONFIRMED] Resumability:** The update remembers a unit/substate and can reset into the mode needed to resume or retry. That is not the same as reverting already-written units.
- **[CONFIRMED] Narrow Take Back preservation:** During `MMC_TB` repartitioning only, `mmc.sh` copies `/fs/mmc1/*` to `/fs/mmc0/mmc1_bk`, preserves/migrates OTA data, repartitions/formats, then restores and deletes the backup (`analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/mmc.sh:111-204,488-499,598-600`).
- **[CONFIRMED] No active config backup directives:** Although `analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/update/parseConfig.lua` implements `[backup]` and `[restore]`, no such section occurs in the materialized stock update configs.
- **[CONFIRMED] Factory Xlet copy is not atomic recovery:** Recovered `qkcp` SHA-256 `aa5605bdd69581aad74c05213553ccac2468399de18f539cf1c2029d58207198` proves `-h` is a 56-byte shared-memory progress channel, not manifest verification. The KIM caller supplies no `-f/-r` checkpoint recovery; the copier creates/truncates final destinations directly and imports no rename/remove rollback primitive. A failed Apps/KIM unit can therefore leave partial or mixed Xlet/preload state (`reports/qkcp_kim_copy_semantics.md`).
- **[UNKNOWN] General rollback:** No general A/B system slot, per-unit undo log, previous-IFS restore path, or reverse flash sequence was identified. A stop/clear/reset branch may leave earlier successful units installed while later units are not.
- **[UNKNOWN] Closed flasher recovery:** IOC, modem, XM, and HD installers may have device-specific recovery behavior not visible in the top-level state machine. This report does not equate absence of top-level rollback with proof that every peripheral lacks a bootloader recovery mode.

## Open gaps

1. **[UNKNOWN]** Update-mode `swdl.bin` boot handoff and the meaning of its `swdl.upd,a` flag. The resident detector and earliest visible nested-ISO signature decisions are now confirmed in `swdlMediaDetect/loader.lua`.
2. **[UNKNOWN]** Exact IMHF generation, random-block selection strength, and how the monitor reacts at every failure point. Header signatures and block-127 full-data hashes are independently verified.
3. **[UNKNOWN]** Unit-specific transactional/recovery properties of the IOC, Sierra, XM, and HD flashers.
4. **[UNKNOWN]** A general system rollback mechanism. Only resume/retry and Take Back partition preservation are confirmed; factory KIM copy non-atomicity is now directly proved.

## Read-only verification commands

From the repository root:

```powershell
Get-FileHash 'Uconnect_VP4,18.45.01-My13-17.zip' -Algorithm SHA256
Get-FileHash analysis_ra4_18.45.01/extracted/swdl.upd -Algorithm SHA256
Get-FileHash analysis_ra4_18.45.01/work/swdl_iso/installer.iso -Algorithm SHA256
Get-FileHash analysis_ra4_18.45.01/work/swdl_iso/primary.iso -Algorithm SHA256
Get-FileHash analysis_ra4_18.45.01/work/swdl_iso/secondary.iso -Algorithm SHA256
Get-FileHash analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/etc/keys/swdl.pub -Algorithm SHA256
Get-FileHash analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/update/isochk.lua -Algorithm SHA256
Get-FileHash analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/update/softwareupdate.lua -Algorithm SHA256
Select-String -Path analysis_ra4_18.45.01/work/installer_iso/etc/manifest.lua -Pattern 'local version','parts =','dst_dir','iso_unit'
Select-String -Path analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/install.sh -Pattern 'isoCopy.lua','isochk.lua','installmonitor.lua','softwareupdate.lua','ISO_COPY_MMC_AUTHENTICATED'
Select-String -Path analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/mmc.sh -Pattern 'mmc1TBbackup','mmc1TBrestore','application mode','update mode'
git diff --check -- reports/usb_update_pipeline.md
```
