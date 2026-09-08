# Performance Pages investigation verification

Date: 2026-09-08. Investigation baseline:
`116d14823e426cdcab6edd9e97ac3f86cbac7f2b`.

## Isolation and pre-analysis verification

**PROVED:** the new worktree
`E:/Documents/GitHub/jeep_uconnect_custom_performance_pages_media` was created
on `codex/performance-pages-media-capability` from the exact requested commit.
Its initial status was clean. No investigation edits were made in the completed
Yelp worktree or the original dirty checkout.

**PROVED:** before creating the worktree, the original checkout was recorded
using the established NUL-delimited porcelain and binary-diff SHA-256 mechanism,
with `GIT_OPTIONAL_LOCKS=0`. Its HEAD was
`894afe8e5361c3595623de599e62ba0f0c0d9f78`, with 40 tracked modifications and one
untracked file:

| Item | SHA-256 |
|---|---|
| NUL-delimited porcelain status | `48adcf412315324596610736df3a34d484f517df288741475434205fb4fc4ee4` |
| Binary diff | `d640dce2da93cbd40692549754f74ee796b897b00d5a38060d4ad17172cdc792` |
| Untracked `docs/00_project_status.md` contents | `9ab7efecc3a09b2b25fbed81091577a6cee10a2c7d669ab7635fc46994362d78` |

**PROVED:** Windows Git initially checked out LF text as CRLF. The first baseline
test attempt exposed missing host Python modules and the resulting Yelp report
freshness mismatch. Only the new worktree's tracked text was normalized back
to its committed LF bytes; no legacy content correction was needed. Existing
local analysis dependencies were used through `PYTHONPATH`, with
`PYTHONDONTWRITEBYTECODE=1` to avoid writes to the dependency checkout. No package
download was required. Git index normalization produced no staged changes.

**PROVED:** before new artifact analysis, the existing KIM19 generator verified
all eight reports with JDK 8u504 `javap`; the separate Yelp generator's `--check`
also passed. The runtime generator re-inventories KIM19 and verifies recovered
source hashes before and after extraction. All 23 pre-existing report JSON files
were independently compared byte for byte against the exact Git baseline.

Baseline commands, from the isolated worktree:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONPATH = 'E:/Documents/GitHub/jeep_uconnect_custom/analysis_work/post_reboot_20260906/venv/Lib/site-packages'
$corpusWork = 'E:/Documents/GitHub/jeep_uconnect_custom/analysis_ra4_18.45.01/work'
python -m unittest discover -s analysis_tools/tests
python -m unittest discover -s prototype/hello_uconnect/tests
python -m unittest discover -s prototype/network_probe/tests
node --test prototype/resident_hmi/tests/*.test.mjs
python -m analysis_tools.kim19_runtime_analysis --work $corpusWork --output reports/kim19_runtime_analysis --javap javap --check
python -m analysis_tools.yelp_observation_analysis --check
```

**PROVED baseline results:** 264 analysis tests, 18 Hello artifact tests,
17 network-probe host tests, and 20 JavaScript tests passed. The strict C99 host
build and its executable also passed under the existing Ubuntu/WSL compiler:

```powershell
wsl -d Ubuntu -- sh -lc 'cd /mnt/e/Documents/GitHub/jeep_uconnect_custom_performance_pages_media && cc -std=c99 -Wall -Wextra -Werror -pedantic prototype/projection_arbiter_c/projection_arbiter.c prototype/projection_arbiter_c/test_projection_arbiter.c -o analysis_work/performance_pages_verification/projection_arbiter_test && analysis_work/performance_pages_verification/projection_arbiter_test'
```

These are repository host tests; no vehicle application or recovered class was
executed. The pre-analysis local Markdown file-link check validated 401 links
with no broken targets. The original-checkout fingerprint still matched.

## Final tests and reproducibility

**PROVED:** the final full suite passed without failures or skips:

| Suite | Passed |
|---|---:|
| `analysis_tools/tests` | 287 |
| Hello artifact tests | 18 |
| Network-probe host tests | 17 |
| Resident-HMI JavaScript tests | 20 |
| Strict C99 arbiter build/executable | All assertions passed |

The Python total is 322. The analysis suite includes all 23 new tests:
11 export-schema/provenance/CLI tests, seven consumer-census tests and five
native-storage tests. They cover real synthetic classfile/JAR parsing, mismatched
source/class/invocation evidence, incomplete handoff claims, substring reader
detection, duplicate members, malformed classes, disclosure filtering, strict
JSON, unsafe output destinations, deterministic bytes and read-only freshness
checks. Synthetic fixtures are host evidence tests, not vehicle files.

**PROVED:** the final producer generation verifies 30 source records and 63
class/method bindings (57 producer, six storage), including exact class hashes,
method descriptors, instruction counts and selected BCI/member/literal tuples.
It emits five report families covering three variants, 16 HTML fields, seven
failure signatures and five consumer/handoff candidate records. The independent
consumer census parses all 23 selected JARs and 7,384 class entries with zero
errors. It records broader candidate APIs but does not infer a handoff from
their presence. The native supplement rechecks the exact EcoDriveSvc hash and
extracts eight function hashes, six non-sensitive literals and fifteen ARM
windows. No source binaries or full disassembly dumps are committed.

**PROVED:** all seven new JSON reports were regenerated and then successfully
checked from the recovered sources. The final producer notes additionally
preserve the distinct older `unava|lable.` and L-Series `unavailable.` packaged
spellings. A check performed between that final note correction and regeneration
correctly reported stale output; regeneration and the subsequent check passed.

```powershell
python tools/analyze_performance_pages_export.py --corpus $corpusWork
python -m analysis_tools.performance_pages_consumer_census --corpus $corpusWork
python -m analysis_tools.performance_pages_native_storage --corpus $corpusWork
python tools/analyze_performance_pages_export.py --corpus $corpusWork --check
python -m analysis_tools.performance_pages_consumer_census --corpus $corpusWork --check
python -m analysis_tools.performance_pages_native_storage --corpus $corpusWork --check
```

**PROVED:** the eight existing KIM19 reports and the separate Yelp report were
also regenerated and checked successfully. All 23 pre-existing JSON report files
remain byte-identical to Git baseline `116d14823`, including earlier retained
inventory/assessment evidence. Earlier broad firmware censuses were not rerun:
their bytes were preserved, while the current generator rechecked the relevant
KIM19/common-base/source manifests. This maintains the requested focused scope.

**PROVED:** `.gitattributes` now requires LF for JSON, preventing the Windows
checkout conversion that caused the initial baseline freshness mismatch. All
seven new reports decode as ASCII, contain no CR bytes and end with LF.
Markdown file-target validation checked 442 local links with zero broken
targets. Whitespace checks passed. No recovered JAR, class, firmware payload,
credential value or signature material is included in the intended changes.

**PROVED:** the final original-checkout audit matches all three recorded
SHA-256 values and its original HEAD exactly. The investigation did not stash,
restore, reset, clean, switch files, stage, or commit in that checkout. Git
commits and the requested push are confined to the new investigation branch.
The final commit identifiers and remote-ref verification are reported with the
completed investigation; no recursive self-hash is embedded in this record.

## Stopping assessment

**INFERRED:** Outcome A is supported within the recovered scope: a constrained
Level 2 timer-report export and no established useful signed consumer/handoff.
The conditional VSB contract follow-up was completed after that boundary was
established. No result promotes a capability above Yelp or establishes generic
file or message authority for another caller.

**UNKNOWN / TARGET OBSERVATION REQUIRED:** actual variant activation, grants,
mounted writable media, platform locale fallback, L-Series missing-title
resource behavior, durable file bytes and any off-unit or unrecovered reader.
No vehicle, recovered endpoint, live backend or message service was contacted.
