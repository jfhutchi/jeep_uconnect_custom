# Interface Inventory

This is the working index of interfaces, services and artifacts relevant to the modernization project.

| Area | Interface / artifact | Confidence | Notes |
|---|---|---:|---|
| Projection | `IPhoneProjection` | VERIFIED | Referenced by factory HMI |
| Projection | `sessionActive` | VERIFIED | Session exists independently of visible `DEVICE_PROJECTION` branch |
| Projection | `startProjection(ppId)` | VERIFIED command; backend effect UNKNOWN | Stock BacktoCar path calls it before checking sessionActive; no teardown/reconnect meaning inferred |
| Projection | `projectionCallState` | VERIFIED | Projection call/caller state feeds stock status bar |
| Projection | `PhoneProjectionEvent` | VERIFIED | Status, status-bar and back-to-car event family |
| Projection | `phoneProjectionService` | VERIFIED reference / UNKNOWN implementation | HMI expects this backend name; implementation not yet located |
| Projection | `DeviceProjection.swf` | VERIFIED reference / UNKNOWN installed artifact | Projection screen referenced by main HMI |
| RA4 app lifecycle | secure AMS + `/fs/mmc1/xletsdir` | VERIFIED | `jvm.sh` retains `-secure`; development selects a security configuration, not insecure mode |
| RA4 app lifecycle | generic Apps Xlet launch | VERIFIED for authorized packages | Apps tile -> ModuleLink `startApp` -> native DRM-check byte 1 -> AMS start; target package authorization remains external |
| RA4 app authorization | detached `key.jar` + DRM/developer identity | VERIFIED binding / UNKNOWN issuer path | New-project signer/token/DRM issuance is not available and must not be bypassed |
| Projection | `isSourceCarPlay` | VERIFIED | Media HMI source awareness |
| Projection | `isSourceGAL` | VERIFIED | Media HMI source awareness |
| Projection | `enableCarplay` | VERIFIED | Persistency property |
| Projection | `enableAndroidAuto` | VERIFIED | Persistency property |
| Projection | `enableMirrorLink` | VERIFIED | Persistency property |
| Projection | `Projection_AutoShow` | VERIFIED | Persistency property |
| Projection | `projectionAutoPlay` | VERIFIED | Persistency property |
| HMI | Adobe AIR / SWF | VERIFIED | Factory interface platform |
| HMI | `main.swf` | VERIFIED | Main HMI artifact |
| HMI | ModuleLink API classes | VERIFIED | High-level Harman service abstraction |
| HMI backend | localhost ModuleLink endpoint | VERIFIED | Existing HMI config references local service communication |
| Service discovery | servicebroker | VERIFIED role / UNKNOWN registration schema | Harman/QNX discovery role observed; projection binding, versioning and owner-death behavior not recovered |
| QNX CAR reference | `/pps/system/navigator/*` | CONFIRMED REFERENCE / UNKNOWN ON RA4 | QNX CAR 2.1 application/window manager contract; not yet found in the RA4 corpus |
| QNX CAR reference | `/pps/services/launcher/control` + Authman | CONFIRMED REFERENCE / UNKNOWN ON RA4 | QNX CAR 2.1 authorized application-lifecycle path; do not use its manual command example on RA4 without stock-contract evidence |
| QNX CAR reference | HMI Notification Manager | CONFIRMED REFERENCE / UNKNOWN ON RA4 | Priority-based multimodal arbitration; HandsFreePhone wraps HFP state and exposes configurable incoming-call presentation priority plus fallback window types, but no HNM artifact or policy hook is proved on RA4 |
| QNX CAR reference | QtQnxCar2 / UI Core / NowPlaying | CONFIRMED REFERENCE / UNKNOWN ON RA4 | Era-compatible reference components only; no ABI, installed service, or permission claim |
| Vehicle state | QNX PPS | VERIFIED | Used around vehicle/CAN data |
| HVAC | `IHvac` | VERIFIED | Factory HMI references higher-level HVAC interface |
| HVAC | `hasHeatedSeat` | VERIFIED | Capability API in factory HMI |
| HVAC | `hasHeatedSteeringWheel` | VERIFIED | Capability API in factory HMI |
| HVAC | `hasVentedSeat` | VERIFIED | Capability API in factory HMI |
| HVAC | HVAC event/state names | VERIFIED | Temperature, fan, vent, defrost, sync, auto and related state observed |
| Seats | `HeatedSeatFL` / `FL_HS_STAT` | VERIFIED | PPS-backed state mapping observed |
| Seats | `HeatedSeatFR` / `FR_HS_STAT` | VERIFIED | PPS-backed state mapping observed |
| Display | QNX Screen | VERIFIED | Core graphics/windowing stack |
| Display | `libscreen.so` | VERIFIED | Used by factory utilities |
| Display | Screen window/buffer APIs | VERIFIED | Factory utilities create windows/buffers and inspect display state |
| Display config | `video_hmi` class | VERIFIED configuration / UNKNOWN contract | Recovered graphics.conf names it; ownership, z-order and buffers unproved |
| QNX Screen reference | window group + focus/sensitivity | CONFIRMED REFERENCE / UNKNOWN ON RA4 | Parent manages joined child visibility; display/group focus is privileged |
| Touch | mtouch infrastructure | VERIFIED | Factory calibration tooling consumes QNX Screen touch events |
| Touch | `screen_get_event` | VERIFIED | Used by factory tooling |
| Touch config | CMC mtouch/scaling | VERIFIED configuration / UNKNOWN projection route | Focus, sensitivity, transform and preemption cancellation unproved |
| Audio | AudioCtrlSvc | VERIFIED | Factory audio service |
| Audio | MME | VERIFIED | Multimedia engine / logical source path |
| Audio | `audioApp -> MME` | VERIFIED | Application audio source mapping observed |
| QNX audio reference | Audio Manager typed handles/concurrency | CONFIRMED REFERENCE / UNKNOWN ON RA4 | Routing/ducking is separate from player pause/resume |
| QNX audio reference | Now Playing phone/status PPS | CONFIRMED REFERENCE / UNKNOWN ON RA4 | Publishes concurrency; each player decides pause/resume |
| QNX voice reference | `io-audio` + `io-acoustic` + `pps-bluetooth` | CONFIRMED REFERENCE / UNKNOWN ON RA4 | HFP transport, AEC, microphone and speaker path are separate from foreground UI |
| USB | QNX `io-usb` stack | VERIFIED | Core USB infrastructure |
| USB | `libusbdi` / usbd APIs | VERIFIED | Factory USB utility uses QNX USB API |
| QNX 6.6 CarPlay transport | `usblauncher` + `RoleSwap_DigitaliPodOut` + `io-usb-dcd` | CONFIRMED REFERENCE / UNKNOWN ON RA4 | Official legacy host-to-device role swap; required automotive iOS drivers supplied through QNX support |
| RA4 USB platform/topology | Harman BE2800 CMC VP4 NA/CA; SD/USB/aux hub 68141322AA/68289895AA; UCI cable 68141323AA; Radio C2 D2784B X455/X458/X457/X456 | CONFIRMED platform/product distinction; HIGH radio connector map / internal route UNKNOWN | Official Mopar distinguishes the data hub from charging-only 68145567AA/AB; a Chrysler-attributed connector view closes power/D-/D+/ground to Radio C2, while active hub silicon, VBUS switching and BE2800 controller/PHY nets remain unknown |
| USB hardware role | OMAP3730 high-speed USB OTG | CONFIRMED silicon / board+BSP UNKNOWN | TI documents host/peripheral modes; public QNX OMAP3730 BSP table lists OTG Host only; BE2800 custom DCD and physical role-switch route remain unproved |
| QNX 6.6 Android transport | Android Accessory Protocol | CONFIRMED REFERENCE / Android Auto receiver UNKNOWN | Accessory transport must not be promoted to a receiver claim |
| Apple accessory | `itun` | VERIFIED | iPhone tunnel adapter / accessory networking component |
| Apple media | `libipod` / iPod integration | VERIFIED | Legacy Apple device integration |
| Foreground | `checkForegroundAvailability` / `onAppRequestForeground` | VERIFIED | Stock allow/deny reasons and pending retry at `0x0025250E-0x002525D2`; retry at `0x002524C4-0x002524FD` |
| Presentation | volatile default-open lease | MODEL_PROVED / TARGET_UNPROVED | Point-of-use freshness prevents stale suppression in both reference models; supported stock policy hook is unknown |
| Navigation | `IStructure.goto/back/removeFromStack` | VERIFIED | Stock screen transition and return primitives |
| Popup | `IPopupManager.show/dequeue` | VERIFIED | Temporary popup layer independent of underlying branch |
| Phone | `processBTCallState` | VERIFIED | Native call goto/popup and previous-screen return downstream of HFP |
| SMS | `SMSManager` popup/TTS paths | VERIFIED | Native message foreground and audio presentation seams |
| Camera | DisplayManager/LayerManager camera paths | VERIFIED | Observation/takeover at `0x002BA764-0x002BA89F`; stack return at `0x002D4D6F-0x002D4EF8`; variants differ |
| Security | RA4 signed-update verification | VERIFIED | USB updater validates signed hashes/signatures |
| Security | later UAS multi-layer signing/encryption | VERIFIED | Reference architecture only; not intended as porting source |

## Next items to resolve

The production contract is projection inside stock Uconnect. The current PC
artifact is a focused projection-ownership bench and contains no replacement
factory screens. A VERIFIED name proves observed stock code, not access permission
or a complete backend.

1. Use the executed [post-reboot XREF/census results](../reports/ra4_post_reboot_checkpoint.md)
   for return, native call/SMS and comfort candidates; follow remaining consumers.
2. Recover Return-to-Uconnect and resume-existing-session control flow.
3. Run the audio/Now-Playing/acoustic marker census, then recover RA4 source,
   ducking, pause/resume, microphone and speaker ownership.
4. Recover heated-seat/heated-wheel popup triggers.
5. Continue the independent temperature units/service-restart quality trace.
6. Follow the completed 122-marker census with imports/XREFs and startup
   configuration. Inspect compressed SWFs separately; raw negatives do not
   exclude their names. Trace installed Mentor board-init/ULPI to PHY/VBUS.
7. Use the static-proved Xlet launch lane only after a legitimate package
   authorization route is supplied; establish screen/service loading separately,
   then measure a tiny resident trial.
