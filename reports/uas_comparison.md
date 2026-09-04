# UAS 21.9 Comparative Research

**Primary target:** RA4 / VP4 18.45.01  
**Comparison corpus:** local `analysis_uas_21.9/` tree  
**Method:** read-only metadata, signature, hash, file-format, and string analysis  
**Scope rule:** UAS observations are not projected onto RA4 unless independently present in RA4 evidence.

## Result

The available UAS tree is useful for comparing the *outer update format*, but it is not an inspectable UAS runtime filesystem. The host application, HMI, and related UAS payloads are encrypted segments. There is no source archive, source hash, extraction log, or full owner-supplied provenance record for this tree. Consequently:

- RA4's `AMS_DEVELOPMENT` selector, development `security.jar`, developer-token implementation, anti-theft flow, and Xlet/Application Manager internals are **RA4-CONFIRMED only**.
- No equivalent UAS implementation can be confirmed or ruled out from this corpus.
- The UAS update metadata and detached signatures are internally consistent and identify a full 21.9 update, but that does not establish the history or completeness of the extracted directory.
- The UAS outer update format is materially different from RA4's visible `swdl.upd` plus installer/primary/secondary ISO layout.

## Evidence labels

| Label | Meaning in this report |
|---|---|
| **RA4-CONFIRMED** | Directly demonstrated in the RA4 18.45.01 corpus. |
| **UAS-ONLY** | Directly demonstrated only in the accessible UAS files. |
| **SHARED** | Independently demonstrated on both sides. |
| **INFERRED** | Plausible interpretation that still needs runtime or decrypted evidence. |
| **UNKNOWN** | The present corpus cannot answer the question. |

## Corpus and provenance boundary

`analysis_uas_21.9/` contains 44 regular files totaling 1,077,907,214 bytes. Its important structure is:

```text
analysis_uas_21.9/extracted/
  manifest.xml
  manifest.sig
  publickey.cer
  second.ifs
  VP4R_Update/
    ss_pasa_usb.metadata
    Signature
    publickeycert.pem
    encrypted_*.tar.gz
    ar7/...
```

No UAS source ZIP or other parent archive is present. No record ties this extracted tree to a user-provided package hash. The three detached signature files are not duplicates, and the directory includes AR7 modem material plus 12 `encrypted_*.tar.gz` files. Three of those encrypted files are not named by the visible update metadata, so directory completeness and package membership cannot be inferred from co-location alone.

**Confidence:** CONFIRMED for the local inventory; UNKNOWN for original-package provenance.  
**Evidence:** `reports/corpus_inventory.md`, `analysis_uas_21.9/extracted/`.  
**Alternative explanation:** a source archive and extraction record may have existed outside the current repository.  
**Next validation:** obtain the owner's original UAS package, hash it before extraction, and reproduce this tree with a deterministic manifest.

## UAS outer authorization wrapper

`manifest.xml` describes a `SoftwareAccessModule`, not the RA4 ISO layout. Exact visible controls include:

- line 8: `Install` is `false`;
- line 9: `Debug` is `false`;
- line 10: `SkipHUIDCheck` is `true`;
- lines 12-14: `publickey.cer`, `manifest.sig`, and `second.ifs` are named;
- line 15: a SHA-256 value binds `second.ifs` to the manifest.

The SHA-256 of `second.ifs` is:

```text
c0020a6ea4038c33c4d2b1b1107057256775f607e5a6d32bdc4f6339d2147b70
```

Its Base64 representation is exactly the value in `manifest.xml:15`. The 256-byte `manifest.sig` also verifies as RSA PKCS#1 v1.5 with SHA-256 over the exact `manifest.xml` bytes using `publickey.cer`.

The certificate visible in that wrapper is:

| Field | Value |
|---|---|
| Subject | `CN=VP4R_RUN_Signing,O=FCA US LLC,L=Auburn Hills,ST=MI,C=US` |
| Issuer | `CN=FCA_MPK2_ROOTCA_V2,O=FCA US LLC,L=Auburn Hills,ST=MI,C=US` |
| Validity | 2012-01-01 through 2066-05-25 UTC |
| Signature | RSA with SHA-256 |
| Certificate SHA-256 | `b82fb388fbb26308718f6b2d26c1ce1e5c883ee3dce325b2ad05f499f11d6cf4` |

**Classification:** UAS-ONLY.  
**Confidence:** CONFIRMED for byte-level binding and detached-signature verification.  
**Interpretation:** the visible wrapper is cryptographically self-consistent. Verification against an independently trusted FCA root and proof of original distribution remain outside the available evidence.

## UAS full-update metadata

`VP4R_Update/ss_pasa_usb.metadata` identifies:

- line 4: `FULL_UPDATE`;
- line 5: `NN-IR-21.9.0-20180516-I09V`;
- line 6: security version `17.57.00`;
- lines 20-118: nine declared encrypted segments, each with a path, IV, and SHA-256;
- line 127: compression enabled;
- lines 128-129: key-wrapping fields;
- line 136: boot-micro digital signing enabled.

All nine declared segment SHA-256 values were recomputed and matched the metadata. The 256-byte `VP4R_Update/Signature` verifies as RSA PKCS#1 v1.5 with SHA-256 over the exact metadata bytes using `VP4R_Update/publickeycert.pem`.

The metadata signer certificate is:

| Field | Value |
|---|---|
| Subject | `CN=VP4R_FW_Signing,O=FCA US LLC,L=Auburn Hills,ST=MI,C=US` |
| Issuer | `CN=FCA_MPK2_ROOTCA_V2,O=FCA US LLC,L=Auburn Hills,ST=MI,C=US` |
| Validity | 2012-01-01 through 2019-03-16 UTC |
| Signature | RSA with SHA-256 |
| Certificate SHA-256 | `d4ffb034c90d4a23ab313f4126bb6f9f27f481eab4f6170defb2ff4bcc2c6cef` |

The declared update destinations span host application, flash loader, voice/VR, HMI skin, NOR, boot micro, and cellular-modem components. This is a segmented full-device update description, not evidence of an application-level Xlet installer.

**Classification:** UAS-ONLY.  
**Confidence:** CONFIRMED.  
**Alternative explanation:** none for the visible fields; the on-device code that interprets them is not present in decrypted form.  
**Next validation:** analyze the authenticated UAS loader and decrypted user-supplied application segment without modifying the source package.

## Encrypted payload limitation

All 12 files named `encrypted_*.tar.gz` lack the gzip magic bytes `1f 8b`; their suffix does not make them directly extractable gzip archives. The visible metadata supplies distinct IVs for the nine declared segments. The application and HMI runtime content therefore remains opaque in this corpus.

A raw ASCII and UTF-16LE scan covered all 32 non-`encrypted_*` UAS files (93,457,470 bytes), including `second.ifs`, both AR7 firmware packages, scripts, metadata, certificates, and signatures. It found no instances of:

```text
AMS_DEVELOPMENT
securityConfiguration
developerToken
developerId
antiTheft
xlet
/fs/etfs
```

This negative result applies only to accessible outer files. It cannot be used to claim that the encrypted application segment lacks those mechanisms.

**Classification:** UAS-ONLY negative evidence.  
**Confidence:** CONFIRMED for the stated scan scope; no conclusion for encrypted content.

## `second.ifs` behavior and handling warning

The small signed IFS embeds a script at byte offset `0x12c`. Its operations include:

| Offset | Operation |
|---:|---|
| `0x13d` | announces a custom IFS script |
| `0x160` | removes contents below `/fota/` |
| `0x16e` | removes `/pas/rwdata/dm_file_persistence.txt` |
| `0x195` | removes `/pas/rwdata/dm_install_persistence.txt` |
| `0x1c0` | terminates `ss_fota_vdm_client` |

This report intentionally records only short diagnostic descriptions rather than reproducing vendor code. The actions look like update/recovery-state cleanup, but their lifecycle and safety cannot be established without the receiving platform's loader semantics.

**Classification:** UAS-ONLY.  
**Confidence:** CONFIRMED for embedded operations; INFERRED for purpose.  
**Alternative explanation:** the helper may be an official service/recovery wrapper, a repackaged support artifact, or another signed workflow. The string `Custom` alone does not establish origin.  
**Safety consequence:** do not execute, flash, or adapt this helper as an RA4 installation mechanism.

## RA4 versus UAS matrix

| Topic | RA4 18.45.01 | Available UAS 21.9 evidence | Label / conclusion |
|---|---|---|---|
| Source provenance | Owner ZIP present; SHA-256 `5388d9310737dc52a65f2825131043362254b3592da2584302b81bc0447f9fdd` | Parent package absent | RA4-CONFIRMED; UAS UNKNOWN provenance |
| Update container | `swdl.upd` with materialized `installer.iso`, `primary.iso`, and `secondary.iso` | Signed SAM wrapper plus signed XML and encrypted segments | Independently confirmed; formats differ |
| Runtime filesystem visibility | Primary and secondary trees are inspectable | Application/HMI payloads are encrypted | Comparison blocked on UAS side |
| AMS startup | `jvm.sh` invokes AMS with `-secure` and `-securityConfiguration` | Not visible | RA4-CONFIRMED; UAS UNKNOWN |
| Development selector | `/fs/etfs/AMS_DEVELOPMENT` selects development `security.jar` | No accessible equivalent reference | RA4-CONFIRMED; UAS UNKNOWN, not absent |
| Production/development security JARs | Both are present and compared deterministically | Not visible | RA4-CONFIRMED; UAS UNKNOWN |
| Developer token | RA4 token-bearing signed descriptors and AMS names are recovered; standard RSA v1.5/PSS verification under all recovered compatible keys is ruled out, while the exact caller/operand/format remains unknown | Not visible | RA4 evidence only |
| Anti-theft/PIN path | RA4 keypad/HMI/gateway/channel-2 path, IOC comparison/success branch, and asynchronous unlock-state publication are traced; comparator provenance and retry/lockout policy remain protected unknowns | Not visible | No cross-generation inference allowed |
| Xlet/Application Manager | RA4 Kona and Xlet trees are inspectable | Not visible | RA4 evidence only |
| Detached outer signatures | RA4 update has its own manifest/signature scheme | Two UAS RSA/SHA-256 detached signatures verify | SHARED concept, generation-specific realization |
| Per-payload integrity | RA4 installer manifests/checks are generation-specific | Nine XML-declared UAS segment hashes match | SHARED concept, not interchangeable format |
| Persistent update state | RA4 ETFS/update state is separately documented | UAS helper removes two `/pas/rwdata/dm_*_persistence.txt` files | Different path/model; purpose only INFERRED |

## Requested comparative questions

### Developer Mode and `securityConfiguration`

**UAS status: UNKNOWN.** No UAS runtime script, AMS binary, security JAR, or decrypted application filesystem is available. Absence from the outer wrapper is not meaningful negative evidence.

### Development policy and trust

**UAS status: UNKNOWN for Kona/application policy.** The two visible UAS signer certificates authenticate the outer SAM wrapper and full-update metadata. They do not establish Xlet signer trust, `key.jar` behavior, or development permissions.

### Anti-theft authorization and developer token

**UAS status: UNKNOWN.** Neither UI nor backend implementation is accessible. No RA4 control-flow arrow is strengthened merely by the UAS update metadata.

### AMS and Xlet installation

**UAS status: UNKNOWN.** The encrypted `Application` segment may contain relevant code, but no lawful decryption/materialization evidence is present. The visible `FULL_UPDATE` pipeline should not be conflated with an application-level install API.

### USB/update mechanism

**UAS-ONLY confirmed:** signed SAM manifest, signed full-update metadata, encrypted segmented payloads, per-segment IV/hash fields, and an authenticated helper IFS.  
**RA4-CONFIRMED:** visible `swdl.upd` and three-ISO architecture.  
**INFERRED shared principle:** both generations authenticate structured update metadata and verify payload integrity. Their package layouts and on-device interpreters are not interchangeable.

## Applicability to the RA4 design

The UAS corpus does not justify a later-generation shortcut for RA4 Developer Mode. It does reinforce three conservative design rules:

1. Keep generation-specific update formats separate.
2. Treat update metadata, signatures, and payload hashes as an authorization boundary, not a nuisance to bypass.
3. Prefer RA4's already-present, authenticated factory state transition over adapting a UAS full-update wrapper.

No UAS file was executed, decrypted, modified, or repackaged during this analysis.

## Highest-value next validation

1. Acquire and hash the owner's original UAS 21.9 package to restore provenance.
2. Reproduce extraction and record a complete per-file manifest.
3. Use an authorized platform-supported method, if available, to inspect the application payload; do not derive or publish protected update keys.
4. Only then search UAS runtime content for AMS startup, development state, anti-theft callbacks, developer tokens, and application management.
5. Keep all resulting UAS statements explicitly generation-scoped until independently matched in RA4.

## Git/vendor-material status

The UAS tree is stock/vendor-bearing local research input and is ignored by `/analysis_uas_21.9/`. This report contains original analysis, hashes, metadata descriptions, and small diagnostic excerpts only. No UAS binary, certificate, signature, encrypted segment, or decompiled vendor source was copied into `reports/`.

**Stock/vendor firmware staged: NO.**
