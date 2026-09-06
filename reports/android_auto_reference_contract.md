# Android Auto reference transport contract

Date: 2026-09-06. Original synthesis of the independent PC bench, incorporated
into canonical draft PR #14. No phone, PC USB driver or RA4 operation was run
for this integration. This is an observable contract, not a receiver protocol
implementation or an analysis of Google's proprietary receiver.

## Provenance and separation

Source: [PR #15](https://github.com/jfhutchi/jeep_uconnect_custom/pull/15), branch
`codex/android-auto-dhu-bench`, reviewed at
`93747c8a63b37dff514d67bb4b713e48cba4b310`. The source
[report](https://github.com/jfhutchi/jeep_uconnect_custom/blob/93747c8a63b37dff514d67bb4b713e48cba4b310/reports/android_auto_dhu_usb_bench.md)
and [PnP helper](https://github.com/jfhutchi/jeep_uconnect_custom/blob/93747c8a63b37dff514d67bb4b713e48cba4b310/analysis_tools/android_auto_usb_snapshot.ps1)
were read in full. The helper selects present Samsung/Google USB nodes, emits
allowlisted USB tokens and driver metadata, and omits serial-bearing instance
suffixes. It neither issues USB requests nor changes drivers. It was reviewed,
not executed or copied into the canonical line.

PR #15 began at `9eb28ad2c9d06753c1b0ec59a251c804b70b4b52`. Its history,
Windows experiments, tools and private observations remain independent. No
merge or cherry-pick was used. PROVED below means observed by that documented
experiment; it is not a new independent reproduction in this run.

## Two reference paths, with different terminal states

```text
DIRECT USB, PC REMAINS HOST
Samsung SM-S931U / Android 16, 04E8:6860
  -> DHU reports AOA protocol v2 accepted
  -> phone disconnects/re-enumerates as 18D1:2D01
  -> interface 0, bulk IN 0x81 / OUT 0x01 reported by DHU
  -> Windows confirms accessory VID/PID
  -> Android independently reports accessory,adb
  -> transport read/write failure [STOP: no direct protocol/TLS/video proof]

DEVELOPMENT ADB TUNNEL
same phone, ordinary 04E8:6860 / mtp,adb
  -> owner-authorized Android Auto development head-unit server + ADB tunnel
  -> Android Auto protocol 1.7 negotiated
  -> TLS 1.2 handshake and verification succeeded
  -> visible projection dashboard
  -> tap changes dashboard to launcher
  -> clean exit; another successful session after tunnel recreation
```

These paths cannot be concatenated into a successful direct-USB session.
AOA protocol version 2 is different from Android Auto protocol version 1.7.
USB ACCESSORY ENUMERATION, ANDROID AUTO PROTOCOL SESSION and VISIBLE PROJECTION
are three separate gates. A successful process exit or generic connection
message is insufficient evidence for any later gate.

## Transport observations and required adapter behavior

| State/transition | Observed reference | Implementation-neutral requirement |
| --- | --- | --- |
| Normal attachment | Samsung `04E8:6860` | Identify the selected phone on its physical attachment path; do not probe unrelated vehicle devices. |
| Accessory support | DHU reports AOA v2 | Obtain a supported protocol response; timeout/error remains a failed gate. The bench did not capture the individual control packets. |
| Accessory start | Real change to `18D1:2D01` | Treat re-enumeration as loss of the old handle and discover the new device; do not reuse stale endpoints. |
| Interface discovery | Interface 0, `0x81` IN / `0x01` OUT in DHU log | Read actual configuration/interface/endpoint descriptors. Those addresses are this phone's observation, not universal constants. |
| Separate debugging interface | ADB on interface 1 after transition | Accessory data and ADB are distinct. Production projection must not depend on developer mode or an ADB tunnel. |
| Bulk access | Discovery succeeded, sustained transport failed | Prove supported ownership/claim, bidirectional transfers and detach cancellation before claiming transport success. |
| Android Auto session | Only the ADB path passed | Use an authorized receiver/provider to establish protocol, TLS, media and input services. Do not infer credentials or protocol implementation from logs. |
| Return to normal USB | Owner reconnect restored Samsung configuration/bindings | Restoration must be observed; this bench does not prove unattended direct-session recovery. |

Google's [AOA specification](https://source.android.com/docs/core/interaction/accessories/aoa)
documents support discovery, identifying strings, accessory start and subsequent
bulk-endpoint discovery. Its public control requests are 51/52/53. The head unit
is the USB host; the Android phone exposes the accessory function. AOA does not
require the RA4 to run a USB device-controller stack. Specification requirements
are reference evidence, not a packet capture of this bench. `18D1:2D00` is the
accessory-only alternative; it was not observed here. Do not copy DHU/OEM
identity strings into a product; an authorized provider must supply its own
supported integration contract.

## PC compatibility limit

The unchanged Google DHU 2.0 executable initially failed with its old bundled
libusb. An isolated substitution of upstream libusb 1.0.30 passed AOA discovery
and transition. The source report independently records Windows accessory
MI_00 bound to MTP/WUDFWpdMtp and ADB MI_01 bound to WinUSB.

- PROVED: this PC/phone reached accessory mode and then transport errors.
- HIGH: old library support for Samsung's composite driver explains the first
  blocker. MTP binding is the leading subsequent access blocker, not a causal
  conclusion verified by a successful driver replacement.
- UNKNOWN: direct Android Auto session, seamless reconnect, measured audio
  quality, full descriptors, bus speed, electrical behavior and RA4 equivalence.

No Windows failure is assigned to QNX. The development ADB success is a
known-good phone/session reference, and direct AOA is a known-good enumeration
reference. There is still no known-good direct USB projection session.

## Canonical use

Use the [PC-versus-RA4 gate matrix](../docs/20_projection_transport_gate_matrix.md)
as the primary decision artifact. The [structured RA4 census](ra4_usb_stack_backend_census.md)
records which installed host APIs can support a future authorized AOA client.
Missing DCD evidence remains relevant to the separate legacy wired CarPlay
role-swap route. No local RA4 capability gate has failed by measurement, so
external compute is not selected.
