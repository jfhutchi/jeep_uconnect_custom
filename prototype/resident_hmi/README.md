# TRAIL: 640x480 resident-HMI feasibility scaffold

PC-only demonstration, original code and CSS. **Not a deployable RA4 app and not
the production navigation model.** Its six screens are a technical scaffold for
state, adapter, legibility and failure-policy tests. Production preserves stock
Radio, Media, Climate, Controls, Phone, Messaging and Settings and adds projection
as a first-class Uconnect application.

No radio connection, persistent storage, sound, camera video, vendor assets, CAN
implementation or phone-projection backend. The scaffold's `stock/app/camera`
mode does not model the corrected session/foreground ownership state machine.

From the repository root, with Python 3 and a local browser:

```powershell
python -m http.server 8765 --bind 127.0.0.1 --directory prototype/resident_hmi
```

Open `http://127.0.0.1:8765/`. Stop with Ctrl+C. Bind only to loopback and serve
this directory, not the repository/vendor corpus. No npm install/build needed.
The ES modules need HTTP; opening `index.html` directly may fail browser CORS.
Node 24 was used for development tests; Python 3.12+ for size accounting.

```powershell
node --test prototype/resident_hmi/tests/*.test.mjs
python -m analysis_tools.hmi_size_report prototype/resident_hmi
```

The size report measures this host source tree (including tests/docs), NOT a
radio package. It estimates allocation using an explicit 4096-byte assumption;
it does not measure filesystem metadata, browser cache, RAM or radio storage.
No data is persisted by app code; the host browser/server can maintain their
own caches/logs outside the RA4 budget. Neither is shipped to the radio.

## What works

- Home, Media, Climate, Controls, Phone placeholder and Settings navigation.
- Mock temperature/fan/auto, heated seats/wheel and playback intents.
- Pending feedback before observed-state updates, single in-flight command,
  bounded inputs, coarse capabilities, rejection and timeout without retry.
- Separate PC controls for camera takeover, disconnect, stale data and command
  response mode. Normal state does not automatically resume after fallback.
- Camera and stock-fallback panels remove custom vehicle actions. They simulate
  policy only, not a real window-manager/camera/fallback implementation.

## Files and boundaries

| File | Responsibility |
| --- | --- |
| `model.mjs` | Renderer-independent reference state machine, validation and abstract intents |
| `mock-adapter.mjs` | In-memory simulated service; no external transport |
| `view.mjs` | Replaceable HTML renderer with escaped service text |
| `app.mjs` | PC event binding, simulated delay, heartbeat and test scenarios |
| `controller.mjs` | Expire queued intents before dispatching to the mock adapter |
| `style.css`, `index.html` | Original fixed-size PC presentation and test bench |
| `tests/` | Node built-in tests; no package dependency |

The [contract](../../docs/resident_hmi_contract.md) defines portable semantics.
The [decision](../../docs/resident_hmi_decision.md) prefers existing AIR/SWF reuse
conditionally, retaining native QNX as an alternative. Both need compatible
toolchains, an authorized loading path and proved stock ownership/fallback.

## Browser verification checklist

1. Verify `#hmi` is exactly 640x480 and all six routes fit without internal scroll.
2. Climate: press `+ Driver`; value must remain old while pending, then change.
3. Set rejection/timeout in PC bench; values must not optimistically change.
4. Camera takeover removes custom actions. Normal state requires Resume.
5. Disconnect / Stop updates causes fallback. No reconnect command replay.
6. Inspect console for app errors; verify no backend/network requests and no
   localStorage/sessionStorage use in source. Factory performance remains UNKNOWN.
