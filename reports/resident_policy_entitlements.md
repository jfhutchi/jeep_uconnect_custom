# RA4 Resident Policy and Entitlements

## Result

RA4 has at least four separate authorization layers: application-byte trust,
Java policy, native DRM/launcher entitlement, and privileged AppManager method
permission. Descriptor lifecycle/category flags are metadata, not substitutes
for those controls. A harmless Hello requests none of the privileged
capabilities, but the exact minimum accepted policy/DRM record is **UNKNOWN**.

## Layer separation

| Layer | Status | Role and Hello consequence |
| --- | --- | --- |
| Detached executable signature | **PROVED** | `key.jar` binds code and the signed descriptor to an application signer. Hello lacks this legitimate envelope. |
| Global Kona security configuration | **PROVED resources / UNKNOWN selection semantics** | Selected `security.jar!/xlet.security` enumerates `base.policy`, `complete.policy`, and `full.policy` and promotes signing keys. Exact policy-domain construction is unavailable. |
| Signed per-application policy | **PROVED presence / UNKNOWN combination** | 122/135 signed descriptors name `security.policy`, and each associated executable carries the named, signature-bound file. Whether it augments, replaces, intersects or requests permissions under `xlet.policy.default` is unknown. |
| Java AppManager permission | **PROVED** | Public install/uninstall/DRM/start/pause/stop methods construct `AppMgrPermission("appMgr")` and call the SecurityManager. Hello calls none of them. |
| Native DRM grant | **PROVED data/check / UNKNOWN minimum grant** | Signed `DRM.jar` holds `grantList` entries keyed by `appIdentifier`, with installer, feature and launcher masks. Native AppManager checks DRM for install preparation and explicit start. |
| Developer/device credential | **PROVED verifier branches / UNKNOWN issuance** | Signed tokens may satisfy or precede signer verification; they do not grant application API capabilities by themselves. Hello has no token. |
| Descriptor category/lifecycle flags | **PROVED metadata** | `xlet.daemon`, `xlet.autostart`, `xlet.isAudio`, `xlet.writeEnabled`, `xlet.AppCategory`, and pause flags affect classification/lifecycle behavior. They are not certificate or policy grants. |

## Policy evidence

All 135 signed stock descriptors contain `xlet.policy.default=full.policy`; 122
also contain `xlet.policy=security.policy`. The global `full.policy` includes
AppManager permissions, while application-specific policies request narrower
or additional facilities. This does not prove that every application receives
every line in `full.policy`, because signer/principal matching and the runtime
combination rule remain unknown.

Consequently, adding `xlet.policy.default=full.policy` to Hello merely because
it is common would not prove least privilege. Omitting it from the current draft
also does not prove a target will accept or run the package. The field must be
issued from a recovered rule or authorized package template, not guessed.

## DRM evidence

- **PROVED:** 26 KIM `DRM.jar` files carry 136 signed grants; 131 correlate to
  extracted apps in the same KIM by `appIdentifier`.
- **PROVED:** all 131 matched grants use `installerType=DRM_SYNC`.
- **PROVED:** matched feature masks are `1`, `2`, `6`, or `64`; launcher masks
  are `0` or `6`.
- **PROVED:** grant `fileLength` does not equal installed executable size for
  any of the 125 matched non-null lengths. DRM filename/length refer to an
  installer representation, while `key.jar` binds installed executable bytes.
- **PROVED:** KIM3 has applications but no KIM3 `DRM.jar`; four extracted apps
  lack a same-KIM grant. This prevents assuming a simple one-file/one-app rule.
- **PROVED:** install completion autostarts only when launcher-mask bit 2 (or a
  stock override) and the global gate allow it. An ordinary app can remain
  stopped after installation.
- **UNKNOWN:** which feature/launcher bits permit a new GUI app to appear and
  launch manually, how KIM3 obtains effective state, and whether a zero launcher
  mask permits only manual start or encodes another rule.

## Minimum Hello request

The smallest evidence-supported request is deliberately a negative capability
profile:

| Capability | Requested |
| --- | --- |
| GUI/Xlet lifecycle | Yes, only the ordinary Xlet/AWT/LWUIT surface |
| Manual foreground launch | Yes, through the stock Apps route after legitimate registration |
| Autostart / daemon / audio | No |
| File write / RMS persistence | No |
| Network / USB / CAN / vehicle service | No |
| AppManager privilege | No |
| Projection / background service / boot integration | No |

**INFERRED:** an authorized issuer should be able to assign a basic GUI policy
and manual-launch DRM/category state without privileged service permissions.
**UNKNOWN:** the exact policy name, principal, `AppCategory`, DRM `featureMask`,
`appLauncherMask`, installer type, or developer grant that implements that
least-privilege outcome on RA4 18.45.01.
