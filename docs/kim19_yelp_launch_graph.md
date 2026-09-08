# KIM19 Yelp launch graph

This graph is the recovered-artifact answer for Yelp 03.00.33. **PROVED** means
the stated edge exists in recovered code or committed launch evidence;
**STRONGLY SUPPORTED** is a cross-artifact conclusion with a remaining runtime
edge; **TARGET OBSERVATION REQUIRED** is current-radio state. The canonical
machine-readable graph is [launch_graph.json](../reports/kim19_yelp/launch_graph.json).

## Ordered graph

| Order | Edge | Classification | Exact boundary |
|---:|---|---|---|
| 1 | `xlet.properties` -> virtual-app catalog | **STRONGLY SUPPORTED** | GUID `1D5347C0-8B5E-11E2-9E96-0800200C9A66`, main class `YelpPOIXlet`, GUI/non-daemon, AppCategory 2; current registration is not in the update image |
| 2 | Apps tile -> HMI `startXlet(appId)` | **PROVED** | Reuses the selected-app dispatch in [app launch UI path](../reports/app_launch_ui_path.md) |
| 3 | HMI -> AppManager/DRM -> AMS | **PROVED** | Native catalog predicate is `!headless && (!daemon || hasGUI) && showInHmi`; start uses the recovered DRM check and `findAndStartApp` chain |
| 4 | AMS -> `YelpPOIXlet.initXlet` | **TARGET OBSERVATION REQUIRED** | Current signer association, grants, registration, and actual return value are target state |
| 5 | `initXlet` -> IXC/container/LWUIT | **PROVED** | `IxcRegistry.getRegistry` BCI 23; `getContainer` BCI 52; container visible BCI 60; `Display.init` BCI 64; pure touch BCI 71; third soft button disabled BCI 78 |
| 6 | `startXlet` -> UI runnable | **PROVED** | `Display.callSerially` BCI 23 and `_appStarted=true` BCI 28; subsequent starts take the already-started return path |
| 7 | runnable -> local setup -> splash | **PROVED** | Applies common/Yelp themes, locale, three RMS datasets, metrics, then `YelpSplashScreen.show` BCI 38 |
| 8 | splash -> worker -> location | **PROVED** | `Thread.start` is triggered on show completion; worker sleeps 3000 ms at BCI 43, calls `GpGeoUtil.LocationInfo` BCI 54, then schedules the UI callback BCI 68 |
| 9 | screen callback -> first home | **PROVED** | 8.4/default selects screen ID 70 at BCI 124, which `GpScreenManager` maps to `GpCurrentLocationScreen`; 6.5 selects ID 74 |
| 10 | home constructor -> useful local UI | **PROVED** | `VRHelper.getInstance` BCI 47, `SpeechListener` enable BCI 57, RMS list BCI 74, `layoutForm` BCI 77 |
| 11 | touch/voice -> request -> result | **PROVED** | Both paths construct `GpSearchRequest`, enqueue it, block on the spinner, and select service-error, zero-result, result-list, or generic-failure UI |

## Earliest useful state

**PROVED:** the earliest useful state is the local current-location home, with
category tiles, editable search field, and voice control. It requires lifecycle,
resources, RMS/location initialization, splash scheduling, and the home/VR
constructor. It does **not** require a Yelp HTTP response, search-backend
authentication, geocoder response, or a parsed business.

**PROVED contradiction preservation:** the splash log says five seconds but the
bytecode sleeps for 3000 ms. A generic property-read exception in `initXlet` is
logged and allowed to return, while an unavailable container explicitly calls
`destroyXlet(true)`. Startup-runnable `Throwable` is logged without a replacement
screen. These are distinct outcomes, not one generic “launch failed” state.

`pauseXlet` only records common state 12. `destroyXlet` records state 13 and saves
the three RMS datasets; it ignores its boolean argument and does not visibly call
`notifyDestroyed`. Those facts are **PROVED** but do not establish what AMS shows
after pause/destruction on a live target.
