# Hello Uconnect host artifact

> **Project status - 2026-09-07: BLOCKED without manufacturer support.**
> The software-only integration is effectively not achievable with the hardware
> and authorized access available to this project. Manufacturer-provided or
> approved development/service hardware, credentials, signing/entitlements and
> compatible licensed software are prerequisites; no sufficient route is confirmed.
> This document is retained as research or a conditional design, not an active
> deployment roadmap. The [current project status](../../docs/00_project_status.md)
> supersedes earlier implementation priorities and defines reopening conditions.

**HOST-BUILT / UNSIGNED / NOT INSTALLABLE ON TARGET**

This directory builds an independently authored Xlet using an ordinary Java
compiler and clean-room compile-only declarations. It contains no projection
engine, native code, JNI, networking, USB, CAN/vehicle-service access,
AppManager privilege, background service, audio ownership, persistence,
autostart or boot integration.

## Prerequisites and build

- The ordinary Eclipse Temurin JDK 8 compiler pinned in `toolchain.json`. Its
  `javac -source 1.4 -target 1.4` mode emits the directly observed classfile
  major 48. The script rejects a different compiler version so the recorded
  artifact hash remains reproducible; this is a host-tool lock, not a Kona/QNX
  SDK requirement.
- Python 3.11 or later. The build/validator uses only the standard library.
- PowerShell 7 or Windows PowerShell 5.1.

From the repository root:

```powershell
./prototype/hello_uconnect/build.ps1 -JdkHome 'C:\path\to\jdk8' -Python 'C:\path\to\python.exe'
```

The script deletes and recreates only `prototype/hello_uconnect/build`, compiles
the declarations into `build/work/compile-api-classes`, compiles the original
Xlet against that directory, packages only `build/work/application-classes`, and
writes reviewed output to `build/out`. It fails if any class is not major 48 or
if any symbolic dependency falls outside `api-allowlist.json`.

`build/out` contains:

- `hello-uconnect.jar` - original application classes only;
- `xlet.properties` - logical draft descriptor, separate from the JAR;
- `BUILD-STATUS.txt`, bytecode/dependency JSON, deterministic member inventory,
  SHA-256 manifest and installed-size estimate;
- this build instruction file and the pinned ordinary-JDK toolchain record.

Generated output is ignored by Git. `reports/hello_uconnect_host_artifact.md`
records the verified reproducible hash and measurements from the committed
source instead of committing a binary.

The build also writes `build/research-installed-layout`, a host-only model of
the proved factory post-install directory shape. It deliberately omits
the payload-root signed descriptor and `prog/jars/key.jar` and is labeled
`UNSIGNED / NON-INSTALLABLE / RESEARCH ARTIFACT`.
`build/out/installed-layout-research-report.json` must classify it as an
incomplete skeleton. The live single-JAR member schema is now proved, but this
build intentionally does not wrap or sign Hello and is not an issuer-produced
package accepted by AMS.

## Gate boundary

The host compile tests only the strong inference that recovered signatures are
sufficient for ordinary Java source compilation. It does not create or imply an
accepted incoming package. The following remain unresolved external/runtime
gates: legitimate issuer/package-signing route,
signer-to-principal/policy construction, DRM/developer entitlement, app-ID
issuance, install/uninstall, foreground ownership, lifecycle acceptance and
completed stock recovery. Do not create a fake `key.jar`, reuse a stock identity,
patch trust or DRM, modify installed Xlet/QDB state, or install this unsigned
artifact on a target.
