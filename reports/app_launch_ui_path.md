# RA4 Installed-Application Catalog and Manual Launch Path

## Scope and safety

This report traces the stock RA4 18.45.01 human-facing path that lists and launches an ordinary installed, non-autostart Xlet. It is static analysis only. Recovered SWFs were parsed in memory; offsets are in reconstructed uncompressed FWS streams. No vendor executable was run, no on-unit command was sent, and no stock artifact was modified.

## Confirmed end-to-end path

```text
AppsMainScreen ITEM event
  -> AppsMainScreen.onItem(event)
  -> contents[event.data.id]
  -> selected entry is ordinary (embedded == false)
  -> selected appId differs from current running app
  -> not the Performance Pages special case
  -> IAppManager.startXlet(selected.appId, "MoreScreen")
  -> module AppManager.startXlet(appId, reason)
  -> sendAppMgrCommand("startApp", payload)
  -> AppManager command envelope with selected appId
  -> native appManager::parseRequest("startApp")
  -> findAndStartApp(appId, DRM-check = 1)
  -> App::start()
  -> AMS-facing start request
```

This closes the earlier gap between a successful non-autostart installation and its supported stock launch surface. Installation itself leaves an ordinary application stopped; selecting its normal Apps-menu entry issues the explicit native `startApp` request.

## Core artifacts

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/skins/default/swf/AppsMainScreen.swf` | 36,208 | `5df0c52056d9495c439e8c90d1826be132f43bc7d4a61951acd4f1adfccbd04d` |
| `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov/MainSupplement.swf` | 1,407,783 | `e9d796ea4b4c83ed518bfe3b3c341e54e510a1ae0f78ebbffbd655b7c36a3258` |
| `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_ru/skins/default/swf/AppsMainScreen.swf` | 28,231 | `2fc0812647cb2d0a74556a20cc23521a3a0279c3a09ff4db1baf093044775b8a` |
| `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_ru/MainSupplement.swf` | 1,324,848 | `a166e881a8114fe19413eb82613c815b56fa97418fb85dc2813e0358ad05855e` |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/bin/appManager` | 1,268,061 | `608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591` |
| `analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/base/kona/lib/kona.jar` | 3,062,680 | `19390472018f02d998690b982f00eb68da5d40d7a8d6fba91499677651015f92` |

## Apps-menu selection

In ROV `AppsMainScreen.swf`:

- `addListeners` is method-info `0x9EEE`, body `0xB771`, code `0xB778`. It registers `GlobalEvent.ITEM` at FWS `0xB79D`, resolves `onItem` at `0xB7A1`, and calls `addEventListener` at `0xB7A7`.
- `onItem` is method-info `0x9F17`, body `0xBDA0`, code `0xBDA7`, length 1,171 bytes. It resolves `contents[event.data.id]` at BCI 39-49 / FWS `0xBDCE..0xBDD8`.
- It reads the selected entry's `embedded` property at BCI 82 / `0xBDF9`; the ordinary non-embedded path begins at BCI 909 / `0xC134`.
- It compares `selected.appId` with `appManager.getRunningAppId()` at BCI 912-938 / `0xC137..0xC151`.
- If the current category is `RUNNING_APPS`, it saves the selected category at BCI 945-989 / `0xC158..0xC184`.
- Performance Pages is a fixed exception: equality with `getPPId()` selects `fullStartDaemonXlet(appId)` at BCI 1029-1051 / `0xC1AC..0xC1C2`.
- Every other ordinary entry loads `Peripheral.appManager` at BCI 1062-1065, the selected `appId` at BCI 1068-1081, literal reason `MoreScreen` at BCI 1084 / `0xC1E3`, and invokes `IAppManager.startXlet(String,String)` at BCI 1087 / `0xC1E6`.
- Selecting the already-running app does not resend start. That branch navigates to `APPS_ACTIVE` at BCI 1095-1163 / `0xC1EE..0xC232`.

RU is bytecode-semantic parity: `onItem` method-info `0x79E8`, code `0x9685`, with the equivalent BCI 1087 invocation at FWS `0x9AC4`.

## HMI command transport

ROV `com.harman.moduleLink::AppManager.startXlet` is method-info `0x1E7A0B`, body `0x2A9712`, code `0x2A971A`:

1. It checks `mAppOperStatus`; matching `appId` plus status `running` dispatches `START_RUNNING_APP` at `0x2A977E..0x2A978D` and returns without a native start command.
2. A super-app-system branch includes both `appId` and `startReason` at `0x2A97A9..0x2A97C7`.
3. The ordinary branch includes only `appId` at `0x2A97CD..0x2A97DB`; the Apps-screen `MoreScreen` reason is not transmitted on that branch.
4. It pushes operation `startApp` at BCI 199 / `0x2A97E1` and invokes `sendAppMgrCommand` at BCI 205 / `0x2A97E7`.

The class initializer sets `dbusIdentifier` to `AppManager` at `0x2A796E..0x2A7971`. `sendAppMgrCommand`, method-info `0x1E7A65`, body `0x2A9AA4`, code `0x2A9AAB`, constructs the command envelope from:

- `{"Type":"Command","Dest":"` at `0x2A9ACF`;
- `dbusIdentifier` at `0x2A9AD6`;
- `","packet":{"` at `0x2A9ADB`;
- the operation and payload through `0x2A9AE9`; and
- `client.send(...)` at BCI 75 / `0x2A9AF6`.

The ordinary logical request is therefore:

```json
{"Type":"Command","Dest":"AppManager","packet":{"startApp":{"appId":"<selected-id>"}}}
```

This is protocol evidence, not a recommendation to bypass the UI or invoke the service directly.

## Native dispatch and DRM enforcement

Native `parseRequest` spans VA `0x1516D4..0x156DFC` / file `0x516D4..0x56DFC`:

- token `startApp` is at file `0x108084`;
- the comparison is file `0x53DD0` and dispatch is `0x53DF0` to handler VA `0x14FDB0`;
- the handler supplies DRM-check byte one at file `0x50650` and calls `findAndStartApp`, VA `0x13B2DC`, at file `0x5066C`;
- no-service, DRM-failure, and app-not-found diagnostics are files `0x105474`, `0x1054BC`, and `0x105510`;
- the sole recovered `App::start` invocation is file `0x3C328` to VA `0x10EE68`; and
- `App::start` reaches the AMS request helper at file `0xF008`.

The ordinary HMI branch contains no local `verifyDRM` call because the native `startApp` handler supplies and enforces the DRM-check flag. This preserves the signed entitlement boundary during manual launch.

## Catalog population and visibility

ROV `AppsMainScreen.initScreen` is method-info `0x9EFA`, body `0xBAE4`, code `0xBAEB`; it restores/sets `activeCategory` and calls `getAppList` at `0xBBCE` or `0xBBE8`. `onCategory`, method-info `0x9F29`, code `0xC47F`, updates the category at `0xC4DE` and requests it at `0xC4F1`.

Module constants are `ALL_APPS=-2` (`0x2A7912..0x2A7914`), `FAVORITE_APPS=-1` (`0x2A7923..0x2A7925`), and `RUNNING_APPS=-3` (`0x2A7934..0x2A7936`). Module `getAppList`, method-info `0x1E79D1`, body `0x2A949F`, code `0x2A94A6`, constructs `category`/`sortby` at `0x2A94DB..0x2A94F3` and sends operation `getAppList` at `0x2A94F8..0x2A94FC`.

`appMgrMessageHandler`, method-info `0x1E792C`, code `0x2A7BEC`, recognizes `getAppList` at `0x2A7DA7`, reads `category/list` at `0x2A7DCE..0x2A7DFA`, builds `mApplications` for `ALL_APPS` at `0x2A7E0D..0x2A7E27`, and dispatches refresh events at `0x2A7EF4..0x2A7F22`. `AppsMainScreen.onRefreshApplications`, method-info `0x9F4B`, code `0xC74C`, assigns `contents = Peripheral.appManager.applications` at `0xC777..0xC781` and displays the active category at `0xC7E8..0xC7EB`.

`createApplicationList`, method-info `0x1E7961`, body `0x2A8C91`, code `0x2A8C99`, constructs an `Applet` for each returned entry. It maps signed/returned `xlet.name` and `xlet.appId`, favorite, embedded status, names, status, and icon paths at `0x2A8CE8..0x2A8DC8` and following. Fixed presentation branches handle stock TravelLink, Hybrid Electric Pages, rear-media/Uconnect Theater, Drive Modes, Trip, and KeySense cases; all other entries are generically appended at `0x2A8FC7..0x2A8FCD`.

No generic `enabled`, `disabled`, `hidden`, or `suppressed` field is read by this HMI builder. Native AppManager can still omit an application before returning `getAppList`; the HMI evidence proves that once an ordinary entry is returned, there is no later generic per-app enable gate in the catalog/selection path.

## Alternate taskbar route

The taskbar supplies a second stock human-facing route:

- `TaskBarManager.populateXlets`, method-info `0x1DE635`, body `0x232633`, code `0x23263B`, converts an ordinary application into `apps::AppXlet` at `0x2327A5..0x232806`.
- `AppXlet.press`, method-info `0x1DF628`, body `0x25D301`, code `0x25D308`, closes the popup and calls `appStateManager.startXlet(id,false)` at BCI 39 / `0x25D32F`.
- `AppStateManager.startXlet`, method-info `0x1DEEBC`, code `0x256867`, resolves the `Applet` at `0x25688A..0x256890` and calls `doStartXlet` at `0x256896..0x256899`.
- `doStartXlet`, method-info `0x1DEED2`, body `0x256913`, code `0x25691B`, requires AppManager status `Ready` at `0x256940..0x25694F`, accepts app status `stopped`, `paused`, or empty at `0x256954..0x256983`, and calls module `startXlet(applet.appId,"true")` at BCI 143 / `0x2569AA`.

RU parity places `AppXlet.press` at code `0x249992`, call `0x2499B9`, and `doStartXlet` at code `0x242FA5`, module call `0x243034`.

The taskbar's fixed `IGNORE` dictionary names stock IDs such as `engineering`, `settings`, `travellink`, and `WIFIAP` at ROV `0x231D6F..0x231DEE`. This is hard-coded stock feature routing/omission, not a dynamic application enable bit.

## Java API and exhaustive caller bounds

`kona.jar!com/harman/appManager/AppManagerImpl.class` is 26,295 bytes, SHA-256 `2ddb5e6efd235a3b85b6743585325351d178bbab7c7dff2e476ad2ad08978714`. `startApp(String,String)` method `0x354F`, code `0x3565`, checks `AppMgrPermission("appMgr")` at `0x356E`, sends `appId`/`name`, loads operation `startApp` at `0x35A7`, and calls `SvcIpcClient.invoke(...,30000)` at `0x35B0`. The overload `startApp(String,boolean)` is method `0x4B08`, code `0x4B1E`, with permission check `0x4B27`, operation `0x4B68`, and invocation `0x4B70`.

This permissioned Java facade is used by fixed application/service flows, but the generic user-facing catalog launch is the HMI command path described above. An exhaustive parse of 33,108 class files in 300 physical JARs / 158 unique JAR hashes found 25 resolved `startApp` JVM invocation instructions with zero parse failures. The non-facade callers are fixed Slacker/Via Mobile, DRM Sync, Destinations, OTA, and Airbiquity HUP workflows; constant-pool-only hits were excluded.

An exhaustive HMI parse covered 1,086 physical SWFs / 482 unique hashes, 511 DoABC blocks, 107,112 method bodies, and 183,791 call instructions with zero parse failures. It found exactly 38 `startXlet` invocations: 19 ROV sites and 19 semantically mirrored RU sites. The Apps-menu and taskbar calls above are the generic routes; the others are fixed resume, audio, Performance Pages, Yelp, phonebook, status-bar, and recovery flows.

## Gates and failure behavior

- Duplicate/running selection is suppressed in `AppsMainScreen` and again in module `AppManager.startXlet`.
- Category controls list selection/presentation, not launch authorization.
- Taskbar launch checks AppManager `Ready` and app `stopped`/`paused`/empty; the direct Apps-menu path does not perform that particular HMI readiness check.
- `AppsMainScreen` ignition and speed-lockout handlers affect special settings/WiFi/list presentation, not the generic ordinary-app tile branch proved here.
- Foreground arbitration occurs after launch/request-foreground handling; `checkForegroundAvailability` is code `0x25250E` and `onAppRequestForeground` code `0x2525D2`.
- Module `appMgrMessageHandler` recognizes the `startApp` response at `0x2A8047`; a nonzero `errorCode` dispatches `START_XLET_ERROR` at `0x2A8057..0x2A8075`.
- Native conditional install-time autostart and the global `/fs/etfs/No_AutoStart_App` gate are separate from this manual Apps-menu request.

## Safe-design consequence and remaining boundary

The least-change proof-app design no longer needs to invent a launcher or call SvcIPC directly. If an authorized package is successfully installed and returned by stock `getAppList`, selecting its generic Apps entry uses the factory HMI request and retains native DRM validation. A safe trial must first confirm that installation left the non-autostart app stopped, then launch it through this UI only, observe explicit success/error state, and preserve all stock special-case gates.

The unresolved Jamaica AOT boundary begins after native AppManager hands `start` to AMS. It prevents attribution of additional AMS-internal launch initiators, but it does not weaken the instruction-proven ordinary UI-to-native chain. Remaining runtime checks are whether the authorized helper is returned by `getAppList` with its expected name/icon/category and whether the exact target unit behaves like these static ROV/RU builds.
