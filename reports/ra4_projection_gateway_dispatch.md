# RA4 projection destination routing and USB ownership boundary

Date: 2026-09-06. Starting canonical head `1708c4f186b62f2a3e2ab763056f86a610406d97`.
Read-only static analysis of existing owner-supplied artifacts; host tools only.

## Decision

**STATIC_PROVED:** the recovered HMI contains a projection client contract that
the recovered native gateway cannot resolve through its inspected normal
command and owner-notification paths. Both `phoneProjectionService` and
`DeviceConnectionManager` fall outside this gateway's fixed destination chain.
Its unknown branch clears the service/object outputs and returns `-1`.
The command caller exits before invocation; the availability caller exits
before an owner query or subscription. Merely registering either service name
does not repair this route in the hash-identified gateway.

This is a more specific integration gap than a missing named executable.
It does not prove a receiver is impossible, explain why the OEM shipped this
combination, identify a supported replacement, or establish a live unit's state.
A legitimate matching bridge/build or a separately supported app/engine API is
now an explicit provider prerequisite. Do not patch the stock gateway or
redirect requests to an unrelated stock destination.

## Artifact identity and method

Paths below are relative to `analysis_ra4_18.45.01/work/` and remain ignored.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `hidden_hbc_ifs/segment_001a0000/files/bin/hmiGateway` | 153124 | `8d7fe8789bb012a66fbebd1bd44eefa506c672a5d70c90fbf92b3a5a6f01ec82` |
| `primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/main.swf` | 95683 | `224ee3e4da03d8102c3f154fc12061c88b8f88b2b6e61f5c6034d65153839172` |
| `primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/MainSupplement.swf` | 1407783 | `e9d796ea4b4c83ed518bfe3b3c341e54e510a1ae0f78ebbffbd655b7c36a3258` |

The gateway has four sections: NULL, `QNX_info`, `QNX_usage`, `.shstrtab`.
Its dynamic relocations/symbols remain accessible through `PT_DYNAMIC` despite
the missing ELF relocation and dynamic-symbol sections. Its dependencies are
`libc.so.3`, `libcpp.so.4`, `libjsoncpp.so.1`, `libsocket.so.3`, `libsvcipc.so.1`.
The original ARM helper previously returned an empty PLT map here; its new
program-header path resolves **181 classic ARM import stubs**. An independent
pyelftools read of the dynamic relocation/symbol tables agrees on every slot
and symbol. This is static linkage evidence, not an execution test.

All native addresses below are ELF virtual addresses. SWF addresses are
reconstructed FWS offsets in ABC 0 of the stated artifact. ARM function labels
are descriptive analysis names; prologue candidates were checked with surrounding
instructions, branch targets, imports and returns. Literal pools are not code.

## HMI to native bridge

The prior [backend contract](ra4_usb_stack_backend_census.md) identifies
MainSupplement methods 7063/7094 as the destination initialization and command
envelope. The shared implementation is in `main.swf`, which has 772 methods in
ABC 0:

| Consumer | Method / FWS anchor | Static behavior |
| --- | --- | --- |
| `Connection.send` | 439 / `0x260A3`, `0x260A7` | Encodes the supplied object and calls the shared span client's send method |
| `Connection.onConfiguration` | 441 / `0x26135` through `0x2614D` | Reads the XML `hb.host` and `hb.port`, then calls client connect |
| `Connection.dataEventListener` | 442 / `0x261DE`, `0x262BF`, `0x262C6` | Decodes incoming data, retrieves a runtime-named member and dispatches an event |
| span client send | 654 / `0x2B6DE` | Sends the prepared message through its superclass |

`ModuleLink.xml` supplies localhost port 4400 for both hb/span, as previously
hashed. The connection code reads **hb**, even though the getter is named span.
The gateway parser reads `Type` at VA `0x10CD6C` and `Dest` at `0x10D06C`,
recognizes `Command` at `0x10CDF4`, and calls its command routine `0x10A9A0`
at `0x10CEF0`. Matching message vocabulary, its native SVCIPC imports and the
stock `boot.sh:250` launch of `hmiGateway -sj` establish the native bridge
relationship with HIGH confidence. This run did not prove the native socket's
bound address or connect to it. The trace is not a supported standalone wire API.

## Fixed destination resolution and failure paths

The service/object resolver starts at **`0x1085E8`**. Its comparison chain
runs through the final `OtaService` comparison at `0x1090E8`/`0x1090F0`.
Early string comparisons are inlined; later comparisons call `0x10E24C`.
That helper checks bytes and length and returns a Boolean. The inspected chain
has fixed literal names and fixed destination assignment branches, with no
arbitrary-destination fallback. Neither projection name occurs anywhere in
this gateway's bytes, and neither is a chain member.

For a concrete nonprojection control, `HVAC` at `0x108D8C` maps through the
branch at `0x109F1C`/`0x109F2C` to the existing HVAC service/object pair.
`ConnectionManager` at `0x108DDC` maps through `0x109E9C`/`0x109EAC` to
`com.harman.service.CMCConnMgr` and its object path. It is a different literal
from `DeviceConnectionManager`; similarity of names supplies no alias.

| Path | Native anchors | Consequence for an unknown projection destination |
| --- | --- | --- |
| Service/object resolver default | `0x1090FC` through `0x109110`; `0x109130` or `0x109150` | Assigns empty strings to both outputs; returns `-1` regardless of logging branch |
| Unknown-destination diagnostic | `0x10913C`, string at `0x120018` | Logging depends on flags; a missing log does not prove resolution |
| Command dispatch | resolver call `0x10AA28`, branch `0x10AA30` -> `0x10ACDC` | Nonzero return goes to cleanup and return at `0x10AD28`/`0x10AD2C`, before native command invocation |
| Owner notification dispatch | Type match `0x10D5DC`, call `0x10D608` -> `0x10C7CC` | Uses the same resolver |
| Owner notification rejection | resolver call `0x10C7F8`, branch `0x10C800` -> `0x10C994` | Exits before `nameHasOwner` and `subscribeOwnerChanged`; no initial availability event is synthesized on this branch |
| Supported owner path, for comparison | `0x10C9DC` -> `0x106C14`; `0x106C30` -> PLT `0x10424C` | Calls imported `SVCIPC_nameHasOwner` only after a destination resolves |
| Supported owner subscription | `0x10CA40` -> PLT `0x1049C0` | Calls imported `SVCIPC_subscribeOwnerChanged` only after resolution |
| Signal callback resolver | `0x1071D8`; unknown store `0x1083D4`/`0x1083D8` | Selects the default callback sentinel for unknown names |
| Signal subscribe caller | `0x10C104`/`0x10C114`; sentinel branch `0x10C128` -> `0x10C06C` | Skips the unknown signal subscription |

The availability distinction matters: **unknown gateway destination** and
**known destination with no current service owner** are different conditions.
Only the latter reaches the ordinary owner-state machinery. A connected HMI
transport, absent availability event or static screen label cannot prove that
the projection provider is registered or even addressable.

**INFERRED:** the HMI preserves a broader build-family contract than this native
gateway implements. Optional packaging, a variant omission and unfinished OEM
integration remain possible explanations. No exact MY16 deployment history,
provider package, complete D-Bus interface or compatibility fix is established.

## USB ownership follow-up

The narrow follow-up reviewed `H1/etc/system/enum/common` and its six
`devices/usb/` rule files, plus the existing `enum_devices.lua` selector.
H1 is the gateway's `segment_001a0000/files/` prefix above.

| File | Bytes | SHA-256 | Finding |
| --- | ---: | --- | --- |
| `etc/system/enum/common` | 280 | `bb84dc4cbb0beadb693167f97ceea397b39f7f76b1c01579458a9fc6a105bcc5` | Includes device rules and configures USB enumeration with MS descriptor checking |
| `etc/system/enum/devices/usb/mtp` | 933 | `41d2345596e0b7efcc05110dcd1204c2b2cc0d5890913794a01b6ed7586ca9a0` | Motorola-specific vendor-class matches and generic MTP/MTPZ compatible-ID matches launch media handling |
| `etc/system/enum/devices/usb/ipod` | 590 | `6786b05e8a2f1089854e253cfdd527a532496baf623daab35433d5de3dee4b1d` | Legacy Apple-identified HID/audio matches launch stock media/audio clients |
| `primary_iso/usr/share/MMC_IFS_EXTENSION/bin/enum_devices.lua` | 1809 | `9ecfd96486821287ff44e1e3f7c3e1b97c120b44a73983a9e9ead08f81c4bb83` | Text Lua selects iPod configuration links for Fiat334/Fiat520 in NA/ECE; it is not an AOA ownership selector |

The other four files contain serial/network VID/PID and mass-storage class
rules. No explicit `18D1:2D01` AOA rule was identified in these six files.
This does **not** prove an AOA interface is unclaimed, that MTP cannot conflict,
or that another process will not attach. Descriptor-dependent matching, the
live rule set, detach/re-enumeration ordering and competing client access remain
UNKNOWN. The PC bench's Windows MTP binding cannot be transplanted into QNX.
No script, driver or enumeration command was executed, and no rule was changed.

## Verification and next decision

Fresh host verification: **145 Python tests passed, no skips**, including five
new import tests. The sectionless-resolution and malformed-dynamic cases were
observed failing before the implementation; section-backed regression tests
still pass. `compileall -q analysis_tools` passed. Real gateway import slots were
independently cross-checked against pyelftools. All seven artifact hash/size rows,
20 native instruction/branch anchors and eight SWF anchors were checked against
freshly parsed artifacts. The empty-string target and both negative name probes
were checked; 83 relative links across changed Markdown files resolved locally.
No target, JavaScript, C99, phone-bench or provider test ran.

Reproduce with the existing ignored venv and the stated hash-bound artifacts:

```powershell
$py = 'analysis_work/post_reboot_20260906/venv/Scripts/python.exe'
$gateway = 'analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/bin/hmiGateway'
& $py -m analysis_tools.arm_elf_analysis imports $gateway
& $py -m analysis_tools.arm_elf_analysis disasm $gateway --start 0x1090E8 --end 0x109158 --literals
& $py -m analysis_tools.arm_elf_analysis disasm $gateway --start 0x10C7CC --end 0x10C808 --literals
& $py -m unittest analysis_tools.tests.test_elf32_imports -v
```

The highest-value backend target is a legitimate **matching component manifest
and supported integration contract**, including the bridge route, device manager,
screen, receiver and exact QNX 6.5/ARM32 dependencies. The independent physical
gate remains an owner-supplied passive C2-to-PHY/controller trace. The
[resident no-engine milestone](../docs/21_first_resident_runtime_proof.md)
remains conditional on its supported packaging/view/rollback prerequisites;
this finding neither creates a deployable package nor selects external compute.

Zero installed radio bytes. No stock binary, full disassembly, SWF, private
credential, license or USB/vehicle-state mutation is part of this change.
