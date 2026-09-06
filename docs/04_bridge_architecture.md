# 04 - Projection Integration Architecture

## Objective

Add native phone projection as an OEM-style application inside stock Uconnect.
Do not replace the stock HMI or RA4 vehicle-service authority.

## Architecture

```text
Tiny RA4-resident projection integration
  |-- stock application arbiter, navigation stack, popups and camera layers
  |-- stock display, touch, audio, media and vehicle services
  `-- optional external projection engine
       only if local storage/CPU/RAM feasibility fails
```

Follow [the resource budget](ra4_resource_budget.md): 15 MB installed cap, 4 MB
runtime growth, 8 MB additional update peak, 45 MB protected stock reserve and
5 MB planned-peak margin.

## Resident responsibilities

- Register/use projection as a stock application/screen.
- Keep session lifetime separate from visible foreground ownership.
- Reuse stock foreground requests, navigation stack, popup and camera layers.
- Provide easy Return to Uconnect and resume-existing-projection paths.
- Gate only duplicate native Phone/Messaging foreground and announcement behavior.
- Preserve Bluetooth/HFP/MAP and stock services unless a narrower proved conflict
  requires arbitration.
- Reuse stock assets/libraries after ABI/access verification.

## Stock responsibilities

Stock retains ordinary screens, vehicle configuration, HVAC/comfort, tuner/media,
phone services, camera priority, display/touch/audio policy and CAN communication.

## Optional external engine

First measure legitimate local engine size, RAM, CPU, graphics, USB and service
access. Use `EXTERNAL_COMPUTE_REQUIRED` only if local feasibility fails. External
compute must not replace the tiny stock-facing arbitration layer or become the
ordinary HMI. Never bundle maps, media libraries, speech models or a browser.

## Foreground and return behavior

Camera/critical stock takeover outranks permitted temporary overlays, which
outrank projection, which outranks ordinary stock HMI only while selected.
Camera uses the stock layer/stack return. Comfort popups do not end projection.
Return to Uconnect hides projection without stopping it; Return to Projection
navigates to the active session. Crash/disconnect returns to stock.

## Unknown integration contracts

Authorized app/screen loading, compatible toolchain, video surface, touch routing,
projection/HFP audio focus, supported call/SMS presentation policy and complete
backend protocol remain unproved. Runtime work belongs on an authorized spare
bench unit after static closure; this document authorizes no radio mutation.
