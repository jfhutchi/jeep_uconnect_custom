# 2017Q2 VP4 Navigation Map Update Reverse-Engineering Findings

Updated: 2026-09-05

This report records owner-authorized, read-only analysis of an original Uconnect navigation update image recovered as `uconnectmapimage.img`. The goal is to understand the legitimate update architecture, media layout, compatibility logic, and runtime behavior without deriving activation secrets, forging licenses, bypassing signing, or modifying the original image.

## Evidence labels

- **[CONFIRMED]** directly established from the update image, extracted metadata, runtime log, or static disassembly.
- **[HIGH]** strongly supported by multiple observations but not yet tied to a named vendor type or field.
- **[INFERRED]** best current interpretation; not yet proved.
- **[UNKNOWN]** unresolved.

No original FCA/Harman/NNG binary, ISO, executable, license file, activation material, or vendor payload is committed by this report.

## 1. FAT32 image geometry and corruption

**[CONFIRMED]** The image contains an MBR partition of type `0x0C` beginning at LBA 8064.

Recovered geometry:

- partition byte offset: `4,128,768`
- bytes/sector: 512
- sectors/cluster: 32
- cluster size: 16,384 bytes
- reserved sectors: 1,696
- FAT copies: 2
- FAT size: 7,392 sectors
- FAT1 offset: `4,997,120`
- FAT2 offset: `8,781,824`
- data-area offset: `12,566,528`
- root cluster: 2
- usable clusters: 945,921

**[CONFIRMED]** The primary boot sector is damaged. Its bytes-per-sector field decodes as `0x4200` / 16896 and FS version as 2, both invalid for the recovered filesystem. Backup boot sector 8 restores 512-byte sectors and FS version 0 but has a high-bit error in total sectors. Primary and backup differ in 65 bytes, mostly single-bit corruption.

**[CONFIRMED]** FAT1 and FAT2 differ heavily: 256,722 mismatches across valid entries, about 27.1% of the usable FAT. Most mismatches are low-Hamming-distance bit errors.

**[CONFIRMED]** FAT1 is the authoritative baseline for the known `swdl.upd` chain. Clusters 3-2401 form 2,399 contiguous clusters and hash exactly to the sidecar MD5. FAT1 describes all 2,399 chain transitions correctly; FAT2 describes only 1,715. FAT1 can still contain rare isolated corruption, demonstrated by the M30 VR payload where FAT2/contiguous data supplied the correct next cluster.

Extraction policy used during analysis:

1. prefer FAT1;
2. verify with sidecar/internal hashes;
3. if verification fails, test contiguous bytes and FAT2 before declaring content corrupt.

## 2. Root media and recovered helpers

**[CONFIRMED]** The root contains the update payload, navigation tree, validation helper, update log, and `md5deep` tooling. Several recorded root starting clusters are themselves bit-corrupted, but the files were recovered structurally.

Recovered helper artifacts included:

- `checkswdl.bat` - verifies `swdl.upd` using `md5deep.exe`
- `KaliSWDL.log` - Harman/Jenkins build log material
- `MD5DEEP.EXE` - valid 32-bit PE build of md5deep/hashdeep tooling
- `README.TXT` - records `NAV_DB=CMCN4VP4NA;HMNA2017Q2;20180723`, branch `trunk_MY16`, and CL `1417938`
- `swdlLog.txt` - successful on-unit software-update log

## 3. Outer SWDL and nested installer ISO

**[CONFIRMED]** `swdl.upd` is exactly 39,303,168 bytes and its MD5 matches the root sidecar:

- MD5: `09ed62270b203e8dc4ff4bdb088def5b`
- SHA-256: `3247f2bcac304e354ffa14ea363c1f61a4945f407da6be75416f29b7f5e70e9a`

It contains an ISO9660 filesystem beginning at offset `0x8000`.

**[CONFIRMED]** The outer ISO contains `installer.iso`, 38,930,432 bytes:

- MD5: `332e5928fc4161479ce4f4612404ad87`
- SHA-256: `ec7ea4aab191e08914b28bc73a867e0c9c24a1989dde107ee00fed6792ec5483`

The installer contains `BIN`, `ETC`, `LIB`, `NAV_dup_Missing_Files`, and `USR` trees.

## 4. Manifest and legitimate update sequence

**[CONFIRMED]** The manifest defines two normal update parts:

1. `SYSTEM CHECK` using `system_module_check`
2. `Nav Dealer Update` using `nav-sync`

The manifest selects market `NA`, product `VP4`, model-year family `MY17`, enables pre/post MD5, sets destination `/fs/mmc0/nav`, and names the external navigation-activation startup script.

**[CONFIRMED]** `nav-sync` calls the navigation update service to obtain copy/remove lists, performs optional pre-MD5, copies returned files with `qkcp`, removes returned files, performs post-MD5, stops the synchronization tool, and then sets the destination tree read-only.

**[CONFIRMED]** The external navigation-activation path is separate from the ordinary manifest `parts` sequence. Static analysis shows activation requests are made through Navigation/NavigationUpdate services and that an accepted activation code is stored internally before reset. This report intentionally does not derive or disclose any activation value.

## 5. Navigation database identity and missing-file repair

**[CONFIRMED]** `dbver.pinfo` contains:

`CMCN4VP4NA;HMNA2017Q2;20180723`

Its MD5 sidecar verifies exactly.

**[CONFIRMED]** The installer also carries `NAV_dup_Missing_Files` branches for older 2016Q4 databases. `naviSyncTools.lua` reads the currently installed `/fs/mmc0/nav/NNG/content/dbver.pinfo`, constructs a matching old-version path, and copies missing files into the current NNG tree before normal synchronization.

This explains why the package includes checksum sidecars for the older installed baseline as well as the newer 2017Q2 payload.

## 6. Successful runtime update evidence

**[CONFIRMED]** The recovered `swdlLog.txt` records a successful update on a MY14 VP4/RA4-family unit.

Observed runtime sequence:

- total units: 3
- unit 2: `SYSTEM CHECK`
- reset from application mode into BOLO/update mode
- unit 3: `Nav Dealer Update`
- Synctool-generated add/remove plan
- pre/update/post MD5 validation
- copying of the selected MY14 navigation license
- stopping NaviSyncTool
- ECU part-number update
- successful completion

**[CONFIRMED]** The selected license copied during this run was:

`Harman_CMC_VP4_NA_VP4_2017Q2_UPDATE_MY14_REVA.lyc`

**[CONFIRMED]** The log records:

- old part number: `68224525AH`
- new ECU part number: `68224525AM`
- `ECU part number Update Successful`
- `Software Update successfully completed`
- resulting software version: `17.11.17`

The log therefore proves successful execution, not merely package structure.

## 7. License corpus structure

**[CONFIRMED]** The recovered `LICENSE` directory contains 17 license triplets (`.lyc.stm`, `.lyc`, `.lyc.md5`) covering 524/VP4 variants from MY13 through MY18. Every `.lyc.md5` matches its corresponding `.lyc`.

Each `.lyc` is 6,488 bytes and begins with the same 8-byte container header:

- type: 2
- declared body size: `0x1950` / 6,480 bytes

The 6,480-byte body is exactly 405 16-byte blocks.

**[CONFIRMED]** Pairwise structural analysis found a universal 16-byte-periodic relative transform between the 17 license bodies:

- pair/lane tests: 2,176
- transitivity violations: 0
- expected-mask support: 95.3612%
- best-possible support: 95.3612%

After applying only relative per-license normalization:

- 6,177 / 6,480 bytes are identical across all 17
- 385 / 405 complete 16-byte blocks are identical
- 303 byte positions are intentionally individualized

The individualized regions are confined to:

- body `0x0000-0x00FF` / file `0x0008-0x0107`: 256 bytes
- three 4-byte fields in body block 16
- body `0x192D-0x194F` / file `0x1935-0x1957`: 35 bytes

All three 4-byte fields are unique across all 17 licenses; none is a simple shared model-year, revision, or 524/VP4 family field.

**Boundary:** this evidence is used only to characterize the container. No absolute mask, activation secret, signing key, or reusable license material is derived or disclosed.

## 8. Synctool ELF extraction

**[CONFIRMED]** The NNG synchronization binary was extracted read-only from `installer.iso` for static analysis:

- size: 2,226,976 bytes
- MD5: `60d613b94735e370f5b84c1ad42da687`
- SHA-256: `aa2e2c425d42a5f60427a89817f676b0d32b3ce73057d89355248acc24d4e330`
- ELF: 32-bit little-endian ARM
- entry point: `0x00103EE0`
- sections: 28
- `.dynsym`, `.dynstr`, `.text`, `.rodata` present
- no `.symtab`
- no debug sections

The binary is stripped, but literal strings and ARM cross-references allow useful control-flow recovery.

## 9. Recovered Synctool control-flow regions

**[CONFIRMED]** Static ARM analysis isolates the following routines:

| Purpose | Address range |
| --- | --- |
| App-SKU handling | `0x00110E6C-0x00111090` |
| `device.nng` parsing | `0x00116178-0x00116574` |
| request-code routine 1 | `0x0011CB14-0x0011CE3C` |
| request-code routine 2 | `0x0011CE3C-0x0011D164` |
| license scan/classification | `0x0011D454-0x0011DEA0` |
| license-distributor lookup | `0x0011F5E0-0x0011F830` |

The request-code routines are separate from the license classifier. Compatibility is evaluated first; activation handling is a later branch.

## 10. License classifier states

**[CONFIRMED]** The classifier emits these states/strings:

- `LICENSES_ALL_VALID`
- `LICENSE_ACTIVATION_NEEDED`
- `LICENSE_INVALID`
- `Found activable license record <%s> type:0x%x`
- `Found incompatible activable license record <%s> type:0x%x`
- `Found invalid license record <%s> type:0x%x`

**[HIGH]** Caller behavior and state assignments support this return enum:

- 0 = all valid
- 1 = activation needed
- 2 = invalid

An invalid state dominates activation-needed state.

## 11. Named license types

**[CONFIRMED]** Static type-name switching maps:

- `0x61CB7108` -> `LICTYPE~Application`
- `0x61CB7112` -> `LICTYPE~User Interface`

Distributor mapping also resolves:

- `0x61CB7108` -> `ILICENSE_DISTRIBUTOR_APPLICATION`
- `0x61CB7112` -> `ILICENSE_DISTRIBUTOR_GUI`

Helper `0x001051F4` recognizes Application-license records and queries property `0x420005FF`.

Helper `0x00105194` recognizes User-Interface-license records and queries property `0x0000000C`.

These are distinct selectors; the setup path also uses a plain `0x000005FF` selector and must not be conflated with `0x420005FF`.

## 12. Device-side versus license-side identity

**[CONFIRMED]** `device.nng` parsing logs:

`Device.nng read, valid:%d t:%s %s appcid:0x%x`

The parsed software-identity schema includes:

- `swid_info`
- `device_swid`
- `application_skuid`

`application_skuid` is stored in the larger SWID/device object around offset `+0x2F4`.

**[CONFIRMED]** The license-side model separately exposes:

- `license`
- `has_license`
- `has_license_of_type`
- `has_license_for_module`
- `license_model`

`license_model` is stored around offset `+0x1D0` in the parsed license object.

This establishes a real architectural split between device/application identity and license-policy metadata.

## 13. Dynamic compatibility vector

**[CONFIRMED]** The license scanner uses object fields:

- `r6 + 0x34` = vector begin
- `r6 + 0x38` = vector end
- `r6 + 0x3C` = vector capacity

The code behaves as a `std::vector<uint32_t>`.

At scanner entry, `end` is reset to `begin`, emptying the vector while retaining its allocation. Synctool then walks an existing device-side record collection, extracts 32-bit values from records, and inserts them into the vector in sorted order.

When an update license is activatable, Synctool extracts another 32-bit metadata value and binary-searches this vector:

- value found -> `Found incompatible activable license record`
- value not found -> `Found activable license record`

**[CONFIRMED]** This incompatibility set is therefore built dynamically from existing device-side license metadata. It is not a hard-coded MY13/MY14/MY15 blacklist.

**[UNKNOWN]** The exact semantic name of the 32-bit value stored in that vector is not yet proved. `application_skuid` and `license_model` are both confirmed named fields elsewhere in the object model, but neither has yet been connected by data-flow proof to this vector.

## 14. App SKU routine: current stopping point

**[CONFIRMED]** The App-SKU routine logs `Loading licenses from device folder <%s>` and later `App SKU ID %d`.

Immediately before logging the SKU, it invokes a virtual method with selector `0x284`, stores the returned integer at object offset `+0x24`, and logs that value as the App SKU ID.

This is the strongest current hook for the next session.

## 15. Working model

The current evidence supports the following legitimate flow:

```text
device.nng / SWID information
        |
        +--> device_swid
        +--> application_skuid
        +--> App SKU lookup (selector 0x284 -> object +0x24)
        |
        v
existing device-side license records
        |
        +--> build sorted 32-bit compatibility/incompatibility vector
        |
        v
update-media .lyc records
        |
        +--> already valid
        +--> activatable
        |      +--> metadata present in incompatibility vector -> incompatible activatable
        |      `--> metadata absent -> activatable
        `--> invalid
                |
                v
classifier result
        |
        +--> all valid
        +--> activation needed
        `--> invalid
                |
                v
separate activation/request-code path only when required
```

The recovered successful runtime log proves that this process ultimately selected the MY14 REVA update license for the MY14 VP4 unit and completed the update successfully.

## 16. Open questions / next work

Highest-value next steps:

1. Trace selector `0x284` in the App-SKU routine and determine the exact source of the logged App SKU ID.
2. Prove whether the scanner's sorted 32-bit compatibility vector stores `application_skuid`, `license_model`, or another named NNG identifier.
3. Trace the two callers of the license scanner far enough to document how device identity and media-license collections are supplied.
4. Preserve the boundary between compatibility research and activation-secret derivation.

## 17. Safety and handling notes

- Keep `uconnectmapimage.img` read-only.
- Do not run filesystem repair tools such as `chkdsk` against the original image.
- Do not commit recovered FCA/Harman/NNG binaries, ISOs, `.lyc` files, keys, or vendor content.
- Prefer hashes, offsets, control-flow facts, and independently reproducible metadata in repository documentation.
- Do not derive, disclose, brute-force, forge, or reuse activation codes, signing secrets, or license credentials.
