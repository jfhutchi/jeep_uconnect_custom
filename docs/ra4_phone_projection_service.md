# RA4 Phone Projection Service Contract

This report covers only the contract's relationship to USB ownership. It does not claim that a projection receiver is installed.

| Element | Recovered expectation |
| --- | --- |
| phoneProjectionService | The HMI expects startProjection with opaque ppId and subscribes to projectionSessionStatus, projectionBackToCar, now-playing, navigation, call, and device status. It checks service-owner availability through the shared ModuleLink span client. |
| DeviceConnectionManager | A separate ModuleLink/SvcIPC destination supplies projection-device status through DCM events. Exact projection device enum values and an owner implementation were not recovered. |
| USB relationship | No recovered command, argument, event, or owner proves that phoneProjectionService or DeviceConnectionManager performs AOA, MTP arbitration, USB role management, or endpoint ownership. The contract is a designed insertion point for projection lifecycle/status, while its USB implementation remains absent or outside the bounded corpus. |
| Gateway | The recovered hmiGateway fixed destination table rejects phoneProjectionService and DeviceConnectionManager before command invocation, nameHasOwner, or owner-change subscription. Registering those names alone would not make the route reachable. |
| Expected owner | A missing optional, variant, licensed, or shared/newer Harman projection backend is the evidence-supported inference. The CMC_MY16_Trunk provenance and Cinemo/GAL vocabulary are leads, not proof of deployment or Android USB ownership. |

The designed insertion point is compatible with a projection backend owning device classification and session status, but no recovered method proves that either dormant destination performs AOA negotiation.

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
