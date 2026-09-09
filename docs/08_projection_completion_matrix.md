# 08 - Projection completion matrix

> **Project status - 2026-09-07: BLOCKED without manufacturer support.**
> The software-only integration is effectively not achievable with the hardware
> and authorized access available to this project. Manufacturer-provided or
> approved development/service hardware, credentials, signing/entitlements and
> compatible licensed software are prerequisites; no sufficient route is confirmed.
> This document is retained as research or a conditional design, not an active
> deployment roadmap. The [current project status](00_project_status.md)
> supersedes earlier implementation priorities and defines reopening conditions.

Updated 2026-09-06. This is the completion audit for the OEM-style projection
goal. It distinguishes recovered stock behavior, host-model conformance and
actual RA4 target proof. A host test or string reference never substitutes for
target behavior.

For the current phone-versus-radio transport decision, use the
[PC reference / RA4 gate matrix](20_projection_transport_gate_matrix.md), which
separates accessory enumeration, protocol/TLS and visible projection and links
the structured runtime census and first no-engine resident proof.

Status vocabulary:

- **STATIC_PROVED**: direct read-only artifact/control-flow evidence.
- **MODEL_PROVED**: original host implementation exercises the required policy.
- **TARGET_UNPROVED**: architecture exists, but no legitimate RA4 build/run proves it.
- **EXTERNAL_EVIDENCE_REQUIRED**: completion needs an artifact, supported interface
  or authorized spare-hardware observation not currently accessible.

| Requirement | Current evidence | Status | Evidence still required for production |
| --- | --- | --- | --- |
| Preserve stock Radio/Media/Climate/Controls/Phone/Messaging/Settings | Product contract and current prototype render no replacement factory screens | MODEL_PROVED / TARGET_UNPROVED | Supported stock application/screen loading boundary and target observation |
| Full 640x480 projection while selected | `DEVICE_PROJECTION`; graphics.conf has OMAP3730/SGX530, CMC mtouch and `video_hmi`; QNX reference proves managed groups/focus | STATIC_PROVED / TARGET_UNPROVED | Exact stock group/class, buffer, z-order, focus/sensitivity, owner-death and render proof |
| Return to Uconnect without ending session | `sessionActive` is independent of current branch at FWS `0x002588C5-0x0025892C`; host model preserves session | STATIC_PROVED / MODEL_PROVED / TARGET_UNPROVED | Complete `PROJECTION_BACKTO_CAR` consumer and supported stock navigation action |
| Return to active projection without reconnect | Stock AppPhone BacktoCar/start check at `0x00262B59-0x00262B72` precedes sessionActive/goto; model preserves session | STATIC_PROVED / MODEL_PROVED / TARGET_UNPROVED | Missing screen/listener, start/resume backend semantics and target continuity measurement |
| Factory camera priority and return | DisplayManager `0x002BA764`; LayerManager preemption/stack unwind `0x002D4D6F-0x002D4EF8` | STATIC_PROVED / MODEL_PROVED / TARGET_UNPROVED | Spare-bench latency, every camera variant and projection restoration |
| Temporary comfort overlay | HVAC popup path `0x0026DA68-0x0026DAB9` proves branch-independent popup layering; model preserves owner/session | STATIC_PROVED / MODEL_PROVED / TARGET_UNPROVED | Heated-seat/wheel event-to-popup consumers and target overlay dismissal |
| Projection owns ordinary call presentation while active | Projection call event `0x002B4E18-0x002B4EBC`; native HFP presentation starts `0x00257983` | STATIC_PROVED / MODEL_PROVED / TARGET_UNPROVED | Supported policy/API that gates only native goto/popup, not HFP ingestion |
| Projection owns ordinary message presentation and audio | Native SMS popup `0x002B6C35-0x002B6C96` and TTS `0x002B85C2-0x002B8750` isolated | STATIC_PROVED / MODEL_PROVED / TARGET_UNPROVED | Supported popup plus TTS gate while preserving MAP/message ingestion |
| Emergency/eCall remains stock-owned | Emergency branch precedes ordinary BT processing; critical owner is explicit in both reference models | STATIC_PROVED / MODEL_PROVED / TARGET_UNPROVED | Configuration-specific target behavior and audio-priority confirmation |
| Inactive/disconnected/invalid/stale restores stock presentation | Host models invalidate state, retain sequence watermark and reject delayed replay | MODEL_PROVED / TARGET_UNPROVED | Real service epoch/sequence contract and failure/restart observation |
| Projection/HFP audio and microphone arbitration | `P/share/audioDSP/audioMgrCMC.conf:24-29` maps stock `audioApp` to MME; QNX reference separates HFP, visual, routing/ducking, playback and acoustic input | STATIC_PROVED (configuration/reference) / TARGET_UNPROVED | Recovered service census; exact source registration, priority, callbacks, mic owner-death; spare-bench tests |
| Tiny resident arbitration implementation | JavaScript model plus C99 no-heap candidate; C source is 19,404 bytes across four files | MODEL_PROVED / TARGET_UNPROVED | C compile/tests, target ABI, linked map, allocated package bytes |
| Protected 77 MB envelope | Caps are 15 MB installed, 4 MB writable, 8 MB extra peak, 45 MB protected, 5 MB residual | MODEL_PROVED / TARGET_UNPROVED | Mount-specific boot/use/update measurements and target package accounting |
| Existing stock projection-screen reuse | `DeviceProjection.swf`, `PROJECTION_BACKTO_CAR` and service/session symbols are referenced by stock HMI | STATIC_PROVED (references) / TARGET_UNPROVED | Complete physical screen artifact, descriptor/loader and supported backend binding |
| Stock lifecycle for an already authorized resident Xlet | Secure AMS startup, non-autostart install state, generic Apps tile, DRM-checked native `startApp` and later foreground arbitration are recovered | STATIC_PROVED / TARGET_UNPROVED | Legitimately authorized inert package returned by target `getAppList`, target launch/fallback observation |
| Authorization of a new resident component | Detached signature/DRM/developer-token binding is recovered; no legitimate new-project issuer or credential is available | EXTERNAL_EVIDENCE_REQUIRED | Written supported package/DRM/developer route or legitimately issued inert signed sample; no bypass |
| Complete CarPlay/Android Auto engine | QNX 6.6-era docs prove a legacy CarPlay USB role-swap transport family; later Smartphone Connectivity is a modular vendor lead, but public 2.0 remains QNX 7.x | EXTERNAL_EVIDENCE_REQUIRED | Support-supplied legacy drivers plus compatible receiver or authorized port, Apple/Google access, target ABI and measured CPU/RAM/storage |
| USB device-role path | OMAP3730 supports OTG host/peripheral; BE2800 and the external D2784B circuit map are identified; Mentor requests ULPI PHY reset; stock onoff calls `usbPowerSwitch`, which changes VBUS-drive bits through `0x480ab000`; QNX 6.6 has generic `io-usb-dcd`, but the public OMAP3730 BSP lists OTG Host only | STATIC_PROVED (silicon/platform/software control); HIGH external circuit map / TARGET_UNPROVED | PHY/power-switch and active hub identity, electrical VBUS behavior, D2784B-to-OMAP route, installed DCD/function driver and role-switch proof; utility completion reporting does not prove hardware success |
| No signing, license or activation bypass | Repository/PR path audit contains no vendor payload, license, key, certificate or activation material | STATIC_PROVED | Re-audit every future package and deployment design |

## Current implementation evidence

The [startup PHY follow-up](../reports/ra4_startup_usb_phy_identity.md) now
identifies intended USB83340-family support and a GPIO-38 reset sequence on
EHCI, separately from Mentor's ULPI configuration. Its vendor-low-byte check
does not establish fitted silicon; the physical port and DCD gates stay open.

The development-host bench now passes all 20 committed tests under Node 24.15.0;
all eight mjs modules pass `node --check`. The earlier isolated V8 fallback was
historical verification. The post-reboot Python discovery passes 135 tests.

The C99 arbiter compiled under Ubuntu/WSL GCC 13.3.0 with
`-std=c99 -Wall -Wextra -Werror -pedantic` and passed all assertions, including
its compile-time <=128-byte state guard. These are host results, not QNX target
ABI, footprint or runtime proof. The bench installs zero radio bytes.

Historical GitHub Actions runs `34038125932` and `34038125990` terminated
before runner allocation. No new hosted-runner result is claimed. The workflow
remains manual-only. Exact local commands/results are in the
[post-reboot checkpoint](../reports/ra4_post_reboot_checkpoint.md).

## Closest completion path

1. Follow the [post-reboot checkpoint](../reports/ra4_post_reboot_checkpoint.md):
   host tests, strict C99 execution, 122-marker census and foreground XREFs are
   complete. Raw markers do not inspect compressed SWF contents.
2. Use the [completed startup PHY trace](../reports/ra4_startup_usb_phy_identity.md)
   to correlate the named EHCI USB83340-family/GPIO-38 path and separate Mentor
   ULPI path to existing topology captures or authorized BE2800 port nets;
   close the physical hub and DCD gates independently.
3. Acquire the matching projection screen/backend contract and prove the
   BacktoCar/start path's session continuity, then close comfort/audio seams.
4. Use the proved Xlet lane only with legitimate package authorization.
5. Measure target storage, RAM, CPU and all foreground/fallback behavior on
   separately authorized spare hardware before deployment or engine selection.

The project is not target-proved by host tests. No step authorizes radio writes,
modified firmware, credential derivation or safety-feature bypass.
