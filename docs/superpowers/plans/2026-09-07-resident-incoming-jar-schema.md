# Resident Incoming-JAR Schema Investigation Plan

> **Execution mode:** Static, read-only firmware research. No signing, credential generation, target connection, installation, trust-store change, DRM change, or vendor-binary execution.

**Goal:** Recover the AMS contract for the single resident-application JAR, prove the incoming-to-installed transformation, and state the smallest remaining legitimate issuance gate.

**Evidence standard:** Every conclusion is labeled PROVED, INFERRED, DISPROVED, or UNKNOWN and cites a reproducible file offset, symbol, artifact hash, or deterministic tool output.

## Task 1: Preserve the parser evidence

- [x] Record the Installer ROM/AOT method map and constant-pool resolution.
- [x] Record bytecode anchors for authenticated preflight, staging, install, upgrade, and rollback.
- [x] Record AOT anchors for direct-JAR iteration, suffix routing, certificate retrieval, and `SigningKeys.verify`.
- [x] Separate method-level proof from credential-branch details that remain opaque.

## Task 2: Add a read-only inverse-transformation check

**Files:**
- Modify: `analysis_tools/resident_package_inspect.py`
- Modify: `analysis_tools/tests/test_resident_package_inspect.py`

- [x] Add failing tests for the AMS split rule and deterministic reconstructed content-set report.
- [x] Implement exact, case-sensitive AMS routing for `.MF`, `.SF`, `.RSA`, and `.DSA` entries.
- [x] Prove the only permitted payload/key overlap is identical root `xlet.properties`.
- [x] Report a canonical content-set fingerprint without writing or reconstructing an archive.
- [x] Update single-JAR reporting to distinguish structural conformance from legitimate authorization.
- [x] Keep all malformed-input behavior fail-closed.

## Task 3: Exhaust recovered-package evidence

- [x] Inventory non-toolchain JARs and distinguish KIM installed trees from live staging artifacts.
- [x] Search app-media, catalog, download, temporary, deleted/recovered, and update-remnant paths.
- [x] Run the inverse-transformation check across every complete recovered installed application.
- [x] Produce a deterministic aggregate report with counts, exceptions, and content fingerprints.

## Task 4: Document the recovered contract

**Files:**
- Add: `reports/resident_incoming_jar_schema.md`
- Update: `reports/resident_package_format.md`
- Update: `reports/resident_install_lifecycle.md`
- Update: `reports/resident_signing_chain.md`
- Update: `reports/resident_identity_model.md`
- Update: `reports/hello_installability_gap.md`

- [x] Document exact member routing and the incoming-to-installed chain.
- [x] Document app-ID validation, payload filename normalization, temp-directory promotion, and upgrade rollback.
- [x] Distinguish archive signing from detached installed storage.
- [x] Disprove nested payload/key envelopes and live `magic.txt` creation by Installer.
- [x] Bound signer alias, certificate-chain, token, Principal/policy, DRM, and issuer-side unknowns.
- [x] Identify the smallest missing artifact needed to cross the remaining evidence boundary.

## Task 5: Verify and deliver

- [x] Run focused tests before and after implementation and preserve the red/green evidence.
- [x] Run all Python tests, inspector tests, Hello tests, Node resident-HMI tests, syntax compilation, deterministic rebuilds, and `git diff --check`.
- [x] Scan the diff for private keys, credentials, recovered certificates, tokens, and proprietary binaries.
- [x] Request an independent final-diff review for unsupported claims and accidental sensitive/binary inclusion.
- [x] Resolve all review findings and rerun affected verification.
- [x] Commit, push the existing branch, and update draft PR #14 without merging it.
