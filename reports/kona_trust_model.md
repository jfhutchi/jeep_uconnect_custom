# RA4 Kona Trust Model

## Scope

This report maps the trust artifacts visible in the owner-supplied RA4 18.45.01 extraction. It does not add certificates, change a keystore, bypass signer checks, recover keys, or claim that desktop Java behavior exactly reproduces the embedded AMS/Jamaica runtime.

Primary artifacts:

- `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/security/cacerts`
- `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/security/security.jar`
- `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/security/development/security.jar`
- JARs beneath `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/`

## Kona `cacerts`

Artifact identity:

- Size: 10,117 bytes
- SHA-256: `2b931d5574d94c886a2ec13c3301585e405f2d68abf90fed3287383e55c7d0d0`
- Format: JKS (`0xfeedfeed` magic), version 2
- Entries: 7 trusted-certificate records
- Structural parse: 10,097 data bytes followed by the expected 20-byte JKS integrity field

| Trusted subject | SHA-256 fingerprint | Certificate expiry |
|---|---|---|
| Chrysler UConnect Website CA | `4e3492e31cf9681c2a6f18ed2dbe8584be4d0945fc1c289615f836dd15952f98` | 2032-05-20 UTC |
| Chrysler UConnect NGTP | `0dbf04e768045a2fa2392e6b0f7465e07a4b8476b49e3d7eee79e35ab89bc5b5` | 2031-12-02 UTC |
| Entrust.net Certification Authority (2048) | `d1c339ea2784eb870f934fc5634e4aa9ad5505016401f26465d37a574663359f` | 2019-12-24 UTC |
| Entrust Certification Authority - L1C | `949cf3b3ce62262a02ed31236ae03725cff4e3b216b8cb291abc68fd097c71cf` | 2019-12-10 UTC |
| VeriSign Class 3 Secure Server CA - G3 | `64903546a58058d1e6f1bead1134ede66a6831d231f0df8d4e28535d7a300496` | 2020-02-07 UTC |
| VeriSign Class 3 Public Primary CA - G5 | `9acfab7e43c8d880d06b262a94deeee4b4659989c3d0caf19baf6405e41ab7df` | 2036-07-16 UTC |
| Chrysler UConnect NGTP IF1 | `32e4ec719aa8e64bc5c6c9432d4fe87e4f2922a38d5717e472473130b29d1514` | 2032-02-19 UTC |

The aliases embedded in the JKS are historical Jenkins workspace paths. They are identifiers, not evidence that those build paths exist on the head unit.

## Security-configuration signers

The security JARs carry these signer certificates:

| Signer | Certificate SHA-256 | Occurrence in security JARs |
|---|---|---|
| Chrysler UConnect Application CA | `9ebf781bd18ad8c1f33b5b4727a2bed922b6cd4fb9680250a30de68045f3f546` | Production only |
| Xlet Developer | `42a6e60121e81a065c6dc0f2e5cc33edd51405d93444e0b4ca292379871039a0` | Development only |
| aicas GmbH | `9f28ad4b65f3eca46049b9f6abfb5c169b8c1ea35dde01380c689dbceab10d4c` | Both |

None of these fingerprints equals one of the seven `cacerts` fingerprints. Because the embedded signer certificates are self-issued, no direct chain from them to the seven parsed JKS entries is visible.

This mismatch is now explained for security-configuration bootstrap: AMS does not use Kona `cacerts` at that edge. It seeds `_internalKeys_` from certificates on `rom:/internal.jar!/xlet.security`, authenticates the selected stock security JAR with those keys, and promotes certificates on the selected JAR's `xlet.security` into final token/certificate verifier keys. Kona `cacerts` can still serve unrelated TLS/PKIX functions; its complete consumer census remains separate.

The embedded first-stage JAR is pointer-bounded in AMS at file `[0x988778,0x9892AD)`, 2,869 bytes, SHA-256 `2dbf7986c70e16d7bb047b897492c6ce164a1b5954837590708ee65b73759dab`. Its zero-byte `xlet.security` entry has two independently valid manifest/signature envelopes. The public bootstrap identities are aicas GmbH DSA certificate SHA-256 `9f28ad4b65f3eca46049b9f6abfb5c169b8c1ea35dde01380c689dbceab10d4c` and aicas RSA certificate SHA-256 `0654d97249cd24168cffbd7987ba6a05b76550dc95d765a9dafc59aaf11afe07`. These authenticate the selected configuration; final application/token verifier keys come from that selected configuration's signed `xlet.security` entry.

## Corpus-wide JAR signer census

A read-only traversal opened every `.jar` below the canonical `XLETS` tree, read only `META-INF/*.RSA`, `*.DSA`, and `*.EC` signature blocks, and parsed their embedded certificates.

- JAR files inspected: 300
- JARs containing at least one signature block: 163
- Unique embedded certificate fingerprints: 5
- Parse errors: 0

| Embedded signer | Signature-block occurrences | `key.jar` occurrences | Security-JAR occurrences |
|---|---:|---:|---:|
| Chrysler UConnect Application CA | 146 | 123 | 1 |
| FCA VP4 Application (EMEA) | 16 | 12 | 0 |
| Accenture | 2 | 2 | 0 |
| aicas GmbH | 2 | 0 | 2 |
| Xlet Developer | 1 | 0 | 1 |

Representative production reuse:

- `base/kona/security/security.jar` uses the Chrysler UConnect Application CA.
- `kim_packages/KIM1/DRM.jar` uses the same certificate.
- Numerous KIM `prog/jars/key.jar` files use the same certificate.

The `Xlet Developer` certificate was found only in `base/kona/security/development/security.jar`. No application `key.jar` in this corpus carried that certificate.

## Evidence-backed architecture map

```text
Factory jvm.sh
  -> selected security.jar                         CONFIRMED
  -> AMS -securityConfiguration ... -secure       CONFIRMED

security.jar
  -> policy/configuration entries                 CONFIRMED
  -> embedded signer certificates                 CONFIRMED
  -> xlet.security certificates promoted into
     final token/certificate verification keys    CONFIRMED
  -> signer/revision -> principal/policy rule      UNKNOWN

application/KIM package
  -> DRM.jar and/or prog/jars/key.jar present     CONFIRMED for many packages
  -> embedded application signer certificate      CONFIRMED for signed JARs
  -> executable members + signed descriptor bound
     by key.jar manifest/.SF/PKCS#7                CONFIRMED corpus-wide
  -> Installer fixed sibling -> VCL keyJar_         CONFIRMED installed-launch graph
  -> signer objects from key.jar!/xlet.properties   CONFIRMED installed-launch graph
  -> AMS getPackageInfo(auth:true) before install  CONFIRMED native caller
  -> AOT signer-key match / principal acceptance   UNKNOWN details
  -> policy index/permission grant                 PARTLY MAPPED; exact native rule UNKNOWN

Kona cacerts
  -> seven network/Uconnect trust certificates    CONFIRMED
  -> security.jar first-stage trust                NOT USED IN PROVED BOOTSTRAP
  -> application signer trust                      NOT DIRECTLY OBSERVED
```

## Findings

### Finding: `cacerts` is not a direct fingerprint list for observed application signers

**Confidence:** CONFIRMED

**Evidence:** All seven JKS certificate fingerprints differ from all five signer fingerprints found across 163 signed JARs.

**Interpretation:** Treating `cacerts` as the complete AMS application-signing trust store is unsupported.

**Resolved first-stage alternative:** Embedded AMS keys, not Kona `cacerts`, are directly used here. `AMSController.<clinit>` extracts signer public keys from `rom:/internal.jar!/xlet.security` into `_internalKeys_`; the selected security JAR is loaded with those keys, and its `xlet.security` certificates are promoted into final verifier keys.

**Next validation:** Locate independent consumers of `/fs/mmc1/kona/security/cacerts`; it remains relevant to other TLS/PKIX functions but is no longer a candidate for this proved security-configuration bootstrap edge.

### Finding: the production application signer is reused broadly

**Confidence:** CONFIRMED

**Evidence:** The Chrysler UConnect Application CA fingerprint occurs in 146 signature blocks, including 123 `key.jar` files and the production security JAR.

**Interpretation:** This certificate is part of the normal factory application packaging ecosystem, not unique to the security bundle.

**Alternative explanation:** Reuse proves common signing identity, not AMS's certificate-chain, expiry, revocation, or principal-acceptance rule.

**Resolved validation:** `reports/kona_application_authorization.md:102-174` proves that `key.jar` is the detached signature carrier. Across 135 applications, its manifests cover all 78,756 regular executable-JAR members; 82,938 of 82,938 entry digests, 137 of 137 `.SF` full-manifest digests, and 137 of 137 PKCS#7 signatures verify. The embedded signed descriptor preserves identity-critical properties, including all six `xlet.developerToken` values.

**Next validation:** Recover AMS's trust-anchor/principal decision after the confirmed native `getPackageInfo({auth:true})` preflight and identify how a signer, optional developer token, DRM entitlement, and policy index combine.

### Finding: the development signer is deliberately isolated in this corpus

**Confidence:** HIGH

**Evidence:** The `Xlet Developer` fingerprint occurs once, only in the stock development security configuration.

**Interpretation:** Development mode definitely changes one promoted verifier key: production supplies Chrysler+aicas, while development supplies Xlet Developer+aicas. It may also alter principal/policy selection through signer identity or revision rather than broader policy text.

**Resolved token role:** The promoted keys are passed in the final `SecurityParameter`; `SignedId` uses them to decrypt the Base64 token and compare its plaintext exactly with `developerId`. They also feed `SigningKeys` certificate verification. This is more than archive-signature metadata, although exact application principal/policy assignment remains open.

**Resolved detached association:** `Installer` owns a fixed `<app>/prog/jars/key.jar` path, installed `AMSController.loadXlet` propagates it to `VerificationClassLoader.keyJar_`, and signer lookup reads certificate objects from `key.jar!/xlet.properties`. Missing-key fallback uses the primary resource. Exact offsets and bounds are in `reports/keyjar_runtime_association.md`.

**Next validation:** Recover AOT `getJarEntryCertificates(URL,String)` and `SigningKeys.verify(Object[])`, principal construction, and policy lookup; verify the missing runtime ID and legitimate credential-issuer boundary without creating credentials. The RSA provider edge itself is resolved in `reports/signedid_jce_semantics.md`.

## Current safe position

Do not add a certificate to `cacerts`, replace a signer, modify either security JAR, or disable verification. The factory corpus already contains both configurations and a stock selection mechanism. The security-configuration bootstrap, promoted token-verifier keys, exact SunJCE `RSA/ECB/PKCS1Padding` token predicate, package content binding, fixed installed `key.jar` association, verifier branch order, and native AppManager-to-AMS authenticated preflight are established. Remaining work is explanatory: recover AOT certificate extraction and `SigningKeys`, the runtime ID/legitimate issuer, incoming external-package association, and how application signer, developer token, DRM entitlement, policy index, and AMS principal construction interact.
