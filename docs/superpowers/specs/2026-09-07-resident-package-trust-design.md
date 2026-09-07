# RA4 Resident Package and Trust Contract Design

Date: 2026-09-07. Approved by the owner's task specification. This work is
read-only with respect to every head unit, firmware image, trust store, package
database and credential. It does not authorize installation or execution.

## Objective

Replace the broad statement "signing/package identity unresolved" with the
smallest evidence-supported contract between the deterministic Hello Uconnect
JAR and a legitimately accepted RA4 resident application. Preserve a strict
separation among the incoming delivery object, AMS's installed layout,
application identity, byte authentication, DRM/launcher entitlement, Java
policy and lifecycle installation state.

## Evidence boundary

- **PROVED:** the stock application-media path and catalog path both hand a
  single local JAR to the secure AMS/AppManager installation boundary. The
  corpus contains no live incoming JAR sample, so its complete internal schema
  is not proved.
- **PROVED:** factory KIM content installs an external descriptor at
  `<appId>/prog/xlet.properties`, an executable JAR and fixed `key.jar` sibling
  below `prog/jars/`, plus a six-byte `magic.txt` copy sentinel.
- **PROVED:** stock `key.jar` files are detached signed envelopes. Their
  manifests bind every executable-JAR member and the embedded signed
  `xlet.properties`; `.SF` authenticates the manifest; PKCS#7 `.RSA` authenticates
  `.SF` and carries public signer certificates.
- **PROVED:** signed and installed descriptors are distinct forms. Identity,
  main class and policy keys agree across all observed pairs, while installation
  commonly rewrites `xlet.jarFile`.
- **PROVED:** AMS uses the fixed installed `key.jar!/xlet.properties` signer
  association, checks the signed developer token first, then the optional
  device token and promoted signing keys. Native AppManager separately performs
  a DRM check and authenticated package-info preflight.
- **UNKNOWN:** the exact single-JAR incoming schema, credential issuer and
  enrollment process, accepted new app-ID allocation rule, AOT certificate-to-
  principal mapping, policy-domain construction, minimum DRM grant, and live
  target acceptance of a newly issued identity.

## Deliverables

Six focused reports will define package format, identity, signing, entitlements,
installation lifecycle and Hello's remaining gap. Each material statement is
graded **PROVED**, **INFERRED** or **UNKNOWN**, cites existing recovered evidence,
and includes bounded reproduction commands.

A new standard-library, read-only inspector will analyze either:

1. a factory installed-layout application directory; or
2. a single ZIP/JAR candidate without assuming it is accepted.

For an installed-layout directory it will parse both descriptor forms, identify
the payload, inventory signature metadata, recompute manifest member digests,
report only public certificate fingerprints/subjects when the optional existing
`cryptography` dependency is available, classify privilege-related descriptor
fields, and list every missing acceptance gate. It will never verify private
authority, create a signature, modify an archive or install anything.

The inspector will use exact classifications:

- `factory-installed-layout-analogue` only when the proved KIM layout is
  satisfied and detached digest coverage is valid;
- `single-jar-candidate` for a JAR supplied to the incoming-object mode;
- `incomplete-installed-layout-skeleton` for the explicitly missing Hello
  envelope pieces, and `invalid-installed-layout` for other malformed or
  inconsistent directory input.

Structural analogy is not installability. A passing stock-layout inspection
means only that the bytes match the recovered factory layout and detached
manifest contract.

## Test strategy

Tests create only original synthetic ZIPs and descriptors. Before implementation
they require failures for missing/malformed descriptors, app-ID/path mismatch,
payload mismatch, absent or malformed detached signatures, incomplete or
incorrect cross-JAR digests, unsafe privilege fields and attempts to treat an
unsigned Hello skeleton as installable. Deterministic JSON output and stable
member inventories are also required.

## Hello artifact decision

The incoming live-package container is not proved, so no purported install JAR
will be created. A host-generated directory may model only the proved installed
layout, containing the existing deterministic original Hello JAR and draft
descriptor but no fabricated `key.jar`, certificate, developer token, DRM grant
or production package identity. It must be named and reported as an
`UNSIGNED / NON-INSTALLABLE / RESEARCH ARTIFACT` and fail installability checks
for the explicit missing detached envelope and issuance gates.

## Safety and acceptance

The work must not expose private key material or token bytes, alter any stock
artifact, weaken AMS/DRM/policy checks, produce target commands, or claim a
structural analogue is accepted. Completion requires all existing tests, new
inspector tests, the deterministic Hello build, syntax checks, credential and
vendor-payload reviews, `git diff --check`, a clean tracked tree after commit,
and a draft PR checkpoint without changing `main`.
