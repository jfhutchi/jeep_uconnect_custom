# Stock Extension Surface Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build deterministic, read-only analyzers and evidence-ledger reports that resolve `SocketCommandSource` activation as far as recovered evidence permits, then census resident Java extension, network/IPC, and user-controlled input surfaces.

**Architecture:** A standard-library JVM classfile parser produces exact type/member/instruction records; an activation graph and bounded archive census turn those records into typed evidence without executing vendor code. A targeted native correlator and schema-validating renderer consume normalized JSON, preserve `PROVED` / `STRONGLY INFERRED` / `UNKNOWN`, and reject any attempt to promote static presence into runtime or reachability claims.

**Tech Stack:** Python 3 standard library (`argparse`, `dataclasses`, `hashlib`, `json`, `pathlib`, `struct`, `tempfile`, `unittest`, `zipfile`), existing read-only ELF/QNX helpers where applicable, Git, Markdown, recovered RA4 artifacts read in place.

---

## File Map

- Create `analysis_tools/evidence_model.py`: evidence classes, seven-state activation ladder, deterministic JSON writer, schema validators.
- Create `analysis_tools/java_classfile.py`: bounded classfile/constant-pool/method/code parser and JVM instruction decoder.
- Create `analysis_tools/activation_graph.py`: typed method graph, SCC calculation, root detection, bounded reverse paths, non-promotion rules.
- Create `analysis_tools/resident_surface_census.py`: sorted JAR/class/resource traversal and Java surface classification.
- Create `analysis_tools/native_endpoint_census.py`: bounded native string/import endpoint correlation for Java-led candidates.
- Create `analysis_tools/render_stock_extension_reports.py`: validate censuses and render the three Markdown reports from the evidence ledger.
- Create `analysis_tools/tests/test_evidence_model.py`: schema, classification, deterministic output, absolute-path rejection tests.
- Create `analysis_tools/tests/test_java_classfile.py`: synthetic classfile and bytecode parser tests.
- Create `analysis_tools/tests/test_activation_graph.py`: recursion, root, path, unresolved dispatch, and state-ladder tests.
- Create `analysis_tools/tests/test_resident_surface_census.py`: synthetic JAR/resource/surface tests.
- Create `analysis_tools/tests/test_native_endpoint_census.py`: synthetic native endpoint/correlation tests.
- Create `analysis_tools/tests/test_render_stock_extension_reports.py`: exact-five and required-field rendering tests.
- Create `reports/stock_extension_surface/evidence_ledger.json`: curated, source-addressed judgments and exactly five ranked candidates.
- Create `reports/stock_extension_surface/activation_call_paths.json`: method-level SocketCommandSource and activation evidence.
- Create `reports/stock_extension_surface/java_extension_surfaces.json`: recovered resident Java extension census.
- Create `reports/stock_extension_surface/network_ipc_endpoints.json`: Java/native network and IPC census.
- Create `reports/stock_extension_surface/user_controlled_input_surfaces.json`: origin-to-capability chains and missing links.
- Create `docs/stock_extension_surface.md`: controlling verdict and exactly five ranked candidates.
- Create `docs/resident_network_services.md`: socket/listener/client/IPC details and reachability boundaries.
- Create `docs/user_controlled_input_surface.md`: user-controlled origin, parser/dispatcher, and capability chains.
- Modify `analysis_tools/README.md`: safe reproduction commands and evidence limitations.

### Task 1: Evidence Model and Deterministic Output

**Files:**
- Create: `analysis_tools/evidence_model.py`
- Create: `analysis_tools/tests/test_evidence_model.py`

- [ ] **Step 1: Write failing evidence-model tests**

Create tests that require exactly the locked classifications, all seven
activation states, source references for proved claims, stable JSON output,
and rejection of absolute host paths:

```python
import json
from pathlib import Path
import tempfile
import unittest

from analysis_tools.evidence_model import (
    ACTIVATION_STATES, CLASSIFICATIONS, validate_activation_ladder,
    validate_evidence, write_json,
)


class EvidenceModelTests(unittest.TestCase):
    def test_locked_vocabulary_and_complete_activation_ladder(self):
        self.assertEqual(CLASSIFICATIONS, ("PROVED", "STRONGLY INFERRED", "UNKNOWN"))
        self.assertEqual(ACTIVATION_STATES, (
            "class_exists", "statically_reachable", "activation_mechanism_exists",
            "activation_configured", "production_enabled", "listener_executable",
            "externally_reachable",
        ))
        ladder = {name: {"classification": "UNKNOWN", "evidence": []}
                  for name in ACTIVATION_STATES}
        validate_activation_ladder(ladder)
        del ladder["externally_reachable"]
        with self.assertRaisesRegex(ValueError, "activation states"):
            validate_activation_ladder(ladder)

    def test_proved_claim_requires_direct_source_reference(self):
        with self.assertRaisesRegex(ValueError, "PROVED.*source"):
            validate_evidence({"classification": "PROVED", "claim": "exists", "sources": []})

    def test_writer_is_deterministic_and_rejects_absolute_paths(self):
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / "out.json"
            write_json(target, {"z": [2, 1], "a": "ok"})
            first = target.read_bytes()
            write_json(target, {"z": [2, 1], "a": "ok"})
            self.assertEqual(first, target.read_bytes())
            self.assertTrue(first.endswith(b"\n"))
            with self.assertRaisesRegex(ValueError, "absolute path"):
                write_json(target, {"input": r"E:\\vendor\\secret.jar"})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests and verify the expected failure**

Run:

```powershell
python -m unittest analysis_tools.tests.test_evidence_model -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'analysis_tools.evidence_model'`.

- [ ] **Step 3: Implement the minimal evidence model**

Implement immutable vocabulary, recursive absolute-path checks, atomic JSON
writing, and validation that `PROVED` claims have at least one source whose
kind is `parsed_structure`, `bytecode_edge`, `resource_structure`,
`artifact_hash`, or `native_call_edge`. Validate that activation ladders have
exactly the seven keys and each value has a locked classification and evidence
list.

- [ ] **Step 4: Run the evidence-model tests and verify they pass**

Run the command from Step 2. Expected: all `EvidenceModelTests` pass with zero
errors or failures.

- [ ] **Step 5: Commit the evidence model**

```powershell
git add -- analysis_tools/evidence_model.py analysis_tools/tests/test_evidence_model.py
git commit -m "analysis: add extension evidence model"
```

### Task 2: Dependency-Free JVM Classfile Structure

**Files:**
- Create: `analysis_tools/java_classfile.py`
- Create: `analysis_tools/tests/test_java_classfile.py`

- [ ] **Step 1: Write failing synthetic classfile tests**

Build class bytes in memory with helpers for UTF-8, Class, NameAndType,
Fieldref, Methodref, InterfaceMethodref, String, Integer, and Code records.
Require parsing of class version, names, superclass, interfaces, fields,
methods, descriptors, constants, exception handlers, and bytecode offsets.
Include a constant-pool Methodref decoy that is never invoked.

The primary assertion is:

```python
model = parse_class(class_fixture())
self.assertEqual(model.name, "example/Server")
self.assertEqual(model.super_name, "java/lang/Object")
self.assertEqual(model.interfaces, ("java/lang/Runnable",))
self.assertEqual([(field.name, field.descriptor) for field in model.fields], [
    ("port", "I"), ("server", "Ljava/net/ServerSocket;"),
])
run = model.method("run", "()V")
self.assertEqual([(i.offset, i.mnemonic) for i in run.instructions], [
    (0, "new"), (3, "dup"), (4, "aload_0"), (5, "getfield"),
    (8, "invokespecial"), (11, "astore_1"), (12, "return"),
])
self.assertEqual([edge.name for edge in run.member_edges], [
    "port", "<init>",
])
self.assertNotIn("unusedDecoy", [edge.name for edge in run.member_edges])
```

Add separate fixtures for `tableswitch`, `lookupswitch`, `wide`,
`invokeinterface`, `invokedynamic`, `getstatic`, `putstatic`, `putfield`,
`ldc`, `ldc_w`, malformed/truncated input, unsupported constant tags, and
declared native/abstract methods.

- [ ] **Step 2: Run the parser tests and verify the expected failure**

Run:

```powershell
python -m unittest analysis_tools.tests.test_java_classfile -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'analysis_tools.java_classfile'`.

- [ ] **Step 3: Implement bounded classfile parsing**

Implement `Reader` methods that bounds-check every read; constant-pool parsing
for tags 1, 3-12, 15-18; two-slot handling for long/double; member and
attribute parsing; Modified UTF-8 compatibility sufficient for ASCII class and
member names; and explicit errors for malformed input. Preserve unknown
attributes by name and length without copying their bytes into results.

Expose frozen records for `ClassModel`, `FieldModel`, `MethodModel`,
`Instruction`, `MemberEdge`, and `ExceptionHandler`. `ClassModel.method()`
must require an exact name/descriptor and fail on absence or ambiguity.

- [ ] **Step 4: Implement the instruction decoder**

Use a complete JVM opcode-width table for fixed-width instructions and
dedicated parsing for `tableswitch`, `lookupswitch`, and `wide`. Resolve only
operands that actually occur in decoded bytecode. Tag member edges as
`field_read`, `field_write`, `invoke_static`, `invoke_special`,
`invoke_virtual`, `invoke_interface`, `invoke_dynamic`, `construct`,
`class_literal`, or `string_literal` as applicable.

- [ ] **Step 5: Run the parser tests and the existing JVM inventory tests**

Run:

```powershell
python -m unittest analysis_tools.tests.test_java_classfile -v
python -m unittest analysis_tools.tests.test_jvm_call_inventory -v
```

Expected: new parser tests pass. The existing JVM inventory suite passes when
its documented `jawa==2.2.0` host dependency is present; otherwise its exact
baseline `ModuleNotFoundError: jawa` remains separately recorded.

- [ ] **Step 6: Commit the classfile parser**

```powershell
git add -- analysis_tools/java_classfile.py analysis_tools/tests/test_java_classfile.py
git commit -m "analysis: parse resident JVM class structure"
```

### Task 3: Activation Graph and Evidence Ladder

**Files:**
- Create: `analysis_tools/activation_graph.py`
- Create: `analysis_tools/tests/test_activation_graph.py`

- [ ] **Step 1: Write failing graph tests**

Construct synthetic `MethodNode` and `CallEdge` records for an Xlet lifecycle
root, a factory path, an uncalled test listener, a recursive pair, and an
unresolved interface call. Assert SCC condensation, deterministic bounded
reverse paths, and no automatic activation-state promotion:

```python
graph = ActivationGraph(nodes, edges)
self.assertEqual(graph.reverse_paths("example/SocketSource#run()V", max_depth=8), [
    ["example/MainXlet#startXlet()V", "example/Factory#create()Ljava/lang/Object;",
     "example/SocketSource#<init>()V", "example/SocketSource#run()V"],
])
self.assertEqual(graph.strong_components(), [
    ("example/A#a()V", "example/B#b()V"),
])
ladder = graph.activation_ladder("example/SocketSource")
self.assertEqual(ladder["class_exists"]["classification"], "PROVED")
self.assertEqual(ladder["production_enabled"]["classification"], "UNKNOWN")
self.assertEqual(ladder["externally_reachable"]["classification"], "UNKNOWN")
```

Require explicit root categories for Xlet lifecycle, UI callback, service
callback, factory/provider, configuration, registration, feature flag, test
framework, thread/Runnable, and unknown external entry.

- [ ] **Step 2: Run the graph tests and verify the expected failure**

Run:

```powershell
python -m unittest analysis_tools.tests.test_activation_graph -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'analysis_tools.activation_graph'`.

- [ ] **Step 3: Implement nodes, typed edges, SCCs, and bounded paths**

Implement deterministic Tarjan SCCs and breadth-first reverse path search.
Reject non-positive bounds. Record truncation when more than 100 paths or a
depth beyond 32 is requested. Do not treat field/type/string/config references
as executable call edges. Treat virtual/interface targets as unresolved unless
the census proves a unique implementation.

- [ ] **Step 4: Implement activation-state judgments**

`class_exists` may be `PROVED` from a parsed class. `statically_reachable` may
be `PROVED` only from a complete syntactic path rooted in parsed resident code.
The remaining states require separately supplied evidence records and default
to `UNKNOWN`; no state inherits the classification of a prior state.

- [ ] **Step 5: Run graph and evidence tests**

Run:

```powershell
python -m unittest analysis_tools.tests.test_evidence_model analysis_tools.tests.test_activation_graph -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit the activation graph**

```powershell
git add -- analysis_tools/activation_graph.py analysis_tools/tests/test_activation_graph.py
git commit -m "analysis: model resident activation paths"
```

### Task 4: Resident Archive and Extension-Surface Census

**Files:**
- Create: `analysis_tools/resident_surface_census.py`
- Create: `analysis_tools/tests/test_resident_surface_census.py`

- [ ] **Step 1: Write failing archive-safety and classification tests**

Create temporary synthetic JARs in shuffled order containing original fixture
classes and small properties/XML/JSON resources. Test sorted deterministic
output, duplicate member reporting, archive traversal rejection, symlink
non-following, byte/count limits, absolute-root redaction, Java-properties
last-key-wins plus duplicate retention, XML external-entity rejection, and
binary-payload omission.

Class fixtures must exercise all requested categories:

```python
expected_categories = {
    "dynamic_loading", "reflection", "configured_class", "factory_provider",
    "resource_package_loading", "scripting_interpreter", "url_protocol",
    "browser_webkit", "structured_data", "network_service", "ipc_service",
    "media_import", "user_file_resource", "plugin_registration",
}
self.assertEqual({surface["category"] for surface in result["surfaces"]},
                 expected_categories)
```

Require each surface to contain `origin`, `signed_component`, `parser`,
`dispatcher`, `capability`, `missing_links`, `classification`, and `sources`.
Assert that an API-only fixture is `PROVED` static presence while its complete
origin-to-capability path remains `UNKNOWN`.

- [ ] **Step 2: Run the census tests and verify the expected failure**

Run:

```powershell
python -m unittest analysis_tools.tests.test_resident_surface_census -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'analysis_tools.resident_surface_census'`.

- [ ] **Step 3: Implement safe sorted archive traversal**

Accept only explicit `--root LABEL=PATH` inputs. Enumerate `.jar`, `.zip`, and
loose `.class` files in sorted relative-path order without following symlinks.
Hash files by streaming reads. Open classes in memory with per-member,
per-archive, total-byte, archive-count, and class-count bounds. Reject absolute
or `..` archive member paths and retain duplicate names as errors.

- [ ] **Step 4: Implement type-aware resource parsing and surface rules**

Add small-text decoding with BOM detection and strict UTF-8/ISO-8859-1 rules,
Java properties parsing, safe XML parsing after rejecting `DOCTYPE`/`ENTITY`,
and strict JSON parsing. Surface rules match parsed invocation owners/names,
descriptors, actual string-load instructions, and structured resource fields.
Constant-pool strings not loaded by bytecode remain `constant_pool_presence`.

- [ ] **Step 5: Implement the four-schema CLI output**

Support:

```powershell
python -m analysis_tools.resident_surface_census `
  --root 'resident=E:/explicit/read-only/root' `
  --focus-class 'com/tweddle/test/input/SocketCommandSource' `
  --output-dir reports/stock_extension_surface
```

The CLI emits the four required JSON files atomically with schema version,
tool version, input manifest hashes, coverage counts, bounded errors, and no
absolute paths. Focus-mode failure to parse the selected class or a direct
caller exits nonzero.

- [ ] **Step 6: Run the census tests and deterministic double-run test**

Run:

```powershell
python -m unittest analysis_tools.tests.test_resident_surface_census -v
```

Expected: all tests pass, including byte-identical output from shuffled input
orders.

- [ ] **Step 7: Commit the resident census**

```powershell
git add -- analysis_tools/resident_surface_census.py analysis_tools/tests/test_resident_surface_census.py
git commit -m "analysis: census resident Java extension surfaces"
```

### Task 5: Exhaust SocketCommandSource Before Broad Scanning

**Files:**
- Modify: `reports/stock_extension_surface/activation_call_paths.json`
- Modify: `reports/stock_extension_surface/java_extension_surfaces.json`
- Modify: `reports/stock_extension_surface/network_ipc_endpoints.json`
- Modify: `reports/stock_extension_surface/user_controlled_input_surfaces.json`
- Create: `reports/stock_extension_surface/socket_command_source_notes.md`

- [ ] **Step 1: Locate every occurrence without extracting artifacts**

Run from the analysis worktree, reading the protected checkout only:

```powershell
$Ra4CorpusRoot = 'E:/Documents/GitHub/jeep_uconnect_custom/analysis_ra4_18.45.01'
python -m analysis_tools.resident_surface_census `
  --root "resident=$Ra4CorpusRoot/work/secondary_iso/usr/share/XLETS" `
  --focus-class 'com/tweddle/test/input/SocketCommandSource' `
  --output-dir reports/stock_extension_surface
```

Expected: exit 0; at least one selected class matches the already documented
SHA-256 `55bf4d4ca3872b4434f69c4d9fe0c04e64fcef69da0682381ca91d904d972edb`.
If the hash differs or no class is found, stop the focused verdict and record
the corpus mismatch rather than substituting another artifact.

- [ ] **Step 2: Review all direct structural evidence**

Inspect the generated records for every occurrence, distinct hash,
superclass/interface, field, method, constructor descriptor, constructor field
write, static initializer, object construction, call, field access, class
literal, loaded string, configured-name reference, and consumer-interface
edge. Add only source-addressed interpretations to
`socket_command_source_notes.md`.

- [ ] **Step 3: Review all recursive paths toward activation roots**

Inspect SCCs and every bounded forward/reverse path toward Xlet lifecycle, UI,
service callback, configuration, registration, factory/provider, feature flag,
thread/Runnable, and test-framework roots. Record unresolved virtual/interface,
reflection, native, missing-class, and out-of-corpus edges separately.

- [ ] **Step 4: Recover listener and protocol behavior structurally**

For every socket-related method, record the exact bytecode evidence for
address/interface, port, backlog, blocking calls, loop branches, `accept`,
connection ownership, stream wrappers, encoding, framing, command comparison,
dispatcher calls, handlers, replies, error paths, flush, close/finally, and
shutdown. Use `UNKNOWN` for values or semantics that cannot be reconstructed
without source-level invention.

- [ ] **Step 5: Enumerate every gate and complete the seven-state ladder**

Record authentication, authorization, source-address, application state,
configuration, entitlement/policy, and environment gates. Explicitly fill all
seven states even when the last five remain `UNKNOWN`. Conclude only the
bounded recovered-corpus verdict: activatable, statically reachable with an
unproved activation link, or dormant/test code with named residual unknowns.

- [ ] **Step 6: Regenerate focus outputs and verify deterministic identity**

Run the focus command twice, hash all four JSON outputs after each run, and
require identical SHA-256 values. Expected: no absolute host path appears and
no archive/class/resource payload is present.

- [ ] **Step 7: Commit only metadata and analysis notes**

```powershell
git add -- reports/stock_extension_surface/activation_call_paths.json `
  reports/stock_extension_surface/java_extension_surfaces.json `
  reports/stock_extension_surface/network_ipc_endpoints.json `
  reports/stock_extension_surface/user_controlled_input_surfaces.json `
  reports/stock_extension_surface/socket_command_source_notes.md
git commit -m "research: exhaust SocketCommandSource activation evidence"
```

Before committing, inspect the staged path list and blob types and record:
`Stock/vendor firmware staged: NO`.

### Task 6: Targeted Native/QNX Endpoint Correlation

**Files:**
- Create: `analysis_tools/native_endpoint_census.py`
- Create: `analysis_tools/tests/test_native_endpoint_census.py`
- Modify: `reports/stock_extension_surface/network_ipc_endpoints.json`

- [ ] **Step 1: Write failing native-correlation tests**

Create small synthetic byte blobs and minimal existing-test ELF fixtures.
Require bounded extraction of ASCII endpoint/path markers, imported socket and
QNX IPC symbols when structurally available, exact Java/native name matches,
and evidence-boundary classifications:

```python
result = correlate(java_endpoints, native_records)
self.assertEqual(result[0]["match_kind"], "exact_endpoint_name")
self.assertEqual(result[0]["classification"], "PROVED")
self.assertEqual(result[0]["production_enabled"], "UNKNOWN")
self.assertEqual(result[0]["externally_reachable"], "UNKNOWN")
```

Test that raw words inside archive-like data do not become imports or calls,
oversized files are explicitly skipped, symlinks are not followed, and output
contains hashes/offsets rather than payloads.

- [ ] **Step 2: Run the native tests and verify the expected failure**

Run:

```powershell
python -m unittest analysis_tools.tests.test_native_endpoint_census -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'analysis_tools.native_endpoint_census'`.

- [ ] **Step 3: Implement bounded candidate-led native scanning**

Accept Java endpoint JSON plus explicit labeled native roots. Search only the
API families and endpoint/path/event names selected from high-value Java
candidates. Reuse `analysis_tools.qnx_usb_inventory.elf_metadata` only when
`pyelftools` is available; otherwise emit a dependency error and continue with
bounded strings/known existing structural records without fabricating import
evidence.

- [ ] **Step 4: Run native tests and targeted recovered scan**

Run tests, then invoke the scanner against only recovered primary/hidden-QNX
roots implicated by the Java candidate names. Expected: deterministic JSON;
each record states whether it is string presence, structured import/export,
native call edge, dispatcher comparison, or exact endpoint correlation.

- [ ] **Step 5: Commit the correlator and endpoint update**

```powershell
git add -- analysis_tools/native_endpoint_census.py `
  analysis_tools/tests/test_native_endpoint_census.py `
  reports/stock_extension_surface/network_ipc_endpoints.json
git commit -m "analysis: correlate resident and QNX endpoints"
```

### Task 7: Report Renderer and Exactly-Five Contract

**Files:**
- Create: `analysis_tools/render_stock_extension_reports.py`
- Create: `analysis_tools/tests/test_render_stock_extension_reports.py`
- Create: `reports/stock_extension_surface/evidence_ledger.json`

- [ ] **Step 1: Write failing renderer contract tests**

Build a complete synthetic ledger with five candidates and all required fields.
Assert generation of three reports and rejection of four or six candidates,
missing candidate fields, missing activation states, proved claims with only
inferential sources, static-presence language promoted to execution, and
absolute input paths.

Required candidate keys are:

```python
REQUIRED_CANDIDATE_FIELDS = {
    "rank", "component", "activation_path", "user_controlled_input",
    "useful_resulting_capability", "prerequisites", "evidence_classification",
    "unresolved_unknowns", "new_package_authorization_required",
}
```

- [ ] **Step 2: Run renderer tests and verify the expected failure**

Run:

```powershell
python -m unittest analysis_tools.tests.test_render_stock_extension_reports -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'analysis_tools.render_stock_extension_reports'`.

- [ ] **Step 3: Implement schema validation and deterministic rendering**

Render stable section order, evidence legend, corpus coverage, errors,
SocketCommandSource verdict and seven-state table, detailed network/IPC table,
user-controlled origin chains, and exactly five ranked candidates. Each claim
line begins with `PROVED`, `STRONGLY INFERRED`, or `UNKNOWN`. Reject target
instructions, bypass terms used as recommendations, and payload-shaped binary
content in the ledger.

- [ ] **Step 4: Run renderer tests**

Run the command from Step 2. Expected: all tests pass.

- [ ] **Step 5: Commit the renderer**

```powershell
git add -- analysis_tools/render_stock_extension_reports.py `
  analysis_tools/tests/test_render_stock_extension_reports.py
git commit -m "analysis: render stock extension evidence reports"
```

### Task 8: Broad Resident Census After Focus Completion

**Files:**
- Modify: `reports/stock_extension_surface/activation_call_paths.json`
- Modify: `reports/stock_extension_surface/java_extension_surfaces.json`
- Modify: `reports/stock_extension_surface/network_ipc_endpoints.json`
- Modify: `reports/stock_extension_surface/user_controlled_input_surfaces.json`
- Modify: `reports/stock_extension_surface/evidence_ledger.json`

- [ ] **Step 1: Run the complete signed resident Java scan**

Use the explicit XLETS/KIM roots under the recovered secondary tree. Preserve
the completed focus records while adding census coverage for dynamic loading,
reflection, configured factories/providers, resources/packages, scripting,
URLs/protocols, browser/WebKit, structured data, sockets, IPC/services,
media/import, files/resources, and plugin registration.

- [ ] **Step 2: Build origin-to-capability chains**

For every high-value surface, attempt to fill:

```text
external/user-controlled origin
  -> signed resident component
  -> parser/dispatcher
  -> useful resulting capability
```

Keep absent arrows in `missing_links`; do not rank an API-only or parser-only
record as a complete mechanism.

- [ ] **Step 3: Select exactly five candidates by evidence and utility**

Rank the best five mechanisms using path completeness first, useful stock
capability second, prerequisites third, and novelty never. Fill all required
fields and answer `new_package_authorization_required` with `yes`, `no`, or
`unknown` plus evidence. Preserve lower-ranked census records outside the final
five.

- [ ] **Step 4: Run targeted QNX correlation for unresolved high-value links**

Use only endpoint names, paths, and services belonging to the selected or
near-selected candidates. Do not broaden into unrelated native reverse
engineering. Update correlations and classifications without promoting runtime
or reachability states.

- [ ] **Step 5: Validate and commit census data**

Run all new analyzer tests, validate every JSON file, check deterministic
regeneration, inspect the staged paths/blob types, then commit only JSON and
curated metadata:

```powershell
git add -- reports/stock_extension_surface
git commit -m "research: census resident stock extension surfaces"
```

Record: `Stock/vendor firmware staged: NO`.

### Task 9: Render Required Reports and Document Reproduction

**Files:**
- Create: `docs/stock_extension_surface.md`
- Create: `docs/resident_network_services.md`
- Create: `docs/user_controlled_input_surface.md`
- Modify: `analysis_tools/README.md`

- [ ] **Step 1: Render all three reports from validated JSON**

Run:

```powershell
python -m analysis_tools.render_stock_extension_reports `
  --input-dir reports/stock_extension_surface `
  --docs-dir docs
```

Expected: exit 0 and exactly the three required Markdown files are created.

- [ ] **Step 2: Verify the controlling report contract**

Programmatically assert exactly five ranked candidates and each required field;
all seven SocketCommandSource states; all three classifications; explicit
class-exists versus static-reachability versus activation/configuration/
production/execution/external-reachability distinctions; and no unsupported
target-action language.

- [ ] **Step 3: Add safe reproduction commands to the analyzer README**

Document prerequisites, explicit corpus-root arguments, focus-first command,
broad command, targeted native command, renderer command, tests, deterministic
double-run check, and evidence limitations. State that tools never execute
recovered artifacts and outputs must not include absolute corpus paths or
binary payloads.

- [ ] **Step 4: Commit reports and reproduction documentation**

```powershell
git add -- docs/stock_extension_surface.md docs/resident_network_services.md `
  docs/user_controlled_input_surface.md analysis_tools/README.md
git commit -m "docs: report stock extension evidence ladder"
```

Record: `Stock/vendor firmware staged: NO`.

### Task 10: Fresh Verification and Repository-Safety Audit

**Files:**
- Verify only; modify earlier files only if a failing test or audit exposes a
  concrete defect, then rerun the applicable red-green cycle.

- [ ] **Step 1: Run all new deterministic tests**

```powershell
python -m unittest `
  analysis_tools.tests.test_evidence_model `
  analysis_tools.tests.test_java_classfile `
  analysis_tools.tests.test_activation_graph `
  analysis_tools.tests.test_resident_surface_census `
  analysis_tools.tests.test_native_endpoint_census `
  analysis_tools.tests.test_render_stock_extension_reports -v
```

Expected: zero failures and zero errors.

- [ ] **Step 2: Run the full existing analyzer suite**

```powershell
python -m unittest discover -s analysis_tools/tests -v
```

Expected: zero behavioral failures. If `cryptography`, `jawa`, or `pyelftools`
remain absent, report their exact already-baselined import errors separately;
do not describe the full suite as passing.

- [ ] **Step 3: Verify deterministic regeneration**

Generate all JSON and Markdown into two separate temporary directories from the
same explicit read-only corpus roots, recursively hash their files, and compare
the relative-path/hash maps. Expected: identical maps.

- [ ] **Step 4: Verify schemas and evidence boundaries**

Run a standard-library validation script that loads every JSON file, checks
schema versions, classifications, required source fields, all seven activation
states, exactly five ranked candidates, no absolute paths, and no embedded
binary/base64 payload fields. Search reports for every execution/reachability
claim and confirm it carries direct evidence or remains `UNKNOWN`.

- [ ] **Step 5: Audit Git content and staged safety**

```powershell
git diff --check
git status --short --untracked-files=all
git ls-files
git diff be5a83be9fc52493ed04070abac12531c6c6b901 --name-only
git diff --cached --name-only
```

Inspect every changed/tracked path and blob type. Expected: no JAR, class, ZIP,
ISO, update image, executable, SWF, certificate, key, token, decoded
filesystem, vendor resource, or other proprietary payload is tracked or
staged. Record: `Stock/vendor firmware staged: NO`.

- [ ] **Step 6: Verify the protected checkout is unchanged**

From `E:/Documents/GitHub/jeep_uconnect_custom`, compare branch, HEAD, and the
complete `git status --short --untracked-files=all` inventory to the recorded
pre-work snapshot. Expected: branch `codex/ra4-driver-temperature`, HEAD
`894afe8e5361c3595623de599e62ba0f0c0d9f78`, and the same unrelated dirty-file
inventory.

- [ ] **Step 7: Verify final branch history and clean worktree**

```powershell
git log --oneline --decorate be5a83be9fc52493ed04070abac12531c6c6b901..HEAD
git status --short --untracked-files=all
```

Expected: focused design, plan, analyzer, census, and report commits; empty
status in the isolated worktree.
