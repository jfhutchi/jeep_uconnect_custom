# Stock extension surface

## Evidence boundary

**PROVED** means direct recovered structure or a source-addressed static edge. **STRONGLY INFERRED** joins direct facts with a stated inference. **UNKNOWN** means the recovered evidence does not establish the claim.

**UNKNOWN** No target/vehicle operations were performed. Static presence is not reported as executable or externally reachable behavior.

## Corpus

**PROVED** Read-only recovered RA4 18.45.01 resident Java, installed descriptors, existing source-addressed repository findings, and candidate-led hidden-HBC metadata. Coverage: 300 resident archives; 72,507 class occurrences; 13,272 unique class hashes; 1,528 parsed small resources; 832 candidate-led hidden-HBC files.

## Java Extension-Surface Census

| Category | Observations | Components | Classification | Boundary |
|---|---:|---:|---|---|
| browser_webkit | 370 | 20 | PROVED | static member-reference census only |
| configured_class | 69 | 69 | PROVED | parsed small-resource class-like values; false positives retained |
| dynamic_loading | 601 | 447 | PROVED | load/define/forName/newInstance references; runtime target unresolved |
| factory_provider | 8375 | 909 | PROVED | name and member-reference candidates; many ordinary factories |
| ipc_service | 1049 | 238 | PROVED | SvcIPC/service-like references; registration and runtime use separate |
| media_import | 703 | 134 | PROVED | media/import-like parser and player references |
| network_service | 125 | 31 | PROVED | socket API references; only SocketCommandSource has a recovered listener chain |
| plugin_registration | 45 | 26 | PROVED | registry/provider references; no generic third-party plugin ingress proved |
| reflection | 339 | 94 | PROVED | reflection API calls; supplied names and receiver types require separate tracing |
| resource_package_loading | 487 | 173 | PROVED | JAR/ZIP/resource/package API references |
| scripting_interpreter | 5 | 2 | PROVED | lexical candidates only; no resident general-purpose script interpreter chain proved |
| structured_data | 4970 | 517 | PROVED | XML/JSON/properties API references; external origin not inherited |
| url_protocol | 243 | 91 | PROVED | URL/URI API references; handler/dispatch capability unresolved per record |
| user_file_resource | 2525 | 522 | PROVED | file/stream/reader references; user control not inferred from File APIs |

**UNKNOWN** Counts establish static observations only. Each category still requires a separate origin-to-capability path.

## SocketCommandSource verdict

**STRONGLY INFERRED** The recovered code is lifecycle-activatable local test automation rather than unreferenced residue, but target execution is unproved and the only recovered factory path binds IPv4 loopback.

| Activation state | Classification | Conclusion |
|---|---|---|
| Class Exists | PROVED | Five recovered resident JAR occurrences contain the same SocketCommandSource class hash. |
| Statically Reachable | PROVED | Concrete Xlet init paths reach the no-argument constructor, and CommandLooper.run has a superclass virtual-dispatch candidate to the concrete wait method. |
| Activation Mechanism Exists | PROVED | Normal Xlet start starts the CommandLooper HU thread; its run loop calls the command source until normal destroy stops it and closes the listener. |
| Activation Configured | STRONGLY INFERRED | Yelp, iHeart, and Application Manager descriptors select concrete AbstractHUXlet subclasses whose recovered init path creates the looper without a discovered feature/configuration gate. |
| Production Enabled | STRONGLY INFERRED | The framework is embedded in recovered production application copies, but these are normal non-daemon or non-autostart applications and listener enablement is conditional on application launch. |
| Listener Executable | UNKNOWN | No target run establishes successful policy checks, bind, port availability, accept, or command effects. |
| Externally Reachable | UNKNOWN | The recovered factory path is loopback-only and the bounded native pass found no candidate-specific forwarder; any off-unit route remains unproved. |

## Ranked candidate mechanisms

### Rank 1 - Stock Apps UI to native AppManager/AMS launch path

**PROVED** Component: Stock Apps UI to native AppManager/AMS launch path.
**PROVED** Activation path: AppsMainScreen item selection -> MainSupplement AppManager.startXlet -> native startApp dispatch with DRM checking -> AMS start.
**PROVED** User-controlled input: selection of an already-listed installed application.
**PROVED** Useful resulting capability: Request normal stock lifecycle launch of an already-authorized resident Xlet.
**PROVED** Prerequisites: application already installed and listed; DRM launcher entitlement permits start; AppManager and secure AMS active.
**UNKNOWN** Unresolved unknowns: target-visible result; whether any newly authorized app appears correctly in the stock list; completion and foreground outcome.
**PROVED** New-package authorization required: no.

### Rank 2 - Tweddle SocketCommandSource local test-input framework

**STRONGLY INFERRED** Component: Tweddle SocketCommandSource local test-input framework.
**STRONGLY INFERRED** Activation path: resident Yelp/iHeart/Application Manager Xlet init -> AbstractHUXlet initCommandLooper -> CommandSource factory -> normal Xlet start -> HU thread accept loop.
**STRONGLY INFERRED** User-controlled input: one line of JSON from an on-unit IPv4 loopback TCP client.
**STRONGLY INFERRED** Useful resulting capability: Drive and inspect resident Tweddle UI/test functions without introducing a new resident package.
**STRONGLY INFERRED** Prerequisites: one containing stock Xlet is launched; socket policy permits bind; 127.0.0.1 port 11111 is available; an already-authorized on-unit client exists.
**UNKNOWN** Unresolved unknowns: target execution; effective socket permission; port collision; successful command behavior; any authorized on-unit client path.
**STRONGLY INFERRED** New-package authorization required: no.

### Rank 3 - Authenticated USB application-media installer

**STRONGLY INFERRED** Component: Authenticated USB application-media installer.
**STRONGLY INFERRED** Activation path: SWDL media detection -> signed nested-image verification -> installer manifest external script -> application JAR staging -> secure AMS install/upgrade.
**STRONGLY INFERRED** User-controlled input: issuer-authorized signed application media inserted through the stock update-media path.
**STRONGLY INFERRED** Useful resulting capability: Install or upgrade an authorized resident Java application using the stock package split, validation, and lifecycle services.
**STRONGLY INFERRED** Prerequisites: legitimately signed installer media; legitimately authorized application package; compatible package metadata; secure AMS and installer services active.
**UNKNOWN** Unresolved unknowns: external application manifest sample; legitimate issuer/tool availability; target transaction and rollback outcome.
**STRONGLY INFERRED** New-package authorization required: yes.

### Rank 4 - KIM3 Application Manager remote catalog pipeline

**STRONGLY INFERRED** Component: KIM3 Application Manager remote catalog pipeline.
**STRONGLY INFERRED** Activation path: UpdateManagerXlet task -> catalog JSON model -> staged download and CRC check -> native installApp -> authenticated AMS preflight/upgrade.
**STRONGLY INFERRED** User-controlled input: stock catalog install/update/remove selection plus remote catalog response and package bytes.
**STRONGLY INFERRED** Useful resulting capability: Catalog-mediated lifecycle management for issuer-authorized resident applications.
**STRONGLY INFERRED** Prerequisites: production catalog service and entitlement; authorized package; network connectivity; native AppManager and secure AMS active.
**UNKNOWN** Unresolved unknowns: production endpoint and response; complete catalog package sample; server-side authorization; target outcome.
**STRONGLY INFERRED** New-package authorization required: yes.

### Rank 5 - Permissioned Kona AppManager Java/SvcIPC API

**STRONGLY INFERRED** Component: Permissioned Kona AppManager Java/SvcIPC API.
**STRONGLY INFERRED** Activation path: already-running signed Xlet method call -> AppMgrPermission check -> SvcIPC AppManager operation -> native dispatcher -> AMS lifecycle helper.
**STRONGLY INFERRED** User-controlled input: application ID and operation parameters supplied by a permissioned resident caller; any human upstream is caller-specific.
**STRONGLY INFERRED** Useful resulting capability: Query, start, pause, stop, install, uninstall, or chain installed applications through resident service contracts.
**STRONGLY INFERRED** Prerequisites: already-authorized resident caller; effective AppMgrPermission appMgr; SvcIPC AppManager and secure AMS active.
**UNKNOWN** Unresolved unknowns: which stock callers expose each operation to a user; live principal/policy; service result and completion semantics.
**STRONGLY INFERRED** New-package authorization required: no.
