# Android Auto DHU wired USB bench: environment established, phone authorization blocked

Date: 2026-09-06 (America/New_York; timestamps below include an offset).

**Result: INCOMPLETE. No Android Auto projection session has been demonstrated.**
Official ADB runs, but `adb devices` returns an empty list and Windows exposes
the Samsung phone's MTP/modem interfaces without an ADB interface. The required
ADB control case has not passed. Direct USB/AOA was deliberately not attempted,
because the experiment requires a successful control case first. This is useful
environment and baseline evidence, not a known-good Android Auto USB reference.

## Isolation and scope

- Repository: `jfhutchi/jeep_uconnect_custom`.
- Experiment branch: `codex/android-auto-dhu-bench`.
- Separate worktree: `E:\Documents\GitHub\jeep_uconnect_android_auto_dhu_bench`.
- Base: freshly fetched `origin/codex/ra4-driver-temperature` at
  `9eb28ad2c9d06753c1b0ec59a251c804b70b4b52`.
- Astra's checkout remains at `E:\Documents\GitHub\jeep_uconnect_custom`.
  Its files and branch were not changed by this experiment. Shared Git metadata
  necessarily gained the new worktree/branch and a fetched remote reference.
- The automatically inherited upstream was removed to prevent an accidental
  default push to the research branch. Publish only the explicit experiment
  branch. No merge or main-branch change is part of this work.

No radio operation, firmware operation, APK installation, phone filesystem
write, security bypass, custom USB request, fuzzing, or packet injection was
performed. No vendor package or private phone content belongs in this branch.

## Environment

| Item | Locally observed value |
| --- | --- |
| Windows | Windows 11 Home, 64-bit |
| OS version/build | `10.0.26200` / `26200` |
| Initially on PATH | No `adb`, `sdkmanager`, or `java` found |
| Existing SDK / Android Studio / DHU | Not found in the searched locations; not a whole-disk absence claim |
| Added Platform-Tools | Official Windows `37.0.1` archive |
| Running ADB | `1.0.41`, package build `37.0.1-15733141` |
| Added DHU | Official stable package `extras;google;auto`, revision `2.0` |
| Running DHU help/version | `2.0-windows`, build `2022-03-30-438482292` |
| DHU dependency | Bundled `libusb-1.0.dll` retained beside the executable |
| SDK Manager / Android Studio | Neither installed for this bench; official archives extracted directly |

Searches checked PATH, `ANDROID*` and `JAVA_HOME` environment variables,
standard Android SDK/Studio directories, and `rg --files --hidden` for `adb.exe`,
`desktop-head-unit.exe`, `sdkmanager.bat`, `studio64.exe`, and `java.exe` below
the user's Local AppData, both Program Files directories, and
`E:\Documents\GitHub`. Inaccessible paths were not exhaustively inspected.

Tools are outside every Git worktree:

```text
C:\Users\JHutc\AppData\Local\Android\DhuBench\platform-tools\adb.exe
C:\Users\JHutc\AppData\Local\Android\DhuBench\extras\google\desktop-head-unit.exe
```

The DHU ZIP expands directly into the selected destination, so this manual
layout uses `extras\google` rather than SDK Manager's `extras\google\auto`.
All commands below use the actual paths. No PATH, SDK environment variable, or
Windows execution-policy change was made.

Google's HTTPS repository metadata selected and verified the packages:

| Package archive | Metadata SHA-1 (matched before extraction) | Locally calculated SHA-256 |
| --- | --- | --- |
| `platform-tools_r37.0.1-win.zip` | `e03e78b1d80b396f1c3358e31251cb31740e1110` | `45f4d63113e895ebde0c90f194099a4676b6ac653bd28d54314a9e022bbc1a99` |
| `desktop-head-unit-windows-x64_r02.0.zip` | `680418d5aca256cce151eb7f9527294e95b6bb8a` | `c15cfceb74c27d0283d136853c6a69f2173d74f2b2cdbd0cc7754353d39df982` |

Metadata: [Platform-Tools repository](https://dl.google.com/android/repository/repository2-3.xml)
and [Google add-on repository](https://dl.google.com/android/repository/addon2-1.xml).
The latter lists DHU 2.0 on stable channel 0 and 2.1 on preview channel 1.
The `addon2-3.xml` endpoint did not list DHU in this observation. No preview or
third-party emulator was installed. Checksums detect archive mismatch; SHA-1
matching is not represented as a separate signature verification.

## Phone

- Manufacturer: Samsung, supported by Windows VID `04E8` and installed drivers.
- Exact model: **UNKNOWN**; a user-editable Windows label is not model proof.
- Android version: **UNKNOWN**, pending authorized read-only ADB properties.
- Phone serial, user-assigned device name, and other personal identifiers are
  intentionally excluded from this report and the helper's output.

After one USB device is authorized, read only `ro.product.model` and
`ro.build.version.release` with `adb -d shell getprop <property>`. Do not dump
all properties, phone storage, contacts, notifications, or application data.

## Control test

### Executed

1. Downloaded the two named official archives using `Invoke-WebRequest` from
   `https://dl.google.com/android/repository/`, checked `Get-FileHash -Algorithm
   SHA1` against Google's metadata, then used `Expand-Archive` outside Git.
2. Ran the following commands with the full paths above:

   ```powershell
   & $adb version
   & $adb devices
   & $dhu --help
   ```

   Here and below `$adb` and `$dhu` denote those executable paths. ADB started
   its ordinary local server on TCP 5037. Initial and repeated device listings
   contained only `List of devices attached` and a blank body.
3. At `2026-09-06T15:05:49-04:00`, `15:07:19-04:00`, and approximately
   `15:09:00-04:00`, the ADB list was still empty. This is neither an
   `unauthorized` device entry nor an authorized `device` entry.
4. Requested that the owner unlock the phone, enable standard USB debugging
   if off, accept this PC's prompt without selecting permanent authorization,
   and report the original setting. No phone-side response or change has yet
   been confirmed in the evidence recorded here.

### Result

**BLOCKED before the ADB authorization prerequisite.** No ADB tunnel was
created; no head-unit-server operation was performed; no DHU projection window
was launched. DHU help executing successfully proves tool startup only.
There is no rendering, Android Auto startup, disconnect, or reconnect result.

### Unexecuted continuation after authorization

Google's [DHU setup guide](https://developer.android.com/training/cars/testing/dhu)
documents the ADB tunnel and direct accessory alternatives. Its
[Android Auto developer-mode instructions](https://developer.android.com/training/cars/testing#developer-mode)
describe the on-phone development menu.

1. Require exactly one intended USB phone in state `device`. Record model,
   Android version, and a new redacted Windows snapshot.
2. On the phone, record the original Android Auto developer-mode state. Enable
   that mode if needed, start its head unit server, and confirm that adding new
   cars is enabled. Record any setting changed and any first-use prompt.
3. Check for an existing TCP 5277 forward/listener before creating this bench's
   forward. Use `adb -d forward --no-rebind tcp:5277 tcp:5277` to avoid replacing
   someone else's forward. Run DHU in ADB mode from its executable directory.
4. Have the owner handle any Android Auto consent prompt and verify the actual
   projection window. Do not save private maps, messages, or screenshots into
   Git. Record only rendering/session outcomes and non-sensitive timing.
5. Exit DHU normally; restart the same control connection and verify it again.
   Remove only the bench-created forward with `adb -d forward --remove tcp:5277`.

These steps are a continuation procedure, not evidence that they ran.

## USB/AOA test

**NOT RUN.** The mandatory control-success gate has not been met.

Local `desktop-head-unit.exe --help` confirms:

```text
-a, --adb=HOSTPORT         use ADB transport (optional host port)
-u, --usb=DEVICE_ID        use USB transport (optional device serial)
```

After the control passes, stop DHU and the phone's development head unit server,
remove the bench ADB forward, take a fresh snapshot, and run the documented
`desktop-head-unit.exe --usb` with only the intended Android phone attached.
If multiple compatible phones are present, target the intended device privately
using the installed version's serial selector; never publish that value.
Do not use the separate wireless bridge mode for this wired experiment.

Observe any USB re-enumeration, accessory interfaces, actual session startup,
and projection rendering independently. Then close DHU, unplug/replug the
phone, verify the normal USB identity and ADB authorization, and repeat the
direct connection once. These operations remain unexecuted.

The DHU guide warns that Windows may need a WinUSB binding and that ADB can
interfere. That is conditional, not evidence that this Samsung needs a driver
replacement. No WinUSB binding is justified yet. Any later change must follow
the driver/rollback gates below.

## USB observations

The following values are directly observed Windows PnP properties, not a raw
USB descriptor or packet capture. All three nodes reported status `OK`.

| Node | VID:PID | Interface / compatible class tokens | Service | Bound provider / version / INF |
| --- | --- | --- | --- | --- |
| Samsung composite parent | `04E8:6860`, revision `0504` | Device class `00`, subclass `00`, protocol `00` | `dg_ssudbus` | Samsung / `2.21.4.0` / `oem165.inf` |
| MTP child | `04E8:6860` | `MI_00`; `06/01/01`; `MS_COMP_MTP` | `WUDFWpdMtp` | Microsoft / `10.0.26100.9278` / `wpdmtp.inf` |
| Modem child | `04E8:6860` | `MI_01`; `02/02/01` | `Modem` | Samsung / `2.21.4.0` / `oem2.inf` |

No ADB interface was exposed in these present-only snapshots. The snapshots at
`2026-09-06T19:08:59.6830139Z` and `2026-09-06T19:12:45.0751350Z` still
contained these three nodes and no
Google-VID node. This timestamp is when the snapshot completed, not when USB
enumeration occurred. Polling cannot exclude an unobserved short transition.
Endpoint addresses, configurations, transfer traffic, negotiated USB speed,
VBUS voltage, and actual enumeration-event timestamps were not captured.

Observed sequence so far:

```text
Samsung 04E8:6860 (MTP + modem, no visible ADB)
  -> repeated same baseline observations
  -> no observed accessory negotiation or projection session
```

For a future successful experiment, Android's
[AOA specification](https://source.android.com/docs/core/interaction/accessories/aoa)
describes `18D1:2D00` for accessory and `18D1:2D01` for accessory plus ADB.
Those IDs are **expected reference values, not observed values here**. An
accessory VID/PID alone would prove neither Android Auto authentication nor
projection rendering. Those require separate session/UI evidence.

### Original observation helper

Run [android_auto_usb_snapshot.ps1](../analysis_tools/android_auto_usb_snapshot.ps1)
from this worktree:

```powershell
.\analysis_tools\android_auto_usb_snapshot.ps1
```

It uses `Get-PnpDevice -PresentOnly` and `Get-PnpDeviceProperty`, selects Samsung
and Google VIDs by default, and emits JSON to stdout. It does not change drivers,
issue USB requests, invoke ADB, or write files. It omits instance suffixes,
friendly names, container IDs, and location paths, retaining only selected
driver metadata and allowlisted VID/PID/interface/class tokens. A VID filter
can include another manufacturer. Multiple devices with the same VID/PID are
deliberately not uniquely identifiable in the redacted result.

## Android Auto observations

| Required behavior | Result |
| --- | --- |
| Authorized ADB connection | Not established; device list empty |
| Android Auto starts | UNKNOWN / not tested |
| DHU displays phone projection | UNKNOWN / not tested |
| Basic UI renders | UNKNOWN / not tested |
| Clean session disconnect | UNKNOWN / not tested |
| Session reconnect | UNKNOWN / not tested |
| Direct accessory transition | UNKNOWN / not attempted |
| Unplug restores ordinary phone USB | UNKNOWN / no unplug cycle observed |
| Normal phone usability after session | UNKNOWN / no session occurred |

No phone logcat, screen recording, network capture, or USB packet dump was
collected. There is no projection console log to preserve because no session
was launched. Tool version/help and redacted PnP/ADB results are recorded above.

## Evidence classification

| Label | Finding and limit |
| --- | --- |
| PROVED | This PC runs official ADB 37.0.1 and DHU 2.0 help; package checksums matched the retrieved Google metadata. This does not prove working projection. |
| PROVED | Windows recognizes a present Samsung `04E8:6860` composite device with MTP/modem children and the listed driver bindings. PnP `OK` is not a full phone-health test. |
| PROVED | Repeated local `adb devices` observations are empty; the required authorized control connection has not been established. |
| HIGH | A phone-side debugging/exposure prerequisite is the leading blocker: a present Samsung composite device has no visible ADB child and official ADB sees nothing. This does not exclude a device-specific driver issue. |
| INFERRED | Disabled USB debugging is a plausible explanation, pending owner confirmation. Do not claim it is the confirmed original setting. |
| INFERRED | A later successful DHU AOA session would be a useful host-side Android USB reference for RA4 research, with different role requirements from the documented CarPlay swap. |
| UNKNOWN | Exact phone model, Android/Android Auto version, ADB authorization, Android Auto control result, direct AOA result, endpoints, timing, and reconnect/rollback behavior. |

## RA4 relevance

This section compares the **documented reference architecture and observed
pre-session baseline**, not a successful PC session. Research was read only
from the experiment's fixed base commit. No new RA4 binary analysis occurred.

Reviewed the current
[research handoff](../RA4_RESEARCH_HANDOFF_CURRENT_FINDINGS.md),
[projection foreground report](projection_foreground_ownership.md),
[projection engine feasibility](../docs/11_projection_engine_feasibility.md),
[OMAP3730 role analysis](../docs/18_omap3730_usb_role_feasibility.md),
[media-hub path](../docs/19_ra4_media_hub_usb_path.md), and related completion
matrix/reference entries.

- **Host/accessory roles:** AOA uses an external USB host and an Android device
  in accessory mode. The PC does not need to become a USB peripheral for that
  path. Therefore Android accessory re-enumeration must not be confused with
  the Apple host/device role swap discussed in the RA4 CarPlay reports.
- **RA4 host evidence:** The reports establish static `io-usb` and
  `libusbdi`/`usbd` host-side evidence. That is directionally relevant to AOA,
  but it does not establish an installed AOA negotiator, Android Auto receiver,
  supported authentication/session implementation, or working projection.
- **Device stack:** `io-usb-dcd`, `devu-dcd`, `libusbdci`, `Device_Stack`, and
  `start_stack::device` are device-role investigation markers. Generic QNX
  documentation is not proof these are installed/configured on RA4. Missing
  RA4 device-role proof cannot by itself rule out the host-side AOA topology.
- **usblauncher:** Existing reports distinguish generic QNX projection-aware
  launch/role rules from evidence on the actual RA4 build. DHU success would
  not establish a corresponding RA4 `usblauncher` configuration or module.
- **OMAP3730, OTG, VBUS, USB ID:** Silicon dual-role capability and public BSP
  host support do not settle RA4 board routing. VBUS control, the media hub's
  exact behavior, and the internal controller route remain unresolved. AOA's
  host path avoids requiring the same host-to-device reversal as the cited
  CarPlay architecture, but ordinary USB data/power integrity still matters.
- **Session versus foreground:** The static foreground report identifies
  `IPhoneProjection.sessionActive`, `PhoneProjection.startProjection`,
  `PhoneProjectionEvent`, and navigation to `DEVICE_PROJECTION`. It separates
  an active session from the currently visible branch. A later DHU experiment
  can observe those concepts independently, but cannot prove the RA4 backend.
- **DeviceProjection.swf:** The existing completion matrix proves references,
  while the physical screen artifact, supported loader, and backend binding
  remain unresolved. No claim of installed functional Android Auto follows
  from those names or from installing DHU on a PC.

The main new conceptual boundary is that a future Android AOA host bench can
test a different USB transport premise from CarPlay's documented role swap.
It resolves none of the RA4 runtime, licensing, resource-budget, video/audio,
vehicle-integration, or authorized-installation gates by itself.

## Rollback

### Changes actually made

- Extracted official tools/archives below the local `Android\DhuBench`
  directory. They remain outside Git and can be removed later when not in use.
- Started the ordinary local ADB server; no device connection or TCP 5277
  forwarding was established in the recorded observations. After the final
  empty device list, `adb kill-server` stopped the bench server at approximately
  `2026-09-06T15:12:45-04:00`; no ADB or DHU process remained in the process query.
- No Windows driver package/binding, USB device enablement, global PATH,
  execution policy, or persistent phone configuration was changed by the agent.
- Requested owner-operated USB debugging setup. Whether the owner performed
  it and its original state remain unconfirmed; restoration cannot be claimed.

No session was entered, so there is no observed post-session return to normal.
The last recorded Windows snapshot still shows the ordinary three-node
baseline. This supports unchanged enumeration, not a complete usability test.

### Required before any later driver change

1. Refresh the exact target identity and current provider/version/INF. Keep any
   unredacted instance selector local and out of Git.
2. Demonstrate the failure with the existing binding and consult Google's
   conditional Windows requirement. Do not replace the Samsung composite
   parent or remove unrelated interfaces merely because WinUSB is mentioned.
3. Preserve the original relevant driver package using Windows' supported
   driver export facility outside Git, and establish the exact-interface
   Device Manager rollback/rebind procedure before changing anything.
4. Change only a confirmed relevant interface if necessary. Afterward stop
   DHU, unplug/replug, restore that interface's original binding, and verify
   normal ADB and MTP enumeration. Do not remove shared packages broadly.

After future phone setup/testing, stop the Android Auto head unit server,
restore only settings that were changed, and turn USB debugging off if it was
initially off. Do not revoke all computers' debugging authorizations or clear
Android Auto data as a blanket cleanup. Do not delete existing host ADB keys.

## Next experiment

**Highest-value single safe next test:** complete one ADB-tunneled DHU control
cycle with the owner present: authorize USB debugging, start Android Auto's
standard development head unit server, visibly render projection, close DHU,
and reconnect once. Record model/Android version and original setting states.
Only after that succeeds should direct DHU USB/AOA negotiation be attempted.

## Verification of deliverables

The PowerShell parser accepted the original helper without errors. A live
invocation returned the baseline above; a schema check verified the VID/PID
identity shape, snapshot-time qualification, and absence of instance/friendly
name/container/location fields. This verifies the helper's observed output,
not an Android Auto connection. `git diff --check` was clean. No production
RA4 code was changed, so unrelated parser/prototype suites were not rerun.

## Follow-up: retry after owner unlocked the phone

The owner reported that the phone had been locked and requested another attempt.
At `2026-09-06T15:16:18-04:00`, ADB was restarted and `adb devices` again
returned an empty list. The redacted PnP snapshot at
`2026-09-06T19:16:22.1976722Z` showed the same Samsung `04E8:6860` composite,
MTP, and modem nodes, all `OK`, with unchanged driver versions and INFs.
No ADB interface appeared. Unlocking alone did not establish the control
connection in this observation.

The owner was asked to check standard USB debugging and accept the PC's prompt
without permanent authorization. USB debugging's original state and any
subsequent change remain unconfirmed. No driver binding or phone setting was
changed by the agent, and no DHU session or direct AOA attempt was made.
The `15:17:28-04:00` ADB retry was also empty. For this follow-up the local
ADB server is left running so it can present an authorization prompt when the
owner enables debugging; no phone transport or TCP 5277 forward exists.
