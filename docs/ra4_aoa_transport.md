# RA4 Android Open Accessory Transport

**Phase-7 classification: B. Physical AOA transport: NOT PROVED.**

## Conclusion

There is no complete legitimate AOA execution surface in the bounded recovered RA4 build. The closest components are fixed-purpose production-internal clients: enum-usb can issue a Microsoft OS descriptor vendor request and select configurations; iofs-pfs, devb-umass, and devc-serusb can perform class-bound bulk/control/reset operations; usb_hub_oc and usbPowerSwitch can monitor or cycle USB power. None accepts the structured AOA sequence or arbitrary deterministic bulk frames.

Exact blocker: No existing stock-authorized process or service exposes a caller-controlled route that combines arbitrary AOA vendor requests, detach/re-enumeration ownership, accessory-interface claiming, and bounded bulk IN/OUT. The matching libusbdi primitives exist, but executing a new native caller is blocked by the unresolved legitimate signing/authorization environment.

The recovered host stack is sufficient in principle for AOA control and bulk operations. This is an API-capability conclusion, not execution authority or physical transport proof.

## Exact AOA control sequence

| State | bmRequestType | bRequest | wValue | wIndex | Payload | Expected | Timeout | Failure |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GET_PROTOCOL | 0xC0 | 51 | 0 | 0 | 2-byte IN buffer; no OUT payload | exactly two bytes containing protocol version 1 or 2 in little-endian order | 1000 ms | on stall, timeout, short response, zero, or unsupported version, release and wait for a new attachment |
| SEND_STRING_0 | 0x40 | 52 | 0 | 0 | NUL-terminated UTF-8 manufacturer string, at most 256 bytes including NUL | complete control OUT transfer | 1000 ms | abort the sequence and release the device |
| SEND_STRING_1 | 0x40 | 52 | 0 | 1 | NUL-terminated UTF-8 model string, at most 256 bytes including NUL | complete control OUT transfer | 1000 ms | abort the sequence and release the device |
| SEND_STRING_2 | 0x40 | 52 | 0 | 2 | NUL-terminated UTF-8 description string, at most 256 bytes including NUL | complete control OUT transfer | 1000 ms | abort the sequence and release the device |
| SEND_STRING_3 | 0x40 | 52 | 0 | 3 | NUL-terminated UTF-8 version string, at most 256 bytes including NUL | complete control OUT transfer | 1000 ms | abort the sequence and release the device |
| SEND_STRING_4 | 0x40 | 52 | 0 | 4 | NUL-terminated UTF-8 URI string, at most 256 bytes including NUL | complete control OUT transfer | 1000 ms | abort the sequence and release the device |
| SEND_STRING_5 | 0x40 | 52 | 0 | 5 | NUL-terminated UTF-8 serial string, at most 256 bytes including NUL | complete control OUT transfer | 1000 ms | abort the sequence and release the device |
| START_ACCESSORY | 0x40 | 53 | 0 | 0 | none | complete zero-length control OUT transfer followed by device detach | 1000 ms | on stall, timeout, or no detach within 5000 ms, release and fail without retrying in place |

After START_ACCESSORY, wait for detach and re-enumeration as `18D1:2D00` or `18D1:2D01`, select configuration 1, claim the first accessory interface's bulk IN/OUT endpoints, exchange only the bounded deterministic test frames, release, and test a clean reconnect.

## Physical success criteria

| Criterion | Proved | Evidence |
| --- | --- | --- |
| phone physically enumerates through the cabin USB/hub path | NO | stock media devices use the path, but no controlled Android AOA observation was performed |
| GET_PROTOCOL succeeds | NO | API compatibility only; request 51 was not issued on RA4 |
| START_ACCESSORY succeeds | NO | API compatibility only; request 53 was not issued on RA4 |
| phone re-enumerates into accessory mode | NO | not physically observed on RA4 |
| expected Google VID/PID is observed | NO | no RA4 observation of 18D1:2D00 or 18D1:2D01 |
| bulk endpoints are claimed | NO | non-AOA class drivers claim bulk endpoints; no AOA claim occurred |
| RA4-side host transmits data | NO | non-AOA bulk capability only; no AOA frame was transmitted |
| phone-side endpoint transmits data | NO | not physically observed on RA4 |
| deterministic frames succeed in both directions | NO | host mock testing only after the Phase-7 B decision |
| clean detach/reconnect works | NO | generic stock cleanup exists, but no AOA detach/reconnect was exercised |

## One next engineering objective

**Establish a legitimate native execution/development environment on a spare RA4.** An authorized QNX 6.5 ARM32 host client can run on the spare RA4, obtain the cabin-phone USB device before MTP, and execute bounded libusbdi control and bulk operations with clean recovery. Constraints: Use an owner-authorized spare radio and an OEM/provider-supported signing, packaging, or development path; do not bypass signing, AMS/DRM, trust, firmware, or vehicle configuration.

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
