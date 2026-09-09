# RA4 AOA Transport Evidence Design

Date: 2026-09-09

Starting checkpoint: `a2daff8c5af6c091c8c199a7e4f75009c47f1169` on
`codex/ra4-wired-projection-feasibility`.

Working branch: `codex/ra4-aoa-transport`.

## Objective

Determine, to the strongest extent supported by recovered RA4 artifacts and
public protocol documentation, whether an Android phone can be negotiated into
Android Open Accessory mode through the RA4 cabin USB path and used for bounded
bidirectional bulk frames. The work stops at the AOA transport boundary and
does not implement the Android Auto projection protocol.

The investigation must decide whether already-authorized RA4 software can
exercise the necessary USB operations. The presence of a binary, library,
symbol, configuration rule, or dormant interface is evidence of capability or
intent only; it is not evidence of caller authority, runtime reachability, or
physical success.

## Safety And Authority Boundary

The work is host-side analysis of owner-supplied recovered artifacts unless an
existing legitimate execution route is proved. It will not bypass signing,
AMS, DRM, or trust checks; modify firmware or vehicle configuration; exploit a
component; access vehicle buses; or work on Yelp, 3G, or network restoration.

No new target executable, Xlet, native library, service, firmware image, or
installer package will be created unless the Phase-7 result proves that it can
run through a legitimate existing authorization route. Static compatibility
with QNX 6.5 or `libusbdi` is not such a route.

## Evidence Model

Each execution surface will receive exactly one primary disposition:

- `PRODUCTION CALLABLE`: an already-authorized component exposes a recovered,
  concrete, usable interface that can issue the required operation.
- `PRODUCTION INTERNAL`: production code performs the operation internally but
  exposes no proved caller-controlled route.
- `TEST/DIAGNOSTIC`: an installed authorized diagnostic surface exists, with
  its normal availability and invocation prerequisites recorded.
- `UNREACHABLE`: the artifact is present but its recovered activation or
  authorization boundary prevents use for this experiment.
- `REQUIRES NEW CODE`: the operation can be expressed by recovered APIs but no
  existing authorized caller is proved.
- `UNKNOWN`: the bounded evidence cannot support a stronger disposition.

Claims will distinguish direct static evidence, documented reference behavior,
inference, and physical proof. Negative claims will state the searched corpus
and its limitations. Recovered-artifact hashes and relative paths will anchor
all material target claims.

## Investigation Sequence

### 1. Execution Surface

Inspect stock-signed USB and media services, enumeration programs, iPod and
MTP/MTPZ handlers, normal diagnostics, production helper binaries, IPC/DBus
interfaces, Java/JNI wrappers, installed utilities, configuration rules, and
resident applications. Recover imports, exports, call sites, option/help text,
configuration consumers, service registration, activation chains, caller
inputs, and authorization boundaries.

The decisive question is whether an already-authorized component accepts
caller-controlled structured operations sufficient for AOA. Imports such as
`usbd_setup_vendor` and `usbd_io` prove only an internal dependency until a
concrete invocation route and argument contract are recovered.

### 2. Exact AOA Protocol

Use Google's public Android Open Accessory documentation as the protocol
authority. Model device detection, `GET_PROTOCOL`, ordered accessory identity
strings, `START_ACCESSORY`, detach, Google accessory VID/PID re-enumeration,
configuration and interface selection, bulk endpoint discovery, bounded frame
exchange, release, and reconnect.

For each control request, record `bmRequestType`, `bRequest`, `wValue`,
`wIndex`, payload, response, timeout, state transition, and error handling.
The model will not contain Android Auto messages.

### 3. RA4 Operation Mapping

Map every AOA state transition to a recovered RA4 primitive and concrete
implementation. The mapping will state whether the primitive is used in
production, whether its use is externally callable, required permissions or
ownership, whether new code is required, and every remaining unknown.

Kernel or driver sufficiency and caller sufficiency are separate decisions.
The recovered host stack may be technically adequate while the experiment is
blocked by the absence of an authorized caller.

### 4. Cabin Hub Transparency

Assess the `68141322AA` / `68289895AA` SD/USB/AUX hub and the recovered
phone-to-hub-to-radio topology for vendor control requests, detach and
re-enumeration, Google VID/PID visibility, descriptors, and sustained bulk
endpoints. Evidence of passive USB 2.0 routing, active mediation, class
filtering, power behavior, or an intelligent hub will be separated.

The final classification is one of `PROVED TRANSPARENT`,
`STRONGLY SUPPORTED`, `BENCH TEST REQUIRED`, `LIKELY BLOCKER`, or
`PROVED BLOCKER`. External instrumentation will be proposed only for a
specific unresolved physical-layer observation and will not be promoted to
proof of RA4-originated AOA negotiation.

### 5. USB Ownership

Trace the current Android insertion lifecycle from hotplug and enumeration
through descriptor classification, MTP/MTPZ selection, media ownership,
interface claims, retries, release, disconnect, and reconnect. Include the
behavior for unknown and vendor-class devices.

Identify whether AOA negotiation must run before an MTP claim, can coexist
during the control-only phase, or requires a narrow release/reclassification
hook. Record the narrowest ownership change that would be required, but do not
implement it unless the experiment remains entirely within proved production
behavior.

### 6. Dormant Projection Contract

Recover only USB-ownership-relevant behavior for `phoneProjectionService` and
`DeviceConnectionManager`: destinations, commands, arguments, events, owner
subscriptions, projection device types, lifecycle, USB relationship, HMI
activation, and expected service owner. Search the bounded recovered artifacts
for a matching implementation or shared/newer-platform provenance.

The dormant client contract, HMI vocabulary, and gateway rejection are not
evidence that a service owner exists or can be installed.

## Phase-7 Decision Gate

The evidence must select one classification before prototype implementation:

- `A`: existing stock-signed code can perform the target AOA test.
- `B`: the RA4 hardware/APIs are sufficient in principle, but the bench test
  requires new target code for which no current authorized execution route is
  available.
- `C`: external instrumentation can prove the RA4 path without new target code,
  with the exact mechanism and proof boundary stated.
- `D`: the current signing/execution boundary prevents a meaningful RA4 AOA
  test, with the missing prerequisite stated exactly.

An A or C result requires a concrete end-to-end route, not an analogy to an
existing utility. A C result must still demonstrate how the RA4-originated host
operations are issued; a passive protocol trace alone cannot do that.

## Conditional Implementation

If and only if Phase 7 is A or C, implement the smallest permitted deterministic
probe that detects one Android device, performs AOA negotiation, observes
re-enumeration, claims bulk endpoints, exchanges bounded deterministic frames,
releases resources, and exits. A companion Android test application may only
echo the bounded test frames.

If Phase 7 is B or D, do not create target-oriented build files or code. Create
`prototype/ra4_aoa_probe/` only if a host-executable protocol model materially
prepares the next legitimate step. That model must be labeled
`NOT TARGET VERIFIED` and consist of a USB host abstraction, deterministic mock
device, AOA state machine, bounded framing, and tests. It must not claim QNX ABI
compatibility, target authorization, cabin-hub success, or physical transport.

All implementation follows red-green-refactor TDD. Required cases include
protocol query success and failure, unsupported versions, control failure,
string ordering, start failure, detach timeout, wrong VID/PID, missing bulk
endpoints, partial reads and writes, mid-transfer disconnect, clean reconnect,
ownership conflict, and deterministic bidirectional framing.

## Deliverables

Create or update:

- `docs/ra4_aoa_transport.md`
- `docs/ra4_usb_execution_surface.md`
- `docs/ra4_android_usb_ownership.md`
- `docs/ra4_phone_projection_service.md`
- `docs/ra4_aoa_test_plan.md`
- `reports/ra4_aoa/aoa_state_machine.json`
- `reports/ra4_aoa/usb_operation_mapping.json`
- `reports/ra4_aoa/execution_surface.json`
- `reports/ra4_aoa/verification.md`

Any report generator will reject absolute local paths, unsupported evidence
promotions, missing source hashes, more than one next objective, and forbidden
Android Auto protocol scope. Generated JSON will be canonical and deterministic.

## Verification And Completion

Before completion:

1. Run every new test and the complete existing repository test suite.
2. Run every report generator twice and verify no diff after the second run.
3. Parse every generated JSON document.
4. Run `git diff --check`.
5. Recompute hashes for every recovered artifact cited by new work and verify
   the recovered artifacts themselves remain unchanged.
6. Recompute the original dirty checkout fingerprint and verify its branch,
   status, staged diff, unstaged diff, and untracked-file hashes are unchanged.
7. Reconcile the ten physical AOA success criteria individually. Anything not
   physically observed remains explicitly unproved.
8. Commit and push `codex/ra4-aoa-transport` without creating a pull request.

The final result will answer the requested fifteen questions and choose exactly
one next engineering objective. Android Auto receiver or projection-protocol
work remains outside this task.
