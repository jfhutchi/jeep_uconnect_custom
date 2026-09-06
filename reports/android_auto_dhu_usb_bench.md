# Android Auto DHU USB bench: control passed, AOA transition proved

Date: 2026-09-06. Times are EDT (UTC-04:00) unless marked UTC.

**Result:** This Windows PC and phone successfully ran Android Auto projection
through Google's DHU over an ADB tunnel, including UI interaction and a second
session. Direct USB discovery failed with the unchanged Google DHU 2.0 and 2.1
packages. An isolated PC-only libusb update allowed the unchanged DHU 2.0
executable to negotiate real AOA mode: `04E8:6860 -> 18D1:2D01`, independently
confirmed by Windows and Android's `accessory,adb` state. Direct projection
then failed at transport access while the accessory interface was bound to MTP.

**There is no successful direct USB Android Auto projection reference yet.**
AOA negotiation and active Android Auto projection are separate evidence gates.
No manual Windows driver rebind, phone firmware change, APK modification,
security bypass, or custom USB request was performed.

## Isolation

- Repository: `jfhutchi/jeep_uconnect_custom`.
- Experiment branch: `codex/android-auto-dhu-bench`.
- Worktree: `E:\Documents\GitHub\jeep_uconnect_android_auto_dhu_bench`.
- Base: freshly fetched `origin/codex/ra4-driver-temperature` at
  `9eb28ad2c9d06753c1b0ec59a251c804b70b4b52`.
- Astra's checkout at `E:\Documents\GitHub\jeep_uconnect_custom` was not
  switched or edited. No main/research-branch commit, push, or merge occurred.
- Draft PR: [#15](https://github.com/jfhutchi/jeep_uconnect_custom/pull/15),
  targeting `codex/ra4-driver-temperature`, not main.

All executable packages, DLLs, downloaded archives, and temporary screenshots
were kept outside Git. Only this original report and the original redacted
PnP helper are experiment deliverables.

## Environment

| Component | Observed value |
| --- | --- |
| Windows | Windows 11 Home, 64-bit, version `10.0.26200`, build `26200` |
| Initial tools | ADB, SDK Manager, Java, Android Studio, and DHU not found on PATH/in searched installation locations; not a whole-disk absence claim |
| Added ADB | Official Platform-Tools `37.0.1`; ADB `1.0.41`, build `37.0.1-15733141` |
| Official stable DHU | `2.0-windows`, build `2022-03-30-438482292` |
| DHU 2.0 bundled libusb | Runtime diagnostic: `1.0.23.11394-rc3` |
| Official preview DHU | `2.1-windows`, build `2022-12-15-495540972`; separately extracted for the discovery comparison |
| Compatibility experiment | Unchanged Google DHU 2.0 executable plus upstream libusb `1.0.30`, Windows VS2019/MS64 DLL, in a separate directory |
| Android Studio / SDK Manager | Not installed for this experiment; official archives extracted directly |

Tool root: `C:\Users\JHutc\AppData\Local\Android\DhuBench`.

```text
platform-tools\adb.exe
extras\google\desktop-head-unit.exe          # original Google DHU 2.0
extras\google\libusb-1.0.dll                  # original bundled library
dhu-2.1-preview\desktop-head-unit.exe         # separate Google preview
dhu-2.0-libusb-1.0.30\desktop-head-unit.exe    # unchanged DHU executable
dhu-2.0-libusb-1.0.30\libusb-1.0.dll          # upstream compatibility DLL
```

The stable ZIP was extracted into `extras\google`, so that actual path differs
from SDK Manager's conventional `extras\google\auto`. No global PATH,
execution-policy, USB filter, or SDK environment change was made. The diagnostic
`LIBUSB_DEBUG=4` setting existed only in one child PowerShell process.

The SDK package source for both DHU versions was
[Google's main repository metadata](https://dl.google.com/android/repository/repository2-3.xml).
It lists 2.0 on channel 0 and 2.1 on channel 1. Google USB Driver r13 came from
[Google add-on metadata](https://dl.google.com/android/repository/addon2-3.xml)
and was extracted for INF inspection only, not installed. Earlier discovery
notes had incorrectly attributed the DHU entries to the add-on feed; the
independent main-feed read corrected that attribution.

| Archive | Check matched before extraction |
| --- | --- |
| `platform-tools_r37.0.1-win.zip` | Google metadata SHA-1 `e03e78b1d80b396f1c3358e31251cb31740e1110` |
| `desktop-head-unit-windows-x64_r02.0.zip` | Google metadata SHA-1 `680418d5aca256cce151eb7f9527294e95b6bb8a` |
| `desktop-head-unit-windows-x64_r02.1.zip` | Google metadata SHA-1 `c27bf84e59dda7b79315b6ca2a314063feffd6ac` |
| `usb_driver_r13-windows.zip` | Google metadata SHA-1 `08a48c39084e9443f6146c239cbd3be6f91e681b` |
| `libusb-1.0.30.7z` | Upstream GitHub release asset SHA-256 `7fb1dfec805b97983763d7d0ae244320da12add1003d4249c96cc4d586398c79` |

Additional locally computed SHA-256 provenance:

| File | SHA-256 |
| --- | --- |
| Platform-Tools archive | `45f4d63113e895ebde0c90f194099a4676b6ac653bd28d54314a9e022bbc1a99` |
| DHU 2.0 archive | `c15cfceb74c27d0283d136853c6a69f2173d74f2b2cdbd0cc7754353d39df982` |
| DHU 2.1 archive | `46f84b65b0862d5b548e46b976615a5db1853535732a728c875792ec166ae721` |
| Original and compatibility-copy DHU 2.0 executable, identical | `8a086d349b204fd7975cfa01133cfdd45dd601f9f14256e8992e27f4cacfc871` |
| DHU 2.0 original libusb DLL | `50a17e3581b91281640869c358d0fe72a981d02dbfe2706cfcef31734c27f84f` |
| DHU 2.1 bundled libusb DLL | `1e926b45dda54e28d69363c48408e16421b97ee7f943e39cbb5477f608d41b14` |
| Upstream 1.0.30 VS2019/MS64 libusb DLL | `e0cb1d0e8c20ae55c4e2f944d3136a2766ede61a16551cc7562eaedae4bc13bc` |

The dependency substitution is an experimental PC compatibility change. It is
not represented as an unchanged Google distribution or a Google-certified
combination. Google DHU still performed the protocol; no replacement Android
Auto receiver, credential change, or custom accessory implementation was used.

## Phone

- Manufacturer: Samsung.
- Model: `SM-S931U`, read using `adb -d shell getprop ro.product.model`.
- Android: `16`, read using `adb -d shell getprop ro.build.version.release`.
- Installed Android Auto: `17.5.663214-release`, from a filtered package-version
  field; no APK was extracted, installed, updated, or modified.
- USB debugging was initially **off**, explicitly confirmed by the owner.
  The owner enabled it and authorized the PC. Whether permanent authorization
  was selected is not known; the owner was advised to leave it unchecked.
- The owner enabled/revealed Android Auto's development menu and started its
  head unit server for the control, then confirmed stopping the server.
  Android Auto developer mode's original state was not separately confirmed.

Serials, user-assigned device names, precise locations, personal UI content,
and identifiers of unrelated USB devices are omitted from Git.

## Control test

### Initial prerequisite and commands

`adb devices` initially returned an empty list, including after the owner
unlocked the phone. After USB debugging was enabled, at `15:20:08`, exactly one
phone appeared in authorized `device` state. Windows added the ADB interface
without changing VID/PID. Android reported `sys.usb.state=mtp,adb`.

The owner used the standard Android Auto developer menu to start the head unit
server. The documented procedure is in Google's
[DHU guide](https://developer.android.com/training/cars/testing/dhu) and
[Android Auto development-menu instructions](https://developer.android.com/training/cars/testing#developer-mode).

After checking for existing forwards/listeners, the actual control used:

```powershell
& $adb -d forward --no-rebind tcp:5277 tcp:5277
& $dhu --adb=5277
```

Here `$adb` and `$dhu` refer to the full local executable paths documented above.
`--no-rebind` prevented replacing an existing forward. A pre-server DHU attempt
reported a local connection but did not establish projection; it was closed and
its forward removed. That initial `connected` message was not counted as success.

### Successful sessions

After the owner started the server and handled first-use prompts, DHU reported
phone protocol `1.7`, a successful TLS 1.2 handshake, and verification `ok`.
The receiver requested protocol `1.7`. No certificates or key material were
extracted, modified, or published.

A DHU `screenshot` first showed the on-phone setup prompt and then, around
15:25, the rendered Android Auto dashboard. Screenshots were inspected locally
outside Git. The first successful session closed using `quit`, exit code 0.
ADB remained authorized and USB state remained `mtp,adb`.

The next launch failed to connect. A follow-up check found no ADB forward;
its disappearance was observed, but its cause was not determined. Recreating
TCP 5277 forwarding enabled a second successful session at `15:27:13` with
another successful protocol/TLS handshake. `tap 44 440` followed by a separate
screenshot showed the app launcher, proving a basic UI response. This session
also exited normally with code 0. The tunnel was explicitly removed before the
USB test, and the owner confirmed stopping the phone's head unit server.

**Control result: PASSED for launch, visible projection, basic rendering/input,
normal application exit, and a second session after tunnel recreation.**
Seamless reconnect without checking/recreating the tunnel was not proved.
Audio stream close/already-playing warnings appeared; audio quality was not
independently validated. Startup time was not measured with a synchronized
clock, so no precise latency is claimed.

## USB/AOA test

The installed versions' own help confirmed `--usb=DEVICE_ID` with an optional
phone serial selector. The tests used the ordinary DHU USB mode, not its
wireless bridge mode. ADB was stopped before every direct attempt.

| Attempt | Preparation and result |
| --- | --- |
| 15:29, Google DHU 2.0 | With the head unit server stopped and ADB tunnel/server removed, `--usb` exhausted discovery. Its broad search also inspected unrelated devices; no configuration was changed. |
| 15:30, Google DHU 2.0 | Selected exactly one authorized phone's serial in memory, stopped ADB, then used `--usb=<private serial>`. Same discovery/access failure. |
| 16:14 resume | Owner reconnected in Transferring files / Android Auto mode. ADB was authorized; normal Samsung baseline was restored. |
| 16:16, diagnostic 2.0 | Same targeted attempt with process-local `LIBUSB_DEBUG=4`; saw the Samsung driver and unrecognized-driver open failures. No accessory transition. |
| 16:18, Google DHU 2.1 preview | Local help checked; targeted USB discovery also failed. Original 2.0 installation preserved. |
| 16:21:46, compatibility copy | Unchanged DHU 2.0 executable with upstream libusb 1.0.30 detected AOA v2, initiated accessory mode, found `18D1:2D01`, and discovered interface 0 with endpoints `0x81` IN and `0x01` OUT. It attached, then reported transport read/write disconnect errors. No direct projection UI appeared. |

Failure strings included `Couldn't find/access compatible USB device`,
`Failed to start Google Automotive Link`, and, after the successful accessory
transition, `Failed to read from transport - disconnect`. A command wrapper
returned exit code 0 even on failure; log and UI evidence take precedence.

The Windows snapshot at `20:22:30.8018717Z` independently confirmed
`18D1:2D01`. ADB reconnected in authorized state and Android reported
`accessory,adb`. This demonstrates real accessory re-enumeration, not an ADB
simulation. No direct-mode phone protocol/TLS success or projected UI was seen.

### Why the dependency test was justified

The bundled 2.0 library identified itself as `libusb v1.0.23.11394-rc3` and
logged `dg_ssudbus` plus unsupported/unrecognized-driver open errors. The
[upstream v1.0.23 Windows source](https://github.com/libusb/libusb/blob/v1.0.23/libusb/os/windows_winusb.c)
recognizes `USBCCGP` as the composite driver, whereas the
[v1.0.30 source](https://github.com/libusb/libusb/blob/v1.0.30/libusb/os/windows_winusb.c)
also names Samsung's `dg_ssudbus`. The
[official upstream release](https://github.com/libusb/libusb/releases/tag/v1.0.30)
provided the replacement DLL. After that one dependency changed, DHU reached
AOA negotiation. This is strong local evidence for the first compatibility
blocker; it does not establish that the later transport problem has the same cause.

## USB observations

All rows below are Windows PnP property observations. Hardware/compatible-ID
class tokens are not a complete descriptor dump. Snapshot timestamps do not
identify exact USB arrival/removal event times.

| State/node | VID:PID | Interface/class evidence | Service | Provider / version / INF |
| --- | --- | --- | --- | --- |
| Normal composite parent | `04E8:6860` | Device `00/00/00`, revision `0504` | `dg_ssudbus` | Samsung / `2.21.4.0` / `oem165.inf` |
| Normal MTP | `04E8:6860` | `MI_00`, `06/01/01`, `MS_COMP_MTP` | `WUDFWpdMtp` | Microsoft / `10.0.26100.9278` / `wpdmtp.inf` |
| Normal modem | `04E8:6860` | `MI_01`, `02/02/01` | `Modem` | Samsung / `2.21.4.0` / `oem2.inf` |
| Normal ADB, after owner enabled debugging | `04E8:6860` | `MI_03`, `FF/42/01` | `WinUSB` | Samsung / `2.19.1.0` / `oem86.inf` |
| Accessory composite parent | `18D1:2D01` | Device `00/00/00`, revision `0504` | `dg_ssudbus` | Samsung / `2.21.4.0` / `oem165.inf` |
| Accessory data interface | `18D1:2D01` | `MI_00`, `FF/FF/00`; Windows still includes `MS_COMP_MTP` | `WUDFWpdMtp` | Microsoft / `10.0.26100.9278` / `wpdmtp.inf` |
| Accessory ADB | `18D1:2D01` | `MI_01`, `FF/42/01` | `WinUSB` | Samsung / `2.19.1.0` / `oem86.inf` |

Observed sequence:

```text
04E8:6860, MTP + modem, ADB absent
  -> owner enables USB debugging
04E8:6860, MTP + modem + authorized ADB (mtp,adb)
  -> two successful ADB-tunneled Android Auto sessions
  -> stop development server / remove tunnel / stop ADB
  -> stock DHU libraries cannot access the Samsung path
  -> isolated upstream libusb update + unchanged DHU USB mode
AOA v2 reported by DHU
  -> 18D1:2D01, accessory interface 0 + ADB interface 1
  -> Android state accessory,adb
  -> transport read/write failure; direct projection NOT active
  -> owner unplugs/reconnects and selects file-transfer mode
04E8:6860, mtp,adb, authorized ADB and original driver bindings restored
```

Google's [AOA specification](https://source.android.com/docs/core/interaction/accessories/aoa)
identifies `18D1:2D01` as accessory plus ADB and `18D1:2D00` as accessory
without ADB. The latter was not observed. Endpoint `0x81`/`0x01` values came
from DHU's local discovery log, not an independent packet capture. USB speed,
configuration descriptors in full, VBUS voltage, and the control-transfer
sequence were not independently captured. No injection, replay, or fuzzing ran.

## Android Auto observations

| Required behavior | Result |
| --- | --- |
| Authorized ADB | PROVED after owner enabled debugging; also worked in accessory state |
| Android Auto starts and renders in DHU | PROVED for ADB transport |
| Basic UI input | PROVED by dashboard-to-launcher change |
| Normal DHU exit | PROVED, two successful control sessions exited with code 0 |
| Control reconnect | PROVED after ADB tunnel recreation; disappearance cause UNKNOWN |
| AOA negotiation and re-enumeration | PROVED with the isolated libusb compatibility copy |
| Direct Android Auto session/projection | Not achieved; transport errors after accessory attachment |
| Direct disconnect/reconnect | Not validated for a successful projection session |
| Normal USB/ADB restoration | PROVED after owner-assisted reconnect: `04E8:6860`, `mtp,adb`, authorized ADB, original bindings; full phone-health testing not performed |

No phone logcat, APK, private app data, certificate/key, packet dump, or personal
screen content is committed. Four temporary control screenshots were deleted
at the pause. Console excerpts here are restricted to non-sensitive protocol
and error information.

## Evidence classification

| Label | Finding and limit |
| --- | --- |
| PROVED | ADB-tunneled Android Auto projected on this PC from this phone; input and a second rendered session worked. |
| PROVED | Normal debugging enablement added ADB without changing `04E8:6860`. |
| PROVED | DHU with updated PC libusb caused `04E8:6860 -> 18D1:2D01`; Windows, DHU and Android state independently corroborated accessory mode. |
| PROVED | Accessory `MI_00` was bound to MTP while ADB used separate `MI_01`; direct transport failed. |
| HIGH | The bundled library's lack of Samsung composite-driver recognition explains the first discovery blocker; the isolated update passed that gate. |
| HIGH | MTP binding on the accessory data interface is the leading next transport-access blocker. No successful WinUSB rebind was performed to prove causality. |
| INFERRED | A correctly matched, supported WinUSB binding for accessory `MI_00`, including its device-interface registration, may enable direct projection. |
| UNKNOWN | Direct Android Auto session success, direct reconnect, exact failure code below DHU's generic transport error, full packet sequence, and RA4 runtime equivalence. |

## RA4 relevance

Read the fixed-base
[current handoff](../RA4_RESEARCH_HANDOFF_CURRENT_FINDINGS.md),
[foreground ownership report](projection_foreground_ownership.md),
[projection engine feasibility](../docs/11_projection_engine_feasibility.md),
[OMAP3730 USB-role analysis](../docs/18_omap3730_usb_role_feasibility.md),
[media-hub path](../docs/19_ra4_media_hub_usb_path.md), and
[completion matrix](../docs/08_projection_completion_matrix.md).
No new RA4 binary analysis or radio operation occurred.

- AOA kept the PC as USB host and changed the phone's accessory function/state.
  This is a different transport premise from the QNX CarPlay host/device role
  reversal discussed in the RA4 reports. Accessory mode is not proof of an
  OTG role swap, reversed VBUS, or phone becoming USB host.
- Recovered RA4 `io-usb` and `libusbdi`/`usbd` host-side evidence is relevant to
  an AOA host path, but does not establish an installed Android Auto receiver,
  accessory negotiator, supported authentication, or working media transport.
- `io-usb-dcd`, `devu-dcd`, `libusbdci`, `Device_Stack`, and
  `start_stack::device` remain markers for a separate device-role investigation.
  Missing device-role proof alone does not rule out host-side AOA.
- QNX `usblauncher` projection/role rules in public documentation must still be
  tied to the actual RA4 build. PC DHU success proves no equivalent RA4 module.
- OMAP3730 OTG silicon capability does not settle the board's port routing,
  hub behavior, USB ID or VBUS controls. AOA avoids the specific CarPlay role
  reversal requirement, but still needs a usable data/power path and receiver.
- `PhoneProjectionEvent`, `startProjection`, `sessionActive`, and foreground
  branch changes describe separate application/session/UI gates. This bench
  directly reinforces that separation: accessory enumeration succeeded without
  a direct projection session, while ADB projection worked on a different path.
- `DeviceProjection.swf` references do not establish its installed payload,
  loader, or backend. No RA4 installation, licensing, resource, audio/video,
  vehicle-integration, or rollback gate is closed by this PC experiment.

## Windows driver investigation and rollback

Google's DHU guide conditionally calls for WinUSB on Windows. Microsoft's
[WinUSB installation guide](https://learn.microsoft.com/en-us/windows-hardware/drivers/usbcon/winusb-installation)
describes manual selection and the required device-interface GUID registration.
The [libusb Windows guidance](https://github.com/libusb/libusb/wiki/Windows)
also distinguishes composite interfaces and driver/interface registration.

Before attempting any rebind, recorded the unique present accessory data node:
`18D1:2D01`, hardware-ID token `MI_00`, provider Microsoft, MTP service,
`wpdmtp.inf`, version `10.0.26100.9278`. Its existing Device Parameters had
neither `DeviceInterfaceGUID` nor `DeviceInterfaceGUIDs`. These Windows
registration values are distinct from Android certificates or cryptographic keys.

Existing inbox INF SHA-256 values:

- `wpdmtp.inf`: `e63d32e929e9aef7568b2a326971ce73715eb4ed915f26c1691bc81d01d303f8`.
- `winusb.inf`: `81465b5b0a773859c3e759f7adb8d238db624dbadfbf919ef0f8f63c94c4d221`.

The intended rollback for a successful interface-only change was selecting the
original inbox MTP driver for that same accessory node. No existing driver
package would be removed; the parent and ADB child would remain untouched.

Device Manager ran elevated and the computer-use helper could inspect but not
control its privileged UI. The owner navigated the MTP entry's manual picker.
Selecting `C:\Windows\INF\winusb.inf` produced a dialog that the specified
location did not contain driver software for the device. No successful rebind
was reported or observed. Google USB Driver r13 was then checksum-verified and
its INF inspected; it contains no matching `18D1:2D01` accessory-data entry.
It was not installed, edited, or forced onto an unrelated interface. The owner
was asked to cancel the wizard.

No registry GUID was added, no new driver package was installed, no driver
signature/security setting was changed, and no composite parent/ADB/modem
interface was manually replaced. The working original Google tool directories
were retained alongside the dependency experiment.

The owner was asked to unplug/replug into the same port, return to Transferring
files / Android Auto, and confirm ordinary usability. USB debugging should be
turned off after testing because it was originally off. The Android Auto head
unit server was already owner-confirmed stopped. Do not clear Android Auto
app data, revoke all computers' authorizations, or delete existing host ADB keys.

After the owner confirmed the mode was set, the snapshot at
`2026-09-06T20:35:43.9807123Z` showed the original four Samsung `04E8:6860`
nodes, all `OK`, with the original provider/version/INF bindings. ADB was
authorized, Android reported `mtp,adb`, and the forward list was empty.
This verifies ordinary USB/ADB recovery after the accessory transition; it is
not an exhaustive phone-health check. No manual driver rollback was needed.
The owner was advised to turn debugging off to restore its original setting;
that phone-side toggle has not yet been independently observed.
The bench ADB server was then stopped and a process check confirmed no ADB or
DHU process remained. No recurring monitor or background USB test was left running.

## Next experiment

The single highest-value next Windows bench test is a targeted direct DHU
session after obtaining and validating a supported, signed WinUSB installation
path specifically for `18D1:2D01` accessory interface `MI_00`, including its
Windows interface registration and a tested return to the existing MTP binding.
Then check direct protocol/session startup, actual rendering, clean exit,
unplug restoration, and a repeat connection. Do not broaden a driver change to
the composite parent or alter phone firmware to get around this remaining gate.

## Deliverable verification

[android_auto_usb_snapshot.ps1](../analysis_tools/android_auto_usb_snapshot.ps1)
is an original read-only helper using `Get-PnpDevice -PresentOnly` and
`Get-PnpDeviceProperty`. It emits JSON to stdout, selects Samsung/Google VIDs
by default, and excludes serial-bearing instance suffixes, friendly names,
container IDs and location paths. Only allowlisted identity/class tokens and
selected driver metadata are returned. Snapshot time is explicitly distinguished
from enumeration-event time. No USB requests, driver actions, ADB calls or file
writes occur in that helper.

PowerShell syntax and live snapshot schema checks passed. Report whitespace,
local links, and known private-identifier checks also passed before staging.
No production RA4 code changed; unrelated parser/prototype tests are not
evidence for this hardware experiment.
