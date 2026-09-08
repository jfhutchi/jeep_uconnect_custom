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

## Observation cases

These are conditional interpretations of future observations. **TARGET
OBSERVATION REQUIRED:** no case has yet been observed on the radio in this phase.

| Case | PROVED by the observation itself | INFERRED crossed boundary | UNKNOWN / next uncertain gate |
|---|---|---|---|
| A: absent | No Yelp entry in the views actually surveyed | Only after all pages/categories are recorded: no exposed Yelp entry at that moment | Installed state, registration, cached visibility flags, category freshness and entitlement; do not infer uninstall |
| B: present, cannot launch | Entry exists and attempted launch/resume failed visibly | Catalog exposure succeeded | Native start/AMS/init/foreground failure; does not isolate DRM |
| C: splash | Yelp-branded application UI executed | On a matching fresh-start chain, container/Display, serial init and splash creation succeeded | Exact binary, resumed versus new lifecycle, delayed home work, network and backend |
| D: home/search, search fails | Search UI accepted the action and displayed failure | Home initialization completed sufficiently for that action | Connection/DNS/TLS/HTTP/account/parse cause; generic failure cannot distinguish them |
| E: backend/application error | Exact error was displayed | If it is response-specific `error.id` behavior, response receipt/JSON processing is supported | A generic local error proves no network traffic; backend identity and authorization success unresolved |
| F: results | Result UI displayed data | Fresh query-dependent relevant results strongly support request/response/parse/display completion | Exact target JAR, arbitrary external input route, listener, future availability |

**INFERRED:** C is a substantial improvement over a tile; F is the strongest
ordinary evidence for usable outbound stock-signed capability. **UNKNOWN:** no
case establishes an external-network-input-to-harmless-effect route available to
an arbitrary phone or computer. A response channel to a stock client is not an
inbound command server.

**TARGET OBSERVATION REQUIRED:** the highest-value next action is one normal
Yelp launch, if present after catalog recording. Record its first screen, exact
error, splash duration and whether it stays visible/running. Do not add a search,
registration, call or repeated launch to that first observation. If a search has
already been performed in ordinary use, classify its result using D/E/F without
repeating it solely for this report. Launch/history/RMS preferences may change.

See [operator checklist](target_observation_checklist.md) and
[machine-readable cases](../reports/kim19_runtime_analysis/yelp_reachability.json).
