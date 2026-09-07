# RA4 resident Xlet container and LWUIT view path

Date: 2026-09-06. Starting canonical head `1484f880642d8f8813b91ed750fb5feceae8effc`.
Existing owner-supplied artifacts were parsed on the host without execution.

## Decision

**STATIC_PROVED stock client path:** two independent application codebases call
`javax.microedition.xlet.XletContext.getContainer()Ljava/awt/Container;`, make
the returned container visible, initialize `com.sun.lwuit.Display`, and schedule
UI work through `Display.callSerially(Runnable)`. The vehicle-user-guide code
also constructs a form, registers a button action listener and calls `Form.show()`.

**STATIC_PROVED runtime metadata:** hash-bound AMS ROM class objects identify
the XletContext interface, AWT Container, LWUIT Display and aicas GLESCanvas.
Combined with actual application invocation sites, this gives **HIGH confidence
in a stock Xlet/AWT/LWUIT graphics path**, not merely generic Xlet lifecycle support.

This narrows the no-engine resident proof's view prerequisite to a concrete
API family. It does not establish a supported custom SDK, full 640x480 usable
app area, native video-buffer import, permitted projection integration, focus
arbitration, camera priority or owner-death cleanup. None of those runtime gates
passes from a Java method name, a successful parse or a stock sample alone.

The [projection gateway mismatch](ra4_projection_gateway_dispatch.md) remains.
A separately authorized application view is a candidate integration lane; it
does not supply the missing receiver or repair the stock projection destinations.

## Artifacts and selection boundary

Prefix X: `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/`.
All paths identify ignored local evidence. Hashes are SHA-256.

| Label | Path under X | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| Registration | `kim_packages/KIM9/xlets/A7A4B215-9B5A-7DAA-457C-15545178E72F/prog/jars/800X480_65_UconnectRegistration-v02.02.06_FIT.jar` | 2174384 | `50b8fd2549679fc06e56507ff61fb972305ce725bd3942684b9df5e43714df8e` |
| User guide | `kim_packages/KIM1/xlets/079aa169-df8f-48b4-b331-4ed51dbf6b12/prog/jars/079aa169-df8f-48b4-b331-4ed51dbf6b12.jar` | 1558076 | `382026942a6cde768c4c3762497523c3300a5c3fa101d8661b2b0dfacfe3b260` |

The first filename explicitly says 800X480. It is evidence for shared API usage,
not for the exact display area on the target Jeep. The second package is the
previously hash-identified user-guide tuple. No app was installed or launched,
and this report does not claim either selected package is active on the live unit.

Initial archive-member inspection located GUI-bearing stock apps. The
reproducible call inventory selected two Registration Xlet class members and
six AbstractHUXlet members in the user-guide JAR. These eight classes had zero unresolved
`invokedynamic` instructions. They are a targeted sample, not an exhaustive
application call graph. Code/resource searches did not execute Java, extract
classes to a target, examine owner account data or reuse vendor implementation.

| Principal class member | Bytes | SHA-256 |
| --- | ---: | --- |
| Registration `com/sprint/chrysler/uar/xlet/UconnectRegistrationXlet.class` | 4505 | `cf345440e0f44eb160b600075842b2eb67b9da1f1dbdde7898826003e5f51596` |
| User guide `com/tweddle/core/AbstractHUXlet.class` | 11077 | `235507825b0edde8df8023a40e98326bdccedb9b3acf79e3f6b30746d5e33c21` |
| User guide `com/tweddle/core/AbstractHUXlet$5.class` | 720 | `565d620b6656f100037b681d38148cc042ace5f041562c4b72591d58527303ad` |

## Resolved invocation evidence

BCIs below are hexadecimal bytecode indices relative to the named JVM method's
Code array, not JAR offsets or reconstructed SWF addresses. Complete selected
method bodies were decoded; surrounding branches and operands were inspected.

| Class / method | BCI | Resolved target and consequence |
| --- | --- | --- |
| Registration `initXlet` | `0x68` | `XletContext.getContainer()Ljava/awt/Container;` |
| Registration `initXlet` | `0x70` | `java.awt.Container.setVisible(Z)V`, with true operand |
| Registration `initXlet` | `0x74` | `Display.init(Ljava/lang/Object;)V` |
| Registration `startXlet` | `0x12` | `Display.callSerially(Ljava/lang/Runnable;)V` |
| User guide `initXlet` | `0x63` | Same XletContext getContainer signature |
| User guide `initXlet` | `0x6B` | Same AWT setVisible signature, with true operand |
| User guide `initXlet` | `0x6F` | Same Display init signature |
| User guide `startXlet` | `0x21` | Queues UI work through Display.callSerially |
| User guide `access$600` | `0x06`, `0x62`, `0x75` | Constructs LWUIT Form, registers Button.addActionListener, calls Form.show |
| User guide `pauseXlet` | `0x0B` | Queues AbstractHUXlet$5 through Display.callSerially |
| User guide `terminate` | `0x04` | Calls XletContext.notifyDestroyed()V |

The Java ME API defines this XletContext container as the parent for an Xlet's
AWT components. Oracle's [PBP application example](https://docs.oracle.com/javame/config/cdc/cdc-opt-impl/ojmeec/1.0/reference/html/z4000c841293984.html)
uses the same family. Oracle's [LWUIT introduction](https://docs.oracle.com/javame/dev-tools/lwuit-1.4/LWUIT_Developer_Guide_HTML/cefiegjh.html)
describes Xlets for CDC and Display/Form application setup. These references
corroborate semantics; neither establishes RA4 vendor support or licensing.

The sample also uses `setPureTouch`, but that call alone does not prove where
hardware touch events originate, who owns focus, or that the whole display is
available. An app button listener proves a stock input-consumer interface,
not exclusive touch ownership or correct camera preemption.

## AMS runtime ownership corroboration

AMS path: `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/AMS`.
Size 11956352; SHA-256
`96683b789ecf06a8575915d0b446b532e1f4ee87feb31d925cb7ba3d7d324d27`.

The existing ROM decoder read the 60,877-entry name pool from file `0x9C2071`
through terminator `0xAB8ECC`. The existing class-pointer table at
`[0xB1BC48,0xB20424)` supplies adjacent class bounds. Matching self-name
markers use the existing `07 E0` plus big-endian one-based pool-ID encoding.
This associates names with bounded class objects rather than relying on raw
substring proximity. These are metadata objects; their complete native
implementations and internal call paths were not reconstructed here.

| Class | Pool ID / name header | Class slot / file bounds | Self-name marker |
| --- | --- | --- | --- |
| `com/aicas/lwuit/gles/GLESCanvas` | 33850 / `0xA6DC1B` | 142 / `[0x59E308,0x59F0D8)` | `0x59E3DE` |
| `com/sun/lwuit/Display` | 34332 / `0xA6F18A` | 623 / `[0x5EED28,0x5F0188)` | `0x5EED94` |
| `java/awt/Container` | 42795 / `0xA82C65` | 868 / `[0x62FDF0,0x631F98)` | `0x62FE80` |
| `javax/microedition/xlet/XletContext` | 44392 / `0xA87235` | 2390 / `[0x706410,0x706468)` | `0x706411` |

The stock [AMS startup](ams_startup_chain.md) separately sets window identity
AMS, initial visibility false, and 640x480 dimensions. It configures a 50M heap,
Xlet scheduling defaults and a GL ES renderer budget. These are shared runtime
configuration values, not proof of spare RAM, per-app isolation or an available
640x480 projection video surface. No new VM or LWUIT library should be charged
as a required private component merely because the stock metadata is ROM/AOT;
permitted reuse and attributable memory still need proof.

## Cleanup and remaining integration boundary

Registration's `pauseXlet` body is empty; its destroy method saves application
state. The user-guide pause method queues work that clears its async-result
stack and calls an application helper. Its destroy method unregisters a
lockout listener and shuts down application schedulers. Its separate terminate
method notifies the Xlet context of destruction.

These differing implementations do not establish a universal release recipe.
No `Display.deinitialize()` or container-hide call occurs directly in the two
sampled principal destroy methods. Framework, manager, subclass and native
cleanup may happen elsewhere. Absence of a direct call is not proof of a leak,
and successful voluntary exit is not proof of hung-app recovery.

**Next technical target:** trace AMS's Xlet container visibility/focus owner and
the native AppManager-to-AMS foreground handoff, including denial, pause/stop,
window disappearance and stock reclaim. Keep camera/critical/comfort precedence
outside the custom app. Native decoded-video buffer import is a separate later
engine integration gate; LWUIT Form.show does not satisfy it. Oracle explicitly
notes that [LWUIT implementation internals](https://docs.oracle.com/javame/dev-tools/lwuit-1.5/devguide/lwuitimpl.htm)
are port-specific and lack compatibility guarantees.

## Reproduction and verification

The original [JVM invocation inventory](../analysis_tools/jvm_call_inventory.py)
uses host-only Python 3.11+ and `jawa==2.2.0`. It reports selected actual call
instructions and hashes without emitting resource bodies or string constants.
It does not resolve reflection, JNI, virtual runtime targets or ROM/AOT code.

```powershell
$py = 'analysis_work/post_reboot_20260906/venv/Scripts/python.exe'
$jar = 'analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages/KIM1/xlets/079aa169-df8f-48b4-b331-4ed51dbf6b12/prog/jars/079aa169-df8f-48b4-b331-4ed51dbf6b12.jar'
& $py -m analysis_tools.jvm_call_inventory $jar --member 'com/tweddle/core/AbstractHUXlet.class$' --owner 'javax/microedition/xlet|java/awt|com/sun/lwuit'
& $py -m unittest analysis_tools.tests.test_jvm_call_inventory -v
```

Fresh full Python suite: **150 tests passed, no skips**. Five new synthetic tests
cover real call resolution, constant-pool-only negatives, opcode-like operand
bytes, member selection and size/magic failures. The missing-tool test failure
was observed before implementation. Python compileall passed. Three artifact
hashes, three principal-class hashes, 13 invocation BCIs and four ROM ownership
rows were rechecked; 88 local links in changed Markdown files resolved. Eight
stock class members were parsed with no unresolved invokedynamic. No target package,
JavaScript/C99 change, radio operation, phone-bench test or provider contact.
All committed content is original tooling, tests and analysis. Radio installed
bytes, writable growth and staging remain zero.
