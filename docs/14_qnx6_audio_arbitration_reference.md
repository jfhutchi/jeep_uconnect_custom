# 14 - QNX 6.6 audio arbitration reference boundary

Updated 2026-09-06. This official-reference comparison is read-only. It does not
authorize PPS writes, PCM opens, microphone access, Bluetooth changes, policy
edits, process launch, or radio installation.

## Result

**CONFIRMED REFERENCE:** QNX CAR 2.1 separates these responsibilities:

~~~text
Bluetooth HFP state ---> HNM visual policy ---> HMI display
         |
         +--------------> io-bluetooth
                                  |
                             io-acoustic (AEC)
                                  |
                             io-audio <--- microphone / speakers

application PCM ---> typed Audio Manager handle
                             |
                    routing + attenuation/mute

Now Playing status <--> players and phones
         |
         +-- application decides stop/pause/resume
~~~

Projection can therefore own ordinary call/message presentation while phone
connectivity remains alive. Visual foreground, playback, voice routing, and
microphone ownership must not be one broad boolean.

**CONFIRMED RA4:** Existing hash/provenance documentation identifies ignored
recovered plaintext `P/share/audioDSP/audioMgrCMC.conf:24-29`, where stock
sources including `audioApp` map to MME. This proves configured logical-source
mapping, not a registration, focus, or ownership API. AudioCtrlSvc is separately
identified in the recovered corpus.

**UNKNOWN ON RA4:** None of the generic services or PPS paths is yet proved
installed, started, ABI-compatible, or authorized for a new client. The exact
Harman AudioCtrlSvc, MME, ModuleLink, and HMI paths remain authoritative.

## Primary evidence

### Audio Manager

Official QNX documentation assigns Audio Manager stream routing, stream-type
identification, device monitoring, and configured concurrency/ducking. A
higher-priority source can attenuate or mute a lower-priority stream. Audio
Manager does not stop or pause media; the player uses Now Playing state and
makes that decision.

A client associates a PCM stream with an Audio Manager handle of the same type.
Documented types include multimedia, ringtone, texttospeech, voice,
voicerecognition, voicerecording, voicetones, videochat, alert, pushtotalk,
soundeffect, and others. The reference exposes concurrency state, muting source,
input state, voice mode, and voice outputs including BT SCO, speaker, and USB.

High-signal reference paths include:

- /pps/services/audio/audio_router_control
- /pps/services/audio/audio_router_status
- /pps/services/audio/control
- /pps/services/audio/devices/
- /pps/services/audio/status
- /pps/services/audio/types/
- /pps/services/audio/voice_status

These are census markers, not RA4 commands.

### Now Playing

All reference media players, including phones, register and exchange activity
through Now Playing. The phone generally has precedence and can tell other
players a call arrived. Players receive status and control such as pause/resume,
but application code performs the playback action.

High-signal paths include media-player control, phone and status under
/pps/services/multimedia plus media-controller control.

### Handsfree voice path

The Bluetooth guide places HFP command/state in handsfree PPS objects. QNX CAR
handsfree telephony uses io-audio, io-acoustic, and io-bluetooth, with acoustic
echo cancellation between cabin audio and Bluetooth PCM. Input mute, voice mode
(ringer/on/off), and voice output routes are separate audio state.

Suppressing a call popup is not the same as releasing a microphone or changing
HFP. A projected assistant may temporarily need the microphone without changing
ordinary screen ownership.

## Mapping to RA4

| Plane | Exact RA4 evidence | Reference analogue | Status |
| --- | --- | --- | --- |
| projection interaction | projectionCallState 0x002B4E18-0x002B4EBC; status bar 0x0001CBA9-0x0001CBBF | phone state plus HNM | RA4 path CONFIRMED; binding UNKNOWN |
| native call visual | processBTCallState 0x00257983 and Phone goto/popup/back | HFP -> HNM event | presentation seam CONFIRMED |
| SMS visual/audio | popup 0x002B6C35-0x002B6C96; TTS 0x002B85C2-0x002B8750 | alert/texttospeech plus notification policy | seams CONFIRMED |
| media source | `P/share/audioDSP/audioMgrCMC.conf:24-29` maps stock `audioApp` to MME; AudioCtrlSvc is identified | typed Audio Manager handle | configuration CONFIRMED; registration/ownership UNKNOWN |
| call/assistant mic | no exact API recovered | voice/recognition plus acoustic input | UNKNOWN |
| camera | display/layer takeover and stack return | independent display priority | visual independence CONFIRMED; audio UNKNOWN |

No fixed address is treated as a stable API.

## Required independent leases

| Lease | Granted only when | Ends on | Stock fallback |
| --- | --- | --- | --- |
| ordinary visual | fresh active session owns interactions | inactive, stale, disconnect, service loss, critical/eCall | native Phone/SMS UI/TTS |
| media | fresh media phase and proved source grant | stop, stale, disconnect | prior stock source |
| prompt | fresh navigation/assistant prompt | prompt end or timeout | prior audio |
| call audio | projected call plus healthy proved voice route | call end, stale, critical/eCall | stock call route |
| microphone | explicit call/assistant phase and exclusive stock grant | phase end, timeout, any fault | immediate stock release |

Return to Uconnect changes display foreground only. Camera preempts display while
audio follows proved stock policy. Emergency/eCall always takes stock ownership.

## Read-only census and decision gate

The recovered-tree probe now also locates the exact stock `audioMgrCMC.conf`,
`AudioCtrlSvc`, and `audioApp` names alongside controlled Audio Manager/API names,
audio control/router/types/voice PPS paths, media-player phone/status, io-audio,
io-acoustic, and pps-bluetooth.

A positive hit requires path/size/hash recording, static architecture/import
analysis, startup provenance, client/server classification, owner-death/reconnect
recovery, and resource measurement. A string alone authorizes no call or write.
A negative applies only to the scanned roots.

## Resource effect

This report and probe are host-only: 0 RA4 installed bytes, 0 writable growth,
and 0 staging bytes. Product caps remain 15 MB installed, 4 MB normal writable,
8 MB additional update peak, 45 MB protected stock reserve, and at least 5 MB
planned-peak margin.

The adapter audio portion stays within the existing <=256 KiB adapter planning
sublimit and bundles no codec, speech model, Bluetooth stack, acoustic engine,
or media service. A projection-engine component that fails measured
storage/CPU/RAM gates is EXTERNAL_COMPUTE_REQUIRED; the arbiter remains resident.

## Best next target

Run the census against the hash-identified recovered 18.45.01 filesystem. For
each Audio Manager, Now Playing, acoustic, MME, or AudioCtrlSvc candidate,
correlate imports and startup, then recover the exact source and microphone
owner-death contract. Decisive evidence is a stock-started service plus a
legitimate existing client path, not a generic QNX name.

## Official sources

- https://www.qnx.com/developers/docs/6.6.0_anm11_wf10/com.qnx.doc.am.system_services/topic/audio_management.html
- https://support7.qnx.com/download/download/26213/System_Services_Reference.pdf
- https://www.qnx.com/download/download/26838/PPS_Objects_Reference.pdf
- https://support7.qnx.com/download/download/26201/Bluetooth_Architectural_Overview_and_Configuration_Guide.pdf
- https://www.qnx.com/download/download/26205/HMI_Notification_Manager.pdf
