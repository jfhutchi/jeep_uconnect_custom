# RA4 Production and Development `security.jar` Diff

## Scope and safety boundary

This report compares the two factory security-configuration JARs already present in the owner-supplied RA4 18.45.01 extraction. The source files were read in place. They were not modified, copied into this report, executed, staged, or repackaged.

Canonical extracted paths:

- Production: `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/security/security.jar`
- Development: `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/security/development/security.jar`

Runtime paths selected by `jvm.sh`:

- Production: `/fs/mmc1/kona/security/security.jar`
- Development: `/fs/mmc1/kona/security/development/security.jar`

## Artifact identity

| Variant | Size | SHA-256 |
|---|---:|---|
| Production | 7,504 bytes | `29a8a350ef0facc30c1c98e5250563a4020ad9c1a243f13e795e2e68e3bd74e7` |
| Development | 7,371 bytes | `fbe5314ab304e122162aae20ace46999b93832fc4c7451439f4ada430eccc8a7` |

These identities match `RA4_RESEARCH_HANDOFF_CURRENT_FINDINGS.md` and the existing extracted-file inventory.

## Method

The current verification pass used Python's standard-library `zipfile`, `hashlib`, and `base64` modules to:

1. enumerate every ZIP entry without extracting it;
2. hash each uncompressed entry with SHA-256;
3. compare entry sets, sizes, CRC-32 values, timestamps, and contents;
4. recompute every SHA-1 entry digest recorded in `META-INF/MANIFEST.MF`; and
5. parse PKCS#7 signer certificates with `cryptography` without attempting to recover private keys or alter trust.

All seven manifest entry digests recomputed correctly in both JARs. This validates the manifest-to-payload digest layer, but it is not a claim that the original RA4 runtime's complete signer-validation path has been reproduced.

## Container and entry comparison

Both JARs contain 17 entries including directory entries. Their functional entry sets are the same:

- `com/aicas/xlet/manager/Device.class`
- `base.policy`
- `complete.policy`
- `full.policy`
- `security.properties`
- `xlet.security`
- `xletmanager.policy`

Both also contain the shared aicas signer records:

- `META-INF/AICASFOR.SF`
- `META-INF/AICASFOR.DSA`

The variant-specific signer records differ:

| Production only | Development only |
|---|---|
| `META-INF/CVP_APP_.SF` | `META-INF/DEVELOPM.SF` |
| `META-INF/CVP_APP_.RSA` | `META-INF/DEVELOPM.RSA` |

ZIP timestamps and signature/manifest bytes differ as expected from the different build times, signer blocks, and `security.properties` value.

## Runtime payload comparison

The following entries are byte-for-byte identical:

| Entry | SHA-256 |
|---|---|
| `com/aicas/xlet/manager/Device.class` | `a452ac3005bbf0bdf18c7dd6d8fed766f7d130524170b4cfbae037efb2edc6e8` |
| `base.policy` | `3f2374537e315ce9358e7cff5c9ab08a93a1fd9708fcfa739121e2d2556b72cd` |
| `complete.policy` | `82059f870a65e76465b1da1948e7eaed83cfbb2e3cc33dcef0ecd9a94980b71c` |
| `full.policy` | `623e870a36dea05b9c5c33b16ccb68bf77a66675d008a2f6d46aa5e859bb2a14` |
| `xlet.security` | `4548fe2fe801f33588932a009aeddc1943f23bad06debccefa8ec2795b2f6c0b` |
| `xletmanager.policy` | `82059f870a65e76465b1da1948e7eaed83cfbb2e3cc33dcef0ecd9a94980b71c` |

The only functional resource difference found is `security.properties`:

| Property | Production | Development |
|---|---:|---:|
| `security.version.major` | `3` | `3` |
| `security.version.minor` | `0` | `0` |
| `security.version.revision` | `13` | `17` |
| `platform.vendor` | `fiat` | `fiat` |

The comment timestamp in that file also differs. Its SHA-256 is `250232ccbe6aea045af42eba592c1a3968b22cb00b07af66eacdfb3112b81a6c` in production and `85254e9e06c6c45f536d35e260afa194925c7ef99e35f42374642470913b2889` in development.

The shared 481-byte `Device.class` has the same constant pool in both variants. Its relevant constants name `java/security/Security.setProperty` and `networkaddress.cache.ttl`; no PIN, anti-theft, Developer Mode, developer-token, or `AMS_DEVELOPMENT` string is present. The historical handoff's `javap` result further records that its static initializer sets the DNS cache TTL to zero.

## Signer comparison

| Variant/role | Subject | Certificate SHA-256 | Validity recorded in certificate |
|---|---|---|---|
| Production primary | Chrysler UConnect Application CA | `9ebf781bd18ad8c1f33b5b4727a2bed922b6cd4fb9680250a30de68045f3f546` | 2012-05-21 through 2032-05-16 UTC |
| Development primary | Xlet Developer | `42a6e60121e81a065c6dc0f2e5cc33edd51405d93444e0b4ca292379871039a0` | 2013-12-27 through 2023-12-25 UTC |
| Shared secondary | aicas GmbH | `9f28ad4b65f3eca46049b9f6abfb5c169b8c1ea35dde01380c689dbceab10d4c` | 2011-10-19 through 4749-09-14 UTC |

All three certificates are self-issued according to their embedded subject and issuer fields. Certificate dates alone do not prove how the older RA4 runtime handled time or algorithm policy.

## Findings

### Finding: policy grants do not change between variants

**Confidence:** CONFIRMED

**Evidence:** The six class/policy entries above have identical SHA-256 values in both canonical JARs.

**Interpretation:** Switching to the development JAR does not select a visibly broader policy-file payload. The observable semantic inputs that change are the security revision and signer identity/signature metadata.

**Alternative explanation:** AMS or another Kona component may interpret the signer identity or revision as a mode discriminator not visible in the policy text.

**Resolved trust-bootstrap edge:** `AMSController` first derives `_internalKeys_` from signer certificates on `rom:/internal.jar!/xlet.security`, uses those keys in a temporary loader for the selected security JAR, then promotes every certificate/public key attached to that JAR's `xlet.security` into the final `SecurityParameter.signingKeys`. The embedded first-stage JAR is AMS file `[0x988778,0x9892AD)`, SHA-256 `2dbf7986c70e16d7bb047b897492c6ce164a1b5954837590708ee65b73759dab`; its verified signers are aicas DSA certificate SHA-256 `9f28ad4b65f3eca46049b9f6abfb5c169b8c1ea35dde01380c689dbceab10d4c` and aicas RSA certificate `0654d97249cd24168cffbd7987ba6a05b76550dc95d765a9dafc59aaf11afe07`. All four variant `.SF` records explicitly cover `xlet.security`. Production therefore promotes Chrysler plus aicas candidates; development promotes Xlet Developer plus aicas. Revision-to-policy and signer-to-principal mapping remain unresolved.

### Finding: the security bundle is not the observed PIN implementation

**Confidence:** CONFIRMED for the recovered RA4 control graph

**Evidence:** The only class is identical in both variants and has no authentication-related constants; all other functional entries are policy/configuration resources. The recovered anti-theft receiver is instead `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/onoff/main.lua`: function 28, source/debug lines 1116-1126, forwards the four input bytes to IOC IPC channel 2, and function 23, lines 687-1055, later maps IOC state/counter/lock-time fields. No development-security operation occurs on that path.

**Interpretation:** The anti-theft PIN gate is independent of the stock Development Security selector. It must remain untouched rather than being repurposed as a developer credential.

**Alternative explanation:** Generic policy behavior can still influence application capability after package authentication, but no PIN-validation implementation or PIN-to-development edge is present in this bundle or the recovered Linux/QNX authorization graph.

**Resolved token decision:** `SignedId` Base64-decodes `xlet.developerToken`; for the promoted RSA primary key, RA4's JCE implementation selects SunJCE `RSA/ECB/PKCS1Padding`, public-decrypt/internal-verify mode, and PKCS#1 v1.5 type-1 unpadding, then requires exact equality with runtime `developerId`. The update corpus supplies no usable ID provider. Remaining validation is the live overlay/legitimate issuer and policy-combination decision.

### Finding: the development JAR is a distinct factory-signed configuration

**Confidence:** CONFIRMED

**Evidence:** It is shipped in the stock extraction, is selected by the stock `jvm.sh`, and carries a distinct `Xlet Developer` signer plus revision 17.

**Interpretation:** The stock firmware contains an intentional development security configuration. The stock ROV/RU Apps List UI creates or deletes `/fs/etfs/AMS_DEVELOPMENT` in `AppsListEngServiceMenu::DevepSecurityKeyEnabled` (reconstructed FWS offset `0x3899D`), after a signed, HU-serial-bound, unexpired service certificate exposes the Service item. Modifying either JAR is not justified by current evidence.

**Alternative explanation:** This remains a manufacturing/service authorization path rather than a general owner-facing feature: the corresponding service-certificate issuing/provisioning process is not present in the corpus.

**Next validation:** Establish the legitimate service-certificate provisioning route, runtime ID/credential issuer, and exact permission mapping for the development-promoted signer set. The provider transformation/padding question is closed by `reports/signedid_jce_semantics.md`.

## Current conclusion

No policy or Java-code patch is indicated. The safe future design preserves both factory JARs byte-for-byte, uses only a legitimately provisioned service certificate and the stock item-19 marker owner, retains AMS `-secure`, and performs a normal controlled restart so `jvm.sh` can resample the marker. Native AppManager now proves the normal success-path removal of per-app Xlet resources, RMS directory/shared record, and native map entry; exhaustive ownership, transaction atomicity, interruption recovery, and prior-version restoration still require dynamic validation. The live single-JAR member schema and AMS split are proved, but implementation remains stopped until authorized signer/developer-token issuance and acceptance, those uninstall safety properties, and production-return access are proved.
