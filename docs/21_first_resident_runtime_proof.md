# First future resident runtime proof: original, manual, no engine

Date: 2026-09-06. **Specification only. No target package has been created,
authorized, deployed or executed.** Work remains on the host until the gates
below are resolved and a future target experiment is separately authorized.

## Artifact and package lane

The first candidate is an independently authored, non-autostart **Kona/AMS
Xlet control application**, delivered through the legitimately authorized stock
application-package route. Use the supplier-approved signed package schema
(Xlet code/JAR, descriptor, signer metadata and any required entitlement).
Do not invent a KIM, BAR or ISO extension/manifest and claim the radio accepts
it. KIM factory distribution is evidence for stock Xlets, not a template to
modify. The exact acceptable live-package format is an EXTERNAL_PROVIDER_GATE.

The [placement decision](16_ra4_resident_placement_decision.md) and
[manual launch evidence](../reports/app_launch_ui_path.md) justify this lane:
authorized installation -> stock application inventory -> ordinary Apps entry
-> `startXlet` -> native DRM-checked `startApp` -> AMS lifecycle. Secure AMS
and the applicable signer/developer policy remain intact. Prefer an authorized
production-mode package; an engineering service certificate or development
identity is needed only if the provider's documented path actually requires it.

Display one original 640x480 test surface: a solid rectangle, an application
label, a manually incremented counter and a stock-supported Exit/Return action.
Use existing permitted fonts or a tiny original asset. No phone engine, USB
client, audio source, background networking, vehicle controls or automatic
launch. Do not load code into the stock main SWF or assume another ADL process.

The [stock Xlet view trace](../reports/ra4_resident_xlet_view_path.md) now proves
two application callers of XletContext.getContainer, AWT visibility and LWUIT
Display/Form APIs, corroborated by matching AMS ROM class metadata. This makes
Xlet/AWT/LWUIT the concrete candidate view API family. Custom-app acceptance,
usable display area, input focus and failure isolation remain unproved. A
supplier must confirm compatible API support and stock foreground registration.
The [stock handoff trace](../reports/ra4_xlet_foreground_handoff.md) distinguishes
screen exit (a pause request plus release of the `ams` display request) from
Close (an explicit stop request). The [native pause-policy trace](../reports/ra4_xlet_pause_watchdog.md)
shows that pauseApp itself selects stop when `xlet.PauseAllowed` is false;
the recovered field default is false. Require supported descriptor semantics
and the effective value for the legitimate new app before the Return trial.
The Java wrapper checks `AppMgrPermission("appMgr")`; that is an observed
permission check, not authorization for a custom app. The normal native
`requestBackground(appId)` event uses the configured SuperApp UUID, so it must
not be assumed to implement Return for an arbitrary new Xlet. Require a
supported action for the legitimate new identity without changing stock identity.
The [display-owner trace](../reports/ra4_display_owner_reclaim.md) follows that
request through LayerManager to native Screen visibility. LayerManager also
reacts to AMS service-owner changes by hiding the AMS window key and restoring
default layer orders. That watches the shared service, not each Xlet; it cannot
establish recovery from an app hang while AMS remains registered. The policy's
returned grant does not validate the discarded device write/read results.
The native per-app watchdog can queue stopApp after an enabled watch expires;
it does not directly reclaim the window/input in that timer handler. Live
activation, supported custom registration, timing and completed recovery remain
unproved. Do not count a queued stop or conditional daemon restart as fail-open
recovery or healthy session preservation.
The [result-completion trace](../reports/ra4_xlet_result_completion.md) also
shows that stop bookkeeping can advance despite a NoReply error, selected AMS
stop errors can be normalized to zero, and failed JSON parsing can coexist with
a zero-code app event. Require raw response/error and parse-validity evidence
alongside the normalized event. Neither an app inventory state nor that event
alone proves lifecycle completion, display/input release or failure containment.
The [AMS cleanup trace](../reports/ra4_ams_destroy_cleanup_contract.md) resolves
the normalized stop errors as Xlet exception (8), AMS TIMEOUT (12) and incomplete
thread termination (20). It traces stock LWUIT/GLES cleanup and explicit Xlet
container removal, including selected exception paths. The timeout runner's
AOT entry and selected paths are now traced; native input/window effects remain
unproved. Retain raw errors even when the normalized result is zero; cleanup
calls and compiled timeout defaults cannot substitute for completed recovery.
The [container/focus follow-up](../reports/ra4_xlet_container_focus_cleanup.md)
identifies the conditional default frame and its AWT detachment/focus cleanup.
Confirm the effective frame factory for the approved package. Shared tree-lock
acquisition, conditional focus transfer and selective event removal must not
be mistaken for bounded native input cancellation or stock foreground recovery.
The [compiled timeout trace](../reports/ra4_ams_aot_timeout_runner.md) now proves
normal and selected exception dispatch to runFinally, alongside action timed
waiting and an AMS TIMEOUT producer. Require separate completion evidence for
the worker action and synchronous finally hook; a wait ending or a hook being
called cannot certify that the worker terminated or shared UI cleanup returned.
The [worker/interruption trace](../reports/ra4_ams_worker_interruption.md) also
shows that both worker return and the caller's timeout fallback can set the
same done flag. The worker normally continues to its queue after an action.
Require evidence of actual action exit, interruption/fallback origin and late
activity, distinguishing worker reuse from app-created thread termination.
The [interrupt/cleanup trace](../reports/ra4_ams_interrupt_request_cleanup.md)
also distinguishes pending AIE and native interrupt status from action exit.
Group cleanup requests blocking-I/O interruption before checking its join
deadline, then has another join pass during escalation. Qualify the supported
native-I/O cancellation contract and observe total cleanup time; a configured
thread timeout does not cover the whole sequence by itself.
The [native I/O and Screen trace](../reports/ra4_native_io_screen_wait.md)
resolves six callback bodies and the stock platform-screen caller's positive
2000000000 wait argument, forwarded to screen_get_event. Callback Booleans
do not uniformly check the underlying operation. The finite wait argument
does not bound the whole event loop, shared locks or recovery. The linked
event-post method throws unsupported-operation, and native window/context
destruction differs from app-container detachment. Require the supported
per-operation cancellation contract, actual event-loop return and restored
stock contacts/focus; do not use whole-context destruction as a Return action.
If the approved Xlet shares a VM with critical
stock apps, obtain bounded scheduling/memory and failure-containment evidence
before use. If those cannot be established, reject this implementation lane;
qualify a supported isolated native package rather than injecting a surface.

## Required APIs and evidence before any trial

| Prerequisite | Evidence required before proceeding | Current status |
| --- | --- | --- |
| Legitimate package identity | Issuer-approved package schema, signer identity, permission set, target release and any required entitlement/developer identity | EXTERNAL_PROVIDER_GATE |
| Compatible build | Authorized QNX 6.5 ARM32 / Kona toolchain and API stubs; reproducible source build; documented permitted stock dependencies | EXTERNAL_PROVIDER_GATE |
| Stock install/register/uninstall | Exact supplier-supported interfaces and acknowledgments, non-autostart descriptor semantics and per-app rollback contract | STATIC_PROVED stock chain; UNKNOWN custom runtime |
| Manual launch | Package appears in stock `getAppList`; ordinary Apps entry uses factory DRM-checked launch | STATIC_PROVED stock route; UNKNOWN custom acceptance |
| View and input | Supported app-owned 640x480 area, focus/release semantics and identity recognized by stock foreground arbiter | STATIC_PROVED stock Xlet/AWT/LWUIT calls and AMS metadata; UNKNOWN custom dimensions, permission and arbitration |
| Foreground priority | Camera, critical/eCall and comfort-overlay precedence enforced outside the custom app; denial/loss events cannot be vetoed by it | STATIC_PROVED admission, conditional pause/stop and display-release request; UNKNOWN custom integration and completed reclaim |
| Return/session continuity | Supported action and effective PauseAllowed for the new identity; legitimate engine session owner survives permitted pause | STATIC_PROVED false/default selects stop and wrappers submit asynchronously; UNKNOWN custom permissions, completion and engine continuity |
| Failure containment | No boot dependency or autostart; bounded resources; stock-owned reclaim on exit, disappearance and unresponsive app; distinguish app failure with AMS alive from AMS owner loss/hang | STATIC_PROVED AMS owner-change hide/order and enabled-watch expiry stop queue; UNKNOWN live activation, bounded completion, input reclaim and target guarantee |
| Baseline and storage | Exact-unit stock health baseline, current writable free blocks, package manifest and allocated-block accounting; update state idle | UNKNOWN future measurement |
| Recovery authority | Supported app-specific stop/uninstall remains reachable without the custom view or process; raw errors, parse validity, normalized result and registry/data reconciliation documented | STATIC_PROVED callback/state bookkeeping can advance despite errors; UNKNOWN completed runtime rollback |
| Experiment setting | Owner-authorized spare bench unit and supplier-supported camera/critical-state validation method, stable power and recovery provisions | External prerequisite; no vehicle operation authorized here |

Expected semantic APIs: Xlet initialize/start/pause/destroy lifecycle, authorized
AppManager install/list/start/stop/uninstall, stock app identity and foreground
request/loss notifications, permitted view create/draw/input/release, and
bounded app-local state if needed. The view trace records observed Java method
signatures, but a compatible SDK must confirm their supported use, lifecycle
and permissions. The stock Java `appMgr` permission identifier is observed;
custom grants, native surface handles, bounded IPC completion and independent
foreground/input reclaim remain unresolved.

## Installed-size estimate and resource accounting

These are **allocation targets, not measured package sizes**. Count manifest,
signer/descriptor/entitlement overhead, alignment and private dependencies.

| Incremental trial component | Provisional installed allowance |
| --- | ---: |
| Original application code and control logic | 512 KiB |
| Original tiny visual assets/defaults | 128 KiB |
| Legitimate package metadata, signatures and entitlement overhead | 128 KiB |
| Necessary private binding code | 256 KiB |
| Filesystem allocation, uncertainty and remaining headroom | Remainder up to 3,000,000 bytes |

Enforce **<=3 MB installed** for the no-engine proof, with no bundled VM,
browser, fonts, SDK or engine. If a required private runtime pushes it above
that limit, stop and revise the approved artifact. This trial does not prove
the complete projection product can fit <=15 MB.

Plan <=1 MB attributable normal growth and <=6 MB additional staging/rollback
for the trial, within the product's <=4 MB and <=8 MB limits. From the historical
~77 MB free-space observation, the trial's 3+1+6 MB peak leaves ~67 MB; the full
product's 15+4+8 MB peak leaves ~50 MB, comprising >=45 MB protected reserve and
>=5 MB residual. Approximate historical free space is not current approval.
Require fresh allocated-block measurements and count AMS/stock-runtime logs or
cache attributable to the app. A 640x480 RGBA buffer's 1,228,800 bytes are RAM,
not installed storage; pitch, extra buffers and heap add to that cost.

## Future execution sequence and acceptance record

This sequence is a design; there are no executable radio commands here.

1. **Authorization and baseline:** verify the approved package hash, issuer,
   permissions, target version, stock health and available blocks. If any
   prerequisite is missing, do not install. Record stock boot/camera/HMI timing
   and failures before introducing the app.
2. **Install/register:** use the authorized stock installer, record explicit
   success, and verify the unique original app identity appears exactly once.
   Confirm it remains stopped. Do not modify a global autostart flag to obtain
   that result.
3. **Manual launch:** use its ordinary stock Apps tile. Record acceptance/error
   from the stock lifecycle and foreground arbiter. If foreground is denied,
   the app must remain non-visible without retry loops or focus stealing.
4. **Trivial render/input:** observe the original rectangle/counter at 640x480,
   update it only on an accepted app input, and measure allocations/CPU. No
   projection or vehicle-control interface is involved.
5. **Stock priority:** through the supplier-approved bench procedure, verify
   factory camera and comfort overlays preempt correctly. Critical/eCall
   validation needs a supported simulation/test mode; do not place emergency
   calls or inject CAN to manufacture a state. If that proof is unavailable,
   the trial does not pass the coexistence gate.
6. **Return, resume and explicit close:** use the supported Return action for
   the new identity with qualified effective PauseAllowed; record which
   lifecycle action was selected. Record pause and display-release completion
   independently, and observe stock foreground/input restoration. Re-enter through the ordinary
   supported app route and check the counter/state and resume acknowledgment.
   Then use explicit Close/stop and verify the app is stopped. A background
   request's zero response, a dispatched Resume, or navigation alone does not
   establish those completion states. Release only app-owned resources.
   Correlate app identity and operation with raw response category, raw AMS
   error when present, reply parse validity and normalized event code. An
   AppManager stopped record or appStopped/appPaused event is insufficient
   without confirmed lifecycle and presentation/input completion.
7. **Failure containment:** only after documented isolation exists, test the
   approved app-only failure/unresponsive scenario on the spare bench. Stock
   must reclaim presentation without relying on custom cleanup. Never terminate
   a shared stock VM/service or install an intentional boot hang to test this.
   Specifically require recovery while AMS remains alive and registered; its
   service-owner callback does not cover that case. Record native visibility,
   input/contact release and stock interaction separately from a policy grant.
   AMS disappearance or VM-hang recovery needs separate supplier evidence and
   cannot be substituted for this app-specific result.
   If a supported per-app watchdog is used, record its enabled state and
   expiry-to-stop-completion and input-reclaim timing. A queued stop request,
   timer counter, successful IPC submission or daemon restart is insufficient.
   Record action completion, app-thread disposition and main-frame container
   removal independently of native visibility/input release. Retain raw AMS
   8/12/20 and distinguish AMS TIMEOUT from D-Bus NoReply. Record configured
   and effective timeout values separately from measured elapsed recovery.
   Correlate worker-action entry/exit, interruption callback, caller timeout
   fallback and finally-hook entry/exit by action identity. Raw AMS TIMEOUT
   does not distinguish its two traced producers; record unknown origin when
   evidence is absent. Do not substitute done_ for actual action exit. Verify
   that late work cannot reacquire display/input or access disposed app
   resources. A continuing stock action worker is distinct from surviving
   app-created threads; record both without requiring the shared worker to die.
   Distinguish pending AIE, native interrupt status, blocking-I/O request
   completion, deadline-based joins and the later escalation joins. Observe
   total elapsed cleanup, surviving app threads and context finalization even
   on error 20. The supported native-I/O contract must cover the app's actual
   operations and cancellation callbacks; do not register an unqualified native
   hook or infer cancellation success from a flag. Shared mutex acquisition
   and callback completion need their own containment evidence.
   Identify the effective main-frame implementation and observe child detachment
   and Java focus cleanup separately from native contact cancellation. Supplier
   isolation evidence must cover shared AWT locks as well as app lifecycle calls;
   do not terminate/dispose a shared stock frame to simulate app-only cleanup.
8. **Uninstall:** use supported app-specific removal; confirm absence from both
   AMS and AppManager inventory and verify the documented disposition of its
   own data/staging. A tile disappearing alone is not successful rollback.
9. **Stock reboot:** reboot through the ordinary supported bench procedure.
   Verify unchanged startup selection, no custom autostart/retry/error loop,
   recovered storage and stock Radio/Media/Phone/Climate/Settings health.
10. **Independent camera and absent-app check:** repeat the baseline camera and
    foreground behavior with the package absent. Retain the complete comparison
    before considering any transport or receiver experiment.

An app return or crash without an engine does not test preservation of a healthy
projection session. That later requirement remains in the transport matrix.

## Rollback and stop conditions

Normal rollback is stock app-specific stop -> supported uninstall -> explicit
AMS/AppManager/data reconciliation -> ordinary reboot -> baseline comparison.
Use the [existing recovery report](../reports/rollback_recovery.md); never copy
registry databases or Xlet directories behind their owners. If the app is hung,
its stock-owned lifecycle/reclaim path must remain available independently of
the custom surface. If removal leaves inconsistent state, stop the experiment
and use only the prequalified supplier recovery procedure. No automatic firmware
reflash, trust-store edits or whole-system reset is a rollback step here.

Stop immediately for an authorization error, unexpected autostart/permission,
boot delay or crash loop, camera/critical precedence regression, stuck foreground
or input, stock audio/phone interruption, unexplained storage growth, missing
acknowledgment or inconsistent inventory, exceeded approved resource bounds,
or inability to remove the app through its stock owner. Do not proceed to phone
transport to compensate for a failed resident-shell gate.

The minimal milestone passes only when all ten observations are documented on
the authorized bench. Its current disposition is **EXTERNAL_PROVIDER_GATE /
UNKNOWN runtime**, with zero installed target bytes in this run.
