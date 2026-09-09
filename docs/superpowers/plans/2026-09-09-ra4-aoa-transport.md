# RA4 AOA Transport Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Determine the legitimate RA4 AOA execution surface, make the Phase-7 decision, and produce deterministic evidence plus only the conditionally permitted host-side or physical probe.

**Architecture:** A read-only evidence audit feeds a strict JSON evidence model and deterministic report renderer. The Phase-7 decision is recorded before any probe code exists. If the result is B or D, the only implementation is a pure-Python, host-executable AOA state machine behind a USB abstraction with a deterministic mock; it is explicitly not target code and not target verified.

**Tech Stack:** Python 3 standard library, `unittest`, existing RA4 ELF/SWF analysis tools, canonical JSON, Git, official Google Android Open Accessory and QNX 6.5 documentation.

---

### Task 1: Freeze the authorized starting state

**Files:**
- Verify: `docs/superpowers/specs/2026-09-09-ra4-aoa-transport-design.md`
- Verify: recovered corpus under the read-only checkout alias `RA4_CORPUS`

- [ ] **Step 1: Confirm the branch and exact design commit**

Run:

```powershell
git branch --show-current
git rev-parse HEAD
git status --porcelain
```

Expected: branch `codex/ra4-aoa-transport`, HEAD
`f503292f35660b632fb92ebb6569db9e564d551f`, and no worktree changes.

- [ ] **Step 2: Recompute the original dirty-checkout fingerprint**

Run the same read-only status, staged-diff, unstaged-diff, and untracked-file
hash commands used before branch creation. Keep the result outside tracked
files for comparison during Task 10.

- [ ] **Step 3: Run the clean baseline test suite**

Run:

```powershell
python -m unittest discover -s analysis_tools/tests -v
```

Expected: 311 tests pass before new tests are added.

### Task 2: Reconstruct the exact AOA contract from primary sources

**Files:**
- Create: `analysis_tools/ra4_aoa_notes.json`
- Later generate: `reports/ra4_aoa/aoa_state_machine.json`

- [ ] **Step 1: Read the official Google AOA protocol documentation**

Record the authoritative URL, access date, AOA protocol versions, accessory
VID/PIDs, request IDs, string IDs, required strings, and re-enumeration rules.
Do not use Android Auto protocol documentation to fill any AOA field.

- [ ] **Step 2: Record the control-transfer sequence**

Create the initial `aoa_sequence` records in `analysis_tools/ra4_aoa_notes.json`
with these fields for every operation:

```json
{
  "state": "GET_PROTOCOL",
  "bmRequestType": 192,
  "bRequest": 51,
  "wValue": 0,
  "wIndex": 0,
  "payload_hex": "",
  "expected_response": "two-byte little-endian protocol version",
  "timeout_ms": 1000,
  "failure": "abort and release the device"
}
```

Add the six ordered `SEND_STRING` operations, `START_ACCESSORY`, detach,
re-enumeration, endpoint selection, bounded bulk exchange, release, and clean
reconnect. Use a fixed 1,000 ms control timeout and a bounded 5,000 ms
detach/re-enumeration timeout in the host model; describe these as test-plan
values rather than RA4 production defaults.

- [ ] **Step 3: Self-check the protocol ledger**

Confirm that request types, request numbers, string indices, NUL termination,
Google VID/PID allowlist, and version handling agree with the Google source.
Confirm that no Android Auto handshake or projection message appears.

### Task 3: Audit every legitimate stock execution surface

**Files:**
- Modify: `analysis_tools/ra4_aoa_notes.json`
- Later generate: `docs/ra4_usb_execution_surface.md`
- Later generate: `reports/ra4_aoa/execution_surface.json`

- [ ] **Step 1: Establish the bounded recovered roots**

Use the same seven roots and aliases as the feasibility census. Read them from
the original checkout without modifying them. Record file counts, root labels,
and the exact limitation that ignored/unmaterialized installed content is not
covered.

- [ ] **Step 2: Re-run existing USB and runtime inventories**

Run the existing `qnx_usb_inventory.py`, `qnx_media_runtime_probe.py`,
`target_production_index.py`, ELF import resolver, and targeted text searches
against `enum-usb`, `connmgr`, `iofs-usb-ipod.so`, MTP/MTPZ rules, media
services, diagnostics, helper binaries, JNI wrappers, service definitions, and
resident applications. Store scratch output outside tracked deliverables.

- [ ] **Step 3: Inspect concrete callers and activation routes**

For each candidate, recover:

```text
artifact -> startup/config activation -> caller-controlled input (if any)
         -> USB functions actually imported/called -> ownership/permissions
         -> primary disposition
```

Classify each candidate exactly as `PRODUCTION CALLABLE`,
`PRODUCTION INTERNAL`, `TEST/DIAGNOSTIC`, `UNREACHABLE`,
`REQUIRES NEW CODE`, or `UNKNOWN`. An import or exported library function alone
may never produce `PRODUCTION CALLABLE`.

- [ ] **Step 4: Hash every newly cited recovered artifact**

Record relative corpus path, byte size, SHA-256, and a bounded locator. Include
at least `libusbdi.so.2`, `enum-usb`, `connmgr`, `iofs-usb-ipod.so`,
`devb-umass`, `devc-serusb`, the MTP enum rule, `enum-usb.conf`, `boot.sh`, and
any service/JNI artifact used in a material conclusion.

- [ ] **Step 5: Answer the execution question before continuing**

State whether already-authorized software exposes a concrete route for vendor
control, descriptor/configuration/interface operations, bulk IN/OUT, reset,
detach, and re-enumeration. List missing operations and distinguish internal
capability from callable authority.

### Task 4: Trace hub transparency, USB ownership, and projection insertion point

**Files:**
- Modify: `analysis_tools/ra4_aoa_notes.json`
- Later generate: `docs/ra4_android_usb_ownership.md`
- Later generate: `docs/ra4_phone_projection_service.md`

- [ ] **Step 1: Assess the cabin media hub**

Correlate the existing part/topology evidence, recovered USB host behavior, hub
monitoring, and public USB hub behavior. For each of vendor control, detach,
re-enumeration, Google VID/PID visibility, descriptors, and bulk transfers,
record the evidence and limitation. Select exactly one hub classification from
the design vocabulary.

- [ ] **Step 2: Reconstruct Android insertion ownership**

Trace:

```text
physical attach -> io-usb/HCD -> enum-usb rules -> MTP/MTPZ match
                -> media/connmgr launch or notification -> interface claim
                -> disconnect/retry/release
```

Recover the generic/unknown-device behavior and `trackUnhandledUsbDevice`
setting. Separate rule matching from proved runtime launch and proved interface
claiming.

- [ ] **Step 3: Identify the narrowest AOA interception point**

State whether AOA must run before MTP ownership, can issue control requests
before the MTP interface claim, or requires release/reclassification. Do not
implement the production ownership change.

- [ ] **Step 4: Recover the USB-relevant dormant projection contract**

Use the hash-identified HMI and gateway evidence to record destinations,
`startProjection(ppId)`, service-owner subscriptions, device events,
projection enums/status, and gateway rejection. Search the bounded corpus for
a matching owner and for shared/newer Harman provenance. Do not broaden into a
general feature census.

### Task 5: Make and freeze the Phase-7 decision

**Files:**
- Modify: `analysis_tools/ra4_aoa_notes.json`

- [ ] **Step 1: Reconcile the A/B/C/D definitions against evidence**

Complete a decision table with required facts, supporting sources, missing
facts, and disqualifiers for each classification.

- [ ] **Step 2: Select exactly one classification**

Write `phase7.classification` and an exact blocker or mechanism. If the result
is C, define the external/existing mechanism completely and explicitly forbid
new target code. If no authorized component can originate AOA, passive USB
instrumentation cannot justify C.

- [ ] **Step 3: Freeze one next engineering objective**

Choose exactly one of: recover/activate the legitimate dormant owner,
establish a legitimate native development environment on a spare radio, or an
alternative route supported by concrete evidence. This choice is made before
prototype implementation.

### Task 6: Build the evidence model and deterministic renderer with TDD

**Files:**
- Create: `analysis_tools/tests/test_ra4_aoa_transport.py`
- Create: `analysis_tools/ra4_aoa_transport.py`
- Modify: `analysis_tools/ra4_aoa_notes.json`

- [ ] **Step 1: Write failing validation and rendering tests**

Tests must assert:

```python
self.assertEqual(set(outputs), set(REQUIRED_OUTPUTS))
self.assertEqual(canonical_json(model), canonical_json(model))
with self.assertRaisesRegex(ModelError, "execution authority"):
    validate_notes(promote_symbol_presence_to_callable(model))
with self.assertRaisesRegex(ModelError, "Phase-7"):
    validate_notes(model_without_single_phase7_decision())
with self.assertRaisesRegex(ModelError, "Android Auto protocol"):
    validate_notes(model_with_forbidden_projection_scope())
```

Also reject absolute source paths, unknown classifications, dangling source
IDs, invalid AOA request constants, unordered string indices, invalid
accessory VID/PIDs, missing success criteria, more than one next objective, and
target code when Phase 7 is B or D.

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```powershell
python -m unittest analysis_tools.tests.test_ra4_aoa_transport -v
```

Expected: import failure because `analysis_tools.ra4_aoa_transport` does not
exist.

- [ ] **Step 3: Implement the minimum validator and renderer**

Create `analysis_tools/ra4_aoa_transport.py` with:

```python
REQUIRED_OUTPUTS = (
    "docs/ra4_aoa_transport.md",
    "docs/ra4_usb_execution_surface.md",
    "docs/ra4_android_usb_ownership.md",
    "docs/ra4_phone_projection_service.md",
    "docs/ra4_aoa_test_plan.md",
    "reports/ra4_aoa/aoa_state_machine.json",
    "reports/ra4_aoa/usb_operation_mapping.json",
    "reports/ra4_aoa/execution_surface.json",
    "reports/ra4_aoa/verification.md",
)

class ModelError(ValueError):
    pass

def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=True, indent=2,
                       sort_keys=True) + "\n").encode("utf-8")
```

Add strict `load_notes`, `validate_notes`, `render_outputs`, `write_outputs`,
`check_outputs`, and CLI `--check` behavior following
`wired_projection_feasibility.py`. The renderer emits only evidence present in
the validated notes.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run the focused unittest command until all renderer/model tests pass.

- [ ] **Step 5: Render the required documents and reports**

Run:

```powershell
python analysis_tools/ra4_aoa_transport.py
python analysis_tools/ra4_aoa_transport.py --check
```

Expected: exactly the nine required outputs are current.

### Task 7: Conditionally implement only the permitted probe model with TDD

**Files if Phase 7 is B or D:**
- Create: `prototype/ra4_aoa_probe/README.md`
- Create: `prototype/ra4_aoa_probe/aoa_transport.py`
- Create: `prototype/ra4_aoa_probe/mock_usb.py`
- Create: `prototype/ra4_aoa_probe/tests/test_aoa_transport.py`

**Files if Phase 7 is A or C:**
- Create only the minimum files justified by the concrete proved mechanism;
  revise this task before implementation if their paths or runtime cannot be
  named from evidence.

- [ ] **Step 1: Apply the Phase-7 branch**

For B or D, place this exact warning at the start of the README:

```text
NOT TARGET VERIFIED. This is a host-executable protocol model. It is not an
RA4 binary, has no target authorization route, and proves neither cabin-hub
transport nor physical AOA operation.
```

For C, do not create target-side code. Remain inside the exact external/existing
mechanism that justified C.

- [ ] **Step 2: Write the first failing state-machine tests**

Define a wished-for API:

```python
result = AoaSession(mock_usb, identity).run()
self.assertEqual(result.protocol_version, 2)
self.assertEqual(mock_usb.string_indices, [0, 1, 2, 3, 4, 5])
self.assertEqual(result.response_payload, b"RA4-AOA-PONG")
```

Add separate tests for protocol query failure, unsupported version, control
failure, string ordering, start failure, detach timeout, wrong VID/PID, missing
bulk endpoints, partial write, partial read, mid-transfer disconnect, clean
reconnect, ownership conflict, and deterministic bidirectional framing.

- [ ] **Step 3: Run tests and verify RED**

Run:

```powershell
python -m unittest discover -s prototype/ra4_aoa_probe/tests -v
```

Expected: import failure because the implementation does not exist.

- [ ] **Step 4: Implement the minimum host abstraction and state machine**

Use a typed `UsbHost` protocol with control IN/OUT, detach/re-enumeration,
configuration/interface claim, bulk read/write, release, and reset operations.
Use immutable device/endpoint records and an explicit state enum. Reject
partial transfers, frames larger than 256 bytes, unexpected state transitions,
wrong VID/PID, and ambiguous device selection. Always release a claimed
interface in `finally`; preserve the primary transfer error if cleanup also
fails.

- [ ] **Step 5: Implement the deterministic mock and framing**

The mock records every operation and returns scripted results. Use a bounded
frame containing a fixed magic, version, sequence, payload length, payload, and
CRC32. The default request/response payloads are `RA4-AOA-PING` and
`RA4-AOA-PONG`; no Android Auto content is permitted.

- [ ] **Step 6: Run tests and verify GREEN**

Run the prototype suite and the focused evidence-model suite. Refactor only
after both are green.

### Task 8: Complete the evidence deliverables

**Files:**
- Generate all nine required deliverables from Task 6
- Modify: `analysis_tools/ra4_aoa_notes.json`

- [ ] **Step 1: Fill the AOA-to-RA4 operation matrix**

For device detection, descriptor reads, `GET_PROTOCOL`, every string,
`START_ACCESSORY`, detach/re-enumeration, configuration/interface selection,
bulk IN/OUT, reset, release, and reconnect, record RA4 API, concrete
implementation, production use, new-code requirement, permissions/ownership,
and remaining unknown.

- [ ] **Step 2: Reconcile physical success criteria**

Record separate booleans and evidence for physical cabin enumeration,
`GET_PROTOCOL`, `START_ACCESSORY`, accessory re-enumeration, Google VID/PID,
bulk endpoint claim, host transmit, phone transmit, bidirectional deterministic
frames, and clean detach/reconnect. Static compatibility leaves these false.

- [ ] **Step 3: Populate the verification report facts**

Record test commands/counts, generator checks, JSON parsing, diff check,
artifact hash verification, original-checkout fingerprint result, branch, and
the fact that no target execution or vehicle modification occurred.

- [ ] **Step 4: Generate twice**

Run the renderer, snapshot `git diff`, run it again, and confirm the second run
introduces no change. Then run `--check`.

### Task 9: Verify the entire repository and evidence boundary

**Files:**
- Verify: all changed files
- Verify: all cited recovered artifacts
- Verify: original dirty checkout

- [ ] **Step 1: Run all Python tests**

Run:

```powershell
python -m unittest discover -s analysis_tools/tests -v
python -m unittest discover -s prototype/ra4_aoa_probe/tests -v
```

Expected: all tests pass. Skip the second command only if Phase 7 is A or C and
no host model was permitted.

- [ ] **Step 2: Run every other existing repository test surface**

Run the Node resident-HMI suite and compile/run the C projection-arbiter test
when their runtimes/compilers are available. Report an unavailable tool as a
verification limitation rather than success.

- [ ] **Step 3: Verify generated artifacts and JSON**

Run `ra4_aoa_transport.py --check` twice and parse every JSON file beneath
`reports/ra4_aoa` with Python's JSON parser.

- [ ] **Step 4: Verify recovered hashes and original checkout**

Rehash every raw artifact cited in the notes. Recompute the original checkout
fingerprint and compare it byte-for-byte with Task 1.

- [ ] **Step 5: Run final Git checks**

Run:

```powershell
git diff --check
git status --short
git diff --stat f503292f35660b632fb92ebb6569db9e564d551f..HEAD
```

Review the complete diff for evidence promotion, forbidden scope, absolute
paths, secrets, and accidental recovered-artifact changes.

### Task 10: Commit and push without a pull request

**Files:**
- Commit: all approved plan, analysis, tests, prototype, docs, and reports

- [ ] **Step 1: Commit the implementation plan**

Commit this file independently with:

```powershell
git add docs/superpowers/plans/2026-09-09-ra4-aoa-transport.md
git commit -m "docs: plan RA4 AOA transport evidence phase"
```

- [ ] **Step 2: Commit the verified evidence implementation**

After Tasks 1-9 pass, stage only the intended files and commit with:

```powershell
git commit -m "research: resolve RA4 AOA transport execution gate"
```

- [ ] **Step 3: Push the branch**

Run:

```powershell
git push origin codex/ra4-aoa-transport
git ls-remote --heads origin refs/heads/codex/ra4-aoa-transport
```

Expected: remote SHA equals the local final commit. Do not create a pull
request.
