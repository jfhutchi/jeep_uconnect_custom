# Read-only analysis tools

## Performance Pages export evidence

`tools/analyze_performance_pages_export.py` strictly validates two reviewed,
hash-bound static evidence inputs and emits canonical ASCII/LF JSON reports for
the Performance Pages variants, export reachability, filename/content control,
storage capability, stock consumers, handoffs, failure signatures, and remaining
gates. Java conclusions can reference exact class/method/descriptor/BCI bindings;
when `--corpus` is supplied, the tool rehashes every source, opens selected JAR
members without loading them, parses the classfile, and verifies every selected
instruction tuple. `--check` compares all report bytes without writing.

```powershell
python tools/analyze_performance_pages_export.py `
  --corpus 'PATH/TO/analysis_ra4_18.45.01/work'
python tools/analyze_performance_pages_export.py --check `
  --corpus 'PATH/TO/analysis_ra4_18.45.01/work'
python -m unittest analysis_tools.tests.test_performance_pages_export_analysis
```

The tool reads recovered files only. It does not contact a service or target,
load vendor classes, create a vehicle payload, or infer runtime reachability
from a static reference. Credential and endpoint values are intentionally absent
from these reports.

The companion consumer census re-parses all 19 KIM19 and four common-base JARs,
emitting allowlisted substring matches and categorized invocation metadata. It
rejects malformed classes and duplicate archive members, and rechecks sources
after extraction. The native supplement follows only the named EcoDrive
service with a fixed source hash and selected ARM windows. Both reject output
under the corpus and support byte-preserving `--check`:

```powershell
python -m analysis_tools.performance_pages_consumer_census --corpus $corpusWork
python -m analysis_tools.performance_pages_consumer_census --corpus $corpusWork --check
python -m analysis_tools.performance_pages_native_storage --corpus $corpusWork
python -m analysis_tools.performance_pages_native_storage --corpus $corpusWork --check
python -m unittest analysis_tools.tests.test_performance_pages_consumer_census analysis_tools.tests.test_performance_pages_native_storage
```

Repository attributes retain JSON as LF on Windows so fresh checkouts preserve
the exact report and reviewed-note bytes. Source hashes, class/instruction
bindings and scan counts substantiate static evidence; none establishes runtime
authorization or a producer-to-consumer handoff by itself. Results and complete
verification commands are in
[the media verification record](../reports/kim19_runtime_analysis/performance_pages_verification.md).

## Stock signed capability follow-up

`stock_capability_index.py` adds process/native loading sites, socket factory
calls, incoming references and type/field/method inventories for selected
classes, and a strict literal-only read of the shipped KIM selection map.
It does not evaluate Lua, resolve virtual dispatch, load Java classes, or write
into its input root. JAR/class hashes retain duplicate occurrence provenance.
Strings/resource payloads are not emitted. The map parser rejects executable
statements and retains last-assignment semantics. Python 3.12+ is required.

```powershell
python -m analysis_tools.stock_capability_index --root 'PATH/TO/XLETS' `
  --select '^(com/tweddle/test/|com/tweddle/core/(HUThread|AbstractHUXlet|http/injection/)|net/sf/microlog/server/socket/|com/harman/network/StrictSocketImpl|com/harman/ams/initializer/Initializer|com/harman/pps/PPSObjectSimulator|com/airbiquity/vp4hup/utils/UnitTestUtil|com/harman/os/Executor|com/harman/ams/initializer/os/Executor)' `
  --output reports/stock_signed_capability/bytecode_index.json
python -m unittest analysis_tools.tests.test_stock_capability_index
```

See [the capability report](../docs/stock_signed_capability_analysis.md) for
interpretation. Missing runtime providers and native/AOT code remain outside
the classpath census. A method named `class$` is recorded as a compiler-helper
category rather than treated as user-configurable loading. Input read/parse
errors fail the run; links and junctions are skipped and reported.

Run commands from the repository root. Firmware inputs stay in ignored local
paths; none of these tools needs a tracked vendor fixture. Do not execute a
vendor ELF, patch an image, or commit license/activation material.

## Resident package structural inspection

`resident_package_inspect.py` recognizes the factory installed-layout form and
the live single-JAR member-routing contract recovered from AMS. It parses Java
properties and JAR manifests, recomputes detached
cross-JAR member digests, checks `.SF` full-manifest digests, inventories JAR
signature blocks, and reports sanitized public PKCS#7 certificate metadata when
the existing `cryptography` dependency is available. It never writes the input,
reconstructs an incoming archive, performs private-key operations, changes
policy, or sends an install request.

```powershell
python -m analysis_tools.resident_package_inspect PATH_TO_APP_ID_DIRECTORY --pretty
python -m analysis_tools.resident_package_inspect CANDIDATE.jar --pretty
python -m analysis_tools.resident_package_inspect KIM_PACKAGES_ROOT --scan-installed-tree --pretty
python -m unittest analysis_tools.tests.test_resident_package_inspect -v
```

A successful directory result means only `factory-installed-layout-analogue`:
the descriptor, confined executable-JAR path, exact `HB_CMC` marker, fixed
sibling `key.jar`, detached digest coverage, paired signature aliases and
parseable public certificate metadata match the recovered post-install shape.
Certificate-parser absence fails closed rather than treating opaque signature
blocks as valid. It is
not proof that the signer is trusted or that DRM/policy grants are effective.
Single-JAR results now predict the exact AMS split: root `xlet.properties` goes
to both outputs, exact uppercase `.MF`/`.SF`/`.RSA`/`.DSA` suffixes go to
`key.jar`, and all other members go to the executable. `schema_contract=PROVED`
identifies the recovered parser contract; `candidate_conforms` and
`accepted_schema` separately report whether a particular input conforms. Every
candidate still reports `installable=false`: structure does not establish issuer authority. The
tree-census mode emits relative paths and canonical member-content fingerprints,
not reconstructed archive bytes.

The inspector validates conventional JAR signatures only as the recovered
production authentication profile. A developer-token-bearing JAR without that
signature shape reports `accepted_schema=AUTHENTICATION_PROFILE_UNKNOWN` and
`candidate_conforms=null`; it does not claim that the token is valid or that
signature metadata is mandatory on a developer-token-success path. A device
token alone remains nonconforming without the conventional signature profile
because the recovered device-token branch continues to certificate verification.

## Lua 5.1 and SWF/ABC inspection

`lua51_inspect.py` and `swf_abc_inspect.py` are original Python-standard-library
inspectors. They never execute input, connect to services or write extracted
payloads. The [driver-temperature report](../reports/ra4_driver_temperature_contract.md)
provides exact ignored artifact paths, hashes and bounded queries.

```text
python -m analysis_tools.lua51_inspect PATH --match 'FT_DRV_ATC_TEMP|US_METRIC'
python -m analysis_tools.lua51_inspect PATH --function 23 --start 200 --count 60
python -m analysis_tools.swf_abc_inspect PATH --match 'IHvac.*zoneTemp'
python -m analysis_tools.swf_abc_inspect PATH --method 2598 --start 0x276BE0 --count 160
python -m analysis_tools.swf_abc_inspect PATH --xref 'PROJECTION_BACKTO_CAR|DEVICE_PROJECTION' --count 200
python -m unittest analysis_tools.tests.test_lua51_inspect analysis_tools.tests.test_swf_abc_inspect
```

Lua supports exactly the LE Lua 5.1 header with 32-bit int/size_t/instructions and
float64 numbers; 16 MB CLI input cap. Output is physical instruction-word indexing,
not decompiled source: CLOSURE upvalue-binding words appear as MOVE/GETUPVAL, and
SETLIST extension words are not specially decoded. Debug locals are evidence,
not guaranteed semantic names. Unsupported Lua opcodes are labeled UNKNOWN.

SWF supports bounded FWS/CWS and DoABC tag 82, ABC version 46.16; 32 MB compressed
and declared-uncompressed cap. It keeps reconstructed FWS offsets and indexes
method traits/signatures and bodies. Disassembly supports documented common
AVM2 operand forms and fails closed on unknown opcodes; it does not guess their
length or verify VM stack/control-flow safety. `--start` is a FWS byte offset;
decoding still begins at the method start. Entire selected method is decoded
even if output is capped, so unsupported opcodes beyond the printed range fail.
Pool names omit namespace-set detail for ordinary multinames; runtime names are
explicitly labeled. `--xref` decodes every method body and reports bounded
instruction-line regex matches, so it finds consumers rather than only method
names; it fails closed if any scanned method contains an unsupported opcode.
The XREF cap limits stored matches, not validation: later instructions and
methods are still decoded. `truncated` is true only if another match exists.
`newcatch` consumes one u30 index. `pushshort` accepts a bounded encoded u32 and
displays its signed low 16 bits, including stock sign-extended operands; other
u30 operands stay strict. See [Adobe's opcode table](https://github.com/adobe/avmplus/blob/master/core/opcodes.tbl)
and [interpreter](https://github.com/adobe/avmplus/blob/master/core/Interpreter.cpp).
Neither tool is a general untrusted-input sandbox/VM verifier.

Fixtures in `fixtures/ra4_driver_temperature_cases.json` are original examples,
not captures or a deployable decoder. No payload or vendor asset is bundled.
These PC-only tools add zero resident dependencies or radio storage usage.

## JVM invocation inventory

`jvm_call_inventory.py` uses Python 3.11+ and host-only `jawa==2.2.0`
(`python -m pip install jawa==2.2.0`). It opens selected `.class` members in a
JAR in memory and reports actual invocation instructions with caller signatures,
bytecode indices, target owner/method/descriptors and class hashes. It emits no
resource bodies, string constants or complete bytecode. Member, owner and method
selectors are regular expressions. A constant-pool reference alone is not a hit.

```powershell
python -m analysis_tools.jvm_call_inventory PATH.jar --member 'Xlet.class$' --owner 'javax/microedition/xlet|com/sun/lwuit/Display'
python -m unittest analysis_tools.tests.test_jvm_call_inventory -v
```

Selected classes are fully decoded before output, with 8 MiB per-class and
256 MiB total uncompressed-class limits. Read/parse errors propagate instead of
returning a successful partial inventory. `invokedynamic` sites are explicitly
counted as unresolved; reflection, JNI, virtual target selection, reachability
and the Jamaica ROM/AOT format are not resolved. This is not a JVM verifier or
an arbitrary-input sandbox. No target class is loaded or executed. See the
[resident view trace](../reports/ra4_resident_xlet_view_path.md).

## Jamaica AOT registration inventory

`jamaica_aot_registry.py` reads a caller-specified table using the existing
ELF32/ARM dependency. It supports the observed 24-byte class and 32-byte member
layout, with kind 1 method records and kind 2 field records. Fields and methods
may share an ordinal. It validates the entire selected range before filtering
output and preserves null adapter/function entries. Java names, live BSS
contents and execution are not inferred.

```powershell
python -m analysis_tools.jamaica_aot_registry PATH_TO_AMS --registry-va 0xc21424 --class-count 1138 --class-slot 439 --class-slot 401
python -m unittest analysis_tools.tests.test_jamaica_aot_registry -v
```

The example addresses/count belong only to the hash-bound image in the
[compiled timeout report](../reports/ra4_ams_aot_timeout_runner.md). Do not
reuse them for a different release without identifying its table. All pointers
use PT_LOAD translation: code/ROM and writable data can have different VA/file
offset differences. BSS pointers are reported but never read as file data.
Reserved-word, kind, bounds, executable-target and pairing failures stop the
reader; an absent requested class is an error rather than a successful empty
result. Default total member limit is 100,000. Output is original metadata,
not target payloads. No firmware fixtures are included in the tests.

## ELF32 / ARM inspection

`arm_elf_analysis.py` uses Python 3.10+ and Capstone (`python -m pip install capstone`
in your chosen development environment). It parses ELF32 little-endian
load segments itself; pyelftools is not required.

```powershell
python -m analysis_tools.arm_elf_analysis metadata analysis_work/Synctool.elf
python -m analysis_tools.arm_elf_analysis imports analysis_work/Synctool.elf
python -m analysis_tools.arm_elf_analysis disasm analysis_work/Synctool.elf --start 0x11A9B4 --end 0x11A9DC --literals
python -m analysis_tools.arm_elf_analysis callers analysis_work/Synctool.elf --target 0x110E6C
python -m analysis_tools.arm_elf_analysis words analysis_work/Synctool.elf --start 0x3127D8 --count 1
python -m analysis_tools.arm_elf_analysis strings analysis_work/Synctool.elf --pattern 'application_skuid|license_model' --xrefs
python -m analysis_tools.arm_elf_analysis references analysis_work/Synctool.elf --value 0x2466BC
python -m analysis_tools.arm_elf_analysis memory analysis_work/Synctool.elf --offset 0x51 --kind str
```

All disassembly ends are exclusive. `disasm --thumb` explicitly chooses Thumb;
there is no automatic instruction-set detection. Disassembly returns exit 2 if
it stops before the requested end, for example on a literal pool. Revisit the
range instead of treating a truncated listing as a complete function.

`imports` resolves classic ARM ADD/ADD/LDR PLT candidates using ELF32 REL
`R_ARM_JUMP_SLOT` symbols. It prefers `PT_DYNAMIC` metadata and uses section-linked
tables when no dynamic segment exists. This handles stripped QNX binaries whose
remaining sections contain no relocation/symbol information. Malformed dynamic
metadata raises an error instead of silently falling back. Dynamic symbol reads
are bounded by file-backed load segments; this is not a full linker or hash-table
symbol-count verifier. It uses raw ARM-word filtering, not full Capstone decoding
or assumed PLT order. Thumb, RELA and other linker stub forms are unsupported.
An empty result is not proof that another binary has no imports. Synthetic tests
cover both metadata paths, bounds, rotated immediates, stub shape and invalid
entries. The [projection gateway report](../reports/ra4_projection_gateway_dispatch.md)
cross-checks 181 real import slots independently. Fixed-address Synctool
conclusions must also pass the SHA-gated evidence verifier.

Whole-segment caller, prologue, immediate, field-access and PC-literal scans
are **candidates**: executable load segments can contain headers and data.
Verify surrounding code and actual installed vtables. `callers` includes
direct BL/BLX candidates, including conditional ARM calls and Thumb candidates
after embedded data; it excludes tail branches and indirect calls. `function`
finds nearby ARM prologues, which need not coincide with actual entries or ends.
`virtual-loads --selector` is only a candidate LDR displacement search, not a
resolved virtual call or a module-selector search. Use `immediate --value` for
immediate constants; synthesized constants can still be missed.

## Synctool evidence anchors

```powershell
python -m analysis_tools.synctool_evidence analysis_work/Synctool.elf --verbose
```

The verifier refuses an unknown SHA-256, then checks selected table entries,
instructions and schema strings used in the
[device/license report](../reports/synctool_device_license_selection.md).
It detects binary/version drift and transcription mistakes. Passing checks
are not a substitute for manually following the surrounding control/data flow.
Only derived, non-secret addresses and assertions are stored in the script;
it contains no license payload, activation data or decompiled vendor source.

## Find existing diagnostic evidence

```powershell
python -m analysis_tools.synctool_log_probe uconnectmapimage.img --max-hits 30
python -m analysis_tools.synctool_log_probe recovered_root_helpers/swdlLog_recovered.txt
```

This standard-library-only streaming probe distinguishes embedded format
strings from runtime-looking marker occurrences. It reports byte offsets,
categories and, when present, a signed decimal App SKU. For complete printable
record/file values inside the known angle-bracket fields it emits only a
full SHA-256 correlation token. Matching tokens let separate
classification and exclusion events be correlated without printing the value; a
token is not proof that unlike record and filename namespaces have the same
meaning. A field whose digest matches the already documented MY14_REVA
filename is additionally labeled `target=my14_reva`; no other value is
printed. Constant-memory per-marker target totals are emitted after the scan,
so `--max-hits` cannot hide whether the target appeared. It never prints record
names or surrounding arbitrary log contents. The display cap does not stop the
full scan or counting. No matches cannot exclude compressed, fragmented, damaged or
differently spelled messages. Even a runtime-looking hit is a candidate, not
authenticated execution evidence.

The probe also recognizes distinct NNG device-ID/SWID, device-code,
content-code, platform-ID, `Using IDs`, and Application-record-count messages.
Identity values are never printed: complete line or angle-bracket values become
SHA-256 equality tokens, while the non-secret record count remains numeric.
This permits cross-message identity correlation without disclosing a unit ID.

## Tests

```powershell
python -m unittest analysis_tools.tests.test_arm_elf_analysis analysis_tools.tests.test_synctool_evidence analysis_tools.tests.test_synctool_log_probe -v
python -m unittest analysis_tools.tests.test_elf32_imports -v
python -m unittest discover -s analysis_tools/tests -v
```

The new tests use synthetic in-memory ELF/log data only. The broader existing
suite also requires `cryptography` for its separate developer-token probe
tests; that dependency is not needed for the Synctool tools. Existing
`jamaica_rom_strings.py` and `qnx_ifs_inventory.py` have their own CLI help
and tests and are unchanged by this investigation.


## qnx_media_runtime_probe.py

Performs a read-only, constant-memory marker census across recovered QNX
filesystem trees. In addition to media/graphics candidates, it distinguishes
QNX CAR 2.1 reference integration names (PPS Navigator, Launcher/Authman, HNM,
Audio Manager, Now Playing, voice-path, Screen group/focus/touch, and multimedia
services) from Harman-specific ModuleLink/servicebroker/projection names and the
proved RA4 AMS/AppManager/Xlet lifecycle. Exact screen and return anchors include
`DeviceProjection.swf`, `PROJECTION_BACKTO_CAR`, and `PhoneProjectionEvent`.
The RA4 foreground-policy family adds the recovered session/start, projection-call,
foreground-request, native call/SMS/TTS, previous-call-screen, camera-layer and
HVAC-popup strings. This makes a stock HMI artifact containing both projection
and presentation-control evidence a first-tier manual inspection target.
The Apple transport family adds QNX 6.6 `usblauncher`, host/device-stack role
swap, iAP2/iPod driver, device-controller/function-driver (`devu-dcd`, QNX 6.x profile names such as
`devu-usbumass-*`, `libusbdci`, `Device_Stack`, the USB-control PPS path,
`start_stack::device`, and `ulink_ctrl`), plus RA4-adjacent `itun`/`libipod`
anchors. These prove
only a candidate transport layer, never the licensed CarPlay receiver. It emits only
controlled marker names, relative paths, file sizes, SHA-256 hashes, counts and
bounded offsets; it does not emit file contents or execute a target artifact.

```text
python -m analysis_tools.qnx_media_runtime_probe RECOVERED_ROOT [RECOVERED_ROOT ...] --pretty
```

The census searches raw bytes and filenames; it does not decompress CWS/SWF,
JAR or image payloads. It misses known projection names inside compressed
`MainSupplement.swf`. Inspect hash-identified HMI artifacts with the SWF tool
even if the raw census reports no hit. Generic `sessionActive`/`servicebroker`
co-occurrence is not projection identity. The
[post-reboot checkpoint](../reports/ra4_post_reboot_checkpoint.md) records the
seven-root 122-marker census and separate 610-SWF return-name census.

The default per-file scan ceiling is 128 MiB and every skipped file is explicit
in the JSON report. Raise the ceiling only for a known recovered artifact. A
marker hit proves only that controlled bytes occur in that file; it does not
prove a running service, supported ABI, authorized caller contract, or that a
standard QNX CAR reference component is present in the customized RA4 product.
Review metadata before committing it, and never commit recovered codecs,
libraries, DSP images or firmware.

## qnx_runtime_correlation.py

Consumes only the redacted JSON produced by `qnx_media_runtime_probe.py`,
validates its complete marker inventory and controlled-marker boundary, assigns
unique labels when input roots share a basename, groups matching files by
integration family, and emits a deterministic candidate order. It never opens a
recovered vendor artifact, preserves no marker offsets or arbitrary source
fields, and rejects unknown markers, stale marker inventories, duplicate roots/paths,
unsafe paths, invalid hashes and malformed counts.

```text
python -m analysis_tools.qnx_media_runtime_probe RECOVERED_ROOT [RECOVERED_ROOT ...] --pretty > qnx-runtime-report.json
python -m analysis_tools.qnx_runtime_correlation qnx-runtime-report.json --pretty
```

Priority tier 1 means a stock-specific/startup marker or configuration/startup
filename; tier 2 means markers from two or more integration families; tier 3 is
single-family evidence. Inspect tier 1 before lower tiers, then correlate a
candidate's hash and relative path with imports, XREFs and startup configuration.
A tier is an inspection priority only. It does not prove that a component runs,
exports a supported ABI, grants an authorized caller contract, or is safe to
invoke. Keep the intermediate and output reports outside Git unless their
controlled metadata has been reviewed.

## qnx_usb_inventory.py

Structured, host-only follow-up to the raw census. Requires Python 3.12+ and
`pyelftools` (validated with 0.33 in the ignored analysis venv). Reads regular
file headers, ELF program/section dynamic tables, dependency and symbol
metadata, and ZIP/JAR central-directory member names. It hashes selected ELF
candidates without executing them or extracting archive payloads.

```text
python -m analysis_tools.qnx_usb_inventory RECOVERED_ROOT [RECOVERED_ROOT ...] > analysis_work/usb-inventory.json
python -m unittest analysis_tools.tests.test_qnx_usb_inventory -v
```

Supply distinct, non-overlapping materialized roots. Input root labels preserve
argument order. Missing roots, read errors and malformed metadata fail loudly;
symlinks/junctions are not followed and skipped links are counted. Output records
the boundary and files lacking dynamic symbols. Program-header parsing matters:
recovered QNX images can retain loadable dynamic tables while lacking their
ordinary ELF sections. Absence from a symbol/name census is not absence from
all statically linked, compressed, renamed or optional runtime code.

The broad USB/DCD/accessory candidate vocabulary can match unrelated names.
Review it; never promote names, dependency edges or docs within an archive to
runtime support. Output contains relative filenames/member names and selected
symbols, which may still be sensitive; keep it ignored and review before any
publication. [Executed RA4 census and limits](../reports/ra4_usb_stack_backend_census.md).

## Stock extension-surface evidence ladder

These standard-library analyzers census recovered resident Java structure and
candidate-led native endpoint metadata without loading a class, extracting an
archive, or executing a recovered artifact. Outputs contain hashes, relative
metadata paths, parsed names, structural edges, bounded offsets, and explicit
`PROVED`, `STRONGLY INFERRED`, or `UNKNOWN` judgments. They must not contain
class/resource payloads or absolute corpus paths.

Run the focused socket analysis before the broad census:

```powershell
$CorpusRoot = 'E:/explicit/read-only/recovered-root'
python -m analysis_tools.resident_surface_census `
  --root "resident=$CorpusRoot/work/secondary_iso/usr/share/XLETS" `
  --focus-class 'com/tweddle/test/input/SocketCommandSource' `
  --output-dir reports/stock_extension_surface
```

After reviewing the focused activation, listener, protocol, and gate evidence,
run the complete resident surface census:

```powershell
python -m analysis_tools.resident_surface_census `
  --root "resident=$CorpusRoot/work/secondary_iso/usr/share/XLETS" `
  --focus-class 'com/tweddle/test/input/SocketCommandSource' `
  --broad `
  --output-dir reports/stock_extension_surface
```

The broad census reports static observations for dynamic loading, reflection,
configured class names, factories/providers, resources/packages, scripting,
URLs/protocols, browser-like APIs, structured data, network services, IPC,
media/import, files/resources, and plugin/registry mechanisms. A count or API
edge never establishes external origin, activation, execution, capability, or
reachability.

Use native correlation only with candidate names selected by the Java or
existing repository evidence:

```powershell
python -m analysis_tools.native_endpoint_census `
  --root "hbc=$CorpusRoot/work/hidden_hbc_ifs" `
  --candidate '127.0.0.1' `
  --candidate '11111' `
  --candidate 'TGTCore-CommandLooperThread' `
  --candidate 'SocketCommandSource' `
  --output reports/stock_extension_surface/native_socket_correlation.json
```

The native tool skips archive-like files, follows no links, enforces file/count
limits, and never treats a raw API word as an import or call. Structured ELF
imports/exports require optional `pyelftools`; without it, the output records
that dependency limitation and retains only bounded string presence.

Render the required reports only from a validated, metadata-only ledger:

```powershell
python -m analysis_tools.render_stock_extension_reports `
  --ledger reports/stock_extension_surface/evidence_ledger.json `
  --docs-dir docs
```

Run the deterministic synthetic tests:

```powershell
python -m unittest `
  analysis_tools.tests.test_evidence_model `
  analysis_tools.tests.test_java_classfile `
  analysis_tools.tests.test_activation_graph `
  analysis_tools.tests.test_resident_surface_census `
  analysis_tools.tests.test_native_endpoint_census `
  analysis_tools.tests.test_render_stock_extension_reports -v
```

For deterministic regeneration, run a command twice and compare SHA-256 maps
for all relative output paths. Review every generated JSON/Markdown file before
committing it. Never commit recovered JARs, classes, resources, filesystem
payloads, native binaries, credentials, or other proprietary content.

### Target production inventory

`target_production_index` inventories every physical file and every JAR member
in one selected KIM, hashes payloads without extracting them, parses application
descriptors and lifecycle classes, and records categorized JVM call sites with
both caller/callee descriptors. Resource-name literals and API categories are
candidates, not proof of consumption, live registration, or external control.

```powershell
python -m analysis_tools.target_production_index `
  --root "$CorpusRoot/work/secondary_iso/usr/share/XLETS/kim_packages/KIM19" `
  --output reports/target_production_state/package_inventory.json
python -m unittest analysis_tools.tests.test_target_production_index -v
```

Its importable `resolve_part(map_path, raw_part)` validates the literal-only Lua
map using the existing parser and applies an independently written ASCII model
of `xlets.lua` read(10)/suffix handling. It does not execute Lua. `None` models a
nil read, while `normalize_part(..., open_succeeded=False)` models an open
failure. Nonmatching input passes through as in the recovered bytecode.

Inventory errors, duplicate members, links, size limits, missing declared JARs
and missing main classes fail explicitly. The manually reviewed target-state
and candidate ledgers are separate from generated static inventory; see
`docs/target_production_state.md` for reachability and current-radio limits.

### KIM19 runtime observation model

`kim19_runtime_analysis` reuses `build_inventory` and requires an identical
baseline before generating eight focused JSON reports. It verifies KIM19 files,
the common-base manifest and prior evidence sources before and after extraction.
It scans all 19 JARs, but emits only selected lifecycle/decision methods plus
transport construction/caller sites, avoiding a second full corpus dump.

`kim19_runtime_notes.json` is the reviewed interpretation and selection ledger.
Its claims are **not** automatically inferred from call counts. Source hashes,
BCIs, caller/callee descriptors, branches, handlers and allowlisted constants
bind those interpretations to recovered evidence. Unapproved literals and
credential values are omitted. Native evidence is manually decoded, source-hash
bound. Sixteen native instruction windows now reproduce condition-flag,
super-app-flag and VSB setup provenance. A bounded vtable follow-up resolves the
catalog selectors as headless, daemon, and daemon `hasGUI` fields; it is kept in
a separate model so the original eight reports remain byte-identical. The
application/service graph validates 23 reviewed relationships
against exact JAR/class/method/descriptor/BCI/callee tuples. These are conditional
relationships, not computed live reachability. Tests reject wrong overloads,
callers, callees, offsets, duplicate graph identities and missing evidence.
Selected properties and the packaged Affiner resource have independent member
hashes. Native libraries and vendor classes are never executed.

The follow-up reports cover Yelp voice input, corrected VSB topic routing,
recipient-specific callbacks, Performance timer export/upload and a ranked
capability assessment in `docs/kim19_capability_assessment.md`.

```powershell
python -m analysis_tools.kim19_runtime_analysis `
  --work "$CorpusRoot/work" `
  --output reports/kim19_runtime_analysis --javap javap
python -m analysis_tools.kim19_runtime_analysis `
  --work "$CorpusRoot/work" `
  --output reports/kim19_runtime_analysis --javap javap --check
python -m unittest analysis_tools.tests.test_kim19_runtime_analysis -v
```

The second command compares every generated byte without writing. Use the same
JDK for reproducible `javap` output hashes (validated here with JDK 8u504).
`javap -s -c -p` independently checks retained invocation BCIs within the exact
method/descriptor; it does not execute classes. The CLI rejects an output under
the recovered work root. All outputs belong in the isolated analysis checkout.

The predicate helper supports only valid recovered `/pps/can/` descriptors.
`known_predicates_match` returns `None` when an attribute is missing, rather than
inventing native missing-data semantics. The native updater can continue after
a missing attribute, and it also has a default-visible path when no condition
flag/super-app identity applies. Valid parsing sets the condition flag. These
helpers must never be used to infer unconditional target visibility or DRM.

Human-reviewed guidance starts at `docs/kim19_runtime_observation_model.md` and
`docs/target_observation_checklist.md`; verification results are in
`reports/kim19_runtime_analysis/verification.md`.

### Deterministic Yelp observation mapping

`yelp_observation_analysis.py` generates a ninth, separately reviewed failure-
signature report without changing the existing KIM19 generator or its eight
outputs. Its model binds native predicates, packaged user-visible messages,
caller/BCI transitions, A-H outcomes, and the exact Yelp/appManager hashes. The
generator and analyzer do not open a network connection, execute a recovered
class, or inspect a radio.

```powershell
python -m analysis_tools.yelp_observation_analysis
python -m analysis_tools.yelp_observation_analysis --check
python -m analysis_tools.yelp_observation_analysis --check `
  --app-manager PATH_TO_RECOVERED_APPMANAGER --yelp-jar PATH_TO_RECOVERED_YELP_JAR
python tools/analyze_yelp_observation.py observation.json
python -m unittest analysis_tools.tests.test_yelp_observation_analysis -v
```

The analyzer accepts the strict JSON fields documented in
`docs/yelp_target_observation_analysis.md`. Omitted fields remain unknown or
unobserved. It rejects contradictions instead of filling gaps, matches packaged
failure text with normalized case and punctuation, and emits canonical JSON with
one next static question and one benign observation. A string match is not
promoted to proof of network traffic or backend acceptance.

### Complete KIM19 Yelp runtime reports

`kim19_yelp_analysis.py` is the final Yelp-specific recovered-artifact report
generator. It reads only the declared descriptor, key JAR, and Yelp JAR;
verifies their exact sizes and SHA-256 values before and after analysis; parses
classes without loading them; binds reviewed Java evidence to class, method,
descriptor, BCI, opcode, owner, name, and callee descriptor; and emits exactly
seven sorted JSON reports. Fixed service material is never emitted: the
authorization value is represented only by category, redaction note, and hash.

```powershell
$CorpusWork = 'E:\Documents\GitHub\jeep_uconnect_custom\analysis_ra4_18.45.01\work'
$Python = 'E:\Documents\GitHub\jeep_uconnect_custom\analysis_work\post_reboot_20260906\venv\Scripts\python.exe'
& $Python -m analysis_tools.kim19_yelp_analysis --work $CorpusWork --output reports/kim19_yelp
& $Python -m analysis_tools.kim19_yelp_analysis --work $CorpusWork --output reports/kim19_yelp --check
& $Python -m unittest analysis_tools.tests.test_kim19_yelp_analysis -v
```

The outputs are `launch_graph.json`, `runtime_gates.json`,
`input_dataflow.json`, `network_fields.json`, `response_actions.json`,
`failure_paths.json`, and `stock_handoffs.json`. Check mode compares exact bytes
and rejects stale, missing, or unexpected files. Verification used Python 3.11,
cryptography 50.0.1, pyelftools 0.33, capstone 5.0.7, jawa, and Temurin JDK
8u504 `javap -s -c -p`.

The generator opens no network connection, executes no vendor class, and writes
only its output directory. It does not inspect or modify a radio. Yelp JAR
SHA-256 is `f05efd2048577c5c5b32532ff9a46a8f42a31e0508946b072d337ab2077b3282`;
descriptor SHA-256 is
`57a3a5defa8fcdcff2b178954b15eff7ba6a22c12140088c1b24ce2a36c9b878`.
