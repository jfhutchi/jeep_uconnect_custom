# Hello Uconnect host artifact

Date: 2026-09-07. Source branch starting point `7e66353`.

**HOST-BUILT / UNSIGNED / NOT INSTALLABLE ON TARGET**

## Decision

The first independently authored RA4 Xlet now builds reproducibly as ordinary
Java 1.4 bytecode without a Kona SDK, QNX SDK, qcc, ARM compiler, JNI library,
custom Screen client or bundled target runtime. Two clean builds with the pinned
ordinary Temurin JDK 8 compiler produced an identical four-member JAR and
identical inventory.

This closes only host source compilation and dependency inspection.
It does not close package authentication, target installation or runtime
acceptance.

## Machine-verifiable result

```text
Hello Uconnect host artifact

Application classfile major:        48
Application native methods:         0
invokedynamic references:           0
Bundled compile stubs:              0
Bundled vendor runtime classes:     0
Custom native libraries:            0
JNI references:                     0
Networking references:              0
USB references:                     0
Vehicle-service references:         0
AppManager privilege references:    0
Autostart:                          false
Daemon:                             false
Audio app:                          false
Unexpected API references:          0
Artifact installability:            NO - accepted live JAR schema and authorized app ID/signer/principal/policy/DRM issuance unresolved
```

| Measurement | Actual value |
| --- | --- |
| Application JAR | `hello-uconnect.jar` |
| SHA-256, clean build 1 | `e3e7fa2cdffc179ea3b031f1744ad0d9958bb5a01b15fcdd3a253b777dc8bbb2` |
| SHA-256, clean build 2 | `e3e7fa2cdffc179ea3b031f1744ad0d9958bb5a01b15fcdd3a253b777dc8bbb2` |
| JAR bytes | 6,534 |
| Draft descriptor bytes | 452 |
| Audited installed-size estimate | 6,986 bytes: JAR plus draft descriptor only; signing/container/filesystem-allocation overhead remains UNKNOWN |
| Application class members | 4 |
| Compiler | Eclipse Temurin `javac 1.8.0_504` |
| Compiler archive SHA-256 | `ea43d46ede95b51e44a12c66711706cddc762e0a766c54bccea18954e902b2aa` |
| Compiler flags | `-source 1.4 -target 1.4 -encoding US-ASCII` |

Deterministic member inventory:

```text
com/jfhutchi/uconnect/hello/HelloUconnectXlet$1.class
com/jfhutchi/uconnect/hello/HelloUconnectXlet$2.class
com/jfhutchi/uconnect/hello/HelloUconnectXlet$3.class
com/jfhutchi/uconnect/hello/HelloUconnectXlet.class
```

The generated output remains ignored under
`prototype/hello_uconnect/build/out`. Rebuild with
`prototype/hello_uconnect/build.ps1`; the script reconstructs the declaration
classpath, application classes, deterministic JAR and all reports from tracked
source.

## Minimum development environment

| Concern | Status | Minimum actually required |
| --- | --- | --- |
| ARM/QNX compiler | **PROVED not required for Hello** | None. There is no native artifact. If a later native component is justified, the requirement is a QNX 6.5-compatible ARM32 little-endian ABI/link contract, exact startup/link objects and imported-library versions. qcc itself remains **UNKNOWN**, not proved indispensable. |
| Java/JamaicaVM/Xlet compilation | **PROVED host build; INFERRED target compatibility** | An ordinary pinned JDK 8 `javac` that emits major 48, Java SE compile classes and the reconstructed declaration classpath. No proprietary Jamaica compiler or bundled VM is used. JamaicaVM remains the stock target runtime and actual loading of this new identity is UNKNOWN. |
| Stock API/stubs | **PROVED signatures; INFERRED sufficiency confirmed for host compilation** | Declaration-only Xlet/LWUIT types and exactly referenced members. Provenance is in `prototype/hello_uconnect/compile_api/PROVENANCE.md`. The stubs are compile-only, contain no vendor implementation, and the validator proves zero are bundled. Target permission/support for a new identity remains UNKNOWN. |
| Package/descriptor | **PROVED logical descriptor fields; UNKNOWN accepted container** | A separate conservative `xlet.properties` draft with original UUIDv5 app ID, explicit main class, GUI true, daemon/audio false and no autostart or privilege field. The accepted incoming live-package layout/schema remains UNKNOWN; no KIM/BAR/ISO format is invented. |
| Signing/identity | **PROVED external gate; UNKNOWN legitimate route** | Issuer-approved app ID, signer/certificate route, signer-to-principal/policy construction, and any DRM/developer entitlement. No `key.jar`, certificate, token, trust-store edit, stock signer or stock identity is generated or reused. |
| Runtime/install | **PROVED stock lane; UNKNOWN custom acceptance** | Accepted install/register/uninstall acknowledgments, ordinary manual Apps launch, effective pause/stop/foreground/input behavior, bounded failure cleanup and documented app-specific rollback on an owner-authorized spare bench. Stock camera, climate, controls, critical/eCall, boot and recovery requirements remain unchanged. |

## Source and validator boundary

`HelloUconnectXlet` obtains the Xlet AWT container, makes it visible, initializes
LWUIT, queues its original surface through `Display.callSerially`, shows
`Hello Uconnect`, updates a counter through a button, and calls
`XletContext.notifyDestroyed()` from Exit. It creates no private thread.

The classfile validator parses class headers, constant-pool class/member
references and method flags. It enforces classfile major 48 and an exact external
owner/member allowlist, verifies that the descriptor main class exists at the
matching JAR path, rejects native methods and invokedynamic, and rejects bundled
compile stubs, vendor runtime classes, native libraries, JNI loaders,
networking, USB, vehicle/service and privileged AppManager owners. Descriptor
validation rejects autostart, daemon, audio, headless, privilege-like or
undocumented fields. Synthetic tests independently exercise every rejection
class.

## Remaining legitimate external gate

Before any target installation, obtain all of the following from a legitimate
issuer/provider route:

1. The accepted incoming package/container format and exact descriptor/member
   placement.
2. The authorized app-ID issuance and signer/certificate process.
3. The signer-to-principal and effective policy construction, including any
   required DRM or developer grant.
4. The stock install/register and documented app-specific uninstall/rollback
   route with explicit acknowledgments.
5. Target evidence that the new identity appears in the ordinary app inventory,
   launches only manually, receives/relinquishes foreground/input correctly,
   and cannot weaken stock camera, critical, climate, controls or boot behavior.

Until all five are satisfied, the generated JAR and descriptor are reviewable
host artifacts only and must not be presented as target-installable.

The [resident package format](resident_package_format.md),
[identity model](resident_identity_model.md), [signing chain](resident_signing_chain.md),
[policy/entitlement boundary](resident_policy_entitlements.md),
[install lifecycle](resident_install_lifecycle.md), and
[Hello gap matrix](hello_installability_gap.md) now specify those stages without
treating the proved factory installed layout as the still-unknown accepted live
single-JAR schema.

## Local verification

- 16 focused artifact-tool tests pass, including synthetic rejection cases.
- 185 `analysis_tools` tests pass from the recovered project virtual
  environment, including 23 package-inspector tests.
- 20 resident-HMI Node tests pass.
- Two complete clean Hello builds have identical JAR hashes and inventories;
  the generated skeleton inventory is SHA-256
  `af3518043de3cf65d61426114ce65e0c9009f88021f5d82a2d9e85ef4636a283`
  and its non-installability report is SHA-256
  `f9f713ec25ac3c442bcd619ed99aec1f8a578d2be13aad4c04ec59e35f84506d`
  in both builds.
- Python syntax compilation and `git diff --check` pass.
- Generated output is ignored; no stock or recovered vendor binary is tracked.
