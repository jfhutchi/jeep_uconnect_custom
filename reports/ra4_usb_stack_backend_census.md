# RA4 structured USB census and projection backend contract

Date: 2026-09-06. Canonical starting head `174d721c5f68763a107118ab714bd5f9e3670e1c`.
Host-only, read-only analysis of existing owner-supplied material. This report
does not authorize a radio connection or target execution.

## Findings that change the decision

- STATIC_PROVED: the materialized QNX host library exports vendor-control,
  descriptor/configuration, pipe and bulk APIs. Stock USB clients import them.
  These are the relevant primitives for an AOA host client; a DCD is not an AOA
  prerequisite on the RA4 side.
- STATIC_PROVED: the stock HMI addresses `phoneProjectionService` through its
  shared ModuleLink `span` client; `startProjection` carries `ppId`. A separate
  destination, `DeviceConnectionManager`, supplies projection-device status.
- STATIC_PROVED: the same HMI initializes CarPlay Cinemo start/stop error codes
  1000/1001 and GAL start-timeout 2501. INFERRED: Cinemo is a meaningful OEM
  provider lead, not merely an arbitrary vendor recommendation.
- UNKNOWN: Radio C2-to-controller routing. The available update/build logs and
  generic hub monitor do not supply the missing physical relationship.
- UNKNOWN: complete installed device-role capability. No named DCD/function
  bundle or projection backend was identified within the explicit boundary
  below. This is not proof of hardware impossibility or absence from every unit.

## Structured census boundary and method

The original [inventory tool](../analysis_tools/qnx_usb_inventory.py) reads
headers, ELF dynamic tables through program headers (with section fallback),
DT_NEEDED and defined/undefined dynamic symbols, plus ZIP/JAR member names. It
hashes candidate ELF files. It does not unpack any archive, execute a binary,
search every raw byte, decompress JAR payloads or resolve runtime services.

| Label | Prefix under `analysis_ra4_18.45.01/work/` | Files |
| --- | --- | ---: |
| root0 | `installer_iso/` | 54 |
| root1 / P | `primary_iso/` | 2,466 |
| root2 | `secondary_iso/` | 766 |
| root3 / B | `hidden_hbc_ifs/standard_boot/files/` | 46 |
| root4 / H1 | `hidden_hbc_ifs/segment_001a0000/files/` | 433 |
| root5 / H2 | `hidden_hbc_ifs/segment_00f20000/files/` | 219 |
| root6 | `hidden_hbc_ifs/segment_019a0000/files/` | 126 |

Result: **4,110 files; 578 ELFs; 321 ZIP/JAR containers; 91,086 member names;
44 ELF candidates; zero skipped links; zero parse failures**. Initial file
header reads totaled 78,637 bytes; that is not the total I/O, because metadata
tables and candidate hashes require additional reads. One ELF has no dynamic
symbol table. This pass is not the previous 1.5 GB raw 122-marker scan.

The first section-only implementation missed 390 ELF dynamic symbol tables.
Program-header parsing reduced that number to one. A synthetic ELF with its
section headers removed reproduced the loss before the fix and now validates
DT_NEEDED plus a defined USB symbol. Never report empty ELF sections as absence
of loadable code, dependencies or exports.

Exact negative follow-up over the resulting paths/member names/dependencies and
USB-related symbols found no `io-usb-dcd`, `libusbdci`, `usblauncher`, named
device/function `devu-*` other than the two known HCDs, `Device_Stack`, gadget,
projection or Cinemo artifact. The broad candidate regex also matches unrelated
`DCD` display symbols, ADC data, `AoAdd` and accessory-gauge images; these were
not classified as USB device-stack evidence. ZIP member names do not exclude
code with generic names or constants within compressed payloads. Static-linked,
renamed, optional/private, differently packaged or unmaterialized implementations
remain outside this negative. No live unit's installed inventory was read.

## Hash-identified host runtime

Paths use the prefix table above; hashes are SHA-256. All rows are ARM32
little-endian ELF. The image's `qnx650` environment and prior TC650 provenance
establish the OS generation; an ELF machine field alone cannot establish QNX
release, C++ ABI compatibility or permission to reuse a component.

| Artifact | Bytes | SHA-256 | Dynamic/startup evidence |
| --- | ---: | --- | --- |
| B `bin/io-usb` | 128629 | `3ac3777b8986c6aebd3c0d226715ee8fa935895c2ee5775bc874ceef569cd3f4` | DT_NEEDED `libc.so.3`; startup configures both host controllers |
| B `lib/dll/devu-omap3530-mg.so` | 45936 | `6916bd0f398f28bf111ace6c3a08e425a90127f283e0105e2bb6f0b58df881a1` | Host HCD, `libc.so.3`; Mentor `0x480ab000`, IRQ 92 |
| B `lib/dll/devu-ehci-omap3.so` | 40215 | `4e267106c1f209e9b32c596d2d04f39d3ee2d3337d0d5601f74f58a33114c03e` | Host HCD, `libc.so.3`; EHCI `0x48064800`, IRQ 77 |
| H1 `lib/dll/libusbdi.so.2` | 47302 | `08c1de09a0ea97da4481275dcdf8191efba7208544fee4f6757a57f48f1b3923` | 62 `usbd_*` exports, DT_NEEDED `libc.so.3` |
| H1 `bin/enum-usb` | 22594 | `b07b6a8ff791f46f6db5988df77cd3a509c8d22265ff54fe2c581212b605b460` | Imports `usbd_setup_vendor`, `usbd_io`, descriptors/config selection; needs `libusbdi.so.2` |
| H1 `bin/devb-umass` | 45394 | `98996317b2efb961f1ffb94fcc55cf75dd94c82f558f220a3f6f0af5a7db658b` | Imports bulk/vendor/pipe APIs; needs USB client library and `libcam.so.2` |
| H1 `bin/devc-serusb` | 125795 | `3bd75f39baace1141fcc7cc731e07c18a2f275888bae0b622763b8e0354c5e17` | Imports host USB client APIs; this serial client is not evidence of a USB gadget |
| H2 `bin/connmgr` | 262855 | `1d40e0762f50d89c29a866e8106bdf1c6d35546cff2e9f1c4956e366daf89a36` | Imports host attach/connect/descriptor/string APIs; no projection exports identified |
| H2 `lib/dll/iofs-usb-ipod.so` | 19937 | `087cb7e158248cc0345fed2f50a5c3223ced2faf1b413cb31c686dc7a84714ec` | Legacy host iPod client imports; not a CarPlay receiver or device function |

The library exports `usbd_setup_vendor`, `usbd_setup_bulk`, `usbd_io`,
`usbd_attach`, `usbd_open_pipe`, `usbd_parse_descriptors`, `usbd_select_config`,
`usbd_select_interface`, `usbd_abort_pipe`, `usbd_detach` and `usbd_topology_ext`.
Fresh symbol inspection identifies `usbd_setup_bulk` at ELF VA `0x903c`,
`usbd_setup_vendor` at `0x91d8` and `usbd_io` at `0x8d08`, each a defined
`STB_GLOBAL`, `STT_FUNC`, `STV_DEFAULT` symbol in that library.
QNX's matching 6.5 documentation describes
[vendor transfers](https://www.qnx.com/developers/docs/6.5.0SP1.update/com.qnx.doc.ddk_en_usb/usbd_setup_vendor.html)
and [bulk transfers](https://www.qnx.com/developers/docs/6.5.0SP1/ddk_en/usb/usbd_setup_bulk.html).
This corroborates the API interpretation, not a supported Android Auto driver.

Disposition: materialized/configured host runtime STATIC_PROVED; usable stock
host stack HIGH; actually loaded state and loadability of a new caller UNKNOWN.
No new component has been linked for or loaded on RA4. Stock import satisfaction
does not grant an arbitrary app permissions or exclusive access to a phone.

## Device/function-stack gate, correctly separated

For **Android Auto via AOA**, the RA4 stays host. Required additions are an
authorized host client/receiver transport adapter, phone-specific enumeration
handling, coordinated ownership with stock enum/media consumers, an authorized
projection engine and stock media/HMI integration. No hardware-role or VBUS
reversal follows from AOA. `enum-usb`'s existing vendor-transfer imports do not
prove it already negotiates AOA or that its rules may be modified.

For the **legacy wired CarPlay role-swap reference**, the candidate bundle is a
QNX-6.5/ARM32-compatible USB device stack, OMAP/Mentor DCD, function driver,
descriptors/endpoint configuration, role/power lifecycle, and authorized Apple
transport/receiver. QNX's [6.6 guide](https://www.qnx.com/developers/docs/6.6.0_anm11_wf10/com.qnx.doc.dev_pub.ref_guide/topic/usblauncher_config_supported_applications.html)
documents a host-to-device path and directs integrators to QNX support for the
automotive iOS drivers. Those are reference components, not installed RA4 proof.

Of the requested A/B/C/D interpretations:

- A, hardware impossible: **not established**.
- B, hardware-capable but missing software: plausible at the OMAP dual-role
  silicon level; **not established for the actual cabin path**.
- C, legitimately addable compatible software: **EXTERNAL_PROVIDER_GATE**;
  requires a provider to confirm this exact BSP/ABI and authorized packaging.
- D, insufficient evidence: **current board/runtime verdict**. Named standard
  device components are absent in this bounded materialization, but a universal
  installed-stack absence or board capability conclusion is not justified.

## Cabin topology: targeted results and exact missing observation

Retain the existing [external media-hub chain](../docs/19_ra4_media_hub_usb_path.md):
hub `68141322AA` / `68289895AA` -> UCI cable `68141323AA` -> Radio C2
`D2784B`, X457/X458 D+/D-. Its external connector attribution remains HIGH.
Neither the new census nor existing board photos closes the internal nets.

Targeted local logs reviewed, without printing private log content:

| Existing file | Bytes | SHA-256 | Result |
| --- | ---: | --- | --- |
| `recovered_root_helpers/swdlLog.txt` | 1043885 | `99fd5cc98ff165137be15295660435b0a96af2a328c3fe31b590e0eaf912cdf1` | No selected connector/controller/attach markers |
| `recovered_root_helpers/swdlLog_recovered.txt` | 1043885 | `bdb57fd2bb3c3d6ea085c90c167b77b9706d0cc19d279aec6eec0d6f475ec973` | Same bounded negative; not counted as an independent topology observation |
| `recovered_root_helpers/KaliSWDL.log` | 43979 | `52be34f0765306ee3db18ed354e596a8b8ae658a503d5880255718ffa9788e50` | EHCI entry at line 167 is an image-build inventory row, not a live attach record |
| `analysis_ra4_18.45.01/extracted/KaliSWDL.log` | 179972 | `31fd720faad6e677fbf7021f6e8e0e7dae9f813f39e0cde065130075c84dabe3` | EHCI line 492 is likewise a build row; other OMAP hits name an ETFS driver |

The exact log probe covered D2784B, the three media-hub/cable part numbers,
BE2800, media hub, root-hub/HCD, controller names/bases, USBFault and USB
attach/enumeration patterns. No evidence was extracted from personal fields.
This is not a search of arbitrary owner storage or a claim that no boot log exists.

`boot.sh:158` starts `usb_hub_oc`; `boot.sh:526-536` orders connection-manager
startup and enumeration. The primary `usb_hub_oc` is 19,595 bytes, SHA-256
`15a6d1a3b9de2a123236e11cb32931e2cdd491c0ca8d394ff4a874094b7b0bb6`.
Its imports include `usbd_topology_ext`, `usbd_hcd_ext_info`, `usbd_status` and
`usbd_feature`; its diagnostics identify hub device numbers and ports. Its
usage metadata says it monitors hub overcurrent and can restore port power.
It is **not a passive probe to run** and provides no named C2 mapping.

Recovered `enum-usb.conf` describes legacy Apple/class selection and device
quirks. `connmgr_P_1_2.json:9` sets `trackUnhandledUsbDevice` to zero and has
embedded-phone/serial rules. Therefore an absent generic connmgr notification
cannot establish absence of a physical USB device. Neither file links a hub
VID/PID to a specific HCD and C2. No new routing inference is made from a port
number, power request or a configuration string.

**Single decisive passive physical observation:** a documented, unpowered
net-trace on an owner-authorized spare BE2800 that follows both C2 X457/X458
through rear-I/O and board-to-board pins to an identified PHY's D+/D- pins,
and identifies which OMAP USB interface that PHY's bus reaches. Record the
board revision and intermediate pins in that one trace record. A PHY photo
alone, its proximity to C2, GPIO 38 or encoded EHCI selector 2 is insufficient.
No such observation was requested or performed on the vehicle in this run.
Hub transparency/power and actual AOA operation would still be separate gates.

## Expected stock projection receiver

Artifact: P `usr/share/MMC_IFS_EXTENSION/share/hmi_rov/MainSupplement.swf`,
SHA-256 `e9d796ea4b4c83ed518bfe3b3c341e54e510a1ae0f78ebbffbd655b7c36a3258`.
Offsets are reconstructed FWS addresses; method IDs belong to ABC 0 of this
hash. Existing SWF tooling parsed and decoded selected bodies without execution.

| Relationship | Method / FWS anchor | Meaning |
| --- | --- | --- |
| Static destination initialization | 7063 / `0x002B47F6` | `dbusIdentifier = phoneProjectionService` |
| Separate device destination | 7063 / `0x002B4809` | `DBUS_DESTINATION = DeviceConnectionManager` |
| Start API name | 7063 / `0x002B482F` | `startProjection` |
| Status/back-to-car signal names | 7063 / `0x002B4842`, `0x002B4855` | `projectionSessionStatus`, `projectionBackToCar` |
| Additional subscriptions | 7063 / `0x002B4868`, `0x002B487B`, `0x002B488E`, `0x002B48A1` | now-playing, navigation, call and device status |
| Provider/error vocabulary | 7063 / `0x002B4900`, `0x002B4912`, `0x002B4924` | Cinemo CarPlay start 1000 / stop 1001; GAL timeout 2501 |
| Shared transport client | 7064 / `0x002B4949`, `0x002B4958` | `Connection.share().span` |
| Incoming projection event binding | 7064 / `0x002B49A3`, `0x002B49AB` | `PHONE_PROJECTION` -> `phoneProjectionMessageHandler` |
| Device event binding | 7064 / `0x002B49B7`, `0x002B49BF` | `DCM` -> `DCMmessageHandler` |
| Start argument | 7086 / `0x002B5190`, `0x002B5195` | `ppId` passed to `sendCommand` |
| Command envelope destination | 7094 / `0x002B54C7`, send `0x002B54F1` | `Type=Command`, destination above, packet containing named command/argument |
| Availability observation | 7090 / `0x002B5299`, `0x002B52AA` | owner-notification subscriptions for the two destinations |

This answers **what was expected to receive startProjection**: the logical
`phoneProjectionService` destination, not the missing SWF, generic AppManager,
an identified Xlet or an invented PPS object. `DeviceConnectionManager` is a
separate device-status destination. The HMI checks the presence of service
owners; connection to a generic broker does not itself prove an owner exists.

`ModuleLink.xml` configures the span/hb endpoint at localhost port 4400 (hash
`46cacc8e084ba4b3024cdf68191da1b7165754cc2bedbc2bf44949a9ab59e533`). This is an
existing transport setting, **not permission or a standalone-client protocol**.
The variable names are DBus-oriented and the wrapper sends a JSON-like envelope.
The subsequent [native gateway trace](ra4_projection_gateway_dispatch.md)
identifies the SVCIPC bridge with HIGH confidence and proves that the recovered
gateway's normal routing rejects both projection destinations. The matching
D-Bus object/interface, executable/package owner and supported caller ABI remain
UNKNOWN; a compatible bridge/build is also required for this HMI route. No
connection was attempted, and no wire request or socket/PPS adapter is supplied.

The prior raw census supplied no exact native `phoneProjectionService` hit;
the new dynamic metadata and archive-member census likewise found no named
receiver. H2 `bin/appManager` (hash
`608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591`) has its
known libc/C++/JSON/PPS/SvcIPC/Colibry dependencies, without a projection-specific
dependency/export identified. That does not exclude a dynamically routed plugin.

| Missing-screen/backend explanation | What this run permits |
| --- | --- |
| Optional/variant/licensed package | INFERRED candidate; service-owner checks and build-family HMI code are consistent, but no exact package/install manifest identified |
| Dynamically resolved or external application bundle | UNKNOWN; missing filenames and dynamic symbols cannot exclude it |
| Backend contract retained without payload | STATIC_PROVED client-side contract exists; deployment reason UNKNOWN |
| Dead/unfinished OEM code | UNKNOWN; cannot distinguish from deliberately omitted variants with this corpus |

The `CMC_MY16_Trunk` debug source-family label is static provenance, not proof
of a working MY16 projection release. The correct next provider request names
`phoneProjectionService`, `DeviceConnectionManager`, matching HMI screen,
Cinemo error vocabulary, **QNX 6.5 ARM32** and exact RA4 release. See the updated
[engine qualification](../docs/11_projection_engine_feasibility.md).

## Host reproduction and limits

Use the existing ignored venv with `capstone`, `cryptography` and newly added
`pyelftools==0.33`. Only pyelftools is a new helper dependency; none belongs on
the radio. From the repository root, PowerShell:

```powershell
$py = 'analysis_work/post_reboot_20260906/venv/Scripts/python.exe'
$base = 'analysis_ra4_18.45.01/work'
$roots = @("$base/installer_iso", "$base/primary_iso", "$base/secondary_iso",
  "$base/hidden_hbc_ifs/standard_boot/files",
  "$base/hidden_hbc_ifs/segment_001a0000/files",
  "$base/hidden_hbc_ifs/segment_00f20000/files",
  "$base/hidden_hbc_ifs/segment_019a0000/files")
& $py -m analysis_tools.qnx_usb_inventory @roots > analysis_work/transport_gates_20260906/structured-inventory.json
& $py -m unittest analysis_tools.tests.test_qnx_usb_inventory -v
& $py -m analysis_tools.swf_abc_inspect "$base/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/MainSupplement.swf" --method 7063 --count 150
```

Inspect methods 7064, 7068, 7071, 7078, 7086, 7090, 7091 and 7094 with the same
hash-bound parser. Full derived output remains ignored. Tool output is metadata
but still needs review before publication. This report commits only original
analysis, names, hashes and short interface/offset references; no vehicle SWF,
ELF, JAR, credential, license or firmware payload.

## Verification executed for this checkpoint

- Five new synthetic inventory tests passed after observed preimplementation
  failures, including the stripped-section/PT_DYNAMIC regression. The complete
  existing Python suite then passed: 140 tests, no skips.
- `compileall -q analysis_tools` completed successfully.
- The final seven-root structured census completed with the counts above.
  All 44 candidate ELF hashes were then recomputed and matched; all SHA-256
  values published in this report were accounted for in fresh local reads.
- Twenty-four reported SWF instruction anchors were checked against their
  corresponding decoded method bodies. The interpretations also use the
  surrounding decoded instructions, not offset existence alone.
- Ninety-eight relative links in the changed Markdown files resolved locally.
  Whitespace and staged-content review are required before commit.
- No JavaScript/C99 implementation changed; those suites were not rerun. No
  target test, phone bench rerun, provider contact or install test occurred.
