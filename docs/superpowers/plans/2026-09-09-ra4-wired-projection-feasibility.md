# RA4 Wired Projection Feasibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a deterministic, evidence-bound feasibility closure for native wired Android Auto and Apple CarPlay on the RA4 without implementing a projection client or modifying a radio or vehicle.

**Architecture:** Treat the committed KIM19 closure as the authoritative baseline, synthesize its USB, graphics, audio, input, HMI, and resource evidence into a structured note model, and generate the requested Markdown and JSON package from one fail-closed renderer. Keep public evidence in a separately identified source ledger and use it only for later FCA/Harman comparison and protocol/authentication boundaries.

**Tech Stack:** Python 3.14 standard library, `unittest`, canonical JSON, Markdown, Git worktrees.

---

### Task 1: Evidence and source closure

**Files:**
- Create: `analysis_tools/wired_projection_notes.json`
- Reference: `docs/11_projection_engine_feasibility.md`
- Reference: `docs/12_ra4_projection_hardware_feasibility.md`
- Reference: `docs/14_qnx6_audio_arbitration_reference.md`
- Reference: `docs/15_qnx6_screen_touch_camera_reference.md`
- Reference: `docs/17_qnx6_carplay_transport_reference.md`
- Reference: `docs/18_omap3730_usb_role_feasibility.md`
- Reference: `docs/19_ra4_media_hub_usb_path.md`
- Reference: `docs/20_projection_transport_gate_matrix.md`
- Reference: `reports/android_auto_reference_contract.md`
- Reference: `reports/ra4_post_reboot_checkpoint.md`
- Reference: `reports/ra4_usb_stack_backend_census.md`

- [x] **Step 1: Extract repository evidence**

Record each positive claim with a repository-relative artifact, SHA-256, symbol/class/function/config anchor, and evidence level. Record each negative claim with the searched roots, term families, and limits.

- [x] **Step 2: Verify public primary sources**

Use official Google, Apple, QNX/BlackBerry, Texas Instruments, NXP, FCC, and FCA/Mopar sources where available. Store title, publisher, URL, date/access note, and the exact claim supported; identify inference explicitly.

- [x] **Step 3: Close the two target assessments separately**

Populate separate Android Auto and CarPlay block matrices using only `ALREADY PRESENT`, `PRESENT BUT NEEDS ADAPTER/GLUE`, `MISSING SOFTWARE`, `MISSING HARDWARE`, `EXTERNAL AUTHENTICATION DEPENDENCY`, and `UNKNOWN`. Select one next engineering objective.

- [x] **Step 4: Validate scope exclusions**

Ensure the model contains no Yelp/3G restoration work, signing/DRM bypass, MFi bypass, secret extraction, firmware modification, vehicle modification, or projection-client implementation.

### Task 2: Deterministic renderer and tests

**Files:**
- Create: `analysis_tools/wired_projection_feasibility.py`
- Create: `analysis_tools/tests/test_wired_projection_feasibility.py`

- [x] **Step 1: Write failing schema and safety tests**

Test required evidence levels, claim/source references, negative-search scope, exact target grades, exact architecture block vocabulary, one-and-only-one next objective, forbidden-topic rejection, repository-relative paths, canonical JSON, and the exact generated file set.

- [x] **Step 2: Run the focused tests and confirm failure**

Run: `python -m unittest analysis_tools.tests.test_wired_projection_feasibility -v`

Expected: import or missing-implementation failure before the renderer exists.

- [x] **Step 3: Implement the minimal validator and renderer**

Implement bounded JSON loading, source-hash verification, fail-closed cross-reference validation, canonical JSON output, Markdown rendering, `--write`, and `--check`. Do not read or execute recovered target binaries.

- [x] **Step 4: Run focused tests**

Run: `python -m unittest analysis_tools.tests.test_wired_projection_feasibility -v`

Expected: all focused tests pass.

### Task 3: Authoritative generated package

**Files:**
- Create: `docs/wired_projection_feasibility.md`
- Create: `docs/ra4_usb_architecture.md`
- Create: `docs/ra4_projection_av_pipeline.md`
- Create: `docs/ra4_projection_hmi_integration.md`
- Create: `docs/ra4_vs_later_uconnect_projection.md`
- Create: `docs/carplay_authentication_boundary.md`
- Create: `docs/android_auto_feasibility.md`
- Create: `reports/wired_projection/usb_inventory.json`
- Create: `reports/wired_projection/av_pipeline.json`
- Create: `reports/wired_projection/projection_gap_matrix.json`
- Create: `reports/wired_projection/hardware_comparison.json`
- Create: `reports/wired_projection/verification.md`

- [x] **Step 1: Generate the complete artifact set**

Run: `python analysis_tools/wired_projection_feasibility.py --write`

Expected: exactly the twelve listed files are created with LF line endings and stable ordering.

- [x] **Step 2: Check main-assessment coverage**

Confirm the main report contains the 22 requested sections, separate grades, exact blockers, minimum architectures, one next objective, evidence labels, public citations, verification, and branch/commit provenance wording.

- [x] **Step 3: Check detailed call graphs and matrices**

Confirm the USB report contains phone insertion through enumeration/classification/service/HMI, the AV report covers video/audio/microphone/input, and the HMI report covers lifecycle and safety arbitration without proposing safety bypass.

### Task 4: Deterministic and regression verification

**Files:**
- Modify: `reports/wired_projection/verification.md`

- [x] **Step 1: Run the complete Python suite**

Run: `python -m unittest discover -s analysis_tools/tests -v`

Expected: all tests pass with no skips.

- [x] **Step 2: Run generated-report check mode twice**

Run twice: `python analysis_tools/wired_projection_feasibility.py --check`

Expected: both runs report the same twelve-file manifest and no drift.

- [x] **Step 3: Verify baseline inputs and Git hygiene**

Run source-hash checks embedded in the renderer, `git diff --check`, and `git status --short`. Recompute the original checkout status/diff/untracked fingerprints and require equality with the pre-work values.

- [x] **Step 4: Review every requested conclusion**

Trace each final positive statement to a claim ID and each absence statement to an explicit bounded search. Downgrade any unsupported conclusion to `UNKNOWN`.

### Task 5: Commit and publish the isolated closure

**Files:**
- Modify: `docs/wired_projection_feasibility.md`
- Modify: `reports/wired_projection/verification.md`

- [x] **Step 1: Record final branch provenance**

Record branch `codex/ra4-wired-projection-feasibility`, authoritative base `5b9826b2b6537f12b4bf08a50003ea6914263700`, and the pending commit process without inventing a self-referential commit hash inside generated content.

- [x] **Step 2: Commit the closure**

Run: `git add analysis_tools/wired_projection_feasibility.py analysis_tools/wired_projection_notes.json analysis_tools/tests/test_wired_projection_feasibility.py docs reports/wired_projection && git commit -m "docs: close RA4 wired projection feasibility"`

Expected: one isolated commit containing only this feasibility package and its plan.

- [x] **Step 3: Push without opening a pull request**

Run: `git push -u origin codex/ra4-wired-projection-feasibility`

Expected: remote branch updated; no PR created.
