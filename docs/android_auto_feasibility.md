# Android Auto Feasibility

**Grade B.** A software prototype is technically plausible because RA4 is already a true USB host with the vendor-control, descriptor and bulk primitives AOA needs, and its display/HMI/audio foundations are substantial. Significant unknowns remain: stock-path AOA ownership, a legitimate receiver, installed H.264 decode, PCM/microphone contracts and measured resources.

## Exact blocker

The first blocker is not Internet service or USB device mode; it is proving that a production-compatible RA4 host client can take a phone from normal enumeration through AOA re-enumeration and exchange bidirectional bulk frames without losing the stock cabin path.

## Minimum architecture

| Block | Status |
| --- | --- |
| PHONE | ALREADY PRESENT |
| USB SESSION | PRESENT BUT NEEDS ADAPTER/GLUE |
| PROJECTION PROTOCOL | MISSING SOFTWARE |
| VIDEO DECODER / DISPLAY | UNKNOWN |
| AUDIO ROUTING | PRESENT BUT NEEDS ADAPTER/GLUE |
| MIC / INPUT RETURN | PRESENT BUT NEEDS ADAPTER/GLUE |
| HMI ARBITRATION | PRESENT BUT NEEDS ADAPTER/GLUE |

## Why Android Auto is first

AOA maps directly to RA4's proved host-side vendor-control, descriptor and bulk APIs. The radio does not need USB peripheral mode, an MFi authentication IC or Internet service. The remaining transport uncertainty can be retired with one narrow bench primitive before acquiring a full receiver.

## Authentication and licensing

AOA is an open transport without a dedicated accessory authentication chip. Android Auto remains a Google-controlled production receiver/protocol integration and must be obtained and authorized legitimately; DHU is a development reference, not a redistributable RA4 engine.

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
