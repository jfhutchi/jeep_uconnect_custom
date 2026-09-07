# Hello Uconnect Xlet Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reproducibly build and prove an independently authored, Java 1.4 / classfile-major-48 Hello Uconnect Xlet while leaving target signing and installation explicitly unresolved.

**Architecture:** Compile clean-room declaration-only Xlet/LWUIT stubs into a host-only classpath JAR, compile original application source with an ordinary JDK 8 compiler, package only original classes into a deterministic JAR, and audit the JAR plus its logical descriptor with a standard-library Python classfile validator and exact API allowlist.

**Tech Stack:** Java 1.4 source/bytecode emitted by JDK 8 `javac`; PowerShell orchestration; Python 3 standard library for deterministic JAR construction, classfile parsing, reports and `unittest` verification.

---

## Tasks

- [x] Correct `docs/10_evidence_gates.md` and
  `docs/21_first_resident_runtime_proof.md`. Separate Java host compilation,
  native ABI work, package authentication and target lifecycle gates. Preserve
  PROVED/INFERRED/UNKNOWN and every stock-safety/recovery requirement.
- [x] Add failing focused tests in
  `prototype/hello_uconnect/tests/test_artifact_tools.py`. Construct minimal
  synthetic classfiles/JARs and require rejection of wrong classfile versions,
  unexpected constant-pool members, native methods, JNI calls, network/USB/
  vehicle/AppManager references and bundled compile stubs. Require deterministic
  packaging/inventory and safe descriptor fields. Run the focused suite and
  observe the expected import/missing-implementation failure.
- [x] Implement `prototype/hello_uconnect/tools/artifact_tools.py` and
  `prototype/hello_uconnect/tools/validate_artifact.py`. Parse classfile headers,
  all relevant constant-pool tags, method access flags and symbolic member
  references; enforce the explicit JSON allowlist; produce bytecode, dependency,
  inventory, SHA-256 and installed-size reports; make every violation fatal.
  Re-run focused tests to green.
- [x] Add the smallest declaration-only sources under
  `prototype/hello_uconnect/compile_api/src`. Include the recovered Xlet,
  XletContext and exception signatures plus only the LWUIT classes/members used
  by Hello. Record a per-signature evidence pointer in
  `prototype/hello_uconnect/compile_api/PROVENANCE.md`. Never package these
  classes in the application JAR.
- [x] Add
  `prototype/hello_uconnect/src/com/jfhutchi/uconnect/hello/HelloUconnectXlet.java`.
  Initialize through XletContext/AWT/LWUIT, show original text, update a counter
  with one button, exit with `notifyDestroyed()`, create no private thread and
  keep pause/destroy behavior bounded.
- [x] Add `prototype/hello_uconnect/descriptor/xlet.properties`, an exact
  `api-allowlist.json`, `build.ps1`, `.gitignore` and README. Use app ID
  `4e9838d7-d08f-5f3a-be95-b309114fc22e`; mark every logical output host-built,
  unsigned and not target-installable; make `build/` the only generated output
  directory and keep it ignored.
- [x] Install or select only ordinary host JDK 8 tooling. Build twice from a
  clean generated directory with `-source 1.4 -target 1.4`, compare SHA-256 and
  inventories, and fail rather than accepting newer bytecode. Record exact
  compiler/runtime versions and generated measurements in
  `reports/hello_uconnect_host_artifact.md` without committing generated JARs.
- [x] Run focused Hello tests, the complete existing Python and Node suites,
  source sanity checks, the full build/validator, a second deterministic build,
  `git diff --check`, and a scoped vendor-content/status review. Resolve all
  failures or record a genuine environmental blocker.
- [x] Update this checklist and PR #14's description with the new host-artifact
  checkpoint. Commit only scoped source/docs/tests, push
  `codex/ra4-driver-temperature`, verify the remote commit and leave `git status`
  clean. Do not run GitHub Actions or merge main.

## Verification contract

The final generated status must report actual values for classfile major,
native methods, invokedynamic, bundled stubs/runtime, native libraries, JNI,
networking, USB, vehicle services, AppManager privilege, unexpected APIs,
autostart, daemon, audio and installability. All prohibited/unexpected counts
must be zero, classfile major must be 48, and installability must remain `NO`.
