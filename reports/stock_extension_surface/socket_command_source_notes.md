# SocketCommandSource evidence record

## Scope and verdict

This record is a static, read-only reconstruction from the recovered resident
Java corpus. It does not report a target observation and it does not provide an
off-unit operating procedure.

**STRONGLY INFERRED:** `SocketCommandSource` is an activatable part of the
Tweddle test-input framework, not merely an unreferenced class. Five recovered
stock application JARs contain byte-identical copies. In each copy, an Xlet
lifecycle path constructs the source and a `Runnable` path consumes it. The
listener is conditional on one of those applications reaching normal Xlet
`initXlet` and `startXlet` lifecycle callbacks.

**PROVED:** The only recovered factory construction uses the no-argument
constructor, which fixes the endpoint to IPv4 loopback `127.0.0.1` and TCP port
`11111`. The recovered Java code contains no authentication, authorization, or
source-address comparison. This is therefore a local test-automation surface,
not evidence of an externally exposed service.

**UNKNOWN:** No target execution was performed. Successful bind under the
selected Java security policy, port availability, actual application launch,
accepted connections, command effects, and any non-loopback forwarding path
remain unproved.

The detailed source addresses below are also present in
`activation_call_paths.json`. Bytecode offsets are offsets within the named
method's `Code` attribute.

## Occurrences and identity

**PROVED:** All five occurrences of
`com/tweddle/test/input/SocketCommandSource.class` are 3,480-byte classfiles
with SHA-256
`55bf4d4ca3872b4434f69c4d9fe0c04e64fcef69da0682381ca91d904d972edb`:

| Recovered metadata path | Application copy |
|---|---|
| `resident/kim_packages/KIM1/xlets/1D5347C0-8B5E-11E2-9E96-0800200C9A66/prog/jars/yelp_embedded_10.r4799-FIT.jar` | Yelp |
| `resident/kim_packages/KIM12/xlets/1D5347C0-8B5E-11E2-9E96-0800200C9A66/prog/jars/yelp_embedded_10.r4799-FIT.jar` | Yelp |
| `resident/kim_packages/KIM1/xlets/d0412192-c51d-476c-91e0-76fc65a82692/prog/jars/d0412192-c51d-476c-91e0-76fc65a82692.jar` | iHeart |
| `resident/kim_packages/KIM12/xlets/d0412192-c51d-476c-91e0-76fc65a82692/prog/jars/iHeart.4491_FIT.jar` | iHeart |
| `resident/kim_packages/KIM3/xlets/c1d77320-6335-48b2-aa22-21912f657311/prog/jars/c1d77320-6335-48b2-aa22-21912f657311.jar` | Application Manager |

**PROVED:** A 300-JAR, 72,507-class-occurrence census found one distinct target
class hash and no construction/reference owner other than
`com/tweddle/test/input/CommandSource`. The only recovered construction edge is
`CommandSource.create` bytecode offset 4 to `SocketCommandSource.<init>()`.
There is no recovered call to the `(I)V` or `(Ljava/lang/String;I)V`
constructors and no loaded reflective/configuration string naming the class.

## Type, constructors, and fields

**PROVED:** The class directly extends
`com/tweddle/test/input/CommandSource` and implements no interface. Its fields
are:

| Field | Descriptor | Recovered initialization |
|---|---|---|
| `DEFAULT_LOCAL_ADDRESS` | `Ljava/lang/String;` | constant `127.0.0.1` |
| `DEFAULT_LOCAL_PORT` | `I` | constant `11111` |
| `host` | `Ljava/lang/String;` | constructor field write |
| `port` | `I` | constructor field write |
| `socket` | `Ljava/net/ServerSocket;` | initially null by JVM instance initialization |

**PROVED:** The no-argument constructor writes port `11111` at offset 8 and
host `127.0.0.1` at offset 14. The integer constructor writes its argument to
`port` at offset 6 and loopback to `host` at offset 12. The string/integer
constructor writes its arguments to `port` at offset 6 and `host` at offset 11.
All first invoke `CommandSource.<init>()` at offset 1.

**PROVED:** `CommandSource` declares abstract `initSource`,
`waitForNewCommand`, and `releaseResources`; `resetSource` releases then
reinitializes the source. Its factory creates the no-argument socket source.
The string constant `/tmp/touchInput` remains legacy/static presence; it is not
on the recovered socket factory path.

## Construction, consumption, and lifecycle

**PROVED:** In every containing application, the construction chain is:

```text
concrete Xlet initXlet
  -> com/tweddle/core/AbstractHUXlet.initXlet
  -> AbstractHUXlet.initCommandLooper
  -> CommandLooper.<init>
  -> CommandSource.create
  -> SocketCommandSource.<init>()
```

`AbstractHUXlet.initXlet` invokes private `initCommandLooper` at bytecode offset
154. That method creates a command listener at offset 2, creates
`CommandLooper` at offset 24, and stores it at offset 27. The looper constructor
creates a `CommandListenerWrapper` at offset 22, calls
`CommandTranslator.create` at offset 29, and calls `CommandSource.create` at
offset 36. No conditional branch occurs between the form-registry completion
and the `initCommandLooper` call.

**PROVED:** Normal Xlet start is the listener-start mechanism.
`AbstractHUXlet.startXlet` checks that the stored looper is non-null and calls
`CommandLooper.start`. That method creates an HU thread named
`TGTCore-CommandLooperThread` for the looper `Runnable`, starts it, and records
`started=true`. `CommandLooper.run` reads the abstract `CommandSource` field and
invokes `waitForNewCommand` at offset 19. The census records that virtual call
as a structural superclass-override candidate for the concrete socket source;
it is not mislabeled as a direct invocation.

**PROVED:** `CommandLooper.run` loops until its `stopped` field is true. A false
return from `waitForNewCommand` causes a 1,000 ms sleep; a true return proceeds
to the next loop iteration without that delay. An interrupted sleep is printed
and the loop condition is checked again.

**PROVED:** Normal destroy owns cleanup. `AbstractHUXlet.destroyXlet` calls
`CommandLooper.stop` at offset 22. `stop` writes `stopped=true`, interrupts the
HU thread, clears `started`, and invokes abstract `releaseResources` at offset
21. The concrete override closes the listening `ServerSocket` at offset 27 and
sets its field to null at offset 51.

**PROVED:** The recovered descriptors select concrete main classes
`com.tweddle.yelp.HUXlet`, `com.tweddle.iheart.IHeartPlayerXlet`, and
`com.tweddle.updatemanager.UpdateManagerXlet`. Yelp and Application Manager
explicitly have `xlet.daemon=false`; no examined descriptor declares an
autostart property. Consequently installation/static presence alone is not a
listener-start event.

## Listener behavior

**PROVED:** `initSource` creates an unbound `ServerSocket` at offset 5, enables
`SO_REUSEADDR` at offset 16, creates `InetSocketAddress(host,port)` at offset
35, and calls `ServerSocket.bind(SocketAddress)` at offset 38. Because the
one-argument bind overload is used, no application-supplied backlog is present.
The JVM's effective default backlog is **UNKNOWN** from the application
classfile.

**PROVED:** `getServerSocket` calls `initSource` when the field is null. If the
socket reports unbound, it makes another one-argument bind attempt at offset
40. Both bind regions catch and print exceptions. The method can return a null
or unbound socket after failure; there is no success-shaped fallback.

**PROVED:** `waitForNewCommand` calls blocking `ServerSocket.accept` at offset
6. For one accepted socket it constructs `InputStreamReader` and
`BufferedReader`, calls `readLine` at offset 42, dispatches the line at offset
57, and, only when the dispatcher returns non-null, writes the response plus
one LF, flushes, and closes the writer. It then closes the reader and accepted
socket and returns true. An `IOException` is printed and returns false.

**PROVED:** There is no socket/read timeout and no accept-worker handoff: the
single looper thread blocks in accept and then services one connection at a
time. No `finally` block is present, so an exception after accept may leave the
accepted client or reader unclosed. `releaseResources` closes the listener; it
does not retain a separate field for the current accepted client.

## Protocol and dispatcher

**PROVED:** Framing is one `BufferedReader.readLine()` request per accepted TCP
connection. Both `InputStreamReader(InputStream)` and
`OutputStreamWriter(OutputStream)` use constructors without a charset, so the
encoding is the resident JVM's platform default, which is **UNKNOWN** here.
Non-null responses are terminated with a single LF. The connection is closed
after that request.

**PROVED:** `CommandTranslator.create` constructs `JsonCommandTranslator`.
That translator parses a top-level JSON object, requires string member
`command`, and obtains object member `args`. Recovered command comparisons are:

`touch`, `putText`, `touchListItem`, `itemElement`, `scrollUp`, `scrollDown`,
`getCurrentForm`, `verifyElement`, `getLabelText`, `getListSize`,
`getRuntimeInfo`, `gc`, `setSettings`, `closeKeyboard`, `runUnitTests`, and
`invoke`.

**PROVED:** Response-bearing handlers return JSON objects as follows:

| Command family | Response member |
|---|---|
| `touch`, `verifyElement`, `closeKeyboard` | `status` boolean |
| `getCurrentForm` | `formName` string |
| `getLabelText` | `text` string |
| `getListSize` | `size` integer |
| `getRuntimeInfo` | `free`, `maxMemory`, `totalMemory`, `threadActiveCount` |
| `gc`, `setSettings` | `status=true` |
| `invoke` | `result` object or `error` object/string representation |

**PROVED:** `putText`, `touchListItem`, `itemElement`, `scrollUp`,
`scrollDown`, and `runUnitTests` do not assign a response in the recovered
dispatcher. Unknown commands also fall through with null. A JSON parse/access
exception is caught and printed, leaving the response null. In all of those
cases the socket source writes no acknowledgement; normal cleanup closes the
connection.

**PROVED:** `invoke` performs reflection on the concrete listener-wrapper
object: it resolves a public method by supplied name and the runtime classes of
the supplied argument objects, then invokes that method on the wrapper. It is
not an arbitrary-class loader. Recovered public wrapper capabilities include
UI touch and lookup operations, text/list manipulation, scrolling, current-form
and runtime inspection, settings mutation, keyboard close, dialog display,
thread-state dump, key event delivery, garbage collection, and Xlet unit-test
dispatch. Static presence of a wrapper method is not proof that a particular
JSON argument shape can reach it successfully.

## Gates and evidence ladder

| State | Classification | Bounded conclusion |
|---|---|---|
| Class exists | **PROVED** | Five recovered occurrences, one identical class hash. |
| Code is statically reachable | **PROVED** | Concrete Xlet lifecycle-to-constructor paths and Runnable-to-override consumption candidates are recovered. |
| Activation mechanism exists | **PROVED** | Xlet start calls `CommandLooper.start`; the HU thread runs the accept loop. |
| Activation is configured | **STRONGLY INFERRED** | The three installed-app descriptors select concrete subclasses whose superclass lifecycle creates the looper; no bytecode/config feature gate was found. |
| Enabled in production | **STRONGLY INFERRED, conditional** | The framework is present in recovered production app copies, but the listener depends on one of these non-daemon applications actually being started. |
| Listener can actually execute | **UNKNOWN** | No target run; effective socket permission, policy composition, port availability, and runtime exceptions are unresolved. |
| Listener is externally reachable | **UNKNOWN, with a proved negative boundary** | Default factory bind is IPv4 loopback only. No off-unit route, forwarder, or native correlation has been proved. |

**PROVED:** No command-level authentication, authorization, entitlement,
source-address check, or state gate appears in the recovered source,
translator, or listener wrapper path. The network bind itself limits the
default listener to loopback.

**UNKNOWN:** The descriptors name app-specific `security.policy` plus default
`full.policy`. Small app-policy resources grant selected Harman interface or
AppManager permissions but contain no explicit `java.net.SocketPermission`.
The recovered evidence does not establish how those policies compose for this
code source or whether the bind succeeds under the live policy.

## Answer to the priority question

**STRONGLY INFERRED:** This is genuinely activatable stock code in three normal
resident applications, not merely dormant/unreferenced test residue. Its
activation is application-lifecycle-dependent and its useful recovered
capability is local UI/test automation.

**UNKNOWN:** It is not proved to have executed on a target, and it is not proved
externally reachable. The recovered factory path's loopback-only bind is direct
evidence against treating it as an off-unit network extension mechanism.
