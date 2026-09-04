# RA4 18.45.01 QNX boot-filesystem recovery

## Scope and safety boundary

This report records a static, read-only recovery of the QNX filesystems embedded in the owner-supplied RA4 `ifs-cmc.bin`. No target executable or recovered script was run. The source image was not modified. Decoded vendor files remain below the ignored `analysis_ra4_18.45.01/` tree and must not be staged or committed.

Evidence labels:

- `CONFIRMED`: reproduced directly from the named bytes.
- `HIGH`: strongly supported by recovered strings or bytecode, but not dynamically observed on a head unit.
- `UNKNOWN`: not proved by the available image.

## Source identity

| Artifact | Size | SHA-256 |
| --- | ---: | --- |
| `analysis_ra4_18.45.01/work/primary_iso/usr/share/IFS/ifs-cmc.bin` | 42,122,670 | `ea6797be141763f35f3059ad858eefbf54f730af0155bebc7af411c47d80ba92` |

The file begins with a standard QNX startup image. Its startup header signature is at file offset `0x8`; the decoded header identifies 32-bit little-endian ARM (`machine=0x28`). The image also contains three byte-aligned `hbcifs\0\0` headers at `0x001A0000`, `0x00F20000`, and `0x019A0000`.

The structure was interpreted against the official QNX startup-header and `dumpifs` descriptions:

- <https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.building/topic/ipl/ipl_startup_header.html>
- <https://qnx.com/developers/docs/6.5.0SP1.update/com.qnx.doc.neutrino_utilities/d/dumpifs.html>

The hashes, boundaries, file counts, and control-flow conclusions below come from the local RA4 bytes rather than from those general references.

## Compression format and recovery method

Recovered `usr/bin/memifs2` from the standard boot filesystem is 81,242 bytes with SHA-256 `33602cab7880f89023b2ae844a35bd77b0219f9b8ea9235a76ee63d8b33c8088`. Its ARM code provides the missing format definition:

- dispatcher `0x105948` tests compression bit `0x80` at `0x105974`;
- the bit-set branch clears `0x80` at `0x105A10` and calls the framed decompressor at `0x105A18`;
- framed dispatcher `0x10572C` reads a big-endian two-byte block length at `0x1057D8`;
- compression type `8` reaches the LZO path at `0x105828`.

Each HBC header stores compression byte `0x88`: framed flag `0x80` plus LZO type `8`. Each payload is therefore a sequence of big-endian 16-bit compressed-block lengths and LZO blocks, followed by a zero-length terminator. Treating the whole payload as one LZO stream fails because it leaves this framing intact.

The original parser and regression tests are:

- `analysis_tools/qnx_ifs_inventory.py`
- `analysis_tools/tests/test_qnx_ifs_inventory.py`

The six tests cover big-endian framing, terminal-zero accounting, truncated blocks, HBC-header discovery, QNX directory/file/symlink records, the header-and-directory end field, and bounds rejection. They pass with Python 3.12 `unittest`.

## Decoded filesystem inventory

| Container | Compressed source boundary | Decoded size | Blocks | Records | Regular files | Decoded SHA-256 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Standard boot imagefs | payload `0x00019110`; 1,512,821 bytes through `0x0018A684` | 3,450,748 | 53 | 71 | 46 | `503d46f0ac412fcff594a9b37cc859d2e029e257a2d2367275c723a5f77d22ab` |
| HBC `0x001A0000` | `0x001A0040`-`0x00F0CCDA`; 14,077,083 bytes | 30,909,752 | 472 | 513 | 433 | `996c5a52cf7e72bb73d95e34e684196ca702061c6c5d9977415b014fbea57fbb` |
| HBC `0x00F20000` | `0x00F20040`-`0x0199F530`; 11,007,217 bytes | 23,083,796 | 353 | 261 | 219 | `57feaf9cfde58172f8a94049227ec895eb2f88607466297e31f8732f201b8512` |
| HBC `0x019A0000` | `0x019A0040`-`0x0282BDAD`; 15,252,846 bytes | 35,478,140 | 542 | 141 | 126 | `aae02c6ea6873e66cde49e814299d43cbeb38e686352fd86324ac91a1feafc42` |

The HBC compressed sizes include their two-byte zero terminators. Inventories and decoded files are under `analysis_ra4_18.45.01/work/hidden_hbc_ifs/`. That directory is research input, not a distributable project artifact.

Across the three HBC images, the parser recovered 778 regular files containing 89,007,481 bytes. The larger decoded-image total includes imagefs headers, directory records, alignment, and other non-file payload bytes.

## Boot and supervisor evidence

The standard boot filesystem recovers `bin/boot.sh`, 29,268 bytes, SHA-256 `c801d473b0b49e8242114635f4022cc67ccbe03093fec188de3b7188dd636ecf`.

Confirmed line-level behavior:

| Lines | Behavior |
| --- | --- |
| `362`-`365` | Embedded-cellular boot branch announces AppManager and creates `/fs/etfs/usr/var/appman/xletRMS` when absent. |
| `367` and `371` | The branch unconditionally assigns `disableDRMArg=-d` and passes it to `appManager -s -j -v ... -c=/etc/system/config/appManager.cfg`. |
| `456`-`459` | CAN boot branch performs the same AppManager/RMS setup. |
| `461` and `465` | The CAN branch also unconditionally assigns and passes `-d`. |
| `648`-`649` | Starts `authenticationService -k /etc/system/config/authenticationServiceKeyFile.json`. |
| `722` | Waits for `/dev/serv-mon/com.aicas.xlet.manager.AMS`. |
| `747` | Starts `/usr/bin/cmc/service/platform/platform_ams_restart.lua`. |
| `751` | Starts `/usr/bin/versionInfo -cfg=/etc/masterConfig.json`. |

There is no condition around either initial `disableDRMArg=-d` assignment. Native analysis resolves the apparent contradiction. `main` at VA `0x197CB0` passes the original arguments to `processOptions` at VA `0x195FFC`. That function constructs a local Poco `OptionSet` at `0x196028` and registers `silent/s`, `json/j`, `presub/p`, `watchdog/w`, `config/c`, `tp`, and `help/h`, but no `drm/d`. The `OptionProcessor` stores only that local set at `0x1D9FC8`; its single-dash path at `0x1DA96C` looks up the substring after `-` as a short option, and common lookup starts at the local-set pointer at `0x1DA1C8`. An inherited/global set, short-option clustering, and long-name-prefix behavior therefore cannot turn `-d` into the missing option. The process-level exception handler at `0x196E00` loads the diagnostic `Unknown option! Option %s is ignored!` at VA `0x21284C`.

A dormant handler branch at `0x19718C` compares the normalized name `drm` and calls setter `0x16D548`, but `drm` is also unregistered and no parser route reaches it. The configuration singleton constructs its DRM-checker subobject through `0x181318`; that constructor initializes enable byte `+5` to `1` at `0x181338`. Install preparation obtains the subobject and calls checker `0x1801D4` at `0x1957A4`; the checker reads the same enable byte at `0x1802C0`, bypassing grant lookup only if it is zero. The confirmed result for RA4 18.45.01 is that DRM checking defaults enabled and stock `-d` is ignored, not that validation is bypassed.

The HBC `0x001A0000` filesystem recovers compiled Lua 5.1 bytecode `usr/bin/cmc/service/platform/platform_ams_restart.lua`, 7,514 bytes, SHA-256 `264e5aaa6e2e09e8bb86a881f4919a66220d1cad2c7ce9443416e5d35f9f720f`.

Exact constant offsets establish:

- AMS service `com.aicas.xlet.manager.AMS` at `0x197`;
- JVM launch `/fs/mmc0/app/bin/jvm.sh` at `0x12DB`;
- AppManager process name at `0x1344`;
- restart-only marker `/fs/etfs/disableDRM` at `0x1361`;
- AppManager command without `-d` at `0x137A`;
- AppManager command with `-d` at `0x13E5`;
- AppManager service wait at `0x1453`.

The bytecode watches AMS D-Bus ownership and restarts the JVM/AppManager after loss or timeout. Its literal set contains no `AMS_DEVELOPMENT`. The JVM launcher, not this supervisor, samples `AMS_DEVELOPMENT` when a new AMS process is started.

This distinguishes two persistent switches:

| Marker | Reader | Confirmed effect |
| --- | --- | --- |
| `/fs/etfs/AMS_DEVELOPMENT` | `/fs/mmc0/app/bin/jvm.sh` | Selects development versus production `security.jar` for a newly launched AMS. |
| `/fs/etfs/disableDRM` | `platform_ams_restart.lua` | Selects restart command text with versus without AppManager argument `-d`; native analysis proves this binary does not register that option, ignores it, and leaves its DRM checker enabled. |

No recovered HBC file contains the literal `AMS_DEVELOPMENT`. A full `disableDRM` literal search across the extracted RA4 analysis tree finds only `platform_ams_restart.lua`.

## Recovered native services and configuration

| Artifact | Size | SHA-256 | Relevant evidence |
| --- | ---: | --- | --- |
| `hidden_hbc_ifs/segment_00f20000/files/etc/system/config/appManager.cfg` | 5,802 | `ab9ed180574d2c9f83c45217f05b132af24abd364ecf59c8447d1ba0cdb9c2d7` | lines 8-14 define preload, installed Xlet, RMS, active DRM, and restore-DRM locations |
| `hidden_hbc_ifs/segment_00f20000/files/bin/appManager` | 1,268,061 | `608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591` | native Xlet/DRM/lifecycle service and `xletsReturnToNew` receiver |
| `hidden_hbc_ifs/segment_00f20000/files/etc/system/config/authenticationServiceKeyFile.json` | 11,359 | `5968ff07dba7a0316a7fc76687cbef5147699d96538d14a10def0bfd5211ad11` | key-ring configuration; key values intentionally not reproduced |
| `hidden_hbc_ifs/segment_019a0000/files/usr/bin/authenticationService` | 273,340 | `9c7c057fbffceb2dc0b77690b6eb07dcd90721de6f89c5a05150fa18cea84699` | SvcIPC service `com.harman.service.authenticationService` |
| `hidden_hbc_ifs/segment_019a0000/files/usr/bin/versionInfo` | 122,275 | `d90bb45ba58f0a3f1e9ee03de85b7a28ee4a03ef7fccbb4b9423b8fee171b8f1` | version/service-property publisher started by `boot.sh` |

The authentication key file has a `keyRing` object with 100 entries named `keyID_1` through `keyID_100`; each stored value is 64 text characters. It also names a product-ID path. This report records only structure, lengths, and the whole-file hash so it does not disclose reusable key material.

## Service-certificate engineering authorization

The recovered HBC content also closes the engineering-menu source that was previously hidden.

`usr/bin/cmc/service/platform/platform_troubleshoot.lua` is compiled Lua 5.1 bytecode, 13,931 bytes, SHA-256 `8beab38ab164479a9fd815116dbfa02a48e3fa661724fa9c4273dc5884a1ba45`. Its constants identify:

- `/etc/security/service.cert` at `0x314`;
- verifier `/fs/mmc0/app/security/scv` at `0x334`;
- public key `/etc/keys/serv_cert_key.pem` at `0x354`;
- `eng_menu` at `0x383` and `EngineeringMenu` at `0x79D`;
- `IgnitionCycles` at `0x7C0` and `ExpireDate` at `0x7ED`;
- `HUSerialNumber` at `0xBAB`;
- HU serial storage `/fs/fram/serialnumber` at `0x1A81`;
- explicit success/failure messages for signature, serial, date, and ignition-cycle validation at `0x1AEB`-`0x1C09`;
- removable-media notification name `SERVICEKEY` at `0x28C3`;
- exported `get_service_flags` at `0x2F31`.

The verifier `primary_iso/usr/share/MMC_IFS_EXTENSION/security/scv` is 1,596,550 bytes, SHA-256 `08bb7992d95b27b98bcb222021015cda152eef9fafa573720845d28c837c7fe1`. Application messages at `0xFE11C`-`0xFE3B8` show a public-key digital-signature verification path. Its options at `0xFE850`-`0xFE9FC` include engineering-flag extraction (`-e`), public-key path (`-p`), certificate path (`-f`), and validation-only mode (`-d`).

The recovered `etc/keys/serv_cert_key.pem` is a 451-byte PEM public key, SHA-256 `07e7a63fd528cdd4b4d23bc6aaac03adda4ca9659d0b4a86ddd5d26b8608831e`. It is a 2048-bit RSA public key; the SubjectPublicKeyInfo DER is 294 bytes with SHA-256 `1011d092ddfe35116474837a45e1ad23601d8ec9d57e75d427c6621bcdf9b635`.

The confirmed authorization model is therefore:

```text
SERVICEKEY removable-media notification
  -> copy candidate service.cert
  -> RSA verification with serv_cert_key.pem
  -> require matching HUSerialNumber
  -> require unexpired date / ignition-cycle allowance
  -> expose EngineeringMenu as service_flags.eng_menu
  -> Peripheral.versionInfo.serviceMenu
  -> engineering gesture / menu reachability
```

This service-certificate chain is separate from the factory anti-theft PIN. It supplies the previously unknown authenticated event that enables the engineering-menu surface; it does not itself create `AMS_DEVELOPMENT`.

## Consequences for the development path

The recovered boot files produce four important corrections:

1. The engineering-menu reachability gate is a signed, serial-bound, expiring service certificate, not factory PIN success.
2. The engineering menu's Development Security item remains the only confirmed creator/deleter of `/fs/etfs/AMS_DEVELOPMENT`.
3. Changing that marker has no direct restart side effect. It is sampled only when `jvm.sh` next launches AMS; a normal reboot or separately initiated AMS restart is required for activation.
4. Native AppManager DRM state is a different control plane. The supplied `-d` argument is not registered by the recovered option set even though a dead-or-indirect `drm` handler exists later. Neither `/fs/etfs/disableDRM` nor `-d` is evidence that AppManager DRM checks, AMS signature checks, or Java policy checks are disabled.

The current evidence therefore rejects the earlier assumed single chain `factory PIN -> developer authorization`. The actual RA4 chains are parallel and must remain separate in any safe design.

## Reproducibility and repository safety

Fresh checks used exact source offsets, SHA-256 over source and decoded byte streams, directory-entry bounds validation, and per-file inventory hashes. No symbolic links from the vendor image were created on the host; symlink targets were recorded as metadata. Absolute and parent-traversal paths are rejected by the extraction procedure.

Before any future commit:

```text
Stock/vendor firmware staged: NO
```

Only the original parser, tests, and this report are eligible project artifacts. The decoded filesystems, inventories containing vendor filenames/hashes, source ZIP, ISOs, stock binaries, scripts, keys, and JARs must stay ignored and unstaged.
