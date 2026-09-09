# RA4 display request, AMS owner change and reclaim boundary

Date: 2026-09-06. Starting canonical head `7b16ef1f28eba5d8b2f10e2ba2619a2fb7ba608c`.
Existing owner-supplied images inspected on the host without execution.

## Decision

**STATIC_PROVED:** the HMI's `DisplayManager` destination resolves to the
`com.harman.service.LayerManager` service, not directly to the executable of
the same display-manager name. Recovered `layermanager.lua` registers that
service and implements `requestDisplay`. Its `ams` false branch calls
`setVisible(":AMS", false)` and reports a grant on the normal return path.
The helper writes a visibility command to the native display resource manager
and performs a read; it discards both operations' return values.

**STATIC_PROVED native mechanism:** DisplayManager's command descriptor for
`v` is Visibility, with a Boolean setter and Screen property `0x33`. That
setter calls `screen_set_window_property_iv`. Command-batch processing reaches
`screen_flush_context`. These establish a concrete stock visibility mechanism,
not a measured physical display/input handoff or an end-to-end acknowledgment.

**STATIC_PROVED service-owner reaction:** LayerManager subscribes to AMS owner
changes. For the AMS service name its callback restores AMS default z-order,
hides `:AMS`, and restores HMI default z-order. The callback does not inspect
oldOwner or newOwner, so the selected branch is not limited to service arrival.
It is a stock-owned cleanup candidate on AMS disappearance as well as other
owner transitions, assuming the subscription delivers that event.

**Critical scope limit:** that identity is the shared AMS service, not an
individual Xlet. A failed or hung app can leave AMS present. An unresponsive
AMS process may also retain service ownership. No deadline or detector for
either situation is proved here. Custom-app failure isolation, input/contact
release, camera/critical/comfort coexistence and target fail-open behavior
remain UNKNOWN. No target runtime gate passes.

## Artifact identities and method

Paths are relative to ignored `analysis_ra4_18.45.01/work/`. Hashes are SHA-256.

| Artifact | Path | Bytes | Hash |
| --- | --- | ---: | --- |
| Gateway | `hidden_hbc_ifs/segment_001a0000/files/bin/hmiGateway` | 153124 | `8d7fe8789bb012a66fbebd1bd44eefa506c672a5d70c90fbf92b3a5a6f01ec82` |
| Layer policy | `hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/misc/layermanager.lua` | 57303 | `8b49b6c1110275966d4bdbb92f93029a575a0fc73515783811414e25e796d285` |
| Window manager | `hidden_hbc_ifs/segment_001a0000/files/usr/bin/DisplayManager` | 214966 | `5e584c71cca22ada8498ceccae8c1270e3f754420262f77f3c38763af31e3385` |

The original Lua 5.1 inspector parses 71 prototypes. Lua offsets below are
file offsets; PCs are zero-based within the named prototype. Debug source-line
numbers provide supporting context, not primary identity. Closure bindings in
the root prototype were inspected alongside function bodies. Native offsets
are ARM virtual addresses. PT_DYNAMIC supplies 143 DisplayManager PLT imports.

The [previous Xlet handoff](ra4_xlet_foreground_handoff.md) supplies the
hash-bound AppsActiveScreen and MainSupplement call sites. No runtime trace,
vendor implementation, complete bytecode or executable payload is published.

## HMI destination and Lua registration

The gateway compares `DisplayManager` at `0x108DF0` through `0x108E00` and
takes mapping branch `0x109E7C`. That branch materializes service
`com.harman.service.LayerManager` and object `/com/harman/service/LayerManager`
from literals `0x1200D4` and `0x1200F4`. This is a recognized destination,
unlike the projection destinations in the [gateway report](ra4_projection_gateway_dispatch.md).

Lua root prototype 0 binds child 27 to `methods.requestDisplay` at
`0x0543` / `0x0597`. Prototype 66 opens `/dev/DisplayManager:0` in `rw` mode
at `0xB921` through `0xB92D`, then calls `service.register` for the mapped
LayerManager name at `0xB93D` through `0xB94D`. The native executable contains
that same resource-manager path. This links the service policy to its lower
display mechanism; it does not establish the live unit's running process state.

The separate `bin/start_display` script labels itself VP2-only and conditionally
starts DisplayManager when passed `-d`. It must not be treated as proof of the
RA4/VP4 boot selection. The exact live startup and service readiness still need
their own evidence.

## AMS visibility and returned grant

Prototype 27, debug source lines 781-878, dispatches several stock requester
families. The relevant branches are:

| Request | File anchors / PCs | Consequence |
| --- | --- | --- |
| `ams`, string `"true"` | `0x612D` PC151; `0x6139` PC154 | Select the AMS activation branch |
| AMS activation | `0x6145` PC157; `0x6155` PC161; `0x6175` PC169 | Request video-layer deactivation, hide `:map`, clear map-request state, show `:AMS` |
| `ams`, string `"false"` | `0x6185` PC173; `0x6191` PC176 | Select the AMS release branch |
| AMS release | `0x6199` PC178 through `0x61A5` PC181 | Call setVisible with `:AMS` and Boolean false |
| Result | `0x61A9` PC182; `0x6389` PC302 through `0x63A1` PC308 | Set grant true after helper returns; return layer/requested-visible/granted fields |

The activation branch is not itself a camera-admission check. It requests
video-layer deactivation, so it must not be exposed as an independent focus
shortcut for a custom app. Preserve the stock HMI admission and camera policy;
the combined path still needs supported integration and bench validation.

Prototype 6 `setVisible` accepts Boolean visibility and converts it to 1 or 0.
At `0x21A2` PC12 it loads the formatter `%s,v,%d;`; `0x21B2` PC16 calls
`dev:write`, then `0x21C2` PC20 calls `dev:read(1)`. Both CALLs specify zero
results. The method has no success return or explicit timeout. A device-library
exception could still interrupt execution; a returned error/short result is
not inspected at this layer. Prototype 7 setZOrder likewise writes and reads
without retaining results. A grant therefore records the policy path's normal
completion, not confirmed compositor success.

## Native visibility operation and window lifecycle

The native command descriptor at `0x1285D8` has these relevant fields:

| Field | Value |
| --- | --- |
| Selector / label | `v` / `Visibility` |
| Setter / value parser | `0x109694` / `0x110754` |
| Property | `0x33`, corroborated by the image's SCREEN_PROPERTY_VISIBLE diagnostic |
| Post-operation readback helper | `0x108D7C` |
| Stored visibility offset | `0x40` |

`CWindowManager::callFunction` loads the descriptor's setter at `0x10DDE4`;
its selected live-window branch calls it at `0x10DF30`. The Boolean setter
loads the descriptor property and native window handle at `0x109754` through
`0x10975C`, then calls `screen_set_window_property_iv` at `0x109760`. It checks
the result through the local diagnostic helper and can call the descriptor's
readback helper. This is not merely a matching import name.

Batch processing calls callFunction at `0x111810`, checks/logs nonzero return
codes, and reaches flush helper `0x1098A4` at `0x111878`. That helper calls
`screen_flush_context(context, 0)` at `0x1098E4`. The Lua API does not consume
the native setter result as a grant condition. Full device-library exception,
read/flush completion and timing semantics are not established by this trace.

The command descriptor region contains 15 entries followed by a zero sentinel
at `0x1287B8`; none is labeled focus or sensitivity. This narrow table census
does not exclude focus handling inside Screen, another service or another API.
Visibility and z-order evidence cannot prove touch/contact cancellation.

Native code also retains visibility in a cached window record on its `v`
path (`0x10DF58` through `0x10DF8C`). A window-create path can apply the stored
value through the same setter at `0x108924`. Do not infer that arbitrary absent
window names get a cache entry or that all creation paths inherit a hidden state.
The selected native window-close path calls its removal helper at `0x107618`
and `screen_destroy_window` at `0x107628`. A close-event reaction does not
establish how a hung owner is detected or how promptly its event is delivered.

`:AMS` is the exact policy/window key observed here. The native name constructor
consults ID_STRING and CLASS and can combine names using `:`. Do not relabel
this as a proved Screen group name or prescribe it to a custom package.

## Service owner change versus an individual app failure

Root prototype 0 sets myAMS to `com.aicas.xlet.manager.AMS` at `0x010F`.
Prototype 66 passes that identity and onOwnerChanged to
`service.subscribeOwnerChanged` at `0xB9E5` through `0xB9F5`.
Prototype 10 contains the callback, with three formal parameters
newName/oldOwner/newOwner. It branches on newName but uses neither owner value.

For the AMS name, `0x29FF` PC35 selects these calls:

1. `setZOrder(":AMS", amsDefault)` at `0x2A13` PC40.
2. `setVisible(":AMS", false)` at `0x2A23` PC44.
3. `setZOrder(":hmi", hmiDefault)` at `0x2A33` PC48.

The captured defaults are AMS 1 and HMI 5 (root `0x023F` PC109 and `0x0233`
PC106). The AMS branch does not explicitly show the HMI, restart it, restore
input focus or terminate a Xlet. Restoring an order value alone cannot prove
that the stock screen becomes visible or interactive.

**HIGH:** the cleanup actions are implemented by the stock LayerManager rather
than a Xlet pause/destroy callback. **UNKNOWN:** live delivery, scheduling bounds,
complete visibility/input restoration, and how a per-app failure is detected
while AMS remains alive. A resident proof must distinguish per-Xlet failure,
AMS service disappearance and AMS unresponsiveness. Do not kill the shared
stock VM to substitute for an app-specific recovery experiment.

## Next evidence and reproduction

The highest remaining static target is AMS/AppManager's **per-Xlet**
pause/destroy/error acknowledgment and container removal path while the shared
AMS service stays present. Follow that into focus/input ownership and any
stock-owned timeout. The service-owner callback found here answers a different
failure scope and cannot close the full fail-open requirement.

**Follow-up:** the [per-Xlet pause/watchdog trace](ra4_xlet_pause_watchdog.md)
identifies a native enabled-watch counter and expiry path that queues stopApp,
with conditional daemon restart. It also establishes that pauseApp can select
stop when PauseAllowed is false. These are lifecycle requests, not completed
container/input reclaim; live activation and bounded recovery remain unproved.

The existing host-only tools reproduce the relevant bodies:

```powershell
$py = 'analysis_work/post_reboot_20260906/venv/Scripts/python.exe'
$lua = 'analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/cmc/service/platform/misc/layermanager.lua'
& $py -m analysis_tools.lua51_inspect $lua --function 27 --start 150 --count 34
& $py -m analysis_tools.lua51_inspect $lua --function 6 --count 30
& $py -m analysis_tools.lua51_inspect $lua --function 10 --count 60
```

Native analysis uses ArmElfAnalyzer/Elf32Image, disassemble, word_xrefs and
PT_DYNAMIC import resolution. All raw output remains in ignored host evidence.
No radio/vehicle action, target command, input injection or provider contact
occurred. This continuation adds original analysis/specifications only, with
zero installed target bytes, normal growth or staging.

Fresh validation matched three artifact hashes/sizes, 28 Lua instruction
anchors and 15 native instruction/literal anchors. All 71 Lua prototypes parsed;
the complete 15-entry native descriptor region and its sentinel were checked,
with the Visibility record matched field-for-field. The three native Screen
call targets resolve within the 143-import inventory. All 83 local links in
six changed Markdown files resolve. The unchanged full host Python suite
passed **150 tests, no skips**. No JavaScript/C99, target or phone-bench test
was run; these checks do not prove runtime recovery.
