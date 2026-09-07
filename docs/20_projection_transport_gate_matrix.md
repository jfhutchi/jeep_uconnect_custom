# PC reference versus RA4 projection gates

Date: 2026-09-06. Decision artifact for canonical draft PR #14. Status explicitly
separates reference observations from the RA4's static and runtime evidence.
The [bench contract](../reports/android_auto_reference_contract.md) preserves
PR #15's provenance and limits; the [RA4 census](../reports/ra4_usb_stack_backend_census.md)
provides hashes, boundaries and the expected backend interface.

| Gate | PC/DHU reference | RA4 evidence | Status | Missing proof |
| --- | --- | --- | --- | --- |
| Cabin path / host detection | PC detects Samsung phone | C2 external pair HIGH; two host HCDs configured | UNKNOWN cabin-to-controller; STATIC_PROVED host configuration | Identified C2-to-PHY/controller net or existing correlated live topology record |
| Host API primitives | DHU performs accessory negotiation | Installed `libusbdi.so.2` exports vendor, descriptor, config, pipe and bulk APIs; stock clients import them | STATIC_PROVED API presence; HIGH usable stock host stack | Authorized client access, ABI/link/load check and exclusive device ownership |
| AOA request | AOA v2 reported after PC library change | Host primitives present; no identified installed AOA negotiator | PROVED PC; UNKNOWN RA4 | Selected phone accepts requests through stock cabin path |
| Accessory re-enumeration | `04E8:6860 -> 18D1:2D01`; Windows and Android corroborate | No RA4 observation | PROVED PC; UNKNOWN RA4 | Fresh accessory enumeration on the same physical path |
| Bulk endpoint availability | Interface 0, IN `0x81`, OUT `0x01` discovered | Descriptor/pipe/bulk API surface present | PROVED PC descriptors; STATIC_PROVED RA4 APIs | Actual descriptors, claim and endpoint availability on RA4 |
| Bulk transport establishment | Direct USB failed after enumeration; ADB tunnel worked | No receiver/client or transfer trial | UNKNOWN RA4; direct PC gate not passed | Sustained bidirectional transfers with detach handling; no stock-device interference |
| Android Auto negotiation | Protocol 1.7 over ADB only | HMI `GAL` vocabulary; engine absent under searched names | PROVED PC/ADB; UNKNOWN RA4 | Authorized receiver reaches protocol agreement over RA4 transport |
| TLS/session setup | TLS 1.2 passed over ADB only | No executable receiver contract | PROVED PC/ADB; EXTERNAL_PROVIDER_GATE RA4 | Compatible authorized engine and legitimate session setup |
| Video path / visible projection | Dashboard rendered over ADB | Stock 640x480 display; decoder/interface/resource gates open | PROVED PC/ADB; UNKNOWN RA4 | Decoder output, composition, frame timing and memory on exact ABI |
| Touch/input | Dashboard-to-launcher tap over ADB | Stock touch infrastructure and host ownership model | PROVED PC/ADB; UNKNOWN RA4 | Input delivery to authorized app/engine, focus release and no stolen stock input |
| Audio / microphone | Audio quality not independently validated | Stock audio services and HMI status contracts | UNKNOWN | Supported audio focus, call/voice paths, latency and restoration |
| Foreground ownership | PC window offers no vehicle-arbiter proof | Native Boolean admission check, HMI state checks, 640x480 app-screen pause and `ams` display-release request | STATIC_PROVED stock calls; UNKNOWN custom app and completed reclaim | Supported foreground identity with camera/critical/comfort priority; background API's SuperApp restriction resolved through permitted custom interface |
| Disconnect/recovery | Clean ADB session exits; second session after tunnel recreation; normal USB after owner reconnect | Host fail-open model; native watchdog stop queue and callback bookkeeping, including stopped-state updates on NoReply | PROVED limited PC behavior; STATIC_PROVED stock request/state paths; UNKNOWN RA4 recovery | Raw errors/parse validity, bounded app cleanup, native input release and automatic stock restoration; no inference from inventory/event alone |
| Return to Uconnect | Not tested by PC/DHU | Stock Xlet screen exit requests pause/display release; native pauseApp selects stop if PauseAllowed is false; Close explicitly stops; re-entry can dispatch Resume | STATIC_PROVED policy and asynchronous requests; UNKNOWN engine continuity | Supported custom Return, effective pause policy and engine continuity; distinct completion acknowledgments for return/resume/stop |
| Camera takeover | No vehicle in bench | Stock HMI camera priority and host arbiter model | STATIC_PROVED stock paths; UNKNOWN custom coexistence | Camera remains independent through app launch, hang, exit and removal |
| Critical/eCall and HVAC | No vehicle in bench | Existing priority/overlay model and stock evidence | UNKNOWN custom coexistence | Authorized integration yields correctly; no emergency-call trial improvised |
| USB device/function stack | Not required for host-side AOA | No named DCD/function bundle in bounded census | UNKNOWN complete board/device capability; EXTERNAL_PROVIDER_GATE for missing components | Exact QNX 6.5 OMAP DCD, descriptors and reversible cabin route if chosen CarPlay transport needs them |
| Stock projection backend | Google DHU services the PC session | HMI names `phoneProjectionService` and `DeviceConnectionManager`; recovered gateway rejects both in normal dispatch | STATIC_PROVED client/gateway routing gap; EXTERNAL_PROVIDER_GATE implementation | Matching supported bridge/build or separate permitted API, provider/package identity, service registration and screen |
| Resident launch and authorization | Windows DHU proves none | Secure AMS/AppManager manual launch; stock Xlet/AWT/LWUIT view callers and AMS metadata | STATIC_PROVED lifecycle/view references; EXTERNAL_PROVIDER_GATE custom app | Legitimate package identity, compatible SDK and supported foreground/surface lifecycle |
| Resource fit | PC RAM/CPU/storage is inapplicable | Approx. 77 MB historical free space; budget unchanged | UNKNOWN measured product fit | <=15 MB installed, <=4 MB growth, <=8 MB extra staging, >=45 MB reserve and >=5 MB residual |
| Rollback | PC/phone returned to ordinary USB state | Stock per-app lifecycle traced; no custom package trial | UNKNOWN RA4 runtime rollback | Package-local uninstall, registry reconciliation, clean reboot and stock baseline |

## Decision rules

1. Host-side AOA can proceed architecturally with either proved reachable host
   controller. EHCI is not disqualified because it lacks peripheral mode. A
   conventional downstream hub does not inherently prevent host-side AOA;
   routing, compatibility, power and device ownership still need proof.
2. The documented QNX 6.6 CarPlay role-swap route is a separate reference. Do
   not transfer its DCD prerequisite to Android Auto or assume QNX 6.6 binaries
   are compatible with the recovered QNX 6.5 image.
3. Enumeration, protocol/TLS and visible projection each need their own
   observation. HMI labels and host tests cannot advance target runtime gates.
4. Do not deploy before the [no-engine resident milestone](21_first_resident_runtime_proof.md)
   prerequisites are met. A provider or missing-evidence gate is not a measured
   local failure and does not select external compute.

The [native gateway trace](../reports/ra4_projection_gateway_dispatch.md) now
proves that backend-name registration alone cannot satisfy the recovered HMI
route: commands and owner subscriptions exit on unknown destinations. USB rule
inspection still does not establish exclusive AOA ownership. This advances the
backend compatibility requirement; it does not establish working Android Auto
at the stock Jeep USB port.

The [Xlet foreground handoff](../reports/ra4_xlet_foreground_handoff.md) identifies
stock display ownership requests and the distinction between pause and stop.
It does not pass a runtime gate: native `requestBackground` emits the configured
SuperApp identity, display release is not yet traced to compositor completion,
and no engine has demonstrated session continuity across the stock pause.

The [pause-policy/watchdog trace](../reports/ra4_xlet_pause_watchdog.md) further
qualifies screen exit: the recovered PauseAllowed default is false, and false
selects stop. Its enabled per-app watchdog expiry queues stopApp; conditional
daemon restart is a different operation from preserving a healthy session.
Asynchronous IPC submission and queued recovery requests do not establish
bounded stop, native visibility or input reclaim while AMS remains registered.

The [callback/result trace](../reports/ra4_xlet_result_completion.md) establishes
why app-state observations need qualification: stopped bookkeeping can advance
on NoReply, selected AMS stop errors normalize to zero, and malformed successful
reply parsing can yield a zero-code app event with a separate failure flag.
Physical cleanup remains unproved; no gate is closed by those notifications.

The [AMS destroy/cleanup trace](../reports/ra4_ams_destroy_cleanup_contract.md)
identifies the normalized errors as Xlet exception, AMS timeout and incomplete
thread termination. It follows actual LWUIT/GLES cleanup and Xlet-container
removal calls, including selected exception paths. The timeout action runner
has no inline ROM body; completed native visibility/input recovery and the
effective deadlines remain UNKNOWN. These findings narrow resident recovery
requirements without changing any USB, transport or engine gate.

The [container/focus trace](../reports/ra4_xlet_container_focus_cleanup.md) now
follows the default frame through AWT detachment, recursive removeNotify,
conditional focus transfer and selected event cleanup. It preserves the
distinction between Java focus/mouse state and native input contacts; shared
window visibility and usable stock foreground still require separate evidence.
