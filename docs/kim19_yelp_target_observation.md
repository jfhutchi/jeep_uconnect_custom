# KIM19 Yelp target observation decision tree

This protocol is deliberately read-only with respect to the target: do not
install, provision, register, subscribe, search, speak, call, navigate, export,
or change configuration. Record the complete Apps pages, then make at most one
ordinary Yelp tap if an enabled Yelp tile already exists. Photograph/video the
first and stable screen, exact wording, timing, whether another app opens, and
whether the display returns/restarts.

## Decision tree

| Observation | What it supports/falsifies | What remains unresolved |
|---|---|---|
| Yelp absent | Supports current catalog/registration gate not passing; falsifies “currently visible” | Installed bytes, hidden registration cause, grants, all later gates |
| Yelp present but disabled | Supports catalog entry with a blocking state | Exact entitlement/DRM/policy cause, lifecycle |
| Tap has no visible effect | Supports selection or launch failure | Whether HMI dispatched, DRM rejected, lifecycle ran invisibly |
| Immediate return to Apps | Supports launch/startup exception or destruction | Exact exception and whether init/start was entered |
| Splash/loading appears | Proves catalog selection, launch authorization sufficient for visible Yelp UI, lifecycle, display, local setup, and splash | Location callback, home/VR, connectivity/backend |
| Splash remains/blank UI | Supports splash worker/location/home-constructor failure | Exact exception and backend (no search request is proved) |
| Registration/subscription message | Proves some stock flow rendered it; supports a current service gate | Which component rendered it, backend reachability, Yelp home |
| Network/service error before home | Supports an added platform/service check or startup failure | DNS/TLS/backend cause; recovered Yelp has no required search HTTP before home, so capture exact text/app identity |
| Search/category/voice home appears | Proves the complete pre-backend chain through `GpCurrentLocationScreen.layoutForm` | Search connectivity, authorization/backend/schema, voice recognition |
| Crash/restart | Supports an uncaught failure after tap | Exact class/cause and whether radio watchdog acted |
| Another application opens | Falsifies the assumption that the observed tile/tap resolved to recovered Yelp identity | Actual catalog mapping and app identity |
| Local dialog | Match exact text against GPS/VR/phone/navigation/generic resources | Trigger cause unless the corresponding action was taken (none should be in this protocol) |

## Evidence discipline

An Apps photograph proves visible labels/icons, not binary identity. A splash
proves visible Yelp lifecycle progress, not backend operation. The home proves
the local pre-backend UI, not network acceptance. No response during the
observation is not proof of a dead endpoint. Preserve contradictions such as a
brief splash followed by return instead of collapsing them into one outcome.

If and only if the first observation reaches a stable Yelp home, stop. A later
search or voice experiment would be a separate, explicitly authorized action
because it sends location and user/recognized text to external services and may
mutate local search/RMS history.

The static branches used to interpret the record are in
[launch graph](kim19_yelp_launch_graph.md), [runtime gates](kim19_yelp_runtime_gates.md),
and [failure states](kim19_yelp_failure_states.md).
