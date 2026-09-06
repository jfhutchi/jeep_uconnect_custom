# 16 - RA4 resident projection component placement

Updated 2026-09-06. This decision separates four concerns that earlier plans
risked conflating: stock projection UI, application identity/lifecycle, the
stock-facing backend adapter, and the licensed phone-projection engine. It is
based on recovered RA4 18.45.01 control flow and is static/read-only. It does
not authorize package creation, installation, service calls, radio writes, or
any signature/authentication workaround.

## Decision

The smallest credible resident-first product has this placement order:

1. Reuse the existing stock projection branch and its assets if the complete
   `DeviceProjection.swf` artifact and supported loader are present.
2. Use the proved secure AMS/AppManager Xlet lifecycle for a separately
   authorized, non-autostart application identity or control shell if stock
   projection-screen reuse cannot supply an independent lifecycle.
3. Add a tiny native service only for a specifically proved backend gap and
   only through a supported servicebroker/ModuleLink registration contract.
4. Keep the licensed CarPlay/Android Auto engine separate from all three. It
   remains local only if an authorized RA4-compatible build fits the full
   resource and runtime gates.

This is a component-placement decision, not a claim that any new package is
currently authorized. It also does not select an external engine merely because
the resident interfaces are incomplete.

## Confirmed RA4 lanes

### Stock projection lane

- `IPhoneProjection.sessionActive` is read at reconstructed FWS
  `0x002588DF` inside `0x002588C5-0x002589A8`.
- Session state and the visible `DEVICE_PROJECTION` branch are independent;
  auto-show navigation occurs at `0x0025892C`.
- `startProjection(ppId)` at `0x002B5177-0x002B519E` is a session-start
  command, distinct from navigating back to an already active session.
- `PhoneProjectionEvent`, `PROJECTION_BACKTO_CAR`,
  `phoneProjectionService`, and `IPhoneProjection` are stock references.
- The physical `DeviceProjection.swf` payload, its loader/descriptor, and the
  implementation of `phoneProjectionService` are not yet established.

Therefore the preferred UI result is conditional: an already-installed stock
projection screen would minimize new assets and preserve OEM navigation, but a
string/class reference alone does not prove that screen exists or can render.

### Secure application lane

The ordinary authorized Xlet lifecycle is directly recovered:

```text
secure AMS startup
  -> /fs/mmc1/xletsdir
  -> authorized non-autostart Xlet remains stopped
  -> AppsMainScreen.onItem
  -> IAppManager.startXlet(appId, "MoreScreen")
  -> ModuleLink AppManager startApp envelope
  -> native parseRequest("startApp")
  -> findAndStartApp(appId, DRM-check = 1)
  -> App::start()
  -> AMS-facing start
  -> stock foreground arbitration
```

Evidence anchors:

- `jvm.sh:58-63` starts AMS with `-secure` and the selected factory security
  configuration; development selection does not remove secure mode.
- The AMS install root is `/fs/mmc1/xletsdir`.
- ROV `AppsMainScreen.onItem` calls `IAppManager.startXlet` at FWS
  `0x0000C1E6`.
- ROV ModuleLink `AppManager.startXlet` is code `0x002A971A`, emits
  `startApp` at `0x002A97E1`, and sends at `0x002A97E7`.
- Native AppManager compares/dispatches `startApp` at file
  `0x00053DD0/0x00053DF0`, supplies DRM-check byte one at
  `0x00050650`, and calls `findAndStartApp` at `0x0005066C`.
- Stock foreground admission and pending retry are at
  `0x0025250E-0x002525D2` and `0x002524C4-0x002524FD`.
- Generic returned applications are appended by the stock Apps catalog; no
  later generic per-app enabled/hidden field is consumed by that HMI builder.

This proves a stock lifecycle for an already authorized application. It does
not prove that a new project can obtain a valid signer/token/DRM grant, that an
Xlet can own the required Screen surface, or that it can bind the projection
backend.

### Stock-facing service lane

ModuleLink, a configured localhost endpoint, servicebroker,
`phoneProjectionService`, MME, AudioCtrlSvc, and `audioApp -> MME` are
recovered names or configurations. The registration schema, caller
authorization, version negotiation, owner-death behavior, display surface,
touch route, audio source acquisition, microphone lease, and projection
backend ABI remain unknown. No direct socket or guessed message is acceptable.

## Placement consequences

| Component | Preferred resident placement | Evidence status |
| --- | --- | --- |
| projection UI | existing stock projection branch and assets | references confirmed; physical payload/loader unknown |
| app identity and user launch | secure non-autostart Xlet returned in stock Apps list | lifecycle static-proved; new-package authorization external |
| ownership policy | transport-free C arbiter behind a narrow adapter | host model proved; target ABI/build unproved |
| backend integration | smallest supported ModuleLink/servicebroker client or provider | service names confirmed; registration/schema unknown |
| video/touch | one stock-managed Screen surface, touch only while selected/unobscured | reference/config confirmed; exact RA4 contract unproved |
| call/message presentation | volatile default-open presentation lease after HFP/MAP ingestion | policy model proved; supported stock hook unproved |
| camera/comfort/critical | no adapter command; stock managers remain autonomous | static/model behavior proved; target timing unproved |
| projection engine | licensed local RA4-compatible build if it passes gates | vendor family found; compatible build and sizes external |

An authorized Xlet is not assumed to be the video decoder. Its most credible
role is application identity, user-visible launch/control, session observation,
and a bounded bridge to an independently authorized backend. Conversely, a
native backend must not seize foreground or replace the stock shell.

## Resource envelope

The first no-engine resident trial keeps the existing sublimits:

| Item | Planning ceiling |
| --- | ---: |
| authorized Xlet/control shell, descriptors, minimal original assets | 0.50 MB |
| native adapter plus transport-free arbiter, if proved necessary | 0.25 MB |
| private glue dependencies | 0.50 MB |
| packaging/allocation uncertainty | 1.75 MB |
| installed no-engine trial total | 3.00 MB |
| normal writable growth | 1.00 MB |
| additional staging/rollback peak | 6.00 MB |

These are ceilings, not measured sizes. Reusing a preinstalled projection
screen counts as zero new installed bytes only after its presence and permitted
reuse are proved. Detached signature envelopes, filesystem allocation, AMS
registry growth, Xlet RMS, logs, crash files, temporary install copies, and
failed-update residue all count.

The complete local product still must remain at or below 15 MB installed, 4 MB
normal writable growth, and 8 MB additional staging while preserving 45 MB of
the approximately 77 MB observed free space and at least 5 MB residual margin.
A full duplicate installation is not assumed.

## Exact evidence gates

| Gate | Evidence that closes it |
| --- | --- |
| existing screen | hash and relative path for the complete `DeviceProjection.swf`, its descriptor/loader, and its imports/consumer XREFs |
| return/resume | complete `PROJECTION_BACKTO_CAR` consumer and proof it navigates without another `startProjection` |
| authorized identity | written supported developer/DRM/package route or a legitimately issued inert signed sample; no credential material belongs in Git |
| backend registration | servicebroker/ModuleLink provider/client schema, version, permissions, reconnect and owner-death semantics |
| Screen/touch | exact group/class, buffers, z-order, focus/sensitivity, transform, cancellation and teardown |
| audio/voice | exact source registration, priorities, duck/pause callbacks, call route, microphone acquisition and owner-death |
| engine | RA4/QNX 6.6 ARM32 support, program authorization, component bytes, RAM/CPU/video/USB/audio requirements |
| target behavior | separately authorized spare-hardware observation of launch, camera, popup, calls/messages, crash fallback and storage peaks |

The read-only `qnx_media_runtime_probe.py` now includes exact stock projection
and RA4 secure-lifecycle anchors. Its redacted JSON flows into
`qnx_runtime_correlation.py`, which provides only an inspection order.
A positive tier still needs imports, XREFs, startup evidence, and an authorized
interface contract.

## Current conclusion

The software-only maximum is no longer an unspecified replacement HMI. It is a
small OEM-launched identity/control shell, stock projection surface where
present, tiny policy adapter, and a separately qualified local engine. The
stock Xlet launch lane is static-proved for authorized applications; new-package
authorization, the projection service schema, the physical projection screen,
and a compatible licensed engine remain external evidence requirements.

No current evidence forces the adapter or control shell to external compute.
Only the engine may later become `EXTERNAL_COMPUTE_REQUIRED`, and only after a
legitimate resident candidate fails compatibility or measured resource gates.
