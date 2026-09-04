# RA4 / UAS Corpus Inventory and Git Safety Audit

> **Post-snapshot supplement (2026-09-03 EDT):** The counts and Git-safety findings below remain the immutable 2026-09-03 inventory snapshot. Later read-only work decoded the RA4 `ifs-cmc.bin` standard imagefs and all three hidden HBC filesystems; that derived extraction and subsequent original analysis tools/tests are documented in Section 3A and are not retroactively included in the snapshot counts.

**Snapshot:** 2026-09-03 21:56 EDT (`2026-09-04T01:56:49Z`)  
**Repository:** `E:\Documents\GitHub\jeep_uconnect_custom`  
**Scope:** every regular file below the repository root except `.git/`; no archive was unpacked and no firmware input was modified.  
**Safety verdict:** **stock/vendor firmware staged: NO**. No stock/vendor file is tracked. At the audit snapshot, ignore coverage was unsafe because only the root Uconnect ZIP was ignored; the post-audit remediation recorded in section 6 now protects the known firmware trees and handoff paths.

## 1. Preflight and invariants

- A process check found no active `7z`, `unzip`, `tar`, or Git process. The only corpus process initially present was another agent's read-only `rg` search; it was stopped before the inventory pass. Codex/plugin hook shells and unrelated MCP services were left untouched.
- Initial PowerShell `Get-ChildItem` and `cmd dir /b` probes blocked while the concurrent search saturated `E:`. Both read-only probes were terminated without output or writes. The complete inventory then ran through `node:fs/promises` and completed normally.
- No firmware archive was opened for extraction. Existing manifests were preferred over rehashing all 6.6 GB. Fresh SHA-256 was limited to the root source ZIP, the locally produced installer ZIP, and small same-size UAS duplicate candidates.
- This report is the only file created by this audit. `.gitignore`, the Git index, staging area, tracked files, firmware inputs, and extracted trees were not changed.

## 2. Exact snapshot reconciliation

The inventory contains **3,398 files**, **6,648,650,761 bytes**, and **zero symlinks**. Every file is assigned to one of the following classes; there are no unclassified files.

| Classification | Files | Bytes | Git/publishing disposition |
|---|---:|---:|---|
| Stock FCA/Chrysler/Harman RA4/UAS firmware or direct firmware derivatives | 3,340 | 6,646,416,922 | Local input only; never commit or publish |
| Original research/docs already tracked | 9 | 27,867 | Tracked and clean |
| Original research/config/tooling currently untracked | 7 | 64,577 | Potentially publishable after review |
| Derived research evidence and inventories | 11 | 1,501,909 | Potentially publishable after content review |
| Generated Python bytecode | 1 | 16,451 | Generated; do not track |
| Third-party `node_modules` scratch dependency tree | 30 | 623,035 | Reproducible dependency material; do not track |
| **Total** | **3,398** | **6,648,650,761** | Exact reconciliation |

The 7 untracked original files are `.gitignore`, `RA4_RESEARCH_HANDOFF_CURRENT_FINDINGS.md`, `docs/superpowers/plans/2026-09-03-ra4-firmware-analysis.md`, and four Python files under `analysis_ra4_18.45.01/tools/`. The generated file is `analysis_ra4_18.45.01/tools/__pycache__/archive_stage.cpython-312.pyc`. The dependency tree is `analysis_ra4_18.45.01/work/security_agent/node_modules/`.

### Top-level inventory

| Path | Files | Bytes | Classification / role |
|---|---:|---:|---|
| `.gitignore` | 1 | 15 | Original repository configuration; currently untracked |
| `Uconnect_VP4,18.45.01-My13-17.zip` | 1 | 1,266,203,571 | Authoritative RA4 18.45.01 source package; stock/vendor; ignored |
| `analysis_ra4_18.45.01/` | 3,341 | 4,304,474,984 | Mixed local RA4 inputs, materialized trees, manifests, and local tools; untracked and not ignored |
| `analysis_uas_21.9/` | 44 | 1,077,907,214 | UAS comparison firmware tree; stock/vendor; untracked and not ignored |
| `docs/` | 9 | 34,078 | Eight tracked project docs plus one untracked research plan |
| `RA4_RESEARCH_HANDOFF_CURRENT_FINDINGS.md` | 1 | 27,389 | Original handoff/report; untracked |
| `README.md` | 1 | 3,510 | Original project documentation; tracked |

### RA4 analysis-tree breakdown

| Path | Files | Bytes | Contents |
|---|---:|---:|---|
| `analysis_ra4_18.45.01/extracted/` | 5 | 1,427,129,365 | Five verbatim members of the source ZIP, including `swdl.upd` |
| `analysis_ra4_18.45.01/work/swdl_iso/` | 3 | 1,425,772,832 | `installer.iso`, `primary.iso`, and `secondary.iso` copied from the update image |
| `analysis_ra4_18.45.01/work/installer_iso/` | 54 | 34,333,260 | Materialized installer filesystem |
| `analysis_ra4_18.45.01/work/primary_iso/` | 2,466 | 371,334,962 | Materialized primary filesystem: native/QNX, HMI, resources, OTA |
| `analysis_ra4_18.45.01/work/secondary_iso/` | 766 | 1,012,221,304 | Materialized Xlet/Kona/KIM/speech filesystem |
| `analysis_ra4_18.45.01/work/installer_iso.zip` | 1 | 31,514,414 | Noncanonical local repack of installer material; firmware-derived |
| `analysis_ra4_18.45.01/work/security_agent/node_modules/` | 30 | 623,035 | Third-party scratch dependencies, not firmware and not project source |
| `analysis_ra4_18.45.01/inventory/` | 6 | 1,499,840 | Existing authoritative inventories and SHA-256 manifest |
| `analysis_ra4_18.45.01/evidence/` | 5 | 2,069 | Source hash, metadata, validation, and tool provenance |
| `analysis_ra4_18.45.01/tools/` | 5 | 43,903 | Four original Python tools plus one generated `.pyc` |

`analysis_ra4_18.45.01/agent_notes/` and `analysis_ra4_18.45.01/notes/` exist but contain no files in this snapshot.

## 3. Canonical source and derived-layer map

Use the materialized `work/*_iso/` trees for file-level inspection and `analysis_ra4_18.45.01/inventory/extracted_hashes.csv` for identity checks. Do not repeatedly unpack the source ZIP, `swdl.upd`, the ISO images, or `installer_iso.zip`.

| Path | Bytes | SHA-256 | Status | Firmware component / relevance |
|---|---:|---|---|---|
| `Uconnect_VP4,18.45.01-My13-17.zip` | 1,266,203,571 | `5388d9310737dc52a65f2825131043362254b3592da2584302b81bc0447f9fdd` | **Authoritative RA4 source package**; fresh hash matches existing evidence | Owner-supplied RA4 18.45.01 package |
| `analysis_ra4_18.45.01/extracted/swdl.upd` | 1,426,147,328 | `c704eb723d6697fd98959888274dda18362c23ce6f66b505e01ce1983148c344` | Canonical extracted ZIP member, but derived from the source ZIP | ISO-9660 software-download/update image |
| `analysis_ra4_18.45.01/work/swdl_iso/installer.iso` | 34,830,624 | `893c1e9dbc16b42d3a0eba8f8470336ec84618d59980735a1e61a58499b830a5` | Canonical extracted installer image for analysis | Update installer/runtime and Lua/shell update scripts |
| `analysis_ra4_18.45.01/work/swdl_iso/primary.iso` | 375,191,552 | `8086b7b6a413c9fd2718d21bd7d027c79c0dc36a1e1d43ea1f7358fd33b890ff` | Canonical extracted primary image for analysis | QNX/native services, AMS, HMI SWFs, OTA and hardware payloads |
| `analysis_ra4_18.45.01/work/swdl_iso/secondary.iso` | 1,015,750,656 | `cd6df921c1da876cb5652f011bd3f1cc6a751a818b3455f478b4e1f7fc7edcb5` | Canonical extracted secondary image for analysis | Kona/AMS Java, KIM Xlets, JARs, speech/data |
| `analysis_ra4_18.45.01/work/installer_iso/` | 34,333,260 | See per-file manifest | Canonical materialized installer tree | Prefer this tree over re-opening installer containers |
| `analysis_ra4_18.45.01/work/primary_iso/` | 371,334,962 | See per-file manifest | Canonical materialized primary tree | Prefer this tree for AMS/HMI/native inspection |
| `analysis_ra4_18.45.01/work/secondary_iso/` | 1,012,221,304 | See per-file manifest | Canonical materialized secondary tree | Prefer this tree for Kona/KIM/JAR inspection |
| `analysis_ra4_18.45.01/work/installer_iso.zip` | 31,514,414 | `c9093568926835fa00396454ff97e98f0815a935e7543b71c3ab896fc889ec4d` | **Noncanonical firmware-derived repack**; fresh identifier only | Redundant for analysis while `work/installer_iso/` exists |
| `analysis_uas_21.9/extracted/` | 1,077,907,214 | No complete corpus hash manifest present | Canonical on-disk UAS comparison tree only; provenance incomplete | UAS comparison update, encrypted payloads, modem files, certificate/signatures |

The UAS source archive itself is not present, and no evidence file records a whole-source UAS hash. Therefore the UAS tree is usable for comparison but cannot currently be tied reproducibly to an owner-supplied source container. This is the principal corpus-provenance blocker.

### Existing reproducibility artifacts

| Artifact | Role |
|---|---|
| `analysis_ra4_18.45.01/evidence/archive_hashes.json` | Source ZIP size and multi-hash record; its SHA-256 was independently rechecked against the current root file |
| `analysis_ra4_18.45.01/evidence/zip_validation.txt` | Records 5 members, 0 path errors, 0 normalized-path duplicates, 0 integrity errors, and exact extraction count/size agreement |
| `analysis_ra4_18.45.01/inventory/zip_inventory.csv` | Central-directory metadata for the 5 source-ZIP members |
| `analysis_ra4_18.45.01/inventory/installer_iso_inventory.csv` | 64 filesystem records, including 54 regular files |
| `analysis_ra4_18.45.01/inventory/primary_iso_inventory.csv` | 2,623 filesystem records, including 2,466 regular files |
| `analysis_ra4_18.45.01/inventory/secondary_iso_inventory.csv` | 1,274 filesystem records, including 766 regular files |
| `analysis_ra4_18.45.01/inventory/extracted_hashes.csv` | 3,294 SHA-256 records spanning ZIP members, 3 ISO images, and all 3 materialized ISO trees |

`extracted_hashes.csv` is the detailed manifest rather than this report repeating thousands of rows. It also stores the first 64 bytes of every record; although small diagnostic excerpts are within the mission's allowed evidence model, that field merits a deliberate publishing review.

### 3A. Post-snapshot QNX boot-filesystem recovery

After the immutable snapshot above, a read-only recovery pass decoded the QNX boot filesystems embedded in the RA4 source chain. The source containers were not modified. These identities connect the owner-supplied package to the exact IFS analyzed:

| Source layer | Bytes | SHA-256 | Provenance role |
|---|---:|---|---|
| `Uconnect_VP4,18.45.01-My13-17.zip` | 1,266,203,571 | `5388d9310737dc52a65f2825131043362254b3592da2584302b81bc0447f9fdd` | Owner-supplied RA4 18.45.01 package |
| `analysis_ra4_18.45.01/work/swdl_iso/primary.iso` | 375,191,552 | `8086b7b6a413c9fd2718d21bd7d027c79c0dc36a1e1d43ea1f7358fd33b890ff` | Canonical primary image extracted from the update container |
| `analysis_ra4_18.45.01/work/primary_iso/usr/share/IFS/ifs-cmc.bin` | 42,122,670 | `ea6797be141763f35f3059ad858eefbf54f730af0155bebc7af411c47d80ba92` | Exact source IFS containing one standard boot imagefs and three HBC filesystems |

The source IFS has a standard QNX startup header at file offset `0x8` and byte-aligned `hbcifs\0\0` headers at `0x001A0000`, `0x00F20000`, and `0x019A0000`. The decoded boundaries and identities are:

| Container | Compressed source boundary | Decoded bytes | Blocks | Records | Regular files | Regular-file bytes | Decoded imagefs SHA-256 |
|---|---|---:|---:|---:|---:|---:|---|
| Standard boot imagefs | payload `0x00019110`; 1,512,821 bytes through `0x0018A684` | 3,450,748 | 53 | 71 | 46 | 2,949,863 | `503d46f0ac412fcff594a9b37cc859d2e029e257a2d2367275c723a5f77d22ab` |
| HBC header `0x001A0000` | `0x001A0040`-`0x00F0CCDA`; 14,077,083 bytes | 30,909,752 | 472 | 513 | 433 | 30,769,956 | `996c5a52cf7e72bb73d95e34e684196ca702061c6c5d9977415b014fbea57fbb` |
| HBC header `0x00F20000` | `0x00F20040`-`0x0199F530`; 11,007,217 bytes | 23,083,796 | 353 | 261 | 219 | 22,931,139 | `57feaf9cfde58172f8a94049227ec895eb2f88607466297e31f8732f201b8512` |
| HBC header `0x019A0000` | `0x019A0040`-`0x0282BDAD`; 15,252,846 bytes | 35,478,140 | 542 | 141 | 126 | 35,306,386 | `aae02c6ea6873e66cde49e814299d43cbeb38e686352fd86324ac91a1feafc42` |

The three HBC images contain **778 regular files totaling 89,007,481 payload bytes** (`433 + 219 + 126` files; `30,769,956 + 22,931,139 + 35,306,386` bytes). The standard boot imagefs contributes another 46 regular files and is deliberately reported separately. The displayed HBC source ranges are inclusive, and their compressed byte counts include the two-byte zero terminators; decoded image sizes also include filesystem headers, records, alignment, and non-file payload bytes.

Decoded inventories and files are local under `analysis_ra4_18.45.01/work/hidden_hbc_ifs/`, with `standard_boot/`, `segment_001a0000/`, `segment_00f20000/`, and `segment_019a0000/` subtrees. Each subtree has an `imagefs.sha256` and `inventory.tsv`. The entire extraction root is vendor-derived research input covered by the path-scoped `analysis_ra4_18.45.01/` ignore rule; it must never be staged, committed, or published.

The recovery and subsequent bounded analyses are reproducible with original project code outside the ignored firmware tree:

| Original artifact | Bytes | SHA-256 | Role |
|---|---:|---|---|
| `analysis_tools/qnx_ifs_inventory.py` | 6,920 | `6cdab8b7493f816b36b583dbee7a6805d3b525c71b234cf621f82dd7fd3aef40` | Parses the standard imagefs and QNX-framed HBC LZO streams, inventories records, and materializes decoded files |
| `analysis_tools/tests/test_qnx_ifs_inventory.py` | 4,399 | `f3732e9207104747f7038b81e1351c6b5be33bd9fc7277dc80024d52724fc373` | Six parser tests covering framing, headers, records, and extraction behavior |
| `analysis_tools/jamaica_rom_strings.py` | 13,329 | `3fdd53837de8eeeef434d1249a0055102ab6ac05a7bc3c29b6752077cb185530` | Strict bounded decoder for JamaicaVM pools and related metadata tables without executing the target |
| `analysis_tools/tests/test_jamaica_rom_strings.py` | 15,268 | `309420c6bfd8359f49fc7e44793295f7be8c824e80536c0d19bb059329b922a7` | Twenty-two pool/tag, prefix-bound, mapping-table, class-bound, and CLI numeric-bound tests |
| `analysis_tools/developer_token_crypto_probe.py` | 41,177 | `f63aff730bdd59b78e832aec385d79564acab5919119e9616f84b8e806766bd8` | Discovers/deduplicates public keys and performs redacted raw-RSA/v1.5/PSS token classification, including independent PSS message-hash/MGF1-hash enumeration, with metadata-only output |
| `analysis_tools/tests/test_developer_token_crypto_probe.py` | 18,219 | `505bc76bf89b0a8b34be3d45f14f2ca6b2d4cfc2329d91d773f278952387540f` | Nineteen crypto-probe tests covering safety, parsing, classification, independent PSS MGF1 digests, determinism, sanitized malformed-key errors, certificate-subject controls, and other error paths |

The HBC compression byte `0x88` combines the QNX framed flag `0x80` with LZO type 8. Static analysis of recovered `usr/bin/memifs2` established the two-byte big-endian frame-length dispatch used by the parser. A complete `unittest` discovery run passes all 47 tests: six imagefs, 22 Jamaica-metadata, and 19 token-probe tests. Two token-corpus runs produced byte-identical sanitized JSON of 32,257 bytes with SHA-256 `91eec01858afddb2313e423e585bca4fcad46ad57baa72b65e78e9122374c5bc`. Detailed format proof, offsets, inventory samples, and per-image hash checks are in `reports/qnx_boot_filesystems.md`; the redacted token result is in `reports/developer_token_analysis.md`.

High-value services and artifacts recovered from these images include:

| Recovered path below `analysis_ra4_18.45.01/work/hidden_hbc_ifs/` | Bytes | SHA-256 | High-level relevance |
|---|---:|---|---|
| `standard_boot/files/bin/boot.sh` | 29,268 | `c801d473b0b49e8242114635f4022cc67ccbe03093fec188de3b7188dd636ecf` | Starts AppManager and authentication services, waits for AMS, and starts the restart supervisor and version service |
| `standard_boot/files/usr/bin/memifs2` | 81,242 | `33602cab7880f89023b2ae844a35bd77b0219f9b8ea9235a76ee63d8b33c8088` | Native format and decompression evidence for the HBC recovery |
| `segment_001a0000/files/usr/bin/cmc/service/platform/platform_ams_restart.lua` | 7,514 | `264e5aaa6e2e09e8bb86a881f4919a66220d1cad2c7ce9443416e5d35f9f720f` | Supervises AMS/AppManager restarts and invokes `jvm.sh` |
| `segment_001a0000/files/usr/bin/cmc/service/platform/platform_troubleshoot.lua` | 13,931 | `8beab38ab164479a9fd815116dbfa02a48e3fa661724fa9c4273dc5884a1ba45` | Verifies the HU-serial-bound, expiring RSA service certificate before enabling `eng_menu` |
| `segment_001a0000/files/usr/bin/cmc/service/platform/vehicle/icsHardKeys.lua` | 31,153 | `86aba0d0c5fbfdeb9d5da36edd66c81e3e76cf16744740d9778612f41a7a1ea5` | Implements the five-second driver-temperature up/down engineering gesture |
| `segment_001a0000/files/bin/hmiGateway` | 153,124 | `8d7fe8789bb012a66fbebd1bd44eefa506c672a5d70c90fbf92b3a5a6f01ec82` | Bridges HMI anti-theft requests into the on/off service path |
| `segment_001a0000/files/usr/bin/onoff/main.lua` | 66,272 | `41c0f3f2709c49d4a4f9b150b8c08c735515a9c50bbfbc2e4c36664d6466e698` | Marshals factory-PIN requests and decodes IOC channel-2 state |
| `segment_00f20000/files/bin/appManager` | 1,268,061 | `608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591` | Native Xlet lifecycle/DRM implementation and embedded-app catalog gating |
| `segment_00f20000/files/etc/system/config/appManager.cfg` | 5,802 | `ab9ed180574d2c9f83c45217f05b132af24abd364ecf59c8447d1ba0cdb9c2d7` | AppManager preload, Xlet, RMS, and DRM path configuration |
| `segment_019a0000/files/usr/bin/authenticationService` | 273,340 | `9c7c057fbffceb2dc0b77690b6eb07dcd90721de6f89c5a05150fa18cea84699` | Recovered SvcIPC authentication service; no anti-theft role is proven |
| `segment_019a0000/files/usr/bin/versionInfo` | 122,275 | `d90bb45ba58f0a3f1e9ee03de85b7a28ee4a03ef7fccbb4b9423b8fee171b8f1` | Publishes platform/version information used during startup |

The recovered corpus is evidence, not an authorization shortcut. The engineering service-certificate gate, factory anti-theft PIN path, AMS development-state transition, and Kona application trust checks remain separate controls; see `reports/authorization_bridge_deep_dive.md`, `reports/anti_theft_auth_flow.md`, `reports/ams_development_flag.md`, and `reports/kona_application_authorization.md`.

## 4. Firmware-family inventory

The existing SHA-256 manifest partitions the RA4 stock corpus as follows:

| Manifest tree | Files | Bytes | Important families |
|---|---:|---:|---|
| `outer_zip_extraction` | 5 | 1,427,129,365 | 1 UPD/ISO image, 1 PE utility, log, batch file, MD5 record |
| `nested_iso_images` | 3 | 1,425,772,832 | installer, primary, secondary ISO images |
| `installer_iso` | 54 | 34,333,260 | 1 large binary, 5 `.so`, 33 Lua files, 11 shell scripts |
| `primary_iso` | 2,466 | 371,334,962 | 1,086 SWFs, 188 corpus-wide ARM ELF records (primarily here), native services, HMI/resources, OTA |
| `secondary_iso` | 766 | 1,012,221,304 | 300 JARs, 38 data files, 136 properties files, KIM/Xlet packages |
| **Total** | **3,294** | **4,270,791,723** | Complete existing per-file SHA-256 coverage for these layers |

Cross-corpus family counts:

- **Native/QNX:** the manifest detects 188 ARM 32-bit little-endian ELF files totaling 86,650,026 bytes. RA4 `work/primary_iso/usr/share/IFS/ifs-cmc.bin` (42,122,670 bytes) is now decoded as the standard boot imagefs plus all three HBC filesystems described in Section 3A; UAS `extracted/second.ifs` (128,496 bytes) remains a separate comparison artifact.
- **HMI:** 1,086 stock SWF files total 141,193,109 bytes, all in the RA4 primary tree.
- **Java/Xlets:** 300 JAR files total 667,796,171 bytes. The secondary tree contains 27 `KIM1`-`KIM27` families, 135 KIM/Xlet package instances, 24 distinct application IDs, 135 `xlet.properties` files, and 135 `key.jar` files.
- **Scripts/config:** RA4 stock contains 54 Lua files, 36 shell scripts, and 1 batch file. UAS adds 4 shell scripts. The RA4 secondary tree contains 136 `.properties` files.
- **Archives/images:** the repository has 3 `.iso`, 1 `.upd`, and 23 `.zip` paths. The ZIP count is the ignored root source, the derived `installer_iso.zip`, and 21 stock ZIP resources within the primary filesystem. JARs are ZIP containers but are counted separately by extension.
- **UAS comparison:** 44 files / 1,077,907,214 bytes, dominated by 12 encrypted `.tar.gz` payloads (984,449,744 bytes), two modem `.spk` images (92,550,064 bytes), one IFS, a signed XML manifest, one `.cer`, one `.pem`, and three 256-byte signature records.
- **Prior handoffs:** the only current path with `handoff` in its name is `RA4_RESEARCH_HANDOFF_CURRENT_FINDINGS.md`. That document mentions a previously examined `RA4_runtime_handoff(1).zip`, but no handoff ZIP is present in this repository snapshot.

## 5. Exact duplicate analysis

### RA4 manifest results

Grouping all 3,294 manifest records by SHA-256 yields:

- 2,136 unique hashes.
- 274 duplicate-content groups.
- 1,158 instances beyond one representative per hash.
- 687,355,024 bytes referenced by duplicate groups.
- 497,721,827 theoretical bytes beyond one representative per hash.

The theoretical figure is an identity metric, **not a deletion recommendation**. Many duplicates are intentional members of different KIM variants or brand/locale paths inside the authentic firmware. Do not mutate or deduplicate the stock tree.

| Family | Duplicate groups | Extra instances | Theoretical extra bytes |
|---|---:|---:|---:|
| JAR | 68 | 142 | 422,716,771 |
| SWF | 88 | 604 | 71,414,600 |
| PNG | 37 | 43 | 1,484,507 |
| BIN | 10 | 19 | 1,066,410 |
| All other types | 71 | 350 | 1,039,539 |
| **Total** | **274** | **1,158** | **497,721,827** |

There are 18 cross-tree hash groups (261 extra instances, 229,875 bytes). Most cross-tree volume is installer content duplicated under `primary_iso/usr/share/OTA/fota_installer/`; the large instance count is mainly the 6-byte `magic.txt` payload repeated across primary and secondary paths.

### Largest representative duplicate groups

The `canonical sample` below is only the path to cite during analysis (the first matching manifest record), not a file to retain while deleting peers.

| SHA-256 | Instances x bytes each | Theoretical extra bytes | Canonical sample |
|---|---:|---:|---|
| `8a421cfda32d05f29d92e263d62307623a1603ec4e2d3c9183ca69b2ff33d4f6` | 8 x 21,909,230 | 153,364,610 | `secondary_iso/usr/share/XLETS/kim_packages/KIM16/xlets/7DEC7834-535D-47B5-BD33-695477EDCD57/prog/jars/GSkills_MY15_LSeries_v02.01.01_FIT.jar` |
| `00b15a1d7268565c3644ba07e1fb1c3789f27b9b118029510652d03139d3ad0d` | 8 x 7,416,574 | 51,916,018 | `secondary_iso/usr/share/XLETS/kim_packages/KIM16/xlets/52c79381-6719-11e1-b86c-0800200c9a66/prog/jars/GSkills_Viper_v01.23.01_FIT.jar` |
| `278a8464c50c92e2a30d7a916202e6ca3faff532f3cca5b792d0ee2c1f5ae0da` | 6 x 5,751,454 | 28,757,270 | `secondary_iso/usr/share/XLETS/kim_packages/KIM16/xlets/6BFD02C0-40C3-11E2-A25F-0800200C9A66/prog/jars/GSkills_MY16_WK_v02.01.01_FIT.jar` |
| `21ed8049f6b51caee1561fd23ca28020c5cdf331d2e177f0ee2b268e337cd122` | 4 x 8,800,617 | 26,401,851 | `secondary_iso/usr/share/XLETS/kim_packages/KIM15/xlets/f1de6bac-9876-3250-8dc2-c729b755a600/prog/jars/OffRoadPages_1.7.1_0906.jar` |
| `d5bd28e5592c4405b475c5396dff878006b6adc55952857ab2c6d0c3ecf32d96` | 4 x 7,555,478 | 22,666,434 | `secondary_iso/usr/share/XLETS/kim_packages/KIM1/xlets/52c79381-6719-11e1-b86c-0800200c9a66/prog/jars/52c79381-6719-11e1-b86c-0800200c9a66.jar` |
| `18754a6c2a72d5a7f507123958082b20dec61f89e864123c63ce7d39ee262f0e` | 2 x 21,907,080 | 21,907,080 | `secondary_iso/usr/share/XLETS/kim_packages/KIM12/xlets/7DEC7834-535D-47B5-BD33-695477EDCD57/prog/jars/GSkills_MY15_LSeries_v02.00.16_FIT.jar` |
| `3c8e646d85d04e3596ac29bae8fcce0fb0e946b52628f66f606b76fbcf8f4569` | 2 x 21,899,303 | 21,899,303 | `secondary_iso/usr/share/XLETS/kim_packages/KIM1/xlets/7DEC7834-535D-47B5-BD33-695477EDCD57/prog/jars/7DEC7834-535D-47B5-BD33-695477EDCD57.jar` |
| `5028c4a7c98916311f9f52bd074fda9edcbca03c62910235d6e84cac65525582` | 3 x 8,737,570 | 17,475,140 | `secondary_iso/usr/share/XLETS/kim_packages/KIM16/xlets/f1de6bac-9876-3250-8dc2-c729b755a600/prog/jars/ORP_1.6.0_FIT.jar` |
| `25498864c6793eb26da2b28308bab4c75c2825dd22be9438f11c7077536eeb01` | 2 x 6,137,768 | 6,137,768 | `primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/skins/default/themeSwfs/fontSwfs/MHeiM.swf` |
| `619ea2eb14b5676602106126e7905f799d4c156d5d161877b0efa53aeea10c88` | 299 x 20,023 | 5,966,854 | `primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/skins/default/themeSwfs/Abarth/226_Abarth.swf` |

### Fresh UAS candidate hashes

The UAS tree has no full hash inventory. Hashing only groups that shared an exact size found five small duplicate pairs (22,791 extra bytes):

| SHA-256 | Bytes each | Exact pair under `analysis_uas_21.9/extracted/VP4R_Update/ar7/` |
|---|---:|---|
| `749bdea111aead6fdfcd7da1664d5f3c22b0b2c5584abab6b00d024d15b42b5e` | 58 | `2493/file/dropbear` = `file/dropbear` |
| `b54e0eebf4cc7b214b489c66f7a7f40e2729a7a7babb8e2538535facdba51e44` | 101 | `2493/chatScript/AT_GET_SKU.cfg` = `chatScript/AT_GET_SKU.cfg` |
| `fae98158577fb3eac2b04609e8bc5218e0439153160b8f4c30282b8250b2c471` | 303 | `2493/activatescript.sh` = `activatescript.sh` |
| `b5f0308aa16dca338713250821ec5ab98dd455a9f7c2129c5619afeb1354ab17` | 6,631 | `2493/file/dnsmasq.nodhcp.logout2.conf` = `file/dnsmasq.nodhcp.logout2.conf` |
| `72dbecb63cca3d50635abe14df88851a7cb3bfa3996d89ed7fe18154e8ad2e2f` | 15,698 | `2493/activatescript_org.sh` = `activatescript_org.sh` |

The three 256-byte UAS signature files have different SHA-256 values and are **not** duplicates. Equal size alone was never treated as identity.

## 6. Git and vendor-material safety audit

### Current Git state

- Branch: `main` at `1c1a8a4ad0863d4e9186a1492d2304320d24ee86`, tracking `origin/main`, ahead 0 / behind 0.
- Tracked: 9 files, all original project documentation (`README.md` plus eight `docs/*.md` files), 27,867 bytes total.
- Modified tracked files: 0 at the audit snapshot.
- Staged files: 0; `git diff --cached --name-status` is empty.
- Stock/vendor firmware tracked: **NO**.
- Stock/vendor firmware staged: **NO**.
- `.git/info/exclude` contains comments only. No `core.excludesFile` is configured.

Pre-report status was:

```text
?? .gitignore
?? RA4_RESEARCH_HANDOFF_CURRENT_FINDINGS.md
?? analysis_ra4_18.45.01/
?? analysis_uas_21.9/
?? docs/superpowers/
```

The newly created `reports/corpus_inventory.md` is expected to add an untracked `reports/` entry; it is original research, not vendor material.

### Ignore coverage at the audit snapshot

`.gitignore` is itself untracked and contains one rule:

```gitignore
Uconnect*.zip
```

`git check-ignore -v --no-index` confirms that this rule ignores `Uconnect_VP4,18.45.01-My13-17.zip`. Representative RA4/UAS `.upd`, `.iso`, `.jar`, `.swf`, encrypted UAS payload, and analysis-tree paths all return exit status 1 (not ignored).

Consequently, **3,339 stock/vendor files totaling 5,380,213,351 bytes are untracked and not ignored**. A broad `git add .` would attempt to stage them. Six of those unignored files exceed 100 MiB:

| Unignored stock path | Bytes |
|---|---:|
| `analysis_ra4_18.45.01/extracted/swdl.upd` | 1,426,147,328 |
| `analysis_ra4_18.45.01/work/swdl_iso/secondary.iso` | 1,015,750,656 |
| `analysis_uas_21.9/extracted/VP4R_Update/encrypted_natp.tar.gz` | 459,086,830 |
| `analysis_ra4_18.45.01/work/swdl_iso/primary.iso` | 375,191,552 |
| `analysis_uas_21.9/extracted/VP4R_Update/encrypted_app.tar.gz` | 214,920,780 |
| `analysis_uas_21.9/extracted/VP4R_Update/encrypted_hmi.tar.gz` | 145,202,461 |

### Recommended protections at the audit snapshot

Before any commit, make ignore coverage path-scoped and shared in Git. At minimum, review and add protections equivalent to:

```gitignore
/Uconnect_VP4,18.45.01-My13-17.zip
/analysis_ra4_18.45.01/
/analysis_uas_21.9/
**/__pycache__/
**/node_modules/
```

The whole-tree rules intentionally protect all firmware descendants, including extensions with unexpected names. They would also hide the four original Python files and metadata currently located under `analysis_ra4_18.45.01/`; independently authored tools intended for Git should first be reviewed and placed under a clean project directory such as `analysis_tools/`. Do not use Git LFS, `git add -f`, or generic `*.zip` rules as workarounds.

The mission also names absent handoff corpora and their ZIP equivalents as vendor-bearing risks. Add explicit path rules if any of those inputs return to the working tree. Do not delete local research inputs and do not remove anything from tracking automatically; no such index cleanup is required today because no stock file is tracked.

### Post-audit remediation

After this timestamped inventory completed, the root `.gitignore` was expanded without staging or committing anything. It now protects both known analysis trees, `.iso` and `.upd` images, the named RA4/UAS source ZIPs, all mission-listed handoff directories and archive equivalents, the historical `%SystemDrive%/` path, `__pycache__/`, and `node_modules/`. The rules deliberately do not ignore `reports/`, `docs/`, `analysis_tools/`, or `prototype/`, so independently authored project artifacts remain reviewable.

Representative `git check-ignore -v --no-index` probes passed for 30 protected firmware/generated paths. Allowed project paths under `reports/`, `docs/`, `analysis_tools/`, and `prototype/` remained unignored. A fresh Git check after the edit still showed an empty index and **stock/vendor firmware staged: NO**. The counts and status block above remain the immutable pre-remediation snapshot; this paragraph records the later safety-state transition.

## 7. Reproducible audit procedure

Git commands executed through `node:child_process.execFile` (argument arrays, no shell interpolation):

```text
git status --porcelain=v2 --branch
git status --short --ignored
git diff --cached --name-status
git ls-files -z
git check-ignore -v --no-index Uconnect_VP4,18.45.01-My13-17.zip
git check-ignore -v --no-index analysis_ra4_18.45.01/extracted/swdl.upd
git check-ignore -v --no-index analysis_ra4_18.45.01/work/swdl_iso/primary.iso
git check-ignore -v --no-index analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/lib/kona.jar
git check-ignore -v --no-index analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/skins/default/themeSwfs/fontSwfs/MHeiM.swf
git check-ignore -v --no-index analysis_uas_21.9/extracted/VP4R_Update/encrypted_app.tar.gz
git config --get core.excludesFile
```

The exact Node filesystem pattern used for the complete metadata pass was:

```js
const fs = await import("node:fs/promises");
const path = await import("node:path");
const root = "E:\\Documents\\GitHub\\jeep_uconnect_custom";
const bases = ["analysis_ra4_18.45.01", "analysis_uas_21.9", "docs"];
const files = [];

for (const base of bases) {
  const basePath = path.join(root, base);
  const entries = await fs.readdir(basePath, { recursive: true, withFileTypes: true });
  for (const entry of entries) {
    if (!entry.isDirectory()) {
      const fullPath = path.join(entry.parentPath, entry.name);
      const stat = await fs.lstat(fullPath);
      files.push({
        path: path.relative(root, fullPath).split(path.sep).join("/"),
        size: stat.size,
        type: entry.isFile() ? "file" : entry.isSymbolicLink() ? "symlink" : "other",
      });
    }
  }
}

for (const entry of await fs.readdir(root, { withFileTypes: true })) {
  if (entry.isFile() || entry.isSymbolicLink()) {
    const fullPath = path.join(root, entry.name);
    const stat = await fs.lstat(fullPath);
    files.push({ path: entry.name, size: stat.size, type: entry.isFile() ? "file" : "symlink" });
  }
}
```

SHA-256 was streamed without materializing additional copies:

```js
const { createHash } = await import("node:crypto");
const { createReadStream } = await import("node:fs");

const sha256 = await new Promise((resolve, reject) => {
  const hash = createHash("sha256");
  const stream = createReadStream(filePath);
  stream.on("data", chunk => hash.update(chunk));
  stream.on("error", reject);
  stream.on("end", () => resolve(hash.digest("hex")));
});
```

RA4 duplicate grouping used the existing `tree,relative_path,size,sha256,...` rows from `extracted_hashes.csv`. UAS fresh hashing was limited to same-size candidate groups; identity was accepted only when SHA-256 also matched.

## 8. Blockers and next safety gate

1. **UAS provenance:** no original UAS 21.9 source package, source hash, extraction log, or complete per-file hash manifest is present. Do not claim reproducibility or authenticity for that comparison tree until an owner-supplied source archive is recorded and inventoried.
2. **Ignore coverage:** path-scoped stock-tree, image, handoff, dependency, and generated-file rules are now present in the untracked `.gitignore`. Review and track that original configuration before relying on it in another clone; continue avoiding broad or forced staging commands.
3. **Publishing review:** `extracted_hashes.csv` is derived metadata but includes 64-byte samples; review that field before committing the manifest publicly.
4. **Commit gate:** immediately before any commit, rerun `git status --short`, `git diff --cached --stat`, and `git diff --cached --name-status`; inspect every staged path and explicitly reconfirm **stock/vendor firmware staged: NO**.
