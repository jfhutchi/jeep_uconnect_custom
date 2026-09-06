# Interface Inventory

This is the working index of interfaces, services and artifacts relevant to the modernization project.

| Area | Interface / artifact | Confidence | Notes |
|---|---|---:|---|
| Projection | `IPhoneProjection` | VERIFIED | Referenced by factory HMI |
| Projection | `sessionActive` | VERIFIED | Session exists independently of visible `DEVICE_PROJECTION` branch |
| Projection | `startProjection(ppId)` | VERIFIED | Distinct session-start command; not the active-session resume operation |
| Projection | `projectionCallState` | VERIFIED | Projection call/caller state feeds stock status bar |
| Projection | `PhoneProjectionEvent` | VERIFIED | Status, status-bar and back-to-car event family |
| Projection | `phoneProjectionService` | VERIFIED reference / UNKNOWN implementation | HMI expects this backend name; implementation not yet located |
| Projection | `DeviceProjection.swf` | VERIFIED reference / UNKNOWN installed artifact | Projection screen referenced by main HMI |
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
| Touch | mtouch infrastructure | VERIFIED | Factory calibration tooling consumes QNX Screen touch events |
| Touch | `screen_get_event` | VERIFIED | Used by factory tooling |
| Audio | AudioCtrlSvc | VERIFIED | Factory audio service |
| Audio | MME | VERIFIED | Multimedia engine / logical source path |
| Audio | `audioApp -> MME` | VERIFIED | Application audio source mapping observed |
| USB | QNX `io-usb` stack | VERIFIED | Core USB infrastructure |
| USB | `libusbdi` / usbd APIs | VERIFIED | Factory USB utility uses QNX USB API |
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

1. Run bounded AVM2 consumer XREFs for `PROJECTION_BACKTO_CAR`,
   `DEVICE_PROJECTION`, native call/SMS presentation and HVAC popup names.
2. Recover Return-to-Uconnect and resume-existing-session control flow.
3. Recover projection/HFP audio focus and microphone/speaker ownership.
4. Recover heated-seat/heated-wheel popup triggers.
5. Continue the independent temperature units/service-restart quality trace.
6. Establish authorized app/screen loading, then measure a tiny resident trial.
