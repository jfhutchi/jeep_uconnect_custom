# RA4 Screen event-loop exit and event-release boundary

Date: 2026-09-06. Starting canonical head `9d16fe2`, clean and synchronized
with origin after fetch. Read-only host artifact analysis; no target execution.

## Decision

**STATIC_PROVED:** the stock platform-screen initializer starts a named daemon
thread. Its compiled run body checks the Boolean returned by access$800
before the native event wait. False reaches a normal return. The event
conversion/dispatch path returns to the loop, so completion of one finite
Screen wait does not itself stop that thread.

**STATIC_PROVED:** KSEventAtom.consume contains a consumed-state write followed
by a call to that class's nativeKSFreeEvent declaration. The inspected library
exports an event-free function under the different class name KSEvent, and
that function calls screen_destroy_event. No FreeEvent symbol is present in
AMS's dynamic-symbol table; the selected AOT registration for the KSEventAtom
native method has no compiled or adapter entry. These are separate facts,
not a proven runtime connection between the Java declaration and the export.

**UNKNOWN:** a supported per-app stop transition for the event loop, actual
event-free binding/invocation, completed native teardown and stock contact
recovery. This trace does not establish an event leak, its rate, or a measured
local failure. No resource, runtime or external-compute decision changes.

## Artifact identity and method binding

Uses the same two hash-verified artifacts as the
[native I/O and Screen trace](ra4_native_io_screen_wait.md): AMS, 11956352
bytes, SHA-256
`96683b789ecf06a8575915d0b446b532e1f4ee87feb31d925cb7ba3d7d324d27`,
and libKSLinked.so, 16112 bytes, SHA-256
`d6dd85dfb50e3337139dc75e2598dc0b43189740a44ab78f18ac981156ff704c`.
ARM addresses below are AMS virtual addresses unless explicitly labeled
library-relative. ROM offsets are file offsets. The selected AOT registry
preserves field and method ordinal namespaces separately.

| Class slot / method ordinal | Method | Storage | Compiled entry |
| --- | --- | --- | --- |
| 917 / 1 | GLESPlatformScreen$KSWindowInitialiser.run | 0xC6C32C | 0x2A0428 |
| 914 / 31 | GLESPlatformScreen.access$800 | 0xC67C44 | inline ROM |
| 914 / 32 | GLESPlatformScreen.access$900 | 0xC6B434 | inline ROM |
| 914 / 33 | GLESPlatformScreen.access$1000 | 0xC6A770 | inline ROM |
| 124 / 4 | KSEventAtom.nativeKSFreeEvent(J)V | 0xC686E4 | zero; adapter also zero |

Zero compiled entries do not mean a method is absent: the accessors have ROM
bodies. The native method has no inline body and its flags identify a native
declaration. Its effective runtime resolution is not established here.

## Thread creation and loop exit

GLESPlatformScreen.initKSWindowData, class 914 method 15, has a 31-byte
ROM body at 0x639068. It constructs the initializer, constructs a Thread
with the literal KSWindowInitialiserThread, calls Thread.setDaemon(true)
at 0x63907F and Thread.start at 0x639083. The references resolve to class
1329 ordinals 65 and 32. Daemon configuration is not a per-app cancellation
or join contract.

In the compiled run body, 0x2A29B4/0x2A29C4 build accessor storage
0xC67C44; it is saved at stack +8. The loop loads it at 0x2A2CD0 and calls
through it at 0x2A2CE8. The return is compared with zero at 0x2A2CF4;
0x2A2CF8 branches to 0x2A32D0 on false. That path restores VM bookkeeping
and returns at 0x2A3324. It contains no call to the native window destructor.

On true, the loop reaches KSEvent.getInstance and the timeout-taking wait
already traced in the preceding report. The selected event-conversion path
loads access$900 from 0xC6B434 and invokes it at 0x2A2E70. Its ROM body at
0x63918D resolves to GLESPlatformScreen.getNextEvent. The subsequent
access$1000 dispatch call at 0x2A2F44 resolves through its ROM body at
0x63919E to GLESPlatformScreen.dispatchEvent. The branch at 0x2A2F48
returns to 0x2A2C30 and the loop's VM-state check and predicate. This is
evidence of repeated waiting, not a complete interpretation of every event
type or exception path.

The access$800 body is five bytes at 0x63917D: the existing partial decoder
records quick operations D7 and D0 with operand 46, then ireturn. This report
does not assign an unverified quick-op operand to a particular Java field.
Separately, the named pumpEvents field (class 914 ordinal 12) is explicitly
assigned true by the constructor at ROM 0x638EE3 through CP4. setVisible
at 0x638FCC writes the different visible field, ordinal 10, through CP13.
These distinct writes do not prove that hiding an app clears the loop predicate.

All 36 declared methods of GLESPlatformScreen were enumerated. No named
stop/dispose/destroy method occurs in that list. That bounded observation
does not exclude inherited behavior, reflection, native field mutation,
optional components or other lifecycle paths.

## Event release and native binding gap

KSEventAtom.consume, class 124 method 14, has a 20-byte body at 0x59B504.
After its quick-op conditional branch, the selected path writes true to
the named consumed field at 0x59B50D, then calls CP14 at 0x59B514.
That reference resolves to class 124 method 4, nativeKSFreeEvent(J)V.
Entering consume or setting consumed cannot certify that native freeing
completed; the write precedes the native call.

The library export is exactly
Java_com_aicas_kodescreen_KSEvent_nativeKSFreeEvent, at library-relative
0x1A58, symbol size 44. It forwards the handle to screen_destroy_event at
0x1A64. A negative result reaches KSThrowNativeWindowException. The
library has no dynamic symbol named
Java_com_aicas_kodescreen_KSEventAtom_nativeKSFreeEvent. AMS's dynamic
symbol table has no name containing FreeEvent. This identifies an unresolved
class-name/binding relationship; it does not prove a runtime link error or
exclude explicit registration, another library or another release mechanism.

A bounded resolved-reference search inspected constant pools for all class
slots 0 through 4121, with no failed pool decodes. It searched field references
to (914,12) and method references to (124,14), (124,4), (127,14), (127,2).
Exactly three matching entries occur:

| Source | Resolved reference | Meaning |
| --- | --- | --- |
| class 914 CP4 | field (914,12) | pumpEvents |
| class 124 CP14 | method (124,4) | nativeKSFreeEvent |
| class 127 CP17 | method (127,2) | native ksDestroyWindow(J)V |

No direct resolved pool reference to KSEventAtom.consume or the no-argument
KSWindow.ksDestroyWindow wrapper was found in that boundary. Symbolic or
quickened references, native calls, dynamic dispatch/registration, optional
JARs and class slots beyond 4121 remain outside this negative result. It
cannot prove that neither method ever runs.

The existing whole-window destructor implementation therefore remains
separate from both normal event-loop return and the per-app AWT detachment
chain. No supported connection from app Return/stop to completed native
event/window/contact release is established by these artifacts alone.

## Resident proof consequence and verification

The [future resident proof](../docs/21_first_resident_runtime_proof.md) now
requires a supplier-supported event ownership/release contract and a supported
per-app lifecycle contract for any shared platform-screen thread. Qualify
which component owns each native event, where release completes, what causes
the relevant loop to exit or remain alive intentionally, and how factory
input remains available. Separate consumed state, loop return, app-container
removal and native destruction acknowledgments.

Next evidence target: resolve the accessor's effective field semantics and
the native event-free registration path, or obtain the corresponding exact
build contract from the legitimate SDK/provider. Neither unresolved static
binding nor finite timeout is a measured reason to switch to external compute.
Cabin USB topology and engine/authorization gates remain unchanged.

Fresh checks reran the preceding two-artifact I/O/Screen verification, then
matched 22 additional ARM anchors, four method-storage bindings, seven inline
ROM bodies, eight resolved references, the complete 4122-pool search and
the selected dynamic-symbol/export/import checks. Only original research
documentation is committed; the exploratory verifier and protected artifacts
remain ignored. No runtime or phone bench test ran. The earlier 162-test
host-suite result remains historical.
All 123 local links across the six changed Markdown files resolve; whitespace
checks pass.
