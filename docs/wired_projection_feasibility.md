# RA4 Wired Projection Feasibility

**Android Auto: B. CarPlay: C.**

## Executive conclusion

RA4 hardware plausibly supports VGA-class wired projection, but the recovered build is not one switch away from either product. Android Auto is **B**: the shortest viable route starts with the existing host stack and adds an authorized AOA/receiver adapter. CarPlay is **C**: it inherits the same AV/HMI gaps and additionally crosses an unproved reversible USB path plus a hard MFi authentication boundary. Pursue Android Auto first. Internet connectivity is supplied by the phone and is independent of this transport decision.

## RA4 USB architecture

[usb-true-host] proves real host operation: production `io-usb` loads Mentor/MUSB at `0x480ab000`/IRQ 92 and EHCI at `0x48064800`/IRQ 77. `libusbdi.so.2` exports attach/detach, descriptor parsing, configuration/interface selection, pipe, vendor-control and bulk I/O entry points; stock clients import them. The physical chain is phone -> active SD/USB/AUX hub -> UCI cable -> Radio C2 D2784B -> unproved internal PHY/controller mapping. See `docs/ra4_usb_architecture.md` for the exact call graph.

## Apple/iAP support

RA4 has active **legacy** Apple media integration: Apple HID/audio rules and `iofs-usb-ipod.so`/iPod media clients are present [apple-legacy]. The exact protocol generation used by those clients is not fully named, but the production activation chain does not prove iAP2. The bounded 122-marker and structured census found no `Probe_iAP2`, iAP2 role-swap service, `usblauncher`, `io-usb-dcd`, device-function bundle or CarPlay receiver [iap2-negative]. Therefore iPhone music support must not be promoted to iAP2 or CarPlay support.

## Android/AOA support

Google AOA keeps the head unit/accessory as USB host and uses vendor requests 51/52/53, re-enumeration to Google accessory VID/PIDs, and bulk IN/OUT endpoints [aoa-reference]. RA4 already has the corresponding low-level primitives [usb-arbitrary-bulk]. What is missing is a production AOA negotiator, explicit AOA rule/ownership handoff, re-enumeration conflict handling and sustained-traffic proof [aoa-ra4-gap]. ADB/manufacturing references are not counted as production capability.

## Existing projection remnants

The HMI has production-grade vocabulary for `phoneProjectionService`, `DeviceConnectionManager`, `startProjection(ppId)`, CarPlay/GAL error states, session, BackToCar, navigation, now-playing and calls [projection-hmi-remnant]. It is dormant/incomplete, not active projection. The recovered native `hmiGateway` has a fixed destination table that rejects both projection destinations before command invocation and owner subscription [projection-gateway-gap]. No matching receiver or bridge owner was found in the bounded corpus.

## Video/display pipeline

RA4 already configures QNX Screen, OMAP3730/SGX530 graphics, `video_hmi`, CMC mtouch and a 640x480@60 display [display-stack]. The silicon includes IVA2.2-class acceleration and related reference data makes 640x480 H.264 Baseline at 30 fps plausible [h264-silicon]. The decisive software fact is still UNKNOWN: no supported installed H.264 decoder/client ABI, pixel/buffer contract, or measured decode-to-display latency is proved [h264-runtime-gap]. Full-screen app/layer integration is plausible but requires stock foreground ownership.

## Touch/input return path

Screen/mtouch and stock HMI/Xlet consumers prove touch-event infrastructure and application lifecycle [touch-input]. Stock event architecture also strongly supports hard-key, rotary and steering-wheel ingestion [button-input]. Projection still needs coordinate/contact normalization, focus/sensitivity grant, preemption cancellation, button mapping and serialization into the active USB session. Absolute touch delivery and the voice-button contract remain runtime/API unknowns.

## Audio output path

AudioCtrlSvc, MME and `audioApp -> MME` mapping prove a stock application/media audio plane [audio-path]. The shortest sink is therefore a stock logical application/media source, not a new sound server. However, the PCM open ABI, sample formats/rates, channels, routing, focus priority, duck/pause, volume/mute and restoration callbacks are not yet recovered. Projection media, prompt and call audio require separate fail-open leases.

## Microphone path

The cabin microphone is consumed by stock phone/VR paths, but ordinary resident-application PCM access is not proved [microphone-path]. Sample format/rate, privilege, exclusivity, AEC integration, assistant-versus-call arbitration and owner-death release remain UNKNOWN. This is a material blocker for Google Assistant, Siri and projected calls, but not for the first transport primitive.

## HMI integration

Stock mechanisms already separate projection session state from visible foreground and implement foreground admission, camera/critical preemption, HVAC popups and navigation-stack return [hmi-arbitration]. A legitimate projection app should enter through the stock application/full-screen container, preserve the session while backgrounded, and use independent visual/audio/mic/input leases. Camera, emergency/eCall, display-off and vehicle-safety policy remain stock-owned. No safety behavior is bypassed.

## Media-hub architecture

The factory 68141322AA/68289895AA module combines SD, USB and AUX behind one radio-facing D+/D- pair, so it contains active hub/controller or mux logic [media-hub]. A conventional downstream hub can still carry host-side AOA and is not presently an Android Auto blocker. The QNX CarPlay role-swap path makes the same module a possible CarPlay blocker: reverse data direction and VBUS behavior are unproved. A different later Mopar hub family exists, but public catalogs do not disclose what changed.

## Later FCA/Harman comparison

The immediate public Uconnect 4 comparison proves production wired Android Auto and CarPlay with media USB, touch, knobs, voice and HMI source takeover [later-uconnect]. It does **not** prove RA4 ancestry: the cited VP4RAC FCC implementation is Panasonic, whereas RA4 is Harman BE2800. Selected public evidence does not expose the later SoC, OS, RAM, USB controller, DSP or receiver internals [later-hardware-unknown]. The defensible conclusion is combination **B+C+D+E**: changed media-hub family, required Apple authentication, a newer/different head-unit platform, and a complete licensed projection software stack; exact contribution of each is UNKNOWN.

## CarPlay authentication boundary

Apple states that CarPlay video uses MFi-SAP and that the authorization challenge/response is handled by an Apple-provided authentication IC [carplay-auth]. This is a hard external dependency; no keys, credentials or bypass are sought. RA4 has no identified compatible IC [ra4-auth-hardware]. It may contain an older authenticator for legacy Apple media, but compatibility and physical location are UNKNOWN. Until the chip is identified, additional compatible authentication hardware must be budgeted as required.

## Android Auto authentication/protocol boundary

AOA has no dedicated hardware-authenticator requirement in its public transport specification [aoa-reference]. Android Auto above AOA remains a licensed/approved receiver and secure protocol integration problem [aa-auth-boundary]; the repository's DHU reference observed the authorized development path but does not supply a production receiver. Consequently Android Auto is materially easier to prototype because it avoids both the CarPlay USB role reversal and Apple authentication-IC dependency.

## Resource feasibility

The 640x480 display, USB 2.0 host primitives and IVA2.2-class silicon make 800x480-ish/30-fps projection credible [resource-fit]. Hardware proved: OMAP3730/Cortex-A8/SGX530/IVA2.2 family and 640x480 display. Software proved: Screen, mtouch, USB host, HMI lifecycle and audio-service foundations. Inferred performance: VGA H.264 at automotive frame rates. UNKNOWN: RAM capacity/headroom, installed decoder, receiver footprint, measured CPU/USB/display bandwidth and end-to-end latency. The approximate 77 MB writable observation is not a RAM or safe-install budget.

## Android Auto classification

**Grade B — plausible but one or more significant unknowns remain.** Host transport is the strongest completed primitive, while AOA ownership, receiver/provider, video decode, audio/mic and measured resources remain open. This grade is not A because no complete local video/audio/session path has been exercised.

## CarPlay classification

**Grade C — requires additional or newly verified hardware-backed authentication and likely USB-path work, while remaining technically plausible.** OMAP dual-role silicon alone is insufficient. The active hub, DCD/function stack, VBUS role lifecycle, MFi IC and licensed receiver are not present as a proved chain.

## Minimum architecture for each

Both targets reuse stock display, application lifecycle, HMI priority, audio-service and input foundations. Android Auto keeps RA4 in host mode and adds AOA plus an authorized receiver. The documented CarPlay route adds iAP2 probing, role swap, device-side USB, MFi authentication and an authorized Apple receiver. The tables mark each block at the evidence-supported ceiling.

### Android Auto

| Block | Status |
| --- | --- |
| PHONE | ALREADY PRESENT |
| USB SESSION | PRESENT BUT NEEDS ADAPTER/GLUE |
| PROJECTION PROTOCOL | MISSING SOFTWARE |
| VIDEO DECODER / DISPLAY | UNKNOWN |
| AUDIO ROUTING | PRESENT BUT NEEDS ADAPTER/GLUE |
| MIC / INPUT RETURN | PRESENT BUT NEEDS ADAPTER/GLUE |
| HMI ARBITRATION | PRESENT BUT NEEDS ADAPTER/GLUE |

### CarPlay

| Block | Status |
| --- | --- |
| PHONE | ALREADY PRESENT |
| USB SESSION | UNKNOWN |
| PROJECTION PROTOCOL | EXTERNAL AUTHENTICATION DEPENDENCY |
| VIDEO DECODER / DISPLAY | UNKNOWN |
| AUDIO ROUTING | PRESENT BUT NEEDS ADAPTER/GLUE |
| MIC / INPUT RETURN | PRESENT BUT NEEDS ADAPTER/GLUE |
| HMI ARBITRATION | PRESENT BUT NEEDS ADAPTER/GLUE |

## Exact blockers

Android Auto: production-compatible AOA ownership and re-enumeration on the actual cabin path; authorized receiver; installed H.264 client path; stock PCM/mic/input contracts; measured resources. CarPlay: all shared AV/HMI blockers plus reversible hub/C2/PHY/VBUS behavior, compatible QNX device stack/DCD/descriptors, a compatible Apple authentication IC, MFi authorization and licensed Apple receiver. Neither target is blocked by obsolete embedded Internet service.

## One recommended next engineering objective

**Prove AOA negotiation and bidirectional bulk I/O through the stock RA4 cabin USB path.** On an owner-authorized spare/bench system, issue the standard AOA control sequence, observe accessory-mode re-enumeration, claim bulk IN/OUT and exchange bounded deterministic frames with clean detach/recovery. This single result validates the shortest Android transport primitive, characterizes media-hub transparency, and avoids projection-client, vehicle and MFi work.

## Verification

The authoritative base is hash-bound. The baseline Python suite passed 305 tests after installing host-only dependencies. The final suite passes 311 tests, including six renderer/model tests. The renderer validates evidence levels, source hashes, negative-search scope, target/status vocabularies, forbidden scope, exact output set and one next objective. Closure also requires two identical `--check` runs, `git diff --check`, input hashes, and equality of the original dirty-checkout fingerprints. No target binary is executed.

## Git branch/commit

Work is isolated on `codex/ra4-wired-projection-feasibility` from `5b9826b2b6537f12b4bf08a50003ea6914263700`. The final Git commit SHA is reported after commit; embedding it in its own generated content would be self-referential. No pull request is created.

## Evidence ledger

| Claim | Level | Statement | Sources |
| --- | --- | --- | --- |
| usb-host-stack | PROVED | RA4 materializes QNX 6.5 io-usb with Mentor/MUSB and EHCI OMAP3 host-controller drivers, plus a host client library exporting descriptor, configuration, vendor-control, pipe, bulk, attach and detach APIs. | repo-usb-census, repo-post-reboot |
| usb-true-host | PROVED | The radio is a true USB host in the recovered production startup: io-usb loads devu-omap3530-mg.so at 0x480ab000/IRQ 92 and devu-ehci-omap3.so at 0x48064800/IRQ 77. | repo-usb-census, repo-post-reboot |
| usb-phy-power | PROVED | Recovered board code requests Mentor ULPI reset and controls VBUS-drive bits through usbPowerSwitch; the exact electrical result and cabin-port controller remain unknown. | repo-usb-power, repo-usb-startup |
| usb-stock-classes | PROVED | Stock production rules and clients cover mass storage, MTP/MTPZ, serial/network classes, legacy Apple HID/audio, and iPod media; they do not establish a projection session. | repo-usb-census, repo-gateway |
| usb-arbitrary-bulk | STRONGLY SUPPORTED | The materialized host API can perform arbitrary vendor control and bidirectional bulk transfers, but access, exclusive ownership, sustained throughput, and new-client loadability are unproved. | repo-usb-census |
| apple-legacy | STRONGLY SUPPORTED | RA4 has active legacy iPod/iPhone media support through iofs-usb-ipod, libipod/itun-adjacent paths, and Apple HID/audio enumeration rules; no recovered activation chain proves iAP2. | repo-usb-census, repo-gateway, repo-post-reboot |
| iap2-negative | PROVED | The bounded recovered-tree census found no named iAP2 probe/role-swap service, usblauncher, io-usb-dcd, compatible device-function bundle, or CarPlay receiver. | repo-usb-census, repo-post-reboot |
| aoa-reference | PROVED | AOA requires the accessory to remain USB host, issue vendor control requests 51/52/53, wait for Google VID/PID re-enumeration, and then use bulk IN/OUT endpoints. | google-aoa |
| aa-dhu-reference | PROVED | Google's current DHU supports Android Auto over USB AOA and exposes 800x480 at 30 fps as a supported head-unit test configuration. | google-dhu, repo-aa-bench |
| aoa-ra4-gap | UNKNOWN | No installed RA4 AOA negotiator or explicit 18D1:2D01 rule is identified; MTP detachment, phone re-enumeration, endpoint ownership and sustained bulk traffic remain untested on RA4. | repo-gateway, repo-usb-census |
| projection-hmi-remnant | PROVED | The HMI contains dormant production vocabulary and call sites for phoneProjectionService, DeviceConnectionManager, startProjection(ppId), CarPlay/GAL errors, session status, BackToCar, navigation, now-playing and call state. | repo-usb-census, repo-hmi |
| projection-gateway-gap | PROVED | The hash-identified production hmiGateway rejects both projection destinations before command invocation or owner subscription; a matching bridge/backend is missing from this build. | repo-gateway |
| display-stack | PROVED | RA4 configures QNX Screen at 640x480@60 with OMAP3730/SGX530 libraries, video_hmi, CMC mtouch/scaling, window/buffer APIs and factory event consumers. | repo-codec, repo-screen, repo-io-screen |
| h264-silicon | STRONGLY SUPPORTED | OMAP3730 contains Cortex-A8, IVA2.2 and SGX530 blocks, and an adjacent IVA2.2 reference demonstrates VGA H.264 Baseline decode at 30 fps; this is plausibility, not an RA4 benchmark. | repo-codec, ti-omap |
| h264-runtime-gap | UNKNOWN | No supported installed H.264 decoder, DSP codec server, OpenMAX component, client ABI, pixel format, buffer contract or measured latency is proved on RA4. | repo-codec, repo-post-reboot |
| touch-input | PROVED | Stock Screen/mtouch and HMI application paths receive touch and foreground events; exact projection coordinates, contact lifecycle, focus/sensitivity ownership and serialization require an adapter and runtime proof. | repo-screen, repo-xlet-view, repo-io-screen |
| button-input | STRONGLY SUPPORTED | Stock HMI mechanisms receive hard-key, rotary and steering-wheel-related events, but the exact projection mapping and voice-button ownership are not closed. | repo-hmi, repo-xlet-view |
| audio-path | PROVED | RA4 contains AudioCtrlSvc/MME infrastructure and a configured audioApp-to-MME logical source mapping; exact PCM sink ABI, sample formats, focus priority, volume and restore callbacks remain unknown. | repo-audio, repo-hmi |
| microphone-path | UNKNOWN | Cabin microphone use by stock phone/VR is evident, but no ordinary resident-application PCM capture API, format, permission, arbitration or owner-death contract is proved. | repo-audio, repo-hmi |
| hmi-arbitration | PROVED | Stock AppStateManager, DisplayManager and LayerManager provide foreground admission, camera/critical preemption, temporary HVAC overlays, session-versus-visibility separation and navigation-stack return. | repo-hmi, repo-screen |
| media-hub | STRONGLY SUPPORTED | The RA4 cabin module is an active SD/USB/AUX hub or multiplexer on one upstream D+/D- pair; fixed downstream behavior would not block host-side AOA, but reverse-role transparency for CarPlay is unknown. | repo-media-hub, mopar-2014 |
| carplay-role-swap | PROVED | The documented QNX 6.6 CarPlay sequence probes Apple devices, requests Digital iPod Out role swap, stops the host stack, and starts io-usb-dcd with device-stack rules. | qnx-usblauncher, repo-media-hub |
| carplay-auth | PROVED | CarPlay video uses MFi-SAP and an Apple-provided authentication IC for the signed authorization exchange; MFi program access and certification are hard external dependencies. | apple-security, apple-mfi |
| ra4-auth-hardware | UNKNOWN | No compatible MFi authentication IC is identified in RA4 artifacts or public board evidence; legacy iPod support does not prove that any existing device is CarPlay-capable. | repo-usb-census, fcc-be2800, apple-security |
| aa-auth-boundary | STRONGLY SUPPORTED | AOA itself specifies no dedicated hardware authenticator, but a production Android Auto receiver/provider, protocol security, product approval and integration contract remain external software/licensing dependencies. | google-aoa, google-dhu, qnx-sdk, repo-engine |
| later-uconnect | PROVED | Public 2018 Uconnect 4C documentation proves production wired Android Auto and CarPlay through media USB with touch, knobs and voice; FCC records identify at least one VP4RAC implementation as a newer Panasonic radio, not the Harman BE2800. | mopar-uconnect4, fcc-vp4rac, fcc-be2800 |
| later-hardware-unknown | UNKNOWN | Public sources used here do not establish the later unit's SoC, CPU, GPU, RAM, storage, OS, USB controller, audio DSP, authentication-IC location or projection-daemon implementation. | fcc-vp4rac, mopar-uconnect4 |
| later-media-hub | STRONGLY SUPPORTED | Mopar assigns later projection-era vehicles a different media-hub part family, but the public catalog does not explain whether the change is electrical, power, protocol, speed or authentication related. | repo-media-hub, mopar-later-hub |
| resource-fit | INFERRED | VGA-class wired projection is plausible on the silicon and display, but overall resident fit is not proved because RAM, available CPU, decoder reservation, USB throughput and receiver size are unmeasured. | repo-codec, repo-resources, google-dhu |

## Sources

1. `reports/ra4_usb_stack_backend_census.md` (Structured census boundary; Hash-identified host runtime; Device/function-stack gate), SHA-256 `cd2dbf9b4573bd2c776ddd80bcb165a9cacd942c6d7c124e8f9a21270432897c`.
2. `reports/ra4_projection_gateway_dispatch.md` (Fixed destination resolution; USB ownership follow-up), SHA-256 `41bf4406ae9ee28e748e7a3d422a9e79572ef520c462c51c7fefc45f7b85a813`.
3. `reports/ra4_post_reboot_checkpoint.md` (122-marker corpus census and startup USB paths), SHA-256 `77322b1e48c072e6aefcbf958c74e0d92b640af27461dd7b0008b4ac25b8e5da`.
4. `reports/ra4_usb_phy_power_control.md` (Mentor ULPI reset and usbPowerSwitch control-flow trace), SHA-256 `81ee93fa8506290079a6122bd8c1aacf41f67f777ccfadbe5a7b8253539421ef`.
5. `reports/ra4_startup_usb_phy_identity.md` (startup-omap3730cmc, USB83340-family EHCI path, GPIO-38 reset), SHA-256 `74b81f841dcec95fe6bf4439e52dbe914f72632b9691a09c4de667c5bee6d8bd`.
6. `docs/12_ra4_projection_hardware_feasibility.md` (Decision; Evidence ladder; New bounded corpus probe), SHA-256 `66aa7ad7ae735f91ee67d2b01fbfadb48afda1bed66c21905106ec9cb69b8d60`.
7. `docs/14_qnx6_audio_arbitration_reference.md` (Mapping to RA4; Required independent leases), SHA-256 `08aa4fa073dc55bf8b06a1f2191c5e59c40d79f6743570cfa609182eff683da1`.
8. `docs/15_qnx6_screen_touch_camera_reference.md` (Exact RA4 evidence; Required surface contract; Unknowns), SHA-256 `e6b86ab69ebe2bde489081f01d1f703d833a192b45f29f90a18aeb858f346226`.
9. `reports/projection_foreground_ownership.md` (Confirmed mechanisms; Arbitration contract), SHA-256 `576f8a5e1475fa3d24ea67f5409b00e83609c005f99283b9bb7eff675cd6cd02`.
10. `reports/android_auto_reference_contract.md` (AOA v2 re-enumeration and DHU protocol observations), SHA-256 `940ab7e8bd38c62e6c657b6853a7268c96dc50003d6297ab3d105203b53a18da`.
11. `docs/19_ra4_media_hub_usb_path.md` (Decision; Connector evidence; Exact next evidence), SHA-256 `1ee9c0b337010a7ade28bfbccb81e8e787965b4d96f15c736c24984f8318085a`.
12. `docs/11_projection_engine_feasibility.md` (Provider qualification matrix; Licensing and access gates), SHA-256 `82d3457a3086b476e8552b74fd8f6741947e77ad67dd92f853d4543000a2c847`.
13. `docs/ra4_resource_budget.md` (Provisional envelope; External capability ledger), SHA-256 `835314688c2145f4ec3b8f2d82ec95cc945426d39ea5ca6bc32497384f4dfae2`.
14. `reports/ra4_resident_xlet_view_path.md` (640x480 Xlet container and lifecycle path), SHA-256 `2d36e62549cc4a42fe67709359cdb9b1a8e5097cbb0f63263e380cbfbbd4238b`.
15. `reports/ra4_native_io_screen_wait.md` (Native wait/event handling and Screen boundary), SHA-256 `99a755fa0b14b2cf9b25f9f6596fa1264201b1780bcc1c7df18dedfe53394446`.
16. [Android Open Accessory 1.0](https://source.android.com/docs/core/interaction/accessories/aoa), Android Open Source Project / Google, accessed 2026-09-09.
17. [Test using the Desktop Head Unit](https://developer.android.com/training/cars/testing/dhu), Android Developers / Google, accessed 2026-09-09.
18. [Verifying accessories for Apple devices and services](https://support.apple.com/guide/security/verifying-accessories-sec70a4f377d/web), Apple Platform Security, accessed 2026-09-09.
19. [MFi Program FAQs](https://mfi.apple.com/en/faqs), Apple, accessed 2026-09-09.
20. [Supported third-party applications and protocols](https://www.qnx.com/developers/docs/6.6.0_anm11_wf10/com.qnx.doc.dev_pub.ref_guide/topic/usblauncher_config_supported_applications.html), QNX 6.6 Device Publishers Guide, accessed 2026-09-09.
21. [QNX SDK for Smartphone Connectivity product brief](https://blackberry.qnx.com/content/dam/qnx/products/qnxcar/QNX_SDKForSmartphone_ProductBrief_Online_FINAL.pdf), BlackBerry QNX, accessed 2026-09-09.
22. [AM/DM37x versus OMAP35x comparison](https://www.ti.com/lit/pdf/sprab80), Texas Instruments, accessed 2026-09-09.
23. [Harman BE2800 VP4 NA/CA internal photographs](https://fccid.io/QNG-BE2800/Internal-Photos/VP4-NA-and-VP4-CA-Internal-Photos-1790035), Federal Communications Commission filing mirror, accessed 2026-09-09.
24. [2014 Jeep Grand Cherokee User Guide](https://vehicleinfo.mopar.com/assets/publications/en-us/Jeep/2014/Grand_Cherokee/100303_14_WK_UG_EN_USC_E11_V1_DIGITAL.pdf), Mopar / FCA, accessed 2026-09-09.
25. [Panasonic VP4RAC equipment authorization](https://fccid.io/ACJ-VP4RAC), Federal Communications Commission filing mirror, accessed 2026-09-09.
26. [2018 Uconnect 4C/4C NAV 8.4-inch Radio Book](https://vehicleinfo.mopar.com/assets/publications/en-us/Ram/2018/1500/9353.pdf), Mopar / FCA, accessed 2026-09-09.
27. [Mopar media hub USB port 68294075AC](https://store.mopar.com/oem-parts/mopar-mopar-media-hub-usb-port-68294075ac), Official Mopar eStore, accessed 2026-09-09.
