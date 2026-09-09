# Hello Uconnect Installability Gap

> **Project status - 2026-09-07: BLOCKED without manufacturer support.**
> The software-only integration is effectively not achievable with the hardware
> and authorized access available to this project. Manufacturer-provided or
> approved development/service hardware, credentials, signing/entitlements and
> compatible licensed software are prerequisites; no sufficient route is confirmed.
> This document is retained as research or a conditional design, not an active
> deployment roadmap. The [current project status](../docs/00_project_status.md)
> supersedes earlier implementation priorities and defines reopening conditions.

## Result

Hello Uconnect remains a genuine, deterministic RA4-compatible Java/Xlet host
artifact and now has a machine-checked model of the proved factory installed
layout and live member-routing contract. It is structurally complete only
through original executable and logical descriptor generation. It is not an
authorized incoming package and has no
legitimate application-signing envelope, issued identity, policy/DRM grant, or
completed AppManager/AMS transaction.

The phrase "signing/package identity unresolved" can now be replaced with this
more exact boundary:

> An authorized FCA/Uconnect/Kona application process must allocate or accept
> the application identity, apply the proved live single-JAR package schema, bind the
> executable member set and signed descriptor to an accepted application signer
> or legitimately provisioned developer/device credential, construct the
> signer-to-principal and Java policy domain, issue effective DRM/manual-launch
> state, and submit that package through the stock AppManager/AMS install and
> uninstall lifecycle. The recovered corpus proves the schema, installed
> detached envelope, and runtime path but does not contain that issuance process
> or a byte-exact live incoming package sample.

## Current host state

- Application JAR SHA-256:
  `e3e7fa2cdffc179ea3b031f1744ad0d9958bb5a01b15fcdd3a253b777dc8bbb2`.
- Four original application classfiles, all major 48; no native/JNI, network,
  USB, vehicle service, AppManager privilege, bundled stub or vendor runtime.
- Logical app ID `4e9838d7-d08f-5f3a-be95-b309114fc22e` is project-local and
  unissued. It does not reuse a stock identity.
- Descriptor is non-autostart, non-daemon and non-audio and requests no
  privileged service integration.
- Generated `build/research-installed-layout` contains the executable,
  descriptor, proved `magic.txt` sentinel and explicit research status. It omits
  the payload-root signed descriptor and `key.jar`; the inspector correctly
  classifies it
  `incomplete-installed-layout-skeleton`, safe for the Hello profile but not
  structurally analogous to a complete stock package.

## Best-supported package/trust chain

```text
Hello Java source
  -> deterministic major-48 executable JAR                         PROVED
  -> proved single-JAR member packaging                            PROVED schema; absent for Hello
  -> signed package descriptor and executable-member manifest      PROVED stock shape; absent for Hello
  -> .SF digest + PKCS#7 signature + accepted public certificate   PROVED stock chain; absent for Hello
  -> legitimate app/developer/device identity issuance             UNKNOWN
  -> AMS certificate/token decision                                PROVED branches; live acceptance UNKNOWN
  -> Java principal + policy domain                                UNKNOWN
  -> DRM/manual-launch entitlement keyed by application ID         PROVED data/check; exact grant UNKNOWN
  -> authenticated AppManager/AMS install and registration         PROVED path; no Hello transaction
  -> generic Apps start, Xlet lifecycle, foreground and uninstall  PROVED static path; target proof UNKNOWN
```

## Gate matrix

| Gate | Status | Evidence | Missing requirement |
| --- | --- | --- | --- |
| Java/Xlet build | **PROVED** | Deterministic ordinary JDK 8 build; major 48; expected SHA-256; bytecode/API validator passes. | None for host compilation. |
| Package/container | **PROVED incoming and installed member schema** | AMS opens the submitted direct JAR and splits it into payload and `key.jar`; all 135 recovered signed production pairs invert consistently. | Authorized issuer output; one live sample remains useful only for byte-exact ZIP serialization. |
| Application identity | **PROVED field relations / UNKNOWN issuance** | App ID joins signed/installed descriptor, directory, DRM and AppManager; non-UUID IDs exist. | Authorized allocation/acceptance of Hello's app ID and any separate package/developer/device identity. |
| Signing | **PROVED stock content chain / MISSING for Hello** | Cross-JAR manifest digests, `.SF`, PKCS#7 `.RSA`, public signer certificate, fixed AMS `key.jar` association. | Authorized application signer or legitimate developer/device credential and packaging service; no private key is present or sought. |
| Policy/DRM | **PROVED layers / UNKNOWN construction** | Signed policy names/files, selected security configuration, AppMgrPermission checks, signed DRM grants and native checks. | Exact least-privilege GUI policy/principal rule and DRM/manual-launch grant for the issued Hello identity. |
| Installer | **PROVED transformation / UNKNOWN authorized artifact** | App media and catalog stage a JAR; AppManager performs authenticated preflight; AMS splits, installs/upgrades, and owns `prog.bak`; stock uninstall path exists. | Authorized ingress/package, safe bench transaction plan, and end-to-end native/DRM rollback behavior. |
| Target runtime proof | **UNKNOWN** | Static generic Apps/manual-start, Xlet lifecycle and cleanup paths are recovered. | Spare-RA4 observation of package acceptance, list visibility, foreground ownership, clean exit, uninstall and stock recovery without affecting camera/climate/controls/boot. |

## Machine-verifiable host result

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
Installed-layout key.jar:           MISSING BY DESIGN
Executable-root xlet.properties:    MISSING BY DESIGN
Accepted incoming package schema:   PROVED; fixture not generated
Artifact installability:            NO
```

No target attempt is justified until the authorized identity/signing/policy/DRM
issuance boundary is supplied and a safe owner-authorized bench plan exists.
