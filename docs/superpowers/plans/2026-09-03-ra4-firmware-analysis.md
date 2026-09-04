# RA4 18.45.01 Firmware Analysis Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development to execute this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a reproducible, read-only architecture and CarPlay feasibility assessment of `Uconnect_VP4,18.45.01-My13-17.zip` without executing or altering firmware payloads.

**Architecture:** Treat the root ZIP as immutable evidence. Store every derived artifact under `analysis_ra4_18.45.01/`, use passive parsers and magic-byte inspection only, and trace final statements to paths, offsets, hashes, or captured tool output. Parallel investigators may read the shared extraction but will not edit it or execute any payload.

**Tech Stack:** PowerShell/.NET ZIP APIs, Windows hashing utilities, passive archive/filesystem parsers available locally, static byte/string inspection, OpenSSL when available, and Markdown evidence reports.

---

### Task 1: Establish Evidence Provenance and Safe Workspace

**Files:**
- Read only: `Uconnect_VP4,18.45.01-My13-17.zip`
- Create: `analysis_ra4_18.45.01/evidence/archive_hashes.txt`
- Create: `analysis_ra4_18.45.01/evidence/tool_versions.txt`
- Create: `analysis_ra4_18.45.01/evidence/archive_metadata.txt`

- [ ] **Step 1: Create explicit derived-data directories**

Create `analysis_ra4_18.45.01/evidence`, `analysis_ra4_18.45.01/inventory`, `analysis_ra4_18.45.01/extracted`, `analysis_ra4_18.45.01/work`, and `analysis_ra4_18.45.01/notes`. Do not change attributes or timestamps on the source ZIP.

- [ ] **Step 2: Record source metadata and hashes**

Calculate SHA-256, SHA-512, SHA-1, and MD5 over the original archive and record its exact byte length and UTC timestamps. Use streaming hash APIs so the 1.266 GB source is never rewritten.

- [ ] **Step 3: Record tool provenance**

Capture OS, PowerShell, archive parser, filesystem parser, OpenSSL, and static-inspection tool versions used. Mark unavailable tools rather than silently substituting an unknown implementation.

- [ ] **Step 4: Re-hash after all analysis**

Repeat every archive hash at the end and byte-compare the pre/post records. Expected result: all digests and the byte length are identical.

### Task 2: Inventory and Extract the ZIP Copy

**Files:**
- Create: `analysis_ra4_18.45.01/inventory/zip_inventory.csv`
- Create: `analysis_ra4_18.45.01/inventory/zip_inventory.txt`
- Create: `analysis_ra4_18.45.01/evidence/zip_validation.txt`
- Create: `analysis_ra4_18.45.01/extracted/**`

- [ ] **Step 1: Parse the ZIP central directory without extraction**

Record each path, uncompressed size, compressed size, timestamp, compression ratio, and directory status. Also record totals and duplicate normalized paths.

- [ ] **Step 2: Validate safe extraction paths**

Reject absolute paths, drive-qualified paths, NUL-containing names, and normalized paths escaping `analysis_ra4_18.45.01/extracted`. Expected result: every entry resolves beneath the extraction root.

- [ ] **Step 3: Test archive integrity passively**

Read/decompress every ZIP member without launching it and record any CRC/decompression error. Expected result: zero corrupt members before proceeding.

- [ ] **Step 4: Extract to the dedicated directory**

Extract only into `analysis_ra4_18.45.01/extracted`, preserving the archive. Record the resulting file count and byte total and compare them with the inventory.

### Task 3: Classify Payloads and Recover Nested Layouts

**Files:**
- Create: `analysis_ra4_18.45.01/inventory/extracted_hashes.csv`
- Create: `analysis_ra4_18.45.01/inventory/file_types.csv`
- Create: `analysis_ra4_18.45.01/inventory/container_layouts.md`
- Create: `analysis_ra4_18.45.01/work/**`

- [ ] **Step 1: Hash and type every extracted file**

Record relative path, size, SHA-256, first 64 bytes, printable magic, entropy sample, and identified format. Identification must rely on passive parsers and signatures, not filename extensions alone.

- [ ] **Step 2: Locate SWDL, ISO, UPD, image, archive, and filesystem candidates**

Search names and magic signatures for ISO-9660/UDF, SquashFS, CramFS, ext filesystems, FAT, tar/cpio, gzip/xz/bzip2, ELF, PE, QNX IFS, Android sparse images, raw partition tables, and vendor headers.

- [ ] **Step 3: Parse nested containers read-only**

Prefer listing/extraction into a new `work/<container-sha256>/` directory. If mounting is necessary, use an explicit read-only loop/mount and unmount immediately; never mount a firmware filesystem read-write.

- [ ] **Step 4: Map partitions and boot/update flow**

Record offsets, lengths, labels, filesystem types, boot images, updater programs/scripts, dependency ordering, target paths/devices, rollback or slot behavior, and the evidence supporting CPU/OS conclusions.

### Task 4: Analyze Authentication and Replaceability

**Files:**
- Create: `analysis_ra4_18.45.01/inventory/security_artifacts.csv`
- Create: `analysis_ra4_18.45.01/notes/security_findings.md`

- [ ] **Step 1: Inventory cryptographic material**

Locate certificates, public keys, detached or embedded signatures, signed manifests, digest lists, CRC tables, encrypted envelopes, and verification-related strings/imports. Parse public metadata only; do not attempt private-key recovery or signature bypass.

- [ ] **Step 2: Trace verification boundaries**

Determine whether authentication covers the outer ZIP, SWDL/ISO/UPD containers, manifests, partitions, or individual packages. Verify any discoverable digest/signature against the exact bytes it claims to cover.

- [ ] **Step 3: Assess component replaceability**

Separate packaging modularity from accepted-update modularity. Report whether applications are individually packaged, whether manifests permit independent targets, and whether cryptographic/dependency checks make unsigned or partial replacement infeasible.

### Task 5: Map Functional Components and Projection Evidence

**Files:**
- Create: `analysis_ra4_18.45.01/inventory/string_hits.csv`
- Create: `analysis_ra4_18.45.01/notes/component_map.md`
- Create: `analysis_ra4_18.45.01/notes/projection_findings.md`

- [ ] **Step 1: Build a case-insensitive string/search index**

Search ASCII and UTF-16LE/BE content for UI/HMI, touch, display/video, audio, Bluetooth, USB/media, navigation, cellular/3G, CAN/vehicle services, HVAC, seats, steering-wheel heat, CarPlay, Apple, iAP/iAP2, Android Auto, projection, MirrorLink, USB host, H.264, and OpenGL terms. Preserve file path, offset, encoding, and bounded context.

- [ ] **Step 2: Correlate strings with executable and service structure**

Use ELF/PE/QNX metadata, library dependencies, configuration, IPC names, device nodes, and manifests to distinguish an implemented component from an incidental string or third-party library capability.

- [ ] **Step 3: Assess hardware/software interfaces relevant to external CarPlay**

Identify evidence for video ingress/compositing, touch event routing, audio source/mixer paths, USB modes, Bluetooth coexistence, CAN controls, and retention of original vehicle-control screens. Clearly mark any hardware claim not proven by this firmware package.

### Task 6: Synthesize the Four Deliverables

**Files:**
- Create: `docs/firmware_architecture.md`
- Create: `docs/component_inventory.md`
- Create: `docs/update_security.md`
- Create: `docs/carplay_feasibility.md`

- [ ] **Step 1: Write firmware architecture**

Document OS, CPU ABI, boot/update chain, container and filesystem layouts, executables, manifests, partitions, and a concise evidence table with `Verified`, `Strong inference`, `Hypothesis`, and `Unknown` confidence labels.

- [ ] **Step 2: Write component inventory**

Map every requested function to discovered files/services/libraries, evidence, confidence, and unresolved questions. Include exact search results for requested projection-related terms and explicitly distinguish positive, negative, and ambiguous evidence.

- [ ] **Step 3: Write update security**

Describe hashes/checksums, certificates/signatures, verification order and coverage, trust anchors visible in the package, anti-rollback/version checks if found, and component replaceability without offering bypass or flash instructions.

- [ ] **Step 4: Write CarPlay feasibility**

Compare native modification with a hidden external CarPlay computer using factory display/touch/audio while preserving Uconnect vehicle controls. Base the recommendation on verified interfaces and identify the specific bench measurements or hardware teardown evidence needed to resolve firmware-only unknowns.

### Task 7: Independent Review and Final Verification

**Files:**
- Verify: `docs/firmware_architecture.md`
- Verify: `docs/component_inventory.md`
- Verify: `docs/update_security.md`
- Verify: `docs/carplay_feasibility.md`
- Create: `analysis_ra4_18.45.01/evidence/final_verification.txt`

- [ ] **Step 1: Run independent evidence review**

Have a reviewer check every high-impact conclusion against extracted evidence and flag unsupported extrapolation, especially OS/CPU, signature coverage, update replaceability, and native-CarPlay feasibility.

- [ ] **Step 2: Check report completeness**

Verify all ten user tasks, all listed vehicle functions, and all requested search terms are addressed. Scan for placeholder text and broken local evidence paths.

- [ ] **Step 3: Reconcile inventories**

Confirm ZIP member counts/sizes match extraction counts/sizes, every cited file exists, every SHA-256 is correctly formatted, and nested extraction provenance is recorded.

- [ ] **Step 4: Confirm source immutability**

Recompute archive hashes and compare with Task 1. Record the comparison and final source metadata in `final_verification.txt`.
