# Stock RA4 signed capability analysis

Original research date: 2026-09-07; revalidated and reconciled with the completed
KIM19 research on 2026-09-09. Evidence is recovered RA4 18.45.01 software and
repository evidence only. No recovered executable or target command was executed.

## Current KIM19 result and audit provenance

**PROVED:** the supplied part number `68224525AM` normalizes to `68224525` and
selects **KIM19** at line 74 of the recovered map. The target part number is
provided, not an outstanding unknown. The actual installed versions, historical
retained packages, effective grants and service state remain **UNKNOWN**.

**PROVED bounded negative:** the recovered ordinary KIM19 installation does
not select any of the five socket-containing copies. They are real, conditionally
activated test/UI code in older signed application packages, not dead classes.
Category **3**, excluded by recovered production package selection, describes
the supplied installation path. Category **4** describes their static lifecycle
path if an exact older copy is already legitimately installed. Category **8**
describes unresolved live target state. Neither successful bind nor an
externally reachable running service has been observed.

The evidence ladder must be read as separate claims:

| Claim | Classification | Evidence or remaining boundary |
|---|---|---|
| Class exists and has public constructors | PROVED | Five copies, one class hash; three constructors |
| A stock caller constructs it when reached | PROVED | `CommandSource.create`, `new` BCI 0 / constructor BCI 4 |
| Old Xlet init/start reaches the construction/worker path | PROVED direct sites; STRONGLY INFERRED indirect dispatch | Section A graph; descriptor/lifecycle/thread receiver flow |
| Target actually constructs it or starts the worker | UNKNOWN | Package/history, authorization and lifecycle not observed |
| Default code requests loopback bind on 11111 | PROVED | Section B constructor-to-field-to-bind provenance |
| Bind succeeds on the target | UNKNOWN | Runtime policy, socket implementation, port and worker state |
| An off-unit peer can reach it | UNKNOWN | No recovered forwarder establishes that path; wildcard default is DISPROVED |

The later [KIM19 assessment](kim19_final_capability_assessment.md),
[Yelp dataflow](kim19_yelp_input_dataflow.md), and
[Performance export analysis](performance_pages_file_write_capability.md)
close several candidates that were still unresolved in the original broad
census. The useful ranking for this request is:

| Rank | Candidate | Supported capability | Remaining boundary |
|---:|---|---|---|
| 1 | Normal Apps launch of KIM19 Yelp 03.00.33 | Existing splash/home/category UI before a Yelp search request | Installed/visible/authorized app, lifecycle, platform services |
| 2 | Performance Pages timer export | Fixed USB/SD `timersResult` HTML output through stock UI | Correct vehicle variant, app grants, existing timer state, writable/durable media |
| 3 | Typed stock service handoffs | Existing Apps/AppManager/AMS and finite IXC/VSB operations | Actual remote bindings, caller permissions and service state; many operations are not benign |
| 4 | Yelp search/result display | Typed HTTPS request/JSON response and stock result UI | Network/account/backend/schema; no service contacted in this work |
| 5 | Historical Tweddle UI/VM queries | `getCurrentForm` / `getRuntimeInfo` implementations | Exact older installed copy, loopback client, policy, bind and worker; excluded from ordinary KIM19 |

**Strongest benign no-new-signature proof candidate:** observe an existing Yelp
UI through its normal authorized Apps launch, if already visible. This is a
conditional proposal, not a target-tested result or an assertion of zero
background traffic: platform/VR/service initialization and other running stock
services prevent a global network-silence guarantee. No target interaction is
part of this research. Performance's ordinary export is the strongest separate
offline data-output candidate, but its success UI alone does not prove bytes
were written: a filename collision skips writing and can still report success.
No new timer driving or vehicle action is required or proposed here.

No recovered KIM19 path establishes user-controlled general class loading,
scripting, process launch, or a reusable external command interface. That is a
bounded result for the examined artifacts, not a universal absence claim about
unrecovered native/AOT code or historical target state. Fixed factories,
packaged native loading, typed IXC/VSB callbacks and ordinary file export remain
stock capabilities, with their existing policy boundaries intact.

This audit created `codex/stock-signed-capability-audit` in
`E:/Documents/GitHub/jeep_uconnect_custom_stock_signed_audit` from the requested
network-probe commit `be5a83be9fc52493ed04070abac12531c6c6b901`, then fast-forwarded
only that new worktree to existing committed research checkpoint
`5b9826b2b6537f12b4bf08a50003ea6914263700`. Other worktrees were left untouched.
The original investigation's state table below is historical provenance.

Fresh validation: **305 analysis tests passed**, full 300-JAR index regeneration
matched the committed JSON content, and all seven selected report/source check
commands passed. Source-addressed graphs, listener/protocol tables and extension
inventories remain in the linked evidence set; they were reused rather than
duplicated. The [audit record](../reports/stock_signed_capability/audit_20260909.json)
and [reproduction record](../reports/stock_signed_capability/audit_20260909.md)
distinguish fresh checks from inherited findings and preserve exact identities.

## Result

**PROVED:** `SocketCommandSource` has a real construction, Xlet lifecycle, worker,
parser, and UI-handler path in five archived application copies. It is not an
unreferenced class. **PROVED:** its only recovered factory chooses
`127.0.0.1:11111`, not a wildcard or vehicle/Wi-Fi address.

**PROVED:** an additional, earlier gate prevents those copies from being selected
by the recovered stock installer configuration. They occur only in **KIM1,
KIM3, and KIM12**. None is a value in the shipped `kim_pkg_map.lua` (289
assignments, 285 distinct part numbers, with last-assignment semantics). The
installer reads the radio part number, looks it up in that map, and copies the
selected package into `kona/preload`. Its missing-entry fallback is KIM0, not
one of the three socket-containing packages.

The best classification is **3: production code but disabled by configuration**,
specifically **excluded by the recovered package-selection configuration**.
This classification concerns the supplied update's ordinary installation path.
**UNKNOWN:** a particular radio's existing installed applications, previous
catalog downloads, historical firmware, or other installation history. If one
of these exact older copies is already legitimately installed, its code has a
**4: conditionally reachable** lifecycle path, still loopback only. There is no
evidence for **6** (a listener actually started) or **7** (production external
interface reachability). The target's runtime state remains **8: unresolved**.

**DISPROVED:** the hypothesis that ordinary selection of a currently mapped KIM
installs one of these five copies. **DISPROVED:** the hypothesis that the
recovered no-argument construction binds all network interfaces. The stronger
claims that this class could never run on any RA4, or that it is globally
unreachable under every historical installation state, are **UNKNOWN**.

No new-signature general-purpose extension or off-unit benign command interface
is established. The strongest usable stock mechanism in the evidence is the
normal **Apps-menu launch of an already installed and authorized application**.
The best *conditional protocol* proof is `getRuntimeInfo` or `getCurrentForm`,
but package presence, successful bind, and an existing authorized local client
are missing prerequisites. Do not change selection, policy, or installation to
make that experiment possible.

## Evidence labels and starting state

- **PROVED:** a directly recovered structure, instruction, configuration value,
  or source-addressed repository finding. A proved call site is not a proved run.
- **STRONGLY INFERRED:** concrete data flow supports an indirect dispatch or
  activation, but runtime resolution remains unobserved.
- **UNKNOWN:** evidence does not establish the claim.
- **DISPROVED:** recovered evidence contradicts the specified bounded hypothesis.

The original checkout was inspected before any mutation:

| Item | Recorded state |
|---|---|
| Original worktree | `E:/Documents/GitHub/jeep_uconnect_custom` |
| Original branch | `codex/ra4-driver-temperature` |
| Original HEAD | `894afe8e5361c3595623de599e62ba0f0c0d9f78` |
| Unrelated changes | 40 tracked modifications and untracked `docs/00_project_status.md`; left untouched |
| Research worktree | `E:/Documents/GitHub/jeep_uconnect_custom_stock_signed_capability` |
| Research branch | `codex/stock-signed-capability-analysis` |
| Research start commit | `6f243b56de46ab6648e3db1198f1f6bf627e1352` |
| Starting cleanliness | Clean new worktree, no unrelated modifications |
| Base rationale | Existing clean stock-extension research, descendant of completed network-probe commit `be5a83be9fc52493ed04070abac12531c6c6b901` |

The new findings supersede the production-enablement inference in
[the earlier stock extension report](stock_extension_surface.md) and
[socket notes](../reports/stock_extension_surface/socket_command_source_notes.md).
Those records remain historical evidence, not the final reachability verdict.

## Corpus, ownership, and reproducible addresses

`R` below means the existing, read-only materialized root
`E:/Documents/GitHub/jeep_uconnect_custom/analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS`.
`W` means its ancestor `analysis_ra4_18.45.01/work`. No copies of recovered
JAR/class/resource payloads are committed.

Fresh indexing covered **300 JARs, 72,507 class occurrences, 13,272 unique class
hashes, and 162,243,647 uncompressed class bytes**, without a parse failure.
It confirms the previous broad census. There are 358 `class$` helper
`Class.forName` sites: compiler-generated class-literal support is counted
separately from other loading candidates. The original broad census also
parsed 1,528 small resources. This is the recovered Java corpus, not every
possible AMS/AOT/native or subsequently downloaded class.

[bytecode_index.json](../reports/stock_signed_capability/bytecode_index.json)
contains archive hashes, unique class hashes, all containing archives, selected
field/method/interface inventories, source-addressed incoming references,
socket/loading/reflection/process/native candidates, and map-selection counts.
`class_sha256 + method + caller_descriptor + offset` identifies an instruction.
Offsets for JVM code in this report are decimal BCIs within that named method;
Lua offsets are hexadecimal file offsets and use the existing parser's function
IDs. Indirect edges below are explicitly distinguished from instruction edges.

Installed-executable ownership and signed-descriptor binding use the existing
[resident package evidence](../reports/resident_package_format.md) and
[policy inventory](../reports/resident_policy_entitlements.md). The corpus also
contains shared platform libraries and unused packages: presence in this tree
does not establish that a class is in an active signed application's domain.
No new credential, signature, or trust analysis was performed.

All socket-class copies are 3,480 bytes, SHA-256
`55bf4d4ca3872b4434f69c4d9fe0c04e64fcef69da0682381ca91d904d972edb`:

| Package | Owning archived app | Path below `R/kim_packages` |
|---|---|---|
| KIM1 | Tweddle Yelp 0.9.4799 | `KIM1/xlets/1D5347C0-8B5E-11E2-9E96-0800200C9A66/prog/jars/yelp_embedded_10.r4799-FIT.jar` |
| KIM12 | Same Yelp | `KIM12/xlets/1D5347C0-8B5E-11E2-9E96-0800200C9A66/prog/jars/yelp_embedded_10.r4799-FIT.jar` |
| KIM1 | Tweddle iHeart 0.8.4991 | `KIM1/xlets/d0412192-c51d-476c-91e0-76fc65a82692/prog/jars/d0412192-c51d-476c-91e0-76fc65a82692.jar` |
| KIM12 | Same descriptor version, different JAR name | `KIM12/xlets/d0412192-c51d-476c-91e0-76fc65a82692/prog/jars/iHeart.4491_FIT.jar` |
| KIM3 | Tweddle Application Manager 1.0.4825 | `KIM3/xlets/c1d77320-6335-48b2-aa22-21912f657311/prog/jars/c1d77320-6335-48b2-aa22-21912f657311.jar` |

The shared translator hash is
`2b5ba8ce28fb63b36e6949b916861cfde3d5c3e9d20e2f1da7cb20ca3a216712`;
wrapper hash is
`bb630e23402a3d15f0bdd5b2dcf1971c11d4c0d08d29eb07b2e169ffcca6c876`.
Same-name classes elsewhere, especially `AbstractHUXlet` and JSON libraries,
have different hashes. Help's superclass must not inherit the socket behavior
of the older Yelp/iHeart superclass merely because their names match.

## A. Construction and activation graph

Let `S`, `C`, `L`, `T`, `Wc`, and `I` mean
`com/tweddle/test/input/{SocketCommandSource,CommandSource,CommandLooper,
JsonCommandTranslator,CommandListenerWrapper,InputTool}` respectively.
`H` means the containing copy's `com/tweddle/core/AbstractHUXlet`.

| From | To / state change | Evidence | Label |
|---|---|---|---|
| Radio's part number | Selected KIM | Installer `xlets.lua` function 4 reads `/dev/fram/partnumber`; function 5 uses `kim_pkg_map` | PROVED |
| Selected KIM | Preload package | Installer function 6, BC/file evidence below | PROVED |
| Installed app descriptor | Concrete Xlet class | `prog/xlet.properties:xlet.mainClass` | PROVED configuration, UNKNOWN actual installation |
| Stock Apps selection | Native AppManager then AMS start | [Apps launch report](../reports/app_launch_ui_path.md), SWF/native addresses | PROVED static path |
| AMS lifecycle | Selected concrete `initXlet`/`startXlet` | Descriptor plus recovered AMS lifecycle contract | STRONGLY INFERRED dispatch; UNKNOWN invocation on target |
| Yelp `HUXlet.initXlet` | `H.initXlet` | `invokespecial` BCI 97 | PROVED direct bytecode call edge |
| iHeart `IHeartPlayerXlet.initXlet` | `H.initXlet` | `invokespecial` BCI 30 | PROVED direct bytecode call edge |
| `UpdateManagerXlet.initXlet` | `H.initXlet` | `invokespecial` BCI 30 | PROVED direct bytecode call edge |
| `H.initXlet` | `H.initCommandLooper` | BCI 154, after form registry initialization | PROVED direct bytecode call edge |
| `H.initCommandLooper` | `I.createCommandListener` | BCI 2; listener field assignment BCI 5 | PROVED direct bytecode call edge |
| `I.createCommandListener` | `InputTool$5` | `new` BCI 0, constructor BCI 4, return BCI 7 | PROVED direct bytecode call edge |
| `H.initCommandLooper` | `L(listener,H.xlet,context)` | `new` BCI 9, constructor BCI 24, looper field BCI 27 | PROVED direct bytecode call edge |
| `L.<init>` | `Wc(listener,xlet,context)` | `new` BCI 15, constructor BCI 22, listener field BCI 25 | PROVED direct bytecode call edge |
| `L.<init>` | `CommandTranslator.create` | BCI 29, translator field BCI 32; factory selects `T` | PROVED direct bytecode call edge |
| `L.<init>` | `C.create` | BCI 36, final `commandSource` field BCI 39 | PROVED direct bytecode call edge |
| `C.create` | `S()` | `new` BCI 0, `invokespecial` BCI 4, return BCI 7 | PROVED direct bytecode call edge |
| Concrete Yelp/iHeart/UpdateManager `startXlet` | `H.startXlet` | BCIs 33 / 11 / 1 respectively | PROVED direct bytecode call edge |
| `H.startXlet` | `L.start` | Non-null looper check BCI 110, call BCI 128 | PROVED direct bytecode call edge |
| `L.start` | `HUThreadFactory.newThread(this,name)` | BCI 19; factory `new HUThread` BCI 0, constructor BCI 6 | PROVED direct bytecode call edge |
| `HUThread.<init>(Runnable,String)` | `Thread(HUThreadRunnable(runnable),name)` | Wrapper constructor BCI 14; Java Thread constructor BCI 18 | PROVED direct bytecode call edge |
| `L.start` | `HUThread.start` then `Thread.start` | BCIs 29 and 4 | PROVED direct bytecode call edge |
| JVM thread dispatch | `HUThreadRunnable.run` | Runnable registered in preceding constructors | STRONGLY INFERRED indirect activation |
| `HUThreadRunnable.run` | `L.run` | Interface `Runnable.run` BCI 28, receiver stored from constructor | STRONGLY INFERRED receiver; PROVED interface call site |
| `L.run` | `S.waitForNewCommand` | Virtual `C.waitForNewCommand` BCI 19; final source populated by `C.create` | STRONGLY INFERRED receiver; PROVED virtual call site |
| `S.waitForNewCommand` | Lazy listener creation/bind and `accept` | `getServerSocket` BCI 3; `accept` BCI 6 | PROVED direct bytecode call edges, UNKNOWN success |
| Normal `H.destroyXlet` | `L.stop` | BCI 22 | PROVED direct bytecode call edge |
| `L.stop` | Thread interrupt and source release | BCIs 9 and 21 | PROVED sites; STRONGLY INFERRED concrete release dispatch |

**PROVED:** `S` extends abstract `C` and directly implements no interfaces;
`L` implements `Runnable`, `Wc` and `InputTool$5` implement `CommandListener`,
and `H` implements `Xlet` and `FormManager`. The owner is the containing Xlet,
with constructor-injected listener, Xlet, and context. The source is assigned
once to the looper's final field. No external DI container is involved.

**PROVED bounded negative:** all incoming bytecode/type references to `S` from
other classes identify `C.create`. No recovered external call selects `S(int)`
or `S(String,int)`. No recovered loaded literal/configuration names `S` for
reflective construction, and no registry/factory alternative selects it. Its
own superclass constructor calls are present in all three constructors.
`C.resetSource` releases then initializes, but no external caller was found.
The `/tmp/touchInput` constant is not a file-ingress activation path.

**PROVED:** `InputTool.INPUT_FRAMEWORK_ENABLED` is a constant value of **1**.
The socket-containing `H.initXlet` has no runtime test-mode check around
`initCommandLooper`; `createCommandListener` unconditionally returns its
concrete listener. Production/development log-level selection and Xlet lockout
registration are separate from this construction. Earlier initialization may
still fail, and actual lifecycle delivery is unknown.

## B. State and listener configuration

| Value / behavior | Provenance and result | Label |
|---|---|---|
| Factory port | `S().<init>` loads 11111 at BCI 5, writes `port` at 8 | PROVED |
| Factory bind address | Loads `127.0.0.1` at BCI 12, writes `host` at 14 | PROVED |
| Integer constructor | Caller argument to `port` BCI 6; fixed loopback to `host` BCI 12; no recovered external caller | PROVED |
| String/integer constructor | Arguments to `port` BCI 6 and `host` BCI 11; no recovered external caller | PROVED |
| Wildcard bind | Not selected by the recovered construction; no later host/port mutation found | DISPROVED for the factory path |
| Socket creation | Lazy: null field -> `initSource`; unbound `ServerSocket()` BCI 5, field BCI 8 | PROVED |
| Reuse address | `setReuseAddress(true)` BCI 16 before bind | PROVED |
| Bind | `InetSocketAddress(host,port)` BCI 35 then one-argument `bind(SocketAddress)` BCI 38 | PROVED |
| Backlog | No explicit backlog supplied; effective JamaicaVM/native default not recovered | UNKNOWN numeric value |
| Accept/client timeout | No timeout setter or application deadline in this path; single thread blocks in accept/readLine | PROVED absence of application configuration; UNKNOWN platform intervention |
| Thread | `TGTCore-CommandLooperThread`; ordinary `java.lang.Thread` through HU wrappers; no explicit daemon/priority setter in these constructors | PROVED |
| Request concurrency | One accepted client serviced on the same looper thread | PROVED |
| Retry | False result -> `Thread.sleep(1000)` at `L.run` BCIs 25/28, then loop; true -> immediate next iteration | PROVED |
| Binding retry | `getServerSocket` rebinds an unbound socket at BCI 40; both bind regions print caught `Exception` | PROVED |
| Stop | Set stopped, interrupt worker, clear started, release source; source closes listener BCI 27 and clears field BCI 51 | PROVED |
| Restart | `L.start` if not started clears stopped and creates a fresh thread; source is lazy after release; no join or automatic dead-worker health check | PROVED |
| Pause | Containing `H.pauseXlet` schedules UI work; it does not call `L.stop` | PROVED |

There are important failure limits. If `initSource` fails before assigning a
socket, `getServerSocket` dereferences null at `isBound`, outside its bind
handler. The request method catches only `IOException`. A handler/runtime
exception can escape to `HUThreadRunnable.run`, whose `Exception` handler logs
it and finishes the worker; it does not reset `L.started`. Thus normal subsequent
`start` need not revive a failed worker. `L.stop` also dereferences its thread
without a null guard. These are static failure paths, not induced failures.

There is no `finally` around accepted-client cleanup. Stop retains only the
listening socket; it does not explicitly close an already accepted client
blocked in `readLine`. Interrupt alone does not prove that read ends on this
platform. A constructor/bind exception, busy port, UI queue blockage, missing
runtime dependency, or denied permission can prevent effective service even
when the lifecycle methods are called. `started`/`stopped` are ordinary boolean
fields, not volatile, and no looper synchronization/join is present.

## C. Wire protocol and effects

**PROVED:** `S.waitForNewCommand` wraps an accepted input stream in a
platform-default `InputStreamReader` and `BufferedReader`, and calls `readLine`
once (BCI 42). Java `readLine` framing accepts LF, CR, CRLF, or an EOF-terminated
final line. No application length bound is imposed. The underlying runtime
implementation/default encoding and memory limits are **UNKNOWN**; UTF-8 and
a numeric maximum must not be assumed. One JSON object is parsed from that
line. Commands are case-sensitive. `command` is obtained by `getString`, and
`args` by required `getJSONObject`, even for parameterless commands.

The nominal request shape is `{"command":"name","args":{...}}`. This parser
is more permissive than strict JSON: the exact recovered `JSONObject.getString`
calls `Object.toString`, rather than enforcing a Java String; `optString`
defaults to empty string, and `optBoolean` defaults to false. The object parser
also has `=`/`=>` separator branches and comma/semicolon handling. The table
uses intended field types, not a claim of strict schema validation. No separate
handshake, login, sequence counter, or protocol version is parsed.

Non-null handler results are written through a platform-default
`OutputStreamWriter`, followed by **one LF**, flushed, and the writer closed
(BCIs 89/96/101/106). Reader and client are then closed (111/116). There is one
request per connection; additional lines are not processed. UI and settings
state can persist in the application across separate connections.

All command comparison/handler-call BCIs below belong to `T.doCommand`.
`Wc` normally queues a numbered inner Runnable on LWUIT's display thread;
that Runnable calls the stored `InputTool$5` listener, which reaches `I` or
the indicated framework object. These interface/callback receiver resolutions
are **STRONGLY INFERRED** from proved constructor and field flow. Handler
implementations and named call sites are **PROVED**. Runtime effects are unknown.

| Command | Args / defaults | Handler at BCI | Reply | Actual scope |
|---|---|---|---|---|
| touch | optional `id`, `label`; nonempty id wins | `doTouchById` 74 / `doTouchByLabel` 97 | `status`: bool | Test UI: finds current-form component and dispatches touch/action; false if neither selector |
| putText | `id`, `text`; `showKeyboard=false` | `putTextById` 159 | none | Test UI: set text, optionally present keyboard |
| touchListItem | `listId`, `index` integer | `doTouchOnItem` 200 | none | Test UI: select/activate list item; resulting application action depends on listener |
| itemElement | `listId`, `index`, `id` | `doTouchItemElement` 252 | none | Test UI: activate nested item component |
| scrollUp | `listId` | `doScrollUp` 282 | none | Test UI scrolling |
| scrollDown | `listId` | `doScrollDown` 312 | none | Test UI scrolling |
| getCurrentForm | `{}` | `getCurrentForm` 331 | `formName` | Benign query: HasId.getId when implemented, otherwise form class name; no form yields null |
| verifyElement | optional `id`, `label`; id wins | `doVerifyElement` 394 / 418 | `status`: bool | Benign query: component presence in current form |
| getLabelText | `id` | `doGetLabelText` 458 | `text` | Benign UI query: Label, TextArea, or HavingReadOnlyText; missing/unsupported yields null |
| getListSize | `id` (not `listId`) | `doGetListSize` 498 | `size`: integer | Benign UI query; underlying component/type/bounds handling applies |
| getRuntimeInfo | `{}` | `doGetRuntimeInfo` 527 | `free`, `maxMemory`, `totalMemory`, `threadActiveCount` | Benign VM query through `I.getVMInfo`, Runtime memory methods and Thread.activeCount |
| gc | `{}` | `doGC` 554 | `status=true` | VM/debug: requests Runtime.gc; reply does not prove collection |
| setSettings | `key`, `value` JSON value | `setSetting` 602 | `status=true` | Application control: Settings map/ObservableValue update, may affect later framework behavior; not a vehicle-setting API |
| closeKeyboard | `{}` | `closeKeyboard` 628 | `status`: bool | Test UI: may clear/submit CVP keyboard text or send pointer events; not a read-only operation |
| runUnitTests | `archive`, `junitCommands` | `runUnitTests` 679 | none | Test/application control: wrapper constructs XletTestRunner; external runtime dependencies and loader policy unresolved |
| invoke | `method`; optional `array`, default zero arguments | `Class.getMethod` 756, `Method.invoke` 766 | `result` or `error` | Reflection on wrapper public methods, including inherited public methods; no caller-specified class receiver |

Response objects use `JSONObject.put`, then `toString`. A Java null result
removes/omits that member, so null text/form/void results may serialize as `{}`;
do not promise `{"result":null}`. Invocation exceptions are placed under
`error`; an `InvocationTargetException` is unwrapped to its target exception.
There are no numeric error codes or universal success acknowledgement.

Unknown commands fall through with null. Missing/malformed JSON fields producing
`JSONException` are printed and normally produce no acknowledgement, followed
by connection close. Ordinary handler runtime exceptions are not all caught
there. EOF before any characters supplies null to the translator; successful
normal cleanup is not guaranteed for that case. No malformed-input experiment
was performed. Asynchronous UI commands can return before their queued action;
most query/response handlers use `callSeriallyAndWait` instead.

`invoke` derives each signature class from `JSONArray.get(i).getClass()`; it
does not translate boxed numbers to primitive `int`, or choose assignable
superclass signatures. A public `(String)` method and public no-argument
methods are structurally simpler candidates than primitive-parameter methods.
This is a method lookup boundary, not proof every wrapper method is callable.

Additional wrapper methods include `doTouchByUIID(String)`,
`doTouchByPoint(int,int)`, `showDialog(String)`, `dumpThreads()`, and
`onKeyUp(Integer)`/`onKeyDown(Integer)`. `showDialog` queues `$18`, whose
`run` constructs a stock `HUMessageDialog(message, OK-button)` at BCI 25 and
calls `show` at 30. `dumpThreads` calls Jamaica `Debug.dumpThreadStates`.
Key methods call the installed device-input listener. No direct vehicle-control
handler is identified in this command set; UI activation can trigger whatever
application action owns a component, so these commands are not all benign.

### Test-runner extension and its limits

`Wc.runUnitTests` constructs `XletTestRunner(xlet,context)` at BCI 12 and calls
`startTests(archive,junitCommands)` at 19. `startTests` creates
`XletTestRunnable`, registers it with `AsyncEventHandler`, and fires an
`AsyncEvent` at 53. The Runnable stores the two supplied strings.

In `XletTestRunnable.run`, `File(archive)` is checked with `exists` at 17.
If present, it constructs `URLClassLoader([file.toURL()], ownClassLoader)`
at 45; otherwise it uses its own class loader. The loader is assigned via
`access$002` at 58. Commands are split with the literal pattern `[ ]`
at 103/110 and passed to the inherited JUnit `start(String[])` at 113.
`XletTestRunner.loadSuiteClass` calls that loader's `loadClass` at 22;
`runSingleMethod` constructs an XletTestCase, sets context and Xlet, and runs it.

**PROVED:** a local-file class-loading/test mechanism exists in recovered
bytecode. **UNKNOWN:** its executable runtime chain. **No `junit/` classes are
present in the 300-JAR census**, including superclass `junit/textui/TestRunner`.
Their possible availability in AMS/AOT or another runtime location is not
established. Accordingly the exact inherited JUnit option grammar is unknown;
do not infer it from a contemporary JUnit implementation. File permissions,
class-loader permissions, effective protection domains, file availability, and
the earlier package/client gates remain. No test archive was created, installed,
loaded, or supplied to a target. This mechanism is not established as a way to
load newly authored unsigned code and was not investigated as a bypass.

## D. Authentication and authorization

**PROVED bounded search result:** no application-layer password, token,
challenge/response, shared-secret comparison, peer-IP allowlist, login/session,
caller-identity check, or per-command entitlement gate was found in the
recovered socket source -> translator -> wrapper -> InputTool request path.
There is no discovered factory/engineering-mode, build-type, system-property,
or DRM test surrounding socket construction in the containing superclass.
This is **not** a global unauthenticated-service claim.

The independent boundaries are:

| Gate | Evidence and consequence | Label |
|---|---|---|
| Package selection | No map output is KIM1, KIM3, or KIM12 | PROVED exclusion from supplied install configuration |
| Installed identity and lifecycle | Signed descriptor/installed package; stock Apps/native launcher includes DRM checks | PROVED static boundary; UNKNOWN target principal/state |
| Bind/client Java policy | `security.jar!/full.policy` line 59 explicitly requests SocketPermission `*` for accept/connect/listen/resolve | PROVED resource; UNKNOWN effective grant |
| Reflection and loading policy | Same policy lines 43-56 include file, class-loader, library, declared-member, and reflection permissions | PROVED resource; UNKNOWN effective domain composition |
| App-specific interface policy | Yelp requests `ppp0`; iHeart requests `tun`; KIM3 manager requests `tun` plus AppMgrPermission | PROVED resources; not a listener bind result |
| Harman socket factory | Initializer `init` BCI 17 installs `Socket.setSocketImplFactory`; StrictSocketImpl checks InterfacePermission and delegates to SocksSocketImpl | PROVED path; UNKNOWN live installation and applicability to accepted sockets |
| ServerSocket factory distinction | No recovered `ServerSocket.setSocketFactory` call; do not assume the client Socket factory changes ServerSocket bind | PROVED bounded absence; UNKNOWN runtime implementation |
| Network scope | Factory endpoint is IPv4 loopback; no recovered specific off-unit bridge | PROVED address; UNKNOWN live routing/forwarding |
| Worker/UI availability | Bind must succeed, worker remain alive, and LWUIT callbacks run | UNKNOWN runtime conditions |

`full.policy` SHA-256 is
`623e870a36dea05b9c5c33b16ccb68bf77a66675d008a2f6d46aa5e859bb2a14`.
App policy absence of SocketPermission does not prove denial when the descriptor
also names `full.policy`. Conversely, a broad grant in a resource does not prove
that the app receives it. No policy resource was altered.

## E. Production-selection proof and network boundary

The installer artifact is
`W/installer_iso/usr/share/scripts/update/installer/xlets.lua`, 8,006 bytes,
SHA-256 `e6849b1260417cdc89762ae76cac1b0f01bab28a833d2211b80498ae0d4466cc`.
It is parsed as Lua 5.1 bytecode, never executed:

| Edge | File evidence | Label |
|---|---|---|
| Bind part-reader closure to `/dev/fram/partnumber` | Root function constant/load `0x48`, closure/upvalue binding `0x68/0x6c` | PROVED |
| Read part number | Function 4 calls device.open with read mode at `0xcc9`, reads 10 bytes at `0xcdd`, normalizes recognized 8-digit-plus-suffix or 9-digit forms | PROVED |
| Bind map selector closure | Root closure `0x70`, root `install` upvalue binding `0x88` | PROVED |
| Select package | Function 5 defaults KIM0 `0xea7`, loads map via dofile `0xebf`, indexes supplied part number `0xed3/0xee3`, returns `0xee7` | PROVED |
| Install uses returned package | Function 6 part-reader call `0xfe5`, map-selector call `0xff1`; result in register 18 | PROVED |
| Reject no-package branch | Function 6 tests selected value/KIM0 at `0x1219/0x1221` | PROVED |
| Copy selected package | Function 6 incorporates register 18 into `kim_packages/<selected>` at `0x126d`; destination `kona/preload`; copy command invocation `0x1299` | PROVED static instruction path |

The map hash and assignment line/package inventory are recorded in
`bytecode_index.json:package_selection`. KIM1/KIM3/KIM12 are absent even before
duplicate assignments are resolved. For example, part `05091051` selects KIM18
(map line 11); `68224525` selects KIM19 (line 74). KIM18 and KIM19 Yelp
descriptors select **`com.sprint.chrysler.yelp.xlet.YelpPOIXlet`, version
03.00.33**, rather than the older Tweddle superclass. The complete census found
no socket class in any mapped package, not just these two examples.

The installer also handles old preload removal and base-directory restoration;
this was only inspected as evidence. No installer command, package selection,
part-number read on a radio, or filesystem update was performed.

The recovered `pf.conf` in hidden HBC segment `00f20000` passes loopback at
line 73, defaults to inbound/outbound blocking at 74-75, and blocks hotspot
guest destinations including private/loopback addresses via `wblk` at 55/91.
Dynamic anchors and live rules remain unknown. The two recovered 3proxy configs
select internal `127.0.0.1`, port 3128, with local override files; they do not
establish an off-unit path into TCP 11111. The earlier 832-file candidate-led
native census found no socket-class/thread-name correlation. Native strings
matching a port alone are not a forwarder.

## Existing extension mechanisms

The following is a classified inventory, not a list of working ingress routes.
Detailed per-class occurrences and source BCIs are in the new index and the
[inherited complete surface inventory](../reports/stock_extension_surface/java_extension_surfaces.json).
`UNKNOWN` means activation, external control, or policy remains unclosed; it
does not mean that a candidate was silently dropped.

| Candidate and owner | Activation and input / load scope | Remaining boundary and production conclusion |
|---|---|---|
| Tweddle JSON `invoke` in the five older copies | Socket dispatcher -> public wrapper methods; supplied method and runtime-typed arguments | PROVED method dispatch; package-excluded, loopback/client/policy gates; no arbitrary class receiver |
| Tweddle `XletTestRunner` | `runUnitTests` -> async event -> local-file URLClassLoader or existing loader -> test class name | PROVED loader instructions; missing JUnit runtime, file/domain/client gates; no new-code use established |
| Tweddle HTTP response injection | HttpMethodExecutor -> InjectionManager; `injectionEnabled` defaults false, XML plan defaults `/fs/etfs/response_injection.xml`; file responses/delays/status/headers | PROVED configuration-driven data substitution, not a listening server; external file writer and enablement UNKNOWN; older copies package-excluded |
| Tweddle model registry / JSONModelResponseProcessor, including Help daemon variant | HTTP response processor obtains type/innerType from MethodDescriptor fields; Class.forName BCI 63 in core variant, reflected construction/population; ModelRegistry holds model classes | PROVED model instantiation; service payload supplies values, not proved arbitrary class selection; descriptor provenance/classpath/domain gates remain |
| Tweddle form registry / wizard descriptors | AbstractHUXlet builds registry from concrete getFormClasses; createFormInstance uses registered Class.newInstance; wizard/resource XML supplies UI descriptions | PROVED stock UI/resource extension; no new class bytes or user-editable registry path proved |
| Airbiquity EventParser in HUP apps | JSON `type` -> fixed response package plus capitalized `<type>Event`; Class.forName BCI 69, newInstance 76, reflected init(HashMap) 108 | PROVED resource-free class-name dispatch within fixed package; caller transport/session and useful safe event remain UNKNOWN; no byte loader |
| Airbiquity UnitTestUtil | Emulator or download-file `enableUT` gate -> HTTP/JSON test worker, optional reflection in newer variant | PROVED test code; no recovered external startUnitTest invocation; no production activation or safe ingress established |
| Platform/Kona service factories | Audio, device input, phone, sensors, telephony, navigation, media, connectivity use reflected stock implementation classes | PROVED platform adaptation; mostly fixed names and framework-owned selection, native/service/permission gates; no arbitrary external plugin origin established |
| Airbiquity FactoryOfFactories | isAPIEmulated -> fixed EmulationSDPClientFactory; normal path uses stock FactoriesLoader | PROVED emulator/stock choice; no caller-supplied class name; runtime configuration UNKNOWN |
| ConnectorImpl | open/openPrim uses URI scheme plus configured class-root/platform to resolve protocol implementation via Class.forName | PROVED protocol-provider selection; classpath, connector configuration and downstream permission checks remain; not arbitrary executable input |
| XML/JAXP/Xerces/DOM/SAX providers | FactoryFinder/ObjectFactory/DOMImplementationRegistry use configured names, system properties, service resources, and class loaders | PROVED generic provider infrastructure; external control over provider names/resources and activation per app UNKNOWN |
| Logging factories/configurators | Commons Logging, Microlog, Kona trace select appenders/formatters via properties and reflection | PROVED configuration-based resident class construction; configuration origin/write permission and live selection UNKNOWN |
| Native `Affiner` loading in resident LWUIT copies | Graphics helper constructor loads fixed `Affiner`; resource stream -> temp file -> System.load BCI 138 | PROVED native resource loading; fixed resource name, loadLibrary/File permissions and ABI; externally supplied library origin UNKNOWN |
| Harman Executor wrappers | Two Runtime.exec(String[]) sites, BCI 23; AMS initializer TimeMgrService.updateOffset calls its wrapper at BCI 6 | PROVED process-launch wrappers; known service caller and fixed task, no user command ingress proved; shared Kona wrapper has no recovered external Java caller |
| Java serialization/reflection support | Storefront Base64 ObjectInputStream subclass resolveClass plus object/array/field reflection in libraries | PROVED decoder infrastructure; externally controllable serialization-to-effect chain UNKNOWN; not exercised |
| Help content bundle/HTML pipeline | Help daemon downloads content, ZIP reader expands resources; Help HtmlForm feeds existing HTML component | PROVED content handling APIs and call sites; network response/user control, activation and content-policy end-to-end UNKNOWN; no general script execution proved |
| Catalog/AMS extension | Already-stock catalog UI selects package -> download -> native AppManager/AMS validation | PROVED/STRONGLY INFERRED from existing reports; new packages still require unavailable authentication; not a solution to this objective |
| Native 3proxy plugin/include and Lua configuration | Shipped config has local plugin/override includes and fixed ProxyReloaded.lua callback | PROVED native configuration hooks, separate from resident signed Java; local-file production provenance and controllability UNKNOWN; no changes attempted |

**PROVED bounded negative:** no direct subclass of a class named ClassLoader,
no resident `defineClass` call site, and no general-purpose Java script
interpreter activation chain was recovered. The prior scripting category's five
hits are Reed-Solomon arithmetic `evaluateAt` and DOM/XPath machinery, not
evidence of a shell or JavaScript console. Native Lua and Help HTML rendering
are separate findings; absence in Java does not establish absence in native/AOT
code. Browser/WebKit lexical hits and HTTP client libraries do not prove a local
HTTP server. Factory/provider counts are not plugin-ingress counts.

## Other input and service candidates

| Input / stock component | What the recovered path can support | Classification / remaining gate |
|---|---|---|
| Stock Apps UI -> native AppManager -> AMS | List and request normal launch of installed authorized Xlets; visible stock form is a benign proof | PROVED static user-facing chain; target installed list, DRM, launch completion UNKNOWN |
| Permissioned Kona AppManager / SvcIPC | Query and manage stock Xlet lifecycle through `com.harman.service.AppManager` and AMS | PROVED method permission checks and request construction; safe query UI/client for each operation and live registration UNKNOWN |
| Tweddle TCP 11111 | Read UI/VM state, existing test UI operations | PROVED package-excluded loopback mechanism; no externally reachable instance established |
| Microlog SocketLogServer in shared kona.jar | Standalone main -> thread -> port 1234 ServerSocket(int), accept, DataInputStream.readUTF, console output | PROVED static log receiver; only self/main construction/start references found; no descriptor/startup activation; production reachability UNKNOWN |
| Airbiquity HUP test HTTP server | ServerSocketFactory.createServerSocket(4700,10,192.168.6.1), HTTP entity decode, test dispatcher | PROVED listener code in multiple HUP variants; no external startUnitTest caller, emulator/enableUT gate; listener/route UNKNOWN; no commands exercised |
| PPS simulator in Kona | Outbound socket/object streams emulate native PPS | PROVED client, not an inbound server; PPS.getObject selects it only for os.arch i386/x86/amd64, selects PPSObjectTarget otherwise; production ARM simulator path DISPROVED under that predicate |
| Native PPS / service callbacks | Existing resident device, media, connectivity, phone and application callbacks | PROVED API/registration infrastructure; no universal external human command path; vehicle/diagnostic interactions excluded from proof candidates |
| HTTP(S) stock clients | Yelp/storefront/catalog/help/media responses populate UI/model/content | PROVED client/parser presence and selected data paths; server-controlled responses, entitlement/connectivity, and safe user-controllable payload route UNKNOWN |
| Paho MQTT / local network module | Client network modules and callback infrastructure | PROVED API/call-site presence; broker configuration, subscription activation, authorization, useful benign message chain UNKNOWN |
| Bluetooth / phone / Via Mobile | Stock phone and connectivity wrappers plus `tun` interface-oriented applications | PROVED corpus API/configuration presence; paired-device/application-protocol-to-benign-effect path UNKNOWN; not a TCP listener inference |
| USB / removable media | Stock media and authenticated software-update ingestion | PROVED existing media/update infrastructure from repository; no unsigned application ingress, watched benign command drop-directory, or complete new-message display chain established |
| Wi-Fi / hotspot | Native networking config and service APIs | PROVED routing/filter configuration; no resident off-unit benign command endpoint established; active interfaces/anchors UNKNOWN |
| Native telnet inetd entry (separate native firmware evidence) | inetd.conf line 23 selects telnetd; pf.conf line 81 permits port 23 on `en` toward vehicle/manufacturing addresses | PROVED configuration pair only; inetd/telnetd startup, credentials/authentication, effective rules and interface access UNKNOWN; not a benign proof candidate and not pursued |
| Native 3proxy | Configured loopback HTTP proxy on 3128, local includes, IP-based policy | PROVED configuration only; live process/overrides/forwarding UNKNOWN; not evidence of off-unit access to socket commands |

There is no additional direct `DatagramSocket`/UDP listener chain established
by this Java census. Obfuscated HTTP/socket users, native IPC implementations,
and dynamically registered callbacks remain bounded static candidates. The
native rows are components of recovered firmware, not newly established
per-Xlet signature associations.

## Best benign proof, remaining unknowns, and validation

**Best evidence-supported stock action:** use the normal Apps screen to launch
an already-installed authorized application and observe its existing UI. The
repository proves the stock UI -> native DRM-checked launcher -> AMS request
chain. This adds no resident package, signature, trust change, or new client.
No target launch was performed in this work.

**Best conditional command:** a `getRuntimeInfo` request with empty `args`, or
`getCurrentForm`, using an *already available authorized on-unit client* and
one of the *already installed exact containing versions*. The report does not
establish either prerequisite. `invoke` of a fixed-message dialog is a secondary
static candidate, with a larger reflection/UI dependency. No port-forwarder,
new helper, test archive, package substitution, or gate-changing procedure is
proposed. Given the shipped KIM map, further attempts to force this listener
are not justified by the present evidence.

Remaining unknowns are the target's installed/history state (the provided part
number is `68224525AM`, resolving to KIM19 as recorded above);
effective per-code-source Java policy and socket implementation; runtime
JUnit/AOT dependencies; successful bind and available local clients; live
filter anchors and forwarding; startup/configuration of other listener and
provider candidates; externally controlled origins for data/model/Help/MQTT
flows; and a complete externally reachable benign proof. Static examination
cannot turn any of these into a runtime observation.

Validation uses the new read-only `analysis_tools.stock_capability_index` plus
the existing classfile/census/Lua parsers, JDK 8 `javap -c -p -s` as an independent
bytecode check, descriptor/resource reads, archive/class SHA-256 identity, and
source-addressed earlier SWF/native reports. Synthetic tests cover duplicate
class identities, stable metadata, unchanged input archives, malformed-input
failure, server-factory/process/native APIs, and literal-map last-assignment
semantics with executable Lua statements rejected. Reproduction commands and
completed test results are in
[validation.json](../reports/stock_signed_capability/validation.json).

This work performed **no signing bypass, trust modification, credential work,
firmware modification, target installation, target command execution,
diagnostic writes, or vehicle-control action**. Authorization of newly authored
resident applications remains an unavailable external dependency.
