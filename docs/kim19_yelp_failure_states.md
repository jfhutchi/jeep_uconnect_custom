# KIM19 Yelp failure states

The canonical layer-separated paths are in
[failure_paths.json](../reports/kim19_yelp/failure_paths.json).

| Layer | Failure | Caller-visible state | Classification |
|---|---|---|---|
| Catalog | absent/unregistered/hidden/not entitled | no enabled Yelp tile | **TARGET OBSERVATION REQUIRED** |
| Launch | DRM/policy/AppManager/AMS rejection | no lifecycle; exact HMI response target-dependent | **TARGET OBSERVATION REQUIRED** |
| Init | unavailable container | logs and calls `destroyXlet(true)` | **PROVED** |
| Init | generic property read exception | logs but method continues/returns | **PROVED** |
| Local setup | theme/RMS/resource/startup throwable | log only; no fallback screen | **PROVED** |
| Splash | image I/O | sparse splash can be built | **PROVED** |
| Splash/location | worker unchecked failure | callback not scheduled; post-state **UNKNOWN** | **PROVED** branch |
| Input | invalid GPS | GPS alert, Yelp remains, no request | **PROVED** |
| Input | lockout | no keyboard or speed-lockout screen | **PROVED** |
| Input | empty/hint/duplicate | ignored/disposed, no new request | **PROVED** |
| Connectivity | null service/three failures | response -1, null response processing | **PROVED** |
| Transport | DNS/TCP/TLS/client throwable | null response; cause collapsed | **PROVED** |
| HTTP/body | non-JSON or malformed JSON | printed/logged; request status may remain empty | **PROVED** |
| JSON | `error` object | service-unavailable dialog | **PROVED** |
| JSON | `total == "0"` | no-results screen | **PROVED** |
| JSON | missing required business field | parser abort path; later UI depends on resulting empty status | **PROVED** / post-state **UNKNOWN** |
| Voice | missing/failed service/session | helper can disable VR or report generic VR error | **PROVED** code; live trigger **TARGET OBSERVATION REQUIRED** |
| Phone | receiver/permission/DBus failure | phone-not-available dialog | **PROVED** |
| Navigation | zero coords + failed geocode | navigation-error dialog | **PROVED** |
| Navigation | not activated or receiver exception | activated/unknown navigation dialog | **PROVED** |

There is no distinct Yelp UI for DNS versus certificate versus TCP failure:
`CallService` catches `Throwable` and returns null. Likewise, there is no
application search retry after a completed failed HTTP attempt; the only
three-attempt loop is connectivity establishment. These distinctions prevent
over-reading a generic service dialog.

**TARGET OBSERVATION REQUIRED:** current registration/subscription screens,
backend acceptance, certificate validity, speech service, phone pairing, and
OpenNav activation. A target photograph can classify the visible branch but
cannot prove the exact installed binary or hidden transport cause.

