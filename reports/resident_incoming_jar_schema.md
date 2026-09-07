# RA4 Live Resident-Application JAR Schema

Date: 2026-09-07. Scope: static analysis of the canonical 18.45.01 recovery and
host-only inspection of already-extracted artifacts. No vendor executable was
run, no target was contacted, and no package, key, certificate, token, trust
store, policy, or DRM state was created or modified.

## Result

The remaining container ambiguity is resolved. The object submitted to secure
AMS is one direct payload JAR. It is not a wrapper around a nested executable
JAR or a nested `key.jar`. In the recovered production form it carries
conventional JAR-signature metadata. AMS opens the submitted file itself as
`java.util.jar.JarFile`, authenticates it, and splits its members into the
installed executable JAR and fixed sibling `key.jar`. The developer-token branch
can short-circuit certificate verification, so this report does not claim that
every legitimately issued development package must contain a certificate block.

```text
authorized issuer output: one direct <download-name>.jar
  |-- xlet.properties                         copied to payload and key.jar
  |-- application classes/resources/policy   copied to payload only
  `-- META-INF/MANIFEST.MF
      META-INF/<alias>.SF
      META-INF/<alias>.RSA or .DSA            copied to key.jar only
                |
                v
authenticated URI preflight (primary JAR URL, no companion key URL)
                |
                v
__newxlet__/
  |-- data/
  `-- prog/
      |-- xlet.properties                    normalized external descriptor
      `-- jars/
          |-- <incoming-basename>.jar        payload-member subset
          `-- key.jar                        signature subset + descriptor
                |
                v
install: rename __newxlet__ -> <xlet.appId>
upgrade: swap <appId>/prog via prog.bak; preserve <appId>/data
```

The exact ZIP byte stream cannot be recovered from the split files because ZIP
entry order, compression parameters, timestamps, extras, and central-directory
layout are lost. The member names and uncompressed member bytes are recoverable.
`reports/resident_incoming_transform_census.json` records a deterministic
content-set fingerprint, explicitly not a reconstructed archive hash.

## Disposition table

| Claim | Disposition | Evidence | Confidence | Remaining unknown |
| --- | --- | --- | --- | --- |
| The live input is the executable archive itself. | **PROVED** | `Installer.copyAndCheck(File,...)` constructs `JarFile(input)`; its compiled overload iterates `JarFile.entries()` and reads each `JarEntry`. Installer ROM class slot 376, wrapper bytecode `0x5BFA23..0x5BFA6D`; compiled member ordinal 2 at VA `0x1B3230` / file `0xB3230`. | High | Authorized issuer tooling and original archive bytes. |
| The live input contains a nested executable JAR. | **DISPROVED** | Non-signature entries of the submitted `JarFile` are copied through `JarOutputStream` into the installed payload. `xlet.jarFile` is overwritten with the submitted file's basename, not read as a nested-member selector. | High | None for this AMS implementation. |
| The live input contains a nested `key.jar`. | **DISPROVED** | AMS creates the fixed output file `prog/jars/key.jar` and routes signature members into it. A nested `key.jar` would be an ordinary payload member. `createNewXlet` anchors: key target `0x5BFB58..0x5BFB63`, copy call `0x5BFB65..0x5BFB70`. | High | None for this AMS implementation. |
| Signature material for the certificate path is on the outer/live JAR. | **PROVED** | Exact `String.endsWith` tests for `.MF`, `.RSA`, `.SF`, `.DSA` occur in compiled `copyAndCheck` at VAs `0x1B4B00`, `0x1B4B78`, `0x1B4BF0`, `0x1B4C68`; `JarEntry.getCertificates()` and `SigningKeys.verify(Object[])` are resolved calls in the same function. | High | Trust-chain acceptance internals and whether an authorized developer-token-success package omits blocks. |
| Root `xlet.properties` is package metadata and signed content. | **PROVED** | Preflight requests `xlet.properties` from the primary JAR URL; split logic compares the exact root name; all 135 installed inversions retain identical root copies in payload and `key.jar`, and all are manifest-covered. | High | Issuer-side field allocation rules. |
| The suffix rules are case-insensitive or accept `.EC`. | **DISPROVED for member routing** | The AOT code calls case-sensitive `String.endsWith` with exactly four uppercase literals. No `.EC` routing literal exists. `.EC` support elsewhere in Java crypto is not implied. | High | Whether a different firmware generation adds formats. |
| AMS creates `magic.txt` during live install/upgrade. | **DISPROVED for `Installer`** | `createNewXlet`, `install`, `upgrade`, and compiled `copyAndCheck` create only the payload, `key.jar`, external properties, and directories. `magic.txt` is absent from Installer's constants and member routing. | High for Installer | Whether a downstream non-Installer component could add a marker; no such writer was found. |
| `HB_CMC` is an AMS `Installer` authentication input for the live application JAR. | **DISPROVED for `Installer`** | AMS authenticates the primary JAR through `VerificationClassLoader` and the JAR signer path. `HB_CMC` occurs in KIM/download reference trees, not this parser or authentication path. | High for `Installer` | Exact factory-copy, download, or pre-Installer sentinel semantics remain unknown. |
| All recovered installed applications are inverse images of the conventionally signed split. | **PROVED** | Deterministic census: 135/135 split-consistent, zero inconsistent, zero unreadable/invalid; 65 distinct member content sets. Census SHA-256 `03159b95b64606bb92f0941413a884e59653584c3c1c5c6d4e347da64687255e`. | High | A byte-identical original live package sample is absent. |
| AMS `Installer` member routing requires a particular signer alias such as `CVP_APP_`. | **DISPROVED for `Installer` routing** | Routing recognizes suffixes, while ordinary JAR signing pairs `.SF` and block files by stem. Stock aliases are observations, not a literal alias allowlist in `Installer`. | High for routing | Any alias restriction inside AOT certificate extraction or `SigningKeys.verify`. |
| The recovered files provide legitimate signing/issuance authority. | **DISPROVED** | Only public certificates and opaque signed tokens are present; no private key, enrollment interface, or issuer service is recovered or generated. | High | Authorized issuer interface/specification. |

## Parser and transformation proof

The canonical AMS binary is
`analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/AMS`,
11,956,352 bytes, SHA-256
`96683b789ecf06a8575915d0b446b532e1f4ee87feb31d925cb7ba3d7d324d27`.
Its Installer class is ROM class slot 376 in file range
`[0x5BF5A8,0x5C0B88)`.

The bounded AOT registry at VA `0xC21424` has 1,138 classes and 6,668 members.
The tracked reader reports Installer member ordinal 2 as:

| Item | Address |
| --- | ---: |
| AOT member record | file `0xB31744` |
| method storage | VA `0xC67E08` |
| adapter | VA `0x112864`, file `0x12864` |
| `copyAndCheck(JarFile,File,File,String,String,String)` | VA `0x1B3230`, file `0xB3230` |
| next registered function bound | VA `0x1B7ACC`, file `0xB7ACC` |

Within that bounded function, the resolved constant pool and call graph include
`JarFile.entries`, `JarFile.getInputStream`, `JarEntry.getName`,
`JarEntry.getCertificates`, two `JarOutputStream` constructions,
`putNextEntry`, `read`, `write`, `closeEntry`, `SigningKeys.verify`, and the exact
member literals listed above. Three `putNextEntry` call sites occur at VAs
`0x1B4D2C`, `0x1B4DB0`, and `0x1B6034`; the third is the separately duplicated
descriptor path. `META-INF/` is tested with `String.startsWith` at VA
`0x1B5AC8`. This is entry-by-entry transformation, not a filesystem copy of a
nested archive.

The exact routing recovered for this firmware is:

| Incoming member | Installed executable | Installed `key.jar` |
| --- | ---: | ---: |
| exact root `xlet.properties` | yes | yes |
| name ending exactly `.MF`, `.SF`, `.RSA`, or `.DSA` | no | yes |
| every other non-directory member | yes | no |

The rule is suffix-based rather than restricted to `META-INF/`; conventional
JAR signing still places the observed files under `META-INF/`. The host
inspector deliberately mirrors the exact case-sensitive routing rule and
separately requires conventional `META-INF/MANIFEST.MF`, paired `.SF`, and
`.RSA`/`.DSA` structural metadata for a single-JAR candidate.

## Package-information preflight

`AMSController.getPackageInfo` at file `0x5BB0A2` delegates to
`Installer.getPackageInfo`. In the incoming branch, bytecode
`0x5C07DD..0x5C0800` checks the URI, calls
`xletPropertiesFromUri(uri, authenticated)`, resolves the same URI to a file,
and returns `PackageInfo(properties, file.length())`.

`xletPropertiesFromUri` calls
`resourceStreamFromUri(uri,"xlet.properties",null,authenticated)` at
`0x5C02CE..0x5C02D6`. Because the companion-key argument is null, authenticated
preflight runs the authenticated `VerificationClassLoader` path over the primary
JAR rather than an installed companion `key.jar`. The native AppManager supplies
`auth=true` before calling this AMS method. Therefore package information is not
a CRC-only or descriptor-only acceptance decision: catalog CRC is transport
integrity, followed by AMS developer-token short-circuit or certificate-path
authentication; a device token is checked before, but does not replace, the
certificate path. The recovered branch order does not prove that conventional
signer metadata is mandatory when a developer token succeeds.

## Install, upgrade, and normalization

`createNewXlet(String,Properties,String)`, code
`0x5BFA7F..0x5BFC89`, proves the filesystem transformation:

1. Trash any stale fixed `__newxlet__` staging directory.
2. Create `__newxlet__/prog/jars` and `__newxlet__/data`.
3. Read optional `xlet.developerToken` and `xlet.deviceToken` from the incoming
   root properties; recovered production copies are manifest-covered, while a
   successful developer-token-only profile is not available to characterize.
4. Resolve the incoming URI to a local file and retain its basename.
5. Create output targets `<basename>` and fixed `key.jar` under `prog/jars`.
6. Invoke `copyAndCheck` to authenticate and split the submitted JAR.
7. Set the external descriptor's `xlet.jarFile` to that basename and store the
   normalized Java properties at `prog/xlet.properties`.

This explains the previously observed production signed/installed filename
difference. In that recovered profile, the manifest-covered descriptor retains
issuer-stage history, while the installed external descriptor selects the actual
submitted basename. `xlet.appId` is not derived from the filename.

`install`, code `0x5BFCC8..0x5BFDB7`, performs authenticated descriptor loading
(`iconst_1` at `0x5BFCE2`), derives/validates the app ID, rejects an existing
target, calls `createNewXlet`, then renames `__newxlet__` to `<appId>`.

`upgrade`, code `0x5BFE94..0x5BFFCB`, performs the same authenticated load and
staging. If the app is absent it delegates to install. Otherwise it reconciles
`prog.bak`, renames current `prog` to `prog.bak`, renames staged `prog` into the
existing application directory, and removes backup/staging state after success.
The sibling `data` directory is not swapped, so application data persists
across this AMS program upgrade. `recoverProgIfNeeded`, code
`0x5BFE05..0x5BFE86`, restores `prog.bak` only when `prog` is absent and rejects
the state where neither exists.

## Identity and authentication contract

`getAppId(Properties,String)`, code `0x5C0002..0x5C00D0`, requires a nonempty
`xlet.appId` whose characters all occur in the literal
`0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_.-`. UUID syntax
is not required. No allocation authority or collision registry is present in
the firmware evidence.

The compiled split routine resolves both token alternatives and certificate
verification. It calls `SecurityParameter.getDeveloperId`, constructs
`SignedId`, obtains configured signing keys, and calls `SignedId.verify`; a
parallel device-ID path is present before certificate verification. In the
previously recovered verifier, developer-token success short-circuits the
certificate path; otherwise an optional device token is checked before
`SigningKeys.verify` receives signer certificate objects. This proves verifier
inputs and branch order, not the legitimate issuance interface.

The following remain **UNKNOWN**:

- accepted certificate-chain construction, certificate ordering, validity-time
  source, revocation behavior, allowed digest/signature algorithms beyond the
  observed corpus, and `SigningKeys.isFirstCheck` promotion/cache semantics;
- any hidden alias restriction beyond ordinary paired JAR-signature stems;
- developer/device ID enrollment and token issuance;
- signer-to-`Principal`, `CodeSource`, `ProtectionDomain`, and policy-domain
  construction;
- authorized `xlet.appId` allocation and collision checking;
- exact issuance rules for `featureMask`, `appLauncherMask`, `AppCategory`,
  `installerType`, manual launch, and autostart;
- AppManager/DRM registration transaction ordering outside the proved AMS file
  promotion.

These are authority and entitlement gaps, not remaining outer-container gaps.

## Recovered-package search boundary

A full recovered-tree inventory found 300 non-toolchain JARs: 296 files in KIM
installed layouts and four runtime libraries (`ams_initializer.jar`, `kona.jar`,
development `security.jar`, and production `security.jar`). No recovered
`usr/share/APPS` source directory, `/fs/mmc0/xlets/temp` staged application,
catalog download JAR, or deleted live package remains. The only recovered
download directory contains `download_ref.txt` and `magic.txt`; its reference
lists only `/fs/mmc1/download/magic.txt`.

Thus there is no byte-for-byte live/installed pair. The 135 inverse checks prove
member semantics, but not original ZIP serialization. The smallest missing
artifact for byte-exact confirmation is **one unmodified, legitimately issued
live incoming application JAR with its known installed counterpart**. The
smallest artifact for crossing the authority boundary is the **authorized
issuer/package specification or service interface** that allocates identity,
supplies an AMS-accepted signature and/or credential authentication profile, and
issues matching policy/DRM grants.

## Reproduction

```powershell
$ams = 'analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/AMS'
python -m analysis_tools.jamaica_aot_registry $ams `
  --registry-va 0xC21424 --class-count 1138 --class-slot 376

$py = 'analysis_work/post_reboot_20260906/venv/Scripts/python.exe'
$kim = 'analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages'
& $py -m analysis_tools.resident_package_inspect $kim `
  --scan-installed-tree --pretty `
  --output reports/resident_incoming_transform_census.json
Get-FileHash -Algorithm SHA256 reports/resident_incoming_transform_census.json
```

The inspector never emits a reconstructed JAR. For a single input JAR,
`structure.valid=true` means only that the visible members conform to the proved
shape; `installable` remains false because public structure cannot establish
issuer authority, AMS trust, policy, or DRM state.
