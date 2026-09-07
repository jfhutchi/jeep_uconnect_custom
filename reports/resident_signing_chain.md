# RA4 Resident Application Signing Chain

## Result

The stock executable JAR is not self-signed. Its fixed sibling `key.jar` is a
detached JAR-signature carrier that binds the executable members and signed
descriptor. The recovered content chain is exact through public signer
certificate extraction:

```text
executable JAR member bytes + key.jar!/xlet.properties
  -> per-member SHA-1/SHA-256 records in key.jar!/META-INF/MANIFEST.MF
  -> full-manifest digest in key.jar!/META-INF/<alias>.SF
  -> detached PKCS#7/CMS signature in key.jar!/META-INF/<alias>.RSA
  -> public application signer certificate(s) embedded in the signature block
  -> AMS key.jar!/xlet.properties certificate objects
  -> developer-token branch, else optional device-token and SigningKeys branch
  -> signer/principal/policy acceptance                         UNKNOWN tail
```

## Directly proved links

- **PROVED:** all 135 recovered executable JARs exist and contain no embedded
  `.RSA`, `.DSA`, or `.EC` signature block.
- **PROVED:** all 135 companion `key.jar` files contain no classes and contain a
  manifest, `.SF`, paired `.RSA`, and signed `xlet.properties`.
- **PROVED:** the corpus verifier resolved 82,938 digest records across the
  associated executable JAR or retained `key.jar` member; all 82,938 matched,
  with zero missing members and zero uncovered executable members.
- **PROVED:** 137/137 `.SF` full-manifest digest records recomputed exactly.
- **PROVED:** OpenSSL 3.5.7 accepted the PKCS#7 signature value over the paired
  `.SF` for 137/137 blocks using `-noverify`. This proves signature mathematics
  against the embedded public certificate, not AMS trust-chain acceptance.
- **PROVED:** AMS `Installer` constructs fixed sibling `key.jar`; installed Xlet
  launch passes it through `XletManager` and `XletClassLoader`; signer lookup
  obtains certificate objects from exactly `key.jar!/xlet.properties`.
- **PROVED:** missing `key.jar` takes a primary-resource signer fallback. No
  evidence shows that fallback accepts an unsigned executable.

## Observed signer metadata

| Public certificate SHA-256 | Observed key JARs | Public identity |
| --- | ---: | --- |
| `9ebf781bd18ad8c1f33b5b4727a2bed922b6cd4fb9680250a30de68045f3f546` | 123 | Chrysler UConnect Application CA |
| `108755c1180f00d64192e123466d806eba48631924aa0135009b80323cb4170a` | 12 | FCA VP4 Application |
| `337af8c28a24f4f1ac3c13b25dfb535335521d6273aef90ade650ab7786d62aa` | 2 dual-signed cases | Accenture additional certificate |

The isolated `Xlet Developer` certificate in development `security.jar` appears
in no stock application `key.jar`. This corpus fact neither supplies its private
key nor proves that a legitimate development package cannot use another form.

## Security-configuration bootstrap and verifier order

`rom:/internal.jar` authenticates the selected production/development
`security.jar` through immutable aicas DSA/RSA roots. Certificates attached to
selected `security.jar!/xlet.security` are promoted as final signing-key
candidates. Production promotes Chrysler plus aicas; development promotes Xlet
Developer plus aicas.

The recovered AMS branch order is:

1. Verify signed `xlet.developerToken` against runtime `developerId`.
2. If it succeeds, return success without the certificate branch.
3. Otherwise, if a device token exists, verify it against runtime device ID.
4. Submit signer certificate objects to `SigningKeys.verify`.

`SignedId` Base64-decodes the token; the RSA path uses public-key
`RSA/ECB/PKCS1Padding` type-1 unpadding and exact plaintext equality with the
runtime ID. The token is signed package metadata, not an anti-theft PIN result.
No token bytes are reproduced or reusable.

## Unknown trust tail

- Legitimate private signing authority, certificate enrollment/CSR process,
  developer-ID issuance, device-ID binding, and organizational approval route.
- AOT `getJarEntryCertificates` details and whether live launch independently
  repeats every demonstrated cross-JAR digest calculation.
- `SigningKeys.verify` chain building, certificate ordering, time, revocation,
  algorithm-policy and cache behavior.
- The exact accepted signer-to-principal, code-source, policy-domain and DRM
  relationship.
- Whether live incoming package authentication uses an internal `key.jar`, a
  normal self-signed outer JAR, or a transformation performed by the installer.

The service certificate is a separate HU-serial-bound, expiring engineering-menu
authorization. **PROVED:** it does not issue an application signer, developer
token, app ID, Java principal or DRM grant. It is not part of this chain.

## Validator boundary

`analysis_tools.resident_package_inspect` recomputes member and `.SF` manifest
digests, requires an exact nonempty `.SF`/signature-block alias pairing, requires
the public PKCS#7 parser and rejects unavailable or unparseable certificate
metadata, and extracts only public certificate metadata. It intentionally reports
`signature_math_verified=false`; it neither invokes an RA4 trust decision nor
treats an embedded certificate as trusted. The existing corpus-wide OpenSSL
result remains the independent signature-math evidence.
