# Stock Extension Surface Evidence-Ladder Design

Date: 2026-09-07. Approved by the owner on 2026-09-07. This design is for
static, host-only, read-only analysis of already recovered artifacts and
existing repository evidence. It does not authorize target or vehicle work.

## Goal

Determine, as far as the recovered evidence permits, whether
`com/tweddle/test/input/SocketCommandSource` is a genuinely activatable stock
capability or dormant/test code. Only after that focused investigation is
exhausted, census the resident signed Java extension surface and correlate the
highest-value candidates with recovered native/QNX evidence.

The result is acceptable when every reported mechanism is traceable through an
explicit evidence ladder, unknown links remain visible, machine-readable
censuses reproduce deterministically, and no report mistakes static presence
for runtime execution or external reachability.

## Locked Safety Boundary

All work occurs in the linked worktree
`E:/Documents/GitHub/jeep_uconnect_custom_stock_extension_surface` on branch
`codex/stock-extension-surface`, based on commit
`be5a83be9fc52493ed04070abac12531c6c6b901`. The existing
`codex/ra4-driver-temperature` checkout is a read-only evidence location for
ignored recovered artifacts. Its branch, worktree files, index, untracked
files, and dirty state must not be changed, stashed, cleaned, restored,
switched, staged, or reset.

The analyzers may read recovered vendor artifacts in place and report bounded
metadata, hashes, class/member names, resource names, structural edges, and
small evidence excerpts needed to support a finding. They must never execute a
recovered class or target binary. They must not extract or copy proprietary
JARs, classes, resources, filesystem payloads, firmware, certificates, keys,
tokens, or other vendor binary content into the worktree. Generated outputs
must contain metadata and conclusions only.

The investigation excludes signing credentials, authorization issuance,
trust-store changes, authentication bypass, AMS weakening, unsigned
installation, firmware modification, and equivalent workarounds. It performs
no target or vehicle operations. A discovered capability is documented, not
activated.

Before every commit, the staged path list and blob types are inspected. Any
archive, executable, JAR, class, SWF, certificate, key, decoded filesystem,
firmware image, or recovered payload is a hard stop. Each delivery records
`Stock/vendor firmware staged: NO`.

## Evidence Vocabulary

Every substantive finding uses exactly one of these classifications:

- **PROVED**: directly established by reproducible recovered bytes, parsed
  structure, a complete static edge, or deterministic analyzer output.
- **STRONGLY INFERRED**: the best explanation of multiple proved facts, but at
  least one required link is not directly observed.
- **UNKNOWN**: evidence is absent, ambiguous, outside the recovered corpus, or
  requires prohibited dynamic/target work.

The analyzers and reports preserve seven distinct activation states:

1. `class_exists`
2. `statically_reachable`
3. `activation_mechanism_exists`
4. `activation_configured`
5. `production_enabled`
6. `listener_executable`
7. `externally_reachable`

Each state has its own classification and evidence references. A later state
does not inherit proof from an earlier state. In particular, a class, parser,
API reference, call edge, or listener body never proves activation,
production enablement, execution, routing, firewall passage, or peer access.

## Considered Approaches

### Selected: structural classfile analysis plus evidence graph

Implement a bounded, dependency-free JVM classfile/bytecode reader, a resident
archive census, and an evidence-graph renderer. This provides method-level
call sites, constructors, fields, type relationships, control-flow structure,
configuration references, resource metadata, and deterministic reverse paths
without depending on vendor execution or opaque decompiler behavior.

Advantages are reproducibility, synthetic-test coverage, exact distinction
between constant-pool presence and executed bytecode, and machine-readable
provenance. The cost is implementing only the classfile features required by
the recovered Java 1.4/5-era corpus and explicitly marking unresolved dynamic
dispatch, reflection targets, native methods, malformed inputs, and unsupported
attributes.

### Rejected as insufficient: strings and constant-pool census

A strings-first scanner is useful for candidate discovery but cannot prove
method invocation, construction, field initialization, call direction, or a
path toward an activation root. It remains an input signal, never the primary
claim mechanism.

### Rejected as primary: decompiler-only workflow

External decompilers can aid manual interpretation, but their transformations
are harder to test and may silently invent source-level structure. Decompiled
text is therefore optional corroboration; parsed classfile offsets and
bytecode edges remain authoritative.

## Architecture

```text
explicit recovered roots (read-only)
        |
        +--> JAR/class/resource inventory + SHA-256
        |         |
        |         +--> class/type/field/method model
        |         +--> bytecode calls, construction, fields, CFG
        |         +--> properties/XML/JSON/service/config references
        |         +--> extension/input/network surface classifiers
        |
        +--> selected native/QNX roots
                  |
                  +--> imports, strings, endpoints, IPC/service markers
                              |
                              v
                    normalized evidence ledger
                              |
              +---------------+----------------+
              |               |                |
       activation paths  surface censuses  rendered reports
```

All commands receive explicit input roots and output paths. Inputs are opened
read-only. Traversal is sorted, symlinks are not followed, size/count limits
fail closed, archive paths are normalized and checked for traversal, duplicate
ZIP members are reported, and errors name the artifact without copying its
content. Output paths are relative to the analysis worktree and are written
atomically.

## Components

### `analysis_tools/java_classfile.py`

Parse classfile headers, constant-pool records, class/superclass/interfaces,
fields, methods, `Code`, exception tables, and the attributes needed to locate
inner/enclosing classes, annotations, and constants. Decode JVM instructions
with bytecode offsets, including variable-length switch and `wide`
instructions. Resolve field/method/interface calls, object construction,
class literals, strings, branches, and local exception-handler edges.

The module does not perform class loading, verification, initialization,
resolution, or execution. Unsupported opcodes/attributes remain explicit in
the result. An invocation edge is a syntactic bytecode edge; virtual/interface
dispatch targets are candidate destinations unless a unique concrete target
is proved.

### `analysis_tools/resident_surface_census.py`

Walk explicit resident application roots and archives, hash artifacts, parse
classes in memory, and emit four normalized datasets:

- activation/call paths;
- Java extension surfaces;
- network/IPC endpoints;
- user-controlled input surfaces.

The census records artifact hash, archive member, class/method/field identity,
bytecode or resource offset, evidence classification, evidence kind, and
unresolved links. It detects dynamic loading/reflection, configured class
names, factories/providers, resource/JAR/package loading, interpreters,
URL/protocol dispatch, browser/WebKit bridges, structured-data parsers,
sockets, Java/native IPC APIs, media/import paths, file/resource inputs, and
plugin/provider registration.

Configuration/resource scanning is bounded and type-aware. Properties are
parsed with Java last-key-wins semantics while duplicate keys are retained as
evidence. XML receives well-formed structural parsing with external entities
disabled. JSON is parsed only when valid. Other small text resources are
classified as text and searched for known registration/class-name forms.
Binary resource names may be inventoried, but their payloads are not emitted.

### `analysis_tools/native_endpoint_census.py`

Correlate only Java candidates that already have a high-value unresolved
native/QNX link. Reuse existing ELF and QNX inventory primitives where
possible. Record imported/exported socket functions, QNX message/channel
functions, service registration/discovery markers, named endpoints, shared
paths/mounts, dispatcher strings, and event names with artifact hashes and
offsets.

An import or string is static presence. A native call edge, registration
structure, or Java/native endpoint-name match strengthens a correlation but
does not by itself prove the service runs or a remote source can reach it.
There is no indiscriminate native reverse-engineering expansion.

### `analysis_tools/render_stock_extension_reports.py`

Validate all census schemas and render the required Markdown reports from a
curated evidence ledger. Rendering fails if an evidence claim has no source
reference, if an activation state is skipped, if a `PROVED` claim depends only
on inference, or if the ranked final candidate list does not contain exactly
five entries.

The renderer emits no command-enabling procedures for target access. It may
describe recovered protocol behavior only to the extent needed to document a
stock capability and its security boundary.

## Priority 1: SocketCommandSource Exhaustion

The first analysis phase selects every byte-identical and distinct occurrence
of `com/tweddle/test/input/SocketCommandSource.class` and all classes that
reference its type, constructors, methods, fields, string name, or relevant
interfaces. The phase is complete only after it attempts to establish:

- artifact/member occurrences and hashes;
- superclass, interfaces, nested/enclosing types, fields, constructor
  descriptors, constructor writes, and static initialization;
- every `new`, constructor call, method call, field read/write, class literal,
  reflective/configured-name occurrence, and consumer interface edge;
- forward and reverse method-level paths, including recursion/SCCs, toward
  Xlet lifecycle methods, UI callbacks, service callbacks, configuration,
  registration, factories/providers, feature flags, and test-framework roots;
- server-socket construction and bind overload, address/interface, port,
  backlog, blocking calls, loop structure, connection ownership, I/O framing,
  encoding, dispatch, replies, failures, close/finally behavior, and cleanup;
- authentication, authorization, source-address, application-state,
  configuration, entitlement, policy, and environment gates.

Reverse reachability is computed over resolved syntactic call and construction
edges. Strongly connected components are condensed before path enumeration so
recursive cycles remain visible without unbounded output. Path length and path
count are bounded and truncation is explicit. Unresolved virtual/interface
dispatch, reflection, native calls, and missing classes are separate edge
types, not silently discarded.

The report answers the immediate question at the highest defensible rung. If
no construction or activation root exists in the recovered corpus, that is a
bounded negative: dormant/test code is supported only for the inspected
artifacts, while activation through absent configuration, native code, mutable
runtime state, or out-of-corpus components remains `UNKNOWN`.

## Priority 2: Resident Extension-Surface Census

After the SocketCommandSource phase is rendered, the analyzer expands across
the recovered signed resident Java applications. Each candidate is modeled as:

```text
external/user-controlled origin
    -> signed resident component
    -> parser/dispatcher
    -> resulting capability
```

Every arrow has its own evidence reference and classification. Missing origin,
delivery, parser, dispatch, or capability links remain explicit. A parser or
API with no user-controlled origin path is static presence only. A configured
class name without a loading call is configuration presence only. A loader
without a user-controlled resource is resident flexibility, not an extension
mechanism.

Origin categories include network peer, USB/removable media, update media,
downloaded content, browser/navigation input, media metadata/content,
filesystem/configuration, app-to-app IPC, HMI/user interaction, and mutable
resident state. Capabilities include display/navigation, media import/playback,
network request/response, local file manipulation, application lifecycle,
service invocation, configuration selection, and data transformation. Vehicle
control and prohibited security-modification paths are excluded from any
experiment or recommendation.

## Priority 3: Native/QNX Correlation

Native analysis begins only from unresolved endpoint names, service APIs,
paths, protocols, or dispatch markers found in the Java census. The correlator
searches the recovered native/QNX corpus for socket/bind/listen/connect, QNX
channel/message APIs, service registration/discovery, named endpoints, shared
paths/mounts, command dispatchers, and event mechanisms.

Each correlation states whether it is an exact string/path match, API import,
call-site edge, dispatcher comparison, or inference. It cannot promote
`production_enabled`, `listener_executable`, or `externally_reachable` without
independent evidence for those states.

## Machine-Readable Schemas

The four committed JSON outputs live under
`reports/stock_extension_surface/`. They use stable key order, sorted arrays,
UTF-8, two-space indentation, and a trailing newline. Absolute host paths are
never committed; inputs use corpus labels plus relative paths. Each file
includes a schema version, generation command, input manifest hashes, tool
version, and bounded-error list.

`reports/stock_extension_surface/activation_call_paths.json` contains nodes,
typed edges, activation roots, SCCs, bounded forward/reverse paths, gates,
seven activation-state judgments, and unresolved dispatch.

`reports/stock_extension_surface/java_extension_surfaces.json` contains
class/member/config/resource evidence, surface categories,
origin-to-capability chains, missing links, and candidate classifications.

`reports/stock_extension_surface/network_ipc_endpoints.json` contains Java and
native endpoint observations, address/port/backlog/framing/lifecycle fields
where recoverable, endpoint-name correlations, gates, and reachability
judgments.

`reports/stock_extension_surface/user_controlled_input_surfaces.json` contains
origin, transport, signed consumer, parser, dispatcher, capability,
prerequisites, evidence at each link, and unresolved unknowns.

## Reports

`docs/stock_extension_surface.md` is the controlling report. It begins with
the SocketCommandSource verdict, walks the seven activation states, then
contains exactly five ranked candidate mechanisms. Each candidate contains
component, activation path, user-controlled input, useful resulting
capability, prerequisites, evidence classification, unresolved unknowns, and
whether new-package authorization is required. Ranking uses proved path
completeness and practical usefulness, not novelty.

`docs/resident_network_services.md` documents listener/client/network and IPC
surfaces, recovered endpoint behavior, lifecycle, gates, and the distinction
between bind/listen evidence and external reachability.

`docs/user_controlled_input_surface.md` documents complete and incomplete
origin-to-capability chains across network, media, files, browser, structured
data, IPC, and configuration surfaces.

All three reports include scope, corpus manifest, method, evidence legend,
bounded errors, and reproduction commands. They explicitly preserve `PROVED`,
`STRONGLY INFERRED`, and `UNKNOWN` throughout.

## Test Strategy

Synthetic, firmware-free tests are written before production analyzer code.
Fixtures are built in memory or in temporary directories and contain no vendor
bytes. Tests cover:

- class/superclass/interface/field/method parsing;
- every invocation form, `new` plus constructor pairing, field access,
  branches, switches, `wide`, exception edges, recursion, and unresolved
  dispatch;
- constructor field initialization and constant/static initialization;
- reverse paths through lifecycle, callback, factory, configuration, and
  feature-flag roots;
- server bind variants, literal and unknown address/port/backlog, accept loops,
  stream wrapping, encoding, framing, dispatch, reply, and cleanup patterns;
- constant-pool-only decoys that must not become call edges;
- reflection, configured providers, URL/protocol, parser, browser, media,
  resource, socket, and IPC classifications;
- bounded archive/resource parsing, duplicate members, traversal paths,
  malformed classes, symlink policy, and size/count limits;
- evidence-state non-promotion and exactly-five-candidate enforcement;
- deterministic output under shuffled filesystem and ZIP member order;
- redaction of absolute corpus roots and absence of binary payloads in JSON.

Existing analyzer tests remain part of the verification suite. Missing optional
host dependencies are recorded distinctly from behavioral failures; the new
analyzers use only the Python standard library so their deterministic tests do
not inherit those environment gaps.

## Error Handling and Evidence Boundaries

Malformed or unsupported artifacts never produce success-shaped records. A
bounded error identifies the corpus label, relative path, member, and reason.
The scan continues only when the failed artifact is independent and the report
marks resulting coverage incomplete. Failure of the selected
SocketCommandSource class, any direct caller, or any claimed activation root is
fatal to the focused verdict.

Analyzer heuristics may nominate candidates but cannot create `PROVED` edges.
Manual interpretation enters the evidence ledger with exact supporting
artifact/member/method/offset references and an explicit classification.
Reports distinguish exhaustive-within-manifest bounded negatives from claims
about the live target or unrecovered code.

## Implementation Sequence

1. Commit this reviewed design as a documentation-only change.
2. Write the detailed test-first implementation plan.
3. Add synthetic failing tests for the evidence model and classfile reader.
4. Implement the minimal structural parser and activation graph.
5. Add failing tests and implement resident surface/resource census.
6. Exhaust SocketCommandSource and render its focused outputs before broad
   resident scanning.
7. Add failing tests and implement bounded native/QNX endpoint correlation.
8. Run the full resident census and curate complete origin-to-capability chains.
9. Render the three reports and four JSON outputs, enforcing exactly five final
   ranked candidates.
10. Run fresh tests, deterministic regeneration/diff checks, schema checks,
    repository/proprietary-content audits, and protected-checkout comparison.

## Acceptance Criteria

- The requested worktree remains the only modified checkout and the protected
  checkout's branch, HEAD, index, files, and dirty inventory remain unchanged.
- SocketCommandSource receives method-level construction, consumption,
  activation-root, listener, protocol, gate, and seven-state analysis before
  the broader census controls the narrative.
- All required Markdown and JSON outputs exist and reproduce from explicit
  read-only corpus roots.
- The controlling report contains exactly five ranked candidates with every
  required field.
- Every substantive claim is `PROVED`, `STRONGLY INFERRED`, or `UNKNOWN` and
  links to evidence; static presence is never presented as behavior.
- All new analyzer behavior follows observed red-green test cycles and the
  complete relevant test suite passes, apart from separately documented
  baseline dependency gaps not introduced by this branch.
- No recovered vendor artifact or proprietary binary payload is tracked or
  staged. Stock/vendor firmware staged: NO.
