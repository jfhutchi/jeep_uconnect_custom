# KIM19 Yelp runtime gates

The full canonical ledger is [runtime_gates.json](../reports/kim19_yelp/runtime_gates.json).
This table separates a gate implemented by Yelp from the live condition that
must satisfy it.

| Gate | Classification | Pass condition | Failure observation |
|---|---|---|---|
| Package registration/catalog | **TARGET OBSERVATION REQUIRED** | Yelp is installed, registered, visible, and entitled | Tile absent or disabled |
| DRM/AppManager/AMS/policy | **TARGET OBSERVATION REQUIRED** | Recovered identity and signer receive current launch/grants | Tap returns, errors, or never enters lifecycle |
| Xlet container/LWUIT | **PROVED** | `getContainer`, visibility, and `Display.init` complete | Container exception destroys Xlet |
| Theme/locale/RMS/metrics | **PROVED** | Startup runnable completes through splash creation | Throwable is logged; no local fallback is constructed |
| Splash worker/location | **PROVED** | Worker survives delay and `LocationInfo` and schedules callback | Splash can remain because only interruption is caught there |
| Home/VR constructor | **PROVED** | helper construction and layout return | An uncaught constructor failure can prevent useful UI; an internally caught VR setup failure disables VR |
| Local pre-backend UI | **PROVED** | screen 70/74 is built | Search/category/voice controls appear before Yelp HTTP |
| Vehicle lockout | **PROVED** | non-emulator lockout false | Keyboard is suppressed or screen 73 is selected |
| Valid location | **PROVED** | local latitude/longitude validity check passes | Touch and voice show GPS alert and enqueue nothing |
| Voice service/session | **TARGET OBSERVATION REQUIRED** | service discovery, session request/start, offboard recognition, and callback succeed | Voice error/generic failure or no recognized term |
| Connectivity | **TARGET OBSERVATION REQUIRED** | emulator/`use_en0` bypass or `connectInternet` succeeds | response code -1 and null-response processing |
| DNS/TCP/TLS/HTTP | **TARGET OBSERVATION REQUIRED** | default client resolves/connects/negotiates and server accepts request | common code collapses transport `Throwable` to null |
| Legacy JSON schema | **TARGET OBSERVATION REQUIRED** | response is JSON with expected top-level/business fields | empty status, parse log, generic failure, or dialog |
| Phone/navigation | **TARGET OBSERVATION REQUIRED** | receiver implementation, permission/activation, and resident service succeed | localized phone/navigation dialog |

**UNKNOWN:** a later `startXlet` call when `_appStarted` is already true performs
no explicit show/resume in Yelp. The platform may restore visibility, but that
behavior is not proved by the Yelp method.

**PROVED:** descriptor `security.policy` grants only
`com.harman.network.InterfacePermission "ppp0"`. Whether inherited/default
policy and signer grants add capabilities on the target is **TARGET OBSERVATION
REQUIRED**; the policy file alone must not be treated as the effective grant set.

