# Resident HMI decision: stock-runtime first, deployment not yet proved

Date: 2026-09-05. Scope: owner-authorized source, mocks and read-only analysis.
No installation, firmware changes, signing changes, CAN writes or projection
engine implementation. This decision supersedes the premature native-only
language and the later replacement-shell interpretation.

**PRODUCT CORRECTION:** production is one projection application inside stock
Uconnect. Stock Radio, Media, Climate, Controls, Phone, Messaging and Settings
remain. The former six-screen artifact has been replaced by a focused
projection-ownership bench.

## Decision

**DESIGN:** First evaluate a small, independently authored projection screen and
foreground-integration module using the installed AIR environment and stock
high-level bindings. It participates in the stock application arbiter, navigation
stack, popup manager and camera layers; it does not replace factory screens.
Add a native bridge only for a proved service gap. Keep native QNX rendering as
an alternative. Do not replace the main SWF, change startup files or assume a
second AIR process. A supported loading/lifecycle boundary remains UNKNOWN.

This is the smallest credible *direction*, not a deployable architecture proven
on hardware. Sharing a stock process may minimize new bytes but increases
failure coupling. If independent loading, bounded resource use and stock
preemption cannot be established, reject that route even if it fits storage.

The PC scaffold uses an implementation-neutral snapshot/intent contract and a
small JavaScript reference state machine. Its HTML/CSS renderer, Node tests and
browser are **PC-only**. The data contract and behavior tests can be implemented
in ActionScript or C/C++; no automatic JavaScript-to-SWF/native conversion is
claimed. No browser, Node, Python, SDK or test runner belongs in an RA4 package.

## Direct local evidence

Canonical prefix `P` = ignored
`analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/`.
Prefix `H` = ignored `analysis_ra4_18.45.01/work/hidden_hbc_ifs/`.
Line numbers refer to original local plaintext; none was executed or changed.

| Evidence | Confidence and implication |
| --- | --- |
| `H/standard_boot/files/bin/boot.sh:95-102` chooses `hmi_ru` / `hmi_rov` and links HMI state/temp locations | CONFIRMED stock variant/path selection; not an extension installation API. |
| Same boot script, line 404, launches `processStarter ADL`, `/bin/adl`, runtime `/lib/air/runtimeSDK`, descriptor `/fs/mmc0/app/share/hmi/main.xml` | CONFIRMED stock HMI startup. `adl` exists in recovered HBC at 19,332 bytes; this launcher size is NOT the full runtime size. |
| `P/share/hmi_rov/main.xml`: AIR namespace 2.5, `main.swf`, `mobileDevice`, requested `renderMode=gpu` | CONFIRMED descriptor and GPU request; actual acceleration/runtime version compatibility UNKNOWN. |
| `H/segment_001a0000/files/usr/lib/lua/qnxair.conf`: width 640, height 480, commented `enable_gles`; log and trace settings | CONFIRMED configuration. Comments are not proof of active GPU enablement. A second config at `segment_00f20000/files/etc/system/config/qnxair.conf` has matching visible settings. Which config wins at runtime remains UNKNOWN. |
| `H/segment_001a0000/files/usr/lib/graphics/omap3730/graphics.conf`: 640x480@60, SGX530 driver names, `video_hmi` class, CMC mtouch driver and scaling path | CONFIRMED configured display/touch infrastructure; active layer ownership and touch delivery to a new app UNKNOWN. Display refresh does not establish app frame rate. |
| `P/share/hmi_rov/ModuleLink.xml`: span/hb localhost port 4400 | CONFIRMED configured endpoint, not an authorized standalone-client contract. No connections attempted. |
| `P/share/audioDSP/audioMgrCMC.conf:24-29`: stock sources, including `audioApp`, map to MME | CONFIRMED logical source mapping, not a new source registration/ownership API. |
| Existing [app launch report](../reports/app_launch_ui_path.md): `AppsMainScreen.onItem` FWS `0xC1E6` calls `startXlet`; ModuleLink sends `startApp`; native DRM gate remains | CONFIRMED ordinary installed-Xlet route. It is not proof that arbitrary SWFs, native apps or this prototype can be installed/launched. |
| Existing [interface inventory](interface_inventory.md): `IHvac`, comfort capability names, Screen event APIs and factory camera resources | CONFIRMED names/references at report level; full subscription semantics, values and write authorization remain UNKNOWN. |

Provenance hashes (SHA-256; derived metadata only):

| Local artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `qnxair.conf` under `usr/lib/lua` | 1,682 | `c2011595785381da3d6d36ec9342bd0634104d85818acb9230e1f2b9c6116daa` |
| `graphics.conf` above | 2,389 | `984bfe3e698cf33f565c7698d98ea6aff2a59d568799e8a8d5a0ba0986204e93` |
| ROV `main.xml` | 5,069 | `d020a5b5049e87907b3deddff8c17cbf56fac24fa5dd235d4392a39e9ba23806` |
| ROV `ModuleLink.xml` | 115 | `46cacc8e084ba4b3024cdf68191da1b7165754cc2bedbc2bf44949a9ab59e533` |

## Decision matrix

All numeric ranges below are engineering targets, not artifact measurements.
Runtime measurements for every RA4 candidate are UNKNOWN. Incremental dependency
bytes are zero only if existing files and compatible APIs can genuinely be reused.

| Criterion | A: stock AIR/SWF | B: small native QNX | C: stock UI + minimal native bridge | D: stock Java/Xlet or Lua |
| --- | --- | --- | --- | --- |
| Incremental installed target | 0.5-2 MB code + <=0.5 MB original assets/defaults; <=3 MB trial total | 0.5-3 MB code + <=0.5 MB assets; total depends on libraries, <=5 MB trial target | A plus <=1 MB bridge target; <=4 MB trial total | UNKNOWN; stock VM/Lua exist but no sized shell |
| New dependencies | None intended; binding/runtime access unproved | None intended beyond stock libc/Screen/font services; ABI unproved | Same as A plus bridge IPC/ABI | Stock facilities present; actual required binding set UNKNOWN |
| RAM | Incremental heap/GC UNKNOWN; shared-process corruption risk; second AIR process not approved | Heap plus graphics buffers UNKNOWN; easier to attribute per-process | Combined heap/IPC/process cost UNKNOWN | VM/heap and rendering cost UNKNOWN |
| CPU / GPU | Existing path renders stock UI; custom cost and GPU use unmeasured | Small redraw regions plausible; font rasterization/composition cost unmeasured | Same UI cost plus IPC | No sufficiently established rendering path for this shell |
| Startup | Existing ADL launch confirmed; module load time UNKNOWN | Separate process possible in principle; supported registration UNKNOWN | Two lifecycle boundaries to prove | Ordinary installed Xlet launch confirmed; arbitrary new package acceptance not proved |
| 640x480 | Direct stock configuration | Screen configuration supports it | Reuses A | Must establish view integration |
| Touch | Stock HMI already consumes input; new screen ownership UNKNOWN | mtouch/Screen present; focus/routing UNKNOWN | Reuses A; bridge must not inject input | App foreground and touch contracts incomplete |
| Harman / PPS / MME | Existing ModuleLink abstraction is strongest nearby seam | Requires protocol/SDK/access work; avoid guessed PPS writes | Bridge only for a demonstrated gap | Permissioned Java facade exists; Lua stock service code exists |
| Fonts/icons/assets | Stock assets potentially reusable in-place; loader/licensing compatibility UNKNOWN | In-place font APIs and resource formats UNKNOWN | Reuses A | UNKNOWN |
| Maintainability | Legacy runtime/toolchain, strong vendor coupling; keep independent source | Small explicit code, but new bindings and rendering work | More IPC/versioning/failure cases; avoid until needed | More lifecycle/security work before useful UI proof |
| PC prototype | Modern AIR may prototype visuals but not prove old QNX compatibility; neutral model works now | Host renderer can share model/contract, not QNX window ABI | Mock bridge can share contract | Host VM does not establish Kona/platform compatibility |
| Update/deployment | Authorized loading/package path UNKNOWN; do not overwrite stock HMI | Authorized process/package path UNKNOWN | Must authorize/update both parts | Signed package/permission gates documented and unresolved |
| Stock fallback | Shared process makes independent fallback harder; must prove stock controller still owns priority | Separate window/process may isolate crashes; arbitration UNKNOWN | UI and bridge failure must independently yield | Existing lifecycle useful but camera guarantees UNKNOWN |
| Toolchain/licensing | Compatible compiler/API stubs and permitted reuse UNKNOWN; no `mxmlc` or host `adl` on PATH in this check | Compatible licensed QNX SDK/headers UNKNOWN; no `qcc` on PATH | Both sets of gates | Legitimate app signer, tooling and APIs unresolved |
| Disposition | **Preferred first feasibility target** | **Retain as alternative** | **Conditional, not initial requirement** | **Defer; no evidence it is a smaller UI route** |

Current [AIR Linux documentation](https://airsdk.dev/docs/basics/install/linux)
describes x86_64/ARM64 and commercial licensing; it does not establish compatibility
with this legacy QNX ARM32 build. Do not download a modern runtime for the radio.
[QNX Screen documentation](https://qnx.com/developers/docs/7.0.0/com.qnx.doc.screen/topic/manual/cscreen_getting_started.html)
illustrates event/render-buffer APIs, but that newer documentation is not proof
of RA4 ABI or permission compatibility. Both checked 2026-09-05; local evidence
governs this decision.

## MVP and performance gates

The PC bench evaluates projection ownership, state freshness and adapter failure
behavior without reproducing factory screens. The target trial is one
stock-integrated projection screen plus foreground/return arbitration. No media decoder, map data, call
handling or projection engine is bundled in that trial. All vehicle changes are abstract
mock intents; a real adapter starts read-only with all write capabilities off.

Use [the contract](resident_hmi_contract.md) and [PC scaffold](../prototype/resident_hmi/README.md).
Stock owns camera, HVAC behavior, audio routing and vehicle settings. The mock
fallback panel is not a recovered fallback API or a safety guarantee.

Proposed **measurement gates**, not specifications proved on RA4:

- First useful screen <=1 s after supported app activation; no boot dependency.
- Touch-to-feedback <=100 ms; no continuous animation; redraw only changed regions.
- Target <=16 MB incremental RAM for an A trial and <=24 MB for B/C, including
  attributable shared allocations; reject if stock headroom or camera suffers.
- Target <5% of one CPU core when idle, <20% over a 10-second interaction sample;
  actual available CPU/RAM and acceptable tail latency remain UNKNOWN.
- One 640x480 RGBA buffer is 1,228,800 bytes; two are 2,457,600 bytes (~2.34 MiB),
  arithmetic only. Pitch, extra compositing surfaces, textures, runtime heap and
  allocator overhead are additional. RGB565 is not assumed usable.
- Compare stock baseline and candidate boot/navigation/phone/camera behavior
  before selecting thresholds for a bench release. Do not claim PC timing is
  radio timing. No runtime experiment is authorized by this document.

## Resource estimate for preferred A trial

| Component | Estimate / target | Measured target bytes |
| --- | ---: | --- |
| Independently authored screen and state code | 0.5-2 MB | UNKNOWN |
| Original assets + packaged defaults | <=0.5 MB, no bundled fonts/images in PC scaffold | UNKNOWN |
| Private dependencies | Intended 0; any required bridge/library must be sized | UNKNOWN |
| Installed trial total, including uncertainty | <=3 MB target, still subject to 15 MB hard cap | UNKNOWN |
| Persistent config/state | <=0.25 MB, no vehicle source-of-truth duplication | UNKNOWN |
| Logs including rotations | <=0.25 MB | UNKNOWN |
| Cache/normal temp | <=0.5 MB | UNKNOWN |
| Normal writable total | <=1 MB target within 4 MB cap | UNKNOWN |
| Additional staging/rollback peak | <=6 MB planning target within 8 MB cap | UNKNOWN; update design not selected |

Estimated preferred-trial peak is <=10 MB, leaving about 67 MB from the owner's
77 MB observation: 45 MB protected plus 22 MB additional headroom. This is not
proof of package/install feasibility. Stock runtime logs/cache attributable to
the trial count too; trace-heavy AIR settings are not free. Actual filesystem
allocation, update failure artifacts and stock variation must be measured.

No small stock-facing integration capability is proved to require external
compute. Bundled maps/media/speech models remain excluded. The complete legitimate
projection engine is locally UNKNOWN; classify it `EXTERNAL_COMPUTE_REQUIRED`
only if measured storage/CPU/RAM or platform requirements make resident execution
unsafe. No replacement shell is a product dependency.

## Next single evidence task

Complete consumer XREFs for `PROJECTION_BACKTO_CAR`, `DEVICE_PROJECTION`,
heated comfort popups and phone/SMS ownership, then trace projection/HFP audio
focus. Continue the independent read-only temperature-quality trace across units
changes and service restart. No runtime call, radio write or vehicle command is
authorized.
