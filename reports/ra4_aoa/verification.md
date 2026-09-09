# RA4 AOA Verification

- Working branch: `codex/ra4-aoa-transport`.
- Baseline suite: 311 tests passed before implementation.
- New tests: 327 analysis tests, 19 AOA host-model tests, 18 Hello Uconnect tests, 17 network-probe tests, 20 resident-HMI Node tests, and the strict C99 projection-arbiter assertions passed.
- Generated-report checks: renderer ran twice and --check passed twice with no second-run drift.
- JSON parse: all three generated JSON documents parsed successfully.
- Diff check: git diff --check passed with no whitespace errors.
- Recovered artifact hashes: all 24 raw recovered artifacts matched their recorded byte sizes and SHA-256 values after implementation.
- Original dirty checkout: branch codex/ra4-driver-temperature at 894afe8e5361c3595623de599e62ba0f0c0d9f78 retained the exact status list, unstaged hash 33a13317707d962e24e9f25f12728dd8b3198466, empty staged hash e69de29bb2d1d6434b8b29ae775ad8c2e48c5391, and untracked no-filter hash 5cd7495dd780e5a53d9928a2d4ef1f72df533c80.
- Physical test: not performed because Phase 7 is B.
- Firmware, signing, trust, AMS/DRM, vehicle configuration, and vehicle buses: not modified or bypassed.
- Android Auto projection protocol: not implemented.
