# RA4 Projection HMI Integration

Projection must remain subordinate to stock camera, emergency, display-off, and safety arbitration. No safety bypass is part of this architecture.

## Existing mechanisms

| Mechanism | Status | Evidence |
| --- | --- | --- |
| projection session state separate from visible foreground | ALREADY PRESENT | projection-hmi-remnant |
| Apps/Xlet 640x480 foreground lifecycle | PRESENT BUT NEEDS ADAPTER/GLUE | hmi-arbitration |
| camera and critical/eCall preemption | ALREADY PRESENT | hmi-arbitration |
| HVAC temporary overlays without branch replacement | ALREADY PRESENT | hmi-arbitration |
| Return-to-Uconnect and Return-to-Projection behavior | PRESENT BUT NEEDS ADAPTER/GLUE | projection-hmi-remnant |
| matching projection bridge/backend owner | MISSING SOFTWARE | projection-gateway-gap |
| projection-specific audio, mic and input leases | MISSING SOFTWARE | audio-path |

## Foreground priority

```text
camera / critical and emergency stock takeover > permitted temporary stock overlay > active projection foreground > ordinary stock HMI
```

Session ownership, visual foreground, audio focus, microphone lease, and input eligibility remain independent state dimensions.
