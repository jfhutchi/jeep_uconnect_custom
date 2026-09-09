# RA4 JNI native-registration limit

Date: 2026-09-06. Starting canonical head `37b1351`, clean and synchronized
with origin after fetch. Static host research only; no target execution or
GitHub Actions.

## Decision

**STATIC_PROVED:** both recovered JNI interface tables point RegisterNatives
and UnregisterNatives to stubs that invoke the internal not-implemented
diagnostic helper. That helper calls the imported abort function. Program
initialization obtains both table pointers and stores them in its configuration.
The inspected standard registration entries do not install native methods.

This closes one specific hypothesis from the
[event-release investigation](ra4_screen_loop_release_boundary.md): standard
JNI RegisterNatives through these tables cannot be treated as a supported
way to connect KSEventAtom.nativeKSFreeEvent to the differently named library
export. A provider cannot establish that compatibility merely by citing the
generic JNI registration API.

**UNKNOWN:** whether the event-free declaration is called, a different
build-specific binding/release path, effective live table selection, and
completed event/contact release. This is not an observed crash or leak and
does not reject every native engine or establish a measured local capability
failure. No external-compute fallback or vendor modification is selected.

## Artifact and table identity

AMS is the same 11956352-byte recovered image, SHA-256
`96683b789ecf06a8575915d0b446b532e1f4ee87feb31d925cb7ba3d7d324d27`.
Addresses are ARM virtual addresses translated through PT_LOAD. Both table
bases are in the image's file-backed executable load segment; they are
static pointer data, not instructions or observed live JNIEnv addresses.

| Table base | GetVersion slot 4 | RegisterNatives slot 215 | UnregisterNatives slot 216 |
| --- | --- | --- | --- |
| 0xC12250 | 0x620450 | 0x6207CC at 0xC125AC | 0x6207B4 at 0xC125B0 |
| 0xC125F0 | 0x620450 | 0x6207CC at 0xC1294C | 0x6207B4 at 0xC12950 |

Both tables begin with four zero reserved entries. Their GetVersion function
constructs 0x00010004 at 0x620450/0x620454 and returns. Table index identities
are corroborated by the local JNI_RegisterNatives/JNI_UnregisterNatives
diagnostic literals and the
[JNI function-table specification](https://docs.oracle.com/javase/8/docs/technotes/guides/jni/spec/functions.html#RegisterNatives),
which assigns indices 215 and 216 and defines registration using method
names, signatures and native function pointers. The reference defines the
interface; the local pointers and instructions establish this build's behavior.

Getter 0x6204F4 constructs 0xC12250; getter 0x620500 loads 0xC125F0.
The selected initialization path calls them at 0x106458 and 0x106460 and
stores the returned pointers at configuration offsets +0x15C and +0x160,
at 0x10645C and 0x106514. This is a concrete configuration connection.
It is not a live observation of which table a particular native caller uses,
nor a claim that every similarly numbered offset elsewhere has that meaning.

## Registration stub and abort path

The complete RegisterNatives instruction body at 0x6207CC loads the
JNI_RegisterNatives literal and calls 0x5E4AAC at 0x6207D4. The corresponding
UnregisterNatives body at 0x6207B4 calls the same helper at 0x6207BC with its
own name literal. Neither body processes an incoming native-method array.

The shared helper at 0x5E4AAC moves that name into the diagnostic argument,
constructs the format and prefix addresses, calls the output helper at
0x5E4AC4, then calls abort through PLT 0x105A28 at 0x5E4AC8. The verified
literals are the not-yet-implemented function diagnostic and INTERNAL NYI
ERROR prefix. The import is abort, not a Java exception constructor or an
ordinary negative registration result.

The stubs contain a following MOV r0,0 instruction. It must not be reported
as successful native registration: the preceding helper calls abort. The
static call path is sufficient to disqualify these entries as a supported
registration mechanism. There is no need to execute this path on a radio.

## Consequence for a legitimate resident adapter

The preceding report proved that ordinary dynamic naming preserves the
KSEventAtom versus KSEvent difference, so a short/argument-qualified lookup
does not explain the mismatch. This follow-up also removes the inspected
standard RegisterNatives entries as a supported explanation. It does not
exclude build-time binding, another matched component set, an implementation
in another library, an unused declaration or another release API.

For any proposed Java/JNI projection adapter, the provider must identify a
supported binding mechanism for this exact AMS/Jamaica build and the required
native APIs. Do not assume a generic RegisterNatives-based adapter is usable.
Native packages that do not depend on this interface require their own
qualification; this finding is not a blanket rejection of native projection.
Do not patch the stubs, alias vendor exports, replace the stock VM or treat
an aborting probe as a required experiment.

The [resident proof](../docs/21_first_resident_runtime_proof.md) and
[engine qualification](../docs/11_projection_engine_feasibility.md) now carry
this exact Java/JNI dependency check. Camera/critical/comfort priority and
stock input recovery still require supported integration and live evidence
in a separately authorized future setting. USB topology, AOA transport,
engine supply and resource budgets remain unchanged.

Next useful local evidence is the Screen-loop accessor's effective quick-op
semantics and its supported lifecycle control, or a concrete alternative
event-release path. The standard JNI registration hypothesis is closed for
these two inspected tables and should not be repeatedly reopened without
new artifact or provider evidence.

## Verification

Local verification reran the preceding artifact checks and matched 25 new
ARM anchors, two JNI table headers, six selected table entries, four literals,
the abort import and both getter call-site censuses. Hash identity and
segment translation were checked. No compiled artifact was executed, no
GitHub Actions run was requested and no vendor payload is committed.
This checkpoint changes original documentation only. The earlier 162-test
host-suite result remains historical.
All 118 local links across six changed Markdown files resolve; whitespace
checks pass. The remote workflow remains the verified manual-only blob.
