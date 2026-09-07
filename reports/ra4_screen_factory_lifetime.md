# RA4 Screen factory and remaining compiled-method boundary

Date: 2026-09-06. Starting canonical head `52c44e5`, clean and synchronized
after fetch. Local read-only artifact analysis; no target or GitHub Actions.

## Decision

**STATIC_PROVED:** all six GLESPlatformScreen methods without inline ROM
bodies have registered compiled entries. Three are graphics/event methods;
three are native wrappers whose selected direct implementations are identified
below. The event-conversion body's two inspected byte stores set and clear
the neighboring stillPressed location, not pumpEvents. The byte-store census
does not supply a supported stop writer.

**STATIC_PROVED:** GLESPlatformScreen.getInstance(Window) allocates a new
screen object and invokes its initializer. GLESGraphicsDevice.setWindow
calls that factory and stores the returned object in its screen field. The
initializer runnable retains the screen in this$0 and is passed to the
named daemon thread. Window.init calls the base GraphicsDevice.setWindow
method, and GLESGraphicsDevice supplies its matching override. The factory
name is not evidence of singleton caching.

**STATIC_PROVED conditional default-frame chain:** the cached
UndecoratedXletMainFrame constructor reaches Frame and Window initialization.
The default Xlet frame is cached even though the lower-level screen factory
allocates a new screen on each invocation. A particular Xlet's child container
must not be equated with a newly constructed top-level frame.

**STATIC_PROVED disposal-result limit:** off the event-dispatch thread,
Window.doDispose catches interruption/invocation failures, logs them, and can
still call postWindowEvent with WINDOW_CLOSED. That call or an eligible queued
closed event is not sufficient evidence that the disposal action completed.

**UNKNOWN:** the effective custom-app frame/device ownership, supported pump
termination or intentional survival, complete native teardown and restored
stock input. A fresh screen object per factory invocation does not establish
one screen thread per Xlet, one native context per app, or safe repeated use
of the factory. No thread leak, completed cleanup or measured failure is claimed.

## Artifact and the six remaining methods

Uses the same 11956352-byte AMS image, SHA-256
`96683b789ecf06a8575915d0b446b532e1f4ee87feb31d925cb7ba3d7d324d27`.
ARM addresses are virtual addresses translated through PT_LOAD; ROM positions
are file offsets. Class slot 914 method ordinals remain separate from fields.

| Ordinal / method | Compiled entry | Adapter | Selected behavior |
| --- | --- | --- | --- |
| 5 getGraphicsConfiguration | 0x297A4C | 0x114A60 | Local graphics environment -> default screen device -> default configuration |
| 11 getBitsPerPixel | 0x293FD0 | 0x1149B8 | Graphics configuration -> GLESGraphicsConfiguration.getBitsPerPixel slot |
| 13 getNextEvent | 0x2A4730 | 0x113B24 | Converts native-event information; selected press-state writes described below |
| 17 initNativeImageLib | 0x15D72C | 0x15D84C | Direct native implementation 0x66EC44 calls img_lib_attach |
| 18 nativeGetEGLSurface | 0x15D4D0 | 0x15D5F8 | Direct native implementation 0x669E24 reads handle +0x0C |
| 19 nativeGetEGLContext | 0x15D274 | 0x15D39C | Direct native implementation 0x669DEC reads handle +0x18 |

The configuration getter calls GraphicsEnvironment.getLocalGraphicsEnvironment
at 0x297AC8, then uses verified method-storage literals for
getDefaultScreenDevice and getDefaultConfiguration before calls at 0x297B10
and 0x297B58. getBitsPerPixel first uses the configuration getter, checks the
returned configuration type, and invokes the GLESGraphicsConfiguration method
slot at 0x2940E0. These selected getter paths are not teardown acknowledgments;
virtual callees and VM helpers are not exhaustively analyzed here.

The native surface/context wrappers forward their long argument at
0x15D558/0x15D2FC to direct calls at 0x15D560/0x15D304. Their non-null
implementations load the result at 0x669E4C/0x669E14 and return; null reaches
an error helper. These are reads from the supplied native handle, not Java
field offsets. initNativeImageLib calls 0x66EC44 at 0x15D7B0. That routine
allocates four bytes, initializes the storage, and calls the imported
img_lib_attach at 0x66EC80. Its successful branch returns the allocated
handle. Four bytes is not the library's total memory cost or a product
footprint measurement. Failure cleanup and indirect library effects are not
qualified by this trace. Adapter entries repeat the same native targets;
they are recorded separately from the primary compiled entries.

## Byte-store boundary

An aligned-word candidate census covered these six intervals, with exclusive
ends: 0x297A4C..0x297BB4, 0x293FD0..0x294174, 0x2A4730..0x2A61B0,
0x15D72C..0x15D84C, 0x15D4D0..0x15D5F8 and 0x15D274..0x15D39C.
Ends are the next registered compiled entry or the method's adapter. Literal
pools can decode as instructions, so matches are candidates until inspected.
Exactly two STRB-family candidates occur, both in getNextEvent:

- 0x2A5A88 stores one at receiver->next block +0x13.
- 0x2A5C4C stores zero at the same location on the inspected zero-result path.

The receiver is saved from r1 at 0x2A474C. Both store paths reload it and
follow its +0x1C block link. The
[field-layout reconstruction](ra4_screen_quick_field_semantics.md) maps this
byte to stillPressed, logical location 47. pumpEvents is the adjacent byte
at logical location 46 / next block +0x12. A press-state reset is therefore
not a pump-stop transition. The second store receives zero from the result
tested at 0x2A5A38-0x2A5A40; its branch reaches the store without changing
that value.

This census excludes transitive calls, computed-address or wider stores,
reflection, dynamic components and other classes. It does not establish
universal absence of a stop writer. Together with the prior 30-inline-body
check, it narrows the declared class's visible implementation without
converting a bounded negative into proof of immutability.

## Factory, device and runnable ownership

The 111-byte getInstance(Window) body starts at ROM 0x638FE3. It executes
new GLESPlatformScreen, passes the Window to its constructor at 0x638FE8,
and invokes initKSWindowData at 0x638FED. Later waiting, validation and error
paths do not turn that initial allocation into a cached-object lookup. The
constructor stores javaWindow and initializes pumpEvents as previously traced.

GLESGraphicsDevice.setWindow, class 911 method 5, has nine bytes at
0x6388E0. It passes its Window argument to that factory at 0x6388E2, then
stores the returned reference to the named screen field at 0x6388E5.
KSWindowInitialiser's bridge constructor at 0x639547 calls its primary
constructor; the latter stores the screen reference to this$0 at 0x63952D.
The previously verified initKSWindowData body constructs the runnable,
constructs KSWindowInitialiserThread with it, sets daemon true and starts it.

A targeted resolved-reference census across class pools 0..4121 finds one
reference to (914,14): class 911 CP8, the factory call above. It finds no
resolved reference to the override (911,5), but does find one to the base
method (947,10): class 988 CP21. Window.init(GraphicsConfiguration), class
988 method 1, is a 97-byte body at 0x644411. At 0x644454 it loads the device,
then this Window, and at 0x644456 invokes that base setWindow method virtually.
GLESGraphicsDevice's superclass is GraphicsDevice, and both method declarations
have the same name and (Window)V descriptor. This establishes the base-call
site and matching override relationship. The effective runtime receiver class,
invocation count and app-specific ownership remain unobserved; a direct
reference to the override was not required to find this caller. Symbolic
references, compiled dispatch, reflection and other components remain outside
the resolved-reference census.

For the [future resident proof](../docs/21_first_resident_runtime_proof.md),
identify whether the approved Xlet uses an existing shared frame/device or
a supported separate one. Map that ownership to screen creation, daemon
lifetime and native resources. Do not assume one per app, destroy a shared
context as Return, or invoke setWindow repeatedly to manufacture app isolation.
Existing per-app container removal remains distinct from frame/device teardown.

## Follow-up: cached frame construction and whole-window disposal

Starting head `1d38c28`; follow-up verified 2026-09-07. The
[default-frame/container trace](ra4_xlet_container_focus_cleanup.md) already
establishes the conditional default factory and per-app removeChild path.
The startup script and initializer hashes were rechecked unchanged for this
follow-up; effective live factory selection remains unobserved.

The factory at ROM 0x5C262C checks its cached field, constructs the default
frame only when null, stores it at 0x5C263C and returns it. The creation path
now connects to the previously traced Screen factory through these constructor
calls (all positions in this section are ROM file offsets):

| Caller | Call position | Target |
| --- | --- | --- |
| Default frame factory | 0x5C2639 | UndecoratedXletMainFrame bridge constructor |
| Bridge constructor | 0x5C2592 | Primary UndecoratedXletMainFrame constructor |
| Primary constructor | 0x5C24F9 | Frame() |
| Frame() | 0x636809 | Frame(String) |
| Frame(String) | 0x636835 | Frame(String, GraphicsConfiguration) |
| Frame(String, GraphicsConfiguration) | 0x636847 | Window(GraphicsConfiguration) |
| Window(GraphicsConfiguration) | 0x644403 | Window.init(GraphicsConfiguration) |
| Window.init | 0x644456 | Virtual GraphicsDevice.setWindow(Window) |

Frame(String) obtains the default screen device/configuration through symbolic
member references whose class-CP indices and global member selectors were
verified separately. They are not resolved class-slot/ordinal pairs. The
selected device's effective runtime class remains an independent condition
for entering GLESGraphicsDevice's screen-creating override. The constructor
chain does not prove that every app constructs a frame or owns native resources.

Window.dispose at 0x64461C calls doDispose. The latter constructs Window$1,
checks EventQueue.isDispatchThread, and either runs the action directly at
0x64464A or calls EventQueue.invokeAndWait at 0x644651. Its exception table
covers the off-dispatch invocation, with handlers for InterruptedException
and InvocationTargetException at 0x644657 and 0x644667. Both log diagnostics
and reach the shared tail at 0x644674. The tail supplies event ID 202 at
0x644675 and calls postWindowEvent at 0x644678. The recovered WindowEvent
constant identifies 202 as WINDOW_CLOSED. A direct action exception on the
event-dispatch branch is outside those two catch ranges; this report does
not claim all disposal failures reach that tail.

postWindowEvent itself checks listener/event-mask eligibility before creating
and posting an event at 0x6445F5-0x644603. Reaching its call site is therefore
not proof that an event was queued or delivered. Even an eligible WINDOW_CLOSED
event after an off-dispatch failure cannot certify completed teardown.

EventQueue.invokeAndWait posts an InvocationEvent at 0x6352CD, calls the
no-argument Object.wait at 0x6352D1, and then inspects getThrowable, wrapping a
non-null result in InvocationTargetException. The inspected body supplies no
wait deadline. **INFERRED consequence of the selected interrupted-wait path:**
the caller may return after logging while queued disposal work has not yet
finished. No event cancellation occurs in the inspected Window catch body.
Actual scheduling, late execution and cleanup duration remain unmeasured.

Window$1.run has 106 bytes at 0x644E58. It conditionally clears the device's
full-screen Window association, requests setVisible(false), sets the named
beforeFirstShow flag, calls Container.removeNotify, disposes a non-null input
context under its lock and clears that reference, then clears the current
focus-cycle root. These are whole-window Java cleanup actions. The inspected
body contains no explicit pumpEvents assignment or native Screen destruction
call; transitive virtual/native effects are not excluded. The earlier
per-app removeChild path does not invoke this whole-window disposal sequence.

For an approved package, qualify the effective shared-frame factory and
ownership boundary. Do not dispose the cached shared frame as an app Return
or child-removal shortcut. If the provider's supported lifecycle uses whole
window disposal for a separately owned frame, retain raw interruption and
action errors, observe actual action completion and possible late work, then
independently verify native release and usable stock focus/contacts. A closed
event, request return and native recovery are separate observations.

Fresh follow-up checks reran the preceding artifact chain, rechecked the
startup-script and initializer hashes, and verified 15 ROM bodies, 22 resolved
call anchors, three symbolic references, two frame superclass links, both
disposal exception handlers and WINDOW_CLOSED's value. No target execution,
new runtime acceptance or measured local failure follows.
All 83 local links across four changed Markdown files resolve; whitespace
checks pass. The workflow remains the verified manual-only blob, and the
owner's September no-Actions restriction remains in force.

## Initial checkpoint verification

Fresh local verification reran the previous artifact chain and checked 46 new
ARM anchors, six method/adapter bindings, six storage literals, three direct
native targets, two imports, both byte-store candidates, six ROM bodies,
seven resolved references, the device superclass/override relationship and
the 4122-pool factory-reference census. Protected
artifacts and exploratory scripts remain ignored. No executable product code
changed; the earlier 162-test host-suite result remains historical.
All 120 local links across five changed Markdown files resolve; whitespace
checks pass. The remote workflow retains the verified manual-only blob.

The follow-up above connects the default frame constructor and narrows whole
window disposal. Its remaining native-release/stock-input completion and
effective package ownership still require an exact-build supported contract.
USB routing, transport, authorization, engine availability and resource gates
remain unchanged; external compute is not selected.
