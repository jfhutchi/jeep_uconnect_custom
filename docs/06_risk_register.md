# 06 - Risk Register

| Risk | Impact | Current status | Mitigation |
|---|---|---|---|
| FCA/Harman firmware signing | High | VERIFIED | Do not base architecture on modified USB firmware. Prefer runtime/external integration. |
| Projection backend absent from RA4 | High | STRONG EVIDENCE | Reconstruct HMI contract; implement compatibility layer only if contract is supportable. |
| RA4 CPU/GPU performance insufficient | High | UNKNOWN | Run modern HMI/projection on hidden external compute, not on OMAP3730 if necessary. |
| Factory display ownership/arbitration | High | UNKNOWN | Bench-test QNX Screen surface behavior and camera preemption. |
| Touch event routing | High | PARTIALLY VERIFIED | QNX Screen/mtouch path exists; determine safe session-specific routing. |
| Projection audio integration | High | STRONG EVIDENCE | Investigate `audioApp`, MME and AudioCtrlSvc contracts. |
| CarPlay licensing/authentication | High | EXPECTED | Use a legitimate projection implementation/module; do not attempt to bypass Apple authentication requirements. |
| Android Auto protocol compatibility | High | EXPECTED | Use an established implementation/module and focus custom work on RA4 integration. |
| Backup-camera regression | Critical | UNKNOWN until bench test | Camera must have hard priority and stock fallback. Do not intercept the safety-relevant camera path unless necessary. |
| HVAC/comfort control regression | Medium/High | STRONG EVIDENCE stock services exist | Keep stock RA4 service authority and reflect actual state after commands. |
| Vehicle configuration differences | Medium | EXPECTED | Capability-detect features; never assume every WK2 has identical options. |
| Boot timing / bridge unavailable | Medium | EXPECTED | Custom layer must be optional; stock RA4 must boot independently. |
| Custom process crash | Medium | EXPECTED | Watchdog and immediate stock-HMI fallback. |
| Spare bench radio differences | Medium | EXPECTED | Prefer a matching or close RA4 part family and document hardware/software versions. |
| Copyright/trade dress | Low/Medium | EXPECTED | Build a Uconnect-inspired layout rather than copying proprietary artwork pixel-for-pixel. |

## Safety boundary

The project will not intentionally implement direct control of powertrain, braking, steering, restraint or other safety-critical vehicle systems.

Comfort/infotainment integrations should use the same high-level RA4 services used by the factory UI where possible.
