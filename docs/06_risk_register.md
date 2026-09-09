# 06 - Risk Register

> **Project status - 2026-09-07: BLOCKED without manufacturer support.**
> The software-only integration is effectively not achievable with the hardware
> and authorized access available to this project. Manufacturer-provided or
> approved development/service hardware, credentials, signing/entitlements and
> compatible licensed software are prerequisites; no sufficient route is confirmed.
> This document is retained as research or a conditional design, not an active
> deployment roadmap. The [current project status](00_project_status.md)
> supersedes earlier implementation priorities and defines reopening conditions.

| Risk | Impact | Current status | Mitigation |
| --- | --- | --- | --- |
| FCA/Harman firmware signing | High | VERIFIED | Do not base architecture on modified USB firmware; use an authorized runtime/app boundary. |
| Projection backend absent/incomplete | High | STRONG EVIDENCE | Reconstruct the HMI contract and evaluate a legitimate compatible engine. |
| RA4 CPU/GPU/RAM insufficient for complete engine | High | UNKNOWN | Measure a local engine first; mark only the engine `EXTERNAL_COMPUTE_REQUIRED` if local feasibility fails. Keep the stock-facing layer resident and tiny. |
| 77 MB free-space exhaustion | Critical | Observed free approximately 77 MB; behavior unmeasured | Enforce 15/4/8 MB caps, protect 45 MB stock reserve, measure allocated bytes and peaks, never fill the filesystem. |
| Duplicate stock and projection call UI | High | Presentation seams CONFIRMED; policy UNKNOWN | Gate only native call goto/popup during an active projection-owned session; preserve HFP/service state and emergency/eCall. |
| Duplicate SMS popup or TTS | High | Presentation/TTS paths CONFIRMED; policy UNKNOWN | Gate native SMS popup and announcement together while projection owns presentation; preserve MAP ingestion. |
| Projection/HFP audio-focus conflict | High | UNKNOWN | Trace focus, microphone and speaker ownership before runtime design; do not disable whole subsystems. |
| Factory display ownership | High | Foreground arbiter CONFIRMED; projection surface UNKNOWN | Reuse stock application requests/pending retry and prove projection surface behavior on an authorized bench. |
| Touch routing | High | PARTIALLY VERIFIED | QNX Screen/mtouch exists; recover and bench-test session-specific routing. |
| CarPlay licensing/authentication | High | EXPECTED | Use a legitimate implementation/module; do not bypass Apple authentication. |
| Android Auto compatibility | High | EXPECTED | Use a legitimate established implementation and keep custom work at the RA4 integration boundary. |
| Backup-camera regression | Critical | Static preemption/stack return CONFIRMED; runtime latency UNKNOWN | Reuse stock DisplayManager/LayerManager path; never intercept it unnecessarily; bench-measure latency/return. |
| Comfort-overlay regression | Medium | Stock HVAC popup layering CONFIRMED; seat/wheel trigger UNKNOWN | Reuse permitted stock popup classes and trace heated-seat/wheel events. |
| Vehicle configuration differences | Medium | EXPECTED | Capability-detect; never assume identical WK2 equipment/camera variants. |
| Boot or integration process failure | High | EXPECTED | Stock boots independently; projection is optional; prove crash/release return. |
| Copyright/trade dress | Low/Medium | EXPECTED | Use stock licensed UI where present and original integration UI; do not clone later artwork. |

## Safety boundary

No direct control of powertrain, braking, steering, restraint or other
safety-critical systems. Vehicle and comfort integration uses stock high-level
services where proved. This register authorizes no radio write or bench action.
