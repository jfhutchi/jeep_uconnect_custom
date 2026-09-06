# Resident HMI feasibility implementation plan

> For agentic workers: use executing-plans inline. User requests autonomous
> implementation, a dedicated branch and an unmerged PR; no review pause or
> additional worktree is required for this run.

**Goal:** Demonstrate a six-screen, 640x480 mock shell without selecting a PC
runtime as a deployable RA4 dependency.

**Architecture:** Prefer reuse of stock AIR/SWF, conditional on supported loading,
service access and fallback. Keep data, state transitions and command policy
separate from a replaceable, PC-only HTML renderer. No target transport exists.

**Tech stack:** Dependency-free JavaScript modules; Node built-in tests; Python
standard-library size accounting. Browser and Node are development tools only.

## Tasks

- [x] Read existing architecture, HMI/interface reports and primary boot/config
  evidence. Confirm PR #12 is open and base this branch on its unchanged tip.
- [x] Verify baseline: `python -m unittest discover -s analysis_tools/tests`
  with the existing ignored test dependency path; 86 pass.
- [x] Create `prototype/resident_hmi/tests/model.test.mjs` first. Cover six
  routes, pending versus observed state, command bounds/capabilities, freshness,
  camera/fallback, disconnect, timeout and late responses. Run
  `node --test prototype/resident_hmi/tests/*.test.mjs` and observe missing API.
- [x] Implement `model.mjs` and `mock-adapter.mjs`. Only an observed snapshot
  changes vehicle values; rejection/timeout/preemption discard pending intents.
  Re-run tests after each connected behavior group.
- [x] Add `view.mjs`, `app.mjs`, `index.html`, `style.css`: fixed 640x480 logical
  layout, six routes, >=48px controls, original text/CSS assets, PC-only scenario
  controls. Test rendered routes and use a browser for visual/interaction checks.
- [x] Test then implement `analysis_tools/hmi_size_report.py`: count file bytes,
  explicitly estimated allocation units, fail budget overflow, keep absent RA4
  artifacts UNKNOWN. No packaging, upload or filesystem modification.
- [x] Write `docs/resident_hmi_decision.md`, `docs/resident_hmi_contract.md` and
  prototype README; update roadmap, architecture language and resource ledger.
  Include confidence, artifact provenance, alternatives and exactly one next
  read-only interface target. Do not broaden to projection/license archaeology.
- [x] Run Node/Python tests, syntax checks, size report, browser checks and
  `git diff --check`. Inspect named staged files for vendor content.
- [x] Commit/push only this branch; open a draft PR against main explicitly
  depending on #12. Verify clean tree, unchanged main and unmerged PR.

## Acceptance examples

`request('climate.driverC', 23, now)` returns a pending abstract intent; the
displayed temperature stays unchanged until a matching newer snapshot arrives.
`receive(camera=true)` cancels the intent and removes all custom vehicle action
controls. `tick(now+2001)` without a fresh snapshot disables actions. A late
response must not regain foreground or revive a cancelled command.

Resource checks distinguish PC source byte counts from a target package. The
45/15/4/8/5 MB reserve envelope remains unchanged. No claim of target deployment,
RAM, startup time or GPU performance may be inferred from PC rendering.

## Verification record

91 Python tests (including five new size tests) and 15 Node tests pass.
Independent code review found and verified fixes for overdue dispatch and late
heartbeat freshness; regression tests cover both. Browser checks confirm six
640x480 routes, no content overflow with the demo data, >=48px-high controls,
pending/observed values, rejection, timeout, stale/disconnect and camera/explicit
resume flows. No app console errors. Temporary tab/server closed after checks.
The optional Playwright CLI encountered a Windows libuv assertion while exiting
its help command; browser verification used the available browser tool instead.
No target executable was built or run, no deployment performed.

Delivery: implementation commit `69fac37` pushed on
`astra/resident-hmi-feasibility`; draft PR
[13](https://github.com/jfhutchi/jeep_uconnect_custom/pull/13) targets main and
explicitly depends on unmerged PR #12. Neither PR merged. Main remains
`6c898a1e09a861ba0973ce0ae6d7cb29d94e0623`. No pending implementation tasks;
target deployment/integration gates are documented future work, not omissions
from the PC-scaffold deliverable.
