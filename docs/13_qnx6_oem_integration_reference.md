# 13 - QNX 6.6 OEM integration reference boundary

Updated 2026-09-06. This report asks whether the stock RA4 may expose an
era-compatible, documented QNX application/window/notification boundary that
can host projection as an OEM-style application. It is a static, read-only
reference comparison. It authorizes no PPS write, process launch, radio
connection, package installation, firmware edit, or authentication workaround.

## Decision

**CONFIRMED REFERENCE:** QNX CAR Platform for Infotainment 2.1, in the official
QNX SDP 6.6 documentation set, defines a coherent OEM integration pattern:

- the HMI requests application lifecycle through PPS and Launcher;
- Launcher consults Authorization Manager (Authman) before starting an app;
- application/window management exchanges state under `/pps/system/navigator`
  and applications render through QNX Screen;
- HMI Notification Manager (HNM) arbitrates asynchronous multimodal events
  using configured priorities and PPS status/messaging objects;
- the reference window stack puts rear camera above all applications and
  supports transient presentation over ordinary content.

**UNKNOWN ON RA4:** None of those generic QNX CAR service names has yet been
proved installed, started, ABI-compatible, or callable by a new application in
the recovered RA4 18.45.01 product. The exact RA4 evidence instead identifies a
custom Harman Adobe AIR/SWF HMI and AppManager/AMS, ModuleLink, servicebroker,
PopupManager, DisplayManager and LayerManager behavior.

**NO DIRECT REUSE AUTHORIZED:** The public QNX command examples and PPS object
names are documentation for the reference platform, not permission or a wire
contract for this customized radio. They must not be written or recreated on
RA4 unless a matching installed component and supported caller contract are
independently proved.

## Official reference evidence

| Reference fact | Official evidence | Product meaning |
| --- | --- | --- |
| QNX CAR 2.1 belongs to the QNX SDP 6.6 documentation family | QNX 6.6 documentation index | correct era for comparison, not binary compatibility |
| App/window managers use PPS for app/window state and Screen for rendering | Application and Window Management, pp. 9 and 25 | a small independent projection surface is architecturally plausible |
| HMI -> PPS -> Launcher -> Authman -> application | Application and Window Management, pp. 15 and 23; Launcher service reference | lifecycle and permission belong to stock services, not an ad-hoc startup script |
| Launcher uses `/pps/services/launcher/control` | Launcher reference and application/window manager requirements | exact reference marker for census; not an RA4 command |
| HNM is a priority-based multimodal event arbiter | HNM guide and QNX HMI guide | could express temporary/call/message priority semantics if present, but does not replace RA4 proof |
| HNM uses control, `Status`, and `Messaging` PPS objects | HNM guide | exact reference markers for census |
| Reference camera is the top HMI layer | Application and Window Management, p. 21 | agrees with product priority, while RA4's own camera path remains authoritative |

Primary sources:

- https://www.qnx.com/developers/docs/6.6.0.update/
- https://support7.qnx.com/download/download/26216/Application_and_Window_Management.pdf
- https://www.qnx.com/developers/docs/6.6.0.update/com.qnx.doc.car.arch/topic/app_support.html
- https://www.qnx.com/developers/docs/6.6.0_anm11_wf10/com.qnx.doc.am.system_services/topic/applauncher.html
- https://www.qnx.com/download/download/26205/HMI_Notification_Manager.pdf

The QNX reference includes HTML5 and Qt5 HMI implementations. That does not make
either suitable for this project: adding a browser or Qt runtime would conflict
with the tiny-footprint rule unless the exact stock runtime, ABI, permissions
and incremental bytes were proved. RA4's evidenced AIR/SWF HMI remains the
preferred reuse boundary for the initial stock-facing surface.

## Reference-to-RA4 comparison

| Required behavior | QNX CAR 2.1 reference | Exact RA4 evidence | Current decision |
| --- | --- | --- | --- |
| authorized app start/stop | Launcher + Authman through PPS | Harman AppManager/AMS names and foreground paths | use no generic launcher until recovered startup/import evidence proves it |
| foreground/window ownership | Navigator/UI Core + Screen | `checkForegroundAvailability`, `onAppRequestForeground`, `IStructure.goto/back` | RA4 stock arbiter remains authoritative |
| temporary notification | HNM priority policy and transparent/overlay window concepts | PopupManager; HVAC popup at `0x0026DA68-0x0026DAB9` | preserve exact stock popup path; HNM is only a candidate mechanism |
| camera priority/return | rear camera is top reference HMI layer | DisplayManager `0x002BA764-0x002BA89F`; LayerManager `0x002D4D6F-0x002D4EF8` | reuse RA4 autonomous camera stack |
| call/message arbitration | HNM includes multimodal sources/plugins in the reference design | native call path `0x00257983`; SMS popup/TTS `0x002B6C35-0x002B6C96` / `0x002B85C2-0x002B8750` | keep volatile default-open presentation lease; no HNM hook assumed |
| projection session | no RA4-specific contract in these generic docs | `IPhoneProjection.sessionActive` at `0x002588DF`; start at `0x002B5177` | session remains independent of visible branch |
| service discovery | PPS service objects | ModuleLink + localhost servicebroker; projection schema unknown | recover Harman registration/version/owner-death contract first |

## Bounded recovered-tree census

`analysis_tools/qnx_media_runtime_probe.py` now scans, without execution or
content disclosure, for both sides of the comparison:

| Marker family | Controlled markers | What a positive result would justify |
| --- | --- | --- |
| QNX lifecycle | `/pps/services/launcher`, `/pps/services/app-launcher`, `/pps/system/navigator`, `authman`, `qtqnxcar2` | candidate file/config for startup, import, and ABI follow-up only |
| QNX notifications/audio | `hmi-notification`, `nowplaying`, `mm-control`, `mm-player`, `mm-renderer`, multimedia renderer PPS path | candidate generic QNX service or client reference only |
| QNX display | `screen_create_window_group` plus existing Screen/GLES markers | candidate window-group owner/client; not permission |
| Harman RA4 | `servicebroker`, `modulelink`, `phoneprojectionservice`, `iphoneprojection` | candidate stock-specific integration implementation/client |
| codec/graphics | existing Codec Engine, DSPLink/CMEM, H.264/OpenMAX/GStreamer, SGX/GLES markers | candidate decoder/render path |

Run the probe only against existing recovered off-radio roots. For every
positive file, record provenance, relative path, size and SHA-256, then:

1. classify executable architecture and imports without execution;
2. find startup/build/config references that establish whether it actually runs;
3. distinguish server implementation from client string reference;
4. locate registration, version, permission, owner-death and reconnect behavior;
5. map only proved fields into the adapter boundary;
6. measure incremental storage and runtime cost before target acceptance.

A complete negative for these controlled names applies only to the scanned
recovered roots. Stripped symbols, renamed OEM components, runtime-constructed
paths and encrypted/compressed subcontainers still require import/call-graph or
container follow-up. A positive string is never sufficient to write an object
or launch an application.

## Best next target

The best local technical target is the existing hash-identified recovered
18.45.01 filesystem census, followed by import/startup correlation of every
QNX-reference and Harman-specific hit. The highest-value outcome is either:

- a stock-started lifecycle/notification service with a recoverable supported
  client contract; or
- a bounded negative that retires the generic QNX CAR path and focuses all
  effort on the Harman AppManager/ModuleLink boundary.

In parallel, an authorized Harman/QNX contact should identify the accepted app
identity, service registration/version contract, Screen window-group ownership,
notification policy hook, owner-death fallback, target ABI, and component sizes.

## Resource effect

This report and probe are development-host artifacts. They install 0 bytes on
RA4, create 0 radio writable growth, and require 0 radio staging bytes. No
generic QNX CAR runtime receives zero-byte budget credit until its installed
presence, ABI, permitted reuse and attributable runtime growth are proved.
