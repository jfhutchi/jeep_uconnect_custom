# RA4 compiled AMS timeout runner and finally dispatch

Date: 2026-09-06. Starting canonical head `61fb2b23be9e00dc9a0f0c6b277100e60a6ae3ca`.
Read-only host analysis. No target execution or deployment.

## Decision

**STATIC_PROVED:** the recovered registration table maps XletThread's
`actionWithTimeout` to ARM entry `0x1AA05C` and its
`actionWithTimeoutNoFinally` helper to `0x1A8EE8`. The absence of inline Java
bytecode is no longer a lookup blocker for these methods.

**STATIC_PROVED:** actionWithTimeout calls the no-finally helper with false,
then dispatches the action's `runFinally()` hook through its virtual method
slot. A traced exception-dispatch path also invokes that hook. The no-finally
helper has an action-state/timed-wait loop and constructs AMS error 12 on its
selected failure path. These are implemented native paths, not timer-name
inferences.

**UNKNOWN:** hard completion deadlines, action/thread termination, delivery of
native interruption, and recovery if a finally hook or shared AWT lock blocks.
The hook call is synchronous within this wrapper; the normal sequence does not
resubmit the hook to the no-finally runner. A timed wait for an action and a
completed finally hook remain distinct evidence. No runtime gate passes and
no measured resident capability fails.

## Identity and segment-aware address translation

Artifact: ignored
`analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/AMS`.
Size **11956352**; SHA-256
`96683b789ecf06a8575915d0b446b532e1f4ee87feb31d925cb7ba3d7d324d27`.

The two PT_LOAD records require different translations:

| Segment | File offset | Virtual address | File-backed bytes | Memory bytes | Flags |
| --- | --- | --- | --- | --- | --- |
| Code / ROM | `0x0` | `0x100000` | `0xB1B4F8` | `0xB1B4F8` | RX |
| Writable data / BSS | `0xB1B4F8` | `0xC1C4F8` | `0x49E1C` | `0x54F74` | RW |

The `+0x100000` conversion used for earlier ROM anchors does **not** apply
to writable registration records: that segment's difference is `0x101000`.
Use PT_LOAD translation for every pointer. Storage references in BSS are
addresses, not initialized objects that can be read from the file.

The explicitly selected registry begins at **VA `0xC21424`, file `0xB20424`**
and contains 1,138 24-byte class records. Their arrays contain **6,668**
32-byte member records: **6,292 methods** and **376 fields**. Of the method
records, 4,102 have nonzero adapter/function pairs. These are counts of the
selected table, not all methods/classes in the ROM or optional packages.

Each class record contains flags, storage address, a zero reserved word,
class slot, member-array VA and count. Each member contains kind, storage
address, two zero reserved words, ordinal, adapter VA, function VA and a final
zero reserved word. Kind 1 addresses methods; kind 2 addresses fields. Fields
and methods have separate ordinal namespaces. For example, class 71 has both
a method and field record numbered 1; treating them as duplicate methods
misreads the table. Null function pairs are preserved, not treated as missing
runtime functionality.

## Bound method entries

Join the member's class slot and **method** ordinal to the independently
decoded ROM method table. Do not attach names to a code pointer from proximity.

| Class / method | Member record file offset | Adapter VA | Function VA |
| --- | --- | --- | --- |
| 439 / 8, XletThread.actionWithTimeout(XletAction)V | `0xB320C4` | `0x114B3C` | `0x1AA05C` |
| 439 / 6, actionWithTimeoutNoFinally(XletAction,boolean)V | `0xB32084` | `0x1134B8` | `0x1A8EE8` |
| 439 / 4, XletThread.run()V | `0xB32044` | `0x1146E4` | `0x1A60A8` |
| 401 / 5, XletCallback.action(String,long,Runnable,boolean)V | `0xB31C64` | `0x112414` | `0x1B7DD8` |

The XletThread class registration is at file `0xB20B44`, with 11 member
records at VA `0xC32FC4`. The XletCallback registration at file `0xB20A6C`
has five member records at VA `0xC32C04`. Adapter functions can be shared
between methods; the distinct function pointer is necessary for body analysis.

## Normal and exceptional finally calls

ARM addresses in this section are **virtual addresses**. The wrapper calls
imported `_setjmp` at `0x1AA0E8`; a nonzero return selects exception dispatch
at `0x1AA53C`. Its local phase word is at stack offset `0x130`.

The normal sequence sets phase 1 at `0x1AA1C8` / `0x1AA1CC`, supplies false
in r3 at `0x1AA204`, and calls the no-finally helper at `0x1AA218`. On return
it sets phase 3, loads method-storage address **`0xC70684`** at
`0x1AA234` / `0x1AA238`, obtains the action's virtual slot and calls through
it at `0x1AA2A4`. The registry binds that storage address to class 399 method
4, **XletAction.runFinally()V**. This is a synchronous virtual hook call.

The exception dispatch subtracts one from the phase, bounds-checks it against
5, and loads a destination from the six-word table at `0x1AA568`:

| Phase | Destination |
| ---: | --- |
| 1 | `0x1AACF8` |
| 2 | `0x1AAE00` |
| 3 | `0x1AAE54` |
| 4 | `0x1AA854` |
| 5 | `0x1AAC98` |
| 6 | `0x1AACC4` |

Phase 1 covers the no-finally helper call. Its handler saves the pending
exception object, reaches `0x1AAD40`, sets phase 3, and resolves the same
`0xC70684` method slot at `0x1AAD68` / `0x1AAD6C`. The hook call occurs at
`0x1AADD8`. The subsequent path passes the saved exception to runtime helper
`0x62FCF0` at `0x1AADFC`. These instructions establish cleanup dispatch during
the traced exception flow; they do not guarantee the hook returns or that
every VM failure can enter this handler. The six table words are data, not
ARM instructions.

The [destroy/cleanup trace](ra4_ams_destroy_cleanup_contract.md) already binds
the cleanup action's runFinally to cleanupThreads, which attempts context
finalization and container removal. This native finding closes the previously
unresolved wrapper-to-hook link. The [AWT focus trace](ra4_xlet_container_focus_cleanup.md)
still identifies shared UI-lock and native input/visibility boundaries.

## Action wait and AMS timeout error producer

The no-finally helper calls XletThread.addAction at `0x1A91E4`. Its Boolean
result and the helper's supplied mode select whether processing reaches its
wait path. Method-storage references identify action `isDone()` at
`0xC6F59C` and thread `functional()` at `0xC6FA10`. The loop tests those
states before waiting; either completed action or nonfunctional thread can
leave that loop. Exiting a wait is not synonymous with successful action work.

The helper reads `System.nativeCurrentTimeMillis()` at `0x1A99BC`, adds a
computed interval, and later recomputes remaining time. It calls
`com.aicas.jamaica.lang.Wait.wait(Object,long)` at `0x1A9B84` and
`0x1A9C94`, followed by clock reads at `0x1A9B8C` / `0x1A9C9C`.
The method registry independently resolves those callee bodies to `0x187C14`
and `0x61D240`. This is wall-clock-based waiting in the compiled implementation;
its effective schedule, delay and clock behavior are not measured here.

After the post-wait action-state check, the selected failure path calls the
action's done hook and constructs an error. At `0x1A9728` it passes integer
**12**, then calls the constructor via the descriptor loaded through literal
`0x1A9F10` at `0x1A9744`. That literal contains method-storage address
`0xC6D4BC`, mapped to AMSError's `(int,String)` constructor. The previously
verified AMSError constants identify 12 as TIMEOUT. The path stores the error
reference at `0x1A976C`. This is a concrete producer of the timeout code that
AppManager can normalize during stop; it is not a captured live timeout.

## Original reader, verification and remaining work

The new [registry reader](../analysis_tools/jamaica_aot_registry.py) accepts
an explicit VA/count boundary and optional class-slot filters. It uses the
existing ELF32 segment reader, validates reserved words, member kinds,
kind/ordinal uniqueness, file backing, executable function destinations and
adapter/function pairing, and preserves fields and null entries. It reports
metadata and never executes the image or reads a live BSS object. It does not
discover tables automatically or resolve Java names by itself.

The [synthetic tests](../analysis_tools/tests/test_jamaica_aot_registry.py)
cover unequal segment translations, BSS/file confusion, field/method ordinal
overlap, malformed records and explicit CLI failure. They contain no firmware.

All 162 host Python tests pass without skips, including 12 tests for this
reader. The actual artifact CLI reproduces the table counts. All 120 local
links across the eight changed Markdown files resolve. This host-only tool
adds no target footprint; no radio/vehicle/phone execution or vendor-payload
commit was performed.

Fresh artifact checks match the selected table counts, four named native
method bindings, 47 ARM instruction anchors, all six exception-table entries,
two descriptor literals and the `_setjmp` import. The next bounded target is
the queued execution body XletThread.run (`0x1A60A8`) and its timed-action /
interruption consumer: determine whether the worker is terminated or merely
reported done, and how it interacts with a blocked finally hook. Runtime
shared-VM isolation, native input cancellation and usable stock restoration
remain required before any separately authorized resident trial. No external
compute fallback is selected on the basis of this static trace.

Follow-up: the [queued worker and interruption trace](ra4_ams_worker_interruption.md)
now follows TimedFromPool through timer start, AIE run/interruptAction dispatch
and normal worker reuse. It proves that both the worker and caller fallback
can set the same done flag, and that two distinct paths construct TIMEOUT.
Actual action exit, late work and native recovery remain separately unproved.
