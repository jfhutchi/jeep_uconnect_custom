# Wired Projection Verification

- Authoritative base: `5b9826b2b6537f12b4bf08a50003ea6914263700` on `codex/kim19-final-capability-closure`.
- Baseline suite: 305 Python tests passed with no failures or skips after resolving three host-only dependencies.
- Final suite: 311 Python tests passed with no failures or skips.
- Required generated-report check runs: 2.
- Compile check: `python -m compileall -q analysis_tools` exited 0.
- Diff check: `git diff --check` exited 0.
- Known verification limit: the optional C arbiter smoke test was unavailable because no C compiler is installed on the analysis host.
- Original checkout: pre-work status, binary diff, cached diff and untracked-file SHA-256 fingerprints must remain unchanged.
- Projection client implementation, firmware writes, radio installation, and vehicle modification: not performed.
- The final commit SHA is reported by Git after commit; generated files intentionally avoid a self-referential hash.
