# RA4 AMS destroy, timeout and container-cleanup contract

Date: 2026-09-06. Starting canonical head `51b5a781c440a5fe78797a66e5c1a72e181b0b78`.
Read-only host analysis of the existing owner-supplied image. No target execution.

## Decision

**STATIC_PROVED:** the three AMS stop errors that native AppManager can normalize
to success are **8: XLET_CAUSED_JAVA_EXCEPTION**, **12: TIMEOUT**, and
**20: XLET_DID_NOT_STOP_ALL_THREADS_ON_DESTROY**. This resolves the previously
unknown names in the [result-completion trace](ra4_xlet_result_completion.md).
A zero normalized result therefore does not certify that every app thread
terminated. D-Bus `NoReply` is a different response category and retains result
34 in that trace; it must not be conflated with AMS error 12.

**STATIC_PROVED:** AMS has explicit destroy and cleanup actions, a separate
thread-cleanup path, LWUIT/GLES cleanup calls, and a call to remove an Xlet
container from its main frame. Exception tables route inspected failures into
cleanup paths. This materially narrows the stock mechanism beyond AppManager
inventory changes.

**UNKNOWN:** completion under a hung app, native window/input consequences of
container removal, actual deadlines, and isolation from stock apps sharing AMS.
The action-with-timeout runner and central callback action implementation have
no inline Java body in the inspected ROM method records. Recovering their names
and callers does not establish the behavior of their AOT/native implementation.
No runtime gate passes and no measured resident capability fails.

## Artifact identity and reproducible boundaries

Paths are relative to ignored `analysis_ra4_18.45.01/work/`; hashes are SHA-256.
AMS anchors below are **file offsets**. AppManager anchors are ARM virtual
addresses. Do not compare them without the appropriate address conversion.

| Artifact | Path | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| AMS | `primary_iso/usr/share/MMC_IFS_EXTENSION/bin/AMS` | 11956352 | `96683b789ecf06a8575915d0b446b532e1f4ee87feb31d925cb7ba3d7d324d27` |
| AppManager | `hidden_hbc_ifs/segment_00f20000/files/bin/appManager` | 1268061 | `608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591` |
| AMS properties | `secondary_iso/usr/share/XLETS/base/kona/data/ams.properties` | 287 | `790847a3a00a62cf0886565f49d103f5a16fd20fe975fced96d3427cafd0fde0` |

Use the existing `jamaica_rom_strings` decoder for the name pool at `0x9C2071`,
25,587 literal records at `0xAB8ED0` and 28,142 member records at `0xAD1EA0`.
The 4,599 little-endian class pointers at `0xB1BC48` require subtracting
`0x100000` to obtain file offsets. Selected class constant pools contain both
global name references and local class/member references. Long constants occupy
two CP indices. Preserve field order, including Boolean fields preceding the
timeout fields; omitting them silently assigns defaults to the wrong names.

Class 359 (AMSError) spans `[0x5BC1A8,0x5BC500)`; its 26 field records begin
at `0x5BC2D0` and end at `0x5BC34F`. Class 362 (AMSProperties) spans
`[0x5BCEE8,0x5BE5B8)`. XletManager is class 420,
`[0x5C5238,0x5C6478)`, with 48 method records. Method count and sequential
record decoding establish local method ordinals; raw selector occurrences in
constant pools are not method boundaries.

## Named errors and actual producer paths

| AMS value | Field name | Field record | Integer CP record |
| ---: | --- | --- | --- |
| 8 | `XLET_CAUSED_JAVA_EXCEPTION` | `0x5BC338` | CP 55 at `0x5BC276` |
| 12 | `TIMEOUT` | `0x5BC329` | CP 59 at `0x5BC28A` |
| 20 | `XLET_DID_NOT_STOP_ALL_THREADS_ON_DESTROY` | `0x5BC342` | CP 67 at `0x5BC2B2` |

These are public/static/final integer field records with constant-value
references, not an inferred correspondence between nearby strings and numbers.
They match AppManager ignoreError comparisons at ARM `0x144EE4`, `0x144EE8`
and `0x144EF0`. Stop-only accepted normalization sets result zero and its local
success flag at `0x14B3F4` / `0x14B3F8`; the previous report retains the guards
and the separate NoReply path.

XletManager's no-argument `destroyXlet` body starts at `0x5C5CDE`. Its guarded
application callback pushes true at `0x5C5D05` and invokes CP 134 at
`0x5C5D06`: class 2389 (`javax/microedition/xlet/Xlet`), method 3,
`destroyXlet(Z)V`. The exception path pushes error 8 at `0x5C5D25`, constructs
AMSError through CP 95 at `0x5C5D3A`, and throws at `0x5C5D3D`.

XletThreadGroup class 443 method 8, `checkThreadTermination(J)V`, starts at
`0x5C7DE2`. Its late failure branch pushes 20 at `0x5C7F91`, constructs
AMSError at `0x5C7FA7` and throws at `0x5C7FAA`. This is an actual producer
of the ignored code. Its diagnostic about forceful stopping is not evidence
that all threads have stopped. This report does not claim that this failure
path skips the caller's subsequent cleanup; the caller has explicit exception
handling and finalization calls.

## Compiled defaults are separate from external configuration

AMSProperties constructor body `[0x5BD31E,0x5BD481)` assigns the following
long constants with `ldc2_w` and `putfield`. Resolve each target through its
CP class/field ordinal and the ordered field table.

| Field | Assignment starts | Compiled value | External file value |
| --- | --- | ---: | ---: |
| `initXletTimeout_` | `0x5BD33C` | 4000 | 20000 |
| `startXletTimeout_` | `0x5BD343` | 3000 | 30000 |
| `pauseXletTimeout_` | `0x5BD34A` | 3000 | 5000 |
| `destroyXletOnErrorTimeout_` | `0x5BD351` | 4000 | omitted |
| `defaultCallbackTimeout_` | `0x5BD358` | 1000 | 10000 |
| `destroyXletTimeout_` | `0x5BD35F` | 10000 | omitted |
| `destroyXletThreadsTimeout_` | `0x5BD366` | 200 | omitted |

For example, CP 22 targets class 362 field 9, `destroyXletTimeout_`, and
CP 20 supplies long 10000. CP 25 targets field 10, `destroyXletThreadsTimeout_`,
with CP 23 supplying long 200. The omission of destroy keys from the external
file therefore does not imply the absence of a distinct compiled default.
These are stored values, **not measured or established effective deadlines**.
Configuration loading, subsequent setters, caller-selected arguments and
scheduling still matter. In particular, neither 10000 nor 200 establishes a
hard bound on presentation/input recovery or AppManagerCore field `0x288`.

## Destroy actions and cleanup are distinct stages

XletManager method 19, `destroyXlet(JJLjava/lang/Long;)V`, has body
`[0x5C5B46,0x5C5BB3)`. It constructs class 433 (`XletManager$8`), passes the
first long and the priority object, and calls XletThread method 8,
`actionWithTimeout(XletAction)V`, at `0x5C5B57`.

Afterward it calls `getCleanupThread()` at `0x5C5B5B`, constructs class 434
(`XletManager$9`) with the second long, and calls the action runner at
`0x5C5B7F`. The catch-all table entry covering body offsets `[0,20)` targets
63, which repeats the cleanup-thread/action path before rethrowing. A failure
obtaining a cleanup thread has a direct `cleanupThreads(J)V` call at
`0x5C5B67`; the corresponding exceptional path calls it at `0x5C5B94`.
This establishes implemented recovery attempts, not guaranteed completion.

The cleanup action's `run()` calls XletManager `cleanup()` at `0x5C6F90`.
Its `runFinally()` calls `access$300` at `0x5C6FA8`; that wrapper calls
`cleanupThreads(J)V` at `0x5C62DE`. The action runner must still execute these
hooks; a method named runFinally alone is not proof of unconditional execution
when native code, scheduling or the VM fails.

`cleanup()` calls `cleanupGraphic()` at `0x5C5D62` and XletCallback `cleanup()`
at `0x5C5D69`. The graphics helper contains:

| Call site | Resolved target |
| --- | --- |
| `0x5C5DC8` | class 623 method 3: LWUIT `Display.deinitialize()` |
| `0x5C5DDA` | class 631 method 8: `LWUITState.destroyGLESCanvas()` |
| `0x5C5DE9` | class 631 method 14: `LWUITState.deactivate(Z)` with false |
| `0x5C5DF5` | XletManager method 3: `disposeRegisteredImages()` |

These are concrete subsystem cleanup calls with local exception handlers.
They are not, by themselves, evidence of native Screen window destruction or
input-contact release.

## Container removal has a concrete caller; completion remains open

`cleanupThreads(J)V` calls `checkThreadTermination(J)V` at `0x5C5BEE`.
It calls XletContextImpl method 11, `finalize()`, at `0x5C5BF5`, and repeats
that call at `0x5C5C00` on the catch-all path. The relevant exception table
covers body offsets `[5,17)` and targets 27. Thus a thrown thread-check error
does not simply bypass the explicit context-finalization attempt.

XletContextImpl's `finalize()` body starts at `0x5C5183`; after obtaining the
main frame and testing the container reference, it calls interface
`XletMainFrame.removeChild(XletContainer)` at `0x5C5193`. Class 418 method 3
identifies that interface signature. This is a direct invocation of the method,
not a claim about when garbage collection might invoke a Java finalizer.
The concrete main-frame implementation and its native presentation/input
effects still need tracing.

The [container/focus follow-up](ra4_xlet_container_focus_cleanup.md) now resolves
the conditional default implementation: UndecoratedXletMainFrame delegates to
AWT removal, recursive removeNotify, focus transfer and selected event cleanup.
The factory can be replaced, and these Java operations do not establish native
visibility/contact release or bounded completion under a shared UI lock hang.

The next timeout boundary is equally specific: XletThread method 8 at record
`0x5C73DF` has no inline body, as does XletCallback's central
`action(String,long,Runnable,boolean)` at `0x5C326E`. Partial parsing stops at
unsupported ROM attributes rather than inventing instruction semantics. These
boundaries remain AOT/native investigation targets; their absence from the
inline bytecode is not absence from the installed executable.

The [compiled timeout follow-up](ra4_ams_aot_timeout_runner.md) now maps the
action runner to ARM `0x1AA05C` and its no-finally helper to `0x1A8EE8`.
Native normal and selected exception paths dispatch runFinally; the helper
contains timed waits and an AMS TIMEOUT producer. Hook completion, worker
termination and bounded shared-VM recovery still require separate proof.

## Product consequence and validation

The [resident proof](../docs/21_first_resident_runtime_proof.md) must retain
raw AMS errors 8/12/20 even when stop normalization yields zero. Require
separate evidence for action completion, app-thread disposition, container
removal, native visibility/input release and usable stock foreground. Record
configured/effective timeout values separately from elapsed recovery time.
Do not treat stop-and-restart as preservation of a healthy projection session.

**Next bounded technical target:** identify the concrete XletMainFrame
`removeChild` implementation and follow its native window/focus/input effects;
then resolve the AOT action-with-timeout entry and its completion hooks.
The provider still must qualify custom package authorization and shared-VM
failure containment before any future bench trial.

Fresh host evidence checks matched three artifact identities, three named error
constants, seven constructor assignments and the four external timeout keys,
seven complete selected method tables, 21 resolved call anchors, and the
selected immediate/exception-table checks. Complete local ROM dumps and the
bounded exploratory reader remain ignored. Only original analysis/specification
text is committed; target installation, writable growth and staging are zero.

The prior callback verification also passes: two artifact identities, 102
native instructions, two tables, nine literals, four import resolutions and
14 HMI instructions with the recorded ABC identity. The unchanged full host
Python suite passes **150 tests, no skips**. All **105 local Markdown links
in seven changed documents** resolve. No target, phone, JavaScript/C99 or
provider test ran; these checks do not measure cleanup or session continuity.
