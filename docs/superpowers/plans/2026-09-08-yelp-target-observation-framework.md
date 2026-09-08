# Yelp Target Observation Framework Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic, evidence-backed framework that maps one ordinary Yelp target observation to defensible hypotheses and the next benign step.

**Architecture:** Keep the existing KIM19 generator and eight reports byte-identical. Add a separate reviewed Yelp model and deterministic ninth-report generator for gates, failure signatures, observation cases, and native predicates. Keep recovered evidence extraction separate from interpretation. Add a standalone JSON-in/JSON-out observation analyzer that performs no network or target operations.

**Tech Stack:** Python 3 standard library, existing Java class parser and ARM ELF analyzer, JSON, Markdown, unittest, JDK `javap` for independent bytecode verification.

---

### Task 1: Preserve and plan the isolated checkpoint

**Files:**
- Create: `docs/superpowers/plans/2026-09-08-yelp-target-observation-framework.md`

- [x] **Step 1: Verify the isolated branch and checkpoint**

Run `git status --short`, `git rev-parse HEAD`, and `git branch --show-current` in the isolated checkout. Expected: clean branch `codex/stock-signed-capability-analysis` at `22b85f5b9721d3a107529f05fff125b0147b1334`.

- [x] **Step 2: Preserve the original checkout boundary**

Use read-only Git commands with optional locks disabled and compare its HEAD/status/diff hashes with the existing verification snapshot. Do not stage, modify, restore, stash, clean, or switch it.

### Task 2: Characterize the targeted native virtual-catalog predicates

**Files:**
- Create: `analysis_tools/yelp_observation_model.json`
- Create: `analysis_tools/tests/test_yelp_observation_analysis.py`
- Create: `docs/native_virtual_catalog_predicates.md`

- [x] **Step 1: Trace the exact native window and dependencies**

Disassemble only the catalog region around `0x12592c-0x125970`, its immediately required callees, argument definitions, and consumers. Resolve imports, literals, callers, and application-object offsets. Record neutral identifiers whenever semantics are not justified.

- [x] **Step 2: Write failing deterministic extraction tests**

Add tests that require each predicate record to bind its address, call target, arguments, consumer branch, affected scope, evidence label, and source window. Verify the tests fail before generator changes.

- [x] **Step 3: Generate bounded native predicate evidence**

Add reviewed windows/records to the existing notes and generator. Do not create a broad native sweep. Re-run the focused tests and require them to pass.

- [x] **Step 4: Document implications for absent, hidden, and disabled Yelp states**

Write `docs/native_virtual_catalog_predicates.md` with addresses, recovered logic, callers, inputs, consumers, neutral roles, evidence strength, and affected applications.

### Task 3: Build the Yelp launch-gate and network contracts

**Files:**
- Create: `analysis_tools/yelp_observation_model.json`
- Create: `docs/yelp_launch_gate_model.md`
- Create: `docs/yelp_network_contract.md`

- [x] **Step 1: Trace launch gates and failure exits**

Follow the exact KIM19 identity through descriptor, registration/catalog, native launch/authorization, AMS association, Xlet init/start, scheduled splash/home, platform services, connectivity, request, response, and error UI. Search for locale, region, vehicle, version, account, subscriber, VSB, DRM, IXC, super-app, automatic exit, and error-screen evidence without treating absent references as live gates.

- [x] **Step 2: Trace the request contract**

Recover endpoint/property provenance, method/path/query construction, headers, omitted sensitive credentials, TLS/client selection, platform connectivity calls, timeout/retry behavior, response schema/status mapping, and error collapse. Classify every external value by source category.

- [x] **Step 3: Write the two focused documents**

Document only gates supported by recovered evidence. Use a Mermaid gate sequence and explicit PROVED, INFERRED, UNKNOWN, and TARGET OBSERVATION REQUIRED sections.

### Task 4: Generate Yelp failure signatures

**Files:**
- Create: `analysis_tools/yelp_observation_analysis.py`
- Create: `analysis_tools/yelp_observation_model.json`
- Create: `analysis_tools/tests/test_yelp_observation_analysis.py`
- Create: `reports/kim19_runtime_analysis/yelp_failure_signatures.json`

- [x] **Step 1: Extract user-visible resource strings and transitions**

Identify exact resource IDs and resolved packaged values where available, their caller/method/BCI, triggering result or exception, next transition, visibility/return behavior, and retry controls. Keep UNKNOWN fields explicit rather than guessing UI lifecycle.

- [x] **Step 2: Write failing schema and provenance tests**

Require unique signature IDs, normalized match strings, exact labels, source hashes or generated-method evidence, and deterministic ordering. Verify failure before implementation.

- [x] **Step 3: Generate and independently inspect the report**

Extend the generator to emit the ninth report, validate selected calls with `javap`, then run write/check passes and compare bytes.

### Task 5: Implement the observation analyzer test-first

**Files:**
- Create: `tools/analyze_yelp_observation.py`
- Create: `analysis_tools/tests/test_yelp_observation_analysis.py`
- Create: `docs/yelp_target_observation_analysis.md`

- [x] **Step 1: Write failing classification tests**

Cover A absent, B disabled, C immediate exit, D exact error, E registration prompt, F normal home, G explicitly reported full functionality, H unmatched/contradictory state, deterministic output, invalid schema, partial observations, case-insensitive failure matching, and the rule that unobserved search/speech/backend behavior is never inferred.

- [x] **Step 2: Implement strict JSON input validation**

Accept only documented fields and JSON scalar types, distinguish omitted from false, reject contradictory combinations, and perform no networking or external execution.

- [x] **Step 3: Implement deterministic hypothesis mapping**

Load committed gate/failure data, classify A-H, match normalized screen/error text, and emit compatible/incompatible hypotheses, established facts, remaining unknowns, one next static question, and one benign observation.

- [x] **Step 4: Run focused tests through red-green-refactor**

Run each new test before implementation to observe the expected failure, then after implementation to observe success. Refactor only while green.

- [x] **Step 5: Document outcomes A-H**

Create `docs/yelp_target_observation_analysis.md` with what each outcome proves, supports, cannot establish, relevant gates/evidence, next static question, and safest ordinary observation.

### Task 6: Integrate reports and documentation

**Files:**
- Modify: `analysis_tools/README.md`
- Modify: `reports/kim19_runtime_analysis/verification.md`
- Modify focused existing Yelp documents only if new evidence corrects or sharpens them.

- [x] **Step 1: Record the new CLI and report contracts**

Add exact invocation examples, input schema, output meaning, deterministic-generation behavior, and the non-network/non-target scope.

- [x] **Step 2: Preserve or explicitly correct prior outputs**

Hash the eight existing JSON reports before changes. Confirm unchanged bytes unless new evidence requires a correction; if changed, document the prior conclusion, corrected conclusion, and exact evidence.

- [x] **Step 3: Validate document links and evidence labels**

Require every local Markdown target to exist and every substantive conclusion to use one of the four evidence labels.

### Task 7: Full verification and focused commit

**Files:**
- Modify: `reports/kim19_runtime_analysis/verification.md`

- [x] **Step 1: Run all relevant tests**

Run the complete existing KIM19/production/native suite plus `test_analyze_yelp_observation`. Expected: zero failures/errors.

- [x] **Step 2: Verify deterministic regeneration**

Run the report generator once in write mode and twice in check mode with the same JDK. Run representative analyzer inputs twice and compare canonical output bytes.

- [x] **Step 3: Verify repository and original-checkout safety**

Run link validation, `git diff --check`, intended-file review, clean-after-commit status, original HEAD/status/diff hash comparison, and remote-head verification.

- [ ] **Step 4: Commit and push**

Create focused commits for evidence/report generation and the observation analyzer if the change naturally separates; otherwise use one cohesive commit. Push `codex/stock-signed-capability-analysis` and report the final full SHA.
