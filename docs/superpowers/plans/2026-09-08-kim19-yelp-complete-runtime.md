# KIM19 Yelp Complete Runtime Reconstruction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconstruct the stock KIM19 Yelp launch, pre-backend UI, touch/voice input, network, response, persistence, failure, and stock-handoff paths as completely as the recovered artifacts allow.

**Architecture:** Add one Yelp-specific, hash-bound analyzer that reads the recovered Yelp package without loading vendor classes or contacting any endpoint. Keep reviewed interpretations in a small canonical JSON model; bind each significant Java claim to class/method/descriptor/BCI/callee or a hashed resource, reuse committed launch evidence for HMI/AppManager/AMS edges, and generate seven focused JSON reports plus the required Markdown documents. Every unresolved runtime edge retains an explicit `UNKNOWN` or `TARGET OBSERVATION REQUIRED` label.

**Tech Stack:** Python 3.11+, existing `analysis_tools.java_classfile`, ZIP/JAR and JSON standard libraries, JDK 8 `javap`, unittest, Markdown, Git.

---

### Task 1: Preserve the isolated evidence checkpoint

**Files:**
- Create: `reports/kim19_yelp/original_checkout_snapshot.json`
- Create: `analysis_tools/kim19_yelp_notes.json`

- [ ] **Step 1: Record the immutable source boundary**

Record the original checkout branch `codex/ra4-driver-temperature`, HEAD `894afe8e5361c3595623de599e62ba0f0c0d9f78`, unstaged diff SHA-256 `d640dce2da93cbd40692549754f74ee796b897b00d5a38060d4ad17172cdc792`, empty staged-diff SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, and untracked `docs/00_project_status.md` Git blob `0aae8d1167e29865adef9e7250e9f352164a10af`. Include the complete sorted dirty-path list but no file contents.

- [ ] **Step 2: Seed the reviewed source model**

Create a canonical JSON model with the Yelp app ID, exact JAR/descriptor paths and hashes, allowed evidence labels, report names, existing committed launch-source references, and empty evidence sections represented as real empty arrays rather than absent keys.

- [ ] **Step 3: Verify the isolated branch**

Run `git status --short --branch`, `git branch --show-current`, and `git rev-parse HEAD`. Expected: only the plan and new Yelp work are dirty on `codex/kim19-yelp-reconstruction`, based on `371c4fa44228b642ddbc7574fb09df5adb067bb7`.

### Task 2: Build the deterministic Yelp report generator test-first

**Files:**
- Create: `analysis_tools/tests/test_kim19_yelp_analysis.py`
- Create: `analysis_tools/kim19_yelp_analysis.py`
- Modify: `analysis_tools/README.md`

- [ ] **Step 1: Write failing schema and evidence-binding tests**

Add tests equivalent to:

```python
def test_reports_require_exact_labels_and_bound_java_sites(self):
    model = minimal_model()
    reports = build_reports(model, fixture_jar())
    self.assertEqual(set(reports), set(REPORT_NAMES))
    self.assertEqual(reports["launch_graph"]["edges"][0]["evidence"][0]["bci"], 7)

def test_check_mode_rejects_stale_output(self):
    with self.assertRaisesRegex(ValueError, "stale report"):
        verify_outputs({"launch_graph": {"format": "wrong"}}, output_dir)
```

Cover unknown labels, duplicate IDs, missing nodes, mismatched class/method/descriptor/BCI/callee, unbound resource values, unsafe recovered paths, accidental credential emission, nondeterministic ordering, stale outputs, and source mutation.

- [ ] **Step 2: Run the focused tests and observe the expected import failure**

Run `python -m unittest analysis_tools.tests.test_kim19_yelp_analysis -v`. Expected: failure because `analysis_tools.kim19_yelp_analysis` does not exist.

- [ ] **Step 3: Implement strict source loading and Java-site validation**

Implement focused APIs with these contracts:

```python
REPORT_NAMES = (
    "launch_graph", "runtime_gates", "input_dataflow", "network_fields",
    "response_actions", "failure_paths", "stock_handoffs",
)

def load_sources(work: Path, notes: dict) -> SourceSet:
    """Open only declared regular files, verify size/hash, and reject mutation."""

def validate_java_site(site: dict, classes: dict[str, JavaClass]) -> dict:
    """Bind one reviewed claim to an exact method instruction and optional callee."""

def build_reports(notes: dict, sources: SourceSet) -> dict[str, dict]:
    """Return canonical, source-bound reports without solving runtime reachability."""
```

Use the existing class parser; never load a vendor class. Redact sensitive field values while preserving their type, source field, hash, and destination header.

- [ ] **Step 4: Implement deterministic write/check behavior**

Support `--work`, `--output`, `--javap`, and `--check`. Write canonical sorted JSON with LF endings; in check mode compare exact bytes and fail on missing, extra, or stale reports. Hash sources before and after generation.

- [ ] **Step 5: Run focused tests to green and commit the generator skeleton**

Run `python -m unittest analysis_tools.tests.test_kim19_yelp_analysis -v`, then commit the test-first generator foundation with `git commit -m "analysis: add deterministic KIM19 Yelp report model"`.

### Task 3: Reconstruct launch and pre-backend reachability

**Files:**
- Modify: `analysis_tools/kim19_yelp_notes.json`
- Create: `reports/kim19_yelp/launch_graph.json`
- Create: `reports/kim19_yelp/runtime_gates.json`
- Create: `docs/kim19_yelp_launch_graph.md`
- Create: `docs/kim19_yelp_runtime_gates.md`

- [ ] **Step 1: Bind registration and Apps-menu launch edges**

Reuse the exact Yelp descriptor identity, native catalog predicates, HMI `startXlet` selection call, DRM-enabled `findAndStartApp`, AMS association, and Xlet entry class evidence already committed. Preserve sender/receiver distinctions and mark current target registration, grants, and current binary identity as `TARGET OBSERVATION REQUIRED`.

- [ ] **Step 2: Bind every Yelp lifecycle and initialization branch**

Trace `YelpPOIXlet.initXlet`, `startXlet`, the serial runnable, splash worker/callback, `pauseXlet`, and `destroyXlet`, including registry, container, Display, property, platform, theme/resource, screen-manager, RMS/location/VR setup, exception handlers, and first selected screen. Add every branch that can prevent the main UI from appearing.

- [ ] **Step 3: Generate the launch and gate reports**

Run the generator in write mode, then twice with `--check`. Require byte-identical output and unchanged recovered-source hashes.

- [ ] **Step 4: Write the explicit launch graph and runtime-gate table**

Document nodes and branches in launch order, with JAR/class/method/descriptor/BCI/caller/callee or resource anchors. State the earliest useful local UI and the exact unresolved edge for each target-dependent gate.

### Task 4: Reconstruct touchscreen, voice, persistence, and network dataflow

**Files:**
- Modify: `analysis_tools/kim19_yelp_notes.json`
- Create: `reports/kim19_yelp/input_dataflow.json`
- Create: `reports/kim19_yelp/network_fields.json`
- Create: `docs/kim19_yelp_input_dataflow.md`
- Create: `docs/kim19_yelp_network_contract.md`

- [ ] **Step 1: Trace the complete touchscreen path**

Follow home/category/edit-search actions through `GpCVPKeyboard`, text-input widgets, field validation, tokenization/normalization, request model creation, queueing, URL selection, and transport. Record maximum lengths, accepted-character evidence, space/token behavior, category constants, location/address/coordinate selection, encoding behavior, and every value that remains uncontrolled or unresolved.

- [ ] **Step 2: Trace the complete voice path**

Follow the visible voice action through location validation, `VRHelperImp` service discovery/session registration, queue/state transitions, recognized-string callback, cancel comparison, UI-thread scheduling, `SpeechListener`, and the shared request path. Keep local feature enablement separate from actual target service availability and recognition success.

- [ ] **Step 3: Trace local storage and reusable platform services**

Reconstruct `GpRecordStoreManager` store names, serialized types, history/favorite mutation and load paths, size/count bounds, and failure handling. Identify location, phone, navigation, VR, AppManager, IXC, VSB, SDP, browser/WebView, and media references; include scoped negative results only after complete targeted class/reference coverage.

- [ ] **Step 4: Recover the request contract field by field**

Trace `GpSearchRequest`, `YelpGeocodeRequest`, `GpBaseRequest`, common `BaseRequest`, connectivity setup, Apache client/request classes, HTTPS URLs, fixed paths, query parameters, headers, credential categories, locale/location/device fields, status handling, retries/timeouts, DNS/TLS boundaries, and response stream parsing. Classify every field as application-, user-, platform-, or server-controlled.

- [ ] **Step 5: Generate and document both dataflows**

Run focused tests, write/check the two reports, and document separate touchscreen and voice graphs. Explicitly state whether arbitrary ordinary text survives to the HTTP request and whether any local interpreter/parser/renderer consumes it first.

### Task 5: Reconstruct response actions, failures, and stock handoffs

**Files:**
- Modify: `analysis_tools/kim19_yelp_notes.json`
- Create: `reports/kim19_yelp/response_actions.json`
- Create: `reports/kim19_yelp/failure_paths.json`
- Create: `reports/kim19_yelp/stock_handoffs.json`
- Create: `docs/kim19_yelp_response_actions.md`
- Create: `docs/kim19_yelp_failure_states.md`
- Create: `docs/kim19_yelp_stock_handoffs.md`

- [ ] **Step 1: Trace every significant response field to a sink**

Bind top-level status/error and every parsed business/location field to display models, image handling, phone/address/coordinate consumers, navigation destinations, local storage, and external service calls. Reject HTML/WebView or executable-content claims unless a concrete parser/renderer edge exists.

- [ ] **Step 2: Close both ends of phone and navigation handoffs**

Identify the sender object/call, platform interface, argument types/field mapping, receiver or platform service contract present in recovered stock artifacts, and caller-visible result/failure branch. Mark a sender-only edge incomplete instead of promoting it to a proved end-to-end handoff.

- [ ] **Step 3: Enumerate failures by layer**

Separate no network, connectivity status failure, DNS/connection/TLS/HTTP ambiguity, null response, malformed JSON, response error, timeout/retry boundary, registration/subscription/authentication observations, missing GPS, missing VR, missing phone/navigation, persistence errors, and generic exceptions. Record whether the Yelp screen remains reachable, is replaced, or has an unknown post-dialog state.

- [ ] **Step 4: Compare concretely with SocketCommandSource**

Compare only actual shared libraries, configuration sources, launch mechanisms, IXC types, permissions, and transports. Preserve the existing negative result that the Yelp JAR contains no `SocketCommandSource`/`CommandLooper` and do not restart a broad socket search.

- [ ] **Step 5: Generate, check, and document the three reports**

Run focused tests plus deterministic write/check passes. Write source-backed response, failure, and handoff documents with explicit receiver limits and contradiction preservation.

### Task 6: Build the target decision tree and update the capability assessment

**Files:**
- Create: `docs/kim19_yelp_target_observation.md`
- Modify: `docs/kim19_capability_assessment.md`
- Modify: `analysis_tools/README.md`
- Modify: `reports/kim19_runtime_analysis/verification.md`

- [ ] **Step 1: Write the exact no-modification observation protocol**

Start with Apps visibility, one Yelp tap, and first/subsequent no-credential screen capture. Cover absent, disabled, immediate return, splash/loading, registration/subscription, service/network error, search/category UI, dialog, blank UI, crash/restart, and another-app launch. For each branch state exactly which launch/gate hypotheses it proves, falsifies, supports, or leaves unresolved.

- [ ] **Step 2: Update the ranked assessment and corrections**

Replace the earlier Yelp summary with the complete launch/pre-backend/input/network/response/handoff result. Keep Performance Pages fixed at its established Level-2 conclusion and rank the next action using the remaining target uncertainty.

- [ ] **Step 3: Document reproducibility and safety**

Add exact generator/test commands, dependency versions, source hashes, sensitive-value redaction rules, and the no-network/no-target-operation boundary to the README and verification record.

### Task 7: Verify, review, commit, and push

**Files:**
- Modify: all files listed in Tasks 1-6 only

- [ ] **Step 1: Run focused and complete tests**

Run `python -m unittest analysis_tools.tests.test_kim19_yelp_analysis -v` and `python -m unittest discover -s analysis_tools/tests -v` using the documented analysis venv. Require zero failures and errors.

- [ ] **Step 2: Verify deterministic regeneration**

Run one write pass and two `--check` passes. Hash the seven outputs after each pass and require identical SHA-256 values. Independently inspect the selected method blocks with JDK 8 `javap -s -c -p`.

- [ ] **Step 3: Review evidence discipline and repository scope**

Run a label/schema audit, Markdown-link check, `git diff --check`, `git status --short`, intended-file diff review, credential-pattern scan, and source-artifact scan. Recompute the original checkout HEAD/status/diff/untracked hashes and require the recorded HEAD, diff, staged diff, and untracked blob hashes to remain unchanged.

- [ ] **Step 4: Commit and push the completed research**

Commit the evidence/reports/docs with `git commit -m "research: reconstruct KIM19 Yelp runtime and handoffs"`, push `codex/kim19-yelp-reconstruction`, and record the local and remote full SHA. If push is unavailable, report the exact local SHA and remote error without claiming a pushed state.
