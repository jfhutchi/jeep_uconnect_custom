# Independent RA4 Xlet Network Probe

Date: 2026-09-07. This report covers host construction and verification only.
It does not report a target installation or RA4 execution result.

## Goal

The probe asks one narrow experimental question: can an independently authored
resident-style Xlet bind a TCP socket on RA4, accept one bounded ASCII line
from another device, acknowledge it and stop without blocking the LWUIT UI?

This change answers the software-side prerequisites on a host. The target-side
question remains open until the separate authorized experiment is performed.

## Static Evidence Basis

The recovered RA4 resident application JAR with SHA-256
`587c06e2152f0f99b6a4a798926147101484876b0995a58f6a5196bc31205c0d`
contains `com/tweddle/test/input/SocketCommandSource.class` with SHA-256
`55bf4d4ca3872b4434f69c4d9fe0c04e64fcef69da0682381ca91d904d972edb`.
A bounded static invocation inventory resolves ordinary `java.net` references
including `ServerSocket`, `Socket`, `InetSocketAddress`, `accept()`, socket
input/output streams, acknowledgements, flush and cleanup. Other resident JAR
classes statically reference `InetAddress`.

Those findings prove that recovered resident code refers to those APIs. No
recovered implementation, proprietary binary, credential or target package is
copied into this probe, and the evidence does not prove that a new application
identity receives permission to use the same APIs.

## Implementation

```text
phone/PC client
      |
bounded ASCII TCP line
      |
NetworkProbeServer worker
      |
NetworkProbeListener events
      |
LWUIT Display.callSerially queue
      |
NetworkProbeXlet labels and Stop button
```

`NetworkProbeServer` is the production networking implementation used by both
the Xlet and host tests. Its single named worker owns `accept()`, client I/O
and socket lifetime. It uses a fixed 257-byte buffer, a 5000 ms client read
timeout and one request per connection. It serves clients sequentially.

The accepted payload is 1 to 256 printable ASCII bytes followed by LF. CRLF is
accepted by removing one terminal CR. Success is exactly
`HELLO FROM UCONNECT\n`; overflow is exactly
`ERROR MESSAGE TOO LONG\n`. Empty or non-printable input receives a bounded
error when a reply remains possible. Malformed connections are closed rather
than recovered as an open-ended stream.

`NetworkProbeXlet` initializes the recovered AWT/LWUIT surface and queues all
widget creation and mutation through `Display.callSerially`. Worker callbacks
capture bounded strings and queue UI work; queued callbacks recheck destruction
before touching a label. The worker never mutates a widget directly.

Shutdown is idempotent and socket-driven. It marks the service stopped and
closes the active client and listening socket to release a blocking `read()` or
`accept()`. The Xlet UI path never joins the worker. A host-only bounded wait
exists solely to test termination.

The Xlet has no vehicle, CAN, diagnostic, GPS, projection, audio, microphone,
camera, USB, Bluetooth, persistence, installer, signer, AppManager privilege,
native-code or firmware function.

## Reproduction

From the repository root in PowerShell:

```powershell
$Python = "C:\path\to\python.exe"
$JdkHome = "C:\Program Files\Eclipse Adoptium\jdk-8.0.504.1-hotspot"
$env:NETWORK_PROBE_JDK_HOME = $JdkHome

& $Python -m unittest discover -s prototype/network_probe/tests -v
& prototype/network_probe/build.ps1 -JdkHome $JdkHome -Python $Python
Get-Content prototype/network_probe/build/out/BUILD-STATUS.txt
Get-Content prototype/network_probe/build/out/SHA256SUMS
Get-Content prototype/network_probe/build/out/jar-inventory.txt
```

The build uses Eclipse Temurin `javac 1.8.0_504` with `-source 1.4 -target
1.4 -encoding US-ASCII`. Compile-only Xlet/LWUIT declarations are placed on a
temporary classpath. Host classes are compiled to a separate directory. Only
application classes are packaged in the deterministic JAR.

## Measured Host Results

The direct localhost transcript from 2026-09-07 was:

```text
PORT 6512
CLIENT HELLO FROM PHONE
HELLO FROM UCONNECT
client_exit=0
server_exit=0
server_stderr=''
```

The port was dynamically selected and is not a target address. Automated tests
also cover LF, CRLF, exactly 256 bytes, 257-byte overflow, empty/control/
non-ASCII rejection, sequential clients, incomplete disconnect, shutdown while
blocked in `accept()`, shutdown while blocked reading a client, repeated stop,
client timeout/refusal, and lifecycle callback/destroy races.

The audited artifact measured:

- JAR: `network-probe-xlet.jar`, 19,027 bytes.
- SHA-256: `0145c942436f9384d833bc6e85e400c6871964df6419969cda5ebd2818df7f8f`.
- Application classes: 7; every classfile major is 48.
- Native methods: 0; `invokedynamic` references: 0.
- Observed exact `java.net` member references: 14.
- Compile stubs, vendor runtime classes and custom native libraries: 0.
- JNI, USB, vehicle-service and AppManager privilege references: 0.
- Unexpected API references: 0.

Exact JAR membership:

```text
com/jfhutchi/uconnect/networkprobe/NetworkProbeListener.class
com/jfhutchi/uconnect/networkprobe/NetworkProbeServer.class
com/jfhutchi/uconnect/networkprobe/NetworkProbeXlet$1.class
com/jfhutchi/uconnect/networkprobe/NetworkProbeXlet$2.class
com/jfhutchi/uconnect/networkprobe/NetworkProbeXlet$3.class
com/jfhutchi/uconnect/networkprobe/NetworkProbeXlet$4.class
com/jfhutchi/uconnect/networkprobe/NetworkProbeXlet.class
```

The exact-member policy also has a negative test: synthetic classfile-major-48
code referencing `java.util.concurrent.Executor.execute` is rejected. This
guards against the false assumption that major 48 alone prevents use of APIs
introduced after Java 1.4.

The output status is deliberately:

```text
HOST-BUILT / UNSIGNED / NOT INSTALLABLE ON TARGET
```

Authorized live package issuance, signer, principal/policy and DRM grant are
unresolved.

## Evidence Classification

### PROVED

- Recovered resident application code statically references the ordinary
  `java.net` networking API family described in the static evidence basis.
- The independently authored production server passes bounded localhost
  protocol and shutdown tests on the host.
- Xlet lifecycle tests serialize UI updates and make queued callbacks inert
  after destruction using executable host doubles.
- The deterministic application-only JAR has the measured hash and inventory,
  uses classfile major 48 and passes the exact API/member audit.
- The JAR contains no host harness, compile declarations, native code,
  proprietary recovered class or vehicle/USB/AppManager dependency.

### STRONGLY INFERRED

- The RA4 resident runtime plausibly supplies the ordinary Java networking
  surface because recovered resident applications reference it.
- Socket closure is the appropriate portable mechanism for releasing the
  probe's blocking `accept()` and `read()` operations during shutdown.
- The host-tested server is a narrow, useful target experiment because the same
  production networking class is packaged with the Xlet.

### UNKNOWN

- Whether this independently authored Xlet is granted networking permission.
- Whether it actually executes on the target.
- Whether socket creation and binding succeed for its application identity.
- Which interfaces and addresses are visible or usable.
- Firewall, packet-filtering and address-binding behavior.
- Hotspot/Wi-Fi routing, client isolation and phone/PC reachability.
- Whether AMS or application policy constrains networking or requires an
  additional legitimate permission declaration.

### DISPROVED

- Host success does not prove target execution, target bind permission or
  phone-to-RA4 reachability.
- Classfile major 48 by itself is not sufficient API-compatibility evidence;
  the negative exact-member test demonstrates why a separate API audit is
  required.
- The generated output is not an installable or signed RA4 package.

## Separately Authorized Target Experiment

No target step was executed by this implementation. After a legitimate
installation and execution mechanism is independently available:

1. Launch an authorized copy of `NetworkProbeXlet` without changing firmware,
   trust policy or credentials.
2. Verify that its UI reports `LISTENING` on port 8888; otherwise record the
   bounded error verbatim and stop.
3. Use legitimate, read-only address discovery to identify the reported RA4
   address and connect a phone or PC through the intended network path.
4. Send `HELLO FROM PHONE` as printable ASCII followed by LF or CRLF.
5. Verify that the Xlet shows the client/message and increments its count.
6. Verify that the peer receives exactly `HELLO FROM UCONNECT` followed by LF.
7. Press Stop and verify normal lifecycle cleanup and loss of reachability.

Each step should record its own observation. A bind success would not by itself
prove peer reachability; a visible address would not prove routing; a failed
connection would not distinguish firewalling from client isolation without a
separate measurement.

## Later Work Boundary

Only after the target networking proof succeeds should later work consider a
custom projection transport: characterize topology, authenticate the peer,
define a bounded framed protocol, prototype a non-vehicle screen, measure
latency/reconnect behavior, add explicit lifecycle controls, and perform a
separate security review. Nothing here claims Apple CarPlay, Android Auto or
any OEM projection compatibility.
