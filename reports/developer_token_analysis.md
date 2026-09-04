# RA4 18.45.01 developer-token analysis

## Scope and conclusion

This report is limited to static, read-only analysis of the owner-supplied RA4 18.45.01 extraction. No firmware image was modified, no target or vendor executable was run, no private key or PIN material was sought, and no credential value is reproduced. Unless otherwise stated, offsets are file offsets in `AMS` and its relevant load mapping is `VA = file offset + 0x100000`.

The AMS-side developer-token path is now directly reconstructed. `xlet.developerToken` is signed package metadata loaded by `VerificationClassLoader` from `xlet.properties`. AMS passes it to `KeyVerifier.verifyAllCertificates`, where a valid developer-token/ID result is the first acceptance alternative. If it fails, AMS evaluates the device-token/certificate path.

`SignedId` supplies the formerly missing token semantics. It Base64-decodes the property, asks `Cipher` for the candidate public key's algorithm name, initializes that cipher in decrypt mode with the public key, decrypts the bytes, constructs a platform-default-charset `String`, and accepts only exact equality with `developerId`. It tries every final `SecurityParameter.signingKeys` entry and succeeds on the first match. No Java `Signature`, hash, PIN, nonce, time, certificate-chain, IPC, or marker-state operand appears in this class.

The confirmed formula is:

```text
verifyDeveloperKey(developerToken)
OR
(
  deviceToken == null
    ? verifyCertificates(signingObjects)
    : verifyDeviceKey(deviceToken) AND verifyCertificates(signingObjects)
)
```

This closes the property-to-cryptographic-predicate call graph. It does not make the developer-token alternative usable: an exhaustive 300-JAR/72,507-class census found no implementation of the reflected getters. The only three recovered `com.aicas.xlet.manager.Device` copies are the same stub. Unless a live-unit system/boot overlay supplies an unrecovered implementation, both IDs become null and the developer-ID-backed alternative cannot succeed.

The signing-key source is also now exact. `rom:/internal.jar!/xlet.security` signer certificates seed immutable `_internalKeys_`; those keys authenticate the selected production/development `security.jar`; certificates attached to that selected JAR's `xlet.security` entry are then promoted into the final `SecurityParameter.signingKeys` used by `SignedId` and `SigningKeys`. The production candidates are Chrysler UConnect Application CA plus aicas GmbH; development substitutes Xlet Developer for Chrysler while retaining aicas. RA4's ROMized JCE code now also resolves the RSA candidate to SunJCE `RSACipher` with effective transformation `RSA/ECB/PKCS1Padding`. The runtime ID provider, legitimate private-key issuer workflow, and later signer-to-policy mapping remain unresolved.

No recovered call edge connects this package credential to the factory anti-theft PIN, the Service-menu certificate, DBus, SvcIPC, native AppManager, or creation of `/fs/etfs/AMS_DEVELOPMENT`. The marker selects the policy JAR at the next AMS launch; it does not generate or mutate the signed token.

## Artifact provenance

| Artifact | Exact evidence |
| --- | --- |
| AMS | `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/AMS`; 11,956,352 bytes; SHA-256 `96683b789ecf06a8575915d0b446b532e1f4ee87feb31d925cb7ba3d7d324d27` |
| AMSClient | `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/AMSClient`; 3,593,200 bytes; SHA-256 `12439c3e2554d388c43ca7f1023e96ad2183f5ae22a20991041b833eaa4eec9` |
| native AppManager | `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/bin/appManager`; 1,268,061 bytes; SHA-256 `608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591` |
| Kona platform JAR | `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/lib/kona.jar`; 3,062,680 bytes; SHA-256 `19390472018f02d998690b982f00eb68da5d40d7a8d6fba91499677651015f92` |
| production security JAR | `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/security/security.jar`; 7,504 bytes; SHA-256 `29a8a350ef0facc30c1c98e5250563a4020ad9c1a243f13e795e2e68e3bd74e7` |
| development security JAR | `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/security/development/security.jar`; 7,371 bytes; SHA-256 `fbe5314ab304e122162aae20ace46999b93832fc4c7451439f4ada430eccc8a7` |

## Reconstructed Jamaica ROM metadata

### Continuous name and descriptor pool

`analysis_tools/jamaica_rom_strings.py` now decodes the complete tag-driven stream rather than assuming resets every 26 entries.

| Property | Exact value |
| --- | --- |
| range | file `[0x9C2071,0xAB8ECC]`, including the zero terminator |
| entries | 60,877, indexed `0..60876` |
| inclusive bytes | 1,011,292 |
| SHA-256 | `3663f3ee68908e0625de021a53537f33264786fb350e54b8fd5614786ed888fb` |
| entry forms | 2,396 short full/reset, 138 extended full/reset, 58,343 front-coded |
| reset bound | maximum reset-index gap 26; reset position is encoded by the tag, not `index % 26` |

Encoding is confirmed as `0x00` terminator; `0x01..0x7F` short full entry; `0x80..0xFE` front-coded entry with suffix length `tag & 0x7F` followed by a one-byte prefix length; and `0xFF` followed by a big-endian two-byte full-entry length. The extended entry at `0xAA1A23` begins `FF 08 01` and is 2,049 bytes, independently falsifying the earlier fixed-26 interpretation.

Exact relevant pool-entry headers include:

| Name | File offset |
| --- | --- |
| `DEVELOPER_KEY_PROPERTY` | `0xA31318` |
| `DEVICE_KEY_PROPERTY` | `0xA3132D` |
| `developerId` | `0xA72B3C` |
| `developerToken` | `0xA72B42` |
| `getDeveloperId` | `0xA78AE5` |
| `getDeveloperToken` | `0xA78AF0` |
| `getSigningKeys` | `0xA7C14B` |
| `securityParameter` | `0xA93B0F` |
| `securityParameter_` | `0xA93B1A` |
| `signingKeys` | `0xA970BA` |
| `verifyDeveloperKey` | `0xAA0296` |
| `xlet.developerToken` | `0xAA146C` |
| `xlet.deviceToken` | `0xAA1480` |

### Literal table and member selectors

| Structure | Exact evidence |
| --- | --- |
| literal table | file `[0xAB8ED0,0xAD1E9C)`; 25,587 big-endian `u32` entries; index 0 null; every other word is a valid one-based pool ID; SHA-256 `8ba5cd317b5b515e6a8054b5e1c1384ab0e153b7eeedfecd87f6c0aa7c1f3afc` |
| separator | zero word at file `0xAD1E9C` |
| member-selector table | file `[0xAD1EA0,0xB08E10)`; 28,142 records of `[u32be one-based name ID][u32be one-based descriptor ID]`; SHA-256 `82e1b04bb13de35c065ed9c42e9c535479f73c06d904f65d79e69f553832616a` |
| selector validation | all 28,142 IDs valid, all descriptors JVM-valid, and all name/descriptor pairs unique |
| class-pointer table | file `[0xB1BC48,0xB20424)`; 4,599 strictly increasing little-endian VAs; SHA-256 `dc20f43fed693dfe8ee3c07b397c3ffb04441afdf077137cacf4059dcb094973` |

The selector table is global and interned, not an ownership list. A class object embeds compact marker `0x8000 | zero-based selector index`; ownership is established only when that marker falls inside a pointer-bounded class object with a resolved self-name marker. Reuse of selector `verify([Ljava/lang/Object;)Z` by both `SigningKeys` and `VerificationClassLoader` is a control demonstrating the distinction.

## Direct class and member ownership

| Class | Pointer-table slot and bounded object | Self-name marker | Confirmed relevant selectors |
| --- | --- | --- | --- |
| `AMSController` | slot 354, `[0x5BA228,0x5BBDF0)` | `0x5BA4C6` | `_internalKeys_` `0x5BA7F0`; `securityParameter` `0x5BA7EC`; constructor `0x5BA839`; `installSecurity` `0x5BABCC`; `getId` `0x5BAD92` |
| `Installer` | slot 376, `[0x5BF5A8,0x5C0B88)` | `0x5BF8E3` | `install(String)Application` `0x5BFCC0`; `recoverProgIfNeeded(String)V` `0x5BFDFD`; `upgrade(String)Application` `0x5BFE8C` |
| `KeyVerifier` | slot 384, `[0x5C1A78,0x5C1BA0)` | `0x5C1AB6` | constructor `0x5C1ACB`; `verifyAllCertificates(Object[],String,String)Z` `0x5C1ADF`; `verifyDeveloperKey(String)Z` `0x5C1B03`; `verifyDeviceKeyAndCertificate(Object[],String)Z` `0x5C1B29`; `verifyCertificates(Object[])Z` `0x5C1B69` |
| `SecurityParameter` | slot 388, `[0x5C2150,0x5C21E0)` | `0x5C2160` | fields `signingKeys`/`developerId`/`deviceId` at `0x5C2170/74/78`; constructor `0x5C217D`; getters at `0x5C219B/0x5C21AA/0x5C21B9` |
| `SignedId` | slot 390, `[0x5C2218,0x5C2378)` | `0x5C227D` | fields `authenticationToken`/`id` at `0x5C2293/97`; `verify(PublicKey[])Z` `0x5C22B5`; `verify(PublicKey)Z` `0x5C22EA`; `decrypt(PublicKey)String` `0x5C232E` |
| `SigningKeys` | slot 391, `[0x5C2378,0x5C2408)` | `0x5C23BE` | fields `keys:PublicKey[]` `0x5C23CE`, `validKey:PublicKey` `0x5C23D2`, `isFirstCheck:boolean` `0x5C23D6`; constructor `0x5C23DB`; AOT/native-form `verify(Object[])Z` `0x5C23F5` |
| `VerificationClassLoader` | slot 397, `[0x5C2748,0x5C2CA0)` | `0x5C2898` | fields `developerToken`/`deviceToken` `0x5C28B0/B4`; constructors `0x5C28CD/0x5C2906`; `doResourceVerification(String)V` `0x5C2A6E`; private `verify(Object[])Z` `0x5C2ACA`; token getters `0x5C2BB4/0x5C2C07`; `isSecureMode()` `0x5C2C5A` |
| `XletProperties` | slot 436, `[0x5C7020,0x5C7098)` | `0x5C7021` | `PROPERTIES_RESOURCE` `0x5C704F`; `DEVELOPER_KEY_PROPERTY` `0x5C7068`; `DEVICE_KEY_PROPERTY` `0x5C706D` |

The member-table record for `getDeveloperToken()Ljava/lang/String;` is file `0xAD8038`, zero-based index 3123, raw `000095a0000006f2`, and compact marker `0x8C33`. This supplies the previously missing signature and class owner.

## Exact property binding and token loading

`XletProperties.DEVELOPER_KEY_PROPERTY == "xlet.developerToken"` is directly proved:

1. Selector record file `0xAD8740` resolves `DEVELOPER_KEY_PROPERTY:Ljava/lang/String;`.
2. Compact selector marker `0x8D14` occurs at `XletProperties` file `0x5C7068`; following metadata `01 08` binds one-based constant-pool entry 8.
3. CP#8 header at file `0x5C7039` is `08 49 24`, selecting literal index `0x4924`.
4. Literal word at file `0xACB360` is one-based pool ID 55203.
5. Pool entry file `0xAA146C` decodes to `xlet.developerToken`.

Independent controls resolve `DEVICE_KEY_PROPERTY` through marker `0x8D15`, CP#9 header `0x5C703C`, literal index `0x4284`, literal word `0xAC98E0`, and pool entry `0xAA1480` to `xlet.deviceToken`; `PROPERTIES_RESOURCE` resolves to `xlet.properties`.

`VerificationClassLoader` has its own exact literal references: CP#65 at `0x5C2865` is `xlet.properties`, CP#75 at `0x5C288D` is `xlet.developerToken`, and CP#77 at `0x5C2895` is `xlet.deviceToken`.

In `getDeveloperToken()` the bytecode loads CP#75 at `0x5C2BF3`, performs the property lookup at `0x5C2BF5`, and caches the result to field `developerToken` at `0x5C2BF8`. `getDeviceToken()` performs the corresponding operations at `0x5C2C46`, `0x5C2C48`, and `0x5C2C4B`. Missing properties yield and cache null. The resource/key/cache flow is confirmed; ordinary JDK target names such as `ClassLoader.getResource`, `URL.openStream`, `Properties.load`, and `Properties.getProperty` are structural-high assignments based on class slots, local method indices, and stack behavior.

## Complete verifier branch trace

`VerificationClassLoader.doResourceVerification` calls its private `verify(Object[])` at file `0x5C2ABC` and stores the result in its verification-success field at `0x5C2ABF`.

Private `VerificationClassLoader.verify`, body `0x5C2AD1..0x5C2AEA`, constructs `KeyVerifier(SecurityParameter)` at `0x5C2AD1..0x5C2AD9`, invokes `getDeveloperToken` at `0x5C2AE0`, invokes `getDeviceToken` at `0x5C2AE4`, calls `KeyVerifier.verifyAllCertificates` at `0x5C2AE7`, and returns its boolean at `0x5C2AEA`.

`KeyVerifier.verifyAllCertificates`, body `0x5C1AE6..0x5C1AFF`, first invokes `verifyDeveloperKey(developerToken)` at `0x5C1AEB`. Branch `ifne` at `0x5C1AF2` returns success directly. Only on failure does it invoke `verifyDeviceKeyAndCertificate(objects,deviceToken)` at `0x5C1AF8`.

`verifyDeveloperKey`, body `0x5C1B0A..0x5C1B25`, constructs `SignedId(authenticationToken, SecurityParameter.getDeveloperId())`, retrieves `SecurityParameter.getSigningKeys()`, calls `SignedId.verify(PublicKey[])`, and returns that result.

`verifyDeviceKeyAndCertificate` has an explicit null-device-token branch at `0x5C1B31`. A non-null token must pass `SignedId(authenticationToken,deviceId).verify(SecurityParameter.signingKeys)` at `0x5C1B4C` and certificate verification at `0x5C1B54`. A null token goes directly to certificate verification at `0x5C1B62`. `verifyCertificates`, body starting `0x5C1B70`, creates `SigningKeys` over those final selected-security-JAR signer keys and calls `SigningKeys.verify(Object[])` at `0x5C1B81`.

Absent and invalid developer tokens converge: there is no explicit null shortcut, failed `SignedId` verification returns false, and the device/certificate alternative runs. Device-token null is materially different: it explicitly permits the certificate-only branch, while a present but invalid device token fails before that shortcut.

## Exact `SignedId` token semantics

The bounded `SignedId` class slice `[0x5C2218,0x5C2378)` is 352 bytes with SHA-256 `9d61e243dad10dd7e7deaaeeaaea03c0b9ede844f47d257b46b69f37b86be709`.

`decrypt(PublicKey)String`, selector marker `0x5C232E`, has inline bytecode at `0x5C2335..0x5C2364`:

```text
algorithm = publicKey.getAlgorithm()                 0x5C2336
cipher = Cipher.getInstance(algorithm)               0x5C233B
cipher.init(Cipher.DECRYPT_MODE, publicKey)           0x5C2340..0x5C2342
ciphertext = BASE64Decoder.decodeBuffer(token)        0x5C2345..0x5C2350
plaintextBytes = cipher.doFinal(ciphertext)           0x5C2356
return new String(plaintextBytes)                     0x5C235B..0x5C2361
```

The constant-pool calls are `Key.getAlgorithm` CP#14, `Cipher.getInstance` CP#15, `Cipher.init(int,Key)` CP#16, `sun.misc.BASE64Decoder` CP#17/18, `CharacterDecoder.decodeBuffer(String)` CP#19, `Cipher.doFinal(byte[])` CP#20, and `String(byte[])` CP#21/22. No explicit transformation, mode, padding, provider, or charset string is supplied by `SignedId`; the following ROMized JCE trace resolves the provider and RSA padding, while the platform default charset remains implicit.

`verify(PublicKey)boolean`, bytecode `0x5C22F1..0x5C2326`, calls `decrypt`, explicitly rejects a null `id`, and evaluates `decryptedString.equals(id)` at `0x5C22FE..0x5C2309`. Its exception table catches `java.lang.Exception` across the decrypt/compare region, logs a bounded failure message, and returns false. `verify(PublicKey[])boolean`, bytecode `0x5C22BC..0x5C22E6`, rejects a null array, iterates from index zero, and returns immediately on the first successful key.

The exact predicate is therefore:

```text
exists key in SecurityParameter.signingKeys:
  cipher = Cipher.getInstance(key.getAlgorithm())
  cipher.init(DECRYPT_MODE, key)
  plaintext = new String(cipher.doFinal(Base64Decode(authenticationToken)))
  plaintext.equals(developerId)
```

The pseudocode omits only exception handling: every caught exception produces false. A null `developerId` cannot succeed. The private issuer and legitimate issuance workflow are not present in the corpus. The consumer's RSA provider, transformation, and padding are now proved below; the plaintext charset remains implicit and is not guessed.

### Exact JCE resolution for the RSA candidate

`reports/signedid_jce_semantics.md` contains the complete bounded trace. The decisive RA4-local edges are:

- the embedded provider-order resource places `com.sun.crypto.provider.SunJCE` at provider 4 (`0x899EDB`);
- `SunJCE$1.run` registers `Cipher.RSA -> com.sun.crypto.provider.RSACipher` and declares `ECB` plus the supported-padding set at `0x5E5CF7..0x5E5D0D` and `0x5E5FB3..0x5E5FE2`;
- `Cipher.getTransforms`, selector `0x44FD` at `0x6E6FD5`, represents bare `RSA` with null mode and padding;
- `Cipher$Transform.setModePadding`, selector `0x4534` at `0x6E81F4`, calls neither setter when those fields are null;
- the `RSACipher` constructor record `[0x5E4F6F,0x5E4F90)` stores `PKCS1Padding` in `paddingType`; `engineSetMode` accepts only the nominal mode `ECB`;
- `Cipher.init(2,publicKey)` reaches `RSACipher` internal `MODE_VERIFY` (numeric 4), selects `RSAPadding.PAD_BLOCKTYPE_1`, performs the public RSA operation, and unpads before returning the bytes (`0x5E5123..0x5E53AF`).

The exact conventional transformation label is therefore `RSA/ECB/PKCS1Padding`. This path is not OAEP and is not Java `Signature` verification: the recovered plaintext must be the exact `developerId` after PKCS#1 v1.5 type-1 unpadding. The promoted aicas DSA candidate cannot instantiate this RSA Cipher service and fails that per-key attempt through the already-confirmed exception-to-false path; the array overload continues to the RSA primary candidate.

## Two-stage signing-key bootstrap

`AMSController.<clinit>`, inline code beginning at `0x5BBBD2`, opens `rom:/internal.jar` (CP#320 loaded at `0x5BBC1C`), scans for `xlet.security` (`0x5BBC3C`), calls `JarEntry.getCertificates()` at `0x5BBC54`, maps every certificate through `Certificate.getPublicKey()` at `0x5BBD0E`, and writes the resulting `PublicKey[]` to `_internalKeys_` at `0x5BBCFC`. Failure writes null at `0x5BBD1C`. These are the immutable first-stage bootstrap keys.

The referenced JAR is recoverable in place. ROM pointer-table slot 4592 at file `0xB20408` points to VA `0xA88778`, mapping to file `0x988778`; the next slot points to file `0x9892B0`. The bounded object contains a valid 2,869-byte ZIP at `[0x988778,0x9892AD)`, followed by three alignment bytes, with SHA-256 `2dbf7986c70e16d7bb047b897492c6ce164a1b5954837590708ee65b73759dab`. It is the only one of the three embedded AMS ZIPs containing `xlet.security`; the other two contain the named JCE jurisdiction-policy resources `default_US_export.policy` and `default_local.policy`.

The embedded JAR has seven entries: manifest, `AICASFOR.SF`/`.DSA`, `AICAS.SF`/`.RSA`, directory record, and zero-byte `xlet.security`. The manifest's empty-entry SHA-1, both `.SF` full-manifest SHA-1 values, and both `.SF` per-entry SHA-1 values recompute exactly. Detached signature math over both `.SF` files verifies without claiming external chain trust. The two embedded self-issued certificate identities are:

| Internal signer | Key | Certificate SHA-256 | SPKI SHA-256 |
| --- | --- | --- | --- |
| aicas GmbH (`AICASFOR.DSA`) | DSA 1024 | `9f28ad4b65f3eca46049b9f6abfb5c169b8c1ea35dde01380c689dbceab10d4c` | `1f970eaeaf14b672bc4e9f027484e3b1f090430299f22730316f27ea206b5baa` |
| Natascha Scharnberg / aicas (`AICAS.RSA`) | RSA 1024 | `0654d97249cd24168cffbd7987ba6a05b76550dc95d765a9dafc59aaf11afe07` | `aae748183a11959af5eb91d0be12031014e851fc4dcc3eb2b940f63c214e45be` |

Because `JarEntry.getCertificates()` is called only after the entry stream is fully consumed, and both signatures cover `xlet.security`, these two public keys are the confirmed `_internalKeys_` candidates. They authenticate the security configuration; they are not the final `SignedId` token keys.

The secure constructor then creates a temporary `VerificationClassLoader` over the selected `securityJar_` using `SecurityParameter(_internalKeys_,null,null)` at `0x5BA8C2..0x5BA8D0`. `AMSController.getCertificates(loader)`, selector `0x5BAC8D` and call `0x5BA8F9`, requests that JAR's `xlet.security` entry and its certificates. Each certificate is converted to a public key at `0x5BA91F`; those selected-JAR keys, plus the two reflected IDs, form the final `SecurityParameter` at `0x5BA958..0x5BA965`.

Every relevant signature file explicitly covers `xlet.security`: production `META-INF/CVP_APP_.SF` and `AICASFOR.SF`, development `META-INF/DEVELOPM.SF` and `AICASFOR.SF`. The known promoted candidates are therefore Chrysler plus aicas in production, and Xlet Developer plus aicas in development. Exact certificate-array ordering and chain flattening/filtering inside the certificate accessor remain unresolved.

`SigningKeys.verify(Object[])` is encoded in AOT/native method form, so its exact certificate iteration still is not proved. Its class metadata contains `Certificate.verify(PublicKey)` and the expected certificate/key/provider exceptions, while its `validKey:PublicKey` and `isFirstCheck:boolean` fields suggest successful-key caching. Those facts constrain but do not replace a compiled control-flow trace.

## `developerId` origin gap

`SecurityParameter` stores constructor arguments directly into its `signingKeys`, `developerId`, and `deviceId` fields at file `0x5C2187..0x5C2197`; its getters directly return those fields.

`AMSController` constructs them as follows:

1. Constructor argument/local 5 is stored to `securityJar_` at `0x5BA87B` and used to construct a file/URL at `0x5BA8A5..0x5BA8BF`.
2. It creates a temporary `VerificationClassLoader` for that one URL with `new SecurityParameter(_internalKeys_,null,null)` at `0x5BA8C2..0x5BA8D0`.
3. It obtains the selected JAR's `xlet.security` certificates and promotes their public keys at `0x5BA8F9..0x5BA940`.
4. It calls private `getId("Developer",loader)` at `0x5BA944/0x5BA948` and `getId("Device",loader)` at `0x5BA94E/0x5BA952`.
5. It constructs the final `SecurityParameter(selectedJarSignerKeys,developerId,deviceId)` at `0x5BA958..0x5BA962` and stores it at `0x5BA965`.

`AMSController.getId` has descriptor `(Ljava/lang/String;Lcom/aicas/xlet/manager/VerificationClassLoader;)Ljava/lang/String;` at member record `0xAD73A0`, selector marker `0x5BAD92`, and body beginning `0x5BAD98`. It loads `com.aicas.xlet.manager.Device`, constructs method name `get` + kind + `Id`, reflectively calls the no-argument method, returns only a `String`, and catches/logs failure before returning null at `0x5BADFF..0x5BAE00`. No DBus, SvcIPC, or native call occurs on this ID-acquisition path.

The exhaustive provider census covered all 300 recovered JARs, 88,666 ZIP entries, 72,507 decompressed class entries, all loose recovered files, launch/config text, and nested archives, with zero ZIP errors and zero loose `.class` files. `com/aicas/xlet/manager/Device.class` exists only in the production security JAR, development security JAR, and Kona JAR. All three copies are byte-identical: 481 bytes, SHA-256 `a452ac3005bbf0bdf18c7dd6d8fed766f7d130524170b4cfbae037efb2edc6e8`, Java class version 48, no fields, and only `<init>()V` plus `<clinit>()V`. They contain neither requested getter. The only nested archives are three empty 22-byte `res/bundle.zip` members. No decompressed class contains `getDeveloperId`; that name occurs only in AMS's reconstructed pool.

The AOT inheritance chain is `VerificationClassLoader -> URLClassLoader -> SecureClassLoader -> ClassLoader`. VCL CP#79 at `0x5C289E` resolves to URLClassLoader class object `0x68E498`; its constructor at `0x5C28D4` calls the one-URL parent constructor. URLClassLoader CP#106 at `0x68E66D` resolves to SecureClassLoader; its no-argument constructor at `0x6AC01E` reaches ClassLoader. ClassLoader's no-argument constructor at `0x66BFA9` calls `getSystemClassLoader()` and the parent-taking constructor. Thus the temporary VCL has the selected security JAR as a URL source and inherits the system loader as parent. The exact parent-first/child-first bodies at `0x5C2943/0x5C294C` remain AOT-encoded, but both available sources contain the same unusable stub.

No recovered startup/configuration assigns `CLASSPATH`, `-classpath`, `-cp`, `-Xbootclasspath`, `java.system.class.loader`, `javaagent`, or `LD_PRELOAD`. Therefore the recovered stock configuration has no usable ID provider and reflection returns null. A mutable live-unit system/boot path or mount overlay remains a theoretical external-state boundary, not a recovered stock transition.

## Signed descriptor evidence and bounded crypto classification

Six installed Xlet descriptors, covering two application IDs and two main classes from one named vendor across KIM1/KIM12/KIM16, contain the same opaque property value. The value is intentionally not reproduced. Its normalized Base64 text is 344 characters, decodes to 256 bytes, and has decoded-byte SHA-256 `126a6126acb7832b1385e3caa9db7c6e78340acb92d020fabe4c86193b5f1045`.

In every case the installed value matches the corresponding descriptor embedded in sibling `prog/jars/key.jar`. The corpus-wide signed-container census in `reports/kona_application_authorization.md` establishes 78,756 executable members covered by 82,938 matching manifest digest records, 137 matching `.SF` full-manifest digests, and 137 mathematically valid embedded PKCS#7 signatures. The token is therefore part of the signed package identity; two application IDs reusing it supports a signer/account/vendor-program scope rather than a per-PIN-session value.

The checked-in metadata-only probe tested the simplest 256-byte RSA-signature hypothesis without printing credential material. It deduplicated 19 public identities, including 17 RSA identities, found 15 token-length-compatible RSA keys, tested both whole-token byte orders, 332 candidate message forms, six PKCS#1 v1.5 digest choices, and all 36 ordered PSS message-hash/MGF1-hash combinations. The exact matrix was 418,320 comparisons. All structure and message matches were negative; positive controls passed.

This bounded negative result rules out only the enumerated v1.5/PSS signature encodings and candidate messages under recovered compatible public keys. The AOT/JCE trace now explains the actual consumer shape: the value is Base64 ciphertext passed through SunJCE `RSA/ECB/PKCS1Padding` public-key decrypt/verify semantics and exact ID equality, not through Java `Signature`. The probe does not supply the missing runtime `developerId`, matching private key, or legitimate issuer workflow, so its negative result remains a boundary rather than an authorization recipe.

## Boundary ledger

| Edge | Status | Exact basis or remaining limit |
| --- | --- | --- |
| signed descriptor -> `xlet.developerToken` | `CONFIRMED` | byte-identical installed/embedded values plus verified manifest, `.SF`, and PKCS#7 layers |
| `XletProperties.DEVELOPER_KEY_PROPERTY` -> literal `xlet.developerToken` | `CONFIRMED` | selector/CP/literal/pool chain `0xAD8740 -> 0x5C7068 -> 0x5C7039 -> 0xACB360 -> 0xAA146C` |
| `VerificationClassLoader.getDeveloperToken` -> descriptor property | `CONFIRMED` | CP#75 load, property lookup, and field cache at `0x5C2BF3..0x5C2BFA` |
| developer token -> `KeyVerifier.verifyDeveloperKey` | `CONFIRMED` | direct calls in private VCL verifier and `verifyAllCertificates` at `0x5C2AE0..0x5C2AE7` and `0x5C1AEB` |
| `rom:/internal.jar!/xlet.security` certificates -> `_internalKeys_` | `CONFIRMED` | `AMSController.<clinit>` at `0x5BBC1C..0x5BBD1C`; embedded ZIP `[0x988778,0x9892AD)` with two verified signer envelopes |
| selected `securityJar_!/xlet.security` signer certificates -> final signing keys | `CONFIRMED` | temporary VCL and certificate/public-key promotion at `0x5BA8C2..0x5BA940`; final `SecurityParameter` at `0x5BA958..0x5BA965` |
| developer token + `developerId` + selected-JAR signing keys -> exact decrypt/equality predicate | `CONFIRMED` | `verifyDeveloperKey` `0x5C1B0A..0x5C1B25`; `SignedId` array/single/decrypt bodies `0x5C22BC..0x5C2364` |
| bare `RSA` algorithm -> SunJCE token transform | `CONFIRMED` | provider resource `0x899E43..0x899FE5`; SunJCE registration `0x5E5CF7..0x5E5FE2`; Cipher/Transform and RSACipher bodies `0x6E6FD0..0x6E821C`, `0x5E4F6F..0x5E53AF` prove `RSA/ECB/PKCS1Padding`, public decrypt, block type 1 |
| selected `securityJar_` -> reflective `Device.getDeveloperId/getDeviceId` | `CONFIRMED` | AMSController constructor and `getId` bodies |
| recovered corpus -> usable ID provider | `CONFIRMED NEGATIVE` | 300 JARs/72,507 class entries plus loose/config/nested-archive census; all three Device copies are the same getter-free stub |
| anti-theft PIN -> developer token/ID | `UNPROVED; bounded negative` | no shared operand, call, IPC name, state transition, or provider was found |
| Service certificate/item 19 -> token mutation | `UNPROVED; bounded negative` | item 19 only creates/deletes the marker; launcher only selects a policy JAR |
| development security JAR -> different token key candidates | `CONFIRMED` | production promotes Chrysler+aicas; development promotes Xlet Developer+aicas from certificates on `xlet.security` |
| selected signer/revision -> permission/principal policy | `UNKNOWN` | exact policy combination and principal assignment remain unrecovered |
| Installer -> direct token consumption | `UNPROVED` | Installer CP has SecurityParameter ID/key getters, but no bounded bytecode invocation uses CP#24, #26, or #28 |

Exact-term scans found no named developer-token bridge in recovered `AMSClient`, native `appManager`, or inspected Kona Java surfaces. Native `appManager` diagnostic `onAMSResult(token=%d)` is an asynchronous request-correlation token, not this Xlet credential. These are bounded negative results, not proof against an opaque unnamed bridge.

## Reproducible read-only operations

The continuous pool and selector/literal links reproduce with:

```powershell
& 'C:\Users\JHutc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' analysis_tools\jamaica_rom_strings.py analysis_ra4_18.45.01\work\primary_iso\usr\share\MMC_IFS_EXTENSION\bin\AMS --offset 0x9C2071 --until-terminator --max-entries 100000 --max-bytes 0x200000 --summary
```

Append either:

```text
--member-offset 0xAD1EA0 --member-count 28142 --find getDeveloperToken --find getDeveloperId --find verifyDeveloperKey
```

or:

```text
--literal-table-offset 0xAB8ED0 --literal-count 25587 --literal-index 0x4924 --literal-index 0x4284
```

At the last focused verification, `analysis_tools/jamaica_rom_strings.py` was 13,329 bytes with SHA-256 `3fdd53837de8eeeef434d1249a0055102ab6ac05a7bc3c29b6752077cb185530`; its 22-test file was 15,268 bytes with SHA-256 `309420c6bfd8359f49fc7e44793295f7be8c824e80536c0d19bb059329b922a7`, and all 22 tests passed. The CLI regression test covers hexadecimal numeric bounds used by the reproduction command above. Final repository-wide test and hash results are recorded in `reports/MASTER_FINDINGS.md` after each report-update cycle.

The independent crypto probe is `analysis_tools/developer_token_crypto_probe.py`, 41,177 bytes, SHA-256 `f63aff730bdd59b78e832aec385d79564acab5919119e9616f84b8e806766bd8`; its 19-test file is 18,219 bytes, SHA-256 `505bc76bf89b0a8b34be3d45f14f2ca6b2d4cfc2329d91d773f278952387540f`. Two prior full corpus runs produced identical sanitized JSON, 32,257 bytes, SHA-256 `91eec01858afddb2313e423e585bca4fcad46ad57baa72b65e78e9122374c5bc`.

## Remaining gaps and next lead

1. Perform read-only live-unit inventory, if and only if an authorized unit and procedure become available, to test the sole remaining `Device` boundary: mutable system/boot paths or mount overlays absent from the update corpus.
2. Identify the legitimate Chrysler/Xlet Developer credential issuer and exact certificate-array ordering/filtering without generating, copying, or replaying credentials.
3. Recover the AOT/native `SigningKeys.verify(Object[])` control flow and the detached-`key.jar` certificate association/order.
4. Prove how the promoted production/development signer set and configuration revision map to application principals, policy indices, and effective permissions.
5. Preserve the confirmed separation: anti-theft PIN success creates neither `developerId`, token, service authorization, nor package-install authority.
