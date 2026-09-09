# 01 - System Goal

> **Project status - 2026-09-07: BLOCKED without manufacturer support.**
> The software-only integration is effectively not achievable with the hardware
> and authorized access available to this project. Manufacturer-provided or
> approved development/service hardware, credentials, signing/entitlements and
> compatible licensed software are prerequisites; no sufficient route is confirmed.
> This document is retained as research or a conditional design, not an active
> deployment roadmap. The [current project status](00_project_status.md)
> supersedes earlier implementation priorities and defines reopening conditions.

## Goal

Integrate Apple CarPlay and Android Auto as first-class projection applications
inside stock 2014 WK2 RA4 Uconnect. Production does not replace factory Radio,
Media, Climate, Controls, Phone, Messaging or Settings. The current PC prototype
is a focused projection-ownership bench; the former six-screen scaffold is
historical only.

## Required experience

- Ordinary operation remains stock Uconnect.
- Active projection may use the full 640x480 display.
- Return to Uconnect leaves the projection session running.
- Returning to projection resumes that session without reconnecting.
- Stock comfort overlays may temporarily appear over projection.
- Factory camera and critical stock presentation always have priority and return
  to the appropriate previous screen afterward.
- Active projection owns projected calls/messages; stock Phone/Messaging must not
  independently take foreground or announce the same message.
- Inactive/disconnected projection restores normal stock phone/message behavior.
- Do not globally disable Bluetooth, HFP, MAP or the phone subsystem to achieve
  presentation ownership.

## Design principle

Reuse stock application arbitration, navigation stack, popup manager, camera
layers, display/touch/audio facilities and high-level vehicle services. Add the
smallest resident integration component possible.

## Constraints

Design for 640x480 and [the protected resource budget](ra4_resource_budget.md):
15 MB installed, 4 MB runtime growth, 8 MB additional update peak, 45 MB stock
reserve and 5 MB planned-peak margin. If a complete projection engine cannot meet
local storage/CPU/RAM constraints, it is `EXTERNAL_COMPUTE_REQUIRED`; the
stock-facing integration remains tiny.

## Non-goals

- Replacement six-screen infotainment shell.
- Later UAS/UAQ firmware port or signing bypass.
- Replacement vehicle-control or camera logic.
- Whole-subsystem connectivity disablement.
- Second dashboard display.
