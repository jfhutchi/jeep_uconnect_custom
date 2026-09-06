# 2017Q2 VP4 Navigation Map Update Reverse-Engineering Findings

Updated: 2026-09-05

This report records owner-authorized, read-only analysis of an original Uconnect navigation update image recovered as `uconnectmapimage.img`. The goal is to understand the legitimate update architecture, media layout, compatibility logic, and runtime behavior without deriving activation secrets, forging licenses, bypassing signing, or modifying the original image.

## Evidence labels

- **[CONFIRMED]** directly established from the update image, extracted metadata, runtime log, or static disassembly.
- **[HIGH]** strongly supported by multiple observations but not yet tied to a named vendor type or field.
- **[INFERRED]** best current interpretation; not yet proved.
- **[UNKNOWN]** unresolved.

No original FCA/Harman/NNG binary, ISO, executable, license file, activation material, or vendor payload is committed by this report.

The continued identity analysis is documented in detail in
[Synctool device and license-selection pipeline](synctool_device_license_selection.md).
It corrects two earlier hypotheses: `application_skuid` is an output property
populated by a license-manager query, and the scanner's incompatibility vector
stores runtime source-container ordinals, not App SKU/model-year IDs.

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
| App-SKU handling (code; exclusive end) | `0x00110E6C-0x00111078` |
| App-SKU caller (code; exclusive end) | `0x0011A9B4-0x0011AF68` |
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

**[CONFIRMED]** Scanner state assignments and caller checks at `0x001250FC-0x00125104` and `0x00125170` establish this return enum:

- 0 = all valid
- 1 = activation needed
- 2 = invalid

Once set, state 2 dominates activation-needed. However, an invalid record sets
state 2 only when context policy byte `+0x51` is zero (`0x0011D89C-0x0011D8AC`).
The context constructors initialize `+0x51/+0x52` to one; these are copied to
result policy bytes `+0/+1`. The normal caller can therefore discard unsuitable
record groups and continue. Enum 0 is not proof that every raw media record
was valid. This qualifies the earlier enum-only model.

## 11. Named license types

**[CONFIRMED]** Static type-name switching maps:

- `0x61CB7108` -> `LICTYPE~Application`
- `0x61CB7112` -> `LICTYPE~User Interface`

Distributor mapping also resolves:

- `0x61CB7108` -> `ILICENSE_DISTRIBUTOR_APPLICATION`
- `0x61CB7112` -> `ILICENSE_DISTRIBUTOR_GUI`

Helper `0x001051F4` recognizes Application-license records and queries property `0x420005FF`.

Helper `0x00105194` recognizes User-Interface-license records and queries property `0x0000000C`.

The setup path supplies plain `0x000005FF` to the Application distributor's
secondary interface slot `+0x28`. That interface encodes the type prefix,
producing `0x420005FF`. The two values are therefore related at a proved adapter
boundary, not interchangeable at arbitrary call sites. The GUI query remains
a distinct selector.

## 12. Device-side versus license-side identity

**[CONFIRMED]** `device.nng` parsing logs:

`Device.nng read, valid:%d t:%s %s appcid:0x%x`

The license manager's named property schema includes:

- `swid_info`
- `device_swid`
- `application_skuid`

**[CONFIRMED]** `application_skuid` names a property subobject at license-manager
offset `+0x2F4`, not a raw integer established as input parsed from `device.nng`.
Callback `0x0023FFD4` calls manager slot `+0x58` with selector zero at
`0x0023FFF8`, formats the returned integer, and updates the property at
`0x00240010`. The implementation substitutes selector 6 or 7 for zero.
The logged App-SKU query instead supplies `0x284`; equality of the two outputs
is not established.

**[CONFIRMED]** The license-side model separately exposes:

- `license`
- `has_license`
- `has_license_of_type`
- `has_license_for_module`
- `license_model`

**[CONFIRMED]** `license_model` is another named property subobject of the
license manager at `+0x1D0`, initialized at `0x00258710` and registered at
`0x002590F4`. Those references do not identify a numeric field in a parsed
license record. The previous "parsed license object" interpretation was too
strong and is superseded by the constructor and property-registration evidence.

**[CONFIRMED]** The separate compact `device.nng` object stores its `appcid`
at `+0x10`; helper `0x00105118` reads it from file offset `0x5C`, called at
`0x001163CC`. No direct flow from this word to logged context `+0x24` has been
proved. Protected device-identity processing is not emulated here.

## 13. Dynamic compatibility vector

**[CONFIRMED]** The license scanner uses object fields:

- `r6 + 0x34` = vector begin
- `r6 + 0x38` = vector end
- `r6 + 0x3C` = vector capacity

The code behaves as a `std::vector<uint32_t>`.

At scanner entry, `end` is reset to `begin`, emptying the vector while retaining
its allocation. Synctool queries the Application distributor for the `0x5FF`
collection, unwraps each record, and checks record slot `+0x24` at
`0x0011D50C`. Already-valid (nonzero) records are skipped. The other records
supply metadata `+0x10` at `0x0011D54C`, inserted sorted and unique.

When an update license is activatable, Synctool extracts another 32-bit metadata value and binary-searches this vector:

- value found -> `Found incompatible activable license record`
- value not found -> GUI exception check, otherwise `Found activable license record`

The GUI helper at `0x0011DBAC` can instead branch to accepted-list insertion
at `0x0011DDE8`. Result list `+4` is therefore accepted/valid, not exclusively
records whose raw validity predicate was already true.

**[CONFIRMED]** This incompatibility set is therefore built dynamically from existing device-side license metadata. It is not a hard-coded MY13/MY14/MY15 blacklist.

**[CONFIRMED]** Both record metadata accessors resolve through vtable
`0x00311740`: slot `+0x10 -> 0x002627CC` and slot `+0x14 -> 0x002627E4`
return record `+0x54`. App SKU is metadata `+8` (record `+0x5C`), whereas
the scanner key is metadata `+0x10` (record `+0x64`).

**[CONFIRMED]** The key's construction is now traced: source-identity map
insertion increments manager `+0x208` at `0x0026F938-0x0026F948`; an entry
retains that count at `0x00257D38-0x00257D40`; it is passed to container
constructor `0x002577B8` and stored at container `+0x34` (`0x002578B8`).
Loader `0x002544F0-0x00254508` transfers it to temporary metadata `+0x10`,
and record constructor `0x00245134-0x0024513C` copies it to record `+0x64`.

**[HIGH]** Its appropriate descriptive name is **runtime source-container
identity ordinal**, not application SKU, model-year ID, or module ID. The map
uses a 16-byte key derived from provider slot `+0x40` and container segment
offset/length. The provider is now resolved to the composite filesystem class:
constructor `0x001C0F40`, vtable `0x003052D8`, slot `+0x40 -> 0x001B5070`.
It accumulates contributions from backing providers through their slot `+0x38`.
One concrete implementation (`0x001C9D30`, table slot `0x003047D8`) mixes the
source name, not protected file bytes. The runtime backing-provider set and
original vendor field name remain unknown; matching keys do not prove matching
filenames or every file byte. See focused report sections 9-10.

## 14. App SKU routine: caller and implementation resolved

**[CONFIRMED]** The App-SKU routine logs `Loading licenses from device folder <%s>` and later `App SKU ID %d`.

**[CONFIRMED]** Caller function `0x0011A9B4-0x0011AF68` sets `r4` from its
incoming context pointer at `0x0011A9C0`. At `0x0011A9D4-0x0011A9DC`, it
loads its seventh argument as a byte and saves it at `[fp-0xA0]`. That argument
is a flag, not a device/SWID pointer. Call `0x0011ACD0` passes the context and
flag to App-SKU handling. Parent call `0x00123794` obtains the context from
parent `+0x154` and forwards its own third argument as this flag.

**[CONFIRMED]** App-SKU handling supplies query selector `0x284` at
`0x00110FB8` and calls manager **vtable slot `+0x58`** at `0x00110FC8`.
It stores the return at context `+0x24` (`0x00110FD8`) and logs it at
`0x00110FF4`. The constructor-installed manager table is `0x00312780`;
slot `+0x58` resolves to `0x002466BC`.

That implementation queries Application distributor slot `+0x2C`, resolved
through secondary table `0x0031284C` to thunk `0x0026414C`. The adapter
encodes `0x284 -> 0x42000284` and uses lookup `0x00263F50`. Module/feature
membership helper `0x0023A590` tests `0x0284` in a halfword vector. Matching
records are ranked by metadata `+8` (unsigned minimum SKU), preferring records
outside configured `online_skus` intervals, then falling back to those inside.
Wrapper getter `0x00262C30` returns this metadata word.

**[HIGH]** `0x284` is a module/feature selector. Its exact vendor module name
is still unknown. It is neither the App SKU itself nor proof of a MY14 selector.

## 15. Working model

The previous model incorrectly drew a direct SWID-input-to-App-SKU arrow.
The now-proved flows are separate:

```text
device.nng -> compact identity / appcid / validity information
                  (not proved to be the logged App SKU)

device-side application-license records
  +-> query 0x284 -> encoded module 0x42000284 -> ranked matching record
  |                                             -> metadata +8
  |                                             -> context +0x24 -> App SKU log
  +-> query 0 -> substituted 6/7 -> ranked matching record -> metadata +8
  |                                             -> application_skuid property
  `-> collection 0x5FF -> skip already-valid records -> metadata +0x10
                                                -> sorted container-ordinal set

media records -> already valid / activatable / invalid
  activatable + container ordinal present in set -> incompatible
  activatable + container ordinal absent from set -> GUI check or activatable
       -> result lists and enum 0/1/2 -> caller-specific handling
       -> activation/request-code handling separately, when required
```

**[CONFIRMED]** Discard implementation `0x0012445C`, reached through adapter
`0x00124D4C` and tail branch `0x00124D70`, uses the same container ordinal
to prune all related entries from result lists `+4/+8/+0xC/+0x10`. It also
collects source names through the container backpointer at record `+0x28`
using `0x00240C18`, retains them
at context `+0x44/+0x48/+0x4C`, and passes derived names to manager slot
`+0x28` at `0x001249F8`. It registers callback `0x00113160`, which compares
planned filenames against the discard-name vector (`0x0011321C`) and clears
matching plan entries' associated objects (`0x00113338-0x00113344`). The
callback first checks path and entry category; it is not an unconditional
filesystem deletion operation.

First scanner caller discards the invalid list at `0x001253B0` when result
policy byte `+0` is set; the second has the analogous call at `0x00126848`.
This establishes record-group-to-file-plan filtering without a MY14 switch.
The separate observed consumer of context App SKU `+0x24` at `0x00125A44`
passes it to the existing request-code routine after classification, not to
the container-key comparison.

The recovered runtime log proves the MY14 REVA file was copied successfully.
It does not identify the internal numeric SKU or individual record states.
The observed filename therefore anchors the outcome, not an inferred numeric
mapping from model year to license.

## 16. Open questions / next work

The caller, virtual implementation, SKU metadata offset, SWID-property output
direction, and scanner-key construction have been resolved. The next evidence
targets needed to tie this mechanism to the exact successful file are:

1. Correlate the now-resolved record-group pruning and filename-exclusion
   callback with the exact MY14 file's runtime record values. Static code
   establishes the mechanism, not that run's internal numeric mapping.
2. Locate an existing Synctool diagnostic log from the successful run that
   includes `App SKU ID`, per-file record classifications, and the final plan.
   The recovered outer SWDL log currently supplies only the filename/outcome.
3. Recover the original name of module selector `0x284` and the historical
   backing-provider configuration. Slot `+0x40` is now resolved to composite
   filesystem identity accumulation; the original class name remains unknown.
4. Keep protected license contents, activation secrets, and bypass construction
   outside this investigation. A numeric MY14/REVA mapping must come from
   legitimate non-secret inventory/diagnostic evidence, not a guessed label.

**[CONFIRMED]** A reusable read-only marker probe scanned all 16,034,824,192
bytes of the original image, not just recovered filenames. It found only nine
embedded format/prefix strings and no runtime-looking instances of the selected
App-SKU/device/classification markers. That closes the intact-plain-text
recovery route for these markers; compressed, fragmented, corrupted,
differently worded, or radio-only logs are not excluded. See the focused
report for offsets and reproduction commands.

## 17. Safety and handling notes

### Continued diagnostic evidence

The [focused report](synctool_device_license_selection.md#8-internal-logger-sink-implementation-and-configured-destinations)
now resolves the internal logger to a sink chain, with `vsnprintf` formatting
and concrete stdout/file implementations. The 2017Q2 installer configuration
names `/dev/stdout` and `/hbsystem/multicore/navi/3` at severity threshold 3.
Append-mode `fopen64` / `fwrite` / `fclose` is proved; a persistent Synctool
log file is not. Later RA4 18.45.01 boot evidence shows null-routing or
`multicored` capture to existing `LOGFILE.DAT` files. This is a specific
read-only capture lead, not proof of historical routing or permission to
enable logging. Result class remains **B - PARTIALLY PROVED**: the exact
MY14_REVA record/SKU association still needs contemporaneous non-secret evidence.

The later boot script's large diagnostic-file allowance is not suitable for
our future app. The [RA4 resource budget](../docs/ra4_resource_budget.md) protects
45 MB of the approximately 77 MB observed free space; evidence captures should
not be staged into that pool.

- Keep `uconnectmapimage.img` read-only.
- Do not run filesystem repair tools such as `chkdsk` against the original image.
- Do not commit recovered FCA/Harman/NNG binaries, ISOs, `.lyc` files, keys, or vendor content.
- Prefer hashes, offsets, control-flow facts, and independently reproducible metadata in repository documentation.
- Do not derive, disclose, brute-force, forge, or reuse activation codes, signing secrets, or license credentials.
