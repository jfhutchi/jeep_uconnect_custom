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
