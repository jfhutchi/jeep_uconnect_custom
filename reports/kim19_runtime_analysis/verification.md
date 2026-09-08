# Verification record

Date: 2026-09-07. Starting isolated checkpoint:
`25fe4d3dc9379e7278cee5ae1ea684715c618430` on
`codex/stock-signed-capability-analysis`.

**PROVED:** the relevant suite passes: 84 tests, zero failures/errors. This
includes the prior 48-test suite, fourteen runtime-model tests and 22 existing
ELF/ARM-analysis tests. Command:

```powershell
python -m unittest `
  analysis_tools.tests.test_kim19_runtime_analysis `
  analysis_tools.tests.test_target_production_index `
  analysis_tools.tests.test_stock_capability_index `
  analysis_tools.tests.test_evidence_model `
  analysis_tools.tests.test_java_classfile `
  analysis_tools.tests.test_activation_graph `
  analysis_tools.tests.test_resident_surface_census `
  analysis_tools.tests.test_native_endpoint_census `
  analysis_tools.tests.test_render_stock_extension_reports `
  analysis_tools.tests.test_lua51_inspect `
  analysis_tools.tests.test_arm_elf_analysis -v
```

**PROVED:** the generator re-inventories all KIM19 files, requires identical
canonical JSON to the baseline, checks embedded/external app ID/name/version/main
class consistency, and resolves `68224525AM` to KIM19 with no fallback. All 19
JAR hashes and the full 37-file manifest remain unchanged. The 24-file common
base, 34 prior source records and the newly traced appManager configuration are
rehashed before and after extraction (96 records total, with deliberate overlap
between manifests and evidence sources).

**PROVED:** two independent generation passes compare identically for all eight
JSON outputs using `--check`. Tool and reviewed selection/interpretation notes
are committed; the notes' hash is included in each report. Source-resource
hashes bind the selected broker/MTS/wallet properties. Commands:

```powershell
python -m analysis_tools.kim19_runtime_analysis `
  --work "$CorpusRoot/work" `
  --output reports/kim19_runtime_analysis --javap javap
python -m analysis_tools.kim19_runtime_analysis `
  --work "$CorpusRoot/work" `
  --output reports/kim19_runtime_analysis --javap javap --check
```

**PROVED:** independent JDK 8u504 `javap -s -c -p` checks 934 retained invocation
sites across 37 key classes, matching method, descriptor and BCI. This includes
Register's lifecycle/state helper, Yelp's init/splash/request/response path,
L-Series vehicle rejection, Store loading, VSB WMA setup and DrmManager, plus
Yelp voice/service/queue callbacks, VSB topic getter/router/notification paths,
Performance upload/export and packaged Affiner loading. Output
hashes are recorded in `validation.json`; no full vendor disassembly dumps or
credential values are committed. These are static checks, not vendor execution.

**PROVED:** native visibility conclusions were manually reviewed against
Capstone ARM disassembly of the hash-bound appManager. The review follows the
updater's flag branches, missing-attribute continuation, final store, catalog
consumers and ASSIST special helper. Import resolution identifies getenv/atoi/
strcmp/memcmp. Follow-up analysis identifies the condition-presence and super-app
flags through parser/UUID comparison stores and their consumers, with sixteen
bounded ARM instruction windows in the generated evidence. Window extraction
rejects incomplete decoding and binds addresses/file offsets/source hashes.
Virtual catalog predicate semantics remain **UNKNOWN**. Canonical notes hashing
is independent of Windows/Unix line endings. The previously unidentified
condition-clear branch is now traced to VSBClient allocation/configuration:
the normal path preserves the same object in r4/r5 before changing the property
pointer. No arbitrary external access to that internal dispatcher is inferred.

**PROVED:** the application/service graph binds 23 reviewed relationships to
exact invocation tuples and rejects missing or mismatched source methods/calls,
duplicate IDs and unknown nodes. It contains all nine app identities and seven
service/output nodes. Graph conditions remain reviewed interpretations, not
automatic runtime reachability. Selected Performance export settings and the
bundled native library have resource hashes. No binary is copied into reports.

**PROVED:** intended tracked changes are only the new focused tool, reviewed
notes, fourteen runtime-model tests, seven documents, eight JSON reports, this
verification record and the analysis-tools README. No recovered payload, JAR, class, firmware or key
is added. Baseline reports remain unchanged. Markdown link targets and staged
whitespace are checked before commit.

**PROVED:** all writes and Git mutations are confined to
`E:/Documents/GitHub/jeep_uconnect_custom_stock_signed_capability`. The original
checkout is only read with optional Git locks disabled; no stash/reset/restore/
clean/checkout/staging operation is performed there. Its verified HEAD remains
`894afe8e5361c3595623de599e62ba0f0c0d9f78`, with 40 tracked modifications and one
untracked file. Final review also compares its status and binary diff hashes
against the verification snapshot:

- Status SHA-256: `48adcf412315324596610736df3a34d484f517df288741475434205fb4fc4ee4`
- Diff SHA-256: `d640dce2da93cbd40692549754f74ee796b897b00d5a38060d4ad17172cdc792`

**UNKNOWN / TARGET OBSERVATION REQUIRED:** current target binary identities,
registration, visibility flags, grants, running Xlets, interfaces, listeners and
backend availability. No live radio or external service was probed. These
limitations are part of the result, not failed verification tests.

## Yelp observation framework update

Date: 2026-09-08. Starting isolated checkpoint:
`22b85f5b9721d3a107529f05fff125b0147b1334` on
`codex/stock-signed-capability-analysis`.

**PROVED:** the bounded native follow-up resolves the three targeted
`CAppManagerApp` vtable selectors. Selector `0x10` calls implementation
`0x10bcbc` and returns headless byte `app+0x284`; selector `0x0c` calls
`0x10bcf4` and returns daemon byte `app+0x239`; selector `0x18` calls
`0x10bc4c` and returns `hasGUI` byte `app+0x295`. Together with direct
`showInHmi` byte `app+0x4d`, the target branch requires
`!headless && (!daemon || hasGUI) && showInHmi`. This corrects the previous
**UNKNOWN** semantic names without changing an earlier generated report.

**PROVED:** the separate Yelp model generates 30 sorted failure signatures.
Each record contains packaged English match text, resource identifier,
trigger/status, caller or recovered method evidence, transition, interpretation,
visibility/return limits, and retry limits. Local motion/location/phone/
navigation/VR failures remain separate from generic request collapse and parsed
response errors. Localized resources share those caller families and are not
duplicated as separate signatures.

**PROVED:** independent `javap -c -p` inspection confirms the main selected UI
sites, including `GpCVPKeyboard.fireOKPressed` AlertDialog BCI350 and generic
failure BCI477; `GpPlaceIconButton.click` generic failure BCI333; and
`SpeechListener.onVRAction` AlertDialog BCI148 and generic failure BCI275.
`SpeechListener.onError` shows the generic failure dialog at BCI41. The prior
934-site JDK validation remains unchanged.

**PROVED:** 95 relevant tests pass with zero failures/errors. This is the prior
84-test KIM19/production/native suite plus eleven Yelp observation tests. The
new tests cover A-H, partial observations, all suggested physical-record field
types, contradictions, exact predicate binding, failure provenance, source-hash
failure, canonical CLI bytes, and report freshness.

**PROVED:** the original `kim19_runtime_analysis` generator reports
`8 reports verified; recovered sources unchanged`. Their SHA-256 values remain:

- `application_activation_matrix.json`: `110e73422041811f1ab51fba4385db9534a01f183e59714306c012581e25d077`
- `application_service_graph.json`: `b415fcd7ff3d4c8dcb048246380cd71799e905771b9f70da5ae6081684f3e98f`
- `background_services.json`: `865b2f2d4dd9a3d5b3a65d3cdec0fa3d4356851816a0e896712bed16af0459d0`
- `method_evidence.json`: `93a387a36ce4fdf9666f8d14fd5b302634b2162f628f7cf046e7a691a992e7b0`
- `network_capabilities.json`: `e4a87a93a2ef8284780f99869bad53ca86c15ef78d1ee46348ab691398a1541e`
- `observation_inference_matrix.json`: `cf666806b38921fabf6bed6839b14458c618492b4288fe2f8eb88e6ca190a29b`
- `validation.json`: `4c17e74ef2c58c282d1a53de9baa71b6df7f479abc01599a85a8286ec5b7bc5f`
- `yelp_reachability.json`: `924b96b4056d389975f5dfc06bfe15bc86299920113a1a734f962f2cae3e6392`

**PROVED:** the new generator hash-checks recovered appManager SHA-256
`608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591`
and Yelp JAR SHA-256
`f05efd2048577c5c5b32532ff9a46a8f42a31e0508946b072d337ab2077b3282`.
One write pass and two `--check` passes succeed. Repeated representative A, D,
and G analyzer outputs have identical canonical bytes. Markdown validation finds
zero broken local links; whitespace checks pass.

**PROVED:** original-checkout verification uses NUL-delimited porcelain to avoid
line-ending ambiguity. HEAD remains
`894afe8e5361c3595623de599e62ba0f0c0d9f78`; the 40 tracked modifications and
one untracked path produce status SHA-256
`48adcf412315324596610736df3a34d484f517df288741475434205fb4fc4ee4`.
The binary diff remains
`d640dce2da93cbd40692549754f74ee796b897b00d5a38060d4ad17172cdc792`.
No original-checkout mutation was performed.

**UNKNOWN / TARGET OBSERVATION REQUIRED:** the framework does not claim Yelp is
present, visible, launchable, provisioned, connected, accepted by its backend,
or fully functional on the radio. The A-H result becomes evidence only after the
corresponding ordinary observation is supplied.

## Complete Yelp runtime reconstruction

Date: 2026-09-08. Work is confined to isolated branch
`codex/kim19-yelp-reconstruction`, based on prior Performance Pages checkpoint
`371c4fa44228b642ddbc7574fb09df5adb067bb7`.

**PROVED:** the Yelp-specific analyzer hash-binds descriptor, key JAR, and Yelp
JAR, parses rather than loads classes, rejects credential-like public strings,
and emits exactly seven deterministic reports. They cover launch, gates,
touch/voice/RMS inputs, request fields, response sinks, layered failures, and
stock phone/navigation handoffs. Fixed authorization material is omitted and
only a SHA-256 is retained.

**PROVED:** independent Temurin JDK 8u504 `javap -s -c -p` inspection confirmed
the selected lifecycle, splash, home, keyboard, speech, URL, header, JSON,
phone, navigation, `PhoneImpl`, and `NavigationImpl` blocks. Recovered platform
`kona.jar` SHA-256 is
`19390472018f02d998690b982f00eb68da5d40d7a8d6fba91499677651015f92`.

**PROVED safety boundary:** no Yelp, geocode, speech, VSB, SDP, phone,
navigation, or other endpoint was contacted; no recovered class was executed;
no target or firmware state was modified. Current target and live-service
claims remain **TARGET OBSERVATION REQUIRED**.

**PROVED verification:** 297 analysis-tool tests pass with zero failures/errors.
One write pass and two exact-byte `--check` passes report seven verified Yelp
reports and unchanged recovered sources. The seven report SHA-256 values are:

- `failure_paths.json`: `b427fc103130d0a063f03bd0f65c6698e2d07955ec852a1f9820d865c95aaf0c`
- `input_dataflow.json`: `cd50425bb61efa8ab8c8c001748658c429d81fd047ccd49f623b5cc0305bf44b`
- `launch_graph.json`: `790c4b9ca80f486565614c092a0b2d875e82576809b0135c163ea72d3a635768`
- `network_fields.json`: `7904348b05bd5fb1cc5d7cb0152790999b5b6532d4fbd80e2b12837eaef75325`
- `response_actions.json`: `334aefd321ff9b56109ee52fc833196db1b488198fffd902659ad2ac43e11947`
- `runtime_gates.json`: `0aaedb4b5820f87d7980359ba82360ac6719f18789a90064ff3a7522cd8b91bf`
- `stock_handoffs.json`: `608b0d5c7dd0000372c1c8f24ff4a7256aa0b5f001f493cf10d1a7de323fb163`

**PROVED original-checkout preservation:** read-only final checks reproduce
branch `codex/ra4-driver-temperature`, HEAD
`894afe8e5361c3595623de599e62ba0f0c0d9f78`, tracked binary-diff SHA-256
`d640dce2da93cbd40692549754f74ee796b897b00d5a38060d4ad17172cdc792`,
empty staged-diff SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`,
and untracked file Git blob `0aae8d1167e29865adef9e7250e9f352164a10af`.
`git status --porcelain=v2 --branch` with its native LF output reproduces
`f530fba15552b37c70dc7e7b1bd18c2f97721711080e207d7015c65a4d3999ce`
and the same 41 dirty paths.
