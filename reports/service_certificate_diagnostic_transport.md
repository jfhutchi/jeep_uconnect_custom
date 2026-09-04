# RA4 18.45.01 service-certificate diagnostic transport

## Scope and integrated result

RA4 contains a confirmed stock diagnostic transport for the active service certificate:

- diagnostic routine `0xF010` stages certificate bytes in `/etc/security/service.cert`, asks the platform service to validate the completed file, and reports the validation result;
- diagnostic routine `0xF011` removes that same fixed pathname and verifies its absence;
- the validator does not trust transport success. It independently invokes the platform certificate evaluator, which verifies the signed certificate, binds it to the head-unit serial number, and enforces date or ignition-cycle validity;
- only a successfully verified certificate can set signed service flags such as `EngineeringMenu`; the certificate transport does not itself create `/fs/etfs/AMS_DEVELOPMENT`, select an AMS security policy, issue an application signer credential, or validate the factory anti-theft PIN.

This closes the local staging and deletion mechanics, not the issuance question. No diagnostic-session or SecurityAccess predicate appears in the recovered `diagserv.lua` routines or their local dispatcher. The transport is now traced through QNX `dev-ipc` channel 7 to the active IOC/V850 diagnostic application. Static V850 control flow proves an IOC-owned session gate before routine dispatch, a generic security-state check, additional condition/state prerequisites, and the final channel-7 forwarding edge. The specific external session transition and authenticated tool event remain **UNKNOWN**; `0xF010`/`0xF011` do not prove a SecurityAccess unlock because their record mask accepts the initialized security state. Local handler absence must not be interpreted as an unauthenticated external interface or as permission to inject a certificate.

The OEM service-certificate issuer and its private signing key are also outside the recovered corpus. The head unit contains a public verification key; that key can validate an owner-authorized credential but cannot issue one.

## Evidence conventions and safety boundary

All findings are from static, read-only parsing of extracted RA4 18.45.01 artifacts. No vendor executable, Lua chunk, updater, Java archive, or service was run. No stock artifact was modified.

For Lua chunks:

- `prototype` identifies the decoded serialized Lua 5.1 function record in parse order;
- `PC` is the zero-based Lua virtual-machine instruction index within that function;
- `file offset` is the byte offset in the serialized `.lua` chunk;
- `source/debug line` is the line table stored by the vendor compiler.

The internal handler indices and `chan:write` argument sequences below are recorded to prove control flow. They are not an external framing guide. This report intentionally does not describe how to originate a diagnostic session, satisfy any gateway policy, or construct an injectable request.

## Artifact ledger

| Artifact | Size | SHA-256 | Role in this trace |
| --- | ---: | --- | --- |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/usr/bin/cmc/service/diagserv.lua` | 282,802 | `777d96dfa3461caa6ebf4765784f9ba2f4d766fd1ddfe54590a655121353bd64` | diagnostic ingress, staging, validation dispatch, and deletion |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/platform_troubleshoot.lua` | 13,931 | `8beab38ab164479a9fd815116dbfa02a48e3fa661724fa9c4273dc5884a1ba45` | platform certificate evaluation and service-flag state |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/lib/lua/ipc.so` | 15,181 | `ec65941a007ab20703101111cbaf1eec282ee55969f37b8ebb0ef9b10f765f55` | Lua IPC binding used by `diagserv.lua` |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/files/bin/dev-ipc` | 75,930 | `ce9be22bf8d820e5e02e215267ead438a56e1c83f471edca2b84e6be56b90a57` | device-side IPC driver context |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/files/bin/dev-ipc.sh` | 3,551 | `52f108e0277cc9f3cf396070c9264cc2983d9af318869981816f2d050b953a1a` | starts `dev-ipc`; line 118 configures 27 channels |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/files/bin/boot.sh` | 29,268 | `c801d473b0b49e8242114635f4022cc67ccbe03093fec188de3b7188dd636ecf` | normal `diagserv` and authentication-service startup |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/bin/enum-devices` | 33,950 | `8321d9546a893fbc0134cd4cd166176d5ccd4363f9a6db44609b3fa4252a7e4f` | invoked only after a valid `0xF010` evaluation |
| `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/security/scv` | 1,596,550 | `08bb7992d95b27b98bcb222021015cda152eef9fafa573720845d28c837c7fe1` | stock service-certificate verifier |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/etc/keys/serv_cert_key.pem` | 451 | `07e7a63fd528cdd4b4d23bc6aaac03adda4ca9659d0b4a86ddd5d26b8608831e` | public service-certificate verification key |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_019a0000/files/usr/bin/authenticationService` | 273,340 | `9c7c057fbffceb2dc0b77690b6eb07dcd90721de6f89c5a05150fa18cea84699` | ownership event used to trigger platform evaluation at boot |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/lib/lua/authenticationServiceKeyFile.json` | 11,359 | `5968ff07dba7a0316a7fc76687cbef5147699d96538d14a10def0bfd5211ad11` | authentication-service boot configuration; no contents or key material reproduced here |

The duplicate configuration at `segment_00f20000/files/etc/system/config/authenticationServiceKeyFile.json` has the same size and SHA-256.

## Chunk integrity and fixed target path

`diagserv.lua` begins with the Lua signature and version/header bytes `1b 4c 75 61 51 00 01 04 04 04 08 00`: Lua 5.1, little-endian, four-byte integer, four-byte `size_t`, four-byte instruction, eight-byte number, and non-integral numbers. A strict recursive parser consumed all 282,802 bytes and recovered 314 prototypes with no trailing bytes.

The active pathname is not inferred from a log message:

- root constant `K64` is `/etc/security/service.cert`; its serialized constant record begins at file offset `0x2CB1`;
- root PC 117, file offset `0x24D`, source/debug line 67, loads that constant into the `service_cert_file` closure state;
- both diagnostic routines capture that same root value as an upvalue;
- `analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/inventory.tsv` line 20 maps `/etc/security` to `/fs/mmc0`.

Therefore these routines operate on the service certificate stored on the MMC-backed filesystem. They do **not** operate on `/fs/etfs/service.key`, `/fs/etfs/AMS_DEVELOPMENT`, `/fs/etfs/enableEngMenu`, an application package, or an AMS registry.

## Ingress and local dispatch

The certificate routines are reached through `diagserv`'s raw IPC reader, not through its separately registered D-Bus methods.

| Stage | Exact evidence | Result |
| --- | --- | --- |
| Open IPC channel | root PCs 2300-2305, file offsets `0x2469-0x247D`, source/debug line 7683, assert `ipc.open(7)` | binds `chan` to internal IPC channel 7 |
| Register D-Bus service | root PCs 2306-2312 register `com.harman.service.diagserv` | separate service surface; no certificate routine is registered as a D-Bus method |
| Install IPC reader | root PCs 2313-2317, file offsets `0x249D-0x24AD`, source/debug line 7689 | assigns the callback to `chan:reader(...)` |
| First-level callback | prototype 298, record `0x3FC23-0x3FCD7`, source/debug lines 7562-7569 | resolves `handler = msgHandler[msg[1]]` and invokes it |
| Bind routine dispatcher | root PCs 2124-2127, file offsets `0x21A9-0x21B5` | stores the routine dispatcher at `msgHandler[49]` |
| Decode routine ID | prototype 268, record `0x3A79A-0x3A88C`, source/debug lines 6876-6886, PCs 0-3 | computes the two-byte routine identifier from internal message fields 3 and 4 |
| Invoke routine | prototype 268 PCs 4-10 | looks up the computed ID and invokes the registered closure |
| Register `0xF010` | root PCs 2018-2022, file offsets `0x2001-0x2011` | maps identifier 61456 (`0xF010`) to prototype 254; PCs 2019-2022 capture `validateServiceKey` |
| Register `0xF011` | root PCs 2023-2026, file offsets `0x2015-0x2021` | maps identifier 61457 (`0xF011`) to prototype 255 |

No diagnostic-session state, SecurityAccess state, anti-theft state, PIN result, certificate precondition, or caller identity is tested in prototypes 254, 255, 268, or 298. No static `msgHandler[0x27]` binding was recovered. This negative evidence is local and bounded: an IOC, gateway, tester-state machine, or another process may reject a request before `diagserv` receives it. That upstream enforcement point is the highest-priority unresolved boundary.

## Routine `0xF010`: stage, then validate

Prototype 254 occupies serialized record `0x34D52-0x354C8`, covers source/debug lines 6249-6307, begins code at `0x34D66`, contains 124 instructions, and captures `service_cert_file` plus `validateServiceKey`.

Internally it uses two phases selected by `msg[2]`. The length and first-segment fields are read from later message slots, and supplied octets are read in a counted loop. Those operands prove segmented staging; they are intentionally not expanded into an external request recipe.

### Common entry and writable mount

- PCs 3-6, file offsets `0x34D72-0x34D7E`, source/debug line 6253, execute `mount -uw /fs/mmc0`.
- The `os.execute` return value is discarded. Failure to make the filesystem writable is not surfaced as a distinct diagnostic result.

### Phase 1: segment write

| PCs / file offsets | Source lines | Confirmed behavior |
| --- | ---: | --- |
| 7-20, `0x34D82-0x34DBA` | 6256-6261 | selects staging phase, derives the counted write length, and distinguishes the first segment from later segments |
| 22-28, `0x34DBE-0x34DD6` | 6263 | first segment opens the fixed path with `w+b`, creating it or truncating an existing certificate |
| 29-34, `0x34DDA-0x34DEE` | 6265 | later segments open the same path with `rb+` |
| 37-39, `0x34DFA-0x34E02` | 6270 | seeks to end before an append |
| 44-50, `0x34E16-0x34E2E` | 6274 | converts each supplied numeric value with `string.char` and writes it |
| 52-53, `0x34E36-0x34E3A` | 6276 | closes the file handle |
| 55-57, `0x34E42-0x34E4A` | 6278 | an open failure only logs an error |
| 58-66, `0x34E4E-0x34E6E` | 6282 | writes internal reply arguments `(49, 1, 240, 16, 1, 0)` on both the successful-write and open-failure paths |

The phase-1 reply therefore means only that the handler reached its acknowledgement site. It is **not proof** that the mount, open, every write, close, or durable-media flush succeeded. The file API return values are not accumulated, no readback occurs, and there is no certificate validation in this phase.

### Phase 2: semantic validation

| PCs / file offsets | Source lines | Confirmed behavior |
| --- | ---: | --- |
| 68-72, `0x34E76-0x34E86` | 6284-6287 | recognizes validation phase and calls captured `validateServiceKey()` |
| 75-86, `0x34E92-0x34EBE` | 6288-6289 | on true, logs validity and writes internal reply arguments `(49, 2, 240, 16, 1, 0)` |
| 87-90, `0x34EC2-0x34ECE` | 6290 | after the positive reply, executes `enum-devices`; its return status is ignored |
| 92-99, `0x34ED6-0x34EF2` | 6292 | on false, writes internal reply arguments `(49, 2, 240, 16, 0)` |
| 100-105, `0x34EF6-0x34F0A` | 6293 | after the negative reply, executes `rm -f` on the fixed certificate path |
| 106-115, `0x34F0E-0x34F2E` | 6294-6297 | logs whether that removal command returned zero |
| 116-118, `0x34F36-0x34F3E` | 6302 | logs an unknown phase selector without a result reply |
| 119-122, `0x34F42-0x34F4E` | 6306 | normal branches execute `mount -ur /fs/mmc0` before return |

Two ordering details matter:

1. the positive validation reply precedes `enum-devices`, so the reply does not prove that command ran successfully;
2. the negative validation reply precedes the handler's explicit removal, so that reply alone does not prove the file is absent. The platform evaluator normally deletes an invalid file first, but the handler does not rely on or verify that side effect before replying.

`enum-devices` is a confirmed post-validation command, but its downstream effect is not proved here. In particular, this call is not evidence of an AMS restart, development-security activation, application installation, or permission assignment.

## Routine `0xF011`: delete the persistent credential

Prototype 255 occupies serialized record `0x354C8-0x35804`, covers source/debug lines 6312-6333, begins code at `0x354DC`, contains 50 instructions, and captures only `service_cert_file`.

| PCs / file offsets | Source lines | Confirmed behavior |
| --- | ---: | --- |
| 3-6, `0x354E8-0x354F4` | 6316 | executes `mount -uw /fs/mmc0`; status is ignored |
| 7-12, `0x354F8-0x3550C` | 6319 | executes `rm -f` on the fixed service-certificate pathname |
| 13-18, `0x35510-0x35524` | 6322 | executes `ls` on the same path and retains the command result |
| 21-28, `0x35530-0x3554C` | 6324 | if the path still exists, writes internal failure arguments `(49, 1, 240, 17, 0)` |
| 33-41, `0x35560-0x35580` | 6327 | if the path is absent, writes internal success arguments `(49, 1, 240, 17, 1, 0)` |
| 45-48, `0x35590-0x3559C` | 6332 | executes `mount -ur /fs/mmc0`; status is ignored |

Unlike engineering-menu item 20, this routine targets `/etc/security/service.cert`. Item 20 targets `/fs/etfs/service.key` through a direct ActionScript file deletion. No alias or call joins those two paths.

Routine `0xF011` removes the persistent certificate file but does not call `com.harman.service.platform.evaluate_service_file`, reset `service_flags`, or emit a cleared-service-flags signal. Consequently, immediate runtime revocation is **not proved**. A subsequent clean platform-service initialization starts the flags as false and an absent file cannot reauthorize them, but an already-running HMI/platform process may retain prior in-memory or displayed state until its normal refresh/restart boundary.

## Validation is separate from transport

### `diagserv` wrapper

`validateServiceKey` is prototype 1, serialized record `0x4206-0x4567`, source/debug lines 325-342, with code at `0x421A`:

- PCs 0-5, file offsets `0x421A-0x422E`, invoke `com.harman.service.platform.evaluate_service_file`;
- PCs 6-10 test the returned table's `valid` field;
- the function returns true only when that field is true.

There is no signature algorithm, serial comparison, or certificate parser in the diagnostic routine itself. Its authority comes entirely from the platform evaluator.

### Platform evaluator

`platform_troubleshoot.lua` provides the security decision:

| Prototype | Record / lines | Confirmed responsibility |
| --- | --- | --- |
| 14 | `0x2C39-0x2DD8`, lines 446-457 | `evaluate_service_file`; calls `processservice_cert_file(true)` and returns `{valid=false}` unless processing returns true |
| 7 | `0x1848-0x1E97`, lines 255-304 | requires the file to exist; executes stock verifier `scv`; requires return code zero; reads `/fs/fram/serialnumber`; compares the parsed certificate serial; parses signed fields; applies validity checks |
| 6 | `0x13D0-0x1848`, lines 214-248 | applies date and ignition-cycle expiry; invalid state reaches deletion at PCs 64-67 |
| 5 | `0x1003-0x13D0`, lines 188-205 | resets the complete in-memory `service_flags` table, remounts MMC writable, removes the certificate at PCs 23-32, and remounts read-only |
| 2 | source/debug lines 63-127 | parses signed service fields; numeric `EngineeringMenu=1` becomes `service_flags.eng_menu=true` |
| 15 | `0x2DD8-0x3198`, lines 465-490 | registers `get_service_flags`, `test_service_flag`, and `evaluate_service_file`; PCs 15-19 (`0x2E28-0x2E38`) register the evaluator |

Prototype 7 invokes `/fs/mmc0/app/security/scv` with the active certificate and `/etc/keys/serv_cert_key.pem`. A zero verifier result is necessary but insufficient: the parsed head-unit serial must match `/fs/fram/serialnumber`, and the signed lifetime fields must remain valid. On success it sets `service_flags.valid=true` and emits `service_flags`; on verifier failure, serial mismatch, or expiry it calls prototype 5 and removes the candidate.

This proves a fail-closed semantic boundary after byte transport. It does **not** identify the OEM issuance service, certificate-request protocol, private signing key, or human approval process. Supplying arbitrary bytes to the staging routine cannot produce a valid certificate without an already authorized signer.

The separate `SERVICEKEY` removable-media path in `platform_troubleshoot.lua` functions 11/12, source/debug lines 406-427/408-422, also copies a candidate `service.cert` and enters the same platform validation path. Diagnostic routine `0xF010` is therefore a second confirmed staging transport, not a replacement for signature verification.

## Boot and lifetime behavior

Normal boot starts the diagnostic service regardless of the early tester-presence optimization:

- `boot.sh` line 321 initializes `diagservON=0`;
- lines 322-325 start `diagserv.lua` early and set the flag when `/pps/can/tester` contains `TestToolPresent::1`;
- lines 557-561 start `diagserv.lua` later when the early instance was not started.

Thus `TestToolPresent` changes launch timing, not whether `diagserv` exists during a completed normal boot. This says nothing about whether an external tester is authorized to reach certificate routines; that policy remains upstream and unknown.

## Upstream channel-7 topology and authorization boundary

The upstream trace remains static and deliberately stops short of reconstructing an externally injectable request. It proves the local transport and narrows the possible authorization owner:

```text
vehicle manufacturing diagnostics
  <-> active IOC/V850 application (hs/cmcioc.bin)
  <-> SPI multiplexed channel 7
  <-> QNX dev-ipc
  <-> Lua ipc.open(7)
  <-> diagserv RoutineControl dispatcher
  -> 0xF010 / 0xF011
```

The HBC-to-IOC direction, manufacturing-diagnostic response use, IOC RoutineControl lookup, handler preconditions, and channel-7 forwarding edge are confirmed. The external physical transport, source ECU/tester, CAN addressing, and gateway policy before the IOC dispatcher remain unresolved.

| Artifact | Exact evidence | Supported conclusion |
| --- | --- | --- |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/files/proc/boot/.script` (16,856 bytes; SHA-256 `fb0e5b3df3295951740818b081fc11f2b69a4bcc50386237b4aea7629cf17086`) | embedded argv file `0xDD8-0xDF8` invokes `/bin/sh /bin/dev-ipc.sh start`; script path begins `0xDE3` | `dev-ipc` is part of normal boot infrastructure |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/files/bin/dev-ipc.sh` (3,551 bytes; SHA-256 `52f108e0277cc9f3cf396070c9264cc2983d9af318869981816f2d050b953a1a`) | lines 73-89 configure SPI3; line 118 launches `dev-ipc` with 27 channels | channel 7 is one endpoint of a generic SPI multiplexor |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/files/bin/dev-ipc` (75,930 bytes; SHA-256 `ce9be22bf8d820e5e02e215267ead438a56e1c83f471edca2b84e6be56b90a57`) | endpoint factory `0x109764-0x109A64` creates `/dev/%s/ch%d` and stores the channel ID; common write `0x108EEC-0x109140` emits length, channel, then opaque payload; common read `0x1095A0-0x109740` dequeues payload | `dev-ipc` multiplexes opaque bytes; the audited creation/read/write paths contain no SID, RID, diagnostic-session, or SecurityAccess decision |
| `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/factory_cleanup_support.lua` (6,704 bytes; SHA-256 `df2ba58786000a42f6167a4cd8b3ea5e8f7c93483097618a05337c94a5ae2ddb`) | lines 153-160 form a manufacturing RoutineControl response; lines 161-162 open and write IPC channel 7; line 180 invokes IOC cleanup | channel 7 carries at least manufacturing-diagnostic response traffic toward vehicle CAN |
| `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/ioc_cleanup.sh` (1,487 bytes; SHA-256 `57a90f7f447bd22cc614656505f37fb85017b4fdb06bbf01aae98bcecb9a29e4`) | lines 4-6 identify V850 EEPROM reset; line 20 opens channel 7 read/write; lines 27-56 implement a V850 request/reply loop | channel 7 is bidirectional between HBC and IOC/V850 |
| `analysis_ra4_18.45.01/work/installer_iso/etc/manifest.lua` (9,288 bytes; SHA-256 `104d18836f41919f1f789110697eebc5e6deee998de79fb5a4c0af35a042770f`) and `analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/update/installerhelper.lua` (9,560 bytes; SHA-256 `0a005395ce53dc29a16cdc3c80c0dd95033ea5f38e3adc7f981054d199cb51c8`) | manifest lines 14-18 identify NA/VP4/MY17; helper prototype 17, serialized file `0x2300-0x254C`, selects `hs` for VP4/MY17 | the active IOC family for this image is `hs`, not an arbitrary V850 variant |
| `analysis_ra4_18.45.01/work/primary_iso/usr/share/V850/hs/cmcioc.bin` (458,752 bytes; SHA-256 `c7bf247bfdb10b5dfda2802df1210671f6a1872140cdeebc014c109a9c77e012`) | flat mapping is runtime VA = file offset + `0x10000`; RoutineControl list file `0x6CB41`; `0xF010` and `0xF011` entries file `0x6CB89`/`0x6CB8C`; handler records file `0x6C978`/`0x6C982`; handlers file `0x5D730`/`0x5D7D0` | direct IOC dispatcher, precondition, handler, and channel-7 forwarding control flow is recoverable |

Negative localization is also material:

- `hmiGateway` has no `/dev/ipc` string; its `com.harman.service.diagserv` name occurs in a broad D-Bus service catalog and does not establish channel-7 ownership.
- `canservice` owns `/pps/can/tester` and `TestToolPresent`, but contains no static `/dev/ipc/ch7` edge. Its unrelated seed-named strings are not evidence of a SecurityAccess decision without control flow.
- no session/security predicate exists in the traced `diagserv.lua` F010/F011/dispatcher/IPC callbacks, and none appears in the audited generic `dev-ipc` transport paths.

The V850 image is a flat application mapped at file offset + `0x10000`: reset vector file `0x0`/VA `0x10000` branches to VA `0x77326` (file `0x67326`), while independent in-image pointers map the build string and valid handler code under the same base. Python 3.12.14 with `pypcode` 4.0.0 and language `V850:LE:32:default` supplied static decoding; no target code was executed. No Ghidra, rizin/radare2, Binary Ninja, IDA, or V850-aware objdump was found locally, and nothing was installed.

The exact pre-Lua path is now:

1. Dispatcher helper file `0x457CC`/VA `0x557CC` maps the request service through the SID table at file `0x6C2FE`; the RoutineControl entry selects descriptor 8 at file `0x6C384`.
2. Descriptor 8 selects a three-byte key and the bounded record-index range. Binary search file `0x456F4-0x457C6` resolves the list at file `0x6CB41`; entries `0x6CB89` and `0x6CB8C` select handler records `0x6C978` and `0x6C982`.
3. Before lookup, dispatcher file `0x45896-0x458AC` compares descriptor 8's allowed session mask with the current low-three-bit IOC diagnostic state at `GP-0x2ED4`. Initialization file `0x45290-0x452B8`, reached from diagnostic init file `0x45CBA`, sets the default session state to mask 1; descriptor 8 allows mask 6. Default state therefore fails before either handler. **An IOC diagnostic-session transition is confirmed as mandatory.**
4. After lookup, file `0x45978-0x45990` repeats the per-record session check. Helper file `0x4537C-0x453C4` also checks the next two-bit authorization/security state and returns negative-response code `0x33` on a generic security-state mismatch. Both routine records use combined mask byte `0x1E`: session mask 6 and security mask 3. The initialized security state mask 1 intersects allowed mask 3, so these routines are not proved to require a SecurityAccess unlock even though the generic gate exists.
5. Common-condition file `0x45962-0x45976` checks record condition mask 1 against `GP-0x2EE8` and returns `0x22` on failure. Each routine handler also calls state getter VA `0x54228`/file `0x44228` and requires state 4; otherwise it returns `0x33` at handler files `0x5D7B8`/`0x5D80E`.
6. F010/F011 handlers VA `0x6D730`/`0x6D7D0` (file `0x5D730`/`0x5D7D0`) call common forwarder VA `0x52FB0`/file `0x42FB0`. At file `0x430E2-0x430EA`, the forwarder loads the IPC handle, selects channel 7, passes the computed length, and calls generic IPC send VA `0x37210`/file `0x27210`.

The state-4 backslice proves a second, independent IOC-local authentication gate:

- a separate proprietary diagnostic handler record at file `0x6C73E` points to wrapper VA `0x6C714`/file `0x5C714`, which calls the authorization state machine VA `0x53B24`/file `0x43B24`;
- initialization VA `0x53EF8`/file `0x43EF8`, called during diagnostic/IPC setup from file `0x42E42`, loads persistent state and initializes the runtime state machine;
- in state 1, code file `0x44002-0x4408E` validates the bounded request shape, exposes a four-byte challenge from persistent state, and moves to state 2 unless a previously provisioned, nonzero allowance restores state 4;
- in state 2, code file `0x440A0-0x44130` validates a four-byte response through comparison routine VA `0x77434`/file `0x67434`. Equality moves to state 4. Mismatch increments a retry count; the third failure enters state 3, persists lockout state, sets a delay, and returns `0x36`; earlier failures return `0x35`. Delay expiry at file `0x441E8-0x4421A` clears the persisted lockout flag and returns to state 1;
- the persistent allowance is not a free local shortcut: mutator VA `0x54180`/file `0x44180` is reached from the proprietary handler only after state 4 and request validation, persists changes, and a separate system event decrements an existing nonzero allowance.

No challenge value, response value, comparison secret, proprietary sub-identifier, or request framing is reproduced. The business owner and legitimate responder for this challenge remain unknown, and nothing in the backslice connects it to the factory anti-theft PIN.

This proves `IOC diagnostic-session gate -> IOC challenge/response authorization state 4 -> condition/security checks -> F010/F011 handlers -> channel 7 -> HBC diagserv`. The actual owner-authorized session-change and challenge-response workflow, tool identity, CAN addressing, and request framing remain unknown and are intentionally not reconstructed here as an injection procedure. An external gateway can also impose additional authorization before this IOC path.

### Exhaustive authorization-state and allowance census

Runtime authorization state is `GP-0x7B38`, RAM `0x03FF75D4`. Its complete direct-use census is:

| Kind | VAs (file offsets are VA minus `0x10000`) |
| --- | --- |
| reads | `0x52E70`, `0x53B9A`, `0x53BF2`, `0x53C5A`, `0x53CC6`, `0x53CF0`, `0x53D2A`, `0x53D64`, `0x53D9E`, `0x53DDA`, `0x53FFA`, `0x5422A` |
| writes | state 1 at `0x53DE4`; state 4 at `0x54018`; state 3 at `0x5402E`; state 2 at `0x5408E`; state 4 at `0x540D4`; state 3 at `0x540F6`; state 1 at `0x5421A` |

Getter VA/file `0x54228/0x44228` has exactly 12 direct callsites: VAs `0x6C394`, `0x6C5CA`, `0x6C612`, `0x6D202`, `0x6D430`, `0x6D4AC`, `0x6D592`, `0x6D73C`, `0x6D7D6`, `0x6D8FE`, `0x6D9B6`, and `0x70FCE`. All are authorization reads in diagnostic-handler surfaces. No getter function-pointer reference or absolute pointer to the state RAM was found.

Persistent allowance slot `0x11A` is shadowed at `GP-0x7B34`, RAM `0x03FF75D8`. Its only exact slot uses are:

- initialization read at VA/file `0x53F30/0x43F30`, followed by erased-state detection and a finite default at `0x53F3E..0x53F5C`;
- state-4-gated read returned through the proprietary handler at `0x53DAA/0x43DAA`;
- persistence from the state-4-gated setter at `0x5419A/0x4419A`;
- persistence from a separate system-event decrement at `0x541CC/0x441CC`.

The embedded default is intentionally omitted. While in state 1, the state machine reads this allowance at `0x5400E/0x4400E`; nonzero restores runtime state 4 at `0x54018/0x44018`, while exhausted state follows the challenge/lockout path. This is direct behavioral proof of a finite factory/manufacturing authorization allowance, although the image supplies no trustworthy OEM symbol for it.

Allowance mutator VA/file `0x54180/0x44180` has exactly two direct callers and no function-pointer references:

1. Direct set at `0x53BBC/0x43BBC`, reachable only after request validation and an explicit pre-existing state-4 check at `0x53B92..0x53BA0`; storage/persistence is `0x54192..0x541A6`.
2. System-event consumption at `0x5136E/0x4136E`, which selects only the decrement behavior; eligibility and persistence are `0x541AC..0x541D8`.

There is therefore no unauthenticated allowance provisioner in this image: the only setter is already state-4-gated, while the other caller only consumes it.

Challenge/comparison slots have similarly closed exact-use sets. Slot `0x11B` is written only through the state-4-gated path at `0x53C28`, initialized/read at `0x53F60/0x53F76`, and supplied to the state machine at `0x54042`. Slot `0x11F` is written only through the state-4-gated path at `0x53C94`, initialized/read at `0x53F8C/0x53FA2`, and read by the comparison path at `0x540AC` before generic comparison at `0x540C8`. No anti-theft, HBC, service-certificate, or Developer Mode routine directly writes either slot. Values are intentionally neither inspected nor reproduced.

### Allowance-decrement event and network origin

The allowance is decremented by a distinct received system-state cycle event, not PIN success. Trigger flag `GP-0x1495` has one writer `0x500D8/0x400D8`, one reader `0x5135E/0x4135E`, and clear `0x51366/0x41366`. Producer `0x5004C/0x4004C`:

1. reads the selected raw ignition-state field through getter `0x4A694/0x3A694`;
2. resets or starts its measurement according to the selected low-bit state at `0x50054..0x500A0`;
3. after a sustained interval, increments persistent cycle counter `GP-0x1498` at `0x500CC..0x500D2`;
4. raises the trigger at `0x500D8`.

Consumer `0x51330/0x41330` reads/clears the trigger, calls the allowance mutator at `0x5136E`, and persists the cycle counter through slot `0x2D5` at `0x51372..0x5137E`.

The two selector inputs are confirmed table-driven network-receive destinations, not arbitrary globals. Primary destination, width, and callback tables begin at file/VA `0x6A608/0x7A608`, `0x6A468/0x7A468`, and `0x6AC88/0x7AC88`. Table index 46 targets `GP-0x2AE0` through destination pointer file `0x6A6C0`, two-byte width metadata `0x6A496`, and callback VA/file `0x59D48/0x49D48`. Index 176 targets `GP-0x2AE4` through pointer `0x6A8C8`, width `0x6A518`, and callback `0x5494C/0x4494C`.

Generic updater `0x68548/0x58548` invokes the indexed callback at `0x685DA`, then copies the received bytes into the indexed destination at `0x68630..0x68654`. Both callbacks read multiple packed fields, confirming received status words. Getter `0x4A694` selects the low three bits of `GP-0x2AE4` at `0x4A69E` when persistent variant selector `GP-0x2AF3` is zero, or the low three bits of `GP-0x2AE0` at `0x4A6B2` otherwise. Initialization at `0x4549E..0x454DE` derives that binary selector from persistent slot `0x232`; the product/network meaning of its two values is not named.

The field's ignition semantics are confirmed end to end. The selected value is stored as raw ignition state at `GP-0x7E54` by `0x2C070..0x2C076`, normalized through `0x2C8D0`, copied to the HBC record by `0x2AB60`, and published from the record beginning at `0x2AD6C`. Derived power mode remains a separate field: `GP-0x7E4E` is forwarded at `0x2C5A4..0x2C5A8` and copied into its own HBC record field at `0x2AE36..0x2AE3A`.

The downstream consumer `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/onoff/main.lua` is 66,272 bytes, SHA-256 `41c0f3f2709c49d4a4f9b150b8c08c735515a9c50bbfbc2e4c36664d6466e698`. Its root debug lines 151-157 map `ignState` values 0-5 to `lock`, `off`, `accessory`, `on`, `start`, and `remote`; lines 169-176 independently map `powerModeState`. Prototype 0.21, debug lines 820-850, converts and emits those two record fields separately. The producer's active value 4 is therefore the raw `start` ignition state, not derived `full_operation` power mode. This closes the state-field classification. The upstream bus, source ECU, literal vendor message/signal name, product-variant meaning, and scheduler timebase remain unknown, so the interval cannot be translated into wall-clock time.

### One-way relationship to factory anti-theft

A manufacturing/write handler at VA/file `0x6C388/0x5C388` (external identifier omitted) calls the authorization getter at `0x6C394`, requires state 4 at `0x6C39A..0x6C39C`, validates a replacement at `0x6C39E..0x6C41C`, persists it through helper call `0x6C42C`, and copies it into the live factory anti-theft comparator at `0x6C446..0x6C452`. Anti-theft initialization VA/file `0x2524C/0x1524C` loads the same persistent field through helper call `0x252E4/0x152E4`.

This proves only:

```text
proprietary diagnostic authorization state 4
  -> permits factory anti-theft comparator provisioning
```

The reverse is absent. PIN-decision VA/file `0x25658/0x15658` uses separate anti-theft state `GP-0x229A`, RAM `0x03FFCE72`. Its equality branch `0x256AE..0x256C2` changes only anti-theft state/publication flags, and publisher `0x2AD6C/0x1AD6C` only publishes that state. The channel-2 registrar, dispatcher, PIN-decision branch, and publisher contain zero references to proprietary state `GP-0x7B38`, allowance `GP-0x7B34`, getter `0x54228`, or mutator `0x54180`.

Combined with the HBC/HMI callback census, the bounded result is:

```text
PIN success -/-> state 4 or slot 0x11A allowance
PIN success -/-> service-certificate authorization
PIN success -/-> AMS_DEVELOPMENT
PIN success -/-> developer credentials
```

The PIN-success callback instead reaches only the separately documented destructive `xletsReturnToNew` factory-application restoration/reset path. Full details are cross-recorded in `reports/anti_theft_auth_flow.md`.

The platform side is also boot-coupled:

- `platform_troubleshoot.lua` prototype 15 observes `com.harman.service.authenticationService` ownership at source/debug lines 480-483 and initiates certificate evaluation when that service becomes available;
- `boot.sh` lines 648-649 launch `authenticationService -k /etc/system/config/authenticationServiceKeyFile.json`;
- platform root source/debug lines 29-45 initialize `service_flags.valid=false` and `service_flags.eng_menu=false` before any certificate succeeds.

The resulting persisted-state model is:

```text
IOC-accepted diagnostic request (session + challenge authorization required)
  -> diagserv 0xF010 stages /etc/security/service.cert
  -> explicit validation phase
  -> platform signature + HU-serial + lifetime validation
  -> valid signed service flags
  -> EngineeringMenu=1 can expose the HMI Service entry
  -> a separate user action, item 19, can toggle /fs/etfs/AMS_DEVELOPMENT
  -> a later jvm.sh invocation selects the corresponding AMS security.jar

diagserv 0xF011
  -> removes only /etc/security/service.cert
  -> does not directly clear live platform/HMI state
  -> next clean platform initialization begins unauthorized when the file is absent
```

The factory anti-theft PIN path is not part of this chain. No PIN input, PIN-success callback, retry counter, anti-theft state, or `checkAntiTheftPIN` term is consumed by the traced IOC dispatcher/handlers, channel-7 transport, or Lua certificate routines. The unresolved IOC state-4 prerequisite must not be relabeled as factory-PIN state without dataflow evidence.

## Atomicity, interruption, and rollback properties

### Confirmed non-atomic behavior

Prototypes 254 and 255 contain no temporary-file, rename, `fsync`, backup, journal, checksum, or transactional-commit step.

- The first `0xF010` segment uses `w+b`, so it truncates any existing valid certificate before the replacement is complete.
- Later segments append in place. Power loss, process death, a missing segment, or a short write can leave a partial candidate at the authoritative pathname.
- The phase-1 acknowledgement is unconditional with respect to the file-open result and does not prove durable data.
- Mount, write, close, `enum-devices`, and final read-only-remount results are not propagated in the success reply.
- The positive validation reply occurs before `enum-devices`; the negative validation reply occurs before `diagserv`'s explicit removal.
- `0xF011` deletes in place and has no recoverable backup. Its absence test is stronger than trusting `rm -f`, but its success reply still precedes the final read-only remount.

The normal invalid-certificate path is fail-closed: platform prototype 5 resets flags and removes an invalid or incomplete candidate. A later boot with no valid certificate initializes service flags to false. This limits authorization persistence, but it does not make the replacement operation atomic or preserve the previous valid credential.

### Runtime rollback qualification

`0xF011` is a persistent-file rollback mechanism, not a proved immediate session revocation:

- it removes the authoritative file and confirms pathname absence;
- it does not invoke the platform evaluator or mutate its captured `service_flags` table;
- it does not notify the HMI;
- it does not delete `/fs/etfs/AMS_DEVELOPMENT` or restart AMS;
- a clean platform/HMI restart or equivalent explicit state refresh is still required for a fully evidenced live-state rollback.

Any future safe implementation must preserve a known-good credential until a replacement is completely written and independently validated, verify the read-only remount, and define a controlled refresh/restart boundary. The stock in-place transport by itself does not provide those guarantees.

## Explicit unknowns and next evidence targets

1. **Upstream diagnostic authorization:** IOC-owned session gating, proprietary challenge/response state 4 with retry/lockout, finite allowance ownership, raw-ignition-state allowance consumption, generic security-state gating, routine handlers, and channel-7 forwarding are confirmed. The remaining task is to identify the legitimate external session transition and challenge responder/issuer, resolve `GP-0x2EE8`, name the upstream ignition message/source ECU and variant selector, and determine whether an external gateway adds authenticated-tool or SecurityAccess policy.
2. **Credential issuance:** Which owner-authorized OEM workflow creates a service certificate for a specific head-unit serial, and which protected service holds the corresponding private signing key?
3. **External framing:** The local bytecode proves internal message fields and replies, but the external transport, encapsulation, addressing, and negative-response behavior have not been traced and are intentionally not reconstructed here as an injection procedure.
4. **Live revocation:** What supported platform/HMI action clears already-published service flags immediately after `0xF011`, without relying on a full head-unit reboot?
5. **`enum-devices` effect:** Why is it invoked after successful validation, and is any completion signal observed by the diagnostic gateway? Its return code is ignored locally.
6. **Mount/write failures:** How are ignored `os.execute` and file-I/O failures surfaced elsewhere, if at all? Static Lua control flow contains no retry or recovery transaction.
7. **Service-to-developer boundary:** A valid certificate can expose the Service menu, after which item 19 can change `AMS_DEVELOPMENT`; no evidence here connects certificate issuance to `developerId`, `developerToken`, application signing, or AMS permission assignment.
8. **Anti-theft relationship:** A state-4-gated manufacturing handler can provision the anti-theft comparator, proving diagnostic authorization is upstream of that protected factory operation. The reverse edge is confirmed absent in the exhaustive direct state/getter/mutator and channel-2 PIN-success xrefs: PIN success does not create state 4, replenish the allowance, authorize the service certificate, or touch the development marker/token.

## Bottom line

RA4 18.45.01 has a concrete, stock, reversible-at-persistence service-certificate transport. `diagserv.lua` owns the diagnostic create/append/validate and delete operations for `/etc/security/service.cert`; `platform_troubleshoot.lua` owns signature, head-unit binding, lifetime checks, service-flag assignment, and invalid-certificate deletion. This provides a legitimate architectural route for an owner-authorized service credential while preserving cryptographic verification.

It is not yet safe to use. The path is proved from the IOC's required diagnostic session and proprietary challenge/response authorization state through condition/security checks and channel 7 to the Lua handlers. State 4 also gates factory anti-theft comparator provisioning, but owner PIN success is proved not to generate that state or its allowance. The legitimate external workflow and credential authority remain unknown; staging is non-atomic, phase-1 acknowledgements overstate success, and deletion does not prove immediate runtime revocation. No part of this trace authorizes bypassing the anti-theft PIN, deriving or replaying the IOC challenge response, forging a service certificate, weakening AMS security, or modifying stock firmware.
