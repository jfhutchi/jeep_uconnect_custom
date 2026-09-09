# Hello Uconnect Xlet Design

> **Project status - 2026-09-07: BLOCKED without manufacturer support.**
> The software-only integration is effectively not achievable with the hardware
> and authorized access available to this project. Manufacturer-provided or
> approved development/service hardware, credentials, signing/entitlements and
> compatible licensed software are prerequisites; no sufficient route is confirmed.
> This document is retained as research or a conditional design, not an active
> deployment roadmap. The [current project status](../../00_project_status.md)
> supersedes earlier implementation priorities and defines reopening conditions.

Date: 2026-09-07. Approved by the owner's task specification. This design is
host-only: it does not authorize target installation, signing, registration or
execution.

## Objective

Produce the first independently authored RA4 application artifact: a tiny Xlet
that follows the recovered stock Xlet/AWT/LWUIT lifecycle, displays a counter,
increments it from a button, and voluntarily exits through
`XletContext.notifyDestroyed()`. The build must emit ordinary Java classfile
major 48 and prove that the application JAR contains no compile stubs, native
code, privileged APIs, bundled runtime, networking, USB or vehicle-service
dependencies.

## Evidence boundary

- **PROVED:** recovered RA4 applications are ordinary JARs containing ordinary
  Java classfiles. Selected stock application families use classfile major 48
  and 49. AMS loads application classes through its Xlet classloader path.
- **PROVED:** selected stock Xlets use the Xlet lifecycle, obtain an AWT
  container, initialize LWUIT, queue work through `Display.callSerially`, create
  forms and buttons, receive action events, and terminate through
  `XletContext.notifyDestroyed()`.
- **PROVED:** this Hello milestone has no need for JNI, a custom native Screen
  client, an ARM executable, a service, a projection engine or a private VM.
- **INFERRED:** an ordinary compiler that emits major 48 plus independently
  reconstructed compile-only declarations is sufficient to compile this Java
  source. The finished JAR and validator make that inference reproducibly
  testable without treating the declaration JAR as a vendor SDK.
- **UNKNOWN:** the accepted incoming live-package container, legitimate issuer
  and signer, signer-to-principal/policy construction, effective DRM or
  developer grant, app-ID issuance, install/uninstall route, foreground
  ownership, lifecycle acceptance and completed stock recovery on a spare RA4.

## Architecture

The source tree has three deliberately separated layers:

1. `compile_api` contains declaration-only Java sources for the exact non-Java-SE
   types and members referenced by Hello. It is compiled to a host-only classpath
   JAR and is never copied into the application payload.
2. `src` contains the original Xlet. It uses only the recovered lifecycle and
   LWUIT surface. It creates no threads; UI work is handed to the stock LWUIT
   serial queue. Pause is passive, destroy drops local references, and the Exit
   action calls `notifyDestroyed()`.
3. `tools` constructs a deterministic stored ZIP/JAR and validates each class's
   header, constant pool, member flags and referenced owners/members against an
   explicit allowlist. It also validates the conservative draft descriptor and
   writes deterministic inventory, dependency, hash and size reports.

`build.ps1` requires an ordinary JDK 8 `javac`/`jar` pair because JDK 8 can emit
`-source 1.4 -target 1.4`. It must fail if the compiler emits any major other
than 48. Python 3 standard-library tooling packages and audits the output. The
application JAR contains only original application classes; the draft
`xlet.properties` remains a separate logical package input.

## Descriptor and identity

The logical app ID is the deterministic UUIDv5
`4e9838d7-d08f-5f3a-be95-b309114fc22e`, derived from the repository URL and the
`hello-uconnect` name. It is project-specific and does not reuse a stock ID.
Only fields already evidenced in recovered descriptors are used. The descriptor
requires GUI mode, disables daemon and audio behavior, contains no true
autostart field, and names the original main class. It is prominently marked
`HOST-BUILT / UNSIGNED / NOT INSTALLABLE ON TARGET`.

## Safety and failure policy

No output is a flash image or accepted RA4 package. No trust-store, DRM,
`security.jar`, stock Xlet, registry or signed stock artifact is modified. The
validator rejects privileged AppManager, network, USB, vehicle/CAN/service,
JNI/native and bundled-runtime references. A future bench attempt remains
blocked until the legitimate package/identity gate and the separate lifecycle,
foreground, rollback and recovery gates are passed without weakening stock
camera, climate, controls or boot behavior.

## Acceptance

The local build is acceptable only when repeated builds produce the same JAR
member inventory and SHA-256; all application classes are major 48; all audited
prohibited/reference counts are zero; the descriptor is non-daemon,
non-autostart and non-audio; focused rejection tests pass; the repository's
existing test suites pass; and generated binaries remain ignored.
