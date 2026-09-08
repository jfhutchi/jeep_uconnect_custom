# KIM19 Yelp stock handoffs

The machine-readable receiver ledger is
[stock_handoffs.json](../reports/kim19_yelp/stock_handoffs.json).

## Phone: both recovered ends

**PROVED sender:** `GpDetailsScreen.processDial` first checks
`HuCommon.isXletPaused`; when not paused it passes the parsed `Phone` string to
`kona.phone.Phone.dial(String)` at BCI 33. Any `Exception` produces the localized
phone-not-available dialog.

**PROVED platform receiver:** `PhoneManager` reflectively selects
`com.harman.phone.PhoneImpl`. Its one-argument dial delegates to its two-argument
overload. `PhoneImpl` checks `PhonePermission("dial")`, calls
`BluetoothService.dial(number)`, compares the result with `CALL_SUCCESS`, and
maps DBus failures/non-success to `PhoneException`. This closes the recovered
Java sender/interface/implementation/service path. Actual pairing, permission,
resident Bluetooth state, and call completion are **TARGET OBSERVATION REQUIRED**.

## Navigation: both recovered ends

**PROVED sender:** the detail action obtains `Navigation.getNavigation`. With
nonzero result coordinates it creates `Geocode(double,double)` and sets street,
name, city, state, and country. With zero coordinates it calls the geocoder,
builds a Geocode from its returned doubles, and attaches address fields. It then
calls `routeToLocation(Geocode)` at BCI 589. The returned boolean is popped.

**PROVED platform receiver:** `Navigation.getNavigation` reflectively selects
`com.harman.navigation.NavigationImpl`, falling back to a base implementation
whose operations throw “not supported.” `NavigationImpl.routeToLocation` rejects
NaN coordinates, checks `OpenNavActivation.isNavActivated`, converts the Geocode
with `NavUtils.geocodeToNavEis`, and calls
`HMIGatewayService.routeToLocation(String)`. OpenNav and service exceptions are
mapped to `NavigationException`, which Yelp renders as a localized dialog.

The receiver evidence is from recovered
`secondary_iso/usr/share/XLETS/base/kona/lib/kona.jar`, SHA-256
`19390472018f02d998690b982f00eb68da5d40d7a8d6fba91499677651015f92`.
Resident native/HMI completion is still **TARGET OBSERVATION REQUIRED**.

## Other handoffs and scoped negatives

- **PROVED:** Apps -> native AppManager/DRM -> AMS -> Xlet lifecycle.
- **PROVED:** `IxcRegistry` is acquired, but Yelp performs no bind/lookup call.
- **PROVED:** kona location supplies search coordinates and destination data.
- **PROVED:** kona speech VR supplies session/state/recognized-string callbacks.
- **PROVED:** YelpGeocodeRequest is a direct HTTPS fallback, not an app launch.
- **PROVED scoped negative:** Yelp has no VSB/SDP client calls. “vsb” in the
  search hostname is not a VSB broker/API edge.
- **PROVED scoped negative:** Yelp contains no SocketCommandSource,
  CommandLooper, command socket, IXC command receiver, browser/WebView, or media
  handoff. Compared with the separate SocketCommandSource surface, it shares
  KIM19/AMS and kona libraries, not the command transport or dispatcher.
