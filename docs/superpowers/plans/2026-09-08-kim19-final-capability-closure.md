# KIM19 Final Capability Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a deterministic, internally consistent final assessment of the useful stock-signed capabilities in recovered KIM19 and separate every remaining question that requires the physical radio.

**Architecture:** Add one small synthesis generator that consumes and hash-binds the already committed KIM19 runtime, stock-signed, target-state, Yelp, and Performance Pages evidence. Keep reviewed final classifications in a separate notes file, validate them against the source reports, and emit exactly three canonical JSON reports. Build the three final Markdown documents from the same classifications and verify report bytes, source hashes, requirements coverage, and Git isolation without rerunning broad corpus discovery.

**Tech Stack:** Python 3 standard library, `unittest`, canonical sorted ASCII JSON, existing recovered-artifact analyzers and reports, Markdown, Git.

---

### Task 1: Specify the final evidence contract with failing tests

**Files:**
- Create: `analysis_tools/tests/test_kim19_final_capability.py`
- Create: `analysis_tools/kim19_final_notes.json`

- [x] **Step 1: Add a failing canonical-output test**

Create a test that imports `REPORT_NAMES`, `build_reports`, `canonical_bytes`, `load_and_validate_notes`, and `verify_evidence_inputs` from `analysis_tools.kim19_final_capability`; asserts exactly `capability_matrix`, `handoff_graph`, and `unresolved_gates`; and asserts sorted ASCII JSON with one trailing LF.

- [x] **Step 2: Add failing semantic-contract tests**

Assert nine unique KIM19 application identities, all 19 JAR records, capability levels limited to `0..5`, highest proved KIM19 level `3`, highest conditional KIM19 level `3`, archived SocketCommandSource level `4` only in a separately scoped historical conditional, decision `B`, and the exact completion marker `STATIC RESEARCH COMPLETE`.

- [x] **Step 3: Add failing graph and observation tests**

Assert every handoff edge references a declared node and source evidence, the graph contains user/network/media/configuration/vehicle inputs and typed phone/navigation/AppManager/IXC/VSB outputs, and unresolved observations cover categories `A`, `B`, `C`, and `D` with transmission, persistence, dependency, falsification, and stop-condition fields.

- [x] **Step 4: Add failing stale-input and check-mode tests**

Use temporary fixtures to prove evidence SHA-256 mismatch, duplicate IDs, unknown labels, dangling edges, stale output, missing output, and unexpected output all fail closed.

- [x] **Step 5: Run the focused test and observe the expected RED result**

Run:

```powershell
& $Python -m unittest analysis_tools.tests.test_kim19_final_capability -v
```

Expected: import failure for the not-yet-created `analysis_tools.kim19_final_capability` module.

### Task 2: Implement the bounded deterministic synthesis generator

**Files:**
- Create: `analysis_tools/kim19_final_capability.py`
- Modify: `analysis_tools/kim19_final_notes.json`

- [x] **Step 1: Implement canonical encoding and evidence locking**

Implement `canonical_bytes()` with sorted keys, ASCII escaping, `allow_nan=False`, and LF termination. Load only declared repository-relative JSON/Markdown evidence paths, reject traversal/absolute paths, compare exact SHA-256 values, and parse JSON without executing recovered code.

- [x] **Step 2: Validate the reviewed notes schema**

Require the labels `PROVED`, `STRONGLY SUPPORTED`, `INFERRED`, `UNKNOWN`, and `TARGET OBSERVATION REQUIRED`; unique IDs; nine applications; 19 inventory JARs; valid levels; complete A-D observation metadata; known graph endpoints; and explicit scope separation between KIM19 and historical archived-package findings.

- [x] **Step 3: Cross-check existing authoritative reports**

Compare application identities, versions, entry points, descriptors, startup modes, and the 19 JAR paths/hashes against `application_activation_matrix.json` and `network_capabilities.json`. Require KIM19 part resolution, 4,572-class/19-JAR coverage, all-JAR hash verification, 23 existing service edges, Yelp phone/navigation receiver closure, and archived KIM1/KIM3/KIM12 socket-package exclusion.

- [x] **Step 4: Build exactly three reports**

Emit `capability_matrix.json` with the inventory, ladder, ranked candidates, per-app/API census, ceiling, scoped negatives, and completion decision; `handoff_graph.json` with typed cross-app taint/handoff paths; and `unresolved_gates.json` with the A-D observation matrix, unknowns, excluded actions, and recommended bounded observation.

- [x] **Step 5: Implement write and exact-byte check modes**

Write only the three declared JSON files. In `--check` mode reject stale, missing, or unexpected JSON files and print a concise verified count.

- [x] **Step 6: Run the focused test and observe GREEN**

Run:

```powershell
& $Python -m unittest analysis_tools.tests.test_kim19_final_capability -v
```

Expected: all focused tests pass with zero errors.

### Task 3: Generate and inspect the final machine-readable package

**Files:**
- Create: `reports/kim19_final/capability_matrix.json`
- Create: `reports/kim19_final/handoff_graph.json`
- Create: `reports/kim19_final/unresolved_gates.json`

- [x] **Step 1: Generate the reports**

Run:

```powershell
& $Python -m analysis_tools.kim19_final_capability --output reports/kim19_final
```

Expected: `3 reports written; evidence inputs verified`.

- [x] **Step 2: Verify exact bytes immediately**

Run the same command with `--check` and require `3 reports verified; evidence inputs verified`.

- [x] **Step 3: Inspect semantic invariants**

Confirm nine applications, 19 JARs, all required evidence labels, graph endpoint closure, A-D observation coverage, decision `B`, the KIM19 Level-3 ceiling, separately scoped historical Level-4 socket condition, and `STATIC RESEARCH COMPLETE`.

### Task 4: Write the authoritative closure documents

**Files:**
- Create: `docs/kim19_final_capability_assessment.md`
- Create: `docs/kim19_stock_capability_graph.md`
- Create: `docs/kim19_target_observation_runbook.md`

- [x] **Step 1: Write the 18-section final assessment**

Cover the executive conclusion; exact inventory; ranked table; graph; SocketCommandSource, IXC, dynamic-extension, and platform-service dispositions; per-app findings; scoped negatives; unknowns; observation matrix; proved and conditional ceilings; action; completion marker; verification; and Git checkpoint. Cite concrete committed reports and keep every inference labeled.

- [x] **Step 2: Write the stock capability graph**

Document the input-to-app-to-handoff-to-action paths, cross-application edges, receiver semantics, and why ordinary returned strings/models are not executable. Include a compact Mermaid graph plus a machine-readable report link.

- [x] **Step 3: Write the target observation runbook**

Define the smallest passive, local-only, network-transmitting, and state-changing observations. For every row include exact action, visible outcomes, proof, falsification boundary, transmission/persistence flags, dependencies, and stop condition; prohibit active socket probing, credentials, backend substitution, calls, routes, registration, media writes, uploads, and installs in the recommended first observation.

- [x] **Step 4: Cross-check Markdown against JSON**

Require matching candidate order, levels, socket/IXC/dynamic conclusions, observation IDs, decision `B`, and completion marker.

### Task 5: Complete verification and record it

**Files:**
- Create: `reports/kim19_final/verification.md`
- Modify: `docs/superpowers/plans/2026-09-08-kim19-final-capability-closure.md`

- [x] **Step 1: Run focused and full tests**

Run the final analyzer tests, existing Yelp/runtime/stock/target tests, then full `analysis_tools/tests` discovery in the documented analysis environment. Require zero failures and errors.

- [x] **Step 2: Run every applicable check-mode generator**

Check the final reports, KIM19 Yelp reports, KIM19 runtime reports, target production reports, stock-signed reports, Yelp observation report, and Performance Pages reports using their documented inputs. Record exact commands and outcomes.

- [x] **Step 3: Verify evidence and repository consistency**

Run `git diff --check`, inspect `git diff --stat` and `git status`, confirm the recovered KIM19 analyzer still reports all 19 JAR hashes unchanged, and compare the original dirty checkout's HEAD/status/diff fingerprints to the recorded baseline.

- [x] **Step 4: Record verification evidence and close plan checkboxes**

Write exact test counts, generator results, evidence hashes, isolation results, and remaining target-only boundaries to `reports/kim19_final/verification.md`; then mark every completed plan item checked.

### Task 6: Commit and push the closure checkpoint

**Files:**
- Modify: `docs/kim19_final_capability_assessment.md`
- Modify: `reports/kim19_final/verification.md`

- [x] **Step 1: Commit the implementation and generated evidence**

Stage only this plan's files and create a descriptive research commit.

- [x] **Step 2: Insert the real commit SHA without falsifying a clean checkpoint**

Use a second documentation-only commit to record the first content commit SHA as the reproducible report checkpoint; describe the final tip SHA in the final response and Git state rather than recursively embedding it.

- [x] **Step 3: Re-run final verification from the committed tree**

Run focused/full tests, final `--check`, `git diff --check`, and status checks after the documentation commit.

- [x] **Step 4: Push without opening a PR**

Push `codex/kim19-final-capability-closure` to `origin`, verify local/remote SHA equality and a clean isolated worktree, and recheck that the original dirty checkout baseline is unchanged.
