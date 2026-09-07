# RA4 Resident Package and Trust Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconstruct the minimum legitimate RA4 resident package, identity, signing, policy and installation contract and add a read-only structural validator without creating credentials or an installable package.

**Architecture:** Treat the single incoming JAR, factory installed layout, detached executable signature, DRM grant, Java policy and AppManager/AMS state as separate layers. Validate only byte structures directly supported by stock artifacts and report unknown authority/runtime decisions as missing gates.

**Tech Stack:** Python 3 standard library for ZIP/JAR/properties/manifest parsing and deterministic JSON; optional existing `cryptography` dependency for public PKCS#7 certificate metadata; `unittest`; Markdown evidence reports; PowerShell for local verification.

---

## Tasks

- [x] Record the approved design and this implementation plan. Reuse the
  existing bounded KIM, installer, AMS, signer, policy and AppManager evidence;
  do not perform another broad firmware scan.
- [x] Add failing synthetic tests for installed-layout recognition, identity and
  descriptor consistency, detached manifest coverage/digest mismatch,
  signature-material presence, prohibited entitlement fields, deterministic
  reports and non-installability of an unsigned Hello skeleton. Observe the
  expected missing-module failure.
- [x] Implement `analysis_tools/resident_package_inspect.py` as a read-only
  standard-library inspector. Support factory installed-layout directories and
  single-JAR candidates; parse Java properties and JAR manifests; validate
  cross-JAR digest coverage; inventory signatures; optionally report sanitized
  public certificate metadata; emit exact missing gates and deterministic JSON.
- [x] Add usage and limits to `analysis_tools/README.md`. Run the focused tests
  against synthetic inputs and bounded known Slacker/Application Manager stock
  directories, recording hashes and structural results without tracking vendor
  bytes.
- [x] Add a deterministic host-only Hello installed-layout analogue generator.
  Include only the existing Hello JAR and descriptor, omit `key.jar` rather than
  fabricating trust material, label every output unsigned/non-installable, keep
  generated output ignored, and prove the inspector reports the intended gaps.
- [x] Create focused reports for resident package format, identity model,
  signing chain, policy entitlements, install lifecycle and Hello installability.
  Finish the gap report with the requested gate/status/evidence/missing table and
  use only PROVED/INFERRED/UNKNOWN classifications.
- [x] Run the complete Python, Hello, Node and deterministic-build verification;
  syntax-check new Python; inspect generated ignore status; scan tracked changes
  for credentials/private keys and recovered implementation bytes; run
  `git diff --check`; inspect status and final diff.
- [x] Mark this checklist complete, commit the coherent checkpoint with
  `[skip ci]`, push `codex/ra4-driver-temperature`, update draft PR #14 without
  dispatching Actions, verify local/remote HEAD and confirm `main` is unchanged.

## Verification contract

The inspector may prove structural analogy and digest/signature presence. It
must never emit `installable: true`; accepted incoming container, legitimate
issuer/identity, certificate trust, signer-to-principal/policy, effective DRM
grant and target runtime acceptance remain explicit external gates until
directly demonstrated through an authorized process.
