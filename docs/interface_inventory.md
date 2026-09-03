# Interface Inventory

This is the working index of interfaces, services and artifacts relevant to the modernization project.

| Area | Interface / artifact | Confidence | Notes |
|---|---|---:|---|
| Projection | `IPhoneProjection` | VERIFIED | Referenced by factory HMI |
| Projection | `PhoneProjectionEvent` | VERIFIED | Referenced by factory HMI |
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
| Service discovery | servicebroker | VERIFIED | Harman/QNX service discovery/IPC role |
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
| Camera | factory camera HMI/resources | VERIFIED | Rear/front/cargo camera UI resources exist depending on product variants |
| Security | RA4 signed-update verification | VERIFIED | USB updater validates signed hashes/signatures |
| Security | later UAS multi-layer signing/encryption | VERIFIED | Reference architecture only; not intended as porting source |

## Next items to resolve

- Complete `IPhoneProjection` method/property/event list.
- ModuleLink/servicebroker discovery and message contract for projection.
- QNX Screen ownership and z-order behavior during projection and camera takeover.
- Touch-event ownership/routing during a projection session.
- Audio source registration and lifecycle for `audioApp` or an equivalent projection source.
- High-level write paths for heated seats, heated steering wheel and HVAC commands.
