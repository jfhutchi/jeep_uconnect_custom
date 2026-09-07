# RA4 Xlet container removal and Java focus cleanup

Date: 2026-09-06. Starting canonical head `a6580233f7967d67d7c2b24f50b511c1b390317d`.
Owner-supplied artifacts inspected read-only on the host. No target execution.

## Decision

**STATIC_PROVED conditional implementation:** AMS's default main-frame factory
creates `UndecoratedXletMainFrame`. Its `removeChild(XletContainer)` delegates
to AWT `Container.remove(Component)`. For an attached child of a displayable
parent, removal invokes the child's `removeNotify`, then clears its parent
reference and removes it from the parent's component list.

**STATIC_PROVED Java cleanup:** XletContainer inherits Container's recursive
removeNotify. That path attempts focus transfer, disposes its lightweight
dispatcher, and calls Component's removeNotify. Component clears recorded focus
ownership, conditionally notifies the input context, removes selected queued
events and calls the keyboard focus manager's `discardKeyEvents` method.

**HIGH intended default frame:** the shipped initializer has no direct call to
the frame-factory setter. However AMS exposes that setter and honors an existing
factory. The static default is not proof of the live factory instance, nor a
universal claim about every optional extension or reflective call.

**UNKNOWN:** completion while an app or shared AWT lock is hung; delivery and
effect of focus transfer; native touch/contact cancellation; shared Screen-window
visibility; restoration of stock foreground. These Java mechanisms narrow the
cleanup contract but do not close the fail-open gate.

## Artifact and address boundaries

Paths are relative to ignored `analysis_ra4_18.45.01/work/`. All AMS addresses
in this report are **file offsets**, not ARM virtual addresses. Hashes are SHA-256.

| Artifact | Path | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| AMS | `primary_iso/usr/share/MMC_IFS_EXTENSION/bin/AMS` | 11956352 | `96683b789ecf06a8575915d0b446b532e1f4ee87feb31d925cb7ba3d7d324d27` |
| Startup script | `primary_iso/usr/share/MMC_IFS_EXTENSION/bin/jvm.sh` | 2795 | `9bd3c63a2c22c17f96e037102283f453afca43eb093bc1291d607a9805f829ec` |
| Initializer | `secondary_iso/usr/share/XLETS/base/kona/extension/ams_initializer.jar` | 21917 | `b40c69ff6cfd3e31e097c5ae33e71f1a314ce8aee2e3a734589f3025a98e959c` |

The startup script selects `ams_initializer.jar` on the AMS command line and
exports native window ID AMS with initial visibility false. Its 640x480
environment is configuration evidence, not a measured app viewport. The
default Java frame's class initializer separately uses width/height property
fallbacks 480/240; their effective override relationship is not resolved here.
Do not substitute either fallback for the product's required 640x480 area.

## Factory selection before container removal

AMSController constructor invokes the supplied initializer before calling
`createSharedMainFrame()` at `0x5BAB06`. That method's body at `0x5BAB92`
checks static `xletMainFrameFactory` (class 354 field 18). Only when it is
null does the method select `UndecoratedXletMainFrame.factory`, then call
`XletMainFrameFactory.createXletMainFrame()` at `0x5BABA2` and store
`sharedMainFrame` (field 19).

Class 393 (`UndecoratedXletMainFrame`) implements XletMainFrame; its factory
field is initialized with class 394 at `0x5C25BF` / `0x5C25C2`. Class 394's
factory body starts at `0x5C262C` and lazily constructs/caches class 393.
XletContextImpl gets the controller's shared frame at `0x5C4F23`; its explicit
finalizer calls the frame's removeChild at `0x5C5193`, as traced in the
[destroy/cleanup report](ra4_ams_destroy_cleanup_contract.md).

The setter `AMSController.setXletMainFrameFactory` remains implemented at
record `0x5BABAD`. A read-only inspection of all **19 class files and 517 JVM
invocation instructions** in the exact initializer JAR found no direct call to
that setter. A bounded scan of successfully decoded AMS ROM class slots
0 through 4121 likewise found no direct resolved CP reference to class 354
method 2. Neither boundary covers runtime reflection or uninspected optional
JARs. The remaining pointer-table entries were not successfully decoded by the
exploratory CP reader and are excluded from the negative result.

## AWT detachment and recursive notification

| Stage | Anchor | Behavior |
| --- | --- | --- |
| Default frame removes child | `0x5C2574` | Class 393 method 3 calls class 868 method 21, `Container.remove(Component)` |
| Tree lock | `0x630897` / `0x63089C` | Obtain the shared AWT tree lock and enter its monitor |
| Attached-child check | `0x6308A2` / `0x6308B1` | Require matching parent and nonnegative child-list index before indexed removal |
| Indexed removal | `0x6308B6` | Call `Container.remove(int)` |
| Displayable-parent branch | `0x6307F9` / `0x6307FC` | Test parent isDisplayable; false skips child removeNotify |
| Child notification | `0x630800` | Virtual call to Component.removeNotify, dispatching through the child's override |
| Detach parent reference | `0x630814` through `0x630816` | Assign null to the child's Component.parent field |
| Remove list entry | `0x63081E` | Remove the indexed component; subsequent processing invalidates and may dispatch a container event |

XletContainer class 416 extends AWT Container and declares only four methods;
it has no removeNotify override. Container method 65 therefore supplies this
step for an ordinary XletContainer. Its body starts at `0x6316F9`, holds the
tree lock and visits child components in reverse order. At `0x631724` it
temporarily disables each child's automatic focus transfer on disposal, calls
removeNotify at `0x631728`, then reenables transfer at `0x63172D`.

For the container itself, the eligible focus branch attempts forward transfer
at `0x631746`, then backward transfer if the forward attempt returns false at
`0x63174E`. A non-null lightweight dispatcher receives dispose at `0x63175D`,
and the reference is cleared. Finally it explicitly calls Component.removeNotify
at `0x631766`. The dispatcher dispose body at `0x640A2E` clears its Java
`mouseEventTarget` field; that assignment is not a native touch-up/cancel event.

These are ordinary monitor-based operations, without a deadline enforced in
the inspected removal bodies. A cleanup call blocked on the tree lock cannot
be treated as a completed recovery merely because it was invoked. This is an
unmeasured possibility to qualify, not evidence of an observed radio deadlock.

## Focus and event cleanup have specific limits

Component method 184, removeNotify, starts at `0x62EE2D`:

1. Clear the most-recent focus owner at `0x62EE2E`. If this component is the
   permanent focus owner, set the permanent focus owner to null at `0x62EE3F`.
2. Under the tree lock, conditionally attempt transferFocus(true) at
   `0x62EE59` when the component owns focus and auto-transfer is enabled.
3. If the input-method event-mask bit is set and an input context exists,
   call `InputContext.removeNotify(Component)` at `0x62EE75`.
4. Call `EventQueue.removeSourceEvents(component, false)` at `0x62EE89`, then
   the current keyboard focus manager's `discardKeyEvents(Component)` at
   `0x62EE90`; clear the component's add-notify completion flag.

The false argument is material. EventQueue method 25's body at `0x63514A`
matches the event source, but its false branch preserves **SequencedEvent,
SentEvent, FocusEvent, WindowEvent, KeyEvent and InputMethodEvent** instances.
It removes other matching queued events through its linked-list update path.
Thus this call is not an unconditional flush of every queued event. The separate
discardKeyEvents call belongs to the focus-manager abstraction; this report
does not conflate its buffers with the EventQueue or native touch state.

The symbolic CP form matters here. Component CP 377 at `0x62D1D7` contains
class-CP index 517 and global member selector 8647, rather than a resolved
class-slot/method-ordinal pair. CP 517 names class 962, KeyboardFocusManager;
selector 8647 names `discardKeyEvents(Component)V`. Ignoring that distinction
would incorrectly attribute the call to unrelated class slot 517. For the
other reported direct references, the class word's high bit selects the
resolved class-slot/local-member form. Unsupported metadata must remain a
boundary rather than a fabricated call target.

No explicit call to hide/dispose the shared main frame or to request stock
foreground appears in the inspected default removeChild, Container removal and
Component removeNotify bodies. This is a bounded observation about those bodies,
not a claim that their virtual callees have no platform effects. The separate
[LayerManager/native visibility route](ra4_display_owner_reclaim.md) still needs
its own completion evidence.

## Acceptance consequence and next target

The [resident proof](../docs/21_first_resident_runtime_proof.md) must identify
the effective main-frame implementation, observe actual child detachment and
Java focus cleanup, and then independently verify native visibility, contact
release and usable stock controls. Shared-AMS failure containment must account
for both app lifecycle calls and shared UI locks. Do not stop or dispose the
shared stock frame to substitute for an app-specific recovery mechanism.

The next bounded target is the AOT/native `XletThread.actionWithTimeout`
implementation and its timeout/finally completion hooks. The Java removal route
is now concrete; further Java method names alone cannot prove a deadline or
recover a stalled shared VM. The supplier-supported package, engine and
isolation contracts remain external prerequisites. No local capability gate
has been measured to fail, so external compute is not selected.

Fresh verification matched three artifact identities, ten complete selected
method tables, 23 direct call anchors and the symbolic discardKeyEvents
reference, plus the factory branch, parent detachment, false event-cleanup
argument, mouse-target field and six event-class exclusions. The initializer
invocation census was read-only. Complete vendor dumps and exploratory readers
remain ignored; committed material is original analysis/specification only.

The prior AMS destroy/error/default verification also passes. The unchanged
full host Python suite passes **150 tests, no skips**; **103 local links in
six changed Markdown documents** resolve. No target, phone, JavaScript/C99
or provider test ran. No target package was built or installed; target writable
growth and staging are zero. These checks do not establish runtime recovery.
