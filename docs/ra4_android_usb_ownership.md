# RA4 Android USB Ownership

## Current owner

On a generic Android phone that advertises the Microsoft-compatible MTP identifier, enum-devices invokes enum-usb check_MS_desc, the MTP rule launches io-fs-media -dpfs for the selected bus/device/interface, and iofs-pfs.so becomes the bulk-transfer owner. connmgr observes only configured USB classes and has trackUnhandledUsbDevice=0; it is not the generic MTP bulk owner.

```text
phone attach through cabin hub -> io-usb/HCD enumeration -> enum-devices invokes enum-usb check_MS_desc -> descriptor and Microsoft-compatible-ID classification -> MTP/MTPZ rule launches io-fs-media -dpfs -> iofs-pfs selects and claims the MTP interface -> bulk media operations -> detach callback, abort/release, and driver exit
```

## AOA interception point

The AOA negotiator must receive the initial device after descriptor/MS-OS classification but before the MTP/MTPZ rule launches io-fs-media and iofs-pfs claims the interface. After START_ACCESSORY detach, the same owner must recognize 18D1:2D00/2D01 before normal unknown-device disposal and claim the first accessory bulk interface.

Narrowest required ownership change: Add an authorized pre-MTP AOA classifier/owner that gets first refusal for eligible phones, suppresses the MTP launch during negotiation, survives logical detach as service state, recognizes Google accessory re-enumeration, and releases back to normal enumeration on failure. No stock configuration change is authorized by this report.

Google's AOA documentation states that AOA and MTP cannot be active simultaneously. The stock MTP/MTPZ driver must therefore not retain the phone interface across the AOA switch.

## Cabin media hub

**STRONGLY SUPPORTED.** The active 68141322AA/68289895AA SD/USB/AUX module already carries downstream device enumeration, standard and class/vendor control traffic, disconnects, and sustained MTP/iPod/mass-storage data over one radio-facing USB path. AOA keeps the radio as host, so no CarPlay-style role reversal is required and no recovered filtering rule targets Google accessory IDs.

Limit: Exact hub or mux silicon, packet-level behavior, C2-to-controller routing, power budget, Google VID/PID observation, and physical AOA traffic remain unobserved; this is strong architectural support, not PROVED TRANSPARENT.

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
