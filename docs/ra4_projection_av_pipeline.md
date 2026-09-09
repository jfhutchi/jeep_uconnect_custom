# RA4 Projection AV and Input Pipeline

## Video/display

| Component | Status | Evidence |
| --- | --- | --- |
| 640x480@60 display, OMAP3730/SGX530 graphics and QNX Screen | ALREADY PRESENT | display-stack |
| full-screen application/Xlet container and stock layer arbitration | PRESENT BUT NEEDS ADAPTER/GLUE | hmi-arbitration |
| IVA2.2-class H.264 silicon capability | PRESENT BUT NEEDS ADAPTER/GLUE | h264-silicon |
| installed supported H.264 decoder and client ABI | UNKNOWN | h264-runtime-gap |
| pixel format, stride, scaling, rotation, buffer queues and measured frame latency | UNKNOWN | h264-runtime-gap |

## Audio output

| Component | Status | Evidence |
| --- | --- | --- |
| AudioCtrlSvc/MME and audioApp logical source mapping | ALREADY PRESENT | audio-path |
| projection PCM sink and exact sample-rate/channel contract | UNKNOWN | audio-path |
| media/prompt/call focus, ducking, volume, mute and restore adapter | MISSING SOFTWARE | audio-path |

## Microphone/voice input

| Component | Status | Evidence |
| --- | --- | --- |
| cabin microphone and stock phone/VR consumers | ALREADY PRESENT | microphone-path |
| resident application PCM capture API and permissions | UNKNOWN | microphone-path |
| assistant/call capture lease, AEC path and USB return | MISSING SOFTWARE | microphone-path |

## Touch/button return

| Component | Status | Evidence |
| --- | --- | --- |
| Screen/mtouch event source and stock touch consumers | ALREADY PRESENT | touch-input |
| absolute coordinate/contact transform and cancellation | UNKNOWN | touch-input |
| hard-key, rotary and steering-wheel event sources | PRESENT BUT NEEDS ADAPTER/GLUE | button-input |
| projection input serialization over the active USB session | MISSING SOFTWARE | touch-input |
