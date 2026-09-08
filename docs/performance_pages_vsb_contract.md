# Performance Pages VSB upload contract

This is a static, read-only answer to the conditional VSB fallback question. It
uses the three hash-bound Performance Pages JARs and the stock VSBClient JAR
already represented in
[`method_evidence.json`](../reports/kim19_runtime_analysis/method_evidence.json),
[`application_service_graph.json`](../reports/kim19_runtime_analysis/application_service_graph.json),
and
[`network_capabilities.json`](../reports/kim19_runtime_analysis/network_capabilities.json).
No service was contacted, no request was replayed, and credential and endpoint
values are omitted.

## Static answer

**PROVED:** each recovered Performance Pages variant has a fixed timer-upload
caller. It supplies stock-generated timer HTML and the stock-generated report
name to an upload controller. The VSB fallback wraps those two values in a JSON
object with exactly two application fields, `data` and `name`, and calls the
stock VSB IXC interface with a fixed Performance Pages operation identity, a
current-time correlation string, and the JSON text.

**PROVED:** the VSB IXC interface is structurally broader than this one caller:
`sendDataToVSB(String, String, String)`,
`setBindNameForCallback(String, String)`, and
`removeBindName(String)` accept strings from resident applications. Its
implementation does not publish an unmatched operation. It selects an operation
from a daemon-owned configured operation set, builds the outer message using
that operation's metadata, and publishes to that operation's configured route.
Two named operations also have dedicated special handling before the generic
operation lookup.

**UNKNOWN:** the recovered IXC method body does not perform an explicit
caller-identity or per-caller operation-authorization check. The caller still
has to cross AMS/IXC lookup, remote-stub, lifecycle, and permission boundaries,
whose effective grants on the target were not recovered. Therefore the general
three-string Java signature does not establish general message-sending authority
for another resident application.

The signed Performance Pages application is consequently restricted by its own
code to a fixed timer-report contract. The shared VSB service is reusable by
configured stock operations, but the recovered evidence does not prove that an
arbitrary resident caller can select an operation or route, add a new operation,
or obtain the required IXC authority.

## Variants and entry path

**PROVED:** Viper `01.23.01`, Jeep `01.57.01`, and MY15 L-Series `02.01.01`
contain the same upload architecture. Viper and Jeep use the same selected
controller/callable class hashes; L-Series uses revised view and concurrency
types while retaining the same two-field application payload and VSB call
descriptor.

The recovered control flow is:

1. The stock timer view supplies an HTML report string and report filename to
   `UploadTimerRunController.submitUploadTask(...)`.
2. The controller retrieves the SDP client.
3. If the SDP client is non-null, it constructs the SDP
   `SendToWebsiteCallable` and submits it.
4. A null SDP client follows the controller's failure-status path. It does not
   enter the VSB fallback.
5. An exception during the SDP attempt reaches the exception handler and
   constructs `VSBSendToWebsiteCallable` (Viper/Jeep BCI 120; L-Series BCI 125),
   then submits it (Viper/Jeep BCI 123; L-Series BCI 128).

The VSB path is thus an exception fallback, not a general alternate transport
selected whenever SDP is absent. Whether a particular stock target reaches the
exception handler is **TARGET OBSERVATION REQUIRED**.

## Application request

`VSBSendToWebsiteCallable` stores only three inputs from Performance Pages:
the HTML text, filename, and stock view/status listener. Its
`createUplinkJSONString()` method constructs a new `JSONObject`, then performs:

| Application JSON field | Value source | Evidence | Control classification |
|---|---|---|---|
| `data` | Callable's timer HTML field | `JSONObject.put` at BCI 73 | Stock timer model/template |
| `name` | Callable's report filename field | `JSONObject.put` at BCI 84 | Stock filename dataflow |

**PROVED:** all three variants use those exact field names and sources. The
older callable returns the serialized JSON at BCI 150; L-Series returns it at
BCI 133. A caught `JSONException` is logged; the method still serializes the
current object. No arbitrary map of user fields, destination URL, MQTT topic,
or callback name is accepted by this Performance Pages method.

`VSBSendToWebsiteCallable.call()` then invokes:

```text
VSBClient.sendDataToVSB(operation, correlationId, payload)
descriptor: (Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V
```

For this caller, `operation` is the fixed Performance Pages identifier
`gskills`,
`correlationId` is `String.valueOf(System.currentTimeMillis())`, and `payload`
is the two-field JSON above. The invocation is at BCI 37 in every recovered
variant. The operation name is application identity, not a credential; no
endpoint or authentication value is reported.

## Callback registration and completion

Before sending, the callable refreshes the VSBClient reference, rebinds itself
in the local IXC registry as an `IxcFromVSB` callback, and calls
`setBindNameForCallback(operation, bindName)`. Viper/Jeep perform the callback
registration call at BCI 61; L-Series at BCI 64. The callable removes the
operation mapping and unbinds after completion or cleanup.

The VSB daemon retains an operation-to-bind-name map. After MQTT delivery token
completion, it resolves the bind name, obtains the `IxcFromVSB` remote object,
and calls `notifySuccess(correlationId)` or
`notifyFailure(correlationId)`. Performance Pages sets its local result status
and releases a `CountDownLatch`; Viper/Jeep release at BCI 28 and L-Series at
BCI 19. The waiting callable then reports stock success or failure status to the
timer view and deregisters.

**PROVED:** these callbacks report local MQTT delivery success or failure and
release the caller's wait. They do not prove that a website stored or accepted
the timer report. The wait duration is obtained from a stock resource setting;
its value is deliberately omitted.

## VSB routing and message envelope

`VSBClientImpl.sendDataToVSB` handles two special operation identities and sends
all other values to the daemon's IXC operation dispatcher. The dispatcher looks
up an exact operation name in a set built from the daemon's configured operation
records. No match results in a log/no-send path.

For a matched generic operation, the dispatcher creates a send task with the
correlation string and application payload. The generic task builds an outer
JSON object whose keys are taken from the selected operation metadata and whose
values are:

| Semantic field | Recovered value source |
|---|---|
| Vehicle identity | Platform vehicle-identity helper |
| Correlation identity | Performance Pages current-time string |
| Data | Parsed two-field Performance Pages JSON object |
| Timestamp | Daemon-side current time |

The task publishes the resulting bytes to the selected operation record's
configured MQTT topic and QoS. Configuration and authenticated connection state
belong to VSBClient; Performance Pages supplies neither the topic nor QoS.
Configured endpoint and credential values are outside this report.

The exact selected-method evidence is:

| Source class and method | Relevant bytecode evidence |
|---|---|
| `VSBClientImpl.sendDataToVSB(String,String,String)` | Special-operation comparisons precede the generic dispatcher call to `com/sprint/chrysler/vsbclient/ixc/d.a(String,String,String)` at BCI 57-63 |
| `com/sprint/chrysler/vsbclient/ixc/d.a(String,String,String)` | Calls its exact-operation lookup at BCI 0-2; only a non-null match reaches the operation object's send method at BCI 13-17 |
| `com/sprint/chrysler/vsbclient/ixc/d.b(String)` | Iterates the configured operation set and accepts only `operationRecord.name.equals(argument)` at BCI 30-39 |
| `t/h/d.b()` | Builds the outer object: vehicle identity at BCI 8-32, correlation identity at BCI 36-63, parsed application data at BCI 65-102, and daemon timestamp at BCI 103-133 |
| `t/h/d.a()` | Reads the configured topic at BCI 5-11, converts the envelope to bytes at BCI 14-18, reads configured QoS at BCI 21-31, and invokes the MQTT publish wrapper at BCI 34 |
| `t/h/d.onSuccess` / `onFailure` | Queues the local result callback with the operation and correlation identity at BCI 9-31 |
| `t/g/b.run()` | Resolves operation to callback bind name at BCI 0-10 and calls `IxcFromVSB.notifySuccess` at BCI 37-42 or `notifyFailure` at BCI 50-55 |

These records are emitted from the selected VSBClient JAR in
[`method_evidence.json`](../reports/kim19_runtime_analysis/method_evidence.json);
the configured broker address and authentication literals are intentionally not
repeated here.

**PROVED:** the VSB implementation therefore exposes a shared configured-
operation dispatcher, not a raw topic publisher. Static presence of the public
three-string IXC method does not establish that arbitrary operation strings are
accepted.

## Authentication and sender authority

The visible boundaries are distinct:

| Boundary | Static result |
|---|---|
| Performance Pages to VSBClient | **PROVED:** local IXC/RMI lookup and remote interface call |
| Operation selection | **PROVED:** exact match against daemon-owned operation records |
| MQTT connection | **PROVED:** VSBClient uses configured TLS/authentication and Paho MQTT code; values omitted |
| Broker acceptance and backend processing | **UNKNOWN:** no live communication or backend evidence |
| IXC caller grant | **UNKNOWN:** no effective target permission/grant set recovered |
| Per-caller operation authorization inside `sendDataToVSB` | **UNKNOWN:** no explicit caller check is visible in the selected method body |

The absence of a check in one Java method is not proof of absent enforcement in
AMS, IXC stubs, registry lookup, policy, or native code. Conversely, the
existence of a configured operation is not proof that another caller is allowed
to invoke it.

## Failure and fallback conditions

The static failure boundaries are:

- **PROVED:** null SDP follows a local failure-status path; only an exception in
  the SDP attempt enters the VSB fallback.
- **PROVED:** absent VSB reference prevents the VSB send.
- **PROVED:** callback registry bind and remote calls can fail through the
  declared RMI/IXC exceptions; cleanup is attempted.
- **PROVED:** an unknown operation has no matching dispatcher object and is not
  published by the generic path.
- **PROVED:** JSON construction errors leave a possibly partial application
  object which is still serialized.
- **PROVED:** a null MQTT delivery token is treated as failure; token callbacks
  otherwise select local success/failure notification.
- **UNKNOWN:** local MQTT delivery success does not establish backend receipt,
  persistence, account association, or later processing.

## Capability boundary

**PROVED:** stock VSBClient is a reusable platform service for a finite,
configured set of stock operations. It supplies local IXC registration,
operation dispatch, message-envelope construction, authenticated MQTT delivery,
and callback routing.

**PROVED:** Performance Pages itself does not expose those degrees of freedom.
Its caller fixes the operation, callback identity, two-field payload schema, and
input sources. Its only runtime-varying request values are stock timer HTML,
the stock report filename, and timestamps/correlation identity.

**UNKNOWN:** the available evidence does not establish a general signed
message-sending capability for new or arbitrary resident applications. That
would require proof of caller authorization plus an already configured
operation that safely accepts the intended caller and payload. Neither follows
from the shared IXC interface alone.

The VSB fallback does not raise the Performance Pages capability above a fixed
application-specific upload. It remains useful evidence that the platform has a
shared configured transport service, while its caller-authority and
operation-provisioning boundaries prevent promotion to a general resident
messaging primitive.
