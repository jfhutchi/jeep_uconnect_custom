# Recovered stock capability assessment: 68224525AM / KIM19

**INFERRED assessment:** Yelp remains the best first candidate for useful
ordinary interaction on this radio. The recovered code closes launch, search,
HTTPS, response and results paths, and now also closes a platform-recognized
speech-to-search path. Performance Pages provides a second concrete capability:
locally exporting stock-generated timer results to USB/SD without a backend
call on that branch. The focused media follow-up classifies that path as
Level 2: fixed destinations, application-generated filenames and timer HTML,
with no established stock-signed consumer handoff. Its exact vehicle/feature gates and target launchability
make it a weaker first lead. Neither has yet been observed on the physical
radio during this research.

## Complete Yelp reconstruction

**PROVED:** the recovered Yelp path is now closed from descriptor and generic
Apps selection through AppManager/DRM/AMS, Xlet lifecycle, local splash,
location refresh, the first 8.4-inch home, touchscreen and speech inputs,
request construction, the default HTTPS client, legacy JSON parsing, result
screens, details, and the recovered phone/navigation platform implementations.
The complete graph and remaining gates are in the
[launch graph](kim19_yelp_launch_graph.md) and
[runtime gate table](kim19_yelp_runtime_gates.md).

**PROVED:** the useful category/search/voice home is pre-backend. The startup
path does not contact the Yelp search endpoint or require a search response
before constructing `GpCurrentLocationScreen`. Touchscreen ordinary text and
recognized speech both reach the same `GpSearchRequest`; ordinary text is
URL-encoded without a local command, HTML, script, or rendering interpreter.
See [input dataflow](kim19_yelp_input_dataflow.md) and
[network contract](kim19_yelp_network_contract.md).

**PROVED:** response data is confined to `Place` models, stock LWUIT widgets,
distance/geocode logic, and typed phone/navigation services. The recovered
receiver chain reaches `PhoneImpl`/BluetoothService and
`NavigationImpl`/HMIGatewayService. Yelp contains no browser/WebView,
active-content sink, SocketCommandSource/CommandLooper, VSB/SDP client, or media
handoff. See [response actions](kim19_yelp_response_actions.md) and
[stock handoffs](kim19_yelp_stock_handoffs.md).

**TARGET OBSERVATION REQUIRED:** current installation/registration, DRM/grants,
actual launch, location and speech services, connectivity, DNS/TLS,
authorization/backend/schema acceptance, phone availability, and OpenNav
activation. The next action remains the bounded
[one-tap observation](kim19_yelp_target_observation.md). This stronger static
closure does not change the Performance Pages conclusion below: it remains a
narrow Level-2 fixed-destination timer-HTML writer with no proved consumer
handoff.

**UNKNOWN:** no demonstrated route allows arbitrary phone, Wi-Fi, Bluetooth or
USB input to become newly executable behavior. Authenticated broker callbacks,
platform voice recognition and client HTTP responses are real input paths,
but do not grant an arbitrary external party authority to use them. The
research found useful existing behavior, not an unsigned-code entry point.

## Ranked serious candidates

Ranking is **INFERRED**, based on completeness of the recovered chain,
ordinary usefulness and the number of unresolved activation gates. The chains
and call sites referenced below are **PROVED static evidence**; all current
target and service states remain **UNKNOWN** unless observed.

| Rank | Candidate and complete conditional chain | Useful effect | Gates / evidence limit |
|---|---|---|---|
| 1 | Apps -> authorized AMS/Yelp Xlet -> scheduled splash/home -> keyboard/category or recognized speech -> GpSearchRequest -> connectivity -> default HTTPS client -> JSON/status -> stock result screen | Search and display businesses; voice supplies a term through the stock service | Installed/registered/visible/authorized state, UI/platform setup, location, connectivity, TLS/credentials and backend acceptance; voice adds service/session gates |
| 2 | Correct Performance Pages variant -> timer/save UI -> USB/SD option -> fixed packaged device path plus timersResult -> generated HTML/name -> create-new-file guard -> writer -> save-status UI | Level 2 timer-report export; backend absent and no established consumer handoff | Exact vehicle/feature/launch gates, timer UI/data and media/permissions; existing filename produces no-write success, and close errors can be suppressed |
| 3 | Performance timer uConnect action -> SDP attempt throws -> VSB callable -> local service/callback binding -> configured uplink -> MQTT delivery -> success/failure callback -> latch -> stock status UI | Existing app-to-service output with visible completion state | Null SDP alone does not select VSB; lookup, permissions, config/authentication and delivery required; success does not prove website persistence |
| 4 | Store launch/loading -> constructed MTS discovery/catalog/vault request -> HTTP response -> account/catalog UI; invalid account confirmation can request Register through AppManager.chain | Catalog/account inspection and a concrete stock app-to-app launch request | Current MTS/authentication/account state; purchase/registration actions change state and are excluded from the first observation |
| 5 | Register init/cached-stage check -> possible notifyDestroyed -> remaining UI init/loading -> MTS subscriber request -> registration/welcome/error UI | Existing provisioning-state workflow | Cached state, lifecycle scheduling and backend state; presence/absence is not a reliable registered/unregistered bit |
| 6 | ASSIST init -> scheduled splash -> main landing UI -> service action -> platform/VSB request and call state | Existing assistance-service UI | Service/phone/VSB state; calls are not harmless daemon probes; its VSB notification bodies are no-ops |
| 7 | Required/conditional background startup -> VSB client config/TLS/MQTT -> subscribed callback -> topic router -> configured stock task -> local callback; DRM waits for VSB then performs subscriber/sync processing | Trusted service communication and app/provisioning changes | No ordinary arbitrary-publisher authority established; effects include update/reset/control work and cannot be used as passive tests |

**PROVED:** the three Performance packages coexist in KIM19. Their descriptor
conditions require Performance Pages present and the respective vehicle line:
Jeep 1, Viper 43, L-Series 44/41/2. When all relevant PPS attributes are present,
the descriptor comparisons can be modeled exactly. Missing-attribute native
control flow is not a simple fail-closed AND. Native property parsing sets the
condition-presence bit; a separate super-app UUID comparison sets the other
visibility flag. L-Series additionally throws on an unsupported line in its
module lifecycle. A same-named Performance Pages tile does not identify which
of these binaries is running or prove its grant contents.

## Important corrections and stronger findings

- **PROVED:** `app+0x29a` bit 3 is a parsed show-condition-presence flag, traced
  through property subobject `app+0x9c`, not an unidentified entitlement bit.
  `app+0x294` is a configured super-app identity result. These flags and native
  catalog visibility are separate from manual launch authorization.
- **PROVED:** VSB `t/j/b.a()String` at callback BCI76 is a topic getter. The
  earlier typed-handler claim in `7714004` is superseded. Accepted callbacks
  queue `t/r/d`; the actual app-topic route reaches IXC dispatch at BCI221.
- **PROVED:** Yelp recognized speech reaches the same stock request/result
  code as touchscreen search. Actual speech recognition and backend operation
  remain **TARGET OBSERVATION REQUIRED**.
- **PROVED:** Performance Pages exports generated `.html` to configured USB/SD
  destinations and has a conditional VSB upload/status route. This strengthens
  the external-interface result from a negative USB-to-code finding to a
  concrete ordinary output capability.
- **PROVED:** callback bodies matter: ASSIST's are empty; DRM can queue work;
  Performance success/failure releases a waiter. The shared interface name
  alone cannot establish a screen effect.

## Coverage and stopping boundary

**PROVED:** analysis covers all nine KIM19 identities, all 19 JARs and 4,572
class entries, with the unchanged 37-file package manifest and separate
24-file common base. The focused tool extracts activation predicates, selected
methods/native windows, a network/interface census, configurations, reviewed
cross-app relationships and observation cases. Independent `javap` checks bind
important calls to their descriptors/offsets. Relevant native visibility,
catalog, launch, property parsing and service configuration were also traced.

**PROVED scoped negative result:** selected KIM19 invocation census finds no
ServerSocket/DatagramSocket/MulticastSocket, script-engine or process-launch
calls. Resource loading, reflection/library factories, local Paho transport,
serialization helpers and native-loading declarations were classified
separately from an externally controlled executable chain. **UNKNOWN:** a
scoped negative Java result cannot rule out a native/platform listener on the
real radio.

**PROVED:** follow-up tracing identifies the special condition-clear/autostart
path as VSBClient setup, and identifies the L-Series native graphics library's
packaged source and rendering caller. **UNKNOWN:** remaining static details
include virtual catalog predicates and production activation of isolated
library/transport candidates. None
currently closes a stronger ordinary external-input path than the ranked
chains. They must not be converted into entitlement, listener or code-loading
claims. Further static work should be driven by evidence that one of these
boundaries matters to the observed target rather than repeating broad censuses.

**INFERRED stopping assessment:** the recovered evidence relevant to choosing
an ordinary supported capability is reasonably exhausted for this pass. Each
serious candidate has a concrete construction/lifecycle path and explicit
gates; further broad enumeration would not resolve installation, grants,
platform-service state, media availability or backend acceptance on this radio.
This is not a claim that every native instruction has been understood.

The completed Yelp checkpoint resolves the selected virtual catalog predicates;
see [their evidence](native_virtual_catalog_predicates.md). The media follow-up
below supersedes the earlier suggestion to keep enumerating that boundary.

## Performance Pages media reassessment

**INFERRED ranking:** Performance Pages remains candidate 2. It is useful as an
ordinary timer-report output, but the fully traced path supports less general
file-transfer reuse than the open research question allowed. This narrows the
possible interpretation; it does not retract the established timer export.
The [capability classification](performance_pages_file_write_capability.md)
and [complete call graph](performance_pages_export_call_graph.md) explain why.

**PROVED:** all variants use fixed packaged USB/SD roots plus `timersResult`,
application-generated names and a mandatory `.html` suffix. The writer's
create-new-file guard skips an existing filename without replacing it; the UI
still receives the success status. Open/write/flush exceptions reach failure
mapping, while close exceptions are logged and suppressed. This corrects the
earlier imprecise statement about generally suppressed write errors.

**PROVED scoped negative result:** the
[KIM19/common-base consumer graph](removable_media_consumer_graph.md) finds no
complete stock-signed reader or importer for the exported timer file.
**UNKNOWN:** a broader live-platform consumer cannot be excluded from this
scoped recovered-artifact result. No cross-application handoff is promoted.

**PROVED:** Performance Pages uses direct Java file operations. Common
permission-gated FileIO and EcoDrive APIs exist separately; the
[native EcoDrive follow-up](ecodrive_native_storage_boundary.md) binds a fixed
internal data source and EcoDrive-specific USB destinations. No KIM19 caller
connects these services to the timer path. **INFERRED:** these unclosed service
leads do not outrank an application with a complete ordinary UI path, and no
finding promotes a capability above Yelp.

The narrow media outcome justified the conditional
[VSB contract follow-up](performance_pages_vsb_contract.md). **PROVED:** the
application constructs its fixed `gskills` timer request; the shared service
accepts only configured operation names on the selected generic dispatch path.
**UNKNOWN:** effective caller authority and live delivery remain outside that
static method. **INFERRED:** VSB no longer needs another broad static contract
pass, and the EcoDrive service's missing ordinary caller does not create a
stronger immediate research direction. The ranked next action remains the one
ordinary Yelp observation described below; no export, upload or service call
was performed during this investigation.

## The next physical observation

**TARGET OBSERVATION REQUIRED:** after recording every ordinary Apps page,
make **one normal Yelp launch if Yelp is present**. Record the first screen,
exact error, whether splash appears, whether it reaches the home/search UI,
and whether it immediately returns or stays visible. Do not append search,
voice, registration, calls, timer runs, exports or uploads to this first
observation. Normal launch can update application history/RMS/preferences.
If Yelp is absent, the completed Apps-page record itself is the evidence;
do not substitute a background-service probe.

**INFERRED:** this single launch best separates mere catalog exposure from
authorized app/UI execution while preserving the highest-value remaining
candidate. A photograph cannot prove exact installed binary identity or live
backend functionality. The [checklist](target_observation_checklist.md) and
[Yelp cases A-F](kim19_yelp_reachability.md) state what each observation supports.

## Reproducible evidence

- [Runtime model](kim19_runtime_observation_model.md)
- [Application/service graph](kim19_application_service_graph.md)
- [Network and external-interface matrix](kim19_network_capabilities.md)
- [Background service and callback trace](kim19_background_services.md)
- [Checkpoint verification](../reports/kim19_runtime_analysis/verification.md)
- [Media investigation verification](../reports/kim19_runtime_analysis/performance_pages_verification.md)
- [Machine-readable graph](../reports/kim19_runtime_analysis/application_service_graph.json)
- [Selected method/native evidence](../reports/kim19_runtime_analysis/method_evidence.json)
- [Complete Yelp launch graph](kim19_yelp_launch_graph.md)
- [Complete Yelp target decision tree](kim19_yelp_target_observation.md)
- [Seven deterministic Yelp reports](../reports/kim19_yelp/launch_graph.json)

**PROVED scope:** recovered artifacts were read only; no vendor classes were
executed, no radio or live backend was contacted, and no firmware, signing,
authorization or vehicle configuration was changed. All research writes and
Git operations for this follow-up occur in the isolated
`codex/kim19-yelp-reconstruction` isolated worktree for this final follow-up;
the Performance Pages conclusion and original dirty checkout remain preserved.
