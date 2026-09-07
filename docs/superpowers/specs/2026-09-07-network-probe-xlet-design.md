# Network Probe Xlet Design

Date: 2026-09-07. Approved by the owner on 2026-09-07. This design is
host-only. It does not authorize target installation, signing, registration,
execution, vehicle access, firmware modification or security-policy changes.

## Goal

Build an independently authored, non-installable resident-style Xlet that asks
one narrow question: can the RA4 resident Java environment plausibly use
ordinary TCP/IP to exchange one bounded text message and acknowledgement with
another device through networking hardware already present in the radio?

The software-side result is acceptable when the exact Java server logic builds
as classfile major 48, passes localhost behavioral tests, and is packaged in an
audited application-only JAR. Target runtime permission, interface visibility
and network reachability remain separate dynamic questions.

## Evidence basis

The implementation is original. Recovered artifacts are used only as static
compatibility evidence and are never copied into the application.

### Proved static evidence

- The recovered resident application JAR with SHA-256
  `587c06e2152f0f99b6a4a798926147101484876b0995a58f6a5196bc31205c0d`
  contains `com/tweddle/test/input/SocketCommandSource.class` with SHA-256
  `55bf4d4ca3872b4434f69c4d9fe0c04e64fcef69da0682381ca91d904d972edb`.
- A bounded invocation inventory of that class resolves calls to ordinary
  `java.net.ServerSocket`, `Socket`, `InetSocketAddress`, `accept()`, socket
  input/output streams, a text acknowledgement, flush and socket cleanup.
- Other recovered resident JAR classes statically reference
  `java.net.InetAddress`.
- Existing repository evidence proves stock Xlet lifecycle, AWT container and
  LWUIT calls used by the independent Hello artifact: `getContainer()`,
  `Container.setVisible(true)`, `Display.init`, `Display.callSerially`,
  `Form.show` and `XletContext.notifyDestroyed()`.
- Selected stock application classfiles use majors 48 and 49. The existing
  conservative host build emits major 48 from Java 1.4 source/target mode.

These facts prove symbols and calls in recovered application code, not that a
new application identity receives the same runtime permissions or topology.

### Strongly inferred

- The resident runtime plausibly supplies the ordinary Java networking surface
  referenced by its recovered applications.
- A small Java 1.4-style server using the same API family is a reasonable
  minimum experiment for the remaining runtime and network-policy question.
- Closing the listening and active client sockets is the simplest portable way
  to release blocking I/O during Xlet shutdown.

### Unknown until target execution

- Whether this independently authored Xlet can be authorized and executed.
- Whether AMS or application policy grants it networking permission.
- Whether socket creation and binding succeed for this application identity.
- Which network interfaces and addresses the Xlet can see.
- Firewall, packet-filtering and address-binding behavior.
- Hotspot or Wi-Fi peer-to-radio reachability from a phone or PC.
- Whether any additional legitimate permission declaration is required.

## Architecture

```text
phone/PC client
      |
  bounded TCP line
      |
NetworkProbeServer worker
      |
NetworkProbeXlet callbacks
      |
LWUIT serial UI queue
```

`NetworkProbeServer` contains the production socket and protocol behavior. It
has no LWUIT or Xlet dependency, so a small Java host harness can execute the
same class over localhost. `NetworkProbeXlet` adapts server events to the
recovered resident lifecycle and LWUIT display. The Python client is an
independent standard-library peer used by both automated and manual host tests.

The Xlet artifact remains separate from Hello. It may reuse the repository's
independently authored compile-only Xlet/LWUIT declarations and deterministic
host artifact tooling as build inputs. Compile declarations remain outside the
application JAR.

## Components

- `NetworkProbeXlet`: lifecycle, minimal screen, Stop action and serialized UI
  updates.
- `NetworkProbeServer`: one listening socket, one worker thread, sequential
  clients, bounded protocol handling and idempotent shutdown.
- `NetworkProbeListener`: small callback contract between the worker and Xlet.
- `NetworkProbeHost`: host-only entry point that starts the production server
  and supports deterministic shutdown testing; it is not packaged in the Xlet
  JAR.
- `network_probe_client.py`: dependency-free client for one request/response.
- Build and validation inputs: pinned JDK 8, Java 1.4 source/target, exact API
  allowlist, logical unsigned descriptor and deterministic JAR audit.

## Protocol

The server listens on TCP port 8888 by default. Tests may supply an ephemeral
port. A client sends one line containing 1 to 256 printable ASCII bytes,
terminated by LF; a preceding CR is accepted as the CRLF terminator. The
success reply is exactly `HELLO FROM UCONNECT\n`.

The server reads at most 257 payload bytes so it can distinguish the maximum
valid message from an overlong one without unbounded buffering. Overlong input
receives `ERROR MESSAGE TOO LONG\n`. Empty, incomplete or non-printable input
receives a bounded diagnostic error when a reply is still possible. Each client
has a finite read timeout. One connection carries one request and one response,
then closes. The service can accept later clients sequentially.

No payload is deserialized or executed. The service has no filesystem,
process, native, vehicle, CAN, diagnostic, GPS, projection, audio, microphone,
camera, USB, Bluetooth, persistence, AppManager or firmware behavior.

## Lifecycle and threading

`initXlet` obtains and exposes the AWT container and initializes LWUIT.
`startXlet` queues form construction through `Display.callSerially` and starts
the server once. `pauseXlet` leaves lifecycle ownership to the platform and does
not create another worker. `destroyXlet` stops the server idempotently and drops
UI/context references.

The single server worker owns `ServerSocket.accept()`, client read/write and
socket closure. It never mutates LWUIT components. Listener callbacks from the
worker immediately enqueue a small `Runnable` with `Display.callSerially`; only
that LWUIT serial queue updates labels and message counts.

Shutdown sets a volatile stop flag and closes both the current client and
listening socket. This is intended to release `read()` or `accept()` without an
unbounded UI-thread join. The host harness exposes a bounded wait used only by
tests to prove that the worker actually terminates.

## UI and errors

The screen shows `Uconnect Network Probe`, state, port, discovered local address
or `unavailable`, last client, last message, received count and a Stop button.
States are `LISTENING`, `CONNECTED`, `RECEIVED` and `ERROR`. Errors expose only
a bounded exception class/message suitable for diagnosis; payloads and error
text are length-bounded before display.

`InetAddress.getLocalHost().getHostAddress()` is a diagnostic hint only. It may
return an unusable, loopback or otherwise incomplete address. Failure displays
`unavailable`; the application never invents or hardcodes a target IP address.

## Host verification

Tests execute the production Java server on localhost and use the Python client
or raw standard-library sockets to verify:

- `HELLO FROM PHONE` receives `HELLO FROM UCONNECT`;
- multiple sequential clients work;
- input over 256 bytes is rejected without unbounded buffering;
- an incomplete clean disconnect does not terminate the service;
- stop closes blocking sockets and the worker exits within a bounded wait;
- the Xlet source compiles with the pinned ordinary JDK 8 compiler;
- every application class is classfile major 48;
- the deterministic JAR contains only expected original application classes;
- compile-only declarations, host harness, native code and unrelated artifacts
  are absent from the JAR.

Localhost success proves the independently authored Java design and client can
communicate. It does not prove RA4 permission, execution or reachability.

## Target experiment boundary

No target step is executed in this work. Once a legitimate installation and
execution mechanism exists, the minimum separate experiment is:

1. Launch an authorized copy of `NetworkProbeXlet`.
2. Verify the UI reaches `LISTENING` on port 8888.
3. Connect a phone or PC through the RA4 network using legitimate, read-only
   address discovery.
4. Send `HELLO FROM PHONE` with the host client.
5. Verify the Xlet displays the message and increments its count.
6. Verify the client receives `HELLO FROM UCONNECT`.
7. Stop the Xlet and verify normal lifecycle cleanup.

No signing bypass, credential use, trust modification, installation work,
vehicle command or firmware modification belongs to that procedure.

## Acceptance

The change is acceptable only if the isolated branch starts clean at
`894afe8`, focused and baseline tests pass, the build and bytecode audit pass,
the JAR is major 48 and application-only, the host round-trip and failure cases
pass, documentation preserves PROVED / STRONGLY INFERRED / UNKNOWN, and the
final staged diff contains only intentional network-probe files. The generated
JAR remains ignored and uncommitted.
