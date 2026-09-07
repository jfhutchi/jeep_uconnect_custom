# RA4 Resident Application Identity Model

## Result

The durable join key visible across descriptor, directory, DRM and AppManager is
`xlet.appId`/`appIdentifier`, but RA4 does not prove an app-ID issuance scheme.
The corpus includes conventional UUID strings as well as values such as `100`,
`999`, and `engineering`; UUID syntax is not a platform-wide requirement.
Hello's UUIDv5 is a collision-resistant project-local placeholder only. It is
not an FCA-issued package or application identity.

## Field relationships

| Field or identity | Status | Evidence-supported role |
| --- | --- | --- |
| Application ID (`xlet.appId`) | **PROVED** | Present in all 135 installed descriptors; equals the KIM application-directory name in all 135; agrees between signed and installed descriptors in all 135; is the AppManager start/uninstall/catalog key. |
| DRM application ID (`appIdentifier`) | **PROVED** | Same-KIM correlation matches 131 DRM grants to application descriptors by case-insensitive app ID. It is the strongest visible DRM-to-app join. |
| Main class (`xlet.mainClass`) | **PROVED** | Signed and installed descriptors agree in all 135 pairs where present; AMS reads it and loads the selected executable through the Xlet classloader. It identifies the entry class, not the package authority. |
| Installed executable name (`xlet.jarFile`) | **PROVED stage-specific** | Selects the executable under `prog/jars`. It differs between signed and installed descriptor in 129/135 pairs, so filename is not the durable identity. |
| Live installer filename | **PROVED stage-specific** | Catalog DRM and download metadata name an incoming representation. Vehicle User Guide uses `IVHClient_v1.0.4-FIT.jar`, signed descriptor `Help.jar`, and installed UUID filename for three distinct stages. |
| Application name/vendor/version | **PROVED metadata** | Signed and installed name/vendor agree across observed pairs; AppManager catalog stores/display uses app ID, app name and media name. These fields do not establish signer authority. |
| Signer certificate | **PROVED authentication input** | Embedded in the detached PKCS#7 signature and presented to AMS signing-key verification. It authenticates the signed member set but is not itself the app ID. |
| Developer ID/token | **PROVED consumer, issuer UNKNOWN** | The signed descriptor may contain `xlet.developerToken`; AMS compares its public-key-decoded content to runtime `developerId`. The legitimate ID provider and issuance process are absent. |
| Device ID/token | **PROVED verifier branch, provisioning UNKNOWN** | An optional device `SignedId` check precedes certificate verification on the fallback path. Live device-ID provisioning is not recovered. |
| Java principal / protection domain | **UNKNOWN** | No recovered method proves how an accepted signer becomes a Java `Principal`, `CodeSource`, or `ProtectionDomain`. |
| Policy domain | **UNKNOWN** | Global policy name and per-app policy are signed metadata, but combine/substitute/intersection behavior and signer-to-policy selection are unrecovered. |
| AMS internal package identity | **UNKNOWN** | AMS owns package/filesystem state beyond the visible tree, but its registry schema and any separate package UUID are not recovered. |
| Native AppManager registry identity | **PROVED bounded** | `AppManager_JavaApps` is a whole JSON array containing `appId`, `appName`, and `medName`; it is downstream state, not an authentication source. |

## Signed versus installed descriptor

The signed descriptor is `key.jar!/xlet.properties`. The normalized installed
descriptor is `<appId>/prog/xlet.properties`.

- **PROVED:** the byte streams differ in 135/135 pairs.
- **PROVED:** `xlet.appId`, `xlet.mainClass`, `xlet.vendor`, `xlet.name`,
  `xlet.policy`, and `xlet.policy.default` agree wherever present in 135/135.
- **PROVED:** `xlet.developerToken` agrees in all six token-bearing pairs. The
  inspector therefore rejects a token mismatch between signed and installed
  forms; it does not expose or validate token content.
- **PROVED:** `xlet.jarFile` differs in 129/135 and may be normalized during
  installation.
- **VALIDATOR CONSERVATIVE RULE:** identity, policy, developer/device-token and
  safety-relevant lifecycle/category fields must agree between signed and
  installed forms. Only `xlet.jarFile` is accepted as a stage-specific
  difference; this is a host structural rule, not a claim that every possible
  installer normalization has been enumerated.
- **INFERRED:** the embedded copy is the package/authentication descriptor and
  the external copy is installed state. The signer source is directly proved as
  `key.jar!/xlet.properties`, but the complete install-time normalization method
  remains unavailable.

## Best-supported identity chain

```text
authorized app-ID allocation                       UNKNOWN authority
  -> signed xlet.properties xlet.appId             PROVED field
  -> key.jar digest/signature envelope             PROVED binding
  -> normalized <appId>/prog/xlet.properties       PROVED installed form
  -> AMS package/classloader state                  PROVED appId use, hidden schema UNKNOWN
  -> DRM grant appIdentifier                        PROVED correlation, acceptance rule UNKNOWN
  -> AppManager JavaApps entry and Apps list        PROVED downstream use
```

For Hello, the main class and project-local ID are internally consistent and
safe. A legitimate future package still needs an authorized process to accept
or replace that ID and bind the issued identity to signer, DRM and policy state.
