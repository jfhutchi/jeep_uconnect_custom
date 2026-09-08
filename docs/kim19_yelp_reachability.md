# Yelp launch and failure decision tree

**PROVED static chain; UNKNOWN current target state.** Scope is only the KIM19
Yelp JAR `640X480_84_Yelp_v03.00.33_FIT.jar`, app ID
`1D5347C0-8B5E-11E2-9E96-0800200C9A66`, main
`com.sprint.chrysler.yelp.xlet.YelpPOIXlet`, plus its production HMI/AMS path.
The tile name alone cannot verify that exact version on the real radio.

## Crossed boundaries

Every call/BCI in this table is **PROVED** in the recovered artifacts. A virtual
or callback edge remains conditional on its runtime receiver and scheduling.
Selected methods, descriptors and source/class hashes are in
[method evidence](../reports/kim19_runtime_analysis/method_evidence.json).

| Stage | Concrete evidence | Failure interpretation |
|---|---|---|
| Discovery/registration | KIM19 descriptor -> recovered installation/AMS completion -> AppManager installed record | UNKNOWN whether performed on this radio |
| Enumeration | Apps init/category getAppList; native visibility byte; MainSupplement Applet construction | Absence does not identify installation, filtering, freshness or category cause |
| Tap | Apps `onItem` ordinary branch calls `startXlet` at FWS `0xc1e6`; already-running branch can resume without new creation | A visible screen does not prove a fresh Xlet lifecycle |
| Native authorization | startApp dispatch file `0x53df0`; handler enables DRM at `0x50650`, calls findAndStartApp `0x5066c` | Missing app, unavailable AMS or failed authorization can prevent creation |
| AMS handoff | App::start call file `0x3c328`; AMS helper `0xf008`; main/key/payload identity association in prior report | Start request is not proof of completed init |
| `initXlet` | Registry BCI23, container52, setVisible60, Display.init64, bundled properties85/load101, platform140 | Container exception handler173 -> destroy208; other exception handler214 logs; exact continuation matters |
| `startXlet` | started guard9; constructs serial runnable20, schedules23, sets started flag28 | Scheduling/flag set alone is not visible UI |
| Serial runnable | ApplyTheme BCI2/5; language/RMS/platform work; splash constructor35/show38; Throwable catch44 | Splash proves more than merely receiving start |
| Splash completion | Worker starts at BCI10; worker location work54 and serial callback68; nested runnable chooses screen70/74 | Persistent splash does not prove waiting for internet |
| Home/search | GpScreenManager creates bundled current-location forms; keyboard/category handlers construct GpSearchRequest | UI is reachable before successful search response |
| Request worker | Keyboard constructor227/queue234/status244; category constructor126/status140; ConnectionManager Thread51/start89 | UI request/status path is concrete but asynchronous |
| Connectivity | BaseRequest.run -> establishConnectivity; emulator or existing `/fs/etfs/use_en0` shortcut; otherwise platform connectInternet BCI95, bounded retries | UNKNOWN chosen target interface, route, permissions or successful connectivity |
| HTTPS | BaseRequest.CallService constructs DefaultHttpClient32, executes53, gets status66; createRequest obtains request URL | TLS/HTTP exceptions can collapse into null response |
| Authentication | GpBaseRequest.addHeaders sets Authorization at BCI13 from a bundled Basic value | PROVED header construction; UNKNOWN credential validity/backend acceptance; value omitted |
| Response | GpBaseRequest creates JSONObject62, dispatches70; GpSearchRequest error branch30/71/78/83 or businesses146 | Parsed application error differs from generic local error |
| Result UI | Keyboard obtains result list401, selects screen443/456; error/zero/fallback branches are separate | Fresh relevant results support operation completion, not arbitrary inbound access |

**PROVED:** bundled search is
`https://vsb.cvp.extra.chrysler.com/yelp-api/v2/search`; bundled geocode is
`https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/find`.
GpGeoUtil loads packaged properties before using these values. **UNKNOWN:**
current endpoint availability and target routing. Neither endpoint was contacted.

**PROVED:** `CallService` catches Throwable at BCI123 and may return null at
BCI170/171. JSON processing has separate parsing/IO exception handling. Search
sets `ERROR` for an `error` object and reads its `id`; keyboard code also handles
`Zero_Results`, `OK` and fallback. **UNKNOWN:** an unqualified "application error"
photo does not identify which branch ran. Record exact text, title and timing.

**PROVED:** there is no Tweddle SocketCommandSource/CommandLooper class in this
exact Yelp JAR. Its resource ClassLoader calls do not load external executable
classes. The packaged permissive WebClientDevWrapper is not invoked by the
traced default-client search path. **UNKNOWN:** actual radio listeners; none was
observed or established by this static search chain.

## Voice input reaches the same search path

**PROVED:** Yelp accepts recognized speech through a stock platform callback,
in addition to its touchscreen keyboard/category controls. The current-location
form constructs `SpeechListener` at BCI54 and enables `VRHelper` at BCI57.
The exact `VRHelper.isEnabled()` implementation returns true. This feature
switch does not guarantee a working voice implementation: `VRHelperImp.init`
obtains the supported-service array, uses its first service, sets credentials
when that service implements `SecureService`, obtains a session and registers
its speech listener (BCI51/56/246/305/331). Exceptions in the service setup are
caught at BCI339 and clear its enabled field at BCI367. A null/empty supported
service array is not a successfully initialized voice service.

**PROVED:** after `init`, the helper constructor checks `enabled` and starts
the background loop at BCI41 only if enabled. `startBackgroundLoop` constructs
and starts the worker Thread at BCI11/21; `VRHelperImp$4.run` calls
`VRQueue.run` at BCI24. This supplies the event-consumer lifecycle, rather than
assuming that queue insertion alone processes a voice request.

**PROVED:** the home voice action checks location validity before starting its
worker. That worker calls `requestOffBoardVr`; the helper queues a
`VRSoftButtonEvent`. `VRQueue.run` dispatches events via `accept` at BCI49;
the soft-button event invokes its handler at BCI2. The corresponding
`VRSessionLogic.handle` requests a platform VR session at BCI31. Requested or
waiting-state handlers can call `startOffboardSession`, which invokes
`Session.startSession` at BCI13. Current session state, scheduling and platform
service availability remain gates, not inferred successes.

**PROVED:** `offboardcommandRecognized(String)` compares the localized cancel
command at BCI37/40. A cancel calls `cancel(true)` at BCI53. Otherwise, with a
current action, it schedules `VRHelperImp$1` on the UI thread at BCI75/78.
That runnable calls `VRAction.onVRAction(String)` at BCI21. The installed
`SpeechListener` uses the recognized text to construct `GpSearchRequest` at
BCI58, queues it at BCI63, checks status at BCI73, and handles error, zero
results and result-screen transitions at BCI148/173/198/242/254.

**INFERRED:** ordinary speech can therefore supply a search term to the same
signed HTTPS/results behavior if these runtime gates succeed. **UNKNOWN:**
microphone/platform routing, current voice-service credentials, remote speech
availability and successful search on this radio. This is not evidence for
arbitrary Bluetooth/phone bytes, a user-accessible command socket or downloaded
executable content. A visible voice control alone does not prove recognition.

**TARGET OBSERVATION REQUIRED:** a previously observed recognized query followed
by relevant results would support both the voice callback and search chains.
The first operator observation remains the single ordinary launch described
below; voice search would add account/network/history state and is not added to
that first observation.

## Observation cases

The earlier six-case sketch is replaced by the deterministic A-H contract in
[Yelp target observation analysis](yelp_target_observation_analysis.md): absent
from all pages, disabled, immediate exit, error, registration/subscription,
normal home/search, explicitly fully functional, and unexpected/partial.
**PROVED:** this correction separates disabled rendering from post-selection
exit, and separates stable local UI from an explicitly observed successful
result flow. It does not alter recovered behavior or any of the original eight
generated runtime reports.

**INFERRED:** a stable home is a substantial improvement over a tile; an
explicitly documented relevant-result flow is the strongest ordinary evidence
for usable outbound stock-signed capability. **UNKNOWN:** no case establishes an
external-network-input-to-harmless-effect route available to an arbitrary phone
or computer. A response channel to a stock client is not an inbound command
server.

**TARGET OBSERVATION REQUIRED:** the highest-value next action is one normal
Yelp launch, if present after catalog recording. Record its first screen, exact
error, splash duration and whether it stays visible/running. Do not add a search,
registration, call or repeated launch to that first observation. If a search has
already been performed in ordinary use, classify it with the A-H analyzer
without repeating it solely for this report. Launch/history/RMS preferences may
change.

See [operator checklist](target_observation_checklist.md) and
[the generated failure signatures](../reports/kim19_runtime_analysis/yelp_failure_signatures.json).
