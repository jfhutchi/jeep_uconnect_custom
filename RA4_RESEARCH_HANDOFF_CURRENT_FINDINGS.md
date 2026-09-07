# Uconnect RA4 18.45.01 Research Handoff - Current Findings

**Status:** current evidence handoff for the owner-authorized, read-only RA4 investigation  
**Primary target:** RA4 / VP4 18.45.01  
**Comparison target:** UAS 21.9 only where explicitly labeled  
**Current implementation status:** STOP - no stock modification, application installation, or flash is yet authorized by the evidence  
**Safety boundary:** no anti-theft PIN bypass or derivation, no service-certificate forgery, no signature disabling, no reuse of vendor credentials, and no stock/vendor material in Git

## 1. Mission and corrected premise

### Current checkpoint: 2026-09-06 default frame and Java focus cleanup

Started clean at `a658023` on canonical `codex/ra4-driver-temperature`; fetched
origin without divergence. The preceding turn made progress on AMS destroy
and explicit container-removal calls. This continuation resolves the conditional
default implementation and its focus/event behavior. The full goal remains active.

**STATIC_PROVED:** AMS selects UndecoratedXletMainFrame's factory only if its
configured factory is null. That frame's removeChild delegates to AWT Container
removal. For an attached child of a displayable parent, the path calls child
removeNotify, clears the parent reference and removes the child-list entry.
XletContainer inherits Container's recursive removeNotify, which attempts focus
transfer, clears its lightweight dispatcher and calls Component.removeNotify.

**STATIC_PROVED Java input cleanup:** Component clears most-recent/permanent
focus state as applicable, conditionally notifies its input context, calls
EventQueue.removeSourceEvents with false and invokes discardKeyEvents on the
keyboard focus manager. The false event-removal path preserves six event
classes, including KeyEvent and FocusEvent. LightweightDispatcher.dispose
clears its Java mouseEventTarget field; it is not a native touch-cancel proof.
The [container/focus report](reports/ra4_xlet_container_focus_cleanup.md)
records method/field identities, factory selection, branches and the distinction
between resolved and symbolic ROM invocation references.

**HIGH intended default:** no direct frame-factory override was found among
19 initializer classes / 517 invocation instructions, or direct resolved CP
references in successfully decoded AMS class slots 0 through 4121. This does
not cover reflection, uninspected optional JARs or undecoded metadata. The
factory setter remains available; the live instance is not measured.

**UNKNOWN:** native visibility and touch/contact release, completed focus
transfer, stock foreground restoration, and bounded cleanup when a shared
AWT tree lock or app callback hangs. The resident specification now requires
effective frame identity and shared UI-lock isolation evidence in addition to
the existing lifecycle/resource prerequisites. No runtime gate passes and no
measured local limit fails. Transport, provider authorization, engine and
resource gates are unchanged; no external-compute fallback is selected.

**Next technical target:** the AOT/native actionWithTimeout implementation and
its timeout/finally completion hooks. The Java removal route is now concrete;
more Java labels cannot prove bounded recovery from a stalled shared VM.
PR #14 remains draft; main and independent PR #15 are preserved. No radio,
vehicle or phone action, provider contact or vendor-payload commit occurred.

Fresh static checks cover three artifact identities, ten selected complete
method tables, 23 direct call anchors, one symbolic invocation reference,
factory/parent/mouse-field assignments and all six event-exclusion branches.
The prior AMS destroy/default checks also pass. The full host Python suite
passes **150 tests, no skips**, and **103 local links in six changed Markdown
documents** resolve. No target or provider test ran.

### Preceding checkpoint: 2026-09-06 AMS destroy and container cleanup

Started clean at `51b5a78` on canonical `codex/ra4-driver-temperature`; fetched
origin without divergence. The preceding goal turn made progress on result
normalization. This continuation advances the actual AMS lifecycle/cleanup
trace. The full projection goal remains active.

**STATIC_PROVED:** the normalized AMS stop codes are 8,
`XLET_CAUSED_JAVA_EXCEPTION`; 12, `TIMEOUT`; and 20,
`XLET_DID_NOT_STOP_ALL_THREADS_ON_DESTROY`. They are constant-valued AMSError
fields, and the destroy/thread-check bodies have concrete producers for 8/20.
D-Bus NoReply remains the separate nonzero result 34. Even zero-code stopped
events cannot certify complete thread termination or physical cleanup.

**STATIC_PROVED:** AMSProperties has separate compiled defaults for destroy
(10000), destroy-on-error (4000), and thread cleanup (200). The compiled
callback default is 1000, whereas the external file specifies 10000. These
stored values are not live or measured deadlines. Ordered field records are
essential: visible, verbose and secure Boolean fields precede the timeout fields.

**STATIC_PROVED:** the destroy wrapper invokes a timeout-managed destroy
action, then a separate cleanup action, with exception paths into cleanup.
The cleanup action reaches LWUIT deinitialization, GLES canvas destruction,
thread checks and explicit XletContext finalization. That finalizer calls
`XletMainFrame.removeChild(XletContainer)`. The thread-check exception path
still attempts context finalization. See the
[AMS destroy/cleanup contract](reports/ra4_ams_destroy_cleanup_contract.md)
for artifact identities, method ordinals, constants and exception-table anchors.

**UNKNOWN:** whether these calls complete when an app hangs; the timeout
runner's AOT/native behavior; concrete main-frame removal's native window,
focus and input effects; and supported custom-app failure containment. The
resident proof now requires raw errors, action completion, thread disposition,
container removal and native presentation/input recovery as distinct evidence.
No runtime gate passes; no measured local limit fails; external compute is
not selected. USB topology, phone transport and legitimate engine gates are
unchanged. PR #15's incorporated reference evidence and independent history
remain intact; PR #14 remains draft and main is preserved.

**Next technical target:** the concrete XletMainFrame removeChild implementation
and its native window/focus/input effects, followed by the AOT timeout runner's
completion hooks. No radio/vehicle/phone actions, provider contact or vendor
payload commits occurred. Only original analysis/specifications changed.

Fresh evidence validation matched three artifact identities, three named error
constants, seven constructor defaults, four external timeout keys, seven selected
complete method tables and 21 resolved call anchors, plus selected byte and
exception-table checks. The prior callback's 102 native and 14 HMI instruction
checks also pass. The full host Python suite passes **150 tests, no skips**;
all **105 local Markdown links in seven changed documents** resolve. These
are static/host checks, not target recovery measurements.

### Preceding checkpoint: 2026-09-06 callback results versus cleanup

Started clean at `e1f12c5` on canonical `codex/ra4-driver-temperature`; fetched
origin without divergence. The preceding goal turn made progress on pause
policy and watchdog queueing. This continuation traces the supplied callback
and the app-level result handler, rather than assuming an event proves cleanup.

**STATIC_PROVED:** callback `0x14ADE8` classifies NoReply separately and maps
it to result 34. For stop, AMS integer errCode 8, 12 or 20 can instead normalize
to success; their semantic names remain unproved. NoReply has no extracted AMS
error object and is not accepted by that normalization helper.

**STATIC_PROVED bookkeeping limit:** the app-level stop-result branch calls
switchToStop even for a nonzero result. It can remove the app from native
paused/running lists, announce appListUpdated and mark its status stopped,
then emit appStopped with the error code intact. Those are AppManager state
changes, not proof that AMS terminated a hung Xlet or released its container.

**STATIC_PROVED malformed-reply limit:** successful-transport JSON parse failure
clears the controller's success flag but retains mapped result zero. The
app-level event can therefore have code zero before later controller logic
uses the failed-parse flag. This does not prove the original request's final
outcome or that a malformed reply occurred on the radio. HMI appPaused handling
checks errorCode before dispatching APP_PAUSED versus START_XLET_ERROR.
The [result-completion report](reports/ra4_xlet_result_completion.md) records
the separate response objects, jump tables, mappings and native/HMI anchors.

The resident proof now requires raw response category, raw AMS error when
present, parse validity and normalized result correlated with app/operation,
plus independent lifecycle, visibility and input completion. No runtime gate
passes, no measured resident limit fails, and external compute is not selected.

**Next technical target:** actual AMS pause/destroy implementation and its
callback-timeout consumer through AWT/Screen container and input cleanup when
an app fails to return, while AMS retains ownership. More native bookkeeping
labels cannot substitute for that downstream proof. PR #14 remains draft/open;
main and independent PR #15 are preserved. Only original documentation changed;
there were no radio/vehicle actions, vendor payload commits or provider contact.

Fresh verification: **150 host Python tests pass, no skips**; two artifact
identities, 102 native instructions, two complete tables, nine literals, four
imports and 14 SWF instructions match, including ABC base/method count.
All 102 local links in the seven changed Markdown documents resolve.

### Preceding checkpoint: 2026-09-06 pause policy and per-app watchdog

Started clean at `71a054a` on canonical `codex/ra4-driver-temperature`; fetched
origin without divergence. The preceding turn made progress on native display
visibility and AMS owner-change scope. This continuation advances per-app
lifecycle evidence; the full projection goal remains active.

**STATIC_PROVED:** native pauseApp tests the app's `xlet.PauseAllowed` byte.
True selects pause; false selects stop. The properties subobject initialization
and extraction reset set the field false. The named parser consumes a string
property; the named serializer emits a JSON Boolean. Two stock packages supply
true/false examples. Both action wrappers call SVCIPC_asyncInvoke, so immediate
submission success is not lifecycle completion. The
[pause/watchdog report](reports/ra4_xlet_pause_watchdog.md) records identities,
subobject arithmetic, parser/default evidence and exact branch/call anchors.

**STATIC_PROVED recovery candidate:** AppManager's watchdog loop checks enabled
per-app counters. Expiry clears the app's watch and queues stopApp on the core
request queue; a conditional daemon branch also queues startApp. The handler
does not directly reclaim the window/input. App constructors initialize watches
disabled, and set-watch processing can fail if the watchdog is not running.
Live activation and permitted custom-app registration are unproved.

**UNKNOWN:** bounded stop/callback completion when a Xlet/VM hangs, effective
watchdog deadlines, container/input removal and healthy engine continuity.
The first resident proof now requires qualified effective PauseAllowed, selected
lifecycle action, and separate completion observations. Queued stop, successful
IPC submission and daemon restart do not satisfy session preservation or
fail-open recovery. The older installation report's destroy-timeout claim is
corrected: AMS has a default callback timeout but no explicit destroy-timeout
key in the recovered properties. Its consumer remains to be traced.

**Next technical target:** callback `0x14ADE8`, queued stopApp dispatch and the
AMS pause/destroy consumer through timeout/error handling into container/input
cleanup while AMS retains ownership. No runtime gate passed; no measured local
capability failed and external compute is not selected. PR #14 stays draft/open;
main and independent PR #15 are preserved. All changes are original documents,
with zero target bytes, target actions or provider contact.

Fresh validation: **150 host Python tests pass, no skips**. Four artifact
hashes/sizes, 110 native instructions, 13 literals, four pointer records and
five import resolutions match. The two stock property lines, subobject offsets
and exact AMS timeout-key set were checked. All 98 local links in the eight
changed Markdown files resolve. No analysis-tool code changed.

### Preceding checkpoint: 2026-09-06 display visibility and AMS owner scope

Started clean at `7b16ef1` on canonical `codex/ra4-driver-temperature`; fetched
origin without divergence. The previous turn made progress on pause, Return,
display-release requests and the SuperApp identity restriction. This turn
traces the display mechanism and distinguishes service loss from an app hang.

**STATIC_PROVED:** the gateway maps HMI `DisplayManager` to
`com.harman.service.LayerManager`. The recovered Lua policy registers that
service, opens `/dev/DisplayManager:0`, and maps an `ams` false request to hiding
`:AMS`. The native Visibility descriptor reaches screen_set_window_property_iv;
batch processing reaches screen_flush_context. Lua discards the write/read
results before returning a normal-path grant, so that grant is not compositor
completion evidence. The [display-owner report](reports/ra4_display_owner_reclaim.md)
records the exact mapping, Lua closures/PCs and native descriptor/call anchors.

**STATIC_PROVED service reaction:** LayerManager subscribes to
`com.aicas.xlet.manager.AMS` owner changes. Its AMS-name branch ignores the old
and new owner values, restores AMS order 1, hides `:AMS`, and restores HMI
order 5. It does not explicitly show the HMI or restore input. A selected
native close-event path removes/destroys the window; neither path proves an
app/VM hang detector or bounded recovery. The separately found start_display
script is labeled VP2-only and is not accepted as RA4 boot proof.

**UNKNOWN:** a failed Xlet while AMS remains registered, an unresponsive AMS
that retains ownership, native input/contact release, actual event delivery,
live boot selection, custom permission and healthy engine continuity. The
resident trial now explicitly requires app-only recovery with AMS alive;
whole-VM loss cannot stand in for that result. No runtime gate passed and no
measured local limit failed. External compute is not selected.

**Next technical target:** per-Xlet pause/destroy/error acknowledgments and
container/input removal in AMS/AppManager while the shared service remains
present, including any independent timeout. The full projection goal remains
active. PR #14 stays open/draft; main and independent PR #15 are preserved.
Only original documentation is added, with zero target bytes or target actions.

Fresh validation: **150 host Python tests pass, no skips**; three artifact
hashes/sizes, 28 Lua anchors and 15 native instruction/literal anchors match.
All 71 Lua prototypes parsed; the 15 native command descriptors and sentinel
were checked, including the complete Visibility record. The three Screen
call targets resolve through the native import inventory. All 83 local links
in six changed Markdown documents resolve. No analysis-tool code changed.

### Preceding checkpoint: 2026-09-06 Xlet foreground and return handoff

Started clean at `679d73b` on canonical `codex/ra4-driver-temperature`; fetched
origin without divergence. Previous goal turn made progress on stock Xlet
graphics. This continuation advances the return/resume and stock-owner path;
the full projection goal remains active and no target runtime gate passes.

**STATIC_PROVED:** the recovered 640x480 AppsActiveScreen requests the `ams`
display on entry. Screen exit conditionally requests pause, then releases the
display request on its normal path. Its Close handler requests stop and avoids
the ordinary exit pause. Re-entry can dispatch `Resume` for the last paused app.
Native requestForeground checks a Boolean HMI foregroundClear reply before
find/start processing. Local HMI availability is a String, converted to a
Boolean wire response; the earlier foreground report now states that precisely.

**STATIC_PROVED restriction:** requestBackground validates supplied appId but
uses configured SuperApp UUID in its normal outgoing invokeAppBackButton event.
The HMI only navigates when event identity matches the running app and the
active app screen is current. The Java wrapper checks AppMgrPermission("appMgr").
Neither fact grants a supported Return API to an arbitrary custom Xlet.
The [handoff report](reports/ra4_xlet_foreground_handoff.md) records artifact
hashes, Java BCIs, native data flow and SWF branch/call anchors.

**UNKNOWN:** native display/input release completion, bounded IPC, owner-loss
reclaim, custom authorization and session survival across pause. No wait for
pause acknowledgment is explicit in the screenOut method, but called code
may block; this is not a hung-app fail-open guarantee. No engine or target app
was created, installed or run. The resident trial now separates Return/resume
observations from explicit Close/stop; resource caps remain unchanged.

**Next technical target:** native DisplayManager's `ams` requester path through
visibility/input ownership and owner-loss recovery, followed by AMS pause/resume
acknowledgments. This provides a concrete target for the remaining reclaim
question. PR #14 stays open/draft; main and independent PR #15 are preserved.
This continuation contains original documentation only and has zero installed
radio bytes. No vehicle/radio/phone operation or provider contact occurred.

Fresh verification: **150 Python tests pass, no skips**. Four artifact hashes,
one class hash, 29 SWF anchors, 16 native instructions and eight Java invocation
BCIs match fresh reads; all 87 local links in seven changed Markdown files
resolve. No analysis-tool code or target package changed.

### Preceding checkpoint: 2026-09-06 resident Xlet view path

Started clean at `1484f88` on canonical `codex/ra4-driver-temperature`; fetched
origin without divergence. Previous goal turn made progress by establishing
the native gateway incompatibility. The full projection product remains
unachieved; this continuation advances its independent resident view lane.

**STATIC_PROVED:** Registration and user-guide application classes call
XletContext.getContainer, AWT Container.setVisible, LWUIT Display.init and
Display.callSerially. The user guide also constructs/shows a Form and registers
a Button action listener. Hash-bound AMS ROM class objects identify XletContext,
Container, Display and aicas GLESCanvas. **HIGH:** stock Xlet/AWT/LWUIT is the
concrete graphics API family for a candidate control shell. The
[view report](reports/ra4_resident_xlet_view_path.md) records exact signatures,
method BCIs, class hashes and ROM ownership anchors.

**UNKNOWN:** custom app acceptance, usable 640x480 area, input/foreground
arbitration, camera/critical priority, native video-buffer integration and
hung-app reclaim. The first sample's filename says 800X480 and does not prove
the Jeep's usable app dimensions. The sampled pause/destroy methods differ;
they do not establish a universal cleanup recipe. Supported SDK/package access
and legitimate authorization remain **EXTERNAL_PROVIDER_GATE**.

Added an original host JVM invocation inventory using `jawa==2.2.0`. It reports
actual instruction references instead of treating constant-pool strings as calls;
resources/full bytecode are not emitted. Eight selected stock class members
were parsed, with zero unresolved invokedynamic. Fresh full Python suite:
**150 tests pass, no skips**, including five new synthetic tests; compileall
passes. No target package, vehicle/radio/phone operation or provider contact.

The next technical target is the AMS container visibility/focus owner and
AppManager-to-AMS foreground/reclaim handoff. Transport, engine, authorization,
resource measurements and rollback runtime gates remain open. All additions
have zero installed radio bytes; the goal remains active.

### Preceding checkpoint: 2026-09-06 native projection gateway routing

Started clean at `1708c4f` on canonical `codex/ra4-driver-temperature`; fetched
origin with no divergence. PR #14 remains open/draft. PR #15's independent
phone/DHU evidence and branch were not changed or rerun.

The new [native gateway trace](reports/ra4_projection_gateway_dispatch.md)
establishes a **STATIC_PROVED routing gap**: recovered `hmiGateway` has a fixed
service/object resolver that recognizes neither `phoneProjectionService` nor
`DeviceConnectionManager`. An unknown destination clears both resolved strings
and returns `-1`; the command caller exits before invocation and the owner
notification caller exits before querying/subscribing. Registering a service
under the HMI's expected name alone cannot make this route work. The stock
`ConnectionManager` mapping is distinct from `DeviceConnectionManager`.

**HIGH:** shared `main.swf` Connection code, gateway message parsing, SVCIPC
imports and boot launch identify the native bridge relationship. **INFERRED:**
the bundled HMI retains a broader build-family contract than this gateway.
**UNKNOWN:** the deployment reason, matching backend/package/bridge and live
state. **EXTERNAL_PROVIDER_GATE:** request supported matching bridge, device
manager, screen and receiver components, or a separate supported app/engine API.
No stock gateway patch, alias substitution or new deployment is proposed.

The ARM tool now reads `PT_DYNAMIC` PLT relocations when stripped ELF sections
cannot supply imports. Its 181 gateway import slots match an independent
pyelftools relocation/symbol read. Five new synthetic tests cover resolution,
malformed/incomplete metadata, absent PLT metadata and ignored relocation types.
Fresh full Python suite: **145 tests pass, no skips**; compileall passes.
The current report records hash-bound native/SWF anchors and USB rule evidence.

The six stock USB device-rule files contain legacy serial/network/storage,
MTP and iPod matches, with no explicit AOA `18D1:2D01` rule identified.
`enum_devices.lua` only selects some Fiat iPod configuration links. Exclusive
AOA ownership and re-enumeration handling remain UNKNOWN; no Windows driver
conclusion is transferred to RA4. No vehicle, phone or target action occurred.

The backend compatibility requirement is sharper, but no transport, engine,
video, audio, input, resource or rollback runtime gate passed. Cabin topology
still needs the passive C2-to-PHY/controller evidence. The resident milestone
and resource caps are unchanged; installed radio effect remains zero bytes.

### Preceding checkpoint: 2026-09-06 transport, backend and provider gates

Canonical branch remains `codex/ra4-driver-temperature`, draft PR #14. This
continuation began with a clean checkout on main `6c898a1`, fetched origin and
switched to the already-current canonical head `174d721`. No local-only work
needed a fast-forward or preservation move. PR #15 at `93747c8` was reviewed
selectively; its branch/history was not merged.

Primary decision artifacts:

- [PC-versus-RA4 transport gate matrix](docs/20_projection_transport_gate_matrix.md).
- [Original PR #15 reference contract and provenance](reports/android_auto_reference_contract.md).
- [Structured USB census, topology boundary and projection backend contract](reports/ra4_usb_stack_backend_census.md).
- [Qualified engine/provider paths](docs/11_projection_engine_feasibility.md).
- [First future no-engine resident proof and prerequisites](docs/21_first_resident_runtime_proof.md).

**PROVED, inherited PC observation:** Android Auto protocol 1.7/TLS/render/input
and a repeat session succeeded over an ADB development tunnel. Direct USB
separately reached AOA v2 and real `04E8:6860 -> 18D1:2D01` accessory
re-enumeration with interface 0 bulk IN `0x81` / OUT `0x01`, then failed
transport access. There is no successful direct USB projection reference.
The Windows library/MTP-driver result is not an RA4 blocker.

**STATIC_PROVED:** AOA's relevant RA4 host APIs are materialized:
`libusbdi.so.2` exposes 62 `usbd_*` symbols including vendor control, bulk I/O,
descriptor/configuration and pipe lifecycle. Stock clients import them. The
new structured census covered 4,110 files, 578 ELF images and 91,086 member
names in 321 ZIP/JARs, with zero parse failures/skipped links. Program-header
parsing avoids false negatives from stripped QNX ELF sections. No matching
named DCD/function bundle, usblauncher or projection backend was identified;
compressed payloads, static/private/renamed/optional implementations are not
universally excluded. Actual loading and new-app permissions remain UNKNOWN.

**STATIC_PROVED:** HMI `startProjection(ppId)` sends through shared ModuleLink
`span` to logical destination `phoneProjectionService`. It separately observes
`DeviceConnectionManager`; the wrapper subscribes to session/back-to-car,
now-playing/navigation/call/device state. Cinemo CarPlay error constants
1000/1001 and GAL timeout 2501 supply a concrete **INFERRED provider lead**.
The service's executable/package, native bridge registration and matching
`DeviceProjection.swf` are still UNKNOWN. No supported socket/PPS ABI is invented.

**UNKNOWN topology:** selected owner update logs contain image-build HCD rows,
not a cabin attach trace. The stock hub monitor has topology/status APIs but
can restore hub power; it is not a passive tool to run. C2 remains unmapped to
Mentor or EHCI. The decisive passive evidence is one documented unpowered
C2 D+/D- net trace through the rear-I/O/board boundary to an identified PHY and
its OMAP USB interface on authorized spare hardware.

**Architecture correction:** AOA keeps RA4 as USB host. Missing device-role
software alone cannot reject wired Android Auto; a reachable EHCI path would
not inherently fail AOA. QNX 6.6 CarPlay role-swap/DCD requirements remain a
separate reference. The actual recovered RA4 generation is **QNX 6.5/ARM32**;
stale 6.6 target claims in engine/placement qualification were corrected.

**EXTERNAL_PROVIDER_GATE:** QNX, Cinemo and Harman/OEM matching-component routes
are qualified inquiry targets, with separate Android Auto/CarPlay authorization,
exact ABI, target bytes and resource measurements still required. None was
contacted. No measured local gate has failed; external compute is not selected.
The first resident trial is a legitimately packaged, manual, non-autostart
original Xlet control surface, <=3 MB installed, conditional on supported view,
arbitration, failure containment and rollback. No target package was created.

Fresh host verification: 140 Python tests pass, including five new structured
inventory tests and the sectionless-dynamic regression observed failing before
the fix. Python compileall passed; 44 candidate ELF hashes were recomputed,
24 published SWF anchors were checked and 98 local Markdown links resolved.
Host API exports and selected SWF method/offset relationships were inspected.
No JavaScript/C99 code changed; their historical
results below are not represented as newly executed.

Resource envelope unchanged: ~77 MB historical free space, >=45 MB protected
reserve, <=15 MB installed product, <=4 MB normal growth, <=8 MB additional
staging, >=5 MB residual. All work adds zero installed radio bytes. No vehicle
connection, target command, firmware change, service/USB/vehicle-state mutation,
credential bypass or protected payload publication occurred.

### Preceding checkpoint: 2026-09-06 startup PHY identity

The [startup PHY report](reports/ra4_startup_usb_phy_identity.md) completes the
startup/I2C/PMIC follow-up. The board-specific startup code names `USB83340C`
on its EHCI path, accesses `0x480648a4` with encoded port selector 2, and pulses
GPIO bank 2 bit 6 (GPIO 38) in the reset/identity routine. It reads four PHY ID
bytes but compares only the vendor low byte `0x24`; intended USB83340-family
support is HIGH, while fitted silicon and physical wiring remain unproved.

The same startup routine separately writes Mentor Interface Control `0x40` and
OTG Control `0x86` at the `0x480ab000` controller. The EHCI chip name cannot be
assigned to Mentor. Generic TWL4030 I2C/audio/graphics strings do not establish
a USB PMIC or power-switch connection; recovered graphics config sets
`tw4030 = 0`. Fresh validation checked source/prefix hashes and startup bounds,
eight ARM ranges (310 instructions), seven instruction anchors and three
configuration/driver hashes. No new implementation or target execution.

The next hardware evidence is an existing owner-supplied topology/boot capture
or authorized passive net/board evidence linking Radio C2 to one controller.
Mentor PHY identity, external VBUS switch, hub reversibility and DCD/function
support remain open. Keep the two controller paths separate in further work.

### Preceding checkpoint: 2026-09-06 USB PHY and power-control trace

The [USB PHY/power-control report](reports/ra4_usb_phy_power_control.md) closes
the previous Mentor board-init/ULPI task. It is current for USB static findings:

- Mentor board init writes `0x20` to ULPI `0x05`: PHY Function Control RESET
  through its SET alias. Port recovery can repeat the reset and set SESSION.
- The separate stock `usbPowerSwitch` utility accesses the same `0x480ab000`
  controller and writes ULPI OTG Control `0x0a` with `0x86` or `0xe6`, changing
  both VBUS-drive bits. This proves the software request path, not actual VBUS
  voltage, physical routing, PHY identity or device-role operation.
- Four `onoff/main.lua` call sites link that request to factory load-shed and
  resume/ignition handling. They discard results. The utility's exhausted-poll
  path can return success, so an exit status cannot establish hardware success.
- Fresh static validation matched three artifact hashes, decoded 12 bounded
  ARM ranges (1,022 instructions), parsed 70 Lua prototypes and checked the four
  zero-result CALLs. No implementation/tool changes or new host-suite runs.

The subsequent startup report above completes this checkpoint's next target
and identifies the EHCI-family lead without closing Mentor or Radio C2 wiring.

### Preceding checkpoint: 2026-09-06 after reboot

The active integration line is `codex/ra4-driver-temperature`, draft PR #14.
It was recovered from local `52a37f1` and fast-forwarded to remote `9eb28ad2`;
`main` remains `6c898a1`. Two untracked pre-crash reports were preserved outside
Git. The command runner works again. The
[post-reboot checkpoint](reports/ra4_post_reboot_checkpoint.md) is authoritative
for the preceding host verification, commands and corpus coverage:

- 135 Python tests and 20 JavaScript tests pass; all 8 mjs files pass syntax
  checks, Python compileall passes, and Synctool passes 83/83 hash-gated anchors.
- The portable arbiter compiled with strict C99 flags and passed its assertions
  under existing Ubuntu/WSL GCC 13.3.0. This is a host result, not a target build.
- The current 122-marker probe and correlator completed over seven existing
  roots: 4,110 files, 1,509,846,870 bytes, no size skips; 628 candidates,
  including 108 tier 1. Raw scanning misses compressed SWF names.
- Recovered `.script` loads `io-usb` with OMAP/Mentor at `0x480ab000`, IRQ 92,
  and EHCI at `0x48064800`, IRQ 77; its environment says `qnx650`.
  QNX 6.6 documentation is reference evidence, not proof of the installed ABI.
- Stock `AppPhone.press` can call `callStartProjection(activePpId)` when
  `BacktoCar` is set before its later session-active navigation check. The
  previous blanket no-start-on-resume inference is withdrawn; the command's
  backend meaning and live-session continuity remain unproved.
- All 610 `hmi_rov` SWFs were parsed for exact return names. `main.swf` maps
  the projection screen filename, but no `DeviceProjection.swf` file exists in
  the seven roots and no exact-name back-to-car listener was found in that
  bounded SWF census. Dynamic names/other variants/packages are not excluded.

The subsequent USB report above completes this checkpoint's board-init/ULPI
target and narrows the remaining physical-route and device-stack questions.
Resident authorization, screen/backend availability, camera/critical priority,
fail-open stock presentation and the existing storage envelope remain gates.
No radio connection, service launch, firmware edit, vehicle-state mutation or
credential bypass occurred. Historical verification/publication statements in
the original investigation below are historical snapshots, not current status.

The project goal remains to understand the smallest safe and reversible owner-authorized path to run an original application while preserving normal vehicle behavior, the factory anti-theft system, AMS secure mode, application authentication, stock update capability, and a verified return to production state.

The original proposed chain was:

~~~text
Developer Mode request
  -> factory anti-theft PIN
  -> developer authorization
  -> AMS development state
  -> developer package installation
~~~

That is not the control flow recovered from RA4 18.45.01. Static evidence proves separate security domains:

1. A signed, head-unit-bound, expiring service certificate authorizes reachability of the engineering Service menu.
2. The factory anti-theft keypad is an independent IOC authentication/state machine.
3. Engineering Service-menu item 19 directly creates or deletes /fs/etfs/AMS_DEVELOPMENT.
4. /fs/etfs/enableEngMenu independently controls inclusion of AppManager's embedded engineering application.
5. Application signer identity, key.jar, DRM.jar, signed descriptor fields, and xlet.developerToken form a separate package-trust domain.
6. authenticationService is a separate keyed hash/random service; no call edge connects it to the PIN, marker, or package developer token.

The best-supported future architecture is therefore:

~~~text
legitimately issued service.cert through an authorized stock path
  -> SERVICEKEY media handler OR internal diagserv staging/finalize
       (IOC session/state-4 gate proved; legitimate external authority unknown)
  -> stock verification, HU-serial match, and validity checks
  -> serviceMenu=true
  -> stock item 19
  -> /fs/etfs/AMS_DEVELOPMENT state
  -> next normal jvm.sh execution
  -> stock production or development security.jar
  -> AMS remains -secure

separately authorized application package
  -> signed key.jar descriptor and executable-member digests
  -> signed DRM entitlement where required
  -> AppManager permission and local DRM check
  -> AMS authenticated package inspection
  -> signer/developer-token/policy decision
  -> install and register
       -> conditional autostart only with DRM launcher entitlement/global gate
       -> otherwise remain stopped until the generic Apps UI sends native DRM-checked startApp
~~~

The first chain is substantially proved. In the second, native ingress, AMS developer-token branch, exact Base64/SunJCE `RSA/ECB/PKCS1Padding`/ID predicate, two-stage security-configuration key promotion, stopped-install launch behavior, and per-app uninstall orchestration are now proved. The missing live runtime developer-ID provider and legitimate issuer, detached signer/principal policy, exact live-package schema, and complete rollback contract remain stop gates.

## 2. Evidence notation and offset conventions

Current continuation vocabulary is PROVED (observed result, with platform and
provenance), STATIC_PROVED (direct static relationship), HIGH (corroborated
but incomplete), INFERRED (interpretation), UNKNOWN and EXTERNAL_PROVIDER_GATE
(requires legitimate issuer/provider evidence). Historical CONFIRMED findings
below retain their original scope and do not imply new target execution.

- **CONFIRMED** means a direct operation, data edge, file access, digest, signature, or control-flow edge was reproduced from the named RA4 artifact.
- **HIGH** means multiple direct artifacts support the conclusion, but one executing endpoint or runtime behavior remains hidden.
- **INFERRED** means the interpretation best fits the evidence but has a plausible alternative.
- **UNKNOWN** means the recovered corpus does not establish the claim.
- **CONFIRMED ABSENT** is used only for a bounded, fully traced function or documented census. It is not a system-wide impossibility claim.
- SWF code offsets are offsets in the reconstructed uncompressed FWS stream unless stated otherwise.
- AMS offsets are executable file offsets. Native AppManager and authenticationService addresses are ELF virtual addresses unless explicitly called file offsets.
- Lua line references are recovered source/debug lines from Lua 5.1 bytecode. Shell references are physical lines.

This handoff reports short names, hashes, paths, methods, and offsets. It does not reproduce a PIN, developer token, authentication key-ring value, private key, service certificate, or vendor source body.

## 3. Canonical RA4 source, recovered filesystems, and tooling

### 3.1 Source chain

Use the existing materialized trees for file analysis. Do not repeatedly unpack the owner ZIP, swdl.upd, or the nested ISOs.

| Layer | Bytes | SHA-256 | Role |
| --- | ---: | --- | --- |
| Uconnect_VP4,18.45.01-My13-17.zip | 1,266,203,571 | 5388d9310737dc52a65f2825131043362254b3592da2584302b81bc0447f9fdd | Authoritative owner-supplied source |
| analysis_ra4_18.45.01/extracted/swdl.upd | 1,426,147,328 | c704eb723d6697fd98959888274dda18362c23ce6f66b505e01ce1983148c344 | USB software-download image |
| analysis_ra4_18.45.01/work/swdl_iso/installer.iso | 34,830,624 | 893c1e9dbc16b42d3a0eba8f8470336ec84618d59980735a1e61a58499b830a5 | Installer runtime and scripts |
| analysis_ra4_18.45.01/work/swdl_iso/primary.iso | 375,191,552 | 8086b7b6a413c9fd2718d21bd7d027c79c0dc36a1e1d43ea1f7358fd33b890ff | System, HMI, AMS, and native services |
| analysis_ra4_18.45.01/work/swdl_iso/secondary.iso | 1,015,750,656 | cd6df921c1da876cb5652f011bd3f1cc6a751a818b3455f478b4e1f7fc7edcb5 | Kona, KIM, Xlets, and application data |
| analysis_ra4_18.45.01/work/primary_iso/usr/share/IFS/ifs-cmc.bin | 42,122,670 | ea6797be141763f35f3059ad858eefbf54f730af0155bebc7af411c47d80ba92 | Standard boot image plus three hidden HBC filesystems |

The immutable corpus snapshot in [corpus_inventory.md](reports/corpus_inventory.md) recorded 3,398 files and 6,648,650,761 bytes before the post-snapshot hidden-IFS recovery. Its canonical RA4 materialized trees contain 54 installer files, 2,466 primary files, and 766 secondary files. The secondary tree contains 300 JARs, 27 KIM families, 135 application instances, 24 distinct application IDs, 135 installed descriptors, and 135 key.jar files.

### 3.2 Hidden QNX filesystem recovery

The standard QNX image and all three HBC filesystems were decoded read-only from ifs-cmc.bin. Compression byte 0x88 means QNX two-byte big-endian length framing plus LZO type 8, proved from recovered memifs2 dispatcher 0x105948, framed reader 0x10572C, big-endian length read 0x1057D8, and type-8 branch 0x105828.

| Container | Source anchor | Decoded bytes | Regular files | Decoded SHA-256 |
| --- | --- | ---: | ---: | --- |
| Standard boot imagefs | payload 0x00019110 | 3,450,748 | 46 | 503d46f0ac412fcff594a9b37cc859d2e029e257a2d2367275c723a5f77d22ab |
| HBC segment | header 0x001A0000 | 30,909,752 | 433 | 996c5a52cf7e72bb73d95e34e684196ca702061c6c5d9977415b014fbea57fbb |
| HBC segment | header 0x00F20000 | 23,083,796 | 219 | 57feaf9cfde58172f8a94049227ec895eb2f88607466297e31f8732f201b8512 |
| HBC segment | header 0x019A0000 | 35,478,140 | 126 | aae02c6ea6873e66cde49e814299d43cbeb38e686352fd86324ac91a1feafc42 |

The three HBC images contain 778 regular files totaling 89,007,481 payload bytes. Decoded vendor files and inventories remain below analysis_ra4_18.45.01/work/hidden_hbc_ifs and must never be staged or published. Full format proof is in [qnx_boot_filesystems.md](reports/qnx_boot_filesystems.md).

### 3.3 Original reproducibility tooling

| Original project artifact | Bytes | SHA-256 | Verification role |
| --- | ---: | --- | --- |
| analysis_tools/qnx_ifs_inventory.py | 6,920 | 6cdab8b7493f816b36b583dbee7a6805d3b525c71b234cf621f82dd7fd3aef40 | Standard imagefs and framed HBC parsing/inventory |
| analysis_tools/tests/test_qnx_ifs_inventory.py | 4,399 | f3732e9207104747f7038b81e1351c6b5be33bd9fc7277dc80024d52724fc373 | Six framing, record, boundary, and extraction tests |
| analysis_tools/jamaica_rom_strings.py | 13,329 | 3fdd53837de8eeeef434d1249a0055102ab6ac05a7bc3c29b6752077cb185530 | Bounded JamaicaVM pool, literal-table, member-selector, and class-pointer decoding |
| analysis_tools/tests/test_jamaica_rom_strings.py | 15,268 | 309420c6bfd8359f49fc7e44793295f7be8c824e80536c0d19bb059329b922a7 | Twenty-two pool/tag, prefix-bound, mapping-table, class-bound, and CLI numeric-bound tests |

Historical checkpoint: six QNX imagefs, 22 Jamaica metadata-decoder and 19 developer-token probe tests passed (47 total). Current post-reboot discovery passes 135 Python tests; see section 1. Other methods used in the reports are static Node file/JAR traversal, manifest digest recomputation, OpenSSL PKCS#7 signature-math verification without trust-chain acceptance, AVM2 parsing, Lua 5.1 decoding, and bounded ARM ELF control-flow analysis. No recovered target executable was run.

## 4. Security-domain separation matrix

| Domain | Authoritative input/state | Producer or writer | Consumer | Confirmed effect | Confirmed relationship to other domains |
| --- | --- | --- | --- | --- | --- |
| Engineering Service authorization | signed service.cert, matching HUSerialNumber, valid date/ignition allowance, EngineeringMenu=1 | authorized certificate issuer plus SERVICEKEY media or internal diagserv `0xF010`; external diagnostic gate unknown | platform_troubleshoot.lua and HMI VersionInfo | service_flags.eng_menu -> Peripheral.versionInfo.serviceMenu | Positive gate for Service-menu reachability; no anti-theft PIN input |
| Anti-theft | four keypad input bytes and IOC state/counter/lock-time | HMI request; external IOC makes decision | hmiGateway, onOff, IOC, HMI state handler | locked/wait/enter/wrong/unlocked/forced-update states | No marker, serviceMenu, signer, or developer-token operation |
| AMS Development Security | /fs/etfs/AMS_DEVELOPMENT regular-file state | AppsListEngServiceMenu item 19 | HMI File.exists and jvm.sh -f test | production/development security.jar selected at next AMS launch | Reached through Service menu; not produced by PIN or token |
| Embedded engineering catalog | /fs/etfs/enableEngMenu | writer UNKNOWN | native AppManager createEmbeddedApps | retain/filter embedded appId engineering | Separate from serviceMenu and AMS security selection |
| Application authorization | key.jar signer, signed descriptor, executable digests, DRM grant, optional signed xlet.developerToken | package/signing and provisioning process | Kona AppManager, native AppManager, AMS | package authentication, policy/permission domain, lifecycle admission | No evidence that PIN or marker creates the package credential |
| Native keyed service | authenticationService key-ring plus product/device inputs | boot/configured service | com.harman.service.authenticationService | keyed SHA-256 and random operations | No proved call edge to PIN, marker, AMS package verification, or developer token |

There is no recovered arrow from successful anti-theft PIN authentication to serviceMenu, AMS_DEVELOPMENT, enableEngMenu, developer-token creation, or signer acceptance. The positive engineering-menu authorization is the service-certificate chain.

## 5. Confirmed Development Security flow

### 5.1 Physical event and HMI entry

The physical event is produced in:

- analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/vehicle/keys.lua, SHA-256 620809fd91f2ddd3d48d874db62ab6afd11a3501e2a5a2d4812922cfa4d40040.
- analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/vehicle/icsHardKeys.lua, 31,153 bytes, SHA-256 86aba0d0c5fbfdeb9d5da36edd66c81e3e76cf16744740d9778612f41a7a1ea5.

keys.lua functions 16-18, debug lines 531-619, route ICS matrices and front-key IPC channel 25 to icsHardKeys.processKnob. icsHardKeys functions 32 and 33, lines 652-683, track the two driver-temperature buttons and start a 5,000 ms timer. Function 11, lines 237-279, emits key=engineerMode when both remain set; the exact emission is bytecode PCs 140-145.

The path does not test anti-theft state. The antiTheftStateUnlocked variable is used only by the volume-knob and audio-power handlers, not the two temperature handlers, processICS, or the five-second timer.

In analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/MainSupplement.swf, ICS::messageHandler at reconstructed FWS 0x2A728C maps engineerMode at 0x2A73EA-0x2A7409 to ICSEvent.ENGINEERING_MODE. HardControls::onEngineeringMode at 0x272F49 navigates to the Apps List engineering extension.

### 5.2 Service-certificate authorization

MainSupplement.swf VersionInfo::requestServiceFlags at 0x2D35B6 requests get_service_flags. VersionInfo::platformMessageHandler reads get_service_flags.eng_menu at 0x2D3A64-0x2D3A6E, stores mServiceMenu, and dispatches the service event through 0x2D3A8C.

The producer is analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/platform_troubleshoot.lua, 13,931 bytes, SHA-256 8beab38ab164479a9fd815116dbfa02a48e3fa661724fa9c4273dc5884a1ba45:

- Functions 11/12, debug lines 406-427/408-422, receive the SERVICEKEY media event, copy candidate service.cert, and invoke evaluation.
- Function 7, lines 255-304, calls stock verifier /fs/mmc0/app/security/scv with /etc/keys/serv_cert_key.pem.
- The evaluator requires verifier success, equality between parsed HUSerialNumber and /fs/fram/serialnumber, valid certificate fields, and valid date/ignition-cycle lifetime.
- Function 2, lines 63-127, maps numeric EngineeringMenu value 1 to service_flags.eng_menu=true.
- Functions 5/6, lines 188-248, clear invalid state and remove an invalid or expired service file.

A second factory-oriented stock ingress is now confirmed in `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/usr/bin/cmc/service/diagserv.lua` (282,802 bytes; SHA-256 `777d96dfa3461caa6ebf4765784f9ba2f4d766fd1ddfe54590a655121353bd64`). Root PCs 2300-2305 open IPC channel 7 and attach `onIpcMessage`; `msgHandler[49]` reaches dispatcher prototype 268 (`0x3A79A-0x3A88C`, lines 6876-6886). Registered `0xF010` prototype 254 (`0x34D52-0x354C8`, lines 6249-6307) stages `/etc/security/service.cert`, then its finalize branch invokes `com.harman.service.platform.evaluate_service_file` through validator prototype 1 (`0x4206-0x4567`, lines 325-342). Registered `0xF011` prototype 255 (`0x354C8-0x35804`, lines 6312-6333) removes the same fixed path.

This closes the internal diagnostic staging/removal transport and the IOC-local authorization gate, not the legitimate external authority or certificate issuer. No local gate appears in the Lua routines, but `cmcioc.bin` requires a non-default diagnostic session, common condition, generic security-mask intersection, and proprietary authorization state 4 before F010/F011 handlers forward through channel 7. State 4 belongs to a challenge/response state machine with retry/lockout and a finite persistent allowance. No secret, response, handler identifier, or external framing is reproduced. The finding must not be read as unauthenticated external reachability. Platform verification, HU-serial equality, and lifetime limits still decide certificate authorization.

The staging operation is non-atomic and acknowledgments are weak. Initial mode opens the active path with `w+b`; continuation uses `rb+` and seeks to the end; no temp file, rename, fsync, backup, checked mount result, or protected cleanup exists. Open failure logs and then reaches the same internal success tuple as a successful write (`0x34E4E-0x34E6E`). A partial or truncated certificate can remain until finalize, later evaluation, or explicit removal. `boot.sh:321-325` merely starts diagserv early when `TestToolPresent::1`; lines 557-561 start it later regardless, so tester presence is not the persistent authorization predicate.

The active IOC artifact is `analysis_ra4_18.45.01/work/primary_iso/usr/share/V850/hs/cmcioc.bin`, 458,752 bytes, SHA-256 `c7bf247bfdb10b5dfda2802df1210671f6a1872140cdeebc014c109a9c77e012`, with flat mapping `VA=file+0x10000`. Exact RoutineControl lookup maps F010/F011 to handlers VA/file `0x6D730/0x5D730` and `0x6D7D0/0x5D7D0`; both call authorization getter `0x54228/0x44228`, require state 4, then forward through channel 7.

The runtime authorization state is `GP-0x7B38`; its getter has exactly 12 direct callsites, all in diagnostic-handler authorization surfaces. Persistent allowance slot `0x11A` can restore state 4, but allowance mutator `0x54180/0x44180` has only two callers: an already-state-4-gated setter and a decrement path. Getter `0x4A694/0x3A694` selects the low three bits of one of two packed network-receive words; that value is carried separately from derived power mode into the HBC OnOff record. `onoff/main.lua` maps raw `ignState` value 4 to `start`, proving the decrement producer is driven by a sustained raw ignition start-state event. Source ECU/bus/message name, binary product-variant meaning, and scheduler timebase remain unresolved.

A one-way cross-domain edge is proved. A manufacturing handler at `0x6C388/0x5C388` requires state 4 and can persist/copy a replacement factory anti-theft comparator. The reverse is absent: the PIN-decision/success path and publisher have no proprietary state/getter/allowance/mutator references. Therefore `state4 -> comparator provisioning authority`, while successful PIN authentication does not create state 4, replenish allowance, authorize `service.cert`, toggle `AMS_DEVELOPMENT`, or create developer credentials.

The verifier scv is 1,596,550 bytes, SHA-256 08bb7992d95b27b98bcb222021015cda152eef9fafa573720845d28c837c7fe1. The recovered verifier key is a public 2,048-bit RSA key; its file hash is recorded in [qnx_boot_filesystems.md](reports/qnx_boot_filesystems.md), but its contents are not reproduced. Possessing the public verifier does not authorize certificate issuance.

AppsListEngMenuScreen exposes Service only while Peripheral.versionInfo.serviceMenu is true at reconstructed offsets 0x3030C-0x30333. Selection enters AppsListEngServiceMenu. This is the authenticated event chain upstream of the marker UI. The actual state transition still requires explicit selection of item 19; certificate validation does not itself create the marker.

### 5.3 Exact marker owner

Equivalent RU and ROV implementations exist in:

- analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_ru/skins/default/swf/AppsListScreen.swf, SHA-256 ac817adc1471c07631e80eccddf8f3231b549d9fc725d8b27cb2d13d54212d67.
- analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/skins/default/swf/AppsListScreen.swf, SHA-256 5bc1630f567c82494ab86e73c308ad2a8b9d341494a5f5de5f66a1505f1416e5.

| Operation | Exact owner and evidence | Result |
| --- | --- | --- |
| UI read | AppsListEngServiceMenu::isDevepSecurityKeyEnabled constructs file:///fs/etfs/AMS_DEVELOPMENT and returns File.exists; RU method 759 ABC offsets 219,463/219,478; ROV method 736 ABC offsets 217,688/217,703; debug lines 758-759 | Determines item label |
| Create | AppsListEngServiceMenu::DevepSecurityKeyEnabled, debug lines 763-774; RU method 760 createTempFile/moveTo at ABC offsets 219,560/219,624; ROV method 737 at 217,785/217,849 | A temporary file is moved to the marker path with overwrite=true |
| Delete | Same method, debug line 785; RU ABC offset 219,683; ROV ABC offset 217,908 | Direct File.deleteFile on the marker |
| Launch-time read | analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/jvm.sh line 59 | Shell -f selects development only for a regular file |

The static item constant ENABLE_DEVP_SECURITY_KEY is 19. The constructor calls the reader and labels the action Enable Development Security or Enable Production Security. The vendor spelling in symbols is Devep.

The writer contains no PIN call, token call, D-Bus/SvcIPC call, process signal, restart, reboot, or filesystem sync. Its creation error handler changes the UI label before moveTo and then catches an exception, so the displayed label alone is not proof that the marker transition succeeded.

A bounded census found the literal only in jvm.sh and the equivalent RU/ROV AppsList methods. It found no literal in all 188 ELF files, all 300 JARs and 21 ZIPs, the 46 standard-IFS regular files, or all 778 hidden-HBC regular files. Dynamically constructed paths or out-of-corpus code remain theoretically possible.

### 5.4 Marker to AMS runtime state

The launcher is analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/jvm.sh, 2,795 bytes, SHA-256 9bd3c63a2c22c17f96e037102283f453afca43eb093bc1291d607a9805f829ec:

- Line 58 initializes /fs/mmc1/kona/security/security.jar.
- Line 59 tests -f /fs/etfs/AMS_DEVELOPMENT and substitutes /fs/mmc1/kona/security/development/security.jar.
- Line 61 logs the selected JAR to /dev/ser3.
- Line 63 starts AMS with the selected -securityConfiguration and unconditional -secure, plus installation, extension, initializer, library, and property paths.

Initial launch is:

~~~text
standard /bin/boot.sh
  -> connectivity_startup.sh at boot line 396 or 712
  -> connectivity_startup.sh lines 23-24
  -> qon -d jvm.sh
  -> /fs/mmc0/app/bin/jvm.sh
  -> selected security configuration and AMS -secure
~~~

The qon -d option belongs to qon and is unrelated to native AppManager's stale -d argument.

platform_ams_restart.lua, SHA-256 264e5aaa6e2e09e8bb86a881f4919a66220d1cad2c7ce9443416e5d35f9f720f, functions 7/9/10 at debug lines 183-250, watches AMS D-Bus ownership and a 120,000 ms startup timer. On startup timeout or later service disappearance it reinvokes jvm.sh, which re-samples the marker. It has no marker literal or marker-change watcher.

Therefore:

- Marker state changes a future AMS process, not the already-running one.
- A later initial or recovery execution of jvm.sh is the confirmed activation boundary.
- Marker change alone is not a confirmed restart trigger.
- Development selection changes the stock security-configuration JAR but never removes -secure.

## 6. service.cert is not /fs/etfs/service.key

Two similarly named artifacts must not be conflated:

| Artifact | Confirmed owner | Exact effect |
| --- | --- | --- |
| /etc/security/service.cert | platform_troubleshoot.lua and diagserv `0xF010`/`0xF011`; standard boot maps /etc/security under /fs/mmc0 | Verified with scv, HU serial, and expiry rules to produce service flags; platform invalidation or the separate internal diagnostic routine can remove it |
| /fs/etfs/service.key | AppsListEngServiceMenu item 20 | Direct ActionScript File.deleteFile only |

In the ROV AppsListScreen.swf, DELETE_SERVICE_KEY is item 20 at 0x36C77-0x36C7C. onItem maps case 20 at 0x37EF7-0x37F01 to block 0x37D11. That block constructs file:///fs/etfs/service.key at 0x37D17-0x37D24, tests exists at 0x37D3E-0x37D45, and deletes it at 0x37D59-0x37D61.

The item-20 block makes no Peripheral, ModuleLink, D-Bus, or platform-service call. platform_troubleshoot registers get_service_flags, test_service_flag, and evaluate_service_file, but no delete/remove method for item 20. Diagserv's internal `0xF011` remover is a separate IPC routine and item 20 does not invoke it. `0xF011` removes persistent state but does not call the evaluator, clear already-published service flags, or notify the HMI, so immediate live revocation is unproved. No recovered alias joins /fs/etfs/service.key to /etc/security/service.cert.

The consumer and eventual effect of /fs/etfs/service.key remain UNKNOWN. Item 20 is not a proved revocation or rollback mechanism for the active service certificate and must not be relied upon as one.

## 7. Independent anti-theft flow and destructive reset

### 7.1 PIN request and IOC decision boundary

The normal anti-theft path is:

~~~text
PopupAntiTheftKeypad Done
  -> AntiTheft.checkAntiTheftPin(input)
  -> ModuleLink Dest=AntiTheft / checkAntiTheftPIN
  -> hmiGateway
  -> com.harman.service.onOff
  -> onoff/main.lua writes IPC channel 2
  -> cmcioc PIN-decision routine compares only in enter-PIN state
  -> equality updates distinct anti-theft state/publication flags
  -> later IOC state/counter/lock-time message
  -> HMI locked/waitForVIN/enterPIN/wrongPIN/unlocked/forced-update state
~~~

Exact anchors:

- PopupAntiTheftKeypad.swf invokes the check at reconstructed offsets 0x5892 and 0x58A1-0x58AA.
- MainSupplement.swf AntiTheft::checkAntiTheftPin starts at 0x2AC4E7 and builds the ModuleLink packet at 0x2AC4FA-0x2AC513.
- hidden HBC hmiGateway is 153,124 bytes, SHA-256 8d7fe8789bb012a66fbebd1bd44eefa506c672a5d70c90fbf92b3a5a6f01ec82. Its resolver/dispatch compares AntiTheft at file offsets 0x7BE0 and 0x8E18, then loads com.harman.service.onOff and its object at 0x9E3C/0x9E4C.
- hidden HBC onoff/main.lua is 66,272 bytes, SHA-256 41c0f3f2709c49d4a4f9b150b8c08c735515a9c50bbfbc2e4c36664d6466e698. Function 28, debug lines 1116-1126, writes message type 0xE0 plus the four supplied input bytes to IPC channel 2 and returns an empty table immediately.
- onoff function 23, lines 687-1055, reads state, counter, and lock-time fields. Lines 921-953 map raw states to the HMI states.
- `cmcioc.bin` channel-2 dispatch reaches PIN-decision VA/file `0x25658/0x15658`; equality branch `0x256AE..0x256C2` changes separate anti-theft state `GP-0x229A` and publication flags; publisher `0x2AD6C/0x1AD6C` emits the result.

The comparison routine is located, but the comparator content, protected provenance, retry thresholds, lockout progression, and VIN coupling remain intentionally unresolved. No PIN material or bypass procedure was derived.

The channel-2 dispatcher, PIN-decision/success branch, and publisher have zero references to proprietary diagnostic state `GP-0x7B38`, finite allowance `GP-0x7B34`, state getter `0x54228`, or allowance mutator `0x54180`. Combined with the HBC/HMI callback census, this confirms PIN success does not authorize state 4, service flags, the development marker, or developer credentials.

### 7.2 xletsReturnToNew is not developer authorization or rollback

When a supported VP4 variant previously entered the PIN state and later receives unlocked, MainSupplement.swf AntiTheft::MessageHandler at 0x2AC1B8-0x2AC209 sends AppManager command xletsReturnToNew.

The receiver is native analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/bin/appManager, 1,268,061 bytes, SHA-256 608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591:

- parseRequest compares xletsReturnToNew at file offset 0x5C460, VA 0x15C460.
- The equal branch calls handler file offset 0x2AA7C, VA 0x12AA7C, through branch-and-link 0x5C4A8.
- Handler 0x12AA7C requests writable media and removes shared record-store files, record-store directories, Xlet installation directories, and /fs/mmc1/resource contents.
- Helper 0x12A95C restores preinstalled Xlets, removes the AMS temporary folder, and requests a head-unit reset.
- Helper 0x12A890 invokes requestReset.

xletsReset is a different parser command. xletsReturnToNew is a broad destructive factory-application restoration, not a Java Xlet transition to NEW, not an AMS_DEVELOPMENT toggle, not a token operation, and not a per-application rollback. It can affect unrelated applications, shared RMS state, and resources. It must not be intentionally invoked during development research.

## 8. Other AppManager and authentication controls

### 8.1 /fs/etfs/enableEngMenu

Native AppManager function file offset 0x29E08, VA 0x129E08, loads /fs/etfs/enableEngMenu at 0x29E20-0x29E24, calls the file predicate with mode 4 at 0x29E2C, and tests the result at 0x29E30.

Its sole direct branch-link caller is createEmbeddedApps at file offset 0x3D1C0, VA 0x13D1C0. The caller filters the embedded application whose appId is engineering; appManager.cfg line 84 lists that entry. The complete primary-plus-hidden literal search found no writer.

This marker changes the native AppManager embedded catalog. It does not set serviceMenu and does not select AMS security.jar.

### 8.2 Native AppManager -d is ignored

Stock boot still passes stale argument text:

- boot.sh lines 367/371 and 461/465 assign and pass disableDRMArg=-d to appManager.
- platform_ams_restart.lua lines 183-209 varies command text using /fs/etfs/disableDRM; constant/value offsets are 0x135C/0x1361 for the marker, 0x1375/0x137A without -d, and 0x13E0/0x13E5 with -d.

The exact native parser closes the question for this binary:

- processOptions at VA 0x195FFC constructs one empty local Poco OptionSet at 0x196028.
- It registers only silent/s, json/j, presub/p, watchdog/w, config/c, tp with no short name, and help/h at 0x196030-0x196978.
- OptionProcessor stores the sole local set at 0x1D9FC8. Its short-option path 0x1DA96C-0x1DAA00 looks up the text following one dash in that set; common lookup begins at 0x1DA1C8.
- No inherited/global option set or short-option clustering can manufacture a d entry.
- The process handler loads the unknown-option-ignored diagnostic at VA 0x21284C from 0x196E00.

A dormant normalized-name branch compares drm at 0x19718C-0x197200 and calls setter 0x16D548 with true at 0x19720C. drm is also not registered. The setter writes configuration byte +0xD9. Configuration constructor 0x143F7C calls DRM subobject constructor 0x181318, which initializes the same field to 1 at 0x181338.

Install preparation calls checker 0x1801D4 from 0x1957A4. The checker reads the enable byte at 0x1802C0; zero returns through the disabled path, while nonzero continues grant lookup and a missing grant returns error 0x1B at 0x180338.

**Current conclusion:** for this exact AppManager binary, DRM checking defaults enabled, install preparation calls it, and supplied -d is unregistered and ignored. /fs/etfs/disableDRM and stale command text are not usable security controls and have no relationship to AMS_DEVELOPMENT.

This later result supersedes earlier reports that conservatively left the native -d effect UNKNOWN before the complete Poco lookup and default-field analysis.

### 8.3 authenticationService

boot.sh line 649 launches authenticationService with /etc/system/config/authenticationServiceKeyFile.json. The JSON is 11,359 bytes, SHA-256 5968ff07dba7a0316a7fc76687cbef5147699d96538d14a10def0bfd5211ad11. Structurally it contains a product-ID path and 100 contiguous key-ring entries; no value or product-ID path is reproduced here.

The service binary is 273,340 bytes, SHA-256 9c7c057fbffceb2dc0b77690b6eb07dcd90721de6f89c5a05150fa18cea84699. It registers com.harman.service.authenticationService at file offset 0x2F970 and object /com/harman/service/authenticationService at 0x2F99C. Its dispatcher reads productID/deviceID at 0x102B30/0x102B54 and routes random at 0x102C00 to handler 0x10293C and sha256 at 0x102C28 to handler 0x102000.

Exact searches find no developer, developerToken, PIN, or AppManager-service link. platform_troubleshoot observes this service becoming available before reevaluating a service certificate, but that scheduling relationship is not evidence that authenticationService validates the service certificate or anti-theft PIN.

## 9. AMS/Kona trust and permission model

### 9.1 Production versus development security configuration

| Property | Production | Development |
| --- | --- | --- |
| Extracted path | secondary_iso/.../kona/security/security.jar | secondary_iso/.../kona/security/development/security.jar |
| Bytes | 7,504 | 7,371 |
| SHA-256 | 29a8a350ef0facc30c1c98e5250563a4020ad9c1a243f13e795e2e68e3bd74e7 | fbe5314ab304e122162aae20ace46999b93832fc4c7451439f4ada430eccc8a7 |
| security.properties revision | 13 | 17 |
| Primary signer | Chrysler UConnect Application CA | Xlet Developer |
| Shared signer | aicas GmbH | aicas GmbH |

Both contain 17 ZIP entries. Device.class, base.policy, complete.policy, full.policy, xlet.security, and xletmanager.policy are byte-identical. Every manifest entry digest recomputes. The only visible functional-resource difference is security.properties revision/timestamp; signature/container metadata and the primary signer differ.

Development selection therefore does not load visibly broader policy text. One effect is now direct: AMS promotes certificates on the selected JAR's `xlet.security` entry into final token/certificate verification keys, changing Chrysler+aicas in production to Xlet Developer+aicas in development. Whether revision and signer identity also change principal construction or policy assignment remains UNKNOWN. The security JAR contains no anti-theft implementation.

### 9.2 cacerts and signer inventory

Kona cacerts is a 10,117-byte JKS v2 file, SHA-256 2b931d5574d94c886a2ec13c3301585e405f2d68abf90fed3287383e55c7d0d0, with seven trusted-certificate entries. None of those seven fingerprints equals any of the five signer fingerprints found in 163 signed JARs.

The 300-JAR signer census found:

- 146 Chrysler UConnect Application CA signature-block occurrences, including 123 application key.jar files.
- 16 FCA VP4 Application occurrences, including 12 key.jar files.
- Two additional Accenture occurrences on dual-signed key JARs.
- Two aicas occurrences, one in each security configuration.
- One Xlet Developer occurrence, only in development/security.jar and in no application key.jar.

This proves that visible cacerts is not a complete direct fingerprint list for security-configuration or application-signing trust. It does not prove that the stock signers are untrusted; AMS may use embedded keys, special security-configuration handling, principal rules, or another store. Adding a root to cacerts is not an evidence-supported application-signing design.

### 9.3 key.jar is the detached application signature

Across all 135 factory application instances:

| Measurement | Verified result |
| --- | ---: |
| Executable regular members | 78,756 |
| Executable members covered by companion key manifest | 78,756 |
| Uncovered executable members | 0 |
| Total manifest entry-digest records recomputed | 82,938 |
| Matching records | 82,938 |
| Missing members or digest mismatches | 0 |
| Full-manifest digests in META-INF/*.SF | 137 of 137 matched |
| PKCS#7 signatures over the .SF payloads | 137 of 137 verified mathematically |

Every key.jar contains signed manifest material plus embedded xlet.properties and no application class. The separately stored executable JARs contain code but no internal signature block. The verified binding is:

~~~text
all executable JAR members + key.jar!/xlet.properties
  -> key.jar manifest entry digests
  -> .SF full-manifest digest
  -> .RSA PKCS#7 signature
  -> embedded signer certificate
~~~

The PKCS#7 check proves signature math against the embedded certificate, not AMS trust-chain, expiry, revocation, or principal acceptance.

Installed filesystem descriptors differ bytewise from their signed embedded descriptors in all 135 cases, usually because xlet.jarFile is normalized to the installed name. App ID, main class, vendor, name, policy, default policy, and developer token agree wherever present. Authenticity must therefore be based on the signed embedded descriptor/member set, not a bytewise comparison with the installed normalized descriptor.

Installed AMS path ownership is now direct. `Installer.getKeyJarFile`, method marker `0x5C05BE`, ignores its `Properties` argument and constructs fixed sibling `<appId>/prog/jars/key.jar`; only the payload helper reads `xlet.jarFile`. `AMSController.loadXlet` calls both helpers at `0x5BB432/0x5BB43C`, `XletManager` checks and converts the key file to a URL at `0x5C5FD9..0x5C5FF3`, and `VerificationClassLoader` stores it in `keyJar_`. When present, signer lookup invokes `getJarEntryCertificates(keyJar_,"xlet.properties")` at `0x5C2AFE..0x5C2B08`; when absent, it falls back to the primary resource. The fixed installed association and signer-object source are confirmed. The certificate extractor and `SigningKeys.verify(Object[])` are AOT/native-form, so exact cross-JAR digest recomputation, chain ordering, revocation/time behavior, and final principal assignment remain unknown. See `reports/keyjar_runtime_association.md`.

### 9.4 DRM.jar is a separate entitlement object

Twenty-six KIM roots contain DRM.jar. The signed descriptor carries grantList records keyed by appIdentifier plus installer type, feature and launcher masks, version, filename/length, VIN/date, and related grant metadata. The DRM signer and grant authorize an application identity and installation attributes. key.jar separately authenticates executable bytes and descriptor metadata.

Native AppManager performs a local grant check before authenticated AMS inspection. These controls must not be collapsed into one signature check.

### 9.5 Developer token and AMS verifier vocabulary

Six factory descriptors, representing two Tweddle application IDs replicated in KIM1/KIM12/KIM16, carry the same `xlet.developerToken` Base64 text, which decodes to the same 256-byte value. In all six cases:

- the same semantic property is inside signed key.jar!/xlet.properties;
- its descriptor digest matches the key manifest;
- the full manifest digest matches the .SF;
- the PKCS#7 signature verifies; and
- the key JAR uses the normal Chrysler production application signer, not Xlet Developer.

The value is intentionally not reproduced. The evidence supports package/vendor signing-time metadata, not a transient anti-theft session result.

A read-only cryptographic census now rules out the most obvious format. Three hundred JARs, 163 signed JARs, 167 embedded-certificate occurrences, Kona `cacerts`, and recovered standalone public-key structures reduce to 19 distinct SPKI identities: 17 RSA and two non-RSA. Fifteen RSA keys are compatible with the token's 256-byte length. They include the compatible Chrysler/Xlet Developer/VP4/Accenture signers and recovered standalone SSH/SWDL/service-certificate/OTA-delta verification keys.

Across 19 deduplicated public identities (17 RSA, two non-RSA), 15 RSA keys are compatible with the token's 256-byte decoded length. Raw public classification produced zero valid PKCS#1 v1.5 blocks and zero strict PSS structures. The exact bounded matrix made 418,320 comparisons: 30 compatible key/complete-token-byte-order recoveries times 332 descriptor/identity/digest/certificate/SPKI message forms times six PKCS#1 v1.5 hashes plus all 36 PSS message-hash/MGF1-hash pairings. Every comparison failed and in-memory positive controls passed. This rules out those tested conventional signature interpretations. The AOT/JCE consumer is now independently proved to use Base64 decoding plus SunJCE `RSA/ECB/PKCS1Padding` public-decrypt/type-1 semantics and exact ID equality, not Java `Signature`; runtime ID and the legitimate issuer remain unresolved.

The result is reproducible with original metadata-only tooling: `analysis_tools/developer_token_crypto_probe.py`, 41,177 bytes, SHA-256 `f63aff730bdd59b78e832aec385d79564acab5919119e9616f84b8e806766bd8`, and its 19-test suite `analysis_tools/tests/test_developer_token_crypto_probe.py`, 18,219 bytes, SHA-256 `505bc76bf89b0a8b34be3d45f14f2ca6b2d4cfc2329d91d773f278952387540f`. Together with six QNX imagefs tests and 22 Jamaica metadata-decoder tests, all 47 pass. Two 32,257-byte corpus JSON runs were byte-identical with SHA-256 `91eec01858afddb2313e423e585bca4fcad46ad57baa72b65e78e9122374c5bc`. The renderer exposes fingerprints/counts only; it does not emit token bytes, PEM, moduli, recovered blocks, private data, or authentication values, and regression tests sanitize malformed-key errors and certificate subject controls.

The current tag-driven decoder reproduces the complete AMS name/descriptor pool from file `0x9C2071` through terminator `0xAB8ECC`: 60,877 entries, 1,011,292 inclusive bytes, SHA-256 `3663f3ee68908e0625de021a53537f33264786fb350e54b8fd5614786ed888fb`. Among its exact names are:

| AMS name | File offset |
| --- | ---: |
| developerId | 0xA72B3C |
| developerToken | 0xA72B42 |
| getDeveloperId | 0xA78AE5 |
| getDeveloperToken | 0xA78AF0 |
| getKeyJarFile | 0xA7A107 |
| getPackageInfo | 0xA7B136 |
| keyJar_ | 0xA88272 |
| verifyDeveloperKey | 0xAA0296 |
| verifyManifestHash | 0xAA02D5 |
| verifyPolicySigned | 0xAA0315 |
| verifyWithSeparateSigningKey | 0xAA03BA (standard PKIX CRL-revocation method; not RA4 package-auth evidence) |
| xlet.developerToken | 0xAA146C |
| xlet.policy | 0xAA14D2 |
| xlet.security | 0xAA150A |

The pool tags, rather than `index % 26`, identify reset, front-coded, and extended full entries. A separate literal table at `0xAB8ED0..0xAD1E9C`, 28,142-record global member-selector table at `0xAD1EA0..0xB08E10`, and 4,599-entry class-pointer table at `0xB1BC48..0xB20424` join those names to pointer-bounded class objects and executable bytecode.

The `verifyWithSeparateSigningKey` name is now deconflicted. Plain AMS diagnostics at file offsets 0xA2BD2F, 0xA2FDF1, 0xA2FE69, 0xA2FEC1/0xA2FF3E, and 0xA2FF12 identify the standard Java `CrlRevocationChecker` path. Public OpenJDK-derived source assigns that method to certificate-revocation processing with a separate CRL-signing key. It is not evidence for the detached application `key.jar` path; `verifyDeveloperKey`, `getKeyJarFile`, and the actual package verifier remain the relevant unresolved names.

Class-object ownership is confirmed for `AMSController`, `KeyVerifier`, `SecurityParameter`, `SignedId`, `SigningKeys`, `VerificationClassLoader`, and `XletProperties`. Exact property binding is:

`XletProperties.DEVELOPER_KEY_PROPERTY` -> CP#8 at `0x5C7039` -> literal index `0x4924` -> literal-table word `0xACB360` -> pool entry `xlet.developerToken` at `0xAA146C`.

`VerificationClassLoader.getDeveloperToken()String`, marker `0x5C2BB4`, loads that key at `0x5C2BF3`, performs the property lookup at `0x5C2BF5`, and caches it at `0x5C2BF8`. Its private verifier body `0x5C2AD1..0x5C2AEA` passes that value and the device token to `KeyVerifier.verifyAllCertificates`.

The confirmed decision is:

```text
verifyDeveloperKey(developerToken)
OR
(
  deviceToken == null
    ? verifyCertificates(objects)
    : verifyDeviceKey(deviceToken) AND verifyCertificates(objects)
)
```

`verifyDeveloperKey` body `0x5C1B0A..0x5C1B25` constructs `SignedId(developerToken,SecurityParameter.getDeveloperId())` and verifies it with the final selected-security-JAR signing keys. `SignedId.decrypt(PublicKey)`, bytecode `0x5C2335..0x5C2364`, calls `key.getAlgorithm()`, `Cipher.getInstance(algorithm)`, `Cipher.init(2,key)`, `BASE64Decoder.decodeBuffer(token)`, `Cipher.doFinal`, and `new String(byte[])`. `verify(PublicKey)`, `0x5C22F1..0x5C2326`, rejects null ID and accepts only `decrypted.equals(id)`; exceptions return false. The array overload `0x5C22BC..0x5C22E6` tries every key and stops at the first success.

The provider default is no longer unknown. AMS's embedded security resource places SunJCE at provider 4 (`0x899EDB`; provider block `[0x899E43,0x899FE5)`, SHA-256 `18e2f729eb57da4f2ed0abe2f6a4957ee845a21c6d53060c8a89e535f3893e9b`), and `SunJCE$1.run` registers `Cipher.RSA`, implementation `com.sun.crypto.provider.RSACipher`, mode `ECB`, and supported paddings at `0x5E5CF7..0x5E5FE2`. Bare `RSA` leaves mode/padding null in `Cipher.getTransforms`; `Cipher$Transform.setModePadding` therefore skips both setters. `RSACipher` supplies constructor default `PKCS1Padding`, maps public-key decrypt to `MODE_VERIFY`, selects `RSAPadding.PAD_BLOCKTYPE_1`, performs the public primitive, and unpads at `0x5E4F6F..0x5E53AF`. Exact class bounds and hashes are in `reports/signedid_jce_semantics.md`.

The trust bootstrap is two-stage. `AMSController.<clinit>` scans `rom:/internal.jar` for `xlet.security`, obtains its signer certificates, extracts public keys, and stores `_internalKeys_` at `0x5BBC1C..0x5BBD1C`. The embedded JAR is pointer-bounded at AMS file `[0x988778,0x9892AD)`, 2,869 bytes, SHA-256 `2dbf7986c70e16d7bb047b897492c6ce164a1b5954837590708ee65b73759dab`; all manifest digests and both detached signatures verify. Its bootstrap certificates are aicas DSA SHA-256 `9f28ad4b65f3eca46049b9f6abfb5c169b8c1ea35dde01380c689dbceab10d4c` and aicas RSA `0654d97249cd24168cffbd7987ba6a05b76550dc95d765a9dafc59aaf11afe07`. A temporary VCL authenticates the selected production/development `security.jar` with those roots at `0x5BA8C2..0x5BA8D0`; selected-JAR `xlet.security` certificates are promoted at `0x5BA8F9..0x5BA940` into final `SecurityParameter.signingKeys` at `0x5BA958..0x5BA965`. Production promotes Chrysler+aicas candidates; development promotes Xlet Developer+aicas. All four corresponding `.SF` records explicitly cover `xlet.security`.

`AMSController` reflectively calls `com.aicas.xlet.manager.Device.getDeveloperId/getDeviceId`. An exhaustive census covered 300 JARs, 88,666 entries, 72,507 decompressed classes, loose files, nested archives, and launch/configuration text. Every recovered production/development/Kona `Device.class` copy is byte-identical (481 bytes, SHA-256 `a452ac3005bbf0bdf18c7dd6d8fed766f7d130524170b4cfbae037efb2edc6e8`) and defines neither getter; no other class contains `getDeveloperId`. The VCL inherits the system loader, but the system-visible Kona copy is the same stub and no stock classpath/boot overlay option exists. Recovered stock therefore returns null; only mutable live-unit state absent from the update corpus remains a theoretical provider.

Remaining unknowns are the legitimate private-key issuer, implicit plaintext charset, any live-unit `Device` overlay, exact AOT certificate-extraction and `SigningKeys.verify(Object[])` flows, certificate-array ordering/filtering, incoming-package detached association, signer/principal mapping, policy combination, and total order of DRM/signature/descriptor/token/registration decisions. No DBus/SvcIPC/native/PIN edge appears in the recovered ID/token path.

### 9.6 Policy and AppManager permission

All 135 signed descriptors specify xlet.policy.default=full.policy. Of those, 122 also name security.policy, and every corresponding executable JAR contains that signed policy file. There are 18 unique per-application policy hashes.

The stock global policy resources include:

- base.policy for baseline property/file/environment grants.
- complete.policy containing AllPermission.
- full.policy granting AppMgrPermission appMgr and chain while leaving setSecurityManager/setPolicy commented.
- xletmanager.policy containing AllPermission.

In kona.jar, MethodPermission.checkPermission obtains the active SecurityManager and calls SecurityManager.checkPermission when non-null. AppManagerImpl install, uninstall, DRM, start, pause, and stop methods construct/check AppMgrPermission("appMgr") before SvcIPC. For example, installApp code starts at class-file offset 0x2B28, checks permission at 0x2B31, loads installApp at 0x2B65, and invokes SvcIpcClient at 0x2B6C.

This is a caller authorization boundary, not proof that a submitted package is authentic. The rule that combines global policy, signed application policy, signer principal, and production/development selection remains UNKNOWN. A safe application must not request AllPermission or unexplained AppManager control.

## 10. Application installation and lifecycle

### 10.1 Resident USB detection and authenticated external dispatch

The normal-runtime outer detector is no longer an open gap.

analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/usr/bin/cmc/service/swdlMediaDetect/loader.lua is 22,538 bytes, SHA-256 f562650958dc487d8558571744cc517ba583550b29c79dba4f335fc07c47e885, inventory line 223:

- Lines 70-80 configure MCD media rule SWDL, /fs/usb0/swdl.upd, outer mount /fs/swdl, nested installer/primary/secondary ISO names, installer mount /fs/installer, manifest etc/manifest.lua, and /etc/keys/swdl.pub.
- notifyOnInsert lines 497-568 accepts the usb0 event, mounts the outer image, authenticates every present nested ISO, requires installer.iso, mounts it, and loads its manifest.
- authenticateISO lines 250-428 verifies the nested ISO header signature, recovers and compares the signed data hash, and handles the authenticated copy/mount boundary.
- executeExternalScript lines 595-621 exports ISO_PATH=/fs/swdl, USB_PATH as the detected USB mount, and INSTALLERISO_PATH=/fs/installer, then executes the selected script from the authenticated installer ISO.

swdlMediaDetect.lua is 18,115 bytes, SHA-256 0bf54e5866ad0a8bff467e592e5ee46d877ba957ee6f1f266f7d94191001088c, inventory line 228. processManifest lines 242-266 dispatches manifest.external.start_script as an external installer rather than entering the normal full-update confirmation/reset path.

The stock 18.45.01 full-update manifest has a normal parts table at installer_iso/etc/manifest.lua lines 230-237 and no external member. Therefore the detector, nested-ISO authentication, manifest load, environment handoff, and external-script dispatcher are CONFIRMED, while the exact factory external manifest, selected start_script value, and a sample live application package remain UNKNOWN.

### 10.2 Stock live application installer

us-app-install.sh, SHA-256 9c199f28d595b61107a04d4e63a31d5f252302d4b3163f265819ce81dbc326bf, requires ISO_PATH and USB_PATH and launches us-app-install.lua, 7,754 bytes, SHA-256 f3de29bef88d1a92fec3cf7e0c84c065eadc71ca898d9b674c6ff15b682ba7ec.

Static Lua flow:

- Prototype 10, debug lines 325-352, walks ISO_PATH/usr/share/APPS application directories, locates JARs, calls AMS getAllProperties, and queries installed Kona version.
- Prototype 8, lines 265-298, captures the JAR filename and stages at `/fs/mmc0/xlets/temp/<jar-filename>`, calls getPackageInfo on the staged URI with auth=false, and previews the installed application identity.
- Prototype 15, lines 382-445, checks Kona minimum/maximum version, calls AMS install or upgrade, requires status=ok, and removes the staging file.

auth=false is confined to metadata preview. The subsequent install/upgrade does not pass that flag, and AMS remains -secure. It is not an authentication bypass.

The corpus contains no external-install manifest and no usr/share/APPS package sample. Factory KIM layout must not be assumed to be the complete live outer-JAR format.

### 10.3 Kona/native AppManager authentication boundary

Kona AppManagerImpl checks AppMgrPermission("appMgr") and sends installApp through com.harman.service.AppManager. Native AppManager then:

- performs the default-enabled local DRM grant lookup;
- constructs filename and uri at 0x19206C and 0x1920F0;
- adds auth=true at 0x192878/0x19288C;
- constructs getPackageInfo at 0x1928C8;
- calls its asynchronous AMS wrapper at 0x192904 with callback 0x193E9C.

Native `installNow` calls adapter file `0xEA84` from `0x91C40`. That adapter materializes request key `uri` at files `0xEAD4/0xEAD8` and exact AMS method `upgrade` at `0xEB34/0xEB38`. Thus catalog `installApp`, including the catalog's fresh-install task, always converges on AMS `upgrade`; the USB script is the recovered path that explicitly selects AMS `install` for an absent app. Whether AMS `upgrade` is a general upsert remains unknown.

The native binary identifies com.aicas.xlet.manager.AMS and /com/aicas/xlet/manager/AMS at file offsets 0x1156D0/0x1156EC. Its DRM-update preflight calls the same getPackageInfo wrapper at 0x1BD83C with callback 0x1BD8E4.

Native AppManager contains no key.jar, META-INF, MANIFEST.MF, .SF, or .RSA vocabulary and links no crypto library. AMS contains getKeyJarFile, keyJar_, and verifier names. The supported responsibility split is:

- request orchestration, error mapping, and local DRM grant gate: CONFIRMED native AppManager;
- authenticated package inspection: CONFIRMED AMS request boundary;
- installed fixed key.jar path, loader propagation, `key.jar!/xlet.properties` signer-object source, and verifier branch order: CONFIRMED AMS call graph;
- exact AOT certificate extraction, cross-JAR runtime digest processing, and `SigningKeys` key match: UNKNOWN implementation;
- exact token-verifier branch, Base64/SunJCE-RSA/ID predicate, and internal-root-to-selected-JAR key promotion: CONFIRMED; legitimate issuer/live ID and principal/policy mapping: UNKNOWN.

### 10.4 Other installation paths

- **KIM3 Application Manager:** application ID c1d77320-6335-48b2-aa22-21912f657311 stages at `/fs/mmc1/download/<huFileName>`. `BaseUpdateInstallTask` enables cleanup and server-directed uninstall-first handling through `filesToDelete`; `InstallerImpl` optionally calls `uninstallApp(appId)`, then calls `installApp(appId,jarFile.getName())`. Install/Update tasks differ in the version sent to the server but converge on this same route. CRC32 proves transfer integrity, not signer authentication.
- **Factory software update:** manifest.lua lines 113-126 define the Apps unit from secondary.iso to /fs/mmc1 using installer xlets. xlets.lua reads the head-unit part number, selects KIM via kim_pkg_map.lua, and copies base/preload/selected Xlets with qkcp. This is factory population, not the narrow live installer. Recovered `qkcp`, 50,222 bytes and SHA-256 `aa5605bdd69581aad74c05213553ccac2468399de18f539cf1c2029d58207198`, proves that `-h` is only a 56-byte shared-memory progress channel. KIM passes no `-f/-r` checkpoint pair, and neither caller nor executable consumes `xletsdir_ref.txt`. The copier creates/truncates final destinations directly and has no rename/remove rollback primitive, so this layer is a confirmed non-atomic merge/overwrite that can leave partial or mixed state (`reports/qkcp_kim_copy_semantics.md`).
- **Visible installed state:** `/fs/mmc1/xletsdir/xlets/<appId>/prog` contains normalized descriptors and JARs. AppManager configuration also identifies `/fs/etfs/usr/var/appman/xletRMS`, preload, live DRM, and restore DRM paths. AppManager's separate catalog persistence is now confirmed as whole-list JSON key `AppManager_JavaApps` in PersistentKeyValue/QDB `/usr/var/qdb/key_value`; the hidden AMS package registry and cross-layer transaction remain unknown.

### 10.5 Lifecycle evidence and gaps

Native AppManager now proves substantially more of the stock per-application uninstall path. In analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/bin/appManager, SHA-256 608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591:

1. The uninstallApp dispatcher at file offset 0x54058 / VA 0x154058 enters startUninstallApp at VA 0x191158 / file offset 0x91158.
2. startUninstallApp stops a running application when necessary and reaches uninstallNow at VA 0x190FAC / file offset 0x90FAC. Its call at file `0x910B0` targets AMS adapter file `0xE854`, which materializes request key `appId` at `0xE8DC/0xE8E0` and exact AMS method `uninstall` at `0xE964/0xE968`.
3. The asynchronous completion path enters onUninstalled at VA 0x18FE94 / file offset 0x8FE94, then the finishUninstallation dispatcher at file offset 0x5CF74 reaches VA 0x193910 / file offset 0x93910.
4. finishUninstallation invokes cleanUpXletResources at VA 0x13B0CC / file offset 0x3B0CC and queues deleteAppFromHashMap. The event loop at file offset 0x5C058 invokes the associated handlers at VAs 0x156DFC and 0x133C4C.
5. removeRMSFiles at VA 0x131B94 / file offset 0x31B94 uses the configured xletRMSDir /fs/etfs/usr/var/appman/xletRMS, recursively removes the per-app directory `<xletRMSDir>/<appId>` through its constructed `rm -R` invocation, and removes the per-app common record `<root>/common/<appId>.rs` through `rm`.

This is direct static proof that stop-if-needed, asynchronous uninstall completion, Xlet-resource cleanup, per-app RMS cleanup, and queued native-map removal belong to the stock uninstall lifecycle. After map deletion, the dispatcher emits `appListUpdated` and queues a complete `AppManager_JavaApps` save through files `0x5C130..0x5C1C4`. It is not proof of atomicity, power-loss/interruption behavior, exhaustive ownership of every app-created file or AMS record, or restoration of a previous version. The recovered delete commands describe native implementation internals and are not a supported manual-uninstall procedure.

`AppManager_JavaApps` is string file `0x101C54`. Its loader starts at VA `0x130050` / file `0x30050`. Its writer starts at VA `0x157698` / file `0x57698`, performs separate persistence `read` and full-value `write` IPCs through `0x57704..0x577C0` and `0x58818..0x58858`, and is called only by dispatcher file `0x5C348`. Install queues the save only after AMS success/native finalization and `appListUpdated` (`0x91580..0x9160C`); uninstall queues it after cleanup/map deletion. No CAS, generation, transaction ID, or retry loop is present.

PersistentKeyValue's default rule routes the key to QDB `/usr/var/qdb/key_value` (`pmem_keyvalue.ini:14-20`; `qdb.cfg:41-44`), table `keyvalueTbl(key TEXT PRIMARY KEY,value TEXT NOT NULL)`, with `journal_mode=truncate`. The key-value section has no backup directory; `qdb_recover.sh:21-22` deletes `key_value*` on corruption.

AMS class-object metadata assigns `Installer.install(String)Application` to body `0x5BFCC0`, `Installer.recoverProgIfNeeded(String)V` to `0x5BFDFD`, and `Installer.upgrade(String)Application` to `0x5BFE8C`. The recovery method loads exact `prog.bak` at `0x5BFE1B` and `0x5BFEE3`; install/upgrade load their exact directory-rename diagnostics at `0x5BFD56`, `0x5BFF2E`, and `0x5BFF5C`. Ownership is confirmed; normal-upgrade invocation, parent path, exact rename/restore/delete order, completeness, and crash behavior remain unknown. See [appmanager_registry_atomicity.md](reports/appmanager_registry_atomicity.md).

Post-install launch is now statically resolved through the stock HMI/module/native route. `onInstalledSignal` at VA 0x1938A8 reaches `finishInstall` at VA 0x1935BC; the latter calls conditional `autoStartApp` at file 0x93858. Autostart requires `(DRM mAppLauncherMask bit 2 OR the stock super-app override) AND the global autostart gate`; the mask is loaded/tested/extracted at files 0x1BB38, 0x1BB3C, and 0x1BB64. When false, the path reaches `INSTALLATION DONE` and successful completion at files 0x91A30/0x91A64 without calling the App start primitive.

An ordinary non-autostart app therefore remains stopped and requires a later explicit request. ROV `AppsMainScreen.swf` (SHA-256 `5df0c52056d9495c439e8c90d1826be132f43bc7d4a61951acd4f1adfccbd04d`) handles the generic item selection in `onItem` (method/body/code `0x9F17/0xBDA0/0xBDA7`) and calls `IAppManager.startXlet(selected.appId,"MoreScreen")` at FWS `0xC1E6`. ROV `MainSupplement.swf` (SHA-256 `e9d796ea4b4c83ed518bfe3b3c341e54e510a1ae0f78ebbffbd655b7c36a3258`) implements module `AppManager.startXlet` at `0x1E7A0B/0x2A9712/0x2A971A`, emits `startApp` at `0x2A97E1`, and sends it at `0x2A97E7/0x2A9AF6`. Native `parseRequest` compares that request at file 0x53DD0 and dispatches at 0x53DF0 to VA 0x14FDB0, which calls `findAndStartApp` with DRM checking enabled at files 0x50650/0x5066C; the App start primitive is reached at 0x3C328. This generic HMI route does not traverse Java `AppMgrPermission`; Java `AppManagerImpl.startApp(String,String)` is a separate caller surface that checks `AppMgrPermission("appMgr")` and invokes SvcIPC at class offsets 0x3565/0x356E/0x35A7/0x35B0.

The complete native parser range, VA 0x1516D4..0x156DFC, contains 56 constant method comparisons but no `enableApp`, `disableApp`, or `launchApp`; a full-file ASCII/case-insensitive/UTF-16LE census and the Java public API agree. This is a confirmed bounded absence of an explicit per-app enable/disable operation in the recovered surfaces, not proof against an external numeric-only suppression state. The stock caller is identified, and the HMI's generic catalog path has no downstream `enabled`, `hidden`, or `suppressed` field; whether native AppManager omits a newly authorized helper from `getAppList`, and its target-unit name/icon/category behavior, remain dynamic unknowns.

| Operation | Current evidence |
| --- | --- |
| Package information/list | HIGH - live installer calls getAllProperties/getPackageInfo; AppManager whole-list JSON/QDB catalog is confirmed, hidden AMS package registry remains unknown |
| Install | CONFIRMED - live installer calls AMS install for an absent app; KIM3 calls native AppManager installApp, which converges on AMS upgrade |
| Upgrade | CONFIRMED - live installer selects AMS upgrade for an existing app; catalog fresh/update paths also converge on upgrade |
| Enable/disable | CONFIRMED bounded negative - no explicit per-app operation exists in the recovered native parser or Java API; launcher entitlement/global autostart are separate |
| Start | CONFIRMED UI/module/native route plus API dispatch - ordinary install completes stopped; the generic Apps entry sends native DRM-checked `startApp`; the permissioned Java API is separate |
| Pause/stop/destroy | CONFIRMED API/native dispatch - permissioned Kona and native pause/stop paths exist; AMS initializer handles controlled Xlet destruction; supported pause/stop UI grammar still needs runtime validation |
| Uninstall/remove | CONFIRMED native lifecycle - KIM3 calls uninstallApp; native AppManager stops if needed, completes asynchronously, cleans Xlet resources/per-app RMS, deletes the native-map entry, and queues full-list QDB persistence |
| Persistence/cleanup | PARTLY CONFIRMED - Xlet tree, RMS path, resource cleanup, native map, and `AppManager_JavaApps` QDB list are known; AMS registry/payload deletion, exhaustive ownership, and reconciliation remain unknown |

The visible AMS callback, resource move/cleanup, native-map update, and QDB whole-list write are separate phases, not one transaction. No A/B application slot or complete previous-version restoration contract is proved. `Installer.recoverProgIfNeeded` proves a real `prog.bak` recovery facility, but not an ordinary-upgrade rollback guarantee. An explicit success result is not by itself proof that AMS, AppManager, process, filesystem, RMS, and QDB state all agree.

## 11. Legitimate full USB software-update path

The full-update path is distinct from the external live application installer:

~~~text
USB swdl.upd
  -> resident swdlMediaDetect
  -> nested ISO authentication and manifest load
  -> normal full-update parts table
  -> installer state machine
  -> 13 ordered system/peripheral/application units
  -> completion/reset or resume/retry/failure state
~~~

Each nested ISO begins with a 32,768-byte custom signed header. isochk.lua, 9,509 bytes, SHA-256 51b4777fa98e8a0f338336b2ebacd7cdccd9e1493817c76f3ef41cad33be2e9f, is designed to:

1. parse the header/build fields;
2. verify the signed header using RSA/SHA-256 and /etc/keys/swdl.pub;
3. enforce target variant/product/market/model and downgrade rules;
4. recover and compare the signed full-ISO data hash and size; and
5. authenticate install-monitor hash material.

The hidden-HBC recovery materializes the referenced key at analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/etc/keys/swdl.pub (inventory line 53): 451-byte PEM public key, SHA-256 804e7cdf410c74a2b6ac52084d9b24c7b5becfd5bbb66a32819356d01f5b676e. Earlier finalized-report statements that this file was absent predate the recovery and are superseded. Independent read-only replay with that public key succeeds for all three nested ISOs: the RSA-SHA256 header signature over bytes 256..32767 verifies, and PKCS#1 public recovery of block 127 returns the exact SHA-256 of bytes 32768..EOF. The recovered data-region hashes are installer.iso 880561a00022ea658a211a76947abb2e2cef1882e64372c6209b3ec7ee7337c1, primary.iso fd5e4ab6409eb6e583c7ccf82d0a7be08980a8b081677efc32f0b0fe94dbe5c6, and secondary.iso 22468c3ba91c125559f6269c444a5c32fa437c08cac8d4b304f55e8ec5761898. This proves the recovered key validates these stock nested ISO envelopes; because it is public-only, it cannot create an accepted signature or authorize modified media.

install.sh copies/authenticates primary.iso, mounts authenticated primary and streamed secondary, starts installmonitor.lua, persists resume/authentication state, and invokes softwareupdate.lua. installmonitor samples streamed secondary blocks against signed IMHF material.

manifest.lua defines 13 ordered units: system check, IOC bootloader, IOC, System, System Data, Speech, EQ, Apps, Embedded Air Card, XM pre-update, XM update, HD update, and OTA update. softwareupdate.lua persists unit/substate and supports retry/resume/reset across required IOC modes.

Resumability is not rollback:

- no general A/B system slot, per-unit undo log, previous-IFS restore, or reverse-flash path was found;
- earlier units can remain written when a later unit fails;
- parseConfig supports backup/restore syntax, but no active stock config uses it;
- MMC Take Back temporarily preserves /fs/mmc1 around a specific repartition flow only;
- a full update is disaster recovery, not routine one-app rollback.

The original signed update must remain byte-for-byte unchanged. It is not an application packaging shortcut.

## 12. Persistence, return to production, and safe design status

### 12.1 Marker persistence boundary

/fs/etfs is a NAND ETFS partition: primary_iso/etc/nand_partition.txt lines 23-24 define ETFS, primary OTA ifs_part_list line 7 maps /fs/etfs, and installer etfs.sh lines 183-197 mounts it. A successfully created root marker is therefore persistent operational state, not a /tmp flag. Ordinary reboot persistence is HIGH, pending direct target observation.

The documented FOTA ETFS flow backs up only /fs/etfs/usr/ before erase/restore. fota_etfs.sh line 128 defines that backup root; erase and restore occur at lines 74 and 84. Root-level /fs/etfs/AMS_DEVELOPMENT is not included. Treat it as persistent but not guaranteed update/format-surviving state.

### 12.2 Routine rollback is two separate operations

The intended routine rollback model, still contingent on dynamic proof, is:

1. Remove exactly the new application through the stock per-app stop/uninstall boundary and independently verify package, process, filesystem, registry, and app-owned data state.
2. While legitimate service authorization remains valid, use the stock item-19 production action, independently verify the marker is absent, allow a normal controlled AMS start, and verify the production security JAR with -secure.

The UI label alone is insufficient because creation errors are caught after the label changes. The stock item-19 owner should own both selection and return. Direct filesystem repair, xletsReturnToNew, disableDRM, or a repacked update are not rollback.

A valid service authorization window that covers both enablement and production return is a hard precondition. Item 20 is not a proved service-certificate removal path. If authorized return access cannot be guaranteed, development selection must not begin.

### 12.3 Current minimal-change candidate

The smallest defensible future design in [minimal_change_design.md](reports/minimal_change_design.md) is conditional:

- legitimately issued unit-bound service authorization;
- stock item 19 and unchanged stock security JARs;
- normal AMS start with -secure;
- a uniquely identified, least-privilege, non-daemon, non-autostart original application;
- an explicitly authorized signing/developer credential path;
- the stock authenticated live installer;
- stock per-app uninstall with exhaustive state verification;
- stock item-19 return to production; and
- unmodified compatible OEM-signed update media retained only for last-resort recovery.

Stop gates remain: native developer trust, live package format, policy-combination semantics, exhaustive per-app ownership/cleanup and uninstall interruption behavior, install atomicity/power-loss behavior, service-certificate issuance/renewal, read-only runtime state verification, and exact-unit authorized recovery procedure.

No current evidence supports modifying security.jar, cacerts, jvm.sh, AMS, AppManager, scv, public keys, update signatures, /fs/etfs/disableDRM, or /fs/etfs/enableEngMenu.

## 13. RA4 versus UAS boundary

All development-security, anti-theft, marker, AMS, Kona, key.jar, and Xlet claims in this handoff are **RA4-CONFIRMED only**.

The available UAS 21.9 tree has 44 files totaling 1,077,907,214 bytes but lacks its parent source archive, source hash, and extraction log. Its visible outer wrapper and full-update metadata are internally consistent:

- manifest.xml and its 256-byte signature verify with the included certificate;
- second.ifs hash matches the signed XML;
- the full-update metadata signature verifies with its included certificate; and
- all nine declared encrypted segment hashes match.

The UAS application/HMI payloads are encrypted. Accessible outer files contain no useful runtime evidence for AMS_DEVELOPMENT, securityConfiguration, developerToken, antiTheft, Xlet trust, or application installation. Absence from those outer files cannot prove absence inside encrypted content.

The UAS signed SAM/XML/encrypted-segment format is not interchangeable with RA4's swdl.upd plus nested ISO design. UAS can support only the general inference that both generations authenticate structured update metadata and payload integrity. It supplies no missing arrow in the RA4 authorization graph and no installation shortcut.

See [uas_comparison.md](reports/uas_comparison.md). Do not adapt or execute UAS second.ifs as an RA4 mechanism.

## 14. Remaining blockers and next safe priorities

### Blockers

1. **Developer trust decision:** the fixed installed `key.jar` association, signer-object source, property-to-token-verifier graph, Base64/SunJCE `RSA/ECB/PKCS1Padding`/exact-ID predicate, and two-stage signer-key promotion are confirmed. The recovered corpus has no usable `Device` provider. Live overlay state, legitimate issuer, AOT certificate extraction/`SigningKeys`, incoming-package association, principal mapping, revocation/time behavior, and production/development policy combination remain unresolved.
2. **Live package format:** the resident authenticated external dispatcher is proved, but no external manifest or usr/share/APPS reference package establishes the exact accepted container layout.
3. **Permission combination:** the rule combining security-configuration signer/revision, global policy, signed per-app policy, application signer, DRM grant, and optional developer token is unknown.
4. **Registry and atomicity:** AppManager's QDB whole-list catalog and its post-AMS ordering are confirmed non-atomic with the surrounding lifecycle. `Installer.recoverProgIfNeeded` owns `prog.bak`, but its exact rename/restore semantics, hidden AMS registry schema, boot reconciliation, power-loss behavior, and any upstream launch suppression remain unknown. No explicit per-app enable/disable operation exists in the recovered native/Java surfaces.
5. **Routine uninstall completeness:** the native stop/completion/Xlet-resource/per-app-RMS/native-map/QDB-save path is proved, but AMS payload disposition, interruption behavior, and exhaustive cleanup of registry state and all application-owned data remain unknown.
6. **Return authorization:** the IOC session/state-4/allowance gate is proved, but the legitimate external challenge authority and service-certificate issuing/renewal process, supported live-state refresh/revocation path, and a validity window sufficient for verified production return are not documented.
7. **Runtime activation observation:** file owner/mode, actual marker durability, live AMS argv/selected JAR, inherited PATH/user/capabilities, and a supported non-destructive restart boundary require owner-authorized read-only observation.
8. **Separate unresolved controls:** the producer of /fs/etfs/enableEngMenu and consumer/meaning of /fs/etfs/service.key remain unknown.
9. **IOC internals:** the correct-PIN comparison/success branch is located and proved separate from diagnostic authorization. The allowance consumer's raw ignition `start` state is now confirmed; its source ECU/bus/message and scheduler timebase remain unknown. Comparator provenance and retry/lockout details remain protected unknowns and must not become bypass research targets.

### Highest-value next work

1. Recover AOT `getJarEntryCertificates(URL,String)` and `SigningKeys.verify(Object[])`, then signer-to-principal/policy mapping; separately test the live-unit `Device` overlay only through owner-authorized read-only observation. The installed detached association and JCE padding boundary are no longer open.
2. Obtain an officially generated, owner-authorized RA4 external-install manifest and harmless reference package; verify its signed member graph off-unit without copying vendor credentials.
3. Prove the accepted developer signer/token issuance path and exact least-privilege policy assignment before designing application code.
4. Map or safely observe AMS registry/install/uninstall state on disposable authorized test state, including ambiguous-result and power-loss outcomes.
5. Document legitimate service-certificate issuance and guaranteed return access, including the official authority that establishes IOC session/state 4 and a supported live-state refresh after persistent removal. Preserve the stock challenge, verifier, unit binding, and allowance behavior.
6. Convert runtime-only questions into a non-mutating observation checklist for a stationary bench unit with stable power.
7. Only after all stop gates close, implement one inert, non-autostart proof application, verify installation leaves it stopped, and launch it only through the proved generic stock Apps entry while dynamically confirming `getAppList` visibility/metadata and one transition per checkpoint in the design/rollback reports.

Work should not return to trying to prove the disproven anti-theft-PIN-to-developer chain. The anti-theft path should be preserved unchanged and treated as an independent vehicle security control.

## 15. Finalized report set and precedence

| Report | Current role |
| --- | --- |
| [MASTER_FINDINGS.md](reports/MASTER_FINDINGS.md) | Concise integrated evidence index |
| [corpus_inventory.md](reports/corpus_inventory.md) | Canonical source layers, inventory snapshot, hashes, and Git safety |
| [qnx_boot_filesystems.md](reports/qnx_boot_filesystems.md) | Standard/HBC filesystem format, extraction, boot services, and service-certificate evidence |
| [service_certificate_diagnostic_transport.md](reports/service_certificate_diagnostic_transport.md) | IOC session/state-4/allowance gate, internal certificate staging/validation/removal, anti-theft directionality, and interruption properties |
| [authorization_bridge_deep_dive.md](reports/authorization_bridge_deep_dive.md) | Hard-key producer, service flag, anti-theft receiver, xletsReturnToNew, and separation matrix |
| [developer_mode_ui.md](reports/developer_mode_ui.md) | Engineering HMI, service-menu reachability, item 19, and item 20 |
| [anti_theft_auth_flow.md](reports/anti_theft_auth_flow.md) | HMI PIN submission and asynchronous state callback |
| [developer_mode_control_flow.md](reports/developer_mode_control_flow.md) | Integrated graded development/anti-theft graph |
| [ams_development_flag.md](reports/ams_development_flag.md) | Marker reader/creator/deleter census, persistence, and activation boundary |
| [ams_startup_chain.md](reports/ams_startup_chain.md) | Initial boot and AMS service-loss restart predecessors |
| [security_jar_diff.md](reports/security_jar_diff.md) | Deterministic production/development security-bundle comparison |
| [kona_trust_model.md](reports/kona_trust_model.md) | cacerts and corpus-wide signer inventory |
| [developer_token_analysis.md](reports/developer_token_analysis.md) | Installed token census, complete Jamaica metadata tables, exact AMS property/verifier graph, and runtime identity-provider blocker |
| [signedid_jce_semantics.md](reports/signedid_jce_semantics.md) | RA4 provider order, bare-RSA selection, PKCS1Padding default, and public-decrypt/type-1 semantics |
| [keyjar_runtime_association.md](reports/keyjar_runtime_association.md) | Fixed installed key.jar ownership, loader propagation, signer-entry association, and verifier ordering |
| [kona_application_authorization.md](reports/kona_application_authorization.md) | Complete detached-signature proof, permissions, native authentication edge, AMS token-verifier graph, and final -d result |
| [application_install_pipeline.md](reports/application_install_pipeline.md) | Resident media detection, external dispatch, live/KIM/factory install, and lifecycle |
| [app_launch_ui_path.md](reports/app_launch_ui_path.md) | Generic Apps catalog/item event, HMI module command, native DRM-checked launch, and bounded caller census |
| [appmanager_registry_atomicity.md](reports/appmanager_registry_atomicity.md) | AppManager JavaApps QDB registry, install/uninstall ordering, interruption windows, and AMS backup bounds |
| [qkcp_kim_copy_semantics.md](reports/qkcp_kim_copy_semantics.md) | Factory copier provenance, progress-only `-h`, non-atomic failure, and checkpoint bounds |
| [usb_update_pipeline.md](reports/usb_update_pipeline.md) | Signed ISO/full-update validation, unit sequence, resume, and rollback limits |
| [minimal_change_design.md](reports/minimal_change_design.md) | Conditional least-change design and stop gates |
| [rollback_recovery.md](reports/rollback_recovery.md) | Per-app/production return, failure matrix, and disaster-recovery boundary |
| [uas_comparison.md](reports/uas_comparison.md) | Strict generation/provenance boundary for UAS 21.9 |

Precedence notes:

- kona_application_authorization.md supersedes earlier UNKNOWN wording for native AppManager -d: it is unregistered and ignored, and the DRM checker defaults enabled.
- authorization_bridge_deep_dive.md and rollback_recovery.md supersede the earlier inference that xletsReturnToNew is a simple Xlet lifecycle reset.
- authorization_bridge_deep_dive.md and the final design reports establish that item 20 deletes /fs/etfs/service.key but is not a proved revocation of /etc/security/service.cert.
- service_certificate_diagnostic_transport.md proves the IOC session/state-4/finite-allowance gate, F010 staging/finalize, F011 removal, and channel-7 forwarding. It does not prove external unauthenticated reachability, the legitimate challenge/certificate authority, or safe transactional rollback. State 4 can authorize anti-theft comparator provisioning, but PIN success has no reverse edge.
- kona_application_authorization.md supersedes preliminary descriptions of key.jar as merely a certificate or descriptor signature; it binds every executable member.
- keyjar_runtime_association.md supersedes the former unknown installed association: Installer constructs the fixed sibling, AMS propagates it to VerificationClassLoader, and signer lookup uses key.jar!/xlet.properties. AOT extraction/SigningKeys and principal assignment remain open.
- the latest application_install_pipeline.md and usb_update_pipeline.md supersede the former unknown outer-media recognizer: resident detection, nested-ISO authentication, external manifest dispatch, and environment handoff are now confirmed.
- the hidden-HBC inventory and independent signature replay supersede older usb_update_pipeline.md and rollback_recovery.md statements that /etc/keys/swdl.pub is not materialized; the recovered public key validates both signed header material and the public-recovered full-data hashes for all three stock nested ISOs, but cannot sign modified media.
- appmanager_registry_atomicity.md supersedes the former hidden-AppManager-registry unknown: `AppManager_JavaApps` is a whole-list QDB record saved after AMS lifecycle completion. The cross-layer path is non-atomic; `Installer.recoverProgIfNeeded` directly owns `prog.bak`, while the exact rename/restore contract remains unresolved.
- qkcp_kim_copy_semantics.md supersedes the former `qkcp -h` manifest/atomicity unknown: `-h` is progress-only, KIM uses no checkpoint recovery, `xletsdir_ref.txt` is not consumed by the recovered copier, and direct merge/overwrite is non-atomic.
- app_launch_ui_path.md supersedes the former stock human-facing caller unknown: the generic `AppsMainScreen` item path reaches module `AppManager.startXlet`, emits native `startApp`, and retains native DRM checking; the separate Java API retains its own permission check. application_install_pipeline.md and kona_application_authorization.md remain authoritative for stopped install/autostart policy and the absence of an explicit per-app enable/disable operation in the recovered native/Java surfaces.
- developer_token_analysis.md and signedid_jce_semantics.md supersede both the old metadata blocker and any implication that the 256-byte decoded value is passed to Java `Signature`. The exact VCL -> KeyVerifier -> SignedId branch, Base64/SunJCE `RSA/ECB/PKCS1Padding`/exact-ID predicate, internal-root bootstrap, and selected-security-JAR signer-key promotion are confirmed. The corpus-wide ID-provider census is negative; the live ID overlay, legitimate issuer, AOT certificate extraction/SigningKeys, and principal/policy mapping remain unresolved.

## 16. Repository and publication safety

Original investigation publication snapshot (current checkpoint: section 1):

- Stock/vendor firmware tracked: **NO**.
- Stock/vendor firmware staged: **NO**.
- Git index: **empty**.
- No commit or push was made by this research pass.
- analysis_ra4_18.45.01, analysis_uas_21.9, source archives, ISOs, decoded filesystems, vendor binaries/JARs/SWFs/scripts, credentials, certificates, and keys remain local ignored inputs.
- Eligible project artifacts are original reports, parsers/tests, diagrams, metadata summaries, patches/deltas, and original application source only after content review.
- Before every future commit, inspect the complete staged-name list and staged diff and reconfirm Stock/vendor firmware staged: NO.

This handoff intentionally contains no raw developer token, authentication key value, anti-theft PIN, service certificate, private key, or reusable signing material.

## 17. Bottom line for the next researcher

The RA4 development-security selector is real, factory-shipped, and fully traced from an authenticated Service-menu gate through item 19 to the next secure AMS launch. The authentication gate is a service certificate, not the anti-theft PIN. Both the SERVICEKEY media ingress and IOC-gated internal diagserv staging/finalize route converge on stock platform verification. The IOC requires a diagnostic session and proprietary state 4 with finite allowance; its legitimate external authority remains unresolved and is not an implementation shortcut. State 4 can authorize protected anti-theft comparator provisioning, but the PIN-success path is proved one-way separate and can only trigger the destructive `xletsReturnToNew` restoration/reset in the recovered HMI flow.

The application path is also materially understood: resident USB detection authenticates the installer ISO and can dispatch an external installer; `key.jar` cryptographically binds all application bytes and signed descriptor metadata; installed AMS constructs its fixed sibling path and obtains signer objects from `key.jar!/xlet.properties`; native AppManager performs an enabled DRM gate and requests AMS authenticated package information; catalog install converges on AMS `upgrade`; AMS loads `xlet.developerToken` and evaluates it through `KeyVerifier`; ordinary non-autostart installation completes stopped; the generic stock Apps UI sends the explicit native DRM-checked launch request; and stock uninstall reaches AMS `uninstall`, then performs scoped resource/RMS/map cleanup followed by a queued whole-list QDB catalog save. That sequence is not atomic with AMS state. `Installer.recoverProgIfNeeded` owns `prog.bak`, but its recovery contract is incomplete. What remains is the missing runtime identity provider/encoding, AOT signer-key/principal rule, incoming live package exemplar, exact policy assignment, AMS payload/reconciliation behavior, and dynamically proved per-app rollback.

Until those stop gates are closed with owner-authorized credentials and non-mutating evidence, the safe implementation is no implementation. Preserve every factory security boundary and continue with the next highest-value unresolved dependency rather than reviving the disproven PIN-to-developer premise.
