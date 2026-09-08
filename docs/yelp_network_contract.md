# Yelp network contract

**PROVED static scope:** this contract describes the recovered Yelp 03.00.33
JAR. It does not contact either endpoint and does not assert that either service
still exists. Sensitive header values are deliberately omitted; their presence,
source, and use are recorded without reproducing credentials.

## Request construction

| Value | Provenance | Recovered use | Runtime limit |
|---|---|---|---|
| Search base URL | packaged `yelp.properties`, key `places_api_base` | `https://vsb.cvp.extra.chrysler.com/yelp-api/v2/search` | **UNKNOWN:** live DNS, route, certificate, service, or backend behavior |
| Geocode base URL | packaged `yelppoconf.properties`, key `geocode_api_base` | `https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/find` | **UNKNOWN:** whether a given action takes the address-geocode path |
| Search term | touch keyboard/category or recognized VR text | `GpSearchRequest` chooses location text or latitude/longitude construction | **TARGET OBSERVATION REQUIRED:** which path a recorded action used |
| Position/location | platform location state, address input, or packaged fake-GPS development values | request query and local distance calculation | **PROVED:** `usefakegps=false` in the packaged production configuration; target location validity unknown |
| Locale | platform/resource locale | localized display and units; three bundled language resources | no catalog-time region restriction is established |
| User-Agent | static `GpBaseRequest` field/value | `addHeaders` calls `HttpRequestBase.setHeader` at BCI5 | value is client metadata, not proof of accepted authentication |
| Authorization | static bundled Yelp class field/value | `addHeaders` sets `Authorization` at BCI13; scheme is Basic | credential bytes are omitted; **UNKNOWN:** validity, identity, revocation, or backend acceptance |
| Google API key | packaged Yelp message resource | statically present and usable by a geocode-related path | value is omitted; presence does not prove a live call or authorization |

**PROVED:** `GpSearchRequest.getURL` tokenizes location input and selects
`searchByLocation` or `searchByLatLon`. Its superclass request path constructs an
HTTP request from that URL. `GpBaseRequest.addHeaders` sets only the recovered
User-Agent and Authorization headers in its own method. **UNKNOWN:** additional
headers inserted by `DefaultHttpClient` or the platform stack at runtime.

## Connectivity and transport

**PROVED:** common `BaseRequest.run` calls `establishConnectivity`. The latter
accepts emulator or existing `/fs/etfs/use_en0` conditions, otherwise calls the
platform Internet connection service and performs bounded status retries.
**UNKNOWN:** the target-selected interface, carrier/hotspot route, permissions,
DNS, or result. The security policy grants network interface permission for
`ppp0`; a declared permission is not proof of a connected interface.

**PROVED:** `BaseRequest.CallService` creates `DefaultHttpClient`, creates the
request, invokes Yelp's header hook, executes it, and obtains the HTTP status.
The URLs use HTTPS. A catch-all Throwable path can return null, after which UI
code can collapse the cause into a generic request-failed dialog. The packaged
`WebClientDevWrapper` is not called by this traced path. **PROVED:** no active
permissive TLS/certificate-bypass edge is established for ordinary Yelp search.

**PROVED:** the recovered connectivity loop is bounded; it is not an unlimited
retry loop. **UNKNOWN:** no Yelp-specific connect/read timeout setter or HTTP
retry handler is established in the selected production request path. Library
defaults and platform service timing therefore remain unknown. Repeating an
ordinary target action is not needed to resolve those static omissions.

## Response contract

`GpBaseRequest.processStream` reads the response by line, builds one string,
constructs `org.json.me.JSONObject` at BCI62, and calls the request-specific
`processJSONObject` at BCI70. **PROVED:** JSON, IO, and general exception paths
are handled separately inside stream processing, but the outer request path can
still expose only a generic failure to the caller.

`GpSearchRequest.processJSONObject` implements these branches:

| Response shape | Recovered state/effect | Observation meaning |
|---|---|---|
| top-level `error` | reads error text/object and `error.id`; sets `ERROR` | exact response-specific text after a search **INFERRED** to support response receipt and parsing |
| missing/empty business result | sets `Zero_Results` | a zero-result screen supports handled completion only when tied to the recorded action |
| `businesses` array | sets `OK`; builds `Place` objects | relevant result UI **INFERRED** to support request, response, parse, and display completion |
| null/exception/fallback | caller can show `BaseRequestFailedAlertDialog` | generic error cannot identify transport or backend layer |

**PROVED:** parsed business fields include name, rating, review count, optional
phone, price level, periods, distance, address/city/country/state/street,
reference, categories, display address, and coordinates. This is stock data
display. It is not executable content or an inbound command channel.

## Error collapse and interpretation

**PROVED:** keyboard, category, and VR search handlers distinguish `ERROR`,
`Zero_Results`, `OK`, and fallback status. They can show an application-error
`AlertDialog`, dedicated zero-results UI, results, or
`BaseRequestFailedAlertDialog`. Exact caller/BCI and localized match strings are
in [the generated failure signatures](../reports/kim19_runtime_analysis/yelp_failure_signatures.json).

**INFERRED:** an exact `INVALID_SIGNATURE`, credential, account, quota, or
location error after a recorded search is stronger evidence of response parsing
than the generic service/communication dialog. **UNKNOWN:** a packaged string
can also be selected by local logic, and a photograph without its preceding
action cannot prove network traffic. The analyzer therefore reports matches and
remaining unknowns separately.

## External-value classification

| Category | Values |
|---|---|
| **PROVED packaged constants** | two base URLs, User-Agent, Basic Authorization value, API key, JSON field names, localized errors, fake-GPS flag/defaults |
| **PROVED local/platform inputs** | typed/category/recognized query, location, language, network-service state |
| **PROVED response-derived values** | error identifiers and business/result fields after JSON parsing |
| **UNKNOWN runtime state** | current credentials, subscriber/account relation, endpoint certificates, routing, HTTP status, backend policy, rate limits |
| **TARGET OBSERVATION REQUIRED** | exact stable screen/error and the ordinary action that immediately preceded it |

No endpoint probe, credential test, authentication attempt, packet capture, or
radio connection was used to produce this contract.
