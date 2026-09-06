# 07 - Product-first next steps

Updated 2026-09-06. Production is projection inside stock Uconnect, not a
replacement shell. The refocused PC prototype exercises only projection
ownership, adapter boundaries and failure policy.

## Next highest-value static task

The [post-reboot checkpoint](../reports/ra4_post_reboot_checkpoint.md) executed
135 Python tests, 20 JS tests, the strict C99 build/run, the seven-root 122-marker
census and bounded foreground XREFs. Do not repeat those acquisitions without
new evidence or code changes.

1. Follow the completed [USB PHY/power trace](../reports/ra4_usb_phy_power_control.md):
   Mentor requests PHY reset; `usbPowerSwitch` changes ULPI VBUS-drive bits
   under stock onoff lifecycle control. Inspect recovered startup/I2C/PMIC
   configuration for explicit PHY identity and power-switch linkage to
   `0x480ab000`; no target execution or role change. Utility success is not
   electrical proof because its exhausted-poll path can return zero.
2. Obtain a matching owner-supplied `DeviceProjection.swf`/backend or legitimate
   provider contract. The seven-root filename census and 610-SWF exact-name
   census did not locate the screen or a back-to-car event listener.
3. Determine the backend meaning of stock BacktoCar-triggered
   `callStartProjection(activePpId)`. Preserve session continuity; do not infer
   teardown or prohibit this command solely from its name.
4. Finish heated-seat/heated-wheel popup event control flow and the separate
   MME source registration, ducking/call route and microphone owner-death trace.
5. Acquire authorized hub/controller/net evidence for Radio C2. The installed
   host paths are known; the physical phone-port and reversible DCD lane are not.

Current evidence: [projection foreground ownership](../reports/projection_foreground_ownership.md).
The [completion matrix](08_projection_completion_matrix.md) separates static,
host-model and target proof so these tasks cannot be closed by a narrow test.
The [resident placement decision](16_ra4_resident_placement_decision.md) separates
proved authorized-Xlet launch from the still-external package authorization and
projection backend/screen gates. The [evidence-gate manifest](10_evidence_gates.md)
names the exact local artifacts,
historical log fields, legitimate contracts and spare-bench measurements needed.

Continue the [driver-temperature trace](../reports/ra4_driver_temperature_contract.md)
independently: close units-change/service-restart quality and stale-cache behavior
without adding a live radio subscription or replacement Climate screen.

## Static-contract exit

Recover session versus foreground lifecycle, return/resume behavior, call/SMS
visual and audio gates, camera stack return, permitted overlays and temperature
quality with explicit CONFIRMED/HIGH/INFERRED/UNKNOWN evidence.

## Authorized lifecycle/resource proof

Establish a supported screen/app boundary and compatible toolchain. Build only a
tiny integration trial. Measure installed bytes, runtime writes, update peak, RAM,
CPU and startup. Preserve the 45 MB stock reserve. No roadmap step authorizes radio
modification.

## Bench-only proofs

Under separate authorization on spare hardware: show/hide projection through the
stock arbiter; verify camera/popup priority; verify Return to Uconnect and session
resume; verify no duplicate call/SMS foreground or TTS while active and normal
behavior while inactive; verify crash fallback.

## Engine feasibility

The [official-source candidate screen](11_projection_engine_feasibility.md)
identifies QNX SDK for Smartphone Connectivity as the first legitimate resident
candidate family. Obtain exact RA4/QNX/ARM compatibility, Apple/Google program
access and component-level target sizes before requesting binaries or assuming
integration.

Evaluate that legitimate engine against local storage, RAM, CPU, video, touch, USB
and audio contracts. Do not choose external hardware merely for convenience. Mark
the engine `EXTERNAL_COMPUTE_REQUIRED` only if resident feasibility fails while
keeping the RA4 integration layer tiny.

## Definition of done

Projection behaves like an OEM Uconnect application: full-screen when selected,
easy to leave/resume, subordinate to camera/critical overlays, compatible with
temporary comfort popups, and sole presenter of projected calls/messages while
active. Ordinary factory screens and disconnected behavior remain stock.
