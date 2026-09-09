# RA4 USB Architecture

This is a static, read-only architecture closure. It proves a configured USB host stack; it does not claim a working projection receiver.

## Controller and role

- Controller paths: QNX io-usb with devu-omap3530-mg.so (Mentor/MUSB OTG block, 0x480ab000, IRQ 92) and devu-ehci-omap3.so (EHCI, 0x48064800, IRQ 77)
- Host proof: Production startup arguments, two host HCDs, libusbdi.so.2 exports, and stock imports prove true host operation independently of media playback.
- Device role: OMAP3730 silicon is dual-role, but the installed QNX device stack, DCD, descriptors and cabin-port peripheral-mode route are UNKNOWN.
- Media hub: The 68141322AA/68289895AA SD/USB/AUX module is active; host transparency is plausible, while CarPlay role reversal and VBUS behavior are UNKNOWN.

## Phone-insertion call graph

```text
PHONE INSERTION: 68141322AA/68289895AA active media hub -> UCI cable -> Radio C2 D2784B [ALREADY PRESENT]
-> USB ENUMERATION: io-usb -> Mentor/MUSB or EHCI OMAP3 HCD -> libusbdi attach/descriptor APIs [ALREADY PRESENT]
-> DEVICE CLASSIFICATION: enum common + six USB rules -> MTP, iPod HID/audio, serial/network or mass-storage client [ALREADY PRESENT]
-> SERVICE: connmgr/io-fs-media/iPod media clients exist; AOA negotiator and projection receiver do not [PRESENT BUT NEEDS ADAPTER/GLUE]
-> MEDIA/HMI: phoneProjectionService/DeviceConnectionManager client vocabulary exists, but hmiGateway rejects both destinations [PRESENT BUT NEEDS ADAPTER/GLUE]
```

## Class and protocol inventory

| Capability | Status | Evidence |
| --- | --- | --- |
| USB host enumeration/hotplug | ALREADY PRESENT | usb-true-host |
| descriptor/config/interface parsing | ALREADY PRESENT | usb-host-stack |
| vendor control and bulk endpoints | ALREADY PRESENT | usb-arbitrary-bulk |
| mass storage | ALREADY PRESENT | usb-stock-classes |
| MTP/MTPZ | ALREADY PRESENT | usb-stock-classes |
| PTP | UNKNOWN | usb-stock-classes |
| legacy iPod/iPhone media | ALREADY PRESENT | apple-legacy |
| iAP2 | MISSING SOFTWARE | iap2-negative |
| USB audio and Apple HID class handling | ALREADY PRESENT | usb-stock-classes |
| generic HID injection to projection | MISSING SOFTWARE | button-input |
| Android Open Accessory negotiation | MISSING SOFTWARE | aoa-ra4-gap |
| RNDIS/USB networking rules | ALREADY PRESENT | usb-stock-classes |
| QNX USB device/function stack | MISSING SOFTWARE | iap2-negative |
| MFi authentication device | UNKNOWN | ra4-auth-hardware |

## Bounded negative searches

| Search | Roots | Terms | Limits | Result |
| --- | --- | --- | --- | --- |
| named-projection-runtime | analysis_ra4_18.45.01/work/installer_iso, analysis_ra4_18.45.01/work/primary_iso, analysis_ra4_18.45.01/work/secondary_iso, analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/files, analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files, analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files, analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_019a0000/files | androidauto, libaoa, autoreceiver, CarPlay receiver, Cinemo projection artifact, MirrorLink, SmartDeviceLink | 4,110 files; 578 ELF files; 321 ZIP/JAR containers; 91,086 member names; ELF dynamic metadata plus the controlled raw-marker census. Static-linked, renamed, encrypted, compressed-content-only, optional, or unmaterialized implementations remain outside the negative. | No named production projection receiver/backend was identified. Dormant HMI vocabulary was identified separately. |
| apple-device-stack | the same seven recovered 18.45.01 roots | iAP2, Probe_iAP2, RoleSwap_DigitaliPodOut, RoleSwap_AppleDevice, usblauncher, io-usb-dcd, devu-dcd, devu-usbumass-*, libusbdci, Device_Stack | 122 controlled markers across the recovered trees plus structured path, archive-member, dependency, import and export inspection. Generic filenames and stripped/static code remain limitations. | Legacy iPod host components were present, but no named iAP2 role-swap/device-function bundle or CarPlay receiver was found. |
| android-aoa-rules | hidden_hbc_ifs/segment_001a0000/files/etc/system/enum/common, hidden_hbc_ifs/segment_001a0000/files/etc/system/enum/devices/usb/*, primary_iso/usr/share/MMC_IFS_EXTENSION/bin/enum_devices.lua | 18D1:2D00, 18D1:2D01, AOA, OpenAccessory, ACCESSORY_START | One common file, six production USB rule files and the selected text Lua helper. Other processes, runtime-generated rules and generic/stripped implementations are outside the negative. | No explicit AOA ownership or personality-switch rule was identified. |
| h264-runtime | seven recovered 18.45.01 roots, 85 tracked text/source blobs at the earlier hardware checkpoint | H.264, AVC, OpenMAX, libOMX, Codec Engine, DSPLink, GStreamer, libavcodec | Controlled raw markers, filenames, dynamic metadata and tracked text. Unknown names, stripped/static implementations and codec capability hidden behind generic media APIs remain limitations. | No supported installed H.264 decode client path or ABI was proved. |

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
