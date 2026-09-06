# TRAIL: 640x480 projection-ownership bench

PC-only original code and CSS. **Not a deployable RA4 application.** This is a
focused executable model of OEM-style projection inside stock Uconnect; it is no
longer a six-screen replacement-HMI mock.

Run from the repository root:

```powershell
python -m http.server 8765 --bind 127.0.0.1 --directory prototype/resident_hmi
```

Open `http://127.0.0.1:8765/`. Bind only to loopback and serve this directory,
not the repository or ignored firmware corpus.

Tests and host-only size accounting:

```powershell
node --test prototype/resident_hmi/tests/*.test.mjs
python -m analysis_tools.hmi_size_report prototype/resident_hmi
```

## What the bench models

- Projection session state separately from the visible foreground owner.
- Full-screen CarPlay or Android Auto placeholder when projection is selected.
- Explicit Return to Uconnect without ending the session.
- Return to the existing active session without reconnecting.
- Camera/critical stock takeover and restoration of the preempted owner.
- A permitted stock comfort overlay without changing the underlying owner.
- Projection-owned call, message and SMS/TTS presentation while active, including
  while ordinary Uconnect is foreground.
- Restoration of native Phone/Messaging presentation after projection disconnect.
- Fail-to-stock behavior on invalid, stale or disconnected integration state.

The "Factory Uconnect" surface deliberately does not reproduce Radio, Media,
Climate, Controls, Phone, Messaging or Settings. Those remain stock product UI.

## Boundaries

No projection engine, radio connection, Bluetooth operation, HFP/MAP control,
audio, camera video, vehicle command, CAN implementation, persistent storage,
vendor asset or network transport exists. The CSP keeps `connect-src 'none'`.
Scenario buttons are outside the 640x480 surface.

`model.mjs` defines the portable state semantics. `mock-adapter.mjs` emits
synthetic version-2 snapshots. `view.mjs` renders only ownership/session state.
`controller.mjs` is the mock scenario boundary. Tests use Node's built-in runner
and have no package dependency.

The evidence basis and unresolved runtime seams are in
[the projection foreground report](../../reports/projection_foreground_ownership.md).
The production storage envelope remains 15 MB installed, 4 MB normal writes,
8 MB additional update peak, 45 MB stock reserve and 5 MB planned-peak margin.
Host source size is not a radio-package measurement.
