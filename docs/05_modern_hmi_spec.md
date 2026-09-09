# 05 - Projection Integration HMI Specification

> **Project status - 2026-09-07: BLOCKED without manufacturer support.**
> The software-only integration is effectively not achievable with the hardware
> and authorized access available to this project. Manufacturer-provided or
> approved development/service hardware, credentials, signing/entitlements and
> compatible licensed software are prerequisites; no sufficient route is confirmed.
> This document is retained as research or a conditional design, not an active
> deployment roadmap. The [current project status](00_project_status.md)
> supersedes earlier implementation priorities and defines reopening conditions.

## Product correction

The resident prototype is a PC-only projection-ownership bench. It deliberately
does not reproduce stock screens. Production preserves Radio, Media, Climate,
Controls, Phone, Messaging and Settings and adds CarPlay/Android Auto as a
first-class Uconnect application.

## Projection screen

- Full 640x480 while visible.
- Native phone-platform appearance; do not reskin projection.
- Obvious Return to Uconnect.
- Obvious stock shortcut back to the active session.
- No reconnect/restart when only foreground changes.
- Distinct disconnected, connecting, loading, active-visible,
  active-backgrounded and error states.
- Honor, but do not depend exclusively on, projection auto-show preference.

## Foreground ownership

Priority: camera/critical stock, permitted stock overlay, active projection,
ordinary stock HMI.

- Factory camera remains latency-neutral and returns through the stock stack.
- HVAC/comfort popups may overlay projection and dismiss back to it.
- Emergency/eCall preempts and retains stock interaction-presentation authority.
- Absent that critical takeover, active projection owns projected call/message
  presentation even if temporarily backgrounded behind ordinary stock or camera
  presentation.
- Suppress duplicate native call goto/popup and SMS popup/TTS.
- Restore native behavior on inactive/disconnected projection.
- Do not globally disable Bluetooth, HFP, MAP or message ingestion.

## Return semantics

Return to Uconnect changes foreground only. Return to Projection uses
`DEVICE_PROJECTION` when `sessionActive`. Stock BacktoCar can issue the distinct
start command before that check; its backend effect is unproved. Session continuity
remains required. Temporary overlays do not change branch. Camera
reuses stock `goto/back/removeFromStack`. Disconnect/error uses stock fallback.

## Resource rules

Reuse stock status bar, navigation, popups, assets and services. Follow
[ra4_resource_budget.md](ra4_resource_budget.md). Do not bundle browsers, maps,
media libraries, speech models, fonts or duplicate assets. A complete engine that
cannot safely fit/execute locally is `EXTERNAL_COMPUTE_REQUIRED`.
