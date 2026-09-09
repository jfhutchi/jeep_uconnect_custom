# RA4 Xlet result normalization and stopped-state bookkeeping

Date: 2026-09-06. Starting canonical head `e1f12c53db87749db62f7a49a74238fe66ea57a8`.
Existing owner-supplied firmware inspected read-only on the host.

## Decision

**STATIC_PROVED:** AppManager callback `0x14ADE8` separates IPC response
classification, a local success/parse flag, a mapped result code, and app
bookkeeping. Those are not interchangeable completion evidence.

For a stop operation, three integer AMS error codes can be normalized to
success. The [AMS cleanup follow-up](ra4_ams_destroy_cleanup_contract.md) now
resolves them as Xlet exception (8), AMS TIMEOUT (12), and failure to stop all
Xlet threads on destroy (20). A `NoReply` error is not one of those normalized
cases; it maps to nonzero result 34. Nevertheless the app-level result handler reaches its
stop bookkeeping for that failure: it selects `appStopped`, calls
`switchToStop`, and later sends the nonzero result in `errorCode`.

**STATIC_PROVED additional limit:** a transport-success reply whose JSON
cannot be parsed clears the controller's success flag but retains mapped
result zero. The app-level callback can therefore publish a zero-code result
before later controller processing uses the failed-parse flag. This does not
prove that the original requester ultimately receives success, or that such
a reply was observed on a radio.

**Product consequence:** an app record marked stopped, a list update, an event
named appStopped/appPaused, or even its normalized zero result does not alone
prove a hung Xlet is contained or the display/input is reclaimed. Preserve raw
error evidence and independently qualify cleanup. These findings extend the
[pause/watchdog report](ra4_xlet_pause_watchdog.md); no runtime gate passes.

## Artifact identities and coordinates

Paths are relative to ignored `analysis_ra4_18.45.01/work/`; hashes are SHA-256.

| Artifact | Path | Bytes | Hash |
| --- | --- | ---: | --- |
| AppManager | `hidden_hbc_ifs/segment_00f20000/files/bin/appManager` | 1268061 | `608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591` |
| Shared HMI | `primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/MainSupplement.swf` | 1407783 | `e9d796ea4b4c83ed518bfe3b3c341e54e510a1ae0f78ebbffbd655b7c36a3258` |

Native anchors are ARM virtual addresses. SWF anchors are reconstructed FWS
offsets in ABC 0, base `0x264EB`, 15157 methods. Selected complete native
functions and the HMI consumer bodies were inspected. Embedded jump tables
were read as data rather than accepting their accidental ARM disassembly.

## Callback identity and response classification

The preceding report identifies `0x14ADE8` as the callback supplied by both
pause and stop paths. It receives status/result/token arguments, looks up the
app by token, and obtains its current operation through `0x10B9C8` at
`0x14B170`. The operation accessor translates intermediate field `0x94`
through table `0x1FFFA0`, whose five entries are `1,3,2,4,5`.
Intermediate-state values therefore must not be confused with operation IDs.
The app handler selects stop for operation 2 and pause for operation 3.

At `0x14B1F4` the callback calls classifier `0x17C788` with status and result.
Relevant observed classifications and their mapping through `0x17C3FC` are:

| Response condition | Classifier category | Mapped result | Anchors |
| --- | ---: | ---: | --- |
| Non-error status and non-null result pointer | 0 | 0 | `0x17C870` / `0x17C874`; table entry `0x17C428` -> `0x17C484` |
| `com.harman.service.Error` | 1 | 9 with parsed AMS error JSON; 12 if null | `0x17C814` / `0x17C844`; `0x17C450` through `0x17C464` |
| Other reported D-Bus error | 2 | 35 | `0x17C868`; table entry `0x17C430` -> `0x17C440` |
| `org.freedesktop.DBus.Error.NoReply` | 3 | 34 | `0x17C7D4` / `0x17C804`; table entry `0x17C434` -> `0x17C448` |
| Non-error status with null result | 4 | 12 | `0x17C894`; table entry `0x17C438` -> `0x17C48C` |
| Null status | 5 | 12 | `0x17C8AC`; table entry `0x17C43C` -> `0x17C48C` |

The complete six-entry jump table at `0x17C428` is
`17C484,17C450,17C440,17C448,17C48C,17C48C`. Result 34 here is a mapping of
an observed error name, not a measured callback deadline. The existing report's
unresolved effective timeout value remains unresolved.

For category 1 the caller obtains parsed AMS error data at `0x14B22C`, using
status member `+8` through helper `0x17D618` (`0x17D664` / `0x17D668`). The
callback stores that error object at stack `+0xF0`. Successful-reply JSON is
parsed into a separate object at stack `+0xE0`; conflating those objects would
misread the normalization and malformed-reply branches.

## Stop-only error normalization

The callback maps the category at `0x14B3A0`. It then checks operation 2
and a false local success flag at `0x14B3C4` through `0x14B3D0`. Only that
selected stop path calls `ignoreError` (`0x144E5C`) at `0x14B3D8`.

The helper checks a non-null JSON value and integer `errCode`
(`0x144E7C`, `0x144EA8`, `0x144ECC`, `0x144EDC`). It accepts exactly
**12, 8 or 20**, using comparisons at `0x144EE4`, `0x144EE8`, `0x144EF0`
and branches at `0x144EEC` / `0x144EF4`. The accepted return is true at
`0x144FDC`; null, wrong-type or other values return false at `0x144FC0`.
Their semantic names, initially unresolved in this native trace, are now
established by the [AMS field/cleanup trace](ra4_ams_destroy_cleanup_contract.md):
Xlet exception (8), AMS TIMEOUT (12) and incomplete thread termination (20).

Accepted normalization sets mapped result zero and the local success flag
true at `0x14B3F4` / `0x14B3F8`. Other errors preserve their mapping.
`NoReply` has category 3, so the category-1 error extraction is skipped; the
null error object fails ignoreError. Its mapped result stays 34. Thus AMS
TIMEOUT can be normalized on stop, while D-Bus NoReply remains nonzero;
a blanket claim that AppManager suppresses every timeout is unsupported.

## App stopped-state updates do not require a zero result

Regardless of that local flag, the callback invokes app handler `0x112648`
at `0x14B420`, passing app, operation, mapped result and the error object.
The handler stores the mapped result in r7. Result zero/nonzero selects
success/error diagnostics at `0x112670` / `0x112674`; both normal branches
join at `0x112824` before operation dispatch.

For operation 2, `0x11293C` / `0x112940` selects the stop branch. That branch
sets event name `appStopped` at `0x112A68` / `0x112A6C` and calls
`switchToStop` (`0x10D930`) at `0x112A78`, without another zero-result gate.

If the app's status field `+0x98` is not already 1, switchToStop:

1. Calls paused-list removal helper `0x12C56C` at `0x10D9B8`.
2. Sends `appListUpdated` at `0x10D9E0` through helper `0x17C98C`.
3. Calls running-list removal helper `0x12C644` at `0x10DA24` and sends
   another appListUpdated at `0x10DA4C`.
4. Calls status setter `0x10D3A0` with value 1 at `0x10DA88` through
   `0x10DA90`; the setter writes the changed value at `0x10D3C8`.

The paused/running helpers use the app token at `+0x40` and removal helper
`0x198B00` at `0x12C5A4` / `0x12C680`. Their diagnostics identify the
collections; this is native AppManager bookkeeping, not an AMS Container,
Screen window, VM thread or input-contact deletion proof. If status is already
1 the routine skips that update sequence. No physical cleanup is inferred.

After operation selection the common path resets intermediate state to 5
at `0x112C2C` / `0x112C34`. For the NoReply example, mapped result 34
takes the non-9 path at `0x112C38` / `0x112C3C`, and the appStopped event
reaches emitter `0x10BFE4` at `0x112E14` with that code intact. The emitter
serializes appId, errorMessage and integer errorCode and sends through
`0x17C98C` at `0x10C128`. Thus an event's name and errorCode convey different
facts. Neither delivery nor target cleanup is proved by static dispatch.

## Malformed successful reply: preserve the parse flag separately

For category 0, the controller parses the result string at `0x14B298`.
Parse success sets its r8 flag to one at `0x14B2C4`. Parse failure logs an
error, clears the parsed result object and sets r8 to zero at `0x14B328`.
The category in r7 remains zero; `0x17C3FC` maps it to result zero anyway.

That result is passed to the app handler before the controller's later
state-machine decisions. A pause operation selects appPaused, then its
normal emitter path uses code zero; a stop selects appStopped with the same
code. This is a static conditional path, not a captured malformed AMS reply.
Later controller decisions still consult r8 (for example `0x14BA00` /
`0x14BA04`); the full controller/request outcome is not reduced to this event.
The future acceptance record must retain parse validity alongside result code.

## HMI pause-result consumer

MainSupplement method 6410 recognizes appPaused at FWS `0x2A7C9B`.
It reads errorCode at `0x2A7CD0` and compares with zero at `0x2A7CD6`.
Nonzero dispatches START_XLET_ERROR at `0x2A7CE9`; zero constructs APP_PAUSED
with appId and dispatches at `0x2A7D0C`. Its earlier SuperApp identity match
clears mSuperAppPausing independently of that error check.

The APP_PAUSED consumer, method 571, updates local flags and has selected
identity-specific behavior. Its SuperApp/current-APPS_ACTIVE branch can
navigate back at `0x251C2D`; a separate app-ID `999` case can request another
pause at `0x251BDC`. Neither supplies a universal custom-app cleanup API.
The separate appStoppedStarted event observed in method 6410 is not treated
as an alias for the native appStopped event without a traced translation.

## Integration requirements and next target

The [resident proof](../docs/21_first_resident_runtime_proof.md) must correlate
the exact app/operation with raw response category, raw AMS errCode when
present, parse validity, normalized result and the resulting lifecycle event.
It must then establish app-container/window removal or hiding, input/contact
release and usable stock foreground independently. A list entry or event
alone cannot close fail-open acceptance.

**Next bounded target:** the actual AMS pause/destroy implementation and its
callback-timeout consumer, followed by AWT/Screen container/input cleanup.
Determine what happens when an app does not return from its lifecycle method,
without executing a target failure injection. AppManager now supplies a
concrete boundary where bookkeeping can advance despite failure; tracing more
labels in that bookkeeping cannot substitute for the downstream cleanup proof.

Reproduction uses existing ARM ELF/PT_DYNAMIC tools and the SWF ABC inspector.
Keep jump tables as data, translate intermediate state before naming operations,
and keep successful reply JSON separate from AMS error JSON. Full disassembly
and vendor artifacts remain in ignored host evidence. Committed changes are
original analysis/specifications only; target bytes, growth and staging are zero.

Fresh validation: two artifact hashes/sizes, 102 native instructions, two
complete native tables, nine literals, four resolved imports and 14 HMI
instructions matched direct reads. ABC base/method count also matched. The
unchanged full host Python suite passed **150 tests, no skips**. No target,
phone, JavaScript/C99 or provider test ran; no runtime cleanup is established.
All 102 local Markdown links in the seven changed documents resolve.
