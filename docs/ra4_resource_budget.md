# RA4 resource budget: stock-system headroom comes first

Updated: 2026-09-05. Mandatory product constraint; supersedes earlier assumptions
that a hidden external computer should render the entire modern HMI by default.

The owner reports approximately **77 MB free writable internal storage**. This
is an approximate observation, not a measured application allocation or proof
that all writable mounts share one pool. Filesystem, units, observation date,
boot state and stock usage variation still need recording. Use decimal MB for
the planning table; future measurements must report bytes and identify the mount.

## Provisional envelope, before implementation

Protect **45 MB for stock-system operation** until representative measurements
justify revising the reserve. Do not shrink it merely to accommodate a feature.
The owner's 35-45 MB reserve range is implemented at its conservative upper end.
The 15-25 MB preferred installed maximum is a ceiling range, not a target to
fill: initial design uses **15 MB total installed**, including private libraries.

| Resource | Planning allowance / cap (MB) | Measured size |
| --- | ---: | --- |
| Core application / integration code (resident technology conditional) | 5 | Not built |
| Minimal custom UI assets | 3 | Not built |
| New private native dependencies | 2 | Not selected/built |
| Small support files and packaged configuration defaults | 1 | Not built |
| Installed-size uncertainty margin | 4 | Not applicable |
| **Installed total** | **15** | **Unknown; no deployable artifact** |
| Mutable configuration | 0.25 | Unknown |
| Persistent application state | 1.25 | Unknown |
| Logs, including rotation files | 1 | Unknown |
| Cache and normal temporary files, combined | 1.5 | Unknown |
| **Runtime writable growth total** | **4** | **Unknown** |
| Additional peak staging / rollback / update overhead, combined | 8 | Unknown; release gate |
| **Maximum planned simultaneous app usage** | **27** | **Unknown** |
| **Protected stock-system reserve** | **45** | Usage variation unmeasured |
| **Additional unallocated margin at planned peak** | **5** | Depends on actual free space |

Planning arithmetic: 77 - 15 - 4 = **58 MB remaining in steady state**;
77 - 15 - 4 - 8 = **50 MB at the proposed peak**, of which 45 MB stays protected.
These are allocation estimates, not claims about existing binaries or measured
runtime behavior. Any future proposal must supply its own installed, persistent,
log/cache-growth and peak-update estimates against this envelope.

The 8 MB update allowance is **not proof that an updater will fit**. A second
complete 15 MB installation plus runtime growth would leave only 43 MB, violating
the reserve even before other staging. No full duplicate install/rollback may
be assumed. Measure the actual simultaneous old/new/temp/rollback footprint
before selecting an update mechanism; if it cannot fit, reduce the product or
separate staging from internal storage through an authorized design. No flashing,
installation or radio-state changes are authorized by this budget document.

## Resident-first deployable architecture

Tiny RA4-resident projection integration -> stock application arbiter, navigation
stack, popups, camera, display, touch, audio and vehicle services -> optional
external projection engine only where local feasibility is disproved or exceeds
the conservative storage/compute envelope.

The maximum credible initial local scope is one lightweight projection
application/screen plus session, foreground, return and notification arbitration.
The six-screen PC scaffold is not a resident product requirement. Stock screens
remain responsible for media, settings and comfort controls. This is a feasibility
target, not a validated interface or claim of installability.

Reuse existing QNX/Harman services, native platform libraries, fonts, graphics,
icons, codecs and media databases where their availability, ABI and permitted
reuse are verified. Reuse has **zero new installed bytes only when genuinely
using stock files**; runtime service state and cache growth still count. Exact
dependency identities, ABI compatibility and incremental sizes remain unknown.
Do not bundle Electron, Chromium, a browser, large language runtimes/frameworks,
duplicate stock libraries/assets, maps, media libraries or speech models.

A PC prototype may use mocks and development tooling, but those dependencies
must be outside the deployable package and replaceable through small explicit
interfaces. No PC-only renderer may silently become the required production HMI.
Storage fit alone does not prove RAM, CPU, graphics or latency feasibility;
measure those separately before committing to the resident feature set.

## External capability ledger

| Capability | Current disposition | Reason / evidence needed |
| --- | --- | --- |
| Tiny stock-facing projection integration | RA4-resident feasibility target | Reuse stock screens, arbitration, popup/camera layers and services; ABI/performance/access remain unverified. |
| Bundled map/media databases or speech/AI models | `EXTERNAL_COMPUTE_REQUIRED` if a feature requires bundling these large datasets locally | Excluded from this app footprint; prefer existing stock/phone services before adding external hardware. This label covers separation from the radio, not a requirement to buy a separate box. |
| New CarPlay / Android Auto projection engine | Local feasibility **UNKNOWN**; not budget-approved | No sized, legitimate compatible engine/build has been identified. Existing HMI references are not a complete backend. Measure storage, RAM, CPU and required facilities; classify `EXTERNAL_COMPUTE_REQUIRED` if they exceed limits, never promise future optimization. |
| PC development tools / firmware analyzers | Development host only | Not part of the deployable app or its footprint. |

Do not introduce external compute as the default renderer merely because it is
easier. First establish the largest supported local feature set. Every feature
that fails the budget/compute gates must be explicitly classified, reduced or
removed; it must not borrow the stock reserve.

## Measurement and release gates

Maintain this document as builds appear: inventory every installed file and
private dependency by allocated bytes as well as logical size, identify reused
stock assets/libraries, and record steady/peak writable use on the actual mount.
Log and cache bounds must include rotated files, crash/recovery data and failed
operations; discardable app data cannot justify deletion of stock state.

Use existing read-only observations where available to measure free space across
boot, ordinary UI/navigation use, Bluetooth/phone sessions, stock log/cache growth,
and safely observable software/update operations. Do not trigger an update or
alter the radio merely to collect a measurement. Account for minimum observed
free space rather than the most favorable idle reading. No release may assume
the provisional peak fits before it is measured, including failure/rollback.

Synctool research currently installs **0 bytes on the radio** and causes **0
bytes of radio writable growth**. Potential historical diagnostic captures can
be much larger than this budget; collect existing artifacts off-radio without
creating an internal staging archive or enabling high-volume logging.

## Projection-integration scaffold, corrected 2026-09-06

The [resident decision](resident_hmi_decision.md) now compares stock AIR/SWF,
native QNX and hybrid before committing to a language. The preferred stock-AIR
trial targets <=3 MB installed, <=1 MB normal writes and <=6 MB additional
staging/rollback peak. These are unmeasured sub-targets, **not a change to the
45/15/4/8/5 MB envelope**. Estimated peak remainder is about 67 MB, including
45 MB protected and 22 MB extra headroom. Full simultaneous file/dependency,
runtime-generated log/cache and failed-update accounting remains a release gate.

The refocused projection-ownership bench has no private package dependencies or
bundled font/icon/image assets. Its current candidate source tree was counted directly
from the 11 committed Git blobs: **29,341 logical bytes**.
Estimated allocation at 4,096-byte units is **53,248 bytes**, excluding filesystem
metadata. This is a source-tree count, not an RA4 installed-size measurement.
It replaces the earlier six-screen source count; browser/Node/Python remain host
tools and are not deployment dependencies.

All measured RA4 installed, writable and temporary bytes remain UNKNOWN because
no target artifact exists. This work installs zero bytes on the radio and makes
no radio writes. Re-run `hmi_size_report` locally when command execution is
available to independently verify the Git-blob count.

For a future complete staging directory, the reporter's `--kind target-package`
requires explicit `--writable-bytes` and `--temporary-bytes`, then checks the
existing caps and reserve. It counts host logical bytes and estimates allocation
with `--allocation-unit`; actual target allocated bytes, filesystem metadata,
shared service growth and stock free-space behavior must still be measured.
