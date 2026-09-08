# KIM19 background services

**PROVED:** VSBClient and DRMSync_VSB declare daemon/headless behavior and perform
their main setup from `initXlet`; their `startXlet` methods are empty. **UNKNOWN:**
neither their physical presence nor missing foreground tiles proves runtime
activation. Native autostart is conditional on the launcher entitlement/override
and global gate described in the [runtime model](kim19_runtime_observation_model.md).

## VSBClient 04.03.23

**PROVED:** main class `t.s.e`, app ID
`f7583530-8d53-11e0-91e4-0800200c9a66`, init constructs `t/s/a` (BCI6) and queues
`t/s/c` (BCI31). The worker reads bundled Xlet properties, initializes
configuration/service managers, constructs WMA receiver `t/b/d` (BCI154), queues
the MQTT manager (BCI167/170), obtains IXC (BCI183), and initializes the VSB
service implementation (BCI190/193).

**PROVED:** MQTT construction runs through `t/b/b` configuration/state methods
and `t/b/a`; SSL factory and username/password are assigned in connect options.
The packaged broker is `ssl://vsb.cvp.extra.chrysler.com:8443`. The client receives
JSON callbacks and dispatches typed or generic queued work. WMA receiver setup
also occurs during the worker path. See [network details](kim19_network_capabilities.md)
and [selected method evidence](../reports/kim19_runtime_analysis/method_evidence.json).

**PROVED:** `VSBClientImpl.c` calls its bind/refresh work. Method `e` rebinds
`VSB:com.sprint.chrysler.vsbclient.ixc.VSBClient` at BCI25. Method `f` enumerates
IXC names, matches lifecycle listeners, looks up remotes at BCI106 and calls
`refreshVSBClientReference` at BCI123. These are local Java remotes, not public
network services. **UNKNOWN:** current registration of each remote, caller
permissions, valid service credentials and current broker sessions.

**PROVED:** DRM and ASSIST contain concrete VSB locator consumers. **UNKNOWN:**
mandatory Yelp dependency on VSB is not established: Yelp's traced search path
uses its HTTP client and obtains a registry, but merely carrying DRM-notification
classes does not prove it registers them. Store/Register's MTS and DRM-related
state likewise must not be treated as proof that VSB is running now.

## DRMSync_VSB 03.01.07

**PROVED:** main `com.sprint.chrysler.drm.xlet.DrmSyncXlet`, app ID
`2BA676FA-1542-11E1-A537-1F614824019B`. Init obtains IXC (BCI8), constructs a
notification service (BCI21), supplies registry/service to DrmManager (BCI41/47),
constructs its worker Thread (BCI58), names/prioritizes it and starts it (BCI85).

**PROVED:** `DrmManager.run` registers an AppManager listener (BCI54/58), sets up
an ignition sensor (BCI64) and initializes its state (BCI67). It checks VSB
reference validity repeatedly (BCI87/142/181/209), with waiting/retry work before
the processing loop. Running/shoulder-tap/processing/low-power state affect the
path; the existence of the worker is not proof of a successful sync.

**PROVED:** `init` loads MTS settings (BCI41), establishes a connection listener
(BCI79), and initializes VSB (BCI85). The locator looks up VSB (BCI25), creates a
callback (BCI76), rebinds it (BCI87), and calls
`VSBClient.setBindNameForCallback` (BCI98). `retrieveSubscriberState` sends VIN
and self app identity to its subscriber-state manager (BCI15/18/21).
`processSyncRequest` checks provisioning/VIN before the grant request (BCI36,
then BCI137/140). The bundled MTS base is
`https://mts.cvp.extra.chrysler.com:8443/mts-api`.

**PROVED:** the notification dispatcher enumerates registry entries (BCI67),
looks up registered remotes (BCI112) and dispatches app-change, process-complete,
registration-change and reset-warning messages (BCI268/283/312/334).
**UNKNOWN:** a callback interface existing in another JAR does not prove that
app has bound a listener; the relevant caller/lifecycle must be present.

**PROVED:** this service also contains stock grant/download/install/upgrade and
reset-related processing. Those capabilities are outside the operator procedure;
the research documents prerequisites without triggering them. **UNKNOWN:** an
ordinary account/app-list change cannot uniquely identify which background
path ran or certify successful authorization of every installed app.

## What can reveal activation without a tile?

| Available evidence | What it can establish | Limit |
|---|---|---|
| Existing service-specific log showing init/bind | INFERRED execution of that setup at the logged time, subject to log provenance | Not current liveness or successful network |
| Existing runtime IXC binding record | INFERRED service registration at capture time | Not proof of a responding callback or backend |
| Ordinary dependent-app service/account message | PROVED message was shown; INFERRED consistency with a stock dependency state | UNKNOWN which daemon supplied it; cache and alternate paths may explain it |
| App-list/registration status changes observed passively | PROVED change in displayed state | UNKNOWN cause, binary identity and exact grant contents |
| No VSB/DRMSync Apps entry | PROVED lack of exposed foreground entry in surveyed views | UNKNOWN installed/running/connected state; expected for headless packages |

**TARGET OBSERVATION REQUIRED:** ordinary UI alone cannot directly prove either
daemon's activation. The checklist does not request logs, registry queries,
diagnostic commands or service invocations. Existing evidence may be interpreted
later if already available; none is required or collected from the radio here.

Machine-readable [background service model](../reports/kim19_runtime_analysis/background_services.json).
