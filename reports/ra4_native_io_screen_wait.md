# RA4 native I/O callbacks and Screen event wait

Date: 2026-09-06. Starting canonical head `a75f790`. Host-only static
research; no radio, vehicle or phone execution.

## Decision

**STATIC_PROVED:** the recovered AMS blocking-I/O registration path has
11 direct ARM call sites, resolving to six callback bodies. Four request a
thread signal, one posts a semaphore and one requests socket shutdown.
Their return values have different meanings; callback success does not
uniformly acknowledge completion of the underlying operation.

**STATIC_PROVED:** the stock GLESPlatformScreen$KSWindowInitialiser.run path
passes the positive long value 2000000000 to KSEvent.ksWaitEvent(long).
That value is forwarded through the AMS native adapter and libKSLinked.so
to screen_get_event. This concrete caller uses a finite timeout argument;
the separate no-argument Java wrapper supplies -1. Neither establishes a
total stock UI recovery deadline.

**STATIC_PROVED:** the linked native event-post implementation throws an
unsupported-operation exception. Its window-destruction implementation calls
screen_destroy_window and screen_destroy_context, then frees its native
handle. This is a different operation from detaching an app's AWT child.

**UNKNOWN:** cancellation coverage through Screen internals, effective event
loop termination, native contact cancellation, successful destruction and
per-app recovery while shared AMS remains alive. No live capability gate
passes or fails; the resident candidate and legitimate SDK/package gates
remain unchanged.

## Artifacts and address convention

| Artifact under recovered primary_iso/usr/share/MMC_IFS_EXTENSION | Bytes | SHA-256 |
| --- | ---: | --- |
| bin/AMS | 11956352 | 96683b789ecf06a8575915d0b446b532e1f4ee87feb31d925cb7ba3d7d324d27 |
| lib/libKSLinked.so | 16112 | d6dd85dfb50e3337139dc75e2598dc0b43189740a44ab78f18ac981156ff704c |

AMS ARM addresses are virtual addresses translated through PT_LOAD. ROM
anchors are file offsets. Library addresses are that ELF's relative virtual
addresses, not live process addresses. Native Java method identities use
the [AOT registry reader](../analysis_tools/jamaica_aot_registry.py); library
entry identities use exported dynamic symbols. Nearby function names are
not assigned to unnamed native helpers by proximity.

AMS declares libKSLinked.so as a dependency; the latter declares libscreen.so.1
and libc.so.3. These are static link relationships, not observed live loading.

## Registration and callback lifecycle

The [preceding cleanup trace](ra4_ams_interrupt_request_cleanup.md) reaches
the callback consumer at AMS 0x611D74. The registration wrapper 0x612AB0
branches to 0x612A30. Under the VM mutex, 0x612A54 reads thread state +0x1DC.
Only when zero do 0x612A60 and 0x612A6C store the callback at +0x1D0 and
payload at +0x1D4; +0x1D8 is cleared. The normal registration result is one
for that branch and zero when interruption was already requested.

Teardown at 0x6128F0 clears payload and callback (0x61291C/0x612920),
conditionally signals a waiter, clears +0x1D8 and returns a result derived
from the saved request state. It does not clear +0x1DC in this body. Wrapper
0x6129E4 uses the BlockingIoInterruptedError class literal on the failure
path. Registration, callback request and teardown are distinct observations.

The aligned executable-load direct BL/BLX search to 0x612AB0 produces:

| Registration call sites | Callback | Mechanism |
| --- | --- | --- |
| 0x5C981C, 0x5C98A4, 0x5C9988 | 0x5C987C | Signal request |
| 0x5C9A3C, 0x5C9B18, 0x5C9BC0 | 0x5C9A9C | Signal request |
| 0x61F8A0 | 0x61F8E0 | Semaphore post |
| 0x63F768 | 0x63FDA8 | Signal request |
| 0x63FF20 | 0x63FFFC | Signal request |
| 0x64CB2C, 0x64CED8 | 0x64CA58 | Socket shutdown and conditional write |

Each callback pointer is verified through the call site's PC-relative r1
literal load. This census does not cover indirect registrations or arbitrary
external-library internals and is not a whole-program cancellation proof.

The four signal callbacks set their second argument's output word to one,
then reach 0x5CA978 and 0x5CAC58. The latter calls pthread_kill at 0x5CAC6C
with signal 0x35. Setup helper 0x5CAA10 supplies the one-instruction return
handler at 0x5CA974 to the sigaction wrapper, whose import call is 0x5E4A28.
This is evidence for signal-based interruption, not a terminating kill.
QNX's matching-era [pthread_kill reference](https://www.qnx.com/developers/docs/6.5.0SP1.update/com.qnx.doc.neutrino_lib_ref/p/pthread_kill.html)
describes delivery to a thread in the process; successful delivery does not
itself establish completion of a blocked operation.

The semaphore callback calls sem_post at 0x61F8EC and returns one at
0x61F8F0 without checking that call's result. Its caller registers before
sem_wait at 0x61F8B0 and reaches teardown afterward.

The socket callback calls helpers 0x649F28 and 0x649F10 from 0x64CA7C and
0x64CA84. They pass numeric modes zero and one to the shutdown import.
Both results are discarded. If payload +0x0C is zero, the callback returns
one; otherwise its result follows a one-byte write to payload +0x14.
The [QNX 6.5 shutdown reference](https://www.qnx.com/developers/docs/6.5.0SP1.update/com.qnx.doc.neutrino_lib_ref/s/shutdown.html)
describes disabling socket directions and reports errors separately.
No close call is established by these two shutdown calls, and no successful
shutdown acknowledgment can be inferred from the callback's Boolean alone.

## Concrete stock Screen wait caller

| Class slot / method ordinal | Method | Compiled entry | Method storage |
| --- | --- | --- | --- |
| 917 / 1 | GLESPlatformScreen$KSWindowInitialiser.run()V | 0x2A0428 | 0xC6C32C |
| 123 / 6 | KSEvent.ksWaitEvent(J)KSEventAtom | 0x18C6D4 | 0xC6C700 |
| 123 / 0 | KSEvent.nativeKSWaitEvent(JJ)J | 0x12F580 | 0xC69264 |

Class 917 CP79 resolves to class 123 method 6; CP77 is long 2000000000.
In the compiled run body, 0x2A29A4/0x2A29B0 build storage address 0xC6C700;
0x2A29D8 preserves it in r8. At 0x2A2D5C the method metadata is loaded for
virtual dispatch. Both selected dispatch-resolution branches converge on
the call at 0x2A2A28. MOVW/MOVT at 0x2A29C0/0x2A29D0 form 0x77359400
in sb; fp is initialized to zero. At 0x2A2A10 and 0x2A2A1C, r3:r2 receives
the long value 0:2000000000. This verifies the actual call argument, beyond
the presence of a constant in the pool.

KSEvent.ksWaitEvent saves the input long at 0x18C6F0, copies it to outgoing
stack arguments at 0x18C77C/0x18C780, and invokes nativeKSWaitEvent through
storage 0xC69264 at 0x18C790. The native adapter copies those arguments at
0x12F614/0x12F618 and calls the imported nativeKSWaitEvent at 0x12F620.
Its VM state transitions before and after the call do not by themselves
prove cancellation inside the external call.

The library export Java_com_aicas_kodescreen_KSEvent_nativeKSWaitEvent
starts at 0x1AFC (symbol size 96). It creates an event at 0x1B0C, retrieves
the unchanged long argument at 0x1B24 and calls screen_get_event at 0x1B30
with the stored context and event. The selected bridge contains no direct
call to the AMS I/O registration wrapper. That bounded absence does not
rule out lower-level QNX interruption mechanisms.

The no-argument method, class 123 ordinal 7, has an eight-byte ROM body at
file 0x59B307: CP12 is long -1 and invocation 0x59B30B resolves to ordinal 6.
It must not be substituted for the positive timeout in the compiled stock
caller. QNX's 2014 [Multimedia Renderer guide, page 31](https://www.qnx.com/download/download/26196/Multimedia_Renderer.pdf)
uses -1 for waiting until an event arrives. The later [QNX 7.1 Screen reference](https://www.qnx.com/developers/docs/7.1/com.qnx.doc.screen/topic/screen_get_event.html)
specifies nanoseconds, under which 2000000000 is two seconds. That unit
interpretation is API context, not a measured RA4 timeout or exact-build
conformance proof. Even a functioning per-call timeout does not bound event
processing, repeat waits, shared locks, scheduling or completed UI recovery.

## Posting and destruction are separate boundaries

The linked nativeKSPostEvent export at 0x1A84 (size 24) calls
KSThrowUnsupportedOperationException at 0x1A8C. Java ksPostEvent also has an
inline throw body at file 0x59B358. These methods supply no proven supported
wake-up route for the event wait.

The linked KSWindow.ksDestroyWindow export at 0x1850 (size 120) calls
screen_destroy_window at 0x1870, screen_destroy_context at 0x1898 and tails
to free at 0x18C4. Error paths invoke the native-window exception helper.
The create-window export constructs the paired context/window handle.
This does not prove that destroying an app container invokes this native
destructor, that destruction returns successfully, or that active contacts
are canceled. Do not treat whole-context destruction as a supported Return
action for one app in the shared VM.

## Consequence and verification

The [future resident proof](../docs/21_first_resident_runtime_proof.md) must
identify which native operations are covered by the supported cancellation
contract and separately observe actual return, event-loop exit, app-view
detachment and restored stock input. Callback Booleans, the finite wait
argument and native destructor entry are insufficient substitutes.

Next local boundary: the stock event loop's termination predicate and native
event ownership/release path, joined to shared platform-screen teardown.
Pending-AIE delivery, effective strictRTSJ configuration and supplier-supported
native recovery remain unresolved. USB topology, transport and engine/provider
gates are unchanged; no external-compute fallback is selected.

Fresh artifact checks cover both identities, the 11 registrations and six
callback mappings, selected native instructions/imports, the three AOT
bindings, exported Screen bridge identities and the selected ROM references.
No committed executable code or tests change. The earlier 162 host tests
remain historical; this checkpoint uses fresh artifact and document checks.
The check matched 74 ARM anchors, 13 imports, three AOT bindings, three
library exports, two inline ROM bodies and four ROM references. All 121
local links across the six changed Markdown files resolve.
