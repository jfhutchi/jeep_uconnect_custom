# RA4 USB Execution Surface

A library export or a fixed-purpose production caller is not a caller-controlled execution surface. The classifications below preserve that boundary.

| Surface | Classification | Operations | Concrete route | Production use | New code | Permissions | Remaining unknown |
| --- | --- | --- | --- | --- | --- | --- | --- |
| libusbdi.so.2 host API | REQUIRES NEW CODE | attach and detach callbacks, descriptor reads, configuration and interface selection, endpoint parsing and pipe claims, vendor control, bulk IN and OUT, device and pipe reset | An authorized native host client would link libusbdi and call its documented APIs. | The hash-identified library exports 62 usbd_* functions and fixed-purpose production clients import subsets. | YES | io-usb client access, a device connection, and exclusive ownership of the selected interface | live permissions and ABI for any future legitimately authorized caller |
| enum-usb | PRODUCTION INTERNAL | attach, device, configuration, and interface descriptors, configuration selection, fixed Microsoft OS descriptor vendor query, device and pipe reset, detach | enum-devices invokes enum-usb with check_MS_desc through /etc/system/enum/common. | Classifies devices and applies fixed enum-usb.conf quirks, including Apple configuration selection and NoMSString exceptions. | YES | runs inside the stock enumeration lifecycle | no structured extension or plug-in interface accepting arbitrary AOA requests was recovered |
| usb descriptor utility | TEST/DIAGNOSTIC | topology, attach, stored or live descriptor reads | usb displays stored or live standard and vendor-unique descriptors for selected bus/device numbers. | Diagnostic descriptor display only; it imports no vendor setup, bulk, reset, configuration selection, or endpoint claim API. | YES | target shell plus io-usb access | legitimate interactive shell availability on a normal unit |
| usb_hub_oc | PRODUCTION INTERNAL | hub topology, hub port status, hub feature requests, port-power recovery | boot.sh starts usb_hub_oc to poll hub status and restore port power after overcurrent. | Monitors hub overcurrent and re-enables port power. | YES | stock startup context and hub access | which recovered binary variant resolves at runtime and which physical cabin hub port it controls |
| usbPowerSwitch | TEST/DIAGNOSTIC | electrical disconnect and reconnect candidate | usbPowerSwitch -p0/-p1 requests the stock USB power path to turn off or on. | Fixed power-control helper; it does not link libusbdi and cannot issue AOA requests or bulk transfers. | YES | target process execution and stock USB power-control service availability | electrical effect on the cabin port and legitimate interactive invocation surface |
| devb-umass | PRODUCTION INTERNAL | bulk IN and OUT, class-specific vendor/control requests, pipe and device reset, detach | enum rules launch devb-umass for class-08 devices with fixed bus/device/interface arguments. | USB mass-storage block driver using SCSI/CAM semantics. | YES | mass-storage interface match and exclusive class-driver claim | none of its fixed class command surface maps to AOA identity or arbitrary bounded frames |
| devc-serusb | PRODUCTION INTERNAL | bulk IN and OUT, class/vendor setup, pipe and device reset, detach | enum rules launch devc-serusb for enumerated serial/modem VID/PID matches. | USB serial/modem character driver. | YES | matching serial interface and exclusive class-driver claim | no general transfer service or AOA rule was recovered |
| io-fs-media / iofs-pfs.so MTP handler | PRODUCTION INTERNAL | descriptor and interface selection, vendor/control requests, bulk IN and OUT, pipe and device reset, detach | MTP and MTPZ enum rules launch io-fs-media -dpfs, which loads iofs-pfs.so and claims the matched interface. | Implements PTP/MTP command/data/event transport and filesystem/media presentation. | YES | MTP/MTPZ match and exclusive media-driver ownership | exact scheduling race between the enum match and interface claim on a live phone |
| iofs-usb-ipod.so legacy Apple handler | PRODUCTION INTERNAL | descriptor reads, configuration selection, vendor/control and interrupt transfers, pipe handling, detach | Apple-specific enum-usb configuration selects an iPod configuration, then io-fs-media loads iofs-usb-ipod.so. | Legacy iPod HID/audio/media integration, not AOA or a projection receiver. | YES | Apple VID/configuration match and media-driver ownership | exact iPod protocol generation; no Android or general raw-transfer contract |
| connmgr USB detector | PRODUCTION INTERNAL | attach and detach observation, device descriptors and strings | connmgr attaches to io-usb, reads device descriptors/strings, applies fixed JSON rules, and publishes selected device events. | Tracks selected USB, MCD, file, and DBus device properties; unhandled USB tracking is disabled. | YES | stock service context; fixed rule configuration | no raw USB IPC extension point was identified |
| ConnMgr test utilities | TEST/DIAGNOSTIC | connectivity-service method invocation | CcmTestService and CallMethod.sh can invoke fixed connectivity test methods when that test service is active. | Already-installed test assets, with no AOA or raw USB method vocabulary. | YES | test-service activation and SvcIPC/DBus access | whether the test service is normally started; irrelevant to missing USB methods |
| phoneProjectionService / DeviceConnectionManager destinations | UNREACHABLE | projection start request, projection and device status events | MainSupplement.swf attempts ModuleLink commands/events through hmiGateway. | Dormant HMI client contract retained in the recovered build. | YES | would require a supported gateway destination and an installed service owner | owner executable, object/interface, package, variant, and USB responsibilities |
| resident Java/Xlet/JNI surface | UNREACHABLE | none recovered for direct USB host control | Existing Xlets run through AMS with fixed signed policy and available Java/native APIs. | Existing applications have no proved direct USB host operation surface. | YES | stock package identity, AMS policy, and any native wrapper entitlement | private dynamically resolved code outside the bounded recovered corpus |

## Phase-7 decision

**B** — No existing stock-authorized process or service exposes a caller-controlled route that combines arbitrary AOA vendor requests, detach/re-enumeration ownership, accessory-interface claiming, and bounded bulk IN/OUT. The matching libusbdi primitives exist, but executing a new native caller is blocked by the unresolved legitimate signing/authorization environment.

External instrumentation: A passive analyzer can answer whether the hub forwards traffic only after some authorized host originates that traffic. A transparent active interposer could act as the AOA host, but that would prove phone-plus-hub wiring behavior, not RA4-originated control, RA4 ownership, or RA4 bulk I/O; it therefore does not justify classification C.

## Recovered artifact anchors

All paths are relative to the read-only `RA4_CORPUS` alias; they do not disclose or depend on a local absolute path.

| Path | Bytes | SHA-256 | Locator |
| --- | --- | --- | --- |
| hidden_hbc_ifs/standard_boot/files/bin/io-usb | 128629 | 3ac3777b8986c6aebd3c0d226715ee8fa935895c2ee5775bc874ceef569cd3f4 | stock USB host process named by boot.sh |
| hidden_hbc_ifs/standard_boot/files/bin/boot.sh | 29268 | c801d473b0b49e8242114635f4022cc67ccbe03093fec188de3b7188dd636ecf | USB host and hub-monitor startup commands |
| hidden_hbc_ifs/standard_boot/files/lib/dll/devu-omap3530-mg.so | 45936 | 6916bd0f398f28bf111ace6c3a08e425a90127f283e0105e2bb6f0b58df881a1 | OMAP USB host-controller driver loaded by io-usb |
| hidden_hbc_ifs/standard_boot/files/lib/dll/devu-ehci-omap3.so | 40215 | 4e267106c1f209e9b32c596d2d04f39d3ee2d3337d0d5601f74f58a33114c03e | EHCI USB host-controller driver loaded by io-usb |
| hidden_hbc_ifs/segment_001a0000/files/lib/dll/libusbdi.so.2 | 47302 | 08c1de09a0ea97da4481275dcdf8191efba7208544fee4f6757a57f48f1b3923 | USB host API exports and fixed-purpose import consumers |
| hidden_hbc_ifs/segment_001a0000/files/bin/enum-usb | 22594 | b07b6a8ff791f46f6db5988df77cd3a509c8d22265ff54fe2c581212b605b460 | stock USB enumerator and Microsoft OS descriptor query client |
| hidden_hbc_ifs/segment_001a0000/files/bin/usb | 30961 | 10627356ba9a83acc8baa18d273dd1f48a12f9799ae6721640e6279a32b1c560 | installed descriptor/topology diagnostic utility |
| hidden_hbc_ifs/segment_001a0000/files/usr/bin/usb_hub_oc | 16648 | 5efe54280bdcbe73c15f62156f11c46db273a8441df8f7f5b2b48fd1c0b03c1c | boot-selected hub overcurrent monitor candidate |
| hidden_hbc_ifs/segment_001a0000/files/usr/bin/usbPowerSwitch | 8226 | 9290f73bd2e5248a6fb0675919a3157ff1e9ce899b6b33b5b5591c79bb6979e4 | fixed USB power-control diagnostic helper |
| hidden_hbc_ifs/segment_001a0000/files/bin/devb-umass | 45394 | 98996317b2efb961f1ffb94fcc55cf75dd94c82f558f220a3f6f0af5a7db658b | fixed-purpose USB mass-storage class driver |
| hidden_hbc_ifs/segment_001a0000/files/bin/devc-serusb | 125795 | 3bd75f39baace1141fcc7cc731e07c18a2f275888bae0b622763b8e0354c5e17 | fixed-purpose USB serial class driver |
| hidden_hbc_ifs/segment_001a0000/files/bin/hmiGateway | 153124 | 8d7fe8789bb012a66fbebd1bd44eefa506c672a5d70c90fbf92b3a5a6f01ec82 | fixed destination dispatch and owner-subscription gateway |
| hidden_hbc_ifs/segment_001a0000/files/etc/enum-usb.conf | 762 | 7b77902d6a23b670d1e9989f57321d60b8669148c12c7823693e22221620b7bb | fixed USB enumeration quirks and configuration selection |
| hidden_hbc_ifs/segment_001a0000/files/etc/system/enum/common | 280 | bb84dc4cbb0beadb693167f97ceea397b39f7f76b1c01579458a9fc6a105bcc5 | enum-devices invocation of enum-usb check_MS_desc |
| hidden_hbc_ifs/segment_001a0000/files/etc/system/enum/devices/usb/mtp | 933 | 41d2345596e0b7efcc05110dcd1204c2b2cc0d5890913794a01b6ed7586ca9a0 | generic MTP and MTPZ io-fs-media launch rules |
| hidden_hbc_ifs/segment_001a0000/files/etc/system/enum/devices/usb/ipod | 590 | 6786b05e8a2f1089854e253cfdd527a532496baf623daab35433d5de3dee4b1d | legacy Apple media-handler launch rules |
| hidden_hbc_ifs/segment_00f20000/files/bin/connmgr | 262855 | 1d40e0762f50d89c29a866e8106bdf1c6d35546cff2e9f1c4956e366daf89a36 | stock device-connection observer and rule consumer |
| hidden_hbc_ifs/segment_00f20000/files/lib/dll/iofs-pfs.so | 117594 | 453002e0715fe2e84d6890092df115895d4a1b1309e6969b5ca27a867d8c8e35 | MTP/PTP interface claim and bulk transport implementation |
| hidden_hbc_ifs/segment_00f20000/files/lib/dll/iofs-usb-ipod.so | 19937 | 087cb7e158248cc0345fed2f50a5c3223ced2faf1b413cb31c686dc7a84714ec | legacy Apple USB media transport implementation |
| hidden_hbc_ifs/segment_00f20000/files/etc/system/config/connmgr_P_1_2.json | 7797 | 417f3a481f24de077c2faa699ea288c2d3999984301f6b7a5ae199ff11bbe718 | boot-selected connection-manager rules and unhandled-device policy |
| hidden_hbc_ifs/segment_00f20000/files/etc/system/config/connmgr_P_2_2.json | 22921 | 31e8236f5ced6770cc5a026fe98adba0cf47aec07a25c4d389855c7cfced0546 | alternate connection-manager rules including iPod/media devices |
| primary_iso/usr/share/MMC_IFS_EXTENSION/bin/usb_hub_oc | 19595 | 15a6d1a3b9de2a123236e11cb32931e2cdd491c0ca8d394ff4a874094b7b0bb6 | alternate installed hub overcurrent monitor |
| primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/MainSupplement.swf | 1407783 | e9d796ea4b4c83ed518bfe3b3c341e54e510a1ae0f78ebbffbd655b7c36a3258 | ROV HMI client carrying the dormant projection contract |
| primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/ModuleLink.xml | 115 | 46cacc8e084ba4b3024cdf68191da1b7165754cc2bedbc2bf44949a9ab59e533 | ROV ModuleLink destination configuration |

## Sources

1. `reports/ra4_usb_stack_backend_census.md` (Hash-identified host runtime; host reproduction and limits), SHA-256 `cd2dbf9b4573bd2c776ddd80bcb165a9cacd942c6d7c124e8f9a21270432897c`.
2. `reports/ra4_projection_gateway_dispatch.md` (Fixed destination dispatch; USB ownership follow-up), SHA-256 `41bf4406ae9ee28e748e7a3d422a9e79572ef520c462c51c7fefc45f7b85a813`.
3. `reports/ra4_usb_phy_power_control.md` (usbPowerSwitch and hub/power control-flow trace), SHA-256 `81ee93fa8506290079a6122bd8c1aacf41f67f777ccfadbe5a7b8253539421ef`.
4. `docs/19_ra4_media_hub_usb_path.md` (Connector evidence; active hub boundary; exact unknowns), SHA-256 `1ee9c0b337010a7ade28bfbccb81e8e787965b4d96f15c736c24984f8318085a`.
5. `reports/resident_policy_entitlements.md` (Resident policy entitlement matrix), SHA-256 `41bde2899dd53bd445a1bfa584f3e1a10e2a4f57e5cc9b2a5fe1ca0a69a60257`.
6. `docs/wired_projection_feasibility.md` (Authoritative feasibility conclusion and evidence ledger), SHA-256 `886c7f29b181574f71308464d77c3bb5fbda5e0dc3d8af6a18ccf98e42818380`.
7. [Android Open Accessory 1.0](https://source.android.com/docs/core/interaction/accessories/aoa), Android Open Source Project / Google, accessed 2026-09-09.
8. [Android Open Accessory 2.0](https://source.android.com/docs/core/interaction/accessories/aoa2), Android Open Source Project / Google, accessed 2026-09-09.
9. [USB accessory overview](https://developer.android.com/develop/connectivity/usb/accessory), Android Developers / Google, accessed 2026-09-09.
10. [QNX SDP 6.5.0 SP1 USB DDK API index](https://www.qnx.com/developers/docs/6.5.0SP1.update/index.html), QNX Software Systems, accessed 2026-09-09.
