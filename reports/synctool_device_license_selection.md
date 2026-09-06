# Synctool device and license-selection pipeline

Updated: 2026-09-05. Read-only, owner-authorized static analysis.

## Result and scope

**[CONFIRMED]** The logged App SKU is obtained from an application-license
record selected by a module/feature query. It is not read directly from
`device.nng`, and the named `application_skuid` property is populated in the
opposite direction: a license-manager query produces a formatted property
value. The scanner's incompatibility key is a different metadata word, assigned
by the loader from a source-identity map's entry count.

**[HIGH]** The best descriptive name for that key is a **runtime source-container
identity ordinal**. It is not an application SKU, a model-year number, the
`license_model` named property, or the module selector. The vendor's original
type/field name is unavailable in this stripped ELF.

**[CONFIRMED]** The recovered update log proves that
`Harman_CMC_VP4_NA_VP4_2017Q2_UPDATE_MY14_REVA.lyc` was copied during a successful
update. It does not expose that file's internal App SKU, its individual record
classifications, or a numeric MY14-to-SKU mapping. Static mechanisms and this
observed filename must not be conflated into a proved model-year lookup table.

Labels match the [main report](map_update_2017q2_reverse_engineering.md):
CONFIRMED = direct evidence; HIGH = strongly supported semantic interpretation;
INFERRED = plausible but unproved; UNKNOWN = not established. All addresses are
ELF virtual addresses; range ends are exclusive unless stated otherwise.

Continuation result: **B - PARTIALLY PROVED** (section 12). Sections 8-10
resolve the configured internal logging endpoints, composite filesystem
provider and record-to-container-name provenance; no radio-specific numeric
MY14 mapping is claimed.

## Reproducible evidence

The local, ignored `analysis_work/Synctool.elf` has size 2,226,976 bytes and
SHA-256 `aa2e2c425d42a5f60427a89817f676b0d32b3ce73057d89355248acc24d4e330`.
It is stripped ELF32, little-endian ARM, entry `0x00103EE0`.

| Load segment | File offset | Virtual address | File size | Memory size |
| --- | --- | --- | --- | --- |
| RX | `0` | `0x00100000` | `0x2175DC` | `0x2175DC` |
| RW | `0x2175DC` | `0x003185DC` | `0x79DC` | `0x1AD00` |

Use `analysis_tools/arm_elf_analysis.py` for bounded disassembly, PC-literal
references, table words, candidate direct callers, strings, and field-access
candidates. Its whole-segment scans are discovery aids, not exhaustive call
graphs or proof that every decoded word is executable code. Validate each
candidate against surrounding instructions and constructor-installed tables.
The tool never executes or modifies the evidence.

## 1. Caller and context provenance

**[CONFIRMED]** The containing function for the call at `0x0011ACD0` starts at
`0x0011A9B4`. Its code ends at `0x0011AF68`; its literal pool ends at
`0x0011AFB4`, where the next routine starts.

| Address | Evidence and consequence |
| --- | --- |
| `0x0011A9C0` | Saves incoming `r0` in `r4`: the Synctool license context. |
| `0x0011A9D4` / `0x0011A9D8` | Reads a byte from `[fp+0xC]`, saves it at `[fp-0xA0]`. With this prologue's `fp = entry SP - 4`, it is the seventh argument, at entry SP + 8. |
| `0x0011ACC8` / `0x0011ACCC` / `0x0011ACD0` | Calls App-SKU handling with `r0 = r4`, `r1 = [fp-0xA0]`. The second argument is a flag, not a SWID object pointer. |
| `0x00123794` | Only direct ARM BL caller found for `0x0011A9B4`. Its parent routine starts at `0x00123298`. |
| `0x001232B4`, `0x00123784`, `0x00123790` | The parent saves its incoming third argument and forwards it as the seventh argument at `[sp+8]`. |
| `0x00123774` | Loads the context from parent object `+0x154`. |
| `0x00117944` / `0x00117950` / `0x00117954` | Allocates `0x54` bytes, constructs the context using `0x00114C5C`, and saves the singleton in global `0x003203FC`. |
| `0x00117914` | Stores the singleton in the parent object's `+0x154` field. |
| `0x00114C90` / `0x00114C98` | Constructor obtains `ILICENSE_MANAGER` and stores its interface at context `+0`. |

The same interface can be acquired lazily at `0x0011AF0C-0x0011AF64`: registry
`0x00321BA0`, descriptor `0x003203DC`, registry slot `+0x14`, result stored in
context `+0` at `0x0011AF38`. Descriptor name at `0x002F358F` is
`ILICENSE_MANAGER::NAME()`.

## 2. Resolve selector 0x284 through concrete virtual tables

**[CONFIRMED]** App-SKU handling's code range is
`0x00110E6C-0x00111078`, followed by literals. The earlier broad endpoint
`0x00111090` included the beginning of the next routine (`0x00111088`).

| Address / table | Evidence |
| --- | --- |
| `0x00110F6C` | Manager slot `+0x24` loads licenses from the device directory before the query. |
| `0x00110FB8` | Sets query argument `r1 = 0x284`. |
| `0x00110FC4` / `0x00110FC8` | Loads and calls manager **vtable slot `+0x58`**. Thus `0x284` is not the vtable displacement. |
| `0x00110FD8` / `0x00110FF4` | Stores returned integer at context `+0x24`, then logs `App SKU ID %d` (string `0x002F3E48`). |
| `0x00241944`, `0x0024195C-0x00241978` | Registers the LICENSE_MANAGER factory, descriptor `0x003203DC`, factory vtable `0x0030C878`. |
| `0x0030C888` -> `0x00287FBC` | Factory creation slot; allocates `0x334` bytes and calls constructor `0x00258694`. |
| `0x002586BC` | Installs manager vtable `0x00312780`. |
| `0x003127D8` -> `0x002466BC` | Concrete implementation of manager slot `+0x58`. |
| `0x002466EC` / `0x00246704` | Obtains the Application distributor via `0x00129350`, then calls its interface slot `+0x2C` with the selector. |
| `0x00246718` | A returned wrapper's primary slot `+0x0C` yields the integer; no record yields zero. |

**[CONFIRMED]** Application distributor factory `0x002A84E4` constructs a
`0x30`-byte object with `0x002616B8` and returns native object `+0x18`.
Constructor installs primary table `0x00312818` and secondary interface table
`0x0031284C`. Secondary slot `+0x2C` (`0x00312878`) is thunk `0x0026414C`,
which adjusts `this` by `-0x18`. The implementation adds the type prefix
`0x42000000` at `0x00264158` and tail-calls lookup `0x00263F50` with mode 1.
The App-SKU query is therefore **`0x284 -> 0x42000284`**.

### What the query matches, and how it ranks records

**[CONFIRMED]** Lookup checks the encoded type against the distributor type
at `0x00264020-0x00264028`. In mode 1 it iterates the distributor's native
`+8` list and calls `0x0023A590` on each wrapper's secondary interface at
`0x002640C8`. For this selector, the helper searches a sorted halfword
module/feature vector for **`0x0284`** (`0x0023A624-0x0023A690`).

**[HIGH]** "Module/feature selector" is the appropriate semantic category;
the exact vendor name of module `0x284` has not been recovered. There is no
evidence that `0x284` means MY14, REVA, or a specific App SKU.

**[CONFIRMED]** Matching wrappers expose an inner license record through
secondary slot `+8`. Lookup calls inner slot `+0x10`, then reads metadata
`+8` at `0x002640FC`. It tracks unsigned minimum SKU values, separately for
SKUs inside and outside configured `online_skus` intervals. Interval testing
at `0x00264108-0x00264118` is lower-inclusive, upper-exclusive. Return logic
at `0x0026406C-0x0026407C` prefers the outside-interval candidate when one
exists, otherwise the inside-interval candidate. Equal values retain the
earlier candidate. The running minima start at `0xFFFFFFFF`, and comparisons
are strict, so that sentinel value itself does not select a candidate.
The default configuration string at `0x00313A68` is `6`;
this is a configuration string, not the observed vehicle's App SKU.

Wrapper constructor `0x00252B9C` installs primary table `0x00310868` and
secondary table `0x00310888` at native `+4`. Its primary slot `+0x0C` is
`0x00262C30`: obtain inner metadata through slot `+0x14`, return metadata
`+8` at `0x00262C4C`. Its secondary slot `+8` is `0x0026283C`, returning
the inner license pointer. Both metadata accessors resolve to the same
address in the concrete record class (section 4).

The flag passed to App-SKU handling affects subsequent load/unload bookkeeping
(`0x00111004`, `0x0011103C`), not the selector or the metadata word returned.

## 3. SWID properties: correct the data-flow direction

**[CONFIRMED]** The named fields are registered on the **license manager**,
not established by these references as input fields parsed from `device.nng`.
Helper `0x00171628` registers names in a property map at manager `+0x288`.

| Name | String | Property / registration evidence |
| --- | --- | --- |
| `swid_info` | `0x003137FC` | Manager `+0x29C`, registered at `0x0025E554`. |
| `device_swid` | `0x00313808` | Manager `+0x264`, setup at `0x0025DD40-0x0025DD48`, registration `0x0025E56C`. |
| `application_skuid` | `0x00313814` | Manager `+0x2F4` is a property subobject, initialized at `0x002589B0-0x002589B8`, registered at `0x0025E584`. |
| `license_model` | `0x00313720` | Manager `+0x1D0` is another property subobject, initialized at `0x00258710`, registered at `0x002590F4`; it is not the scanner's numeric key. |

**[CONFIRMED]** Callback `0x0023FFD4` queries manager slot `+0x58` with
**selector zero** at `0x0023FFF8`, formats its result via `0x00142DCC` at
`0x00240004`, and updates the property at manager `+0x2F4` using
`0x0016EE2C` at `0x00240010`. It marks the property changed at
`0x0024001C-0x00240028`. Callback binding is present at
`0x0025E804-0x0025E858`.

In `0x002466BC`, selector zero is replaced with **6 or 7**, selected by
global `0x0032E344` (`0x002466DC` / `0x002466E0`). Thus the named property
and the logged `0x284` query share an implementation but **do not necessarily
return the same SKU**. No direct `application_skuid -> context +0x24` store
has been established; the proved flow runs from license records to each output.

### device.nng is a separate input

**[CONFIRMED]** Routine `0x00116178-0x00116574` reads and validates the device
file, with the familiar log at string `0x002F44C0`. Its compact parsed object
has identity fields at `+8/+0xC` and an `appcid` word at `+0x10`.
Helper `0x00105118` seeks file offset `0x5C` and reads four bytes; call
`0x001163CC` supplies the `+0x10` destination. The path also obtains
`ISECURE_TIMESTAMP_SAVER` (descriptor `0x003203C4`) and calls its slot
`+0x18` at `0x00116444`.

**[UNKNOWN]** This does not yet prove how `appcid` participates in each
record's validity evaluation. It does prove that it must not be renamed
App SKU merely because both are integers. Protected identity processing is
not emulated or reverse-engineered into reusable credentials here.

## 4. Scanner key: source-container ordinal, not SKU

**[CONFIRMED]** The scanner at `0x0011D454-0x0011DEA0` maintains sorted,
unique 32-bit values in context `+0x34/+0x38/+0x3C` (begin/end/capacity).
Entry resets the end pointer to begin. The Application distributor's
secondary slot `+0x28` (`0x00312874 -> 0x002723A0`) handles collection
selector `0x5FF`, encoding it as `0x420005FF`.

| Stage | Exact evidence |
| --- | --- |
| Device-side collection | Distributor query at `0x0011D4B8`; wrapper secondary `+8` at `0x0011D4FC` obtains the inner record. |
| Population filter | Record slot `+0x24` at `0x0011D50C`; nonzero already-valid records are skipped, zero-valued records reach key insertion. This vector is not a list of every installed license. |
| Inserted key | Record metadata through slot `+0x10` at `0x0011D524`; metadata **`+0x10`** loaded at `0x0011D54C`. |
| Media collection | Manager slot `+0x1C` at `0x0011D6E8` resolves to `0x002621DC`, copying the manager `+0x22C` list. |
| Candidate key | Inner metadata through slot `+0x14` at `0x0011D7F8`; metadata **`+0x10`** loaded at `0x0011D804`. |
| Activatable check | Record slot `+0x20` called at `0x0011D80C`. |
| Incompatibility | Binary search `0x0011DB58-0x0011DBA8`, equality comparison `0x0011DB90`; found key reaches incompatible handling at `0x0011DC48` and log `0x0011DCB4`. Absence reaches the GUI exception check, otherwise activable log `0x0011DC0C`. |

### Resolve the two metadata accessors

**[CONFIRMED]** Concrete license record constructor `0x00245080` initializes
a `0x78`-byte allocation (allocation site `0x00254164`) and installs table
`0x00311740` at `0x002450A0`. Table slot `+0x10 -> 0x002627CC` and slot
`+0x14 -> 0x002627E4` **both return `this +0x54`**. Therefore:

| Meaning | Metadata offset | Concrete license-record offset |
| --- | --- | --- |
| App SKU | `+8` | `+0x5C` |
| Scanner grouping key | `+0x10` | `+0x64` |

This independently excludes the hypothesis that different accessor offsets
made these two words aliases of one another.

### Trace the grouping key back to its creation

**[CONFIRMED]** The key is not merely an unnamed word observed near a parser.
Its full construction path is visible:

| Address | Assignment / relationship |
| --- | --- |
| `0x0026F938-0x0026F948` | New source-identity map-node insertion increments the map count at map `+4` (manager `+0x208`). |
| `0x00257D2C-0x00257D40` | Reads entry `+0x20`; if zero, initializes it from manager `+0x208`. |
| `0x00257D44` / `0x00257D54` | Passes that retained entry value as `r3` to container constructor `0x002577B8`. |
| `0x002577D4` / `0x002578B8` | Saves incoming identifier, stores it at container `+0x34`. |
| `0x002544E8-0x00254508` | Loads that container `+0x34` word and places it at temporary metadata `+0x10` (`fp-0x98`, with metadata base `fp-0xA8`). |
| `0x00245134` / `0x00245138` | License-record constructor copies supplied metadata `+0x10` to record `+0x64`. |
| `0x0011D54C` / `0x0011D804` | Scanner compares the same word from device-side and update-media records. |

The identity map is at manager `+0x204`, with count `+0x208` initialized
to zero at `0x00258748`. Routine `0x00257C28` forms a 16-byte lookup key
from provider slot `+0x40` output (`0x00257C64`) and container segment
offset/length (`0x00257C68-0x00257CD4`). Comparator `0x00133854` compares
16 bytes. Matching keys reuse an entry's assigned ordinal; a new entry gets
the current count after insertion. This is a manager/runtime-local allocation
scheme, not evidence of a persistent manufacturer-issued identifier.

**[HIGH]** The scanner groups records with the same source-container identity.
Provider slot `+0x40` is now resolved as a backing-provider accumulator (section 9);
equal ordinals must not be strengthened into "same filename" or "all bytes
identical" without resolving that provider. The traced populated-metadata
path also does not establish that every failure/partial-parse path has a
nonzero key.

## 5. Classifier outputs and caller evidence

**[CONFIRMED]** Result states are `0 = LICENSES_ALL_VALID`,
`1 = LICENSE_ACTIVATION_NEEDED`, and `2 = LICENSE_INVALID`. Once state 2 is
set, activation-needed does not overwrite it (`0x0011DC1C-0x0011DC28`).
Result object lists are `+4` accepted/valid, `+8` activatable, and `+0xC`
invalid/incompatible, with another list at `+0x10`.

**GUI exception [CONFIRMED]:** When an activatable record's key is absent,
`0x0011DBAC` calls GUI helper `0x00105194`. A true result branches at
`0x0011DBB4` to `0x0011DDE8`, loads result `+4` at `0x0011DDEC`, and rejoins
accepted-list insertion at `0x0011D8E8`. Thus `+4` is not exclusively a list
of records whose raw validity predicate was already true. Ordinary absent-key
records instead take the activable log/state-1 path. This qualifies the earlier
unconditional "absent means activatable" statement; it is not a bypass proposal.

**Important policy qualification [CONFIRMED]:** An invalid/incompatible record
is added to result `+0xC`, but sets enum 2 only when context byte `+0x51`
is zero (`0x0011D89C-0x0011D8AC`). Constructor `0x00114C5C` initializes both
context `+0x51` and `+0x52` to **one** (`0x00114D1C`, `0x00114D30`,
`0x00114D4C`); alternate constructor `0x00115F30` does likewise. Scanner
`0x0011D7AC-0x0011D7BC` copies these policy bytes into result `+0/+1`.
Thus enum 0 does **not** prove every record in every raw media file was valid.
This constructor policy supports discarding unsuitable records instead of
failing the entire multi-variant update. No named configuration switch or
modification procedure is established or proposed here.

Two direct scanner call sites are `0x001250F8` and `0x00125898`. Both obtain
the context through their parent's `+0xC8` pointer and that object's `+0x154`
field, and supply a result object initialized by `0x0012B2E8`. First caller
checks state 2 at `0x00125104` and state 1 at `0x00125170`; second saves
the state at `0x001258A4`.

### Container-wide pruning and filename propagation

**[CONFIRMED]** Discard adapter `0x00124D4C` obtains context from parent
`+0x154`, passes the result and supplied discard list, and tail-branches at
`0x00124D70` to `0x0012445C`. This explains why a BL-only caller search
does not find callers of the implementation itself.

When result policy byte `+0` is set, the first scanner caller transfers the
invalid/incompatible list into a temporary list (`0x00125354-0x001253A0`)
and calls this adapter at `0x001253B0`. The second scanner caller has the
equivalent path at `0x001267EC-0x00126850`. The first also discards the
activatable list when policy byte `+1` is set and enum is 1
(`0x00125164-0x00125208`). These are consumer paths, not inferred semantics
from a log string.

| Discard stage | Evidence |
| --- | --- |
| Identify container groups | `0x00124510` obtains each supplied record's metadata; `0x0012452C` reads metadata `+0x10`; `0x001246E4-0x0012477C` builds a sorted unique temporary key vector. |
| Remember source names | `0x001245DC` calls `0x00240C18`, which follows record `+0x28` to its container and copies the container's name subobject; `0x001245EC` converts the returned name and `0x00124618-0x001246D0` inserts it sorted/unique in context `+0x44/+0x48/+0x4C`. |
| Remove related result entries | `0x00124818-0x00124840` enumerates result lists `+4/+8/+0xC/+0x10`; `0x00124888` obtains metadata; `0x00124898` addresses its `+0x10` key; matching entries are unlinked at `0x00124ABC-0x00124AD8`. Thus a discarded group's already-valid records can also be removed. |
| Notify license manager | `0x00124998-0x001249F8` constructs arguments from the stored names and calls manager slot `+0x28` (`0x003127A8 -> 0x0024BFDC`). |
| Change the file plan | `0x00124A88-0x00124A98` registers callback `0x00113160` with the parent enumerator through `0x001049AC`. The callback compares the plan entry's name with context `+0x44` at `0x0011321C`. On equality, it releases the entry's associated object at `0x00113338` and clears entry `+8` at `0x00113340`. |
| Diagnostic anchor | `0x001247F4` references `0x002F5340`, the record-discard count log. Callback `0x00113304` references `Removing file from file copy: <%s>` at `0x002F40A4`. |

Callback `0x00113160` first checks the supplied path against context `+0xC`
and requires the entry's associated object to have category 2 at `+0x40`
(`0x00113174-0x001131B8`). The filename comparison is only reached after
those gates. These details prevent incorrectly treating it as an unconditional
filesystem deletion routine. All changes described here are operations of the
vendor's update code; this analysis never invokes them.

**[HIGH]** This is container/file-level exclusion implemented through record
groups: unsuitable records can exclude related records and matching planned
files from further consideration. It supplies the connection from license
classification to multi-file variant filtering. It is not a filename-based
MY14 lookup or an equality comparison between App SKU and the container key.

**[CONFIRMED]** A separate downstream consumer reads the logged App SKU from
context `+0x24` at `0x00125A44` and passes it to the existing request-code
routine at `0x00125A4C`, after classification. This is an interface-boundary
observation only; request-code computation and values are out of scope.

Activation/request-code handling is a separate, subsequent process. No
activation material, validity-rule patch, credential derivation, or bypass
is part of this analysis.

## 6. What explains MY14 REVA, and what does not

**[CONFIRMED]** Installer configuration uses device license directory
`/fs/mmc0/nav/NNG/license` and media directory `license`. The `[update]`
`sku_compatibility` configuration matches product/database family strings
(CMC/FCAVP, VP3/VP4, NA/EU/ROW and EU/EUGCM aliases). It contains no MY14,
REVA, or numeric App-SKU mapping. Its parser at `0x00120538` reads the
configuration name via `0x0012056C` and populates destination `+0x20`
through `0x0011FE84` at `0x0012060C`. This string-pattern compatibility
must not be equated with the license-record SKU query.

Printable-string search of the ELF found no MY14, REVA, 2017Q2, 68224525,
or `opennav_fiat` literal. That is a bounded negative observation, not proof
that no model-specific policy exists in license data.

**[CONFIRMED]** The update's recovered outer log contains the successful
MY14 filename in pre-MD5, copy, and post-MD5 events (the recovered file has
bit corruption; not all occurrences are pristine). It reports the part-number
transition `68224525AH -> 68224525AM` and resulting software `17.11.17`.
It does not contain the internal `App SKU ID` diagnostic or a record-level
classification trace.

### Attempt to recover the missing diagnostics from the original image

**[CONFIRMED]** `analysis_tools/synctool_log_probe.py` scanned all
**16,034,824,192 bytes** of `uconnectmapimage.img` read-only, including bytes
outside currently recovered files. It found nine exact marker occurrences:
six App-SKU/device/record-classification/file-exclusion format strings and three `Discarding`
prefixes (one formatted count, two other embedded strings). No hit had a
runtime-looking numeric App SKU, device-validity value, or substituted record
name. The App-SKU format string occurred at image offset `0x010DCE48`;
record-state strings were at `0x010DDA88`, `0x010DDAB4`, and `0x010DDAE4`.

This excludes intact plain-text diagnostic messages containing these exact
markers in this image, not compression, fragmentation across a marker,
corruption, different diagnostic spelling, or logs stored only on the radio.
The probe prints offsets/categories and optional numeric SKU only; it does
not dump surrounding log contents or protected material. It now also computes
a full SHA-256 token for a complete printable value in the known
angle-bracket record/file fields. This can correlate repeated runtime values
across classification and file-exclusion events without emitting the value.
Matching tokens are strong evidence of equal field bytes; they do not prove that
a record name, container identity, or filename has a particular semantic role.

The new token path and synthetic boundary tests are committed but have not been
executed under Python because the local command service is unavailable. The
86-test result below records the last executable suite before this enhancement;
it must not be read as verification of the new tests.

The recovered outer `swdlLog_recovered.txt` was separately scanned in full:
1,043,885 bytes, zero marker hits. The compiled installer Lua's printable
launch-related strings did not establish a dedicated Synctool diagnostic-file
path in that earlier pass. Section 8 now identifies the configured endpoints
through the logger and installer INI. Do not assume that the outer SWDL log
captures either endpoint.

**[INFERRED]** The file's MY14/REVA label describes how the vendor packaged
compatible records; a literal filename/model-year switch in this Synctool
has not been found. Device-specific validity still comes from the existing
license-manager validation path, not from comparing the filename with the
vehicle model year.

The concrete next evidence target is an existing **Synctool diagnostic log
from this successful run** (or an owner-provided, read-only installed-license
inventory with non-secret SKU/module and record-state diagnostics). It should
correlate the App-SKU query, per-file record classifications, and final copy
plan. Such observations would tie the recovered mechanism to the exact MY14
file without deriving protected license contents or generating activation
material. The `device.nng` `appcid` alone is not enough to make that mapping.

## 7. Reproduction and verification

From the repository root, with Python 3 and Capstone installed:

```powershell
python -m analysis_tools.synctool_evidence analysis_work/Synctool.elf --verbose
python -m analysis_tools.arm_elf_analysis disasm analysis_work/Synctool.elf --start 0x11A9B4 --end 0x11A9DC --literals
python -m analysis_tools.arm_elf_analysis words analysis_work/Synctool.elf --start 0x3127D8 --count 1
python -m analysis_tools.arm_elf_analysis disasm analysis_work/Synctool.elf --start 0x257D2C --end 0x257D58
python -m analysis_tools.arm_elf_analysis disasm analysis_work/Synctool.elf --start 0x11331C --end 0x113344
python -m analysis_tools.synctool_log_probe uconnectmapimage.img --max-hits 30
python -m unittest discover -s analysis_tools/tests
```

Verification passed **86 analysis-tool tests** and **83 selected real-ELF
evidence anchors**, using Python 3.14.4 and Capstone 5.0.9. Anchors cover
instructions, vtable entries, and property/log names. Tests use synthetic
fixtures, not vendor files. The [tooling guide](../analysis_tools/README.md) documents scan
limitations, dependencies and additional CLI modes. For the full existing
test suite, `cryptography` was installed only under ignored
`analysis_work/test_deps` and that directory supplied through the test process's
`PYTHONPATH`; the system Python installation and vendor inputs were unchanged.

No direct parser/validation execution, license normalization, credential
derivation, image repair, firmware patching, or radio flashing was performed.

## 8. Internal logger: sink implementation and configured destinations

**[CONFIRMED]** The investigated messages share logger `0x00143694`:
App SKU call `0x00110FF4`, invalid record `0x0011D86C`, activable record
`0x0011DC0C`, incompatible record `0x0011DCB4`, discard counts `0x00124804`,
and file exclusion `0x00113310`. The App-SKU descriptor has category `synctool`
(string `0x002F36C4`) and numeric severity 3. Do not invent a vendor severity
name or assume a separate "Found valid" message exists.

| Boundary | Direct evidence |
| --- | --- |
| Singleton and formatting | Global `0x00320440`; constructor `0x001435D4`, allocation `0x2040`. Call `0x001436DC -> 0x0013643C`; `0x0013647C -> 0x00103C10`, resolved through ELF REL/PLT to `vsnprintf`, with capacity `0x2000`. |
| Fan-out | Logger `+0x2004` heads a sink chain terminated by `-1`. `0x001364B0-0x001364CC` calls each sink's slot `+8`, following sink `+4`. |
| Early buffer | Constructor `0x001434A8` installs table `0x002F7298`; slot `+8 -> 0x00143404` copies descriptors and duplicates message text into a linked list. This is process memory, not persistent logging. |
| Configuration | `0x00142780` reads wide `debug` (`0x002F5674`) and wide `log_%d` (`0x002F81D8`), iterating 1 through 10; colon delimiter `0x002F7910`, numeric level conversion `0x00142C08`. |
| Stdout special name | Exact `stdout` selects constructor `0x00130458`, table `0x002F6B58`, sink `0x00136D58`; tail `0x00136D90 -> printf` at PLT `0x00103E20`. |
| File/path sink | Other names select constructor `0x001304E8`, table `0x002F6B28`, slot `+8 -> 0x00136EC4`. Name stored at sink `+0xEC`; `0x00136EE8 -> fopen64` (`0x0010376C`) with mode `a`; message write `0x00136F3C -> fwrite` (`0x001035B0`); close tail `0x00136F5C -> fclose` (`0x00103970`). |
| Filtering | `0x001333CC` rejects severity greater than sink `+0xD4` (`0x001333E8`), and can apply a category filter at `+0xD8`. |
| Buffered replay | `0x00142A18-0x00142A64` replays buffered entries to configured sinks. `0x00142A68-0x00142A80` destroys the early buffer. No configured sink can mean no retained messages. |

The new `imports` mode reproduces C-library symbol resolution without executing
firmware or assuming PLT entry ordering. It supports the classic ARM stub shape
and ELF32 REL jump-slot entries; an empty result for another linker/ISA is not
proof that a binary imports nothing.

**[CONFIRMED, configuration not historical execution]** In the hash-identified
2017Q2 installer ISO, `usr/bin/nav/NNG_Synctool/sync_main.ini` configures:

- `[debug] log_1`: `/dev/stdout::3`
- `[debug] log_2`: `/hbsystem/multicore/navi/3::3`

Both are *path* sinks, including `/dev/stdout` (different from special name
`stdout`). These diagnostics therefore go through append-open/write/close to
stdout and the Harman navigation trace endpoint when this configuration is
applied and the opens succeed. Neither destination is an ordinary persistent
Synctool log pathname proved by this ELF. The separate `server_logging`
configuration names navigation channel `/4`; it must not be substituted for
the internal logger's `/3` channel.

Installer `usr/share/scripts/navi-sync.sh` starts Synctool in its directory
without redirecting its standard streams. This script alone does not identify
the inherited stdout consumer. It also does not prove that this was the only
launcher used by the successful run. QNX slog, stderr, direct socket output,
and a dedicated diagnostic-file rotation policy are not established for these
logger calls; stdout/endpoint handling can occur downstream in other processes.

### Follow the concrete /hbsystem lead, with version separation

**[CONFIRMED for recovered RA4 18.45.01 only]** Its boot script
`analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/files/bin/boot.sh`
has SHA-256 `c801d473b0b49e8242114635f4022cc67ccbe03093fec188de3b7188dd636ecf`.
Lines 169-207 route navigation channel `/3` to `/dev/null` when logging is
disabled, or start `multicored` mounted at `/hbsystem/multicore`. Existing
capture configurations name `/fs/mmc1/LOGFILE.DAT`, `/fs/usb0/LOGFILE.DAT`,
or `/fs/sd0/LOGFILE.DAT`; another branch supplies no explicit capture file.
These are read-only artifact leads, **not instructions to enable logging**.
The observed boot capture limit is 524,288,000 bytes, far beyond the new
application storage budget; it must not be adopted as an application default.

The recovered `multicored` binary imports resource-manager/socket facilities
and contains logfile, ring-buffer, index and old-file diagnostics. This supports
the **[HIGH]** interpretation of `/hbsystem` as a diagnostic-service namespace,
not an ordinary disk directory. No retrospective `cat` of the write endpoint
is recommended. Full daemon retention/rotation and historical BOLO routing
remain **[UNKNOWN]**. This later firmware's boot policy cannot establish that
any `LOGFILE.DAT` was recorded during the 17.11.17 update.

## 9. Provider +0x40: composite filesystem identity, not protected payload

**[CONFIRMED]** The provider retained in loader source descriptors comes from
`IFILESYS`, not from a license-record SKU or device identity property:

| Stage | Address / layout |
| --- | --- |
| Registry | Helper `0x001292C0` obtains descriptor `0x003203CC` (`IFILESYS::NAME()`). |
| Filesystem construction | Registration `0x001BA704-0x001BA72C`, factory table `0x003043C0`, creation slot `0x003043D0 -> 0x001CF260`, constructor `0x001C4AD4`, installed table `0x00305348`. |
| Logical provider lookup | Filesystem slot `+0x10` (`0x00305358`) is `0x001C44B0`. It looks up a name in its provider map, or allocates `0x2C` bytes at `0x001C45D0`, constructs via `0x001C0F40` at `0x001C45E0`, and retains the result. |
| Installed provider table | Constructor `0x001C0F5C` installs `0x003052D8`. Slot `+0x40` (`0x00305318`) is `0x001B5070`. |
| Identity operation | `0x001B5070` iterates provider map `+0x10`, obtains each entry's backing object at `+0x14`, and calls its **slot `+0x38`** at `0x001B50A8-0x001B50AC`. It forwards the same source descriptor and 16-byte output accumulator. |

**[HIGH]** "Composite logical-filesystem provider" is a descriptive class name;
the stripped ELF does not recover its original C++ class name. This operation
updates a caller-supplied four-word accumulator, not a returned integer ID or
a pointer to 16 bytes of license content. The license manager subsequently
mixes the segment offset and length at `0x00257C68-0x00257CD0` and assigns a
runtime map ordinal as already documented in section 4.

**[CONFIRMED, one concrete backing implementation]** `IROOTDIR_FACTORY`
constructor `0x001B5364` installs `0x00304950`. Slot `+0x20`
(`0x00304970 -> 0x001B61B4`) constructs a `0xC`-byte backing object with
table `0x003047A0`. Its slot `+0x38` (`0x003047D8`) is `0x001C9D30`.
This implementation reads the source descriptor's name at `0x001C9DA0`,
converts its 32-bit character units to 16-bit units through `0x001312F8`
(`0x001C9DC8`), and mixes the name, including its terminator, into the four-word
accumulator. The implementation's data flow does not read file content, an
inode, a device SWID or a license credential. Its arithmetic is not implemented
as a tool here; no protected container is decoded.

**[UNKNOWN]** The successful run's complete registered backing-provider set
and ordering are unavailable. This concrete name-mixing implementation must
not be promoted to proof that it was the sole contributor. Even with that
provider alone, a finite accumulator can collide: equal ordinals prove reused
map identity within one manager instance, not identical source filenames,
complete bytes, or a persistent ID comparable between different runs.

## 10. Source descriptor to copy-plan filename, without license decoding

**[CONFIRMED]** `0x00260D4C` enumerates logical license sources. In its first
path, `0x00260EBC` calls `IFILESYS +0x10` with logical provider name `app`,
from wide `%app%license` at `0x00313B44`. Enumeration helper `0x0023DF10`
retains the provider at list node `+8` (`0x0023DFC4`) and the enumerated name
at node `+0xC` (`0x0023DFC8`). This is directory/source metadata, not a value
decoded from the protected `.lyc` body.

Loader `0x00257E34` reads that provider/name pair. It puts the provider at
source descriptor `+4` (`0x00257FB0`), copies the name at descriptor `+0`,
and compares the source extension with wide `lyc` at `0x00313B98`.
For `.lyc`, it reads successive eight-byte outer segment headers at
`0x00257FE0-0x00257FFC`; the current position returned at `0x00258014`
becomes descriptor `+8` at `0x00258024`, and the declared segment length
becomes `+0xC` at `0x00258020`. The descriptor is passed to `0x00257C28`.
Only the loader's static control/data flow is inspected, not protected content.

Container constructor `0x002577B8` copies the name and retains descriptor
fields `+4/+8/+0xC/+0x10`. Record construction saves the container pointer
at `0x002540B8`, forwards it in `r3` at `0x00254174`, and stores it in
record `+0x28` at `0x002450AC`. Thus **record `+0x28` is a container
backpointer**, not an inline filename or a bare C string. Name helper
`0x00240C18` follows it and copies the name at container `+0`. This completes
the missing provenance link to section 5's discard-name vector and copy-plan
filename comparison. It does not identify a historical runtime container
address or ordinal for MY14_REVA.

## 11. Selector 0x284: bounded follow-up result

**[CONFIRMED]** Immediate filtering found seven ARM candidates for `0x284`:
the query at `0x00110FB8` and six structure-offset ADD instructions at
`0x0023B2FC`, `0x0023DE90`, `0x0025D3CC`, `0x0025DD78`, `0x0025F2A8`,
and `0x0025FD38`. Those offsets do not establish module aliases. Aligned word
searches found no literal `0x00000284` or `0x42000284` table entry in the
file-backed load segments. Synthesized constants, packed halfwords, indirect
tables and other binaries are not excluded by these negative checks.

The Application distributor registers `has_module_license` at
`0x0026196C-0x00261980` (name `0x00313828`). Together with the proved encoded
query and halfword membership lookup, this supports the **[HIGH]** module/feature
interpretation and Application subsystem ownership. The vendor feature name,
and any claimed meaning such as MY14, remain **[UNKNOWN]**. No name is invented.

## 12. Result class and read-only evidence plan

**B - PARTIALLY PROVED.** Static evidence now connects source enumeration,
composite provider identity, segment descriptors, record container backpointers,
group pruning and filename exclusion. It also identifies configured diagnostic
destinations. The independent runtime log proves the MY14_REVA copy. Still absent
are that run's selected App SKU for module `0x284`, per-file record predicates,
the device-side ordinal set, backing-provider configuration, and associations
between those values and the MY14_REVA container. These independent facts do
not establish a numeric MY14 selection rule or a category-A result.

Highest-value read-only target: an **already recorded Harman multicored capture
from the successful update**, with its matching index/old-file companions and
timestamps if present. Check existing owner archives or radio/media inventories
for the three `LOGFILE.DAT` paths in section 8. A named artifact was not found
in the inspected recovered RA4 file inventory or the final repository-wide
filename-only `*LOGFILE*` / `*logfile*` check (including ignored evidence,
excluding Git/dependency directories). No new blind raw-image scan was run.
The original image's prior intact-marker scan remains relevant.

Record the current version, existing `/hbsystem/multicore/navi/3` link/resource
mapping and logging configuration as context only. Do not create flags, change
configuration, mount writable, start a logger, rerun an update, or request an
activation operation. The endpoint itself is not proved to support reading
past records. The current QNX slog buffer is not established as this logger's
sink, so it is not the primary collection recommendation.

Disk capture files may survive reboot, but daemon reuse/rotation can overwrite
them; exact retention is unproved. Process buffers and uncaptured streams
cannot be assumed to survive process exit, ignition cycling or reboot. If the
historical messages went to `/dev/null`, that path retained nothing to recover.
Any available capture should be copied **off-radio**, without staging a large
archive inside the approximately 77 MB free-space pool.

Extract only non-secret `synctool` App-SKU/category/severity messages, source
filenames, valid/activatable/incompatible/invalid classifications, discard counts
and copy-plan exclusions. Standard messages may still lack per-record module
membership, ordinals or the selected-record-to-filename relationship. If so,
completion needs an **existing, legitimate non-secret diagnostic inventory**
correlating source name, segment bounds, module membership, SKU and classification
within the same run. No such inventory interface/path is yet established;
do not claim that a plain App-SKU log alone closes the mapping.
