# KIM19 target-observation closure runbook

This runbook resolves only facts that recovered artifacts cannot answer. It is for the vehicle owner; no observation in this document was performed during static research. The canonical matrix is [unresolved_gates.json](../reports/kim19_final/unresolved_gates.json).

## Safety and ordering

Run observations in order. Prefer A before B, and stop after the first useful B result. Categories C and D require separate owner approval because they transmit or change state. Do not test credentials, alter DNS/TLS, contact historical/private endpoints, probe listeners, forward ports, enable diagnostics, install packages, change policy/trust/DRM, or modify vehicle configuration.

Normal HMI navigation is treated as passive in A. A normal app launch in B can update application history/preferences even though it is local-only. Record exact text and photographs; do not infer a backend, daemon, binary identity, or permission from a generic error.

## A. Zero-modification/passive

### A1 — Passive stock inventory

- **Exact action:** Record the existing software/part-number screen. Photograph every ordinary Apps page, category, favorites view, and running view without opening a tile.
- **Expected visible states:** Reported part/software values; every visible tile/name; no tile for a headless daemon is expected.
- **Proves:** What the ordinary HMI exposes at that moment and whether Yelp, Store, Register, ASSIST, or Performance Pages is visible.
- **Falsifies:** A claim that an app is currently visible if it is absent from every recorded ordinary view. It does not falsify installation, authorization, or daemon execution.
- **Data transmission:** No.
- **Persistent change:** No intended persistent change.
- **Network/Bluetooth/GPS:** None required.
- **Stop:** Stop after all existing views and the version screen are recorded. Do not open a tile.

### A2 — Already-existing package/service evidence only

- **Exact action:** If the owner already possesses a non-mutating official package/version export, service log, or IXC inventory, preserve it and compare exact versions/bind names. Issue no new diagnostic command.
- **Expected visible states:** Exact KIM19 or older app version; existing VSB/DRM init/bind record; or no relevant record.
- **Proves:** The recorded artifact identity or setup at the log/export time, subject to provenance.
- **Falsifies:** Only a matching recorded identity/state. Absence does not prove a component never ran.
- **Data transmission/persistent change/network:** None.
- **Dependencies:** Already-existing owner evidence.
- **Stop:** Stop if obtaining evidence would require a target command, new logging, policy change, port/listener probe, or helper installation.

## B. Local-interaction-only

### B1 — One normal Yelp launch (recommended)

- **Exact action:** After A1, if Yelp is visible, tap it once. Record the first screen, exact error text, splash, approximate transition time, whether category/search home appears, and whether the screen remains visible. Enter no search.
- **Expected visible states:** No tile; immediate authorization/registration error or return; splash then failure; stable pre-backend category/search home; unexpected screen.
- **Proves:** The deepest crossed boundary among catalog exposure, AppManager/DRM/AMS authorization, lifecycle, local resources/container/theme, and pre-backend UI.
- **Falsifies:** Only prerequisites earlier than the observed boundary. A launch failure does not falsify later static code or identify its cause without a specific message.
- **Data transmission:** No Yelp search request. Do not add a packet test.
- **Persistent change:** Possible normal app history/preferences.
- **Network:** Not required for the proved home construction. Platform location may be queried locally.
- **Dependencies:** Visible Yelp tile and normal HMI.
- **Stop:** Stop at the first stable home screen, exact error, or return to Apps. No search, voice, dial, route, socket probe, or repeated launch.

### B2 — One normal Performance Pages launch (fallback only)

- **Exact action:** Only if Yelp is absent and the owner chooses the second candidate, tap a visible Performance Pages tile once. Record its exact name/variant cues, first screen, error, and stable landing UI.
- **Expected visible states:** No tile; authorization/vehicle-feature error; Viper/Jeep/L-Series landing UI; unexpected screen.
- **Proves:** The visible variant and progress through vehicle predicate, AMS, and local UI gates.
- **Falsifies:** Only the corresponding observed activation hypothesis; it does not test media or VSB.
- **Data transmission:** None intended.
- **Persistent change:** Possible normal app history/preferences.
- **Network:** Not required.
- **Dependencies:** Visible tile and live vehicle PPS/configuration.
- **Stop:** Stop at the first stable landing/error/return. Do not start a timer, save, export, or upload.

## C. Network-transmitting

These are not part of the recommended first observation.

### C1 — One stock Yelp category search

- **Exact action:** Only after successful B1 and separate approval for network transmission, select one ordinary fixed category once. Record loading, exact error, result list, and details availability. Do not choose phone/navigation.
- **Expected visible states:** Connectivity error; TLS/service/backend error; no results; results/details.
- **Proves:** Progress through request construction, connectivity, TLS/backend/schema acceptance, and stock result rendering to the deepest observed boundary.
- **Falsifies:** A result list falsifies a claim that current stock search is wholly unavailable. Failure does not uniquely identify DNS, TLS, credential, account, or schema cause.
- **Data transmission:** Yes—stock query/location metadata.
- **Persistent change:** Possible cache/history/preferences.
- **Network/Bluetooth/GPS:** Network and location required; Bluetooth not required.
- **Stop:** Stop at the first results/details screen or exact error. Do not repeat, dial, route, alter TLS/DNS, or inspect credentials.

### C2 — One stock Yelp voice search

- **Exact action:** Only after C1 and separate approval, invoke Yelp's ordinary voice action once and speak a harmless generic term.
- **Expected visible states:** VR unavailable; cancel/no-recognition; recognized term then network error; same results UI as touch.
- **Proves:** Live VR discovery/session/callback and convergence into the stock request path.
- **Falsifies:** A successful result falsifies a claim that voice is disconnected from search. Failure does not falsify the static listener/callback graph.
- **Data transmission:** Yes—recognized term/location through the stock request.
- **Persistent change:** Possible cache/history/preferences.
- **Network/Bluetooth/GPS:** Microphone/VR, location, and network required; Bluetooth not required.
- **Stop:** Stop after one recognition/result/error. Do not repeat or speak sensitive content.

## D. State-changing

### D1 — One typed Yelp phone or navigation handoff

- **Exact action:** With explicit side-effect approval, choose exactly one result and either initiate the phone action or request navigation—never both in the same observation.
- **Expected visible states:** Service-unavailable dialog; phone confirmation/call state; navigation activation/error/route state.
- **Proves:** Runtime availability of the selected typed receiver chain to the deepest visible boundary.
- **Falsifies:** Only the selected live-service hypothesis; the proved static sender/receiver chain remains.
- **Data transmission:** Yes for a call; navigation may use platform/network data.
- **Persistent change:** Yes—call/navigation state and possible history.
- **Dependencies:** Successful C1; paired phone for dial, or GPS/OpenNav/HMI for route.
- **Stop:** Stop/cancel at the first confirmation, call state, route state, or exact error. Follow local law and owner safety requirements.

### D2 — One Performance Pages media export

- **Exact action:** With explicit approval and empty owner-controlled media, create one ordinary timer record, select one stock USB or SD save option, safely remove the medium, and inspect the single `timersResult` file off-unit.
- **Expected visible states:** Media unavailable; stock save failure; UI success but no/partial file; complete generated HTML.
- **Proves:** Live variant, timer UI, mount/grant/write path, and off-unit durability to the observed boundary.
- **Falsifies:** A complete file falsifies a claim that the direct writer is unusable on that setup. UI success alone does not prove complete bytes.
- **Data transmission:** No network transmission.
- **Persistent change:** Yes—timer/app state and one removable-media file.
- **Dependencies:** Launchable correct variant, timer state, writable USB/SD.
- **Stop:** Stop after one file inspection. Do not craft names/content, reinsert for consumption, or upload.

### D3 — Excluded state-changing service workflows

Do not use registration, Store purchase/account confirmation, ASSIST calls, Performance upload, DRMSync/VSB triggers, application install/update/reset, or diagnostic/test commands as closure probes. They transmit and/or change stock application, account, communication, or vehicle-adjacent state. Each would require a separate objective, safety plan, and explicit authorization.

## Outcome interpretation for B1

| Observation | Supports | Does not support |
|---|---|---|
| Yelp absent from all A1 views | No ordinary visible Yelp entry at capture time | Not proof of no installed binary, no daemon, or no hidden/filtered catalog record |
| Tap returns immediately or shows authorization/registration error | Tile selection occurred; a pre-lifecycle or early lifecycle gate blocked progress | Not proof which DRM/registration/service gate failed without exact evidence |
| Splash appears, then error/return | AMS lifecycle and enough local resources/UI executed for splash | Not proof of home/search, connectivity, or backend acceptance |
| Stable category/search home | Useful Level-1 local Yelp UI is reachable; catalog, authorization, lifecycle, theme/container, and home construction passed | Not proof of search backend, voice, phone, or navigation |
| Unexpected UI/version | Target state contradicts the expected KIM19 presentation | Not license to probe; preserve evidence and reassess statically only if genuinely new artifacts exist |

## Recommended sequence

Perform A1. If Yelp is visible, perform B1 once and stop. If Yelp is absent, preserve A1 as the result; B2 is optional only if the owner values the second-ranked Performance Pages candidate. C and D are not needed to complete static research.
