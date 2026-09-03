# 640x480 HMI prototype

This is the first runnable UI prototype for issue #7.

## What it demonstrates

- Exact 640x480 application frame for the original RA4 display target.
- Newer-Uconnect-inspired Home, Radio, Media, Climate, Controls, Phone, Projection, and Settings flows.
- Persistent bottom application bar.
- Driver/passenger temperature controls and fan state.
- AUTO, A/C, SYNC, recirculation, and defrost state.
- Driver/passenger heated-seat state and heated-steering-wheel state.
- Android Auto and Apple CarPlay connection/session-state simulation.
- A placeholder native projection surface boundary: the future real projection engine owns the projection pixels; the Jeep HMI does not reskin CarPlay/Android Auto.
- Factory-camera-priority simulation.
- Explicit stock-Uconnect fallback controls.

## Safety boundary

The prototype is deliberately disconnected from the vehicle.

`MockVehicleService` is the only state provider. There is:

- no CAN implementation
- no RA4 write path
- no firmware flashing
- no signing work
- no safety-critical vehicle control

The future integration layer should replace the mock with high-level stock RA4 service adapters as those interfaces are verified.

## Run

From the repository root in a VS Code PowerShell terminal:

```powershell
py -m http.server 8080 --directory .\prototype\hmi
```

Then open `http://localhost:8080`.

Because the prototype has no build system or external dependencies, `index.html` can also be opened directly in a browser.

## Current architecture seam

The UI talks only to a service-like object (`MockVehicleService`). This is intentional. The target architecture is:

```text
Modern HMI
   |
   v
abstract comfort/media/projection services
   |
   +-- stock RA4 ModuleLink/PPS/service adapters
   +-- projection engine adapter
   +-- display/touch/audio bridge
```

The HMI must never grow direct safety-critical CAN logic.

## Next coding steps

1. Split the mock contract into explicit service interfaces/adapters.
2. Add capability discovery so controls appear only when supported by the vehicle.
3. Add projection state-machine tests.
4. Add display/touch/audio bridge interfaces with bench-only mock implementations.
5. Replace simulated projection pixels with a real projection-video input only after issue #9 selects the legitimate Android Auto/CarPlay engine.
