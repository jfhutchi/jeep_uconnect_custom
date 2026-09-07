# RA4 Xlet pause policy and watchdog recovery boundary

Date: 2026-09-06. Starting canonical head `71a054a5611b02a31aa4b73bbc126f6f6b4e476e`.
Read-only host analysis of existing owner-supplied artifacts; no target execution.

## Decision

**STATIC_PROVED:** `pauseApp` does not always request a pause. After its
validation/pending checks, the native handler tests the app's
`xlet.PauseAllowed` field. True selects the `pause` wrapper; false selects
the `stop` wrapper. Consequently the stock screen-exit `pauseXlet` call in the
[foreground handoff](ra4_xlet_foreground_handoff.md) is not a universal
session-preserving Return operation. The property's recovered initialization
and reset default is false. Supported descriptor semantics and the effective
value for a legitimate new app must be qualified before its Return trial.

**STATIC_PROVED:** both wrappers call the same asynchronous service-IPC helper.
Its immediate Boolean result reflects IPC submission, not a completed Xlet
pause/stop, released input or surviving engine session.

**STATIC_PROVED watchdog mechanism:** a native AppManager watchdog loop examines
enabled per-app counters. Expiry disables that app's watch and queues a
`stopApp` request on AppManagerCore's request queue. A conditional branch also
queues `startApp` for the daemon case identified by the code's diagnostic.
This is a stock recovery candidate while AMS remains registered; the inspected
expiry function does not directly kill a process or release a window/input.

**UNKNOWN:** live watchdog activation, supported registration for a custom app,
effective scheduling/deadlines, stop completion when the app/VM is hung, and
independent presentation/input reclaim. Neither this request queue nor the
[AMS owner-change callback](ra4_display_owner_reclaim.md) closes the product's
fail-open gate. No runtime gate passes; no measured local capability fails.

## Artifact identities

Paths are relative to ignored `analysis_ra4_18.45.01/work/`. Hashes are SHA-256.
Native anchors are ARM virtual addresses, not file offsets.

| Artifact | Path | Bytes | Hash |
| --- | --- | ---: | --- |
| AppManager | `hidden_hbc_ifs/segment_00f20000/files/bin/appManager` | 1268061 | `608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591` |
| AMS properties | `secondary_iso/usr/share/XLETS/base/kona/data/ams.properties` | 287 | `790847a3a00a62cf0886565f49d103f5a16fd20fe975fced96d3427cafd0fde0` |
| Pause-enabled stock example | `secondary_iso/usr/share/XLETS/kim_packages/KIM3/xlets/c1d77320-6335-48b2-aa22-21912f657311/prog/xlet.properties` | 587 | `cf1ad2e4326821d334dd591a48d29ac30d886d9730844865655749278f8a53ff` |
| Pause-disabled stock example | `secondary_iso/usr/share/XLETS/kim_packages/KIM3/xlets/A7A4B215-9B5A-7DAA-457C-15545178E72E/prog/xlet.properties` | 560 | `5598d4287562712af2e86a7d5cba9acee3aa9fd3fb928a62f269ab1886624c29` |

The two stock descriptors contain `xlet.PauseAllowed=true` at line 9 and
`xlet.PauseAllowed=false` at line 7 respectively. These are factory examples,
not evidence that their package, identity or permissions can be reused.

## PauseAllowed storage, default and parsing

The native app contains a properties subobject at offset `0x9C`. Construction
at `0x10F158` / `0x10F164` and independently `0x112EF4` / `0x112F00` passes
that address to constructor `0x1D1850`. Thus properties offset `0x19E` is
app offset `0x23A`; properties presence byte `0x1FD` is app byte `0x299`.
This explains why a search only for stores using immediate offset `0x23A`
finds no initialization even though the corresponding byte is initialized.

| Evidence | Anchors | Consequence |
| --- | --- | --- |
| Constructor default | `0x1D1988`, `0x1D19A0` | Initialize properties byte `0x19E` to zero |
| Properties reset | `0x1CB3D0`, `0x1CB3EC` | Reset that byte to zero |
| Extraction starts with reset | `0x1CF654`, `0x1CF684` | Reset before parsing the supplied properties JSON; do not assume an earlier true value survives extraction |
| Named input | `0x1D03CC`, `0x1D03D0`, `0x1D03F4` | Select `xlet.PauseAllowed` and call Boolean-property parser `0x1CADD0`, passing default zero |
| Successful result | `0x1D0404`, `0x1D0408`, `0x1D0424`, `0x1D0430` | Store parsed byte at `0x19E` and set presence bit 0 at `0x1FD` only when the helper succeeds |
| Named output | `0x10CDF0`, `0x10CDF4`, `0x10CE04`, `0x10CE08` | Serialize the same app byte as a JSON Boolean under `xlet.PauseAllowed`; output is gated by the presence bit |

The input helper obtains the JSON member at `0x1CAE58`, checks null at
`0x1CAE7C`, requires `isString` at `0x1CAE94`, and converts with `asString`
at `0x1CAEE4`. After its string-processing helper it compares against `true`
and `false` literals (`0x200E50` / `0x200E48`) at `0x1CAF20` / `0x1CAF40`.
The recognized branches set one/zero and return success. Missing, wrong-type
or unrecognized input uses the supplied default and returns failure; the
caller then skips the field/presence update, leaving the reset false value.
Do not confuse this string-valued input with the Boolean serialized output.
This report does not prescribe a package writer or unverified case rules.

## From pauseApp to asynchronous pause or stop

The dispatcher loads `pauseApp` through the literal at `0x154FAC` and calls
handler `0x13A804` at `0x15402C`. The handler validates the ID, finds the app
at `0x13A8BC`, checks already-paused state and handles pending/busy cases
before the selected branch. This report does not claim all requests reach it.

| Selected branch | Anchors | Behavior |
| --- | --- | --- |
| Decision | `0x13AAC0`, `0x13AAC4`, `0x13AAC8` | Load app byte `0x23A`; zero branches to `0x13AB54` |
| True | `0x13AAF8`, `0x13AAFC`, `0x13AB10` | Read core timeout field `0x288`, then call pause wrapper `0x10EC54` |
| False | `0x13AB80`, `0x13AB84`, `0x13AB98` | Read the same timeout field and call stop wrapper `0x10E600` |
| Callback | `0x13AB04`, `0x13AB08`, `0x13AB8C`, `0x13AB90` | Both selected calls receive callback address `0x14ADE8` |
| Pause command | `0x10ED20`, `0x10ED24`, `0x10ED50` | Build `pause` and call common helper `0x17C4A4` |
| Stop command | `0x10E6D0`, `0x10E6D4`, `0x10E700` | Build `stop` and call the same helper |
| IPC submission | `0x17C588`, `0x17C58C`, `0x17C590`, `0x17C5E4` | Call `SVCIPC_asyncInvoke`; nonnegative submission result selects true, error path selects false |

The wrappers include the appId and preserve the supplied callback and timeout
argument through this call. A nonzero submission result is not the callback's
eventual result. The timeout field's effective value and its relation to AMS
callback timers are not established by merely observing its load. An admitted
Return can still lead to stop when PauseAllowed is false; an admitted pause
can still fail or time out. Engine-session ownership across either operation
remains a separate supported-contract requirement.

## Per-app watchdog: registration and expiry are separate from reclaim

RTTI at `0x217690` names `19CAppManagerWatchDog`; its vtable reference at
`0x217664` leads to the run entry `0x1C8384` at slot `0x217670`. The run
body calls timer handler `0x1C7C28` for two app collections at `0x1C89DC`
and `0x1C8A20`. App constructors initialize watch-enable byte `0x29C`
and counter/timeout words `0x2A0` / `0x2A4` to zero (`0x10F168` through
`0x10F174`, repeated at `0x112F04` through `0x112F10`). A watch therefore
must be enabled through subsequent stock processing.

The recovered request parser recognizes `setAppWatchDogTimeout`,
`removeAppWatchDogTimeout` and `patWatchDog`. The set helper `0x1C75A8`
first checks whether the watchdog is running at `0x1C75D0`; its false path
logs the not-running condition and returns code 5. On a successful new-watch
path it enables the app at `0x1C775C`, writes the counter at `0x1C7768`,
and stores the reset timeout at `0x1C7774`. The parser's default branch
passes integer 10 at `0x1C7A84`. These are implemented paths, not proof that
the live RA4 enables the facility or registers a new custom app.

| Timer-handler stage | Anchors | Observed action |
| --- | --- | --- |
| Eligibility | `0x1C7CC0`, `0x1C7CC8` | Skip records with watch byte `0x29C` zero |
| Counter decision | `0x1C7E24`, `0x1C7E28`, `0x1C7E2C` | Read counter through `0x10BAF8`; positive values skip the expiry body |
| Expiry disable | `0x1C80B8`, `0x1C80C8`, setter `0x10BA18` | Clear the app's watch-enable byte before constructing its stop request |
| Stop request | `0x1C80F8`, `0x1C80FC`, `0x1C8100` | Construct a request with method `stopApp` and formatted appId parameters |
| Queue insertion | `0x1C8118`, `0x1C811C`, `0x1C8124` | Obtain AppManagerCore, use its `0x334` member and helper `0x19B9A0` |
| Conditional restart | `0x1C8134`, `0x1C813C`, `0x1C8274`, `0x1C8298` | A virtual predicate controls a second `startApp` request and queue insertion; the branch's diagnostic identifies daemon restart |
| Counter advance | `0x1C82BC`, `0x1C82C0`, `0x1C82C8` | Read, subtract one, and write the app's counter |

The queue helper calls `0x1EC3C0` at `0x19B9B8`; a normal insertion stores
the request pointer at `0x1EC444` and increments queue length at `0x1EC47C`.
The timer handler thus submits ordinary lifecycle work instead of directly
reclaiming the display. Its diagnostic saying an app's time is up is not
evidence that termination has completed. The watch is cleared before queueing,
so this body alone does not establish automatic repeat attempts after a failed
stop. Do not enable daemon behavior to obtain recovery or session persistence.

The loop passes 1000 to a delay helper at `0x1C8A30` / `0x1C8A34`; the timer
diagnostic describes seconds. Neither is a measured deadline. Locks, queue
processing, scheduler behavior, callback completion and downstream AMS cleanup
remain relevant. The string `App watchdog fired` elsewhere in AppManager was
found in error-description construction and is not used as evidence of this
timer's actual firing or a direct-kill path.

## Keep the timeout evidence precise

The recovered AMS properties contain `startXletTimeout=30000`,
`initXletTimeout=20000`, `pauseXletTimeout=5000` and
`defaultCallbackTimeout=10000`, plus init/start/pause/destroy/callback priority
keys. They contain **no explicit destroy-timeout key**. The earlier
[installation report](application_install_pipeline.md) is corrected to
distinguish these facts. These values do not establish effective target
deadlines, default-timeout use for destroy, or a connection to AppManagerCore
field `0x288` without tracing their consumers.

The [AMS destroy/cleanup follow-up](ra4_ams_destroy_cleanup_contract.md) now
resolves separate compiled defaults: destroy 10000, destroy-on-error 4000 and
thread cleanup 200. It also distinguishes the compiled callback default 1000
from the external file's 10000. These stored values still do not establish
effective deadlines, live configuration or bounded input/display recovery.

## Product consequence and next evidence

The [resident milestone](../docs/21_first_resident_runtime_proof.md) must record
the custom app's effective PauseAllowed state and a supported session-owner
contract. Return, explicit Close, pause/stop callback completion, visibility
release and input release need distinct evidence. A stop-and-restart sequence
does not preserve a healthy projection connection.

**Next bounded static target:** follow callback `0x14ADE8`, queued `stopApp`
dispatch and the AMS pause/destroy consumer into app-container/input cleanup,
especially callback timeout/error behavior while AMS retains ownership. The
watchdog's enabled state, permitted app registration and timing need separate
qualification. A lifecycle timeout name is not independent failure containment.

**Callback follow-up:** the [result-completion trace](ra4_xlet_result_completion.md)
now shows stop-specific normalization of three AMS errors and a separate
NoReply mapping that remains nonzero. Stop bookkeeping can still mark the app
stopped on that failure. A malformed successful reply can also produce a
zero-code app event while the controller retains a failed-parse flag. Raw
response evidence and physical container/input cleanup must be distinguished
from normalized events and AppManager inventory.

Reproduce native anchors using the existing `ArmElfAnalyzer`, `Elf32Image`,
`disassemble(start, end)`, `plt_imports()`, `word_xrefs()` and `memory_offsets()`.
Inspect both PC-relative literals and paired MOVW/MOVT values. Account for
subobject offsets and conditional branches before attaching a property name.
All vendor artifacts and complete disassembly remain in ignored host paths.
Committed material is original analysis/specification text, with zero installed
target bytes, normal growth or staging. No radio, vehicle or phone test occurred.

Fresh validation: four artifact hashes/sizes, 110 native instruction anchors,
13 literals, four pointer records and five resolved imports matched direct
reads. The properties subobject arithmetic, two stock descriptor lines and
exact four AMS timeout keys were also checked. The unchanged full host Python
suite passed **150 tests, no skips**. These host checks do not measure runtime
pause, watchdog firing, cleanup or session preservation.
All 98 local Markdown links in the eight changed documents resolve.
