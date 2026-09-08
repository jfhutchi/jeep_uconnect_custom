# KIM19 communication and extension capabilities

**PROVED static evidence:** KIM19 contains concrete outbound client, platform
messaging and local IPC paths. **UNKNOWN:** no arbitrary external-input route,
running listener or live target/backend availability is established. This report
does not turn service names, classes or credentials into a probe procedure.

## Scope and reproducibility

**PROVED:** [network_capabilities.json](../reports/kim19_runtime_analysis/network_capabilities.json)
scans all 19 selected JARs, including key/support archives. It records separate
invocation and class-reference counts, transport construction sites, syntactic
callers, native declarations and selected configuration values. The existing
indexer validates the complete baseline before this extraction; no archive is
loaded as executable code. Relevant common-base interpretation remains bounded
to previously traced framework/loading/service paths and its 24-file manifest.

**PROVED:** zero matched KIM19 invocation sites were found for ServerSocket,
DatagramSocket, MulticastSocket, the HTTP-server heuristic, script engines and
Runtime/ProcessBuilder process launch. **UNKNOWN:** these are scoped negative
results, not proof that platform-native services or the radio have no listeners.
The count classifier is a documented candidate heuristic; its "HTTP client"
bucket includes broad HTTP references, not resolved transport execution.

**PROVED:** selected `java.net` invocation counts are Yelp 3, Store 6, VSBClient
13; all others zero. "Socket" counts include socket-factory calls: Yelp 4,
DRMSync 2, ASSIST 2, Store 9, Register 2, VSBClient 13. Such a count is not a
socket constructor or an activated path. **PROVED:** only L-Series declares
native methods in these JARs (three declarations) and has one System.load call.
Other apps can still invoke native-backed common-base services.

## Construction, activation and input effects

Each construction below is **PROVED** syntactically; end-to-end activation is
conditional. The full candidate matrix includes address derivation, direction,
authentication, input, effect and external-origin limits for each candidate.

| Candidate | Concrete predecessor and lifecycle | Direction / input / effect | Authorization and reachability limit |
|---|---|---|---|
| Yelp search/geocode | Ordinary launch -> home -> keyboard/category request -> ConnectionManager -> BaseRequest HTTP execute | Outbound request, inbound response; terms/location become a request; JSON becomes business/error UI | Bundled Basic header plus TLS; valid backend acceptance UNKNOWN; no inbound command listener |
| Store discovery/vault | Loading-screen completion -> MTSDiscoveryRequest; updateBundles/updateVault queue later requests | Outbound HTTP(S), catalog/account/vault responses alter stock screens | MTS auth/account state and native launch gates; presence alone proves no account |
| Register subscriber state | Init-stage check -> HURLoadingScreen -> MTSSubscriberStateRequest | Outbound subscriber request; JSON/RMS controls registration flow/error display | Cached state and live service differ; no Bluetooth listener established by ViaMobile metadata |
| VSB MQTT | init -> t/s/c -> t/b/b Runnable -> d/f/g -> t/b/a.c -> Paho connect | Client-created connection receives broker JSON callbacks; handlers queue stock work | TLS factory, configured identity and MQTT credentials; arbitrary nearby publisher authority UNKNOWN |
| VSB WMA messages | t/s/c constructs t/b/d -> Connector.open -> worker/listeners | Platform wireless messages wake processing and queue work | Not TCP; sender/payload acceptance and arbitrary-sender access unresolved |
| VSB/DRM/ASSIST IXC | Service bind, locator lookup, callback registration and dispatcher | Local stock-app calls and notifications can update app/registration/service state | AMS/IXC identity/permissions and running services required; registry names are not IP endpoints |
| Phone/VR/location/sensors | Yelp listeners, ASSIST local services, Performance module initialization | Platform events influence existing screen/location/phone state | Platform events are not arbitrary phone commands; actual service grants UNKNOWN |

**PROVED:** VSB's Paho `TCPNetworkModule.start` calls the socket factory and
`Socket.connect` (BCI83/102). Its callback is attached in the configured client
builder. `t/b/b.messageArrived` parses JSON (BCI46/55), looks up a handler
(BCI68), dispatches a typed handler (BCI76) or queues generic JSON work
(BCI142/150). **UNKNOWN:** which subscribed messages are permitted by current
credentials or can be supplied by any proposed external party. This is an
existing authenticated service path, not a demonstrated open command channel.

**PROVED:** VSB `t/b/d` constructs two WMA connections using bundled SMS-port
URIs, starts `t/b/e` and sets listeners (BCI50/71/93/118/126/136).
`notifyIncomingMessage` wakes worker state and queues a Runnable (BCI22/41/57).
**UNKNOWN:** actual modem/WMA activation, inbound sender validation and a unique
harmless UI consequence. No messages were sent to the target.

**PROVED:** Store contains `AllCertSSLSocketFactory` socket methods, but its
traced common `BaseRequest.CallService` creates `DefaultHttpClient` directly.
**UNKNOWN:** no production activation edge from this request path to that
permissive factory was established; do not claim active certificate bypass.
The same distinction applies to Yelp's uncalled WebClientDevWrapper.

## Recovered endpoint settings

All values below are **PROVED bundled configuration**, with member hashes in
the JSON report. **UNKNOWN:** current target configuration, credentials,
successful connection and service availability. Development URLs in comments
are not treated as active endpoints. No endpoint was contacted.

| Owner/resource | Key or role | Bundled value |
|---|---|---|
| Yelp properties | Search | `https://vsb.cvp.extra.chrysler.com/yelp-api/v2/search` |
| Yelp properties | Geocode | `https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/find` |
| VSBClient/vsbconf.properties | BROKER_URL | `ssl://vsb.cvp.extra.chrysler.com:8443` |
| Store/Register/DRMSync mts.properties | mts-server | `https://mts.cvp.extra.chrysler.com:8443/mts-api` |
| Store/wallet.properties | smps-url | `https://max.ccdc02.com/smpsmrc/Service.svc/` |

**PROVED:** Store's VehicleConfig can override its MTS base address. VSB startup
initializes its configuration/identity subsystems before configuring Paho;
connect options set an SSL factory and username/password. **UNKNOWN:** a
packaged wallet URL alone does not establish its active payment path. Credential
values, private payloads and signing material are not reproduced.

## External-origin distinctions

| Origin | PROVED recovered mechanism | UNKNOWN boundary |
|---|---|---|
| Another stock app | VSB IXC service, DRM notification listeners, ASSIST locator | Current registry bindings, permissions and service liveness |
| Remote backend | HTTP responses and MQTT callbacks, conditional on successful client connection | Current authentication, routing, broker policy and backend health |
| Phone/Bluetooth | Platform phone state/listeners; ViaMobile metadata references | Arbitrary phone bytes reaching an app-owned parser or command handler |
| Wi-Fi/hotspot | App calls platform connectivity; network client can operate on an authorized route | Which interface/route is selected; hotspot isolation and reachability |
| USB | No selected USB-content-to-code path established | Platform USB functions do not establish app input or execution |
| Loopback/local transport | Paho LocalNetworkModule and local IPC candidates exist | No activated localhost TCP server inferred from "local" or IXC |
| JNI/native bridge | L-Series native declarations; native-backed platform APIs | Exported remote entry, input control and runtime activation |

## Extension classification

| Mechanism | Classification and evidence | Conclusion |
|---|---|---|
| ClassLoader resource reads | PROVED packaged properties/resources, including Yelp configuration | Configuration/content use; no external class definition |
| Reflection in collections | PROVED typed array allocation in backport libraries | Ordinary static library behavior |
| Class.forName / named implementations | PROVED Utils/Paho library selectors; MessageCatalog chooses message implementation | Library/factory selection; external executable origin UNKNOWN |
| Paho LocalNetworkModule | PROVED reflective local-transport class lookup | Configuration route and production activation UNKNOWN |
| XML/provider resources | PROVED prior complete inventory distinguishes metadata/resource names from handlers | No external XML-to-executable handler chain established |
| Store Base64 helper | PROVED object/class-resolution helper exists | External input reaching it UNKNOWN; not a proved extension interface |
| L-Series Affiner | PROVED System.load at BCI138 and native declarations | Loading primitive; caller activation and external path control UNKNOWN |
| Common base | PROVED connector/factory/resource and AMS class-loading infrastructure | Signed identity/permission boundaries still apply |
| Backend JSON/catalog/resource data | PROVED parsing into existing stock objects/UI where traced | Content/configuration influence, not demonstrated executable-code extension |

**UNKNOWN:** no complete externally supplied content -> executable code route
was established. No scripting-engine invocation, new resident app installation
or arbitrary code-loading route is claimed. See the source-bound common-base
analysis in [stock signed capabilities](stock_signed_capability_analysis.md) and
[AMS association](../reports/keyjar_runtime_association.md).
