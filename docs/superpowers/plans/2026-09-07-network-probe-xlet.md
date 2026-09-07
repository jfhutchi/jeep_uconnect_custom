# Network Probe Xlet Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and host-prove an independent classfile-major-48 resident-style
Xlet that accepts one bounded ASCII TCP message and returns a fixed
acknowledgement, without making any target-runtime claim.

**Architecture:** `NetworkProbeServer` owns one worker, listening socket and
sequential client I/O; `NetworkProbeXlet` adapts its callbacks to the LWUIT
serial queue; a Java host harness and Python client exercise the production
server over localhost. The deterministic artifact auditor enforces an exact
Java 1.4-era API allowlist in addition to classfile major 48.

**Tech Stack:** Java 1.4 source/target emitted by pinned Temurin JDK 8; Java SE
blocking sockets; recovered Xlet/AWT/LWUIT signatures through independent
compile-only declarations; Python 3 standard library and `unittest`; PowerShell
build orchestration.

---

## File map

- Modify `prototype/hello_uconnect/tools/artifact_tools.py`: add optional generic
  artifact labeling, required-member enforcement and observed API categories
  without changing Hello's defaults.
- Modify `prototype/hello_uconnect/tests/test_artifact_tools.py`: prove the new
  optional audit behavior and unchanged default behavior.
- Create `prototype/network_probe/src/com/jfhutchi/uconnect/networkprobe/`:
  original Xlet, listener and production server classes.
- Create `prototype/network_probe/host_src/com/jfhutchi/uconnect/networkprobe/`:
  host-only process entry point, excluded from the JAR.
- Create `prototype/network_probe/test_support/src/`: executable Xlet/LWUIT
  doubles and a lifecycle race test runner, excluded from the JAR.
- Create `prototype/network_probe/network_probe_client.py`: one bounded
  request/response client.
- Create `prototype/network_probe/tests/test_network_probe.py`: real localhost,
  lifecycle and artifact tests.
- Create `prototype/network_probe/build.ps1`, `.gitignore`, `toolchain.json`,
  `api-allowlist.json` and `descriptor/xlet.properties`: reproducible build and
  exact compatibility policy.
- Create `prototype/network_probe/README.md` and `docs/network_probe_xlet.md`:
  operation, evidence, exact verification and target-only unknowns.

## Task 1: Make the artifact audit describe intentional APIs

**Files:**

- Modify: `prototype/hello_uconnect/tests/test_artifact_tools.py`
- Modify: `prototype/hello_uconnect/tools/artifact_tools.py`

- [x] **Step 1: Write failing optional-policy tests**

Add tests that construct a synthetic major-48 class referencing
`java/net/ServerSocket.<init>()V` and assert this policy behavior:

```python
policy["artifact_label"] = "Uconnect Network Probe host artifact"
policy["required_members"] = [
    ["java/net/ServerSocket", "<init>", "()V"],
]
policy["observed_owner_prefixes"] = {"networking": ["java/net/"]}
report = audit_artifact(jar, descriptor, policy_path)
self.assertEqual(report["artifact"]["label"], policy["artifact_label"])
self.assertEqual(report["dependencies"]["observed_api_references"], {"networking": 1})
```

Add a second assertion that a missing required member raises
`ValidationError` containing `required API member`. Retain a test proving the
Hello policy's absent optional fields still yields its current label and report
shape.

- [x] **Step 2: Run the focused test and observe RED**

Run:

```powershell
& $Python -m unittest prototype.hello_uconnect.tests.test_artifact_tools -v
```

Expected: the new test fails because `artifact_label`, `required_members` and
`observed_owner_prefixes` are not implemented.

- [x] **Step 3: Implement the minimal generic audit extension**

In `audit_artifact`, parse optional required-member and observed-prefix policy
fields, compare required triples to `all_member_references`, count unique
referenced members by configured owner prefix, and add only these fields:

```python
report["artifact"]["label"] = policy.get(
    "artifact_label", "Hello Uconnect host artifact"
)
report["dependencies"]["observed_api_references"] = observed_counts
```

Raise a deterministic error naming the first sorted missing required member.
Use the report label in `write_reports`; append sorted observed-category counts
only when configured. Existing Hello values remain unchanged; review clarifies
the legacy networking count as `prohibited_networking_references`, and JSON
intentionally adds an empty `observed_api_references` mapping when none exist.

- [x] **Step 4: Run focused and full existing tests to GREEN**

Run the focused Hello suite, then `unittest discover -s analysis_tools/tests`.
Expected: 16+ focused tests and 195 analysis tests pass with zero failures.

## Task 2: Prove the bounded production TCP protocol

**Files:**

- Create: `prototype/network_probe/tests/test_network_probe.py`
- Create: `prototype/network_probe/host_src/com/jfhutchi/uconnect/networkprobe/NetworkProbeHost.java`
- Create: `prototype/network_probe/src/com/jfhutchi/uconnect/networkprobe/NetworkProbeListener.java`
- Create: `prototype/network_probe/src/com/jfhutchi/uconnect/networkprobe/NetworkProbeServer.java`
- Create: `prototype/network_probe/network_probe_client.py`

- [x] **Step 1: Write failing real-socket tests**

The Python suite compiles the Java server and host entry point with
`-source 1.4 -target 1.4`, starts `NetworkProbeHost 0`, reads its `PORT <n>`
line, and asserts:

```python
self.assertEqual(run_client(port, "HELLO FROM PHONE"), "HELLO FROM UCONNECT")
self.assertEqual(raw_exchange(port, b"A" * 257 + b"\n"), b"ERROR MESSAGE TOO LONG\n")
```

Add separate tests for LF and CRLF, exactly 256 payload bytes, non-ASCII and
control-byte rejection, two sequential clients, disconnect before LF, stop
while blocked in `accept()`, stop while blocked in client `read()`, and repeated
stop. Each server process must exit within three seconds and expose no stack
trace.

Add Python-client tests for one successful exchange, a message over 256 encoded
ASCII bytes, non-ASCII input, timeout and connection refusal. Errors must be
bounded and produce a nonzero CLI exit.

- [x] **Step 2: Run the probe suite and observe RED**

Run:

```powershell
& $Python -m unittest discover -s prototype/network_probe/tests -v
```

Expected: compilation/import fails because the production server and client do
not exist.

- [x] **Step 3: Implement the minimal server and client**

`NetworkProbeListener` exposes only:

```java
void onState(String state, String detail);
void onMessage(String clientAddress, String message, int receivedCount);
```

`NetworkProbeServer` uses `new ServerSocket()`, `setReuseAddress(true)`,
`bind(new InetSocketAddress(port))`, one named `Thread`, sequential `accept()`,
a 5000 ms client timeout and byte-at-a-time reads into a fixed 257-byte array.
It accepts printable ASCII only, strips one CR immediately before LF, rejects
and closes on overflow, writes fixed US-ASCII replies, and never retries within
a malformed connection. `stop()` is synchronized/idempotent, sets a volatile
flag and closes the active client and listening socket. `awaitStopped(long)` is
host-observation only and never called by the Xlet UI path.

`NetworkProbeHost` prints only `PORT <actualPort>`, waits for `STOP` on stdin,
calls `stop()`, requires bounded worker termination, and exits nonzero if the
worker remains alive. The Python client validates its encoded byte count before
connecting, sends LF, reads one bounded reply line and reports timeout/refusal
without a traceback.

- [x] **Step 4: Run protocol tests to GREEN**

Run the focused Python suite. Expected: every socket, client-error and shutdown
case passes using the production Java server.

## Task 3: Integrate the Xlet lifecycle and serialized UI safely

**Files:**

- Create: `prototype/network_probe/test_support/src/javax/microedition/xlet/*.java`
- Create: `prototype/network_probe/test_support/src/com/sun/lwuit/**/*.java`
- Create: `prototype/network_probe/test_support/src/com/jfhutchi/uconnect/networkprobe/NetworkProbeLifecycleTest.java`
- Create: `prototype/network_probe/src/com/jfhutchi/uconnect/networkprobe/NetworkProbeXlet.java`

- [x] **Step 1: Write the failing lifecycle race runner**

Executable host doubles implement only the already recovered declarations.
Their `Display.callSerially` queues runnables until the test explicitly drains
them, and `Label` records bounded mutations. The Java runner asserts:

```java
xlet.initXlet(context);
xlet.startXlet();
Display.runNext();                 // construct UI and start server
listenerEventArrives();            // callback is queued, not applied directly
xlet.destroyXlet(true);
xlet.destroyXlet(true);            // idempotent
Display.runAll();                  // queued pre-destroy callback is inert
assertNoPostDestroyLabelMutation();
```

Also assert Stop calls `notifyDestroyed()` once, all UI mutations occur while
the fake display is draining its serial queue, and destruction never starts a
new worker.

- [x] **Step 2: Run the lifecycle test and observe RED**

Run the Python test that compiles/runs `NetworkProbeLifecycleTest`. Expected:
failure because `NetworkProbeXlet` is absent.

- [x] **Step 3: Implement the smallest Xlet UI adapter**

Follow Hello's exact initialization pattern. Use the existing recovered
`Form`, `Label`, `Button` and `BorderLayout` surface. Display the requested
fields in bounded label text without introducing an unproved widget. Every
worker callback captures immutable strings and queues a `Runnable`; the
runnable checks `destroyed` before touching any label. Stop calls server
`stop()` and `XletContext.notifyDestroyed()`; destroy marks `destroyed` before
closing sockets and clearing references. No network wait or join occurs on the
LWUIT thread.

- [x] **Step 4: Run lifecycle and protocol tests to GREEN**

Expected: queued-callback, repeated-destroy, Stop and real-socket tests all pass.

## Task 4: Build and audit the non-installable Xlet artifact

**Files:**

- Create: `prototype/network_probe/.gitignore`
- Create: `prototype/network_probe/toolchain.json`
- Create: `prototype/network_probe/api-allowlist.json`
- Create: `prototype/network_probe/descriptor/xlet.properties`
- Create: `prototype/network_probe/build.ps1`
- Extend: `prototype/network_probe/tests/test_network_probe.py`

- [x] **Step 1: Add failing artifact acceptance tests**

Run the build from a clean generated directory and require:

```python
self.assertEqual(bytecode["application_classfile_majors"], [48])
self.assertEqual(bytecode["native_methods"], 0)
self.assertEqual(bytecode["invokedynamic_references"], 0)
self.assertIn("java/net/ServerSocket", observed_network_owners)
self.assertNotIn("NetworkProbeHost.class", jar_members)
```

Require the exact expected application member set, absence of compile stubs,
vendor runtime/native/JNI/USB/vehicle/AppManager references, safe descriptor
flags, and deterministic JAR bytes across two builds. Inject a synthetic
Java-6+ `java/util/concurrent` reference and prove the exact API allowlist
rejects it even when its classfile major is 48.

- [x] **Step 2: Run the artifact test and observe RED**

Expected: failure because the build, policy and descriptor do not exist.

- [x] **Step 3: Implement the build and compatibility policy**

Pin `javac 1.8.0_504`, compile with `-source 1.4 -target 1.4 -encoding
US-ASCII`, compile shared independent Xlet/LWUIT declarations to a temporary
classpath, compile only `src` into application classes, compile `host_src` only
to a separate host directory, and package only application classes into
`network-probe-xlet.jar` through the deterministic artifact tool.

Use logical app ID `29a0ee8d-04e9-5a2f-a4da-ee29d3b488d3`, derived with UUIDv5
from `https://github.com/jfhutchi/jeep_uconnect_custom/network-probe-xlet`.
Descriptor fields remain GUI true, headless/daemon/audio false, no autostart and
no privilege field. The exact API policy allows only members used by the
compiled source, requires the networking/lifecycle members central to the
probe, and records observed `java/net/` references rather than prohibiting
them. `build/` is the only generated directory and is ignored.

- [x] **Step 4: Run artifact and regression tests to GREEN**

Run two clean builds, compare JAR SHA-256 and inventory, run the complete probe,
Hello, analysis and resident-HMI suites, and require no warnings other than the
known JDK 8 bootstrap warning from `-source 1.4` if the pinned compiler emits
it.

## Task 5: Record evidence and exact reproduction

**Files:**

- Create: `prototype/network_probe/README.md`
- Create: `docs/network_probe_xlet.md`

- [x] **Step 1: Write the focused documentation**

Record the goal, ASCII byte protocol, architecture diagram, worker/UI ownership,
shutdown behavior, exact build/client/test commands, actual classfile major,
actual JAR inventory/hash, and actual localhost transcript. Include explicit
`PROVED`, `STRONGLY INFERRED`, `UNKNOWN` and `DISPROVED` sections.

- [x] **Step 2: Preserve the target boundary**

Document but do not execute the seven-step authorized target experiment from
the design. State that localhost behavior cannot establish bind permission,
interface visibility, firewalling, hotspot isolation, routing, AMS policy or
phone reachability. Describe only the later custom-projection phase sequence;
do not claim CarPlay or Android Auto compatibility.

- [x] **Step 3: Run documentation sanity checks**

Check relative links, ASCII encoding, placeholders, generated values against
fresh build reports, and source wording for any claim that implies target
execution.

## Task 6: Final verification, review, commit and push

**Files:** All intentional network-probe and shared-auditor files from Tasks 1-5.

- [x] **Step 1: Run a fresh verification pass**

Run the complete relevant tests, clean build twice, JAR inventory, classfile
audit, localhost round-trip, overlong/disconnect/shutdown cases, `git
diff --check`, `git status --short`, `git diff --stat` and full `git diff`.
Search the untracked/staged set for proprietary binaries, firmware, images,
certificates, keys, extracted OEM JARs and large blobs. Generated build output
must remain ignored and unstaged.

- [x] **Step 2: Review as an upstream maintainer**

Check newer APIs, UI-thread access, accept/read/destroy races, socket/thread
leaks, unbounded reads/errors, dead code, speculative abstractions, proprietary
material, test-only production hooks and evidence overstatement. Correct every
Critical or Important finding and rerun verification.

- [ ] **Step 3: Stage with explicit paths and inspect the index**

Use one `git add --` command that enumerates every intentional pathname and no
wildcard. Before commit run exactly:

```powershell
git status --short
git diff --cached --stat
git diff --cached --name-only
git diff --cached
git diff --cached --check
```

- [ ] **Step 4: Create the focused implementation commit**

Commit with subject `Add independent RA4 Xlet network probe`. Do not amend,
merge or touch the original worktree.

- [ ] **Step 5: Push only the isolated branch**

Push `codex/network-probe-xlet` to `origin`, verify the remote SHA, leave the
worktree available for review, and report exact evidence without claiming the
probe worked on Uconnect hardware.
