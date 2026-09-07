# RA4 interruption requests and thread-cleanup escalation

Date: 2026-09-06. Starting canonical head
`7faebedf13f990f5f642642f3ed3b4514ad847d5`. Read-only host research;
no radio, vehicle or phone execution.

## Decision

**STATIC_PROVED:** the AIE request path reaches a native setter that stores
the pending exception on the Java Thread object. For a non-null exception it
then reaches Thread.interrupt0 and a native interrupt-state update. The native
interrupt flag can be set and the request path can return without waiting for
the target action to exit. Pending exception, interrupt status and action
completion are distinct states.

**STATIC_PROVED:** XletThreadGroup.checkThreadTermination first requests
blocking-I/O interruption for group members, then performs deadline-based
joins. If threads remain, it fires registered AIEs, applies a special stop to
exactly named java.util.TimerThread instances, joins again with 50 ms per
array entry and checks activeCount again. Remaining threads cause priority
reduction and AMSError 20. This is a scoped escalation sequence, not a general
kill of every thread and not proof that all app threads terminate.

**STATIC_PROVED:** the I/O request reaches a native helper that acquires a
VM mutex, sets request state and conditionally calls a registered callback.
That helper is a separate operation from the AIE pending-exception setter.
The Java cleanup deadline is checked after the initial I/O-interruption call;
the later 50 ms join pass also exists beyond the first deadline loop.

**UNKNOWN:** a hard end-to-end cleanup bound, coverage and completion of
every native I/O callback, interrupt delivery through arbitrary app code,
shared-monitor recovery, and native window/contact restoration. No measured
local capability gate fails. The resident approach remains a candidate, with
the legitimate package/SDK and runtime isolation gates still open.

## Identity and address convention

AMS is the same 11956352-byte image used in the
[worker trace](ra4_ams_worker_interruption.md), SHA-256
`96683b789ecf06a8575915d0b446b532e1f4ee87feb31d925cb7ba3d7d324d27`.
ROM anchors below are file offsets; ARM anchors are virtual addresses. The
[AOT registry reader](../analysis_tools/jamaica_aot_registry.py) uses PT_LOAD
translation and joins method ordinals separately from fields.

| Class / ordinal | Native method | Entry |
| --- | --- | --- |
| 2475 / 26 | MemoryArea.setPendingAIE(Thread,AIE)V | `0x61F68C` |
| 2475 / 27 | MemoryArea.getPendingAIE(Thread)AIE | `0x61F360` |
| 1329 / 4 | Thread.interrupt0()V | `0x61D87C` |
| 1329 / 5 | Thread.interrupted0(boolean)Z | `0x61D82C` |
| 97 / 8 | Scheduler.interruptBlockingIO0(Thread)V | `0x5C9DB0` |
| 2475 / 8 | MemoryArea.strictRTSJ()Z | `0x61F2E8` |

## Pending exception and interrupt status

AIE.fire contains the resolved invocation of
RealtimeThread.interrupt(Thread,AIE) at ROM `0x70AC92`, CP 15. That callee's
complete inline body at `0x713D9F` tests Thread.isAlive and only then invokes
MemoryArea.setPendingAIE at `0x713DA8`; it returns void. No action-exit
acknowledgment appears in that wrapper.

The native setter stores the exception at Java Thread offset `0x18`.
Its non-null path writes at `0x61F6AC` and tail-branches at `0x61F6B4` to
Thread.interrupt0. The null path writes at `0x61F6B8` and returns directly.
The getter independently reads exactly offset `0x18` at `0x61F360`.

Thread.interrupt0 obtains the native thread pointer through helper `0x611458`,
which reads Java Thread offset `0x10` when non-null. A missing native pointer
returns at `0x61D890`; otherwise the wrapper tail-branches to `0x602F90`.
That helper first tests native-thread offset `0x180`, returns if already set,
or stores **1** at `0x602FA4`. It then selects state-dependent branches using
native offsets `0x16C` and `0x88`. Those paths may return directly or reach
helpers `0x602ED4` / `0x60CD5C`. The mask values alone are not assigned
unverified scheduler-state names here.

Thread.interrupted0 independently reads the same native offset `0x180` at
`0x61D854`, normalizes it to a Boolean, and conditionally clears it at
`0x61D868` according to its Boolean argument. This corroborates the interrupt
status meaning. It does not turn an interrupt request into thread termination.

AIE.clear at ROM `0x70ACD7` compares the current thread's pending AIE with
this object, then calls setPendingAIE with null on the matching path. The
native null-setter path does not itself clear native interrupt status; that
has the separate accessor described above. Other VM consumers may update
these states. Full asynchronous delivery/defer semantics are not inferred
from these request-side operations.

## Blocking-I/O interruption is a separate path

XletThreadGroup.checkThreadTermination calls
ThreadGroupController.interruptBlockingIO at ROM `0x5C7DE8`, before its
active-count/deadline loop. The group-controller body at `0x59A16C` checks
ThreadGroup.checkAccess, obtains its lock, enters a monitor, iterates members
and calls Scheduler.interruptBlockingIO(Thread) at `0x59A198`. Its catch-all
monitor-exit path is present. This is stock permissioned group logic; it is
not an API authorization for a custom app.

Scheduler's five-byte wrapper at `0x5994C3` invokes interruptBlockingIO0.
The native method obtains the target's native thread pointer and calls
helper `0x611D74` at `0x5C9E34`. That helper calls imported
pthread_mutex_lock at `0x611D8C`, using VM-state offset `0xAF0`. It loads a
callback from target offset `0x1D0`, sets offset `0x1DC` to 1, and, when a
callback exists, calls it at `0x611DCC` using the value at offset `0x1D4`.
The routine contains additional state checks, callback retries and waits;
its normal unlock call is at `0x611E00`.

These instructions establish an implemented callback-based I/O request.
They do not identify every registered callback or prove bounded callback
execution, coverage of a prospective projection engine's native calls, or
successful I/O completion. No callback registration or native hook is changed.

## Thread-check stages and residual-thread handling

The complete inline method is class 443 / 8, ROM `0x5C7DE2`, 458 bytes.
Its deadline-based stage compares the supplied long with
System.currentTimeMillis, computes remaining time, and calls Thread.join(J)
at `0x5C7E60` while time remains. It also notifies selected XletThread objects
before joining. This happens after the initial blocking-I/O request.

If active threads remain, the later sequence is:

| ROM anchor | Operation |
| --- | --- |
| `0x5C7F04` | Fire each AIE obtained from the stored forced-termination list |
| `0x5C7F3D` / `0x5C7F47` | Compare class name with exact java.util.TimerThread, then call Thread.stop only on that matching path |
| `0x5C7F6B` / `0x5C7F6E` | Load CP 121, long 50, and join each entry in the selected thread array |
| `0x5C7F7D` | Recheck ThreadGroup.activeCount |
| `0x5C7F8A` | If still active, call ThreadGroupController.setMaxPriority with the configured reduced-priority field |
| `0x5C7F91` / `0x5C7FA7` | Construct AMSError 20 and throw it |

The second join pass requests 50 ms per array entry, not one shared 50 ms
deadline for the entire pass. It follows the first loop's deadline checks.
Locks, I/O callbacks, enumeration, notification and exception handling add
other work. Therefore neither the stored 200 thread-cleanup default nor the
supplied first-loop deadline establishes the total recovery duration.

The earlier [destroy/cleanup report](ra4_ams_destroy_cleanup_contract.md)
already proves that the caller attempts explicit context finalization on
normal and selected exception paths, including after a thread-check error.
This follow-up explains why such an attempt must be distinguished from
completed thread isolation and native presentation/input recovery.

## Configuration and interpretation limits

MemoryArea.strictRTSJ loads runtime state through VM pointer offset `0x48`
and field `0xCDC`, then returns it. Native property-publication code also
uses this field to select the value for the literal jamaica.strictRTSJ.
It is not a constant-return function in this artifact.

The recovered jvm.sh and ams.properties contain no explicit strictRTSJ
selection. An aligned direct-ARM field search in VA `[0x100000,0x650000)`
found readers but
did not resolve the initializer. Indirect initialization and optional runtime
configuration remain outside that result. Its value is UNKNOWN. This finding
does not establish the field's complete semantic scope or select strict versus
non-strict ATC behavior. Generic RTSJ documentation remains contextual.

The partial ROM helper encounters unsupported quick opcode `0xD4` within
AIE.fire. Only the directly checked invocation anchor is used here; no
complete fire/defer interpretation is claimed from a guessed opcode. The
other selected inline bodies decode completely under the existing helper.

## Resident proof consequence and next boundary

The [resident proof](../docs/21_first_resident_runtime_proof.md) now separates
pending AIE, native interrupt status, I/O-request completion, deadline-based
join, escalation joins, surviving app threads and actual action exit. It must
observe total cleanup time and prove containment even if error 20 is returned
and context cleanup is attempted. A native request or timer value is not a
completion acknowledgment.

The next local boundary is the compiled/native consumer of pending AIE and
the registration/coverage of I/O callbacks used by the stock UI path. The
effective VM configuration, supplier-supported native API contract and live
shared-monitor/stock display-input recovery still require stronger evidence.
No external compute fallback is selected, no package is deployed and no
vendor payload is committed.

Fresh verification matches three artifact identities, six native method
bindings, 53 native instruction anchors, five complete inline method bodies,
19 resolved invocation anchors, two imports and three property literals.
The additional artifact hashes are jvm.sh
`9bd3c63a2c22c17f96e037102283f453afca43eb093bc1291d607a9805f829ec`
and ams.properties
`790847a3a00a62cf0886565f49d103f5a16fd20fe975fced96d3427cafd0fde0`.
No committed implementation or test changes in this checkpoint; the earlier
162-test host-suite result is historical and was not rerun.
All 124 local links in the seven changed Markdown files resolve.

Follow-up: the [native I/O and Screen wait trace](ra4_native_io_screen_wait.md)
now maps 11 direct registration sites to six callbacks, checks their different
return semantics and follows a concrete stock caller into the Screen wait.
The caller supplies a positive timeout, while the no-argument API supplies -1.
Pending-AIE delivery and completed native UI/input recovery remain open.
