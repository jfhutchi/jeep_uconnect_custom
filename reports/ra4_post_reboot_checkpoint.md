# RA4 post-reboot verification and static checkpoint

Date: 2026-09-06. Baseline: `9eb28ad2c9d06753c1b0ec59a251c804b70b4b52`.
Subsequent work: [Mentor PHY reset and stock VBUS-drive control](ra4_usb_phy_power_control.md)
completes this checkpoint's final board-init/ULPI target and records the narrower
remaining PHY/physical-route/device-stack gates. Results below retain their
original checkpoint scope.
Verified tool/test revision: `d0f3c269599aa96c62de5c782c924f17e82ef1bb`.
This checkpoint supersedes the earlier frozen-runner status and the inference
that an active-session return can never issue a start-named command. It contains
original analysis and metadata only. No radio, target service or vendor program
was executed; no firmware, vehicle state or authorization material was modified.

## Recovery

- Starting checkout: `main`, `6c898a1e09a861ba0973ce0ae6d7cb29d94e0623`.
- No staged or tracked-file changes. Two untracked files existed:
  `reports/_tool_probe.txt` and `reports/projection_foreground_ownership.md`.
- Both were inspected, copied and moved outside the repository to
  `C:/Users/JHutc/.codex/ra4-recovery-20260906/`. Their `.original` copies remain
  there. The foreground draft predates the remote's revised report; it was
  preserved rather than overwriting the published version. The other file says
  `probe`. No unique pre-crash code change was found.
- Original SHA-256 values: foreground draft
  `dd7ae2e28b157838a622de08333bb3f063516c238aa14797428c33955e3f0cb4`;
  probe `25be323556dad377abb57fe7ec8c4b99a6527f488dda28d0c9b686528659c909`.
- Fetch advanced the remote tracking head from `84553b5` to `9eb28ad2`.
  The local active-line branch was `52a37f1`, with 0 local-only and 47
  remote-only commits. It was switched to and fast-forwarded with
  `git merge --ff-only origin/codex/ra4-driver-temperature`.
- `main` was not modified. No reset, clean, history rewrite or force push.

## Executed verification

All commands below run from the repository root unless stated otherwise.
Local logs and generated results are under ignored
`analysis_work/post_reboot_20260906/` (abbreviated `$out` below).
Python is 3.14.4; Node is 24.15.0; Ubuntu/WSL GCC is 13.3.0.

Initial `python -m unittest discover -s analysis_tools/tests -v` failed:
114 loader/test entries, two assertion failures and one import error.
The probe fixture contains both `ModuleLink` and `ModuleLink.xml`, so the
correct substring count is two; offsets are now asserted too. The malformed
root-label fixture lacked the required marker inventory and failed at the
earlier schema gate. Its valid inventory was restored. The missing dependency
was `cryptography`; dependencies were installed in an ignored isolated venv,
not the system Python.

```powershell
$out = 'analysis_work/post_reboot_20260906'
python -m venv "$out/venv"
& "$out/venv/Scripts/python.exe" -m pip install cryptography capstone
& "$out/venv/Scripts/python.exe" -m unittest discover -s analysis_tools/tests -v
python -m compileall -q analysis_tools
node --test prototype/resident_hmi/tests/*.test.mjs
Get-ChildItem prototype/resident_hmi -Filter *.mjs -Recurse | ForEach-Object { node --check $_.FullName }
python -m analysis_tools.hmi_size_report prototype/resident_hmi
& "$out/venv/Scripts/python.exe" -m analysis_tools.synctool_evidence analysis_work/Synctool.elf --verbose
git diff --check
```

Installed dependency versions: cryptography 50.0.1, capstone 5.0.9, cffi 2.1.1,
pycparser 3.0. Final results (all exit 0):

| Check | Executed result | Local evidence |
| --- | --- | --- |
| Full Python discovery | 135 tests, OK, no skips | python-tests-final.log |
| Python compileall | exit 0 | command output |
| JavaScript ownership/model/view | 20 passed, 0 failed/skipped | node-tests-final.log |
| JavaScript syntax | all 8 mjs files checked | command output |
| Synctool hash-gated static assertions | SHA matched, 83/83 anchors passed | synctool-evidence.log |
| Host HMI size | 11 files, 33,215 logical bytes, 53,248 estimated allocated bytes | hmi-size.json |
| Strict C99 compile and executable | all assertions passed | c99-tests-final.log |
| Patch whitespace | exit 0 | git diff --check |

Exact C99 command, using the already installed Ubuntu toolchain:

```powershell
wsl -d Ubuntu -- sh -lc 'cd /mnt/e/Documents/GitHub/jeep_uconnect_custom && cc -std=c99 -Wall -Wextra -Werror -pedantic prototype/projection_arbiter_c/projection_arbiter.c prototype/projection_arbiter_c/test_projection_arbiter.c -o analysis_work/post_reboot_20260906/projection_arbiter_test && analysis_work/post_reboot_20260906/projection_arbiter_test'
```

This verifies host conformance and the <=128-byte state compile guard. It is
not a QNX target build, package-size measurement or radio execution result.

The real HMI XREF exposed two decoder gaps: `newcatch` at FWS `0x0022BA3A`
and a sign-extended negative `pushshort` at `0x0027266D`. Added synthetic tests
first reproduced both; the decoder now handles those operand forms. A separate
regression reproduced early exit at the XREF cap, which could skip unsupported
instructions in the same or later methods. Capped searches now validate every
body and only mark truncation when an additional match exists. Other u30 bounds
remain strict. See `swf-regression-before.log`, `pushshort-before.log` and
`swf-tests-after.log`; final SWF suite is 12 tests.

Operand basis: [Adobe opcode table](https://github.com/adobe/avmplus/blob/master/core/opcodes.tbl)
and [AVM2 interpreter](https://github.com/adobe/avmplus/blob/master/core/Interpreter.cpp),
whose pushshort implementation truncates to signed 16 bits. This inspector is
still not a VM/stack verifier or a general untrusted-input sandbox.

## 122-marker census

Executed once over the existing materialized roots, then correlated; both
commands exited 0. No source archive was unpacked. The inventory includes
embedded containers already present in those roots; totals are file bytes read,
not deduplicated unique firmware bytes or an installed-radio footprint.

```powershell
python -m analysis_tools.qnx_media_runtime_probe analysis_ra4_18.45.01/work/installer_iso analysis_ra4_18.45.01/work/primary_iso analysis_ra4_18.45.01/work/secondary_iso analysis_ra4_18.45.01/work/hidden_hbc_ifs/standard_boot/files analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_019a0000/files --pretty > analysis_work/post_reboot_20260906/runtime-probe.json
python -m analysis_tools.qnx_runtime_correlation analysis_work/post_reboot_20260906/runtime-probe.json --pretty > analysis_work/post_reboot_20260906/runtime-correlation.json
```

| Root label | Materialized root under work/ | Files | Bytes |
| --- | --- | ---: | ---: |
| installer_iso | installer_iso | 54 | 34,333,260 |
| primary_iso | primary_iso | 2,466 | 371,334,962 |
| secondary_iso | secondary_iso | 766 | 1,012,221,304 |
| files#1 | hidden_hbc_ifs/standard_boot/files | 46 | 2,949,863 |
| files#2 | hidden_hbc_ifs/segment_001a0000/files | 433 | 30,769,956 |
| files#3 | hidden_hbc_ifs/segment_00f20000/files | 219 | 22,931,139 |
| files#4 | hidden_hbc_ifs/segment_019a0000/files | 126 | 35,306,386 |
| Total | 7 roots, 122 markers | 4,110 | 1,509,846,870 |

Zero oversize skips; 628 candidate files, 108 tier 1, 48 cross-family.
Local output SHA-256: probe
`cf5d505391ce4ac565a9b8ec147c19de9b49f4fff5c69f216b1457b417000090`;
correlation `3a88fe4c1070b0ad7d64e9568ed5cbfcb20d468017352ab2bcc7a345dd745fb4`.
Tier-1 inspection began with `boot.sh` and `.script`; the hash-known HMI was
then inspected separately. The two known host-controller DLLs were traced from
`.script` rather than treating their lower raw-census tier as a reason to omit them.

**STATIC_PROVED (bounded raw census):** no hits for `usblauncher`, `io-usb-dcd`,
`devu-dcd`, `devu-usbumass-`, `libusbdci`, `ulink_ctrl` or either role-swap marker.
These are exact-byte/filename negatives, not global driver absence. Neither a
generic `sessionActive` nor a `servicebroker` hit proves projection identity.

**Critical limitation:** the raw scanner does not decompress CWS/SWF or JARs.
It found zero `PROJECTION_BACKTO_CAR`, `phoneProjectionService` and
`checkForegroundAvailability` hits despite known compressed HMI definitions.
Do not use that result to reject the stock projection seam. No notification-family
raw hits likewise proves no more than a bounded marker negative.

## A: installed USB startup now linked to controllers

Artifact paths here are relative to `hidden_hbc_ifs/standard_boot/files`.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| proc/boot/.script | 16,856 | fb0e5b3df3295951740818b081fc11f2b69a4bcc50386237b4aea7629cf17086 |
| bin/boot.sh | 29,268 | c801d473b0b49e8242114635f4022cc67ccbe03093fec188de3b7188dd636ecf |
| bin/io-usb | 128,629 | 3ac3777b8986c6aebd3c0d226715ee8fa935895c2ee5775bc874ceef569cd3f4 |
| lib/dll/devu-omap3530-mg.so | 45,936 | 6916bd0f398f28bf111ace6c3a08e425a90127f283e0105e2bb6f0b58df881a1 |
| lib/dll/devu-ehci-omap3.so | 40,215 | 4e267106c1f209e9b32c596d2d04f39d3ee2d3337d0d5601f74f58a33114c03e |

**STATIC_PROVED:** `.script` has the `io-usb` executable/argv at file offsets
`0x132C/0x1333`, `-c` at `0x133A`, and two driver clauses: `omap3530-mg` at
`0x1340` with `ioport=0x480ab000,irq=92,ctrl_noping` at `0x134C`; `ehci-omap3`
at `0x1374` with `ioport=0x48064800,irq=77` at `0x137F`. This is recovered boot
configuration, not an observed live launch or a command to run on the radio.
At `0x13AA` the environment declares `QNX_VERSION=qnx650`; the Mentor driver
also carries a `TC650`/`hardware/devu/hc/mg` build-path string at `0x9574`.
The QNX 6.6 documents remain reference material, not an identified installed ABI.

**HIGH:** these are the installed host-stack controller paths. The Mentor driver
has root-port, transfer and ULPI symbols (including `mentor_ulpi_write` at string
offset `0x1925`); the EHCI DLL identifies itself as a host controller at `0x8A48`;
`io-usb` contains HCD initialization diagnostics. No runtime role behavior or
specific phone-port-to-controller connection follows from those names alone.

**STATIC_PROVED:** the boot GPIO config's line 4 names `USBFault`, input GPIO
164. SHA-256 `d37066a23ca22b571e57bc7ba510f213a8a23ee0228dc996a26ea9d66b551b9d`.
This is fault-input evidence, not proof of VBUS output/ID control. `boot.sh`
also invokes `usb_hub_oc`; no role-switch effect is inferred.

**UNKNOWN:** cabin hub to BE2800 rear/main-board routing, which controller owns
Radio C2, exact PHY/PMIC and VBUS/ID control, installed hardware-specific DCD,
function descriptors and reversible device-stack transition. The absence of
public BSP device support or of these raw markers is not global impossibility.

## B: BacktoCar/start ordering and missing screen boundary

Both SWFs are under `primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov`:

- `MainSupplement.swf`: SHA-256
  `e9d796ea4b4c83ed518bfe3b3c341e54e510a1ae0f78ebbffbd655b7c36a3258`;
  ABC 0, FWS base `0x264EB`, 15,157 method signatures.
- `main.swf`: SHA-256
  `224ee3e4da03d8102c3f154fc12061c88b8f88b2b6e61f5c6034d65153839172`;
  ABC 0, FWS base `0x22B`, 772 method signatures.

Executed queries (all exit 0 after parser fixes):

```powershell
$hmi = 'analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/share/hmi_rov'
python -m analysis_tools.swf_abc_inspect "$hmi/MainSupplement.swf" --xref 'PROJECTION_BACKTO_CAR|DEVICE_PROJECTION|mPrevScreenBeforeActiveCall|SMS_INCOMING_MESSAGE' --count 200
python -m analysis_tools.swf_abc_inspect "$hmi/main.swf" --xref 'DeviceProjection.swf|DEVICE_PROJECTION' --count 50
python -m analysis_tools.swf_abc_inspect "$hmi/MainSupplement.swf" --xref 'heated|seatHeat|steeringWheelHeat|DynamicPopupNames.*HVAC|backtoCar|backToCar' --count 160
```

The first query decoded all bodies in the only ABC block without truncation.
Full bodies of methods 1251, 7071 and 8248 were also decoded locally, with
selected output in `foreground-methods.txt`; no disassembly is committed.
Reproduce the important method ranges with `--method 1251 --count 300` and
`--method 7071 --start 0x2B4C81 --count 30` on MainSupplement.

**STATIC_PROVED:** method 7071 recognizes the projection-back-to-car signal,
sets `mBacktoCar=true` at `0x002B4C97`, and dispatches the event at
`0x002B4CA2-0x002B4CA9`. That branch itself does not navigate or stop a session.

**STATIC_PROVED:** `AppPhone.press` method 1251 reads `BacktoCar` at
`0x00262B59`; if true, it calls `callStartProjection(activePpId)` at
`0x00262B72`. This precedes the emergency and assist presentation branches and
the later `sessionActive` check at `0x00262BCD`, followed by
`goto(DEVICE_PROJECTION)` at `0x00262BE7` on its eligible active path.
The existing method 7086 sends the start command and clears `mBacktoCar`.

**INFERRED:** the start-named command may reacquire/resume projection after
BacktoCar. **UNKNOWN:** whether it restarts the session, changes only video
ownership, or performs another backend operation. The previous HIGH inference
that every active-session return must omit `startProjection` is withdrawn.
The host model still requires continuity; it does not implement a vendor command.
Factory camera/critical priority and fail-open phone/message policy are unchanged.

**STATIC_PROVED:** `main.swf` method 426 maps `DEVICE_PROJECTION` to
`DeviceProjection.swf` at `0x0002306E`; method 430 also references it at
`0x00024FF1`. No file with that name exists in the seven materialized roots.

A separate in-memory census parsed all 610 SWFs/610 ABC blocks in `hmi_rov`,
with zero parse errors. It selected pools containing exact case-folded names
`projection_backto_car`, `deviceprojection.swf`, `backtocar` or
`projectionbacktocar`, then fully decoded selected ABC bodies with
`find_references(..., r'PROJECTION_BACKTO_CAR|BacktoCar', 100)`.
Only main and MainSupplement matched; output was not truncated. The recorded
references show event definition/dispatch and the BacktoCar getter/phone-button
consumer, but no exact-name event listener. Output: `rov-return-census.json`.
Its SHA-256 is `f69398143ebf7eedc4917106ce5b56789b9885cb5fc771489c0d7b8a8a8e94d0`.
This does not exclude dynamically constructed names, other HMI variants,
unmaterialized embedded payloads, optional packages or another software build.
The missing listener's actual Return-to-Uconnect navigation remains UNKNOWN.

Heated comfort symbol candidates were found, but their full event-to-popup
control flow was not closed in this checkpoint. Native call/SMS/TTS and camera
claims retain their previously bounded scope.

## Resident authorization, resources, and next target

AMS/AppManager/Xlet remains the legitimate resident control-shell lane. A new
package still needs a legitimately issued signer/package identity and signed
descriptor/digests (`key.jar`), applicable DRM entitlement, and the accepted
developer identity/token/provider contract when that lane requires it. The
service-menu route separately requires a legitimately issued HU-bound service
certificate. The recovered files do not identify a provider that can issue all
of these; owner permission alone does not manufacture those artifacts.
No bypass or vendor credential reuse was attempted.

No radio bytes were installed or written. Preserve approximately 77 MB observed
free, >=45 MB stock reserve, 15 MB installed cap, 4 MB normal growth, 8 MB extra
staging, >=5 MB planned residual margin and <=3 MB no-engine trial target.
Host source/build size does not qualify a target package or engine. External
compute remains contingent on a measured local capability failure.

**Single next technical target:** statically trace the recovered
`devu-omap3530-mg.so` board-initialization and ULPI routines to concrete PHY/VBUS
operations, then correlate them with boot configuration and authorized BE2800
net evidence. This can narrow the OTG-to-physical-port gap with existing files;
the absent projection screen/provider remains an independent acquisition gate.
