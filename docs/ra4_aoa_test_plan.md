# RA4 AOA Test Plan

**NOT TARGET VERIFIED.** Phase 7 does not provide an authorized target caller. The executable test harness is a host-only state-machine model.

## Deterministic parameters

| Parameter | Value |
| --- | --- |
| Identity | six fixed harmless strings: Owner Lab, RA4 AOA Probe, Bounded transport test, 1.0, example.invalid URI, and RA4-AOA-0001 |
| Control timeout | 1000 ms |
| Detach/re-enumeration timeout | 5000 ms |
| Maximum frame | 256 bytes |
| Request | RA4-AOA-PING |
| Response | RA4-AOA-PONG |
| Recovery | abort and close pipes, release the claimed interface/device, preserve the primary error, then accept one clean fresh-device reconnect |

## Physical execution gate

No existing stock-authorized process or service exposes a caller-controlled route that combines arbitrary AOA vendor requests, detach/re-enumeration ownership, accessory-interface claiming, and bounded bulk IN/OUT. The matching libusbdi primitives exist, but executing a new native caller is blocked by the unresolved legitimate signing/authorization environment.

Do not run a physical test until an existing authorized caller or a legitimate native development environment supplies the exact control, ownership, and bulk operations. Passive traces may validate hub behavior but cannot establish RA4-originated AOA negotiation.

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
