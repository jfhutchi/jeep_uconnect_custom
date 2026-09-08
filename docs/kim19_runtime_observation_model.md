# KIM19 runtime observation model

**PROVED, recovered artifacts:** a tile proves much less than a successful launch.
Native AppManager filters the catalog before HMI renders it, and the ordinary
launch path checks authorization separately. **UNKNOWN:** this radio's installed
versions, flags, grants and service state. This report is an interpretation model
for later ordinary UI observation, not a report that the radio was inspected.

Evidence checkpoint: `25fe4d3dc9379e7278cee5ae1ea684715c618430`. All new analysis
uses the isolated stock-signed-capability checkout. No target connection, service
probe, vendor-code execution or recovered-file modification is part of this work.

## How to interpret evidence

| Label | Meaning here |
|---|---|
| PROVED | Directly decoded recovered behavior, or a narrowly stated observation once actually recorded |
| INFERRED | Interpretation conditional on matching production behavior and correctly identified UI |
| UNKNOWN | Evidence cannot isolate the state/cause |
| TARGET OBSERVATION REQUIRED | Must be supplied by later ordinary radio observation |

**PROVED:** `68224525AM` normalizes to `68224525` and selects KIM19 exactly,
without KIM0 fallback. Nine applications, 37 physical files, 19 JARs and 4,572
class entries remain identical to the baseline. **INFERRED:** the damaged
historical log field `6822<525AM` refers to that part; it is not silently repaired.
See [baseline identity](target_production_state.md) and
[activation matrix](../reports/kim19_runtime_analysis/application_activation_matrix.json).

**PROVED:** the recovered sequence separates:

`package membership -> installation/AMS acknowledgement -> AppManager record ->
catalog inclusion -> HMI tile -> authorized start/resume -> Xlet execution ->
working UI -> network operation -> backend acceptance -> usable response`.

**UNKNOWN:** failure at a later state cannot be diagnosed from an earlier state
alone. A name/icon also cannot establish the target's exact JAR hash or version.

## Shared registration and visibility path

**PROVED:** the recovered installer selects/stages package content; AMS/native
installation completion and acknowledgement feed `finishInstall`, which updates
the installed app object, emits `appListUpdated`, persists installed records and
conditionally autostarts. `AppManager_JavaApps` contains `appId`, `name`, `medName`
records in the persistent key/value store. Package files alone are not those
records. See [installation lifecycle](../reports/resident_install_lifecycle.md),
[registry persistence](../reports/appmanager_registry_atomicity.md), and
[install pipeline](../reports/application_install_pipeline.md).

**PROVED:** ordinary Apps requests a category/sort-filtered list. MainSupplement
turns returned entries into Applets using identity/name/status/icon properties;
Apps displays those objects. All Apps, Favorites and Running are distinct views
(`-2`, `-1`, `-3`). Name/start-time sorting means order is not installation order.
Category changes and a stale list can explain a partial observation. Full HMI
offsets and the AMS association are in
[app launch UI path](../reports/app_launch_ui_path.md) and
[key.jar association](../reports/keyjar_runtime_association.md).

**PROVED:** native `appManager` SHA-256
`608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591`
contains the following concrete logic. Addresses are ARM virtual addresses;
subtract `0x100000` for file offsets at these sites.

| Native site | PROVED behavior | Interpretation limit |
|---|---|---|
| `0x1330d4`, `0x13311c/0x133124` | Visibility updater iterates app objects, with a type discriminator | UNKNOWN exact meaning of all object types |
| `0x133150..0x133164` | Evaluates descriptor conditions if `(byte[app+0x29a] & 8) != 0 OR byte[app+0x294] != 0` | UNKNOWN provenance/meaning of those flags; do not call them proved DRM grants |
| `0x1331c8`, `0x1333c4..0x133460` | Iterates conditions; compares current PPS strings to accepted alternatives | PROVED equality/OR within each set when attributes exist |
| `0x1334b0..0x1334e0`, `0x133774` | A present but nonmatching value exits false; a missing attribute logs an error, sets false and continues | PROVED missing data can be overwritten by a later condition; not a simple fail-closed AND |
| `0x133550..0x1335d4`, `0x133784` | Non-evaluation branch defaults visible except conditional ASSIST suppression | PROVED descriptor presence alone does not guarantee evaluation |
| `0x133658` | Stores show-in-HMI byte at `app+0x4d` | PROVED cached app visibility state |
| `0x125664/0x12566c`, `0x125978/0x125980` | Catalog skips entries with false visibility | PROVED consumption, not merely an unused setter |
| `0x12592c..0x125970` | Other virtual predicates precede visibility testing | UNKNOWN complete semantic names of these extra filters |

**PROVED:** `readShowConditions` also logs rejected attributes outside `/pps/can/`
and malformed/empty conditions (strings at file `0x1188f4`, `0x118974`,
`0x1189e8`, `0x118a58`). The new parser deliberately accepts only the valid
recovered descriptor subset; it does not emulate malformed native recovery.

**PROVED:** ordinary `startApp` enables DRM checking at file `0x50650`, enters
`findAndStartApp` at `0x5066c`, and can fail before AMS start for missing app,
missing AMS or authorization. Conditional autostart uses launcher-mask bit 2
or super-app override and a global gate. **UNKNOWN:** a tile's presence does
not prove either manual-launch or autostart entitlement.

## Application-by-application interpretation

**PROVED:** exact UUID, main class, external descriptor, JAR, properties, category,
icons, language names and version for all nine identities are preserved in the
[machine-readable activation matrix](../reports/kim19_runtime_analysis/application_activation_matrix.json).
The lifecycle rows below are **PROVED static calls**; first-screen predictions
are **INFERRED**, and their occurrence is **TARGET OBSERVATION REQUIRED**.

| Identity/version | Startup and first effect | Later dependencies/failure phase | What an entry does not settle |
|---|---|---|---|
| Yelp 03.00.33 | Manual conditional start; container/Display, serial initialization, splash, delayed home/search | Init/theme/platform failures before home; HTTP/backend only when a request runs | Exact binary, network, backend, subscriber state |
| DRMSync_VSB 03.01.07 | Declared daemon/headless; init starts worker, startXlet empty | VSB validity, low power, processing, subscriber/VIN/provisioning and backend gates | No tile says nothing about daemon activity |
| ASSIST 04.00.14 | Init schedules loading splash, then MainLandingScreen | Container/platform/local VSB/phone services; service action after UI | Active subscription or working calling |
| Viper Performance Pages 01.23.01 | Conditional catalog; GSkillsModule/UI runnable/home work | Vehicle sensors, resources, module initialization | Same visible name does not identify variant |
| Store 02.33.07 | Config/start arguments; serial loading screen; discovery request | Discovery/vault/account failures after loading screen | Absence does not identify account/provisioning state |
| Jeep Performance Pages 01.57.01 | Conditional catalog; GSkillsModule/UI runnable/home work | Vehicle sensors, resources, module initialization | Visibility is not launch DRM or verified vehicle configuration |
| L-Series Performance Pages 02.01.01 | Module init and managed UI runnable | Explicit unsupported-vehicle rejection during init AND start | Catalog inclusion does not defeat later module check |
| Register 02.03.01 | Init checks cached stage, then scheduled loading screen | Destruction notification during init or subscriber failure after screen | Presence does not mean unregistered; absence does not mean registered |
| VSBClient 04.03.23 | Declared daemon/headless; init queues config/MQTT/SMS/IXC worker; startXlet empty | Config/credentials/TLS/connection/registry gates | No tile does not establish stopped/uninstalled |

## Three Performance Pages variants

**PROVED:** all three packages coexist physically in KIM19, have distinct UUIDs
and the same display name. Each declares `xlet.showConditions`:

| Variant | Feature attribute | Vehicle-line attribute | Additional recovered module behavior |
|---|---|---|---|
| Jeep | `/pps/can/vehcfg/VC_PP_Prsnt:1` | `/pps/can/vehcfg/VC_VEH_LINE:1` | Reads vehicle brand/TRANS_TYPE and prepares UI/resources |
| Viper | Same feature predicate | `/pps/can/vehcfg/VC_VEH_LINE:43` | Reads vehicle brand/TRANS_TYPE and prepares UI/resources |
| L-Series | Same feature predicate | `/pps/can/vehcfg/VC_VEH_LINE:{44;41;2}` | Maps vehicle state; rejects UNSUPPORTED at module init and start |

**PROVED:** if native condition evaluation is active and both attributes exist,
these mutually exclusive line conditions allow at most one variant to satisfy
the recovered predicates at one instant. **UNKNOWN:** actual simultaneous target
installation and exposure; bypass/default-visible paths and missing PPS prevent
an unconditional exclusivity claim from filenames alone.

**PROVED:** L-Series `GSkillsModule.initModule` compares `VehicleLineEnum.UNSUPPORTED`
at BCI101/104/107 and throws at BCI146; `startModule` repeats the comparison at
BCI12/15/18 and throws at BCI83. Its Xlet init catch calls `notifyDestroyed` at
BCI30. **UNKNOWN:** an equivalent rejection was not established in the inspected
Jeep/Viper module paths; their shared `defineCarBrand` even contains a comparison
to line 43, so names must not replace analysis of runtime branding behavior.

**PROVED:** HMI recognizes Performance Pages specially and calls
`fullStartDaemonXlet` rather than the ordinary `startXlet` branch. That HMI choice
does not by itself establish descriptor daemon state or a completed launch.

**INFERRED:** if a Jeep variant is independently identified, the correct native
flags are active, both PPS values exist and the catalog is fresh, its visible
tile supports PP=1 and line=1 at evaluation time. **UNKNOWN:** an ordinary photo
of "Performance Pages" alone proves none of those assumptions or launch DRM.
The single better observation remains a normal Yelp launch if available.

## Register, Store and ASSIST

**PROVED:** Register's `HuRegistrationManager.isRegistrationShow()` reads cached
subscriber state, validates it, and returns true for `COMPLETED_STAGE_3` or
`FULL_STAGE_2`. In that branch it calls `XletContext.notifyDestroyed` at BCI89.
Null/invalid state and the handled JSON exception return false. This is an
**init-time lifecycle check**, not a catalog show predicate.

**PROVED:** Register init calls that helper at BCI30 and, on true, calls its own
`destroyXlet(true)` at BCI71. That method only logs; there is no return after the
call in init, which falls through to container setup at BCI82 and Display setup
at BCI94. **UNKNOWN:** timing of AMS response to the earlier destruction
notification; neither deterministic early-abort nor persistent tile removal is
proved. **UNKNOWN:** exact conditions for disappearance from every Apps view
remain unresolved. A present Register tile is not a provisioning-state oracle.

**PROVED:** Store init reads configuration and passes `startArgs.drm.accountDN`
and `emailID` into application data. `StorefrontLoadingScreen.onShowCompleted`
constructs discovery at BCI37 and queues it at BCI40. In `updateVault`, a present
vault plus invalid Uconnect ID prompts a confirmation; accepting invokes
`launchRegistration` at BCI72 and returns at BCI75. Otherwise later code registers
a DRM notification listener. Missing vault retries can reach an alert and
`notifyDestroyed` at BCI267. These are post-UI gates, not proof that an absent
Store tile means no account. **TARGET OBSERVATION REQUIRED:** record any existing
account/service text without confirming registration, purchases or changes.

**PROVED:** ASSIST has a native special case in the default-visibility branch.
Helper VA `0x129b2c` requires `getenv("VARIANT_PRODUCT") == "524"`, reads
`ECSB_PRSNT` from `/pps/can/vehcfg0`, and returns true when its integer value is
not 1. A true helper suppresses ASSIST at VA `0x1335d4`. **UNKNOWN:** that branch's
applicability and values on the radio; do not generalize it to every variant.
**PROVED:** ASSIST reaches a landing screen through serial callbacks; its
communication manager locates VSB and binds a local callback. **UNKNOWN:** a
landing screen establishes neither backend service nor a successful phone call.

## Using the model

Use the [operator checklist](target_observation_checklist.md), then the
[Yelp cases](kim19_yelp_reachability.md). The
[network report](kim19_network_capabilities.md) separates response/callback paths
from external reachability, and the
[background report](kim19_background_services.md) explains why missing service
tiles cannot identify daemon state. **INFERRED:** Yelp remains the strongest
candidate because its ordinary launch and user-visible search-result chain are
concrete. **TARGET OBSERVATION REQUIRED:** determine whether it is exposed and
what its first normal launch displays.
