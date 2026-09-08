# KIM19 Yelp network contract

No endpoint was contacted. This is a static contract from the recovered
descriptor, resources, and bytecode. Canonical fields are in
[network_fields.json](../reports/kim19_yelp/network_fields.json).

## Search request

| Item | Recovered value/control | Classification |
|---|---|---|
| Method | GET, application-controlled | **PROVED** |
| Base URL | `https://vsb.cvp.extra.chrysler.com/yelp-api/v2/search` | **PROVED** |
| `term` | user/recognized speech; transformations described in the input dataflow | **PROVED** |
| `ll` | platform latitude,longitude in ordinary mode | **PROVED** |
| `location` | right side of localized near/in grammar | **PROVED** |
| `sort` | literal `0` on recovered touch/voice paths | **PROVED** |
| Headers | Content-Type `text/plain`; Accept `application/json`; Connection `close`; User-Agent `TU` | **PROVED** |
| Authorization | fixed application value; omitted, SHA-256 `f123350ba1b7473a5e933cfcd84c5d32f91858823962de28239f845339c43013` | **PROVED**, redacted |

`GpSearchRequest.getURL` globally removes apostrophes, lower-cases a copy only
for near/in detection, and otherwise preserves case in the encoded `term`.
Ordinary mode calls `LocationInfo` and appends `ll`. Near/in mode does not add
`ll`; it adds encoded `location`. An `UnsupportedEncodingException` is printed,
but UTF-8 support is expected from the runtime; the partial-URL behavior after
that exceptional branch is **PROVED** code and not a claim that it occurs.

## Geocode fallback

When a selected result has zero coordinates, the details navigation action
constructs `YelpGeocodeRequest` using the displayed address. It calls:

`https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/find?text=<address>&f=pjson`

**PROVED:** the first comma is removed by concatenating the portions, newline
becomes space, and space becomes `+`; other characters are not generally
percent-encoded. The parser iterates `locations`, assigning `extent.ymax` to
latitude and `extent.xmax` to longitude, so the last entry wins.

## Transport and parsing

**PROVED:** common `BaseRequest` tries platform connectivity up to three times,
sleeping 30 ms after each failure. It constructs `DefaultHttpClient`, applies
30,000 ms connect and socket-read timeouts, creates an `HttpGet`, sets headers,
executes, stores HTTP status, and closes idle connections. No application-level
search retry follows HTTP/TLS failure.

**PROVED:** the response entity is read as characters, joined with newlines,
and parsed by `org.json.me.JSONObject`. A malformed body prints/logs an error;
there is no alternate HTML or active-content parser. The common layer regards
2xx as successful, but can still inspect/log an erroneous response body.

**UNKNOWN:** exact DNS configuration, proxy, TLS versions/ciphers, SNI, trust
store, certificate validity, and server behavior. Current endpoint reachability,
authorization acceptance, subscription state, and schema are **TARGET
OBSERVATION REQUIRED**.
