# Yelp target observation analysis

This framework maps one ordinary physical observation to bounded conclusions.
**PROVED:** the classifier performs local JSON validation and deterministic
string matching only. **UNKNOWN:** current target state until an observation is
supplied. **TARGET OBSERVATION REQUIRED:** do not fill unobserved fields with
assumptions; use `not_observed`, `not_attempted`, or `unknown`.

## Input contract

```json
{
  "catalog_scope": "all_pages",
  "tile_state": "enabled",
  "launch_state": "home",
  "search_state": "not_observed",
  "functionality": "not_observed",
  "screen_text": "optional exact visible title and body"
}
```

Allowed values are:

| Field | Values |
|---|---|
| `catalog_scope` | `all_pages`, `partial`, `unknown` |
| `tile_state` | `absent`, `disabled`, `enabled`, `unknown` |
| `launch_state` | `not_attempted`, `immediate_exit`, `error`, `registration`, `home`, `unexpected` |
| `search_state` | `not_observed`, `failed`, `results` |
| `functionality` | `not_observed`, `home_or_search`, `fully_functional` |
| `screen_text` | optional string copied from the stable screen |

The physical-record fields below are also accepted. Boolean fields may be
`true`, `false`, or `null` when explicitly unknown.

| Detail field | Type and use |
|---|---|
| `yelp_present` | boolean/null; cross-checked with `tile_state` |
| `launch_attempted` | boolean/null; permits classification from the raw record when `launch_state` is omitted |
| `splash_seen` | boolean/null; preserved as lifecycle evidence without implying home or backend success |
| `first_screen_text` | string; combined with error text for signature matching |
| `error_text` | string; a nonempty value after a launch attempt derives outcome D unless registration is explicit |
| `remained_open` | boolean/null; true supports F when no narrower state is supplied |
| `returned_to_apps` | boolean/null; true after a launch derives C unless an error/registration state is explicit |
| `registration_prompt` | boolean/null; true derives E |
| `approx_transition_seconds` | nonnegative number; preserved without threshold-based inference |
| `notes` | string; preserved for context and never used to promote an outcome |

The tool rejects unknown fields, invalid values, contradictory presence/launch/
return fields, launching an absent/disabled tile, search observations without a
home/search launch state, and a `fully_functional` claim without observed
results.

```powershell
python tools/analyze_yelp_observation.py observation.json
Get-Content observation.json | python tools/analyze_yelp_observation.py
```

Output contains the A-H outcome, matched packaged failure signatures,
established facts, supported inferences, incompatible and compatible
hypotheses, remaining unknowns, one next static question, and one benign next
observation. Output keys and ordering are canonical and repeatable.

## Outcome matrix

| Outcome | What the observation proves | What it supports | What it does not establish | Relevant gates/evidence | Next static question | Next benign observation |
|---|---|---|---|---|---|---|
| A: absent from all pages | **PROVED observation:** no Yelp entry appeared in every catalog page explicitly surveyed | **INFERRED:** Yelp was not exposed by those views at that time | **UNKNOWN:** uninstall, package absence, specific native predicate, DRM, region, subscription | registration/object map -> category -> `!headless && (!daemon || hasGUI) && showInHmi` | Compare Yelp descriptor defaults with each catalog predicate and persistence field | **TARGET OBSERVATION REQUIRED:** preserve one complete Apps/Favorites/Running page sequence without changing settings |
| B: disabled/grey | **PROVED observation:** Yelp rendered but ordinary selection was disabled | **INFERRED:** identity enumeration and rendering crossed more gates than A | **UNKNOWN:** the disabling component, start authorization, network, account | catalog success -> HMI enabled/status state; launch not yet crossed | Trace HMI Applet enabled/status properties from `getAppList` | Record exact styling and adjacent status text without repeated taps |
| C: launches/exits | **PROVED observation:** an enabled Yelp entry accepted launch and returned/vanished | **INFERRED:** catalog and part of start/resume ran | **UNKNOWN:** fresh versus resume, native/AMS/init cause, network attempt | HMI start -> DRM/resource gate -> AMS -> `initXlet`; container exception can call `destroyXlet(true)` | Correlate splash/timing with recovered exit sites | Record splash presence and elapsed time to the prior screen on the ordinary attempt |
| D: error | **PROVED observation:** exact recorded error text appeared after the recorded action | **INFERRED:** any matched packaged error path became visible | **UNKNOWN:** network traffic for generic/local errors; transport/backend root cause | local GPS/action gates; request status ERROR/zero/fallback; generated failure signatures | Inspect only the exact resource caller and status branch | Record title, body, preceding action, and whether Yelp remains visible; do not retry solely for analysis |
| E: registration/subscription | **PROVED observation:** the launch flow presented registration/account/subscription language | **INFERRED:** a post-launch platform, service, or account gate is active | **UNKNOWN:** screen owner; Yelp-owned registration was not found; account/network state | platform wrapper, Store/Register/common popup, or parsed account error | Match exact text across Yelp/common/Register/Store/native resources | Record title/body/buttons, then stop without accepting or changing state |
| F: normal home/search | **PROVED observation:** Yelp remained visible at ordinary home/search UI | **INFERRED:** catalog, launch/resume, foreground, and sufficient UI initialization succeeded | **UNKNOWN:** fresh lifecycle, search, speech, connectivity, TLS, backend acceptance | splash/home chain crossed; network chain remains optional/unobserved | Identify controls that enqueue `GpSearchRequest` and local prerequisites | Record first stable screen/control enabled state; add no search solely for this framework |
| G: fully functional | **PROVED observation:** observer explicitly recorded normal UI plus relevant results from an ordinary search in the documented flow | **INFERRED:** platform connectivity, request, HTTPS response, parse, and display crossed runtime gates | **UNKNOWN:** exact JAR hash, arbitrary inbound access, future service, unobserved speech | full stock outbound request/results chain | Compare observed fields with recovered response schema | Preserve the existing record; no repeat action is needed solely for analysis |
| H: unexpected/partial | **PROVED observation:** supplied facts do not support a narrower A-G case | **INFERRED:** one more precise stable-screen record is needed | **UNKNOWN:** catalog absence, launch success, error cause, backend behavior | first unresolved observable boundary | Match recorded text/styling against recovered resources before expanding research | Record one complete stable screen, title/text, page, and preceding ordinary action |

## Interpretation rules

**PROVED:** A requires `catalog_scope=all_pages`; an absent tile with partial or
unknown coverage maps to H. B requires the visible disabled state and no launch.
C requires the immediate-exit observation. D covers a launch error or an
observed failed search. E is reserved for explicit registration/account/
subscription presentation. F means stable local home/search UI without an
explicitly completed result flow. G requires both observed results and an
explicit fully-functional statement. Everything insufficient or unexpected is H.

**PROVED:** failure matching case-folds text, keeps letters/digits, collapses
punctuation/whitespace, and reports every matching signature in sorted order.
It does not silently convert a match into proof of a backend request.

**UNKNOWN:** no outcome establishes an arbitrary phone/computer input route,
general Internet access, or executable content delivery. **INFERRED:** G is the
strongest ordinary evidence for usable stock-signed outbound Yelp capability.
The [launch gates](yelp_launch_gate_model.md),
[network contract](yelp_network_contract.md), and
[native predicates](native_virtual_catalog_predicates.md) define the limits.
