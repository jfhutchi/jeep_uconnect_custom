# 17 - QNX 6.6 Apple CarPlay transport reference

Updated 2026-09-06. This note closes one narrow engine-generation question with
official QNX 6.6-era documentation and separates USB transport enablement from
the licensed CarPlay receiver. It is reference research only. No USB rule,
descriptor, PPS object, radio service, or target file was read or changed.

## Result

**CONFIRMED REFERENCE:** the QNX SDP 6.6 / Apps and Media device-publisher
documentation explicitly includes Apple CarPlay support in `usblauncher`.
The documented sequence starts the USB host stack to identify the iPhone, sends
`RoleSwap_DigitaliPodOut`, stops host mode after success, and starts the
`io-usb-dcd` device stack. QNX directs automotive integrators to their Project
Manager or QNX support for the required iOS drivers.

**CONFIRMED SILICON / UNKNOWN BOARD+BSP:** TI's OMAP36xx/37xx documentation
confirms that the SoC USB OTG block supports host/peripheral operation. QNX's
public OMAP3730 BSP table lists USB OTG only as host, so the installed custom
DCD and physical port wiring remain decisive.

**UNKNOWN ON RA4:** tracked RA4 evidence establishes QNX USB infrastructure,
`libusbdi`/usbd use, `itun`, legacy `libipod`, and stock HMI CarPlay
references. It does not yet establish `usblauncher`, `io-usb-dcd`, the role
swap rule, descriptors, required private drivers, or a CarPlay receiver in the
18.45.01 runtime.

**ENGINE CONSEQUENCE:** the public Smartphone Connectivity 2.0 binaries remain
rejected as a direct QNX 6.6 candidate, but it is no longer accurate to treat
all pre-7.x CarPlay enablement as undocumented. A supported QNX 6.6-generation
Apple transport path existed. The complete receiver, program authorization,
RA4 BSP/controller support, and target resource fit still require QNX/Apple
evidence.

## Official QNX 6.6 flow

```text
iPhone attaches
  -> io-usb host stack detects device
  -> usblauncher reads descriptors
  -> RoleSwap_DigitaliPodOut request
  -> iPhone becomes USB host
  -> QNX target stops host stack
  -> QNX target starts io-usb-dcd device stack
  -> automotive iOS driver(s) supplied through QNX support
  -> CarPlay receiver/projection manager
  -> HMI, Screen, touch, audio and session integration
```

Only the first seven lines are established as a QNX 6.6 reference transport
sequence. The final two lines are architectural requirements; the public page
does not identify the receiver binary, service ABI, license package, or target
footprint.

Primary sources:

- QNX 6.6 Supported third-party applications and protocols:
  https://www.qnx.com/developers/docs/6.6.0_anm11_wf10/com.qnx.doc.dev_pub.ref_guide/topic/usblauncher_config_supported_applications.html
- QNX 6.6 usblauncher service:
  https://get.qnx.com/developers/docs/6.6.0.update/com.qnx.doc.dev_pub.ref_guide/topic/usblauncher.html
- QNX 6.6 device object:
  https://www.qnx.com/developers/docs/6.6.0.update/com.qnx.doc.dev_pub.ref_guide/topic/usblauncher_device.html
- QNX 6.6 release notes correcting the CarPlay host-first sequence:
  https://www.qnx.com/developers/articles/rel_5849_7.html

The QNX device object documents `role_swap` values `AppleDevice` for iAP2
client mode and `DigitaliPodOut` for CarPlay. The release note explicitly
states that the host stack must detect/request the switch before the device
stack runs. These details make the recovered-tree search more discriminating
than a generic `carplay` string.

## RA4 comparison

| Layer | RA4 evidence | Current conclusion |
| --- | --- | --- |
| USB host stack | QNX `io-usb`, `libusbdi` and factory USB utility evidence | CONFIRMED infrastructure, not CarPlay |
| Apple accessory/media | `itun`, `libipod` and legacy Apple media integration | CONFIRMED adjacent capability, not receiver |
| stock HMI | `isSourceCarPlay`, `enableCarplay`, `IPhoneProjection`, session/event/screen references | CONFIRMED dormant integration vocabulary |
| USB role swap | no tracked `RoleSwap_DigitaliPodOut` or `io-usb-dcd` proof | UNKNOWN pending recovered-tree census |
| receiver/manager | `phoneProjectionService` expected by HMI; implementation not located | UNKNOWN |
| authorization | Apple MFi status and QNX licensed drivers/components required | EXTERNAL_EVIDENCE_REQUIRED |
| resource fit | no component sizes or RA4 runtime measurements | MEASUREMENT_REQUIRED |

The coexistence of legacy Apple media and projection vocabulary is a reason to
search exact runtime/startup files. It is not evidence that hidden CarPlay can
be enabled by a flag. Persistency properties express product policy; they do
not supply missing USB device-mode drivers, authentication, receiver, video,
audio, or certification.

## Android Auto boundary

The 2014 QNX CAR 2.1 architecture guide states that its USB layer can handle
Android Accessory Protocol. That is not proof of an Android Auto head-unit
receiver. The explicit Android Auto receiver/library and AOA control material
found publicly belongs to newer QNX 7.x documentation. No QNX 6.6 Android Auto
receiver is claimed from these sources.

This asymmetry is intentional:

- legacy QNX 6.6 Apple CarPlay transport: CONFIRMED REFERENCE;
- legacy QNX 6.6 Android accessory transport: CONFIRMED REFERENCE;
- legacy QNX 6.6 Android Auto receiver: UNKNOWN;
- either receiver installed/callable on RA4: UNKNOWN.

## Static correlation plan

The recovered-tree probe now searches exact controlled markers:

- `usblauncher`
- `io-usb-dcd`
- `RoleSwap_DigitaliPodOut`
- `RoleSwap_AppleDevice`
- `iAP2`
- `mm-ipod`
- `io-fs-media`
- `itun`
- `libipod`
- `devu-dcd`
- `ulink_ctrl`

Pass the redacted probe JSON to `qnx_runtime_correlation.py`. Highest-value
positive files are startup scripts, usblauncher rules/descriptors, binaries or
libraries where legacy Apple transport co-occurs with projection-service,
Screen or audio markers. A hit remains a candidate until file provenance,
imports/XREFs, process startup, controller/BSP applicability, permission and
licensed caller contract are established.

A complete exact-tree negative would narrow RA4 18.45.01 to the HMI stubs plus
legacy media components, making a QNX-supplied add-on or port necessary. It
would not prove that no compatible licensed package exists externally.

See [OMAP3730 USB role feasibility](18_omap3730_usb_role_feasibility.md) for the
silicon, public-BSP, board-wiring and DCD distinction.

## Resource and safety effect

This reference and PC-only marker update install 0 bytes on the radio, write 0
radio bytes and require 0 radio staging. Any required `usblauncher`,
`io-usb-dcd`, descriptor/rule, private iOS driver, receiver, projection
manager or dependency must be included in the 15 MB installed cap unless
already present, compatible and legitimately reusable. Runtime PPS/state, logs,
crash data, and update copies count against the 4 MB/8 MB writable limits.
