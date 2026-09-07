# RA4 queued worker, timed interruption and completion-flag limits

Date: 2026-09-06. Starting canonical head
`f3943dbdd867035ac6981d83f5a86c11083d4267`. Read-only host analysis;
no radio, vehicle or phone execution.

## Decision

**STATIC_PROVED:** XletThread.run takes a queued action, builds a timed
interruptible wrapper and invokes it. Its normal continuation calls the
action's done method, notifies waiters and returns to the queue loop. This
path reuses the worker; it does not terminate the worker after each action.

**STATIC_PROVED:** XletAction.done writes only `done_ = true`. The caller's
timeout fallback also invokes that method before constructing AMSError 12.
Consequently, this Boolean cannot distinguish an observed return from the
worker's timed invocation from the caller declaring its wait finished.

**STATIC_PROVED:** the timed implementation starts a timer and reaches
AsynchronouslyInterruptedException.doInterruptible. That body dispatches
Interruptible.run and, on a selected exception path, interruptAction. The
AMS callback's interruptAction constructs AMSError 12 and stores it in the
action's error field. There are now two distinct traced TIMEOUT producers.

**UNKNOWN:** actual interrupt delivery, elapsed termination time, any late
action activity after the caller's fallback, shared-lock recovery, completion
of the caller's synchronous finally hook, and native display/input recovery.
No live overrun or overlap was observed. No runtime gate passes and no measured
resident capability fails. USB, phone transport, engine/provider and resource
gates are unchanged.

## Artifact and method identity

Use the same AMS image as the [AOT timeout report](ra4_ams_aot_timeout_runner.md):
11956352 bytes, SHA-256
`96683b789ecf06a8575915d0b446b532e1f4ee87feb31d925cb7ba3d7d324d27`.
Code addresses below are ARM virtual addresses; explicitly labeled ROM
locations are file offsets. Use ELF PT_LOAD translation, including the
writable segment's distinct mapping. The original
[registry reader](../analysis_tools/jamaica_aot_registry.py) selects method
records by class slot and method ordinal, separately from field ordinals.

| Class / method ordinal | Method | Native entry |
| --- | --- | --- |
| 439 / 4 | XletThread.run()V | `0x1A60A8` |
| 441 / 0 | TimedFromPool(RelativeTime) | `0x1A0DCC` |
| 441 / 1 | TimedFromPool.doInterruptible(Interruptible)V | `0x19F104` |
| 2547 / 1 | javax.realtime.Timed.doInterruptible(Interruptible)Z | `0x45E4C0` |
| 2448 / 6 | AsynchronouslyInterruptedException.doInterruptible(Interruptible)Z | `0x45D23C` |

Class 440, XletThread$1, implements Interruptible (class 2465). Its run and
interruptAction methods have inline ROM bodies. Class 442, XletTimed, extends
javax.realtime.Timed (2547); the independently bound class header establishes
that inheritance. These names are joined to method records, not inferred
from nearby strings.

## Worker dispatch and continuation

The worker tests shuttingDownThreads through method storage `0xC70EA8` at
`0x1A6228`; a true result selects the return path at `0x1A6238`. It calls
pollAction at `0x1A62AC`. For a selected action, it loads a long from action
offset `0x10`, constructs RelativeTime with nanoseconds zero at `0x1A64E4`,
and passes that object to TimedFromPool's constructor at `0x1A64FC`.
This trace does not derive a complete effective deadline from that argument.

It constructs XletThread$1 with the worker and selected action at `0x1A6564`.
Method storage `0xC6A6D0` identifies the ensuing virtual call at `0x1A65F4`
as TimedFromPool.doInterruptible. Its receiver and argument come from the
new timed wrapper and interruptible callback, respectively.

After that call returns on the normal path, the worker enters its monitor,
calls XletAction.done via `0xC6B564` at `0x1A66E8`, and calls
Object.notifyAll via `0xC67E54` at `0x1A6708`. After monitor release, branches
at `0x1A6748` / `0x1A6750` return to `0x1A61F8`, the shutdown/queue loop.
This is a reusable action worker, with a distinct shutdown condition. The
selected normal path does not prove every exceptional path continues.

## Timed invocation and interruption callback

TimedFromPool.doInterruptible calls XletTimed.reuse through `0xC6D654` at
`0x19F384`, then Timed.doInterruptible through `0xC6C004` at `0x19F400`.
On normal return it obtains the timed-object pool through access$000 and
calls Vector.add at `0x19F4F4`. A returned timed object is pool bookkeeping,
not a terminated Xlet worker.

Timed.doInterruptible calls Timer.start through `0xC6BF3C` at `0x45E6D0`,
then directly calls the AIE body at `0x45E6F0`. Its normal continuation calls
Timer.stop through `0xC6C17C` at `0x45E788`. The inline Timed$1 handler at
ROM file `0x717A25` invokes AIE.fire using resolved CP 3 at `0x717A29`.
Timer construction/dispatch and timer delivery on the actual radio remain
different observations.

The AIE body resolves the Interruptible.run interface member using storage
`0xC69BBC`, then calls it at `0x45E04C`. Its phase word is set to 6 before
that call. The exception jump table begins at `0x45D61C`; its phase-6 word
at `0x45D630` selects `0x45DD60`. That handler calls a runtime check; a
nonzero result branches to `0x45E190`. The ensuing interface resolution uses
literal `0x45E4B8`, containing `0xC69AE4` for Interruptible.interruptAction,
and dispatches at `0x45E248`. A later virtual call at `0x45E2C4` uses
`0xC70334`, AIE.clear. This is a selected implemented exception path, not a
proof that an arbitrary blocked instruction reaches it within a deadline.

XletThread$1.run begins at ROM file `0x5C74F7` and calls XletAction.callRun
using resolved CP 4 at `0x5C74FB`. The interruption callback begins at
`0x5C753B`: it passes **12** at `0x5C7547`, invokes AMSError's
`(int,String)` constructor at `0x5C7567` and stores the resulting reference
in XletAction.error_ at `0x5C756A`. Its message contains `timeout after `.
This callback differs from the caller-side fallback documented previously,
which constructs the same numeric error after its own wait expires.

## Why done cannot certify recovery

The complete inline XletAction.done body at ROM file `0x5C2F39` consists of
aload_0, iconst_1, putfield CP 3 and return. CP 3 resolves to class 399 field
5, Boolean done_. It performs no thread join, native cancellation or
visibility/input acknowledgment.

The no-finally caller's failure path dispatches that same done method at
`0x1A94C8`, before constructing error 12 at `0x1A9728` / `0x1A9744` and
storing the error at `0x1A976C`. The [previous wrapper trace](ra4_ams_aot_timeout_runner.md)
then explains the normal return to a synchronous runFinally call.
The done flag alone therefore cannot rule out overlap between late worker
activity and caller cleanup. This is an evidence limitation, not a claim
that such overlap has been observed on the radio.

For conceptual context only, the vendor-hosted
[RTSJ 1.0.2 AIE reference](https://www.aicas.com/rtsj/Version_1_0_2/javax/realtime/AsynchronouslyInterruptedException.html)
describes deferred interruption in non-interruptible regions, including the
lexical scope of synchronized statements; pending interruption is delivered
when execution enters interruptible code. This explains why timer expiry
alone is insufficient. It does not establish this RA4 build's conformance,
compiler settings, native-call handling or measured interruption latency.

## Consequence for the resident proof

The [future resident proof](../docs/21_first_resident_runtime_proof.md) must
correlate the exact action with worker entry/exit, interruption callback,
caller fallback, finally-hook entry/exit and any subsequent activity. It
must distinguish a reusable worker from app-created threads that should end.
It must also verify that late work cannot regain display/input ownership or
touch app resources after cleanup. Raw TIMEOUT alone cannot identify which
of the two traced paths produced it; absent origin evidence, record unknown.

Failure injection still requires separately approved spare-bench isolation.
No shared-VM hang or native stop is authorized by this report. The next local
boundary is the VM interruption-delivery/defer mechanism reached by AIE.fire
and the compiled action path, including whether this build can bound shared
monitor/native-call cases. Native stock foreground/contact recovery and a
legitimate compatible SDK/package remain separate gates.

Fresh artifact verification matches one identity, five native method bindings,
13 method-storage bindings, 60 native instruction anchors, four pointer/table
words, four complete inline method bodies and five resolved ROM references.
The pointer/table words were verified as data, not disassembled instructions.
No committed implementation or test changed in this documentation checkpoint;
the preceding 162-test host result is historical, not a new target proof.
All 114 local links across the six changed Markdown files resolve.

Follow-up: the [native interrupt request and cleanup escalation](ra4_ams_interrupt_request_cleanup.md)
trace now separates pending AIE and native interrupt status, follows the
group's blocking-I/O request into native callback dispatch, and identifies
deadline-based joins followed by another per-entry join pass. Request-side
state and configured timeout values still cannot certify action exit or total
native recovery time.
