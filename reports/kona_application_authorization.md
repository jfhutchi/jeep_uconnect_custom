# RA4 Kona application authorization chain

## Scope and safety boundary

This report integrates the application-package, signer, DRM, policy, Java API, SvcIPC, and ROMized AMS evidence in the owner-supplied RA4 18.45.01 extraction. The work was static and read-only. No target executable was run, no firmware image or vendor archive was modified, and no credential, private key, anti-theft PIN material, or bypass procedure is reproduced.

Offsets into `AMS` are file offsets. Addresses in native `appManager` and `authenticationService` are ELF virtual addresses unless explicitly labeled as file offsets; the first `appManager` load maps file offset zero at `0x100000`. Offsets into a `.class` below are offsets in the decompressed class-file member, not offsets in `kona.jar`. JAR signature verification used stock archive bytes and a temporary directory outside the extracted firmware tree.

Evidence grades used here:

- `CONFIRMED`: directly reproduced from the named artifact.
- `HIGH`: the artifacts strongly support the edge, but the executing native method was not recovered.
- `UNKNOWN`: compatible with the evidence, but no call or data edge has been proved.

This report extends, and should be read with:

- `reports/kona_trust_model.md`
- `reports/developer_token_analysis.md`

## Executive result

The RA4 application code JARs are not self-signed, but they are not unsigned in the authorization sense. The companion `key.jar` is a detached JAR-signature carrier:

```text
application JAR entry bytes
  -> digest records in key.jar!/META-INF/MANIFEST.MF        CONFIRMED
  -> full-manifest digest in key.jar!/META-INF/*.SF         CONFIRMED
  -> PKCS#7 signature in key.jar!/META-INF/*.RSA             CONFIRMED, signature math
  -> embedded production application certificate            CONFIRMED
  -> AMS fixed key.jar association and signer-object source   CONFIRMED
  -> AOT certificate/key match and principal decision         PARTLY UNKNOWN

key.jar!/xlet.properties
  -> same manifest/signature chain                           CONFIRMED
  -> appId, main class, policy names, and developerToken     CONFIRMED signed metadata

DRM.jar!/xlet.properties
  -> its own manifest/.SF/.RSA chain                         CONFIRMED
  -> signed grantList keyed by appIdentifier                 CONFIRMED
  -> installer type, feature and launcher masks, VIN/date    CONFIRMED metadata fields

Java AppManager API
  -> AppMgrPermission("appMgr")                              CONFIRMED
  -> SecurityManager.checkPermission                         CONFIRMED when a manager exists
  -> SvcIPC com.harman.service.AppManager                    CONFIRMED
  -> native DRM grant check                                  CONFIRMED call site and default-on flag
  -> AMS getPackageInfo({uri, auth:true})                     CONFIRMED native delegation
  -> AMS fixed key.jar/signature-object association            CONFIRMED direct call order
  -> AOT certificate extraction and SigningKeys match          UNKNOWN implementation details
  -> AMS policy/principal assignment                          UNKNOWN exact call order
  -> launch outcome                                           CONFIRMED API/result boundary
```

The most important correction to the earlier preliminary model is therefore:

> `key.jar` signs both the embedded application descriptor and every regular file in the separately stored executable JAR. It is not merely an identity certificate or a signature over `xlet.properties`.

The remaining trust gap is no longer how executable bytes are bound to a signer, how installed AMS finds the companion, or which signed property reaches the developer branch. `Installer` constructs the fixed sibling path, `VerificationClassLoader` obtains signer objects from `key.jar!/xlet.properties`, and `verifyDeveloperKey` consumes the signed `xlet.developerToken`. The remaining gap is the AOT certificate-extraction/key-match implementation, which principal and policy rule follows a successful decision, and how an authorized issuer supplies the otherwise absent runtime developer ID and matching credential.

The hidden-HBC native evidence also closes an important false lead: in this exact `appManager`, boot's `-d` argument is not a registered option and is caught as an unknown option. The actual DRM checker subobject initializes enabled. Therefore `-d` must not be described or used as a proved DRM-disable control for RA4 18.45.01.

## Core artifact identities

| Artifact | Size | SHA-256 |
| --- | ---: | --- |
| `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/AMS` | 11,956,352 | `96683b789ecf06a8575915d0b446b532e1f4ee87feb31d925cb7ba3d7d324d27` |
| `analysis_ra4_18.45.01/work/primary_iso/usr/share/IFS/ifs-cmc.bin` | 42,122,670 | `ea6797be141763f35f3059ad858eefbf54f730af0155bebc7af411c47d80ba92` |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/files/bin/boot.sh` | 29,268 | `c801d473b0b49e8242114635f4022cc67ccbe03093fec188de3b7188dd636ecf` |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/bin/appManager` | 1,268,061 | `608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591` |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/etc/system/config/appManager.cfg` | 5,802 | `ab9ed180574d2c9f83c45217f05b132af24abd364ecf59c8447d1ba0cdb9c2d7` |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/platform_ams_restart.lua` | 7,514 | `264e5aaa6e2e09e8bb86a881f4919a66220d1cad2c7ce9443416e5d35f9f720f` |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_019a0000/files/usr/bin/authenticationService` | 273,340 | `9c7c057fbffceb2dc0b77690b6eb07dcd90721de6f89c5a05150fa18cea84699` |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/etc/system/config/authenticationServiceKeyFile.json` | 11,359 | `5968ff07dba7a0316a7fc76687cbef5147699d96538d14a10def0bfd5211ad11` |
| `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/lib/kona.jar` | 3,062,680 | `19390472018f02d998690b982f00eb68da5d40d7a8d6fba91499677651015f92` |
| `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/security/security.jar` | 7,504 | `29a8a350ef0facc30c1c98e5250563a4020ad9c1a243f13e795e2e68e3bd74e7` |
| `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/security/development/security.jar` | 7,371 | `fbe5314ab304e122162aae20ace46999b93832fc4c7451439f4ada430eccc8a7` |

Representative application tuple, all beneath `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/`:

| Member | Exact evidence |
| --- | --- |
| Installed descriptor | `kim_packages/KIM1/xlets/079aa169-df8f-48b4-b331-4ed51dbf6b12/prog/xlet.properties`; 1,638 bytes; SHA-256 `7319c16b876610a6c9b2fbeb40164b791a8ae1c5ec839ae38b2a9f3fb13ac430` |
| Detached signature carrier | `kim_packages/KIM1/xlets/079aa169-df8f-48b4-b331-4ed51dbf6b12/prog/jars/key.jar`; 27,207 bytes; SHA-256 `faccde0e49150c883d2f7a247987ba48d20e90b5966bfdab9556ab70d8cf0e49` |
| Signed descriptor member | `key.jar!/xlet.properties`; SHA-256 `3f4dc532c46eb276234e8ec826336d84c8724f50fb9ea1e3a1cc61076333ab63` |
| Executable content | `kim_packages/KIM1/xlets/079aa169-df8f-48b4-b331-4ed51dbf6b12/prog/jars/079aa169-df8f-48b4-b331-4ed51dbf6b12.jar`; 1,558,076 bytes; SHA-256 `382026942a6cde768c4c3762497523c3300a5c3fa101d8661b2b0dfacfe3b260` |
| DRM grant carrier | `kim_packages/KIM1/DRM.jar`; 3,484 bytes; SHA-256 `0a4cb4ead688547658a7ac5d0beecd0b242c36aa5bdf0f1f887cad5707f06ad2` |
| Signed DRM member | `DRM.jar!/xlet.properties`; 6,375 bytes; SHA-256 `57f3f994c25e4653bf1722ef0e2470684ea4528d7c80e55ec145876b0c47e35c` |

## Corpus-wide package shape

A traversal rooted at `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages` found:

- 27 numbered KIM directories.
- 26 KIM directories containing installed Xlet descriptors.
- 135 `xlets/*/prog/xlet.properties` descriptors.
- 135 corresponding `prog/jars/key.jar` files.
- 135 corresponding executable JARs named by the installed `xlet.jarFile` property; all exist.
- 26 `DRM.jar` files. KIM7 has a DRM JAR and no extracted Xlets; KIM3 has extracted Xlets and no DRM JAR.

Every `key.jar` contains standard `META-INF` manifest/signature material and an embedded `xlet.properties`; none contains a `.class` member. Every referenced executable JAR contains code, but the corpus has zero `.RSA`, `.DSA`, or `.EC` signature blocks in those 135 executable JARs and zero per-entry digest records in their own manifests.

That apparent separation is intentional: the signing metadata for the executable JAR is stored in `key.jar`.

## `key.jar` is the detached executable signature

### Complete content binding

For each application, the following association was made only from the installed descriptor and sibling paths:

1. Read `prog/xlet.properties`.
2. Resolve `xlet.jarFile` under the sibling `prog/jars/` directory.
3. Open sibling `prog/jars/key.jar`.
4. Parse and unfold `key.jar!/META-INF/MANIFEST.MF` according to JAR manifest continuation-line rules.
5. Resolve every manifest `Name` first against `key.jar`, then against the associated executable JAR.
6. Recompute the declared SHA-1 or SHA-256 digest over the exact uncompressed member bytes.

Results:

| Measurement | Result |
| --- | ---: |
| Applications checked | 135 |
| Regular files in associated executable JARs | 78,756 |
| Regular executable-JAR files covered by the companion key manifest | 78,756 |
| Uncovered regular executable-JAR files | 0 |
| Manifest entry-digest records resolving to executable-JAR members | 82,795 |
| Manifest entry-digest records resolving to retained `key.jar` members | 143 |
| Total entry-digest records recomputed | 82,938 |
| Matching digests | 82,938 |
| Missing named members | 0 |
| Digest mismatches | 0 |

The record count exceeds the regular-file count because some members have more than one declared digest algorithm. Coverage was also checked by unique regular member name; all 78,756 were present in the relevant key manifest.

For the representative Vehicle User Guide tuple above, the key manifest has 386 digest records and all 386 resolve and match. For sibling HelpDaemon application `4c74b232-3360-42ff-a05f-d098ba85b220`, its key manifest has 308 matching records.

### Manifest-to-signer binding

The next two links were independently checked:

- All 137 `META-INF/*.SF` files in the 135 key JARs carry a SHA-1 digest of the complete corresponding `MANIFEST.MF`; 137 of 137 recompute exactly.
- Each `.SF` has a corresponding PKCS#7 `.RSA` signature block. OpenSSL 3.5.7 `cms -verify -binary -inform DER ... -content ... -noverify` accepted all 137 of 137 signatures.

`-noverify` is deliberate. It proves that the PKCS#7 signature value matches the stock `.SF` payload and embedded signing certificate. It does not reproduce AMS certificate-chain, expiry, revocation, principal, or trust-anchor decisions.

The confirmed content chain is therefore:

```text
all executable JAR files + key.jar!/xlet.properties
  -> key.jar manifest entry digests
  -> .SF full-manifest digest
  -> .RSA PKCS#7 signature
  -> embedded signer certificate
```

### Production signer identities

Signer membership among the 135 `key.jar` files:

| Signer certificate SHA-256 | Key JARs | Notes |
| --- | ---: | --- |
| `9ebf781bd18ad8c1f33b5b4727a2bed922b6cd4fb9680250a30de68045f3f546` | 123 | Chrysler UConnect Application CA |
| `108755c1180f00d64192e123466d806eba48631924aa0135009b80323cb4170a` | 12 | VP4 Application; ten are single-signer and two are dual-signed |
| `337af8c28a24f4f1ac3c13b25dfb535335521d6273aef90ade650ab7786d62aa` | 2 | Additional certificate in the two VP4 dual-signed JARs; identified as Accenture in `kona_trust_model.md` |

The stock `Xlet Developer` certificate found in the development `security.jar` occurs in no application `key.jar` in this corpus. That is a confirmed corpus fact, not proof that development mode cannot accept a different packaging form.

## Signed descriptor versus installed descriptor

The descriptor retained inside `key.jar` is the signed package descriptor. The filesystem descriptor is an installed/runtime form.

Across all 135 applications:

- The two byte streams are byte-for-byte unequal in 135 of 135 cases.
- A Java-properties parser found complete semantic equality in 6 of 135 cases.
- `xlet.appId`, `xlet.mainClass`, `xlet.vendor`, `xlet.name`, `xlet.policy`, and `xlet.policy.default` agree wherever present in 135 of 135 pairs.
- `xlet.developerToken` agrees in all six pairs that contain it and is absent from both sides in the other 129.
- `xlet.jarFile` agrees in 6 pairs and differs in 129. The installed form commonly rewrites a build/source name to an installed UUID or package filename.

Representative Vehicle User Guide evidence:

- Installed descriptor `.../KIM1/xlets/079aa169-df8f-48b4-b331-4ed51dbf6b12/prog/xlet.properties`: app ID line 15, `xlet.policy.default` line 18, main class line 19, `xlet.policy` line 21, installed `xlet.jarFile` line 24.
- Signed `key.jar!/xlet.properties`: the signed JAR filename is `Help.jar`, while the installed filename is `079aa169-df8f-48b4-b331-4ed51dbf6b12.jar`.
- Both descriptors identify the same app ID, main class, policy names, and developer-token value after Java-properties unescaping.

This proves that normal installation may rename the executable container without changing the signed internal member set. It also means bytewise comparison of the installed descriptor to the signed descriptor is not a valid authenticity test.

The exact native rule that chooses which descriptor copy is authoritative at install and launch is not recovered. The presence of both forms and the complete signature over the embedded form strongly support the embedded copy as the authentication source and the filesystem copy as normalized installed state, but that choice remains `HIGH`, not a recovered call edge.

### Java descriptor consumers

The inspectable Kona Java layer confirms that runtime code reads normalized application properties, but it does not contain the signer verifier:

| Class/member in `base/kona/lib/kona.jar` | Exact evidence |
| --- | --- |
| `kona/xlet/XletInfo.class` | 5,178 bytes; SHA-256 `d2526c884d62f3708daed4949e68b0944ea19a0219d195f62ca799f461b0ef36`; constant-pool record `0x787` is `xlet.appId`, `0x91A` is implementation class `com.harman.xlet.XletInfoImpl`, and `0x94C` is `/xlet.properties` |
| `XletInfo.getProperties(Class)` | code starts at class-file offset `0xE24`, length 42 |
| `XletInfo.getAppId(Xlet)` | code starts at `0xF31`, length 16 |
| `XletInfo.getDataDirectory(Class)` | code starts at `0xF89`, length 42 |
| `com/harman/utils/PlatformUtils.class` | 6,527 bytes; SHA-256 `05130401aef0c8bc15c90c59587c15e9b1373f011145905021fe0d89bc31965d`; constant-pool records `0x8F2`, `0x947`, `0x954`, and `0x960` hold `/xlet.properties`, `xlet.appId`, `xlet.name`, and `xlet.vendor` |
| `PlatformUtils.loadProperties()` | code starts at `0x1379`, length 123 |
| `com/harman/service/appManager/AppManagerService.class` | 2,073 bytes; SHA-256 `4482027fd1e2767273f6354e81f571dc337a4a5123f382e1d5372500639fdd1a`; constant-pool record `0x16F` is service operation `getXletPropsbyName` |
| `AppManagerService.getXletPropsbyName(String)` | code starts at `0x671`, length 65, and uses a `SvcIpcClient` return type recorded at constant-pool offset `0x206` |

`AppManagerImpl.class` also contains installed-tree constants `/fs/mmc1/xletsdir/xlets/` at constant-pool record `0x1D9F`, `/fs/mmc1/apps/` at `0x1DC2`, and `/fs/mmc1/resource` at `0x1DE8`.

These classes prove property access and service lookup after installation. Exact searches of their decompressed class data found no `developerToken`, `getDeveloperToken`, or `verifyDeveloperKey` constant; those names remain confined to the ROMized AMS evidence in the inspected platform JAR/binary set.

## `DRM.jar` is a separately signed entitlement list

Each of the 26 `DRM.jar` files contains a signed `xlet.properties` and no application classes. Its `xlet.amsDRM` value is JSON with a top-level `grantList`. Individual grants include:

- `appIdentifier`
- `fileName`
- `fileLength`
- `fileChecksum`
- `installerType`
- `featureMask`
- `appLauncherMask`
- version and expiry fields

The DRM signature chain was separately verified:

| Check | Result |
| --- | ---: |
| DRM JARs | 26 |
| Manifest entry digests over `xlet.properties` | 26 matching, 0 mismatch |
| `.SF` full-manifest digests | 26 matching, 0 mismatch |
| PKCS#7 signatures over `.SF` | 26 valid, 0 failure |

Twenty-two DRM JARs carry the Chrysler UConnect Application CA certificate fingerprint `9ebf...f546`; four carry VP4 Application fingerprint `1087...70a`.

### Grant-to-application correlation

The 26 DRM JARs contain 136 grants. Matching by case-insensitive `appIdentifier` within the same KIM directory gives:

- 131 grants matched to 131 of the 135 extracted application descriptors.
- All 131 matched grants have `installerType=DRM_SYNC`.
- Matched `featureMask` distribution: 99 value `2`, 23 value `1`, 6 value `6`, and 3 value `64`.
- Matched `appLauncherMask` distribution: 99 value `0` and 32 value `6`.
- 103 of the 131 grant filenames equal the installed `xlet.jarFile`; only 11 equal the signed descriptor's source/build `xlet.jarFile`.

Four extracted applications have no same-KIM grant:

- KIM1 app `1efb8b70-1ab5-11e1-bddb-0800200c9a66`.
- The three KIM3 applications; KIM3 has no DRM JAR.

Five grants have no extracted application in the same KIM:

- The sole KIM7 grant; KIM7 has no extracted Xlet directory.
- KIM15 app IDs `100` and `999`.
- KIM25 app IDs `7DEC7834-535D-47B5-BD33-695477EDCD57` and `52c79381-6719-11e1-b86c-0800200c9a66`.

These mismatches show that a KIM payload may carry a regional/model entitlement set that is not identical to its extracted Xlet set. They do not by themselves show an authorization failure.

No one of the 136 grants has a non-null `fileChecksum`. Of 125 matched applications whose grant has a non-null `fileLength`, zero lengths equal the extracted executable JAR size. The DRM filename and length therefore describe an installer/package representation, not the installed executable JAR bytes. Executable integrity is instead established by the companion key-manifest signature chain.

For the representative Vehicle User Guide:

- DRM app identifier matches `079aa169-df8f-48b4-b331-4ed51dbf6b12`.
- DRM filename is `IVHClient_v1.0.4-FIT.jar`, length 1,590,554, installer type `DRM_SYNC`, feature mask `2`, launcher mask `0`.
- Signed descriptor filename is `Help.jar`.
- Installed executable filename is `079aa169-df8f-48b4-b331-4ed51dbf6b12.jar`, size 1,558,076.

The three filenames are different identities at three package stages. Joining them by filename alone is unsafe; `appIdentifier` plus the signed key-manifest member set is the stronger relation.

## Developer token is signed package metadata

`reports/developer_token_analysis.md` identifies six installed descriptors: Vehicle User Guide and HelpDaemon in KIM1, KIM12, and KIM16. The opaque value is not reproduced here.

New evidence from the package-signature correlation establishes:

1. Each of the six matching `key.jar!/xlet.properties` members contains the same semantic `xlet.developerToken` value as its installed descriptor.
2. The embedded descriptor's entry digest matches its `key.jar` manifest.
3. The full key manifest matches the `.SF` digest.
4. The PKCS#7 signature over the `.SF` verifies.
5. All six key JARs use the Chrysler UConnect Application CA signer, not the stock `Xlet Developer` security-configuration signer.

A read-only recovered-key census adds a strict negative boundary. Across 300 JARs, 163 signed JARs, 167 embedded-certificate occurrences, seven Kona `cacerts` certificates, the duplicate OTA CA file, and six public-only RSA artifacts, SPKI deduplication yields 19 candidate identities: 17 RSA and two non-RSA. Fifteen RSA identities are 2048-bit and size-compatible with the 256-byte token; the other two RSA keys are too short. Raw public recovery under all 15 compatible keys and both whole-token byte orders yields zero valid PKCS#1 v1.5 envelopes, zero recognized `DigestInfo` values, and zero strict RSA-PSS encoded-message structures under the tested digest and MGF1 parameterizations.

The bounded verification matrix used 332 descriptor, identity, digest, certificate, and SPKI-derived message forms; MD5, SHA-1, SHA-224, SHA-256, SHA-384, and SHA-512; all 15 token-length-compatible keys; and both byte orders. Each digest was tested with PKCS#1 v1.5, while PSS independently enumerated all 36 ordered message-hash/MGF1-hash pairs across the six digests. The exact matrix was 30 compatible key/order cases x 332 messages x (6 v1.5 + 36 PSS pairs) = 418,320 comparisons. Every comparison failed, while in-memory positive controls recognized valid SHA-256 v1.5, same-hash PSS, and PSS with a different MGF1 digest. Important tested keys include the token-bearing Chrysler signer (SPKI SHA-256 `834fd5e4342e84006b535c5e491d179ad9ba14428672f8e29246bbbca26a7ff2`) and stock Xlet Developer signer (`8892b57c000132771f940148a618a06777d8e5bed1dec6f0b377570378e48db8`). This rules out only those enumerated v1.5/PSS parameterizations under recovered compatible RA4 keys, not every RSA construction. No raw token, PEM, modulus, recovered block, or private material was emitted.

This changes the edge ledger as follows:

| Edge | Grade | Exact basis |
| --- | --- | --- |
| application signer -> `xlet.developerToken` bytes | `CONFIRMED` | token is in `key.jar!/xlet.properties`; its manifest digest, `.SF` manifest digest, and PKCS#7 signature all verify |
| developer token -> executable member set | `CONFIRMED` common signed envelope | token-bearing descriptor and every executable member are covered by the same signed key manifest |
| developer token -> application/vendor scope | `HIGH` | two Tweddle app IDs reuse one value across KIM1/KIM12/KIM16; value is package-static and signer-bound |
| anti-theft PIN success -> token creation | `UNSUPPORTED/UNKNOWN` | no such state or call edge exists; stock packages already contain the signed token |
| `verifyDeveloperKey` -> this descriptor token | `CONFIRMED` | `VerificationClassLoader.getDeveloperToken` reads exact property `xlet.developerToken`; its private verifier passes that value to `KeyVerifier.verifyAllCertificates`, which calls `verifyDeveloperKey` first |
| token -> decrypted developer identity | `CONFIRMED` | `SignedId` Base64-decodes the token; RA4 SunJCE resolves RSA to `RSA/ECB/PKCS1Padding`, public-decrypt/internal-verify mode, and type-1 unpadding; the resulting default-charset string must equal `developerId` exactly |
| `rom:/internal.jar` -> selected-security-JAR trust | `CONFIRMED` | signer public keys from `rom:/internal.jar!/xlet.security` populate `_internalKeys_` and parameterize the temporary selected-JAR loader |
| development `security.jar` -> altered token key candidates | `CONFIRMED` | certificates on selected `xlet.security` are promoted into final signing keys: production Chrysler+aicas versus development Xlet Developer+aicas |
| recovered RA4 public key -> tested RSA v1.5/PSS signature interpretations | `CONFIRMED ABSENT` | all 15 token-length-compatible RSA identities, both byte orders, six v1.5 hashes, and all 36 PSS message-hash/MGF1-hash pairs fail strict structure and the bounded 418,320-comparison matrix |

The safe interpretation is now exact on the consumer side: `xlet.developerToken` is a Base64 ciphertext credential supplied in signed package metadata. For each promoted selected-security-JAR signer key, `SignedId.decrypt` uses `Cipher.getInstance(key.getAlgorithm())`, decrypt mode with the public key, and exact plaintext equality with runtime `developerId`. For the RSA primary candidate, RA4's own JCE classes select SunJCE `RSACipher`, the constructor default `PKCS1Padding`, internal `MODE_VERIFY`, and PKCS#1 v1.5 block type 1; bare `RSA` therefore has the conventional label `RSA/ECB/PKCS1Padding`. It is not a transient result generated by factory anti-theft PIN authentication and is not passed to Java `Signature`. The legitimate private-key issuer, plaintext charset assumption, and runtime ID source remain unresolved; no stock token may be copied or replayed.

The continuous AMS pool contains bare field name `developerId` at `0xA72B3C`, getter `getDeveloperId` at `0xA78AE5`, bare field `developerToken` at `0xA72B42`, and getter `getDeveloperToken` at `0xA78AF0`. Class-object metadata assigns `developerId` to `SecurityParameter` and `developerToken` plus `getDeveloperToken()String` to `VerificationClassLoader`; the direct call graph is reconstructed below.

## Policy selection and permission assignment

### Global policy index

Both production and development security JARs contain byte-identical policy resources. In production `security.jar`:

| Member | Size | SHA-256 | Relevant evidence |
| --- | ---: | --- | --- |
| `xlet.security` | 107 | `4548fe2fe801f33588932a009aeddc1943f23bad06debccefa8ec2795b2f6c0b` | line 4 `policy.1=base.policy`; line 5 `policy.2=complete.policy`; line 6 `policy.3=full.policy` |
| `base.policy` | 1,784 | `3f2374537e315ce9358e7cff5c9ab08a93a1fd9708fcfa739121e2d2556b72cd` | baseline property/file/environment permissions |
| `complete.policy` | 53 | `82059f870a65e76465b1da1948e7eaed83cfbb2e3cc33dcef0ecd9a94980b71c` | line 2 `java.security.AllPermission` |
| `full.policy` | 6,174 | `623e870a36dea05b9c5c33b16ccb68bf77a66675d008a2f6d46aa5e859bb2a14` | lines 7-8 grant AppMgrPermission `appMgr` and `chain`; lines 92-93 leave `setSecurityManager` and `setPolicy` commented |
| `xletmanager.policy` | 53 | `82059f870a65e76465b1da1948e7eaed83cfbb2e3cc33dcef0ecd9a94980b71c` | line 2 `java.security.AllPermission` |

`full.policy` explicitly comments that it excludes `com.harman.network.InterfacePermission`; application-specific policies may request that permission.

### Per-application policy

All 135 signed descriptors contain `xlet.policy.default=full.policy`. Of those, 122 also contain `xlet.policy=security.policy`, and each associated executable JAR contains the named `security.policy`. There are 18 unique application-policy SHA-256 values.

Because every regular executable-JAR file is covered by the key manifest, all 122 application `security.policy` members are cryptographically bound to the same application signer as their code and descriptor.

Representative policies:

- Vehicle User Guide `security.policy`: 188 bytes; SHA-256 `aaa4c3f9a07c2c4970f1368be560e4ef960fca3385f21fe51efb85541fd35aad`; requests FileIO read/write and AppMgrPermission `appMgr`.
- HelpDaemon `security.policy`: 252 bytes; SHA-256 `ef972932c46670584fd700fffcb0d6ff002aa2e3df0f8accd9e41f28c80cd280`; additionally requests InterfacePermission `ppp0`.

The exact runtime semantics among `xlet.policy.default`, the named global policy, the signed application `security.policy`, signer principal, and development mode remain unrecovered. The artifacts support a model in which the signed per-app file requests/defines application-specific permissions and the named global policy supplies a platform policy class or ceiling, but whether AMS combines, substitutes, intersects, or falls back is `UNKNOWN` until the policy-loader method is recovered.

### Java enforcement of AppManager permission

Relevant classes in `kona.jar`:

| Class member | Size | SHA-256 |
| --- | ---: | --- |
| `kona/appManager/AppManager.class` | 7,308 | `4e1346f07e9c3fd26b4eaa4874840faa40807bef21dcf0838b8801e886d00924` |
| `com/harman/appManager/AppManagerImpl.class` | 26,295 | `2ddb5e6efd235a3b85b6743585325351d178bbab7c7dff2e476ad2ad08978714` |
| `com/harman/appManager/AppMgrPermission.class` | 464 | `1cc50a998324d95528d36e7481b5881fdb406974ccda813a90112a5d96956686` |
| `com/harman/security/MethodPermission.class` | 1,311 | `e7014c2ded97a0f9495dc6f5fa88bb4d61ac01a5419d46ebb2910b619add4e31` |

The public `AppManager` API declares install, uninstall, DRM update/query, start, pause, stop, reset, and chain operations; `AppManagerImpl` supplies the SvcIPC-backed implementation traced below.

`AppMgrPermission` extends `MethodPermission`. In `MethodPermission.checkPermission()`:

- Code starts at class-file offset `0x4CF`, length 14.
- `System.getSecurityManager()` is invoked at `0x4CF`.
- If the result is non-null, `SecurityManager.checkPermission(this)` is invoked at `0x4D9`.

Every relevant public operation in `AppManagerImpl` starts by constructing `AppMgrPermission("appMgr")` and invoking `checkPermission()` at bytecode index 9:

| Java method | Code start | Permission check | SvcIPC operation load | `SvcIpcClient.invoke` |
| --- | ---: | ---: | ---: | ---: |
| `installApp(String,String)` | `0x2B28` | `0x2B31` | `installApp` at `0x2B65` | `0x2B6C` |
| `uninstallApp(String)` | `0x2E8C` | `0x2E95` | `uninstallApp` at `0x2EBC` | `0x2EC3` |
| `updateDRM(String)` | `0x30B4` | `0x30BD` | `updateDRM` at `0x30D9` | `0x30E1` |
| `getAllDRM(String)` | `0x3367` | `0x3370` | service name `getDRM` at `0x3397` | `0x339F` |
| `getDRM(String)` | `0x3466` | `0x346F` | service name `getAppsDRM` at `0x3496` | `0x349E` |
| `startApp(String,String)` | `0x3565` | `0x356E` | `startApp` at `0x35A7` | `0x35B0` |
| `pauseApp(String)` | `0x36CB` | `0x36D4` | `pauseApp` at `0x36FE` | `0x3706` |
| `stopApp(String)` | `0x3813` | `0x381C` | `stopApp` at `0x3846` | `0x384E` |

The Java wrapper therefore cannot be called successfully by an Xlet lacking `AppMgrPermission("appMgr")` while a security manager is active. This is an API permission boundary, not the package authenticity boundary; passing it only permits a request to the service.

## SvcIPC and native install boundary

`AppManagerImpl.class` constant-pool record `0x210A` contains `com.harman.service.AppManager`. Its static initializer starts at `0x6636` and loads that name at `0x6642`, constructing the object path by replacing `.` with `/`, yielding `/com/harman/service/AppManager`.

`installApp(String,String)` constructs a request map with `appId` and `filename`, then calls:

```text
SvcIpcClient.invoke("installApp", request, true, true, timeout)
```

The exact constant-pool method reference is `com/harman/svcipc/SvcIpcClient.invoke(Ljava/lang/String;Ljava/lang/Object;ZZI)Ljava/lang/Object;` at class constant-pool record `0xD4`.

The response's `errorCode` is decoded by a `tableswitch` at class-file offset `0x2BB0`, covering values 0 through 47. Relevant outcomes include:

| Service code | Java outcome | `new` instruction offset |
| ---: | --- | ---: |
| 0 | success path | branch at `0x2C80` |
| 14 | `JarNotFoundException` | `0x2C83` |
| 16 | `DrmVinException` | `0x2CC9` |
| 17 | `DrmDateCheckException` | `0x2CD3` |
| 21 | `NoWriteAccessException` | `0x2CF1` |
| 25 | `InternalErrorException` | `0x2C97` |
| 27 | `AppNotListedInDrmException` | `0x2CBF` |
| 30 | `XletPackageException` | `0x2CB5` |
| 31 | `JarNotSignedException` | `0x2CAB` |
| 33 | `AmsBusyException` | `0x2C8D` |
| 36 | `GetInfoTimeoutException` | `0x2CA1` |
| 37 | `StopRequestTimeoutException` | `0x2CDD` |
| 38 | `InstallTimeOutException` | `0x2CFB` |
| 39 | `AutoStartTimeoutException` | `0x2D2D` |
| 40 | `InstallErrorException` | `0x2D05` |
| 41 | `AutoStartAmsException` | `0x2D37` |
| 42 | `XletUnstoppableException` | `0x2CE7` |
| 45 | `ResourceExtractionTimeoutException` | `0x2D0F` |
| 46 | `EcoFileExtractionException` | `0x2D19` |
| 47 | `IconFileExtractionException` | `0x2D23` |

All other values in the switch fall through to generic `AppManagerException` at `0x2D41`.

This proves that the backend install contract distinguishes at least:

- package presence/format,
- DRM membership,
- DRM VIN and date checks,
- signature acceptance,
- AMS availability,
- extraction,
- installation, and
- automatic start.

The Java layer maps backend results. Hidden-HBC recovery now identifies a confirmed native AppManager-to-AMS authentication edge, a separate native DRM gate, and the distinction between conditional post-install autostart and later explicit start, although the precise order of every trust check is still not recovered.

### Native install completion and explicit start

Native AppManager is `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/bin/appManager`, 1,268,061 bytes, SHA-256 `608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591`. For this ELF, executable VAs equal file offsets plus `0x100000`.

**[CONFIRMED]** Installation does not launch an ordinary non-autostart Xlet:

- `onInstalledSignal` at VA `0x1938A8` calls `finishInstall` at VA `0x1935BC` from file `0x938E4`.
- `finishInstall` calls `onAppInstalled()` at file `0x936EC`, applies intermediate state 5 at `0x93700`, revokes write access at `0x93850`, and calls `autoStartApp` at `0x93858`.
- `autoStartApp` reads DRM launcher-mask bit 2: mask load file `0x1BB38`, `tst #4` at `0x1BB3C`, and bit extraction at `0x1BB64`. Its launch condition is `(DRM launcher-mask bit 2 OR stock super-app override) AND AppManager global autostart gate`.
- When false, the path reaches `INSTALLATION DONE` at file `0x91A30` and success completion at `0x91A64` without calling the App start primitive.

**[CONFIRMED]** A stopped ordinary app is launched later by an explicit native `startApp` operation with DRM checking enabled. The Java API is separately permissioned:

- Native `parseRequest` spans VA `0x1516D4..0x156DFC`. It compares token `startApp` (file `0x108084`) at file `0x53DD0` and dispatches at `0x53DF0` to VA `0x14FDB0`.
- The handler writes the DRM-check argument one at file `0x50650` and calls `findAndStartApp` at VA `0x13B2DC` from `0x5066C`. The no-service, DRM-failed, and not-found diagnostics are at files `0x105474`, `0x1054BC`, and `0x105510`.
- `findAndStartApp` reaches the sole App start primitive at file `0x3C328` to VA `0x10EE68`; App start sends the AMS-facing `start` operation through the helper called at file `0xF008`.
- The Java-side `AppManagerImpl.startApp(String,String)` offsets `0x3565/0x356E/0x35A7/0x35B0` independently prove the `AppMgrPermission("appMgr")` check, SvcIPC operation load, and invocation.
- The stock generic Apps UI takes a direct HMI-module-to-native route. ROV `AppsMainScreen.swf` (36,208 bytes, SHA-256 `5df0c52056d9495c439e8c90d1826be132f43bc7d4a61951acd4f1adfccbd04d`) handles the selected item in `onItem` (method/body/code `0x9F17/0xBDA0/0xBDA7`) and calls `IAppManager.startXlet(selected.appId,"MoreScreen")` at FWS `0xC1E6`. ROV `MainSupplement.swf` (1,407,783 bytes, SHA-256 `e9d796ea4b4c83ed518bfe3b3c341e54e510a1ae0f78ebbffbd655b7c36a3258`) implements `AppManager.startXlet` at `0x1E7A0B/0x2A9712/0x2A971A`, emits `startApp` at `0x2A97E1`, and sends it at `0x2A97E7/0x2A9AF6` to destination `AppManager`. That stock HMI invocation does not traverse the Java permission check, but it does retain the proved native DRM check.

The global autostart gate is not per-app enablement. Native config parsing handles `alwaysAutostartApps` at file `0x76BAC..0x76BF8`; if absent, it tests `/fs/etfs/No_AutoStart_App` at `0x76C28` and stores the runtime gate at `0x76C50/0x76C6C`. The recovered `appManager.cfg` contains only two fixed stock UUIDs in `delayedStartApps` at line 26 and no `alwaysAutostartApps`, so an arbitrary installed helper is not selected by that delayed list.

**[CONFIRMED bounded negative]** The complete native parser has 56 constant method-token comparisons, including install/upgrade/uninstall/start/pause/stop and specialized daemon/delayed/assist/embedded operations, but no `enableApp`, `disableApp`, or `launchApp` comparison. A full-file case-sensitive/case-insensitive ASCII and UTF-16LE census finds none of those tokens, and the Java public AppManager API also declares no per-app enable/disable method. This proves absence from the recovered operation surfaces, not absence of every possible numeric-only or external suppression state.

### Native AppManager delegates authenticated package inspection to AMS

The recovered native `appManager` is an ELF32 ARM executable with entry point `0x108EE8`. Its dynamic dependencies are `libsvcipc.so.1`, `libjsoncpp.so.1`, `libsys_colibry_net.so`, `libsys_colibry.so`, `libsys_trace_clienttrace.so`, `libpps.so.1`, `libcpp.so.4`, and `libc.so.3`; there is no linked crypto library. Exact byte searches find none of `key.jar`, `META-INF`, `MANIFEST.MF`, `.SF`, or `.RSA`. It does contain the generic result text `Signing check of jar file failed` at file offset `0x1107E0`, consistent with error translation rather than local JAR-signature parsing.

In the install-start path, native `appManager`:

- constructs request fields `filename` at `0x19206C` and `uri` at `0x1920F0`;
- adds JSON field `auth` using string VA `0x20F000` at `0x192878`, then constructs boolean `true` at `0x19288C`;
- constructs method name `getPackageInfo` from string VA `0x20FE18` at `0x1928C8`;
- calls its generic asynchronous AMS wrapper at `0x192904`, with callback VA `0x193E9C`.

The target identity is explicit in the same binary: `com.aicas.xlet.manager.AMS` is at file offset `0x1156D0` and `/com/aicas/xlet/manager/AMS` at `0x1156EC`. The wrapper beginning at `0x17E75C` also loads `getPackageInfo` at `0x17E888`. Native DRM-update code logs `AM:startDRMUpdate() check signing for path="%s"` via string VA `0x21631C` at `0x1BD818`, then calls that `getPackageInfo` wrapper at `0x1BD83C` with callback VA `0x1BD8E4`.

This proves that native AppManager asks AMS to inspect a URI in authenticated mode before install and delegates the DRM-update signing preflight to the same AMS method. Combined with AMS's `getKeyJarFile`, `keyJar_`, and verifier vocabulary below, the best-supported responsibility split is:

| Responsibility | Grade | Evidence |
| --- | --- | --- |
| request orchestration, local DRM gate, error mapping | `CONFIRMED` native AppManager | call sites above and the checker below |
| authenticated package inspection | `CONFIRMED` AMS call | `getPackageInfo` request includes `auth:true` |
| parsing `key.jar` and verifying its detached signature/member digests | `HIGH` AMS | AMS owns the key-JAR/verifier names; native AppManager has no JAR-signature vocabulary or crypto dependency |
| exact AMS verifier call sequence and trust-anchor lookup | `UNKNOWN` | JamaicaVM ROM metadata has not yet been mapped to executable methods |

`appManager.cfg` independently fixes the storage model. Its default profile sets `preloadXletsDir=/fs/mmc1/kona/preload` at line 8, `xletsDir=/fs/mmc1/xletsdir` at line 9, `xletRMSDir=/fs/etfs/usr/var/appman/xletRMS` at line 10, live DRM data at line 13, and the preload DRM restore source at line 14.

### Native DRM checker and the unregistered `-d` argument

Boot and restart artifacts select whether the text `-d` is present, but that does not establish its native meaning:

- `boot.sh` lines 367 and 461 set `disableDRMArg=-d`; lines 371 and 465 pass it to `appManager -s -j -v ... -c=...` in the two boot branches.
- The Lua 5.1 main prototype in `platform_ams_restart.lua`, source lines 183-209, tests `/fs/etfs/disableDRM`: marker constant record/value offsets are `0x135C/0x1361`; the command omitting `-d` is `0x1375/0x137A`; the command including `-d` is `0x13E0/0x13E5`. Bytecode PCs 40-44 perform the test; PCs 45-48 select the no-`-d` command when the file test returns numeric 1, and PCs 50-53 otherwise select the command containing `-d`.

The exact `appManager` option parser closes the other half of this question. `processOptions` at `0x195FFC` constructs an empty local Poco `OptionSet` at `0x196028`, then registers only:

| Long option | Short option | Construction VAs |
| --- | --- | --- |
| `silent` | `s` | `0x196030`, `0x196044` |
| `json` | `j` | `0x196198`, `0x1961AC` |
| `presub` | `p` | `0x196300`, `0x196314` |
| `watchdog` | `w` | `0x196468`, `0x19647C` |
| `config` | `c` | `0x1965D0`, `0x1965E4` |
| `tp` | empty short name | `0x1967A4`, `0x1967B8` |
| `help` | `h` | `0x196964`, `0x196978` |

The `OptionProcessor` is constructed from that local set at `0x196AD4` and Unix-style parsing is enabled at `0x196AE0`. Its single-dash path at `0x1DA96C` copies the substring following `-` and calls the common lookup with its short-option selector at `0x1DAA00`. Thus `-d` produces a lookup for short name `d`; short-option clustering or a long-name prefix cannot manufacture a missing one-character entry. No inherited/global option set is consulted: the processor stores the sole local `OptionSet` pointer at `0x1D9FC8`, and common lookup starts from that pointer at `0x1DA1C8`. The process-level exception handler logs that an unknown option is ignored via string VA `0x21284C` loaded at `0x196E00`. `-d`, `-v`, and boot's `--bp` are absent from the registered list.

There is a dormant handler branch that compares a normalized option name to `drm` at `0x19718C-0x197200`. On equality it passes `1` at `0x197208` to the setter at `0x16D548`, whose only direct branch-link caller is `0x19720C`. The setter logs `AM:checkDRM(enable=%s)` using string file offset `0x10B5DC` and stores the byte at `0x16D58C`. Because `drm` is not registered either, there is no route from this function's constructed option set to that handler branch.

The stored byte is the enable field of the DRM checker subobject, not an unexplained standalone switch. The configuration singleton constructor at `0x143F7C` constructs that subobject at whole-object offset `0xD4` by calling constructor `0x181318` at `0x1440B0`; the subobject constructor initializes byte `+5` to `1` at `0x181338`. The setter's whole-object offset `0xD9` is the same byte. Install preparation obtains the singleton at `0x195788`, adds `0xD4`, and calls checker `0x1801D4` at `0x1957A4`. The checker reads enable byte `+5` at `0x1802C0`: zero logs the disabled path and returns success, while nonzero continues into grant lookup; a missing grant produces error `0x1B` at `0x180338`.

For this exact binary, the defensible result is therefore `CONFIRMED`: DRM checking defaults enabled, install preparation calls it, and `-d` is unregistered and ignored. The marker/file and stale boot argument show intended historical configuration vocabulary, but they do not implement a working DRM-disable transition in this recovered build.

### `authenticationService` is a separate keyed crypto service

`boot.sh` line 649 launches `authenticationService -k /etc/system/config/authenticationServiceKeyFile.json`. The key JSON is described only structurally here: root keys are `keyRing` and `prodIdPath`; `keyRing` contains 100 contiguous `keyID_1` through `keyID_100` objects, each with only a `value` field; all 100 values are distinct 64-character hexadecimal strings. No value or production-ID path is reproduced.

The service registers `com.harman.service.authenticationService` at file offset `0x2F970` and object `/com/harman/service/authenticationService` at `0x2F99C`. Its dispatcher reads `productID` at VA `0x102B30` and `deviceID` at `0x102B54`; it dispatches `random` at `0x102C00-0x102C04` to handler `0x10293C`, and `sha256` at `0x102C28-0x102C2C` to handler `0x102000`. The SHA-256 handler reads `keyID` at `0x102010`, message data at `0x102138`, and emits `hash` at `0x10227C`.

Exact byte searches find no `developer`, `developerToken`, or `PIN` string in this service and no authentication-service identity in native `appManager`. This is negative evidence, not proof that no other process calls it. The proved role is a product/device-bound keyed hashing/random SvcIPC service. No call edge currently connects it to AMS package authentication, Developer Mode, factory PIN success, or `xlet.developerToken`.

## AMS verification vocabulary and limits

`AMS` is a 32-bit little-endian ARM ET_EXEC image. It retains 28 ordinary ELF sections but no `.symtab`; its `.dynsym` has 414 entries and does not name the ROMized AMS Java methods. Its `.comment` identifies `Jamaica Builder ELF binary Utility` at file offset `0xB65326`, while runtime strings identify `Jamaica Virtual Machine Version 6.0harman Release 0 (build 8938)` at `0xB0F5E4`, build date `Mon Aug 24 14:02:01 UTC 2015` at `0xB11B4C`, and `Jamaica Static Compiler` at `0xB11D24`.

Relevant Java names live in one tag-driven JamaicaVM pool rather than ordinary NUL-delimited strings. The checked-in decoder reproduces all 60,877 entries from file `0x9C2071` through the zero terminator at `0xAB8ECC`; the 1,011,292-byte inclusive span has SHA-256 `3663f3ee68908e0625de021a53537f33264786fb350e54b8fd5614786ed888fb`. Entry tags identify short/full resets, front-coded suffixes, or extended full entries; 26 is only the maximum reset gap. The following headers are therefore global pool entries, not disconnected anchor-local strings.

| Decoded AMS entry | Header file offset |
| --- | ---: |
| `getDeveloperId` | `0xA78AE5` |
| `getDeveloperToken` | `0xA78AF0` |
| `getKeyJarFile` | `0xA7A107` |
| `getPackageInfo` | `0xA7B136` |
| `keyJar_` | `0xA88272` |
| `verifyAllCertificates` | `0xAA0250` |
| `verifyCertificates` | `0xAA027B` |
| `verifyDeveloperKey` | `0xAA0296` |
| `verifyDeviceKeyAndCertificate` | `0xAA02A3` |
| `verifyExemptJar` | `0xAA02B9` |
| `verifyFrameworkSigned` | `0xAA02C4` |
| `verifyManifestHash` | `0xAA02D5` |
| `verifyManifestMainAttrs` | `0xAA02E3` |
| `verifyPolicySigned` | `0xAA0315` |
| `verifyRevocationStatus` | `0xAA0361` |
| `verifySignature` | `0xAA038E` |
| `verifyWithSeparateSigningKey` | `0xAA03BA` |
| `xlet.developerToken` | `0xAA146C` |
| `xlet.deviceToken` | `0xAA1480` |
| `xlet.jarFile` | `0xAA148A` |
| `xlet.policy` | `0xAA14D2` |
| `xlet.policy.default` | `0xAA14D9` |
| `xlet.security` | `0xAA150A` |
| `xletPoliciesMayBeCached` | `0xAA1613` |
| `xletPropertiesFromAppId` | `0xAA1633` |
| `xletPropertiesFromUri` | `0xAA163E` |

One decoded verifier-shaped name is now classified more narrowly. `verifyWithSeparateSigningKey` is standard Java PKIX revocation vocabulary, not evidence of the RA4 detached `key.jar` mechanism. The same AMS image contains plain diagnostic fragments `CrlRevocationChecker.verifyPossibleCRLs` at file offset `0xA2BD2F`, `CrlRevocationChecker.buildToNewKey()` at `0xA2FDF1`, `verifyRevocationStatus CRL entry` at `0xA2FE69`, `circular dependency` at `0xA2FEC1`/`0xA2FF3E`, and `CrlRevocationChecker.verifyWithSeparateSigningKey()` at `0xA2FF12`. The method and its separate-CRL-signing-key purpose are independently present in the [OpenJDK-derived `CrlRevocationChecker` source](https://android.googlesource.com/platform/libcore/+/51b1b6997fd3f980076b8081f7f1165ccc2a4008/ojluni/src/main/java/sun/security/provider/certpath/CrlRevocationChecker.java) and current [OpenJDK `RevocationChecker`](https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/sun/security/provider/certpath/RevocationChecker.java). It must therefore be excluded from the proprietary package-authentication hypothesis unless an independent caller edge says otherwise.

The continuous pool segment beginning at `0xA8FEAC` yields:

- `policy` at `0xA8FEAC`
- `policy        loading and granting` at `0xA8FEB3`
- `policy file not signed by aicas` at `0xA8FED1`
- `policy provider ` at `0xA8FEEB`
- `policy,access` at `0xA8FEF6`
- `policy.allowSystemProperty` at `0xA8FF02`
- `policy.expandProperties` at `0xA8FF17`
- `policy.ignoreIdentityScope` at `0xA8FF29`
- `policy.provider` at `0xA8FF3E`

The `aicas` diagnostic aligns with the aicas signer present on both stock system security JARs. It does not prove that `verifyPolicySigned` validates an application's `security.policy`; the diagnostic may apply only to the system security configuration.

### Direct ROM class and verifier call graph

The Jamaica metadata schema is now sufficiently reconstructed to assign selectors to pointer-bounded class objects and follow the relevant bytecode. The supporting structures are:

- literal table `[0xAB8ED0,0xAD1E9C)`: 25,587 big-endian words, index 0 null, all other values valid one-based pool IDs, SHA-256 `8ba5cd317b5b515e6a8054b5e1c1384ab0e153b7eeedfecd87f6c0aa7c1f3afc`;
- global member-selector table `[0xAD1EA0,0xB08E10)`: 28,142 unique records `[u32be name ID][u32be descriptor ID]`, SHA-256 `82e1b04bb13de35c065ed9c42e9c535479f73c06d904f65d79e69f553832616a`;
- class-pointer table `[0xB1BC48,0xB20424)`: 4,599 strictly increasing little-endian VAs, SHA-256 `dc20f43fed693dfe8ee3c07b397c3ffb04441afdf077137cacf4059dcb094973`.

The member table is interned, not an ownership table. Ownership is proved when compact marker `0x8000 | selector-index` occurs inside a class-object bound that also has an exact self-name marker. Relevant confirmed class objects are:

| Class | Pointer slot and file bound | Relevant owned members |
| --- | --- | --- |
| `AMSController` | 354, `[0x5BA228,0x5BBDF0)` | constructor `0x5BA839`; `installSecurity` `0x5BABCC`; `getId` `0x5BAD92` |
| `KeyVerifier` | 384, `[0x5C1A78,0x5C1BA0)` | `verifyAllCertificates` `0x5C1ADF`; `verifyDeveloperKey` `0x5C1B03`; device/certificate alternatives `0x5C1B29/0x5C1B69` |
| `SecurityParameter` | 388, `[0x5C2150,0x5C21E0)` | fields `signingKeys`, `developerId`, `deviceId`; corresponding getters |
| `SignedId` | 390, `[0x5C2218,0x5C2378)` | `authenticationToken`, `id`, `verify(PublicKey[])`, `decrypt(PublicKey)` |
| `SigningKeys` | 391, `[0x5C2378,0x5C2408)` | fields `keys:PublicKey[]`, `validKey:PublicKey`, `isFirstCheck:boolean`; AOT/native-form `verify(Object[])` |
| `VerificationClassLoader` | 397, `[0x5C2748,0x5C2CA0)` | token fields/getters, `doResourceVerification`, private `verify(Object[])` |
| `XletProperties` | 436, `[0x5C7020,0x5C7098)` | `PROPERTIES_RESOURCE`, `DEVELOPER_KEY_PROPERTY`, `DEVICE_KEY_PROPERTY` |

`Installer` slot 376, `[0x5BF5A8,0x5C0B88)`, owns `getJarsDir` at `0x5C0556`, `getJarFile` at `0x5C0589`, and `getKeyJarFile` at `0x5C05BE`. The last method ignores its `Properties` argument and constructs the literal fixed sibling `<app>/prog/jars/key.jar`; only the executable name is read from `xlet.jarFile`. `AMSController.loadXlet` calls the payload and key helpers at `0x5BB432/0x5BB43C`, converts both paths, and passes them to `XletManager` at `0x5BB470`. `XletManager` tests key-file existence and converts it to a URL at `0x5C5FD9..0x5C5FF3`; `XletClassLoader` forwards that URL; and `VerificationClassLoader` stores it in `keyJar_` at `0x5C28F2..0x5C28F6` or `0x5C2932..0x5C2936`.

When `keyJar_` exists, `VerificationClassLoader.getSigners(String)` calls `getJarEntryCertificates(keyJar_,"xlet.properties")` at `0x5C2AFE..0x5C2B08`. When it is null, `0x5C2B2F..0x5C2B34` falls back to signer objects from the requested primary resource; the class overload makes the same choice. `doResourceVerification` resolves the primary `JarEntry`, obtains those signer objects, calls the private verifier, and stores its result at `0x5C2A77..0x5C2AC1`. The two-argument certificate extractor at `0x5C29DB` is AOT/native-form, so this proves the fixed signer-object source but not its exact manifest/entry-draining implementation or runtime recomputation of every cross-JAR digest. The complete ledger is `reports/keyjar_runtime_association.md`.

`XletProperties.DEVELOPER_KEY_PROPERTY == "xlet.developerToken"` is direct: selector record `0xAD8740`, marker `0x5C7068`, CP#8 header `0x5C7039`, literal index `0x4924`, literal-table word `0xACB360`, pool entry `0xAA146C`. The device-token control resolves through CP#9/literal `0x4284` to pool entry `0xAA1480`.

`VerificationClassLoader.getDeveloperToken()String` is selector record `0xAD8038`, marker `0x5C2BB4`. It loads literal `xlet.properties`, loads exact key `xlet.developerToken` at `0x5C2BF3`, performs the property lookup at `0x5C2BF5`, and caches the result at `0x5C2BF8`. The device-token getter has the matching flow at `0x5C2C46..0x5C2C4B`.

The confirmed verification sequence is:

```text
VerificationClassLoader.doResourceVerification
  -> VerificationClassLoader.verify(Object[])
       -> getDeveloperToken()
       -> getDeviceToken()
       -> KeyVerifier.verifyAllCertificates(objects, developerToken, deviceToken)
            -> verifyDeveloperKey(developerToken)
                 -> SignedId(token, SecurityParameter.getDeveloperId())
                    .verify(SecurityParameter.getSigningKeys())
            -> only if false: verifyDeviceKeyAndCertificate(objects, deviceToken)
```

The private VCL verifier body is `0x5C2AD1..0x5C2AEA`. `verifyAllCertificates` body `0x5C1AE6..0x5C1AFF` calls the developer branch at `0x5C1AEB`, returns immediately on success through branch `0x5C1AF2`, and calls the device/certificate alternative at `0x5C1AF8` only on failure. A null device token explicitly takes certificate-only verification; a present invalid device token fails that shortcut.

`SignedId.decrypt(PublicKey)`, inline bytecode `0x5C2335..0x5C2364`, calls `Key.getAlgorithm`, `Cipher.getInstance`, `Cipher.init(2,key)`, `BASE64Decoder.decodeBuffer(token)`, `Cipher.doFinal`, and `new String(byte[])`. `verify(PublicKey)`, `0x5C22F1..0x5C2326`, rejects null ID and calls `decrypted.equals(id)`; caught exceptions return false. `verify(PublicKey[])`, `0x5C22BC..0x5C22E6`, tries each key and succeeds on the first match. No explicit provider, transformation, padding, charset, hash, Signature API, PIN, nonce, time, IPC, or marker operand appears.

`AMSController` performs a two-stage key bootstrap. Its static initializer scans `rom:/internal.jar` for `xlet.security`, obtains that entry's certificates, extracts public keys, and stores `_internalKeys_` at `0x5BBC1C..0x5BBD1C`. The JAR is the pointer-bounded embedded ZIP `[0x988778,0x9892AD)`, 2,869 bytes, SHA-256 `2dbf7986c70e16d7bb047b897492c6ce164a1b5954837590708ee65b73759dab`; both signature envelopes and all manifest digest layers verify. Its bootstrap identities are aicas DSA certificate SHA-256 `9f28ad4b65f3eca46049b9f6abfb5c169b8c1ea35dde01380c689dbceab10d4c` and aicas RSA certificate SHA-256 `0654d97249cd24168cffbd7987ba6a05b76550dc95d765a9dafc59aaf11afe07`. The constructor creates a temporary selected-`securityJar_` VCL with those roots at `0x5BA8C2..0x5BA8D0`, obtains certificates on the selected JAR's `xlet.security` at `0x5BA8F9`, promotes their public keys at `0x5BA91F`, then stores those promoted keys with the reflected IDs in the final `SecurityParameter` at `0x5BA958..0x5BA965`. Production promotes Chrysler+aicas candidates; development promotes Xlet Developer+aicas.

An exhaustive census of 300 JARs, 88,666 ZIP entries, 72,507 class entries, loose files, nested archives, and launch/config text found only three `Device.class` copies (production, development, Kona), all byte-identical at 481 bytes with SHA-256 `a452ac3005bbf0bdf18c7dd6d8fed766f7d130524170b4cfbae037efb2edc6e8`, with only constructors and neither getter. The VCL inherits the system class loader while using the selected security JAR as URL source, but the system-visible Kona copy is the same stub. No stock classpath/boot overlay option or alternate provider exists in the extraction. No DBus/SvcIPC/native call appears in the ID path. Only unrecovered live-unit mutable/overlay state remains a theoretical identity source.

This closes installed `key.jar` path ownership, signer-entry association, property loading, token semantics, two-stage key promotion, and the developer/device/certificate branch topology. It does not yet close:

- the legitimate private-key authority, authorized credential-issuance process, and implicit plaintext charset;
- any live-unit `Device` overlay absent from the complete update corpus;
- the AOT/native `SigningKeys.verify(Object[])` branch structure;
- the AOT/native `getJarEntryCertificates(URL,String)` digest/certificate extraction behavior;
- caller and scope of `verifyPolicySigned`;
- the detached application-`key.jar` trust/principal rule for Chrysler, VP4, developer, or aicas identities;
- the total ordering of DRM, detached signature, descriptor, policy, token, registration, and persistence checks.

The full offset ledger and reproduction commands are in `reports/developer_token_analysis.md`.

## End-to-end authorization map

```text
Installer/package container
  |
  | appId + filename request
  v
Kona AppManagerImpl
  |-- SecurityManager.checkPermission(AppMgrPermission("appMgr"))
  `-- SvcIPC /com/harman/service/AppManager :: installApp
          |
          v
native appManager
  |-- local DRM checker defaults enabled                         CONFIRMED
  |     `-- appIdentifier/grant lookup; missing -> error 0x1B    CONFIRMED
  |-- build {filename, uri, auth:true}                            CONFIRMED
  `-- AMS :: getPackageInfo                                      CONFIRMED IPC call
          |
          |-- Installer fixed sibling -> VCL keyJar_              CONFIRMED call graph
          |-- signer objects from key.jar!/xlet.properties        CONFIRMED call graph
          |-- AOT certificate extraction / SigningKeys key match  UNKNOWN details
          |-- runtime cross-JAR digest recomputation              UNKNOWN implementation
          |     |-- appId, mainClass, policy/default             CONFIRMED signed data
          |     `-- optional developerToken                      CONFIRMED signed data
          |          `-- VCL.getDeveloperToken                   CONFIRMED property load
          |              `-- KeyVerifier.verifyDeveloperKey      CONFIRMED direct call
          |                  `-- SignedId(token,developerId)
          |                      .verify(selected-JAR signer keys)
          |                           `-- Base64 + public Cipher
          |                               + exact ID equality      CONFIRMED
          |-- failed developer branch -> device/certificate      CONFIRMED alternative
          `-- return package information/authentication result   CONFIRMED boundary
                  |
                  | install normalized descriptor/JAR + register HIGH
                  v
AMS launch/security domain
  |-- production or development security.jar                    CONFIRMED startup choice elsewhere
  |-- internal.jar roots -> selected-JAR signer-key promotion    CONFIRMED
  |-- token branch and SignedId cryptographic predicate          CONFIRMED
  |-- runtime developer-ID provider                              ABSENT IN RECOVERED CORPUS
  |-- credential issuer + signer/principal/trust policy         UNKNOWN
  |-- global + signed per-app policy assignment                  UNKNOWN combination rule
  |-- permission domain / Xlet creation                          HIGH
  `-- start, pause, stop, uninstall lifecycle                    CONFIRMED Java/IPC surface
```

The component boundary is now materially narrower. Native AppManager performs the local DRM-grant gate and asks AMS for authenticated package information. Installed AMS constructs and propagates the fixed `key.jar` sibling, obtains signer objects from its `xlet.properties` entry, loads the exact developer property, promotes selected-security-JAR keys, applies the Base64/SunJCE-RSA/ID predicate first, and only then enters the device/certificate alternative. `Installer.copyAndCheck` now proves the direct incoming-JAR member split that creates the payload and detached `key.jar`. The remaining trust gap is inside AOT certificate extraction and `SigningKeys.verify`, the legitimate issuer/live-unit ID overlay, authorized issuance/serialization, and signer-to-policy/principal mapping.

## Safe design implications

1. A safe custom application path must preserve the detached signature model. Modifying any regular application member, including its own manifest or `security.policy`, breaks a digest in the signed `key.jar` manifest.
2. DRM authorization and content integrity are separate signed objects. A DRM grant authorizes an app identity and installation attributes; `key.jar` authenticates the actual installed member bytes and descriptor.
3. Editing the installed filesystem `xlet.properties` is neither a sound signing procedure nor sufficient proof of authorization. Normal installation already transforms that file, while the signed descriptor remains inside `key.jar`.
4. Adding a root to Kona `cacerts` is not supported as an application-signing solution. The observed application signer fingerprints do not directly equal that JKS's trusted-certificate fingerprints, and the actual AMS signer trust source is still unknown.
5. The boot argument `-d` is not a usable or proved security control in this build. It is unregistered and ignored, while the DRM checker initializes enabled. Any design that relies on toggling that argument would be both ineffective and based on the wrong trust boundary.
6. Globally replacing `security.jar`, granting `AllPermission`, disabling DRM, or bypassing signature checks would erase the platform's existing separation of entitlement, integrity, and runtime permission. Nothing in this report justifies those actions.
7. The smallest safe eventual implementation should use a factory-supported development signer/token or a narrowly scoped owner-generated trust entry only after the native trust-store and principal-selection path are proved. It should request only the permissions required by the helper application and retain the stock production path for all factory Xlets.
8. Installing an inert non-autostart proof app is behaviorally distinct from launching it. A safe trial must verify that install finishes with the app stopped, then use only the statically proved generic stock Apps entry (`AppsMainScreen` -> module `AppManager` -> native DRM-checked `startApp`). Before relying on it, dynamically verify that the target unit returns the authorized helper in `getAppList` with the intended metadata and follows the recovered ROV/RU behavior.

## Highest-value unresolved questions

1. What exact chain-building, ordering, revocation/time, and caching rules do AOT `getJarEntryCertificates(URL,String)` and `SigningKeys.verify(Object[])` apply after the now-confirmed `key.jar!/xlet.properties` signer-object association?
2. Does an authorized target unit expose a mutable system/boot overlay supplying the otherwise absent `Device` getters, and what supported authority issues credentials for that live ID under the promoted RSA key?
3. How do the promoted production Chrysler+aicas versus development Xlet Developer+aicas keys and revisions change application signer acceptance or policy selection when `/fs/etfs/AMS_DEVELOPMENT` is active?
4. Is `xlet.policy.default` a fallback, a policy-class selector, a ceiling, or an input to policy intersection with signed `security.policy`?
5. What authorized issuer tool or service serializes this proved direct-JAR member schema, and which byte-exact ZIP/signature conventions does it require beyond the recovered semantic contract?
6. Which persistent registry fields retain DRM membership, signer identity, installed descriptor normalization, and launch/suppression state? No explicit per-app enable/disable operation exists in the recovered native or Java surfaces.
7. Why do boot/restart assets still vary the unregistered `-d` argument, and did an earlier or product-variant `appManager` register it with different default semantics?

## Reproducibility notes

Read-only verification performed for this report:

- SHA-256 and file-size checks over the exact paths named above.
- ZIP/JAR central-directory enumeration without executing target content.
- Java-properties parsing with line continuation and escape handling.
- JAR manifest line unfolding and per-member SHA-1/SHA-256 recomputation.
- Full-manifest digest recomputation for every `key.jar` and `DRM.jar` `.SF` file.
- PKCS#7 detached signature verification over every `.SF` using OpenSSL 3.5.7 with certificate-chain validation intentionally disabled.
- DER certificate parsing for SHA-256 signer fingerprints.
- Java class-file constant-pool, method `Code`, and `tableswitch` parsing for the exact offsets reported.
- Complete tag-driven ROM pool decoding plus literal/member/class-object linkage over `AMS`.
- Independent reproduction with `analysis_tools/jamaica_rom_strings.py` (13,329 bytes; SHA-256 `3fdd53837de8eeeef434d1249a0055102ab6ac05a7bc3c29b6752077cb185530`) and its 22-test suite `analysis_tools/tests/test_jamaica_rom_strings.py` (15,268 bytes; SHA-256 `309420c6bfd8359f49fc7e44793295f7be8c824e80536c0d19bb059329b922a7`). The CLI reproduces the full 60,877-entry pool, selected literal mappings, and member-selector signatures used above, including hexadecimal numeric bounds.
- Deterministic metadata-only token classification with `analysis_tools/developer_token_crypto_probe.py` (41,177 bytes; SHA-256 `f63aff730bdd59b78e832aec385d79564acab5919119e9616f84b8e806766bd8`) and its 19-test suite `analysis_tools/tests/test_developer_token_crypto_probe.py` (18,219 bytes; SHA-256 `505bc76bf89b0a8b34be3d45f14f2ca6b2d4cfc2329d91d773f278952387540f`). Together with the six QNX imagefs tests and 22 Jamaica metadata-decoder tests, all 47 tests pass. Two production JSON runs were byte-identical at 32,257 bytes with sanitized-output SHA-256 `91eec01858afddb2313e423e585bca4fcad46ad57baa72b65e78e9122374c5bc`; no token, PEM, modulus, recovered block, private data, or authentication value was emitted.
- ELF header, section, dynamic-symbol, dependency, and `.comment` inspection for `AMS`, native `appManager`, and `authenticationService`.
- ARM disassembly of native option registration/lookup, unknown-option handling, DRM flag construction/use, install preparation/completion, conditional autostart, explicit start/pause/stop dispatch, AMS `getPackageInfo` requests, and authentication-service dispatch.
- Lua 5.1 prototype/constant/instruction decoding for the restart marker branch.
- Safe structural validation of the authentication key JSON without emitting any key value or production-ID path.

No raw developer-token value, certificate private key, PIN material, vendor source code, or stock binary is included in this report.
