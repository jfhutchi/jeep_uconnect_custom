# Target production state: 68224525AM / RA4 18.45.01

Research date: 2026-09-07. Recovered-artifact analysis only; no radio, network
endpoint, installer, diagnostic write, or vendor executable was exercised.

## Result and evidence convention

**PROVED:** the recovered production selector maps the exact supplied part
number **68224525AM -> 68224525 -> KIM19**. It does not fall back to KIM0.
KIM19 contains nine application descriptors, nine application payload JARs,
nine companion key JARs, one package-level DRM JAR, and nine magic markers:
**37 files, 19 JARs, 4,572 class entries**. The common `base` tree is copied
separately and is not a tenth KIM application.

**PROVED:** the existing stock Apps catalog and manual launch mechanism is a
production HMI path. **CONDITIONALLY REACHABLE:** selecting an already registered
and authorized Yelp app can reach its bundled splash/home UI without installing
new code. **UNKNOWN:** whether that exact application is currently installed,
listed, authorized, and working on this radio. No network listener acquired a
complete, satisfied activation chain on the actual target in this phase.

Evidence labels are **PROVED**, **INFERRED**, **UNKNOWN**, and **DISPROVED**.
PROVED describes the particular static fact stated, not successful execution on
the radio. Direct JVM invocation instructions are distinguished from inferred
AMS lifecycle, virtual receiver, event, and scheduler dispatch. Candidate
classes A-G describe reachability separately from those evidence labels.

The machine reports are the detailed evidence ledger:

- [Part resolution](../reports/target_production_state/part_number_resolution.json):
  selection stages, locations, fallbacks, artifact hashes, supplied identity.
- [Package inventory](../reports/target_production_state/package_inventory.json):
  every file/member identity, all nine descriptors, lifecycle declarations,
  permissions, API sites and resource-name references, preserving caller and
  callee descriptors and JVM bytecode offsets.
- [Candidates](../reports/target_production_state/capability_candidates.json):
  all ten reachability questions for each of 14 candidates, source hashes,
  selected method call records, common-base manifest and second-pass results.
- [Validation](../reports/target_production_state/validation.json): fresh test,
  repeat-index, source-integrity, independent-disassembly and scope results.

## 1. Exact part selection, including the other revision stage

Artifact paths here are relative to the recovered
`analysis_ra4_18.45.01/work/` root. The JSON source dictionaries give full
relative paths and SHA-256 identities. BCI means offset within a JVM method;
Lua locations below are offsets in the serialized recovered file. SWF locations
are decompressed FWS offsets, as in the inherited HMI report.

| Stage | Exact evidence | Meaning for this target |
|---|---|---|
| Apps update unit | `installer_iso/etc/manifest.lua` lines 113-126, 226-235 | The 18.45.01 manifest includes installer `xlets`, source `usr/share/XLETS` on `secondary.iso`, destination `/fs/mmc1/`. |
| Read selection input | `installer_iso/usr/share/scripts/update/installer/xlets.lua`, root `0x48`, closure captures `0x68-0x88`; fn6 calls `0xfe5` and `0xff1` | Reads `/dev/fram/partnumber`, then passes fn4's result to fn5. The supplied user value is modeled; FRAM was not read on the radio. |
| Normalize | fn4 open `0xcc9`, read(10) `0xcdd`, pattern call `0xd05`, substring call `0xd25` | Anchored eight digits plus two letters matches `68224525AM`; substring 1..8 returns `68224525`. `AM` is not compared with a minimum revision. |
| Exact lookup | `secondary_iso/usr/share/XLETS/kim_packages/kim_pkg_map.lua` **line 74** | `kim_pkg_map["68224525"] = "KIM19"`, comment `MY14 VP4 NA`. No neighboring-key inference. |
| Selector default | fn5 `0xea7`, `0xebf`, `0xed3`, `0xee3`, `0xee7` | Initial KIM0; execute shipped map, exact table lookup, return matching value. The matched row wins. Missing table/key retains KIM0; a failed `dofile` is not caught as a successful fallback. |
| Market directory | fn6 `0x1011-0x1041` | China/CH selects working name `xlets`; other values use `xletsdir`. This changes the destination directory, not KIM19. |
| Common and selected copy | fn6 `0x11f9`, `0x1219/0x1221`, `0x1299`, `0x144d`, `0x14d5` | Common base, then non-KIM0 selected package to `kona/preload`, selected resource tree, and selected Xlets to working tree. KIM19 has no separate resource directory in the recovered tree. |
| Completion/registration boundary | fn6 copy-progress/error branches through `0x1635`, post-installer call `0x1719`; `jvm.sh` line 63 | Selection is not successful copying or registration. AMS later opens mutable `/fs/mmc1/xletsdir` with stock security. |

The new ASCII model reproduces the read window and pattern order. It also
preserves nonmatching raw values: the bytecode overwrites `PN ERROR` with the
read result before matching. An open failure retains `PN ERROR`; a nil read
remains nil; a short eight-digit read passes through; nine initial digits are
truncated to nine. Those details are tested and must not be replaced with a
more restrictive invented normalization rule.

The pre-installer file `secondary_iso/etc/xlets_mmc1_preinstall.txt` removes
legacy `kona-fiat-permissions.jar` and old `kona/data/DRM.jar`; it does not choose
a KIM. The existing [qkcp analysis](../reports/qkcp_kim_copy_semantics.md)
establishes recursive merge/overwrite, not an atomic mirror or guaranteed
rollback. Working copies, later AMS upgrades, retained state and failed updates
can therefore differ from the selected source tree.

There is a **separate ECU revision table**, found in both
`installer_iso/etc/ecupart.lua` and
`primary_iso/usr/share/OTA/fota_installer/etc/ecupart.lua`. Both have the same
SHA-256 and line 27 explicitly assigns
`ecu_part_number["68224525"] = "68224525AM"`. This is an output revision,
not an alternate KIM mapping.

The full installer `softwareupdate.lua` fn14 reads ten bytes and returns base
and suffixed part values (`0x22e3`, `0x22f7`, `0x231f`, `0x233f`, `0x235b`).
Fn13 loads `ecupart.lua` and returns the matching revision (`0x21cc`, `0x21e0`,
`0x21f0`); a missing key yields nil here, not KIM0. Following successful
installation, fn19 calls fn14 at `0x2934`, fn13 at `0x2948`, and compares the
old/new suffix values at `0x2958`. Root closure bindings `0x238/0x23c`
independently identify those callees. No recovered write was executed.

The FOTA `softwareupdate.lua` is **plaintext**, unlike the full installer's
compiled chunk. Its `getNewECUPartNumber` lines 473-484, `getPartNumber`
489-514 and `partnumberUpdate` 563-581 independently confirm the same 8+2
normalization. `beginUpdate` lines 633-635 dispatches component `partnumber`
to that revision stage. This does not force or select an Xlet KIM.

A stem search also finds `68224525Z` and `68224525A` in native `ndr` at file
offsets `0x8e884` and `0x8e890`. These are not exact `68224525AM` assignments
or a KIM table. Their consumer-to-KIM relationship is **UNKNOWN**; they do not
override the direct installer/map proof. Exact AM occurrences in the recovered
selection/revision configuration are the two `ecupart.lua` rows.

No App/Boot/Nav version comparison exists in the KIM fn4/fn5 decision. The
manifest's 18.45.01 identity and outer firmware compatibility/authentication
remain prerequisites for applying that source tree. `primary_iso/etc/version.txt`
contains a MY17/NAFTA/VP4 build label; it does not negate the map's explicit
MY14 entry. These artifacts do not prove that every recorded historical update
actually installed the Apps unit on this radio.

## 2. Exact KIM19 applications and activation limits

All entries below are **PROVED present in recovered KIM19**. Main classes,
UUIDs, complete descriptors, lifecycle method signatures and hashes are in the
machine inventory. All nine declare `security.policy` and `full.policy` as the
policy/default names. Each payload's actual `security.policy` declares
`InterfacePermission "ppp0"`; VSBClient also declares private-sensor,
on/off-control and AppManager permissions. Effective granted permissions still
depend on stock AMS policy/identity; `full.policy` is not proof of AllPermission.
Companion key JARs are inventoried by hash/member metadata only, with no key
payload copied into these reports.

| Payload JAR | App/version | Main class | Production activation/configuration evidence |
|---|---|---|---|
| `640X480_84_Yelp_v03.00.33_FIT.jar` | Yelp 03.00.33 | `com.sprint.chrysler.yelp.xlet.YelpPOIXlet` | Category 2, daemon=false, pause=true; ordinary manual Apps launch. No descriptor showConditions. |
| `DRMSync_VSB_03.01.07_FIT.jar` | DRMSync_VSB 03.01.07 | `com.sprint.chrysler.drm.xlet.DrmSyncXlet` | daemon=true/headless=true; init constructs IXC notification service and starts DrmManager thread at BCI85. |
| `640X480_84_Assist_VSB_04.00.14_FIT.jar` | ASSIST 04.00.14 | `com.sprint.chrysler.assist.xlet.AssistXlet` | Category 5; init calls startAssist BCI129; `$1.run` creates/shows loading splash BCI32/35. |
| `GSkills_Viper_v01.23.01_FIT.jar` | Performance Pages 01.23.01 | `com.sprint.gskills.xlet.GSkillsXlet` | showConditions: `VC_PP_Prsnt:1`, `VC_VEH_LINE:43`. |
| `640X480_84_UconnectStore_v02.33.07_FIT.jar` | Store 02.33.07 | `com.sprint.chrysler.storefront.xlet.StorefrontXlet` | Category 5; init tests vehicle configuration BCI69 and calls processDRM BCI89; start calls initStorefront BCI16. |
| `GSkills_Jeep_v01.57.01_FIT.jar` | Performance Pages 01.57.01 | `com.sprint.gskills.xlet.GSkillsXlet` | showConditions: `VC_PP_Prsnt:1`, `VC_VEH_LINE:1`. |
| `GSkills_MY15_LSeries_v02.01.01_FIT.jar` | Performance Pages 02.01.01 | `com.sprint.gskills.xlet.GSkillsXlet` | showConditions: `VC_PP_Prsnt:1`, `VC_VEH_LINE:{44;41;2}`. |
| `640X480_84_UconnectRegistration_v02.03.01_FIT.jar` | Register 02.03.01 | `com.sprint.chrysler.uar.xlet.UconnectRegistrationXlet` | Category 5; init calls isRegistrationShow BCI30 and can destroy BCI71; start queues UI at BCI18. |
| `VSBClient_04.03.23_FIT.jar` | VSBClient 04.03.23 | `t.s.e` | daemon=true/headless=true; init queues `t/s/c` at BCI31; startXlet itself returns immediately. |

KIM19 selecting all three Performance Pages payloads does not establish the
target's PPS values or prove that all three will be shown. Even the Jeep name
does not prove `VC_PP_Prsnt=1`. Likewise, `daemon=true` is a declaration rather
than a current-process observation. Native post-install autostart has a DRM
launcher-mask/super-app and global-autostart gate, independently proved at
AppManager files `0x1bb38/0x1bb3c/0x1bb64` and `0x93858` in the
[authorization report](../reports/kona_application_authorization.md).

The common base has **24 physical files**, separately listed in the candidates
JSON. Its Kona library, initializer, AMS properties and production/development
security configuration are shared framework, not separately selected apps.
The boot chain to AppManager and secure AMS is preserved from the
[startup analysis](../reports/ams_startup_chain.md). Native Wi-Fi, ConnMgr,
Bluetooth/media services, inetd configuration and 3proxy are outside KIM19
and are analyzed as shared production framework.

The index records physical code, descriptor registration intent and lifecycle
entry definitions separately from **UNKNOWN actual registration/activation**.
API counts are syntactic call candidates, including bundled library code. Test
name flags are search aids, not dead-code classification. No unvisited method
is declared dead merely because this phase did not find its predecessor.

## 3. Expected firmware versus the actual radio

| Required category | What the evidence establishes |
|---|---|
| EXPECTED FROM PRODUCTION MAP | Exact supplied part selects the nine-app KIM19 source tree plus common base, conditional on successful installation. |
| PRESENT IN RECOVERED FIRMWARE | Exact descriptors, JAR/member hashes, native startup/configuration files and build manifests. These are update-image contents. |
| PROVED INSTALLED ON THIS RADIO | No independently verified current per-app inventory, AppManager capture, filesystem hash list or registration database was found. The user reports part 68224525AM, system 18.45.01, App 19.39.20, Boot 17.9.0, Nav 9.10.32.702279; these are accepted as supplied observations, not a nine-app inventory. |
| UNKNOWN | Current visible and hidden app identities/versions, completed Apps-unit update, later upgrades, actual DRM state, vehicle configuration predicates, service flags and running listeners. |

An important version distinction is now resolved: the recovered
`primary_iso/usr/share/V850/TB/manifest.xml` line 5 says
`19.39.20 app 17.09.00 bolo`. **PROVED:** those strings describe the V850
application/bootloader package. **INFERRED:** after formatting normalization,
they correspond to the supplied App/Boot values. They are not Yelp's Xlet
version. The recovered version file says system 18.45.01; the navigation
binary also contains the supplied navigation version string. Matching build
values is corroboration of firmware family, not live application registration.

The earlier map-update report needs a narrower reading. Raw
`recovered_root_helpers/swdlLog_recovered.txt` is bit-damaged. At offset
`0xfed1f` it contains `68224525AH`; the subsequent new-part field reads
**`6822<525AM`**, followed by damaged success text and `Version = 17.11.17`.
The earlier expansion to exact `68224525AM` is **INFERRED**, corroborated by the
clean ECU table, not a clean literal recovered from the log. Linking that
historical event to this particular current radio also remains unproved.
The uncorrected sibling `swdlLog.txt` begins with zeros and is not a second
independent confirmation. Neither log proves current KIM19 installation.

Repository reports, known recovered helper logs, materialized firmware
descriptors/manifests/version files and named image assets were searched.
The engineering PNGs found under the firmware HMI tree are shipped artwork,
not screenshots of this unit. No serial-bound current app inventory or matching
installed-payload hash capture was identified. This is a bounded search result,
not proof that no such evidence exists outside the repository/corpus.

## 4. Current Yelp: activation, inputs, dispatch and effects

The exact KIM19 Yelp payload has **274 classes and 35 non-class resources**.
Every class was parsed; relevant method call records are retained in the
candidates JSON. Independent `javap -c -p` checks use this exact JAR, not an
earlier Yelp or another KIM's similarly named class.

### Stock launch and first observable effect

```text
Human selects existing ordinary Yelp tile
  -> AppsMainScreen.onItem: selected appId, MoreScreen
  -> MainSupplement AppManager.startXlet: startApp request
  -> native start handler: findAndStartApp(DRM-check=1)
  -> App::start / AMS-facing start
  ~> AMS lifecycle dispatch: YelpPOIXlet.initXlet/startXlet
  -> init: getContainer(52), setVisible(60), Display.init(64)
  -> start: if not _appStarted, construct $1(20), callSerially(23)
  ~> LWUIT EDT runs YelpPOIXlet$1.run
  -> load bundled theme/language and saved search lists
  -> new YelpSplashScreen(35), show(38)
```

`->` represents recovered direct calls/data flow; `~>` marks inferred runtime
callback/lifecycle dispatch with a registered object. The HMI/native portion is
source-addressed in [app_launch_ui_path.md](../reports/app_launch_ui_path.md):
HMI call FWS `0xc1e6`, module send `0x2a97e7`, native DRM-check argument file
`0x50650`, dispatch call `0x5066c`, and App::start call `0x3c328`.

The splash loads `/res/splash_screen_yelp_<language>...` from bundled resources.
Its `onShowCompleted` starts `$1` at BCI10; the worker obtains location at BCI54
then schedules `$1$1.run` at BCI68. That callback switches screen type at BCI60:
65 goes to screen 74; **84/default goes to screen 70 at BCI124**.
`GpScreenManager.createForm(int)` has a fixed 70-77 switch; 70 constructs
`GpCurrentLocationScreen` at BCI64. This is fixed screen dispatch, not an
external class-name factory.

The first splash does not require a search response. Resource failure is
caught/logged by the startup runnable; it is not proof of a successful UI.
Location/VR/native services may affect progression beyond it. Normal lifecycle
loads and, on destroy, saves its own search lists; the optional app-launch
experiment is an ordinary benign action, not a promise of zero internal writes.

### Search input to rendered data

`GpCVPKeyboard.fireOKPressed` constructs `GpSearchRequest` at BCI227, queues it
at BCI234, reads results at BCI401, and navigates to the results screen at
BCI443/456. Category selection constructs the same request in
`GpPlaceIconButton.click` BCI126. Voice's `SpeechListener.onVRAction` constructs
it at BCI58, queues at BCI63, reads results at BCI198 and navigates at BCI242/254.
These are real fixed actions. Keyboard/category handlers and voice callbacks
are not a generic command interpreter.

`ConnectionManager.processNextRequest` creates a worker at BCI51 and starts it
at BCI89. `BaseRequest.run` calls establishConnection BCI1, CallService BCI8,
processResponse BCI14, then releases waiting UI through dialog disposal and
latch countDown BCI41. Virtual calls to `getURL`, `processStream` and
`processJSONObject` resolve to the request subclass by the explicit constructed
object; runtime virtual dispatch is **INFERRED**, not a direct static edge.

`BaseRequest.establishConnection` checks emulator BCI18 and `/fs/etfs/use_en0`
existence BCI29. Without those exceptions, it gets stock Connectivity and calls
`connectInternet` BCI95 with bounded retries; failure leads to the normal error
flow. No marker was created or changed. The normal `CallService` constructs
**DefaultHttpClient at BCI32 and executes at BCI53**.

`GpBaseRequest.processStream` reads response text, constructs JSON BCI62, and
calls processJSONObject BCI70. `GpSearchRequest.processJSONObject` handles error
and business arrays, populates fixed `Place` fields (e.g. name setter BCI202),
then adds objects to the result list at BCI678. Those values are displayed by
the results route. No response-controlled Java class or process launch was
proved. A real result still needs accepted HTTPS, usable connectivity and a
functioning backend; no external endpoint was contacted in this phase.

### Configuration, phone, voice, location and IPC

| Input/configuration | Receiver and evidence | Applicability/effect |
|---|---|---|
| `xlet.properties` | Yelp init BCI85/101/108 | Reads bundled Xlet version and logs it. printPlatformInfo reads PlatformInfo BCI2/5; log visibility to an ordinary user is UNKNOWN. |
| `yelp.properties`, `yelppoconf.properties` | GpGeoUtil class initializer BCI57 -> loadProperties, resource loads BCI20/39, endpoint setters BCI69/73 | Bundled `places_api_base=https://vsb.cvp.extra.chrysler.com/yelp-api/v2/search`; geocode endpoint `https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/find`. Resource configuration, not a demonstrated writable external override. |
| Location | GpGeoUtil.LocationInfo BCI0/6/87/92/97 | `usefakegps=false` selects resident GeoLocationInfo on non-emulator. Fake coordinates are selected only by the alternate flag/emulator branch. |
| Spare fake-business setting | `fakebizlocation=true`; isBizLocationFake helper | Helper is physically present, but no invocation of isBizLocationFake was found in this exact JAR. Do not claim all production business locations are forced by this resource. |
| Location callbacks | AqLocationProviderImpl constructor BCI18/64 registers LocationListener; listener locationUpdated/providerStateChanged | Resident location data callback path; no externally exposed network receiver established. |
| Voice recognition | VRHelperImp.init BCI51/56, 297/305/331 | Selects supported stock VR service/session, installs state/speech listeners; SecureService credentials API is used at BCI246. Credentials were neither extracted for use nor altered. Recognized action reaches the fixed search flow. |
| Phone status | GpDetailsScreen constructor BCI24/59 | Uses PhoneManager and registers status listener. processDial BCI33 is a separate actual dial action, excluded from the benign proof. It does not prove a Yelp Via Mobile transport. |
| IXC | Yelp init BCI23 gets IxcRegistry | No bind occurs in this lifecycle. Bundled DrmNotificationManager can bind at BCI25, but no Yelp call into its setup/register was found. Registry acquisition alone is not endpoint activation. |
| AppManager | HuCommon.getUConnectId/getDrmVin call getAllDRM BCI7; AppInfoManager.loadAppIdentifierList calls queryAppIds BCI37 | Shared metadata helpers present. No generic external request-to-AppManager start/install path through Yelp was found. Effective permission and caller activation remain distinct. |
| Stored searches/language/theme | startup runnable BCI2/5/8/15/21/24; destroyXlet BCI16/19/22 | Existing UI resource selection and RMS search history; no input-to-code loader proved. |

### Comparison with old Tweddle Yelp

The current main implements `javax.microedition.xlet.Xlet` directly; it does
not extend old `AbstractHUXlet`. No Tweddle namespace, SocketCommandSource,
CommandLooper, Socket-named or Test-named class exists in the exact current
payload. No retained or replacement command/test framework was established.
The old framework's behavior must not be transferred to this application.

Current `WebClientDevWrapper` and its permissive TLS helper classes are
physically present, but there is **no invocation of wrapClient in this JAR**.
The inspected production request constructs a plain DefaultHttpClient. The
word "Dev" is not itself proof of disabled code; the absent caller and actual
CallService implementation are the relevant evidence. No runtime reflected
activation of that wrapper was proved. The only three Yelp ClassLoader API
sites read bundled properties; there are no Yelp reflection, process-launch,
native-library-load or socket-construction call sites in the inventory.

## 5. Ranked service/capability results

The machine candidate entries answer constructor, starter, enable condition,
target satisfaction, address/interface, role, authorization, input, benign
effect and chain completeness separately. A means a recovered production
route is proved; it is not a claim that a live radio was tested. B means
conditions remain. C/D/E/F/G mean configured-disabled, test/emulator,
static-presence, disproved and unknown respectively.

| Rank | Candidate | Class | Supported result and unresolved gate |
|---:|---|---|---|
| 1 | Ordinary Apps catalog | A | Existing HMI getAppList request/response displays names/icons. Actual returned list unknown; this is the least-invasive read-only observation. |
| 2 | Yelp bundled UI | B | Complete recovered manual-launch and bundled splash route, with lifecycle/scheduler inference explicit. Actual listed identity, DRM/AMS acceptance and rendering unknown. Highest-ranked app capability. |
| 3 | Yelp HTTPS search | B | Fixed UI input -> request -> JSON -> results/error display. Live network/server and entitlement state unknown. |
| 4 | Performance Pages | B | Fixed GSkills module factory and lifecycle start; three descriptor vehicle predicates must not be assumed satisfied. |
| 5 | ASSIST/Store/Register initial UI | B | Selected lifecycle paths present; registration/DRM/business-state gates. No account, purchase or support action proposed. |
| 6 | VSB MQTT | B | Real production daemon initialization and authenticated outbound MQTT client; no harmless owner-controlled broker-to-effect route proved. |
| 7 | DRMSync IXC | B | Real daemon init creates notification service/worker; actual start, DRM/VSB state and benign external input route unknown. |
| 8 | Microlog 1234 | E | Shared SocketLogServer.main constructs/starts it, run creates ServerSocket BCI17, accepts BCI102. No production main/start predecessor found. |
| 9 | Airbiquity test HTTP | D | Previously traced enableUT/emulator listener belongs to HUP copies outside selected KIM19; no UnitTestUtil/startUnitTest site in selected inventory. |
| 10 | Native telnet | B | USB enum -> adapter script -> authorized network flag -> inetd. Flag satisfaction, login and actual interface unknown. Diagnostic starter is not a read-only option. |
| 11 | Native 3proxy | E | Loopback proxy configuration plus route-update/reload predecessor. Initial production process launcher still unknown. |
| 12 | Bluetooth/Via Mobile | G | Framework/device callbacks present; no complete current Yelp transport-to-benign-effect chain. Register's isViaMobileSupported is merchandising JSON, not transport registration. |
| 13 | USB/media callbacks | G | Production ConnMgr/MCD event rules found; complete user-visible media handling chain not closed here. No selected-KIM code importer found. |
| 14 | Wi-Fi service | B | Recovered boot starts WifiSvc through wlan_startup.sh; current hardware/configuration and benign status-to-HMI chain unknown. |

VSB is not just a Paho-library grep hit. `t/s/e.initXlet` constructs state and
queues `t/s/c` at BCI31. `t/s/c.run` obtains the `t/b/b` Runnable at BCI167 and
queues it at BCI170. `t/b/b.run` enters its state/configuration connection logic;
`d -> f -> g` reaches `t/b/a.c`, which calls `MqttClient.connect` BCI25.
`t/b/a.a(SSLSocketFactory)` sets TLS socket factory BCI68, authentication fields
BCI88/101, constructs the non-emulator client BCI226 and registers callback
BCI239. `messageArrived` parses JSON BCI46/55 and dispatches via a topic map
BCI68/76 or a queued handler BCI142/150. This is an authenticated service
boundary with further vehicle-related handlers; no MQTT packet or vehicle
action was sent, and no arbitrary human input is promoted to an authorized
stock capability. The live broker/provisioning state remains unknown.

Native telnet also has a better boundary than mere configuration presence.
Recovered USB enum rules recognize vendor/product `2001:3c05` and
`0b95:7720` and start dlink.sh/cisco.sh. Their lines 5-9 first call
`test_service_flag network` and exit on failure. Then they set up en0 using
configured static address, DHCP or fallback 192.168.6.1, and start inetd at
line 69. `platform_troubleshoot.lua` fn2 `0x595-0x5bd` maps signed `Network=1`
to the network flag; the established verifier/serial/expiry checks remain in
force. Default false is not proof of the current live flag. `inetd.conf`
line 23 supplies telnetd and pf.conf lines 73-82 constrain loopback/en traffic.
The separate `diagserv` fn162 calls inetd at `0x23708` from a diagnostic
write handler; this is neither a read-only inspection procedure nor evidence
that the listener started at boot. No credentials were sought or used.

3proxy's config defaults to internal 127.0.0.1, port 3128, `auth iponly`, with
runtime include files for upstream/network/plugin settings. Boot starts
ConnMgr; its ROUTE_HISTORY rule inserts at startup and sends link-state events
to RouteHistoryCtrl.lua. That Lua's fn4 reads `/tmp/3proxy.pid` at `0xe06`,
falling back to the process name; fn5 updates route/DNS/parent files and reloads
an existing proxy. This is a reload predecessor, **not proof of construction**.
The initial launcher and actual include state remain UNKNOWN. The fixed
ProxyReloaded.lua config callback does not provide an arbitrary external
process-execution facility.

## 6. Targeted second pass and bounded negative results

All 19 selected archives were examined for URI/MIME/protocol and provider
registration, resource factories, IPC/event callbacks, Bluetooth/USB/media,
HTML/XML/help, configuration/content parsing, serialization, sockets, native
loading and process calls. The index records source-addressed candidates,
not a claim that every library method is production active.

- **URI/deep links:** no current Yelp incoming deep-link or custom-protocol
  registration was traced. Its URL sites construct outbound search/geocode
  requests. A URI object or a URL initializer is not a receiver.
- **Service providers and Help:** none of the selected JARs contains a
  `META-INF/services` resource or HTML document. The three XML resources are
  Maven `pom.xml` metadata; no selected Help Xlet exists. This says nothing
  about an unrecovered installed app or all shared-platform viewer code.
- **Factories:** Jeep/Viper GSkillsProjectFactory constructs a fixed module;
  current Yelp uses a numeric screen switch. Other reflection/JSON metadata
  sites are indexed, but no external class-name-to-execution chain is proved.
- **Configuration consumption:** matched resource-name literals are recorded
  with methods/BCIs, separately from proven consumption such as Yelp's
  properties load. Store, DRM and VSB configuration/service synchronization
  is not a read-only arbitrary input mechanism.
- **Serialization:** Yelp data populates fixed Place/UI objects. VSB broker
  JSON enters an authenticated service dispatcher; complete safe owner
  invocation is not established. No generic deserialization-to-code result.
- **Loopback/process/native:** selected KIM19 JARs contain no Runtime.exec or
  ProcessBuilder invocation. `http://localhost/` in bundled DPBaseRequest is
  an initial value, not a listener. L-Series LWUIT Affiner.loadLibrary BCI138
  calls System.load, but no external path-to-load flow is established. Shared
  Executor, simulator and factory wrappers retain the prior activation and
  authority boundaries; shared presence is not a human ingress path.

These negative findings are bounded to the explicitly scanned artifacts.
Absence in recovered KIM19 does not prove absence on the actual radio.
SocketCommandSource/invoke/runUnitTests were not re-pursued: there is no new
premise changing their exclusion from recovered production KIM selection.

## 7. Read-only next observation and completion answers

The most useful next observation is a human inspection of the existing
ordinary **Apps menu**, including its visible categories/pages. Record names
and icons. This follows the proven getAppList route and makes no installation,
security change, diagnostic write or account action. It only proves returned
visible entries; absence from the menu does not prove absence of files.

If Yelp is already listed, an optional second step is ordinary selection of
that tile, recording its splash/home UI or exact stock error, then returning
with normal navigation. Stop at the UI result; search, dialing, purchases,
account registration and vehicle actions are unnecessary. Normal app-owned
history/RMS behavior can occur on launch/exit. Merely inspecting the catalog
is the stricter read-only experiment.

Use an already accessible normal version screen to record the supplied
version tuple if desired. No newly invented hidden-menu entry sequence,
complete daemon/version export, telnet login or diagnostic-query procedure is
supported by this phase. A complete installed inventory would require an
already authorized, source-supported read-only interface or a pre-existing
capture; neither was identified here.

1. **Exact KIM:** KIM19 via proven 8+2 normalization and exact map row 74.
2. **Exact selected apps:** the nine rows in section 2, 37-file inventory,
   plus separately enumerated common base/native framework.
3. **Production activation:** ordinary Apps catalog/launch is stock code;
   individual app, daemon and network effects retain their explicit gates.
   No actual-radio activation measurement was made.
4. **Actual installed evidence:** supplied system identity/version observations,
   matching recovered build fields and a damaged historical update log;
   no current per-app inventory proof.
5. **Existing harmless capability:** view stock catalog; conditionally display
   existing Yelp UI through its authorized normal launcher. No new code needed.
6. **Highest-value uncertainty:** whether Yelp is visible/authorized on this
   exact unit, and what the normal tile selection displays. This is more
   informative and less invasive than testing unresolved service listeners.

## Reproduction and validation scope

`analysis_tools.target_production_index` uses the existing strict Java class
and Java-properties parsers. It never evaluates recovered Lua/Java, extracts
JAR payloads, or writes below a recovered input root. It fails on malformed
classes, duplicate member names, missing declared JAR/main class, links and
resource limits. Tests cover normalization/fallback, duplicate map semantics,
index determinism, no recovered writes, descriptor preservation, malformed
input and limits. Full inventory rebuild and manifest comparisons are separate
from those synthetic tests.

```powershell
& $researchPython -m analysis_tools.target_production_index `
  --root 'E:/Documents/GitHub/jeep_uconnect_custom/analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages/KIM19' `
  --output reports/target_production_state/package_inventory.json
& $researchPython -m unittest analysis_tools.tests.test_target_production_index
```

Run from the isolated research checkout with `$researchPython` bound to the
existing analysis Python interpreter. The phase uses no online availability
claims or radio execution tests. Static validation cannot substitute for the
explicit current-radio unknowns above.
