# RA4 `key.jar` Runtime Association and Verification Order

## Scope and safety boundary

This report resolves which RA4 AMS classes construct, carry, and consume the installed companion `key.jar` path. It also separates installed-Xlet launch from incoming-package preflight and reconstructs the recoverable signer-verification order. The analysis is static and read-only. No vendor executable was run, no firmware or archive was modified, and no private key, developer credential, anti-theft PIN material, or bypass procedure is included.

Offsets are file offsets in:

`analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/AMS`

- Size: 11,956,352 bytes
- SHA-256: `96683b789ecf06a8575915d0b446b532e1f4ee87feb31d925cb7ba3d7d324d27`
- Jamaica/AOT address conversion: `VA = file offset + 0x100000`

Evidence grades:

- `CONFIRMED`: direct class ownership and recoverable bytecode/data flow.
- `HIGH`: strongly supported by adjacent artifacts, but the executing AOT/native body is unavailable.
- `UNKNOWN`: compatible with the evidence but not proved.

## Executive result

`key.jar` is a fixed installed-layout sibling selected by `com/aicas/xlet/manager/Installer`. It is not named by an application-controlled property:

```text
/fs/mmc1/xletsdir/<appId>/prog/jars/<xlet.jarFile>
/fs/mmc1/xletsdir/<appId>/prog/jars/key.jar
```

At installed launch, `AMSController.loadXlet` obtains both files, passes their paths through `XletManager`, and constructs an `XletClassLoader`. `VerificationClassLoader` stores the companion URL in `keyJar_`. When that URL exists, its signer lookup obtains certificate objects from exactly `key.jar!/xlet.properties`; when it does not exist, it falls back to signer objects from the primary application URL/resource.

The resulting objects enter this direct verification order:

```text
VerificationClassLoader.doResourceVerification(resource)
  -> getSigners(resource)
       -> key.jar!/xlet.properties certificates, if keyJar_ exists
       -> otherwise primary-resource certificates
  -> VerificationClassLoader.verify(objects)
       -> KeyVerifier.verifyAllCertificates(objects, developerToken, deviceToken)
            -> verifyDeveloperKey(developerToken) first
            -> only on failure: optional device-token check
                               plus SigningKeys.verify(objects)
```

This closes path ownership, loader propagation, the fixed signer-entry association, and verifier branch order. It does not prove the exact implementation of certificate extraction or runtime cross-JAR digest recomputation: `getJarEntryCertificates(URL,String)` and `SigningKeys.verify(Object[])` are AOT/native-form boundaries without recoverable inline Java bytecode.

## Class-object anchors

The Jamaica class-pointer table is `[0xB1BC48,0xB20424)`. These pointer-bounded class objects participate in the path:

| Class | Slot | File bounds | Size | Slice SHA-256 |
| --- | ---: | --- | ---: | --- |
| `AMSController` | 354 | `[0x5BA228,0x5BBDF0)` | 7,112 | `b056f82df1417c9b9584157e9c1f96971c8eb7828a352b16eef6d40261cbb5d9` |
| `Installer` | 376 | `[0x5BF5A8,0x5C0B88)` | 5,600 | `1afa152c93b978620a4b77d602ffe8af889c492a6781560a4e65489dfa041b0d` |
| `KeyVerifier` | 384 | `[0x5C1A78,0x5C1BA0)` | 296 | `e6f3510ae8873fca16e3c19e96d85ffbc9928e8f0a06fa5a8a2a1c77d312047b` |
| `SecurityParameter` | 388 | `[0x5C2150,0x5C21E0)` | 144 | `4465a42d4f216407da0cab2e977a185691e862f1f6702717222df474f299cd23` |
| `SigningKeys` | 391 | `[0x5C2378,0x5C2408)` | 144 | `f9e1f7a46794458607e4158168a5a26517e4d08ec08b5608a3eb443ef6cbeaaa` |
| `VerificationClassLoader` | 397 | `[0x5C2748,0x5C2CA0)` | 1,368 | `9c16f928fd8b8585e1751607597146d9b14df61478ffea5a23c68bfadadb41d8` |
| `XletClassLoader` | 414 | `[0x5C4000,0x5C4B08)` | 2,824 | `b51e116893f2946e0015861ab81b35f628c724f461b7c390679bcee64a394bd4` |
| `XletManager` | 420 | `[0x5C5238,0x5C6478)` | 4,672 | `506ba441f058da239d09ecf9426f36acbfcf3f0d36fc1d9d020c8e42383421a1` |

## `Installer` owns the fixed sibling path

`Installer` owns all three relevant path helpers:

| Member | Selector record | Compact marker | Method marker |
| --- | --- | --- | --- |
| `getJarsDir(String)String` | `0xAD7C18` | `0x8BAF` | `0x5C0556` |
| `getJarFile(String,Properties)File` | `0xAD7C50` | `0x8BB6` | `0x5C0589` |
| `getKeyJarFile(String,Properties)File` | `0xAD7C58` | `0x8BB7` | `0x5C05BE` |

The reconstructed construction is:

```text
getJarsDir(appId)
  = getAppDir(appId) + separator + "prog" + separator + "jars"

getJarFile(appId, properties)
  = new File(getJarsDir(appId) + separator
             + properties.getProperty("xlet.jarFile"))

getKeyJarFile(appId, properties)
  = new File(getJarsDir(appId) + separator + "key.jar")
```

`getKeyJarFile` does not read its `Properties` argument. The detached-key filename and association are therefore structural. Literal anchors are:

| Literal | Literal-table index | Literal record | Name-pool header |
| --- | ---: | ---: | ---: |
| `key.jar` | 8249 | `0xAC0FB4` | `0xA881C2` |
| `prog` | 3361 | `0xABC354` | `0xA90B8D` |
| `jars` | 3284 | `0xABC220` | `0xA82757` |
| `xlet.jarFile` | 14207 | `0xAC6CCC` | `0xAA148A` |

A raw byte pair `8B B7` at `0x5C0157` is an instruction operand, not a method boundary. The genuine `getKeyJarFile` marker is `0x5C05BE`.

## Installed-launch propagation

`AMSController.loadXlet(String,Object,boolean)` has selector record `0xAD7458`, compact marker `0x8AB7`, and method marker `0x5BB40E`. Its recoverable sequence is:

1. `0x5BB419`: call `Installer.xletPropertiesFromAppId`.
2. `0x5BB421`: obtain `xlet.mainClass`.
3. `0x5BB432`: call `Installer.getJarFile` through CP#234.
4. `0x5BB43C`: call `Installer.getKeyJarFile` through CP#235. This is the only `AMSController` invocation of that CP entry.
5. `0x5BB453` and `0x5BB458`: convert both `File` objects to path strings.
6. `0x5BB470`: call the long `XletManager.createXletManager` overload with both paths.

The long overload has selector `0xAD8690`, compact marker `0x8CFE`, and method marker `0x5C5F56`. It passes main class, payload path, key path, data directory, extension-loader state, `SecurityParameter`, signals, and daemon state to the path-to-URL overload at `0x5C5F7E`.

The path-to-URL overload has selector `0xAD8598`, marker `0x8CDF`, and performs:

- `0x5C5FD9..0x5C5FE1`: construct `File(keyJarPath)`;
- `0x5C5FE3..0x5C5FE7`: test `File.exists()`;
- absent: retain null key URL;
- present, `0x5C5FEB..0x5C5FF3`: convert the file through `toURI().toURL()`;
- `0x5C601C`: pass that URL or null into the URL-based overload.

The URL-based overload has selector `0xAD85A0`, marker `0x8CE0`, and method marker `0x5C602F`. It constructs `XletClassLoader` at `0x5C6047..0x5C6059` when an extension parent exists or at `0x5C605E..0x5C6068` otherwise. It then loads `xlet.budgets` at `0x5C606A..0x5C607B`, loads `xlet.properties` at `0x5C607D..0x5C6092`, and calls `loader.loadClass(mainClass,true)` at `0x5C6094..0x5C609C` before constructing the final `XletManager` instance.

`XletClassLoader` forwards the key URL to `VerificationClassLoader`:

- four-argument constructor marker `0x5C433A`, super call at `0x5C4345`;
- five-argument constructor marker `0x5C435E`, super call at `0x5C436C`.

`VerificationClassLoader` owns `keyJar_:Ljava/net/URL;`, selector record `0xAD7FD0`, compact marker `0x8C26`, field marker `0x5C28C0`. Its four-argument constructor assigns the field at `0x5C28F2..0x5C28F6`; the five-argument constructor assigns it at `0x5C2932..0x5C2936`.

The complete confirmed ownership graph is therefore:

```text
Installer fixed sibling path
  -> AMSController payload/key path pair
  -> XletManager existence test and URL conversion
  -> XletClassLoader constructor
  -> VerificationClassLoader.keyJar_
```

## Fixed signer-entry association

Relevant `VerificationClassLoader` members are:

| Member | Selector record | Method marker |
| --- | --- | --- |
| `getJarEntryCertificates(URL,String)Certificate[]` | `0xAD8018` | `0x5C29DB` (`0x8C2F`) |
| `getJarEntryCertificates(String)Certificate[]` | `0xAD8048` | `0x5C29B8` (`0x8C35`) |
| `doResourceVerification(String)` | `0xAD8028` | `0x5C2A6E` (`0x8C31`) |
| `getSigners(String)Object[]` | `0xAD8030` | `0x5C2AEE` (`0x8C32`) |
| `getSigners(Class)Object[]` | `0xAD7FF8` | `0x5C2B65` (`0x8C2B`) |
| private `verify(Object[])boolean` | `0xAD7F38` | `0x5C2ACA` (`0x8C13`) |

`getSigners(String)` loads `keyJar_` at `0x5C2AF7..0x5C2AFA`. When non-null, it calls `getJarEntryCertificates(keyJar_, "xlet.properties")` at `0x5C2AFE..0x5C2B08`; the invocation is CP#37 at `0x5C2B05`. The literal is CP#65, literal-table index 16310, literal record `0xAC8DA8`, and name-pool header `0xAA1500`.

When `keyJar_` is null, `0x5C2B2F..0x5C2B34` invokes the one-argument helper using the requested primary resource name. `getSigners(Class)` implements the same split: fixed companion `key.jar!/xlet.properties` certificates when the key URL exists, otherwise the primary class's signer objects.

The one-argument helper at `0x5C29B8` selects `urls_[0]` and delegates to the two-argument helper. The two-argument method at `0x5C29DB` is AOT/native-form with no recoverable inline Java body. The exact entry-draining, manifest-digest recomputation, certificate-chain extraction, and exception behavior remain unknown.

## Verification ordering

`doResourceVerification(String)` at `0x5C2A6E` opens the primary URL's JAR and resolves the requested `JarEntry` at `0x5C2A77..0x5C2A8B`. When the entry exists, it obtains signer objects at `0x5C2AB3..0x5C2AB8`, calls private `verify(Object[])` at `0x5C2AB9..0x5C2ABE`, and stores the result in the verification-success field at `0x5C2ABF..0x5C2AC1`.

Private `VerificationClassLoader.verify(Object[])` constructs `KeyVerifier`, obtains its cached developer and device tokens, and invokes `KeyVerifier.verifyAllCertificates(objects,developerToken,deviceToken)` at `0x5C2AE7..0x5C2AE9`.

`KeyVerifier.verifyAllCertificates` has selector `0xAD7E48`, marker `0x8BF5`, and method marker `0x5C1ADF`. Its direct branch order is:

1. `0x5C1AE9..0x5C1AED`: `verifyDeveloperKey(developerToken)`.
2. `0x5C1AF0..0x5C1AF4`: return success immediately when that branch succeeds.
3. `0x5C1AF5..0x5C1AFA`: otherwise call `verifyDeviceKeyAndCertificate(objects,deviceToken)`.

The fallback members are `verifyDeveloperKey(String)` at `0x5C1B03` (selector `0xAD7E28`), `verifyDeviceKeyAndCertificate(Object[],String)` at `0x5C1B29` (`0xAD7E30`), and `verifyCertificates(Object[])` at `0x5C1B69` (`0xAD7E38`). With a non-null device token, the device `SignedId` must succeed before certificate verification at `0x5C1B52..0x5C1B56`. With a null device token, execution goes directly to certificate verification at `0x5C1B60..0x5C1B64`.

`verifyCertificates` constructs `SigningKeys(SecurityParameter.getSigningKeys())` at `0x5C1B70..0x5C1B7D` and invokes `SigningKeys.verify(objects)` at `0x5C1B80..0x5C1B83`. That method has selector `0xAD7F38`, marker `0x8C13`, and method marker `0x5C23F5`. Its record has no inline Java bytecode body. Nearby fields are `keys`, `validKey`, and `isFirstCheck`; the constructor at `0x5C23DB` initializes `isFirstCheck` and retains the selected-security-JAR trusted-key array.

The strongest supported trust-order statement is:

```text
resource/class signer objects
  -> developer-token verification first
  -> if false, optional device SignedId verification
  -> trusted SigningKeys certificate verification
```

Developer-token success short-circuits the certificate branch. This is a package-authentication alternative inside AMS; it is not evidence of any PIN, diagnostic-session, service-certificate, or `/fs/etfs/AMS_DEVELOPMENT` transition.

## Incoming package-info preflight is different

The installed-launch path above must not be conflated with incoming URI inspection.

`AMSController.getPackageInfo(String,String,boolean)` at `0x5BB0A2` calls `Installer.getPackageInfo(String,String,boolean)`, selector `0xAD7438`, marker `0x8AB3`, method marker `0x5C07B4`.

`Installer.getPackageInfo` first determines whether the input maps to an installed application at `0x5C07BC..0x5C07C3`:

- installed branch: `xletPropertiesFromAppId` at `0x5C07CA..0x5C07CF`, then `getJarFile` at `0x5C07D1..0x5C07D7`;
- incoming URI branch: `checkIfExists(uri)` at `0x5C07DD..0x5C07E1`, `xletPropertiesFromUri(uri,authenticated)` at `0x5C07E2..0x5C07E7`, then `uriToFile(uri)` at `0x5C07EA..0x5C07EE`;
- both converge on `PackageInfo(properties,file.length())` at `0x5C07F1..0x5C0800`.

`xletPropertiesFromUri(String,boolean)`, selector `0xAD7BC8`, marker `0x8BA5`, method marker `0x5C02B8`, calls:

```text
resourceStreamFromUri(uri, "xlet.properties", null, authenticated)
```

at `0x5C02CE..0x5C02D6`. `resourceStreamFromUri`, selector `0xAD7C08`, marker `0x8BAD`, method marker `0x5C01D7`, converts an optional key `File` only when non-null at `0x5C01EA..0x5C01F6`, constructs a `VerificationClassLoader` at `0x5C01FC..0x5C021C`, supplies `SecurityParameter` only when `authenticated` is true at `0x5C020C..0x5C0218`, and requests the resource stream at `0x5C0231..0x5C0237`.

Because `xletPropertiesFromUri` passes null for the key file, incoming package-info preflight does not use the installed sibling `key.jar`. It follows the primary-URL authentication path over the direct incoming JAR; the recovered production form is conventionally signed, while a valid developer token can short-circuit certificate verification. `Installer.copyAndCheck` later splits that same archive into payload and fixed companion `key.jar`; installed launch then supplies the companion key URL. The complete split proof is in `reports/resident_incoming_jar_schema.md`.

## What is and is not proved

Confirmed:

1. `Installer` alone constructs the fixed `key.jar` sibling path; the filename is not descriptor-controlled.
2. Installed launch propagates that path through `AMSController`, `XletManager`, `XletClassLoader`, and `VerificationClassLoader.keyJar_`.
3. Existing companion-key lookup obtains signer objects from exactly `key.jar!/xlet.properties`.
4. Missing companion-key lookup falls back to primary application resource/class signers.
5. Developer-token verification precedes and can short-circuit device/certificate verification.
6. Certificate verification receives the promoted selected-security-JAR key array through `SigningKeys`.
7. Incoming URI package-info preflight passes no companion key file and uses the primary URL.

Not proved:

1. `getJarEntryCertificates(URL,String)` implementation details, including exact manifest processing and digest recomputation.
2. Whether runtime launch independently recomputes every cross-JAR member digest demonstrated by the offline corpus verifier.
3. `SigningKeys.verify(Object[])` chain building, accepted algorithms, ordering, revocation/time behavior, and `isFirstCheck` cache semantics.
4. How verified signer objects become principals, `CodeSource`, `ProtectionDomain`, or final policy grants.
5. Whether a missing `key.jar` could ever authenticate an unsigned payload. The structural fallback exists; acceptance does not follow from it.
6. Original live ZIP serialization and authorized issuer tooling. Physical `key.jar` creation and member routing are now proved in `Installer.copyAndCheck`.

## Safe design implications

The fixed sibling name is a platform contract, not an invitation to replace the stock file. A safe owner-authorized helper must use a legitimate issuance/package path that produces the expected payload/signature relationship. Renaming, substituting, omitting, or repacking `key.jar` is not justified; neither is relying on the missing-key fallback. No implementation should proceed until `SigningKeys`, signer-to-principal/policy assignment, authorized issuance, and cross-layer rollback behavior are proved or safely observed.
