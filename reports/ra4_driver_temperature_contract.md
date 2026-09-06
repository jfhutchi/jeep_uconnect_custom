# RA4 read-only driver-temperature contract

Updated 2026-09-06. Scope: RA4 18.45.01, ROV HMI, automatic front climate,
non-MP4 conversion branch. Static inspection only; no vendor code executed,
radio connection, subscription sent, PPS opened, vehicle command or image edit.
The publisher module has startup writes and command handlers: **do not load or
execute it to test the read-only findings**.

## Result and confidence

**CONFIRMED:** the stock high-level value is a **string-valued climate setpoint**,
not the prototype's integer-Celsius field or a measured cabin-temperature sensor.
`FT_DRV_ATC_TEMP` flows through a units-dependent filter, physical-side mapping,
`zone` service event, ModuleLink cache and `IHvac.zoneTemp(String): String`.
The concrete client and publisher agree on `zone`, `controls`, `temp` and the
front-left/right names. The native gateway's HVAC destination/service mapping is
also established. No standalone application's access permission is established.

**HIGH:** the corresponding endpoints are the intended end-to-end stock route.
The complete native subscription/callback marshalling and delivery ordering are
not traced here. Matching endpoints plus a destination mapping are not a live
delivery test or proof of a reliable freshness protocol.

**INFERRED / proposed application policy:** model numeric, low-limit, high-limit,
unavailable and stale states separately. Combine temperature with verified units,
automatic-climate capability and driver-side mapping before presenting it.
Keep writes disabled. A change event alone is not evidence of current validity.

## Reproduction and address conventions

All inputs are ignored local artifacts under `analysis_ra4_18.45.01/work/`.
Do not copy them to tracked paths. Abbreviations used below:

| Input | Relative path below work | SHA-256 |
| --- | --- | --- |
| H: HVAC publisher | `hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/vehicle/hvac.lua` | `3ddadef2296acb475b307893b9a61fa8c7324dce336dcb3baaef1ff89a5b0b50` |
| S: service wrapper | `hidden_hbc_ifs/segment_001a0000/files/usr/bin/service.lua` | `1460473d791f70a8fbf5e47c24d3b81959d1164de6c6ad2479a6d89513c4f1be` |
| M: ROV client | `primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/MainSupplement.swf` | `e9d796ea4b4c83ed518bfe3b3c341e54e510a1ae0f78ebbffbd655b7c36a3258` |
| V: HVAC screen | `primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/skins/default/swf/HVACHomeScreen.swf` | `cf894eb59e31b7e7b426dfc2eeb2ab9fc3bd14c90082408e8367e54a404f1f18` |
| G: native gateway | `hidden_hbc_ifs/segment_001a0000/files/bin/hmiGateway` | `8d7fe8789bb012a66fbebd1bd44eefa506c672a5d70c90fbf92b3a5a6f01ec82` |

H is 56,263 bytes / 37 prototypes; S is 12,970 bytes / 26 prototypes.
M is 1,407,783 bytes / 15,157 methods in ABC 0, ABC FWS base `0x264EB`.
V has 424 methods in ABC 0, base `0x1510F`. G is 153,124 bytes, ARM ELF32 LE.
Lua addresses are original chunk **file offsets**, with preorder prototype IDs.
SWF addresses are **reconstructed uncompressed FWS offsets**, not compressed-file
offsets or runtime addresses. Gateway addresses below are **VAs**; its cited text
and literals have file offset = VA minus `0x100000`.

Use the original read-only tools, replacing H/M/V with the paths above:

```text
python -m analysis_tools.lua51_inspect H --function 10 --count 100
python -m analysis_tools.lua51_inspect H --function 23 --start 200 --count 60
python -m analysis_tools.lua51_inspect H --function 7 --count 30
python -m analysis_tools.swf_abc_inspect M --method 2596 --count 180
python -m analysis_tools.swf_abc_inspect M --method 2598 --start 0x276BE0 --count 160
python -m analysis_tools.swf_abc_inspect M --method 2582 --count 120
python -m analysis_tools.swf_abc_inspect V --method 26 --count 140
```

Tools print input hashes. Only original scripts, synthetic fixtures and derived
metadata belong in git; no complete disassemblies or reconstructed vendor source.
Parser semantics reference the primary [Lua 5.1 undumper](https://www.lua.org/source/5.1/lundump.c.html),
[Lua instruction definitions](https://www.lua.org/source/5.1/lopcodes.h.html), and
[Adobe AVM2 specification, author-issued document mirrored by Burgerlib](https://burgerlib.readthedocs.io/en/latest/avm2overview.pdf).
These describe file formats, not Harman's contract. The tools are not VM verifiers.

## Publisher path: direct evidence

```text
comfortstat FT_DRV_ATC_TEMP (string)
  -> AutoCtrl + changed-value + invalid-sentinel gates
  -> rangeCheckTempValue + PersonalConfig temperatureUnits
  -> VC_LHD_RHD physical-side mapping
  -> updateProperty(zone, temp, value)
  -> service.emit(HVAC handle, zone, {zone, controls:{temp}})
  -> JSON encode / svcipc.emit
  ... native callback marshalling not fully traced ...
  -> ModuleLink zone envelope -> cached string -> HvacEvent -> IHvac.zoneTemp
```

| Edge | CONFIRMED evidence |
| --- | --- |
| Publisher identity | H f36 loads `com.harman.service.HVAC` at `0xC017`, calls service registration at `0xC01F`; handle saved at `0xC027`. |
| PPS status source | H f36 `0xC0B3` loads `/pps/can/comfortstat?wait,delta`; mode is `rc`. This is code evidence, not a performed open. |
| Notification processing | H f36 registers `HVACstatNotification` at `0xC193/0xC197`. H f32 `0xBB2C..0xBB48` calls `processHVACstat`, rearms `ppsHVACstatRecvObj.notify`, and loops if notified immediately. |
| Raw attribute dispatch/cache | H f26 `0x9EC1..0x9F2D` iterates status pairs. At `0x9EED` it calls `checkFrontproperties(attr,value)` **before** updating `canSignalsFront[attr]` at `0x9EF5`. |
| Front automatic selection | H f23 `0x7BE8..0x7C14`: `AutoCtrl == true`, exact attr `FT_DRV_ATC_TEMP`, changed value, and value not string `127`. |
| Units/conversion | H f23 `0x7C1C..0x7C58`: units must exist; MP4 uses a different function. Non-MP4 calls f10 at `0x7C54`. Stores converted result in `driverTemp` at `0x7C5C`. |
| Driver-side choice | H f23 `0x7C68..0x7CA0`: `VC_LHD_RHD == "2"` selects `frontRight` (call `0x7C88`); other values select `frontLeft` (call `0x7CA0`). Do not equate the fallback branch with positively verified left-hand drive. |
| Single-front mirror | H f23 `0x7CA4..0x7CBC`: if `Dual_Front == false`, also saves `zones.front.temp`; this assignment itself emits no extra event. |
| Deferred raw value | H f23 `0x7CC4/0x7CCC` stores `rawDriverTemp` if conversion yields nil or units are missing. |
| Changed published value | H f7 `0x1725..0x1765`: compares `zones[zone][name]`; only a different value updates the cache and emits `zone` with `{zone, controls:{name:value}}` at `0x1761`. |
| Service emit | H f3 `0x14C5..0x14D9` passes HVAC handle, signal and params to `service.emit`. S f10 `0x12C7..0x12D3` encodes params, then calls `svcipc.emit` at `0x12EB`. |

The initial snapshot timer path is H f13, code `0x23B2`. Automatic driver selection
at `0x23DA..0x23F6` uses the same attr/sentinel, and `0x23FE..0x2442` gates units
and conversion. The side-specific initial emits are `0x2472` / `0x2496`.
Do not assume this direct initial emit has the same cache-update behavior as f7.

## Value and units: exact filter, not supported adjustment limits

H f10 code `0x1E5C..0x1F50`, debug lines 282-309, initializes the return value
from the **original input string**. The numeric helper f4 at `0x1571` adds zero
for comparisons; it does not replace the preserved return string. There is no
Fahrenheit-to-Celsius conversion or integer-only check in this function.

Ordered decisions for **non-MP4 automatic** input:

| Input / units | Result | Evidence |
| --- | --- | --- |
| Exact `"0"` | `"lo"`, before units checks | H `0x1E60..0x1E6C` |
| Exact `"126"` | `"hi"`, before units checks | H `0x1E70..0x1E7C` |
| `METRIC`, numeric >45 | nil; defer/suppress | H `0x1E80..0x1EA8` |
| `METRIC`, numeric >30 and <=45 | `"hi"` | H `0x1EAC..0x1EC4` |
| `METRIC`, numeric <14 | `"lo"` | H `0x1EC8..0x1EE0` |
| `METRIC`, 14..30 inclusive | Original string, including fractional text | Remaining metric path to `0x1F4C` |
| `US`, numeric <45 | nil; defer/suppress | H `0x1EE4..0x1F0C` |
| `US`, numeric >84 | `"hi"` | H `0x1F10..0x1F28` |
| `US`, numeric 45..<60 | `"lo"` | H `0x1F2C..0x1F44` |
| `US`, 60..84 inclusive | Original string | Remaining US path to `0x1F4C` |
| Other units | nil, except the early `0` / `126` cases | H `0x1F48` |
| Exact `"127"` | Dropped upstream; do not apply the numeric filter to it | H `0x7C10..0x7C14` |

**HIGH:** `METRIC` denotes Celsius and `US` Fahrenheit; the stock UI's corresponding
numeric scale supports this interpretation. These filter ranges are **not** proof
of all supported physical setpoints, increments or command bounds. Malformed
numeric text is not safely handled by the stock helper; a new adapter must reject
it, not reproduce the arithmetic coercion blindly.

H f35 `0xBD93..0xBDB3` requests PersonalConfig `temperatureUnits` and `ready`;
`0xBDB7..0xBDDB` subscribes to both. H f29 `0xAF60..0xAF74` maps a
`temperatureUnits` notification to `US_METRIC`; `0xAF78..0xAFB8` checks readiness,
changed units and automatic climate. For non-MP4, `0xB0EC..0xB170` re-filters a
cached raw driver value, publishes it by side, and clears that raw cache.
This is not proof that every units change immediately republishes every value.
Readiness shapes differ locally: f35 tests initial `ready` against Boolean true
at `0xBDF7`; f29's ready notification tests string `"true"`. Preserve this
distinction until the PersonalConfig producer/serialization path is traced.

V method 82 (`0x23C49`) distinguishes automatic from manual climate at `0x23C61`.
For non-MP4 automatic climate it checks `temperatureUnits` against `US` / `us` at
`0x23D6D..0x23D86` and selects slider endpoints 59/85 versus 13/31 at
`0x23D8F..0x23DB1`, consistent with LO/HI endpoints surrounding the numeric ranges.
The publisher filter itself only accepts uppercase unit names. Do not silently
assume the screen's permissive case handling is the publisher contract.

## Capabilities and physical zones

H f28 derives `AutoCtrl` and `Dual_Front` from string `VC_HVAC_Config`:

| Configuration | AutoCtrl | Dual_Front | Assignment evidence |
| --- | --- | --- | --- |
| `0`, `1` | false | false | H `0xA229/0xA239`, `0xA259/0xA269` |
| `2` | true | false | H `0xA289/0xA299` |
| `3` | false | true | H `0xA2B9/0xA2C9` |
| `4` | true | true | H `0xA2E9/0xA2F9` |
| `5` | true | true | H `0xA359/0xA361`; rear configuration has extra variant checks |
| `6` | false | true | H `0xA381/0xA391` |

These are internal capability flags, not a complete externally published capability
schema. The current vehicle's values were not observed. H f27 `0xA0C5..0xA0E5`
copies a configuration table to `supportedHVACzones`. Tables use string `yes`/`no`,
not booleans. The automatic single-front table has `front=yes` and side zones=no
at H `0x566..0x576`; automatic dual-front has side zones=yes at `0x5A6/0x5AA`.

H f8 (`getZoneProperties`, binding `0x64E`) returns a `zones` collection of
`{zone, controls}` for requested supported zones. H f9 (`getControlProperties`,
binding `0x65E`) filters requested controls and returns `{zone, controls}`.
Unsupported zones yield no matching controls, not a temperature of zero.

V method 26 checks `hasDualFrontZones` / `hasRightHandDrive` at `0x21086/0x21094`
before displaying the left control. It reads the left cache through IHvac at
`0x210F4` and tests `hvacSystemAutomatic` at `0x21103`. Manual climate takes a
different display scale. **Do not label a manual MTC value Celsius/Fahrenheit.**

## ModuleLink and native bridge

| Stage | CONFIRMED evidence |
| --- | --- |
| Interface | M method 2478, method-info `0x1E1ADD`: `IHvac.zoneTemp(String): String`. Concrete method 2582 code `0x2759F4`. |
| Destination | M cinit `0x273B0F/0x273B13` assigns `HVAC`; `0x273C4D/0x273C51` assigns signal `zone`; `0x273CC5/0x273CC9` assigns `temp`. |
| Subscription | M connected method 2585 calls `sendSubscribe(zone)` at `0x2760B7`; also subscribes to `temp` at `0x2760F3`. Method 2594 `0x276433..0x27645A` builds Type=Subscribe, Dest=HVAC, Signal=<name> and passes the string to the existing client. No subscription was sent in this research. |
| Gateway service mapping | G `0x108D8C` loads the literal at `0x120C5C` (`HVAC`), calls comparison helper `0x10E24C` at `0x108D94`, then branches on nonzero at `0x108D9C` to `0x109F1C`. Helper's matched-length/equal path returns 1 at `0x10E2B8`. |
| Service/object names | G `0x109F1C` loads `com.harman.service.HVAC` (`0x120C30`) into the selected output; `0x109F2C` loads `/com/harman/service/HVAC` (`0x120C48`). Full callback marshalling remains outside this trace. |
| Client receive registration | M constructor 2535 registers `hvacMessageHandler` with ConnectionEvent.HVAC at `0x2742BC/0x2742BF`. |
| Event envelope | M 2596 `0x2765CF..0x2765E0` passes received `data.zone.zone` and `data.zone.controls` to method 2598. |
| Snapshot/reply envelope | M 2596 `0x276582..0x27658A` handles `getZoneProperties.zones`; `0x2765A4..0x2765B5` handles `getControlProperties.zone/controls`. M 2597 iterates zones and calls the same control handler. |
| Temperature field | M 2598 `0x276BE3..0x276BFD` tests own `temp` property and compares against `SNA`. |
| Cache and side event | For frontLeft, M `0x276C53/0x276C59` reads/saves temp and `0x276C68..0x276C6F` dispatches HVAC_ZONE_FRONT_LEFT_TEMP. frontRight equivalents `0x276C84/0x276C8A`, `0x276C99..0x276CA0`. |
| Event names | M HvacEvent cinit: `hvacZoneTemp` at `0x2E5A23`, `hvacZoneFrontLeftTemp` at `0x2E5A37`, `hvacZoneFrontRightTemp` at `0x2E5A4B`. |
| Consumer | M HVACManager method 2043 reads `Peripheral.hvac.zoneTemp(ZONE_FRONT_LEFT)` at `0x26DA34`, compares prior cache and updates it at `0x26DA4B`. V screen method 26 reads the same getter at `0x210F4`. |

`getZoneTemp()` is a refresh request, **not** the getter returning the value.
M 2581 requests `temp` for frontLeft/frontRight/rear via `getControlValue` at
`0x2759A4/0x2759B4/0x2759C4`. M 2589 builds `getControlProperties` with `zone`
and a `controls` array. The getter `zoneTemp(zone)` returns cached strings;
its unsupported-zone fallback is **`lo`** at `0x275A2E`, not an error. An adapter
must validate the zone before relying on this getter. `ZONE_FRONT` routes to the
front-right cache in this getter; do not use it as a generic driver alias.

## Validity and freshness: hazards proved by the trace

1. PPS sentinel `127` is suppressed. f26 still caches the raw status afterward.
   No explicit invalidation accompanies that input in the traced event path.
2. f7 only emits when the **published** value changes. Normal stable setpoints can
   legitimately produce no events for much longer than the mock's 2 seconds.
3. The client `SNA` branch skips cache assignment and side events but still reaches
   the generic temperature event at M `0x276D21..0x276D30`. Therefore even a generic
   temperature notification can cause a consumer to read the old cached value.
4. The side and generic events are constructed with only the event-type argument.
   They do not carry a newly sampled temperature, sample timestamp or sequence.
5. The client defines `TEMP_UNKNOWN` as `--` at M `0x2739D7..0x2739DA`; its presence
   does not make every missing/suppressed update turn into that sentinel.
6. Service available false changes an availability flag at M `0x276523..0x276535`.
   This branch alone does not clear the temperature caches.

**UNKNOWN:** sample age, liveness cadence, reconnect ordering, atomic association
of a temperature with the units epoch, and whether a native bridge supplies an
additional invalidation signal. No valid freshness threshold can be measured
from these static constants. A cached getter response is not proof of a new
physical observation. Do not feed these events directly into v1's full-snapshot
freshness clock.

## Concrete read-only adapter seam and original fixture

The original fixture at
`analysis_tools/fixtures/ra4_driver_temperature_cases.json` contains hand-authored
examples, **not radio captures**. It records endpoint shapes and proposed decoding
outcomes, independently of the PC mock's guessed integer range. It is not a wire
sender or a license/vehicle-control fixture.

| Proposed application field | Meaning |
| --- | --- |
| `sourceZone` | Validated physical `frontLeft` / `frontRight`; derive logical driver only from separately verified side configuration. |
| `kind` | `numeric`, `low`, `high`, `unavailable`; never substitute numeric zero for absent state. |
| `value`, `unit` | Finite numeric display value and `C`/`F` only for verified non-MP4 automatic mode with matching units; limits have no invented numeric value. |
| `quality` | Distinguish observed value from `unknown`, `units_pending`, `unsupported_mode`, `stale`; these are original app states, not recovered wire fields. |
| `unitsEpoch`, `session` | Locally assigned metadata; invalidate interpretation across units/service changes until consistent state is re-established. Not stock-provided sequence numbers. |
| `receivedAt` | Local monotonic receipt time only. Must not be labeled physical sample time or used alone to prove freshness. |

Require an allowlisted zone, positive automatic/variant capability, known units
and strict finite-number parsing. Retain LO/HI and unavailable states. Reject
unknown/empty/malformed fields. Do not silently convert manual percentages or
unknown units. Field-age/liveness policy is deliberately **not implemented**
until the missing source-quality contract is closed. No change to prototype
v1, no real adapter, no enabled writes and no new resident dependency result.

## Resource effect

This change installs **0 bytes on the radio**, writes **0 runtime bytes there**,
and requires **0 radio staging bytes**. Python inspectors and fixture are PC-only.
The eventual single-field read-only decoder can be budgeted provisionally within
existing core-code allowance (target <=8 KiB code and <=1 KiB state, no private
dependencies, assets, persistence, logs or cache); **not built/measured** and not
a budget for transport or a complete HMI. Keep the product caps unchanged:
15 MB installed, 4 MB runtime growth, 8 MB additional update peak, 45 MB stock
reserve and 5 MB unallocated planned-peak margin. No feature in this task has
been shown to require external compute.

## Next single highest-value task

Close **read-only temperature quality across a units change and service restart**:
trace PersonalConfig's `temperatureUnits`/`ready` producer and hmiGateway's
subscription callback/wrapping path, then design a fixture-driven per-field
quality adapter without adding any live transport. In particular, determine
whether the existing services can distinguish stale cached setpoints from a
current valid value after `127`/`SNA`, and whether a refresh has any stronger
quality guarantee. If the artifacts cannot answer that, document the precise
passive trace fields needed; do not invent a heartbeat or freshness timeout.
This is an actionable next task, not a requirement for the owner to operate
the radio now. Screen loading, camera ownership and crash fallback remain
independent prerequisites before any resident trial.

## Verification for this change

The original inspectors have 12 synthetic tests, including malformed/truncated
inputs, bounds, operand alignment, a named class/typed getter and optional method
arguments. Full analysis suite: 103 tests pass with existing ignored
`analysis_work/test_deps` on PYTHONPATH; default Python lacks the optional
cryptography dependency required by one pre-existing test module. The unchanged
prototype's 15 Node tests pass. Fixture JSON parses. Exact source hashes and
bounded instruction queries above were checked against local read-only artifacts.
An independent review found no Critical/Important issue; its minor typed-ABC
coverage observation was addressed with the additional synthetic test.

Prototype host source remains 31,325 logical bytes / 61,440 estimated allocated
bytes at a 4,096-byte allocation assumption. This is **not** a radio installed-size
measurement. No visual/UI code changed, so the prior visual check was not repeated.
