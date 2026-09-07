# RA4 Screen-loop accessor: fused byte read and segmented field location

Date: 2026-09-06. Starting canonical head `1ac0ba2`, clean and synchronized
after fetch. Local static analysis only; no radio execution or GitHub Actions.

## Decision

Later follow-up: the [compiled-method and factory trace](ra4_screen_factory_lifetime.md)
identifies the six non-inline entries, distinguishes their two press-state byte
stores from pumpEvents, and connects new screen creation to a graphics device
and retained daemon runnable. A supported stop/release transition remains open.

**STATIC_PROVED:** the five-byte GLESPlatformScreen.access$800 body uses a
fused D7/D0 operation. D7 obtains its receiver from local variable zero and
consumes the following opcode and two-byte operand. For operand 46, the D0
sub-handler follows one object-block link, then loads a signed byte at offset
0x12 in the next block. The operand is a field-location value; it is not a
constant-pool index or a flat receiver-relative byte offset.

**STATIC_PROVED:** both inspected D7/D0 dispatch variants share their load
handler with D7/D1. They use LDRSB without a subsequent one-bit mask before
pushing the result. Standalone D0 instead loads an unsigned byte and masks
with 1. The method descriptor is Boolean, but that does not justify rewriting
the fused instruction semantics as a normalized Boolean load for arbitrary
stored byte values. Ordinary stored zero/one values agree in both paths.

**HIGH, following the field-layout reconstruction below:** location 46 maps
to the named pumpEvents field. The loader's selected allocation rules and
the class's field metadata produce that location, corroborated by eight
other quick getters. This is a static reconstruction, not a live object-layout
observation. **UNKNOWN:** a supported writer that requests loop exit, live
visibility between threads, and completed event/contact release. No supported
per-app stop API or runtime failure is established.

## Artifact and dispatch evidence

AMS is the same 11956352-byte recovered image, SHA-256
`96683b789ecf06a8575915d0b446b532e1f4ee87feb31d925cb7ba3d7d324d27`.
ARM addresses are virtual addresses translated through PT_LOAD; ROM addresses
are file offsets. Pointer tables are treated as data, not disassembled code.
The [preceding loop trace](ra4_screen_loop_release_boundary.md) identifies
class slot 914, method ordinal 31, storage 0xC67C44 and the caller's zero test
leading to normal return. Its ROM body at file offset 0x63917D is
`D7 D0 00 2E AC`, with descriptor `(Ljava/awt/GLESPlatformScreen;)Z`.

The interpreter loads an opcode at 0x5E9ACC, obtains base 0xC0C914 through
the literal at 0x5E9ADC, and indexes the fast table with an additional 0x38C
at 0x5E9AE4. It transfers control through the selected pointer at 0x5E9AF0.

| Dispatch entry | Address of table word | Target |
| --- | --- | --- |
| Fast D7 | 0xC0CFFC | 0x5EB89C |
| Slow D7 | 0xC0CC70 | 0x5F4FDC |
| Fast D7/D0 | 0x5EB964 | 0x5F7A98 |
| Fast D7/D1 | 0x5EB968 | 0x5F7A98 |
| Slow D7/D0 | 0x5F5088 | 0x5F7AF4 |
| Slow D7/D1 | 0x5F508C | 0x5F7AF4 |
| Fast standalone D0 | 0xC0CFE0 | 0x5EB27C |

The fast D7 body reads the next opcode at 0x5EB8B8, its operand bytes at
0x5EB8C4/0x5EB8CC, and advances past those three bytes. It reads the local
base at 0x5EB8B0 and obtains the receiver at 0x5EB8D4. After the null check,
it subtracts 0xB4 from the sub-opcode and uses the inline pointer table at
0x5EB8F4. The slow variant obtains the sub-opcode and operand through helpers
at 0x5F4FE0/0x5F4FEC, selects the same local receiver, and dispatches through
the table at 0x5F5018. These are fused operations; listing D7 and D0 as two
independently dispatched instructions would misrepresent this interpreter.

## Address calculation and returned value

For the selected nonnegative 16-bit operand, the verified load calculation is:

1. Divide the logical byte location by four to obtain a logical word index;
   retain the low two bits as its byte lane.
2. While the word index exceeds six, follow the pointer at block +0x1C and
   subtract seven from the word index.
3. Load a signed byte at the remaining word index times four, plus the lane.

For 46: logical word 11, lane 2, one link, remaining word 4, offset 18
(0x12). This is an explanation of recovered code, not a target address or
an instruction to mutate a live object. Block headers and unrelated fields
are not assigned meanings from this calculation.

The fast path's link load is at 0x5F7ABC, offset composition at 0x5F7AD4,
LDRSB at 0x5F7ADC and result push at 0x5F7AE0. The slow path's corresponding
anchors are 0x5F7B14, 0x5F7B28, 0x5F7B2C and 0x5F7B30. Neither selected
load-to-dispatch span contains an AND mask. Standalone D0 uses LDRB at
0x5EB2F4 and AND 1 at 0x5EB2FC. No corrupted-byte behavior or live divergence
was tested, and none is alleged.

## Field descriptor path

The named constructor write to pumpEvents remains independently established
through class 914 CP4 at ROM 0x638EE3. setVisible writes the different named
visible field through CP13. Neither fact supplies pumpEvents' effective
numeric field location, and declaration ordinal 12 is not location 46.

The ordinary putfield dispatcher calls 0x5E8724 at 0x5EA260. On its selected
resolved-field path, the helper reads a type byte from descriptor +7 at
0x5E87C4 and a location from descriptor +0x10 at 0x5E87CC. Its B and Z table
entries at 0x5E8820 and 0x5E8880 both select the segmented byte store at
0x5E8B10, ending in STRB at 0x5E8B40. This supplies a concrete next trace:
recover how class 914 CP4 obtains that descriptor and location, then identify
a supported false-writing lifecycle caller. The follow-up below reconstructs
the location but does not observe a particular initialized runtime object.

The earlier 4122-pool negative reference census retains its original boundary.
This instruction trace is not a new exhaustive census of quick writes,
native stores, reflection, inherited behavior or optional components. Field
packing must not be inferred solely from declaration order or neighboring
getters. No direct field mutation is proposed as a lifecycle API.

## Follow-up: named field layout and bounded writer check

Starting head `f26a3e7`, 2026-09-06. The field loader at 0x5D67D0 calls the
superclass resolver at 0x5D67F8. With no superclass, it seeds the logical
word count at three (0x5D6F50/0x5D6F58); otherwise it obtains the superclass's
layout word and available small-field locations through 0x5D6814-0x5D6854.
ROM class 914 names class 1286, java/lang/Object, as its direct superclass.
Object has no superclass or declared fields. This supplies a three-word
starting layout without inherited instance fields.

The loader reads each field record through 0x5D5E20, obtains its descriptor
type through 0x5D0954/0x6148F8, and skips instance-location allocation when
the static bit is set at 0x5D6A78. It links each new descriptor in encounter
order: head store at 0x5D6F38 and next link at 0x5D6A74. The resolved CP
field path selects the field-list head at 0x5D17A4 and follows +0x18 links
according to the member ordinal at 0x5D17C8/0x5D17CC. Class 914 CP4 encodes
the resolved field pair (914,12), whose declaration is pumpEvents:Z.

The type-dispatch table at 0x5D6A98 sends B/Z to 0x5D6FE8, L/I to
0x5D6F64 and J to 0x5D6CB8. Ordinary word allocation advances the logical
word count and writes its byte location to descriptor +0x10 at 0x5D6FA4.
The selected long case starts at logical word nine, remainder two within
its seven-word block, and consumes two words without an alignment gap.
The byte allocator first reuses a saved byte, then a saved halfword, then
space from a word. Its no-hole branch at 0x5D715C allocates one word and
saves the remaining byte and halfword. The selected halfword reuse path at
0x5D7000 consumes its first byte and saves the second. Static fields do not
consume instance space.

Applying those selected rules to all 17 declarations yields 14 instance
locations; the three excluded static declarations are
_windowPropertyVisibility_, windowInitDone and lock:

| Field | Logical byte location | Corroborating quick getter operand |
| --- | --- | --- |
| javaWindow | 12 | access$1100: D6/3 |
| ksWindow | 16 | getKSWindow: D6/4 |
| eglDisplay | 20 | getDisplay: D6/5 |
| eglConfig | 24 | getConfig: D6/6 |
| eglSurface | 28 | getSurface: D6/7 |
| eglContext | 32 | getEGLContext: D6/8 |
| nativeImageLibHandler | 36 | getNativeImageHandle: D5/9 |
| currentVisibility | 44 | No selected quick getter |
| visible | 45 | Named setVisible write is separate |
| ie | 48 | access$400: D6/12 |
| pumpEvents | 46 | access$800: D0/46 |
| stillPressed | 47 | No selected quick getter |
| prevPressedX | 52 | No selected quick getter |
| prevPressedY | 56 | No selected quick getter |

D5/D6 operands are logical word indices: their verified handlers load with
index scaled by four, while D5 reads the following word as well. D0 is a
logical byte location. Accounting for that distinction, eight other getter
bodies agree with the reconstructed locations before comparing access$800.
The position of ie before pumpEvents in declaration order does not force
the byte flag after ie in storage: the byte allocator reuses the remaining
halfword at 46. The result is HIGH evidence for access$800 reading pumpEvents;
it is not a generic VM layout implementation or a live memory measurement.

All 30 inline bodies among this class's 36 declared methods were decoded to
their ends. The bounded decoder handles D7 as a fused read; getBounds also
uses standalone D4, whose two-byte operand consumption and word load were
verified at 0x5EACB4. Exactly one putfield targeting resolved (914,12) occurs:
the constructor at file offset 0x638EE3, immediately preceded by iconst_1.
No false-writing named putfield occurs in these 30 bodies. The six methods
without inline bodies, native/reflection/dynamic behavior, other classes and
optional components are outside this writer result. This does not prove the
flag is immutable or that the thread leaks. setVisible still writes location
45's named field; it is not evidence of clearing pumpEvents at location 46.

Fresh follow-up verification reran the preceding artifact chain and checked
64 new ARM anchors, eight table entries, superclass metadata, all 14 derived
instance locations, three static exclusions, eight other getters and the
target getter. All 30 inline bodies decoded, with exactly the constructor
write described above. The reconstruction deliberately rejects unmodeled
type/alignment cases rather than generalizing beyond this class. No target
or vendor VM code was executed; the helper remains ignored.
All 79 local links across the four follow-up Markdown files resolve;
whitespace checks pass. The workflow remains the verified manual-only blob.

## Product consequence and verification

The [future resident proof](../docs/21_first_resident_runtime_proof.md) still
requires the provider-supported per-app lifecycle and event ownership/release
contract. A zero predicate can reach a normal loop return; this trace does
not connect app Return, hiding, pause or stop to that zero, nor prove native
destruction or stock focus/contact recovery. The
[standard JNI registration limit](ra4_jni_registration_limit.md) remains
closed for the two inspected tables. No vendor replacement is selected.

Initial-checkpoint local checks reran the preceding hash-verified I/O, Screen-loop, native
lookup and JNI-registration checks. New checks matched 58 ARM anchors, ten
dispatch entries, the dispatch-base literal and the five accessor bytes;
verified both unmasked load spans; and checked six host arithmetic examples
including block boundaries and location 46. These are static artifact and
derived-address checks, not VM execution. No committed executable code changes;
the prior 162-test host-suite result remains historical. Exploratory scripts
and protected artifacts remain ignored. USB topology, AOA/protocol transport,
engine supply, authorization and all target resource gates remain unchanged.
That initial checkpoint verified 117 local links across five changed Markdown
files and passed whitespace checks. The follow-up verification is recorded above.
